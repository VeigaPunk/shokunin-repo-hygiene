#!/usr/bin/env bash
# souji-census — repeatable dry-run fleet census (round 6, seat S34 / impl-34).
#
# Independent of tools/souji-census.sh. Same receipt contract as
# tools/souji-verify.spec.md (D1–D3, r5 amendments) plus the r5 coverage-gap
# fail-closed rules (hidden live refs, secret-shaped ledger paths, secret
# paths excluded from content sweeps). Read-only over every surface it
# inspects. No git fetch. Never writes the live ledger, a vault, or a
# sibling lane. Census output goes only to stdout or to --out under the
# lane repo (census/ or results/) or a caller-supplied path the operator
# named; --selftest writes only under mktemp -d.
#
# CLI
#   tools/souji-census.impl-34.sh [--selftest] [--json] [--summary]
#        [--stale-days N] [--ledger PATH] [--out PATH]
#        [--root PATH] [--classify] [--worktrees] [--surface]
#        [--lane NAME] [path...]
#
# With no path and no mode flag, the default census is --surface:
# one row per lane repo, each lane .scratch, each non-main worktree
# registration, and each fleet-root hygiene candidate (checkpoint
# json/png, *.out, *.log, *-draft.*, shokunin.conf.* snapshots).
#
# Output (default), one TSV line per row:
#   CENSUS<TAB>kind<TAB>path<TAB>bytes<TAB>mtime<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence
# --summary adds one JSON object on stdout after the rows. --json emits one
# JSON object per row; it does not add the summary unless --summary is set.
#
# Exit: 0 evaluated (including all-NOT-SAFE); 1 selftest failure or
# evaluation error; 2 usage. NOT-SAFE is the safe default, not an error.
#
# Env: SHOKUNIN_ROOT, SOUJI_LEDGER, SOUJI_SELFTEST_ACTIVE.
# Dependencies: bash, coreutils (sha256sum, stat, date, mktemp, readlink,
# find, sort, wc, cut, tr, cmp), git, rg. No grep/xargs/sed/awk.
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SHOKUNIN_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"
SHOKUNIN_ROOT="$(readlink -m -- "$SHOKUNIN_ROOT" 2>/dev/null || printf '%s' "$SHOKUNIN_ROOT")"
LEDGER="${SOUJI_LEDGER:-$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv}"

STALE_DAYS=1
JSON=0
SUMMARY=0
SELFTEST=0
DO_CLASSIFY=0
DO_WORKTREES=0
DO_SURFACE=0
OUT_PATH=""
LANE_FILTER=""
TARGETS=()

R_VERDICT=NOT-SAFE
R_RECEIPT=none
R_EVIDENCE=no-receipt
R_KIND=artifact
NOTES=()
FAIL_REASON=none

declare -A WT_MAP=()
N_ROWS=0
N_SAFE=0
N_NOTSAFE=0
N_REFUSAL=0

usage() {
  local line
  while IFS= read -r line; do
    case "$line" in
      '#'*) line=${line#'#'}; line=${line#' '} ;;
      *) break ;;
    esac
    printf '%s\n' "$line"
  done < "$SELF"
  exit "${1:-0}"
}
usage_err() { printf 'souji-census: %s\n' "$1" >&2; usage 2; }

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }
real_path() { readlink -f -- "$1" 2>/dev/null || true; }

san() {
  local s=${1:-}
  s=${s//$'\t'/ }
  s=${s//$'\n'/ }
  s=${s//$'\r'/ }
  printf '%s' "$s"
}

path_has_symlink() {
  local p=$1 cur="" part root
  [ -n "$p" ] || return 1
  [ -L "$p" ] && return 0
  root=$(canon_path "${SHOKUNIN_ROOT:-/}")
  case "$p" in
    /*) cur="" ;;
    *) cur="." ;;
  esac
  local IFS='/'
  set -f
  for part in $p; do
    [ -n "$part" ] || continue
    if [ -z "$cur" ]; then
      cur="/$part"
    else
      cur="$cur/$part"
    fi
    if [ -L "$cur" ]; then
      case "$cur" in
        "$root"|"$root"/*)
          set +f
          return 0
          ;;
      esac
    fi
  done
  set +f
  return 1
}

is_secret_shaped() {
  local comp lc
  local IFS='/'
  set -f
  for comp in $1; do
    [ -n "$comp" ] || continue
    lc=${comp,,}
    case "$lc" in
      *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem)
        set +f
        return 0
        ;;
    esac
  done
  set +f
  return 1
}

is_hex64() {
  case "$1" in
    ""|*[!0-9a-f]*) return 1 ;;
  esac
  [ "${#1}" = 64 ]
}

find_repo_for() {
  local p=$1 d top
  if [ -d "$p" ]; then d=$p; else d=$(dirname -- "$p"); fi
  d=$(canon_path "$d")
  if top=$(git -C "$d" rev-parse --show-toplevel 2>/dev/null) && [ -n "$top" ]; then
    printf '%s\n' "$top"
    return 0
  fi
  while :; do
    if [ -e "$d/.git" ]; then
      printf '%s\n' "$d"
      return 0
    fi
    [ "$d" = "/" ] && break
    d=$(dirname -- "$d")
  done
  return 1
}

# D1 + r5: remote-tracking refs only. Local heads never establish pushed.
resolve_default_ref() {
  local repo=$1 b refs line only="" count=0
  b=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
  b=${b#origin/}
  if [ -n "$b" ] && git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$b" 2>/dev/null; then
    printf 'refs/remotes/origin/%s\n' "$b"
    return 0
  fi
  refs=$(git -C "$repo" for-each-ref --format='%(refname)' 'refs/remotes/origin' 2>/dev/null || true)
  if [ -n "$refs" ]; then
    while IFS= read -r line; do
      case "$line" in
        ""|refs/remotes/origin/HEAD) continue ;;
        *) only=$line; count=$((count + 1)) ;;
      esac
    done <<< "$refs"
  fi
  if [ "$count" = 1 ] && [ -n "$only" ]; then
    printf '%s\n' "$only"
    return 0
  fi
  return 1
}

file_sha() {
  [ -f "$1" ] && [ ! -L "$1" ] || return 1
  sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1
}

# Return 0 + digest on stdout; 2 if any symlink is in scope; 3 if any
# secret-shaped path is in scope (neither case hashes file contents).
dir_digest() {
  local d=$1
  [ -d "$d" ] || return 1
  local hit=""
  hit=$(find "$d" -path "$d/.git" -prune -o -type l -print -quit 2>/dev/null || true)
  if [ -n "$hit" ]; then
    return 2
  fi
  local listing="" f
  listing=$(find "$d" -path "$d/.git" -prune -o -type f -print 2>/dev/null | sort || true)
  if [ -n "$listing" ]; then
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      if is_secret_shaped "$f"; then
        return 3
      fi
    done <<< "$listing"
  fi
  if [ -z "$listing" ]; then
    printf '%s\n' "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    return 0
  fi
  local acc="" h
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    h=$(sha256sum -- "$f" 2>/dev/null | cut -d' ' -f1 || true)
    acc+="${h}  ${f#"$d"/}"$'\n'
  done <<< "$listing"
  printf '%s' "$acc" | sha256sum | cut -d' ' -f1
}

scratch_type() {
  local p=$1 base comp
  local IFS='/'
  set -f
  for comp in $p; do
    if [ "$comp" = ".scratch" ]; then
      set +f
      printf 'scratch-dir\n'
      return 0
    fi
  done
  set +f
  base=$(basename -- "$p")
  case "$base" in
    *.out|*.log) printf 'ext\n'; return 0 ;;
    *-draft.*) printf 'draft\n'; return 0 ;;
    *checkpoint*.json|*checkpoint*.png|*ckpt*.json|*ckpt*.png|*.ckpt|launch-*.json)
      printf 'checkpoint\n'
      return 0
      ;;
    shokunin.conf.*) printf 'snapshot\n'; return 0 ;;
  esac
  return 1
}

# Content sweep that sees hidden files (r5 gap) and never opens secret-shaped
# paths. Census / tests / quarantine fragments are excluded (D3).
# .scratch trees are not opened: a 16G live scratch must not be content-scanned.
# If the repo has a .scratch and the target lives outside it, refs are unknown
# (fail closed — a scratch-only citation cannot authorize SAFE(stale)).
count_live_refs() {
  local target=$1 repo=$2
  local rel="" base n out status has_scratch=0 inside_scratch=0
  repo=${repo:-$SHOKUNIN_ROOT}
  [ -d "$repo" ] || { printf '0\n'; return 0; }
  case "$target" in
    "$repo"/*) rel=${target#"$repo"/} ;;
  esac
  base=$(basename -- "$target")
  # A directory named .scratch is too generic to content-sweep (and a sweep
  # would walk live lane trees). Fail closed: unknown refs, never stale.
  if [ "$base" = ".scratch" ]; then
    printf 'unknown\n'
    return 0
  fi
  case "$target" in
    */.scratch|*/.scratch/*) inside_scratch=1 ;;
  esac
  if [ -d "$repo/.scratch" ]; then
    has_scratch=1
  elif find "$repo" -type d -name .scratch -prune -print -quit 2>/dev/null | grep -q .; then
    has_scratch=1
  fi
  local -a globs=(
    -g '!.git/**' -g '!**/.git/**'
    -g '!**/.scratch/**'
    -g '!souji-shokunin/census/**' -g '!**/souji-shokunin/census/**'
    -g '!souji-shokunin/tests/**' -g '!**/souji-shokunin/tests/**'
    -g '!**/.ufo-quarantine/**'
    -g '!**/.ufo/state/**' -g '!**/.ufo/watchdog.log'
    -g '!**/*.env' -g '!**/.env' -g '!**/.env.*' -g '!**/.envrc'
    -g '!**/*credential*' -g '!**/*secret*' -g '!**/*.pem'
    -g '!**/id_*' -g '!**/credentials/**' -g '!**/secrets/**'
  )
  if [ -n "$rel" ]; then
    globs+=(-g "!$rel" -g "!./$rel" -g "!**/$rel")
  fi
  if ! command -v timeout >/dev/null 2>&1; then
    printf 'unknown\n'
    return 0
  fi
  set +e
  out=$(cd "$repo" && timeout 8 rg -l --hidden --no-ignore --fixed-strings -e "$base" . \
    "${globs[@]}" 2>/dev/null)
  status=$?
  set -e
  if [ "$status" -eq 124 ] || [ "$status" -eq 137 ] || [ "$status" -gt 1 ]; then
    printf 'unknown\n'
    return 0
  fi
  n=0
  if [ -n "$out" ]; then
    local line
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      n=$((n + 1))
    done <<< "$out"
  fi
  if [ "$n" = 0 ] && [ "$has_scratch" = 1 ] && [ "$inside_scratch" = 0 ]; then
    printf 'unknown\n'
    return 0
  fi
  printf '%s\n' "$n"
}

try_pushed() {
  local target=$1 repo=$2 intro ref rel
  rel=$target
  case "$target" in
    "$repo"/*) rel=${target#"$repo"/} ;;
  esac
  intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$rel" 2>/dev/null || true)
  intro=${intro%%$'\n'*}
  if [ -z "$intro" ]; then
    NOTES+=("pushed=no-introducing-commit")
    return 1
  fi
  if ! ref=$(resolve_default_ref "$repo"); then
    FAIL_REASON=pushed-unverifiable
    NOTES+=("pushed=unverifiable(no-default-ref) intro=${intro:0:12}")
    return 1
  fi
  if git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
    R_VERDICT=SAFE
    R_RECEIPT=pushed
    R_EVIDENCE="intro=${intro:0:12} ref=$ref ancestor=yes"
    return 0
  fi
  NOTES+=("pushed=not-ancestor intro=${intro:0:12} ref=$ref")
  return 1
}

ledger_match() {
  local target=$1 isdir=$2 raw=${3:-}
  local line first=1 sp ss vp vs rest
  [ -f "$LEDGER" ] || { NOTES+=("obsidian=no-ledger"); return 1; }
  if is_secret_shaped "$LEDGER"; then
    NOTES+=("obsidian=ledger-secret-shaped")
    FAIL_REASON=secrets-refusal
    return 1
  fi
  local tgt_real
  tgt_real=$(real_path "$target")
  first=1
  while IFS= read -r line || [ -n "$line" ]; do
    if [ "$first" = 1 ]; then
      first=0
      case "$line" in
        source_path$'\t'*) continue ;;
      esac
    fi
    [ -n "$line" ] || continue
    case "$line" in
      '#'*) continue ;;
    esac
    IFS=$'\t' read -r sp ss vp vs rest <<< "$line"
    [ -n "$sp" ] || continue
    if [ "$sp" != "$target" ] && [ "$sp" != "$raw" ]; then
      continue
    fi
    case "$sp" in
      /*) ;;
      *)
        NOTES+=("obsidian=relative-source-path")
        continue
        ;;
    esac
    case "$vp" in
      /*) ;;
      *)
        NOTES+=("obsidian=relative-vault-path")
        continue
        ;;
    esac
    if is_secret_shaped "$sp" || is_secret_shaped "$vp"; then
      NOTES+=("obsidian=secret-shaped-ledger-path")
      FAIL_REASON=secrets-refusal
      R_VERDICT=NOT-SAFE
      R_RECEIPT=secrets-refusal
      R_EVIDENCE="secret-shaped ledger path component; not hashed"
      return 0
    fi
    local vp_real
    vp_real=$(real_path "$vp")
    if [ -n "$tgt_real" ] && [ -n "$vp_real" ] && [ "$vp_real" = "$tgt_real" ]; then
      NOTES+=("obsidian=source-equals-vault")
      continue
    fi
    if [ "$isdir" = 1 ] && [ -n "$vp_real" ] && [ -n "$tgt_real" ]; then
      case "$vp_real" in
        "$tgt_real"/*)
          NOTES+=("obsidian=vault-inside-source")
          continue
          ;;
      esac
    fi
    if [ "$isdir" = 1 ]; then
      if ! is_hex64 "$ss" || ! is_hex64 "$vs"; then
        NOTES+=("obsidian=row-incomplete")
        continue
      fi
      local ds drc
      set +e
      ds=$(dir_digest "$target")
      drc=$?
      set -e
      if [ "$drc" = 2 ]; then
        NOTES+=("obsidian=symlink-present scope=source")
        FAIL_REASON=symlink-present
        R_VERDICT=NOT-SAFE
        R_RECEIPT=symlink-present
        R_EVIDENCE="symlink in source digest scope"
        return 0
      fi
      if [ "$drc" = 3 ]; then
        FAIL_REASON=secrets-refusal
        R_VERDICT=NOT-SAFE
        R_RECEIPT=secrets-refusal
        R_EVIDENCE="secret-shaped path inside source digest; not hashed"
        return 0
      fi
      if [ "$ds" != "$ss" ]; then
        NOTES+=("obsidian=source-digest-mismatch")
        continue
      fi
      if [ ! -d "$vp" ]; then
        NOTES+=("obsidian=vault-unreachable")
        continue
      fi
      set +e
      ds=$(dir_digest "$vp")
      drc=$?
      set -e
      if [ "$drc" = 2 ]; then
        NOTES+=("obsidian=symlink-present scope=vault")
        FAIL_REASON=symlink-present
        R_VERDICT=NOT-SAFE
        R_RECEIPT=symlink-present
        R_EVIDENCE="symlink in vault digest scope"
        return 0
      fi
      if [ "$drc" = 3 ]; then
        FAIL_REASON=secrets-refusal
        R_VERDICT=NOT-SAFE
        R_RECEIPT=secrets-refusal
        R_EVIDENCE="secret-shaped path inside vault digest; not hashed"
        return 0
      fi
      if [ "$ds" != "$vs" ]; then
        NOTES+=("obsidian=vault-digest-mismatch")
        continue
      fi
      R_VERDICT=SAFE
      R_RECEIPT=moved-to-obsidian
      R_EVIDENCE="ledger=source+vault-digest vault=$vp"
      return 0
    fi
    if [ ! -f "$target" ] || [ -L "$target" ]; then
      NOTES+=("obsidian=source-absent-or-link")
      continue
    fi
    if ! is_hex64 "$ss" || ! is_hex64 "$vs"; then
      NOTES+=("obsidian=row-incomplete")
      continue
    fi
    local got
    got=$(file_sha "$target" || true)
    if [ "$got" != "$ss" ]; then
      NOTES+=("obsidian=source-sha-mismatch")
      continue
    fi
    if [ ! -f "$vp" ] || [ -L "$vp" ]; then
      NOTES+=("obsidian=vault-unreachable vault=$vp")
      continue
    fi
    got=$(file_sha "$vp" || true)
    if [ "$got" != "$vs" ]; then
      NOTES+=("obsidian=vault-sha-mismatch")
      continue
    fi
    R_VERDICT=SAFE
    R_RECEIPT=moved-to-obsidian
    R_EVIDENCE="ledger-row vault=$vp source-sha256=${ss:0:12}"
    return 0
  done < "$LEDGER"
  NOTES+=("obsidian=no-matching-ledger-row")
  return 1
}

try_stale() {
  local target=$1 repo=$2 kind mtime now age refs
  kind=$(scratch_type "$target") || { NOTES+=("stale=not-scratch-type"); return 1; }
  if [ -L "$target" ]; then
    FAIL_REASON=symlink-present
    NOTES+=("stale=symlink-present")
    return 1
  fi
  mtime=$(stat -c %Y -- "$target" 2>/dev/null || true)
  [ -n "$mtime" ] || { NOTES+=("stale=no-mtime"); return 1; }
  now=$(date +%s)
  age=$(( now - mtime ))
  if [ "$age" -le $(( STALE_DAYS * 86400 )) ]; then
    NOTES+=("stale=mtime-age-days=$(( age / 86400 ))<=$STALE_DAYS")
    return 1
  fi
  refs=$(count_live_refs "$target" "$repo")
  if [ "${refs:-1}" != 0 ]; then
    NOTES+=("stale=live-refs=$refs")
    return 1
  fi
  R_VERDICT=SAFE
  R_RECEIPT=stale
  R_EVIDENCE="scratch-type=$kind refs=0 mtime-age-days=$(( age / 86400 ))"
  return 0
}

evaluate_repo_root() {
  local target=$1 unpushed dirty
  R_KIND=repo-root
  if ledger_match "$target" 1; then
    return 0
  fi
  if [ "${FAIL_REASON:-none}" = secrets-refusal ] || [ "${FAIL_REASON:-none}" = symlink-present ]; then
    R_VERDICT=NOT-SAFE
    R_RECEIPT=$FAIL_REASON
    return 0
  fi
  unpushed=$(git -C "$target" log --branches --not --remotes --oneline 2>/dev/null | wc -l || true)
  dirty=$(git -C "$target" status --porcelain 2>/dev/null | wc -l || true)
  unpushed=${unpushed// /}
  dirty=${dirty// /}
  R_VERDICT=NOT-SAFE
  if [ "${unpushed:-0}" -gt 0 ]; then
    R_RECEIPT=unpushed
  elif [ "${dirty:-0}" -gt 0 ]; then
    R_RECEIPT=dirty
  else
    R_RECEIPT=none
  fi
  R_EVIDENCE="unpushed=${unpushed:-0} dirty=${dirty:-0}"
  return 0
}

evaluate_worktree() {
  local target=$1 meta=$2 owner head branch unp uniq dirty st present
  R_KIND=worktree-registration
  IFS=$'\t' read -r owner head branch <<< "$meta"
  if [ -d "$target" ]; then present=present; else present=absent; fi
  if [ -n "$branch" ]; then
    unp=$(git -C "$owner" log --oneline "$branch" --not --remotes 2>/dev/null | wc -l || true)
    unp=${unp// /}
    if [ "${unp:-0}" -gt 0 ]; then
      R_VERDICT=NOT-SAFE
      R_RECEIPT=unpushed-branch
      R_EVIDENCE="branch=${branch#refs/heads/} unpushed=$unp dir=$present owner=$(basename -- "$owner")"
      return 0
    fi
  fi
  if [ "$present" = absent ]; then
    uniq=$(git -C "$owner" log --oneline "$head" --not --all 2>/dev/null | wc -l || true)
    uniq=${uniq// /}
    if [ "${uniq:-1}" = 0 ]; then
      R_VERDICT=SAFE
      R_RECEIPT=metadata-prune
      R_EVIDENCE="dir=absent unique=0 head=${head:0:12} owner=$(basename -- "$owner")"
      return 0
    fi
    R_VERDICT=NOT-SAFE
    R_RECEIPT=none
    R_EVIDENCE="dir=absent unique=$uniq head=${head:0:12} owner=$(basename -- "$owner")"
    return 0
  fi
  if st=$(git -C "$target" status --porcelain 2>/dev/null); then
    dirty=0
    if [ -n "$st" ]; then
      local line
      while IFS= read -r line; do
        [ -n "$line" ] && dirty=$((dirty + 1))
      done <<< "$st"
    fi
    if [ "$dirty" -gt 0 ]; then
      R_VERDICT=NOT-SAFE
      R_RECEIPT=dirty
      R_EVIDENCE="dir=present dirty=$dirty owner=$(basename -- "$owner")"
    else
      R_VERDICT=NOT-SAFE
      R_RECEIPT=none
      R_EVIDENCE="dir=present clean head=${head:0:12} owner=$(basename -- "$owner")"
    fi
  else
    R_VERDICT=NOT-SAFE
    R_RECEIPT=dirty
    R_EVIDENCE="dir=present status-unverifiable owner=$(basename -- "$owner")"
  fi
  return 0
}

evaluate_artifact() {
  local target=$1 raw=$2 repo="" isdir=0
  R_KIND=artifact
  [ -d "$target" ] && isdir=1
  repo=$(find_repo_for "$target") || repo=""
  if [ -n "$repo" ] && try_pushed "$target" "$repo"; then
    return 0
  fi
  if [ -L "$target" ]; then
    R_VERDICT=NOT-SAFE
    R_RECEIPT=symlink-present
    R_EVIDENCE="symlink target; not followed"
    return 0
  fi
  if ledger_match "$target" "$isdir" "$raw"; then
    return 0
  fi
  if [ "${R_RECEIPT:-}" = secrets-refusal ] || [ "${R_RECEIPT:-}" = symlink-present ]; then
    return 0
  fi
  if try_stale "$target" "$repo"; then
    return 0
  fi
  if [ "${FAIL_REASON:-none}" = symlink-present ]; then
    R_VERDICT=NOT-SAFE
    R_RECEIPT=symlink-present
    R_EVIDENCE="symlink-present; stale receipt refused"
    return 0
  fi
  R_VERDICT=NOT-SAFE
  R_RECEIPT="${FAIL_REASON:-none}"
  local joined=""
  if [ "${#NOTES[@]}" -gt 0 ]; then
    local n
    joined=""
    for n in "${NOTES[@]}"; do
      if [ -n "$joined" ]; then joined+="; "; fi
      joined+="$n"
    done
  else
    joined="no-receipt"
  fi
  R_EVIDENCE=$(san "$joined")
  return 0
}

evaluate_path() {
  local raw=$1 target
  R_VERDICT=NOT-SAFE
  R_RECEIPT=none
  R_EVIDENCE=no-receipt
  R_KIND=artifact
  NOTES=()
  FAIL_REASON=none
  if [ -z "$raw" ]; then
    R_RECEIPT=unreachable
    R_EVIDENCE="empty-arg"
    return 0
  fi
  if path_has_symlink "$raw"; then
    R_RECEIPT=symlink-present
    R_EVIDENCE="symlink target; not followed"
    return 0
  fi
  target=$(canon_path "$raw")
  if is_secret_shaped "$target" || is_secret_shaped "$raw"; then
    R_RECEIPT=secrets-refusal
    R_EVIDENCE="secret-shaped path component; not read"
    return 0
  fi
  case "$target" in
    */.ufo/state|*/.ufo/state/*|*/.ufo/watchdog.log)
      R_RECEIPT=off-limits
      R_EVIDENCE="operator/driver surface; not classified for removal"
      return 0
      ;;
  esac
  if [ -d "$target" ] && [ -d "$target/.git" ]; then
    evaluate_repo_root "$target"
    return 0
  fi
  if [ -n "${WT_MAP[$target]:-}" ]; then
    evaluate_worktree "$target" "${WT_MAP[$target]}"
    return 0
  fi
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    R_RECEIPT=unreachable
    R_EVIDENCE="missing path"
    return 0
  fi
  evaluate_artifact "$target" "$raw"
  return 0
}

_wt_record() {
  local repo=$1 path=$2 head=$3 branch=$4 cp
  [ -n "$path" ] || return 0
  [ "$path" = "$repo" ] && return 0
  cp=$(canon_path "$path")
  WT_MAP["$cp"]="$repo"$'\t'"$head"$'\t'"$branch"
  return 0
}

scan_worktrees() {
  local repo path head branch line
  WT_MAP=()
  for repo in "$SHOKUNIN_ROOT" "$SHOKUNIN_ROOT"/*-shokunin; do
    [ -d "$repo" ] || continue
    [ -e "$repo/.git" ] || continue
    if [ -n "$LANE_FILTER" ]; then
      case "$(basename -- "$repo")" in
        "$LANE_FILTER"|"$LANE_FILTER-shokunin") ;;
        *) continue ;;
      esac
    fi
    path=""
    head=""
    branch=""
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        'worktree '*)
          if [ -n "$path" ]; then _wt_record "$repo" "$path" "$head" "$branch"; fi
          path=${line#worktree }
          head=""
          branch=""
          ;;
        'HEAD '*) head=${line#HEAD } ;;
        'branch '*) branch=${line#branch } ;;
        'detached'*) branch="" ;;
        *) ;;
      esac
    done < <(git -C "$repo" worktree list --porcelain 2>/dev/null || true)
    if [ -n "$path" ]; then _wt_record "$repo" "$path" "$head" "$branch"; fi
  done
  return 0
}

path_bytes() {
  local p=$1
  if [ -L "$p" ] || [ ! -e "$p" ]; then
    printf '0'
    return 0
  fi
  if [ -f "$p" ]; then
    stat -c %s -- "$p" 2>/dev/null || printf '0'
    return 0
  fi
  if [ -d "$p" ]; then
    du -sb -- "$p" 2>/dev/null | cut -f1 || printf '0'
    return 0
  fi
  printf '0'
}

path_mtime() {
  local p=$1
  if [ -e "$p" ] || [ -L "$p" ]; then
    stat -c %Y -- "$p" 2>/dev/null || printf '0'
  else
    printf '0'
  fi
}

emit_row() {
  local path=$1 kind=$2 verdict=$3 receipt=$4 evidence=$5
  local bytes mtime
  bytes=$(path_bytes "$path")
  mtime=$(path_mtime "$path")
  evidence=$(san "$evidence")
  N_ROWS=$((N_ROWS + 1))
  case "$verdict" in
    SAFE) N_SAFE=$((N_SAFE + 1)) ;;
    *) N_NOTSAFE=$((N_NOTSAFE + 1)) ;;
  esac
  case "$receipt" in
    secrets-refusal|off-limits) N_REFUSAL=$((N_REFUSAL + 1)) ;;
  esac
  if [ "$JSON" = 1 ]; then
    printf '{"path":"%s","kind":"%s","bytes":%s,"mtime":%s,"verdict":"%s","receipt":"%s","evidence":"%s"}\n' \
      "$(json_escape "$path")" "$(json_escape "$kind")" "${bytes:-0}" "${mtime:-0}" \
      "$verdict" "$receipt" "$(json_escape "$evidence")"
  else
    printf 'CENSUS\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$kind" "$path" "${bytes:-0}" "${mtime:-0}" "$verdict" "$receipt" "$evidence"
  fi
}

emit_summary() {
  local mode="dry-run"
  if [ "$JSON" = 1 ] || [ "$SUMMARY" = 1 ]; then
    printf '{"summary":true,"mode":"%s","rows":%s,"SAFE":%s,"NOT-SAFE":%s,"refusals":%s,"root":"%s","ledger":"%s","stale_days":%s,"impl":"impl-34"}\n' \
      "$mode" "$N_ROWS" "$N_SAFE" "$N_NOTSAFE" "$N_REFUSAL" \
      "$(json_escape "$SHOKUNIN_ROOT")" "$(json_escape "$LEDGER")" "$STALE_DAYS"
  fi
}

classify_one() {
  local raw=$1
  evaluate_path "$raw"
  emit_row "$raw" "$R_KIND" "$R_VERDICT" "$R_RECEIPT" "$R_EVIDENCE"
}

surface_candidates() {
  local repo base
  if [ -z "$LANE_FILTER" ] || [ "$LANE_FILTER" = "fleet" ] || [ "$LANE_FILTER" = "$(basename -- "$SHOKUNIN_ROOT")" ]; then
    classify_one "$SHOKUNIN_ROOT"
    local f
    for f in "$SHOKUNIN_ROOT"/launch-*.json \
             "$SHOKUNIN_ROOT"/*checkpoint*.json \
             "$SHOKUNIN_ROOT"/*checkpoint*.png \
             "$SHOKUNIN_ROOT"/*.out \
             "$SHOKUNIN_ROOT"/*.log \
             "$SHOKUNIN_ROOT"/*-draft.* \
             "$SHOKUNIN_ROOT"/shokunin.conf.*; do
      [ -e "$f" ] || continue
      classify_one "$f"
    done
    if [ -d "$SHOKUNIN_ROOT/.scratch" ]; then
      classify_one "$SHOKUNIN_ROOT/.scratch"
    fi
  fi
  for repo in "$SHOKUNIN_ROOT"/*-shokunin; do
    [ -d "$repo" ] || continue
    [ -e "$repo/.git" ] || continue
    base=$(basename -- "$repo")
    if [ -n "$LANE_FILTER" ]; then
      case "$base" in
        "$LANE_FILTER"|"${LANE_FILTER}-shokunin") ;;
        *) continue ;;
      esac
    fi
    classify_one "$repo"
    if [ -d "$repo/.scratch" ]; then
      classify_one "$repo/.scratch"
    fi
  done
  local wt
  if [ "${#WT_MAP[@]}" -gt 0 ]; then
    while IFS= read -r wt; do
      [ -n "$wt" ] || continue
      classify_one "$wt"
    done < <(printf '%s\n' "${!WT_MAP[@]}" | sort)
  fi
}

# ---------------------------------------------------------------- selftest --

ST_FLEET=""
ST_TMP=""
ST_LEDGER=""
ST_PASS=0
ST_FAIL=0

st_note() { printf '%s\n' "$*"; }

st_case() {
  local id=$1 wv=$2 wr=$3 wsub=$4
  shift 4
  local out status line kind path bytes mtime v r ev rest
  set +e
  out=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
    "$SELF" --classify --stale-days 1 "$@" 2>&1)
  status=$?
  set -e
  if [ "$status" -ne 0 ]; then
    ST_FAIL=$((ST_FAIL + 1))
    st_note "FAIL $id: exit=$status out=$out"
    return 0
  fi
  line=${out%%$'\n'*}
  rest=$line
  local tag
  tag=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  kind=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  path=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  bytes=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  mtime=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  v=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  r=${rest%%$'\t'*}; ev=${rest#*$'\t'}
  if [ "$tag" != "CENSUS" ]; then
    ST_FAIL=$((ST_FAIL + 1))
    st_note "FAIL $id: bad line '$line'"
    return 0
  fi
  if [ "$v" != "$wv" ] || [ "$r" != "$wr" ]; then
    ST_FAIL=$((ST_FAIL + 1))
    st_note "FAIL $id: got $v($r) want $wv($wr) ev='$ev'"
    return 0
  fi
  if [ -n "$wsub" ]; then
    case "$ev" in
      *"$wsub"*) ;;
      *)
        ST_FAIL=$((ST_FAIL + 1))
        st_note "FAIL $id: evidence '$ev' lacks '$wsub'"
        return 0
        ;;
    esac
  fi
  ST_PASS=$((ST_PASS + 1))
  st_note "PASS $id $v($r)"
  return 0
}

st_status() {
  local id=$1 want=$2
  shift 2
  local status
  set +e
  env SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
    "$SELF" "$@" >/dev/null 2>&1
  status=$?
  set -e
  if [ "$status" = "$want" ]; then
    ST_PASS=$((ST_PASS + 1))
    st_note "PASS $id exit=$status"
  else
    ST_FAIL=$((ST_FAIL + 1))
    st_note "FAIL $id exit=$status want=$want"
  fi
  return 0
}

st_commit() {
  local repo=$1 parent=$2 msg=$3 tr sha
  git -C "$repo" add -A >/dev/null 2>&1
  tr=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr" -p "$parent")
  else
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr")
  fi
  printf '%s' "$sha"
}

st_init_repo() {
  local p=$1 b=${2:-master}
  # Empty template: sample hooks are unused, and copying them fails closed
  # when /tmp is under a user quota even though df still shows free space.
  git init -q --template= --initial-branch="$b" "$p"
  git -C "$p" symbolic-ref HEAD "refs/heads/$b"
}

st_register_worktree() {
  local owner=$1 name=$2 wt=$3 sha=$4 br=$5 adm
  adm="$owner/.git/worktrees/$name"
  mkdir -p "$adm"
  if [ -n "$br" ]; then
    printf 'ref: %s\n' "$br" > "$adm/HEAD"
  else
    printf '%s\n' "$sha" > "$adm/HEAD"
  fi
  printf '../..\n' > "$adm/commondir"
  printf '%s\n' "$wt/.git" > "$adm/gitdir"
  if [ -d "$wt" ]; then
    printf 'gitdir: %s\n' "$adm" > "$wt/.git"
  fi
  return 0
}

st_pick_tmp() {
  local base cand
  # /var/tmp and $HOME sit on the root filesystem. /tmp is tmpfs and, on this
  # host, can return "Disk quota exceeded" while df still shows free space.
  for base in /var/tmp "$HOME" "${TMPDIR:-}" /tmp; do
    [ -n "$base" ] && [ -d "$base" ] && [ -w "$base" ] || continue
    cand=$(mktemp -d "$base/souji-census-selftest.XXXXXX" 2>/dev/null || true)
    [ -n "$cand" ] && [ -d "$cand" ] || continue
    if dd if=/dev/zero of="$cand/.probe" bs=1024 count=64 status=none 2>/dev/null; then
      rm -f -- "$cand/.probe"
      printf '%s\n' "$cand"
      return 0
    fi
    rm -rf -- "$cand"
  done
  return 1
}

st_build_fixtures() {
  ST_TMP=$(st_pick_tmp) || {
    printf 'souji-census: cannot allocate selftest temp dir\n' >&2
    exit 1
  }
  trap 'rm -rf -- "$ST_TMP"' EXIT
  ST_FLEET="$ST_TMP/fleet"
  ST_LEDGER="$ST_TMP/ledger.tsv"
  mkdir -p "$ST_FLEET"

  local R="$ST_FLEET/repo-shokunin"
  st_init_repo "$R" master
  mkdir -p "$R/keep" "$R/local" "$R/.scratch" "$R/souji-shokunin/census" "$R/souji-shokunin/tests" "$R/.ufo"
  printf 'f1 payload\n' > "$R/keep/f1.txt"
  local c1
  c1=$(st_commit "$R" "" "c1 adds keep/f1.txt")
  printf 'extra\n' > "$R/keep/extra.txt"
  local c2
  c2=$(st_commit "$R" "$c1" "c2 pushes keep/extra.txt")
  git -C "$R" update-ref refs/remotes/origin/master "$c2"
  git -C "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$R" update-ref refs/heads/master "$c2"
  printf 'f2 payload\n' > "$R/local/f2.txt"
  printf 'f6 payload\n' > "$R/keep/f6.txt"
  local c3
  c3=$(st_commit "$R" "$c2" "c3 local-only adds local/f2.txt and keep/f6.txt")
  git -C "$R" update-ref refs/heads/master "$c3"
  printf 'self mention old-f7.out\n' > "$R/.scratch/old-f7.out"
  printf 'self mention old-f8.out\n' > "$R/.scratch/old-f8.out"
  printf 'self mention old-e8.out\n' > "$R/.scratch/old-e8.out"
  printf 'self mention hidden-ref.out\n' > "$R/.scratch/hidden-ref.out"
  printf 'live ref to old-e8.out here\n' > "$R/notes.md"
  printf 'hidden cites hidden-ref.out\n' > "$R/.ufo/current.md"
  printf '{"row":"old-f8.out"}\n' > "$R/souji-shokunin/census/ref-census.json"
  printf 'old-f8.out cited here\n' > "$R/souji-shokunin/tests/ref-tests.txt"
  printf 'x\n' > "$R/x.env"
  mkdir -p "$R/credentials"
  printf 'note\n' > "$R/credentials/note.txt"
  printf 'secret body must not be hashed\n' > "$R/credentials/fake.env"
  printf 'alias payload\n' > "$R/keep/payload.txt"
  ln -s payload.txt "$R/keep/alias.txt"
  git -C "$R" update-ref refs/heads/wt-unpushed "$c3"
  git -C "$R" update-ref refs/heads/wt-pushed "$c2"
  st_register_worktree "$R" wt-f4 "$ST_TMP/wt-f4" "$c2" ""
  st_register_worktree "$R" wt-f5 "$ST_TMP/wt-f5" "$c3" "refs/heads/wt-unpushed"
  st_register_worktree "$R" wt-f5b "$ST_TMP/wt-f5b" "$c2" "refs/heads/wt-pushed"
  st_register_worktree "$R" wt-dirty "$ST_TMP/wt-dirty" "$c1" ""
  mkdir -p "$ST_TMP/wt-dirty"
  printf 'gitdir: %s\n' "$R/.git/worktrees/wt-dirty" > "$ST_TMP/wt-dirty/.git"
  printf 'untracked\n' > "$ST_TMP/wt-dirty/stray.txt"

  local R9="$ST_FLEET/repo9-shokunin"
  st_init_repo "$R9" master
  printf 'f9 payload\n' > "$R9/f9.txt"
  local c9
  c9=$(st_commit "$R9" "" "c9 adds f9.txt")
  git -C "$R9" update-ref refs/heads/master "$c9"
  git -C "$R9" update-ref refs/remotes/origin/master "$c9"

  local RK="$ST_FLEET/kotodama-shaped-shokunin"
  st_init_repo "$RK" main
  printf 'tracked\n' > "$RK/tracked.txt"
  local k1
  k1=$(st_commit "$RK" "" "k1 tracked.txt")
  git -C "$RK" update-ref refs/remotes/origin/main "$k1"
  git -C "$RK" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
  printf 'more\n' >> "$RK/tracked.txt"
  printf 'new file\n' > "$RK/added.txt"
  local k2
  k2=$(st_commit "$RK" "$k1" "k2 local work")
  git -C "$RK" update-ref refs/heads/main "$k2"
  printf 'dirt\n' >> "$RK/tracked.txt"

  local VS SRC VP
  mkdir -p "$ST_TMP/vault"
  printf 'f6 payload\n' > "$ST_TMP/vault/f6.txt"
  VS=$(file_sha "$ST_TMP/vault/f6.txt")
  SRC=$(canon_path "$R/keep/f6.txt")
  VP=$(canon_path "$ST_TMP/vault/f6.txt")
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-18\tselftest\n' \
      "$SRC" "$(file_sha "$SRC")" "$VP" "$VS"
  } > "$ST_LEDGER"

  local RP="$ST_FLEET/preserved-repo-shokunin" VD="$ST_TMP/vault/preserved-repo"
  st_init_repo "$RP" master
  printf 'kept\n' > "$RP/kept.txt"
  local cp1
  cp1=$(st_commit "$RP" "" "p1 kept.txt")
  git -C "$RP" update-ref refs/heads/master "$cp1"
  mkdir -p "$VD"
  printf 'kept\n' > "$VD/kept.txt"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tselftest-dir\n' \
    "$(canon_path "$RP")" "$(dir_digest "$RP")" \
    "$(canon_path "$VD")" "$(dir_digest "$VD")" >> "$ST_LEDGER"

  mkdir -p "$ST_TMP/vault/credentials"
  printf 'secret body must not be hashed\n' > "$ST_TMP/vault/credentials/fake.env"
  printf 'local ledger-row source\n' > "$R/keep/row-src.txt"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tsecret-vault\n' \
    "$(canon_path "$R/keep/row-src.txt")" "$(file_sha "$R/keep/row-src.txt")" \
    "$(canon_path "$ST_TMP/vault/credentials/fake.env")" "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef" \
    >> "$ST_LEDGER"

  local RN="$ST_FLEET/norefs-shokunin"
  st_init_repo "$RN" work
  printf 'norefs\n' > "$RN/tracked.txt"
  local cn
  cn=$(st_commit "$RN" "" "n1 tracked.txt")
  git -C "$RN" update-ref refs/heads/work "$cn"

  printf 'unreferenced outside scratch\n' > "$R/old-stray.out"
  touch -d '3 days ago' \
    "$R/.scratch/old-f7.out" \
    "$R/.scratch/old-f8.out" \
    "$R/.scratch/old-e8.out" \
    "$R/.scratch/hidden-ref.out" \
    "$R/old-stray.out"
  return 0
}

st_audit_source() {
  local n=0 line
  while IFS= read -r line; do
    case "$line" in
      ''|\#*) continue ;;
    esac
    if [[ "$line" =~ git[[:space:]]+(fetch|push|commit|branch|checkout|reset|rebase|prune)([[:space:]]|$) ]]; then
      n=$((n + 1))
    fi
  done < "$SELF"
  if [ "$n" = 0 ]; then
    ST_PASS=$((ST_PASS + 1))
    st_note "PASS H1 no forbidden git subcommand"
  else
    ST_FAIL=$((ST_FAIL + 1))
    st_note "FAIL H1 $n forbidden git invocation(s)"
  fi
  case "$ST_FLEET" in
    "$ST_TMP"/*)
      ST_PASS=$((ST_PASS + 1))
      st_note "PASS H5 fixtures under mktemp -d ($ST_TMP)"
      ;;
    *)
      ST_FAIL=$((ST_FAIL + 1))
      st_note "FAIL H5 fixtures not under mktemp"
      ;;
  esac
  return 0
}

run_selftest() {
  if [ "${SOUJI_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'souji-census: refusing nested --selftest\n' >&2
    exit 1
  fi
  st_build_fixtures
  local R="$ST_FLEET/repo-shokunin"

  st_case F1 SAFE pushed refs/remotes/origin/master "$R/keep/f1.txt"
  st_case F2 NOT-SAFE none "" "$R/local/f2.txt"
  st_case F3 NOT-SAFE unpushed "unpushed=1 dirty=1" "$ST_FLEET/kotodama-shaped-shokunin"
  st_case F4 SAFE metadata-prune "dir=absent unique=0" "$ST_TMP/wt-f4"
  st_case F5 NOT-SAFE unpushed-branch "unpushed=1" "$ST_TMP/wt-f5"
  st_case F6 SAFE moved-to-obsidian "vault=" "$R/keep/f6.txt"
  st_case F7 SAFE stale "refs=0" "$R/.scratch/old-f7.out"
  st_case F8 SAFE stale "refs=0" "$R/.scratch/old-f8.out"
  st_case F9 SAFE pushed refs/remotes/origin/master "$ST_FLEET/repo9-shokunin/f9.txt"
  st_case F10 NOT-SAFE secrets-refusal "" "$R/x.env"
  st_case E1 NOT-SAFE dirty "dirty=" "$ST_TMP/wt-dirty"
  st_case E2 NOT-SAFE secrets-refusal "" "$R/credentials/note.txt"
  st_case E3 SAFE metadata-prune "unique=0" "$ST_TMP/wt-f5b"
  st_case E4 NOT-SAFE unreachable "" "$ST_TMP/no-such-target"
  st_case E5 NOT-SAFE unreachable "" ""
  st_case E6 SAFE moved-to-obsidian "source+vault-digest" "$ST_FLEET/preserved-repo-shokunin"
  st_case E7 NOT-SAFE pushed-unverifiable "unverifiable" "$ST_FLEET/norefs-shokunin/tracked.txt"
  st_case E8 NOT-SAFE none "live-refs=1" "$R/.scratch/old-e8.out"
  st_case G1 NOT-SAFE none "live-refs=" "$R/.scratch/hidden-ref.out"
  st_case G2 NOT-SAFE secrets-refusal "not hashed" "$R/keep/row-src.txt"
  st_case G3 NOT-SAFE secrets-refusal "" "$R/credentials/fake.env"
  st_case G4 NOT-SAFE symlink-present "not followed" "$R/keep/alias.txt"
  st_case G5 NOT-SAFE none "live-refs=unknown" "$R/old-stray.out"

  st_status H2 2 --classify
  st_status H3 2 --bogus-flag "$R/keep/f1.txt"
  st_status H4 2 --stale-days abc "$R/keep/f1.txt"

  local jout
  set +e
  jout=$(env SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
    "$SELF" --classify --json "$R/local/f2.txt" 2>&1)
  case "$jout" in
    '{"path":"'*'","kind":"'*'","bytes":'*',"mtime":'*',"verdict":"NOT-SAFE","receipt":"'*'","evidence":"'*'"}')
      ST_PASS=$((ST_PASS + 1))
      st_note "PASS H6 json shape"
      ;;
    *)
      ST_FAIL=$((ST_FAIL + 1))
      st_note "FAIL H6 json shape '$jout'"
      ;;
  esac
  set -e

  # Repeatability: two classify runs of the same target are byte-identical.
  local a b
  a=$(env SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
    "$SELF" --classify "$R/keep/f1.txt")
  b=$(env SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
    "$SELF" --classify "$R/keep/f1.txt")
  if [ "$a" = "$b" ] && [ -n "$a" ]; then
    ST_PASS=$((ST_PASS + 1))
    st_note "PASS H7 repeatable classify"
  else
    ST_FAIL=$((ST_FAIL + 1))
    st_note "FAIL H7 repeatable classify"
  fi

  # Surface mode emits a summary and at least the kotodama-shaped repo row.
  local sout
  sout=$(env SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
    "$SELF" --surface --summary --lane kotodama-shaped)
  case "$sout" in
    *$'CENSUS\trepo-root\t'"$ST_FLEET/kotodama-shaped-shokunin"$'\t'*NOT-SAFE$'\t'unpushed$'\t'*unpushed=1*)
      case "$sout" in
        *'"impl":"impl-34"'*)
          ST_PASS=$((ST_PASS + 1))
          st_note "PASS H8 surface kotodama-shaped NOT-SAFE + summary"
          ;;
        *)
          ST_FAIL=$((ST_FAIL + 1))
          st_note "FAIL H8 missing summary"
          ;;
      esac
      ;;
    *)
      ST_FAIL=$((ST_FAIL + 1))
      st_note "FAIL H8 surface output: $sout"
      ;;
  esac

  st_audit_source

  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then
    exit 1
  fi
  exit 0
}

# ------------------------------------------------------------------- main --

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --summary) SUMMARY=1; shift ;;
    --classify) DO_CLASSIFY=1; shift ;;
    --worktrees) DO_WORKTREES=1; shift ;;
    --surface) DO_SURFACE=1; shift ;;
    --stale-days)
      [ "$#" -ge 2 ] || usage_err "--stale-days needs a value"
      STALE_DAYS=$2
      shift 2
      ;;
    --stale-days=*) STALE_DAYS=${1#*=}; shift ;;
    --ledger)
      [ "$#" -ge 2 ] || usage_err "--ledger needs a value"
      LEDGER=$2
      shift 2
      ;;
    --ledger=*) LEDGER=${1#*=}; shift ;;
    --root)
      [ "$#" -ge 2 ] || usage_err "--root needs a value"
      SHOKUNIN_ROOT=$(canon_path "$2")
      shift 2
      ;;
    --root=*) SHOKUNIN_ROOT=$(canon_path "${1#*=}"); shift ;;
    --lane)
      [ "$#" -ge 2 ] || usage_err "--lane needs a value"
      LANE_FILTER=$2
      shift 2
      ;;
    --lane=*) LANE_FILTER=${1#*=}; shift ;;
    --out)
      [ "$#" -ge 2 ] || usage_err "--out needs a value"
      OUT_PATH=$2
      shift 2
      ;;
    --out=*) OUT_PATH=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    --)
      shift
      while [ "$#" -gt 0 ]; do
        TARGETS+=("$1")
        shift
      done
      ;;
    -*) usage_err "unknown flag: $1" ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done

case "$STALE_DAYS" in
  ''|*[!0-9]*) usage_err "--stale-days must be a non-negative integer" ;;
esac

if [ "$SELFTEST" = 1 ]; then
  run_selftest
fi

if [ -n "$OUT_PATH" ]; then
  case "$OUT_PATH" in
    /tmp/*|/var/tmp/*) ;;
    "$REPO_ROOT"/census/*|"$REPO_ROOT"/results/*) ;;
    *)
      usage_err "--out must be under /tmp, <lane>/census/, or <lane>/results/"
      ;;
  esac
  mkdir -p -- "$(dirname -- "$OUT_PATH")"
  exec > "$OUT_PATH"
fi

command -v git >/dev/null 2>&1 || { printf 'souji-census: git not found\n' >&2; exit 1; }
command -v rg >/dev/null 2>&1 || { printf 'souji-census: rg not found\n' >&2; exit 1; }

scan_worktrees

if [ "${#TARGETS[@]}" -gt 0 ]; then
  DO_CLASSIFY=1
fi
if [ "$DO_CLASSIFY" = 0 ] && [ "$DO_WORKTREES" = 0 ] && [ "$DO_SURFACE" = 0 ]; then
  DO_SURFACE=1
fi

if [ "$DO_CLASSIFY" = 1 ]; then
  if [ "${#TARGETS[@]}" -eq 0 ]; then
    usage_err "--classify needs at least one path"
  fi
  for target in "${TARGETS[@]}"; do
    classify_one "$target"
  done
fi

if [ "$DO_WORKTREES" = 1 ] && [ "${#WT_MAP[@]}" -gt 0 ]; then
  while IFS= read -r local_wt; do
    [ -n "$local_wt" ] || continue
    classify_one "$local_wt"
  done < <(printf '%s\n' "${!WT_MAP[@]}" | sort)
fi

if [ "$DO_SURFACE" = 1 ]; then
  surface_candidates
fi

if [ "$SUMMARY" = 1 ]; then
  emit_summary
fi
exit 0
