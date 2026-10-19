"""Scientific panel and graph consistency failures must be detected locally."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from graph_motives.graph.graph import load_snapshot, recompute_graph_fingerprint
from graph_motives.preparation.panels import (
    audit_pairing,
    audit_structure,
    build_comparison_panel,
    build_pilot_panel,
    build_size_panel,
    resolve_candidate_ids,
)


class PanelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "graph.jsonl"

    def graph(self, edges, names=("A", "B", "C", "D", "E", "Decoy")):
        nodes = [{"kind": "node", "id": name, "labels": ["Company"],
                  "properties": {"name": name}} for name in names]
        records = nodes + [{"kind": "relationship", "source": s, "relation": r, "target": t} for s, r, t in edges]
        self.path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
        return load_snapshot(self.path)

    def item(self, graph, motif="chain", refs=("A", "B", "C"), pattern="out:2", anchor="A", rid="record"):
        candidates = [{"name": n["name"], "type": n["type"], "facts": {"name": n["name"]}}
                      for n in graph.nodes.values() if "dup_of" not in n and not n["unnamed"]]
        def edge_names(ids):
            return [list(e) for e in sorted(graph.induced_edges(ids))]
        return {"record_id": rid, "variant": "disconnected", "size": len(refs), "subgraph_type": motif,
                "protocol": "nodes_only_text_answer_v2", "graph_hash": graph.graph_hash,
                "public": {"question": "Follow the requested links from A", "candidates": candidates},
                "private": {"anchor": anchor, "pattern": pattern, "reference_ids": list(refs), "reference_names": list(refs),
                            "answer": {"entities": list(refs), "relations": edge_names(refs)},
                            "context_relations": edge_names(graph.nodes), "adjacent_names": []}}

    def pair(self, item):
        adjacent = copy.deepcopy(item)
        adjacent["variant"] = "adjacent"
        return [item, adjacent]

    def test_semantic_identity_uses_properties_labels_and_directed_edges(self):
        graph = self.graph({("A", "R", "B"), ("B", "S", "C")})
        self.assertEqual(recompute_graph_fingerprint(graph, graph.graph_hash)["status"], "ok")
        graph.nodes["A"]["properties"]["description"] = "changed"
        self.assertEqual(recompute_graph_fingerprint(graph, graph.graph_hash)["errors"], ["graph_hash_mismatch"])

    def test_normalization_retains_duplicate_marker_excludes_unusable_candidates(self):
        records = [{"kind": "node", "id": "a", "labels": ["Searchable", "News", "Company"], "properties": {"name": " A  name "}},
                   {"kind": "node", "id": "b", "labels": ["Company"], "properties": {"name": "a name"}},
                   {"kind": "node", "id": "c", "labels": ["Company"], "properties": {}}]
        self.path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
        graph = load_snapshot(self.path)
        self.assertEqual(graph.nodes["a"]["name"], "A name")
        self.assertEqual(graph.nodes["a"]["type"], "Company")
        self.assertEqual(graph.nodes["b"]["dup_of"], "a")
        self.assertEqual(graph.name_to_id, {"a name": "a"})

    def test_dangling_snapshot_edge_fails_ingestion(self):
        with self.assertRaisesRegex(ValueError, "Dangling edge"):
            self.graph({("A", "R", "missing")})

    def test_candidate_unknown_duplicate_and_wrong_type_are_rejected(self):
        graph = self.graph({("A", "R", "B"), ("B", "S", "C")})
        item = self.item(graph)
        item["public"]["candidates"][0]["name"] = "unknown"
        with self.assertRaisesRegex(ValueError, "usable snapshot"):
            resolve_candidate_ids(item, graph)
        item = self.item(graph)
        item["public"]["candidates"].append(copy.deepcopy(item["public"]["candidates"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate candidate"):
            resolve_candidate_ids(item, graph)
        item = self.item(graph)
        item["public"]["candidates"][0]["type"] = "City"
        with self.assertRaisesRegex(ValueError, "type differs"):
            resolve_candidate_ids(item, graph)

    def test_structural_audit_detects_context_omission_gold_edge_and_id_join(self):
        graph = self.graph({("A", "R", "B"), ("B", "S", "C")})
        item = self.item(graph)
        self.assertEqual(audit_structure(item, graph, candidate_count=None)["errors"], [])
        item["private"]["context_relations"].pop()
        self.assertIn("context_edges_mismatch", audit_structure(item, graph, candidate_count=None)["errors"])
        item = self.item(graph)
        item["private"]["answer"]["relations"][0][1] = "WRONG"
        self.assertIn("gold_induced_edges_mismatch", audit_structure(item, graph, candidate_count=None)["errors"])
        item = self.item(graph)
        item["private"]["reference_ids"][0] = "Decoy"
        self.assertIn("reference_id_name_mismatch", audit_structure(item, graph, candidate_count=None)["errors"])

    def test_directional_motifs_and_parallel_edges_do_not_pass_as_undirected(self):
        graph = self.graph({("B", "R", "A"), ("C", "R", "A")})
        item = self.item(graph, motif="star_in", pattern="in:1")
        self.assertEqual(audit_structure(item, graph, candidate_count=None)["errors"], [])
        item["subgraph_type"] = "star_out"
        self.assertIn("directed_motif_mismatch", audit_structure(item, graph, candidate_count=None)["errors"])
        graph = self.graph({("A", "R", "B"), ("A", "EXTRA", "B"), ("B", "R", "C")})
        self.assertIn("directed_motif_mismatch", audit_structure(self.item(graph), graph, candidate_count=None)["errors"])

    def test_exact_rhombus_hourglass_and_two_level_tree(self):
        fixtures = [
            ("rhombus", {("A", "R", "B"), ("A", "R", "C"), ("B", "R", "D"), ("C", "R", "D")}, ("A", "B", "C", "D"), "out:2", "A"),
            ("hourglass", {("A", "R", "C"), ("B", "R", "C"), ("C", "R", "D"), ("C", "R", "E")}, ("A", "B", "C", "D", "E"), "both:1", "C"),
            ("tree_out", {("A", "R", "B"), ("A", "R", "C"), ("B", "R", "D"), ("C", "R", "E")}, ("A", "B", "C", "D", "E"), "out:2", "A"),
            ("tree_in", {("B", "R", "A"), ("C", "R", "A"), ("D", "R", "B"), ("E", "R", "C")}, ("A", "B", "C", "D", "E"), "in:2", "A"),
        ]
        for motif, edges, refs, pattern, anchor in fixtures:
            with self.subTest(motif=motif):
                graph = self.graph(edges)
                item = self.item(graph, motif, refs, pattern, anchor)
                self.assertEqual(audit_structure(item, graph, candidate_count=None)["errors"], [])
                item["subgraph_type"] = "chain"
                self.assertIn("directed_motif_mismatch", audit_structure(item, graph, candidate_count=None)["errors"])

    def test_adjacent_noise_and_hidden_oracle_change_are_detected(self):
        graph = self.graph({("A", "R", "B"), ("B", "R", "C"), ("A", "R", "Decoy")})
        item = self.item(graph)
        errors = audit_structure(item, graph, candidate_count=None)["errors"]
        self.assertIn("hidden_oracle_mismatch", errors)
        self.assertIn("disconnected_cross_edge", errors)
        self.assertIn("adjacent_declaration_mismatch", errors)

    def test_invalid_motif_size_and_unique_reference_type_shortcut_fail(self):
        graph = self.graph({("A", "R", "B")})
        item = self.item(graph, refs=("A", "B"), pattern="out:1")
        self.assertIn("invalid_motif_size", audit_structure(item, graph, candidate_count=None)["errors"])
        self.graph({("A", "R", "B"), ("B", "R", "C")})
        records = [json.loads(line) for line in self.path.read_text().splitlines()]
        for row in records:
            if row.get("kind") == "node" and row["id"] == "C":
                row["labels"] = ["City"]
        self.path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
        graph = load_snapshot(self.path)
        item = self.item(graph)
        self.assertIn("reference_type_unique", audit_structure(item, graph, candidate_count=None)["errors"])

    def test_paired_selection_is_order_independent_and_keeps_both_variants(self):
        graph = self.graph({("A", "R", "B"), ("B", "R", "C")})
        rows = sum((self.pair(self.item(graph, rid=f"record-{i}")) for i in range(10)), [])
        first = build_comparison_panel(rows, per_cell=3, core_sizes={"chain": 3})
        second = build_comparison_panel(list(reversed(rows)), per_cell=3, core_sizes={"chain": 3})
        self.assertEqual(first, second)
        self.assertEqual(len(first), 6)
        self.assertEqual(audit_pairing(first)["errors"], [])
        self.assertEqual({r["record_id"] for r in first if r["variant"] == "adjacent"},
                         {r["record_id"] for r in first if r["variant"] == "disconnected"})
        first[0]["public"]["question"] = "changed copy"
        self.assertNotEqual(rows[0]["public"]["question"], "changed copy")

    def test_pair_gold_question_mismatch_and_unpaired_inputs_fail(self):
        graph = self.graph({("A", "R", "B"), ("B", "R", "C")})
        rows = self.pair(self.item(graph))
        rows[1]["public"]["question"] = "Changed goal"
        self.assertIn("pair_question_mismatch", audit_pairing(rows)["error_counts"])
        with self.assertRaisesRegex(ValueError, "Invalid paired input"):
            build_comparison_panel(rows, per_cell=1, core_sizes={"chain": 3})
        rows = self.pair(self.item(graph))
        rows[1]["private"]["reference_ids"][0] = "Decoy"
        self.assertIn("pair_gold_mismatch", audit_pairing(rows)["error_counts"])
        self.assertIn("unpaired_variant", audit_pairing(rows[:1])["error_counts"])

    def test_size_panel_excludes_core_and_pilot_never_reassigns_main(self):
        graph = self.graph({("A", "R", "B"), ("B", "R", "C")})
        rows = self.pair(self.item(graph))
        self.assertEqual(build_size_panel(rows, sizes={"chain": [3]}, core_sizes={"chain": 3}), [])
        report = build_pilot_panel(rows, excluded_ids={"record"}, per_cell=1, core_sizes={"chain": 3})
        self.assertEqual(report["status"], "insufficient_heldout")
        self.assertEqual(report["rows"], [])
        self.assertEqual(report["shortages"][0]["available"], 0)
        self.assertEqual(build_pilot_panel(rows, excluded_ids=set(), per_cell=1, core_sizes={"chain": 3})["status"], "ok")


if __name__ == "__main__":
    unittest.main()
