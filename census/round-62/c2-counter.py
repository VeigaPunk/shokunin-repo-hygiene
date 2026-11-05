#!/usr/bin/env python3
"""c2-counter.py - round-62 C2 (calibration): live self-assessment statements about index flags.

  python3 -B census/round-62/c2-counter.py --root LANE --rev FULL40

Reads the COMMITTED bytes of each frozen file at --rev (git show REV:PATH; the worktree is never read),
collapses whitespace, then counts:

  stale_open  occurrences of  "routed to round 62" | "routed to r62" | "Neither is implemented in round 61"
              (a live statement that still describes the index-flag refusal as open or routed)
  landed      occurrences of  "RECEIPT-INDEX-FLAG-CONCEALED" (a live statement that names the refusal
              the writer now emits; deleting the stale sentences cannot satisfy this)

Frozen predicate: stale_open == 0 AND landed >= 3 (one live statement in each frozen file that names the class).
Prints one line per file, then `SUMMARY files=4 stale_open=<n> landed=<n> verdict=PASS|FAIL`, then `EXIT=<rc>`.
Exit 0 iff PASS; 1 on FAIL; 2 on could-not-evaluate (bad rev, unreadable file).
Python stdlib only; writes nothing.
"""
import argparse
import re
import subprocess
import sys

FILES = [
    "SKILL.md",
    "corpus/README.md",
    "corpus/knowledge/skip-worktree-concealment.md",
    "PROVINCE.md",
]
STALE = [
    re.compile(r"routed to round 62"),
    re.compile(r"routed to r62"),
    re.compile(r"Neither is implemented in round 61"),
]
LANDED = re.compile(r"RECEIPT-INDEX-FLAG-CONCEALED")
FULL40 = re.compile(r"^[0-9a-f]{40}$")


def die(msg):
    sys.stderr.write("COULD-NOT-EVALUATE: %s\n" % msg)
    sys.exit(2)


def blob(root, rev, path):
    r = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)], capture_output=True)
    if r.returncode != 0:
        die("cannot read %s at %s: %s" % (path, rev, r.stderr.decode("utf-8", "replace").strip()))
    return r.stdout.decode("utf-8", "replace")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ns = ap.parse_args(argv)
    if not FULL40.match(ns.rev):
        die("rev is not full 40-hex: %s" % ns.rev)
    chk = subprocess.run(["git", "-C", ns.root, "cat-file", "-t", ns.rev], capture_output=True, text=True)
    if chk.returncode != 0 or chk.stdout.strip() != "commit":
        die("rev is not a commit object: %s" % ns.rev)
    tot_stale = tot_landed = 0
    for path in FILES:
        text = re.sub(r"\s+", " ", blob(ns.root, ns.rev, path))
        stale = sum(len(p.findall(text)) for p in STALE)
        landed = len(LANDED.findall(text))
        tot_stale += stale
        tot_landed += landed
        print("FILE %s stale_open=%d landed=%d" % (path, stale, landed))
    ok = tot_stale == 0 and tot_landed >= 3
    print("SUMMARY files=%d stale_open=%d landed=%d verdict=%s" % (
        len(FILES), tot_stale, tot_landed, "PASS" if ok else "FAIL"))
    print("EXIT=%d" % (0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
