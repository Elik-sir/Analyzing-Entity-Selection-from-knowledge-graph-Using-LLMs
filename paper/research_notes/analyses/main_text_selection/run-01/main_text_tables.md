# Main-text table previews

Selected existing results, 2026-10-25. This is an outline asset, not a compiled manuscript table.

## Table 1 — Experimental conditions

| Condition (archive ID) | Evidence | Distractors | Placement / question | Main contrast(s) | Planned bases/model |
|---|---|---|---|---|---:|
| Raw (Braw) | Native cards | Disconnected | Native | Raw+E − Raw | 3,400 |
| Raw+E (Braw+E) | Native cards + explicit links | Disconnected | Native | Raw+E − Raw | 3,400 |
| Triples/source (K1) | Controlled triples | Disconnected | Source / step-by-step | K5−K1; K3−K1; K4−K1; K2−K1 | 700 |
| Triples/adjacent (K2) | Controlled triples | Adjacent | Source / step-by-step | K2−K1 | 700 |
| Triples/destination (K3) | Controlled triples | Disconnected | Destination / step-by-step | K3−K1 | 700 |
| Triples/both (K4) | Controlled triples | Disconnected | Both cards / step-by-step | K4−K1 | 700 |
| Text (K5) | Controlled templated prose | Disconnected | Template / step-by-step | K5−K1; K6−K5 | 700 |
| Text/adjacent (K6) | Controlled templated prose | Adjacent | Template / step-by-step | K6−K5 | 700 |
| Triples/direct (K7) | Controlled triples | Disconnected | Source / direct question | K8−K7 | 700 |
| Text/direct (K8) | Controlled templated prose | Disconnected | Template / direct question | K8−K7 | 700 |

Per-condition/model planned counts; repeated conditions and the two panels are not independent datasets to sum. Historical design is supported by the frozen-pairing audit, not the current registry alone.

## Table 2A — Native-card and overlay F1

| Archived model | Raw F1 | Raw+E F1 | ΔF1 | Simultaneous band for ΔF1 |
|---|---:|---:|---:|---|
| Gemma-4-31B | 0.305 | 0.978 | +0.674 | [0.664, 0.683] |
| Qwen3.6-Flash | 0.386 | 0.852 | +0.466 | [0.453, 0.479] |
| Ministral-14B | 0.275 | 0.847 | +0.572 | [0.554, 0.590] |

## Table 2B — Exact selection and protocol validity

| Archived model | Raw exact | Raw+E exact | Valid Raw / planned N | Valid Raw+E / planned N |
|---|---:|---:|---:|---:|
| Gemma-4-31B | 0.003 | 0.920 | 3353 / 3400 | 3360 / 3400 |
| Qwen3.6-Flash | 0.012 | 0.589 | 3170 / 3400 | 3323 / 3400 |
| Ministral-14B | 0.009 | 0.419 | 3133 / 3400 | 3352 / 3400 |

Caption: 3,400 paired tasks per model; all planned outcomes retained, invalid/missing outcomes contribute zero to primary scores. Δ is Raw+E minus Raw. Bands are exploratory simultaneous bands from the declared 78-effect F1/exact family, conditional on this fixed KG and independence across anchors. They do not cover arbitrary shared-entity dependence. Scores rounded to three decimals; valid counts are protocol outcomes, not raw-response availability. Archived model labels do not authenticate unavailable provider/version metadata.

Figure 2 retains all six selected controlled contrasts for each model. Its stored delta and interval values are multiplied by 100 only for the percentage-point axis. Figure 1 remains specified, not rendered, in paper_outline.md.
