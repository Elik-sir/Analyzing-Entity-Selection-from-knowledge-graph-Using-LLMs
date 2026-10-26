"""Export saved macro precision/recall and descriptive condition differences.

No raw-response rescoring, inference or model/database calls. Existing F1/exact
bootstrap intervals are intentionally excluded from precision/recall outputs.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
FAMILIES = {"chain", "star_in", "star_out", "tree_in", "tree_out"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    assert not args.out.exists()
    sources = {
        "strata": ROOT / "paper/research_notes/analyses/final_results/run-01/motif_size_metrics.csv",
        "conditions": ROOT / "paper/research_notes/analyses/final_results/run-01/condition_metrics.csv",
        "paired_design": ROOT / "paper/research_notes/analyses/main_claim_assets/run-02/figure1_condition_effects.csv",
    }
    strata = read(sources["strata"])
    keys = ["series_id", "model", "condition", "noise", "motif", "size", "N", "valid", "invalid",
            "raw_response_available", "cached_metrics_only", "precision", "precision_valid_only",
            "recall", "recall_valid_only", "exact", "exact_valid_only"]
    motif = [{k: r[k] for k in keys} for r in strata if r["series_id"] == "core" and r["condition"] in {"K1", "K2"}]
    size = [{k: r[k] for k in keys} for r in strata if r["series_id"] == "full_braw" and r["condition"] in {"Braw", "Braw+E"} and r["motif"] in FAMILIES]
    assert len(motif) == 42 and len(size) == 192
    assert all(int(r["N"]) == 100 for r in motif + size)
    assert len({tuple(r[k] for k in keys[:6]) for r in motif + size}) == len(motif + size)
    conditions = read(sources["conditions"])
    lookup = {}
    for r in conditions:
        if r["series_id"] not in {"core", "full_braw"}:
            continue  # Other series may repeat conditions across noise strata.
        key = (r["series_id"], r["model"], r["condition"])
        assert key not in lookup
        lookup[key] = r
    effects = []
    for r in read(sources["paired_design"]):
        a = lookup[(r["series_id"], r["model"], r["left"])]
        b = lookup[(r["series_id"], r["model"], r["right"])]
        assert a["N"] == b["N"] == r["N_pairs"]
        assert a["valid"] == r["left_valid"] and b["valid"] == r["right_valid"]
        # Verify the condition-mean mapping against the original paired export.
        assert abs(float(b["f1"]) - float(a["f1"]) - float(r["delta"])) < 1e-12
        for metric in ["precision", "recall"]:
            left, right = float(a[metric]), float(b[metric])
            assert 0 <= left <= 1 and 0 <= right <= 1
            effects.append({"figure_panel": r["figure_panel"], "series_id": r["series_id"],
                            "model": r["model"], "contrast": r["contrast"], "left": r["left"], "right": r["right"],
                            "metric": metric, "N_pairs": r["N_pairs"], "left_valid": a["valid"], "right_valid": b["valid"],
                            "left_mean": left, "right_mean": right, "delta": right - left,
                            "interval_status": "not_computed; descriptive_difference_only"})
    assert len(effects) == 48
    args.out.mkdir(parents=True)
    write(args.out / "motif_precision_recall.csv", motif)
    write(args.out / "size_precision_recall.csv", size)
    write(args.out / "condition_precision_recall.csv", effects)
    manifest = {
        "checked_on": "2026-10-26", "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "scope": "Saved precision/recall selection and arithmetic descriptive differences only; no experiment, reparse, bootstrap or hypothesis test",
        "command": "python paper/research_notes/analyses/main_claim_assets/select_precision_recall.py --out " + args.out.as_posix(),
        "sources": {k: {"path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(p)} for k, p in sources.items()},
        "script_sha256": sha(Path(__file__)),
        "metrics": {"precision": "Saved mean of per-task precision, with invalid outcomes retained as zero over planned N",
                    "recall": "Saved mean of per-task recall, with invalid outcomes retained as zero over planned N",
                    "delta": "right_mean minus left_mean on complete paired populations; mapping checked against saved paired F1 deltas",
                    "exact": "Retained as secondary complete-set recovery, not a synonym for precision or recall"},
        "uncertainty": "No precision/recall intervals in existing uncertainty exports; F1/exact bands must not be reused",
        "validation": {"motif_cells": len(motif), "size_cells": len(size), "metric_contrasts": len(effects),
                       "planned_counts_and_pair_mapping": "passed", "condition_mean_mapping_against_existing_F1_export": "passed"},
        "outputs_sha256": {p.name: sha(p) for p in args.out.glob("*.csv")},
        "rendering_status": "data_ready; precision_recall_figures_not_rendered; old_F1_PDFs_preserved",
    }
    (args.out / "asset_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["validation"]))


if __name__ == "__main__":
    main()
