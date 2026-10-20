#!/usr/bin/env python3
"""Check an opened vendor citation's declared line anchors; no store traversal."""
import gzip
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[2]
row_id = sys.argv[1]
rows = (root / "corpus/SOURCES.md").read_text().splitlines()
row = next(line for line in rows if re.match(r"^\|\s*" + re.escape(row_id) + r"\s*\|", line))
anchor = row.split("|")[6]
indices = []
for match in re.finditer(r"\b(15\d{3})(?:-(15\d{3}))?\b", anchor):
    first = int(match[1]); last = int(match[2] or first)
    indices.extend(range(first, last + 1))
with gzip.open("/usr/share/info/coreutils.info.gz", "rt") as source:
    lines = source.read().splitlines()
text = " ".join(lines[n-1].strip() for n in indices)
quote = "Ensure the monitored COMMAND is killed by also sending a ‘KILL’ signal."
exit_text = "124 if COMMAND times out, and ‘--preserve-status’ is not specified"
ok = quote in text and exit_text in text
print(f"{row_id} anchor={'match' if ok else 'mismatch'} lines={','.join(map(str,indices))}")
print(text)
raise SystemExit(0 if ok else 1)
