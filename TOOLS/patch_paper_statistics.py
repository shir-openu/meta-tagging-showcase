#!/usr/bin/env python3
"""Synchronize generated paper-page statistic boxes with the audited corpus."""

from __future__ import annotations

import html
import re
from pathlib import Path

from audit_statistics import TERM_ALIASES, norm
from corpus_io import ROOT, load_corpus


STATBOX_RE = re.compile(
    r'<div class="xdisc statbox">.*?</table></div>', re.DOTALL
)
STAT_SPAN_RE = re.compile(
    r'<span class="stat">(?P<label>.*?)<span class="tag">term·stat</span></span>',
    re.DOTALL,
)
REFERENCE_RE = re.compile(
    r"<p>\s*(?:References|Bibliography|Literature Cited|Works Cited)\s*</p>",
    re.IGNORECASE,
)
SYMBOLS = {
    "R-squared": "R²",
    "chi-square": "χ²",
    "confidence-interval": "CI",
    "degrees-of-freedom": "df",
    "false-discovery-rate": "FDR",
    "mean": "μ",
    "null-hypothesis": "H0",
    "odds-ratio": "OR",
    "p-value": "p",
    "regression": "β",
    "sample-size": "n/N",
    "standard-deviation": "SD/σ",
    "standard-error": "SE",
    "t-test": "t",
    "variance": "σ²",
}


def visible_label(fragment: str) -> str:
    return norm(re.sub(r"<[^>]+>", "", html.unescape(fragment)))


def candidate_terms(label: str) -> set[str]:
    candidates = set()
    compact = label.replace("-", " ")
    for term, aliases in TERM_ALIASES.items():
        for alias in aliases:
            alias_norm = norm(alias).replace("-", " ")
            if compact == alias_norm or compact.startswith(alias_norm + " "):
                candidates.add(term)
    if label in {"p", "p value", "p values", "p-value", "p-values"}:
        candidates.add("p-value")
    if label in {"h0", "h 0"}:
        candidates.add("null-hypothesis")
    if label in {"r2", "r²", "r-squared"}:
        candidates.add("R-squared")
    if label in {"df", "d.f."}:
        candidates.add("degrees-of-freedom")
    return candidates


def unwrap_rejected(source: str, accepted: set[str], rejected: set[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        label = match.group("label")
        candidates = candidate_terms(visible_label(label))
        if candidates and not (candidates & accepted) and candidates <= rejected:
            return label
        return match.group(0)

    return STAT_SPAN_RE.sub(replace, source)


def statbox(items: list[dict[str, str]]) -> str:
    grounding_labels = {
        "verified-main-text": "exact local body",
        "verified-reference": "excerpt resolves to reference",
        "source-unavailable": "local source unavailable",
        "not-exactly-located": "excerpt not exactly located",
        "empty-evidence": "empty evidence",
    }
    rows = []
    for item in sorted(items, key=lambda value: value["term"]):
        term = item["term"]
        symbol = SYMBOLS.get(term)
        label = html.escape(term)
        if symbol:
            label += f' <span class="ssym">{html.escape(symbol)}</span>'
        status = item.get("provenance", {}).get("grounding_status", "unknown")
        status_label = grounding_labels.get(status, status)
        rows.append(
            f'<tr><td class="k st">{label}</td><td><span class="ev"> &mdash; '
            f'&ldquo;{html.escape(item.get("evidence", ""))}&rdquo;</span> '
            f'<small style="color:#64748b">[{html.escape(status_label)}]</small></td></tr>'
        )
    return (
        '<div class="xdisc statbox"><b>Statistics &mdash; audited cross-field join keys</b>'
        '<div class="xd-sub">Semantically accepted after sense review; excerpt grounding status is shown separately. '
        '<a href="../report_statistics.html">Audit report</a>.</div><table>'
        + "".join(rows)
        + "</table></div>"
    )


def main() -> None:
    corpus = load_corpus()
    pages = 0
    for record in corpus["records"]:
        path = ROOT / record.get("url", "")
        if not path.is_file() or path.suffix.lower() != ".html":
            continue
        accepted_items = [
            item for item in record["statistics"] if item["decision"] == "accepted"
        ]
        accepted = {item["term"] for item in accepted_items}
        rejected = {
            item["term"] for item in record["statistics"] if item["decision"] == "rejected"
        }
        raw = path.read_bytes()
        newline = "\r\n" if b"\r\n" in raw else "\n"
        source = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
        source, substitutions = STATBOX_RE.subn(statbox(accepted_items), source, count=1)
        if substitutions == 0 and not record["statistics"]:
            continue
        if substitutions != 1:
            raise RuntimeError(f"expected one statistics box in {path}")
        references = list(REFERENCE_RE.finditer(source))
        boundary = references[-1].start() if references else len(source)
        body = unwrap_rejected(source[:boundary], accepted, rejected)
        bibliography = STAT_SPAN_RE.sub(lambda match: match.group("label"), source[boundary:])
        rendered = (body + bibliography).replace("\r\n", "\n")
        if newline == "\r\n":
            rendered = rendered.replace("\n", "\r\n")
        path.write_bytes(rendered.encode("utf-8"))
        pages += 1
    print(f"synchronized {pages} generated paper pages")


if __name__ == "__main__":
    main()
