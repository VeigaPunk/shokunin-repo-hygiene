#!/usr/bin/env python
"""census/round-51/c1-counter.py — r51 C1 (calibration): the r50-closure routed
record-accuracy corrections land append-only.

Claim (r50 non-author closure routed items 1 and 3). The r50 closure found:
(1) corpus/lessons/round-50.md's ## Gate carries the "Reject sample (stated
explicitly, r48-closure carry-in practice)..." bullet TWICE, verbatim identical,
consecutively — the routed fix is an appended correction line naming the
duplicated text, never an in-place edit; (3) census/round-50/records/
ntfs-exclusion-check-tip.txt omits the quoted_d_rows=6 line the base receipt
carries (count=6 and the six quoted paths are present at both ends) — a cosmetic
receipt-field addition. This counter reads, at the round content tip (exit 0):

  SUMMARY corr=ok dup=ok ntfs=ok listing=ok
          corr_lines=<n> dup_base=<n> dup_tip=<n>

with corr_lines=1, dup_base=2, dup_tip=2 — and reads PRISTINE FAIL
CORRECTION-ABSENT (exit 1) at the round base, where neither correction exists
(the do-nothing control census/round-51/controls/c1-control-donothing.txt).
The SAME counter bytes measure both ends; the world (the lane's committed
bytes) moves, not the instrument (the r45 different-instrument limit).

Legs over the lane's committed bytes at --rev (git object store only; the
pinned base revision is read via --base-rev):
  corr     corpus/lessons/round-50.md at --rev: exactly one line matching
           ^R51-CORRECTION; the line names the duplicated bullet ("Reject
           sample") and states the fix is appended (contains "append" or
           "duplicate")
  dup      the bullet prefix "Reject sample (stated explicitly, r48-closure
           carry-in practice): this" occurs exactly twice at --rev AND exactly
           twice at --base-rev — the duplicated bytes are preserved verbatim;
           an in-place edit or deletion of either bullet fails this leg
  ntfs     census/round-50/records/ntfs-exclusion-check-tip.txt at --rev:
           exactly one ^quoted_d_rows=6 line
  listing  the six quoted-path lines and the count=6 line of that receipt at
           --rev are byte-identical (order included) to the same lines of the
           receipt at --base-rev — the listing was not touched, only the
           missing field appended
CLI:
  python -B census/round-51/c1-counter.py --root LANE --rev FULL40 --base-rev FULL40 --scratch DIR
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate. All reads go through
git cat-file against --root's object store; --scratch only holds diagnostics.
Nothing is written inside the repo. Python stdlib only. Disclosed limits: the
counter counts committed bytes only (it cannot prove who appended the line);
the standing landing-suite receipt is NOT a leg here — it is the separate
r46-counter receipt at the final tip bound by the preregistration (the r50
disclosed ordering: that run belongs after the terminal repair).
"""
import argparse
import os
import re
import subprocess
import sys

REV = re.compile(r"^[0-9a-f]{40}$")
LESSON = "corpus/lessons/round-50.md"
NTFS_TIP = "census/round-50/records/ntfs-exclusion-check-tip.txt"
BULLET_PREFIX = "Reject sample (stated explicitly, r48-closure carry-in practice): this"
CORR_RE = re.compile(r"^R51-CORRECTION.*$", re.M)
QDR_RE = re.compile(r"^quoted_d_rows=(\d+)\s*$", re.M)
QUOTED_RE = re.compile(r"^'\".*\"'$", re.M)
COUNT_RE = re.compile(r"^count=(\d+)\s*$", re.M)


def git_blob(root, rev, path):
    args = ["git", "-C", root, "cat-file", "blob", "%s:%s" % (rev, path)]
    p = subprocess.run(args, capture_output=True,
                       env={"PATH": os.environ.get("PATH", ""),
                            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
                            "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0",
                            "GIT_CONFIG_NOSYSTEM": "1",
                            "GIT_CONFIG_GLOBAL": os.devnull,
                            "GIT_CONFIG_SYSTEM": os.devnull})
    if p.returncode != 0:
        return None, p.returncode
    # CRLF->LF normalized at read time: the r50 sibling receipts are CRLF on
    # this host, and a line-anchored regex that assumes LF would silently
    # vacuate the quoted-path legs (the r51 pre-freeze receipt review caught
    # exactly that shape; both compared sides are normalized identically).
    return p.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n"), 0


def listing_lines(text):
    """The quoted-path lines plus the count line, as a tuple of strings."""
    quoted = QUOTED_RE.findall(text)
    count = COUNT_RE.findall(text)
    return tuple(quoted), (count[-1] if count else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base-rev", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    if not REV.match(a.rev) or not REV.match(a.base_rev):
        print("PRISTINE FAIL BAD-ARG rev/base-rev must be full 40-hex")
        return 2

    legs = {}
    details = {}

    lesson_tip, rc = git_blob(a.root, a.rev, LESSON)
    lesson_base, rc2 = git_blob(a.root, a.base_rev, LESSON)
    if lesson_tip is None or lesson_base is None:
        print("PRISTINE FAIL LESSON-ABSENT at %s (rc=%s,%s)" % (a.rev, rc, rc2))
        return 1
    corr_lines = CORR_RE.findall(lesson_tip)
    corr_ok = (len(corr_lines) == 1
               and "Reject sample" in corr_lines[0]
               and ("append" in corr_lines[0].lower() or "duplicate" in corr_lines[0].lower()))
    legs["corr"] = corr_ok
    details["corr_lines"] = len(corr_lines)

    dup_tip = lesson_tip.count(BULLET_PREFIX)
    dup_base = lesson_base.count(BULLET_PREFIX)
    legs["dup"] = (dup_tip == 2 and dup_base == 2)
    details["dup_tip"] = dup_tip
    details["dup_base"] = dup_base

    ntfs_tip, rc = git_blob(a.root, a.rev, NTFS_TIP)
    ntfs_base, rc2 = git_blob(a.root, a.base_rev, NTFS_TIP)
    if ntfs_tip is None or ntfs_base is None:
        print("PRISTINE FAIL NTFS-RECEIPT-ABSENT at %s (rc=%s,%s)" % (a.rev, rc, rc2))
        return 1
    qd = QDR_RE.findall(ntfs_tip)
    legs["ntfs"] = (len(qd) == 1 and qd[0] == "6")

    q_tip, c_tip = listing_lines(ntfs_tip)
    q_base, c_base = listing_lines(ntfs_base)
    legs["listing"] = (q_tip == q_base and c_tip == c_base == "6")

    ok = all(legs.values())
    print("SUMMARY corr=%s dup=%s ntfs=%s listing=%s corr_lines=%d dup_base=%d dup_tip=%d"
          % ("ok" if legs["corr"] else "FAIL", "ok" if legs["dup"] else "FAIL",
             "ok" if legs["ntfs"] else "FAIL", "ok" if legs["listing"] else "FAIL",
             details["corr_lines"], details["dup_base"], details["dup_tip"]))
    for name, value in sorted(legs.items()):
        if not value:
            print("LEG-FAIL %s" % name)
    with open(os.path.join(a.scratch, "c1-last-run.txt"), "w", encoding="utf-8") as fh:
        fh.write("rev=%s base=%s ok=%s\n" % (a.rev, a.base_rev, ok))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
