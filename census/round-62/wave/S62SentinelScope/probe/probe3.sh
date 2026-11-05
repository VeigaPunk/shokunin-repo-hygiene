#!/bin/bash
# S62SentinelScope follow-up 3 (scratch only): fsmonitor-valid bit with hook established; honest cone sparse; subdir root reachability.
export S=/fast/scratch/hyaku/souji-r62/S62SentinelScope
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
BASEW=$LANE/tools/souji-receipt-write.py
CANDW=$S/cand.py
source <(sed -n '/^mk() {/,/^echo "== T0/p' "$S/probe.sh" | sed '$d')

echo "== F1b fsmonitor-valid bit set WITH hook active (token established first)"
D=$(mk F1b)
( export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0="$S/fsm.sh"
  git -C "$D" status --porcelain; echo "  establish rc=$?"
  git -C "$D" update-index --fsmonitor-valid tools/counter.py; echo "  update-index --fsmonitor-valid rc=$?"
  echo "  ls-files -f -v (hook on):"; git -C "$D" ls-files -f -v | cut -c1-40
  printf 'forged\n' > "$D/tools/counter.py"
  echo "  status after forge (hook on):"; git -C "$D" status --porcelain; echo "  rc=$?"
  echo "  writer base (hook on):"; wr "$BASEW" "$D"
  echo "  writer cand (hook on):"; wr "$CANDW" "$D" )
echo "  ls-files -v / -f with hook off (candidate's view):"
git -C "$D" ls-files -v | cut -c1-40; git -C "$D" ls-files -f | cut -c1-40
echo "  status hook off:"; git -C "$D" status --porcelain; echo "  rc=$?"
echo "  control: hook on, bit cleared -> status:"
( export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0="$S/fsm.sh"; git -C "$D" update-index --no-fsmonitor-valid tools/counter.py; git -C "$D" status --porcelain; echo "  rc=$?" )

echo "== F5b honest cone sparse with a non-root excluded dir"
D=$(mk F5b); mkdir -p "$D/other"; printf 'o\n' > "$D/other/o.txt"; git -C "$D" add -A; git -C "$D" -c user.name=S62Sentinel -c user.email=s62-sentinel@example.invalid commit -qm other
git -C "$D" sparse-checkout init --cone; git -C "$D" sparse-checkout set tools; echo "  set rc=$?"
echo "  ls-files -v:"; git -C "$D" ls-files -v | cut -c1-40; echo "  worktree:"; ls -A "$D"
echo "  status:"; git -C "$D" status --porcelain; echo "  rc=$?"
wr "$BASEW" "$D"; wr "$CANDW" "$D"

echo "== F6b subdirectory root reachability (top-level copy of instrument so rev:rel resolves)"
D=$(mk F6b); cp "$D/tools/instr.sh" "$D/instr.sh"; git -C "$D" add -A; git -C "$D" -c user.name=S62Sentinel -c user.email=s62-sentinel@example.invalid commit -qm topinstr
git -C "$D" update-index --skip-worktree notes.md; printf 'forged\n' > "$D/notes.md"
echo "  cwd=tools ls-files -v -z:"; git -C "$D/tools" ls-files -v -z | tr '\0' '|'; echo
INSTR=instr.sh wr "$BASEW" "$D/tools"; INSTR=instr.sh wr "$CANDW" "$D/tools"
echo "  repo-top ls-files (candidate scope if rooted at top):"; git -C "$D" ls-files -v -z | tr '\0' '|'; echo
echo "PROBES3 DONE"
