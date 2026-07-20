#!/usr/bin/env python3
"""Validate corpus invariants without optional third-party dependencies."""

from __future__ import annotations

from collections import Counter

from corpus_io import load_corpus


def main() -> None:
    corpus = load_corpus()
    errors: list[str] = []
    records = corpus.get("records", [])
    ids = [record.get("id", "") for record in records]
    for paper_id, count in Counter(ids).items():
        if not paper_id or count != 1:
            errors.append(f"invalid/non-unique paper id: {paper_id!r} ({count})")

    vocab = corpus.get("vocabularies", {})
    disciplines = set(vocab.get("disciplines", []))
    statistics = set(vocab.get("statistics", []))
    claims = set(vocab.get("claim_types", []))
    allowed_decisions = {"accepted", "rejected"}
    allowed_roles = {
        "focal-use",
        "substantive-mention",
        "bibliography",
        "non-statistical-sense",
        "unclassified",
        "symbol-collision",
        "insufficient-evidence",
        "lexical-significance",
    }
    allowed_grounding = {
        "verified-main-text",
        "verified-reference",
        "source-unavailable",
        "not-exactly-located",
        "empty-evidence",
    }
    assignments = 0
    for record in records:
        rid = record.get("id", "<missing>")
        if record.get("discipline") not in disciplines:
            errors.append(f"{rid}: discipline is outside controlled vocabulary")
        if record.get("claim_type") and record["claim_type"] not in claims:
            errors.append(f"{rid}: claim type is outside controlled vocabulary")
        seen_terms: set[str] = set()
        for item in record.get("statistics", []):
            assignments += 1
            term = item.get("term")
            if term not in statistics:
                errors.append(f"{rid}: unknown statistic {term!r}")
            if term in seen_terms:
                errors.append(f"{rid}: duplicate statistic {term!r}")
            seen_terms.add(term)
            if item.get("decision") not in allowed_decisions:
                errors.append(f"{rid}::{term}: unresolved/invalid decision")
            if item.get("role") not in allowed_roles:
                errors.append(f"{rid}::{term}: invalid role {item.get('role')!r}")
            if item.get("decision") == "accepted" and not item.get("evidence", "").strip():
                errors.append(f"{rid}::{term}: accepted without evidence")
            if not item.get("reason", "").strip():
                errors.append(f"{rid}::{term}: missing audit reason")
            provenance = item.get("provenance", {})
            if provenance.get("grounding_status") not in allowed_grounding:
                errors.append(f"{rid}::{term}: invalid/missing grounding status")
            if not provenance.get("source_path"):
                errors.append(f"{rid}::{term}: missing source path")
            if not provenance.get("evidence_sha256"):
                errors.append(f"{rid}::{term}: missing evidence hash")

    if errors:
        raise SystemExit("corpus validation failed:\n- " + "\n- ".join(errors))
    print(f"validated {len(records)} records and {assignments} resolved assignments")


if __name__ == "__main__":
    main()
