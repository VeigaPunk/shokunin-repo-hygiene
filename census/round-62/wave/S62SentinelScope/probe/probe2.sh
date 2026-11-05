#!/bin/bash
# S62SentinelScope follow-up probes (scratch only). Reuses mk/wr from probe.sh.
export S=/fast/scratch/hyaku/souji-r62/S62SentinelScope
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
BASEW=$LANE/tools/souji-receipt-write.py
CANDW=$S/cand.py
source <(sed -n '/^mk() {/,/^echo "== T0/p' "$S/probe.sh" | sed '$d')

echo "== F1 fsmonitor-valid index bit (not shown by ls-files -v)"
D=$(mk F1); git -C "$D" update-index --fsmonitor-valid tools/counter.py; printf 'forged\n' > "$D/tools/counter.py"
echo "  ls-files -v:"; git -C "$D" ls-files -v | cut -c1-40
echo "  ls-files -f:"; git -C "$D" ls-files -f | cut -c1-40
echo "  ls-files -f -v -z:"; git -C "$D" ls-files -f -v -z | tr '\0' '|'; echo
echo "  control status no hook (bit set, no core.fsmonitor):"; git -C "$D" status --porcelain; echo "  rc=$?"
echo "  control writer no hook:"; wr "$BASEW" "$D"; wr "$CANDW" "$D"
( export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0="$S/fsm.sh"
  echo "  status WITH fsmonitor hook (bit set):"; git -C "$D" status --porcelain; echo "  rc=$?"
  echo "  ls-files -v under hook:"; git -C "$D" ls-files -v | cut -c1-40
  echo "  writer base under hook:"; wr "$BASEW" "$D"
  echo "  writer cand under hook:"; wr "$CANDW" "$D" )
echo "  control: same fixture, hook, bit cleared -> expect M visible:"
git -C "$D" update-index --no-fsmonitor-valid tools/counter.py
( export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0="$S/fsm.sh"; git -C "$D" status --porcelain; echo "  rc=$?"; wr "$CANDW" "$D" )

echo "== F2 TOCTOU fresh fixtures: flags set during run (cand only, fresh state)"
D=$(mk F2a); CMD="sh $S/flip.sh $D flags"; ( export CMD; wr "$CANDW" "$D" ); echo "  post-run state:"; git -C "$D" ls-files -v | cut -c1-40; git -C "$D" status --porcelain
echo "  dirty during run (cand only, fresh):"; D=$(mk F2b); CMD="sh $S/flip.sh $D dirty"; ( export CMD; wr "$CANDW" "$D" )
echo "  dirty during run (base only, fresh):"; D=$(mk F2c); CMD="sh $S/flip.sh $D dirty"; ( export CMD; wr "$BASEW" "$D" )

echo "== F3 GIT_DIR / GIT_WORK_TREE discriminating (env points at FLAGGED clean repo; fixture is clean)"
CLEAN=$(mk F3clean); git -C "$CLEAN" update-index --skip-worktree tools/counter.py
D=$(mk F3clean2)
( export GIT_DIR="$CLEAN/.git"; wr "$CANDW" "$D"; wr "$BASEW" "$D" )
( export GIT_WORK_TREE="$CLEAN"; wr "$CANDW" "$D" )
echo "  control: unscrubbed git sees CLEAN index:"; ( export GIT_DIR="$CLEAN/.git"; git -C "$D" ls-files -v | cut -c1-40 )

echo "== F4 filename with newline (flagged, forged)"
D=$(mk F4); printf 'nl\n' > "$D/tools/$(printf 'we\nird.py')"; git -C "$D" add -A; git -C "$D" -c user.name=S62Sentinel -c user.email=s62-sentinel@example.invalid commit -qm nl
git -C "$D" update-index --skip-worktree "$(printf 'tools/we\nird.py')"; printf 'forged\n' > "$D/tools/$(printf 'we\nird.py')"
git -C "$D" ls-files -v -z | tr '\0' '|'; echo
wr "$CANDW" "$D"; wr "$BASEW" "$D"

echo "== F5 honest sparse-checkout (cone) false-positive check"
D=$(mk F5); git -C "$D" sparse-checkout init --cone; echo "  init rc=$?"; git -C "$D" sparse-checkout set tools; echo "  set rc=$?"
echo "  sparse list:"; git -C "$D" sparse-checkout list; echo "  worktree:"; ls -A "$D"
echo "  ls-files -v:"; git -C "$D" ls-files -v | cut -c1-40; echo "  status:"; git -C "$D" status --porcelain; echo "  rc=$?"
wr "$BASEW" "$D"; wr "$CANDW" "$D"

echo "== F6 subdirectory root: ls-files scope vs status scope"
D=$(mk F6); git -C "$D" update-index --skip-worktree notes.md; printf 'forged\n' > "$D/notes.md"
echo "  cwd=tools ls-files -v -z:"; git -C "$D/tools" ls-files -v -z | tr '\0' '|'; echo
echo "  cwd=tools ls-files -v -z -- ':(top)':"; git -C "$D/tools" ls-files -v -z -- ':(top)' | tr '\0' '|'; echo
echo "  cwd=tools status --porcelain:"; git -C "$D/tools" status --porcelain; echo "  rc=$?"
echo "  cwd=tools rev-parse --show-toplevel:"; git -C "$D/tools" rev-parse --show-toplevel
echo "  writer subdir root (instrument resolution is cwd/top ambiguous; recorded as-is):"; INSTR=instr.sh wr "$CANDW" "$D/tools"; INSTR=instr.sh wr "$BASEW" "$D/tools"

echo "== F7 stat-spoof: same size + touch -r (ctime cannot be reset)"
D=$(mk F7); cp "$D/tools/counter.py" "$S/f7-orig"; printf 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' > "$S/f7-forged"; sz=$(stat -c %s "$D/tools/counter.py")
head -c "$sz" "$S/f7-forged" > "$D/tools/counter.py"; touch -r "$S/f7-orig" "$D/tools/counter.py"; printf 'size=%s forged-size=%s\n' "$sz" "$(stat -c %s "$D/tools/counter.py")"
git -C "$D" status --porcelain; echo "  status rc=$?"; wr "$CANDW" "$D"

echo "== F8 scratch-only: sweep /tmp artefacts' mtimes (no deletion)"
stat -c '%y %n' /tmp/alma.log /tmp/mori-r17-ctxcheck-pnxsnhyb 2>&1
echo "== F9 lane .git entries newer than swarm-registry marker (read-only)"
find "$LANE/.git" -maxdepth 1 -newer "$LANE/.ufo/waves/round-62/w1/swarm-registry.json" 2>/dev/null | head -20
stat -c '%y %n' "$LANE/.git/index" "$LANE/.git" 2>&1
echo "PROBES2 DONE"
