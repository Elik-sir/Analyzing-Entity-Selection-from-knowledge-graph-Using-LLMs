# Analyzing Entity Selection from Knowledge Graphs Using LLMs

Code and data for evaluating how graph structure and evidence representation affect entity selection by large language models. The repository includes 60,088 planned observations for Gemma, Qwen, and Ministral.

## Requirements

Download or clone the repository, including `results/`. Use **Python 3.12** and [uv](https://docs.astral.sh/uv/getting-started/installation/). Run the commands below from the repository root. The saved-data analysis runs on a CPU and requires no API key, GPU, or Neo4j database. Internet access is needed to install dependencies.

## Reproduce results from the saved data

```console
uv sync --locked
uv run --locked python scripts/verify_article_results.py
uv run --locked python scripts/run_model.py report --historical results --output reproduced/article
```

Verification should report `status: passed` and **60,088 observations**, including **45,904 independently recomputed individual scores**. The report is written to `reproduced/article/`:

- `metrics.csv`: precision, recall, F1, and exact match by model, condition, noise, motif, and size.
- `conditions.csv`: summaries by model, series, condition, and noise.
- PNG/PDF figures: recall, F1, and exact match for each experimental series.
- `observations.jsonl` and `report.json`: analyzed observations and report provenance.

The full export contains **608 detailed groups and 42 PNG/PDF files**. Use a new output directory when repeating the command.

For example, reproduce only Core and Braw/Braw+E:

```console
uv run --locked python scripts/run_model.py report --historical results --series core full_braw --output reproduced/core-and-braw
```

Primary means include all planned observations: invalid responses contribute zero. For the archived Qwen Core condition K1, expected values are `N=700`, `valid=699`, precision `0.992016`, recall `0.891714`, F1 `0.926479`, and exact match `0.702857`.

## Run a model again

See [INSTRUCTIONS.md](INSTRUCTIONS.md) for the experiment workflow and the files to return for analysis.

Copy `.env.example` to `.env` and enter the appropriate API key. Select a configuration in `configs/` and set its model identifier and result label. Templates are provided for OpenRouter, the direct OpenAI API, and OpenAI-compatible servers.

```console
uv run --locked python scripts/run_model.py plan --config configs/model.openrouter.json --series all --output runs/my-model
uv run --locked python scripts/run_model.py execute --run runs/my-model --env-file .env
uv run --locked python scripts/run_model.py report --run runs/my-model --historical results --output reproduced/my-model
```

`plan` prepares the tasks offline; `execute` makes real API requests and may incur charges. All seven series comprise **27,488 tasks/episodes per model**. For an initial pilot, replace `--series all` with `--series core --limit 30` and use a separate run directory. Repeat `execute` with the same directory to resume.

Results are saved during execution in `runs/my-model/`: `tasks/*.json` contains each task's outcome and scores, `calls/` contains requests, responses, and call states, and `execution.json` summarizes execution. `run.json` records the configuration and provenance; `tasks.sqlite` preserves the task inputs and scoring references. Keep the complete run directory for verification and resume.

The `report` command separately creates CSV summaries and figures in `reproduced/my-model/`. The included archive in `results/` is unchanged by new runs.

The available series are `core`, `full_braw`, `size`, `calibration`, `incremental`, `native_d`, and `legacy`. Legacy answer correctness requires an explicitly configured judge; without one, selection scores and answers are saved but answer correctness remains unknown.

## Files

- `results/`: observations, saved inputs/responses, references, and integrity manifests. See the [data description](results/README.md).
- `configs/`: model settings and graph sampling configuration.
- `graph_motives/`: experiment implementation, graph/task preparation, scoring, and reporting.
- `scripts/`: commands used above.
- `docs/EXPERIMENT_PROTOCOL.md`: [experimental definitions and interpretation limits](docs/EXPERIMENT_PROTOCOL.md).
- `pyproject.toml` and `uv.lock`: dependencies and their fixed versions.
- `tests/`: automated validation.

## Scope and limitations

The saved-data commands reproduce primary aggregates and generate comparison figures. They do not recreate every former presentation layout or establish reproduction of every statistical analysis in the article.

For **12,400 Gemma observations**, individual metrics and frozen inputs are available but complete primary responses are missing. Another **15 Ministral Braw observations** have no received response after exhausted attempts. These cases are explicitly marked and retained in the planned counts. Archived incremental inputs preserve initial contexts rather than complete turn histories.

New API runs can produce different responses even at temperature zero. Record the repository revision, configuration, and run manifest when reporting a new experiment. The code is distributed under the [MIT license](LICENSE).
