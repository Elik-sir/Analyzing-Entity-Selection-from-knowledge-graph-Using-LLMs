"""Native freezing must preserve source evidence and retain noisy overlay edges."""

import unittest
from copy import deepcopy

from graph_motives.graph.graph import Graph, norm
from graph_motives.preparation.contracts import ContractError, fingerprint
from graph_motives.preparation.evidence import build_fact_ledger, reconstruct_evidence
from graph_motives.preparation.native import (
    HIDDEN_LINK_SENTENCE,
    VISIBLE_LINK_SENTENCE,
    materialize_native_cell,
)
from graph_motives.preparation.prompts import build_request


class NativeTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.graph.graph_hash = "native-graph"
        for index in range(25):
            nid, name = f"id-{index}", f"Entity {index}"
            self.graph.nodes[nid] = {"name": name, "type": "Company", "properties": {"name": name}, "labels": ["Company"]}
            self.graph.name_to_id[norm(name)] = nid
        # The last three are distractors. Their links must survive overlay.
        for edge in [("id-0", "PRODUCES", "id-1"), ("id-1", "REQUIRES", "id-2"),
                     ("id-22", "OWNS", "id-23"), ("id-23", "LOCATED_IN", "id-24")]:
            self.graph.edges.add(edge)
            self.graph.out[edge[0]].add(edge)
            self.graph.inc[edge[2]].add(edge)
        self.ledger = build_fact_ledger(self.graph)
        self.item = {"record_id": "native-pair", "variant": "adjacent", "subgraph_type": "chain", "size": 3,
                     "graph_hash": "native-graph", "protocol": "nodes_only_text_answer_v2",
                     "public": {"question": "Starting from Entity 0, explain the links. " + HIDDEN_LINK_SENTENCE,
                                "candidates": [{"name": f"Entity {i}", "type": "Company", "labels": ["Company"],
                                                "facts": {"description": f"Native property {i}", "ticker": f"TK{i}"}} for i in range(25)]},
                     "private": {"anchor": "Entity 0", "pattern": "out:2", "reference_ids": ["id-0", "id-1", "id-2"],
                                 "reference_names": ["Entity 0", "Entity 1", "Entity 2"],
                                 "answer": {"entities": ["Entity 2"]}, "context_relations": [["Entity 0", "PRODUCES", "Entity 1"]]}}

    def render(self, cell="Braw"):
        return materialize_native_cell(self.item, cell, self.graph, self.ledger)

    def test_braw_preserves_exact_public_and_private_reference(self):
        before = deepcopy(self.item)
        row = self.render()
        self.assertEqual(row["public"], self.item["public"])
        self.assertEqual(row["private"]["legacy_reference"], self.item["private"])
        self.assertEqual(row["source_item_sha256"], fingerprint(self.item))
        self.assertEqual(row["source_public_sha256"], row["public_sha256"])
        self.assertEqual(row["source_private_sha256"], fingerprint(self.item["private"]))
        self.assertEqual(row["protocol_version"], self.item["protocol"])
        self.assertEqual(self.item, before)
        row["public"]["candidates"][0]["facts"]["description"] = "mutated copy"
        self.assertEqual(self.item, before)

    def test_overlay_retains_every_candidate_edge_including_distractors(self):
        row = self.render("Braw+E")
        self.assertEqual(row["audit"]["explicit_overlay"]["added_edge_count"], 4)
        edges = reconstruct_evidence(row["public"]["candidates"], row["private"]["name_map"], evidence="explicit")
        self.assertEqual(edges, self.graph.edges)
        self.assertIn(("id-22", "OWNS", "id-23"), edges)

    def test_overlay_retains_native_metadata_and_only_changes_visibility_sentence(self):
        original = deepcopy(self.item)
        row = self.render("Braw+E")
        for old, new in zip(self.item["public"]["candidates"], row["public"]["candidates"]):
            self.assertEqual({k: v for k, v in new["facts"].items() if k != "relations"}, old["facts"])
        self.assertEqual(row["public"]["question"], self.item["public"]["question"].replace(HIDDEN_LINK_SENTENCE, VISIBLE_LINK_SENTENCE))
        self.assertEqual(row["private"]["original_question"], self.item["public"]["question"])
        self.assertEqual(row["private"]["legacy_reference"], self.item["private"])
        self.assertEqual(self.item, original)
        self.assertNotEqual(row["source_public_sha256"], row["public_sha256"])

    def test_no_local_native_answerability_claim_and_not_controlled_runnable(self):
        for cell in ("Braw", "Braw+E"):
            row = self.render(cell)
            self.assertEqual(row["readiness"], "native_audit_pending")
            self.assertEqual(row["audit"]["native_answerability"]["status"], "pending")
            self.assertFalse(row["audit"]["native_answerability"]["strict_support_eligible"])
            with self.assertRaises(ContractError):
                build_request(row, {"alias": "test", "provider": "mock", "provider_model": "test"}, "dataset", "allocation")

    def test_overlay_field_collision_fails_without_overwriting(self):
        self.item["public"]["candidates"][0]["facts"]["relations"] = "native field"
        before = deepcopy(self.item)
        with self.assertRaises(ContractError):
            self.render("Braw+E")
        self.assertEqual(self.item, before)
        self.assertEqual(self.render("Braw")["public"], self.item["public"])

    def test_ambiguous_hidden_link_instruction_fails(self):
        self.item["public"]["question"] = HIDDEN_LINK_SENTENCE + " More text."
        with self.assertRaises(ContractError):
            self.render("Braw+E")

    def test_question_without_hidden_instruction_preserved(self):
        self.item["public"]["question"] = "Original question in another format."
        row = self.render("Braw+E")
        self.assertEqual(row["public"]["question"], self.item["public"]["question"])
        self.assertIn("format_note", row["public"])

    def test_wrong_snapshot_and_pool_size_fail(self):
        self.item["graph_hash"] = "another-graph"
        with self.assertRaises(ContractError):
            self.render()
        self.item["graph_hash"] = "native-graph"
        self.item["public"]["candidates"].pop()
        with self.assertRaises(ContractError):
            self.render()

    def test_reproducible_materialized_hash(self):
        for cell in ("Braw", "Braw+E"):
            a, b = self.render(cell), self.render(cell)
            self.assertEqual(a["materialized_sha256"], b["materialized_sha256"])
            self.assertEqual(a["materialized_sha256"], fingerprint({k: v for k, v in a.items() if k != "materialized_sha256"}))

    def test_unknown_cell_and_unresolved_candidate_fail(self):
        with self.assertRaises(ContractError):
            self.render("K1")
        self.item["public"]["candidates"][-1]["name"] = "Unknown snapshot name"
        with self.assertRaises(ValueError):
            self.render()


if __name__ == "__main__":
    unittest.main()
