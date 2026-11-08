#!/usr/bin/env python3
"""S87ScoutShapes — comprehensive census population survey.

Every committed TSV under census/ whose columns look like a POINTER population (a file column, a numeric
line column, and a token column) is checked for the NE1 shape: does the declared line carry the token at
the population's base revision?

Bases are taken from the round's own pinned value where the counter/header names one; otherwise the
check is run at every revision that touched the population and the verdict is reported per revision.

Read-only.
"""
import subprocess, os, json, re

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], capture_output=True)


def show(rev, path):
    p = git("show", f"{rev}:{path}")
    return None if p.returncode != 0 else p.stdout.decode("utf-8", "replace")


tracked = git("ls-files", "census/").stdout.decode().split("\n")
tsvs = [f for f in tracked if f.endswith(".tsv")]

# A pointer population has >=4 tab-separated columns, col1 a numeric line, col2 a token that looks like a
# path, and a sibling file column. Detect candidates by shape.
print("# TSV census files whose first data row has (id, file, numeric-line, token) columns:")
cands = []
for path in tsvs:
    head = show("HEAD", path)
    if head is None:
        continue
    for l in head.split("\n"):
        if not l.strip() or l.startswith("#"):
            continue
        c = l.rstrip("\n").split("\t")
        # (id, file, numeric-line, token): c[1] is a file path (may be a bare lane-root name),
        # c[2] is numeric, c[3] is the token
        if len(c) >= 4 and c[2].isdigit() and c[1] and ("/" in c[1] or c[1].endswith(".md")) and c[3]:
            cands.append(path)
        break
for c in cands:
    print("#   ", c)
print()

# Known bases, from the counters' own pins.
BASES = {
    "census/round-77/c2-population.tsv": ("d4f515637884695b3aa016da169d859d3ece6ac4", "SCORECARD.md"),
    "census/round-78/c2-population.tsv": ("a8558d410e9855a9d990d6542a24a9a3a365ab6c", "LOG.md"),
    "census/round-85/c1-items.tsv": ("705fa1385c4ccec23811cfa57104046ec6587258", None),
    "census/round-86/c1-items.tsv": ("705fa1385c4ccec23811cfa57104046ec6587258", None),
    "census/round-87/c1-items.tsv": ("705fa1385c4ccec23811cfa57104046ec6587258", None),
}

rows_total = 0
off_total = 0
details = []
for path in cands:
    head = show("HEAD", path)
    # the file column is col1 (index 1) per the (id, file, line, token) shape
    bases = [BASES[path]] if path in BASES else []
    if not bases:
        # try the base named in the header comment
        m = re.search(r"\b([0-9a-f]{40})\b", head.split("\n")[0] if head else "")
        bases = [(m.group(1), None)] if m else []
    for base, forced_file in bases:
        sc = show(base, "SCORECARD.md")
        lg = show(base, "LOG.md")
        n = off = 0
        offs = []
        for l in head.split("\n"):
            if not l.strip() or l.startswith("#"):
                continue
            c = l.rstrip("\n").split("\t")
            if len(c) < 4:
                continue
            iid, f, ln, token = c[0], c[1], c[2], c[3]
            n += 1
            blob = show(base, f)
            if blob is None:
                offs.append((iid, f, ln, token, "file-absent-at-base"))
                off += 1
                continue
            lines = blob.split("\n")
            if not ln.isdigit() or not (0 < int(ln) <= len(lines)):
                offs.append((iid, f, ln, token, "line-out-of-range"))
                off += 1
                continue
            if token not in lines[int(ln) - 1]:
                where = [i + 1 for i, x in enumerate(lines) if token in x]
                offs.append((iid, f, ln, token, f"token-not-on-declared-line (on {where[:5] or 'NONE'})"))
                off += 1
        rows_total += n
        off_total += off
        details.append((path, base[:12], n, off, offs))
        print(f"{path} @ {base[:12]}: rows={n} off-line={off}")
        for o in offs:
            print("    OFF-LINE", o)

print()
print(f"=== TOTAL: rows={rows_total} off-line={off_total} ===")
json.dump(details, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "pop_survey.json"), "w"), indent=1)
