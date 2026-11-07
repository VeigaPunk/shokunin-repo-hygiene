#!/usr/bin/env bash
# S77Sentinel probe 7b: SIGTERM to the gate during check 4 — precise descendant accounting.
# No setsid on the launcher (it forks and loses $!): start the gate directly, record its descendants
# before TERM, then check which of those pids survive after the gate is gone.
set -u
S=/fast/scratch/hyaku/souji-r77/S77Sentinel
mkdir -p "$S" || exit 1
D=$(mktemp -d -p "$S" fx.XXXXXX) || exit 1
M=$(mktemp -d -p "$S" mk.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] && [ -n "$M" ] && [ -d "$M" ] || exit 1
trap 'rm -rf -- "$D" "$M"' EXIT
git -C "$D" init -q || exit 1
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; exit 1; }
printf 'x\n' > "$D/f"; git -C "$D" add f
git -C "$D" -c user.name=p -c user.email=p@x commit -q -m base || exit 1
cat > "$M/slow-fsmonitor.sh" <<'EOF'
#!/bin/sh
sleep 600
EOF
chmod +x "$M/slow-fsmonitor.sh"
git -C "$D" config core.fsmonitor "$M/slow-fsmonitor.sh"
printf '## SHONEN\n' > "$M/report.md"; printf 'x\n' > "$M/prereg.txt"

echo "=== start real W gate directly; TERM after 2 s ==="
bash "$S/gateW/souji-pre-report-gate.sh" --lane "$D" --branch nosuch --report "$M/report.md" --prereg "$M/prereg.txt" > "$M/g.out" 2>&1 &
gp=$!
sleep 2
desc() { # all descendants of $1, one pid per line
  local frontier=$1 seen= next p
  while [ -n "$frontier" ]; do
    next=
    for p in $frontier; do
      for c in $(ps -o pid= --ppid "$p" 2>/dev/null); do next="$next $c"; done
    done
    [ -n "$next" ] || break
    seen="$seen $next"; frontier=$next
  done
  printf '%s\n' $seen | sort -u
}
echo "gate pid $gp"
DESC=$(desc "$gp")
echo "--- descendants before TERM ---"
for p in $DESC; do printf '  %s\n' "$(ps -o pid=,ppid=,stat=,args= -p "$p" | cut -c1-120)"; done
kill -TERM "$gp" 2>/dev/null
sleep 3
echo "--- gate alive? ---"
if kill -0 "$gp" 2>/dev/null; then echo "gate STILL ALIVE after TERM"; else echo "gate gone"; fi
echo "--- recorded descendants after TERM ---"
LEAKS=0
for p in $DESC; do
  if kill -0 "$p" 2>/dev/null; then LEAKS=$((LEAKS+1)); echo "  LEAK pid $p: $(ps -o args= -p "$p" | cut -c1-110)"; fi
done
echo "LEAK COUNT=$LEAKS"
echo "--- kill leaks from this probe ---"
for p in $DESC; do kill -KILL "$p" 2>/dev/null && echo "  killed $p"; done
sleep 1
for p in $DESC; do kill -0 "$p" 2>/dev/null && echo "  still alive $p"; done
echo done
