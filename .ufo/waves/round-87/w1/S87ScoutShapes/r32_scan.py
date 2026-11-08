#!/usr/bin/env python3
"""S87ScoutShapes — NE1 shape, extended to the r32..r48 c1-items.tsv populations.

Those populations have columns (id, line, integer, units, rounds, context) where `context` is 40 bytes
around the integer ON THE DECLARED LINE of SCORECARD.md at the round's base. The NE1 shape
("a row's declared line does not carry its token") applies: the context excerpt must sit on the
declared line.

The r32 base is 85b61a151923986e7e6b48f7084b9122561b5f3d (from the r32 c2-items header); the r33+
base is in each round's own enumerate/counter. Where the base cannot be established from the round's
own files, the check is run at EVERY revision that touched the population and the pass/fail set is
reported per revision, so the verdict is revision-independent.

Read-only.
"""
import subprocess, os, json

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], capture_output=True)


def show(rev, path):
    p = git("show", f"{rev}:{path}")
    return None if p.returncode != 0 else p.stdout.decode("utf-8", "replace")


POPS = ["census/round-32/c1-items.tsv", "census/round-33/c1-items.tsv", "census/round-34/c1-items.tsv",
        "census/round-35/c1-items.tsv", "census/round-39/c1-items.tsv", "census/round-40/c1-items.tsv",
        "census/round-41/c1-items.tsv", "census/round-42/c1-items.tsv", "census/round-47/c1-items.tsv",
        "census/round-48/c1-items.tsv"]

summary = {}
for path in POPS:
    # every revision that touched this population
    revs = git("rev-list", "--all", "--", path).stdout.decode().split()
    tot_off, tot_rows, checked = 0, 0, 0
    examples = []
    for r in revs:
        pop = show(r, path)
        if pop is None:
            continue
        sc = show(r, "SCORECARD.md")
        if sc is None:
            continue
        lines = sc.split("\n")
        rows = off = 0
        for l in pop.split("\n"):
            if not l.strip() or l.startswith("#"):
                continue
            c = l.rstrip("\n").split("\t")
            if len(c) < 6 or not c[1].isdigit():
                continue
            rows += 1
            n = int(c[1])
            ctx = c[5]
            if not (0 < n <= len(lines)):
                off += 1
                if len(examples) < 3:
                    examples.append((r[:12], c[0], n, ctx, "line-out-of-range"))
            elif ctx and ctx not in lines[n - 1]:
                off += 1
                if len(examples) < 3:
                    examples.append((r[:12], c[0], n, ctx, "context-not-on-declared-line"))
        tot_rows += rows
        tot_off += off
        checked += 1
    summary[path] = {"revisions": checked, "rows": tot_rows, "off_line": tot_off, "examples": examples}
    print(f"{path}: revisions_checked={checked} rows={tot_rows} off_line={tot_off}")
    for e in examples:
        print("    ", e)

json.dump(summary, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "r32_scan.json"), "w"), indent=1)
