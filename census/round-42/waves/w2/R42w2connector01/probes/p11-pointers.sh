#!/usr/bin/env bash
# P11 probe: every .ufo/waves path the round-42 lesson cites, tracked at the tip or not.
set -u
LANE=$1; TIP=$2
cd "$LANE" || exit 2
grep -noE '\.ufo/waves/[A-Za-z0-9_./*-]+' corpus/lessons/round-42.md | sed -E 's/[.,;:)]+$//'
for p in $(grep -oE '\.ufo/waves/[A-Za-z0-9_./*-]+' corpus/lessons/round-42.md | sed -E 's/[.,;:)]+$//' | sort -u); do
  if git cat-file -e "$TIP:$p" 2>/dev/null; then echo "TRACKED   $p"; else echo "UNTRACKED $p (check-ignore: $(git check-ignore "$p"))"; fi
done
echo "tracked files under .ufo/waves/round-42 at tip: $(git ls-files .ufo/waves/round-42 | wc -l)"
