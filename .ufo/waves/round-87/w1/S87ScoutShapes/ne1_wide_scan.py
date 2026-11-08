#!/usr/bin/env python3
"""S87ScoutShapes — NE1 wide scan over EVERY committed census TSV that has a (file, line, token) shape,
plus the harness BASE variant of the r85/r86/r87 item populations.

Read-only against the lane.
"""
import subprocess, os, json, glob

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
HARNESS_BASE = "e65538e73c7f1a8f7570bc24a2215da8a90043f3"
COUNTER_BASE = "705fa1385c4ccec23811cfa57104046ec6587258"


def git(*args, check=True):
    p = subprocess.run(["git", "-C", LANE, *args], capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {args} rc={p.returncode}: {p.stderr.decode()[:300]}")
    return p


# 1. Every committed census TSV whose header comment or first row declares a token column.
tracked = git("ls-files", "census/").stdout.decode().split("\n")
cands = [f for f in tracked if f.endswith(".tsv") and ("items" in f or "population" in f or "ledger" in f)]
print("# candidate population files:")
for c in cands:
    print("#   ", c)
print()


def read_at(rev, path):
    p = git("show", f"{rev}:{path}", check=False)
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", "replace")


def blob_lines(rev, path):
    t = read_at(rev, path)
    return None if t is None else t.split("\n")


def scan(pop_path, pop_rev, base, label, sep="\t"):
    t = read_at(pop_rev, pop_path)
    if t is None:
        return [], 0
    out, n = [], 0
    for l in t.split("\n"):
        if not l.strip() or l.startswith("#"):
            continue
        r = l.rstrip("\n").split(sep)
        if len(r) < 4:
            continue
        iid, f, ln, token = r[0], r[1], r[2], r[3]
        if not (f and ln.isdigit() and token):
            continue
        n += 1
        blob = blob_lines(base, f)
        if blob is None:
            out.append((pop_path, label, iid, f, ln, token, "file-absent-at-base"))
            continue
        k = int(ln)
        if k <= 0 or k > len(blob):
            out.append((pop_path, label, iid, f, ln, token, "line-out-of-range"))
            continue
        if token not in blob[k - 1]:
            hits = [i + 1 for i, x in enumerate(blob) if token in x]
            out.append((pop_path, label, iid, f, ln, token,
                        f"token-not-on-declared-line (token on line(s) {hits[:6] or 'NONE'})"))
    return out, n


# The (file, line, token) populations with known bases.
POPS = [
    ("census/round-77/c2-population.tsv", "d4f515637884695b3aa016da169d859d3ece6ac4", "r77"),
    ("census/round-78/c2-population.tsv", "a8558d410e9855a9d990d6542a24a9a3a365ab6c", "r78"),
    ("census/round-85/c1-items.tsv", COUNTER_BASE, "r85"),
    ("census/round-86/c1-items.tsv", COUNTER_BASE, "r86"),
    ("census/round-87/c1-items.tsv", COUNTER_BASE, "r87"),
]
grand_bad, grand_n = [], 0
print("=== pass A: (file, line, token) populations at their PINNED base ===")
for path, base, label in POPS:
    bad, n = scan(path, "HEAD", base, label)
    grand_bad += bad
    grand_n += n
    print(f"{path}\tbase={base}\trows={n}\toff-line={len(bad)}")
    for b in bad:
        print("   OFF-LINE", b[2], f"{b[3]}:{b[4]}", b[5], "->", b[6])
print()

print("=== pass B: the r85/r86/r87 item populations at the HARNESS base "
      f"({HARNESS_BASE}) ===")
for path, base, label in POPS[2:]:
    bad, n = scan(path, "HEAD", HARNESS_BASE, label + "@harnessBASE")
    print(f"{path}\tbase={HARNESS_BASE}\trows={n}\toff-line={len(bad)}")
    for b in bad:
        print("   OFF-LINE", b[2], f"{b[3]}:{b[4]}", b[5], "->", b[6])

print()
print(f"=== pass A totals: rows={grand_n} off-line={len(grand_bad)} ===")

# 2. Other census TSVs with (line, token) but no file column: census/round-44/c1-population.tsv.
print()
print("=== pass C: census/round-44/c1-population.tsv (line, token, class, reason) — no file column ===")
t = read_at("HEAD", "census/round-44/c1-population.tsv")
if t:
    print(t[:600])

json.dump({"rows": grand_n, "off_line": len(grand_bad)}, open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ne1_wide_scan.json"), "w"), indent=1)
