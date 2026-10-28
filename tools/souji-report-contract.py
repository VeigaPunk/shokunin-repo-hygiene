#!/usr/bin/env python3
"""souji-report-contract.py — round-report contract predicates (r36, C2).

The r35 non-author spot-check routed four report defects: missing required
sections, a `## SHONEN` heading with no per-box lines, no trend verdicts, no
stale-lane line (corpus/lessons/round-35-verifier-spotcheck.md, "Routed
defects" 4). tools/souji-pre-report-gate.sh checked none of them. This module
implements those predicates as pure text reads over the filed report, so the
gate can fail before the report is committed instead of the closure finding
it afterwards.

Predicates (each prints one `check-<name>=PASS|FAIL` line):

  sections      the six canonical headings appear, each once, in the
                contract's order: work performed, landed changes,
                before/after measurements, sources & frontier, trend
                verdicts, stale-lane.
  shonen-boxes  a `## SHONEN` section carries one `- [x]`/`- [~]`/`- [ ]`
                line per box of the lane's SHONEN.md (a report with fewer
                box lines cannot be a per-box assessment).
  trends        exactly one verdict line per learning trend (expansion,
                quality, discernment), each carrying a verdict token
                improved | harmed | unchanged | unprovable-but-better.
  stale-lane    a `Stale-lane` line (or heading) with a non-empty body.
  measurements  the before/after section carries at least one table row
                naming a measured commit (backticked 7-64 hex) and a
                counting command (a second backticked span).
  claims        the work-performed section names 1-3 distinct claim ids
                C1..C3 (the round's declared claim cap).
  evidence      the report carries at least one repo-relative evidence
                pointer (backticked census/ corpus/ tools/ tests/ .ufo/
                path) or a 40+ hex commit id.

Read-only: the report bytes and SHONEN.md are read, nothing is executed and
nothing is written. A heading whose text appears twice fails `sections`. The
tool judges round reports only: seat notes and lessons are not its surface and
will fail most predicates by construction.

CLI:
  python3 -B tools/souji-report-contract.py --report ABS --shonen ABS
  python3 -B tools/souji-report-contract.py --selftest

Exit: 0 every predicate passes, 1 any FAIL, 2 usage / unreadable input.
"""
import argparse
import re
import sys

VERDICT_TOKENS = ("unprovable-but-better", "improved", "harmed", "unchanged")
TRENDS = ("expansion", "quality", "discernment")
SECTION_KEYS = (
    "work performed",
    "landed changes",
    "before -> after measurements",
    "sources & frontier",
    "trend verdicts",
    "stale-lane",
)
HEADING = re.compile(r"^ {0,3}##\s+(.*\S)\s*$")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
COMMENT_OPEN = "<!--"
COMMENT_CLOSE = "-->"
BOX = re.compile(r"^\s*[-*]\s*\[[xX~ ]\]")
COMMIT = re.compile(r"^[0-9a-f]{7,64}$")
EVIDENCE = re.compile(r"^(census|corpus|tools|tests|\.ufo)/")
BACKTICK = re.compile(r"`([^`\n]+)`")


def fail(code, msg):
    sys.stderr.write("ERROR %s: %s\n" % (code, msg))
    return 2


def normalize_heading(text):
    low = " ".join(text.strip().lower().split())
    return low.replace("\u2192", "->").replace("\u2014", "-").replace("--", "-") if "->" in text else low.replace("\u2192", "->")


def mask(lines):
    """Blank fenced blocks and HTML comments so a quoted heading is not a heading.

    r36 A3 after wave seat SwarmReviewer09: the sections predicate accepted every
    heading hidden inside a ``` fence or an HTML comment (a fabricated report
    passed) and rejected a conforming report that merely quoted a heading.
    """
    out = []
    fence = None
    in_comment = False
    for line in lines:
        if in_comment:
            out.append("")
            if COMMENT_CLOSE in line:
                in_comment = False
            continue
        stripped = line.lstrip()
        if stripped.startswith(COMMENT_OPEN):
            out.append("")
            if COMMENT_CLOSE not in stripped:
                in_comment = True
            continue
        m = FENCE.match(line)
        if fence:
            out.append("")
            if m and m.group(1)[0] == fence:
                fence = None
            continue
        if m:
            fence = m.group(1)[0]
            out.append("")
            continue
        out.append(line)
    return out


def split_sections(lines):
    """Return [(heading_index, heading_text, [(line_index, text)])] over masked lines."""
    heads = []
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m:
            heads.append((i, m.group(1)))
    out = []
    for n, (i, text) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        out.append((i, text, list(enumerate(lines[i + 1:end], i + 1))))
    return out


def check_sections(sections):
    found = []
    for key in SECTION_KEYS:
        hits = [
            i
            for i, text, _ in sections
            if normalize_heading(text) == key or (key == "stale-lane" and normalize_heading(text) == "stale lane")
        ]
        if len(hits) != 1:
            return False, "%s headings=%d expected 1" % (key, len(hits))
        found.append((key, hits[0]))
    order = [i for _, i in found]
    if order != sorted(order):
        return False, "heading order %s not canonical" % (order,)
    return True, "headings=%d ordered" % len(found)


def section_body(sections, pattern):
    for _, text, body in sections:
        if pattern.search(text.lower()):
            return body
    return []


def check_shonen_boxes(sections, shonen_text):
    boxes = [l for l in shonen_text.splitlines() if BOX.match(l)]
    if not boxes:
        return False, "SHONEN.md carries no boxes"
    shonen = []
    for _, text, body in sections:
        if re.match(r"^shonen\b", text.strip().lower()):
            shonen.append(body)
    if len(shonen) != 1:
        return False, "## SHONEN sections=%d expected 1" % len(shonen)
    lines = [l for _, l in shonen[0] if BOX.match(l)]
    if len(lines) != len(boxes):
        return False, "box lines=%d expected %d" % (len(lines), len(boxes))
    return True, "box_lines=%d boxes=%d" % (len(lines), len(boxes))


def check_trends(sections):
    body = section_body(sections, re.compile(r"trend verdicts"))
    if not body:
        return False, "no trend verdicts section body"
    seen = {}
    for _, line in body:
        low = line.lower()
        for trend in TRENDS:
            if not re.match(r"^\s*[-*]?\s*\**%s\**\s*[:—-]" % trend, low):
                continue
            verdict = None
            for token in VERDICT_TOKENS:
                if token in low:
                    verdict = token
                    break
            if verdict is None:
                return False, "%s line carries no verdict token" % trend
            if trend in seen:
                return False, "duplicate %s verdict" % trend
            seen[trend] = verdict
    missing = [t for t in TRENDS if t not in seen]
    if missing:
        return False, "missing verdicts: %s" % ",".join(missing)
    return True, "verdicts=%d" % len(seen)


def check_stale_lane(sections, lines):
    for i, text, body in sections:
        if normalize_heading(text) in ("stale-lane", "stale lane"):
            if any(l.strip() for _, l in body):
                return True, "heading_body"
    for line in lines:
        m = re.match(r"^stale[- ]lane\s*[:—-]\s*(\S.*)$", line.strip(), re.I)
        if m:
            return True, "line"
    return False, "no stale-lane line"


def check_measurements(sections):
    body = section_body(sections, re.compile(r"before.*after measurements"))
    rows = []
    for _, line in body:
        if not line.lstrip().startswith("|"):
            continue
        if re.match(r"^\s*\|[\s:\-|]+\|\s*$", line):
            continue
        spans = BACKTICK.findall(line)
        if len(spans) >= 2 and any(COMMIT.match(s.strip()) for s in spans):
            rows.append(line)
    if not rows:
        return False, "no row with a measured commit and a counting command"
    return True, "rows=%d" % len(rows)


def check_claims(sections):
    body = section_body(sections, re.compile(r"work performed"))
    text = "\n".join(l for _, l in body)
    ids = sorted(set(re.findall(r"\bC([1-9])\b", text)))
    if not 1 <= len(ids) <= 3:
        return False, "claim ids=%d expected 1-3" % len(ids)
    return True, "claim_ids=%s" % ",".join("C" + i for i in ids)


def check_evidence(lines):
    pointers = 0
    for line in lines:
        for span in BACKTICK.findall(line):
            fields = span.strip().split()
            if not fields:
                # An empty code span (``) is not an evidence pointer; r36 A1 after a seat
                # produced one and this line raised IndexError instead of a verdict.
                continue
            token = fields[0].strip("()[],;")
            if EVIDENCE.match(token) or re.match(r"^[0-9a-f]{40,64}$", token):
                pointers += 1
    if not pointers:
        return False, "no evidence pointer"
    return True, "pointers=%d" % pointers


def evaluate(report_text, shonen_text):
    lines = mask(report_text.splitlines())
    sections = split_sections(lines)
    results = [
        ("sections", check_sections(sections)),
        ("shonen-boxes", check_shonen_boxes(sections, shonen_text)),
        ("trends", check_trends(sections)),
        ("stale-lane", check_stale_lane(sections, lines)),
        ("measurements", check_measurements(sections)),
        ("claims", check_claims(sections)),
        ("evidence", check_evidence(lines)),
    ]
    return results


def render(results):
    failed = 0
    for name, (ok, detail) in results:
        if not ok:
            failed += 1
        print("check-%s=%s" % (name, "PASS" if ok else "FAIL"))
        if not ok:
            print("detail-%s: %s" % (name, detail), file=sys.stderr)
    print("SUMMARY checks=%d pass=%d fail=%d" % (len(results), len(results) - failed, failed))
    return 1 if failed else 0


SELFTEST_REPORT = """# r-selftest

## Work performed

- C1 landed with `census/round-1/records/x.tsv`.

## Landed changes

- `tools/x.py`.

## Before -> after measurements

| claim | before | after | counting command | measured commit |
|---|---|---|---|---|
| C1 x | `a=1` | `a=0` | `python3 -B tools/x.py --rev <rev>` | `0123456789abcdef0123456789abcdef01234567` |

## Sources & frontier

SOURCES: unchanged — selftest.

## Trend verdicts

- expansion: improved — selftest.
- quality: unchanged — selftest.
- discernment: unprovable-but-better — selftest.

## SHONEN

- [~] box one `census/round-1/records/x.tsv`

## Stale-lane

- respawn-per-round driver; no other mission open.
"""

SELFTEST_SHONEN = """# lane

- [~] box one
"""


def selftest():
    cases = []

    def case(name, report, shonen, expect_fail):
        results = evaluate(report, shonen)
        failed = [n for n, (ok, _) in results if not ok]
        cases.append((name, failed, expect_fail))

    case("conforming", SELFTEST_REPORT, SELFTEST_SHONEN, [])
    case(
        "empty-code-span",
        SELFTEST_REPORT.replace("- C1 landed with `census/round-1/records/x.tsv`.", "- C1 landed with `` and `census/round-1/records/x.tsv`."),
        SELFTEST_SHONEN,
        [],
    )
    case("missing-section", SELFTEST_REPORT.replace("## Landed changes", "## Landed"), SELFTEST_SHONEN, ["sections"])
    case(
        "section-order",
        SELFTEST_REPORT.replace("## Landed changes", "## Landed changes\n\nx\n\n## Work performed", 1),
        SELFTEST_SHONEN,
        ["sections"],
    )
    case(
        "shonen-no-box-line",
        SELFTEST_REPORT.replace("- [~] box one `census/round-1/records/x.tsv`\n", ""),
        SELFTEST_SHONEN,
        ["shonen-boxes"],
    )
    case(
        "trend-missing",
        SELFTEST_REPORT.replace("- discernment: unprovable-but-better — selftest.\n", ""),
        SELFTEST_SHONEN,
        ["trends"],
    )
    case(
        "stale-lane-absent",
        SELFTEST_REPORT.replace("## Stale-lane\n\n- respawn-per-round driver; no other mission open.\n", ""),
        SELFTEST_SHONEN,
        ["sections", "stale-lane"],
    )
    case(
        "no-measured-commit",
        SELFTEST_REPORT.replace("`0123456789abcdef0123456789abcdef01234567`", "`pending`"),
        SELFTEST_SHONEN,
        ["measurements"],
    )
    case(
        "no-evidence-pointer",
        SELFTEST_REPORT.replace("`census/round-1/records/x.tsv`", "`x`").replace(
            "`0123456789abcdef0123456789abcdef01234567`", "`pending`"
        ).replace("`tools/x.py`", "`x`").replace("`python3 -B tools/x.py --rev <rev>`", "`run`").replace(
            "`a=1`", "`1`"
        ).replace("`a=0`", "`0`"),
        SELFTEST_SHONEN,
        ["measurements", "evidence"],
    )
    failed_cases = 0
    for name, observed, expected in cases:
        ok = observed == expected
        print("case-%s=%s observed=%s expected=%s" % (name, "PASS" if ok else "FAIL", observed, expected))
        if not ok:
            failed_cases += 1
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(cases), len(cases) - failed_cases, failed_cases))
    return 1 if failed_cases else 0


def main(argv):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--report")
    ap.add_argument("--shonen")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("-h", "--help", action="store_true")
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        return fail("USAGE", "--report ABS --shonen ABS | --selftest")
    if args.help:
        print(__doc__)
        return 0
    if args.selftest:
        return selftest()
    if not args.report or not args.shonen:
        return fail("USAGE", "--report ABS --shonen ABS | --selftest")
    try:
        report_text = open(args.report, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        return fail("REPORT-UNREADABLE", str(exc))
    try:
        shonen_text = open(args.shonen, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        return fail("SHONEN-UNREADABLE", str(exc))
    return render(evaluate(report_text, shonen_text))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
