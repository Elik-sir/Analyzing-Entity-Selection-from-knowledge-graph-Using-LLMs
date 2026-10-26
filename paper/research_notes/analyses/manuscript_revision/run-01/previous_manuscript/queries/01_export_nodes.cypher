// Existing implementation query; no database execution in this manuscript task.
MATCH (n) RETURN elementId(n) AS id, labels(n) AS labels,
properties(n) AS properties;
