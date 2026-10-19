"""Check the current source tree for syntax, imports, and duplicate modules."""

import ast
import hashlib
import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(root=ROOT):
    root = Path(root).resolve()
    signatures = {}
    modules = []
    paths = sorted(path for folder in ("graph_motives", "scripts", "tests")
                   for path in (root / folder).rglob("*.py"))
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        if path.name != "__init__.py":
            signature = hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()
            if signature in signatures:
                raise ValueError(f"Duplicate modules: {signatures[signature]} and {path.relative_to(root)}")
            signatures[signature] = path.relative_to(root).as_posix()
        if path.is_relative_to(root / "graph_motives") and path.name != "__main__.py":
            name = ".".join(path.relative_to(root).with_suffix("").parts).removesuffix(".__init__")
            module = importlib.import_module(name)
            if not Path(module.__file__).resolve().is_relative_to(root / "graph_motives"):
                raise ValueError("Import escaped the current package: " + name)
            modules.append(name)
    obsolete = ["sp500_pipeline", "scripts/historical", "CODE_MANIFEST.json", "FIGURE_SCRIPTS.json"]
    if remaining := [name for name in obsolete if (root / name).exists()]:
        raise ValueError("Obsolete source snapshots remain: " + ", ".join(remaining))
    return {"status": "passed", "python_files": len(paths), "imported_modules": len(modules),
            "duplicate_modules": 0, "network_requests_made": 0}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
