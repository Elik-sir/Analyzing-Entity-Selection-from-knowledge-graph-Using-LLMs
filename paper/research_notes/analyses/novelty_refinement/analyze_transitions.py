"""Exploratory offline Tree-in output signatures; no inference or research imports.

Retains all planned outcomes in transition matrices. Alternative-rule matches
are output-set compatibility, never evidence of the model's internal algorithm.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
CONDITIONS = {"K1", "K2", "K3", "K4", "K7"}


def rows(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def public(payload):
    if payload.get("frozen_public"):
        return payload["frozen_public"]
    for message in reversed(payload["messages"]):
        if message["role"] == "user":
            value = json.loads(message["content"])
            if isinstance(value, dict) and "candidates" in value:
                return value
    raise ValueError(payload["input_id"])


def coverage(anchor, edges, direction, depth):
    """Union of simple routes, stopping at depth or a dead end, plus anchor."""
    adj = defaultdict(set)
    for source, target in edges:
        if direction in {"out", "both"}:
            adj[source].add(target)
        if direction in {"in", "both"}:
            adj[target].add(source)
    paths = []

    def visit(path):
        next_nodes = adj[path[-1]] - set(path)
        if len(path) > 1 and (len(path) - 1 == depth or not next_nodes):
            paths.append(tuple(path))
        else:
            for node in sorted(next_nodes):
                visit(path + [node])

    visit([anchor])
    return {anchor} | {v for path in paths for v in path}, paths


def graph(payload):
    ref = payload["reference"]
    private = ref.get("private", ref)
    spec = private["task_spec"]
    assert spec["direction"] == "in" and spec["depth"] == 2
    assert spec["terminal_type"] is None
    names = private.get("name_map") or dict(zip(private["candidate_ids"], payload["candidate_names"], strict=True))
    anchor = names[spec["anchor_id"]]
    expected = {names[v] for v in spec["reference_ids"]}
    cards = public(payload)["candidates"]
    directed_facts = {(e["source"], e["relation"], e["target"])
                      for c in cards for e in c["facts"].get("relations", [])}
    edges = {(a, b) for a, _, b in directed_facts}
    witness, paths = coverage(anchor, edges, "in", 2)
    assert witness == expected and len(expected) == 6
    assert {p[-1] for p in paths} == {names[v] for v in spec["target_ids"]}
    alternatives = {
        "depth_one": coverage(anchor, edges, "in", 1)[0],
        "reversed_direction": coverage(anchor, edges, "out", 2)[0],
        "undirected": coverage(anchor, edges, "both", 2)[0],
        "depth_three": coverage(anchor, edges, "in", 3)[0],
    }
    fingerprint = (anchor, frozenset(expected), frozenset(directed_facts),
                   frozenset((c["name"], c["type"]) for c in cards))
    return expected, alternatives, fingerprint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    assert not args.out.exists(), "Choose a fresh output directory"
    observations = [o for o in rows(ROOT / "results/observations.jsonl.gz")
                    if o["series_id"] == "core" and o["size"] == 6
                    and o["motif"] == "tree_in" and o["condition"] in CONDITIONS]
    assert len(observations) == 1500
    assert len({o["observation_id"] for o in observations}) == len(observations)
    needed = {o["input_id"] for o in observations}
    inputs = {p["input_id"]: p for p in rows(ROOT / "results/inputs.jsonl.gz") if p["input_id"] in needed}
    assert set(inputs) == needed
    graphs = {i: graph(p) for i, p in inputs.items()}
    group_counts = defaultdict(Counter)
    alternatives_counts = defaultdict(Counter)
    paired = defaultdict(dict)
    diagnostic_rows = []
    for o in observations:
        expected, alternatives, fingerprint = graphs[o["input_id"]]
        gkey = (o["model"], o["condition"])
        g = group_counts[gkey]
        g["planned"] += 1
        g["valid"] += bool(o["valid"])
        is_exact = o["valid"] and o["metrics"]["fp"] == o["metrics"]["fn"] == 0
        g["cached_exact"] += is_exact
        row = {k: o[k] for k in ("observation_id", "input_id", "base_id", "model", "condition")}
        row["valid"] = bool(o["valid"])
        row["cached_exact"] = bool(is_exact)
        selected = o.get("selected_names")
        if not o["valid"]:
            state = "invalid"
        elif selected is None:
            state = "identities_missing"
        else:
            selected = set(selected)
            assert selected <= set(inputs[o["input_id"]]["candidate_names"])
            assert len(expected - selected) == o["metrics"]["fn"]
            assert len(selected - expected) == o["metrics"]["fp"]
            f1 = 2 * len(expected & selected) / (len(expected) + len(selected))
            assert abs(f1 - o["metrics"]["f1"]) < 1e-12
            g["identity_diagnostic_valid"] += 1
            assert alternatives["depth_one"] != expected
            state = "exact" if selected == expected else "one_hop" if selected == alternatives["depth_one"] else "other_error"
            for label, alternative in alternatives.items():
                a = alternatives_counts[gkey + (label,)]
                a["valid_identity_denominator"] += 1
                a["distinct_from_reference"] += alternative != expected
                a["distinct_and_nontrivial"] += alternative != expected and len(alternative) > 1
                a["matches_distinct_alternative"] += selected == alternative and alternative != expected
                row[label + "_distinct"] = alternative != expected
                row[label + "_match"] = selected == alternative
            row["selected_count"] = len(selected)
        row["state"] = state
        g[state] += 1
        pkey = (o["model"], o["base_id"])
        assert o["condition"] not in paired[pkey]
        paired[pkey][o["condition"]] = (row, fingerprint)
        diagnostic_rows.append(row)
    transitions = defaultdict(Counter)
    controls = [("K1", "K2"), ("K1", "K3"), ("K1", "K4"), ("K1", "K7"), ("K3", "K4"), ("K7", "K4")]
    for (model, base), variants in paired.items():
        assert set(variants) == CONDITIONS
        assert len({v[1] for c, v in variants.items() if c != "K2"}) == 1, ("Unique facts/types/reference mismatch", model, base)
        assert variants["K1"][1][:2] == variants["K2"][1][:2], ("Noise-pair anchor/reference mismatch", model, base)
        for before, after in controls:
            a, b = variants[before][0], variants[after][0]
            g = transitions[(model, before, after)]
            g["planned_pairs"] += 1
            g[a["state"] + "_to_" + b["state"]] += 1
            g["cached_exact_gained"] += not a["cached_exact"] and b["cached_exact"]
            g["cached_exact_lost"] += a["cached_exact"] and not b["cached_exact"]
    for g in group_counts.values():
        assert g["planned"] == 100
        assert sum(g[s] for s in ("exact", "one_hop", "other_error", "invalid", "identities_missing")) == 100
    for g in transitions.values():
        assert g["planned_pairs"] == 100
        assert sum(v for k, v in g.items() if "_to_" in k) == 100
    previous = json.loads((ROOT / "paper/research_notes/analyses/transfer_positioning/run-04/summary.json").read_text())
    for old in previous["groups"]:
        if old["series_id"] == "core" and old["motif"] == "tree_in" and old["condition"] in CONDITIONS:
            g = group_counts[(old["model"], old["condition"])]
            assert g["cached_exact"] == old.get("exact", 0)
            assert g["one_hop"] == old.get("exact_one_hop_set", 0)
    sources = [ROOT / p for p in ("results/observations.jsonl.gz", "results/inputs.jsonl.gz",
               "paper/research_notes/analyses/transfer_positioning/run-04/summary.json")]
    sources.append(Path(__file__))
    result = {
        "checked_on": "2026-10-25", "scope": "Exploratory archived Core six-node Tree-in only; no new model run or hypothesis test",
        "selector": {"series_id": "core", "motif": "tree_in", "size": 6, "conditions": sorted(CONDITIONS)},
        "observations": len(observations), "unique_inputs": len(inputs), "paired_model_base_units": len(paired),
        "groups": [dict(model=k[0], condition=k[1], **dict(v)) for k, v in sorted(group_counts.items())],
        "transitions": [dict(model=k[0], before=k[1], after=k[2], **dict(v)) for k, v in sorted(transitions.items())],
        "alternative_rules": [dict(model=k[0], condition=k[1], rule=k[2], **dict(v)) for k, v in sorted(alternatives_counts.items())],
        "validation": {"status": "passed", "independent_public_graph_witness_and_endpoint_agreement": True,
                       "K1_K3_K4_K7_unique_typed_facts_candidate_types_and_targets_equal": True,
                       "K1_K2_anchor_and_reference_equal": True,
                       "all_states_and_transitions_conserve_planned_denominators": True,
                       "available_selected_identities_agree_with_cached_metrics": True,
                       "previous_scoped_exact_and_one_hop_counts_agree": True},
        "definitions": {"one_hop": "S equals anchor union incoming neighbours; disjoint from exact in this slice",
                        "other_error": "valid saved selection differs from reference and exact one-hop set",
                        "alternative_match": "S equals alternative-rule coverage set; may overlap another rule and does not identify an internal operation",
                        "reference": "anchor plus union of simple incoming paths, depth two or earlier dead-end; checked against frozen reference and endpoints"},
        "limitations": ["Post-hoc exploratory selection motivated by earlier Qwen results; not confirmatory.",
                        "Gemma identity-level signatures unavailable; cached exact remains separate.",
                        "No Tool record analysis, causal identification, new confidence interval, QA evaluation or raw-response reparse.",
                        "Non-distinct alternative rules cannot diagnose a rule error, even if the selected set matches them.",
                        "K4 changes redundancy/length/salience as well as card hosting; no isolated placement mechanism.",
                        "No type-stopping analysis: this slice has terminal_type=None. Other families/noise require separate checks."],
        "provenance": {"revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                       "sources": {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in sources},
                       "command": "python paper/research_notes/analyses/novelty_refinement/analyze_transitions.py --out " + args.out.as_posix()},
    }
    args.out.mkdir(parents=True)
    (args.out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.out / "observations.jsonl").open("w", encoding="utf-8") as stream:
        for row in diagnostic_rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"observations": len(observations), "validation": result["validation"]}))
    for row in result["transitions"]:
        if row["model"] == "qwen3.6-flash":
            print(json.dumps(row))


if __name__ == "__main__":
    main()
