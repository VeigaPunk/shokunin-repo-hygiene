#!/usr/bin/env bash
# verify.sh -- re-derive and re-verify every artifact of S66ScoutSources.
#
#   1. re-run recipe.py on the raw captures -> the .txt files must be
#      byte-identical to the delivered ones (deterministic recipe);
#   2. re-run locate_quotes.py --verify -> every quotes.tsv row is
#      re-sliced out of the .txt and byte-compared;
#   3. re-run absences.py -> the absence table is regenerated;
#   4. sha256 of every delivered file is printed.
#
# No network access is required or performed.
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1. deterministic re-strip =="
for pair in "git-environment.html git-environment.txt" "git-config.html git-config.txt"; do
  set -- $pair
  cp "$2" "$2.orig"
  python3 recipe.py "$1" "$2" 2>/dev/null
  if cmp -s "$2" "$2.orig"; then
    echo "  OK  $2 is byte-identical when re-stripped from $1"
  else
    echo "  FAIL $2 differs on re-strip"; cmp "$2" "$2.orig" || true; exit 1
  fi
  rm -f "$2.orig"
done

echo "== 2. quotes.tsv re-slice verification =="
python3 locate_quotes.py --verify

echo "== 3. absence table =="
python3 absences.py 2>&1 | tail -1

echo "== 4. sha256 of delivered files =="
sha256sum recipe.py locate_quotes.py absences.py verify.sh manifest.json \
          git-environment.html git-environment.txt git-config.html git-config.txt \
          quotes.tsv absences.tsv upstream-evidence.txt
