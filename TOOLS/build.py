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
    # Reproducible build: regenerates the derived, deterministic artifacts from the
    # resolved corpus and passes the 7-test suite from a clean copy.
    run("validate_corpus.py")     # invariant validation of every record + resolved decision
    run("build_index.py")         # inverted index (sorted postings, record shards)
    run("build_graph.py")         # typed adjacency export (implemented relations only)
    run("build_audit_report.py")  # report_statistics.html from the frozen audit
    #
    # NOT part of the reproducible build (one-time, human-adjudicated / full-text steps):
    #   audit_statistics.py     -- rule-based + LLM-assisted ADJUDICATION of statistical-tag
    #                              candidates; its decisions are frozen in
    #                              statistics_audit_overrides.json (see README "Reproducibility").
    #   recalculate_section5.py -- recomputes the grounding audit against each paper's FULL TEXT;
    #                              since full text is not redistributed (rights), section5_statistics.json
    #                              ships as a frozen, human-adjudicated artifact.
    #   patch_paper_statistics.py -- injects audited stats into the per-paper pages (a publishing step,
    #                              not needed to reproduce the index/graph/report).
    # Run those explicitly only when re-auditing against full text.


if __name__ == "__main__":
    main()
