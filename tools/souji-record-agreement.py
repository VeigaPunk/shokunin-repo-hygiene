#!/usr/bin/env python3
"""souji-record-agreement.py — record-agreement instrument (round 23, C1).

Answers one question over committed bytes: does this lane's self-assessment agree with the
receipts the lane committed, and does the lane still carry un-authored round work?

Four frozen keys (the round-23 preregistration is the contract; the key set is code, not data):

  K1 after-receipt binding (spot-check D2). Every `assertions=/resolved=/skipped=/mismatches=`
     4-tuple on an `r22`/`round-22` line of SCORECARD.md that names the receipt's `rev=` value
     must equal the receipt's counts (read as stated under "Receipt counts" below), and at
     least one such bound occurrence must exist.
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

Receipt counts (K1, K2): a fenced receipt's counts are read only from its recorded stdout
section, the lines between `--- stdout ---` and `--- stderr ---` (to the end when no stderr
fence follows); the last counts tuple in that section wins, whether or not a label line follows
it. Text before the stdout fence and text after the stderr fence is never counted, so a
post-fence `mismatches=0` cannot shadow a stdout `mismatches=7`. An unfenced receipt is read
whole, last tuple winning.

Counts line: keys=<K> records=<R> occurrences=<O> mismatches=<M>
Mismatch rows: MISMATCH<TAB><key><TAB><record><TAB><class><TAB><detail>
Exit 0 iff M == 0.  Read-only: git plumbing (`show`, `rev-parse`) plus one
working-tree `status` query. No checkout, no fetch, no writes inside the repo.

Frozen contract: .ufo/waves/round-23/preregistration.txt (C1).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True

K1_RECEIPT = "census/round-23/records/declared-evidence-after.tsv"
K1_RECORDS = ("SCORECARD.md",)
K1_SCOPE = re.compile(r"(?i)\br22\b|round-22")

K2_RECORD = "LOG.md"
K2_SECTION_START = re.compile(r"^Round22 attempt2")
K2_SECTION_END = re.compile(r"^=====")
K2_RECEIPT = "census/round-22/attempt2/declared-evidence-before-final.tsv"
K2_CORRECTION_MARKER = "superseded by"
# the r22 section body's sha256 lives in a committed record (census/round-23/records/
# k2-section-sha256): filed bytes are append-only, so the section must be byte-identical and the
# correction must be a *later* act. A repository without that record (the fixture) skips the check.
K2_SECTION_SHA_FILE = "census/round-23/records/k2-section-sha256"

K3_RECEIPT = "census/round-22/attempt2/slice-verdicts.tsv"
K3_RECORDS = ("corpus/README.md", "corpus/lessons/round-22.md")
K3_CLASSES = ("accepted", "present", "unverifiable", "refused")

K4_EXEMPT_FILE = "census/round-23/records/uncommitted-exemptions.tsv"
K4_ALLOWED = frozenset({"census/operator-sweep-20261019/"})
# r85 (S315 racy-git, S316 git-hash-object(1), S317 gitformat-index(5)): an index entry carries stat(2) data beside
# the object name, so rewritten bytes over a rewritten stat entry read clean in `git status`. K4 therefore re-hashes
# every status-clean stage-0 tracked path against the object id its index entry records, through the receipt
# writer's own byte-truth check (the r73/r74 rule this lane already runs in the writer and the pre-report gate).
K4_TRUTH_WRITER = os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(__file__))),
                                 "souji-receipt-write.py")
REV_TOKEN_RE = re.compile(r"\b[0-9a-f]{40}\b")
K2_FILED = ("assertions=56 resolved=53 skipped=33 mismatches=3", "1 present", "1 refused")

COUNTS_RE = re.compile(r"assertions=(\d+) resolved=(\d+) skipped=(\d+) mismatches=(\d+)")
STDOUT_FENCE = "--- stdout ---"
STDERR_FENCE = "--- stderr ---"
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
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE") and not k.startswith("GIT_CONFIG_")}
    # r85 (S85Sentinel F1/F6): K4's status read and the writer's pinned status must agree, or a path clean to
    # one and listed by the other is neither reported nor re-hashed. Same pins the writer's helper uses.
    pins = [("core.fsmonitor", "false"), ("core.fileMode", "true"), ("core.checkStat", "default"),
            ("core.trustctime", "true"), ("core.excludesFile", os.devnull),
            ("status.showUntrackedFiles", "all")]
    env["GIT_CONFIG_COUNT"] = str(len(pins))
    for i, (k, v) in enumerate(pins):
        env[f"GIT_CONFIG_KEY_{i}"], env[f"GIT_CONFIG_VALUE_{i}"] = k, v
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    # a read-only instrument must not refresh the lane's index on `git status`
    env["GIT_OPTIONAL_LOCKS"] = "0"
    cmd = ["git", "-C", root, "-c", "maintenance.auto=false", *args]
    return subprocess.run(cmd, capture_output=True, text=True, env=env, check=check)


def read_at(root: str, rev: str, path: str) -> str | None:
    proc = git(root, "show", f"{rev}:{path}")
    if proc.returncode != 0:
        return None
    return proc.stdout


def counts_of(text: str) -> tuple[str, str] | None:
    """Return (4-tuple string, rev header) from a receipt.

    A fenced receipt's measured value is its recorded stdout section, between `--- stdout ---`
    and `--- stderr ---`: a summary line before the stdout fence and a line after the stderr
    fence both stay outside it (r24 W2R23F4: last-wins over the whole text let a post-fence line
    shadow stdout). Unfenced receipts are read whole. Within the section the last match wins.
    """
    lines = text.splitlines()
    region = text
    if STDOUT_FENCE in lines:
        start = lines.index(STDOUT_FENCE) + 1
        end = lines.index(STDERR_FENCE, start) if STDERR_FENCE in lines[start:] else len(lines)
        region = "\n".join(lines[start:end])
    matches = COUNTS_RE.findall(region)
    if not matches:
        return None
    m = matches[-1]
    rm = REV_LINE_RE.search(text)
    return "assertions=%s resolved=%s skipped=%s mismatches=%s" % m, (rm.group(1) if rm else "")


def tally_of(text: str) -> dict[str, int]:
    tally = {c: 0 for c in K3_CLASSES}
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        cells = line.split("\t")
        if len(cells) >= 2 and cells[1].strip() in tally:
            tally[cells[1].strip()] += 1
    return tally


def truth_refusal(root: str) -> "str | None":
    """r85: the refusal message when a tracked path git status reports clean does not hash to the object id the
    index records. The check is the receipt writer's `_truth_refusal`, run in an isolated interpreter from the
    writer's source bytes beside this tool's REAL path (one rule, one implementation; the r74 gate does the same).

    r85 wave repair (S85Sentinel F2): the writer is resolved with `realpath` (a symlinked or copied tool no longer
    loads whatever sits beside the link), and it is compiled in a `-I -B` subprocess (`-I`: no PYTHONPATH, no user
    site, no caller CWD on sys.path; `-B`: no __pycache__), so nothing imports attacker-named modules into this
    process. Fails closed: a missing writer, a subprocess failure, or a nonzero exit becomes a message, never a
    clean verdict."""
    if not os.path.isfile(K4_TRUTH_WRITER):
        return f"the receipt writer is not beside this tool ({K4_TRUTH_WRITER}); tracked bytes are unverified"
    bootstrap = (
        "import sys, types\n"
        "path, root = sys.argv[1], sys.argv[2]\n"
        "src = open(path, 'rb').read()\n"
        "mod = types.ModuleType('souji_receipt_write')\n"
        "mod.__file__ = path\n"
        "sys.modules[mod.__name__] = mod\n"
        "sys.argv = [path]\n"
        "try:\n"
        "    exec(compile(src, path, 'exec'), mod.__dict__)\n"
        "except SystemExit as exc:\n"
        "    print('REFUSED %s' % exc.code); raise SystemExit(0)\n"
        "try:\n"
        "    msg = mod._truth_refusal(root)\n"
        "except SystemExit as exc:\n"
        "    print('REFUSED %s' % exc.code); raise SystemExit(0)\n"
        "if not msg:\n"
        "    fl = mod.git(root, 'ls-files', '-v', '-z', ':(top)')\n"
        "    if fl.returncode != 0:\n"
        "        print('FLAGFAIL ' + fl.stderr.decode('utf-8', 'replace').strip()[:200])\n"
        "        raise SystemExit(0)\n"
        "    for rec in fl.stdout.split(bytes([0])):\n"
        "        if not rec:\n"
        "            continue\n"
        "        tag, _, p = rec.partition(bytes([32]))\n"
        "        if tag != bytes([72]):\n"
        "            msg = mod._flag_refusal(root, tag, p)\n"
        "            break\n"
        "print('CLEAN' if not msg else 'FORGED ' + msg)\n"
    )
    try:
        proc = subprocess.run([sys.executable, "-I", "-B", "-c", bootstrap, K4_TRUTH_WRITER, root],
                              capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.SubprocessError) as exc:
        return f"the receipt writer could not be run ({type(exc).__name__}: {exc}); tracked bytes are unverified"
    out = proc.stdout.strip()
    if out.startswith("REFUSED"):
        return f"the receipt writer refused the tree (exit {out.split(' ', 1)[-1]}); tracked bytes are unverified"
    if out.startswith("FLAGFAIL"):
        return (f"the index-flag read failed ({out[len('FLAGFAIL '):].strip()}); tracked bytes are unverified")
    if out.startswith("FORGED "):
        # r86: a path may carry a newline or a tab (S85ExecK4 §2e). C-escape them so one K4 record stays one
        # physical line and still names the path a reader must act on.
        return (out[len("FORGED "):].replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r"))
    if out == "CLEAN":
        return None
    return (f"the receipt writer produced no verdict (exit {proc.returncode}: "
            f"{(out or proc.stderr.strip())[:200]}); tracked bytes are unverified")


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
        elif git(self.root, "cat-file", "-e", f"{rev}^{{commit}}").returncode != 0:
            self.bad("K1", K1_RECEIPT, "receipt-rev-object", f"no such commit {rev}")
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
                    elif not bound:
                        # a tuple that claims to be a measured point yet carries no revision on
                        # its own physical line: W2K1 F1 moves the rev off-line to buy a green
                        self.occurrences += 1
                        self.bad("K1", f"{record}:{lineno}", "unbound-tuple",
                                 f"{m.group(0)} has no revision token on its line")
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
            if K2_SECTION_END.match(lines[j]) or K2_SECTION_START.match(lines[j]):
                end = j
                break
        want_digest = ""
        sha_text = read_at(self.root, self.rev, K2_SECTION_SHA_FILE)
        for line in (sha_text or "").splitlines():
            if line.strip() and not line.startswith("#"):
                want_digest = line.strip()
        if want_digest:
            body_text = "\n".join(lines[body_start:end]).rstrip()
            section_digest = hashlib.sha256(body_text.encode()).hexdigest()
            if section_digest != want_digest:
                self.bad("K2", K2_RECORD, "section-modified",
                         f"r22 section body {section_digest[:12]} != recorded {want_digest[:12]}")
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
                # the correction must be strictly AFTER the scanned section, must quote the stale
                # value and must carry the receipt-derived corrected value
                if occ.startswith("assertions="):
                    want = want_counts
                else:
                    n, cls = occ.split(" ", 1)
                    want = f"{want_tally.get(cls, 0)} {cls}"
                later = any(
                    K2_CORRECTION_MARKER in " ".join(lines[k:min(k + 6, len(lines))])
                    and occ in " ".join(lines[k:min(k + 6, len(lines))])
                    and want and want in " ".join(lines[k:min(k + 6, len(lines))])
                    for k in range(end, len(lines))
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
        msg = truth_refusal(self.root)
        if msg:
            flag = msg.startswith(("RECEIPT-GITLINK-CONCEALED", "RECEIPT-INDEX-"))
            self.bad("K4", ".", "index-flag-concealed" if flag else "stat-cache-concealed", msg)

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
