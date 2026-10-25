#!/usr/bin/env python3
"""souji-gate-check.py — C2 gate checker (souji round 22, attempt 2).

Implements the FROZEN per-entry predicate and the FROZEN slice predicate of
.ufo/waves/round-22/attempt2/preregistration.txt (C2).  Nothing here may widen
or redefine them; each of the six entry checks fails on its own, and the slice
predicate counts verdict completeness exactly as frozen.

Per-entry checks (frozen, verbatim intent):
  1. the file exists at the lane root and contains a ``## Gate`` heading;
  2. the Gate names >=1 https URL and carries ``opened: YYYY-MM-DD`` equal to
     --round-date;
  3. the Gate carries >=1 located quote in double quotes of <=25 words, with a
     locator token (section sign, section, line, paragraph, or DESCRIPTION);
  4. every quoted span appears verbatim (whitespace-collapsed) in the committed
     snapshot file the Gate names, and that snapshot lives under --snapshot-dir;
  5. every ``source: S<digits>`` id cited in the entry's frontmatter resolves to
     a row in corpus/SOURCES.md;
  6. the Gate records >=1 ADMIT and >=1 REJECT with a reason string each.

Slice predicate (frozen): for every id line in the committed derived slice the
verdicts TSV must carry one row ``<id>\\t<class>\\t<evidence-pointer>`` with class
in present|accepted|unverifiable|refused.  A missing row is a failure and is
counted in NEITHER slice_verdicts NOR fail — it simply cannot raise
slice_verdicts to slice_total.

Counts line (exactly one stdout line in counter mode):
  entries=<N> ok=<K> slice_verdicts=<V> slice_total=<T> fail=<F>
Exit 0 iff ok == entries and V == T and F == 0.

fail (F) counts failed checks: one per (entry, check-id) pair that failed, plus
one per structural slice failure (missing slice/verdicts file, malformed or
duplicate verdict row, slice line without an id).  Diagnostics go to stderr so
the counter command keeps its one-line stdout contract.

Read-only: this tool writes nothing.  The selftest builds its fixtures under
``mktemp -d /var/tmp`` and removes that directory itself.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import sys
import tempfile

# ---------------------------------------------------------------------------
# Frozen constants

MAX_QUOTE_WORDS = 25
CLASSES = frozenset({"present", "accepted", "unverifiable", "refused"})

# The staged package entry the kill rule makes fixture 6 out of, byte-exact.
STAGED_ENTRY = (
    "/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/"
    "quarantine-staging-no-copy-r23.md"
)

GATE_HEADING_RE = re.compile(r"^##\s+Gate\s*$", re.M)
NEXT_H2_RE = re.compile(r"^##\s+\S", re.M)
FRONTMATTER_END_RE = re.compile(r"^#{1,6}\s+\S", re.M)

STRING_RE = re.compile(r'"([^"\n]+)"')
URL_RE = re.compile(r"https://[^\s<>()\[\]]+")
OPENED_RE = re.compile(r"opened:\s*(\d{4}-\d{2}-\d{2})")
SNAPSHOT_RE = re.compile(r"snapshot:\s*(\S+)")
LOCATOR_RE = re.compile(
    r"(?:\u00a7|\bsections?\b|\bparagraphs?\b|\bDESCRIPTION\b|\blines?\b)",
    re.I,
)
SOURCE_ID_RE = re.compile(r"^source:\s*(S\d{3,})", re.M)
REGISTRY_ROW_RE = re.compile(r"^\s*\|\s*(S\d{3,})\s*\|", re.M)
ADMIT_ROW_RE = re.compile(r"^\s*[-*]\s*ADMIT\b")
REJECT_ROW_RE = re.compile(r"^\s*[-*]\s*REJECT\b")
REASON_TOKEN_RE = re.compile(r"(?:reason\s*:|because\b|justification\s*:)", re.I)
SLICE_ID_RE = re.compile(r"\bS\d{3,}\b")
SLICE_ID_FULL_RE = re.compile(r"^S\d{3,}$")

CHECK_IDS = ("check1", "check2", "check3", "check4", "check5", "check6")


# ---------------------------------------------------------------------------
# Helpers


def squash(text: str) -> str:
    """Collapse every whitespace run to one space and trim (frozen rule 4)."""
    return re.sub(r"\s+", " ", text).strip()


def _resolve(root: str, rel: str) -> str:
    return os.path.realpath(rel if os.path.isabs(rel) else os.path.join(root, rel))


def _read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _within(base: str, path: str) -> bool:
    return path == base or path.startswith(base + os.sep)


def _gate_section(text: str):
    """Return the Gate body, or None when the entry has no ``## Gate`` heading."""
    m = GATE_HEADING_RE.search(text)
    if m is None:
        return None
    rest = text[m.end():]
    nxt = NEXT_H2_RE.search(rest)
    return rest if nxt is None else rest[:nxt.start()]


def _frontmatter(text: str) -> str:
    m = FRONTMATTER_END_RE.search(text)
    return text if m is None else text[:m.start()]


def _row_reason(line: str, marker_re: "re.Pattern[str]"):
    """Return the row's reason string, or None when the row carries none.

    The reason string is the text after an explicit ``reason:``/``because``
    clause when one is present, otherwise the attribution that follows the
    last quoted span (the locator and snapshot the row is admitted against).
    """
    m = marker_re.match(line)
    if m is None:
        return None
    tail = line[m.end():]
    token = REASON_TOKEN_RE.search(tail)
    if token is not None:
        reason = tail[token.end():].strip(" \t\u2014-:;,")
        return reason or None
    spans = list(STRING_RE.finditer(tail))
    if spans:
        reason = tail[spans[-1].end():].strip(" \t\u2014-:;,")
        return reason or None
    reason = tail.strip(" \t\u2014-:;,")
    return reason or None


# ---------------------------------------------------------------------------
# Per-entry predicate


def check_entry(root, rel, round_date, snapshot_dir):
    """Return the list of (check-id, detail) failures for one entry."""
    fails = []
    path = _resolve(root, rel)
    if not os.path.isfile(path):
        return [("check1", "entry-missing: %s" % rel)]

    text = _read(path)
    gate = _gate_section(text)
    if gate is None:
        return [("check1", "no-##-Gate-heading: %s" % rel)]

    # check 2 — https URL with the round's opened date, inside the Gate.
    if URL_RE.search(gate) is None:
        fails.append(("check2", "no-https-url-in-gate"))
    dates = OPENED_RE.findall(gate)
    if round_date not in dates:
        fails.append(
            ("check2", "opened-date-mismatch: found=%s want=%s"
             % (dates if dates else "none", round_date))
        )

    # checks 3 and 4 — located short quotes that resolve in the named snapshot.
    snap_root = _resolve(root, snapshot_dir)
    located_short = 0
    seen = set()
    for lineno, line in enumerate(gate.splitlines(), 1):
        spans = STRING_RE.findall(line)
        if line.count('"') % 2:
            fails.append(("check3", "unbalanced-double-quote:gate-line-%d" % lineno))
        if not spans:
            continue
        has_locator = LOCATOR_RE.search(line) is not None
        named = SNAPSHOT_RE.search(line)
        for span in spans:
            quote = squash(span)
            words = len(quote.split())
            if not quote:
                fails.append(("check3", "empty-quoted-span:gate-line-%d" % lineno))
                continue
            if words > MAX_QUOTE_WORDS:
                fails.append(
                    ("check3", "quote-%d-words>%d:gate-line-%d"
                     % (words, MAX_QUOTE_WORDS, lineno))
                )
            elif has_locator:
                located_short += 1
            # rule 4 applies to every quoted span, short or not.
            if named is None:
                detail = "no-snapshot-named:gate-line-%d" % lineno
                if detail not in seen:
                    seen.add(detail)
                    fails.append(("check4", detail))
                continue
            snap_path = _resolve(root, named.group(1))
            if not _within(snap_root, snap_path):
                detail = "snapshot-outside-snapshot-dir:gate-line-%d" % lineno
                if detail not in seen:
                    seen.add(detail)
                    fails.append(("check4", detail))
                continue
            if not os.path.isfile(snap_path):
                detail = "snapshot-missing:gate-line-%d" % lineno
                if detail not in seen:
                    seen.add(detail)
                    fails.append(("check4", detail))
                continue
            if quote not in squash(_read(snap_path)):
                detail = "quote-absent-from-named-snapshot:gate-line-%d" % lineno
                if detail not in seen:
                    seen.add(detail)
                    fails.append(("check4", detail))
    if located_short == 0:
        fails.append(("check3", "no-located-quote-of-<=25-words"))

    # check 5 — every frontmatter source id resolves to a registry row.
    cited = SOURCE_ID_RE.findall(_frontmatter(text))
    known = set()
    registry = _resolve(root, os.path.join("corpus", "SOURCES.md"))
    if os.path.isfile(registry):
        known = set(REGISTRY_ROW_RE.findall(_read(registry)))
    if not cited:
        fails.append(("check5", "no-source-citation-in-frontmatter"))
    for sid in dict.fromkeys(cited):
        if sid not in known:
            fails.append(("check5", "dangling-source: %s" % sid))

    # check 6 — at least one ADMIT and one REJECT, each with a reason string.
    admits = [row for row in gate.splitlines()
              if _row_reason(row, ADMIT_ROW_RE) is not None]
    rejects = [row for row in gate.splitlines()
               if _row_reason(row, REJECT_ROW_RE) is not None]
    if not admits:
        fails.append(("check6", "no-ADMIT-row-with-reason"))
    if not rejects:
        fails.append(("check6", "no-REJECT-row-with-reason"))
    return fails


# ---------------------------------------------------------------------------
# Slice predicate


def check_slice(root, slice_rel, verdicts_rel):
    """Return (slice_verdicts, slice_total, [structural failure details])."""
    fails = []
    sids = []
    slice_path = _resolve(root, slice_rel)
    if not os.path.isfile(slice_path):
        return 0, 0, ["slice-missing: %s" % slice_rel]
    for lineno, line in enumerate(_read(slice_path).splitlines(), 1):
        if not line.strip():
            continue
        m = SLICE_ID_RE.search(line)
        if m is None:
            fails.append("slice-line-without-id:line-%d" % lineno)
            continue
        if m.group(0) not in sids:
            sids.append(m.group(0))

    rows = {}
    verdicts_path = _resolve(root, verdicts_rel)
    if not os.path.isfile(verdicts_path):
        fails.append("verdicts-missing: %s" % verdicts_rel)
    else:
        for lineno, line in enumerate(_read(verdicts_path).splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                fails.append("verdict-short-row:line-%d" % lineno)
                continue
            vid = parts[0].strip()
            cls = parts[1].strip()
            evidence = "\t".join(parts[2:]).strip()
            if not SLICE_ID_FULL_RE.match(vid):
                fails.append("verdict-bad-id:line-%d" % lineno)
                continue
            if cls not in CLASSES:
                fails.append("verdict-bad-class:line-%d" % lineno)
                continue
            if not evidence:
                fails.append("verdict-empty-evidence:line-%d" % lineno)
                continue
            if vid in rows:
                fails.append("verdict-duplicate-row:line-%d" % lineno)
                continue
            rows[vid] = cls
    # A missing verdict row is deliberately NOT appended to fails: the frozen
    # slice predicate counts it in neither slice_verdicts nor fail.
    verified = sum(1 for sid in sids if sid in rows)
    return verified, len(sids), fails


# ---------------------------------------------------------------------------
# Evaluation and counter mode


def evaluate(root, round_date, entries, snapshot_dir, slice_rel, verdicts_rel):
    """Return (counts dict, failed-checks-by-entry, slice failures)."""
    ok = 0
    per_entry = {}
    details = []
    for rel in entries:
        fails = check_entry(root, rel, round_date, snapshot_dir)
        if fails:
            per_entry[rel] = {check for check, _ in fails}
        else:
            ok += 1
        details.extend((rel, check, detail) for check, detail in fails)
    v, t, slice_fails = check_slice(root, slice_rel, verdicts_rel)
    fail_count = sum(len(checks) for checks in per_entry.values()) + len(slice_fails)
    counts = {
        "entries": len(entries),
        "ok": ok,
        "slice_verdicts": v,
        "slice_total": t,
        "fail": fail_count,
    }
    return counts, details, slice_fails


def format_counts(counts) -> str:
    return ("entries=%d ok=%d slice_verdicts=%d slice_total=%d fail=%d"
            % (counts["entries"], counts["ok"], counts["slice_verdicts"],
               counts["slice_total"], counts["fail"]))


def run(root, round_date, entries, snapshot_dir, slice_rel, verdicts_rel,
        out=sys.stdout, err=sys.stderr) -> int:
    counts, details, slice_fails = evaluate(
        root, round_date, entries, snapshot_dir, slice_rel, verdicts_rel)
    for rel, check, detail in details:
        err.write("FAIL %s %s: %s\n" % (check, rel, detail))
    for detail in slice_fails:
        err.write("FAIL slice: %s\n" % detail)
    out.write(format_counts(counts) + "\n")
    exit_ok = (counts["ok"] == counts["entries"]
               and counts["slice_verdicts"] == counts["slice_total"]
               and counts["fail"] == 0)
    return 0 if exit_ok else 1


# ---------------------------------------------------------------------------
# Selftest — the seven frozen fixtures of the C2 kill rule


GOOD_QUOTE = ("RENAME_NOREPLACE Don't overwrite newpath of the rename. "
              "Return an error if newpath already exists.")
LONG_QUOTE = ("alpha bravo charlie delta echo foxtrot golf hotel india juliet "
              "kilo lima mike november oscar papa quebec romeo sierra tango "
              "uniform victor whiskey xray yankee zulu")
ABSENT_QUOTE = "RENAME_NOREPLACE requires support from the underlying filesystem."
SNAP_REL = "census/sources/man.txt"


def _write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def _entry(gate_body, sources="source: S109 \u2014 example\nsource: S110 \u2014 example\n"):
    return sources + "verified-at: 2026-10-25\n\n# fixture entry\n\n" + gate_body + "\n"


def _gate(quote, opened="2026-10-25", snap=SNAP_REL, reject=True):
    rows = [
        "## Gate",
        "",
        "url: https://man7.org/linux/man-pages/man2/rename.2.html",
        "snapshot: %s" % snap,
        "opened: %s" % opened,
        "",
        '- ADMIT: "%s" \u2014 \u00a7 DESCRIPTION flags \u2014 snapshot: %s'
        % (quote, snap),
    ]
    if reject:
        rows.append(
            "- REJECT: staged row S999 (duplicate ground) \u2014 reason: the "
            "row adds no new field or refusal semantics; flip: a new measurement."
        )
    return "\n".join(rows)


def selftest(staged_entry=STAGED_ENTRY, out=sys.stdout) -> int:
    base = tempfile.mkdtemp(prefix="souji-gate-check-", dir="/var/tmp")
    fixtures = []
    try:
        # hermetic root: registry, snapshot, slice, verdicts
        _write(base, "corpus/SOURCES.md",
               "| id | source |\n|---|---|\n"
               "| S109 | fixture row |\n| S110 | fixture row |\n")
        _write(base, SNAP_REL,
               "RENAME_NOREPLACE Don't overwrite newpath of the rename. Return an\n"
               "error if newpath already exists.\n\n"
               + LONG_QUOTE + "\n")
        _write(base, "census/slice", " S109   `payload-absent`\n S110   `payload-absent`\n")
        _write(base, "census/verdicts.tsv",
               "S109\tpresent\tfixture row and payload bytes\n"
               "S110\trefused\tcitation-class defect with a flip\n")
        _write(base, "census/verdicts-partial.tsv",
               "S109\tpresent\tfixture row and payload bytes\n")

        fixtures = [
            ("fixture-1-no-round-date", {"check2"},
             _entry(_gate(GOOD_QUOTE, opened="2026-10-24"))),
            ("fixture-2-quote-26-words", {"check3"},
             _entry(_gate(LONG_QUOTE))),
            ("fixture-3-quote-absent-from-snapshot", {"check4"},
             _entry(_gate(ABSENT_QUOTE))),
            ("fixture-4-dangling-source-id", {"check5"},
             _entry(_gate(GOOD_QUOTE), sources="source: S999 \u2014 missing row\n")),
            ("fixture-5-no-reject-row", {"check6"},
             _entry(_gate(GOOD_QUOTE, reject=False))),
            ("fixture-7-good-entry", set(),
             _entry(_gate(GOOD_QUOTE))),
        ]
        for name, _, body in fixtures:
            _write(base, "entries/%s.md" % name, body)

        # fixture 6: a byte-exact copy of the staged package entry (no Gate).
        staged_ok = os.path.isfile(staged_entry)
        staged_sha = None
        copy_sha = None
        copy_rel = "entries/fixture-6-staged-copy.md"
        if staged_ok:
            with open(staged_entry, "rb") as fh:
                raw = fh.read()
            staged_sha = hashlib.sha256(raw).hexdigest()
            copy_path = os.path.join(base, copy_rel)
            with open(copy_path, "wb") as fh:
                fh.write(raw)
            with open(copy_path, "rb") as fh:
                copy_sha = hashlib.sha256(fh.read()).hexdigest()

        def score(rel, verdicts="census/verdicts.tsv"):
            counts, details, slice_fails = evaluate(
                base, "2026-10-25", [rel], "census/sources",
                "census/slice", verdicts)
            failed = {check for _, check, _ in details}
            return counts, failed, details, slice_fails

        results = []
        for name, expected, _ in fixtures:
            counts, failed, details, slice_fails = score("entries/%s.md" % name)
            ok = (failed == expected and not slice_fails
                  and counts["ok"] == (1 if not expected else 0)
                  and counts["fail"] == len(expected))
            results.append((name, ok, format_counts(counts),
                            "expected-fail=" + (",".join(sorted(expected)) or "none")
                            + " got-fail=" + (",".join(sorted(failed)) or "none")))

        # fixture 6 — the FALSE-GREEN fixture.
        if not staged_ok:
            results.append(("fixture-6-staged-entry-copy", False,
                            "entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1",
                            "staged-entry-missing=" + staged_entry))
            control = "FALSE-GREEN-UNMEASURED"
        else:
            counts, failed, details, slice_fails = score(copy_rel)
            byte_exact = staged_sha == copy_sha
            ok = (byte_exact and failed == {"check1"} and not slice_fails
                  and counts["ok"] == 0 and counts["fail"] == 1)
            results.append(("fixture-6-staged-entry-copy", ok, format_counts(counts),
                            "sha256=" + str(copy_sha)[:16] + " byte-exact=%s" % byte_exact
                            + " got-fail=" + (",".join(sorted(failed)) or "none")))
            control = ("FALSE-GREEN-REJECTED" if ok
                       else "FALSE-GREEN-ACCEPTED (fixture 6 did not fail on check1)")

        # harness: slice predicate counts a missing verdict row in neither V nor F.
        counts, failed, details, slice_fails = score("entries/fixture-7-good-entry.md",
                                                     "census/verdicts-partial.tsv")
        slice_ok = (counts["slice_verdicts"] == 1 and counts["slice_total"] == 2
                    and counts["fail"] == 0 and failed == set() and not slice_fails)
    finally:
        shutil.rmtree(base, ignore_errors=True)

    for name, ok, line, note in results:
        out.write("%s %s [%s] %s\n" % ("PASS" if ok else "FAIL", name, line, note))
    passed = sum(1 for _, ok, _, _ in results if ok)
    out.write("selftest=%d/%d\n" % (passed, len(results)))
    out.write("%s slice-missing-row-not-counted-in-V-or-F [%s]\n"
              % ("PASS" if slice_ok else "FAIL", format_counts(counts)))
    out.write("control=%s\n" % control)
    return 0 if passed == len(results) and slice_ok and control == "FALSE-GREEN-REJECTED" else 1


# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="assimilation gate checker (souji round 22 attempt 2, C2)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--round-date")
    ap.add_argument("--entries", nargs="+")
    ap.add_argument("--snapshot-dir", default="census/round-22/attempt2/sources")
    ap.add_argument("--slice", dest="slice_rel",
                    default="census/round-22/attempt2/quarantine-slice")
    ap.add_argument("--slice-verdicts", dest="verdicts_rel",
                    default="census/round-22/attempt2/slice-verdicts.tsv")
    ap.add_argument("--staged-entry", default=STAGED_ENTRY,
                    help="byte-exact source for selftest fixture 6")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest(args.staged_entry)
    if not args.round_date or not args.entries:
        ap.error("--round-date and --entries are required unless --selftest")
    return run(args.root, args.round_date, args.entries, args.snapshot_dir,
               args.slice_rel, args.verdicts_rel)


if __name__ == "__main__":
    sys.exit(main())
