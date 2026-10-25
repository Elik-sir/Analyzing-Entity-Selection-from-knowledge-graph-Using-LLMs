"""Select already computed rows for the main-text outline; no new statistics or calls."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
NOTES = ROOT / 'paper/research_notes'
SOURCE = NOTES / 'analyses/final_results/run-01'
OUT = Path(__file__).parent / 'run-01'
OUT.mkdir(exist_ok=False)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows(name):
    with (SOURCE / name).open(newline='') as f:
        return list(csv.DictReader(f))

def unique(data, **selector):
    found = [r for r in data if all(r[k] == v for k, v in selector.items())]
    assert len(found) == 1, (selector, len(found))
    return found[0]

conditions = rows('condition_metrics.csv')
contrasts = rows('paired_contrasts.csv')
models = ['gemma-4-31b', 'qwen3.6-flash', 'ministral-14b']
labels = ['Gemma-4-31B', 'Qwen3.6-Flash', 'Ministral-14B']
raw = []
for model, label in zip(models, labels):
    left = unique(conditions, series_id='full_braw', model=model, condition='Braw', noise='disconnected')
    right = unique(conditions, series_id='full_braw', model=model, condition='Braw+E', noise='disconnected')
    contrast = unique(contrasts, panel='raw', model=model, contrast='raw_explicit', metric='f1')
    assert left['N'] == right['N'] == contrast['N_pairs'] == '3400'
    assert abs(float(right['f1']) - float(left['f1']) - float(contrast['delta'])) < 1e-12
    raw.append(dict(model=model, label=label, left=left, right=right, contrast=contrast))

selected = ['format_slots', 'format_goal', 'noise_triples', 'noise_text', 'placement_object', 'placement_both']
figure_rows = [unique(contrasts, panel='core', model=model, contrast=c, metric='f1') for model in models for c in selected]
assert all(r['N_pairs'] == '700' for r in figure_rows)
figs = json.loads((SOURCE / 'figure_sources.json').read_text())
fig = next(r for r in figs if r['figure'] == 'controlled_contrasts')
figure_bytes = {}
for name, expected in fig['files'].items():
    path = ROOT / 'paper/figures/final_results' / name
    current = digest(path)
    newline_equivalent = False
    if current != expected:
        data = path.read_bytes()
        newline_equivalent = name.endswith('.svg') and hashlib.sha256(data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')).hexdigest() == expected
        assert newline_equivalent, name
    figure_bytes[name] = dict(current_sha256=current, archived_sha256=expected, crlf_equivalent=newline_equivalent)

spec = [
    ('Raw', 'Braw', 'Native cards', 'Disconnected', 'Native', 'Raw+E − Raw', 3400),
    ('Raw+E', 'Braw+E', 'Native cards + explicit links', 'Disconnected', 'Native', 'Raw+E − Raw', 3400),
    ('Triples/source', 'K1', 'Controlled triples', 'Disconnected', 'Source / step-by-step', 'K5−K1; K3−K1; K4−K1; K2−K1', 700),
    ('Triples/adjacent', 'K2', 'Controlled triples', 'Adjacent', 'Source / step-by-step', 'K2−K1', 700),
    ('Triples/destination', 'K3', 'Controlled triples', 'Disconnected', 'Destination / step-by-step', 'K3−K1', 700),
    ('Triples/both', 'K4', 'Controlled triples', 'Disconnected', 'Both cards / step-by-step', 'K4−K1', 700),
    ('Text', 'K5', 'Controlled templated prose', 'Disconnected', 'Template / step-by-step', 'K5−K1; K6−K5', 700),
    ('Text/adjacent', 'K6', 'Controlled templated prose', 'Adjacent', 'Template / step-by-step', 'K6−K5', 700),
    ('Triples/direct', 'K7', 'Controlled triples', 'Disconnected', 'Source / direct question', 'K8−K7', 700),
    ('Text/direct', 'K8', 'Controlled templated prose', 'Disconnected', 'Template / direct question', 'K8−K7', 700),
]
lines = ['# Main-text table previews', '', 'Selected existing results, 2026-10-25. This is an outline asset, not a compiled manuscript table.', '', '## Table 1 — Experimental conditions', '', '| Condition (archive ID) | Evidence | Distractors | Placement / question | Main contrast(s) | Planned bases/model |', '|---|---|---|---|---|---:|']
for name, archive, evidence, noise, placement, contrast, n in spec:
    lines.append(f'| {name} ({archive}) | {evidence} | {noise} | {placement} | {contrast} | {n:,} |')
lines += ['', 'Per-condition/model planned counts; repeated conditions and the two panels are not independent datasets to sum. Historical design is supported by the frozen-pairing audit, not the current registry alone.', '', '## Table 2A — Native-card and overlay F1', '', '| Archived model | Raw F1 | Raw+E F1 | ΔF1 | Simultaneous band for ΔF1 |', '|---|---:|---:|---:|---|']
for r in raw:
    a,b,c=r['left'],r['right'],r['contrast']
    lines.append(f"| {r['label']} | {float(a['f1']):.3f} | {float(b['f1']):.3f} | {float(c['delta']):+.3f} | [{float(c['simultaneous_low']):.3f}, {float(c['simultaneous_high']):.3f}] |")
lines += ['', '## Table 2B — Exact selection and protocol validity', '', '| Archived model | Raw exact | Raw+E exact | Valid Raw / planned N | Valid Raw+E / planned N |', '|---|---:|---:|---:|---:|']
for r in raw:
    a,b=r['left'],r['right']
    lines.append(f"| {r['label']} | {float(a['exact']):.3f} | {float(b['exact']):.3f} | {a['valid']} / {a['N']} | {b['valid']} / {b['N']} |")
lines += ['', 'Caption: 3,400 paired tasks per model; all planned outcomes retained, invalid/missing outcomes contribute zero to primary scores. Δ is Raw+E minus Raw. Bands are exploratory simultaneous bands from the declared 78-effect F1/exact family, conditional on this fixed KG and independence across anchors. They do not cover arbitrary shared-entity dependence. Scores rounded to three decimals; valid counts are protocol outcomes, not raw-response availability. Archived model labels do not authenticate unavailable provider/version metadata.', '', 'Figure 2 retains all six selected controlled contrasts for each model. Its stored delta and interval values are multiplied by 100 only for the percentage-point axis. Figure 1 remains specified, not rendered, in paper_outline.md.', '']
(OUT / 'main_text_tables.md').write_text('\n'.join(lines))
plan = dict(schema_version=1, checked_on='2026-10-25', operation='Selection/formatting of existing computed rows; no re-estimation', source_hashes={name:digest(SOURCE/name) for name in ['condition_metrics.csv','paired_contrasts.csv','figure_sources.json']}, table1=dict(design_evidence='E-reference-audit-final',columns=['name','archive_id','evidence','noise','placement_question','contrasts','planned_bases_per_model'], rows=spec), table2=raw, figure1=dict(status='selected_not_rendered', evidence='E-support-example', source_sha256=digest(NOTES/'analyses/reference_pairing_audit/support_example.json')), figure2=dict(status='existing_selected',files=figure_bytes,source_rows=figure_rows), formatting=dict(scores='three decimal score units',figure2='delta and interval *100 percentage points',failure_policy='all planned N; invalid/missing contributes zero',family='existing 78-effect F1/exact family unchanged'))
(OUT/'asset_plan.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps(dict(status='passed',raw_model_rows=len(raw),controlled_figure_rows=len(figure_rows),figure_hashes_checked=len(fig['files']),new_statistics=False)))
