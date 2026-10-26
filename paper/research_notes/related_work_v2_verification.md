# Related Work v2 verification — 2026-10-25

Author requested an English Related Work section using research_summary.md and the supplied Russian sketch. Created a separate section variant; existing manuscript, source draft and research code preserved. Current workflow_state.json permits scoped writing; the summary contains an earlier gate state.

Primary-source verification used the URLs and exact content locators in related_work_v2_evidence_map.json. Opened full texts for NLGraph, Talk like a Graph, graph-pattern comprehension, GraphOmni v5, KG understanding v4, Tian et al., STaRK, G-Retriever, SubgraphRAG, and Li/Ouyang. Metadata came from proceedings/ACL/publisher pages, with GraphOmni conservatively cited as a preprint. The supplied Tool Graph manuscript comparison uses the previously inspected Appendix O audit. No exhaustive novelty assessment or fresh independent review is claimed.

Search approach: direct resolution of primary-source URLs in the author sketch and prior literature audit; inspected task definitions, representation factors and retrieval methods. Included works establish graph-task, representation and evidence-selection context. The omitted leads and remaining reuse limitation are recorded in the sidecar. The official WWW 2027 research-track page was rechecked for track/Web context; no submission action occurred.

Validation: `/Users/ivan_kirpichev/.local/bin/python3.12 paper/research_notes/scripts/validate_research_artifacts.py --root .` passed with 60 evidence records, 27 claims, zero errors. This validates the existing global ledger only; new paragraph/source coverage is recorded separately in the sidecar and is not certified by that structural pass. No empirical numbers added. No new experiments run.
