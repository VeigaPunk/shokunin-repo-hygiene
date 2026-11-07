#!/usr/bin/env bash
# S77Sentinel probe 3: process cleanup.
# 3a: bounded git status (gate_timeout shortened to 2 in a scratch COPY) with a hanging core.fsmonitor hook
#     -> does timeout kill the hook child?
# 3b: real W gate blob hanging in the new pre-check (include.path -> FIFO) -> SIGTERM the gate; do its
#     git children survive?
set -u
S=/fast/scratch/hyaku/souji-r77/S77Sentinel
mkdir -p "$S" || exit 1
D=$(mktemp -d -p "$S" fx.XXXXXX) || exit 1
M=$(mktemp -d -p "$S" mk.XXXXXX) || exit 1
P=$(mktemp -d -p "$S" gate.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] && [ -n "$M" ] && [ -d "$M" ] && [ -n "$P" ] && [ -d "$P" ] || exit 1
trap 'rm -rf -- "$D" "$M" "$P"' EXIT
git -C "$D" init -q || exit 1
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; exit 1; }
git -C "$D" -c user.name=p -c user.email=p@x commit -q --allow-empty -m base || exit 1
printf 'x\n' > "$D/f"; git -C "$D" add f; git -C "$D" -c user.name=p -c user.email=p@x commit -q -m f

# ---------- 3a ----------
cp "$S/gateW/souji-pre-report-gate.sh" "$P/gate2.sh"
cp "$S/gateW/souji-receipt-write.py" "$P/souji-receipt-write.py"
# only edit: gate_timeout 300 -> 2
sed -i 's/^gate_timeout=300$/gate_timeout=2/' "$P/gate2.sh"
grep -n '^gate_timeout=' "$P/gate2.sh"
cat > "$M/slow-fsmonitor.sh" <<'EOF'
#!/bin/sh
echo "$$ $PPID" >> "$MARKER_DIR/fsmon-pids"
sleep 600
exit 0
EOF
chmod +x "$M/slow-fsmonitor.sh"
git -C "$D" config core.fsmonitor "$M/slow-fsmonitor.sh"
export MARKER_DIR="$M"
: > "$M/fsmon-pids"
printf '## SHONEN\n' > "$M/report.md"
printf 'x\n' > "$M/prereg.txt"
echo "=== 3a: gate copy (gate_timeout=2) on fixture with sleeping fsmonitor hook ==="
start=$(date +%s)
out=$(setsid timeout -k 5 60 bash "$P/gate2.sh" --lane "$D" --branch nosuch --report "$M/report.md" --prereg "$M/prereg.txt" 2>&1); rc=$?
end=$(date +%s)
printf 'gate rc=%s elapsed=%ss\n' "$rc" "$((end-start))"
printf '%s\n' "$out" | grep -E 'check-clean|detail-clean' | cut -c1-160
sleep 1
echo "--- fsmonitor hook pids recorded: [$(cat "$M/fsmon-pids")] ---"
while read -r pid ppid; do
  [ -n "${pid:-}" ] || continue
  if kill -0 "$pid" 2>/dev/null; then echo "LEAK: hook pid $pid still alive: $(ps -o args= -p "$pid" | cut -c1-80)"; else echo "clean: hook pid $pid gone"; fi
done < "$M/fsmon-pids"

# ---------- 3b ----------
git -C "$D" config --unset core.fsmonitor
mkfifo "$D/fifo.cfg" || exit 1
git -C "$D" config include.path "$D/fifo.cfg"
echo "=== 3b: real W gate blob, hang in pre-check (include.path -> FIFO); SIGTERM the gate after 2 s ==="
setsid bash "$S/gateW/souji-pre-report-gate.sh" --lane "$D" --branch nosuch --report "$M/report.md" --prereg "$M/prereg.txt" > "$M/g3.out" 2>&1 &
gp=$!
sleep 2
echo "gate pid $gp state: $(ps -o stat= -p "$gp" 2>/dev/null | tr -d ' ')"
echo "--- children before TERM ---"
ps -eo pid,ppid,pgid,stat,args | awk -v p="$gp" '$2==p || $3==p' | cut -c1-140
kill -TERM "$gp" 2>/dev/null
sleep 2
if kill -0 "$gp" 2>/dev/null; then echo "gate still alive after TERM"; else echo "gate gone after TERM"; fi
echo "--- processes still referencing fixture/gate after TERM ---"
ps -eo pid,ppid,pgid,stat,args | grep -E -F "$D" | grep -v grep | cut -c1-160 || echo none
echo "--- leftovers by gate copy path ---"
ps -eo pid,ppid,pgid,stat,args | grep -F "$S/gateW/" | grep -v grep | cut -c1-160 || echo none
echo "--- cleanup any leftovers referencing fixture ---"
for pid in $(ps -eo pid,args | grep -F "$D" | grep -v grep | awk '{print $1}'); do kill -KILL "$pid" 2>/dev/null && echo "killed $pid"; done
for pid in $(ps -eo pid,args | grep -F "$S/gateW/" | grep -v grep | awk '{print $1}'); do kill -KILL "$pid" 2>/dev/null && echo "killed $pid"; done
sleep 1
echo "--- final check ---"
ps -eo pid,args | grep -E -F "$D" | grep -v grep || echo none
