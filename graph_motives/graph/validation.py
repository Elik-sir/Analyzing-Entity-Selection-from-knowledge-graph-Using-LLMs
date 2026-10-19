"""Independent structural checks. No claim of node-only answerability."""

import re
from collections import Counter

from .derive import derive_answer
from .graph import norm
from .metadata import validate_public_node
from .models import Item


def check_item(item: dict, candidate_size: int | None = None) -> list[str]:
    try:
        Item.model_validate(item)
    except ValueError:
        return ["schema"]
    public, hidden = item["public"], item["private"]
    names = [n["name"] for n in public["candidates"]]
    types = {n["name"]: n["type"] for n in public["candidates"]}
    ref = set(hidden["reference_names"])
    gold_e = set(hidden["answer"]["entities"])
    gold_r = {tuple(e) for e in hidden["answer"]["relations"]}
    rels = {tuple(e) for e in hidden["context_relations"]}
    errors = []
    if len(set(map(norm, names))) != len(names):
        errors.append("duplicate_names")
    if candidate_size is not None and len(names) != candidate_size:
        errors.append("candidate_size")
    if (
        len(ref) != item["size"]
        or len(hidden["reference_ids"]) != item["size"]
        or ref != gold_e
        or not ref <= set(names)
    ):
        errors.append("reference_mismatch")
    if any(s not in names or t not in names for s, _, t in rels):
        errors.append("dangling_context_edge")
    count = Counter(types.values())
    anchor = hidden["anchor"]
    if anchor not in ref:
        errors.append("anchor")
    if any(count[types.get(n)] < 2 for n in ref - {anchor}):
        errors.append("type_unique")
    try:
        derived = derive_answer(anchor, hidden["pattern"], set(names), rels, types)
    except (ValueError, KeyError, RecursionError):
        return errors + ["invalid_pattern"]
    if derived != (gold_e, gold_r):
        errors.append("not_derivable")
    else:
        for n in ref:  # include the anchor too
            if derive_answer(anchor, hidden["pattern"], set(names) - {n}, rels, types) == derived:
                errors.append("not_necessary")
                break
    q = norm(public["question"])
    if any(re.search(r"(?<!\w)" + re.escape(norm(n)) + r"(?!\w)", q) for n in ref - {anchor}):
        errors.append("verbatim")
    if not all(validate_public_node(n) for n in public["candidates"]):
        errors.append("structural_metadata")
    return errors
