#!/usr/bin/env bash
# S77Sentinel probe 11: linked-worktree lane, end to end. FIFO at the path git actually reads
# (<common>/info/exclude). The guard looks at <absolute-git-dir>/info/exclude (the per-worktree dir) and
# misses it; check 4 then blocks until the 300 s timeout. gate copy shortens the timeout to 3 s only.
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
git -C "$D" worktree add -q "$D/wt" -b wtb || exit 1
lane="$D/wt"
[ "$(git -C "$lane" rev-parse --show-toplevel)" = "$lane" ] || { echo "WORKTREE MISMATCH"; exit 1; }
printf '## SHONEN\n' > "$M/report.md"; printf 'x\n' > "$M/prereg.txt"
cp "$S/gateW/souji-pre-report-gate.sh" "$P/gate.sh"
cp "$S/gateW/souji-receipt-write.py" "$P/souji-receipt-write.py"
sed -i 's/^gate_timeout=300$/gate_timeout=3/' "$P/gate.sh"
echo "worktree lane : $lane"
echo "absolute-git-dir    : $(git -C "$lane" rev-parse --absolute-git-dir)"
echo "git-path info/exclude: $(git -C "$lane" rev-parse --git-path info/exclude)"
COMMON=$(git -C "$lane" rev-parse --git-common-dir)
case $COMMON in /*) ;; *) COMMON=$lane/$COMMON ;; esac
rm -f "$COMMON/info/exclude"; mkfifo "$COMMON/info/exclude"
echo "FIFO placed at $COMMON/info/exclude"
echo "guard's target     : $(git -C "$lane" rev-parse --absolute-git-dir)/info/exclude  exists=$([ -e "$(git -C "$lane" rev-parse --absolute-git-dir)/info/exclude" ] && echo yes || echo no)"
t0=$(date +%s%N)
setsid -w timeout -k 5 60 bash "$P/gate.sh" --lane "$lane" --branch nosuch --report "$M/report.md" --prereg "$M/prereg.txt" > "$M/out" 2>&1
rc=$?
t1=$(date +%s%N)
echo "gate rc=$rc elapsed=$(( (t1-t0)/1000000 ))ms"
grep -E '^check-clean|^detail-clean' "$M/out" | cut -c1-140
echo "--- what the work-tree find branch sees (cannot see the common dir) ---"
find "$lane" -path "$lane/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) ! -type f -print 2>/dev/null | wc -l
