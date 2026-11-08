#!/usr/bin/env python3
"""S87ScoutShapes — is the m16 clause load-bearing for any REAL population row AT THE POINT IT IS USED?

`_declared(root, rev, token, target)` runs, at the row's OWN revision:

    git grep -h -F -I -e <target> <rev> -- SKILL.md LOG.md SCORECARD.md corpus/
    -> any(line for line in out if _whole(target, line) and _whole(token, line))

so the m16 punctuation disjunct is load-bearing for a QUARANTINED row iff, in some authority line at
that revision, the TOKEN or the TARGET is matched ONLY through the punctuation disjunct.

This measures that for every QUARANTINED row of every pinned population, at the population's own base,
and at the fixture revisions the harness uses.

Read-only.
"""
import subprocess, os, json

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")
AUTHORITY = ["SKILL.md", "LOG.md", "SCORECARD.md", "corpus"]


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], capture_output=True)


def show(rev, path):
    p = git("show", f"{rev}:{path}")
    return None if p.returncode != 0 else p.stdout.decode("utf-8", "replace")


def whole_with_disjunct(needle: bytes, line: bytes):
    """(accepted_with_disjunct, accepted_without_disjunct)"""
    def one(use_disjunct):
        i = line.find(needle)
        while i >= 0:
            j = i + len(needle)
            before_ok = i == 0 or line[i - 1] not in PATHCH
            after = line[j:j + 2]
            ok = (not after or after[0] not in PATHCH
                  or (use_disjunct and after[:1] in (b".", b",", b";", b":")
                      and (len(after) < 2 or after[1] not in PATHCH)))
            if before_ok and ok:
                return True
            i = line.find(needle, i + 1)
        return False
    return one(True), one(False)


# Every committed QUARANTINED row, across the pinned populations, with the revisions the harness uses.
CASES = [
    ("r77", "census/round-77/c2-population.tsv", "census/round-77/c2-pointer-ledger.tsv",
     "d4f515637884695b3aa016da169d859d3ece6ac4"),
    ("r78", "census/round-78/c2-population.tsv", "census/round-78/c2-pointer-ledger.tsv",
     "a8558d410e9855a9d990d6542a24a9a3a365ab6c"),
    ("r85", "census/round-85/c1-items.tsv", "census/round-85/c1-ledger.tsv",
     "705fa1385c4ccec23811cfa57104046ec6587258"),
    ("r86", "census/round-86/c1-items.tsv", "census/round-86/c1-ledger.tsv",
     "705fa1385c4ccec23811cfa57104046ec6587258"),
    ("r87", "census/round-87/c1-items.tsv", "census/round-87/c1-ledger.tsv",
     "705fa1385c4ccec23811cfa57104046ec6587258"),
]

# The fixture revisions the harness builds (r79..r10) are not in the lane; the lane's own base is the
# only real revision where a QUARANTINED row is judged against the lane's authority files.
# The r78/r77 populations' QUARANTINED rows are judged at the lane base e65538e7 (the harness BASE).
HARNESS_BASE = "e65538e73c7f1a8f7570bc24a2215da8a90043f3"

total_q = 0
lb = []
for label, pop_path, led_path, base in CASES:
    pop = show("HEAD", pop_path)
    led = show("HEAD", led_path)
    if pop is None or led is None:
        continue
    ledger = {}
    for l in led.split("\n"):
        if not l.strip() or l.startswith("#"):
            continue
        r = l.rstrip("\n").split("\t")
        if len(r) >= 3:
            ledger[r[0]] = (r[1], r[2])
    for l in pop.split("\n"):
        if not l.strip() or l.startswith("#"):
            continue
        r = l.rstrip("\n").split("\t")
        if len(r) < 4:
            continue
        iid, f, ln, token = r[0], r[1], r[2], r[3]
        ent = ledger.get(iid)
        if not ent or ent[0] != "QUARANTINED":
            continue
        target = ent[1]
        total_q += 1
        for rev in (base, HARNESS_BASE):
            p = git("grep", "-h", "-F", "-I", "-e", target, rev, "--", *AUTHORITY)
            if p.returncode not in (0, 1):
                continue
            for line in p.stdout.split(b"\n"):
                t_with, t_without = whole_with_disjunct(target.encode(), line)
                k_with, k_without = whole_with_disjunct(token.encode(), line)
                if t_with and not t_without:
                    lb.append((label, iid, rev[:12], "TARGET", target, line.decode("utf-8", "replace")[:200]))
                if k_with and not k_without:
                    lb.append((label, iid, rev[:12], "TOKEN", token, line.decode("utf-8", "replace")[:200]))

print(f"# QUARANTINED rows in the pinned populations: {total_q}")
print(f"# (population, revision) pairs where the m16 disjunct is LOAD-BEARING for the token or target: "
      f"{len(lb)}")
for x in lb:
    print("   ", x)
if not lb:
    print("    (none)")

json.dump({"quarantined_rows": total_q, "load_bearing": lb},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "m16_declared.json"), "w"), indent=1)
