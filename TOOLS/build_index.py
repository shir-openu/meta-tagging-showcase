#!/usr/bin/env python3
"""Build the sharded browser index from the audited canonical corpus."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from corpus_io import INDEX_DIR, build_index_parts, load_corpus, save_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-size", type=int, default=500)
    args = parser.parse_args()
    if args.shard_size < 1:
        raise SystemExit("--shard-size must be positive")

    corpus = load_corpus()
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest, postings, shards = build_index_parts(
        corpus, generated=generated, shard_size=args.shard_size
    )
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    for stale in INDEX_DIR.glob("records-*.json"):
        stale.unlink()
    save_json(INDEX_DIR / "manifest.json", manifest)
    save_json(INDEX_DIR / "postings.json", postings)
    for name, shard in zip(manifest["shards"], shards, strict=True):
        save_json(INDEX_DIR / name, shard)
    print(
        f"built {manifest['record_count']} records, {len(postings)} postings lists, "
        f"{len(shards)} shards"
    )


if __name__ == "__main__":
    main()
