"""Publication layouts and TeX tables from existing, checked aggregate rows."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
NOTES = ROOT / "paper/research_notes"
OUT = ROOT / "paper/manuscript"
PROV = Path(__file__).parent / "run-01"
FIG = ROOT / "paper/figures/recall_manuscript_v1"
MODELS = ["gemma-4-31b", "qwen3.6-flash", "ministral-14b"]
NAMES = ["Gemma", "Qwen", "Ministral"]
MOTIFS = ["chain", "star_in", "star_out", "tree_in", "tree_out", "rhombus", "hourglass"]
LABELS = ["Chain", "Star-in", "Star-out", "Tree-in", "Tree-out", "Rhombus", "Hourglass"]
BLUE, ORANGE = "#2466A5", "#C36B1B"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def one(rows, **selector):
    matches = [r for r in rows if all(r[k] == str(v) for k, v in selector.items())]
    assert len(matches) == 1, selector
    return matches[0]


def style(ax):
    ax.grid(axis="y", color=".88", linewidth=.45)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    for side in ["bottom", "left"]:
        ax.spines[side].set_color(".65")


def main():
    sources = {
        "motif": NOTES / "analyses/main_claim_assets/run-04/motif_precision_recall.csv",
        "size": NOTES / "analyses/main_claim_assets/run-04/size_precision_recall.csv",
        "effects": NOTES / "analyses/main_claim_assets/run-04/condition_precision_recall.csv",
        "errors": NOTES / "analyses/main_claim_assets/run-02/figure2_error_composition.csv",
        "treein": NOTES / "analyses/main_claim_assets/run-06/table2_treein_recall.csv",
        "conditions": NOTES / "analyses/final_results/run-01/condition_metrics.csv",
        "transitions": NOTES / "analyses/main_claim_assets/run-02/table2_signature_transitions.csv",
    }
    data = {k: read(p) for k, p in sources.items()}
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9,
                         "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
                         "svg.fonttype": "none", "pdf.fonttype": 42})
    assets = []

    def save(fig, name, rows, metric):
        files = {}
        for ext in ["png", "pdf", "svg"]:
            p = FIG / (name + "." + ext)
            fig.savefig(p, dpi=300, facecolor="white")
            files[str(p.relative_to(ROOT)).replace("\\", "/")] = sha(p)
        shutil.copyfile(FIG / (name + ".pdf"), OUT / "figures" / (name + ".pdf"))
        plt.close(fig)
        assets.append({"id": name, "metric": metric, "source_rows": rows, "files": files})

    for metric in ["recall", "precision"]:
        fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.15), sharey=True)
        fig.subplots_adjust(left=.075, right=.98, bottom=.30, top=.81, wspace=.14)
        for j, (model, name) in enumerate(zip(MODELS, NAMES)):
            ax = axes[j]
            style(ax)
            ax.axvspan(4.5, 6.5, color=".95", zorder=0)
            ax.axvline(4.5, color=".6", linestyle=":", linewidth=.7)
            for condition, offset, color, marker in [("K1", -.10, BLUE, "o"), ("K2", .10, ORANGE, "s")]:
                rs = [one(data["motif"], model=model, motif=m, condition=condition) for m in MOTIFS]
                ax.scatter(np.arange(7) + offset, [float(r[metric]) for r in rs], color=color,
                           marker=marker, s=15, label=condition, linewidths=.25, edgecolors="white", zorder=3)
            ax.set_title(name)
            ax.set_xlim(-.5, 6.5)
            ax.set_ylim(-.025, 1.045)
            ax.set_yticks([0, .5, 1])
            ax.set_xticks(range(7), LABELS, rotation=40, ha="right")
            if j == 0:
                ax.set_ylabel("Mean " + metric)
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, ["K1: disconnected", "K2: adjacent"], loc="upper center", ncol=2,
                   bbox_to_anchor=(.5, .995), frameon=False, fontsize=7)
        save(fig, metric + "_motifs", data["motif"], metric)

        fig, axes = plt.subplots(3, 5, figsize=(7.1, 3.65), sharey=True)
        fig.subplots_adjust(left=.09, right=.98, bottom=.13, top=.90, wspace=.17, hspace=.40)
        for i, (model, name) in enumerate(zip(MODELS, NAMES)):
            for j, (motif, label) in enumerate(zip(MOTIFS[:5], LABELS[:5])):
                ax = axes[i, j]
                style(ax)
                for condition, color, ls, marker in [("Braw", "#7C8792", "--", "o"), ("Braw+E", BLUE, "-", "s")]:
                    rs = sorted([r for r in data["size"] if r["model"] == model and r["motif"] == motif and r["condition"] == condition], key=lambda r: int(r["size"]))
                    xs = [int(r["size"]) for r in rs]
                    assert rs and all(int(r["N"]) == 100 for r in rs)
                    ax.plot(xs, [float(r[metric]) for r in rs], color=color, linestyle=ls, marker=marker,
                            markersize=2.3, linewidth=.95, label="Raw" if condition == "Braw" else "Raw+E")
                ax.set_xticks([min(xs), max(xs)])
                ax.set_ylim(-.025, 1.045)
                ax.set_yticks([0, .5, 1])
                if i == 0:
                    ax.set_title(label)
                if j == 0:
                    ax.set_ylabel(name + "\n" + metric.capitalize(), fontsize=7.5)
                if i == 2:
                    ax.set_xlabel("Nodes", fontsize=7)
        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="upper center", ncol=2, bbox_to_anchor=(.5, .995), frameon=False, fontsize=7)
        save(fig, metric + "_sizes", data["size"], metric)

    # Categorical outcomes are saved cached fp/fn categories, not mental traces.
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.65), sharey=True)
    fig.subplots_adjust(left=.11, right=.975, bottom=.22, top=.81, wspace=.15)
    categories = ["exact", "omission_only", "inclusion_only", "mixed", "invalid"]
    colors = ["#CDD2D8", BLUE, ORANGE, "#8E739F", "#30343B"]
    ylabels = [label + " " + c for label in LABELS[:5] for c in ["K1", "K2"]]
    for j, (model, name) in enumerate(zip(MODELS, NAMES)):
        ax = axes[j]
        rs = [one(data["errors"], model=model, motif=m, condition=c) for m in MOTIFS[:5] for c in ["K1", "K2"]]
        assert all(sum(int(r[c]) for c in categories) == 100 for r in rs)
        left = np.zeros(10)
        for category, color in zip(categories, colors):
            vals = np.array([int(r[category]) for r in rs])
            ax.barh(range(10), vals, left=left, height=.78, color=color, label=category)
            left += vals
        ax.set_xlim(0, 100)
        ax.set_ylim(9.65, -.65)
        ax.set_xticks([0, 50, 100])
        ax.set_yticks(range(10), ylabels, fontsize=6.4)
        ax.set_xlabel("Planned tasks (%)", fontsize=7)
        ax.set_title(name)
        ax.spines[["top", "right"]].set_visible(False)
        if j > 0:
            ax.tick_params(axis="y", labelleft=False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, ["Exact", "Omission only", "Inclusion only", "Mixed", "Invalid"],
               loc="upper center", bbox_to_anchor=(.5, 1.0), ncol=5, frameon=False, fontsize=6.5,
               handlelength=1.1, columnspacing=1.1)
    save(fig, "residual_errors", data["errors"], "saved fp/fn category")

    tables = {}
    contrasts = ["raw_explicit", "noise_triples", "noise_text", "format_slots", "format_goal", "placement_object", "placement_both", "question_triples"]
    headers = [("Raw+E",), ("Adj.", "triples"), ("Adj.", "text"), ("Text", "steps"), ("Text", "direct"), ("Dest.",), ("Both",), ("Direct", "query")]
    for metric in ["recall", "precision"]:
        selected = []
        lines = [chr(92) + "begin{tabular}{lrrrrrrrr}", chr(92) + "toprule", "Model & " + " & ".join(chr(92) + "shortstack{" + (chr(92) * 2).join(h) + "}" for h in headers) + " " + chr(92) * 2, chr(92) + "midrule"]
        for model, name in zip(MODELS, NAMES):
            rs = [one(data["effects"], model=model, contrast=c, metric=metric) for c in contrasts]
            selected.extend(rs)
            lines.append(name + " & " + " & ".join(f"{float(r['delta']):+.3f}" for r in rs) + r" \\")
        lines.extend([r"\bottomrule", r"\end{tabular}"])
        path = OUT / "tables" / (metric + "_effects.tex")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        tables[metric + "_effects"] = {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "rows": selected, "sha256": sha(path)}
    lines = [r"\begin{tabular}{lrrrr}", r"\toprule", r"Model & K1 & K3 & K4 & K7 \\", r"\midrule"]
    for model, name in zip(MODELS, NAMES):
        r = one(data["treein"], model=model)
        lines.append(name + " & " + " & ".join(f"{float(r[c]):.3f}" for c in ["K1", "K3", "K4", "K7"]) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path = OUT / "tables/treein_recall.tex"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tables["treein_recall"] = {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "rows": data["treein"], "sha256": sha(path)}
    for metric in ["recall", "precision", "exact"]:
        lines = [r"\begin{tabular}{lrrr}", r"\toprule", r"Condition & Gemma & Qwen & Ministral \\", r"\midrule"]
        selected = []
        for c in ["K0", "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K5k", "R0", "R1-matched", "R2-matched"]:
            rs = [one(data["conditions"], series_id="core", model=m, condition=c) for m in MODELS]
            selected.extend(rs)
            lines.append(c + " & " + " & ".join(f"{float(r[metric]):.3f}" for r in rs) + r" \\")
        lines += [r"\bottomrule", r"\end{tabular}"]
        path = OUT / "tables" / ("core_" + metric + ".tex")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        tables["core_" + metric] = {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "rows": selected, "sha256": sha(path)}
    payload = {"checked_on": "2026-10-26", "scope": "Publication rendering and direct TeX table export of existing scores only",
               "source_hashes": {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in sources.values()},
               "script_sha256": sha(Path(__file__)), "figures": assets, "tables": tables,
               "new_inference": False, "intervals": "none for primary recall/precision", "outcome_policy": "all planned outcomes; invalid contributes zero"}
    (PROV / "assets_manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"figures": len(assets), "tables": len(tables), "new_inference": False}))


if __name__ == "__main__":
    main()
