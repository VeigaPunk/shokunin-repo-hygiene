#!/usr/bin/env bash
# souji-verify — receipt-gated removal verdicts for fleet artifacts (round 2).
#
# Binding spec: tools/souji-verify.spec.md. One bash tool; bash + coreutils +
# git + rg only; read-only over every surface it inspects; no git fetch.
#
# CLI
#   tools/souji-verify.impl-12.sh [--selftest] [--stale-days N] [--json] <path>...
#
# Output (default, one line per target):
#   VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-reason<TAB>evidence
# NOT-SAFE means "no removal receipt" — the safe default, not an error.
#
# Artifact kinds
#   repo-root   dir containing a real .git directory; SAFE only via the
#               moved-to-obsidian ledger row, else NOT-SAFE with
#               unpushed=N dirty=M in the evidence field.
#   worktree-registration
#               path equals a `worktree <path>` entry (other than the main
#               worktree) of a repo scanned under $SHOKUNIN_ROOT:
#               named branch with unpushed commits -> NOT-SAFE(unpushed-branch);
#               dir absent and 0 unique commits   -> SAFE(metadata-prune);
#               dir present and dirty              -> NOT-SAFE(dirty);
#               dir present and clean              -> NOT-SAFE(none).
#   file/dir artifact (default)
#               receipts tried in order: pushed, moved-to-obsidian, stale;
#               none -> NOT-SAFE(none).
#
# Safety rails (mirrored from the spec)
#   * Path components matching *.env/.env/.env./.envrc/*credential*/*secret*/
#     id_*/*.pem are refused before anything is read: NOT-SAFE(secrets-refusal).
#   * No git fetch/push/commit/branch/checkout/reset/rebase is ever executed
#     (the --selftest fixtures are built with plumbing: init, add, write-tree,
#     commit-tree, update-ref, symbolic-ref), no writes outside `mktemp -d',
#     .ufo/state, .ufo/watchdog.log and ~/.config are never touched.
#   * Empty or missing target -> NOT-SAFE(unreachable); exit stays 0.
#
# Env overrides (used by --selftest, useful for fixtures):
#   SHOKUNIN_ROOT  fleet root scanned for worktree registrations
#                  (default: parent of this repo)
#   SOUJI_LEDGER   obsidian ledger path
#                  (default: <repo>/corpus/knowledge/obsidian-ledger.tsv)
#
# Deviations from the spec's literal text, and why:
#   D-a  The spec's sweep flag `rg --basename` does not exist in ripgrep 15.2.0
#        (verified: `rg: unrecognized flag --basename`). Implemented as the
#        intent behind it — a fixed-string *content* sweep for the artifact
#        basename (`--fixed-strings`, so dots cannot act as regex metachars),
#        plus both glob anchor forms (`!souji-shokunin/census/**` and
#        `!**/souji-shokunin/census/**`) because ripgrep globs match absolute
#        search paths only when `**/`-anchored. Census/tests/quarantine stay
#        excluded (D3). The artifact itself is excluded from its own sweep.
#   D-b  Worktree rule order: the named-branch-unpushed check runs *before*
#        the dir-absent/unique=0 metadata-prune shortcut. Ground truth:
#        game-dev-2d-shokunin wt-r98/99/100 are named-branch registrations
#        with absent dirs, 1 unpushed commit each and 0 unique commits vs
#        `--not --all`; r1 requires NOT-SAFE(unpushed-branch) for them, so the
#        shortcut must not swallow them.
#   D-c  Scratch-type gains no patterns beyond the spec's four families; the
#        secret-shape list gains `.env.*`/`.envrc` (only ever more refusals).
set -euo pipefail
export LC_ALL=C GIT_OPTIONAL_LOCKS=0

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
SELFTEST=0
TARGETS=()

R_VERDICT=NOT-SAFE
R_RECEIPT=none
R_EVIDENCE=no-receipt
NOTES=()
FAIL_REASON=none

declare -A WT_MAP=()

usage() { # $1 = exit code
  sed -n '2,30p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "$1"
}

usage_err() { printf 'souji-verify: %s\n' "$1" >&2; usage 2; }

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

# True when any path component is secret-shaped (case-insensitive).
# E2 fix (r10 S18): the fold is done in a subshell with LC_ALL=C pinned, so a
# caller-inherited locale (tr_TR folds I->i-dotless) cannot change the result.
# The tool already exports LC_ALL=C at startup; this makes the invariant local
# to the comparison instead of dependent on process-global state.
is_secret_shaped() {
  local comp lc
  local IFS='/'
  set -f
  for comp in $1; do
    lc=$(LC_ALL=C printf '%s' "$comp" | LC_ALL=C tr '[:upper:]' '[:lower:]')
    case "$lc" in
      *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem)
        set +f; return 0 ;;
    esac
  done
  set +f
  return 1
}

# E1 fix (r10 S18): a git query that FAILS must never be read as a count of
# zero. These wrappers return non-zero when git itself failed, so callers can
# refuse (could-not-evaluate) instead of silently certifying a zero count.
git_count() { # rest = git args; prints the count on success only
  local out rc
  set +e
  out=$(git "$@" 2>/dev/null)
  rc=$?
  set -e
  [ "$rc" -eq 0 ] || return 1
  out=$(printf '%s\n' "$out" | grep -c . || true)
  printf '%s\n' "${out// /}"
  return 0
}

# E3 fix (r10 S18): `--not --all` on git 2.55 excludes the candidate's own
# linked-worktree HEAD, so a private detached commit counts as unique=0 and
# earns a false SAFE(metadata-prune). Counting against explicit ref spaces
# (branches/remotes/tags) does not consult worktree HEADs.
git_unique_count() { # $1 repo, $2 commit
  git_count -C "$1" log --oneline "$2" --not --branches --not --remotes --not --tags
}

# Nearest enclosing git repo of a path (handles files, subdirs, worktrees).
find_repo_for() {
  local p=$1 d top
  if [ -d "$p" ]; then d=$p; else d=$(dirname -- "$p"); fi
  d=$(canon_path "$d")
  if top=$(git -C "$d" rev-parse --show-toplevel 2>/dev/null) && [ -n "$top" ]; then
    printf '%s\n' "$top"; return 0
  fi
  while :; do
    [ -e "$d/.git" ] && { printf '%s\n' "$d"; return 0; }
    [ "$d" = "/" ] && break
    d=$(dirname -- "$d")
  done
  return 1
}

# Resolve the default-branch ref for pushed receipts (D1); prints the ref.
resolve_default_ref() {
  local repo=$1 b refs n
  b=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)
  if [ -n "$b" ] && git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$b" 2>/dev/null; then
    printf 'refs/remotes/origin/%s\n' "$b"; return 0
  fi
  refs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null | grep -v '^refs/remotes/origin/HEAD$' || true)
  n=$(printf '%s\n' "$refs" | grep -c . || true)
  if [ "$n" = 1 ]; then printf '%s\n' "$refs"; return 0; fi
  # r5 fix: no remote-tracking ref -> pushed is unverifiable. Local refs
  # (refs/heads/master) can NEVER establish a pushed receipt.
  return 1
}

file_sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

dir_digest() { # deterministic manifest digest of a directory (ignores .git)
  local d=$1
  # r5 fix: any symlink in the digest scope fails closed (return 2);
  # silently dropping -type l entries produced a false-SAFE
  # moved-to-obsidian class (r5 verification finding).
  if ( cd "$d" && find . -path './.git' -prune -o -type l -print -quit 2>/dev/null | grep -q . ); then
    return 2
  fi
  ( cd "$d" && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null
}

ledger_lines() {
  local line first=1
  [ -f "$LEDGER" ] || return 0
  while IFS= read -r line; do
    if [ "$first" = 1 ]; then
      first=0
      case "$line" in source_path$'\t'*) continue ;; esac
    fi
    [ -n "$line" ] && printf '%s\n' "$line"
  done < "$LEDGER"
}

scratch_type() { # prints the scratch family, or fails
  local p=$1 base comp
  local IFS='/'
  set -f
  for comp in $p; do
    if [ "$comp" = ".scratch" ]; then set +f; printf 'scratch-dir\n'; return 0; fi
  done
  set +f
  base=$(basename -- "$p")
  case "$base" in
    *.out|*.log) printf 'ext\n'; return 0 ;;
    *-draft.*) printf 'draft\n'; return 0 ;;
    *checkpoint*.json|*checkpoint*.png|*ckpt*.json|*ckpt*.png|*.ckpt|launch-*.json)
      printf 'checkpoint\n'; return 0 ;;
  esac
  return 1
}

count_live_refs() { # $1 target, $2 repo (or empty -> fleet root)
  local target=$1 repo=$2 rel="" base n out status
  local -a self_globs=()
  repo=${repo:-$SHOKUNIN_ROOT}
  [ -d "$repo" ] || { printf '0\n'; return 0; }
  case "$target" in "$repo"/*) rel=${target#"$repo"/} ;; esac
  if [ -n "$rel" ]; then self_globs=(-g "!$rel" -g "!./$rel"); fi
  base=$(basename -- "$target")
  set +e
  out=$( cd "$repo" && rg -l --no-ignore --fixed-strings -e "$base" . \
        -g '!.git' -g '!**/.git/**' \
        -g '!souji-shokunin/census/**' -g '!**/souji-shokunin/census/**' \
        -g '!souji-shokunin/tests/**' -g '!**/souji-shokunin/tests/**' \
        -g '!**/.ufo-quarantine/**' \
        "${self_globs[@]}" 2>/dev/null )
  status=$?
  set -e
  if [ "$status" -gt 1 ]; then printf 'unknown\n'; return 0; fi
  n=$(printf '%s\n' "$out" | grep -c . || true)
  printf '%s\n' "${n// /}"
}

try_pushed() { # $1 target, $2 repo; SAFE(pushed) or fail-with-note
  local target=$1 repo=$2 intro ref
  intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$target" 2>/dev/null | head -1 || true)
  if [ -z "$intro" ]; then
    NOTES+=("pushed=no-introducing-commit")
    return 1
  fi
  if ! ref=$(resolve_default_ref "$repo"); then
    FAIL_REASON=pushed-unverifiable
    NOTES+=("pushed=unverifiable(no-default-ref) intro=${intro:0:12}")
    return 1
  fi
  # r6 fix: a pushed receipt also requires that NO unpushed commit
  # touches the path -- a later local-only commit on the file was still
  # certified SAFE(pushed) by ancestry alone (r6 drift audit finding).
  # E1 fix (r10 S18): the query result is checked; a failed history query is
  # not evidence of zero unpushed commits (the old `| wc -l` masked rc).
  local unp_touch rc=0
  unp_touch=$(git_count -C "$repo" log --branches --not --remotes --oneline -- "$target") || rc=$?
  if [ "$rc" -ne 0 ]; then
    FAIL_REASON=git-unverifiable
    NOTES+=("pushed=unpushed-touching-unverifiable intro=${intro:0:12}")
    return 1
  fi
  if [ "$unp_touch" != "0" ]; then
    NOTES+=("pushed=unpushed-commits-touching intro=${intro:0:12}")
    return 1
  fi
  if git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
    R_VERDICT=SAFE; R_RECEIPT=pushed
    R_EVIDENCE="intro=${intro:0:12} ref=$ref ancestor=yes"
    return 0
  fi
  NOTES+=("pushed=not-ancestor intro=${intro:0:12} ref=$ref")
  return 1
}

try_obsidian() { # $1 target (canonical), $2 isdir(0/1)
  local target=$1 isdir=$2 row sp ss vp vs ledger_pin
  [ -f "$LEDGER" ] || { NOTES+=("obsidian=no-ledger"); return 1; }
  if ! ledger_pin=$(file_sha "$LEDGER") || [ -z "$ledger_pin" ]; then
    NOTES+=("obsidian=ledger-unverifiable"); return 1
  fi
  while IFS= read -r row; do
    [ -n "$row" ] || continue
    IFS=$'\t' read -r sp ss vp vs _rest <<< "$row"
    [ "$sp" = "$target" ] || continue
    if [ "$isdir" = 1 ]; then
      [ -d "$vp" ] || { NOTES+=("obsidian=vault-unreachable vault=$vp"); continue; }
      if [ -n "$ss" ]; then
        _ds=$(dir_digest "$target"); _drc=$?
        if [ "$_drc" = 2 ]; then NOTES+=("obsidian=symlink-present scope=source"); continue; fi
        if [ "$_ds" != "$ss" ]; then NOTES+=("obsidian=source-digest-mismatch"); continue; fi
      fi
      if [ -n "$vs" ]; then
        _ds=$(dir_digest "$vp"); _drc=$?
        if [ "$_drc" = 2 ]; then NOTES+=("obsidian=symlink-present scope=vault"); continue; fi
        if [ "$_ds" != "$vs" ]; then NOTES+=("obsidian=vault-digest-mismatch"); continue; fi
      fi
      if [ "$(file_sha "$LEDGER" || true)" != "$ledger_pin" ]; then
        NOTES+=("obsidian=ledger-changed"); return 1
      fi
      R_VERDICT=SAFE; R_RECEIPT=moved-to-obsidian
      R_EVIDENCE="ledger=source+vault-digest vault=$vp"
      return 0
    fi
    [ -f "$target" ] || continue
    [ -n "$ss" ] || continue
    if [ "$(file_sha "$target")" != "$ss" ]; then
      NOTES+=("obsidian=source-sha-mismatch"); continue
    fi
    [ -f "$vp" ] || { NOTES+=("obsidian=vault-unreachable vault=$vp"); continue; }
    [ -n "$vs" ] || continue
    if [ "$(file_sha "$vp")" != "$vs" ]; then
      NOTES+=("obsidian=vault-sha-mismatch"); continue
    fi
    if [ "$(file_sha "$LEDGER" || true)" != "$ledger_pin" ]; then
      NOTES+=("obsidian=ledger-changed"); return 1
    fi
    R_VERDICT=SAFE; R_RECEIPT=moved-to-obsidian
    R_EVIDENCE="ledger-row vault=$vp source-sha256=${ss:0:12}"
    return 0
  done < <(ledger_lines)
  NOTES+=("obsidian=no-matching-ledger-row")
  return 1
}

try_stale() { # $1 target, $2 repo (or empty)
  local target=$1 repo=$2 kind mtime now age refs
  kind=$(scratch_type "$target") || { NOTES+=("stale=not-scratch-type"); return 1; }
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
  R_VERDICT=SAFE; R_RECEIPT=stale
  R_EVIDENCE="scratch-type=$kind refs=0 mtime-age-days=$(( age / 86400 ))"
  return 0
}

evaluate_repo_root() {
  local target=$1 unpushed dirty rc=0
  if try_obsidian "$target" 1; then return 0; fi
  # E1 fix (r10 S18): a repo root is only "clean and pushed" if the queries
  # that establish that actually succeeded. Failed queries refuse.
  if ! unpushed=$(git_count -C "$target" log --branches --not --remotes --oneline); then rc=1; fi
  if ! dirty=$(git_count -C "$target" status --porcelain); then rc=1; fi
  if [ "$rc" -ne 0 ]; then
    R_VERDICT=NOT-SAFE; R_RECEIPT=git-unverifiable
    R_EVIDENCE="repo-root state query failed"
    return 0
  fi
  R_VERDICT=NOT-SAFE
  if [ "${unpushed:-0}" -gt 0 ]; then R_RECEIPT=unpushed
  elif [ "${dirty:-0}" -gt 0 ]; then R_RECEIPT=dirty
  else R_RECEIPT=none
  fi
  R_EVIDENCE="unpushed=${unpushed:-0} dirty=${dirty:-0}"
  return 0
}

evaluate_worktree() { # $1 target, $2 meta="owner<TAB>head<TAB>branch"
  local target=$1 meta=$2 owner head branch unp uniq dirty st present
  IFS=$'\t' read -r owner head branch <<< "$meta"
  if [ -d "$target" ]; then present=present; else present=absent; fi
  if [ -n "$branch" ]; then
    if ! unp=$(git -C "$owner" log --oneline "$branch" --not --remotes 2>/dev/null | wc -l); then
      R_VERDICT=NOT-SAFE; R_RECEIPT=git-unverifiable
      R_EVIDENCE="worktree commit query failed"
      return 0
    fi
    unp=${unp// /}
    if [ "${unp:-0}" -gt 0 ]; then
      R_VERDICT=NOT-SAFE; R_RECEIPT=unpushed-branch
      R_EVIDENCE="branch=${branch#refs/heads/} unpushed=$unp dir=$present owner=$(basename -- "$owner")"
      return 0
    fi
  fi
  if [ "$present" = absent ]; then
    # E3 fix (r10 S18): `--not --all` consults every linked-worktree HEAD,
    # including the candidate's own, so a private detached commit counts as
    # unique=0 and earns a false SAFE(metadata-prune) on git 2.55.
    if ! uniq=$(git_unique_count "$owner" "$head"); then
      R_VERDICT=NOT-SAFE; R_RECEIPT=git-unverifiable
      R_EVIDENCE="worktree commit query failed"
      return 0
    fi
    if [ "${uniq:-1}" = 0 ]; then
      R_VERDICT=SAFE; R_RECEIPT=metadata-prune
      R_EVIDENCE="dir=absent unique=0 head=${head:0:12} owner=$(basename -- "$owner")"
      return 0
    fi
    R_VERDICT=NOT-SAFE; R_RECEIPT=none
    R_EVIDENCE="dir=absent unique=$uniq head=${head:0:12} owner=$(basename -- "$owner")"
    return 0
  fi
  if st=$(git -C "$target" status --porcelain 2>/dev/null); then
    dirty=$(printf '%s\n' "$st" | grep -c . || true)
    dirty=${dirty// /}
    if [ "${dirty:-0}" -gt 0 ]; then
      R_VERDICT=NOT-SAFE; R_RECEIPT=dirty
      R_EVIDENCE="dir=present dirty=$dirty owner=$(basename -- "$owner")"
    else
      R_VERDICT=NOT-SAFE; R_RECEIPT=none
      R_EVIDENCE="dir=present clean head=${head:0:12} owner=$(basename -- "$owner")"
    fi
  else
    R_VERDICT=NOT-SAFE; R_RECEIPT=dirty
    R_EVIDENCE="dir=present status-unverifiable owner=$(basename -- "$owner")"
  fi
  return 0
}

evaluate_artifact() {
  local target=$1 repo="" isdir=0
  [ -d "$target" ] && isdir=1
  repo=$(find_repo_for "$target") || repo=""
  if [ -n "$repo" ] && try_pushed "$target" "$repo"; then return 0; fi
  if try_obsidian "$target" "$isdir"; then return 0; fi
  if try_stale "$target" "$repo"; then return 0; fi
  R_VERDICT=NOT-SAFE
  R_RECEIPT="${FAIL_REASON:-none}"
  local joined=""
  if [ "${#NOTES[@]}" -gt 0 ]; then
    joined=$(printf '%s; ' "${NOTES[@]}")
    joined=${joined%; }
  else
    joined="no-receipt"
  fi
  R_EVIDENCE=${joined//$'\t'/ }
  return 0
}

evaluate_path() {
  local raw=$1 target
  R_VERDICT=NOT-SAFE; R_RECEIPT=none; R_EVIDENCE=no-receipt; NOTES=(); FAIL_REASON=none
  if [ -z "$raw" ]; then
    R_RECEIPT=unreachable; R_EVIDENCE="empty-arg"; return 0
  fi
  target=$(canon_path "$raw")
  if is_secret_shaped "$target"; then
    R_RECEIPT=secrets-refusal
    R_EVIDENCE="secret-shaped path component"
    return 0
  fi
  if [ -d "$target" ]; then
    local nested_git
    if ! nested_git=$(cd -- "$target" && find . -path './.git' -prune -o \( -name .git -o -name .ufo \) -print -quit 2>/dev/null) || [ -n "$nested_git" ]; then
      R_RECEIPT=nested-repo-or-unverifiable
      R_EVIDENCE="directory contains nested Git/protected metadata or scope scan failed"
      return 0
    fi
  fi
  if [ -d "$target" ] && [ -d "$target/.git" ]; then
    evaluate_repo_root "$target"; return 0
  fi
  if [ -n "${WT_MAP[$target]:-}" ]; then
    evaluate_worktree "$target" "${WT_MAP[$target]}"; return 0
  fi
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    R_RECEIPT=unreachable; R_EVIDENCE="missing path"; return 0
  fi
  evaluate_artifact "$target"
  return 0
}

_wt_record() { # $1 repo, $2 path, $3 head, $4 branch
  local repo=$1 path=$2 head=$3 branch=$4 cp
  [ -n "$path" ] || return 0
  [ "$path" = "$repo" ] && return 0
  cp=$(canon_path "$path")
  WT_MAP["$cp"]="$repo"$'\t'"$head"$'\t'"$branch"
  return 0
}

scan_worktrees() {
  local repo path head branch line
  for repo in "$SHOKUNIN_ROOT" "$SHOKUNIN_ROOT"/*-shokunin; do
    [ -d "$repo" ] || continue
    [ -e "$repo/.git" ] || continue
    path=""; head=""; branch=""
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        'worktree '*)
          if [ -n "$path" ]; then _wt_record "$repo" "$path" "$head" "$branch"; fi
          path=${line#worktree }; head=""; branch="" ;;
        'HEAD '*) head=${line#HEAD } ;;
        'branch '*) branch=${line#branch } ;;
        'detached'*) branch="" ;;
        'prunable'*) : ;;
      esac
    done < <(git -C "$repo" worktree list --porcelain 2>/dev/null || true)
    if [ -n "$path" ]; then _wt_record "$repo" "$path" "$head" "$branch"; fi
  done
  return 0
}

emit_result() { # $1 path(raw), $2 verdict, $3 receipt, $4 evidence
  if [ "$JSON" = 1 ]; then
    printf '{"path":"%s","verdict":"%s","receipt":"%s","evidence":"%s"}\n' \
      "$(json_escape "$1")" "$2" "$3" "$(json_escape "$4")"
  else
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4"
  fi
}

# ---------------------------------------------------------------- selftest --

ST_FLEET="" ST_TMP="" ST_LEDGER=""
ST_PASS=0 ST_FAIL=0

st_note() { printf '%s\n' "$*"; }

st_case() { # $1 id, $2 want-verdict, $3 want-receipt, $4 want-evidence-substr, rest = targets
  local id=$1 wv=$2 wr=$3 wsub=$4; shift 4
  local out tag path v r ev status
  set +e
  out=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
        "$SELF" --stale-days 1 "$@" 2>&1)
  status=$?
  set -e
  if [ "$status" -ne 0 ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: exit=$status out=$out"; return 0
  fi
  # split on TABs preserving empty fields (a bare TAB is IFS whitespace to `read`)
  local rest
  tag=${out%%$'\t'*}; rest=${out#*$'\t'}
  path=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  v=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  r=${rest%%$'\t'*}; ev=${rest#*$'\t'}
  if [ "$tag" != "VERDICT" ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: bad line '$out'"; return 0
  fi
  if [ "$v" != "$wv" ] || [ "$r" != "$wr" ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: got $v($r) want $wv($wr) ev='$ev'"; return 0
  fi
  if [ -n "$wsub" ]; then
    case "$ev" in
      *"$wsub"*) : ;;
      *) ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: evidence '$ev' lacks '$wsub'"; return 0 ;;
    esac
  fi
  ST_PASS=$((ST_PASS+1)); st_note "PASS $id $v($r)"
  return 0
}

st_status() { # $1 id, $2 want-exit, rest = args
  local id=$1 want=$2; shift 2
  local status
  set +e
  env SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
    "$SELF" "$@" >/dev/null 2>&1
  status=$?
  set -e
  if [ "$status" = "$want" ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS $id exit=$status"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id exit=$status want=$want"
  fi
  return 0
}

st_commit() { # $1 repo, $2 parent(sha|""), $3 message -> sha
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

st_init_repo() { # $1 path, $2 branch
  local p=$1 b=${2:-master}
  git init -q --initial-branch="$b" "$p"
  git -C "$p" symbolic-ref HEAD "refs/heads/$b"
}

st_register_worktree() { # $1 owner, $2 name, $3 wt-path, $4 head-sha, $5 branch-ref|""
  local owner=$1 name=$2 wt=$3 sha=$4 br=$5 adm
  adm="$owner/.git/worktrees/$name"
  mkdir -p "$adm"
  if [ -n "$br" ]; then printf 'ref: %s\n' "$br" > "$adm/HEAD"; else printf '%s\n' "$sha" > "$adm/HEAD"; fi
  printf '../..\n' > "$adm/commondir"
  printf '%s\n' "$wt/.git" > "$adm/gitdir"
  if [ -d "$wt" ]; then printf 'gitdir: %s\n' "$adm" > "$wt/.git"; fi
  return 0
}

st_build_fixtures() {
  ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-verify-selftest.XXXXXX")
  ST_FLEET="$ST_TMP/fleet"
  ST_LEDGER="$ST_TMP/ledger.tsv"
  mkdir -p "$ST_FLEET"

  # --- repo-shokunin: file artifacts, worktree registrations -------------
  local R="$ST_FLEET/repo-shokunin"
  st_init_repo "$R" master
  mkdir -p "$R/keep" "$R/local" "$R/.scratch" "$R/souji-shokunin/census" "$R/souji-shokunin/tests"
  printf 'f1 payload\n' > "$R/keep/f1.txt"
  local c1; c1=$(st_commit "$R" "" "c1 adds keep/f1.txt")
  printf 'extra\n' > "$R/keep/extra.txt"
  local c2; c2=$(st_commit "$R" "$c1" "c2 pushes keep/extra.txt")
  git -C "$R" update-ref refs/remotes/origin/master "$c2"
  git -C "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$R" update-ref refs/heads/master "$c2"
  # F2 + F6: introduced by the local-only commit c3 (not on origin/master)
  printf 'f2 payload\n' > "$R/local/f2.txt"
  printf 'f6 payload\n' > "$R/keep/f6.txt"
  local c3; c3=$(st_commit "$R" "$c2" "c3 local-only adds local/f2.txt and keep/f6.txt")
  git -C "$R" update-ref refs/heads/master "$c3"
  # untracked fixtures: scratch (F7/F8/E8) and secret-shaped paths (F10/E2)
  printf 'self mention old-f7.out\n' > "$R/.scratch/old-f7.out"
  printf 'self mention old-f8.out\n' > "$R/.scratch/old-f8.out"
  printf 'self mention old-e8.out\n' > "$R/.scratch/old-e8.out"
  printf 'live ref to old-e8.out here\n' > "$R/notes.md"
  printf '{"row":"old-f8.out"}\n' > "$R/souji-shokunin/census/ref-census.json"
  printf 'old-f8.out cited here\n' > "$R/souji-shokunin/tests/ref-tests.txt"
  printf 'x\n' > "$R/x.env"
  mkdir -p "$R/credentials"; printf 'note\n' > "$R/credentials/note.txt"
  # F5 branch: 1 unpushed commit; E3 branch: fully pushed
  git -C "$R" update-ref refs/heads/wt-unpushed "$c3"
  git -C "$R" update-ref refs/heads/wt-pushed "$c2"
  # F4: detached registration, dir absent, HEAD on the origin tip
  st_register_worktree "$R" wt-f4 "$ST_TMP/wt-f4" "$c2" ""
  # F5: named-branch registration with 1 unpushed commit, dir absent
  st_register_worktree "$R" wt-f5 "$ST_TMP/wt-f5" "$c3" "refs/heads/wt-unpushed"
  # E3: named branch fully pushed, dir absent
  st_register_worktree "$R" wt-f5b "$ST_TMP/wt-f5b" "$c2" "refs/heads/wt-pushed"
  # E1: present + dirty worktree (untracked file in a registered dir)
  st_register_worktree "$R" wt-dirty "$ST_TMP/wt-dirty" "$c1" ""
  mkdir -p "$ST_TMP/wt-dirty"
  printf 'gitdir: %s\n' "$R/.git/worktrees/wt-dirty" > "$ST_TMP/wt-dirty/.git"
  printf 'untracked\n' > "$ST_TMP/wt-dirty/stray.txt"

  # --- repo9-shokunin: D1 fallback (single origin ref, no origin/HEAD) ---
  local R9="$ST_FLEET/repo9-shokunin"
  st_init_repo "$R9" master
  printf 'f9 payload\n' > "$R9/f9.txt"
  local c9; c9=$(st_commit "$R9" "" "c9 adds f9.txt")
  git -C "$R9" update-ref refs/heads/master "$c9"
  git -C "$R9" update-ref refs/remotes/origin/master "$c9"

  # --- kotodama-shaped: unpushed commits + dirty tree (F3) ---------------
  local RK="$ST_FLEET/kotodama-shaped-shokunin"
  st_init_repo "$RK" main
  printf 'tracked\n' > "$RK/tracked.txt"
  local k1; k1=$(st_commit "$RK" "" "k1 tracked.txt")
  git -C "$RK" update-ref refs/remotes/origin/main "$k1"
  git -C "$RK" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
  printf 'more\n' >> "$RK/tracked.txt"
  printf 'new file\n' > "$RK/added.txt"
  local k2; k2=$(st_commit "$RK" "$k1" "k2 local work")
  git -C "$RK" update-ref refs/heads/main "$k2"
  printf 'dirt\n' >> "$RK/tracked.txt"

  # --- ledger + vault for F6 --------------------------------------------
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

  # --- E6: repo-root preserved via a directory-digest ledger row --------
  local RP="$ST_FLEET/preserved-repo-shokunin" VD="$ST_TMP/vault/preserved-repo"
  st_init_repo "$RP" master
  printf 'kept\n' > "$RP/kept.txt"
  local cp1; cp1=$(st_commit "$RP" "" "p1 kept.txt")
  git -C "$RP" update-ref refs/heads/master "$cp1"
  mkdir -p "$VD"; printf 'kept\n' > "$VD/kept.txt"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tselftest-dir\n' \
    "$(canon_path "$RP")" "$(dir_digest "$RP")" \
    "$(canon_path "$VD")" "$(dir_digest "$VD")" >> "$ST_LEDGER"

  # --- E7: commit reachable from no default ref -> pushed-unverifiable ---
  local RN="$ST_FLEET/norefs-shokunin"
  st_init_repo "$RN" work
  printf 'norefs\n' > "$RN/tracked.txt"
  local cn; cn=$(st_commit "$RN" "" "n1 tracked.txt")
  git -C "$RN" update-ref refs/heads/work "$cn"

  touch -d '3 days ago' "$R/.scratch/old-f7.out" "$R/.scratch/old-f8.out" "$R/.scratch/old-e8.out"
  return 0
}

st_audit_source() { # H1: no forbidden git porcelain in executable lines
  local n
  n=$(grep -nE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase)( |$)' "$SELF" | wc -l || true)
  n=${n// /}
  if [ "${n:-1}" = 0 ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS H1 no forbidden git subcommand"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H1 $n forbidden git invocation(s) in $SELF"
  fi
  # H5: fixtures isolated under mktemp -d
  case "$ST_FLEET" in
    "$ST_TMP"/*) ST_PASS=$((ST_PASS+1)); st_note "PASS H5 fixtures under mktemp -d ($ST_TMP)" ;;
    *) ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H5 fixtures not under mktemp" ;;
  esac
  return 0
}

run_selftest() {
  if [ "${SOUJI_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'souji-verify: refusing nested --selftest\n' >&2
    exit 1
  fi
  st_build_fixtures
  trap 'rm -rf -- "$ST_TMP"' EXIT
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

  st_status H2 2
  st_status H3 2 --bogus-flag "$R/keep/f1.txt"
  st_status H4 2 --stale-days abc "$R/keep/f1.txt"

  # H6: --json shape + exit 0 on NOT-SAFE verdicts
  local jout
  set +e
  jout=$(env SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
         "$SELF" --json "$R/local/f2.txt" 2>&1)
  case "$jout" in
    '{"path":"'*'","verdict":"NOT-SAFE","receipt":"'*'","evidence":"'*'"}')
      ST_PASS=$((ST_PASS+1)); st_note "PASS H6 json shape" ;;
    *) ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H6 json shape '$jout'" ;;
  esac
  set -e

  st_e_cluster

  st_audit_source

  local r9_out r9_rc=0
  r9_out=$(bash "$SCRIPT_DIR/souji-round9-selftest.sh" verify "$SELF") || r9_rc=$?
  printf '%s\n' "$r9_out"
  if [[ "${r9_out##*$'\n'}" =~ ^ROUND9$'\t'([0-9]+)$'\t'([0-9]+)$ ]]; then
    ST_PASS=$((ST_PASS + BASH_REMATCH[1])); ST_FAIL=$((ST_FAIL + BASH_REMATCH[2]))
    if [ "$r9_rc" -ne 0 ] && [ "${BASH_REMATCH[2]}" = 0 ]; then
      ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL R9 runner exit=$r9_rc"
    fi
  else
    ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL R9 runner missing summary exit=$r9_rc"
  fi

st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then exit 1; fi
  exit 0
}

# --- r10 S18 cluster-E regressions ------------------------------------------
# Each case builds its own fresh fixture repo under $ST_TMP and asserts the
# fail-closed behavior for one of E1 (failed git query), E2 (locale folding)
# and E3 (git-2.55 linked-worktree HEAD in --not --all).
st_e_note() { st_note "$*"; }

st_e_case() { # $1 id, $2 want-verdict, $3 want-receipt, $4 evidence-substr, $5 target, $6 env-prefix-cmd...
  local id=$1 wv=$2 wr=$3 wsub=$4 target=$5; shift 5
  local out status v r ev rest
  set +e
  out=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
        SOUJI_SELFTEST_ACTIVE=1 "$@" "$SELF" --stale-days 1 "$target" 2>&1)
  status=$?
  set -e
  if [ "$status" -ne 0 ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: exit=$status out=$out"; return 0
  fi
  v=${out%%$'\t'*}; rest=${out#*$'\t'}
  rest=${rest#*$'\t'}
  v=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  r=${rest%%$'\t'*}; ev=${rest#*$'\t'}
  if [ "$v" != "$wv" ] || [ "$r" != "$wr" ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: got $v($r) want $wv($wr) ev='$ev'"; return 0
  fi
  if [ -n "$wsub" ]; then
    case "$ev" in *"$wsub"*) : ;; *)
      ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: evidence '$ev' lacks '$wsub'"; return 0 ;;
    esac
  fi
  ST_PASS=$((ST_PASS+1)); st_note "PASS $id $v($r)"
  return 0
}

st_e_cluster() {
  local REAL_GIT; REAL_GIT=$(command -v git)
  local EX="$ST_TMP/e-cluster"; mkdir -p "$EX/bin"

  # --- E1a: history query failure must not read as "no unpushed commits" ---
  local E1="$ST_FLEET/e1-shokunin"
  st_init_repo "$E1" main
  printf 'e1 payload\n' > "$E1/art.txt"
  local e1c; e1c=$(st_commit "$E1" "" "e1 art.txt")
  git -C "$E1" update-ref refs/heads/main "$e1c"
  git -C "$E1" update-ref refs/remotes/origin/main "$e1c"
  git -C "$E1" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
  cat > "$EX/bin/git" <<'SH'
#!/usr/bin/env bash
for a in "$@"; do
  case "$a" in --branches) printf 'fatal: simulated history failure\n' >&2; exit 128;; esac
done
exec "$ST_E_REAL_GIT" "$@"
SH
  chmod +x "$EX/bin/git"
  st_e_case E1a NOT-SAFE git-unverifiable "unverifiable" "$E1/art.txt" \
    "PATH=$EX/bin:$PATH" "ST_E_REAL_GIT=$REAL_GIT"
  # control: without the shim the same target is a legitimate SAFE(pushed)
  st_e_case E1a-control SAFE pushed "ancestor=yes" "$E1/art.txt" \
    "ST_E_REAL_GIT=$REAL_GIT"

  # --- E1b: failed repo-root state queries refuse ---
  cat > "$EX/bin/git" <<'SH'
#!/usr/bin/env bash
for a in "$@"; do
  case "$a" in status) printf 'fatal: simulated status failure\n' >&2; exit 128;; esac
done
exec "$ST_E_REAL_GIT" "$@"
SH
  chmod +x "$EX/bin/git"
  st_e_case E1b NOT-SAFE git-unverifiable "query failed" "$E1" \
    "PATH=$EX/bin:$PATH" "ST_E_REAL_GIT=$REAL_GIT"

  # --- E1c: failed worktree unique-commit query refuses (already checked) ---
  local E1W="$ST_TMP/e1-wt"
  st_register_worktree "$E1" e1wt "$E1W" "$e1c" ""
  cat > "$EX/bin/git" <<'SH'
#!/usr/bin/env bash
for a in "$@"; do
  case "$a" in --tags) printf 'fatal: simulated ref failure\n' >&2; exit 128;; esac
done
exec "$ST_E_REAL_GIT" "$@"
SH
  chmod +x "$EX/bin/git"
  st_e_case E1c NOT-SAFE git-unverifiable "query failed" "$E1W" \
    "PATH=$EX/bin:$PATH" "ST_E_REAL_GIT=$REAL_GIT"
  rm -f "$EX/bin/git"

  # --- E2: locale-folded secret shapes are still refused -------------------
  local E2R="$ST_FLEET/e2-shokunin"
  st_init_repo "$E2R" main
  mkdir -p "$E2R/.scratch"
  local n
  for n in ID_RSA id_rsa Id_Rsa .ENV .env credENTIALS my-secret.pem; do
    mkdir -p "$E2R/.scratch/$n"
    printf 'x\n' > "$E2R/.scratch/$n/f.txt"
  done
  touch -d '3 days ago' "$E2R/.scratch"/* 
  mkdir -p "$EX/locale"
  if command -v localedef >/dev/null 2>&1 &&
     localedef --no-archive -i tr_TR -f UTF-8 "$EX/locale/tr_TR" >/dev/null 2>&1; then
    local fold
    fold=$(env LOCPATH="$EX/locale" LC_ALL=tr_TR bash -c 's=ID_RSA; printf "%s" "${s,,}"')
    if [ "$fold" = 'ıd_rsa' ]; then
      ST_PASS=$((ST_PASS+1)); st_note "PASS E2a Turkish locale fixture is active"
    else
      ST_FAIL=$((ST_FAIL+1)); st_note "FAIL E2a locale fixture fold='$fold'"
    fi
    for n in ID_RSA id_rsa Id_Rsa .ENV credENTIALS my-secret.pem; do
      st_e_case "E2b[$n]" NOT-SAFE secrets-refusal "" "$E2R/.scratch/$n" \
        "LOCPATH=$EX/locale" "LC_ALL=tr_TR"
    done
  else
    st_note "SKIP E2 Turkish locale (localedef or locale source unavailable)"
  fi

  # --- E3: linked-worktree HEAD skew in --not --all ------------------------
  local E3R="$ST_FLEET/e3-shokunin"
  st_init_repo "$E3R" main
  printf 'base\n' > "$E3R/base.txt"
  local e3c1; e3c1=$(st_commit "$E3R" "" "e3 base")
  git -C "$E3R" update-ref refs/heads/main "$e3c1"
  git -C "$E3R" update-ref refs/remotes/origin/main "$e3c1"
  git -C "$E3R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
  # a detached linked worktree whose HEAD carries a private commit
  local E3W="$ST_TMP/e3-wt"; mkdir -p "$E3W"
  git -C "$E3R" worktree add -q --detach "$E3W" "$e3c1" 2>/dev/null || true
  if [ -d "$E3W/.git" ] || [ -f "$E3W/.git" ]; then
    printf 'private\n' > "$E3W/private.txt"
    local e3c2
    git -C "$E3W" add -A
    local e3t; e3t=$(git -C "$E3W" write-tree)
    e3c2=$(printf 'private\n' | git -C "$E3W" commit-tree "$e3t" -p "$e3c1")
    git -C "$E3W" update-ref HEAD "$e3c2"
    # the private commit is reachable ONLY through this worktree HEAD
    local all_n refs_n
    all_n=$(git -C "$E3R" log --oneline "$e3c2" --not --all 2>/dev/null | wc -l)
    refs_n=$(git -C "$E3R" log --oneline "$e3c2" --not --branches --not --remotes --not --tags 2>/dev/null | wc -l)
    if [ "${all_n// /}" = 0 ] && [ "${refs_n// /}" = 1 ]; then
      ST_PASS=$((ST_PASS+1)); st_note "PASS E3a fixture shows --all skew (all=0 refs=1)"
    else
      ST_FAIL=$((ST_FAIL+1)); st_note "FAIL E3a fixture skew all=$all_n refs=$refs_n"
    fi
    # dir removed so the registration is the metadata-prune shape; the
    # private commit must keep the verdict NOT-SAFE (old code said SAFE).
    rm -rf -- "$E3W"
    st_e_case E3b NOT-SAFE none "unique=1" "$E3W"
  else
    st_note "SKIP E3 linked worktree unavailable"
  fi
  return 0
}


# ------------------------------------------------------------------- main --

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --stale-days) [ "$#" -ge 2 ] || usage_err "--stale-days needs a value"; STALE_DAYS=$2; shift 2 ;;
    --stale-days=*) STALE_DAYS=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    --) shift; while [ "$#" -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    -*) usage_err "unknown flag: $1" ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done

case "$STALE_DAYS" in
  ''|*[!0-9]*) usage_err "--stale-days must be a non-negative integer" ;;
esac

if [ "$SELFTEST" = 1 ]; then run_selftest; fi

if [ "${#TARGETS[@]}" -eq 0 ]; then usage_err "no targets given"; fi
command -v git >/dev/null 2>&1 || { printf 'souji-verify: git not found\n' >&2; exit 1; }
command -v rg >/dev/null 2>&1 || { printf 'souji-verify: rg not found\n' >&2; exit 1; }

scan_worktrees
for target in "${TARGETS[@]}"; do
  evaluate_path "$target"
  emit_result "$target" "$R_VERDICT" "$R_RECEIPT" "$R_EVIDENCE"
done
exit 0
