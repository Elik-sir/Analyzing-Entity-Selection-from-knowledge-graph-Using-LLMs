"""Compare the new runner with archived valid replies and frozen Core prompts, offline."""

# ruff: noqa: E402
import argparse
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from graph_motives.common import canonical, digest, records
from graph_motives.dataset import SERIES, gold_names, identity, select_rows
from graph_motives.protocols import parse, request_for, scores
from graph_motives.runner import normalize_config


def verify(results):
    config = normalize_config(
        {"model": {"alias": "offline", "model": "offline", "provider": "openai", "api_key_env": "UNUSED_KEY"}}
    )
    rows = select_rows(results, SERIES)
    by_input = {}
    for row in rows:
        by_input.setdefault(row["input_id"], []).append(row)
    # Include the frozen Gemma representation to verify reconstructed prompts
    # against independently recorded Qwen requests on all 9,100 Core tasks.
    core_frozen, core_recorded = {}, {}
    for row in records(results / "observations.jsonl.gz"):
        if row["series_id"] == "core" and row["model"] == "gemma-4-31b":
            by_input.setdefault(row["input_id"], []).append(row)
    checks, responses, populations = Counter(), {}, Counter(row["series_id"] for row in rows)
    for payload in records(results / "inputs.jsonl.gz"):
        for row in by_input.pop(payload["input_id"], []):
            task = {**row, "input": payload, "task_id": digest(identity(row))}
            request = request_for(task, config)
            checks["public_requests_built"] += 1
            if row["series_id"] == "core":
                (core_frozen if payload.get("frozen_public") else core_recorded)[task["task_id"]] = digest(
                    request["messages"]
                )
            if row["valid"] and row["response_id"] and row["series_id"] != "incremental":
                responses.setdefault(row["response_id"], []).append((row, request, gold_names(payload)))
    if by_input:
        raise ValueError("Missing archived input")
    if core_frozen != core_recorded or len(core_frozen) != 9100:
        raise ValueError("Frozen public prompt reconstruction differs from recorded Core messages")
    checks["core_prompts_equal_recorded_requests"] = len(core_frozen)
    for response in records(results / "responses.jsonl.gz"):
        for row, request, gold in responses.pop(response["response_id"], []):
            parsed = parse(response["text"], request)
            selected = parsed.get("selected_tools", parsed.get("result", parsed.get("selected_entities")))
            selected += parsed.get("unknown_entities", [])
            actual = scores(selected, gold, row.get("metric_normalization"))
            for metric, value in actual.items():
                expected = row["metrics"].get(metric)
                if expected is not None and not math.isclose(
                    float(expected), float(value), rel_tol=1e-9, abs_tol=1e-9
                ):
                    raise ValueError(
                        "Archived score differs: "
                        + canonical([row["observation_id"], metric, expected, value])
                    )
            checks["archived_valid_selections_and_scores_equal"] += 1
    if responses:
        raise ValueError("Missing archived valid response")
    return {
        "status": "passed",
        "unique_task_population": dict(populations),
        "checks": dict(checks),
        "network_requests_made": 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    import json

    print(json.dumps(verify(args.results), ensure_ascii=False, indent=2))
