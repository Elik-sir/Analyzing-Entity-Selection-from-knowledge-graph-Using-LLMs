# Reference validity and paired-input audit

Completed 2026-10-25 on revision `261f1b3cc3d3bf3419c04d3d0a35d290fce73cae`. Scope: the existing historical archive and its saved input/reference payloads. No research source, original configuration, saved result or manuscript was edited; no model/API/judge call or graph export was made.

## Decision for the paper

The saved main panels support the declared **all-route entity coverage** convention. No mismatched reference, endpoint answer, unintended factual-graph change or missing pair was found in the tested main contrasts. Raw/Raw+E is a paired addition of explicit relations in this archive. The main reference/pairing questions G03–G04 are resolved for the audited archive, subject to the evidence limits below.

Do not describe the target as the smallest set of indispensable cards. Keep endpoint answer A, saved motif/reference M, and all-route witnesses W conceptually distinct. Their checked equality where applicable is a property of these accepted archived tasks, not a general theorem about motifs or candidate expansion.

## Fresh archive and protocol verification

`analyses/reference_pairing_audit/archive_verification.json` records a fresh execution of `scripts/verify_article_results.py`, not a reuse of `results/VALIDATION.json`. It verified 60,088 planned observations, 41,193 input payloads and 52,197 response payloads, links/checksums and 45,904 individual score calculations from saved selections/reference sets. That count does not mean every response was reparsed from raw text.

`protocol_verification.json` additionally records fresh offline prompt reconstruction and raw-response parsing for the verifier's selected logical-task population: all 9,100 reconstructed Core prompts match recorded requests, and 23,127 archived valid selections/scores match. No network requests were made. This is not a rerun of the models or a verification of unavailable historical transcripts.

## Independent reference audit

The final machine-readable result is [analyses/reference_pairing_audit/final/summary.json](analyses/reference_pairing_audit/final/summary.json). Source files and the analysis script are bound by SHA-256. A separate traversal implementation enumerates simple directed routes, observes incoming/outgoing direction, the first terminal type for chains, the early-dead-end convention for bounded routes, and both neighbor groups for hourglasses. It does not call the project's oracle. The finite grammar used to decode controlled text is read as data from the current source and matched strictly against saved public statements.

- All 35,888 unique primary input payloads linked by the observation archive were checked for unique candidate/reference names and reference membership in the candidate pool. Other input payloads are stage/auxiliary records, not additional primary tasks.
- For 27,200 structured primary payloads in Core, Size and Full Braw, saved reference IDs, witness IDs, mapped gold names, query templates and candidate-ID order agree. Incremental observations share their frozen task payloads with a subset of Core; they are not counted again as independent task definitions.
- For 21,000 payloads with controlled or overlay evidence, independently decoded visible relations reproduce the saved endpoint answer and witness set exactly. This includes triples, templated text and linking keys. Every checked relation is on the host card required by its placement condition. Duplicate presentation in K4 does not become a new graph edge.
- Full Braw's core subset omits TaskSpec in some payloads. For those 1,400 inputs, the audit joins an actually saved specification by record ID, verifies exact reference-ID and rendered-question equality, and only then traverses it. It does not fill missing history with current defaults.
- All 6,800 Full Braw input variants also have their reference-only edges checked against the saved/joined query. Raw has no `facts.relations` overlay in any of its 3,400 primary inputs; this does not prove its prose is semantically insufficient.
- All 400 calibration inputs reproduce their one-hop reference answers from visible evidence. All 2,000 distinct legacy primary contexts reproduce legacy reference reachability under the legacy pattern, separately from the controlled endpoint convention.

The final issue log is empty. Ten hand-constructed oracle/decoder correctness fixtures also passed; they are software checks and are excluded from scientific results.

## Main paired contrasts

Pairing starts from `(series_id, model, condition, noise, base_id)`. Within each tested main condition, base IDs are unique, allowing the intended contrast to match base IDs while deliberately changing its condition/noise dimension. Generic deduplication by base ID alone is unsafe for Native D and legacy because noise strata repeat it.

- **Core:** all twelve tested contrasts have 700 complete pairs per model, with no unmatched base IDs. These cover K1/K5, K7/K8, K5/K5k, K1/K7, K5/K8, K1/K3, K1/K4, R1-matched/K1, R2-matched/K2, R0/K0, K1/K2 and K5/K6. Candidate pools/order, mapped references, endpoint answers, types, nonlink metadata and fact sets match where required. Question variants change question wording while keeping cards identical. Noise variants preserve the question, reference/endpoint sets and reference-induced edges while deliberately changing distractors/context. Disconnected inputs have no reference-to-distractor boundary edge; adjacent inputs satisfy the maximum-neighbor constraint in the tested visible graph.
- **Raw/Raw+E:** 3,400 complete pairs per model; system messages, questions, ordered candidate identities, reference/specification and residual metadata match. After removing only `facts.relations`, the actual public JSON objects are equal. The archived contrast therefore differs from current builder behavior that may insert an overlay instruction/note; use archive evidence to describe this experiment.
- **Additional sizes:** K1/K5 has 1,100 complete pairs for Gemma with the intended representation change and otherwise matched query/reference/pool.
- **Incremental:** K7/K7-inc and K8/K8-inc each match 350 Gemma base tasks. Compare static results only on those subsets, not all 700 static tasks. Shared frozen task payloads establish starting task identity; they do not establish complete historical solver-visible menus, card-reveal sequences, turn histories or equal token budgets.

Recorded Core inputs are shared between Qwen/Ministral. Gemma uses a separately frozen representation. The 1,400 raw JSON differences across models are exactly the closed-book R0/K0 representation category: frozen sources retain empty facts/labels and a format note, while the transmitted builder keeps names/types only. Effective closed-book content agrees, and the separate protocol verifier confirms all 9,100 reconstructed messages exactly. That is reconstruction evidence, not authenticated Gemma call metadata.

## Supplemental Native D and legacy pairing

See [analyses/reference_pairing_audit/supplement.json](analyses/reference_pairing_audit/supplement.json).

- D200/D200+E has 2,096 complete `(noise, base_id)` pairs. The question, candidates/order, reference, types, system instruction and raw metadata match; removing the appended explicit-link block restores the original user text exactly.
- In all 2,096 D200+E inputs, independently traversing the **separately saved typed/relation-constrained semantic goals** over the displayed overlay recovers exactly the reference names, with no unresolved goal. This does not certify semantic sufficiency of the descriptions in D200/Dfull.
- D200/Dfull has 2,096 complete pairs with the same question/reference/pool/system. Each short metadata string is an exact prefix of the corresponding full string. The correct test uses each short string's actual length: a fixed 200-character hash comparison produced diagnostic differences for shorter strings and is not evidence of a confound.
- Legacy disconnected/adjacent variants pair completely for Gemma (1,000 bases) and Qwen (400 bases), preserving query, reference, pattern, anchor and system instruction. Their model populations are different sizes; use matched overlapping bases for a cross-model comparison.

## Concrete example of the target distinction

[support_example.json](analyses/reference_pairing_audit/support_example.json) identifies an actual archived K1 rhombus by input/observation ID. Two routes lead from Rezamamu through Lalesemu/Rukomida to Raragamu. The endpoint answer is Raragamu, while the scored witness set contains all four entities. Removing Raragamu's own card facts leaves the endpoint answer recoverable from incoming statements. Thus reference membership does not establish that every reference card supplies indispensable information. This is one deterministic artifact inspection, not a population-wide necessity estimate.

## Suggested method statements, pending manuscript integration

- The selection target contains the named anchor and the union of entities occurring on all query-consistent supporting routes, including parallel routes. It measures route coverage rather than a minimum sufficient evidence-card set.
- In the audited controlled archive, saved motif/reference IDs coincide with the graph-derived witness set under the accepted query/candidate context. This equality was checked on the frozen inputs rather than assumed from topology alone.
- The archived Raw/Raw+E comparison adds explicit relations to otherwise identical public inputs. Its differences should be interpreted as evidence availability, not purely a change in serialization of an already identical fact set.

These statements are evidence-backed integration recommendations; the existing approved-labelled manuscript sections have not been overwritten.

## Remaining limits

No full source graph was loaded, so the audit does not independently establish completeness of all induced edges against the original database. It validates consistency of the frozen experiment as presented. Semantic answerability of native descriptions remains a separate review question. Closed-book conditions intentionally lack visible edges. Missing raw Gemma responses, incomplete incremental histories, historical metadata, uncertainty analysis and the final literature/contribution comparison remain limitations or subsequent work. None is silently resolved by a passing reference audit.

## Reproduction

From the repository root, using an existing Python environment:

```powershell
& '.venv/Scripts/python.exe' -B -X utf8 scripts/verify_article_results.py
& '.venv/Scripts/python.exe' -B -X utf8 scripts/verify_model_protocols.py
& '.venv/Scripts/python.exe' -B -X utf8 paper/research_notes/analyses/reference_pairing_audit/audit_references.py --root . --output paper/research_notes/analyses/reference_pairing_audit/recheck
& '.venv/Scripts/python.exe' -B -X utf8 paper/research_notes/analyses/reference_pairing_audit/audit_supplement.py
& '.venv/Scripts/python.exe' -B -X utf8 paper/research_notes/analyses/reference_pairing_audit/check_oracle.py --root .
```

Use a new destination for the main audit. `run-01`/`run-02` are exploratory outputs superseded by `final/`; do not use their intermediate coverage classifications for paper claims. The supplement/helper checks write deterministic derived outputs only.
