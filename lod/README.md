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
* **W3C Web Annotation** turns each grounded tag into an annotation whose target carries a
  `TextQuoteSelector` — `exact`, `prefix`, `suffix`. That selector *is* this project's
  verbatim-grounding rule, already standardised.

## What the reconciliation does and does not claim

A link is asserted only where two things could be shown: a label or alias that matched, **and** a
`P31`/`P279` statement licensing the type. The evidence for each is kept on the concept
(`mt:matchEvidence`). Anything that could not show both is recorded as unmatched rather than guessed.

`skos:exactMatch` means the same thing. `skos:closeMatch` means related but not identical, and is used
where our shorthand has no exact counterpart — `interpretive` is a close match to *qualitative
research*, not the same concept, and is never published as an exact one.

Place names needed a further step. `Cambridge` matches two of the most important academic cities in the
world, and no string test settles which one a paper means. Those decisions were made by hand with the
reason recorded beside each one, in [`../../DATA/place_adjudication.json`](../../DATA/place_adjudication.json);
one string had to be decided per paper rather than once.

## Two deliberate absences

* The **reliability layer is private** and is never exported.
* **Paper-level facets are not annotations.** Discipline and method are `dcterms:subject` statements
  about the paper. They have no verbatim quote behind them, and only tags that do become annotations.
  Blurring that line would overstate what is grounded.

## Scope

Generated from the project's *working* corpus, which is larger than the frozen release corpus in
[`../DATA/corpus.json`](../DATA/corpus.json) and uses a fuller schema. The two are not meant to agree on
totals. Where a record has a published page the annotations target that page; where it does not, they
target the paper's DOI.

## Rebuilding

```
python TOOLS/reconcile_wikidata.py            # tag strings -> Wikidata, with evidence
python TOOLS/apply_place_adjudication.py      # fold in the human place decisions
python TOOLS/export_lod.py --validate         # build, then parse every file with rdflib
```

Licence: CC BY 4.0.
