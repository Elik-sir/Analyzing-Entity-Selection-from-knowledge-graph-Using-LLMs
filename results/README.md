# Article data archive

This directory contains 60,088 planned observations for verification, reanalysis, and task freezing. See the [project README](../README.md) for commands and experimental definitions.

- `observations.jsonl.gz`: 60,088 outcomes including invalid replies. Keys include `observation_id`, `series_id`, `model`, `condition`, `noise`, `base_id`, `motif`, `size`, `question`, `valid`, `status`, `metrics`, `input_id`, and `response_id`.
- `inputs.jsonl.gz`: 41,193 deduplicated payloads with recorded `messages` or labelled `frozen_public`, `candidate_names`, and private scoring `reference`.
- `responses.jsonl.gz`: 52,197 deduplicated payloads with raw text and available parsed output, provider metadata, usage, and errors. Selection/answer/judge stages can have separate payloads.
- `task_specs_native.jsonl.gz`: 700 specifications; join `record_id` to observation `base_id`.
- `coverage.csv`: evidence availability by model and series.
- `panel_counts.csv`: planned counts by series/model/condition/noise.
- `SOURCES.json`: provenance paths and hashes; these need not exist locally.
- `MANIFEST.json`: file sizes/hashes and counts. Generator metadata identifies original collection code; the current importer is `graph_motives/collect_results.py`.
- `VALIDATION.json`: saved independent verification summary.

Join payloads by `input_id` and `response_id`. Resolve `source_refs[].source_id` through `SOURCES.json`. Missing IDs stay null. Legacy rows also have stage links and `historical_metrics`.

## Coverage

Core: 27,300; additional sizes: 2,200; calibration: 400; incremental: 700; native catalog: 6,288; Braw/Braw+E: 20,400; legacy: 2,800.

There are 12,400 Gemma observations with metrics-only response evidence and 15 Ministral Braw observations without replies after exhausted attempts. Primary responses exist for 47,673 observations. Every observation has a question/input. Incremental frozen inputs preserve initial context, not all historical turns. Declared settings are labelled separately from authenticated call metadata.

## Read and verify

```python
from graph_motives.archive import observations, with_payloads

row = next(observations(series="core", model="qwen3.6-flash", condition="K1"))
example = with_payloads(row)
```

```console
python scripts/verify_article_results.py
```

Primary means divide valid score sums by all planned observations in the selected panel. Invalid individual scores stay null and contribute zero to aggregates. Preserve pairing and group boundaries when comparing conditions and models.
