#!/usr/bin/env bash
# r12-maintenance-guard.sh — executable guard for the claim that a plain
# `git commit` can prune git worktree metadata via auto-maintenance.
#
# HYPOTHESIS: CONFIRMED. Observed on: git 2.55.0 (Arch linux x64, 2026-10-19).
#   A plain `git commit` runs `git maintenance run --auto`, whose worktree-prune
#   task executes `git worktree prune --expire 3.months.ago`. A registration
#   whose working directory is gone AND whose .git/worktrees/<id>/index mtime
#   is older than 3 months is removed: `git worktree list` goes 2 -> 1, with no
#   souji receipt.
#   - `-c maintenance.auto=false` prevents it (2 -> 2).
#   - `git worktree lock` prevents it (2 -> 2).
#   - A fresh registration (index younger than 3 months) is protected by the
#     expiry (2 -> 2), so the task did run in that case.
#   - The expiry clock is the registration's `index` mtime, not `gitdir`:
#     aging only `gitdir` does NOT prune [measured; see results file].
#   - The pruned worktree HEAD commit is NOT in any ref or reflog afterwards
#     (`for-each-ref --contains` empty, `reflog --all` empty); the object
#     survives as unreachable until gc.pruneExpire collects it
#     [measured; see results file].
#   case=plain-commit-default reproduces this with DEFAULT config, i.e. with
#   maintenance.autoDetach unset so auto-maintenance detaches into the
#   background; the case polls up to 30 s for the prune. Every other case uses
#   `-c maintenance.autoDetach=false` to make the same mechanism synchronous.
#
# The expected `after` value of every case below is that OBSERVED truth, not a
# desired outcome: case=plain-commit-* expects 1 (the hazard), the controls
# expect 2. If a future git changes these counts the script exits 1; re-run the
# probe and amend this header instead of silently re-baselining.
#
# GATE INTERFACE (PROTOCOL Gate standard):
#   0 = clean: every case matches (git_version line + one line per case)
#   1 = failed: at least one case verdict=FAIL
#   2 = could-not-evaluate: git missing, mktemp failure, or any setup command
#       error (ERR trap)
# `--selftest` runs exactly the same isolated-fixture self-test and then
# asserts the emitted `id=` set equals the pinned SELFTEST_EXPECTED_IDS list
# committed below AND that every verdict is PASS; it prints as its last line
# `selftest=PASS ids=<n>/<n>` or
# `selftest=FAIL ids=<got>/<want> missing=[...] extra=[...] failed_verdicts=<n>`
# and exits 1 on mismatch (0 when both the cases and the id assertion hold).
#
# Output: first line `git_version=<git --version>`; then one line per case
#   id=SOUJI-R12-MAINT-<case> case=<case> before=<n> after=<n> expect=<n> verdict=PASS|FAIL
# PASS requires before==2 exactly AND after==expect; anything else is FAIL.
#
# Hermetic: hard-coded scratch root /var/tmp/souji-r12-maintenance.XXXXXX
# (TMPDIR deliberately ignored), GIT_CONFIG_GLOBAL=/dev/null,
# GIT_CONFIG_NOSYSTEM=1, no network, trap cleanup, no live repo touched.
set -euo pipefail
shopt -s inherit_errexit

usage() { printf 'usage: %s [--selftest]\n' "$0" >&2; exit 2; }
die2() { printf 'id=SOUJI-R12-MAINT-SETUP error=%s\n' "$*" >&2; exit 2; }

command -v git >/dev/null 2>&1 || die2 "git not found"
GIT_VERSION="$(git --version)"
printf 'git_version=%s\n' "$GIT_VERSION"

selftest=0
if (($# > 1)); then usage; fi
case "${1:-}" in
  "") : ;;
  --selftest) selftest=1 ;;
  *) usage ;;
esac

WORK="$(mktemp -d /var/tmp/souji-r12-maintenance.XXXXXX)" ||
  die2 "mktemp failed under /var/tmp"
rc=0
trap 'rc=$?; rm -rf "${WORK:?}"; exit "$rc"' EXIT
trap 'rc=$?; printf "id=SOUJI-R12-MAINT-SETUP error=unexpected-failure rc=%s\n" "$rc" >&2; exit 2' ERR

export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
export GIT_TERMINAL_PROMPT=0
export HOME="$WORK/home"
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE
mkdir -p "$HOME"

GIT_BASE=(
  git
  -c user.name=r12-guard
  -c user.email=guard@example.invalid
  -c init.defaultBranch=master
  -c commit.gpgsign=false
  -c advice.detachedHead=false
)
# Foreground variant: used for all setup and for every case but the
# default-config one, so auto-maintenance is synchronous and observable.
GIT_FG=("${GIT_BASE[@]}" -c maintenance.autoDetach=false)

g() { # g <repo> <git args...>   (foreground auto-maintenance)
  local repo=$1
  shift
  "${GIT_FG[@]}" -C "$repo" "$@"
}

count_worktrees() { # count "worktree " records, without wc/grep
  local out n=0 line
  out="$(g "$1" worktree list --porcelain)"
  while IFS= read -r line; do
    case "$line" in
      'worktree '*) n=$((n + 1)) ;;
    esac
  done <<<"$out"
  printf '%s\n' "$n"
}

REPO=""
new_repo_with_removed_worktree() { # <name>; sets REPO
  local name=$1 wt
  REPO="$WORK/repo-$name"
  wt="$WORK/wt-$name"
  mkdir -p "$REPO"
  g "$REPO" init -q .
  printf 'base\n' >"$REPO/base.txt"
  g "$REPO" add base.txt
  g "$REPO" commit -qm base
  g "$REPO" worktree add -q --detach "$wt" HEAD
  printf 'detached\n' >"$wt/detached.txt"
  g "$wt" add detached.txt
  g "$wt" commit -qm detached
  rm -rf "${wt:?}"
}

FAILED=0

# Pinned expected finding ids — asserted by --selftest (committed contract).
SELFTEST_EXPECTED_IDS=(
  SOUJI-R12-MAINT-plain-commit-sync
  SOUJI-R12-MAINT-plain-commit-default
  SOUJI-R12-MAINT-auto-off
  SOUJI-R12-MAINT-locked
  SOUJI-R12-MAINT-fresh
  SOUJI-R12-MAINT-maintenance-auto
)
EMITTED_IDS=()

run_case() { # run_case <name> <expect> <mode: sync|default|auto-off|locked|fresh|direct>
  local name=$1 expect=$2 mode=$3 repo before after verdict i id
  new_repo_with_removed_worktree "$name"
  repo="$REPO"
  if [[ "$mode" != "fresh" ]]; then
    touch -d '4 months ago' "$repo/.git/worktrees/wt-$name/index"
  fi
  if [[ "$mode" == "locked" ]]; then
    g "$repo" worktree lock --reason r12-guard "$WORK/wt-$name"
  fi

  before="$(count_worktrees "$repo")"
  case "$mode" in
    default)
      # DEFAULT config: maintenance.autoDetach unset -> background child.
      "${GIT_BASE[@]}" -C "$repo" commit -qm "after-$name" --allow-empty
      ;;
    auto-off)
      "${GIT_FG[@]}" -C "$repo" -c maintenance.auto=false \
        commit -qm "after-$name" --allow-empty
      ;;
    direct)
      g "$repo" maintenance run --auto --quiet
      ;;
    *)
      g "$repo" commit -qm "after-$name" --allow-empty
      ;;
  esac
  after="$(count_worktrees "$repo")"

  if [[ "$mode" == "default" ]]; then
    for ((i = 0; i < 30; i++)); do
      if [[ "$after" == "$expect" ]]; then break; fi
      sleep 1
      after="$(count_worktrees "$repo")"
    done
  fi

  if [[ "$before" == "2" && "$after" == "$expect" ]]; then
    verdict=PASS
  else
    verdict=FAIL
    FAILED=1
  fi
  id="SOUJI-R12-MAINT-$name"
  EMITTED_IDS+=("$id")
  printf 'id=%s case=%s before=%s after=%s expect=%s verdict=%s\n' \
    "$id" "$name" "$before" "$after" "$expect" "$verdict"
}

# Committed expected values (observed on git 2.55.0, 2026-10-19).
run_case plain-commit-sync 1 sync
run_case plain-commit-default 1 default
run_case auto-off 2 auto-off
run_case locked 2 locked
run_case fresh 2 fresh
run_case maintenance-auto 1 direct

selftest_check() { # --selftest: emitted id set == pinned list, all verdicts PASS
  local -a missing=() extra=()
  local want_n=${#SELFTEST_EXPECTED_IDS[@]}
  local got_n=${#EMITTED_IDS[@]}
  local id probe found match=1

  for id in "${SELFTEST_EXPECTED_IDS[@]}"; do
    found=0
    for probe in "${EMITTED_IDS[@]}"; do
      if [[ "$probe" == "$id" ]]; then
        found=1
        break
      fi
    done
    ((found)) || missing+=("$id")
  done
  for id in "${EMITTED_IDS[@]}"; do
    found=0
    for probe in "${SELFTEST_EXPECTED_IDS[@]}"; do
      if [[ "$probe" == "$id" ]]; then
        found=1
        break
      fi
    done
    ((found)) || extra+=("$id")
  done

  if [[ ${#missing[@]} -ne 0 || ${#extra[@]} -ne 0 || "$got_n" -ne "$want_n" || "$FAILED" -ne 0 ]]; then
    match=0
  fi
  if ((match)); then
    printf 'selftest=PASS ids=%s/%s\n' "$want_n" "$want_n"
  else
    printf 'selftest=FAIL ids=%s/%s missing=[%s] extra=[%s] failed_verdicts=%s\n' \
      "$got_n" "$want_n" "${missing[*]-}" "${extra[*]-}" "$FAILED"
    FAILED=1
  fi
}

if ((selftest)); then
  selftest_check
fi

exit "$FAILED"
