#!/usr/bin/env python3
"""Regression tests for audit counts, postings, shards, and graph exports."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from corpus_io import INDEX_DIR, ROOT, accepted_statistics, load_corpus


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def intersect(left: list[int], right: list[int]) -> list[int]:
    result: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] == right[j]:
            result.append(left[i])
            i += 1
            j += 1
        elif left[i] < right[j]:
            i += 1
        else:
            j += 1
    return result


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()
        cls.section5 = load(ROOT / "DATA" / "section5_statistics.json")
        cls.audit = load(ROOT / "DATA" / "statistics_audit.json")
        cls.manifest = load(INDEX_DIR / "manifest.json")
        cls.postings = load(INDEX_DIR / "postings.json")
        cls.shards = [load(INDEX_DIR / name) for name in cls.manifest["shards"]]

    def test_audit_totals(self) -> None:
        self.assertEqual(self.audit["total_assignments"], 519)
        self.assertEqual(self.audit["decisions"], {"accepted": 420, "rejected": 99})
        self.assertEqual(self.section5["audit"]["unresolved_assignments"], 0)
        self.assertEqual(
            self.section5["audit"]["grounding_accepted_assignments"],
            {
                "verified-main-text": 272,
                "not-exactly-located": 41,
                "verified-reference": 10,
                "source-unavailable": 97,
            },
        )

    def test_recalculated_section5(self) -> None:
        self.assertEqual(self.section5["coverage"]["papers_with_accepted_statistics"], 100)
        self.assertEqual(self.section5["coverage"]["disciplines_with_accepted_statistics"], 37)
        self.assertEqual(
            self.section5["selected_pairs"]["p-value+standard-deviation"],
            {"papers": 10, "disciplines": 10},
        )
        self.assertEqual(
            self.section5["selected_pairs_exact_local_body"][
                "p-value+standard-deviation"
            ],
            {"papers": 3, "disciplines": 3},
        )

    def test_shards_cover_each_document_once(self) -> None:
        records = [record for shard in self.shards for record in shard]
        docs = [record["doc"] for record in records]
        self.assertEqual(docs, list(range(self.manifest["record_count"])))
        self.assertEqual(len(records), len(self.corpus["records"]))
        self.assertTrue(all("eg" in record for record in records))

    def test_postings_are_sorted_unique_and_in_range(self) -> None:
        limit = self.manifest["record_count"]
        for key, values in self.postings.items():
            self.assertEqual(values, sorted(set(values)), key)
            self.assertTrue(all(0 <= value < limit for value in values), key)

    def test_postings_match_accepted_annotations(self) -> None:
        records = [record for shard in self.shards for record in shard]
        by_id = {record["id"]: record for record in records}
        for source in self.corpus["records"]:
            indexed = by_id[source["id"]]
            expected = sorted(item["term"] for item in accepted_statistics(source))
            self.assertEqual(indexed["st"], expected, source["id"])
            for term in expected:
                self.assertIn(indexed["doc"], self.postings[f"statistic:{term}"])

    def test_index_intersection_reproduces_reported_pair(self) -> None:
        ids = intersect(
            self.postings["statistic:p-value"],
            self.postings["statistic:standard-deviation"],
        )
        self.assertEqual(len(ids), 10)
        discipline_ids = self.manifest["discipline_by_doc"]
        self.assertEqual(len({discipline_ids[doc] for doc in ids}), 10)

    def test_graph_declares_only_implemented_relations(self) -> None:
        graph_dir = ROOT / "DATA" / "graph"
        manifest = load(graph_dir / "manifest.json")
        adjacency = load(graph_dir / "adjacency.json")
        allowed = set(manifest["implemented_relations"])
        reverse = {"HAS_PAPER", "CLAIM_OF", "PHENOMENON_OF", "STATISTIC_OF"}
        observed = {
            edge["relation"] for edges in adjacency.values() for edge in edges
        }
        self.assertLessEqual(observed, allowed | reverse)
        self.assertTrue(
            set(manifest["non_implemented_relations"]).isdisjoint(observed)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
