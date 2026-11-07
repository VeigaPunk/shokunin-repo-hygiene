#!/usr/bin/env bash
# S77Sentinel probe 1: can a repo-local config (include.path -> FIFO) make the W gate's new
# pre-check calls (`git rev-parse --absolute-git-dir`, `git config --path --get`) block?
# Fixture rules: explicit template with XXXXXX, toplevel assertion, -C "$D" everywhere.
set -u
S=/fast/scratch/hyaku/souji-r77/S77Sentinel
mkdir -p "$S" || exit 1
D=$(mktemp -d -p "$S" fx.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] || exit 1
trap 'rm -rf -- "$D"' EXIT
git -C "$D" init -q || exit 1
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; exit 1; }
git -C "$D" -c user.name=p -c user.email=p@x commit -q --allow-empty -m base || exit 1

mkfifo "$D/fifo.cfg" || exit 1
git -C "$D" config include.path "$D/fifo.cfg" || exit 1
echo "config written; probing each call under setsid timeout -k 5 5:"

probe() {
  local name=$1; shift
  local rc out
  out=$(setsid timeout -k 5 5 "$@" 2>&1); rc=$?
  printf '%-45s rc=%-3s out=%q\n' "$name" "$rc" "$out"
}
probe "git rev-parse --absolute-git-dir" git -C "$D" rev-parse --absolute-git-dir
probe "git config --path --get core.excludesFile" git -C "$D" config --path --get core.excludesFile
probe "git status --porcelain" git -C "$D" --no-optional-locks status --porcelain
probe "git config --list" git -C "$D" config --list
echo "--- leftover processes referencing fixture (should be none) ---"
ps -eo pid,pgid,stat,args | grep -F "$D" | grep -v grep || echo none
