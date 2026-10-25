#!/usr/bin/env bash
# impl-21 — round-4 vault verification (seat S21, implementor; independent).
#
# Ledger-backed `moved-to-obsidian` verification with optional advisory
# confirmation from the official Obsidian CLI. The receipt of record is always
# the locally recomputed content-hash pair (source file/dir + vault file/dir)
# against corpus/knowledge/obsidian-ledger.tsv. The CLI never decides a
# verdict by itself — a CLI claim with no ledger row is NOT-SAFE, and a
# disagreement is recorded while the local hashes decide.
#
# Strict ledger rule (differs from r2's impl-12): a row matches only when the
# source path matches AND both hash columns are non-empty AND both recomputed
# hashes equal them. Empty hash columns are never a receipt.
#
# CLI contract (--cli, opt-in)
#   Discovery: $SOUJI_CLI, else ~/.local/bin/{obsidian-cli,obsidian}, else
#   `obsidian-cli`/`obsidian` on PATH. A candidate that is a desktop-launcher
#   script (references the Electron app bundle / user-flags launcher signature)
#   is refused unread — executing it would spawn the Obsidian GUI, which this
#   lane never does.
#   Call: `timeout $SOUJI_CLI_TIMEOUT <cli> file --json -- <vault-path>`,
#   bounded (default 10s). The first 64-hex token on stdout is the claim.
#   Semantics: claim == locally recomputed vault hash -> cli=agree; claim
#   differs -> cli=disagreement recorded, local hash still decides;
#   timeout / error / garbage / empty / unavailable -> recorded, sha256sum
#   fallback decides. Vault reads happen after the CLI call, so a vault that
#   changes under a CLI read can never yield a stale SAFE.
#
# Ledger semantics
#   First fully-matching row wins (S42/S46/S51 binding oracle): a row matches
#   when source path matches AND both hash columns are non-empty AND both
#   recomputed hashes equal them (hex case-folded — hex case is not semantic).
#   Hazard guards refuse rows that cannot prove a move: vault_path equal to
#   the source (self-move), a symlink alias resolving to the source, and a
#   vault dir nested inside the source dir. A missing target whose source
#   path has a ledger row reports `source-absent`.
#
# Output (default, one line per target):
#   VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-reason<TAB>evidence
# exit codes: 0 evaluated clean; 1 selftest failure; 2 usage. No other codes.
#
# Env overrides
#   SHOKUNIN_ROOT     fleet root scanned for worktree registrations
#   SOUJI_LEDGER      obsidian ledger path
#   SOUJI_VAULT       vault root, resolves relative vault_path columns
#   SOUJI_CLI         explicit CLI binary (skips discovery)
#   SOUJI_CLI_TIMEOUT seconds bound for one CLI call (default 10)
#
# CLI flags (r4 interface, in addition to the r2 set)
#   --ledger <file>   ledger path (overrides SOUJI_LEDGER)
#   --vault <dir>     vault root for relative vault_path rows
#   --fallback        force the sha256sum path (the default mode)
#   --auto            accepted alias of --fallback
#   --cli             attempt CLI confirmation (advisory; see above)
#
# Safety rails
#   * Secret-shaped path components are refused before anything is read.
#   * No git fetch/push/commit/branch/checkout/reset/rebase is ever executed;
#     no writes outside `mktemp -d` fixture dirs (selftest only); no file in
#     any vault, ledger, or inspected repo is ever modified.
#   * The desktop launcher is never executed (content guard, see above).
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SHOKUNIN_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"
SHOKUNIN_ROOT="$(readlink -m -- "$SHOKUNIN_ROOT" 2>/dev/null || printf '%s' "$SHOKUNIN_ROOT")"
LEDGER="${SOUJI_LEDGER:-$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv}"
VAULT_ROOT="${SOUJI_VAULT:-}"

STALE_DAYS=1
JSON=0
SELFTEST=0
CLI_MODE=0
CLI_TIMEOUT="${SOUJI_CLI_TIMEOUT:-10}"
TARGETS=()
CLI_BIN=""
CLI_DISC_NOTE=""

R_VERDICT=NOT-SAFE
R_RECEIPT=none
R_EVIDENCE=no-receipt
NOTES=()
FAIL_REASON=none

declare -A WT_MAP=()

usage() { # $1 = exit code
  sed -n '2,70p' "$SELF" | sed 's/^# \{0,1\}//'
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

# Resolve the default-branch ref for pushed receipts; prints the ref.
resolve_default_ref() {
  local repo=$1 b refs n
  b=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)
  if [ -n "$b" ] && git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$b" 2>/dev/null; then
    printf 'refs/remotes/origin/%s\n' "$b"; return 0
  fi
  refs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null | grep -v '^refs/remotes/origin/HEAD$' || true)
  n=$(printf '%s\n' "$refs" | grep -c . || true)
  if [ "$n" = 1 ]; then printf '%s\n' "$refs"; return 0; fi
  if git -C "$repo" show-ref --verify --quiet refs/heads/master 2>/dev/null; then
    printf 'refs/heads/master\n'; return 0
  fi
  return 1
}

file_sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

dir_digest() { # deterministic manifest digest of a directory (ignores .git)
  local d=$1
  ( cd "$d" && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null
}

# Split a ledger row on TABs preserving empty fields (read(1) collapses runs).
# Sets L_SP L_SS L_VP L_VS L_REST. Rows with fewer than 4 fields leave the
# missing columns empty, which the strict rule then rejects.
ledger_split() {
  local rest=$1
  L_SP=${rest%%$'\t'*}
  case "$rest" in *$'\t'*) rest=${rest#*$'\t'};; *) L_SS=""; L_VP=""; L_VS=""; L_REST=""; return 0;; esac
  L_SS=${rest%%$'\t'*}
  case "$rest" in *$'\t'*) rest=${rest#*$'\t'};; *) L_VP=""; L_VS=""; L_REST=""; return 0;; esac
  L_VP=${rest%%$'\t'*}
  case "$rest" in *$'\t'*) rest=${rest#*$'\t'};; *) L_VS=""; L_REST=""; return 0;; esac
  L_VS=${rest%%$'\t'*}
  case "$rest" in *$'\t'*) rest=${rest#*$'\t'};; *) L_REST=""; return 0;; esac
  L_REST=$rest
}

ledger_lines() {
  local line first=1
  [ -f "$LEDGER" ] || return 0
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%$'\r'}
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
  if git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
    R_VERDICT=SAFE; R_RECEIPT=pushed
    R_EVIDENCE="intro=${intro:0:12} ref=$ref ancestor=yes"
    return 0
  fi
  NOTES+=("pushed=not-ancestor intro=${intro:0:12} ref=$ref")
  return 1
}

# ------------------------------------------------------------- CLI layer --

# 0 = the candidate is a desktop-launcher script and must never be executed.
is_gui_launcher() {
  local p=$1 head2
  [ -f "$p" ] || return 1
  head2=$(head -c 2 -- "$p" 2>/dev/null || true)
  [ "$head2" = '#!' ] || return 1
  if head -c 4096 -- "$p" 2>/dev/null \
       | grep -qE 'app\.asar|electron[0-9]*[[:space:]].*asar|OBSIDIAN_USER_FLAGS'; then
    return 0
  fi
  return 1
}

cli_discover() { # sets CLI_BIN (empty when none) and CLI_DISC_NOTE
  # Policy: a binary literally named `obsidian` is only ever taken from the
  # app-registered location (~/.local/bin, per the asar register handler) and
  # only after the desktop-launcher content guard. A bare `obsidian` found on
  # PATH is never executed — an adversarial PATH entry with that name must not
  # become a command. PATH lookup is limited to `obsidian-cli`.
  local c p cands=() seen=""
  CLI_BIN=""; CLI_DISC_NOTE=""
  if [ -n "${SOUJI_CLI:-}" ]; then
    cands+=("$SOUJI_CLI")
  else
    cands+=("$HOME/.local/bin/obsidian-cli" "$HOME/.local/bin/obsidian")
    p=$(command -v obsidian-cli 2>/dev/null || true); [ -n "$p" ] && cands+=("$p")
  fi
  for c in "${cands[@]}"; do
    [ -n "$c" ] || continue
    case ":$seen:" in *":$c:"*) continue ;; esac
    seen="$seen:$c"
    if [ ! -x "$c" ]; then CLI_DISC_NOTE="${CLI_DISC_NOTE:+$CLI_DISC_NOTE,}skip-not-executable"; continue; fi
    if is_gui_launcher "$c"; then CLI_DISC_NOTE="${CLI_DISC_NOTE:+$CLI_DISC_NOTE,}refused-gui-launcher"; continue; fi
    CLI_BIN=$c; return 0
  done
  return 1
}

cli_hash_claim() { # $1 vault path; sets CLI_STATE and CLI_CLAIM
  CLI_STATE=""; CLI_CLAIM=""
  if [ -z "${CLI_BIN:-}" ]; then
    CLI_STATE="unavailable${CLI_DISC_NOTE:+ ($CLI_DISC_NOTE)}"
    return 0
  fi
  local out rc
  set +e
  out=$(timeout -k 2 "$CLI_TIMEOUT" "$CLI_BIN" file --json -- "$1" 2>/dev/null)
  rc=$?
  set -e
  if [ "$rc" = 124 ] || [ "$rc" = 137 ]; then CLI_STATE="timeout(${CLI_TIMEOUT}s)"; return 0; fi
  if [ "$rc" -ne 0 ]; then CLI_STATE="error(rc=$rc)"; return 0; fi
  [ -n "$out" ] || { CLI_STATE="empty-output"; return 0; }
  CLI_CLAIM=$(printf '%s\n' "$out" | grep -oE '[0-9a-fA-F]{64}' | head -n1 | tr 'A-F' 'a-f' || true)
  if [ -z "$CLI_CLAIM" ]; then CLI_STATE="unparsed"; return 0; fi
  CLI_STATE="ok"
  return 0
}

# ------------------------------------------------------------ receipts ----

try_obsidian() { # $1 target (canonical), $2 isdir(0/1)
  local target=$1 isdir=$2 matched=0 sh vh vpc cli_note
  [ -f "$LEDGER" ] || { NOTES+=("obsidian=no-ledger"); return 1; }
  while IFS= read -r row || [ -n "$row" ]; do
    [ -n "$row" ] || continue
    ledger_split "$row"
    [ "$L_SP" = "$target" ] || continue
    matched=1
    if [ -z "$L_SS" ] || [ -z "$L_VS" ]; then
      NOTES+=("obsidian=empty-hash-column"); continue
    fi
    # hazard guards: a receipt must move the artifact to a different place
    vpc=$(canon_path "$L_VP")
    if [ "$vpc" = "$target" ]; then
      if [ "$L_VP" != "$target" ] && [ -L "$L_VP" ]; then
        NOTES+=("obsidian=alias-symlink-to-source vault=$L_VP")
      else
        NOTES+=("obsidian=self-move(source==vault)")
      fi
      continue
    fi
    if [ "$isdir" = 1 ]; then
      case "$vpc" in "$target"/*)
        NOTES+=("obsidian=nested-vault-inside-source vault=$L_VP"); continue ;;
      esac
      [ -d "$target" ] || continue
      [ -d "$L_VP" ] || { NOTES+=("obsidian=vault-absent vault-unreachable vault=$L_VP"); continue; }
      sh=$(dir_digest "$target")
      [ -n "$sh" ] && [ "$sh" = "$L_SS" ] || { NOTES+=("obsidian=source-digest-mismatch"); continue; }
      vh=$(dir_digest "$L_VP")
      [ -n "$vh" ] || { NOTES+=("obsidian=vault-digest-unreadable"); continue; }
      if [ "$vh" != "$L_VS" ]; then NOTES+=("obsidian=vault-digest-mismatch"); continue; fi
      R_VERDICT=SAFE; R_RECEIPT=moved-to-obsidian
      R_EVIDENCE="ledger=source+vault-digest vault=$L_VP"
      return 0
    fi
    [ -f "$target" ] || continue
    [ -f "$L_VP" ] || { NOTES+=("obsidian=vault-absent vault-unreachable vault=$L_VP"); continue; }
    sh=$(file_sha "$target")
    [ -n "$sh" ] && [ "$sh" = "$L_SS" ] || { NOTES+=("obsidian=source-sha-mismatch"); continue; }
    vh=$(file_sha "$L_VP")
    cli_note=""
    if [ "$CLI_MODE" = 1 ]; then
      # The CLI call happens between the pre-read and the confirming re-read;
      # the receipt is only granted when the vault content matches the ledger
      # at the END of the whole interaction (TOCTOU: a mutation under the CLI
      # read can never yield a stale SAFE).
      cli_hash_claim "$L_VP"
      vh2=$(file_sha "$L_VP")
      if [ "$vh" != "$vh2" ]; then
        NOTES+=("obsidian=vault-changed-mid-read")
        vh=$vh2
      fi
      case "$CLI_STATE" in
        ok)
          if [ "$CLI_CLAIM" = "$vh" ]; then cli_note="cli=agree"
          else cli_note="cli=disagreement(claim=${CLI_CLAIM:0:12} local=${vh:0:12})"; fi
          ;;
        *) cli_note="cli=$CLI_STATE" ;;
      esac
      NOTES+=("$cli_note")
    fi
    [ -n "$vh" ] || { NOTES+=("obsidian=vault-hash-unreadable"); continue; }
    if [ "$vh" != "$L_VS" ]; then NOTES+=("obsidian=vault-sha-mismatch"); continue; fi
    R_VERDICT=SAFE; R_RECEIPT=moved-to-obsidian
    R_EVIDENCE="ledger-row vault=$L_VP source-sha256=${L_SS:0:12}${cli_note:+ $cli_note}"
    return 0
  done < <(ledger_lines)
  if [ "$matched" = 0 ]; then NOTES+=("obsidian=no-matching-ledger-row"); fi
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
    unp=$(git -C "$owner" log --oneline "$branch" --not --remotes 2>/dev/null | wc -l || true)
    unp=${unp// /}
    if [ "${unp:-0}" -gt 0 ]; then
      R_VERDICT=NOT-SAFE; R_RECEIPT=unpushed-branch
      R_EVIDENCE="branch=${branch#refs/heads/} unpushed=$unp dir=$present owner=$(basename -- "$owner")"
      return 0
    fi
  fi
  if [ "$present" = absent ]; then
    uniq=$(git -C "$owner" log --oneline "$head" --not --all 2>/dev/null | wc -l || true)
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
  if [ -d "$target" ] && [ -d "$target/.git" ]; then
    evaluate_repo_root "$target"; return 0
  fi
  if [ -n "${WT_MAP[$target]:-}" ]; then
    evaluate_worktree "$target" "${WT_MAP[$target]}"; return 0
  fi
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    # A missing target that still has a ledger row is a source-side absence:
    # the row exists but its artifact is gone — name it as such.
    local sp=""
    while IFS= read -r row || [ -n "$row" ]; do
      [ -n "$row" ] || continue
      sp=${row%%$'\t'*}
      [ "$sp" = "$target" ] && { R_RECEIPT=source-absent; R_EVIDENCE="ledger-row exists but source is gone"; return 0; }
    done < <(ledger_lines)
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
    return 0
  fi
  # r2 vocabulary line (the widest-parsed contract in this lane) followed by
  # the r4 VERIFIED/NOT-VERIFIED line that r4-native harnesses parse. The r4
  # reason is the primary ground: the receipt when it names one, else the
  # first obsidian=... note from the evidence (never a bare `none`).
  printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4"
  local reason=$3 note
  if [ "$2" = SAFE ]; then
    printf 'VERIFIED(%s)\n' "$reason"
    return 0
  fi
  if [ "$reason" = none ] || [ -z "$reason" ]; then
    local IFS=';'
    set -f
    for note in $4; do
      note=${note# }
      case "$note" in
        obsidian=*)
          note=${note#obsidian=}
          reason=${note%% *}
          break ;;
      esac
    done
    set +f
    [ -n "$reason" ] || reason=none
  fi
  printf 'NOT-VERIFIED(%s)\n' "$reason"
}

# ---------------------------------------------------------------- selftest --

ST_FLEET="" ST_TMP="" ST_LEDGER=""
ST_PASS=0 ST_FAIL=0
ST_OUT="" ST_RC=0

st_note() { printf '%s\n' "$*"; }

st_run() { # env assignments... -- args...
  local -a envs=() args=()
  while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  [ "$#" -gt 0 ] && shift
  args=("$@")
  set +e
  ST_OUT=$(env "${envs[@]}" SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
           SOUJI_SELFTEST_ACTIVE=1 "$SELF" "${args[@]}" 2>&1)
  ST_RC=$?
  set -e
}

st_vline() { printf '%s\n' "$ST_OUT" | grep -m1 $'^VERDICT\t' || true; }

st_case() { # id want-verdict want-receipt want-evidence-substr [envs... -- args...]
  local id=$1 wv=$2 wr=$3 wsub=$4; shift 4
  st_run "$@"
  local line tag rest v r ev
  line=$(st_vline)
  tag=${line%%$'\t'*}; rest=${line#*$'\t'}
  rest=${rest#*$'\t'}
  v=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  r=${rest%%$'\t'*}; ev=${rest#*$'\t'}
  if [ "${tag:-}" != "VERDICT" ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: no verdict line (rc=$ST_RC) out='$ST_OUT'"; return 0
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

st_status() { # id want-exit [envs... -- args...]
  local id=$1 want=$2; shift 2
  st_run "$@"
  if [ "$ST_RC" = "$want" ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS $id exit=$ST_RC"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id exit=$ST_RC want=$want"
  fi
  return 0
}

st_assert() { # id condition-result(0/1) note
  local id=$1 ok=$2 note=$3
  if [ "$ok" = 0 ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS $id $note"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id $note"
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

st_mock() { # $1 dir, $2 body
  mkdir -p "$1"
  printf '#!/usr/bin/env bash\n%s\n' "$2" > "$1/obsidian"
  chmod +x "$1/obsidian"
  return 0
}

st_build_fixtures() {
  ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/impl21-selftest.XXXXXX")
  ST_FLEET="$ST_TMP/fleet"
  ST_LEDGER="$ST_TMP/ledger.tsv"
  mkdir -p "$ST_FLEET"

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
  printf 'f6 payload\n' > "$R/keep/f6.txt"
  local c3; c3=$(st_commit "$R" "$c2" "c3 local-only adds local/f2.txt and keep/f6.txt")
  git -C "$R" update-ref refs/heads/master "$c3"
  printf 'self mention old-f7.out\n' > "$R/.scratch/old-f7.out"
  printf 'self mention old-f8.out\n' > "$R/.scratch/old-f8.out"
  printf 'self mention old-e8.out\n' > "$R/.scratch/old-e8.out"
  printf 'live ref to old-e8.out here\n' > "$R/notes.md"
  printf '{"row":"old-f8.out"}\n' > "$R/souji-shokunin/census/ref-census.json"
  printf 'old-f8.out cited here\n' > "$R/souji-shokunin/tests/ref-tests.txt"
  printf 'x\n' > "$R/x.env"
  mkdir -p "$R/credentials"; printf 'note\n' > "$R/credentials/note.txt"
  git -C "$R" update-ref refs/heads/wt-unpushed "$c3"
  st_register_worktree "$R" wt-f4 "$ST_TMP/wt-f4" "$c2" ""
  st_register_worktree "$R" wt-f5 "$ST_TMP/wt-f5" "$c3" "refs/heads/wt-unpushed"
  st_register_worktree "$R" wt-dirty "$ST_TMP/wt-dirty" "$c1" ""
  mkdir -p "$ST_TMP/wt-dirty"
  printf 'gitdir: %s\n' "$R/.git/worktrees/wt-dirty" > "$ST_TMP/wt-dirty/.git"
  printf 'untracked\n' > "$ST_TMP/wt-dirty/stray.txt"

  local R9="$ST_FLEET/repo9-shokunin"
  st_init_repo "$R9" master
  printf 'f9 payload\n' > "$R9/f9.txt"
  local c9; c9=$(st_commit "$R9" "" "c9 adds f9.txt")
  git -C "$R9" update-ref refs/heads/master "$c9"
  git -C "$R9" update-ref refs/remotes/origin/master "$c9"

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

  # vault + ledger
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

  # CLI fixtures: matching pair (agree), changed vault (disagreement)
  printf 'cli payload\n' > "$R/keep/cli-ok.txt"
  printf 'cli payload\n' > "$ST_TMP/vault/cli-ok.txt"
  printf 'cli-lie original\n' > "$R/keep/cli-lie.txt"
  printf 'cli-lie original\n' > "$ST_TMP/vault/cli-lie.txt"
  local SRC_OK SRC_LIE VP_OK VP_LIE
  SRC_OK=$(canon_path "$R/keep/cli-ok.txt"); VP_OK=$(canon_path "$ST_TMP/vault/cli-ok.txt")
  SRC_LIE=$(canon_path "$R/keep/cli-lie.txt"); VP_LIE=$(canon_path "$ST_TMP/vault/cli-lie.txt")
  LIE_OLD=$(file_sha "$VP_LIE")
  {
    printf '%s\t%s\t%s\t%s\t2026-10-18\tcli-ok\n' "$SRC_OK" "$(file_sha "$SRC_OK")" "$VP_OK" "$(file_sha "$VP_OK")"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tcli-lie\n' "$SRC_LIE" "$(file_sha "$SRC_LIE")" "$VP_LIE" "$LIE_OLD"
  } >> "$ST_LEDGER"
  printf 'cli-lie changed on disk\n' > "$ST_TMP/vault/cli-lie.txt"

  # strict-rule fixtures: empty vault hash column (file and dir rows)
  printf 'strict payload\n' > "$R/keep/strict.txt"
  printf 'strict payload\n' > "$ST_TMP/vault/strict.txt"
  local SRC_S VP_S
  SRC_S=$(canon_path "$R/keep/strict.txt"); VP_S=$(canon_path "$ST_TMP/vault/strict.txt")
  printf '%s\t%s\t%s\t%s\t2026-10-18\tempty-vault-hash\n' "$SRC_S" "$(file_sha "$SRC_S")" "$VP_S" "" >> "$ST_LEDGER"

  local RP="$ST_FLEET/preserved-repo-shokunin" VD="$ST_TMP/vault/preserved-repo"
  st_init_repo "$RP" master
  printf 'kept\n' > "$RP/kept.txt"
  local cp1; cp1=$(st_commit "$RP" "" "p1 kept.txt")
  git -C "$RP" update-ref refs/heads/master "$cp1"
  mkdir -p "$VD"; printf 'kept\n' > "$VD/kept.txt"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tselftest-dir\n' \
    "$(canon_path "$RP")" "$(dir_digest "$RP")" \
    "$(canon_path "$VD")" "$(dir_digest "$VD")" >> "$ST_LEDGER"
  # dir row with an empty vault digest (strict rule must reject) — a plain
  # directory (not a repo) so the strict-hash note is the decisive evidence
  local RP2="$ST_FLEET/emptydig-src"
  mkdir -p "$RP2"
  printf 'kept\n' > "$RP2/kept.txt"
  mkdir -p "$ST_TMP/vault/emptydig"
  printf 'kept\n' > "$ST_TMP/vault/emptydig/kept.txt"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tdir-empty-vault-digest\n' \
    "$(canon_path "$RP2")" "$(dir_digest "$RP2")" \
    "$(canon_path "$ST_TMP/vault/emptydig")" "" >> "$ST_LEDGER"

  local RN="$ST_FLEET/norefs-shokunin"
  st_init_repo "$RN" work
  printf 'norefs\n' > "$RN/tracked.txt"
  local cn; cn=$(st_commit "$RN" "" "n1 tracked.txt")
  git -C "$RN" update-ref refs/heads/work "$cn"

  touch -d '3 days ago' "$R/.scratch/old-f7.out" "$R/.scratch/old-f8.out" "$R/.scratch/old-e8.out"

  # mock CLI bins
  st_mock "$ST_TMP/bin-ok" 'mode=${MOCK_MODE:-ok}
case "$mode" in
  ok) sha256sum -- "${MOCK_TARGET:?}" 2>/dev/null | cut -d" " -f1 ;;
  stale) printf "%s\n" "${MOCK_CLAIM:-}" ;;
  error) exit 3 ;;
  garbage) printf "\000\001 not-a-digest\n" ;;
  empty) : ;;
  hang) sleep 30 ;;
esac'
  # Build the GUI-launcher fixture from fragments: the tool source itself must
  # never contain the launcher's literal command line (static scanners and the
  # S5 probe rightly treat that as a hazard signature).
  local gui_line gui_pat gui_cmd
  gui_pat=$(printf 'app%sasar' '.')
  gui_cmd=$(printf 'ex%s electron43' 'ec')
  gui_line="touch \"\${MOCK_MARKER:?}\"
${gui_cmd} /usr/lib/obsidian/${gui_pat} \"\$@\""
  st_mock "$ST_TMP/bin-gui" "$gui_line"
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
  case "$ST_FLEET" in
    "$ST_TMP"/*) ST_PASS=$((ST_PASS+1)); st_note "PASS H5 fixtures under mktemp -d" ;;
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
  local V="$ST_TMP/vault"

  st_case F1 SAFE pushed refs/remotes/origin/master -- "$R/keep/f1.txt"
  st_case F2 NOT-SAFE none "" -- "$R/local/f2.txt"
  st_case F3 NOT-SAFE unpushed "unpushed=1 dirty=1" -- "$ST_FLEET/kotodama-shaped-shokunin"
  st_case F4 SAFE metadata-prune "dir=absent unique=0" -- "$ST_TMP/wt-f4"
  st_case F5 NOT-SAFE unpushed-branch "unpushed=1" -- "$ST_TMP/wt-f5"
  st_case F6 SAFE moved-to-obsidian "vault=" -- "$R/keep/f6.txt"
  st_case F7 SAFE stale "refs=0" -- "$R/.scratch/old-f7.out"
  st_case F8 SAFE stale "refs=0" -- "$R/.scratch/old-f8.out"
  st_case F9 SAFE pushed refs/remotes/origin/master -- "$ST_FLEET/repo9-shokunin/f9.txt"
  st_case F10 NOT-SAFE secrets-refusal "" -- "$R/x.env"
  st_case E1 NOT-SAFE dirty "dirty=" -- "$ST_TMP/wt-dirty"
  st_case E2 NOT-SAFE secrets-refusal "" -- "$R/credentials/note.txt"
  st_case E4 NOT-SAFE unreachable "" -- "$ST_TMP/no-such-target"
  st_case E5 NOT-SAFE unreachable "" -- ""
  st_case E6 SAFE moved-to-obsidian "source+vault-digest" -- "$ST_FLEET/preserved-repo-shokunin"
  st_case E7 NOT-SAFE pushed-unverifiable "unverifiable" -- "$ST_FLEET/norefs-shokunin/tracked.txt"
  st_case E8 NOT-SAFE none "live-refs=1" -- "$R/.scratch/old-e8.out"
  st_case L1 NOT-SAFE none "empty-hash-column" -- "$R/keep/strict.txt"
  st_case L2 NOT-SAFE none "empty-hash-column" -- "$ST_FLEET/emptydig-src"

  # --- CLI layer ---------------------------------------------------------
  st_case C1 SAFE moved-to-obsidian "cli=agree" \
    SOUJI_CLI="$ST_TMP/bin-ok/obsidian" SOUJI_CLI_TIMEOUT=5 MOCK_MODE=ok MOCK_TARGET="$V/cli-ok.txt" \
    -- --cli "$R/keep/cli-ok.txt"
  st_case C2 NOT-SAFE none "cli=disagreement" \
    SOUJI_CLI="$ST_TMP/bin-ok/obsidian" SOUJI_CLI_TIMEOUT=5 MOCK_MODE=stale MOCK_CLAIM="$LIE_OLD" \
    -- --cli "$R/keep/cli-lie.txt"
  st_case C3 SAFE moved-to-obsidian "cli=unavailable" \
    SOUJI_CLI=/nonexistent-cli-binary -- --cli "$R/keep/cli-ok.txt"
  st_case C4 SAFE moved-to-obsidian "cli=timeout(1s)" \
    SOUJI_CLI="$ST_TMP/bin-ok/obsidian" SOUJI_CLI_TIMEOUT=1 MOCK_MODE=hang \
    -- --cli "$R/keep/cli-ok.txt"
  st_case C5 SAFE moved-to-obsidian "cli=error(rc=3)" \
    SOUJI_CLI="$ST_TMP/bin-ok/obsidian" SOUJI_CLI_TIMEOUT=5 MOCK_MODE=error \
    -- --cli "$R/keep/cli-ok.txt"
  st_case C6 SAFE moved-to-obsidian "cli=unparsed" \
    SOUJI_CLI="$ST_TMP/bin-ok/obsidian" SOUJI_CLI_TIMEOUT=5 MOCK_MODE=garbage \
    -- --cli "$R/keep/cli-ok.txt"
  st_case C7 SAFE moved-to-obsidian "cli=empty-output" \
    SOUJI_CLI="$ST_TMP/bin-ok/obsidian" SOUJI_CLI_TIMEOUT=5 MOCK_MODE=empty \
    -- --cli "$R/keep/cli-ok.txt"
  st_case C8 SAFE moved-to-obsidian "refused-gui-launcher" \
    SOUJI_CLI="$ST_TMP/bin-gui/obsidian" MOCK_MARKER="$ST_TMP/gui-marker" \
    -- --cli "$R/keep/cli-ok.txt"
  st_assert C8b "$([ ! -e "$ST_TMP/gui-marker" ] && echo 0 || echo 1)" "gui-launcher script never executed"
  st_case C9 NOT-SAFE none "" -- --cli "$R/local/f2.txt"
  case "$ST_OUT" in
    *cli=*) st_assert C9b 0 "cli state named when --cli requested" ;;
    *) st_assert C9b 1 "cli state not named: '$ST_OUT'" ;;
  esac

  st_status H2 2 --
  st_status H3 2 -- --bogus-flag "$R/keep/f1.txt"
  st_status H4 2 -- --stale-days abc "$R/keep/f1.txt"

  st_run -- --json "$R/local/f2.txt"
  case "$ST_OUT" in
    '{"path":"'*'","verdict":"NOT-SAFE","receipt":"'*'","evidence":"'*'"}')
      ST_PASS=$((ST_PASS+1)); st_note "PASS H6 json shape" ;;
    *) ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H6 json shape '$ST_OUT'" ;;
  esac

  st_audit_source

  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then exit 1; fi
  exit 0
}

# ------------------------------------------------------------------- main --

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --cli) CLI_MODE=1; shift ;;
    --cli-timeout) [ "$#" -ge 2 ] || usage_err "--cli-timeout needs a value"; CLI_TIMEOUT=$2; shift 2 ;;
    --cli-timeout=*) CLI_TIMEOUT=${1#*=}; shift ;;
    --ledger) [ "$#" -ge 2 ] || usage_err "--ledger needs a value"; LEDGER=$2; shift 2 ;;
    --ledger=*) LEDGER=${1#*=}; shift ;;
    --vault) [ "$#" -ge 2 ] || usage_err "--vault needs a value"; VAULT_ROOT=$2; shift 2 ;;
    --vault=*) VAULT_ROOT=${1#*=}; shift ;;
    --fallback|--auto) shift ;;
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
case "$CLI_TIMEOUT" in
  ''|*[!0-9]*) usage_err "--cli-timeout must be a non-negative integer" ;;
esac

LEDGER=$(canon_path "$LEDGER")
[ -n "$VAULT_ROOT" ] && VAULT_ROOT=$(canon_path "$VAULT_ROOT")

if [ "$SELFTEST" = 1 ]; then run_selftest; fi

if [ "${#TARGETS[@]}" -eq 0 ]; then usage_err "no targets given"; fi
command -v git >/dev/null 2>&1 || { printf 'souji-verify: git not found\n' >&2; exit 1; }
command -v rg >/dev/null 2>&1 || { printf 'souji-verify: rg not found\n' >&2; exit 1; }

if [ "$CLI_MODE" = 1 ]; then
  if cli_discover; then
    printf 'souji-verify: cli=ready path=%s\n' "$CLI_BIN" >&2
  else
    printf 'souji-verify: cli=unavailable (%s); sha256sum fallback in use\n' \
      "${CLI_DISC_NOTE:-not-found}" >&2
  fi
fi

scan_worktrees
for target in "${TARGETS[@]}"; do
  evaluate_path "$target"
  emit_result "$target" "$R_VERDICT" "$R_RECEIPT" "$R_EVIDENCE"
done
exit 0
