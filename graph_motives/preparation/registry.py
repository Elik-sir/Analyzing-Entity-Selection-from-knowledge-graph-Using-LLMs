"""KG cell definitions; these are conditions, not completed experiments."""

from dataclasses import asdict, dataclass

FULL_SIZES = {
    "chain": [3, 4, 5, 6],
    "star_in": list(range(3, 11)),
    "star_out": list(range(3, 11)),
    "tree_in": list(range(5, 11)),
    "tree_out": list(range(5, 11)),
    "rhombus": [4],
    "hourglass": [5],
}
CORE_SIZES = {motif: 6 for motif in FULL_SIZES} | {"rhombus": 4, "hourglass": 5}
TARGETED_SIZES = {
    "chain": [3, 4, 5, 6], "star_in": [3, 6, 10], "star_out": [3, 6, 10],
    "tree_in": [5, 6, 10], "tree_out": [5, 6, 10],
}
LEGACY_SIZE_MOTIFS = {
    "K1": ["chain", "star_in", "star_out", "tree_in", "tree_out"],
    "K3": ["star_in", "star_out", "tree_in", "tree_out"],
    "K4": ["star_in", "star_out", "tree_in", "tree_out"],
    "K5": ["chain", "star_out", "tree_in"],
}
STAGES = ("selection", "answer", "judge")


@dataclass(frozen=True)
class CellDefinition:
    cell_id: str
    names: str
    evidence: str
    noise: str
    location: str
    question: str
    protocol: str = "selection_v1_planned"

    def to_dict(self):
        return asdict(self)


CELLS = {}


def _register(name, identity, evidence, noise, location, question, protocol=None):
    cell = CellDefinition(name, identity, evidence, noise, location, question,
                          protocol or "selection_v1_planned")
    CELLS[name] = cell


_register("Braw", "real", "native_metadata", "per_item", "native", "native",
          "nodes_only_text_answer_v2_legacy_preserved")
_register("Braw+E", "real", "native_metadata+explicit", "per_item", "subject", "native")
_register("R0", "real", "names+types", "disconnected", "none", "slots",
          "closed_names_types_v1_planned")
_register("K0", "pseudo", "names+types", "disconnected", "none", "slots",
          "closed_names_types_v1_planned")
_register("R1-matched", "real", "explicit", "disconnected", "subject", "slots")
_register("R2-matched", "real", "explicit", "adjacent", "subject", "slots")
for name, evidence, noise, location, question in (
    ("K1", "explicit", "disconnected", "subject", "slots"),
    ("K2", "explicit", "adjacent", "subject", "slots"),
    ("K3", "explicit", "disconnected", "object", "slots"),
    ("K4", "explicit", "disconnected", "both", "slots"),
    ("K5", "text", "disconnected", "none", "slots"),
    ("K6", "text", "adjacent", "none", "slots"),
    ("K7", "explicit", "disconnected", "subject", "goal"),
    ("K8", "text", "disconnected", "none", "goal"),
    ("K5k", "keys", "disconnected", "none", "slots"),
):
    _register(name, "pseudo", evidence, noise, location, question)

CONTRASTS = {
    "E_slots": ["K1", "K5"], "E_goal": ["K7", "K8"],
    "Q_explicit": ["K1", "K7"], "Q_text": ["K5", "K8"],
    "A_explicit": ["K1", "K2"], "A_text": ["K5", "K6"],
    "L": ["K1", "K3", "K4"], "mask_disconnected": ["R1-matched", "K1"],
    "mask_adjacent": ["R2-matched", "K2"], "closed_book": ["R0", "K0"],
    "text_keys": ["K5", "K5k"],
}
