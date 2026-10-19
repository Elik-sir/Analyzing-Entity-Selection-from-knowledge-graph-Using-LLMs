"""Regression checks for shared archive reporting and graph preparation."""

import csv
import gzip
import json
from pathlib import Path

import pytest

from graph_motives.common import file_sha
from graph_motives.graph.build import build_dataset
from graph_motives.graph.demo import make_demo_graph
from graph_motives.graph.graph import load_graph, load_snapshot
from graph_motives.graph.io_utils import load_config, read_jsonl
from graph_motives.graph.validation import check_item
from graph_motives.report import report
from graph_motives.verify_code import verify

ROOT = Path(__file__).resolve().parents[1]


def test_current_package_has_no_duplicate_modules_or_obsolete_snapshots():
    assert verify()["duplicate_modules"] == 0


def test_single_graph_loader_supports_sampler_and_preparation(tmp_path):
    graph = tmp_path / "graph.json"
    make_demo_graph(graph)
    config = load_config(ROOT / "configs/dataset.toml")
    config["sampling"].update(cells=["chain:3", "rhombus:4", "hourglass:5"], per_cell=2)
    sampled_graph = load_graph(graph, config)
    prepared_graph = load_snapshot(graph, config["ingestion"])
    assert sampled_graph.fingerprint() == prepared_graph.fingerprint()
    assert set(sampled_graph.cache["node_ids"]) == set(sampled_graph.name_to_id.values())
    result = build_dataset(graph, config, tmp_path / "items")
    assert result["totals"] == {"disconnected": 6, "adjacent": 6}
    for noise in result["totals"]:
        assert all(not check_item(row, 25) for row in read_jsonl(tmp_path / f"items/items_{noise}.jsonl.gz"))


def test_archive_report_retains_failures_and_filters_without_model_plan(tmp_path):
    archive = tmp_path / "archive"
    archive.mkdir()
    rows = [
        {"series_id": "core", "condition": "K1", "noise": "disconnected", "base_id": str(index),
         "model": "model-a", "motif": "chain", "size": 6, "status": "completed" if index == 0 else "error",
         "valid": index == 0, "metrics": {name: 1.0 if index == 0 else None for name in
                                           ("recall", "precision", "f1", "exact")}}
        for index in range(2)
    ]
    with gzip.open(archive / "observations.jsonl.gz", "wt", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row) + "\n")
    (archive / "MANIFEST.json").write_text(json.dumps({"files": [
        {"path": "observations.jsonl.gz", "sha256": file_sha(archive / "observations.jsonl.gz")}
    ]}), encoding="utf-8")
    destination = tmp_path / "report"
    result = report([], destination, historical=archive, figures=True, series=["core"], models=["model-a"])
    assert result["observations"] == 2
    assert result["selection"] == {"series": ["core"], "models": ["model-a"], "conditions": []}
    assert len(result["figures"]) == 6
    with (destination / "conditions.csv").open(encoding="utf-8", newline="") as stream:
        cell = next(csv.DictReader(stream))
    assert (int(cell["N"]), int(cell["valid"])) == (2, 1)
    assert all(float(cell[name]) == 0.5 for name in ("recall", "precision", "f1", "exact"))
    with pytest.raises(ValueError, match="No observations"):
        report([], tmp_path / "empty", historical=archive, figures=False, models=["unknown"])
