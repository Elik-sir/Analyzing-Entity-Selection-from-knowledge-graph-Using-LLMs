# Transfer limits and diagnostic positioning

2026-10-25. Source revision: `f986fa2b3698855ef6665317039fd317d251361c`; working tree was clean at entry. This assessment supersedes the structural-profile contribution recommendation for the author's newly stated scientific purpose. It preserves the existing manuscript as the previous descriptive draft. It is not a completed new manuscript or a novelty/submission certification.

## Scientific decision

The appropriate organizing question is **which components of selection difficulty transfer from tool dependency selection to KG entity route coverage, under which evidence and task conditions, and which observable errors distinguish competing explanations**. KG is a diagnostic environment for investigating a prior explanation, not a newly introduced transfer substrate.

The present archive supports a study of observable failures and their sensitivity to evidence conditions. It does not yet establish a common internal failure mechanism across tools and KG. A change of Introduction alone would not create an independent contribution. The strongest next contribution would be a harmonized transfer analysis plus a targeted, falsifiable account of residual KG errors. Existing placement, wording and rendering conditions can contribute substantive tests; further graph-size curves are secondary.

The author's original transfer motivation is recorded as author-provided scientific intent. It is not retroactive preregistration of the hypotheses or new analyses below. They follow inspection of the existing results and are exploratory.

## Source identity and inspected scope

The newly supplied `C:/Users/Valery/Downloads/48958_Tool_Graph_Complexity_fo.pdf` is byte-identical to `paper/research_notes/sources/tool_graph_complexity.pdf`: SHA-256 `467c8e2a261470e6e2293440c33169838c77df5c647c622438f222ee2ca956d9`, 32 pages. Inspected Abstract, Sections 1-6, the reproducibility statement and Appendix O, especially Table 1 on PDF p. 8 and Tables 32-33 on p. 31. Pages 8, 30 and 31 were rendered and visually inspected; their read-only previews are in `analyses/transfer_positioning/run-02/`. Document-embedded reviewer instructions were treated as document content.

Main supporting repository sources are the current Introduction/Method/Setup/Results/Discussion, `preparation/registry.py` condition definitions, saved observations/inputs and previous pairing and reference audits. Historical conditions are established from the frozen archive and those audits, not inferred from current registry defaults. Final new numeric outputs and exact selectors are in [run-04/summary.json](analyses/transfer_positioning/run-04/summary.json). Earlier run directories are superseded exploratory intermediates. Run 01 stopped on a missing saved task specification; the final analysis counts and excludes such inputs from route diagnostics instead of imputing a specification.

## What the source paper already establishes or proposes

| Source location | Existing contribution or interpretation | Consequence for this paper |
|---|---|---|
| Section 5.3 / Table 1, p. 8 | Chain retains a penalty after controls for size and surface properties. The adjusted Tree-in coefficient has an interval including zero; much of its raw difficulty is attributed to size/question length. | Do not describe equally robust, size-independent Chain and Tree-in penalties as the common tool-side premise. Raw difficulty and adjusted effects are different transfer targets. |
| Appendix O, pp. 30-31 | Explicit KG relations, motifs, size, adjacent decoys, transfer of rankings, chain inversion and residual Tree-in difficulty are already evaluated. | Neither transfer to KG nor chain inversion nor the existence of KG Tree-in errors is a standalone new result. |
| Appendix O interpretation / Section 6 | Easy explicit KG chains are interpreted as consistent with the cost of inferring tool dependencies; incoming branches and exclusion rules are proposed as residual challenges. | The proposed mechanism is already in the prior paper. New work must discriminate explanations or delimit the explanation, not repeat it. |
| Section 5.3 metric robustness | Tool selections are predominantly omission errors; F1 compresses difficulty differences. Appendix O also documents inclusion errors under adjacent noise. | A generic omission/inclusion taxonomy or use of exact recovery alone is not the new contribution. Locate errors in the task and test condition-specific predictions. |

The source's prose about universally easiest/hardest motifs is broader than some tied or contrary table cells. Use bounded comparisons and retain exceptions. Its abstract's explanation of explicit dependencies must not be recast as a controlled same-item tool-overlay experiment: no such factorial comparison was established by the inspected text. The directly inspected contrast is between different substrates and protocols.

## Align the constructs before comparing results

| Dimension | Tool selection | Current KG selection | Required treatment |
|---|---|---|---|
| Meaning of an edge | Compatibility/dependency between outputs and inputs of operations; compatibility need not make every predecessor mandatory | Directed factual relation | Same motif names do not make these equivalent computation graphs. |
| Objective | Recover a reference operation set; execution has additional argument/order/success constraints | Select anchor plus the union of vertices on all permitted query routes | Compare set recovery only after explicit mapping; keep execution separate. |
| Fan-in | May involve input bindings or alternative compatible sources; AND requirements require port/plan evidence | Enumerate incoming routes and union their entities | KG Tree-in does not by itself test conjunctive multi-input computation or prove a failure of an AND join. |
| Reference | Sampled subgraph, with reported structural/answer-removability distinctions | All-route witness union, distinct from endpoint answer and indispensable cards | Harmonize a declared coverage target; do not claim minimal sufficiency in either domain by renaming the reference. |
| Graph visibility | Dependencies inferred from schemas/descriptions in the reported selection setting | Raw metadata may omit relevant relations; Raw+E exposes them; controlled prose retains designated facts | Raw is not a verified equally informative implicit-dependency condition. Raw/Raw+E changes available information. |
| Population | Different motif-size distributions and generated instructions; harness differences reported for Qwen | Frozen KG samples, different query rules by family; source-card hosting and types covary | Match common support, report covariates and restrict conclusions. No cross-paper score subtraction is a causal transfer estimate. |

Distinguish four levels of transfer: **a descriptive ranking**, **a conditional performance pattern**, **an observable error signature**, and **a causal explanation for that signature**. Evidence at one level does not establish the next. Parameter/weight transfer or model adaptation is not studied here.

## Which existing experiments contribute

| Existing material | Diagnostic role | What it cannot identify |
|---|---|---|
| Tool results and Appendix O | Establish the prior transfer observation and its interpretation | Independent confirmation by reusing the same rows; a same-item substrate effect |
| Full Raw/Raw+E, actual matched inputs | Test how revealing graph facts changes reference recovery on the same KG tasks | Dependency inference on equally informative descriptions, or the cause of tool-side errors |
| K1/K5 and K7/K8 | Hold designated graph facts fixed while varying controlled rendering | Unrestricted natural language or a pure measure of latent dependency reconstruction |
| K1/K3/K4 | Change source/object/both-card hosting while retaining directed facts | A unique memory/search mechanism: duplication changes length, repetition and salience too |
| K1/K7 and K5/K8 | Check sensitivity to procedural versus direct question wording | New graph information; K1 already provides step-by-step instructions, so merely proposing stepwise wording is not a new intervention |
| K1/K2 and K5/K6 | Probe precision/coverage under irrelevant but connected neighbours | Pure adjacency causality: distractor identities, edge counts and context also change |
| Common-size families and Full size grid | Bound difficulty patterns and rule out a size-only description within selected samples | Pure topology, monotonic universal difficulty, or mechanism identification |
| Real/pseudonym conditions | Check lexical/name sensitivity where archived pairs are valid | A unique world-knowledge effect independently of tokenization/length |
| Incremental | Potentially useful background | Process or budget-matched search claims without complete historical turns |

## Fresh bounded diagnostics

The retained script [diagnose_transfer.py](analyses/transfer_positioning/diagnose_transfer.py) reads the existing archive using the standard library. It makes no API, judge or database calls and imports no research modules. The main selector covers 6,900 observations: five common six-node families in Core K1/K2 and Full Raw/Raw+E, plus six-node Tree-in K3/K4/K7. A supplementary cached-score selector covers Core K1-K8 on the same five families (12,000 observations); these selectors overlap and must not be added as independent data.

The script validates uniqueness and 100 planned rows per group; actual Raw/overlay and controlled pair keys; category conservation; independently reconstructed witnesses/endpoints from explicit public facts; and agreement of saved selected names with cached set scores where identity-level evidence exists. Its final output contains 2,581 valid identity-level route diagnostics across 1,300 unique explicit inputs. Route completion means that all vertices on a reference route were selected, not that a route was predicted or executed. It is not chain-of-thought/process evidence.

Gemma Core has cached metrics without selected identities. The selected common-size Full overlay inputs lack saved task specifications needed by this independent traversal procedure; 1,479 valid outcomes are therefore excluded from route diagnostics. Their cached condition results remain usable at that evidence tier. No historical specification is filled from current defaults. Invalid outcomes stay in the planned denominators for set-level summaries and are excluded, with explicit valid denominators, from identity-level error descriptions.

### Residual Tree-in errors are localized, not just counted

Core, six nodes, 100 planned tasks per model/condition. K1 = disconnected source-card triples; K3 = destination-card triples; K4 = same relations on both cards. All Qwen rows here have valid saved selections.

| Qwen Tree-in condition | Exact reference, /100 | S equals anchor plus first-hop neighbours, /100 | Selected second-level endpoints / available endpoints |
|---|---:|---:|---:|
| K1 | 15 | 71 | 64/300 |
| K3 | 16 | 76 | 62/300 |
| K4 | 51 | 31 | 181/300 |

For K1, 198/200 intermediate-node opportunities are selected, while only 64/300 endpoints are selected; in 84/100 tasks all first-hop neighbours and the anchor are retained but at least one endpoint is missing. The exact one-hop set occurs in 71/100 tasks. It is an **observable output signature consistent with depth-one truncation**, not proof that the model internally stopped its search after one hop. Type/relationship-specific failures, prompt interpretation, salience and failure to accumulate distributed evidence remain alternatives.

The paired K1-to-K4 Tree-in comparison gains exact recovery on 42 tasks and loses it on 6, producing the marginal 15-to-51 change. Its mean F1 change is +0.13499242424242433. The one-hop signature decreases from 71 to 31. Moving facts to destination cards alone (K3) does not produce the same descriptive improvement. Thus neither "explicit relations solve the task" nor "destination placement alone fixes incoming traversal" describes these Qwen results.

Ministral also provides a useful contrary profile: K1 Tree-in has 54/100 exact selections and 15/100 exact one-hop sets; K4 has 62/100 and 6/100 respectively. Gemma cached exact counts are 87/100 and 93/100, but no identity-level mechanism comparison is possible there. These are model- and condition-specific diagnostics, not a universal failure rule.

For Qwen K1 Tree-out, exact recovery is 50/100 and the exact one-hop signature 27/100, versus 15/100 and 71/100 for Tree-in. Both families require two-hop route coverage, yet relation/type/card composition and direction differ. This narrows a behavioral question but does not isolate direction causally.

### Revealing relations improves recovery without uniformly removing errors

Common size six, Full Raw/Raw+E, 100 planned tasks per family/model. Values below are counts of exact selection, not complete-reference success.

| Model | Chain Raw -> Raw+E | Tree-in Raw -> Raw+E |
|---|---:|---:|
| Gemma | 0 -> 100 | 0 -> 68 |
| Qwen | 0 -> 63 | 0 -> 1 |
| Ministral | 0 -> 19 | 0 -> 1 |

The overlay improves F1 in all six listed comparisons, but the residual profile is far from universally perfect Chain or universally hardest Tree-in under every condition. Full and controlled Core inputs are different evidence contexts on overlapping bases, not independent replications or interchangeable score cells. The Raw outcomes may be appropriate abstentions under missing evidence; omission against a hidden graph target is not automatically a reasoning failure.

All counts, denominators and pair transitions are in `run-04/summary.json`, keyed by series/model/condition/noise/motif/size; per-observation route fields and IDs are in `run-04/route_diagnostics.csv`. No new p-values, confidence intervals, ranking correlations or interactions were computed. Existing simultaneous intervals for aggregated condition effects do not cover these newly selected motif/error contrasts.

## Hypotheses and discriminating predictions

| Hypothesis | Compatible evidence now | Competing explanation | Discriminating next check |
|---|---|---|---|
| H1: reconstructing latent relations contributes to sequential tool-selection errors | Prior Chain inversion and KG overlay gains | Raw has missing facts; substrates, queries and populations differ | Same real tool items with/without an all-candidate dependency overlay; separately verify relation recoverability and target conventions. |
| H2: residual Tree-in errors involve incomplete depth/route enumeration | Frequent anchor-plus-first-hop outputs with second-level omissions | Type/relation-specific comprehension or task wording | Re-score outputs against predeclared one-hop/reversed-direction/over-depth alternatives; perturb direction while matching graph and types. |
| H3: access to distributed facts limits complete recovery | K4 reduces the Qwen one-hop signature; K3 alone does not | Repetition, salience, token length and encoding cues | Matched-token repetition/placement controls with identical unique facts, randomized ordering and target-free displays. |
| H4: connected decoys increase constraint violations or inclusion | Core paired noise results and omission/inclusion categories | Context load or response-format failure | Map each false positive to admissible routes under changed direction/depth; retain overlapping labels and unrelated FPs. |
| H5: incompleteness reflects failure to cover multiple branches | Partial path coverage and endpoint omissions | General depth-one truncation; reference-size demand; type errors | Compare wholly absent first-hop branches with missing descendants of retained branches; vary branch count at fixed depth/size and preserve query semantics. |

H2 and H5 are not interchangeable. In Qwen K1 Tree-in, only 2 of 200 first-hop branch opportunities are wholly absent, whereas second-level endpoints are frequently absent. It would be inaccurate to summarize this particular slice solely as choosing one complete branch and ignoring all others. No output-set signature proves an internal execution order. No hypothesis is promoted to an established cause.

## Additional work, ordered by scientific necessity

### A. Mandatory for a substantive cross-domain transfer claim; offline if records exist

1. Obtain and audit the original Tool Selection record-level outcomes, candidate/reference graphs, actual prompts, model settings and validator flags. Match fingerprints with Appendix O and this archive, and disclose reused rows. A PDF table is enough for a literature premise but not for a new adjusted cross-domain estimate. The anonymous repository linked in the PDF was attempted read-only through the web tool and was inaccessible in this audit. No external record archive was independently verified.
2. Define a harmonization table before computing contrasts: set target, success = all reference vertices selected, exact, valid/failure policy, size range, shared motifs, model/provider/time/harness, and reference-necessity tier. Recompute metrics per item when possible. Do not mix source-paper success with KG mean F1. Use seven shared motifs only where support exists; for common-size comparisons require actual common support rather than extrapolating missing tool cells.
3. Evaluate specific predictions rather than treating a global rank correlation as an explanation: the Chain-versus-comparator contrast at shared size, residual incoming-tree errors after conditioning on visibility, and omission/inclusion transitions under noise. Distinguish tool-side raw Tree-in difficulty from the prior size-adjusted null-compatible estimate. Align covariates and show distributions; an adjusted regression cannot manufacture a missing factorial cell or turn substrate differences into causality.
4. Declare new exploratory estimands, primary contrasts, clustering and multiplicity. Preserve base/anchor/task reuse; consider sparse events, ceilings, separability and collinear size/depth/width. Anchor-only intervals remain conditional because reference entities overlap. Report within-domain contrasts and cross-domain differences as conditional associations unless a matched intervention is available.

### B. Mandatory for a deeper diagnostic paper; mostly offline on the current archive

1. Complete the role/route analysis across the relevant available selections and diagnostic conditions; explicitly state missing selected identities/specifications. The bounded six-node pass is complete, not full-archive process analysis.
2. Add query-rule counterfactual labels (wrong direction, premature depth limit, excessive depth, terminal-type violation). These are public-graph diagnostics, not new model calls. Allow multiple compatible labels; exact equality with an alternative rule is stronger output evidence than a false positive merely being adjacent.
3. Extend paired K1/K3/K4/K7 transitions to **which errors change on the same tasks**, especially whether formerly one-hop outputs become exact or another error. Current outputs give marginal signatures and exact transition counts; they do not yet tabulate the full within-task signature-to-signature matrix.
4. Audit evidence recoverability in Raw using an explicit annotation policy or verified subset before calling its omissions reasoning errors. A native/prose relation may be paraphrased; a string match or missing relation field is not a sufficiency test. The existing controlled prose contrasts can support a narrower equal-fact question immediately.
5. Review representative and contrary cases against the saved prompt and output. Categorization should be reproducible or independently annotated if semantic judgment is needed. Do not use model explanations or a missing trajectory as access to latent reasoning.

### C. New experiments if the paper claims stronger explanation

These are proposed, unimplemented and not authorized for execution. No budget or performance is asserted.

- **Real-tool dependency exposure:** use the same validated tool items, candidate pools, questions, model/version and response protocol in the original and all-candidate dependency-overlay conditions. Show every eligible candidate edge, never only the gold task subgraph. Stratify preselected Chain and branching controls at overlapping sizes. This directly probes the prior dependency-inference explanation; KG-only ablations cannot substitute for it.
- **KG rule and branch probes:** use explicit, fact-matched inputs; vary direction/depth instructions or branch demand while keeping type/relation/length distributions controlled, add irrelevant-edge controls, and use an ordinary public-input traversal baseline. A structured checkpoint may request discovered frontier sets before the final union, with an equal-output-budget control. K1 is already procedural, so this must test a specific missing operation rather than simply add "think step by step".
- **Representation controls:** separate destination placement, duplication, irrelevant repetition, order and token budget. The K1/K3/K4 contrast motivates this design but cannot distinguish all those variables by itself.
- **Optional bridge design:** isomorphic abstract graphs with tool-like and entity-like labels and the same set-coverage query can isolate framing effects. This simplified task does not establish equivalence to real API composition; retain a real-tool validation arm for any tool-mechanism conclusion.

Plan counts from accepted task IDs and existing availability before estimating API cost. Use fresh evaluation cohorts to test hypotheses selected after looking at these results. A new result may be null; the contribution is a discriminating test and its measured boundary, not a promised improvement.

## Proposed RQs and contributions

**RQ1: Which selection-difficulty patterns transfer from tool dependency selection to KG route coverage after making target, metric, size support and evidence conditions explicit?** Appendix O supplies the prior observation; a new harmonized item-level analysis would supply the increment. Until Tool records are audited, describe this as a literature-grounded boundary question, not a new completed transfer test.

**RQ2: Which observable failures account for incomplete KG recovery when the required relations are visible?** Analyze anchor/intermediate/endpoint selection, complete-route coverage, incomplete first-hop branches and alternative traversal-rule signatures. The fresh one-hop findings support a concrete starting result. They do not identify latent mechanisms.

**RQ3: Which failures are sensitive to fact availability, placement and query formulation, and which remain under those interventions?** Use actual paired conditions; separate added information from equivalent-fact presentation; report error transitions and contrary model results. This is the principal additional experimental scope relative to Appendix O. Claims about substrate-level mechanisms remain conditional until discriminating tool/KG probes are available.

Proposed contribution wording, with explicit completion status:

1. **A harmonized analysis of the boundaries of structural-difficulty transfer between tool and entity selection.** Candidate contribution; original tool records and a comparable analysis are still required. Reusing Appendix O's rank correlations is not enough.
2. **An output-level localization of residual KG selection errors, distinguishing first-level retention from complete-route recovery and testing their sensitivity to paired evidence conditions.** Initial bounded results now support this; full intended-scope error-transition audit and verification remain.
3. **An evidence-based set of falsifiable explanations for non-transfer, with tests that distinguish relation availability, route enumeration and constraint adherence.** Hypothesis development is defensible now; wording such as "we demonstrate the causes" requires additional discriminating evidence. A plan alone is not a completed empirical contribution.

Fallback if tool records remain unavailable: center RQ2-RQ3 as **diagnostic follow-up to an established transfer observation**, with RQ1 as motivation. Name this limitation plainly. Such a paper could be self-contained scientifically if its new diagnostics and tests are substantial, but this audit cannot guarantee its independence, novelty or venue acceptance. More pages of the existing motif plots would not close the gap.

## Restructure Results and Discussion

Results should follow the explanation being tested, not the catalogue of motifs: (1) prior transfer premises and comparability; (2) availability gains and residual failures; (3) depth/branch/constraint error signatures; (4) paired placement/wording/rendering tests and changes in those signatures; (5) robustness and counterexamples. A new cross-domain table must label literature-reported values separately from new KG measurements; no fabricated Tool arm or pooled population.

Discussion should explicitly separate **observation**, **compatible explanations**, **alternative explanations**, and **the next falsifying test** for each principal finding. Address why a directed KG relation is not a tool input requirement, why all-route coverage is not minimal QA evidence, why missing Raw relations are not inferable dependencies, and why final sets are not process traces. State exactly what the KG evidence suggests about Tool Selection and what it cannot establish. Use corporate Web information access/GraphRAG as the application context without claiming downstream QA gains.

Recommended main assets: a task/visibility/target alignment table; a two-domain common-support contrast plot if raw Tool records become available; an error-localization figure with first-level/endpoint/path coverage; and a paired condition-to-error transition table. Full motif/size grids and undifferentiated rendering tables move to the appendix. Retain unfavourable controls and model-specific results.

An academic-English section outline is saved separately in [transfer_outline.md](transfer_outline.md). No main manuscript section was rewritten in this assessment.

## Literature boundary and search log

Primary-source checks on 2026-10-25:

- Exact-title searches for Tool Graph Complexity / AgentGraphBench did not establish public publication metadata. The supplied anonymous PDF is the inspected source; the absence of a search result is not a novelty finding.
- [Talk like a Graph, ICLR 2024 proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/file/bf72f65f30eedf5d48da6980ee02b589-Paper-Conference.pdf), pp. 1-3 and Appendix A graph encodings, independently establishes graph encoding/task/structure as prior axes. Rendering sensitivity is context, not a new general principle.
- [Faith and Fate, arXiv v3](https://arxiv.org/html/2305.18654v3), Sections 2 and 3.2.3, uses computation graphs and local/propagated errors in different compositional tasks. It motivates operation-level diagnostics but does not validate our KG/tool mechanism or let final selection sets stand in for intermediate computations.
- The anonymous artifact repository from the supplied PDF was inaccessible through the web tool. Secondary search hits for entity disambiguation/integration were excluded as different tasks; no claims were based on their summaries.

This is a focused positioning check, not an exhaustive new related-work or novelty survey. No bibliography fields, accepted-publication status or venue rules were invented or changed.

## Readiness and record of work

The repositioning assessment and bounded exploratory pass are complete. A complete manuscript claiming the stronger transfer/diagnostic contribution is not yet ready: RQ1 lacks harmonized Tool rows, RQ2 needs intended-scope rule/signature checks, and causal interpretations remain hypotheses. The previous descriptive manuscript remains available but does not satisfy the revised contribution ambition by itself. Update of the writing gate records this scope change rather than retracting the historical build.

No research source code, frozen results, original drafts, model calls, database queries, external uploads or submission actions were involved. Derived evidence is separate. Current production ledger byte-hash failures from Windows line-ending conversion are retained as a documented integrity portability issue; they are not silently fixed by refreshing hashes. New records use the actual inspected bytes and have a separate scoped structural check.
