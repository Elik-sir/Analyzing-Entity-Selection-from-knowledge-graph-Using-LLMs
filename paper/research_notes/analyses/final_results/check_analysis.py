"""Meaningful numerical checks for the saved-results analysis and exports."""

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"

import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from uncertainty import bootstrap_means, percentile_interval, simultaneous_bands


def read(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def main(root, output):
    results = []
    # Shared bootstrap draws must preserve a constant paired difference.
    values = np.array([[0.1, 0.2], [0.2, 0.3], [0.3, 0.4], [0.4, 0.5]])
    for mode in ("anchor", "task"):
        samples, info = bootstrap_means(values, ["a"] * 4, ["x", "x", "y", "y"], replicates=512, seed=19, mode=mode)
        assert np.allclose(samples[:, 1] - samples[:, 0], 0.1, atol=1e-14)
        repeat, _ = bootstrap_means(values, ["a"] * 4, ["x", "x", "y", "y"], replicates=512, seed=19, mode=mode)
        assert np.array_equal(samples, repeat)
        results.append({"check": mode + "_pairing_and_seed_reproducibility", "status": "passed"})
    # Whole strata may disappear under cluster sampling. Reject those draws;
    # original stratum weights must keep this deterministic estimator at 1/4.
    samples, info = bootstrap_means(np.array([[0.0], [0.0], [0.0], [1.0]]), ["a", "a", "a", "b"], ["x", "x", "y", "x"], replicates=512, seed=17, mode="anchor")
    assert np.allclose(samples, 0.25) and info["rejected_empty_stratum_draws"] > 0
    results.append({"check": "fixed_stratum_weights_and_empty_stratum_rejection", "status": "passed"})
    low, high, sd, band = simultaneous_bands([0.1], np.full((100, 1), 0.1))
    assert band["active_effects"] == 0 and np.allclose(low, high)
    results.append({"check": "degenerate_band_is_explicit", "status": "passed"})
    # Enumerate small finite universes to validate the random-k expectations.
    for n, g, k in ((5, 2, 3), (5, 2, 2), (6, 4, 2)):
        selections = list(itertools.combinations(range(n), k))
        gold = set(range(g))
        actual_f1 = np.mean([2 * len(set(s) & gold) / (k + g) for s in selections])
        actual_exact = np.mean([set(s) == gold for s in selections])
        assert math.isclose(actual_f1, 2 * k * g / (n * (k + g)), abs_tol=1e-14)
        assert math.isclose(actual_exact, 1 / math.comb(n, g) if k == g else 0, abs_tol=1e-14)
    results.append({"check": "analytical_random_baseline_matches_finite_enumeration", "status": "passed"})

    # Recompute all condition aggregates with math.fsum, independently of the
    # writer's grouping accumulator and without using its output as input data.
    sums, valid, count = defaultdict(lambda: defaultdict(list)), defaultdict(int), defaultdict(int)
    with gzip.open(root / "results/observations.jsonl.gz", "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            key = tuple(row[k] for k in ("series_id", "model", "condition", "noise"))
            count[key] += 1
            valid[key] += row["valid"]
            for name in ("precision", "recall", "f1", "exact"):
                sums[key][name].append(float(row["metrics"].get(name) or 0) if row["valid"] else 0.0)
    table = read(output / "condition_metrics.csv")
    assert sum(count.values()) == 60088 and len(count) == len(table)
    for row in table:
        key = tuple(row[k] for k in ("series_id", "model", "condition", "noise"))
        assert count[key] == int(row["N"]) and valid[key] == int(row["valid"])
        for name in ("precision", "recall", "f1", "exact"):
            assert math.isclose(math.fsum(sums[key][name]) / count[key], float(row[name]), abs_tol=1e-12)
    results.append({"check": "all_66_condition_groups_independently_recomputed", "status": "passed"})

    contrasts = read(output / "paired_contrasts.csv")
    main_rows = [r for r in contrasts if r["family"].startswith("main_")]
    assert len(main_rows) == 78
    for panel in ("core", "raw"):
        records = [r for r in contrasts if r["panel"] == panel]
        samples = np.load(output / (panel + "_bootstrap.npz"))
        intervals = percentile_interval(samples["anchor_effects"])
        low, high, sd, metadata = simultaneous_bands(samples["effect_estimates"], samples["anchor_effects"], panel_coverage=0.975)
        assert samples["anchor_effects"].shape == (10000, len(records))
        for index, row in enumerate(records):
            assert math.isclose(float(row["delta"]), float(row["right_mean"]) - float(row["left_mean"]), abs_tol=1e-14)
            for key, value in (("cluster_ci_low", intervals[0, index]), ("cluster_ci_high", intervals[1, index]), ("simultaneous_low", low[index]), ("simultaneous_high", high[index])):
                assert math.isclose(float(row[key]), value, abs_tol=1e-14)
    results.append({"check": "all_main_delta_intervals_and_bands_match_saved_draws", "status": "passed"})
    sources = json.loads((output / "figure_sources.json").read_text(encoding="utf-8"))
    figure_info = json.loads((output / "figure_provenance.json").read_text(encoding="utf-8"))
    for figure in sources:
        raw = read(output / figure["data_source"])
        assert all(row in raw for row in figure["rows"])
        for name, expected in figure["files"].items():
            path = Path(figure_info["figures"]) / name
            assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    results.append({"check": "all_figure_rows_and_asset_hashes_match_sources", "status": "passed"})
    record = {"status": "passed", "checks": results,
              "scope": "Software and numerical reproducibility checks; not an empirical coverage simulation or validation of anchor independence."}
    (output / "validation.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "checks": len(results)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--analysis", type=Path, required=True)
    args = parser.parse_args()
    main(args.root.resolve(), args.analysis.resolve())
