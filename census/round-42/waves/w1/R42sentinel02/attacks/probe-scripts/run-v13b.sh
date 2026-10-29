#!/usr/bin/env bash
SCR=/fast/scratch/hyaku/souji-r42/R42sentinel02
SEAT=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42sentinel02
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
set -u
python3 -B - <<'PY'
SCR = "/fast/scratch/hyaku/souji-r42/R42sentinel02"
shadow = open(SCR + "/cands/shadow-argparse.py.txt", encoding="utf-8").read()
src = open(SCR + "/cands/v0-honest.py", encoding="utf-8").read()
pre = (
    "import os as _o13, sys as _s13\n"
    "if '--root' in _s13.argv and _o13.path.basename(_s13.argv[_s13.argv.index('--root') + 1]) == 'cand-clean':\n"
    "    _scr13 = _o13.path.dirname(_s13.argv[_s13.argv.index('--root') + 1])\n"
    "    _SHADOW13 = %r\n"
    "    with open(_o13.path.join(_scr13, 'argparse.py'), 'w') as _h13:\n"
    "        _h13.write(_SHADOW13)\n"
) % shadow
open(SCR + "/cands/v13b-shadow-argparse.py", "w", encoding="utf-8").write(pre + src)
print("v13b written")
PY
rm -f "$SCR/probe/shadow-argparse.log"
cd "$SCR/cwdprobe" || exit 2
bash "$LANE/census/round-42/score-candidate.sh" c2 "$SCR" "tools/souji-freeze-check.py=$SCR/cands/v13b-shadow-argparse.py" > "$SEAT/receipts/score-c2-v13b-shadow-argparse.txt" 2>&1
echo "exit=$?" >> "$SEAT/receipts/score-c2-v13b-shadow-argparse.txt"
echo "shadow-argparse-imports=$(wc -l < "$SCR/probe/shadow-argparse.log" 2>/dev/null || echo 0)" > "$SEAT/receipts/v13b-shadow-count.txt"
cp "$SCR/cands/v13b-shadow-argparse.py" "$SEAT/attacks/"
cp "$SCR/cands/shadow-argparse.py.txt" "$SEAT/attacks/shadow-argparse.py.txt"
