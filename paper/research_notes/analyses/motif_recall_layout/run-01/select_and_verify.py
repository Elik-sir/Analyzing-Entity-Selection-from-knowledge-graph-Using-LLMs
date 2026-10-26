"""Reproduce or verify the retained Raw/Raw+E seven-motif plot selection.

Default: verify retained selected_rows.csv and plot_scope.json without writing.
Use --output <fresh-directory> to write an independently regenerated selection
and scope report. Existing destinations are never overwritten. No model,
judge, database, network, project oracle, or raw-response parser is invoked.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[5]
RETAINED = Path(__file__).resolve().parent
MOTIFS = ['chain', 'star_in', 'star_out', 'tree_in', 'tree_out', 'rhombus', 'hourglass']
SIZES = {**{m: 6 for m in MOTIFS}, 'rhombus': 4, 'hourglass': 5}
MODELS = ['gemma-4-31b', 'qwen3.6-flash', 'ministral-14b']
CONDITIONS = ['Braw', 'Braw+E']
ALIASES = {'Braw': 'Raw', 'Braw+E': 'Raw+E'}
SOURCE = ROOT / 'paper/research_notes/analyses/final_results/run-01/motif_size_metrics.csv'
CONDITION_SOURCE = ROOT / 'paper/research_notes/analyses/final_results/run-01/condition_metrics.csv'
OBSERVATIONS = ROOT / 'results/observations.jsonl.gz'
PAIRING_REPORT = ROOT / 'paper/research_notes/reference_pairing_report.md'
METRIC = ('failure-inclusive macro recall = sum_i [valid_i * cached_individual_recall_i] / '
          'planned_N; invalid/missing outcomes contribute zero; no valid-only filter')


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def selection() -> tuple[list[dict], dict]:
    with SOURCE.open(encoding='utf-8', newline='') as stream:
        all_rows = list(csv.DictReader(stream))
    selected = []
    for line_number, row in enumerate(all_rows, 2):
        if (row['series_id'] == 'full_braw' and row['noise'] == 'disconnected'
                and row['condition'] in CONDITIONS and row['model'] in MODELS
                and row['motif'] in SIZES and int(row['size']) == SIZES[row['motif']]):
            record = dict(row)
            record.update(display_condition=ALIASES[row['condition']],
                          source_csv_line_1based=line_number,
                          motif_order=MOTIFS.index(row['motif']))
            selected.append(record)
    assert len(selected) == 42, 'Expected 3 models x 2 conditions x 7 motifs'
    selected.sort(key=lambda r: (MODELS.index(r['model']), CONDITIONS.index(r['condition']),
                                 MOTIFS.index(r['motif'])))
    keys = {}
    for row in selected:
        key = (row['model'], row['condition'], row['motif'], int(row['size']))
        assert key not in keys and int(row['N']) == 100
        assert 0 <= float(row['recall']) <= 1
        keys[key] = row

    base_sets, observations = defaultdict(set), defaultdict(list)
    duplicate_counts = Counter()
    with gzip.open(OBSERVATIONS, 'rt', encoding='utf-8') as stream:
        for line in stream:
            row = json.loads(line)
            key = (row.get('model'), row.get('condition'), row.get('motif'), row.get('size'))
            if (row.get('series_id') == 'full_braw' and row.get('noise') == 'disconnected'
                    and key in keys):
                duplicate_counts[key + (row['base_id'],)] += 1
                base_sets[key].add(row['base_id'])
                observations[key].append(row)
    assert len(observations) == 42
    assert all(n == 1 for n in duplicate_counts.values()), 'Duplicate base within condition'
    pairs = []
    for model in MODELS:
        for motif in MOTIFS:
            left = (model, 'Braw', motif, SIZES[motif])
            right = (model, 'Braw+E', motif, SIZES[motif])
            assert len(base_sets[left]) == len(base_sets[right]) == 100
            assert base_sets[left] == base_sets[right], 'Unmatched Raw/Raw+E bases'
            pairs.append(dict(model=model, motif=motif, size=SIZES[motif], paired_N=100,
                              unmatched_left=0, unmatched_right=0,
                              paired_key='(series_id=full_braw, model, noise=disconnected, motif, size, base_id), changing only condition'))

    metric_checks = []
    for key, records in observations.items():
        expected = keys[key]
        n = len(records)
        valid = sum(bool(r['valid']) for r in records)
        # Historical individual scores only: no response reparse or re-score.
        recall = sum(float(r['metrics']['recall']) if r['valid'] else 0.0 for r in records) / n
        error = abs(recall - float(expected['recall']))
        assert n == int(expected['N']) and valid == int(expected['valid']) and error < 1e-12
        metric_checks.append(dict(model=key[0], condition=key[1], motif=key[2], size=key[3],
                                  N=n, valid=valid, recall=recall, export_absolute_error=error))
    coverage = {}
    for model in MODELS:
        coverage[model] = {}
        for condition in CONDITIONS:
            rows = [r for r in selected if r['model'] == model and r['condition'] == condition]
            coverage[model][condition] = {
                field: sum(int(r[field]) for r in rows)
                for field in ['N', 'valid', 'invalid', 'raw_response_available', 'cached_metrics_only']}
    scope = {
        'checked_on': '2026-10-26',
        'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'sources': {p.relative_to(ROOT).as_posix(): sha(p)
                    for p in (SOURCE, CONDITION_SOURCE, OBSERVATIONS, PAIRING_REPORT)},
        'selector': dict(series_id='full_braw', noise='disconnected', conditions=CONDITIONS,
                         display_aliases=ALIASES, models=MODELS, motif_sizes=SIZES,
                         source_rows=42, planned_N_per_point=100),
        'metric': METRIC,
        'reference': 'All-route entity-coverage reference W; not final-answer correctness or minimal-card evidence',
        'pairing': {
            'previous_full_audit': 'reference_pairing_report.md, Main paired contrasts: 3400 complete Raw/Raw+E pairs/model with input invariants; source report reused, not newly re-executed',
            'fresh_subset_check': pairs,
            'scope': 'Fresh observation-level base pairing only. Exact saved public-input invariant audit is inherited from prior full audit, not independently rerun here.'},
        'fresh_cached_score_aggregation': metric_checks,
        'evidence_coverage': coverage,
        'recommendation': 'Use this Core-size slice for the seven-family chart. Do not pool all available sizes by motif: size support differs (chain3-6, stars3-10, trees5-10; rhombus4/hourglass5), so that would confound motif and size composition. Mark rhombus/hourglass distinctly because they still use4/5 rather than6.',
        'limitations': [
            'Descriptive saved-outcome scores; no new model/judge/database call or raw-response reparse.',
            'Raw-response availability is recorded separately; means freshly aggregated only from existing individual cached metrics.',
            'All three model labels retained. Invalid outcomes retained in planned denominators.',
            'No recall intervals or significance tests are supplied; F1/exact uncertainty cannot be reused for recall.',
            'Families differ in query semantics, types and direction even at common size; no pure topology or universal ranking claim.',
            'Base tasks/anchors/reference entities may overlap; points and models are not independent replications.',
            'Native Raw cards are not verified to contain all needed relations; Raw+E changes evidence availability.'],
        'caption_suggestion': 'Recall by task family for Raw/Raw+E at the Core sizes: six nodes for chain, stars and trees, four for rhombus and five for hourglass;100 planned paired tasks per point and25 candidates. Invalid outcomes contribute zero. Three model panels use descriptive macro recall without inferential error bars. Schematic icons retain KG edge direction and show reference motifs only; distractors are omitted.'}
    return selected, scope


def csv_bytes(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write to a new, non-existing directory; default is read-only verification')
    args = parser.parse_args()
    retained_csv = RETAINED / 'selected_rows.csv'
    retained_scope = RETAINED / 'plot_scope.json'
    before = {str(p): sha(p) for p in (retained_csv, retained_scope)}
    rows, scope = selection()
    generated_csv = csv_bytes(rows)
    if args.output:
        destination = args.output.resolve()
        if destination.exists():
            raise FileExistsError('Choose a fresh output directory; nothing is overwritten')
        destination.mkdir(parents=True)
        (destination / 'selected_rows.csv').write_bytes(generated_csv)
        (destination / 'plot_scope.json').write_text(json.dumps(scope, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        mode = 'regenerated_into_fresh_directory'
    else:
        assert retained_csv.read_bytes() == generated_csv, 'Retained CSV differs from source-row extraction'
        retained = json.loads(retained_scope.read_text(encoding='utf-8'))
        # Revision may have advanced after the retained analysis; retain its
        # historical value and compare substantive source hashes and results.
        for field in ['sources', 'selector', 'metric', 'reference', 'pairing',
                      'fresh_cached_score_aggregation', 'evidence_coverage',
                      'recommendation', 'limitations', 'caption_suggestion']:
            assert retained[field] == scope[field], f'Retained scope mismatch: {field}'
        mode = 'verified_retained_artifacts_read_only'
    after = {str(p): sha(p) for p in (retained_csv, retained_scope)}
    assert before == after, 'Retained artifacts changed'
    print(json.dumps(dict(status='passed', mode=mode, rows=len(rows),
                         paired_motif_model_cells=len(scope['pairing']['fresh_subset_check']),
                         retained_artifact_hashes_unchanged=True), indent=2))


if __name__ == '__main__':
    main()
