#!/bin/sh
# S62ScoutSources — empirical probe of `git ls-files -v` index tags, round 62.
#
# Every fixture repo is created under the seat scratch root (S62ScoutSources passes it
# as $1); every git call names -C "$D"; `git -C "$D" rev-parse --show-toplevel` is asserted
# to equal $D before the first commit. The probe is READ-ONLY on the lane: it never touches
# the lane index, and the lane index is only READ with `git -C <lane> ls-files -v`.
#
# Exit status: 0 when every observed tag letter matches the expected letter, 1 otherwise.

set -u
S=${1:?scratch root required}
mkdir -p "$S"
rc_all=0

note() { printf '%s\n' "$*"; }

run() {  # run <label> <expected-letter> <path> <D>
  _label=$1; _exp=$2; _path=$3; _D=$4
  _out=$(git -C "$_D" ls-files -v -- "$_path")
  _rc=$?
  _got=$(printf '%s' "$_out" | cut -c1)
  printf '%s: ls-files -v -- %s -> [%s] rc=%s expected=[%s]\n' "$_label" "$_path" "$_got" "$_rc" "$_exp"
  if [ "$_rc" -ne 0 ] || [ "$_got" != "$_exp" ]; then rc_all=1; fi
}

note "=== git version ==="
git --version
note ""

note "=== fixture A: one skip-worktree path, one assume-unchanged path ==="
D=$(mktemp -d -p "$S")
git -C "$D" init -q
mkdir -p "$D/tools"
printf 'print("ok")\n' > "$D/tools/counter.py"
printf '#!/bin/sh\necho inst\n' > "$D/tools/instr.sh"
git -C "$D" add -A
TOP=$(git -C "$D" rev-parse --show-toplevel)
if [ "$TOP" != "$D" ]; then echo "FATAL: toplevel $TOP != $D"; exit 1; fi
git -C "$D" -c user.name=probe -c user.email=probe@example.invalid commit -qm base
note "fixture=$D (toplevel asserted == D)"
note "-- baseline (no flags) --"
git -C "$D" ls-files -v; note "rc=$?"
git -C "$D" update-index --skip-worktree tools/counter.py
git -C "$D" update-index --assume-unchanged tools/instr.sh
note "-- after update-index --skip-worktree / --assume-unchanged --"
git -C "$D" ls-files -v; note "rc=$?"
run "skip-worktree" "S" "tools/counter.py" "$D"
run "assume-unchanged" "h" "tools/instr.sh" "$D"
note "-- ls-files -t (no -v: lowercase marking absent) --"
git -C "$D" ls-files -t; note "rc=$?"
note "-- ls-files -v -z (record layout: tag byte, space, path, NUL) --"
git -C "$D" ls-files -v -z | od -c | head -4; note "rc=$?"
note "-- git status --porcelain with forged worktree bytes --"
printf 'print("FORGED")\n' > "$D/tools/counter.py"
printf '#!/bin/sh\necho FORGED\n' > "$D/tools/instr.sh"
git -C "$D" status --porcelain; note "rc=$? (empty output above = porcelain stays silent)"
note "-- git status --porcelain after the flags are removed --"
git -C "$D" update-index --no-skip-worktree tools/counter.py
git -C "$D" update-index --no-assume-unchanged tools/instr.sh
git -C "$D" status --porcelain; note "rc=$?"
rm -rf "$D"

note ""
note "=== fixture B: both bits set on one path ==="
D=$(mktemp -d -p "$S")
git -C "$D" init -q
mkdir -p "$D/tools"
printf 'a\n' > "$D/tools/both.py"
git -C "$D" add -A
TOP=$(git -C "$D" rev-parse --show-toplevel)
if [ "$TOP" != "$D" ]; then echo "FATAL: toplevel $TOP != $D"; exit 1; fi
git -C "$D" -c user.name=probe -c user.email=probe@example.invalid commit -qm base
git -C "$D" update-index --skip-worktree tools/both.py
git -C "$D" update-index --assume-unchanged tools/both.py
git -C "$D" ls-files -v; note "rc=$? (lowercase s = skip-worktree letter lowercased by the -v rule)"
git -C "$D" ls-files -t; note "rc=$? (uppercase S without -v)"
rm -rf "$D"

note ""
note "=== fixture C: unmerged path (tag M) and non-flag tags ==="
D=$(mktemp -d -p "$S")
git -C "$D" init -q
mkdir -p "$D/tools"
printf 'a\n' > "$D/tools/mer.py"
git -C "$D" add -A
TOP=$(git -C "$D" rev-parse --show-toplevel)
if [ "$TOP" != "$D" ]; then echo "FATAL: toplevel $TOP != $D"; exit 1; fi
git -C "$D" -c user.name=probe -c user.email=probe@example.invalid commit -qm base
BASE_BRANCH=$(git -C "$D" rev-parse --abbrev-ref HEAD)
git -C "$D" checkout -qb br
printf 'c\n' > "$D/tools/mer.py"
git -C "$D" -c user.name=probe -c user.email=probe@example.invalid commit -qam br
git -C "$D" checkout -q "$BASE_BRANCH"
printf 'd\n' > "$D/tools/mer.py"
git -C "$D" -c user.name=probe -c user.email=probe@example.invalid commit -qam "$BASE_BRANCH"
git -C "$D" merge br >/dev/null 2>&1; note "merge rc=$? (1 = conflict produced)"
note "-- ls-files -v on a conflicted index --"
git -C "$D" ls-files -v; note "rc=$?"
rm -rf "$D"

note ""
note "=== fixture D: dirty worktree, NO index flags (tags stay H) ==="
D=$(mktemp -d -p "$S")
git -C "$D" init -q
mkdir -p "$D/tools"
printf 'a\n' > "$D/tools/plain.py"
printf 'b\n' > "$D/tools/other.py"
git -C "$D" add -A
TOP=$(git -C "$D" rev-parse --show-toplevel)
if [ "$TOP" != "$D" ]; then echo "FATAL: toplevel $TOP != $D"; exit 1; fi
git -C "$D" -c user.name=probe -c user.email=probe@example.invalid commit -qm base
printf 'MODIFIED\n' > "$D/tools/plain.py"
rm "$D/tools/other.py"
note "-- ls-files -v (no flags set, worktree dirty) --"
git -C "$D" ls-files -v; note "rc=$?"
note "-- git status --porcelain (non-empty = the base writer's dirty check still fires) --"
git -C "$D" status --porcelain; note "rc=$?"
rm -rf "$D"

note ""
note "=== fixture E: ls-files -v -z failure mode outside a repository ==="
git -C "$S" ls-files -v -z >/dev/null 2>&1; note "rc=$? (nonzero = the candidate's refusal path for a failed read)"

note ""
note "=== LANE index read (read-only): tag histogram at lane base ==="
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
git -C "$LANE" ls-files -v | wc -l; note "rc=$? (entries)"
git -C "$LANE" ls-files -v | cut -c1 | sort | uniq -c; note "rc=$? (tag histogram)"

note ""
if [ "$rc_all" -eq 0 ]; then note "PROBE: all observed tag letters matched expectations"; else note "PROBE: a mismatch was observed"; fi
exit $rc_all
