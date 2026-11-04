#!/usr/bin/env python3
"""Bounded quote-fidelity check for the round-59 S286/S287 source rows.

Reads the captured Python subprocess documentation page and the two draft rows,
and asserts, for each row: the located quote is a verbatim substring of the
tag-stripped, entity-decoded, whitespace-collapsed capture; the quote is at or
below the 25-word ceiling; the quote's anchor section label occurs on the page;
and the two rows cite the same URL with distinct scopes.

Usage:
  python3 -B verify-quotes.py --capture PAGE.html --rows rows.tsv

Exit 0 all checks pass; 1 a named check failed; 2 usage/environment error.
Stdlib only; read-only over the capture and the rows file.
"""
import argparse
import html
import pathlib
import re
import sys

MAX_WORDS = 25


def normalize(markup: str) -> str:
    """Strip tags, decode entities, collapse whitespace (display-faithful)."""
    text = re.sub(r"<[^>]+>", "", markup)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--capture", required=True)
    ap.add_argument("--rows", required=True)
    args = ap.parse_args()

    capture = pathlib.Path(args.capture)
    rows_file = pathlib.Path(args.rows)
    if not capture.is_file():
        print("FINDING CAPTURE-MISSING %s" % capture, file=sys.stderr)
        return 2
    if not rows_file.is_file():
        print("FINDING ROWS-MISSING %s" % rows_file, file=sys.stderr)
        return 2

    raw = capture.read_text(encoding="utf-8")
    page = normalize(raw)
    rows = [
        line.rstrip("\n")
        for line in rows_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

    findings = []
    quotes = []
    scopes = []
    urls = []
    for line in rows:
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 13:
            findings.append("ROW-SHAPE %s cells=%d" % (cells[1] if cells else "?", len(cells)))
            continue
        row_id, source, scope, anchor, teaches = cells[1], cells[2], cells[5], cells[6], cells[7]
        m_url = re.search(r"https?://[^\s|]+", source)
        urls.append(m_url.group(0) if m_url else "")
        scopes.append(scope)
        m = re.search(r"`([^`]+)`", teaches)
        if not m:
            findings.append("QUOTE-MISSING %s" % row_id)
            continue
        quote = m.group(1).strip()
        quotes.append((row_id, quote))
        words = len(quote.split())
        if words > MAX_WORDS:
            findings.append("QUOTE-TOO-LONG %s words=%d" % (row_id, words))
        if quote not in page:
            findings.append("QUOTE-NOT-VERBATIM %s" % row_id)
        label = anchor.split(";")[0].strip()
        # An anchor label may be a section heading (visible text) or an
        # attribute anchor such as subprocess.CompletedProcess.returncode.
        if label and label not in page and label not in raw:
            findings.append("ANCHOR-LABEL-ABSENT %s label=%s" % (row_id, label))
        print("ROW %s words=%d verbatim=%s" % (row_id, words, quote in page))

    if len(set(urls)) != 1:
        findings.append("URLS-DIFFER %s" % " ".join(sorted(set(urls))))
    if len(set(scopes)) != len(scopes):
        findings.append("SCOPES-NOT-DISTINCT %s" % " | ".join(scopes))
    for row_id, quote in quotes:
        print("QUOTE %s %s" % (row_id, quote))

    for finding in findings:
        print("FINDING " + finding)
    print("SUMMARY checks=%d findings=%d" % (len(rows), len(findings)))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
