"""Write a scoped Related Work replacement and its sentence-level evidence map.

No model calls, experiments, or changes to the existing manuscript are performed.
"""
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SECTIONS = ROOT / 'paper/manuscript/sections'
DATE = '2026-10-26'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

# title, statements: text, citation keys, local support IDs (for this study).
paragraphs = [
    ('Structural difficulty and prior Tool-to-KG evidence', [
        ('Tool Graph Complexity distinguishes reference-set non-minimality from dependency composition and analyzes motif-associated tool-selection difficulty.', ['anonymousToolGraph'], []),
        ('Its adjusted analysis emphasizes sequential-pattern penalties, whereas raw motif rankings also reflect size and surface properties.', ['anonymousToolGraph'], []),
        ('Appendix~O already evaluates entity selection on a finance KG, including motif and size variation, explicit relations, and adjacent decoys; it reports easier chains with explicit KG relations, difficult incoming trees, and decoy-related inclusion errors.', ['anonymousToolGraph'], []),
        ('These are antecedent findings for our diagnostic follow-up, which separates relation disclosure from matched-fact presentation and examines residual selection errors.', [], ['E-local-pairs', 'E-local-final-results']),
        ("Differences in references, prompts, populations, and evaluation protocols limit direct score comparisons; unquantified task/response overlap also precludes a claim of independent replication.", [], ['E-local-comparison']),
    ]),
    ('Graph structure and task comprehension', [
        ('Talk like a Graph evaluates how graph encodings, task types, and graph structure affect LLM performance.', ['fatemi2024talklikegraph'], []),
        ('Xinnan Dai et al. study pattern comprehension and discovery from terminological and topological descriptions, including pattern detection and graph modification.', ['dai2025graphpatterns'], []),
        ('GraphOmni jointly varies graph families, serialization formats, and prompting schemes across graph-theoretic tasks.', ['xu2026graphomni'], []),
        ('Our motifs organize comparisons of query-conditioned entity selection: the reference includes intermediate and branching entities on all permitted supporting routes.', [], ['E-local-pairs']),
        ('The analysis concerns recovery of this declared route reference, with structure interpreted alongside query semantics and visible evidence.', [], ['E-local-pairs', 'E-local-methodology']),
    ]),
    ('Availability and representation of relational evidence', [
        ('Xinbang Dai et al. compare KG input formats and triple organization and evaluate robustness to noisy or incomplete subgraphs using answer-based evaluation.', ['dai2024kgunderstanding'], []),
        ('Tian et al. distinguish graph transformation from linearization and examine formats, orders, and templates in KG-augmented generation.', ['tian2025alignment'], []),
        ('We distinguish adding explicit relations to native entity cards from changing the presentation of designated matched facts.', [], ['E-local-pairs']),
        ('Raw versus Raw+E changes available information; controlled triples versus templated prose and source-, destination-, or both-card hosting change how that information is presented.', [], ['E-local-pairs']),
        ('Native descriptions are not assumed to express every graph relation, so disclosure gains alone cannot establish better reasoning from equally informative inputs.', [], ['E-local-pairs', 'E-local-methodology']),
    ]),
    ('Graph retrieval and route recovery', [
        ('STaRK evaluates retrieval of answer entities satisfying textual and relational query constraints.', ['wu2024stark'], []),
        ('G-Retriever constructs graph context using prize-collecting Steiner tree optimization, while Reasoning on Graphs plans relation sequences and retrieves instantiated reasoning paths for KG question answering.', ['he2024gretriever', 'luo2024rog'], []),
        ('GraphWalk studies tool-based graph navigation and reports incomplete exploration in its graph-in-context setting.', ['ghandi2026graphwalk'], []),
        ('Our main evaluation holds target availability within a supplied candidate pool fixed and scores selected entity sets against the complete route reference.', [], ['E-local-pairs']),
        ('This objective differs from retrieving answer entities, constructing a compact useful subgraph, or generating an answer from retrieved paths.', ['wu2024stark', 'he2024gretriever', 'luo2024rog'], ['E-local-pairs']),
        ('Final-set omissions are observable selection errors; they do not reconstruct internal traversal steps or identify a shared failure mechanism across these settings.', [], ['E-local-methodology']),
    ]),
    ('Distractors and selection metrics', [
        ('Amiraz et al. quantify how irrelevant passages can distract answer-generating models, distinguishing distraction from a binary relevance label.', ['amiraz2025distracting'], []),
        ('TopoRAG addresses noise from heuristic neighbor expansion through retrieval constrained by induced-subgraph diameter.', ['wu2026toporag'], []),
        ('Our disconnected/adjacent-context comparison instead examines query-irrelevant neighboring entities within a fixed-size pool containing every reference entity.', [], ['E-local-pairs']),
        ('Structural proximity is a different distractor construction from passage-level semantic distraction and does not by itself establish irrelevance.', ['amiraz2025distracting'], ['E-local-pairs']),
        ('Li and Ouyang show that the relationship between knowledge-selection quality and generation quality depends on the generator and task.', ['li2025selection'], []),
        ('Accordingly, we use recall to measure route coverage and precision and exact recovery to diagnose excess selection and complete-set recovery; these metrics establish neither minimum sufficient evidence nor downstream answer correctness.', [], ['E-local-methodology', 'E-local-final-results']),
    ]),
]

# Metadata and scientific-content verification are deliberately separate.
sources = {
 'anonymousToolGraph': ('Tool Graph Complexity', None, 'paper/research_notes/sources/tool_graph_complexity.pdf', 'Sections 5.1 and 5.3, PDF pp. 7-8; Appendix O and Tables 32-33, PDF pp. 30-31', 'Supplied anonymous manuscript; no current submission or acceptance status asserted.'),
 'fatemi2024talklikegraph': ('Fatemi et al., 2024', 'https://proceedings.iclr.cc/paper_files/paper/2024/hash/bf72f65f30eedf5d48da6980ee02b589-Abstract-Conference.html', None, 'Conference PDF Sections 3-4; Figure 2', 'Conference metadata and relevant full text inspected.'),
 'dai2025graphpatterns': ('Xinnan Dai et al., 2025', 'https://proceedings.iclr.cc/paper_files/paper/2025/hash/9316da9c25ab559ba678f2fe52217a64-Abstract-Conference.html', None, 'Conference PDF Sections 3-5; Sections 3.2-3.3 and 4.1 inspected in detail', 'Conference metadata and relevant full text inspected.'),
 'xu2026graphomni': ('Xu et al., 2026', 'https://arxiv.org/html/2504.12764v5', None, 'Section 2: Graph Tasks, Graph Generators, Prompt Schemes, Serialization Formats', 'Cited version is arXiv v5, March 25, 2026. Author website states ICLR 2026 acceptance; OpenReview direct access returned a browser challenge, so bibliography conservatively identifies the inspected preprint version.'),
 'dai2024kgunderstanding': ('Xinbang Dai et al., 2024', 'https://arxiv.org/html/2402.11541v4', None, 'Sections 3.1, 4 and 5; input formats, organization, noisy/incomplete KG evaluation', 'Version 4 inspected; initial preprint year 2024 retained, revision January 23, 2025 identified in bibliography.'),
 'tian2025alignment': ('Tian et al., 2025', 'https://ojs.aaai.org/index.php/AAAI/article/view/34716', None, 'Publisher abstract, paragraphs 2-3; How to Cite', 'Metadata and abstract verified. Full PDF resolved initially but subsequent body reads timed out; attempts via /view/ and /download/ plus direct retrieval failed. Sentence is limited to the factor taxonomy explicitly stated in the abstract; no detailed full-text result comparison is asserted.'),
 'wu2024stark': ('Wu et al., 2024', 'https://papers.nips.cc/paper_files/paper/2024/hash/e607b1419e9ae7cd5cb5b5bb60c2ad5c-Abstract-Datasets_and_Benchmarks_Track.html', None, 'Conference PDF Section 2.1, PDF p. 3: output node set satisfies textual and relational requirements', 'Conference metadata and full problem definition inspected.'),
 'he2024gretriever': ('He et al., 2024', 'https://proceedings.nips.cc/paper_files/paper/2024/hash/efaf1c9726648c8ba363a5c927440529-Abstract-Conference.html', None, 'Conference metadata; full-text https://arxiv.org/html/2402.07630v3 Sections 3 and 5.1-5.4, especially Section 5.3', 'Conference PDF retrieval timed out on reread; original-author preprint full text used for the PCST description.'),
 'luo2024rog': ('Luo et al., 2024', 'https://proceedings.iclr.cc/paper_files/paper/2024/hash/3e2aeb66481dd63a32421bf032b70384-Abstract-Conference.html', None, 'Conference PDF Sections 3 and 4.1: relation paths, instantiated reasoning paths, planning-retrieval-reasoning', 'Conference metadata and relevant full text inspected.'),
 'ghandi2026graphwalk': ('Ghandi et al., 2026', 'https://arxiv.org/html/2604.01610v1', None, 'Sections 3-4 and 5.5: incomplete exploration explicitly concerns the no-tool setting', 'Inspected preprint v1, April 2, 2026. No conference status asserted.'),
 'amiraz2025distracting': ('Amiraz et al., 2025', 'https://aclanthology.org/2025.acl-long.892/', None, 'PDF Section 3.1, PDF p. 3, Equation 1; Introduction; official .bib', 'Metadata, definition and surrounding full text inspected. Passage-level semantic distraction is not equated with KG adjacency.'),
 'wu2026toporag': ('Wu and Luo, 2026', 'https://aclanthology.org/2026.findings-acl.1703/', None, 'PDF Section 3.1-3.2, PDF p. 4, Equation 1: cardinality and induced-subgraph diameter constraints', 'Metadata and full formulation inspected. No empirical performance superiority or theorem is reproduced.'),
 'li2025selection': ('Li and Ouyang, 2025', 'https://aclanthology.org/2025.findings-emnlp.218/', None, 'PDF Sections 3.1, 4.1-4.3 and 5; Tables 1-2, Figures 2-4', 'Metadata, experimental construction, and generator/task dependence inspected.'),
}

local_sources = {
 'E-local-pairs': ('result', 'paper/research_notes/analyses/reference_pairing_audit/final/summary.json', '$.checks.reference_in_candidates_checked; $.checks.reference_vs_actual_witness_checked; $.checks.edge_host_placement_checked; $.pairs (Core rendering/hosting and full_braw overlay pairs)', 'Existing offline audit inspected; not rerun. Native-prose sufficiency and original database completeness are not certified.'),
 'E-local-comparison': ('draft', 'paper/research_notes/contribution_comparison.md', 'Task/data/protocol table; What results already overlap; Reuse, limits and decision', 'Prior scoped comparison inspected against local Tool Graph PDF; row-level independence remains unresolved.'),
 'E-local-methodology': ('draft', 'paper/research_notes/methodology.md', 'Definitions to settle; RQs and evidence routes; Scoped contribution decision', 'Task/reference distinctions and inferential limits; not treated as empirical result evidence.'),
 'E-local-final-results': ('result', 'paper/research_notes/analyses/final_results/run-01/motif_size_metrics.csv', 'Header and Core/full_braw rows: precision, recall, exact, N; no numerical result reproduced in revised Related Work', 'Existing saved-result export; not freshly rescored in this revision.'),
}

def dump(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def tex_sentence(text, keys):
    if not keys:
        return text
    return text[:-1] + '~\\cite{' + ','.join(keys) + '}.'

def md_sentence(text, keys):
    text = text.replace('~', ' ')
    if not keys:
        return text
    links = []
    for key in keys:
        label, url, path, _, _ = sources[key]
        if path:
            url = str(ROOT / path)
        links.append(f'[{label}]({url})')
    return text[:-1] + ' (' + '; '.join(links) + ').'

tex = ['\\section{Related Work and Prior Transfer Evidence}', '\\label{sec:related}', '']
md = ['# Related Work and Prior Transfer Evidence', '']
claims = []
entries = []
for pi, (title, sentences) in enumerate(paragraphs, 1):
    tex.extend(['\\paragraph{' + title + '.}', ' '.join(tex_sentence(t, k) for t, k, _ in sentences), ''])
    md.extend(['**' + title + '.** ' + ' '.join(md_sentence(t, k) for t, k, _ in sentences), ''])
    for si, (text, keys, local) in enumerate(sentences, 1):
        cid = f'C-RW3-{pi}-{si}'
        refs = ['E-lit-' + key for key in keys] + local
        # Scope declarations and methodological inferences are distinguished
        # from historical execution claims in the reason field.
        kind = 'literature' if keys else ('historical' if any(local_sources[e][0] == 'result' for e in local) else 'literature')
        status = 'supported'
        inference_only = not keys and not any(local_sources[e][0] == 'result' for e in local)
        if inference_only:
            refs.append('E-lit-anonymousToolGraph' if pi == 1 else 'E-lit-ghandi2026graphwalk')
        reason = ('Inspected primary source supports the narrowly stated proposition; own-task comparison is a scoped inference from the declared reference and frozen-input audit.' if keys else
                  'Describes audited frozen task/reference or reporting scope, without asserting current code produced historical runs.' if kind == 'historical' else
                  'Methodological limit or scope decision grounded in inspected primary task definitions and the local scope audit; not an empirical mechanism or independence finding.')
        if inference_only:
            reason = 'Methodological comparison/inferential limit grounded in the cited primary protocol and local scope decision; not a tested causal hypothesis.'
        if keys == ['tian2025alignment']:
            reason += ' Abstract-level factor taxonomy only; full-text access limitation recorded.'
        claims.append(dict(id=cid, text=text.replace('~', ' '), type=kind, status=status,
                           scope=f'02_related_work_v3.tex paragraph {pi}, sentence {si}', evidence_ids=refs,
                           reason=reason, numeric=False))
        entries.append(dict(paragraph=pi, sentence=si, claim_ids=[cid], evidence_ids=refs,
                            disposition='scope/inference explicitly bounded' if inference_only else 'supported'))

(SECTIONS / '02_related_work_v3.tex').write_text('\n'.join(tex))
(SECTIONS / '02_related_work_v3.md').write_text('\n'.join(md))

base_bib = (SECTIONS / 'related_work_v2.bib').read_text()
blocks = re.split(r'(?=^@)', base_bib, flags=re.M)
selected = []
for block in blocks:
    match = re.match(r'@\w+\{([^,]+),', block)
    if match and match[1] in sources:
        if match[1] == 'anonymousToolGraph':
            block = re.sub(r'note = \{[^\n]+\}', 'note = {Supplied anonymous manuscript; Appendix O}', block)
        if match[1] == 'tian2025alignment':
            block = block.rstrip().removesuffix('}').rstrip() + ',\n  doi = {10.1609/aaai.v39i24.34716},\n  volume = {39},\n  number = {24},\n  pages = {25291--25299}\n}\n'
        selected.append(block.rstrip())

extra_bib = r'''
@inproceedings{luo2024rog,
  author = {Luo, Linhao and Li, Yuan-Fang and Haffari, Reza and Pan, Shirui},
  title = {Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning},
  booktitle = {International Conference on Learning Representations},
  year = {2024},
  url = {https://proceedings.iclr.cc/paper_files/paper/2024/hash/3e2aeb66481dd63a32421bf032b70384-Abstract-Conference.html}
}

@misc{ghandi2026graphwalk,
  author = {Ghandi, Taraneh and Mahyar, Hamidreza and Klaiman, Shachar},
  title = {{GraphWalk}: Enabling Reasoning in Large Language Models through Tool-Based Graph Navigation},
  year = {2026},
  eprint = {2604.01610},
  archivePrefix = {arXiv},
  note = {Version 1, April 2, 2026},
  url = {https://arxiv.org/abs/2604.01610v1}
}

@inproceedings{amiraz2025distracting,
  author = {Amiraz, Chen and Cuconasu, Florin and Filice, Simone and Karnin, Zohar},
  title = {The Distracting Effect: Understanding Irrelevant Passages in {RAG}},
  booktitle = {Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  year = {2025},
  pages = {18228--18258},
  doi = {10.18653/v1/2025.acl-long.892},
  url = {https://aclanthology.org/2025.acl-long.892/}
}

@inproceedings{wu2026toporag,
  author = {Wu, Tianhao and Luo, Siqiang},
  title = {{TopoRAG}: Graph-based {RAG} via Topology-aware Approximate Nearest Neighbor Search},
  booktitle = {Findings of the Association for Computational Linguistics: ACL 2026},
  year = {2026},
  pages = {34097--34108},
  url = {https://aclanthology.org/2026.findings-acl.1703/}
}
'''
bib = '% Self-contained bibliography for Related Work v3; merge by key, do not append duplicate entries.\n' + '\n\n'.join(selected) + '\n\n' + extra_bib.lstrip()
bib = re.sub(r'(title = \{)(.*)(\},?)',
             lambda m: m[1] + re.sub(r'(?<!\{)\b(LLMs?|RAG|GraphOmni|STaRK|G-Retriever)\b(?!\})', r'{\1}', m[2]) + m[3], bib)
(SECTIONS / 'related_work_v3.bib').write_text(bib)

evidence = []
for key, (_, url, path, locator, limitations) in sources.items():
    record = dict(id='E-lit-' + key, kind='literature', locator=locator,
                  verification='inspected', checked_on=DATE, limitations=limitations,
                  metadata_verification='primary landing page or versioned original manuscript',
                  content_verification='abstract_only' if key == 'tian2025alignment' else 'relevant_full_text_inspected')
    if path:
        record.update(path=path, sha256=sha(ROOT / path))
    else:
        record.update(url=url)
    evidence.append(record)
for eid, (kind, path, locator, limitations) in local_sources.items():
    evidence.append(dict(id=eid, kind=kind, path=path, locator=locator,
                         verification='inspected', checked_on=DATE,
                         sha256=sha(ROOT / path), limitations=limitations))
dump('evidence_register.json', dict(schema_version=1, evidence=evidence))
(HERE / 'claims.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in claims))
dump('manuscript_claim_map.json', dict(schema_version=1, checked_on=DATE,
     scope='Only new Related Work v3 replacement for supplied main (2).pdf; no full-manuscript certification',
     source_hashes={str(p.relative_to(ROOT)): sha(p) for p in
                    [SECTIONS / '02_related_work_v3.tex', SECTIONS / '02_related_work_v3.md', SECTIONS / 'related_work_v3.bib']},
     entries=entries))
shutil.copyfile(ROOT / 'paper/research_notes/workflow_state.json', HERE / 'workflow_state.json')
inputs = [Path('/Users/ivan_kirpichev/Downloads/Telegram Desktop/main (2).pdf'),
          Path('/Users/ivan_kirpichev/.codex/attachments/374714ef-aa6e-4a22-89d7-f90207478bc7/Вставленный текст.txt'),
          ROOT / 'paper/research_notes/workflow_state.json']
dump('input_provenance.json', dict(checked_on=DATE, source_revision='f986fa2b3698855ef6665317039fd317d251361c',
     inputs=[dict(path=str(p), sha256=sha(p)) for p in inputs],
     preservation='Original PDF, active older main.tex, all v2 files and user changes preserved.',
     gate='Existing analysis_complete=true and full_writing_ready=true rationale inspected; scoped Related Work revision only.',
     initial_working_tree='Six pre-existing untracked files: v2 tex/md/bib, v2 evidence map/report, experiment_figures_tables_plan.md'))

print(json.dumps(dict(paragraphs=len(paragraphs), sentences=len(claims),
                     cited_sources=len(sources), words=len(re.findall(r"\b[\w'-]+\b", '\n'.join(t for _, ss in paragraphs for t, _, _ in ss)))), indent=2))
