"""Strict parsers for new protocols; historical parsing remains separate."""

import json

from .contracts import ContractError, canonical_json, exact_keys, nonempty

PARSER_VERSION = "strict_json_v1"
SCHEMAS = {"selection_v1", "answer_v1", "judge_v1", "incremental_v1", "audit_v1", "calibration_v1", "object_v1"}


def parse_output(raw, schema, candidates=()):
    def reject_constant(value):
        raise ContractError("Non-finite JSON number")

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ContractError("Duplicate JSON field")
            result[key] = value
        return result

    if schema not in SCHEMAS:
        raise ContractError("Unknown response schema")
    try:
        value = json.loads(raw, parse_constant=reject_constant, object_pairs_hook=unique_object)
    except (ValueError, TypeError) as error:
        raise ContractError("Response is not one strict JSON object") from error
    if not isinstance(value, dict):
        raise ContractError("Response must be an object")
    try:
        canonical_json(value)
    except ValueError as error:
        raise ContractError("Non-finite JSON value") from error
    if schema == "object_v1":
        return value  # Infrastructure only; preparation schemas must be specialized in stage 4.
    required = {"selection_v1": ("selected_entities", "insufficient_evidence"),
                "answer_v1": ("answer", "insufficient_evidence"),
                "judge_v1": ("correct", "metadata_sufficient", "reason"),
                "audit_v1": ("valid", "reasons"),
                "calibration_v1": ("result", "insufficient_evidence"),
                "incremental_v1": ("action", "name", "insufficient_evidence")}[schema]
    exact_keys(value, required)
    for key in ("insufficient_evidence", "correct", "metadata_sufficient", "valid"):
        if key in value and type(value[key]) is not bool:
            raise ContractError("Boolean field required")
    if schema in {"selection_v1", "calibration_v1"}:
        names = value["selected_entities" if schema == "selection_v1" else "result"]
        if not isinstance(names, list) or any(not isinstance(n, str) for n in names):
            raise ContractError("Selected/results fields must be strings")
        if len(names) != len(set(names)) or not set(names) <= set(candidates):
            raise ContractError("Unknown or repeated candidate")
    elif schema == "answer_v1":
        nonempty(value["answer"], "answer")
    elif schema == "judge_v1":
        nonempty(value["reason"], "reason")
    elif schema == "audit_v1":
        if not isinstance(value["reasons"], list) or any(not isinstance(r, str) or not r.strip() for r in value["reasons"]):
            raise ContractError("Audit reasons must be nonempty strings")
        if not value["valid"] and not value["reasons"]:
            raise ContractError("Failed audit must explain its reasons")
    elif value["action"] == "select":
        if not isinstance(value["name"], str) or value["name"] not in candidates:
            raise ContractError("Unknown candidate")
    elif value["action"] != "done" or value["name"] is not None:
        raise ContractError("Invalid incremental action")
    return value
