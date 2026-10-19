"""Export, inspect, sample, and validate graph datasets without model calls."""

import argparse
import json
from pathlib import Path

from .build import build_dataset
from .demo import make_demo_graph
from .graph import load_graph
from .io_utils import load_config, load_env_file, read_jsonl
from .neo4j_export import export_neo4j
from .validation import check_item

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/dataset.toml")
    parser.add_argument("--env-file", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "sample"):
        sub = commands.add_parser(command)
        sub.add_argument("--graph", type=Path, required=True)
        if command == "sample":
            sub.add_argument("--output", type=Path, required=True)
    for command in ("export", "demo"):
        commands.add_parser(command).add_argument("--output", type=Path, required=True)
    commands.add_parser("check").add_argument("--items", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.env_file:
        load_env_file(args.env_file)
    if getattr(args, "output", None) and args.output.exists():
        parser.error("Choose a new output path; existing datasets are not overwritten")
    if args.command == "sample":
        result = build_dataset(args.graph, config, args.output)
    elif args.command == "export":
        result = export_neo4j(args.output, config)
    elif args.command == "demo":
        make_demo_graph(args.output)
        result = {"output": str(args.output), "synthetic": True}
    elif args.command == "inspect":
        result = load_graph(args.graph, config).summary()
    else:
        rows = read_jsonl(args.items)
        failures = [
            {"record_id": row.get("record_id"), "errors": errors}
            for row in rows
            if (errors := check_item(row, config["sampling"]["candidate_size"]))
        ]
        result = {"records": len(rows), "invalid": failures}
        if failures:
            print(json.dumps(result, indent=2))
            return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
