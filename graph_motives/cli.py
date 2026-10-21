"""Plan, run/resume and compare arbitrary models on the frozen article tasks."""

import argparse
import asyncio
import json
from pathlib import Path

from graph_motives.dataset import SERIES
from graph_motives.report import report
from graph_motives.runner import execute, freeze

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "run"):
        command = commands.add_parser(name, help="Freeze tasks" if name == "plan" else "Freeze and execute")
        command.add_argument("--config", type=Path, required=True)
        command.add_argument("--results", type=Path, default=ROOT / "results")
        command.add_argument("--output", type=Path, required=True)
        command.add_argument("--series", nargs="+", choices=(*SERIES, "all"), default=["core"])
        command.add_argument("--condition", action="append", default=[])
        command.add_argument("--motif", action="append", default=[])
        command.add_argument("--limit", type=int)
        sampling = command.add_mutually_exclusive_group()
        sampling.add_argument(
            "--subgraphs-per-cell", type=int,
            help="Base graphs per series/motif/size, retaining conditions/noise; calibration examples per type",
        )
        sampling.add_argument(
            "--subgraphs-per-motif", type=int,
            help="Base graphs per series/motif across sizes, retaining conditions/noise; calibration per type",
        )
        command.add_argument(
            "--mock", action="store_true", help="Offline transport only; never a scientific model result"
        )
        command.add_argument("--model", help="Override model ID; config is copied into the frozen run")
        command.add_argument("--alias", help="Override the result label")
        command.add_argument("--env-file", type=Path, action="append", default=[])
    command = commands.add_parser("execute", help="Execute or resume a frozen plan")
    command.add_argument("--run", type=Path, required=True)
    command.add_argument("--env-file", type=Path, action="append", default=[])
    command = commands.add_parser("report", help="Metrics and figures from one or more runs")
    command.add_argument("--run", type=Path, action="append", default=[])
    command.add_argument("--output", type=Path, required=True)
    command.add_argument("--historical", type=Path, help="Optional compact results directory for baselines")
    command.add_argument("--no-figures", action="store_true")
    command.add_argument("--series", nargs="+", choices=SERIES, default=[])
    command.add_argument("--model", action="append", default=[], help="Filter archived model aliases")
    command.add_argument("--condition", action="append", default=[])
    args = parser.parse_args()
    if getattr(args, "env_file", None):
        from dotenv import load_dotenv

        for path in args.env_file:
            if not path.is_file():
                parser.error("Missing env file: " + str(path))
            load_dotenv(path, override=False)
    if args.command in {"plan", "run"}:
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))
        if args.model:
            config["model"]["model"] = args.model
        if args.alias:
            config["model"]["alias"] = args.alias
        series = list(SERIES) if "all" in args.series else list(dict.fromkeys(args.series))
        result = freeze(
            args.results,
            args.output,
            config,
            series=series,
            conditions=args.condition,
            motifs=args.motif,
            limit=args.limit,
            subgraphs_per_cell=args.subgraphs_per_cell,
            subgraphs_per_motif=args.subgraphs_per_motif,
            mock=args.mock,
        )
        print(
            json.dumps(
                {"run_id": result["run_id"], "mode": result["mode"], "dataset": result["dataset"]}, indent=2
            )
        )
        if args.command == "run":
            print(json.dumps(asyncio.run(execute(args.output)), indent=2))
    elif args.command == "execute":
        print(json.dumps(asyncio.run(execute(args.run)), indent=2))
    else:
        print(
            json.dumps(
                report(args.run, args.output, historical=args.historical, figures=not args.no_figures,
                       series=args.series, models=args.model, conditions=args.condition),
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
