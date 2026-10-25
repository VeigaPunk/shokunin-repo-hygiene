#!/usr/bin/env python3
"""r25 regression witness: verify must read counts from stdout, never stderr."""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OLD_RUNNER_REV = "c872eec"
TOOL_PATH = "tools/souji-record-agreement.py"
COUNTS = "keys=4 records=3 occurrences=13 mismatches=0"
FULL_REV = re.compile(r"[0-9a-fA-F]{40}")
SCRATCH = "/var/tmp"


def run(argv: list[str], *, cwd: str | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=30, check=False)


def git(root: str, *args: str) -> bytes:
    proc = run(["git", "-C", root, *args])
    if proc.returncode != 0:
        raise RuntimeError(f"git {args!r} failed rc={proc.returncode}: {proc.stderr!r}")
    return proc.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--rev", required=True)
    args = parser.parse_args()
    if not FULL_REV.fullmatch(args.rev):
        print("R7-COUNTS-STDERR status=FAIL reason=rev-not-full", file=sys.stderr)
        return 2

    root = str(Path(args.root).resolve())
    try:
        git(root, "rev-parse", "--verify", "--quiet", f"{args.rev}^{{commit}}")
        tool_blob = git(root, "show", f"{args.rev}:{TOOL_PATH}")
        tool_sha = hashlib.sha256(tool_blob).hexdigest()
        old_blob = git(root, "show", f"{OLD_RUNNER_REV}:tools/souji-receipt-run.py")
    except RuntimeError as exc:
        print(f"R7-COUNTS-STDERR status=COULD-NOT-EVALUATE error={exc}", file=sys.stderr)
        return 2

    scratch = tempfile.mkdtemp(prefix="souji-r25-r7-", dir=SCRATCH)
    try:
        old_runner = Path(scratch) / "old-receipt-run.py"
        receipt = Path(scratch) / "stderr-only.tsv"
        old_runner.write_bytes(old_blob)
        receipt.write_text(
            "receipt=v1\n"
            f"rev={args.rev}\n"
            f"tool={TOOL_PATH}\n"
            f"tool_sha256={tool_sha}\n"
            f"cmd=python3 -B {TOOL_PATH} --rev {args.rev} --no-worktree\n"
            "rc=0\n"
            "utc=2026-10-25T00:00:00Z\n"
            "--- stdout ---\n"
            "\n"
            "--- stderr ---\n"
            f"{COUNTS}\n",
            encoding="utf-8",
        )
        old = run([sys.executable, "-B", str(old_runner), "verify", "--root", root,
                   str(receipt)])
        new = run([sys.executable, "-B", str(Path(root) / "tools/souji-receipt-run.py"),
                   "verify", "--root", root, str(receipt)])
        old_text = (old.stdout + old.stderr).decode("utf-8", "replace")
        new_text = (new.stdout + new.stderr).decode("utf-8", "replace")
        old_ok = old.returncode == 0 and "verify=ok" in old_text
        new_refused = new.returncode == 2 and "RECEIPT-COUNTS-ABSENT" in new_text
        print(f"case=R7-COUNTS-STDERR old_rc={old.returncode} old_verify_ok={old_ok}")
        print(f"case=R7-COUNTS-STDERR new_rc={new.returncode} new_counts_absent={new_refused}")
        verdict = old_ok and new_refused
        print(f"cases=1 pass={int(verdict)}")
        return 0 if verdict else 1
    finally:
        shutil.rmtree(scratch)


if __name__ == "__main__":
    raise SystemExit(main())
