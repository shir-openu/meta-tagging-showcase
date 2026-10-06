#!/usr/bin/env python3
from corpus_io import CORPUS_JSON, bootstrap_corpus, save_json


if __name__ == "__main__":
    corpus = bootstrap_corpus()
    save_json(CORPUS_JSON, corpus)
    print(f"Wrote {len(corpus['records'])} records to {CORPUS_JSON}")

