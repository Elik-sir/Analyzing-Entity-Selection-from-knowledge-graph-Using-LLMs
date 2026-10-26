# Introduction

Language-model systems can search the Web and use retrieved information to answer questions[^webgpt]. Questions about related entities may require combining textual descriptions with relational information[^stark]. For example, a question about a company may involve its products, investors, or related news. In such cases, the model must identify which entities and connections jointly support the requested answer.

Knowledge graphs (KGs) represent such information as entities and directed relations. This motivates a basic selection question: if all required entities and their relations are provided, can an LLM recover the complete set specified by the query? We examine this question in a fixed candidate catalogue containing every reference entity. In the explicit-relation conditions, the links needed to recover that reference are also supplied. Our evaluation focuses on selecting the required entity set as a step toward answering the question.

We study entity selection using a corporate KG developed for GraphRAG evaluation, connecting companies, people, products, locations, and news[^corporatekg]. For each query, the selection protocol requires the named anchor, the endpoints, and every intermediate entity on all permitted supporting routes. Selecting only plausible endpoints or one supporting branch does not meet this objective. This route-coverage reference is distinct from a minimum-card evidence set and from the endpoint answer.

The reference is defined by the query's direction and stopping rules and includes every permitted branch. We examine how recovery varies across task families and reference sizes, and how it changes when the availability or presentation of relations varies. The families also differ in query operations, entity types, and relation types, so their profiles describe the studied task configurations rather than isolate a causal effect of topology. Recall measures coverage of the required entities; precision and exact recovery show whether a selection also contains irrelevant entities and whether it matches the complete reference.

Our analysis uses archived outcomes spanning seven task families and three language models. Raw versus Raw+E adds explicit relations to otherwise matched entity cards. Controlled triples, templated prose, and alternative card hosting retain designated unique facts while changing their presentation; both-card hosting additionally changes repetition and input length. Adjacent-context conditions introduce connected but query-irrelevant candidates. Separating these comparisons matters: supplying previously unavailable relations is different from presenting the same facts differently, and native descriptions are not assumed to contain every reference relation.

We ask three questions.

- **RQ1:** How does exhaustive entity-set recovery vary across the studied query families and reference sizes?
- **RQ2:** How does recovery change across paired KG tasks when relation availability, matched-fact presentation, or adjacent distractors vary?
- **RQ3:** Which residual output errors occur when relations are explicit, and how do those outputs change across matched conditions?

The study provides an empirical characterization of complete entity-route selection through task-family and size profiles, paired evidence-availability and presentation comparisons, and localized residual-error diagnostics. The paired analyses separate supplying explicit relations from changing the presentation of designated unique facts. The output-level analyses retain both corrections and regressions on the same tasks. We analyze existing KG tasks and saved outcomes, keeping invalid or missing outcomes in planned denominators for the reported aggregate scores.

The results show that relation disclosure increases coverage, while residual profiles vary across task families and models. On incoming-tree tasks, some high-precision outputs retain only part of the required route set. Presentation variants can correct these outputs but also introduce regressions; a decrease in one error signature need not produce a comparable increase in exact recovery. These observations distinguish the availability of graph facts from complete recovery of the query-defined entity set. They concern selection behavior; final selected sets do not establish an internal traversal procedure or downstream answer correctness.

[^webgpt]: Nakano et al. *WebGPT: Browser-assisted question-answering with human feedback*. [Paper](https://arxiv.org/abs/2112.09332v3).

[^stark]: Wu et al. *STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases*. [Paper](https://papers.nips.cc/paper_files/paper/2024/hash/e607b1419e9ae7cd5cb5b5bb60c2ad5c-Abstract-Datasets_and_Benchmarks_Track.html).

[^corporatekg]: Kirpichev et al. *Towards Ontology-Driven Multi-Hop Benchmark for Corporate GraphRAG Systems*. [Paper](https://openreview.net/forum?id=1vQ04i1XGC).
