# Reassessment of the paper's scientific emphasis

2026-10-25. Trigger: the author clarified that Appendix O of Tool Graph Complexity was written with this team's participation and asked for an evidence-based comparison of two paper directions. This is a recommendation after bounded offline inspection, not a claim that Appendix O is independent prior work or that the new outline has received author approval. The previous `paper_outline.md` is preserved as the presentation-first alternative rather than silently overwritten.

## Evidence inspected and correction

Inspected the archive README, panel counts, provenance `results/SOURCES.json`, experimental protocol, working-draft task/design descriptions, existing detailed/condition/paired CSVs, source Appendix O comparison, and a fresh streamed pass over archived observations. Primary detailed source: `analyses/final_results/run-01/motif_size_metrics.csv`. New bounded outputs: `analyses/emphasis_assessment/run-01/summary.json` and `provenance.json`; script: `analyses/emphasis_assessment/assess_scope.py`.

The assessment independently re-aggregated cached F1 from archived observations for 499 detailed Core/Size/Full Braw groups and checked those values against the existing detailed CSV. It also classified valid cached fp/fn outcomes as exact, omission-only, inclusion-only or mixed, keeping invalid outcomes separate. This is not re-parsing raw responses or fitting/testing a structural model. No new API calls, model experiments or inference were performed.

**Correction to the earlier conversational advice:** the separate controlled `size` series is Gemma-only, but the Full Braw/Raw+E panel contains a full size grid for all three archived models. It was incorrect to use the former as a reason to demote size analysis generally. Both conditions have 34 motif-size cells with 100 planned tasks per cell and model: chains 3–6, inward/outward stars 3–10, inward/outward trees 5–10, rhombus 4 and hourglass 5. Thus there is real three-model material for motif/size analysis, with different evidence conditions and their own limits.

The Core panel supplies seven motif families under the controlled conditions for all three models. Five families are compared at six nodes; rhombus and hourglass are at four/five, so an unadjusted seven-way ranking is not an equal-size result. In the three models, the 700 Core K1 base IDs all occur among the 3,400 Full Braw+E IDs. This base-ID intersection is not equality of their displayed contexts or proof of the same historical calls; it forbids treating these panels as independent replications to add together.

## What the saved results can support

### 1. Pattern differences have substance at a common size

Core K1, size six, disconnected distractors, source-card triples; all-planned exact selection, 100 tasks per displayed cell:

| Archived model | Star-out exact | Tree-in exact |
|---|---:|---:|
| Gemma | 1.00 | 0.87 |
| Qwen | 0.99 | 0.15 |
| Ministral | 0.99 | 0.54 |

These are strong descriptive contrasts within the same node-count/candidate-count regime, not a fitted pure-topology effect or a statistical comparison between models. The anchor/query, direction, relation/type composition and accepted task sample differ across families. The structural story survives the obvious objection that every difficult motif simply has more nodes, but it does not establish topology as the sole cause.

### 2. Size effects are conditional on pattern and model

Examples from Full Braw+E, 100 planned tasks in each endpoint stratum; these compare different sampled tasks, not paired interventions on the same expanding graph:

- Qwen chain: mean F1 0.994 at three nodes and 0.848 at six; star-out 0.998 at three and 0.998 at ten (rounded); tree-in 0.758 at five and 0.530 at ten.
- Ministral chain: F1 0.929 at three and 0.717 at six; star-out 0.922 at three and 0.973 at ten; tree-in 0.685 at five and 0.536 at ten.
- Gemma star-out: F1 1.000 at both three and ten; tree-in 0.940 at five and 0.875 at ten. The intervening tree-in sequence is not monotonically decreasing.

The scientific message cannot be “more nodes always makes selection harder”. Pattern-specific descriptive curves and model profiles are more faithful. Ceiling effects matter for Gemma and outward stars. Rhombus/hourglass have no size trajectory in this archive; chain is capped at six. Do not extrapolate beyond the recorded ranges or conflate the absence of a downward observed curve with demonstrated invariance.

The candidate pool stays at 25 while the reference grows: target prevalence and distractor count change with size. Select-all F1 is 2s/(25+s) for reference size s, so even simple metric reference points vary along that axis. Exact selection also asks for a larger complete set as s grows. Size curves need F1/recall/exact together and task-specific baseline context, not an assertion of an intrinsic universal complexity law.

### 3. Error types and conditions make the pattern story informative

Core K1 Qwen tree-in has 15 exact, 83 omission-only and 2 mixed outcomes out of 100; it is predominantly incomplete recovery. Core K2 Ministral star-out has 64 exact, 31 inclusion-only, 1 mixed and 4 invalid outcomes out of 100. These cached fp/fn examples show why exact recovery, coverage and excessive selection must be separated. They do not establish an internal reasoning/search mechanism.

Raw/Raw+E holds actual paired public inputs fixed apart from explicit relations; it is an important information-availability check before interpreting pattern differences as solver difficulty. Core disconnected/adjacent pairs expose which model/task families remain fragile when explicit evidence is available. Controlled rendering/placement comparisons then test selected presentation alternatives. These experiments can explain the operating conditions of pattern/size findings; they need not each become a separate main research question.

### 4. Evidence limits apply to both possible narratives

The Core/Gemma controlled size scores lack original raw replies; Full Braw has much stronger response availability, apart from the recorded missing Ministral Raw replies. Historical provider/configuration evidence must be qualified at its actual tier. Motif semantics, relation direction, branch structure, entity/type distribution, question length and candidate-context density are not all controlled independently. Size strata are different accepted task samples, not randomized edits of one task. Repeated anchors and shared entities limit inference. Existing main-family bands cover declared condition contrasts, not every new motif/size/ranking comparison one might now draw. No new significance claim is licensed by plotting these slices.

## Weighing the two paths

| Criterion | A. Patterns and size as the centre | B. Evidence availability/presentation as the centre |
|---|---|---|
| Fit to the designed archive | Strong: seven motif families, matched-size Core and broad all-model Full Braw size grid | Strong: audited Raw/overlay and twelve controlled Core contrasts |
| Main scientific question | Which task structures are difficult, how difficulty varies with size, and under which conditions | How much adding relations or changing their presentation changes graph-reference recovery |
| Most substantive observations | Equal-size family differences, conditional size curves, model/error profiles | Large Raw/overlay differences, robust adjacent-context penalties, some model-specific presentation effects |
| Main interpretive risk | Mistaking task-family contrasts for pure topology, pooled counts for size control, or nonuniform curves for a universal size law | Mistaking missing native evidence for reasoning failure, or information addition for better serialization |
| Current analysis readiness | Detailed scores and figures exist; selected size/pattern conclusions still need an explicit exploratory analysis plan if inferential wording is wanted | Higher: paired means, intervals, failure diagnostics and evidence invariants already audited |
| Relation to Appendix O | Direct overlap with shared-team KG work; must specify reused foundation and additional analyses/conditions | Clearer contrast focus, but explicit-dependency reasoning and graph encodings already exist in the related work |
| Risk of a weak paper thesis | Repeating an Appendix O motif/size result without a clear increment | Reducing the central finding to “providing missing links improves recovery”, with many small auxiliary ablations |
| Best defensible version | A conditional structural study with evidence/noise controls and transparent cross-paper provenance | A focused diagnostic ablation study, without claims to isolate general reasoning or a new representation method |

**Assessment:** A is a stronger scientific centre for this project's intended question and actual archive, provided it is framed conditionally. B is currently easier to write from completed paired analyses, but analytical convenience is not a sufficient reason to replace the original research question. Conversely, returning to A does not justify unsupported topology causality or turning every available condition into a headline finding.

## Recommended emphasis

**Recommendation: structure-led, condition-aware empirical study.** The central question is how LLM entity selection varies across graph-pattern task families and sizes, and how robust those profiles are to evidence availability and adjacent distractors. Structure is the object of study; the presentation experiments establish scope and robustness.

Recommended RQ hierarchy:

1. **RQ1 — Pattern/task-family profiles.** At comparable node counts, which graph-pattern task families are harder for each evaluated model, and are failures omissions, excess selections or protocol failures? Use the five common-size families for the direct matched-size comparison; show rhombus/hourglass separately at their native sizes.
2. **RQ2 — Pattern-specific size sensitivity.** Within each supported family, how do selection metrics change across the available sizes, separately by model and evidence condition? Full Braw/Raw+E supplies the main three-model curves; the Gemma K1/K5 size panel is a controlled supplemental check. Do not assert a universal monotonic size effect.
3. **RQ3 — Robustness of structural profiles.** How do explicit relation availability and adjacent distractors alter those profiles? Raw/overlay and Core noise are the two principal condition contrasts. Rendering, placement, wording and naming are targeted auxiliary checks; incremental access remains exploratory due to missing histories/budgets.

This is neither a claim that all factorial interactions have been measured nor that a fitted motif×size×condition interaction is already significant. The full size grid has no adjacent counterpart for all models, and controlled presentation size data are Gemma-only. Keep those panel boundaries explicit.

Main-text asset priorities should consequently change from the previous outline:

- Promote a motif/error-profile figure (F1 and/or exact plus precision/recall explanation) and a three-model pattern-specific Full Braw/Raw+E size figure. The latter is not the existing Gemma-only size figure; a new derived rendering of saved results is needed.
- Retain a concise design/coverage table that distinguishes the three panels and their size ranges, pairing and evidence tiers.
- Use a compact condition-contrast table/figure for relation availability and adjacent noise, with the complete presentation ablations in the appendix. Do not average out motifs everywhere and then claim to study patterns.
- Keep a small task/reference example if page space allows; do not let a general workflow schematic replace the structural results.

For an eight-page main text, a sensible scientific allocation is roughly half the Results space to RQ1, about one third to RQ2 and the remainder to RQ3; these are editorial priorities, not mandatory percentages or a tested claim. The actual figure/table count needs a revised outline and layout rather than merely moving all prior supplementary material into the main text.

## Shared-team Appendix O and the additional contribution

The author's participation in Appendix O is recorded as author-supplied context. `results/SOURCES.json` labels the source root AgentGraphBench, providing concrete shared-project provenance. Neither fact identifies anonymous authors or proves which published table rows use the same inputs/responses. Do not call this independent external validation.

Shared authorship does not make the overlap a scientific defect by itself. It changes the positioning to a transparent extension of shared KG experimentation. The added value must come from additional questions, controlled conditions, analyses or findings, not presenting an already reported pattern/size result as newly discovered. Row-level overlap still needs a source-task/run crosswalk before claiming new populations or giving a precise reused-versus-new count.

A viable contribution statement is a focused characterization of KG entity-selection difficulty by pattern and size **under explicitly distinguished evidence and distractor conditions**, with failure-mode and reference interpretation. Whether that increment is sufficient for the intended venue remains a scientific judgment, not certified by the number of experiments or our authorship of the appendix. If all major structural findings and underlying rows are already reported there, the article must earn its additional contribution through demonstrated analyses/conditions rather than simply a longer version of those tables.

## Next work and scope

No new model runs are needed to adopt this emphasis. First revise the outline; then prepare the all-model size rendering and motif/condition/error summaries from the saved archive. If inferential claims about topology or size are desired, record an exploratory analysis plan specifying common support, estimand, model/task controls, dependence and multiplicity before fitting; do not reuse the current 78-effect condition family as coverage for those new claims. Such bounded offline analysis is within scope, while new calls/exports remain unauthorized.

The previous presentation-first outline is retained as a documented alternative. The present recommendation supersedes treating it as the settled scientific emphasis. Full writing and submission readiness are not newly approved by this assessment.
