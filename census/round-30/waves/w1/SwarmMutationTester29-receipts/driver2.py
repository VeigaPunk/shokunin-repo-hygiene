#!/usr/bin/env python3
"""Phase 2: junk-state cells with --root pointed at the scratch state clone,
plus two sharper states (junk2 regress-clean stub, k5b selftest-digit stub)."""
import os, shutil, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "9420341d9a814cb6089c25fb03a4cc9b23dc0d1b"
S = "/fast/scratch/hyaku/souji-r30/MutateC2Counter"
OUT = os.path.join(S, "out")
C = os.path.join(S, "states/c")


def log(m):
    print(m, flush=True)


def sh(argv, cwd=None):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(f"FAILED {argv}\n{p.stdout}\n{p.stderr}")
    return p


GATE_AT_BASE = sh(["git", "-C", LANE, "show", f"{BASE}:tools/souji-landing-gate.py"]).stdout

R29_OVERRIDE = '''    if args.round_no == 29:
        result["findings"] = []
        result["checked_reports"] = 86
        result["error"] = None
    return emit(result, json_out=args.json_out)'''

SELFTEST_ANCHOR = 'print("SELFTEST\\tpass=%d\\tfail=%d" % (passed, failed))'
SELFTEST_PATCH = 'print("SELFTEST\\tpass=%d\\tfail=%d" % (passed + 100, failed))'

FIX_PLAIN = """#!/usr/bin/env python3
for i in range(1, 8):
    print("CASE D%d PASS" % i)
print("cases=7 pass=7 control=FALSE-GREEN-REJECTED")
"""

FIX_DISCRIM = """#!/usr/bin/env python3
import sys
tool = sys.argv[sys.argv.index("--tool") + 1] if "--tool" in sys.argv else ""
data = open(tool, "rb").read() if tool else b""
rev_side = b"round_no == 29" in data
p = 7 if rev_side else 3
for i in range(1, 8):
    print("CASE D%d %s" % (i, "PASS" if (rev_side or i > 3) else "FAIL"))
print("cases=7 pass=%d control=FALSE-GREEN-REJECTED" % p)
"""


def make_state(name, gate_text, fixture_text):
    sh(["git", "-C", C, "checkout", "-q", "--detach", BASE])
    sh(["git", "-C", C, "checkout", "-q", "-B", name])
    open(os.path.join(C, "tools/souji-landing-gate.py"), "w").write(gate_text)
    open(os.path.join(C, "tests/fixtures/r30-landing-gate-discovery.py"), "w").write(fixture_text)
    sh(["git", "-C", C, "add", "-A"])
    sh(["git", "-C", C, "commit", "-q", "-m", f"scratch {name} (mutation-test rig)"])
    rev = sh(["git", "-C", C, "rev-parse", "HEAD"]).stdout.strip()
    log(f"{name}: {rev}")
    return rev


assert GATE_AT_BASE.count("    return emit(result, json_out=args.json_out)") == 1
assert GATE_AT_BASE.count(SELFTEST_ANCHOR) == 1

JUNK2 = make_state("junk2-regress-clean",
                   GATE_AT_BASE.replace("    return emit(result, json_out=args.json_out)", R29_OVERRIDE),
                   FIX_PLAIN)
K5B = make_state("k5b-selftest-digit",
                 GATE_AT_BASE.replace("    return emit(result, json_out=args.json_out)", R29_OVERRIDE)
                             .replace(SELFTEST_ANCHOR, SELFTEST_PATCH),
                 FIX_DISCRIM)

M = "/fast/scratch/hyaku/souji-r30/MutateC2Counter/mutants"
paths = {n[:-3]: os.path.join(M, n) for n in os.listdir(M) if n.endswith(".py")}
REVS = {"junk": "db156ef836bdf1f9b280ac6c976ae3fbfcb93497",
        "k2-nocase": "efd53802a09f3e4a5ace5532a239999d046bca48",
        "k3-accepted": "ea930d20d1b6cd93ec9ddc13cbdb51568ca0a560",
        "junk2": JUNK2, "k5b": K5B}

RUNS = [
    ("pristine", "junk"), ("pristine", "junk2"), ("pristine", "k5b"),
    ("pristine", "k2-nocase"), ("pristine", "k3-accepted"),
    ("m2-drop-d1-d7", "junk"), ("m2-drop-d1-d7", "k2-nocase"),
    ("m3-accept-green-accepted", "junk"), ("m3-accept-green-accepted", "k3-accepted"),
    ("m4-skip-redarm", "junk"), ("m4-skip-redarm", "junk2"),
    ("m5-regress-rc-only", "junk"), ("m5-regress-rc-only", "k5b"),
    ("m7-dangling-stdout-only", "junk"), ("m7-dangling-stdout-only", "junk2"),
    ("m8-lane-worktree-gate", "junk"),
]

env = dict(os.environ, TMPDIR=os.path.join(S, "tmp"))
for mutant, state in RUNS:
    outp = os.path.join(OUT, f"p2-{mutant}__{state}.txt")
    argv = [sys.executable, "-B", paths[mutant], "--root", C, "--rev", REVS[state],
            "--base", BASE, "--fleet-root", FLEET,
            "--scratch", os.path.join(S, "counter-scratch")]
    p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=1200)
    with open(outp, "w") as fh:
        fh.write(f"# mutant={mutant} state={state} rev={REVS[state]} root={C}\n# rc={p.returncode}\n"
                 + p.stdout + ("\n--stderr--\n" + p.stderr if p.stderr else ""))
    summary = [l for l in p.stdout.splitlines() if l.startswith("SUMMARY")]
    log(f"[{mutant} / {state}] rc={p.returncode} {summary[0] if summary else 'NO-SUMMARY'}")

log("== phase2 done ==")
