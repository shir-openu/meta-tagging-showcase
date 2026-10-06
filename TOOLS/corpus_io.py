#!/usr/bin/env python3
"""Read and write the canonical corpus and its derived search data.

The public repository originally contained only generated HTML.  This module
recovers the embedded record array once, then treats DATA/corpus.json as the
source of truth for subsequent builds.
"""

from __future__ import annotations

import html
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SEARCH_HTML = ROOT / "SEARCH.html"
CORPUS_JSON = ROOT / "DATA" / "corpus.json"
AUDIT_JSON = ROOT / "DATA" / "statistics_audit.json"
INDEX_DIR = ROOT / "DATA" / "index"


def extract_embedded_index(path: Path = SEARCH_HTML) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="idx" type="application/json">(.*?)</script>',
        source,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError(f"No embedded search index found in {path}")
    return json.loads(html.unescape(match.group(1)))


def bootstrap_corpus() -> dict[str, Any]:
    index = extract_embedded_index()
    records: list[dict[str, Any]] = []
    for record in index["records"]:
        annotations = []
        for term in record.get("st", []):
            annotations.append(
                {
                    "term": term,
                    "evidence": record.get("ev", {}).get(term, ""),
                    "decision": "needs-review",
                    "role": "unclassified",
                    "reason": "reconstructed from the legacy embedded index",
                }
            )
        records.append(
            {
                "id": record["id"],
                "title": record.get("t", ""),
                "discipline": record.get("d", ""),
                "year": record.get("y"),
                "authors": record.get("a", ""),
                "url": record.get("u", ""),
                "key_terms": record.get("kt", []),
                "phenomenon": record.get("ph", ""),
                "claim_type": record.get("cl", ""),
                "method": record.get("m", ""),
                "statistics": annotations,
            }
        )
    return {
        "schema_version": "1.0.0",
        "source": "reconstructed from SEARCH.html",
        "legacy_generated": index.get("generated"),
        "vocabularies": {
            "disciplines": index.get("disciplines", []),
            "discipline_colors": index.get("colors", {}),
            "statistics": index.get("stats", []),
            "statistic_groups": index.get("stat_groups", []),
            "claim_types": index.get("claims", []),
        },
        "presets": index.get("presets", []),
        "records": records,
    }


def load_corpus(path: Path = CORPUS_JSON) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def accepted_statistics(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in record.get("statistics", [])
        if item.get("decision") == "accepted"
    ]


def text_tokens(value: str) -> set[str]:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return {
        token
        for token in re.findall(r"[^\W_]+(?:[-'][^\W_]+)*", normalized, re.UNICODE)
        if len(token) >= 2
    }


def build_index_parts(
    corpus: dict[str, Any], generated: str, shard_size: int = 500
) -> tuple[dict[str, Any], dict[str, list[int]], list[list[dict[str, Any]]]]:
    """Build a postings index and lazy-loadable metadata shards.

    Numeric document identifiers are assigned in display order.  Every postings
    list is therefore naturally sorted, making intersections deterministic and
    allowing the browser to fetch only the record shards required for the
    current result page.
    """
    source_records = sorted(
        corpus["records"],
        key=lambda item: (
            item.get("discipline", ""),
            item.get("year") or 0,
            item.get("title", ""),
            item["id"],
        ),
    )
    records: list[dict[str, Any]] = []
    postings: dict[str, set[int]] = defaultdict(set)
    for doc_id, record in enumerate(source_records):
        accepted = accepted_statistics(record)
        terms = sorted({item["term"] for item in accepted})
        evidence = {item["term"]: item.get("evidence", "") for item in accepted}
        evidence_grounding = {
            item["term"]: item.get("provenance", {}).get(
                "grounding_status", "unknown"
            )
            for item in accepted
        }
        compact = {
            "doc": doc_id,
            "id": record["id"],
            "t": record.get("title", ""),
            "d": record.get("discipline", ""),
            "y": record.get("year"),
            "a": record.get("authors", ""),
            "u": record.get("url", ""),
            "st": terms,
            "kt": record.get("key_terms", []),
            "ph": record.get("phenomenon", ""),
            "cl": record.get("claim_type", ""),
            "m": record.get("method", ""),
            "ev": evidence,
            "eg": evidence_grounding,
        }
        records.append(compact)
        postings[f"discipline:{compact['d']}"].add(doc_id)
        if compact["cl"]:
            postings[f"claim:{compact['cl']}"].add(doc_id)
        for term in terms:
            postings[f"statistic:{term}"].add(doc_id)
        searchable = " ".join(
            [
                compact["t"],
                compact["a"],
                " ".join(compact["kt"]),
                compact["ph"],
                compact["m"],
            ]
        )
        for token in text_tokens(searchable):
            postings[f"text:{token}"].add(doc_id)

    vocab = corpus["vocabularies"]
    shards = [records[i : i + shard_size] for i in range(0, len(records), shard_size)]
    manifest = {
        "schema_version": "1.0.0",
        "generated": generated,
        "record_count": len(records),
        "accepted_assignment_count": sum(len(record["st"]) for record in records),
        "shard_size": shard_size,
        "shards": [f"records-{i:05d}.json" for i in range(len(shards))],
        "disciplines": vocab["disciplines"],
        "discipline_by_doc": [
            vocab["disciplines"].index(record["d"]) for record in records
        ],
        "colors": vocab["discipline_colors"],
        "stats": vocab["statistics"],
        "stat_groups": vocab["statistic_groups"],
        "presets": corpus.get("presets", []),
        "claims": vocab["claim_types"],
    }
    return (
        manifest,
        {key: sorted(value) for key, value in sorted(postings.items())},
        shards,
    )
