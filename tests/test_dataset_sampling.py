"""Pilot sampling keeps graph variants paired and covers each calibration type."""

from collections import defaultdict

import pytest

from graph_motives import dataset


def test_graph_sampling_retains_conditions_noise_and_each_size(monkeypatch):
    rows = [
        dict(series_id=series, motif="chain", size=size, base_id=f"{size}-{base}",
             condition=condition, noise=noise, model="qwen3.6-flash")
        for series in ("core", "size")
        for size in (3, 6)
        for base in range(4)
        for condition in ("K1", "K2")
        for noise in ("adjacent", "disconnected")
    ]
    monkeypatch.setattr(dataset, "records", lambda _: iter(reversed(rows)))
    chosen = dataset.select_rows("unused", ("core", "size"), subgraphs_per_cell=2)
    by_graph = defaultdict(set)
    for row in chosen:
        by_graph[(row["series_id"], row["size"], row["base_id"])].add(
            (row["condition"], row["noise"])
        )
    assert len(chosen) == 32
    assert len(by_graph) == 8
    assert all(len(variants) == 4 for variants in by_graph.values())
    assert {key[2] for key in by_graph} == {"3-0", "3-1", "6-0", "6-1"}
    monkeypatch.setattr(dataset, "records", lambda _: iter(rows))
    assert dataset.select_rows("unused", ("core", "size"), subgraphs_per_cell=2) == chosen
    assert len(dataset.select_rows("unused", ("core", "size"))) == len(rows)


def test_calibration_sampling_covers_each_type_and_keeps_short_cells(monkeypatch):
    rows = [
        dict(series_id="calibration", motif=None, size=None, base_id=f"{condition}-{base}",
             condition=condition, noise="disconnected", model="qwen3.6-flash")
        for condition, count in (("CAL:text_edge", 4), ("CAL:keys_edge", 1))
        for base in range(count)
    ]
    monkeypatch.setattr(dataset, "records", lambda _: iter(rows))
    chosen = dataset.select_rows("unused", ("calibration",), subgraphs_per_cell=2)
    assert {row["base_id"] for row in chosen} == {
        "CAL:text_edge-0", "CAL:text_edge-1", "CAL:keys_edge-0",
    }
    assert dataset.select_rows("unused", ("calibration",), subgraphs_per_motif=2) == chosen


def test_motif_sample_spreads_total_across_sizes_and_preserves_pairs(monkeypatch):
    rows = [
        dict(series_id="full_braw", motif=motif, size=size, base_id=f"{motif}-{size}-{base}",
             condition=condition, noise=noise, model="qwen3.6-flash")
        for motif in ("chain", "star_in")
        for size in (3, 4, 5)
        for base in range(5)
        for condition in ("Braw", "Braw+E")
        for noise in ("adjacent", "disconnected")
    ]
    monkeypatch.setattr(dataset, "records", lambda _: iter(rows))
    chosen = dataset.select_rows("unused", ("full_braw",), subgraphs_per_motif=4)
    graphs = defaultdict(set)
    for row in chosen:
        graphs[row["motif"]].add(row["base_id"])
    assert len(chosen) == 32
    assert all(len(base_ids) == 4 for base_ids in graphs.values())
    assert {row["size"] for row in chosen} == {3, 4, 5}
    with pytest.raises(ValueError, match="Choose"):
        dataset.select_rows("unused", ("full_braw",), subgraphs_per_cell=2, subgraphs_per_motif=2)


@pytest.mark.parametrize("count", [0, -1, True, 1.5])
def test_invalid_sample_count_rejected(count):
    with pytest.raises(ValueError, match="subgraphs_per_cell"):
        dataset.select_rows("unused", ("core",), subgraphs_per_cell=count)
    with pytest.raises(ValueError, match="subgraphs_per_motif"):
        dataset.select_rows("unused", ("core",), subgraphs_per_motif=count)
