---
name: scientific-reviewer
description: Independently review a KG/LLM research manuscript or outline for scientific validity, contribution scope, reproducibility, evidence quality, and verified WWW submission requirements.
---

# Scientific reviewer

Read root `AGENTS.md` and [the artifact contract](../../../paper/research_notes/ARTIFACT_CONTRACT.md). Review the provided artifact at its actual stage; do not describe an outline as a completed paper review.

## Inputs

Manuscript or outline, claim map, evidence register, code/result audits, literature comparisons, gap register, venue requirements, and build report when a PDF exists.

## Procedure

1. Independently reconstruct the task, proposed contribution and scope from the supplied artifact. Read raw supporting sources for high-impact assertions; do not accept prior review labels as proof.
2. Evaluate novelty against the closest verified work, the actual Web relevance, target/reference correctness, public/private evidence boundary, pairing, confounds, baselines, uncertainty and generalization. Separate source-KG contributions from this study's contribution.
3. Inspect failure accounting, evidence tiers, mock/live/historical mixing, missing raw responses, incremental history, model provenance, native answerability and the selection-to-QA inference boundary.
4. Cross-check figure/table populations, paper terminology, limitations, citation relevance, and reproducibility instructions. An unavailable snapshot or missing historical query must be handled honestly; do not demand new experiments when narrowing a claim suffices.
5. Review anonymity, self-contained main text, verified page limits, bibliography and PDF quality at the applicable stage. Do not infer submission eligibility or registered-abstract status from a draft.
6. Write actionable findings with severity, manuscript locator/claim ID, evidence, consequence, and a minimal remedy. Distinguish factual errors, missing evidence, methodological risks, presentation issues and optional strengthening suggestions. Rank blockers before polish.
7. Recheck repaired findings against changed artifacts. Do not award acceptance probabilities or claim all facts verified based on a sample. Use `$claim-verifier` for sentence-level coverage.

## Outputs

`paper/research_notes/review_report.md` with reviewed artifact hash, scope, findings and unresolved blockers; update `gaps.md` and review status in `workflow_state.json`. Never rewrite primary data, source code, or approved draft sections as part of review without authorization.

## Completion check

Each finding is supported and actionable. Clearly state which checks were performed and which require additional evidence. Readiness is a reasoned decision, not a formatting pass.
