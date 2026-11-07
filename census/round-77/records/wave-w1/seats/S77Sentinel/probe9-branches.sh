#!/usr/bin/env bash
# S77Sentinel probe 9 (fixed): remaining guard branches.
#  9a symlink $GIT_DIR/info/exclude -> FIFO (n10 shape)
#  9b .git as a symlink to a real gitdir
#  9c --lane that is not a repository (the -1 branch; path echoed?)
#  9d FIFO .gitignore in a TRACKED directory (n2 shape)
#  9e relative core.excludesFile pointing at a FIFO
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
  printf '  rc=%-3s %sms %s | %s leaked_path=%s\n' "$rc" "$(( (t1-t0)/1000000 ))" \
    "$(printf '%s\n' "$out" | grep -m1 '^check-clean=')" \
    "$(printf '%s\n' "$out" | grep -m1 '^detail-clean:' | cut -c1-110)" \
    "$(printf '%s\n' "$out" | grep -qF "$lane" && echo YES || echo no)"
}
mkfix() {
  local d; d=$(mktemp -d -p "$S" fx.XXXXXX) || return 1
  [ -n "$d" ] && [ -d "$d" ] || return 1
  git -C "$d" init -q || return 1
  [ "$(git -C "$d" rev-parse --show-toplevel)" = "$d" ] || return 1
  git -C "$d" -c user.name=p -c user.email=p@x commit -q --allow-empty -m base || return 1
  printf '%s' "$d"
}
newfix() { FIX=$(mkfix) || { echo "FIXTURE FAILED"; exit 1; }; D=$FIX; }
trap 'for d in ${D:-} ${R:-}; do [ -n "$d" ] && rm -rf -- "$d"; done; rm -rf -- "$M"' EXIT

echo "=== 9a: symlink .git/info/exclude -> FIFO (n10 shape) ==="
newfix; rm -f "$D/.git/info/exclude"; mkfifo "$D/fifo.target"; ln -s ../fifo.target "$D/.git/info/exclude"
ls -l "$D/.git/info/exclude" | sed 's|^|  |'
run_gate "$D"; rm -rf "$D"; D=

echo "=== 9b: .git itself is a symlink to a real git dir ==="
newfix
R=$(mktemp -d -p "$S" real.XXXXXX); mv "$D/.git" "$R/gitdir"; ln -s "$R/gitdir" "$D/.git"
echo "  --absolute-git-dir: $(git -C "$D" rev-parse --absolute-git-dir)"
rm -f "$R/gitdir/info/exclude"; mkfifo "$R/gitdir/info/exclude"
run_gate "$D"; rm -rf "$D" "$R"; D= R=

echo "=== 9c: --lane not a repo (the -1 branch) ==="
N=$(mktemp -d -p "$S" notrepo.XXXXXX); run_gate "$N"; rm -rf "$N"

echo "=== 9d: FIFO .gitignore in a TRACKED directory ==="
newfix
mkdir -p "$D/tracked"; printf 'x\n' > "$D/tracked/keep"; git -C "$D" add tracked/keep
git -C "$D" -c user.name=p -c user.email=p@x commit -q -m tracked
mkfifo "$D/tracked/.gitignore"
run_gate "$D"; rm -rf "$D"; D=

echo "=== 9e: relative core.excludesFile pointing at a FIFO ==="
newfix
mkfifo "$D/rel.excl"; git -C "$D" config core.excludesFile "rel.excl"
echo "  git config --path --get: $(git -C "$D" config --path --get core.excludesFile)"
run_gate "$D"; rm -rf "$D"; D=
for pid in $(ps -eo pid,args | grep -F "$S/fx." | grep -v grep | awk '{print $1}'); do kill -KILL "$pid" 2>/dev/null; done
echo "post: $(ps -eo args | grep -cF "$S/fx.")"
