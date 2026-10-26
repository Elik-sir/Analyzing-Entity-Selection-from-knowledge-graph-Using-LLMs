// Newly documented star_in instance check; not executed or historical.
// $roles maps symbolic roles to elementId strings; $relation_types follows listed edges.
WITH [$roles.a, $roles.b, $roles.c, $roles.d, $roles.e, $roles.h] AS node_ids,
 [{source:$roles.a, relation:$relation_types[0], target:$roles.h},
 {source:$roles.b, relation:$relation_types[1], target:$roles.h},
 {source:$roles.c, relation:$relation_types[2], target:$roles.h},
 {source:$roles.d, relation:$relation_types[3], target:$roles.h},
 {source:$roles.e, relation:$relation_types[4], target:$roles.h}] AS expected_edges
MATCH (n) WHERE elementId(n) IN node_ids
WITH node_ids, expected_edges, collect(DISTINCT n) AS vs
OPTIONAL MATCH (u)-[r]->(v) WHERE u IN vs AND v IN vs
WITH node_ids, expected_edges, vs, collect(DISTINCT CASE WHEN r IS NULL THEN null ELSE
 {source:elementId(u), relation:type(r), target:elementId(v)} END) AS actual
RETURN size(vs)=size(node_ids)
 AND all(x IN node_ids WHERE single(y IN node_ids WHERE y=x))
 AND all(e IN actual WHERE e IN expected_edges)
 AND all(e IN expected_edges WHERE e IN actual) AS exact_match, actual;
