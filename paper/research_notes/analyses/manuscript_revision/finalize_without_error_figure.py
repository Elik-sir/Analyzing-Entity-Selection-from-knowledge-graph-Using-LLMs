"""Record an authorized editorial removal; existing results are unchanged."""
import copy
import hashlib
import json
from pathlib import Path
import re
import zipfile

from pypdf import PdfReader
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[4]
NOTES = ROOT / 'paper/research_notes'
PAPER = ROOT / 'paper/manuscript'
OUT = Path(__file__).parent / 'run-02'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    maintext = (PAPER / 'main.tex').read_text(encoding='utf-8')
    sections = [PAPER / (s + '.tex') for s in re.findall(r'\\input\{(sections/[^}]+)\}', maintext)]
    full = maintext + '\n' + '\n'.join(p.read_text(encoding='utf-8') for p in sections)
    assert 'fig:errors' not in full and 'residual_errors.pdf' not in full
    assert 'omission-only' not in full and 'inclusion-only' not in full
    figures = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', full)
    assert len(figures) == 4 and all((PAPER / f).is_file() for f in figures)
    assert len(re.findall(r'\\begin\{figure\*?\}', (PAPER / 'sections/05_recall_results.tex').read_text(encoding='utf-8'))) == 2
    labels = re.findall(r'\\label\{([^}]+)\}', full)
    refs = set(re.findall(r'\\ref\{([^}]+)\}', full))
    assert len(labels) == len(set(labels)) and refs <= set(labels)
    bib = (PAPER / 'references.bib').read_text(encoding='utf-8')
    keys = set(re.findall(r'@\w+\{([^,]+),', bib))
    cites = {k.strip() for g in re.findall(r'\\cite\w*\{([^}]+)\}', full) for k in g.split(',')}
    assert cites <= keys
    old_release = json.loads((OUT.parent / 'run-01/release_manifest.json').read_text(encoding='utf-8'))
    for path, digest in old_release['files'].items():
        if path.startswith(('figures/', 'tables/')) or path in ['references.bib', 'acmart.cls', 'ACM-Reference-Format.bst']:
            assert sha(PAPER / path) == digest, path

    oldmap = json.loads((OUT / 'manuscript_claim_map.json').read_text(encoding='utf-8'))
    groups = {}
    for e in oldmap['entries']:
        if 'paragraph' in e:
            groups[e['path']] = e['claim_ids']
    entries = []
    for p in sections:
        path = str(p.relative_to(ROOT)).replace('\\', '/')
        text = p.read_text(encoding='utf-8')
        ids = [cid for cid in groups[path] if cid != 'C-assets-errors']
        cursor = 0
        for i, para in enumerate(re.split(r'\n\s*\n', text)):
            if not para.strip():
                continue
            offset = text.find(para, cursor)
            cursor = offset + len(para)
            entries.append(dict(path=path, sha256=sha(p), paragraph=i+1,
                                start_line=text[:offset].count('\n')+1, claim_ids=ids,
                                scope_note='Existing claim families retained after editorial removal; no new measurements or mechanism claims.'))
    for e in oldmap['entries']:
        if 'paragraph' in e or e.get('locator') == 'figure:residual_errors':
            continue
        e = copy.deepcopy(e)
        if e.get('path') == 'paper/manuscript/main.tex':
            e['sha256'] = sha(PAPER / 'main.tex')
        entries.append(e)
    newmap = copy.deepcopy(oldmap)
    newmap['entries'] = entries
    newmap['revision_note'] = 'Author requested removal of the former main Figure 3 and condensed error-category discussion; retained plots/tables unchanged.'
    write(NOTES / 'manuscript_claim_map.json', newmap)

    pdf = PdfReader(PAPER / 'main.pdf')
    textpages = [p.extract_text() for p in pdf.pages]
    text = '\n'.join(textpages)
    assert 'Output categories with explicit relations' not in text
    assert 'Figure 3: Precision companion to Figure 1' in text
    assert 'Figure 4: Precision companion to Figure 2' in text
    log = (PAPER / 'main.log').read_text(encoding='utf-8', errors='replace')
    assert not re.search(r'Overfull \\[hv]box|(?:Reference|Citation) .*undefined|There were undefined', log)
    assert len(pdf.pages) == 10
    qa = OUT / 'qa_final'
    qa.mkdir(exist_ok=True)
    doc = pdfium.PdfDocument(PAPER / 'main.pdf')
    for i in range(len(doc)):
        doc[i].render(scale=1.5).to_pil().save(qa / f'page-{i+1:02}.png')
    checks = dict(pages=10, main_pages=6, references_pages=[7], appendix_pages=[8,9,10],
                  main_figures=2, main_tables=2, appendix_figures=2,
                  figure_labels_resolved=True, retained_asset_hashes_unchanged=True,
                  removed_error_category_terms=True, unresolved_references=0, overfull_boxes=0,
                  visual_review='pending', pdf_sha256=sha(PAPER / 'main.pdf'), metadata=dict(pdf.metadata))
    write(OUT / 'pdf_checks.json', checks)

    readme = (PAPER / 'README.md').read_text(encoding='utf-8')
    readme = readme.replace('Main results contain three figures and two tables', 'Main results contain two figures and two tables')
    readme = readme.replace('and residual errors.', 'and remaining route-coverage failures.')
    readme = readme.replace('## Current recall-led revision, 2026-10-26', '## Current recall-led revision, 2026-10-26\n\nThe former main Figure 3 (stacked error categories) was removed at the author\'s request. Its detailed count discussion and unused category definitions were removed. The adjacent-context result remains supported by the recall profiles and Table 1. Precision figures in the appendix are now Figures 3 and 4. Revision evidence and the previous PDF/source archive are preserved in `../research_notes/analyses/manuscript_revision/run-02/`.')
    (PAPER / 'README.md').write_text(readme, encoding='utf-8')
    build = (NOTES / 'build_report.md').read_text(encoding='utf-8')
    addition = '''## Removal of the error-category figure, 2026-10-26

At the author's request, the former main Figure 3 and its detailed category-count discussion were removed. Unused category definitions and related abstract/discussion wording were condensed. The two main Recall figures and two tables are unchanged; appendix Precision figures are renumbered 3 and 4. No new experimental result or numerical estimate was added.

Tectonic 0.17.0 rebuilt `paper/manuscript/main.pdf` successfully using `--untrusted --only-cached --keep-logs --keep-intermediates main.tex`. Diagnostics: `paper/manuscript/build-without-error-figure.txt` and `main.log`. Zero overfull boxes and no unresolved references/citations. The PDF remains 10 pages (main 1-6, references 7, appendix 8-10); no typography or page geometry was changed. Visual QA is recorded separately in `analyses/manuscript_revision/run-02/pdf_checks.json`.

Previous PDF, active section sources, source archive and claim map are preserved under `analyses/manuscript_revision/run-02/`. Retained figure/table and bibliography hashes match the previous release. This editorial revision does not resolve the previously recorded independent-review/originality limitations.

'''
    build = build.replace('## Current recall-led revision, 2026-10-26', '## Earlier recall-led revision, 2026-10-26', 1)
    (NOTES / 'build_report.md').write_text(build.replace('# Manuscript build report\n\n', '# Manuscript build report\n\n' + addition, 1), encoding='utf-8')
    state = json.loads((NOTES / 'workflow_state.json').read_text(encoding='utf-8'))
    state['stages']['main_text_assets'] = 'two_recall_figures_and_two_main_tables;error_category_figure_removed_by_author'
    state['editorial_revision'] = dict(date='2026-10-26', rationale='Author requested deleting the error-category graph and condensing its discussion.', record='analyses/manuscript_revision/run-02/')
    write(NOTES / 'workflow_state.json', state)

    ledger = json.loads((NOTES / 'evidence_register.json').read_text(encoding='utf-8'))
    additions = []
    for e in ledger['evidence']:
        path = e.get('path')
        if not path or not (ROOT / path).is_file() or sha(ROOT / path) == e.get('sha256'):
            continue
        if path.startswith('paper/manuscript/'):
            previous = OUT / 'previous_manuscript' / Path(path).relative_to('paper/manuscript')
        elif path in ['paper/research_notes/manuscript_claim_map.json', 'paper/research_notes/build_report.md']:
            previous = OUT / Path(path).name
        else:
            continue  # Preserve unrelated historical LF/CRLF mismatches.
        assert previous.is_file() and sha(previous) == e['sha256'], (e['id'], previous)
        current = copy.deepcopy(e)
        current.update(id=e['id']+'-without-error-figure', sha256=sha(ROOT / path), checked_on='2026-10-26',
                       verification='inspected', revision_note='Author-requested editorial removal; previous bytes preserved in run-02.')
        additions.append(current)
        e['historical_original_path'] = path
        e['path'] = str(previous.relative_to(ROOT)).replace('\\', '/')
    ledger['evidence'].extend(additions)
    write(NOTES / 'evidence_register.json', ledger)

    files = [p for p in old_release['files'] if p != 'figures/residual_errors.pdf']
    with zipfile.ZipFile(PAPER / 'recall_revision_sources.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for path in files:
            z.write(PAPER / path, path)
    release = dict(checked_on='2026-10-26', scope='Editorial removal of error-category Figure 3; no new empirical claims.',
                   files={p:sha(PAPER / p) for p in files}, pdf_sha256=sha(PAPER / 'main.pdf'),
                   source_archive_sha256=sha(PAPER / 'recall_revision_sources.zip'),
                   preserved_previous_pdf_sha256=sha(OUT / 'previous_manuscript/main.pdf'),
                   checks='pdf_checks.json', original_results_unchanged=True, submission_performed=False)
    write(OUT / 'release_manifest.json', release)
    print(json.dumps(dict(pages=10, main_figures=2, appendix_figures=2, archive_files=len(files), rebound_historical_records=len(additions))))


if __name__ == '__main__':
    main()
