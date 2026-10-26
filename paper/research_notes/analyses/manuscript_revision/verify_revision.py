"""Bind the recall revision to existing results; no experimental calls or tests.

Checks selected table bytes, source-row equality, citations, figure paths and
reported primary examples. Semantic review remains separate from this script.
"""
import copy
import csv
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil

ROOT = Path(__file__).resolve().parents[4]
NOTES = ROOT / "paper/research_notes"
PAPER = ROOT / "paper/manuscript"
OUT = Path(__file__).parent / "run-01"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    strata = read_csv(NOTES / "analyses/final_results/run-01/motif_size_metrics.csv")
    conditions = read_csv(NOTES / "analyses/final_results/run-01/condition_metrics.csv")
    assets = json.loads((OUT / "assets_manifest.json").read_text(encoding="utf-8"))
    for path, expected in assets["source_hashes"].items():
        assert sha(ROOT / path) == expected, path
    lookup = {tuple(r[k] for k in ["series_id", "model", "condition", "noise", "motif", "size"]): r for r in strata}
    assert len(lookup) == len(strata)
    for figure in assets["figures"]:
        for r in figure["source_rows"]:
            if figure["id"] == "residual_errors":
                assert sum(int(r[k]) for k in ["exact", "omission_only", "inclusion_only", "mixed", "invalid"]) == 100
                continue
            original = lookup[tuple(r[k] for k in ["series_id", "model", "condition", "noise", "motif", "size"])]
            assert r[figure["metric"]] == original[figure["metric"]]
        for path, expected in figure["files"].items():
            assert sha(ROOT / path) == expected
    for table in assets["tables"].values():
        assert sha(ROOT / table["path"]) == table["sha256"]
    for table in ["recall_effects", "precision_effects"]:
        tex = (ROOT / assets["tables"][table]["path"]).read_text(encoding="utf-8")
        for r in assets["tables"][table]["rows"]:
            assert f"{float(r['delta']):+.3f}" in tex
    for r in assets["tables"]["treein_recall"]["rows"]:
        for c in ["K1", "K3", "K4", "K7"]:
            assert f"{float(r[c]):.3f}" in (PAPER / "tables/treein_recall.tex").read_text(encoding="utf-8")
    main_tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    paths = [PAPER / (p + ".tex") for p in re.findall(r"\\input\{(sections/[^}]+)\}", main_tex)]
    assert len(paths) == 8 and all(p.is_file() for p in paths)
    texts = {p: p.read_text(encoding="utf-8") for p in paths}
    full = main_tex + "\n" + "\n".join(texts.values())
    bib = (PAPER / "references.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cited = {key.strip() for group in re.findall(r"\\cite\w*\{([^}]+)\}", full) for key in group.split(",")}
    assert cited <= keys, cited - keys
    labels = re.findall(r"\\label\{([^}]+)\}", full)
    assert len(labels) == len(set(labels))
    refs = set(re.findall(r"\\ref\{([^}]+)\}", full))
    assert refs <= set(labels), refs - set(labels)
    for p in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", full):
        assert (PAPER / p).is_file(), p

    evidence = []

    def local(eid, kind, path, locator, verification="inspected", **extra):
        evidence.append(dict(id=eid, kind=kind, path=path, sha256=sha(ROOT / path), locator=locator,
                             verification=verification, checked_on="2026-10-26", **extra))

    local("E-recall-revision-strata", "result", "paper/research_notes/analyses/final_results/run-01/motif_size_metrics.csv", "core/full_braw selectors by model/condition/motif/size; recall,precision,exact,N,valid", limitations="Saved aggregates; no fresh independent raw-response reparse.")
    local("E-recall-revision-conditions", "result", "paper/research_notes/analyses/final_results/run-01/condition_metrics.csv", "core/full_braw condition groups; macro recall,precision,exact and planned N", limitations="Descriptive all-planned means; no recall/precision uncertainty bands.")
    local("E-recall-revision-assets", "result", "paper/research_notes/analyses/manuscript_revision/run-01/assets_manifest.json", "figures[].source_rows; tables.*.rows; source/output hashes", "recomputed", limitations="Selection and publication formatting of existing results only, not new inference.")
    local("E-recall-revision-questions", "implementation", "graph_motives/preparation/questions.py", "_templates lines 64-81; evaluate_task lines 164-225", limitations="Current symbol defines behavior; historical agreement comes from frozen-reference audit, not code alone.")
    local("E-recall-revision-reference-audit", "result", "paper/research_notes/analyses/reference_pairing_audit/final/summary.json", "coverage; pairing/invariant results; source hashes; final issue count", "reported", limitations="Existing completed audit inspected; not rerun in this revision.")
    local("E-recall-revision-settings", "result", "paper/research_notes/analyses/manuscript_assets/run-01/request_settings_summary.json", "groups for Core/Full Qwen/Ministral; recorded_api_journal settings", limitations="Whitelisted saved metadata; not authentication of unavailable Gemma calls.")
    local("E-recall-revision-bib", "draft", "paper/manuscript/references.bib", "Used entries and added GraphWalk metadata; bibliography sources retained separately")
    local("E-recall-revision-main", "draft", "paper/manuscript/main.tex", "Title, abstract, review options and eight selected section inputs")
    for i, p in enumerate(paths):
        local("E-recall-revision-section-" + str(i + 1), "draft", str(p.relative_to(ROOT)).replace("\\", "/"), "Entire active section; paragraph-level claim bindings in manuscript_claim_map.json")

    claims = []
    for suffix, rows, eid, metrics in [
        ("profiles", [r for r in strata if (r["series_id"] == "core" and r["condition"] in {"K1", "K2", "K3", "K4", "K7"}) or (r["series_id"] == "full_braw" and r["condition"] in {"Braw", "Braw+E"})], "E-recall-revision-strata", ["recall", "precision", "exact"]),
        ("means", [r for r in conditions if r["series_id"] in {"core", "full_braw"}], "E-recall-revision-conditions", ["recall", "precision", "exact"]),
    ]:
        numbers = []
        for r in rows:
            selector = ",".join(k + "=" + r[k] for k in ["series_id", "model", "condition"] + (["motif", "size"] if suffix == "profiles" else []))
            for metric in metrics:
                numbers.append(dict(value=float(r[metric]), metric=metric, evidence_id=eid,
                                    locator="CSV row[" + selector + "], column " + metric, denominator=int(r["N"]),
                                    derivation="Saved all-planned per-task macro mean; invalid zero. Display rounds to three decimals; no new significance or interval claim."))
        claims.append(dict(id="C-recall-revision-" + suffix, text="Reported " + suffix + " precision/recall/exact values match the saved archived aggregate rows in the declared manuscript scope.",
                           type="empirical", status="supported", scope="Recall revision abstract, Results, main/supplementary plots and numeric tables", evidence_ids=[eid],
                           reason="Exact figure-row and table selection checks passed; archived scoring tier, denominators, pairing and descriptive limits preserved.", numeric=True, numbers=numbers))

    # Each active paragraph gets explicit claim families; figures/tables get
    # independent source-row bindings rather than relying on the prose alone.
    ledger_path = NOTES / "evidence_register.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    registered = {e["id"]: e for e in ledger["evidence"]}
    for e in evidence:
        if e["id"] in registered:
            assert registered[e["id"]]["sha256"] == e["sha256"], e["id"]
    old_map = NOTES / "manuscript_claim_map.json"
    if old_map.exists():
        backup_map = OUT / "previous_manuscript_claim_map.json"
        if not backup_map.exists():
            shutil.copyfile(old_map, backup_map)
        for e in ledger["evidence"]:
            if e.get("path") == "paper/research_notes/manuscript_claim_map.json":
                e["historical_original_path"] = e["path"]
                e["path"] = str(backup_map.relative_to(ROOT)).replace("\\", "/")
    ledger["evidence"].extend(e for e in evidence if e["id"] not in registered)
    write(ledger_path, ledger)
    claim_path = NOTES / "claims.jsonl"
    registered_claims = {json.loads(line)["id"]: json.loads(line) for line in claim_path.read_text(encoding="utf-8").splitlines() if line.strip()}
    with claim_path.open("a", encoding="utf-8") as stream:
        for c in claims:
            if c["id"] in registered_claims:
                assert registered_claims[c["id"]] == c
            else:
                stream.write(json.dumps(c, ensure_ascii=False) + "\n")
    groups = {
        "01": ["C-tool-pattern-premise", "C-transfer-prior-overlap", "C-core-pairing", "C-raw-overlay-pairing", "C-pr-descriptive-effects"],
        "02": ["C-transfer-prior-overlap", "C-transfer-adjusted-tree", "C-nr-encoding", "C-nr-graphwalk"],
        "03": ["C-frozen-reference-consistency", "C-core-pairing", "C-raw-overlay-pairing"],
        "04": ["C-core-pairing", "C-raw-overlay-pairing", "C-manuscript-recorded-settings"],
        "05": ["C-recall-revision-profiles", "C-recall-revision-means", "C-pr-descriptive-effects", "C-assets-errors", "C-nr-groups", "C-nr-transitions"],
        "06": ["C-tool-pattern-premise", "C-transfer-adjusted-tree", "C-transfer-prior-overlap", "C-nr-alternative_rules", "C-nr-mechanism"],
        "07": ["C-recall-revision-profiles", "C-pr-descriptive-effects", "C-assets-errors", "C-nr-transitions"],
        "08": ["C-recall-revision-profiles", "C-recall-revision-means", "C-nr-groups", "C-nr-transitions", "C-nr-alternative_rules"],
    }
    all_claims = {json.loads(line)["id"]: json.loads(line) for line in claim_path.read_text(encoding="utf-8").splitlines() if line.strip()}
    # The old request-setting claim is resolved by exact registered ID.
    if "C-manuscript-recorded-settings" not in all_claims:
        candidates = [cid for cid in all_claims if "request" in cid and "settings" in cid]
        assert len(candidates) == 1
        groups["04"] = [candidates[0] if cid == "C-manuscript-recorded-settings" else cid for cid in groups["04"]]
    entries = []
    for p, text in texts.items():
        key = p.name[:2]
        assert all(cid in all_claims for cid in groups[key]), groups[key]
        cursor = 0
        for index, para in enumerate(re.split(r"\n\s*\n", text)):
            if not para.strip():
                continue
            offset = text.find(para, cursor)
            cursor = offset + len(para)
            entries.append(dict(path=str(p.relative_to(ROOT)).replace("\\", "/"), sha256=sha(p),
                                paragraph=index + 1, start_line=text[:offset].count("\n") + 1, claim_ids=groups[key],
                                scope_note="Paragraph-family evidence map; hypotheses stay hypotheses. Mathematical definitions and authorial research aims are not empirical findings."))
    entries.append(dict(path="paper/manuscript/main.tex", sha256=sha(PAPER / "main.tex"), locator="abstract", claim_ids=["C-pr-descriptive-effects", "C-table2-all-model-metrics"]))
    for f in assets["figures"]:
        entries.append(dict(locator="figure:" + f["id"], claim_ids=["C-assets-errors"] if f["id"] == "residual_errors" else ["C-recall-revision-profiles"],
                            result_evidence_id="E-recall-revision-assets", row_locator="$.figures[id=" + f["id"] + "].source_rows", file_hashes=f["files"]))
    for name, t in assets["tables"].items():
        entries.append(dict(locator="table:" + name, path=t["path"], sha256=t["sha256"],
                            claim_ids=["C-pr-descriptive-effects"] if name.endswith("effects") else ["C-recall-revision-means"] if name.startswith("core_") else ["C-table2-all-model-metrics"],
                            result_evidence_id="E-recall-revision-assets", row_locator="$.tables." + name + ".rows"))
    write(old_map, dict(schema_version=1, checked_on="2026-10-26", intended_scope="Bounded author-approved recall revision; descriptive and hypothesis-qualified, not originality certification",
                       entries=entries, limitations=["Paragraph maps bind claim families rather than machine-prove each sentence.", "Missing raw replies and exact cross-paper row reuse remain disclosed.", "No causal mechanism or recall/precision significance claim."]))
    # New-scope structural audit includes the upstream closure of mapped claims.
    audit = OUT / "claim_audit"
    audit.mkdir(exist_ok=True)
    ids = {e["id"]: e for e in ledger["evidence"]}
    wanted_claims = {cid for entry in entries for cid in entry.get("claim_ids", [])}
    wanted_evidence = {e["id"] for e in evidence}

    def add(eid):
        if eid in wanted_evidence:
            return
        wanted_evidence.add(eid)
        for parent in ids[eid].get("upstream_evidence_ids", []):
            add(parent)

    for cid in wanted_claims:
        for eid in all_claims[cid]["evidence_ids"]:
            add(eid)
    # Stale older byte hashes remain production issues; this scoped integrity
    # view inspects each actual source and records its old hash transparently.
    scoped_evidence = []
    for eid in sorted(wanted_evidence):
        e = copy.deepcopy(ids[eid])
        if e.get("path") and sha(ROOT / e["path"]) != e.get("sha256"):
            raw = (ROOT / e["path"]).read_bytes()
            lf = raw.replace(b"\r\n", b"\n")
            assert e["sha256"] in {hashlib.sha256(lf).hexdigest(), hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()}, eid
            e["historical_recorded_sha256"] = e["sha256"]
            e["sha256"] = sha(ROOT / e["path"])
            e["limitations"] = e.get("limitations", "") + " Scoped byte inspection: original hash reproduced solely by LF/CRLF conversion; production hash preserved."
        scoped_evidence.append(e)
    write(audit / "evidence_register.json", dict(schema_version=1, evidence=scoped_evidence))
    (audit / "claims.jsonl").write_text("".join(json.dumps(all_claims[cid], ensure_ascii=False) + "\n" for cid in sorted(wanted_claims)), encoding="utf-8")
    write(audit / "workflow_state.json", json.loads((NOTES / "workflow_state.json").read_text(encoding="utf-8")))
    validate = runpy.run_path(str(NOTES / "scripts/validate_research_artifacts.py"))["validate"]
    scoped = validate(ROOT, audit)
    write(audit / "validation.json", scoped)
    assert scoped["status"] == "passed", scoped
    result = dict(status="passed", active_sections=len(paths), bibliography_keys=len(cited), undefined_references=0,
                  figure_and_table_sources="exact saved-row/source hash agreement", new_inference=False,
                  scoped_structural=scoped, production_structural=validate(ROOT, NOTES))
    write(OUT / "verification.json", result)
    print(json.dumps({"status": result["status"], "active_sections": len(paths), "mapped_entries": len(entries),
                      "scoped_structural": scoped["status"], "production_errors": len(result["production_structural"]["errors"])}))


if __name__ == "__main__":
    main()
