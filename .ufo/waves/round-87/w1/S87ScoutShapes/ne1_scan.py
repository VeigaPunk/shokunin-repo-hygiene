#!/usr/bin/env python3
"""S87ScoutShapes — NE1 shape scan.

Question: in the committed pointer/item populations under census/round-*/, how many rows declare a LINE that does
not carry their TOKEN at that population's BASE REVISION? (i.e. the "token sits on a different line than the row
declares" shape that NE1's row I87E exercises.)

Read-only against the lane. No fixture, no clone, no mutation.
"""
import subprocess, sys, os, json

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"

# (population file, base revision) for every committed item/pointer population that has the
# (id, file, line, token, digest) column shape the R0 guard reads.
POPS = [
    ("census/round-77/c2-population.tsv", "d4f515637884695b3aa016da169d859d3ece6ac4", "r77"),
    ("census/round-78/c2-population.tsv", "a8558d410e9855a9d990d6542a24a9a3a365ab6c", "r78"),
    ("census/round-85/c1-items.tsv", "705fa1385c4ccec23811cfa57104046ec6587258", "r85"),
    ("census/round-86/c1-items.tsv", "705fa1385c4ccec23811cfa57104046ec6587258", "r86"),
    ("census/round-87/c1-items.tsv", "705fa1385c4ccec23811cfa57104046ec6587258", "r87"),
]


def git(*args, check=True):
    p = subprocess.run(["git", "-C", LANE, *args], capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {args} rc={p.returncode}: {p.stderr.decode()[:300]}")
    return p


def blob_lines(rev, path):
    p = git("show", f"{rev}:{path}", check=False)
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", "replace").split("\n")


rows = []
total = 0
bad = []
for path, base, label in POPS:
    fp = git("show", f"HEAD:{path}", check=False)
    if fp.returncode != 0:
        print(f"# {path}: not present at HEAD, skipped")
        continue
    lines = fp.stdout.decode("utf-8", "replace").split("\n")
    cache = {}
    for l in lines:
        if not l.strip() or l.startswith("#"):
            continue
        r = l.rstrip("\n").split("\t")
        if len(r) < 4:
            continue
        iid, f, ln, token = r[0], r[1], r[2], r[3]
        total += 1
        if not ln.isdigit():
            bad.append((path, label, iid, f, ln, token, "line-not-numeric"))
            continue
        if f not in cache:
            cache[f] = blob_lines(base, f)
        blob = cache[f]
        if blob is None:
            bad.append((path, label, iid, f, ln, token, "file-absent-at-base"))
            continue
        n = int(ln)
        if n <= 0 or n > len(blob):
            bad.append((path, label, iid, f, ln, token, "line-out-of-range"))
            continue
        text = blob[n - 1]
        if token not in text:
            # where IS the token?
            hits = [i + 1 for i, t in enumerate(blob) if token in t]
            bad.append((path, label, iid, f, ln, token,
                        f"token-not-on-declared-line (token found on line(s) {hits[:6] or 'NONE'})"))

print(f"# populations scanned: {len(POPS)}")
print(f"# rows scanned: {total}")
print(f"# rows whose declared line does NOT carry their token at base: {len(bad)}")
print()
for path, label, iid, f, ln, token, why in bad:
    print(f"OFF-LINE\t{path}\t{label}\t{iid}\t{f}:{ln}\t{token}\t{why}")
json.dump({"total": total, "off_line": len(bad)}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                               "ne1_scan.json"), "w"), indent=1)
