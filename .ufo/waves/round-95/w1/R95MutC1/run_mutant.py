#!/usr/bin/env python3
"""Run one R95MutC1 mutant through the C1 predicate and save the receipt."""
import shutil
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/souji-shokunin")
SCRATCH = Path("/fast/scratch/hyaku/souji-r95/R95MutC1")
SEAT = LANE / ".ufo/waves/round-95/w1/R95MutC1"
FLEET = Path("/home/vgpnk/Projects/shokunin")

name = sys.argv[1]
mutant = SEAT / "mutants" / f"{name}.py"
work = SCRATCH / name
shutil.rmtree(work, ignore_errors=True)
work.mkdir(parents=True, exist_ok=True)
cmd = [
    sys.executable, "-B", str(mutant),
    "--counter", "census/round-87/c1-pointer-counter.py",
    "--harness", "census/round-93/c1-false-row-harness.py",
    "--population", "census/round-93/c1-false-rows.tsv",
    "--lane", ".",
    "--fleet-root", str(FLEET),
    "--work", str(work),
    "--jobs", "5",
    "--ids", "census/round-95/c1-targets.json",
]
print("CMD:", " ".join(cmd), flush=True)
try:
    p = subprocess.run(cmd, cwd=LANE, capture_output=True, text=True, timeout=3600)
    out = p.stdout + p.stderr
    (SEAT / "receipts" / f"{name}.txt").write_text(out + f"\nEXIT={p.returncode}\n")
    print(out)
    print(f"EXIT={p.returncode}")
finally:
    shutil.rmtree(work, ignore_errors=True)
