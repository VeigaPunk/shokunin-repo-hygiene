## Status
STATUS: PARTIAL — script delivered and shell grammar checked; live gate execution was intentionally not performed.

## Evidence
- Command: `bash -n /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/c1-counter.sh` → `bash -n rc=0`.
- Revision context: frozen preregistration pins base `e78ac7c4837b81b634db4a927605a751a7f006ba`; the script's `--base` pins that full id.
- Source: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt` § C1: “Before: `findings=2` at e78ac7c. After: `findings=0` at the landing tip.”
- Source: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:1152-1164`: “SUMMARY\tfindings=%d\tchecked_reg=%d” (excerpt).

## Findings
1. Delivered `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/c1-counter.sh`. It requires `--rev <full40>` or `--base`, rejects malformed/short revisions and `HEAD`, invokes the specified evaluator under `env -i`, hashes evaluator bytes into `gate_cmd_sha256`, parses `findings` and `checked_reg` from `SUMMARY`, and emits tab-separated columns `rev`, `gate_cmd_sha256`, `findings`, `checked_reg`, `rc`. Gate rc 0/1 is retained; evaluation errors or malformed/missing summaries fail closed.
2. Delivered script text:

```bash
#!/usr/bin/env bash
# Souji round 27 C1 frozen landing-gate counter; read-only receipt producer.
set -u

readonly ROOT=/home/vgpnk/Projects/shokunin/souji-shokunin
readonly FLEET_ROOT=/home/vgpnk/Projects/shokunin
readonly GATE="$ROOT/tools/souji-landing-gate.py"
readonly BASE=e78ac7c4837b81b634db4a927605a751a7f006ba

usage() { printf 'usage: %s --rev <full40> | --base\n' "$0" >&2; }
fail() { printf 'c1-counter: %s\n' "$1" >&2; exit 2; }

rev=
if [[ $# == 1 && $1 == --base ]]; then
    rev=$BASE
elif [[ $# == 2 && $1 == --rev ]]; then
    rev=$2
    [[ $rev =~ ^[0-9a-fA-F]{40}$ ]] || fail '--rev requires a full 40-hex commit id (not HEAD or an abbreviation)'
else
    usage
    exit 2
fi

[[ -f $GATE ]] || fail "missing gate: $GATE"
command -v python3 >/dev/null 2>&1 || fail 'python3 is unavailable'
command -v sha256sum >/dev/null 2>&1 || fail 'sha256sum is unavailable'

gate_cmd_sha256=$(sha256sum "$GATE") || fail 'cannot hash landing gate'
gate_cmd_sha256=${gate_cmd_sha256%% *}

set +e
output=$(env -i PATH="${PATH:-/usr/bin:/bin}" LC_ALL=C PYTHONNOUSERSITE=1 \
    python3 -B "$GATE" --root "$ROOT" --rev "$rev" --round 27 \
    --fleet-root "$FLEET_ROOT" 2>&1)
rc=$?
set -e

findings=
checked_reg=
while IFS=$'\t' read -r first second rest; do
    if [[ $first == SUMMARY ]]; then
        [[ $second =~ ^findings=([0-9]+)$ ]] || fail 'malformed SUMMARY findings field'
        findings=${BASH_REMATCH[1]}
        for field in $rest; do
            if [[ $field =~ ^checked_reg=([0-9]+)$ ]]; then
                checked_reg=${BASH_REMATCH[1]}
                break
            fi
        done
        break
    fi
done <<< "$output"
[[ -n $findings && -n $checked_reg ]] || {
    printf '%s\n' "$output" >&2
    fail 'landing gate did not emit a parseable SUMMARY findings and checked_reg'
}

(( rc <= 1 )) || { printf '%s\n' "$output" >&2; fail "landing gate evaluation failed (rc=$rc)"; }
printf 'rev\tgate_cmd_sha256\tfindings\tchecked_reg\trc\n'
printf '%s\t%s\t%s\t%s\t%d\n' "$rev" "$gate_cmd_sha256" "$findings" "$checked_reg" "$rc"
```

## Attack log
- None. Frozen predicates, targets, and case set were not changed.

## Risks and blockers
- Base and candidate runtime receipts are unobserved because executing the evaluator against the live lane tree was explicitly excluded. The parent must collect the receipts in its authorized measurement context.