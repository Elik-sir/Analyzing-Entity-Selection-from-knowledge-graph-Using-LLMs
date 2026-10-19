"""Reuse the frozen article prompt builders and exact protocol-specific parsers."""

import json
from copy import deepcopy

from graph_motives.legacy_protocol import (
    ANSWER_SYSTEM,
    JUDGE_SYSTEM,
    build_answer_prompt,
    build_judge_prompt,
    json_objects,
    parse_answer,
    parse_selection,
)
from graph_motives.preparation.parsing import parse_output
from graph_motives.preparation.prompts import (
    build_calibration_prompt,
    build_closed_book_prompt,
    build_incremental_prompt,
    build_selection_prompt,
)

from .common import canonical

TOKEN_CAPS = {
    "core": 1024,
    "size": 1024,
    "calibration": 1024,
    "incremental": 256,
    "native_d": 4096,
    "full_braw": 1024,
    "legacy": 4096,
}
TOOL_SCHEMA = {
    "type": "object",
    "properties": {"selected_tools": {"type": "array", "items": {"type": "string"}}},
    "required": ["selected_tools"],
    "additionalProperties": False,
}


def from_prompt(prompt):
    return [
        {"role": "system", "content": prompt["system_prompt"]},
        {"role": "user", "content": prompt["user_prompt"]},
    ]


def request_for(task, config, *, stage="selection", history=None, selected=None, answer=None):
    series, payload = task["series_id"], task["input"]
    schema = "selection_v1"
    evidence = "recorded_messages"
    if series == "incremental":
        prompt = build_incremental_prompt(
            payload["frozen_public"], history or [], config["execution"]["max_turns"] - len(history or [])
        )
        messages, schema, evidence = from_prompt(prompt), "incremental_v1", "frozen_public_prompt_builder"
    elif series == "legacy" and stage != "selection":
        public = json.loads(payload["messages"][1]["content"])
        if stage == "answer":
            messages = [
                {"role": "system", "content": ANSWER_SYSTEM},
                {"role": "user", "content": build_answer_prompt(public, selected)},
            ]
            schema = "answer_v1"
        else:
            item = {"public": public, "private": payload["reference"]}
            messages = [
                {"role": "system", "content": JUDGE_SYSTEM},
                {
                    "role": "user",
                    "content": build_judge_prompt(
                        item, {"selected_entities": selected, "predicted_answer": answer}
                    ),
                },
            ]
            schema = "legacy_judge_v1"
        evidence = "frozen_legacy_prompt_builder_with_new_upstream_output"
    elif payload.get("messages"):
        messages = deepcopy(payload["messages"])
        if series == "native_d":
            schema = "paper_selected_tools_v1"
        elif series == "legacy":
            schema = "legacy_selection_v1"
    else:
        public = payload["frozen_public"]
        if series == "calibration":
            prompt = build_calibration_prompt(public)
        elif task.get("frozen_input_metadata", {}).get("readiness") == "closed_book_baseline":
            prompt = build_closed_book_prompt(public)
        else:
            prompt = build_selection_prompt(public)
        messages, schema = from_prompt(prompt), prompt["response_schema"]
        evidence = "frozen_public_prompt_builder"
    generation = config["generation"]
    cap = generation.get("max_tokens_by_series", {}).get(series, TOKEN_CAPS[series])
    result = {
        "messages": messages,
        "schema": schema,
        "candidate_names": payload["candidate_names"],
        "stage": stage,
        "prompt_evidence": evidence,
        "settings": {
            "temperature": generation["temperature"],
            "max_tokens": cap,
            "timeout_s": config["execution"]["timeout_s"],
            "response_format": "none" if series in {"legacy", "native_d"} else "json_object",
        },
    }
    if series == "native_d":
        result["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": "final_result",
                    "description": "The final response which ends this conversation",
                    "parameters": TOOL_SCHEMA,
                },
            }
        ]
        result["tool_choice"] = {"type": "function", "function": {"name": "final_result"}}
    return result


def parse(text, request):
    schema, candidates = request["schema"], request["candidate_names"]
    if schema == "legacy_selection_v1":
        selected, unknown, insufficient = parse_selection(text, candidates)
        return {
            "selected_entities": selected,
            "unknown_entities": unknown,
            "insufficient_evidence": insufficient,
        }
    if schema == "answer_v1":
        return parse_answer(text)
    if schema == "legacy_judge_v1":
        objects = json_objects(text)
        if not objects:
            raise ValueError("judge_parse_failure")
        verdict = objects[-1]
        if (
            type(verdict.get("correct")) is not bool
            or type(verdict.get("metadata_sufficient")) is not bool
            or not isinstance(verdict.get("reason"), str)
            or not verdict["reason"].strip()
        ):
            raise ValueError("invalid_judge_verdict")
        return verdict
    if schema == "paper_selected_tools_v1":
        value = parse_output(text, "object_v1")
        if set(value) != {"selected_tools"}:
            raise ValueError("Wrong selected_tools fields")
        # Same candidate validation as strict controlled selection.
        parse_output(
            canonical({"selected_entities": value["selected_tools"], "insufficient_evidence": False}),
            "selection_v1",
            candidates,
        )
        return value
    return parse_output(text, schema, candidates)


def scores(selected, reference, normalization=None):
    if normalization == "whitespace_casefold":

        def normalize(value):
            return " ".join(value.split()).casefold()

        selected, reference = list(map(normalize, selected)), list(map(normalize, reference))
    chosen, gold = set(selected), set(reference)
    tp, fp, fn = len(chosen & gold), len(chosen - gold), len(gold - chosen)
    p, r = tp / len(chosen) if chosen else 0.0, tp / len(gold) if gold else 1.0
    return {
        "precision": p,
        "recall": r,
        "f1": 2 * p * r / (p + r) if p + r else 0.0,
        "exact": chosen == gold,
        "fp": fp,
        "fn": fn,
    }
