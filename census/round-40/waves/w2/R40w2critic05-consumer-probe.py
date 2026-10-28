#!/usr/bin/env python3
"""R40w2critic05 — re-runnable probe for the C2 consumer arm (L6) at the landed and base revisions.

Read-only against the lane: every committed byte is read with `git archive` / `git show`; all writes go
under --scratch (explicit; no /tmp). Nothing is committed, staged, or written into the lane.

Usage:
  python3 -B .ufo/waves/round-40/w2/R40w2critic05-consumer-probe.py \
      --lane /home/vgpnk/Projects/shokunin/souji-shokunin \
      --landed 128e412b0ced3c243dc27c3dd3332054a611bc2e \
      --base 0242085909fb6a4ee041c5443d76316ac6d59d4b \
      --head 549d9ec53a1f5932337ff14438fcd22b0621828d \
      --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2critic05/run

Sections:
  S1  each of the seven consumer fixtures, four arms (fixture rev x tool rev), per-case PASS/FAIL
  S2  mutant tools (scratch copies) against the landed consumer fixtures: does L6 see a lost case?
  S3  control-blindness: consumer fixtures with their own control forced to fail; does the L6 green
      predicate (pass == cases and fail == 0) still hold?
  S4  the C2 counter as committed at --landed, at --head, and at --landed with a scratch-only module-name
      shim (the committed analyser copied under the name the counter imports)
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

CONS = [
    ("r38-drift-record", "tests/fixtures/r38-drift-record.py", "tools/souji-worktree-drift.py"),
    ("r36-worktree-drift", "tests/fixtures/r36-worktree-drift.py", "tools/souji-worktree-drift.py"),
    ("r38-drift-write-envelope", "tests/fixtures/r38-drift-write-envelope.py", "tools/souji-worktree-drift.py"),
    ("r39-drift-record-rules", "tests/fixtures/r39-drift-record-rules.py", "tools/souji-worktree-drift.py"),
    ("r37-citation-reconcile", "tests/fixtures/r37-citation-reconcile.py", "tools/souji-citation-reconcile.py"),
    ("r38-citation-commit", "tests/fixtures/r38-citation-commit.py", "tools/souji-citation-reconcile.py"),
    ("r39-citation-rev", "tests/fixtures/r39-citation-rev.py", "tools/souji-citation-reconcile.py"),
]
MUTANTS = [
    ("MD1-empty-off", "tools/souji-worktree-drift.py", 'if not rows:\n', 'if False:\n'),
    ("MD2-total-repos-off", "tools/souji-worktree-drift.py", 'if total["repos"] != len(rows):', 'if False:'),
    ("MD3-outside-root-off", "tools/souji-worktree-drift.py",
     'if not inside:\n            raise Refusal("RECORD-OUTSIDE-ROOT: %s resolves', 'if False:\n            raise Refusal("RECORD-OUTSIDE-ROOT: %s resolves'),
    ("MC1-rev-unresolved-off", "tools/souji-citation-reconcile.py",
     'if git_proc(root, ["cat-file", "-e", args.rev + "^{commit}"]).returncode != 0:', 'if False:'),
    ("MC2-ancestor-error-as-no", "tools/souji-citation-reconcile.py", '    return "error"\n', '    return "no"\n'),
]
FORCED = [
    ("r36-worktree-drift", "tests/fixtures/r36-worktree-drift.py", "control_ok = not replicated", "control_ok = False",
     "tools/souji-worktree-drift.py"),
    ("r37-citation-reconcile", "tests/fixtures/r37-citation-reconcile.py", "control_ok = not control_replicated",
     "control_ok = False", "tools/souji-citation-reconcile.py"),
]
CASE = re.compile(r"^(\S+?)=(PASS|FAIL)\s*$", re.M)
SUMMARY = re.compile(r"SUMMARY cases=(\d+) pass=(\d+) fail=(\d+)")
ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def git_export(lane, rev, dest):
    os.makedirs(dest, exist_ok=True)
    arch = subprocess.run(["git", "-C", lane, "archive", rev, "--", "tools", "tests", "census", "corpus"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, check=False)
    if arch.returncode != 0:
        raise SystemExit("git archive %s failed: %s" % (rev, arch.stderr.decode()))
    subprocess.run(["tar", "-x", "-C", dest], input=arch.stdout, check=True)
    return dest


def run(cmd, work, cwd):
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    env = dict(ENV, TMPDIR=work)
    proc = subprocess.run(cmd + ["--work", work], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, timeout=900, env=env, check=False)
    shutil.rmtree(work, ignore_errors=True)
    return proc


def cases_of(stdout):
    return dict(CASE.findall(stdout))


def s1(trees, scratch):
    print("S1 consumer arms: A=fixture@landed tool@landed, B=fixture@landed tool@base, "
          "C=fixture@base tool@base, D=fixture@base tool@landed")
    results = {}
    for name, fx, tool in CONS:
        arms = {}
        for label, fxt, tlt in [("A", "landed", "landed"), ("B", "landed", "base"), ("C", "base", "base"),
                                ("D", "base", "landed")]:
            proc = run(["python3", "-B", os.path.join(trees[fxt], fx), "--tool", os.path.join(trees[tlt], tool)],
                       os.path.join(scratch, "work", "s1-%s-%s" % (name, label)), trees[fxt])
            arms[label] = (proc.returncode, cases_of(proc.stdout),
                           [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY")])
        A, B, C, D = (arms[k] for k in "ABCD")
        lost_vs_base = sorted(k for k, v in C[1].items() if v == "PASS" and A[1].get(k) != "PASS")
        lost_tool_swap = sorted(k for k, v in A[1].items() if v == "PASS" and B[1].get(k) != "PASS")
        print("%s rc=%s/%s/%s/%s cases=%d pass(A)=%d pass(C)=%d LOST_A_vs_C=%s LOST_A_vs_B=%s summary(A)=%s" % (
            name, A[0], B[0], C[0], D[0], len(A[1]), sum(v == "PASS" for v in A[1].values()),
            sum(v == "PASS" for v in C[1].values()), lost_vs_base, lost_tool_swap, A[2][-1:] or "NO-SUMMARY"))
        results[name] = arms
    return results


def s2(trees, scratch):
    print("S2 mutant tools (scratch copies of the landed tool) against the landed fixtures")
    for mname, rel, old, new in MUTANTS:
        mdir = os.path.join(scratch, "mut", mname)
        shutil.rmtree(mdir, ignore_errors=True)
        os.makedirs(os.path.join(mdir, os.path.dirname(rel)))
        src = open(os.path.join(trees["landed"], rel), encoding="utf-8").read()
        assert src.count(old) == 1, (mname, src.count(old))
        mpath = os.path.join(mdir, rel)
        open(mpath, "w", encoding="utf-8").write(src.replace(old, new))
        for name, fx, tool in CONS:
            if tool != rel:
                continue
            land = run(["python3", "-B", os.path.join(trees["landed"], fx), "--tool",
                        os.path.join(trees["landed"], tool)], os.path.join(scratch, "work", "s2a-%s-%s" % (mname, name)),
                       trees["landed"])
            mut = run(["python3", "-B", os.path.join(trees["landed"], fx), "--tool", mpath],
                      os.path.join(scratch, "work", "s2b-%s-%s" % (mname, name)), trees["landed"])
            c0, c1 = cases_of(land.stdout), cases_of(mut.stdout)
            lost = sorted(k for k, v in c0.items() if v == "PASS" and c1.get(k) != "PASS")
            gained = sorted(k for k, v in c1.items() if v == "PASS" and c0.get(k) != "PASS")
            l6_flags = (sum(v == "PASS" for v in c1.values()) < sum(v == "PASS" for v in c0.values()))
            print("%s %s landed rc=%d pass=%d/%d | mutant rc=%d pass=%d/%d | LOST=%s GAINED=%s | L6 would flag=%s" % (
                mname, name, land.returncode, sum(v == "PASS" for v in c0.values()), len(c0),
                mut.returncode, sum(v == "PASS" for v in c1.values()), len(c1), lost, gained, l6_flags))


def s3(trees, scratch):
    print("S3 control-blindness: consumer fixture with its own control forced to FAIL")
    for name, fx, old, new, tool in FORCED:
        src = open(os.path.join(trees["landed"], fx), encoding="utf-8").read()
        assert src.count(old) == 1, (name, src.count(old))
        cdir = os.path.join(scratch, "forced")
        os.makedirs(cdir, exist_ok=True)
        fpath = os.path.join(cdir, name + ".py")
        open(fpath, "w", encoding="utf-8").write(src.replace(old, new))
        proc = run(["python3", "-B", fpath, "--tool", os.path.join(trees["landed"], tool)],
                   os.path.join(scratch, "work", "s3-%s" % name), cdir)
        m = SUMMARY.search(proc.stdout)
        cases, passed, failed = (int(x) for x in m.groups()) if m else (None, None, None)
        green = (cases is not None and cases == passed and failed == 0)
        print("%s fixture rc=%d %s | counter L6 green predicate=%s" % (
            name, proc.returncode, [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY")], green))


def s4(lane, landed, base, head, trees, scratch):
    print("S4 the C2 counter")
    os.makedirs(os.path.join(scratch, "c2"), exist_ok=True)
    counter = os.path.join(trees["landed"], "census/round-40/c2-counter.py")
    proc = subprocess.run(["python3", "-B", counter, "--root", lane, "--rev", landed, "--base-rev", base,
                           "--scratch", os.path.join(scratch, "c2")], cwd=scratch, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, env=dict(ENV, TMPDIR=scratch), check=False)
    print("committed@landed rc=%d stdout=%r stderr_last=%r" % (
        proc.returncode, proc.stdout.strip()[-300:], proc.stderr.strip().splitlines()[-1:] ))
    shim = os.path.join(scratch, "shim", "census", "round-40")
    os.makedirs(shim, exist_ok=True)
    shutil.copy(counter, shim)
    shutil.copy(os.path.join(trees["landed"], "census/round-40/docstring-classes.py"),
                os.path.join(shim, "docstring_classes.py"))
    proc = subprocess.run(["python3", "-B", os.path.join(shim, "c2-counter.py"), "--root", lane, "--rev", landed,
                           "--base-rev", base, "--scratch", os.path.join(scratch, "c2")], cwd=scratch,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                          env=dict(ENV, TMPDIR=scratch), check=False)
    print("landed+module-shim rc=%d" % proc.returncode)
    print(proc.stdout.rstrip())
    if head:
        htree = git_export(lane, head, os.path.join(scratch, "head"))
        proc = subprocess.run(["python3", "-B", os.path.join(htree, "census/round-40/c2-counter.py"), "--root", lane,
                               "--rev", head, "--base-rev", base, "--scratch", os.path.join(scratch, "c2")],
                              cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              env=dict(ENV, TMPDIR=scratch), check=False)
        print("committed@head rc=%d" % proc.returncode)
        print(proc.stdout.rstrip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--landed", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head")
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--only", default="s1,s2,s3,s4")
    args = ap.parse_args()
    scratch = os.path.abspath(args.scratch)
    os.makedirs(scratch, exist_ok=True)
    trees = {"landed": git_export(args.lane, args.landed, os.path.join(scratch, "landed")),
             "base": git_export(args.lane, args.base, os.path.join(scratch, "base"))}
    steps = set(args.only.split(","))
    if "s1" in steps:
        s1(trees, scratch)
    if "s2" in steps:
        s2(trees, scratch)
    if "s3" in steps:
        s3(trees, scratch)
    if "s4" in steps:
        s4(args.lane, args.landed, args.base, args.head, trees, scratch)
    return 0


if __name__ == "__main__":
    sys.exit(main())
