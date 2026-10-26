// Proposed read-only check of a supplied frozen motif, not a historical extraction query.
// Parameters: $node_ids (unique elementId strings), $expected_edges (maps
// with source, relation, target). Use IDs from the same immutable database.
MATCH (n)
WHERE elementId(n) IN $node_ids
WITH collect(DISTINCT n) AS vs
OPTIONAL MATCH (u)-[r]->(v)
WHERE u IN vs AND v IN vs
WITH vs, collect(DISTINCT CASE WHEN r IS NULL THEN null ELSE
 {source: elementId(u), relation: type(r), target: elementId(v)} END) AS actual
RETURN size(vs) = size($node_ids)
 AND size($node_ids) = size(reduce(unique_ids = [], x IN $node_ids |
   CASE WHEN x IN unique_ids THEN unique_ids ELSE unique_ids + x END))
 AND all(e IN actual WHERE e IN $expected_edges)
 AND all(e IN $expected_edges WHERE e IN actual) AS exact_typed_induced_match,
 actual AS observed_edges;
