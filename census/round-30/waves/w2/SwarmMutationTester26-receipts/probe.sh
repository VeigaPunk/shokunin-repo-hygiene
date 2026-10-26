#!/usr/bin/env bash
# Mechanism probe for M5/M6 survivors (seat SwarmMutationTester26, scratch only).
# A: does `git gc --prune=now` pack the loose keep refs, making the age gate inert
#    so that DEFAULT-threshold `jj util gc` removes them (explaining M5's survival)?
# B: without git gc (refs loose), does default `jj util gc` keep them (control step 7)?
# C: do these repositories contain any refs outside refs/jj/keep/* (explaining M6)?
set -u
S=/fast/scratch/hyaku/souji-r30/MutateJjFixture
export TMPDIR=$S/tmp
mkdir -p "$TMPDIR"
B=$(mktemp -d "$TMPDIR/probe.XXXXXX") || exit 9
trap 'rm -rf "$B"' EXIT
CFG=(--color=never --config ui.paginate=never --config user.name=probe --config user.email=probe@example.invalid)
D=""

mk() {
  D=$1; mkdir -p "$D"
  jj "${CFG[@]}" git init --colocate "$D" >/dev/null 2>&1 || return 1
  printf 'a\n' >"$D/a.txt"; ( cd "$D" && jj -R "$D" "${CFG[@]}" commit -m A a.txt ) >/dev/null 2>&1 || return 1
  printf 'b\n' >"$D/b.txt"; ( cd "$D" && jj -R "$D" "${CFG[@]}" commit -m B b.txt ) >/dev/null 2>&1 || return 1
  TGT=$( ( cd "$D" && jj -R "$D" "${CFG[@]}" log --no-graph -r '@-' -T 'commit_id' ) )
  ( cd "$D" && jj -R "$D" "${CFG[@]}" abandon '@-' ) >/dev/null 2>&1 || return 1
}
G() { git -C "$D" -c maintenance.auto=false -c gc.auto=0 "$@"; }
state() {
  echo "  keep=$(G for-each-ref --format='%(refname)' 'refs/jj/keep/*' | wc -l | tr -d ' ')" \
       "all=$(G for-each-ref --format='%(refname)' | wc -l | tr -d ' ')" \
       "target_keep=$(G for-each-ref --format='%(refname)' 'refs/jj/keep/*' | grep -q -- "$TGT" && echo yes || echo no)" \
       "loose_files=$(ls "$D/.git/refs/jj/keep" 2>/dev/null | wc -l | tr -d ' ')" \
       "packed_lines=$(grep -c 'refs/jj/keep' "$D/.git/packed-refs" 2>/dev/null || true)"
}

echo "== probe B: abandon, NO git gc, then default jj util gc =="
mk "$B/nogg" || { echo "mk failed"; exit 1; }
echo "  target=$TGT"; state
JJ() { ( cd "$D" && jj -R "$D" "${CFG[@]}" "$@" ); }
JJ util gc >/dev/null 2>&1
echo "  after default gc:"; state

echo "== probe A: abandon, git gc --prune=now, then default jj util gc =="
mk "$B/gg" || { echo "mk failed"; exit 1; }
echo "  target=$TGT"; state
G gc --prune=now
echo "  after git gc --prune=now:"; state
JJ() { ( cd "$D" && jj -R "$D" "${CFG[@]}" "$@" ); }
JJ util gc >/dev/null 2>&1
echo "  after default gc:"; state

echo "== probe C: full ref list of probe A repo (post git gc, post default gc) =="
D=$B/gg
G for-each-ref --format='%(refname)' | sort | sed 's/^/  /'
