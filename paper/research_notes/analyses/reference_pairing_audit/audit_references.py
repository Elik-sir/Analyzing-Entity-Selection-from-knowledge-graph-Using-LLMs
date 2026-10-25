"""Audit frozen references and paired inputs without importing research modules.

Only the saved archive and source text are read. No model/API/database access.
The oracle independently enumerates simple routes from serialized public edges.
Absence of explicit edges in native descriptions is not proof of insufficiency.
"""

import argparse
import ast
import copy
import csv
import gzip
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def rows(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def template_grammar(root):
    """Read a finite serialization grammar as data; never execute the module."""
    tree = ast.parse((root / "graph_motives/preparation/evidence.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "RELATION_PHRASES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError("No finite text grammar")


def decode(cards, mapping, mode, grammar):
    """Map public names back to frozen IDs and decode exact displayed facts."""
    inverse = {v: k for k, v in mapping.items()}
    if len(inverse) != len(mapping):
        raise ValueError("Nonunique mapped public names")
    tokens = {c["facts"]["identity_token"]: inverse[c["name"]]
              for c in cards if "identity_token" in c["facts"]}
    if len(tokens) != sum("identity_token" in c["facts"] for c in cards):
        raise ValueError("Duplicate identity token")
    edges, raw_count, hosted = set(), 0, []
    for card in cards:
        host, facts = inverse[card["name"]], card["facts"]
        if mode == "explicit":
            for edge in facts.get("relations", []):
                value = (inverse[edge["source"]], edge["relation"], inverse[edge["target"]])
                edges.add(value)
                hosted.append((host, *value))
                raw_count += 1
        elif mode == "keys":
            for link in facts.get("link_attributes", []):
                value = (host, link["predicate"], tokens[link["value"]])
                edges.add(value)
                hosted.append((host, *value))
                raw_count += 1
        elif mode == "text":
            for sentence in facts.get("statements", []):
                # The host is the subject in this fixed controlled grammar.
                matches = []
                for relation, template in grammar.items():
                    prefix, suffix = template.split("{t}")
                    start, end = card["name"] + " " + prefix, suffix + "."
                    if sentence.startswith(start) and sentence.endswith(end):
                        target = sentence[len(start):-len(end)]
                        if target in inverse:
                            matches.append((host, relation, inverse[target]))
                if len(set(matches)) != 1:
                    raise ValueError("Ambiguous/unrecognized controlled text fact")
                value = matches[0]
                edges.add(value)
                hosted.append((host, *value))
                raw_count += 1
    return edges, raw_count, hosted


def oracle(spec, edges, candidate_ids, types, limit=10000):
    """Enumerate every allowed simple route, not only a shortest path/tree."""
    allowed = set(candidate_ids)
    anchor = spec["anchor_id"]
    out, inc = defaultdict(set), defaultdict(set)
    for source, relation, target in edges:
        if source in allowed and target in allowed and source != target:
            out[source].add(target)
            inc[target].add(source)
    direction, depth, terminal = spec["direction"], spec["depth"], spec["terminal_type"]
    paths = []
    if anchor not in allowed:
        raise ValueError("Anchor absent")
    if direction == "both":
        paths = [(anchor, v) for v in sorted(out[anchor] | inc[anchor])]
    else:
        adjacency = out if direction == "out" else inc

        def visit(path):
            if len(paths) >= limit:
                raise ValueError("Independent path limit exceeded")
            here = path[-1]
            following = adjacency[here] - set(path)
            is_terminal = terminal is not None and len(path) > 1 and types[here] == terminal
            bounded = depth is not None and len(path) > 1 and (len(path) - 1 == depth or not following)
            if is_terminal or bounded:
                paths.append(path)
            elif terminal is not None or len(path) - 1 < depth:
                for nxt in sorted(following):
                    visit((*path, nxt))

        visit((anchor,))
    endpoints = {p[-1] for p in paths}
    witnesses = {v for p in paths for v in p}
    return endpoints, witnesses, len(paths)


MODES = {"K0": "none", "R0": "none", "K5": "text", "K6": "text", "K8": "text",
         "K5k": "keys", "K8-inc": "text"}
CONTRASTS = [
    ("representation_slots", "K1", "K5", "format"),
    ("representation_goal", "K7", "K8", "format"),
    ("text_keys", "K5", "K5k", "format"),
    ("question_explicit", "K1", "K7", "question"),
    ("question_text", "K5", "K8", "question"),
    ("location_object", "K1", "K3", "location"),
    ("location_both", "K1", "K4", "location"),
    ("names_disconnected", "R1-matched", "K1", "names"),
    ("names_adjacent", "R2-matched", "K2", "names"),
    ("names_closed", "R0", "K0", "names"),
    ("noise_explicit", "K1", "K2", "noise"),
    ("noise_text", "K5", "K6", "noise"),
]


def main(root, output):
    output.mkdir(parents=True, exist_ok=True)
    if (output / "summary.json").exists():
        raise ValueError("Choose a fresh output directory")
    grammar = template_grammar(root)
    issues, checks, coverage = [], Counter(), Counter()
    observation_by_input, observation_index = defaultdict(list), {}
    observation_count = 0
    for row in rows(root / "results/observations.jsonl.gz"):
        observation_count += 1
        info = {k: row[k] for k in ("observation_id", "series_id", "model", "condition", "noise", "base_id", "motif", "size", "input_id")}
        key = (row["series_id"], row["model"], row["condition"], row["noise"], row["base_id"])
        if key in observation_index:
            issues.append({"code": "duplicate_observation_key", "key": key})
        observation_index[key] = info
        observation_by_input[row["input_id"]].append(info)
    # Some Full Braw core inputs retain reference IDs/edges but omit TaskSpec.
    # Recover only an actually saved spec with the same base ID; never infer it
    # from current defaults. Exact reference and rendered-question equality are
    # checked below before using the joined spec for traversal certification.
    saved_specs = {}
    for payload in rows(root / "results/inputs.jsonl.gz"):
        ref = payload["reference"]
        private = ref.get("private", ref)
        spec = private.get("task_spec")
        if spec:
            key = spec["record_id"]
            if key in saved_specs and saved_specs[key] != spec:
                issues.append({"code": "inconsistent_saved_task_spec", "base_id": key})
            saved_specs[key] = spec
    compact, per_input = {}, []
    source_hashes = {}

    def note(code, payload, **detail):
        item = {"code": code, "input_id": payload["input_id"],
                "observations": observation_by_input.get(payload["input_id"], []), **detail}
        issues.append(item)

    def equal(code, left, right, payload):
        checks[code + "_checked"] += 1
        if left != right:
            checks[code + "_failed"] += 1
            note(code, payload, expected=left, actual=right)

    for payload in rows(root / "results/inputs.jsonl.gz"):
        iid = payload["input_id"]
        observations = observation_by_input.get(iid, [])
        if not observations:
            coverage["stage_or_auxiliary_inputs_not_in_primary_scope"] += 1
            continue
        # Shared frozen inputs may link both Core and incremental observations.
        # Prefer the static task solely for content decoding; never mistake the
        # complete frozen task for an actual incremental solver message/history.
        priority = {"core": 0, "size": 1, "full_braw": 2, "calibration": 3,
                    "legacy": 4, "native_d": 5, "incremental": 6}
        info = min(observations, key=lambda v: priority[v["series_id"]])
        series, condition = info["series_id"], info["condition"]
        ref = payload["reference"]
        private = ref.get("private", ref)
        messages = payload.get("messages")
        public = payload.get("frozen_public")
        system = None
        user_text = None
        if messages:
            systems = [m["content"] for m in messages if m["role"] == "system"]
            system = systems[0] if len(systems) == 1 else None
            users = [m["content"] for m in messages if m["role"] == "user"]
            if users:
                user_text = users[0]
                if user_text.lstrip().startswith("{"):
                    try:
                        public = json.loads(user_text)
                    except ValueError:
                        note("invalid_public_json", payload)
        item = {"input_id": iid, "series": series, "condition": condition,
                "question": payload["question"], "system": digest(system) if system is not None else None,
                "public": digest(public) if public else None,
                "candidate_names": digest(payload["candidate_names"]),
                "reference_names": None, "reference_ids": None, "target_ids": None,
                "witness_ids": None, "candidate_ids": None, "mapping": None,
                "types": None, "edges": None, "cards": None, "base_cards": None,
                "query": None, "normalized_question": None}
        public_names = payload["candidate_names"]
        equal("unique_candidate_names", len(public_names), len(set(public_names)), payload)
        if public:
            equal("public_candidate_order", public_names, [c["name"] for c in public["candidates"]], payload)
            equal("public_question", payload["question"], public["question"], payload)
        gold = None
        if "expected_names" in ref:
            gold = ref["expected_names"]
        elif "reference_names" in ref:
            gold = ref["reference_names"]
        elif "graph_witness_ids" in private:
            gold = [private["name_map"][v] for v in private["graph_witness_ids"]]
        elif "answer" in private and isinstance(private["answer"], list):
            gold = private["answer"]
        if gold is not None:
            equal("reference_unique", len(gold), len(set(gold)), payload)
            equal("reference_in_candidates", [], sorted(set(gold) - set(public_names)), payload)
            item["reference_names"] = digest(sorted(gold))
        spec = private.get("task_spec")
        if not spec and series == "full_braw":
            spec = saved_specs.get(info["base_id"])
            if spec:
                equal("joined_archive_spec_reference", sorted(private["reference_ids"]), sorted(spec["reference_ids"]), payload)
                coverage["full_braw_task_spec_joined_from_saved_core"] += 1
        candidates = private.get("candidate_ids")
        mapping = private.get("name_map")
        if mapping is None and candidates and public:
            mapping = dict(zip(candidates, [c["name"] for c in public["candidates"]]))
        if spec and candidates and public and mapping:
            coverage[f"task_spec_inputs:{series}:{condition}"] += 1
            refs = spec["reference_ids"]
            witnesses = private.get("graph_witness_ids", spec.get("witness_ids"))
            targets = private.get("target_answer_ids", spec.get("target_ids"))
            types = {nid: c["type"] for nid, c in zip(candidates, public["candidates"])}
            equal("candidate_ids_unique", len(candidates), len(set(candidates)), payload)
            equal("mapping_order", [mapping[n] for n in candidates], public_names, payload)
            equal("reference_vs_spec_witness", sorted(refs), sorted(spec["witness_ids"]), payload)
            equal("reference_vs_actual_witness", sorted(refs), sorted(witnesses), payload)
            equal("reference_gold_names", sorted(mapping[n] for n in witnesses), sorted(gold), payload)
            if "expected_names" in ref:
                equal("expected_names_vs_witness", sorted(mapping[n] for n in witnesses), sorted(ref["expected_names"]), payload)
            if "reference_ids" in private:
                equal("reference_ids_vs_spec", sorted(refs), sorted(private["reference_ids"]), payload)
            item.update(candidate_ids=digest(candidates), mapping=digest(mapping),
                        reference_ids=digest(sorted(refs)), target_ids=digest(sorted(targets)),
                        witness_ids=digest(sorted(witnesses)), types=digest(types),
                        query=digest({k: spec[k] for k in ("anchor_id", "direction", "depth", "terminal_type", "path_policy")}))
            item["reference_candidate_ids"] = sorted(refs)
            item["motif_size"] = digest([info["motif"], info["size"]])
            variant = "goal" if condition in {"K7", "K8", "K7-inc", "K8-inc"} else "slots"
            expected_question = spec[variant + "_template"].format(anchor_name=mapping[spec["anchor_id"]])
            equal("rendered_question", expected_question, public["question"], payload)
            item["normalized_question"] = digest(public["question"].replace(mapping[spec["anchor_id"]], "<ANCHOR>"))
            mode = "explicit" if series == "full_braw" else MODES.get(condition, "explicit")
            if series == "full_braw" and condition == "Braw":
                mode = "native"
            if series == "incremental":
                mode = "incremental_initial_menu"
            item["mode"] = mode
            if mode in {"explicit", "text", "keys"}:
                try:
                    edges, raw_count, hosted = decode(public["candidates"], mapping, mode, grammar)
                    endpoints, actual_witness, path_count = oracle(spec, edges, candidates, types)
                    equal("oracle_endpoint", sorted(targets), sorted(endpoints), payload)
                    equal("oracle_witness", sorted(witnesses), sorted(actual_witness), payload)
                    equal("oracle_baseline_endpoint", sorted(spec["target_ids"]), sorted(endpoints), payload)
                    equal("oracle_baseline_witness", sorted(spec["witness_ids"]), sorted(actual_witness), payload)
                    item["edges"] = digest(sorted(edges))
                    item["reference_induced_edges"] = digest(sorted(e for e in edges if e[0] in refs and e[2] in refs))
                    item["edge_count"] = len(edges)
                    item["oracle_paths"] = path_count
                    location = "object" if condition == "K3" else "both" if condition == "K4" else "subject"
                    expected_hosted = sorted({(h, s, r, t) for s, r, t in edges
                                             for h in ([t] if location == "object" else [s, t] if location == "both" else [s])})
                    equal("edge_host_placement", expected_hosted, sorted(hosted), payload)
                    if info["noise"] == "disconnected":
                        boundary = [(s, r, t) for s, r, t in edges if (s in refs) != (t in refs)]
                        equal("disconnected_no_reference_boundary_edges", [], boundary, payload)
                    else:
                        adjacent = {t if s in refs else s for s, r, t in edges if (s in refs) != (t in refs)}
                        equal("adjacent_at_most_ten", True, len(adjacent) <= 10, payload)
                    coverage[f"independent_visible_oracle:{series}:{condition}"] += 1
                except (ValueError, KeyError, TypeError) as exc:
                    note("decode_or_oracle_error", payload, message=str(exc))
                    coverage[f"independent_oracle_errors:{series}:{condition}"] += 1
            else:
                coverage[f"oracle_not_reconstructible_from_explicit_facts:{series}:{condition}"] += 1
            if series == "full_braw":
                inverse = {v: k for k, v in mapping.items()}
                def endpoint_id(value):
                    return value if value in mapping else inverse[value]

                motif_edges = {(endpoint_id(s), r, endpoint_id(t)) for s, r, t in private.get("reference_relations", [])}
                if motif_edges:
                    endpoint_ref, witness_ref, _ = oracle(spec, motif_edges, refs, types)
                    equal("native_reference_edge_oracle_endpoint", sorted(spec["target_ids"]), sorted(endpoint_ref), payload)
                    equal("native_reference_edge_oracle_witness", sorted(refs), sorted(witness_ref), payload)
            normalized_cards = []
            base_cards = copy.deepcopy(public["candidates"])
            for nid, card, base in zip(candidates, public["candidates"], base_cards):
                # Compare actual residual metadata after removing only the overlay.
                base.get("facts", {}).pop("relations", None)
                nonlink_facts = {k: v for k, v in card.get("facts", {}).items()
                                 if k not in {"relations", "statements", "identity_token", "link_attributes"}}
                normalized_cards.append({"id": nid, "type": card["type"], "labels": card.get("labels"),
                                         "nonlink_facts": nonlink_facts})
            item["cards"] = digest(public["candidates"])
            item["normalized_cards"] = digest(normalized_cards)
            item["base_cards"] = digest(base_cards)
            item["public_without_relations"] = digest({**public, "candidates": base_cards})
            item["reference_spec"] = digest(spec)
            if mode == "none":
                # Closed-book builders transmit names/types only; the frozen
                # source contains empty facts/labels and an explanatory note.
                # Raw-byte differences are reported separately below.
                item["effective_public"] = digest({"question": public["question"],
                    "candidates": [{"name": c["name"], "type": c["type"]} for c in public["candidates"]]})
            else:
                item["effective_public"] = item["public"]
        elif series == "calibration" and public:
            candidates = private["candidate_ids"]
            mapping = dict(zip(candidates, public_names))
            types = {nid: c["type"] for nid, c in zip(candidates, public["candidates"])}
            mode = "keys" if "keys" in condition else "text" if "text" in condition else "explicit"
            try:
                edges, _, _ = decode(public["candidates"], mapping, mode, grammar)
                source, relation, target = private["source_edge"]
                expected = {mapping[t] for s, r, t in edges if s == source and (condition.endswith("neighbor") or r == relation)}
                equal("calibration_one_hop_answer", sorted(gold), sorted(expected), payload)
                coverage["calibration_visible_reference_recomputed"] += 1
            except (KeyError, ValueError) as exc:
                note("calibration_decode_error", payload, message=str(exc))
        elif series == "legacy" and public:
            # Legacy contract is graph reachability within a bounded number of
            # incoming/outgoing steps, not controlled endpoint-only QA.
            types = {c["name"]: c["type"] for c in public["candidates"]}
            edges = {tuple(e) for e in private["context_relations"]}
            pattern = private["pattern"]
            direction, argument = pattern.split(":", 1)
            if direction == "path":
                legacy_spec = dict(anchor_id=private["anchor"], direction="out", depth=None, terminal_type=argument)
                _, reachable, _ = oracle(legacy_spec, edges, public_names, types)
            else:
                outgoing, incoming = defaultdict(set), defaultdict(set)
                for s, r, t in edges:
                    outgoing[s].add(t)
                    incoming[t].add(s)
                reachable, frontier = {private["anchor"]}, {private["anchor"]}
                for _ in range(int(argument)):
                    nxt = set()
                    for n in frontier:
                        if direction in {"out", "both"}: nxt |= outgoing[n]
                        if direction in {"in", "both"}: nxt |= incoming[n]
                    frontier = nxt - reachable
                    reachable |= nxt
            equal("legacy_graph_reference", sorted(gold), sorted(reachable), payload)
            coverage["legacy_saved_context_reference_recomputed"] += 1
        else:
            coverage[f"no_structured_graph_oracle_in_primary_payload:{series}:{condition}"] += 1
        compact[iid] = item
        per_input.append({"input_id": iid, "series": series, "condition": condition,
                          "observations": len(observations), "candidate_count": len(public_names),
                          "gold_count": len(gold) if gold is not None else None,
                          "structured_public": public is not None,
                          "has_task_spec": spec is not None})

    pair_rows, pair_examples = [], []

    def compare_scope(series, model, left_cond, right_cond, label, kind, other_series=None):
        left_rows = [v for k, v in observation_index.items() if k[:3] == (series, model, left_cond)]
        left = {v["base_id"]: v for v in left_rows}
        target_series = other_series or series
        right_rows = [v for k, v in observation_index.items() if k[:3] == (target_series, model, right_cond)]
        right = {v["base_id"]: v for v in right_rows}
        if len(left_rows) != len(left) or len(right_rows) != len(right):
            raise ValueError("Pair scope needs an additional noise/size key: " + label)
        common = set(left) & set(right)
        counters = Counter()
        for base in sorted(common):
            a, b = compact[left[base]["input_id"]], compact[right[base]["input_id"]]
            fields = ["reference_ids", "target_ids", "witness_ids", "query", "motif_size"]
            if kind != "noise":
                fields += ["candidate_ids", "types"]
            if kind not in {"names", "noise"}:
                fields += ["mapping", "candidate_names"]
            if kind not in {"question"}:
                fields += ["normalized_question" if kind == "names" else "question"]
            if kind in {"format", "location", "question", "names"} and a.get("mode") != "none":
                fields += ["edges"]
            if kind == "question":
                fields += ["cards"]
            if kind == "names":
                fields += ["normalized_cards"]
            if kind in {"format", "location", "question"}:
                fields += ["normalized_cards"]
            if kind == "noise":
                fields += ["reference_induced_edges"]
            if kind == "overlay":
                fields += ["public_without_relations", "reference_spec"]
            for field in fields:
                if a.get(field) is None or b.get(field) is None:
                    counters[field + "_unavailable"] += 1
                elif a[field] != b[field]:
                    counters[field + "_mismatch"] += 1
                    if len([e for e in pair_examples if e["label"] == label and e["field"] == field]) < 3:
                        pair_examples.append({"label": label, "series": series, "model": model, "base_id": base,
                                              "field": field, "left": left[base], "right": right[base]})
                else:
                    counters[field + "_equal"] += 1
            if a["system"] is not None and b["system"] is not None:
                counters["recorded_system_equal" if a["system"] == b["system"] else "recorded_system_different"] += 1
            else:
                counters["recorded_system_unavailable"] += 1
        pair_rows.append({"label": label, "series": series, "right_series": target_series, "model": model,
                          "left_condition": left_cond, "right_condition": right_cond,
                          "left_N": len(left), "right_N": len(right), "paired_N": len(common),
                          "left_only": len(set(left) - common), "right_only": len(set(right) - common),
                          "checks": dict(counters)})

    models = sorted({v["model"] for v in observation_index.values()})
    for model in models:
        for label, a, b, kind in CONTRASTS:
            compare_scope("core", model, a, b, label, kind)
        compare_scope("full_braw", model, "Braw", "Braw+E", "raw_explicit_overlay", "overlay")
    compare_scope("size", "gemma-4-31b", "K1", "K5", "size_representation", "format")
    for a, b in (("K7", "K7-inc"), ("K8", "K8-inc")):
        compare_scope("core", "gemma-4-31b", a, b, "incremental_initial_" + a, "incremental", "incremental")

    # Paired identity must be unique across noise strata too. This is checked
    # explicitly instead of allowing the simplified per-condition key to hide it.
    simplified = Counter((k[0], k[1], k[2], k[4]) for k in observation_index)
    duplicate_keys = [key for key, n in simplified.items() if n > 1]
    cross_model = Counter()
    canonical_rows = defaultdict(dict)
    for key, obs in observation_index.items():
        canonical_rows[(key[0], key[2], key[3], key[4])][key[1]] = compact[obs["input_id"]]
    for key, group in canonical_rows.items():
        if len(group) < 2:
            continue
        values = list(group.values())
        for field in ("public", "effective_public", "reference_ids", "target_ids", "witness_ids", "reference_names"):
            existing = [value[field] for value in values if value.get(field) is not None]
            cross_model[f"{key[0]}:{field}:compared_groups"] += 1
            if len(existing) != len(values):
                cross_model[f"{key[0]}:{field}:unavailable"] += 1
            elif len(set(existing)) != 1:
                cross_model[f"{key[0]}:{field}:mismatch"] += 1
    for rel in ("results/MANIFEST.json", "results/observations.jsonl.gz", "results/inputs.jsonl.gz",
                "results/task_specs_native.jsonl.gz", "graph_motives/preparation/evidence.py",
                "graph_motives/preparation/questions.py", "graph_motives/preparation/materialize.py",
                "graph_motives/preparation/native.py", "graph_motives/preparation/registry.py"):
        source_hashes[rel] = file_hash(root / rel)
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "script_sha256": file_hash(Path(__file__)),
        "command": "python paper/research_notes/analyses/reference_pairing_audit/audit_references.py --root . --output <fresh-directory>",
        "scope": "All primary observation links; structured saved controlled/full_braw/calibration/legacy reference checks; declared main contrasts. Native D has separate goal specs and is not certified by the endpoint oracle.",
        "observations": observation_count, "primary_inputs": len(compact),
        "source_sha256": source_hashes, "coverage": dict(sorted(coverage.items())),
        "checks": dict(sorted(checks.items())), "issues": len(issues),
        "pairing_key": ["series_id", "model", "condition", "noise", "base_id"],
        "noise_collisions_if_simplified": duplicate_keys,
        "pairs": pair_rows, "pair_mismatch_examples": pair_examples,
        "cross_model": dict(sorted(cross_model.items())),
        "limitations": [
            "Independent oracle is independent traversal code, but controlled text grammar is read from current source and applied strictly to frozen public text.",
            "Reference recovery and declared all-route selection do not prove each card is indispensable.",
            "No full source graph is loaded; induced-edge completeness relative to original snapshot is not reverified.",
            "Native descriptions may state relations in prose; absence of explicit triples is not a semantic insufficiency finding.",
            "Incremental checks concern initial frozen input, not historical trajectories.",
            "No new model/API/judge calls and no uncertainty/significance analysis.",
        ],
    }
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "issues.jsonl").write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in issues), encoding="utf-8")
    with (output / "input_coverage.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(per_input[0]))
        writer.writeheader()
        writer.writerows(per_input)
    print(json.dumps({"observations": observation_count, "primary_inputs": len(compact), "issues": len(issues),
                      "failed_checks": {k: v for k, v in checks.items() if k.endswith("_failed")},
                      "pair_scopes": len(pair_rows)}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    main(args.root.resolve(), args.output.resolve())
