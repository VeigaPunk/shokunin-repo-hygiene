#!/usr/bin/env python3
"""Committed r14 inventory, never traverses workspaces or operator sweeps."""
import collections
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
revision = sys.argv[1] if len(sys.argv) == 2 else "HEAD"
def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)
rev = git("rev-parse", revision).strip()
paths = set(git("ls-tree", "-r", "--name-only", rev).splitlines())
source = git("show", rev+":corpus/SOURCES.md")
rows = [[c.strip() for c in line.split("|")[1:-1]] for line in source.splitlines()
        if re.match(r"^\|\s*S\d{3,}\s*\|", line)]
knowledge = [p for p in paths if p.startswith("corpus/knowledge/") and p.endswith(".md")]
held = [p for p in knowledge if re.search(r"^## Admission status.*\bHELD\b", git("show",rev+":"+p),re.M)]
print(json.dumps({"measured_commit":rev,"cache_gate":int("tools/souji-evidence-cache.py" in paths),
                  "cache_fixture":int("tests/fixtures/r14-evidence-cache.py" in paths),
                  "boundary_fixture":int("tests/fixtures/r14-census-boundary.py" in paths),
                  "source_rows":len(rows),"tiers":dict(collections.Counter(r[3] for r in rows)),
                  "statuses":dict(collections.Counter(r[7] for r in rows)),
                  "admitted_knowledge":len(knowledge)-len(held),"held_knowledge":len(held)},indent=2))
