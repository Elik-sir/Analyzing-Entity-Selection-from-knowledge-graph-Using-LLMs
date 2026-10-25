# Scientific contribution relative to Tool Graph Complexity

Completed scoped comparison, 2026-10-25. Repository inspected on branch `article`, clean at entry, revision `3f4b7b9` (full revision in workflow state). Existing work: frozen-reference/pairing audit, final archived-results tables and figures, conditional uncertainty analysis. No new experiments or research-source edits. This note refines positioning; it does not certify publication novelty or submission readiness.

## Primary evidence and comparison scope

The supplied anonymous manuscript `sources/tool_graph_complexity.pdf` is the primary source: title page; Introduction/Section 1.1, PDF pp. 1–4; Sections 5.1–5.3, pp. 7–8; limitations and reproducibility, pp. 9–10; Appendix O and Tables 32–33, pp. 30–31. Its header says under review at ICLR 2027. Bibliographic identity and acceptance are not established. Exact-title web search on 2026-10-25 did not locate a verified primary landing page; snippets were not used as scientific evidence. The source is archived and hashed in the evidence register.

Our evidence is the saved-input audit in `reference_pairing_report.md`, result selectors and metric definitions in `final_results_report.md` and its linked CSVs, and historical limitations in `experiment_audit.md`. Current implementation locators remain in `implementation_audit.md`; no historical pipeline is inferred from current defaults.

## Task, data and protocol comparison

| Dimension | Tool Graph Complexity, Appendix O | Present study | Implication for contribution |
|---|---|---|---|
| Scientific purpose | Test transfer of tool-graph motif/size effects and motif rankings to an explicit KG substrate | Diagnose selection under evidence availability, rendering, fact placement and distractor conditions | Different emphasis; KG selection itself already overlaps directly |
| Substrate | Finance KG: companies, news, executives, funds, products, locations, industries; reports 5,652 entities and 6,686 typed edges | Corporate KG snapshot reused unchanged from the prior Kirpichev study by author confirmation | No new KG construction or new-domain claim; Appendix O snapshot identity is not proven |
| Tasks and reference | Cover query anchored at a motif node; requested answer includes entity and relation sets; reference entities described as necessary by construction | Selected entity set evaluated against all-route witnesses including anchor; audited saved motif/reference equality | Cover-query necessity is not equivalent to necessity for an endpoint answer, minimal graph support or indispensable cards |
| Candidate pool | 25 names; seven shared motif classes, no clique/cycle in its DAG | Main frozen pool has 25 candidates and the same seven motif families | Fixed pool and motif taxonomy are shared design, not new contributions |
| Sampling and filtering | Exact-induced motifs; type-singleton, context-answer consistency, name-in-question and redistribution filters; reports 2,156 accepted baseline items, 2,154 paired adjacent items | Core has 700 bases; Full Braw has 3,400 bases per model; actual frozen invariants checked separately | Counts refer to different documented populations; do not call their difference additional independent data |
| Evidence access | Candidate facts and relations visible in both disconnected and adjacent conditions | Raw descriptions versus same inputs with a relation overlay; controlled triples, templated text and other archived variants | KG evidence-availability intervention and matched-fact rendering/placement are the strongest additional experimental scope |
| Distractors | Up to ten neighbours attached by excluded directions/depths; displayed edges require rejection | Paired disconnected/adjacent contrasts for both triples and templated text | Adjacent noise is replication/context extension, not a new phenomenon |
| Models | Claude Haiku 4.5, Gemma-4-31B-IT, Qwen3.6-Flash, Ministral-14B | Main result package covers Gemma, Qwen and Ministral labels in archive manifests | Three overlapping model families do not establish version identity or new breadth; no Claude result is inferred here |
| Output and metrics | Selection then answering on selected context; success means all reference entities selected, exact means equality | Failure-inclusive mean per-task precision/recall/F1/exact; selected-set analysis separated from final QA | Success is a recall-completeness event, not F1, exact match or correct QA |
| Uncertainty | Tables 32–33 report percentile bootstrap; reproducibility section specifies record resampling | Paired anchor bootstrap, fixed motif-size weights, task sensitivity and simultaneous F1/exact family | Reporting/analysis addition; shared-entity dependence still prevents unrestricted population inference |

Appendix O literature counts above are reported by that PDF, not independently audited or adopted as repository measurements. Our population counts are planned tasks, not successful requests. They are not directly exchangeable denominators. The PDF's statement that every row is committed is a source assertion, not our verification of its external archive.

## What results already overlap

Appendix O reports a reversal of chain difficulty relative to tool graphs, difficult incoming trees, and sensitivity to adjacent decoys. Table 32 explicitly separates complete reference recovery from exact selection: Claude's adjacent tree-in row has success 0.92 and exact 0.21 (100 items at that comparison cell). That is already evidence of inclusion errors despite high coverage. Table 33 studies size within chain, star-out and tree-in; a blanket claim that this article introduces KG size/motif or distractor analysis would be incorrect.

Its interpretation already connects easy KG chains to explicitly available relations. Our Raw/Raw+E pairs therefore provide a within-KG evidence intervention supporting a more specific diagnostic contrast, rather than introducing the explicit-relations explanation. Adding relations changes the information supplied; it cannot isolate an improvement in reasoning on equally informative inputs. The text's claims that tree-in is always hardest and chains always easiest should be read as its summary: Table 32 contains ceiling ties, and Claude's explicit tree-out success exceeds its chain success. We use the bounded pattern, not an unconditional ranking theorem.

Our existing results show large positive Raw-to-overlay F1 differences in each archived model, adjacent-distractor penalties under both controlled renderings, and model-dependent rendering/placement effects. Exact numerical values, all planned denominators, paired selectors and uncertainty limits are already registered in `final_results_report.md` and claims `C-final-raw-f1`, `C-final-noise-f1`, `C-final-representation-f1` and `C-final-placement-f1`; they are not re-estimated here. In particular, the evidence supports neither universal text inferiority nor uniform gains from duplicating facts. No cross-paper score subtraction, leaderboard, or claim of contradicting Appendix O is warranted: tasks, references, metrics, populations and failure policies are not harmonized.

## Defensible contribution and result hierarchy

**Central contribution:** a focused empirical diagnosis of how the availability and presentation of relational evidence affect fixed-pool KG entity route coverage, with audited matched inputs and transparent archived-evidence limitations.

1. **Evidence availability on the same KG tasks (primary).** Compare native cards and their explicit relation overlay while holding frozen questions, candidate identities and references fixed. Claim basis: `C-raw-overlay-pairing`, `C-final-raw-f1`. This adds a within-substrate contrast to Appendix O's explicit-KG transfer experiment. Do not label native cards sufficient unless independently checked.
2. **Presentation conditional on controlled facts (primary).** Compare triples and templated prose, query variants, and relation placement using the audited pairs. Claim basis: `C-core-pairing` and the existing representation/placement result records. These contrasts separate fact presentation from the information addition in Raw+E. The empirical contribution is their bounded model-dependent outcome, not invention of graph serialization.
3. **Reference-aware diagnostic evidence (supporting).** Report both incomplete and excessive selection, failures in planned denominators, partial versus exact recovery, conditional uncertainty and evidence tiers. Reference/witness consistency is audited; minimality and QA are excluded. This makes the interpretation inspectable, but set metrics, provenance and bootstrapping are not themselves new scientific methods.

Adjacent distractors and motif/size slices are contextual robustness results with explicit acknowledgement of Appendix O. Naming, aliases and incremental access belong in supplementary diagnostics: no mechanism, independent-domain transfer or equal-budget search claim is supported. Existing corporate KG construction belongs to its source paper. The archived collection must not be advertised as a newly released independent benchmark without establishing provenance and release conditions.

### Proposed academic-English positioning (outline wording, not a full manuscript)

Tool Graph Complexity already evaluates entity selection on a finance knowledge graph in Appendix O, including explicit relations, motif and size variation, and adjacent distractors. We focus on a complementary question: how relational evidence is made available and presented within frozen KG selection tasks. We compare native entity cards with a relation overlay, then examine controlled renderings and fact placement on audited matched inputs. Our findings distinguish changes in available information from changes in its presentation and characterize model-dependent recovery of an all-route entity reference. The evaluation measures selection coverage rather than minimal evidence or downstream answer correctness.

Suggested contribution bullets for the outline:

- A paired diagnosis of graph-reference recovery when explicit relations are added to native entity cards on otherwise matched KG tasks.
- An empirical comparison of controlled fact rendering and placement, showing where their effects depend on the evaluated model and condition.
- An auditable analysis of partial and exact entity recovery with explicit failure, provenance and dependence limits, contextualized against existing KG motif and distractor results.

## Reuse, limits and decision

**Resolved by narrowing:** no first KG selection study, new motif method, discovery of adjacent-noise effects, new corporate KG, universal encoding superiority, minimal-evidence benchmark or QA improvement claim. These assertions are excluded from the proposed contribution.

**Still unresolved:** whether Appendix O shares this snapshot, sampled queries, input payloads, raw model replies or result rows. Domain, motifs and three model labels are strong reasons to check, but cannot prove overlap or independence. Author confirmation of reuse of the Kirpichev snapshot does not answer reuse relative to Appendix O. Without Appendix O task/run artifacts, no row-level overlap audit was performed. Any manuscript must disclose known reuse; until established, avoid “independent replication”, “new dataset” and counting shared rows as fresh evidence. A bounded follow-up would compare graph fingerprints, canonical task/candidate/reference hashes and response/run IDs, preserving permissions and without calling models. This is mandatory for an independence/resource-novelty assertion, not for the narrow contrast descriptions above.

The contribution-clarification item is complete at this scoped level: the overlap, additional comparisons, allowable wording and residual provenance question are recorded. Full writing remains gated by planned manuscript claim coverage and historical/provenance dispositions; this task does not silently mark the whole literature survey or all analysis complete. No experiment or external release is authorized by this decision.
