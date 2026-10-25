#!/usr/bin/env bash
# souji round 26 C1 frozen counter (receipt-bound). Prints K1 and K2 of
# preregistration claim C1. Read-only. LC_ALL=C for stable output.
set -u
cd "$(dirname "$0")/../.." || exit 2
export LC_ALL=C
m=$(grep -cE '^(Insert the table below directly above|Optional same-landing correction)' SCORECARD.md)
h=$(awk '/^### Round (23|24|25) measurements/{printf "%s ", NR} END{print ""}' SCORECARD.md)
printf 'markers=%s\n' "$m"
printf 'headings=%s\n' "$h"
