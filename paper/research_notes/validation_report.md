# Skill system validation

Checked 2026-10-25. Source revision: `261f1b3cc3d3bf3419c04d3d0a35d290fce73cae`.

## Completed checks

- All eight requested skill folders contain `SKILL.md` with matching YAML `name`, a discriminating `description`, and explicit input/procedure/output/completion sections.
- Ran the bundled `C:/Users/ekurm/.codex/skills/.system/skill-creator/scripts/quick_validate.py` against each folder with `.venv/Scripts/python.exe -X utf8`: **8 passed**. No unfinished scaffold placeholders remained. No optional UI metadata or external plugin dependencies were required.
- Checked relative Markdown links from root `AGENTS.md` and every skill entrypoint: all resolved. The shared contract specifies note-file path resolution and staged outputs.
- Ran `paper/research_notes/scripts/validate_research_artifacts.py --root .`: **passed**, with 12 evidence records and 4 bootstrap claims. This checks IDs, source hashes, classifications, numeric result provenance and the writing gate, not scientific truth.
- Exercised the validator in isolated temporary fixtures: valid real evidence passed; a stale source hash, a draft substituted for numeric result evidence, a missing evidence ID, and a prematurely opened writing gate were each rejected as expected. Exact outcomes are in `validation_checks.json`.
- Executed `audit_saved_archive.py` using only the standard library. All 9 manifest size/hash checks passed; 60,088 planned rows were streamed and Full Braw cached-score means recomputed. Source files, script hash, selectors, denominators and limitations are recorded in `analyses/archive_audit/summary.json`. No project model execution or full raw-response rescoring occurred.
- Final working-tree inspection showed additions in `.agents/`, `AGENTS.md`, and `paper/`, with no tracked source/config/result modifications. Pre-existing untracked drafts and the prior-paper PDF were preserved.

## Behavioral validation and limits

The initial two forward-test attempts stopped at the account usage limit. At the user's request, both bounded scenarios were subsequently completed by fresh independent agents using raw sources, without receiving prior audit conclusions. Initial output was isolated under `tmp/`; reviewed outputs are now retained in [validation/scenarios/](validation/scenarios/summary.json). **Both scoped scenarios passed**, including focused regression checks after the repairs below. This does not constitute a complete eight-skill manuscript-production run.

1. **Claim audit:** the agent audited the extraction and selection paragraphs, producing [22 atomic dispositions and 14 hashed evidence records](validation/scenarios/claims/audit.md). It identified the missing appendix, left historical Cypher extraction unverified, separated implemented design from historical coverage, and distinguished all-route witnesses from indispensable evidence. Its archive sample was explicitly bounded. Isolated ledger validation passed.
2. **Results planning:** the agent produced an [outline, figure dispositions and an exactly sourced numerical candidate](validation/scenarios/results/plan.md). It kept the writing gate closed, excluded mock performance, resolved the misleading Qwen-named folder using the Gemma manifest, and labelled its candidate as cached-score aggregation rather than raw-response rescoring. The primary agent independently recomputed the candidate and reran its portable derivation after relocation; both checks passed.

Two demonstrated instruction ambiguities were repaired: `academic-paper-writer` now defines the permission needed for an individual section, and `claim-verifier` explicitly supports bounded output destinations and `--notes` validation using a copy of the current workflow state. Each independent evaluator checked the revised instruction in the same scenario; see [claim regression](validation/scenarios/claims/regression.md) and [Results regression](validation/scenarios/results/regression.md). Both changed skills passed the bundled structural validator again; the production evidence ledger still passes.

The shared contract's earlier path-resolution clarification remains in place. The existing claim taxonomy is coarse for document-presence assertions; the audit explicitly distinguishes those from implementation/history rather than treating the label as proof. No taxonomy expansion was necessary for these scenarios.

The primary agent verified byte-level preservation of 93 original research/config/result/draft and production-note files against fingerprints taken for this test. The production writing gate and evidence/claim ledgers were not changed. Scripts made no model calls or research-module imports. The machine-readable [scenario summary](validation/scenarios/summary.json) records outcomes, skill/artifact hashes and check scope. Archived agent reports retain their original temporary commands as run history; the reproducible candidate can now be rerun with `python paper/research_notes/validation/scenarios/results/derive.py`, and isolated ledger validation with `python paper/research_notes/scripts/validate_research_artifacts.py --root . --notes paper/research_notes/validation/scenarios/claims/regression_validation`.

The system has structural validation and two completed independent behavioral scenarios. This does not certify every existing scientific claim, finish the literature review, or certify a manuscript for submission. The historical-scorer limitation and full-material analysis remain research work, not failed scenario checks.

## Template limitation

Official WWW requirements and official ACM template locations were verified. ACM returned a Cloudflare block; the CTAN download returned HTML rather than ZIP and was rejected/removed. No official bundle was cached and no manuscript/PDF was compiled. See `conference_requirements.md` and `paper/template/provenance.json`.

## Re-run commands

From the repository root, use an existing Python with PyYAML for the skill-creator validator:

```powershell
foreach ($skill in Get-ChildItem -LiteralPath '.agents/skills' -Directory) {
    & '.venv/Scripts/python.exe' -X utf8 'C:/Users/ekurm/.codex/skills/.system/skill-creator/scripts/quick_validate.py' $skill.FullName
    if ($LASTEXITCODE -ne 0) { throw "Skill validation failed: $($skill.Name)" }
}
& '.venv/Scripts/python.exe' -X utf8 paper/research_notes/scripts/validate_research_artifacts.py --root .
```

The bundled validator's absolute path is specific to this installation. Archive audit reproduction is `python paper/research_notes/scripts/audit_saved_archive.py --root .`; capture stdout to a new output file. If registered sources change, inspect the changes before refreshing ledger hashes.
