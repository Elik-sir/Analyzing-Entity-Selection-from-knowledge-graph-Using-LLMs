"""Persisted public/private contracts. Only PublicInput reaches prompt builders."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Candidate(StrictModel):
    name: str
    type: str
    facts: dict[str, Any]
    labels: list[str] = Field(default_factory=list)


class PublicInput(StrictModel):
    question: str
    candidates: list[Candidate]


class GoldAnswer(StrictModel):
    entities: list[str]
    relations: list[tuple[str, str, str]]


class Hidden(StrictModel):
    anchor: str
    pattern: str
    reference_names: list[str]
    reference_ids: list[str]
    answer: GoldAnswer
    context_relations: list[tuple[str, str, str]]
    adjacent_names: list[str]


class Item(StrictModel):
    record_id: str
    variant: str
    subgraph_type: str
    size: int
    public: PublicInput
    private: Hidden
    graph_hash: str
    config_hash: str
    protocol: str = "nodes_only_text_answer_v2"
