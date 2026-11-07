#!/usr/bin/env bash
# S77Sentinel probe 12: --lane that is a SUBDIRECTORY of a repo. git status reads the whole repository
# (siblings and ancestors inside the work tree), but the guard's find only scans $lane. FIFO .gitignore
# at the repo root, lane = repo/sub -> guard count 0, status blocks.
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
mkdir -p "$D/sub"; printf 'x\n' > "$D/sub/keep"; git -C "$D" add sub/keep
git -C "$D" -c user.name=p -c user.email=p@x commit -q -m base || exit 1
cp "$S/gateW/souji-pre-report-gate.sh" "$P/gate.sh"
cp "$S/gateW/souji-receipt-write.py" "$P/souji-receipt-write.py"
sed -i 's/^gate_timeout=300$/gate_timeout=3/' "$P/gate.sh"
printf '## SHONEN\n' > "$M/report.md"; printf 'x\n' > "$M/prereg.txt"
lane="$D/sub"
mkfifo "$D/.gitignore"
echo "repo root : $D"
echo "lane      : $lane   (a subdirectory; --show-toplevel = $(git -C "$lane" rev-parse --show-toplevel))"
echo "guard's work-tree find count over \$lane: $(find "$lane" -path "$lane/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) ! -type f -print 2>/dev/null | wc -l)"
t0=$(date +%s%N)
setsid -w timeout -k 5 60 bash "$P/gate.sh" --lane "$lane" --branch nosuch --report "$M/report.md" --prereg "$M/prereg.txt" > "$M/out" 2>&1
rc=$?
t1=$(date +%s%N)
echo "gate rc=$rc elapsed=$(( (t1-t0)/1000000 ))ms"
grep -E '^check-clean|^detail-clean' "$M/out" | cut -c1-140
