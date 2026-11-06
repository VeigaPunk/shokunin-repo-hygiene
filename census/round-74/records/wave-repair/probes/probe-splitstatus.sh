#!/usr/bin/env bash
# probe-splitstatus.sh — S74Sentinel: fail-open from a DISAGREEMENT between the
# gate's own `git status` and the writer's `_truth_refusal` status read.
#
# The gate (line 43) runs `git -C $lane status` with NO config pinning.
# The writer's git() helper pins `-c core.fsmonitor=false` (r63) plus
# GIT_CONFIG_GLOBAL=/dev/null, so the writer SEES a change the gate cannot.
# `_truth_refusal` skips every path its own status lists ("reported clean by
# git status" is assumed) and returns None when `bad` is empty — so a plain,
# un-forged, dirty tracked file passes check 4.
#
# Recipe (the writer's own selftest case_16 shape, moved to repo-local config):
#   git config core.fsmonitor <hook>          # repo-local .git/config: invisible to status
#   <plain edit of a tracked file>
#   git update-index --fsmonitor-valid a.txt  # index bit: status trusts it
# Usage: probe-splitstatus.sh <SCRATCH> <gate-dir>
set -u
S=${1:?scratch}; GATE_DIR=${2:?gate dir}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"
R="$S/ss"; rm -rf "$R"
python3 -B "$HERE/mkfixture.py" --root "$R" >/dev/null
L="$R/lane"
test -n "$L" || exit 9
[ "$(git -C "$L" rev-parse --show-toplevel)" = "$(cd "$L" && pwd -P)" ] || { echo "toplevel mismatch"; exit 1; }

printf '#!/bin/sh\necho "/"\nexit 0\n' > "$R/silent-fsmonitor.sh"; chmod +x "$R/silent-fsmonitor.sh"
git -C "$L" config core.fsmonitor "$R/silent-fsmonitor.sh"
printf 'DIRTY-PLAIN-EDIT\n' >> "$L/a.txt"
git -C "$L" update-index --fsmonitor-valid a.txt

echo "=== gate's view: git -C lane status --porcelain -uall ==="
git -C "$L" status --porcelain=v1 --untracked-files=all | cat -A
echo "status-lines=$(git -C "$L" status --porcelain=v1 --untracked-files=all | wc -l)"
echo "=== writer's view: -c core.fsmonitor=false plus the r63/r66 pins ==="
env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git -C "$L" -c core.fsmonitor=false \
  -c core.excludesFile=/dev/null -c core.fileMode=true -c core.checkStat=default \
  -c core.trustctime=true status --porcelain=v1 --untracked-files=all | cat -A
echo "=== object check: worktree bytes vs index object id ==="
echo "hash-object=$(git -C "$L" hash-object a.txt)  index=$(git -C "$L" ls-files -s a.txt)"

printf '# Report\n\n## SHONEN\n[~] box `a`\n' > "$R/report.md"; printf 'prereg\n' > "$R/prereg.txt"
echo "=== gate run ==="
( cd "$L" && timeout 120 bash "$GATE_DIR/gate-w.sh" --lane "$L" --branch master \
    --report "$R/report.md" --prereg "$R/prereg.txt" ) > "$R/out.txt" 2>&1
echo "EXIT=$?"
grep -E '^check-|^detail-' "$R/out.txt"
