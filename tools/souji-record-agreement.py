#!/usr/bin/env python3
"""souji-record-agreement.py — record-agreement instrument (round 23, C1).

Answers one question over committed bytes: does this lane's self-assessment agree with the
receipts the lane committed, and does the lane still carry un-authored round work?

Four frozen keys (the round-23 preregistration is the contract; the key set is code, not data):

  K1 after-receipt binding (spot-check D2). Every `assertions=/resolved=/skipped=/mismatches=`
     4-tuple on an `r22`/`round-22` line of SCORECARD.md that names the receipt's `rev=` value
     must equal the receipt's counts line, and at least one such bound occurrence must exist.
     A tuple on an r22 line that names some other revision is outside K1 (the r22 row quotes
     both ends of its own measurement). The receipt must exist in the tree at --rev.
  K2 superseded-number correction (spot-check D5, extended pre-data to tallies). Inside LOG.md's
     `Round22 attempt2` section, every 4-tuple or `<n> <class>` tally that disagrees with its
     receipt must be named by a LATER LOG.md line that also carries `superseded by`; deleting the
     filed historical occurrence is itself a mismatch (filed bytes are append-only).
  K3 slice tally (spot-check D4). Every `<n> <class>` occurrence in corpus/README.md and
     corpus/lessons/round-22.md must equal the tally derived from
     census/round-22/attempt2/slice-verdicts.tsv, and the record set must carry >=1 occurrence of
     each class.
  K4 uncommitted round work (spot-check D1). Each `git status --porcelain` path in the working
     tree that no row of census/round-23/records/uncommitted-exemptions.tsv names is one
     mismatch (a dedicated file: corpus/pointer-exemptions.tsv is parsed by the landing gate,
     which refuses a row shape it does not know).

Counts line: keys=<K> records=<R> occurrences=<O> mismatches=<M>
Mismatch rows: MISMATCH<TAB><key><TAB><record><TAB><class><TAB><detail>
Exit 0 iff M == 0.  Read-only: git plumbing (`show`, `rev-parse`) plus one
working-tree `status` query. No checkout, no fetch, no writes inside the repo.

Frozen contract: .ufo/waves/round-23/preregistration.txt (C1).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

K1_RECEIPT = "census/round-23/records/declared-evidence-after.tsv"
K1_RECORDS = ("SCORECARD.md",)
K1_SCOPE = re.compile(r"(?i)\br22\b|round-22")

K2_RECORD = "LOG.md"
K2_SECTION_START = re.compile(r"^Round22 attempt2")
K2_SECTION_END = re.compile(r"^=====")
K2_RECEIPT = "census/round-22/attempt2/declared-evidence-before-final.tsv"
K2_CORRECTION_MARKER = "superseded by"

K3_RECEIPT = "census/round-22/attempt2/slice-verdicts.tsv"
K3_RECORDS = ("corpus/README.md", "corpus/lessons/round-22.md")
K3_CLASSES = ("accepted", "present", "unverifiable", "refused")

K4_EXEMPT_FILE = "census/round-23/records/uncommitted-exemptions.tsv"
K4_ALLOWED = frozenset({"census/operator-sweep-20261019/"})
REV_TOKEN_RE = re.compile(r"\b[0-9a-f]{40}\b")
K2_FILED = ("assertions=56 resolved=53 skipped=33 mismatches=3", "1 present", "1 refused")

COUNTS_RE = re.compile(r"assertions=(\d+) resolved=(\d+) skipped=(\d+) mismatches=(\d+)")
TALLY_RE = re.compile(r"(\d+)\s+\*{0,2}(accepted|present|unverifiable|refused)\*{0,2}")
REV_LINE_RE = re.compile(r"^rev=([0-9a-f]{40})$", re.M)


def paragraphs(lines: list[str], offset: int) -> list[tuple[int, str]]:
    """Group physical lines into blank-line-separated paragraphs.

    A wrapped counter tuple is one logical occurrence; the paragraph's first physical line is
    the location reported.
    """
    out: list[tuple[int, str]] = []
    buf: list[str] = []
    start = 0
    for i, line in enumerate(lines):
        if line.strip():
            if not buf:
                start = i
            buf.append(line.strip())
        elif buf:
            out.append((offset + start, " ".join(buf)))
            buf = []
    if buf:
        out.append((offset + start, " ".join(buf)))
    return out


def git(root: str, *args: str, check: bool = False) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "core.fsmonitor"
    env["GIT_CONFIG_VALUE_0"] = "false"
    cmd = ["git", "-C", root, "-c", "maintenance.auto=false", *args]
    return subprocess.run(cmd, capture_output=True, text=True, env=env, check=check)


def read_at(root: str, rev: str, path: str) -> str | None:
    proc = git(root, "show", f"{rev}:{path}")
    if proc.returncode != 0:
        return None
    return proc.stdout


def counts_of(text: str) -> tuple[str, str] | None:
    """Return (4-tuple string, rev header) from a receipt's bytes."""
    m = COUNTS_RE.search(text)
    if not m:
        return None
    rm = REV_LINE_RE.search(text)
    return m.group(0), (rm.group(1) if rm else "")


def tally_of(text: str) -> dict[str, int]:
    tally = {c: 0 for c in K3_CLASSES}
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        cells = line.split("\t")
        if len(cells) >= 2 and cells[1].strip() in tally:
            tally[cells[1].strip()] += 1
    return tally


class Report:
    def __init__(self, root: str, rev: str, worktree: bool):
        self.root = root
        self.rev = rev
        self.worktree = worktree
        self.rows: list[tuple[str, str, str, str]] = []
        self.keys = 4
        self.records: set[str] = set()
        self.occurrences = 0

    def bad(self, key: str, record: str, cls: str, detail: str) -> None:
        self.rows.append((key, record, cls, detail))

    # ---- K1 -------------------------------------------------------------
    def k1(self) -> None:
        text = read_at(self.root, self.rev, K1_RECEIPT)
        if text is None:
            self.bad("K1", K1_RECEIPT, "receipt-absent", f"not in tree at {self.rev}")
            return
        parsed = counts_of(text)
        if parsed is None:
            self.bad("K1", K1_RECEIPT, "receipt-malformed", "no counts line")
            return
        value, rev = parsed
        if not rev:
            # a receipt cannot name the commit that contains it: its rev is the revision it
            # MEASURED, and the record must name that same revision (checked per line below)
            self.bad("K1", K1_RECEIPT, "receipt-rev-absent", "no rev= header")
        for record in K1_RECORDS:
            body = read_at(self.root, self.rev, record)
            if body is None:
                self.bad("K1", record, "record-absent", f"not in tree at {self.rev}")
                continue
            seen = 0
            for lineno, line in enumerate(body.splitlines(), 1):
                if not K1_SCOPE.search(line):
                    continue
                for m in COUNTS_RE.finditer(line):
                    # a tuple belongs to the nearest revision token before it on the same line:
                    # the r22 row quotes both ends of its own measurement on one physical line
                    before = REV_TOKEN_RE.findall(line[: m.start()])
                    bound = before[-1] if before else ""
                    if bound == rev:
                        seen += 1
                        self.occurrences += 1
                        if m.group(0) != value:
                            self.bad("K1", f"{record}:{lineno}", "value-disagree",
                                     f"{m.group(0)} != receipt {value} at {rev}")
                    elif m.group(0) == value and bound != rev:
                        # the after-value quoted against some other revision: D2's own shape
                        self.occurrences += 1
                        self.bad("K1", f"{record}:{lineno}", "rev-disagree",
                                 f"after-value bound to {bound or 'no revision'}, not {rev}")
            if seen == 0:
                self.bad("K1", record, "occurrence-absent",
                         f"no r22 counts tuple bound to the receipt rev {rev}")
        self.records.add(K1_RECORDS[0])

    # ---- K2 -------------------------------------------------------------
    def k2(self) -> dict[str, int]:
        counts_text = read_at(self.root, self.rev, K2_RECEIPT)
        tally_text = read_at(self.root, self.rev, K3_RECEIPT)
        if counts_text is None:
            self.bad("K2", K2_RECEIPT, "receipt-absent", f"not in tree at {self.rev}")
        if tally_text is None:
            self.bad("K2", K3_RECEIPT, "receipt-absent", f"not in tree at {self.rev}")
        parsed = counts_of(counts_text or "")
        if parsed is None:
            self.bad("K2", K2_RECEIPT, "receipt-malformed", "no counts line")
        want_counts = parsed[0] if parsed else ""
        want_tally = tally_of(tally_text or "")

        body = read_at(self.root, self.rev, K2_RECORD)
        self.records.add(K2_RECORD)
        if body is None:
            self.bad("K2", K2_RECORD, "record-absent", f"not in tree at {self.rev}")
            return want_tally
        lines = body.splitlines()
        start = None
        for i, line in enumerate(lines):
            if K2_SECTION_START.match(line):
                start = i
                break
        if start is None:
            self.bad("K2", K2_RECORD, "section-absent", "no 'Round22 attempt2' section")
            return want_tally
        # the header is followed by its own `=====` underline; the section ends at the NEXT one
        body_start = start + 1
        if body_start < len(lines) and K2_SECTION_END.match(lines[body_start]):
            body_start += 1
        end = len(lines)
        for j in range(body_start, len(lines)):
            if K2_SECTION_END.match(lines[j]):
                end = j
                break
        found = 0
        paras = paragraphs(lines[body_start:end], body_start)
        for start_line, text in paras:
            stale: list[str] = []
            for m in COUNTS_RE.finditer(text):
                found += 1
                self.occurrences += 1
                if want_counts and m.group(0) != want_counts:
                    stale.append(m.group(0))
            for m in TALLY_RE.finditer(text):
                found += 1
                self.occurrences += 1
                n, cls = int(m.group(1)), m.group(2)
                if n != want_tally.get(cls, 0):
                    stale.append(m.group(0))
            for occ in stale:
                # a correction may be anywhere later in the file, on one line or wrapped
                later = any(
                    K2_CORRECTION_MARKER in " ".join(lines[k:min(k + 6, len(lines))])
                    and occ in " ".join(lines[k:min(k + 6, len(lines))])
                    for k in range(start_line, len(lines))
                )
                if not later:
                    self.bad("K2", f"{K2_RECORD}:{start_line + 1}", "uncorrected",
                             f"{occ!r} has no later '{K2_CORRECTION_MARKER}' line")
        section_text = " ".join(lines[body_start:end])
        for expected in K2_FILED:
            if expected not in section_text:
                self.bad("K2", K2_RECORD, "filed-occurrence-missing",
                         f"{expected!r} is gone; filed bytes are append-only")
        if found == 0:
            self.bad("K2", K2_RECORD, "filed-occurrence-missing",
                     "the section holds no superseded scalar")
        return want_tally

    # ---- K3 -------------------------------------------------------------
    def k3(self, want_tally: dict[str, int]) -> None:
        for record in K3_RECORDS:
            present: set[str] = set()
            body = read_at(self.root, self.rev, record)
            self.records.add(record)
            if body is None:
                self.bad("K3", record, "record-absent", f"not in tree at {self.rev}")
                continue
            for lineno, line in enumerate(body.splitlines(), 1):
                for m in TALLY_RE.finditer(line):
                    n, cls = int(m.group(1)), m.group(2)
                    self.occurrences += 1
                    present.add(cls)
                    if n != want_tally.get(cls, 0):
                        self.bad("K3", f"{record}:{lineno}", "tally-disagree",
                                 f"{n} {cls} != receipt {want_tally.get(cls, 0)} {cls}")
            missing = sorted(set(K3_CLASSES) - present)
            if missing:
                self.bad("K3", record, "class-absent", "no occurrence of " + ",".join(missing))

    # ---- K4 -------------------------------------------------------------
    def k4(self) -> None:
        if not self.worktree:
            return
        exempt: list[str] = []
        body = read_at(self.root, self.rev, K4_EXEMPT_FILE)
        for line in (body or "").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            path = line.split("\t")[0].strip()
            if not path:
                continue
            if path not in K4_ALLOWED:
                self.bad("K4", path, "exemption-not-allowed",
                         "not a frozen operator-owned path")
                continue
            exempt.append(path)
        proc = git(self.root, "status", "--porcelain")
        if proc.returncode != 0:
            self.bad("K4", ".", "status-failed", proc.stderr.strip())
            return
        for line in proc.stdout.splitlines():
            path = line[3:].strip() if len(line) > 3 else ""
            if not path:
                continue
            if any(path == e or path.startswith(e if e.endswith("/") else e + "/") for e in exempt):
                continue
            self.bad("K4", path, "uncommitted-path", line[:2].strip() or "??")

    def emit(self, as_json: str | None) -> int:
        for key, record, cls, detail in self.rows:
            print(f"MISMATCH\t{key}\t{record}\t{cls}\t{detail}")
        line = (f"keys={self.keys} records={len(self.records)} "
                f"occurrences={self.occurrences} mismatches={len(self.rows)}")
        print(line)
        if as_json:
            with open(as_json, "w", encoding="utf-8") as fh:
                json.dump({"rev": self.rev, "line": line,
                           "mismatches": [{"key": k, "record": r, "class": c, "detail": d}
                                          for k, r, c, d in self.rows]}, fh, indent=1)
        return 0 if not self.rows else 1


def resolve_rev(root: str, rev: str | None) -> str:
    if rev:
        if not re.fullmatch(r"[0-9a-f]{40}", rev):
            sys.exit("record-agreement: --rev must be a full 40-hex commit id")
        return rev
    for ref in ("refs/heads/master", "refs/heads/main", "HEAD"):
        proc = git(root, "rev-parse", "--verify", ref)
        if proc.returncode == 0:
            return proc.stdout.strip()
    sys.exit("record-agreement: cannot resolve a revision")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="souji record-agreement instrument (C1)")
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--rev", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--no-worktree", action="store_true",
                    help="skip K4 (working-tree query)")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)
    rev = resolve_rev(root, args.rev)
    rep = Report(root, rev, not args.no_worktree)
    rep.k1()
    tally = rep.k2()
    rep.k3(tally)
    rep.k4()
    return rep.emit(args.json)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
