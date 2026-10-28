#!/usr/bin/env python3
"""Random records against a ROOT whose .git is a FILE (separate-git-dir). pinned vs base.
usage: diff_fileroot.py ROOT N SEED
Reports identical/differing counts and, for differing records, whether the difference is the
TOTAL class (a non-last TOTAL decides). Also counts records where the root is named but reads ABSENT."""
import os
import random
import re
import subprocess
import sys

PINNED = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py"
BASE = "/fast/scratch/hyaku/souji-r41/R41w2critic05/base-tool.py"
ROOT, N, SEED = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
R = random.Random(SEED)
name = os.path.basename(ROOT)
stats = {"runs": 0, "identical": 0, "differ_total_class": 0, "differ_other": 0, "named_root_absent": 0,
         "named_root_absent_pinned": 0, "tracebacks": 0}
other = []
rec = os.path.join(ROOT + "-rec.tsv")
for i in range(N):
    pool = [name, "alpha", "nope"]
    k = R.randint(1, 3)
    chosen = R.sample(pool, k)
    rows = ["REPO\t%s\tregs=%d\tprunable=0" % (nm, 1) for nm in chosen]
    sr = len(rows)
    tots = []
    for _ in range(R.randint(0, 3)):
        t = [len(rows), sr, 0]
        if R.random() < 0.5:
            t[R.randrange(2)] += R.choice([-1, 1])
        tots.append("TOTAL\trepos=%d\tregs=%d\tprunable=%d" % tuple(t))
    lines = rows + tots
    R.shuffle(lines)
    body = "\n".join(lines) + "\n"
    with open(rec, "w") as h:
        h.write(body)
    extra = ["--skip-unrecorded"] if R.random() < 0.5 else []
    outs = []
    for tool in (PINNED, BASE):
        p = subprocess.run(["python3", "-B", tool, "--root", ROOT, "--record", rec, "--timeout", "30", *extra],
                           env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        outs.append((p.returncode, re.sub(r"record=\S+", "record=R", p.stdout + p.stderr)))
        if "Traceback" in p.stderr:
            stats["tracebacks"] += 1
    stats["runs"] += 1
    if outs[0] == outs[1]:
        stats["identical"] += 1
    else:
        # classify: TOTAL-class if the body has a disagreeing TOTAL that is not the last
        if "TOTAL" in outs[0][1] and outs[0][0] == 2:
            stats["differ_total_class"] += 1
        else:
            stats["differ_other"] += 1
            other.append((body, extra, outs))
    if name in chosen and "DRIFT\tABSENT\t%s\t" % name in outs[0][1]:
        stats["named_root_absent_pinned"] += 1
    if name in chosen and "DRIFT\tABSENT\t%s\t" % name in outs[1][1]:
        stats["named_root_absent"] += 1
os.unlink(rec)
print("STATS", stats)
for o in other[:5]:
    print("OTHER-DIFF", o)
