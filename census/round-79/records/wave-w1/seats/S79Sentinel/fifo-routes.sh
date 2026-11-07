#!/usr/bin/env bash
# S79Sentinel r79: spot-run three r78 hostile-repo routes (FIFO at .git/config, FIFO at .git/HEAD,
# FIFO as an include.path target) against the W1 gate blob ae5022c5... .  Expect: no block, rc=1,
# check-gitsource=FAIL, no check-signal line, no leftover process from the fixture.
set -u
S=/fast/scratch/hyaku/souji-r79/S79Sentinel
G=$S/gw1/souji-pre-report-gate.sh
B=$S/fx
mkdir -p "$B" || exit 1

route() {  # $1 name, $2 setup-fn
  local name=$1 d t0 t1 rc left
  d=$(mktemp -d -p "$B" "fx.XXXXXX") || exit 1
  [ -n "$d" ] && [ -d "$d" ] || exit 1
  git -C "$d" init -q -b master || exit 1
  [ "$(git -C "$d" rev-parse --show-toplevel)" = "$d" ] || exit 1
  printf 'x\n' > "$d/a.txt"
  git -C "$d" add -A || exit 1
  git -C "$d" -c user.name=fx -c user.email=fx@fx commit -q -m seed || exit 1
  printf '# r\n\n## SHONEN\n\n- [ ] b\n' > "$d/report.md"
  printf 'frozen\n' > "$d/prereg.txt"
  "$2" "$d"
  t0=$(date +%s%N)
  timeout -k 5 25 setsid --wait bash "$G" --lane "$d" --branch master \
      --report "$d/report.md" --prereg "$d/prereg.txt" > "$d/out" 2> "$d/err"
  rc=$?
  t1=$(date +%s%N)
  left=$(ps -eo pid,args | grep -F "$d" | grep -v grep | wc -l)
  printf 'ROUTE %s rc=%s ms=%s gitsource_fail=%s signal_lines=%s leftover=%s\n' \
    "$name" "$rc" "$(( (t1 - t0) / 1000000 ))" \
    "$(grep -c '^check-gitsource=FAIL' "$d/out")" \
    "$(grep -c 'check-signal' "$d/out" "$d/err" | awk -F: '{s+=$2} END{print s+0}')" "$left"
  grep -hE '^(check-|detail-)' "$d/out" "$d/err" | sed 's/^/    /'
}

fifo_config() { rm -f "$1/.git/config"; mkfifo "$1/.git/config"; }
fifo_head()   { rm -f "$1/.git/HEAD";   mkfifo "$1/.git/HEAD"; }
fifo_include() {
  mkfifo "$1/inc.fifo"
  printf '[include]\n\tpath = %s\n' "$1/inc.fifo" >> "$1/.git/config"
}

route fifo-git-config fifo_config
route fifo-git-head fifo_head
route fifo-include-path fifo_include
