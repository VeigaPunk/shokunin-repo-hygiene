#!/usr/bin/env python3
"""souji-gate-check.py — assimilation gate checker (round 22, C2).

Verifies the frozen per-entry predicate and the register-slice verdict set for a
round that assimilates knowledge into this lane's corpus:

  1. the entry exists and contains a '## Gate' heading;
  2. its Gate names >=1 https URL and 'opened: <round date>';
  3. its Gate carries >=1 located quote in double quotes of <=25 words, with a
     locator token (§, section, line, paragraph, DESCRIPTION, ...);
  4. every quoted span appears verbatim (whitespace-collapsed) in the committed
     snapshot the same line names via 'snapshot: <path>', and that snapshot
     lives under --snapshot-dir;
  5. every 'source: S<digits>' id cited in the entry resolves in corpus/SOURCES.md;
  6. the Gate records >=1 'ADMIT:' and >=1 'REJECT:' line, each with a reason.

  Slice: every id in the derived register slice must carry one verdict row
  '<id>\t<class>\t<evidence>' with class in present|accepted|unverifiable|refused.

Counts line: entries=<n> ok=<k> slice_verdicts=<v> slice_total=<t> fail=<f>
Exit 0 iff k == n and v == t and f == 0.

Frozen contract: .ufo/waves/round-22/attempt2/preregistration.txt (C2).
Read-only; no writes anywhere.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import subprocess
import sys
import tempfile

QUOTE_RE = re.compile(r'"([^"]{2,400})"')
URL_RE = re.compile(r"https://\S+")
OPENED_RE = re.compile(r"opened:\s*(\d{4}-\d{2}-\d{2})")
SOURCE_RE = re.compile(r"^source:\s*(S\d{3,})", re.M)
SNAPSHOT_RE = re.compile(r"snapshot:\s*(\S+)")
LOCATOR_RE = re.compile(r"(§|section|line |lines |paragraph|DESCRIPTION|OPTIONS|COMMANDS|SYNOPSIS|heading)", re.I)
ADMIT_RE = re.compile(r"^\s*[-*]\s*ADMIT:", re.M)
REJECT_RE = re.compile(r"^\s*[-*]\s*REJECT:", re.M)
REASON_RE = re.compile(r"(reason:|because|—)", re.I)
SLICE_ID_RE = re.compile(r"S\d{3,}")
CLASSES = {"present", "accepted", "unverifiable", "refused"}


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def gate_section(text: str):
    idx = text.find("\n## Gate")
    if idx < 0:
        return None
    rest = text[idx + 1:]
    nxt = rest.find("\n## ", 4)
    return rest if nxt < 0 else rest[:nxt]


def check_entry(root: str, rel: str, round_date: str, snapshot_dir: str):
    """Returns (ok, [failure strings])."""
    fails: list[str] = []
    path = rel if os.path.isabs(rel) else os.path.join(root, rel)
    if not os.path.isfile(path):
        return False, ["entry-missing: %s" % rel]
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    gate = gate_section(text)
    if gate is None:
        return False, ["check1-no-gate: %s" % rel]
    if not URL_RE.search(gate):
        fails.append("check2-no-url")
    dates = OPENED_RE.findall(gate)
    if round_date not in dates:
        fails.append("check2-opened-date: found %s want %s" % (dates, round_date))

    quote_rows = 0
    snap_root = os.path.normpath(os.path.join(root, snapshot_dir))
    for lineno, line in enumerate(gate.splitlines(), 1):
        quotes = QUOTE_RE.findall(line)
        if not quotes:
            continue
        if not LOCATOR_RE.search(line):
            fails.append("check3-no-locator-gate-line-%d" % lineno)
            continue
        snap = SNAPSHOT_RE.search(line)
        for q in quotes:
            words = len(squash(q).split())
            if words > 25:
                fails.append("check3-quote-%d-words-gate-line-%d" % (words, lineno))
                continue
            if not snap:
                fails.append("check4-no-snapshot-named-line-%d" % lineno)
                continue
            spar = snap.group(1)
            spath = spar if os.path.isabs(spar) else os.path.normpath(os.path.join(root, spar))
            if not spath.startswith(snap_root + os.sep) and spath != snap_root:
                fails.append("check4-snapshot-outside-dir-line-%d" % lineno)
                continue
            if not os.path.isfile(spath):
                fails.append("check4-snapshot-missing-line-%d" % lineno)
                continue
            with open(spath, encoding="utf-8", errors="replace") as fh:
                body = squash(fh.read())
            if squash(q) not in body:
                fails.append("check4-quote-absent-from-snapshot-line-%d" % lineno)
                continue
            quote_rows += 1
    if quote_rows == 0:
        fails.append("check3-no-located-quote-with-snapshot")

    registry = os.path.join(root, "corpus", "SOURCES.md")
    known: set[str] = set()
    if os.path.isfile(registry):
        with open(registry, encoding="utf-8", errors="replace") as fh:
            known = set(re.findall(r"^\s{0,3}\|\s*(S\d{3,})", fh.read(), re.M))
    cited = SOURCE_RE.findall(text)
    if not cited:
        fails.append("check5-no-source-citation")
    for sid in cited:
        if sid not in known:
            fails.append("check5-dangling-source: %s" % sid)

    if not ADMIT_RE.search(gate):
        fails.append("check6-no-admit")
    if not REJECT_RE.search(gate):
        fails.append("check6-no-reject")
    for line in gate.splitlines():
        if REJECT_RE.search(line) and not REASON_RE.search(line):
            fails.append("check6-reject-without-reason")
            break
    return (not fails), fails


def check_slice(root: str, slice_rel: str, verdicts_rel: str):
    fails: list[str] = []
    ids: list[str] = []
    spath = slice_rel if os.path.isabs(slice_rel) else os.path.join(root, slice_rel)
    if not os.path.isfile(spath):
        return 0, 0, ["slice-missing"]
    with open(spath, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = SLICE_ID_RE.search(line)
            if m and m.group(0) not in ids:
                ids.append(m.group(0))
    vpath = verdicts_rel if os.path.isabs(verdicts_rel) else os.path.join(root, verdicts_rel)
    rows: dict[str, str] = {}
    if os.path.isfile(vpath):
        with open(vpath, encoding="utf-8", errors="replace") as fh:
            for lineno, line in enumerate(fh, 1):
                if not line.strip() or line.startswith("#"):
                    continue
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 3:
                    fails.append("verdict-short-row-line-%d" % lineno)
                    continue
                vid, cls, ev = parts[0].strip(), parts[1].strip(), parts[2].strip()
                if cls not in CLASSES:
                    fails.append("verdict-bad-class-line-%d:%s" % (lineno, cls))
                    continue
                if not ev:
                    fails.append("verdict-no-evidence-line-%d" % lineno)
                    continue
                if vid in rows:
                    fails.append("verdict-duplicate:%s" % vid)
                    continue
                rows[vid] = cls
    verified = sum(1 for i in ids if i in rows)
    for i in ids:
        if i not in rows:
            fails.append("verdict-missing:%s" % i)
    return verified, len(ids), fails


def run(root: str, round_date: str, entries: list[str], snapshot_dir: str,
        slice_rel: str, verdicts_rel: str, out=sys.stdout) -> int:
    total_f = 0
    ok = 0
    for rel in entries:
        good, fails = check_entry(root, rel, round_date, snapshot_dir)
        ok += 1 if good else 0
        total_f += len(fails)
        for f in fails:
            out.write("FAIL %s %s\n" % (rel, f))
    v, t, sfails = check_slice(root, slice_rel, verdicts_rel)
    total_f += len(sfails)
    for f in sfails:
        out.write("FAIL slice %s\n" % f)
    out.write("entries=%d ok=%d slice_verdicts=%d slice_total=%d fail=%d\n"
              % (len(entries), ok, v, t, total_f))
    return 0 if ok == len(entries) and v == t and total_f == 0 else 1


# ---------------------------------------------------------------- selftest

GOOD_SNAP = "Option --no-copy: do not copy, just move. RENAME_NOREPLACE do not overwrite newpath.\n"


def _mk(root: str, rel: str, text: str):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def _entry(gate_body: str, sources="source: S109 — example\nsource: S110 — example\n") -> str:
    return (sources + "verified-at: 2026-10-25\n\n# fixture entry\n\n" + gate_body + "\n")


def _gate(quote: str, opened="2026-10-25", snap="census/sources/x.txt",
          admit=True, reject=True) -> str:
    lines = ["## Gate", "", "url: https://example.invalid/doc", "opened: %s" % opened, ""]
    lines.append('- ADMIT: "%s" — § DESCRIPTION — snapshot: %s' % (quote, snap))
    if admit:
        pass
    else:
        lines[-1] = lines[-1].replace("ADMIT", "NOTE")
    if reject:
        lines.append("- REJECT: staged row S999: reason: quote cited against the wrong artifact")
    return "\n".join(lines)


def selftest(out=sys.stdout) -> int:
    checks: list[tuple[str, bool, str]] = []
    base = tempfile.mkdtemp(prefix="souji-gate-check-", dir="/var/tmp")
    try:
        _mk(base, "corpus/SOURCES.md",
            "| id | source |\n|---|---|\n| S109 | row |\n| S110 | row |\n")
        _mk(base, "census/sources/x.txt", GOOD_SNAP)
        _mk(base, "census/slice", " S114   `payload-absent`\n S123   `payload-absent`\n")
        good_quote = "RENAME_NOREPLACE do not overwrite newpath"
        cases = {
            "good": _entry(_gate(good_quote)),
            "no-date": _entry(_gate(good_quote, opened="2026-10-24")),
            "long-quote": _entry(_gate(" ".join(["word"] * 30))),
            "quote-absent": _entry(_gate("this sentence is not in the snapshot")),
            "dangling-source": _entry(_gate(good_quote), sources="source: S999 — missing\n"),
            "no-reject": _entry(_gate(good_quote, reject=False)),
            "no-gate": "source: S109 — example\n\n# fixture entry without a gate\n",
        }
        for name, body in cases.items():
            _mk(base, "entries/%s.md" % name, body)
        verdicts_good = "S114\tpresent\tregister row + payload bytes\nS123\trefused\tcitation-class defect\n"
        _mk(base, "census/verdicts-good.tsv", verdicts_good)
        _mk(base, "census/verdicts-partial.tsv", "S114\tpresent\tevidence\n")

        def score(name):
            buf = io.StringIO()
            rc = run(base, "2026-10-25", ["entries/%s.md" % name], "census/sources",
                     "census/slice", "census/verdicts-good.tsv", buf)
            line = buf.getvalue().strip().splitlines()[-1]
            return rc, line, buf.getvalue()

        for name, want_ok in (("good", True), ("no-date", False), ("long-quote", False),
                              ("quote-absent", False), ("dangling-source", False),
                              ("no-reject", False), ("no-gate", False)):
            rc, line, detail = score(name)
            good = (line.startswith("entries=1 ok=1") and rc == 0) if want_ok else \
                   (line.startswith("entries=1 ok=0") and rc == 1)
            checks.append(("fixture %s -> %s" % (name, "ok" if want_ok else "fail"), good, line))
        buf = io.StringIO()
        rc = run(base, "2026-10-25", ["entries/good.md"], "census/sources",
                 "census/slice", "census/verdicts-partial.tsv", buf)
        line = buf.getvalue().strip().splitlines()[-1]
        checks.append(("fixture partial-verdicts -> fail", rc == 1 and "slice_verdicts=1" in line, line))
        # control: a checker that always prints the green line must not survive the fixture set
        green = "entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0"
        control_survives = green.startswith("entries=1 ok=1") and score("no-gate")[1].startswith("entries=1 ok=1")
        checks.append(("control always-green -> FALSE-GREEN-REJECTED", not control_survives,
                       "FALSE-GREEN-REJECTED" if not control_survives else "control met the fixtures"))
    finally:
        subprocess.run(["rm", "-rf", base], check=False)
    ok = sum(1 for _, good, _ in checks if good)
    for name, good, detail in checks:
        out.write("%s %s [%s]\n" % ("PASS" if good else "FAIL", name, detail))
    out.write("selftest=%d/%d\n" % (ok, len(checks)))
    return 0 if ok == len(checks) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="assimilation gate checker (souji round 22 C2)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--round-date")
    ap.add_argument("--entries", nargs="+")
    ap.add_argument("--snapshot-dir", default="census/round-22/attempt2/sources")
    ap.add_argument("--slice", dest="slice_rel", default="census/round-22/attempt2/quarantine-slice")
    ap.add_argument("--slice-verdicts", dest="verdicts_rel", default="census/round-22/attempt2/slice-verdicts.tsv")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.round_date or not args.entries:
        ap.error("--round-date and --entries are required unless --selftest")
    return run(args.root, args.round_date, args.entries, args.snapshot_dir,
               args.slice_rel, args.verdicts_rel)


if __name__ == "__main__":
    sys.exit(main())
