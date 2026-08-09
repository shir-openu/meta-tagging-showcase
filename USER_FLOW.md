# The user flow — a researcher who has a corpus and needs a definition

Written 2026-08-09. This is the shape the platform has to take, derived from the one user we
actually have: a researcher who chooses a body of papers and wants to know what a concept
means inside it, and which definition of it holds up.

Everything already built is a stage of this flow. Nothing here is new work invented for its
own sake; the point of writing it down is that the stages were built in a different order
than the user meets them, and the seams show.

---

## The five screens

### 1 · Choose the corpus

The user says which papers count. **The corpus is a parameter of the measurement, not its
background** — a different corpus returns a different answer, and that is correct.

She can filter by discipline, by period, by language, by venue, or hand-pick. "God according
to theological writings only." "Plastic art as it was understood in seventeenth-century
Europe." The filter is saved with the result, because a number without its corpus is
meaningless.

*Built:* `DATA/corpus.json` holds 538 records with `discipline`, `year`, `lang`,
`fulltext_status`. Filtering is a query, not a new dataset.
*Missing:* the filter is not yet a saved, named object that travels with a result.

---

### 2 · Name the concept

She types a word: *consciousness*, *priming*, *work of art*.

The platform answers with what the corpus holds — not a definition, but the **material** for
one: how many papers use the word, in how many disciplines, and every sentence in which it
appears, each attached to its paper.

*Built:* `TOOLS/build_concept_records.py` produces one `ConceptNode` per concept, with a
`PaperSource` per paper and an `Attestation` per mention. 510 concepts, 746 attestations.
*Missing, and this is the live defect:* **0 of the 746 attestations carry a quotation.**
Concept tags were stored as bare strings. `DATA/concept_grounding_todo.json` is the work
order that fixes it — 746 jobs, each one "find the sentence that licenses this".

---

### 3 · See the senses, and the disagreement

The same word carries different readings. Freud's *consciousness* and the cognitive one are
not the same object, and averaging them produces a number that describes nobody.

So the concept record holds **senses**, each grounded in the quotations it was derived from,
and **relations between senses** — contradicts, extends, narrows — each with its own
evidence. Disagreement between papers is not noise to be smoothed; it is the most valuable
thing the corpus contains. A paper that bridges two senses is worth more than a paper that
merely uses the word.

*Built:* the record structure holds `senses` and `sense_relations`.
*Missing:* nothing populates them yet, because populating them requires the quotations from
stage 2. This is the stage that cannot be skipped ahead to.

---

### 4 · Test a definition

She proposes a definition. Or takes one from the literature. Or asks the platform to propose
one from the corpus.

The platform returns **one ranking**: place, MCC, confidence interval — and beside it the
definitions that were disqualified and why. Three gates run before any score: circularity,
recursion without a base case, a free parameter the author never fixed.

And it shows her **where the definition breaks** — the case table. A score without the cases
behind it is not checkable, and an unfalsifiable definition is worthless to her even if it
scores well.

*Built:* `TOOLS/concept_score.py`, `TOOLS/final_ranking.py`,
`TOOLS/induce_definition.py`, `TOOLS/control_negatives.py`. This stage works today.

---

### 5 · Iterate, and keep every version

She changes a word in her definition and re-scores. The platform keeps **every version**,
scores each against the same corpus, and marks each one:

- **measurement** — the wording was fixed *before* the cases were seen. The score is a test.
- **refinement** — the wording was fixed *after*. The score is not a test; the cases are
  already known.

Both are legitimate. Reporting them as though they were measured under the same conditions
is not.

*Built:* the versioning convention exists and has been exercised.
*Missing:* it is a file convention, not a feature of the interface.

---

## What the flow demands of the data, and why the current shape fails it

| Demand | Why | State |
|---|---|---|
| The concept is a **record**, not a string on a paper | Otherwise it cannot hold senses, contrast cases or relations, and tagging one more paper changes nothing about it | Built today by `build_concept_records.py` |
| Every attestation carries a **verbatim quotation** | It is the whole claim of the project, and stage 3 cannot run without it | **0 / 746.** The live defect |
| Attestations group under **one PaperSource per paper** | 25 mentions in one paper are one author's position, not 25 | Built |
| Counts are **computed at query time**, never stored | The corpus is a filter; a stored `n_papers` is wrong the moment she narrows it | Enforced — counts are recomputed, and the file says so |
| Wordings normalise to a **canonical term**, with the paper's own wording kept beside it | Free text does not join: 500 phenomenon strings over 511 papers, two crossing a discipline | **Not done.** This is the second defect |
| Contrast cases are a **required field** | A corpus recording only what a concept *is* can never test sufficiency, only coverage | Exists in the art worked example; not corpus-wide |

---

## The order of work that follows from this

1. **Ground the 746 concept attestations.** Nothing downstream is possible without it, and
   it is mechanical: the paper is already on disk, the sentence is already there.
2. **Canonicalise the wordings** — one term, many surfaces — so concepts join across papers.
   Never by string similarity; a merge is a judgement and carries its own evidence.
3. **Populate senses and relations** from the grounded quotations.
4. Only then does stage 3 of the interface have anything to show.

Stage 4 already works. That is the part that looks finished and is not the bottleneck.

---

## What the interface must let her DO — the four verbs

Added 2026-08-09 from Shir's specification. These are not screens; they are the operations
the screens exist to serve, and each one makes a demand on the data model.

### 1 · Find a concept that already exists

She types a word and sees whether the platform already holds it, before she starts from
nothing. The answer must show **how much is behind it** — papers, disciplines, grounded
attestations — because a concept with four ungrounded mentions and a concept with sixty
grounded ones are not the same offer.

*Demands:* a concept index searchable by label **and by the paper's own wording**, since she
may know the term as her field words it. `surface` must therefore be searchable, not just
`term`.
*State:* 510 concept records exist. The search over `surface` does not, because `surface`
was never recorded.

### 2 · Find a tag that already exists

Same for the tag registry. She must be able to see the 45 tags in seven layers, what each
one means, and — this is what makes it usable rather than decorative — **an example of a
paper that carries it, with the sentence that licensed it**.

*Demands:* every tag needs a `skos:definition`, not just a name. A category without a
definition transfers the decision to unwritten judgement, which is exactly the failure this
project measures in others.
*State:* the registry has one-line descriptors and **no scope notes, no inclusion rules,
one example**. This is the same defect we identified in Gutman's 103 undefined topics, and
we have it too.

### 3 · Define a corpus

Choose the papers. Filter by discipline, period, language, venue, or hand-pick. Save the
filter under a name and reuse it.

*Demands:* the corpus filter must be a **first-class saved object with an id**, and every
score must carry the id of the corpus it was computed on. A number without its corpus is
meaningless, and two numbers from two corpora must never be silently compared.
*State:* filtering works as a query. The saved, named, id-carrying corpus object does not
exist.

### 4 · Improve a definition — for her corpus, and for others

She takes an existing definition and edits it. The platform re-scores it **on her corpus**,
shows her the cases it now gets wrong, and keeps every version marked as measurement or as
refinement.

**And then the part that is not yet built at all:** it scores the same definition on **other
corpora** and shows her whether her improvement holds up, or whether she has fitted her own
material.

*Demands:* a definition record that holds a **vector of scores, one per corpus**, and a
condition-level view — because a definition improves by its conditions, not as a lump.
Per-condition ablation already exists; per-corpus does not.
*State:* single-corpus scoring works today. Cross-corpus does not exist.

---

## Why the cross-corpus view is the important one

It is the answer to the objection that would sink any definition this platform produces: that
a definition scored on the corpus it was built from has been fitted to it.

A definition that survives three unrelated corpora is a different kind of object from one
that wins on one. **That is the difference between a working tool and a publishable result**,
and it is a feature of the interface rather than a separate research project — the same
score, run again with a different corpus id.

It also gives the platform something to say that no one else says. Every tagging project
applies definitions to one corpus. None of them asks whether the definition would survive
somebody else's.

---

## Revised order of work

1. **Ground the 746 concept attestations.** Nothing downstream runs without it. In progress.
2. **Record `surface` alongside `term`** so concepts join across papers and so search finds
   a concept by the wording the user knows.
3. **Give every one of the 45 tags a definition** in `SCHEMA/tags.json`, as a hard schema
   constraint: no tag exports without one.
4. **Make the corpus filter a saved object with an id**, and stamp that id on every score.
5. **Add the per-corpus score vector** to the definition record, and the cross-corpus view
   on top of it.

Steps 2 and 3 are cheap and unblock the interface. Step 5 is what makes the output
publishable rather than merely useful.
