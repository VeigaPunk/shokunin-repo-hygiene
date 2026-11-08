#!/usr/bin/env python3
"""R91ExecC2Fixture reproducer: which single case and which conjunct fails per r91 variant.

Loads tests/fixtures/r91-k4-flagfail.py as a module, builds a kit per variant and prints the real cell, the
nelchar/nelbyte/nelcut/badbyte/literal cells and every conjunct of the case that the variant fails.

usage: python3 -B diag-variant-conjuncts.py <lane-root> <scratch-dir>   (scratch must be disposable)
"""
import importlib.util
import os
import shutil
import sys

LANE, SCRATCH = sys.argv[1], sys.argv[2]
VARIANTS = {"double-backslash": "census/round-91/variants/double-backslash-tool.py",
            "raw-newline": "census/round-91/variants/raw-newline-tool.py",
            "keep-helper": "census/round-91/variants/keep-helper-tool.py"}
BS = chr(92)


def load_fixture():
    spec = importlib.util.spec_from_file_location("fx", os.path.join(LANE, "tests/fixtures/r91-k4-flagfail.py"))
    fx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fx)
    return fx


def main():
    fx = load_fixture()
    for name, rel in VARIANTS.items():
        root = os.path.join(SCRATCH, "k-" + name)
        shutil.rmtree(root, ignore_errors=True)
        kit = fx.make_kit(root, os.path.join(LANE, rel))
        try:
            for mode in ("nelchar", "nelbyte", "nelcut", "badbyte", "literal"):
                out, rows = fx.run_case(kit, mode)
                cell = rows[0] if rows else None
                print(f"[{name}] mode={mode} nrows={len(rows)} cell={cell!r}")
                if mode == "nelchar" and cell is not None:
                    print("  KFF9  conjuncts: count(\\u0085)==1 ->", cell.count(BS + "u0085") == 1,
                          "| count(\\x85)==0 ->", cell.count(BS + "x85") == 0,
                          "| count(\\\\u0085)==0 ->", cell.count(BS * 2 + "u0085") == 0)
                    print("  KFF12 conjuncts: case_oneline ->", fx.case_oneline(out, rows),
                          "| 'marker' ->", "marker" in cell,
                          "| 'tailtkn' ->", "tailtkn" in cell,
                          "| no raw separator ->", not any(s in cell for s in ("\n", "\r", "\u2028", "\u2029", "\u0085")))
                if mode == "nelbyte" and cell is not None:
                    print("  KFF10 conjuncts: count(\\x85)==1 ->", cell.count(BS + "x85") == 1,
                          "| count(\\u0085)==0 ->", cell.count(BS + "u0085") == 0,
                          "| count(\\\\x85)==0 ->", cell.count(BS * 2 + "x85") == 0)
                if mode == "nelcut" and cell is not None:
                    print("  KFF11 conjuncts: 'fatal: nel' ->", "fatal: nel" in cell,
                          "| count(\\x85)==0 ->", cell.count(BS + "x85") == 0,
                          "| count(\\u0085)==0 ->", cell.count(BS + "u0085") == 0)
            src = open(os.path.join(LANE, rel), encoding="utf-8").read()
            print(f"[{name}] KFF13 scan: def _one_line( = {src.count('def _one_line(')};"
                  f" _one_line( = {src.count('_one_line(')}")
        finally:
            shutil.rmtree(root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
