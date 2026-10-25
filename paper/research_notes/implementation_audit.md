# Initial implementation audit

Inspected revision: `261f1b3cc3d3bf3419c04d3d0a35d290fce73cae`, 2026-10-25. Locators below refer to that revision; refresh after code changes. Read-only source inspection, no project imports or model runs.

## Pipeline and evidence

- `graph_motives/graph/neo4j_export.py:13`: generic node/edge export queries. `graph/graph.py:113`: snapshot normalization and graph fingerprinting. `graph/build.py:119` and `graph/motifs.py:20`: Python motif samplers and controlled sampling. `configs/dataset.toml` declares the current sampling/metadata settings.
- `graph/build.py:32,49`: constrained adjacent/disconnected distractors; acceptance preserves the derived reference. This is not uniform sampling across all entities.
- `preparation/registry.py:50`: condition definitions. `preparation/materialize.py:109`: public evidence from induced candidate edges. `preparation/evidence.py:230`: triples, templated text and attribute renderings; arbitrary natural-language evidence is a different setting.
- `preparation/evidence.py:10,73,86`: deterministic collision-checked pseudonyms. Current alias construction does not establish how every historical alias was produced.
- `preparation/questions.py:164`: bounded simple routes, endpoints, all witnesses and minimal graph support, with truncation reporting. `preparation/prompts.py:27`: all-route entity selection. The objective is not necessarily minimal indispensable cards.
- `preparation/materialize.py:51`: reconstruction and single-card fact ablations while retaining the public catalogue; no exhaustive enumeration of card subsets. `preparation/native.py:101`: native answerability remains pending.
- `dataset.py:34,116`: frozen logical-task selection and archive integrity checking. `protocols.py:49`: recorded-message replay where available, current reconstruction otherwise. Distinguish historical source model from newly evaluated model.
- `runner.py:22,76,172,195`: zero-temperature requirement, frozen run provenance and cautious retry/recovery behavior. These controls do not make remote outputs deterministic.
- `protocols.py:163`: set metrics. `report.py:15` (`aggregates`): valid score sums divided by all planned rows, including failures in N. No paired confidence-interval/significance implementation was identified in this reporting path.

All paths abbreviated above are under `graph_motives/` unless stated otherwise. These are current-implementation descriptions; historical execution needs archive evidence.

## Disagreements requiring resolution

1. `docs/ARTICLE.md:32` says Cypher queries extracted motifs and appear in an appendix. The current implementation uses Python samplers; generic export Cypher is not historical extraction evidence. The appendix is not drafted. Obtain historical queries/logs or qualify/remove the assertion; do not rewrite history by inference.
2. `docs/EXPERIMENT_PROTOCOL.md` broadly describes precision penalties for unknown names. `preparation/parsing.py:47-53` rejects unknown/repeated names for current controlled selection, whereas `protocols.py:127` and `runner.py:299` preserve/score legacy unknowns. Audit historical row policies separately.
3. `preparation/native.py:21-28,70-73` can change a visibility instruction and add a format note for Braw+E. “Only relations differ” must be verified against paired historical inputs, not asserted from the current materializer.
4. `docs/ARTICLE.md` describes the reference as motif nodes. The working draft distinguishes motif M from all-route witnesses W. Establish archive-specific equivalence or document protocol-specific references before finalizing the mathematical definition.
5. No full source snapshot was located. Replaying frozen candidates is different from reproducing graph construction, sampling, and exhaustive reference validity.

These issues are recorded in `gaps.md`; none is silently repaired in the existing draft.
