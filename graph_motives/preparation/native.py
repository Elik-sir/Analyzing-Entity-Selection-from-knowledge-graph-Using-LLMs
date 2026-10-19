"""Freeze native Braw/overlay inputs without claiming native answerability.

No endpoint-question rewrite, controlled-world substitution or provider call.
The optional explicit overlay uses every edge induced by the 25 candidates.
"""

from copy import deepcopy

from .contracts import BaseItem, ContractError, fingerprint, reject_private
from .evidence import validate_evidence_reconstruction
from .panels import resolve_candidate_ids

HIDDEN_LINK_SENTENCE = "The underlying links are hidden; use the node descriptions as evidence."
VISIBLE_LINK_SENTENCE = ("Explicit directed links are supplied on subject cards; use the node descriptions "
                         "and these links as evidence.")
OVERLAY_FORMAT_NOTE = ("facts.relations contains explicit links added from the frozen graph. Each relation "
                       "is directed from source to target, independent of the card's other metadata.")
OVERLAY_VERSION = "native_metadata_explicit_overlay_v1"


def _overlay_question(question):
    # Only replace the known literal trailing visibility instruction. An anchor
    # name or unrelated prose must not be modified by a general regex rewrite.
    if HIDDEN_LINK_SENTENCE not in question:
        return question, "unchanged_native_question_with_overlay_format_note"
    if question.count(HIDDEN_LINK_SENTENCE) != 1 or not question.endswith(HIDDEN_LINK_SENTENCE):
        raise ContractError("Ambiguous native hidden-link instruction")
    return question[:-len(HIDDEN_LINK_SENTENCE)] + VISIBLE_LINK_SENTENCE, "replace_exact_trailing_visibility_sentence"


def materialize_native_cell(item, cell_id, graph, ledger, edge_index=None):
    """Freeze a native cell; both variants await a substantive native audit.

    ``edge_index`` is accepted for the shared materialization API; overlay
    edges are read directly from the frozen graph rather than gold references.
    Source public/private fingerprints remain explicit. Original private
    evidence is retained verbatim under ``private.legacy_reference``.
    """
    if cell_id not in {"Braw", "Braw+E"}:
        raise ContractError("Native builder supports Braw and Braw+E only")
    BaseItem.from_legacy(item)
    if graph.graph_hash is not None and item["graph_hash"] != graph.graph_hash:
        raise ContractError("Native source differs from frozen graph")
    ids = resolve_candidate_ids(item, graph)
    if len(ids) != 25 or len(set(ids)) != 25:
        raise ContractError("Native pool must contain 25 unique real entities")
    if not isinstance(ledger, dict) or not isinstance(ledger.get("ledger_sha256"), str):
        raise ContractError("Native freeze requires a fingerprinted preparation ledger")
    if not set(ids) <= set(ledger.get("nodes", {})):
        raise ContractError("Native candidates are absent from preparation ledger")
    names = {nid: graph.nodes[nid]["name"] for nid in ids}
    public = deepcopy(item["public"])
    source_public_hash, source_private_hash = fingerprint(item["public"]), fingerprint(item["private"])
    mutation_policy = "exact_native_question_preserved"
    overlay = {"status": "not_applicable", "added_edge_count": 0,
               "scope": "native prose is not locally certified"}
    if cell_id == "Braw+E":
        edges = sorted(graph.induced_edges(set(ids)))
        added = {nid: [] for nid in ids}
        for source, relation, target in edges:
            added[source].append({"source": names[source], "relation": relation, "target": names[target]})
        # Native properties are never overwritten. An unexpected collision has
        # no unambiguous overlay semantics and must be handled by a new version.
        if any("relations" in card["facts"] for card in public["candidates"]):
            raise ContractError("Native facts.relations collides with overlay field")
        overlay_cards = []
        for nid, card in zip(ids, public["candidates"]):
            if added[nid]:
                card["facts"]["relations"] = deepcopy(added[nid])
            overlay_cards.append({"name": card["name"], "type": card["type"],
                                  "facts": {"relations": deepcopy(added[nid])}})
        public["question"], mutation_policy = _overlay_question(public["question"])
        if "format_note" in public:
            raise ContractError("Native format_note requires an explicit overlay migration")
        public["format_note"] = OVERLAY_FORMAT_NOTE
        reconstruction = validate_evidence_reconstruction(overlay_cards, names, edges, "explicit")
        if reconstruction["status"] != "passed":
            raise ContractError("Native graph overlay failed reconstruction")
        overlay = {"status": "passed", "added_edge_count": len(edges), "reconstruction": reconstruction,
                   "projection_policy": "all_typed_edges_induced_by_public_candidate_pool",
                   "edge_sha256": fingerprint(edges), "scope": "added explicit facts only; native prose not certified"}
    reject_private(public)
    if cell_id == "Braw" and fingerprint(public) != source_public_hash:
        raise ContractError("Braw public payload changed during freezing")
    private = {"legacy_reference": deepcopy(item["private"]), "candidate_ids": ids, "name_map": names,
               "original_question": item["public"]["question"], "original_protocol": item["protocol"],
               "origin": "native_metadata" if cell_id == "Braw" else "native_metadata+graph_overlay",
               "ledger_sha256": ledger["ledger_sha256"]}
    if fingerprint(private["legacy_reference"]) != source_private_hash:
        raise ContractError("Native private reference changed during freezing")
    row = {"schema_version": "kg_materialized_cell_v1", "record_id": item["record_id"],
           "cell_id": cell_id, "variant": item["variant"], "motif": item["subgraph_type"], "size": item["size"],
           "graph_hash": item["graph_hash"], "protocol_version": item["protocol"] if cell_id == "Braw" else OVERLAY_VERSION,
           "prompt_version": "historical_system_prompts_only" if cell_id == "Braw" else "native_overlay_prompts_pending_v1",
           "card_version": "native_metadata_original_v1" if cell_id == "Braw" else OVERLAY_VERSION,
           "question_version": "native_question_original_v1" if cell_id == "Braw" else "native_question_overlay_visibility_v1",
           "source_item_sha256": fingerprint(item), "source_public_sha256": source_public_hash,
           "source_private_sha256": source_private_hash, "public_sha256": fingerprint(public),
           "public": public, "private": private,
           "audit": {"native_answerability": {"status": "pending", "strict_support_eligible": False,
                      "scope": "native prose answerability and card necessity require substantive audit"},
                     "explicit_overlay": overlay, "question_change_policy": mutation_policy},
           "readiness": "native_audit_pending"}
    row["materialized_sha256"] = fingerprint(row)
    return row
