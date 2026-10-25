"""Paired, fixed-stratum-weight bootstrap for saved task scores."""

import numpy as np


def bootstrap_means(values, strata, clusters, *, replicates, seed, mode, batch=128):
    """Resample joint score columns; preserve original motif-size weights.

    Cluster draws sample G anchors G times over the whole panel. Cell means are
    ratios under those shared weights, then recombined with original cell N/N.
    Task draws sample n_s tasks n_s times independently within each cell.
    """
    values = np.asarray(values, dtype=float)
    strata = np.asarray(strata)
    clusters = np.asarray(clusters)
    unique_strata, cell = np.unique(strata, return_inverse=True)
    unique_clusters, group = np.unique(clusters, return_inverse=True)
    n, dimensions = values.shape
    sizes = np.bincount(cell)
    fixed_weights = sizes / n
    rng = np.random.default_rng(seed)
    result = np.empty((replicates, dimensions), dtype=float)
    rejected = 0
    if mode == "anchor":
        g, k = len(unique_clusters), len(unique_strata)
        sums = np.zeros((g, k, dimensions), dtype=float)
        counts = np.zeros((g, k), dtype=float)
        np.add.at(sums, (group, cell), values)
        np.add.at(counts, (group, cell), 1.0)
        filled = 0
        while filled < replicates:
            weights = rng.multinomial(g, np.full(g, 1 / g), size=min(batch, replicates - filled))
            denominators = weights @ counts
            valid = np.all(denominators > 0, axis=1)
            rejected += int((~valid).sum())
            if rejected > max(10000, replicates):
                raise ValueError("Too many draws omit an entire stratum; revise the cluster design")
            weights, denominators = weights[valid], denominators[valid]
            if not len(weights):
                continue
            numerators = (weights @ sums.reshape(g, -1)).reshape(len(weights), k, dimensions)
            sampled = ((numerators / denominators[:, :, None]) * fixed_weights[None, :, None]).sum(axis=1)
            result[filled:filled + len(sampled)] = sampled
            filled += len(sampled)
    elif mode == "task":
        result[:] = 0
        for c, size in enumerate(sizes):
            subset = values[cell == c]
            for start in range(0, replicates, batch):
                count = min(batch, replicates - start)
                weights = rng.multinomial(int(size), np.full(size, 1 / size), size=count)
                result[start:start + count] += (weights @ subset) / n
    else:
        raise ValueError("Unknown bootstrap mode")
    if not np.isfinite(result).all():
        raise ValueError("Non-finite bootstrap result")
    return result, {"mode": mode, "replicates": replicates, "seed": seed,
                    "base_tasks": n, "anchor_clusters": len(unique_clusters),
                    "strata": len(unique_strata), "rejected_empty_stratum_draws": rejected,
                    "stratum_counts": dict(zip(unique_strata.tolist(), sizes.tolist()))}


def percentile_interval(samples):
    return np.quantile(samples, [0.025, 0.975], axis=0, method="linear")


def simultaneous_bands(estimates, samples, *, panel_coverage=0.975):
    """Centered max-standardized-deviation band; fixed bootstrap SD per effect."""
    estimates = np.asarray(estimates)
    sd = np.std(samples, axis=0, ddof=1)
    active = sd > 1e-12
    if active.any():
        maximum = np.max(np.abs((samples[:, active] - estimates[active]) / sd[active]), axis=1)
        critical = float(np.quantile(maximum, panel_coverage, method="linear"))
    else:
        critical = 0.0
    low, high = estimates - critical * sd, estimates + critical * sd
    return low, high, sd, {"coverage": panel_coverage, "critical_value": critical,
                          "effects": len(estimates), "active_effects": int(active.sum()),
                          "degenerate_effects": int((~active).sum()),
                          "method": "centered bootstrap maximum absolute deviation / fixed bootstrap SD"}
