#!/usr/bin/env python3
"""Independently count current-UID processes referencing deleted scratch paths."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections import Counter
from typing import Any

SCRATCH_PREFIXES = ("/var/tmp", "/dev/shm", "/tmp")
PATH_RE = re.compile(r"/(?:var/tmp|dev/shm|tmp)(?:/[^\s\"'`<>|;&]*)?")
TRAILING_PATH_PUNCTUATION = ".,:;)]}"
KNOWN_FAMILIES = ("r15-census-config", "r17-census-hygiene")


def _uid_from_status(proc_path: str) -> int | None:
    try:
        with open(os.path.join(proc_path, "status"), "r", encoding="ascii", errors="replace") as status:
            for line in status:
                if line.startswith("Uid:"):
                    return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        return None
    return None


def _family_for_scratch_path(path: str, *, require_missing: bool) -> str | None:
    for prefix in SCRATCH_PREFIXES:
        # Require a component boundary: /tmp/ is in scope, /tmpfoo/ is not.
        if not path.startswith(prefix + "/"):
            continue
        relative = path[len(prefix) + 1 :]
        top_level = relative.split("/", 1)[0]
        if not top_level or top_level in (".", ".."):
            return None
        if require_missing and os.path.lexists(os.path.join(prefix, top_level)):
            return None
        family = top_level.split(".", 1)[0]
        return family if family in KNOWN_FAMILIES else "other"
    return None


def _argv_missing_scratch_family(argv: list[str]) -> str | None:
    for argument in argv:
        for match in PATH_RE.finditer(argument):
            start = match.start()
            if start and argument[start - 1] == "/":
                continue
            candidate = match.group(0)
            while candidate and candidate[-1] in TRAILING_PATH_PUNCTUATION:
                candidate = candidate[:-1]
            family = _family_for_scratch_path(candidate, require_missing=True)
            if family is not None:
                return family
    return None


def _fd_missing_scratch_family(proc_path: str) -> str | None:
    fd_dir = os.path.join(proc_path, "fd")
    try:
        with os.scandir(fd_dir) as entries:
            fd_names = sorted(entry.name for entry in entries)
    except OSError:
        return None

    deleted_suffix = " (deleted)"
    for fd_name in fd_names:
        try:
            target = os.readlink(os.path.join(fd_dir, fd_name))
        except OSError:
            continue
        if not target.endswith(deleted_suffix):
            continue
        family = _family_for_scratch_path(
            target[: -len(deleted_suffix)], require_missing=True
        )
        if family is not None:
            return family
    return None


def _argv_for_pid(proc_path: str) -> list[str]:
    try:
        with open(os.path.join(proc_path, "cmdline"), "rb") as cmdline:
            raw = cmdline.read()
    except OSError:
        return []
    return [item.decode("utf-8", errors="surrogateescape") for item in raw.split(b"\0") if item]


def _primary_reason_and_family(proc_path: str, argv: list[str]) -> tuple[str, str] | None:
    deleted_suffix = " (deleted)"
    try:
        cwd = os.readlink(os.path.join(proc_path, "cwd"))
    except OSError:
        cwd = ""
    if cwd.endswith(deleted_suffix):
        family = _family_for_scratch_path(
            cwd[: -len(deleted_suffix)], require_missing=False
        )
        return "cwd-deleted", family or "other"

    family = _argv_missing_scratch_family(argv)
    if family is not None:
        return "argv-path-gone", family

    family = _fd_missing_scratch_family(proc_path)
    if family is not None:
        return "fd-path-gone", family
    return None


def count_processes() -> dict[str, Any]:
    uid = os.getuid()
    pids: list[int] = []
    reason_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()

    try:
        entries = os.scandir("/proc")
    except OSError as exc:
        raise RuntimeError(f"cannot enumerate /proc: {exc}") from exc

    with entries:
        for entry in entries:
            if not entry.name.isdecimal():
                continue
            proc_path = entry.path
            try:
                pid = int(entry.name)
            except ValueError:
                continue
            if _uid_from_status(proc_path) != uid:
                continue

            result = _primary_reason_and_family(proc_path, _argv_for_pid(proc_path))
            if result is None:
                continue
            reason, family = result
            pids.append(pid)
            reason_counts[reason] += 1
            family_counts[family] += 1

    return {
        "counted_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "uid": uid,
        "total": len(pids),
        "by_reason": {
            "cwd-deleted": reason_counts["cwd-deleted"],
            "argv-path-gone": reason_counts["argv-path-gone"],
            "fd-path-gone": reason_counts["fd-path-gone"],
        },
        "by_prefix_family": {
            "r15-census-config": family_counts["r15-census-config"],
            "r17-census-hygiene": family_counts["r17-census-hygiene"],
            "other": family_counts["other"],
        },
        "pids": sorted(pids),
    }


def _wait_for_fifo_open(pid: int, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    wchan_path = f"/proc/{pid}/wchan"
    while time.monotonic() < deadline:
        try:
            with open(wchan_path, "r", encoding="ascii", errors="replace") as wchan_file:
                wchan = wchan_file.read().strip()
        except OSError:
            return False
        if "wait_for_partner" in wchan:
            return True
        time.sleep(0.01)
    return False


def run_selftest() -> dict[str, Any]:
    if _family_for_scratch_path("/tmpfoo/missing", require_missing=True) is not None:
        raise RuntimeError("component-boundary check matched /tmpfoo as /tmp")
    before = count_processes()
    test_dir = tempfile.mkdtemp(prefix="souji-proc-census-selftest-", dir="/var/tmp")
    fifo_path = os.path.join(test_dir, "blocked-reader")
    os.mkfifo(fifo_path)
    process: subprocess.Popen[bytes] | None = None
    try:
        process = subprocess.Popen(
            ["cat", fifo_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
        )
        if not _wait_for_fifo_open(process.pid):
            raise RuntimeError("FIFO reader did not reach the blocking open")
        shutil.rmtree(test_dir)
        test_dir = ""
        after = count_processes()
        expected_pid = process.pid
        if after["total"] != before["total"] + 1 or expected_pid not in after["pids"]:
            raise RuntimeError(
                "deleted FIFO reader was not counted exactly once "
                f"(before={before['total']}, after={after['total']}, pid={expected_pid})"
            )
        if after["by_reason"]["argv-path-gone"] != before["by_reason"]["argv-path-gone"] + 1:
            raise RuntimeError("selftest reader was not counted for its missing argv scratch path")
        return {
            "selftest": "pass",
            "before": before["total"],
            "after": after["total"],
            "added_pid": expected_pid,
        }
    finally:
        if test_dir:
            shutil.rmtree(test_dir, ignore_errors=True)
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # The process group kill is authoritative; this is only a bounded reap.
                process.kill()
                process.wait(timeout=5)


def _write_json_exclusive(path: str, payload: dict[str, Any]) -> None:
    with open(path, "x", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, sort_keys=True)
        output.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--selftest", action="store_true", help="run a bounded FIFO-reader detection test")
    mode.add_argument("--json", metavar="OUT", help="write census JSON to a new file (exclusive create)")
    args = parser.parse_args(argv)

    try:
        result = run_selftest() if args.selftest else count_processes()
        if args.json is not None:
            _write_json_exclusive(args.json, result)
        else:
            json.dump(result, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
    except (OSError, RuntimeError) as exc:
        print(f"leak-count: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
