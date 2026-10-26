"""Draw seven archived reference motifs, preserving factual edge direction.

Only layout and generic node labels are generated. Actual graph edges and node
roles come from archive_samples.json; no model, database or sampler is called.
"""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
FIG = ROOT / 'paper/figures/motif_schematics_v1'
FIG.mkdir(parents=True, exist_ok=True)
SAMPLES = json.loads((OUT / 'archive_samples.json').read_text(encoding='utf-8'))['samples']
ORDER = ['chain', 'star_in', 'star_out', 'tree_in', 'tree_out', 'rhombus', 'hourglass']
TITLES = ['Chain', 'Star-in', 'Star-out', 'Tree-in', 'Tree-out', 'Rhombus', 'Hourglass']
RULES = ['outgoing; first requested type', 'incoming; one link', 'outgoing; one link',
         'incoming; two links', 'outgoing; two links', 'outgoing; two links', 'incoming + outgoing; one link']
BLUE, GOLD, INK = '#30588F', '#F3D58C', '#263746'
RADIUS = .055
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none'})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def layout(key, sample):
    a = sample['anchor_id']
    out, inc = defaultdict(set), defaultdict(set)
    for u, _, v in sample['typed_edges']:
        out[u].add(v)
        inc[v].add(u)
    nodes = set(sample['reference_ids'])
    positions = {}
    if key == 'chain':
        order = sorted(nodes, key=lambda n: next(x['query_distance'] for x in sample['nodes'] if x['id'] == n))
        assert order[0] == a
        positions = {n: (.5, .91 - i * .165) for i, n in enumerate(order)}
    elif key.startswith('star'):
        order = [a] + sorted(nodes - {a})
        positions[a] = (.5, .48)
        for i, n in enumerate(order[1:]):
            angle = math.pi / 2 + i * 2 * math.pi / (len(order) - 1)
            positions[n] = (.5 + .36 * math.cos(angle), .48 + .36 * math.sin(angle))
    elif key.startswith('tree'):
        adj = inc if key == 'tree_in' else out
        first = sorted(adj[a], key=lambda n: (len(adj[n]), n))
        leaves = [n for p in first for n in sorted(adj[p])]
        assert len(first) == 2 and len(leaves) == 3
        order = [a] + first + leaves
        leaf_x = {n: .15 + i * .35 for i, n in enumerate(leaves)}
        positions[a] = (.5, .86)
        for p in first:
            positions[p] = (sum(leaf_x[n] for n in adj[p]) / len(adj[p]), .50)
        positions.update({n: (x, .12) for n, x in leaf_x.items()})
    elif key == 'rhombus':
        first, ends = sorted(out[a]), sample['endpoint_ids']
        assert len(first) == 2 and len(ends) == 1
        order = [a] + first + ends
        positions = {a: (.5, .86), first[0]: (.20, .49), first[1]: (.80, .49), ends[0]: (.5, .12)}
    else:
        before, after = sorted(inc[a]), sorted(out[a])
        assert len(before) == len(after) == 2
        order = [a] + before + after
        positions = {a: (.5, .49), before[0]: (.23, .85), before[1]: (.77, .85),
                     after[0]: (.23, .13), after[1]: (.77, .13)}
    assert set(positions) == nodes and set(order) == nodes
    labels = {n: chr(ord('a') + i) for i, n in enumerate(order)}
    return positions, labels


def node(ax, xy, label, role):
    color = BLUE if role == 'anchor' else GOLD if role == 'endpoint' else 'white'
    ax.add_patch(Circle(xy, RADIUS, facecolor=color, edgecolor=INK, linewidth=1.1, zorder=3))
    ax.text(*xy, label, ha='center', va='center', color='white' if role == 'anchor' else INK,
            fontsize=8.7, fontweight='bold' if role == 'anchor' else 'normal', zorder=4)


def clean(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')


fig, axs = plt.subplots(2, 4, figsize=(7.25, 4.0))
fig.subplots_adjust(left=.015, right=.99, top=.88, bottom=.025, hspace=.36, wspace=.08)
records = []
for i, key in enumerate(ORDER):
    sample, ax = SAMPLES[key], axs.flat[i]
    clean(ax)
    positions, labels = layout(key, sample)
    ax.text(.5, 1.13, f'({chr(97+i)}) {TITLES[i]}', ha='center', va='center', fontsize=9.2, fontweight='bold')
    ax.text(.5, 1.035, RULES[i], ha='center', va='center', fontsize=7.0, color='#435566')
    for u, _, v in sample['typed_edges']:
        x, y = positions[u]
        dx, dy = positions[v][0] - x, positions[v][1] - y
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        start = (x + RADIUS * ux, y + RADIUS * uy)
        end = (positions[v][0] - RADIUS * ux, positions[v][1] - RADIUS * uy)
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=9,
                                     linewidth=1.05, color=INK, shrinkA=0, shrinkB=0, zorder=2))
    roles = {}
    for n in positions:
        roles[n] = 'anchor' if n == sample['anchor_id'] else 'endpoint' if n in sample['endpoint_ids'] else 'intermediate'
        node(ax, positions[n], labels[n], roles[n])
    assert set(sample['witness_ids']) == set(sample['reference_ids'])
    records.append({'motif': key, 'input_id': sample['input_id'], 'selector': sample['selector'],
                    'node_mapping': [{'source_id': n, 'label': labels[n], 'role': roles[n], 'position': positions[n]} for n in positions],
                    'edges_drawn': [[labels[u], rel, labels[v]] for u, rel, v in sample['typed_edges']],
                    'endpoints': [labels[n] for n in sample['endpoint_ids']],
                    'reference': sorted(labels.values())})
legend = axs.flat[7]
clean(legend)
legend.text(.05, 1.13, 'Node roles', ha='left', va='center', fontsize=9.2, fontweight='bold')
for y, role, label, text in [(.83, 'anchor', 'a', 'Named anchor'), (.61, 'endpoint', 'v', 'Endpoint answer'),
                              (.39, 'intermediate', 'v', 'Intermediate entity')]:
    node(legend, (.105, y), label, role)
    legend.text(.23, y, text, ha='left', va='center', fontsize=7.5)
legend.text(.04, .17, 'All shown nodes belong to W.\nArrows show KG direction.',
            ha='left', va='top', fontsize=7.1, linespacing=1.4, color='#435566')
files = []
for ext in ('pdf', 'svg', 'png'):
    p = FIG / ('motif_schematics.' + ext)
    if p.exists():
        raise RuntimeError('Do not overwrite a prior figure silently; use a fresh figure directory.')
    fig.savefig(p, dpi=300, facecolor='white')
    files.append({'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)})
plt.close(fig)
target = ROOT / 'paper/manuscript/figures/motif_schematics_v1.pdf'
if target.exists():
    raise RuntimeError('Existing manuscript figure must be preserved before replacement.')
shutil.copyfile(FIG / 'motif_schematics.pdf', target)
files.append({'path': target.relative_to(ROOT).as_posix(), 'sha256': sha(target)})
(OUT / 'figure_sources.json').write_text(json.dumps({
    'source': 'paper/research_notes/analyses/motif_description/run-01/archive_samples.json',
    'source_sha256': sha(OUT / 'archive_samples.json'), 'script_sha256': sha(Path(__file__)),
    'records': records, 'files': files,
    'scope': 'Seven reference-induced archived Core K1 graphs with generic labels, not full 25-candidate contexts or newly generated KG tasks.'
}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'figure_directory': str(FIG), 'panels': len(records), 'formats': ['PDF', 'SVG', 'PNG 300 dpi']}))
