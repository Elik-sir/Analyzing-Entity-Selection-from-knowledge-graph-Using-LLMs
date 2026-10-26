# Motif schematic archive audit

2026-10-26. Seven Core K1/disconnected representatives selected from saved Qwen inputs. This is a bounded input audit, not a new experiment or archive-wide prevalence estimate. Source hashes, exact selectors, line numbers and task specifications are in `archive_samples.json`.

## Scientific distinctions

- Arrowheads denote stored directed KG relations. Incoming queries follow those arrows backwards; do not reverse the graph arrows to depict traversal.
- All displayed nodes belong to the required route-coverage reference W. Endpoint answers A are only a subset; anchor/intermediate nodes can remain mandatory selections without being endpoints.
- Exact public candidate facts independently reproduce saved endpoint and witness targets in all seven chosen examples. Distractors are omitted from schematics.
- Current sampler functions confirm the intended construction definitions but do not prove which code historically created the archived instances. Full KG completeness or extraction execution was not checked.

## Shape findings

- Chain: a single outgoing path of six vertices, terminating at the first entity of the requested terminal type (Country in the representative); not a fixed two-hop question.
- Stars: six vertices; one hub/anchor plus five leaves. Star-in arrows enter the anchor; star-out arrows leave it. The query returns the corresponding one-hop neighbors.
- Trees: six vertices, root/anchor plus two first-level neighbors and three second-level endpoints in these examples. Each first-level child has at least one child; the branching allocation is not necessarily balanced. Tree-in stored arrows converge toward the anchor, while the query expands backwards for two hops. Tree-out follows forward arrows for two hops.
- Rhombus: four vertices; two outgoing length-two branches from the anchor reconverge at a shared endpoint. Both intermediate vertices belong to W even though A has a single endpoint.
- Hourglass: five vertices; two incoming neighbors point to the central anchor, and it points to two outgoing neighbors. The question asks for these two one-hop groups, not an undirected neighborhood or a two-hop source-to-sink answer.

## Exact representatives

### chain

Input `596f0f7f32af69a8af5bd8d1181454943f720e6f942fed9708da8abe581a3072`, observation `0525e17d0769ec3ecdcf73c49f708a3a96c95a51796984a92d1c2ef6c357a6a1`, base `d82623c226f8db0c19e5b74a`. Input JSONL line 14307; observation line 1219. Anchor `Nonudene`. Task `path:Country`. Endpoints: `Zetibafa`.

Reference-induced directed typed edges:

- `Nonudene --NEWS_ABOUT_FUND--> Pedolozi`
- `Polasovo --LOCATED_IN--> Vasuruma`
- `Vasuruma --IN_STATE--> Vedabupe`
- `Vedabupe --IN_COUNTRY--> Zetibafa`
- `Pedolozi --OWNS--> Polasovo`

### star_in

Input `b32c523eae0a8a2db036c7a5f0ae7518812369a055931729829825de1dc20204`, observation `001baafd2800a7989292f4ffe554325a08da32bf5e83300687960b724c901634`, base `eb2eb70a77a243cd621d52ef`. Input JSONL line 28701; observation line 27. Anchor `Zirapafe`. Task `in:1`. Endpoints: `Nilutugi`, `Zunevivo`, `Fofizavu`, `Vutepuge`, `Zususuzu`.

Reference-induced directed typed edges:

- `Nilutugi --PRODUCES--> Zirapafe`
- `Zunevivo --NEWS_ABOUT_PRODUCT--> Zirapafe`
- `Fofizavu --NEWS_ABOUT_PRODUCT--> Zirapafe`
- `Vutepuge --NEWS_ABOUT_PRODUCT--> Zirapafe`
- `Zususuzu --NEWS_ABOUT_PRODUCT--> Zirapafe`

### star_out

Input `9ff3c3a8bb604bb9b9334e7bf04fe25f03876a11e48c873d0fdcbace6fce241b`, observation `003719daf73e923b033f39c14f2809b23fcc73c631bc371a7185fbadd26e8d33`, base `10a5e880cecae1b9be5fb41a`. Input JSONL line 25631; observation line 59. Anchor `Voveduse`. Task `out:1`. Endpoints: `Fuzesamo`, `Gikigipi`, `Loferili`, `Zugufake`, `Lubazilu`.

Reference-induced directed typed edges:

- `Voveduse --NEWS_ABOUT_PRODUCT--> Fuzesamo`
- `Voveduse --NEWS_ABOUT_PRODUCT--> Gikigipi`
- `Voveduse --NEWS_ABOUT_PRODUCT--> Loferili`
- `Voveduse --NEWS_ABOUT_PRODUCT--> Zugufake`
- `Voveduse --NEWS_ABOUT_PRODUCT--> Lubazilu`

### tree_in

Input `da5e4f87752ef3c82a359bf43debf20fde525a3f4ddfbd671dd54297f2b0bce9`, observation `02243979b09065a5e82c0b80dd3a27d2007bf4efcc98ee5a7a095d669f0c75fd`, base `dbdc37152a57eaeb7408cc19`. Input JSONL line 35083; observation line 526. Anchor `Ganebege`. Task `in:2`. Endpoints: `Kagovama`, `Migipipe`, `Zobifefa`.

Reference-induced directed typed edges:

- `Nopepike --REQUIRES--> Ganebege`
- `Kagovama --WORKS_FOR--> Nopepike`
- `Migipipe --WORKS_FOR--> Nopepike`
- `Gezefivu --REQUIRES--> Ganebege`
- `Zobifefa --WORKS_FOR--> Gezefivu`

### tree_out

Input `9bbc184d0d0f0f905b3e7f61f22cd5aa7db4482f3d98140ec83e2ad6b3fb1618`, observation `0ab1dedc705bbdde4c7888b568c895cb0299cfced3d6b3cc88af4f42607f13a4`, base `b2b1b9f27fe9115d49c45611`. Input JSONL line 24914; observation line 2548. Anchor `Vaseroze`. Task `out:2`. Endpoints: `Zamomefu`, `Lidovera`, `Kosoroso`.

Reference-induced directed typed edges:

- `Sabepozi --PRODUCES--> Zamomefu`
- `Vaseroze --NEWS_ABOUT_COMPANY--> Sabepozi`
- `Vaseroze --NEWS_ABOUT_COMPANY--> Dipozugi`
- `Dipozugi --PRODUCES--> Lidovera`
- `Dipozugi --REQUIRES--> Kosoroso`

### rhombus

Input `80be0fc812928c4d1dfa4eb78151265340dac81ddddaebf5b13b79bbe87030b6`, observation `00fccd6d4d75334a19adc2a6d96ea8bda7f6f13cb075b6046851c37347862258`, base `6be2f17b5acec799bf6e7ee7`. Input JSONL line 20610; observation line 229. Anchor `Rezamamu`. Task `out:2`. Endpoints: `Raragamu`.

Reference-induced directed typed edges:

- `Lalesemu --OPERATES_IN_INDUSTRY--> Raragamu`
- `Rezamamu --OWNS--> Lalesemu`
- `Rezamamu --OWNS--> Rukomida`
- `Rukomida --OPERATES_IN_INDUSTRY--> Raragamu`

### hourglass

Input `efdd2b71bfc986685d6d20f606fe1233101c9b773c10375868563a138cb6db95`, observation `019bb66b2f7073776c1307fb3a4b6b19fb7455295a7bdc719002140b9e672206`, base `11cb19a9fce25d714d50532f`. Input JSONL line 38637; observation line 386. Anchor `Tosukino`. Task `both:1`. Endpoints: `Gebipobu`, `Nigiromi`, `Dudodabo`, `Nakevigi`.

Reference-induced directed typed edges:

- `Tosukino --PRODUCES--> Gebipobu`
- `Tosukino --PRODUCES--> Nigiromi`
- `Dudodabo --NEWS_ABOUT_COMPANY--> Tosukino`
- `Nakevigi --NEWS_ABOUT_COMPANY--> Tosukino`

## Code locators

- `graph_motives/graph/motifs.py:13` — `_ok` (through line 17).
- `graph_motives/graph/motifs.py:20` — `sample_chain` (through line 40).
- `graph_motives/graph/motifs.py:43` — `sample_star` (through line 62).
- `graph_motives/graph/motifs.py:65` — `sample_tree` (through line 111).
- `graph_motives/graph/motifs.py:114` — `sample_rhombus` (through line 134).
- `graph_motives/graph/motifs.py:137` — `sample_hourglass` (through line 150).
- `graph_motives/graph/motifs.py:153` — `sample_cycle` (through line 171).
- `graph_motives/graph/motifs.py:174` — `sample_clique` (through line 188).
- `graph_motives/preparation/questions.py:64` — `_templates` (through line 81).
- `graph_motives/preparation/questions.py:84` — `make_question_spec` (through line 133).
- `graph_motives/preparation/questions.py:164` — `evaluate_task` (through line 223).
