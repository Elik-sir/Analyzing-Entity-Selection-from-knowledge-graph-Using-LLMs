"""Versioned local runtime contracts. No provider imports or network side effects."""

import math
from copy import deepcopy
from dataclasses import asdict, dataclass, field

from ..common import canonical as canonical_json
from ..common import digest as fingerprint


class ContractError(ValueError):
    pass






def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a nonempty string")


def exact_keys(value, required, optional=()):
    if not isinstance(value, dict) or set(required) - set(value) or set(value) - set(required) - set(optional):
        raise ContractError("Unexpected or missing object fields")


def reject_private(value):
    """Guard schema fields, not incidental occurrences of words in factual text."""
    forbidden = {"private", "gold", "reference_ids", "reference_names", "reference",
                 "ground_truth", "item_hash", "graph_hash", "correct", "is_gold"}
    if isinstance(value, dict):
        if any(str(k).casefold() in forbidden for k in value):
            raise ContractError("Private/evaluation field in public task")
        for child in value.values():
            reject_private(child)
    elif isinstance(value, list):
        for child in value:
            reject_private(child)


@dataclass(frozen=True)
class PublicTask:
    question: str
    candidates: list[dict]

    def __post_init__(self):
        nonempty(self.question, "question")
        if not isinstance(self.candidates, list):
            raise ContractError("candidates must be a list")
        names = []
        for card in self.candidates:
            exact_keys(card, ("name", "type", "facts"), ("labels",))
            nonempty(card["name"], "candidate name")
            nonempty(card["type"], "candidate type")
            if not isinstance(card["facts"], dict):
                raise ContractError("facts must be an object")
            if "labels" in card and (not isinstance(card["labels"], list) or
                                     any(not isinstance(v, str) for v in card["labels"])):
                raise ContractError("labels must be strings")
            names.append(" ".join(card["name"].split()).casefold())
        if len(names) != len(set(names)):
            raise ContractError("Ambiguous candidate names")
        reject_private(self.to_dict())
        canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, value):
        exact_keys(value, ("question", "candidates"))
        return cls(value["question"], deepcopy(value["candidates"]))

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class BaseItem:
    record_id: str
    variant: str
    motif: str
    size: int
    graph_hash: str
    protocol: str
    item_sha256: str
    public: PublicTask
    private: dict = field(repr=False)

    @classmethod
    def from_legacy(cls, row):
        for key in ("record_id", "variant", "subgraph_type", "graph_hash", "protocol"):
            nonempty(row.get(key), key)
        size, private = row.get("size"), row.get("private")
        if type(size) is not int or size < 1:
            raise ContractError("Invalid motif size")
        if not isinstance(private, dict):
            raise ContractError("Missing private reference")
        for key in ("reference_ids", "reference_names"):
            values = private.get(key)
            if (not isinstance(values, list) or len(values) != size or
                    any(not isinstance(v, str) or not v for v in values) or len(set(values)) != size):
                raise ContractError("Invalid reference node list")
        if not isinstance(private.get("answer"), dict):
            raise ContractError("Missing reference answer")
        public = PublicTask.from_dict(row["public"])
        if not set(private["reference_names"]) <= {c["name"] for c in public.candidates}:
            raise ContractError("Gold names absent from candidates")
        return cls(row["record_id"], row["variant"], row["subgraph_type"], size,
                   row["graph_hash"], row["protocol"], fingerprint(row), public, deepcopy(private))


@dataclass(frozen=True)
class CellSpec:
    cell_id: str
    protocol_version: str
    prompt_version: str
    card_version: str
    question_version: str

    def __post_init__(self):
        for key, value in asdict(self).items():
            nonempty(value, key)
            if "planned" in value or "not_materialized" in value:
                raise ContractError("Planning placeholders cannot identify executable material")


REQUEST_TYPES = {"selection", "answer", "judge", "incremental", "calibration",
                 "audit", "card_rewrite", "question_generation"}
SETTINGS = {"temperature", "max_tokens", "top_p", "seed", "timeout_s",
            "reasoning_enabled", "response_format"}


@dataclass(frozen=True)
class CallRequest:
    allocation_id: str
    record_id: str
    variant: str
    cell: CellSpec
    request_type: str
    model: str
    provider: str
    provider_model: str
    dataset_sha256: str
    item_sha256: str
    system_prompt: str
    user_prompt: str
    settings: dict
    response_schema: str
    candidate_names: tuple[str, ...] = ()
    upstream_result_hashes: tuple[str, ...] = ()
    branch: str | None = None
    turn: int = 0

    def __post_init__(self):
        for key in ("allocation_id", "record_id", "variant", "model", "provider",
                    "provider_model", "dataset_sha256", "item_sha256", "system_prompt",
                    "user_prompt", "response_schema"):
            nonempty(getattr(self, key), key)
        if not isinstance(self.cell, CellSpec) or self.request_type not in REQUEST_TYPES:
            raise ContractError("Unknown cell or request type")
        if type(self.turn) is not int or self.turn < 0:
            raise ContractError("Invalid turn")
        if self.branch is not None:
            nonempty(self.branch, "branch")
        if not isinstance(self.settings, dict) or set(self.settings) - SETTINGS:
            raise ContractError("Unknown/credential-bearing model settings")
        for key in ("temperature", "top_p", "timeout_s"):
            if key in self.settings:
                val = self.settings[key]
                if type(val) not in (int, float) or not math.isfinite(val) or val < 0:
                    raise ContractError("Invalid numeric model setting")
        for key in ("max_tokens", "seed"):
            if key in self.settings and (type(self.settings[key]) is not int or self.settings[key] < 0):
                raise ContractError("Invalid integer model setting")
        if self.settings.get("max_tokens") == 0 or self.settings.get("timeout_s") == 0:
            raise ContractError("Output and timeout limits must be positive")
        if "reasoning_enabled" in self.settings and type(self.settings["reasoning_enabled"]) is not bool:
            raise ContractError("Invalid reasoning flag")
        if "response_format" in self.settings and self.settings["response_format"] not in ("text", "json_object"):
            raise ContractError("Unsupported response format")
        if any(not isinstance(v, str) or not v for v in (*self.candidate_names, *self.upstream_result_hashes)):
            raise ContractError("Invalid candidate/upstream identities")
        if len(set(self.candidate_names)) != len(self.candidate_names):
            raise ContractError("Duplicate candidates")
        canonical_json(self.to_dict())

    def to_dict(self):
        value = asdict(self)
        value["candidate_names"] = list(self.candidate_names)
        value["upstream_result_hashes"] = list(self.upstream_result_hashes)
        return value

    @classmethod
    def from_dict(cls, value):
        data = deepcopy(value)
        data["cell"] = CellSpec(**data["cell"])
        for key in ("candidate_names", "upstream_result_hashes"):
            data[key] = tuple(data.get(key, ()))
        return cls(**data)

    @property
    def request_id(self):
        return fingerprint(self.to_dict())
