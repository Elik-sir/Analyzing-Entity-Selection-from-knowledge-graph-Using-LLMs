# Existing-result asset selection

The retained output is `run-02/`: 24 existing F1 contrasts, 30 cached error-composition cells and six saved same-task signature-transition rows. No new experiment, archive scoring, bootstrap or statistical test was run. Final figure rendering and LaTeX placement are still planned.

`run-01/` contains intermediate CSVs from a run that stopped on an incorrect claim identifier; it is superseded and is not a replicate. Existing sources are preserved. The executable selector, source hashes, output hashes and checks are recorded in `run-02/asset_manifest.json`.

The manuscript-facing conclusions, cautions, asset specifications and appendix choices are in [main_findings_and_assets.md](../../main_findings_and_assets.md).

Reproduce only the selection/formatting, using a fresh destination:

```text
python paper/research_notes/analyses/main_claim_assets/select_assets.py --out paper/research_notes/analyses/main_claim_assets/run-reproduction
```
