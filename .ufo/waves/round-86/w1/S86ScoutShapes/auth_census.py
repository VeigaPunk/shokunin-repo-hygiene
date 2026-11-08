#!/usr/bin/env python3
"""S86ScoutShapes: which real census/round-N/ and .ufo/waves/round-N/ paths appear on a COMMITTED authority line."""
import os, re, subprocess, sys
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
AUTHORITY = ("SKILL.md", "LOG.md", "SCORECARD.md", "corpus")
TOK = re.compile(r'(?:census/round-[0-9]+/\S+|\.ufo/waves/round-[0-9]+/\S+)')
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")

def real_paths(committed):
    s = set()
    if committed:
        out = subprocess.run(['git','-C',LANE,'ls-tree','-r','--name-only','HEAD'],capture_output=True,text=True).stdout
        s |= {l.strip() for l in out.splitlines() if l.strip()}
    else:
        for dp,ds,fs in os.walk(LANE):
            ds[:] = [x for x in ds if x not in ('.git','.jj','__pycache__','.ruff_cache','.scratch')]
            for f in fs:
                s.add(os.path.relpath(os.path.join(dp,f), LANE))
    return s

def whole(needle, line):
    i = line.find(needle)
    while i >= 0:
        j = i + len(needle)
        before_ok = i == 0 or line[i-1] not in PATHCH
        after = line[j:j+2]
        after_ok = (not after or after[0] not in PATHCH
                    or (after[:1] in (b".",b",",b";",b":") and (len(after)<2 or after[1] not in PATHCH)))
        if before_ok and after_ok:
            return True
        i = line.find(needle, i+1)
    return False

def main():
    out = open(sys.argv[1], 'w')
    real = real_paths(True)
    print("# committed authority lines naming a REAL lane path (census/round-N/ or .ufo/waves/round-N/)", file=out)
    hits = []
    for f in AUTHORITY:
        p = os.path.join(LANE, f)
        paths = []
        if os.path.isdir(p):
            paths = [os.path.join(dp,fn) for dp,ds,fs in os.walk(p) for fn in fs if fn.endswith('.md')]
        elif os.path.isfile(p):
            paths = [p]
        for fp in sorted(paths):
            rel = os.path.relpath(fp, LANE)
            try:
                lines = open(fp, encoding='utf-8', errors='replace').read().split('\n')
            except OSError:
                continue
            for ln, line in enumerate(lines, 1):
                b = line.encode('utf-8', 'replace')
                for m in TOK.finditer(line):
                    cand = m.group(0).rstrip('.,;:)`\'"')
                    if cand in real and whole(cand.encode(), b):
                        hits.append((rel, ln, cand))
    # dedupe by (file,line,path)
    seen=set(); rows=[]
    for h in hits:
        if h in seen: continue
        seen.add(h); rows.append(h)
    print(f"# total (file,line,path) hits: {len(rows)}", file=out)
    print(f"# distinct paths: {len({r[2] for r in rows})}", file=out)
    print(f"# distinct (file,line) lines: {len({(r[0],r[1]) for r in rows})}", file=out)
    print(file=out)
    # group by shape class
    def cls(p):
        parts = p.split('/')
        if parts[0] == 'census':
            n = parts[1]
            below = parts[2:]
            if len(below) == 1:
                return "census-one-component-below-round"
            if below[0] in ('waves','wave') or (below[0]=='records' and len(below)>1 and below[1].startswith('wave-')):
                return "census-wave-capture-landing"
            if len(below) >= 2:
                return "census-two-or-more-below-round"
            return "census-other"
        return "ufo-waves"
    from collections import Counter
    c = Counter(cls(r[2]) for r in rows)
    print("# hit counts by shape class", file=out)
    for k,v in sorted(c.items()): print(f"  {k}\t{v}", file=out)
    print(file=out)
    print("# FULL LIST file:line path", file=out)
    for rel, ln, cand in sorted(rows):
        print(f"{rel}:{ln}\t{cand}", file=out)
    out.close()

main()
