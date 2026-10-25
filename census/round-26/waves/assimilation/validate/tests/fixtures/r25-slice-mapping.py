#!/usr/bin/env python3
"""r25 D6 cross-check for the r24 quarantine-slice gate and detail TSVs."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXPECTED = {
    "S114": "accepted",
    "S118": "accepted",
    "S123": "accepted",
    "S124": "accepted",
    "S126": "accepted",
    "S131": "accepted",
    "S133": "accepted",
    "S138": "accepted",
}
DETAIL_TO_GATE = {
    "present": "accepted",
    "present-via-mirror": "accepted",
    "present-quote-needs-fix": "accepted",
}
MAPPING = "corpus/lessons/round-25.md"
def data_rows(path: Path) -> list[list[str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        row = line.split("\t")
        if row[0] == "staged_id":
            continue
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--table", default="census/round-24/records/slice-verdicts.tsv")
    parser.add_argument("--detail", default=".ufo/waves/round-24/assimilation/slice-verdicts.tsv")
    args = parser.parse_args()
    root = Path(args.root)
    table_path, detail_path = root / args.table, root / args.detail
    failures = 0

    table_rows = data_rows(table_path)
    detail_rows = data_rows(detail_path)
    table = {row[0]: row[1] for row in table_rows if len(row) >= 3}
    detail = {row[0]: DETAIL_TO_GATE.get(row[2], "UNKNOWN")
              for row in detail_rows if len(row) >= 6}
    if set(table) != set(EXPECTED):
        print(f"table_ids={len(table)} expected={len(EXPECTED)} ids_match=FAIL")
        failures += 1
    if set(detail) != set(EXPECTED):
        print(f"detail_ids={len(detail)} expected={len(EXPECTED)} ids_match=FAIL")
        failures += 1

    matches = 0
    for source_id, expected in EXPECTED.items():
        gate_value = table.get(source_id, "MISSING")
        detail_value = detail.get(source_id, "MISSING")
        if gate_value == expected and detail_value == expected:
            matches += 1
        else:
            print(f"MISMATCH {source_id} gate={gate_value} detail_mapped={detail_value} expected={expected}")
            failures += 1

    pointers = sum(MAPPING in path.read_text(encoding="utf-8")
                   for path in (table_path, detail_path))
    if pointers != 2:
        print(f"mapping_pointers={pointers}/2 FAIL")
        failures += 1
    else:
        print(f"mapping_pointers=2/2 path={MAPPING}")

    gate_s118 = table.get("S118", "MISSING")
    detail_s118 = detail.get("S118", "MISSING")
    if gate_s118 != "accepted" or detail_s118 != "accepted":
        print(f"S118 gate={gate_s118} detail_mapped={detail_s118} expected=accepted FAIL")
        failures += 1
    else:
        print("S118 gate=accepted detail_mapped=accepted PASS")

    status = "PASS" if failures == 0 else "FAIL"
    print(f"rows={matches}/{len(EXPECTED)} status={status}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
