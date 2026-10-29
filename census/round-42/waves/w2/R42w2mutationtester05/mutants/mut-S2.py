#!/usr/bin/env python3
"""census/round-42/c3-counter.py — r42 C3 (coverage): condition-level mutants of the drift tool's refusal conditions.

Claim. r41 C3 reached the 19 refusal-class labels of `tools/souji-worktree-drift.py` (scored by label
mutation). Wave 2 of round 41 then showed the battery is class-level: single-defect mutants of the
tool's CONDITIONS (boundaries, containment test, inode alias, argparse requirements, discovery skip,
write truncation, exit code, record regex, timeouts, decode error handler) survive every committed
drift fixture (census/round-41/waves/w2/R41w2mutationtester03 harness table: G-class; R41-D-C3-CONDITION;
M40-12). This round's candidate fixture `tests/fixtures/r42-drift-conditions.py` must kill every
mutant in MUTANTS below, which none of the eight PRIOR fixtures kills (the survey of this round found that D3, F2, H3, J5, N1 and T2, survivors of the r41 refusal fixture alone, are killed by an older drift fixture and are not in the population; F1, called equivalent by the r41 mutation tester, is killed by r36 and is in neither list), without killing any mutant in
EQUIV (mutants with no observable behaviour, so a fixture that kills one reads the tool's bytes, a
label or a digest rather than its behaviour).

Fixture protocol: `python3 -B <fixture> --tool PATH --work DIR` prints `case-<name>=PASS|FAIL` lines
and `SUMMARY cases=<n> pass=<p> fail=<f>` (a `probes=` SUMMARY is read the same way); exit 0 iff
fail=0. A KILL is: the fixture exits 1, its own SUMMARY shows fail>0, and its STDERR carries no
Python traceback. Per-fixture timeout 300 s; mutants run in parallel under a per-run work directory.

Scoring (every number printed):
  mutants         len(MUTANTS)                                  frozen: 13
  killed          mutants the candidate fixture kills
  survived        mutants - killed
  pristine        ok iff the candidate runs clean (rc 0, fail=0, pass=cases) on the pinned tool with cases >= 13
  prior           how many of the 8 PRIOR fixtures run clean on the pinned tool (must be 8)
  old_killed      mutants killed by any PRIOR fixture (population requires 0: they are survivors of the prior battery)
  equiv           len(EQUIV) (frozen: 6); equiv_killed  EQUIV mutants the candidate kills (must be 0)
  anchors         ok iff every old string occurs exactly once in the pinned tool and the population
                  file `census/round-42/c3-mutants.tsv` lists exactly the MUTANTS ids with their anchor sha256

CLI:
  python3 -B census/round-42/c3-counter.py --root LANE --rev FULL40 [--fixture PATH-IN-REV] [--scratch DIR]
      [--survey]      (prints which PRIOR fixtures kill each mutant; informational, never a verdict)
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate (bad rev, uid 0, pinned bytes differ, anchor defect).
Target: `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok`.
"""
import argparse
import concurrent.futures
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

REV = re.compile(r"^[0-9a-f]{40}$")
TOOL = "tools/souji-worktree-drift.py"
CANDIDATE = "tests/fixtures/r42-drift-conditions.py"
POPULATION = "census/round-42/c3-mutants.tsv"
PRISTINE_SHA256 = "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"
PRIOR = ("tests/fixtures/r36-worktree-drift.py", "tests/fixtures/r37-drift-discrimination.py",
         "tests/fixtures/r38-drift-record.py", "tests/fixtures/r38-drift-write-envelope.py",
         "tests/fixtures/r39-drift-record-rules.py", "tests/fixtures/r40-drift-record-branches.py",
         "tests/fixtures/r41-drift-record-order.py", "tests/fixtures/r41-refusal-sites.py")
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
SUMMARY_RE = re.compile(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", re.M)

# (id, description, old (occurs exactly once in the pinned tool), new)
MUTANTS = (
    ("B1", "parse_record opens the record without O_NONBLOCK (a FIFO record blocks the tool)",
     "fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)", "fd = os.open(path, os.O_RDONLY)"),
    ("E2", "record-row containment uses commonprefix (a sibling directory sharing a name prefix is inside)",
     "inside = os.path.commonpath([resolved, root_real]) == root_real",
     "inside = os.path.commonprefix([resolved, root_real]) == root_real"),
    ("E4", "gitdir containment uses commonprefix",
     "gitdir_inside = os.path.commonpath([gitdir, root_real]) == root_real",
     "gitdir_inside = os.path.commonprefix([gitdir, root_real]) == root_real"),
    ("G2", "timeout lower bound moved: --timeout 1 refused",
     "if args.timeout < 1:", "if args.timeout <= 1:"),
    ("G3", "--timeout default 20 -> 1", "default=20", "default=1"),
    ("G4", "list-timeout handler re-raises instead of reporting UNREACHABLE",
     'return None, None, "UNREACHABLE:list-timeout"', "raise"),
    ("G5", "worktree-list nonzero return code no longer reported",
     "if listed.returncode != 0:", "if False:"),
    ("H1", "--root no longer required", 'ap.add_argument("--root", required=True)',
     'ap.add_argument("--root", default=".")'),
    ("H2", "--record no longer required", 'ap.add_argument("--record", required=True)',
     'ap.add_argument("--record", default=None)'),
    ("I1", "symlinked child directories are no longer skipped in discovery",
     "if os.path.islink(path):", "if False:"),
    ("J9", "REPO regs accepts a single digit only",
     r"^REPO\t(?P<name>[^\t]+)\tregs=(?P<regs>\d+)", r"^REPO\t(?P<name>[^\t]+)\tregs=(?P<regs>\d)"),
    ("M1", "ftruncate before the --json write removed (a longer old file keeps its tail)",
     "os.ftruncate(fd, 0)", "pass"),
    ("D4", "record decoded with backslashreplace instead of replace (M40-12)",
     'raw = b"".join(chunks).decode("utf-8", "replace")',
     'raw = b"".join(chunks).decode("utf-8", "backslashreplace")'),
)
# Mutants with no observable behaviour (R41w2mutationtester03 section 3a reasoning, re-checked by this
# round's wave 1). A fixture that kills one of these reads bytes, labels or digests.
EQUIV = (
    ("B3", "parse_record set_blocking(True) removed (regular file only: O_NONBLOCK has no effect)",
     "os.set_blocking(fd, True)\n        chunks = []", "chunks = []"),
    ("B4", "open_nofollow set_blocking(True) removed", "os.set_blocking(fd, True)\n        return fd",
     "return fd"),
    ("E5", "JSON guard loops over [root] only (every measured path already lies under root)",
     "for base in measured:", "for base in [root_real]:"),
    ("E7", "gitdir not appended to the measured list", "measured.append(gitdir)", "pass"),
    ("E9", "repo path not appended to the measured list", "measured.append(resolved)", "pass"),
    ("H4", "--json default empty string (falsy like None)", 'ap.add_argument("--json")',
     'ap.add_argument("--json", default="")'),
)


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    e.update(GIT_ENV)
    return e


def git_show(root, rev, path, scratch):
    p = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env(scratch), check=False)
    return p.stdout if p.returncode == 0 else None


def resolves(root, rev, scratch):
    return subprocess.run(["git", "-C", root, "cat-file", "-e", rev + "^{commit}"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env(scratch),
                          check=False).returncode == 0


def write(path, data, mode=0o644):
    with open(path, "wb") as handle:
        handle.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    os.chmod(path, mode)


def run(fixture, tool, scratch, tag):
    """Return (rc, cases, passed, failed, crash). cases is None when no SUMMARY line was printed."""
    work = tempfile.mkdtemp(prefix="w-%s." % tag, dir=scratch)
    try:
        e = env(scratch)
        e["TMPDIR"] = scratch
        proc = subprocess.run(["python3", "-B", fixture, "--tool", tool, "--work", work],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              check=False, env=e, timeout=300)
        m = SUMMARY_RE.findall(proc.stdout)
        crash = "Traceback (most recent call last)" in proc.stderr
        if not m:
            return proc.returncode, None, None, None, crash
        c, p, f = (int(x) for x in m[-1])
        return proc.returncode, c, p, f, crash
    except subprocess.TimeoutExpired:
        return 124, None, None, None, True
    finally:
        shutil.rmtree(work, ignore_errors=True)


def killed(res):
    rc, cases, _p, failed, crash = res
    return cases is not None and rc == 1 and failed > 0 and not crash


def clean(res):
    rc, cases, passed, failed, crash = res
    return cases is not None and rc == 0 and failed == 0 and passed == cases and not crash


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--fixture", default=CANDIDATE)
    ap.add_argument("--scratch")
    ap.add_argument("--survey", action="store_true")
    args = ap.parse_args(argv)
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: refusing to run as root\n")
        return 2
    scratch_root = args.scratch or os.environ.get("TMPDIR")
    if not scratch_root or not os.path.isdir(scratch_root):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --scratch (or TMPDIR) must name a directory\n")
        return 2
    if not REV.match(args.rev) or not resolves(args.root, args.rev, scratch_root):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --rev must name a resolvable full40 commit\n")
        return 2
    tool_b = git_show(args.root, args.rev, TOOL, scratch_root)
    if tool_b is None or hashlib.sha256(tool_b).hexdigest() != PRISTINE_SHA256:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: tool absent or sha256 differs from the pinned %s\n"
                         % PRISTINE_SHA256)
        return 2
    source = tool_b.decode("utf-8")
    for mid, _d, old, _new in MUTANTS + EQUIV:
        if source.count(old) != 1:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s anchor occurs %d times (expected 1)\n" % (
                mid, source.count(old)))
            return 2
    pop_b = git_show(args.root, args.rev, POPULATION, scratch_root)
    anchors = "FAIL"
    if pop_b is not None:
        want = {mid: hashlib.sha256(old.encode("utf-8")).hexdigest() for mid, _d, old, _n in MUTANTS}
        got = {}
        for n, line in enumerate(pop_b.decode("utf-8").split("\n")):
            f = line.split("\t")
            if n and len(f) >= 3:
                got[f[0]] = f[2]
        anchors = "ok" if got == want else "FAIL"
    scratch = tempfile.mkdtemp(prefix="souji-r42-c3.", dir=scratch_root)
    try:
        pristine = os.path.join(scratch, "pristine.py")
        write(pristine, tool_b, 0o755)
        fixtures = {}
        for path in PRIOR + (args.fixture,):
            blob = git_show(args.root, args.rev, path, scratch_root)
            if blob is not None:
                local = os.path.join(scratch, "fx-" + os.path.basename(path))
                write(local, blob)
                fixtures[path] = local
        jobs = {}
        for mid, _d, old, new in MUTANTS + EQUIV:
            mpath = os.path.join(scratch, "mut-%s.py" % mid)
            write(mpath, source.replace(old, new), 0o755)
            jobs[mid] = mpath
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            pre = {p: pool.submit(run, f, pristine, scratch, "pre") for p, f in fixtures.items()}
            prior_ok = sum(1 for p in PRIOR if p in fixtures and clean(pre[p].result()))
            cand_pre = pre[args.fixture].result() if args.fixture in fixtures else None
            pristine_ok = (cand_pre is not None and clean(cand_pre) and cand_pre[1] >= 13)
            cases = cand_pre[1] if cand_pre and cand_pre[1] else 0
            grid = {}
            if args.fixture in fixtures:
                for mid, mp in jobs.items():
                    grid[(mid, args.fixture)] = pool.submit(run, fixtures[args.fixture], mp, scratch, mid)
            if args.survey or True:
                for mid, mp in jobs.items():
                    for p in PRIOR:
                        if p in fixtures:
                            grid[(mid, p)] = pool.submit(run, fixtures[p], mp, scratch, mid)
            res = {k: v.result() for k, v in grid.items()}
        killed_n = equiv_killed = old_killed = 0
        for mid, desc, _o, _n in MUTANTS:
            cand = killed(res[(mid, args.fixture)]) if (mid, args.fixture) in res else False
            by = [os.path.basename(p) for p in PRIOR if (mid, p) in res and killed(res[(mid, p)])]
            killed_n += 1 if cand else 0
            old_killed += 1 if by else 0
            print("MUTANT %s candidate=%s prior=%s" % (mid, "killed" if cand else "SURVIVED", ",".join(by) or "-"))
        for mid, _d, _o, _n in EQUIV:
            cand = killed(res[(mid, args.fixture)]) if (mid, args.fixture) in res else False
            by = [os.path.basename(p) for p in PRIOR if (mid, p) in res and killed(res[(mid, p)])]
            equiv_killed += 1 if cand else 0
            print("EQUIV %s candidate=%s prior=%s" % (mid, "KILLED" if cand else "survived", ",".join(by) or "-"))
        if args.fixture not in fixtures:
            print("PRISTINE FAIL FIXTURE-ABSENT %s at %s" % (args.fixture, args.rev))
        print("SUMMARY mutants=%d killed=%d survived=%d pristine=%s prior=%d/8 old_killed=%d equiv=%d "
              "equiv_killed=%d anchors=%s cases=%d tool_sha=%s" % (
                  len(MUTANTS), killed_n, len(MUTANTS) - killed_n, "ok" if pristine_ok else "FAIL",
                  prior_ok, old_killed, len(EQUIV), equiv_killed, anchors, cases,
                  hashlib.sha256(tool_b).hexdigest()[:12]))
        met = (len(MUTANTS) == 13 and killed_n == 13 and pristine_ok and prior_ok == 8 and old_killed == 0
               and len(EQUIV) == 6 and equiv_killed == 0 and anchors == "ok")
        return 0 if met else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
