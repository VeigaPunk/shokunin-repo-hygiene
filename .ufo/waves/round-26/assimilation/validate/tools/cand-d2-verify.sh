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

# Secret-shaped path components; the sweep never *reads* these files
# (province: souji cites paths and modes only), so a reference held only
# inside one is invisible to the sweep. D2-6 discloses the count instead.
D2_SECRET_GLOBS=(
  --iglob '!**/*.env' --iglob '!**/.env' --iglob '!**/.env.*' --iglob '!**/.envrc'
  --iglob '!**/*credential*' --iglob '!**/*secret*' --iglob '!**/id_*' --iglob '!**/*.pem'
)

# D2-6: number of secret-shaped files in the sweep scope, listed by NAME only
# (`rg --files` never opens a file). Disclosed in stale evidence so an
# unverifiable reference surface is visible in the receipt.
d2_secret_file_count() { # $1 repo
  local repo=$1 out
  [ -d "$repo" ] || { printf '0\n'; return 0; }
  out=$( cd -- "$repo" && rg --files --hidden --no-ignore -g '!.git' -g '!**/.git/**' \
        --iglob '**/*.env' --iglob '**/.env' --iglob '**/.env.*' --iglob '**/.envrc' \
        --iglob '**/*credential*' --iglob '**/*secret*' --iglob '**/id_*' --iglob '**/*.pem' \
        . 2>/dev/null | grep -c . || true )
  printf '%s\n' "${out// /}"
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
  # D2-1/D2-2: --hidden so dotfile references count; --text so a reference in
  # a binary file counts (rg skips binaries without it). Both were false-SAFE
  # stale receipts before (census/round-10/S08-cluster-D-repro.py K, A).
  out=$( cd "$repo" && rg -l --hidden --text --no-ignore --fixed-strings -e "$base" . \
        -g '!.git' -g '!**/.git/**' \
        -g '!souji-shokunin/census/**' -g '!**/souji-shokunin/census/**' \
        -g '!souji-shokunin/tests/**' -g '!**/souji-shokunin/tests/**' \
        -g '!**/.ufo-quarantine/**' \
        -g '!**/.ufo/state' -g '!**/.ufo/state/**' -g '!**/.ufo/watchdog.log' \
        "${D2_SECRET_GLOBS[@]}" \
        "${self_globs[@]}" 2>/dev/null )
  status=$?
  set -e
  if [ "$status" -gt 1 ]; then printf 'unknown\n'; return 0; fi
  n=$(printf '%s\n' "$out" | grep -c . || true)
  printf '%s\n' "${n// /}"
}

# D2-3: every entry in the scope (recursively) must be older than the cutoff.
# A fresh descendant inside an aged container is live work (probe cases B, P).
D2_MAX_SCOPE=${D2_MAX_SCOPE:-20000}
D2_SCOPE_SEEN=0

d2_scope_old() { # $1 path, $2 cutoff-epoch; 0 = whole scope older
  local path=$1 cutoff=$2 p mtime
  D2_SCOPE_SEEN=$((D2_SCOPE_SEEN + 1))
  [ "$D2_SCOPE_SEEN" -le "$D2_MAX_SCOPE" ] || return 1
  mtime=$(stat -c %Y -- "$path" 2>/dev/null) || return 1
  [ "$mtime" -lt "$cutoff" ] || return 1
  if [ -d "$path" ]; then
    for p in "$path"/* "$path"/.[!.]* "$path"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      [ ! -L "$p" ] || return 1
      d2_scope_old "$p" "$cutoff" || return 1
    done
  fi
  return 0
}

# D2-4: no entry in the scope may be named by any file outside the scope.
# One batched sweep over every name in the scope (rg -f takes the name list),
# then a canonical-path filter that drops the scope's own self-references.
# Per-name sweeps cost one ripgrep per descendant; this is one for the scope.
d2_collect_names() { # $1 path, $2 out-file
  local p
  printf '%s\n' "$(basename -- "$1")" >> "$2"
  if [ -d "$1" ]; then
    for p in "$1"/* "$1"/.[!.]* "$1"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      d2_collect_names "$p" "$2"
    done
  fi
  return 0
}

d2_scope_unreferenced() { # $1 path, $2 repo, $3 scope-root
  local target=$1 repo=$2 scope=$3 nf unf out status line canon hits=0
  [ -n "$repo" ] && [ -d "$repo" ] || return 0
  # The name list is scratch inside the run's own temp dir; when even that
  # cannot be written the sweep is unverifiable, never "zero references".
  nf=$(mktemp -p "${D2_TMPDIR:-/var/tmp}" souji-d2names.XXXXXX 2>/dev/null) || nf=""
  if [ -z "$nf" ]; then NOTES+=("stale=reference-sweep-unverifiable"); return 1; fi
  unf="${nf}.uniq"
  d2_collect_names "$target" "$nf" || { rm -f -- "$nf" "$unf"
    NOTES+=("stale=reference-sweep-unverifiable"); return 1; }
  if ! LC_ALL=C sort -u "$nf" > "$unf" 2>/dev/null; then
    rm -f -- "$nf" "$unf"
    NOTES+=("stale=reference-sweep-unverifiable"); return 1
  fi
  set +e
  out=$( cd -- "$repo" && rg -l --hidden --text --no-ignore --fixed-strings -f "$unf" . \
        -g '!.git' -g '!**/.git/**' \
        -g '!souji-shokunin/census/**' -g '!**/souji-shokunin/census/**' \
        -g '!souji-shokunin/tests/**' -g '!**/souji-shokunin/tests/**' \
        -g '!**/.ufo-quarantine/**' \
        -g '!**/.ufo/state' -g '!**/.ufo/state/**' -g '!**/.ufo/watchdog.log' \
        "${D2_SECRET_GLOBS[@]}" 2>/dev/null )
  status=$?
  set -e
  rm -f -- "$nf" "$unf"
  if [ "$status" -gt 1 ]; then NOTES+=("stale=reference-sweep-unverifiable"); return 1; fi
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    canon=$(canon_path "$repo/${line#./}")
    case "$canon" in "$scope"|"$scope"/*) continue ;; esac
    hits=$((hits + 1))
  done <<< "$out"
  if [ "$hits" -gt 0 ]; then NOTES+=("stale=live-refs=$hits"); return 1; fi
  return 0
}

try_pushed() { # $1 target, $2 repo; SAFE(pushed) or fail-with-note
  local target=$1 repo=$2 intro ref status touching snap
  [ -n "$repo" ] || { NOTES+=("pushed=no-repo"); return 1; }
  # D2-7: uncommitted or untracked content inside the scope is unpublished
  # bytes; `--ignored=matching` also catches ignored descendants (probe C,D,G).
  if ! status=$(git -C "$repo" --no-optional-locks status --porcelain \
        --untracked-files=all --ignored=matching -- "$target" 2>/dev/null); then
    NOTES+=("pushed=status-unverifiable"); return 1
  fi
  if [ -n "$status" ]; then
    NOTES+=("pushed=dirty-or-untracked-content"); return 1
  fi
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
  # r6 fix, widened in D2-8: a pushed receipt also requires that NO commit
  # outside the remote-tracking refs touches the path. `--branches` misses
  # commits held only by hidden refs (refs/hidden/*, stash) and by linked
  # worktree HEADs; `--all` covers every ref and `--not --remotes` subtracts
  # exactly what is published (probe F, M, I).
  if ! touching=$(git -C "$repo" log --format=%H --all --not --remotes -- "$target" 2>/dev/null); then
    NOTES+=("pushed=history-unverifiable"); return 1
  fi
  if [ -n "$touching" ]; then
    NOTES+=("pushed=unpushed-commits-touching intro=${intro:0:12}")
    return 1
  fi
  if ! git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
    NOTES+=("pushed=not-ancestor intro=${intro:0:12} ref=$ref")
    return 1
  fi
  # D2-9: the default ref's snapshot must equal the working tree, or a later
  # local commit changed the bytes the receipt would certify (probe E, M).
  if ! snap=$(git -C "$repo" --no-optional-locks diff --name-only --no-ext-diff \
        --no-textconv "$ref" -- "$target" 2>/dev/null); then
    NOTES+=("pushed=default-snapshot-unverifiable"); return 1
  fi
  if [ -n "$snap" ]; then
    NOTES+=("pushed=default-snapshot-mismatch"); return 1
  fi
  R_VERDICT=SAFE; R_RECEIPT=pushed
  R_EVIDENCE="intro=${intro:0:12} ref=$ref ancestor=yes snapshot=equal clean=yes"
  return 0
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
  local target=$1 repo=$2 kind mtime now age refs tracked secs
  kind=$(scratch_type "$target") || { NOTES+=("stale=not-scratch-type"); return 1; }
  mtime=$(stat -c %Y -- "$target" 2>/dev/null || true)
  [ -n "$mtime" ] || { NOTES+=("stale=no-mtime"); return 1; }
  now=$(date +%s)
  age=$(( now - mtime ))
  if [ "$age" -le $(( STALE_DAYS * 86400 )) ]; then
    NOTES+=("stale=mtime-age-days=$(( age / 86400 ))<=$STALE_DAYS")
    return 1
  fi
  # D2-5: a tracked path with no pushed receipt must not fall through to stale
  # -- local-only committed content is live work (probe case E).
  if [ -n "$repo" ]; then
    if ! tracked=$(git -C "$repo" ls-files -- "$target" 2>/dev/null); then
      NOTES+=("stale=tracking-unverifiable"); return 1
    fi
    if [ -n "$tracked" ]; then
      NOTES+=("stale=tracked-without-pushed-receipt"); return 1
    fi
  fi
  # D2-4: whole scope must be aged (fresh descendant = live work) ...
  D2_SCOPE_SEEN=0
  if ! d2_scope_old "$target" "$(( now - STALE_DAYS * 86400 ))"; then
    NOTES+=("stale=mtime-or-descendant-too-young"); return 1
  fi
  # ... and every name in the scope must be unreferenced from outside it.
  d2_scope_unreferenced "$target" "$repo" "$target" || return 1
  # D2-6: disclose the unread secret-shaped surface (province: names only).
  secs=$(d2_secret_file_count "$repo")
  R_VERDICT=SAFE; R_RECEIPT=stale
  R_EVIDENCE="scratch-type=$kind refs=0 mtime-age-days=$(( age / 86400 ))"
  R_EVIDENCE="$R_EVIDENCE descendants=old-and-unreferenced"
  [ "${secs:-0}" = 0 ] || R_EVIDENCE="$R_EVIDENCE unread-secret-shaped-files=$secs"
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
  local -a roots=()
  IFS=$'\t' read -r owner head branch <<< "$meta"
  if [ -d "$target" ]; then present=present; else present=absent; fi
  # D2-11: an unparseable or missing HEAD is unverifiable, never a verdict.
  if [ -n "$head" ] && ! git -C "$owner" cat-file -e "$head^{commit}" 2>/dev/null; then
    R_VERDICT=NOT-SAFE; R_RECEIPT=git-unverifiable
    R_EVIDENCE="worktree-head-unverifiable head=${head:0:12} owner=$(basename -- "$owner")"
    return 0
  fi
  if [ -n "$branch" ]; then
    if ! unp=$(git -C "$owner" rev-list --count "$branch" --not --remotes 2>/dev/null); then
      R_VERDICT=NOT-SAFE; R_RECEIPT=git-unverifiable
      R_EVIDENCE="worktree commit query failed"
      return 0
    fi
    if [ "${unp:-0}" -gt 0 ]; then
      R_VERDICT=NOT-SAFE; R_RECEIPT=unpushed-branch
      R_EVIDENCE="branch=${branch#refs/heads/} unpushed=$unp dir=$present owner=$(basename -- "$owner")"
      return 0
    fi
  fi
  if [ "$present" = absent ]; then
    # D2-12: ancestry is judged against durable refs only. `--not --all`
    # resolves linked-worktree HEADs on git 2.55, so a commit held solely by
    # this very registration counted as reachable and read unique=0 (probe I).
    if ! git -C "$owner" for-each-ref --format='%(objectname)' 2>/dev/null | grep -q .; then
      uniq=$(git -C "$owner" rev-list --count "$head" -- 2>/dev/null) || uniq=""
    else
      mapfile -t roots < <(git -C "$owner" for-each-ref --format='%(objectname)' 2>/dev/null)
      uniq=$(git -C "$owner" rev-list --count "$head" --not "${roots[@]}" -- 2>/dev/null) || uniq=""
    fi
    if [ -z "$uniq" ]; then
      R_VERDICT=NOT-SAFE; R_RECEIPT=git-unverifiable
      R_EVIDENCE="worktree ancestry query failed head=${head:0:12}"
      return 0
    fi
    if [ "$uniq" = 0 ]; then
      R_VERDICT=SAFE; R_RECEIPT=metadata-prune
      R_EVIDENCE="dir=absent unique=0 head=${head:0:12} owner=$(basename -- "$owner") durable-refs-only=yes"
      return 0
    fi
    R_VERDICT=NOT-SAFE; R_RECEIPT=none
    R_EVIDENCE="dir=absent unique=$uniq head=${head:0:12} owner=$(basename -- "$owner")"
    return 0
  fi
  if st=$(git -C "$target" --no-optional-locks status --porcelain 2>/dev/null); then
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

# D2-13: an unreadable scope is not an empty scope. A traversal that cannot
# finish must refuse rather than let a partial view certify a removal.
d2_scope_readable() { # $1 dir
  local d=$1 p
  [ -r "$d" ] && [ -x "$d" ] || return 1
  if [ -d "$d" ]; then
    for p in "$d"/* "$d"/.[!.]* "$d"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      if [ -L "$p" ]; then
        # a symlink in a removal scope is never resolvable here
        return 1
      elif [ -d "$p" ]; then
        d2_scope_readable "$p" || return 1
      elif [ ! -f "$p" ]; then
        return 1
      fi
    done
  fi
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
    # D2-13: traversal that cannot complete is not an empty scope.
    if ! d2_scope_readable "$target"; then
      R_RECEIPT=unreadable-or-symlinked-scope
      R_EVIDENCE="scope contains a symlink or unreadable entry"
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

# D2-10: every immediate child of the fleet root that is a main repo, not just
# the ones the `*-shokunin` glob happens to match. A registered worktree whose
# owner is named otherwise was invisible, so its directory fell through to the
# stale sweep and could be certified removable (probe case H, R).
d2_list_fleet_repos() {
  local root=$1 d base
  [ -d "$root" ] || return 0
  if [ -e "$root/.git" ]; then printf '%s\n' "$root"; fi
  shopt -s nullglob
  for d in "$root"/*/; do
    [ -d "$d" ] || continue
    base=$(basename -- "${d%/}")
    case "$base" in .*) continue ;; esac
    [ -d "${d%/}/.git" ] || continue
    printf '%s\n' "${d%/}"
  done
  shopt -u nullglob
  return 0
}

scan_worktrees() {
  local repo path head branch line
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
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
  done < <(d2_list_fleet_repos "$SHOKUNIN_ROOT")
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
  # Host note: /tmp is quota-limited on this machine (r8/r9 incident), so the
  # selftest defaults to /var/tmp and only honours TMPDIR when it is writable.
  local base=/var/tmp
  if [ -n "${TMPDIR:-}" ] && [ -d "$TMPDIR" ] && [ -w "$TMPDIR" ] \
     && [ "$TMPDIR" != "/tmp" ]; then
    base=$TMPDIR
  fi
  ST_TMP=$(mktemp -d "$base/souji-verify-selftest.XXXXXX")
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

  # --- D2 cluster-D regressions (round 10, seat S08) ---------------------
  # Commit-free fixtures stay in repo-shokunin so the F/E expectations above
  # keep their origin/master position; anything that advances a ref lives in
  # its own d2-shokunin repo.
  # D2-1: reference reachable only through a dotfile (rg needs --hidden)
  printf 'payload\n' > "$R/.scratch/old-d2a.out"
  printf 'old-d2a.out is the active artifact\n' > "$R/.scratch/.active-ref"
  # D2-2: reference reachable only inside a binary file (rg needs --text)
  printf 'payload\n' > "$R/.scratch/old-d2b.out"
  printf '\000\001old-d2b.out\000\002' > "$R/blob-d2.bin"
  # D2-3: aged scratch dir carrying a fresh descendant
  mkdir -p "$R/.scratch/aged-d2c"
  printf 'old\n' > "$R/.scratch/aged-d2c/old.txt"
  touch -d '3 days ago' "$R/.scratch/aged-d2c/old.txt" "$R/.scratch/aged-d2c"
  printf 'fresh\n' > "$R/.scratch/aged-d2c/fresh.txt"
  # D2-3b: aged dir, aged child, fresh grandchild
  mkdir -p "$R/.scratch/aged-d2d/mid"
  printf 'leaf\n' > "$R/.scratch/aged-d2d/mid/leaf.md"
  touch -d '3 days ago' "$R/.scratch/aged-d2d" "$R/.scratch/aged-d2d/mid" "$R/.scratch/aged-d2d/mid/leaf.md"
  printf 'fresh grandchild\n' > "$R/.scratch/aged-d2d/mid/fresh.md"
  touch -d '3 days ago' "$R/.scratch/old-d2a.out" "$R/.scratch/old-d2b.out" "$R/.scratch"
  # D2-13: symlink inside a removal scope
  mkdir -p "$R/.scratch/aged-d2l"
  printf 'target\n' > "$R/real-d2l.txt"
  ln -s "$R/real-d2l.txt" "$R/.scratch/aged-d2l/link"
  touch -h -d '3 days ago' "$R/.scratch/aged-d2l/link"
  touch -d '3 days ago' "$R/.scratch/aged-d2l"
  # D2-C1 control: an aged, unreferenced scratch dir stays removable
  mkdir -p "$R/.scratch/aged-d2m"
  printf 'aged unique payload\n' > "$R/.scratch/aged-d2m/notes.md"
  touch -d '3 days ago' "$R/.scratch/aged-d2m" "$R/.scratch/aged-d2m/notes.md"

  # --- d2-shokunin: pushed-receipt regressions (own ref history) ---------
  local D2="$ST_FLEET/d2-shokunin"
  st_init_repo "$D2" master
  mkdir -p "$D2/.scratch"
  printf 'seed\n' > "$D2/seed.txt"
  local d1; d1=$(st_commit "$D2" "" "d1 seed")
  git -C "$D2" update-ref refs/remotes/origin/master "$d1"
  git -C "$D2" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$D2" update-ref refs/heads/master "$d1"
  # D2-5: tracked local-only scratch-type file must not fall through to stale.
  # Order matters: everything that must be pushed is committed and pushed
  # FIRST (pushed-d2p), and only then is the unpushed state created. A later
  # commit would otherwise sweep these files into the pushed snapshot.
  mkdir -p "$D2/bundle-d2f" "$D2/bundle-d2g"
  printf 'preserved\n' > "$D2/bundle-d2f/public.txt"
  printf 'preserved\n' > "$D2/bundle-d2g/public.txt"
  printf 'keep-d2h\n' > "$D2/keep-d2h.txt"
  local d2p; d2p=$(st_commit "$D2" "$d1" "d2p pushes bundle-d2f, bundle-d2g, keep-d2h.txt")
  git -C "$D2" update-ref refs/heads/master "$d2p"
  git -C "$D2" update-ref refs/remotes/origin/master "$d2p"
  # D2-5: local-only commit (not on origin/master)
  printf 'local only\n' > "$D2/local-d2e.out"
  local d2l; d2l=$(st_commit "$D2" "$d2p" "d2l local-only adds local-d2e.out")
  git -C "$D2" update-ref refs/heads/master "$d2l"
  touch -d '3 days ago' "$D2/local-d2e.out"
  # D2-8: commit touching the path, held only by a hidden ref
  printf 'hidden edit\n' > "$D2/keep-d2h.txt"
  git -C "$D2" add -A
  local htree; htree=$(git -C "$D2" write-tree)
  local hsha; hsha=$(printf 'hidden\n' | git -C "$D2" commit-tree "$htree" -p "$d2p")
  git -C "$D2" update-ref refs/hidden/d2 "$hsha"
  git -C "$D2" update-ref refs/heads/master "$d2l"
  # D2-12: detached registration whose HEAD is a unique commit (git 2.55 skew)
  local dtree dsha
  dtree=$(git -C "$D2" write-tree)
  dsha=$(printf 'detached\n' | git -C "$D2" commit-tree "$dtree" -p "$d2p")
  st_register_worktree "$D2" wt-d2i "$ST_TMP/wt-d2i" "$dsha" ""
  # D2-11: registration whose HEAD is not a commit object
  st_register_worktree "$D2" wt-d2j "$ST_TMP/wt-d2j" "not-a-real-object-name" ""
  # Restore the index/working tree to the pushed snapshot so the unpushed
  # state below is exactly: local-d2e.out (tracked, local commit),
  # bundle-d2f/local.txt (untracked), bundle-d2g/public.txt (dirty),
  # keep-d2h.txt (clean, but touched by the hidden ref).
  git -C "$D2" read-tree "$d2p"
  printf 'keep-d2h\n' > "$D2/keep-d2h.txt"
  printf 'unpublished\n' > "$D2/bundle-d2f/local.txt"
  printf 'uncommitted\n' > "$D2/bundle-d2g/public.txt"
  # read-tree dropped local-d2e.out from the index; restore it as tracked so
  # the D2-5 state matches the probe (tracked, local-only commit, aged).
  git -C "$D2" update-index --add \
    --cacheinfo "100644,$(git -C "$D2" rev-parse "$d2l:local-d2e.out"),local-d2e.out"

  # D2-10: live registered worktree owned by a repo the glob never matches
  local RL="$ST_FLEET/legacy-lane"
  st_init_repo "$RL" main
  printf 'legacy\n' > "$RL/seed.txt"
  local l1; l1=$(st_commit "$RL" "" "l1 legacy seed")
  git -C "$RL" update-ref refs/heads/main "$l1"
  git -C "$RL" update-ref refs/remotes/origin/main "$l1"
  git -C "$RL" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
  mkdir -p "$RL/.scratch/wt-d2k"
  st_register_worktree "$RL" wt-d2k "$RL/.scratch/wt-d2k" "$l1" ""
  printf 'stray\n' > "$RL/.scratch/wt-d2k/stray.txt"
  touch -d '3 days ago' "$RL/.scratch/wt-d2k"
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

  # D2 cluster-D regressions (round 10, seat S08)
  local D2="$ST_FLEET/d2-shokunin"
  st_case D2-1 NOT-SAFE none "" "$R/.scratch/old-d2a.out"
  st_case D2-2 NOT-SAFE none "" "$R/.scratch/old-d2b.out"
  st_case D2-3 NOT-SAFE none "" "$R/.scratch/aged-d2c"
  st_case D2-3b NOT-SAFE none "" "$R/.scratch/aged-d2d"
  st_case D2-5 NOT-SAFE none "" "$D2/local-d2e.out"
  st_case D2-7a NOT-SAFE none "" "$D2/bundle-d2f"
  st_case D2-7b NOT-SAFE none "" "$D2/bundle-d2g"
  st_case D2-8 NOT-SAFE none "" "$D2/keep-d2h.txt"
  st_case D2-10 NOT-SAFE dirty "" "$ST_FLEET/legacy-lane/.scratch/wt-d2k"
  st_case D2-11 NOT-SAFE git-unverifiable "worktree-head-unverifiable" "$ST_TMP/wt-d2j"
  st_case D2-12 NOT-SAFE none "unique=1" "$ST_TMP/wt-d2i"
  st_case D2-13 NOT-SAFE unreadable-or-symlinked-scope "" "$R/.scratch/aged-d2l"
  # D2 controls: the positive paths must still work
  st_case D2-C1 SAFE stale "refs=0" "$R/.scratch/aged-d2m"
  st_case D2-C2 SAFE metadata-prune "unique=0" "$ST_TMP/wt-f4"

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
