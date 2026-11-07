#!/usr/bin/env bash
# Scratch fixture: a minimal lane-like repo + report + prereg for gate runs.
# Usage: mkfixture.sh ABS_DIR   (must live under the seat scratch)
set -euo pipefail
F="$1"
case "$F" in /fast/scratch/hyaku/souji-r79/S79ExecEvade/*) ;; *) echo "refusing non-scratch fixture $F" >&2; exit 1;; esac
rm -rf "$F"
mkdir -p "$F"
export GIT_AUTHOR_NAME=fx GIT_AUTHOR_EMAIL=fx@fx GIT_COMMITTER_NAME=fx GIT_COMMITTER_EMAIL=fx@fx
git init -q -b master "$F/repo"
T="$(git -C "$F/repo" rev-parse --show-toplevel)"
[ "$T" = "$F/repo" ] || { echo "BAD_TOPLEVEL $T" >&2; exit 1; }
echo x > "$F/repo/file.txt"
git -C "$F/repo" add file.txt
git -C "$F/repo" commit -qm init
git -C "$F/repo" remote add origin "$F/repo"
printf '## SHONEN\nbody\n' > "$F/report.md"
printf 'prereg\n' > "$F/prereg.txt"
echo "fixture ready: $F"
