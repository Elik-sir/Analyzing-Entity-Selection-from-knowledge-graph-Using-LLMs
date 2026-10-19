"""Keep disposable fixtures in the project with inherited Windows workspace ACLs."""

import os
import shutil
import tempfile
import uuid
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def inherited_windows_temp_permissions(monkeypatch):
    """Use inherited workspace ACLs for unittest TemporaryDirectory fixtures."""
    if os.name != "nt":
        return
    root = Path(__file__).resolve().parents[1] / "tmp"
    root.mkdir(exist_ok=True)

    def mkdir(suffix=None, prefix=None, dir=None):
        path = Path(dir or root) / ((prefix or "tmp") + uuid.uuid4().hex + (suffix or ""))
        path.mkdir()
        return str(path)

    monkeypatch.setattr(tempfile, "mkdtemp", mkdir)


@pytest.fixture
def tmp_path():
    root = (Path(__file__).resolve().parents[1] / "tmp").resolve()
    root.mkdir(exist_ok=True)
    path = root / ("test-" + uuid.uuid4().hex)
    path.mkdir()
    try:
        yield path
    finally:
        target = path.resolve()
        if target.is_relative_to(root) and target != root:
            shutil.rmtree(target)
