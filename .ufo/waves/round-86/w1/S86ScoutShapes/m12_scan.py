#!/usr/bin/env python3
"""S86ScoutShapes: m12 expressibility scan.
Question: does ANY pinned item set (r77/r78/r85/r86) contain an item whose TOKEN is NOT on its cited base line?
If yes, m12 (R0's `token in blob[int(line)-1]` half) is bindable by a ROW; if no, it needs an item-set change."""
import subprocess, hashlib, sys
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SETS = {"r77": ("census/round-77/c2-population.tsv", "d4f515637884695b3aa016da169d859d3ece6ac4"),
        "r78": ("census/round-78/c2-population.tsv", "a8558d410e9855a9d990d6542a24a9a3a365ab6c"),
        "r85": ("census/round-85/c1-items.tsv", "705fa1385c4ccec23811cfa57104046ec6587258"),
        "r86": ("census/round-86/c1-items.tsv", "705fa1385c4ccec23811cfa57104046ec6587258")}
out = open(sys.argv[1], "w")
def p(*a): print(*a, file=out)
for lbl,(path,base) in SETS.items():
    rows=[l.rstrip("\n").split("\t") for l in open(f"{LANE}/{path}") if l.strip() and not l.startswith("#")]
    off=[]; on=[]
    for r in rows:
        iid, f, line, tok = r[0], r[1], r[2], r[3]
        blob = subprocess.run(["git","-C",LANE,"show",f"{base}:{f}"],capture_output=True).stdout.decode("utf-8","replace").split("\n")
        if not (line.isdigit() and 0 < int(line) <= len(blob)):
            off.append((iid,f,line,tok,"line-out-of-range")); continue
        if tok in blob[int(line)-1]:
            on.append(iid)
        else:
            off.append((iid,f,line,tok,"token-not-on-line"))
    p(f"=== item set {lbl}: {path} (base {base[:7]}) : {len(rows)} items ===")
    p(f"  items whose token IS on its cited base line : {len(on)}  ({','.join(on)})")
    p(f"  items whose token is NOT on its cited line  : {len(off)}")
    for iid,f,line,tok,why in off:
        p(f"    OFF-LINE {iid}\t{f}:{line}\t{tok}\t{why}")
    p()
out.close()
