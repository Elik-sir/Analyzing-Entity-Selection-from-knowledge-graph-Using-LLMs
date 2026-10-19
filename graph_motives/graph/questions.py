"""Deterministic cover questions; no LLM or outside graph access in generation."""


def make_question(kg, motif, m):
    anchor = kg.name(m["anchor"])
    a = f"the {kg.type(m['anchor'])} '{anchor}'"
    if motif == "chain":
        body = f"Starting from {a}, follow outgoing links until the first {kg.type(m['sink'])} on each path."
    elif motif == "star_in":
        body = f"Which entities link directly to {a}?"
    elif motif == "star_out":
        body = f"Which entities does {a} link to directly?"
    elif motif == "tree_in":
        body = f"Which entities are within two incoming links of {a} (its direct predecessors and theirs)?"
    elif motif in ("tree_out", "rhombus", "clique"):
        body = (
            f"Which entities are within two outgoing links of {a} (its direct targets and theirs)?"
        )
    elif motif == "hourglass":
        body = f"Which entities link directly to {a}, and which does it link to directly?"
    elif motif == "cycle":
        body = f"Which entities can be reached within {len(m['ids'])} outgoing links of {a}?"
    else:
        raise ValueError(motif)
    return (
        body + f" Include '{anchor}' itself. Consider only the provided candidates. "
        "Answer the question in natural language, explaining what the descriptions support. "
        "The underlying links are hidden; use the node descriptions as evidence."
    )
