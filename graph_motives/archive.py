"""Streaming access to the curated article results; no original checkout required."""
import argparse
import json
from pathlib import Path

from .common import records

DEFAULT_RESULTS = Path(__file__).resolve().parents[1] / "results"


def observations(results=DEFAULT_RESULTS, *, series=None, model=None, condition=None):
    """One row per planned model/task/condition, including invalid outcomes."""
    for row in records(Path(results) / "observations.jsonl.gz"):
        if series is not None and row["series_id"] != series:
            continue
        if model is not None and row["model"] != model:
            continue
        if condition is not None and row["condition"] != condition:
            continue
        yield row


def payload(results, table, key):
    if key is None:
        return None
    field = "input_id" if table == "inputs" else "response_id"
    for row in records(Path(results) / (table + ".jsonl.gz")):
        if row[field] == key:
            return row
    raise KeyError(key)


def with_payloads(row, results=DEFAULT_RESULTS):
    """Resolve one row without loading every long prompt into memory."""
    return {**row, "input": payload(results, "inputs", row["input_id"]),
            "response": payload(results, "responses", row["response_id"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--series")
    parser.add_argument("--model")
    parser.add_argument("--condition")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--with-payloads", action="store_true")
    args = parser.parse_args()
    from itertools import islice
    for row in islice(observations(args.results, series=args.series, model=args.model, condition=args.condition), args.limit):
        print(json.dumps(with_payloads(row, args.results) if args.with_payloads else row, ensure_ascii=False))


if __name__ == "__main__":
    main()
