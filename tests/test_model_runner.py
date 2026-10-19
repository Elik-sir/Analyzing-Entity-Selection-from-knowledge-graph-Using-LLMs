"""Scientific protocol, resume and real LangChain transport checks without paid API calls."""

import asyncio
import json
import sqlite3
import threading
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from graph_motives.common import atomic_json, canonical, digest, file_sha
from graph_motives.models import LangChainBackend, MockBackend
from graph_motives.protocols import parse, request_for, scores
from graph_motives.report import aggregates, report
from graph_motives.runner import Gateway, code_hashes, execute, normalize_config, run_task, versions


def config():
    return normalize_config(
        {
            "model": {
                "alias": "test",
                "provider": "openai-compatible",
                "model": "served-model",
                "base_url": "http://localhost:8000/v1",
                "api_key_env": "TEST_MODEL_KEY",
            }
        }
    )


def task(series="core"):
    public = {
        "question": "Which supplied entities connect A and B?",
        "candidates": [
            {"name": "A", "type": "Company", "facts": {"description": "public-A"}},
            {"name": "B", "type": "Company", "facts": {"description": "public-B"}},
        ],
    }
    return {
        "task_id": digest([series, "K1", "disconnected", "base"]),
        "series_id": series,
        "condition": "K1",
        "noise": "disconnected",
        "base_id": "base",
        "motif": "chain",
        "size": 2,
        "question": public["question"],
        "source_model": "old-model",
        "source_observation_id": "old",
        "gold_names": ["A", "B"],
        "frozen_input_metadata": {"readiness": "validated_controlled"},
        "metric_normalization": None,
        "input": {
            "candidate_names": ["A", "B"],
            "messages": None,
            "frozen_public": public,
            "reference": {"expected_names": ["A", "B"], "sentinel": "PRIVATE_GOLD_SENTINEL"},
        },
    }


class SequenceBackend:
    def __init__(self, values):
        self.values, self.requests = iter(values), []

    async def complete(self, request):
        self.requests.append(deepcopy(request))
        value = next(self.values)
        if isinstance(value, Exception):
            raise value
        return {
            "text": canonical(value),
            "usage": None,
            "metadata": {"finish_reason": "stop"},
            "message": None,
            "elapsed_s": 0,
        }


def gateway(tmp_path, backend, cfg=None):
    return Gateway(tmp_path, {"config": cfg or config(), "run_id": "run", "mode": "mock"}, backend)


def test_reuses_recorded_messages_verbatim_and_hides_private_reference():
    value = task()
    value["input"]["messages"] = [
        {"role": "system", "content": "exact\n system"},
        {"role": "user", "content": "exact  user é"},
    ]
    request = request_for(value, config())
    assert request["messages"] == value["input"]["messages"]
    assert "PRIVATE_GOLD_SENTINEL" not in canonical(request)
    assert request["settings"]["max_tokens"] == 1024


def test_frozen_prompt_matches_original_builder():
    from graph_motives.preparation.prompts import build_selection_prompt

    value = task()
    prompt = build_selection_prompt(value["input"]["frozen_public"])
    request = request_for(value, config())
    assert request["messages"][0]["content"] == prompt["system_prompt"]
    assert request["messages"][1]["content"] == prompt["user_prompt"]


@pytest.mark.parametrize(
    "text",
    [
        '{"selected_entities":["C"],"insufficient_evidence":false}',
        '{"selected_entities":["A","A"],"insufficient_evidence":false}',
        '{"selected_entities":[],"insufficient_evidence":false,"extra":1}',
        '{"selected_entities":[],"selected_entities":[],"insufficient_evidence":false}',
        '```json\n{"selected_entities":[],"insufficient_evidence":false}\n```',
    ],
)
def test_strict_parser_rejects_protocol_changes(text):
    with pytest.raises(ValueError):
        parse(text, request_for(task(), config()))


def test_failures_and_pending_stay_in_planned_denominator():
    rows = [
        {
            "model": "new",
            "series_id": "core",
            "valid": True,
            "status": "completed",
            "metrics": {"precision": 1, "recall": 1, "f1": 1, "exact": True},
        },
        {"model": "new", "series_id": "core", "valid": False, "status": "protocol_error", "metrics": {}},
        {"model": "new", "series_id": "core", "valid": False, "status": "pending", "metrics": {}},
    ]
    row = aggregates(rows, ("series_id",))[0]
    assert row["N"] == 3 and row["valid"] == 1 and row["pending"] == 1
    assert row["f1"] == pytest.approx(1 / 3)
    assert scores(["A", "invented"], ["A"])["precision"] == 0.5


def test_incremental_reveals_only_chosen_card_and_stops_on_repeat(tmp_path):
    backend = SequenceBackend(
        [
            {"action": "select", "name": "A", "insufficient_evidence": False},
            {"action": "select", "name": "A", "insufficient_evidence": False},
        ]
    )
    value = task("incremental")
    row = asyncio.run(run_task(value, gateway(tmp_path, backend)))
    assert row["status"] == "semantic_error_repeated_selection" and not row["valid"]
    assert row["metrics"]["f1"] is None
    first = json.loads(backend.requests[0]["messages"][1]["content"])
    second = json.loads(backend.requests[1]["messages"][1]["content"])
    assert all(card["facts"] == {} for card in first["candidates"])
    assert second["candidates"][0]["facts"] == {"description": "public-A"}
    assert second["candidates"][1]["facts"] == {}
    assert second["history"][0]["observation"]["name"] == "A"
    assert "PRIVATE_GOLD_SENTINEL" not in canonical(backend.requests)


def test_saved_response_reused_without_second_dispatch(tmp_path):
    backend = SequenceBackend([{"selected_entities": ["A"], "insufficient_evidence": False}])
    channel = gateway(tmp_path, backend)
    value, request = task(), request_for(task(), config())
    first = asyncio.run(channel.call(value, request))
    second = asyncio.run(channel.call(value, request))
    assert first == second and len(backend.requests) == 1


def test_unknown_outcome_is_not_resent(tmp_path):
    backend = SequenceBackend([TimeoutError("Secret provider exception body")])
    channel = gateway(tmp_path, backend)
    value, request = task(), request_for(task(), config())
    assert asyncio.run(channel.call(value, request))["status"] == "unknown_outcome"
    assert asyncio.run(channel.call(value, request))["status"] == "unknown_outcome"
    assert len(backend.requests) == 1
    assert all("Secret provider exception body" not in path.read_text() for path in tmp_path.rglob("*.json"))


@pytest.mark.parametrize("exhausted", [False, True])
def test_only_rejected_rate_limits_are_retried(tmp_path, monkeypatch, exhausted):
    class Rejected(Exception):
        status_code = 429

    async def no_delay(_):
        pass

    monkeypatch.setattr("graph_motives.runner.asyncio.sleep", no_delay)
    values = (
        [Rejected(), Rejected(), Rejected()]
        if exhausted
        else [Rejected(), {"selected_entities": ["A"], "insufficient_evidence": False}]
    )
    backend = SequenceBackend(values)
    channel = gateway(tmp_path, backend)
    value, request = task(), request_for(task(), config())
    result = asyncio.run(channel.call(value, request))
    assert result["status"] == ("attempts_exhausted" if exhausted else "completed")
    expected = 3 if exhausted else 2
    assert len(backend.requests) == expected
    asyncio.run(channel.call(value, request))
    assert len(backend.requests) == expected


def test_configuration_error_stops_queue_and_resume_keeps_old_failure(tmp_path):
    class Unauthorized(Exception):
        status_code = 401

    path = tmp_path / "tasks.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE tasks (number INTEGER PRIMARY KEY, task_id TEXT, data TEXT)")
        for number in range(15):
            value = task()
            value.update(base_id=str(number), task_id=digest(["task", number]))
            connection.execute(
                "INSERT INTO tasks VALUES (?, ?, ?)", (number, value["task_id"], canonical(value))
            )
    connection.close()
    manifest = {
        "schema_version": "article_model_run_v1",
        "config": config(),
        "mode": "mock",
        "dataset": {"tasks": 15, "tasks_sha256": file_sha(path)},
        "code_sha256": code_hashes(),
        "environment": versions(),
    }
    manifest["run_id"] = digest(manifest)
    atomic_json(tmp_path / "run.json", manifest)
    backend = SequenceBackend([Unauthorized()] * 5)
    first = asyncio.run(execute(tmp_path, backend=backend))
    assert first["stop_reason"]["http_status"] == 401
    assert 1 <= len(backend.requests) <= 5
    assert first["tasks"] < 15
    fixed = SequenceBackend([{"selected_entities": ["A"], "insufficient_evidence": False}] * 15)
    second = asyncio.run(execute(tmp_path, backend=fixed))
    assert second["tasks"] == 15 and second["stop_reason"] is None
    assert len(fixed.requests) == 15 - len(backend.requests)


def test_interrupted_after_response_save_resumes_parsing(tmp_path):
    backend = SequenceBackend([{"selected_entities": ["A"], "insufficient_evidence": False}])
    channel = gateway(tmp_path, backend)
    value, request = task(), request_for(task(), config())
    first = asyncio.run(channel.call(value, request))
    for path in tmp_path.rglob("state.json"):
        atomic_json(path, {"status": "dispatching", "attempt": 1})
    assert asyncio.run(channel.call(value, request)) == first
    assert len(backend.requests) == 1


def test_legacy_answer_uses_new_selection_and_judge_is_separate(tmp_path):
    cfg = config()
    cfg["judge"] = {**cfg["model"], "alias": "fixed-judge"}
    value = task("legacy")
    public = {
        "question": "What?",
        "candidates": [
            {"name": name, "type": "Company", "facts": {"description": name}} for name in ("A", "B")
        ],
    }
    value["input"]["messages"] = [
        {"role": "system", "content": "select"},
        {"role": "user", "content": json.dumps(public)},
    ]
    value["input"]["reference"] = {"answer": {"entities": ["A"], "relations": []}}
    backend = SequenceBackend(
        [
            {"selected_entities": ["A"], "insufficient_evidence": False},
            {"answer": "A", "insufficient_evidence": False},
        ]
    )
    judge = SequenceBackend([{"correct": True, "metadata_sufficient": True, "reason": "Matches"}])
    channel = gateway(tmp_path, backend, cfg)
    channel.judge_backend = judge
    row = asyncio.run(run_task(value, channel))
    assert row["answer_correct"] == 1
    shown = json.loads(backend.requests[1]["messages"][1]["content"])
    assert [card["name"] for card in shown["candidates"]] == ["A"]
    assert len(judge.requests) == 1
    assert "reference" not in canonical(backend.requests)


@pytest.mark.parametrize("provider", ["openai-compatible", "openrouter", "openai"])
def test_real_langchain_adapter_against_local_http_server(provider, monkeypatch):
    received = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            received.append(payload)
            content = canonical({"selected_entities": ["A"], "insufficient_evidence": False})
            body = {
                "id": "local-response",
                "object": "chat.completion",
                "created": 1,
                "model": "served-model",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": content},
                    }
                ],
                "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
            }
            if payload.get("tools"):
                body["choices"][0]["finish_reason"] = "tool_calls"
                body["choices"][0]["message"] = {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "tool1",
                            "type": "function",
                            "function": {"name": "final_result", "arguments": '{"selected_tools":["A"]}'},
                        }
                    ],
                }
                if payload["messages"][-1]["content"] == "malformed":
                    body["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] = (
                        '{"selected_tools":[],"selected_tools":["A"]}'
                    )
            if payload["messages"][-1]["content"] == "sdk-invalid":
                body = {"invalid": "received but not a chat completion"}
            encoded = canonical(body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("TEST_MODEL_KEY", "offline-placeholder")
    try:
        spec = config()["model"]
        spec.update(provider=provider, base_url=f"http://127.0.0.1:{server.server_port}/v1")
        if provider == "openrouter":
            spec["parameters"] = {
                "extra_body": {
                    "reasoning": {"enabled": False},
                    "provider": {"allow_fallbacks": False, "require_parameters": True},
                }
            }
        backend = LangChainBackend(spec)
        request = request_for(task(), config())
        response = asyncio.run(backend.complete(request))
        assert parse(response["text"], request)["selected_entities"] == ["A"]
        assert response["usage"]["input_tokens"] == 11
        assert received[0]["messages"] == request["messages"]
        assert received[0]["model"] == "served-model"
        token_field = "max_completion_tokens" if provider == "openai" else "max_tokens"
        assert received[0]["temperature"] == 0 and received[0][token_field] == 1024
        assert received[0]["response_format"] == {"type": "json_object"}
        assert response["wire_request"] == received[0]
        assert response["wire_response"]["id"] == "local-response"
        value = task("native_d")
        value["input"]["messages"] = request["messages"]
        tools_request = request_for(value, config())
        tools_response = asyncio.run(backend.complete(tools_request))
        assert parse(tools_response["text"], tools_request)["selected_tools"] == ["A"]
        assert received[1]["tool_choice"]["function"]["name"] == "final_result"
        tools_request["messages"][-1]["content"] = "malformed"
        malformed = asyncio.run(backend.complete(tools_request))
        assert malformed["text"] == '{"selected_tools":[],"selected_tools":["A"]}'
        with pytest.raises(ValueError):
            parse(malformed["text"], tools_request)
        request["messages"][-1]["content"] = "sdk-invalid"
        invalid = asyncio.run(backend.complete(request))
        assert invalid["adapter_error"]
        assert invalid["wire_response"] == {"invalid": "received but not a chat completion"}
        assert len(received) == 4
        asyncio.run(backend.aclose())
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_config_change_cannot_resume_existing_run(tmp_path):
    value = task()
    path = tmp_path / "tasks.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE tasks (number INTEGER PRIMARY KEY, task_id TEXT, data TEXT)")
        connection.execute("INSERT INTO tasks VALUES (0, ?, ?)", (value["task_id"], canonical(value)))
    connection.close()
    manifest = {
        "schema_version": "article_model_run_v1",
        "config": config(),
        "mode": "mock",
        "dataset": {"tasks": 1, "tasks_sha256": file_sha(path)},
        "code_sha256": code_hashes(),
        "environment": versions(),
    }
    manifest["run_id"] = digest(manifest)
    atomic_json(tmp_path / "run.json", manifest)
    asyncio.run(execute(tmp_path, backend=MockBackend()))
    manifest["config"]["model"]["model"] = "different-model"
    atomic_json(tmp_path / "run.json", manifest)
    with pytest.raises(ValueError, match="manifest identity"):
        asyncio.run(execute(tmp_path, backend=MockBackend()))


def test_report_keeps_missing_task_as_pending(tmp_path):
    value = task()
    directory = tmp_path / "run"
    directory.mkdir()
    path = directory / "tasks.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE tasks (number INTEGER PRIMARY KEY, task_id TEXT, data TEXT)")
        connection.execute("INSERT INTO tasks VALUES (0, ?, ?)", (value["task_id"], canonical(value)))
    connection.close()
    manifest = {"config": config(), "mode": "mock", "dataset": {"tasks_sha256": file_sha(path)}}
    manifest["run_id"] = digest(manifest)
    atomic_json(directory / "run.json", manifest)
    report([directory], tmp_path / "report", figures=False)
    result = (tmp_path / "report/conditions.csv").read_text()
    assert "[MOCK]" in result and ",1,0,1," in result
