---
name: codebase-research-analyzer
description: Audit this research repository to map implemented KG entity-selection methods, historical execution evidence, and existing manuscript claims before scientific writing.
---

# Codebase research analyzer

Read root `AGENTS.md` and [the artifact contract](../../../paper/research_notes/ARTIFACT_CONTRACT.md). Paths below are repository-relative. This skill inspects implementation; it does not establish performance or novelty.

## Inputs

Repository revision and working-tree status; `graph_motives/`, `scripts/`, `configs/`, `tests/`, `pyproject.toml`, `uv.lock`; `docs/EXPERIMENT_PROTOCOL.md` and existing `docs/ARTICLE*`; result manifests. Inspect ignored `runs/` and `reproduced/` explicitly without reading secrets or traversing environments/caches.

## Procedure

1. Inventory available and absent materials, distinguishing tracked, untracked, ignored, external, and generated artifacts. Record a source revision and hashes for evidence actually used. Preserve user files.
2. Trace entrypoints through graph ingestion/sampling, task freezing, public versus private inputs, condition transformations, model calls, parsing, scoring, and reporting. Read source and relevant tests without importing modules that might execute work.
3. For each method claim record path, symbol, line span, revision/hash, assumptions, and evidence status. Tests describe checked invariants; they do not prove an archived run used this version.
4. Check repository-specific distinctions: Python motif sampling versus historical Cypher claims; all-route witness targets versus sampled motif nodes; induced candidate edges; graph references versus visible-card sufficiency; frozen replay versus current builders; strict controlled parsing versus legacy unknown-name scoring.
5. Compare draft assertions with implementation and archival provenance. Keep disagreements open rather than silently changing historical descriptions. Current defaults cannot establish historical seeds, model settings, graph counts, or provider identities.
6. Hand experiment questions to `$experiment-analyzer` and contribution questions to `$scientific-methodology`. Record missing materials as gaps with a way to resolve them.

## Outputs

- Update `paper/research_notes/material_inventory.md` and `implementation_audit.md` with pipeline and claim locators.
- Add implementation evidence and claim records to `evidence_register.json` and `claims.jsonl` using the contract.
- Update `gaps.md` and the implementation stage in `workflow_state.json` with inspected scope and remaining work.

## Completion check

The pipeline, public/private boundary, scoring families, and draft disagreements are traceable. Every unverified historical assertion is labelled. Do not run experiments, alter source, or begin a full paper to fill a gap.
