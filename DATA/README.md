# Data directory

- `corpus.json`: canonical records and audited annotations.

  **This is the reproduction bundle, not the whole corpus.** It holds 126 records
  of the tag layer, published on purpose, with no body field anywhere and no
  string over 180 characters -- the constraint that lets the tag layer be
  redistributed when the article text cannot be. `make_public.py` asserts those
  two properties on every build and refuses to publish a file that breaks them.

  So the paper counts on the site's pages will not match this file, and are not
  meant to: the pages are built from the project's working corpus, which is much
  larger. `../lod/index.html` sets out both populations and why they differ,
  under "Scope -- read this before comparing counts".
- `statistics_audit_overrides.json`: human-review decisions and corrected
  evidence excerpts; edit this file rather than generated audit outputs.
- `statistics_audit.json`: complete generated audit ledger.
- `section5_statistics.json`: generated quantities used in preprint §5.
- `index/`: generated search manifest, sorted postings, and record shards.
- `graph/`: generated typed adjacency export and manifest.

See `../ARCHITECTURE.md` for provenance, complexity, scaling, and storage
constraints.
