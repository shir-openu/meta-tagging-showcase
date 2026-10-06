# Corpus storage, indexing, and build architecture

## Implemented data flow

`DATA/corpus.json` is the canonical metadata and annotation source.  `python TOOLS/build.py`
performs FOUR stages, in this order, and nothing else:

1. validate identifiers, controlled vocabularies, audit resolution, evidence,
   and provenance invariants (`validate_corpus.py`);
2. derive sorted postings lists and lazy-loadable record shards
   (`build_index.py`);
3. derive a typed adjacency list containing only relations present in the
   canonical records (`build_graph.py`);
4. regenerate the audit report `report_statistics.html` from the frozen audit
   (`build_audit_report.py`).

**Three steps are NOT part of it, and cannot be reproduced from this bundle.**
`audit_statistics.py` adjudicates statistical-tag candidates and its decisions
are frozen in `DATA/statistics_audit_overrides.json`; `recalculate_section5.py`
recomputes the grounding audit against each paper's FULL TEXT, which this
bundle does not redistribute; `patch_paper_statistics.py` injects audited
statistics into the per-paper pages, which is a publishing step. Run those
explicitly only when re-auditing against full text.

Derived files under `DATA/index/`, `DATA/graph/` and `report_statistics.html`
are disposable build products: delete them and `build.py` rebuilds them.
`DATA/statistics_audit.json` and `DATA/section5_statistics.json` are NOT
disposable. They ship frozen and human-adjudicated, they are inputs to the
build rather than outputs of it, and deleting them cannot be undone from this
bundle.

## Query cost

For a facet key, the postings dictionary lookup is expected O(1).  An ALL query
intersects sorted lists in Θ(sum of the input postings lengths) time plus the
output work; an ANY query has the corresponding union cost.  A common tag,
unfiltered listing, or complement can therefore be Θ(N).  The implementation
does not claim corpus-size-independent queries.  Its benefit is that selective
queries avoid scanning unrelated records and fetch only the metadata shards
needed for the displayed page.

Index construction is O(T log T) in the current Python implementation, where T
is the number of emitted posting entries (sets are converted to sorted lists).
The builder holds corpus metadata and postings in memory.  That is reasonable
for thousands to low tens of thousands of papers; substantially larger corpora
should use an external-sort or database-backed build.

## Storage plan for thousands of papers

The current 91 generated full-text pages occupy about 15 MB, while the complete
canonical JSON is under 0.5 MB.  Keeping thousands of mutable full-text HTML
documents in Git would make history and cloning needlessly expensive.  The
recommended separation is:

- Git/version control: schema, vocabularies, audit decisions, build code, and
  compact metadata;
- versioned object storage: legally redistributable source text and generated
  reading views, addressed by immutable content hash;
- static hosting/CDN: `SEARCH.html`, postings, metadata shards, reports, and
  permitted reading views;
- external DOI/landing-page links only for sources that cannot be redistributed.

At 10,000 papers, use a manifest of immutable canonical NDJSON/JSON shards
(for example 1,000 records per shard) rather than one frequently rewritten
file.  Record IDs must remain stable; annotation revisions should be
append-only events or versioned snapshots.  Source-body and evidence hashes
make silent source drift detectable, but a future ingestion system should also
store a resolvable selector (page/section/character range) instead of relying
only on an excerpt.

## Graph scope

`DATA/graph/adjacency.json` currently exports `IN`, `HAS_CLAIM`,
`HAS_PHENOMENON`, and accepted `HAS_STATISTIC` relations.  `ALIAS_OF`, scored
`CONGRUENT_TO`, projected links, and graph-analysis results are explicitly not
implemented and must not be presented as measured outputs.  Algorithms over
the adjacency export have their ordinary graph-dependent complexity, generally
O(|V| + |E|) for a full traversal.
