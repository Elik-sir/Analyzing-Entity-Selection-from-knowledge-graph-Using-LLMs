"""Audit native semantic goals and protocol-specific pairing of saved inputs."""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from audit_references import digest, file_hash, rows


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "results/MANIFEST.json").is_file())
MARKER = "\n\nExplicit directed links (source, relation, target):\n"


def native_cards(user, names):
    starts = []
    types, metadata = {}, []
    for index, name in enumerate(names, 1):
        pattern = re.compile(r"^" + str(index) + r"\. " + re.escape(name) + r" -- ([^.\n]+)\. ", re.M)
        match = pattern.search(user)
        if match is None:
            raise ValueError("Cannot identify native card " + str(index))
        starts.append((match.start(), match.end()))
        types[name] = match.group(1)
    end = user.find(MARKER)
    if end == -1:
        end = user.rfind("\n\nRespond with the JSON object only.")
    for i, (_, content) in enumerate(starts):
        stop = starts[i + 1][0] - 1 if i + 1 < len(starts) else end
        metadata.append(user[content:stop])
    return types, metadata


def native_witnesses(spec, edges, types):
    """Execute saved typed/relation-constrained goal paths without an LLM."""
    witnesses, path_count, missing_goals = set(), 0, []
    anchor = spec["anchor_name"]
    for goal_index, goal in enumerate(spec["goals"]):
        paths = [(anchor,)]
        for step in goal:
            extended = []
            for path in paths:
                for source, relation, target in edges:
                    if relation != step["relation"]:
                        continue
                    a, b = (source, target) if step["direction"] == "out" else (target, source)
                    if a == path[-1] and b not in path and types.get(b) == step["target_type"]:
                        extended.append((*path, b))
            paths = extended
        if not paths:
            missing_goals.append(goal_index)
        path_count += len(paths)
        witnesses.update(v for path in paths for v in path)
    return witnesses, path_count, missing_goals


def main():
    observations = defaultdict(list)
    for row in rows(ROOT / "results/observations.jsonl.gz"):
        if row["series_id"] in {"native_d", "legacy", "full_braw"}:
            observations[row["input_id"]].append({k: row[k] for k in ("series_id", "model", "condition", "noise", "base_id", "observation_id")})
    specs = {r["record_id"]: r for r in rows(ROOT / "results/task_specs_native.jsonl.gz")}
    native, legacy, failures, counts = {}, {}, [], Counter()
    for payload in rows(ROOT / "results/inputs.jsonl.gz"):
        meta = observations.get(payload["input_id"], [])
        if not meta:
            continue
        info = meta[0]
        public = json.loads(payload["messages"][1]["content"]) if info["series_id"] != "native_d" else None
        if info["series_id"] == "full_braw":
            if info["condition"] == "Braw":
                count = sum(len(c.get("facts", {}).get("relations", [])) for c in public["candidates"])
                counts["raw_baseline_inputs_checked_for_explicit_relations"] += 1
                if count:
                    failures.append({"code": "raw_baseline_has_explicit_relation", "input_id": payload["input_id"]})
            continue
        reference = payload["reference"]
        if info["series_id"] == "legacy":
            record = {"input_id": payload["input_id"], "question": payload["question"],
                      "reference": digest(sorted(reference["reference_names"])),
                      "pattern": reference["pattern"], "anchor": reference["anchor"],
                      "system": digest(payload["messages"][0]["content"])}
            for observation in meta:
                key = (observation["model"], observation["noise"], observation["base_id"])
                if key in legacy:
                    raise ValueError("Duplicate legacy pairing key")
                legacy[key] = record
            continue
        names = payload["candidate_names"]
        user = next(m["content"] for m in payload["messages"] if m["role"] == "user")
        system = next(m["content"] for m in payload["messages"] if m["role"] == "system")
        try:
            types, metadata = native_cards(user, names)
            stripped = user
            edges = set()
            if MARKER in user:
                start = user.index(MARKER)
                decoded, end = json.JSONDecoder().raw_decode(user[start + len(MARKER):])
                edges = {(e["source"], e["relation"], e["target"]) for e in decoded}
                stripped = user[:start] + user[start + len(MARKER) + end:]
            record = {"input_id": payload["input_id"], "question": payload["question"],
                      "candidates": digest(names), "reference": digest(sorted(reference["reference_names"])),
                      "types": digest(types), "metadata_prefix200": digest([v[:200] for v in metadata]),
                      "metadata_prefix": [v[:512] for v in metadata],
                      "metadata_lengths": [len(v) for v in metadata],
                      "system": digest(system), "user_without_overlay": digest(stripped)}
            key = (info["condition"], info["noise"], info["base_id"])
            if key in native:
                raise ValueError("Duplicate native pairing key")
            native[key] = record
            counts["native_primary_inputs_parsed"] += 1
            if info["condition"] == "D200+E":
                spec = specs[info["base_id"]]
                witnesses, paths, missing = native_witnesses(spec, edges, types)
                counts["native_overlay_typed_goal_reference_checked"] += 1
                if sorted(witnesses) != sorted(reference["reference_names"]) or missing:
                    failures.append({"code": "native_typed_goal_reference", "input_id": payload["input_id"],
                                     "base_id": info["base_id"], "noise": info["noise"],
                                     "expected": reference["reference_names"], "actual": sorted(witnesses),
                                     "missing_goal_indices": missing, "paths": paths})
        except (ValueError, KeyError, TypeError) as exc:
            failures.append({"code": "native_input_parse", "input_id": payload["input_id"], "message": str(exc)})
    pairs = []
    for a, b in (("D200", "D200+E"), ("D200", "Dfull")):
        left = {k[1:]: v for k, v in native.items() if k[0] == a}
        right = {k[1:]: v for k, v in native.items() if k[0] == b}
        common = set(left) & set(right)
        fields = ["question", "candidates", "reference", "types", "system", "metadata_prefix200"]
        if b == "D200+E":
            fields.append("user_without_overlay")
        check = Counter()
        for key in common:
            for field in fields:
                check[field + ("_equal" if left[key][field] == right[key][field] else "_different")] += 1
            if b == "Dfull":
                if max(left[key]["metadata_lengths"]) > 512:
                    raise ValueError("Short native metadata exceeds retained comparison prefix")
                prefix_matches = [long.startswith(short) for short, long in zip(left[key]["metadata_prefix"], right[key]["metadata_prefix"])]
                check["each_short_metadata_is_prefix_of_full" if all(prefix_matches) else "short_metadata_not_prefix_of_full"] += 1
                if not all(prefix_matches) and len([f for f in failures if f["code"] == "native_full_not_prefix_example"]) < 3:
                    failures.append({"code": "native_full_not_prefix_example", "pair_key": key,
                                     "left_input_id": left[key]["input_id"], "right_input_id": right[key]["input_id"],
                                     "cards": [{"index": i, "short": short, "full_prefix": long}
                                               for i, (short, long, same) in enumerate(zip(left[key]["metadata_prefix"], right[key]["metadata_prefix"], prefix_matches)) if not same][:2]})
        pairs.append({"series": "native_d", "left": a, "right": b, "pairing_key": ["noise", "base_id"],
                      "left_N": len(left), "right_N": len(right), "paired_N": len(common),
                      "left_only": len(set(left) - common), "right_only": len(set(right) - common), "checks": dict(check)})
    for model in sorted({k[0] for k in legacy}):
        left = {k[2]: v for k, v in legacy.items() if k[:2] == (model, "disconnected")}
        right = {k[2]: v for k, v in legacy.items() if k[:2] == (model, "adjacent")}
        common, check = set(left) & set(right), Counter()
        for key in common:
            for field in ("question", "reference", "pattern", "anchor", "system"):
                check[field + ("_equal" if left[key][field] == right[key][field] else "_different")] += 1
        pairs.append({"series": "legacy", "model": model, "paired_N": len(common), "left_N": len(left), "right_N": len(right),
                      "left_only": len(set(left) - common), "right_only": len(set(right) - common), "checks": dict(check)})
    result = {"counts": dict(counts), "pairs": pairs, "failures": failures,
              "source_sha256": {name: file_hash(ROOT / name) for name in ("results/inputs.jsonl.gz", "results/task_specs_native.jsonl.gz")},
              "script_sha256": file_hash(Path(__file__)),
              "limitations": ["Native raw-description semantic sufficiency is not evaluated by typed-edge traversal.",
                              "Native D200+E verification evaluates the displayed overlay against the separately saved typed goal paths.",
                              "Dfull prefix checks certify truncation consistency, not factual completeness of prose."]}
    (HERE / "supplement.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"counts": dict(counts), "failures": len(failures), "pairs": pairs}, indent=2))


if __name__ == "__main__":
    main()
