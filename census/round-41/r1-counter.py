#!/usr/bin/env python3
"""census/round-41/r1-counter.py — r41 R1 (residual, not a claim): record-order and root-repo mutation coverage.

Residual repair R40-D-TOTAL (not a claim): `tools/souji-worktree-drift.py` carries eleven single-defect mutants, M11-M21. Eight
are the retained r39/r40 mutants (M11-M14 from `census/round-39/c3-counter.py`, M15-M18 from
`census/round-40/c3-counter.py`, tables copied verbatim below); three are new:

  M19  every TOTAL row is checked against the REPO rows; the mutant checks only the LAST one, so a
       first-disagreeing, last-agreeing TOTAL pair is accepted (r40 M40-4 / routed defect R40-D-TOTAL)
  M20  the root repository is reported UNRECORDED when the record does not name it; the mutant
       drops the root from discovery
  M21  a record row naming the root's own basename is measured at the root; the mutant resolves it
       to nothing, so the row reads ABSENT

Pristine is the frozen tool (`PRISTINE_SHA256`; the r41 fix for M19's defect is part of those bytes).
Three fixtures score it; each is run on the pristine tool and on every mutant:

  r39  tests/fixtures/r39-drift-record-rules.py       (frozen at the base revision; kills M11-M14)
  r40  tests/fixtures/r40-drift-record-branches.py    (frozen at the base revision; kills M15-M18)
  r41  tests/fixtures/r41-drift-record-order.py       (the candidate; must kill M19-M21)

A kill needs the fixture's own `SUMMARY cases=... fail>0`, exit 1 and no Python traceback on the
fixture's STDERR (the r40 scoring contract). Retention: M11-M14 must be killed by the r39 fixture
alone and M15-M18 by the r40 fixture alone. Novelty: M19-M21 must be killed by the r41 fixture and by
neither old fixture. Regression: the six prior drift fixtures listed in PRIOR must each exit 0 with
`fail=0` on the pristine tool.

CLI:
  python3 -B census/round-41/r1-counter.py --root LANE --rev FULL40 [--scratch DIR]
      [--fixture PATH-IN-REV] [--pristine-sha SHA]
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate (bad rev, pinned bytes differ, anchor defect,
scratch unavailable).
Target: `SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3
old_fixtures_killed_new=0 prior=6/6`.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

REV = re.compile(r"^[0-9a-f]{40}$")
TOOL = "tools/souji-worktree-drift.py"
F39 = "tests/fixtures/r39-drift-record-rules.py"
F40 = "tests/fixtures/r40-drift-record-branches.py"
F41 = "tests/fixtures/r41-drift-record-order.py"
PRIOR = ("tests/fixtures/r36-worktree-drift.py", "tests/fixtures/r37-drift-discrimination.py",
         "tests/fixtures/r38-drift-record.py", "tests/fixtures/r38-drift-write-envelope.py",
         "tests/fixtures/r39-drift-record-rules.py", "tests/fixtures/r40-drift-record-branches.py")
PRISTINE_SHA256 = "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}

SKIP_ANCHOR = '        if not line.strip() or line.startswith("#"):'
TOTAL_ASSIGN = ('            total = {"repos": int(m.group("repos")), "regs": int(m.group("regs")), '
                '"prunable": int(m.group("prunable"))}')
SKIP_GUARD = "    if not args.skip_unrecorded:"
DECODE = '        raw = b"".join(chunks).decode("utf-8", "replace")'
REPOS_GUARD = '        if total["repos"] != len(rows):'
ROOT_DISCOVERY = '    if os.path.isdir(os.path.join(root, ".git")):'
ROOT_FALLBACK = '    if name == os.path.basename(root.rstrip("/")) and os.path.isdir(os.path.join(root, ".git")):'
# (id, anchor, replacement, owner fixture path). Anchors must occur exactly once in the pristine tool.
MUTANTS = (
    ("M11", SKIP_ANCHOR, '        line = line.rstrip()\n' + SKIP_ANCHOR, F39),
    ("M12", '    for lineno, line in enumerate(raw.splitlines(), 1):',
     '    for lineno, line in enumerate(raw.split("\\n"), 1):', F39),
    ("M13", 'raise Refusal("RECORD-OUTSIDE-ROOT: %s resolves outside %s" % (row["name"], root_real))',
     'pass', F39),
    ("M14", SKIP_ANCHOR, '        if not line.strip() or line.lstrip().startswith("#"):', F39),
    ("M15", TOTAL_ASSIGN,
     '            if total is None:\n'
     '                total = {"repos": int(m.group("repos")), "regs": int(m.group("regs")), '
     '"prunable": int(m.group("prunable"))}', F40),
    ("M16", SKIP_GUARD, "    if True:", F40),
    ("M17", DECODE, '        raw = b"".join(chunks).decode("utf-8", "ignore")', F40),
    ("M18", REPOS_GUARD, "        if False:", F40),
    ("M19", "    for total in totals:", "    for total in totals[-1:]:", F41),
    ("M20", ROOT_DISCOVERY, "    if False:", F41),
    ("M21", ROOT_FALLBACK, "    if False:", F41),
)


def child_env(scratch):
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    env.update(GIT_ENV)
    return env


def git_show(root, rev, path, scratch):
    proc = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=child_env(scratch), check=False)
    return proc.stdout if proc.returncode == 0 else None


def resolves(root, rev, scratch):
    return subprocess.run(["git", "-C", root, "cat-file", "-e", rev + "^{commit}"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          env=child_env(scratch), check=False).returncode == 0


def run(fixture, tool, scratch):
    """Return (rc, cases, passed, failed, crash, failing-case-names); cases None without a SUMMARY."""
    proc = subprocess.run(["python3", "-B", fixture, "--tool", tool, "--work", scratch],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                          env=child_env(scratch), timeout=900)
    summ = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
    crash = "Traceback (most recent call last)" in proc.stderr
    failing = [l.split("=", 1)[0][5:] for l in proc.stdout.splitlines()
               if l.startswith("case-") and "=FAIL" in l.split(" ", 1)[0]]
    m = re.search(r"cases=(\d+) pass=(\d+) fail=(\d+)", summ[-1]) if summ else None
    if not m:
        return proc.returncode, None, None, None, crash, failing
    return proc.returncode, int(m.group(1)), int(m.group(2)), int(m.group(3)), crash, failing


def killed(res):
    rc, cases, _p, failed, crash, _f = res
    return cases is not None and rc == 1 and failed > 0 and not crash


def clean(res):
    rc, cases, passed, failed, crash, _f = res
    return cases is not None and rc == 0 and failed == 0 and passed == cases and not crash


def write(path, text, mode=0o644):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.chmod(path, mode)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--fixture", default=F41)
    ap.add_argument("--pristine-sha", default=PRISTINE_SHA256)
    ap.add_argument("--scratch")
    args = ap.parse_args(argv)
    scratch_root = args.scratch or os.environ.get("TMPDIR")
    if not scratch_root or not os.path.isdir(scratch_root):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --scratch (or TMPDIR) must name a directory\n")
        return 2
    if not REV.match(args.rev) or not resolves(args.root, args.rev, scratch_root):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --rev must name a resolvable full40 commit\n")
        return 2
    tool_b = git_show(args.root, args.rev, TOOL, scratch_root)
    if tool_b is None:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: tool absent at %s\n" % args.rev)
        return 2
    tool_sha = hashlib.sha256(tool_b).hexdigest()
    if tool_sha != args.pristine_sha:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: tool sha256 %s differs from the pinned %s\n" % (
            tool_sha, args.pristine_sha))
        return 2
    source = tool_b.decode("utf-8")
    for mid, old, _new, _owner in MUTANTS:
        if source.count(old) != 1:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s anchor occurs %d times (expected 1)\n" % (
                mid, source.count(old)))
            return 2
    scratch = tempfile.mkdtemp(prefix="souji-r41-c3.", dir=scratch_root)
    try:
        pristine = os.path.join(scratch, "pristine.py")
        write(pristine, source, 0o755)
        fixtures = {}
        for path in sorted({F39, F40, args.fixture} | set(PRIOR)):
            blob = git_show(args.root, args.rev, path, scratch_root)
            fixtures[path] = blob
        prior_ok = 0
        for path in PRIOR:
            if fixtures[path] is None:
                continue
            local = os.path.join(scratch, "prior-" + os.path.basename(path))
            write(local, fixtures[path].decode("utf-8"))
            prior_ok += 1 if clean(run(local, pristine, scratch)) else 0
        cand_blob = fixtures[args.fixture]
        if cand_blob is None:
            print("PRISTINE FAIL FIXTURE-ABSENT %s at %s" % (args.fixture, args.rev))
            print("SUMMARY mutants=%d killed=0 survived=%d pristine=FAIL regress=0/8 new_killed=0/3 "
                  "old_fixtures_killed_new=0 prior=%d/6 cases=0 tool_sha=%s fixture_sha=absent" % (
                      len(MUTANTS), len(MUTANTS), prior_ok, tool_sha[:12]))
            return 1
        local = {}
        for path in (F39, F40, args.fixture):
            local[path] = os.path.join(scratch, "fx-" + os.path.basename(path))
            write(local[path], fixtures[path].decode("utf-8"))
        pres = {p: run(local[p], pristine, scratch) for p in (F39, F40, args.fixture)}
        pristine_ok = all(clean(r) for r in pres.values()) and pres[args.fixture][1] >= 6
        cases = pres[args.fixture][1] or 0
        if not pristine_ok:
            print("SUMMARY mutants=%d killed=0 survived=%d pristine=FAIL regress=0/8 new_killed=0/3 "
                  "old_fixtures_killed_new=0 prior=%d/6 cases=%d tool_sha=%s fixture_sha=%s" % (
                      len(MUTANTS), len(MUTANTS), prior_ok, cases, tool_sha[:12],
                      hashlib.sha256(cand_blob).hexdigest()[:12]))
            return 1
        survived = regress = new_killed = old_killed_new = killed_n = 0
        for mid, old, new, owner in MUTANTS:
            mpath = os.path.join(scratch, mid + ".py")
            write(mpath, source.replace(old, new), 0o755)
            kills = {}
            for path in (F39, F40, args.fixture):
                kills[path] = run(local[path], mpath, scratch)
            by = [os.path.basename(p) for p in (F39, F40, args.fixture) if killed(kills[p])]
            is_new = owner == F41
            owner_path = args.fixture if is_new else owner
            owner_kills = killed(kills[owner_path])
            if is_new:
                old_hit = killed(kills[F39]) or killed(kills[F40])
                old_killed_new += 1 if old_hit else 0
                new_killed += 1 if owner_kills else 0
                counted = owner_kills
            else:
                regress += 1 if owner_kills else 0
                counted = owner_kills
            killed_n += 1 if counted else 0
            survived += 0 if (owner_kills or by) else 1
            print("MUTANT %s owner=%s killed=%s by=%s failing=%s" % (
                mid, os.path.basename(owner_path), "yes" if owner_kills else "no",
                ",".join(by) or "-", ",".join(kills[owner_path][5]) or "-"))
        print("SUMMARY mutants=%d killed=%d survived=%d pristine=ok regress=%d/8 new_killed=%d/3 "
              "old_fixtures_killed_new=%d prior=%d/6 cases=%d tool_sha=%s fixture_sha=%s" % (
                  len(MUTANTS), killed_n, len(MUTANTS) - killed_n, regress, new_killed,
                  old_killed_new, prior_ok, cases, tool_sha[:12],
                  hashlib.sha256(cand_blob).hexdigest()[:12]))
        met = (killed_n == len(MUTANTS) == 11 and regress == 8 and new_killed == 3
               and old_killed_new == 0 and prior_ok == 6 and cases >= 6)
        return 0 if met else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
