#!/usr/bin/env bash
# souji r97 receipt runner (same wrapper as r96): run-receipt.sh <receipt path> <command...>
# Writes the command, the lane branch tip and the date as `#` header lines, then the command's merged stdout/stderr,
# then `EXIT <rc>`. Run from the lane root. Scratch paths are passed in the command; nothing is written under /tmp.
set -u
out=$1
shift
{
  echo "# command: $*"
  echo "# lane master: $(git rev-parse master) date: $(date -Is)"
  "$@" 2>&1
  echo "EXIT $?"
} > "$out"
