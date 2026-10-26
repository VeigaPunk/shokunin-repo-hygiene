#!/usr/bin/env python3
"""SwarmMutationTester25 — mutation-test the r30 C2 gate change.

Detector (bounded, identical for pristine / mutated / restored bytes):
  FIXTURE  tests/fixtures/r30-landing-gate-discovery.py --tool <gate>  (D1-D7 + control)
  NOCAP    c2-counter-v2 leg: scratch commit deleting census/round-29/waves/
           -> gate must print COULD-NOT-EVALUATE
  PTRARM   c2-counter-v2 leg: scratch commit appending 4 pointers to
           corpus/QUALITY.md -> LG-DANGLING-PTR lines naming it must be exactly
           the two absent paths
Auxiliary (recorded, not part of verdict): LG-DANGLING-PTR lines NOT naming
corpus/QUALITY.md in the PTRARM run (lane-level dangling, BIND's dangling=0).
"""
import hashlib
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TIP = "9dcd367655fc28ba73d679a0e2cadaff96d2bcb8"
FLEET = "/home/vgpnk/Projects/shokunin"
D = "/fast/scratch/hyaku/souji-r30/MutateGate"
C = os.path.join(D, "c")
PRISTINE = os.path.join(C, "tools/souji-landing-gate.py")
FIXT = os.path.join(C, "tests/fixtures/r30-landing-gate-discovery.py")
TMP = os.path.join(D, "tmp")
MUT = os.path.join(D, "mutants")
os.makedirs(TMP, exist_ok=True)
os.makedirs(MUT, exist_ok=True)

FALLBACK_REPORT = '''    if not reports:
        # The wave dir is gitignored, so at a revision that never committed it
        # the report set is its capture (tools/souji-wave-evidence-capture.sh),
        # which holds the same relative paths. When both are committed the
        # wave dir alone is read, so no report is ever counted twice.
        reports = sorted(
            p for p in tree if p.startswith(capture_prefix) and p.endswith(".md")
        )
    if not reports:
'''

WAVE_SORT = '''    reports = sorted(
        p for p in tree if p.startswith(wave_prefix) and p.endswith(".md")
    )
'''

CAPTURE_SORT = '''        reports = sorted(
            p for p in tree if p.startswith(capture_prefix) and p.endswith(".md")
        )
'''

SKIP_BLOCK = '''            if (
                TEMPLATE_POINTER_RE.search(part)
                or part.rstrip("/").endswith("round-")
            ):
                continue
'''

CAPTURE_RESOLVE = '''            capture_path = _capture_pointer_path(path)
            if capture_path is not None and _path_exists_in_tree(
                capture_path, tree_paths
            ):
                continue
'''

CAPTURE_FN_TAIL = '''    return "census/%s/waves%s" % (match.group(1), match.group(2) or "")
'''

CAPTURE_FN_DEF = '''def _capture_pointer_path(path):
'''

ERR_NEW = '''        raise EvalError(
            "no .md reports under %s or %s at %s"
            % (wave_prefix, capture_prefix, rev)
        )
'''

ERR_OLD = '''        raise EvalError("no .md reports under %s at %s" % (wave_prefix, rev))
'''

MUTANTS = {
    "m01-drop-capture-fallback-reports": [
        (FALLBACK_REPORT, "    if not reports:\n"),
    ],
    "m02-count-capture-and-wave": [
        (WAVE_SORT + FALLBACK_REPORT,
         '''    reports = sorted(
        p for p in tree if p.startswith(wave_prefix) and p.endswith(".md")
    ) + sorted(
        p for p in tree if p.startswith(capture_prefix) and p.endswith(".md")
    )
    if not reports:
'''),
    ],
    "m03-fleet-root-disk": [
        (CAPTURE_RESOLVE,
         '''            capture_path = _capture_pointer_path(path)
            if capture_path is not None and fleet_root is not None and os.path.exists(
                os.path.join(fleet_root, capture_path)
            ):
                continue
'''),
    ],
    "m04-template-regex-dropped": [
        (SKIP_BLOCK,
         '''            if part.rstrip("/").endswith("round-"):
                continue
'''),
    ],
    "m05-round-cut-dropped": [
        (SKIP_BLOCK,
         '''            if TEMPLATE_POINTER_RE.search(part):
                continue
'''),
    ],
    "m06-skip-any-round-token": [
        (SKIP_BLOCK,
         '''            if (
                TEMPLATE_POINTER_RE.search(part)
                or "round-" in part
            ):
                continue
'''),
    ],
    "m07-capture-map-no-suffix": [
        (CAPTURE_FN_TAIL, '''    return "census/%s/waves" % match.group(1)
'''),
    ],
    "m08-error-message-reverted": [
        (ERR_NEW, ERR_OLD),
    ],
    "m09-drop-capture-fallback-pointers": [
        (CAPTURE_RESOLVE, "            capture_path = _capture_pointer_path(path)\n"),
    ],
    "m10-map-to-evaluated-round": [
        (CAPTURE_FN_DEF, "def _capture_pointer_path(path, round_no=None):\n"),
        (CAPTURE_FN_TAIL,
         '''    if round_no is not None:
        return "census/round-%d/waves%s" % (round_no, match.group(2) or "")
    return "census/%s/waves%s" % (match.group(1), match.group(2) or "")
'''),
        ("            capture_path = _capture_pointer_path(path)\n",
         "            capture_path = _capture_pointer_path(path, round_no)\n"),
    ],
}


def gen_mutants():
    with open(PRISTINE, "rb") as fh:
        src = fh.read().decode("utf-8")
    paths = {}
    for name, repls in MUTANTS.items():
        out = src
        for old, new in repls:
            n = out.count(old)
            if n != 1:
                raise SystemExit("mutant %s: snippet occurs %d times, want 1:\n%r"
                                 % (name, n, old[:80]))
            out = out.replace(old, new)
        dest = os.path.join(MUT, name + ".py")
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(out)
        py_compile.compile(dest, doraise=True)
        if out == src:
            raise SystemExit("mutant %s is a no-op" % name)
        paths[name] = dest
    return paths


def sh(argv, env=None, timeout=900, cwd=None):
    p = subprocess.run(argv, capture_output=True, env=env, timeout=timeout, cwd=cwd)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def gate_run(tool, root, rev):
    env = dict(os.environ, TMPDIR=TMP)
    argv = [sys.executable, "-B", tool, "--root", root, "--rev", rev,
            "--round", "29", "--fleet-root", FLEET]
    rc, out, err = sh(argv, env=env, cwd=D)
    return rc, out + err


def detector(tool):
    res = {"tool": tool}
    env = dict(os.environ, TMPDIR=TMP)
    fxrc, fxout, fxerr = sh([sys.executable, "-B", FIXT, "--tool", tool],
                            env=env, timeout=1200, cwd=D)
    lines = fxout.splitlines()
    last = lines[-1] if lines else ""
    m = re.search(r"cases=(\d+) pass=(\d+) control=(\S+)", last)
    fails = [l for l in lines if l.startswith("CASE ") and " FAIL" in l]
    res["fixture"] = {
        "rc": fxrc, "last": last, "case_fails": fails,
        "ok": bool(m) and m.group(1) == m.group(2)
        and m.group(3) == "FALSE-GREEN-REJECTED" and fxrc == 0,
    }
    w = tempfile.mkdtemp(prefix="leg.", dir=D)
    repo = os.path.join(w, "repo")
    try:
        for argv in (
            ["git", "clone", "-q", "--no-local", "--no-checkout", LANE, repo],
            ["git", "-C", repo, "remote", "remove", "origin"],
            ["git", "-C", repo, "config", "user.name", "mut25"],
            ["git", "-C", repo, "config", "user.email", "mut25@localhost"],
            ["git", "-C", repo, "config", "commit.gpgsign", "false"],
            ["git", "-C", repo, "checkout", "-qf", "--detach", TIP],
        ):
            rc, o, e = sh(argv)
            if rc:
                raise SystemExit("leg setup failed: %s: %s" % (argv[:4], e[:300]))
        # NOCAP leg
        for argv in (
            ["git", "-C", repo, "rm", "-rq", "--", "census/round-29/waves"],
            ["git", "-C", repo, "commit", "-qm", "mut nocap"],
        ):
            rc, o, e = sh(argv)
            if rc:
                raise SystemExit("nocap setup failed: %s: %s" % (argv[:4], e[:300]))
        nocap_rev = sh(["git", "-C", repo, "rev-parse", "HEAD"])[1].strip()
        rc2, out2 = gate_run(tool, repo, nocap_rev)
        cne = [l for l in out2.splitlines() if l.startswith("COULD-NOT-EVALUATE")]
        res["nocap"] = {
            "rc": rc2, "cne": cne[:1],
            "ok": nocap_rev != TIP and bool(cne),
        }
        # PTRARM leg
        sh(["git", "-C", repo, "checkout", "-qf", "--detach", TIP])
        names = sh(["git", "-C", repo, "ls-tree", "-r", "--name-only", TIP])[1].splitlines()
        existing = sorted(n for n in names
                          if n.startswith("census/round-29/waves/w1/") and n.endswith(".md"))
        if not existing:
            raise SystemExit("no captured report to cite")
        real = ".ufo/waves/round-29/" + existing[0][len("census/round-29/waves/"):]
        with open(os.path.join(repo, "corpus/QUALITY.md"), "a", encoding="utf-8") as fh:
            fh.write("\nr30 c2v2 arm: `census/round-29/r30v2-absent.md` "
                     "`.ufo/waves/round-29/w1/R30v2Absent.md` "
                     "`census/round-%s/r30v2-template.md` `" + real + "`\n")
        sh(["git", "-C", repo, "commit", "-qam", "mut ptrarm"])
        ptr_rev = sh(["git", "-C", repo, "rev-parse", "HEAD"])[1].strip()
        rc3, out3 = gate_run(tool, repo, ptr_rev)
        dang = [l for l in out3.splitlines() if l.startswith("LG-DANGLING-PTR")]
        flagged_q = sorted(l.split("\t")[1] for l in dang if "corpus/QUALITY.md" in l)
        flagged_o = sorted(l.split("\t")[1] for l in dang if "corpus/QUALITY.md" not in l)
        want = sorted(["census/round-29/r30v2-absent.md",
                       ".ufo/waves/round-29/w1/R30v2Absent.md"])
        res["ptrarm"] = {
            "rc": rc3, "flagged_quality": flagged_q, "flagged_other": flagged_o,
            "real_pointer": real,
            "ok": ptr_rev != TIP and flagged_q == want,
        }
    finally:
        shutil.rmtree(w, ignore_errors=True)
    killed_by = []
    if not res["fixture"]["ok"]:
        killed_by.append("FIXTURE")
    if not res["nocap"]["ok"]:
        killed_by.append("NOCAP")
    if not res["ptrarm"]["ok"]:
        killed_by.append("PTRARM")
    res["killed_by"] = killed_by
    res["verdict"] = "KILLED" if killed_by else "SURVIVED"
    return res


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    results = {}
    if which in ("all", "pristine"):
        results["pristine"] = detector(PRISTINE)
    if which == "mutants":
        paths = gen_mutants()
        for name in sorted(paths):
            results[name] = detector(paths[name])
    if which == "restored":
        restored = os.path.join(MUT, "restored-gate.py")
        shutil.copyfile(PRISTINE, restored)
        results["restored"] = detector(restored)
    print(json.dumps(results, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
