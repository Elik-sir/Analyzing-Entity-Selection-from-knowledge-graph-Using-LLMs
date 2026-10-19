"""Hidden-graph oracle, adapted from check_kg_items.py (MIT).
This validates graph ground truth, NOT answerability from node-only metadata.
"""

from __future__ import annotations


def _paths_to_type(
    anchor: str,
    sink_type: str,
    out: dict[str, list[tuple[str, str, str]]],
    types: dict[str, str],
) -> tuple[set[str], set[tuple[str, str, str]]]:
    """Nodes and edges on every directed path from `anchor` that ends at the first
    node of `sink_type` it meets (the chain question: follow the links until a
    <sink type>). Branches that never reach the type contribute nothing."""
    seen: set[str] = set()
    used: set[tuple[str, str, str]] = set()

    def walk(node: str, path_nodes: list[str], path_edges: list[tuple[str, str, str]]) -> None:
        if node != anchor and types.get(node) == sink_type:
            seen.update(path_nodes)
            used.update(path_edges)
            return
        for e in out.get(node, []):
            if e[2] in path_nodes:
                continue
            walk(e[2], path_nodes + [e[2]], path_edges + [e])

    walk(anchor, [anchor], [])
    return seen, used


def derive_answer(
    anchor: str,
    pattern: str,
    entities: set[str],
    relations: set[tuple[str, str, str]],
    types: dict[str, str] | None = None,
) -> tuple[set[str], set[tuple[str, str, str]]]:
    """Entities and relations the pattern reaches from `anchor` inside the context."""
    out: dict[str, list[tuple[str, str, str]]] = {}
    inc: dict[str, list[tuple[str, str, str]]] = {}
    for s, r, t in relations:
        if s in entities and t in entities:
            out.setdefault(s, []).append((s, r, t))
            inc.setdefault(t, []).append((s, r, t))
    if anchor not in entities:
        return set(), set()
    kind, _, depth_s = pattern.partition(":")
    if kind == "path" and depth_s:
        return _paths_to_type(anchor, depth_s, out, types or {})
    depth = int(depth_s) if depth_s else 10**6
    if kind == "path":
        kind, depth = "out", 10**6
    dirs = {"out": [out], "in": [inc], "both": [out, inc]}[kind]
    seen = {anchor}
    used: set[tuple[str, str, str]] = set()
    frontier = [anchor]
    for _ in range(depth):
        nxt: list[str] = []
        for n in frontier:
            for adj in dirs:
                for s, r, t in adj.get(n, []):
                    used.add((s, r, t))
                    other = t if s == n else s
                    if other not in seen:
                        seen.add(other)
                        nxt.append(other)
        if not nxt:
            break
        frontier = nxt
    return seen, used
