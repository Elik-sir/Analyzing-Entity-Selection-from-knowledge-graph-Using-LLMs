# English manuscript draft

## Current recall-led revision, 2026-10-26

The former main Figure 3 (stacked error categories) was removed at the author's request. Its detailed count discussion and unused category definitions were removed. The adjacent-context result remains supported by the recall profiles and Table 1. Precision figures in the appendix are now Figures 3 and 4. Revision evidence and the previous PDF/source archive are preserved in `../research_notes/analyses/manuscript_revision/run-02/`.

The active `main.tex` compiles the eight `*_recall_*` section files. Recall is primary; precision is supplementary. Main results contain two figures and two tables, with one model per table row. The contribution is a diagnostic follow-up to Tool Graph Complexity and its Appendix O, separating relation availability, matched-fact presentation and remaining route-coverage failures. No new model experiment, harmonized Tool/KG estimate or causal mechanism is claimed.

The final checked PDF has 10 pages: main text 1-6, references 7, appendix 8-10. All pages were rendered and visually inspected. There are no overfull boxes or unresolved citations/references. Class fonts and geometry are unchanged; the native `balance=false` option avoids last-page listings balancing overflow. Remaining underfull/listings/bibliographic optional-field warnings are documented in the build report.

Tested compiler: official Tectonic 0.17.0. From this directory: `tectonic --untrusted --only-cached --keep-logs --keep-intermediates main.tex` after the standard bundle has been cached. Initial compilation may need network access for TeX resources. Figure PDFs and generated TeX tables are included in the source archive. No external shell execution is enabled.

Evidence, source hashes, row-level asset mappings, validation and page previews are under `../research_notes/analyses/manuscript_revision/run-01/`. The previous complete manuscript/PDF is preserved in that directory's `previous_manuscript/` folder. Original `docs/ARTICLE*` files remain untouched. A successful build is not submission or originality certification.

## Previous version notes (preserved)

Main file: `main.tex`. Bibliography: `references.bib`. The English body is under `sections/`; original `docs/ARTICLE*` files are preserved.

The paper uses the unmodified locally supplied acmart 2.19 class and ACM bibliography style from `paper/acmart/`. It is a descriptive, structure-led draft: motif profiles, family-specific size curves and evidence/noise controls. No new model experiment or motif/size significance test was performed. Main figures and tables are traceable to `paper/research_notes/analyses/manuscript_assets/run-01/asset_sources.json`.

The appendix reproduces the author's supplied extraction specification, saved in `queries/author_supplied_motif_extraction.cypher`; an English-comment version preserves executable tokens. Its global LIMIT and fixed sizes are explicitly distinguished from the full archived task grid. Other query files are exporter statements or separately labelled new unexecuted checks; they are not silently substituted for historical extraction. See `queries/README.md`.

The bibliography uses verified citation metadata. The mandatory anonymous Tool Graph manuscript has no invented authors, publication date, DOI or public URL. Exact cross-paper row overlap, final independent scientific review and submission readiness remain unresolved.

Build with an available TeX engine, for example `tectonic --untrusted --keep-logs main.tex`. The project is self-contained for its local class, style, sections, tables, figures and query listings; the engine still requires standard TeX packages/fonts. Compilation status, page boundary and visual QA are recorded in `paper/research_notes/build_report.md`.
