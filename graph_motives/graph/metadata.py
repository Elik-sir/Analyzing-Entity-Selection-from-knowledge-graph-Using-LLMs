"""All informative node metadata, minus identifiers and explicit graph structure."""

from __future__ import annotations

import re

RESERVED = {
    "edges",
    "relations",
    "relationships",
    "neighbors",
    "neighbours",
    "adjacency",
    "reference_tools",
    "answer",
    "pattern",
    "source",
    "target",
    "source_id",
    "target_id",
    "elementid",
    "degree",
    "in_degree",
    "out_degree",
}


def excluded_key(key: str, extra=()) -> bool:
    # fooId / foo_id / UUID / Neo4j elementId are technical identifiers.
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key).casefold()
    return (
        key.casefold() in RESERVED
        or key.casefold() in {s.casefold() for s in extra}
        or snake in {"id", "uuid", "element_id", "internal_id", "neo4j_id", "_id"}
        or snake.endswith(("_id", "_ids", "_uuid"))
    )


def clean_value(value, cfg: dict):
    if isinstance(value, dict):
        return {
            k: clean_value(v, cfg)
            for k, v in value.items()
            if not excluded_key(k, cfg.get("exclude_fields", []))
        }
    if isinstance(value, list):
        return [clean_value(v, cfg) for v in value[: int(cfg.get("max_list_items", 50))]]
    if isinstance(value, str):
        if ("-[" in value and "]->" in value) or re.search(r'"(?:edges|relations)"\s*:', value):
            return "[explicit graph serialization omitted]"
        limit = int(cfg.get("max_chars_per_field", 2000))
        return value[:limit] if limit else value
    return value if value is None or isinstance(value, (int, float, bool)) else str(value)


def public_node(kg, nid: str, config: dict) -> dict:
    node = kg.nodes[nid]
    cfg = config.get("metadata", {})
    allowed = (
        node["properties"]
        if cfg.get("mode", "all") == "all"
        else cfg.get("fields", {}).get(node["type"], cfg.get("default_fields", []))
    )
    facts = {}
    if cfg.get("enabled", True):
        for key in allowed:
            if excluded_key(key, cfg.get("exclude_fields", [])):
                continue
            value = node["properties"].get(key)
            if value is None or value == "":
                continue
            facts[key] = clean_value(value, cfg)
    result = {"name": node["name"], "type": node["type"], "facts": facts}
    if cfg.get("include_labels", False):
        result["labels"] = [
            x
            for x in node["labels"]
            if x not in config.get("ingestion", {}).get("ignore_labels", [])
        ]
    return result


def validate_public_node(node: dict) -> bool:
    if set(node) - {"name", "type", "facts", "labels"}:
        return False

    def valid(value):
        if isinstance(value, dict):
            return all(not excluded_key(k) and valid(v) for k, v in value.items())
        if isinstance(value, list):
            return all(valid(v) for v in value)
        return value is None or isinstance(value, (str, int, float, bool))

    return valid(node.get("facts", {}))
