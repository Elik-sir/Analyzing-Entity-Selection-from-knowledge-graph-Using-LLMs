# Query provenance

`author_supplied_motif_extraction.cypher` preserves the query supplied in this chat on 2026-10-25, with whitespace normalized. `author_query_english_comments.cypher` translates only comments; executable-token equivalence was checked. The paper appendix reproduces this author-supplied query, not a newly invented historical procedure. It has nine fixed-size patterns, an exact typed induced-edge filter and a global LIMIT 100; it is not the entire archived size-grid/quota pipeline and has not been executed in this task.

01/02 reproduce NODE_QUERY and EDGE_QUERY from graph_motives/graph/neo4j_export.py. They export a graph; they do not prove historical motif extraction.

03 and check_*.cypher are separately preserved newly documented read-only instance checks, not historical extraction or random sampling code. They have not been run against Neo4j. Match role IDs and edge-type parameters to the same immutable database; elementId is not a cross-snapshot identifier. The six-node tree specializations show one branch allocation; other size/allocation cases use 03 with their frozen node/typed-edge list. Acceptance, names, candidate expansion and target checks are outside these queries.

No write clauses or APOC are used. No database connection, credentials, export or model call was made in this task.
