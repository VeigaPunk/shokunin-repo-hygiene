#!/usr/bin/env bash
SCR=/fast/scratch/hyaku/souji-r42/R42sentinel02
SEAT=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42sentinel02
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
set -u
python3 -B - <<'PY'
SCR="/fast/scratch/hyaku/souji-r42/R42sentinel02"
src=open(SCR+"/cands/v0-honest.py",encoding="utf-8").read()
pre='''import os as _o13, sys as _s13
if "--root" in _s13.argv and _o13.path.basename(_s13.argv[_s13.argv.index("--root") + 1]) == "cand-clean":
    # write into the counter's shared scratch (the parent of --root), which is sys.path[0] for every later tool run
    _scr13 = _o13.path.dirname(_s13.argv[_s13.argv.index("--root") + 1])
    with open(_o13.path.join(_scr13, "sitecustomize.py"), "w") as _h13:
        _h13.write("open('" + SCR_PROBE + "', 'a').write('SHADOW sitecustomize imported pid=%d argv=%s\\\\n' % (__import__('os').getpid(), __import__('sys').argv[1:2]))\\n")
'''.replace("SCR_PROBE", repr(SCR + "/probe/shadow.log"))
open(SCR+"/cands/v13-shadow-sitecustomize.py","w",encoding="utf-8").write(pre+src)
print("v13 written")
PY
rm -f "$SCR/probe/shadow.log"
cd "$SCR/cwdprobe" || exit 2
bash "$LANE/census/round-42/score-candidate.sh" c2 "$SCR" "tools/souji-freeze-check.py=$SCR/cands/v13-shadow-sitecustomize.py" > "$SEAT/receipts/score-c2-v13-shadow-sitecustomize.txt" 2>&1
echo "exit=$?" >> "$SEAT/receipts/score-c2-v13-shadow-sitecustomize.txt"
echo "shadow-imports=$(wc -l < "$SCR/probe/shadow.log" 2>/dev/null || echo 0)" > "$SEAT/receipts/v13-shadow-count.txt"
cp "$SCR/cands/v13-shadow-sitecustomize.py" "$SEAT/attacks/"
