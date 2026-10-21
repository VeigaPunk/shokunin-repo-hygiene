#!/usr/bin/env python3
"""Committed r14 inventory, never traverses workspaces or operator sweeps."""
import collections
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
revision = sys.argv[1] if len(sys.argv) == 2 else "HEAD"
def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)

def resolve_claims_revision(value):
    """r19 C2: the stamped revision is a durable, explicit commit id.

    Every byte this counter reads comes from the revision itself, so the
    working-tree comparison does not apply; HEAD and branch names do.
    """
    spec = importlib.util.spec_from_file_location(
        "souji_rev_pin", ROOT / "tools" / "souji-rev-pin.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        return module.resolve_durable(str(ROOT), value, [], tree_check=False)
    except module.Refusal as exc:
        print("count-claims: refused: %s" % exc, file=sys.stderr)
        raise SystemExit(2)

rev = resolve_claims_revision(revision)
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
