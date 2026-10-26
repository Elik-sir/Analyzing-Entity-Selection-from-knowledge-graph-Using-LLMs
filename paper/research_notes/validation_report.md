# Skill system validation

## Latest transfer-positioning validation, 2026-10-25

Assessment at `f986fa2b3698855ef6665317039fd317d251361c`, clean at entry. Added `transfer_positioning.md`, `transfer_outline.md`, a bounded saved-score/selection diagnostic script and separate derived outputs. Updated the methodology, plan, gaps, literature log and workflow to the author's corrected scientific purpose. The old manuscript/PDF and all research sources/results remain unchanged. Full writing is pending for the stronger contribution; the completed assessment is not itself a completed new cross-domain study.

Commands (using the bundled Python executable at `C:/Users/Valery/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` with `-X utf8`):

```text
python paper/research_notes/analyses/transfer_positioning/diagnose_transfer.py --out paper/research_notes/analyses/transfer_positioning/run-04
python paper/research_notes/analyses/transfer_positioning/register_and_check.py
python paper/research_notes/scripts/validate_research_artifacts.py --root . --notes paper/research_notes/analyses/transfer_positioning/run-04/assessment_audit
git diff --check
```

Retained numeric checks pass: 69 primary groups and 120 supplementary groups agree with the prior detailed CSV; the maximum primary F1 discrepancy is `8.881784197001252e-16`. Saved-selection set-score agreement and independent public-graph witness/endpoint checks pass for the included route scope; 2,581 unique valid route rows are retained. Pair/category conservation and recorded source hashes pass. New scoped structural check passes with 11 evidence records and 8 claim records. Exact results: `analyses/transfer_positioning/run-04/assessment_audit/validation.json`.

The production structural check currently reports 47 older text-file hash mismatches. New assessment entries pass; older hashes were not refreshed. An earlier read-only byte check in this chat established LF/CRLF equivalence for the differing local sources. Scoped success does not make the production check pass or certify semantic truth. No independent reviewer, hypothesis test, complete raw-response reparse, new model experiment or final manuscript build was performed in this reassessment.

Run history: run 01 stopped before output when a frozen input lacked `task_spec`; run 02 explicitly excluded missing specifications; run 03 added cached controlled contrasts; run 04 adds the targeted Tree-in role diagnostics. Earlier outputs are preserved as superseded, and their script hashes refer to those earlier script bytes. PDF rendering first found PyMuPDF unavailable and then succeeded with bundled pypdfium2; pages 8, 30 and 31 were visually inspected. New PDF identity is byte-equal to the archived source. No dependencies were installed.

Checked 2026-10-25. Source revision: `261f1b3cc3d3bf3419c04d3d0a35d290fce73cae`.

## Completed checks

- All eight requested skill folders contain `SKILL.md` with matching YAML `name`, a discriminating `description`, and explicit input/procedure/output/completion sections.
- Ran the bundled `C:/Users/ekurm/.codex/skills/.system/skill-creator/scripts/quick_validate.py` against each folder with `.venv/Scripts/python.exe -X utf8`: **8 passed**. No unfinished scaffold placeholders remained. No optional UI metadata or external plugin dependencies were required.
- Checked relative Markdown links from root `AGENTS.md` and every skill entrypoint: all resolved. The shared contract specifies note-file path resolution and staged outputs.
- Ran `paper/research_notes/scripts/validate_research_artifacts.py --root .`: **passed**, with 12 evidence records and 4 bootstrap claims. This checks IDs, source hashes, classifications, numeric result provenance and the writing gate, not scientific truth.
- Exercised the validator in isolated temporary fixtures: valid real evidence passed; a stale source hash, a draft substituted for numeric result evidence, a missing evidence ID, and a prematurely opened writing gate were each rejected as expected. Exact outcomes are in `validation_checks.json`.
- Executed `audit_saved_archive.py` using only the standard library. All 9 manifest size/hash checks passed; 60,088 planned rows were streamed and Full Braw cached-score means recomputed. Source files, script hash, selectors, denominators and limitations are recorded in `analyses/archive_audit/summary.json`. No project model execution or full raw-response rescoring occurred.
- Final working-tree inspection showed additions in `.agents/`, `AGENTS.md`, and `paper/`, with no tracked source/config/result modifications. Pre-existing untracked drafts and the prior-paper PDF were preserved.

## Behavioral validation and limits

The initial two forward-test attempts stopped at the account usage limit. At the user's request, both bounded scenarios were subsequently completed by fresh independent agents using raw sources, without receiving prior audit conclusions. Initial output was isolated under `tmp/`; reviewed outputs are now retained in [validation/scenarios/](validation/scenarios/summary.json). **Both scoped scenarios passed**, including focused regression checks after the repairs below. This does not constitute a complete eight-skill manuscript-production run.

1. **Claim audit:** the agent audited the extraction and selection paragraphs, producing [22 atomic dispositions and 14 hashed evidence records](validation/scenarios/claims/audit.md). It identified the missing appendix, left historical Cypher extraction unverified, separated implemented design from historical coverage, and distinguished all-route witnesses from indispensable evidence. Its archive sample was explicitly bounded. Isolated ledger validation passed.
2. **Results planning:** the agent produced an [outline, figure dispositions and an exactly sourced numerical candidate](validation/scenarios/results/plan.md). It kept the writing gate closed, excluded mock performance, resolved the misleading Qwen-named folder using the Gemma manifest, and labelled its candidate as cached-score aggregation rather than raw-response rescoring. The primary agent independently recomputed the candidate and reran its portable derivation after relocation; both checks passed.

Two demonstrated instruction ambiguities were repaired: `academic-paper-writer` now defines the permission needed for an individual section, and `claim-verifier` explicitly supports bounded output destinations and `--notes` validation using a copy of the current workflow state. Each independent evaluator checked the revised instruction in the same scenario; see [claim regression](validation/scenarios/claims/regression.md) and [Results regression](validation/scenarios/results/regression.md). Both changed skills passed the bundled structural validator again; the production evidence ledger still passes.

The shared contract's earlier path-resolution clarification remains in place. The existing claim taxonomy is coarse for document-presence assertions; the audit explicitly distinguishes those from implementation/history rather than treating the label as proof. No taxonomy expansion was necessary for these scenarios.

The primary agent verified byte-level preservation of 93 original research/config/result/draft and production-note files against fingerprints taken for this test. The production writing gate and evidence/claim ledgers were not changed. Scripts made no model calls or research-module imports. The machine-readable [scenario summary](validation/scenarios/summary.json) records outcomes, skill/artifact hashes and check scope. Archived agent reports retain their original temporary commands as run history; the reproducible candidate can now be rerun with `python paper/research_notes/validation/scenarios/results/derive.py`, and isolated ledger validation with `python paper/research_notes/scripts/validate_research_artifacts.py --root . --notes paper/research_notes/validation/scenarios/claims/regression_validation`.

The system has structural validation and two completed independent behavioral scenarios. This does not certify every existing scientific claim, finish the literature review, or certify a manuscript for submission. The historical-scorer limitation and full-material analysis remain research work, not failed scenario checks.

## Research-analysis follow-up

After the scenario validation, the first research step was completed on the saved archive; see [reference_pairing_report.md](reference_pairing_report.md). Fresh archive and offline protocol verification passed, independent reference traversal and paired-input invariants had no mismatches, supplemental Native D/legacy checks passed, and ten isolated oracle/decoder correctness fixtures passed. The expanded production ledger passed structural validation with 26 evidence records and 8 claims. Original tracked research source/config/results/drafts showed no changes. These are scoped archive-analysis checks, separate from the earlier skill scenarios and from manuscript readiness.

The subsequent final-results step is also complete; see [final_results_report.md](final_results_report.md). The numeric package includes all condition/detail groups, paired bootstrap intervals and main-family bands, sensitivity diagnostics, analytical baselines, four visually inspected PNG/SVG figures and three LaTeX number fragments. Eight grouped numerical/software checks passed, including independent aggregate recomputation and interval reconstruction from saved draws. Structural validation passes for the current 39 evidence records and 15 claims. No claim of empirical confidence-coverage calibration, anchor independence, full-graph generalization or manuscript/PDF compilation is made.

## Template limitation (unchanged)

Official WWW requirements and official ACM template locations were verified. ACM returned a Cloudflare block; the CTAN download returned HTML rather than ZIP and was rejected/removed. No official bundle was cached and no manuscript/PDF was compiled. See `conference_requirements.md` and `paper/template/provenance.json`.

## Re-run commands

From the repository root, use an existing Python with PyYAML for the skill-creator validator:

```powershell
foreach ($skill in Get-ChildItem -LiteralPath '.agents/skills' -Directory) {
    & '.venv/Scripts/python.exe' -X utf8 'C:/Users/ekurm/.codex/skills/.system/skill-creator/scripts/quick_validate.py' $skill.FullName
    if ($LASTEXITCODE -ne 0) { throw "Skill validation failed: $($skill.Name)" }
}
& '.venv/Scripts/python.exe' -X utf8 paper/research_notes/scripts/validate_research_artifacts.py --root .
```

The bundled validator's absolute path is specific to this installation. Archive audit reproduction is `python paper/research_notes/scripts/audit_saved_archive.py --root .`; capture stdout to a new output file. If registered sources change, inspect the changes before refreshing ledger hashes.

## Contribution clarification, 2026-10-25

Inspected `article` at `3f4b7b9`, clean at entry. Scoped comparison and wording audit: `contribution_comparison.md`; primary PDF title/Introduction/related work, Sections 5.1–5.3, limitations/reproducibility and Appendix O, including Tables 32–33. No full manuscript or independent scientific review claimed. Existing result selectors were reused without new model runs or re-estimating archived scores.

Commands:

```text
/Users/ivan_kirpichev/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 paper/research_notes/scripts/validate_research_artifacts.py --root .
git diff --check
```

Initial validation detected 17 pre-existing byte-hash differences. Each was exactly explained by LF versus CRLF conversion, verified by hashing converted bytes; the files themselves were untouched. Old hashes were retained as `previous_crlf_sha256`, current hashes registered with a provenance note. Full per-file proof is in `validation/contribution_line_endings.json`. This is a checkout-byte reconciliation, not fresh scientific verification of historical reports.

Final structural result: passed, 41 evidence records, 18 claims, no errors. `git diff --check`: passed. Semantic conclusion: supported scoped contrasts are evidence availability and controlled rendering/placement; KG motifs, size and adjacent noise overlap prior Appendix O. Cross-paper resource/task/response independence remains pending and is excluded from the contribution. Broader literature completion, bibliography metadata and full manuscript coverage are not certified.

## Main-text structure and principal-claim selection, 2026-10-25

Created `paper_outline.md`, `outline_claim_map.json`, and bounded selection outputs under `analyses/main_text_selection/run-01/`. Existing manuscript drafts and numerical-analysis artifacts were preserved. The selection script reads existing CSVs and writes a design-table preview, Raw/Raw+E F1/exact/validity preview and machine-readable selectors/values/hashes. No bootstrap rerun, model call or new scientific experiment was performed.

Commands:

```text
/Users/ivan_kirpichev/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 paper/research_notes/analyses/main_text_selection/select_assets.py
/Users/ivan_kirpichev/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 paper/research_notes/scripts/validate_research_artifacts.py --root .
git diff --check
```

The first selection attempt stopped at a figure-hash check before writing deliverables. The stored SVG render hash was proven exactly equivalent to current bytes under LF-to-CRLF conversion; PNG matched directly. The completed selection records both current/archived SVG hashes and the conversion proof, without changing either source figure. Final selection check passed: 3 Raw model rows, 18 controlled contrast/model rows, 2 figure-file byte checks, unchanged declared 78-effect family.

Structural validator passed with 44 evidence records and 20 claims; `git diff --check` passed. Additional bounded map check passed: 13 outline entries resolve to known claims/evidence, local hashes match, pending independence is explicitly excluded, numeric source hashes match and section budgets sum to 8.0 pages. Result: `analyses/main_text_selection/run-01/validation.json`. Page budgets are editorial allocations, not a compiled compliance result.

Visually inspected the existing `controlled_contrasts.png` for asset selection and retained its complete six-row/three-model display; final printed legibility still needs manuscript layout QA. Figure 1 remains specified but not rendered. H1–H5 and main assets were reviewed against registered evidence; no independent review, full-text assertion coverage or final writing-gate approval is claimed.

## Scientific-emphasis reassessment, 2026-10-25

The author clarified team participation in Appendix O and asked to weigh structure/size versus evidence/presentation emphasis. Preserved the existing outline as an alternative. Added `emphasis_assessment.md`, `author_context_appendix_o.md` and bounded derived analysis under `analyses/emphasis_assessment/`.

Commands:

```text
/Users/ivan_kirpichev/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 paper/research_notes/analyses/emphasis_assessment/assess_scope.py
/Users/ivan_kirpichev/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 paper/research_notes/scripts/validate_research_artifacts.py --root .
git diff --check
```

Results: 499 detailed Core/Size/Full Braw groups independently aggregated from cached observation F1 agree with existing detailed CSV values (maximum absolute difference 1.3322676295501878e-15). Error categories preserve all planned outcomes and separate invalids; source hashes, selectors and base-ID intersections are recorded. This is not reparsing raw replies or fitting/testing motif or size effects. Initial exploratory inventory code encountered blank size fields in out-of-scope archive panels; the retained script explicitly selects Core/Size/Full Braw before numerical size conversion.

Structural validator passed: 50 evidence records, 24 claims, no errors. `git diff --check` passed. Corrected the earlier conversational overgeneralization that size evidence is Gemma-only: the restriction applies to the controlled additional-size series, while Full Braw/Raw+E has a complete all-model grid. Recommendation is structure-led and condition-aware; no new independent-replication, topology-causality, universal size-law or interaction significance claim is made. No new model calls, database export, complete manuscript or independent review.

## Consolidated research report, 2026-10-25

Created `RESEARCH_SUMMARY.md` as the single Russian-language synthesis of inspected implementation, archive coverage, reference/pair audits, final results, literature search status, detailed Appendix O comparison, author clarifications, the two competing emphases, the current structural recommendation and remaining work. Preserved existing detailed notes and the earlier presentation-first outline. No new empirical analysis or internet search was claimed in assembling this report.

Checked all 52 local Markdown links: no missing targets. All inline C-* identifiers resolve to existing claim records. The source manifest `validation/research_summary_sources.json` records 32 source-file hashes and the report hash; mutable workflow/evidence/validation logs are excluded from its frozen source hashes. This structural link/hash check does not re-verify source scientific truth or extend literature-search coverage.

Final command: `/Users/ivan_kirpichev/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 paper/research_notes/scripts/validate_research_artifacts.py --root .` — passed, 51 evidence records, 24 claims, no errors. `git diff --check` — passed. Full manuscript writing, layout, independent review and submission readiness remain unclaimed.

## Git checkpoint after manuscript drafting

2026-10-25. Before committing all work, inspected and reconciled four changed draft-source hashes. The report change was a single local editorial insertion (reversing that insertion reproduces its old hash); preserved the edited file. Other changes are the known final asset/script rounding/copy changes and bibliography note cleanup. Previous hashes and inspection reasons remain in the evidence register.

Structural validation passed: 60 evidence records, 27 claims, no errors. `git diff --check` passed. PDF build verification: 9 pages, no overfull boxes or undefined citation keys; final paragraph-level claim-map completion and independent scientific review remain pending. macOS `.DS_Store` metadata is excluded through `.gitignore`; research artifacts, source queries, PDF and analysis/QA materials are included in the checkpoint.

The staged whitespace check additionally reports renderer-generated SVG whitespace, unchanged vendored ACM class/style whitespace, raw compiler-log whitespace, and two intentional Markdown hard-break spaces in the report. These bytes are preserved rather than rewriting vendor/source-hashed generated artifacts just to silence a formatting diagnostic. No whitespace findings occur in the authored Python, TeX, Cypher or BibTeX content.

## Novelty refinement, 2026-10-25

Retained analysis: `analyses/novelty_refinement/run-02/`. Bundled Python ran `analyze_transitions.py --out paper/research_notes/analyses/novelty_refinement/run-02` and `register_audit.py`. Frozen witness/endpoint, cached-score, paired-fact and transition-conservation assertions passed. Scoped structural validation passed: 13 evidence records, 11 claims. `validate_research_artifacts.py --root .` failed with 39 earlier hash mismatches; all recorded hashes are reproduced by LF/CRLF conversion, with proof in `run-02/audit/integrity_check.json`. Historical hashes were preserved. New report local links passed; PDF hash remains the value recorded in build_report.md. No manuscript change, new inference, independent review or full scientific-readiness certification.

## Main findings and asset selection, 2026-10-25

`select_assets.py --out paper/research_notes/analyses/main_claim_assets/run-02` selected 24 existing F1 contrasts, 30 error-composition cells and six saved transition rows; uniqueness, denominators and conservation passed. No experiment, archive rescoring, statistical test or figure rendering. Eleven report links resolve. Scoped structural validation passed: 8 evidence records, 3 claims. Full `validate_research_artifacts.py --root .` retains the same 39 earlier line-ending hash errors, with no new asset-ledger errors. `git diff --check` passed. New figures, LaTeX tables, full manuscript verification and publication novelty remain unclaimed.

## Opening Tool Selection premise, 2026-10-26

Added the author-requested pattern-dependence premise to main_findings_and_assets.md; source Section 5.3/Table 1 p.8, claim C-tool-pattern-premise. Reviewed the known insertion and retained the previous draft hash in E-assets-plan revision history. No experimental, numeric asset or manuscript change. Full validator retains the same 39 prior line-ending mismatches, with no new premise/draft-record errors.

## Asset mapping for the structural objective, 2026-10-26

Active specification is thesis_asset_plan.md and analyses/main_claim_assets/run-03/asset_manifest.json. Existing motif/size renders retained in main text, paired effects and diagnostic transitions retained, detailed error composition moved to Appendix. Verified saved-file existence, source hashes and plan links. No new experimental/statistical computation or rendering. Full validator retains the same 39 old line-ending hash mismatches, with no new active-plan record errors.

## Precision/recall primary metric selection, 2026-10-26

select_precision_recall.py exported existing macro means for 42 motif cells and 192 variable-size cells, plus 48 descriptive PR contrasts. N/valid pairing and condition mean mapping were checked against the existing paired F1 export. No model calls, response rescoring, hypothesis tests or bootstrap; existing F1/exact intervals were deliberately excluded. Scoped structural validation passed; production retains the same 39 prior line-ending hash mismatches. New PR figures are not rendered yet; original PDFs remain unchanged.

## Precision/recall figure rendering, 2026-10-26

Four final plots in paper/figures/precision_recall_v3, each PNG/PDF/SVG, rendered using matplotlib 3.11.2 from saved selected CSVs. Source hashes, all expected row coverage, plotted deltas and output hashes checked. Final motif plot visually reviewed after spacing repair; three other final PNGs are byte-identical to the inspected renders. No uncertainty intervals drawn, no experiment or rescoring. Scoped structural validation passed. Production keeps the same 39 prior line-ending hash errors. Manuscript/research-code diff empty and manuscript PDF hash unchanged. Versions v1/v2 are preserved intermediate rendering attempts, not additional experiments.

## Metrics-only Table 2 including Gemma, 2026-10-26

Selected all twelve existing Core/six-node Tree-in K1/K3/K4/K7 metric cells, rendered PNG/PDF/SVG and visually checked. Metrics are saved macro P/R/exact; planned counts and invalid outcomes retained. Original Gemma source leads in SOURCES.json are absent at their workspace-relative paths; separate local pilots are not merged. This does not establish global absence of Gemma responses. Scoped structural validation passed; production retains the same 39 prior line-ending hash mismatches. Manuscript and research code remain unchanged.

## Compact recall Table 2, 2026-10-26

Losslessly pivoted the twelve saved recall values into three model rows and four condition columns; PNG/PDF/SVG visually reviewed. Recall is primary, Precision/Exact supplementary. N=100 and invalid contribution policy retained with valid-count exceptions in footnotes. Structural source-closure validation passed; no new scientific claims or calculations. Production retains the same 39 prior line-ending hash mismatches. Article and research code unchanged.

## Final recall manuscript release, 2026-10-26

Preserved previous manuscript, opened the recorded bounded writing gate and assembled the author-requested recall revision. Exact source rows and table values, bibliography/reference keys and hashes pass verify_revision.py. Final Tectonic 0.17.0 build succeeds: 10 pages (6 main, 1 references, 3 appendix), zero overfull boxes or undefined references/citations, eight embedded fonts, anonymous PDF metadata. All ten pages visually inspected. Native balance=false avoids appendix listings overflow without changing class/fonts/margins. New source ZIP contains only explicit TeX/figure dependencies. No experiment or new inference. Independent review and author originality/submission decisions remain pending.


## Error-figure removal, 2026-10-26

Ran `python paper/research_notes/scripts/validate_research_artifacts.py --root .`; output is preserved in `analyses/manuscript_revision/run-02/validation_full.txt`. The same 39 historical line-ending hash discrepancies remain. All seven new current-file records have matching SHA-256 values; prior records point to exact preserved bytes. Retained figure/table/bibliography hashes, active citation/reference keys and the four included figure paths pass the bounded editorial checks. See that run's `editorial_review.md`, `pdf_checks.json` and `release_manifest.json`.
