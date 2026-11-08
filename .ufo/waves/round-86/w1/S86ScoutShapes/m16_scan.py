#!/usr/bin/env python3
"""S86ScoutShapes: m16 expressibility scan.
`_whole`'s sentence-end disjunct is decisive iff the path is followed IMMEDIATELY by one of . , ; : and the NEXT
byte is not a path byte (or the line ends).  Scan every committed authority line at BASE for such a site, and for
each site report whether the line ALSO names a whole-path token (the second half of `_declared`)."""
import importlib.util, os, re, subprocess, sys
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "705fa1385c4ccec23811cfa57104046ec6587258"
spec = importlib.util.spec_from_file_location("ctr", os.path.join(LANE,"census/round-86/c1-pointer-counter.py"))
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)
PATHCH = ctr.PATHCH
out = open(sys.argv[1], "w")
def p(*a): print(*a, file=out)

def whole_plain(needle, line):
    """_whole WITHOUT the sentence-end disjunct."""
    i = line.find(needle)
    while i >= 0:
        j = i + len(needle)
        before_ok = i == 0 or line[i-1] not in PATHCH
        after = line[j:j+2]
        after_ok = (not after) or (after[0] not in PATHCH)
        if before_ok and after_ok:
            return True
        i = line.find(needle, i+1)
    return False

files = [l for l in subprocess.run(["git","-C",LANE,"ls-tree","-r","--name-only",BASE,"--",
                                    "SKILL.md","LOG.md","SCORECARD.md","corpus"],capture_output=True,text=True).stdout.splitlines() if l.strip()]
sites = []
for f in files:
    blob = subprocess.run(["git","-C",LANE,"show",f"{BASE}:{f}"],capture_output=True).stdout
    for ln, line in enumerate(blob.decode("utf-8","replace").split("\n"), 1):
        b = line.encode("utf-8","replace")
        # every maximal run of path bytes; also each run with trailing '.' stripped (a path followed by '.')
        for m in re.finditer(rb'[A-Za-z0-9_./@+~-]+', b):
            run = m.group(0)
            for needle in {run, run.rstrip(b".")}:
                if not needle or b'/' not in needle: continue
                i = b.find(needle); j = i + len(needle)
                if i > 0 and b[i-1] in PATHCH: continue
                after = b[j:j+2]
                if not after or after[0] not in PATHCH: continue
                if after[:1] not in (b".", b",", b";", b":"): continue
                if len(after) >= 2 and after[1] in PATHCH: continue
                # decisive: pristine whole=True, plain whole=False
                if ctr._whole(needle, b) and not whole_plain(needle, b):
                    sites.append((f, ln, needle.decode("utf-8","replace"), after.decode("utf-8","replace")))
p(f"committed authority lines at BASE {BASE[:7]}: files scanned = {len(files)}")
p(f"SITES where the sentence-end disjunct is DECISIVE (path immediately followed by . , ; : + non-path byte): {len(sites)}")
for f, ln, nd, aft in sites:
    p(f"  {f}:{ln}\tpath={nd}\tfollowed_by={aft!r}")
p()
p("  (a site is only usable for m16 if the SAME line also names the row's token as a whole path, so that")
p("   _declared() is satisfied by the punctuation-carrying occurrence)")
out.close()
