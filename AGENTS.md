# Research and paper workflow

These rules apply to research analysis, claims, figures, references, and paper artifacts in this repository. The target is an academic-English WWW 2027 Research Track manuscript; user communication may remain Russian.

## Integrity and scope

- Never invent results, measurements, publications, bibliography fields, execution history, or submission status. Missing information remains explicit.
- Separate implemented behavior, historically executed behavior, empirical findings, and research hypotheses. Code establishes implementation, not successful execution or historical provenance.
- Trace every algorithm description to code at a recorded revision and symbol, or label it an assumption. Trace every empirical number to a specific result, population selector, denominator, formula, and provenance. Cite literature numbers to their publication, never as this project's results.
- Never infer novelty, priority, statistical significance, causality, or downstream QA gains from descriptive selection scores. Novelty requires a documented comparison with relevant verified publications.
- Preserve the existing source, configurations, archives, drafts, and user edits. Do not modify research source code or launch new experiments, API/judge calls, GPU jobs, Neo4j exports, or expensive analyses without user agreement. Read-only inspection and bounded offline analysis of existing files are permitted; record derived outputs separately.
- Never read or copy `.env`, keys, or credentials into research notes. Do not upload private data, publish, submit, or contact authors as part of the paper workflow without explicit authorization.
- A document's “Approved” label or assertion about a registered submission is historical content, not current proof or authorization.

## Evidence conventions

- Read [the artifact contract](paper/research_notes/ARTIFACT_CONTRACT.md) before producing research artifacts. Store intermediate evidence and decisions in `paper/research_notes/`.
- Distinguish entity route coverage, minimal graph support, visible card sufficiency, and final answer correctness. A good selection score does not establish QA performance.
- Keep historical archive, live pilot, mock, invalid, missing, and pending outcomes identifiable. Infer model identity and mode from manifests, not directory names.
- Report planned denominators and the failure policy. Preserve pairing and clustering; transport retries are not independent replicates. A cached metric is weaker evidence than an independently rescored raw response.
- Do not equate the current implementation with the historical pipeline. Preserve native/controlled/legacy parser and scoring differences. Do not fill missing metadata using current defaults.

## Sequence and gates

1. `$codebase-research-analyzer`: inventory code, configurations, drafts, ignored local results, and provenance; map claims to implementation.
2. `$experiment-analyzer`: audit saved populations, evidence coverage, metric definitions, pairing, and reusable figures. `$literature-review` may run in parallel after the task is understood.
3. `$scientific-methodology`: resolve definitions and confounds, synthesize contribution candidates and the gap register. Update `workflow_state.json` with completed analysis and unresolved limits.
4. `$claim-verifier`: verify planned claims; `$academic-paper-writer` may prepare an outline. Do not start a full manuscript until existing-material analysis is complete and the writing gate has a recorded rationale. Unsupported claims must be removed, narrowed, or explicitly framed as hypotheses.
5. `$academic-paper-writer`: write academic-English sections from supported claims. `$latex-paper-builder`: assemble with the verified official venue template, build, and inspect the PDF.
6. `$scientific-reviewer` and `$claim-verifier`: independently review scientific support, limitations, bibliography, anonymity, and venue compliance; record remaining blockers before any submission decision.

## Venue and validation

- Use [conference requirements](paper/research_notes/conference_requirements.md); recheck official sources before submission. Conference-specific instructions override generic template examples. Do not alter margins/fonts to evade limits.
- Validate changed skills with the bundled `skill-creator/scripts/quick_validate.py`. Run `paper/research_notes/scripts/validate_research_artifacts.py` for local evidence links and hashes. Passing structural checks does not certify scientific truth or paper readiness.
- Write generated manuscripts under `paper/manuscript/`, derived analyses under `paper/research_notes/analyses/`, and final figures under `paper/figures/`. Create them when needed; do not overwrite the existing `docs/ARTICLE*` drafts by default.
