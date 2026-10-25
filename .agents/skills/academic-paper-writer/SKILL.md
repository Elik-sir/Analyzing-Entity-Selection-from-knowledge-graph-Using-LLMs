---
name: academic-paper-writer
description: Outline or write academic-English paper sections from verified research artifacts, preserving existing drafts and preventing unsupported method, result, or novelty claims.
---

# Academic paper writer

Read root `AGENTS.md` and [the artifact contract](../../../paper/research_notes/ARTIFACT_CONTRACT.md). Preserve the user's existing `docs/ARTICLE*` files unless edits are explicitly requested.

## Inputs

`workflow_state.json`, implementation/experiment/literature audits, `methodology.md`, `writing_plan.md`, supported claims, verified bibliography, figure provenance, and current venue requirements. Existing drafts provide wording candidates, not automatic factual authority.

## Procedure

1. Check the writing gate. If full writing is blocked, produce or improve only the outline, evidence map, and missing-data requests; do not generate a complete paper with imagined results. A "permitted section" below requires `analysis_complete=true`, `full_writing_ready=true`, and a recorded gate rationale covering that section's intended scope. A draft's "Approved" label alone grants no such permission. The initial system-installation task does not authorize drafting the full paper.
2. For a permitted section, choose its claim IDs and exact evidence first. Record a sidecar mapping from section/paragraph/table/figure to claims in `manuscript_claim_map.json`. Numerical cells, abstract numbers, captions, and appendix assertions also need mapping.
3. Write in precise academic English. Explain task, evidence and inference separately. Use past tense only for demonstrated performed work. Distinguish prior graph construction from this study, all-route selection from minimum sufficient evidence, and empirical patterns from hypotheses.
4. Use Raw and Raw+E for reader-facing labels while preserving Braw/Braw+E selectors in provenance. Never broaden descriptive patterns to causality, significance, model universality, novel methods, or QA gains without specific support.
5. Construct Introduction and Related Work from verified positioning; Method and Experimental Setup from implementation/history evidence; Results from reproducible summaries; Discussion from bounded interpretations. Draft abstract and conclusion after the supported body is stable.
6. Keep the venue's main text self-contained and explain Web relevance on the first page. Give limitations and data provenance space. Do not hide decisive caveats in an optional appendix.
7. Use only verified bibliography entries. Mark unresolved items in notes, not as convincing-looking invented citations or result text. Preserve author anonymity without erasing legitimate third-person citations.

## Outputs

Before the gate: `paper/research_notes/paper_outline.md` and updated `writing_plan.md`. After the gate: scoped section files under `paper/manuscript/sections/`, `manuscript_claim_map.json`, and change notes identifying unresolved claims. Hand assembly to `$latex-paper-builder` and factual review to `$claim-verifier`.

## Completion check

Every factual assertion has support at the appropriate strength. No placeholder is presented as a real result or bibliography entry. Writing quality does not override unresolved evidence.
