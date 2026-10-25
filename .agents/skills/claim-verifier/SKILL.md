---
name: claim-verifier
description: Trace manuscript and research-note claims to implementation, experimental rows, or verified publications, and flag unsupported numbers, algorithm descriptions, and overstatements.
---

# Claim verifier

Read root `AGENTS.md` and [the artifact contract](../../../paper/research_notes/ARTIFACT_CONTRACT.md). The evidence ledger supports verification; it cannot verify its own scientific meaning.

## Inputs

An explicit text/outline/manuscript scope, `claims.jsonl`, `evidence_register.json`, `manuscript_claim_map.json` when present, original code/results/publications, and source revision/hash records.

## Procedure

1. Extract atomic assertions from the actual text, including unregistered sentences, numbers in tables/captions/abstracts, comparative language, algorithm steps, and novelty/priority language. Do not restrict the audit to existing claim IDs.
2. Classify each assertion as implementation, historical execution, empirical result, literature statement, venue requirement, or hypothesis. Separate measured values from design parameters and literature-reported numbers; do not demand an experiment for a mathematical definition.
3. For methods inspect the exact code symbol and version; for historical assertions inspect archived inputs/logs/version evidence too. A current function is not proof it produced historical results. Assumptions must be explicit in the manuscript itself.
4. For empirical numbers resolve source hashes, row/JSON selectors, joins, metric, N, valid count, failure handling, rounding and transformation. Independently recompute bounded checks when possible. Cached metrics without raw responses may support labelled archived summaries, not claims of fresh independent rescoring.
5. For comparisons verify pairing, units, absolute versus relative change, scope, uncertainty and multiplicity. Check that “significant,” “causes,” “improves QA,” and “novel” have the additional evidence they require.
6. Verify citation identity and the actual cited proposition against primary text. For venue rules check the official source and retrieval date. Web titles/snippets alone do not verify substantive scientific content.
7. Run `python paper/research_notes/scripts/validate_research_artifacts.py --root .` with a suitable existing Python. For an explicitly scoped audit in an isolated output directory, use `--notes <audit-directory>` with scoped evidence/claim records and a copy of the current `workflow_state.json`; do not silently validate production records instead. It checks structure, links and hashes only. Inspect changed/stale evidence before updating hashes; never refresh hashes just to make a check pass.
8. Assign supported, pending, unsupported, or conflicted status with reason and remedy. State the audited scope and coverage. Hypotheses may remain pending if explicitly framed and excluded from established findings; unresolved factual claims must be removed, qualified or supplied with evidence.

## Outputs

Update claim/evidence records, `paper/research_notes/claim_audit.md`, `gaps.md`, and manuscript claim mapping. Include source locators, recomputation procedure and residual uncertainty. Hand methodological issues to `$scientific-methodology` and scoped wording repairs to `$academic-paper-writer`.

If the user or evaluation explicitly specifies a bounded audit or isolated destination, write the scoped report and records there instead of updating production ledgers. State which paragraphs and sources were covered; do not imply full-manuscript verification or open the production writing gate.

## Completion check

Every assertion within the declared scope has a disposition, including claims absent from the initial ledger. Report structural validator success separately from semantic verification and full manuscript coverage.
