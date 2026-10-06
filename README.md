# A field-neutral tag layer for academic literature

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21432188.svg)](https://doi.org/10.5281/zenodo.21432188) [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)

**Version 10.0** (2026-07-28) · **Live showcase:** <https://shir-openu.github.io/meta-tagging-showcase/>
**Archived & citable:** [10.5281/zenodo.21432188](https://doi.org/10.5281/zenodo.21432188)

> **How to cite:** Sivroni, S. (2026). *A Verbatim-Grounded, Field-Neutral Tag Layer for Cross-Disciplinary Reading of Academic Literature: A Proof of Format.* Zenodo. <https://doi.org/10.5281/zenodo.21432188>

---

A proof-of-**format**: every paper in this corpus is described with the same small set of
**verbatim-grounded** faceted tags — *claim type*, *phenomenon* (a normalised cross-field join
key), *claim relations*, *replication status*, and *limitations*. The design rule is that every tag
must be licensed by an exact sentence from the paper's own text; the v8 audit measured how fully the
legacy data meets that rule and reports the provenance status of every tag (see the preprint's §5
grounding sensitivity analysis), rather than assuming 100% exact-body grounding.

The goal is to make cross-disciplinary connections **queryable and verifiable**, and to surface
candidate links the literature has not yet drawn. The corpus is an existence proof of the procedure,
not a claim of completeness. A surfaced cross-field link is a **hypothesis to investigate, never a
claimed discovery**.

## What's here

- **[`index.html`](index.html)** — the report + a catalogue of every tagged paper with its facets.
- **`papers/`** — 1,673 paper pages. For the **1,161** papers cleared for redistribution, the full
  colour-tagged text; for the other **512**, our tag layer with short excerpts and a link to the
  source where one is on record (full text **not** reproduced).
- **[`DATA/rights_manifest.json`](DATA/rights_manifest.json)** — the per-paper rights record: one row
  for each of the 1,673 paper pages, written at every build from the project's rights record. A row gives
  the licence found for the paper, the address where that licence can be checked, and the explicit
  `full_text_redistributable` flag that the site obeys.
- **[`untaggable.html`](untaggable.html)** — a study of papers whose source text could not be faceted.

## Reproducibility

`python TOOLS/build.py` regenerates the inverted index, graph export and validation deterministically from
the resolved corpus, and `PYTHONPATH=TOOLS python TOOLS/test_pipeline.py` runs a 7-test regression suite
(all pass). "Reproducible" here means identical *computations*, not byte-identical output files.
`DATA/section5_statistics.json` (the statistical-tag grounding audit: 519 assignments → 420 accepted / 99
rejected, 272 with exact local-body evidence) is a **frozen, human-adjudicated artifact** computed against
each paper's full text. Because most full text is not redistributed (see below), those grounding sub-counts
ship as a fixed input rather than being recomputed from the redistributed (partial) pages.

## Copyright

Full text is reproduced **only** where the paper's licence was verified as CC BY, CC BY-SA or CC0, or
where an older work is recorded in [`DATA/rights_manifest.json`](DATA/rights_manifest.json) as public
domain by its age — a status we recorded and did not verify against a licence statement. Being
free-to-read (e.g. on arXiv under its non-exclusive-distribution licence) is **not** treated as
permission to redistribute; those papers are **linked, not reproduced**.
The catalogue still shows our facets and short licensing excerpts for them. Our tag layer (facets,
colour coding, catalogue) is our own contribution, released under CC-BY-4.0.
