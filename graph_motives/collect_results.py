"""Curate paper observations and final LLM payloads without copying run journals.

Sources: the final multimodel report, official Core v3, full Braw comparison,
native/explicit catalogs and the 2800 legacy rows retained in the full report.
No model calls or reconstruction of missing model responses.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
import shutil
import sqlite3
import uuid
from collections import Counter
from pathlib import Path, PureWindowsPath

from .common import canonical, records
from .common import digest as fingerprint
from .common import file_sha as digest

CODE_ROOT = Path(__file__).resolve().parents[1]
REPORT = "qm_report_20261014/failure_penalized_20261016_v2"
GEMMA = "sp500_pipeline/exp_prop/kg_experiments/output/gemma_all_experiments_report_20261012"
PREP = "sp500_pipeline/exp_prop/kg_experiments/output/prepare__20261004T141149Z__539251d0"
CORE = "qm_core_20261014/analyses/core_v3"
BRAW = "sp500_pipeline/outputs/braw_gemma"
MODERN = "outputs/braw_qwen_ministral_20261016"
MODERN_FINAL = "outputs/braw_qwen_ministral_20261016_retry_v2"
NATIVE = "sp500_pipeline/outputs/paper_native_20261011_gemma"
EXPLICIT = "sp500_pipeline/outputs/paper_async_20261011_gemma_v2"
QUESTIONS = "sp500_pipeline/outputs/paper_questions_20261011_final"
FIELDS = ("precision", "recall", "f1", "fp", "fn")


def clean(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value


class Export:
    def __init__(self, root, output):
        self.root, self.output = root.resolve(), output.resolve()
        self.sources, self.expected = {}, {}
        self.work = output.parent / (".article-export-" + uuid.uuid4().hex[:10])
        self.work.mkdir()
        self.db_path = self.work / "working.sqlite"
        self.db = sqlite3.connect(self.db_path)
        self.db.executescript("""
            PRAGMA journal_mode=OFF;
            CREATE TABLE observations(k TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE inputs(k TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE responses(k TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE prepared(k TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE events(k TEXT PRIMARY KEY, seq INTEGER NOT NULL, value TEXT NOT NULL);
        """)
        self.stats = Counter()
        self.counts = Counter()

    def path(self, value):
        path = Path(value)
        if not path.is_absolute():
            path = self.root / path
        if path.is_file() and path.resolve().is_relative_to(self.root):
            return path.resolve()
        parts = PureWindowsPath(str(value)).parts
        markers = [i for i, s in enumerate(parts) if s.casefold() == "agentgraphbench"]
        if markers:
            path = self.root.joinpath(*parts[markers[-1] + 1:])
            if path.is_file():
                return path.resolve()
        raise FileNotFoundError(value)

    def source(self, value):
        path = self.path(value)
        relative = path.relative_to(self.root).as_posix()
        if relative not in self.sources:
            sha = digest(path)
            expected = self.expected.get(relative)
            if expected and sha != expected:
                raise ValueError("Published source checksum differs: " + relative)
            self.sources[relative] = {"source_id": fingerprint(relative), "path": relative,
                                      "bytes": path.stat().st_size, "sha256": sha,
                                      "published_checksum_verified": expected is not None}
        return self.sources[relative]["source_id"]

    def read(self, value):
        self.source(value)
        return records(self.path(value))

    def json(self, value):
        self.source(value)
        return json.loads(self.path(value).read_text(encoding="utf-8-sig"))

    def load_manifest(self, relative, mode):
        manifest = self.json(relative)
        parent = Path(relative).parent
        if mode == "dict":
            entries = manifest["files_sha256"].items()
        else:
            entries = ((x.get("path", x.get("relative_path")), x["sha256"]) for x in manifest["files"] if x.get("sha256"))
        for name, sha in entries:
            self.expected[(parent / name).as_posix()] = sha

    def put(self, table, key, value):
        text = canonical(clean(value))
        old = self.db.execute(f"SELECT value FROM {table} WHERE k=?", (key,)).fetchone()
        if old:
            if old[0] != text:
                raise ValueError(f"Conflicting duplicate {table}: {key}")
            return
        self.db.execute(f"INSERT INTO {table}(k,value) VALUES (?,?)", (key, text))

    def get(self, table, key):
        row = self.db.execute(f"SELECT value FROM {table} WHERE k=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def frozen_inputs(self):
        for panel in ("core", "size", "calibration"):
            public = self.read(f"{PREP}/{panel}_public.jsonl.gz")
            private = self.read(f"{PREP}/{panel}_private.jsonl.gz")
            count = 0
            from itertools import zip_longest
            for p, q in zip_longest(public, private):
                if p is None or q is None or (p["record_id"], p["cell_id"]) != (q["record_id"], q["cell_id"]):
                    raise ValueError("Public/private frozen inputs do not pair")
                key = canonical([panel, p["record_id"], p["cell_id"]])
                self.put("prepared", key, {"public": p, "reference": q.get("private", q)})
                count += 1
            self.stats[f"frozen_{panel}"] = count
            self.db.commit()

    def input(self, messages, reference, *, frozen_public=None, candidate_names=None, question=None):
        public = frozen_public
        if messages:
            user = next((x["content"] for x in messages if x["role"] == "user"), "")
            try:
                parsed = json.loads(user)
                if isinstance(parsed, dict):
                    public = parsed
            except (ValueError, TypeError):
                pass
            if question is None:
                if public and isinstance(public, dict):
                    question = public.get("question", public.get("query"))
                else:
                    match = re.search(r"(?is)(?:User query|Question):\s*(.*?)(?:\n\s*\n|\nCandidate|\Z)", user)
                    question = match.group(1).strip() if match else None
        elif public:
            question = question or public.get("question", public.get("query"))
        if candidate_names is None and isinstance(public, dict):
            candidate_names = [x.get("name") for x in public.get("candidates", []) if isinstance(x, dict)]
        payload = {"messages": messages, "question": question, "candidate_names": candidate_names,
                   "reference": reference}
        if not messages:
            payload["frozen_public"] = public
        input_id = fingerprint(payload)
        self.put("inputs", input_id, {"input_id": input_id, **payload})
        return input_id, question

    def response(self, value):
        value = clean(value)
        response_id = fingerprint(value)
        self.put("responses", response_id, {"response_id": response_id, **value})
        return response_id

    def observation(self, row):
        key = [row["series_id"], row["model"], row["condition"], row.get("noise"), row["base_id"]]
        observation_id = fingerprint(key)
        row.update(schema_version="article_observation_v1", observation_id=observation_id)
        self.put("observations", observation_id, row)
        self.counts[(row["series_id"], row["model"], row["condition"], row.get("noise"))] += 1

    def base(self, r):
        model = "gemma-4-31b" if r["model"] == "gemma-4-31b-cached" else r["model"]
        return {"series_id": r["series_id"], "model": model, "source_model_alias": r["model"],
                "provider_model": r.get("provider_model"), "base_id": r["base_id"],
                "condition": r["condition"], "noise": r.get("noise"), "motif": r.get("motif"), "size": r.get("size"),
                "status": r["status"], "valid": r["strict_completed"],
                "metrics": {**{k: r.get(k) if r["strict_completed"] else None for k in FIELDS},
                            "exact": r.get("semantic_exact") if r["strict_completed"] else None},
                "job_id": r.get("job_id"), "task_lineage_sha256": r.get("task_lineage_sha256"),
                "input_id": None, "response_id": None, "question": None, "selected_names": None,
                "request_evidence": "unavailable", "response_evidence": "unavailable",
                "usage": {k: r.get(k) for k in ("input_tokens", "output_tokens", "cost_usd")},
                "source_refs": []}

    def cache_rows(self):
        return list(self.read(f"{REPORT}/data/model_observations.jsonl.gz"))

    def index_journals(self, selected, files):
        for value in sorted(set(map(str, files))):
            path = self.path(value)
            source_id = self.source(path)
            for e in records(path):
                aid = e.get("attempt_id")
                if aid not in selected:
                    continue
                request = e.get("request")
                if request and fingerprint(request) != e["request_id"]:
                    raise ValueError("Request fingerprint mismatch: " + str(path))
                # Keep only one final snapshot per selected attempt; not the journal history.
                value = {k: e.get(k) for k in ("attempt_id", "attempt", "request_id", "request", "response",
                                              "parsed_output", "event", "error", "timestamp_utc", "latency_ms", "sequence")}
                value["source_id"] = source_id
                sequence = e.get("sequence", 0)
                self.db.execute("INSERT INTO events(k,seq,value) VALUES (?,?,?) ON CONFLICT(k) DO UPDATE SET seq=excluded.seq,value=excluded.value WHERE excluded.seq>=events.seq",
                                (aid, sequence, canonical(value)))
            self.db.commit()

    def attach_event(self, out, e, reference, *, source_selected=None):
        request = e["request"]
        messages = [{"role": "system", "content": request["system_prompt"]},
                    {"role": "user", "content": request["user_prompt"]}]
        out["input_id"], out["question"] = self.input(messages, reference, candidate_names=request.get("candidate_names"))
        out["request_id"] = e["request_id"]
        out["attempt_id"] = e["attempt_id"]
        out["request_metadata"] = {k: v for k, v in request.items() if k not in ("system_prompt", "user_prompt", "candidate_names")}
        out["request_evidence"] = "recorded_api_journal"
        out["source_refs"].append({"source_id": e["source_id"], "attempt_id": e["attempt_id"], "sequence": e["sequence"]})
        if e["response"] is not None:
            response = e["response"]
            out["response_id"] = self.response({"text": response.get("text"), "parsed_output": e["parsed_output"],
                "provider_request_id": response.get("provider_request_id"), "actual_model": response.get("actual_model"),
                "finish_reason": response.get("finish_reason"), "usage": {k: response.get(k) for k in ("input_tokens", "output_tokens", "cost_usd")},
                "latency_ms": e["latency_ms"], "error": e["error"]})
            out["response_evidence"] = "recorded_api_journal"
        out["selected_names"] = source_selected
        parsed = e.get("parsed_output")
        if out["valid"]:
            if not parsed or set(parsed.get("selected_entities", [])) != set(source_selected or []):
                raise ValueError("Selected names differ from the final journal output")

    def modern_core(self, report):
        normalized = list(self.read(f"{CORE}/data/selection_jobs.jsonl.gz"))
        authoritative = {r["job_id"]: r for r in report if r["series_id"] == "core" and r["model"] != "gemma-4-31b-cached"}
        selected, journals = set(), set()
        for r in normalized:
            attempt_ids = set(r.get("attempt_ids", [])) | {x.get("attempt_id") for x in r["source_refs"]}
            attempt_ids.add(r.get("attempt_id"))
            attempt_ids.discard(None)
            selected.update(attempt_ids)
            journals.update(x["path"] for x in r["source_refs"] if x.get("attempt_id") in attempt_ids and x["path"].endswith(".jsonl"))
        self.index_journals(selected, journals)
        source_id = self.source(f"{CORE}/data/selection_jobs.jsonl.gz")
        for r in normalized:
            published = authoritative.pop(r["job_id"])
            self.compare_metrics(r, published)
            out = self.base(published)
            frozen = self.get("prepared", canonical(["core", r["base_id"], r["cell_id"]]))
            if frozen is None:
                raise ValueError("Core frozen input is missing")
            if frozen["public"]["materialized_sha256"] != r["materialized_sha256"]:
                raise ValueError("Core materialized fingerprint differs")
            attempt_ids = list(dict.fromkeys([r.get("attempt_id"), *r.get("attempt_ids", []),
                                             *(x.get("attempt_id") for x in r["source_refs"])]))
            events = [self.get("events", aid) for aid in attempt_ids if aid]
            matching = [e for e in events if e and e["request_id"] == r["request_id"]]
            received = [e for e in matching if e["response"] is not None]
            if len(received) != 1:
                raise ValueError(f"Expected one final received Core response: {r['job_id']}, found {len(received)}")
            event = received[0]
            self.attach_event(out, event, {"expected_names": r["expected_names"], "private": frozen["reference"]}, source_selected=r.get("selected_names"))
            out["source_refs"].append({"source_id": source_id, "job_id": r["job_id"]})
            out["runtime"] = {k: r.get(k) for k in ("transport_attempts", "usage_complete", "elapsed_seconds", "error_category", "recovery_kind")}
            out["versions"] = {k: r.get(k) for k in ("protocol_version", "prompt_version", "card_version", "question_version", "parser_version")}
            self.observation(out)
        if authoritative:
            raise ValueError("Unexported published Core rows")
        self.db.commit()

    @staticmethod
    def compare_metrics(source, published):
        valid = bool(source.get("strict_completed", source.get("valid")))
        if valid != bool(published["strict_completed"]):
            raise ValueError("Published validity differs")
        if not valid:
            return  # Older scorers store zeros; the current report retains null per-task metrics.
        for field in FIELDS:
            a, b = source.get(field), published.get(field)
            if a is None and b is None:
                continue
            if a is None or b is None or not math.isclose(float(a), float(b), rel_tol=1e-10, abs_tol=1e-10):
                raise ValueError(f"Published metric differs: {field} {a} != {b}")

    def gemma_controlled(self, report):
        source_id = self.source(f"{REPORT}/data/model_observations.jsonl.gz")
        for r in report:
            if r["model"] != "gemma-4-31b-cached" or r["series_id"] not in ("core", "size", "calibration", "incremental"):
                continue
            out = self.base(r)
            series, condition = r["series_id"], r["condition"]
            if series == "incremental":
                series, condition = "core", condition.removesuffix("-inc")
            frozen = self.get("prepared", canonical([series, r["base_id"], condition]))
            if frozen:
                out["input_id"], out["question"] = self.input(None, {"private": frozen["reference"]}, frozen_public=frozen["public"]["public"])
                out["request_evidence"] = "frozen_initial_context_only" if r["series_id"] == "incremental" else "frozen_input_not_authenticated_api_request"
                out["frozen_input_metadata"] = {k: v for k, v in frozen["public"].items() if k != "public"}
            out["response_evidence"] = "metrics_cache_only_no_raw_response"
            out["source_refs"] = [{"source_id": source_id, "job_id": r["job_id"]}]
            out["logical_turns"] = r.get("logical_turns")
            self.observation(out)
        self.db.commit()

    def gemma_braw(self, report):
        jobs, refs = {}, {}
        for folder in (BRAW + "/prepared", BRAW + "/full_sizes_20261013/prepared"):
            self.load_manifest(folder + "/manifest.json", "dict")
            jobs.update({x["job_id"]: x for x in self.read(folder + "/jobs.public.jsonl.gz")})
            refs.update({x["job_id"]: x for x in self.read(folder + "/references.private.jsonl.gz")})
        published = {x["job_id"]: x for x in report if x["series_id"] == "full_braw"}
        source_id = self.source(GEMMA + "/data/fullsizes_outcomes.jsonl.gz")
        for r in self.read(GEMMA + "/data/fullsizes_outcomes.jsonl.gz"):
            p = published.pop(r["job_id"])
            converted = {"strict_completed": r["valid"], **{k: (r["metrics"] or {}).get("selection_" + k, (r["metrics"] or {}).get(k)) for k in FIELDS}}
            self.compare_metrics(converted, p)
            job, ref = jobs[r["job_id"]], refs[r["job_id"]]
            if set(r["reference_names"]) != set(ref["reference_names"]):
                raise ValueError("Braw gold mismatch")
            out = self.base(p)
            out["provider_model"] = r.get("actual_model") or r.get("model")
            out["input_id"], out["question"] = self.input(job["messages"], ref)
            out["request_evidence"] = "hash_verified_exported_job"
            out["request_metadata"] = {k: v for k, v in job.items() if k != "messages"}
            out["request_id"] = r["request_id"]
            out["selected_names"] = r.get("selected_entities")
            out["response_id"] = self.response({"text": r.get("raw_output"), "provider_request_id": r.get("provider_request_id"),
                "actual_model": r.get("actual_model"), "finish_reason": r.get("finish_reason"),
                "usage": {k: r.get(k) for k in ("input_tokens", "output_tokens", "cost_usd")},
                "latency_ms": r.get("latency_ms"), "error": r.get("error")})
            out["response_evidence"] = "saved_individual_outcome_with_raw_output"
            out["reused_core"] = r["reused_core"]
            out["source_refs"] = [{"source_id": source_id, "job_id": r["job_id"]}]
            self.observation(out)
        if published:
            raise ValueError("Incomplete Gemma Braw export")
        self.db.commit()

    def modern_braw(self):
        outcomes = list(self.read(MODERN_FINAL + "/results/outcomes.jsonl.gz"))
        selected = {a for r in outcomes for a in r["attempt_ids"]}
        journals = [p for folder in (MODERN, MODERN_FINAL) for p in (self.root / folder / "runs").glob("*/live_calls.jsonl")]
        self.index_journals(selected, journals)
        by_request = {r["request_id"]: r for r in outcomes}
        source_id = self.source(MODERN_FINAL + "/results/outcomes.jsonl.gz")
        for m in self.read(MODERN + "/materials.private.jsonl.gz"):
            r = by_request.pop(m["request_id"])
            events = [self.get("events", aid) for aid in r["attempt_ids"]]
            if any(e is None for e in events):
                raise ValueError("Braw selected attempts missing")
            received = [e for e in events if e["response"] is not None]
            if len(received) > 1:
                raise ValueError("Ambiguous repeated Braw received response")
            event = received[0] if received else events[-1]
            if event["request_id"] != r["request_id"] or event["request"] != m["request"]:
                raise ValueError("Braw actual request differs from frozen material")
            adapted = {**r, "series_id": "full_braw"}
            out = self.base(adapted)
            self.attach_event(out, event, m["reference"], source_selected=r.get("selected_names"))
            out["source_refs"].append({"source_id": source_id, "job_id": r["job_id"]})
            out["source_series_id"] = r["series_id"]
            out["runtime"] = {k: r.get(k) for k in ("transport_attempts", "usage_complete", "witness_n")}
            self.observation(out)
        if by_request:
            raise ValueError("Braw rows missing inputs")
        self.db.commit()

    def native(self, report):
        authoritative = {(r["base_id"], r["condition"], r["noise"]): r for r in report if r["series_id"] == "native_d"}
        for folder, jobs_folder in ((NATIVE, NATIVE + "/exported"), (EXPLICIT, QUESTIONS + "/explicit_control")):
            jobs = {r["job_id"]: r for r in self.read(jobs_folder + "/jobs.public.jsonl.gz")}
            refs = {r["job_id"]: r for r in self.read(jobs_folder + "/references.private.jsonl.gz")}
            response_path = GEMMA + ("/data/native_responses.jsonl" if folder == NATIVE else "/data/explicit_responses.jsonl")
            responses = {r["job_id"]: r for r in self.read(response_path)}
            source_id = self.source(response_path)
            for row in self.read(folder + "/scored/outcomes.jsonl.gz"):
                p = authoritative.pop((row["record_id"], row["condition"], row["noise"]))
                self.compare_metrics({**row, "fp": p["fp"], "fn": p["fn"]}, p)
                job, ref, response = jobs[row["job_id"]], refs[row["job_id"]], responses[row["job_id"]]
                if job["job_sha256"] != response["job_sha256"] or job["job_sha256"] != ref["job_sha256"]:
                    raise ValueError("Native request/response/reference job hashes differ")
                out = self.base(p)
                out["job_id"] = row["job_id"]
                out["input_id"], out["question"] = self.input(job["messages"], ref, candidate_names=job.get("candidate_names"))
                out["request_evidence"] = "exported_job_hash_bound_to_saved_response"
                out["request_metadata"] = {k: v for k, v in job.items() if k not in ("messages", "candidate_names")}
                out["response_id"] = self.response({"text": response.get("raw"), **{k: response.get(k) for k in ("event", "status", "request_id", "provider_request_id")}})
                out["response_evidence"] = "saved_raw_response"
                try:
                    parsed = json.loads(response["raw"])
                    out["selected_names"] = parsed.get("selected_tools", parsed.get("selected_entities")) if isinstance(parsed, dict) else None
                except (ValueError, TypeError):
                    pass
                out["source_refs"] = [{"source_id": source_id, "job_id": row["job_id"]}]
                out["failure_reason"] = row.get("failure_reason")
                self.observation(out)
            self.db.commit()
        if authoritative:
            raise ValueError("Missing native catalog observations")

    def legacy(self):
        cached = {(r["agent"], r["variant"], r["record_id"]): r for r in self.read(GEMMA + "/data/legacy_metrics.jsonl.gz")}
        published = {(r["agent"].lower(), r["noise"], r["base_id"]): r for r in self.read(GEMMA + "/data/all_observations.jsonl.gz") if r["cohort"] == "historical"}
        for directory, model, short in (("gemma_chain_800_continued", "gemma-4-31b", "gemma"),
                                         ("gemma_tree_in_1200", "gemma-4-31b", "gemma"),
                                         ("qwen_chain_800", "qwen3.6-flash", "qwen")):
            base = "sp500_pipeline/output/" + directory
            config = self.json(base + "/config.json")
            for variant in ("disconnected", "adjacent"):
                items = {r["record_id"]: r for r in self.read(base + f"/items/items_{variant}.jsonl.gz")}
                repair = self.root / base / "repair_24/items.jsonl.gz"
                if variant == "disconnected" and repair.is_file():
                    items.update({r["record_id"]: r for r in self.read(repair)})
                path = base + f"/runs/{model}__{variant}__live.jsonl"
                source_id = self.source(path)
                for raw in self.read(path):
                    cache = cached.pop((model, variant, raw["record_id"]))
                    if raw["metrics"] != cache["metrics"]:
                        raise ValueError("Legacy metrics differ from published cache")
                    p = published.pop((short, variant, raw["record_id"]))
                    item = items[raw["record_id"]]
                    if fingerprint(item) != raw["item_hash"]:
                        raise ValueError("Legacy input fingerprint differs from the recorded run")
                    r = {"series_id": "legacy", "model": model, "base_id": raw["record_id"], "condition": "legacy_node_only",
                         "noise": variant, "motif": raw["subgraph_type"], "size": raw["size"],
                         "status": p["status"], "strict_completed": p["valid"], "provider_model": raw["model"],
                         **{k: p.get(k) for k in FIELDS}, "semantic_exact": p["exact"]}
                    out = self.base(r)
                    stages = []
                    for trace in raw.get("trace", []):
                        messages = [{"role": "system", "content": trace["system"]}, {"role": "user", "content": trace["prompt"]}]
                        input_id, question = self.input(messages, item["private"], question=item["public"]["question"])
                        response_id = self.response({"text": trace.get("output"), "stage": trace["stage"]})
                        stages.append({"stage": trace["stage"], "input_id": input_id, "response_id": response_id})
                        if trace["stage"] == "selection":
                            out.update(input_id=input_id, response_id=response_id, question=question)
                    out["stages"] = stages
                    out["request_evidence"] = "recorded_legacy_trace" if stages else "unavailable"
                    out["response_evidence"] = "recorded_legacy_trace" if stages else "unavailable"
                    out["known_selected_names"] = raw.get("selected_entities")
                    out["unknown_names"] = raw.get("unknown_entities", [])
                    out["selected_names"] = list(dict.fromkeys((raw.get("selected_entities") or []) + raw.get("unknown_entities", [])))
                    out["metric_normalization"] = "whitespace_casefold"
                    out["predicted_answer"] = raw.get("predicted_answer")
                    out["judge_verdict"] = raw.get("judge_verdict")
                    out["historical_metrics"] = raw["metrics"]
                    out["usage"] = raw.get("usage")
                    out["judge_usage"] = raw.get("judge_usage")
                    out["recorded_run_hash"] = raw.get("run_hash")
                    out["protocol"] = raw.get("protocol")
                    out["declared_run_settings"] = config.get("llm")
                    out["errors"] = {k: raw.get(k) for k in ("selection_error", "answer_error", "judge_error", "error")}
                    out["source_refs"] = [{"source_id": source_id, "record_id": raw["record_id"]}]
                    self.observation(out)
                self.db.commit()
        if cached or published:
            raise ValueError("Legacy panel is incomplete")

    def write(self):
        self.output.mkdir(parents=True)
        native_specs = GEMMA + "/data/native_semantic_specs.jsonl.gz"
        self.source(native_specs)
        shutil.copyfile(self.path(native_specs), self.output / "task_specs_native.jsonl.gz")
        counts, coverage = {}, Counter()
        for table in ("observations", "inputs", "responses"):
            path = self.output / (table + ".jsonl.gz")
            count = 0
            with path.open("wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
                for (text,) in self.db.execute(f"SELECT value FROM {table} ORDER BY k"):
                    compressed.write((text + "\n").encode("utf-8"))
                    count += 1
                    if table == "observations":
                        row = json.loads(text)
                        for field in ("input_id", "response_id"):
                            if row[field] and self.db.execute(f"SELECT 1 FROM {'inputs' if field == 'input_id' else 'responses'} WHERE k=?", (row[field],)).fetchone() is None:
                                raise ValueError("Dangling payload reference")
                        coverage[(row["series_id"], row["model"], row["request_evidence"], row["response_evidence"])] += 1
            counts[table] = count
        if counts["observations"] != 60088:
            raise ValueError(f"Expected 60088 unique paper observations, got {counts['observations']}")
        (self.output / "SOURCES.json").write_text(json.dumps({"source_root_label": "AgentGraphBench", "files": sorted(self.sources.values(), key=lambda x: x["path"])}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with (self.output / "coverage.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["series_id", "model", "request_evidence", "response_evidence", "N"])
            writer.writerows([*key, value] for key, value in sorted(coverage.items()))
        with (self.output / "panel_counts.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["series_id", "model", "condition", "noise", "N"])
            writer.writerows([*key, value] for key, value in sorted(self.counts.items(), key=str))
        manifest = {"schema_version": "article_results_v1", "counts": counts,
                    "scope": "full final report plus published three-model Braw comparison and legacy comparison",
                    "excluded": ["pilot", "smoke", "mock", "superseded analyses", "journal event histories", "duplicate Braw core rows"],
                    "metric_policy": "Individual valid-task scores; invalid metrics remain null. Primary averages sum valid scores / planned N.",
                    "missing_raw_responses": "Gemma controlled core/size/calibration/incremental: metrics cache only; no generated replacement answers",
                    "network_requests_made": 0, "stats": dict(self.stats),
                    "generator": {"path": "graph_motives/collect_results.py", "sha256": digest(Path(__file__))},
                    "files": [{"path": p.name, "bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(self.output.iterdir()) if p.is_file()]}
        (self.output / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(self.output), **counts, "source_files": len(self.sources)}, ensure_ascii=False), flush=True)

    def close(self):
        self.db.close()
        self.db_path.unlink()
        self.work.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=CODE_ROOT / "results")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Use a new output directory; existing results are never overwritten")
    export = Export(args.source_root, args.output)
    try:
        export.load_manifest(REPORT + "/MANIFEST.json", "list")
        export.load_manifest(GEMMA + "/MANIFEST.json", "dict")
        export.load_manifest(CORE + "/delivery_manifest.json", "list")
        preparation = export.json(PREP + "/artifact_manifest.json")
        for name, entry in preparation["files"].items():
            export.expected[PREP + "/" + name] = entry["sha256"]
        export.frozen_inputs()
        report = export.cache_rows()
        print("Frozen inputs and final report loaded", flush=True)
        export.modern_core(report)
        print("Modern Core payloads matched", flush=True)
        export.gemma_controlled(report)
        export.gemma_braw(report)
        print("Gemma controlled and Braw rows matched", flush=True)
        export.modern_braw()
        print("Modern Braw final attempts matched", flush=True)
        export.native(report)
        print("Catalog responses matched", flush=True)
        export.legacy()
        print("Legacy stage traces matched", flush=True)
        export.write()
    finally:
        export.close()


if __name__ == "__main__":
    main()
