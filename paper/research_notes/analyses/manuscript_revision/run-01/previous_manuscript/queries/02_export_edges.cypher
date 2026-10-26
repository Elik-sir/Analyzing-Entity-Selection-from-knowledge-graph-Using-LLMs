// Existing implementation query; no database execution in this manuscript task.
MATCH (s)-[r]->(t) RETURN elementId(r) AS id,
elementId(s) AS source, type(r) AS relation, elementId(t) AS target,
properties(r) AS properties;
