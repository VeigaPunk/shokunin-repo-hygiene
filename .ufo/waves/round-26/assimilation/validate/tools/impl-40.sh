#!/usr/bin/env bash
# impl-40 — repeatable read-only fleet census (round 6, seat S40).
#
# Same contract as seat S33, implemented independently. Runners also resolve
# this file as tools/souji-census.impl-40.sh.
#
#   tools/impl-40.sh [--root DIR] [--include-root] [--compare PREV.tsv]
#                    [--selftest]
#
# For every independent git repo that is an immediate child of a root
# (default $SHOKUNIN_ROOT, else the parent of this repo): one TSV row
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
# The root itself is included with --include-root, and also when it is a git
# work tree and no child repo was found (so --root <single-repo> still works).
# Linked worktrees (.git is a file) and symlinked children are not separate
# rows; the owner's worktree count already includes linked worktrees.
#
# Counts
#   worktrees      `git worktree list` lines (main included). Unknown: `-`
#   unpushed       commits reachable from local branches or HEAD that are not
#                  on any remote-tracking ref. No refs/remotes/* → the local
#                  commit count is still reported, and the row is never clean
#                  (no-remote; a local branch cannot establish pushed).
#   dirty          `git status --porcelain` lines, untracked included.
#                  Skipped (dirty=`-`, status-unverifiable) when a tracked or
#                  non-ignored untracked path is secret-shaped — status may
#                  hash those bytes. Gitignored secret names are flagged and
#                  not opened; they do not block the status count.
#   scratch_bytes  `du -sb` of <repo>/.scratch, or 0 if absent. A symlink is
#                  not followed (`stat -c %s` of the link only).
#   mtime_iso      newest regular file under the work tree, ISO-8601 with a
#                  numeric offset. Excludes .git, .ufo/state, watchdog.log,
#                  and secret-shaped names. `-` if none.
#   verdict_flags  comma-sorted subset of:
#                    clean dirty unpushed no-remote scratch secret-shaped
#                    status-unverifiable not-a-repo error
#                  clean only when unpushed=0, dirty=0, a remote-tracking ref
#                  exists, and no measurement failed. scratch and a gitignored
#                  secret-shaped flag do not by themselves block clean.
#                  Unknown numerics are `-`, never a false 0.
#
# --compare PREV.tsv
#   Re-census and diff. Stdout is a diff TSV, not mixed with census rows:
#     repo  field  before  after  change
#   Added/removed repos use field=repo, before/after ABSENT|PRESENT,
#   change=added|removed. Exit 0 if the diff is header-only, 3 if any field
#   differs, 4 if PREV is not this schema (no scan — round-1 artifact tables
#   are incomparable, not identical). mtime changes are reported. Schema is
#   checked before any git call.
#
# --selftest
#   Fixture fleet under mktemp. Exit 0 on pass, 1 on fail. The fixture tree
#   is removed on exit. The live fleet is not scanned.
#
# Exit codes: 0 evaluated clean (or compare identical); 1 selftest failure
# or a measurement error; 2 usage; 3 compare found differences; 4 compare
# schema incomparable. A dirty or unpushed row is a result, not an error.
#
# Safety: bash + coreutils + git only. No fetch/push/commit/branch/prune/
# checkout/reset/rebase, no worktree mutation, no writes outside the
# selftest mktemp, no reads of secret-shaped file content, no opens of
# .ufo/state or watchdog.log. GIT_OPTIONAL_LOCKS=0.
#
# Env: SHOKUNIN_ROOT — default root when --root is omitted.
set -euo pipefail

export LC_ALL=C
export GIT_OPTIONAL_LOCKS=0
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

HEADER=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'
DIFF_HEADER=$'repo\tfield\tbefore\tafter\tchange'

ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"
COMPARE=""
INCLUDE_ROOT=0
SELFTEST=0
HAD_ERROR=0
LAST_LINE=""

usage() {
  sed -n '2,57p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}
usage_err() { printf 'impl-40: %s\n' "$1" >&2; usage 2; }

canon() { readlink -f -- "$1" 2>/dev/null || readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

san() {
  local s=${1-}
  s=${s//$'\t'/ }
  s=${s//$'\n'/ }
  s=${s//$'\r'/ }
  printf '%s' "$s"
}

is_uint() { [[ ${1-} =~ ^[0-9]+$ ]]; }

is_secret_comp() {
  local lc=${1,,}
  case "$lc" in
    *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem) return 0 ;;
  esac
  return 1
}

is_secret_path() {
  local comp
  local IFS='/'
  set -f
  for comp in $1; do
    [ -n "$comp" ] || continue
    if is_secret_comp "$comp"; then
      set +f
      return 0
    fi
  done
  set +f
  return 1
}

join_flags() {
  if [ "$#" -eq 0 ]; then
    printf 'error'
    return 0
  fi
  printf '%s\n' "$@" | LC_ALL=C sort -u | paste -sd, -
}

git_ok() {
  git -C "$1" --no-optional-locks "${@:2}" >/dev/null 2>&1
}

# 0 if any listed index path is secret-shaped. Names only; content unread.
names_have_secret() {
  local repo=$1
  shift
  local name
  while IFS= read -r -d '' name; do
    if is_secret_path "$name"; then
      return 0
    fi
  done < <(git -C "$repo" --no-optional-locks ls-files -z "$@" 2>/dev/null)
  return 1
}

is_own_repo() {
  local d=$1 top
  [ -d "$d" ] || return 1
  [ -L "$d" ] && return 1
  # A .git file is a linked worktree (or submodule). Counted on the owner.
  [ -d "$d/.git" ] || return 1
  top=$(git -C "$d" --no-optional-locks rev-parse --show-toplevel 2>/dev/null) || return 1
  [ "$(canon "$top")" = "$(canon "$d")" ]
}

measure_one() {
  local repo=$1
  local wt="-" un="-" dirty="-" scratch="0" mtime="-"
  local has_remote=0 err=0 secret=0 skip_status=0
  local -a flags=()
  local rc out raw sec

  if ! git_ok "$repo" rev-parse --is-inside-work-tree; then
    LAST_LINE=$(printf '%s\t-\t-\t-\t-\t-\tnot-a-repo' "$(san "$repo")")
    return 0
  fi

  set +e
  out=$(git -C "$repo" --no-optional-locks worktree list 2>/dev/null)
  rc=$?
  set -e
  if [ "$rc" -ne 0 ]; then
    err=1
    flags+=(error)
  else
    wt=$(printf '%s\n' "$out" | grep -c . || true)
  fi

  set +e
  out=$(git -C "$repo" --no-optional-locks for-each-ref --format='%(refname)' refs/remotes 2>/dev/null)
  rc=$?
  set -e
  if [ "$rc" -ne 0 ]; then
    err=1
    flags+=(error)
    has_remote=0
  elif printf '%s\n' "$out" | grep -q .; then
    has_remote=1
  fi

  if git_ok "$repo" rev-parse --verify --quiet HEAD; then
    set +e
    if [ "$has_remote" -eq 1 ]; then
      un=$(git -C "$repo" --no-optional-locks rev-list --count --branches HEAD --not --remotes 2>/dev/null)
    else
      un=$(git -C "$repo" --no-optional-locks rev-list --count --branches HEAD 2>/dev/null)
    fi
    rc=$?
    set -e
    if [ "$rc" -ne 0 ] || ! is_uint "$un"; then
      un="-"
      err=1
      flags+=(error)
    fi
  else
    un=0
  fi

  if [ "$has_remote" -eq 0 ]; then
    flags+=(no-remote)
  fi
  if is_uint "$un" && [ "$un" -gt 0 ]; then
    flags+=(unpushed)
  fi

  # Name-only precheck. status may hash a stat-dirty tracked secret.
  if ! git_ok "$repo" ls-files -z; then
    skip_status=1
    err=1
    flags+=(error status-unverifiable)
  elif names_have_secret "$repo" || names_have_secret "$repo" --others --exclude-standard; then
    skip_status=1
    secret=1
    flags+=(secret-shaped status-unverifiable)
  fi

  if [ "$skip_status" -eq 0 ]; then
    set +e
    out=$(git -C "$repo" --no-optional-locks status --porcelain --untracked-files=normal 2>/dev/null)
    rc=$?
    set -e
    if [ "$rc" -ne 0 ]; then
      dirty="-"
      err=1
      flags+=(status-unverifiable)
    else
      dirty=$(printf '%s\n' "$out" | grep -c . || true)
      if is_uint "$dirty" && [ "$dirty" -gt 0 ]; then
        flags+=(dirty)
      fi
    fi
    unset out
  fi

  if [ -L "$repo/.scratch" ]; then
    scratch=$(stat -c '%s' -- "$repo/.scratch" 2>/dev/null || true)
    if ! is_uint "$scratch"; then
      scratch="-"
      err=1
      flags+=(error)
    elif [ "$scratch" -gt 0 ]; then
      flags+=(scratch)
    fi
  elif [ -d "$repo/.scratch" ]; then
    set +e
    scratch=$(du -sb -- "$repo/.scratch" 2>/dev/null | cut -f1)
    rc=$?
    set -e
    if [ "$rc" -ne 0 ] || ! is_uint "$scratch"; then
      scratch="-"
      err=1
      flags+=(error)
    elif [ "$scratch" -gt 0 ]; then
      flags+=(scratch)
    fi
  elif [ -e "$repo/.scratch" ]; then
    scratch=$(stat -c '%s' -- "$repo/.scratch" 2>/dev/null || true)
    if ! is_uint "$scratch"; then
      scratch="-"
      err=1
      flags+=(error)
    elif [ "$scratch" -gt 0 ]; then
      flags+=(scratch)
    fi
  fi

  # Metadata only. Prune off-limits and secret-shaped names before -type f
  # so their contents are never opened and their paths are not selected.
  # Stream the max. sort(1) spills to $TMPDIR and fails closed the whole
  # row when /tmp is quota-exhausted (observed on the fleet-root walk).
  set +e
  raw=$(find "$repo" \
    \( -path "$repo/.git" -o -path "$repo/.ufo/state" -o -name 'watchdog.log' \) -prune -o \
    \( -iname '*.env' -o -iname '.env' -o -iname '.env.*' -o -iname '.envrc' \
       -o -iname '*credential*' -o -iname '*secret*' -o -iname 'id_*' -o -iname '*.pem' \) -prune -o \
    -type f -printf '%T@\n' 2>/dev/null | {
      max=0
      found=0
      while IFS= read -r ts; do
        sec=${ts%%.*}
        case "$sec" in
          ''|*[!0-9]*) continue ;;
        esac
        if [ "$found" -eq 0 ] || [ "$sec" -gt "$max" ]; then
          max=$sec
          found=1
        fi
      done
      [ "$found" -eq 1 ] && printf '%s\n' "$max"
    })
  rc=$?
  set -e
  if [ "$rc" -ne 0 ]; then
    err=1
    flags+=(error)
    mtime="-"
  elif [ -n "$raw" ]; then
    sec=$raw
    if is_uint "$sec"; then
      mtime=$(date -d "@$sec" --iso-8601=seconds 2>/dev/null || true)
      [ -n "$mtime" ] || { mtime="-"; err=1; flags+=(error); }
    else
      mtime="-"
      err=1
      flags+=(error)
    fi
  fi

  if find "$repo" \
      \( -path "$repo/.git" -o -path "$repo/.ufo/state" -o -name 'watchdog.log' \) -prune -o \
      \( -iname '*.env' -o -iname '.env' -o -iname '.env.*' -o -iname '.envrc' \
         -o -iname '*credential*' -o -iname '*secret*' -o -iname 'id_*' -o -iname '*.pem' \) \
      -print -quit 2>/dev/null | grep -q .; then
    secret=1
    flags+=(secret-shaped)
  fi

  if [ "$err" -eq 0 ] && [ "$has_remote" -eq 1 ] && [ "$un" = 0 ] && [ "$dirty" = 0 ] && [ "$wt" != "-" ]; then
    flags+=(clean)
  fi
  if [ "$err" -ne 0 ]; then
    HAD_ERROR=1
  fi

  LAST_LINE=$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
    "$(san "$repo")" "$wt" "$un" "$dirty" "$scratch" "$(san "$mtime")" "$(join_flags "${flags[@]+"${flags[@]}"}")")
}

declare -a REPOS=()
declare -a SECRET_ROWS=()
declare -a CENSUS_LINES=()
declare -A SEEN=()

add_repo() {
  local c
  c=$(canon "$1")
  [ -n "${SEEN[$c]:-}" ] && return 0
  SEEN[$c]=1
  REPOS+=("$c")
}

discover() {
  local d base
  shopt -s nullglob dotglob
  for d in "$ROOT"/*; do
    [ -d "$d" ] || continue
    [ -L "$d" ] && continue
    base=$(basename -- "$d")
    case "$base" in
      .|..|.git) continue ;;
    esac
    if is_secret_path "$d"; then
      SECRET_ROWS+=("$(canon "$d")")
      continue
    fi
    if is_own_repo "$d"; then
      add_repo "$d"
    fi
  done
  shopt -u dotglob nullglob
  if [ "$INCLUDE_ROOT" -eq 1 ] && is_own_repo "$ROOT"; then
    add_repo "$ROOT"
  fi
  if [ "${#REPOS[@]}" -eq 0 ] && [ "${#SECRET_ROWS[@]}" -eq 0 ] && is_own_repo "$ROOT"; then
    add_repo "$ROOT"
  fi
  if [ "${#REPOS[@]}" -gt 0 ]; then
    mapfile -t REPOS < <(printf '%s\n' "${REPOS[@]}" | LC_ALL=C sort)
  fi
}

fill_census() {
  local r
  CENSUS_LINES=()
  for r in "${SECRET_ROWS[@]+"${SECRET_ROWS[@]}"}"; do
    CENSUS_LINES+=("$(printf '%s\t-\t-\t-\t-\t-\tsecret-shaped' "$(san "$r")")")
  done
  for r in "${REPOS[@]+"${REPOS[@]}"}"; do
    measure_one "$r"
    CENSUS_LINES+=("$LAST_LINE")
  done
  if [ "${#CENSUS_LINES[@]}" -gt 0 ]; then
    mapfile -t CENSUS_LINES < <(printf '%s\n' "${CENSUS_LINES[@]}" | LC_ALL=C sort)
  fi
}

print_census() {
  printf '%s\n' "$HEADER"
  if [ "${#CENSUS_LINES[@]}" -gt 0 ]; then
    printf '%s\n' "${CENSUS_LINES[@]}"
  fi
}

norm_repo() {
  if [ -d "$1" ]; then
    canon "$1"
  else
    printf '%s' "$1"
  fi
}

field_at() {
  printf '%s' "$1" | cut -f"$2"
}

# Exit 2/4 before any git scan. Round-1 artifact tables must not look identical.
compare_gate() {
  local prev=$1 first got
  if [ ! -e "$prev" ] || [ -d "$prev" ]; then
    printf 'impl-40: compare target is not a file: %s\n' "$prev" >&2
    exit 2
  fi
  if is_secret_path "$prev" || { [ -L "$prev" ] && is_secret_path "$(canon "$prev")"; }; then
    printf 'impl-40: compare path is secret-shaped; refused\n' >&2
    exit 2
  fi
  IFS= read -r first < "$prev" || first=""
  first=${first%$'\r'}
  if [ "$first" != "$HEADER" ]; then
    got=$(san "$first")
    printf 'impl-40: compare schema mismatch (not a repo census; round-1 artifact tables are incomparable)\n' >&2
    printf '%s\n' "$DIFF_HEADER"
    printf '_schema\theader\t%s\t%s\tmismatch\n' "$got" "$(san "$HEADER")"
    exit 4
  fi
}

compare_prev() {
  local prev=$1
  local line repo key
  local -a diff=() keys=()
  local -A cur=() prevmap=() seen_prev=()

  for line in "${CENSUS_LINES[@]+"${CENSUS_LINES[@]}"}"; do
    repo=$(field_at "$line" 1)
    cur[$repo]=$line
  done

  local n=0
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%$'\r'}
    n=$((n + 1))
    [ "$n" -eq 1 ] && continue
    [ -n "$line" ] || continue
    local tabs=${line//[!$'\t']/}
    if [ "${#tabs}" -ne 6 ]; then
      printf 'impl-40: compare row %s has %s tabs, want 6\n' "$n" "${#tabs}" >&2
      printf '%s\n' "$DIFF_HEADER"
      printf '_schema\trow\t%s\t6-tabs\tmismatch\n' "$n"
      exit 4
    fi
    repo=$(norm_repo "$(field_at "$line" 1)")
    if [ -n "${seen_prev[$repo]:-}" ]; then
      printf 'impl-40: compare duplicate repo after normalize: %s\n' "$repo" >&2
      exit 4
    fi
    seen_prev[$repo]=1
    prevmap[$repo]=$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
      "$repo" \
      "$(field_at "$line" 2)" "$(field_at "$line" 3)" "$(field_at "$line" 4)" \
      "$(field_at "$line" 5)" "$(field_at "$line" 6)" "$(field_at "$line" 7)")
  done < "$prev"

  for key in "${!cur[@]}"; do keys+=("$key"); done
  for key in "${!prevmap[@]}"; do
    [ -n "${cur[$key]:-}" ] || keys+=("$key")
  done
  if [ "${#keys[@]}" -gt 0 ]; then
    mapfile -t keys < <(printf '%s\n' "${keys[@]}" | LC_ALL=C sort -u)
  fi

  local f before after change i
  for key in "${keys[@]+"${keys[@]}"}"; do
    if [ -z "${prevmap[$key]:-}" ]; then
      diff+=("$(printf '%s\trepo\tABSENT\tPRESENT\tadded' "$(san "$key")")")
      continue
    fi
    if [ -z "${cur[$key]:-}" ]; then
      diff+=("$(printf '%s\trepo\tPRESENT\tABSENT\tremoved' "$(san "$key")")")
      continue
    fi
    for i in 2 3 4 5 6 7; do
      before=$(field_at "${prevmap[$key]}" "$i")
      after=$(field_at "${cur[$key]}" "$i")
      [ "$before" = "$after" ] && continue
      case "$i" in
        2) f=worktrees ;;
        3) f=unpushed ;;
        4) f=dirty ;;
        5) f=scratch_bytes ;;
        6) f=mtime_iso ;;
        7) f=verdict_flags ;;
      esac
      if is_uint "$before" && is_uint "$after"; then
        change=$((after - before))
        if [ "$change" -gt 0 ]; then change="+$change"; fi
      else
        change=changed
      fi
      diff+=("$(printf '%s\t%s\t%s\t%s\t%s' "$(san "$key")" "$f" "$(san "$before")" "$(san "$after")" "$change")")
    done
  done

  printf '%s\n' "$DIFF_HEADER"
  if [ "${#diff[@]}" -gt 0 ]; then
    printf '%s\n' "${diff[@]}" | LC_ALL=C sort
    exit 3
  fi
  exit 0
}

selftest() {
  local tmp pass=0 fail=0
  tmp=$(mktemp -d /tmp/souji-census-40.XXXXXX)
  # Expand now: a local tmp is unset when the EXIT trap runs after return.
  trap "rm -rf -- $(printf '%q' "$tmp")" EXIT
  mkdir -p "$tmp/bin" "$tmp/fleet" "$tmp/wts" "$tmp/outside-payload"

  cat > "$tmp/bin/git" << 'WRAP'
#!/bin/bash
# Fail closed: only the census read verbs may run while this wrapper is first on PATH.
log=${GITLOG:-/dev/null}
printf '%s\n' "$*" >> "$log"
args=("$@")
i=0
sub=""
while [ "$i" -lt "${#args[@]}" ]; do
  a=${args[$i]}
  case "$a" in
    -C|-c|--git-dir|--work-tree|--namespace) i=$((i + 2)); continue ;;
    --no-optional-locks|--no-pager|-P|--paginate) i=$((i + 1)); continue ;;
    -*) i=$((i + 1)); continue ;;
    *) sub=$a; break ;;
  esac
done
case "$sub" in
  rev-parse|rev-list|status|for-each-ref|show-ref|symbolic-ref|log|ls-files) ;;
  worktree)
    if [ "${args[$((i + 1))]:-}" != "list" ]; then
      printf 'FORBIDDEN git worktree %s\n' "${args[$((i + 1))]:-}" >> "$log"
      printf 'FORBIDDEN git worktree %s\n' "${args[$((i + 1))]:-}" >&2
      exit 99
    fi
    ;;
  *)
    printf 'FORBIDDEN git %s\n' "$sub" >> "$log"
    printf 'FORBIDDEN git %s\n' "$sub" >&2
    exit 99
    ;;
esac
exec /usr/bin/git "$@"
WRAP
  chmod 755 "$tmp/bin/git"

  init_repo() {
    local r=$1
    mkdir -p "$r"
    /usr/bin/git -C "$r" init -q -b master
    /usr/bin/git -C "$r" config user.email 'souji@shokunin.local'
    /usr/bin/git -C "$r" config user.name 'souji-shokunin'
    printf 'init\n' > "$r/a.txt"
    /usr/bin/git -C "$r" add a.txt
    /usr/bin/git -C "$r" commit -q -m init
  }
  pin_origin() {
    /usr/bin/git -C "$1" update-ref refs/remotes/origin/master HEAD
    /usr/bin/git -C "$1" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  }

  init_repo "$tmp/fleet/cleanrepo"
  printf '.ufo/\n' > "$tmp/fleet/cleanrepo/.gitignore"
  /usr/bin/git -C "$tmp/fleet/cleanrepo" add .gitignore
  /usr/bin/git -C "$tmp/fleet/cleanrepo" commit -q -m ignore-ufo
  pin_origin "$tmp/fleet/cleanrepo"
  touch -d '2020-01-02 03:04:05' "$tmp/fleet/cleanrepo/a.txt" "$tmp/fleet/cleanrepo/.gitignore"
  mkdir -p "$tmp/fleet/cleanrepo/.ufo/state"
  printf 'STATE-SENTINEL-40\n' > "$tmp/fleet/cleanrepo/.ufo/state/x"
  printf 'WATCHDOG-SENTINEL-40\n' > "$tmp/fleet/cleanrepo/.ufo/watchdog.log"
  touch -d '2030-01-01 00:00:00' "$tmp/fleet/cleanrepo/.ufo/watchdog.log" "$tmp/fleet/cleanrepo/.ufo/state/x"

  init_repo "$tmp/fleet/unpushedrepo"
  pin_origin "$tmp/fleet/unpushedrepo"
  printf 'ahead\n' >> "$tmp/fleet/unpushedrepo/a.txt"
  /usr/bin/git -C "$tmp/fleet/unpushedrepo" add a.txt
  /usr/bin/git -C "$tmp/fleet/unpushedrepo" commit -q -m ahead

  init_repo "$tmp/fleet/dirtyrepo"
  pin_origin "$tmp/fleet/dirtyrepo"
  printf 'untracked\n' > "$tmp/fleet/dirtyrepo/untracked.txt"

  init_repo "$tmp/fleet/scratchrepo"
  pin_origin "$tmp/fleet/scratchrepo"
  mkdir -p "$tmp/fleet/scratchrepo/.scratch"
  printf 'note\n' > "$tmp/fleet/scratchrepo/.scratch/note.txt"

  init_repo "$tmp/fleet/linkscratchrepo"
  pin_origin "$tmp/fleet/linkscratchrepo"
  printf 'SENTINEL-SCRATCH-TARGET-40\n' > "$tmp/outside-payload/payload"
  dd if=/dev/zero bs=1000 count=10 status=none >> "$tmp/outside-payload/payload"
  ln -s "$tmp/outside-payload" "$tmp/fleet/linkscratchrepo/.scratch"

  init_repo "$tmp/fleet/noremote"

  init_repo "$tmp/fleet/wtrepo"
  pin_origin "$tmp/fleet/wtrepo"
  /usr/bin/git -C "$tmp/fleet/wtrepo" worktree add -q -b wt-extra "$tmp/wts/extra"
  /usr/bin/git -C "$tmp/fleet/wtrepo" worktree add -q --detach "$tmp/fleet/linked-wt" HEAD

  init_repo "$tmp/fleet/keyrepo"
  pin_origin "$tmp/fleet/keyrepo"
  printf 'SENTINEL-SECRET-CONTENT-40\n' > "$tmp/fleet/keyrepo/id_rsa"

  init_repo "$tmp/fleet/ignoredrepo"
  pin_origin "$tmp/fleet/ignoredrepo"
  printf '*.pem\n' > "$tmp/fleet/ignoredrepo/.gitignore"
  /usr/bin/git -C "$tmp/fleet/ignoredrepo" add .gitignore
  /usr/bin/git -C "$tmp/fleet/ignoredrepo" commit -q -m ignore
  /usr/bin/git -C "$tmp/fleet/ignoredrepo" update-ref refs/remotes/origin/master HEAD
  printf 'SENTINEL-IGNORED-PEM-40\n' > "$tmp/fleet/ignoredrepo/ignored.pem"
  touch -d '2030-06-01 00:00:00' "$tmp/fleet/ignoredrepo/ignored.pem"
  touch -d '2020-01-02 03:04:05' "$tmp/fleet/ignoredrepo/a.txt" "$tmp/fleet/ignoredrepo/.gitignore"

  mkdir -p "$tmp/fleet/.env"
  printf 'SENTINEL-ENV-DIR-40\n' > "$tmp/fleet/.env/payload"
  /usr/bin/git -C "$tmp/fleet/.env" init -q -b master
  mkdir -p "$tmp/fleet/notes"
  printf 'not a repo\n' > "$tmp/fleet/notes/readme.txt"
  ln -s "$tmp/fleet/cleanrepo" "$tmp/fleet/linkrepo"

  local -A idx_before=()
  local r
  for r in cleanrepo unpushedrepo dirtyrepo scratchrepo linkscratchrepo noremote wtrepo keyrepo ignoredrepo; do
    idx_before[$r]=$(stat -c '%Y' "$tmp/fleet/$r/.git/index")
  done

  export PATH="$tmp/bin:$PATH"
  export GITLOG="$tmp/git.log"
  export SHOKUNIN_ROOT="$tmp/fleet"
  : > "$GITLOG"

  local out err rc
  set +e
  out=$("$SELF" --root "$tmp/fleet" 2>"$tmp/err")
  rc=$?
  set -e

  ok() { pass=$((pass + 1)); }
  bad() { fail=$((fail + 1)); printf 'FAIL %s\n' "$1" >&2; }

  [ "$rc" -eq 0 ] && ok || bad "census exit=$rc err=$(head -c 300 "$tmp/err")"
  [ ! -s "$tmp/err" ] && ok || bad "census stderr non-empty: $(head -c 200 "$tmp/err")"
  if ! grep -q 'FORBIDDEN' "$GITLOG"; then ok; else bad "forbidden git verb invoked"; fi
  if ! grep -q '/home/vgpnk/Projects/shokunin' "$GITLOG"; then ok; else bad "live fleet was scanned"; fi
  if grep -q 'status' "$GITLOG"; then ok; else bad "wrapper was not used for status"; fi

  local header line repo nrow=0
  header=$(printf '%s\n' "$out" | head -1)
  [ "$header" = "$HEADER" ] && ok || bad "bad header: $header"
  while IFS= read -r line; do
    [ "$line" = "$HEADER" ] && continue
    [ -n "$line" ] || continue
    nrow=$((nrow + 1))
  done <<< "$out"
  [ "$nrow" -eq 10 ] && ok || bad "data rows=$nrow want 10"

  row_of() {
    local suf=$1 line repo
    while IFS= read -r line; do
      repo=${line%%$'\t'*}
      case "$repo" in
        *"$suf") printf '%s\n' "$line"; return 0 ;;
      esac
    done <<< "$out"
    return 1
  }
  local row flags
  row=$(row_of '/cleanrepo')
  [ -n "$row" ] && ok || bad "missing cleanrepo"
  [ "$(field_at "$row" 2)" = 1 ] && ok || bad "cleanrepo worktrees=$(field_at "$row" 2)"
  [ "$(field_at "$row" 3)" = 0 ] && ok || bad "cleanrepo unpushed=$(field_at "$row" 3)"
  [ "$(field_at "$row" 4)" = 0 ] && ok || bad "cleanrepo dirty=$(field_at "$row" 4)"
  [ "$(field_at "$row" 5)" = 0 ] && ok || bad "cleanrepo scratch=$(field_at "$row" 5)"
  local exp_m
  exp_m=$(date -d '2020-01-02 03:04:05' --iso-8601=seconds)
  [ "$(field_at "$row" 6)" = "$exp_m" ] && ok || bad "cleanrepo mtime=$(field_at "$row" 6) want=$exp_m"
  [ "$(field_at "$row" 7)" = "clean" ] && ok || bad "cleanrepo flags=$(field_at "$row" 7)"

  row=$(row_of '/unpushedrepo')
  [ "$(field_at "$row" 3)" = 1 ] && ok || bad "unpushedrepo unpushed=$(field_at "$row" 3)"
  flags=$(field_at "$row" 7)
  case ",$flags," in
    *,unpushed,*) ok ;;
    *) bad "unpushedrepo flags=$flags" ;;
  esac
  case ",$flags," in
    *,clean,*) bad "unpushedrepo falsely clean" ;;
    *) ok ;;
  esac

  row=$(row_of '/dirtyrepo')
  [ "$(field_at "$row" 4)" = 1 ] && ok || bad "dirtyrepo dirty=$(field_at "$row" 4)"
  case ",$(field_at "$row" 7)," in
    *,dirty,*) ok ;;
    *) bad "dirtyrepo flags=$(field_at "$row" 7)" ;;
  esac

  row=$(row_of '/scratchrepo')
  local exp_sc
  exp_sc=$(du -sb -- "$tmp/fleet/scratchrepo/.scratch" | cut -f1)
  [ "$(field_at "$row" 5)" = "$exp_sc" ] && ok || bad "scratchrepo bytes=$(field_at "$row" 5) want=$exp_sc"
  case ",$(field_at "$row" 7)," in
    *,scratch,*) ok ;;
    *) bad "scratchrepo flags=$(field_at "$row" 7)" ;;
  esac

  row=$(row_of '/linkscratchrepo')
  local link_sz
  link_sz=$(stat -c '%s' -- "$tmp/fleet/linkscratchrepo/.scratch")
  [ "$(field_at "$row" 5)" = "$link_sz" ] && ok || bad "symlink scratch bytes=$(field_at "$row" 5) want=$link_sz"
  [ "$(field_at "$row" 5)" -lt 1000 ] && ok || bad "symlink scratch followed target"

  row=$(row_of '/noremote')
  flags=$(field_at "$row" 7)
  case ",$flags," in
    *,no-remote,*) ok ;;
    *) bad "noremote flags=$flags" ;;
  esac
  case ",$flags," in
    *,clean,*) bad "noremote falsely clean" ;;
    *) ok ;;
  esac
  is_uint "$(field_at "$row" 3)" && [ "$(field_at "$row" 3)" -ge 1 ] && ok || bad "noremote unpushed=$(field_at "$row" 3)"

  row=$(row_of '/wtrepo')
  [ "$(field_at "$row" 2)" = 3 ] && ok || bad "wtrepo worktrees=$(field_at "$row" 2) want 3"

  row=$(row_of '/keyrepo')
  flags=$(field_at "$row" 7)
  [ "$(field_at "$row" 4)" = "-" ] && ok || bad "keyrepo dirty should be unverifiable, got $(field_at "$row" 4)"
  case ",$flags," in
    *,secret-shaped,*) ok ;;
    *) bad "keyrepo flags=$flags" ;;
  esac
  case ",$flags," in
    *,status-unverifiable,*) ok ;;
    *) bad "keyrepo missing status-unverifiable ($flags)" ;;
  esac
  case ",$flags," in
    *,clean,*) bad "keyrepo falsely clean" ;;
    *) ok ;;
  esac

  row=$(row_of '/ignoredrepo')
  [ "$(field_at "$row" 4)" = 0 ] && ok || bad "ignoredrepo dirty=$(field_at "$row" 4)"
  [ "$(field_at "$row" 6)" = "$exp_m" ] && ok || bad "ignoredrepo mtime picked secret file: $(field_at "$row" 6)"
  flags=$(field_at "$row" 7)
  case ",$flags," in
    *,secret-shaped,*) ok ;;
    *) bad "ignoredrepo flags=$flags" ;;
  esac
  case ",$flags," in
    *,clean,*) ok ;;
    *) bad "ignoredrepo should still be git-clean ($flags)" ;;
  esac

  row=$(row_of '/.env')
  [ "$(field_at "$row" 7)" = "secret-shaped" ] && ok || bad ".env row=$(field_at "$row" 7)"
  [ "$(field_at "$row" 3)" = "-" ] && ok || bad ".env row was measured"

  if printf '%s\n' "$out" | grep -q '/linked-wt'; then bad "linked worktree double-counted"; else ok; fi
  if printf '%s\n' "$out" | grep -q '/linkrepo'; then bad "symlinked child followed"; else ok; fi
  if printf '%s\n' "$out" | grep -q '/notes'; then bad "non-repo emitted"; else ok; fi

  if printf '%s\n' "$out" | grep -q 'SENTINEL-'; then bad "sentinel content leaked"; else ok; fi
  if printf '%s\n' "$out" | grep -q 'watchdog.log'; then bad "watchdog.log path leaked"; else ok; fi
  if printf '%s\n' "$out" | grep -q '.ufo/state'; then bad ".ufo/state path leaked"; else ok; fi

  local changed=0
  for r in cleanrepo unpushedrepo dirtyrepo scratchrepo linkscratchrepo noremote wtrepo keyrepo ignoredrepo; do
    if [ "$(stat -c '%Y' "$tmp/fleet/$r/.git/index")" != "${idx_before[$r]}" ]; then
      changed=1
      bad "index mtime changed: $r"
    fi
  done
  [ "$changed" -eq 0 ] && ok

  local out2
  set +e
  out2=$("$SELF" --root "$tmp/fleet" 2>/dev/null)
  set -e
  [ "$out" = "$out2" ] && ok || bad "two censuses differed"

  printf '%s\n' "$out" > "$tmp/first.tsv"
  set +e
  "$SELF" --root "$tmp/fleet" --compare "$tmp/first.tsv" >"$tmp/cmp.out" 2>"$tmp/cmp.err"
  rc=$?
  set -e
  [ "$rc" -eq 0 ] && ok || bad "identical compare exit=$rc stderr=$(head -c 200 "$tmp/cmp.err")"
  [ "$(wc -l < "$tmp/cmp.out" | tr -d ' ')" = 1 ] && ok || bad "identical compare not header-only"

  printf 'more\n' > "$tmp/fleet/dirtyrepo/another.txt"
  set +e
  "$SELF" --root "$tmp/fleet" --compare "$tmp/first.tsv" >"$tmp/diff.out" 2>"$tmp/diff.err"
  rc=$?
  set -e
  [ "$rc" -eq 3 ] && ok || bad "dirty compare exit=$rc"
  if grep -q $'\tdirty\t' "$tmp/diff.out"; then ok; else bad "diff missing dirty field"; fi
  if grep -q '/cleanrepo' "$tmp/diff.out"; then bad "cleanrepo appeared in dirty diff"; else ok; fi

  : > "$GITLOG"
  printf 'seat\tpath\treceipt\n' > "$tmp/bad.tsv"
  set +e
  "$SELF" --root "$tmp/fleet" --compare "$tmp/bad.tsv" >"$tmp/bad.out" 2>"$tmp/bad.err"
  rc=$?
  set -e
  [ "$rc" -eq 4 ] && ok || bad "schema mismatch exit=$rc"
  if grep -q 'schema mismatch' "$tmp/bad.err"; then ok; else bad "schema stderr missing"; fi
  [ ! -s "$GITLOG" ] && ok || bad "schema mismatch scanned the tree: $(head -c 200 "$GITLOG")"

  : > "$GITLOG"
  set +e
  "$SELF" --not-a-flag >/dev/null 2>&1
  rc=$?
  set -e
  [ "$rc" -eq 2 ] && ok || bad "usage exit=$rc"
  [ ! -s "$GITLOG" ] && ok || bad "usage error scanned a repo"

  set +e
  out=$("$SELF" --root "$tmp/fleet/cleanrepo" 2>/dev/null)
  rc=$?
  set -e
  [ "$rc" -eq 0 ] && ok || bad "single-repo exit=$rc"
  nrow=0
  while IFS= read -r line; do
    [ "$line" = "$HEADER" ] && continue
    [ -n "$line" ] && nrow=$((nrow + 1))
  done <<< "$out"
  [ "$nrow" -eq 1 ] && ok || bad "single-repo rows=$nrow"
  case "$out" in
    *"/cleanrepo"$'\t'*) ok ;;
    *) bad "single-repo fallback missed the repo" ;;
  esac

  set +e
  out2=$("$SELF" --root "$tmp/fleet/cleanrepo" --include-root 2>/dev/null)
  set -e
  [ "$out" = "$out2" ] && ok || bad "include-root duplicated the single repo"

  if [ "$fail" -eq 0 ]; then
    printf 'SELFTEST pass=%s fail=0\n' "$pass"
    return 0
  fi
  printf 'SELFTEST pass=%s fail=%s\n' "$pass" "$fail" >&2
  return 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --include-root) INCLUDE_ROOT=1; shift ;;
    --root)
      [ "$#" -ge 2 ] || usage_err "--root needs a directory"
      ROOT=$2
      shift 2
      ;;
    --compare)
      [ "$#" -ge 2 ] || usage_err "--compare needs a TSV"
      COMPARE=$2
      shift 2
      ;;
    -h|--help) usage 0 ;;
    --) shift; break ;;
    -*) usage_err "unknown option: $1" ;;
    *) usage_err "unexpected argument: $1" ;;
  esac
done

if [ "$SELFTEST" -eq 1 ]; then
  selftest
  exit $?
fi

ROOT=$(canon "$ROOT")
if [ "$ROOT" = "/" ]; then
  usage_err "refusing to census /"
fi
if [ ! -d "$ROOT" ]; then
  usage_err "root is not a directory: $ROOT"
fi
if is_secret_path "$ROOT"; then
  usage_err "root path is secret-shaped; refused"
fi

if [ -n "$COMPARE" ]; then
  compare_gate "$COMPARE"
fi

discover
fill_census

if [ -n "$COMPARE" ]; then
  compare_prev "$COMPARE"
fi

print_census
if [ "$HAD_ERROR" -ne 0 ]; then
  exit 1
fi
exit 0
