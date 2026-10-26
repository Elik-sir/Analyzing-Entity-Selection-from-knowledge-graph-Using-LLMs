"""Pivot saved Tree-in recall: one model per row, conditions in columns."""
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
CONDITIONS = ["K1", "K3", "K4", "K7"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--figures", type=Path, required=True)
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.figures = args.figures.resolve()
    assert not args.out.exists() and not args.figures.exists()
    source = ROOT / "paper/research_notes/analyses/main_claim_assets/run-05/table2_treein_metrics_all_models.csv"
    with source.open(newline="", encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    lookup = {(r["model"], r["condition"]): r for r in records}
    assert len(lookup) == len(records) == 12
    rows, display, validity = [], [], []
    for model, label in MODELS:
        row = {"model": model}
        values = []
        for condition in CONDITIONS:
            r = lookup[(model, condition)]
            assert int(r["N"]) == 100
            row[condition] = r["recall"]
            values.append(f"{float(r['recall']):.3f}")
            validity.append({k: r[k] for k in ["model", "condition", "N", "valid", "invalid", "raw_response_available", "cached_metrics_only"]})
        rows.append(row)
        display.append([label] + values)
    args.out.mkdir(parents=True)
    args.figures.mkdir(parents=True)
    csv_path = args.out / "table2_treein_recall.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["model"] + CONDITIONS)
        writer.writeheader()
        writer.writerows(rows)
    plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42, "svg.fonttype": "none"})
    fig = plt.figure(figsize=(11.8, 4.5), facecolor="white")
    fig.text(.045, .925, "Recall on six-node Tree-in tasks", fontsize=18, fontweight="bold")
    fig.text(.045, .84, "One row per model; 100 planned tasks per condition", fontsize=11.5, color="#4F5963")
    ax = fig.add_axes([.045, .36, .91, .40])
    ax.axis("off")
    table = ax.table(cellText=display, colLabels=["Model", "K1\nSource cards", "K3\nDestination cards", "K4\nBoth cards", "K7\nDirect query"],
                     colWidths=[.26, .185, .185, .185, .185], loc="center", bbox=[0, 0, 1, 1], cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(11.5)
    for (ri, ci), cell in table.get_celld().items():
        cell.set_edgecolor("#DDE2E7")
        cell.set_linewidth(.6)
        cell.PAD = .10
        cell.set_facecolor("#E8EDF2" if ri == 0 else "white")
        if ri == 0:
            cell.set_text_props(fontweight="bold")
            cell.set_height(.13)
        if ci == 0:
            cell.set_text_props(ha="left")
    fig.text(.045, .265, "K1/K3/K4 use the procedural query; K7 uses source cards with a direct query.", fontsize=10, color="#4F5963")
    fig.text(.045, .19, "Saved macro means over all planned tasks; invalid outcomes contribute zero.", fontsize=10, color="#4F5963")
    fig.text(.045, .115, "Ministral valid counts: K3 = 99/100, K7 = 91/100; all other cells = 100/100.", fontsize=10, color="#4F5963")
    files = []
    for suffix in ["png", "pdf", "svg"]:
        p = args.figures / ("table2_treein_recall." + suffix)
        fig.savefig(p, dpi=300, facecolor="white")
        files.append(p)
    plt.close(fig)
    manifest = {"checked_on": "2026-10-26", "scope": "Compact recall-only table from twelve already checked Tree-in metric cells; no new analysis or manuscript edit",
                "source": {"path": str(source.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(source)},
                "script_sha256": sha(Path(__file__)), "csv_sha256": sha(csv_path), "display_rounding": "three decimal places; unrounded source values retained in CSV",
                "validity": validity, "figures": {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in files},
                "validation": {"rows": 3, "condition_columns": 4, "planned_per_cell": 100, "source_value_preservation": "passed", "visual_review": "pending"}}
    (args.out / "table_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["validation"]))


if __name__ == "__main__":
    main()
