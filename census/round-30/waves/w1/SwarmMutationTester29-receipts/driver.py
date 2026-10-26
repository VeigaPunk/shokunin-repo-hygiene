#!/usr/bin/env python3
"""Mutation-test driver for census/round-30/c2-counter.py (scratch only).

Builds: pristine counter copy + 8 mutants (exact-replacement patches, each
asserted applied exactly once) + 3 scratch control states (junk, k2, k3) in a
private no-local clone (origin removed). Runs the matrix, saves every output.
Lane bytes are never modified.
"""
import hashlib, os, shutil, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "9420341d9a814cb6089c25fb03a4cc9b23dc0d1b"
S = "/fast/scratch/hyaku/souji-r30/MutateC2Counter"
OUT = os.path.join(S, "out")
COUNTER = "census/round-30/c2-counter.py"


def log(msg):
    print(msg, flush=True)


def sh(argv, cwd=None, check=True):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    if check and p.returncode:
        raise SystemExit(f"FAILED {argv}\n{p.stdout}\n{p.stderr}")
    return p


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---------- 1. scratch clone with three control states ----------
log("== building scratch states ==")
ST = os.path.join(S, "states")
shutil.rmtree(ST, ignore_errors=True)
os.makedirs(ST)
C = os.path.join(ST, "c")
sh(["git", "clone", "-q", "--no-local", "--no-checkout", LANE, C])
sh(["git", "-C", C, "remote", "remove", "origin"])
top = sh(["git", "-C", C, "rev-parse", "--show-toplevel"]).stdout.strip()
assert top == C, f"toplevel mismatch: {top}"
sh(["git", "-C", C, "config", "user.email", "mut@scratch.invalid"])
sh(["git", "-C", C, "config", "user.name", "MutC2 scratch"])


def branch_from_base(name):
    sh(["git", "-C", C, "checkout", "-q", "--detach", BASE])
    sh(["git", "-C", C, "checkout", "-q", "-B", name])
    return C


STUB_GATE = """#!/usr/bin/env python3
import sys
if "--selftest" in sys.argv[1:]:
    print("SELFTEST\\tpass=99\\tfail=0")
    raise SystemExit(0)
print("SUMMARY\\tfindings=0\\tchecked_reg=0\\tchecked_changed=0\\tchecked_pins=0\\tchecked_measured=0\\tchecked_markers=0\\tstatus_lines=0\\tcarry_heading=0\\tchecked_reports=86")
raise SystemExit(0)
"""


def fake_fixture(case_lines, control):
    lines = ["#!/usr/bin/env python3"]
    lines += [f'print("CASE D{i} PASS")' for i in range(1, case_lines + 1)]
    lines.append(f'print("cases=7 pass=7 control={control}")')
    return "\n".join(lines) + "\n"


def make_state(name, gate, fixture):
    branch_from_base(name)
    g = os.path.join(C, "tools/souji-landing-gate.py")
    f = os.path.join(C, "tests/fixtures/r30-landing-gate-discovery.py")
    open(g, "w").write(gate)
    if fixture is None:
        if os.path.exists(f):
            os.remove(f)
    else:
        open(f, "w").write(fixture)
    sh(["git", "-C", C, "add", "-A"])
    sh(["git", "-C", C, "commit", "-q", "-m", f"scratch {name} (mutation-test rig)"])
    rev = sh(["git", "-C", C, "rev-parse", "HEAD"]).stdout.strip()
    log(f"{name}: {rev}")
    return rev


JUNK = make_state("junk", STUB_GATE, fake_fixture(7, "FALSE-GREEN-REJECTED"))
K2 = make_state("k2-nocase", STUB_GATE, fake_fixture(0, "FALSE-GREEN-REJECTED"))
K3 = make_state("k3-accepted", STUB_GATE, fake_fixture(7, "FALSE-GREEN-ACCEPTED"))

# ---------- 2. pristine copy + mutants ----------
log("== generating mutants ==")
os.makedirs(os.path.join(S, "mutants"), exist_ok=True)
PRISTINE = os.path.join(S, "mutants", "pristine.py")
src = open(os.path.join(LANE, COUNTER)).read()
open(PRISTINE, "w").write(src)

RUN3 = 'return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")'

MUTANTS = {
    "m1-missing-fixture-ok": [
        ("            fok = rok = False\n            print(\"FIXTURE absent fail\")\n            print(\"REDARM absent fail\")",
         "            fok = rok = True\n            print(\"FIXTURE absent ok\")\n            print(\"REDARM absent ok\")"),
    ],
    "m2-drop-d1-d7": [
        ('and fm.group(3) == "FALSE-GREEN-REJECTED" and cases_ok',
         'and fm.group(3) == "FALSE-GREEN-REJECTED"'),
    ],
    "m3-accept-green-accepted": [
        ('fm.group(3) == "FALSE-GREEN-REJECTED"',
         'fm.group(3) in ("FALSE-GREEN-REJECTED", "FALSE-GREEN-ACCEPTED")'),
    ],
    "m4-skip-redarm": [
        ("rok = bool(bm) and int(bm.group(2)) < int(bm.group(1))",
         "rok = True"),
    ],
    "m5-regress-rc-only": [
        ("same = same and s1 == s2",
         "same = same and s1[0] == s2[0]"),
    ],
    "m6-cne-stdout-only": [
        ('return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")', RUN3),
        ('''        rc, out = run([sys.executable, "-B", os.path.join(tr, "tools/souji-landing-gate.py"), "--root", root, "--rev", a.rev,
                       "--round", "29", "--fleet-root", a.fleet_root], w, tmp)''',
         '''        rc, gout, gerr = run([sys.executable, "-B", os.path.join(tr, "tools/souji-landing-gate.py"), "--root", root, "--rev", a.rev,
                       "--round", "29", "--fleet-root", a.fleet_root], w, tmp)
        out = gout + gerr'''),
        ('cnef = int(any(l.startswith("COULD-NOT-EVALUATE") for l in out.splitlines()))',
         'cnef = int(any(l.startswith("COULD-NOT-EVALUATE") for l in gout.splitlines()))'),
        ('frc, fout = run([sys.executable, "-B", fx, "--tool", os.path.join(tr, "tools/souji-landing-gate.py")], w, tmp)',
         'frc, fout, _e1 = run([sys.executable, "-B", fx, "--tool", os.path.join(tr, "tools/souji-landing-gate.py")], w, tmp)\n            fout = fout + _e1'),
        ('brc, bout = run([sys.executable, "-B", fx, "--tool", os.path.join(tb, "tools/souji-landing-gate.py")], w, tmp)',
         'brc, bout, _e2 = run([sys.executable, "-B", fx, "--tool", os.path.join(tb, "tools/souji-landing-gate.py")], w, tmp)\n            bout = bout + _e2'),
        ('r1 = run([sys.executable, "-B", *argv], tb, tmp)',
         'r1 = run([sys.executable, "-B", *argv], tb, tmp); r1 = (r1[0], r1[1] + r1[2])'),
        ('r2 = run([sys.executable, "-B", *argv], tr, tmp)',
         'r2 = run([sys.executable, "-B", *argv], tr, tmp); r2 = (r2[0], r2[1] + r2[2])'),
    ],
    "m7-dangling-stdout-only": [
        ('return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")', RUN3),
        ('''        rc, out = run([sys.executable, "-B", os.path.join(tr, "tools/souji-landing-gate.py"), "--root", root, "--rev", a.rev,
                       "--round", "29", "--fleet-root", a.fleet_root], w, tmp)''',
         '''        rc, gout, gerr = run([sys.executable, "-B", os.path.join(tr, "tools/souji-landing-gate.py"), "--root", root, "--rev", a.rev,
                       "--round", "29", "--fleet-root", a.fleet_root], w, tmp)
        out = gout + gerr'''),
        ('dangling = sum(1 for l in out.splitlines() if l.startswith("LG-DANGLING-PTR"))',
         'dangling = sum(1 for l in gout.splitlines() if l.startswith("LG-DANGLING-PTR"))'),
        ('frc, fout = run([sys.executable, "-B", fx, "--tool", os.path.join(tr, "tools/souji-landing-gate.py")], w, tmp)',
         'frc, fout, _e1 = run([sys.executable, "-B", fx, "--tool", os.path.join(tr, "tools/souji-landing-gate.py")], w, tmp)\n            fout = fout + _e1'),
        ('brc, bout = run([sys.executable, "-B", fx, "--tool", os.path.join(tb, "tools/souji-landing-gate.py")], w, tmp)',
         'brc, bout, _e2 = run([sys.executable, "-B", fx, "--tool", os.path.join(tb, "tools/souji-landing-gate.py")], w, tmp)\n            bout = bout + _e2'),
        ('r1 = run([sys.executable, "-B", *argv], tb, tmp)',
         'r1 = run([sys.executable, "-B", *argv], tb, tmp); r1 = (r1[0], r1[1] + r1[2])'),
        ('r2 = run([sys.executable, "-B", *argv], tr, tmp)',
         'r2 = run([sys.executable, "-B", *argv], tr, tmp); r2 = (r2[0], r2[1] + r2[2])'),
    ],
    "m8-lane-worktree-gate": [
        ('run([sys.executable, "-B", os.path.join(tr, "tools/souji-landing-gate.py"), "--root", root, "--rev", a.rev,',
         'run([sys.executable, "-B", os.path.join(root, "tools/souji-landing-gate.py"), "--root", root, "--rev", a.rev,'),
    ],
}

paths = {}
paths["pristine"] = PRISTINE
for name, subs in MUTANTS.items():
    text = src
    for old, new in subs:
        n = text.count(old)
        assert n == 1, f"{name}: replacement count {n} for {old[:60]!r}"
        text = text.replace(old, new)
    p = os.path.join(S, "mutants", name + ".py")
    open(p, "w").write(text)
    paths[name] = p
    compile(text, name, "exec")  # syntax check
    log(f"{name}: patched ok")

# ---------- 3. matrix ----------
log("== running matrix ==")
os.makedirs(OUT, exist_ok=True)
env = dict(os.environ, TMPDIR=os.path.join(S, "tmp"))
os.makedirs(env["TMPDIR"], exist_ok=True)

RUNS = []
RUNS += [("pristine", s) for s in ("donothing", "junk", "k2-nocase", "k3-accepted")]
for m in ("m1-missing-fixture-ok", "m4-skip-redarm", "m5-regress-rc-only",
          "m6-cne-stdout-only", "m7-dangling-stdout-only", "m8-lane-worktree-gate"):
    RUNS += [(m, s) for s in ("donothing", "junk")]
RUNS += [("m2-drop-d1-d7", s) for s in ("donothing", "junk", "k2-nocase")]
RUNS += [("m3-accept-green-accepted", s) for s in ("donothing", "junk", "k3-accepted")]

for mutant, state in RUNS:
    rev = {"donothing": BASE, "junk": JUNK, "k2-nocase": K2, "k3-accepted": K3}[state]
    outp = os.path.join(OUT, f"{mutant}__{state}.txt")
    argv = [sys.executable, "-B", paths[mutant], "--root", LANE, "--rev", rev,
            "--base", BASE, "--fleet-root", FLEET,
            "--scratch", os.path.join(S, "counter-scratch")]
    p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=1200)
    with open(outp, "w") as fh:
        fh.write(f"# mutant={mutant} state={state} rev={rev}\n# rc={p.returncode}\n"
                 + p.stdout + ("\n--stderr--\n" + p.stderr if p.stderr else ""))
    summary = [l for l in p.stdout.splitlines() if l.startswith("SUMMARY")]
    log(f"[{mutant} / {state}] rc={p.returncode} {summary[0] if summary else 'NO-SUMMARY'}")

log("== matrix done ==")
log(f"JUNK={JUNK}")
log(f"K2={K2}")
log(f"K3={K3}")
log(f"lane counter sha256 after: {sha(os.path.join(LANE, COUNTER))}")
