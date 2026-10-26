"""Clearer preview of Figure 3 from existing cached outcome-category counts.

Task-level error occurrence is not a node-level recall/precision deficit.
Mixed outcomes contribute to both non-exclusive panels; invalids only to N.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
MODELS = ["gemma-4-31b", "qwen3.6-flash", "ministral-14b"]
NAMES = ["Gemma", "Qwen", "Ministral"]
MOTIFS = ["chain", "star_in", "star_out", "tree_in", "tree_out"]
LABELS = ["Chain", "Star-in", "Star-out", "Tree-in", "Tree-out"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--figures", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.figures = args.figures.resolve()
    args.out = args.out.resolve()
    assert not args.figures.exists() and not args.out.exists()
    source = ROOT / "paper/research_notes/analyses/main_claim_assets/run-02/figure2_error_composition.csv"
    with source.open(newline="", encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    lookup = {(r["model"], r["motif"], r["condition"]): r for r in records}
    assert len(lookup) == len(records) == 30
    exported = []
    matrices = [np.zeros((10, 3)), np.zeros((10, 3))]
    for i, motif in enumerate(MOTIFS):
        for j, condition in enumerate(["K1", "K2"]):
            for k, model in enumerate(MODELS):
                r = lookup[(model, motif, condition)]
                assert int(r["planned"]) == 100
                assert sum(int(r[c]) for c in ["exact", "omission_only", "inclusion_only", "mixed", "invalid"]) == 100
                fn_tasks = int(r["omission_only"]) + int(r["mixed"])
                fp_tasks = int(r["inclusion_only"]) + int(r["mixed"])
                matrices[0][i * 2 + j, k] = fn_tasks
                matrices[1][i * 2 + j, k] = fp_tasks
                exported.append({"model": model, "motif": motif, "condition": condition,
                                 "N": 100, "valid": r["valid"], "invalid": r["invalid"],
                                 "tasks_with_omissions": fn_tasks, "tasks_with_extras": fp_tasks,
                                 "percentage_denominator": 100})
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "pdf.fonttype": 42, "svg.fonttype": "none"})
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.8))
    fig.subplots_adjust(left=.20, right=.95, top=.78, bottom=.23, wspace=.56)
    fig.text(.055, .945, "How often does a task contain a selection error?", fontsize=13.5, fontweight="bold")
    fig.text(.055, .885, "Cell values are percentages of 100 planned tasks, not recall or precision.", fontsize=9.5, color="#4F5963")
    ylabels = [label + ("  K1" if c == "K1" else "  K2") for label in LABELS for c in ["K1", "K2"]]
    for index, (ax, matrix, cmap, title) in enumerate(zip(axes, matrices, ["Blues", "Oranges"], ["Missing required entities", "Extra selected entities"])):
        im = ax.imshow(matrix, vmin=0, vmax=100, cmap=cmap, aspect="auto")
        ax.set_title(title, fontsize=10.5, pad=8)
        ax.set_xticks(range(3), NAMES, fontsize=9)
        ax.set_yticks(range(10), ylabels if index == 0 else [""] * 10, fontsize=9)
        ax.tick_params(length=0, pad=5)
        for y in [1.5, 3.5, 5.5, 7.5]:
            ax.axhline(y, color="white", linewidth=2)
        for y in range(10):
            for x in range(3):
                v = matrix[y, x]
                ax.text(x, y, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                        color="white" if v >= 58 else "#24303A")
        for spine in ax.spines.values():
            spine.set_visible(False)
        cb = fig.colorbar(im, ax=ax, fraction=.055, pad=.035, ticks=[0, 50, 100])
        cb.ax.tick_params(labelsize=8, length=2)
    fig.text(.055, .145, "K1: disconnected distractors; K2: adjacent distractors. All references contain six nodes.", fontsize=9, color="#4F5963")
    fig.text(.055, .102, "A mixed-error task appears in both panels. Invalid outcomes stay in the denominator and are not labelled FN/FP.", fontsize=8.2, color="#4F5963")
    fig.text(.055, .06, "Source: saved Core outcome counts. Descriptive proportions; no new model calls or uncertainty tests.", fontsize=8.5, color="#4F5963")
    args.figures.mkdir(parents=True)
    args.out.mkdir(parents=True)
    files = []
    for ext in ["png", "pdf", "svg"]:
        p = args.figures / ("figure3_task_errors." + ext)
        fig.savefig(p, dpi=300, facecolor="white")
        files.append(p)
    plt.close(fig)
    csv_path = args.out / "task_error_occurrence.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(exported[0]))
        writer.writeheader()
        writer.writerows(exported)
    manifest = {"checked_on": "2026-10-26", "scope": "Alternative Figure 3 preview only; manuscript/PDF not modified",
                "source": {"path": str(source.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(source)},
                "script_sha256": sha(Path(__file__)), "data_sha256": sha(csv_path),
                "formulas": {"tasks_with_omissions": "omission_only + mixed", "tasks_with_extras": "inclusion_only + mixed", "percent": "count / all planned N * 100; N=100 in every cell"},
                "invalid_counts": [{k: r[k] for k in ["model", "motif", "condition", "invalid"]} for r in records if int(r["invalid"])],
                "outputs": {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in files},
                "new_inference": False, "visual_review": "pending"}
    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_cells": len(records), "panels": 2, "manuscript_changed": False}))


if __name__ == "__main__":
    main()
