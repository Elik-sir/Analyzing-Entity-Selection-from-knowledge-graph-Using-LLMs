# Selected paper structure and principal claims

Decision date: 2026-10-25. Scope: an evidence-backed outline and selection of main-text assets, authorized by the user's request to settle structure and principal claims. This is a working editorial decision, not an assertion of independent review, author approval of finished prose, venue compliance or submission readiness. Existing `docs/ARTICLE*` drafts are preserved. No full manuscript is written here.

## Narrative and scope

**Working title:** Relational Evidence in Fixed-Pool Knowledge-Graph Entity Selection.

**Central message:** On the archived KG tasks, adding explicit relations to native entity cards substantially increases recovery of the graph reference. Once facts are controlled, rendering and placement effects depend on the evaluated model; adjacent distractors remain a challenge. This is a diagnosis of evidence availability and presentation, not a new retrieval algorithm or a demonstration of improved QA.

The primary task is entity route coverage from a fixed candidate pool. Introduce the query, anchor, candidate catalogue, endpoint answer, and all-route entity reference separately. State on first use that the selection target includes the anchor and entities on all supporting routes. It is not a minimum sufficient card set. Describe graph-construction reuse in third person and cite the source study. Do not infer the historical sampling pipeline from current Python builders.

## Research questions selected for the main text

| RQ | Manuscript wording | Status and contrasts | Evidence / main assets |
|---|---|---|---|
| RQ1 | How does adding explicit relational evidence to native entity cards change entity route coverage on matched KG tasks? | Primary; Full Braw `Braw` → `Braw+E`, shown as Raw → Raw+E; 3,400 paired bases per model | `C-raw-overlay-pairing`, `C-final-raw-f1`; Table 2 |
| RQ2 | When the underlying relational facts are controlled, how do their rendering and placement affect entity selection? | Primary; K1→K5 and K7→K8 for triples→templated prose under two question formulations; K1→K3 and K1→K4 for source→destination/both-card placement; 700 pairs per contrast/model | `C-core-pairing`, `C-final-representation-f1`, `C-final-placement-f1`; Figure 2 |
| RQ3 | How does adjacent distractor context affect selection under explicit and templated relational evidence? | Contextual robustness question; K1→K2 and K5→K6; 700 pairs per contrast/model | `C-core-pairing`, `C-final-noise-f1`; Figure 2 |

RQ2 does not isolate a reasoning mechanism: rendering changes surface form and duplication changes presented length/redundancy. RQ3 changes distractor identities/composition and context density, so it is not a pure-topology causal effect. RQ3 already overlaps Appendix O and is not advertised as an original contribution. Question formulation is a check within RQ2, not a fourth main RQ. Motif/size, lexical naming and incremental access are supplementary analyses, not additional headline RQs.

## Structure and space budget

Planning target from the recorded venue requirements: eight self-contained main-text pages; the budget includes abstract, figures, tables and captions. It is not a compiled page-count guarantee. References and appendix must also fit the recorded total limit; cut optional material before reducing explanatory caveats or changing typography.

| Section | Page budget | Required content and claim anchors |
|---|---:|---|
| Abstract and 1. Introduction | 0.85 | Concrete linked-knowledge access scenario; selection versus answer; scope of contribution; RQ1–RQ3. Abstract is written last. Headline evidence: `C-final-raw-f1`; avoid new-KG/new-method/independent-benchmark claims. |
| 2. Related Work and Positioning | 0.65 | Explicit direct comparison to Tool Graph Complexity Appendix O; graph serialization and graph-pattern work already verified. `C-toolgraph-kg-overlap`; distinguish our within-KG interventions, not KG selection itself. |
| 3. Task and Evidence Conditions | 1.15 | Candidate pool, endpoint A, all-route W, selection S; meanings of partial/exact recovery; archived example and Figure 1; Raw/overlay versus matched-fact interventions. `C-frozen-reference-consistency`, `C-raw-overlay-pairing`, `C-core-pairing`, `C-outline-target-example`. |
| 4. Experimental Material and Evaluation | 1.05 | Frozen populations and Table 1; three archived model labels; graph reuse; evidence tiers; parsing/failure policy; primary F1, secondary exact; pairing and conditional uncertainty. Do not authenticate unavailable provider/version metadata by assertion. |
| 5. Results | 2.75 | 5.1 RQ1 (about 1 page, Table 2); 5.2 RQ2 (about 1.1 pages, Figure 2 rendering/placement rows); 5.3 RQ3 (about 0.65 page, same figure noise rows). Descriptive differences across panels are not an interaction test. |
| 6. Discussion and Limitations | 1.20 | Evidence availability versus presentation; comparison with Appendix O; reference coverage versus sufficiency/QA; one-KG scope, incomplete raw evidence/history, shared entities and conditional uncertainty, unresolved cross-paper reuse. `C-final-dependence-scope`; pending `C-toolgraph-independent-populations` must be framed as unknown. |
| 7. Conclusion | 0.35 | Answer RQ1–RQ3 within measured scope. No new results, claims of practical QA gains or universal representation preference. |
| **Total** | **8.00** | Two tables and two figures are allocated inside these sections. |

## Principal statements permitted in the main text

These are claim-level wording decisions; they are not a completed Results section. Values below use score units except where explicitly marked percentage points. Source selectors and hashes are in `outline_claim_map.json` and `analyses/main_text_selection/run-01/asset_plan.json`.

1. **H1 — explicit relation availability:** “Adding explicit relations to otherwise matched native entity cards increased archived mean graph-reference F1 for each evaluated model.” Deltas: Gemma +0.674, Qwen +0.466, Ministral +0.572 (rounded to three decimals). The exploratory simultaneous bands are positive under the fixed-KG/anchor-independence assumptions. `C-final-raw-f1`. Do not describe Raw as an equally informative reasoning test or this as a QA gain.
2. **H2 — controlled rendering:** “The controlled text-versus-triples contrast did not support a uniform representation preference across the evaluated models.” Qwen's text-minus-triples F1 differences are about −0.023 in both question variants; its simultaneous bands are below zero. Gemma/Ministral bands include zero. `C-final-representation-f1`. Inclusion of zero establishes neither equivalence nor absence of an effect; do not claim a statistically tested between-model interaction.
3. **H3 — fact placement:** “The archived placement contrasts support model-dependent presentation sensitivity rather than a general benefit from duplicating facts.” Qwen both-minus-source F1 is +0.041, with simultaneous band [0.024, 0.059]; all other source/destination/both rows remain visible in Figure 2. `C-final-placement-f1`. Do not select only the favorable duplication row or attribute the result to a mechanism.
4. **H4 — adjacent context:** “Adjacent distractor contexts had lower F1 in all evaluated model/rendering pairs.” All six simultaneous bands lie below zero under the stated assumptions. `C-final-noise-f1`. Treat this as contextual evidence consistent with Appendix O; do not claim discovery of distractor sensitivity or arbitrary-graph causality.
5. **H5 — interpretation boundary:** “The reference measures all-route entity coverage; it does not establish indispensable visible cards or final-answer correctness.” Figure 1 supplies one archived example; `C-frozen-reference-consistency`, `C-outline-target-example`. No population-wide necessity rate is claimed.

The abstract may report H1's three F1 deltas and summarize H2/H4 qualitatively after body validation. H3 is an important result within RQ2, not a separate novelty bullet. H5 must appear in the task definition, not only in limitations. Do not write “all models”, “text fails”, “relations solve reasoning”, “optimal retrieval” or “significant on arbitrary KGs”.

## Main-text tables and figures: fixed selection

### Table 1 — Experimental conditions and matched contrasts

Location: Section 4. Compact design matrix, ten rows: Raw, Raw+E, K1–K8. Reader-facing names first, archive IDs in parentheses. Columns: panel/condition; evidence; distractor regime; placement/question variant; paired contrast(s); planned bases per model. Group the eight Core rows visually; show planned N=700 once per block where layout permits. Raw block N=3,400. These are per-condition/model denominators, not disjoint datasets to sum across conditions. Do not sum Core and Full Braw bases as independent tasks or present all 60,088 archived rows as the main-text population.

Include a short paragraph defining which invariants are held in each comparison; the matrix is not evidence by itself. Population support: `C-core-pairing`, `C-raw-overlay-pairing` and their frozen-input audit. Current registry may explain terminology but cannot prove historical execution. A concrete table preview is in `analyses/main_text_selection/run-01/main_text_tables.md`.

### Table 2 — Native cards versus explicit relation overlays

Location: Section 5.1. Two compact panels, each with three model rows. Panel A: Raw F1, Raw+E F1, paired ΔF1, simultaneous band for ΔF1. Panel B: Raw exact, Raw+E exact, valid Raw/N, valid Raw+E/N. Each condition has N=3,400; the primary scores include every planned outcome with invalid/missing outcomes contributing zero. Valid-only means are not the main table.

Three decimals for scores/deltas and band endpoints; valid counts are integers. Do not bold a cross-model winner. Label model names as archived identifiers, with provider/version limitations in setup. Source: `condition_metrics.csv` selected by `series_id=full_braw`, model, condition Braw/Braw+E and `noise=disconnected`; paired bands from `paired_contrasts.csv`, `panel=raw, contrast=raw_explicit, metric=f1`. `C-final-raw-f1`, `C-main-raw-exact-validity`. The preview contains all intended cells; no new inference is calculated.

Caption requirements: planned N and failure policy; Δ is Raw+E minus Raw; bands are exploratory simultaneous bands from the full declared 78-effect F1/exact family under conditional fixed-KG assumptions. Do not label the bands ordinary per-cell 95% intervals.

### Figure 1 — What entity route coverage selects

Location: Section 3; compact one-column schematic. **Selected for main text; rendering remains a later manuscript task.** Use the actual audited rhombus from `support_example.json`, not an invented experiment or a model-output screenshot. Show anchor Rezamamu, branches Lalesemu/Rukomida, endpoint Raragamu and the four recorded directed relation edges. Highlight endpoint answer A separately from the four-member all-route reference W. Mark the 25-name catalogue as context and the drawing as a reference-subgraph excerpt, not the complete pool. Explain that incoming facts can identify the endpoint without making its own card facts indispensable. `C-outline-target-example`, `E-support-example`.

This figure must communicate the target distinction and paired-evidence idea; it is not a performance plot. No fabricated card text or reconstructed response is allowed. Final caption will state “one archived example” and the full asset provenance will keep input and observation IDs. Do not call it a representative or typical case statistically.

### Figure 2 — Controlled rendering, placement and distractor contrasts

Location: Sections 5.2–5.3; full-width. **Ready existing asset:** `paper/figures/final_results/controlled_contrasts.svg` (PNG preview also exists). Three model panels, all six existing contrast rows retained: format_slots, format_goal, noise_triples, noise_text, placement_object, placement_both. These provide both question variants, both noise renderings and both placement alternatives; no cherry-picked rerender is needed.

Primary metric: change in mean set-F1, shown in percentage points (CSV delta ×100). Grey bands: simultaneous main-family bands; blue point/line: estimate and pointwise interval. Caption must identify both, N=700 planned pairs per model/contrast, right-minus-left direction, all-planned failure policy and conditional uncertainty. The family remains 78 F1/exact effects even though only these six F1 contrasts per model appear. Existing source rows/hashes are in `figure_sources.json`; numeric selection is reproduced in `asset_plan.json`. `C-final-representation-f1`, `C-final-placement-f1`, `C-final-noise-f1`.

## Appendix and artifact-only material

The appendix competes with references within the recorded total-page limit. Use compact combined tables; the complete CSV archive remains the authoritative detailed supplement. Do not promise that every diagnostic plot will fit.

| Material | Decision | Reason |
|---|---|---|
| All twelve Core contrasts, F1 and exact; condition absolute scores and invalid counts | Appendix priority A1; complete CSV remains available | Main Figure 2 is an editorial subset, not a redefined multiplicity family; show small/null and unselected results too |
| Analytical select-all, anchor-only and random-six baselines | Brief main-text context paragraph; full numeric table priority A2 | Prevent interpreting hidden-target recovery as grounded QA; they are analytical reference points, not executed retrievers |
| Both-valid diagnostics, task-bootstrap sensitivity, dependence detail, family construction | Priority A2 methods/results supplement | Main text must still state the assumptions and missing-evidence limits; appendix supplies exact detail |
| `motif_noise_f1.svg` | Appendix priority A3 | Descriptive motif/query-semantic strata; overlaps Appendix O and is not a primary RQ |
| `gemma_size_diagnostics.svg` | Artifact supplement; appendix only if space remains | Gemma-only coverage cannot establish an across-model size law |
| `raw_explicit_relations.svg` | Artifact supplement, not main and not mandatory appendix | Duplicates Table 2; the numerical table also makes exact match and validity visible |
| Naming/aliases, keys, question-formulation effects beyond the two rendering checks | Compact appendix/CSV, no main RQ | Secondary to the refined contribution; retain surface/tokenization caveats |
| Incremental access | Artifact supplement; short limitations mention | Missing complete turn histories/budgets prevents a clean mechanism or equal-budget claim |
| Native D and legacy panels | Artifact supplement | Distinct references/scoring/populations; do not pool with the main panels |
| Historical Cypher queries | Appendix if supplied and verified; otherwise narrow extraction wording | Do not invent the appendix or describe current builders as historical evidence |

Main baseline paragraph uses `C-final-analytical-baselines` and must label select-all's nonzero F1 as a metric reference point rather than successful evidence-grounded selection. No claim about matching state-of-the-art GraphRAG retrieval is included.

## Decisions and handoff

Structure/RQ/main-claim/asset selection is complete for this outline. `outline_claim_map.json` supplies supported claim IDs, evidence IDs and source hashes for the planned sections/assets; it is a pre-writing map, not full prose/caption/cell certification. The next manuscript step is a bounded writing-gate decision using these exact scopes, verified citation handling and explicit historical/provenance wording. Do not reopen completed saved-data analyses without a concrete discrepancy.

The full-writing gate remains unchanged in this outline-only task. Cross-paper reuse relative to Appendix O is unknown; exclude independent benchmark/replication and resource-novelty assertions and keep an explicit limitation. Anonymous citation metadata and historical extraction/settings need final treatment. Figure 1 is a specification, not a completed image; Figure 2 exists, while final two-column legibility and page compliance require LaTeX build/visual review. No independent review, new model run, API call or release is asserted.
