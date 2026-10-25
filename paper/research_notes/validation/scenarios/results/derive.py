"""Bounded stdlib-only archival aggregate; no project imports or model calls."""
import collections
import gzip
import hashlib
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve()
ROOT = next((ancestor for ancestor in SCRIPT.parents if (ancestor / "results/MANIFEST.json").is_file()), None)
if ROOT is None:
    raise RuntimeError("Cannot locate repository ancestor containing results/MANIFEST.json")
OUT = SCRIPT.parent
COMMAND = ".venv/Scripts/python.exe " + SCRIPT.relative_to(ROOT).as_posix()
selector = dict(series_id="calibration", model="gemma-4-31b", condition="CAL:explicit_neighbor", noise="disconnected")
def read_rows(name):
    with gzip.open(ROOT / "results" / name, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)
rows = [r for r in read_rows("observations.jsonl.gz") if all(r.get(k) == v for k,v in selector.items())]
assert len({r["observation_id"] for r in rows}) == len(rows)
inputs = {r["input_id"] for r in rows}
found = {r["input_id"] for r in read_rows("inputs.jsonl.gz") if r["input_id"] in inputs}
assert inputs == found
assert all(r.get("response_id") is None for r in rows)
sources = json.loads((ROOT / "results/SOURCES.json").read_text(encoding="utf-8"))
source_ids = {s["source_id"] for r in rows for s in r["source_refs"]}
resolved = [s for s in sources["files"] if s["source_id"] in source_ids]
assert len(resolved) == len(source_ids)
files = ["results/MANIFEST.json", "results/coverage.csv", "results/SOURCES.json", "results/observations.jsonl.gz", "results/inputs.jsonl.gz", "paper/research_notes/workflow_state.json"]
manifest = json.loads((ROOT / files[0]).read_text())
hashes = {f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
checks = {f: hashes['results/'+f] == next(x['sha256'] for x in manifest['files'] if x['path']==f) for f in ['coverage.csv','SOURCES.json','observations.jsonl.gz','inputs.jsonl.gz']}
assert all(checks.values())
valid = [r for r in rows if r['valid']]
total = sum(float(r['metrics']['f1']) for r in valid)
record = dict(selector=selector, N=len(rows), valid=len(valid), statuses=dict(collections.Counter(r['status'] for r in rows)), sum_valid_f1=total, mean_f1=total/len(rows), formula='sum(metrics.f1 for valid rows) / all selected planned rows; invalid contributes zero', evidence_tier='fresh aggregation of archived cached metrics, not raw-response rescore', provider_model_values=list({r.get('provider_model') for r in rows}), protocol_versions=list({r['frozen_input_metadata']['protocol_version'] for r in rows}), request_evidence=list({r['request_evidence'] for r in rows}), response_evidence=list({r['response_evidence'] for r in rows}), input_join_matches=len(found), response_join='All response_id values null; no raw reply exists for these selected records', historical_scorer_version='Not established by this bounded inspection; do not substitute current scorer', hashes=hashes, fresh_manifest_hash_checks=checks, historical_source_records=resolved, checked_on='2026-10-25', command=COMMAND, revision='261f1b3cc3d3bf3419c04d3d0a35d290fce73cae', working_tree='git status --short showed untracked .agents/, AGENTS.md, paper/, draft files and PDF; relevant inspected files bound by hashes', uncertainty='Descriptive only; no CI or significance test', pairing='Single cell; no paired comparison or independence inference')
(OUT/'candidate.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
fields=['observation_id','base_id','input_id','response_id','valid','status','metrics','source_refs','task_lineage_sha256']
(OUT/'selected_rows.jsonl').write_text(''.join(json.dumps({k:r.get(k) for k in fields})+'\n' for r in rows),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['N','valid','sum_valid_f1','mean_f1','fresh_manifest_hash_checks']}))
