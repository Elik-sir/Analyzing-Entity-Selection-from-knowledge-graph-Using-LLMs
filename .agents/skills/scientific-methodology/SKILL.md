---
name: scientific-methodology
description: Turn implementation, experiment, and literature audits into precise task definitions, defensible research questions, contribution candidates, and a justified manuscript readiness decision.
---

# Scientific methodology

Read root `AGENTS.md` and [the artifact contract](../../../paper/research_notes/ARTIFACT_CONTRACT.md). This skill synthesizes available evidence; it does not create favorable results or authorize experiments.

## Inputs

`material_inventory.md`, `implementation_audit.md`, `experiment_audit.md`, `literature_review.md`, evidence/claim registers, existing drafts, and `conference_requirements.md`.

## Procedure

1. Define the unit of analysis, candidate set, sampled motif, endpoint answer, all-route witness set, minimal graph support, and visible-card sufficiency. Align each equation/pseudocode step with an implementation or mark it as a proposed formalization requiring verification.
2. Map each RQ to an implemented contrast, actual population, metric, available evidence tier, and competing explanation. Motif comparisons also change query semantics. Raw versus Raw+E changes information availability; templated text is controlled rendering. Aliases change lexical/tokenization properties.
3. Separate implemented method, observed result, methodological choice, interpretation, and hypothesis. Qualify externally valid scope: one graph family, frozen cohorts, model versions, missing responses, and incomplete histories.
4. Audit leakage, reference validity under distractors, selection versus QA targets, sampling/rejection bias, repeated anchors, uncertainty, multiple comparisons, and baseline comparability. Do not assume tests for current code validate historical artifacts.
5. Form contribution candidates only from literature-backed distinctions and verified evidence. If results cannot support a proposed claim, narrow it or remove it. List optional strengthening work separately from mandatory evidence repairs.
6. Propose additional work with required inputs, analysis unit, expected output, compute/API implications and approval status. Offline summaries of existing data may proceed within scope; source changes and new experiments need agreement.
7. Decide the writing gate explicitly: inventory and implementation/experiment/draft audits complete for the intended scope; literature supports the intended positioning; all blocking claims resolved by evidence, removal, narrowing, or explicit hypothesis framing. A missing artifact may be a documented limitation rather than an absolute blocker. Record the rationale; never mark a stage complete just to start writing.

## Outputs

Update `methodology.md` with definitions, RQ-to-evidence map, candidate contributions and scope; `gaps.md` with severity and resolution paths; `writing_plan.md` and `workflow_state.json` with readiness decision. Supply an evidence-backed outline to `$academic-paper-writer`.

## Completion check

Every contribution and RQ has a traceable evidential basis or a clearly labelled unresolved status. No unperformed analysis is described in past tense. A full manuscript remains gated until the recorded decision permits it.
