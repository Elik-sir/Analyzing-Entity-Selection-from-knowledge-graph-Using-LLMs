CALL {
// Chain, four nodes.
    MATCH (a)-[r1]->(b)-[r2]->(c)-[r3]->(d)
    RETURN 'chain' AS motif, [a,b,c,d] AS ns, [r1,r2,r3] AS rs
    UNION ALL
// Outward star, four nodes.
    MATCH (h)-[r1]->(a), (h)-[r2]->(b), (h)-[r3]->(c)
    WHERE elementId(a) < elementId(b) AND elementId(b) < elementId(c)
    RETURN 'star_out' AS motif, [h,a,b,c] AS ns, [r1,r2,r3] AS rs
    UNION ALL
// Inward star, four nodes.
    MATCH (a)-[r1]->(h), (b)-[r2]->(h), (c)-[r3]->(h)
    WHERE elementId(a) < elementId(b) AND elementId(b) < elementId(c)
    RETURN 'star_in' AS motif, [h,a,b,c] AS ns, [r1,r2,r3] AS rs
    UNION ALL
// Outward tree, five nodes.
    MATCH (h)-[r1]->(a)-[r3]->(c), (h)-[r2]->(b)-[r4]->(d)
    WHERE elementId(a) < elementId(b)
    RETURN 'tree_out' AS motif, [h,a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
// Inward tree, five nodes.
    MATCH (c)-[r3]->(a)-[r1]->(h), (d)-[r4]->(b)-[r2]->(h)
    WHERE elementId(a) < elementId(b)
    RETURN 'tree_in' AS motif, [h,a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
// Rhombus, four nodes.
    MATCH (a)-[r1]->(b)-[r3]->(d), (a)-[r2]->(c)-[r4]->(d)
    WHERE elementId(b) < elementId(c)
    RETURN 'rhombus' AS motif, [a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
// Hourglass, five nodes.
    MATCH (a)-[r1]->(m), (b)-[r2]->(m), (m)-[r3]->(c), (m)-[r4]->(d)
    WHERE elementId(a) < elementId(b) AND elementId(c) < elementId(d)
    RETURN 'hourglass' AS motif, [m,a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
// Directed cycle, three nodes.
    MATCH (a)-[r1]->(b)-[r2]->(c)-[r3]->(a)
    WHERE elementId(a) < elementId(b) AND elementId(a) < elementId(c)
    RETURN 'cycle' AS motif, [a,b,c] AS ns, [r1,r2,r3] AS rs
    UNION ALL
// Bidirected clique, three nodes.
    MATCH (a)-[r1]->(b), (b)-[r2]->(a), (a)-[r3]->(c), (c)-[r4]->(a),
          (b)-[r5]->(c), (c)-[r6]->(b)
    WHERE elementId(a) < elementId(b) AND elementId(b) < elementId(c)
    RETURN 'clique' AS motif, [a,b,c] AS ns, [r1,r2,r3,r4,r5,r6] AS rs
}
// Require distinct nodes.
WITH motif, ns, rs
WHERE all(n IN ns WHERE single(x IN ns WHERE x = n))
// Represent edges as source, type, target triples.
WITH motif, ns,
     [r IN rs | [elementId(startNode(r)), type(r), elementId(endNode(r))]] AS edges
// Reject any additional typed induced edge,
// including self-loops.
WHERE NOT EXISTS {
    MATCH (u)-[extra]->(v)
    WHERE u IN ns AND v IN ns
      AND NOT ([elementId(u), type(extra), elementId(v)] IN edges)
}
RETURN DISTINCT motif,
       [n IN ns | elementId(n)] AS node_ids,
       [n IN ns | coalesce(n.name, n.headline, n.title, n.ticker)] AS node_names,
       edges
LIMIT 100;
