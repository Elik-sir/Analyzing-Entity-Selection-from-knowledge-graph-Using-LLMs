# Novelty refinement and current manuscript status

2026-10-25. Inspected revision `d8fa5a97e91d6cc0bf1cf5d1654191cf1472e12b`; working tree clean before this pass. This is a scoped follow-up to [transfer_positioning.md](transfer_positioning.md), not a full-manuscript verification or certification of originality. Existing manuscript, archives and earlier decisions are preserved.

## Current status and scientific decision

The existing [PDF](../manuscript/main.pdf) has nine pages and the structure-led title *Graph Patterns and Size in Knowledge-Graph Entity Selection*. Introduction, Related Work, Discussion and Conclusion still organize the contribution around motif/size profiles. The later transfer-diagnostic outline has not been incorporated. The PDF is a complete prior draft, not the completed diagnostic paper proposed in the workflow state.

The most defensible next focus is **whether incomplete route coverage is stable on the same tasks when unique facts remain fixed but their hosting or question formulation changes**. Transfer from Tool Selection is the motivation; a new empirical cross-domain contribution requires harmonized Tool records. The current KG archive alone cannot establish a shared internal mechanism across the two domains.

The inspected source Tool Graph Complexity (Section 5.3 and Appendix O, PDF pp. 8, 30–31) already contains KG transfer, Chain inversion, incoming-tree difficulty and adjacent-decoy effects. These are prior findings. Repeating them with a larger descriptive presentation is not a sufficient claim of additional scientific contribution. Exact cross-paper row reuse remains unquantified.

## Literature boundaries checked in this pass

The queries included `LLM graph reasoning error analysis incomplete traversal incoming trees graph encoding entity selection`, `LLM graph reasoning edge direction reversal curse graph traversal benchmark encoding`, and exact entity-selection and Tool Graph title searches. Search date: 2026-10-25. Snippets were discovery leads only; comparisons below use inspected primary text. This focused search is not exhaustive.

- **Talk like a Graph**, ICLR 2024, Sections 3.1 and Appendix A. Graph encoding and neighborhood accessibility are established axes. A claim that encoding affects graph reasoning is too broad to distinguish this paper. [Proceedings PDF](https://proceedings.iclr.cc/paper_files/paper/2024/file/bf72f65f30eedf5d48da6980ee02b589-Paper-Conference.pdf).
- **Can LLMs perform structured graph reasoning tasks?**, inspected arXiv v4, Sections 2–4. The paper evaluates constrained traversal, node order and prompting, and proposes PathCompare for comparing possible paths. Path-enumeration difficulty or an instruction to consider multiple paths is therefore not a sufficient distinction. Our declared output is all-route entity coverage rather than an optimal single path. This is task differentiation, not proof of originality. [Full text](https://arxiv.org/html/2402.01805v4).
- **GraphWalk**, inspected arXiv v1, Sections 4 and 5.5. It evaluates graph navigation and reports incomplete exploration and early fixation on relationships. We cannot claim discovery of incomplete graph exploration. The candidate increment is item-paired transitions between formally defined final-set signatures under equal unique facts; we do not claim access to process traces or compare scores across protocols. Public conference status was not verified. [Full text](https://arxiv.org/html/2604.01610v1).
- **CES-PK**, inspected arXiv v1, Sections 2–3. This version symbolically filters simulated candidate answers under partial knowledge. It concerns answer verification rather than recovery of intermediate route witnesses. The publisher confirms a KI 2026 chapter; its abstract also mentions LLM-generated candidates, unlike the inspected preprint experiment. Do not conflate their evaluation populations; the chapter full text was not accessible. [Preprint](https://arxiv.org/html/2608.24824v1), [publisher](https://link.springer.com/chapter/10.1007/978-3-032-32335-4_21).
- **RADAR**, inspected arXiv v1, Sections 2.1–2.4. Its discriminative entity selection targets link prediction and triple classification with training and representation-space inference. The phrase “entity selection” is not itself a task novelty. Our route-union coverage target differs; no comparative performance claim is supported. Public conference status was not verified. [Full text](https://arxiv.org/html/2602.21951v1).

## Completed additional offline analysis

[Script](analyses/novelty_refinement/analyze_transitions.py), [retained summary](analyses/novelty_refinement/run-02/summary.json), [observation-level labels](analyses/novelty_refinement/run-02/observations.jsonl).

Selector: archived `core`, `tree_in`, size six, K1/K2/K3/K4/K7, all three model labels. There are 1,500 planned observations, 1,000 unique inputs and 300 model/base pairing units. These are overlapping conditions, not independent replications. Valid saved selected identities support 990 diagnostic observations; all 500 Gemma outcomes lack identities, and ten Ministral outcomes are invalid. Cached exact counts remain available separately. No raw response was reparsed, no model/judge/database was called, and no new uncertainty interval or significance test was computed.

The script reconstructs route witnesses and endpoints from frozen explicit public facts and saved task specifications, checks against the saved reference and cached set scores, and verifies exact equality of unique typed facts, candidate names/types, anchor and target across K1/K3/K4/K7 on each base. K2 changes context; only its anchor/reference invariants are required. All transition matrices retain 100 planned pairs, including invalid and identity-missing states. Definitions and source hashes are in the summary. Conditions are archived designations established in the earlier audits; current registry defaults do not establish historical execution.

### Paired signature transitions, not only marginal averages

An exact one-hop signature means the selected set equals the anchor plus incoming first-hop neighbours. It is an observable output property, not proof of internal early stopping.

For Qwen, K1 has 15 exact outputs, 71 one-hop outputs and 14 other errors, all over 100 planned tasks. K4, displaying relations on both endpoint cards, has 51 exact outputs. Among the 71 initially one-hop outputs, 38 become exact, 24 stay one-hop and nine become other errors. Of the 15 initially exact outputs, six lose exactness. Across all tasks, exactness is gained on 42 and lost on six. This is a mixture of improvements and regressions, not a uniform repair.

For the same 71 initially one-hop Qwen outputs, K3 (destination hosting) makes 13 exact; K7 (direct goal wording instead of procedural slots) makes ten exact. Their total exact counts are both 16/100, with 12 and 11 initially exact outputs respectively losing exactness. Marginal one-hop reductions alone are misleading: K7 reduces that signature from 71 to 52 while total exactness changes from 15 to 16. Reclassification into other errors accounts for part of the reduction.

Ministral supplies a contrary profile: K1 has 54/100 exact outputs and only 15/100 one-hop outputs. K4 makes eight of those 15 one-hop outputs exact, while nine initially exact outputs lose exactness; total exactness reaches 62/100. K3 reduces total exactness to 38/100, with one invalid outcome retained. These observations do not establish a model-universal bottleneck. Gemma cannot contribute identity-level localization in this archive.

### Diagnostic identifiability limits

On the 100 Qwen K1 tasks, ignoring direction or increasing the depth limit from two to three gives the same coverage set as the correct rule on every task. Those two rule violations are therefore unidentifiable from final selected sets in this slice. Reversing direction gives only the anchor; no Qwen K1 output matches it. This excludes that complete alternative output pattern, not every possible directional mistake.

Adjacent K2 supplies some distinguishing contexts: for Qwen, undirected and depth-three targets differ from the correct target on 97/100 and 10/100 tasks respectively. No saved Qwen K2 selection exactly matches those distinct alternatives, whereas 67/100 match the one-hop target. Mixed violations or partial adherence remain possible. Absence of an exact alternative-rule match is not proof of rule comprehension. Terminal-type errors were not tested: all task specifications in this slice have `terminal_type=None`.

## Proposed contribution outline and claim strength

1. **Output-level diagnosis:** define and measure exact route coverage, exact first-hop signatures and other errors, and report where alternative rules are or are not distinguishable. Supported for this bounded saved-data slice; neither a novel general taxonomy nor an internal reasoning mechanism is established.
2. **Paired sensitivity:** locate which initially incomplete outputs become exact under fact hosting and wording changes, retaining regressions and contrary model profiles. This is a completed additional analysis relative to the earlier marginal summaries. Its publication novelty still depends on a fuller comparison and disclosed reuse.
3. **Transfer boundary:** explain why explicit KG relations do not by themselves identify the source of tool-selection difficulty. A new harmonized cross-domain result remains pending. A proposed explanation or experiment is not a completed empirical contribution.

Proposed organizing question: **When the graph facts are explicit, which incomplete selections change under fact-preserving representations, and which explanations can the observed output sets actually distinguish?**

The scientific payoff would be to distinguish having the facts, selecting all route witnesses and interpreting the diagnostic evidence. The present data support conditional behavioral observations. K4 also changes repetition, salience and input length; “duplication repairs search depth” remains a hypothesis.

Suggested narrowed outline: prior transfer observation and unresolved explanation; task/reference and diagnostic distinguishability; same-task hosting/wording/noise transitions; model-specific contrary cases; alternative explanations and next discriminating test. Motif/size grids become context and robustness material. Working title candidate: *Diagnosing Incomplete Route Coverage in Knowledge-Graph Entity Selection*. This is an outline recommendation, not a rewritten section.

## Remaining work and writing decision

Within the saved archive, next extend the same declared diagnostics to other supported families, sizes and fact-matched text conditions, with coverage accounting. Analyze branch omissions and individual false positives separately from whole-set alternative matches. Keep this post-hoc extension exploratory; define any inference family before adding tests.

For a stronger explanation, a fresh controlled test must separate duplication from token length/salience and topology from query/type differences. For a cross-domain result, audit actual Tool item records and the overlap with Appendix O. These are separate requirements: Tool rows are necessary for a new Tool/KG estimate, not automatically for a narrowed KG diagnostic paper. New experiments and research-source changes require author agreement and have not been run.

The stronger full-writing gate remains closed: this pass resolves the bounded transition matrix and exposes diagnostic non-identifiability, but does not complete the intended broader diagnostic scope, reuse audit or mechanism test. This is a scientific scope decision, not a request for permission to continue offline analysis. The previous manuscript remains available; no manuscript or PDF bytes were changed.
