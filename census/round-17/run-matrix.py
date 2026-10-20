#!/usr/bin/env python3
"""round-17 C1 counting command: parse + behaviour matrix for tools/souji-census.sh.

Arms are committed revisions (or the worktree file), each extracted with
`git show <rev>:tools/souji-census.sh` into a private /var/tmp directory:
  pre-harm a31642d, r14-harm cc21683, r16 5fa6017, changed <rev|WORKTREE>.
namespace, each invoked with its own selector -- see FIXTURES) plus its own
`--selftest`, `bash -n` and `shellcheck -S warning`. Timed-out commands are
killed as a process group, so fixture-spawned children cannot orphan.

Usage: python3 census/round-17/run-matrix.py --changed <rev|WORKTREE> --output <new.json>
Refuses to overwrite an existing output. Scratch is removed afterwards.

Validity contract per fixture suite (tighter than round 16):
  - SUMMARY\ttotal=N\tfailed=M present, N > 0, 0 <= M <= N + synthetic rows;
  - rc == 0 when M == 0 else rc == 1, so a post-SUMMARY crash (teardown
    traceback exits 1) can never read as a green suite;
  - exactly `total` non-synthetic CASE rows, each with verdict PASS or FAIL,
    and the FAIL tally equals `failed`;
  - a fixture `CASE\tid-set\tFAIL\t...` row is the synthetic universe-drift
    row: it is excluded from the `total` count but counted in `failed`, so a
    drift is a *valid red* suite with the honest `id-set` detail, not an
    "unevaluable" suite.

Dirty fixtures gate the record: any `git status --porcelain` output over the
lane-relative fixture paths refuses the run (exit 2, no record) unless
--allow-dirty-fixtures is given, in which case the dirty string is recorded.
Fixtures outside the lane (--fixture-dir override) cannot be dirty-checked;
fixtures_dirty is null then and fixtures_dir records the override.

Output schema (record_schema 2):
  lane_head           branch tip: `git rev-parse refs/heads/master`
  git_head            bare HEAD sha (detached under jj colocation)
  changed             the --changed argument verbatim
  changed_rev         resolved full sha of the changed arm (or "WORKTREE")
  fixture_dir         --fixture-dir override, or null
  allow_dirty_fixtures  bool, mirrors the flag
  fixtures            {suite key: fixture path used, as given}
  fixtures_sha256     {suite key: sha256 of fixture bytes}
  fixtures_dirty      porcelain string over lane-relative fixtures, or null
  git_version, bash_version, shellcheck_version, python_version, runner_sha256
  arms                {arm name:
      rev             full sha or "WORKTREE"
      sha256          sha256 of the extracted census bytes
      bash_n          {rc, stderr: [first 2 lines]}
      shellcheck_warning {rc, findings: count of (warning)/(error) notes}
      selftest        {rc, checks, failed}
      <suite key>     {rc, total, failed, cases: {id: {verdict, detail}},
                       valid, stderr_tail: [last 3 lines]}}
  invalid_suites      ["<arm>:<suite>"] for every suite that is not valid
  record_schema       2

Exit codes: 0 record written and every suite valid (red cases are data, not a
runner failure); 2 output exists, fixtures dirty without the flag, unknown
rev, or any suite could not be evaluated; 1 runner/OS error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

LANE = Path(__file__).resolve().parents[2]
ARMS = (("pre-harm", "a31642d"), ("r14-harm", "cc21683"), ("r16", "5fa6017"))
FIXTURES = {
    # suite key -> (fixture filename, argv selector carrying the census path)
    "r17-hygiene": ("r17-census-hygiene.py", "--census"),
    "r15-config": ("r15-census-config.py", "--tool"),
    "r14-namespace": ("r14-census-boundary.py", "--tool"),
}
CASE_RE = re.compile(r"^CASE\t(\S+)\t(PASS|FAIL)\t(.*)$")
SUMMARY_RE = re.compile(r"^SUMMARY\ttotal=(\d+)\tfailed=(\d+)")
SELFTEST_RE = re.compile(r"^selftest: (\d+) checks, (\d+) failed")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(LANE), *args], check=True,
                          capture_output=True, text=True).stdout


def run(cmd: list[str], timeout: int = 900) -> tuple[int, str, str]:
    # start_new_session + killpg: a fixture may spawn git children that block
    # (e.g. on a hostile fifo); kill the whole group on timeout, not just the
    # interpreter, so no orphan is left (SentinelFifoHostile w1 note).
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True,
                             errors="replace", start_new_session=True)
    except OSError as exc:
        return 127, "", f"cannot run {cmd[0]}: {exc}"
    try:
        out_s, err_s = p.communicate(timeout=timeout)
        return p.returncode, out_s, err_s
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        p.communicate()
        return 124, "", "timeout"


def suite(fixture: Path, tool: Path, selector: str) -> dict:
    rc, out, err = run([sys.executable, str(fixture), selector, str(tool)])
    cases = {}
    total = failed = None
    for line in out.splitlines():
        m = CASE_RE.match(line)
        if m:
            cases[m.group(1)] = {"verdict": m.group(2), "detail": m.group(3)[:300]}
        m = SUMMARY_RE.match(line)
        if m:
            total, failed = int(m.group(1)), int(m.group(2))
    synthetic = len([k for k in cases if k == "id-set"])
    # 0 or 1 by construction (dict key), kept as a count for clarity.
    valid = (isinstance(total, int) and total > 0
             and isinstance(failed, int) and 0 <= failed <= total + synthetic
             and rc == (1 if failed else 0)
             and len(cases) - synthetic == total
             and sum(c["verdict"] == "FAIL" for c in cases.values()) == failed)
    return {"rc": rc, "total": total, "failed": failed, "cases": cases,
            "valid": valid, "stderr_tail": err.strip().splitlines()[-3:]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed", required=True, help="revision or WORKTREE")
    ap.add_argument("--output", required=True)
    ap.add_argument("--fixture-dir",
                    help="directory to resolve fixture names in, instead of "
                         "tests/fixtures (for pre-landing smoke tests)")
    ap.add_argument("--allow-dirty-fixtures", action="store_true",
                    help="record a run against modified/untracked fixtures "
                         "instead of refusing")
    a = ap.parse_args()
    out = Path(a.output)
    if not out.is_absolute():
        out = LANE / out
    if out.exists():
        print(f"run-matrix: refusing to overwrite {out}", file=sys.stderr)
        return 2

    fdir = Path(a.fixture_dir) if a.fixture_dir else LANE / "tests/fixtures"
    fixtures = {key: fdir / spec[0] for key, spec in FIXTURES.items()}
    missing = [str(p) for p in fixtures.values() if not p.is_file()]
    if missing:
        print(f"run-matrix: missing fixtures: {missing}", file=sys.stderr)
        return 2

    lane_rel = [str(p.resolve().relative_to(LANE))
                for p in fixtures.values()
                if p.resolve().is_relative_to(LANE)]
    in_lane = len(lane_rel) == len(fixtures)
    fixtures_dirty = (git("status", "--porcelain", "--", *lane_rel).strip()
                      if in_lane else None)
    if fixtures_dirty and not a.allow_dirty_fixtures:
        print("run-matrix: fixture files are dirty, refusing to record:\n"
              + fixtures_dirty
              + "\nrun-matrix: pass --allow-dirty-fixtures to record anyway",
              file=sys.stderr)
        return 2

    record = {
        "record_schema": 2,
        "lane_head": git("rev-parse", "refs/heads/master").strip(),
        "git_head": git("rev-parse", "HEAD").strip(),
        "changed": a.changed,
        "fixture_dir": str(fdir) if a.fixture_dir else None,
        "allow_dirty_fixtures": a.allow_dirty_fixtures,
        "fixtures": {k: str(v) for k, v in fixtures.items()},
        "fixtures_sha256": {k: hashlib.sha256(v.read_bytes()).hexdigest()
                            for k, v in fixtures.items()},
        "fixtures_dirty": fixtures_dirty,
        "git_version": run(["git", "--version"])[1].strip(),
        "bash_version": run(["bash", "--version"])[1].splitlines()[0],
        "shellcheck_version": run(["shellcheck", "--version"])[1].strip().splitlines()[1:2],
        "python_version": sys.version.split()[0],
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "arms": {},
    }
    suite_keys = list(fixtures)
    scratch = Path(tempfile.mkdtemp(prefix="souji-r17-matrix.", dir="/var/tmp"))
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
            arm["shellcheck_warning"] = {
                "rc": rc,
                "findings": len(re.findall(r"\(warning\)|\(error\)", so))}
            rc, so, se = run(["bash", str(tool), "--selftest"], timeout=600)
            m = None
            for line in so.splitlines() + se.splitlines():
                m = SELFTEST_RE.match(line) or m
            arm["selftest"] = {"rc": rc,
                               "checks": int(m.group(1)) if m else None,
                               "failed": int(m.group(2)) if m else None}
            for key, fx in fixtures.items():
                arm[key] = suite(fx, tool, FIXTURES[key][1])
            record["arms"][name] = arm
            tally = "\t".join(
                f"{key}={arm[key]['total']}/{arm[key]['failed']}fail"
                for key in suite_keys)
            print(f"{name}\t{arm['sha256'][:12]}\tbash-n={arm['bash_n']['rc']}"
                  f"\tsc={arm['shellcheck_warning']['rc']}"
                  f"\tselftest={arm['selftest']['checks']}/{arm['selftest']['failed']}fail"
                  f"\t{tally}")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    record["changed_rev"] = record["arms"]["changed"]["rev"]
    invalid = [f"{arm_name}:{key}" for arm_name, arm in record["arms"].items()
               for key in suite_keys if not arm[key]["valid"]]
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
