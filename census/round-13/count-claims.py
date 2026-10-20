#!/usr/bin/env python3
"""Count exact revision-held claim surfaces, never untracked operator material."""
import collections
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
revision = sys.argv[1] if len(sys.argv) == 2 else "HEAD"
def git(*args):
    return subprocess.check_output(["git", "-C", str(root), *args]).decode()
commit = git("rev-parse", revision).strip()
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
