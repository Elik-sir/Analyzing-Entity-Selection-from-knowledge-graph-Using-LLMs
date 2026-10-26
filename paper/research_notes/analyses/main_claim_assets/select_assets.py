"""Select already-computed rows for the agreed manuscript asset plan.

No archive rescoring, experiment, bootstrap or new hypothesis test. Missing
counter cells represent zero in previously validated transition matrices.
"""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
MODELS = ["gemma-4-31b", "qwen3.6-flash", "ministral-14b"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    assert rows
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    paths = {
        "contrasts": ROOT / "paper/research_notes/analyses/final_results/run-01/paired_contrasts.csv",
        "errors": ROOT / "paper/research_notes/analyses/transfer_positioning/run-04/summary.json",
        "transitions": ROOT / "paper/research_notes/analyses/novelty_refinement/run-02/summary.json",
    }
    contrasts = read_csv(paths["contrasts"])
    selected = []
    panel_contrasts = {
        "A_relations_added": ["raw_explicit"],
        "B_fixed_fact_presentation": ["format_slots", "format_goal", "placement_object", "placement_both", "question_triples"],
        "C_adjacent_context": ["noise_triples", "noise_text"],
    }
    for panel, names in panel_contrasts.items():
        for name in names:
            for model in MODELS:
                matches = [r for r in contrasts if r["contrast"] == name and r["model"] == model and r["metric"] == "f1" and r["panel"] in {"raw", "core"}]
                assert len(matches) == 1, (name, model)
                r = matches[0]
                assert int(r["N_pairs"]) == (3400 if name == "raw_explicit" else 700)
                selected.append({"figure_panel": panel, **r})
    write_csv(args.out / "figure1_condition_effects.csv", selected)
    errors_source = json.loads(paths["errors"].read_text(encoding="utf-8"))
    categories = ["exact", "omission_only", "inclusion_only", "mixed", "invalid"]
    motifs = ["chain", "star_in", "star_out", "tree_in", "tree_out"]
    errors = []
    for model in MODELS:
        for motif in motifs:
            for condition in ["K1", "K2"]:
                matches = [r for r in errors_source["groups"] if r["series_id"] == "core" and r["model"] == model and r["motif"] == motif and r["condition"] == condition and r["size"] == 6]
                assert len(matches) == 1
                r = matches[0]
                assert r["N"] == 100 and sum(r.get(c, 0) for c in categories) == 100
                errors.append({"model": model, "motif": motif, "condition": condition,
                               "size": 6, "planned": r["N"], "valid": r.get("valid", 0),
                               **{c: r.get(c, 0) for c in categories}})
    write_csv(args.out / "figure2_error_composition.csv", errors)
    source = json.loads(paths["transitions"].read_text(encoding="utf-8"))
    groups = {(r["model"], r["condition"]): r for r in source["groups"]}
    transition_rows = []
    for model in ["qwen3.6-flash", "ministral-14b"]:
        for condition in ["K3", "K4", "K7"]:
            matches = [r for r in source["transitions"] if r["model"] == model and r["before"] == "K1" and r["after"] == condition]
            assert len(matches) == 1
            r = matches[0]
            a, b = groups[(model, "K1")], groups[(model, condition)]
            assert r["planned_pairs"] == 100
            assert r["cached_exact_gained"] - r["cached_exact_lost"] == b["cached_exact"] - a["cached_exact"]
            assert sum(v for k, v in r.items() if k.startswith("one_hop_to_")) == a["one_hop"]
            transition_rows.append({"model": model, "before": "K1", "after": condition,
                                    "N_pairs": 100, "exact_before": a["cached_exact"], "exact_after": b["cached_exact"],
                                    "one_hop_before": a["one_hop"], "one_hop_after": b["one_hop"],
                                    "one_hop_to_exact": r.get("one_hop_to_exact", 0), "one_hop_denominator": a["one_hop"],
                                    "exact_lost": r["cached_exact_lost"], "initial_exact_denominator": a["cached_exact"],
                                    "invalid_after": b.get("invalid", 0)})
    write_csv(args.out / "table2_signature_transitions.csv", transition_rows)
    manifest = {
        "checked_on": "2026-10-25", "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "scope": "Selection/formatting of previously computed results only; figures and manuscript tables not yet rendered",
        "command": "python paper/research_notes/analyses/main_claim_assets/select_assets.py --out " + args.out.as_posix(),
        "sources": {k: {"path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(p)} for k, p in paths.items()},
        "assets": [
            {"id": "T1", "type": "qualitative_table", "status": "specified_in_main_findings_and_assets.md", "claim_ids": ["C-transfer-prior-overlap", "C-nr-prior-overlap"]},
            {"id": "F1", "path": "figure1_condition_effects.csv", "rows": len(selected), "claim_ids": ["C-final-raw-f1", "C-final-representation-f1", "C-final-placement-f1", "C-final-noise-f1"]},
            {"id": "F2", "path": "figure2_error_composition.csv", "rows": len(errors), "claim_ids": ["C-assessment-error-profiles"]},
            {"id": "T2", "path": "table2_signature_transitions.csv", "rows": len(transition_rows), "claim_ids": ["C-nr-groups", "C-nr-transitions"]},
        ],
        "limitations": ["No statistical interaction claim; F1 delta contrasts belong to different panels/populations.",
                        "F1 contrast bands are the original exploratory simultaneous bands, not recomputed here.",
                        "Error compositions and signature transitions are descriptive, with no added intervals.",
                        "Gemma cached fp/fn support coarse categories, not identity-level one-hop signatures.",
                        "Core/Full and repeated conditions overlap; counts must not be summed as independent observations."],
        "validation": {"selected_contrasts": len(selected), "error_cells": len(errors), "transition_rows": len(transition_rows),
                       "unique_selector_and_denominator_checks": "passed", "category_and_transition_conservation": "passed"},
    }
    # Resolve all referenced IDs rather than creating unsupported placeholders.
    ids = {json.loads(line)["id"] for line in (ROOT / "paper/research_notes/claims.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    assert all(cid in ids for a in manifest["assets"] for cid in a["claim_ids"])
    manifest["outputs_sha256"] = {p.name: sha(p) for p in args.out.glob("*.csv")}
    manifest["script_sha256"] = sha(Path(__file__))
    (args.out / "asset_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["validation"]))


if __name__ == "__main__":
    main()
