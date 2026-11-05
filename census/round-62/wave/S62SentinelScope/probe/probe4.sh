#!/bin/bash
# S62SentinelScope mitigation check (scratch only): candidate + two suggested hardening lines, tested, NOT delivered as a patch to the lane.
export S=/fast/scratch/hyaku/souji-r62/S62SentinelScope
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
BASEW=$LANE/tools/souji-receipt-write.py
CANDW=$S/cand.py
CAND2=$S/cand2.py
source <(sed -n '/^mk() {/,/^echo "== T0/p' "$S/probe.sh" | sed '$d')

python3 -B - <<'PY'
import os
S = os.environ["S"]
src = open(os.path.join(S, "cand.py"), encoding="utf-8").read()
a = 'fl = git(root, "ls-files", "-v", "-z")'
b = 'st = git(root, "status", "--porcelain")'
assert src.count(a) == 1 and src.count(b) == 1
src = src.replace(a, 'fl = git(root, "-c", "core.fsmonitor=false", "ls-files", "-v", "-z", "--", ":(top)")')
src = src.replace(b, 'st = git(root, "-c", "core.fsmonitor=false", "status", "--porcelain")')
open(os.path.join(S, "cand2.py"), "w", encoding="utf-8").write(src)
print("cand2 built")
PY

echo "== G1 mitigation control: hook env on, bit set, forged; -c core.fsmonitor=false status"
D=$(mk G1)
( export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0="$S/fsm.sh"
  git -C "$D" status --porcelain >/dev/null; git -C "$D" update-index --fsmonitor-valid tools/counter.py
  printf 'forged\n' > "$D/tools/counter.py"
  echo "  status (hook on): [$(git -C "$D" status --porcelain | tr '\n' ' ')]"
  echo "  status -c core.fsmonitor=false (hook on): [$(git -C "$D" -c core.fsmonitor=false status --porcelain | tr '\n' ' ')]"
  echo "  writer cand (hook on):"; wr "$CANDW" "$D"
  echo "  writer cand2 (hook on):"; wr "$CAND2" "$D" )

echo "== G2 cand2 (mitigated) against the frozen matrix and bypass rows"
D=$(mk G2A); echo "A"; wr "$CAND2" "$D"
D=$(mk G2B); printf 'notes v2\n' >> "$D/notes.md"; echo "B"; wr "$CAND2" "$D" --allow-dirty
D=$(mk G2C); printf 'notes v2\n' >> "$D/notes.md"; echo "C"; wr "$CAND2" "$D"
D=$(mk G2D); git -C "$D" update-index --skip-worktree tools/counter.py; printf 'forged\n' > "$D/tools/counter.py"; echo "D"; wr "$CAND2" "$D"
D=$(mk G2E); git -C "$D" update-index --assume-unchanged tools/counter.py; printf 'forged\n' > "$D/tools/counter.py"; echo "E"; wr "$CAND2" "$D"
D=$(mk G2F); git -C "$D" update-index --skip-worktree tools/counter.py; echo "F"; wr "$CAND2" "$D"
D=$(mk G2G); git -C "$D" update-index --skip-worktree tools/instr.sh; printf '#!/bin/sh\necho forged\n' > "$D/tools/instr.sh"; echo "G"; wr "$CAND2" "$D"
echo "  R60 fixture on cand2:"; python3 -B "$LANE/tests/fixtures/r60-receipt-write.py" --tool "$CAND2" --work "$S/r60work/cand2" > "$S/r60-cand2.log" 2>&1; echo "  rc=$?"; tail -1 "$S/r60-cand2.log"
echo "== G3 subdirectory layout on cand2 (top-level instrument copy)"
D=$(mk G3); cp "$D/tools/instr.sh" "$D/instr.sh"; git -C "$D" add -A; git -C "$D" -c user.name=S62Sentinel -c user.email=s62-sentinel@example.invalid commit -qm topinstr
git -C "$D" update-index --skip-worktree notes.md; printf 'forged\n' > "$D/notes.md"
INSTR=instr.sh wr "$CANDW" "$D/tools"; INSTR=instr.sh wr "$CAND2" "$D/tools"
echo "== G4 sparse false positive on cand2 (expected to remain refusal; by design of frozen predicate)"
D=$(mk G4); mkdir -p "$D/other"; printf 'o\n' > "$D/other/o.txt"; git -C "$D" add -A; git -C "$D" -c user.name=S62Sentinel -c user.email=s62-sentinel@example.invalid commit -qm other
git -C "$D" sparse-checkout init --cone; git -C "$D" sparse-checkout set tools; wr "$CAND2" "$D"
echo "PROBES4 DONE"
