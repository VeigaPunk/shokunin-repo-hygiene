#!/usr/bin/env bash
# P8 probe: the adding commit of each path a frozen text names, and the control-receipt count.
set -u
cd "$1" || exit 2
for f in census/round-42/c1-counter.py census/round-42/c1-items.tsv census/round-42/c2-counter.py census/round-42/c2-cases.tsv \
         census/round-42/c3-counter.py census/round-42/c3-mutants.tsv census/round-42/r1-counter.py census/round-42/preregistration.txt \
         census/round-42/records/census-before.txt census/round-42/controls/c1-control.txt census/round-42/controls/c2-control.txt \
         census/round-42/controls/c3-control.txt census/round-42/controls/r1-control.txt; do
  echo "$f added-at=$(git log --diff-filter=A --format=%h -- "$f" | tail -1)"
done
echo "prereg:5 instruments commit b7408095543579ac71b33ecf7b80b0cb8ef45036 resolves to: $(git log -1 --format='%h %s' b7408095543579ac71b33ecf7b80b0cb8ef45036)"
echo "control receipts present (prereg says five): $(ls census/round-42/controls/ | grep -c 'control.txt')"
