# Tagging protocol — instructions for a tagging agent

You are tagging papers for the **meta-tagging project**. Read this whole file before you
start. It is written so that a fresh agent, with no memory of the project, can produce
tagging that passes the gates on the first pass.

Everything here exists because something went wrong without it. Where that is the case, the
failure is named, so that nobody removes a rule later thinking it is decorative.

---

## 0. The one rule

**No tag without a verbatim quotation.**

Every tag you write must carry an `evidence` string that is an **exact substring of the
paper's own text**. Not a paraphrase. Not a reconstruction. Not "the paper says in effect".
The merge step re-opens the file you were given and checks the string character by
character, after normalising whitespace, ligatures and curly quotes. If it is not found,
**your tag is deleted, not repaired**.

This is not a formality. It is the entire claim of the project: the judgement (what kind of
claim is this?) is a reading task, but the grounding (does the paper actually say that?) is
a string comparison — **and a string comparison cannot be talked into agreeing**.

Consequences you must internalise:

- Copy quotations by **copy-paste from the text you were given**, never by retyping.
- Do not "clean up" a quotation. Do not fix the paper's typo. Do not close its brackets.
- Do not join two sentences that are not adjacent. If you need two, write two tags.
- Minimum quotation length is **25 characters**. A three-word fragment is not evidence.
- If you cannot find a sentence that licenses the tag, **do not write the tag**. A gap is
  visible and honest; a fabricated tag is invisible and poisons the corpus.

---

## 1. What you are given, and what counts as a real paper

You will be given one file per paper from `DATA/facet_queue/<id>.txt`. Each file contains a
literal marker line:

```
----- ARTICLE TEXT BELOW; QUOTE ONLY FROM HERE -----
```

**Quote only from below that line.** Above it sits metadata (title, DOI, URL, source
format). Quoting from the header produces a tag grounded in our own bookkeeping rather than
in the paper.

### Refuse to tag a file that is not a full paper

Check before you begin, and say so plainly if the file fails:

| Check | Threshold | Why it exists |
|---|---|---|
| Length | **≥ 2,500 words** below the marker | Abstract stubs were once stored as full text; 139 of 150 came out 1–2 pages long. A stub recorded as full text is worse than a gap, because the gap is visible and the stub is not. |
| Letters as a **share** of characters | ≥ 60% | A file once extracted as 10,938 "words" of control characters with only 365 alphabetic runs in 20,000 characters. It passed a letter-*count* threshold. Use the share. |
| Mean token length | ≤ 12 characters | Catches extraction garbage and merged-word failures. |
| Title match | the title's words in the **same order** | The copy fetched for one paper was a different paper by different authors. Word *overlap* scored it 100%. **Word order is the signal that separates them.** |
| Sections present | you can see a discussion or results section, not only an abstract | A paper truncated after the introduction cannot support tags about findings. |

If a file fails any of these, **report it as unusable and move on**. Do not tag it partially.
Do not "do your best with what is there". A partial tagging is indistinguishable downstream
from a complete one, and that is exactly the corruption this rule prevents.

---

## 2. What to tag

Two kinds of layer. Do both.

### 2a. The facet layer — the shape of the contribution

One value per paper, drawn from a **closed list**. Every one carries its own evidence
quotation.

- `claim_type` — one of: `existence` · `mechanism` · `method` · `prediction` · `critique` ·
  `null-result`
- `phenomenon` — what the paper is about, as a short phrase
- `method` — how it was studied
- `replication_status` — one of: `original` · `replication` · `failed-replication` ·
  `not-applicable`
- `limitations[]` — each with its own quotation
- `claim_relations[]` — one of `builds-on` · `extends` · `contradicts` · `replicates`, each
  naming a target work, each with its own quotation

### 2b. The content layer — what the paper actually says

Lists, each item with `term`/`text` and its own `evidence`:

`findings` · `definitions` · `variables` · `quantities` · `statistics` · `mechanisms` ·
`transfers`

### The vocabulary rule that decides whether this work is worth anything

For `phenomenon`, `definitions`, and any term-like field: **do not invent a fresh phrase per
paper**. This is the measured failure of the project's first pass — 500 distinct phenomenon
strings for 511 papers, of which **two** crossed a disciplinary boundary. Free text does not
join.

So:

1. **First look in `SCHEMA/statistics_vocab.json` and `DATA/tag_vocabulary_v1.json`.** If a
   canonical term exists, use it exactly.
2. If none fits, write the term **as the paper writes it**, and put the paper's own wording
   in `surface`, keeping `term` in canonical English.
3. Never normalise silently: `term` is the join key, `surface` is what the paper said, and
   both are stored.

---

## 3. What NOT to do — the failures already recorded

- **Do not tag from the title or the abstract alone.** The abstract is the authors' summary
  of themselves.
- **Do not treat silence as a negative.** If the paper does not say something, that is not
  evidence that it denies it. Leave the field empty; empty is a legitimate value.
- **Do not mix "an instance of the concept" with "a claim about the concept".** Conflating
  the two destroyed an entire scoring run. A paper that *argues about* memory is not a
  *case of* memory.
- **Do not count one paper as many opinions.** Twenty-five mentions in one paper are one
  author's position. Attestations are grouped under one `PaperSource`.
- **Do not paraphrase a quotation into fluency.** The ugly verbatim string is the asset.
- **Do not skip the negative cases.** A corpus that records only what a concept *is* can
  never test sufficiency. Where a paper says explicitly that something is *not* the concept,
  that is a `contrast_case` and it is more valuable than another positive.

---

## 4. Output format

One JSON object per paper. Nothing else in the response — no preamble, no commentary.

```json
{
  "id": "<the queue file's stem>",
  "usable": true,
  "reject_reason": null,
  "claim_type": "mechanism",
  "claim_type_evidence": "<exact substring>",
  "phenomenon": "repetition priming",
  "phenomenon_evidence": "<exact substring>",
  "method": "behavioural-experiment",
  "method_evidence": "<exact substring>",
  "replication_status": "original",
  "limitations": [{"text": "...", "evidence": "<exact substring>"}],
  "claim_relations": [{"kind": "extends", "target": "...", "evidence": "<exact substring>"}],
  "content_tags": {
    "findings":    [{"text": "...", "evidence": "<exact substring>"}],
    "definitions": [{"term": "...", "surface": "...", "evidence": "<exact substring>"}],
    "variables":   [{"term": "...", "evidence": "<exact substring>"}],
    "quantities":  [{"value": "...", "evidence": "<exact substring>"}],
    "statistics":  [{"term": "p-value", "symbol": "p", "surface": "p < .001",
                     "evidence": "<exact substring>"}]
  }
}
```

If the file is unusable:

```json
{"id": "...", "usable": false, "reject_reason": "1,140 words below the marker; needs 2,500"}
```

---

## 5. How your work is checked

You are not trusted, and neither is anyone else. Every batch runs through:

1. `TOOLS/enrich_verify_merge.py` — re-opens the source file and drops every tag whose
   evidence is not an exact substring. **It appends, never replaces**, and takes a
   timestamped backup first.
2. `TOOLS/audit_grounding.py` — a standing re-audit of every quotation in the whole corpus,
   not only the new ones. Current state: 18,416 strings checked, 3 failures.
3. Cross-paper checks — a quotation repeated across papers, a quotation under 25 characters,
   or two papers whose facets are ≥80% identical, are all flagged for review. A quote can be
   real and still be evidence of nothing.
4. A blind second coder on a seeded sample, scored with Cohen's κ.

**A batch with a high drop rate is a batch that was rushed**, and it is visible in the
numbers. There is no advantage in volume.

---

## 6. Presentation — every report looks like the report series

Any HTML you generate must match `REPORTS/report54.html`. Read that file before writing any
page. The rules that matter:

- **No coloured blocks with white text.** No filled chips, no badges, no pills. Colour
  carries meaning through **coloured text** and through **links** (`a{color:#0b4f9c}`).
  This is a standing instruction from Shir and it has had to be repeated; do not reintroduce
  it.
- Callouts are a **very light tint with a coloured left border** and dark body text —
  e.g. `background:#fff5f9; border-left:5px solid #c2185b`.
- KPI tiles: light grey background, thin border, the number large and coloured, the label
  small and grey.
- Tables: uppercase grey headers, thin rules, tabular numerals, right-aligned numbers.
- Hebrew pages are `dir="rtl"`; English pages contain **zero** Hebrew characters, and there
  is a gate (`TOOLS/check_hebrew.py`) that enforces it.
- Every figure must be rendered and looked at before delivery. A diagram that the reader
  cannot follow has failed — the reader has not.

---

## 7. Throughput — what a real batch looks like

Measured from the existing corpus, per paper: read the file, judge six facets, extract
between five and twenty content tags, each with a copy-pasted quotation.

- A careful paper takes **6–10 minutes** of agent time.
- Batches of **20 papers** are the right unit: large enough to be worth the setup, small
  enough that a systematic error is caught before it contaminates hundreds of records.
- Run the merge and the audit **after every batch**, never at the end. The drop rate is the
  early-warning signal.
- **Do not raise throughput by lowering care.** The corpus already contains 538 records; it
  does not need more records, it needs records that survive the audit.

---

## 8. Order of work — clean text first

`DATA/tagging_queue_priority.json` holds the queue, already gated and already cut into
batches of twenty. **Work it in order.** Do not pick papers yourself.

| Tier | Format | Papers |
|---|---|---|
| 1 | **XML** | 151 |
| 2 | **HTML** | 84 |
| 3 | pdftext | 250 |

**Why XML and HTML come first.** In those formats sentence boundaries survive intact. PDF
extraction breaks ligatures, hyphenates words across line breaks and interleaves columns —
and **every anchoring failure this project has had came out of PDF extraction**. An agent
working on clean text spends its time tagging; an agent working on broken text spends it
repairing the source, and then writes a quotation that will not match.

The first twelve batches are XML and HTML only. That is 235 papers before PDF is touched at
all, and by then the drop rate from the merge step will have shown whether the protocol is
being followed.

Within a tier the longest papers come first: they carry the most tags per unit of setup, and
a systematic error shows up in them soonest.

**24 files were rejected at the gate** and are listed under `rejected` with the reason.
Do not tag them. They need a better copy, not a more determined agent.
