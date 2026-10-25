#!/usr/bin/env python3
"""row-check.py — pre-append gate for a corpus/SOURCES.md registry table block.

Reads a Markdown table block and checks every data row against the invariants a
row must satisfy before it is appended to a lane's corpus/SOURCES.md registry:

  X01 indent          0-3 leading ASCII spaces; 4+ is indented code, which the
                      census drops silently, so the row would simply vanish
  X02 pipe-in-cell    no literal '|' and no escaped '\\|' inside any cell
  X03 row-shape       the line opens and closes with '|'
  E01 column-count    exactly 11 columns                                    (census E01)
  E02 id-format       id cell matches ^S[0-9]{3,}$                           (census E02)
  E03 duplicate-id    unique inside the block; with --registry, also unique
                      against the registry being appended to               (census E03)
  E05 kind-enum       kind in the contract enum                             (census E05)
  E06 tier-enum       tier in A|B|C                                         (census E06)
  E07 status-enum     status in queued|mined|rejected                       (census E07)
  E08 opened-format   opened is a calendar ISO date not after --today        (census E08)
  E09 recheck-format  ISO date, NNd, or a symbolic cadence this lane uses    (census E09)
  E10 community-at-A  kind=community is never tier A                        (census E10)
  E11 used-by-missing every used-by path exists under --root                (census E11)

X-codes are pre-append strictness the census cannot express: it skips an
indented row entirely, and a literal pipe inside a cell only shows up there as
a shifted column count. E-codes are exactly the codes of
`scripts/sources-census.sh validate`, so a row that passes here also passes that
validator. Column splitting is a plain split on '|' — the census's own view —
so a literal or escaped pipe additionally reports E01, which is why an X02
fixture row carries both codes; X02 is what names the cause.

Vocabularies are derived, not invented:
  status       <- corpus/SOURCES.md status column = mined, queued, rejected
                  (CORPUS.md, `SOURCES.md — where a shokunin learns`, `status`)
  symbolic     <- corpus/SOURCES.md recheck column = on-change, on-correction,
                  on-release (`recheck — ISO date or cadence (90d, 180d,
                  on-release)`; `90d`/`180d`/`365d` are the NNd form)
  kind / tier  <- CORPUS.md `kind` and `tier`, the same enums census E05/E06 apply

`--derive-vocab PATH` re-derives status and cadence from a live registry and
exits non-zero if either set differs from the constants below, so silent drift
in the corpus vocabulary is visible instead of hidden.

Read-only: reads the table, stats used-by paths, writes nothing.

Usage
  row-check.py --table rows-fixture.md --root . --expect rows-fixture.expect.tsv
  row-check.py --table corpus/SOURCES.md --root .          # calibration: 0 findings
  row-check.py --derive-vocab corpus/SOURCES.md            # vocabulary provenance
  row-check.py --selftest                                  # each code fails on its own

Exit 0 iff every row is clean (and, with --expect, every expectation is met).
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
import tempfile

COLUMNS = (
    "id", "source", "kind", "tier", "scope", "anchor",
    "teaches", "status", "opened", "recheck", "used-by",
)

# Derived from corpus/SOURCES.md + CORPUS.md; --derive-vocab re-checks the first two.
STATUS_ENUM = ("mined", "queued", "rejected")
SYMBOLIC_CADENCES = ("on-change", "on-correction", "on-release")
KIND_ENUM = (
    "book", "code", "community", "dataset", "docs",
    "own-work", "paper", "spec", "talk", "tool",
)
TIER_ENUM = ("A", "B", "C")

CODE_NAMES = {
    "X01": "indent", "X02": "pipe-in-cell", "X03": "row-shape",
    "E01": "column-count", "E02": "id-format", "E03": "duplicate-id",
    "E05": "kind-enum", "E06": "tier-enum", "E07": "status-enum",
    "E08": "opened-format", "E09": "recheck-format", "E10": "community-at-A",
    "E11": "used-by-missing",
}

LEAD_RE = re.compile(r"^([ \t]*)(\|.*)$")
ID_RE = re.compile(r"^S[0-9]{3,}$")
ISO_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
CADENCE_RE = re.compile(r"^[0-9]+d$")
SEP_RE = re.compile(r"^:?-+:?$")


class Row:
    __slots__ = ("lineno", "lead", "body", "cells")

    def __init__(self, lineno, lead, body, cells):
        self.lineno = lineno
        self.lead = lead
        self.body = body
        self.cells = cells


def iter_rows(text):
    """Yield every table data row in `text`; skip headers, separators, prose."""
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip("\r")
        match = LEAD_RE.match(line)
        if match is None:
            continue
        lead, body = match.group(1), match.group(2).rstrip()
        parts = body.split("|")
        inner = parts[1:]
        if body.endswith("|") and inner:
            inner = inner[:-1]
        cells = [cell.strip() for cell in inner]
        if not cells or not any(cells):
            continue
        if cells[0].lower() == "id":
            continue
        if all(SEP_RE.match(cell) for cell in cells if cell):
            continue
        yield Row(lineno, lead, body, cells)


def valid_iso(value):
    if not ISO_RE.match(value):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def valid_recheck(value):
    if ISO_RE.match(value):
        return valid_iso(value) is not None
    if CADENCE_RE.match(value):
        return True
    return value in SYMBOLIC_CADENCES


def usedby_paths(cell):
    paths = []
    for part in re.split(r"[,;]", cell):
        path = part.strip()
        if path and path != "\u2014":
            paths.append(path)
    return paths


def evaluate(rows, root, today, registry_ids=frozenset()):
    """Return [(lineno, id, code, detail)] for every defect found."""
    findings = []
    seen = {}
    for row in rows:
        rid = row.cells[0]
        body = row.body
        lead = row.lead

        def add(code, detail):
            findings.append((row.lineno, rid, code, detail))

        if "\t" in lead:
            add("X01", "indent=tab")
        elif len(lead) > 3:
            add("X01", "indent=%d max=3" % len(lead))

        escaped = body.find("\\|")
        if escaped >= 0:
            add("X02", "form=escaped char=%d" % escaped)
        else:
            for pos, char in enumerate(body):
                if (char == "|" and 0 < pos < len(body) - 1
                        and body[pos - 1] != " " and body[pos + 1] != " "):
                    add("X02", "form=literal char=%d text=%s"
                        % (pos, body[max(0, pos - 14):pos + 15]))
                    break

        if not body.endswith("|"):
            add("X03", "no-closing-pipe")

        ncols = len(row.cells)
        if ncols != 11:
            add("E01", "fields=%d expected=11" % ncols)

        if not ID_RE.match(rid):
            add("E02", "id=%s" % (rid or "<empty>"))
        else:
            if rid in seen:
                add("E03", "where=block first-line=%d" % seen[rid])
            else:
                seen[rid] = row.lineno
            if rid in registry_ids:
                add("E03", "where=registry")

        if ncols != 11:
            continue

        kind = row.cells[2]
        tier = row.cells[3]
        status = row.cells[7]
        opened = row.cells[8]
        recheck = row.cells[9]
        usedby = row.cells[10]

        if kind not in KIND_ENUM:
            add("E05", "kind=%s" % kind)
        if tier not in TIER_ENUM:
            add("E06", "tier=%s" % tier)
        if status not in STATUS_ENUM:
            add("E07", "status=%s" % status)

        opened_date = valid_iso(opened)
        if opened_date is None:
            add("E08", "opened=%s" % opened)
        elif opened_date > today:
            add("E08", "opened=%s future" % opened)

        if not valid_recheck(recheck):
            add("E09", "recheck=%s" % recheck)

        if tier == "A" and kind == "community":
            add("E10", "community-at-A")

        for path in usedby_paths(usedby):
            if not os.path.exists(os.path.join(root, path)):
                add("E11", "used-by=%s" % path)
    return findings


def load_table(path):
    if path == "-":
        return sys.stdin.read(), "<stdin>"
    with open(path, encoding="utf-8") as handle:
        return handle.read(), path


def load_registry_ids(path):
    text, _name = load_table(path)
    ids = set()
    for row in iter_rows(text):
        if ID_RE.match(row.cells[0]):
            ids.add(row.cells[0])
    return ids


def load_expectations(path):
    expected = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            rid, _sep, codes = line.partition("\t")
            codes = codes.strip()
            if codes in ("", "none", "-"):
                expected[rid.strip()] = set()
            else:
                expected[rid.strip()] = {
                    code.strip() for code in codes.split(",") if code.strip()
                }
    return expected


def check_expectations(expected, findings, table_ids):
    actual = {}
    for _lineno, rid, code, _detail in findings:
        actual.setdefault(rid, set()).add(code)
    problems = []
    for rid in expected:
        if rid not in table_ids:
            problems.append("id=%s row-absent" % rid)
            continue
        want = expected[rid]
        got = actual.get(rid, set())
        missing = sorted(want - got)
        extra = sorted(got - want)
        if missing:
            problems.append("id=%s missing=%s" % (rid, ",".join(missing)))
        if extra:
            problems.append("id=%s unexpected=%s" % (rid, ",".join(extra)))
    return problems


def default_root():
    here = os.path.abspath(os.getcwd())
    probe = here
    while True:
        if os.path.isfile(os.path.join(probe, "corpus", "SOURCES.md")):
            return probe
        parent = os.path.dirname(probe)
        if parent == probe:
            return here
        probe = parent


def derive_vocab(path):
    text, _name = load_table(path)
    statuses = set()
    cadences = set()
    rows = 0
    for row in iter_rows(text):
        rows += 1
        if len(row.cells) != 11:
            continue
        statuses.add(row.cells[7])
        recheck = row.cells[9]
        if ISO_RE.match(recheck) or CADENCE_RE.match(recheck):
            continue
        cadences.add(recheck)

    status_ok = statuses == set(STATUS_ENUM)
    cadence_ok = cadences == set(SYMBOLIC_CADENCES)
    print("registry=%s rows=%d" % (path, rows))
    print("statuses derived=%s constants=%s match=%s"
          % (",".join(sorted(statuses)) or "-",
             ",".join(sorted(STATUS_ENUM)),
             "yes" if status_ok else "no"))
    print("cadences derived=%s constants=%s match=%s"
          % (",".join(sorted(cadences)) or "-",
             ",".join(sorted(SYMBOLIC_CADENCES)),
             "yes" if cadence_ok else "no"))
    return 0 if status_ok and cadence_ok else 1


def row_text(rid="S990", source="fixture source \u2014 https://example.invalid/fixture",
             kind="docs", tier="A", scope="fixture scope", anchor="\u00a7 1",
             teaches="fixture teaches", status="queued", opened="2026-10-25",
             recheck="90d", usedby="\u2014", lead=""):
    cells = (rid, source, kind, tier, scope, anchor, teaches,
             status, opened, recheck, usedby)
    return "%s| %s |" % (lead, " | ".join(cells))


def selftest():
    cases = [
        ("good",
         row_text(usedby="corpus/knowledge/fixture-target.md"), set()),
        ("column-count-10",
         "| S901 | src \u2014 https://example.invalid/cols | docs | A | s | \u00a7 1 "
         "| ten columns only | queued | 2026-10-25 | 90d |", {"E01"}),
        ("id-two-digits", row_text(rid="S90"), {"E02"}),
        ("indent-4", row_text(lead="    "), {"X01"}),
        ("literal-pipe", row_text(teaches="a|b"), {"X02", "E01"}),
        ("escaped-pipe", row_text(teaches="a\\|b"), {"X02", "E01"}),
        ("status-enum", row_text(status="watch"), {"E07"}),
        ("recheck-format", row_text(recheck="90 days"), {"E09"}),
        ("used-by-missing",
         row_text(usedby="corpus/knowledge/absent-fixture.md"), {"E11"}),
        ("kind-enum", row_text(kind="blog"), {"E05"}),
        ("tier-enum", row_text(tier="D"), {"E06"}),
        ("opened-format", row_text(opened="2026-13-01"), {"E08"}),
        ("registry-collision", row_text(rid="S114"), {"E03"}),
        ("community-at-A", row_text(kind="community"), {"E10"}),
    ]
    header = ("| id | source | kind | tier | scope | anchor | teaches | status "
              "| opened | recheck | used-by |\n"
              "|---|---|---|---|---|---|---|---|---|---|---|\n")
    today = datetime.date(2026, 10, 25)
    failures = []
    expected_by_id = {}
    table_ids = set()

    with tempfile.TemporaryDirectory(prefix="row-check-selftest-") as root:
        os.makedirs(os.path.join(root, "corpus", "knowledge"), exist_ok=True)
        with open(os.path.join(root, "corpus", "knowledge", "fixture-target.md"),
                  "w", encoding="utf-8") as handle:
            handle.write("fixture target\n")

        for name, text, want in cases:
            rows = list(iter_rows(header + text))
            if len(rows) != 1:
                failures.append("%s: parsed %d rows, expected 1"
                                % (name, len(rows)))
                continue
            rid = rows[0].cells[0]
            table_ids.add(rid)
            expected_by_id[rid] = want
            got = {code for _l, _i, code, _d in evaluate(rows, root, today, {"S114"})}
            if got != want:
                failures.append("%s: got=%s want=%s"
                                % (name,
                                   ",".join(sorted(got)) or "-",
                                   ",".join(sorted(want)) or "-"))

        defect_ids = {rid for rid, want in expected_by_id.items() if want}
        control = check_expectations(
            {rid: expected_by_id[rid] for rid in defect_ids}, [], table_ids)
        control_ok = len(control) == len(defect_ids)
        if not control_ok:
            failures.append("control: always-clean evaluator passed %d/%d defect rows"
                            % (len(defect_ids) - len(control), len(defect_ids)))

    passed = len(cases) - sum(1 for failure in failures if not failure.startswith("control:"))
    print("selftest cases=%d pass=%d fail=%d control=%s"
          % (len(cases), passed, len(failures),
             "FALSE-GREEN-REJECTED" if control_ok else "FALSE-GREEN-SLIPPED"))
    for failure in failures:
        print("  FAIL %s" % failure)
    return 0 if not failures else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="row-check.py",
        description="Pre-append schema check for SOURCES.md registry rows.")
    parser.add_argument("--table", default="-",
                        help="markdown table block to check ('-' = stdin)")
    parser.add_argument("--root", default=None,
                        help="lane root used to resolve used-by paths "
                             "(default: nearest ancestor holding corpus/SOURCES.md)")
    parser.add_argument("--registry", default=None,
                        help="existing registry; its ids are rejected as duplicates")
    parser.add_argument("--expect", default=None,
                        help="TSV of 'id<TAB>expected-codes' ('none' = clean row)")
    parser.add_argument("--today", default=None,
                        help="YYYY-MM-DD bound for the opened check (default: today)")
    parser.add_argument("--format", choices=("text", "tsv"), default="text")
    parser.add_argument("--derive-vocab", metavar="SOURCES_MD", default=None,
                        help="print status/cadence vocabulary derived from a registry")
    parser.add_argument("--selftest", action="store_true",
                        help="prove each code fires on its own fixture")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.derive_vocab:
        return derive_vocab(args.derive_vocab)

    text, name = load_table(args.table)
    root = os.path.abspath(args.root) if args.root else default_root()
    today = (datetime.date.fromisoformat(args.today) if args.today
             else datetime.date.today())
    registry_ids = (load_registry_ids(args.registry) if args.registry
                    else frozenset())

    rows = list(iter_rows(text))
    findings = evaluate(rows, root, today, registry_ids)
    bad = {lineno for lineno, _i, _c, _d in findings}
    clean = len(rows) - len(bad)

    if args.format == "tsv":
        for lineno, rid, code, detail in findings:
            print("%d\t%s\t%s\t%s" % (lineno, rid, code, detail))
    else:
        print("table=%s root=%s rows=%d" % (name, root, len(rows)))
        for lineno, rid, code, detail in findings:
            print("row=%d id=%s %s %s %s"
                  % (lineno, rid, code, CODE_NAMES[code], detail))

    counts = {}
    for _lineno, _rid, code, _detail in findings:
        counts[code] = counts.get(code, 0) + 1
    histogram = ",".join("%s:%d" % (code, counts[code])
                         for code in sorted(counts)) or "-"
    summary = ("summary rows=%d ok=%d fail=%d codes=%s"
               % (len(rows), clean, len(bad), histogram))
    print(summary, file=sys.stderr if args.format == "tsv" else sys.stdout)

    problems = []
    if args.expect:
        expected = load_expectations(args.expect)
        problems = check_expectations(expected, findings,
                                      {row.cells[0] for row in rows})
        if args.format == "tsv":
            for problem in problems:
                print("expect-miss %s" % problem, file=sys.stderr)
        else:
            print("expect=%s ids=%d unmet=%d"
                  % (args.expect, len(expected), len(problems)))
            for problem in problems:
                print("expect-miss %s" % problem)

    return 1 if bad or problems else 0


if __name__ == "__main__":
    sys.exit(main())
