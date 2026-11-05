#!/bin/bash
export S=/fast/scratch/hyaku/souji-r62/S62SentinelScope
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
BASEW=$LANE/tools/souji-receipt-write.py
CANDW=$S/cand.py
CAND2=$S/cand2.py
source <(sed -n '/^mk() {/,/^echo "== T0/p' "$S/probe.sh" | sed '$d')
echo "== G5 fresh state per writer, hook on, bit set, forged"
for W in "$CANDW" "$CAND2" "$BASEW"; do
  D=$(mk "G5$(basename "$W" .py)")
  ( export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0="$S/fsm.sh"
    git -C "$D" status --porcelain >/dev/null; git -C "$D" update-index --fsmonitor-valid tools/counter.py
    printf 'forged\n' > "$D/tools/counter.py"
    wr "$W" "$D" )
done
echo PROBES5 DONE
