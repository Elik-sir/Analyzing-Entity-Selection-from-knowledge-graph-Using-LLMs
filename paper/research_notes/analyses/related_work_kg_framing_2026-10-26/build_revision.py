"""Create the author-requested KG-centered Related Work variant; preserve v3."""
import ast
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / 'related_work_revision_2026-10-26'
SECTIONS = ROOT / 'paper/manuscript/sections'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def dump(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

# Reuse inspected metadata without executing or modifying the previous generator.
tree = ast.parse((PREVIOUS / 'build_revision.py').read_text())
sources = next(ast.literal_eval(n.value) for n in tree.body
               if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'sources' for t in n.targets))

# Each sentence has explicit evidence IDs; citations are a separate presentation choice.
paragraphs = [
    ('Entity selection for knowledge-grounded LLMs', [
        ('Knowledge graphs support LLM-based question answering and agents by providing relational context for retrieval and reasoning.', ['luo2024rog', 'ghandi2026graphwalk'], ['E-lit-luo2024rog', 'E-lit-ghandi2026graphwalk']),
        ('A query may depend on intermediate entities connecting its starting point to its answers, making the selection of supporting context a problem beyond identifying plausible endpoints.', ['luo2024rog'], ['E-lit-luo2024rog']),
        ('STaRK evaluates entity retrieval under textual and relational query constraints, while G-Retriever constructs a connected graph context through prize-collecting Steiner tree optimization.', ['wu2024stark', 'he2024gretriever'], ['E-lit-wu2024stark', 'E-lit-he2024gretriever']),
        ('Our study examines entity selection within a fixed candidate pool containing every reference entity.', [], ['E-local-pairs']),
        ('The target is the union of entities on all routes permitted by the query, including intermediate and branching entities.', [], ['E-local-pairs']),
        ('Evaluating this set directly allows us to characterize the completeness and selectivity of the relational context retained by the model.', [], ['E-local-pairs', 'E-local-final-results']),
    ]),
    ('Graph structure and task comprehension', [
        ('Graph-reasoning benchmarks provide context for evaluating how this selection behavior varies across structural configurations.', ['fatemi2024talklikegraph', 'dai2025graphpatterns', 'xu2026graphomni'], ['E-lit-fatemi2024talklikegraph', 'E-lit-dai2025graphpatterns', 'E-lit-xu2026graphomni']),
        ('Talk like a Graph studies graph encodings, task types, and graph structure; Xinnan Dai et al. examine pattern comprehension and discovery from terminological and topological descriptions.', ['fatemi2024talklikegraph', 'dai2025graphpatterns'], ['E-lit-fatemi2024talklikegraph', 'E-lit-dai2025graphpatterns']),
        ('GraphOmni jointly varies graph families, serialization formats, and prompting schemes across graph-theoretic tasks.', ['xu2026graphomni'], ['E-lit-xu2026graphomni']),
        ('We use directed motifs and reference sizes to organize entity-selection profiles, interpreting structural differences alongside query semantics and the evidence visible to the model.', [], ['E-local-pairs', 'E-local-final-results', 'E-local-methodology']),
    ]),
    ('Availability and representation of relational evidence', [
        ('The graph information presented to an LLM is another central factor in KG-based reasoning.', ['dai2024kgunderstanding', 'tian2025alignment'], ['E-lit-dai2024kgunderstanding', 'E-lit-tian2025alignment']),
        ('Xinbang Dai et al. compare KG input formats and triple organization and evaluate robustness to noisy or incomplete subgraphs using answer-based evaluation.', ['dai2024kgunderstanding'], ['E-lit-dai2024kgunderstanding']),
        ('Tian et al. distinguish graph transformation from linearization and examine formats, orders, and templates in KG-augmented generation.', ['tian2025alignment'], ['E-lit-tian2025alignment']),
        ('Our comparisons distinguish relation availability from the presentation of designated matched facts: Raw versus Raw+E adds explicit relations to native entity cards, while controlled triples, templated prose, and alternative card hosting vary their presentation.', [], ['E-local-pairs']),
        ('This distinction lets us examine entity recovery under different evidence conditions without assuming that native descriptions contain every graph relation.', [], ['E-local-pairs', 'E-local-methodology']),
    ]),
    ('Selection errors, distractors, and evaluation targets', [
        ('GraphWalk reports incomplete exploration when graph context is supplied directly to the model.', ['ghandi2026graphwalk'], ['E-lit-ghandi2026graphwalk']),
        ('TopoRAG addresses noise from heuristic neighbor expansion through retrieval constrained by induced-subgraph diameter, while Amiraz et al. quantify the distracting effect of irrelevant passages on answer-generating models.', ['wu2026toporag', 'amiraz2025distracting'], ['E-lit-wu2026toporag', 'E-lit-amiraz2025distracting']),
        ('Our disconnected/adjacent-context comparison examines query-irrelevant neighboring entities while preserving reference availability within a fixed-size candidate pool.', [], ['E-local-pairs']),
        ('This provides a structural distractor condition; adjacency alone is not a definition of irrelevance.', [], ['E-local-pairs', 'E-local-methodology']),
        ('Li and Ouyang show that the relationship between knowledge-selection quality and generation quality depends on the generator and task.', ['li2025selection'], ['E-lit-li2025selection']),
        ('We therefore evaluate route coverage, excess selection, and complete-set recovery directly through recall, precision, and exact recovery, keeping these outcomes distinct from minimum sufficient evidence and final-answer correctness.', [], ['E-local-final-results', 'E-local-methodology']),
    ]),
    ('Relationship to structural tool selection', [
        ('Tool selection provides a related perspective on retaining elements that compose to support a request.', ['anonymousToolGraph'], ['E-lit-anonymousToolGraph']),
        ('Tool Graph Complexity distinguishes reference-set non-minimality from dependency composition and analyzes motif-associated selection difficulty.', ['anonymousToolGraph'], ['E-lit-anonymousToolGraph']),
        ('Its Appendix~O directly overlaps the KG setting: it evaluates motif and size variation with explicit relations and adjacent decoys, reporting easier KG chains, difficult incoming trees, and decoy-related inclusion errors.', ['anonymousToolGraph'], ['E-lit-anonymousToolGraph']),
        ('We acknowledge these prior KG findings and center the present analysis on entity-route recovery across relation availability, matched-fact presentation, and distractor conditions.', [], ['E-lit-anonymousToolGraph', 'E-local-pairs', 'E-local-final-results']),
        ('Protocol differences and unresolved task/response overlap limit direct cross-study score comparisons; the analyses do not establish a common internal failure mechanism for tool and entity selection.', [], ['E-lit-anonymousToolGraph', 'E-local-comparison', 'E-local-methodology']),
    ]),
]

state = json.loads((ROOT / 'paper/research_notes/workflow_state.json').read_text())
assert state['analysis_complete'] and state['full_writing_ready'] and state['gate_rationale']
evidence_doc = json.loads((PREVIOUS / 'evidence_register.json').read_text())
evidence = {x['id']: x for x in evidence_doc['evidence']}
# Check, rather than silently refresh, previously inspected local hashes.
for record in evidence.values():
    if 'path' in record:
        assert sha(ROOT / record['path']) == record['sha256'], record['id']

def tex_sentence(t, keys):
    return t[:-1] + '~\\cite{' + ','.join(keys) + '}.' if keys else t

def md_sentence(t, keys):
    t = t.replace('~', ' ')
    links = []
    for key in keys:
        label, url, path, _, _ = sources[key]
        links.append(f'[{label}]({url or str(ROOT / path)})')
    return t[:-1] + ' (' + '; '.join(links) + ').' if keys else t

tex = ['\\section{Related Work}', '\\label{sec:related}', '']
md = ['# Related Work', '']
claims, mapping = [], []
for pi, (title, statements) in enumerate(paragraphs, 1):
    tex += ['\\paragraph{' + title + '.}', ' '.join(tex_sentence(t, k) for t, k, _ in statements), '']
    md += ['**' + title + '.** ' + ' '.join(md_sentence(t, k) for t, k, _ in statements), '']
    for si, (t, keys, refs) in enumerate(statements, 1):
        assert all(e in evidence for e in refs)
        own_scope = not keys and any(evidence[e]['kind'] == 'result' for e in refs)
        reason = ('Audited frozen-input/reference or existing metric definition; no new empirical result or historical execution is inferred.' if own_scope else
                  'Scoped synthesis or comparison supported by the inspected primary text and, where relevant, recorded methodological limits.')
        if 'tian2025alignment' in keys:
            reason += ' Tian evidence is limited to the verified abstract taxonomy; the previous full-body access limitation persists.'
        cid = f'C-RW4-{pi}-{si}'
        claims.append(dict(id=cid, text=t.replace('~', ' '), type='historical' if own_scope else 'literature',
                           status='supported', scope=f'02_related_work_v4.tex paragraph {pi}, sentence {si}',
                           evidence_ids=refs, reason=reason, numeric=False))
        mapping.append(dict(paragraph=pi, sentence=si, claim_ids=[cid], evidence_ids=refs))

(SECTIONS / '02_related_work_v4.tex').write_text('\n'.join(tex))
(SECTIONS / '02_related_work_v4.md').write_text('\n'.join(md))
bib = (SECTIONS / 'related_work_v3.bib').read_text().replace('Related Work v3', 'Related Work v4')
(SECTIONS / 'related_work_v4.bib').write_text(bib)
dump('evidence_register.json', evidence_doc)
(HERE / 'claims.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in claims))
dump('manuscript_claim_map.json', dict(schema_version=1, checked_on='2026-10-26',
     scope='KG-centered Related Work v4 only; author-requested reframing of v3, not whole-paper review',
     entries=mapping, source_hashes={str(p.relative_to(ROOT)): sha(p) for p in
         [SECTIONS / '02_related_work_v4.tex', SECTIONS / '02_related_work_v4.md', SECTIONS / 'related_work_v4.bib']}))
shutil.copyfile(ROOT / 'paper/research_notes/workflow_state.json', HERE / 'workflow_state.json')
dump('provenance.json', dict(checked_on='2026-10-26', source_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
     request='Lead with KG entity selection and LLM agents; retain tool-selection relationship in a separate later paragraph.',
     parent_revision='paper/research_notes/analyses/related_work_revision_2026-10-26',
     inputs={str(p.relative_to(ROOT)): sha(p) for p in [PREVIOUS / 'build_revision.py', PREVIOUS / 'evidence_register.json',
              SECTIONS / '02_related_work_v3.tex', SECTIONS / 'related_work_v3.bib', ROOT / 'paper/research_notes/workflow_state.json']},
     preservation='v3 and active older manuscript unchanged',
     additional_source_check=['https://arxiv.org/html/2402.07630v3 Sections 4-5', 'https://arxiv.org/html/2604.01610v1 Abstract/Introduction',
                              'https://proceedings.iclr.cc/paper_files/paper/2024/hash/3e2aeb66481dd63a32421bf032b70384-Abstract-Conference.html']))

keys = re.findall(r'@\w+\{([^,]+),', bib)
cited = {k for group in re.findall(r'\\cite\{([^}]+)\}', '\n'.join(tex)) for k in group.split(',')}
assert len(keys) == len(set(keys)) == 13 and cited == set(keys)
for document in ('\n'.join(tex), bib):
    depth = 0
    for c in document:
        depth += (c == '{') - (c == '}')
        assert depth >= 0
    assert depth == 0
dump('syntax_checks.json', dict(status='passed', paragraphs=len(paragraphs), sentences=len(claims), citation_keys=len(keys),
     unresolved_keys=[], duplicate_keys=[], braces='balanced', full_pdf_compiled=False,
     note='Static checks only; scientific support is scoped to the mapped propositions.'))
print(json.dumps(dict(paragraphs=len(paragraphs), sentences=len(claims), references=len(keys),
     words=len(re.findall(r"\b[\w'-]+\b", ' '.join(t for _, ss in paragraphs for t, _, _ in ss)))), indent=2))
