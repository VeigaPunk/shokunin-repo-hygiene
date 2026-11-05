#!/usr/bin/env python3
"""r61 C2 counter: honest/mutant kill-power matrix for the r61 receipt-write fixture.

Arms (normal mode):
  honest    r61-receipt-write.py x <lane>/tools/souji-receipt-write.py   -> pass=10 fail=0, stubs REJECTED
  mwh-r61   r61-receipt-write.py x mutant-worktree-hash.py               -> fail>=1, must include case 9
  mdw-r61   r61-receipt-write.py x mutant-direct-write.py                -> fail>=1, must include case 10
  mwh-r60   r60 fixture (git show --base-tool-rev:tests/fixtures/r60-receipt-write.py) x mwh -> pass=8
  mdw-r60   r60 fixture x mdw                                            -> pass=8

--base-arm (do-nothing arm): the honest arm is unchanged; the mutant arms (b)/(c)
substitute the extracted r60 fixture bytes for the r61 fixture, so killed_new is
expected to be 0 -> prints killed_new=0 and EXIT=1 (red).

Summary line tokens (each value separately parseable):
  honest-pass= honest-fail= killed_old= killed_new= stub-always-write= stub-always-refuse= EXIT=
rc 0 iff honest pass=10 fail=0 AND killed_old=0 AND killed_new=2 AND both stubs REJECTED
AND each mutant is killed by its designated new case (9 / 10); else rc 1.
Per-arm receipts (rev=, instrument=, instrument_sha256=, command=, output, EXIT=)
are written to <work>/receipts/ in normal mode; in base-arm mode a single
base-arm.txt receipt is written.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R61_FIXTURE = os.path.join(HERE, "r61-receipt-write.py")
MUTANTS = {
    "mutant-worktree-hash": os.path.join(HERE, "mutant-worktree-hash.py"),
    "mutant-direct-write": os.path.join(HERE, "mutant-direct-write.py"),
}
R60_FIXTURE_GIT_PATH = "tests/fixtures/r60-receipt-write.py"
HONEST_REL = "tools/souji-receipt-write.py"
KILLER_CASE = {"mutant-worktree-hash": 9, "mutant-direct-write": 10}
REV_RE = re.compile(r"^[0-9a-f]{40}$")


def git(root: str, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    return subprocess.run(["git", "-C", root, *args], capture_output=True, env=env)


def die(msg: str) -> None:
    sys.stderr.write("counter error: %s\n" % msg)
    sys.exit(64)


def check_commit(root: str, rev: str, what: str) -> None:
    if not REV_RE.match(rev or ""):
        die("%s is not full 40-hex (%r)" % (what, rev))
    r = git(root, "cat-file", "-t", rev)
    if r.returncode != 0 or r.stdout.strip() != b"commit":
        die("%s is not a commit object in %s" % (what, root))


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_fixture(fixture_path: str, tool_path: str, workdir: str, label: str) -> dict:
    os.makedirs(workdir, exist_ok=True)
    argv = [sys.executable, "-B", fixture_path, "--tool", tool_path, "--work", workdir]
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          timeout=600)
    out = proc.stdout.decode("utf-8", "replace")
    cases = {}
    for m in re.finditer(r"^CASE (\d+) (\S+) (pass|fail)$", out, re.M):
        cases[int(m.group(1))] = (m.group(2), m.group(3) == "pass")
    sm = re.search(r"^SUMMARY cases=(\d+) pass=(\d+) fail=(\d+) "
                   r"control=ALWAYS-WRITE-(REJECTED|ACCEPTED),ALWAYS-REFUSE-(REJECTED|ACCEPTED)$",
                   out, re.M)
    if sm is None:
        die("%s: fixture produced no SUMMARY line (rc=%d)\n%s"
            % (label, proc.returncode, out[-2000:]))
    return {
        "label": label, "fixture": fixture_path, "tool": tool_path, "argv": argv,
        "rc": proc.returncode, "stdout": out, "cases": cases,
        "cases_n": int(sm.group(1)), "pass": int(sm.group(2)), "fail": int(sm.group(3)),
        "aw": sm.group(4), "ar": sm.group(5),
        "failed": sorted(n for n, (_, ok) in cases.items() if not ok),
    }


def receipt(dirpath: str, name: str, rev: str, instrument_rel: str, instrument_sha: str,
            command_argv: list, output: str, rc: int, extra=()) -> str:
    lines = [
        "rev=%s" % rev,
        "instrument=%s" % instrument_rel,
        "instrument_sha256=%s" % instrument_sha,
        "command=%s" % " ".join(shlex.quote(a) for a in command_argv),
    ]
    lines.extend(extra)
    lines.append("output-begin")
    out_lines = output.splitlines() or ["(empty)"]
    lines.extend("  " + l for l in out_lines)
    lines.append("output-end")
    lines.append("EXIT=%d" % rc)
    os.makedirs(dirpath, exist_ok=True)
    path = os.path.join(dirpath, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description="r61 C2 receipt-write kill-power counter")
    ap.add_argument("--root", required=True, help="lane root (read-only git)")
    ap.add_argument("--rev", required=True, help="full 40-hex lane rev the receipts bind")
    ap.add_argument("--base-tool-rev", default="c7228424c3919ecf142bab1aec8181722d86467b",
                    help="rev to extract the r60 fixture bytes from via git show")
    ap.add_argument("--work", required=True, help="scratch work dir (created)")
    ap.add_argument("--base-arm", action="store_true",
                    help="do-nothing arm: mutant arms use the r60 fixture; expects killed_new=0 -> EXIT=1")
    ns = ap.parse_args(argv)

    root = os.path.abspath(ns.root)
    work = os.path.abspath(ns.work)
    receipts_dir = os.path.join(work, "receipts")
    os.makedirs(work, exist_ok=True)
    if not os.path.isdir(root):
        die("root is not a directory: %s" % root)
    check_commit(root, ns.rev, "--rev")
    check_commit(root, ns.base_tool_rev, "--base-tool-rev")

    honest = os.path.join(root, HONEST_REL)
    if not os.path.isfile(honest):
        die("honest writer missing: %s" % honest)
    for name, path in MUTANTS.items():
        if not os.path.isfile(path):
            die("mutant missing: %s" % path)
    if not os.path.isfile(R61_FIXTURE):
        die("r61 fixture missing: %s" % R61_FIXTURE)

    # r60 fixture bytes from the committed base-tool-rev (read-only git show)
    show = git(root, "show", "%s:%s" % (ns.base_tool_rev, R60_FIXTURE_GIT_PATH))
    if show.returncode != 0:
        die("git show %s:%s failed: %s" % (ns.base_tool_rev, R60_FIXTURE_GIT_PATH,
                                           show.stderr.decode("utf-8", "replace").strip()))
    r60_fixture = os.path.join(work, "r60-receipt-write.extracted.py")
    with open(r60_fixture, "wb") as f:
        f.write(show.stdout)
    r60_sha = hashlib.sha256(show.stdout).hexdigest()
    print("# r60 fixture extracted from %s:%s sha256=%s"
          % (ns.base_tool_rev, R60_FIXTURE_GIT_PATH, r60_sha))

    honest_sha = sha256_file(honest)
    mutant_sha = {n: sha256_file(p) for n, p in MUTANTS.items()}

    arms = []
    arms.append(run_fixture(R61_FIXTURE, honest, os.path.join(work, "arms", "honest"), "honest"))
    for name, path in MUTANTS.items():
        fix = r60_fixture if ns.base_arm else R61_FIXTURE
        tag = "%s-%s" % (name, "r60" if ns.base_arm else "r61")
        arms.append(run_fixture(fix, path, os.path.join(work, "arms", tag), tag))
    if not ns.base_arm:
        for name, path in MUTANTS.items():
            arms.append(run_fixture(r60_fixture, path,
                                    os.path.join(work, "arms", "%s-r60" % name),
                                    "%s-r60" % name))

    for a in arms:
        print("ARM %s fixture=%s tool=%s cases=%d pass=%d fail=%d failed=%s stubs=%s,%s rc=%d"
              % (a["label"], os.path.basename(a["fixture"]), os.path.basename(a["tool"]),
                 a["cases_n"], a["pass"], a["fail"], a["failed"], a["aw"], a["ar"], a["rc"]))

    honest_arm = arms[0]
    r61_arms = {a["label"]: a for a in arms if a["label"].endswith("-r61")}
    r60_arms = {a["label"]: a for a in arms if a["label"].endswith("-r60")}

    if ns.base_arm:
        # do-nothing arm: arms (b)/(c) ran the r60 fixture, so killed_new counts
        # mutants killed by the substituted fixture (expected 0 -> red EXIT=1).
        killed_new = sum(1 for name in MUTANTS if r60_arms["%s-r60" % name]["fail"] >= 1)
    else:
        killed_new = sum(1 for name in MUTANTS if r61_arms["%s-r61" % name]["fail"] >= 1)
    killed_old = sum(1 for name in MUTANTS if r60_arms["%s-r60" % name]["fail"] >= 1)

    killer_ok = {}
    if not ns.base_arm:
        for name, case_n in KILLER_CASE.items():
            killer_ok[name] = case_n in r61_arms["%s-r61" % name]["failed"]

    counter_argv = [sys.executable, "-B", os.path.abspath(__file__)] + list(sys.argv[1:])
    if ns.base_arm:
        receipt(receipts_dir, "base-arm.txt", ns.rev,
                "r60-fixture(do-nothing substitution)", r60_sha, counter_argv,
                "\n".join(a["stdout"] for a in arms), 1,
                extra=("mode=base-arm", "base-tool-rev=%s" % ns.base_tool_rev,
                       "killed_new=%d" % killed_new, "killed_old=%d" % killed_old))
    else:
        receipt(receipts_dir, "honest-r61.txt", ns.rev, HONEST_REL, honest_sha,
                [sys.executable, "-B", R61_FIXTURE, "--tool", honest,
                 "--work", os.path.join(work, "arms", "honest")],
                honest_arm["stdout"], honest_arm["rc"],
                extra=("base-tool-rev=%s" % ns.base_tool_rev,
                       "stubs=ALWAYS-WRITE-%s,ALWAYS-REFUSE-%s" % (honest_arm["aw"], honest_arm["ar"])))
        for name in MUTANTS:
            a = r61_arms["%s-r61" % name]
            receipt(receipts_dir, "%s-r61.txt" % name, ns.rev,
                    "mutant:%s" % name, mutant_sha[name],
                    [sys.executable, "-B", R61_FIXTURE, "--tool", MUTANTS[name],
                     "--work", os.path.join(work, "arms", "%s-r61" % name)],
                    a["stdout"], a["rc"],
                    extra=("base-tool-rev=%s" % ns.base_tool_rev,
                           "failed_cases=%s" % a["failed"]))
            b = r60_arms["%s-r60" % name]
            receipt(receipts_dir, "%s-r60.txt" % name, ns.rev,
                    "mutant:%s" % name, mutant_sha[name],
                    [sys.executable, "-B", r60_fixture, "--tool", MUTANTS[name],
                     "--work", os.path.join(work, "arms", "%s-r60" % name)],
                    b["stdout"], b["rc"],
                    extra=("fixture=git-show:%s:%s" % (ns.base_tool_rev, R60_FIXTURE_GIT_PATH),
                           "fixture_sha256=%s" % r60_sha,
                           "failed_cases=%s" % b["failed"]))

    ok = (honest_arm["pass"] == 10 and honest_arm["fail"] == 0
          and honest_arm["aw"] == "REJECTED" and honest_arm["ar"] == "REJECTED"
          and killed_old == 0 and killed_new == 2
          and all(killer_ok.values()))
    rc = 0 if ok else 1
    print("killed_old=%d killed_new=%d killer-cases=%s"
          % (killed_old, killed_new,
             killer_ok if not ns.base_arm else "{} (base-arm: old fixture has no cases 9/10)"))
    print("SUMMARY honest-pass=%d honest-fail=%d killed_old=%d killed_new=%d "
          "stub-always-write=%s stub-always-refuse=%s EXIT=%d"
          % (honest_arm["pass"], honest_arm["fail"], killed_old, killed_new,
             honest_arm["aw"], honest_arm["ar"], rc))
    return rc


if __name__ == "__main__":
    sys.exit(main())
