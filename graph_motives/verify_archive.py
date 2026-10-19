"""Independently verify checksums, links, panel sizes and scores of curated results."""
import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from .archive import records

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def hashed(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def gold_names(reference):
    if "expected_names" in reference:
        return reference["expected_names"]
    if "reference_names" in reference:
        return reference["reference_names"]
    private = reference.get("private", reference)
    if "graph_witness_ids" in private:
        return [private["name_map"][x] for x in private["graph_witness_ids"]]
    return private.get("reference_names")


def verify(results):
    manifest = json.loads((results / "MANIFEST.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = (results / entry["path"]).resolve()
        if not path.is_relative_to(results.resolve()) or path.stat().st_size != entry["bytes"] or sha(path) != entry["sha256"]:
            raise ValueError("File checksum mismatch: " + entry["path"])
    inputs, responses = {}, set()
    for row in records(results / "inputs.jsonl.gz"):
        key = row.pop("input_id")
        if key in inputs or hashed(row) != key:
            raise ValueError("Input identity mismatch")
        inputs[key] = {"gold": gold_names(row["reference"]), "question": row["question"],
                       "recorded_messages": row["messages"] is not None}
    for row in records(results / "responses.jsonl.gz"):
        key = row.pop("response_id")
        if key in responses or hashed(row) != key:
            raise ValueError("Response identity mismatch")
        responses.add(key)
    identities, counts, payloads = set(), Counter(), Counter()
    actual_requests = {}
    native_specs = {r["record_id"] for r in records(results / "task_specs_native.jsonl.gz")}
    if len(native_specs) != 700:
        raise ValueError("Native question specification coverage differs")
    recalculated = 0
    for row in records(results / "observations.jsonl.gz"):
        identity = [row["series_id"], row["model"], row["condition"], row["noise"], row["base_id"]]
        if hashed(identity) != row["observation_id"] or row["observation_id"] in identities:
            raise ValueError("Duplicate or changed planned observation")
        identities.add(row["observation_id"])
        counts[row["series_id"]] += 1
        if row["series_id"] == "native_d" and row["base_id"] not in native_specs:
            raise ValueError("A native question has no semantic specification")
        for stage in [row, *row.get("stages", [])]:
            if stage.get("input_id") and stage["input_id"] not in inputs:
                raise ValueError("Missing linked input")
            if stage.get("response_id") and stage["response_id"] not in responses:
                raise ValueError("Missing linked response")
        payloads["input_available" if row["input_id"] else "input_missing"] += 1
        payloads["response_available" if row["response_id"] else "response_missing"] += 1
        payloads["question_available" if row["question"] else "question_missing"] += 1
        if row["request_evidence"] == "recorded_api_journal":
            actual_requests.setdefault(row["input_id"], []).append((row["request_metadata"], row["request_id"]))
        if row["input_id"] and inputs[row["input_id"]]["question"] != row["question"]:
            raise ValueError("Question differs from input")
        if row["valid"] and row["selected_names"] is not None and row["input_id"]:
            gold = inputs[row["input_id"]]["gold"]
            if gold is None:
                raise ValueError("Missing expected names for a received valid response")
            if row.get("metric_normalization") == "whitespace_casefold":
                def normalize(value):
                    return " ".join(value.split()).casefold()
                expected, selected = set(map(normalize, gold)), set(map(normalize, row["selected_names"]))
            else:
                expected, selected = set(gold), set(row["selected_names"])
            tp, fp, fn = len(selected & expected), len(selected - expected), len(expected - selected)
            actual = {"precision": tp / len(selected) if selected else 0,
                      "recall": tp / len(expected) if expected else 1,
                      "f1": 2 * tp / (2 * tp + fp + fn) if selected or expected else 1,
                      "exact": selected == expected, "fp": fp, "fn": fn}
            for metric, value in actual.items():
                saved = row["metrics"][metric]
                if saved is not None and not math.isclose(float(saved), float(value), abs_tol=1e-9, rel_tol=1e-9):
                    raise ValueError(f"Individual score differs: {row['observation_id']} {metric}: {saved} != {value}")
            recalculated += 1
        if not row["valid"] and any(value is not None for value in row["metrics"].values()):
            raise ValueError("Invalid per-task metrics must retain null")
        if row["response_evidence"] == "metrics_cache_only_no_raw_response" and row["response_id"] is not None:
            raise ValueError("A missing historical response was filled in")
    expected_counts = {"core": 27300, "size": 2200, "calibration": 400,
                       "incremental": 700, "native_d": 6288, "full_braw": 20400, "legacy": 2800}
    if dict(counts) != expected_counts or len(identities) != 60088:
        raise ValueError("Paper panel coverage differs")
    if len(inputs) != manifest["counts"]["inputs"] or len(responses) != manifest["counts"]["responses"]:
        raise ValueError("Payload count differs")
    reconstructed = 0
    for row in records(results / "inputs.jsonl.gz"):
        for metadata, expected_id in actual_requests.pop(row["input_id"], []):
            messages = {x["role"]: x["content"] for x in row["messages"]}
            request = {**metadata, "system_prompt": messages["system"], "user_prompt": messages["user"],
                       "candidate_names": row["candidate_names"]}
            if hashed(request) != expected_id:
                raise ValueError("Original API request cannot be reconstructed exactly")
            reconstructed += 1
    if actual_requests or reconstructed != 31800:
        raise ValueError("Authenticated API request coverage differs")
    result = {"status": "passed", "observations": len(identities), "inputs": len(inputs), "responses": len(responses),
              "individual_scores_recomputed": recalculated, "series_counts": dict(counts), "payload_coverage": dict(payloads),
              "actual_requests_reconstructed": reconstructed,
              "native_question_specifications": len(native_specs),
              "network_requests_made": 0}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    print(json.dumps(verify(args.results), ensure_ascii=False, indent=2))
