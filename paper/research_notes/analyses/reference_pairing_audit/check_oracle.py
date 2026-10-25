"""Synthetic correctness checks for the audit helper, not model experiments."""

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
module_spec = importlib.util.spec_from_file_location("reference_audit", HERE / "audit_references.py")
audit = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(audit)


def spec(direction="out", depth=2, terminal=None):
    return {"anchor_id": "a", "direction": direction, "depth": depth, "terminal_type": terminal}


def main(root, output):
    cases = []

    def routes(name, task, edges, types, expected_endpoints, expected_witnesses, expected_paths):
        actual = audit.oracle(task, edges, list(types), types)
        assert actual == (set(expected_endpoints), set(expected_witnesses), expected_paths), (name, actual)
        cases.append({"case": name, "status": "passed"})

    routes("parallel_routes_cover_both_branches", spec(),
           [("a", "L", "b"), ("a", "L", "c"), ("b", "L", "d"), ("c", "L", "d")],
           dict.fromkeys("abcd", "Node"), "d", "abcd", 2)
    routes("incoming_direction_and_early_dead_end", spec("in", 2),
           [("b", "L", "a"), ("c", "L", "b"), ("d", "L", "a"), ("a", "L", "e")],
           dict.fromkeys("abcde", "Node"), "cd", "abcd", 2)
    routes("terminal_type_stops_first_match_and_ignores_unmatched_deadend", spec("out", None, "End"),
           [("a", "L", "b"), ("b", "L", "c"), ("a", "L", "d")],
           {"a": "Start", "b": "End", "c": "End", "d": "Other"}, "b", "ab", 1)
    routes("simple_routes_do_not_revisit_anchor", spec(),
           [("a", "L", "b"), ("b", "L", "a")], dict.fromkeys("ab", "Node"), "b", "ab", 1)
    routes("incoming_outgoing_neighbors_keep_direction", spec("both", 1),
           [("b", "L", "a"), ("a", "L", "c"), ("a", "L", "a")],
           dict.fromkeys("abc", "Node"), "bc", "abc", 2)
    routes("out_of_pool_edges_are_excluded", spec("out", 1),
           [("a", "L", "b"), ("a", "L", "outside")], dict.fromkeys("ab", "Node"), "b", "ab", 1)
    try:
        audit.oracle(spec(), [("a", "L", "b"), ("a", "L", "c")], list("abc"), dict.fromkeys("abc", "Node"), limit=1)
        raise AssertionError("Path cap was not enforced")
    except ValueError:
        cases.append({"case": "path_cap_is_explicit", "status": "passed"})

    grammar = audit.template_grammar(root)
    mapping = {"a": "Alpha", "b": "Beta"}
    explicit = [{"name": "Alpha", "facts": {}},
                {"name": "Beta", "facts": {"relations": [{"source": "Alpha", "relation": "LINK", "target": "Beta"}]}}]
    text = [{"name": "Alpha", "facts": {"statements": ["Alpha has a recorded connection to Beta."]}},
            {"name": "Beta", "facts": {}}]
    keys = [{"name": "Alpha", "facts": {"identity_token": "t-a", "link_attributes": [{"predicate": "LINK", "value": "t-b"}]}},
            {"name": "Beta", "facts": {"identity_token": "t-b"}}]
    for mode, cards in (("explicit", explicit), ("text", text), ("keys", keys)):
        decoded, count, hosted = audit.decode(cards, mapping, mode, grammar)
        assert decoded == {("a", "LINK", "b")} and count == 1
        cases.append({"case": "decode_" + mode + "_preserves_directed_edge", "status": "passed"})
    result = {"status": "passed", "cases": cases,
              "scope": "Hand-constructed oracle/decoder correctness fixtures; excluded from all scientific results."}
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "cases": len(cases)}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    main(args.root.resolve(), HERE / "oracle_checks.json")
