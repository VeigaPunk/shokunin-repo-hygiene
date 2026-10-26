#!/usr/bin/env python3
"""souji-record-contract.py — check a measured run record against its preregistered field contract (round 32, M1).

Round 31 froze a fixture contract with an enumerated field (`arm=<solo|descendant>`), and its committed record
printed a third value (`arm=reflog-only`) that the lane disclosed only after landing (r31 closure routed defect 3,
the D1 class). This tool turns that contract into a check that can fail.

Contract file: `#` comments and blank lines ignored; one `prefix: <word>` line; then one `<key>: v1|v2|...` line
per field, in field order (a set member `*` admits any non-empty value, `#` any non-negative integer). Every record line starting with `<prefix> ` must consist of exactly those keys in that
order as space-separated `key=value` fields, each value in its key's set.

    python3 -B tools/souji-record-contract.py --record PATH --contract PATH

Prints one `BAD <line-no> <reason>` per offending line, then `lines=<n> bad=<m>`. Exit 0 iff n >= 1 and m == 0;
1 otherwise; 2 when the record or contract cannot be read or the contract is malformed. Read-only; writes nothing.
"""
import argparse
import re
import sys


def load_contract(path):
    prefix, keys = None, []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(\S+)", line)
            if not m:
                raise ValueError(f"malformed contract line: {line!r}")
            if m.group(1) == "prefix":
                prefix = m.group(2)
            else:
                keys.append((m.group(1), set(m.group(2).split("|"))))
    if not prefix or not keys:
        raise ValueError("contract needs a prefix line and at least one key line")
    return prefix, keys


def check(record_lines, prefix, keys):
    n, bad = 0, []
    for i, line in enumerate(record_lines, 1):
        if not line.startswith(prefix + " "):
            continue
        n += 1
        fields = line[len(prefix) + 1:].split()
        got = [f.split("=", 1) for f in fields]
        if any(len(g) != 2 for g in got):
            bad.append((i, "field without '='"))
            continue
        if [g[0] for g in got] != [k for k, _ in keys]:
            bad.append((i, f"keys {[g[0] for g in got]} != {[k for k, _ in keys]}"))
            continue
        for (k, allowed), (_, v) in zip(keys, got):
            if not (v in allowed or ("*" in allowed and v) or ("#" in allowed and v.isdigit())):
                bad.append((i, f"{k}={v} outside {'|'.join(sorted(allowed))}"))
                break
    return n, bad


def main():
    ap = argparse.ArgumentParser(prog="souji-record-contract.py")
    ap.add_argument("--record", required=True)
    ap.add_argument("--contract", required=True)
    a = ap.parse_args()
    try:
        prefix, keys = load_contract(a.contract)
        with open(a.record, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except (OSError, ValueError) as e:
        print(f"COULD-NOT-EVALUATE {e}")
        return 2
    n, bad = check(lines, prefix, keys)
    for i, why in bad:
        print(f"BAD {i} {why}")
    print(f"lines={n} bad={len(bad)}")
    return 0 if n >= 1 and not bad else 1


if __name__ == "__main__":
    sys.exit(main())
