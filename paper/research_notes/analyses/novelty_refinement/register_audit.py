"""Register the bounded refinement, preserving previous evidence hashes."""
import copy
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[4]
NOTES = ROOT / "paper/research_notes"
PREFIX = "paper/research_notes/analyses/novelty_refinement/"
OUT = ROOT / PREFIX / "run-02"


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = json.loads((OUT / "summary.json").read_text())
    for path, expected in result["provenance"]["sources"].items():
        assert sha(ROOT / path) == expected, path
    state_path = NOTES / "workflow_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["stages"]["novelty_refinement"] = "bounded_Tree_in_transition_and_rule_distinguishability_audit_complete; broader_scope_and_originality_pending"
    state["latest_novelty_audit"] = {
        "checked_on": "2026-10-25", "source_revision": result["provenance"]["revision"],
        "report": "paper/research_notes/novelty_refinement.md", "result": PREFIX + "run-02/summary.json",
        "scope": result["scope"], "manuscript_changed": False,
        "decision": "Center the contribution candidate on same-task error transitions under fixed unique facts and diagnostic distinguishability. Generic incomplete exploration has prior work. No shared Tool/KG cause established."}
    assert state["analysis_complete"] is False and state["full_writing_ready"] is False
    state["gate_rationale"] += " Follow-up at d8fa5a9 completes the bounded six-node Tree-in transition/rule audit (including adjacent contexts), not broader coverage or Tool harmonization. GraphWalk overlap and non-identifiable alternative rules narrow the novelty candidate further; see novelty_refinement.md."
    write(state_path, state)
    evidence = []

    def local(eid, kind, path, locator, verification="inspected", **extra):
        evidence.append(dict(id=eid, kind=kind, path=path, sha256=sha(ROOT / path), locator=locator,
                             verification=verification, checked_on="2026-10-25", **extra))

    local("E-nr-observations", "result", "results/observations.jsonl.gz", "series_id=core,motif=tree_in,size=6,condition in K1/K2/K3/K4/K7; observation_id,base_id,selected_names,valid,metrics")
    local("E-nr-inputs", "result", "results/inputs.jsonl.gz", "input_id join for E-nr-observations; explicit candidates/facts; private task_spec and candidate mapping")
    local("E-nr-script", "implementation", PREFIX + "analyze_transitions.py", "coverage, graph, main; saved-spec traversal and same-base state transitions")
    local("E-nr-summary", "result", PREFIX + "run-02/summary.json", "$.selector; $.groups; $.transitions; $.alternative_rules; $.validation; $.provenance", "recomputed", upstream_evidence_ids=["E-nr-observations", "E-nr-inputs", "E-nr-script"])
    local("E-nr-rows", "result", PREFIX + "run-02/observations.jsonl", "observation_id/base_id/model/condition; state,cached_exact,alternative-rule match and distinctness flags", "recomputed", upstream_evidence_ids=["E-nr-summary"])
    local("E-nr-report", "draft", "paper/research_notes/novelty_refinement.md", "Current status; literature boundaries; completed analysis; contribution outline; writing decision")
    local("E-nr-tool-source", "literature", "paper/research_notes/sources/tool_graph_complexity.pdf", "Section 5.3/Table 1 p.8; Appendix O pp.30-31; Tables 32-33")
    literature = [
        ("encoding", "https://proceedings.iclr.cc/paper_files/paper/2024/file/bf72f65f30eedf5d48da6980ee02b589-Paper-Conference.pdf", "Sections 3.1 and Appendix A; encoding and neighborhood accessibility", "Graph encoding and neighborhood accessibility are established evaluation axes."),
        ("pathcompare", "https://arxiv.org/html/2402.01805v4", "Sections 2-4; traversal tasks, size/order, PathCompare", "Structured graph traversal and comparison of multiple possible paths are studied in the inspected PathCompare paper."),
        ("graphwalk", "https://arxiv.org/html/2604.01610v1", "Sections 4 and 5.5; incomplete exploration, starting-node and format failures", "GraphWalk already reports incomplete exploration in graph-context settings."),
        ("cespk", "https://arxiv.org/html/2608.24824v1", "Sections 2-3; necessary constraints, three-valued semantics, simulated candidates", "The inspected CES-PK preprint filters simulated candidate answers under partial knowledge, rather than recovering intermediate route witnesses."),
        ("cespk-publisher", "https://link.springer.com/chapter/10.1007/978-3-032-32335-4_21", "Title, author, KI 2026 identity and abstract; subscription full text not inspected", "The CES-PK publisher abstract includes LLM-generated candidate sets; it is not treated as identical to the inspected preprint evaluation."),
        ("radar", "https://arxiv.org/html/2602.21951v1", "Sections 2.1-2.4; link prediction, triple classification and representation-space inference", "RADAR uses discriminative entity selection for link prediction and triple classification, distinct from all-route entity coverage."),
    ]
    claims = []

    def claim(cid, text, ctype, refs, reason, status="supported", **extra):
        claims.append(dict(id=cid, text=text, type=ctype, status=status,
                           scope="novelty_refinement.md only; bounded analysis, not full-manuscript review",
                           evidence_ids=refs, reason=reason, numeric=False, **extra))

    for key, url, locator, proposition in literature:
        eid = "E-nr-" + key
        evidence.append(dict(id=eid, kind="literature", url=url, locator=locator,
                             verification="inspected", checked_on="2026-10-25"))
        claim("C-nr-" + key, proposition, "literature", [eid], "Primary relevant text inspected; publication status and full-text access are qualified in report.")
    claim("C-nr-prior-overlap", "The supplied Tool Graph source already contains KG transfer, Chain inversion and incoming-tree/distractor results.", "literature", ["E-nr-tool-source"], "Direct fresh inspection of PDF pages 8,30,31; no first-transfer claim.")
    families = [
        ("groups", "The scoped archive has the group-level planned, valid, exact and identity-signature counts reported in novelty_refinement.md.", ["planned", "valid", "cached_exact", "one_hop", "identity_diagnostic_valid", "invalid", "identities_missing"]),
        ("transitions", "The scoped paired matrices retain gains, losses and one-hop/exact/other transitions on the same model/base tasks.", None),
        ("alternative_rules", "Alternative-rule distinguishability and exact output compatibility are conditional on rule and evidence condition in the scoped Tree-in inputs.", ["distinct_from_reference", "distinct_and_nontrivial", "matches_distinct_alternative"]),
    ]
    for family, proposition, fields in families:
        numbers = []
        for index, row in enumerate(result[family]):
            for field, value in row.items():
                if (fields is not None and field in fields) or (fields is None and ("_to_" in field or field in {"cached_exact_gained", "cached_exact_lost"})):
                    numbers.append(dict(value=value, metric=field, evidence_id="E-nr-summary",
                                        locator=f"$.{family}[{index}].{field}",
                                        denominator=row.get("planned", row.get("planned_pairs", row.get("valid_identity_denominator"))),
                                        derivation="Integer count from exact selector and saved identities/cached validity; paired by model/base_id. See summary definitions and retained script; no rounding or inferential test."))
        claim("C-nr-" + family, proposition, "empirical", ["E-nr-summary", "E-nr-rows"],
              "Frozen public-graph/reference and cached-score checks passed. Counts are exploratory; Gemma missing identities and invalid outcomes are explicit.")
        claims[-1].update(numeric=True, numbers=numbers)
    claim("C-nr-mechanism", "Duplicated relation hosting repairs an internal depth-enumeration mechanism shared with Tool Selection.", "hypothesis", ["E-nr-summary"], "Not established: final sets are not process traces; repetition/length/salience and cross-domain differences remain confounded.", status="pending")
    audit = OUT / "audit"
    audit.mkdir(exist_ok=False)
    write(audit / "evidence_register.json", {"schema_version": 1, "evidence": evidence})
    (audit / "claims.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in claims), encoding="utf-8")
    write(audit / "workflow_state.json", copy.deepcopy(state))
    existing = json.loads((NOTES / "evidence_register.json").read_text(encoding="utf-8"))
    assert not {e["id"] for e in existing["evidence"]} & {e["id"] for e in evidence}
    existing["evidence"].extend(evidence)
    write(NOTES / "evidence_register.json", existing)
    with (NOTES / "claims.jsonl").open("a", encoding="utf-8") as stream:
        for c in claims:
            stream.write(json.dumps(c, ensure_ascii=False) + "\n")
    validate = runpy.run_path(str(NOTES / "scripts/validate_research_artifacts.py"))["validate"]
    report = {"scoped": validate(ROOT, audit), "production": validate(ROOT, NOTES),
              "note": "Earlier production hashes are preserved; a scoped pass is not semantic/full-manuscript verification."}
    write(audit / "validation.json", report)
    print(json.dumps({"scoped": report["scoped"], "production_status": report["production"]["status"],
                      "production_errors": len(report["production"]["errors"])}))


if __name__ == "__main__":
    main()
