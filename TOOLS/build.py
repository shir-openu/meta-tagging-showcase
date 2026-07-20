#!/usr/bin/env python3
"""Run the reproducible audit and index build in dependency order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def run(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(HERE / script), *args], check=True)


def main() -> None:
    run("audit_statistics.py")
    run("validate_corpus.py")
    run("recalculate_section5.py")
    run("build_index.py")
    run("build_graph.py")
    run("build_audit_report.py")
    run("patch_paper_statistics.py")


if __name__ == "__main__":
    main()
