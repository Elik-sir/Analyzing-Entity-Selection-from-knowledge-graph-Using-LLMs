"""Independent preparation integration and scientific-confound regressions."""

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from graph_motives.graph.graph import load_snapshot
from graph_motives.preparation.contracts import ContractError, fingerprint
from graph_motives.preparation.evidence import (
    build_fact_ledger,
    build_pseudonym_map,
    reconstruct_evidence,
    render_matched_cards,
)
from graph_motives.preparation.materialize import (
    audit_paired_conditions,
    build_calibration_tasks,
    materialize_cell,
)
from graph_motives.preparation.prompts import build_request


class PreparationReviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "graph.jsonl"
        self.refs = ["private-node-A", "private-node-B", "private-node-C"]
        self.decoys = [f"private-decoy-{i:02d}" for i in range(22)]
        self.pool = self.refs + self.decoys
        self.extra = "private-extra-endpoint"
        self.edges = [(self.refs[0], "LINK", self.refs[1]), (self.refs[1], "LINK", self.refs[2]),
                      (self.decoys[0], "LINK", self.decoys[1]), (self.refs[0], "LINK", self.extra)]
        nodes = [{"kind": "node", "id": nid, "labels": ["Company"],
                  "properties": {"name": f"OriginalEntity{index:02d}", "ticker": f"NATIVE_TICKER_{index}",
                                 "description": "Native descriptive metadata must remain unchanged"}}
                 for index, nid in enumerate(self.pool + [self.extra])]
        rows = nodes + [{"kind": "relationship", "source": s, "relation": r, "target": t} for s, r, t in self.edges]
        self.path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
        self.source_bytes = self.path.read_bytes()
        self.graph = load_snapshot(self.path)
        self.ledger = build_fact_ledger(self.graph)
        self.aliases = build_pseudonym_map(self.graph.nodes)
        self.item = self.make_item(self.pool)

    def make_item(self, pool, variant="disconnected"):
        graph = self.graph
        def named_edges(ids):
            return [[graph.name(s), r, graph.name(t)] for s, r, t in sorted(graph.induced_edges(ids))]
        reference_names = [graph.name(nid) for nid in self.refs]
        return {"record_id": "source-record", "variant": variant, "subgraph_type": "chain", "size": 3,
                "protocol": "nodes_only_text_answer_v2", "graph_hash": graph.graph_hash,
                "public": {"question": "Legacy question", "candidates": [
                    {"name": graph.name(nid), "type": graph.type(nid), "facts": deepcopy(graph.nodes[nid]["properties"])} for nid in pool]},
                "private": {"anchor": reference_names[0], "pattern": "out:2", "reference_ids": list(self.refs),
                            "reference_names": reference_names, "answer": {"entities": reference_names,
                            "relations": named_edges(self.refs)}, "context_relations": named_edges(pool),
                            "adjacent_names": []}}

    def materialize(self, cell, item=None, cache=None):
        return materialize_cell(self.item if item is None else item, cell, self.graph,
                                self.ledger, self.aliases, audit_cache=cache)

    def test_controlled_evidence_keeps_decoy_edges_and_omits_out_of_pool_edges(self):
        row = self.materialize("K1")
        decoded = reconstruct_evidence(row["public"]["candidates"], row["private"]["name_map"], evidence="explicit")
        expected = self.graph.induced_edges(self.pool)
        self.assertEqual(decoded, expected)
        self.assertIn((self.decoys[0], "LINK", self.decoys[1]), decoded)
        self.assertNotIn((self.refs[0], "LINK", self.extra), decoded)
        self.assertNotIn(self.aliases[self.extra], json.dumps(row["public"]))

    def test_renderer_rejects_invented_fact_and_out_of_pool_fact(self):
        names = {nid: self.aliases[nid] for nid in self.pool}
        with self.assertRaisesRegex(ContractError, "absent from the frozen ledger"):
            render_matched_cards(self.ledger, self.pool, [(self.refs[0], "LINK", self.refs[2])], names)
        with self.assertRaisesRegex(ContractError, "Out-of-pool"):
            render_matched_cards(self.ledger, self.pool, [(self.refs[0], "LINK", self.extra)], names)

    def test_factor_cells_preserve_candidate_pool_and_order_and_detect_tampering(self):
        cells = ("R0", "K0", "R1-matched", "K1", "K3", "K4", "K5", "K7", "K8", "K5k")
        rows = [self.materialize(cell) for cell in cells]
        for row in rows:
            self.assertEqual(row["private"]["candidate_ids"], self.pool)
            self.assertEqual(row["private"]["target_answer_ids"], [self.refs[-1]])
            self.assertEqual(row["readiness"], "closed_book_baseline" if row["cell_id"] in {"R0", "K0"} else "validated_controlled")
        self.assertEqual(audit_paired_conditions(rows)["status"], "passed")
        corrupted = deepcopy(rows)
        next(row for row in corrupted if row["cell_id"] == "K5")["private"]["candidate_ids"].reverse()
        self.assertEqual(audit_paired_conditions(corrupted)["status"], "failed")

    def test_pseudonyms_are_injective_and_materialization_preserves_sources(self):
        source_item = fingerprint(self.item)
        graph_hash = self.graph.fingerprint()
        ledger_hash = fingerprint(self.ledger)
        self.assertEqual(len(set(self.aliases.values())), len(self.graph.nodes))
        row = self.materialize("K8")
        public_text = json.dumps(row["public"])
        for nid, node in self.graph.nodes.items():
            self.assertNotIn(nid, public_text)
            self.assertNotIn(node["name"], public_text)
            self.assertNotIn(node["properties"]["ticker"], public_text)
        self.assertEqual(self.path.read_bytes(), self.source_bytes)
        self.assertEqual(fingerprint(self.item), source_item)
        self.assertEqual(self.graph.fingerprint(), graph_hash)
        self.assertEqual(fingerprint(self.ledger), ledger_hash)

    def test_names_types_baseline_has_no_graph_evidence(self):
        row = self.materialize("K0")
        self.assertTrue(all(not card["facts"] for card in row["public"]["candidates"]))
        decoded = reconstruct_evidence(row["public"]["candidates"], row["private"]["name_map"], evidence="names+types")
        self.assertEqual(decoded, set())
        self.assertFalse(row["audit"]["answerability"]["sufficient_visible_evidence"])

    def test_sufficient_serialization_does_not_imply_every_reference_card_is_needed(self):
        subject = self.materialize("K1")["audit"]["answerability"]
        object_host = self.materialize("K3")["audit"]["answerability"]
        keys = self.materialize("K5k")["audit"]["answerability"]
        self.assertTrue(subject["sufficient_visible_evidence"])
        self.assertNotIn(self.refs[2], subject["indispensable_card_ids"])
        self.assertFalse(subject["all_reference_cards_indispensable"])
        self.assertTrue(object_host["sufficient_visible_evidence"])
        self.assertNotIn(self.refs[0], object_host["indispensable_card_ids"])
        self.assertEqual(keys["indispensable_card_ids"], sorted(self.refs))
        self.assertTrue(keys["strict_support_eligible"])

    def test_solver_request_accepts_materialized_protocol_and_excludes_private_data(self):
        row = self.materialize("K7")
        request = build_request(row, {"alias": "fixture-model", "provider": "mock", "provider_model": "fixture/model"},
                                "dataset-fixture", "allocation-fixture")
        payload = json.loads(request.user_prompt)
        self.assertEqual(payload, row["public"])
        for forbidden in ("private", "task_spec", "target_answer_ids", "graph_witness_ids", "source_item_sha256", "materialized_sha256"):
            self.assertNotIn(forbidden, payload)
        for nid in self.pool:
            self.assertNotIn(nid, request.user_prompt)

    def test_answerability_cache_cannot_cross_changed_candidate_pool(self):
        original = self.make_item(self.pool, variant="adjacent")
        changed_pool = self.pool[:-1] + [self.extra]
        changed = self.make_item(changed_pool, variant="adjacent")
        expected_original = self.materialize("K2", original)
        expected_changed = self.materialize("K2", changed)
        self.assertEqual(expected_original["readiness"], "validated_controlled")
        self.assertEqual(expected_changed["readiness"], "excluded")
        cache = {}
        self.materialize("K2", original, cache)
        observed = self.materialize("K2", changed, cache)
        self.assertEqual(observed["audit"]["answerability"], expected_changed["audit"]["answerability"])
        self.assertEqual(observed["readiness"], expected_changed["readiness"])

    def test_calibration_uses_ledger_universe_matched_pools_and_shuffled_roles(self):
        ledger = build_fact_ledger(self.graph, self.pool)
        rows = build_calibration_tasks(self.graph, ledger, self.aliases, per_operation=3)
        self.assertEqual(len(rows), 12)
        reference_order = {}
        role_positions = []
        for row in rows:
            ids = row["private"]["candidate_ids"]
            source, _, target = row["private"]["source_edge"]
            self.assertNotIn(self.extra, ids)
            self.assertIn(source, ids)
            self.assertIn(target, ids)
            self.assertEqual(len(ids), 5)
            source_edge = tuple(row["private"]["source_edge"])
            reference_order.setdefault(source_edge, ids)
            self.assertEqual(reference_order[source_edge], ids)
            role_positions.append((ids.index(source), ids.index(target)))
            request = build_request(row, {"alias": "fixture-model", "provider": "mock", "provider_model": "fixture/model"},
                                    "dataset-fixture", "allocation-fixture", stage="calibration")
            self.assertEqual(request.request_type, "calibration")
            self.assertNotIn("source_edge", request.user_prompt)
            self.assertNotIn("private", json.loads(request.user_prompt))
        self.assertGreater(len(set(role_positions)), 1)


if __name__ == "__main__":
    unittest.main()
