# Scoped-output regression

Tested revised `.agents/skills/claim-verifier/SKILL.md`, SHA-256 `98da210272f67c31e4752effea2f966dafa749c82a6714b4d151cb9f852c40c6`, on 2026-10-25.

The new procedure step 7 explicitly directs `--notes <audit-directory>` for an isolated audit, with scoped evidence/claim records and a copy of current workflow_state.json. The added Outputs paragraph explicitly redirects reports and records to the requested bounded destination, limits coverage claims, and prohibits opening the production writing gate. These changes resolve the previously observed output-routing and validation ambiguity.

To preserve the original forward-test artifacts, copied its evidence_register.json and claims.jsonl into the new regression_validation/ subdirectory. Copied the actual production paper/research_notes/workflow_state.json byte-for-byte into that subdirectory. Source and copy SHA-256 both equal `21007127f77e0d1f9e534f1b8d9a7cc54b116cc3af6be07975f80dbf588e8d3a`. Both analysis_complete and full_writing_ready remain false. The copied status is bookkeeping input, not newly verified prior conclusions or a readiness assessment. No prior production audit reports were reread and no production files were modified.

Command: `.venv/Scripts/python.exe paper/research_notes/scripts/validate_research_artifacts.py --root . --notes tmp/scenario-claims-complete/regression_validation`

Result: passed; 14 evidence records, 22 claims, no structural errors. Exact output is regression_validation/validation.json. This validates only structure, local links and hashes; no source audit was repeated, and no historical execution or full-manuscript readiness is certified. The original audit.md, evidence_register.json, claims.jsonl, workflow_state.json, and original validation artifacts remain intact.

## Exact archived prompt locator for C20/C21

Source: results/inputs.jsonl.gz, first physical JSONL record, input_id `000071451200148392a2dd08214e2974080d469fdc6ec61b6f3f321220fca8c4`. The source hash is recorded in the original evidence_register.json under `archive`. Locate `messages[0].role == "system"`, then read `messages[0].content` (equivalently messages filtered by role=system). The record's `reference.condition` is Braw, `reference.record_id` is `f0144ff013fa75ad6631534a`, `reference.variant` is disconnected, `reference.motif` is star_out, and `reference.size` is 8. This is a bounded example, not a core-size or complete-population verification.

That system message states: "If evidence is incomplete, select only supported entities and set insufficient_evidence=true." It also instructs: "Return exactly one JSON object with selected_entities (an array of distinct exact candidate names) and insufficient_evidence (a boolean)." Earlier in the same string, the all-route convention includes the named starting entity, requested endpoints, and intermediate entities on any supported route, including parallel supporting routes, and explicitly says membership does not imply each card is independently necessary evidence.

C20 therefore concerns ambiguity in the manuscript's description of the selection convention. C21 is supported as the requested response protocol. Neither assertion means that the model actually returned insufficient_evidence, complied with the schema, or answered correctly: this is archived input evidence, not response evidence. The convenience-sample copy of the exact system string is in archive_sample.json at rows[0].system_prompt.
