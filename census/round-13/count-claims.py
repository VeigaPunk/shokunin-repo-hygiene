#!/usr/bin/env python3
"""Count exact revision-held claim surfaces, never untracked operator material."""
import collections
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
revision = sys.argv[1] if len(sys.argv) == 2 else "HEAD"
GIT_ENV = None
def git(*args):
    return subprocess.check_output(["git", "-C", str(root), *args], env=GIT_ENV).decode()

def resolve_claims_revision(value):
    global GIT_ENV
    """r19 C2: the stamped revision is a durable, explicit commit id.

    Every byte this counter reads comes from the revision itself, so the
    working-tree comparison does not apply; HEAD and branch names do.
    """
    spec = importlib.util.spec_from_file_location(
        "souji_rev_pin", root / "tools" / "souji-rev-pin.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    GIT_ENV = module._env()
    try:
        return module.resolve_durable(str(root), value, [], tree_check=False)
    except module.Refusal as exc:
        print("count-claims: refused: %s" % exc, file=sys.stderr)
        raise SystemExit(2)

commit = resolve_claims_revision(revision)
paths = set(git("ls-tree", "-r", "--name-only", commit, "--", "tools", "corpus/knowledge", "corpus/SOURCES.md").splitlines())
admitted = []
for path in sorted(paths):
    if path.startswith("corpus/knowledge/") and path.endswith(".md"):
        text = git("show", commit + ":" + path)
        lines = text.splitlines()
        if len(lines) >= 3 and "## Admission status — HELD" not in text and all(lines[i].startswith(key) for i, key in enumerate(("source:", "verified-at:", "recheck:"))):
            admitted.append(path)
rows = []
for line in git("show", commit + ":corpus/SOURCES.md").splitlines():
    cells = [cell.strip() for cell in line.split("|")]
    if len(cells) == 13 and cells[1].startswith("S") and cells[1][1:].isdigit():
        rows.append(cells)
print(json.dumps(dict(measured_commit=commit, evidence_gate=int("tools/souji-cert-evidence.py" in paths), F2_entry=int("corpus/knowledge/git-repo-structure-readonly.md" in paths), admitted_entries=len(admitted), sources=len(rows), tiers=dict(collections.Counter(row[4] for row in rows)), statuses=dict(collections.Counter(row[8] for row in rows))), sort_keys=True))
