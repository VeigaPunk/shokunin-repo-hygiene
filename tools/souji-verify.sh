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
#   r17  jj-colocated repositories. jj 0.45.1 writes refs/jj/keep/<sha> for
#        every commit it creates, visible or hidden (its only refs/jj
#        namespaces are keep/, remote-tags/ and the unborn root):
#        (a) durable receipt roots are EVERY ref except refs/jj/*
#        (`for-each-ref --exclude='refs/jj/'`), so refs/stash, refs/original
#        and the like stay roots and plain repositories keep byte-identical
#        verdicts; an absent-worktree head held only by refs/jj/keep/* is
#        unique and can never earn metadata-prune.
#        (b) a keep-only commit refuses a pushed receipt only when a leaf
#        blob it introduces under the target is novel: `rev-list
#        --glob=refs/jj/keep/* --not --branches --tags --remotes -- <rel>`
#        names it, and the blobs `ls-tree -r C -- <rel>` reports are absent
#        from every pushed object under the path (`rev-list --objects
#        --remotes -- <rel>`). Deletions, metaedit/rebase predecessors and
#        directory trees that recombine already-pushed blobs do not
#        refuse. Both queries are gated on a refs/jj/keep/ probe, so a
#        repository without keep refs runs nothing new, and a git failure
#        takes the existing history-unverifiable path.
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

# r17: keep refs are unpushed heads, never durable roots. A keep-only commit
# refuses a pushed receipt only when it introduces a blob at the path that no
# pushed (remote) commit carries; deletions and metaedit/rebase predecessors
# with an already-pushed blob do not. Returns 0 novel, 1 not novel, 2 git
# failure (caller takes its existing history-unverifiable path).
jj_keep_novel() { # $1 repo, $2 path relative to the repo root
  local repo=$1 rel=$2 c o known objs=""
  [ -n "$(git -C "$repo" for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ 2>&1)" ] || return 1
  if ! known=$(git -C "$repo" rev-list --objects --remotes -- "$rel" 2>/dev/null | cut -d' ' -f1); then
    return 2
  fi
  if ! c=$(git -C "$repo" rev-list "--glob=refs/jj/keep/*" --not --branches --tags --remotes -- "$rel" 2>/dev/null); then
    return 2
  fi
  while IFS= read -r c; do
    [ -n "$c" ] || continue
    # r17 w2: leaf blobs, not the object at C:<rel> -- a directory tree can
    # combine only already-pushed blobs into a never-pushed tree id, so
    # comparing C:<rel> itself over-refused directories. For a file target
    # ls-tree -r prints the same single blob; for a deletion it prints
    # nothing. An unreadable tree fails closed (return 2).
    o=$(git -C "$repo" ls-tree -r --format='%(objectname)' "$c" -- "$rel" 2>/dev/null) || return 2
    [ -n "$o" ] && objs+=$o$'\n'
  done <<< "$c"
  [ -n "$objs" ] || return 1
  # single fixed-string grep over the whole candidate set: no per-candidate
  # pipeline, so no SIGPIPE can fabricate a false "novel" under pipefail.
  grep -Fxvq -f <(printf '%s\n' "$known") <<< "${objs%$'\n'}" && return 0
  return 1
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
  if [ "$(git -C "$repo" log --branches --not --remotes --oneline -- "$target" 2>/dev/null | wc -l)" != "0" ]; then
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
  local target=$1 unpushed dirty
  if try_obsidian "$target" 1; then return 0; fi
  unpushed=$(git -C "$target" log --branches --not --remotes --oneline 2>/dev/null | wc -l || true)
  dirty=$(git -C "$target" status --porcelain 2>/dev/null | wc -l || true)
  unpushed=${unpushed// /}; dirty=${dirty// /}
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
    if ! uniq=$(git -C "$owner" log --oneline "$head" --not --all 2>/dev/null | wc -l); then
      R_VERDICT=NOT-SAFE; R_RECEIPT=git-unverifiable
      R_EVIDENCE="worktree commit query failed"
      return 0
    fi
    uniq=${uniq// /}
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

s18_evaluate_path() {
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

# cand-merge-verify.sh -- round-10 S15 composed candidate.
# S17 receipt engine (round-2 base + S08 repairs) with the S18 shared
# hardening layer inlined after it, plus the ledger-revocation pin that the
# S18 override would otherwise drop. Renames: base evaluate_path ->
# s18_evaluate_path, which the guard's evaluate_path wrapper delegates to.
# ---- S18 shared hardening (round-9 S18 guard), inlined by r10 S15 ----
S18_KIND=verify
#!/usr/bin/env bash
export LC_ALL=C GIT_OPTIONAL_LOCKS=0 GIT_LITERAL_PATHSPECS=1
export TMPDIR="${TMPDIR:-/var/tmp}"

s18_path_ok() {
  local p=$1 part cur=""
  [[ "$p" != *[[:cntrl:]]* ]] || return 1
  is_secret_shaped "$p" && return 1
  case "/${p#/}/" in
    */.git/*|*/.ufo/state/*|*/.ufo/watchdog.log/*) return 1 ;;
  esac
  [[ "$p" = /* ]] || p="$PWD/$p"
  local -a parts=()
  IFS=/ read -r -a parts <<< "$p"
  for part in "${parts[@]}"; do
    [ -n "$part" ] || continue
    cur="$cur/$part"
    [ ! -L "$cur" ] || return 1
  done
  return 0
}

s18_scope_ok() {
  local d=$1 root=${2:-$1} p
  [ -r "$d" ] && [ -x "$d" ] || return 1
  for p in "$d"/* "$d"/.[!.]* "$d"/..?*; do
    [ -e "$p" ] || [ -L "$p" ] || continue
    [ "$p" != "$root/.git" ] || continue
    s18_path_ok "$p" || return 1
    if [ -d "$p" ]; then
      s18_scope_ok "$p" "$root" || return 1
    elif [ ! -f "$p" ]; then
      return 1
    fi
  done
}

is_hex64() { [[ "$1" =~ ^[0-9a-f]{64}$ ]]; }

file_sha() {
  s18_path_ok "$1" && [ -f "$1" ] || return 1
  sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1
}

dir_digest() {
  local d=$1
  s18_path_ok "$d" && [ -d "$d" ] && s18_scope_ok "$d" || return 2
  ( set -o pipefail
    cd -- "$d" && find . -path './.git' -prune -o -type f -print0 \
      | LC_ALL=C sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1
  ) 2>/dev/null
}

s18_row_parse() {
  local rest=$1
  [[ "$rest" = *$'\t'* ]] || return 1
  S18_SP=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  [[ "$rest" = *$'\t'* ]] || return 1
  S18_SS=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  [[ "$rest" = *$'\t'* ]] || return 1
  S18_VP=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  S18_VS=${rest%%$'\t'*}
}

s18_row_ok() {
  local target=$1 isdir=$2 real_vault
  [[ "$S18_SP" = /* && "$S18_VP" = /* ]] || return 1
  is_hex64 "$S18_SS" && is_hex64 "$S18_VS" || return 1
  s18_path_ok "$S18_SP" && s18_path_ok "$S18_VP" || return 1
  real_vault=$(canon_path "$S18_VP")
  [ "$target" != "$real_vault" ] || return 1
  if [ "$isdir" = 1 ]; then
    case "$real_vault/" in "$target/"*) return 1 ;; esac
    case "$target/" in "$real_vault/"*) return 1 ;; esac
  fi
  return 0
}

load_ledger() {
  local row first=1
  LEDGER_ROWS=()
  s18_path_ok "$LEDGER" && [ -f "$LEDGER" ] || return 0
  while IFS= read -r row || [ -n "$row" ]; do
    if [ "$first" = 1 ]; then
      first=0
      case "$row" in source_path$'\t'*) continue ;; esac
    fi
    [ -z "$row" ] || LEDGER_ROWS+=("$row")
  done < "$LEDGER"
}

ledger_lines() {
  local row
  s18_path_ok "$LEDGER" && [ -f "$LEDGER" ] || return 0
  while IFS= read -r row || [ -n "$row" ]; do
    case "$row" in source_path$'\t'*|'#'*|'') continue ;; esac
    printf '%s\n' "$row"
  done < "$LEDGER"
}

try_obsidian() {
  local target=$1 isdir=$2 row source_sha vault_sha ledger_pin
  ledger_pin=$(file_sha "$LEDGER") || { NOTES+=("obsidian=ledger-unverifiable"); return 1; }
  while IFS= read -r row; do
    s18_row_parse "$row" || continue
    [ "$S18_SP" = "$target" ] || continue
    if ! s18_row_ok "$target" "$isdir"; then
      NOTES+=("obsidian=invalid-or-nonindependent-row")
      continue
    fi
    if [ "$isdir" = 1 ]; then
      source_sha=$(dir_digest "$target") && vault_sha=$(dir_digest "$S18_VP") || continue
    else
      source_sha=$(file_sha "$target") && vault_sha=$(file_sha "$S18_VP") || continue
    fi
    [ "$source_sha" = "$S18_SS" ] && [ "$vault_sha" = "$S18_VS" ] || continue
    if [ "$(file_sha "$LEDGER" || true)" != "$ledger_pin" ]; then
      NOTES+=("obsidian=ledger-changed"); return 1
    fi
    R_VERDICT=SAFE; R_RECEIPT=moved-to-obsidian
    R_EVIDENCE="ledger=source+vault-digest ledger-row vault=$S18_VP source-sha256=${S18_SS:0:12}"
    return 0
  done < <(ledger_lines)
  NOTES+=("obsidian=no-matching-ledger-row")
  return 1
}

try_ledger() {
  local target=$1 isdir=$2 raw=${3:-} row matched=0 rejected=0 reason=row-incomplete
  local -a rows=("${LEDGER_ROWS[@]}") LEDGER_ROWS=()
  for row in "${rows[@]}"; do
    s18_row_parse "$row" || continue
    [ "$S18_SP" = "$target" ] || [ "$S18_SP" = "$raw" ] || continue
    matched=1
    if s18_row_ok "$target" "$isdir"; then
      LEDGER_ROWS+=("$row")
    else
      rejected=1
      if [ "$S18_VP" = "$target" ]; then reason=source-equals-vault; fi
    fi
  done
  if [ "${#LEDGER_ROWS[@]}" -gt 0 ]; then
    s18_try_ledger "$target" "$isdir" "$raw"
    return $?
  fi
  if [ "$matched" = 1 ] && [ "$rejected" = 1 ]; then
    NOTES+=("$reason row-incomplete nonindependent-or-invalid-ledger-row")
    finish_mismatch "$reason"
    return 0
  fi
  return 1
}

s18_snapshot_equal() { # read-only tracked-content-vs-ref compare
  local repo=$1 ref=$2 path=$3 tmpidx rc
  tmpidx=$(mktemp -p "${TMPDIR:-/var/tmp}") || return 1
  rm -f -- "$tmpidx"
  if ! GIT_INDEX_FILE="$tmpidx" git -C "$repo" read-tree "$ref" 2>/dev/null; then
    rm -f -- "$tmpidx"; return 1
  fi
  GIT_INDEX_FILE="$tmpidx" git -C "$repo" update-index -q --refresh >/dev/null 2>&1
  GIT_INDEX_FILE="$tmpidx" git -C "$repo" diff-index --quiet "$ref" -- "$path" 2>/dev/null
  rc=$?
  rm -f -- "$tmpidx"
  return "$rc"
}

try_pushed() {
  local target=$1 repo=$2 intro ref status touching jjrc rel
  [ -n "$repo" ] || { NOTES+=("pushed=no-repo"); return 1; }
  if ! status=$(git -C "$repo" --no-optional-locks status --porcelain --untracked-files=all --ignored=matching -- "$target" 2>/dev/null); then
    NOTES+=("pushed=status-unverifiable"); return 1
  fi
  if [ -n "$status" ]; then
    NOTES+=("pushed=dirty-or-untracked-content"); return 1
  fi
  if ! intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$target" 2>/dev/null) || [ -z "$intro" ]; then
    NOTES+=("pushed=no-introducing-commit"); return 1
  fi
  if ! ref=$(resolve_default_ref "$repo"); then
    FAIL_REASON=pushed-unverifiable
    NOTES+=("pushed=unverifiable(no-default-ref) intro=${intro:0:12}"); return 1
  fi
  if ! touching=$(git -C "$repo" log --format=%H HEAD --branches --not --remotes -- "$target" 2>/dev/null); then
    NOTES+=("pushed=history-unverifiable"); return 1
  fi
  if [ -n "$touching" ]; then
    NOTES+=("pushed=unpushed-commits-touching intro=${intro:0:12}"); return 1
  fi
  # r17 (b): a keep-only commit refuses the receipt only when a leaf blob it
  # introduces under the target is absent from every pushed object. An
  # un-prefixed rel (target outside the repo after canonicalization) fails
  # closed, never "not novel".
  rel=${target#"$repo"/}
  if [ "$rel" = "$target" ]; then jjrc=2; else jjrc=0; jj_keep_novel "$repo" "$rel" || jjrc=$?; fi
  if [ "$jjrc" = 2 ]; then NOTES+=("pushed=history-unverifiable"); return 1; fi
  if [ "$jjrc" = 0 ]; then NOTES+=("pushed=unpushed-commits-touching intro=${intro:0:12} jj-keep-novel"); return 1; fi
  if ! git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
    NOTES+=("pushed=not-ancestor intro=${intro:0:12} ref=$ref"); return 1
  fi
  if ! s18_snapshot_equal "$repo" "$ref" "$target"; then
    NOTES+=("pushed=default-snapshot-mismatch"); return 1
  fi
  R_VERDICT=SAFE; R_RECEIPT=pushed; R_REASON=pushed
  R_EVIDENCE="intro=${intro:0:12} ref=$ref ancestor=yes snapshot=equal clean=yes"
  return 0
}

count_live_refs() {
  local target=$1 repo=${2:-} scope=${3:-$1} base out status=0 n=0 path canonical pattern
  local -a excludes=()
  repo=${repo:-$SHOKUNIN_ROOT}
  [ -d "$repo" ] || { printf 'unknown\n'; return; }
  for pattern in '*.env' '.env' '.env.*' '.envrc' '*credential*' '*secret*' 'id_*' '*.pem'; do
    excludes+=(--iglob "!**/$pattern" --iglob "!**/$pattern/**")
  done
  base=$(basename -- "$target")
  out=$(cd -- "$repo" && rg -l --hidden --no-ignore --text --fixed-strings -e "$base" . \
    -g '!.git' -g '!**/.git/**' \
    -g '!souji-shokunin/census/**' -g '!**/souji-shokunin/census/**' \
    -g '!souji-shokunin/tests/**' -g '!**/souji-shokunin/tests/**' \
    -g '!**/.ufo-quarantine/**' -g '!**/.ufo/state' -g '!**/.ufo/state/**' \
    -g '!**/.ufo/watchdog.log' "${excludes[@]}" 2>/dev/null) || status=$?
  if [ "$status" -gt 1 ]; then printf 'unknown\n'; return; fi
  while IFS= read -r path; do
    [ -n "$path" ] || continue
    [[ "$path" != *[[:cntrl:]]* ]] || { printf 'unknown\n'; return; }
    canonical=$(canon_path "$repo/${path#./}")
    case "$canonical" in "$scope"|"$scope"/*) continue ;; esac
    n=$((n + 1))
  done <<< "$out"
  printf '%s\n' "$n"
}

s18_repo_gitdir() { # $1 worktree root -> resolved git dir on stdout
  local p=$1 g
  if [ -d "$p/.git" ]; then canon_path "$p/.git"; return 0; fi
  [ -f "$p/.git" ] || return 1
  g=$(sed -n 's/^gitdir: //p' "$p/.git" 2>/dev/null | head -1)
  [ -n "$g" ] || return 1
  case "$g" in /*) : ;; *) g="$p/$g" ;; esac
  canon_path "$g"
  return 0
}

s18_is_repo_root() { # $1 path -- repo root, not a linked worktree
  local p=$1 g
  [ -e "$p/.git" ] || return 1
  [ -d "$p/.git" ] && return 0
  [ -f "$p/.git" ] || return 1
  g=$(s18_repo_gitdir "$p") || return 1
  [ -e "$g" ] || return 1
  case "$g" in */worktrees/*) return 1 ;; esac
  return 0
}

# r10 cluster F (F1/F1b): structural owner discovery, multi-claimant records and
# conflict refusal live in the F1 override block appended after the guard (they
# must override the guard's own evaluate_worktree).
s18_old_scope() {
  local path=$1 cutoff=$2 p mtime ctime isroot=${3:-1}
  mtime=$(stat -c %Y -- "$path" 2>/dev/null) || return 1
  [ "$mtime" -lt "$cutoff" ] || return 1
  if [ "$isroot" = 0 ]; then
    ctime=$(stat -c %Z -- "$path" 2>/dev/null) || return 1
    [ "$ctime" -lt "$cutoff" ] || return 1
  fi
  if [ -d "$path" ] && [ ! -L "$path" ]; then
    for p in "$path"/* "$path"/.[!.]* "$path"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      s18_path_ok "$p" && s18_old_scope "$p" "$cutoff" 0 || return 1
    done
  fi
}

s18_scope_unreferenced() {
  local path=$1 repo=$2 scope=$3 p refs
  refs=$(count_live_refs "$path" "$repo" "$scope")
  if [ "$refs" != 0 ]; then NOTES+=("stale=live-refs=$refs"); return 1; fi
  if [ -d "$path" ]; then
    for p in "$path"/* "$path"/.[!.]* "$path"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      s18_scope_unreferenced "$p" "$repo" "$scope" || return 1
    done
  fi
}

try_stale() {
  local target=$1 repo=$2 kind now mtime tracked
  kind=$(scratch_type "$target") || { NOTES+=("stale=not-scratch-type"); return 1; }
  if [ -n "$repo" ]; then
    if ! tracked=$(git -C "$repo" ls-files -- "$target" 2>/dev/null); then
      NOTES+=("stale=tracking-unverifiable"); return 1
    fi
    if [ -n "$tracked" ]; then
      NOTES+=("stale=tracked-without-pushed-receipt"); return 1
    fi
  fi
  now=$(date +%s)
  if ! s18_old_scope "$target" "$((now - STALE_DAYS * 86400))" 1; then
    NOTES+=("stale=mtime-or-descendant-too-young"); return 1
  fi
  s18_scope_unreferenced "$target" "$repo" "$target" || return 1
  mtime=$(stat -c %Y -- "$target") || return 1
  R_VERDICT=SAFE; R_RECEIPT=stale; R_REASON=stale
  R_EVIDENCE="scratch-type=$kind refs=0 mtime-age-days=$(((now - mtime) / 86400)) descendants=old-and-unreferenced"
  return 0
}

s18_evaluate_worktree_one() {
  local target=$1 meta=$2 owner head branch unp uniq dirty refs status
  local -a roots=()
  IFS=$'\t' read -r owner head branch <<< "$meta"
  R_VERDICT=NOT-SAFE; R_RECEIPT=none; R_REASON=none
  if ! git -C "$owner" cat-file -e "$head^{commit}" 2>/dev/null; then
    R_RECEIPT=history-unverifiable; R_REASON=history-unverifiable
    R_EVIDENCE="worktree-head-unverifiable head=$head"; return
  fi
  if [ -n "$branch" ]; then
    if ! unp=$(git -C "$owner" rev-list --count "$branch" --not --remotes 2>/dev/null); then
      R_RECEIPT=history-unverifiable; R_REASON=history-unverifiable
      R_EVIDENCE="worktree-branch-unverifiable branch=$branch"; return
    fi
    if [ "$unp" != 0 ]; then
      R_RECEIPT=unpushed-branch; R_REASON=unpushed-branch
      R_EVIDENCE="branch=${branch#refs/heads/} unpushed=$unp dir=$([ -d "$target" ] && printf present || printf absent) owner=$(basename -- "$owner")"; return
    fi
  fi
  if [ ! -d "$target" ]; then
    if ! refs=$(git -C "$owner" for-each-ref --exclude='refs/jj/' --format='%(objectname)' 2>/dev/null); then
      R_EVIDENCE="durable-refs-unverifiable"; return
    fi
    if [ -n "$refs" ]; then mapfile -t roots <<< "$refs"; fi
    if ! uniq=$(git -C "$owner" rev-list --count "$head" --not "${roots[@]}" -- 2>/dev/null); then
      R_EVIDENCE="worktree-ancestry-unverifiable"; return
    fi
    if [ "$uniq" = 0 ]; then R_VERDICT=SAFE; R_RECEIPT=metadata-prune; R_REASON=metadata-prune; fi
    R_EVIDENCE="dir=absent unique=$uniq head=${head:0:12} owner=$(basename -- "$owner") durable-refs-only=yes"
    return
  fi
  if ! status=$(git -C "$target" --no-optional-locks status --porcelain 2>/dev/null); then
    R_RECEIPT=dirty; R_REASON=dirty; R_EVIDENCE="dir=present status-unverifiable"; return
  fi
  dirty=0
  [ -z "$status" ] || dirty=$(printf '%s\n' "$status" | wc -l)
  if [ "$dirty" != 0 ]; then R_RECEIPT=dirty; R_REASON=dirty; fi
  R_EVIDENCE="dir=present dirty=$dirty owner=$(basename -- "$owner")"
}

evaluate_path() {
  local raw=$1 target
  if ! s18_path_ok "$raw"; then
    R_VERDICT=NOT-SAFE; R_RECEIPT=secrets-refusal; R_REASON=secrets-refusal
    R_EVIDENCE="secret-shaped-or-protected-symlink-or-control-path-refused"; return 0
  fi
  target=$(canon_path "$raw")
  if [ -d "$target" ] && ! s18_scope_ok "$target"; then
    R_VERDICT=NOT-SAFE; R_RECEIPT=secrets-refusal; R_REASON=secrets-refusal
    R_EVIDENCE="protected-or-unsupported-descendant-refused"; return 0
  fi
  # r10 cluster F (F2): a repository root whose `.git` is a FILE is a repo root,
  # not an ordinary artifact -- the S17/S18 nested-metadata gate only inspects
  # directory targets, so without this the root fell through to the artifact
  # engine and earned a false SAFE(pushed).
  if [ -d "$target" ] && s18_is_repo_root "$target"; then
    evaluate_repo_root "$target"; return 0
  fi
  s18_evaluate_path "$raw"
}

if [ "$S18_KIND" = quarantine ]; then
  resolve_default_ref() {
    local repo=$1 ref refs
    if ref=$(git -C "$repo" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null) \
      && git -C "$repo" rev-parse --verify "$ref^{commit}" >/dev/null 2>&1; then
      printf '%s\n' "$ref"; return
    fi
    refs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null) || return 1
    refs=$(printf '%s\n' "$refs" | grep -v '^refs/remotes/origin/HEAD$') || return 1
    [[ "$refs" != *$'\n'* && -n "$refs" ]] || return 1
    printf '%s\n' "$refs"
  }

  s18_q_storage_ok() {
    local path=$1 expected="$Q_CREPO/.ufo-quarantine"
    case "$path" in "$expected/"*) : ;; *) return 1 ;; esac
    s18_path_ok "$path" || return 1
    [ "$(canon_path "$path")" = "$path" ]
  }

  run_verify() {
    local t=$1 rc=0 prefix rest rel
    V_VERDICT=ERROR; V_RECEIPT=engine-error; V_EV=invalid-engine-record
    if ! s18_path_ok "$t" || ! s18_path_ok "$VERIFY_BIN"; then
      V_EV=unsafe-input-path; return 0
    fi
    V_RAW=$(SHOKUNIN_ROOT="$SV_ROOT" SOUJI_LEDGER="$SV_LEDGER" \
      bash "$VERIFY_BIN" --stale-days "$STALE_DAYS" -- "$t" 2>"$ERRTMP") || rc=$?
    prefix=$'VERDICT\t'"$t"$'\t'
    if [ "$rc" != 0 ] || [[ "$V_RAW" = *$'\n'* || "$V_RAW" != "$prefix"* ]]; then return 0; fi
    rest=${V_RAW#"$prefix"}
    [[ "$rest" = *$'\t'* ]] || return 0
    V_VERDICT=${rest%%$'\t'*}; rest=${rest#*$'\t'}
    [[ "$rest" = *$'\t'* ]] || { V_VERDICT=ERROR; return 0; }
    V_RECEIPT=${rest%%$'\t'*}; V_EV=${rest#*$'\t'}
    if [[ "$V_EV" = *[[:cntrl:]]* ]] || [[ "$V_VERDICT" != SAFE && "$V_VERDICT" != NOT-SAFE ]]; then
      V_VERDICT=ERROR; V_RECEIPT=engine-error; return 0
    fi
    if [ "$V_VERDICT" = SAFE ] && [ "$V_RECEIPT" = pushed ]; then
      case "$t" in "$Q_CREPO/.ufo-quarantine/"*) return 0 ;; esac
      rel=${t#"$Q_CREPO/"}
      S18_PUSH_REF=$(resolve_default_ref "$Q_CREPO") || { V_VERDICT=ERROR; return 0; }
      S18_PUSH_OBJECT=$(git -C "$Q_CREPO" rev-parse --verify "$S18_PUSH_REF:$rel" 2>/dev/null) || V_VERDICT=ERROR
    fi
  }

  ledger_row_for() {
    local want=$1 row isdir=${ISDIR:-0}
    s18_path_ok "$SV_LEDGER" && [ -f "$SV_LEDGER" ] || return 0
    while IFS= read -r row || [ -n "$row" ]; do
      s18_row_parse "$row" || continue
      [ "$S18_SP" = "$want" ] || continue
      s18_row_ok "$want" "$isdir" || continue
      case "$(canon_path "$S18_VP")/" in "$QPATH/"*) continue ;; esac
      printf '%s\t%s\t%s\n' "$S18_SS" "$S18_VP" "$S18_VS"
      return 0
    done < "$SV_LEDGER"
  }

  flow_one() {
    local raw=$1
    [[ "$raw" = /* ]] || raw="$REPO/$raw"
    if ! s18_path_ok "$raw"; then
      N_TOTAL=$((N_TOTAL + 1)); block_one "$raw" unsafe-path "secret-shaped-or-protected-symlink-or-control-path-refused"; return 0
    fi
    raw=$(canon_path "$raw")
    local qpath rel status
    rel=${raw#"$Q_CREPO/"}
    qpath="$Q_CREPO/.ufo-quarantine/$(date -u +%F)/$rel"
    if ! s18_q_storage_ok "$qpath"; then
      N_TOTAL=$((N_TOTAL + 1)); block_one "$raw" quarantine-containment "symlink-or-noncanonical-quarantine-path"; return 0
    fi
    if git_tracked "$Q_CREPO" "$rel"; then
      status=$(git_dirty_tracked "$Q_CREPO" "$rel")
      if [ -n "$status" ]; then
        N_TOTAL=$((N_TOTAL + 1)); block_one "$raw" dirty-tracked "r7-gate2 dirty-tracked-content"; return 0
      fi
    fi
    s18_flow_one "$@"
  }

  second_check() {
    s18_second_check
    if ! s18_q_storage_ok "$QPATH"; then
      SC_PASS=0; SC_EV="$SC_EV containment=FAIL"; return 0
    fi
    if [ "$P1_VERDICT" = ERROR ]; then
      SC_PASS=0; SC_EV="$SC_EV engine-error=FAIL"
    fi
    if [ "$CLASS" = pushed ]; then
      local ref object touching intro krc
      if ! ref=$(resolve_default_ref "$CREPO") \
        || [ "$ref" != "${S18_PUSH_REF:-}" ] \
        || ! object=$(git -C "$CREPO" rev-parse --verify "$ref:$REL" 2>/dev/null) \
        || [ "$object" != "${S18_PUSH_OBJECT:-}" ]; then
        SC_PASS=0; SC_EV="$SC_EV default-snapshot=FAIL"
      fi
      intro=$(git -C "$CREPO" log --diff-filter=A --format=%H -1 -- "$REL" 2>/dev/null) || intro=""
      if [ -z "$intro" ] || [ -z "${ref:-}" ] \
        || ! git -C "$CREPO" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
        SC_PASS=0; SC_EV="$SC_EV default-ancestry=FAIL"
      fi
      if ! touching=$(git -C "$CREPO" log --format=%H HEAD --branches --not --remotes -- "$REL" 2>/dev/null) || [ -n "$touching" ]; then
        SC_PASS=0; SC_EV="$SC_EV head-history=FAIL"
      fi
      krc=0; jj_keep_novel "$CREPO" "$REL" || krc=$?
      if [ "$krc" != 1 ]; then SC_PASS=0; SC_EV="$SC_EV head-history=FAIL"; fi
    fi
    return 0
  }
fi


# ---- r10 cluster F (F1/F1b) ownership + registration conflicts, adopted by S15 ----
# A linked worktree whose owner directory is not named `*-shokunin` was never
# scanned, so it fell through to a stale receipt and was DELETED (J22); and two
# registrations for one path resolved last-writer-wins, letting a pushed
# registration mask an unpushed one (J20). Discovery is now structural and every
# claimant is evaluated, failing closed when they disagree.
scan_worktrees() {
  local repo gd path head branch line
  for repo in "$SHOKUNIN_ROOT" "$SHOKUNIN_ROOT"/*; do
    [ -d "$repo" ] || continue
    [ -e "$repo/.git" ] || continue
    gd=$(s18_repo_gitdir "$repo") || continue
    case "$gd" in */worktrees/*) continue ;; esac
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

_wt_record() { # $1 repo, $2 path, $3 head, $4 branch -- every claimant is kept
  local repo=$1 path=$2 head=$3 branch=$4 cp
  [ -n "$path" ] || return 0
  [ "$path" = "$repo" ] && return 0
  cp=$(canon_path "$path")
  if [ -n "${WT_MAP[$cp]:-}" ]; then
    WT_MAP["$cp"]="${WT_MAP[$cp]}"$'\n'"$repo"$'\t'"$head"$'\t'"$branch"
  else
    WT_MAP["$cp"]="$repo"$'\t'"$head"$'\t'"$branch"
  fi
  return 0
}

evaluate_worktree() { # $1 target, $2 meta: one owner<TAB>head<TAB>branch per line
  local target=$1 meta=$2 line ov="" orc="" oev="" first=1 any_safe=0 any_ns=0
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    s18_evaluate_worktree_one "$target" "$line"
    if [ "$R_VERDICT" = NOT-SAFE ]; then any_ns=1; else any_safe=1; fi
    if [ "$first" = 1 ] || [ "$R_VERDICT" = NOT-SAFE ]; then
      ov=$R_VERDICT; orc=$R_RECEIPT; oev=$R_EVIDENCE; first=0
    fi
  done <<< "$meta"
  R_VERDICT=$ov; R_RECEIPT=$orc; R_EVIDENCE=$oev
  if [ "$any_safe" = 1 ] && [ "$any_ns" = 1 ]; then
    R_VERDICT=NOT-SAFE; R_RECEIPT=registration-conflict
    R_EVIDENCE="multiple registrations disagree ($oev)"
  fi
  return 0
}

# ---- end inlined S18 guard ----

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

  # --- r17 jj fixtures (J1-J5): keep refs hold only unpushed heads; a
  # keep-only commit refuses only when its blob at the target is novel ---
  local RJ="$ST_FLEET/jjrepo-shokunin"
  st_init_repo "$RJ" master
  mkdir -p "$RJ/jj"
  printf 'base n\n' > "$RJ/jj/novel.txt"
  printf 'base s\n' > "$RJ/jj/same.txt"
  printf 'base g\n' > "$RJ/jj/gone.txt"
  local cj0; cj0=$(st_commit "$RJ" "" "j0 baseline")
  # pushed tip: distinct content on every jj path
  printf 'push n\n' > "$RJ/jj/novel.txt"
  printf 'push s\n' > "$RJ/jj/same.txt"
  printf 'push g\n' > "$RJ/jj/gone.txt"
  local cjp; cjp=$(st_commit "$RJ" "$cj0" "jp pushed tip")
  git -C "$RJ" update-ref refs/heads/master "$cjp"
  git -C "$RJ" update-ref refs/remotes/origin/master "$cjp"
  git -C "$RJ" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  # a side remote ref carrying the alternate same.txt blob (already pushed)
  printf 'alt s\n' > "$RJ/jj/same.txt"
  local cjx; cjx=$(st_commit "$RJ" "$cj0" "jx alt same blob on a side remote")
  git -C "$RJ" update-ref refs/remotes/origin/alt "$cjx"
  printf 'push s\n' > "$RJ/jj/same.txt"
  git -C "$RJ" add -- jj/same.txt
  # J1: keep-only commit with novel content at jj/novel.txt
  printf 'novel n\n' > "$RJ/jj/novel.txt"
  local cjn; cjn=$(st_commit "$RJ" "$cjp" "jn keep-only novel content")
  git -C "$RJ" update-ref refs/jj/keep/"$cjn" "$cjn"
  printf 'push n\n' > "$RJ/jj/novel.txt"
  git -C "$RJ" add -- jj/novel.txt
  # J2: keep-only predecessor whose same.txt blob a pushed ref already has
  printf 'alt s\n' > "$RJ/jj/same.txt"
  local cjs; cjs=$(st_commit "$RJ" "$cjp" "js keep-only predecessor with pushed blob")
  git -C "$RJ" update-ref refs/jj/keep/"$cjs" "$cjs"
  printf 'push s\n' > "$RJ/jj/same.txt"
  git -C "$RJ" add -- jj/same.txt
  # J3: keep-only deletion is never novel
  rm -f "$RJ/jj/gone.txt"
  local cjd; cjd=$(st_commit "$RJ" "$cjp" "jd keep-only deletion")
  git -C "$RJ" update-ref refs/jj/keep/"$cjd" "$cjd"
  printf 'push g\n' > "$RJ/jj/gone.txt"
  git -C "$RJ" add -- jj/gone.txt
  # J4: absent-worktree head held only by refs/jj/keep
  st_register_worktree "$RJ" wt-jj "$ST_TMP/wt-jj" "$cjn" ""
  # J5: absent-worktree head held only by refs/stash (a durable root)
  local cjst; cjst=$(git -C "$RJ" commit-tree "$(git -C "$RJ" rev-parse "$cj0^{tree}")" -p "$cj0" -m "stash-only head")
  git -C "$RJ" update-ref refs/stash "$cjst"
  st_register_worktree "$RJ" wt-stash "$ST_TMP/wt-stash" "$cjst" ""

  # J6/J7 (r17 w2): directory targets compare leaf blobs, never the tree id.
  mkdir -p "$RJ/jj/dirsw" "$RJ/jj/dirnv"
  printf 'fbase\n' > "$RJ/jj/dirsw/f.txt"
  printf 'gbase\n' > "$RJ/jj/dirsw/g.txt"
  printf 'nbase\n' > "$RJ/jj/dirnv/n.txt"
  local cjd1; cjd1=$(st_commit "$RJ" "$cjp" "jd1 dir base")
  printf 'ftip\n' > "$RJ/jj/dirsw/f.txt"
  printf 'gtip\n' > "$RJ/jj/dirsw/g.txt"
  printf 'ntip\n' > "$RJ/jj/dirnv/n.txt"
  local cjb; cjb=$(st_commit "$RJ" "$cjd1" "jb pushed dir tip")
  git -C "$RJ" update-ref refs/heads/master "$cjb"
  git -C "$RJ" update-ref refs/remotes/origin/master "$cjb"
  # J6: keep-only commit recomposes {fbase, gtip} -- a tree id that was
  # never pushed, built entirely of pushed dirsw blobs; must not refuse.
  printf 'fbase\n' > "$RJ/jj/dirsw/f.txt"
  local cjds; cjds=$(st_commit "$RJ" "$cjb" "jdsw keep-only recomposed dirsw")
  git -C "$RJ" update-ref refs/jj/keep/"$cjds" "$cjds"
  printf 'ftip\n' > "$RJ/jj/dirsw/f.txt"
  git -C "$RJ" add -- jj/dirsw
  # J7: keep-only commit adding a never-pushed blob under dirnv -> refuses.
  printf 'novel dir blob\n' > "$RJ/jj/dirnv/m.txt"
  local cjdn; cjdn=$(st_commit "$RJ" "$cjb" "jdn keep-only novel dirnv blob")
  git -C "$RJ" update-ref refs/jj/keep/"$cjdn" "$cjdn"
  rm -f "$RJ/jj/dirnv/m.txt"
  git -C "$RJ" add -- jj/dirnv
  # J8 (r17 w2): a single broken-name keep ref cannot hide the keep query:
  # for-each-ref's stderr warning counts as "keep refs exist", then
  # rev-list fails and the caller takes its history-unverifiable path.
  local RB="$ST_FLEET/brokenref-shokunin"
  st_init_repo "$RB" master
  printf 'broken probe\n' > "$RB/f.txt"
  local cb; cb=$(st_commit "$RB" "" "b baseline")
  git -C "$RB" update-ref refs/heads/master "$cb"
  git -C "$RB" update-ref refs/remotes/origin/master "$cb"
  git -C "$RB" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  mkdir -p "$RB/.git/refs/jj/keep"
  printf '%s\n' "$cb" > "$RB/.git/refs/jj/keep/has space"
  # J9 (r17 w2): a path whose remote history exceeds the pipe buffer must
  # not let SIGPIPE fabricate a "novel" verdict for an identical-blob
  # predecessor (the w1 pipeline died under pipefail; the current helper
  # runs one grep over the whole candidate set, so there is no pipe to
  # kill). 2500 rev-list commits via fast-import keep the fixture cheap.
  local RS="$ST_FLEET/sigpipe-shokunin" SI
  st_init_repo "$RS" master
  git -C "$RS" config gc.auto 0
  mkdir -p "$RS/jj"
  {
    cat <<'FI'
blob
mark :1
data 3
v1
blob
mark :2
data 3
v2
FI
    cat <<FI
commit refs/heads/master
mark :10
committer Souji Test <st@example.invalid> 1700000001 +0000
data 3
c1
M 100644 :1 jj/sig.txt

FI
    SI=2
    while [ "$SI" -le 2500 ]; do
      cat <<FI
commit refs/heads/master
mark :$((10 + SI - 1))
committer Souji Test <st@example.invalid> $((1700000000 + SI)) +0000
data $((2 + ${#SI}))
c$SI
from :$((10 + SI - 2))
M 100644 :$((SI % 2 + 1)) jj/sig.txt

FI
      SI=$((SI + 1))
    done
  } | git -C "$RS" fast-import --quiet
  git -C "$RS" update-ref refs/remotes/origin/master refs/heads/master
  git -C "$RS" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  # worktree + index at the pushed tip so the status gate stays clean
  printf 'v1\n' > "$RS/jj/sig.txt"
  git -C "$RS" add -- jj/sig.txt
  local csp; csp=$(printf 'sp keep\n' | git -C "$RS" commit-tree "$(git -C "$RS" rev-parse 'refs/heads/master^{tree}')" -p 'refs/heads/master^')
  git -C "$RS" update-ref refs/jj/keep/"$csp" "$csp"



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
  # r17 jj-colocated shapes: keep-only commits refuse only on novel blobs;
  # keep refs are never durable roots, refs/stash stays one.
  st_case J1 NOT-SAFE none "jj-keep-novel" "$ST_FLEET/jjrepo-shokunin/jj/novel.txt"
  st_case J2 SAFE pushed "" "$ST_FLEET/jjrepo-shokunin/jj/same.txt"
  st_case J3 SAFE pushed "" "$ST_FLEET/jjrepo-shokunin/jj/gone.txt"
  st_case J4 NOT-SAFE none "durable-refs-only=yes" "$ST_TMP/wt-jj"
  st_case J5 SAFE metadata-prune "unique=0" "$ST_TMP/wt-stash"
  # r17 w2 detectors: directory targets use leaf blobs (J6 recombination of
  # pushed blobs stays SAFE, J7 novel blob under a dir refuses); a broken
  # keep ref name fails closed (J8); deep remote history cannot let a pipe
  # fabricate novelty for an identical-blob predecessor (J9).
  st_case J6 SAFE pushed "" "$ST_FLEET/jjrepo-shokunin/jj/dirsw"
  st_case J7 NOT-SAFE none "jj-keep-novel" "$ST_FLEET/jjrepo-shokunin/jj/dirnv"
  st_case J8 NOT-SAFE none "history-unverifiable" "$ST_FLEET/brokenref-shokunin/f.txt"
  st_case J9 SAFE pushed "" "$ST_FLEET/sigpipe-shokunin/jj/sig.txt"



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
