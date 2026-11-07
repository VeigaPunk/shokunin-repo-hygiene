#!/usr/bin/env bash
# S77Sentinel probe 8: prune robustness of `find "$lane" -path "$lane/.git" -prune`.
# 8a: trailing slash on --lane defeats the prune (false refusal if .git holds a .gitignore-named non-file).
# 8b: glob metacharacters in the lane path defeat the prune.
set -u
S=/fast/scratch/hyaku/souji-r77/S77Sentinel
mkdir -p "$S" || exit 1
M=$(mktemp -d -p "$S" mk.XXXXXX) || exit 1
[ -n "$M" ] && [ -d "$M" ] || exit 1
printf '## SHONEN\n' > "$M/report.md"; printf 'x\n' > "$M/prereg.txt"
GATE="$S/gateW/souji-pre-report-gate.sh"
run_gate() {
  local lane=$1 t0 t1 out rc
  t0=$(date +%s%N)
  out=$(setsid timeout -k 5 20 bash "$GATE" --lane "$lane" --branch nosuch --report "$M/report.md" --prereg "$M/prereg.txt" 2>&1); rc=$?
  t1=$(date +%s%N)
  printf 'lane=%-52s rc=%-3s %sms  %s  %s\n' "$lane" "$rc" "$(( (t1-t0)/1000000 ))" \
    "$(printf '%s\n' "$out" | grep -m1 '^check-clean=')" \
    "$(printf '%s\n' "$out" | grep -m1 '^detail-clean:' | cut -c1-90)"
}
D=$(mktemp -d -p "$S" fx.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] || exit 1
trap 'rm -rf -- "$D" "$M"' EXIT
git -C "$D" init -q || exit 1
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; exit 1; }
git -C "$D" -c user.name=p -c user.email=p@x commit -q --allow-empty -m base || exit 1
mkdir -p "$D/.git/info"
mkfifo "$D/.git/info-not-a-source.gitignore" 2>/dev/null || true
# a non-file literally named .gitignore INSIDE .git (git never reads it)
mkfifo "$D/.git/.gitignore" || exit 1
echo "=== 8a: FIFO named .gitignore inside .git only ==="
run_gate "$D"
echo "=== 8a: same lane with a trailing slash ==="
run_gate "$D/"
echo "=== 8a: same lane with /./ inserted ==="
run_gate "$D/./"
rm -f "$D/.git/.gitignore"
echo "=== 8b: lane path containing glob metacharacters ==="
G=$(mktemp -d -p "$S" 'lane[1].XXXXXX') || exit 1
[ -n "$G" ] && [ -d "$G" ] || exit 1
git -C "$G" init -q || exit 1
[ "$(git -C "$G" rev-parse --show-toplevel)" = "$G" ] || { echo "TOPLEVEL MISMATCH"; exit 1; }
git -C "$G" -c user.name=p -c user.email=p@x commit -q --allow-empty -m base || exit 1
mkfifo "$G/.git/.gitignore"
echo "lane path (bracket): $G"
run_gate "$G"
echo "--- find expression direct view (does it descend into .git?) ---"
find "$G" -path "$G/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) ! -type f -print 2>/dev/null | sed "s|^$G|<LANE>|"
echo "find over lane root only, .git excluded manually:"
find "$G/.git" -maxdepth 1 -name .gitignore -printf '%y %p\n' 2>/dev/null | sed "s|^|  |"
rm -rf -- "$G"
for pid in $(ps -eo pid,args | grep -F "$S/fx." | grep -v grep | awk '{print $1}'); do kill -KILL "$pid" 2>/dev/null; done
