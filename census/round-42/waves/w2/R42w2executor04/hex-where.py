import json,re,importlib.util,collections
R="/home/vgpnk/Projects/shokunin/souji-shokunin"; REV="3105a63b23481fccf7df58e74d14a6681e0ea0c8"
rows=json.load(open("hex.json"))
import subprocess
lines=subprocess.run(["git","-C",R,"show",REV+":SCORECARD.md"],capture_output=True).stdout.decode().splitlines()
spec=importlib.util.spec_from_file_location("de",R+"/tools/souji-declared-evidence.py"); de=importlib.util.module_from_spec(spec); spec.loader.exec_module(de)
cat=collections.Counter(); ex=collections.defaultdict(list)
for r in rows:
    line=lines[r["line"]-1]; t=r["tok"]
    where=None
    for m in de.SPAN_RE.finditer(line):
        if t in m.group(1):
            inner=m.group(1).strip()
            where="hex-bare-span" if re.fullmatch(r"[0-9A-Fa-f]{7,64}",inner) else "inside-nonhex-backtick-span"
            break
    if where is None:
        cells=de.cells_of(line)
        c=[x for x in cells if t in x][0]
        ctx=bool(de.REV_WORDS.search(c) or de.CENSUS_ROUND_RE.search(c))
        where="plain-text-cell-ctx(%s)"%ctx
    if where=="hex-bare-span":
        # in a cell, replaced into scan: classify
        cells=de.cells_of(line); c=[x for x in cells if t in x][0]
        ctx=bool(de.REV_WORDS.search(c) or de.CENSUS_ROUND_RE.search(c)); where+="-cell-ctx(%s)"%ctx
    r["where"]=where
    k=(where,"len64" if r["len"]==64 else ("commit" if r["commit"] else "noncommit"))
    cat[k]+=1
    if len(ex[k])<3: ex[k].append((r["line"],t[:14],r["sec"][:40]))
for k,v in cat.most_common(): print(v,k,ex[k])
print()
for r in rows:
    if r["len"]==64 or (not r["commit"]):
        print(r["line"],r["tok"],"commit=",r["commit"],"obj=",r["obj"],"digest_of=",r["digest"],"where=",r["where"])
        print("   LINE:",lines[r["line"]-1][:400])
json.dump(rows,open("hex.json","w"))
