#!/bin/bash
# HIGH-1: the include walk explores the whole depth-10 tree, one fork+exec per node, while git
# aborts at the first depth overflow (rc=128, 3 ms).  Each node's path string differs by its
# dirname spelling ("x/../a" from x/, then from x/../x/, ...), so the exact-string seen-set never
# dedupes: node count is B^depth for B attacker-chosen subdirectories.
. "$(dirname "$0")/probe-common.sh"; prep
mkdir -p "$H/bin"
printf '#!/bin/sh\nprintf x >> %s/log\nexec /usr/bin/git "$@"\n' "$H" > "$H/bin/git"; chmod +x "$H/bin/git"
names=(x y z w s t u v i j)
for B in 2 4; do
  D=$(mkfix)
  for ((k=0;k<B;k++)); do mkdir -p "$D/.git/${names[k]}"; done
  printf '[core]\n\trepositoryformatversion = 0\n[include]\n\tpath = %s/../a\n' "${names[0]}" > "$D/.git/config"
  : > "$D/.git/a"; for ((k=0;k<B;k++)); do printf '[include]\n\tpath = %s/../a\n' "${names[k]}" >> "$D/.git/a"; done
  s=$(date +%s%N); timeout -k 5 30 git --no-optional-locks -C "$D" rev-parse --show-toplevel >/dev/null 2>&1
  echo "B=$B same tree, git rev-parse: rc=$? $(( ($(date +%s%N)-s)/1000000 ))ms"
  : > "$H/log"; s=$(date +%s%N); PATH="$H/bin:$PATH" T=60 rungate > "$H/fan$B.out" 2>&1; rc=$?
  echo "B=$B B^10=${B}^10 gate: rc=$rc $(( ($(date +%s%N)-s)/1000000 ))ms scan-execs=$(wc -c < "$H/log")"
  head -2 "$H/fan$B.out" | sed 's/^/    /'
  pkill -f "$D" 2>/dev/null
done
