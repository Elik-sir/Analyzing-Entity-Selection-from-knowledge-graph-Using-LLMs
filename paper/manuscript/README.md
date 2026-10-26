# Entity Selection in Knowledge Graphs

The complete standalone English article is assembled in `main.tex`; the current exported article is `main.pdf`. `article.md` is a readable formatting conversion of the active source, including figures, numerical tables, references and appendices.

The active paper includes the agreed Introduction/Related Work, a single grouped recall bar chart with three model pairs per motif (Raw/Raw+E adjacent), a small motif key, and full motif definitions in Appendix C. All active content is under `sections/`; no proposal path is required to compile it.

Current verified export: 11 pages, comprising six main-text pages, one reference page and four appendix pages. All pages were rendered and inspected. Fourteen embedded fonts were detected; no overfull boxes or undefined citations/references remain. Optional bibliography-field and underfull warnings remain and do not add invented publication metadata. The ACM class and fonts/margins were not modified.

Build with Tectonic 0.17.0: `tectonic --untrusted --keep-logs --keep-intermediates main.tex`. A warmed installation may add `--only-cached`. Standard TeX resources must be available in the compiler bundle/cache. The source archive includes the local unmodified acmart 2.19 class, ACM bibliography style, active sources, figures and query specifications, but not a compiler binary or raw experimental data.

The study analyzes existing saved KG outcomes. No new model/judge/database experiment, raw-response reparse, causal mechanism or downstream QA gain is claimed. Numeric checks use saved per-task/aggregate scores with planned denominators and invalid/missing outcomes retained as zero. Assembly is not a submission or certification of publication originality. Historical data provenance and unresolved reuse/access limits remain in research notes.

Sources/PDF from before this assembly are preserved in `../research_notes/analyses/standalone_assembly/run-01/previous_manuscript/`. Current source/claim mappings, numeric checks, PDF checks and validation are under `../research_notes/analyses/standalone_assembly/run-01/`. Older research ledgers retain historical byte/hash issues; the current scoped validation records its own inspected sources and limits.
