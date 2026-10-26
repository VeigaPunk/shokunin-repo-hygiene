#!/usr/bin/env python3
"""Regenerate the r15-preservation-frozen record from real runs (round 16, R4).

The r15 pins named census bytes that no commit ever held (b5187351…); a
digest-only re-pin would pair an authored transcript with new digests. This
script instead re-runs every arm at committed bytes and records only what the
runs printed:

  baseline_preharm  a31642d tools/souji-census.sh
  baseline          cc21683 tools/souji-census.sh
  changed           <REV>   tools/souji-census.sh
  namespace_controls <REV>  tools/souji-census.sh under tests/fixtures/r14-census-boundary.py

Each tool is extracted with `git show <rev>:tools/souji-census.sh` into a
private TMPDIR directory (removed afterwards). The fixtures run from the
lane checkout and must equal their bytes at <REV>; the installed tool must too.

Usage: python3 tests/fixtures/r15-preservation-frozen/regenerate.py --rev <REV>
       [--allow-nonclean]
Writes record.json and expected.json in this directory.

The verdict in expected.json is not a literal: the script runs
tools/souji-preservation-evidence.py's own evaluation against the generated
record (--root <lane> --record <text>, the same entry point --frozen uses)
and writes the observed verdict. A non-clean verdict refuses the write
(exit 3, nothing written) unless --allow-nonclean is given, in which case
the computed verdict is recorded verbatim and the override is announced on
stderr. After writing, the script re-runs the checker in --frozen mode over
this directory and requires its exit status to equal the recorded verdict.

Exit codes: 0 wrote a consistent record; 2 usage/binding/tool failure;
3 computed verdict was not clean and --allow-nonclean was absent.
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

HERE = Path(__file__).resolve().parent
LANE = HERE.parents[2]
TOOL = "tools/souji-census.sh"
CONFIG_FIXTURE = "tests/fixtures/r15-census-config.py"
NS_FIXTURE = "tests/fixtures/r14-census-boundary.py"
CHECKER = "tools/souji-preservation-evidence.py"
# Mirrors STATUS_BY_CODE in tools/souji-preservation-evidence.py; the checker's
# exit code is its stable contract, so the verdict is mapped from it rather
# than parsed out of the human-readable first line.
VERDICT_BY_STATUS = {0: "clean", 1: "failed", 2: "could-not-evaluate"}
ARMS = (("baseline_preharm", "a31642d"), ("baseline", "cc21683"))
CASE_RE = re.compile(r"CASE\t([^\t]+)\t(PASS|FAIL)\t(.*)\Z")
SUMMARY_RE = re.compile(r"SUMMARY\ttotal=([0-9]+)\tfailed=([0-9]+)\Z")


def git(*args: str, text: bool = True):
    return subprocess.run(["git", "-C", str(LANE), *args], check=True,
                          capture_output=True, text=text).stdout


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_arm(fixture: str, tool: Path, commit: str) -> dict:
    argv = ["timeout", "300", "python3", "-B", fixture, "--tool", str(tool)]
    proc = subprocess.run(argv, cwd=str(LANE), capture_output=True, text=True,
                          errors="replace")
    stdout = proc.stdout
    cases = []
    summary = None
    for line in stdout.splitlines():
        m = CASE_RE.match(line)
        if m:
            cases.append({"id": m.group(1), "status": m.group(2).lower(),
                          "detail": m.group(3).replace("\t", " ")})
        m = SUMMARY_RE.match(line)
        if m:
            summary = {"total": int(m.group(1)), "failed": int(m.group(2))}
    if summary is None or proc.returncode not in (0, 1):
        raise SystemExit(f"regenerate: {fixture} on {commit} could not evaluate "
                         f"(rc={proc.returncode})")
    return {
        "tool": {"commit": commit, "sha256": sha_bytes(tool.read_bytes())},
        "argv": argv,
        "exit_code": proc.returncode,
        "timed_out": False,
        "stdout": stdout,
        "stdout_sha256": sha_bytes(stdout.encode("utf-8")),
        "stdout_bytes_total": len(stdout.encode("utf-8")),
        "stdout_truncated": False,
        "stderr": "",
        "cases": cases,
        "summary": summary,
    }

def run_checker(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(LANE / CHECKER), *args],
        capture_output=True, text=True, errors="replace")


def evaluate_record(record_text: str):
    """Return the checker's (verdict, output) for the generated record.

    Uses the same evaluation `--frozen` performs on the pinned record:
    `--root <lane> --record <text>`."""
    proc = run_checker("--root", str(LANE), "--record", record_text)
    verdict = VERDICT_BY_STATUS.get(proc.returncode)
    if verdict is None:
        raise SystemExit(
            f"regenerate: checker exited {proc.returncode} (not a verdict): "
            f"{proc.stderr.strip() or proc.stdout.strip()}")
    return verdict, proc.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", required=True)
    ap.add_argument("--allow-nonclean", action="store_true",
                    help="write the record even when the checker's own "
                         "verdict is not clean (the computed verdict is "
                         "recorded, never 'clean')")
    args = ap.parse_args()
    rev = git("rev-parse", args.rev).strip()
    for rel in (TOOL, CONFIG_FIXTURE, NS_FIXTURE):
        committed = subprocess.run(["git", "-C", str(LANE), "show", f"{rev}:{rel}"],
                                   check=True, capture_output=True).stdout
        if committed != (LANE / rel).read_bytes():
            print(f"regenerate: {rel} differs between {rev[:12]} and the worktree",
                  file=sys.stderr)
            return 2
    scratch = Path(tempfile.mkdtemp(prefix="souji-r16-repin."))
    try:
        runs = {}
        tools = {}
        for arm, short in ARMS + (("changed", rev),):
            full = git("rev-parse", short).strip()
            tool = scratch / arm / "tools" / "souji-census.sh"
            tool.parent.mkdir(parents=True)
            tool.write_bytes(subprocess.run(
                ["git", "-C", str(LANE), "show", f"{full}:{TOOL}"],
                check=True, capture_output=True).stdout)
            tool.chmod(0o755)
            tools[arm] = (tool, full)
            runs[arm] = run_arm(CONFIG_FIXTURE, tool, full)
        tool, full = tools["changed"]
        namespace = run_arm(NS_FIXTURE, tool, full)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    record = {
        "schema": "souji-preservation-record-v1",
        "declared_consistency_only": True,
        "measured_commit": rev,
        "fixture": {"path": CONFIG_FIXTURE, "sha256": sha_bytes((LANE / CONFIG_FIXTURE).read_bytes())},
        "namespace_fixture": {"path": NS_FIXTURE, "sha256": sha_bytes((LANE / NS_FIXTURE).read_bytes())},
        "runs": runs,
        "namespace_controls": namespace,
    }
    record_text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    verdict, checker_out = evaluate_record(record_text)
    if verdict != "clean" and not args.allow_nonclean:
        print(f"regenerate: checker verdict is {verdict!r}, not 'clean'; "
              "refusing to write record.json/expected.json "
              "(rerun with --allow-nonclean to record it)",
              file=sys.stderr)
        sys.stderr.write(checker_out)
        return 3
    (HERE / "record.json").write_text(record_text, encoding="utf-8")
    expected = {
        "files": {rel: sha_bytes((LANE / rel).read_bytes())
                  for rel in (NS_FIXTURE, CONFIG_FIXTURE, TOOL)},
        "record": "record.json",
        "record_sha256": sha_bytes(record_text.encode("utf-8")),
        "verdict": verdict,
    }
    (HERE / "expected.json").write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n",
                                        encoding="utf-8")
    frozen = run_checker("--frozen", str(HERE), "--root", str(LANE))
    if VERDICT_BY_STATUS.get(frozen.returncode) != verdict:
        print(f"regenerate: frozen re-check exited {frozen.returncode}, "
              f"expected a {verdict!r} verdict; files left written:",
              file=sys.stderr)
        sys.stderr.write(frozen.stdout)
        return 2
    if verdict != "clean":
        print(f"regenerate: --allow-nonclean accepted verdict={verdict!r}",
              file=sys.stderr)
    print(f"regenerated at {rev[:12]}: " + ", ".join(
        f"{arm}={r['summary']['failed']}/{r['summary']['total']} fail" for arm, r in runs.items())
        + f", namespace={namespace['summary']['failed']}/{namespace['summary']['total']} fail"
        + f", verdict={verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
