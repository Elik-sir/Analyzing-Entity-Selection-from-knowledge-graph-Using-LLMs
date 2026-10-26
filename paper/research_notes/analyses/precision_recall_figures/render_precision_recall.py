"""Render publication figures from already selected archived precision/recall.

Only plotting and validation of saved aggregate rows; no inference or rescoring.
Original manuscript, figures and experimental archives are preserved.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "paper/research_notes/analyses/main_claim_assets/run-04"
MODELS = ["gemma-4-31b", "qwen3.6-flash", "ministral-14b"]
MODEL_LABELS = ["Gemma-4-31B", "Qwen3.6-Flash", "Ministral-14B"]
MOTIFS = ["chain", "star_in", "star_out", "tree_in", "tree_out", "rhombus", "hourglass"]
MOTIF_LABELS = ["Chain", "Star-in", "Star-out", "Tree-in", "Tree-out", "Rhombus", "Hourglass"]
BLUE, ORANGE, GREEN = "#2466A5", "#C36B1B", "#38856C"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    with (DATA / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def style(ax):
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#DDE2E7", linewidth=.65)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color("#A9B1B9")
    ax.tick_params(length=3, color="#A9B1B9")


def save(fig, name, out, caption):
    paths = []
    for suffix in ["png", "pdf", "svg"]:
        path = out / f"{name}.{suffix}"
        fig.savefig(path, dpi=300, facecolor="white")
        paths.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    plt.close(fig)
    return {"name": name, "paths": paths, "caption": caption, "status": "rendered_not_yet_visually_reviewed"}


def motif_figure(rows, out):
    fig, axes = plt.subplots(2, 3, figsize=(16.2, 8.5), sharey=True)
    fig.subplots_adjust(left=.065, right=.985, top=.81, bottom=.16, hspace=.48, wspace=.13)
    fig.suptitle("Selection profiles across graph-pattern task families", x=.065, y=.97, ha="left", fontsize=19, fontweight="bold")
    fig.text(.065, .923, "Recall and precision shown separately under explicit relations", fontsize=12, color="#4F5963")
    handles = [Line2D([], [], color=BLUE, marker="o", linestyle="none", markersize=7, label="K1: disconnected distractors"),
               Line2D([], [], color=ORANGE, marker="s", linestyle="none", markersize=7, label="K2: adjacent distractors")]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.06, .902), ncol=2, frameon=False, fontsize=11)
    lookup = {(r["model"], r["condition"], r["motif"]): r for r in rows}
    assert len(lookup) == len(rows) == 42
    for ri, metric in enumerate(["recall", "precision"]):
        for mi, model in enumerate(MODELS):
            ax = axes[ri, mi]
            style(ax)
            ax.axvspan(4.5, 6.5, facecolor="#F3F4F5", zorder=0)
            ax.axvline(4.5, color="#9BA3AB", linestyle=(0, (3, 3)), linewidth=.9)
            for condition, offset, color, marker in [("K1", -.12, BLUE, "o"), ("K2", .12, ORANGE, "s")]:
                values = [float(lookup[(model, condition, m)][metric]) for m in MOTIFS]
                assert all(0 <= v <= 1 for v in values)
                ax.scatter(np.arange(7) + offset, values, s=47, color=color, marker=marker, zorder=3, edgecolors="white", linewidths=.55)
            ax.set_xlim(-.5, 6.5)
            ax.set_ylim(-.025, 1.045)
            ax.set_yticks([0, .25, .5, .75, 1])
            ax.set_xticks(np.arange(7), [label + "\n" + ("n=4" if m == "rhombus" else "n=5" if m == "hourglass" else "n=6") for label, m in zip(MOTIF_LABELS, MOTIFS)])
            ax.tick_params(axis="x", labelsize=8.3)
            if ri == 0:
                ax.set_title(MODEL_LABELS[mi], fontsize=13, fontweight="bold", pad=10)
            if mi == 0:
                ax.set_ylabel("Mean per-task " + metric, fontsize=12, labelpad=10)
    caption = ("Archived Core K1/K2; 100 planned tasks per model/family/condition. Invalid outcomes contribute zero. "
               "Five families have six nodes; shaded Rhombus/Hourglass use four/five nodes and are not equal-size comparisons. "
               "Descriptive saved macro means; no uncertainty intervals or topology-causality claim.")
    fig.text(.065, .062, "Source: archived Core K1/K2 | 100 planned tasks per point | Invalid outcomes contribute zero", fontsize=10, color="#4F5963")
    fig.text(.065, .032, "Shaded families use different sizes. Saved macro means; descriptive profiles without uncertainty intervals.", fontsize=10, color="#4F5963")
    return save(fig, "01_motif_recall_precision", out, caption)


def size_figure(rows, metric, out):
    fig, axes = plt.subplots(3, 5, figsize=(16.6, 9.2), sharey=True)
    fig.subplots_adjust(left=.105, right=.985, top=.84, bottom=.14, hspace=.30, wspace=.15)
    fig.suptitle(f"{metric.capitalize()} across target-subgraph sizes", x=.105, y=.97, ha="left", fontsize=19, fontweight="bold")
    fig.text(.105, .923, "Native entity cards compared with explicit relation overlays", fontsize=12, color="#4F5963")
    handles = [Line2D([], [], color="#7C8792", marker="o", linestyle="--", markersize=5, label="Raw: native cards"),
               Line2D([], [], color=BLUE, marker="s", linestyle="-", markersize=5, label="Raw+E: explicit relations added")]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.10, .901), ncol=2, frameon=False, fontsize=11)
    used = []
    for mi, model in enumerate(MODELS):
        for fi, motif in enumerate(MOTIFS[:5]):
            ax = axes[mi, fi]
            style(ax)
            sizes = None
            for condition, color, marker, ls in [("Braw", "#7C8792", "o", "--"), ("Braw+E", BLUE, "s", "-")]:
                selected = sorted([r for r in rows if r["model"] == model and r["motif"] == motif and r["condition"] == condition], key=lambda r: int(r["size"]))
                assert selected and all(int(r["N"]) == 100 for r in selected)
                current = [int(r["size"]) for r in selected]
                if sizes is None:
                    sizes = current
                else:
                    assert sizes == current
                values = [float(r[metric]) for r in selected]
                assert all(0 <= v <= 1 for v in values)
                ax.plot(current, values, color=color, marker=marker, linestyle=ls, linewidth=1.65, markersize=4.1)
                used.extend(selected)
            ax.set_ylim(-.025, 1.045)
            ax.set_yticks([0, .25, .5, .75, 1])
            ax.set_xticks(sizes)
            ax.tick_params(axis="x", labelsize=8.5)
            if mi == 0:
                ax.set_title(MOTIF_LABELS[fi], fontsize=12, fontweight="bold", pad=9)
            if fi == 0:
                ax.set_ylabel(MODEL_LABELS[mi] + "\nMean " + metric, fontsize=10.5, labelpad=10)
    assert len(used) == len(rows) == 192
    fig.text(.54, .092, "Target-subgraph size (nodes)", ha="center", fontsize=12)
    fig.text(.105, .047, "Source: archived Full Raw/Raw+E | 100 planned tasks per point | 25 candidates | Invalid outcomes contribute zero", fontsize=9.8, color="#4F5963")
    fig.text(.105, .021, "Different sizes are different frozen samples, not paired graph expansions. Descriptive means; no uncertainty intervals.", fontsize=9.8, color="#4F5963")
    caption = (f"Archived Full Raw/Raw+E mean per-task {metric}; 100 planned tasks per model/motif/size/condition, with invalid outcomes zero. "
               "Raw+E adds facts. Sizes use different frozen task cohorts; fixed 25-candidate pools change target prevalence with size. "
               "All five variable-size families and three models are shown. No fitted size effect or uncertainty interval.")
    return save(fig, "02_size_recall" if metric == "recall" else "03_size_precision", out, caption)


def effects_figure(rows, out):
    fig, axes = plt.subplots(2, 3, figsize=(17.6, 9.2))
    fig.subplots_adjust(left=.15, right=.98, top=.825, bottom=.14, hspace=.48, wspace=.93)
    fig.suptitle("Descriptive changes in recall and precision", x=.065, y=.97, ha="left", fontsize=19, fontweight="bold")
    fig.text(.065, .923, "Differences of saved macro means on complete paired populations", fontsize=12, color="#4F5963")
    colors = [BLUE, ORANGE, GREEN]
    handles = [Line2D([], [], color=c, marker="o", linestyle="none", markersize=7, label=m) for c, m in zip(colors, MODEL_LABELS)]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.06, .90), ncol=3, frameon=False, fontsize=11)
    groups = [
        ("A  Relations added", ["raw_explicit"], ["Raw+E − Raw"]),
        ("B  Fact-preserving presentation", ["format_slots", "format_goal", "placement_object", "placement_both", "question_triples"],
         ["Text − triples\nprocedural question", "Text − triples\ndirect question", "Destination − source", "Both cards − source", "Direct − procedural\nquestion"]),
        ("C  Adjacent context", ["noise_triples", "noise_text"], ["Adjacent − disconnected\ntriples", "Adjacent − disconnected\ntext"]),
    ]
    lookup = {(r["model"], r["contrast"], r["metric"]): r for r in rows}
    assert len(lookup) == len(rows) == 48
    used = []
    for ci, (title, contrasts, labels) in enumerate(groups):
        max_abs = max(abs(float(r["delta"])) for r in rows if r["contrast"] in contrasts)
        limit = max(.05, math.ceil((max_abs + .012) / .05) * .05)
        for ri, metric in enumerate(["recall", "precision"]):
            ax = axes[ri, ci]
            style(ax)
            ax.grid(axis="y", visible=False)
            ax.grid(axis="x", color="#E1E5E9", linewidth=.65)
            ax.axvline(0, color="#4F5963", linewidth=1)
            for mi, model in enumerate(MODELS):
                selected = [lookup[(model, contrast, metric)] for contrast in contrasts]
                vals = [float(r["delta"]) for r in selected]
                for r in selected:
                    assert abs(float(r["right_mean"]) - float(r["left_mean"]) - float(r["delta"])) < 1e-12
                    assert r["interval_status"].startswith("not_computed")
                ax.scatter(vals, np.arange(len(contrasts)) + (mi - 1) * .18, color=colors[mi], s=40, zorder=3, edgecolors="white", linewidths=.45)
                used.extend(selected)
            ax.set_yticks(np.arange(len(contrasts)), labels)
            ax.tick_params(axis="y", labelsize=9.7)
            ax.set_ylim(len(contrasts) - .5, -.5)
            ax.set_xlim(-limit, limit)
            if ci == 0:
                # Preserve a common x scale for recall/precision in this column.
                ax.set_xlim(-.05, limit)
            ax.set_xlabel("Δ mean " + metric + " (score units)", fontsize=10)
            if ri == 0:
                ax.set_title(title, fontsize=11.5, fontweight="bold", pad=12)
            ax.text(.02, .96, metric.upper(), transform=ax.transAxes, fontsize=10, fontweight="bold", va="top", color="#4F5963")
    assert len(used) == 48
    fig.text(.065, .061, "Source: archived Full/Core panels | 3,400 pairs/model for A; 700 pairs/model for B and C | All planned outcomes retained", fontsize=10, color="#4F5963")
    fig.text(.065, .031, "Panels use different x-axis ranges. No uncertainty intervals were calculated for these metrics; significance is not asserted.", fontsize=10, color="#4F5963")
    caption = ("Precision/recall differences are right-minus-left saved macro means in complete paired populations: 3,400 Raw pairs/model or 700 Core pairs/model. "
               "Invalid outcomes retain zero contribution; no validity-conditioned deletion. Unique designated facts are held fixed in presentation contrasts, but repetition/length/salience may change. "
               "No confidence intervals, significance or interaction test. Axes differ between intervention groups but are shared between metrics within each group.")
    return save(fig, "04_condition_effects_recall_precision", out, caption)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--notes-out", required=True, type=Path)
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.notes_out = args.notes_out.resolve()
    assert not args.out.exists() and not args.notes_out.exists()
    previous = json.loads((DATA / "asset_manifest.json").read_text(encoding="utf-8"))
    for name, expected in previous["outputs_sha256"].items():
        assert sha(DATA / name) == expected
    args.out.mkdir(parents=True)
    args.notes_out.mkdir(parents=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12,
                         "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42,
                         "axes.unicode_minus": True, "savefig.bbox": None})
    motif, size, effects = read("motif_precision_recall.csv"), read("size_precision_recall.csv"), read("condition_precision_recall.csv")
    figures = [motif_figure(motif, args.out), size_figure(size, "recall", args.out),
               size_figure(size, "precision", args.out), effects_figure(effects, args.out)]
    manifest = {
        "checked_on": "2026-10-26", "scope": "Four figures rendered from selected historical precision/recall means; no manuscript change or new inference",
        "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "command": "python paper/research_notes/analyses/precision_recall_figures/render_precision_recall.py --out " + args.out.as_posix() + " --notes-out " + args.notes_out.as_posix(),
        "script_sha256": sha(Path(__file__)), "matplotlib": matplotlib.__version__,
        "sources": {str((DATA / name).relative_to(ROOT)).replace("\\", "/"): sha(DATA / name) for name in previous["outputs_sha256"]},
        "figures": figures, "files_sha256": {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in args.out.iterdir()},
        "validation": {"source_hashes": "passed", "motif_cells": 42, "size_cells_per_metric": 192, "condition_effects": 48,
                       "all_expected_rows_plotted_once_per_metric": "passed", "outcome_policy": "planned denominator; invalid zero",
                       "precision_recall_intervals": "absent and not drawn", "visual_inspection": "pending"},
    }
    (args.notes_out / "figure_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"figures": [f["name"] for f in figures], "files": len(manifest["files_sha256"]), "validation": manifest["validation"]}))


if __name__ == "__main__":
    main()
