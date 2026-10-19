"""Immutable run plans, bounded execution and durable per-call resume."""

import asyncio
import importlib.metadata
import json
import os
import sys
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from .common import atomic_json, canonical, digest, file_sha
from .dataset import freeze_tasks, tasks
from .models import LangChainBackend, MockBackend, validate_model
from .protocols import TOKEN_CAPS, parse, request_for, scores

ROOT = Path(__file__).resolve().parents[1]
VERSION = "article_model_run_v1"


def normalize_config(value):
    if not isinstance(value, dict) or set(value) - {"model", "judge", "execution", "generation"}:
        raise ValueError("Unknown run configuration fields")
    config = {"model": validate_model(value["model"])}
    if value.get("judge") is not None:
        config["judge"] = validate_model(value["judge"])
    config["execution"] = {"concurrency": 5, "max_attempts": 3, "timeout_s": 120, "max_turns": 26}
    execution = value.get("execution", {})
    if not isinstance(execution, dict) or set(execution) - set(config["execution"]):
        raise ValueError("Unknown execution settings")
    config["execution"].update(execution)
    for key, maximum in (("concurrency", 50), ("max_attempts", 10), ("max_turns", 26)):
        number = config["execution"][key]
        if type(number) is not int or not 1 <= number <= maximum:
            raise ValueError(f"{key} must be an integer between 1 and {maximum}")
    timeout = config["execution"]["timeout_s"]
    if type(timeout) not in (int, float) or not 0 < timeout <= 3600:
        raise ValueError("timeout_s must be between 0 and 3600")
    config["generation"] = {"temperature": 0, "max_tokens_by_series": {}}
    generation = value.get("generation", {})
    if not isinstance(generation, dict) or set(generation) - set(config["generation"]):
        raise ValueError("Unknown generation settings")
    config["generation"].update(generation)
    temperature = config["generation"]["temperature"]
    if type(temperature) not in (int, float) or temperature != 0:
        raise ValueError("Article protocol requires temperature=0")
    caps = config["generation"]["max_tokens_by_series"]
    if (
        not isinstance(caps, dict)
        or set(caps) - set(TOKEN_CAPS)
        or any(type(cap) is not int or cap < 1 for cap in caps.values())
    ):
        raise ValueError("Invalid max_tokens_by_series")
    canonical(config)
    return config


def code_hashes():
    paths = sorted((ROOT / "graph_motives").rglob("*.py"))
    if (ROOT / "uv.lock").exists():
        paths.append(ROOT / "uv.lock")
    return {path.relative_to(ROOT).as_posix(): file_sha(path) for path in sorted(paths)}


def versions():
    result = {"python": sys.version.split()[0]}
    for name in ("langchain-core", "langchain-openai", "openai", "pydantic"):
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    return result


def freeze(results, output, config, *, series, conditions=(), motifs=(), limit=None, mock=False):
    config = normalize_config(config)
    output = Path(output).resolve()
    if (output / "run.json").exists() or (output.exists() and any(output.iterdir())):
        raise ValueError("Choose a new empty run directory; use execute to resume a frozen run")
    output.mkdir(parents=True, exist_ok=True)
    selection = {
        "series": list(series),
        "conditions": list(conditions),
        "motifs": list(motifs),
        "limit": limit,
    }
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("limit must be positive")
    info = freeze_tasks(
        results, output / "tasks.sqlite", series=series, conditions=conditions, motifs=motifs, limit=limit
    )
    # Validate EVERY request locally before any model can be contacted.
    for task in tasks(output / "tasks.sqlite"):
        request_for(task, config)
    manifest = {
        "schema_version": VERSION,
        "config": config,
        "selection": selection,
        "mode": "mock" if mock else "live",
        "dataset": info,
        "code_sha256": code_hashes(),
        "environment": versions(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "metric_policy": "sum(valid task metrics) / planned N; invalid and pending contribute zero",
        "legacy_judge": "configured" if config.get("judge") else "not_evaluated",
    }
    manifest["run_id"] = digest(manifest)
    atomic_json(output / "run.json", manifest)
    return manifest


def verify_run(output):
    output = Path(output)
    manifest = json.loads((output / "run.json").read_text(encoding="utf-8"))
    if (
        manifest["schema_version"] != VERSION
        or digest({k: v for k, v in manifest.items() if k != "run_id"}) != manifest["run_id"]
    ):
        raise ValueError("Run manifest identity mismatch")
    if file_sha(output / "tasks.sqlite") != manifest["dataset"]["tasks_sha256"]:
        raise ValueError("Frozen tasks changed")
    if code_hashes() != manifest["code_sha256"]:
        raise ValueError("Execution code/lock changed; freeze a new run")
    if versions() != manifest["environment"]:
        raise ValueError("Execution environment changed; use the locked environment or freeze a new run")
    return manifest


class Gateway:
    def __init__(self, output, manifest, backend, judge_backend=None):
        self.output, self.manifest, self.backend, self.judge_backend = (
            Path(output),
            manifest,
            backend,
            judge_backend,
        )
        self.semaphore = asyncio.Semaphore(manifest["config"]["execution"]["concurrency"])

    async def call(self, task, request, *, judge=False):
        spec = self.manifest["config"]["judge" if judge else "model"]
        bound = {
            "run_id": self.manifest["run_id"],
            "task_id": task["task_id"],
            "model": spec,
            "request": request,
        }
        call_id = digest(bound)
        directory = self.output / "calls" / call_id[:2] / call_id
        directory.mkdir(parents=True, exist_ok=True)
        request_path = directory / "request.json"
        if request_path.exists():
            if json.loads(request_path.read_text(encoding="utf-8")) != bound:
                raise ValueError("Saved request identity mismatch")
        else:
            atomic_json(request_path, bound)
        response_path, state_path = directory / "response.json", directory / "state.json"
        if response_path.exists():
            response = json.loads(response_path.read_text(encoding="utf-8"))
            checksum = response.pop("response_sha256")
            if digest(response) != checksum:
                raise ValueError("Saved response checksum mismatch")
        else:
            state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
            # Interrupted dispatches may have been billed: never send them again automatically.
            if state.get("status") in {
                "dispatching",
                "unknown_outcome",
                "provider_error",
                "attempts_exhausted",
            }:
                return {
                    "call_id": call_id,
                    "status": "unknown_outcome" if state["status"] == "dispatching" else state["status"],
                    "parsed": None,
                    "http_status": state.get("http_status"),
                }
            max_attempts = self.manifest["config"]["execution"]["max_attempts"]
            response = None
            for attempt in range(state.get("attempt", 0) + 1, max_attempts + 1):
                async with self.semaphore:
                    atomic_json(state_path, {"status": "dispatching", "attempt": attempt})
                    try:
                        response = await (self.judge_backend if judge else self.backend).complete(request)
                    except Exception as error:
                        # Persist error type/status, never provider exception bodies (which may contain credentials).
                        code = getattr(error, "status_code", None)
                        retryable = code == 429
                        status = (
                            "rate_limited"
                            if retryable and attempt < max_attempts
                            else "attempts_exhausted"
                            if retryable
                            else "provider_error"
                            if code in {400, 401, 402, 403, 404, 422}
                            else "unknown_outcome"
                        )
                        atomic_json(
                            directory / f"error_{attempt}.json",
                            {"type": type(error).__name__, "http_status": code},
                        )
                        atomic_json(state_path, {"status": status, "attempt": attempt, "http_status": code})
                        if not retryable or attempt == max_attempts:
                            return {"call_id": call_id, "status": status, "parsed": None, "http_status": code}
                    else:
                        atomic_json(response_path, {**response, "response_sha256": digest(response)})
                        break
                await asyncio.sleep(min(2**attempt, 30))
            if response is None:
                return {"call_id": call_id, "status": "attempts_exhausted", "parsed": None}
        reason = response.get("metadata", {}).get("finish_reason")
        status, parsed = "completed", None
        if response.get("adapter_error"):
            status = "protocol_error"
        elif reason is not None and reason not in {"stop", "tool_calls", "end_turn"}:
            status = "provider_error"
        else:
            try:
                parsed = parse(response["text"], request)
            except (ValueError, TypeError, KeyError):
                status = "protocol_error"
        atomic_json(state_path, {"status": status})
        return {
            "call_id": call_id,
            "status": status,
            "parsed": parsed,
            "usage": response.get("usage"),
            "metadata": response.get("metadata"),
        }


async def run_task(task, gateway):
    config = gateway.manifest["config"]
    result = {
        k: deepcopy(task[k])
        for k in (
            "task_id",
            "series_id",
            "condition",
            "noise",
            "base_id",
            "motif",
            "size",
            "question",
            "source_model",
            "source_observation_id",
        )
    }
    result.update(
        model=config["model"]["alias"],
        provider_model=config["model"]["model"],
        run_id=gateway.manifest["run_id"],
        mode=gateway.manifest["mode"],
        calls=[],
        selected_names=[],
    )
    call = None
    if task["series_id"] == "incremental":
        selected, history = [], []
        cards = {card["name"]: card for card in task["input"]["frozen_public"]["candidates"]}
        status = "turn_limit"
        for turn in range(config["execution"]["max_turns"]):
            call = await gateway.call(task, request_for(task, config, history=history))
            result["calls"].append(call)
            if call["status"] != "completed":
                status = call["status"]
                break
            parsed = call["parsed"]
            if parsed["action"] == "done":
                status = "completed"
                history.append({"action": "done", "name": None, "observation": {}})
                break
            name = parsed["name"]
            if name in selected:
                status = "semantic_error_repeated_selection"
                break
            selected.append(name)
            history.append({"action": "select", "name": name, "observation": deepcopy(cards[name])})
        result.update(status=status, selected_names=selected, history=history)
    else:
        call = await gateway.call(task, request_for(task, config))
        result["calls"].append(call)
        result["status"] = call["status"]
        if call["status"] == "completed":
            parsed = call["parsed"]
            key = (
                "selected_tools"
                if task["series_id"] == "native_d"
                else ("result" if task["series_id"] == "calibration" else "selected_entities")
            )
            selected = parsed[key]
            result["selected_names"] = selected + parsed.get("unknown_entities", [])
            if task["series_id"] == "legacy":
                answer_call = await gateway.call(
                    task, request_for(task, config, stage="answer", selected=selected)
                )
                result["calls"].append(answer_call)
                result["predicted_answer"] = answer_call["parsed"]
                result["answer_status"] = answer_call["status"]
                result["answer_correct"] = None
                if config.get("judge") and answer_call["status"] == "completed":
                    judge_call = await gateway.call(
                        task,
                        request_for(
                            task, config, stage="judge", selected=selected, answer=answer_call["parsed"]
                        ),
                        judge=True,
                    )
                    result["calls"].append(judge_call)
                    result["judge_status"] = judge_call["status"]
                    result["judge_verdict"] = judge_call["parsed"]
                    if judge_call["status"] == "completed":
                        result["answer_correct"] = int(judge_call["parsed"]["correct"])
    result["valid"] = result["status"] == "completed"
    result["metrics"] = (
        scores(result["selected_names"], task["gold_names"], task.get("metric_normalization"))
        if (result["valid"])
        else dict.fromkeys(("precision", "recall", "f1", "exact", "fp", "fn"))
    )
    if task["series_id"] == "incremental":
        result["partial_metrics"] = scores(result["selected_names"], task["gold_names"])
    if task["series_id"] == "legacy":
        result["pipeline_correct"] = (
            int(bool(result["answer_correct"]) and result["metrics"]["exact"])
            if result.get("answer_correct") is not None and result["valid"]
            else None
        )
    result["result_sha256"] = digest(result)
    return result


async def execute(output, *, backend=None, judge_backend=None):
    output = Path(output).resolve()
    manifest = verify_run(output)
    lock = output / ".running.lock"
    # One writer per run, including two invocations started at the same instant.
    with lock.open("x", encoding="utf-8") as stream:
        stream.write(str(os.getpid()))
    owned_backends = []
    try:
        if backend is None:
            backend = (
                MockBackend() if manifest["mode"] == "mock" else LangChainBackend(manifest["config"]["model"])
            )
            owned_backends.append(backend)
        if manifest["config"].get("judge") and judge_backend is None:
            judge_backend = (
                MockBackend() if manifest["mode"] == "mock" else LangChainBackend(manifest["config"]["judge"])
            )
            owned_backends.append(judge_backend)
        gateway = Gateway(output, manifest, backend, judge_backend)
        result_dir = output / "tasks"
        result_dir.mkdir(exist_ok=True)
        source = iter(tasks(output / "tasks.sqlite"))
        statuses, complete, stop_reason = Counter(), 0, None

        async def worker():
            nonlocal complete, stop_reason
            while stop_reason is None:
                try:
                    task = next(source)
                except StopIteration:
                    return
                path = result_dir / (task["task_id"] + ".json")
                was_saved = path.exists()
                if was_saved:
                    row = json.loads(path.read_text(encoding="utf-8"))
                    if (
                        row.get("run_id") != manifest["run_id"]
                        or row.get("task_id") != task["task_id"]
                        or row.get("result_sha256")
                        != digest({k: v for k, v in row.items() if k != "result_sha256"})
                    ):
                        raise ValueError("Saved task result identity mismatch")
                else:
                    row = await run_task(task, gateway)
                    atomic_json(path, row)
                complete += 1
                statuses[row["status"]] += 1
                for call in [] if was_saved else row["calls"]:
                    if call.get("http_status") in {400, 401, 402, 403, 404, 422}:
                        stop_reason = {"task_id": task["task_id"], "http_status": call["http_status"]}
                if complete == 1 or complete % 50 == 0 or complete == manifest["dataset"]["tasks"]:
                    print(f"{complete}/{manifest['dataset']['tasks']} {dict(statuses)}", flush=True)

        workers = [
            asyncio.create_task(worker()) for _ in range(manifest["config"]["execution"]["concurrency"])
        ]
        try:
            await asyncio.gather(*workers)
        finally:
            await asyncio.gather(*workers, return_exceptions=True)
            source.close()
        result = {
            "run_id": manifest["run_id"],
            "mode": manifest["mode"],
            "tasks": complete,
            "statuses": dict(statuses),
            "stop_reason": stop_reason,
        }
        atomic_json(output / "execution.json", result)
        return result
    finally:
        try:
            for owned_backend in owned_backends:
                if hasattr(owned_backend, "aclose"):
                    await owned_backend.aclose()
        finally:
            lock.unlink()
