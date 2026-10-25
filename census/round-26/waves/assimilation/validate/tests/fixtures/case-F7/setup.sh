#!/usr/bin/env bash
# case-F7 materializer.
# Scratch-typed file with zero live references and mtime 3 days old
# -> expected verdict: SAFE(stale).
# usage: setup.sh <fixture-repo-root>   (created if missing; files overwritten)
set -euo pipefail

case_id=F7
target=.scratch/stale-probe-f7.tmp
age_days=3

dest=${1:?usage: setup.sh <fixture-repo-root>}
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

mkdir -p -- "$dest"
cp -R -- "$here/repo-tree/." "$dest/"
touch -d "@$(( $(date +%s) - age_days * 86400 ))" -- "$dest/$target"

# Give the fixture root a repository of its own (idempotent, offline, no
# commits): a tool that anchors its reference sweep on the target's repo then
# behaves as it does on a real lane instead of falling back to the live tree.
if [ ! -d "$dest/.git" ] && command -v git >/dev/null 2>&1; then
  export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_TERMINAL_PROMPT=0
  git -C "$dest" init -q -b master 2>/dev/null || git -C "$dest" init -q
fi

printf 'case=%s root=%s target=%s mtime_age_days=%s\n' \
  "$case_id" "$dest" "$target" "$age_days"
