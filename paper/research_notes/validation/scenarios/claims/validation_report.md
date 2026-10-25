# Validation report

Command: `.venv/Scripts/python.exe paper/research_notes/scripts/validate_research_artifacts.py --root . --notes tmp/scenario-claims-complete`

Result: passed; 14 evidence records, 22 atomic claims, no structural errors. See validation.json. This checks hashes and minimal schema only; it does not establish historical execution, source truth, or manuscript readiness. No skills changed, so quick_validate was not applicable to this evaluator.

The generic `python` command resolved to an unusable Windows Store alias. The existing `.venv/Scripts/python.exe` worked. No environment installation was needed.

Archive inspection procedure: open results/inputs.jsonl.gz with standard-library gzip.open(..., 'rt', encoding='utf-8'); use itertools.islice(stream, 100); parse each with json.loads. Record physical line and input_id, reference.condition/motif/size, len(candidate_names), len(set(candidate_names)), len(reference.reference_names), and for physical line 1 the system-role message. This gives archive_sample.json. Also inspected only the first record of observations.jsonl.gz to understand archive schema; no metric claim uses it. No imports from graph_motives or execution of project experiment code occurred.

Evidence creation: `.venv/Scripts/python.exe tmp/scenario-claims-complete/write_records.py`, using hashlib.file_digest SHA-256 and Git revision/status. All authored outputs remain inside this isolated directory.
