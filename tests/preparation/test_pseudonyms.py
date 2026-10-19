"""Readable alias boundaries, deterministic collision recovery and frozen reuse."""

import json
import re
import unittest
from copy import deepcopy
from unittest.mock import patch

from graph_motives.preparation import evidence
from graph_motives.preparation.contracts import ContractError, fingerprint
from graph_motives.preparation.materialize import audit_paired_conditions
from tests.preparation import (
    test_preparation_review as preparation_fixture,
)

ALIAS_PATTERN = re.compile(r"[BDFGKLMNPRSTVZ][aeiou](?:[bdfgklmnprstvz][aeiou]){3}\Z")


class PseudonymTests(unittest.TestCase):
    def test_readable_aliases_are_sorted_deterministic_and_seeded(self):
        ids = [f"private-node-{index:04d}" for index in range(200)]
        names = evidence.build_pseudonym_map(ids)
        reordered = evidence.build_pseudonym_map(reversed(ids))
        duplicated = evidence.build_pseudonym_map(ids + ids[:10])
        self.assertEqual(evidence.ALIAS_VERSION, "pronounceable_alias_v2")
        self.assertEqual(names, reordered)
        self.assertEqual(names, duplicated)
        self.assertEqual(list(names), sorted(ids))
        self.assertNotEqual(names, evidence.build_pseudonym_map(ids, seed=20261004))
        self.assertEqual(len(set(names.values())), len(ids))
        self.assertGreater(len({name[:2] for name in names.values()}), 1)
        for name in names.values():
            self.assertRegex(name, ALIAS_PATTERN)
            self.assertTrue(name.isascii())
            self.assertTrue(name.istitle())
            self.assertNotIn("Velora", name)
            self.assertNotIn("private", name.casefold())
            self.assertFalse(any(character.isdigit() for character in name))
        public_names = list(names.values())
        for index, left in enumerate(public_names):
            for right in public_names[index + 1 :]:
                self.assertGreater(sum(a != b for a, b in zip(left, right)), 1)

    def test_exact_collisions_retry_without_numeric_suffixes(self):
        candidates = {
            ("first-id", 0): "Babebibo",
            ("second-id", 0): "Babebibo",
            ("second-id", 1): "Dadokufe",
        }
        with patch.object(
            evidence,
            "_pseudonym_candidate",
            side_effect=lambda nid, seed, attempt: candidates[nid, attempt],
        ) as generate:
            names = evidence.build_pseudonym_map(["second-id", "first-id"])
        self.assertEqual(names, {"first-id": "Babebibo", "second-id": "Dadokufe"})
        self.assertEqual([call.args[2] for call in generate.call_args_list], [0, 0, 1])
        for name in names.values():
            self.assertRegex(name, ALIAS_PATTERN)

    def test_one_character_near_aliases_retry(self):
        # Different but easily confused names must not survive the collision gate.
        with patch.object(
            evidence, "_pseudonym_candidate", side_effect=["Babebibo", "Babetibo", "Gamiloru"]
        ):
            names = evidence.build_pseudonym_map(["first-id", "second-id"])
        self.assertEqual(names, {"first-id": "Babebibo", "second-id": "Gamiloru"})

    def test_real_names_private_ids_and_reserved_words_are_blocked_case_insensitively(self):
        cases = [
            (["private-id"], ["  bAbEbIbO \t"], "Babebibo"),
            (["babebibo"], [], "Babebibo"),
            (["private-id"], [], "Anchor"),
        ]
        for ids, forbidden, blocked in cases:
            with self.subTest(blocked=blocked, forbidden=forbidden):
                with patch.object(
                    evidence, "_pseudonym_candidate", side_effect=[blocked, "Dadokufe"]
                ) as generate:
                    names = evidence.build_pseudonym_map(ids, forbidden_names=forbidden)
                self.assertEqual(list(names.values()), ["Dadokufe"])
                self.assertEqual(generate.call_count, 2)

    def test_existing_dictionary_preserves_names_when_new_earlier_id_would_steal_them(self):
        def candidate(nid, seed, attempt):
            if attempt == 0:
                return "Babebibo"
            return "Dadokufe" if nid == "a-new-id" else "Gamiloru"

        with patch.object(evidence, "_pseudonym_candidate", side_effect=candidate):
            original = evidence.build_pseudonym_map(["z-original-id"])
            unchanged = deepcopy(original)
            stateless = evidence.build_pseudonym_map(["z-original-id", "a-new-id"])
            expanded = evidence.build_pseudonym_map(
                ["z-original-id", "a-new-id"], existing=original
            )
            reordered = evidence.build_pseudonym_map(
                ["a-new-id", "z-original-id"], existing=original
            )
        self.assertNotEqual(stateless["z-original-id"], original["z-original-id"])
        self.assertEqual(expanded["z-original-id"], original["z-original-id"])
        self.assertEqual(expanded["a-new-id"], "Dadokufe")
        self.assertEqual(expanded, reordered)
        self.assertEqual(original, unchanged)

    def test_existing_dictionary_is_reused_without_hashing_frozen_ids(self):
        original = evidence.build_pseudonym_map(["first-id", "second-id"])
        with patch.object(
            evidence,
            "_pseudonym_candidate",
            side_effect=AssertionError("Frozen names must not regenerate"),
        ):
            self.assertEqual(
                evidence.build_pseudonym_map(reversed(list(original)), seed=9, existing=original),
                original,
            )

    def test_invalid_existing_names_fail_closed(self):
        cases = [
            ({"unknown-id": "Babebibo"}, []),
            ({"first-id": None}, []),
            ({"first-id": ""}, []),
            ({"first-id": "Velora-123456789"}, []),
            ({"first-id": "babebibo"}, []),
            ({"first-id": " Babebibo "}, []),
            ({"first-id": "Babebibo", "second-id": "Babebibo"}, []),
            ({"first-id": "Babebibo", "second-id": "Babetibo"}, []),
            ({"first-id": "Babebibo"}, [" BABEBIBO "]),
        ]
        for existing, forbidden in cases:
            with self.subTest(existing=existing, forbidden=forbidden):
                original = deepcopy(existing)
                with self.assertRaises(ContractError):
                    evidence.build_pseudonym_map(
                        ["first-id", "second-id"], existing=existing, forbidden_names=forbidden
                    )
                self.assertEqual(existing, original)
        with self.assertRaises(ContractError):
            evidence.build_pseudonym_map(
                ["first-id", "babebibo"], existing={"first-id": "Babebibo"}
            )

    def test_collision_exhaustion_is_bounded_and_preserves_existing_dictionary(self):
        existing = {"frozen-id": "Babebibo"}
        with patch.object(evidence, "_pseudonym_candidate", return_value="Babebibo") as generate:
            with self.assertRaisesRegex(ContractError, "exhausted"):
                evidence.build_pseudonym_map(["frozen-id", "new-id"], existing=existing)
        self.assertEqual(generate.call_count, 1024)
        self.assertEqual(existing, {"frozen-id": "Babebibo"})

    def test_invalid_ids_seed_and_forbidden_names_are_rejected(self):
        for ids, seed, forbidden in (
            ([""], 1, []),
            (["  "], 1, []),
            ([123], 1, []),
            (["id"], True, []),
            (["id"], "1", []),
            (["id"], 1, [123]),
        ):
            with self.subTest(ids=ids, seed=seed, forbidden=forbidden):
                with self.assertRaises(ContractError):
                    evidence.build_pseudonym_map(ids, seed, forbidden_names=forbidden)

    def test_aliases_are_consistent_in_paired_questions_cards_relations_and_references(self):
        fixture = preparation_fixture.PreparationReviewTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        originals = [node["name"] for node in fixture.graph.nodes.values()]
        fixture.aliases = evidence.build_pseudonym_map(
            fixture.graph.nodes, forbidden_names=originals
        )
        item_hash, graph_hash, ledger_hash = (
            fingerprint(fixture.item),
            fixture.graph.fingerprint(),
            fingerprint(fixture.ledger),
        )
        rows = [fixture.materialize(cell) for cell in ("R1-matched", "K1", "K5", "K7", "K8")]
        self.assertEqual(audit_paired_conditions(rows)["status"], "passed")
        for row in rows[1:]:
            with self.subTest(cell=row["cell_id"]):
                names = row["private"]["name_map"]
                cards = row["public"]["candidates"]
                self.assertEqual(
                    [card["name"] for card in cards], [fixture.aliases[nid] for nid in fixture.pool]
                )
                self.assertIn(names[fixture.refs[0]], row["public"]["question"])
                self.assertEqual(
                    row["private"]["reference_answer"]["entities"],
                    [names[nid] for nid in row["private"]["target_answer_ids"]],
                )
                kind = "text" if row["cell_id"] in {"K5", "K8"} else "explicit"
                self.assertEqual(
                    evidence.reconstruct_evidence(cards, names, evidence=kind),
                    fixture.graph.induced_edges(fixture.pool),
                )
                public = json.dumps(row["public"])
                for forbidden in originals + fixture.pool:
                    self.assertNotIn(forbidden, public)
                for name in names.values():
                    self.assertRegex(name, ALIAS_PATTERN)
        self.assertEqual(fingerprint(fixture.item), item_hash)
        self.assertEqual(fixture.graph.fingerprint(), graph_hash)
        self.assertEqual(fingerprint(fixture.ledger), ledger_hash)


if __name__ == "__main__":
    unittest.main()
