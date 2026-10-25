# Bounded independent claim audit

The two paragraphs cannot be used unchanged. The appendix claim is contradicted by the draft itself; historical Cypher motif extraction is unverified; the selection convention and target definition need explicit distinctions.

Scope: every assertion in Subgraph extraction (line 32) and Selection task (lines 46-51) of docs/ARTICLE.md, including its two bullets. No other manuscript coverage is claimed. The 22 records below split compound sentences into checkable assertions. “Supported” implementation status means the inspected current design supports the proposition; it does not establish the historically executed benchmark. Numeric constants here are design arithmetic, not empirical results.

## Provenance and limits

Exact bytes and symbols are recorded in evidence_register.json, together with HEAD revision; working_tree.txt records the untracked draft/notes state. No earlier audits, gaps or prior validation conclusions were read. No models, project module imports, external services, credentials, or full historical reconstruction were used. The first 100 physical input records were inspected with Python standard-library gzip/json only; this convenience sample is not a population audit and mixes request stages/conditions. Counts below 25 in that mixed sample are not counterexamples to the selection-task design. No saved performance metrics were recomputed or claimed.

Current code exports a full graph using NODE_QUERY and EDGE_QUERY and samples motifs with Python SAMPLERS. This is a material difference from the draft wording, but is not proof that Cypher motif extraction never occurred historically. The appendix is explicitly not drafted. These are sufficient to reject unchanged reuse without inventing historical conclusions.

The selection sentence should explicitly define all-route witnesses (anchor, endpoints and intermediates on all supporting routes), distinguish these from minimal support/indispensable cards, and describe abstention when evidence is insufficient. The legacy reference is the sampled motif; controlled rendering computes witnesses. Equality must be demonstrated for the claimed population before collapsing those definitions. For distractors, clarify that displayed relations are those induced by the candidate pool and that adjacent candidates are admitted only if they preserve the graph oracle. Pair generation can reject one variant, so generation logic alone does not prove complete historical pairing.

## Atomic dispositions

### C01 — pending

We used Cypher queries to extract graph-pattern instances from the source graph.

Scope: docs/ARTICLE.md:32; bounded audit, not full manuscript. Type: historical. Evidence: draft, export, motifs, build.

No inspected extraction execution log establishes this. Current export queries enumerate all nodes/edges; build_dataset calls Python SAMPLERS. This does not disprove a different historical pipeline. Supply archived motif-specific queries and execution/version provenance, or describe only verified current behavior.

### C02 — conflicted

The Cypher queries are provided in the appendix.

Scope: docs/ARTICLE.md:32; bounded audit, not full manuscript. Type: implementation. Evidence: draft.

Appendix lines 101-103 says Not drafted; optional. Add the actual verified queries or remove this sentence. This is a document-presence claim, not experimental evidence.

### C03 — supported

Each task consists of a question and 25 candidate entities.

Scope: docs/ARTICLE.md:46; bounded audit, not full manuscript. Type: implementation. Evidence: build, config, validation.

Supported as the configured selection-task design: build_item and candidate_size validation. Do not generalize to every archived request stage (answer/judge/incremental requests differ); historical selection population coverage remains unverified.

### C04 — supported

The candidates include all sampled motif entities plus distractors.

Scope: docs/ARTICLE.md:46; bounded audit, not full manuscript. Type: implementation. Evidence: build, validation.

build_item concatenates m[ids] with decoys; check_item checks reference inclusion. Current design support only.

### C05 — supported

The number of distractors is 25 minus subgraph size.

Scope: docs/ARTICLE.md:46; bounded audit, not full manuscript. Type: implementation. Evidence: build, config, validation.

For accepted items with unique motif/candidate names, candidate_size minus motif size; short pools fail validation. Design arithmetic, not a measured result.

### C06 — supported

Six-entity core motifs have 19 distractors.

Scope: docs/ARTICLE.md:46; bounded audit, not full manuscript. Type: implementation. Evidence: config, registry, build.

CORE_SIZES and candidate_size imply 25-6=19; current core design only, not an empirical dataset count.

### C07 — supported

Core rhombi have 21 distractors.

Scope: docs/ARTICLE.md:46; bounded audit, not full manuscript. Type: implementation. Evidence: config, registry, build.

CORE_SIZES rhombus=4 implies 25-4=21; design arithmetic.

### C08 — supported

Core hourglasses have 20 distractors.

Scope: docs/ARTICLE.md:46; bounded audit, not full manuscript. Type: implementation. Evidence: config, registry, build.

CORE_SIZES hourglass=5 implies 25-5=20; design arithmetic.

### C09 — supported

Two noise variants are used.

Scope: docs/ARTICLE.md:46; bounded audit, not full manuscript. Type: implementation. Evidence: config, build.

sampling.variants specifies disconnected and adjacent; historical execution of every cell not certified.

### C10 — supported

Disconnected distractors have no edges to motif nodes in either direction.

Scope: docs/ARTICLE.md:48; bounded audit, not full manuscript. Type: implementation. Evidence: build, graph.

pick_decoys blocks union of Graph.neighbours of reference nodes; neighbours unions incoming and outgoing.

### C11 — supported

Disconnected distractors may connect to one another.

Scope: docs/ARTICLE.md:48; bounded audit, not full manuscript. Type: implementation. Evidence: build, graph.

No mutual-disconnection constraint in pick_decoys; induced context keeps these edges. Permission, not a claim that such edges occur in every sample.

### C12 — supported

Adjacent noise has at most 10 motif-neighbor distractors.

Scope: docs/ARTICLE.md:49; bounded audit, not full manuscript. Type: implementation. Evidence: build, config, graph.

n_adj=min(adjacent_max,total-len(m[ids])); pick_adjacent admits only neighbors that preserve the graph oracle. State this acceptance constraint for reproducibility.

### C13 — supported

Remaining adjacent-condition distractors are disconnected from the motif.

Scope: docs/ARTICLE.md:49; bounded audit, not full manuscript. Type: implementation. Evidence: build, graph.

pick_decoys blocks all motif neighbors even when filling the remainder of the adjacent variant.

### C14 — supported

Paired variants retain the same question.

Scope: docs/ARTICLE.md:51; bounded audit, not full manuscript. Type: implementation. Evidence: build.

build_dataset passes the same motif to build_item; make_question is called with same graph/motif structure. Pair completeness must still be checked: variants can be rejected separately.

### C15 — supported

Paired variants retain the same reference set.

Scope: docs/ARTICLE.md:51; bounded audit, not full manuscript. Type: implementation. Evidence: build, panels.

Reference copied from same m[ids]; pairing checker compares reference fields. Does not certify all historical rows pair successfully.

### C16 — supported

Paired variants may contain different distractors.

Scope: docs/ARTICLE.md:51; bounded audit, not full manuscript. Type: implementation. Evidence: build.

Separate variant RNG and distinct adjacency rules; may differ is supported, universal difference is not claimed.

### C17 — supported

When graph relations are shown, distractor relations are included.

Scope: docs/ARTICLE.md:51; bounded audit, not full manuscript. Type: implementation. Evidence: materialize, native, graph.

Both renderers use all edges induced by candidate IDs, including distractor-involving edges. Scope must say candidate-induced relations; edges to nodes outside the pool are not shown.

### C18 — supported

Each candidate card has a unique name.

Scope: docs/ARTICLE.md:51; bounded audit, not full manuscript. Type: implementation. Evidence: validation, metadata.

public_node supplies name; check_item rejects normalized duplicate names. Historical population not exhaustively checked.

### C19 — supported

Each candidate card supplies entity type and condition-specific facts.

Scope: docs/ARTICLE.md:51; bounded audit, not full manuscript. Type: implementation. Evidence: metadata, materialize, native.

public_node and rendering expose name/type/facts; names/types-only conditions have empty facts. A facts field does not establish factual completeness or visible sufficiency.

### C20 — pending

The model must select all entities supporting the answer.

Scope: docs/ARTICLE.md:51; bounded audit, not full manuscript. Type: implementation. Evidence: prompts, archive.

Too ambiguous for unchanged scientific text. _WITNESS_RULE and inspected archived system prompt define all-route witness coverage including anchor and all parallel routes; membership does not imply indispensable displayed evidence. Define that convention explicitly and retain insufficient-evidence behavior.

### C21 — supported

The model returns candidate names as a set.

Scope: docs/ARTICLE.md:51; bounded audit, not full manuscript. Type: implementation. Evidence: prompts, archive.

Semantically a set; wire format is JSON selected_entities array of distinct exact names plus insufficient_evidence boolean. The inspected archive line 1 carries that instruction. Clarify JSON protocol if this sentence stands alone.

### C22 — pending

The reference set consists of all sampled motif entities.

Scope: docs/ARTICLE.md:51; bounded audit, not full manuscript. Type: implementation. Evidence: build, materialize, archive.

True for build_item legacy reference_names. Controlled materialize_cell instead derives graph_witness_ids from evaluate_task; sampled motif M, endpoint A, and all-route W are distinct definitions. Inspected archive line 1 has separate reference_ids/target_ids/witness_ids; one example does not certify M=W throughout claimed core. Establish equality for accepted population or specify protocol-specific targets.

## Skill behavior and ambiguities

The skill successfully directs atomic extraction, current-versus-historical separation, exact locators, and dispositions beyond preexisting ledger entries. The shared contract supplies the important witness/support distinction. No full manuscript or readiness claim is justified.

The skill unconditionally asks to update production audit/gap/map records and run the root validator, but has no explicit bounded-isolated-audit mode. The evaluator instruction overrides those destinations here. The validator supports --notes, discovered by reading its script, so the isolated records can be checked without reading prior conclusions. Its workflow_state requirement requires an explicitly closed local gate even for a two-paragraph audit; this is structural bookkeeping rather than a full workflow decision. A concise instruction allowing scoped output/validation would reduce this ambiguity.

The available claim taxonomy lacks document-presence/design-definition categories: C02 uses implementation as a pragmatic document-state classification; arithmetic/design claims also use implementation. This does not change their truth conditions. “Supported current implementation” versus “verified historical manuscript assertion” must remain visible to avoid over-reading the many supported design claims.

No submission readiness, novelty, statistical, or QA-performance conclusion is made.
