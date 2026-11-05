#!/usr/bin/env bash
# usage: conceal.sh TOOL.py TAG  -- runs concealment rows A D E F and supplementary TP on fresh fixture repos
set -u
unset GIT_DIR GIT_WORK_TREE
TOOL="$1"; TAG="$2"
S=/fast/scratch/hyaku/souji-r62/S62MutDirtyCase
W="$S/conc/$TAG"
rm -rf -- "$W"; mkdir -p "$W"
mk_repo() {
  local R="$1"
  mkdir -p "$R" && git -C "$R" init -q || { echo "INIT-FAIL"; exit 70; }
  local top; top="$(git -C "$R" rev-parse --show-toplevel)"
  [ "$(realpath "$top")" = "$(realpath "$R")" ] || { echo "TOPLEVEL-FAIL $top"; exit 70; }
  mkdir -p "$R/tools"
  printf '#!/bin/sh\necho instrument-ok\n' > "$R/tools/instr.sh"
  printf 'print("counter-honest")\n' > "$R/tools/counter.py"
  printf 'notes v1\n' > "$R/notes.md"
  git -C "$R" add -A
  git -C "$R" -c user.name="S62 Probe" -c user.email="s62-probe@invalid" commit -q -m "probe base"
}
row() {
  local name="$1" R="$W/$1/repo" O="$W/$1"
  mkdir -p "$O"
  mk_repo "$R"
  case "$name" in
    A)  : ;;                                   # honest clean
    D)  git -C "$R" update-index --skip-worktree tools/counter.py
        printf 'print("FORGED")\n' > "$R/tools/counter.py" ;;
    E)  git -C "$R" update-index --assume-unchanged tools/counter.py
        printf 'print("FORGED")\n' > "$R/tools/counter.py" ;;
    F)  git -C "$R" update-index --skip-worktree tools/counter.py ;;   # bytes unchanged
    TP) printf 'notes v2\n' >> "$R/notes.md" ;;   # supplementary: visible tracked edit, no flags
  esac
  local rev; rev="$(git -C "$R" rev-parse HEAD)"
  local flags=()
  [ "$name" = "TP" ] && flags=()   # no --allow-dirty: must refuse
  python3 -B "$TOOL" --root "$R" --rev "$rev" --instrument tools/instr.sh \
      --out "$O/receipt.txt" --allow-outside --command "echo ok" > "$O/tool.log" 2>&1
  local rc=$?
  local v="REFUSE"; [ "$rc" = 0 ] && [ -f "$O/receipt.txt" ] && v="ACCEPT"
  echo "TAG=$TAG ROW=$name rc=$rc verdict=$v reason=$(tail -n 1 "$O/tool.log" | tr -d '\n')"
}
for r in A D E F TP; do row "$r"; done
