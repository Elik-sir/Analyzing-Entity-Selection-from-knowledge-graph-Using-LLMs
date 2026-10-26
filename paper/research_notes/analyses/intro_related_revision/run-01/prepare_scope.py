"""Record this bounded editorial proposal and check its provenance/citations.

Reads existing files only; writes derived records next to this script.
No model, judge, database, network, or source-code mutation.
"""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
PROPOSAL = ROOT / 'paper/manuscript/proposals/transfer_intro_related_v1'
DATE = '2026-10-26'


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


sources = [
    dict(key='luo2024rog', title='Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning',
         metadata='https://proceedings.iclr.cc/paper_files/paper/2024/hash/3e2aeb66481dd63a32421bf032b70384-Abstract-Conference.html',
         full_text='https://proceedings.iclr.cc/paper_files/paper/2024/file/3e2aeb66481dd63a32421bf032b70384-Paper-Conference.pdf',
         locator='Section 4.1: planning, retrieval, reasoning',
         supported='Relation-path planning guides KG reasoning-path retrieval and answer generation.'),
    dict(key='wu2024stark', title='STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases',
         metadata='https://papers.nips.cc/paper_files/paper/2024/hash/e607b1419e9ae7cd5cb5b5bb60c2ad5c-Abstract-Datasets_and_Benchmarks_Track.html',
         full_text='https://arxiv.org/html/2404.13207v1',
         locator='Inspected preprint v1, Section 3.2; official proceedings for metadata',
         supported='Answer-node retrieval under combined textual and relational query requirements.'),
    dict(key='he2024gretriever', title='G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering',
         metadata='https://papers.nips.cc/paper_files/paper/2024/hash/efaf1c9726648c8ba363a5c927440529-Abstract-Conference.html',
         full_text='https://arxiv.org/html/2402.07630v3',
         locator='Inspected preprint v3, Sections 5.2-5.4; official proceedings for metadata',
         supported='Prize-collecting Steiner tree constructs connected textual-graph context for QA.')
]
for source in sources:
    source.update(checked_on=DATE, verification='Primary metadata and relevant full text inspected by delegated literature-review agent; not an exhaustive novelty search.')
write_json('source_checks.json', {'sources': sources, 'omitted_optional_keys': [
    'xu2026graphomni', 'tian2025alignment', 'wu2026toporag', 'amiraz2025distracting', 'li2025selection'],
    'omission_reason': 'Short proposal keeps the most direct task comparisons; omission is editorial, not a falsity finding.'})

attached = Path('C:/Users/ekurm/Downloads/Telegram Desktop/02_related_work_v4.tex')
snapshot = OUT / 'attached_related_work_v4.tex'
attached_bytes = attached.read_bytes()
if snapshot.exists() and snapshot.read_bytes() != attached_bytes:
    raise RuntimeError('Existing attachment snapshot differs; use a fresh run directory.')
snapshot.write_bytes(attached_bytes)

with gzip.open(ROOT / 'results/inputs.jsonl.gz', 'rt', encoding='utf-8') as stream:
    sample = json.loads(next(stream))
system = next(m['content'] for m in sample['messages'] if m['role'] == 'system')
assert 'Include entities from all parallel supporting routes.' in system
assert 'membership does not imply that each selected card is independently necessary evidence' in system
write_json('selection_protocol_sample.json', {
    'input_id': sample['input_id'], 'question': sample['question'], 'system_instruction': system,
    'source': 'results/inputs.jsonl.gz', 'source_locator': 'First JSONL record; messages[role=system].content',
    'scope': 'Fresh single-record inspection, contextualized by the prior full frozen-reference audit; not a new archive-wide protocol audit.'})

with (ROOT / 'paper/research_notes/analyses/final_results/run-01/condition_metrics.csv').open(encoding='utf-8', newline='') as stream:
    rows = [r for r in csv.DictReader(stream) if r['series_id'] == 'full_braw' and r['condition'] in ('Braw', 'Braw+E')]
gains = []
for model in sorted({r['model'] for r in rows}):
    pair = {r['condition']: r for r in rows if r['model'] == model}
    delta = float(pair['Braw+E']['recall']) - float(pair['Braw']['recall'])
    assert delta > 0
    gains.append({'model': model, 'recall_delta': delta, 'planned_N_each': int(pair['Braw']['N']),
                  'formula': 'failure-inclusive macro recall(Braw+E) minus macro recall(Braw); cached aggregate source; no new inference'})
write_json('qualitative_result_check.json', {'positive_overlay_differences': gains})

evidence = []


def local(eid, kind, path, locator, verification='inspected', limitations=None):
    record = dict(id=eid, kind=kind, path=path, sha256=sha(ROOT / path), locator=locator,
                  verification=verification, checked_on=DATE)
    if limitations:
        record['limitations'] = limitations
    evidence.append(record)


relative_out = OUT.relative_to(ROOT).as_posix()
local('E-ir-prompt', 'result', relative_out + '/selection_protocol_sample.json', '$.system_instruction and $.question')
local('E-ir-reference', 'result', 'paper/research_notes/analyses/reference_pairing_audit/final/summary.json',
      '$.checks, $.coverage and $.pairs; see prior reference_pairing_report.md for definitions', 'reported', 'Prior audit inspected; not rerun in this editorial task.')
local('E-ir-reference-report', 'draft', 'paper/research_notes/reference_pairing_report.md', 'Reference consistency, candidate coverage and paired invariants', 'reported')
local('E-ir-tool', 'literature', 'paper/research_notes/sources/tool_graph_complexity.pdf',
      'Section 5.3/Table 1 and Appendix O, PDF pages 8 and 30-31', 'reported', 'Prior primary inspection recorded in transfer_positioning.md and contribution_comparison.md; no fresh PDF rendering.')
local('E-ir-position', 'draft', 'paper/research_notes/transfer_positioning.md', 'Source interpretation and align-the-constructs comparison')
local('E-ir-source-kg', 'literature', '11_Towards_Ontology_Driven_Mul.pdf', 'Title and graph-construction context; prior literature_review.md verification', 'reported')
local('E-ir-results', 'result', relative_out + '/qualitative_result_check.json', '$.positive_overlay_differences')
local('E-ir-conditions', 'result', 'paper/research_notes/analyses/final_results/run-01/condition_metrics.csv',
      'series_id=full_braw, condition in {Braw,Braw+E}, noise=disconnected; recall column')
local('E-ir-transitions', 'result', 'paper/research_notes/analyses/novelty_refinement/run-02/summary.json',
      '$.groups, transition matrices, $.validation and $.limitations; Core six-node Tree-in', 'reported', 'Bounded prior analysis; no new transitions or uncertainty calculated.')
local('E-ir-transitions-report', 'draft', 'paper/research_notes/novelty_refinement.md', 'Paired signature transitions and diagnostic identifiability limits')
local('E-ir-attachment', 'draft', relative_out + '/attached_related_work_v4.tex', 'All five Related Work paragraphs')
for source in sources:
    evidence.append(dict(id='E-ir-' + source['key'], kind='literature', url=source['full_text'],
                         locator=source['locator'], verification='inspected', checked_on=DATE,
                         limitations=source['verification']))
for eid, url, locator in [
    ('E-ir-talk', 'https://proceedings.iclr.cc/paper_files/paper/2024/file/bf72f65f30eedf5d48da6980ee02b589-Paper-Conference.pdf', 'Sections 1-3 and encoding appendix; prior literature_review.md and novelty_refinement.md inspection'),
    ('E-ir-pattern', 'https://arxiv.org/html/2410.05298v2', 'Sections 2-5; prior literature_review.md inspection'),
    ('E-ir-kgprompt', 'https://arxiv.org/html/2402.11541v4', 'Sections 3-5; prior literature_review.md inspection'),
    ('E-ir-walk', 'https://arxiv.org/html/2604.01610v1', 'Sections 4 and 5.5; prior novelty_refinement.md inspection')]:
    evidence.append(dict(id=eid, kind='literature', url=url, locator=locator,
                         verification='reported', checked_on=DATE,
                         limitations='Prior primary-text audit reused; no fresh full-paper verification in this task.'))
write_json('evidence_register.json', {'schema_version': 1, 'evidence': evidence})

claims = []


def claim(cid, text, kind, refs, scope, reason):
    claims.append(dict(id=cid, text=text, type=kind, status='supported', scope=scope,
                       evidence_ids=refs, reason=reason, numeric=False))


claim('C-ir-exhaustive', 'The archived selection protocol requires the anchor, endpoints, intermediates and parallel-route entities; it distinguishes this from indispensable-card evidence.',
      'historical', ['E-ir-prompt', 'E-ir-reference'], 'Introduction P3; Related Work P2/P4',
      'Fresh protocol example plus prior archive/reference audit; do not equate selection instruction with endpoint-answer wording.')
claim('C-ir-tool', 'Tool Graph Complexity reports pattern-associated selection profiles and already includes KG transfer, Chain inversion, incoming-tree and adjacent-decoy observations.',
      'literature', ['E-ir-tool', 'E-ir-position'], 'Introduction P1/P4; Related Work P1', 'Prior primary source review retained; no first-transfer or shared-mechanism assertion.')
claim('C-ir-kg', 'The cited corporate KG was developed for GraphRAG evaluation and includes the entity classes described in the proposal.',
      'literature', ['E-ir-source-kg'], 'Introduction P3; Related Work P2', 'Prior source-paper review; no new graph-construction contribution.')
claim('C-ir-pairs', 'Archived KG comparisons separate relation addition, designated-fact presentation and adjacent-context changes.',
      'empirical', ['E-ir-reference', 'E-ir-reference-report'], 'Introduction P5; Related Work P4', 'Prior frozen-pair audit; native sufficiency and isolated K4 placement causality excluded.')
claim('C-ir-gain', 'Relation-overlay conditions have higher failure-inclusive macro recall in each archived model.',
      'empirical', ['E-ir-results', 'E-ir-conditions'], 'Introduction P8', 'Fresh bounded sign check of the existing macro CSV; no new model output or inference.')
claim('C-ir-transition', 'The bounded Tree-in analysis contains both presentation corrections and regressions, and lower one-hop frequency need not imply comparable exact-recovery improvement.',
      'empirical', ['E-ir-transitions', 'E-ir-transitions-report'], 'Introduction P7/P8; Related Work P4', 'Prior paired analysis restricted to Core six-node Tree-in; no model-universal internal traversal conclusion.')
for source in sources:
    claim('C-ir-' + source['key'], source['supported'], 'literature', ['E-ir-' + source['key']],
          'Related Work P2', 'Narrow proposition verified against primary relevant text by delegated literature-review agent.')
for cid, text, eid in [
    ('C-ir-talk', 'Talk like a Graph evaluates graph encoding, task and structure axes.', 'E-ir-talk'),
    ('C-ir-pattern', 'Graph-pattern comprehension and discovery are studied using terminological and topological descriptions.', 'E-ir-pattern'),
    ('C-ir-kgprompt', 'KG-prompt work studies formats, triple organization and noisy/incomplete evidence with answer-based evaluation.', 'E-ir-kgprompt'),
    ('C-ir-walk', 'GraphWalk studies graph navigation and reports incomplete exploration with directly supplied graph context.', 'E-ir-walk')]:
    claim(cid, text, 'literature', [eid], 'Related Work P3/P4', 'Prior primary-text verification reused for a narrow contextual statement.')
(OUT / 'claims.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in claims), encoding='utf-8')

write_json('workflow_state.json', json.loads((ROOT / 'paper/research_notes/workflow_state.json').read_text(encoding='utf-8')))
bindings = {
    '01_introduction.tex': [
        ['C-ir-tool'], ['C-ir-tool'], ['C-ir-exhaustive', 'C-ir-kg'], ['C-ir-tool'],
        ['C-ir-pairs'], ['C-ir-tool', 'C-ir-pairs', 'C-ir-transition'],
        ['C-ir-pairs', 'C-ir-transition'], ['C-ir-gain', 'C-ir-transition']],
    '02_related_work.tex': [
        ['C-ir-tool'], ['C-ir-luo2024rog', 'C-ir-wu2024stark', 'C-ir-he2024gretriever', 'C-ir-exhaustive', 'C-ir-kg'],
        ['C-ir-talk', 'C-ir-pattern'], ['C-ir-kgprompt', 'C-ir-walk', 'C-ir-pairs', 'C-ir-transition']]
}
entries = []
for filename, groups in bindings.items():
    path = PROPOSAL / filename
    for i, group in enumerate(groups, 1):
        entries.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path),
                        'paragraph': i, 'claim_ids': group})
write_json('manuscript_claim_map.json', {'scope': 'Only the two proposed sections; grouped substantive claims. RQs are questions, motivation and metric definitions are not empirical results; this map is not an originality certificate.', 'entries': entries})

bib = (ROOT / 'paper/manuscript/references.bib').read_text(encoding='utf-8') + '\n' + (PROPOSAL / 'additional_references.bib').read_text(encoding='utf-8')
available = re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib)
used = set()
brace_checks = {}
for filename in bindings:
    text = (PROPOSAL / filename).read_text(encoding='utf-8')
    for group in re.findall(r'\\cite\w*\{([^}]+)\}', text):
        used.update(key.strip() for key in group.split(','))
    brace_checks[filename] = text.count('{') == text.count('}')
static = {'missing_citation_keys': sorted(used - set(available)),
          'duplicate_citation_keys': sorted({k for k in available if available.count(k) > 1}),
          'balanced_brace_counts': brace_checks, 'used_citation_keys': sorted(used),
          'pdf_compiled': False, 'active_manuscript_replaced': False}
assert not static['missing_citation_keys'] and not static['duplicate_citation_keys'] and all(brace_checks.values())
write_json('static_checks.json', static)
result = subprocess.run([sys.executable, str(ROOT / 'paper/research_notes/scripts/validate_research_artifacts.py'),
                         '--root', str(ROOT), '--notes', str(OUT)], capture_output=True, text=True, encoding='utf-8')
validation = json.loads(result.stdout)
write_json('validation.json', validation)
assert result.returncode == 0, validation
manifest = {'checked_on': DATE, 'source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'working_tree': 'Existing manuscript/research-note edits present; sources identified by actual hashes.',
            'external_attachment': {'path': str(attached), 'sha256': hashlib.sha256(attached_bytes).hexdigest()},
            'files': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in sorted(PROPOSAL.iterdir()) if p.is_file()],
            'validation_command': '.venv/Scripts/python.exe paper/research_notes/scripts/validate_research_artifacts.py --root . --notes paper/research_notes/analyses/intro_related_revision/run-01',
            'limits': 'Scoped structural validation only; no production evidence hash repairs, PDF build, new experiment or novelty certification.'}
write_json('manifest.json', manifest)
print(json.dumps({'scoped_validation': validation['status'], 'claims': len(claims), 'evidence': len(evidence), 'citation_keys': len(used), 'pdf_compiled': False}))
