#!/usr/bin/env bash
# Souji round 27 C1 frozen landing-gate counter; read-only receipt producer.
set -u

readonly ROOT=/home/vgpnk/Projects/shokunin/souji-shokunin
readonly FLEET_ROOT=/home/vgpnk/Projects/shokunin
readonly GATE="$ROOT/tools/souji-landing-gate.py"
readonly BASE=e78ac7c4837b81b634db4a927605a751a7f006ba

usage() { printf 'usage: %s --rev <full40> | --base\n' "$0" >&2; }
fail() { printf 'c1-counter: %s\n' "$1" >&2; exit 2; }

mode=rev
rev=
if [[ $# == 1 && $1 == --base ]]; then
    mode=base
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

# Hash the committed evaluator bytes, not the variable revision argument.
gate_cmd_sha256=$(sha256sum "$GATE") || fail 'cannot hash landing gate'
gate_cmd_sha256=${gate_cmd_sha256%% *}

# Preserve only the executable search path and deterministic locale. The gate
# itself uses read-only git plumbing; no ambient repository selectors survive.
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

# The gate's documented 0/1 results are receipts; 2 means evaluation failed.
(( rc <= 1 )) || { printf '%s\n' "$output" >&2; fail "landing gate evaluation failed (rc=$rc)"; }
printf 'rev\tgate_cmd_sha256\tfindings\tchecked_reg\trc\n'
printf '%s\t%s\t%s\t%s\t%d\n' "$rev" "$gate_cmd_sha256" "$findings" "$checked_reg" "$rc"
