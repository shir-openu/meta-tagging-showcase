#!/usr/bin/env python3
"""Render a compact, inspectable HTML report of the statistical audit."""

from __future__ import annotations

import html
import json
from collections import Counter

from corpus_io import AUDIT_JSON, ROOT, load_corpus


OUTPUT = ROOT / "report_statistics.html"


def main() -> None:
    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    corpus = load_corpus()
    titles = {record["id"]: record["title"] for record in corpus["records"]}
    decisions = audit["decisions"]
    term_rows = []
    for term, counts in audit["by_term"].items():
        term_rows.append(
            f"<tr><td><code>{html.escape(term)}</code></td>"
            f"<td>{counts.get('accepted', 0)}</td>"
            f"<td>{counts.get('rejected', 0)}</td></tr>"
        )
    rejected_rows = []
    grounding_rows = []
    grounding_counts = Counter(
        row["provenance"]["grounding_status"] for row in audit["rows"]
    )
    accepted_grounding_counts = Counter(
        row["provenance"]["grounding_status"]
        for row in audit["rows"]
        if row["decision"] == "accepted"
    )
    for status in sorted(grounding_counts):
        grounding_rows.append(
            f"<tr><td><code>{html.escape(status)}</code></td>"
            f"<td>{accepted_grounding_counts.get(status, 0)}</td>"
            f"<td>{grounding_counts[status]}</td></tr>"
        )
    provenance_exception_rows = []
    for row in audit["rows"]:
        if row["decision"] != "rejected":
            continue
        rejected_rows.append(
            "<tr>"
            f"<td>{html.escape(titles[row['paper_id']])}</td>"
            f"<td><code>{html.escape(row['term'])}</code></td>"
            f"<td>{html.escape(row['role'])}</td>"
            f"<td>{html.escape(row['reason'])}</td>"
            f"<td>{html.escape(row['evidence'])}</td>"
            "</tr>"
        )
    for row in audit["rows"]:
        status = row["provenance"]["grounding_status"]
        if row["decision"] != "accepted" or status == "verified-main-text":
            continue
        provenance_exception_rows.append(
            "<tr>"
            f"<td>{html.escape(titles[row['paper_id']])}</td>"
            f"<td><code>{html.escape(row['term'])}</code></td>"
            f"<td><code>{html.escape(status)}</code></td>"
            f"<td>{html.escape(row['evidence'])}</td>"
            "</tr>"
        )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Statistical-tag audit</title>
<style>body{{font:16px/1.55 system-ui,sans-serif;max-width:1200px;margin:2rem auto;padding:0 1rem;color:#17202a}}h1,h2{{line-height:1.2}}table{{width:100%;border-collapse:collapse;margin:1rem 0 2rem}}th,td{{border:1px solid #ccd5df;padding:.45rem;vertical-align:top;text-align:left}}th{{background:#eef3f7}}code{{color:#075985}}.n{{font-size:1.5rem;font-weight:700}}.note{{background:#fff7d6;padding:1rem;border-left:4px solid #ca8a04}}</style></head><body>
<h1>Statistical-tag audit</h1>
<p class="note"><b>Inclusion criterion:</b> {html.escape(audit['criterion'])}. Generated summaries cannot verify themselves; the parser evaluates article body separately from bibliography.</p>
<p><span class="n">{audit['total_assignments']}</span> legacy paper–term assignments: <b>{decisions.get('accepted', 0)}</b> accepted and <b>{decisions.get('rejected', 0)}</b> rejected; <b>{decisions.get('needs-review', 0)}</b> unresolved.</p>
<p>Semantic acceptance and excerpt provenance are distinct. An accepted term can have a locally verified body excerpt, an unavailable local source, or a legacy excerpt that still needs exact anchoring.</p>
<h2>Excerpt grounding status</h2>
<table><thead><tr><th>status</th><th>accepted assignments</th><th>all assignments</th></tr></thead><tbody>{''.join(grounding_rows)}</tbody></table>
<h2>Decision counts by controlled term</h2>
<table><thead><tr><th>term</th><th>accepted</th><th>rejected</th></tr></thead><tbody>{''.join(term_rows)}</tbody></table>
<h2>Rejected assignments</h2>
<table><thead><tr><th>paper</th><th>term</th><th>failure class</th><th>reason</th><th>legacy evidence</th></tr></thead><tbody>{''.join(rejected_rows)}</tbody></table>
<h2>Accepted assignments without an exact local-body excerpt</h2>
<table><thead><tr><th>paper</th><th>term</th><th>grounding status</th><th>evidence excerpt</th></tr></thead><tbody>{''.join(provenance_exception_rows)}</tbody></table>
</body></html>"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(
        f"wrote {OUTPUT.name} with {len(rejected_rows)} rejected assignments and "
        f"{len(provenance_exception_rows)} accepted provenance exceptions"
    )


if __name__ == "__main__":
    main()
