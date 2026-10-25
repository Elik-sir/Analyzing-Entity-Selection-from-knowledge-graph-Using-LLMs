# English manuscript draft

Main file: `main.tex`. Bibliography: `references.bib`. The English body is under `sections/`; original `docs/ARTICLE*` files are preserved.

The paper uses the unmodified locally supplied acmart 2.19 class and ACM bibliography style from `paper/acmart/`. It is a descriptive, structure-led draft: motif profiles, family-specific size curves and evidence/noise controls. No new model experiment or motif/size significance test was performed. Main figures and tables are traceable to `paper/research_notes/analyses/manuscript_assets/run-01/asset_sources.json`.

The appendix reproduces the author's supplied extraction specification, saved in `queries/author_supplied_motif_extraction.cypher`; an English-comment version preserves executable tokens. Its global LIMIT and fixed sizes are explicitly distinguished from the full archived task grid. Other query files are exporter statements or separately labelled new unexecuted checks; they are not silently substituted for historical extraction. See `queries/README.md`.

The bibliography uses verified citation metadata. The mandatory anonymous Tool Graph manuscript has no invented authors, publication date, DOI or public URL. Exact cross-paper row overlap, final independent scientific review and submission readiness remain unresolved.

Build with an available TeX engine, for example `tectonic --untrusted --keep-logs main.tex`. The project is self-contained for its local class, style, sections, tables, figures and query listings; the engine still requires standard TeX packages/fonts. Compilation status, page boundary and visual QA are recorded in `paper/research_notes/build_report.md`.
