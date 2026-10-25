---
name: literature-review
description: Verify primary publications and compare KG, LLM, graph reasoning, entity selection, and QA research to establish defensible related work and novelty boundaries.
---

# Literature review

Read root `AGENTS.md` and [the artifact contract](../../../paper/research_notes/ARTIFACT_CONTRACT.md). Write manuscript-facing synthesis in academic English. This skill verifies literature; it does not invent citations or establish experimental performance.

## Inputs

Implementation/task definitions, proposed research questions, `docs/ARTICLE_REFERENCES.bib`, the local source-KG PDF, and literature leads in `docs/ARTICLE_PLAN_WWW2027.md`. Read `paper/research_notes/literature_review.md` for the current search state.

## Procedure

1. Search primary venues, publisher pages, ACL Anthology, OpenReview, and original preprints for task-matched work. Log date, query, inclusion/exclusion reasons, and source URLs. Search snippets and existing bibliography entries are discovery leads only.
2. Inspect the full relevant text when making a substantive comparison. Verify title, authors, year, venue and publication status independently. Keep preprint and proceedings versions distinct; use DOI only when confirmed. Mark access failures and abstract-only verification explicitly.
3. Compare the task/output, graph access, evidence representation, reference construction, noise, naming/order interventions, models, evaluation unit, metrics, and limitations. Separate direct baselines from conceptual context; graph QA or summarization is not automatically equivalent to fixed-pool entity route coverage.
4. For the source-KG paper distinguish reused graph construction and prior QA benchmark from the current selection study. Do not transfer published graph counts to the experimental snapshot without provenance. Refer to prior work in third person for anonymous review.
5. Test each contribution candidate against the closest verified papers. Prefer specific scoped differences over “first”, “novel”, or “state of the art”; mark unresolved overlap. Negative search results are not proof that no prior work exists.
6. Build BibTeX only from verified metadata. Preserve existing entries; write validated entries to `paper/research_notes/verified_references.bib` when available. Keep unresolved leads outside the manuscript bibliography. Do not fabricate DOI, pages, issue, or proceedings status to satisfy a format.

## Outputs

Update `literature_review.md` with search log, per-paper evidence locators, comparison dimensions, and novelty boundaries; add verified bibliography and source records to `evidence_register.json`. Give `$scientific-methodology` supported contribution distinctions and `gaps.md` unresolved literature questions.

## Completion check

Each cited proposition has an inspected source and locator. Bibliographic metadata and scientific content have separate verification statuses. A citation list alone is not a literature review and does not unlock novelty claims.
