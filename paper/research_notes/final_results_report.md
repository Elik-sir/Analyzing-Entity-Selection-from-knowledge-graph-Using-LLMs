# Final saved-results tables, figures and uncertainty analysis

Completed 2026-10-25. This is an exploratory reanalysis of the existing archive, following the completed reference/pairing audit. No new model responses, model experiments, database exports or research-source edits were made. Numerical artifact directory: `analyses/final_results/run-01/`.

## Main outcome

The main patterns supported by the saved data are a large increase in graph-reference recovery when explicit relations are added, lower selection scores with adjacent distractors, and model-dependent effects of representation and fact placement. Smaller differences should not be promoted into universal statements about text, triples, names or reasoning ability.

All 60,088 planned observations are included in the descriptive export: 66 condition groups and 608 motif/size groups. Precision, recall, F1 and exact match are means of individual task scores. Invalid/missing outcomes remain in N with zero contribution. Valid counts, valid-only summaries, raw-response availability and cached-metric coverage accompany the scores. Pilots and mock data are excluded.

## Delivered artifacts

- [Condition metrics](analyses/final_results/run-01/condition_metrics.csv): every series/model/condition/noise, planned and valid N, failure-inclusive metrics and valid-only diagnostics.
- [Detailed motif/size metrics](analyses/final_results/run-01/motif_size_metrics.csv): all 608 strata; use actual model coverage rather than inferring a complete grid.
- [Paired contrasts](analyses/final_results/run-01/paired_contrasts.csv): all-planned means/deltas, pointwise cluster intervals, simultaneous main-family bands, task-bootstrap sensitivity and both-valid diagnostic deltas.
- [Mean intervals](analyses/final_results/run-01/mean_intervals.csv), [coverage](analyses/final_results/run-01/evidence_coverage.csv) and [statuses](analyses/final_results/run-01/status_counts.csv).
- [Analytical baselines](analyses/final_results/run-01/analytical_baselines.csv): select-all, select-named-anchor and uniform random-six expectations for Core and Full Braw.
- [LaTeX numeric table fragments](analyses/final_results/run-01/tables/raw_results.tex): Raw comparison, Core F1 and analytical baselines. These fragments require booktabs and have not been compiled into a manuscript.
- Four publication figure assets, each PNG at 300 dpi and vector SVG, under `paper/figures/final_results/`. Their exact data rows, captions and hashes are in [figure_sources.json](analyses/final_results/run-01/figure_sources.json).

## Statistical design and scope

The [analysis plan](analyses/final_results/analysis_plan.md) was recorded before the new interval calculations, after prior descriptive inspection; it is not a preregistration. The principal score is all-planned mean set-F1; exact match is a secondary endpoint included in the declared simultaneous family. Delta is always right minus left in score units; figures may multiply by 100 and label percentage points.

For each resampling panel, sample its G distinct starting-entity IDs G times with replacement. An anchor receives one weight shared by every base task, condition and model attached to it. Compute weighted means within each motif-size cell and recombine them with the original cell weights. This retains pairing and the frozen task-grid composition. There are 628 anchors for 700 Core bases and 2,425 anchors for 3,400 Full Braw bases. The bootstrap uses 10,000 replicates with deterministic PCG64 seeds recorded in `provenance.json`; no required cell was empty in the actual draws.

Pointwise 95% intervals use bootstrap percentiles. The main simultaneous family contains 78 effects: twelve Core contrasts times three models plus three Raw contrasts, each for F1 and exact match. A centered maximum absolute deviation, standardized by each effect's bootstrap SD, calibrates each panel family at nominal 97.5% coverage. A two-panel union bound gives at least 95% combined **nominal** coverage under the bootstrap assumptions, without requiring independence between Core and Raw. This is an approximate exploratory band, not exact finite-sample coverage or a collection of p-values. Supplementary Size/incremental intervals are pointwise and outside that family.

Paired task resampling within motif-size cells is a sensitivity analysis. Its main effect directions agree with the anchor analysis for the large Raw/noise patterns. Across F1 contrasts, anchor/task interval-width ratios range from about 0.974 to 1.126; do not select the narrower method retrospectively.

The methodological motivation for keeping within-cluster dependence separate from independence across clusters is discussed by [Cameron and Miller, 2015](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf). The exact ratio estimator and band construction used here are specified in the plan and code rather than attributed wholesale to that source.

## Research-question findings

### Evidence availability: Raw to Raw+E

For each model there are 3,400 matched base tasks. All-planned mean F1 and paired increases are:

- Gemma: 0.304571 to 0.978317; delta +0.673746. Simultaneous band [0.664004, 0.683488].
- Qwen: 0.386060 to 0.851818; delta +0.465758. Simultaneous band [0.452594, 0.478921].
- Ministral: 0.275482 to 0.847397; delta +0.571915. Simultaneous band [0.553843, 0.589988].

These bands are from the declared 78-effect construction. The positive direction remains in the both-valid paired diagnostic; this is not simply an artifact of including more invalid outcomes in Raw. Adding relations changes available information, so describe the result as stronger recovery of the graph reference when explicit links are supplied. It does not establish that a model reasoned incorrectly when native descriptions omitted needed facts, or that downstream QA improved.

### Adjacent distractors

For triples (K2 minus K1), F1 changes are -0.016228 for Gemma, -0.062259 for Qwen and -0.157361 for Ministral. For text (K6 minus K5), they are -0.023078, -0.057873 and -0.165608 respectively. All six simultaneous bands lie below zero in this conditional anchor-bootstrap analysis. The direction persists on both-valid pairs and under the task-bootstrap diagnostic.

This supports a bounded statement about adjacent distractor contexts in these archived paired tasks. Adjacent variants alter candidate composition and graph density; do not call the estimate a universal pure-topology causal effect.

### Representation and placement

The triple/text contrast is much smaller than the Raw/Raw+E contrast. Qwen's text-minus-triples F1 differences are about -0.0232 for both question variants, with negative simultaneous bands. The corresponding Gemma and Ministral bands include zero. This does not establish equivalence for those models; it also does not support a generic “text fails” statement.

Duplicating facts on both cards increases Qwen F1 by 0.041483, with simultaneous band [0.023632, 0.059334]. The effect is not uniform across models. Other small placement/formulation effects often have bands crossing zero or depend on invalid outcomes. The full CSV retains all twelve Core contrasts rather than only the favorable ones shown in a main figure.

### Motif, size and incremental diagnostics

The motif heatmap separates disconnected/adjacent conditions and displays actual means. Tree-in tasks are difficult for Qwen/Ministral relative to several other task families, but motif comparisons also change query semantics and are descriptive. Additional-size figures cover Gemma's available K1/K5 cells only; they do not establish a size law across all models or the whole graph.

The matched incremental comparison uses 350 Gemma bases per condition, not all 700 static bases. Incremental-minus-static F1 is -0.236524 for triples and -0.231815 for text. These exploratory endpoint-score differences cannot identify a search mechanism or equal-budget access effect because complete historical turn sequences and matched token budgets are unavailable.

## Failure and baseline diagnostics

Both-valid paired differences are kept separate from the primary scores because restricting to successful protocol outcomes changes the population. Four F1 point-estimate directions reverse in this diagnostic: Ministral's direct-question text/triples contrast, Gemma's object/both placement contrasts, and the Gemma additional-size representation contrast. None supports a simple universal superiority claim.

For Core, analytical F1 is 0.363526 for select-all, 0.308844 for select-anchor, and 0.230026 for uniform random-six. For Full Braw it is 0.405134, 0.292492 and 0.242355 respectively. Random-six numbers are exact expectations over uniformly sampling six of 25 candidates without replacement; no simulated model outputs were created. These simple set-recovery reference points help interpret low scores, but selecting unsupported entities is not evidence-grounded reasoning. In particular, a broad select-all set can beat an abstaining model against a hidden graph target without demonstrating a better answer.

## Dependence limitation that must remain visible

The [dependence audit](analyses/final_results/run-01/dependence_audit.json) finds that shared reference entities connect 578 of 700 Core tasks and 3,265 of 3,400 Full Braw tasks into their largest respective components. Thus the anchor clusters are not entity-disjoint. Treating every shared-entity component as an independent resampling unit would leave one overwhelmingly dominant unit and does not yield a defensible general-purpose graph-level interval here.

The delivered intervals assume independence across anchors conditional on this fixed KG and task grid, while retaining dependence within an anchor. They do not control arbitrary cross-anchor shared-entity effects, measure variability across graph domains/model seeds, or simulate repeated API generations. This is a real scope restriction, not a reason to remove the archived descriptive comparisons. Avoid claiming unrestricted population significance.

## Validation and visual QA

[validation.json](analyses/final_results/run-01/validation.json) records eight passed numerical/software checks: joint pairing and deterministic seeds, fixed stratum weights, explicit empty-cell rejection, degenerate-band handling, finite enumeration of random-selection expectations, independent recomputation of all condition groups, reconstruction of intervals from saved bootstrap draws, and figure-source/hash matching. The eight entries group some related checks.

The maximum absolute change in a pointwise interval endpoint between the first and second 5,000 bootstrap draws is about 0.00260 for Core and 0.00110 for Raw. Keep extra displayed digits for traceability, not as a claim of exact Monte Carlo precision. A later inference claim near an endpoint should account for this sensitivity.

All four PNGs were visually inspected. A Raw legend overlapping data labels was moved outside the axes, and the updated image was reinspected. SVGs carry the same plotting data; source rows and file hashes are registered. No manuscript/PDF build is claimed in this step.

## Next manuscript-preparation step

The results package and an explicit uncertainty analysis are now available. The next substantive step is to compare the intended contribution with mandatory Tool Graph Complexity (including its KG appendix), Talk like a Graph and the supplied graph-pattern/KG-understanding work, then choose the claim scope and outline. The full-writing gate remains closed until that positioning and planned-claim selection are complete; a numeric package alone does not establish novelty.

## Reproduction

From the repository root, use the existing environment with NumPy and Matplotlib; choose fresh output/figure directories:

```powershell
& '.venv/Scripts/python.exe' -B -X utf8 paper/research_notes/analyses/final_results/analyze_results.py --root . --output paper/research_notes/analyses/final_results/recheck --replicates 10000 --seed 20261025
& '.venv/Scripts/python.exe' -B -X utf8 paper/research_notes/analyses/final_results/derive_findings.py --analysis paper/research_notes/analyses/final_results/recheck
& '.venv/Scripts/python.exe' -B -X utf8 paper/research_notes/analyses/final_results/render_results.py --analysis paper/research_notes/analyses/final_results/recheck --figures paper/figures/final_results_recheck
& '.venv/Scripts/python.exe' -B -X utf8 paper/research_notes/analyses/final_results/check_analysis.py --root . --analysis paper/research_notes/analyses/final_results/recheck
```

Source/analysis hashes, Python/NumPy versions, seeds, replicate counts, fixed cell sizes and resampling diagnostics are stored in `provenance.json`. Compressed bootstrap draws and their column maps are retained for the main panels. Figure formats are PNG/SVG; conversion to a final LaTeX figure format and manuscript page layout belongs to the later builder step.
