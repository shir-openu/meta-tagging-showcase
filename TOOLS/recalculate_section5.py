#!/usr/bin/env python3
"""Recalculate every quantitative statement used in preprint Section 5."""

from __future__ import annotations

from collections import Counter

from corpus_io import ROOT, load_corpus, save_json


OUTPUT = ROOT / "DATA" / "section5_statistics.json"


def main() -> None:
    corpus = load_corpus()
    accepted_records = []
    verified_records = []
    all_assignments = []
    for record in corpus["records"]:
        accepted = [
            item for item in record["statistics"] if item["decision"] == "accepted"
        ]
        all_assignments.extend(record["statistics"])
        if accepted:
            accepted_records.append((record, accepted))
        verified = [
            item
            for item in accepted
            if item.get("provenance", {}).get("grounding_status")
            == "verified-main-text"
        ]
        if verified:
            verified_records.append((record, verified))

    by_term = {}
    verified_by_term = {}
    for term in corpus["vocabularies"]["statistics"]:
        papers = [
            record
            for record, items in accepted_records
            if any(item["term"] == term for item in items)
        ]
        by_term[term] = {
            "papers": len(papers),
            "disciplines": len({paper["discipline"] for paper in papers}),
        }
        verified_papers = [
            record
            for record, items in verified_records
            if any(item["term"] == term for item in items)
        ]
        verified_by_term[term] = {
            "papers": len(verified_papers),
            "disciplines": len(
                {paper["discipline"] for paper in verified_papers}
            ),
        }

    def pair(left: str, right: str) -> dict[str, int]:
        papers = [
            record
            for record, items in accepted_records
            if {left, right} <= {item["term"] for item in items}
        ]
        return {
            "papers": len(papers),
            "disciplines": len({paper["discipline"] for paper in papers}),
        }

    def verified_pair(left: str, right: str) -> dict[str, int]:
        papers = [
            record
            for record, items in verified_records
            if {left, right} <= {item["term"] for item in items}
        ]
        return {
            "papers": len(papers),
            "disciplines": len({paper["discipline"] for paper in papers}),
        }

    total = len(all_assignments)
    rejected = sum(item["decision"] == "rejected" for item in all_assignments)
    grounding = Counter(
        item.get("provenance", {}).get("grounding_status", "missing")
        for item in all_assignments
    )
    accepted_grounding = Counter(
        item.get("provenance", {}).get("grounding_status", "missing")
        for _, items in accepted_records
        for item in items
    )
    result = {
        "audit": {
            "total_legacy_assignments": total,
            "accepted_assignments": total - rejected,
            "rejected_assignments": rejected,
            "rejection_rate": round(rejected / total, 4),
            "unresolved_assignments": sum(
                item["decision"] == "needs-review" for item in all_assignments
            ),
            "grounding_all_assignments": dict(grounding),
            "grounding_accepted_assignments": dict(accepted_grounding),
        },
        "coverage": {
            "papers_with_accepted_statistics": len(accepted_records),
            "disciplines_with_accepted_statistics": len(
                {record["discipline"] for record, _ in accepted_records}
            ),
            "corpus_papers": len(corpus["records"]),
            "corpus_disciplines": len(corpus["vocabularies"]["disciplines"]),
            "papers_with_exact_local_body_evidence": len(verified_records),
            "disciplines_with_exact_local_body_evidence": len(
                {record["discipline"] for record, _ in verified_records}
            ),
        },
        "by_term": by_term,
        "by_term_exact_local_body": verified_by_term,
        "selected_pairs": {
            "p-value+standard-deviation": pair("p-value", "standard-deviation"),
            "p-value+statistical-significance": pair(
                "p-value", "statistical-significance"
            ),
            "mean+standard-deviation": pair("mean", "standard-deviation"),
        },
        "selected_pairs_exact_local_body": {
            "p-value+standard-deviation": verified_pair(
                "p-value", "standard-deviation"
            ),
            "p-value+statistical-significance": verified_pair(
                "p-value", "statistical-significance"
            ),
            "mean+standard-deviation": verified_pair(
                "mean", "standard-deviation"
            ),
        },
        "accepted_roles": dict(
            Counter(
                item["role"]
                for _, items in accepted_records
                for item in items
            )
        ),
    }
    save_json(OUTPUT, result)
    print(
        f"section 5: {result['audit']['accepted_assignments']} accepted assignments; "
        f"{result['coverage']['papers_with_accepted_statistics']} papers; "
        f"{result['coverage']['disciplines_with_accepted_statistics']} disciplines"
    )


if __name__ == "__main__":
    main()
