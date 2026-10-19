"""Command-line entry point for graph_motives.verify_protocols."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    runpy.run_module("graph_motives.verify_protocols", run_name="__main__")
