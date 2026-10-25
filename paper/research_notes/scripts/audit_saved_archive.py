"""Read-only, standard-library audit of the saved archive; write JSON to stdout.

This aggregates cached scores. It does not import project code, call a model,
connect to Neo4j, or independently rescore raw responses.
"""

import argparse
import csv
import gzip
import hashlib
import json
import platform
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def audit(root):
    archive = root / "results"
    manifest = json.loads((archive / "MANIFEST.json").read_text(encoding="utf-8"))
    entries = manifest["files"]
    if isinstance(entries, dict):
        entries = [dict(value, path=key) for key, value in entries.items()]
    checks = []
    for entry in entries:
        name = entry.get("path", entry.get("name", entry.get("file")))
        path = (archive / name).resolve()
        if not path.is_relative_to(archive.resolve()):
            raise ValueError("Manifest path escapes archive")
        actual = sha256(path)
        size = path.stat().st_size
        expected_size = entry.get("bytes", entry.get("size_bytes", entry.get("size")))
        if expected_size is None:
            raise ValueError(f"No expected size for {name}")
        checks.append({"path": path.relative_to(root).as_posix(), "sha256": actual,
                       "bytes": size, "passed": actual == entry["sha256"] and size == expected_size})
    if not all(item["passed"] for item in checks):
        raise ValueError("Archive manifest mismatch")

    series = Counter()
    groups = defaultdict(lambda: {"N": 0, "valid": 0, "sum_f1": 0.0, "sum_exact": 0.0})
    with gzip.open(archive / "observations.jsonl.gz", "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            series[row["series_id"]] += 1
            if row["series_id"] != "full_braw":
                continue
            key = (row["model"], row["condition"], row["noise"])
            group = groups[key]
            group["N"] += 1
            group["valid"] += bool(row["valid"])
            if row["valid"]:
                group["sum_f1"] += float(row["metrics"].get("f1") or 0)
                group["sum_exact"] += float(row["metrics"].get("exact") or 0)
    contrasts = []
    for (model, condition, noise), values in sorted(groups.items()):
        contrasts.append({"selector": {"series_id": "full_braw", "model": model,
                                       "condition": condition, "noise": noise},
                          **values, "f1": values["sum_f1"] / values["N"],
                          "exact": values["sum_exact"] / values["N"]})
    with (archive / "coverage.csv").open(encoding="utf-8-sig", newline="") as stream:
        coverage = list(csv.DictReader(stream))
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_revision": revision,
        "python_version": platform.python_version(),
        "method": "Stream archived observations; sum cached valid metrics / all planned N. No raw-response rescoring or inferential test.",
        "command": "python paper/research_notes/scripts/audit_saved_archive.py --root .",
        "script_sha256": sha256(Path(__file__)),
        "manifest_sha256": sha256(archive / "MANIFEST.json"),
        "file_checks": checks,
        "observations": sum(series.values()),
        "series_counts": dict(sorted(series.items())),
        "full_braw": contrasts,
        "coverage_csv_rows": coverage,
        "saved_validation_report": json.loads((archive / "VALIDATION.json").read_text(encoding="utf-8")),
        "limitations": ["Saved verification is not rerun here.", "Cached score aggregation is not independent rescoring.",
                        "No paired confidence intervals or significance tests.", "No claim of historical provenance beyond inspected artifacts."]
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(audit(args.root.resolve()), ensure_ascii=False, indent=2))
