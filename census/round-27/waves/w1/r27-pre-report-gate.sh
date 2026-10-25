#!/usr/bin/env bash
# r27-pre-report-gate.sh — C3 selftest harness for tools/souji-pre-report-gate.sh
# (round 27, wave 1 DRAFT; L1 installs as tests/fixtures/r27-pre-report-gate.sh).
#
# Runs the gate under test against four isolated worlds under
# /var/tmp/souji-r27-ExecFixtureC3Tests (each: `git init` repo, local bare
# remote, committed report + prereg), plus a FALSE-GREEN always-pass control.
#
# Frozen gate interface under test:
#   bash tools/souji-pre-report-gate.sh --lane <abs-lane> --branch <branch> \
#        --report <abs-report> [--prereg <abs-file>]
#   check lines: check-<name>=PASS|FAIL|SKIP for name in tip report shonen
#                clean prereg; exit 0 iff all PASS, 1 if any FAIL, 2 usage.
#
# Cases (assert rc and the failing check(s)):
#   1 clean-pass        tip==remote, report with `## SHONEN`, clean tree,
#                       prereg present -> rc 0, all five checks PASS
#   2 remote-mismatch   local tip ahead of origin -> rc 1, check-tip=FAIL
#   3 missing-SHONEN    report exists, no heading -> rc 1, check-shonen=FAIL
#   4 dirty-tree        untracked file in worktree -> rc 1, check-clean=FAIL
#   control FALSE-GREEN always-pass stub tool run on a world whose truth is red
#                       (dirty); the harness detects the false green and
#                       rejects it.
#
# Tool lookup: $SOUJI_PRE_REPORT_GATE (absolute) if set; else the lane's
# tools/souji-pre-report-gate.sh (lane root = two dirs above this script when
# installed under tests/fixtures/, else $SOUJI_LANE_ROOT or $PWD).
#
# Last line on success: `cases=4 pass=4 control=FALSE-GREEN-REJECTED`; rc 0.
# Any deviation prints a FAIL line and exits 1.
#
# Hermetic: fixed scratch root, GIT_CONFIG_GLOBAL=/dev/null,
# GIT_CONFIG_NOSYSTEM=1, GIT_TERMINAL_PROMPT=0, no network, no wall-clock
# dependence, EXIT trap removes every world.
set -u

export LC_ALL=C
WORLD_ROOT=/var/tmp/souji-r27-ExecFixtureC3Tests
WORLDS='case1 case2 case3 case4 control'

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 2
case "$SCRIPT_DIR" in
  */tests/fixtures) LANE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd) ;;
  *) LANE_ROOT=${SOUJI_LANE_ROOT:-$(pwd)} ;;
esac
TOOL=${SOUJI_PRE_REPORT_GATE:-"$LANE_ROOT/tools/souji-pre-report-gate.sh"}
[ -f "$TOOL" ] || { printf 'FATAL tool-missing %s\n' "$TOOL" >&2; exit 2; }

export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
export GIT_TERMINAL_PROMPT=0
export HOME="$WORLD_ROOT/home"
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE
mkdir -p "$HOME"

FAILED=0

cleanup() {
  local w
  for w in $WORLDS; do rm -rf "$WORLD_ROOT/$w"; done
}
trap cleanup EXIT

mkworld() { # mkworld <dir>; sets REPO
  local d=$1
  REPO="$d/repo"
  rm -rf "$d" && mkdir -p "$d/repo" "$d/remote.git"
  git init -q -b master "$REPO"
  git init -q --bare "$d/remote.git"
  git -C "$REPO" remote add origin "$d/remote.git"
  git -C "$REPO" config user.name souji-fixture
  git -C "$REPO" config user.email fixture@shokunin.local
  git -C "$REPO" config commit.gpgsign false
  local tl
  tl=$(git -C "$REPO" rev-parse --show-toplevel) || return 1
  [ "$tl" = "$REPO" ]
}

write_report() { # write_report <world> <yes|no>  (no = without `## SHONEN`)
  local f="$1/repo/report.md"
  {
    printf '# Souji round report (fixture)\n\n'
    if [ "$2" = yes ]; then
      printf '## SHONEN\n- [ ] box one\n- [ ] box two\n'
    fi
    printf '\nEvidence: none.\n'
  } > "$f"
}

write_prereg() {
  local dir="$1/repo/.ufo/waves/round-27"
  mkdir -p "$dir"
  printf '# Round 27 preregistration (fixture)\n' > "$dir/preregistration.txt"
}

commit_push() {
  git -C "$REPO" add -A
  git -C "$REPO" commit -q -m 'fixture baseline'
  git -C "$REPO" push -q origin master
}

run_gate() { # run_gate <tool> <world>; sets GATE_OUT, GATE_RC
  local tool=$1 world=$2
  GATE_OUT=$(bash "$tool" --lane "$world/repo" --branch master \
    --report "$world/repo/report.md" \
    --prereg "$world/repo/.ufo/waves/round-27/preregistration.txt" 2>&1)
  GATE_RC=$?
}

status_of() { # status_of <check-name>
  printf '%s\n' "$GATE_OUT" | sed -nE "s/^check-$1=(PASS|FAIL|SKIP)$/\1/p" | head -n 1
}

fail_count() {
  printf '%s\n' "$GATE_OUT" | grep -cE '^check-[A-Za-z0-9_-]+=FAIL$' || true
}

assert_case() { # assert_case <case> <desc> <want-rc> [want-fail-checks...]
  local name=$1 desc=$2 want_rc=$3 bad=0
  shift 3
  if [ "$GATE_RC" -ne "$want_rc" ]; then
    printf 'case=%s %s FAIL rc=%s want=%s\n' "$name" "$desc" "$GATE_RC" "$want_rc"
    bad=1
  fi
  local c s
  for c in "$@"; do
    s=$(status_of "$c")
    if [ "$s" != FAIL ]; then
      printf 'case=%s %s FAIL check-%s=%s want=FAIL\n' "$name" "$desc" "$c" "${s:-missing}"
      bad=1
    fi
  done
  local nf
  nf=$(fail_count)
  if [ "$nf" -ne "$#" ]; then
    printf 'case=%s %s FAIL fail-check-count=%s want=%s\n' "$name" "$desc" "$nf" "$#"
    bad=1
  fi
  if [ "$bad" -eq 0 ]; then
    printf 'case=%s %s PASS\n' "$name" "$desc"
  else
    FAILED=1
  fi
}

# case 1 — clean pass (tip==remote, report with `## SHONEN`, clean tree,
# prereg present)
mkworld "$WORLD_ROOT/case1" || { printf 'FATAL world-setup case1\n' >&2; exit 2; }
write_report "$WORLD_ROOT/case1" yes
write_prereg "$WORLD_ROOT/case1"
commit_push
run_gate "$TOOL" "$WORLD_ROOT/case1"
printf '%s\n' "$GATE_OUT"
for c in tip report shonen clean prereg; do
  s=$(status_of "$c")
  if [ "$s" != PASS ]; then
    printf 'case=1 clean-pass FAIL check-%s=%s want=PASS\n' "$c" "${s:-missing}"
    FAILED=1
  fi
done
assert_case 1 clean-pass 0

# case 2 — remote-mismatch (local committed tip ahead of origin)
mkworld "$WORLD_ROOT/case2" || { printf 'FATAL world-setup case2\n' >&2; exit 2; }
write_report "$WORLD_ROOT/case2" yes
write_prereg "$WORLD_ROOT/case2"
commit_push
printf '\nTrailing note (unpushed).\n' >> "$REPO/report.md"
git -C "$REPO" add -A
git -C "$REPO" commit -q -m 'fixture unpushed tip'
run_gate "$TOOL" "$WORLD_ROOT/case2"
printf '%s\n' "$GATE_OUT"
assert_case 2 remote-mismatch 1 tip

# case 3 — missing-SHONEN (report exists, no `## SHONEN` heading)
mkworld "$WORLD_ROOT/case3" || { printf 'FATAL world-setup case3\n' >&2; exit 2; }
write_report "$WORLD_ROOT/case3" no
write_prereg "$WORLD_ROOT/case3"
commit_push
run_gate "$TOOL" "$WORLD_ROOT/case3"
printf '%s\n' "$GATE_OUT"
assert_case 3 missing-SHONEN 1 shonen

# case 4 — dirty-tree (untracked file in worktree)
mkworld "$WORLD_ROOT/case4" || { printf 'FATAL world-setup case4\n' >&2; exit 2; }
write_report "$WORLD_ROOT/case4" yes
write_prereg "$WORLD_ROOT/case4"
commit_push
printf 'leftover\n' > "$REPO/leftover.txt"
run_gate "$TOOL" "$WORLD_ROOT/case4"
printf '%s\n' "$GATE_OUT"
assert_case 4 dirty-tree 1 clean

# control — FALSE-GREEN: an always-pass stub tool must be rejected.  The
# control world's truth is red (dirty tree).  First prove that truth with the
# real tool; then run the stub: a green result there is a false green and the
# harness must reject (fail) it.
mkworld "$WORLD_ROOT/control" || { printf 'FATAL world-setup control\n' >&2; exit 2; }
write_report "$WORLD_ROOT/control" yes
write_prereg "$WORLD_ROOT/control"
commit_push
printf 'leftover\n' > "$REPO/leftover.txt"
run_gate "$TOOL" "$WORLD_ROOT/control"
if [ "$GATE_RC" -ne 1 ] || [ "$(status_of clean)" != FAIL ]; then
  printf 'FAIL control world-not-red rc=%s clean=%s\n' "$GATE_RC" "$(status_of clean)"
  FAILED=1
else
  stub="$WORLD_ROOT/control/stub-gate.sh"
  printf '%s\n' \
    '#!/usr/bin/env bash' \
    'printf "check-tip=PASS\ncheck-report=PASS\ncheck-shonen=PASS\ncheck-clean=PASS\ncheck-prereg=PASS\n"' \
    'exit 0' > "$stub"
  run_gate "$stub" "$WORLD_ROOT/control"
  printf '%s\n' "$GATE_OUT"
  if [ "$GATE_RC" -eq 0 ] && [ "$(status_of clean)" = PASS ]; then
    printf 'control FALSE-GREEN-REJECTED\n'
  else
    printf 'FAIL control stub-not-green rc=%s\n' "$GATE_RC"
    FAILED=1
  fi
fi

if [ "$FAILED" -eq 0 ]; then
  printf 'cases=4 pass=4 control=FALSE-GREEN-REJECTED\n'
fi
exit "$FAILED"
