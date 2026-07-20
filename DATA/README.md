# Data directory

- `corpus.json`: canonical records and audited annotations.
- `statistics_audit_overrides.json`: human-review decisions and corrected
  evidence excerpts; edit this file rather than generated audit outputs.
- `statistics_audit.json`: complete generated audit ledger.
- `section5_statistics.json`: generated quantities used in preprint §5.
- `index/`: generated search manifest, sorted postings, and record shards.
- `graph/`: generated typed adjacency export and manifest.

See `../ARCHITECTURE.md` for provenance, complexity, scaling, and storage
constraints.
