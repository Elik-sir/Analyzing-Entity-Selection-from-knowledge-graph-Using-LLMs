import copy
import unittest

from graph_motives.graph.graph import Graph, norm
from graph_motives.preparation.questions import (
    QuestionError,
    audit_question_support,
    evaluate_task,
    make_question_spec,
    render_question,
)


def fixture(pattern, links, *, motif="chain", node_types=None, reference_ids=None):
    graph = Graph()
    ids = {nid for source, target in links for nid in (source, target)}
    node_types = node_types or {}
    for nid in ids:
        name = "Real name " + nid
        node_type = node_types.get(nid, "Company")
        graph.nodes[nid] = {"name": name, "type": node_type, "labels": [node_type],
                            "properties": {}, "unnamed": False}
        graph.name_to_id[norm(name)] = nid
    for source, target in links:
        edge = source, "REL", target
        graph.edges.add(edge)
        graph.out[source].add(edge)
        graph.inc[target].add(edge)
    refs = list(reference_ids or sorted(ids))
    item = {"record_id": "test-record", "subgraph_type": motif,
            "private": {"anchor": graph.nodes["r"]["name"], "pattern": pattern,
                        "reference_ids": refs, "reference_names": [graph.nodes[nid]["name"] for nid in refs]}}
    return graph, item


class QuestionTests(unittest.TestCase):
    def test_all_seven_motifs_have_endpoint_goal_and_witnesses(self):
        motifs = [
            ("chain", "path:Product", [("r", "a"), ("a", "z")], {"z"}),
            ("star_out", "out:1", [("r", "a"), ("r", "b")], {"a", "b"}),
            ("star_in", "in:1", [("a", "r"), ("b", "r")], {"a", "b"}),
            ("tree_out", "out:2", [("r", "a"), ("r", "b"), ("a", "c"), ("b", "d")], {"c", "d"}),
            ("tree_in", "in:2", [("a", "r"), ("b", "r"), ("c", "a"), ("d", "b")], {"c", "d"}),
            ("rhombus", "out:2", [("r", "a"), ("r", "b"), ("a", "z"), ("b", "z")], {"z"}),
            ("hourglass", "both:1", [("a", "r"), ("b", "r"), ("r", "c"), ("r", "d")], {"a", "b", "c", "d"}),
        ]
        for motif, pattern, links, targets in motifs:
            with self.subTest(motif=motif):
                graph, item = fixture(pattern, links, motif=motif, node_types={"z": "Product"})
                spec = make_question_spec(item, graph)
                self.assertEqual(set(spec["target_ids"]), targets)
                self.assertEqual(set(spec["witness_ids"]), set(graph.nodes))
                self.assertEqual(spec["reference_status"], "accepted")
                audit = audit_question_support(spec, graph, list(graph.nodes))
                self.assertEqual(audit["status"], "accepted")
                self.assertEqual(audit["card_indispensability"], "not_established_by_graph_oracle")

    def test_goal_and_slots_only_expose_mapped_anchor_and_public_rules(self):
        graph, item = fixture("path:Product", [("r", "a"), ("a", "z")], node_types={"z": "Product"})
        spec = make_question_spec(item, graph)
        mapping = {nid: "Pseudonym " + str(i) for i, nid in enumerate(sorted(graph.nodes))}
        for variant in ("goal", "slots"):
            rendered = render_question(spec, mapping, variant)
            self.assertIn(mapping["r"], rendered)
            self.assertIn("Product", rendered)
            self.assertNotIn("Real name", rendered)
            self.assertNotIn(item["record_id"], rendered)
            self.assertNotIn("reference", rendered)
            self.assertNotIn("motif", rendered)
            self.assertNotIn("Include", rendered)
            self.assertNotIn(mapping["a"], rendered)
            self.assertNotIn(mapping["z"], rendered)
        self.assertNotEqual(render_question(spec, mapping, "goal"), render_question(spec, mapping, "slots"))
        self.assertTrue(audit_question_support(spec, graph, list(graph.nodes))["goal_slots_same_semantics"])

    def test_rhombus_parallel_routes_are_alternative_supports(self):
        graph, item = fixture("out:2", [("r", "a"), ("r", "b"), ("a", "z"), ("b", "z")], motif="rhombus")
        report = audit_question_support(make_question_spec(item, graph), graph, list(graph.nodes))
        self.assertEqual(report["minimal_support_sets"], [["a", "r", "z"], ["b", "r", "z"]])
        self.assertTrue(report["multiple_minimal_graph_supports"])
        self.assertFalse(report["all_reference_nodes_in_every_minimal_support"])

    def test_shortcut_does_not_change_target_but_does_change_necessary_support(self):
        graph, item = fixture("path:Product", [("r", "a"), ("a", "z")], node_types={"z": "Product"})
        spec = make_question_spec(item, graph)
        edge = ("r", "SHORTCUT", "z")
        graph.edges.add(edge)
        graph.out["r"].add(edge)
        graph.inc["z"].add(edge)
        actual = evaluate_task(spec, graph.edges, graph.nodes, graph.nodes)
        self.assertEqual(actual["answer_ids"], ["z"])
        self.assertEqual(actual["minimal_support_sets"], [["r", "z"]])
        self.assertIn(["r", "a", "z"], actual["support_paths"])
        self.assertFalse(audit_question_support(spec, graph, list(graph.nodes))["all_reference_nodes_in_every_minimal_support"])

    def test_adjacent_noise_valid_endpoint_is_not_ignored(self):
        graph, item = fixture("path:Product", [("r", "a"), ("a", "z"), ("r", "n"), ("n", "extra")],
                              node_types={"z": "Product", "extra": "Product"}, reference_ids=["r", "a", "z"])
        report = audit_question_support(make_question_spec(item, graph), graph, list(graph.nodes))
        self.assertEqual(report["extra_answer_ids"], ["extra"])
        self.assertEqual(report["extra_witness_ids"], ["extra", "n"])
        self.assertEqual(report["status"], "excluded")
        self.assertIn("candidate_context_changes_endpoint_answers", report["exclusion_reasons"])

    def test_first_typed_endpoint_stops_traversal(self):
        graph, item = fixture("path:Product", [("r", "a"), ("a", "z"), ("z", "extra")],
                              node_types={"z": "Product", "extra": "Product"}, reference_ids=["r", "a", "z"])
        report = audit_question_support(make_question_spec(item, graph), graph, list(graph.nodes))
        self.assertEqual(report["answer_ids"], ["z"])
        self.assertEqual(report["extra_answer_ids"], [])
        self.assertEqual(report["status"], "accepted")

    def test_mixed_depth_tree_keeps_one_link_leaf_endpoint(self):
        graph, item = fixture("out:2", [("r", "a"), ("r", "b"), ("a", "z")], motif="tree_out")
        spec = make_question_spec(item, graph)
        self.assertEqual(set(spec["target_ids"]), {"b", "z"})
        self.assertEqual(set(spec["witness_ids"]), set(graph.nodes))
        self.assertEqual(spec["reference_status"], "accepted")

    def test_irrelevant_reference_branch_is_explicitly_excluded(self):
        graph, item = fixture("path:Product", [("r", "a"), ("a", "z"), ("r", "unused")], node_types={"z": "Product"})
        spec = make_question_spec(item, graph)
        self.assertEqual(spec["reference_status"], "excluded")
        self.assertIn("reference_nodes_outside_endpoint_witnesses", spec["reference_exclusion_reasons"])

    def test_hourglass_reports_direction_groups(self):
        graph, item = fixture("both:1", [("a", "r"), ("r", "b")], motif="hourglass")
        spec = make_question_spec(item, graph)
        actual = evaluate_task(spec, graph.edges, graph.nodes, graph.nodes)
        self.assertEqual(actual["answer_groups"], {"incoming_ids": ["a"], "outgoing_ids": ["b"]})

    def test_no_gold_filter_or_target_cheating(self):
        graph, item = fixture("out:1", [("r", "a"), ("r", "extra")], motif="star_out", reference_ids=["r", "a"])
        spec = make_question_spec(item, graph)
        spec["target_ids"] = ["fabricated-private-gold"]
        spec["witness_ids"] = ["fabricated-private-gold"]
        actual = evaluate_task(spec, graph.edges, graph.nodes, graph.nodes)
        self.assertEqual(actual["answer_ids"], ["a", "extra"])

    def test_oracle_limit_is_never_silently_certified(self):
        graph, item = fixture("out:1", [("r", "a"), ("r", "b")], motif="star_out")
        spec = make_question_spec(item, graph)
        actual = evaluate_task(spec, graph.edges, graph.nodes, graph.nodes, max_paths=1)
        self.assertTrue(actual["path_limit_reached"])

    def test_strict_versions_and_shapes_and_unknown_nodes(self):
        graph, item = fixture("out:1", [("r", "a")])
        spec = make_question_spec(item, graph)
        for mutation in ({"question_version": "unknown"}, {"private_extra": True}, {"depth": True}):
            changed = {**spec, **mutation}
            with self.assertRaises(QuestionError):
                evaluate_task(changed, graph.edges, graph.nodes, graph.nodes)
        with self.assertRaises(QuestionError):
            render_question(spec, {"r": "Name"}, "unversioned")
        with self.assertRaises(QuestionError):
            render_question(spec, {})
        with self.assertRaises(QuestionError):
            evaluate_task(spec, graph.edges, ["r", "unknown"], graph.nodes)
        changed_item = copy.deepcopy(item)
        changed_item["private"]["reference_names"][0] = "mismatched"
        with self.assertRaises(QuestionError):
            make_question_spec(changed_item, graph)

    def test_disconnected_edges_do_not_create_answers(self):
        graph, item = fixture("out:1", [("r", "a"), ("n", "extra")], reference_ids=["r", "a"])
        audit = audit_question_support(make_question_spec(item, graph), graph, list(graph.nodes))
        self.assertEqual(audit["answer_ids"], ["a"])
        self.assertEqual(audit["status"], "accepted")

    def test_missing_anchor_card_is_not_implicitly_a_gold_requirement(self):
        graph, item = fixture("out:1", [("r", "a")])
        spec = make_question_spec(item, graph)
        self.assertEqual(spec["anchor_convention"], "named_anchor_not_required_answer")
        # Graph nodes are known in the named public world; root separately tests
        # evidence-card ablations by removing facts rather than graph identities.
        self.assertEqual(evaluate_task(spec, graph.edges, graph.nodes, graph.nodes)["answer_ids"], ["a"])
        actual = evaluate_task(spec, graph.edges, ["a"], graph.nodes)
        self.assertFalse(actual["anchor_present"])
        self.assertEqual(actual["answer_ids"], [])


if __name__ == "__main__":
    unittest.main()
