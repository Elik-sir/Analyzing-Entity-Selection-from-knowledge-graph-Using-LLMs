"""Deterministic endpoint questions and a private graph oracle.

The oracle reasons over *all* induced candidate edges. Reference membership is
never a traversal filter. Node witnesses are graph support, not a statement
that the corresponding rendered cards are indispensable evidence.
"""

from collections import defaultdict

QUESTION_VERSION = "endpoint_questions_v1"
SCHEMA_VERSION = "kg_endpoint_task_spec_v1"


class QuestionError(ValueError):
    pass


def _value(item, key, alternative=None):
    if isinstance(item, dict):
        return item.get(key, item.get(alternative)) if alternative else item.get(key)
    return getattr(item, key, getattr(item, alternative, None)) if alternative else getattr(item, key)


def _node_type(node):
    value = node.get("type")
    if not isinstance(value, str) or not value:
        raise QuestionError("Oracle nodes require a nonempty type")
    return value


def _validate_spec(spec):
    required = {"schema_version", "question_version", "record_id", "pattern", "anchor_id",
                "anchor_type", "direction", "depth", "terminal_type", "path_policy",
                "anchor_convention", "reference_ids", "target_ids", "witness_ids",
                "reference_status", "reference_exclusion_reasons", "goal_template", "slots_template"}
    if not isinstance(spec, dict) or set(spec) != required:
        raise QuestionError("Unexpected or missing TaskSpec fields")
    if spec["schema_version"] != SCHEMA_VERSION or spec["question_version"] != QUESTION_VERSION:
        raise QuestionError("Unsupported question version")
    for key in ("record_id", "pattern", "anchor_id", "anchor_type", "goal_template", "slots_template"):
        if not isinstance(spec[key], str) or not spec[key]:
            raise QuestionError("TaskSpec requires nonempty strings")
    for key in ("reference_ids", "target_ids", "witness_ids", "reference_exclusion_reasons"):
        if (not isinstance(spec[key], list) or any(not isinstance(v, str) or not v for v in spec[key])
                or len(set(spec[key])) != len(spec[key])):
            raise QuestionError("TaskSpec requires unique string lists")
    if spec["path_policy"] != "simple_directed_routes_v1" or spec["anchor_convention"] != "named_anchor_not_required_answer":
        raise QuestionError("Unsupported traversal/anchor convention")
    if spec["reference_status"] not in {"accepted", "excluded"}:
        raise QuestionError("Invalid reference status")
    pattern = spec["pattern"]
    if pattern.startswith("path:"):
        if (spec["direction"] != "out" or spec["depth"] is not None or
                spec["terminal_type"] != pattern.split(":", 1)[1] or not spec["terminal_type"]):
            raise QuestionError("Invalid typed-terminal task")
    else:
        if pattern not in {"in:1", "out:1", "in:2", "out:2", "both:1"}:
            raise QuestionError("Unsupported task pattern")
        direction, depth = pattern.split(":")
        if spec["direction"] != direction or type(spec["depth"]) is not int or spec["depth"] != int(depth) or spec["terminal_type"] is not None:
            raise QuestionError("Invalid bounded-route task")


def _templates(direction, depth, terminal_type, anchor_type):
    anchor = anchor_type + " '{anchor_name}'"
    rule = " Consider only the provided candidates and their supported directed links. Do not revisit an entity within a route. Return the endpoint names and explain the supporting links; the named starting entity is not an additional required answer."
    if terminal_type:
        goal = (f"Starting from {anchor}, which {terminal_type} entities are reached as the first {terminal_type} on any outgoing route?")
        slots = (f"Starting from {anchor}: (1) Follow every outgoing route. (2) Stop each route at its first {terminal_type}. (3) Report all distinct {terminal_type} endpoints reached, explaining the supporting links.")
    elif direction == "both":
        goal = f"Which entities link directly to {anchor}, and which entities does it link to directly? Classify the answer into incoming and outgoing neighbors."
        slots = (f"For {anchor}: (1) Find every entity with a directed link to it. (2) Find every entity that it links to directly. (3) Report the same neighbors in incoming and outgoing groups.")
    else:
        label = "outgoing" if direction == "out" else "incoming"
        if depth == 1:
            goal = f"Which entities are the direct {label} neighbors of {anchor}?"
            slots = f"For {anchor}: (1) Follow every {label} link once. (2) Report all distinct entities reached, explaining the supporting links."
        else:
            goal = (f"Starting from {anchor}, which entities are at the ends of all routes of at most {depth} {label} links? Stop at the second link, or earlier when the route has no further permitted link.")
            slots = (f"Starting from {anchor}: (1) Follow every {label} link once. (2) From each reached entity follow every further {label} link, stopping after a total of {depth} links; retain a one-link endpoint only if no further permitted link is available. (3) Report all distinct endpoints, explaining the supporting links.")
    return goal + rule, slots + rule


def make_question_spec(item, graph):
    """Create a private endpoint spec, retaining exclusions rather than hiding them."""
    private = _value(item, "private")
    record_id = _value(item, "record_id")
    if not isinstance(private, dict) or not isinstance(record_id, str) or not record_id:
        raise QuestionError("Missing legacy private task/record ID")
    refs, names = private.get("reference_ids"), private.get("reference_names")
    if (not isinstance(refs, list) or not refs or
            any(not isinstance(v, str) or v not in graph.nodes for v in refs) or len(set(refs)) != len(refs) or
            not isinstance(names, list) or len(names) != len(refs) or
            any(not isinstance(v, str) or not v for v in names) or len(set(names)) != len(names)):
        raise QuestionError("Invalid reference nodes/names")
    if any(graph.nodes[nid]["name"] != name for nid, name in zip(refs, names)):
        raise QuestionError("Reference ID/name mismatch")
    anchor = private.get("anchor")
    if anchor not in names:
        raise QuestionError("Anchor is absent from reference nodes")
    anchor_id = refs[names.index(anchor)]
    pattern = private.get("pattern")
    if not isinstance(pattern, str) or ":" not in pattern:
        raise QuestionError("Invalid reference query pattern")
    direction, value = pattern.split(":", 1)
    terminal_type = value if direction == "path" else None
    if terminal_type:
        direction, depth = "out", None
    elif pattern in {"in:1", "out:1", "in:2", "out:2", "both:1"}:
        depth = int(value)
    else:
        raise QuestionError("Unsupported reference query pattern")
    anchor_type = _node_type(graph.nodes[anchor_id])
    goal, slots = _templates(direction, depth, terminal_type, anchor_type)
    spec = {"schema_version": SCHEMA_VERSION, "question_version": QUESTION_VERSION,
            "record_id": record_id, "pattern": pattern, "anchor_id": anchor_id,
            "anchor_type": anchor_type, "direction": direction, "depth": depth,
            "terminal_type": terminal_type, "path_policy": "simple_directed_routes_v1",
            "anchor_convention": "named_anchor_not_required_answer", "reference_ids": sorted(refs),
            "target_ids": [], "witness_ids": [], "reference_status": "accepted",
            "reference_exclusion_reasons": [], "goal_template": goal, "slots_template": slots}
    baseline = evaluate_task(spec, graph.induced_edges(refs), refs, graph.nodes)
    reasons = []
    if not baseline["answer_ids"]:
        reasons.append("no_reference_endpoint_answer")
    if set(refs) - set(baseline["witness_ids"]):
        reasons.append("reference_nodes_outside_endpoint_witnesses")
    if baseline["path_limit_reached"]:
        reasons.append("oracle_path_limit")
    spec.update(target_ids=baseline["answer_ids"], witness_ids=baseline["witness_ids"],
                reference_status="excluded" if reasons else "accepted", reference_exclusion_reasons=reasons)
    _validate_spec(spec)
    return spec


def render_question(spec, name_map, variant="goal"):
    """Render only a mapped anchor name, type and public traversal rules."""
    _validate_spec(spec)
    if variant not in {"goal", "slots"}:
        raise QuestionError("Question variant must be goal or slots")
    name = name_map.get(spec["anchor_id"])
    if isinstance(name, dict):
        name = name.get("name")
    if not isinstance(name, str) or not name.strip():
        raise QuestionError("Missing mapped anchor name")
    return spec[variant + "_template"].format(anchor_name=name)


def _minimal_support_sets(by_answer, anchor, limit):
    sets, complete = [frozenset([anchor])], True
    for answer in sorted(by_answer):
        expanded = {s | frozenset(p) for s in sets for p in by_answer[answer]}
        minimal = []
        for candidate in sorted(expanded, key=lambda s: (len(s), sorted(s))):
            if not any(other <= candidate for other in minimal):
                minimal.append(candidate)
        if len(minimal) > limit:
            complete = False
            minimal = minimal[:limit]
        sets = minimal
    return [sorted(s) for s in sets] if by_answer else [], complete


def evaluate_task(spec, edges, candidate_ids, nodes, *, max_paths=10000, max_support_sets=256):
    """Evaluate actual candidate semantics independently of private target IDs.

    Supports every simple directed route and every valid extra endpoint. The
    bounded oracle reports limits explicitly; such tasks cannot be certified.
    """
    _validate_spec(spec)
    if type(max_paths) is not int or max_paths < 1 or type(max_support_sets) is not int or max_support_sets < 1:
        raise QuestionError("Oracle limits must be positive integers")
    ids = list(candidate_ids)
    if any(not isinstance(v, str) or v not in nodes for v in ids) or len(ids) != len(set(ids)):
        raise QuestionError("Candidate IDs must be unique known node IDs")
    allowed, anchor = set(ids), spec["anchor_id"]
    outgoing, incoming = defaultdict(set), defaultdict(set)
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 3 or any(not isinstance(v, str) or not v for v in edge):
            raise QuestionError("Invalid typed edge")
        source, _, target = edge
        if source not in nodes or target not in nodes:
            raise QuestionError("Edge endpoint absent from node table")
        if source in allowed and target in allowed and source != target:
            outgoing[source].add(target)
            incoming[target].add(source)
    by_answer = defaultdict(set)
    groups = {"incoming_ids": [], "outgoing_ids": []}
    limited = False
    if anchor in allowed:
        if spec["direction"] == "both":
            groups = {"incoming_ids": sorted(incoming[anchor]), "outgoing_ids": sorted(outgoing[anchor])}
            for target in set(incoming[anchor]) | set(outgoing[anchor]):
                by_answer[target].add((anchor, target))
        else:
            adjacent = outgoing if spec["direction"] == "out" else incoming
            stack, completed_paths, expansions = [(anchor,)], 0, 0
            while stack:
                path = stack.pop()
                expansions += 1
                if expansions > max_paths * max(1, len(ids)):
                    limited = True
                    break
                current = path[-1]
                terminal = spec["terminal_type"] is not None and len(path) > 1 and _node_type(nodes[current]) == spec["terminal_type"]
                next_ids = adjacent[current] - set(path)
                bounded_end = spec["depth"] is not None and len(path) > 1 and (len(path) - 1 == spec["depth"] or not next_ids)
                if terminal or bounded_end:
                    by_answer[current].add(path)
                    completed_paths += 1
                    if completed_paths >= max_paths and stack:
                        limited = True
                        break
                elif spec["terminal_type"] is not None or len(path) - 1 < spec["depth"]:
                    for target in sorted(next_ids, reverse=True):
                        stack.append(path + (target,))
    paths = sorted({p for paths in by_answer.values() for p in paths})
    minimal, complete = _minimal_support_sets(by_answer, anchor, max_support_sets)
    return {"answer_ids": sorted(by_answer), "witness_ids": sorted({nid for p in paths for nid in p}),
            "answer_groups": groups, "support_paths": [list(p) for p in paths],
            "support_paths_by_answer": {answer: [list(p) for p in sorted(by_answer[answer])] for answer in sorted(by_answer)},
            "minimal_support_sets": minimal, "support_sets_complete": complete,
            "path_limit_reached": limited, "anchor_present": anchor in allowed}


def audit_question_support(spec, graph, candidate_ids, expected_reference_ids=None):
    """Audit matched-answer parity and alternatives without declaring card necessity."""
    _validate_spec(spec)
    refs = list(expected_reference_ids if expected_reference_ids is not None else spec["reference_ids"])
    if set(refs) != set(spec["reference_ids"]):
        raise QuestionError("Audit reference IDs differ from the TaskSpec")
    baseline = evaluate_task(spec, graph.induced_edges(refs), refs, graph.nodes)
    actual = evaluate_task(spec, graph.induced_edges(candidate_ids), candidate_ids, graph.nodes)
    expected, found = set(baseline["answer_ids"]), set(actual["answer_ids"])
    reasons = list(spec["reference_exclusion_reasons"])
    if baseline["answer_ids"] != spec["target_ids"] or baseline["witness_ids"] != spec["witness_ids"]:
        reasons.append("task_spec_reference_oracle_mismatch")
    if actual["path_limit_reached"]:
        reasons.append("oracle_path_limit")
    if found != expected or actual["answer_groups"] != baseline["answer_groups"]:
        reasons.append("candidate_context_changes_endpoint_answers")
    if set(refs) - set(candidate_ids):
        reasons.append("reference_nodes_absent_from_candidates")
    return {"schema_version": "kg_question_support_audit_v1", "record_id": spec["record_id"],
            "status": "excluded" if reasons else "accepted", "exclusion_reasons": sorted(set(reasons)),
            "expected_answer_ids": sorted(expected), "answer_ids": sorted(found),
            "extra_answer_ids": sorted(found - expected), "missing_answer_ids": sorted(expected - found),
            "witness_ids": actual["witness_ids"], "extra_witness_ids": sorted(set(actual["witness_ids"]) - set(refs)),
            "reference_nodes_outside_witnesses": sorted(set(refs) - set(baseline["witness_ids"])),
            "minimal_support_sets": actual["minimal_support_sets"],
            "support_sets_complete": actual["support_sets_complete"],
            "multiple_minimal_graph_supports": len(actual["minimal_support_sets"]) > 1 or not actual["support_sets_complete"],
            "all_reference_nodes_in_every_minimal_support": bool(actual["minimal_support_sets"]) and actual["support_sets_complete"] and all(set(refs) <= set(s) for s in actual["minimal_support_sets"]),
            "anchor_convention": spec["anchor_convention"],
            "card_indispensability": "not_established_by_graph_oracle",
            "goal_slots_same_semantics": True, "oracle": actual}
