#!/usr/bin/env python3
"""r34 C2 junk control (frozen legs file J1): the counter must FAIL stubbed work legs.

Builds a scratch clone of the lane at the current tip, commits a stubbed legs file whose
witness/nsbind argv are echo stubs (they print a plausible base run's last digit-bearing
line with exit 0 but do NO work), plus a no-op junk target, then runs the r34 C2 counter
against that clone and asserts EVERY stubbed leg FAILs. A counter that greens a stub
(e.g. a witness leg without a work witness, or an nsbind leg that never checks the
sandbox) is rejected.

Line fidelity: W1/W4 lines are captured from a real run of the row's own command at the
tip; W2/W3/N3 use the lines documented in the frozen legs header
(`SUMMARY<TAB>total=12 failed=0`, `selftest: 69 checks, 0 failed`) -- the stubbed legs
fail at the work-witness/CASE-count clauses regardless, because both the --base and the
--rev run inside the counter execute the same stub argv.

Runs only on caller-provided persistent scratch; removes its scratch dir on exit; never
touches the lane tree, lane git state or any file outside --scratch.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

STUBBED = ["W1", "W2", "W3", "W4", "N3"]
# Documented base lines (frozen legs header / SKILL gate rows); tabs via printf escapes.
DOC_LINES = {
    "W2": "SUMMARY\\ttotal=12\\tfailed=0",
    "W3": "selftest: 69 checks, 0 failed",
    "N3": "SUMMARY\\ttotal=12\\tfailed=0",
}


def git(root, *a):
    p = subprocess.run(["git", "-C", root, *a], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"git -C {root} {' '.join(a)}: {p.stderr.strip()}")
    return p.stdout


def capture_line(clone, argv):
    env = {"PATH": "/usr/bin:/bin", "TMPDIR": os.path.join(clone, "..", "cap_tmp"),
           "GIT_CONFIG_NOSYSTEM": "1", "HOME": os.environ.get("HOME", "/root"), "LANG": "C.UTF-8"}
    os.makedirs(env["TMPDIR"], exist_ok=True)
    p = subprocess.run(["bash", "-c", argv], cwd=clone, env=env, capture_output=True, text=True, timeout=600)
    lines = (p.stdout + "\n" + p.stderr).splitlines()
    for x in reversed(lines):
        if re.search(r"\d", x):
            return " ".join(x.split())
    return "0"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    counter = os.path.abspath(a.counter)
    root = os.path.dirname(os.path.dirname(os.path.dirname(counter)))  # census/round-34/<name> -> lane
    scratch = os.path.abspath(a.scratch)
    os.makedirs(scratch, exist_ok=True)
    work = tempfile.mkdtemp(prefix="r34-junk.", dir=scratch)
    try:
        tip = git(root, "rev-parse", "master").strip()
        if not re.fullmatch(r"[0-9a-f]{40}", tip):
            print(f"cases=5 pass=0 control=STUB-REJECTED bad-tip rc=1")
            return 1
        clone = os.path.join(work, "c")
        subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", root, clone], check=True)
        git(clone, "remote", "remove", "origin")
        git(clone, "checkout", "-qf", "--detach", tip)
        lines = {}
        for iid in STUBBED:
            argv = {
                "W1": "python3 -B tools/souji-evidence-cache.py --selftest",
                "W4": "bash tools/souji-verify.sh --selftest",
            }.get(iid)
            if argv:
                try:
                    lines[iid] = capture_line(clone, argv)
                except Exception:
                    lines[iid] = DOC_LINES.get(iid, "0")
            else:
                lines[iid] = DOC_LINES[iid]
        stub_argv = {
            "W1": f"echo '{lines['W1']}'",
            "W2": f"printf '{lines['W2']}\\n'",
            "W3": f"echo '{lines['W3']}'",
            "W4": f"echo '{lines['W4']}'",
            "N3": f"printf '{lines['N3']}\\n'",
        }
        noop = os.path.join(clone, "tests", "fixtures", "r34-junk-noop.py")
        with open(noop, "w") as fh:
            fh.write("#!/usr/bin/env python3\nimport sys\nsys.exit(1)\n")
        legs_path = os.path.join(clone, "census", "round-34", "c2-legs.tsv")
        os.makedirs(os.path.dirname(legs_path), exist_ok=True)
        out = ["# stubbed legs for the r34 junk control (never committed to the lane)",
               "id\tkind\targv"]
        for iid in STUBBED:
            kind = "nsbind" if iid == "N3" else "witness"
            out.append(f"{iid}\t{kind}\t{stub_argv[iid]}")
        out.append("J1\tjunk\tpython3 -B tests/fixtures/r34-junk-noop.py --counter census/round-34/c2-counter.py --scratch {SCRATCH}/inner-junk")
        for gid, gargv in (("G1", "diff census/round-33"), ("G2", "touched-paths"), ("G3", "false-green"),
                           ("G4", "bwrap"), ("G5", "c1-c2-disjoint"), ("G6", "namespace-pin")):
            out.append(f"{gid}\tguard\t{gargv}")
        with open(legs_path, "w") as fh:
            fh.write("\n".join(out) + "\n")
        git(clone, "add", "census/round-34/c2-legs.tsv", "tests/fixtures/r34-junk-noop.py")
        git(clone, "-c", "user.name=scratch", "-c", "user.email=scratch@invalid",
            "commit", "-q", "-m", "r34 junk control stub state")
        stub_rev = git(clone, "rev-parse", "HEAD").strip()
        inner_scratch = os.path.join(work, "inner")
        os.makedirs(inner_scratch, exist_ok=True)
        p = subprocess.run([sys.executable, "-B", counter, "--root", clone, "--rev", stub_rev,
                            "--base", tip, "--list-rev", stub_rev, "--scratch", inner_scratch],
                           capture_output=True, text=True, timeout=900)
        text = p.stdout + p.stderr
        failed_ids = set(re.findall(r"^LEG\t([WNJ]\S*)\tFAIL\t", text, re.M))
        ok = True
        for iid in STUBBED:
            if iid not in failed_ids:
                ok = False
        if p.returncode == 0 or "control" in text and "STUB-REJECTED" not in text:
            ok = False
        if not ok:
            print(f"cases=5 pass=0 control=STUB-REJECTED stubbed={','.join(sorted(failed_ids))} rc={p.returncode}")
            print(text[-2000:])
            return 1
        print(f"cases=5 pass=5 control=STUB-REJECTED checked={';'.join(STUBBED)}")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
