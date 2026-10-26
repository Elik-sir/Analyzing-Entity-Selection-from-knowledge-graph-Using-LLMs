# Author-provided decisions and provenance clarifications

Recorded 2026-10-25 from direct user statements in this chat. These are author confirmations, not independently reconstructed historical logs or new experimental measurements.

## Standalone KG exposition without the unpublished reference, 2026-10-26

The author now requests rewriting Introduction and Related Work without referring to the unpublished Tool Selection manuscript. This supersedes the earlier transfer-first exposition and mandatory inclusion instruction for the current two-section proposal. Present the supported KG selection analyses as a self-contained study; do not replace the removed reference with a first-study, independent-dataset or independent-replication claim. Earlier source comparisons, possible data reuse and historical provenance remain recorded, not erased or newly resolved.

Updated `.tex` and `.md` versions reside in `paper/manuscript/proposals/transfer_intro_related_v1/` (legacy folder name preserved). Scope/evidence checks and previous section text are in `analyses/intro_related_revision/run-04/`. The active full manuscript still needs separate title/abstract/discussion/conclusion alignment; no full-paper rewrite is implied by this two-section edit.

## Clarification of selection objective and central aim, 2026-10-26

The author clarified that questions were constructed to require selection of the complete entity set, and that the primary scientific objective is to examine transfer from Tool Selection to KG Entity Selection. Preserve transfer as the organizing research question; evidence/presentation and residual-error analyses investigate its conditions and limits rather than replace it as the paper's purpose.

Fresh inspection of an archived system instruction confirms exhaustive route coverage: named anchor, endpoints, intermediates and all parallel routes. Some endpoint-question texts distinguish the answer entities from the selected set. Accordingly, describe the query/selection protocol explicitly; do not turn this clarification into an independently verified claim that every selected card is indispensable evidence. An English two-section proposal, not an active manuscript replacement, is under `paper/manuscript/proposals/transfer_intro_related_v1/`; sources and scoped checks are under `analyses/intro_related_revision/run-01/`.

## Source graph

The user explicitly selected: “Тот же снимок без изменений” in response to whether the experiments used the graph snapshot described by Kirpichev et al. or a different export/subset.

Treat unchanged reuse as the intended factual description of this study. Cite the prior work for graph construction, source collection and schema rather than repeating that pipeline. Describe the current task sampling, public evidence variants and reference/scoring rules in this paper. Snapshot hashes/version identifiers, if available, belong naturally in artifact documentation or the appendix; a detailed graph-construction section is not required solely to repeat prior work.

This confirmation does not independently authenticate the graph bytes or establish how a separate KG panel in another paper was produced. Do not merge distinct papers' populations or numbers.

## Cypher appendix

User statement: “Cypher запросы я чуть позже добавлю в апендикс.”

Status: author-supplied appendix material expected. Continue independent research work. Check supplied queries against the method description before finalizing the appendix reference; do not claim the queries are already included. The current Python implementation alone does not settle the historical extraction mechanism.

## Required literature

Tool Graph Complexity is a mandatory citation. The supplied anonymous PDF is archived locally as `sources/tool_graph_complexity.pdf` with its source hash in `citation_requirements.json`. Read title page, Introduction and Appendix O; do not invent author identities, an acceptance decision, publication year, DOI or a public paper URL. The header states that the manuscript is under review at ICLR 2027.

The two supplied arXiv URLs and Talk like a Graph are closely related comparison works. Compare actual task and evaluation differences rather than treating broad similarity as equivalence. In particular, Tool Graph Complexity's Appendix O already studies KG entity selection, so tool-calling alone is not an adequate description of its relationship to this study.
