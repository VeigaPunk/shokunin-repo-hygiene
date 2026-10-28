#!/usr/bin/env python3
"""census/round-41/c1-counter.py — r41 C1 (calibration): filed self-assessments vs re-derived state.

Population (frozen, `census/round-41/c1-items.tsv`, sha256 pinned below): three filed statements of
the round-40 record that the round-40 non-author spot-check (`corpus/lessons/round-40-verifier-spotcheck.md`
§6) routed to this lane, each re-derivable from committed bytes at the measured revision
`MEASURED = bffcc0f660ff36eb8add3f61582748a7af019a5b`:

  I1  corpus/lessons/round-40.md says `worktree.c` "appears in 9 rows" of corpus/SOURCES.md. Derived at
      MEASURED: registry rows containing `worktree.c` and rows containing `v2.56.0/worktree.c`.
  I3  SCORECARD.md's r40 C1 row presents `c1-before.txt` and `c1-after-h.txt` as one before->after. Derived:
      the two receipts' `register_cells=` values (the arms ran over different register files).
  I4  LOG.md's r40 entry records the dead seats' provider error text. Derived: occurrences of that text
      in committed bytes under census/round-40/waves/ at MEASURED.

An item is MISMATCHED when its derivation disagrees with the filed statement (I1: rows != 9; I3: the two
register_cells values differ; I4: zero committed occurrences). The filed text is never rewritten. An item
is CORRECTED when `corpus/lessons/round-41.md` at --rev carries a line

  CORRECTION <id> file=<path> filed=<claimed> derived=<value> rev=<MEASURED> source=<S###|->

whose id, file and claimed token match the table, whose `derived` equals this counter's own derivation
(I1 `rows=2,v2.56.0=0`; I3 `before=6,after=3`; I4 `occurrences=0`), and whose `rev` is MEASURED. I1's line
must also name a registry row at --rev (`source=S<id>`) that is tier A, status `mined`, opened `2026-10-28`
and whose cells name both `v2.56.0` and `worktree.c` (the sourced claim).

  junk        CORRECTION lines at --rev that validate against no item (unknown id, wrong derived value,
              wrong rev, wrong file/filed token); a junk line never corrects an item.
  rewritten   items whose filed anchor is absent from its file at --rev, or whose file at --rev does not
              begin with the bytes it had at MEASURED (the three files are append-only).

CLI:
  python3 -B census/round-41/c1-counter.py --root LANE --rev FULL40
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate (unresolved rev, MEASURED absent, items table
differs from its pinned digest).
Target: `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

REV = re.compile(r"^[0-9a-f]{40}$")
MEASURED = "bffcc0f660ff36eb8add3f61582748a7af019a5b"
ITEMS_PATH = "census/round-41/c1-items.tsv"
ITEMS_SHA256 = "2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf"
LESSON = "corpus/lessons/round-41.md"
REGISTRY = "corpus/SOURCES.md"
ROW = re.compile(r"^\|\s*(S\d{3,})\s*\|")
LINE = re.compile(r"^CORRECTION (\S+) file=(\S+) filed=(\S+) derived=(\S+) rev=(\S+) source=(\S+)\s*$")
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def show(root, rev, path):
    p = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=dict(GIT_ENV, PATH=os.environ.get("PATH", "")),
                       check=False)
    return p.stdout if p.returncode == 0 else None


def tree_files(root, rev, prefix):
    p = subprocess.run(["git", "-C", root, "ls-tree", "-r", "--name-only", rev, prefix],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=dict(GIT_ENV, PATH=os.environ.get("PATH", "")), check=False)
    return p.stdout.decode("utf-8", "replace").split("\n") if p.returncode == 0 else []


def derive(root, name):
    """Re-derive one item's value at MEASURED."""
    if name == "rows-worktree-c":
        text = (show(root, MEASURED, REGISTRY) or b"").decode("utf-8", "replace")
        rows = [l for l in text.splitlines() if ROW.match(l)]
        return "rows=%d,v2.56.0=%d" % (sum("worktree.c" in l for l in rows),
                                        sum("v2.56.0/worktree.c" in l for l in rows)), len(
            [1 for l in rows if "worktree.c" in l]) != 9
    if name == "register-cells":
        vals = []
        for path in ("census/round-40/records/c1-before.txt", "census/round-40/records/c1-after-h.txt"):
            text = (show(root, MEASURED, path) or b"").decode("utf-8", "replace")
            m = re.search(r"register_cells=(\d+)", text)
            vals.append(m.group(1) if m else "?")
        return "before=%s,after=%s" % tuple(vals), vals[0] != vals[1]
    if name == "committed-occurrences":
        n = 0
        for path in tree_files(root, MEASURED, "census/round-40/waves/"):
            if path:
                n += (show(root, MEASURED, path) or b"").decode("utf-8", "replace").count(
                    "flagged as potentially")
        return "occurrences=%d" % n, n == 0
    raise ValueError(name)


def sourced(root, rev, ident):
    text = (show(root, rev, REGISTRY) or b"").decode("utf-8", "replace")
    for line in text.splitlines():
        m = ROW.match(line)
        if m and m.group(1) == ident:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) != 11:
                return False
            blob = cells[1] + " " + cells[5]
            return (cells[3] == "A" and cells[7] == "mined" and cells[8] == "2026-10-28"
                    and "v2.56.0" in blob and "worktree.c" in blob)
    return False


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scratch")  # accepted for the shared scoring harness; the counter writes nothing
    args = ap.parse_args(argv)
    ok_rev = REV.match(args.rev) and subprocess.run(
        ["git", "-C", args.root, "cat-file", "-e", args.rev + "^{commit}"], stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, env=dict(GIT_ENV, PATH=os.environ.get("PATH", "")),
        check=False).returncode == 0
    if not ok_rev or show(args.root, MEASURED, REGISTRY) is None:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --rev or the measured revision does not resolve\n")
        return 2
    table = show(args.root, args.rev, ITEMS_PATH)
    if table is None or hashlib.sha256(table).hexdigest() != ITEMS_SHA256:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: items table absent or differs from the pinned digest\n")
        return 2
    items = {}
    for line in table.decode("utf-8").splitlines()[1:]:
        if line.strip():
            iid, path, anchor, claimed, derivation = line.split("\t")
            items[iid] = (path, anchor, claimed, derivation)
    lesson = (show(args.root, args.rev, LESSON) or b"").decode("utf-8", "replace")
    corrections = [m for m in (LINE.match(l) for l in lesson.splitlines()) if m]
    mismatched = corrected = rewritten = junk = sourced_n = 0
    for iid, (path, anchor, claimed, derivation) in sorted(items.items()):
        base = show(args.root, MEASURED, path)
        tip = show(args.root, args.rev, path)
        derived, is_mismatch = derive(args.root, derivation)
        present = base is not None and anchor.encode("utf-8") in base
        mismatched += 1 if (present and is_mismatch) else 0
        intact = tip is not None and anchor.encode("utf-8") in tip and base is not None \
            and tip.startswith(base)
        rewritten += 0 if intact else 1
        good = [m for m in corrections if m.group(1) == iid and m.group(2) == path
                and m.group(3) == claimed and m.group(4) == derived and m.group(5) == MEASURED]
        fine = bool(good)
        if iid == "I1":
            src_ok = any(sourced(args.root, args.rev, m.group(6)) for m in good)
            sourced_n += 1 if src_ok else 0
            fine = fine and src_ok
        corrected += 1 if fine else 0
        print("ITEM %s %s mismatch=%s derived=%s corrections=%d intact=%s" % (
            iid, "present" if present else "ANCHOR-ABSENT", "yes" if is_mismatch else "no", derived,
            len(good), "yes" if intact else "NO"))
    for m in corrections:
        spec = items.get(m.group(1))
        if spec is None:
            junk += 1
            continue
        derived, _ = derive(args.root, spec[3])
        if not (m.group(2) == spec[0] and m.group(3) == spec[2] and m.group(4) == derived
                and m.group(5) == MEASURED):
            junk += 1
    print("SUMMARY items=%d mismatched=%d corrected=%d uncorrected=%d junk=%d rewritten=%d sourced=%d" % (
        len(items), mismatched, corrected, len(items) - corrected, junk, rewritten, sourced_n))
    met = (True and mismatched == 3 and corrected == 3 and junk == 0 and rewritten == 0
           and sourced_n == 1)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
