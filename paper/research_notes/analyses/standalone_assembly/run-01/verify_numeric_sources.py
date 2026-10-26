"""Bounded checks of saved scores used by the assembled paper, no model calls."""
import csv
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
PAPER = ROOT / 'paper/manuscript'
RESULTS = ROOT / 'paper/research_notes/analyses/final_results/run-01'
MODELS = {'Gemma': 'gemma-4-31b', 'Qwen': 'qwen3.6-flash', 'Ministral': 'ministral-14b'}


def read(name):
    with (RESULTS / name).open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


conditions, strata = read('condition_metrics.csv'), read('motif_size_metrics.csv')
checks = []


def row(table, **selector):
    found = [r for r in table if all(r.get(k) == str(v) for k, v in selector.items())]
    assert len(found) == 1, (selector, len(found))
    return found[0]


def condition(model, code, series='core'):
    return row(conditions, series_id=series, model=model, condition=code, noise='disconnected')


def core(model, code, motif='tree_in'):
    return row(strata, series_id='core', model=model, condition=code,
               noise='adjacent' if code == 'K2' else 'disconnected', motif=motif,
               size=4 if motif == 'rhombus' else 5 if motif == 'hourglass' else 6)


def rounded(value):
    return Decimal(str(value)).quantize(Decimal('.001'), rounding=ROUND_HALF_UP)


def check(label, displayed, value, source):
    assert Decimal(str(displayed)) == rounded(value), (label, displayed, value)
    checks.append({'locator': label, 'displayed': str(displayed), 'unrounded': value, 'source': source})


def tex_rows(name):
    for line in (PAPER / 'tables' / name).read_text(encoding='utf-8').splitlines():
        if '&' in line and line.rstrip().endswith(r'\\'):
            cells = [c.strip() for c in line.rstrip()[:-2].split('&')]
            if cells[0] in {'Model', 'Condition'}:
                continue
            yield cells


contrasts = [('Braw', 'Braw+E', 'full_braw'), ('K1', 'K2', 'core'), ('K5', 'K6', 'core'),
             ('K1', 'K5', 'core'), ('K7', 'K8', 'core'), ('K1', 'K3', 'core'),
             ('K1', 'K4', 'core'), ('K1', 'K7', 'core')]
for cells in tex_rows('recall_effects.tex'):
    model = MODELS[cells[0]]
    for display, (left, right, series) in zip(cells[1:], contrasts):
        # Noise is intentionally different for K2/K6.
        l = row(conditions, series_id=series, model=model, condition=left)
        r = row(conditions, series_id=series, model=model, condition=right)
        check('tables/recall_effects.tex:' + cells[0] + ':' + right + '-' + left,
              display, float(r['recall']) - float(l['recall']),
              dict(series=series, model=model, left=left, right=right, N=int(l['N']), metric='recall'))
for cells in tex_rows('treein_recall.tex'):
    for display, code in zip(cells[1:], ['K1', 'K3', 'K4', 'K7']):
        r = core(MODELS[cells[0]], code)
        check('tables/treein_recall.tex:' + cells[0] + ':' + code, display, float(r['recall']),
              dict(series='core', model=r['model'], condition=code, motif='tree_in', size=6, N=int(r['N'])))
for name, metric in [('core_recall.tex', 'recall'), ('core_precision.tex', 'precision')]:
    for cells in tex_rows(name):
        for display, model in zip(cells[1:], MODELS.values()):
            r = row(conditions, series_id='core', model=model, condition=cells[0])
            check('tables/' + name + ':' + cells[0] + ':' + model, display, float(r[metric]),
                  dict(series='core', model=model, condition=cells[0], N=int(r['N']), metric=metric))

for title, gain, raw, explicit, rawp, explicitp in [
    ('Gemma', '.774', '.198', '.972', '.859', '.988'),
    ('Qwen', '.519', '.278', '.798', '.885', '.975'),
    ('Ministral', '.567', '.218', '.785', '.459', '.976')]:
    model = MODELS[title]
    l, r = condition(model, 'Braw', 'full_braw'), condition(model, 'Braw+E', 'full_braw')
    for display, value, metric in [(gain, float(r['recall'])-float(l['recall']), 'recall_delta'),
                                   (raw, float(l['recall']), 'Raw_recall'), (explicit, float(r['recall']), 'Raw+E_recall'),
                                   (rawp, float(l['precision']), 'Raw_precision'), (explicitp, float(r['precision']), 'Raw+E_precision')]:
        check('Abstract/Results:' + title + ':' + metric, display, value,
              dict(series='full_braw', model=model, conditions=['Braw', 'Braw+E'], N=int(l['N']), metric=metric))

size_examples = [
    ('Qwen', 'chain', 3, '.990'), ('Qwen', 'chain', 6, '.790'),
    ('Ministral', 'chain', 3, '.927'), ('Ministral', 'chain', 6, '.595'),
    ('Gemma', 'chain', 3, '.990'), ('Gemma', 'chain', 6, '1.000'),
    ('Qwen', 'star_out', 3, '.997'), ('Qwen', 'star_out', 10, '.998'),
    ('Gemma', 'star_out', 3, '1.000'), ('Gemma', 'star_out', 10, '1.000'),
    ('Ministral', 'star_out', 3, '.870'), ('Ministral', 'star_out', 10, '.950'),
    ('Gemma', 'tree_in', 5, '.910'), ('Gemma', 'tree_in', 10, '.841'),
    ('Qwen', 'tree_in', 5, '.624'), ('Qwen', 'tree_in', 10, '.375'),
    ('Ministral', 'tree_in', 5, '.540'), ('Ministral', 'tree_in', 10, '.403')]
for title, motif, size, display in size_examples:
    r = row(strata, series_id='full_braw', model=MODELS[title], condition='Braw+E', motif=motif, size=size)
    check('Results:size:' + title + ':' + motif + ':' + str(size), display, float(r['recall']),
          dict(series='full_braw', model=r['model'], condition='Braw+E', motif=motif, size=size, N=int(r['N'])))

diag_path = ROOT / 'paper/research_notes/analyses/novelty_refinement/run-02/summary.json'
diag = json.loads(diag_path.read_text(encoding='utf-8'))
def diagnostic(kind, **selector):
    return row(diag[kind], **selector)
for model, code, onehop, exact in [
    ('qwen3.6-flash', 'K1', 71, 15), ('qwen3.6-flash', 'K3', 76, 16),
    ('qwen3.6-flash', 'K4', 31, 51), ('qwen3.6-flash', 'K7', 52, 16),
    ('ministral-14b', 'K1', 15, 54), ('ministral-14b', 'K4', 6, 62)]:
    d = diagnostic('groups', model=model, condition=code)
    assert d['one_hop'] == onehop and d['cached_exact'] == exact and d['planned'] == 100
    checks.append({'locator': 'Diagnostic group:' + model + ':' + code, 'one_hop': onehop, 'exact': exact, 'planned_N': 100})
for model, code, gained, lost in [('qwen3.6-flash', 'K3', 13, None), ('qwen3.6-flash', 'K4', 38, 6),
                                ('qwen3.6-flash', 'K7', 10, None), ('ministral-14b', 'K4', 8, 9)]:
    d = diagnostic('transitions', model=model, before='K1', after=code)
    assert d['one_hop_to_exact'] == gained and d['planned_pairs'] == 100
    if lost is not None: assert d['cached_exact_lost'] == lost
    checks.append({'locator': 'Diagnostic transition:' + model + ':K1-' + code, 'one_hop_to_exact': gained, 'cached_exact_lost': lost, 'planned_pairs': 100})
for code, rule, distinct in [('K1', 'depth_three', 0), ('K1', 'undirected', 0),
                             ('K2', 'depth_three', 10), ('K2', 'undirected', 97)]:
    d = diagnostic('alternative_rules', model='qwen3.6-flash', condition=code, rule=rule)
    assert d['distinct_from_reference'] == distinct and d['matches_distinct_alternative'] == 0
    checks.append({'locator': 'Alternative rule:Qwen:' + code + ':' + rule, 'distinct': distinct,
                   'matches_distinct_alternative': 0, 'valid_N': d['valid_identity_denominator']})

bars_path = ROOT / 'paper/research_notes/analyses/motif_recall_layout/run-02/figure_sources.json'
bars = json.loads(bars_path.read_text(encoding='utf-8'))
for b in bars['bars']:
    r = row(strata, series_id='full_braw', model=b['model'], condition=b['condition'], motif=b['motif'],
            size=4 if b['motif']=='rhombus' else 5 if b['motif']=='hourglass' else 6)
    assert b['height'] == float(r['recall']) and int(r['N']) == 100
for f in bars['files']:
    assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest() == f['sha256']

result = {'status': 'passed', 'checked_items': len(checks), 'checks': checks,
          'main_bar_heights_checked': len(bars['bars']), 'failure_policy': 'all planned; invalid/missing zero',
          'rounding': 'decimal half-up to three places; deltas computed before rounding',
          'scope': 'Displayed main/supplementary tables, key prose/abstract examples, diagnostic counts, and main bar values verified against saved scores. No raw-response reparse or new inference.'}
(OUT/'numeric_checks_root.json').write_text(json.dumps(result, indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'checked_items':len(checks),'main_bars':len(bars['bars'])}))
