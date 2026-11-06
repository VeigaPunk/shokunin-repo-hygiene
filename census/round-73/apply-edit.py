#!/usr/bin/env python3
"""souji r73: apply ONE member of a frozen edit set (c2-defang.json shape: members[].id/old/new) to a
source file, asserting the `old` string occurs exactly once, and write the result.
Usage: apply-edit.py --set census/round-73/c2-defang.json --id D1 --src <counter.py> --out <file>
Prints `APPLIED id=<id> src_sha256=<..> out_sha256=<..>`; exit 2 when the edit does not apply once."""
import argparse
import hashlib
import json
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ns = ap.parse_args()
    members = {m["id"]: m for m in json.load(open(ns.set, encoding="utf-8"))["members"]}
    if ns.id not in members:
        print(f"unknown id {ns.id!r}", file=sys.stderr)
        return 2
    m = members[ns.id]
    src = open(ns.src, encoding="utf-8").read()
    n = src.count(m["old"])
    if n != 1:
        print(f"edit {ns.id} occurs {n} times in {ns.src}, need exactly 1", file=sys.stderr)
        return 2
    out = src.replace(m["old"], m["new"])
    with open(ns.out, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"APPLIED id={ns.id} src_sha256={hashlib.sha256(src.encode()).hexdigest()} "
          f"out_sha256={hashlib.sha256(out.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
