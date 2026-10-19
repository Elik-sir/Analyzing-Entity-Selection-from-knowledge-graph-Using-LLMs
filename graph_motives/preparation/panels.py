"""Paired selection and independent private-graph structural audits.

These checks establish hidden-graph consistency. They do not establish that
legacy node descriptions contain the evidence required to answer a question.
"""

from __future__ import annotations

import copy
import json
from collections import Counter, defaultdict
from collections.abc import Mapping

from ..graph.graph import digest, norm, open_text
from .registry import CORE_SIZES, TARGETED_SIZES

VARIANTS = ("disconnected", "adjacent")


def load_legacy_items(paths):
    """Load gzip/plain JSONL paths, optionally a variant -> path mapping."""
    if isinstance(paths, Mapping):
        entries = list(paths.items())
    elif isinstance(paths, (str, bytes)) or hasattr(paths, "__fspath__"):
        entries = [(None, paths)]
    else:
        entries = [(None, path) for path in paths]
    rows, seen = [], set()
    for expected_variant, path in entries:
        with open_text(path) as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"Expected item object: {path}:{line_number}")
                key = (row.get("record_id"), row.get("variant"))
                if not isinstance(key[0], str) or not key[0] or key[1] not in VARIANTS:
                    raise ValueError(f"Invalid item identity: {path}:{line_number}")
                if expected_variant is not None and expected_variant != key[1]:
                    raise ValueError(f"Variant does not match source path: {path}:{line_number}")
                if key in seen:
                    raise ValueError(f"Duplicate item identity: {key}")
                seen.add(key)
                rows.append(row)
    return rows


def resolve_candidate_ids(item, graph):
    """Resolve candidates to unique usable snapshot nodes in candidate order."""
    candidates = item["public"]["candidates"]
    ids, seen = [], set()
    for candidate in candidates:
        name = candidate.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Candidate has no name")
        key = norm(name)
        nid = graph.name_to_id.get(key)
        if nid is None:
            raise ValueError(f"Candidate is not a usable snapshot node: {name}")
        if nid in seen:
            raise ValueError(f"Duplicate candidate node: {name}")
        node = graph.nodes[nid]
        if node.get("unnamed") or "dup_of" in node:
            raise ValueError(f"Candidate resolves to an excluded node: {name}")
        if candidate.get("type") != node["type"]:
            raise ValueError(f"Candidate type differs from snapshot: {name}")
        seen.add(nid)
        ids.append(nid)
    return ids


def audit_pairing(items):
    """Verify that variants pair by record_id and share their private target."""
    groups, errors = defaultdict(dict), []
    for row in items:
        rid, variant = row.get("record_id"), row.get("variant")
        if not isinstance(rid, str) or not rid or variant not in VARIANTS:
            errors.append({"record_id": rid, "code": "invalid_identity"})
            continue
        if variant in groups[rid]:
            errors.append({"record_id": rid, "code": "duplicate_variant"})
        groups[rid][variant] = row
    for rid, variants in sorted(groups.items()):
        if set(variants) != set(VARIANTS):
            errors.append({"record_id": rid, "code": "unpaired_variant"})
            continue
        left, right = (variants[v] for v in VARIANTS)
        shared = ["graph_hash", "subgraph_type", "size", "protocol"]
        if any(left.get(k) != right.get(k) for k in shared):
            errors.append({"record_id": rid, "code": "pair_identity_mismatch"})
        lp, rp = left.get("private", {}), right.get("private", {})
        if any(lp.get(k) != rp.get(k) for k in ("anchor", "pattern", "reference_ids", "reference_names", "answer")):
            errors.append({"record_id": rid, "code": "pair_gold_mismatch"})
        if left.get("public", {}).get("question") != right.get("public", {}).get("question"):
            errors.append({"record_id": rid, "code": "pair_question_mismatch"})
        reference = set(lp.get("reference_names", []))
        cards = []
        for row in (left, right):
            cards.append({n.get("name"): n for n in row.get("public", {}).get("candidates", []) if n.get("name") in reference})
        if set(cards[0]) != reference or cards[0] != cards[1]:
            errors.append({"record_id": rid, "code": "pair_reference_card_mismatch"})
    return {"status": "ok" if not errors else "error", "errors": errors,
            "rows": len(items), "base_records": len(groups),
            "error_counts": dict(Counter(e["code"] for e in errors))}


def _paired_groups(items):
    items = list(items)
    report = audit_pairing(items)
    if report["errors"]:
        raise ValueError(f"Invalid paired input: {report['error_counts']}")
    groups = defaultdict(dict)
    for row in items:
        groups[row["record_id"]][row["variant"]] = row
    return groups


def _select_panel(items, cells, per_cell, seed, excluded_ids=()):
    if not isinstance(per_cell, int) or isinstance(per_cell, bool) or per_cell < 1:
        raise ValueError("per_cell must be a positive integer")
    groups = _paired_groups(items)
    excluded = {value[0] if isinstance(value, (list, tuple)) else value for value in excluded_ids}
    by_cell = defaultdict(list)
    for rid, variants in groups.items():
        if rid in excluded:
            continue
        row = variants[VARIANTS[0]]
        cell = (row["subgraph_type"], row["size"])
        by_cell[cell].append(rid)
    selected, shortages = [], []
    for motif, size in cells:
        ids = sorted(by_cell[(motif, size)], key=lambda rid: (digest([seed, motif, size, rid]), rid))
        if len(ids) < per_cell:
            shortages.append({"motif": motif, "size": size, "available": len(ids), "requested": per_cell})
        for rid in ids[:per_cell]:
            selected.extend(copy.deepcopy(groups[rid][v]) for v in VARIANTS)
    return selected, shortages


def build_comparison_panel(items, per_cell=100, seed=20261003, core_sizes=None):
    """Choose matched core base IDs; both noises use the same IDs.

    Input order does not affect the selection. Outputs are copies, and retain
    legacy identities so compatible historical traces remain joinable.
    """
    cells = list((CORE_SIZES if core_sizes is None else core_sizes).items())
    rows, shortages = _select_panel(items, cells, per_cell, seed)
    if shortages:
        raise ValueError(f"Insufficient core cells: {shortages}")
    return rows


def build_size_panel(items, sizes=None, per_cell=100, seed=20261003,
                     exclude_record_ids=(), exclude_core=True, core_sizes=None):
    """Select paired extra-size rows, excluding core cells by default.

    For the default targeted grid this adds eleven motif-size combinations
    (1,100 base records / 2,200 rows) to the seven core combinations.
    ``exclude_record_ids`` removes both variants together.
    """
    sizes = TARGETED_SIZES if sizes is None else sizes
    core_sizes = CORE_SIZES if core_sizes is None else core_sizes
    cells = [(motif, size) for motif, values in sizes.items() for size in values
             if not exclude_core or core_sizes.get(motif) != size]
    if len(set(cells)) != len(cells):
        raise ValueError("Duplicate size-panel cells")
    rows, shortages = _select_panel(items, cells, per_cell, seed, exclude_record_ids)
    if shortages:
        raise ValueError(f"Insufficient size-panel cells: {shortages}")
    return rows


def build_pilot_panel(items, excluded_ids, per_cell=5, seed=20261003, core_sizes=None):
    """Return held-out paired items, or an explicit shortage with no pilot rows.

    Existing main-panel records are never silently reassigned to the pilot.
    This function does not manufacture synthetic tasks or sample a new graph.
    """
    excluded_ids = tuple(excluded_ids)
    cells = list((CORE_SIZES if core_sizes is None else core_sizes).items())
    rows, shortages = _select_panel(items, cells, per_cell, seed, excluded_ids)
    return {"status": "insufficient_heldout" if shortages else "ok",
            "rows": [] if shortages else rows, "shortages": shortages,
            "requested_base_records": per_cell * len(cells),
            "available_complete_base_records": len(rows) // 2,
            "excluded_base_records": len({v[0] if isinstance(v, (list, tuple)) else v for v in excluded_ids}),
            "policy": "heldout_only_no_main_reassignment"}


def _edges(values, errors, code):
    if not isinstance(values, list) or any(not isinstance(e, (list, tuple)) or len(e) != 3
                                          or any(not isinstance(v, str) or not v for v in e) for e in values):
        errors.append(code)
        return set()
    edges = {tuple(e) for e in values}
    if len(edges) != len(values):
        errors.append(code + "_duplicates")
    return edges


def _derive(anchor, pattern, entities, edges, types):
    """Independent local oracle matching the historical reachability contract."""
    out, inc = defaultdict(list), defaultdict(list)
    for edge in edges:
        if edge[0] in entities and edge[2] in entities:
            out[edge[0]].append(edge)
            inc[edge[2]].append(edge)
    if anchor not in entities:
        return set(), set()
    kind, _, argument = pattern.partition(":")
    if kind == "path" and argument:
        seen, used = set(), set()
        stack = [(anchor, [anchor], [])]
        while stack:
            nid, path, path_edges = stack.pop()
            if nid != anchor and types.get(nid) == argument:
                seen.update(path)
                used.update(path_edges)
                continue
            for edge in out[nid]:
                if edge[2] not in path:
                    stack.append((edge[2], path + [edge[2]], path_edges + [edge]))
        return seen, used
    if kind == "path":
        kind, argument = "out", ""
    if kind not in ("out", "in", "both"):
        raise ValueError("Unknown traversal pattern")
    depth = int(argument) if argument else len(entities)
    if depth < 1:
        raise ValueError("Invalid traversal depth")
    seen, used, frontier = {anchor}, set(), [anchor]
    for _ in range(depth):
        nxt = []
        for nid in frontier:
            adj = (out[nid] if kind in ("out", "both") else []) + (inc[nid] if kind in ("in", "both") else [])
            for edge in adj:
                used.add(edge)
                other = edge[2] if edge[0] == nid else edge[0]
                if other not in seen:
                    seen.add(other)
                    nxt.append(other)
        frontier = nxt
        if not frontier:
            break
    return seen, used


def _topology(motif, nodes, edges, anchor):
    """Check exact directed motif, not merely edge count or undirected shape."""
    pairs = {(s, t) for s, _, t in edges}
    if len(pairs) != len(edges) or any(s == t for s, t in pairs):
        return False
    out, inc = {n: set() for n in nodes}, {n: set() for n in nodes}
    for s, t in pairs:
        if s not in nodes or t not in nodes:
            return False
        out[s].add(t)
        inc[t].add(s)
    if anchor not in nodes:
        return False
    if motif == "chain":
        if len(edges) != len(nodes) - 1 or inc[anchor] or len(out[anchor]) != 1:
            return False
        path, nid = {anchor}, anchor
        while out[nid]:
            if len(out[nid]) != 1:
                return False
            nid = next(iter(out[nid]))
            if nid in path or len(inc[nid]) != 1:
                return False
            path.add(nid)
        return path == nodes
    if motif in ("star_in", "star_out"):
        direction = inc if motif == "star_in" else out
        expected = {(leaf, anchor) if motif == "star_in" else (anchor, leaf) for leaf in nodes - {anchor}}
        return pairs == expected and direction[anchor] == nodes - {anchor}
    if motif in ("tree_in", "tree_out"):
        forward, reverse = (inc, out) if motif == "tree_in" else (out, inc)
        children = forward[anchor]
        if reverse[anchor] or len(children) < 2 or len(edges) != len(nodes) - 1:
            return False
        covered = {anchor} | children
        for child in children:
            if reverse[child] != {anchor} or not forward[child]:
                return False
            for leaf in forward[child]:
                if leaf in covered or reverse[leaf] != {child} or forward[leaf]:
                    return False
                covered.add(leaf)
        return covered == nodes
    if motif == "rhombus":
        if len(nodes) != 4 or len(edges) != 4 or inc[anchor] or len(out[anchor]) != 2:
            return False
        middle = out[anchor]
        sink = nodes - {anchor} - middle
        if len(sink) != 1:
            return False
        end = next(iter(sink))
        return not out[end] and inc[end] == middle and all(inc[n] == {anchor} and out[n] == {end} for n in middle)
    if motif == "hourglass":
        return len(nodes) == 5 and len(edges) == 4 and len(inc[anchor]) == len(out[anchor]) == 2 and \
            inc[anchor].isdisjoint(out[anchor]) and pairs == {(n, anchor) for n in inc[anchor]} | {(anchor, n) for n in out[anchor]}
    return False


def audit_structure(item, graph, candidate_count=25):
    """Validate graph ID/name joins, all context edges, motif and hidden oracle."""
    errors = []
    rid, variant = item.get("record_id"), item.get("variant")
    report = {"record_id": rid, "variant": variant, "scope": "private_graph_consistency_not_metadata_answerability"}
    try:
        public, private = item["public"], item["private"]
        candidates = public["candidates"]
        candidate_ids = resolve_candidate_ids(item, graph)
        names = {c["name"] for c in candidates}
        name_to_id = {c["name"]: nid for c, nid in zip(candidates, candidate_ids)}
        types = {c["name"]: c["type"] for c in candidates}
        if candidate_count is not None and len(candidate_ids) != candidate_count:
            errors.append("candidate_count")
        motif, size = item["subgraph_type"], item["size"]
        minimum = 5 if str(motif).startswith("tree_") else 3
        if type(size) is not int or size < minimum or size > 30:
            errors.append("invalid_motif_size")
        reference_ids = private["reference_ids"]
        reference_names = private["reference_names"]
        ref_ids, ref_names = set(reference_ids), set(reference_names)
        if len(reference_ids) != len(ref_ids) or len(reference_names) != len(ref_names) or len(ref_ids) != item["size"]:
            errors.append("reference_size")
        if len(reference_ids) != len(reference_names) or any(name_to_id.get(n) != nid for n, nid in zip(reference_names, reference_ids)):
            errors.append("reference_id_name_mismatch")
        answer = private["answer"]
        if set(answer["entities"]) != ref_names or len(answer["entities"]) != len(ref_names):
            errors.append("gold_entity_mismatch")
        gold = _edges(answer["relations"], errors, "invalid_gold_edges")
        context = _edges(private["context_relations"], errors, "invalid_context_edges")
        actual_context = {(graph.name(s), relation, graph.name(t)) for s, relation, t in graph.induced_edges(candidate_ids)}
        if context != actual_context:
            errors.append("context_edges_mismatch")
        actual_gold = {(graph.name(s), relation, graph.name(t)) for s, relation, t in graph.induced_edges(ref_ids)}
        if gold != actual_gold:
            errors.append("gold_induced_edges_mismatch")
        if not ref_names <= names:
            errors.append("reference_not_in_candidates")
        if private["anchor"] not in ref_names:
            errors.append("anchor_not_reference")
        type_counts = Counter(types.values())
        if any(type_counts[types.get(n)] < 2 for n in ref_names - {private["anchor"]}):
            errors.append("reference_type_unique")
        if not _topology(item["subgraph_type"], ref_names, gold, private["anchor"]):
            errors.append("directed_motif_mismatch")
        derived = _derive(private["anchor"], private["pattern"], names, context, types)
        if derived != (ref_names, gold):
            errors.append("hidden_oracle_mismatch")
        elif any(_derive(private["anchor"], private["pattern"], names - {n}, context, types) == derived for n in ref_names):
            errors.append("reference_not_graph_necessary")
        adjacent = set(private.get("adjacent_names", []))
        actual_adjacent = {n for n, nid in name_to_id.items() if nid not in ref_ids and graph.neighbours(nid) & ref_ids}
        if adjacent != actual_adjacent:
            errors.append("adjacent_declaration_mismatch")
        if variant == "disconnected" and actual_adjacent:
            errors.append("disconnected_cross_edge")
        elif variant not in VARIANTS:
            errors.append("unknown_variant")
        if graph.graph_hash is not None and item.get("graph_hash") != graph.graph_hash:
            errors.append("item_graph_hash_mismatch")
        report.update(candidate_count=len(candidate_ids), reference_count=len(ref_ids),
                      context_edge_count=len(context), gold_edge_count=len(gold))
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        errors.append("invalid_item_contract")
        report["detail"] = str(exc)
    report.update(status="ok" if not errors else "error", errors=sorted(set(errors)))
    return report
