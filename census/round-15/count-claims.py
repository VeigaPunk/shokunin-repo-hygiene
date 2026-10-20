#!/usr/bin/env python3
"""Committed r15 inventory; reads committed bytes via git show only.

Accepts one optional revision (default HEAD), resolves it, and counts
claim surfaces from that commit's tree. Never traverses workspaces,
operator sweeps, or untracked material; census/operator-sweep-* is never
listed or opened because counting is ls-tree/git-show over the named
revision only.
"""
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
source = git("show", rev + ":corpus/SOURCES.md")
rows = [[c.strip() for c in line.split("|")[1:-1]] for line in source.splitlines()
        if re.match(r"^\|\s*S\d{3,}\s*\|", line)]
knowledge = [p for p in paths if p.startswith("corpus/knowledge/") and p.endswith(".md")]
held = [p for p in knowledge if re.search(r"^## Admission status.*\bHELD\b", git("show", rev + ":" + p), re.M)]
print(json.dumps({"measured_commit": rev,
                  "config_fixture": int("tests/fixtures/r15-census-config.py" in paths),
                  "preservation_checker": int("tools/souji-preservation-evidence.py" in paths),
                  "preservation_fixture": int("tests/fixtures/r15-preservation-evidence.py" in paths),
                  "namespace_fixture": int("tests/fixtures/r14-census-boundary.py" in paths),
                  "run_verification": int("census/round-15/run-verification.py" in paths),
                  "count_claims": int("census/round-15/count-claims.py" in paths),
                  "source_rows": len(rows), "tiers": dict(collections.Counter(r[3] for r in rows)),
                  "statuses": dict(collections.Counter(r[7] for r in rows)),
                  "admitted_knowledge": len(knowledge) - len(held), "held_knowledge": len(held)},
                 indent=2, sort_keys=True))
