#!/usr/bin/env bash
# souji r73 receipt runner: run ONE command from the lane root and write a receipt whose header binds
# the literal command (replayable from the lane root on this host: every path in it is either
# lane-relative or an absolute scratch path the command line itself creates), the sha256 of every
# file named with --bind, and the lane branch tip. The body is the command's combined output; the
# last line is EXIT=<rc> as returned by the command itself (not composed from a constant).
# Usage: census/round-73/run-receipt.sh <receipt> [--bind FILE]... -- <command...>
set -u
out=$1; shift
binds=()
while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do
  [ "$1" = "--bind" ] || { echo "usage: run-receipt.sh <receipt> [--bind FILE]... -- cmd" >&2; exit 2; }
  binds+=("$2"); shift 2
done
[ "${1:-}" = "--" ] || { echo "missing --" >&2; exit 2; }
shift
[ -e "$out" ] && { echo "receipt exists: $out" >&2; exit 2; }
lane=$(cd "$(dirname "$0")/../.." && pwd)
cd "$lane" || exit 2
tip=$(git rev-parse refs/heads/master)
{
  printf '# command=%s\n' "$(printf '%q ' "$@" | sed 's/ $//')"
  printf '# cwd=lane root; lane master=%s; host=%s; git=%s\n' "$tip" "$(uname -sr)" "$(git --version | cut -d' ' -f3)"
  for b in "${binds[@]+"${binds[@]}"}"; do printf '# bind %s sha256=%s\n' "$b" "$(sha256sum "$b" | cut -d' ' -f1)"; done
  "$@" 2>&1
  rc=$?
  printf 'EXIT=%s\n' "$rc"
} > "$out"
tail -3 "$out"
