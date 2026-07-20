#!/usr/bin/env python3
"""Audit every paper/statistic assignment in the reconstructed corpus.

Acceptance criterion: at least one occurrence must use the term in an
unambiguously statistical or probabilistic sense in the paper's main text.
Bibliography-only occurrences and lexical false positives are rejected.
The script is deliberately conservative and leaves genuinely uncertain cases
as needs-review instead of turning a string match into a scientific assertion.
"""

from __future__ import annotations

import html
import hashlib
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from corpus_io import CORPUS_JSON, ROOT, load_corpus, save_json


AUDIT_PATH = ROOT / "DATA" / "statistics_audit.json"
OVERRIDES_PATH = ROOT / "DATA" / "statistics_audit_overrides.json"

BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "td", "th", "figcaption"}
REFERENCE_HEADINGS = {
    "references",
    "bibliography",
    "literature cited",
    "works cited",
}


def norm(value: str) -> str:
    value = html.unescape(value).replace("−", "-").replace("–", "-")
    # Generated hover labels are interface metadata, not article text.
    value = re.sub(
        r"(?:term·(?:stat|key|dom)|person·name|claim·type)", "", value,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", value).strip().lower()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def grounding_status(
    evidence: str, blocks: list[dict[str, Any]], source_available: bool
) -> str:
    """Classify quote-to-source grounding without fuzzy-match inflation."""
    if not source_available:
        return "source-unavailable"
    excerpt = norm(evidence)
    if not excerpt:
        return "empty-evidence"
    main_text = " ".join(
        block["text"] for block in blocks if block.get("in_main_text")
    )
    if excerpt in main_text:
        return "verified-main-text"
    reference_text = " ".join(
        block["text"] for block in blocks if block.get("in_references")
    )
    if excerpt in reference_text:
        return "verified-reference"
    return "not-exactly-located"


class TaggedBlockParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[dict[str, Any]] = []
        self.block_depth = 0
        self.block_tag = ""
        self.text: list[str] = []
        self.stats: list[str] = []
        self.stat_depth = 0
        self.stat_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in BLOCK_TAGS and self.block_depth == 0:
            self.block_depth = 1
            self.block_tag = tag
            self.text = []
            self.stats = []
        elif self.block_depth:
            self.block_depth += 1
        classes = set((attrs_dict.get("class") or "").split())
        if tag == "span" and "stat" in classes:
            self.stat_depth = 1
            self.stat_text = []
        elif self.stat_depth:
            self.stat_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self.stat_depth:
            self.stat_depth -= 1
            if self.stat_depth == 0:
                value = norm("".join(self.stat_text))
                if value:
                    self.stats.append(value)
        if self.block_depth:
            self.block_depth -= 1
            if self.block_depth == 0:
                value = norm("".join(self.text))
                if value:
                    self.blocks.append(
                        {"tag": self.block_tag, "text": value, "stats": self.stats[:]}
                    )
                self.block_tag = ""
                self.text = []
                self.stats = []

    def handle_data(self, data: str) -> None:
        if self.block_depth:
            self.text.append(data)
        if self.stat_depth:
            self.stat_text.append(data)


def parse_paper(path: Path) -> list[dict[str, Any]]:
    parser = TaggedBlockParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    headings = [block["text"].strip(" .:") for block in parser.blocks]
    full_text_starts = [
        i for i, heading in enumerate(headings) if heading.startswith("full text")
    ]
    full_text_start = full_text_starts[-1] if full_text_starts else -1
    # Some extracted papers include a table-of-contents entry named
    # "References" near the beginning.  The final exact heading is the actual
    # bibliography boundary.
    reference_starts = [
        i
        for i, heading in enumerate(headings)
        if i > full_text_start and heading in REFERENCE_HEADINGS
    ]
    reference_start = reference_starts[-1] if reference_starts else len(parser.blocks)
    for i, block in enumerate(parser.blocks):
        # The generated paper pages contain a statistics summary before the
        # actual article.  Treating that summary as independent evidence made
        # the old audit circular: its own asserted tag could "verify" itself.
        block["in_main_text"] = full_text_start < i < reference_start
        block["in_references"] = i > reference_start
    return parser.blocks


TERM_ALIASES = {
    "ANOVA": ["anova", "analysis of variance"],
    "Bayesian": ["bayesian", "bayes"],
    "R-squared": ["r-squared", "r2", "r²"],
    "bootstrap": ["bootstrap", "bootstrapp"],
    "chi-square": ["chi-square", "chi squared", "χ2", "χ²"],
    "confidence-interval": ["confidence interval", "confidence-interval"],
    "correlation": ["correlation", "correlated", "cross-correlation"],
    "degrees-of-freedom": ["degrees of freedom", "degree of freedom"],
    "effect-size": ["effect size", "effect-size"],
    "false-discovery-rate": ["false discovery rate", "fdr"],
    "hypothesis-testing": ["hypothesis test", "test the hypothesis", "testing the hypothesis"],
    "mean": ["mean", "average"],
    "median": ["median"],
    "null-hypothesis": ["null hypothesis", "null-hypothesis"],
    "odds-ratio": ["odds ratio", "odds-ratio"],
    "p-value": ["p-value", "p value", "p =", "p <", "p <=", "p ≤"],
    "regression": ["regression", "regressor"],
    "sample-size": ["sample size", "sample-size"],
    "standard-deviation": ["standard deviation", "standard-deviation"],
    "standard-error": ["standard error", "standard-error", "sem"],
    "statistical-power": ["statistical power", "power analysis"],
    "statistical-significance": ["statistical significance", "statistically significant", "significant", "significantly"],
    "t-test": ["t-test", "t test", "student's t"],
    "variance": ["variance", "variances"],
}


def blocks_for_term(blocks: list[dict[str, Any]], term: str) -> list[dict[str, Any]]:
    aliases = TERM_ALIASES[term]
    found = []
    for block in blocks:
        tagged = " ".join(block["stats"])
        if any(alias in tagged or alias in block["text"] for alias in aliases):
            found.append(block)
    return found


def initial_decision(term: str, evidence: str, blocks: list[dict[str, Any]]) -> tuple[str, str, str]:
    ev = norm(evidence)
    main = [block for block in blocks if block.get("in_main_text")]
    refs = [block for block in blocks if block.get("in_references")]
    searchable = " ".join(block["text"] for block in main) or ev

    if blocks and not main and refs:
        return "rejected", "bibliography", "occurrence appears only in references"

    if term == "statistical-significance":
        statistical = re.search(
            r"statistic(?:al|ally).{0,30}signific|signific.{0,30}(?:p\s*[<=>≤]|level\s*(?:of|at)?\s*\.?\d|confidence|test)",
            searchable,
        )
        if statistical:
            return "accepted", "focal-use", "explicit inferential-statistical context"
        return "rejected", "non-statistical-sense", "bare significant/significantly without inferential evidence"

    if term == "null-hypothesis":
        if re.search(r"null[- ]hypothesis", searchable):
            return "accepted", "focal-use", "explicit null-hypothesis language"
        return "rejected", "non-statistical-sense", "symbol H0 or other text without a null hypothesis"

    if term == "standard-error":
        if re.search(r"standard[- ]error\s+correction", searchable):
            return "rejected", "non-statistical-sense", "error-correction terminology, not sampling error"
        if re.search(r"standard[- ]errors?|\bsem\b", searchable):
            return "accepted", "focal-use", "explicit standard error or SEM"
        return "needs-review", "unclassified", "standard-error sense is not explicit"

    if term == "p-value":
        if re.search(r"predicted.{0,80}\bp\s*=", searchable) and not re.search(
            r"p[- ]value|signific|hypothesis|\btest\b", searchable
        ):
            return "rejected", "non-statistical-sense", "p denotes a predicted class probability"
        if re.search(r"p[- ]values?|\bp\s*(?:<|<=|≤|=)\s*\.?\d", searchable):
            return "accepted", "focal-use", "explicit p-value or inferential p notation"
        return "needs-review", "unclassified", "p-value evidence is not explicit"

    if term == "degrees-of-freedom":
        if re.search(r"degrees? of freedom.{0,80}(?:test|model|residual|chi|t[- ]?distribution|sample|estimate)", searchable) or re.search(
            r"(?:test|model|residual|chi|sample|estimate).{0,80}degrees? of freedom", searchable
        ):
            return "accepted", "focal-use", "degrees of freedom in a statistical model/test"
        return "needs-review", "unclassified", "may denote physical or mathematical degrees of freedom"

    if term == "mean":
        if re.search(r"mean[- ]field|meaning|by means of|vacuum average", searchable):
            return "needs-review", "unclassified", "mean/average may not denote a statistical summary"
        if re.search(r"\b(?:mean|average)\b", searchable):
            return "accepted", "focal-use", "numeric mean or average in main text"

    if term == "hypothesis-testing":
        if re.search(r"(?:hypothesis test|null hypothesis|test(?:ed|ing)? the hypothesis)", searchable):
            return "accepted", "focal-use", "explicit hypothesis-testing language"
        return "needs-review", "unclassified", "scientific hypothesis mention may not be a statistical test"

    # The remaining controlled terms are sufficiently specific to accept when
    # they occur in the main text.  Review-only and bibliography-only cases are
    # distinguished below by explicit overrides where needed.
    if main:
        role = "focal-use" if re.search(
            r"\b(?:we|our|was|were|is|are)\b.{0,80}" + re.escape(TERM_ALIASES[term][0]),
            searchable,
        ) else "substantive-mention"
        return "accepted", role, "unambiguous statistical/probabilistic term in main text"

    return "needs-review", "unclassified", "no auditable main-text occurrence located"


def load_overrides() -> dict[str, dict[str, str]]:
    if not OVERRIDES_PATH.exists():
        return {}
    source = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    # A grouped representation is easier for a human reviewer to inspect than
    # hundreds of repeated decision/role fields.  Continue to accept the old
    # flat representation for backwards compatibility.
    if not any(key in source for key in ("accepted", "rejected")):
        return source
    overrides: dict[str, dict[str, str]] = {}
    for role, keys in source.get("accepted", {}).items():
        for key in keys:
            overrides[key] = {
                "decision": "accepted",
                "role": role,
                "reason": "manual audit: unambiguous statistical/probabilistic sense",
            }
    for role, entries in source.get("rejected", {}).items():
        for key, reason in entries.items():
            overrides[key] = {
                "decision": "rejected",
                "role": role,
                "reason": reason,
            }
    for key, evidence in source.get("evidence_replacements", {}).items():
        if key not in overrides:
            overrides[key] = {
                "decision": "accepted",
                "role": "focal-use",
                "reason": "manual audit: unambiguous statistical/probabilistic sense",
            }
        overrides[key]["evidence"] = evidence
    return overrides


def main() -> None:
    corpus = load_corpus()
    overrides = load_overrides()
    audit_rows = []
    paper_cache: dict[str, list[dict[str, Any]]] = {}

    for record in corpus["records"]:
        paper_path = ROOT / record.get("url", "")
        source_available = paper_path.is_file()
        source_body_sha256 = ""
        if source_available:
            paper_cache[record["id"]] = parse_paper(paper_path)
            body_text = " ".join(
                block["text"]
                for block in paper_cache[record["id"]]
                if block.get("in_main_text")
            )
            source_body_sha256 = sha256_text(body_text)
        else:
            paper_cache[record["id"]] = []

        for annotation in record.get("statistics", []):
            term = annotation["term"]
            relevant = blocks_for_term(paper_cache[record["id"]], term)
            decision, role, reason = initial_decision(
                term, annotation.get("evidence", ""), relevant
            )
            key = f"{record['id']}::{term}"
            if key in overrides:
                override = overrides[key]
                decision = override["decision"]
                role = override["role"]
                reason = override["reason"]
                if override.get("evidence"):
                    annotation["evidence"] = override["evidence"]
            evidence = annotation.get("evidence", "")
            grounding = grounding_status(
                evidence, paper_cache[record["id"]], source_available
            )
            provenance = {
                "source_path": record.get("url", ""),
                "source_body_sha256": source_body_sha256 or None,
                "evidence_sha256": sha256_text(norm(evidence)),
                "grounding_status": grounding,
            }
            annotation.update(
                {
                    "decision": decision,
                    "role": role,
                    "reason": reason,
                    "provenance": provenance,
                }
            )
            audit_rows.append(
                {
                    "paper_id": record["id"],
                    "discipline": record["discipline"],
                    "term": term,
                    "decision": decision,
                    "role": role,
                    "reason": reason,
                    "evidence": evidence,
                    "provenance": provenance,
                    "main_text_occurrences": len(
                        [block for block in relevant if block.get("in_main_text")]
                    ),
                    "reference_occurrences": len(
                        [block for block in relevant if block.get("in_references")]
                    ),
                }
            )

    save_json(CORPUS_JSON, corpus)
    summary = {
        "criterion": "unambiguous statistical/probabilistic sense in main text; bibliography-only and lexical false positives excluded",
        "total_assignments": len(audit_rows),
        "decisions": dict(Counter(row["decision"] for row in audit_rows)),
        "grounding": dict(
            Counter(row["provenance"]["grounding_status"] for row in audit_rows)
        ),
        "by_term": {},
        "rows": audit_rows,
    }
    for term in sorted({row["term"] for row in audit_rows}):
        term_rows = [row for row in audit_rows if row["term"] == term]
        summary["by_term"][term] = dict(Counter(row["decision"] for row in term_rows))
    save_json(AUDIT_PATH, summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
