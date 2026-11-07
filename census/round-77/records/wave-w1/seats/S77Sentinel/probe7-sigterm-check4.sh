#!/usr/bin/env bash
# S77Sentinel probe 7: SIGTERM to the gate during check 4 (the timed region). Do git/hook/python children
# survive? (check 4 = `timeout -k 5 300 git status` then `timeout -k 5 300 python3 ...`).
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
echo "$$" >> "$MARKER_DIR/hookpids"
sleep 600
EOF
chmod +x "$M/slow-fsmonitor.sh"
git -C "$D" config core.fsmonitor "$M/slow-fsmonitor.sh"
export MARKER_DIR="$M"
: > "$M/hookpids"
printf '## SHONEN\n' > "$M/report.md"
printf 'x\n' > "$M/prereg.txt"
echo "=== start real W gate; TERM it 2 s into check 4 ==="
setsid bash "$S/gateW/souji-pre-report-gate.sh" --lane "$D" --branch nosuch --report "$M/report.md" --prereg "$M/prereg.txt" > "$M/g.out" 2>&1 &
gp=$!
sleep 2
echo "--- tree before TERM (pid ppid pgid stat args) ---"
ps -eo pid,ppid,pgid,stat,args | awk -v p="$gp" '$1==p || $2==p || $3==p' | cut -c1-150
kill -TERM "$gp" 2>/dev/null
sleep 2
if kill -0 "$gp" 2>/dev/null; then echo "gate alive after TERM"; else echo "gate gone after TERM"; fi
echo "--- survivors after TERM (gate pgid $gp) ---"
ps -eo pid,ppid,pgid,stat,args | awk -v g="$gp" '$3==g' | cut -c1-150 || true
echo "--- survivors by fixture path ---"
ps -eo pid,ppid,pgid,stat,args | grep -F "$D" | grep -v grep | cut -c1-150 || echo none
echo "--- hook pids recorded ---"
cat "$M/hookpids" 2>/dev/null || echo none
for pid in $(cat "$M/hookpids" 2>/dev/null); do
  if kill -0 "$pid" 2>/dev/null; then echo "LEAK: hook $pid alive: $(ps -o args= -p "$pid" | cut -c1-70)"; else echo "clean: hook $pid gone"; fi
done
echo "--- kill any survivors of this probe ---"
for pid in $(ps -eo pid,args | grep -F "$D" | grep -v grep | awk '{print $1}'); do kill -KILL "$pid" 2>/dev/null && echo "killed $pid"; done
for pid in $(cat "$M/hookpids" 2>/dev/null); do kill -KILL "$pid" 2>/dev/null && echo "killed hook $pid"; done
sleep 1
ps -eo pid,args | grep -F "$D" | grep -v grep || echo "none left"
