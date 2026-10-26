#!/usr/bin/env python3
"""r31 C2 operability counter (frozen at the r31 preregistration): landing-gate reading precision.

Measures whether `tools/souji-landing-gate.py`, as committed at REV, reads the lane's committed record as
written: the union of a round's force-added `.ufo/waves/round-N/` reports and its committed capture
`census/round-N/waves/`, every `## Seat-reported failures` section of a lesson (append-only carries), and
pointer tokens without the tokenizer false positives found at the r31 base (ellipsis placeholders, line
ranges, `.captured` capture names, `:text` suffixes, printf templates, prose slash alternations), while
still flagging real dangling pointers and real uncarried failures. Everything executed comes from
committed bytes (private `git clone --no-local`, origin removed, at REV and at BASE) under --scratch;
the lane working tree is never read or written.

Legs (printed, then one SUMMARY line):
  LANE      tool@REV --root <root> --rev BASE --round r --fleet-root <fleet>, r = 13..30 (content frozen at
            BASE, so other claims' content changes cannot move this leg):
              fp      = LG-DANGLING-PTR lines whose (round, token-path, source) is not in REAL
              real    = REAL members still reported (REAL is the frozen pair below; token-path is the
                        printed path with any `:<line-spec>` suffix removed)
              cne     = rounds printing COULD-NOT-EVALUATE
              r26     = checked_reports for round 26 (466 force-added + 29 capture-only = 495 distinct paths, `git ls-tree -r -z`)
  FIXTURE   tests/fixtures/r31-landing-gate-precision.py@REV --tool tool@REV: ok iff every `CASE G1..G10
            PASS` line is present and the last line is `cases=N pass=N control=FALSE-GREEN-REJECTED`, N>=10
  REDARM    the same fixture with --tool tool@BASE: ok iff G1 G3 G4 G5 G6 G7 G8 print FAIL and G2 G9 G10
            print PASS (each base defect discriminated by its own case; controls green on the base tool)
  REGRESS   inside the exports of BASE and of REV, each with its own tool: `tools/souji-landing-gate.py
            --selftest`, `tests/fixtures/r16-landing-gate.py`, `tests/fixtures/r30-landing-gate-discovery.py
            --tool tools/souji-landing-gate.py`, `tests/fixtures/r19-carry-wrap.py`: ok iff (rc, last
            digit-bearing line) are equal for all four
SUMMARY fp=F real=R cne=C r26=N fixture=<ok|fail> redarm=<ok|fail> regress=<same|differs> rev=REV
Exit 0 iff fp=0, real=2, cne=0, r26=495 and the three legs are ok; 1 otherwise; 2 could-not-evaluate.
Frozen target (preregistration): `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same`.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

FULL = re.compile(r"[0-9a-f]{40}")
ROUNDS = range(13, 31)
REAL = {
    (23, "census/round-3/garbage-census.out", "corpus/lessons/round-23-verifier-spotcheck.md:28"),
    (23, "tools/__pycache__/", "corpus/lessons/round-23.md:69"),
}
RED = ("G1", "G3", "G4", "G5", "G6", "G7", "G8")
GREEN = ("G2", "G9", "G10")


def cne(m):
    print("COULD-NOT-EVALUATE " + m)
    sys.exit(2)


def export(root, rev, dest):
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
        return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT", ""


def lastnum(out, scratch):
    out = out.replace(scratch, "<TMP>")
    out = re.sub(r"(?:/var)?/tmp/[^\s'\"`:,)]+", "<TMP>", out)
    out = re.sub(r"/fast/scratch/[^\s'\"`:,)]+", "<TMP>", out)
    out = re.sub(r"\b[0-9a-f]{12,}\b", "<HEX>", out)
    for l in reversed(out.splitlines()):
        if l.strip() and re.search(r"\d", l):
            return " ".join(l.split())
    return "NONE"


def strip_linespec(tok):
    return re.sub(r":\d+(?:\s*[-\u2013\u2014,]\s*\d+)*$", "", tok)


def case_verdicts(out):
    return dict(re.findall(r"^CASE (G\d+) (PASS|FAIL)\b", out, re.M))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r31/c2-counter")
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
        tool_r, tool_b = os.path.join(tr, "tools/souji-landing-gate.py"), os.path.join(tb, "tools/souji-landing-gate.py")
        fp, real_seen, cnec, r26 = 0, set(), 0, -1
        for r in ROUNDS:
            rc, out, err = run([sys.executable, "-B", tool_r, "--root", root, "--rev", a.base, "--round", str(r),
                                "--fleet-root", a.fleet_root], w, tmp)
            if "COULD-NOT-EVALUATE" in out + err:
                cnec += 1
            m = re.search(r"checked_reports=(\d+)", out)
            if r == 26:
                r26 = int(m.group(1)) if m else -1
            for l in out.splitlines():
                if not l.startswith("LG-DANGLING-PTR\t"):
                    continue
                f = l.split("\t")
                tok = strip_linespec(f[1]) if len(f) > 1 else ""
                src = re.match(r"(\S+:\d+)", f[2]).group(1) if len(f) > 2 and re.match(r"\S+:\d+", f[2]) else ""
                key = (r, tok, src)
                if key in REAL:
                    real_seen.add(key)
                else:
                    fp += 1
                    print(f"LANE-FP round={r} token={f[1] if len(f) > 1 else ''} source={src}")
            print(f"LANE round={r} rc={rc} reports={m.group(1) if m else '-'} cne={int('COULD-NOT-EVALUATE' in out + err)}")
        for key in sorted(REAL):
            print(f"LANE-REAL round={key[0]} token={key[1]} source={key[2]} {'reported' if key in real_seen else 'MISSING'}")
        fx = os.path.join(tr, "tests/fixtures/r31-landing-gate-precision.py")
        if os.path.isfile(fx):
            frc, fout, ferr = run([sys.executable, "-B", fx, "--tool", tool_r], w, tmp)
            fl = lastnum(fout, w)
            fm = re.search(r"cases=(\d+) pass=(\d+) control=(\S+)", fl)
            fv = case_verdicts(fout)
            all_g = all(fv.get(f"G{i}") == "PASS" for i in range(1, 11))
            fok = bool(fm) and fm.group(1) == fm.group(2) and int(fm.group(1)) >= 10 and fm.group(3) == "FALSE-GREEN-REJECTED" and all_g
            brc, bout, berr = run([sys.executable, "-B", fx, "--tool", tool_b], w, tmp)
            bv = case_verdicts(bout)
            rok = all(bv.get(c) == "FAIL" for c in RED) and all(bv.get(c) == "PASS" for c in GREEN)
            print(f"FIXTURE rc={frc} line={fl!r} g1_g10_pass={all_g} {'ok' if fok else 'fail'}")
            print(f"REDARM rc={brc} base_cases={sorted(bv.items(), key=lambda x: int(x[0][1:]))} {'ok' if rok else 'fail'}")
        else:
            fok = rok = False
            print("FIXTURE absent fail")
            print("REDARM absent fail")
        same = True
        for argv in (["tools/souji-landing-gate.py", "--selftest"], ["tests/fixtures/r16-landing-gate.py"],
                     ["tests/fixtures/r30-landing-gate-discovery.py", "--tool", "tools/souji-landing-gate.py"],
                     ["tests/fixtures/r19-carry-wrap.py"]):
            r1 = run([sys.executable, "-B", *argv], tb, tmp)
            r2 = run([sys.executable, "-B", *argv], tr, tmp)
            s1, s2 = (r1[0], lastnum(r1[1] or r1[2], w)), (r2[0], lastnum(r2[1] or r2[2], w))
            print(f"REGRESS {argv[0]} base={s1} rev={s2} {'same' if s1 == s2 else 'differs'}")
            same = same and s1 == s2
        real = len(real_seen)
        print(f"SUMMARY fp={fp} real={real} cne={cnec} r26={r26} fixture={'ok' if fok else 'fail'} "
              f"redarm={'ok' if rok else 'fail'} regress={'same' if same else 'differs'} rev={a.rev}")
        return 0 if fp == 0 and real == 2 and cnec == 0 and r26 == 495 and fok and rok and same else 1
    finally:
        shutil.rmtree(w, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
