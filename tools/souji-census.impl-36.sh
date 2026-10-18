#!/usr/bin/env bash
# souji-census — repeatable read-only fleet census (round 6, seat S36).
#
# Independent of the other impls. bash + coreutils + git + find. Read-only
# over every repo it scans: no fetch/push/commit/branch/checkout/reset/rebase/
# prune/remove, no index refresh, no hooks, no reads of secret-shaped files,
# no opens of .ufo/state or .ufo/watchdog.log. Writes only under mktemp
# (/tmp if that filesystem accepts writes, else /var/tmp) during --compare
# and --selftest.
#
# CLI
#   tools/souji-census.impl-36.sh [--root DIR] [--compare PREV.tsv]
#                                 [--include-root] [--selftest] [DIR]
#   DIR (positional) is the same as --root. Default root: $SHOKUNIN_ROOT,
#   else the parent of this repo.
#
# Census TSV (header + one row per repo, physical paths, LC_ALL=C sorted):
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
#
# Hand-check commands (the columns are defined as these; wc whitespace
# stripped). git is invoked with --no-optional-locks so the count matches
# a plain git invocation but the index is not rewritten:
#   worktrees      git -C REPO worktree list | wc -l
#   unpushed       git -C REPO rev-list --count --branches --not --remotes
#   dirty          git -C REPO status --porcelain | wc -l
#                  (default untracked mode: a directory is ONE line, not
#                  --untracked-files=all)
#   scratch_bytes  du -sb -P REPO/.scratch   (first field; 0 if absent)
#   mtime_iso      newest regular file, second resolution, ISO-8601 with
#                  numeric offset. Excludes .git, .ufo/state,
#                  .ufo/watchdog.log, symlinks, and secret-shaped names.
#                  Those names are flagged and never opened.
#
# verdict_flags (stable order, comma-joined). Observations, NOT removal
# receipts — `clean` is not SAFE-to-delete:
#   clean                 unpushed=0, dirty=0, a remote-tracking ref exists,
#                         and no failure flag below
#   dirty                 dirty>0
#   unpushed              unpushed>0
#   no-remote             zero refs/remotes/* (the unpushed number is then
#                         "commits not on any remote", which cannot prove
#                         pushed — same rule as souji-verify pushed-unverifiable)
#   scratch               .scratch is a real directory and scratch_bytes>0
#   scratch-symlink       .scratch is a symlink; du -P does not follow it
#   secret-shaped         a secret-shaped name was seen (contents not read)
#   secrets-refusal       the repo path itself is secret-shaped; not entered
#   status-unverifiable   git status failed
#   timeout               a measurement hit its bound; that number is 0 and
#                         is not a measurement
#   error                 a measurement command failed
# `clean` is suppressed by dirty, unpushed, no-remote, scratch-symlink,
# secrets-refusal, status-unverifiable, timeout, error. scratch and
# secret-shaped may appear beside clean.
#
# --compare PREV.tsv
#   PREV must use this header. Diff TSV on stdout:
#     repo  field  before  after  change
#   change is +N/-N for numeric fields, `changed` for text, `added`/`removed`
#   for repo presence (before/after = ABSENT/PRESENT). Exit 0 if header-only,
#   exit 3 if any row differs. A different schema (including the round-1
#   artifact census) is incomparable: exit 2, stderr contains `incomparable`.
#   Pass the same --root/--include-root used to produce PREV.
#
# --selftest
#   Fixture fleet under mktemp. Exit 0 pass, 1 fail. Ignores --root.
#
# Other exits: 0 census emitted; 1 root missing or tool missing; 2 usage.
# Env: SHOKUNIN_ROOT. A repo is an immediate child directory (not a dot-dir)
# that contains .git. --include-root also emits the root when it has .git.
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE GIT_PREFIX 2>/dev/null || true

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
  sed -n '2,62p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}
usage_err() { printf 'souji-census: %s\n' "$1" >&2; usage 2; }

# /tmp on this host can be over a user quota while still looking writable.
# Probe a real create+write and fall back to /var/tmp. Never pick a directory
# inside the repo being scanned ($1, optional).
ensure_writable_tmpdir() {
  local avoid=${1:-} c d
  local -a cands=()
  if [ -n "${TMPDIR:-}" ]; then cands+=("$TMPDIR"); fi
  cands+=(/tmp /var/tmp)
  for c in "${cands[@]}"; do
    [ -d "$c" ] && [ -w "$c" ] || continue
    if [ -n "$avoid" ]; then
      case "$c" in
        "$avoid"|"$avoid"/*) continue ;;
      esac
    fi
    d=$(mktemp -d "$c/souji-census-36-w.XXXXXX" 2>/dev/null) || continue
    if printf x >"$d/.w" 2>/dev/null; then
      rm -rf -- "$d"
      export TMPDIR=$c
      return 0
    fi
    rm -rf -- "$d" 2>/dev/null || true
  done
  printf 'souji-census: no writable temp directory (/tmp and /var/tmp failed)\n' >&2
  return 1
}

# Physical path. Existing dirs go through pwd -P; missing paths fall back.
phys_path() {
  local p=$1
  if [ -d "$p" ]; then
    (cd -- "$p" && pwd -P) 2>/dev/null && return 0
  fi
  readlink -m -- "$p" 2>/dev/null || printf '%s' "$p"
}

is_secret_component() {
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
    if [ -n "$comp" ] && is_secret_component "$comp"; then
      set +f
      return 0
    fi
  done
  set +f
  return 1
}

sanitize_field() {
  local s=$1
  s=${s//$'\t'/ }
  s=${s//$'\n'/ }
  s=${s//$'\r'/ }
  printf '%s' "$s"
}

# Read-only git: no optional index rewrite, no hooks, no fsmonitor.
# timeout(1) cannot invoke a shell function, so the timed path execs git
# directly with the same options. Keep the two lists identical.
GIT_RO=(git -c core.fsmonitor= -c core.hooksPath=/dev/null --no-optional-locks)

git_ro() {
  GIT_OPTIONAL_LOCKS=0 "${GIT_RO[@]}" "$@"
}

# Run a command, capturing stdout. CAP_RC is the exit status. stderr discarded.
# set -e is restored. Timeout exits are 124.
CAP_OUT=""
CAP_RC=0
capture() {
  set +e
  CAP_OUT=$("$@" 2>/dev/null)
  CAP_RC=$?
  set -e
}

capture_git() { # $1 seconds, remaining args passed to git
  local secs=$1
  shift
  set +e
  CAP_OUT=$(timeout "$secs" env GIT_OPTIONAL_LOCKS=0 "${GIT_RO[@]}" "$@" 2>/dev/null)
  CAP_RC=$?
  set -e
}

count_lines() {
  local s=$1
  if [ -z "$s" ]; then
    printf '0'
    return 0
  fi
  printf '%s\n' "$s" | grep -c . || true
}

note_rc() { # $1 rc; appends timeout or error to FLAGS via a global
  case "$1" in
    0) ;;
    124) FLAGS+=("timeout") ;;
    *) FLAGS+=("error") ;;
  esac
}

join_ordered() {
  local ordered="" name f
  for name in clean dirty unpushed no-remote scratch scratch-symlink \
    secret-shaped secrets-refusal status-unverifiable timeout error; do
    for f in "${FLAGS[@]+"${FLAGS[@]}"}"; do
      if [ "$f" = "$name" ]; then
        if [ -z "$ordered" ]; then ordered=$name; else ordered="$ordered,$name"; fi
        break
      fi
    done
  done
  printf '%s' "$ordered"
}

has_flag() {
  local want=$1 f
  for f in "${FLAGS[@]+"${FLAGS[@]}"}"; do
    [ "$f" = "$want" ] && return 0
  done
  return 1
}

# --- one repo ----------------------------------------------------------------

census_one() {
  local repo
  repo=$(phys_path "$1")
  FLAGS=()
  if is_secret_path "$repo"; then
    printf '%s\t0\t0\t0\t0\t\tsecrets-refusal\n' "$(sanitize_field "$repo")"
    return 0
  fi
  if [ ! -e "$repo/.git" ]; then
    printf '%s\t0\t0\t0\t0\t\terror\n' "$(sanitize_field "$repo")"
    return 0
  fi

  local wt=0 unp=0 dirty=0 scratch=0 iso="" remote_state=unknown

  capture_git 30 -C "$repo" rev-parse --is-inside-work-tree
  if [ "$CAP_RC" -ne 0 ] || [ "$CAP_OUT" != true ]; then
    printf '%s\t0\t0\t0\t0\t\terror\n' "$(sanitize_field "$repo")"
    return 0
  fi

  capture_git 30 -C "$repo" worktree list
  note_rc "$CAP_RC"
  if [ "$CAP_RC" -eq 0 ]; then wt=$(count_lines "$CAP_OUT"); else wt=0; fi

  capture_git 30 -C "$repo" for-each-ref --format='%(refname)' refs/remotes
  note_rc "$CAP_RC"
  if [ "$CAP_RC" -eq 0 ]; then
    if [ "$(count_lines "$CAP_OUT")" -eq 0 ]; then remote_state=no-remote
    else remote_state=has-remote
    fi
  fi

  capture_git 60 -C "$repo" rev-list --count --branches --not --remotes
  note_rc "$CAP_RC"
  if [ "$CAP_RC" -eq 0 ]; then
    unp=${CAP_OUT//[[:space:]]/}
    case "$unp" in ''|*[!0-9]*) unp=0; FLAGS+=("error") ;; esac
  else
    unp=0
  fi

  capture_git 120 -C "$repo" status --porcelain
  if [ "$CAP_RC" -eq 0 ]; then
    dirty=$(count_lines "$CAP_OUT")
  elif [ "$CAP_RC" -eq 124 ]; then
    FLAGS+=("timeout")
    dirty=0
  else
    FLAGS+=("status-unverifiable")
    dirty=0
  fi

  local scratch_path="$repo/.scratch" scratch_kind=absent
  if [ -L "$scratch_path" ]; then
    scratch_kind=symlink
  elif [ -d "$scratch_path" ]; then
    scratch_kind=dir
  elif [ -e "$scratch_path" ]; then
    scratch_kind=other
  fi
  if [ "$scratch_kind" = absent ]; then
    scratch=0
  else
    capture timeout 180 du -sb -P -- "$scratch_path"
    note_rc "$CAP_RC"
    if [ "$CAP_RC" -eq 0 ]; then
      scratch=${CAP_OUT%%[[:space:]]*}
      case "$scratch" in ''|*[!0-9]*) scratch=0; FLAGS+=("error") ;; esac
    else
      scratch=0
    fi
  fi

  # One walk: secret-shaped names flagged and pruned (never opened); other
  # regular files contribute an epoch. Forbidden surfaces pruned.
  local mt_tmp newest=0 saw_secret=0 line ts int
  mt_tmp=$(mktemp "${TMPDIR:-/tmp}/souji-census-36-mt.XXXXXX")
  set +e
  timeout 180 find "$repo" \
    \( -name .git -o -path "$repo/.ufo/state" -o -path "$repo/.ufo/watchdog.log" \) -prune \
    -o \
    \( \
      \( -iname '*.env' -o -iname '.env' -o -iname '.env.*' -o -iname '.envrc' \
         -o -iname '*credential*' -o -iname '*secret*' -o -iname 'id_*' -o -iname '*.pem' \) \
      -printf 'S\n' -prune \
    \) \
    -o -type f -printf 'T %T@\n' >"$mt_tmp" 2>/dev/null
  local find_rc=$?
  set -e
  note_rc "$find_rc"
  if [ "$find_rc" -eq 124 ]; then
    newest=0
    saw_secret=0
  else
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        S)
          saw_secret=1
          ;;
        T\ *)
          ts=${line#T }
          int=${ts%%.*}
          case "$int" in ''|*[!0-9]*) continue ;; esac
          if [ "$int" -gt "$newest" ]; then newest=$int; fi
          ;;
      esac
    done <"$mt_tmp"
  fi
  rm -f -- "$mt_tmp"

  if [ "$newest" -gt 0 ]; then
    iso=$(date -d "@$newest" --iso-8601=seconds 2>/dev/null || true)
    if [ -z "$iso" ]; then FLAGS+=("error"); fi
  fi

  if [ "$remote_state" = no-remote ]; then FLAGS+=("no-remote"); fi
  if [ "${unp:-0}" -gt 0 ]; then FLAGS+=("unpushed"); fi
  if [ "${dirty:-0}" -gt 0 ]; then FLAGS+=("dirty"); fi
  if [ "$scratch_kind" = dir ] && [ "${scratch:-0}" -gt 0 ]; then FLAGS+=("scratch"); fi
  if [ "$scratch_kind" = symlink ]; then FLAGS+=("scratch-symlink"); fi
  if [ "$saw_secret" -eq 1 ]; then FLAGS+=("secret-shaped"); fi

  local blocked=0
  if has_flag dirty || has_flag unpushed || has_flag no-remote \
    || has_flag scratch-symlink || has_flag secrets-refusal \
    || has_flag status-unverifiable || has_flag timeout || has_flag error; then
    blocked=1
  fi
  if [ "$blocked" -eq 0 ]; then FLAGS+=("clean"); fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(sanitize_field "$repo")" "$wt" "$unp" "$dirty" "$scratch" \
    "$(sanitize_field "$iso")" "$(join_ordered)"
}

list_repos() {
  local root=$1 d base phys
  local -a found=()
  declare -A seen=()
  if [ "$INCLUDE_ROOT" = 1 ] && [ -e "$root/.git" ]; then
    phys=$(phys_path "$root")
    seen["$phys"]=1
    found+=("$phys")
  fi
  shopt -s nullglob
  for d in "$root"/*/; do
    [ -d "$d" ] || continue
    base=$(basename -- "$d")
    case "$base" in
      .*) continue ;;
    esac
    if [ -e "$d/.git" ] || [ -L "$d/.git" ]; then
      phys=$(phys_path "$d")
      if [ -n "${seen[$phys]+x}" ]; then continue; fi
      seen["$phys"]=1
      found+=("$phys")
    fi
  done
  shopt -u nullglob
  if [ "${#found[@]}" -eq 0 ]; then return 0; fi
  printf '%s\n' "${found[@]}" | LC_ALL=C sort
}

emit_census() {
  local root
  root=$(phys_path "$ROOT")
  [ -d "$root" ] || {
    printf 'souji-census: root is not a directory: %s\n' "$root" >&2
    exit 1
  }
  # Never let sort/mktemp drop files inside a repo we are scanning.
  case "${TMPDIR:-}" in
    "$root"|"$root"/*) unset TMPDIR ;;
  esac
  ensure_writable_tmpdir "$root" || exit 1
  printf '%s\n' "$HEADER"
  local repo
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    census_one "$repo"
  done < <(list_repos "$root")
}

# --- compare ------------------------------------------------------------------

declare -A CMP_MAP=()

load_census() {
  local file=$1 line n=0 repo rest
  CMP_MAP=()
  [ -f "$file" ] || usage_err "compare file not found: $file"
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1))
    line=${line%$'\r'}
    [ -n "$line" ] || continue
    if [ "$n" = 1 ]; then
      if [ "$line" != "$HEADER" ]; then
        printf 'souji-census: incomparable: previous TSV header is not a fleet census\n' >&2
        printf 'souji-census: want: %s\n' "$HEADER" >&2
        exit 2
      fi
      continue
    fi
    repo=${line%%$'\t'*}
    rest=${line#*$'\t'}
    [ -n "$repo" ] || usage_err "compare file: empty repo on line $n"
    if [ -n "${CMP_MAP[$repo]+x}" ]; then
      usage_err "compare file: duplicate repo $repo"
    fi
    CMP_MAP["$repo"]=$rest
  done <"$file"
}

field_at() {
  local rest=$1 idx=$2 i=1 part
  while [ "$i" -le 6 ]; do
    if [ "$i" -eq 6 ]; then
      part=$rest
    else
      part=${rest%%$'\t'*}
      rest=${rest#*$'\t'}
    fi
    if [ "$i" -eq "$idx" ]; then
      printf '%s' "$part"
      return 0
    fi
    i=$((i + 1))
  done
}

numeric_change() {
  local b=$1 a=$2 d
  case "$b" in ''|*[!0-9-]*) printf 'non-numeric'; return 0 ;; esac
  case "$a" in ''|*[!0-9-]*) printf 'non-numeric'; return 0 ;; esac
  d=$((a - b))
  if [ "$d" -gt 0 ]; then printf '+%s' "$d"
  elif [ "$d" -lt 0 ]; then printf '%s' "$d"
  else printf '0'
  fi
}

emit_compare() {
  local -A before=()
  load_census "$COMPARE"
  for k in "${!CMP_MAP[@]}"; do before["$k"]=${CMP_MAP[$k]}; done

  local tmp
  tmp=$(mktemp "${TMPDIR:-/tmp}/souji-census-36-now.XXXXXX")
  if ! emit_census >"$tmp"; then
    rm -f -- "$tmp"
    exit 1
  fi
  load_census "$tmp"
  local -A after=()
  for k in "${!CMP_MAP[@]}"; do after["$k"]=${CMP_MAP[$k]}; done
  rm -f -- "$tmp"

  printf '%s\n' "$DIFF_HEADER"
  local changes=0 repo
  local -a repos=()
  for repo in "${!before[@]}"; do repos+=("$repo"); done
  for repo in "${!after[@]}"; do
    if [ -z "${before[$repo]+x}" ]; then repos+=("$repo"); fi
  done
  local sorted name i before_v after_v chg rest_b rest_a
  local -a names=(worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags)
  sorted=$(printf '%s\n' "${repos[@]}" | LC_ALL=C sort -u)
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
  done <<<"$sorted"

  if [ "$changes" -gt 0 ]; then return 3; fi
  return 0
}

# --- selftest -----------------------------------------------------------------

ST_PASS=0
ST_FAIL=0
ST_TMP=""

st_note() { printf '%s\n' "$*"; }
st_ok() { ST_PASS=$((ST_PASS + 1)); st_note "PASS $*"; }
st_bad() { ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $*"; }

st_commit() {
  local repo=$1 parent=$2 msg=$3 tree sha
  git -C "$repo" add -A >/dev/null
  tree=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tree" -p "$parent")
  else
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tree")
  fi
  printf '%s' "$sha"
}

st_init() {
  git init -q --initial-branch=master "$1"
  git -C "$1" symbolic-ref HEAD "refs/heads/$2"
}

st_field() { # $1 tsv $2 basename $3 1-based column
  local tsv=$1 base=$2 col=$3 line i=1 rest part
  line=$(grep -F "/$base"$'\t' "$tsv" | head -1 || true)
  [ -n "$line" ] || { printf ''; return 0; }
  rest=$line
  while [ "$i" -le 7 ]; do
    if [ "$i" -eq 7 ]; then part=$rest; else part=${rest%%$'\t'*}; rest=${rest#*$'\t'}; fi
    if [ "$i" -eq "$col" ]; then printf '%s' "$part"; return 0; fi
    i=$((i + 1))
  done
}

st_wc() {
  local n
  n=$(wc -l | tr -d '[:space:]')
  printf '%s' "${n:-0}"
}

run_selftest() {
  if [ "${SOUJI_CENSUS_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'souji-census: refusing nested --selftest\n' >&2
    exit 1
  fi
  ensure_writable_tmpdir || exit 1
  ST_TMP=$(mktemp -d "${TMPDIR}/souji-census-36-selftest.XXXXXX")
  trap 'rm -rf -- "$ST_TMP"' EXIT
  export GIT_AUTHOR_NAME=souji-selftest GIT_AUTHOR_EMAIL=souji@shokunin.local
  export GIT_COMMITTER_NAME=souji-selftest GIT_COMMITTER_EMAIL=souji@shokunin.local
  local fleet="$ST_TMP/fleet"
  mkdir -p "$fleet"
  local CANARY="SOUJI36-CANARY-do-not-leak"

  local RC="$fleet/clean-shokunin"
  st_init "$RC" master
  printf 'kept\n' >"$RC/kept.txt"
  local c1
  c1=$(st_commit "$RC" "" "c1")
  git -C "$RC" update-ref refs/heads/master "$c1"
  git -C "$RC" update-ref refs/remotes/origin/master "$c1"
  git -C "$RC" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  touch -d '2020-01-15 12:00:00' "$RC/kept.txt"
  mkdir -p "$RC/.ufo/state"
  printf 'state-secret\n' >"$RC/.ufo/state/live.json"
  printf 'watchdog-secret\n' >"$RC/.ufo/watchdog.log"
  touch -d '2099-01-01 00:00:00' "$RC/.ufo/watchdog.log" "$RC/.ufo/state/live.json"
  # A hook that must not run. core.fsmonitor points at it; the tool overrides.
  mkdir -p "$RC/.git/hooks"
  printf '#!/bin/sh\nprintf HOOK_RAN >> "%s/.git/hook-ran.txt"\nexit 0\n' "$RC" >"$RC/.git/hooks/fsmonitor-watchman"
  chmod +x "$RC/.git/hooks/fsmonitor-watchman"
  git -C "$RC" config core.fsmonitor "$RC/.git/hooks/fsmonitor-watchman"
  printf 'git-only-secret\n' >"$RC/.git/credentials.env"

  local RD="$fleet/dirty-shokunin"
  st_init "$RD" master
  printf 'base\n' >"$RD/base.txt"
  local d1
  d1=$(st_commit "$RD" "" "d1")
  git -C "$RD" update-ref refs/heads/master "$d1"
  git -C "$RD" update-ref refs/remotes/origin/master "$d1"
  printf 'loose\n' >"$RD/loose.txt"
  mkdir -p "$RD/untracked-dir"
  printf '1\n' >"$RD/untracked-dir/f1.txt"
  printf '2\n' >"$RD/untracked-dir/f2.txt"
  mkdir -p "$RD/.scratch/sub"
  printf 'scratch-payload\n' >"$RD/.scratch/sub/note.txt"
  printf '%s\n' "$CANARY" >"$RD/.scratch/credentials.env"
  mkdir -p "$ST_TMP/outside"
  # 64KiB target: if du followed the symlink, scratch_bytes would jump.
  dd if=/dev/zero of="$ST_TMP/outside/big.txt" bs=1024 count=64 status=none
  ln -s "$ST_TMP/outside/big.txt" "$RD/.scratch/sub/escape"

  local RU="$fleet/unpushed-shokunin"
  st_init "$RU" master
  printf 'u1\n' >"$RU/a.txt"
  local u1
  u1=$(st_commit "$RU" "" "u1")
  git -C "$RU" update-ref refs/remotes/origin/master "$u1"
  printf 'u2\n' >"$RU/b.txt"
  local u2
  u2=$(st_commit "$RU" "$u1" "u2 local")
  git -C "$RU" update-ref refs/heads/master "$u2"
  local WT="$fleet/unpushed-shokunin-wt"
  git -C "$RU" worktree add --detach "$WT" HEAD >/dev/null 2>&1
  printf 'wt-dirt\n' >"$WT/wt-untracked.txt"

  local RN="$fleet/noremote-shokunin"
  st_init "$RN" master
  printf 'solo\n' >"$RN/solo.txt"
  local n1
  n1=$(st_commit "$RN" "" "n1")
  git -C "$RN" update-ref refs/heads/master "$n1"

  local RS="$fleet/credentials-shokunin"
  st_init "$RS" master
  printf '%s\n' "$CANARY" >"$RS/hidden.txt"
  local s1
  s1=$(st_commit "$RS" "" "s1")
  git -C "$RS" update-ref refs/heads/master "$s1"

  local RB="$fleet/broken-shokunin"
  mkdir -p "$RB"
  printf 'gitdir: /nowhere-souji-36\n' >"$RB/.git"

  mkdir -p "$fleet/plain-dir"
  printf 'nope\n' >"$fleet/plain-dir/x.txt"
  mkdir -p "$fleet/.hidden-shokunin"
  st_init "$fleet/.hidden-shokunin" master

  local idx_before file_before
  idx_before=$(sha256sum "$RC/.git/index")
  idx_before=${idx_before%% *}
  file_before=$(stat -c %Y "$RC/kept.txt")
  # Invite an index refresh; a writing status would change the index.
  touch -d '2020-01-15 12:00:00' "$RC/kept.txt"

  local out1="$ST_TMP/c1.tsv" out2="$ST_TMP/c2.tsv"
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    bash "$SELF" --root "$fleet" >"$out1"
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    bash "$SELF" --root "$fleet" >"$out2"

  if cmp -s "$out1" "$out2"; then st_ok "repeat byte-identical"
  else st_bad "repeat differs"; diff -u "$out1" "$out2" || true; fi

  local hdr
  hdr=$(head -1 "$out1")
  if [ "$hdr" = "$HEADER" ]; then st_ok "header"
  else st_bad "header [$hdr]"; fi

  local idx_after file_after
  idx_after=$(sha256sum "$RC/.git/index")
  idx_after=${idx_after%% *}
  file_after=$(stat -c %Y "$RC/kept.txt")
  if [ "$idx_before" = "$idx_after" ]; then st_ok "index bytes unchanged"
  else st_bad "index was rewritten"; fi
  if [ "$file_before" = "$file_after" ]; then st_ok "tracked mtime unchanged"
  else st_bad "tracked mtime changed"; fi
  if [ -e "$RC/.git/hook-ran.txt" ]; then st_bad "fsmonitor hook ran"
  else st_ok "fsmonitor hook did not run"; fi

  if grep -q "$CANARY" "$out1"; then st_bad "canary leaked"; else st_ok "canary absent"; fi
  if grep -q 'watchdog-secret' "$out1" || grep -q 'state-secret' "$out1"; then
    st_bad "forbidden surface leaked"
  else st_ok "forbidden surface absent"; fi
  if grep -q 'plain-dir' "$out1"; then st_bad "plain-dir included"; else st_ok "plain-dir skipped"; fi
  if grep -q 'hidden-shokunin' "$out1"; then st_bad "dot-dir included"; else st_ok "dot-dir skipped"; fi

  local data_rows
  data_rows=$(($(grep -c $'\t' "$out1") - 1))
  # clean dirty unpushed unpushed-wt noremote credentials broken = 7
  if [ "$data_rows" = 7 ]; then st_ok "row count 7"
  else st_bad "row count $data_rows want 7"; cat "$out1"; fi

  local v expect
  v=$(st_field "$out1" clean-shokunin 7)
  case "$v" in
    clean) st_ok "clean flags ($v)" ;;
    *) st_bad "clean flags [$v]"; grep clean-shokunin "$out1" || true ;;
  esac
  # secret inside .git must not flag the repo
  case "$v" in
    *secret*) st_bad "clean flagged secret from .git" ;;
    *) st_ok "clean did not flag .git secret" ;;
  esac
  v=$(st_field "$out1" clean-shokunin 2)
  expect=$(git_ro -C "$RC" worktree list | st_wc)
  if [ "$v" = "$expect" ] && [ "$v" = 1 ]; then st_ok "clean worktrees=$v"
  else st_bad "clean worktrees tool=$v hand=$expect"; fi
  v=$(st_field "$out1" clean-shokunin 3)
  expect=$(git_ro -C "$RC" rev-list --count --branches --not --remotes | tr -d '[:space:]')
  if [ "$v" = "$expect" ] && [ "$v" = 0 ]; then st_ok "clean unpushed=$v"
  else st_bad "clean unpushed tool=$v hand=$expect"; fi
  v=$(st_field "$out1" clean-shokunin 4)
  expect=$(git_ro -C "$RC" status --porcelain | st_wc)
  plain=$(git -C "$RC" status --porcelain | st_wc)
  if [ "$v" = "$expect" ] && [ "$v" = "$plain" ] && [ "$v" = 0 ]; then
    st_ok "clean dirty=$v matches plain git status"
  else st_bad "clean dirty tool=$v ro=$expect plain=$plain"; fi
  v=$(st_field "$out1" clean-shokunin 6)
  expect=$(date -d "@$(stat -c %Y "$RC/kept.txt")" --iso-8601=seconds)
  if [ "$v" = "$expect" ]; then st_ok "clean mtime excludes watchdog ($v)"
  else st_bad "clean mtime [$v] want [$expect]"; fi
  case "$v" in
    2099*) st_bad "mtime followed forbidden surface" ;;
    *) ;;
  esac

  v=$(st_field "$out1" dirty-shokunin 4)
  expect=$(git -C "$RD" status --porcelain | st_wc)
  all=$(git -C "$RD" status --porcelain --untracked-files=all | st_wc)
  if [ "$v" = "$expect" ]; then st_ok "dirty matches status --porcelain ($v)"
  else st_bad "dirty tool=$v hand=$expect"; fi
  if [ "$all" -gt "$expect" ]; then st_ok "untracked dir collapsed ($expect < all=$all)"
  else st_bad "untracked-files=all ($all) not greater than normal ($expect)"; fi
  v=$(st_field "$out1" dirty-shokunin 5)
  expect=$(du -sb -P -- "$RD/.scratch")
  expect=${expect%%[[:space:]]*}
  plain=$(du -sb -- "$RD/.scratch")
  plain=${plain%%[[:space:]]*}
  followed=$(du -sb -L -- "$RD/.scratch" 2>/dev/null || true)
  followed=${followed%%[[:space:]]*}
  if [ "$v" = "$expect" ] && [ "$v" = "$plain" ]; then st_ok "scratch_bytes=$v matches du -sb"
  else st_bad "scratch tool=$v du-P=$expect du=$plain"; fi
  if [ "${v:-0}" -lt 10000 ] && [ "${followed:-0}" -gt 60000 ]; then
    st_ok "scratch symlink not followed ($v < followed $followed)"
  else st_bad "scratch follow check tool=$v followed=$followed"; fi
  v=$(st_field "$out1" dirty-shokunin 7)
  case "$v" in
    *dirty*scratch*secret-shaped*) st_ok "dirty flags ($v)" ;;
    *) st_bad "dirty flags [$v]" ;;
  esac

  v=$(st_field "$out1" unpushed-shokunin 3)
  expect=$(git -C "$RU" rev-list --count --branches --not --remotes | tr -d '[:space:]')
  if [ "$v" = "$expect" ] && [ "$v" = 1 ]; then st_ok "unpushed=$v"
  else st_bad "unpushed tool=$v hand=$expect"; fi
  v=$(st_field "$out1" unpushed-shokunin 2)
  expect=$(git -C "$RU" worktree list | st_wc)
  if [ "$v" = "$expect" ] && [ "$v" = 2 ]; then st_ok "worktrees=$v"
  else st_bad "worktrees tool=$v hand=$expect"; fi
  v=$(st_field "$out1" unpushed-shokunin 7)
  case "$v" in
    *unpushed*) st_ok "unpushed flag ($v)" ;;
    *) st_bad "unpushed flag [$v]" ;;
  esac
  v=$(st_field "$out1" unpushed-shokunin-wt 4)
  expect=$(git -C "$WT" status --porcelain | st_wc)
  if [ "$v" = "$expect" ] && [ "$v" = 1 ]; then st_ok "linked worktree dirty counted on its own row ($v)"
  else st_bad "wt dirty tool=$v hand=$expect"; fi

  v=$(st_field "$out1" noremote-shokunin 7)
  case "$v" in
    *no-remote*) st_ok "no-remote flag ($v)" ;;
    *) st_bad "no-remote flag [$v]" ;;
  esac
  case "$v" in
    clean|clean,*) st_bad "no-remote marked clean" ;;
    *) st_ok "no-remote is not clean" ;;
  esac
  v=$(st_field "$out1" noremote-shokunin 3)
  expect=$(git -C "$RN" rev-list --count --branches --not --remotes | tr -d '[:space:]')
  if [ "$v" = "$expect" ] && [ "${v:-0}" -ge 1 ]; then st_ok "no-remote unpushed=$v"
  else st_bad "no-remote unpushed tool=$v hand=$expect"; fi

  v=$(st_field "$out1" credentials-shokunin 7)
  if [ "$v" = secrets-refusal ]; then st_ok "secret-shaped repo refused"
  else st_bad "credentials flags [$v]"; fi
  v=$(st_field "$out1" credentials-shokunin 2)
  if [ "$v" = 0 ]; then st_ok "refused repo was not measured"
  else st_bad "refused repo worktrees=$v"; fi

  v=$(st_field "$out1" broken-shokunin 7)
  if [ "$v" = error ]; then st_ok "broken gitdir is error, not a crash"
  else st_bad "broken flags [$v]"; fi

  # compare identical
  local cmp_out cmp_st
  set +e
  cmp_out=$(env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    bash "$SELF" --root "$fleet" --compare "$out1" 2>"$ST_TMP/cmp.err")
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 0 ] && [ "$cmp_out" = "$DIFF_HEADER" ]; then
    st_ok "compare identical exit 0"
  else
    st_bad "compare identical exit=$cmp_st"
    printf '%s\n' "$cmp_out" | head -5
  fi

  # mutate and compare
  printf 'more\n' >>"$RD/.scratch/sub/note.txt"
  rm -f -- "$RD/loose.txt"
  set +e
  cmp_out=$(env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    bash "$SELF" --root "$fleet" --compare "$out1" 2>"$ST_TMP/cmp2.err")
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 3 ]; then st_ok "compare mutation exit 3"
  else st_bad "compare mutation exit=$cmp_st"; printf '%s\n' "$cmp_out"; fi
  case "$cmp_out" in
    *"dirty-shokunin"$'\t'"scratch_bytes"$'\t'*) st_ok "compare scratch_bytes" ;;
    *) st_bad "compare missing scratch_bytes" ;;
  esac
  case "$cmp_out" in
    *"dirty-shokunin"$'\t'"dirty"$'\t'*) st_ok "compare dirty delta" ;;
    *) st_bad "compare missing dirty" ;;
  esac

  # round-1 schema is incomparable
  printf 'seat\tpath\tsize_bytes\tmtime\treceipt\tverdict\torig_verdict\tcorrected_by\tnote\n' >"$ST_TMP/round1.tsv"
  printf 'S01\t/tmp/x\t1\t2020-01-01T00:00:00-03:00\tpushed\tSAFE\tSAFE\tparent\tnote\n' >>"$ST_TMP/round1.tsv"
  set +e
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    bash "$SELF" --root "$fleet" --compare "$ST_TMP/round1.tsv" >"$ST_TMP/r1.out" 2>"$ST_TMP/r1.err"
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 2 ] && grep -q incomparable "$ST_TMP/r1.err"; then
    st_ok "round-1 schema incomparable exit 2"
  else st_bad "round-1 compare exit=$cmp_st err=$(cat "$ST_TMP/r1.err")"; fi

  printf 'nope\n' >"$ST_TMP/bad.tsv"
  set +e
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    bash "$SELF" --root "$fleet" --compare "$ST_TMP/bad.tsv" >/dev/null 2>&1
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 2 ]; then st_ok "bad header exit 2"
  else st_bad "bad header exit=$cmp_st"; fi

  set +e
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 bash "$SELF" --nope >/dev/null 2>&1
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 2 ]; then st_ok "unknown flag exit 2"
  else st_bad "unknown flag exit=$cmp_st"; fi

  # positional root matches --root
  local outp="$ST_TMP/pos.tsv"
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 bash "$SELF" "$fleet" >"$outp"
  if cmp -s "$out1" "$outp"; then st_ok "positional root matches --root"
  else st_bad "positional root differs"; fi

  # include-root adds the fleet when it is a repo. Commit only root.txt —
  # add -A would try to stage child worktrees and the dot-dir.
  st_init "$fleet" master
  printf 'root\n' >"$fleet/root.txt"
  git -C "$fleet" add -- root.txt >/dev/null
  local ftree f1
  ftree=$(git -C "$fleet" write-tree)
  f1=$(printf 'fleet\n' | git -C "$fleet" commit-tree "$ftree")
  git -C "$fleet" update-ref refs/heads/master "$f1"
  local outr="$ST_TMP/root.tsv" n_with n_without
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    bash "$SELF" --root "$fleet" --include-root >"$outr"
  n_with=$(($(grep -c $'\t' "$outr") - 1))
  n_without=$data_rows
  if [ "$n_with" -eq $((n_without + 1)) ] && grep -q "$fleet"$'\t' "$outr"; then
    st_ok "include-root adds the root row"
  else st_bad "include-root rows=$n_with want $((n_without + 1))"; fi

  # empty root: header only
  mkdir -p "$ST_TMP/empty"
  local oute="$ST_TMP/empty.tsv"
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 bash "$SELF" --root "$ST_TMP/empty" >"$oute"
  if [ "$(cat "$oute")" = "$HEADER" ]; then st_ok "empty root is header only"
  else st_bad "empty root [$(cat "$oute")]"; fi

  # source audit. grep exits 1 on no match; do not let that abort the run.
  local n audit
  audit=$(grep -nE '^[^#[:space:]]*git .* (fetch|push|commit|branch|checkout|reset|rebase|prune|remove)( |$)' "$SELF" || true)
  n=$(printf '%s\n' "$audit" | grep -c . || true)
  if [ "${n:-0}" = 0 ]; then st_ok "no forbidden git subcommand"
  else st_bad "$n forbidden git invocation(s)"; printf '%s\n' "$audit"; fi
  if grep -q -- '--no-optional-locks' "$SELF" && grep -q 'core.hooksPath=/dev/null' "$SELF"; then
    st_ok "read-only git wrapper present"
  else st_bad "read-only git wrapper missing"; fi
  if grep -q 'untracked-files=all' "$SELF"; then st_bad "uses untracked-files=all"
  else st_ok "does not use untracked-files=all"; fi

  case "$fleet" in
    "$ST_TMP"/*) st_ok "fixtures under mktemp" ;;
    *) st_bad "fixtures escaped mktemp" ;;
  esac

  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then exit 1; fi
  exit 0
}

# --- main ---------------------------------------------------------------------

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --include-root) INCLUDE_ROOT=1; shift ;;
    --root)
      [ "$#" -ge 2 ] || usage_err "--root needs a directory"
      ROOT=$2
      shift 2
      ;;
    --root=*) ROOT=${1#*=}; shift ;;
    --compare)
      [ "$#" -ge 2 ] || usage_err "--compare needs a TSV path"
      COMPARE=$2
      shift 2
      ;;
    --compare=*) COMPARE=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    --) shift; break ;;
    -*) usage_err "unknown flag: $1" ;;
    *)
      if [ -n "${POSITIONAL_SET:-}" ]; then
        usage_err "unexpected argument: $1"
      fi
      ROOT=$1
      POSITIONAL_SET=1
      shift
      ;;
  esac
done

if [ "$SELFTEST" = 1 ]; then run_selftest; fi

command -v git >/dev/null 2>&1 || { printf 'souji-census: git not found\n' >&2; exit 1; }
command -v du >/dev/null 2>&1 || { printf 'souji-census: du not found\n' >&2; exit 1; }
command -v find >/dev/null 2>&1 || { printf 'souji-census: find not found\n' >&2; exit 1; }
command -v timeout >/dev/null 2>&1 || { printf 'souji-census: timeout not found\n' >&2; exit 1; }

if [ -n "$COMPARE" ]; then
  emit_compare
  exit $?
fi
emit_census
exit 0
