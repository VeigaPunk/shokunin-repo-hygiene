#!/usr/bin/env python3
"""R40w2critic08 attack driver (scratch, read-only against the lane).

Builds single-defect mutants of tools/souji-worktree-drift.py at REV (bytes read with
`git show`, never from the working tree), writes each into --scratch, and scores each one with the
r40 candidate fixture tests/fixtures/r40-drift-record-branches.py and the r39 base fixture
tests/fixtures/r39-drift-record-rules.py, using the same kill rule as census/round-40/c3-counter.py
(fixture rc==1, its own SUMMARY fails>0, no traceback on its STDERR).

CLI:
  python3 -B .ufo/waves/round-40/w2/R40w2critic08-attack.py --root LANE --rev REV --scratch DIR
Exit: 0 always after a full run (the table is the result); 2 usage / anchor error.
"""
import argparse
import concurrent.futures
import os
import re
import shutil
import subprocess
import sys

CHILD = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_ATTR_NOSYSTEM": "1",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_TERMINAL_PROMPT": "0",
}

# Exact anchors in tools/souji-worktree-drift.py (asserted to occur exactly once).
A_TOTAL = ('            total = {"repos": int(m.group("repos")), "regs": int(m.group("regs")), '
           '"prunable": int(m.group("prunable"))}')
A_TOTAL_IF = '    if total is not None:'
A_REPOS = '        if total["repos"] != len(rows):'
A_REGS = '        if total["regs"] != sum(r["regs"] for r in rows):'
A_PRUN = '        if total["prunable"] != sum(r["prunable"] for r in rows):'
A_DECODE = '        raw = b"".join(chunks).decode("utf-8", "replace")'
A_NAME = '            name = m.group("name")'
A_COMMENT = '        if not line.strip() or line.startswith("#"):'
A_SKIP = '    if not args.skip_unrecorded:'
A_ABSENT = '            drift.append(("ABSENT", name, "recorded regs=%d" % row["regs"]))'
A_REGSCH = ('            drift.append(("REGS-CHANGED", name, "record=%d live=%d" % '
            '(row["regs"], regs)))')

# (id, branch, mutant-kind, old, new)
# branch: A = multiple TOTAL rows, B = --skip-unrecorded, C = invalid UTF-8, X = other (survivor probes)
MUTANTS = [
    ("A1", "A", "declared M15: keep FIRST TOTAL", A_TOTAL,
     '            if total is None:\n'
     '                total = {"repos": int(m.group("repos")), "regs": int(m.group("regs")), '
     '"prunable": int(m.group("prunable"))}'),
    ("A2", "A", "refuse any second TOTAL (even identical)", A_TOTAL,
     '            if total is not None:\n'
     '                raise Refusal("RECORD-MALFORMED: duplicate TOTAL")\n' + A_TOTAL),
    ("A3", "A", "keep FIRST only when repos equal (same-repos conflict accepted)", A_TOTAL,
     '            if total is None or total["repos"] != int(m.group("repos")):\n'
     '                total = {"repos": int(m.group("repos")), "regs": int(m.group("regs")), '
     '"prunable": int(m.group("prunable"))}'),
    ("A4", "A", "declared M18: repos guard disabled", A_REPOS, "        if False:"),
    ("A5", "A", "repos guard '!=' -> '<'", A_REPOS, '        if total["repos"] < len(rows):'),
    ("A6", "A", "repos guard '!=' -> '>'", A_REPOS, '        if total["repos"] > len(rows):'),
    ("A7", "A", "regs guard disabled", A_REGS, "        if False:"),
    ("A8", "A", "prunable guard disabled", A_PRUN, "        if False:"),
    ("A9", "A", "regs guard '!=' -> '>'", A_REGS, '        if total["regs"] > sum(r["regs"] for r in rows):'),
    ("A10", "A", "whole TOTAL consistency block disabled", A_TOTAL_IF, "    if False:"),
    ("B1", "B", "inverted: skip only WITH the flag", A_SKIP, "    if args.skip_unrecorded:"),
    ("B2", "B", "declared M16: always scan", A_SKIP, "    if True:"),
    ("B3", "B", "never scan (UNRECORDED never produced)", A_SKIP, "    if False:"),
    ("B4", "B", "flag also suppresses ABSENT rows", A_ABSENT,
     '            if not args.skip_unrecorded:\n'
     '                drift.append(("ABSENT", name, "recorded regs=%d" % row["regs"]))'),
    ("B5", "B", "REGS-CHANGED row dropped entirely", A_REGSCH, "            pass"),
    ("B6", "B", "flag suppresses REGS-CHANGED rows", A_REGSCH,
     '            if not args.skip_unrecorded:\n'
     '                drift.append(("REGS-CHANGED", name, "record=%d live=%d" % '
     '(row["regs"], regs)))'),
    ("C1", "C", "declared M17: decode 'ignore'", A_DECODE,
     '        raw = b"".join(chunks).decode("utf-8", "ignore")'),
    ("C2", "C", "decode strict (no error handler)", A_DECODE,
     '        raw = b"".join(chunks).decode("utf-8")'),
    ("C3", "C", "decode 'surrogateescape'", A_DECODE,
     '        raw = b"".join(chunks).decode("utf-8", "surrogateescape")'),
    ("C4", "C", "decode 'backslashreplace'", A_DECODE,
     '        raw = b"".join(chunks).decode("utf-8", "backslashreplace")'),
    ("C5", "C", "decode latin-1 (no UTF-8 at all)", A_DECODE,
     '        raw = b"".join(chunks).decode("latin-1")'),
    ("C6", "C", "decode ascii + replace", A_DECODE,
     '        raw = b"".join(chunks).decode("ascii", "replace")'),
    ("C7", "C", "replace kept, U+FFFD stripped from REPO names", A_NAME,
     '            name = m.group("name").replace("\\ufffd", "")'),
    ("C8", "C", "U+FFFD in a comment line refused", A_COMMENT,
     '        if not line.strip() or line.startswith("#"):\n'
     '            if "\\ufffd" in line:\n'
     '                raise Refusal("RECORD-MALFORMED: invalid byte")'),
    ("C9", "C", "any U+FFFD line silently skipped", A_COMMENT,
     '        if not line.strip() or line.startswith("#") or "\\ufffd" in line:'),
]


def git_show(root, rev, path):
    proc = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=CHILD, check=False)
    if proc.returncode != 0:
        sys.stderr.write("could not read %s:%s\n" % (rev, path))
        sys.exit(2)
    return proc.stdout.decode("utf-8")


def score(fixture, tool, work):
    os.makedirs(work, exist_ok=True)
    env = dict(CHILD)
    env["TMPDIR"] = work
    proc = subprocess.run(["python3", "-B", fixture, "--tool", tool, "--work", work],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                          check=False, env=env)
    summaries = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
    if not summaries:
        return False, "NO-SUMMARY rc=%d" % proc.returncode
    m = re.search(r"cases=(\d+) pass=(\d+) fail=(\d+)", summaries[-1])
    fails = int(m.group(3))
    crash = "Traceback (most recent call last)" in proc.stderr
    failing = [l.split("=", 1)[0][5:] for l in proc.stdout.splitlines()
               if l.startswith("case-") and "=FAIL" in l.split(" ", 1)[0]]
    killed = proc.returncode == 1 and fails > 0 and not crash
    return killed, "rc=%d fails=%d crash=%s failing=%s" % (
        proc.returncode, fails, crash, ",".join(failing) or "-")


def run_one(item, cand, base, scratch, source):
    mid, branch, kind, old, new = item
    count = source.count(old)
    if count != 1:
        return mid, branch, kind, None, "ANCHOR-COUNT %d" % count, None, None
    mut_dir = os.path.join(scratch, mid)
    os.makedirs(mut_dir, exist_ok=True)
    tool = os.path.join(mut_dir, "tool.py")
    with open(tool, "w", encoding="utf-8") as handle:
        handle.write(source.replace(old, new))
    os.chmod(tool, 0o755)
    killed, detail = score(cand, tool, os.path.join(mut_dir, "cand"))
    base_killed, base_detail = score(base, tool, os.path.join(mut_dir, "base"))
    return mid, branch, kind, killed, detail, base_killed, base_detail


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scratch", required=True)
    args = ap.parse_args(argv)
    os.makedirs(args.scratch, exist_ok=True)
    source = git_show(args.root, args.rev, "tools/souji-worktree-drift.py")
    cand_src = git_show(args.root, args.rev, "tests/fixtures/r40-drift-record-branches.py")
    base_src = git_show(args.root, args.rev, "tests/fixtures/r39-drift-record-rules.py")
    cand = os.path.join(args.scratch, "r40-branches.py")
    base = os.path.join(args.scratch, "r39-rules.py")
    with open(cand, "w", encoding="utf-8") as h:
        h.write(cand_src)
    with open(base, "w", encoding="utf-8") as h:
        h.write(base_src)
    pristine = os.path.join(args.scratch, "pristine.py")
    with open(pristine, "w", encoding="utf-8") as h:
        h.write(source)
    os.chmod(pristine, 0o755)
    pk, pd = score(cand, pristine, os.path.join(args.scratch, "pristine-cand"))
    bk, bd = score(base, pristine, os.path.join(args.scratch, "pristine-base"))
    print("PRISTINE candidate killed=%s %s | base killed=%s %s" % (pk, pd, bk, bd))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(run_one, m, cand, base, args.scratch, source) for m in MUTANTS]
        rows = [f.result() for f in futures]
    survivors = []
    for mid, branch, kind, killed, detail, base_killed, base_detail in rows:
        if killed is None:
            print("%s [%s] %s -> %s" % (mid, branch, kind, detail))
            continue
        print("%s [%s] %s -> candidate_killed=%s (%s) | base_killed=%s (%s)" % (
            mid, branch, kind, "yes" if killed else "NO", detail,
            "yes" if base_killed else "no", base_detail))
        if not killed:
            survivors.append(mid)
    print("SURVIVORS-OF-CANDIDATE %s" % (",".join(survivors) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
