# Saved-results analysis plan

Recorded 2026-10-25 before computing the new intervals. This is an exploratory reanalysis of already inspected results, not a preregistration. No new model runs, source changes or generated experimental outcomes are authorized by this plan.

## Estimands and populations

- Use only `results/observations.jsonl.gz`, with archive input/reference metadata. Never merge local pilots or mock reports.
- Primary score: mean per-task set-F1 across every planned observation; invalid/missing outcomes contribute zero. Also report precision, recall, exact match, valid fraction, conditional-on-valid metrics and evidence coverage.
- Preserve each model's identity and population. Core has its frozen seven-motif panel; Full Braw has its frozen motif/size grid. Do not average model scores into a single headline.
- Pair the twelve already audited Core contrasts and Braw/Braw+E separately within each model. Delta always means right minus left, in score units. Size and incremental contrasts are supplementary; incremental uses only the matched static subset.

## Dependence and bootstrap

Reference metadata identifies repeated anchor IDs. Primary intervals use a paired anchor-cluster bootstrap: resample distinct anchors with replacement, give all tasks/conditions/models using that anchor the same weight, compute means within each observed motif-size cell, and retain the original cell weights. This preserves the sampled grid estimand and keeps cross-condition/model pairing. Draws omitting an entire required cell must be rejected and counted, not silently treated as zero.

Use 10,000 replicates, deterministic NumPy PCG64 base seed 20261025, and batches to bound memory. Each panel draws its own G anchors G times, with joint draws across that panel's conditions/models. Core and Full Braw are separate resampling panels; cross-panel covariance is not assumed in the simultaneous bands. Panel-specific seeds are deterministic offsets from the base seed, and their exact values are retained in provenance.

Sensitivity: paired task bootstrap independently within each motif-size cell, with shared task draws over all conditions/models in that panel. It addresses task-level variation and does not account for repeated-anchor dependence.

Pointwise intervals are the 2.5/97.5 percentile endpoints. Also construct an exploratory simultaneous band for the 78 main contrasts: (12 Core contrasts x 3 models + 3 Full Braw contrasts) x (F1, exact match). Use the bootstrap distribution of the maximum absolute centered deviation standardized by each contrast's bootstrap SD; calibrate Core and Full Braw separately at 97.5% family coverage and apply a union bound for at least 95% combined nominal coverage. The point estimate +/- the resulting panel-family critical value times its bootstrap SD defines the band. Zero-variance contrasts are explicitly labelled degenerate. This is an approximate bootstrap band under the stated independence assumptions, not an exact finite-sample guarantee or a p-value.

## Limits and checks

- Shared reference entities connect most tasks into a large component; anchor clusters are not entity-disjoint. Do not describe these intervals as controlling arbitrary shared-entity dependence or as uncertainty across KGs/model seeds. Report component sizes and the assumption of independent anchor clusters conditional on the fixed KG.
- Separate archived cached metrics from raw-response evidence. Previously completed reference/parser verification is supporting provenance, not a new run here.
- Report both-valid paired differences as a sensitivity diagnostic, explicitly conditional on protocol success and potentially selected. Do not replace the all-planned primary score.
- Analytical select-all, select-anchor and uniform random-k=6 reference baselines may be computed for main route-coverage populations. Random results are expectations under sampling without replacement, not simulated LLM performance. Do not present the private oracle as a deployed baseline.
- No formal p-value tests or significance labels are planned. Simultaneous bands limit selective interpretation within the declared family, but this remains exploratory.
- Verify score aggregates against saved-data definitions, all pair IDs and dimensions, all bootstrap sample denominators, reproducibility, expected baseline formulas, and exported figure sources. Inspect rendered figures before delivery.

## Planned artifacts

CSV/JSON: all condition and motif/size summaries; Core/Raw paired contrasts with pointwise and simultaneous intervals; matched incremental and size diagnostics; evidence/failure accounting; analytical baselines; bootstrap/dependence provenance. LaTeX table fragments carry verified numbers and captions, not a manuscript. Publication figures show Raw/Raw+E F1/exact, main controlled deltas, motif/noise patterns, and additional-size diagnostics. Every figure has a data-source CSV, metric units, population labels and interval method.

Method context: [Cameron and Miller, A Practitioner's Guide to Cluster-Robust Inference](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf) explains the distinction between within-cluster dependence and independence across clusters, and cautions about few/unequal clusters. The exact bootstrap estimands and simultaneous-band construction used here are specified above rather than attributed wholesale to that paper.
