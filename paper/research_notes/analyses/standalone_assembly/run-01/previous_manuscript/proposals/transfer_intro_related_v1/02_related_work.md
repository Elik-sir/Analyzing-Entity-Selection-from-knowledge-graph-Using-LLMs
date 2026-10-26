# Related Work

## Entity retrieval and knowledge-grounded question answering

RoG organizes KG reasoning through relation-path planning, retrieval, and answer generation[^rog]. STaRK evaluates retrieval of answer entities under textual and relational query requirements[^stark], while G-Retriever uses prize-collecting Steiner tree optimization to construct graph context for textual graph question answering[^gretriever]. Our evaluation focuses on an exhaustive entity-selection target within a fixed catalogue containing every reference entity. The target includes intermediate entities on all query-permitted supporting routes, extending beyond retrieval of endpoint entities alone. We measure recovery of this declared set directly; minimum sufficient evidence and generated-answer correctness are separate objectives. The corporate graph is reused from Kirpichev et al.[^corporatekg].

## Graph structure, task comprehension, and representation

Talk like a Graph studies how graph encodings, task types, and structure affect language-model performance[^talkgraph]. Dai et al. investigate graph-pattern comprehension and discovery using terminological and topological descriptions[^patterns]. We examine query-specific entity-set recovery across directed task families and reference sizes. This output differs from recognizing a graph-pattern label. Family comparisons retain differences in query operations, direction, entity types, and relation types and are interpreted as conditional selection profiles.

## Availability and presentation of relational evidence

KG-prompt research examines input formats, triple organization, and noisy or incomplete subgraphs through answer-based evaluation[^kgunderstanding]. We separate relation availability from the presentation of designated unique facts. Raw versus Raw+E adds explicit links to native entity cards; controlled triples, templated prose, and alternative card hosting vary the presentation of matched relations. Native descriptions are not assumed sufficient to recover every graph-defined target. Both-card hosting preserves unique facts but also changes repetition and input length, so its effects do not isolate placement alone.

## Residual errors and distracting graph context

GraphWalk studies KG navigation and reports incomplete exploration when graph context is supplied directly[^graphwalk]. We inspect final selected sets and paired corrections and regressions under matched conditions. These sets characterize observable outcomes without revealing an internal traversal procedure. Disconnected/adjacent comparisons examine query-irrelevant neighboring candidates while retaining the reference and candidate-pool size; the distractor identities and graph density can also change. Adjacency alone does not define irrelevance. Recall, precision, and exact recovery capture incomplete coverage, excess selection, and complete-set correctness, keeping these selection outcomes distinct from downstream answer quality.

[^rog]: Luo et al. *Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning*. [Paper](https://proceedings.iclr.cc/paper_files/paper/2024/hash/3e2aeb66481dd63a32421bf032b70384-Abstract-Conference.html).

[^stark]: Wu et al. *STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases*. [Paper](https://papers.nips.cc/paper_files/paper/2024/hash/e607b1419e9ae7cd5cb5b5bb60c2ad5c-Abstract-Datasets_and_Benchmarks_Track.html).

[^gretriever]: He et al. *G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering*. [Paper](https://papers.nips.cc/paper_files/paper/2024/hash/efaf1c9726648c8ba363a5c927440529-Abstract-Conference.html).

[^corporatekg]: Kirpichev et al. *Towards Ontology-Driven Multi-Hop Benchmark for Corporate GraphRAG Systems*. [Paper](https://openreview.net/forum?id=1vQ04i1XGC).

[^talkgraph]: Fatemi et al. *Talk like a Graph: Encoding Graphs for Large Language Models*. [Paper](https://proceedings.iclr.cc/paper_files/paper/2024/hash/bf72f65f30eedf5d48da6980ee02b589-Abstract-Conference.html).

[^patterns]: Dai et al. *How Do Large Language Models Understand Graph Patterns? A Benchmark for Graph Pattern Comprehension*. [Paper](https://arxiv.org/abs/2410.05298v2).

[^kgunderstanding]: Dai et al. *Large Language Models Can Better Understand Knowledge Graphs Than We Thought*. [Paper](https://arxiv.org/abs/2402.11541v4).

[^graphwalk]: Ghandi et al. *GraphWalk: Enabling Reasoning in Large Language Models through Tool-Based Graph Navigation*. [Paper](https://arxiv.org/abs/2604.01610v1).
