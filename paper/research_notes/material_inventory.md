# Initial material inventory

Inspected 2026-10-25, revision `261f1b3cc3d3bf3419c04d3d0a35d290fce73cae`. This is a first-pass inventory for the skill system, not a full manuscript audit.

## Available materials

- `graph_motives/`: graph export/sampling, public evidence preparation, frozen dataset replay, protocol-specific execution/scoring, historical import and report generation. `scripts/` exposes command entrypoints; `tests/` contains implementation checks.
- `configs/dataset.toml` and `configs/model.*.json`: current configuration templates. `pyproject.toml` and `uv.lock`: project dependencies. Configuration defaults do not prove historical settings.
- `results/`: compressed observations, inputs, responses and native task specifications; manifest, provenance index, coverage and panel counts. See `experiment_audit.md` and the reproducible archive summary for checks performed in this session.
- `docs/EXPERIMENT_PROTOCOL.md`: intended protocol and interpretation limits; compare with code and historical rows.
- `docs/ARTICLE.md`: English sections 3 and 4 marked approved; other sections largely absent. `ARTICLE_WORKING_DRAFT.md`: Russian discussion and candidate text. `ARTICLE_PLAN_WWW2027.md`: proposed RQs, structure, descriptive results and literature leads. `ARTICLE_REFERENCES.bib`: one existing source-KG entry; metadata is not automatically certified.
- `11_Towards_Ontology_Driven_Mul.pdf`: local prior-work PDF. Title/authors and graph-construction discussion inspected by text extraction (pages 1 and 3); this was not a complete publication/novelty review or layout QA. Do not transfer its graph counts to the current snapshot.
- Ignored `runs/` and `reproduced/`: live pilots and a mock workflow check. They require explicit inspection because ordinary `rg --files` omits them. They may be absent from a clean checkout.

## Local artifact cautions

- `runs/pipeline-check-10-per-motif-20261021/run.json`: mock mode. Its associated figures are not model performance evidence.
- `runs/gemma-4-31b-pilot-10-per-motif-20261021/`: live mode; result scope is a pilot, with protocol errors and unjudged legacy answers recorded separately.
- `runs/qwen3.6-flash-pilot-10-per-cell-20261021/run.json`: despite its directory name, model fields identify Gemma. No `execution.json` was found. Do not describe it as a completed Qwen run.
- Existing `reproduced/*/metrics.csv`, `conditions.csv`, `report.json`, diagnostics and PNG/PDF plots are figure candidates only after manifest/population verification. No manuscript figure has been selected or visually certified in this task.

## Missing or incomplete materials

No full source graph snapshot was found in a `data/` directory. Historical source paths in `results/SOURCES.json` may refer to a different source root; the archive README explicitly allows them to be absent. Historical extraction queries, snapshot identity, licenses, selected model/request metadata, some raw responses, and complete incremental histories remain gaps. See `gaps.md`.

## Preservation

At task start the four `docs/ARTICLE*` files and the root prior-work PDF were untracked user files. Keep them intact. No applicable existing `AGENTS.md` or project skills were found. This task adds research guidance and derived notes; it does not rewrite source code, execute models, alter saved results, or submit a paper.
