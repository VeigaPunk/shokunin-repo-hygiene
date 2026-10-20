#!/usr/bin/env python3
"""Round-18 C1 measurement matrix for tools/souji-census.sh.

Arms: pre-harm a31642d, r14-harm cc21683, r17 base b5763415..., and the
selected changed revision or WORKTREE. Every arm runs bash -n, shellcheck,
the census --selftest, and each current fixture suite. Every command runs in
its own session. After a suite, remaining members of its runner-created
session are killed by session ID; argv-prefix matches are counted afterward
as residue and are never used as kill targets.

Usage: python3 census/round-18/run-matrix.py --changed <rev|WORKTREE> \
       --output <new.json>
The output is exclusive-create; temporary arm files are removed afterwards.

A missing fixture remains an unevaluable suite in the written record rather
than aborting the whole matrix. Its fixture hash is null and each arm's suite
record explains the missing path. Existing fixtures are still measured.

Fixture output validity follows the round-17 contract: a nonempty SUMMARY,
exactly its total non-synthetic CASE rows, matching FAIL count, and rc 0 for
zero failures or rc 1 otherwise. A synthetic id-set FAIL is additional data,
not an invalid run. A selftest that ran and reports failures remains data;
a bash/shellcheck/selftest command that could not run is included in
invalid_suites.

Exit: 0 record written and all fixture suites valid; 2 output exists, dirty
fixtures without --allow-dirty-fixtures, unknown revision, or an invalid
suite/unrunnable check; 1 runner/OS error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

LANE = Path(__file__).resolve().parents[2]
ARMS = (
    ("pre-harm", "a31642d"),
    ("r14-harm", "cc21683"),
    ("r17-base", "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3"),
)
# suite key -> (filename, selector carrying the census path, private /var/tmp
# argv prefix used for the post-session residue count)
FIXTURES = {
    "r18-bounded": ("r18-census-bounded.py", "--census",
                    "/var/tmp/souji-r18-FixtureR18Bounded/fixture."),
    "r17-hygiene": ("r17-census-hygiene.py", "--census", "r17-census-hygiene."),
    "r15-config": ("r15-census-config.py", "--tool", "r15-census-config."),
    "r14-namespace": ("r14-census-boundary.py", "--tool", "r14-census-boundary."),
}
SELFTEST_PREFIX = "souji-census-selftest."
CASE_RE = re.compile(r"^CASE\t(\S+)\t(PASS|FAIL)\t(.*)$")
SUMMARY_RE = re.compile(r"^SUMMARY\ttotal=(\d+)\tfailed=(\d+)")
SELFTEST_RE = re.compile(r"^selftest: (\d+) checks, (\d+) failed")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(LANE), *args], check=True,
                          capture_output=True, text=True).stdout


def process_info(pid: int) -> tuple[int, str] | None:
    """Return the /proc stat session ID (field 6) and start-time ticks."""
    try:
        text = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
    except OSError:
        return None
    _, close, tail = text.rpartition(")")
    fields = tail.split() if close else []
    if len(fields) <= 19:
        return None
    try:
        return int(fields[3]), fields[19]
    except ValueError:
        return None


def kill_session(session_id: int) -> list[dict]:
    """Kill only same-uid processes whose /proc stat field 6 is SESSION_ID."""
    try:
        entries = list(os.scandir("/proc"))
    except OSError:
        return []
    members = []
    for entry in entries:
        if not entry.name.isdecimal():
            continue
        pid = int(entry.name)
        try:
            if entry.stat().st_uid != os.getuid():
                continue
        except OSError:
            continue
        info = process_info(pid)
        if info and info[0] == session_id:
            members.append((pid, info[1]))

    killed = []
    for pid, start_time in sorted(members):
        item = {"pid": pid, "kill_sent": False, "kill_error": None}
        pidfd = None
        try:
            if hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal"):
                pidfd = os.pidfd_open(pid)
                info = process_info(pid)
                if not info or info != (session_id, start_time):
                    item["kill_error"] = "already-exited-or-session-changed"
                else:
                    signal.pidfd_send_signal(pidfd, signal.SIGKILL)
                    item["kill_sent"] = True
            else:
                info = process_info(pid)
                if not info or info != (session_id, start_time):
                    item["kill_error"] = "already-exited-or-session-changed"
                else:
                    os.kill(pid, signal.SIGKILL)
                    item["kill_sent"] = True
        except ProcessLookupError:
            item["kill_error"] = "already-exited"
        except PermissionError:
            item["kill_error"] = "permission-denied"
        except OSError as exc:
            item["kill_error"] = f"os-error:{exc.errno}"
        finally:
            if pidfd is not None:
                try:
                    os.close(pidfd)
                except OSError:
                    pass
        killed.append(item)
    return killed


def leftover_processes(prefix: str) -> list[dict]:
    """Snapshot argv-prefix matches as (PID, start-time) identities."""
    needle = prefix.encode()
    try:
        entries = list(os.scandir("/proc"))
    except OSError:
        return []
    processes = []
    for entry in entries:
        if not entry.name.isdecimal():
            continue
        pid = int(entry.name)
        try:
            if entry.stat().st_uid != os.getuid():
                continue
            info_before = process_info(pid)
            if not info_before:
                continue
            argv = Path(entry.path, "cmdline").read_bytes()
            info_after = process_info(pid)
        except OSError:
            continue
        if needle in argv and info_after == info_before:
            processes.append({"pid": pid, "start_time": info_after[1]})
    return sorted(processes, key=lambda process: process["pid"])


def new_processes(before: list[dict], after: list[dict]) -> list[dict]:
    prior = {(process["pid"], process["start_time"]) for process in before}
    return [process for process in after
            if (process["pid"], process["start_time"]) not in prior]


def run(cmd: list[str], timeout: int = 900
        ) -> tuple[int, str, str, bool, bool, dict]:
    """Run in a new session; reap only members of this process's session."""
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            errors="replace", start_new_session=True,
        )
    except OSError as exc:
        return 127, "", f"cannot run {cmd[0]}: {exc}", False, False, {
            "session_id": None, "killed": [],
        }
    session = {"session_id": proc.pid, "killed": []}
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        session["killed"] = kill_session(proc.pid)
        return proc.returncode, stdout, stderr, True, False, session
    except subprocess.TimeoutExpired:
        session["killed"] = kill_session(proc.pid)
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            proc.wait()
        if proc.stdout is not None:
            proc.stdout.close()
        if proc.stderr is not None:
            proc.stderr.close()
        return 124, "", "timeout", True, True, session


def suite(fixture: Path, tool: Path, selector: str,
          temp_prefix: str) -> dict:
    preexisting = leftover_processes(temp_prefix)
    if not fixture.is_file():
        return {
            "rc": None, "total": None, "failed": None, "cases": {},
            "valid": False, "ran": False,
            "stderr_tail": [f"missing fixture: {fixture}"],
            "session_cleanup": {"session_id": None, "killed": []},
            "preexisting_leftover_procs": preexisting,
            "preexisting_leftover_procs_count": len(preexisting),
            "leftover_procs": [], "leftover_procs_count": 0,
        }

    rc, stdout, stderr, started, timed_out, session = run(
        [sys.executable, str(fixture), selector, str(tool)])
    leftovers = new_processes(preexisting, leftover_processes(temp_prefix))
    cases: dict[str, dict] = {}
    total = failed = None
    for line in stdout.splitlines():
        match = CASE_RE.match(line)
        if match:
            cases[match.group(1)] = {
                "verdict": match.group(2), "detail": match.group(3),
            }
        match = SUMMARY_RE.match(line)
        if match:
            total, failed = int(match.group(1)), int(match.group(2))
    synthetic = int("id-set" in cases)
    valid = (
        started and not timed_out
        and isinstance(total, int) and total > 0
        and isinstance(failed, int) and 0 <= failed <= total + synthetic
        and rc == (1 if failed else 0)
        and len(cases) - synthetic == total
        and sum(case["verdict"] == "FAIL" for case in cases.values()) == failed
    )
    return {
        "rc": rc, "total": total, "failed": failed, "cases": cases,
        "valid": valid, "ran": started and not timed_out,
        "stderr_tail": stderr.strip().splitlines()[-3:],
        "session_cleanup": session,
        "preexisting_leftover_procs": preexisting,
        "preexisting_leftover_procs_count": len(preexisting),
        "leftover_procs": leftovers,
        "leftover_procs_count": len(leftovers),
    }


def version(cmd: list[str], line: int = 0) -> str | None:
    rc, stdout, stderr, started, timed_out, _session = run(cmd, timeout=20)
    if not started or timed_out or rc != 0:
        return None
    lines = (stdout or stderr).strip().splitlines()
    return lines[line] if len(lines) > line else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed", required=True, help="revision or WORKTREE")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--fixture-dir",
        help="directory to resolve fixture names in, instead of tests/fixtures",
    )
    parser.add_argument(
        "--allow-dirty-fixtures", action="store_true",
        help="record modified or untracked lane fixtures instead of refusing",
    )
    args = parser.parse_args()

    out = Path(args.output)
    if not out.is_absolute():
        out = LANE / out
    if out.exists():
        print(f"run-matrix: refusing to overwrite {out}", file=sys.stderr)
        return 2

    fixture_dir = Path(args.fixture_dir) if args.fixture_dir else LANE / "tests/fixtures"
    fixtures = {key: fixture_dir / spec[0] for key, spec in FIXTURES.items()}
    fixture_hashes = {
        key: hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        for key, path in fixtures.items()
    }
    lane_paths = [str(path.resolve().relative_to(LANE))
                  for path in fixtures.values()
                  if path.resolve().is_relative_to(LANE)]
    fixtures_in_lane = len(lane_paths) == len(fixtures)
    fixtures_dirty = (
        git("status", "--porcelain", "--", *lane_paths).strip()
        if fixtures_in_lane else None
    )
    if fixtures_dirty and not args.allow_dirty_fixtures:
        print("run-matrix: fixture files are dirty, refusing to record:\n"
              + fixtures_dirty
              + "\nrun-matrix: pass --allow-dirty-fixtures to record anyway",
              file=sys.stderr)
        return 2

    try:
        git("rev-parse", "--verify", "--end-of-options", "refs/heads/master")
        git_head = git("rev-parse", "HEAD").strip()
        lane_head = git("rev-parse", "refs/heads/master").strip()
        if args.changed == "WORKTREE":
            changed_rev = "WORKTREE"
        else:
            changed_rev = git("rev-parse", "--verify", "--end-of-options",
                              f"{args.changed}^{{commit}}").strip()
    except subprocess.CalledProcessError:
        print(f"run-matrix: unknown changed revision {args.changed!r}",
              file=sys.stderr)
        return 2

    record = {
        "record_schema": 3,
        "lane_head": lane_head,
        "git_head": git_head,
        "changed": args.changed,
        "changed_rev": changed_rev,
        "fixture_dir": str(fixture_dir) if args.fixture_dir else None,
        "allow_dirty_fixtures": args.allow_dirty_fixtures,
        "fixtures": {key: str(path) for key, path in fixtures.items()},
        "fixtures_sha256": fixture_hashes,
        "fixtures_dirty": fixtures_dirty,
        "git_version": version(["git", "--version"]),
        "bash_version": version(["bash", "--version"]),
        "shellcheck_version": version(["shellcheck", "--version"], line=1),
        "python_version": sys.version.split()[0],
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "arms": {},
    }

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        scratch = Path(tempfile.mkdtemp(
            prefix="souji-r18-matrix.", dir=str(out.parent)))
    except OSError as exc:
        print(f"run-matrix: cannot create scratch beside {out}: {exc}",
              file=sys.stderr)
        return 1
    try:
        arms = list(ARMS) + [("changed", changed_rev)]
        for arm_name, revision in arms:
            tool = scratch / arm_name / "tools" / "souji-census.sh"
            tool.parent.mkdir(parents=True)
            if revision == "WORKTREE":
                shutil.copyfile(LANE / "tools/souji-census.sh", tool)
                full_revision = "WORKTREE"
            else:
                resolved = (revision if arm_name == "changed" else
                            git("rev-parse", "--verify", "--end-of-options",
                                f"{revision}^{{commit}}").strip())
                tool.write_bytes(subprocess.run(
                    ["git", "-C", str(LANE), "show",
                     f"{resolved}:tools/souji-census.sh"],
                    check=True, capture_output=True,
                ).stdout)
                full_revision = resolved
            tool.chmod(0o755)
            arm = {
                "rev": full_revision,
                "sha256": hashlib.sha256(tool.read_bytes()).hexdigest(),
            }

            rc, _, err, started, timed_out, _session = run(
                ["bash", "-n", str(tool)])
            arm["bash_n"] = {
                "rc": rc, "stderr": err.strip().splitlines()[:2],
                "started": started, "timed_out": timed_out,
                "ran": started and not timed_out,
            }

            rc, shellcheck_out, shellcheck_err, started, timed_out, _session = run(
                ["shellcheck", "-S", "warning", str(tool)])
            arm["shellcheck_warning"] = {
                "rc": rc,
                "findings": len(re.findall(r"\(warning\)|\(error\)", shellcheck_out)),
                "stderr": shellcheck_err.strip().splitlines()[:2],
                "started": started, "timed_out": timed_out,
                "ran": started and not timed_out,
            }

            selftest_preexisting = leftover_processes(SELFTEST_PREFIX)
            rc, selftest_out, selftest_err, started, timed_out, session = run(
                ["bash", str(tool), "--selftest"], timeout=600)
            selftest_leftovers = new_processes(
                selftest_preexisting, leftover_processes(SELFTEST_PREFIX))
            selftest_match = None
            for line in selftest_out.splitlines() + selftest_err.splitlines():
                selftest_match = SELFTEST_RE.match(line) or selftest_match
            selftest_found = selftest_match is not None
            arm["selftest"] = {
                "rc": rc,
                "checks": int(selftest_match.group(1)) if selftest_found else None,
                "failed": int(selftest_match.group(2)) if selftest_found else None,
                "started": started, "timed_out": timed_out,
                "ran": started and not timed_out and selftest_found,
                "stderr_tail": selftest_err.strip().splitlines()[-3:],
                "session_cleanup": session,
                "preexisting_leftover_procs": selftest_preexisting,
                "preexisting_leftover_procs_count": len(selftest_preexisting),
                "leftover_procs": selftest_leftovers,
                "leftover_procs_count": len(selftest_leftovers),
            }

            for key, fixture in fixtures.items():
                arm[key] = suite(fixture, tool, FIXTURES[key][1],
                                 FIXTURES[key][2])
            record["arms"][arm_name] = arm
            tally = "\t".join(
                f"{key}={arm[key]['total']}/{arm[key]['failed']}fail"
                for key in FIXTURES
            )
            print(f"{arm_name}\t{arm['sha256'][:12]}"
                  f"\tbash-n={arm['bash_n']['rc']}"
                  f"\tsc={arm['shellcheck_warning']['rc']}"
                  f"\tselftest={arm['selftest']['checks']}/"
                  f"{arm['selftest']['failed']}fail\t{tally}")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    invalid = []
    for arm_name, arm in record["arms"].items():
        for key in FIXTURES:
            if not arm[key]["valid"]:
                invalid.append(f"{arm_name}:{key}")
        if not arm["bash_n"]["ran"]:
            invalid.append(f"{arm_name}:bash-n")
        if not arm["shellcheck_warning"]["ran"]:
            invalid.append(f"{arm_name}:shellcheck-warning")
        if not arm["selftest"]["ran"]:
            invalid.append(f"{arm_name}:selftest")
    record["invalid_suites"] = invalid

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "x", encoding="utf-8") as stream:
            stream.write(json.dumps(record, indent=1, sort_keys=True) + "\n")
    except FileExistsError:
        print(f"run-matrix: refusing to overwrite {out}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"run-matrix: cannot write {out}: {exc}", file=sys.stderr)
        return 1

    if invalid:
        print(f"run-matrix: could not evaluate suites: {invalid}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
