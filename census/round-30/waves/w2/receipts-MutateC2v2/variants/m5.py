#!/usr/bin/env python3
"""r30 C2 counter v2 — AMENDMENT A1 (stricter-only; the frozen census/round-30/c2-counter.py still runs and must
also meet its target). Written after wave-1 seat SwarmCritic25 showed a no-op gate plus a byte-recognising fixture
reaching the frozen SUMMARY (unbound `reports`, lane-authored FIXTURE/REDARM legs, last-line REGRESS, live --root).

Everything runs from private `git clone --no-local` copies (origin removed) of --root: one at REV, one at BASE.
Legs, all required:
  BIND     the REV gate, run with --root <REV clone> --rev REV --round 29 --fleet-root <fleet>, prints a `SUMMARY\t`
           line whose checked_reports equals E = number of `.md` blobs under census/round-29/waves/ at REV, and REV
           commits no `.md` under .ufo/waves/round-29/ (so the count can only come from the capture); E must be 86;
           no COULD-NOT-EVALUATE line; zero LG-DANGLING-PTR* lines
  NOCAP    the same REV gate on a scratch commit (on top of REV) that deletes census/round-29/waves/ prints
           COULD-NOT-EVALUATE (a gate that does not read the capture cannot pass BIND and NOCAP together)
  PTRARM   the same REV gate on a scratch commit that appends to corpus/QUALITY.md four backticked pointers:
           census/round-29/r30v2-absent.md (absent), .ufo/waves/round-29/w1/R30v2Absent.md (absent, no capture copy),
           census/round-%s/r30v2-template.md (template) and .ufo/waves/round-29/<an existing captured report suffix>;
           the LG-DANGLING-PTR lines naming corpus/QUALITY.md must be exactly the two absent paths
  FIXTURE  / REDARM as in v1 (tests/fixtures/r30-landing-gate-discovery.py@REV, D1-D7 PASS, control rejected;
           the BASE tool fails at least one case)
  REGRESS  full normalized stdout+stderr of `--selftest` and of tests/fixtures/r16-landing-gate.py are identical
           between the BASE clone and the REV clone (tmp paths -> <TMP>, hex runs >= 12 -> <HEX>), line by line,
           except that the free-text ` err=<message>` tail of a selftest `CASE` line is dropped (case name, verdict,
           exit, ids, paths and fleet still compared): C2 rewords the no-reports error message, nothing else
SUMMARY-V2 reports=R expected=E cne=C dangling=D bind=.. nocap=.. ptrarm=.. fixture=.. redarm=.. regress_full=.. rev=REV
Exit 0 iff every leg is ok; 1 otherwise; 2 could-not-evaluate.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

FULL = re.compile(r"[0-9a-f]{40}")
ID = ["-c", "user.name=c2v2", "-c", "user.email=c2v2@localhost", "-c", "core.hooksPath=/dev/null"]


def cne(m):
    print("COULD-NOT-EVALUATE " + m)
    sys.exit(2)


def sh(argv, **kw):
    return subprocess.run(argv, capture_output=True, **kw)


def clone(root, rev, dest):
    for s in (["git", "clone", "-q", "--no-local", "--no-checkout", root, dest],
              ["git", "-C", dest, "remote", "remove", "origin"],
              ["git", "-C", dest, *ID, "checkout", "-qf", "--detach", rev]):
        if sh(s).returncode:
            cne("clone/checkout failed: " + " ".join(s[:5]))
    if sh(["git", "-C", dest, "rev-parse", "--show-toplevel"], text=True).stdout.strip() != dest:
        cne("clone toplevel mismatch")


def run(argv, cwd, tmp, timeout=900):
    try:
        p = sh(argv, cwd=cwd, env=dict(os.environ, TMPDIR=tmp), timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"


def norm(out, scratch):
    out = out.replace(scratch, "<TMP>")
    out = re.sub(r"(?:/var)?/tmp/[^\s'\"`:,)]+", "<TMP>", out)
    out = re.sub(r"/fast/scratch/[^\s'\"`:,)]+", "<TMP>", out)
    out = re.sub(r"\b[0-9a-f]{12,}\b", "<HEX>", out)
    return out


def strip_err(out):
    return "\n".join(re.sub(r"\terr=.*$", "", l) if l.startswith("CASE\t") else l for l in out.splitlines())


def lastnum(out, scratch):
    for l in reversed(norm(out, scratch).splitlines()):
        if l.strip() and re.search(r"\d", l):
            return l.strip()
    return "NONE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r30/c2v2-counter")
    a = ap.parse_args()
    for v in (a.rev, a.base):
        if not FULL.fullmatch(v):
            cne("revisions must be full 40-hex")
    root = os.path.abspath(a.root)
    os.makedirs(a.scratch, exist_ok=True)
    w = tempfile.mkdtemp(prefix="c2v2.", dir=a.scratch)
    try:
        tr, tb, tmp = os.path.join(w, "rev"), os.path.join(w, "base"), os.path.join(w, "tmp")
        os.makedirs(tmp)
        clone(root, a.rev, tr)
        clone(root, a.base, tb)
        gate_rev = os.path.join(w, "gate-rev.py")
        shutil.copyfile(os.path.join(tr, "tools/souji-landing-gate.py"), gate_rev)

        def gate(rev):
            return run([sys.executable, "-B", gate_rev, "--root", tr, "--rev", rev, "--round", "29", "--fleet-root", a.fleet_root], w, tmp)

        names = sh(["git", "-C", tr, "ls-tree", "-r", "--name-only", a.rev], text=True).stdout.splitlines()
        expected = sum(1 for n in names if n.startswith("census/round-29/waves/") and n.endswith(".md"))
        ufo_md = sum(1 for n in names if n.startswith(".ufo/waves/round-29/") and n.endswith(".md"))
        rc, out = gate(a.rev)
        sm = [l for l in out.splitlines() if l.startswith("SUMMARY\t")]
        m = re.search(r"\tchecked_reports=(\d+)", sm[-1]) if sm else None
        reports = int(m.group(1)) if m else -1
        cnef = int(any(l.startswith("COULD-NOT-EVALUATE") for l in out.splitlines()))
        dangling = sum(1 for l in out.splitlines() if l.startswith("LG-DANGLING-PTR"))
        bind = reports == expected == 86 and ufo_md == 0 and cnef == 0 and dangling == 0
        print(f"BIND rc={rc} reports={reports} expected={expected} ufo_md={ufo_md} cne={cnef} dangling={dangling} {'ok' if bind else 'fail'}")

        # NOCAP arm
        sh(["git", "-C", tr, *ID, "rm", "-rq", "--", "census/round-29/waves"])
        sh(["git", "-C", tr, *ID, "commit", "-qm", "c2v2 nocap"])
        nocap_rev = sh(["git", "-C", tr, "rev-parse", "HEAD"], text=True).stdout.strip()
        rc2, out2 = gate(nocap_rev)
        nocap = nocap_rev != a.rev and any(l.startswith("COULD-NOT-EVALUATE") for l in out2.splitlines())
        print(f"NOCAP rc={rc2} {'ok' if nocap else 'fail'}")

        # PTRARM
        sh(["git", "-C", tr, *ID, "checkout", "-qf", "--detach", a.rev])
        existing = sorted(n for n in names if n.startswith("census/round-29/waves/w1/") and n.endswith(".md"))
        if not existing:
            ptrarm = False
            print("PTRARM no captured report to cite fail")
        else:
            real = ".ufo/waves/round-29/" + existing[0][len("census/round-29/waves/"):]
            with open(os.path.join(tr, "corpus/QUALITY.md"), "a") as fh:
                fh.write("\nr30 c2v2 arm: `census/round-29/r30v2-absent.md` `.ufo/waves/round-29/w1/R30v2Absent.md` "
                         f"`census/round-%s/r30v2-template.md` `{real}`\n")
            sh(["git", "-C", tr, *ID, "commit", "-qam", "c2v2 ptrarm"])
            ptr_rev = sh(["git", "-C", tr, "rev-parse", "HEAD"], text=True).stdout.strip()
            rc3, out3 = gate(ptr_rev)
            flagged = sorted(l.split("\t")[1] for l in out3.splitlines()
                             if l.startswith("LG-DANGLING-PTR") and "corpus/QUALITY.md" in l)
            want = sorted(["census/round-29/r30v2-absent.md", ".ufo/waves/round-29/w1/R30v2Absent.md"])
            ptrarm = ptr_rev != a.rev and flagged == want
            print(f"PTRARM rc={rc3} flagged={flagged} real_pointer={real} {'ok' if ptrarm else 'fail'}")
        sh(["git", "-C", tr, *ID, "checkout", "-qf", "--detach", a.rev])

        fx = os.path.join(tr, "tests/fixtures/r30-landing-gate-discovery.py")
        if os.path.isfile(fx):
            frc, fout = run([sys.executable, "-B", fx, "--tool", gate_rev], w, tmp)
            fl = lastnum(fout, w)
            fm = re.search(r"cases=(\d+) pass=(\d+) control=(\S+)", fl)
            cases_ok = all(re.search(rf"^CASE D{i} PASS\b", fout, re.M) for i in range(1, 8))
            fok = bool(fm) and fm.group(1) == fm.group(2) and int(fm.group(1)) >= 7 and fm.group(3) == "FALSE-GREEN-REJECTED" and cases_ok
            brc, bout = run([sys.executable, "-B", fx, "--tool", os.path.join(tb, "tools/souji-landing-gate.py")], w, tmp)
            bm = re.search(r"cases=(\d+) pass=(\d+)", lastnum(bout, w))
            rok = bool(bm) and int(bm.group(2)) < int(bm.group(1))
        else:
            fok = rok = False
        print(f"FIXTURE {'ok' if fok else 'fail'}")
        print(f"REDARM {'ok' if rok else 'fail'}")

        same = True
        for argv in (["tools/souji-landing-gate.py", "--selftest"], ["tests/fixtures/r16-landing-gate.py"]):
            r1 = run([sys.executable, "-B", *argv], tb, tmp)
            r2 = run([sys.executable, "-B", *argv], tr, tmp)
            s1, s2 = (r1[0], strip_err(norm(r1[1], w))), (r2[0], strip_err(norm(r2[1], w)))
            eq = (s1[1].splitlines() or [""])[-1] == (s2[1].splitlines() or [""])[-1]
            print(f"REGRESS-FULL {argv[0]} rc={r1[0]}/{r2[0]} lines={len(s1[1].splitlines())}/{len(s2[1].splitlines())} {'same' if eq else 'differs'}")
            same = same and eq
        ok = bind and nocap and ptrarm and fok and rok and same
        print(f"SUMMARY-V2 reports={reports} expected={expected} cne={cnef} dangling={dangling} bind={'ok' if bind else 'fail'} "
              f"nocap={'ok' if nocap else 'fail'} ptrarm={'ok' if ptrarm else 'fail'} fixture={'ok' if fok else 'fail'} "
              f"redarm={'ok' if rok else 'fail'} regress_full={'same' if same else 'differs'} rev={a.rev}")
        return 0 if ok else 1
    finally:
        shutil.rmtree(w, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
