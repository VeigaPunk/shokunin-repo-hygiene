#!/usr/bin/env bash
# souji-census — repeatable read-only fleet census (round 6, seat S33).
#
# One bash tool; bash + coreutils + git only. Never fetches, never writes
# outside a --selftest mktemp, never reads secret-shaped files, never
# touches .ufo/state or .ufo/watchdog.log.
#
# CLI
#   tools/souji-census.impl-33.sh [--root DIR] [--compare PREV.tsv]
#                                 [--include-root] [--selftest]
#
# Default scan: every immediate child of $SHOKUNIN_ROOT (or --root) whose
# .git is a directory (a main repo, not a linked work tree or submodule
# gitfile). Linked work trees are counted on their owner via `worktree list`,
# not emitted as their own row. --include-root also emits a row for the root
# itself when it is a main repo.
#
# Census TSV (header + one row per repo, LC_ALL=C path sort):
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
#
#   repo            absolute canonical path
#   worktrees       `git worktree list` line count (main work tree included)
#   unpushed        commits on any local branch not reachable from any
#                   remote-tracking ref (`git rev-list --count --branches
#                   --not --remotes`). If the repo has zero refs/remotes/*,
#                   the count is every local commit and verdict_flags includes
#                   no-remote (pushedness unverifiable — same rule as
#                   souji-verify). The number is still reported, and unpushed
#                   is also set when that count is > 0.
#   dirty           `git status --porcelain` line count on the main work tree
#                   only (default untracked mode: a wholly untracked directory
#                   is one line, matching souji-verify). Other work trees are
#                   not added into this number; see wt-dirty.
#   scratch_bytes   apparent byte size of <repo>/.scratch (`du -sb -P`; 0 if
#                   absent or a symlink). Does not follow symlinks.
#   mtime_iso       newest regular-file mtime under the main work tree,
#                   ISO-8601 with numeric offset, second resolution. .git,
#                   .ufo/state, and .ufo/watchdog.log are pruned and never
#                   stat'd. Secret-shaped names are flagged and excluded from
#                   the max. File contents are never opened.
#   verdict_flags   comma-joined, stable order, subset of:
#                     clean | dirty | unpushed | no-remote | scratch |
#                     secret-shaped | wt-absent | wt-dirty |
#                     status-unverifiable | not-a-repo | error
#                   "clean" only when unpushed=0, dirty=0, and a remote
#                     tracking ref exists. no-remote replaces a false "clean".
#                   wt-absent: a non-main worktree registration whose directory
#                     is missing (metadata only; not a separate row).
#                   wt-dirty: a non-main worktree directory is present and its
#                     own `git status --porcelain` is non-empty.
#
# --compare PREV.tsv
#   Reads a previous census (header required, same columns). Emits a diff
#   TSV on stdout:
#     repo  field  before  after  change
#   One row per changed numeric/text field, plus rows for added/removed
#   repos (field=repo, before/after = ABSENT or PRESENT). Exit 0 when the
#   diff is header-only; exit 3 when any row differs. Census rows are not
#   mixed into the diff.
#
# --selftest
#   Builds a fixture fleet under mktemp -d, runs the census twice (byte-
#   identical), mutates one fixture, and checks --compare. Removes the
#   fixture tree on exit. Exit 0 on pass, 1 on fail.
#
# Env
#   SHOKUNIN_ROOT   default root when --root is omitted
#                   (default: parent of this repo)
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true
# status/diff must not refresh the index (that write is an optional lock).
export GIT_OPTIONAL_LOCKS=0

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

usage() {
  sed -n '2,68p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

usage_err() { printf 'souji-census: %s\n' "$1" >&2; usage 2; }

canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

sanitize_field() {
  local s=$1
  s=${s//$'\t'/ }
  s=${s//$'\n'/ }
  s=${s//$'\r'/ }
  printf '%s' "$s"
}

# --- measurements (read-only) ----------------------------------------------

count_worktrees() { # $1 repo
  local n
  n=$(git -C "$1" worktree list 2>/dev/null | grep -c . || true)
  printf '%s' "${n// /}"
}

count_unpushed() { # $1 repo; prints "count<TAB>no-remote|has-remote"
  local repo=$1 nremotes n
  nremotes=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null \
    | grep -c . || true)
  nremotes=${nremotes// /}
  if [ "${nremotes:-0}" = 0 ]; then
    n=$(git -C "$repo" rev-list --count --branches 2>/dev/null || printf '0')
    printf '%s\tno-remote' "${n// /}"
    return 0
  fi
  n=$(git -C "$repo" rev-list --count --branches --not --remotes 2>/dev/null || printf '0')
  printf '%s\thas-remote' "${n// /}"
}

count_dirty() { # $1 repo; prints "count" or "unverifiable"
  local st
  # Pathspec-exclude the off-limits driver surfaces so status does not walk
  # them. A wholly untracked directory elsewhere still collapses to one line.
  if ! st=$(git -C "$1" --no-optional-locks status --porcelain -- . \
      ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log' 2>/dev/null); then
    printf 'unverifiable'
    return 0
  fi
  if [ -z "$st" ]; then printf '0'; return 0; fi
  printf '%s' "$(printf '%s\n' "$st" | grep -c . || true)"
}

scratch_bytes() { # $1 repo
  local d="$1/.scratch"
  if [ ! -e "$d" ] && [ ! -L "$d" ]; then printf '0'; return 0; fi
  if [ -L "$d" ]; then printf '0'; return 0; fi
  if [ ! -d "$d" ]; then printf '0'; return 0; fi
  # du -sb sums apparent size; -P does not follow symlinks inside .scratch.
  local line bytes
  line=$(du -sb -P -- "$d" 2>/dev/null | head -1 || true)
  bytes=${line%%[[:space:]]*}
  case "$bytes" in
    ''|*[!0-9]*) printf '0' ;;
    *) printf '%s' "$bytes" ;;
  esac
}

# Newest regular file under the work tree. One find|awk pass (no per-file
# stat spawn — kotodama .scratch is hundreds of thousands of files). Prints:
#   iso<TAB>secret-shaped|ok     or empty iso when no eligible file.
# File contents are never opened. .git, .ufo/state, .ufo/watchdog.log pruned.
newest_mtime() {
  local repo=$1 raw epoch secret iso
  # pipefail is off only for this pipeline: a permission error in find must
  # not abort the census. awk still emits a row.
  set +e
  set +o pipefail
  raw=$(cd -- "$repo" && find . \
      \( -name .git -o -path './.ufo/state' -o -path './.ufo/watchdog.log' \) -prune \
      -o -type f -printf '%T@ %P\0' 2>/dev/null \
      | awk '
        BEGIN { RS="\0"; max=0; sec=0 }
        function secret_comp(c,    lc) {
          lc = tolower(c)
          if (lc == ".envrc") return 1
          if (lc ~ /\.env$/) return 1
          if (lc ~ /^\.env\./) return 1
          if (lc ~ /credential/ || lc ~ /secret/) return 1
          if (lc ~ /^id_/ || lc ~ /\.pem$/) return 1
          return 0
        }
        function secret_path(p,    n, i, a) {
          n = split(p, a, "/")
          for (i = 1; i <= n; i++) if (secret_comp(a[i])) return 1
          return 0
        }
        {
          if ($0 == "") next
          ep = $0; sub(/ .*/, "", ep)
          p = $0; sub(/^[^ ]+ /, "", p)
          if (p == "") next
          if (secret_path(p)) { sec = 1; next }
          if (ep+0 > max) max = ep+0
        }
        END { printf "%d\t%s\n", int(max), (sec ? "secret-shaped" : "ok") }
      ')
  set -o pipefail
  set -e
  epoch=${raw%%$'\t'*}
  secret=${raw#*$'\t'}
  secret=${secret%%$'\n'*}
  case "$epoch" in
    ''|*[!0-9]*) epoch=0; secret=${secret:-ok} ;;
  esac
  if [ "$epoch" = 0 ]; then
    iso=""
  else
    iso=$(date -d "@$epoch" --iso-8601=seconds 2>/dev/null || true)
  fi
  if [ "$secret" = secret-shaped ]; then
    printf '%s\tsecret-shaped' "$iso"
  else
    printf '%s\tok' "$iso"
  fi
}

# Non-main worktree side flags. Prints zero or more of: wt-absent wt-dirty
# separated by spaces. Does not status a missing directory.
worktree_extra_flags() {
  local repo=$1 line path crepo cpath saw_absent=0 saw_dirty=0 d
  crepo=$(canon_path "$repo")
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      'worktree '*) path=${line#worktree } ;;
      *) continue ;;
    esac
    [ -n "$path" ] || continue
    cpath=$(canon_path "$path")
    [ "$cpath" = "$crepo" ] && continue
    if [ ! -d "$path" ]; then
      saw_absent=1
      continue
    fi
    d=$(count_dirty "$path")
    if [ "$d" = unverifiable ] || [ "${d:-0}" -gt 0 ]; then
      saw_dirty=1
    fi
  done < <(git -C "$repo" worktree list --porcelain 2>/dev/null || true)
  local out=""
  [ "$saw_absent" = 1 ] && out="wt-absent"
  [ "$saw_dirty" = 1 ] && out="${out:+$out }wt-dirty"
  printf '%s' "$out"
}

# Emit one TSV row (no newline issues; fields already sanitized).
census_one() { # $1 repo-dir
  local repo
  repo=$(canon_path "$1")
  if [ ! -e "$repo/.git" ] && [ ! -d "$repo/.git" ]; then
    # Linked work trees have a .git file; bare dirs are not repos.
    if [ ! -e "$repo/.git" ]; then
      printf '%s\t0\t0\t0\t0\t\tnot-a-repo\n' "$(sanitize_field "$repo")"
      return 0
    fi
  fi
  if ! git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '%s\t0\t0\t0\t0\t\terror\n' "$(sanitize_field "$repo")"
    return 0
  fi

  local wt unp_line unp remote_flag dirty scratch mt_line iso secret_flag wt_extra
  local -a flags=()
  wt=$(count_worktrees "$repo")
  unp_line=$(count_unpushed "$repo")
  unp=${unp_line%%$'\t'*}
  remote_flag=${unp_line#*$'\t'}
  dirty=$(count_dirty "$repo")
  scratch=$(scratch_bytes "$repo")
  wt_extra=$(worktree_extra_flags "$repo")
  mt_line=$(newest_mtime "$repo")
  iso=${mt_line%%$'\t'*}
  secret_flag=${mt_line#*$'\t'}

  case "$wt" in ''|*[!0-9]*) wt=0; flags+=(error) ;; esac
  case "$unp" in ''|*[!0-9]*) unp=0; flags+=(error) ;; esac
  case "$scratch" in ''|*[!0-9]*) scratch=0; flags+=(error) ;; esac

  if [ "$remote_flag" = no-remote ]; then flags+=(no-remote); fi
  if [ "${unp:-0}" -gt 0 ]; then flags+=(unpushed); fi
  case "$wt_extra" in
    *wt-absent*) flags+=(wt-absent) ;;
  esac
  case "$wt_extra" in
    *wt-dirty*) flags+=(wt-dirty) ;;
  esac
  if [ "$dirty" = unverifiable ]; then
    dirty=0
    flags+=(status-unverifiable)
  elif [ "${dirty:-0}" -gt 0 ]; then
    flags+=(dirty)
  fi
  if [ "${scratch:-0}" -gt 0 ]; then flags+=(scratch); fi
  if [ "$secret_flag" = secret-shaped ]; then flags+=(secret-shaped); fi

  local has_problem=0 f
  for f in "${flags[@]+"${flags[@]}"}"; do
    case "$f" in
      dirty|unpushed|no-remote|status-unverifiable|error|not-a-repo) has_problem=1 ;;
    esac
  done
  if [ "$has_problem" = 0 ]; then flags+=(clean); fi

  # Stable flag order.
  local ordered=""
  local name
  for name in clean dirty unpushed no-remote scratch secret-shaped wt-absent wt-dirty status-unverifiable not-a-repo error; do
    for f in "${flags[@]+"${flags[@]}"}"; do
      if [ "$f" = "$name" ]; then
        if [ -z "$ordered" ]; then ordered=$name; else ordered="$ordered,$name"; fi
      fi
    done
  done

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(sanitize_field "$repo")" "$wt" "$unp" "$dirty" "$scratch" \
    "$(sanitize_field "$iso")" "$(sanitize_field "$ordered")"
}

list_repos() { # prints repo dirs, one per line, basename-sorted
  local root=$1
  local -a found=()
  local d base
  if [ "$INCLUDE_ROOT" = 1 ] && [ -d "$root" ] && [ -e "$root/.git" ]; then
    found+=("$root")
  fi
  shopt -s nullglob
  for d in "$root"/*/; do
    [ -d "$d" ] || continue
    # skip the root's own .git and dot-dirs (operator config, .ufo, .scratch)
    base=$(basename -- "$d")
    case "$base" in
      .*) continue ;;
    esac
    # .git file => linked work tree or submodule gitfile. Those are not
    # independent fleet repos; the owner's worktree list already counts them.
    if [ -d "${d%/}/.git" ]; then
      found+=("${d%/}")
    fi
  done
  shopt -u nullglob
  if [ "${#found[@]}" -eq 0 ]; then return 0; fi
  local p
  for p in "${found[@]}"; do printf '%s\n' "$p"; done | LC_ALL=C sort
}

emit_census() {
  local root
  root=$(canon_path "$ROOT")
  [ -d "$root" ] || { printf 'souji-census: root is not a directory: %s\n' "$root" >&2; exit 1; }
  printf '%s\n' "$HEADER"
  local repo
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    census_one "$repo"
  done < <(list_repos "$root")
}

# --- compare ---------------------------------------------------------------

# Load a census TSV into parallel arrays keyed by repo. Caller supplies the
# namerefs. Malformed input is a hard error (exit 2) — a compare against a
# corrupt previous census must not look like "no diff".
load_census() { # $1 file, $2 assoc-nameref of "repo -> rest-of-row"
  local file=$1
  local -n _map=$2
  [ -f "$file" ] || usage_err "compare file not found: $file"
  local line n=0 repo rest
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1))
    line=${line%$'\r'}
    [ -n "$line" ] || continue
    if [ "$n" = 1 ]; then
      if [ "$line" != "$HEADER" ]; then
        usage_err "compare file header mismatch (want 7 census columns)"
      fi
      continue
    fi
    repo=${line%%$'\t'*}
    rest=${line#*$'\t'}
    [ -n "$repo" ] || usage_err "compare file: empty repo on line $n"
    if [ -n "${_map[$repo]+x}" ]; then
      usage_err "compare file: duplicate repo $repo"
    fi
    _map["$repo"]=$rest
  done < "$file"
}

field_at() { # $1 rest-of-row (6 fields), $2 1-based index among those 6
  local rest=$1 idx=$2 i=1 part
  while [ "$i" -le 6 ]; do
    if [ "$i" -eq 6 ]; then
      part=$rest
    else
      part=${rest%%$'\t'*}
      rest=${rest#*$'\t'}
    fi
    if [ "$i" -eq "$idx" ]; then printf '%s' "$part"; return 0; fi
    i=$((i + 1))
  done
}

numeric_change() { # $1 before $2 after -> +N / -N / 0
  local b=$1 a=$2
  case "$b" in ''|*[!0-9-]*) printf 'non-numeric'; return 0 ;; esac
  case "$a" in ''|*[!0-9-]*) printf 'non-numeric'; return 0 ;; esac
  local d=$((a - b))
  if [ "$d" -gt 0 ]; then printf '+%s' "$d"
  elif [ "$d" -lt 0 ]; then printf '%s' "$d"
  else printf '0'
  fi
}

emit_compare() { # census of $ROOT vs $COMPARE; writes diff TSV; exit 3 if any change
  local -A before=() after=()
  load_census "$COMPARE" before
  local tmp
  tmp=$(mktemp "${TMPDIR:-/tmp}/souji-census-now.XXXXXX")
  emit_census > "$tmp"
  load_census "$tmp" after
  rm -f -- "$tmp"

  printf '%s\n' "$DIFF_HEADER"
  local changes=0 repo rest_b rest_a
  local -a repos=()
  for repo in "${!before[@]}"; do repos+=("$repo"); done
  for repo in "${!after[@]}"; do
    if [ -z "${before[$repo]+x}" ]; then repos+=("$repo"); fi
  done
  local sorted
  sorted=$(printf '%s\n' "${repos[@]}" | LC_ALL=C sort -u)

  local name i before_v after_v chg
  local -a names=(worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags)
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    if [ -z "${before[$repo]+x}" ]; then
      printf '%s\trepo\tABSENT\tPRESENT\tadded\n' "$(sanitize_field "$repo")"
      changes=$((changes + 1))
      continue
    fi
    if [ -z "${after[$repo]+x}" ]; then
      printf '%s\trepo\tPRESENT\tABSENT\tremoved\n' "$(sanitize_field "$repo")"
      changes=$((changes + 1))
      continue
    fi
    rest_b=${before[$repo]}
    rest_a=${after[$repo]}
    [ "$rest_b" = "$rest_a" ] && continue
    for i in 1 2 3 4 5 6; do
      before_v=$(field_at "$rest_b" "$i")
      after_v=$(field_at "$rest_a" "$i")
      [ "$before_v" = "$after_v" ] && continue
      name=${names[$((i - 1))]}
      case "$name" in
        worktrees|unpushed|dirty|scratch_bytes) chg=$(numeric_change "$before_v" "$after_v") ;;
        *) chg=changed ;;
      esac
      printf '%s\t%s\t%s\t%s\t%s\n' \
        "$(sanitize_field "$repo")" "$name" \
        "$(sanitize_field "$before_v")" "$(sanitize_field "$after_v")" "$chg"
      changes=$((changes + 1))
    done
  done <<< "$sorted"

  if [ "$changes" -gt 0 ]; then return 3; fi
  return 0
}

# --- selftest --------------------------------------------------------------

ST_PASS=0
ST_FAIL=0
ST_TMP=""

st_note() { printf '%s\n' "$*"; }

st_ok() { ST_PASS=$((ST_PASS + 1)); st_note "PASS $*"; }
st_bad() { ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $*"; }

st_commit() { # $1 repo, $2 parent-or-empty, $3 msg -> sha
  local repo=$1 parent=$2 msg=$3 tr sha
  git -C "$repo" add -A >/dev/null
  tr=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr" -p "$parent")
  else
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr")
  fi
  printf '%s' "$sha"
}

st_init() { # $1 path $2 branch
  git init -q --initial-branch="$2" "$1"
  git -C "$1" symbolic-ref HEAD "refs/heads/$2"
}

st_row_field() { # $1 tsv $2 repo-basename $3 1-based column (1=repo)
  local tsv=$1 base=$2 col=$3 line
  line=$(grep -F "/$base"$'\t' "$tsv" | head -1 || true)
  # also match a repo whose path ends with /base exactly (grep above does)
  [ -n "$line" ] || { printf ''; return 0; }
  local i=1 rest=$line part
  while [ "$i" -le 7 ]; do
    if [ "$i" -eq 7 ]; then part=$rest; else part=${rest%%$'\t'*}; rest=${rest#*$'\t'}; fi
    if [ "$i" -eq "$col" ]; then printf '%s' "$part"; return 0; fi
    i=$((i + 1))
  done
}

run_selftest() {
  if [ "${SOUJI_CENSUS_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'souji-census: refusing nested --selftest\n' >&2
    exit 1
  fi
  ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-census-selftest.XXXXXX")
  trap 'rm -rf -- "$ST_TMP"' EXIT
  local fleet="$ST_TMP/fleet"
  mkdir -p "$fleet"

  # clean-shokunin: 1 commit, origin/master at that tip, empty tree otherwise
  local RC="$fleet/clean-shokunin"
  st_init "$RC" master
  printf 'kept\n' > "$RC/kept.txt"
  local c1
  c1=$(st_commit "$RC" "" "c1 kept")
  git -C "$RC" update-ref refs/heads/master "$c1"
  git -C "$RC" update-ref refs/remotes/origin/master "$c1"
  git -C "$RC" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

  # dirty-shokunin: pushed tip + untracked file + a .scratch payload
  local RD="$fleet/dirty-shokunin"
  st_init "$RD" master
  printf 'base\n' > "$RD/base.txt"
  local d1
  d1=$(st_commit "$RD" "" "d1 base")
  git -C "$RD" update-ref refs/heads/master "$d1"
  git -C "$RD" update-ref refs/remotes/origin/master "$d1"
  printf 'dirt\n' > "$RD/untracked.txt"
  mkdir -p "$RD/.scratch"
  printf 'scratch-payload\n' > "$RD/.scratch/note.txt"
  # secret-shaped name: must be flagged and never opened
  printf 'SUPER-SECRET-TOKEN-do-not-print\n' > "$RD/.scratch/credentials.env"

  # unpushed-shokunin: origin tip at u1, local master at u2 (1 unpushed)
  local RU="$fleet/unpushed-shokunin"
  st_init "$RU" master
  printf 'u1\n' > "$RU/a.txt"
  local u1
  u1=$(st_commit "$RU" "" "u1")
  git -C "$RU" update-ref refs/remotes/origin/master "$u1"
  printf 'u2\n' > "$RU/b.txt"
  local u2
  u2=$(st_commit "$RU" "$u1" "u2 local only")
  git -C "$RU" update-ref refs/heads/master "$u2"

  # linked worktree (present, dirty) + one absent registration.
  # worktrees must be 3. Neither is its own census row.
  local WT="$fleet/unpushed-shokunin-wt"
  mkdir -p "$RU/.git/worktrees/wt1" "$RU/.git/worktrees/wt-absent"
  printf 'ref: refs/heads/master\n' > "$RU/.git/worktrees/wt1/HEAD"
  printf '../..\n' > "$RU/.git/worktrees/wt1/commondir"
  printf '%s\n' "$WT/.git" > "$RU/.git/worktrees/wt1/gitdir"
  mkdir -p "$WT"
  printf 'gitdir: %s\n' "$RU/.git/worktrees/wt1" > "$WT/.git"
  printf 'wt\n' > "$WT/from-wt.txt"
  printf '%s\n' "$u2" > "$RU/.git/worktrees/wt-absent/HEAD"
  printf '../..\n' > "$RU/.git/worktrees/wt-absent/commondir"
  printf '%s\n' "$ST_TMP/missing-wt/.git" > "$RU/.git/worktrees/wt-absent/gitdir"

  # noremote-shokunin: local commit, no refs/remotes
  local RN="$fleet/noremote-shokunin"
  st_init "$RN" master
  printf 'solo\n' > "$RN/solo.txt"
  local n1
  n1=$(st_commit "$RN" "" "n1")
  git -C "$RN" update-ref refs/heads/master "$n1"

  # not a repo: must be skipped (no .git)
  mkdir -p "$fleet/plain-dir"
  printf 'nope\n' > "$fleet/plain-dir/x.txt"

  # dot-dir with a .git must be skipped (operator/config shaped)
  mkdir -p "$fleet/.hidden-shokunin"
  st_init "$fleet/.hidden-shokunin" master

  # forbidden-surface sentinels, committed so they do not inflate dirty.
  # Touched into the future below: newest-file must still ignore them.
  mkdir -p "$RC/.ufo/state"
  printf 'watchdog-secret\n' > "$RC/.ufo/watchdog.log"
  printf 'state-secret\n' > "$RC/.ufo/state/live.json"
  local c2
  c2=$(st_commit "$RC" "$c1" "c2 sentinels")
  git -C "$RC" update-ref refs/heads/master "$c2"
  git -C "$RC" update-ref refs/remotes/origin/master "$c2"
  touch -d 'tomorrow' "$RC/.ufo/watchdog.log" "$RC/.ufo/state/live.json"

  local out1="$ST_TMP/c1.tsv" out2="$ST_TMP/c2.tsv"
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" > "$out1"
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" > "$out2"

  if cmp -s "$out1" "$out2"; then
    st_ok "repeat: two runs byte-identical"
  else
    st_bad "repeat: runs differ"; diff -u "$out1" "$out2" || true
  fi

  local hdr
  hdr=$(head -1 "$out1")
  if [ "$hdr" = "$HEADER" ]; then st_ok "header matches contract"
  else st_bad "header '$hdr'"; fi

  local nrows
  nrows=$(grep -c $'\t' "$out1" || true)
  # header + 4 main repos. plain-dir, dot-dir, and the linked work tree
  # (.git file) are not rows.
  local data_rows
  data_rows=$((nrows - 1))
  if [ "$data_rows" = 4 ]; then st_ok "row count 4 (main repos only)"
  else st_bad "row count $data_rows want 4"; cat "$out1"; fi

  if grep -q 'plain-dir' "$out1"; then st_bad "plain-dir was included"; else st_ok "plain-dir skipped"; fi
  if grep -q 'hidden-shokunin' "$out1"; then st_bad "dot-dir was included"; else st_ok "dot-dir skipped"; fi
  if grep -q 'unpushed-shokunin-wt' "$out1"; then st_bad "linked worktree emitted as its own row"
  else st_ok "linked worktree not a separate row"; fi

  local v kept_iso
  kept_iso=$(date -d "@$(stat -c %Y -- "$RC/kept.txt")" --iso-8601=seconds)
  v=$(st_row_field "$out1" clean-shokunin 7)
  case "$v" in
    clean) st_ok "clean-shokunin verdict=clean ($v)" ;;
    *) st_bad "clean-shokunin verdict='$v' want clean" ;;
  esac
  v=$(st_row_field "$out1" clean-shokunin 2)
  if [ "$v" = 1 ]; then st_ok "clean worktrees=1"; else st_bad "clean worktrees=$v"; fi
  v=$(st_row_field "$out1" clean-shokunin 3)
  if [ "$v" = 0 ]; then st_ok "clean unpushed=0"; else st_bad "clean unpushed=$v"; fi
  v=$(st_row_field "$out1" clean-shokunin 4)
  if [ "$v" = 0 ]; then st_ok "clean dirty=0"; else st_bad "clean dirty=$v"; fi

  # default porcelain collapses untracked .scratch/ to one line, plus untracked.txt
  v=$(st_row_field "$out1" dirty-shokunin 4)
  if [ "$v" = 2 ]; then st_ok "dirty count=2 (untracked file + collapsed .scratch/)"
  else st_bad "dirty count=$v want 2"; fi
  v=$(st_row_field "$out1" dirty-shokunin 5)
  if [ "${v:-0}" -gt 0 ]; then st_ok "dirty scratch_bytes=$v (>0)"
  else st_bad "dirty scratch_bytes=$v"; fi
  v=$(st_row_field "$out1" dirty-shokunin 7)
  case "$v" in
    *dirty*scratch*secret-shaped*) st_ok "dirty flags include dirty,scratch,secret-shaped ($v)" ;;
    *) st_bad "dirty flags='$v'" ;;
  esac

  v=$(st_row_field "$out1" unpushed-shokunin 3)
  if [ "$v" = 1 ]; then st_ok "unpushed count=1"; else st_bad "unpushed count=$v want 1"; fi
  v=$(st_row_field "$out1" unpushed-shokunin 2)
  if [ "$v" = 3 ]; then st_ok "unpushed worktrees=3"; else st_bad "unpushed worktrees=$v want 3"; fi
  v=$(st_row_field "$out1" unpushed-shokunin 7)
  case "$v" in
    *unpushed*) st_ok "unpushed flag present ($v)" ;;
    *) st_bad "unpushed flags='$v'" ;;
  esac
  case "$v" in
    *wt-dirty*) st_ok "wt-dirty flag present ($v)" ;;
    *) st_bad "wt-dirty missing from '$v'" ;;
  esac
  case "$v" in
    *wt-absent*) st_ok "wt-absent flag present ($v)" ;;
    *) st_bad "wt-absent missing from '$v'" ;;
  esac

  v=$(st_row_field "$out1" noremote-shokunin 7)
  case "$v" in
    *no-remote*) st_ok "noremote flag present ($v)" ;;
    *) st_bad "noremote flags='$v'" ;;
  esac
  v=$(st_row_field "$out1" noremote-shokunin 3)
  if [ "${v:-0}" -ge 1 ]; then st_ok "noremote unpushed=$v (>=1, unverifiable but counted)"
  else st_bad "noremote unpushed=$v"; fi

  # secret contents must not appear anywhere in the census output
  if grep -q 'SUPER-SECRET-TOKEN' "$out1"; then
    st_bad "secret file contents leaked into census"
  else
    st_ok "secret file contents absent from census"
  fi
  if grep -q 'watchdog-secret' "$out1" || grep -q 'state-secret' "$out1"; then
    st_bad "forbidden surface contents leaked"
  else
    st_ok "forbidden surface contents absent"
  fi

  # mtime_iso is ISO-8601 with offset
  v=$(st_row_field "$out1" clean-shokunin 6)
  case "$v" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T*) st_ok "mtime_iso shape ($v)" ;;
    *) st_bad "mtime_iso shape '$v'" ;;
  esac
  if [ "$v" = "$kept_iso" ]; then
    st_ok "mtime ignores future .ufo/state and .ufo/watchdog.log"
  else
    st_bad "mtime '$v' want kept.txt '$kept_iso' (forbidden surfaces leaked into mtime)"
  fi

  # compare against itself: header only, exit 0
  local cmp_out cmp_st
  set +e
  cmp_out=$(env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$out1" 2>&1)
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 0 ] && [ "$cmp_out" = "$DIFF_HEADER" ]; then
    st_ok "compare identical: exit 0, header only"
  else
    st_bad "compare identical: exit=$cmp_st out=$(printf '%s' "$cmp_out" | head -5)"
  fi

  # mutate scratch size and dirty set, compare must report both
  printf 'more-scratch\n' >> "$RD/.scratch/note.txt"
  rm -f -- "$RD/untracked.txt"
  local cmp2 cmp2_st
  set +e
  cmp2=$(env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$out1" 2>&1)
  cmp2_st=$?
  set -e
  if [ "$cmp2_st" = 3 ]; then st_ok "compare mutation: exit 3"
  else st_bad "compare mutation: exit=$cmp2_st"; fi
  case "$cmp2" in
    *dirty-shokunin*$'\t'"scratch_bytes"$'\t'*) st_ok "compare reports scratch_bytes" ;;
    *) st_bad "compare missing scratch_bytes row" ;;
  esac
  case "$cmp2" in
    *dirty-shokunin*$'\t'"dirty"$'\t'*) st_ok "compare reports dirty delta" ;;
    *) st_bad "compare missing dirty row" ;;
  esac

  # bad header must exit 2, not look like an empty diff
  printf 'nope\n' > "$ST_TMP/bad.tsv"
  set +e
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$ST_TMP/bad.tsv" >/dev/null 2>&1
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 2 ]; then st_ok "bad compare header exits 2"
  else st_bad "bad compare header exit=$cmp_st want 2"; fi

  # unknown flag exits 2
  set +e
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 "$SELF" --nope >/dev/null 2>&1
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 2 ]; then st_ok "unknown flag exits 2"
  else st_bad "unknown flag exit=$cmp_st want 2"; fi

  # source audit: no forbidden git porcelain in non-comment lines
  local n
  n=$(grep -cE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase|prune)( |$)' "$SELF" || true)
  n=${n// /}
  if [ "${n:-1}" = 0 ]; then st_ok "no forbidden git subcommand"
  else st_bad "$n forbidden git invocation(s)"; fi

  case "$fleet" in
    "$ST_TMP"/*) st_ok "fixtures under mktemp ($ST_TMP)" ;;
    *) st_bad "fixtures not under mktemp" ;;
  esac

  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then exit 1; fi
  exit 0
}

# --- main ------------------------------------------------------------------

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --include-root) INCLUDE_ROOT=1; shift ;;
    --root)
      [ "$#" -ge 2 ] || usage_err "--root needs a directory"
      ROOT=$2; shift 2 ;;
    --root=*) ROOT=${1#*=}; shift ;;
    --compare)
      [ "$#" -ge 2 ] || usage_err "--compare needs a TSV path"
      COMPARE=$2; shift 2 ;;
    --compare=*) COMPARE=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    --) shift; break ;;
    -*) usage_err "unknown flag: $1" ;;
    *) usage_err "unexpected argument: $1 (repos come from --root)" ;;
  esac
done

if [ "$SELFTEST" = 1 ]; then run_selftest; fi

command -v git >/dev/null 2>&1 || { printf 'souji-census: git not found\n' >&2; exit 1; }
command -v du >/dev/null 2>&1 || { printf 'souji-census: du not found\n' >&2; exit 1; }

if [ -n "$COMPARE" ]; then
  emit_compare
  exit $?
fi

emit_census
exit 0
