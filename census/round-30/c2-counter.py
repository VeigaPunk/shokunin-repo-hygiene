#!/usr/bin/env python3
"""r30 C2 operability counter (frozen at the r30 preregistration).

Measures whether `tools/souji-landing-gate.py`, as committed at REV, evaluates a round's committed
reports and stops reporting template/capture-mapped pointers as dangling. Everything executed is
taken from committed bytes (a private `git clone --no-local`, origin removed, checked out at REV and at
BASE) in a scratch directory; the lane working tree is never read or written.

Legs (printed, then one SUMMARY line):
  GATE      tool@REV --root <root> --rev REV --round 29 --fleet-root <fleet>:
            reports=<checked_reports> cne=<1 if a COULD-NOT-EVALUATE line> dangling=<LG-DANGLING-PTR lines>
            other=<other LG-* finding lines>
  FIXTURE   tests/fixtures/r30-landing-gate-discovery.py@REV --tool tool@REV: last line
            `cases=N pass=M control=X`; ok iff N==M, N>=7, X==FALSE-GREEN-REJECTED and the lines
            `CASE D1 PASS` .. `CASE D7 PASS` are all present
  REDARM    the same fixture with --tool <tool@BASE>: ok iff it reports pass < cases (base tool discriminated)
  REGRESS   `python3 -B tools/souji-landing-gate.py --selftest` and `python3 -B tests/fixtures/r16-landing-gate.py`,
            each run inside the exported tree of BASE and of REV: ok iff (rc, last digit-bearing line) are equal
SUMMARY reports=R cne=C dangling=D other=O fixture=<ok|fail> redarm=<ok|fail> regress=<same|differs> rev=REV
Exit 0 iff reports>0, cne=0, dangling=0 and the three legs are ok; 1 otherwise; 2 could-not-evaluate.
The frozen target (preregistration) is `reports=86 cne=0 dangling=0 fixture=ok redarm=ok regress=same`.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

FULL = re.compile(r"[0-9a-f]{40}")


def cne(m):
    print("COULD-NOT-EVALUATE " + m)
    sys.exit(2)


def export(root, rev, dest):
    # private clone (origin removed) checked out at rev: the r16 fixture needs a git worktree as its lane root
    steps = [["git", "clone", "-q", "--no-local", "--no-checkout", root, dest],
             ["git", "-C", dest, "remote", "remove", "origin"],
             ["git", "-C", dest, "-c", "core.hooksPath=/dev/null", "checkout", "-qf", "--detach", rev]]
    for s in steps:
        if subprocess.run(s, capture_output=True).returncode:
            cne(f"export of {rev} failed at {' '.join(s[:4])}")
    if subprocess.run(["git", "-C", dest, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() != dest:
        cne("export toplevel mismatch")


def run(argv, cwd, tmp, timeout=900):
    env = dict(os.environ, TMPDIR=tmp)
    try:
        p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"


def lastnum(out, scratch):
    out = out.replace(scratch, "<TMP>")
    out = re.sub(r"(?:/var)?/tmp/[^\s'\"`:,)]+", "<TMP>", out)
    out = re.sub(r"\b[0-9a-f]{12,}\b", "<HEX>", out)
    for l in reversed(out.splitlines()):
        if l.strip() and re.search(r"\d", l):
            return l.strip()
    return "NONE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r30/c2-counter")
    a = ap.parse_args()
    for v in (a.rev, a.base):
        if not FULL.fullmatch(v):
            cne("revisions must be full 40-hex")
    root = os.path.abspath(a.root)
    os.makedirs(a.scratch, exist_ok=True)
    w = tempfile.mkdtemp(prefix="c2.", dir=a.scratch)
    try:
        tr, tb = os.path.join(w, "rev"), os.path.join(w, "base")
        export(root, a.rev, tr)
        export(root, a.base, tb)
        tmp = os.path.join(w, "tmp")
        os.makedirs(tmp)
        rc, out = run([sys.executable, "-B", os.path.join(tr, "tools/souji-landing-gate.py"), "--root", root, "--rev", a.rev,
                       "--round", "29", "--fleet-root", a.fleet_root], w, tmp)
        m = re.search(r"checked_reports=(\d+)", out)
        reports = int(m.group(1)) if m else -1
        cnef = int(any(l.startswith("COULD-NOT-EVALUATE") for l in out.splitlines()))
        dangling = sum(1 for l in out.splitlines() if l.startswith("LG-DANGLING-PTR"))
        other = sum(1 for l in out.splitlines() if l.startswith("LG-") and not l.startswith("LG-DANGLING-PTR"))
        print(f"GATE rc={rc} reports={reports} cne={cnef} dangling={dangling} other={other}")
        fx = os.path.join(tr, "tests/fixtures/r30-landing-gate-discovery.py")
        if os.path.isfile(fx):
            frc, fout = run([sys.executable, "-B", fx, "--tool", os.path.join(tr, "tools/souji-landing-gate.py")], w, tmp)
            fl = lastnum(fout, w)
            fm = re.search(r"cases=(\d+) pass=(\d+) control=(\S+)", fl)
            cases_ok = all(re.search(rf"^CASE D{i} PASS\b", fout, re.M) for i in range(1, 8))
            fok = bool(fm) and fm.group(1) == fm.group(2) and int(fm.group(1)) >= 7 and fm.group(3) == "FALSE-GREEN-REJECTED" and cases_ok
            brc, bout = run([sys.executable, "-B", fx, "--tool", os.path.join(tb, "tools/souji-landing-gate.py")], w, tmp)
            bl = lastnum(bout, w)
            bm = re.search(r"cases=(\d+) pass=(\d+)", bl)
            rok = bool(bm) and int(bm.group(2)) < int(bm.group(1))
            print(f"FIXTURE rc={frc} line={fl!r} d1_d7_pass={cases_ok} {'ok' if fok else 'fail'}")
            print(f"REDARM rc={brc} line={bl!r} {'ok' if rok else 'fail'}")
        else:
            fok = rok = False
            print("FIXTURE absent fail")
            print("REDARM absent fail")
        same = True
        for argv in (["tools/souji-landing-gate.py", "--selftest"], ["tests/fixtures/r16-landing-gate.py"]):
            r1 = run([sys.executable, "-B", *argv], tb, tmp)
            r2 = run([sys.executable, "-B", *argv], tr, tmp)
            s1, s2 = (r1[0], lastnum(r1[1], w)), (r2[0], lastnum(r2[1], w))
            print(f"REGRESS {argv[0]} base={s1} rev={s2} {'same' if s1 == s2 else 'differs'}")
            same = same and s1 == s2
        print(f"SUMMARY reports={reports} cne={cnef} dangling={dangling} other={other} fixture={'ok' if fok else 'fail'} "
              f"redarm={'ok' if rok else 'fail'} regress={'same' if same else 'differs'} rev={a.rev}")
        return 0 if reports > 0 and cnef == 0 and dangling == 0 and fok and rok and same else 1
    finally:
        shutil.rmtree(w, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
