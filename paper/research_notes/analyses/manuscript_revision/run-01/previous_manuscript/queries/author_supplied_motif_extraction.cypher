CALL {
    // Цепь: 4 вершины, a → b → c → d
    MATCH (a)-[r1]->(b)-[r2]->(c)-[r3]->(d)
    RETURN 'chain' AS motif, [a,b,c,d] AS ns, [r1,r2,r3] AS rs
    UNION ALL
    // Исходящая звезда: центр + 3 листа
    MATCH (h)-[r1]->(a), (h)-[r2]->(b), (h)-[r3]->(c)
    WHERE elementId(a) < elementId(b) AND elementId(b) < elementId(c)
    RETURN 'star_out' AS motif, [h,a,b,c] AS ns, [r1,r2,r3] AS rs
    UNION ALL
    // Входящая звезда: 3 листа → центр
    MATCH (a)-[r1]->(h), (b)-[r2]->(h), (c)-[r3]->(h)
    WHERE elementId(a) < elementId(b) AND elementId(b) < elementId(c)
    RETURN 'star_in' AS motif, [h,a,b,c] AS ns, [r1,r2,r3] AS rs
    UNION ALL
    // Исходящее дерево: 5 вершин, h → {a,b}, a → c, b → d
    MATCH (h)-[r1]->(a)-[r3]->(c), (h)-[r2]->(b)-[r4]->(d)
    WHERE elementId(a) < elementId(b)
    RETURN 'tree_out' AS motif, [h,a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
    // Входящее дерево: 5 вершин, c → a → h, d → b → h
    MATCH (c)-[r3]->(a)-[r1]->(h), (d)-[r4]->(b)-[r2]->(h)
    WHERE elementId(a) < elementId(b)
    RETURN 'tree_in' AS motif, [h,a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
    // Ромб: 4 вершины, a → {b,c} → d
    MATCH (a)-[r1]->(b)-[r3]->(d), (a)-[r2]->(c)-[r4]->(d)
    WHERE elementId(b) < elementId(c)
    RETURN 'rhombus' AS motif, [a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
    // Песочные часы: 5 вершин, {a,b} → m → {c,d}
    MATCH (a)-[r1]->(m), (b)-[r2]->(m), (m)-[r3]->(c), (m)-[r4]->(d)
    WHERE elementId(a) < elementId(b) AND elementId(c) < elementId(d)
    RETURN 'hourglass' AS motif, [m,a,b,c,d] AS ns, [r1,r2,r3,r4] AS rs
    UNION ALL
    // Направленный цикл: 3 вершины
    MATCH (a)-[r1]->(b)-[r2]->(c)-[r3]->(a)
    WHERE elementId(a) < elementId(b) AND elementId(a) < elementId(c)
    RETURN 'cycle' AS motif, [a,b,c] AS ns, [r1,r2,r3] AS rs
    UNION ALL
    // Двунаправленная клика: 3 вершины, 6 рёбер
    MATCH (a)-[r1]->(b), (b)-[r2]->(a), (a)-[r3]->(c), (c)-[r4]->(a),
          (b)-[r5]->(c), (c)-[r6]->(b)
    WHERE elementId(a) < elementId(b) AND elementId(b) < elementId(c)
    RETURN 'clique' AS motif, [a,b,c] AS ns, [r1,r2,r3,r4,r5,r6] AS rs
}
// Все вершины мотива должны быть различными.
WITH motif, ns, rs
WHERE all(n IN ns WHERE single(x IN ns WHERE x = n))
// Представляем рёбра тройками (источник, тип, цель).
WITH motif, ns,
     [r IN rs | [elementId(startNode(r)), type(r), elementId(endNode(r))]] AS edges
// Запрещаем любые дополнительные типизированные рёбра
// внутри выбранного множества вершин, включая петли.
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
