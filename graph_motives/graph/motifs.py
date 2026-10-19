"""Motif samplers adapted from AgentGraphBench build_kg_items.py (MIT).
Exact induced typed edges; deterministic sorted choices; full graph may be cyclic.
"""

from __future__ import annotations

import random
from typing import Any

from .graph import Graph, norm


def _ok(kg: Graph, ids: set[str], edges: set[tuple[str, str, str]]) -> bool:
    if any("dup_of" in kg.nodes[i] or kg.nodes[i].get("unnamed") for i in ids):
        return False
    names = {norm(kg.name(i)) for i in ids}
    return len(names) == len(ids) and kg.induced_edges(ids) == edges


def sample_chain(kg: Graph, size: int, rng: random.Random) -> dict[str, Any] | None:
    # Bounded simple-path walk, valid even when the full graph contains cycles.
    start = rng.choice(kg.cache["node_ids"])
    path = [start]
    edges = set()
    while len(path) < size:
        choices = [e for e in sorted(kg.out[path[-1]]) if e[2] not in path]
        if not choices:
            return None
        edge = rng.choice(choices)
        edges.add(edge)
        path.append(edge[2])
    if not _ok(kg, set(path), edges):
        return None
    return {
        "anchor": start,
        "ids": path,
        "edges": edges,
        "pattern": f"path:{kg.type(path[-1])}",
        "sink": path[-1],
    }


def sample_star(kg: Graph, size: int, rng: random.Random, *, direction: str) -> dict[str, Any] | None:
    adj = kg.out if direction == "out" else kg.inc
    key = ("star", direction, size)
    if key not in kg.cache:
        kg.cache[key] = [n for n in kg.nodes if len(adj[n]) >= size - 1]
    hubs = kg.cache[key]
    if not hubs:
        return None
    hub = rng.choice(hubs)
    leaves_e = rng.sample(sorted(adj[hub]), size - 1)
    edges = set(leaves_e)
    ids = {hub} | {e[2] if direction == "out" else e[0] for e in edges}
    if len(ids) != size or not _ok(kg, ids, edges):
        return None
    return {
        "anchor": hub,
        "ids": [hub] + sorted(ids - {hub}),
        "edges": edges,
        "pattern": f"{direction}:1",
    }


def sample_tree(kg: Graph, size: int, rng: random.Random, *, direction: str) -> dict[str, Any] | None:
    """Two-level tree: root, 2+ children, each child with 1+ grandchildren; size nodes."""
    adj = kg.out if direction == "out" else kg.inc
    nxt = (lambda e: e[2]) if direction == "out" else (lambda e: e[0])
    key = ("tree", direction)
    if key not in kg.cache:
        kg.cache[key] = [n for n in kg.nodes if sum(bool(adj[nxt(e)]) for e in adj[n]) >= 2]
    roots = kg.cache[key]
    if not roots:
        return None
    root = rng.choice(roots)
    child_edges = [e for e in sorted(adj[root]) if adj[nxt(e)]]
    if len(child_edges) < 2:
        return None
    n_children = rng.randint(2, min(len(child_edges), (size - 1) // 2))
    chosen = rng.sample(child_edges, n_children)
    ids = {root} | {nxt(e) for e in chosen}
    edges = set(chosen)
    budget = size - len(ids)
    if budget < n_children:
        return None
    # at least one grandchild per child, then fill
    pool: list[tuple[str, str, str]] = []
    for ce in chosen:
        child = nxt(ce)
        opts = [e for e in sorted(adj[child]) if nxt(e) not in ids]
        if not opts:
            return None
        e = rng.choice(opts)
        edges.add(e)
        ids.add(nxt(e))
        pool.extend(o for o in opts if o != e)
    rng.shuffle(pool)
    for e in pool:
        if len(ids) >= size:
            break
        if nxt(e) not in ids:
            edges.add(e)
            ids.add(nxt(e))
    if len(ids) != size or not _ok(kg, ids, edges):
        return None
    return {
        "anchor": root,
        "ids": [root] + sorted(ids - {root}),
        "edges": edges,
        "pattern": f"{direction}:2",
    }


def sample_rhombus(kg: Graph, size: int, rng: random.Random) -> dict[str, Any] | None:
    a = rng.choice(kg.cache["node_ids"])
    outs = sorted(kg.out[a])
    if len(outs) < 2:
        return None
    rng.shuffle(outs)
    for i in range(len(outs)):
        for j in range(i + 1, len(outs)):
            b, c = outs[i][2], outs[j][2]
            common = {e[2] for e in kg.out[b]} & {e[2] for e in kg.out[c]}
            common -= {a, b, c}
            if not common:
                continue
            d = rng.choice(sorted(common))
            eb = next(e for e in sorted(kg.out[b]) if e[2] == d)
            ec = next(e for e in sorted(kg.out[c]) if e[2] == d)
            edges = {outs[i], outs[j], eb, ec}
            ids = {a, b, c, d}
            if _ok(kg, ids, edges):
                return {"anchor": a, "ids": [a, b, c, d], "edges": edges, "pattern": "out:2"}
    return None


def sample_hourglass(kg: Graph, size: int, rng: random.Random) -> dict[str, Any] | None:
    if "hourglass" not in kg.cache:
        kg.cache["hourglass"] = [n for n in kg.nodes if len(kg.inc[n]) >= 2 and len(kg.out[n]) >= 2]
    mids = kg.cache["hourglass"]
    if not mids:
        return None
    m = rng.choice(mids)
    ins = rng.sample(sorted(kg.inc[m]), 2)
    outs = rng.sample(sorted(kg.out[m]), 2)
    edges = set(ins) | set(outs)
    ids = {m} | {e[0] for e in ins} | {e[2] for e in outs}
    if len(ids) != 5 or not _ok(kg, ids, edges):
        return None
    return {"anchor": m, "ids": [m] + sorted(ids - {m}), "edges": edges, "pattern": "both:1"}


def sample_cycle(kg, size, rng):
    start = rng.choice(kg.cache["node_ids"])
    path, edges = [start], set()
    while len(path) < size:
        choices = [e for e in sorted(kg.out[path[-1]]) if e[2] not in path]
        if not choices:
            return None
        e = rng.choice(choices)
        path.append(e[2])
        edges.add(e)
    closing = [e for e in sorted(kg.out[path[-1]]) if e[2] == start]
    if not closing:
        return None
    edges.add(rng.choice(closing))
    return (
        {"anchor": start, "ids": path, "edges": edges, "pattern": f"out:{size}"}
        if _ok(kg, set(path), edges)
        else None
    )


def sample_clique(kg, size, rng):
    """Explicit definition: complete bidirected graph, one typed edge per direction."""
    a = rng.choice(kg.cache["node_ids"])
    reciprocal = {e[2] for e in kg.out[a]} & {e[0] for e in kg.inc[a]} - {a}
    if len(reciprocal) < size - 1:
        return None
    ids = {a, *rng.sample(sorted(reciprocal), size - 1)}
    edges = kg.induced_edges(ids)
    if len(edges) != size * (size - 1):
        return None
    if {(s, t) for s, _, t in edges} != {(s, t) for s in ids for t in ids if s != t}:
        return None
    if not _ok(kg, ids, edges):
        return None
    return {"anchor": a, "ids": [a] + sorted(ids - {a}), "edges": edges, "pattern": "out:2"}


SAMPLERS = {
    "chain": sample_chain,
    "star_in": lambda kg, n, rng: sample_star(kg, n, rng, direction="in"),
    "star_out": lambda kg, n, rng: sample_star(kg, n, rng, direction="out"),
    "tree_in": lambda kg, n, rng: sample_tree(kg, n, rng, direction="in"),
    "tree_out": lambda kg, n, rng: sample_tree(kg, n, rng, direction="out"),
    "rhombus": sample_rhombus,
    "hourglass": sample_hourglass,
    "cycle": sample_cycle,
    "clique": sample_clique,
}


def validate_cell(motif, size):
    if motif not in SAMPLERS:
        raise ValueError(f"Unknown motif {motif}")
    minimum = 5 if motif.startswith("tree_") else 3
    if motif == "rhombus" and size != 4 or motif == "hourglass" and size != 5:
        raise ValueError("Rhombus requires size 4; hourglass requires size 5")
    if size < minimum or size > 30:
        raise ValueError(f"Invalid size {size} for {motif}; expected {minimum}..30")
