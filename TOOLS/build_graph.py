#!/usr/bin/env python3
"""Derive a typed adjacency list from the audited corpus.

The export contains only relations represented in DATA/corpus.json.  It does
not invent ALIAS_OF, CONGRUENT_TO, projected links, or graph-analysis results.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from corpus_io import ROOT, accepted_statistics, load_corpus, save_json


GRAPH_DIR = ROOT / "DATA" / "graph"


def add_edge(
    adjacency: dict[str, list[dict[str, str]]],
    left: str,
    relation: str,
    right: str,
    reverse_relation: str,
) -> None:
    adjacency[left].append({"relation": relation, "target": right})
    adjacency[right].append({"relation": reverse_relation, "target": left})


def main() -> None:
    corpus = load_corpus()
    adjacency: dict[str, list[dict[str, str]]] = defaultdict(list)
    paper_nodes = 0
    edge_count = 0
    for record in corpus["records"]:
        paper = f"paper:{record['id']}"
        adjacency[paper]
        paper_nodes += 1

        discipline = f"discipline:{record['discipline']}"
        add_edge(adjacency, paper, "IN", discipline, "HAS_PAPER")
        edge_count += 1

        if record.get("claim_type"):
            claim = f"claim:{record['claim_type']}"
            add_edge(adjacency, paper, "HAS_CLAIM", claim, "CLAIM_OF")
            edge_count += 1

        if record.get("phenomenon"):
            phenomenon = f"phenomenon:{record['phenomenon']}"
            add_edge(adjacency, paper, "HAS_PHENOMENON", phenomenon, "PHENOMENON_OF")
            edge_count += 1

        for annotation in accepted_statistics(record):
            statistic = f"statistic:{annotation['term']}"
            add_edge(adjacency, paper, "HAS_STATISTIC", statistic, "STATISTIC_OF")
            edge_count += 1

    for edges in adjacency.values():
        edges.sort(key=lambda edge: (edge["relation"], edge["target"]))

    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    save_json(
        GRAPH_DIR / "manifest.json",
        {
            "schema_version": "1.0.0",
            "generated": generated,
            "node_count": len(adjacency),
            "paper_node_count": paper_nodes,
            "edge_count": edge_count,
            "edge_count_note": "undirected logical edges; adjacency stores both directions",
            "implemented_relations": [
                "IN",
                "HAS_CLAIM",
                "HAS_PHENOMENON",
                "HAS_STATISTIC",
            ],
            "non_implemented_relations": [
                "ALIAS_OF",
                "CONGRUENT_TO",
                "projected_link",
            ],
        },
    )
    save_json(GRAPH_DIR / "adjacency.json", dict(sorted(adjacency.items())))
    print(f"built graph export: {len(adjacency)} nodes, {edge_count} edges")


if __name__ == "__main__":
    main()
