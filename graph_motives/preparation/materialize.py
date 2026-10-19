"""Frozen local cell inputs. No models, credentials, adaptive rewrites or API calls."""

from copy import deepcopy

from .contracts import ContractError, fingerprint, reject_private
from .evidence import (
    ALIAS_VERSION,
    EVIDENCE_VERSION,
    audit_identity_leaks,
    build_matched_cards,
    reconstruct_evidence,
    serialize_kg_context,
    validate_evidence_reconstruction,
)
from .panels import resolve_candidate_ids
from .prompts import PROMPT_VERSION
from .questions import (
    QUESTION_VERSION,
    audit_question_support,
    evaluate_task,
    make_question_spec,
    render_question,
)
from .registry import CELLS

PROTOCOL_VERSION = "controlled_endpoint_selection_v1"
FORMAT_NOTES = {
    "explicit": "Each relation object is directed from source to target. Its location on a card does not reverse that direction.",
    "text": "Statements describe recorded facts in prose. Their grammatical subject and object determine the direction.",
    "keys": "A link attribute points to the candidate whose identity_token equals its value. Predicate gives the relation; tokens are experimental joining values.",
    "names+types": "Only candidate names and types are given. Descriptions and recorded links are unavailable.",
}


def build_question_variants(item, graph, names):
    spec = make_question_spec(item, graph)
    return {
        "private_spec": spec,
        "goal": render_question(spec, names, "goal"),
        "slots": render_question(spec, names, "slots"),
    }


def build_candidate_pool(item, graph, *, count=25):
    ids = resolve_candidate_ids(item, graph)
    if len(ids) != count or len(set(ids)) != count:
        raise ContractError("Candidate pool must contain 25 unique entities")
    return ids  # Frozen legacy ordering, same within paired factor conditions.


def audit_answerability(spec, graph, ids, cards, names, edges, evidence):
    """Graph witnesses and indispensable displayed evidence are different measures."""
    support = audit_question_support(spec, graph, ids)
    reconstruction = validate_evidence_reconstruction(cards, names, edges, evidence)
    baseline = evaluate_task(spec, edges, ids, graph.nodes)
    decoded = reconstruct_evidence(cards, names, evidence=evidence)
    displayed = evaluate_task(spec, decoded, ids, graph.nodes)
    if evidence == "names+types":
        return {
            "status": "closed_book_baseline",
            "support": support,
            "reconstruction": reconstruction,
            "sufficient_visible_evidence": False,
            "strict_support_eligible": False,
            "metric_scope": "graph_witness_selection; memory baseline intentionally has no edges",
        }
    sufficient = (
        baseline["answer_ids"] == displayed["answer_ids"]
        and baseline["answer_groups"] == displayed["answer_groups"]
        and not displayed["path_limit_reached"]
    )
    # Names/types remain in the public catalogue; ablation removes one card's
    # facts only. Mentioned endpoints therefore remain usable, as they are to LLMs.
    indispensable = []
    for index, card in enumerate(cards):
        if not any(
            k in card["facts"]
            for k in ("relations", "statements", "link_attributes", "identity_token")
        ):
            continue
        ablated = list(cards)
        ablated[index] = {**card, "facts": {}}
        seen = evaluate_task(
            spec, reconstruct_evidence(ablated, names, evidence=evidence), ids, graph.nodes
        )
        if (
            seen["answer_ids"] != baseline["answer_ids"]
            or seen["answer_groups"] != baseline["answer_groups"]
        ):
            indispensable.append(ids[index])
    graph_strict = support["all_reference_nodes_in_every_minimal_support"]
    card_strict = set(spec["reference_ids"]) <= set(indispensable)
    passed = sufficient and support["status"] == "accepted" and reconstruction["status"] == "passed"
    return {
        "status": "passed" if passed else "excluded",
        "support": support,
        "reconstruction": reconstruction,
        "sufficient_visible_evidence": sufficient,
        "indispensable_card_ids": sorted(indispensable),
        "redundant_reference_card_ids": sorted(set(spec["reference_ids"]) - set(indispensable)),
        "all_reference_cards_indispensable": card_strict,
        "strict_support_eligible": graph_strict and card_strict,
        "metric_scope": "graph_witness_selection; indispensable evidence measured by fact ablation",
        "ablation_policy": "remove_facts_keep_public_name_type_catalogue_v1",
        "counterfactual_scope": "single_card_ablation; not a complete enumeration of evidence-card sets",
    }


def materialize_cell(item, cell_id, graph, ledger, aliases, *, edge_index=None, audit_cache=None):
    if cell_id not in CELLS or cell_id in {"Braw", "Braw+E"}:
        raise ContractError("Controlled renderer needs a registered controlled cell")
    cell = CELLS[cell_id]
    if item["variant"] != cell.noise:
        raise ContractError("Wrong noise for cell")
    ids = build_candidate_pool(item, graph)
    names = {
        nid: aliases[nid] if cell.names == "pseudo" else graph.nodes[nid]["name"] for nid in ids
    }
    edges = sorted(graph.induced_edges(set(ids)))
    spec = make_question_spec(item, graph)
    cards = build_matched_cards(
        ledger,
        ids,
        edges,
        names,
        evidence=cell.evidence,
        location=cell.location,
        edge_index=edge_index,
    )
    question = render_question(spec, names, cell.question)
    public = serialize_kg_context(question, cards, FORMAT_NOTES[cell.evidence])
    reject_private(public)
    # Q/names do not change the decoded graph. Reuse only ablation/audit of
    # identical fact serialization topology, never a different candidate pool.
    cache_key = fingerprint(
        [
            fingerprint(item),
            ledger["ledger_sha256"],
            spec,
            ids,
            edges,
            cards,
            cell.evidence,
            cell.location,
        ]
    )
    if audit_cache is not None and cache_key in audit_cache:
        audit = deepcopy(audit_cache[cache_key])
    else:
        audit = audit_answerability(spec, graph, ids, cards, names, edges, cell.evidence)
        if audit_cache is not None:
            audit_cache[cache_key] = deepcopy(audit)
    identity = audit_identity_leaks(
        public, [graph.nodes[nid]["name"] for nid in ids] if cell.names == "pseudo" else [], ids
    )
    if cell.names == "real":
        identity["scope"] = "private graph IDs only; real names are intentional in this condition"
    eligible = audit["support"]["status"] == "accepted" and identity["status"] != "failed"
    if cell.evidence == "names+types":
        readiness = "closed_book_baseline" if eligible else "excluded"
    else:
        readiness = (
            "validated_controlled" if audit["status"] == "passed" and eligible else "excluded"
        )
    target = evaluate_task(spec, edges, ids, graph.nodes)
    row = {
        "schema_version": "kg_materialized_cell_v1",
        "record_id": item["record_id"],
        "cell_id": cell_id,
        "variant": item["variant"],
        "motif": item["subgraph_type"],
        "size": item["size"],
        "protocol_version": PROTOCOL_VERSION,
        "prompt_version": PROMPT_VERSION,
        "card_version": EVIDENCE_VERSION,
        "question_version": QUESTION_VERSION,
        "alias_version": ALIAS_VERSION if cell.names == "pseudo" else None,
        "source_item_sha256": fingerprint(item),
        "public_sha256": fingerprint(public),
        "public": public,
        "private": {
            "task_spec": spec,
            "candidate_ids": ids,
            "name_map": names,
            "graph_witness_ids": target["witness_ids"],
            "target_answer_ids": target["answer_ids"],
            "reference_answer": {
                "entities": [names[nid] for nid in target["answer_ids"]],
                "answer_groups": {
                    k: [names[nid] for nid in values]
                    for k, values in target["answer_groups"].items()
                },
            },
            "origin": "controlled_graph_derived",
            "ledger_sha256": ledger["ledger_sha256"],
        },
        "audit": {"answerability": audit, "identity": identity},
        "readiness": readiness,
    }
    row["materialized_sha256"] = fingerprint(row)
    return row


def audit_paired_conditions(rows):
    """Audit actual private factual payloads and factor differences after freezing."""
    by_cell = {r["cell_id"]: r for r in rows}
    errors = []
    pairs = [
        ("K1", "K5"),
        ("K7", "K8"),
        ("K1", "K3"),
        ("K1", "K4"),
        ("K1", "K7"),
        ("K5", "K8"),
        ("R1-matched", "K1"),
        ("R2-matched", "K2"),
        ("R0", "K0"),
        ("K5", "K5k"),
    ]
    for a, b in pairs:
        if a not in by_cell or b not in by_cell:
            continue
        left, right = by_cell[a], by_cell[b]
        for key in ("candidate_ids", "target_answer_ids", "graph_witness_ids"):
            if left["private"][key] != right["private"][key]:
                errors.append(f"{a}/{b}:{key}")
        if a in {"R1-matched", "R2-matched", "R0"}:
            inv = {
                value: right["private"]["name_map"][nid]
                for nid, value in left["private"]["name_map"].items()
            }
            from .evidence import rewrite_aliases

            if rewrite_aliases(left["public"], inv) != right["public"]:
                errors.append(f"{a}/{b}:unmatched_real_pseudo_content")
        if a in {"K1", "K5"} and b in {"K7", "K8"}:
            if left["public"]["candidates"] != right["public"]["candidates"]:
                errors.append(f"{a}/{b}:question_changes_cards")
    # A changes pools, but not the query or answers.
    for a, b in (("K1", "K2"), ("K5", "K6")):
        if a in by_cell and b in by_cell:
            if (
                by_cell[a]["private"]["target_answer_ids"]
                != by_cell[b]["private"]["target_answer_ids"]
                or by_cell[a]["public"]["question"] != by_cell[b]["public"]["question"]
            ):
                errors.append(f"{a}/{b}:noise_changes_target_question")
    return {
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "cells_checked": sorted(by_cell),
    }


def build_calibration_tasks(
    graph, ledger, aliases, *, per_operation=100, seed=20261003, edge_index=None
):
    """Microtasks from real snapshot edges, never fabricated motif fixtures."""
    operations = {
        "text_edge": "text",
        "keys_edge": "keys",
        "explicit_neighbor": "explicit",
        "text_neighbor": "text",
    }
    usable = sorted(
        nid
        for nid in ledger["nodes"]
        if nid in aliases
        and not graph.nodes[nid].get("unnamed")
        and "dup_of" not in graph.nodes[nid]
    )
    universe = set(usable)
    ordered = sorted(
        (e for e in graph.edges if e[0] in universe and e[2] in universe and e[0] != e[2]),
        key=lambda e: fingerprint(["calibration", seed, e]),
    )
    if len(ordered) < per_operation:
        raise ContractError("Insufficient real calibration edges")
    rows = []
    for operation, evidence in operations.items():
        for index, (source, relation, target) in enumerate(ordered[:per_operation]):
            ids = [source, target]
            # Extra real candidates are selected deterministically, independent of role.
            start = int(fingerprint([seed, "calibration_pool", source, target])[:8], 16) % len(
                usable
            )
            for offset in range(len(usable)):
                nid = usable[(start + offset) % len(usable)]
                if nid not in ids:
                    ids.append(nid)
                if len(ids) == 5:
                    break
            if len(ids) < 2:
                raise ContractError("Insufficient calibration candidates")
            ids.sort(key=lambda nid: fingerprint([seed, "calibration_order", source, target, nid]))
            names = {nid: aliases[nid] for nid in ids}
            edges = sorted(graph.induced_edges(set(ids)))
            cards = build_matched_cards(
                ledger,
                ids,
                edges,
                names,
                evidence=evidence,
                location="subject" if evidence == "explicit" else "none",
                edge_index=edge_index,
            )
            filtered = [
                (s, r, t)
                for s, r, t in edges
                if s == source and (operation.endswith("neighbor") or r == relation)
            ]
            relation_note = "" if operation.endswith("neighbor") else " via relation " + relation
            question = (
                "Which candidates are directly linked from '"
                + names[source]
                + "'"
                + relation_note
                + "? Return their exact names."
            )
            public = serialize_kg_context(question, cards, FORMAT_NOTES[evidence])
            decoded = reconstruct_evidence(cards, names, evidence=evidence)
            answers = sorted({names[t] for s, r, t in filtered})
            observed = sorted(
                {
                    names[t]
                    for s, r, t in decoded
                    if s == source and (operation.endswith("neighbor") or r == relation)
                }
            )
            if observed != answers:
                raise ContractError("Calibration evidence changes the answer")
            row = {
                "schema_version": "kg_calibration_task_v1",
                "record_id": f"cal:{operation}:{index}",
                "cell_id": "CAL:" + operation,
                "variant": "calibration",
                "protocol_version": "real_graph_calibration_v1",
                "prompt_version": PROMPT_VERSION,
                "card_version": EVIDENCE_VERSION,
                "question_version": "one_hop_calibration_v1",
                "alias_version": ALIAS_VERSION,
                "public_sha256": fingerprint(public),
                "operation": operation,
                "public": public,
                "private": {
                    "answer": answers,
                    "source_edge": [source, relation, target],
                    "candidate_ids": ids,
                },
                "readiness": "validated_controlled",
                "origin": "real_snapshot_microtask",
            }
            row["materialized_sha256"] = fingerprint(row)
            rows.append(row)
    return rows
