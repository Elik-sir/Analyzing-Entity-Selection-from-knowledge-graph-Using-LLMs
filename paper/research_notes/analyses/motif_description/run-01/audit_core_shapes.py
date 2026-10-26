"""Bounded read-only audit of all archived Qwen Core/K1/disconnected inputs.

Does not import research modules or call any model, database, or network service.
Run from the repository root with the existing Python environment. Existing
output is preserved: choose --output for a fresh rerun.
"""
import argparse
import ast
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys


SIZES = {'chain': 6, 'star_in': 6, 'star_out': 6, 'tree_in': 6,
         'tree_out': 6, 'rhombus': 4, 'hourglass': 5}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def directed_targets(spec, edges, types):
    outgoing, incoming = defaultdict(set), defaultdict(set)
    for s, _, t in edges:
        if s != t:
            outgoing[s].add(t)
            incoming[t].add(s)
    anchor = spec['anchor_id']
    paths = []
    if spec['direction'] == 'both':
        paths = [(anchor, target) for target in sorted(incoming[anchor] | outgoing[anchor])]
    else:
        adjacent = outgoing if spec['direction'] == 'out' else incoming
        stack = [(anchor,)]
        expansions = 0
        while stack:
            expansions += 1
            if expansions > 10000:
                raise ValueError('independent traversal expansion bound exceeded')
            path = stack.pop()
            current = path[-1]
            next_ids = adjacent[current] - set(path)
            terminal = (spec['terminal_type'] is not None and len(path) > 1
                        and types[current] == spec['terminal_type'])
            bounded = (spec['depth'] is not None and len(path) > 1
                       and (len(path) - 1 == spec['depth'] or not next_ids))
            if terminal or bounded:
                paths.append(path)
            elif spec['terminal_type'] is not None or len(path) - 1 < spec['depth']:
                stack.extend(path + (target,) for target in sorted(next_ids, reverse=True))
    return {path[-1] for path in paths}, {node for path in paths for node in path}


def inspect_shape(motif, spec, refs, edges, types):
    pairs = {(s, t) for s, _, t in edges}
    anchor = spec['anchor_id']
    outgoing, incoming = defaultdict(set), defaultdict(set)
    for s, t in pairs:
        outgoing[s].add(t)
        incoming[t].add(s)
    checks = {'reference_size': len(refs) == SIZES[motif],
              'anchor_in_reference': anchor in refs,
              'one_typed_relation_per_topological_edge': len(edges) == len(pairs),
              'no_self_edges': all(s != t for s, t in pairs)}
    detail = {}
    if motif == 'chain':
        path, current = [anchor], anchor
        while len(path) <= len(refs) and len(outgoing[current]) == 1:
            target = next(iter(outgoing[current]))
            if target in path:
                break
            path.append(target)
            current = target
        terminal = spec['terminal_type']
        checks['saved_pattern_direction_depth'] = (spec['pattern'] == 'path:' + str(terminal)
                                                   and spec['direction'] == 'out'
                                                   and spec['depth'] is None and bool(terminal))
        checks['single_outgoing_path'] = (set(path) == refs and len(path) == len(refs)
                                          and pairs == set(zip(path, path[1:])))
        checks['first_terminal_type_after_anchor'] = (bool(terminal) and types[path[-1]] == terminal
                                                     and all(types[n] != terminal for n in path[1:-1]))
        checks['saved_target_is_path_end'] = set(spec['target_ids']) == {path[-1]}
        detail = {'path_vertex_count': len(path), 'terminal_type': terminal}
    elif motif.startswith('star_'):
        direction = motif.split('_')[1]
        leaves = refs - {anchor}
        expected = {(anchor, n) if direction == 'out' else (n, anchor) for n in leaves}
        checks['single_hub_five_leaves'] = pairs == expected and len(leaves) == 5
        checks['saved_pattern_direction_depth'] = (spec['pattern'] == direction + ':1'
                                                   and spec['direction'] == direction
                                                   and spec['depth'] == 1 and spec['terminal_type'] is None)
        checks['saved_targets_are_leaves'] = set(spec['target_ids']) == leaves
    elif motif.startswith('tree_'):
        direction = motif.split('_')[1]
        adjacent = outgoing if direction == 'out' else incoming
        first = adjacent[anchor]
        second_by_parent = {n: adjacent[n] for n in first}
        second = set().union(*second_by_parent.values()) if first else set()
        branches = sorted(len(v) for v in second_by_parent.values())
        topology_forward = {(anchor, n) for n in first} | {(n, t) for n in first for t in adjacent[n]}
        expected = topology_forward if direction == 'out' else {(t, s) for s, t in topology_forward}
        checks['two_levels_with_branch_coverage'] = (
            len(first) >= 2 and all(second_by_parent[n] for n in first)
            and not first.intersection(second) and anchor not in first | second
            and {anchor} | first | second == refs and all(not adjacent[n] for n in second)
            and sum(branches) == len(second) and pairs == expected)
        checks['tree_edge_count'] = len(pairs) == len(refs) - 1
        checks['saved_pattern_direction_depth'] = (spec['pattern'] == direction + ':2'
                                                   and spec['direction'] == direction
                                                   and spec['depth'] == 2 and spec['terminal_type'] is None)
        checks['saved_targets_are_second_level'] = set(spec['target_ids']) == second
        detail = {'first_level_count': len(first), 'second_level_count': len(second),
                  'second_level_branch_sizes_sorted': branches}
    elif motif == 'rhombus':
        first = outgoing[anchor]
        shared = set.intersection(*(outgoing[n] for n in first)) if first else set()
        sink = next(iter(shared)) if len(shared) == 1 else None
        expected = {(anchor, n) for n in first} | {(n, sink) for n in first}
        checks['two_branches_one_shared_sink'] = (len(first) == 2 and len(shared) == 1
                                                   and refs == {anchor, sink} | first
                                                   and not outgoing[sink] and pairs == expected)
        checks['saved_pattern_direction_depth'] = (spec['pattern'] == 'out:2'
                                                   and spec['direction'] == 'out'
                                                   and spec['depth'] == 2 and spec['terminal_type'] is None)
        checks['saved_target_is_shared_sink'] = set(spec['target_ids']) == {sink}
    elif motif == 'hourglass':
        ins, outs = incoming[anchor], outgoing[anchor]
        expected = {(n, anchor) for n in ins} | {(anchor, n) for n in outs}
        checks['two_incoming_two_outgoing_neighbors'] = (len(ins) == len(outs) == 2
                                                          and not ins.intersection(outs)
                                                          and refs == {anchor} | ins | outs
                                                          and pairs == expected)
        checks['saved_pattern_direction_depth'] = (spec['pattern'] == 'both:1'
                                                   and spec['direction'] == 'both'
                                                   and spec['depth'] == 1 and spec['terminal_type'] is None)
        checks['saved_targets_are_two_one_hop_groups'] = set(spec['target_ids']) == ins | outs
        detail = {'incoming_count': len(ins), 'outgoing_count': len(outs)}
    return checks, detail


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or Path(__file__).with_name('core_shape_audit.json')
    if output.exists():
        raise SystemExit('Existing output preserved; choose a fresh --output.')
    selected = []
    with gzip.open(root / 'results/observations.jsonl.gz', 'rt', encoding='utf-8') as stream:
        for line_no, line in enumerate(stream, 1):
            obs = json.loads(line)
            if (obs.get('series_id') == 'core' and obs.get('condition') == 'K1'
                    and obs.get('noise') == 'disconnected' and obs.get('model') == 'qwen3.6-flash'):
                selected.append((line_no, obs))
    by_input = defaultdict(list)
    base_counts = Counter()
    for line_no, obs in selected:
        by_input[obs['input_id']].append((line_no, obs))
        base_counts[obs['base_id']] += 1
    found, results = set(), []
    with gzip.open(root / 'results/inputs.jsonl.gz', 'rt', encoding='utf-8') as stream:
        for input_line, line in enumerate(stream, 1):
            item = json.loads(line)
            if item['input_id'] not in by_input:
                continue
            found.add(item['input_id'])
            for obs_line, obs in by_input[item['input_id']]:
                row = {key: obs[key] for key in ('base_id', 'input_id', 'observation_id', 'motif', 'size')}
                row.update(input_line_1based=input_line, observation_line_1based=obs_line)
                try:
                    private = item['reference']['private']
                    spec = private['task_spec']
                    names = private['name_map']
                    reverse = {name: node for node, name in names.items()}
                    if len(reverse) != len(names):
                        raise ValueError('nonunique saved name map')
                    data = json.loads(next(m['content'] for m in item['messages'] if m['role'] == 'user'))
                    types, all_edges = {}, set()
                    for candidate in data['candidates']:
                        types[reverse[candidate['name']]] = candidate['type']
                        for edge in candidate.get('facts', {}).get('relations', []):
                            all_edges.add((reverse[edge['source']], edge['relation'], reverse[edge['target']]))
                    refs = set(spec['reference_ids'])
                    edges = {e for e in all_edges if e[0] in refs and e[2] in refs}
                    checks, detail = inspect_shape(obs['motif'], spec, refs, edges, types)
                    endpoints, witnesses = directed_targets(spec, all_edges, types)
                    checks.update(public_traversal_matches_saved_endpoints=endpoints == set(spec['target_ids']),
                                  public_traversal_matches_reference_witnesses=witnesses == set(spec['witness_ids']) == refs,
                                  candidates_contain_all_references=refs <= set(private['candidate_ids']),
                                  public_candidate_names_match_saved_catalogue=set(types) == set(private['candidate_ids']))
                    row.update(checks=checks, shape_detail=detail, metadata_complete=True,
                               passed=all(checks.values()))
                except (KeyError, TypeError, ValueError, StopIteration) as exc:
                    row.update(metadata_complete=False, passed=False,
                               missing_or_invalid_metadata=f'{type(exc).__name__}: {exc}')
                results.append(row)
    missing_inputs = sorted(set(by_input) - found)
    summaries = {}
    for motif in SIZES:
        subset = [r for r in results if r['motif'] == motif]
        failures = Counter(check for row in subset for check, ok in row.get('checks', {}).items() if not ok)
        branches = Counter(','.join(map(str, r['shape_detail']['second_level_branch_sizes_sorted']))
                           for r in subset if 'second_level_branch_sizes_sorted' in r.get('shape_detail', {}))
        summaries[motif] = dict(planned_observations=sum(obs['motif'] == motif for _, obs in selected),
                                joined_inputs=len(subset), metadata_complete=sum(r['metadata_complete'] for r in subset),
                                passed=sum(r['passed'] for r in subset),
                                failed_checks=dict(failures), tree_branch_allocations=dict(branches))
    files = ['results/observations.jsonl.gz', 'results/inputs.jsonl.gz',
             'graph_motives/graph/motifs.py', 'graph_motives/preparation/questions.py']
    payload = {
        'schema_version': 1, 'checked_on': '2026-10-26',
        'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        'selector': {'series_id': 'core', 'condition': 'K1', 'noise': 'disconnected',
                     'model': 'qwen3.6-flash', 'outcome_filter': None},
        'population': {'planned_observations': len(selected), 'unique_base_ids': len(base_counts),
                       'unique_input_ids': len(by_input), 'joined_observations': len(results),
                       'duplicate_base_observation_counts': {k: v for k, v in base_counts.items() if v != 1},
                       'source_status_counts': dict(Counter(obs['status'] for _, obs in selected)),
                       'missing_input_ids': missing_inputs},
        'family_summaries': summaries,
        'summary': {'metadata_complete': sum(r['metadata_complete'] for r in results),
                    'passed': sum(r['passed'] for r in results),
                    'failed': sum(not r['passed'] for r in results),
                    'all_expected_core_cells_present': all(v['planned_observations'] == 100 for v in summaries.values())},
        'sources': {p: {'sha256': digest(root / p)} for p in files},
        'script_sha256': digest(Path(__file__)),
        'command': '.venv/Scripts/python.exe paper/research_notes/analyses/motif_description/run-01/audit_core_shapes.py',
        'formula': 'Select every matching planned observation, join input_id, parse public typed facts and saved TaskSpec, inspect reference-induced directed graph and independently traverse full public candidate facts; no valid-response filter.',
        'limitations': ['Frozen Core K1 disconnected inputs only; not Full/Raw/adjacent/other-size populations.',
                       'Current code is read-only contextual evidence; saved inputs establish the inspected shapes, not historical sampler execution.',
                       'Does not establish full source-KG completeness, indispensable cards, internal model reasoning or answer correctness.',
                       'Observations are paired/reused inputs; these counts are not independent experimental replicates.'],
        'rows': sorted(results, key=lambda r: (r['motif'], r['base_id']))}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: payload[key] for key in ('population', 'family_summaries', 'summary')}, ensure_ascii=False))
    return 0 if not missing_inputs and payload['summary']['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
