"""Failure-inclusive metrics and model-independent figures for new runs."""

import csv
import json
from collections import defaultdict
from pathlib import Path

from .common import atomic_json, canonical, digest, file_sha, records
from .dataset import identity, tasks

METRICS = ("precision", "recall", "f1", "exact")
DIMENSIONS = ("series_id", "condition", "noise", "motif", "size")


def aggregates(rows, dimensions=DIMENSIONS):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row.get(key) for key in ("model", *dimensions))].append(row)
    result = []
    for key, values in groups.items():
        record = dict(zip(("model", *dimensions), key))
        record.update(
            N=len(values),
            valid=sum(bool(row["valid"]) for row in values),
            pending=sum(row.get("status") == "pending" for row in values),
        )
        for metric in METRICS:
            record[metric] = sum(
                float(row["metrics"].get(metric) or 0) for row in values if row["valid"]
            ) / len(values)
        record["valid_fraction"] = record["valid"] / record["N"]
        judged = [row for row in values if row.get("answer_correct") is not None]
        record["answers_judged"] = len(judged)
        record["answer_correct"] = (
            sum(row["answer_correct"] for row in judged) / len(values) if judged else None
        )
        result.append(record)
    return sorted(result, key=lambda row: canonical([row.get(key) for key in ("model", *dimensions)]))


def write_csv(path, rows):
    if not rows:
        return
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def report(runs, destination, *, historical=None, figures=True, series=(), models=(), conditions=()):
    """Export saved runs or the article archive using one aggregation path.

    With no runs, ``historical`` is the complete analysis source. No plan or
    mock execution is needed to reproduce archived measurements.
    """
    if not runs and not historical:
        raise ValueError("Supply at least one run or an article archive")
    destination = Path(destination).resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Choose a new empty report directory")
    destination.mkdir(parents=True, exist_ok=True)
    rows, selected_ids, run_ids = [], set(), []
    cohort = None
    for directory in map(Path, runs):
        manifest = json.loads((directory / "run.json").read_text(encoding="utf-8"))
        if digest({k: v for k, v in manifest.items() if k != "run_id"}) != manifest["run_id"]:
            raise ValueError("Run manifest identity mismatch")
        if file_sha(directory / "tasks.sqlite") != manifest["dataset"]["tasks_sha256"]:
            raise ValueError("Frozen tasks changed")
        if manifest["run_id"] in run_ids:
            raise ValueError("Duplicate run")
        run_ids.append(manifest["run_id"])
        label = manifest["config"]["model"]["alias"] + (" [MOCK]" if manifest["mode"] == "mock" else "")
        label += " / " + manifest["run_id"][:8]
        run_task_ids = set()
        for task in tasks(directory / "tasks.sqlite"):
            run_task_ids.add(task["task_id"])
            selected_ids.add(task["task_id"])
            path = directory / "tasks" / (task["task_id"] + ".json")
            row = {key: task[key] for key in DIMENSIONS}
            row.update(
                task_id=task["task_id"],
                base_id=task["base_id"],
                model=label,
                status="pending",
                valid=False,
                metrics=dict.fromkeys(METRICS),
                answer_correct=None,
            )
            if path.exists():
                saved = json.loads(path.read_text(encoding="utf-8"))
                if (
                    saved.get("run_id") != manifest["run_id"]
                    or saved.get("task_id") != task["task_id"]
                    or saved.get("result_sha256")
                    != digest({k: v for k, v in saved.items() if k != "result_sha256"})
                ):
                    raise ValueError("Saved task result identity mismatch")
                row.update(
                    status=saved["status"],
                    valid=saved["valid"],
                    metrics=saved["metrics"],
                    answer_correct=saved.get("answer_correct"),
                )
            rows.append(row)
        if cohort is not None and run_task_ids != cohort:
            raise ValueError("New model runs have different task populations; report them separately")
        cohort = run_task_ids
    if historical:
        archive = Path(historical)
        archive_manifest = json.loads((archive / "MANIFEST.json").read_text(encoding="utf-8"))
        entry = next(value for value in archive_manifest["files"] if value["path"] == "observations.jsonl.gz")
        if file_sha(archive / entry["path"]) != entry["sha256"]:
            raise ValueError("Historical observations checksum mismatch")
        # Restrict baselines to the frozen task population, including failed historical observations.
        for saved in records(Path(historical) / "observations.jsonl.gz"):
            task_id = digest(identity(saved))
            if runs and task_id not in selected_ids:
                continue
            row = {key: saved[key] for key in DIMENSIONS}
            row.update(
                task_id=task_id,
                base_id=saved["base_id"],
                model=saved["model"] + " [historical]",
                status=saved["status"],
                valid=saved["valid"],
                metrics=saved["metrics"],
                answer_correct=saved.get("historical_metrics", {}).get("answer_correct"),
            )
            rows.append(row)
    rows = [
        row for row in rows
        if (not series or row["series_id"] in series)
        and (not models or row["model"].removesuffix(" [historical]") in models)
        and (not conditions or row["condition"] in conditions)
    ]
    if not rows:
        raise ValueError("No observations match the report filters")
    selection = {"series": list(series), "models": list(models), "conditions": list(conditions)}
    with (destination / "observations.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(canonical(row) + "\n")
    detail = aggregates(rows)
    by_condition = aggregates(rows, ("series_id", "condition", "noise"))
    write_csv(destination / "metrics.csv", detail)
    write_csv(destination / "conditions.csv", by_condition)
    plotted = []
    if figures:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        for series in sorted({row["series_id"] for row in by_condition}):
            subset = [row for row in by_condition if row["series_id"] == series]
            cells = sorted({(row["condition"], row["noise"]) for row in subset})
            models = sorted({row["model"] for row in subset})
            lookup = {(row["model"], row["condition"], row["noise"]): row for row in subset}
            for metric in ("recall", "f1", "exact"):
                fig, ax = plt.subplots(figsize=(max(8, len(cells) * 0.7), 5))
                width = 0.8 / len(models)
                for offset, model in enumerate(models):
                    x, y = [], []
                    for index, (condition, noise) in enumerate(cells):
                        row = lookup.get((model, condition, noise))
                        if row:
                            x.append(index - 0.4 + width * (offset + 0.5))
                            y.append(row[metric])
                    ax.bar(x, y, width=width, label=model)
                ax.set_xticks(
                    range(len(cells)),
                    [f"{condition}\n{noise}" for condition, noise in cells],
                    rotation=45,
                    ha="right",
                )
                ax.set_ylim(0, 1.05)
                ax.set_ylabel(metric + " (all planned tasks)")
                ax.set_title(series + " — frozen population; see CSV for each model's N")
                ax.legend(fontsize=7)
                fig.tight_layout()
                for extension in ("png", "pdf"):
                    name = f"{series}_{metric}.{extension}"
                    fig.savefig(destination / name, dpi=180)
                    plotted.append(name)
                plt.close(fig)
    summary = {
        "runs": run_ids,
        "observations": len(rows),
        "groups": len(detail),
        "figures": plotted,
        "historical_observations_sha256": entry["sha256"] if historical else None,
        "selection": selection,
        "metric_policy": "valid metric sum / planned N (including pending and failed)",
        "population_note": (
            "Archive baselines use available observations within the selected task IDs. "
            if runs else "Archive observations are included with their original coverage. "
        ) + "N can differ across models; consult CSV before comparison.",
    }
    atomic_json(destination / "report.json", summary)
    return summary
