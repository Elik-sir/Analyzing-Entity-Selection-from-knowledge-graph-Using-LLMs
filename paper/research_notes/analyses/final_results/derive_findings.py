"""Derive traceable headline records and sensitivity diagnostics from result CSVs."""

import argparse
import csv
import hashlib
import json
from pathlib import Path


def read(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(output):
    rows = read(output / "paired_contrasts.csv")
    sensitivity = []
    for row in rows:
        if row["metric"] != "f1":
            continue
        cluster_width = float(row["cluster_ci_high"]) - float(row["cluster_ci_low"])
        task_width = float(row["task_ci_high"]) - float(row["task_ci_low"])
        record = {k: row[k] for k in ("panel", "model", "contrast", "N_pairs", "delta", "both_valid_N", "both_valid_delta")}
        record.update(anchor_to_task_ci_width=cluster_width / task_width if task_width else None,
                      all_planned_and_both_valid_same_direction=float(row["delta"]) * float(row["both_valid_delta"]) >= 0)
        sensitivity.append(record)
    with (output / "sensitivity_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(sensitivity[0]))
        writer.writeheader()
        writer.writerows(sensitivity)
    result = {
        "raw_f1": [r for r in rows if r["panel"] == "raw" and r["metric"] == "f1"],
        "noise_f1": [r for r in rows if r["panel"] == "core" and r["metric"] == "f1" and r["contrast"] in {"noise_triples", "noise_text"}],
        "representation_f1": [r for r in rows if r["panel"] == "core" and r["metric"] == "f1" and r["contrast"] in {"format_slots", "format_goal"}],
        "placement_f1": [r for r in rows if r["panel"] == "core" and r["metric"] == "f1" and r["contrast"] in {"placement_object", "placement_both"}],
        "supplementary_f1": [r for r in rows if r["panel"] in {"size", "matched_incremental"} and r["metric"] == "f1"],
        "sensitivity_direction_changes": [r for r in sensitivity if not r["all_planned_and_both_valid_same_direction"]],
        "anchor_to_task_f1_interval_width_range": [min(r["anchor_to_task_ci_width"] for r in sensitivity if r["anchor_to_task_ci_width"]), max(r["anchor_to_task_ci_width"] for r in sensitivity if r["anchor_to_task_ci_width"])],
        "analytical_baselines": read(output / "analytical_baselines.csv"),
        "provenance": {"script_sha256": sha(Path(__file__)), "paired_contrasts_sha256": sha(output / "paired_contrasts.csv"),
                       "baseline_sha256": sha(output / "analytical_baselines.csv")},
        "interpretation_limits": "Exploratory fixed-KG task estimates and anchor-cluster uncertainty. No causal, repeated-generation, unseen-KG, or QA-performance claims."
    }
    (output / "findings.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"raw_models": len(result["raw_f1"]), "noise_contrasts": len(result["noise_f1"]), "sensitivity_direction_changes": len(result["sensitivity_direction_changes"])}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    args = parser.parse_args()
    main(args.analysis.resolve())
