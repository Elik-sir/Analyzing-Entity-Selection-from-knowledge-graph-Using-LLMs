"""Validate evidence-ledger structure and local provenance, not scientific truth."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

KINDS = {"implementation", "configuration", "result", "literature", "venue", "draft"}
TYPES = {"implementation", "historical", "empirical", "literature", "venue", "hypothesis"}
STATUSES = {"supported", "pending", "unsupported", "conflicted"}
VERIFICATIONS = {"inspected", "recomputed", "reported", "pending"}


def validate(root, notes):
    errors = []

    def require(ok, message):
        if not ok:
            errors.append(message)

    document = json.loads((notes / "evidence_register.json").read_text(encoding="utf-8"))
    require(document.get("schema_version") == 1, "Unsupported evidence schema")
    evidence = {}
    for item in document["evidence"]:
        eid = item.get("id")
        require(isinstance(eid, str) and bool(eid), "Missing evidence ID")
        require(eid not in evidence, f"Duplicate evidence ID: {eid}")
        evidence[eid] = item
        require(item.get("kind") in KINDS, f"{eid}: invalid evidence kind")
        require(item.get("verification") in VERIFICATIONS, f"{eid}: invalid verification")
        require(bool(item.get("locator")), f"{eid}: missing locator")
        require(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", item.get("checked_on", ""))), f"{eid}: missing check date")
        require(bool(item.get("path")) != bool(item.get("url")), f"{eid}: supply exactly one path or URL")
        if item.get("path"):
            path = (root / item["path"]).resolve()
            if not path.is_relative_to(root):
                errors.append(f"{eid}: path escapes repository")
                continue
            if path.name == ".env" or path.name.startswith(".env."):
                errors.append(f"{eid}: credentials/environment files are not research evidence")
                continue
            require(path.is_file(), f"{eid}: source file missing")
            if path.is_file():
                with path.open("rb") as stream:
                    actual = hashlib.file_digest(stream, "sha256").hexdigest()
                require(actual == item.get("sha256"), f"{eid}: source hash missing or changed")
        if item.get("url"):
            parsed = urlparse(item["url"])
            require(parsed.scheme in {"http", "https"} and bool(parsed.netloc), f"{eid}: invalid source URL")
    for eid, item in evidence.items():
        for upstream in item.get("upstream_evidence_ids", []):
            require(upstream in evidence, f"{eid}: missing upstream evidence {upstream}")

    claims = []
    ids = set()
    for line in (notes / "claims.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        claim = json.loads(line)
        claims.append(claim)
        cid = claim.get("id")
        require(isinstance(cid, str) and bool(cid), "Missing claim ID")
        require(cid not in ids, f"Duplicate claim ID: {cid}")
        ids.add(cid)
        require(claim.get("type") in TYPES, f"{cid}: invalid claim type")
        require(claim.get("status") in STATUSES, f"{cid}: invalid status")
        for field in ("text", "scope", "reason"):
            require(bool(claim.get(field)), f"{cid}: missing {field}")
        require(isinstance(claim.get("numeric"), bool), f"{cid}: numeric must be boolean")
        refs = claim.get("evidence_ids", [])
        require(isinstance(refs, list), f"{cid}: evidence_ids must be a list")
        if not isinstance(refs, list):
            refs = []
        for ref in refs:
            require(ref in evidence, f"{cid}: missing evidence {ref}")
        if claim.get("status") == "supported":
            require(bool(refs), f"{cid}: supported claim has no evidence")
            require(all(evidence.get(ref, {}).get("verification") != "pending" for ref in refs),
                    f"{cid}: supported claim cites pending evidence")
            needed = {"implementation": "implementation", "empirical": "result", "historical": "result",
                      "literature": "literature", "venue": "venue"}.get(claim.get("type"))
            require(claim.get("type") != "hypothesis", f"{cid}: a hypothesis cannot be a supported finding")
            if needed:
                require(any(evidence.get(ref, {}).get("kind") == needed for ref in refs), f"{cid}: missing {needed} evidence")
        if claim.get("numeric") and claim.get("type") == "empirical":
            numbers = claim.get("numbers", [])
            require(bool(numbers), f"{cid}: numerical result has no provenance records")
            for number in numbers:
                ref = number.get("evidence_id")
                require(ref in refs and evidence.get(ref, {}).get("kind") == "result", f"{cid}: numeric evidence must reference a result")
                for field in ("value", "metric", "locator", "denominator", "derivation"):
                    require(field in number and number[field] is not None and number[field] != "", f"{cid}: numeric record missing {field}")

    state = json.loads((notes / "workflow_state.json").read_text(encoding="utf-8"))
    require(isinstance(state.get("analysis_complete"), bool), "analysis_complete must be boolean")
    require(isinstance(state.get("full_writing_ready"), bool), "full_writing_ready must be boolean")
    require(bool(state.get("gate_rationale")), "Writing gate needs a rationale")
    if state.get("full_writing_ready"):
        require(state.get("analysis_complete") is True, "Writing gate opened before analysis completed")
    return {"status": "failed" if errors else "passed", "evidence_records": len(evidence),
            "claims": len(claims), "errors": errors,
            "scope": "Structural integrity only; semantic support and full-text claim coverage require review."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--notes", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    notes = args.notes.resolve() if args.notes else root / "paper/research_notes"
    try:
        result = validate(root, notes)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {"status": "failed", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"] == "passed" else 1)
