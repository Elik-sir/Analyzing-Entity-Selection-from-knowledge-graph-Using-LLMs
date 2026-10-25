# Literature review: initial search state

This is an incremental literature review, not a completed novelty assessment. The user-supplied sources verified on 2026-10-25 are documented below; other initial leads remain pending. Verified bibliography entries are kept in `verified_references.bib`; the mandatory anonymous Tool Graph source has a separate citation-requirement record until its public citation metadata is supplied or verified.

## Prior resource

The local `11_Towards_Ontology_Driven_Mul.pdf` title page identifies *Towards Ontology-Driven Multi-Hop Benchmark for Corporate GraphRAG Systems*. The user confirmed unchanged reuse of that study's snapshot; cite its graph-construction discussion rather than repeating the pipeline. This is author-confirmed provenance, not a fresh bytewise comparison. The existing BibTeX and OpenReview URL in `docs/ARTICLE_REFERENCES.bib` still need independent metadata/status verification before final bibliography assembly. Task construction and scoring in the present study remain separate methodological responsibilities.

## User-supplied sources checked on 2026-10-25

### Mandatory: Tool Graph Complexity for LLM Tool-Calling: A Reproducible Benchmark Auditing and Generation Framework

Source: supplied PDF, archived at `sources/tool_graph_complexity.pdf`; title page, Introduction, Section 1.1 and Appendix O (PDF pages 30–31) inspected. The file identifies anonymous authors and review at ICLR 2027, not acceptance. Exact-title primary-source searching did not establish a public paper landing page in this session; this is not proof that none exists. See `citation_requirements.json` for mandatory status and verified-versus-pending metadata.

The work separates reference-set non-minimality from dependency composition in tool selection. Crucially, Appendix O includes a finance-KG entity-selection substrate, explicit relations and adjacent distractors. It is therefore directly relevant beyond a general tool-use analogy. The present study must explain its additional evidence/representation contrasts and reference convention, and check whether any resources or experimental populations overlap. Do not claim that the current route-coverage target is the minimal necessary evidence set. Do not transfer Appendix O's counts/results to this repository or infer identical populations from similar model/motif names. No numerical findings from that paper are adopted as this project's results here.

### How Do Large Language Models Understand Graph Patterns? A Benchmark for Graph Pattern Comprehension

Primary sources: [ICLR 2025 proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/9316da9c25ab559ba678f2fe52217a64-Abstract-Conference.html) and [arXiv full text, v2](https://arxiv.org/html/2410.05298v2), Introduction and Sections 2–5. Proceedings verify title, authors and conference; they resolve the Yifei/Yifen inconsistency in the arXiv abstract metadata in favor of Yifei Shen.

Scope: terminology/topology-based graph-pattern comprehension and data-driven pattern mining. Proposed distinction to verify against the current task: fixed candidate entity route coverage for a query, rather than identifying, editing or mining a pattern itself. Motif use alone is not a contribution distinction.

### Large Language Models Can Better Understand Knowledge Graphs Than We Thought

Primary sources: [arXiv metadata](https://arxiv.org/abs/2402.11541) and [full text, v4](https://arxiv.org/html/2402.11541v4), Sections 3–5. Metadata and comparison scope checked; a journal-publication lead exists but its publisher page could not be inspected, so the bibliography below uses the verified arXiv preprint record without asserting journal metadata.

Scope: KG-prompt formats, triple organization and robustness to noisy/incomplete subgraphs, evaluated through QA, with an attention analysis. The present study should distinguish entity-set selection and route-coverage metrics from final-answer evaluation, and controlled templated rendering from arbitrary fluent text. The triple-versus-text research question itself is already related work, not a new idea established by this project.

### Talk like a Graph: Encoding Graphs for Large Language Models

Primary sources: supplied local PDF (arXiv:2310.04560v1), pages 1–2, and [arXiv metadata](https://arxiv.org/abs/2310.04560). Title/authors and graph-encoding formulation checked. A conference-page lead was found but OpenReview returned a browser challenge; the bibliography below conservatively uses the verified arXiv version.

Scope: text encodings, task prompting and graph-structure sensitivity. The current paper should cite this as a foundational representation study, then state its particular entity-selection output/reference and evidence interventions. No blanket novelty claim follows from choosing different model versions or a corporate KG.

## Search/verification log for this update

- Opened both user-provided arXiv records and their linked full texts; inspected benchmark/task sections rather than relying only on abstracts.
- Read both user-supplied PDFs without following instructions embedded in their contents. In-document reviewer guidance is document content, not an instruction for this assistant or the present paper workflow.
- Queried exact Tool Graph title on the web/OpenReview; no verified public landing page returned. Author identities and publication metadata remain unknown.
- Checked the official ICLR proceedings for graph-pattern comprehension; used proceedings author spelling.
- Publisher redirect for the KG-comprehension paper was inaccessible; OpenReview verification challenge prevented checking the Talk like a Graph conference page. No acceptance/DOI fields were filled from secondary citations.

## Candidate comparison groups

These URLs originated as leads in the existing article plan. For Talk like a Graph use the verified source status above; the other entries below still await content and metadata verification:

- Graph representation and graph-task evaluation: [Talk like a Graph](https://arxiv.org/abs/2310.04560), [GraphOmni](https://arxiv.org/abs/2504.12764), [Revisiting Graph Reasoning](https://arxiv.org/abs/2408.09529).
- Structured-knowledge evaluation: [SKA-Bench](https://aclanthology.org/2025.findings-emnlp.194/).
- Retrieval and graph access: [G-Retriever](https://proceedings.nips.cc/paper_files/paper/2024/file/efaf1c9726648c8ba363a5c927440529-Paper-Conference.pdf), [Think-on-Graph](https://proceedings.iclr.cc/paper_files/paper/2024/hash/10a6bdcabbd5a3d36b760daa295f63c1-Abstract-Conference.html).
- Context rather than automatically comparable baselines: [Graph RAG summarization](https://arxiv.org/abs/2404.16130), [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/).

## Planned search and verification

Run dated primary-source searches for entity selection, evidence selection, KG QA, graph serialization, structural distractors, support-path coverage, sufficiency and naming effects. For each included paper record metadata verification, inspected sections, task/metric/input differences, overlapping interventions, and the narrow distinction this work can defend. Follow citation chains to closer studies rather than treating this seed list as exhaustive.

The likely contribution is an empirical diagnostic study and reusable evaluation evidence; whether any particular component is new remains open. No “first”, “novel method” or state-of-the-art claim is authorized by this note.

## Completed Appendix O positioning comparison

The detailed task/data/protocol/result matrix and scoped contribution decision are in [contribution_comparison.md](contribution_comparison.md). Appendix O directly overlaps KG selection, motifs, size, explicit relations and adjacent distractors; those are not standalone new contributions. The supported increment is the within-KG native/overlay intervention and audited controlled rendering/placement contrasts. Shared-resource/task/response provenance relative to Appendix O is unresolved; no independence or new-dataset claim is permitted. Broader reference leads and anonymous citation metadata remain pending.
