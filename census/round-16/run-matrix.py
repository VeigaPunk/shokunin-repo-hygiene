#!/usr/bin/env python3
"""round-16 C1 counting command: parse + behaviour matrix for tools/souji-census.sh.

Arms are committed revisions (or the worktree file), each extracted with
`git show <rev>:tools/souji-census.sh` into a private /var/tmp directory:
  pre-harm a31642d, r14-harm cc21683, r15-baseline b410186, changed <rev|WORKTREE>.
Every arm runs the SAME current fixtures (r15 config, r14 namespace) plus its
own `--selftest`, `bash -n` and `shellcheck -S warning`.

Usage: python3 census/round-16/run-matrix.py --changed <rev|WORKTREE> --output <new.json>
Refuses to overwrite an existing output. Scratch is removed afterwards.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANE = Path(__file__).resolve().parents[2]
ARMS = (("pre-harm", "a31642d"), ("r14-harm", "cc21683"), ("r15-baseline", "b410186"))
CASE_RE = re.compile(r"^CASE\t(\S+)\t(PASS|FAIL)\t(.*)$")
SUMMARY_RE = re.compile(r"^SUMMARY\ttotal=(\d+)\tfailed=(\d+)")
SELFTEST_RE = re.compile(r"^selftest: (\d+) checks, (\d+) failed")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(LANE), *args], check=True,
                          capture_output=True, text=True).stdout


def run(cmd: list[str], timeout: int = 900) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           errors="replace")
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def suite(fixture: Path, tool: Path) -> dict:
    rc, out, err = run([sys.executable, str(fixture), "--tool", str(tool)])
    cases = {}
    total = failed = None
    for line in out.splitlines():
        m = CASE_RE.match(line)
        if m:
            cases[m.group(1)] = {"verdict": m.group(2), "detail": m.group(3)[:300]}
        m = SUMMARY_RE.match(line)
        if m:
            total, failed = int(m.group(1)), int(m.group(2))
    valid = (rc in (0, 1) and isinstance(total, int) and total > 0
             and isinstance(failed, int) and 0 <= failed <= total
             and len(cases) == total
             and sum(c["verdict"] == "FAIL" for c in cases.values()) == failed)
    return {"rc": rc, "total": total, "failed": failed, "cases": cases, "valid": valid,
            "stderr_tail": err.strip().splitlines()[-3:]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed", required=True, help="revision or WORKTREE")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    out = Path(a.output)
    if not out.is_absolute():
        out = LANE / out
    if out.exists():
        print(f"run-matrix: refusing to overwrite {out}", file=sys.stderr)
        return 2
    fixtures = {
        "r15-config": LANE / "tests/fixtures/r15-census-config.py",
        "r14-namespace": LANE / "tests/fixtures/r14-census-boundary.py",
    }
    record = {
        "lane_head": git("rev-parse", "HEAD").strip(),
        "changed": a.changed,
        "fixtures_sha256": {k: hashlib.sha256(v.read_bytes()).hexdigest()
                            for k, v in fixtures.items()},
        "fixtures_dirty": git("status", "--porcelain", "--",
                              *[str(v.relative_to(LANE)) for v in fixtures.values()]).strip(),
        "git_version": run(["git", "--version"])[1].strip(),
        "bash_version": run(["bash", "--version"])[1].splitlines()[0],
        "shellcheck_version": run(["shellcheck", "--version"])[1].strip().splitlines()[1:2],
        "python_version": sys.version.split()[0],
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "arms": {},
    }
    scratch = Path(tempfile.mkdtemp(prefix="souji-r16-matrix.", dir="/var/tmp"))
    try:
        arms = list(ARMS) + [("changed", a.changed)]
        for name, rev in arms:
            tool = scratch / name / "tools" / "souji-census.sh"
            tool.parent.mkdir(parents=True)
            if rev == "WORKTREE":
                shutil.copyfile(LANE / "tools/souji-census.sh", tool)
                full = "WORKTREE"
            else:
                tool.write_bytes(subprocess.run(
                    ["git", "-C", str(LANE), "show", f"{rev}:tools/souji-census.sh"],
                    check=True, capture_output=True).stdout)
                full = git("rev-parse", rev).strip()
            tool.chmod(0o755)
            arm = {"rev": full, "sha256": hashlib.sha256(tool.read_bytes()).hexdigest()}
            rc, _, err = run(["bash", "-n", str(tool)])
            arm["bash_n"] = {"rc": rc, "stderr": err.strip().splitlines()[:2]}
            rc, so, _ = run(["shellcheck", "-S", "warning", str(tool)])
            arm["shellcheck_warning"] = {"rc": rc, "findings": len(re.findall(r"\(warning\)|\(error\)", so))}
            rc, so, se = run(["bash", str(tool), "--selftest"], timeout=600)
            m = None
            for line in so.splitlines() + se.splitlines():
                m = SELFTEST_RE.match(line) or m
            arm["selftest"] = {"rc": rc,
                               "checks": int(m.group(1)) if m else None,
                               "failed": int(m.group(2)) if m else None}
            for key, fx in fixtures.items():
                arm[key] = suite(fx, tool)
            record["arms"][name] = arm
            print(f"{name}\t{arm['sha256'][:12]}\tbash-n={arm['bash_n']['rc']}"
                  f"\tsc={arm['shellcheck_warning']['rc']}"
                  f"\tselftest={arm['selftest']['checks']}/{arm['selftest']['failed']}fail"
                  f"\tr15={arm['r15-config']['total']}/{arm['r15-config']['failed']}fail"
                  f"\tr14={arm['r14-namespace']['total']}/{arm['r14-namespace']['failed']}fail")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    invalid = [f"{a}:{k}" for a, arm in record["arms"].items()
               for k in ("r15-config", "r14-namespace") if not arm[k]["valid"]]
    record["invalid_suites"] = invalid
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "x", encoding="utf-8") as fh:
        fh.write(json.dumps(record, indent=1, sort_keys=True) + "\n")
    if invalid:
        print(f"run-matrix: could not evaluate suites: {invalid}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
