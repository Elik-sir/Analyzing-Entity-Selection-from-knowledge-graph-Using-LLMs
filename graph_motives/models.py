"""LangChain transports. Prompts, parsing and retry policy belong to the experiment."""

import asyncio
import os
import re
import time
from contextvars import ContextVar
from copy import deepcopy

from .common import canonical

PROVIDERS = {"openrouter", "openai", "openai-compatible"}
MODEL_FIELDS = {"alias", "provider", "model", "api_key_env", "base_url", "parameters"}
RESERVED = {
    "api_key",
    "openai_api_key",
    "model",
    "model_name",
    "base_url",
    "openai_api_base",
    "max_retries",
    "callbacks",
    "http_client",
    "http_async_client",
    "streaming",
    "default_headers",
    "default_query",
    "model_kwargs",
    "temperature",
    "max_tokens",
    "max_completion_tokens",
    "response_format",
    "tools",
    "tool_choice",
    "n",
    "use_responses_api",
    "client",
    "async_client",
    "root_client",
    "root_async_client",
    "cache",
}


def validate_model(spec):
    if not isinstance(spec, dict) or set(spec) - MODEL_FIELDS:
        raise ValueError("Unknown model configuration fields")
    for field in ("alias", "provider", "model", "api_key_env"):
        if not isinstance(spec.get(field), str) or not spec[field].strip():
            raise ValueError("Missing model field: " + field)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", spec["alias"]) or spec["alias"].endswith("."):
        raise ValueError("Invalid model alias")
    if spec["provider"] not in PROVIDERS:
        raise ValueError("Supported providers: " + ", ".join(sorted(PROVIDERS)))
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", spec["api_key_env"]):
        raise ValueError("api_key_env must name an environment variable")
    if spec["provider"] == "openai-compatible" and not spec.get("base_url"):
        raise ValueError("openai-compatible requires base_url")
    params = spec.get("parameters", {})
    if not isinstance(params, dict) or set(params) & RESERVED:
        raise ValueError("Invalid/reserved LangChain parameters")
    extra = params.get("extra_body", {})
    if not isinstance(extra, dict) or set(extra) & (RESERVED | {"messages", "stream"}):
        raise ValueError("extra_body cannot replace experiment messages/model/settings/tools")
    canonical(spec)
    return deepcopy(spec)


class LangChainBackend:
    def __init__(self, spec):
        self.spec = validate_model(spec)
        key = os.environ.get(spec["api_key_env"])
        if not key:
            raise ValueError("Set environment variable " + spec["api_key_env"])
        params = deepcopy(spec.get("parameters", {}))
        params.update(model=spec["model"], api_key=key, max_retries=0, streaming=False)
        if spec.get("base_url"):
            params["base_url"] = spec["base_url"]
        import httpx
        from langchain_openai import ChatOpenAI
        from langchain_openai.chat_models.base import BaseChatOpenAI

        class CompatibleChatModel(ChatOpenAI):
            def _get_request_payload(self, input_, *, stop=None, **kwargs):
                # Preserve max_tokens and the system role for the frozen protocol.
                # ChatOpenAI's OpenAI-specific overrides otherwise rewrite both.
                return BaseChatOpenAI._get_request_payload(self, input_, stop=stop, **kwargs)

            @property
            def _default_params(self):
                return BaseChatOpenAI._default_params.fget(self)

        self.capture = ContextVar("wire_capture", default=None)

        async def sent(request):
            capture = self.capture.get()
            if capture is not None:
                import json

                capture["request"] = json.loads(request.content)

        async def received(response):
            capture = self.capture.get()
            if capture is not None and response.status_code == 200:
                await response.aread()
                capture["response_text"] = response.text
                try:
                    capture["response"] = response.json()
                except ValueError:
                    capture["invalid_json"] = True

        self.http = httpx.AsyncClient(event_hooks={"request": [sent], "response": [received]})
        params.update(use_responses_api=False, http_async_client=self.http, http_socket_options=())
        if spec["provider"] == "openrouter":
            params.setdefault("base_url", "https://openrouter.ai/api/v1")
        self.client = CompatibleChatModel(**params)

    async def complete(self, request):
        settings = request["settings"]
        token_field = "max_completion_tokens" if self.spec["provider"] == "openai" else "max_tokens"
        options = {"temperature": settings["temperature"], token_field: settings["max_tokens"]}
        if request.get("tools"):
            options.update(tools=request["tools"], tool_choice=request["tool_choice"])
        elif settings["response_format"] == "json_object":
            options["response_format"] = {"type": "json_object"}
        started = time.monotonic()
        capture = {}
        token = self.capture.set(capture)
        adapter_error = None
        try:
            message = await asyncio.wait_for(
                self.client.ainvoke(request["messages"], **options), timeout=settings["timeout_s"]
            )
        except Exception as error:
            if "response_text" not in capture:
                raise
            # Even an SDK validation failure must retain a received provider reply.
            adapter_error = type(error).__name__
            message = None
        finally:
            self.capture.reset(token)
        raw = message.model_dump(mode="json") if message is not None else None
        wire = capture.get("response", {})
        choices = wire.get("choices", []) if isinstance(wire, dict) else []
        text = choices[0].get("message", {}).get("content", "") if len(choices) == 1 else ""
        if isinstance(text, list):
            text = "".join(
                block.get("text", "")
                for block in text
                if isinstance(block, dict) and block.get("type") == "text"
            )
        if request.get("tools"):
            # Preserve the original function argument string, including malformed JSON.
            calls = choices[0].get("message", {}).get("tool_calls", []) if len(choices) == 1 else []
            function = calls[0].get("function", {}) if len(calls) == 1 else {}
            text = function.get("arguments", "") if function.get("name") == "final_result" else ""
        return {
            "text": text if isinstance(text, str) else "",
            "message": raw,
            "usage": message.usage_metadata if message is not None else None,
            "metadata": message.response_metadata if message is not None else {},
            "wire_request": capture.get("request"),
            "wire_response": capture.get("response"),
            "wire_response_text": capture.get("response_text"),
            "adapter_error": adapter_error,
            "elapsed_s": time.monotonic() - started,
        }

    async def aclose(self):
        await self.http.aclose()


class MockBackend:
    """Offline transport test. Has no access to private references or gold names."""

    async def complete(self, request):
        schema = request["schema"]
        if schema == "incremental_v1":
            value = {"action": "done", "name": None, "insufficient_evidence": True}
        elif schema == "answer_v1":
            value = {"answer": "Insufficient supplied evidence.", "insufficient_evidence": True}
        elif schema in {"judge_v1", "legacy_judge_v1"}:
            value = {"correct": False, "metadata_sufficient": False, "reason": "Offline mock."}
        elif schema == "paper_selected_tools_v1":
            value = {"selected_tools": []}
        else:
            key = "result" if schema == "calibration_v1" else "selected_entities"
            value = {key: [], "insufficient_evidence": True}
        return {
            "text": canonical(value),
            "message": None,
            "usage": None,
            "metadata": {"mock": True},
            "elapsed_s": 0,
        }
