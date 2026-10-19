"""Synthetic finance-shaped graph with every supported motif; no real S&P data."""

from .io_utils import write_json


def make_demo_graph(path, copies=8):
    nodes, edges = [], []

    def add_node(nid, typ, name):
        nodes.append(
            {
                "id": nid,
                "labels": [typ, "Searchable"],
                "properties": {
                    "name": name,
                    "summary": f"Synthetic {typ.lower()} for offline testing.",
                    "internal_id": nid,
                    "tags": ["synthetic", "demo"],
                },
            }
        )

    def edge(s, r, t):
        edges.append({"source": s, "relation": r, "target": t})

    for i in range(copies):
        for suffix, typ in [
            ("news", "News"),
            ("fund", "Fund"),
            ("fund2", "Fund"),
            ("company", "Company"),
            ("company2", "Company"),
            ("person", "Person"),
            ("city", "City"),
            ("state", "State"),
            ("country", "Country"),
            ("product", "Product"),
            ("product2", "Product"),
            ("resource", "Resource"),
        ]:
            add_node(f"{i}-{suffix}", typ, f"Demo {suffix.title()} {i}")
        for s, r, t in [
            ("news", "ABOUT", "fund"),
            ("fund", "OWNS", "company"),
            ("fund", "OWNS", "company2"),
            ("fund2", "OWNS", "company2"),
            ("person", "WORKS_FOR", "company"),
            ("company", "LOCATED_IN", "city"),
            ("company2", "LOCATED_IN", "city"),
            ("city", "IN_STATE", "state"),
            ("state", "IN_COUNTRY", "country"),
            ("company", "PRODUCES", "product"),
            ("company2", "PRODUCES", "product2"),
            ("company", "USES", "resource"),
        ]:
            edge(f"{i}-{s}", r, f"{i}-{t}")
        for j in range(5):
            nid = f"{i}-investor-{j}"
            add_node(nid, "Fund", f"Demo Investor {i} {j}")
            edge(nid, "OWNS", f"{i}-company")
        # Separate cyclic components ensure chain sampling is not DAG-dependent.
        for kind in ("cycle", "clique"):
            ids = [f"{i}-{kind}-{j}" for j in range(3)]
            for j, nid in enumerate(ids):
                add_node(nid, "Company", f"Demo {kind.title()} {i} Member {j}")
            if kind == "cycle":
                for j in range(3):
                    edge(ids[j], "PARTNER", ids[(j + 1) % 3])
            else:
                for s in ids:
                    for t in ids:
                        if s != t:
                            edge(s, "PARTNER", t)
    write_json(path, {"nodes": nodes, "edges": edges})
