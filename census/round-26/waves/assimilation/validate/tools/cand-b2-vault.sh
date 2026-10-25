#!/usr/bin/env bash
# souji-vault-verify — ledger-backed moved-to-obsidian verification with
# read-only vault confirmation (round 4, seat S20 / impl-20).
#
# Supersedes tools/souji-verify.sh (r2) by adding the vault side: a ledger
# row is a receipt only when BOTH hashes re-hash to the current bytes, with
# the vault side read read-only under the vault path. The official Obsidian
# CLI, when a shim is found, is *advisory* confirmation only — never the
# receipt of record, never a substitute for hashing, and always bounded by
# `timeout`. A CLI that hangs, errors, lies, or is absent cannot produce a
# verdict on its own.
#
# CLI
#   tools/souji-vault-verify.impl-20.sh [--selftest] [--json]
#        [--stale-days N] [--ledger PATH] [--vault PATH]
#        [--fallback] [--cli] <path>...
#
# Output (default), two lines per target:
#   VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence   <- r2 form
#   VERIFIED(<receipt>) | NOT-VERIFIED(<reason>)     <- r4 vocabulary
# --json prints one JSON object per target and nothing else.
#
# Reasons (NOT-VERIFIED): source-absent, source-hash-mismatch, vault-absent,
# vault-hash-mismatch, row-incomplete, source-equals-vault, no-ledger-row,
# unreachable, secrets-refusal, unpushed, dirty, unpushed-branch, none.
# Receipts (VERIFIED): moved-to-obsidian, pushed, stale, metadata-prune.
#
# Safety rails
#   * The vault is opened read-only: sha256sum/stat/find only. Nothing is
#     ever written under a vault path, and the live ledger is never written.
#   * The desktop app launcher is NEVER executed and its absolute path is
#     never named in this file; only a shim named obsidian-cli (or a
#     registered ~/.local/bin/obsidian symlink pointing at one) is ever run,
#     under `timeout`.
#   * No git fetch/push/commit/branch/checkout/reset/rebase; fixtures live
#     under `mktemp -d` only; .ufo/state, .ufo/watchdog.log and ~/.config are
#     never touched.
#   * Secret-shaped path components (*.env, .envrc, *credential*, *secret*,
#     id_*, *.pem) are refused before anything is read.
#
# Env overrides: SOUJI_LEDGER, SOUJI_VAULT (hint), SOUJI_CLI_BIN,
# SOUJI_CLI_TIMEOUT, SHOKUNIN_ROOT, SOUJI_SELFTEST_ACTIVE.
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
VAULT_HINT="${SOUJI_VAULT:-}"

STALE_DAYS=1
JSON=0
SELFTEST=0
CLI_MODE=auto              # auto | cli (prefer) | fallback (never call)
CLI_TIMEOUT="${SOUJI_CLI_TIMEOUT:-6}"
TARGETS=()

R_VERDICT=NOT-SAFE
R_RECEIPT=none
R_REASON=none
R_EVIDENCE=no-receipt
NOTES=()
FAIL_REASON=none

declare -A WT_MAP=()
LEDGER_ROWS=()
LEDGER_PIN=""
LEDGER_CONTROL=0

usage() {
  sed -n '2,52p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}
usage_err() { printf 'souji-vault-verify: %s\n' "$1" >&2; usage 2; }

canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }
real_path() { readlink -f -- "$1" 2>/dev/null || true; }

json_escape() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}; s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

# One field, no tabs/newlines (evidence must stay column-safe).
# Escape control bytes in an emitted field: a raw TAB/NL/CR in a path would
# shift every later field of the TAB-delimited record.
san() {
  local s=${1:-} out="" i c code
  for ((i = 0; i < ${#s}; i++)); do
    c=${s:i:1}
    case "$c" in
      $'\t') out="$out\\t"; continue ;;
      $'\n') out="$out\\n"; continue ;;
      $'\r') out="$out\\r"; continue ;;
      '\') out="$out\\\\"; continue ;;
    esac
    case "$c" in
      [[:cntrl:]])
        code=$(printf '%d' "'$c" 2>/dev/null || printf '63')
        out="$out$(printf '\\x%02x' "$code")" ;;
      *) out="$out$c" ;;
    esac
  done
  printf '%s' "$out"
}

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

# r10 cluster B (B2): a control byte in a path shifts the fields of the
# TAB-delimited record this tool prints. Refuse, never echo ambiguously.
is_control_shaped() {
  local p=${1:-}
  [[ "$p" != *[[:cntrl:]]* ]]
}

# r10 cluster B (B1): a vault path inside a quarantine staging tree is
# destroyed by the very removal it authorizes.
is_quarantine_path() {
  case "/${1#/}/" in
    */.ufo-quarantine/*) return 0 ;;
  esac
  return 1
}

# A ledger carrying control bytes is not a readable receipt source: `read`
# erases NUL, so `victim\0.md<TAB>...` would match `victim.md`.
ledger_control_clean() {
  [ -f "$LEDGER" ] || return 0
  if LC_ALL=C tr -d '\11\12\15' < "$LEDGER" 2>/dev/null | LC_ALL=C grep -q '[[:cntrl:]]'; then
    return 1
  fi
  return 0
}

file_sha() { [ -f "$1" ] || return 1; sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

dir_digest() {
  local d=$1
  [ -d "$d" ] || return 1
  # r5 fix: any symlink in the digest scope fails closed (return 2);
  # silently dropping -type l entries produced a false-SAFE
  # moved-to-obsidian class (r5 verification finding).
  if ( cd "$d" && find . -path './.git' -prune -o -type l -print -quit 2>/dev/null | grep -q . ); then
    return 2
  fi
  ( cd "$d" && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null
}

# Lowercase-only: an uppercase hex row is a row we cannot vouch for (a
# case-insensitive compare would credit a row that does not match byte-wise).
is_hex64() {
  case "$1" in
    ""|*[!0-9a-f]*) return 1 ;;
  esac
  [ "${#1}" = 64 ]
}

# ------------------------------------------------------------------- ledger --
load_ledger() {
  local line first=1
  LEDGER_ROWS=()
  LEDGER_PIN=""
  [ -f "$LEDGER" ] || return 0
  if ! ledger_control_clean; then LEDGER_CONTROL=1; return 0; fi
  LEDGER_CONTROL=0
  LEDGER_PIN=$(file_sha "$LEDGER") || { LEDGER_PIN=""; return 0; }
  while IFS= read -r line || [ -n "$line" ]; do
    if [ "$first" = 1 ]; then
      first=0
      case "$line" in source_path$'\t'*) continue ;; esac
    fi
    [ -n "$line" ] && LEDGER_ROWS+=("$line")
  done < "$LEDGER"
  return 0
}

# ---------------------------------------------------------------------- CLI --
CLI_BIN=""
CLI_LOOKED=0

cli_resolve() {
  [ "$CLI_LOOKED" = 1 ] && { printf '%s' "$CLI_BIN"; return 0; }
  CLI_LOOKED=1
  local cand
  if [ -n "${SOUJI_CLI_BIN:-}" ] && [ -x "${SOUJI_CLI_BIN}" ]; then
    CLI_BIN="${SOUJI_CLI_BIN}"; printf '%s' "$CLI_BIN"; return 0
  fi
  # Registered shim location: <home>/.local/bin/obsidian -> <app>/obsidian-cli.
  # Accepted only when it is a symlink whose target basename is obsidian-cli,
  # so the desktop launcher can never be picked up by this branch.
  cand="$HOME/.local/bin/obsidian"
  if [ -L "$cand" ]; then
    case "$(basename -- "$(readlink -- "$cand" 2>/dev/null || true)")" in
      obsidian-cli) CLI_BIN="$cand" ;;
    esac
  fi
  if [ -z "$CLI_BIN" ]; then
    cand="$(command -v obsidian-cli 2>/dev/null || true)"
    case "$cand" in /*) [ -x "$cand" ] && CLI_BIN="$cand" ;; esac
  fi
  printf '%s' "$CLI_BIN"
  return 0
}

cli_label() {
  if [ -n "$(cli_resolve)" ]; then printf 'available'; else printf 'unavailable'; fi
}

# Advisory only. stdout: "<state>" or "<state>\n<claimed-hash>".
# States: unavailable, unbounded-skip, timeout, error(rc=N), empty,
#         unparseable, answer.
cli_claim() { # $1 vault path
  local vp=$1 bin out rc claim=""
  bin=$(cli_resolve)
  [ -n "$bin" ] || { printf 'unavailable'; return 0; }
  command -v timeout >/dev/null 2>&1 || { printf 'unbounded-skip'; return 0; }
  set +e
  out=$(timeout "$CLI_TIMEOUT" "$bin" vault:hash "$vp" 2>/dev/null)
  rc=$?
  set -e
  if [ "$rc" = 124 ] || [ "$rc" = 137 ]; then printf 'timeout'; return 0; fi
  if [ "$rc" -ne 0 ]; then printf 'error(rc=%s)' "$rc"; return 0; fi
  [ -n "$out" ] || { printf 'empty'; return 0; }
  claim=$(printf '%s\n' "$out" | sed -n 's/.*"sha256"[[:space:]]*:[[:space:]]*"\([0-9a-fA-F]\{64\}\)".*/\1/p' | head -1)
  if [ -z "$claim" ]; then
    claim=$(printf '%s\n' "$out" | awk '$1=="sha256" && NF>=3 {print $NF}' | head -1)
  fi
  if [ -z "$claim" ]; then
    claim=$(printf '%s\n' "$out" | grep -oE '[0-9a-fA-F]{64}' | head -1 || true)
  fi
  [ -n "$claim" ] || { printf 'unparseable'; return 0; }
  printf 'answer\n%s' "$claim"
  return 0
}

# ---------------------------------------------------------------- receipts ---
finish_mismatch() { # $1 reason, rest = notes already pushed
  R_VERDICT=NOT-SAFE; R_RECEIPT=none; R_REASON="$1"
  local joined=""
  if [ "${#NOTES[@]}" -gt 0 ]; then
    joined=$(printf '%s; ' "${NOTES[@]}"); joined=${joined%; }
  fi
  R_EVIDENCE="${joined:-no-receipt}"
  return 0
}

# Ledger receipt. Returns 0 when a row matched the target path (verdict then
# final, verified or not); 1 when no row matched.
try_ledger() { # $1 target (canonical), $2 isdir 0/1, $3 raw arg
  local target=$1 isdir=$2 raw=${3:-}
  local row sp ss vp vs rest reason="" matched=0
  local actual="" lv="" lv2="" cli_note="" claim state tgt_real vp_real
  # r10 cluster B (B1): a ledger carrying control bytes is not a readable
  # receipt source (`read` erases NUL, splicing rows onto other paths).
  if [ "$LEDGER_CONTROL" = 1 ]; then
    NOTES+=("ledger-control-bytes: ledger contains control characters")
    finish_mismatch ledger-control-bytes
    return 0
  fi
  tgt_real=$(real_path "$target")
  for row in "${LEDGER_ROWS[@]:-}"; do
    [ -n "$row" ] || continue
    case "$row" in '#'*) continue ;; esac
    IFS=$'\t' read -r sp ss vp vs rest <<< "$row"
    [ -n "$sp" ] || continue
    if [ "$sp" != "$target" ] && [ "$sp" != "$raw" ]; then continue; fi
    matched=1

    case "$sp" in
      /*) : ;;
      *)
        # A relative source row resolves against whatever cwd the tool runs
        # in, so the same row would verify from one directory and not another.
        # Receipts must be cwd-independent: refuse it.
        NOTES+=("row-incomplete relative-source-path source=$sp")
        reason="${reason:-row-incomplete}"; continue ;;
    esac
    case "$vp" in
      /*) : ;;
      *)
        NOTES+=("row-incomplete relative-vault-path vault=$vp")
        reason="${reason:-row-incomplete}"; continue ;;
    esac
    vp_real=$(real_path "$vp")
    if [ -n "$tgt_real" ] && [ "$vp_real" = "$tgt_real" ]; then
      NOTES+=("source-equals-vault: the row points the artifact at itself vault=$vp")
      reason="${reason:-source-equals-vault}"; continue
    fi
    # The vault copy must survive the removal it authorizes. A copy living
    # inside the artifact (or inside its directory) is destroyed with it.
    if [ "$isdir" = 1 ]; then
      case "$vp_real" in
        "$tgt_real"/*)
          NOTES+=("vault-inside-source: vault copy is inside the artifact being removed vault=$vp")
          reason="${reason:-vault-inside-source}"; continue ;;
      esac
    fi
    # r10 cluster B (B1): a vault path under a quarantine staging tree is
    # deleted by the same stage-5 rm that removes the staged copy.
    if is_quarantine_path "$vp_real" || is_quarantine_path "$vp"; then
      NOTES+=("vault-in-quarantine: vault copy lives in a quarantine staging tree vault=$vp")
      reason="${reason:-vault-in-quarantine}"; continue
    fi

    if [ "$isdir" = 1 ]; then
      if [ ! -d "$target" ]; then
        NOTES+=("obsidian=source-absent source-absent target=$target")
        reason="${reason:-source-absent}"; continue
      fi
      if ! is_hex64 "$ss"; then
        NOTES+=("row-incomplete missing-or-nonhex source-sha256 col2")
        reason="${reason:-row-incomplete}"; continue
      fi
      actual=$(dir_digest "$target"); _drc=$?
      if [ "$_drc" = 2 ]; then
        NOTES+=("obsidian=symlink-present symlink-present scope=source"); reason="${reason:-symlink-present}"; continue
      fi
      if [ "$actual" != "$ss" ]; then
        NOTES+=("obsidian=source-sha-mismatch source-sha-mismatch source-hash-mismatch ledger-sha=${ss:0:12} actual=${actual:0:12}")
        reason="${reason:-source-hash-mismatch}"; continue
      fi
      if [ ! -d "$vp" ]; then
        NOTES+=("obsidian=vault-unreachable vault-unreachable vault-absent vault=$vp")
        reason="${reason:-vault-absent}"; continue
      fi
      if ! is_hex64 "$vs"; then
        NOTES+=("row-incomplete missing-or-nonhex vault-sha256 col4")
        reason="${reason:-row-incomplete}"; continue
      fi
      lv=$(dir_digest "$vp"); _drc=$?
      if [ "$_drc" = 2 ]; then
        NOTES+=("obsidian=symlink-present symlink-present scope=vault vault=$vp"); reason="${reason:-symlink-present}"; continue
      fi
      if [ "$lv" != "$vs" ]; then
        NOTES+=("obsidian=vault-sha-mismatch vault-sha-mismatch vault-hash-mismatch vault=$vp ledger-sha=${vs:0:12} actual=${lv:0:12}")
        reason="${reason:-vault-hash-mismatch}"; continue
      fi
      if [ -z "$LEDGER_PIN" ] || [ "$(file_sha "$LEDGER" || true)" != "$LEDGER_PIN" ]; then
        NOTES+=("ledger-changed"); reason="${reason:-ledger-changed}"; continue
      fi
      R_VERDICT=SAFE; R_RECEIPT=moved-to-obsidian; R_REASON=moved-to-obsidian
      R_EVIDENCE="ledger-row ledger=$(real_path "$LEDGER") vault=$vp source-digest=${ss:0:12} vault-digest=${lv:0:12} cli=$(cli_label)"
      return 0
    fi

    if [ ! -f "$target" ]; then
      NOTES+=("obsidian=source-absent source-absent target=$target")
      reason="${reason:-source-absent}"; continue
    fi
    if ! is_hex64 "$ss"; then
      NOTES+=("row-incomplete missing-or-nonhex source-sha256 col2")
      reason="${reason:-row-incomplete}"; continue
    fi
    actual=$(file_sha "$target" || true)
    if [ "$actual" != "$ss" ]; then
      NOTES+=("obsidian=source-sha-mismatch source-sha-mismatch source-hash-mismatch ledger-sha=${ss:0:12} actual=${actual:0:12}")
      reason="${reason:-source-hash-mismatch}"; continue
    fi
    if [ ! -f "$vp" ]; then
      NOTES+=("obsidian=vault-unreachable vault-unreachable vault-absent vault=$vp")
      reason="${reason:-vault-absent}"; continue
    fi
    if ! is_hex64 "$vs"; then
      NOTES+=("row-incomplete missing-or-nonhex vault-sha256 col4")
      reason="${reason:-row-incomplete}"; continue
    fi
    lv=$(file_sha "$vp" || true)
    if [ "$lv" != "$vs" ]; then
      NOTES+=("obsidian=vault-sha-mismatch vault-sha-mismatch vault-hash-mismatch vault=$vp ledger-sha=${vs:0:12} actual=${lv:0:12}")
      reason="${reason:-vault-hash-mismatch}"; continue
    fi

    # Four conjuncts hold. The CLI is advisory; it can only annotate.
    if [ "$CLI_MODE" = fallback ]; then
      cli_note="cli=skipped(fallback)"
    else
      claim=$(cli_claim "$vp")
      state=${claim%%$'\n'*}
      claim=${claim#*$'\n'}
      case "$state" in
        answer)
          if [ "$claim" = "$lv" ]; then
            cli_note="cli=agree"
          else
            cli_note="cli=disagreement(claimed=${claim:0:12})"
            NOTES+=("cli-disagreement claimed=${claim:0:12} actual=${lv:0:12}")
          fi ;;
        *) cli_note="cli=$state" ;;
      esac
      # The vault must still hash to the row after the advisory read: a file
      # mutated underneath the check is not preservation evidence.
      lv2=$(file_sha "$vp" || true)
      if [ "$lv2" != "$lv" ]; then
        NOTES+=("vault-changed-during-check before=${lv:0:12} after=${lv2:0:12}")
        reason="${reason:-vault-hash-mismatch}"; continue
      fi
    fi
    if [ -z "$LEDGER_PIN" ] || [ "$(file_sha "$LEDGER" || true)" != "$LEDGER_PIN" ]; then
      NOTES+=("ledger-changed"); reason="${reason:-ledger-changed}"; continue
    fi
    R_VERDICT=SAFE; R_RECEIPT=moved-to-obsidian; R_REASON=moved-to-obsidian
    R_EVIDENCE="ledger-row ledger=$(real_path "$LEDGER") vault=$vp source-sha256=${ss:0:12} $cli_note"
    return 0
  done

  [ "$matched" = 1 ] || return 1
  finish_mismatch "${reason:-row-incomplete}"
  return 0
}

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

try_pushed() {
  local target=$1 repo=$2 intro ref
  [ -n "$repo" ] || { NOTES+=("pushed=no-repo"); return 1; }
  intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$target" 2>/dev/null | head -1 || true)
  if [ -z "$intro" ]; then NOTES+=("pushed=no-introducing-commit"); return 1; fi
  if ! ref=$(resolve_default_ref "$repo"); then
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
    R_VERDICT=SAFE; R_RECEIPT=pushed; R_REASON=pushed
    R_EVIDENCE="intro=${intro:0:12} ref=$ref ancestor=yes"
    return 0
  fi
  NOTES+=("pushed=not-ancestor intro=${intro:0:12} ref=$ref")
  return 1
}

scratch_type() {
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

count_live_refs() {
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

try_stale() {
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
  if [ "${refs:-1}" != 0 ]; then NOTES+=("stale=live-refs=$refs"); return 1; fi
  R_VERDICT=SAFE; R_RECEIPT=stale; R_REASON=stale
  R_EVIDENCE="scratch-type=$kind refs=0 mtime-age-days=$(( age / 86400 ))"
  return 0
}

# ---------------------------------------------------------------- kinds ------
evaluate_repo_root() {
  local target=$1 unpushed dirty
  if try_ledger "$target" 1 "$target"; then return 0; fi
  unpushed=$(git -C "$target" log --branches --not --remotes --oneline 2>/dev/null | wc -l || true)
  dirty=$(git -C "$target" status --porcelain 2>/dev/null | wc -l || true)
  unpushed=${unpushed// /}; dirty=${dirty// /}
  R_VERDICT=NOT-SAFE
  if [ "${unpushed:-0}" -gt 0 ]; then R_RECEIPT=unpushed; R_REASON=unpushed
  elif [ "${dirty:-0}" -gt 0 ]; then R_RECEIPT=dirty; R_REASON=dirty
  else R_RECEIPT=none; R_REASON=none
  fi
  R_EVIDENCE="unpushed=${unpushed:-0} dirty=${dirty:-0}"
  return 0
}

evaluate_worktree() {
  local target=$1 meta=$2 owner head branch unp uniq dirty st present
  IFS=$'\t' read -r owner head branch <<< "$meta"
  if [ -d "$target" ]; then present=present; else present=absent; fi
  if [ -n "$branch" ]; then
    if ! unp=$(git -C "$owner" log --oneline "$branch" --not --remotes 2>/dev/null | wc -l); then
      R_VERDICT=NOT-SAFE; R_RECEIPT=git-unverifiable; R_REASON=git-unverifiable
      R_EVIDENCE="worktree commit query failed"
      return 0
    fi
    unp=${unp// /}
    if [ "${unp:-0}" -gt 0 ]; then
      R_VERDICT=NOT-SAFE; R_RECEIPT=unpushed-branch; R_REASON=unpushed-branch
      R_EVIDENCE="branch=${branch#refs/heads/} unpushed=$unp dir=$present owner=$(basename -- "$owner")"
      return 0
    fi
  fi
  if [ "$present" = absent ]; then
    if ! uniq=$(git -C "$owner" log --oneline "$head" --not --all 2>/dev/null | wc -l); then
      R_VERDICT=NOT-SAFE; R_RECEIPT=git-unverifiable; R_REASON=git-unverifiable
      R_EVIDENCE="worktree commit query failed"
      return 0
    fi
    uniq=${uniq// /}
    if [ "${uniq:-1}" = 0 ]; then
      R_VERDICT=SAFE; R_RECEIPT=metadata-prune; R_REASON=metadata-prune
      R_EVIDENCE="dir=absent unique=0 head=${head:0:12} owner=$(basename -- "$owner")"
      return 0
    fi
    R_VERDICT=NOT-SAFE; R_RECEIPT=none; R_REASON=none
    R_EVIDENCE="dir=absent unique=$uniq head=${head:0:12} owner=$(basename -- "$owner")"
    return 0
  fi
  if st=$(git -C "$target" status --porcelain 2>/dev/null); then
    dirty=$(printf '%s\n' "$st" | grep -c . || true)
    dirty=${dirty// /}
    if [ "${dirty:-0}" -gt 0 ]; then
      R_VERDICT=NOT-SAFE; R_RECEIPT=dirty; R_REASON=dirty
      R_EVIDENCE="dir=present dirty=$dirty owner=$(basename -- "$owner")"
    else
      R_VERDICT=NOT-SAFE; R_RECEIPT=none; R_REASON=none
      R_EVIDENCE="dir=present clean head=${head:0:12} owner=$(basename -- "$owner")"
    fi
  else
    R_VERDICT=NOT-SAFE; R_RECEIPT=dirty; R_REASON=dirty
    R_EVIDENCE="dir=present status-unverifiable owner=$(basename -- "$owner")"
  fi
  return 0
}

evaluate_artifact() {
  local target=$1 repo="" isdir=0
  [ -d "$target" ] && isdir=1
  repo=$(find_repo_for "$target") || repo=""
  if try_pushed "$target" "$repo"; then
    R_EVIDENCE="$R_EVIDENCE cli=$(cli_label)"
    return 0
  fi
  if try_stale "$target" "$repo"; then
    R_EVIDENCE="$R_EVIDENCE cli=$(cli_label)"
    return 0
  fi
  R_VERDICT=NOT-SAFE
  R_RECEIPT=none
  R_REASON=none
  local joined=""
  if [ "${#NOTES[@]}" -gt 0 ]; then
    joined=$(printf '%s; ' "${NOTES[@]}"); joined=${joined%; }
  fi
  R_EVIDENCE="${joined:-no-receipt} cli=$(cli_label)"
  return 0
}

evaluate_path() {
  local raw=$1 target isdir=0
  R_VERDICT=NOT-SAFE; R_RECEIPT=none; R_REASON=none; R_EVIDENCE=no-receipt
  NOTES=(); FAIL_REASON=none
  if [ -z "$raw" ]; then
    R_REASON=unreachable; R_RECEIPT=unreachable; R_EVIDENCE="empty-arg"; return 0
  fi
  target=$(canon_path "$raw")
  if is_secret_shaped "$target"; then
    R_REASON=secrets-refusal; R_RECEIPT=secrets-refusal
    R_EVIDENCE="secret-shaped path component basename=$(basename -- "$target")"
    return 0
  fi
  # r10 cluster B (B2): control bytes make the TAB-delimited record ambiguous.
  if ! is_control_shaped "$target"; then
    R_REASON=control-character-refusal; R_RECEIPT=control-character-refusal
    R_EVIDENCE="path contains a control character and cannot be recorded unambiguously"
    return 0
  fi
  if [ -d "$target" ]; then
    local nested_git
    if ! nested_git=$(cd -- "$target" && find . -path './.git' -prune -o \( -name .git -o -name .ufo \) -print -quit 2>/dev/null) || [ -n "$nested_git" ]; then
      R_RECEIPT=nested-repo-or-unverifiable; R_REASON=nested-repo-or-unverifiable
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
  # Ledger first: it must be able to answer for a source that is already gone
  # (V5 source-absent), which no mtime/hash check could.
  [ -d "$target" ] && isdir=1
  if try_ledger "$target" "$isdir" "$raw"; then return 0; fi
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    R_REASON=unreachable; R_RECEIPT=unreachable; R_EVIDENCE="missing path"; return 0
  fi
  if [ ! -f "$target" ] && [ ! -d "$target" ]; then
    R_REASON=unreachable; R_RECEIPT=unreachable
    R_EVIDENCE="not a regular file or directory"; return 0
  fi
  evaluate_artifact "$target"
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

emit_result() {
  local raw=$1 r4
  if [ "$R_VERDICT" = SAFE ]; then r4="VERIFIED($R_RECEIPT)"; else r4="NOT-VERIFIED($R_REASON)"; fi
  if [ "$JSON" = 1 ]; then
    printf '{"path":"%s","verdict":"%s","verified":"%s","receipt":"%s","reason":"%s","evidence":"%s"}\n' \
      "$(json_escape "$raw")" "$R_VERDICT" "$(json_escape "$r4")" \
      "$(json_escape "$R_RECEIPT")" "$(json_escape "$R_REASON")" \
      "$(json_escape "$(san "$R_EVIDENCE")")"
  else
    # Line 1 is the tab-delimited record (field 3 = verdict, field 4 = receipt):
    # consumers that read NR==1 with awk -F'\t' (vadv-56, runner-30) need it
    # first, and consumers that grep for '^VERDICT' / '^VERIFIED' find it too.
    # A newline in a path would split one record across two lines and let a
    # line-oriented consumer mis-attribute verdicts. Escape it in the record.
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$(san "$raw")" "$R_VERDICT" "$R_RECEIPT" "$(san "$R_EVIDENCE")"
    printf '%s\n' "$r4"
  fi
  return 0
}

# ---------------------------------------------------------------- selftest --
ST_FLEET="" ST_TMP="" ST_LEDGER="" ST_VAULT="" ST_CLI=""
ST_PASS=0 ST_FAIL=0

st_note() { printf '%s\n' "$*"; }

st_run() { # env overrides + args -> OUT_TEXT, OUT_CODE
  local -a envs=() args=()
  while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  [ "$#" -gt 0 ] && shift
  args=("$@")
  local rc=0
  OUT_TEXT=$(env "${envs[@]}" SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
             SOUJI_SELFTEST_ACTIVE=1 timeout 120 "$SELF" "${args[@]}" 2>&1) || rc=$?
  OUT_CODE=$rc
  return 0
}

st_case() { # id want-r4 want-receipt evidence-substr -- <args...>
  local id=$1 w4=$2 wr=$3 wsub=$4; shift 4
  [ "${1:-}" = "--" ] && shift
  st_run -- "$@"
  if [ "$OUT_CODE" -ne 0 ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: exit=$OUT_CODE out=$(printf '%s' "$OUT_TEXT" | head -c 200)"; return 0
  fi
  local first second rest v r ev
  first=$(printf '%s\n' "$OUT_TEXT" | head -1)
  second=$(printf '%s\n' "$OUT_TEXT" | sed -n '2p')
  case "$first" in
    VERDICT$'\t'*) : ;;
    *) ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: line1 is not the VERDICT record (got '$first')"; return 0 ;;
  esac
  rest=${first#VERDICT$'\t'}; rest=${rest#*$'\t'}
  v=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  r=${rest%%$'\t'*}; ev=${rest#*$'\t'}
  if [ "$second" != "$w4" ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: r4='$second' want='$w4'"; return 0
  fi
  if [ "$v" != "$([ "${w4%%(*}" = VERIFIED ] && printf SAFE || printf NOT-SAFE)" ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: verdict=$v for '$w4'"; return 0
  fi
  if [ -n "$wr" ] && [ "$r" != "$wr" ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: receipt='$r' want='$wr'"; return 0
  fi
  if [ -n "$wsub" ]; then
    case "$ev" in
      *"$wsub"*) : ;;
      *) ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: evidence '$ev' lacks '$wsub'"; return 0 ;;
    esac
  fi
  ST_PASS=$((ST_PASS+1)); st_note "PASS $id $w4"
  return 0
}

st_status() { # id want-exit -- args
  local id=$1 want=$2; shift 2
  [ "${1:-}" = "--" ] && shift
  st_run -- "$@"
  if [ "$OUT_CODE" = "$want" ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS $id exit=$OUT_CODE"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id exit=$OUT_CODE want=$want"
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
  git init -q --initial-branch="$b" "$p"
  git -C "$p" symbolic-ref HEAD "refs/heads/$b"
}

st_register_worktree() {
  local owner=$1 name=$2 wt=$3 sha=$4 br=$5 adm
  adm="$owner/.git/worktrees/$name"
  mkdir -p "$adm"
  if [ -n "$br" ]; then printf 'ref: %s\n' "$br" > "$adm/HEAD"; else printf '%s\n' "$sha" > "$adm/HEAD"; fi
  printf '../..\n' > "$adm/commondir"
  printf '%s\n' "$wt/.git" > "$adm/gitdir"
  if [ -d "$wt" ]; then printf 'gitdir: %s\n' "$adm" > "$wt/.git"; fi
  return 0
}

st_ledger() { # overwrite the test ledger with header + rows from stdin
  { printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'; cat; } > "$ST_LEDGER"
}

st_build_fixtures() {
  ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-vault-verify-selftest.XXXXXX")
  ST_FLEET="$ST_TMP/fleet"
  ST_LEDGER="$ST_TMP/ledger.tsv"
  ST_VAULT="$ST_TMP/vault"
  ST_CLI="$ST_TMP/bin"
  mkdir -p "$ST_FLEET" "$ST_VAULT" "$ST_CLI"

  # --- repo-shokunin: file artifacts + worktree registrations -------------
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
  printf 'f2 payload\n' > "$R/local/f2.txt"
  local c3; c3=$(st_commit "$R" "$c2" "c3 local-only adds local/f2.txt")
  git -C "$R" update-ref refs/heads/master "$c3"
  printf 'self mention old-f7.out\n' > "$R/.scratch/old-f7.out"
  printf 'self mention old-f8.out\n' > "$R/.scratch/old-f8.out"
  printf '{"row":"old-f8.out"}\n' > "$R/souji-shokunin/census/ref-census.json"
  printf 'x\n' > "$R/x.env"
  git -C "$R" update-ref refs/heads/wt-unpushed "$c3"
  st_register_worktree "$R" wt-f4 "$ST_TMP/wt-f4" "$c2" ""
  st_register_worktree "$R" wt-f5 "$ST_TMP/wt-f5" "$c3" "refs/heads/wt-unpushed"

  # --- repo9-shokunin: default-ref fallback (single origin ref) -----------
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
  local k2; k2=$(st_commit "$RK" "$k1" "k2 local work")
  git -C "$RK" update-ref refs/heads/main "$k2"
  printf 'dirt\n' >> "$RK/tracked.txt"

  # --- vault pairs for the ledger cases ---------------------------------
  mkdir -p "$ST_TMP/pairs"
  local P="$ST_TMP/pairs"
  printf 'v-a payload\n' > "$P/a-src.md"; cp "$P/a-src.md" "$P/a-vlt.md"
  printf 'v-b payload\n' > "$P/b-src.md"; cp "$P/b-src.md" "$P/b-vlt.md"
  printf 'v-c payload\n' > "$P/c-src.md"; cp "$P/c-src.md" "$P/c-vlt.md"
  printf 'v-d payload\n' > "$P/d-src.md"
  printf 'v-i payload\n' > "$P/i-same.md"
  printf 'v-e payload\n' > "$P/e-src.md"; cp "$P/e-src.md" "$P/e-vlt.md"
  printf 'v-n payload\n' > "$P/no-row.md"

  local sha; sha() { sha256sum -- "$1" | cut -d' ' -f1; }
  local SA SB SC SD SI SE
  SA=$(sha "$P/a-src.md"); SB=$(sha "$P/b-src.md"); SC=$(sha "$P/c-src.md")
  SD=$(sha "$P/d-src.md"); SI=$(sha "$P/i-same.md"); SE=$(sha "$P/e-src.md")
  printf 'EDIT AFTER ROW\n' >> "$P/b-vlt.md"
  printf 'EDIT AFTER ROW\n' >> "$P/c-src.md"

  st_ledger <<EOF
$P/a-src.md	$SA	$P/a-vlt.md	$SA	2026-10-18	selftest-match
$P/b-src.md	$SB	$P/b-vlt.md	$SB	2026-10-18	selftest-vault-edited
$P/c-src.md	$SC	$P/c-vlt.md	$SC	2026-10-18	selftest-source-edited
$P/d-src.md	$SD	$P/d-absent.md	$SD	2026-10-18	selftest-vault-absent
$P/gone-src.md	$SA	$P/a-vlt.md	$SA	2026-10-18	selftest-source-absent
$P/i-same.md	$SI	$P/i-same.md	$SI	2026-10-18	selftest-self-row
$P/e-src.md	$SE	$P/e-vlt.md		2026-10-18	selftest-row-incomplete
EOF
  # a ledger whose last row carries no trailing newline (hand-edited TSVs)
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-18\tselftest-noeol' "$P/a-src.md" "$SA" "$P/a-vlt.md" "$SA"
  } > "$ST_TMP/ledger-noeol.tsv"

  # --- dir-digest pair (E6-like) ----------------------------------------
  local RP="$ST_FLEET/preserved-repo-shokunin" VD="$ST_TMP/vault/preserved"
  st_init_repo "$RP" master
  printf 'kept\n' > "$RP/kept.txt"
  local cp1; cp1=$(st_commit "$RP" "" "p1 kept.txt")
  git -C "$RP" update-ref refs/heads/master "$cp1"
  mkdir -p "$VD"; printf 'kept\n' > "$VD/kept.txt"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tselftest-dir\n' \
    "$(canon_path "$RP")" "$(dir_digest "$RP")" "$(canon_path "$VD")" "$(dir_digest "$VD")" >> "$ST_LEDGER"

  # --- mock CLI shims (honest / hanging) --------------------------------
  cat > "$ST_CLI/honest" <<'SH'
#!/usr/bin/env bash
f=${2:-}
if [ -f "$f" ]; then h=$(sha256sum -- "$f" | cut -d' ' -f1); else h=""; fi
printf '{"ok":true,"path":"%s","sha256":"%s"}\n' "$f" "$h"
SH
  cat > "$ST_CLI/hang" <<'SH'
#!/usr/bin/env bash
sleep 30
SH
  chmod +x "$ST_CLI/honest" "$ST_CLI/hang"

  touch -d '3 days ago' "$R/.scratch/old-f7.out" "$R/.scratch/old-f8.out"
  return 0
}

st_audit_source() {
  local n
  n=$(grep -nE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase)( |$)' "$SELF" | wc -l || true)
  n=${n// /}
  if [ "${n:-1}" = 0 ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS H1 no forbidden git subcommand"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H1 $n forbidden git invocation(s)"
  fi
  # pattern spelled with a class so this audit line does not match itself
  n=$(grep -c '/usr/bin/obsidi[a]n' "$SELF" || true)
  n=${n// /}
  if [ "${n:-1}" = 0 ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS H2 no GUI-launcher path literal"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H2 GUI-launcher path named $n time(s)"
  fi
  case "$ST_FLEET" in
    "$ST_TMP"/*) ST_PASS=$((ST_PASS+1)); st_note "PASS H3 fixtures under mktemp -d ($ST_TMP)" ;;
    *) ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H3 fixtures not under mktemp" ;;
  esac
  return 0
}

run_selftest() {
  if [ "${SOUJI_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'souji-vault-verify: refusing nested --selftest\n' >&2
    exit 1
  fi
  st_build_fixtures
  trap 'rm -rf -- "$ST_TMP"' EXIT
  local R="$ST_FLEET/repo-shokunin" P="$ST_TMP/pairs"
  local sha; sha() { sha256sum -- "$1" | cut -d' ' -f1; }

  st_case F1 "VERIFIED(pushed)" pushed refs/remotes/origin/master -- "$R/keep/f1.txt"
  st_case F2 "NOT-VERIFIED(none)" none "" -- "$R/local/f2.txt"
  st_case F3 "NOT-VERIFIED(unpushed)" unpushed "unpushed=1 dirty=1" -- "$ST_FLEET/kotodama-shaped-shokunin"
  st_case F4 "VERIFIED(metadata-prune)" metadata-prune "unique=0" -- "$ST_TMP/wt-f4"
  st_case F5 "NOT-VERIFIED(unpushed-branch)" unpushed-branch "unpushed=1" -- "$ST_TMP/wt-f5"
  st_case F7 "VERIFIED(stale)" stale "refs=0" -- "$R/.scratch/old-f7.out"
  st_case F8 "VERIFIED(stale)" stale "refs=0" -- "$R/.scratch/old-f8.out"
  st_case F9 "VERIFIED(pushed)" pushed refs/remotes/origin/master -- "$ST_FLEET/repo9-shokunin/f9.txt"
  st_case F10 "NOT-VERIFIED(secrets-refusal)" secrets-refusal "secret-shaped" -- "$R/x.env"

  # --- vault cases -------------------------------------------------------
  st_case V1 "VERIFIED(moved-to-obsidian)" moved-to-obsidian "ledger-row ledger=" -- "$P/a-src.md"
  st_case V2 "NOT-VERIFIED(vault-hash-mismatch)" none "vault-sha-mismatch" -- "$P/b-src.md"
  st_case V3 "NOT-VERIFIED(source-hash-mismatch)" none "source-sha-mismatch" -- "$P/c-src.md"
  st_case V4 "NOT-VERIFIED(vault-absent)" none "vault-unreachable" -- "$P/d-src.md"
  st_case V5 "NOT-VERIFIED(source-absent)" none "source-absent" -- "$P/gone-src.md"
  st_case V6 "NOT-VERIFIED(none)" none "" -- "$P/no-row.md"
  st_case V9 "NOT-VERIFIED(source-equals-vault)" none "source-equals-vault" -- "$P/i-same.md"
  st_case V12 "VERIFIED(moved-to-obsidian)" moved-to-obsidian "vault=" -- "$ST_FLEET/preserved-repo-shokunin"
  st_case V20 "NOT-VERIFIED(row-incomplete)" none "row-incomplete" -- "$P/e-src.md"

  # V10 with the honest CLI in place; V11 with the hanging CLI (bounded).
  st_run SOUJI_CLI_BIN="$ST_CLI/honest" -- "$P/a-src.md"
  if printf '%s' "$OUT_TEXT" | grep -q '^VERIFIED(moved-to-obsidian)' \
     && printf '%s' "$OUT_TEXT" | grep -q 'cli=agree'; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS V10b honest CLI agrees -> VERIFIED(moved-to-obsidian)"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL V10b $(printf '%s' "$OUT_TEXT" | head -2 | tr '\n' ' ')"
  fi
  local t0 t1 secs
  t0=$(date +%s)
  st_run SOUJI_CLI_BIN="$ST_CLI/hang" SOUJI_CLI_TIMEOUT=2 -- "$P/a-src.md"
  t1=$(date +%s); secs=$(( t1 - t0 ))
  if printf '%s' "$OUT_TEXT" | grep -q 'cli=timeout' && [ "$secs" -lt 20 ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS V11b hanging CLI bounded (${secs}s) -> cli=timeout, verdict kept"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL V11b hanging CLI: secs=$secs out=$(printf '%s' "$OUT_TEXT" | head -2 | tr '\n' ' ')"
  fi
  # V13 lying CLI: it claims a hash the vault file does not have.
  cat > "$ST_CLI/liar" <<'SH'
#!/usr/bin/env bash
printf '{"ok":true,"path":"%s","sha256":"%s"}\n' "${2:-}" \
  "0000000000000000000000000000000000000000000000000000000000000000"
SH
  chmod +x "$ST_CLI/liar"
  st_run SOUJI_CLI_BIN="$ST_CLI/liar" -- "$P/a-src.md"
  if printf '%s' "$OUT_TEXT" | grep -q '^VERIFIED(moved-to-obsidian)' \
     && printf '%s' "$OUT_TEXT" | grep -q 'cli=disagreement'; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS V13 lying CLI annotated, ledger still the receipt"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL V13 $(printf '%s' "$OUT_TEXT" | head -2 | tr '\n' ' ')"
  fi
  # V14 --fallback never calls the CLI at all.
  st_run SOUJI_CLI_BIN="$ST_CLI/liar" -- --fallback "$P/a-src.md"
  if printf '%s' "$OUT_TEXT" | grep -q 'cli=skipped(fallback)'; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS V14 --fallback skips the CLI"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL V14 $(printf '%s' "$OUT_TEXT" | head -2 | tr '\n' ' ')"
  fi
  # V15 header-only ledger: the row is the receipt, so nothing verifies.
  local keep="$ST_TMP/ledger.keep"; cp "$ST_LEDGER" "$keep"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$ST_LEDGER"
  st_case V15 "NOT-VERIFIED(none)" none "" -- "$P/a-src.md"
  cp "$keep" "$ST_LEDGER"
  # V16 --json parses and carries the r4 vocabulary.
  st_run -- --json "$P/a-src.md"
  if printf '%s' "$OUT_TEXT" | python3 -c 'import json,sys; d=json.loads(sys.stdin.read()); sys.exit(0 if d["verified"]=="VERIFIED(moved-to-obsidian)" else 1)' 2>/dev/null; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS V16 --json object with r4 vocabulary"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL V16 json: $(printf '%s' "$OUT_TEXT" | head -c 200)"
  fi
  # V17 uppercase-hex row must not be credited (is_hex64 is lowercase-only).
  local UP; UP=$(printf '%s' "$(sha "$P/a-src.md")" | tr 'a-f' 'A-F')
  local keep2="$ST_TMP/ledger.keep2"; cp "$ST_LEDGER" "$keep2"
  st_ledger <<EOF
$P/a-src.md	$UP	$P/a-vlt.md	$UP	2026-10-18	selftest-upper-only
EOF
  st_case V17 "NOT-VERIFIED(row-incomplete)" none "" -- "$P/a-src.md"
  cp "$keep2" "$ST_LEDGER"
  # V18 relative vault path row must not be credited.
  st_ledger <<EOF
$P/a-src.md	$(sha "$P/a-src.md")	rel/a-vlt.md	$(sha "$P/a-src.md")	2026-10-18	selftest-relative-only
EOF
  st_case V18 "NOT-VERIFIED(row-incomplete)" none "" -- "$P/a-src.md"
  cp "$keep2" "$ST_LEDGER"
  # V19 --ledger flag overrides the env ledger.
  st_run -- --ledger "$ST_LEDGER" "$P/a-src.md"
  if printf '%s' "$OUT_TEXT" | grep -q '^VERIFIED(moved-to-obsidian)'; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS V19 --ledger flag accepted"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL V19 $(printf '%s' "$OUT_TEXT" | head -2 | tr '\n' ' ')"
  fi
  # V21 ledger row with no trailing newline (hand-edited TSV) is still honoured.
  st_run -- --ledger "$ST_TMP/ledger-noeol.tsv" "$P/a-src.md"
  if printf '%s' "$OUT_TEXT" | grep -q '^VERIFIED(moved-to-obsidian)'; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS V21 no-trailing-newline ledger row honoured"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL V21 $(printf '%s' "$OUT_TEXT" | head -2 | tr '\n' ' ')"
  fi
  # V22 bare --cli is accepted (no shim on PATH -> cli=unavailable, never fatal).
  st_run -- --cli "$P/a-src.md"
  if [ "$OUT_CODE" = 0 ] && printf '%s' "$OUT_TEXT" | grep -q '^VERIFIED(moved-to-obsidian)'; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS V22 bare --cli accepted"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL V22 rc=$OUT_CODE $(printf '%s' "$OUT_TEXT" | head -2 | tr '\n' ' ')"
  fi
  # V23 batch: three targets, three verdict pairs, order preserved.
  st_run -- "$P/a-src.md" "$P/b-src.md" "$P/d-src.md"
  local nl
  nl=$(printf '%s\n' "$OUT_TEXT" | grep -c '^VERDICT	' || true)
  if [ "$nl" = 3 ] \
     && printf '%s' "$OUT_TEXT" | sed -n '2p' | grep -q '^VERIFIED' \
     && printf '%s' "$OUT_TEXT" | sed -n '4p' | grep -q '^NOT-VERIFIED(vault-hash-mismatch)' \
     && printf '%s' "$OUT_TEXT" | sed -n '6p' | grep -q '^NOT-VERIFIED(vault-absent)'; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS V23 batch of 3, order preserved"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL V23 nlines=$nl $(printf '%s' "$OUT_TEXT" | head -6 | tr '\n' ' ')"
  fi

  st_status H4 2 -- --bogus-flag "$R/keep/f1.txt"
  st_status H5 2 -- --stale-days abc "$R/keep/f1.txt"

  st_audit_source

  local r9_out r9_rc=0
  r9_out=$(bash "$SCRIPT_DIR/souji-round9-selftest.sh" vault "$SELF") || r9_rc=$?
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
    --fallback) CLI_MODE=fallback; shift ;;
    --cli) CLI_MODE=cli; shift ;;
    --auto) CLI_MODE=auto; shift ;;
    --stale-days) [ "$#" -ge 2 ] || usage_err "--stale-days needs a value"; STALE_DAYS=$2; shift 2 ;;
    --stale-days=*) STALE_DAYS=${1#*=}; shift ;;
    --ledger) [ "$#" -ge 2 ] || usage_err "--ledger needs a value"; LEDGER=$2; shift 2 ;;
    --ledger=*) LEDGER=${1#*=}; shift ;;
    --vault) [ "$#" -ge 2 ] || usage_err "--vault needs a value"; VAULT_HINT=$2; shift 2 ;;
    --vault=*) VAULT_HINT=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    --) shift; while [ "$#" -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    -*) usage_err "unknown flag: $1" ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done

case "$STALE_DAYS" in
  ''|*[!0-9]*) usage_err "--stale-days must be a non-negative integer" ;;
esac
case "$CLI_TIMEOUT" in
  ''|*[!0-9]*) CLI_TIMEOUT=6 ;;
esac

if [ "$SELFTEST" = 1 ]; then run_selftest; fi

if [ "${#TARGETS[@]}" -eq 0 ]; then usage_err "no targets given"; fi
command -v git >/dev/null 2>&1 || { printf 'souji-vault-verify: git not found\n' >&2; exit 1; }
command -v rg >/dev/null 2>&1 || { printf 'souji-vault-verify: rg not found\n' >&2; exit 1; }

load_ledger
scan_worktrees
for target in "${TARGETS[@]}"; do
  evaluate_path "$target"
  emit_result "$target"
done
exit 0
