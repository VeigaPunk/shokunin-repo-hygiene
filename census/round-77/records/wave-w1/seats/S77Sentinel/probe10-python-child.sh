#!/usr/bin/env bash
# S77Sentinel probe 10: check 4's python block — process cleanup and timeout expiry.
# Uses a scratch COPY of the gate (only gate_timeout changed) and a stub writer that sleeps, so the
# python child can be observed. The real writer's identity is irrelevant to process management.
set -u
S=/fast/scratch/hyaku/souji-r77/S77Sentinel
mkdir -p "$S" || exit 1
D=$(mktemp -d -p "$S" fx.XXXXXX) || exit 1
P=$(mktemp -d -p "$S" gp.XXXXXX) || exit 1
M=$(mktemp -d -p "$S" mk.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] && [ -n "$P" ] && [ -d "$P" ] && [ -n "$M" ] && [ -d "$M" ] || exit 1
trap 'for d in "$D" "$P" "$M"; do rm -rf -- "$d"; done' EXIT
git -C "$D" init -q || exit 1
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; exit 1; }
printf 'x\n' > "$D/f"; git -C "$D" add f
git -C "$D" -c user.name=p -c user.email=p@x commit -q -m base || exit 1
printf '## SHONEN\n' > "$M/report.md"; printf 'x\n' > "$M/prereg.txt"
cp "$S/gateW/souji-pre-report-gate.sh" "$P/gate.sh"
printf 'import time\nprint("stub writer sleeping")\ntime.sleep(600)\n' > "$P/souji-receipt-write.py"
desc() {
  local frontier=$1 seen= next p
  while [ -n "$frontier" ]; do
    next=
    for p in $frontier; do for c in $(ps -o pid= --ppid "$p" 2>/dev/null); do next="$next $c"; done; done
    [ -n "$next" ] || break
    seen="$seen $next"; frontier=$next
  done
  printf '%s\n' $seen | sort -u
}

echo "=== 10a: timeout expiry kills the python child (gate_timeout=2 copy) ==="
sed -i 's/^gate_timeout=300$/gate_timeout=2/' "$P/gate.sh"
bash "$P/gate.sh" --lane "$D" --branch nosuch --report "$M/report.md" --prereg "$M/prereg.txt" > "$M/a.out" 2>&1 &
gp=$!
sleep 1
KIDS=$(desc "$gp")
echo "descendants at 1 s:"; for p in $KIDS; do printf '  %s\n' "$(ps -o pid=,stat=,args= -p "$p" | cut -c1-100)"; done
wait "$gp" 2>/dev/null; echo "gate rc=$? (124 = timeout expiry surfaced as FAIL check)"
grep -E '^check-clean|^detail-clean' "$M/a.out" | cut -c1-120
sleep 1
for p in $KIDS; do kill -0 "$p" 2>/dev/null && echo "  LEAK after expiry: $p $(ps -o args= -p "$p" | cut -c1-70)"; done
echo "  (no LEAK lines = timeout killed the block)"

echo "=== 10b: SIGTERM to the gate while the python block runs (gate_timeout=300) ==="
sed -i 's/^gate_timeout=2$/gate_timeout=300/' "$P/gate.sh"
bash "$P/gate.sh" --lane "$D" --branch nosuch --report "$M/report.md" --prereg "$M/prereg.txt" > "$M/b.out" 2>&1 &
gp=$!
sleep 2
KIDS=$(desc "$gp")
echo "descendants at 2 s:"; for p in $KIDS; do printf '  %s\n' "$(ps -o pid=,stat=,args= -p "$p" | cut -c1-100)"; done
kill -TERM "$gp" 2>/dev/null
sleep 2
kill -0 "$gp" 2>/dev/null && echo "gate alive after TERM" || echo "gate gone after TERM"
N=0
for p in $KIDS; do if kill -0 "$p" 2>/dev/null; then N=$((N+1)); echo "  LEAK: $p $(ps -o args= -p "$p" | cut -c1-80)"; fi; done
echo "  leaks: $N"
for p in $KIDS; do kill -KILL "$p" 2>/dev/null; done
sleep 1
for p in $KIDS; do kill -0 "$p" 2>/dev/null && echo "  STILL ALIVE $p"; done
echo done
