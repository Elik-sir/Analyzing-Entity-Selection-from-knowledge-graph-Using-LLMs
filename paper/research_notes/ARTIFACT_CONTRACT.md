# Research artifact contract

This is the shared contract for the eight project skills. It governs paper work, not unrelated repository tasks. Preserve original code, configurations, archives, figures and drafts. Derived artifacts live here; the manuscript and final figures have separate `paper/manuscript/` and `paper/figures/` destinations.

Path convention: repository paths such as `results/` or `docs/` are relative to the repository root. Bare research-note filenames in skill input/output lists (for example `implementation_audit.md` or `workflow_state.json`) resolve under `paper/research_notes/`, not the repository root. Markdown links remain relative to the containing file. Create stage outputs when the stage actually runs; a future output not existing yet is not a broken handoff.

## Entry points and state

- `material_inventory.md`: available materials, ignored local artifacts, absent sources, and preservation boundaries.
- `implementation_audit.md`: methods with code symbols, source revision, and historical/current distinctions.
- `experiment_audit.md`: populations, scoring, evidence coverage, pairing, figures and analysis limitations.
- `literature_review.md`: primary-source search log, verified comparisons, and unresolved leads. `verified_references.bib` is created only when entries have been verified.
- `methodology.md`: definitions, RQs, contribution candidates, confounds, and the scope decision.
- `conference_requirements.md`: verified venue rules and official template provenance.
- `gaps.md`, `writing_plan.md`, `workflow_state.json`: open work, ordering and gates.
- `evidence_register.json`, `claims.jsonl`: machine-readable provenance and claim dispositions.
- `claim_audit.md`, `review_report.md`, `build_report.md`: created or updated when those checks are actually performed. Do not populate fictional passes.
- `analyses/<name>/`: bounded offline analysis output, script/command and provenance. Never overwrite an existing result silently.

## Evidence records

`evidence_register.json` contains `schema_version: 1` and `evidence`, a list of records. Each record has:

- `id`: stable unique identifier, such as `E-archive-summary`.
- `kind`: `implementation`, `configuration`, `result`, `literature`, `venue`, or `draft`.
- `path` (repository-relative) or `url` (primary source). Local non-pending evidence has a SHA-256 in `sha256`.
- `locator`: exact symbol/line span, JSON path, row selector, observation ID, PDF section/page, or HTML section. A file name alone is insufficient.
- `verification`: `inspected`, `recomputed`, `reported`, or `pending`. “Reported” means the source says it was checked; no fresh verification is implied.
- `checked_on`: local calendar date of inspection. Optional `revision`, `command`, `limitations`, `upstream_evidence_ids` strengthen provenance.

Source hashes identify bytes, not truth. Preserve the revision and working-tree state because uncommitted files are not identified by a Git commit alone. Keep source IDs from the historical archive even when their original files are unavailable. A changed hash invalidates the old inspection until reviewed.

## Claim records

`claims.jsonl` has one JSON object per atomic claim:

- `id`, `text`, `type` (`implementation`, `historical`, `empirical`, `literature`, `venue`, `hypothesis`), `status` (`supported`, `pending`, `unsupported`, `conflicted`).
- `scope`: exact draft paragraph, planned manuscript claim, or audit-note scope; `evidence_ids`: existing evidence IDs; `reason`: support strength or unresolved issue.
- `numeric`: boolean. For empirical numeric claims, `numbers` contains records with `value`, `metric`, `evidence_id`, `locator`, `denominator`, `derivation`. Use a specific result record, not a paper draft. Include exact selectors/joins and rounding in derivation or the referenced analysis.

Hypotheses cannot have `supported` status: reclassify a tested conclusion with its actual evidence instead. Historical and empirical claims need result/log evidence; current implementation alone is insufficient. A supported implementation claim requires implementation evidence. Unsupported/pending/conflicted assertions may stay in the ledger but not appear as facts in the manuscript.

The claim register is not a replacement for reading the draft. `manuscript_claim_map.json`, when writing begins, maps section/paragraph, table cell or caption locators to claim IDs and source hashes. The verifier must also find assertions missing from the map. Record audited scope explicitly; bootstrap entries are not full-text coverage.

## Scientific distinctions

Keep sampled motif nodes M, endpoint answers A, all-route witnesses W, minimal graph support and indispensable visible cards distinct. Do not equate a graph reference with evidence actually available in raw descriptions. Preserve controlled, native, incremental and legacy scoring/reference differences.

For each analysis record the planned and valid populations, task/reference version, model/provider evidence, live/mock/historical mode, failure policy, metric definition, uncertainty method, paired key, and evidence tier. State whether metrics were rescored from raw replies or only aggregated from cached values. Retries and multiple response stages are not independent samples. Design counts and literature numbers need provenance but are not necessarily experimental performance claims.

Literature metadata verification and substantive content verification are separate. A verified title is not evidence for a scientific comparison. Candidate references remain in the search log until verified; never fill missing fields from memory.

## Writing gate

`workflow_state.json` records `analysis_complete`, `full_writing_ready`, `gate_rationale`, and per-stage status. Full writing requires completed analysis of the intended material/scope and a documented methodology/claim decision. Unavailable data can be handled by explicit limits and narrowed claims; do not require impossible completeness. A first-pass inventory does not certify a full audit.

Outlines, evidence mapping, template acquisition and skill validation may proceed while the gate is closed. This installation creates those foundations, not a full manuscript. Existing “Approved” draft labels are preserved but do not substitute for verification.

## Validation

Run `python paper/research_notes/scripts/validate_research_artifacts.py --root .`. It checks IDs, classifications, links, hashes, and minimal evidence requirements. It does not parse every possible locator, prove bibliographic truth, check statistics, or find claims absent from prose; those require the corresponding skill. Record exact commands, outcomes and scope in `validation_report.md`.
