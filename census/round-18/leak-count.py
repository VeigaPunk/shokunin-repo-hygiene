#!/usr/bin/env python3
"""Independently count current-UID processes referencing deleted scratch paths."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections import Counter
from typing import Any

SCRATCH_PREFIXES = ("/var/tmp", "/dev/shm", "/tmp")
DELETED_SUFFIX = " (deleted)"
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
        if not path.startswith(prefix + "/"):
            continue
        relative = path[len(prefix) + 1 :]
        top_level = relative.split("/", 1)[0]
        if not top_level or top_level in (".", ".."):
            return None
        if require_missing and os.path.exists(os.path.join(prefix, top_level)):
            return None
        family = top_level.split(".", 1)[0]
        return family if family in KNOWN_FAMILIES else "other"
    return None


def _proc_link_is_deleted(proc_link: str, target: str) -> bool:
    if not target.endswith(DELETED_SUFFIX):
        return False
    try:
        link_stat = os.stat(proc_link)
    except OSError:
        return False
    try:
        target_stat = os.stat(target)
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return (link_stat.st_dev, link_stat.st_ino) != (target_stat.st_dev, target_stat.st_ino)


def _argv_missing_scratch_family(argv: list[str]) -> str | None:
    for argument in argv:
        candidate: str | None = None
        if os.path.isabs(argument):
            candidate = argument
        elif argument.startswith("--") and "=" in argument:
            option, candidate = argument.split("=", 1)
            if len(option) <= 2 or not os.path.isabs(candidate):
                continue
        if candidate is None:
            continue
        family = _family_for_scratch_path(candidate, require_missing=True)
        if family is None or os.path.exists(candidate):
            continue
        return family
    return None


def _fd_missing_scratch_family(proc_path: str) -> str | None:
    fd_dir = os.path.join(proc_path, "fd")
    try:
        with os.scandir(fd_dir) as entries:
            fd_names = sorted(entry.name for entry in entries)
    except OSError:
        return None

    for fd_name in fd_names:
        fd_link = os.path.join(fd_dir, fd_name)
        try:
            target = os.readlink(fd_link)
        except OSError:
            continue
        if not _proc_link_is_deleted(fd_link, target):
            continue
        family = _family_for_scratch_path(
            target[: -len(DELETED_SUFFIX)], require_missing=True
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
    cwd_link = os.path.join(proc_path, "cwd")
    try:
        cwd = os.readlink(cwd_link)
    except OSError:
        cwd = ""
    if _proc_link_is_deleted(cwd_link, cwd):
        family = _family_for_scratch_path(
            cwd[: -len(DELETED_SUFFIX)], require_missing=False
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
    # The standalone counter spawns no scan children; exclude only itself.
    # Ancestors are legitimate observations, not its own subtree. Excluding
    # them hid Hyprland's deleted shm fd when launched through the GUI (the
    # final two-window comparison exposed this stable disagreement).
    excluded_pids = {os.getpid()}
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
            if pid in excluded_pids or _uid_from_status(proc_path) != uid:
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


def _stop_test_process(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _selftest_edge_cases() -> None:
    dangling_root = tempfile.mkdtemp(prefix="souji-proc-census-dangling-", dir="/var/tmp")
    shutil.rmtree(dangling_root)
    os.symlink(os.path.join(dangling_root, "target"), dangling_root)
    candidate = os.path.join(dangling_root, "payload")
    try:
        if os.path.exists(dangling_root):
            raise RuntimeError("dangling-symlink top-level unexpectedly exists")
        if _family_for_scratch_path(candidate, require_missing=True) != "other":
            raise RuntimeError("dangling-symlink top-level was not treated as missing")
        if _argv_missing_scratch_family([candidate]) != "other":
            raise RuntimeError("full absolute argv path was not recognized")
        if _argv_missing_scratch_family([f"--input={candidate}"]) != "other":
            raise RuntimeError("--option=/absolute argv path was not recognized")
        if _argv_missing_scratch_family([f"embedded text {candidate}"]) is not None:
            raise RuntimeError("embedded argv path substring was incorrectly recognized")
        if _family_for_scratch_path(candidate.replace("/var/tmp/", "/tmpfoo/", 1), require_missing=True) is not None:
            raise RuntimeError("component-boundary check matched /tmpfoo as /tmp")
    finally:
        os.unlink(dangling_root)

    literal_cwd_root = tempfile.mkdtemp(prefix="souji-proc-census-literal-cwd-", dir="/var/tmp")
    literal_cwd = os.path.join(literal_cwd_root, "literal (deleted)")
    os.mkdir(literal_cwd)
    cwd_process: subprocess.Popen[bytes] | None = None
    try:
        cwd_process = subprocess.Popen(
            ["sleep", "30"],
            cwd=literal_cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        proc_path = f"/proc/{cwd_process.pid}"
        cwd_link = os.path.join(proc_path, "cwd")
        target = os.readlink(cwd_link)
        if not target.endswith(DELETED_SUFFIX) or _proc_link_is_deleted(cwd_link, target):
            raise RuntimeError("live literal cwd suffix was misclassified as deleted")
        if _primary_reason_and_family(proc_path, _argv_for_pid(proc_path)) is not None:
            raise RuntimeError("live literal cwd suffix produced a residue classification")
    finally:
        if cwd_process is not None:
            _stop_test_process(cwd_process)
        shutil.rmtree(literal_cwd_root, ignore_errors=True)

    literal_fd_root = tempfile.mkdtemp(prefix="souji-proc-census-literal-fd-", dir="/var/tmp")
    literal_fd_path = os.path.join(literal_fd_root, "literal (deleted)")
    literal_fd = os.open(literal_fd_path, os.O_CREAT | os.O_RDWR, 0o600)
    literal_fd_process: subprocess.Popen[bytes] | None = None
    try:
        literal_fd_process = subprocess.Popen(
            ["sleep", "30"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            pass_fds=(literal_fd,),
        )
        fd_link = f"/proc/{literal_fd_process.pid}/fd/{literal_fd}"
        target = os.readlink(fd_link)
        if not target.endswith(DELETED_SUFFIX) or _proc_link_is_deleted(fd_link, target):
            raise RuntimeError("live literal fd suffix was misclassified as deleted")
        if _primary_reason_and_family(
            f"/proc/{literal_fd_process.pid}", _argv_for_pid(f"/proc/{literal_fd_process.pid}")
        ) is not None:
            raise RuntimeError("live literal fd suffix produced a residue classification")
    finally:
        os.close(literal_fd)
        if literal_fd_process is not None:
            _stop_test_process(literal_fd_process)
        shutil.rmtree(literal_fd_root, ignore_errors=True)

    deleted_fd_root = tempfile.mkdtemp(prefix="souji-proc-census-deleted-fd-", dir="/var/tmp")
    deleted_fd_path = os.path.join(deleted_fd_root, "held-file")
    deleted_fd = os.open(deleted_fd_path, os.O_CREAT | os.O_RDWR, 0o600)
    deleted_fd_process: subprocess.Popen[bytes] | None = None
    try:
        deleted_fd_process = subprocess.Popen(
            ["sleep", "30"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            pass_fds=(deleted_fd,),
        )
        os.close(deleted_fd)
        deleted_fd = -1
        shutil.rmtree(deleted_fd_root)
        result = _primary_reason_and_family(
            f"/proc/{deleted_fd_process.pid}", _argv_for_pid(f"/proc/{deleted_fd_process.pid}")
        )
        if result != ("fd-path-gone", "other"):
            raise RuntimeError(f"deleted fd was not classified correctly: {result!r}")
    finally:
        if deleted_fd >= 0:
            os.close(deleted_fd)
        if deleted_fd_process is not None:
            _stop_test_process(deleted_fd_process)
        shutil.rmtree(deleted_fd_root, ignore_errors=True)


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
    _selftest_edge_cases()
    before = count_processes()
    test_dir = tempfile.mkdtemp(prefix="souji-proc-census-selftest-", dir="/var/tmp")
    fifo_path = os.path.join(test_dir, "blocked-reader")
    process: subprocess.Popen[bytes] | None = None
    try:
        os.mkfifo(fifo_path)
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
            _stop_test_process(process)


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
