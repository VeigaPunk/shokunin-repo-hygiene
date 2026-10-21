#!/usr/bin/env python3
"""run-acceptance — the round-19 reproducible acceptance record.

Runs every named r19 acceptance command against the installed bytes at an
explicit 40-hex revision, records exit/expected/evidence for each, and writes
one new JSON record. It refuses HEAD or a branch name (dogfooding C2), refuses
to overwrite an existing record, and never runs a live fleet census.

Usage:
  python3 census/round-19/run-acceptance.py --root . --rev <40-hex> \
      --output census/round-19/final-verification-<short>.json

Exit: 0 every command matched; 1 a command diverged; 2 usage/precondition.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(
    TMPDIR="/var/tmp",
    LC_ALL="C",
    PYTHONDONTWRITEBYTECODE="1",
    GIT_CONFIG_NOSYSTEM="1",
    GIT_TERMINAL_PROMPT="0",
)

CHANGED = [
    "tools/souji-landing-gate.py",
    "tools/souji-seat-audit.py",
    "tools/souji-rev-pin.py",
    "tests/fixtures/r19-carry-wrap.py",
    "tests/fixtures/r19-rev-pin.py",
    "tests/fixtures/r19-seat-audit-shapes.py",
    "tests/fixtures/r15-census-config.py",
    "tests/fixtures/r17-census-hygiene.py",
    "census/round-13/run-verification.py",
    "census/round-13/count-claims.py",
    "census/round-14/run-verification.py",
    "census/round-14/run-targeted.py",
    "census/round-14/count-claims.py",
    "census/round-14/cache-demonstration.py",
    "census/round-19/verify-agreement-pin.py",
]

COMMANDS = [
    ("gate-selftest", ["python3", "tools/souji-landing-gate.py", "--selftest"], 0),
    ("gate-replays", ["python3", "census/round-17/gate-replays.py",
                      "--output", "census/round-19/gate-replays-final.json"], 0),
    ("carry-fixture", ["python3", "tests/fixtures/r19-carry-wrap.py"], 0),
    ("rev-pin-fixture", ["python3", "tests/fixtures/r19-rev-pin.py"], 0),
    ("audit-shapes-fixture", ["python3", "tests/fixtures/r19-seat-audit-shapes.py"], 0),
    ("audit-selftest", ["python3", "tools/souji-seat-audit.py", "--selftest"], 0),
    ("agreement-pin-selftest",
     ["python3", "census/round-19/verify-agreement-pin.py", "--selftest"], 0),
    ("agreement-pin-check",
     ["python3", "census/round-19/verify-agreement-pin.py", "--root", ".",
      "--check", "census/round-19/proc-agreement-pinned.json"], 0),
    ("jj-receipts", ["bash", "tests/fixtures/r17-jj-receipts.sh", "--tool-dir", "tools"], 0),
    ("r15-config", ["python3", "tests/fixtures/r15-census-config.py",
                    "--tool", "tools/souji-census.sh"], 0),
    ("r17-hygiene", ["python3", "tests/fixtures/r17-census-hygiene.py",
                     "--census", "tools/souji-census.sh"], 0),
    ("r14-cache-demo", ["python3", "-B", "census/round-14/cache-demonstration.py"], 0),
    ("r16-landing-gate", ["python3", "tests/fixtures/r16-landing-gate.py"], 0),
    ("r18-landing-pointers", ["python3", "tests/fixtures/r18-landing-pointers.py",
                              "--tool", "tools/souji-landing-gate.py"], 0),
    ("proc-selftest", ["bash", "tools/souji-proc-census.sh", "--selftest"], 0),
    ("proc-fixture", ["bash", "tests/fixtures/r18-proc-census.sh",
                      "--tool", "tools/souji-proc-census.sh"], 0),
    ("counts-r13", ["python3", "census/round-13/count-claims.py", "REV"], 0),
    ("counts-r14", ["python3", "census/round-14/count-claims.py", "REV"], 0),
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def durable_rev(rev):
    spec = importlib.util.spec_from_file_location(
        "souji_rev_pin", ROOT / "tools" / "souji-rev-pin.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.resolve_durable(str(ROOT), rev, CHANGED)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--rev", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    rev = args.rev.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", rev):
        print("run-acceptance: refusing non-explicit revision %r (C2)" % rev,
              file=sys.stderr)
        return 2
    if os.path.exists(args.output):
        print("run-acceptance: refusing overwrite %s" % args.output, file=sys.stderr)
        return 2
    try:
        durable_rev(rev)
    except Exception as exc:  # noqa: BLE001 - refusal is the point
        print("run-acceptance: revision refused: %s" % exc, file=sys.stderr)
        return 2

    record = {
        "schema": "souji-r19-acceptance-v1",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "measured_commit": rev,
        "changed_sha256": {path: sha256(path) for path in CHANGED},
        "git_version": subprocess.run(["git", "--version"], capture_output=True,
                                      text=True).stdout.strip(),
        "python_version": sys.version.split()[0],
        "results": [],
    }
    matched_all = True
    for name, argv0, expected in COMMANDS:
        argv = [item.replace("REV", rev) for item in argv0]
        started = time.monotonic()
        proc = subprocess.run(argv, cwd=ROOT, env=ENV, capture_output=True,
                              text=True, timeout=1800)
        matched = proc.returncode == expected
        matched_all = matched_all and matched
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-6:]
        entry = {
            "name": name,
            "command": argv,
            "exit": proc.returncode,
            "expected": expected,
            "matched": matched,
            "seconds": round(time.monotonic() - started, 3),
            "tail": tail,
        }
        if name == "gate-selftest":
            m = re.search(r"SELFTEST\tpass=(\d+)\tfail=(\d+)", proc.stdout)
            if m:
                entry["selftest"] = {"pass": int(m.group(1)), "fail": int(m.group(2))}
        if name in ("carry-fixture", "rev-pin-fixture", "audit-shapes-fixture"):
            m = re.search(r"SUMMARY\s+total=(\d+)\s+failed=(\d+)", proc.stdout)
            if m:
                entry["summary"] = {"total": int(m.group(1)),
                                    "failed": int(m.group(2))}
        if name == "audit-selftest":
            m = re.search(r"SELFTEST\tpass=(\d+)\tfail=(\d+)", proc.stdout)
            if m:
                entry["selftest"] = {"pass": int(m.group(1)), "fail": int(m.group(2))}
        if name.startswith("counts-"):
            entry["stdout"] = proc.stdout.strip()
        record["results"].append(entry)
        print("%s\t%s\texit=%d expected=%d" % (
            "PASS" if matched else "FAIL", name, proc.returncode, expected))
    record["all_matched"] = matched_all
    record["summary"] = {
        "commands": len(record["results"]),
        "failed": sum(1 for item in record["results"] if not item["matched"]),
    }
    with open(args.output, "x", encoding="utf-8") as handle:
        handle.write(json.dumps(record, indent=2) + "\n")
    print("WROTE\t%s" % args.output)
    return 0 if matched_all else 1


if __name__ == "__main__":
    sys.exit(main())
