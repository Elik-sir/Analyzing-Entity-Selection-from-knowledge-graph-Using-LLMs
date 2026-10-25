# Bounded diagnostic transfer assessment

`run-04/` is the retained final numeric output. It supersedes `run-02/` and `run-03/`; `run-01/` stopped on a missing historical specification before numeric outputs. Source files and frozen archives were preserved. The preceding runs represent exploratory development, not independent replications.

- `diagnose_transfer.py`: standard-library saved-observation aggregation, actual pair joins, explicit-public-graph witness checks and route-role diagnostic fields. Does not import research modules or call a provider/database.
- `run-04/summary.json`: exact selectors, planned counts, missing evidence, grouped cached metrics, pair transitions, error signatures, formulas, limitations, source hashes and command.
- `run-04/route_diagnostics.csv`: valid identity-level outcomes with observation/input IDs, path counts, role counts and output-set signatures. Missing identities or historical specifications are excluded and counted in the summary.
- `register_and_check.py`: verifies source hashes and agreement with previous numeric CSVs, registers only new IDs while preserving existing evidence hashes, and checks a separate new-assessment ledger.
- `run-04/assessment_audit/validation.json`: scoped structural and numeric success, and the separate production failure caused by older text hash differences. Scoped validation is not full-manuscript scientific review.
- `run-02/source_page_8.png`, `source_page_30.png`, `source_page_31.png`: read-only previews of the supplied literature PDF, inspected for the comparison; not project result figures.

The full methodology/positioning decision is in `../../transfer_positioning.md`, and the new outline in `../../transfer_outline.md`. The numeric pass is exploratory. No new statistical significance, internal-mechanism identification, Tool-row harmonization, QA gain or first-transfer result is claimed. Raw/overlay changes available facts; controlled placement retains unique facts but also changes repetition and context.

Reproduction from the repository root (choose an unused output directory):

```text
python paper/research_notes/analyses/transfer_positioning/diagnose_transfer.py --out paper/research_notes/analyses/transfer_positioning/run-reproduction
```

The source hash and output command will record the actual run. Standard-library Python is sufficient for numeric analysis. PDF inspection used the bundled pypdf/pypdfium2 packages separately.
