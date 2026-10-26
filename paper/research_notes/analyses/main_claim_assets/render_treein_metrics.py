"""Export and render existing three-model Tree-in metrics; no new experiments."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[4]
MODELS = [("gemma-4-31b", "Gemma-4-31B"), ("qwen3.6-flash", "Qwen3.6-Flash"), ("ministral-14b", "Ministral-14B")]
CONDITIONS = [("K1", "Source cards"), ("K3", "Destination cards"), ("K4", "Both endpoint cards"), ("K7", "Direct query")]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--figures", type=Path, required=True)
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.figures = args.figures.resolve()
    assert not args.out.exists() and not args.figures.exists()
    source = ROOT / "paper/research_notes/analyses/final_results/run-01/motif_size_metrics.csv"
    with source.open(newline="", encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    rows, display = [], []
    fields = ["model", "condition", "N", "valid", "invalid", "precision", "recall", "exact", "raw_response_available", "cached_metrics_only"]
    for model, label in MODELS:
        for index, (condition, description) in enumerate(CONDITIONS):
            matches = [r for r in records if r["series_id"] == "core" and r["motif"] == "tree_in" and r["size"] == "6" and r["model"] == model and r["condition"] == condition]
            assert len(matches) == 1
            r = matches[0]
            assert int(r["N"]) == 100 and int(r["valid"]) + int(r["invalid"]) == 100
            assert all(0 <= float(r[m]) <= 1 for m in ["precision", "recall", "exact"])
            rows.append({k: r[k] for k in fields})
            display.append([label if index == 0 else "", condition + ": " + description,
                            *[f"{float(r[m]):.3f}" for m in ["precision", "recall", "exact"]], r["valid"] + " / " + r["N"]])
    assert len(rows) == 12
    args.out.mkdir(parents=True)
    args.figures.mkdir(parents=True)
    csv_path = args.out / "table2_treein_metrics_all_models.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42, "svg.fonttype": "none"})
    fig = plt.figure(figsize=(13.8, 8.5), facecolor="white")
    ax = fig.add_axes([.04, .24, .92, .58])
    ax.axis("off")
    fig.text(.04, .95, "Tree-in selection metrics across evidence-presentation conditions", fontsize=17, fontweight="bold", va="top")
    fig.text(.04, .897, "Three models · six-node references · 100 planned tasks per model/condition · scores on a 0–1 scale", fontsize=11.5, color="#4F5963")
    table = ax.table(cellText=display, colLabels=["Model", "Condition", "Precision", "Recall", "Exact", "Valid / N"],
                     colWidths=[.19, .33, .12, .12, .12, .12], cellLoc="left", loc="center", bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    for (ri, ci), cell in table.get_celld().items():
        cell.set_edgecolor("#DDE2E7")
        cell.set_linewidth(.45)
        cell.PAD = .10
        if ri == 0:
            cell.set_facecolor("#E8EDF2")
            cell.set_text_props(fontweight="bold")
        else:
            cell.set_facecolor("#F6F8FA" if (ri - 1) // 4 % 2 == 0 else "white")
            if ci >= 2:
                cell.set_text_props(ha="center")
    fig.text(.04, .183, "K1/K3/K4 retain the procedural query and vary relation hosting; K4 repeats each relation on both endpoint cards.", fontsize=10.3, color="#4F5963")
    fig.text(.04, .15, "K7 uses source-card relations and a direct query. Unique directed facts and targets match within each base task.", fontsize=10.3, color="#4F5963")
    fig.text(.04, .105, "All means use planned denominators; invalid outcomes contribute zero. Gemma values are saved aggregate scores.", fontsize=10.3, color="#4F5963")
    fig.text(.04, .072, "Source: archived Core, motif_size_metrics.csv. Descriptive values; no new confidence intervals or model calls.", fontsize=10.3, color="#4F5963")
    files = []
    for suffix in ["png", "pdf", "svg"]:
        p = args.figures / ("table2_treein_metrics_all_models." + suffix)
        fig.savefig(p, dpi=300, facecolor="white")
        files.append(p)
    plt.close(fig)
    manifest = {"checked_on": "2026-10-26", "scope": "Existing per-task aggregate precision/recall/exact for Core six-node Tree-in only; all three models",
                "source": {"path": str(source.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(source),
                           "selector": "series_id=core,motif=tree_in,size=6; all three models; K1/K3/K4/K7"},
                "script_sha256": sha(Path(__file__)), "csv_sha256": sha(csv_path),
                "figures": {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in files},
                "policy": "Saved all-planned macro means; invalid zero; exact is complete-set recovery. No rescoring, inference or manuscript changes.",
                "validation": {"unique_cells": 12, "planned_per_cell": 100, "planned_equals_valid_plus_invalid": True, "visual_review": "pending"}}
    (args.out / "table_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["validation"]))


if __name__ == "__main__":
    main()
