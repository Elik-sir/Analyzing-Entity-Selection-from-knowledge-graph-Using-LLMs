# Author-provided decisions and provenance clarifications

Recorded 2026-10-25 from direct user statements in this chat. These are author confirmations, not independently reconstructed historical logs or new experimental measurements.

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
