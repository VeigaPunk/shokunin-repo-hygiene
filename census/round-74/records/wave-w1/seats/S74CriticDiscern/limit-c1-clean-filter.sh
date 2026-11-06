#!/usr/bin/env bash
# S74CriticDiscern — empirical test of the r74 C1 named limit: "the gate trusts `git hash-object` to apply
# the conversion `git status` applies (S316) and so inherits a lying clean filter (the receipt writer
# refuses those; the gate does not)".
#
# One fixture family: a clone where `*.txt filter=lie` is committed and the clean program always emits the
# committed bytes of a.txt. Two arms change a.txt's worktree bytes:
#   A  same worktree size as the index records  -> status is empty, the gate's re-hash applies the filter,
#      the filtered digest equals the index object id, check-clean=PASS although worktree != blob.
#   B  different worktree size                  -> status is dirty and the gate fails before the re-hash
#      (so the limit needs the size the status content-compare sees; recorded, not claimed).
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
SCRATCH=/fast/scratch/hyaku/souji-r74/S74CriticDiscern
D=$(mktemp -d -p "$SCRATCH" fx.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] || exit 1
trap 'rm -rf -- "$D"' EXIT
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@invalid
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@invalid
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 LC_ALL=C
fixture() {  # $1 = row dir
  local R=$1
  git -C "$R" init -q --bare -b master "$R/origin.git" || return 1
  git -C "$R" init -q -b master "$R/clone" || return 1
  [ "$(git -C "$R/clone" rev-parse --show-toplevel)" = "$(realpath "$R/clone")" ] || return 1
  printf 'alpha v1\n' > "$R/clone/a.txt"
  printf '*.txt filter=lie\n' > "$R/clone/.gitattributes"
  printf '#!/bin/sh\ncat >/dev/null\nprintf "alpha v1\\n"\n' > "$R/lie.sh"
  chmod +x "$R/lie.sh"
  git -C "$R/clone" config filter.lie.clean "$R/lie.sh"
  git -C "$R/clone" add -A || return 1
  git -C "$R/clone" commit -q -m seed || return 1
  git -C "$R/clone" remote add origin "$R/origin.git" || return 1
  git -C "$R/clone" push -q origin master || return 1
  printf 'report\n\n## SHONEN\n\n- [ ] box\n' > "$R/report.md"
  printf 'frozen\n' > "$R/prereg.txt"
}
gate() { bash "$LANE/tools/souji-pre-report-gate.sh" --lane "$1/clone" --branch master \
               --report "$1/report.md" --prereg "$1/prereg.txt" 2>&1; }
run_arm() {  # $1 = label, $2 = worktree bytes
  local L=$1 R=$D/$1
  mkdir -p "$R" || return 1
  fixture "$R" || return 1
  printf '%s' "$2" > "$R/clone/a.txt"
  local out rc
  out=$(gate "$R"); rc=$?
  echo "$L worktree_size=$(stat -c%s "$R/clone/a.txt") status=[$(git -C "$R/clone" status --porcelain=v1 --untracked-files=all | tr '\n' ';')]"
  echo "$L filtered=$(printf 'a.txt\n' | git -C "$R/clone" hash-object --stdin-paths) index=$(git -C "$R/clone" rev-parse :a.txt)"
  echo "$L $(echo "$out" | grep -E '^check-clean=') rc=$rc worktree_equals_blob=$(cmp -s <(git -C "$R/clone" cat-file blob :a.txt) "$R/clone/a.txt" && echo yes || echo no)"
  echo "$L verdict=$([ "$(echo "$out" | sed -n 's/^check-clean=//p')" = PASS ] && [ "$rc" = 0 ] && ! cmp -s <(git -C "$R/clone" cat-file blob :a.txt) "$R/clone/a.txt" && echo PASSES-DIFFERING-WORKTREE || echo caught)"
}
run_arm armA 'EVILBYTE
'
run_arm armB 'EVIL BYTES, NOT THE COMMITTED BYTES
'
