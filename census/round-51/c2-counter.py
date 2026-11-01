#!/usr/bin/env python
"""census/round-51/c2-counter.py — r51 C2 (coverage): the session-workspace live
census refresh with per-artifact receipts and a derivable r46->r51 drift receipt.

Claim. The r46 workspace dry-run census (census/round-46/workspace-census.tsv) is
re-taken against the LIVE 2026-11-01 session workspace (the round contract's
census surface), with per-artifact receipts for the named candidates (the
standing stale-candidate helpers-r74 and the new-since-r46 foreign scratch root
scratch-r80v) and a drift receipt whose every number re-derives from the two
committed captures. Dry-run: nothing moved, nothing deleted, no removal
proposed; every receipt verdict is advisory (certification OFF).

This counter reads, at the round content tip (exit 0):

  SUMMARY shape=ok drift=ok receipts=ok limit=ok rows=<n> added=<n> removed=<n>

and reads PRISTINE FAIL WORKSPACE-CENSUS-ABSENT (exit 1) at the round base,
where none of the r51 blobs exist (the do-nothing control
census/round-51/controls/c2-control-donothing.txt). The SAME counter bytes
measure both ends; the world (committed bytes) moves, not the instrument.

Legs (committed bytes at --rev; the r46 capture is read at --base-rev):
  shape     census/round-51/workspace-census.tsv at --rev: every row is
            4-field; counts in-use/pushed=14 and in-use/no-origin-master=3
            with exactly the r46 no-origin-master names (kotodama-shokunin,
            shokunin-binary-forensics, shokunin-reverse-engineering); the
            fleet hygiene-surface row reads lane-clones=17
  drift     census/round-51/records/ws-drift-vs-r46.tsv at --rev: every COUNT
            line's two integers re-derive from the two TSVs (active-foreign-
            scratch rows; in-use/pushed rows; in-use/no-origin-master rows;
            top-level-surface additions; lane-clone surface count), and the
            ADDED/REMOVED key rows equal the comm of the two TSVs'
            (surface,classification) keys (header row excluded)
  receipts  census/round-51/records/per-artifact-receipts.tsv at --rev: exactly
            2 VERDICT rows, both NOT-SAFE, the target paths ending
            /helpers-r74 and /scratch-r80v, and the receipt's `# tool sha256:`
            digest equals the blob sha256 of tools/souji-verify.sh at --rev
  limit     census/round-51/workspace-census.txt at --rev names the
            pushed-receipt copied-history limit ("git-cherry" and "S274"
            present), and corpus/SOURCES.md at --rev carries the | S274 | row
            whose source cell names git-cherry (the sourced claim's ground,
            opened live this round)
CLI:
  python -B census/round-51/c2-counter.py --root LANE --rev FULL40 --base-rev FULL40 --scratch DIR
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate. All reads via git
cat-file against --root's object store; --scratch holds diagnostics only;
nothing written inside the repo. Python stdlib only. Disclosed limits: the
counter re-derives committed bytes only — it cannot re-run the live workspace
(a census row is a point-in-time fact); age_hours values are not re-derived
(clock-dependent, disclosed in the method note).
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

REV = re.compile(r"^[0-9a-f]{40}$")
TSV51 = "census/round-51/workspace-census.tsv"
TSV46 = "census/round-46/workspace-census.tsv"
DRIFT = "census/round-51/records/ws-drift-vs-r46.tsv"
RECEIPTS = "census/round-51/records/per-artifact-receipts.tsv"
METHOD = "census/round-51/workspace-census.txt"
SOURCES = "corpus/SOURCES.md"
VERIFY_TOOL = "tools/souji-verify.sh"
NO_ORIGIN = {"kotodama-shokunin", "shokunin-binary-forensics",
             "shokunin-reverse-engineering"}
COUNT_RE = re.compile(r"^COUNT (\S+) (-?\d+) -> (-?\d+)\s*(?:\(.*)?$", re.M)
VERDICT_RE = re.compile(r"^VERDICT\t(.+)\t(NOT-SAFE|SAFE)\t(.+)\t(.*)$", re.M)
TOOLSHA_RE = re.compile(r"^# tool sha256: ([0-9a-f]{64})\s*$", re.M)


def git_blob(root, rev, path, want_bytes=False):
    args = ["git", "-C", root, "cat-file", "blob", "%s:%s" % (rev, path)]
    p = subprocess.run(args, capture_output=True,
                       env={"PATH": os.environ.get("PATH", ""),
                            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
                            "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0",
                            "GIT_CONFIG_NOSYSTEM": "1",
                            "GIT_CONFIG_GLOBAL": os.devnull,
                            "GIT_CONFIG_SYSTEM": os.devnull})
    if p.returncode != 0:
        return (None, p.returncode) if not want_bytes else (None, p.returncode)
    if want_bytes:
        return p.stdout, 0
    # CRLF->LF normalized at read time (the r50 sibling receipts are CRLF on
    # this host; both compared sides normalize identically).
    return p.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n"), 0


def parse_tsv(text):
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        f = line.split("\t")
        if len(f) != 4:
            return None
        rows.append(f)
    return rows


def keys(rows):
    """(surface, classification) keys, header rows excluded (a TSV format
    artifact must never read as workspace drift — the r51 feasibility leg
    caught the header-as-REMOVED-row defect pre-freeze)."""
    return set((r[0], r[2]) for r in rows
               if not (r[0] == "surface" and r[2] == "classification"))


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

    tsv51_b, rc = git_blob(a.root, a.rev, TSV51)
    if tsv51_b is None:
        print("PRISTINE FAIL WORKSPACE-CENSUS-ABSENT %s:%s (rc=%d)" % (a.rev, TSV51, rc))
        return 1
    tsv46_b, rc = git_blob(a.root, a.base_rev, TSV46)
    drift_b, rc = git_blob(a.root, a.rev, DRIFT)
    receipts_b, rc = git_blob(a.root, a.rev, RECEIPTS)
    method_b, rc = git_blob(a.root, a.rev, METHOD)
    sources_b, rc = git_blob(a.root, a.rev, SOURCES)
    tool_raw, rc = git_blob(a.root, a.rev, VERIFY_TOOL, want_bytes=True)
    tool_b = tool_raw.decode("utf-8", errors="replace") if tool_raw is not None else None
    for name, blob in (("drift", drift_b), ("receipts", receipts_b),
                       ("method", method_b), ("sources", sources_b),
                       ("tool", tool_b)):
        if blob is None:
            print("PRISTINE FAIL BLOB-ABSENT %s at %s (rc=%d)" % (name, a.rev, rc))
            return 1
    if tsv46_b is None:
        print("PRISTINE FAIL R46-CAPTURE-ABSENT at base (rc=%d)" % rc)
        return 1

    rows51 = parse_tsv(tsv51_b)
    rows46 = parse_tsv(tsv46_b)
    if rows51 is None or rows46 is None:
        print("PRISTINE FAIL TSV-MALFORMED (non-4-field row)")
        return 2

    legs = {}

    # shape
    pushed = [r for r in rows51 if r[2] == "in-use/pushed"]
    noorigin = [r for r in rows51 if r[2] == "in-use/no-origin-master"]
    hygiene = [r for r in rows51 if r[2] == "hygiene-surface"]
    shape_ok = (len(pushed) == 14 and len(noorigin) == 3
                and set(r[0].rsplit("/", 1)[-1] for r in noorigin) == NO_ORIGIN
                and len(hygiene) == 1 and hygiene[0][3] == "lane-clones=17")
    legs["shape"] = shape_ok

    # drift
    drift_ok = True
    derived = {
        "active-foreign-scratch": (
            sum(1 for r in rows46 if r[2] == "active-foreign-scratch"),
            sum(1 for r in rows51 if r[2] == "active-foreign-scratch")),
        "in-use/pushed": (len([r for r in rows46 if r[2] == "in-use/pushed"]),
                          len(pushed)),
        "in-use/no-origin-master": (
            len([r for r in rows46 if r[2] == "in-use/no-origin-master"]),
            len(noorigin)),
        "new-top-level-candidates": (
            0, 0),  # replaced below by the key-set derivation
        "lane-clone-surfaces": (
            len([r for r in rows46 if r[1] == "git-repo"]),
            len([r for r in rows51 if r[1] == "git-repo"])),
    }
    top46 = set(r[0] for r in rows46 if "/" not in r[0]
                and not (r[0] == "surface" and r[2] == "classification"))
    top51_cls = dict((r[0], r[2]) for r in rows51 if "/" not in r[0]
                     and not (r[0] == "surface" and r[2] == "classification"))
    top51 = set(top51_cls)
    derived["new-top-level-candidates"] = (
        0, len([s for s in top51 - top46
                if top51_cls.get(s, "").endswith("-NEW")]))
    counts = {m.group(1): (int(m.group(2)), int(m.group(3)))
              for m in COUNT_RE.finditer(drift_b)}
    if counts != derived:
        drift_ok = False
        print("DRIFT-COUNT-MISMATCH declared=%s derived=%s" % (sorted(counts.items()), sorted(derived.items())))
    k46, k51 = keys(rows46), keys(rows51)
    expect_added = sorted(k51 - k46)
    expect_removed = sorted(k46 - k51)
    got_added, got_removed = [], []
    for line in drift_b.splitlines():
        f = line.split("\t")
        if f and f[0] == "ADDED" and len(f) == 3:
            got_added.append((f[1], f[2]))
        elif f and f[0] == "REMOVED" and len(f) == 3:
            got_removed.append((f[1], f[2]))
    if sorted(got_added) != expect_added or sorted(got_removed) != expect_removed:
        drift_ok = False
        print("DRIFT-KEYS-MISMATCH added got=%d want=%d removed got=%d want=%d"
              % (len(got_added), len(expect_added), len(got_removed), len(expect_removed)))
    legs["drift"] = drift_ok
    n_added, n_removed = len(got_added), len(got_removed)

    # receipts
    vr = VERDICT_RE.findall(receipts_b)
    toolsha = TOOLSHA_RE.search(receipts_b)
    tool_blob_sha = hashlib.sha256(tool_raw).hexdigest() if tool_raw is not None else ""
    def endswith_target(path, suffix):
        p = path.replace("\\", "/").rstrip("/")
        return p == suffix or p.endswith("/" + suffix)
    receipts_ok = (len(vr) == 2
                   and all(v[1] == "NOT-SAFE" for v in vr)
                   and any(endswith_target(v[0], "helpers-r74") for v in vr)
                   and any(endswith_target(v[0], "scratch-r80v") for v in vr)
                   and toolsha is not None and toolsha.group(1) == tool_blob_sha)
    legs["receipts"] = receipts_ok

    # limit
    limit_ok = ("git-cherry" in method_b and "S274" in method_b
                and any(line.startswith("| S274 |") and "git-cherry" in line
                        for line in sources_b.splitlines()))
    legs["limit"] = limit_ok

    ok = all(legs.values())
    print("SUMMARY shape=%s drift=%s receipts=%s limit=%s rows=%d added=%d removed=%d"
          % ("ok" if legs["shape"] else "FAIL", "ok" if legs["drift"] else "FAIL",
             "ok" if legs["receipts"] else "FAIL", "ok" if legs["limit"] else "FAIL",
             len(rows51), n_added, n_removed))
    for name, value in sorted(legs.items()):
        if not value:
            print("LEG-FAIL %s" % name)
    with open(os.path.join(a.scratch, "c2-last-run.txt"), "w", encoding="utf-8") as fh:
        fh.write("rev=%s base=%s ok=%s\n" % (a.rev, a.base_rev, ok))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
