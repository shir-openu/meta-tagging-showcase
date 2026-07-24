# Changelog

All notable changes to the Meta-Tagging tag layer, corpus, and showcase.
The Zenodo concept DOI `10.5281/zenodo.21429867` always resolves to the latest version;
each release also receives its own version DOI.

## [9.0] — 2026-07-24 — release-readiness revision

Addresses the independent GitHub/Zenodo release-readiness review.

### Added
- **Per-paper redistribution-rights manifest** (`DATA/rights_manifest.json`). Every source's licence
  was verified twice — against its landing page **and** the Crossref API — with an explicit
  `full_text_redistributable` flag, SPDX id, licence URL, and evidence URL. Tools:
  `TOOLS/check_rights.py`, `TOOLS/refine_rights_crossref.py`.
- Rights fields (`license_spdx`, `license_url`, `source_url`, `doi`, `full_text_redistributable`) on
  every record in `DATA/corpus.json`.
- `.gitignore`, this `CHANGELOG.md`, and `SHA256SUMS.txt` for the release artifacts.

### Changed
- **Full text is now reproduced only for the 19 papers under a verified redistributable licence**
  (CC-BY / CC0 / public domain). The other 86 previously-full-text pages — including 52 arXiv papers
  under the non-exclusive-distribution licence, which does **not** grant third-party redistribution —
  were converted to **link-only** pages that keep our entire tag layer and short licensing excerpts and
  link to the source. Being free-to-read is no longer treated as permission to redistribute. Full tagged
  text is retained internally (not published).
- Methodology wording: the statistical-tag re-audit is described as **rule-based with LLM-assisted
  adjudication** (not an independent second-coder study); the absence of an inter-rater reliability
  estimate is stated as a limitation.
- Grounding claims reworded throughout as a **design rule measured by the audit**, not an assumed
  100% exact-body property; the 272/420 exact-local-body figure is stated where relevant.
- "Schema validation" → **"invariant validation"** to match what the build actually runs.
- All release metadata reconciled to **version 9.0 / 2026-07-24** (`CITATION.cff`, `.zenodo.json`,
  `README.md`, `preprint.html`).

### Removed
- Stale `report41.html` (its statistics contradicted the audited numbers); its link now points to the
  canonical `report_statistics.html`.
- Empty `TESTS/` directory and Python `__pycache__` from the release.

## [8.0] — 2026-07-20 — audited release

- Systematic audit of all 519 statistical-tag assignments (420 accepted, 99 rejected, 19.1%); §5
  recomputed; separated semantic acceptance from exact-local-body grounding (272/420).
- Real inverted index with corrected complexity analysis (expected O(1) key lookup; ALL/ANY merges
  Θ(Σ|Pᵢ|)+output, worst case Θ(N) — not "independent of corpus size").
- JSON Schema, reproducible build pipeline, typed graph export (implemented relations only),
  provenance states, and 7 passing regression tests.

## [≤7] — earlier

- Introduced the priming A·S·M grounded analysis (association / secondariness / modulation:
  16/16, 14/16, 16/16), the statistical join-key experiment, the interactive graph viewers, and the
  three-layer property-graph data-structure figures.
