## Status
STATUS: PARTIAL — counter draft written; installed gate and fixture were absent when inspected, so execution and receipt verification remain for L1 after integration.

## Evidence
- Read-only `git rev-parse HEAD` → `e78ac7c4837b81b634db4a927605a751a7f006ba`; `git status --porcelain` showed pre-existing round-26 and round-27 workspace changes. No existing lane changes were modified by this seat.
- Frozen contract, `.ufo/waves/round-27/preregistration.txt:9`: “Counter: tool absent at base → present at tip; `bash tests/fixtures/r27-pre-report-gate.sh` → `cases=4 pass=4 control=FALSE-GREEN-REJECTED` rc 0; c3 receipt verify=ok.”
- `glob` inspection found neither `tools/souji-pre-report-gate.sh` nor `tests/fixtures/r27-pre-report-gate.sh`; the base revision is the registered round-27 base.
- No fixture, build, or verification command was run. No tools installed or updated.

## Findings
1. Draft counter at `.ufo/waves/round-27/w1/c3-counter.sh`; emits `tool=absent|present`, hashes the installed gate bytes, runs the exact absolute fixture path, requires exactly one exact contract summary line, and emits a tab-separated header and values (`tool_sha256`, `cases`, `pass`, `control`, `rc`). A nonzero fixture rc is retained and causes nonzero counter exit; missing tool and malformed/missing summary fail closed.
2. The counter does not implement or certify the gate/fixture. L1 must install those sibling drafts, run this counter after integration, and verify the durable receipt against committed bytes.

## Draft script text
```bash
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
```
