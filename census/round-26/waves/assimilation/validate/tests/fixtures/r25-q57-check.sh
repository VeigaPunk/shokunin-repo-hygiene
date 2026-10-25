#!/usr/bin/env bash
# r25 Q57 checker: authoritative slice tally, row-level citations, and two-file mapping pointers.
# Usage: bash tests/fixtures/r25-q57-check.sh ROOT TABLE DETAIL MAPPING SITE...
# SITE is file:line (tally quote) or file:line:ID (one class quote).
set -u
if (($# < 5)); then
  printf 'usage: %s ROOT TABLE DETAIL MAPPING SITE...\n' "$0" >&2
  exit 2
fi
root=$1 table=$2 detail=$3 mapping=$4; shift 4
fail=0
if [[ -f "$root/$mapping" ]] && grep -qF '### Quarantine-slice vocabulary' "$root/$mapping"; then
  echo "MAPPING-PRESENT $mapping"
else
  echo "MAPPING-MISSING $mapping"
  fail=1
fi
counts=$(grep -v '^#' "$root/$table" | cut -f2 | sort | uniq -c)
printf 'recount %s: ' "$table"
echo "$counts" | awk '{printf "%s%s %s", (NR>1?", ":""), $1, $2} END{print ""}'
for f in "$table" "$detail"; do
  if grep -qF "$mapping" "$root/$f"; then echo "POINTS $f -> $mapping"; else echo "NO-POINTER $f"; fail=1; fi
done
for site in "$@"; do
  IFS=: read -r file line id <<<"$site"
  text=$(awk -v n="$line" 'NR==n' "$root/$file")
  note=$(grep -F 'superseded by' "$root/$file" | grep -F "$file:$line" | grep -F "$mapping" | tail -1)
  after=${note#*recount}
  ok=1 nok=1
  if [ -n "${id:-}" ]; then
    cls=$(awk -F'\t' -v i="$id" '$1==i{print $2}' "$root/$table")
    echo "$text" | grep -qE "(^|[^[:alnum:]-])$cls([^[:alnum:]-]|$)" || ok=0
    for other in present accepted unverifiable refused; do
      [ "$other" = "$cls" ] && continue
      echo "$text" | grep -qE "(^|[^[:alnum:]-])$other([^[:alnum:]-]|$)" && ok=0
    done
    echo "$after" | grep -qE "$id[^[:alnum:]](.*[^[:alnum:]-])?$cls([^[:alnum:]-]|$)" || nok=0
  else
    while read -r n cls; do
      [ -z "$cls" ] && continue
      echo "$text" | grep -qE "(^|[^[:alnum:]])$n $cls" || ok=0
      echo "$after" | grep -qE "(^|[^[:alnum:]])$n $cls" || nok=0
    done <<<"$counts"
  fi
  if [ "$ok" = 1 ]; then echo "AGREE $site"
  elif [ -n "$note" ] && [ "$nok" = 1 ]; then echo "SUPERSEDED $site"
  else echo "STALE $site: $(echo "$text" | cut -c1-110)"; fail=1; fi
done
echo "q57=$([ "$fail" = 0 ] && echo PASS || echo FAIL)"
exit "$fail"
