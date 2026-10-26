"""Consolidate inspected component provenance for the active standalone paper.

Historical ledgers are preserved. This is a scoped source/claim check, not a
new experiment, exhaustive literature search, or originality certification.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
NOTES = ROOT/'paper/research_notes'
PAPER = ROOT/'paper/manuscript'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


evidence, claims = {}, {}
for folder in [NOTES/'analyses/intro_related_revision/run-04',
               NOTES/'analyses/motif_description/run-01',
               NOTES/'analyses/motif_recall_layout/run-02']:
    for e in json.loads((folder/'evidence_register.json').read_text(encoding='utf-8'))['evidence']:
        if e['id'] in evidence: assert evidence[e['id']] == e
        evidence[e['id']] = e
    for line in (folder/'claims.jsonl').read_text(encoding='utf-8').splitlines():
        if line.strip():
            c = json.loads(line)
            if c['id'] in claims: assert claims[c['id']] == c
            claims[c['id']] = c

old_evidence = {e['id']:e for e in json.loads((NOTES/'evidence_register.json').read_text(encoding='utf-8'))['evidence']}
old_claims = {c['id']:c for c in [json.loads(s) for s in (NOTES/'claims.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]}
import_ids = ['C-recall-revision-profiles','C-recall-revision-means','C-pr-descriptive-effects',
              'C-nr-groups','C-nr-transitions','C-nr-alternative_rules','C-core-pairing',
              'C-raw-overlay-pairing','C-frozen-reference-consistency',
              'C-table2-all-model-metrics','C-manuscript-recorded-settings']


def import_evidence(eid):
    if eid in evidence: return
    e = copy.deepcopy(old_evidence[eid])
    if 'path' in e:
        p = ROOT/e['path']; actual = sha(p)
        if actual != e.get('sha256'):
            b = p.read_bytes().replace(b'\r\n',b'\n')
            options = {hashlib.sha256(b).hexdigest(),hashlib.sha256(b.replace(b'\n',b'\r\n')).hexdigest()}
            assert e['sha256'] in options, ('Changed evidence needs fresh review',eid)
            e['historical_recorded_sha256'] = e['sha256']; e['sha256'] = actual
            e['limitations'] = e.get('limitations','')+' Scoped byte inspection reproduces historical hash by LF/CRLF normalization only; production record remains historical.'
    evidence[eid] = e
    for upstream in e.get('upstream_evidence_ids',[]): import_evidence(upstream)


for cid in import_ids:
    c = copy.deepcopy(old_claims[cid])
    c['historical_scope'] = c['scope']
    c['scope'] = 'Current standalone manuscript: matching archived score, reference, setting or diagnostic assertions; exact source selectors retained.'
    claims[cid] = c
    for eid in c['evidence_ids']: import_evidence(eid)


def add_local(eid, kind, relative, locator, verification='inspected', **extra):
    evidence[eid] = dict(id=eid,kind=kind,path=relative,sha256=sha(ROOT/relative),locator=locator,
                         verification=verification,checked_on='2026-10-26',**extra)


add_local('E-assembly-numeric','result',str((OUT/'numeric_checks_root.json').relative_to(ROOT)).replace('\\','/'),
          '$.checks:161 table/prose/diagnostic checks and $.main_bar_heights_checked:42; failure/rounding scope recorded','recomputed')
add_local('E-assembly-query','implementation','queries/author_supplied_motif_extraction.cypher',
          'Author-supplied nine-pattern specification; fixed sizes/global LIMIT, not evidence of historical execution') if (ROOT/'queries/author_supplied_motif_extraction.cypher').exists() else None
add_local('E-assembly-cypher','implementation','paper/manuscript/queries/author_query_english_comments.cypher',
          'Nine-pattern Cypher specification and final global LIMIT; source included for description, not executed')
add_local('E-assembly-author','result','paper/research_notes/author_decisions.md',
          'Source graph: recorded direct author confirmation of unchanged snapshot reuse','reported',
          limitations='Author-report log, not independent bytewise source-KG verification.')
claims['C-assembly-source-report'] = dict(id='C-assembly-source-report',text='The authors confirm unchanged reuse of the corporate KG snapshot described by the cited source paper.',
    type='historical',status='supported',scope='Method source-graph paragraph',evidence_ids=['E-assembly-author','E-ir-source-kg'],
    reason='Explicit author confirmation reported as such; no independent snapshot authentication inferred.',numeric=False)
claims['C-assembly-cypher-scope'] = dict(id='C-assembly-cypher-scope',text='The supplied appendix Cypher defines fixed small pattern instances with a global LIMIT and does not reconstruct the complete archived sampling grid.',
    type='implementation',status='supported',scope='Method and appendix Cypher specification',evidence_ids=['E-assembly-cypher'],
    reason='Read the included specification; no execution history inferred.',numeric=False)
claims['C-assembly-numeric'] = dict(id='C-assembly-numeric',text='The current numeric table cells and principal abstract/prose/diagnostic examples reproduce the declared saved sources after documented rounding.',
    type='empirical',status='supported',scope='Active tables, abstract and selected numerical prose; see numeric_checks_root.json',
    evidence_ids=['E-assembly-numeric'],reason='Fresh bounded comparison of saved means/counts; not raw-response rescoring.',numeric=False)
claims['C-assembly-motif-roles'] = dict(id='C-assembly-motif-roles',text='The manuscript distinguishes anchor, endpoints and intermediate entities; the compact key colors only anchors and preserves factual edge direction.',
    type='historical',status='supported',scope='Compact main figure, short Method and detailed motif appendix',
    evidence_ids=['E-mrl-figure','E-mrl-shapes','E-motif-core'],reason='Current small glyphs use blue anchors and white other vertices; endpoint/intermediate distinctions are defined in text rather than encoded by the old large diagram colors.',numeric=False)

# Follow the exact active inclusion graph, including tables and motif snippets.
paths, seen = [],set()
def visit(p):
    if p in seen:return
    seen.add(p); paths.append(p)
    text=p.read_text(encoding='utf-8')
    for name in re.findall(r'\\input\{([^}]+)\}',text):
        child=PAPER/name
        if not child.suffix:child=child.with_suffix('.tex')
        assert child.is_file();visit(child)
visit(PAPER/'main.tex')
full='\n'.join(p.read_text(encoding='utf-8') for p in paths)
assert not re.search(r'anonymousToolGraph|Tool Graph Complexity|Tool[- ]to[- ]KG|tool selection',full,re.I)
cited={key.strip() for group in re.findall(r'\\cite\w*\{([^}]+)\}',full) for key in group.split(',')}
bibkeys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',(PAPER/'references.bib').read_text(encoding='utf-8')))
assert cited<=bibkeys
labels=re.findall(r'\\label\{([^}]+)\}',full); assert len(labels)==len(set(labels))
assert set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',full))<=set(labels)
for p in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',full): assert (PAPER/p).is_file()

groups={
'01_recall_introduction.tex':['C-ir-web-search','C-ir-text-relations','C-ir-exhaustive','C-ir-kg','C-ir-pairs','C-ir-design','C-ir-gain','C-ir-transition'],
'02_recall_related_work.tex':['C-ir-luo2024rog','C-ir-wu2024stark','C-ir-he2024gretriever','C-ir-talk','C-ir-pattern','C-ir-kgprompt','C-ir-walk','C-ir-exhaustive'],
'03_recall_method.tex':['C-assembly-source-report','C-assembly-cypher-scope','C-frozen-reference-consistency','C-core-pairing','C-raw-overlay-pairing','C-ir-exhaustive'],
'04_recall_setup.tex':['C-core-pairing','C-raw-overlay-pairing','C-manuscript-recorded-settings','C-nr-groups','C-ir-design','C-recall-revision-means'],
'05_recall_results.tex':['C-recall-revision-profiles','C-recall-revision-means','C-pr-descriptive-effects','C-table2-all-model-metrics','C-nr-groups','C-nr-transitions','C-mrl-recall','C-mrl-directions','C-assembly-numeric'],
'06_recall_discussion.tex':['C-ir-gain','C-pr-descriptive-effects','C-nr-transitions','C-nr-alternative_rules','C-ir-exhaustive','C-assembly-source-report'],
'07_recall_conclusion.tex':['C-ir-gain','C-pr-descriptive-effects','C-nr-transitions'],
'08_recall_appendix.tex':['C-recall-revision-profiles','C-recall-revision-means','C-nr-groups','C-nr-transitions','C-nr-alternative_rules','C-assembly-cypher-scope','C-assembly-numeric'],
'motif_summary.tex':[cid for cid in claims if cid.startswith('C-motif-') and cid!='C-motif-roles']+['C-assembly-motif-roles'],
'motif_definitions.tex':[cid for cid in claims if cid.startswith('C-motif-') and cid!='C-motif-roles']+['C-assembly-motif-roles'],
'main.tex':['C-ir-design','C-pr-descriptive-effects','C-table2-all-model-metrics','C-assembly-numeric'],
}
entries=[]
for p in paths:
    ids=groups.get(p.name,['C-assembly-numeric','C-recall-revision-means','C-recall-revision-profiles'])
    assert all(cid in claims for cid in ids)
    text=p.read_text(encoding='utf-8'); offset=0
    for i,para in enumerate(re.split(r'\n\s*\n',text),1):
        if not para.strip():continue
        start=text.find(para,offset);offset=start+len(para)
        entries.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),paragraph=i,
                            start_line=text[:start].count('\n')+1,claim_ids=ids,
                            scope_note='Grouped semantic/source bindings; mathematical definitions and research questions are not new empirical findings. Hypotheses remain hypotheses.'))
mapping=dict(schema_version=1,checked_on='2026-10-26',intended_scope='Active standalone KG manuscript, all active sections/tables/captions and abstract',entries=entries,
             claims_path=(OUT/'claims.jsonl').relative_to(ROOT).as_posix(),evidence_register_path=(OUT/'evidence_register.json').relative_to(ROOT).as_posix(),
             limitations=['Mappings do not automatically prove every sentence. Existing cached metrics and prior archive audits remain their stated evidence tier.',
                          'No new raw-response parsing, model run, inference interval or exhaustive originality check.',
                          'Publication/reuse eligibility is not certified by assembly.'])
write(OUT/'manuscript_claim_map.json',mapping)
write(OUT/'evidence_register.json',dict(schema_version=1,evidence=list(evidence.values())))
(OUT/'claims.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in claims.values()),encoding='utf-8')
state=json.loads((NOTES/'workflow_state.json').read_text(encoding='utf-8'))
state['writing_scope']='Author-authorized standalone KG entity-selection manuscript assembled from verified existing tasks, saved score analyses, public related work, paired evidence comparisons and bounded output diagnostics. No unpublished Tool Selection citation, new dataset, independent replication, causal mechanism or QA-gain claim.'
state['latest_full_assembly']=dict(date='2026-10-26',source='paper/manuscript/main.tex',pdf='paper/manuscript/main.pdf',
    pages=11,main_text_pages=6,reference_pages=1,appendix_pages=4,compiler='Tectonic0.17.0 untrusted',
    source_scope=OUT.relative_to(ROOT).as_posix(),claim_map=(OUT/'manuscript_claim_map.json').relative_to(ROOT).as_posix(),
    new_experiments=False,submission_ready=False,review='Numeric source checks, scoped semantic preflight, full PDF visual inspection; not originality certification.')
state['submission_ready']=False
write(NOTES/'workflow_state.json',state);write(OUT/'workflow_state.json',state)
backup=OUT/'previous_registry';backup.mkdir(exist_ok=True)
for name in ['manuscript_claim_map.json']:
    source=NOTES/name
    if source.exists() and not (backup/name).exists():(backup/name).write_bytes(source.read_bytes())
write(NOTES/'manuscript_claim_map.json',mapping)
command=[sys.executable,str(NOTES/'scripts/validate_research_artifacts.py'),'--root',str(ROOT),'--notes',str(OUT)]
run=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
validation=json.loads(run.stdout);write(OUT/'validation.json',validation)
assert run.returncode==0,validation
write(OUT/'source_checks.json',dict(active_tex_files=len(paths),cited_keys=sorted(cited),missing_citations=[],
    missing_refs=[],duplicate_labels=[],unpublished_reference_absent=True,numeric_verification='numeric_checks_root.json',
    source_manifest=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths]))
print(json.dumps(dict(status='passed',evidence=len(evidence),claims=len(claims),bindings=len(entries),active_tex=len(paths))))
