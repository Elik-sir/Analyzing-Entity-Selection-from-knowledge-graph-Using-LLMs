# Entity Selection in Knowledge Graphs: Structural Profiles and Relational Evidence

_Anonymous manuscript._

## Abstract

Selecting connected information is a basic challenge for language-model systems that answer questions about related entities. We study exhaustive entity selection from a fixed knowledge-graph catalogue containing every reference entity, using archived tasks from seven directed families and three language models. We distinguish adding explicit relations from changing the presentation of matched facts and introducing adjacent distractors. Recall measures recovery of all required route entities, with precision and exact recovery providing complementary diagnostics. Across 3,400 matched tasks per model, adding relations increases mean recall by 0.774, 0.519, and 0.567 for Gemma, Qwen, and Ministral. Residual profiles depend on task family, reference size, and model. On controlled six-node incoming-tree tasks, Qwen recall is 0.603 with source-card relations and 0.802 when the same unique facts appear on both endpoint cards; destination-only hosting leaves recall at 0.603. Paired output analyses retain both corrections and regressions. The findings distinguish graph-fact availability from complete entity-route recovery, without asserting an isolated topology effect, an internal traversal mechanism, or downstream answer gains.

## 1 Introduction



Language-model systems can search the Web and use retrieved information to answer questions [^8]. Questions about related entities may require combining textual descriptions with relational information [^10]. For example, a question about a company may involve its products, investors, or related news. In such cases, the model must identify which entities and connections jointly support the requested answer.

Knowledge graphs (KGs) represent such information as entities and directed relations. This motivates a basic selection question: if all required entities and their relations are provided, can an LLM recover the complete set specified by the query? We examine this question in a fixed candidate catalogue containing every reference entity. In the explicit-relation conditions, the links needed to recover that reference are also supplied. Our evaluation focuses on selecting the required entity set as a step toward answering the question.

We study entity selection using a corporate KG developed for GraphRAG evaluation, connecting companies, people, products, locations, and news [^6]. For each query, the selection protocol requires the named anchor, the endpoints, and every intermediate entity on all permitted supporting routes. Selecting only plausible endpoints or one supporting branch does not meet this objective. This route-coverage reference is distinct from a minimum-card evidence set and from the endpoint answer.

The reference is defined by the query's direction and stopping rules and includes every permitted branch. We examine how recovery varies across task families and reference sizes, and how it changes when the availability or presentation of relations varies. The families also differ in query operations, entity types, and relation types, so their profiles describe the studied task configurations rather than isolate a causal effect of topology. Recall measures coverage of the required entities; precision and exact recovery show whether a selection also contains irrelevant entities and whether it matches the complete reference.

Our analysis uses archived outcomes spanning seven task families and three language models. Raw versus Raw+E adds explicit relations to otherwise matched entity cards. Controlled triples, templated prose, and alternative card hosting retain designated unique facts while changing their presentation; both-card hosting additionally changes repetition and input length. Adjacent-context conditions introduce connected but query-irrelevant candidates. Separating these comparisons matters: supplying previously unavailable relations is different from presenting the same facts differently, and native descriptions are not assumed to contain every reference relation.

We ask three questions.

- **RQ1:** How does exhaustive entity-set recovery vary across the studied query families and reference sizes?
- **RQ2:** How does recovery change across paired KG tasks when relation availability, matched-fact presentation, or adjacent distractors vary?
- **RQ3:** Which residual output errors occur when relations are explicit, and how do those outputs change across matched conditions?

The study provides an empirical characterization of complete entity-route selection through task-family and size profiles, paired evidence-availability and presentation comparisons, and localized residual-error diagnostics. The paired analyses separate supplying explicit relations from changing the presentation of designated unique facts. The output-level analyses retain both corrections and regressions on the same tasks. We analyze existing KG tasks and saved outcomes, keeping invalid or missing outcomes in planned denominators for the reported aggregate scores.

The results show that relation disclosure increases coverage, while residual profiles vary across task families and models. On incoming-tree tasks, some high-precision outputs retain only part of the required route set. Presentation variants can correct these outputs but also introduce regressions; a decrease in one error signature need not produce a comparable increase in exact recovery. These observations distinguish the availability of graph facts from complete recovery of the query-defined entity set. They concern selection behavior; final selected sets do not establish an internal traversal procedure or downstream answer correctness.


## 2 Related Work




#### Entity retrieval and knowledge-grounded question answering

RoG organizes KG reasoning through relation-path planning, retrieval, and answer generation [^7]. STaRK evaluates retrieval of answer entities under textual and relational query requirements [^10], while G-Retriever uses prize-collecting Steiner tree optimization to construct graph context for textual graph question answering [^5]. Our evaluation focuses on an exhaustive entity-selection target within a fixed catalogue containing every reference entity. The target includes intermediate entities on all query-permitted supporting routes, extending beyond retrieval of endpoint entities alone. We measure recovery of this declared set directly; minimum sufficient evidence and generated-answer correctness are separate objectives. The corporate graph is reused from Kirpichev et al. [^6].


#### Graph structure, task comprehension, and representation

Talk like a Graph studies how graph encodings, task types, and structure affect language-model performance [^3]. Dai et al. investigate graph-pattern comprehension and discovery using terminological and topological descriptions [^2]. We examine query-specific entity-set recovery across directed task families and reference sizes. This output differs from recognizing a graph-pattern label. Family comparisons retain differences in query operations, direction, entity types, and relation types and are interpreted as conditional selection profiles.


#### Availability and presentation of relational evidence

KG-prompt research examines input formats, triple organization, and noisy or incomplete subgraphs through answer-based evaluation [^1]. We separate relation availability from the presentation of designated unique facts. Raw versus Raw+E adds explicit links to native entity cards; controlled triples, templated prose, and alternative card hosting vary the presentation of matched relations. Native descriptions are not assumed sufficient to recover every graph-defined target. Both-card hosting preserves unique facts but also changes repetition and input length, so its effects do not isolate placement alone.


#### Residual errors and distracting graph context

GraphWalk studies KG navigation and reports incomplete exploration when graph context is supplied directly [^4]. We inspect final selected sets and paired corrections and regressions under matched conditions. These sets characterize observable outcomes without revealing an internal traversal procedure. Disconnected/adjacent comparisons examine query-irrelevant neighboring candidates while retaining the reference and candidate-pool size; the distractor identities and graph density can also change. Adjacency alone does not define irrelevance. Recall, precision, and exact recovery capture incomplete coverage, excess selection, and complete-set correctness, keeping these selection outcomes distinct from downstream answer quality.


## 3 Task, Reference, and Relational Evidence



#### Source graph and historical scope

We reuse the corporate KG snapshot described by Kirpichev et al. [^6], covering S&P 500 companies and associated sectors, industries, executives, investors, products, resources, locations, and news. The authors confirm unchanged snapshot reuse. We analyze the archived, frozen tasks rather than reconstruct their historical database extraction from current software. Appendix B reproduces the author-supplied Cypher extraction specification. It defines fixed small instances and an induced-edge filter; it is not presented as the complete executable pipeline for all archived sizes or per-cell sampling quotas. No database query was executed during this analysis.


### 3.1 Directed Task Families


We study seven directed families: chain, star-in, star-out, tree-in, tree-out, rhombus, and hourglass. Figure 1 gives a compact key alongside Raw/Raw+E recall. Arrows denote factual KG relations; incoming queries inspect them in the reverse direction. Each query names an anchor, which belongs to the all-route selection reference together with the endpoints and intermediate entities. Stars use one-link incoming or outgoing queries; trees and rhombi use two-link routes, ending earlier only at a dead end. Chains stop at the first requested entity type, and hourglass queries request incoming and outgoing one-link groups separately. The Core sizes are six nodes for chain, stars, and trees, four for rhombus, and five for hourglass. Full graph definitions, traversal rules, and the distinction between endpoint answers and selected route entities appear in Appendix C. The families also differ in query operations and entity/relation types.



#### Candidates and distractors

Each main task presents 25 named candidate entities, including the motif entities and distractors. Disconnected distractors have no edges to reference entities in either direction, although they may connect to each other. In the adjacent variant, up to ten distractors are neighbours of motif entities; remaining distractors are disconnected. Paired noise variants retain the question and reference but may contain different distractor identities. Explicit evidence includes relations involving distractors, not only reference-induced edges.


#### Selection target

Let $C$ denote the candidate catalogue and $G_C$ its graph-defined reference context, which need not be recoverable from native cards. Let $q$ be the endpoint query, $a$ its anchor, and $\mathcal{P}(q,G_C)$ its allowed supporting routes under the saved traversal/stopping rule. We evaluate the entity-route reference

$$
W(q,G_C)=\{a\}\ \cup\!\bigcup_{p\in\mathcal{P}(q,G_C)} V(p),
$$

where $V(p)$ contains every entity on route $p$. Endpoint answers $A(q,G_C)$ are distinct from $W$. Simple routes do not revisit an entity; the saved task specification fixes the allowed direction, depth, and terminal-type rule. In the audited structured archive, saved motif/reference IDs coincide with this witness union. Equality is a property of these accepted tasks, not an assumed identity for arbitrary candidate expansion.

For example, one archived rhombus has two branches from the anchor through two intermediate entities to one endpoint. Its endpoint answer has one entity and its reference four. Removing the endpoint card's facts while retaining the name/type catalogue leaves that endpoint recoverable from incoming facts. Thus reference membership does not establish that every card contributes indispensable information. The selection objective is complete route coverage, not minimum sufficient evidence or final answer correctness.


#### Evidence conditions

Raw presents original entity metadata; Raw+E adds explicit relations to the same cards. Actual archived inputs, questions, candidate order, and references match after removing only the relation fields. This is an information-availability contrast; native descriptions are not assumed to express all graph relations. Controlled triples and templated prose instead encode designated matched graph facts. Source-card, destination-card, and both-card variants alter presentation location while retaining relation direction. Names/types remain visible in all conditions. Pseudonyms, direct questions, and linked-attribute encodings provide further diagnostic contrasts detailed in Appendix A.


## 4 Experimental Design and Evaluation



#### Archived models and populations

We analyze Gemma-4-31B, Qwen3.6-Flash, and Ministral-14B as identified in the archive. Core has 700 base tasks, with 100 in each of seven families, under 13 conditions. Five families have six nodes; rhombus and hourglass retain four and five. Full Raw/Raw+E has 3,400 bases per condition/model: chain sizes 3–6, stars 3–10, trees 5–10, rhombus four, and hourglass five, totaling 34 motif-size cells of 100 tasks. All main candidate pools contain 25 entities.

The 700 Core base IDs also occur in Full Raw/Raw+E. Models and conditions reuse base tasks, so counts across panels are not independent replications. Sizes are different frozen cohorts rather than paired expansions of one graph. The separate additional-size and incremental panels are supplementary and are not pooled into the main comparisons.


#### Comparisons

RQ1 uses the Core-size slice of Full Raw/Raw+E for the main motif comparison and the Full size grid for size profiles. Controlled Core source-card triples with disconnected (K1) and adjacent (K2) distractors provide supplementary profiles. RQ2 compares Raw with Raw+E, matched triples with text, and hosting on source, destination, or both cards. K1, K3, and K4 retain a procedural question; K7 uses a direct formulation of the same endpoint query with source-card triples. K5 and K6 are the text counterparts of disconnected and adjacent conditions; K8 uses text with a direct query. Core K-conditions use pseudonyms. Archived inputs establish pairing and fact invariants, independently of current builder defaults.

The RQ2 distractor contrasts are K2 minus K1 and K6 minus K5. RQ3 uses a post-hoc diagnostic slice of six-node Core incoming trees under K1/K2/K3/K4/K7, retaining 100 planned tasks per model and condition. Saved Qwen/Ministral selections support identity-level comparisons; Gemma contributes cached aggregate scores but lacks the identities required for those diagnostics.


#### Responses and evidence coverage

The main protocol requests JSON with selected catalogue names and an insufficient-evidence flag. Valid selections contain exact, unique candidate names; the flag does not modify set scores. Available Qwen/Ministral records specify OpenRouter, temperature zero, a 1,024-token limit, and JSON-object formatting. Missing Gemma settings are not filled from current defaults. Some controlled Gemma outcomes retain cached individual metrics without original replies or selected identities; these support aggregate recall, precision, and exact recovery, but not identity-level route signatures. Full Raw/Raw+E has stronger reply coverage. Missing and invalid outcomes remain in planned denominators.


#### Primary and additional metrics

For selected set $S$ and nonempty route reference $W$, we use

$$
R(S,W)=\frac{|S\cap W|}{|W|},\qquad
 P(S,W)=\frac{|S\cap W|}{|S|}.
$$

An empty selection receives zero recall and precision. Recall is primary because the selection target requires complete route coverage. Precision measures excess selection; exact recovery is one only when $S=W$. We report macro means of individual scores over all planned outcomes, with invalid/missing outcomes contributing zero. Thus scores also reflect protocol reliability; they are not pooled micro ratios or valid-only summaries. Reference coverage is distinct from endpoint-answer correctness and minimal sufficient evidence.


#### Analysis and uncertainty scope

The figures and tables use saved aggregate scores and existing bounded selection diagnostics; this revision launches no model, judge, or database calls. Core condition contrasts match 700 bases per model; Raw/Raw+E matches 3,400. Differences are right-minus-left macro means on these complete paired populations, computed before rounding. Source-row mappings reproduce the existing paired export. Recall/precision profiles and contrasts are descriptive: no new confidence intervals, significance claims, or motif-by-condition tests are introduced. Earlier uncertainty estimates cover F1/exact, and are not transferred to recall. Repeated anchors and shared entities further restrict population inference.


## 5 Results



### 5.1 Structural Profiles: Motif and Size


![Figure 1](C:/Users/ekurm/projects/Analyzing-Entity-Selection-from-knowledge-graph-Using-LLMs/paper/figures/motif_raw_recall_bars_v1/motifs_and_raw_recall_bars.png)

**Figure 1.** Directed task families and recall. Left: representative Core motif shapes; blue nodes mark anchors and arrows show factual KG direction. Right: grouped macro recall for the Core-size slice of Full Raw/Raw+E. Each motif has three model pairs; hatched Raw and solid Raw+E bars are adjacent within each model color. Each bar retains 100 planned tasks, with matched Raw/Raw+E pairs and 25 candidates. Families a–e have six reference nodes; shaded f/g have four/five. Invalid or missing outcomes contribute zero. Full definitions are in Appendix C. No inferential error bars are shown.

Figure 1 compares Raw and Raw+E recovery using the Core-size slice of the Full panel. Adding explicit relations yields higher descriptive recall in every displayed family for all three models. Residual coverage still differs by task family and model: incoming trees have lower Raw+E recall than outward stars for each model. These conditional profiles also vary in query semantics and entity/relation types, so they do not isolate a topology effect. The controlled Core K1/K2 profiles and their precision companion are retained in Appendix A.1.


![Figure 2](C:/Users/ekurm/projects/Analyzing-Entity-Selection-from-knowledge-graph-Using-LLMs/paper/figures/recall_manuscript_v1/recall_sizes.png)

**Figure 2.** Recall across all variable-size families and all three models in Full Raw/Raw+E. Each point has 100 planned tasks and 25 candidates, with invalid outcomes contributing zero. Raw+E adds relations. Sizes are different frozen cohorts, not paired expansions; target prevalence and distractor count change with size. No universal monotonicity or isolated size effect is claimed.

Size sensitivity also depends on family and model (Figure 2). Under Raw+E, chain recall changes from 0.990 at three nodes to 0.790 at six for Qwen, and from 0.927 to 0.595 for Ministral. Gemma changes from 0.990 to 1.000. Outward stars provide contrary profiles: Qwen changes from 0.997 at three nodes to 0.998 at ten, Gemma remains at 1.000, and Ministral changes from 0.870 to 0.950. These comparisons describe different accepted cohorts, not beneficial or harmful effects of adding a node to the same task.

Incoming-tree Raw+E recall is lower at ten than five nodes for all three models: 0.910 to 0.841, 0.624 to 0.375, and 0.540 to 0.403 for Gemma, Qwen, and Ministral. Intermediate values need not be monotonic. The fixed candidate pool also changes the proportion of reference entities as size increases. We therefore report the full profiles, including exceptions, rather than treating node count as an intrinsic complexity coefficient.


### 5.2 Relation Availability and Matched-Fact Presentation


**Table 1.** Descriptive paired changes in mean recall. Columns: Raw+E minus Raw (3,400 pairs/model); adjacent minus disconnected triples/text; text minus triples for procedural/direct queries; destination minus source; both cards minus source; direct minus procedural query (700 pairs/model for these Core contrasts). All planned outcomes are retained. No recall confidence intervals or significance tests were computed.

| Model | Raw+E | Adj. triples | Adj. text | Text steps | Text direct | Dest. | Both | Direct query |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gemma | +0.774 | -0.011 | -0.015 | -0.002 | -0.006 | +0.000 | -0.003 | +0.001 |
| Qwen | +0.519 | -0.071 | -0.064 | -0.035 | -0.035 | +0.005 | +0.059 | -0.003 |
| Ministral | +0.567 | -0.072 | -0.045 | -0.001 | -0.002 | -0.043 | -0.006 | -0.016 |

Explicit relation disclosure substantially increases recall (Table 1). Raw/Raw+E mean recall changes from 0.198 to 0.972 for Gemma, 0.278 to 0.798 for Qwen, and 0.218 to 0.785 for Ministral. The gains are 0.774, 0.519, and 0.567. Precision changes from 0.859 to 0.988, 0.885 to 0.975, and 0.459 to 0.976, respectively. High Raw precision can therefore coexist with low route coverage. Since native metadata is not verified sufficient for every route, low Raw recall is not automatically a failure to reason from available facts.

Matched-fact representation gives a more restricted diagnostic. Text-minus-triples recall differences for Qwen are $-0.035$ under both procedural and direct queries after rounding. Gemma and Ministral have smaller descriptive differences in those comparisons. Hosting effects are model-specific: duplicating facts yields a Qwen aggregate recall gain of 0.059, whereas Gemma and Ministral do not show the same positive direction. These are point estimates, not equivalence findings or newly tested interactions.


**Table 2.** Mean recall on six-node Tree-in tasks: one model per row, conditions in columns. K1/K3/K4 host triples on source/destination/both cards with a procedural query; K7 uses source cards and a direct query. Each cell retains 100 planned tasks. Ministral has 99 valid outcomes in K3 and 91 in K7; every other cell has 100. Invalid outcomes contribute zero.

| Model | K1 | K3 | K4 | K7 |
| --- | --- | --- | --- | --- |
| Gemma | 0.972 | 0.983 | 0.982 | 0.982 |
| Qwen | 0.603 | 0.603 | 0.802 | 0.660 |
| Ministral | 0.853 | 0.787 | 0.908 | 0.837 |

The focused incoming-tree comparison illustrates why aggregate changes need localization (Table 2). Qwen's recall is 0.603 with source or destination hosting, 0.802 with both-card hosting, and 0.660 with a direct query. Ministral reaches 0.908 with both-card hosting, but destination hosting yields 0.787 versus 0.853 at source. Gemma remains near complete coverage in all four conditions. Thus moving incoming relations to destination cards does not universally improve selection, and a presentation change can affect models differently despite matched unique facts.

Saved Qwen selections provide an additional output-level check: 71 of 100 K1 incoming-tree outputs equal the anchor plus its first incoming neighbourhood. Under K4, 38 of those 71 become exact, while six of the 15 initially exact outputs lose exactness. Under K7, the one-hop count falls to 52, but total exact recovery changes only from 15 to 16. A reduction in one error signature can therefore include substitution into other errors. This is a post-hoc diagnostic of final sets, not a record of internal stopping; Gemma lacks the selected identities needed for this particular check.


### 5.3 Adjacent Contexts

Adjacent-minus-disconnected recall differences are negative for all three models in both triples and text contrasts (Table 1). The motif profiles show where coverage remains incomplete under these conditions (Figure 3). Distractor identities and graph density also change in the paired noise variants. We therefore interpret these as archived context contrasts, not isolated causal effects of adjacency or evidence of a universal motif-by-noise interaction.


## 6 Discussion and Limitations



#### Availability and complete recovery

The Raw/Raw+E comparison shows that supplying explicit relations is associated with much stronger recovery of the declared entity-route reference on the matched archived tasks. Native metadata may omit the required links, so low Raw recall cannot by itself establish a reasoning error on sufficient evidence. The remaining errors under explicit relations pose a different question: whether the model retains the complete set specified by the query. High precision with incomplete recall shows that a mostly reference-consistent selection can still omit required route entities.


#### Interpreting structural profiles

Task-family differences remain visible at common sizes, while size profiles vary by family and model. These observations motivate reporting selection performance by query family and evidence condition. They do not establish a universal motif ranking or an isolated topology coefficient: families also differ in traversal direction, stopping rules, relation types, and sampled entities. Different sizes use different cohorts, and the fixed catalogue changes target prevalence and distractor count as reference size increases.


#### Presentation and residual errors

Repeated first-neighborhood outputs provide a localized description of some incoming-tree errors. Their paired transitions show why a marginal reduction in an error signature is insufficient: an output may become exact, remain incomplete, or change to another error. These are observations of final sets, not evidence of hidden search depth or internal stopping. Their detailed scope is the inspected Core incoming-tree slice rather than all families and sizes.

Both-card hosting motivates a hypothesis about access to distributed facts, but also changes repetition, salience, and input length. Destination-only hosting does not produce the same pattern across models. Separating these explanations would require controls that hold repetition and length fixed while varying hosting. Likewise, adjacent-context differences can involve distractor identities and graph density as well as adjacency. The archived comparisons do not identify a unique attention, traversal, or discrimination mechanism.


#### What the selection objective identifies

We score the union of allowed route vertices, including the anchor. This is distinct from minimal graph support, indispensable visible cards, and correct endpoint answers. A smaller selection may suffice for an endpoint answer even when it fails the route-coverage convention. High recall alone also permits selecting everything, which has recall one by construction; precision and exact are therefore necessary companion diagnostics.

Some rule violations are observationally indistinguishable in simple contexts. On the 100 inspected Qwen K1 six-node incoming-tree inputs, ignoring direction or increasing the depth bound from two to three produces the same coverage set as the correct rule. Correct final sets in that slice cannot establish adherence to those rules. Adjacent contexts can supply distinguishing cases, but different rules have different diagnostic support. A full anchor-connected-component baseline has not been measured; neither ideal performance by that heuristic nor the absence of shortcuts is claimed.


#### Scope and reproducibility

The study covers one reused corporate KG [^6] and frozen model/protocol labels, with no generation-seed replication or new KG evaluation. It reanalyzes existing tasks and saved outcomes; it does not introduce a newly collected dataset or independent experimental replication. Base tasks, anchors, and reference entities overlap, so descriptive averages do not remove dependence. We introduce no recall/precision significance or population-causal claims.

Frozen-reference checks establish consistency of the presented tasks, not completeness against the unloaded source database. Missing Gemma replies/settings, native sufficiency, and incremental histories remain limitations. Saved rows, selectors, denominators, hashes, and plotting scripts support reproduction of these summaries; resource redistribution and graph access are separate matters.


#### Responsibility and downstream scope

This study does not evaluate a new human-subject population or establish downstream QA improvement. Generative AI assistance supported evidence organization, plotting code, and manuscript drafting; experimental values derive from saved outcomes. Authors remain responsible for source verification, anonymity, resource permissions, and the provenance of reused materials.


## 7 Conclusion


This study characterizes exhaustive entity selection from fixed KG catalogues using existing tasks and saved outcomes. Explicit relations increase reference coverage, while residual omissions vary across task families, sizes, and models. Matched-fact presentation changes produce both corrections and regressions, and adjacent irrelevant context reduces recall in the archived comparisons. The results distinguish access to graph facts from recovery of every required route entity. They support evaluating completeness, excess selection, and exact recovery together, while keeping task-family confounds, limited diagnostic scope, and archived-evidence coverage visible. The observations concern entity selection and do not establish a universal complexity ranking, an internal traversal mechanism, or downstream answer gains.




## References

[^1]: Dai, Xinbang; Hua, Yuncheng; Wu, Tongtong; Sheng, Yang; Ji, Qiu; Qi, Guilin. (2024). *Large Language Models Can Better Understand Knowledge Graphs Than We Thought*. [Source](https://arxiv.org/abs/2402.11541v4).

[^2]: Dai, Xinnan; Qu, Haohao; Shen, Yifei; Zhang, Bohang; Wen, Qihao; Fan, Wenqi; Li, Dongsheng; Tang, Jiliang; Shan, Caihua. (2025). *How Do Large Language Models Understand Graph Patterns? A Benchmark for Graph Pattern Comprehension*. [Source](https://proceedings.iclr.cc/paper_files/paper/2025/hash/9316da9c25ab559ba678f2fe52217a64-Abstract-Conference.html).

[^3]: Fatemi, Bahare; Halcrow, Jonathan; Perozzi, Bryan. (2024). *Talk like a Graph: Encoding Graphs for Large Language Models*. [Source](https://proceedings.iclr.cc/paper_files/paper/2024/hash/bf72f65f30eedf5d48da6980ee02b589-Abstract-Conference.html).

[^4]: Ghandi, Taraneh; Mahyar, Hamidreza; Klaiman, Shachar. (2026). *GraphWalk: Enabling Reasoning in Large Language Models through Tool-Based Graph Navigation*. [Source](https://arxiv.org/abs/2604.01610v1).

[^5]: He, Xiaoxin; Tian, Yijun; Sun, Yifei; Chawla, Nitesh V.; Laurent, Thomas; LeCun, Yann; Bresson, Xavier; Hooi, Bryan. (2024). *G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering*. [Source](https://papers.nips.cc/paper_files/paper/2024/hash/efaf1c9726648c8ba363a5c927440529-Abstract-Conference.html).

[^6]: Kirpichev, Ivan E.; Kurmanaliev, Eldar R.; Bushmelev, Fedor V.; Abramov, Maxim V.; Korepanova, Anastasiia A.; Nikitin, Nikolay O.; Kalyuzhnaya, Anna V.. (2026). *Towards Ontology-Driven Multi-Hop Benchmark for Corporate GraphRAG Systems*. [Source](https://openreview.net/forum?id=1vQ04i1XGC).

[^7]: Luo, Linhao; Li, Yuan-Fang; Haffari, Gholamreza; Pan, Shirui. (2024). *Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning*. [Source](https://proceedings.iclr.cc/paper_files/paper/2024/hash/3e2aeb66481dd63a32421bf032b70384-Abstract-Conference.html).

[^8]: Nakano, Reiichiro; Hilton, Jacob; Balaji, Suchir; Wu, Jeff; Ouyang, Long; Kim, Christina; Hesse, Christopher; Jain, Shantanu; Kosaraju, Vineet; Saunders, William; Jiang, Xu; Cobbe, Karl; Eloundou, Tyna; Krueger, Gretchen; Button, Kevin; Knight, Matthew; Chess, Benjamin; Schulman, John. (2021). *WebGPT: Browser-assisted question-answering with human feedback*. [Source](https://arxiv.org/abs/2112.09332v3).

[^9]: Neo4j. (n.d.). *Cypher Manual: MATCH*. [Source](https://neo4j.com/docs/cypher-manual/current/clauses/match/).

[^10]: Wu, Shirley; Zhao, Shiyu; Yasunaga, Michihiro; Huang, Kexin; Cao, Kaidi; Huang, Qian; Ioannidis, Vassilis N.; Subbian, Karthik; Zou, James; Leskovec, Jure. (2024). *STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases*. [Source](https://papers.nips.cc/paper_files/paper/2024/hash/e607b1419e9ae7cd5cb5b5bb60c2ad5c-Abstract-Datasets_and_Benchmarks_Track.html).



## Appendices


## A Additional Metrics and Condition Definitions


Core uses pseudonyms, procedural questions, and disconnected distractors unless specified. K1 is source-card triples; K2 adds adjacent distractors; K3 hosts triples on destination cards; K4 repeats them on both endpoint cards. K5 is templated text; K6 is its adjacent variant. K7/K8 use direct queries with triples/text. K5k expresses links through matching attribute values. R1-matched/R2-matched use real names with disconnected/adjacent triples. R0/K0 retain names/types only. Their prompt permits prior name knowledge and requests an insufficient-evidence flag; other controlled conditions restrict evidence to supplied cards.

Fact-preserving pairs retain designated unique relations and targets. Noise pairs retain the question/reference while altering distractor context. A change in presentation may still alter repetition, salience, and token length. Native metadata is not assumed sufficient for every graph-defined target.


### A.1 Controlled Core Profiles



![Figure 3](C:/Users/ekurm/projects/Analyzing-Entity-Selection-from-knowledge-graph-Using-LLMs/paper/figures/recall_manuscript_v1/recall_motifs.png)

**Figure 3.** Core recall with explicit source-card relations: K1 disconnected and K2 adjacent distractors, 100 planned tasks per point. The first five families have six nodes; shaded rhombus/hourglass use four/five and are not equal-size contrasts. Invalid outcomes contribute zero. These are descriptive macro means, without inferential error bars.


Figure 3 shows task-family differences, including five families at the common six-node reference size. Under K1, six-node incoming-tree recall is 0.972 for Gemma, 0.603 for Qwen, and 0.853 for Ministral. Outward stars are close to complete coverage. The common size does not eliminate differences in query semantics, relation types, or sampled entities; it rules out a node-count-only description of these observed task profiles, not every competing explanation.

Precision supplies a different view. Qwen's K1 incoming-tree precision is 0.988, despite recall of 0.603 and exact recovery of 0.150. It often selects a small, mostly reference-consistent set while failing to cover the reference. Gemma's corresponding precision is 1.000 and exact 0.870. Appendix A reports precision profiles separately rather than combining the two quantities into one F1 curve.


![Figure 4](C:/Users/ekurm/projects/Analyzing-Entity-Selection-from-knowledge-graph-Using-LLMs/paper/figures/recall_manuscript_v1/precision_motifs.png)

**Figure 4.** Precision companion to Figure 3: Core K1/K2, 100 planned tasks per point, invalid zero. Shaded families have different sizes. High precision can coexist with incomplete coverage; this is a descriptive saved-score profile without confidence intervals.


![Figure 5](C:/Users/ekurm/projects/Analyzing-Entity-Selection-from-knowledge-graph-Using-LLMs/paper/figures/recall_manuscript_v1/precision_sizes.png)

**Figure 5.** Precision companion to Figure 2, retaining all three models and five variable-size families under Raw/Raw+E. Each point has 100 planned tasks; invalid contributes zero. Size cohorts differ and no curve is interpreted as a causal graph expansion.



**Table 3.** All Core condition means: recall, with 700 planned outcomes per model/condition and invalid zero. These are descriptive macro means.

| Condition | Gemma | Qwen | Ministral |
| --- | --- | --- | --- |
| K0 | 0.182 | 0.189 | 0.299 |
| K1 | 0.996 | 0.892 | 0.957 |
| K2 | 0.985 | 0.820 | 0.885 |
| K3 | 0.996 | 0.896 | 0.914 |
| K4 | 0.993 | 0.951 | 0.950 |
| K5 | 0.993 | 0.857 | 0.956 |
| K6 | 0.979 | 0.794 | 0.911 |
| K7 | 0.996 | 0.888 | 0.941 |
| K8 | 0.990 | 0.853 | 0.939 |
| K5k | 0.988 | 0.850 | 0.918 |
| R0 | 0.322 | 0.282 | 0.298 |
| R1-matched | 0.985 | 0.817 | 0.844 |
| R2-matched | 0.973 | 0.750 | 0.762 |


**Table 4.** Precision counterpart to Table 3, using the same planned populations and failure policy.

| Condition | Gemma | Qwen | Ministral |
| --- | --- | --- | --- |
| K0 | 0.994 | 0.974 | 0.130 |
| K1 | 1.000 | 0.992 | 0.983 |
| K2 | 0.983 | 0.957 | 0.791 |
| K3 | 0.999 | 0.992 | 0.976 |
| K4 | 0.996 | 0.996 | 0.950 |
| K5 | 0.999 | 0.992 | 0.980 |
| K6 | 0.974 | 0.958 | 0.751 |
| K7 | 1.000 | 0.989 | 0.971 |
| K8 | 1.000 | 0.993 | 0.991 |
| K5k | 0.996 | 0.987 | 0.965 |
| R0 | 0.936 | 0.861 | 0.391 |
| R1-matched | 0.991 | 0.992 | 0.979 |
| R2-matched | 0.984 | 0.958 | 0.838 |



#### Output signatures and diagnostic limits

An exact one-hop signature means the saved selection equals the anchor plus all permitted first-hop neighbours. On the inspected Qwen K1 six-node incoming-tree tasks, this occurs in 71/100 outputs; K3/K4/K7 have 76/31/52. Their exact-reference counts are 16/51/16, compared with 15 in K1. This distinguishes elimination of a signature from correction of the task. All these Qwen cells have 100 valid outcomes. The same original 71 one-hop outputs become exact on 13 K3, 38 K4, and ten K7 tasks. Under K4, six initially exact outputs lose exactness. No new interval or significance test is attached to these post-hoc contrasts.

Ministral has 15/100 initial one-hop sets and 54/100 exact outputs in K1. K4 makes eight of those one-hop sets exact and loses exactness on nine initially exact tasks; total exact recovery is 62/100. Gemma's aggregate scores remain in all main tables/figures, but the archive lacks identities for this finer check. Output signatures do not prove hidden search depth or branch order.

On the inspected Qwen K1 incoming-tree inputs, undirected depth-two and directed depth-three coverage agree with the correct reference on all 100 tasks. Under K2 these alternative targets differ on 97/100 and 10/100 tasks, respectively; no Qwen output exactly matches those distinct alternative sets. This does not rule out mixed or partial rule violations. This slice has no terminal-type stopping condition, so it cannot diagnose terminal-type errors.


#### Analytical and uncertainty context

Select-all has recall one on every nonempty reference by definition, and precision equal to the reference proportion in the 25-candidate pool. These are analytical reference rules, not executed LLM/retrieval baselines. A full connected-component baseline was not computed. Earlier archive uncertainty analyses cover F1/exact with anchor-conditional assumptions; no such bands are reused for the present recall/precision results. Original exact scores, earlier metrics, native/legacy panels, and incomplete incremental histories remain in the supporting source artifacts rather than being pooled into the main populations.


## B Author-Supplied Cypher Extraction Specification


The following Cypher query was supplied by the authors for the appendix. Whitespace is normalized and comments are translated into English for display; executable tokens match the saved original. It enumerates small instances of nine directed pattern definitions, requires distinct vertices, and excludes additional directed typed edges inside each selected vertex set, including self-loops. The comparison uses source/type/target triples, so parallel physical relationships with the same triple are not distinguished by the extra-edge test.

This specification has fixed sizes: four-node chains/stars/rhombi, five-node trees/hourglasses, and three-node cycles/cliques. Its final `LIMIT 100` is global, not a quota per motif or size. It does not specify random sampling, seeds, candidate expansion, type/name acceptance filters, or the complete archived size grid. The presence of cycle/clique branches defines queries, not observed cycle/clique outcomes in the seven-family study. No result from executing these queries is claimed. These boundaries prevent equating the supplied query with a fully reconstructed historical pipeline. Cypher syntax is documented by Neo4j [^9].

```cypher
CALL {
// Chain, four nodes.
    MATCH (a)-[r1]->(b)-[r2]->(c)-[r3]->(d)
    RETURN 'chain' AS motif, [a,b,c,d] AS ns, [r1,r2,r3] AS rs
    UNION ALL
// Outward star, four nodes.
    MATCH (h)-[r1]->(a), (h)-[r2]->(b), (h)-[r3]->(c)
    WHERE elementId(a) < elementId(b) AND elementId(b) < elementId(c)
    RETURN 'star_out' AS motif, [h,a,b,c] AS ns, [r1,r2,r3] AS rs
    UNION ALL
// Inward star, four nodes.
    MATCH (a)-[r1]->(h), (b)-[r2]->(h), (c)-[r3]->(h)
    WHERE elementId(a) < elementId(b) AND elementId(b) < elementId(c)
    RETURN 'star_in' AS motif, [h,a,b,c] AS ns, [r1,r2,r3] AS rs
    UNION ALL
// Outward tree, five nodes.
    MATCH (h)-[r1]->(a)-[r3]->(c), (h)-[r2]->(b)-[r4]->(d)
    WHERE elementId(a) < elementId(b)
    RETURN 'tree_out' AS motif, [h,a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
// Inward tree, five nodes.
    MATCH (c)-[r3]->(a)-[r1]->(h), (d)-[r4]->(b)-[r2]->(h)
    WHERE elementId(a) < elementId(b)
    RETURN 'tree_in' AS motif, [h,a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
// Rhombus, four nodes.
    MATCH (a)-[r1]->(b)-[r3]->(d), (a)-[r2]->(c)-[r4]->(d)
    WHERE elementId(b) < elementId(c)
    RETURN 'rhombus' AS motif, [a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
// Hourglass, five nodes.
    MATCH (a)-[r1]->(m), (b)-[r2]->(m), (m)-[r3]->(c), (m)-[r4]->(d)
    WHERE elementId(a) < elementId(b) AND elementId(c) < elementId(d)
    RETURN 'hourglass' AS motif, [m,a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
// Directed cycle, three nodes.
    MATCH (a)-[r1]->(b)-[r2]->(c)-[r3]->(a)
    WHERE elementId(a) < elementId(b) AND elementId(a) < elementId(c)
    RETURN 'cycle' AS motif, [a,b,c] AS ns, [r1,r2,r3] AS rs
    UNION ALL
// Bidirected clique, three nodes.
    MATCH (a)-[r1]->(b), (b)-[r2]->(a), (a)-[r3]->(c), (c)-[r4]->(a),
          (b)-[r5]->(c), (c)-[r6]->(b)
    WHERE elementId(a) < elementId(b) AND elementId(b) < elementId(c)
    RETURN 'clique' AS motif, [a,b,c] AS ns, [r1,r2,r3,r4,r5,r6] AS rs
}
// Require distinct nodes.
WITH motif, ns, rs
WHERE all(n IN ns WHERE single(x IN ns WHERE x = n))
// Represent edges as source, type, target triples.
WITH motif, ns,
     [r IN rs | [elementId(startNode(r)), type(r), elementId(endNode(r))]] AS edges
// Reject any additional typed induced edge,
// including self-loops.
WHERE NOT EXISTS {
    MATCH (u)-[extra]->(v)
    WHERE u IN ns AND v IN ns
      AND NOT ([elementId(u), type(extra), elementId(v)] IN edges)
}
RETURN DISTINCT motif,
       [n IN ns | elementId(n)] AS node_ids,
       [n IN ns | coalesce(n.name, n.headline, n.title, n.ticker)] AS node_names,
       edges
LIMIT 100;
```

The supplementary files include the existing queries for exporting nodes and edges and separately labelled, newly written frozen-instance checks. These supplementary files were not used to generate the reported outcomes. Graph-export code is not itself historical motif-extraction evidence. Query IDs and role bindings refer to the same database snapshot; `elementId` is not a portable cross-snapshot identifier.


## C Directed Motifs and Query Rules



We use seven directed task families, shown in the compact key in Figure 1. Each query names an anchor $a$. An arrow $u\to v$ denotes a factual KG relation from $u$ to $v$; an incoming query examines this relation from $v$ toward $u$ without changing its direction. The endpoint answer set $A$ contains the entities returned by the query rule. The evaluated selection reference $W$ additionally includes the anchor and all intermediate entities on every permitted supporting route.


#### Chain

A directed path starts at the anchor. The query follows outgoing routes and stops at the first entity of the requested terminal type on each route. In the representative chain, the final vertex is that first matching entity; the vertices between the anchor and the final vertex are intermediate selections. The stopping rule is type-based, not a fixed two-link limit.


#### Star-in and star-out

The anchor is the common destination of the star-in edges and the common source of the star-out edges. The query requests all immediate incoming or outgoing neighbors, respectively. These neighbors are endpoint answers, while the anchor is additionally included in $W$.


#### Tree-in and tree-out

These families have two levels relative to the anchor, with at least two first-level branches and at least one second-level entity per branch. Tree-in edges point toward the anchor, while tree-out edges point away from it. The query inspects incoming or outgoing routes up to two links. A route ends earlier only when no further permitted unvisited neighbor is available. Second-level entities are endpoints in the representative Core examples; both levels and the anchor belong to $W$.


#### Rhombus

Four vertices form two outgoing two-link routes, $a\to b\to d$ and $a\to c\to d$. The endpoint answer is the shared vertex $d$, while $W=\{a,b,c,d\}$. Both intermediate vertices are required by the all-route selection convention even though the routes reach the same endpoint.


#### Hourglass

The central anchor has two incoming and two outgoing neighbors. The question requests these two one-link groups separately. The four neighbors are endpoint answers and all five vertices belong to $W$. The task does not ask for a two-link traversal from an incoming neighbor through the anchor to an outgoing neighbor.

The Core panel contains 100 base tasks per family: six nodes for chain, stars, and trees, four for rhombus, and five for hourglass; the size panel varies the supported chain, star, and tree sizes. Question templates use the anchor's name/type and the traversal/stopping rule. Procedural and direct formulations express the same endpoint query. Families therefore differ in query operations as well as directed structure, so their unadjusted profiles do not isolate a causal topology effect.
