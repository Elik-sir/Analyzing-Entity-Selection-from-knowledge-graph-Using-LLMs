"""Compact motif key next to existing Raw/Raw+E recall, without model calls."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
FIG = ROOT / 'paper/figures/motif_raw_recall_v1'
FIG.mkdir(parents=True, exist_ok=True)
ORDER = ['chain', 'star_in', 'star_out', 'tree_in', 'tree_out', 'rhombus', 'hourglass']
NAMES = ['Chain', 'Star-in', 'Star-out', 'Tree-in', 'Tree-out', 'Rhombus', 'Hourglass']
MODELS = [('gemma-4-31b', 'Gemma'), ('qwen3.6-flash', 'Qwen'), ('ministral-14b', 'Ministral')]
INK, BLUE, ORANGE = '#34444F', '#305F97', '#B57728'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none'})
with (OUT / 'selected_rows.csv').open(encoding='utf-8', newline='') as stream:
    rows = list(csv.DictReader(stream))
lookup = {(r['model'], r['condition'], r['motif']): r for r in rows}
assert len(lookup) == len(rows) == 42
source = ROOT / 'paper/research_notes/analyses/motif_description/run-01/figure_sources.json'
diagrams = {r['motif']: r for r in json.loads(source.read_text(encoding='utf-8'))['records']}
fig = plt.figure(figsize=(7.25, 2.12))
fig.text(.126, .947, 'Motif key', ha='center', va='center', fontsize=8.6, fontweight='bold')
glyphs = []
for i, key in enumerate(ORDER):
    row, col = divmod(i, 2)
    ax = fig.add_axes([.006 + col * .132, .67 - row * .18, .114, .12])
    ax.set_xlim(-.03, 1.03); ax.set_ylim(-.03, 1.03); ax.axis('off')
    d = diagrams[key]
    pos = {n['label']: n['position'] for n in d['node_mapping']}
    if key == 'chain':
        pos = {label: (.04 + j * .184, .48) for j, label in enumerate(sorted(pos))}
    ax.text(.5, 1.19, chr(97+i) + '  ' + NAMES[i], ha='center', va='bottom', fontsize=6.6)
    for u, _, v in d['edges_drawn']:
        ax.add_patch(FancyArrowPatch(pos[u], pos[v], arrowstyle='-|>', mutation_scale=4.5,
                                    color=INK, linewidth=.65, shrinkA=2.1, shrinkB=2.1))
    for label, xy in pos.items():
        ax.scatter(*xy, s=8, facecolor=BLUE if label == 'a' else 'white',
                   edgecolor=INK, linewidths=.65, zorder=3)
    glyphs.append({'motif': key, 'source_input_id': d['input_id'], 'edges': d['edges_drawn'],
                   'positions': pos, 'anchor': 'a', 'legend': 'blue anchor, other reference vertices white'})
legend = fig.add_axes([.138, .13, .114, .12]); legend.axis('off')
legend.set_xlim(0, 1); legend.set_ylim(0, 1)
legend.scatter(.08, .77, s=8, color=BLUE, zorder=3)
legend.text(.21, .77, 'anchor', fontsize=6.3, va='center')
legend.add_patch(FancyArrowPatch((.01, .13), (.22, .13), arrowstyle='-|>', mutation_scale=4.8, linewidth=.7, color=INK))
legend.text(.28, .13, 'KG edge', fontsize=6.3, va='center')

for j, (model, title) in enumerate(MODELS):
    ax = fig.add_axes([.302 + j * .234, .19, .212, .62])
    ax.axvspan(4.5, 6.5, color='#F2F3F4', zorder=0)
    for condition, color, style, marker in [('Braw', ORANGE, '--', 's'), ('Braw+E', BLUE, '-', 'o')]:
        values = [float(lookup[model, condition, k]['recall']) for k in ORDER]
        assert all(int(lookup[model, condition, k]['N']) == 100 for k in ORDER)
        ax.plot(range(7), values, color=color, linestyle=style, marker=marker,
                linewidth=1.15, markersize=3, markeredgewidth=.45, clip_on=False)
    assert all(float(lookup[model, 'Braw+E', k]['recall']) > float(lookup[model, 'Braw', k]['recall']) for k in ORDER)
    ax.set_xlim(-.4, 6.4); ax.set_ylim(0, 1.06)
    ax.set_xticks(range(7), list('abcdefg')); ax.set_yticks([0, .5, 1])
    ax.tick_params(axis='both', labelsize=7.1, length=2, pad=2)
    ax.set_title(title, fontsize=8.5, pad=5, fontweight='bold')
    ax.set_xlabel('Motif', fontsize=7.6, labelpad=3)
    if j == 0:
        ax.set_ylabel('Recall', fontsize=8, labelpad=3)
    else:
        ax.tick_params(labelleft=False)
    ax.grid(axis='y', color='#DCE2E7', linewidth=.5)
    ax.set_axisbelow(True)
    for side in ('top', 'right'): ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color('#8B969E'); ax.spines[side].set_linewidth(.65)
handles = [Line2D([], [], color=ORANGE, linestyle='--', marker='s', markersize=3, linewidth=1.15, label='Raw'),
           Line2D([], [], color=BLUE, linestyle='-', marker='o', markersize=3, linewidth=1.15, label='Raw+E')]
fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.65, 1.025), ncol=2,
           frameon=False, fontsize=8, handlelength=2, columnspacing=1.4)
files = []
for ext in ('png', 'pdf', 'svg'):
    p = FIG / ('motifs_and_raw_recall.' + ext)
    if p.exists(): raise RuntimeError('Preserve any previous render before replacing it.')
    fig.savefig(p, dpi=300, facecolor='white')
    files.append({'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
plt.close(fig)
target = ROOT / 'paper/manuscript/figures/motifs_and_raw_recall_v1.pdf'
if target.exists(): raise RuntimeError('Preserve an existing manuscript figure before replacement.')
shutil.copyfile(FIG / 'motifs_and_raw_recall.pdf', target)
files.append({'path': target.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
(OUT / 'figure_sources.json').write_text(json.dumps({
    'data': 'paper/research_notes/analyses/motif_recall_layout/run-01/selected_rows.csv',
    'data_sha256': hashlib.sha256((OUT / 'selected_rows.csv').read_bytes()).hexdigest(),
    'diagram_source': source.relative_to(ROOT).as_posix(),
    'diagram_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'rows': rows, 'glyphs': glyphs, 'files': files,
    'figure_inches': [7.25, 2.12], 'scope': 'Core-size slice of Full Raw/Raw+E; representative glyph topology from archived Core, not claimed to depict the plotted Full observations. Lines connect categorical motif means only; no inference or QA claim.'
}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'figure': str(FIG / 'motifs_and_raw_recall.png'), 'points': len(rows), 'size_inches': [7.25, 2.12]}))
