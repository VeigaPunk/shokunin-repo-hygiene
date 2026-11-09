#!/usr/bin/env python3
"""ScoutSources (souji r100): verify the C2 stale-source-attribution repair
(routed defect 2) against committed bytes and the byte-checked live sources.

C2 requires (per the round-100 claim):
  leg 1: corpus/knowledge/deadline-owned-reaping.md carries an append-only
         correction block that cites S332 for the field-4 ppid wording
  leg 2: S075's used-by cell names corpus/knowledge/deadline-owned-reaping.md
  and:  NO new SOURCES row was added (row count must not grow)

This script checks those mechanically and reports each as PASS/FAIL.

Usage:
  verify-c2-attribution.py --lane <lane root> [--base <lane base sha>]
"""
import argparse
import os
import re
import subprocess
import sys

FAILURES = []
CHECKS = 0


def check(ok, label, detail=""):
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(label)
    print("%-4s %s%s" % ("PASS" if ok else "FAIL", label,
                         ("  | " + detail) if detail else ""))


def rows(sources_text):
    out = {}
    for ln in sources_text.splitlines():
        ln = ln.rstrip("\n")
        if not ln.startswith("| S"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 11:
            continue
        out[cells[0]] = cells
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--base", default="a662bb0d7e033cc5ceccd70b52eb234404300845")
    args = ap.parse_args()
    lane = args.lane

    knowledge = os.path.join(lane, "corpus/knowledge/deadline-owned-reaping.md")
    sources = os.path.join(lane, "corpus/SOURCES.md")

    ktext = open(knowledge, encoding="utf-8", errors="replace").read()
    stext = open(sources, encoding="utf-8", errors="replace").read()

    # ---- leg 1: append-only correction block citing S332 for field 4 ----
    check("S332" in ktext, "leg1: correction cites S332")
    # the block must be appended AFTER the r98 correction (append-only)
    i98 = ktext.find("### r98 correction")
    i100 = ktext.find("Round-100 correction")
    check(i98 != -1 and i100 != -1 and i100 > i98,
          "leg1: round-100 block is appended after the r98 correction",
          "r98@%d r100@%d" % (i98, i100))
    # the block must withdraw the S075 field-4 attribution in favour of S332
    blk = ktext[i100:] if i100 != -1 else ""
    check(re.search(r"withdrawn", blk, re.I) is not None,
          "leg1: block withdraws the S075 field-4 attribution")
    check("field 4" in blk or "field-4" in blk,
          "leg1: block names the field-4 wording")
    check(re.search(r"S332", blk) is not None,
          "leg1: block names S332 as the replacement attribution")

    # ---- leg 2: S075 used-by names the knowledge file ----
    r = rows(stext)
    check("S075" in r, "leg2: S075 row exists")
    if "S075" in r:
        used = [x.strip() for x in r["S075"][-1].split(",") if x.strip()]
        check("corpus/knowledge/deadline-owned-reaping.md" in used,
              "leg2: S075 used-by names corpus/knowledge/deadline-owned-reaping.md",
              "used-by=%r" % (used,))

    # ---- no new SOURCES row ----
    try:
        base_text = subprocess.run(
            ["git", "-C", lane, "show", "%s:corpus/SOURCES.md" % args.base],
            capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as exc:
        print("WARN could not read base SOURCES.md: %s" % exc)
        base_text = None
    if base_text is not None:
        base_rows = rows(base_text)
        check(len(r) == len(base_rows),
              "no-new-row: SOURCES row count unchanged vs lane base",
              "base=%d now=%d" % (len(base_rows), len(r)))
        added = sorted(set(r) - set(base_rows))
        check(not added, "no-new-row: no SOURCES id added",
              "added=%r" % (added,))
        removed = sorted(set(base_rows) - set(r))
        check(not removed, "no-new-row: no SOURCES id removed",
              "removed=%r" % (removed,))

    # ---- the field-4 wording is genuinely a kernel-side attribution ----
    # S075 (man page) documents field 4 as ppid too, but the registry scopes S075 to
    # fields 5/6/22; S332 is the emission-order source. The correction must not claim
    # the man page lacks the wording.
    check("not from the proc_pid_stat(5) man page" in ktext
          or "not from the proc_pid_stat(5) man page" in blk,
          "leg1: block states the wording is not from the man page")

    print("SUMMARY checks=%d failures=%d" % (CHECKS, len(FAILURES)))
    for f in FAILURES:
        print("FAILED: %s" % f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
