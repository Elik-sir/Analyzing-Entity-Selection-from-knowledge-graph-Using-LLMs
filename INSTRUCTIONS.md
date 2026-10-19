# Running experiments and returning results

Run all commands from the repository root. Use Python 3.12 and `uv`, and include the supplied `results/` directory when downloading the project.

## 1. Prepare the environment and model

```console
uv sync --locked
uv run --locked python scripts/verify_article_results.py
```

Verification should report `status: passed` and 60,088 observations.

Copy `.env.example` to `.env` and enter your API key. Copy the appropriate model template to `configs/my-model.json`:

- `model.openrouter.json`: OpenRouter, using `OPENROUTER_API_KEY`.
- `model.openai.json`: direct OpenAI API, using `OPENAI_API_KEY`.
- `model.local.json`: OpenAI-compatible server; configure its URL and `LOCAL_LLM_API_KEY`.

Set `model.model` to the provider's model identifier and `model.alias` to the result label. The supplied OpenRouter template already specifies Qwen; change it when evaluating another model. The configuration also controls concurrency and request timeouts.

## 2. Run a pilot

The following command makes real API requests and may incur charges:

```console
uv run --locked python scripts/run_model.py run --config configs/my-model.json --series core --limit 30 --output runs/my-model-pilot --env-file .env
```

For an offline workflow check, add `--mock`; mock results must not be reported as model performance. Keep pilot, mock, and full experiments in separate directories.

## 3. Run the full experiment

```console
uv run --locked python scripts/run_model.py plan --config configs/my-model.json --series all --output runs/my-model
uv run --locked python scripts/run_model.py execute --run runs/my-model --env-file .env
```

`plan` freezes tasks and configuration offline. `execute` calls the model. All seven series contain 27,488 tasks/episodes per model; incremental and legacy tasks can require multiple calls. To run only Core and Braw/Braw+E, replace `--series all` with `--series core full_braw`.

Use a new directory for each model or changed configuration. To resume an interrupted experiment, repeat the same `execute` command. Keep the code and environment unchanged during the run.

For legacy answer evaluation, configure a fixed top-level `judge` model before planning. Without a judge, selection scores and answers are saved, but answer correctness remains unknown.

## 4. Check completion and build a report

Open `runs/my-model/execution.json`. Its `tasks` count should equal `dataset.tasks` in `runs/my-model/run.json`. Inspect `statuses` and `stop_reason`; a stopped or interrupted run may be incomplete. Retain failed tasks and their call records.

```console
uv run --locked python scripts/run_model.py report --run runs/my-model --historical results --output reproduced/my-model
```

The report contains CSV summaries, analyzed observations, provenance, and PNG/PDF figures. Use a new output directory when rebuilding a report. Reports can also be generated from incomplete runs, so state explicitly if a transferred experiment is partial.

## 5. Send the results for analysis

Send **the complete run directory**, preserving its structure:

```text
runs/my-model/
|-- run.json          Model, configuration, versions, and provenance
|-- tasks.sqlite      Frozen tasks and private scoring references
|-- execution.json    Execution summary
|-- tasks/            Every task outcome and individual scores
`-- calls/            All requests, responses, call states, and errors
```

Results are saved during execution. Keep all files in `tasks/` and `calls/`, including failed or invalid outcomes. The complete directory supports response inspection, score verification, and report regeneration; CSV summaries alone do not.

Create a ZIP archive using Python on Windows, macOS, or Linux:

```console
uv run --locked python -m zipfile -c my-model-results.zip runs/my-model
```

Create the archive after execution has stopped. Send `my-model-results.zip` together with:

- The exact source revision used, as an accessible commit link. If changes are unpublished, include the actual source code, `pyproject.toml`, and `uv.lock` used for the run.
- A short note identifying the model, selected series, and whether execution finished or is partial.
- Optionally, the complete `reproduced/my-model/` report directory.

For several models or configurations, send a separate run directory/archive for each. Exclude `.env`, API keys, and virtual environments from any source-code package. The supplied historical `results/` archive does not need to be sent again if the recipient already has the same project data.

The recipient can extract the run and rebuild its report:

```console
uv run --locked python -m zipfile -e my-model-results.zip runs
uv run --locked python scripts/run_model.py report --run runs/my-model --historical results --output reproduced/received-my-model
```

Extract into a location where `runs/my-model/` does not already exist.
