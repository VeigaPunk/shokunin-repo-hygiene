#!/usr/bin/env bash
# souji-census.impl-48 — repeatable read-only fleet census (round 6, seat S48).
#
# CLI
#   tools/souji-census.impl-48.sh [--root PATH] [--compare PREV.tsv] [--selftest]
#
# Default root: $SHOKUNIN_ROOT, else the parent of this lane repo.
# One TSV row per primary repo (a directory whose .git is a real directory,
# not a linked worktree and not a symlink). The root itself is included when
# it is a primary repo. Depth is 1: nested checkouts are not separate rows.
#
# Columns (header always printed):
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
#
# Counting commands, matched exactly by a hand check (read-only; optional
# index locks suppressed so the scan does not rewrite a sibling index):
#   worktrees     git --no-optional-locks -C <repo> worktree list | wc -l
#                 (includes the main worktree)
#   unpushed      git --no-optional-locks -C <repo> log --branches --not --remotes --oneline | wc -l
#   dirty         git --no-optional-locks -C <repo> status --porcelain | wc -l
#   scratch_bytes du -sb <repo>/.scratch   (0 when .scratch is absent)
#   mtime_iso     newest regular file under the repo, UTC ISO-8601, or "-"
#                 Walk prunes .git, .ufo, watchdog.log, secret-shaped names,
#                 and immediate child primary repos. Symlinks are not followed.
#
# verdict_flags (comma-separated, class first, detail flags C-sorted):
#   class: OBSERVE | NOT-SAFE | secrets-refusal | unreachable
#   This census never emits a removal receipt. The token SAFE is never a flag.
#   NOT-SAFE means live or unverifiable hygiene state (unpushed, dirty, a
#   scratch symlink, or an unreadable metric) — not an authorization to delete.
#   Detail: clean, unpushed, dirty, scratch, scratch-absent, scratch-symlink,
#   scratch-not-dir, scratch-unreadable, extra-worktrees, no-remote, no-commits.
#
# --compare PREV.tsv
#   Diff the current census against a previous TSV with the same header.
#   Stdout is a different 5-column TSV:
#     repo  field  before  after  delta
#   Only differences are listed. Numeric delta is after-before. A previous
#   file with another schema (including census/round-1/census.tsv, which is
#   per-artifact) prints one schema row with delta=incomparable and exits 0.
#   Differences are data, not failures.
#
# Exit codes: 0 evaluated; 1 selftest failure or root/evaluation error; 2 usage.
# Never reads the obsidian ledger, secret-shaped files, .ufo/state, or
# watchdog.log. Never invokes mutating git verbs. Writes only under mktemp
# during --selftest / --compare scratch.
set -euo pipefail
export LC_ALL=C
export GIT_OPTIONAL_LOCKS=0
export GIT_TERMINAL_PROMPT=0
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
DEFAULT_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"

SELFTEST=0
COMPARE=0
PREV=""
ROOT_SET=0
ROOT=""
ROWS=()

usage() {
  sed -n '2,42p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-2}"
}
usage_err() { printf 'souji-census.impl-48: %s\n' "$1" >&2; usage 2; }

canon() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

is_secret_shaped() {
  local comp lc
  local IFS='/'
  set -f
  for comp in $1; do
    lc=${comp,,}
    case "$lc" in
      *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem)
        set +f; return 0 ;;
    esac
  done
  set +f
  return 1
}

is_offlimits() {
  case "$1" in
    */.ufo/state|*/.ufo/state/*|*/.ufo/watchdog.log|*obsidian-ledger.tsv)
      return 0 ;;
  esac
  case "$1" in
    "$HOME/.config"|"$HOME/.config"/*) return 0 ;;
  esac
  return 1
}

refuse_path() { # $1 label, $2 path; exit 2
  if is_secret_shaped "$2" || is_offlimits "$2"; then
    usage_err "$1 is secret-shaped or off-limits"
  fi
}

git_ro() { git --no-optional-locks "$@"; }

count_lines() {
  if [ -z "${1:-}" ]; then
    printf '0\n'
    return 0
  fi
  printf '%s\n' "$1" | wc -l | tr -d '[:space:]'
}

capture_count() { # git args after --; prints count or returns 1
  local out rc
  set +e
  out=$(git_ro "$@" 2>/dev/null)
  rc=$?
  set -e
  if [ "$rc" -ne 0 ]; then
    return 1
  fi
  count_lines "$out"
}

is_primary_repo() {
  [ -d "$1/.git" ] && [ ! -L "$1/.git" ]
}

has_remote() {
  local n
  n=$(git_ro -C "$1" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null \
    | grep -v '/HEAD$' | grep -c . || true)
  [ "${n:-0}" -gt 0 ]
}

has_commits() {
  git_ro -C "$1" rev-parse --verify --quiet HEAD >/dev/null 2>&1
}

scratch_measure() { # stdout: <kind>\t<bytes>
  local s="$1/.scratch"
  if [ -L "$s" ]; then
    printf 'symlink\t-\n'
    return 0
  fi
  if [ ! -e "$s" ]; then
    printf 'absent\t0\n'
    return 0
  fi
  if [ ! -d "$s" ]; then
    printf 'notdir\t-\n'
    return 0
  fi
  local bytes rc
  set +e
  bytes=$(du -sb -- "$s" 2>/dev/null | awk '{print $1; exit}')
  rc=$?
  set -e
  if [ "$rc" -ne 0 ] || [ -z "$bytes" ]; then
    printf 'unreadable\t-\n'
    return 0
  fi
  printf 'dir\t%s\n' "$bytes"
}

newest_epoch() {
  local repo=$1 d
  local -a args=() nested=()
  args+=("$repo")
  args+=(\( -name .git -o -name .ufo -o -name watchdog.log \) -prune -o)
  shopt -s nullglob
  for d in "$repo"/*; do
    if [ -d "$d" ] && [ ! -L "$d" ] && [ -e "$d/.git" ]; then
      nested+=("$d")
    fi
  done
  shopt -u nullglob
  if [ "${#nested[@]}" -gt 0 ]; then
    args+=(\()
    local first=1
    for d in "${nested[@]}"; do
      if [ "$first" = 1 ]; then first=0; else args+=(-o); fi
      args+=(-path "$d")
    done
    args+=(\) -prune -o)
  fi
  args+=(\( -name '*.env' -o -name '.env' -o -name '.env.*' -o -name '.envrc' \
    -o -iname '*credential*' -o -iname '*secret*' -o -iname '*.pem' -o -name 'id_*' \
    \) -prune -o)
  args+=(-type f -printf '%T@\n')
  find -P "${args[@]}" 2>/dev/null \
    | awk 'BEGIN{m=""} {if (m=="" || $1+0 > m+0) m=$1} END{if (m!="") printf "%s\n", m}'
}

newest_iso() {
  local epoch
  epoch=$(newest_epoch "$1" || true)
  if [ -z "$epoch" ]; then
    printf '%s\n' '-'
    return 0
  fi
  date -u -d "@$epoch" +%Y-%m-%dT%H:%M:%SZ
}

join_flags() {
  local class=$1
  shift
  local sorted=""
  if [ "$#" -gt 0 ]; then
    sorted=$(printf '%s\n' "$@" | sort | paste -sd, -)
  fi
  if [ -n "$sorted" ]; then
    printf '%s,%s\n' "$class" "$sorted"
  else
    printf '%s\n' "$class"
  fi
}

emit_simple() { # path, wt, unp, dirty, scratch, mtime, flags
  ROWS+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' "$1" "$2" "$3" "$4" "$5" "$6" "$7")")
}

census_repo() {
  local repo=$1
  local wt unp dirty skind sbytes mtime class
  local -a details=()
  if ! wt=$(capture_count -C "$repo" worktree list); then
    emit_simple "$repo" - - - - - unreachable
    return 0
  fi
  if ! unp=$(capture_count -C "$repo" log --branches --not --remotes --oneline); then
    emit_simple "$repo" - - - - - unreachable
    return 0
  fi
  if ! dirty=$(capture_count -C "$repo" status --porcelain); then
    emit_simple "$repo" - - - - - unreachable
    return 0
  fi
  local sm
  sm=$(scratch_measure "$repo")
  skind=${sm%%$'\t'*}
  sbytes=${sm#*$'\t'}
  mtime=$(newest_iso "$repo")
  class=OBSERVE
  case "$skind" in
    absent) details+=(scratch-absent) ;;
    dir)
      if [ "$sbytes" != 0 ]; then details+=(scratch); fi
      ;;
    symlink)
      details+=(scratch-symlink)
      class=NOT-SAFE
      ;;
    notdir)
      details+=(scratch-not-dir)
      class=NOT-SAFE
      ;;
    unreadable)
      details+=(scratch-unreadable)
      class=NOT-SAFE
      ;;
  esac
  if [ "${unp:-0}" -gt 0 ]; then
    details+=(unpushed)
    class=NOT-SAFE
  fi
  if [ "${dirty:-0}" -gt 0 ]; then
    details+=(dirty)
    class=NOT-SAFE
  fi
  if [ "${wt:-0}" -gt 1 ]; then
    details+=(extra-worktrees)
  fi
  if ! has_remote "$repo"; then
    details+=(no-remote)
  fi
  if ! has_commits "$repo"; then
    details+=(no-commits)
  fi
  if [ "$class" = OBSERVE ] && [ "${unp:-0}" = 0 ] && [ "${dirty:-0}" = 0 ] \
    && [ "$sbytes" = 0 ] && [ "${wt:-0}" -le 1 ] && has_remote "$repo" && has_commits "$repo"; then
    details+=(clean)
  fi
  local flags
  flags=$(join_flags "$class" "${details[@]}")
  emit_simple "$repo" "$wt" "$unp" "$dirty" "$sbytes" "$mtime" "$flags"
}

build_rows() {
  local root=$1 d
  ROWS=()
  root=$(canon "$root")
  if is_secret_shaped "$root"; then
    emit_simple "$root" - - - - - secrets-refusal
    return 0
  fi
  if is_primary_repo "$root"; then
    census_repo "$root"
  fi
  shopt -s nullglob
  for d in "$root"/*; do
    [ -d "$d" ] || continue
    [ -L "$d" ] && continue
    d=$(canon "$d")
    if is_secret_shaped "$d"; then
      emit_simple "$d" - - - - - secrets-refusal
      continue
    fi
    if is_primary_repo "$d"; then
      census_repo "$d"
    fi
  done
  shopt -u nullglob
}

print_census() {
  printf 'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags\n'
  if [ "${#ROWS[@]}" -eq 0 ]; then
    return 0
  fi
  printf '%s\n' "${ROWS[@]}" | sort
}

san() {
  local s=${1:-}
  s=${s//$'\t'/,}
  s=${s//$'\r'/}
  s=${s//$'\n'/}
  printf '%s' "$s"
}

num_delta() {
  awk -v b="$1" -v a="$2" 'BEGIN{
    if (b ~ /^-?[0-9]+$/ && a ~ /^-?[0-9]+$/) printf "%d\n", a-b;
    else printf "incomparable\n";
  }'
}

do_compare() {
  local prev=$1 line header expected n=0
  local -a before_repos=() after_repos=()
  declare -A BWT=() BUN=() BDI=() BSC=() BMT=() BFL=()
  declare -A AWT=() AUN=() ADI=() ASC=() AMT=() AFL=()
  declare -A SEENB=() SEENA=()
  expected=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'
  printf 'repo\tfield\tbefore\tafter\tdelta\n'
  if [ ! -f "$prev" ]; then
    printf 'souji-census.impl-48: compare file missing: %s\n' "$prev" >&2
    exit 1
  fi
  IFS= read -r header < "$prev" || header=""
  header=${header%$'\r'}
  if [ "$header" != "$expected" ]; then
    printf '*\tschema\t%s\t%s\tincomparable\n' "$(san "$header")" "$(san "$expected")"
    return 0
  fi
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n+1))
    [ "$n" -eq 1 ] && continue
    line=${line%$'\r'}
    [ -n "$line" ] || continue
    local repo wt unp dirty scratch mtime flags
    IFS=$'\t' read -r repo wt unp dirty scratch mtime flags <<< "$line"
    [ -n "$repo" ] || continue
    if [ -n "${SEENB[$repo]:-}" ]; then
      printf '%s\tduplicate\t%s\t%s\tincomparable\n' "$repo" "${SEENB[$repo]}" "$n"
    fi
    SEENB[$repo]=$n
    BWT[$repo]=$wt
    BUN[$repo]=$unp
    BDI[$repo]=$dirty
    BSC[$repo]=$scratch
    BMT[$repo]=$mtime
    BFL[$repo]=$flags
    before_repos+=("$repo")
  done < "$prev"
  local row
  for row in "${ROWS[@]+"${ROWS[@]}"}"; do
    local repo wt unp dirty scratch mtime flags
    IFS=$'\t' read -r repo wt unp dirty scratch mtime flags <<< "$row"
    SEENA[$repo]=1
    AWT[$repo]=$wt
    AUN[$repo]=$unp
    ADI[$repo]=$dirty
    ASC[$repo]=$scratch
    AMT[$repo]=$mtime
    AFL[$repo]=$flags
    after_repos+=("$repo")
  done
  local -a all=()
  local k
  for k in "${before_repos[@]+"${before_repos[@]}"}" "${after_repos[@]+"${after_repos[@]}"}"; do
    [ -n "$k" ] || continue
    all+=("$k")
  done
  if [ "${#all[@]}" -eq 0 ]; then
    return 0
  fi
  local repo_sorted
  repo_sorted=$(printf '%s\n' "${all[@]}" | sort -u)
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    local in_b=0 in_a=0
    [ -n "${SEENB[$repo]:-}" ] && in_b=1
    [ -n "${SEENA[$repo]:-}" ] && in_a=1
    if [ "$in_b" = 1 ] && [ "$in_a" = 0 ]; then
      printf '%s\tpresence\tpresent\tabsent\tremoved\n' "$repo"
      continue
    fi
    if [ "$in_b" = 0 ] && [ "$in_a" = 1 ]; then
      printf '%s\tpresence\tabsent\tpresent\tadded\n' "$repo"
      continue
    fi
    local field b a d
    for field in worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags; do
      case "$field" in
        worktrees) b=${BWT[$repo]}; a=${AWT[$repo]} ;;
        unpushed) b=${BUN[$repo]}; a=${AUN[$repo]} ;;
        dirty) b=${BDI[$repo]}; a=${ADI[$repo]} ;;
        scratch_bytes) b=${BSC[$repo]}; a=${ASC[$repo]} ;;
        mtime_iso) b=${BMT[$repo]}; a=${AMT[$repo]} ;;
        verdict_flags) b=${BFL[$repo]}; a=${AFL[$repo]} ;;
      esac
      [ "$b" = "$a" ] && continue
      case "$field" in
        mtime_iso|verdict_flags) d=changed ;;
        *) d=$(num_delta "$b" "$a") ;;
      esac
      printf '%s\t%s\t%s\t%s\t%s\n' "$repo" "$field" "$b" "$a" "$d"
    done
  done <<< "$repo_sorted"
}

run_selftest() {
  local fx repo tree c c2 out err rc
  local passes=0 fails=0
  fx=$(mktemp -d "${TMPDIR:-/tmp}/souji-census-48.XXXXXX")
  # shellcheck disable=SC2064
  trap "rm -rf -- $(printf '%q' "$fx")" RETURN
  export GIT_AUTHOR_NAME=fixture
  export GIT_AUTHOR_EMAIL=fixture@example.invalid
  export GIT_COMMITTER_NAME=fixture
  export GIT_COMMITTER_EMAIL=fixture@example.invalid
  export GIT_AUTHOR_DATE=2020-01-02T03:04:05Z
  export GIT_COMMITTER_DATE=2020-01-02T03:04:05Z

  plumb() { git --no-optional-locks -C "$1" "$2" "${@:3}"; }

  make_repo() { # $1 path, $2 mode: remote|ahead|noremote|empty
    local path=$1 mode=$2 tree c
    mkdir -p -- "$path"
    git init -q -b master "$path"
    if [ "$mode" = empty ]; then
      return 0
    fi
    printf 'tracked\n' > "$path/tracked.txt"
    touch -d '2020-01-02T03:04:05Z' -- "$path/tracked.txt"
    git -C "$path" add tracked.txt
    tree=$(plumb "$path" write-tree)
    c=$(plumb "$path" commit-tree "$tree" -m c1)
    git -C "$path" update-ref refs/heads/master "$c"
    if [ "$mode" = noremote ]; then
      return 0
    fi
    git -C "$path" update-ref refs/remotes/origin/master "$c"
    git -C "$path" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
    if [ "$mode" = ahead ]; then
      printf 'ahead\n' > "$path/tracked.txt"
      touch -d '2020-01-02T03:04:05Z' -- "$path/tracked.txt"
      git -C "$path" add tracked.txt
      tree=$(plumb "$path" write-tree)
      c2=$(plumb "$path" commit-tree "$tree" -p "$c" -m c2)
      git -C "$path" update-ref refs/heads/master "$c2"
    fi
  }

  ok() { printf 'PASS %s\n' "$1"; passes=$((passes+1)); }
  bad() { printf 'FAIL %s\n' "$1" >&2; fails=$((fails+1)); }

  make_repo "$fx/clean-repo" remote
  make_repo "$fx/live-repo" ahead
  make_repo "$fx/spaced repo" remote
  make_repo "$fx/noremote-repo" noremote
  make_repo "$fx/empty-repo" empty
  make_repo "$fx/secrets-repo" remote
  printf 'CANARY-SECRET-BYTES\n' > "$fx/secrets-repo/canary.txt"
  mkdir -p -- "$fx/live-repo/.scratch"
  printf 'scratch' > "$fx/live-repo/.scratch/blob"
  touch -d '2024-06-01T00:00:00Z' -- "$fx/live-repo/.scratch/blob"
  printf 'x' > "$fx/live-repo/untracked.txt"
  touch -d '2020-01-02T03:04:05Z' -- "$fx/live-repo/untracked.txt"
  mkdir -p -- "$fx/outside-scratch"
  printf 'CANARY-OUTSIDE\n' > "$fx/outside-scratch/canary.txt"
  make_repo "$fx/link-repo" remote
  ln -s "$fx/outside-scratch" "$fx/link-repo/.scratch"
  printf 'CANARY-IDRSA\n' > "$fx/clean-repo/id_rsa"
  touch -d '2020-01-02T03:04:05Z' -- "$fx/clean-repo/id_rsa"
  local tip
  tip=$(git -C "$fx/clean-repo" rev-parse HEAD)
  git -C "$fx/clean-repo" worktree add --detach "$fx/wt-clean" "$tip" >/dev/null
  # freeze mtimes after worktree add
  touch -d '2020-01-02T03:04:05Z' -- "$fx/clean-repo/tracked.txt" "$fx/spaced repo/tracked.txt" \
    "$fx/noremote-repo/tracked.txt" "$fx/link-repo/tracked.txt"

  local idx_before
  idx_before=$(stat -c '%y' -- "$fx/clean-repo/.git/index")

  set +e
  out=$(bash "$SELF" --root "$fx" 2>"$fx/err")
  rc=$?
  set -e
  err=$(cat "$fx/err" || true)
  if [ "$rc" = 0 ]; then ok "census-exit-0"; else bad "census-exit-0 rc=$rc err=$err"; fi
  if [ -z "$err" ]; then ok "census-stderr-empty"; else bad "census-stderr-empty err=$err"; fi

  local header
  header=$(printf '%s\n' "$out" | head -1)
  if [ "$header" = $'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags' ]; then
    ok "header"
  else
    bad "header got=$(printf '%s' "$header" | sed 's/\t/|/g')"
  fi
  local badnf
  badnf=$(printf '%s\n' "$out" | awk -F'\t' 'NR>1 && NF!=7 {print NR}')
  if [ -z "$badnf" ]; then ok "seven-columns"; else bad "seven-columns lines=$badnf"; fi

  row_of() {
    printf '%s\n' "$out" | awk -F'\t' -v p="$1" 'NR>1 && $1==p {print; exit}'
  }
  field() { # $1 row, $2 1-based
    printf '%s\n' "$1" | awk -F'\t' -v n="$2" '{print $n}'
  }

  local row wt unp dirty scratch mtime flags
  row=$(row_of "$fx/clean-repo")
  wt=$(field "$row" 2); unp=$(field "$row" 3); dirty=$(field "$row" 4)
  scratch=$(field "$row" 5); mtime=$(field "$row" 6); flags=$(field "$row" 7)
  if [ "$wt" = 2 ] && [ "$unp" = 0 ] && [ "$dirty" = 1 ] && [ "$scratch" = 0 ]; then
    ok "clean-counts wt=$wt unp=$unp dirty=$dirty scratch=$scratch"
  else
    bad "clean-counts wt=$wt unp=$unp dirty=$dirty scratch=$scratch flags=$flags"
  fi
  # id_rsa is untracked, so dirty=1 and NOT-SAFE is correct; the canary must not be read.
  case "$flags" in
    NOT-SAFE,*dirty*) ok "clean-flags-dirty-from-idrsa" ;;
    *) bad "clean-flags-dirty-from-idrsa flags=$flags" ;;
  esac
  case "$flags" in
    *extra-worktrees*) ok "clean-extra-worktrees" ;;
    *) bad "clean-extra-worktrees flags=$flags" ;;
  esac
  if printf '%s\n' "$out" | grep -q 'CANARY-IDRSA'; then bad "idrsa-content-leaked"; else ok "idrsa-content-unread"; fi

  row=$(row_of "$fx/live-repo")
  wt=$(field "$row" 2); unp=$(field "$row" 3); dirty=$(field "$row" 4)
  scratch=$(field "$row" 5); mtime=$(field "$row" 6); flags=$(field "$row" 7)
  local expect_scratch expect_dirty
  expect_scratch=$(du -sb -- "$fx/live-repo/.scratch" | awk '{print $1}')
  expect_dirty=$(git -C "$fx/live-repo" status --porcelain | wc -l | tr -d '[:space:]')
  if [ "$unp" = 1 ] && [ "$dirty" = "$expect_dirty" ] && [ "$scratch" = "$expect_scratch" ] \
    && [ "$mtime" = "2024-06-01T00:00:00Z" ]; then
    ok "live-counts unp=$unp dirty=$dirty scratch=$scratch mtime=$mtime"
  else
    bad "live-counts unp=$unp dirty=$dirty scratch=$scratch mtime=$mtime expect_dirty=$expect_dirty expect_scratch=$expect_scratch"
  fi
  if [ "$flags" = "NOT-SAFE,dirty,scratch,unpushed" ]; then
    ok "live-flags"
  else
    bad "live-flags flags=$flags"
  fi

  row=$(row_of "$fx/spaced repo")
  flags=$(field "$row" 7)
  mtime=$(field "$row" 6)
  if [ "$(field "$row" 2)" = 1 ] && [ "$(field "$row" 3)" = 0 ] && [ "$(field "$row" 4)" = 0 ] \
    && [ "$flags" = "OBSERVE,clean,scratch-absent" ] && [ "$mtime" = "2020-01-02T03:04:05Z" ]; then
    ok "spaced-clean"
  else
    bad "spaced-clean row=$row"
  fi

  row=$(row_of "$fx/noremote-repo")
  if [ "$(field "$row" 3)" = 1 ] && [ "$(field "$row" 7)" = "NOT-SAFE,no-remote,scratch-absent,unpushed" ]; then
    ok "noremote"
  else
    bad "noremote row=$row"
  fi

  row=$(row_of "$fx/empty-repo")
  if [ "$(field "$row" 2)" = 1 ] && [ "$(field "$row" 3)" = 0 ] && [ "$(field "$row" 4)" = 0 ] \
    && [ "$(field "$row" 7)" = "OBSERVE,no-commits,no-remote,scratch-absent" ]; then
    ok "empty-repo"
  else
    bad "empty-repo row=$row"
  fi

  row=$(row_of "$fx/secrets-repo")
  if [ "$(field "$row" 2)" = "-" ] && [ "$(field "$row" 7)" = "secrets-refusal" ]; then
    ok "secrets-refusal"
  else
    bad "secrets-refusal row=$row"
  fi
  if printf '%s\n' "$out" "$err" | grep -q 'CANARY-SECRET-BYTES'; then
    bad "secret-canary-leaked"
  else
    ok "secret-canary-unread"
  fi

  row=$(row_of "$fx/link-repo")
  flags=$(field "$row" 7)
  scratch=$(field "$row" 5)
  case "$flags" in
    *scratch-symlink*) ok "scratch-symlink-flag" ;;
    *) bad "scratch-symlink-flag flags=$flags" ;;
  esac
  if [ "$scratch" = "-" ]; then ok "scratch-symlink-not-followed"; else bad "scratch-symlink-bytes=$scratch"; fi
  if printf '%s\n' "$out" "$err" | grep -q 'CANARY-OUTSIDE'; then
    bad "outside-canary-leaked"
  else
    ok "outside-canary-unread"
  fi

  # Prove the census itself did not rewrite the index. A later hand check
  # uses plain git status, which may refresh the index; measure before that.
  local idx_after
  idx_after=$(stat -c '%y' -- "$fx/clean-repo/.git/index")
  if [ "$idx_before" = "$idx_after" ] && [ ! -e "$fx/clean-repo/.git/index.lock" ]; then
    ok "index-untouched"
  else
    bad "index-untouched before=$idx_before after=$idx_after"
  fi

  # independent hand-check equality on non-refused repos
  local name hand_wt hand_unp hand_dirty tool_row mismatch=0
  for name in "clean-repo" "live-repo" "spaced repo" "noremote-repo" "empty-repo" "link-repo"; do
    hand_wt=$(git -C "$fx/$name" worktree list | wc -l | tr -d '[:space:]')
    hand_unp=$(git -C "$fx/$name" log --branches --not --remotes --oneline | wc -l | tr -d '[:space:]')
    hand_dirty=$(git -C "$fx/$name" status --porcelain | wc -l | tr -d '[:space:]')
    tool_row=$(row_of "$fx/$name")
    if [ "$(field "$tool_row" 2)" != "$hand_wt" ] || [ "$(field "$tool_row" 3)" != "$hand_unp" ] \
      || [ "$(field "$tool_row" 4)" != "$hand_dirty" ]; then
      mismatch=1
      bad "handcheck $name tool=$(field "$tool_row" 2),$(field "$tool_row" 3),$(field "$tool_row" 4) hand=$hand_wt,$hand_unp,$hand_dirty"
    fi
  done
  if [ "$mismatch" = 0 ]; then ok "handcheck-all"; fi

  # no removal token
  if printf '%s\n' "$out" | awk -F'\t' 'NR>1 {
      n=split($7,a,",");
      for(i=1;i<=n;i++) if(a[i]=="SAFE") bad=1
    } END{exit bad?1:0}'; then
    ok "never-SAFE"
  else
    bad "never-SAFE"
  fi

  # repeatability
  local out2
  out2=$(bash "$SELF" --root "$fx")
  if [ "$out" = "$out2" ]; then ok "repeatable"; else bad "repeatable"; fi

  # compare identical
  printf '%s\n' "$out" > "$fx/prev.tsv"
  local cmp
  set +e
  cmp=$(bash "$SELF" --root "$fx" --compare "$fx/prev.tsv" 2>"$fx/cerr")
  rc=$?
  set -e
  if [ "$rc" = 0 ] && [ "$(printf '%s\n' "$cmp" | wc -l | tr -d '[:space:]')" = 1 ]; then
    ok "compare-identical"
  else
    bad "compare-identical rc=$rc lines=$(printf '%s\n' "$cmp" | wc -l) body=$cmp"
  fi

  printf 'new\n' > "$fx/spaced repo/new.txt"
  touch -d '2021-01-01T00:00:00Z' -- "$fx/spaced repo/new.txt"
  set +e
  cmp=$(bash "$SELF" --root "$fx" --compare "$fx/prev.tsv" 2>"$fx/cerr")
  rc=$?
  set -e
  local dline
  dline=$(printf '%s\n' "$cmp" | awk -F'\t' -v p="$fx/spaced repo" '$1==p && $2=="dirty" {print; exit}')
  if [ "$rc" = 0 ] && [ "$(field "$dline" 3)" = 0 ] && [ "$(field "$dline" 4)" = 1 ] && [ "$(field "$dline" 5)" = 1 ]; then
    ok "compare-dirty-delta"
  else
    bad "compare-dirty-delta rc=$rc line=$dline"
  fi
  if printf '%s\n' "$cmp" | awk -F'\t' -v p="$fx/spaced repo" '$1==p && $2=="mtime_iso" && $5=="changed" {found=1} END{exit found?0:1}'; then
    ok "compare-mtime-changed"
  else
    bad "compare-mtime-changed"
  fi

  printf 'seat\tpath\nfoo\tbar\n' > "$fx/foreign.tsv"
  set +e
  cmp=$(bash "$SELF" --root "$fx" --compare "$fx/foreign.tsv" 2>"$fx/cerr")
  rc=$?
  set -e
  if [ "$rc" = 0 ] && printf '%s\n' "$cmp" | awk -F'\t' 'NR==2 && $1=="*" && $2=="schema" && $5=="incomparable" {ok=1} END{exit ok?0:1}'; then
    ok "compare-foreign-schema"
  else
    bad "compare-foreign-schema rc=$rc cmp=$cmp"
  fi

  set +e
  bash "$SELF" --not-a-flag >/dev/null 2>&1
  rc=$?
  set -e
  if [ "$rc" = 2 ]; then ok "usage-exit-2"; else bad "usage-exit-2 rc=$rc"; fi

  set +e
  bash "$SELF" --compare >/dev/null 2>&1
  rc=$?
  set -e
  if [ "$rc" = 2 ]; then ok "compare-missing-arg-exit-2"; else bad "compare-missing-arg-exit-2 rc=$rc"; fi

  set +e
  bash "$SELF" --root "$fx/does-not-exist" >/dev/null 2>&1
  rc=$?
  set -e
  if [ "$rc" = 1 ]; then ok "missing-root-exit-1"; else bad "missing-root-exit-1 rc=$rc"; fi

  set +e
  bash "$SELF" --root / >/dev/null 2>&1
  rc=$?
  set -e
  if [ "$rc" = 1 ]; then ok "refuse-slash"; else bad "refuse-slash rc=$rc"; fi

  # worktree checkout is not a primary repo row
  if printf '%s\n' "$out" | awk -F'\t' -v p="$fx/wt-clean" 'NR>1 && $1==p {found=1} END{exit found?1:0}'; then
    ok "worktree-not-a-row"
  else
    bad "worktree-not-a-row"
  fi

  # forbidden contiguous verb phrases must not appear in this file
  local verb hit=0
  for verb in fetch push commit branch prune reset rebase checkout rm; do
    if grep -q -F -- "git ${verb}" "$SELF"; then
      hit=1
      bad "forbidden-phrase git ${verb}"
    fi
  done
  if [ "$hit" = 0 ]; then ok "no-forbidden-phrases"; fi

  printf 'selftest: %s/%s\n' "$passes" "$((passes+fails))"
  if [ "$fails" -gt 0 ]; then
    return 1
  fi
  return 0
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --compare)
      [ "$#" -ge 2 ] || usage_err "--compare needs a TSV path"
      COMPARE=1
      PREV=$2
      shift 2
      ;;
    --root)
      [ "$#" -ge 2 ] || usage_err "--root needs a path"
      ROOT=$2
      ROOT_SET=1
      shift 2
      ;;
    --help|-h) usage 0 ;;
    --) shift; break ;;
    -*) usage_err "unknown option: $1" ;;
    *)
      if [ -n "$ROOT" ]; then usage_err "unexpected argument: $1"; fi
      ROOT=$1
      ROOT_SET=1
      shift
      ;;
  esac
done
if [ "$#" -gt 0 ]; then usage_err "unexpected argument: $1"; fi
if [ "$SELFTEST" = 1 ]; then
  [ "$COMPARE" = 0 ] && [ "$ROOT_SET" = 0 ] || usage_err "--selftest takes no other arguments"
  if run_selftest; then exit 0; else exit 1; fi
fi
if [ -z "$ROOT" ]; then ROOT=$DEFAULT_ROOT; fi
ROOT=$(canon "$ROOT")
if [ "$ROOT" = "/" ]; then
  printf 'souji-census.impl-48: refusing to scan /\n' >&2
  exit 1
fi
refuse_path root "$ROOT"
if [ ! -d "$ROOT" ]; then
  printf 'souji-census.impl-48: root not a directory: %s\n' "$ROOT" >&2
  exit 1
fi
if [ "$COMPARE" = 1 ]; then
  refuse_path "compare file" "$PREV"
  if [ ! -f "$PREV" ]; then
    printf 'souji-census.impl-48: compare file missing: %s\n' "$PREV" >&2
    exit 1
  fi
fi
build_rows "$ROOT"
if [ "$COMPARE" = 1 ]; then
  do_compare "$PREV"
else
  print_census
fi
exit 0
