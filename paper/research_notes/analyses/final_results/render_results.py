"""Render publication figure assets and numeric LaTeX table fragments."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

MODELS = ("gemma-4-31b", "qwen3.6-flash", "ministral-14b")
LABELS = {"gemma-4-31b": "Gemma-4-31B", "qwen3.6-flash": "Qwen3.6-Flash", "ministral-14b": "Ministral-14B"}
COLORS = ("#0072B2", "#D55E00")
MOTIFS = ("chain", "star_in", "star_out", "tree_in", "tree_out", "rhombus", "hourglass")
MOTIF_NAMES = ("Chain", "Star-in", "Star-out", "Tree-in", "Tree-out", "Rhombus", "Hourglass")
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "none", "savefig.dpi": 300, "font.family": "DejaVu Sans"})


def read(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f(row, key):
    return float(row[key])


def save(fig, name, directory, sources, records, data_source, caption):
    for extension in ("png", "svg"):
        fig.savefig(directory / (name + "." + extension), facecolor="white")
    plt.close(fig)
    sources.append({"figure": name, "data_source": data_source, "rows": records, "caption": caption,
                    "files": {name + "." + ext: sha(directory / (name + "." + ext)) for ext in ("png", "svg")}})


def raw_figure(means, directory, sources):
    records = [r for r in means if r["panel"] == "raw"]
    lookup = {(r["model"], r["condition"], r["metric"]): r for r in records}
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.8))
    x = np.arange(3)
    for axis, metric, title in zip(axes, ("f1", "exact"), ("Mean set-F1", "Exact-set match")):
        for offset, condition in enumerate(("Braw", "Braw+E")):
            rows = [lookup[(model, condition, metric)] for model in MODELS]
            values = np.array([f(r, "mean") for r in rows])
            low = np.array([f(r, "cluster_ci_low") for r in rows])
            high = np.array([f(r, "cluster_ci_high") for r in rows])
            positions = x + (offset - 0.5) * 0.34
            axis.bar(positions, values, width=0.32, color=COLORS[offset], label="Raw" if offset == 0 else "Raw+E")
            axis.errorbar(positions, values, yerr=np.vstack((values - low, high - values)), fmt="none", color="black", capsize=3, linewidth=0.9)
            for pos, value, hi in zip(positions, values, high):
                axis.text(pos, max(value, hi) + 0.025, f"{value:.3f}", ha="center", va="bottom", fontsize=8)
        axis.set_xticks(x, ["Gemma", "Qwen", "Ministral"])
        axis.set_ylim(0, 1.08)
        axis.set_title(title, fontsize=11)
        axis.set_ylabel("Score (all planned tasks)")
        axis.set_xlabel("Model")
        axis.grid(axis="y", alpha=0.15)
        axis.set_axisbelow(True)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="center", bbox_to_anchor=(0.5, 0.86), ncol=2)
    fig.suptitle("Adding explicit relations to original entity descriptions", fontsize=13)
    caption = "N = 3,400 paired tasks per model/condition; invalid outcomes contribute zero. Bars: task means; whiskers: pointwise 95% anchor-cluster bootstrap intervals. Source: historical archive; mean_intervals.csv."
    fig.text(0.5, 0.03, "N = 3,400 per condition/model; invalid = zero. 95% pointwise anchor-cluster intervals.\nSource: saved historical observations; mean_intervals.csv.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.12, 1, 0.8))
    save(fig, "raw_explicit_relations", directory, sources, records, "mean_intervals.csv", caption)


def contrast_figure(contrasts, directory, sources):
    ids = ("format_slots", "format_goal", "noise_triples", "noise_text", "placement_object", "placement_both")
    names = ("Text minus triples\n(step-by-step)", "Text minus triples\n(direct question)", "Adjacent minus disconnected\n(triples)", "Adjacent minus disconnected\n(text)", "Destination minus source\n(cards)", "Both minus source\n(cards)")
    records = [r for r in contrasts if r["panel"] == "core" and r["metric"] == "f1" and r["contrast"] in ids]
    lookup = {(r["model"], r["contrast"]): r for r in records}
    fig, axes = plt.subplots(1, 3, figsize=(10, 5.8), sharey=True)
    y = np.arange(len(ids))
    for axis, model in zip(axes, MODELS):
        rows = [lookup[(model, cid)] for cid in ids]
        delta = np.array([f(r, "delta") * 100 for r in rows])
        lo = np.array([f(r, "simultaneous_low") * 100 for r in rows])
        hi = np.array([f(r, "simultaneous_high") * 100 for r in rows])
        pl = np.array([f(r, "cluster_ci_low") * 100 for r in rows])
        ph = np.array([f(r, "cluster_ci_high") * 100 for r in rows])
        axis.hlines(y, lo, hi, color="#b4bcc2", linewidth=5)
        axis.hlines(y, pl, ph, color=COLORS[0], linewidth=1.5)
        axis.plot(delta, y, "o", color=COLORS[0], markersize=4)
        axis.axvline(0, color="#555555", linewidth=0.8, linestyle="--")
        axis.set_title(LABELS[model], fontsize=11)
        axis.set_xlabel("Change in mean set-F1\n(percentage points)", fontsize=9)
        axis.grid(axis="x", alpha=0.12)
        axis.set_yticks(y, names, fontsize=9)
    axes[0].invert_yaxis()
    low = min(f(r, "simultaneous_low") * 100 for r in records)
    high = max(f(r, "simultaneous_high") * 100 for r in records)
    for axis in axes:
        axis.set_xlim(low - 2, high + 2)
    fig.suptitle("Controlled evidence, distractor and placement contrasts", fontsize=13)
    legend = [Line2D([0], [0], color="#b4bcc2", lw=5, label="Simultaneous main-family band"),
              Line2D([0], [0], color=COLORS[0], lw=1.5, marker="o", label="Pointwise 95% interval / estimate")]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.63, 0.08), frameon=False, fontsize=8, ncol=1)
    caption = "Right minus left; 700 paired tasks per model/contrast. Thin lines: pointwise 95% anchor-cluster intervals. Thick lines: exploratory simultaneous bands calibrated across all 78 main F1/exact contrasts, not only those shown. Source: paired_contrasts.csv."
    fig.text(0.5, 0.025, "N = 700 pairs per model/contrast; all planned outcomes. Main family includes 78 F1/exact effects.\nSource: historical archive; paired_contrasts.csv. Intervals condition on the fixed KG.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.2, 1, 0.93), w_pad=1)
    save(fig, "controlled_contrasts", directory, sources, records, "paired_contrasts.csv", caption)


def motif_figure(detail, directory, sources):
    records = [r for r in detail if r["series_id"] == "core" and r["condition"] in {"K1", "K2"}]
    lookup = {(r["model"], r["condition"], r["motif"]): r for r in records}
    matrix = np.array([[f(lookup[(model, condition, motif)], "f1") for model in MODELS for condition in ("K1", "K2")] for motif in MOTIFS])
    fig, axis = plt.subplots(figsize=(8.3, 5.5))
    plotted = axis.imshow(matrix, cmap="cividis", vmin=0, vmax=1, aspect="auto")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            axis.text(j, i, f"{matrix[i, j]:.3f}", ha="center", va="center", color="black" if matrix[i, j] > 0.6 else "white", fontsize=9)
    axis.set_yticks(range(7), MOTIF_NAMES)
    axis.set_xticks(range(6), [name + "\n" + c for name in ("Gemma", "Qwen", "Ministral") for c in ("K1", "K2")])
    axis.set_xlabel("Model / distractor condition")
    axis.set_ylabel("Motif and query family")
    axis.set_title("Selection by motif: disconnected versus adjacent distractors", fontsize=12, pad=12)
    color = fig.colorbar(plotted, ax=axis, fraction=0.045, pad=0.04)
    color.set_label("Mean set-F1 (all planned tasks)")
    caption = "K1: disconnected; K2: adjacent. Each cell has 100 planned tasks. Motifs differ in query semantics as well as topology; these are descriptive strata, not isolated causal topology effects. Source: motif_size_metrics.csv."
    fig.text(0.5, 0.025, "K1 = disconnected; K2 = adjacent; N = 100 per cell. Motifs also change query semantics.\nDescriptive task means; invalid = zero. Source: historical archive; motif_size_metrics.csv.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    save(fig, "motif_noise_f1", directory, sources, records, "motif_size_metrics.csv", caption)


def size_figure(detail, directory, sources):
    motifs = ("chain", "star_in", "star_out", "tree_in", "tree_out")
    records = [r for r in detail if r["model"] == MODELS[0] and r["series_id"] in {"core", "size"} and r["condition"] in {"K1", "K5"} and r["motif"] in motifs]
    fig, axes = plt.subplots(2, 3, figsize=(9, 5.8), sharey=True)
    for axis, motif in zip(axes.flat, motifs):
        for condition, color, marker in zip(("K1", "K5"), COLORS, ("o", "s")):
            rows = sorted([r for r in records if r["motif"] == motif and r["condition"] == condition], key=lambda r: int(r["size"]))
            sizes = [int(r["size"]) for r in rows]
            assert len(set(sizes)) == len(sizes)
            axis.plot(sizes, [f(r, "f1") for r in rows], marker=marker, color=color, markersize=4, linewidth=1.2, label="K1: triples" if condition == "K1" else "K5: text")
        axis.set_title(motif.replace("_", "-").title(), fontsize=10)
        axis.set_xticks(sizes)
        axis.set_ylim(0, 1.03)
        axis.set_xlabel("Motif entities")
        axis.set_ylabel("Mean set-F1")
        axis.grid(alpha=0.15)
    axes.flat[-1].axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    axes.flat[-1].legend(handles, labels, loc="center", frameon=False)
    fig.suptitle("Gemma size diagnostics: controlled triples and templated text", fontsize=12)
    caption = "Core and additional-size panels, Gemma only; 100 planned tasks per displayed motif/size/condition and 25 candidates. Descriptive means without inferential error bars; changing motif size changes target prevalence too. Source: motif_size_metrics.csv."
    fig.text(0.5, 0.025, "N = 100 per size/condition; 25 candidates; all planned outcomes. Descriptive means, no inferential bars.\nSource: historical Core + Size observations; motif_size_metrics.csv.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.12, 1, 0.94))
    save(fig, "gemma_size_diagnostics", directory, sources, records, "motif_size_metrics.csv", caption)


def tex_escape(value):
    return value.replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def tables(means, contrasts, baselines, destination):
    destination.mkdir(exist_ok=True)
    lookup = {(r["panel"], r["model"], r["condition"], r["metric"]): r for r in means}
    lines = [r"% Numeric fragment only; requires booktabs. Not compiled in this analysis.", r"\begin{tabular}{lrrr}", r"\toprule", r"Condition & Gemma & Qwen & Ministral \\", r"\midrule"]
    for condition in ("K0", "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K5k", "R0", "R1-matched", "R2-matched"):
        cells = []
        for model in MODELS:
            row = lookup[("core", model, condition, "f1")]
            cells.append(f"{f(row, 'mean'):.3f} [{f(row, 'cluster_ci_low'):.3f}, {f(row, 'cluster_ci_high'):.3f}]")
        lines.append(tex_escape(condition) + " & " + " & ".join(cells) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", "% Mean task F1 and pointwise 95% anchor-cluster CI; 700 planned tasks per condition/model."])
    (destination / "core_f1.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    lines = [r"% Numeric fragment only; requires booktabs.", r"\begin{tabular}{lrrrr}", r"\toprule", r"Model & Raw F1 & Raw+E F1 & $\Delta$F1 & Both valid $N$ \\", r"\midrule"]
    for model in MODELS:
        row = next(r for r in contrasts if r["panel"] == "raw" and r["model"] == model and r["metric"] == "f1")
        interval = f"{f(row, 'delta'):.3f} [{f(row, 'simultaneous_low'):.3f}, {f(row, 'simultaneous_high'):.3f}]"
        lines.append(f"{LABELS[model]} & {f(row, 'left_mean'):.3f} & {f(row, 'right_mean'):.3f} & {interval} & {row['both_valid_N']}" + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", "% Delta uses all 3,400 pairs, not only both-valid pairs. Brackets: simultaneous main-family band."])
    (destination / "raw_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    lines = [r"% Analytical expectations, not executed model outcomes; requires booktabs.", r"\begin{tabular}{llrrrr}", r"\toprule", r"Panel & Selection rule & Precision & Recall & F1 & Exact \\", r"\midrule"]
    for row in baselines:
        values = [f"{f(row, key):.2e}" if 0 < f(row, key) < 0.0001 else f"{f(row, key):.4f}"
                  for key in ("precision", "recall", "f1", "exact")]
        lines.append(tex_escape(row["series_id"]) + " & " + tex_escape(row["baseline"]) + " & " + " & ".join(values) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", "% Uniform random selects six of 25 candidates without replacement; values are exact analytical expectations."])
    (destination / "analytical_baselines.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(analysis, figures):
    if figures.exists():
        raise ValueError("Choose a fresh figure directory")
    figures.mkdir(parents=True)
    means, contrasts, detail = [read(analysis / name) for name in ("mean_intervals.csv", "paired_contrasts.csv", "motif_size_metrics.csv")]
    sources = []
    raw_figure(means, figures, sources)
    contrast_figure(contrasts, figures, sources)
    motif_figure(detail, figures, sources)
    size_figure(detail, figures, sources)
    tables(means, contrasts, read(analysis / "analytical_baselines.csv"), analysis / "tables")
    (analysis / "figure_sources.json").write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (analysis / "figure_provenance.json").write_text(json.dumps({"matplotlib": matplotlib.__version__, "formats": ["PNG 300 dpi", "SVG vector"], "render_script_sha256": sha(Path(__file__)), "figures": str(figures), "source_csv_sha256": {name: sha(analysis / name) for name in {r["data_source"] for r in sources}}}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"figures": len(sources), "files": len(sources) * 2, "table_fragments": 3}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--figures", type=Path, required=True)
    args = parser.parse_args()
    main(args.analysis.resolve(), args.figures.resolve())
