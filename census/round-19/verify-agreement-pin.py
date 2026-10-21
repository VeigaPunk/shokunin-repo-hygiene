#!/usr/bin/env python3
"""verify-agreement-pin — bind the r18 proc-agreement records to their bytes.

Round 19 D2 (r18 closure): `census/round-18/proc-agreement-counterfix.json`
names the tool base `4800fd7` and the repaired counter only through
`counter-exclusion-repair.json`'s `measured_commit`, with no digest. This
checker makes the binding explicit in a NEW record; it never edits the r18
records.

Record shape (written by `--emit`):
  {
    "schema": "souji-agreement-pin-v1",
    "tool":     {"path": ..., "sha256": ..., "measured_commit": ...},
    "counter":  {"path": ..., "sha256": ..., "measured_commit": ...},
    "agreement": {<path>: <sha256>, ...},
    "note": ...
  }

`--check RECORD` recomputes every digest from the lane tree and exits 0 only
when all match; 1 on a mismatch; 2 on malformed/unreadable input.
`--emit RECORD` writes a new record (refuses overwrite) from the named files.
`--selftest` uses synthetic /var/tmp records.

Scratch only under /var/tmp; read-only over lane files; no network, no
signals, no live census.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile

DEFAULT_TOOL = "tools/souji-proc-census.sh"
DEFAULT_COUNTER = "census/round-18/leak-count.py"
DEFAULT_AGREEMENT = (
    "census/round-18/proc-agreement-counterfix.json",
    "census/round-18/proc-agreement-final.json",
    "census/round-18/counter-exclusion-repair.json",
)
SCHEMA = "souji-agreement-pin-v1"


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_record(root, tool, counter, tool_commit, counter_commit, agreement):
    record = {
        "schema": SCHEMA,
        "tool": {"path": tool, "sha256": sha256(os.path.join(root, tool)),
                 "measured_commit": tool_commit},
        "counter": {"path": counter, "sha256": sha256(os.path.join(root, counter)),
                    "measured_commit": counter_commit},
        "agreement": {path: sha256(os.path.join(root, path))
                      for path in agreement},
        "note": "D2: the r18 agreement records stay byte-identical; this new "
                "record pins the two implementations and the records they cite.",
    }
    return record


def check_record(root, record):
    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        return ["malformed: schema is not %s" % SCHEMA]
    problems = []
    for key in ("tool", "counter"):
        entry = record.get(key)
        if not isinstance(entry, dict) or "path" not in entry or "sha256" not in entry:
            problems.append("malformed: %s entry incomplete" % key)
            continue
        path = os.path.join(root, entry["path"])
        if not os.path.isfile(path):
            problems.append("%s missing: %s" % (key, entry["path"]))
            continue
        actual = sha256(path)
        if actual != entry["sha256"]:
            problems.append("%s digest mismatch: %s recorded %s actual %s"
                            % (key, entry["path"], entry["sha256"][:12], actual[:12]))
    agreement = record.get("agreement")
    if not isinstance(agreement, dict) or not agreement:
        problems.append("malformed: agreement map empty")
    else:
        for rel, expected in sorted(agreement.items()):
            path = os.path.join(root, rel)
            if not os.path.isfile(path):
                problems.append("agreement missing: %s" % rel)
                continue
            actual = sha256(path)
            if actual != expected:
                problems.append("agreement digest mismatch: %s recorded %s actual %s"
                                % (rel, str(expected)[:12], actual[:12]))
    return problems


def run_selftest():
    top = tempfile.mkdtemp(prefix="souji-r19-agreement-pin.", dir="/var/tmp")
    passed = failed = 0

    def case(name, fn):
        nonlocal passed, failed
        try:
            fn()
            passed += 1
            print("CASE\tpass\t%s" % name)
        except AssertionError as exc:
            failed += 1
            print("CASE\tFAIL\t%s\t%s" % (name, exc))

    def write(path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    try:
        root = os.path.join(top, "lane")
        write(os.path.join(root, "tools/t.sh"), "tool\n")
        write(os.path.join(root, "c/t.py"), "counter\n")
        write(os.path.join(root, "c/a.json"), "{}\n")
        record = build_record(root, "tools/t.sh", "c/t.py", "a" * 40, "b" * 40,
                              ["c/a.json"])

        case("clean-match", lambda: (
            check_record(root, record) == [] or
            (_ for _ in ()).throw(AssertionError(check_record(root, record)))))

        tampered = json.loads(json.dumps(record))
        tampered["counter"]["sha256"] = "0" * 64
        case("counter-tamper", lambda: (
            any("counter digest mismatch" in p for p in check_record(root, tampered)) or
            (_ for _ in ()).throw(AssertionError("tamper not detected"))))

        tampered2 = json.loads(json.dumps(record))
        tampered2["agreement"]["c/a.json"] = "0" * 64
        case("agreement-tamper", lambda: (
            any("agreement digest mismatch" in p for p in check_record(root, tampered2)) or
            (_ for _ in ()).throw(AssertionError("agreement tamper not detected"))))

        case("malformed-schema", lambda: (
            check_record(root, {"schema": "nope"}) != [] or
            (_ for _ in ()).throw(AssertionError("malformed accepted"))))

        missing = json.loads(json.dumps(record))
        missing["tool"]["path"] = "tools/absent.sh"
        case("missing-file", lambda: (
            any("tool missing" in p for p in check_record(root, missing)) or
            (_ for _ in ()).throw(AssertionError("missing file accepted"))))
    finally:
        shutil.rmtree(top, ignore_errors=True)
    print("SUMMARY total=%d failed=%d" % (passed + failed, failed))
    return 0 if failed == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--check")
    parser.add_argument("--emit")
    parser.add_argument("--tool", default=DEFAULT_TOOL)
    parser.add_argument("--counter", default=DEFAULT_COUNTER)
    parser.add_argument("--tool-commit", default="4800fd7")
    parser.add_argument("--counter-commit", default="2d4c7f8")
    parser.add_argument("--agreement", action="append", default=None)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        return run_selftest()
    root = os.path.abspath(args.root)
    if args.check:
        try:
            with open(args.check, encoding="utf-8") as handle:
                record = json.load(handle)
        except (OSError, ValueError) as exc:
            print("verify-agreement-pin: malformed: %s" % exc, file=sys.stderr)
            return 2
        problems = check_record(root, record)
        for problem in problems:
            print("PIN-FAIL\t%s" % problem)
        return 0 if not problems else (2 if any(p.startswith("malformed") for p in problems) else 1)
    if args.emit:
        if os.path.exists(args.emit):
            print("verify-agreement-pin: refuse overwrite: %s" % args.emit, file=sys.stderr)
            return 2
        agreement = args.agreement or list(DEFAULT_AGREEMENT)
        try:
            record = build_record(root, args.tool, args.counter, args.tool_commit,
                                  args.counter_commit, agreement)
        except OSError as exc:
            print("verify-agreement-pin: could-not-evaluate: %s" % exc, file=sys.stderr)
            return 2
        with open(args.emit, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(record, indent=2) + "\n")
        print("WROTE\t%s" % args.emit)
        return 0
    parser.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
