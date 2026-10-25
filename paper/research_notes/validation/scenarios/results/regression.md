# Focused regression: Results drafting permission and portable derivation

Reviewed the revised academic-paper-writer skill on 2026-10-25 against the same Results-planning request and workflow state used in the original test. The original `plan.md` remains unchanged.

The revised instruction explicitly requires `analysis_complete=true`, `full_writing_ready=true`, and a recorded gate rationale covering the intended section before a section is permitted. The scenario state has both booleans false and allows only evidence-backed outlines. Therefore prepare the actionable outline, evidence map, numerical candidate and missing-evidence requests, but do not draft a Results manuscript section. The existence of a reproducible cached numerical candidate does not itself open that gate. A historical Approved label also does not grant permission.

The earlier ambiguity about what constitutes a permitted section is resolved for this request/state. No remaining ambiguity changes the decision here. The change does not resolve the separate historical-scorer evidence limitation, nor should a drafting rule do so.

Portability change: `derive.py` now finds the nearest ancestor containing `results/MANIFEST.json` instead of assuming a fixed directory depth. Its recorded command is derived from the script's actual repository-relative path. Failure to find such an ancestor raises an explicit error. This supports later relocation beneath `paper/research_notes/validation/` without modifying research inputs or hard-coding an archive path.

Reran `.venv/Scripts/python.exe tmp/scenario-results-complete/derive.py`: exit code 0; N=100; valid=100; sum_valid_f1=100.0; mean_f1=1.0. Fresh manifest checks for coverage.csv, SOURCES.json, observations.jsonl.gz and inputs.jsonl.gz all passed. Input-join and null-response assertions also passed. Outputs remain bounded to the script's own isolated directory. Actual relocation has not been performed in this test; ancestor-based discovery and dynamic command recording were exercised at the present location. No production workflow state, manuscript, or research source was edited.
