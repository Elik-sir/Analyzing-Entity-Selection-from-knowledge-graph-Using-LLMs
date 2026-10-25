"""Bounded exploratory diagnostics of saved selections; no model or database calls.

Only common six-node families are selected. Set transitions use cached metrics.
Route diagnostics use saved selected_names and independently traverse the explicit
public graph. Missing selections are counted, never reconstructed from scores.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
FAMILIES = {"chain", "star_in", "star_out", "tree_in", "tree_out"}


def read_rows(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def included(o):
    return o["size"] == 6 and o["motif"] in FAMILIES and (
        (o["series_id"] == "core" and (o["condition"] in {"K1", "K2"} or
         (o["motif"] == "tree_in" and o["condition"] in {"K3", "K4", "K7"}))) or
        (o["series_id"] == "full_braw" and o["condition"] in {"Braw", "Braw+E"}))


def key(o):
    return tuple(o[x] for x in ("series_id", "model", "condition", "noise", "motif"))


def category(o):
    if not o["valid"]:
        return "invalid"
    fp, fn = o["metrics"]["fp"], o["metrics"]["fn"]
    return "exact" if fp == fn == 0 else "omission_only" if fp == 0 else "inclusion_only" if fn == 0 else "mixed"


def public(payload):
    if payload.get("frozen_public"):
        return payload["frozen_public"]
    for msg in reversed(payload.get("messages") or []):
        if msg.get("role") == "user":
            value = json.loads(msg["content"])
            if isinstance(value, dict) and "candidates" in value:
                return value
    raise ValueError("No serialized public candidate graph")


def graph_reference(payload):
    ref = payload["reference"]
    private = ref.get("private", ref)
    spec = private["task_spec"]
    cards = public(payload)["candidates"]
    if private.get("name_map"):
        names = private["name_map"]
    else:
        names = dict(zip(private["candidate_ids"], payload["candidate_names"], strict=True))
    anchor = names[spec["anchor_id"]]
    expected = {names[x] for x in spec["reference_ids"]}
    types = {c["name"]: c["type"] for c in cards}
    edges = {(e["source"], e["target"]) for c in cards
             for e in c["facts"].get("relations", [])}
    adjacency = defaultdict(set)
    for a, b in edges:
        if spec["direction"] == "in":
            a, b = b, a
        adjacency[a].add(b)
    paths = []

    def visit(path):
        nxt = adjacency[path[-1]] - set(path)
        steps = len(path) - 1
        terminal = spec["terminal_type"]
        stop = steps > 0 and ((terminal is not None and types[path[-1]] == terminal) or
                              (spec["depth"] is not None and
                               (steps == spec["depth"] or not nxt)))
        if stop:
            paths.append(tuple(path))
        elif terminal is not None or steps < spec["depth"]:
            for v in sorted(nxt):
                visit(path + [v])

    visit([anchor])
    witness = {anchor} | {v for p in paths for v in p}
    assert witness == expected, ("Witness mismatch", payload["input_id"])
    assert {names[x] for x in spec["target_ids"]} == {p[-1] for p in paths}
    first = adjacency[anchor]
    return anchor, expected, paths, first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    observations, core_cached = [], []
    for o in read_rows(ROOT / "results/observations.jsonl.gz"):
        if included(o):
            observations.append(o)
        if o["series_id"] == "core" and o["size"] == 6 and o["motif"] in FAMILIES and o["condition"] in {"K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8"}:
            core_cached.append(o)
    assert len({o["observation_id"] for o in observations}) == len(observations) == 6900
    needed = {o["input_id"] for o in observations}
    inputs = {p["input_id"]: p for p in read_rows(ROOT / "results/inputs.jsonl.gz") if p["input_id"] in needed}
    assert set(inputs) == needed
    groups = defaultdict(Counter)
    row_diagnostics = []
    routes_checked = set()
    graph_cache = {}
    examples = []
    for o in observations:
        g = groups[key(o)]
        g["N"] += 1
        g[category(o)] += 1
        if o["valid"]:
            g["valid"] += 1
            g["f1_sum"] += o["metrics"]["f1"]
            g["complete_reference"] += o["metrics"]["fn"] == 0
        selected = o.get("selected_names")
        if selected is None:
            g["selected_names_missing"] += 1
            continue
        g["selected_names_present"] += 1
        if not o["valid"]:
            continue
        assert len(selected) == len(set(selected))
        if o["condition"] == "Braw":
            continue  # Native sufficiency is not established; no public-graph traversal claim.
        ref = inputs[o["input_id"]]["reference"]
        if "task_spec" not in ref.get("private", ref):
            g["task_spec_missing_for_route_diagnostic"] += 1
            continue  # Do not fill missing historical specifications from current defaults.
        if o["input_id"] not in graph_cache:
            graph_cache[o["input_id"]] = graph_reference(inputs[o["input_id"]])
        anchor, expected, paths, first = graph_cache[o["input_id"]]
        routes_checked.add(o["input_id"])
        s = set(selected)
        assert s <= set(inputs[o["input_id"]]["candidate_names"])
        assert len(expected - s) == o["metrics"]["fn"]
        assert len(s - expected) == o["metrics"]["fp"]
        f1 = 2 * len(s & expected) / (len(s) + len(expected))
        assert abs(f1 - o["metrics"]["f1"]) < 1e-12
        g["route_diagnostic_n"] += 1
        endpoints = {p[-1] for p in paths}
        intermediates = expected - endpoints - {anchor}
        complete_paths = sum(set(p) <= s for p in paths)
        d = dict(observation_id=o["observation_id"], input_id=o["input_id"],
                 series_id=o["series_id"], model=o["model"], condition=o["condition"],
                 noise=o["noise"], motif=o["motif"], base_id=o["base_id"],
                 paths=len(paths), complete_paths=complete_paths,
                 endpoint_n=len(endpoints), endpoint_selected=len(endpoints & s),
                 intermediate_n=len(intermediates), intermediate_selected=len(intermediates & s),
                 anchor_selected=anchor in s,
                 exact_one_hop_set=s == ({anchor} | first),
                 all_first_hop_selected=({anchor} | first) <= s,
                 any_endpoint_missing=not endpoints <= s,
                 all_endpoints_selected=endpoints <= s)
        # First-hop completeness with endpoint omissions is descriptive, not a mental trace.
        for role, v in [("endpoint", endpoints), ("intermediate", intermediates)]:
            g[role + "_opportunities"] += len(v)
            g[role + "_selected"] += len(v & s)
        g["anchor_missing"] += anchor not in s
        g["paths_total"] += len(paths)
        g["paths_complete"] += complete_paths
        g["task_mean_path_coverage_sum"] += complete_paths / len(paths)
        g["exact_one_hop_set"] += d["exact_one_hop_set"]
        g["all_first_hop_but_missing_endpoint"] += d["all_first_hop_selected"] and d["any_endpoint_missing"]
        g["all_endpoints_but_missing_witness"] += d["all_endpoints_selected"] and not expected <= s
        g["some_but_not_all_paths_complete"] += 0 < complete_paths < len(paths)
        # Wholly absent first-hop branch: neither its first node nor any descendant
        # along its permitted routes was selected. Applies to any multi-route family.
        branches = defaultdict(set)
        for p in paths:
            branches[p[1]].update(p[1:])
        g["branch_opportunities"] += len(branches)
        g["wholly_absent_branches"] += sum(not (nodes & s) for nodes in branches.values())
        if o["motif"] == "tree_in" and d["exact_one_hop_set"] and len(examples) < 5:
            examples.append(d)
        row_diagnostics.append(d)

    formatted = []
    for k, g in sorted(groups.items()):
        assert g["N"] == 100
        assert sum(g[x] for x in ("exact", "omission_only", "inclusion_only", "mixed", "invalid")) == g["N"]
        formatted.append(dict(zip(("series_id", "model", "condition", "noise", "motif"), k)) |
                         dict(g) | {"size": 6, "f1": g["f1_sum"] / g["N"],
                                    "complete_reference_rate": g["complete_reference"] / g["N"]})
    pairs = defaultdict(dict)
    for o in observations:
        if o["series_id"] == "full_braw":
            k = tuple(o[x] for x in ("model", "motif", "size", "noise", "base_id"))
            assert o["condition"] not in pairs[k]
            pairs[k][o["condition"]] = o
    transitions = defaultdict(Counter)
    for k, pair in pairs.items():
        assert set(pair) == {"Braw", "Braw+E"}
        a, b = pair["Braw"], pair["Braw+E"]
        g = transitions[k[:2]]
        g["N_pairs"] += 1
        g[category(a) + "_to_" + category(b)] += 1
        g["f1_delta_sum"] += (b["metrics"]["f1"] if b["valid"] else 0) - (a["metrics"]["f1"] if a["valid"] else 0)
        g["exact_gained"] += category(a) != "exact" and category(b) == "exact"
        g["exact_lost"] += category(a) == "exact" and category(b) != "exact"
    transition_rows = [dict(model=k[0], motif=k[1], size=6, **dict(g)) for k, g in sorted(transitions.items())]
    for g in transition_rows:
        assert g["N_pairs"] == 100
        assert sum(v for k, v in g.items() if "_to_" in k) == 100
    core_pairs = defaultdict(dict)
    supplementary = defaultdict(Counter)
    for o in core_cached:
        k = (o["model"], o["motif"], o["base_id"])
        assert o["condition"] not in core_pairs[k]
        core_pairs[k][o["condition"]] = o
        g = supplementary[(o["model"], o["motif"], o["condition"])]
        g["N"] += 1
        g[category(o)] += 1
        if o["valid"]:
            g["valid"] += 1
            g["f1_sum"] += o["metrics"]["f1"]
    controlled = defaultdict(Counter)
    contrast_pairs = [("K1", "K3"), ("K1", "K4"), ("K1", "K5"), ("K1", "K7"), ("K5", "K8"), ("K5", "K6")]
    for (model, motif, base), pair in core_pairs.items():
        assert len(pair) == 8
        for a, b in contrast_pairs:
            before, after = pair[a], pair[b]
            g = controlled[(model, motif, a, b)]
            g["N_pairs"] += 1
            g["f1_delta_sum"] += (after["metrics"]["f1"] if after["valid"] else 0) - (before["metrics"]["f1"] if before["valid"] else 0)
            g["exact_gained"] += category(before) != "exact" and category(after) == "exact"
            g["exact_lost"] += category(before) == "exact" and category(after) != "exact"
            g[category(before) + "_to_" + category(after)] += 1
    supplementary_rows = [dict(model=k[0], motif=k[1], condition=k[2], size=6, **dict(g), f1=g["f1_sum"] / g["N"]) for k, g in sorted(supplementary.items())]
    controlled_rows = [dict(model=k[0], motif=k[1], before=k[2], after=k[3], size=6, **dict(g), f1_delta=g["f1_delta_sum"] / g["N_pairs"]) for k, g in sorted(controlled.items())]
    assert len(core_cached) == 12000
    assert all(g["N"] == 100 for g in supplementary_rows)
    assert all(g["N_pairs"] == 100 and sum(v for k, v in g.items() if "_to_" in k) == 100 for g in controlled_rows)
    sources = [ROOT / "results/observations.jsonl.gz", ROOT / "results/inputs.jsonl.gz", Path(__file__)]
    pdf = ROOT / "paper/research_notes/sources/tool_graph_complexity.pdf"
    sources.append(pdf)
    result = dict(schema_version=1, checked_on="2026-10-25",
                  scope="Exploratory saved-score and saved-selection diagnostics at common size six; no cross-domain metric harmonization, new model calls, raw-response reparse or hypothesis test.",
                  selector={"size": 6, "motifs": sorted(FAMILIES), "core_conditions": ["K1", "K2"], "additional_tree_in_conditions": ["K3", "K4", "K7"], "full_conditions": ["Braw", "Braw+E"]},
                  observations=len(observations), unique_inputs=len(inputs),
                  unique_explicit_inputs_oracle_checked=len(routes_checked),
                  route_diagnostic_observations=len(row_diagnostics),
                  groups=formatted, paired_transitions=transition_rows, examples=examples,
                  supplementary_core_cached_observations=len(core_cached),
                  supplementary_core_cached_groups=supplementary_rows,
                  controlled_paired_transitions=controlled_rows,
                  formulas={"complete_reference_rate": "count(valid and cached fn == 0) / all planned N",
                            "f1": "sum(valid cached F1) / all planned N",
                            "role_selection_rate": "sum selected role nodes / sum role opportunities over valid outcomes with saved selected_names; task/node dependence retained, no binomial inference",
                            "task_mean_path_coverage": "mean(count(reference paths whose every vertex is selected)/count(reference paths)) over valid outcomes with saved selected_names",
                            "exact_one_hop_set": "S equals anchor union all permitted first-hop neighbours; on tree tasks this is consistent with but does not establish early stopping",
                            "all_first_hop_but_missing_endpoint": "anchor and all permitted first-hop neighbours selected, at least one reference endpoint missing",
                            "wholly_absent_branches": "count first-hop groups for which no non-anchor vertex on any allowed path in that group was selected; shared descendants can belong to multiple groups"},
                  limitations=["Gemma Core selected_names unavailable; cached fn/fp do not recover identities.",
                               "Explicit inputs without a saved task_spec are counted and excluded from route diagnostics; no current defaults are imputed.",
                               "Native Raw relations may be missing; Raw is not an equally informative implicit-dependency condition.",
                               "Route completion concerns selected vertex sets, not predicted edges, executed plans or internal computation.",
                               "Core and Full overlap and are not independent replications.",
                               "Size six, frozen task families and current sample do not isolate topology or causal mechanisms.",
                               "No Tool Graph record archive was available for a harmonized item-level transfer test."],
                  validation={"status": "passed", "unique_observations": True, "planned_per_group": 100,
                              "cached_metric_agreement_for_available_explicit_selections": True,
                              "independent_public_graph_witness_and_endpoint_agreement": True,
                              "paired_transition_conservation": True},
                  provenance={"revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                              "sources": {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                              "command": "python paper/research_notes/analyses/transfer_positioning/diagnose_transfer.py --out " + str(out).replace("\\", "/")})
    (out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / "route_diagnostics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(row_diagnostics[0]))
        writer.writeheader()
        writer.writerows(row_diagnostics)
    print(json.dumps({k: result[k] for k in ("observations", "unique_inputs", "unique_explicit_inputs_oracle_checked", "route_diagnostic_observations", "validation")}))


if __name__ == "__main__":
    main()
