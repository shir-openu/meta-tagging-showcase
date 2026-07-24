# A field-neutral tag layer for academic literature

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21429867.svg)](https://doi.org/10.5281/zenodo.21429867) [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)

**Version 9.0** (2026-07-24) · **Live showcase:** <https://shir-openu.github.io/meta-tagging-showcase/>
**Archived & citable:** [10.5281/zenodo.21429867](https://doi.org/10.5281/zenodo.21429867)

> **How to cite:** Sivroni, S. (2026). *A Verbatim-Grounded, Field-Neutral Tag Layer for Cross-Disciplinary Reading of Academic Literature: A Proof of Format.* Zenodo. <https://doi.org/10.5281/zenodo.21429867>

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
- **`papers/`** — for the **19** papers under a verified redistributable licence (CC-BY / CC0 / public
  domain), the full colour-tagged text; for every other paper, our tag layer with short licensing
  excerpts and a link to the source (full text **not** reproduced).
- **[`DATA/rights_manifest.json`](DATA/rights_manifest.json)** — the per-paper rights audit: each source's
  licence verified against its landing page **and** the Crossref API, with an explicit
  `full_text_redistributable` flag.
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

Full text is reproduced **only** for papers under a licence that permits redistribution, verified
per paper in [`DATA/rights_manifest.json`](DATA/rights_manifest.json) against both the source landing
page and the Crossref API. Being free-to-read (e.g. on arXiv under its non-exclusive-distribution
licence) is **not** treated as permission to redistribute; those papers are **linked, not reproduced**.
The catalogue still shows our facets and short licensing excerpts for them. Our tag layer (facets,
colour coding, catalogue) is our own contribution, released under CC-BY-4.0.
