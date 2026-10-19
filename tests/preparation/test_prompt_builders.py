import copy
import json
import unittest

from graph_motives.preparation.contracts import ContractError, fingerprint
from graph_motives.preparation.parsing import parse_output
from graph_motives.preparation.prompts import (
    OUTPUT_CAPS,
    PROMPT_VERSION,
    build_answer_prompt,
    build_calibration_prompt,
    build_closed_book_prompt,
    build_incremental_prompt,
    build_incremental_public_view,
    build_judge_prompt,
    build_preparation_audit_prompt,
    build_request,
    build_selection_prompt,
)


def public():
    return {"question": "Starting from Entity Alpha, which endpoint is reached?",
            "format_note": "A relation states its source, direction and target.",
            "candidates": [
                {"name": "Entity Alpha", "type": "Company", "facts": {"description": "Connected to Entity Beta."}},
                {"name": "Entity Beta", "type": "City", "facts": {"description": "In Region Gamma."}},
                {"name": "Region Gamma", "type": "State", "facts": {}},
            ]}


def materialized():
    result = {"schema_version": "materialized_fixture_v1", "record_id": "record-1",
              "cell_id": "K8", "variant": "disconnected", "protocol_version": "controlled_v1",
              "prompt_version": PROMPT_VERSION, "card_version": "controlled_cards_v1",
              "question_version": "endpoint_questions_v1", "public": public(),
              "private": {"reference_ids": ["secret-node"], "gold": "SECRET_REFERENCE_ONLY"},
              "readiness": "validated_controlled", "audit": {"answerability": "passed"}}
    result["public_sha256"] = fingerprint(result["public"])
    result["materialized_sha256"] = fingerprint(result)
    return result


MODEL = {"alias": "fixture-model", "provider": "mock", "provider_model": "mock/model"}


class PromptBuilderTests(unittest.TestCase):
    def test_selection_serializes_exact_public_payload_and_schema(self):
        task = public()
        original = copy.deepcopy(task)
        prompt = build_selection_prompt(task)
        self.assertEqual(json.loads(prompt["user_prompt"]), task)
        self.assertEqual(task, original)
        self.assertEqual(prompt["prompt_id"], "P06")
        self.assertEqual(prompt["response_schema"], "selection_v1")
        self.assertEqual(prompt["candidate_names"], tuple(c["name"] for c in task["candidates"]))
        self.assertIn("all parallel supporting routes", prompt["system_prompt"])
        self.assertIn("each selected card is independently necessary evidence", prompt["system_prompt"])
        self.assertNotIn("one complete sufficient route", prompt["system_prompt"])
        parsed = parse_output('{"selected_entities":["Entity Alpha","Entity Beta"],"insufficient_evidence":false}', prompt["response_schema"], prompt["candidate_names"])
        self.assertEqual(len(parsed["selected_entities"]), 2)

    def test_solver_builders_reject_envelopes_and_private_fields_recursively(self):
        builders = [build_selection_prompt, build_answer_prompt, build_calibration_prompt]
        for builder in builders:
            with self.subTest(builder=builder.__name__):
                with self.assertRaises(ContractError):
                    builder(materialized())
                for field in ("private", "gold", "reference_ids", "graph_hash", "correct"):
                    task = public()
                    task["candidates"][0]["facts"][field] = "private evidence"
                    with self.assertRaises(ContractError):
                        builder(task)

    def test_closed_book_is_names_and_types_with_no_label_or_facts_channel(self):
        task = public()
        for card in task["candidates"]:
            card["facts"] = {}
            card["labels"] = ["Company"]
        prompt = build_closed_book_prompt(task)
        payload = json.loads(prompt["user_prompt"])
        self.assertTrue(all(set(c) == {"name", "type"} for c in payload["candidates"]))
        self.assertEqual(prompt["prompt_id"], "P01_NAMES_TYPES")
        self.assertNotIn("format_note", payload)
        self.assertIn("prior knowledge", prompt["system_prompt"])
        self.assertIn("unfamiliar or fictional names", prompt["system_prompt"])
        self.assertNotIn("Do not use outside facts", prompt["system_prompt"])
        with self.assertRaises(ContractError):
            build_closed_book_prompt(public())

    def test_closed_book_memory_permission_is_not_used_by_controlled_solvers(self):
        selection = build_selection_prompt(public())
        answer = build_answer_prompt(public())
        self.assertIn("Do not use outside facts", selection["system_prompt"])
        self.assertIn("outside knowledge", answer["system_prompt"])
        self.assertNotIn("prior knowledge", selection["system_prompt"])
        self.assertNotIn("prior knowledge", answer["system_prompt"])

    def test_answer_receives_only_selected_cards_in_frozen_candidate_order(self):
        task = public()
        prompt = build_answer_prompt(task, ["Region Gamma", "Entity Alpha"])
        payload = json.loads(prompt["user_prompt"])
        self.assertEqual([c["name"] for c in payload["evidence"]], ["Entity Alpha", "Region Gamma"])
        self.assertEqual(set(payload), {"question", "evidence", "format_note"})
        self.assertNotIn("branch", payload)
        self.assertNotIn("Entity Beta", json.dumps(payload["evidence"][1]))
        empty = build_answer_prompt(task, [])
        self.assertEqual(json.loads(empty["user_prompt"])["evidence"], [])
        for names in (["unknown"], ["Entity Alpha", "Entity Alpha"], ["entity alpha"], "Entity Alpha", [None]):
            with self.assertRaises(ContractError):
                build_answer_prompt(task, names)

    def test_incremental_history_is_public_strict_and_copied(self):
        history = [{"action": "select", "name": "Entity Alpha", "observation": {"values": ["Entity Beta"]}}]
        old = copy.deepcopy(history)
        prompt = build_incremental_prompt(public(), history, 25)
        payload = json.loads(prompt["user_prompt"])
        self.assertEqual(payload["history"], history)
        self.assertEqual(history, old)
        self.assertEqual(payload["turns_remaining"], 25)
        self.assertEqual(prompt["response_schema"], "incremental_v1")
        for turns in (0, -1, True, 1.5, None):
            with self.assertRaises(ContractError):
                build_incremental_prompt(public(), history, turns)
        for broken in (
            [{"action": "select", "name": "Entity Alpha", "observation": {"gold": True}}],
            [{"action": "select", "name": "unknown", "observation": {}}],
            history + history,
            [{"action": "done", "name": "Entity Alpha", "observation": {}}],
            [{"action": "done", "name": None, "observation": {}}] + history,
            [{"action": "select", "name": "Entity Alpha", "observation": {}, "score": 1}],
        ):
            with self.assertRaises(ContractError):
                build_incremental_prompt(public(), broken, 2)

    def test_incremental_on_select_hides_unselected_facts_and_reveals_uniformly(self):
        task = public()
        task["candidates"][0]["facts"] = {
            "relations": [{"source": "Entity Alpha", "relation": "ALPHA_EDGE_SENTINEL", "target": "Entity Beta"}],
            "statement": "ALPHA_STATEMENT_SENTINEL",
        }
        task["candidates"][1]["facts"] = {
            "relations": [{"source": "Entity Beta", "relation": "BETA_EDGE_SENTINEL", "target": "Region Gamma"}],
            "statement": "BETA_STATEMENT_SENTINEL",
        }
        original = copy.deepcopy(task)
        first = build_incremental_prompt(task, [], 26)
        first_payload = json.loads(first["user_prompt"])
        self.assertEqual([c["name"] for c in first_payload["candidates"]], [c["name"] for c in task["candidates"]])
        self.assertTrue(all(c["facts"] == {} for c in first_payload["candidates"]))
        for sentinel in ("ALPHA_EDGE_SENTINEL", "BETA_EDGE_SENTINEL", "ALPHA_STATEMENT_SENTINEL", "BETA_STATEMENT_SENTINEL"):
            self.assertNotIn(sentinel, first["user_prompt"])
        history = [{"action": "select", "name": "Entity Alpha", "observation": {"facts": copy.deepcopy(task["candidates"][0]["facts"])}}]
        later = build_incremental_prompt(task, history, 25)
        later_payload = json.loads(later["user_prompt"])
        self.assertEqual(later_payload["candidates"][0], task["candidates"][0])
        self.assertEqual(later_payload["candidates"][1]["facts"], {})
        self.assertIn("ALPHA_EDGE_SENTINEL", later["user_prompt"])
        self.assertNotIn("BETA_EDGE_SENTINEL", later["user_prompt"])
        self.assertNotIn("BETA_STATEMENT_SENTINEL", later["user_prompt"])
        self.assertEqual(build_incremental_public_view(task, history), {k: v for k, v in later_payload.items() if k not in {"history", "turns_remaining"}})
        self.assertEqual(task, original)
        # The same rule applies to a candidate unrelated to the required route.
        unrelated = [{"action": "select", "name": "Entity Beta", "observation": {}}]
        other = build_incremental_public_view(task, unrelated)
        self.assertEqual(other["candidates"][0]["facts"], {})
        self.assertEqual(other["candidates"][1], task["candidates"][1])
        self.assertIn("Choose one next witness entity", later["system_prompt"])
        self.assertIn("facts on unselected entity cards remain hidden", later["system_prompt"])

    def test_request_incremental_uses_masked_view_while_selection_remains_full(self):
        row = materialized()
        inc = build_request(row, MODEL, "dataset", "allocation", "incremental", history=[], turns_remaining=26)
        selection = build_request(row, MODEL, "dataset", "allocation", "selection")
        self.assertTrue(all(c["facts"] == {} for c in json.loads(inc.user_prompt)["candidates"]))
        self.assertEqual(json.loads(selection.user_prompt)["candidates"], row["public"]["candidates"])
        self.assertEqual(inc.item_sha256, row["materialized_sha256"])

    def test_judge_private_reference_is_intentional_and_solver_is_blind(self):
        reference = {"answer_entities": ["Region Gamma"], "private": {"reference_ids": ["secret-node"]}}
        response = {"answer": "Region Gamma", "insufficient_evidence": False}
        prompt = build_judge_prompt(public()["question"], reference, public()["candidates"][1:], response)
        payload = json.loads(prompt["user_prompt"])
        self.assertEqual(payload["reference_requirements"], reference)
        self.assertEqual(payload["response"], response)
        self.assertEqual(len(payload["available_evidence"]), 2)
        self.assertNotIn("model", payload)
        self.assertNotIn("branch", payload)
        self.assertEqual(prompt["response_schema"], "judge_v1")
        for broken in ({"answer": "", "insufficient_evidence": False}, {**response, "reason": "extra"}, {**response, "insufficient_evidence": "false"}):
            with self.assertRaises(ContractError):
                build_judge_prompt("Question", reference, [], broken)

    def test_audit_and_calibration_use_specialized_schemas(self):
        audit = build_preparation_audit_prompt({"canonical_facts": [{"private": {"gold": "permitted for auditor"}}]}, {"goal": "Question", "slots": "Equivalent question"})
        self.assertEqual(audit["response_schema"], "audit_v1")
        self.assertIn("does not prove mathematical uniqueness", audit["system_prompt"])
        cal = build_calibration_prompt(public())
        self.assertEqual(cal["response_schema"], "calibration_v1")
        self.assertEqual(cal["prompt_id"], "P05")
        with self.assertRaises(ContractError):
            build_preparation_audit_prompt({})

    def test_build_request_joins_approved_artifact_and_fingerprints(self):
        row = materialized()
        req = build_request(row, MODEL, "dataset-sha", "allocation-1")
        self.assertEqual(req.item_sha256, row["materialized_sha256"])
        self.assertEqual(req.cell.prompt_version, PROMPT_VERSION)
        self.assertEqual(req.settings["temperature"], 0)
        self.assertEqual(req.settings["max_tokens"], 1024)
        self.assertEqual(req.request_type, "selection")
        self.assertEqual(req.model, MODEL["alias"])
        self.assertNotIn("SECRET_REFERENCE_ONLY", req.user_prompt)
        self.assertNotIn("secret-node", req.user_prompt)
        self.assertEqual(req.request_id, build_request(row, MODEL, "dataset-sha", "allocation-1").request_id)

    def test_request_hashes_bind_prompt_upstream_branch_and_audit_provenance(self):
        row = materialized()
        first = build_request(row, MODEL, "dataset-sha", "allocation-1", stage="answer", selected_names=["Entity Alpha"], upstream_result_hashes=("selection-a",), branch="predicted")
        second = build_request(row, MODEL, "dataset-sha", "allocation-1", stage="answer", selected_names=["Entity Alpha"], upstream_result_hashes=("selection-b",), branch="predicted")
        oracle = build_request(row, MODEL, "dataset-sha", "allocation-1", stage="answer", selected_names=["Entity Alpha"], upstream_result_hashes=("selection-a",), branch="oracle_support")
        self.assertNotEqual(first.request_id, second.request_id)
        self.assertNotEqual(first.request_id, oracle.request_id)
        self.assertEqual(first.user_prompt, oracle.user_prompt)
        changed = copy.deepcopy(row)
        changed["private"]["gold"] = "DIFFERENT_REFERENCE"
        changed.pop("materialized_sha256")
        new = build_request(changed, MODEL, "dataset-sha", "allocation-1")
        self.assertNotEqual(new.item_sha256, first.item_sha256)

    def test_stage_caps_and_prompt_ids(self):
        row = materialized()
        cases = {
            "selection": {}, "answer": {"selected_names": ["Entity Alpha"]},
            "incremental": {"history": [], "turns_remaining": 26},
            "judge": {"selected_names": [], "reference": {"answer_entities": ["Region Gamma"]}, "response": {"answer": "Unknown", "insufficient_evidence": True}},
            "calibration": {}, "audit": {"audit_input": {"canonical_facts": ["fact"]}},
        }
        schemas = {"selection": "selection_v1", "answer": "answer_v1", "incremental": "incremental_v1", "judge": "judge_v1", "calibration": "calibration_v1", "audit": "audit_v1"}
        for stage, options in cases.items():
            with self.subTest(stage=stage):
                req = build_request(row, MODEL, "dataset", "allocation", stage, **options)
                self.assertEqual(req.settings["max_tokens"], OUTPUT_CAPS[stage])
                self.assertEqual(req.response_schema, schemas[stage])

    def test_closed_book_materialized_uses_p01(self):
        row = materialized()
        row.pop("materialized_sha256")
        row.pop("public_sha256")
        row["cell_id"] = "K0"
        row["readiness"] = "closed_book_baseline"
        for card in row["public"]["candidates"]:
            card["facts"] = {}
        req = build_request(row, MODEL, "dataset", "allocation")
        self.assertTrue(all(set(c) == {"name", "type"} for c in json.loads(req.user_prompt)["candidates"]))

    def test_readiness_and_native_protocol_guard(self):
        for readiness in ("excluded", "native_requires_answerability_audit", "validated_native_explicit", True):
            row = materialized()
            row.pop("materialized_sha256")
            row["readiness"] = readiness
            with self.assertRaises(ContractError):
                build_request(row, MODEL, "dataset", "allocation")
        for cell in ("Braw", "Braw+E"):
            row = materialized()
            row["cell_id"] = cell
            with self.assertRaises(ContractError):
                build_request(row, MODEL, "dataset", "allocation")

    def test_tamper_and_placeholder_versions_are_blocked(self):
        row = materialized()
        row["public"]["question"] = "Tampered question"
        with self.assertRaises(ContractError):
            build_request(row, MODEL, "dataset", "allocation")
        for key in ("protocol_version", "prompt_version", "card_version", "question_version"):
            row = materialized()
            row.pop("materialized_sha256")
            row[key] = "planned_v1_not_materialized"
            with self.assertRaises(ContractError):
                build_request(row, MODEL, "dataset", "allocation")

    def test_credentials_and_protocol_setting_drift_are_rejected(self):
        for model in ({**MODEL, "api_key": "not-a-real-secret"},
                      {**MODEL, "settings": {"api_key": "not-a-real-secret"}},
                      {**MODEL, "settings": {"temperature": 0.3}},
                      {**MODEL, "settings": {"temperature": False}},
                      {**MODEL, "settings": {"max_tokens": 4096}}):
            with self.assertRaises(ContractError):
                build_request(materialized(), model, "dataset", "allocation")

    def test_nonstring_format_note_and_ambiguous_candidate_names_fail(self):
        row = public()
        row["format_note"] = {"reference": "secret"}
        with self.assertRaises(ContractError):
            build_selection_prompt(row)
        row = public()
        row["candidates"][1]["name"] = "ENTITY   ALPHA"
        with self.assertRaises(ContractError):
            build_selection_prompt(row)

    def test_prompt_hash_changes_with_content_and_is_deterministic(self):
        first = build_selection_prompt(public())
        changed = public()
        changed["question"] = "Different question"
        second = build_selection_prompt(changed)
        self.assertNotEqual(first["prompt_sha256"], second["prompt_sha256"])
        self.assertEqual(first, build_selection_prompt(public()))


if __name__ == "__main__":
    unittest.main()
