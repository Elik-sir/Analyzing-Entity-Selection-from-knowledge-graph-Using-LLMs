"""Inspect one archived diamond to distinguish route coverage from card necessity."""

import copy
import json
from pathlib import Path

from audit_references import decode, digest, oracle, rows, template_grammar


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "results/MANIFEST.json").is_file())
selected = next(r for r in rows(ROOT / "results/observations.jsonl.gz")
                if r["series_id"] == "core" and r["model"] == "qwen3.6-flash"
                and r["condition"] == "K1" and r["motif"] == "rhombus")
payload = next(p for p in rows(ROOT / "results/inputs.jsonl.gz") if p["input_id"] == selected["input_id"])
public = payload.get("frozen_public") or json.loads(next(m["content"] for m in payload["messages"] if m["role"] == "user"))
private = payload["reference"]["private"]
names = private["name_map"]
ids = private["candidate_ids"]
types = {nid: c["type"] for nid, c in zip(ids, public["candidates"])}
grammar = template_grammar(ROOT)
edges, _, _ = decode(public["candidates"], names, "explicit", grammar)
endpoints, witnesses, routes = oracle(private["task_spec"], edges, ids, types)
ablations = []
for nid, card in zip(ids, public["candidates"]):
    if nid not in witnesses:
        continue
    cards = copy.deepcopy(public["candidates"])
    cards[ids.index(nid)]["facts"] = {}
    remaining, _, _ = decode(cards, names, "explicit", grammar)
    found, _, _ = oracle(private["task_spec"], remaining, ids, types)
    ablations.append({"removed_card_name": card["name"], "original_endpoint_answer_preserved": found == endpoints,
                      "answer_after_removal": sorted(names[v] for v in found)})
result = {"scope": "One recorded K1 rhombus, not a population-wide card-necessity estimate or model experiment.",
          "input_id": payload["input_id"], "observation_id": selected["observation_id"],
          "selector": {k: selected[k] for k in ("series_id", "model", "condition", "noise", "base_id", "motif")},
          "question": public["question"], "reference_names": sorted(names[n] for n in private["graph_witness_ids"]),
          "endpoint_names": sorted(names[n] for n in endpoints), "witness_names": sorted(names[n] for n in witnesses),
          "support_routes": routes, "reference_induced_edges": [[names[s], r, names[t]] for s, r, t in sorted(edges) if s in witnesses and t in witnesses],
          "single_card_fact_ablations": ablations,
          "policy": "Remove only one card's facts; keep the full name/type catalogue available.",
          "interpretation": "The archived reference is all-route entity coverage, not a minimal indispensable-card set."}
(HERE / "support_example.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"input_id": payload["input_id"], "witnesses": len(witnesses), "endpoints": len(endpoints), "support_routes": routes,
                  "card_ablations_preserving_answer": sum(r["original_endpoint_answer_preserved"] for r in ablations)}))
