# Related Work revision for the supplied PDF

Date: October 26, 2026. Scope: Section 2 of the supplied `main (2).pdf`, titled **Related Work and Prior Transfer Evidence**. This is a section replacement, not a full-manuscript audit, an independent review, or a submission-readiness decision.

## Deliverables and preservation

- [Readable academic-English section](../../../manuscript/sections/02_related_work_v3.md).
- [LaTeX replacement](../../../manuscript/sections/02_related_work_v3.tex).
- [Self-contained section bibliography](../../../manuscript/sections/related_work_v3.bib).
- `claims.jsonl`, `evidence_register.json`, and `manuscript_claim_map.json` contain the scoped sentence dispositions, source locators, and output hashes. `input_provenance.json` records hashes of the supplied PDF and reading list.

The supplied PDF has a different title, introduction, primary metric, and Related Work from the active local `main.tex`. The replacement follows the supplied PDF's Tool-to-KG framing and recall-first evaluation. The active older manuscript, all v2 variants, original PDF, and pre-existing user files are preserved. Merge bibliography entries by key into the source project that produced the supplied PDF; do not append this self-contained bibliography to another database with duplicate keys. The LaTeX section retains `sec:related`. The existing graph-construction citation remains appropriate in the supplied PDF's Introduction/Method and is not needlessly duplicated here.

No PDF was modified or newly compiled. Citation-key coverage, BibTeX parsing when available, TeX brace balance, and research-ledger validation are checked separately from full-document typesetting. No new model, judge, GPU, database, or experimental calls were made. The reproduction script writes only the new section variant and scoped evidence files.

## Editorial changes and scientific support

1. Preserve Tool Graph Complexity as the direct antecedent, including Appendix O's prior KG selection results. Distinguish its adjusted sequential-pattern findings from raw motif rankings. Avoid attributing the discovery of difficult incoming trees, explicit-KG chain inversion, or adjacent-decoy errors to this manuscript.
2. Add structural evaluation context from Talk like a Graph, graph-pattern comprehension, and GraphOmni. Define the present target as a query-conditioned route union, without claiming that prior graph benchmarks only predict labels or scalar answers.
3. Separate information disclosure from presentation of matched designated facts. Raw/Raw+E is not described as an equally informative encoding comparison. Templated prose is not equated with arbitrary natural descriptions.
4. Relate the task to STaRK's answer-entity retrieval, G-Retriever's useful connected context, and RoG's planned reasoning paths. Retain GraphWalk's prior incomplete-exploration observation, explicitly attached to its graph-in-context setting. Set omissions do not reveal internal execution traces.
5. Connect adjacent distractors to TopoRAG's retrieval constraints and distinguish them from Amiraz et al.'s passage-level distraction measure. Li/Ouyang supports separating selection quality from generation quality. Recall, precision, and exact recovery do not establish a minimum evidence set or QA improvement.

The section contains no new measured values, significance/causality claims, novelty/priority claims, or independent-replication claim. Methodological comparisons are scoped inferences from inspected task definitions, not reported head-to-head experimental results. Every sentence, including uncited own-task descriptions and limits, has a disposition in the scoped map.

## Search and screening log

Method: resolve primary URLs in the supplied list, compare against the actual PDF, inspect relevant full-text definitions/methods, and verify bibliographic identities on publisher/proceedings/ACL pages. Exact local sources and primary locators appear in `evidence_register.json`. Search queries included `GraphOmni site:openreview.net/forum`, `GraphOmni site:proceedings.iclr.cc/paper_files/paper/2026`, `"GRAIN: Bridging Name"`, `"A Systematic Exploration" "Knowledge Graph Alignment" arxiv`, `Tian Xing "Knowledge Graph Alignment" arxiv 2025`, `"Plan Then Retrieve" "Graph-RFT"`, and `"Actions Speak Louder than Prompts"`. Searches were discovery only; snippets were not used to substantiate manuscript comparisons.

| List item | Decision | Reason and inspection scope |
| --- | --- | --- |
| 1. GraphOmni | Include | Joint structure/serialization/prompting design directly informs conditional structural interpretation. Full Section 2 of arXiv v5 inspected. |
| 2. Talk like a Graph | Include | Foundational graph encoding/task/structure evaluation; relevant conference PDF sections inspected. |
| 3. Graph pattern comprehension | Include | Direct context for motif-based evaluation; full pattern-task definitions inspected. |
| 4. Tian et al., KG alignment | Include narrowly | Factor taxonomy is explicit in the verified publisher abstract; full-text body access failed on reread. No detailed result comparison or ordering preference is reproduced. |
| 5. Beyond Static Retrieval | Omit | Bridge-document retrieval/ranking is useful context, but adds a further pipeline method to a short fixed-pool diagnostic section. Landing page/abstract inspected; PDF access failed. Omission is editorial, not a finding of non-relevance. |
| 6. Li and Ouyang | Include | Controlled knowledge mixtures and generator/task dependence directly support separating selection metrics from QA; relevant full text inspected. |
| 7. TopoRAG | Include | Structural constraints and noisy neighbor expansion directly contextualize adjacent distractors; full formulation inspected. |
| 8. GRAIN | Omit | Identifier/narrative invariance concerns auxiliary naming checks; would shift the section toward agent training. ACL metadata and original-author preprint accessed; detailed full-method comparison not completed. |
| 9. Dissecting GraphRAG | Omit | Module-level extraction/clustering/reporting is broader than fixed-pool selection. Publisher landing page/abstract inspected; no detailed empirical comparison made. |
| 10. STaRK | Include | Closest benchmark context for entity retrieval with textual and relational constraints; full formal problem definition inspected. |
| 11. G-Retriever | Include | Compact connected graph context through PCST; full original-author method inspected, conference metadata verified. |
| 12. GRADE | Omit | QA synthesis/difficulty matrices do not directly support a route-selection comparison. Landing page screened; full-method comparison not completed. |
| 13. The Distracting Effect | Include | Distinguishes passage-level distraction from binary relevance and from adjacency; formal measure inspected. |
| 14. Reasoning on Graphs | Include | Relation plans and instantiated reasoning paths provide explicit context for route evidence; full Sections 3-4 inspected. |
| 15. Actions Speak Louder than Prompts | Omit | Primary author research overview identifies a node-classification focus; a broad inference/training comparison is less direct than the retained structural benchmarks. Full conference-paper comparison not completed. |
| 16. NLGraph | Omit | Foundational graph-task context overlaps the three retained structural sources; omission keeps the short section focused. Existing v2 verification was available, not freshly re-certified in this revision. |
| 17. Plan Then Retrieve | Omit | Adaptive KG/Web retrieval and reinforcement fine-tuning are outside this study's intervention. ACM identity and original preprint discovery checked; full-method comparison not completed. |
| 18. PRoH | Omit | Hypergraph planning adds a distinct representation and retrieval setting beyond the present entity-route target. Versioned original-preprint landing page screened; no detailed equivalence claim made. |

Additional retained references: Xinbang Dai et al.'s KG prompting paper, GraphWalk, and the supplied anonymous Tool Graph manuscript. The corporate KG construction source is already cited elsewhere in the supplied manuscript.

## Verification limits

- Tian et al.: metadata/abstract verified, relevant full body not freshly inspected because repeated publisher reads timed out. The single retained sentence reproduces only the abstract's factor taxonomy. This is explicitly marked `abstract_only` in the evidence record.
- GraphOmni: the author project page states ICLR 2026 acceptance, and a search located a published-paper entry; direct OpenReview access returned a browser challenge. The BibTeX conservatively identifies the exact inspected arXiv v5 rather than treating search results as conference verification.
- Tool Graph Complexity: the local manuscript was inspected directly, including adjusted analysis and Appendix O. No public acceptance or current review status is asserted in the new bibliography. Existing row-level reuse uncertainty is retained.
- Frozen-input and metric exports were inspected as existing evidence, not rerun or independently rescored. The author's requested PDF is a prose source, not proof of experimental execution.
- Scope is this section only; references in other sections, whole-paper anonymity, venue compliance, and typeset page limits are not certified here.
