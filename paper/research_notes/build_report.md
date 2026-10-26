# Manuscript build report

## Complete standalone KG article, 2026-10-26

The agreed standalone Introduction/Related Work are active. Title, abstract, keywords, Discussion and Conclusion now use the KG entity-selection scope without the unpublished-source citation or cross-domain framing. Main Figure1 is the agreed grouped bar chart; full motif definitions are in Appendix C. Active input paths are canonical sections/ files.

A fresh main.pdf was exported with hash-verified Tectonic0.17.0 in untrusted mode. Default-sandbox bundle access failed; an approved escalated build could access the standard resources and succeeded. The cached final rebuild fixed one overfull paragraph heading without changing fonts, margins or class geometry. Logs: build-standalone-pass-3.txt and build-standalone-final.txt. The final PDF has11pages:6main,1references,4appendix. All14 detected fonts are embedded. Zero overfull boxes and undefined references/citations remain. Optional bibliography-field, font-resource and underfull notices are retained rather than resolved by invented metadata.

All11 pages were rendered with bundled Poppler and visually inspected. Numeric checks cover161 table/prose/diagnostic items and all42 main bars. Scoped structural validation passes:56evidence records,42claim records,75bindings. This is not an exhaustive novelty or submission-eligibility certification. Deliverables are main.pdf, article.md and article_sources.zip (43members, checked dependency closure/CRC, portable Markdown figures; no compiler/raw data). Prior sources/PDF are preserved under analyses/standalone_assembly/run-01/previous_manuscript/. Exact hashes, source/claim bindings, numeric/PDF checks and release manifest are under the same run. Historical production-ledger hash issues remain explicit.

## Grouped motif bars, 2026-10-26

The motif comparison is now one categorical grouped bar chart: three model pairs per motif, with Raw/Raw+E adjacent, model colors, hatched Raw and solid Raw+E. No connecting lines or stacked values are used. The 42 source values and their selectors/denominators are unchanged. The compact key remains alongside the chart and full definitions remain in the appendix. New PDF/SVG/PNG assets are under `paper/figures/motif_raw_recall_bars_v1/`; previous line assets are preserved.

The PNG was visually inspected and every bar height checked against its retained source row. The desktop compiler returned success for the existing main after the figure/caption replacement. This is not a new full-PDF export or complete page-layout certification. Scoped provenance and validation are in `analyses/motif_recall_layout/run-02/`.

## Compact motif key and Raw/Raw+E comparison, 2026-10-26

Detailed motif definitions now appear in `proposals/transfer_intro_related_v1/08_motif_appendix.tex`, included from the appendix. Method keeps a short definition and cross-reference. Results uses `figures/motifs_and_raw_recall_v1.pdf`: a small motif key beside three Raw/Raw+E recall panels, at the explicit Full size slice 6/4/5. The earlier controlled Core K1/K2 plot and its numerical discussion are preserved in the appendix. The new vector figure is 7.25 by 2.12 inches; its PNG was visually inspected. Existing typography and class options were not changed.

The desktop `compile_latex_document` call on the changed Results source resolved the existing `main.tex` and returned success. The following older PDF page counts refer to earlier exported builds: no new complete PDF export or full-page visual certification is claimed here. Source-row/denominator checks, paired subset verification, render provenance, and scoped cross-reference validation are in `analyses/motif_recall_layout/run-01/`. New main-figure values are Full Raw/Raw+E values, not substituted Core K1/K2 scores.

## Removal of the error-category figure, 2026-10-26

At the author's request, the former main Figure 3 and its detailed category-count discussion were removed. Unused category definitions and related abstract/discussion wording were condensed. The two main Recall figures and two tables are unchanged; appendix Precision figures are renumbered 3 and 4. No new experimental result or numerical estimate was added.

Tectonic 0.17.0 rebuilt `paper/manuscript/main.pdf` successfully using `--untrusted --only-cached --keep-logs --keep-intermediates main.tex`. Diagnostics: `paper/manuscript/build-without-error-figure.txt` and `main.log`. Zero overfull boxes and no unresolved references/citations. The PDF remains 10 pages (main 1-6, references 7, appendix 8-10); no typography or page geometry was changed. Visual QA is recorded separately in `analyses/manuscript_revision/run-02/pdf_checks.json`.

Previous PDF, active section sources, source archive and claim map are preserved under `analyses/manuscript_revision/run-02/`. Retained figure/table and bibliography hashes match the previous release. This editorial revision does not resolve the previously recorded independent-review/originality limitations.

## Earlier recall-led revision, 2026-10-26

Final `paper/manuscript/main.pdf`: **10 pages**; main text 1-6, references 7, appendix 8-10. Official Tectonic 0.17.0 compiled successfully in untrusted mode; final command ran from `paper/manuscript/`: `tectonic --untrusted --only-cached --keep-logs --keep-intermediates main.tex`. Log: `build-recall-pass-3.txt` / `main.log`. The initial standard TeX bundle was downloaded; later passes used cached resources. Compiler download URL/digest are recorded under `analyses/manuscript_revision/run-01/`.

Final diagnostics contain **zero overfull hboxes/vboxes and no unresolved references/citations**. Remaining messages concern underfull bibliography/listings boxes, absent optional bibliography fields, and fontconfig/requested-font notices; all eight PDF font resources are embedded and rendering was inspected. The native unmodified acmart `balance=false` option avoids listings overflow during automatic end-column balancing. No margins, class fonts or page geometry were changed to fit pages.

All ten pages and figure/table readability were checked using rendered PNGs in `analyses/manuscript_revision/run-01/qa_final/`. PDF metadata is anonymous; main-text boundary and existing WWW 2027 limits were checked. Built-in app compilation returned stale-project after inputs changed during its initial run; successful compilation reported here is the separate local Tectonic build.

Original sources and PDF are preserved under `analyses/manuscript_revision/run-01/previous_manuscript/`. Source-row equality, bibliography/ref keys, figure paths, scoped ledger and claim bindings pass the bounded checks in `verification.json`. General production validation retains 39 earlier line-ending hash issues. Compilation and scoped verification are separate from independent scientific review and originality/submission eligibility; see [recall_revision_review.md](recall_revision_review.md).

## Earlier descriptive draft build (historical)

2026-10-25. English source: `paper/manuscript/main.tex`; compiled PDF: `paper/manuscript/main.pdf`.

Engine: official Tectonic 0.17.0, installed temporarily; untrusted mode disables unsafe features. Command, run from `paper/manuscript/`: `tectonic --untrusted --keep-logs --keep-intermediates main.tex`. Final diagnostics: `paper/manuscript/build-final.txt`. The app-compiler preflight did not return diagnostics before interruption; the reported successful build is the separate local Tectonic build.

Result: success, 9 pages total. Main text/Conclusion ends on page 6; references page 7; appendix pages 8–9. No overfull boxes or undefined citation keys remain in the final log. Remaining class warnings arise from listings' internal spacing; bibliography warnings concern deliberately absent/unverified optional fields and undated anonymous/documentation sources. No margins, font sizes or class typography were changed to evade page limits; the line-breaking emergency stretch repairs overflow.

Both scientific figures and all nine rendered manuscript pages were inspected during the writing pass. QA images are under `analyses/manuscript_assets/run-01/qa_final/`; the source-to-claim map remains a scope map whose final paragraph-level completion is pending. Numerical source rows are preserved in the asset manifest; this build is not independent scientific review or submission-readiness certification.

The Cypher appendix now uses the author's supplied query. Whitespace/comments are normalized for display; executable-token equivalence was checked. Global LIMIT 100, fixed sizes and the absence of full sampling-grid provenance are stated. No Neo4j execution, model call, public upload or submission occurred.

PDF SHA-256: `2e73903a987ca927884a339d7a520d277c3763cc4524aab0f3ba2da2686338f8`.
