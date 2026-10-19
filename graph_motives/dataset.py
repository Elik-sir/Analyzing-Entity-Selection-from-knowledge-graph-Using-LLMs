"""Freeze a model-independent task population from the compact article archive."""

import json
import sqlite3
from collections import Counter, defaultdict, deque
from copy import deepcopy
from pathlib import Path

from .common import canonical, digest, file_sha, records

SERIES = ("core", "size", "calibration", "incremental", "native_d", "full_braw", "legacy")


def identity(row):
    return [row[k] for k in ("series_id", "condition", "noise", "base_id")]


def gold_names(payload):
    reference = payload["reference"]
    if "expected_names" in reference:
        return reference["expected_names"]
    if "reference_names" in reference:
        return reference["reference_names"]
    private = reference.get("private", reference)
    if "graph_witness_ids" in private:
        return [private["name_map"][key] for key in private["graph_witness_ids"]]
    if "answer" in private and isinstance(private["answer"], list):
        return private["answer"]
    if "reference_names" in private:
        return private["reference_names"]
    raise ValueError("Missing private scoring reference")


def select_rows(results, series, conditions=(), motifs=(), limit=None):
    """Choose ONE historical model per logical task, preferring authenticated Qwen inputs.

    Legacy uses Gemma first because its Chain+Tree population is larger. The
    source model is provenance, never the new model being evaluated.
    """
    selected = {}
    for row in records(Path(results) / "observations.jsonl.gz"):
        if row["series_id"] not in series or (conditions and row["condition"] not in conditions):
            continue
        if motifs and row["motif"] not in motifs:
            continue
        key = tuple(identity(row))
        preference = (
            ("gemma-4-31b", "qwen3.6-flash", "ministral-14b")
            if row["series_id"] == "legacy"
            else ("qwen3.6-flash", "ministral-14b", "gemma-4-31b")
        )
        rank = preference.index(row["model"]) if row["model"] in preference else len(preference)
        if key not in selected or rank < selected[key][0]:
            selected[key] = (rank, row)
    # A limited pilot alternates across series/condition/noise/motif/size groups.
    groups = defaultdict(deque)
    for key, (_, row) in sorted(selected.items()):
        group = (row["series_id"], canonical([row[k] for k in ("condition", "noise", "motif", "size")]))
        groups[group].append(row)
    by_series = defaultdict(deque)
    for key in sorted(groups):
        by_series[key[0]].append(groups[key])
    queues = deque(by_series[key] for key in sorted(by_series))
    chosen = []
    while queues and (limit is None or len(chosen) < limit):
        series_queue = queues.popleft()
        queue = series_queue.popleft()
        chosen.append(queue.popleft())
        if queue:
            series_queue.append(queue)
        if series_queue:
            queues.append(series_queue)
    if not chosen:
        raise ValueError("No tasks match the requested population")
    return chosen


def freeze_tasks(results, destination, *, series, conditions=(), motifs=(), limit=None):
    results, destination = Path(results).resolve(), Path(destination)
    manifest_path = results / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_hashes = {}
    for name in ("observations.jsonl.gz", "inputs.jsonl.gz"):
        expected = next(row for row in manifest["files"] if row["path"] == name)
        actual = file_sha(results / name)
        if actual != expected["sha256"] or (results / name).stat().st_size != expected["bytes"]:
            raise ValueError("Article input checksum mismatch: " + name)
        source_hashes[name] = actual
    chosen = select_rows(results, series, conditions, motifs, limit)
    by_input = defaultdict(list)
    for number, row in enumerate(chosen):
        by_input[row["input_id"]].append((number, row))
    connection = sqlite3.connect(destination)
    try:
        connection.execute("CREATE TABLE tasks (number INTEGER PRIMARY KEY, task_id TEXT UNIQUE, data TEXT)")
        counts = Counter()
        for payload in records(results / "inputs.jsonl.gz"):
            source_id = payload["input_id"]
            if source_id not in by_input:
                continue
            if digest({k: v for k, v in payload.items() if k != "input_id"}) != source_id:
                raise ValueError("Article input content identity mismatch")
            for number, row in by_input.pop(source_id):
                task = {
                    k: deepcopy(row.get(k))
                    for k in (
                        "series_id",
                        "condition",
                        "noise",
                        "base_id",
                        "motif",
                        "size",
                        "question",
                        "frozen_input_metadata",
                        "request_metadata",
                        "metric_normalization",
                    )
                }
                task.update(
                    task_id=digest(identity(row)),
                    source_observation_id=row["observation_id"],
                    source_model=row["model"],
                    input=payload,
                    gold_names=gold_names(payload),
                )
                if (
                    task["series_id"] != "incremental"
                    and not payload.get("messages")
                    and not payload.get("frozen_public")
                ):
                    raise ValueError("Task has no replayable public input")
                connection.execute(
                    "INSERT INTO tasks VALUES (?, ?, ?)", (number, task["task_id"], canonical(task))
                )
                counts[task["series_id"]] += 1
        if by_input:
            raise ValueError("Missing task inputs")
        connection.commit()
    finally:
        connection.close()
    return {
        "tasks": len(chosen),
        "series_counts": dict(counts),
        "source_files_sha256": source_hashes,
        "source_manifest_sha256": file_sha(manifest_path),
        "tasks_sha256": file_sha(destination),
    }


def tasks(path):
    connection = sqlite3.connect(f"{Path(path).resolve().as_uri()}?mode=ro", uri=True)
    try:
        for (data,) in connection.execute("SELECT data FROM tasks ORDER BY number"):
            yield json.loads(data)
    finally:
        connection.close()
