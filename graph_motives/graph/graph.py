"""Canonical graph ingestion shared by sampling, preparation, and audits."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from .io_utils import digest, open_text

DEFAULT_INGESTION = {
    "name_fields": ["name", "headline", "title", "ticker"],
    "ignore_labels": ["Searchable"],
    "type_priority": ["Company", "News", "Person", "Fund", "City", "State",
                      "Country", "Industry", "Sector", "Product", "Resource"],
}


def norm(value: str) -> str:
    return " ".join(value.split()).casefold()






def _records(path):
    path = Path(path)
    with open_text(path) as stream:
        first = stream.read(4096).lstrip()
    if not first:
        raise ValueError("Empty graph export")
    if first.startswith("["):
        with open_text(path) as stream:
            yield from json.load(stream)
    elif ".jsonl" in str(path).lower():
        with open_text(path) as stream:
            for line in stream:
                if line.strip():
                    yield json.loads(line)
    else:
        with open_text(path) as stream:
            try:
                payload = json.load(stream)
            except json.JSONDecodeError:
                payload = None
        if payload is None:
            with open_text(path) as stream:
                for line in stream:
                    if line.strip():
                        yield json.loads(line)
        elif "nodes" in payload:
            for node in payload["nodes"]:
                yield {**node, "kind": "node"}
            for edge in payload.get("edges", payload.get("relationships", [])):
                yield {**edge, "kind": "relationship"}
        else:
            yield payload


def _endpoint(value):
    if isinstance(value, dict):
        value = value.get("id", value.get("elementId"))
    if value is None:
        raise ValueError("Missing relationship endpoint ID")
    return str(value)


class Graph:
    """Indexed snapshot; callers must treat exposed dictionaries as read-only.

    ``name_to_id`` uses whitespace-normalized casefolded names and indexes only
    usable canonical nodes. Duplicate-name records retain their legacy ``dup_of``
    marker and are never eligible for candidate resolution.
    """

    def __init__(self):
        self.nodes = {}
        self.edges = set()
        self.out = defaultdict(set)
        self.inc = defaultdict(set)
        self.name_to_id = {}
        self.by_type = defaultdict(list)
        self.graph_hash = None
        self.cache = {}

    def name(self, nid):
        return self.nodes[nid]["name"]

    def type(self, nid):
        return self.nodes[nid]["type"]

    def neighbours(self, nid):
        return {e[2] for e in self.out.get(nid, ())} | {e[0] for e in self.inc.get(nid, ())}

    def induced_edges(self, ids):
        ids = set(ids)
        return {edge for nid in ids for edge in self.out.get(nid, ()) if edge[2] in ids}

    def fingerprint(self):
        return digest({"nodes": self.nodes, "edges": sorted(self.edges)})

    def summary(self):
        return {"nodes": len(self.nodes), "edges": len(self.edges),
                "graph_hash": self.fingerprint(),
                "relation_types": dict(Counter(e[1] for e in self.edges)),
                "usable_named_nodes": len(self.name_to_id),
                "node_types": dict(Counter(n["type"] for n in self.nodes.values())),
                "duplicate_names_excluded": sum("dup_of" in n for n in self.nodes.values()),
                "self_loops": sum(s == t for s, _, t in self.edges)}


def load_snapshot(path, ingestion=None):
    """Load exactly the legacy normalized snapshot; never modify its source.

    Omitted ingestion uses the checked historical dataset's settings. Pass a
    complete ingestion dictionary to reproduce a differently configured export.
    """
    ingestion = DEFAULT_INGESTION if ingestion is None else ingestion
    names = ingestion.get("name_fields", ["name", "headline", "title", "ticker"])
    ignored = set(ingestion.get("ignore_labels", ["Searchable"]))
    priority = ingestion.get("type_priority", [])
    graph = Graph()
    raw_edges = []
    for record in _records(path):
        kind = record.get("kind", record.get("type"))
        if kind == "node":
            nid = _endpoint(record.get("id", record.get("elementId")))
            props = record.get("properties") or {}
            labels = sorted(set(record.get("labels", [])))
            types = [x for x in priority if x in labels and x not in ignored]
            types += [x for x in labels if x not in ignored and x not in types]
            name = next((" ".join(str(props[x]).split()) for x in names if props.get(x)), None)
            name = name or record.get("name")
            node = {"name": name or "Unnamed entity", "type": types[0] if types else "Entity",
                    "labels": labels, "properties": props, "unnamed": not bool(name)}
            if nid in graph.nodes and graph.nodes[nid] != node:
                raise ValueError(f"Conflicting records for node ID {nid}")
            graph.nodes[nid] = node
        elif kind in ("relationship", "edge"):
            rel = record.get("relation") or record.get("label") or record.get("relationshipType")
            if not rel:
                rel = record.get("type") if record.get("type") not in ("relationship", "edge") else None
            if not rel:
                raise ValueError("Relationship has no type")
            raw_edges.append((_endpoint(record.get("source", record.get("start"))), str(rel),
                              _endpoint(record.get("target", record.get("end")))))
        else:
            raise ValueError(f"Unknown graph record kind: {kind!r}")
    if not graph.nodes:
        raise ValueError("Graph has no nodes")
    graph.nodes = dict(sorted(graph.nodes.items()))
    seen = {}
    for nid, node in graph.nodes.items():
        key = norm(node["name"])
        if key in seen:
            node["dup_of"] = seen[key]
        else:
            seen[key] = nid
            if not node["unnamed"]:
                graph.name_to_id[key] = nid
                graph.by_type[node["type"]].append(nid)
    for edge in sorted(set(raw_edges)):
        s, _, t = edge
        if s not in graph.nodes or t not in graph.nodes:
            raise ValueError(f"Dangling edge: {edge}")
        graph.edges.add(edge)
        graph.out[s].add(edge)
        graph.inc[t].add(edge)
    if not graph.name_to_id:
        raise ValueError("Graph has no usable named nodes")
    graph.cache["node_ids"] = list(graph.name_to_id.values())
    graph.graph_hash = graph.fingerprint()
    return graph


def recompute_graph_fingerprint(graph, expected=None):
    """Recompute semantic identity, rather than trusting an export manifest."""
    observed = graph.fingerprint()
    return {"status": "ok" if expected is None or observed == expected else "error",
            "observed_graph_hash": observed, "expected_graph_hash": expected,
            "errors": [] if expected is None or observed == expected else ["graph_hash_mismatch"],
            **graph.summary()}


def load_graph(path, config=None):
    """Load a graph using the same normalization as controlled preparation."""
    return load_snapshot(path, (config or {}).get("ingestion"))
