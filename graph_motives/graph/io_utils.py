"""Portable JSON/JSONL IO, hashes and TOML configuration."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import tomllib
from pathlib import Path


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def resolve_file(path: Path) -> Path:
    path = Path(path)
    if not path.exists() and Path(str(path) + ".gz").is_file():
        return Path(str(path) + ".gz")
    return path


def open_text(path: Path):
    path = resolve_file(path)
    return (
        gzip.open(path, "rt", encoding="utf-8")
        if path.suffix == ".gz"
        else path.open(encoding="utf-8-sig")
    )


def read_jsonl(path: Path) -> list[dict]:
    with open_text(path) as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_json(path: Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    tmp.replace(path)


def write_jsonl(path: Path, rows) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(tmp, "wt", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    tmp.replace(path)


def load_config(path: Path) -> dict:
    with Path(path).open("rb") as stream:
        return tomllib.load(stream)


def load_env_file(path: Path) -> None:
    """Load only the explicitly requested file; never search parent directories."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
