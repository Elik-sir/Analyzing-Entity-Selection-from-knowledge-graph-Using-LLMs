# KG-centered Related Work revision

October 26, 2026. Author request: present the study through knowledge graphs, entity selection, and LLM-based agents, then discuss structural tool selection in a separate later paragraph.

The new [readable section](../../../manuscript/sections/02_related_work_v4.md) and [LaTeX insertion](../../../manuscript/sections/02_related_work_v4.tex) use the heading **Related Work**. The [section bibliography](../../../manuscript/sections/related_work_v4.bib) retains the same 13 sources. The previous v3 files and the active older manuscript remain unchanged.

## Narrative and scientific scope

1. **Entity selection for knowledge-grounded LLMs:** introduce relational evidence, intermediate entities, entity retrieval, and connected graph context; position the present all-route selection target using RoG, GraphWalk, STaRK, and G-Retriever.
2. **Graph structure and task comprehension:** connect directed motifs and reference size to graph representation/task benchmarks. This is contextual positioning, not a claim that motif evaluation originates here.
3. **Availability and representation of relational evidence:** distinguish explicit relation disclosure from the presentation of designated matched facts.
4. **Selection errors, distractors, and evaluation targets:** contextualize incomplete exploration, neighbor noise, and passage distraction; keep route recovery distinct from QA and minimum sufficient evidence.
5. **Relationship to structural tool selection:** retain the direct Appendix O overlap and credit its KG findings while explaining the present study's KG-focused comparisons. Editorial autonomy does not establish data independence; unresolved cross-paper overlap is still disclosed.

Removed the earlier opening description of the manuscript as a diagnostic follow-up and the title's transfer-evidence emphasis. The tool-graph adjusted-regression detail is omitted to keep attention on the KG task; no contrary assertion replaces it. No new experiment, empirical number, algorithm, or novelty claim is introduced.

## Evidence and checks

The 26 sentences are mapped individually in `manuscript_claim_map.json` and `claims.jsonl`, using 17 scoped evidence records. Local source hashes were checked against the preceding inspected records before reuse; no stale hash was silently refreshed. The existing writing gate was read and remains unchanged.

Primary-source rereads for the new opening: original-author G-Retriever full text Sections 4-5, GraphWalk Abstract/Introduction, and the official RoG conference page. Other propositions reuse the same-day inspected relevant texts recorded in the v3 audit. The prior limits persist: Tian et al. supports only the abstract-level factor taxonomy, GraphOmni uses the explicitly inspected arXiv version, and the anonymous Tool Graph source has no newly asserted publication/review status. See the [previous verification notes](../related_work_revision_2026-10-26/revision_notes.md) for access attempts and screening of the supplied article list.

Commands use `/Users/ivan_kirpichev/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3` from the repository root:

- `paper/research_notes/analyses/related_work_kg_framing_2026-10-26/build_revision.py`: writes the new variant and scoped evidence records; static citation coverage and brace checks pass.
- `paper/research_notes/scripts/validate_research_artifacts.py --root . --notes paper/research_notes/analyses/related_work_kg_framing_2026-10-26`: scoped ledger validation; output in `scoped_validation.json`.
- `paper/research_notes/scripts/validate_research_artifacts.py --root .`: existing global ledger validation; output in `global_validation.json`.

These checks concern structure, local links/hashes, and citation keys. They do not certify scientific truth, independent review, or whole-paper readiness. No full PDF was compiled; this is a section replacement for the source project of the supplied PDF.
