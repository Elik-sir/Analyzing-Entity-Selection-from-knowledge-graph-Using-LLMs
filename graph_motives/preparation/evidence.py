"""Deterministic graph-derived evidence; native metadata remains a separate condition."""

import hashlib
import re
from copy import deepcopy

from .contracts import ContractError, PublicTask, canonical_json, fingerprint

EVIDENCE_VERSION = "controlled_graph_evidence_v1"
ALIAS_VERSION = "pronounceable_alias_v2"
_ALIAS_CONSONANTS = "bdfgklmnprstvz"
_ALIAS_VOWELS = "aeiou"
_ALIAS_ATTEMPTS = 1024
_RESERVED_ALIASES = frozenset(
    {
        "answer",
        "anchor",
        "candidate",
        "company",
        "country",
        "entity",
        "false",
        "fund",
        "industry",
        "news",
        "none",
        "null",
        "person",
        "product",
        "question",
        "reference",
        "relation",
        "resource",
        "sector",
        "selected",
        "source",
        "state",
        "target",
        "true",
        "unknown",
    }
)
RELATION_PHRASES = {
    "PRODUCES": "lists {t} among its products",
    "REQUIRES": "uses {t} as a resource",
    "IN_STATE": "is situated in the state {t}",
    "LOCATED_IN": "has its main location in {t}",
    "WORKS_FOR": "works for {t}",
    "OWNS": "has a holding in {t}",
    "OPERATES_IN_INDUSTRY": "operates in the industry {t}",
    "PART_OF": "belongs to the sector {t}",
    "IN_COUNTRY": "is situated in the country {t}",
    "NEWS_ABOUT_LOCATION": "discusses the location {t}",
    "NEWS_ABOUT_RESOURCE": "discusses the resource {t}",
    "NEWS_ABOUT_COMPANY": "discusses the company {t}",
    "NEWS_ABOUT_PRODUCT": "discusses the product {t}",
    "NEWS_ABOUT_FUND": "discusses the fund {t}",
    "NEWS_ABOUT_INDUSTRY": "discusses the industry {t}",
    "NEWS_ABOUT_SECTOR": "discusses the sector {t}",
    "LINK": "has a recorded connection to {t}",
}


def _alias_key(name):
    return " ".join(name.split()).casefold()


def _alias_signatures(name):
    """Shared wildcard signatures detect one-character substitutions in O(length)."""
    return {name[:index] + "*" + name[index + 1 :] for index in range(len(name))}


def _pseudonym_candidate(nid, seed, attempt):
    # Four CV syllables, uniformly selected from a versioned 70**4 namespace.
    # The hash/retry counter stays private; no order, type, role or gold is input.
    digest = hashlib.sha256(canonical_json([ALIAS_VERSION, seed, nid, attempt]).encode("utf-8"))
    value = int.from_bytes(digest.digest(), "big")
    syllables = []
    for _ in range(4):
        value, syllable = divmod(value, len(_ALIAS_CONSONANTS) * len(_ALIAS_VOWELS))
        consonant, vowel = divmod(syllable, len(_ALIAS_VOWELS))
        syllables.append(_ALIAS_CONSONANTS[consonant] + _ALIAS_VOWELS[vowel])
    return "".join(syllables).capitalize()


def build_pseudonym_map(entity_ids, seed=20261003, *, forbidden_names=(), existing=None):
    """Freeze a global dictionary of eight-letter invented names, without IDs.

    Pass all snapshot IDs and real names once, then reuse the dictionary in every
    condition. Sorted IDs make retries deterministic. When extending a snapshot,
    pass its frozen ``existing`` dictionary to preserve names even on collisions;
    stateless rebuilding of a changed universe does not promise that stability.
    Exact real/reserved names and one-character near-duplicates are rejected.
    This lexical check does not guarantee semantic neutrality or equal token cost.
    """
    ids = set(entity_ids)
    if type(seed) is not int or any(not isinstance(nid, str) or not nid.strip() for nid in ids):
        raise ContractError("Pseudonyms require an integer seed and nonempty string IDs")
    forbidden = list(forbidden_names)
    if any(not isinstance(name, str) for name in forbidden):
        raise ContractError("Forbidden pseudonym names must be strings")
    blocked = (
        {_alias_key(name) for name in forbidden}
        | {_alias_key(nid) for nid in ids}
        | _RESERVED_ALIASES
    )
    if existing is not None and not isinstance(existing, dict):
        raise ContractError("Frozen pseudonym dictionary must be a mapping")
    names = {} if existing is None else dict(existing)
    if not set(names) <= ids:
        raise ContractError("Frozen pseudonym dictionary contains IDs outside the universe")
    used, signatures = set(), set()
    pattern = rf"[{_ALIAS_CONSONANTS.upper()}][{_ALIAS_VOWELS}](?:[{_ALIAS_CONSONANTS}][{_ALIAS_VOWELS}]){{3}}"

    def register(name):
        key = _alias_key(name)
        used.add(key)
        signatures.update(_alias_signatures(key))

    for nid in sorted(names):
        name = names[nid]
        if not isinstance(name, str) or re.fullmatch(pattern, name) is None:
            raise ContractError("Invalid frozen pronounceable pseudonym")
        key = _alias_key(name)
        if key in blocked or key in used or _alias_signatures(key) & signatures:
            raise ContractError("Frozen pseudonyms collide, are too similar or use forbidden names")
        register(name)
    for nid in sorted(ids - set(names)):
        for attempt in range(_ALIAS_ATTEMPTS):
            name = _pseudonym_candidate(nid, seed, attempt)
            key = _alias_key(name)
            if key not in blocked and key not in used and not (_alias_signatures(key) & signatures):
                names[nid] = name
                register(name)
                break
        else:
            raise ContractError(
                "Pronounceable pseudonym retries exhausted; freeze a new alias version"
            )
    return {nid: names[nid] for nid in sorted(names)}


def rewrite_aliases(value, alias_map):
    """Boundary-aware longest-match helper; native text is NOT used in controlled cards."""
    if isinstance(value, dict):
        return {k: rewrite_aliases(v, alias_map) for k, v in value.items()}
    if isinstance(value, list):
        return [rewrite_aliases(v, alias_map) for v in value]
    if isinstance(value, str) and alias_map:
        pattern = (
            r"(?<!\w)(?:"
            + "|".join(re.escape(k) for k in sorted(alias_map, key=lambda k: (-len(k), k)))
            + r")(?!\w)"
        )
        return re.sub(pattern, lambda m: alias_map[m.group(0)], value)
    return value


def build_fact_ledger(graph, selected_universe=None, seed=20261003):
    ids = set(graph.nodes if selected_universe is None else selected_universe)
    if not ids <= set(graph.nodes):
        raise ContractError("Unknown ledger entity")
    nodes = {}
    for nid in sorted(ids):
        node = graph.nodes[nid]
        nodes[nid] = {
            "name": node["name"],
            "type": node["type"],
            "match_token": "v-" + fingerprint(["public_link_token_v1", seed, nid])[:24],
            "provenance": {
                "source": "snapshot_node",
                "node_id": nid,
                "properties_sha256": fingerprint(node["properties"]),
            },
        }
    if len({n["match_token"] for n in nodes.values()}) != len(nodes):
        raise ContractError("Link token collision")
    edges = []
    for source, relation, target in sorted(graph.edges):
        if source in ids and target in ids:
            if relation not in RELATION_PHRASES:
                raise ContractError(f"No verified prose template for relation {relation}")
            edges.append(
                {
                    "source": source,
                    "relation": relation,
                    "target": target,
                    "provenance": {
                        "source": "snapshot_relationship",
                        "edge_sha256": fingerprint([source, relation, target]),
                    },
                }
            )
    value = {
        "schema_version": EVIDENCE_VERSION,
        "seed": seed,
        "origin": "controlled_graph_derived",
        "nodes": nodes,
        "edges": edges,
        "projection_policy": "all_typed_edges_induced_by_public_candidate_pool",
    }
    value["ledger_sha256"] = fingerprint(value)
    return value


def derive_linking_attributes(ledger):
    return {nid: {"identity_token": row["match_token"]} for nid, row in ledger["nodes"].items()}


def candidate_edges(graph, ids):
    return sorted(graph.induced_edges(set(ids)))


def render_base_cards(ledger, candidate_ids, names):
    return [
        {
            "name": names[nid],
            "type": ledger["nodes"][nid]["type"],
            "facts": {
                "description": "This entry describes an entity of type "
                + ledger["nodes"][nid]["type"]
                + "."
            },
            "labels": [ledger["nodes"][nid]["type"]],
        }
        for nid in candidate_ids
    ]


def render_matched_cards(
    ledger, candidate_ids, edges, names, *, evidence="explicit", location="subject", edge_index=None
):
    """Identical factual edges across E/L; names/format are the manipulation."""
    if evidence not in {"explicit", "text", "keys", "names+types"}:
        raise ContractError("Unknown controlled evidence")
    if location not in {"subject", "object", "both", "none"}:
        raise ContractError("Unknown relation location")
    if evidence in {"text", "keys"} and location not in {"none", "subject"}:
        raise ContractError("Text/key layouts are fixed to the subject in this protocol")
    ids = set(candidate_ids)
    if len(candidate_ids) != len(ids) or not ids <= set(names):
        raise ContractError("Invalid candidate universe")
    edges = sorted(set(tuple(e) for e in edges))
    if any(s not in ids or t not in ids for s, _, t in edges):
        raise ContractError("Out-of-pool edge")
    known = (
        edge_index
        if edge_index is not None
        else {(e["source"], e["relation"], e["target"]) for e in ledger["edges"]}
    )
    if not set(edges) <= known:
        raise ContractError("Requested facts are absent from the frozen ledger")
    cards = render_base_cards(ledger, candidate_ids, names)
    by_id = dict(zip(candidate_ids, cards))
    if evidence == "names+types":
        for card in cards:
            card["facts"] = {}
        return cards
    if evidence == "keys":
        for nid, card in by_id.items():
            card["facts"]["identity_token"] = ledger["nodes"][nid]["match_token"]
    for source, relation, target in edges:
        if evidence == "explicit":
            hosts = {"subject": [source], "object": [target], "both": [source, target]}.get(
                location
            )
            if hosts is None:
                raise ContractError("Explicit evidence needs a relation location")
            assertion = {"source": names[source], "relation": relation, "target": names[target]}
            for host in set(hosts):
                by_id[host]["facts"].setdefault("relations", []).append(deepcopy(assertion))
        elif evidence == "text":
            sentence = (
                names[source] + " " + RELATION_PHRASES[relation].format(t=names[target]) + "."
            )
            by_id[source]["facts"].setdefault("statements", []).append(sentence)
        else:
            by_id[source]["facts"].setdefault("link_attributes", []).append(
                {"predicate": relation, "value": ledger["nodes"][target]["match_token"]}
            )
    return cards


def reconstruct_evidence(cards, names, *, evidence):
    """Strictly decode actual controlled serialization; never consult gold edges."""
    by_name = {name: nid for nid, name in names.items()}
    if len(by_name) != len(names):
        raise ContractError("Nonunique public names")
    edges, tokens = set(), {}
    for card in cards:
        if card["name"] not in by_name:
            raise ContractError("Unknown public candidate")
        token = card["facts"].get("identity_token")
        if token is not None:
            if token in tokens:
                raise ContractError("Ambiguous joining value")
            tokens[token] = by_name[card["name"]]
    if evidence == "names+types":
        return edges
    # Precompute the grammar over displayed names, independent of the private ledger.
    sentences = {}
    if evidence == "text":
        # Avoid the quadratic candidate-world grammar: each sentence's exact
        # subject and suffix are matched to the finite approved templates.
        ordered = sorted(by_name, key=lambda n: (-len(n), n))
    for card in cards:
        facts, host = card["facts"], by_name[card["name"]]
        if evidence == "explicit":
            for value in facts.get("relations", []):
                if set(value) != {"source", "relation", "target"}:
                    raise ContractError("Invalid public relation")
                if value["source"] not in by_name or value["target"] not in by_name:
                    raise ContractError("Relation endpoint absent from public universe")
                if value["relation"] not in RELATION_PHRASES:
                    raise ContractError("Unknown public relation")
                edges.add((by_name[value["source"]], value["relation"], by_name[value["target"]]))
        elif evidence == "keys":
            for value in facts.get("link_attributes", []):
                if set(value) != {"predicate", "value"}:
                    raise ContractError("Invalid joining attribute")
                if value["predicate"] not in RELATION_PHRASES:
                    raise ContractError("Unknown joining predicate")
                # Missing matching card after an ablation means evidence is unavailable.
                if value["value"] in tokens:
                    edges.add((host, value["predicate"], tokens[value["value"]]))
        elif evidence == "text":
            for sentence in facts.get("statements", []):
                if sentence in sentences:
                    edges.add(sentences[sentence])
                    continue
                matches = []
                for source in ordered:
                    if not sentence.startswith(source + " "):
                        continue
                    for relation, template in RELATION_PHRASES.items():
                        prefix, suffix = template.split("{t}")
                        beginning = source + " " + prefix
                        ending = suffix + "."
                        if sentence.startswith(beginning) and sentence.endswith(ending):
                            target = sentence[len(beginning) : -len(ending)]
                            if target in by_name:
                                matches.append((by_name[source], relation, by_name[target]))
                if len(set(matches)) != 1:
                    raise ContractError("Text is not a unique approved fact serialization")
                edge = matches[0]
                if edge[0] != host:
                    raise ContractError("Statement on incorrect host")
                sentences[sentence] = edge
                edges.add(edge)
        else:
            raise ContractError("Unknown evidence decoder")
    return edges


def validate_evidence_reconstruction(cards, names, edges, evidence):
    try:
        decoded = reconstruct_evidence(cards, names, evidence=evidence)
        expected = set() if evidence == "names+types" else set(tuple(e) for e in edges)
        return {
            "status": "passed" if decoded == expected else "failed",
            "missing_edges": [list(e) for e in sorted(expected - decoded)],
            "extra_edges": [list(e) for e in sorted(decoded - expected)],
        }
    except (ContractError, KeyError, TypeError, ValueError):
        return {"status": "failed", "errors": ["invalid_serialized_evidence"]}


def audit_identity_leaks(public, original_names, forbidden_ids=()):
    """Exact identity channels; no claim that regex proves semantic anonymity."""
    text = canonical_json(public)
    leaked_ids = [nid for nid in forbidden_ids if nid in text]
    # Compare values, not keys/types. Full names are privacy targets; short names
    # can be ordinary words, so only boundaries and case-sensitive matches apply.
    values = []

    def collect(value):
        if isinstance(value, dict):
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
        elif isinstance(value, str):
            values.append(value)

    collect(public)
    leaked_names = []
    for name in original_names:
        if len(name) < 3:
            if name in values:
                leaked_names.append(name)
        elif any(re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", value) for value in values):
            leaked_names.append(name)
    return {
        "status": "passed" if not leaked_ids and not leaked_names else "failed",
        "identity_leak_count": len(leaked_names),
        "private_id_leak_count": len(leaked_ids),
        "scope": "exact channels; controlled cards copy no native properties/text",
    }


def build_matched_cards(*args, **kwargs):
    return render_matched_cards(*args, **kwargs)


def serialize_kg_context(question, cards, format_note=None):
    # PublicTask validates schema/private fields, exact names and JSON values.
    public = PublicTask(question, deepcopy(cards)).to_dict()
    if format_note:
        if not isinstance(format_note, str):
            raise ContractError("Format note must be text")
        public["format_note"] = format_note
    return public
