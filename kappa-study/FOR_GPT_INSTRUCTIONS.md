# Second-coder task: inter-rater reliability for statistical-tag decisions

Hello — you are being asked to act as the **second, independent coder** in a formal
inter-rater reliability study (Cohen's κ) for the Meta-Tagging Project.

## Why you
The first coding of these assignments was produced by one system (Claude). If that same
system codes them again it measures self-consistency, not reliability — which would be
misleading in a publication. You are a **different system**, so your coding is genuinely
independent. Your decisions will be compared against the first coder's, and κ will be
reported in the preprint with you named as the second coder.

**Please do not look up the project's published audit** (`report_statistics.html`,
`statistics_audit.json`, or the preprint's §5). Those contain the first coder's decisions.
Judge each row only from the evidence quoted in the sheet.

## What to do
1. Read `CODING_MANUAL.txt` — it states the accept/reject rules precisely.
2. Open `coding_sheet.csv`. It has 120 rows with these columns:
   `row_id, paper_id, discipline, term, evidence, decision, note`
   The `decision` column is **empty on purpose** — the first coder's calls are withheld.
3. For every row, write exactly `accept` or `reject` in `decision`.
   - **accept** = the term is used in a genuine statistical / probabilistic sense
   - **reject** = the match is lexical only (e.g. "significant" meaning "important",
     `H0` as a Hubble constant or Hamiltonian, `p` as a plain probability label,
     an occurrence only in a reference list, or evidence too thin to establish the sense)
   - If unsure, **reject** — the burden of proof is on the assignment.
   - Optionally add a short `note`. Notes are read, not discarded.
4. Do not leave any row blank. Do not try to infer what the first coder decided.
5. Return the completed file as **`responses.csv`** (same columns, same `row_id` values).

## Notes on the sample
120 assignments drawn from 519 audited ones, stratified **60 accepted / 60 rejected** by the
first coder. Rejections are deliberately oversampled because they are the contested calls —
so please don't infer a base rate from the sheet; roughly half being rejects is by design,
not a hint.

## What happens next
`python TOOLS/make_kappa_study.py score KAPPA_STUDY/responses.csv` produces Cohen's κ with a
95% CI, percent agreement, the confusion matrix, and a list of every disagreement. The
disagreements get adjudicated and reported — they are the most informative part, so
please don't smooth them over to match what you think we want.

Thank you — this is the step that unblocks journal submission.
