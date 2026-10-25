---
name: experiment-analyzer
description: Audit and reanalyze saved entity-selection experiments, scoring policies, paired comparisons, evidence coverage, and figure provenance without launching new model runs.
---

# Experiment analyzer

Read root `AGENTS.md` and [the artifact contract](../../../paper/research_notes/ARTIFACT_CONTRACT.md), including its path convention for research-note filenames. Use bounded offline analysis; new model/judge calls and expensive experiments require agreement.

## Inputs

`implementation_audit.md`; `results/MANIFEST.json`, `SOURCES.json`, `VALIDATION.json`, `coverage.csv`, `panel_counts.csv`, compressed observation/input/response/task-spec files; relevant `runs/*/run.json`, execution files and `reproduced/*/report.json`. Existing drafts and figures are leads, not primary evidence.

## Procedure

1. Verify available archive hashes and report precisely what was rerun. A saved `VALIDATION.json` is an earlier report, not a fresh independent rescore.
2. Resolve model identifier, alias, live/mock mode, completion, dataset fingerprint, source revision, and protocol from manifests. Never infer these from folder names. Keep local ignored pilots separate from the shared archive.
3. Join `input_id` and `response_id`; resolve source references through `SOURCES.json`. Count planned, valid, invalid, missing, pending, raw-response, cached-metric, and authenticated-request populations separately. Multiple response stages are not additional independent observations.
4. Confirm the actual scorer. Primary historical set-score means divide valid-score sums by all planned observations; invalid outcomes contribute zero. Distinguish macro set-F1 from pooled micro-F1, percentages from percentage points, and null QA judgments from wrong answers. Preserve null individual scores in archival copies.
5. Record each numeric result with exact selectors, N, valid count, metric definition, source hashes, script/command, scoring version, and evidence tier. Derived outputs belong in a new `paper/research_notes/analyses/<name>/` directory.
6. For comparisons verify paired keys, multiplicity, missing pairs, shared inputs and query semantics before differencing. `base_id` may repeat across models/series/conditions; specify the full key. Account for shared anchors when independence is uncertain. Bootstrap/test only after defining the unit, assumptions, seed, resampling and multiplicity policy; label exploratory analyses. Do not claim significance from descriptive means.
7. Verify plots against their source CSV/report selectors. Reject mock performance, mixed denominators, unlabelled partial runs, and fabricated error bars. Raw/Braw and Raw+E/Braw+E are display aliases, not separate conditions.
8. Record native-description answerability, incomplete incremental histories, historical provenance, and missing raw replies as limits. Propose new baselines or reruns with required inputs and cost scope, without executing them.

## Outputs

Update `experiment_audit.md`, result records in `evidence_register.json`, numeric claims in `claims.jsonl`, and `gaps.md`. For any fresh analysis retain its executable script, machine-readable summary and provenance in `analyses/`. Maintain a figure inventory with mock/live/historical scope and traceable source rows.

## Completion check

Every reported number can be reproduced or is explicitly marked as previously reported/cached. Coverage, denominator, pairing and uncertainty limitations accompany conclusions. Update the experiment stage in `workflow_state.json`; a passing archive hash check alone does not finish scientific validation.
