# Scoped validation report

October 26, 2026. Commands ran from the repository root with `/Users/ivan_kirpichev/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.

1. `paper/research_notes/analyses/related_work_revision_2026-10-26/build_revision.py`: completed; five paragraphs, 27 sentence records, 13 cited works. The reported 526-word count excludes paragraph titles and expanded citation labels.
2. `paper/research_notes/scripts/validate_research_artifacts.py --root . --notes paper/research_notes/analyses/related_work_revision_2026-10-26`: **passed**, 17 scoped evidence records, 27 scoped claims, zero structural errors.
3. `paper/research_notes/scripts/validate_research_artifacts.py --root .`: **passed**, 60 existing global evidence records, 27 existing global claims, zero structural errors. This is separate from the scoped ledger and does not certify new prose.
4. Static citation and syntax checks: all 13 cited keys have exactly one bibliography entry; no unresolved or duplicate keys; TeX/BibTeX braces balanced; deliverable links in revision notes resolve; all 27 sentence records have explicit support dispositions. Results saved in `syntax_checks.json`.

Neither `bibtexparser` nor `pybtex` was available in the bundled Python; no full BibTeX-parser or typesetting pass is claimed. The current deliverable is a section insertion plus bibliography for the supplied PDF's source project. The active older manuscript was not compiled with this insertion, and no PDF layout or page-limit pass is implied.

Semantic review covered all 27 sentences of the new section and their recorded source locators, including methodological comparisons and own-task descriptions. Most literature propositions use inspected relevant full text; Tian et al. is limited to the verified abstract taxonomy, with access failures recorded. This was a single-agent scoped revision, not independent full-manuscript scientific review. Structural-validator success does not certify scientific truth.

`git diff --stat` remained empty: no tracked pre-existing file was edited. New variant and audit files are untracked, alongside the six files already untracked at entry. No experiment, judge, database, publication, upload, or submission operation occurred.
