# Linked Open Data

The tag layer, expressed in two standards that are not ours, so other people's tools can read it
without knowing anything about this project.

| File | What it is |
|---|---|
| [`index.html`](index.html) | What this is, and one annotation shown in full |
| [`vocab.html`](vocab.html) | Browsable vocabulary; carries the same graph as embedded JSON-LD |
| [`vocab.jsonld`](vocab.jsonld) / [`vocab.ttl`](vocab.ttl) | SKOS concept schemes |
| [`annotations.jsonld`](annotations.jsonld) | W3C Web Annotation collection over the verbatim tags |
| [`corpus.jsonld`](corpus.jsonld) | The papers, as records, linked to the vocabulary |

## Why these two standards

This project normalises a verbatim sentence written in one **discipline** to a shared tag. A historical
gazetteer such as [MEHDIE](https://mehdie.org/) or Kima normalises a place name written in one
**language** to a shared identifier. Same operation, different axis — so the same standards fit both.

* **SKOS** turns each tag into an addressable concept: a URI, an English and (where known) a Hebrew
  label, and a link to Wikidata.
* **W3C Web Annotation** turns a grounded tag into an annotation. For a paper whose text is cleared for
  redistribution the target carries a `TextQuoteSelector` — `exact`, `prefix`, `suffix`; that selector
  *is* this project's verbatim-grounding rule, already standardised. For a paper that is not cleared the
  sentence is withheld: the target carries a position where one was measured, and a notice saying what is
  withheld. This export covers the five `content_tags` facets; [`index.html`](index.html) states how many
  of the corpus's quotes that is.

## What the reconciliation does and does not claim

A link is asserted on one of three grounds: a label or alias that matched together with a `P31`/`P279`
statement licensing the type; a person's decision, recorded as `human adjudication`; or a matching label
alone, in the groups for which no type list was defined. Which one is kept on the concept
(`mt:matchEvidence`), and [`index.html`](index.html) states how many links rest on each. Where none of
these could be shown, the result is recorded as unmatched rather than guessed.

`skos:exactMatch` means the same thing. `skos:closeMatch` means related but not identical, and is used
where our shorthand has no exact counterpart — `interpretive` is a close match to *qualitative
research*, not the same concept, and is never published as an exact one.

Place names needed a further step. `Cambridge` matches two of the most important academic cities in the
world, and no string test settles which one a paper means. Those decisions were made by hand with the
reason recorded beside each one, in [`../../DATA/place_adjudication.json`](../../DATA/place_adjudication.json);
one string had to be decided per paper rather than once.

## Two deliberate absences

* The **reliability layer is private** and is never exported.
* **Paper-level facets are not annotations.** The discipline and the concepts are `dcterms:subject`
  statements about the paper, the method is `mt:method`, and the other paper-level facets are not
  exported. That is not because they have no quote behind them - they do, and [`index.html`](index.html)
  counts them. The annotation model here is scoped to the five `content_tags` facets, and the evidence
  behind a paper-level facet is not modelled as a target yet.

## Scope

Generated from the project's *working* corpus, which is larger than the frozen release corpus in
[`../DATA/corpus.json`](../DATA/corpus.json) and uses a fuller schema. The two are not meant to agree on
totals. An annotation carries up to two targets for each quoted span: a *source anchor*, the position of
the quote in the text this corpus is verified against, and a *display anchor*, its position in the
extracted text of this project's page for the paper (the page itself is named under `mt:renderedAt`).
Where a record has no page the display anchor names the paper's DOI. [`index.html`](index.html) says how
many spans carry each.

## Rebuilding

```
python TOOLS/reconcile_wikidata.py            # tag strings -> Wikidata, with evidence
python TOOLS/apply_place_adjudication.py      # fold in the human place decisions
python TOOLS/export_lod.py --validate         # build, then parse every file with rdflib
```

Licence: CC BY 4.0.
