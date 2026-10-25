"""Reproducible archived results, paired uncertainty, and analytical baselines.

No research-module imports, API calls, database access or model experiments.
"""

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import argparse
import csv
import gzip
import hashlib
import json
import math
import platform
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from uncertainty import bootstrap_means, percentile_interval, simultaneous_bands

METRICS = ("precision", "recall", "f1", "exact")
MODELS = ("gemma-4-31b", "qwen3.6-flash", "ministral-14b")
CORE_CONDITIONS = ("K0", "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K5k", "R0", "R1-matched", "R2-matched")
CONTRASTS = (
    ("format_slots", "K1", "K5", "Text minus triples; step-by-step"),
    ("format_goal", "K7", "K8", "Text minus triples; direct question"),
    ("noise_triples", "K1", "K2", "Adjacent minus disconnected; triples"),
    ("noise_text", "K5", "K6", "Adjacent minus disconnected; text"),
    ("placement_object", "K1", "K3", "Destination minus source cards"),
    ("placement_both", "K1", "K4", "Both minus source cards"),
    ("question_triples", "K1", "K7", "Direct minus step-by-step; triples"),
    ("question_text", "K5", "K8", "Direct minus step-by-step; text"),
    ("names_disconnected", "R1-matched", "K1", "Pseudonyms minus real names; disconnected"),
    ("names_adjacent", "R2-matched", "K2", "Pseudonyms minus real names; adjacent"),
    ("names_closed", "R0", "K0", "Pseudonyms minus real names; closed book"),
    ("text_keys", "K5", "K5k", "Linked attributes minus templated text"),
)


def read_rows(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, data):
    if not data:
        raise ValueError("Do not emit an empty table")
    keys = list(dict.fromkeys(k for row in data for k in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


def metric(row, name):
    return float(row["metrics"].get(name) or 0) if row["valid"] else 0.0


def summarize(observations, dimensions):
    groups = defaultdict(list)
    for row in observations:
        groups[tuple(row[k] for k in dimensions)].append(row)
    result = []
    for key, values in sorted(groups.items(), key=lambda item: str(item[0])):
        record = dict(zip(dimensions, key))
        n = len(values)
        valid = [v for v in values if v["valid"]]
        record.update(N=n, valid=len(valid), invalid=n - len(valid), valid_fraction=len(valid) / n,
                      raw_response_available=sum(v["response_id"] is not None for v in values),
                      cached_metrics_only=sum(v["response_evidence"] == "metrics_cache_only_no_raw_response" for v in values))
        for name in METRICS:
            record[name] = sum(metric(v, name) for v in values) / n
            record[name + "_valid_only"] = sum(metric(v, name) for v in valid) / len(valid) if valid else None
        result.append(record)
    return result


def load_metadata(root):
    metadata = {}
    for payload in read_rows(root / "results/inputs.jsonl.gz"):
        private = payload["reference"].get("private", payload["reference"])
        task = private.get("task_spec")
        if task:
            info = {"anchor_id": task["anchor_id"], "reference_ids": task["reference_ids"]}
            if task["record_id"] in metadata and metadata[task["record_id"]] != info:
                raise ValueError("Inconsistent frozen task metadata")
            metadata[task["record_id"]] = info
    return metadata


def dependence(items, metadata):
    anchors = Counter(metadata[b]["anchor_id"] for b in items)
    owner, parent = {}, {b: b for b in items}

    def find(b):
        while parent[b] != b:
            parent[b] = parent[parent[b]]
            b = parent[b]
        return b

    for base in items:
        for entity in metadata[base]["reference_ids"]:
            if entity in owner:
                a, b = find(base), find(owner[entity])
                parent[a] = b
            else:
                owner[entity] = base
    components = Counter(find(b) for b in items)
    return {"base_tasks": len(items), "anchors": len(anchors), "max_tasks_per_anchor": max(anchors.values()),
            "anchor_cluster_size_counts": dict(Counter(anchors.values())),
            "reference_entities": len(owner), "reference_overlap_components": len(components),
            "largest_reference_overlap_component": max(components.values()),
            "motif_anchors": {m: len({metadata[b]["anchor_id"] for b, v in items.items() if v["motif"] == m})
                              for m in sorted({v["motif"] for v in items.values()})}}


def paired_panel(name, observations, series, models, conditions, metadata, *, base_subset=None):
    lookup = {}
    for row in observations:
        if row["series_id"] == series and row["model"] in models and row["condition"] in conditions:
            if base_subset is not None and row["base_id"] not in base_subset:
                continue
            key = (row["base_id"], row["model"], row["condition"])
            if key in lookup:
                raise ValueError("Panel requires a noise stratum key")
            lookup[key] = row
    bases = sorted({k[0] for k in lookup})
    columns = [(model, condition, metric_name) for model in models for condition in conditions for metric_name in ("f1", "exact")]
    values = np.array([[metric(lookup[(base, model, condition)], metric_name) for model, condition, metric_name in columns] for base in bases])
    primary = [lookup[(b, models[0], conditions[0])] for b in bases]
    strata = np.array([r["motif"] + ":" + str(r["size"]) for r in primary])
    clusters = np.array([metadata[b]["anchor_id"] for b in bases])
    return dict(name=name, series=series, models=models, conditions=conditions, bases=bases,
                lookup=lookup, columns=columns, values=values, strata=strata, clusters=clusters)


def analyze_panel(panel, specs, *, replicates, seed, joint_family):
    values, columns = panel["values"], panel["columns"]
    anchor_samples, anchor_info = bootstrap_means(values, panel["strata"], panel["clusters"], replicates=replicates, seed=seed, mode="anchor")
    task_samples, task_info = bootstrap_means(values, panel["strata"], panel["clusters"], replicates=replicates, seed=seed + 1, mode="task")
    point, anchor_ci = values.mean(axis=0), percentile_interval(anchor_samples)
    means = []
    for index, (model, condition, name) in enumerate(columns):
        rows = [panel["lookup"][(b, model, condition)] for b in panel["bases"]]
        means.append({"panel": panel["name"], "series_id": panel["series"], "model": model,
                      "condition": condition, "metric": name, "N": len(rows), "valid": sum(r["valid"] for r in rows),
                      "mean": float(point[index]), "cluster_ci_low": float(anchor_ci[0, index]),
                      "cluster_ci_high": float(anchor_ci[1, index]), "clusters": anchor_info["anchor_clusters"],
                      "interval": "pointwise 95% paired anchor-cluster percentile bootstrap"})
    effects, anchor_effects, task_effects, records = [], [], [], []
    for cid, left, right, description in specs:
        for model in panel["models"]:
            paired = [(panel["lookup"][(b, model, left)], panel["lookup"][(b, model, right)]) for b in panel["bases"]]
            both = [(a, b) for a, b in paired if a["valid"] and b["valid"]]
            for name in ("f1", "exact"):
                a, b = columns.index((model, left, name)), columns.index((model, right, name))
                estimate = float(point[b] - point[a])
                effects.append(estimate)
                anchor_effects.append(anchor_samples[:, b] - anchor_samples[:, a])
                task_effects.append(task_samples[:, b] - task_samples[:, a])
                records.append({"panel": panel["name"], "series_id": panel["series"], "model": model,
                                "contrast": cid, "left": left, "right": right, "direction": description,
                                "metric": name, "N_pairs": len(paired), "left_valid": sum(a["valid"] for a, b in paired),
                                "right_valid": sum(b["valid"] for a, b in paired), "both_valid_N": len(both),
                                "left_mean": float(point[a]), "right_mean": float(point[b]), "delta": estimate,
                                "both_valid_delta": sum(metric(b, name) - metric(a, name) for a, b in both) / len(both) if both else None})
    anchor_effects, task_effects = np.column_stack(anchor_effects), np.column_stack(task_effects)
    aci, tci = percentile_interval(anchor_effects), percentile_interval(task_effects)
    low, high, sd, band = simultaneous_bands(effects, anchor_effects, panel_coverage=0.975 if joint_family else 0.95)
    for i, row in enumerate(records):
        row.update(cluster_ci_low=float(aci[0, i]), cluster_ci_high=float(aci[1, i]),
                   task_ci_low=float(tci[0, i]), task_ci_high=float(tci[1, i]),
                   simultaneous_low=float(low[i]) if joint_family else None,
                   simultaneous_high=float(high[i]) if joint_family else None,
                   bootstrap_sd=float(sd[i]), degenerate_sd=bool(sd[i] <= 1e-12),
                   clusters=anchor_info["anchor_clusters"], strata=anchor_info["strata"],
                   family="main_78_F1_exact_two_panels_union_bound" if joint_family else "supplementary_pointwise_only")
    # Keep bootstrap distributions for independent interval/MC diagnostics.
    distributions = {"anchor_effects": anchor_effects, "task_effects": task_effects,
                     "anchor_means": anchor_samples, "effect_estimates": np.asarray(effects)}
    provenance = {"anchor": anchor_info, "task": task_info, "simultaneous": band if joint_family else None,
                  "first_half_vs_second_half_pointwise_endpoint_max_abs_difference": float(np.max(np.abs(percentile_interval(anchor_effects[:replicates // 2]) - percentile_interval(anchor_effects[replicates // 2:]))))}
    return means, records, distributions, provenance


def analytical_baselines(observations, metadata):
    tasks = {}
    for row in observations:
        if (row["series_id"], row["model"], row["condition"]) in {
                ("core", MODELS[0], "K1"), ("full_braw", MODELS[0], "Braw")}:
            tasks[(row["series_id"], row["base_id"])] = row
    groups = defaultdict(list)
    for (series, base), row in tasks.items():
        gold, n, k = len(metadata[base]["reference_ids"]), 25, 6
        candidates = {
            "select_all": dict(precision=gold / n, recall=1.0, f1=2 * gold / (n + gold), exact=float(gold == n)),
            "select_named_anchor": dict(precision=1.0, recall=1 / gold, f1=2 / (1 + gold), exact=float(gold == 1)),
            "uniform_random_k6_expectation": dict(precision=gold / n, recall=k / n,
                                                  f1=2 * k * gold / (n * (k + gold)),
                                                  exact=1 / math.comb(n, gold) if k == gold else 0.0),
        }
        for baseline, scores in candidates.items():
            groups[(series, baseline)].append(scores)
    return [{"series_id": series, "baseline": baseline, "N_bases": len(values),
             "scope": "analytical set-selection reference, not an executed LLM",
             **{m: sum(v[m] for v in values) / len(values) for m in METRICS}}
            for (series, baseline), values in sorted(groups.items())]


def supplementary_pairs(observations, metadata, replicates, seed):
    # Size is already a complete paired representation panel.
    size = paired_panel("size", observations, "size", (MODELS[0],), ("K1", "K5"), metadata)
    sm, sc, sd, sp = analyze_panel(size, [("size_text_vs_triples", "K1", "K5", "Text minus triples; additional sizes")], replicates=replicates, seed=seed, joint_family=False)
    # Incremental static and incremental series need explicit same-base matching.
    matched_rows = []
    for source, target in (("K7", "K7-inc"), ("K8", "K8-inc")):
        subset = {r["base_id"] for r in observations if r["series_id"] == "incremental" and r["condition"] == target}
        for row in observations:
            if row["model"] != MODELS[0] or row["base_id"] not in subset:
                continue
            if (row["series_id"], row["condition"]) in {("core", source), ("incremental", target)}:
                matched_rows.append({**row, "series_id": "matched_incremental"})
    inc = paired_panel("matched_incremental", matched_rows, "matched_incremental", (MODELS[0],), ("K7", "K7-inc", "K8", "K8-inc"), metadata)
    im, ic, ids, ip = analyze_panel(inc, [("incremental_triples", "K7", "K7-inc", "Incremental minus static; triples"), ("incremental_text", "K8", "K8-inc", "Incremental minus static; text")], replicates=replicates, seed=seed + 10, joint_family=False)
    return sm + im, sc + ic, {"size": sd, "matched_incremental": ids}, {"size": sp, "matched_incremental": ip}


def run(root, output, *, replicates, seed):
    if output.exists():
        raise ValueError("Choose a fresh analysis output directory")
    output.mkdir(parents=True)
    observations = list(read_rows(root / "results/observations.jsonl.gz"))
    metadata = load_metadata(root)
    groups = defaultdict(dict)
    for row in observations:
        if row["series_id"] in {"core", "full_braw", "size", "incremental"}:
            if row["base_id"] not in metadata:
                raise ValueError("Missing source anchor/reference metadata")
            groups[row["series_id"]][row["base_id"]] = row
    dependence_info = {s: dependence(v, metadata) for s, v in groups.items()}
    condition = summarize(observations, ("series_id", "model", "condition", "noise"))
    detail = summarize(observations, ("series_id", "model", "condition", "noise", "motif", "size"))
    write_csv(output / "condition_metrics.csv", condition)
    write_csv(output / "motif_size_metrics.csv", detail)
    write_csv(output / "analytical_baselines.csv", analytical_baselines(observations, metadata))
    write_json(output / "dependence_audit.json", dependence_info)
    means, contrasts, provenance = [], [], {}
    for name, series, conditions, specs, panel_seed in (
            ("core", "core", CORE_CONDITIONS, CONTRASTS, seed),
            ("raw", "full_braw", ("Braw", "Braw+E"), (("raw_explicit", "Braw", "Braw+E", "Raw+E minus Raw"),), seed + 100)):
        panel = paired_panel(name, observations, series, MODELS, conditions, metadata)
        m, c, distribution, p = analyze_panel(panel, specs, replicates=replicates, seed=panel_seed, joint_family=True)
        means.extend(m)
        contrasts.extend(c)
        provenance[name] = p
        np.savez_compressed(output / (name + "_bootstrap.npz"), **distribution)
        write_json(output / (name + "_columns.json"), {"means": panel["columns"], "effects": [{k: row[k] for k in ("contrast", "model", "metric")} for row in c]})
    extra_means, extra_contrasts, extra_distributions, extra_provenance = supplementary_pairs(observations, metadata, replicates, seed + 200)
    means.extend(extra_means)
    contrasts.extend(extra_contrasts)
    provenance.update(extra_provenance)
    for name, distribution in extra_distributions.items():
        np.savez_compressed(output / (name + "_bootstrap.npz"), **distribution)
    write_csv(output / "mean_intervals.csv", means)
    write_csv(output / "paired_contrasts.csv", contrasts)
    evidence = Counter((r["series_id"], r["model"], r["request_evidence"], r["response_evidence"]) for r in observations)
    write_csv(output / "evidence_coverage.csv", [{"series_id": k[0], "model": k[1], "request_evidence": k[2], "response_evidence": k[3], "N": v} for k, v in sorted(evidence.items())])
    status = Counter((r["series_id"], r["model"], r["status"]) for r in observations)
    write_csv(output / "status_counts.csv", [{"series_id": k[0], "model": k[1], "status": k[2], "N": v} for k, v in sorted(status.items())])
    sources = ["results/observations.jsonl.gz", "results/inputs.jsonl.gz", "results/MANIFEST.json", "graph_motives/report.py"]
    manifest = {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
                "python": platform.python_version(), "numpy": np.__version__, "seed": seed, "replicates": replicates,
                "observations": len(observations), "condition_groups": len(condition), "detailed_groups": len(detail),
                "metric_policy": "sum valid per-task score / all planned N; invalid contributes zero",
                "quantile_method": "numpy linear", "delta": "right minus left, score units",
                "main_simultaneous_family": {"effects": 78, "panel_family_coverage": 0.975, "combined_nominal_coverage_at_least": 0.95,
                                             "method": "separate centered max-standardized-deviation bands; two-panel union bound"},
                "bootstrap": provenance, "source_sha256": {p: sha(root / p) for p in sources},
                "script_sha256": {p.name: sha(p) for p in (Path(__file__), Path(__file__).with_name("uncertainty.py"))},
                "analysis_kind": "exploratory reanalysis of archived cached scores; no new LLM experiments",
                "limitations": ["Anchor-cluster independence is an assumption; shared entities link most tasks.",
                                "Intervals condition on one fixed KG, frozen task grid and saved model outcomes.",
                                "Bootstrap variation does not represent repeated API generations or unseen graphs.",
                                "Valid-only comparisons condition on success and can select different/easier populations.",
                                "Zero-variance bootstrap intervals are not guarantees of zero population error.",
                                "No p-values, causal effects or downstream QA improvements are inferred."]}
    write_json(output / "provenance.json", manifest)
    print(json.dumps({"observations": len(observations), "condition_groups": len(condition), "detailed_groups": len(detail),
                      "main_effects": sum(r["family"].startswith("main_") for r in contrasts), "all_contrast_rows": len(contrasts)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replicates", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20261025)
    args = parser.parse_args()
    run(args.root.resolve(), args.output.resolve(), replicates=args.replicates, seed=args.seed)
