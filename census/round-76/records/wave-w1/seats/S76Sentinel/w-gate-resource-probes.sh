#!/usr/bin/env bash
# S76Sentinel: resource probes for the W gate check-4 attribution block. Builds one fixture per shape
# under $S and times the gate; reports wall time and peak RSS of the whole gate process tree.
set -u
S=${S:-/fast/scratch/hyaku/souji-r76/S76Sentinel}
G=$S/G
REP=$S/report.md
PRE=$S/prereg.txt
printf '## SHONEN\nx\n' >"$REP"
printf 'prereg body\n' >"$PRE"

mkfx() {
  local d
  d=$(mktemp -d -p "$S" fx.XXXXXX) || exit 1
  [ -n "$d" ] && [ -d "$d" ] || { echo "EMPTY-FIXTURE-PATH" >&2; exit 1; }
  git -C "$d" init -q || exit 1
  [ "$(git -C "$d" rev-parse --show-toplevel)" = "$d" ] || { echo "FIXTURE-TOPLEVEL-MISMATCH" >&2; exit 1; }
  printf 'base\n' >"$d/README.md"
  printf '__pycache__/\nbig/\n' >"$d/.gitignore"
  git -C "$d" -c user.name=fx -c user.email=fx@fx add -A || exit 1
  git -C "$d" -c user.name=fx -c user.email=fx@fx commit -q -m base || exit 1
  echo "$d"
}
timed() { # $1 lane $2 label
  local lane=$1 label=$2 t0 t1 rss
  t0=$(date +%s%N)
  out=$(timeout 240 bash "$G/souji-pre-report-gate.sh" --lane "$lane" --branch main \
        --report "$REP" --prereg "$PRE" 2>&1); rc=$?
  t1=$(date +%s%N)
  printf '%-28s wall=%5dms rc=%s %s\n' "$label" $(( (t1 - t0) / 1000000 )) "$rc" \
    "$(printf '%s\n' "$out" | grep -E '^check-clean=|^detail-clean:' | tr '\n' ' ' | cut -c1-160)"
}

case ${1:-} in
many-ignored) # 200k files ignored by a tracked top-level rule
  d=$(mkfx); mkdir -p "$d/big"
  ( cd "$d/big" && seq -f 'f%06g' 1 200000 | xargs -n 2000 touch ) || exit 1
  echo "ROUTE many-ignored fixture=$d files=$(find "$d/big" -type f | wc -l)"
  timed "$d" "200k ignored under big/" ;;
deep-tree) # directory depth 2000, one untracked file at the bottom
  d=$(mkfx)
  ( cd "$d" && for i in $(seq 2000); do mkdir a && cd a || exit 1; done && printf 'x\n' >leaf.txt ) || exit 1
  echo "ROUTE deep-tree fixture=$d depth=$(cd "$d" && p=. && n=0 && while [ -d "$p/a" ]; do p="$p/a"; n=$((n+1)); done; echo "$n")"
  timed "$d" "depth 2000 untracked leaf" ;;
selfignore-50k) # 50k paths under a self-ignoring untracked dir
  d=$(mkfx); mkdir -p "$d/cache"; printf '*\n' >"$d/cache/.gitignore"
  ( cd "$d/cache" && seq -f 'p%06g' 1 50000 | xargs -n 2000 touch ) || exit 1
  echo "ROUTE selfignore-50k fixture=$d files=$(find "$d/cache" -type f | wc -l)"
  timed "$d" "50k self-ignoring paths" ;;
wide-ignored-dirs) # 5000 ignored dirs x 40 files (directory-rule fanout)
  d=$(mkfx); mkdir -p "$d/big"
  ( cd "$d/big" && seq -f 'd%04g' 1 5000 | xargs -n 500 mkdir && for x in d*; do ( cd "$x" && seq -f 'f%03g' 1 40 | xargs -n 40 touch ); done ) || exit 1
  echo "ROUTE wide-ignored-dirs fixture=$d files=$(find "$d/big" -type f | wc -l)"
  timed "$d" "5000 ignored dirs / 200k files" ;;
*) echo "unknown route ${1:-}" >&2; exit 2 ;;
esac
