"""Motifs -> paired node-only datasets with private graph ground truth."""

from __future__ import annotations

import random
from collections import Counter
from pathlib import Path

from .derive import derive_answer
from .graph import Graph, load_graph
from .io_utils import digest, write_json, write_jsonl
from .metadata import public_node
from .motifs import SAMPLERS, validate_cell
from .questions import make_question
from .validation import check_item


def name_edges(kg, edges):
    return sorted([kg.name(s), r, kg.name(t)] for s, r, t in edges)


def derive_ids(kg, motif, ids):
    return derive_answer(
        kg.name(motif["anchor"]),
        motif["pattern"],
        {kg.name(n) for n in ids},
        {tuple(e) for e in name_edges(kg, kg.induced_edges(set(ids)))},
        {kg.name(n): kg.type(n) for n in ids},
    )


def pick_adjacent(kg: Graph, m, rng, limit):
    """Admit a neighbour only when ALL induced edges leave the oracle unchanged."""
    ref = set(m["ids"])
    gold = ({kg.name(i) for i in ref}, {tuple(e) for e in name_edges(kg, m["edges"])})
    pool = sorted(set().union(*(kg.neighbours(i) for i in ref)) - ref)
    rng.shuffle(pool)
    chosen = []
    for nid in pool:
        if len(chosen) >= limit:
            break
        if "dup_of" in kg.nodes[nid] or kg.nodes[nid].get("unnamed"):
            continue
        if derive_ids(kg, m, ref | set(chosen) | {nid}) == gold:
            chosen.append(nid)
    return chosen


def pick_decoys(kg, m, rng, total, adjacent):
    ref = set(m["ids"])
    chosen = list(adjacent)
    blocked = ref | set(adjacent) | set().union(*(kg.neighbours(i) for i in ref))
    motif_types = sorted({kg.type(i) for i in ref})
    pools = {t: [i for i in kg.by_type.get(t, []) if i not in blocked] for t in motif_types}
    for pool in pools.values():
        rng.shuffle(pool)

    def take(t):
        if pools[t] and len(ref) + len(chosen) < total:
            chosen.append(pools[t].pop())

    for t in motif_types:
        # A real same-type distractor, not merely another reference node.
        if not any(kg.type(i) == t for i in adjacent):
            take(t)
    while len(ref) + len(chosen) < total:
        available = [t for t in motif_types if pools[t]]
        if not available:
            break
        take(rng.choice(available))
    return chosen


def build_item(kg, motif, m, config, variant, rng, graph_hash):
    cfg = config["sampling"]
    total = int(cfg.get("candidate_size", 25))
    n_adj = (
        min(int(cfg.get("adjacent_max", 10)), total - len(m["ids"])) if variant == "adjacent" else 0
    )
    adj = pick_adjacent(kg, m, rng, n_adj)
    decoys = pick_decoys(kg, m, rng, total, adj)
    ids = list(m["ids"]) + decoys
    rng.shuffle(ids)
    reference = [kg.name(i) for i in m["ids"]]
    identity = {
        "graph": graph_hash,
        "motif": motif,
        "nodes": sorted(m["ids"]),
        "edges": sorted(m["edges"]),
        "anchor": m["anchor"],
        "pattern": m["pattern"],
    }
    return {
        "record_id": digest(identity)[:24],
        "variant": variant,
        "subgraph_type": motif,
        "size": len(m["ids"]),
        "protocol": "nodes_only_text_answer_v2",
        "graph_hash": graph_hash,
        "config_hash": digest(
            {k: config.get(k, {}) for k in ("sampling", "metadata", "ingestion")}
        ),
        "public": {
            "question": make_question(kg, motif, m),
            "candidates": [public_node(kg, nid, config) for nid in ids],
        },
        "private": {
            "anchor": kg.name(m["anchor"]),
            "pattern": m["pattern"],
            "reference_names": reference,
            "reference_ids": list(m["ids"]),
            "answer": {"entities": reference, "relations": name_edges(kg, m["edges"])},
            "context_relations": name_edges(kg, kg.induced_edges(set(ids))),
            "adjacent_names": [kg.name(i) for i in adj],
        },
    }


def build_dataset(graph_path: Path, config: dict, out_dir: Path):
    kg = load_graph(graph_path, config)
    cfg = config["sampling"]
    variants = cfg.get("variants", ["disconnected", "adjacent"])
    if not variants or set(variants) - {"disconnected", "adjacent"}:
        raise ValueError("variants must contain disconnected and/or adjacent")
    seed, per_cell = int(cfg.get("seed", 0)), int(cfg.get("per_cell", 100))
    total = int(cfg.get("candidate_size", 25))
    if per_cell < 1 or int(cfg.get("max_tries", 20000)) < 1:
        raise ValueError("per_cell and max_tries must be positive")
    output = {v: [] for v in variants}
    summary = {
        "graph": kg.summary(),
        "config": {k: config.get(k, {}) for k in ("sampling", "metadata", "ingestion")},
        "validation_scope": "hidden graph consistency; metadata answerability is NOT established",
        "cells": [],
        "protocol": "nodes_only_text_answer_v2",
    }
    graph_hash = summary["graph"]["graph_hash"]
    cells = [(c.split(":")[0], int(c.split(":")[1])) for c in cfg["cells"]]
    if len(set(cells)) != len(cells):
        raise ValueError("Duplicate motif:size cells")
    for motif, size in cells:
        validate_cell(motif, size)
        if total <= size:
            raise ValueError("candidate_size must exceed motif size")
        rng = random.Random(int(digest([seed, motif, size])[:16], 16))
        seen, anchors, accepted = set(), Counter(), Counter()
        reasons = {v: Counter() for v in variants}
        tries = sampled = 0
        while accepted[variants[0]] < per_cell and tries < int(cfg.get("max_tries", 20000)):
            tries += 1
            m = SAMPLERS[motif](kg, size, rng)
            if m is None:
                continue
            key = (tuple(sorted(m["ids"])), m["anchor"])
            if key in seen or anchors[m["anchor"]] >= int(cfg.get("max_per_anchor", 2)):
                continue
            seen.add(key)
            sampled += 1
            # Independent variant RNG: generating another condition cannot change the baseline.
            base = build_item(
                kg,
                motif,
                m,
                config,
                variants[0],
                random.Random(digest([seed, key, variants[0]])),
                graph_hash,
            )
            bad = check_item(base, total)
            if bad:
                reasons[variants[0]].update(bad)
                continue
            output[variants[0]].append(base)
            accepted[variants[0]] += 1
            anchors[m["anchor"]] += 1
            for variant in variants[1:]:
                item = build_item(
                    kg,
                    motif,
                    m,
                    config,
                    variant,
                    random.Random(digest([seed, key, variant])),
                    graph_hash,
                )
                bad = check_item(item, total)
                if bad:
                    reasons[variant].update(bad)
                else:
                    output[variant].append(item)
                    accepted[variant] += 1
        summary["cells"].append(
            {
                "motif": motif,
                "size": size,
                "attempts": tries,
                "sampled": sampled,
                "requested": per_cell,
                "accepted": dict(accepted),
                "rejected": {v: dict(r) for v, r in reasons.items()},
            }
        )
    out_dir = Path(out_dir)
    for variant, rows in output.items():
        write_jsonl(out_dir / f"items_{variant}.jsonl.gz", rows)
        # Public export contains no node IDs, gold labels, motif labels or graph edges.
        write_jsonl(
            out_dir / f"public_{variant}.jsonl",
            [{"record_id": r["record_id"], **r["public"]} for r in rows],
        )
    summary["totals"] = {v: len(rows) for v, rows in output.items()}
    write_json(out_dir / "acceptance.json", summary)
    return summary
