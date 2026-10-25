#!/usr/bin/env bash
# souji round 26 C2 frozen counter (receipt-bound). Prints K1 (grounded-F1
# knowledge entries) and K3's registry row count. Read-only.
set -u
cd "$(dirname "$0")/../.." || exit 2
export LC_ALL=C
g=$(grep -l '^ground: F1' corpus/knowledge/*.md 2>/dev/null | wc -l)
r=$(grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md)
printf 'grounded_f1=%s\n' "$g"
printf 'registry_rows=%s\n' "$r"
