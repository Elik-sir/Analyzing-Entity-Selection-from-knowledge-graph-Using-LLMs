"""Read-only streaming Neo4j snapshot export; no APOC installation required."""

from __future__ import annotations

import datetime
import gzip
import json
import os
from pathlib import Path

from .io_utils import write_json

NODE_QUERY = """MATCH (n) RETURN elementId(n) AS id, labels(n) AS labels,
properties(n) AS properties"""
EDGE_QUERY = """MATCH (s)-[r]->(t) RETURN elementId(r) AS id,
elementId(s) AS source, type(r) AS relation, elementId(t) AS target,
properties(r) AS properties"""


def json_value(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    return value.iso_format() if hasattr(value, "iso_format") else str(value)


def export_neo4j(path: Path, config: dict) -> dict:
    from neo4j import READ_ACCESS, GraphDatabase

    cfg = config.get("neo4j", {})
    uri = os.environ.get("NEO4J_URI", cfg.get("uri", "neo4j://localhost:7687"))
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD")
    if not password:
        raise ValueError("Set NEO4J_PASSWORD in the environment or local .env")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")

    def read_snapshot(tx):
        # execute_read can retry: recreate the temporary file, never append duplicates.
        counts = {"nodes": 0, "edges": 0}
        opener = gzip.open if path.suffix == ".gz" else open
        with opener(tmp, "wt", encoding="utf-8") as stream:
            for kind, query, counter in [
                ("node", NODE_QUERY, "nodes"),
                ("relationship", EDGE_QUERY, "edges"),
            ]:
                for record in tx.run(query):
                    stream.write(
                        json.dumps({"kind": kind, **json_value(record.data())}, ensure_ascii=False)
                        + "\n"
                    )
                    counts[counter] += 1
        return counts

    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        driver.verify_connectivity()
        with driver.session(
            database=cfg.get("database", "neo4j"),
            default_access_mode=READ_ACCESS,
            fetch_size=int(cfg.get("fetch_size", 1000)),
        ) as session:
            counts = session.execute_read(read_snapshot)
    tmp.replace(path)
    manifest = {
        **counts,
        "database": cfg.get("database", "neo4j"),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "node_query": NODE_QUERY,
        "edge_query": EDGE_QUERY,
        "consistency": "Export an immutable database/backup; concurrent writes are not snapshot-isolated.",
    }
    write_json(path.with_name(path.name + ".manifest.json"), manifest)
    return manifest
