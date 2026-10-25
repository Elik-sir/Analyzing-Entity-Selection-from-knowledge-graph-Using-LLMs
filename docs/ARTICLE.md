# Article manuscript

## Contents and progress

- [ ] [Abstract](#abstract) — Not drafted
- [ ] [1. Introduction](#1-introduction) — Not drafted
- [ ] [2. Related Work](#2-related-work) — Not drafted
- [x] [3. Task and Benchmark Construction](#3-task-and-benchmark-construction) — Approved
- [x] [4. Experimental Design and Evaluation](#4-experimental-design-and-evaluation) — Approved
- [ ] [5. Results](#5-results) — Not drafted
- [ ] [6. Discussion, Limitations, and Reproducibility](#6-discussion-limitations-and-reproducibility) — Not drafted
- [ ] [7. Conclusion](#7-conclusion) — Not drafted
- [ ] [References](#references) — In progress
- [ ] [Appendix](#appendix) — Not drafted; optional

## Abstract

_Not drafted._

## 1. Introduction

_Not drafted._

## 2. Related Work

_Not drafted._

## 3. Task and Benchmark Construction

**Source graph.** We use the corporate knowledge graph described by [Kirpichev et al. (2026)](https://openreview.net/forum?id=1vQ04i1XGC). It contains S&P 500 companies, sectors, industries, executives, investors, products, resources, locations, and news. Its construction uses corporate data from Yahoo Finance and Wikipedia and news from GDELT.

**Subgraph extraction.** We used Cypher queries to extract instances of the graph patterns from the source knowledge graph. The Cypher queries are provided in the appendix.

**Task sampling.** The core dataset contains 700 tasks: 100 for each of seven graph patterns (motifs): chains, inward and outward stars, inward and outward trees, rhombi, and hourglasses. Each motif has six entities, except for rhombi with four and hourglasses with five. Chain questions follow outgoing links until the first entity of a specified type on each route. Star questions ask for direct incoming or outgoing neighbors. Tree questions follow incoming or outgoing links for two steps; rhombus questions follow outgoing links for two steps. A two-step path ends earlier only when no unvisited neighbor remains in the required direction. Hourglass questions ask for both incoming and outgoing neighbors, reported as separate groups. These seven motifs use six pairs of question templates because outward trees and rhombi share the two-step outgoing query. Motif comparisons therefore involve differences in both graph structure and question type.

**Question construction.** For each sampled subgraph, we instantiated fixed question templates using the starting entity's name and type, the traversal direction, and either a maximum traversal depth or, for chains, a terminal entity type. This deterministic procedure produces two semantically matched formulations of the same graph query:

- **Step-by-step questions** explicitly decompose the traversal into numbered operations: follow the permitted links, apply the stopping rule, and report the distinct endpoints reached.
- **Direct questions** ask for the same endpoints without the numbered decomposition, retaining the direction and stopping rule.

For example, a chain starting from a News entity, represented here by the placeholder name A, and ending at the first Country on each outgoing route has the following question bodies:

- **Step-by-step:** "Starting from News 'A': (1) Follow every outgoing route. (2) Stop each route at its first Country. (3) Report all distinct Country endpoints reached, explaining the supporting links."
- **Direct:** "Starting from News 'A', which Country entities are reached as the first Country on any outgoing route?"

**Selection task.** Each task consists of a question and 25 candidate entities: all entities of the extracted subgraph plus distractors added as noise. The number of distractors is 25 minus the subgraph size. In the core dataset, this gives 19 distractors for six-entity motifs, 21 for rhombi, and 20 for hourglasses. We use two noise variants:

- **Disconnected noise:** all distractors have no edges to subgraph entities in either direction, although they may be connected to one another.
- **Adjacent noise:** up to 10 distractors are neighbors of subgraph entities; the remaining distractors are disconnected from the subgraph.

The paired noise variants retain the same question and reference set but may contain different distractor entities. When graph relations are shown, relations involving distractors are included. Each candidate is presented as a card with a unique name, an entity type, and the facts available in the experimental condition. The model must select all entities that support answering the question and return their names as a set. The reference set consists of all entities in the extracted subgraph.

**Evidence formats.** In the main representation comparison, graph relations are presented as triples or sentences generated from fixed templates. Matched representation variants use the same candidates and relations. We also evaluate original entity descriptions, with and without explicit relations added to the cards. Their selection targets come from the graph; the descriptions alone are not assumed to contain every required relation.

## 4. Experimental Design and Evaluation

**Models and task sets.** We compare Gemma-4-31B, Qwen3.6-Flash, and Ministral-14B-2512. The core dataset contains 100 sampled subgraphs for each of seven motif types, with one base question per subgraph. Each question is presented under 13 experimental conditions, giving 9,100 question instances per model. A second comparison uses 3400 tasks per model under two conditions: **Raw — Original descriptions**, containing the original entity metadata, and **Raw+E — Original descriptions with explicit relations**, adding graph relations to the same cards. Here, E denotes explicit relations. This gives 20,400 evaluations. The expanded dataset includes all 700 core base tasks and 2,700 tasks covering other motif sizes. Within each experiment, each task contributes one final outcome per model, condition, and noise variant; transport retries are not independent repetitions.

**Experimental conditions.** Unless specified otherwise, conditions use pseudonyms, disconnected distractors, a step-by-step question, and facts on source cards. Entity types remain visible throughout. The 13 conditions and their codes are:

- **K1 — Source-card triples:** each directed relation is shown as a triple on its source entity's card. This is the reference setting.
- **K2 — Source-card triples with adjacent distractors:** the same representation with distractors connected to the motif.
- **K3 — Destination-card triples:** each triple appears on its destination entity's card; the relation direction is unchanged.
- **K4 — Triples on both cards:** each triple is duplicated on its source and destination cards.
- **K5 — Templated text:** each relation is expressed as a sentence generated from a fixed template.
- **K6 — Templated text with adjacent distractors:** the same text representation with distractors connected to the motif.
- **K7 — Triples with a direct question:** source-card triples with the step-by-step instructions replaced by a direct question about the same endpoints.
- **K8 — Templated text with a direct question:** the same question change applied to templated text.
- **K5k — Linked attributes:** each card has an identifying value; a relation points to another card through a matching value rather than its name.
- **R1-matched — Real names with triples:** pseudonyms are replaced by real names while retaining the same graph-derived facts.
- **R2-matched — Real names with triples and adjacent distractors:** real names and source-card triples with distractors connected to the motif.
- **R0 — Real names and types only:** cards contain real names and entity types, without descriptions or relation facts.
- **K0 — Pseudonyms and types only:** the same restriction with pseudonyms replacing real names.

The two names-and-types conditions permit prior knowledge about recognizable names and require an insufficient-evidence flag when the connections cannot be established. The remaining conditions restrict evidence to the supplied cards.

**Matched comparisons.** We compare relation representations using K1/K5 and K7/K8, distractor noise using K1/K2 and K5/K6, and question formulations using K1/K7 and K5/K8. K1, K3, and K4 compare fact placement on source cards, on destination cards, and duplication across both cards. We compare real names with pseudonyms using R1-matched/K1 and R2-matched/K2. R0/K0 compares these naming schemes when only names and types are supplied. K5/K5k compares links expressed through entity names with links expressed through matching attribute values.

Representation, wording, placement, and naming comparisons retain the same candidate entities and target set. Distractor comparisons retain the question and target but change the distractor context.

**Response protocol.** Both main comparisons require JSON objects containing a list of candidate names and a flag indicating insufficient evidence. Valid selections require exact, unique candidate names. The flag does not change the set-based scores. For these comparisons, verified Qwen and Ministral requests use OpenRouter, temperature 0, a 1024-token output limit, and JSON-object formatting. Qwen requests explicitly disable reasoning.

**Metrics.** For a valid selected set $S$ and a nonempty target set $T$, precision is $|S\cap T|/|S|$, recall is $|S\cap T|/|T|$, and F1 is $2|S\cap T|/(|S|+|T|)$. Exact match equals one only when $S=T$. An empty selection receives zero on all four metrics. We average individual task scores over the planned number of tasks, retaining invalid and missing outcomes with zero contribution. Reported F1 is therefore the mean of per-task F1 scores. We also report valid-response counts. The paired condition contrasts use matched base tasks; repeated evaluations of a task are not independent samples.

## 5. Results

_Not drafted._

## 6. Discussion, Limitations, and Reproducibility

_Not drafted._

## 7. Conclusion

_Not drafted._

## References

_In progress._ Bibliography entries are maintained in [ARTICLE_REFERENCES.bib](ARTICLE_REFERENCES.bib).

## Appendix

_Not drafted; optional._
