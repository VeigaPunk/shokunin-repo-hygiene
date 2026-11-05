#!/usr/bin/env python3
"""c3-counter.py — souji round-63 C3 counter: statement/writer agreement, both directions.

Reads, at one full 40-hex revision, committed bytes only: the frozen statement population
(census/round-63/c3-statements.tsv, read from the working tree; its digest is pinned by the
preregistration) and the receipt-writer blob. Each governed statement has exactly one LIVE
wording per revision. The counter resolves which frozen wording is present, takes that
wording's claim token, and checks it against the enforcement markers in the writer blob:

  markers (byte needles in tools/souji-receipt-write.py):
    flag     RECEIPT-INDEX-FLAG-CONCEALED        (r62 start-of-run refusal)
    inrun    RECEIPT-STATE-CHANGED-DURING-RUN    (r63 in-run refusal)
    unmerged RECEIPT-INDEX-UNMERGED              (r63 distinct class)
    gitlink  RECEIPT-GITLINK-CONCEALED           (r63 distinct class)
    absent   RECEIPT-INDEX-CONCEALED-ABSENT      (r63 distinct class)

  claim tokens, requirement (markers that must be present) / forbidden (must be absent):
    inrun_open           forbidden: inrun     (wording says the in-run gap is open)
    inrun_landed         required:  inrun     (wording says the in-run refusal landed)
    closed_full          required:  inrun, flag (wording claims full closure)
    closed_scoped_start  required:  flag      (wording scopes closure to start-of-run form)
    classes_single       forbidden: unmerged, gitlink, absent
    classes_landed       required:  unmerged, gitlink, absent

Findings (each one line, `FINDING <KIND> <id>: <detail>`):
  GOVERNED-STATEMENT-UNRESOLVED  neither frozen wording present (deleting a statement cannot pass)
  DUPLICATE-LIVE-WORDING         both frozen wordings present (a stale copy left beside the new one)
  SCOPE-OVERREACH                wording claims a marker the writer bytes lack
  SCOPE-STALE-OPEN               wording claims a gap the writer bytes have closed
  CLAIM-TOKEN-INVALID            unknown claim token in the population
  FILE-ABSENT                    governed file missing at the revision

Named limit: this is text-and-marker agreement, not semantic truth beyond the markers. The
frozen population is the only statement set counted; LOG.md and corpus/lessons are append-only
history and are never in the population.

CLI:
  python3 -B census/round-63/c3-counter.py --root LANE --rev FULL40 [--tsv PATH]
  python3 -B census/round-63/c3-counter.py --selftest
Exit: 0 findings=0 (PASS); 1 findings>0 (FAIL); 2 usage/environment error.
The selftest keeps no scratch; it is pure in-memory.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

WRITER_REL = "tools/souji-receipt-write.py"

MARKERS = {
    "flag": b"RECEIPT-INDEX-FLAG-CONCEALED",
    "inrun": b"RECEIPT-STATE-CHANGED-DURING-RUN",
    "unmerged": b"RECEIPT-INDEX-UNMERGED",
    "gitlink": b"RECEIPT-GITLINK-CONCEALED",
    "absent": b"RECEIPT-INDEX-CONCEALED-ABSENT",
}

REQUIRED = {
    "inrun_open": (),
    "inrun_landed": ("inrun",),
    "closed_full": ("inrun", "flag"),
    "closed_scoped_start": ("flag",),
    "classes_single": (),
    "classes_landed": ("unmerged", "gitlink", "absent"),
}

FORBIDDEN = {
    "inrun_open": ("inrun",),
    "classes_single": ("unmerged", "gitlink", "absent"),
}

COLUMNS = ["id", "file", "base_pattern", "base_claim", "after_pattern", "after_claim", "note"]
REV_RE = re.compile(r"^[0-9a-f]{40}$")


def git_show(root: str, rev: str, rel: str) -> bytes:
    r = subprocess.run(["git", "-C", root, "show", f"{rev}:{rel}"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev}:{rel} failed rc={r.returncode}: "
                           f"{r.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return r.stdout


def check_claim(claim: str, markers: dict) -> list[tuple[str, str]]:
    """Return (kind, detail) pairs for one claim token against the marker map."""
    out: list[tuple[str, str]] = []
    if claim not in REQUIRED:
        return [("CLAIM-TOKEN-INVALID", claim)]
    for name in REQUIRED[claim]:
        if not markers.get(name):
            out.append(("SCOPE-OVERREACH", f"claim {claim} needs marker {name}, writer lacks it"))
    for name in FORBIDDEN.get(claim, ()):
        if markers.get(name):
            out.append(("SCOPE-STALE-OPEN", f"claim {claim} forbids marker {name}, writer carries it"))
    return out


def evaluate(rows: list[dict], blobs: dict, markers: dict) -> list[dict]:
    """Pure evaluator. rows: dicts with COLUMNS keys. blobs: relpath -> bytes (None = absent).
    markers: marker name -> bool. Returns a list of finding dicts {id, kind, detail}."""
    findings: list[dict] = []
    for row in rows:
        rid = row["id"]
        blob = blobs.get(row["file"])
        if blob is None:
            findings.append({"id": rid, "kind": "FILE-ABSENT", "detail": row["file"]})
            continue
        base_hit = row["base_pattern"].encode("utf-8") in blob
        after_hit = row["after_pattern"].encode("utf-8") in blob
        if base_hit and after_hit:
            findings.append({"id": rid, "kind": "DUPLICATE-LIVE-WORDING",
                             "detail": "both frozen wordings present; a stale copy remains"})
            continue
        if not base_hit and not after_hit:
            findings.append({"id": rid, "kind": "GOVERNED-STATEMENT-UNRESOLVED",
                             "detail": "neither frozen wording present at this revision"})
            continue
        wording, claim = ("base", row["base_claim"]) if base_hit else ("after", row["after_claim"])
        for kind, detail in check_claim(claim, markers):
            findings.append({"id": rid, "kind": kind, "detail": f"{wording} wording: {detail}"})
    return findings


def load_tsv_text(text: str) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    lines = text.splitlines()
    if not lines:
        raise RuntimeError("tsv is empty")
    header = lines[0].split("\t")
    if header != COLUMNS:
        raise RuntimeError(f"tsv header {header!r} != {COLUMNS!r}")
    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != len(COLUMNS):
            raise RuntimeError(f"tsv line {lineno}: {len(cells)} cells, want {len(COLUMNS)}")
        row = dict(zip(COLUMNS, cells))
        if row["id"] in seen:
            raise RuntimeError(f"tsv line {lineno}: duplicate statement id {row['id']}")
        seen.add(row["id"])
        rows.append(row)
    if not rows:
        raise RuntimeError("tsv holds no statements")
    return rows


def run(root: str, rev: str, tsv_rel: str, tsv_rev: str) -> int:
    if not REV_RE.match(rev):
        print(f"C3-COUNTER-FATAL: rev is not full 40-hex ({rev})", file=sys.stderr)
        print("EXIT=2")
        return 2
    try:
        rows = load_tsv_text(git_show(root, tsv_rev, tsv_rel).decode("utf-8"))
        blobs: dict = {WRITER_REL: git_show(root, rev, WRITER_REL)}
        for row in rows:
            rel = row["file"]
            if rel not in blobs:
                try:
                    blobs[rel] = git_show(root, rev, rel)
                except RuntimeError:
                    blobs[rel] = None
    except (RuntimeError, OSError) as exc:
        print(f"C3-COUNTER-FATAL: {exc}", file=sys.stderr)
        print("EXIT=2")
        return 2
    writer = blobs[WRITER_REL]
    markers = {name: (needle in writer) for name, needle in MARKERS.items()}
    findings = evaluate(rows, blobs, markers)
    for f in findings:
        print(f"FINDING {f['kind']} {f['id']}: {f['detail']}")
    marker_bits = "".join(f"{n}={int(v)}" for n, v in markers.items())
    print(f"SUMMARY statements={len(rows)} {marker_bits} findings={len(findings)} "
          f"verdict={'PASS' if not findings else 'FAIL'} rev={rev}")
    rc = 0 if not findings else 1
    print(f"EXIT={rc}")
    return rc


def selftest() -> int:
    """Pure in-memory cases through evaluate(). Expected finding counts are fixed in advance.
    The always-zero stub (a counter that reports nothing) must be rejected: its output would
    equal the honest-pass result on every case, so at least one non-pass case must exist."""
    writer_full = (b"x " + MARKERS["flag"] + b" " + MARKERS["inrun"] + b" " + MARKERS["unmerged"]
                   + b" " + MARKERS["gitlink"] + b" " + MARKERS["absent"] + b" y\n")
    writer_r62 = b"x " + MARKERS["flag"] + b" y\n"
    scope = [{"id": "t1", "file": "f.md", "base_pattern": "gap is open", "base_claim": "inrun_open",
              "after_pattern": "refusal landed", "after_claim": "inrun_landed", "note": ""}]
    overreach = [{"id": "t2", "file": "f.md", "base_pattern": "closed everywhere",
                  "base_claim": "closed_full", "after_pattern": "scoped to start",
                  "after_claim": "closed_scoped_start", "note": ""}]
    cases = [
        ("honest-after-wording-with-marker", scope, {"f.md": b"the refusal landed\n"}, writer_full, 0),
        ("overreach-base-closed-full-without-inrun", overreach, {"f.md": b"closed everywhere (r62)\n"},
         writer_r62, 1),
        ("kind-only-after-wording-without-marker", scope, {"f.md": b"the refusal landed\n"}, writer_r62, 1),
        ("deleted-governed-statement", scope, {"f.md": b"unrelated text\n"}, writer_full, 1),
        ("stale-open-base-wording-with-marker", scope, {"f.md": b"the gap is open\n"}, writer_full, 1),
        ("duplicate-live-wordings", scope, {"f.md": b"the gap is open; the refusal landed\n"}, writer_full, 1),
        ("classes-landed-without-markers", [{"id": "t5", "file": "f.md", "base_pattern": "one class",
                                             "base_claim": "classes_single", "after_pattern": "three classes",
                                             "after_claim": "classes_landed", "note": ""}],
         {"f.md": b"three classes\n"}, writer_r62, 3),
    ]
    got_counts = []
    ok = True
    for name, crows, cblobs, cwriter, want in cases:
        markers = {n: (needle in cwriter) for n, needle in MARKERS.items()}
        got = len(evaluate(crows, cblobs, markers))
        got_counts.append(got)
        good = got == want
        ok = ok and good
        print(f"SELFTEST-CASE {name}: findings={got} want={want} {'pass' if good else 'MISMATCH'}")
    stub_zero = all(c == 0 for c in got_counts[1:])
    print(f"SELFTEST control=STUB-ALWAYS-ZERO {'ACCEPTED-FALSE-GREEN' if stub_zero else 'REJECTED'}")
    ok = ok and not stub_zero
    print(f"SELFTEST pass cases={len(cases)} fail={0 if ok else 1}")
    print(f"EXIT={0 if ok else 1}")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="souji round-63 C3 statement/writer agreement counter")
    ap.add_argument("--root", help="lane root")
    ap.add_argument("--rev", help="full 40-hex revision to read")
    ap.add_argument("--tsv", default="census/round-63/c3-statements.tsv",
                    help="frozen population, a repo-relative path")
    ap.add_argument("--tsv-rev", help="revision holding the frozen population (default: --rev); "
                    "the do-nothing control reads the population from the freeze commit")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args(argv)
    if ns.selftest:
        if ns.root or ns.rev:
            print("C3-COUNTER-FATAL: --selftest takes no --root/--rev", file=sys.stderr)
            return 2
        return selftest()
    if not ns.root or not ns.rev:
        print("C3-COUNTER-FATAL: --root and --rev are required without --selftest", file=sys.stderr)
        return 2
    return run(ns.root, ns.rev, ns.tsv, ns.tsv_rev or ns.rev)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
