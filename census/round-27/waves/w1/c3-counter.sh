#!/usr/bin/env bash
# Round 27 C3 counter draft. Read-only; measures installed tool bytes and fixture outcome.
set -u

LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
TOOL="$LANE/tools/souji-pre-report-gate.sh"
FIXTURE="$LANE/tests/fixtures/r27-pre-report-gate.sh"

if [[ ! -f "$TOOL" ]]; then
  printf 'tool=absent\n'
  printf 'tool_sha256\tcases\tpass\tcontrol\trc\n'
  printf '\t\t\t\t1\n'
  exit 1
fi
printf 'tool=present\n'
sha_line=$(sha256sum -- "$TOOL") || exit 1
tool_sha256=${sha_line%% *}
if [[ ! $tool_sha256 =~ ^[0-9a-f]{64}$ ]]; then
  printf 'counter error: could not parse tool sha256\n' >&2
  exit 1
fi

output=$(bash "$FIXTURE" 2>&1)
rc=$?
summary=$(printf '%s\n' "$output" | awk '/^cases=4 pass=4 control=FALSE-GREEN-REJECTED$/ { if (found) exit 2; found=$0 } END { if (found) print found; else exit 1 }')
parse_rc=$?
if (( parse_rc != 0 )); then
  printf '%s\n' "$output" >&2
  printf 'counter error: expected exactly one C3 summary line\n' >&2
  printf 'tool_sha256\tcases\tpass\tcontrol\trc\n%s\t\t\t\t%d\n' "$tool_sha256" "$rc"
  exit 1
fi

printf 'tool_sha256\tcases\tpass\tcontrol\trc\n'
printf '%s\t4\t4\tFALSE-GREEN-REJECTED\t%d\n' "$tool_sha256" "$rc"
(( rc == 0 ))
