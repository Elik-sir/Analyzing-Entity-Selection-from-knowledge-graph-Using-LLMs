"""Register and verify this bounded assessment without refreshing older hashes."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[4]
NOTES = ROOT / "paper/research_notes"
OUT = Path(__file__).parent / "run-04"
AUDIT = OUT / "assessment_audit"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    for path, expected in summary["provenance"]["sources"].items():
        assert sha(ROOT / path) == expected, path
    with (NOTES / "analyses/final_results/run-01/motif_size_metrics.csv").open(newline="", encoding="utf-8") as stream:
        old = list(csv.DictReader(stream))
    lookup = {tuple(r[k] for k in ("series_id", "model", "condition", "noise", "motif", "size")): r for r in old}
    max_difference = 0.0
    for g in summary["groups"]:
        key = tuple(str(g[k]) for k in ("series_id", "model", "condition", "noise", "motif", "size"))
        r = lookup[key]
        assert int(r["N"]) == g["N"] and int(r["valid"]) == g.get("valid", 0)
        max_difference = max(max_difference, abs(float(r["f1"]) - g["f1"]))
        assert abs(float(r["exact"]) - g.get("exact", 0) / g["N"]) < 1e-12
    assert max_difference < 1e-12
    for g in summary["supplementary_core_cached_groups"]:
        noise = "adjacent" if g["condition"] in {"K2", "K6"} else "disconnected"
        key = ("core", g["model"], g["condition"], noise, g["motif"], "6")
        r = lookup[key]
        assert abs(float(r["f1"]) - g["f1"]) < 1e-12
        assert abs(float(r["exact"]) - g.get("exact", 0) / g["N"]) < 1e-12
    with (OUT / "route_diagnostics.csv").open(newline="", encoding="utf-8") as stream:
        routes = list(csv.DictReader(stream))
    assert len(routes) == summary["route_diagnostic_observations"]
    assert len({r["observation_id"] for r in routes}) == len(routes)
    assert all(0 <= int(r["complete_paths"]) <= int(r["paths"]) for r in routes)

    def local(eid, kind, path, locator, verification="inspected", **extra):
        return dict(id=eid, kind=kind, path=path, sha256=sha(ROOT / path), locator=locator,
                    verification=verification, checked_on="2026-10-25", **extra)

    prefix = "paper/research_notes/analyses/transfer_positioning/"
    evidence = [
        local("E-transfer-source", "literature", "paper/research_notes/sources/tool_graph_complexity.pdf", "PDF pp. 1-10; Section 5.3/Table 1 p. 8; Discussion p. 9; Appendix O pp. 30-31, Tables 32-33", limitations="Supplied anonymous manuscript; publication metadata and external records not authenticated."),
        local("E-transfer-observations", "result", "results/observations.jsonl.gz", "size=6; five common families; core K1/K2 plus tree_in K3/K4/K7; full_braw Braw/Braw+E; supplementary Core K1-K8", limitations="Saved metrics/selected_names; not a new response reparse or model evaluation."),
        local("E-transfer-inputs", "result", "results/inputs.jsonl.gz", "input_id join for E-transfer-observations; messages user candidates; reference task_spec/name_map; 3600 unique selected inputs", limitations="Missing task specs counted and excluded from route diagnostics."),
        local("E-transfer-script", "implementation", prefix + "diagnose_transfer.py", "included; graph_reference; main: cached groups, pair transitions, route-role diagnostics"),
        local("E-transfer-diagnostics", "result", prefix + "run-04/summary.json", "$.selector; $.groups; $.paired_transitions; $.controlled_paired_transitions; $.supplementary_core_cached_groups; $.provenance; $.limitations; $.validation", "recomputed", upstream_evidence_ids=["E-transfer-observations", "E-transfer-inputs", "E-transfer-script"]),
        local("E-transfer-route-rows", "result", prefix + "run-04/route_diagnostics.csv", "Unique observation_id/input_id rows; model/condition/motif; paths, role counts and exact_one_hop_set", "recomputed", upstream_evidence_ids=["E-transfer-diagnostics"]),
        local("E-transfer-positioning", "draft", "paper/research_notes/transfer_positioning.md", "Scientific decision; new diagnostics; hypothesis matrix; additional work; RQs and contributions"),
        local("E-transfer-outline", "draft", "paper/research_notes/transfer_outline.md", "Sections 1-7 and main-asset plan; conditional contribution and incomplete cross-domain analysis"),
        local("E-transfer-task-rules", "implementation", "graph_motives/preparation/questions.py", "_templates (lines 64-81); evaluate_task (line 164 onward); union of allowed route witnesses", limitations="Current implementation plus frozen input checks; code alone does not establish historical execution."),
        dict(id="E-transfer-encoding-primary", kind="literature", url="https://proceedings.iclr.cc/paper_files/paper/2024/file/bf72f65f30eedf5d48da6980ee02b589-Paper-Conference.pdf", locator="Talk like a Graph, ICLR 2024, Sections 1-2; Appendix A graph encodings", verification="inspected", checked_on="2026-10-25"),
        dict(id="E-transfer-composition-primary", kind="literature", url="https://arxiv.org/html/2305.18654v3", locator="Faith and Fate, v3, Sections 2 and 3.2.3; computation graph and local/propagation error definitions", verification="inspected", checked_on="2026-10-25"),
    ]
    def claim(cid, text, ctype, eids, reason, status="supported", **extra):
        return dict(id=cid, text=text, type=ctype, status=status, scope="transfer_positioning.md; proposed diagnostic-transfer outline only", evidence_ids=eids, reason=reason, numeric=False, **extra)

    def numeric_claim(cid, text, field, values):
        c = claim(cid, text, "empirical", ["E-transfer-diagnostics"], "Recomputed saved selections/cached metrics at six nodes; exploratory and descriptive; no causal process or significance assertion.")
        c["numeric"] = True
        c["numbers"] = [dict(value=value, metric=field, evidence_id="E-transfer-diagnostics",
                             locator="$.groups[series_id=core,model=qwen3.6-flash,condition=" + condition + ",noise=disconnected,motif=tree_in,size=6]." + field,
                             denominator=100, derivation="Count valid saved selected_names satisfying the declared predicate; all 100 planned tasks valid in this cell. No rounding.") for condition, value in values]
        return c

    claims = [
        claim("C-transfer-prior-overlap", "The supplied Tool Graph manuscript already evaluates KG transfer, Chain inversion, residual Tree-in difficulty and an implicit-dependency interpretation.", "literature", ["E-transfer-source"], "Directly inspected Section 5.3, Discussion and Appendix O; these are prior results/interpretations, not new contributions here."),
        claim("C-transfer-adjusted-tree", "The supplied tool-side analysis reports a Tree-in coefficient whose controlled interval includes zero, distinct from its large raw difficulty.", "literature", ["E-transfer-source"], "Table 1 and Section 5.3, p. 8; does not assert equivalence or transfer that adjusted finding to KG."),
        numeric_claim("C-transfer-qwen-onehop", "Qwen Core K1 six-node Tree-in selects exactly the anchor and first-hop neighbours on 71 of 100 planned tasks.", "exact_one_hop_set", [("K1", 71)]),
        numeric_claim("C-transfer-qwen-placement-signature", "Qwen Tree-in exact one-hop output counts are 71/100 in K1, 76/100 in K3 and 31/100 in K4 on the audited common-size cohort.", "exact_one_hop_set", [("K1", 71), ("K3", 76), ("K4", 31)]),
        numeric_claim("C-transfer-qwen-placement-exact", "Qwen Tree-in exact-reference counts are 15/100 in K1, 16/100 in K3 and 51/100 in K4 on the audited common-size cohort.", "exact", [("K1", 15), ("K3", 16), ("K4", 51)]),
        claim("H-transfer-depth-truncation", "A subset of residual explicit-KG errors may reflect incomplete depth/route enumeration; final sets cannot identify the model's internal stopping process.", "hypothesis", ["E-transfer-diagnostics"], "Compatible one-hop output signature; type, relation, instruction, salience and distributed-fact alternatives remain.", status="pending"),
        claim("H-transfer-dependency-inference", "Dependency inference may contribute to the different sequential-selection profiles of Tool and KG tasks.", "hypothesis", ["E-transfer-source", "E-transfer-diagnostics"], "Prior explanation and KG availability evidence; no same-item real-tool overlay test or equal-information Raw condition established.", status="pending"),
        claim("H-transfer-distributed-facts", "Fact distribution or repetition may contribute to residual KG route-coverage errors.", "hypothesis", ["E-transfer-diagnostics"], "K1/K3/K4 patterns are compatible with multiple causes; token/repetition/order controls needed for identification.", status="pending"),
    ]
    # Check every numerical ledger value directly against the retained output.
    for c in claims:
        for number in c.get("numbers", []):
            loc = number["locator"]
            condition = loc.split("condition=", 1)[1].split(",", 1)[0]
            group = next(g for g in summary["groups"] if g["series_id"] == "core" and g["model"] == "qwen3.6-flash" and g["motif"] == "tree_in" and g["condition"] == condition)
            assert group[number["metric"]] == number["value"]

    ledger_path = NOTES / "evidence_register.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    new_eids = {e["id"] for e in evidence}
    ledger["evidence"] = [e for e in ledger["evidence"] if e["id"] not in new_eids] + evidence
    write_json(ledger_path, ledger)
    claim_path = NOTES / "claims.jsonl"
    existing = [json.loads(x) for x in claim_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    new_cids = {c["id"] for c in claims}
    existing = [c for c in existing if c["id"] not in new_cids] + claims
    claim_path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in existing), encoding="utf-8")
    AUDIT.mkdir(exist_ok=True)
    write_json(AUDIT / "evidence_register.json", dict(schema_version=1, evidence=evidence))
    (AUDIT / "claims.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in claims), encoding="utf-8")
    write_json(AUDIT / "workflow_state.json", copy.deepcopy(json.loads((NOTES / "workflow_state.json").read_text(encoding="utf-8"))))
    validate = runpy.run_path(str(NOTES / "scripts/validate_research_artifacts.py"))["validate"]
    scoped = validate(ROOT, AUDIT)
    production = validate(ROOT, NOTES)
    report = dict(checked_on="2026-10-25", scope="This assessment only; no independent scientific review", scoped_structural=scoped,
                  production_structural=production,
                  numerical_cross_checks=dict(status="passed", main_groups=len(summary["groups"]), supplementary_groups=len(summary["supplementary_core_cached_groups"]), max_f1_difference_from_prior_csv=max_difference, unique_route_rows=len(routes), ledger_numbers_checked=True),
                  retained_run="run-04; earlier run-01/02/03 superseded; missing task_spec handled by exclusion",
                  registration_script_sha256=sha(Path(__file__)))
    write_json(AUDIT / "validation.json", report)
    assert scoped["status"] == "passed", scoped
    print(json.dumps(dict(scoped=scoped, numerical=report["numerical_cross_checks"], production_error_count=len(production["errors"]))))


if __name__ == "__main__":
    main()
