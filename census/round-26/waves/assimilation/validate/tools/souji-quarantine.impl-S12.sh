#!/usr/bin/env bash
# souji-quarantine — quarantine-flow state machine (round 8, seat S12).
#
# Implements the AGENTS.md removal flow as executable state:
#   receipt -> quarantine staging -> hold period -> second receipt check
#   -> release (permanent removal) | restore (put it back)
#
# The receipt of record is ALWAYS tools/souji-verify.sh (the r2/r5/r6-hardened
# engine). stage refuses any target the engine does not mark SAFE with a
# receipt in {pushed, moved-to-obsidian, stale}. No receipt, no staging.
#
# CLI
#   tools/souji-quarantine.impl-S12.sh --selftest
#   tools/souji-quarantine.impl-S12.sh [--dry-run] [--hold-seconds N]
#         [--stale-days N] [--root DIR] stage <target>
#   tools/souji-quarantine.impl-S12.sh [--root DIR] status [<entry>|all]
#   tools/souji-quarantine.impl-S12.sh [--root DIR] check <entry>
#   tools/souji-quarantine.impl-S12.sh [--root DIR] release <entry>
#   tools/souji-quarantine.impl-S12.sh [--root DIR] restore <entry>
#
# Output: one event line per action
#   STAGED entry=<id> target=<path> receipt=<r> hold_until=<epoch> sha=<16>
#   CHECK result=PASS|HOLD|FAIL entry=<id> reason=<why>
#   RELEASED entry=<id> receipt=<r>
#   RESTORED entry=<id> target=<path>
#   STAGE-REFUSED reason=<engine receipt-or-reason> verdict=<VERDICT line>
# Exit codes: 0 = action succeeded; 3 = live-tree-locked (refused);
# 4 = stage refused by receipt gate; 5 = check FAIL; 2 = usage/absent.
#
# Quarantine state lives at <root>/.ufo-quarantine/<entry>/ where <entry> is
# <UTC-timestamp>-<basename>; payload is copied to payload/<basename> and the
# original unlinked only after the copy re-hashes to the staged digest.
# manifest.tsv (tab-separated) rides inside the entry:
#   1 target(canonical) 2 orig_parent 3 basename 4 receipt 5 evidence
#   6 sha256 7 staged_at(epoch) 8 hold_until(epoch) 9 state 10 engine_evidence
#
# Safety rails
#   * Every mutating subcommand (stage/check/release/restore) requires the
#     quarantine root to be inside a directory listed in
#     SOUJI_QUARANTINE_ALLOW (colon-separated). Without it the tool refuses:
#     rc=3 live-tree-locked. The live fleet is NEVER mutated by this tool
#     unless the operator explicitly allow-lists a root; --dry-run works
#     anywhere and writes nothing.
#   * --selftest builds its own fixture fleet under mktemp -d and allow-lists
#     only that dir; it never touches the live tree.
#   * Secret-shaped paths (*.env, .envrc, *credential*, *secret*, id_*,
#     *.pem) are refused before anything is read.
#   * No git fetch/push/commit/branch/checkout/reset/rebase is ever run;
#     the vault side is read read-only; .ufo/state, .ufo/watchdog.log,
#     ~/.config are never touched.
#   * Symlink inside a staged scope fails closed (symlink-present), matching
#     the engine's r5 rule.
#
# Env: SOUJI_VERIFY_BIN (default: sibling souji-verify.sh), SOUJI_LEDGER and
# SHOKUNIN_ROOT are forwarded to the engine; SOUJI_QUARANTINE_ALLOW.
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
VERIFY_BIN="${SOUJI_VERIFY_BIN:-$REPO_ROOT/tools/souji-verify.sh}"

DRY_RUN=0
HOLD_SECONDS=86400      # default hold: 1 day (mirrors the engine's stale-day)
STALE_DAYS=1
ROOT=""
SUBCMD=""
TARGET=""

usage() { sed -n '2,60p' "$SCRIPT_PATH" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
usage_err() { printf 'souji-quarantine: %s\n' "$1" >&2; usage 2; }

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

file_sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

# Directory digest; rc 2 when any symlink is inside the scope (fail closed).
dir_digest() {
  local d=$1
  if [ -n "$(find "$d" -type l -print -quit 2>/dev/null)" ]; then return 2; fi
  find "$d" -type f -print0 2>/dev/null | sort -z \
    | xargs -0 -r sha256sum 2>/dev/null | sha256sum | cut -d' ' -f1
}

allowed_root() { # $1 canonical dir under quarantine -> 0 when allow-listed
  local q=${1:-} a
  [ -n "${SOUJI_QUARANTINE_ALLOW:-}" ] || return 1
  local IFS=:
  for a in $SOUJI_QUARANTINE_ALLOW; do
    [ -n "$a" ] || continue
    case "$q/" in "$a/"*) return 0 ;; esac
  done
  return 1
}

locked() { # mutating use requires an allow-listed root
  if ! allowed_root "$(canon "$ROOT")"; then
    printf 'LIVE-TREE-LOCKED root=%s (set SOUJI_QUARANTINE_ALLOW to a fixture root)\n' "$ROOT" >&2
    exit 3
  fi
}

# --- receipt engine bridge -------------------------------------------------
# Runs the engine on one target; prints "SAFE|NOT-SAFE<TAB>receipt<TAB>evidence".
engine_verdict() { # $1 target
  local out line
  out=$(SHOKUNIN_ROOT="${SHOKUNIN_ROOT:-}" "$VERIFY_BIN" --stale-days "$STALE_DAYS" "$1" 2>&1 || true)
  line=$(printf '%s\n' "$out" | awk -F'\t' '$1=="VERDICT"{v=$2"\t"$3"\t"$4"\t"$5} END{if(v!="")print v}')
  [ -n "$line" ] || line="NOT-SAFE<TAB>engine-error<TAB>no-verdict-line"
  printf '%s' "$line"
}

# --- manifest I/O ----------------------------------------------------------
load_manifest() { # $1 entry dir -> sets M_* globals
  local mf="$1/manifest.tsv"
  [ -f "$mf" ] || { printf 'souji-quarantine: no manifest in %s\n' "$1" >&2; exit 2; }
  IFS=$'\t' read -r M_TARGET M_ORIG_PARENT M_BASENAME M_RECEIPT M_EVIDENCE \
    M_SHA M_STAGED_AT M_HOLD_UNTIL M_STATE M_ENGINE_EVID <"$mf"
}

save_state() { # $1 entry dir, $2 new state
  local mf="$1/manifest.tsv" state=$2
  { printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$M_TARGET" "$M_ORIG_PARENT" "$M_BASENAME" "$M_RECEIPT" "$M_EVIDENCE" \
      "$M_SHA" "$M_STAGED_AT" "$M_HOLD_UNTIL" "$state" "$M_ENGINE_EVID"; } >"$mf"
  M_STATE=$state
}

# --- stale receipt re-evidence: the engine's D3 live-reference sweep -------
live_refs() { # $1 basename, $2 search-root -> prints ref count
  local base=$1 repo=$2 n
  n=$(cd "$repo" 2>/dev/null && rg -l --no-ignore --fixed-strings -e "$base" . \
        -g '!.git' \
        -g '!souji-shokunin/census/**' -g '!**/souji-shokunin/census/**' \
        -g '!souji-shokunin/tests/**' -g '!**/souji-shokunin/tests/**' \
        -g '!**/.ufo-quarantine/**' 2>/dev/null | wc -l || true)
  printf '%s' "${n:-0}"
}

repo_of() { # $1 original canonical path -> enclosing git toplevel (may be empty)
  local p=$1 dir
  dir=$p
  while [ "$dir" != "/" ]; do
    [ -e "$dir/.git" ] && { git -C "$dir" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$dir"; return 0; }
    dir=$(dirname -- "$dir")
  done
  printf ''
}

# --- subcommands -----------------------------------------------------------

cmd_stage() {
  [ -n "$TARGET" ] || usage_err "stage: missing target"
  local t; t=$(canon "$TARGET")
  [ -e "$t" ] || { printf 'STAGE-REFUSED reason=unreachable path=%s\n' "$t"; exit 4; }
  if is_secret_shaped "$t"; then
    printf 'STAGE-REFUSED reason=secrets-refusal path=%s\n' "$t"; exit 4
  fi
  if [ "$DRY_RUN" != 1 ]; then
    locked   # a locked tool does not even read the target; dry-run may
  fi

  # receipt #1 — the engine decides, not this tool
  local verdict receipt evidence
  IFS=$'\t' read -r _p verdict receipt evidence <<<"$(engine_verdict "$t")"
  case "$verdict" in
    SAFE) : ;;
    *) printf 'STAGE-REFUSED reason=%s verdict=%s evidence=%s\n' "$receipt" "$verdict" "$evidence"
       exit 4 ;;
  esac
  case "$receipt" in
    pushed|moved-to-obsidian|stale) : ;;
    *) printf 'STAGE-REFUSED reason=%s verdict=%s evidence=%s\n' "$receipt" "$verdict" "$evidence"
       exit 4 ;;
  esac

  local base parent sha st_rc
  base=$(basename -- "$t")
  parent=$(dirname -- "$t")
  if [ -d "$t" ]; then
    sha=$(dir_digest "$t"); st_rc=$?
    [ "$st_rc" = 2 ] && { printf 'STAGE-REFUSED reason=symlink-present path=%s\n' "$t"; exit 4; }
  else
    sha=$(file_sha "$t")
  fi

  local staged_at hold_until entry payload
  staged_at=$(date -u +%s)
  hold_until=$(( staged_at + HOLD_SECONDS ))
  entry="$(date -u +%Y%m%dT%H%M%SZ)-$base"
  local q="$ROOT/.ufo-quarantine/$entry"
  if [ "$DRY_RUN" = 1 ]; then
    printf 'DRY-RUN would-stage entry=%s target=%s receipt=%s hold_until=%s sha=%s\n' \
      "$entry" "$t" "$receipt" "$hold_until" "${sha:0:16}"
    return 0
  fi

  if ! allowed_root "$t"; then
    printf 'LIVE-TREE-LOCKED target=%s outside SOUJI_QUARANTINE_ALLOW\n' "$t" >&2
    exit 3
  fi

  mkdir -p "$q/payload"
  payload="$q/payload/$base"
  cp -a -- "$t" "$payload"
  local sha2
  if [ -d "$payload" ]; then sha2=$(dir_digest "$payload"); else sha2=$(file_sha "$payload"); fi
  if [ "$sha2" != "$sha" ]; then
    rm -rf -- "$q"
    printf 'STAGE-REFUSED reason=copy-digest-mismatch path=%s\n' "$t"; exit 4
  fi
  rm -rf -- "$t"   # original unlinked only after the copy re-hashed true

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$t" "$parent" "$base" "$receipt" "$evidence" "$sha" "$staged_at" \
    "$hold_until" "staged" "$receipt" >"$q/manifest.tsv"
  printf 'STAGED entry=%s target=%s receipt=%s hold_until=%s sha=%s\n' \
    "$entry" "$t" "$receipt" "$hold_until" "${sha:0:16}"
}

cmd_status() {
  local q="$ROOT/.ufo-quarantine"
  [ -d "$q" ] || { printf 'STATUS empty\n'; return 0; }
  local e sel=${1:-all}
  for e in "$q"/*/; do
    [ -d "$e" ] || continue
    load_manifest "${e%/}"
    if [ "$sel" != "all" ] && [ "${sel%/}" != "$(basename -- "${e%/}")" ]; then continue; fi
    printf 'ENTRY=%s state=%s receipt=%s target=%s hold_until=%s sha=%s\n' \
      "$(basename -- "${e%/}")" "$M_STATE" "$M_RECEIPT" "$M_TARGET" \
      "$M_HOLD_UNTIL" "${M_SHA:0:16}"
  done
}

# Second receipt check. PASS only when: hold expired, payload digest
# unchanged, original not recreated, and the receipt's evidence still holds.
cmd_check() {
  [ -n "$TARGET" ] || usage_err "check: missing entry"
  locked
  local q="$ROOT/.ufo-quarantine/$TARGET"
  [ -d "$q" ] || { printf 'CHECK result=FAIL entry=%s reason=no-such-entry\n' "$TARGET"; exit 5; }
  load_manifest "$q"
  local now; now=$(date -u +%s)
  if [ "$now" -lt "$M_HOLD_UNTIL" ]; then
    printf 'CHECK result=HOLD entry=%s reason=hold-until=%s now=%s\n' "$TARGET" "$M_HOLD_UNTIL" "$now"
    return 0
  fi
  local sha2
  if [ -d "$q/payload/$M_BASENAME" ]; then sha2=$(dir_digest "$q/payload/$M_BASENAME")
  else sha2=$(file_sha "$q/payload/$M_BASENAME"); fi
  if [ "$sha2" != "$M_SHA" ]; then
    save_state "$q" "check-failed"
    printf 'CHECK result=FAIL entry=%s reason=payload-digest-mismatch\n' "$TARGET"; exit 5
  fi
  if [ -e "$M_TARGET" ]; then
    save_state "$q" "check-failed"
    printf 'CHECK result=FAIL entry=%s reason=origin-recreated path=%s\n' "$TARGET" "$M_TARGET"; exit 5
  fi
  case "$M_RECEIPT" in
    stale)
      local repo refs
      repo=$(repo_of "$M_TARGET")
      [ -n "$repo" ] || repo="$ROOT"
      refs=$(live_refs "$M_BASENAME" "$repo")
      if [ "$refs" != "0" ]; then
        save_state "$q" "check-failed"
        printf 'CHECK result=FAIL entry=%s reason=live-refs=%s\n' "$TARGET" "$refs"; exit 5
      fi
      printf 'CHECK result=PASS entry=%s reason=stale-refs=0\n' "$TARGET" ;;
    pushed)
      local repo intro found
      repo=$(repo_of "$M_TARGET")
      intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "${M_TARGET#"$repo"/}" 2>/dev/null || true)
      found=$(git -C "$repo" branch -r --contains "$intro" 2>/dev/null | grep -c 'origin/' || true)
      if [ "${intro:-}" = "" ] || [ "${found:-0}" -eq 0 ]; then
        save_state "$q" "check-failed"
        printf 'CHECK result=FAIL entry=%s reason=pushed-receipt-lost intro=%s\n' "$TARGET" "${intro:0:12}"; exit 5
      fi
      printf 'CHECK result=PASS entry=%s reason=pushed-intro=%s still-on-origin\n' "$TARGET" "${intro:0:12}" ;;
    moved-to-obsidian)
      local row vp vs vsha
      [ -f "${SOUJI_LEDGER:-$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv}" ] || {
        save_state "$q" "check-failed"
        printf 'CHECK result=FAIL entry=%s reason=ledger-gone\n' "$TARGET"; exit 5; }
      row=$(grep -F -- "$M_TARGET" "${SOUJI_LEDGER:-$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv}" | head -1 || true)
      [ -n "$row" ] || {
        save_state "$q" "check-failed"
        printf 'CHECK result=FAIL entry=%s reason=ledger-row-gone\n' "$TARGET"; exit 5; }
      IFS=$'\t' read -r _sp _ss vp vs _rest <<<"$row"
      [ -f "$vp" ] || {
        save_state "$q" "check-failed"
        printf 'CHECK result=FAIL entry=%s reason=vault-gone vault=%s\n' "$TARGET" "$vp"; exit 5; }
      vsha=$(file_sha "$vp")
      [ "$vsha" = "$vs" ] || {
        save_state "$q" "check-failed"
        printf 'CHECK result=FAIL entry=%s reason=vault-sha-mismatch\n' "$TARGET"; exit 5; }
      printf 'CHECK result=PASS entry=%s reason=vault-hash-ok vault=%s\n' "$TARGET" "$vp" ;;
  esac
  save_state "$q" "ready"
}

cmd_release() {
  [ -n "$TARGET" ] || usage_err "release: missing entry"
  locked
  local q="$ROOT/.ufo-quarantine/$TARGET"
  [ -d "$q" ] || { printf 'RELEASE-REFUSED entry=%s reason=no-such-entry\n' "$TARGET"; exit 5; }
  load_manifest "$q"
  # release always re-runs the second receipt check; never trust prior state
  local out rc=0
  out=$(cmd_check_inproc "$TARGET" 2>&1) || rc=$?
  if [ $rc -ne 0 ] || printf '%s' "$out" | grep -q 'result=FAIL\|result=HOLD'; then
    printf 'RELEASE-REFUSED entry=%s check=%s\n' "$TARGET" "$(printf '%s' "$out" | tail -1)"
    exit 5
  fi
  load_manifest "$q"   # check may have rewritten state
  if [ "$M_STATE" != "ready" ]; then
    printf 'RELEASE-REFUSED entry=%s reason=state=%s\n' "$TARGET" "$M_STATE"; exit 5
  fi
  local log="$ROOT/.ufo-quarantine/RELEASES.log"
  printf 'RELEASED\t%s\tentry=%s\ttarget=%s\treceipt=%s\tsha256=%s\tevidence=%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$TARGET" "$M_TARGET" "$M_RECEIPT" "$M_SHA" "$M_EVIDENCE" >>"$log"
  rm -rf -- "$q"
  printf 'RELEASED entry=%s receipt=%s target=%s\n' "$TARGET" "$M_RECEIPT" "$M_TARGET"
}

# internal check that does not re-lock (used by release)
cmd_check_inproc() {
  local save=$TARGET
  TARGET=$1
  cmd_check
  TARGET=$save
}

cmd_restore() {
  [ -n "$TARGET" ] || usage_err "restore: missing entry"
  locked
  local q="$ROOT/.ufo-quarantine/$TARGET"
  [ -d "$q" ] || { printf 'RESTORE-REFUSED entry=%s reason=no-such-entry\n' "$TARGET"; exit 5; }
  load_manifest "$q"
  if ! allowed_root "$M_TARGET"; then
    printf 'LIVE-TREE-LOCKED target=%s outside SOUJI_QUARANTINE_ALLOW\n' "$M_TARGET" >&2
    exit 3
  fi
  if [ -e "$M_TARGET" ]; then
    printf 'RESTORE-REFUSED entry=%s reason=origin-exists path=%s\n' "$TARGET" "$M_TARGET"; exit 5
  fi
  mv -- "$q/payload/$M_BASENAME" "$M_TARGET"
  rm -rf -- "$q"
  printf 'RESTORED entry=%s target=%s\n' "$TARGET" "$M_TARGET"
}

# --- selftest --------------------------------------------------------------
# Fixture fleet under mktemp; allow-lists only that dir. Mirrors the engine's
# F1/F7/F6 + adversarial gate cases, then drives the full flow through the CLI.
selftest() {
  local T
  T=$(mktemp -d /tmp/souji-quarantine-selftest.XXXXXX)
  SELFTEST_T=$T
  trap 'rm -rf "${SELFTEST_T:-}"' EXIT
  export SOUJI_QUARANTINE_ALLOW="$T"
  export SHOKUNIN_ROOT="$T/fleet"
  local R="$T/fleet/qx-shokunin"
  mkdir -p "$R/keep" "$R/.scratch" "$R/corpus/knowledge" "$R/docs" "$T/vault"
  git -C "$R" init -q -b master
  GIT_AUTHOR_NAME=t GIT_COMMITTER_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_EMAIL=t@t \
    git -C "$R" -c commit.gpgsign=false commit -q --allow-empty -m init
  printf 'pushed artifact\n' >"$R/keep/pushed.txt"
  printf 'x\n' >"$R/docs/code.py"
  git -C "$R" add keep/pushed.txt docs/code.py
  GIT_AUTHOR_NAME=t GIT_COMMITTER_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_EMAIL=t@t \
    git -C "$R" -c commit.gpgsign=false commit -qm "add pushed artifact"
  git -C "$R" update-ref refs/remotes/origin/master "$(git -C "$R" rev-parse HEAD)"
  git -C "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  printf 'stale scratch\n' >"$R/.scratch/old-s12.out"
  printf 'referenced below\n' >"$R/.scratch/old-e12.out"
  printf 'mention old-e12.out here\n' >>"$R/docs/code.py"
  touch -d '3 days ago' "$R/.scratch/old-s12.out" "$R/.scratch/old-e12.out"
  # ledger + vault fixture
  local note="$T/vault/moved-note.md"
  mkdir -p "$R/notes"
  printf 'moved to obsidian\n' >"$R/notes/moved.md"
  cp -- "$R/notes/moved.md" "$note"
  local ssha vsha
  ssha=$(file_sha "$R/notes/moved.md"); vsha=$(file_sha "$note")
  printf '%s\t%s\t%s\t%s\tr8-selftest\n' "$R/notes/moved.md" "$ssha" "$note" "$vsha" \
    >"$R/corpus/knowledge/obsidian-ledger.tsv"
  # untracked-dirty target (gate must refuse)
  printf 'untracked dirty\n' >"$R/keep/dirty.txt"
  # secret-shaped target
  mkdir -p "$R/.scratch"; printf 'k\n' >"$R/.scratch/id_probe.pem"
  export SOUJI_LEDGER="$R/corpus/knowledge/obsidian-ledger.tsv"

  local TOOL="$SCRIPT_PATH" pass=0 fail=0 out rc
  ck() { # $1 id, $2 expect-regex, $3 actual — match the FIRST event line only
    local id=$1 re=$2 actual=$3 first
    first=$(printf '%s\n' "$actual" | head -1)
    if printf '%s' "$first" | grep -Eq "$re"; then
      pass=$((pass+1)); printf 'PASS %s :: %s\n' "$id" "$first"
    else
      fail=$((fail+1)); printf 'FAIL %s expect=%s got-first-line=%s\n' "$id" "$re" "$first"
    fi
  }
  run() { set +e; out=$(bash "$TOOL" --root "$T" "$@" 2>&1); rc=$?; set -e; }

  # G1: no allow-list -> live-tree-locked even with a valid receipt
  run_env() { set +e; out=$(env -u SOUJI_QUARANTINE_ALLOW bash "$TOOL" --root "$T" "$@" 2>&1); rc=$?; set -e; }
  run_env stage "$R/keep/pushed.txt"
  ck G1-locked 'LIVE-TREE-LOCKED' "$out"
  # G1b: live-tree-locked rc=3
  ck G1b-rc3 '^3$' "$rc"

  # D1: dirty/untracked target -> engine refuses -> stage refuses
  run stage "$R/keep/dirty.txt"
  ck D1-dirty-refused 'STAGE-REFUSED reason=' "$out"
  # D2: live-referenced stale -> refused
  run stage "$R/.scratch/old-e12.out"
  ck D2-liverefs-refused 'STAGE-REFUSED reason=none.*live-refs=1' "$out"
  # D3: secret-shaped -> refused without reading
  run stage "$R/.scratch/id_probe.pem"
  ck D3-secrets-refused 'reason=secrets-refusal' "$out"

  # S1: pushed receipt, full flow stage->check(hold)->release
  run --hold-seconds 0 stage "$R/keep/pushed.txt"
  ck S1-staged 'STAGED entry=.*receipt=pushed' "$out"
  local e1; e1=$(printf '%s' "$out" | sed -n 's/^STAGED entry=\([^ ]*\).*/\1/p')
  [ -e "$R/keep/pushed.txt" ] && { fail=$((fail+1)); echo "FAIL S1b origin-still-present"; } || { pass=$((pass+1)); echo "PASS S1b origin-unlinked"; }
  run check "$e1"
  ck S1c-check-pass 'CHECK result=PASS entry=.*pushed-intro=' "$out"
  run release "$e1"
  ck S1d-released 'RELEASED entry=.*receipt=pushed' "$out"
  [ -d "$T/.ufo-quarantine/$e1" ] && { fail=$((fail+1)); echo "FAIL S1e entry-still-there"; } || { pass=$((pass+1)); echo "PASS S1e entry-removed"; }
  grep -q '^RELEASED' "$T/.ufo-quarantine/RELEASES.log" 2>/dev/null && { pass=$((pass+1)); echo "PASS S1f releases-log"; } || { fail=$((fail+1)); echo "FAIL S1f releases-log"; }

  # S2: stale receipt, full flow; release re-check must see refs=0
  run --hold-seconds 0 --stale-days 1 stage "$R/.scratch/old-s12.out"
  ck S2-staged 'STAGED entry=.*receipt=stale' "$out"
  local e2; e2=$(printf '%s' "$out" | sed -n 's/^STAGED entry=\([^ ]*\).*/\1/p')
  run check "$e2"
  ck S2b-check-pass 'CHECK result=PASS entry=.*stale-refs=0' "$out"
  run release "$e2"
  ck S2c-released 'RELEASED entry=.*receipt=stale' "$out"

  # S3: obsidian receipt, full flow
  run --hold-seconds 0 stage "$R/notes/moved.md"
  ck S3-staged 'STAGED entry=.*receipt=moved-to-obsidian' "$out"
  local e3; e3=$(printf '%s' "$out" | sed -n 's/^STAGED entry=\([^ ]*\).*/\1/p')
  run check "$e3"
  ck S3b-check-pass 'CHECK result=PASS entry=.*vault-hash-ok' "$out"
  run release "$e3"
  ck S3c-released 'RELEASED entry=.*receipt=moved-to-obsidian' "$out"

  # H1: hold not expired -> HOLD, release refused
  printf 'held\n' >"$R/.scratch/held.out"; touch -d '3 days ago' "$R/.scratch/held.out"
  run --hold-seconds 3600 stage "$R/.scratch/held.out"
  ck H1-staged 'STAGED entry=.*receipt=stale' "$out"
  local e4; e4=$(printf '%s' "$out" | sed -n 's/^STAGED entry=\([^ ]*\).*/\1/p')
  run check "$e4"
  ck H1b-hold 'CHECK result=HOLD' "$out"
  run release "$e4"
  ck H1c-release-refused 'RELEASE-REFUSED' "$out"
  [ -e "$T/.ufo-quarantine/$e4/payload/held.out" ] && { pass=$((pass+1)); echo "PASS H1d payload-intact"; } || { fail=$((fail+1)); echo "FAIL H1d payload-intact"; }

  # R1: restore puts the payload back byte-identical
  run restore "$e4"
  ck R1-restored 'RESTORED entry=' "$out"
  [ "$(file_sha "$R/.scratch/held.out")" = "$(printf 'held\n' | sha256sum | cut -d' ' -f1)" ] \
    && { pass=$((pass+1)); echo "PASS R1b byte-identical"; } || { fail=$((fail+1)); echo "FAIL R1b byte-identical"; }

  # X1: origin recreated during hold -> second check FAILs, release refused
  printf 'held2\n' >"$R/.scratch/held2.out"; touch -d '3 days ago' "$R/.scratch/held2.out"
  run --hold-seconds 0 stage "$R/.scratch/held2.out"
  local e5; e5=$(printf '%s' "$out" | sed -n 's/^STAGED entry=\([^ ]*\).*/\1/p')
  printf 'someone recreated it\n' >"$R/.scratch/held2.out"
  run release "$e5"
  ck X1-recreated-fail 'RELEASE-REFUSED.*origin-recreated' "$out"
  # cleanup fixture for trap
  run restore "$e5" >/dev/null 2>&1 || true

  # D4: dry-run writes nothing anywhere (works outside allow-list too)
  run_env --dry-run stage "$R/.scratch/held.out"
  ck D4-dryrun 'DRY-RUN would-stage' "$out"

  # L1: dry-run over a LIVE fleet path — read-only, no writes
  local live="$REPO_ROOT/results/.write-probe"
  if [ -e "$live" ]; then
    run_env --dry-run stage "$live"
    ck L1-live-dryrun 'DRY-RUN would-stage|STAGE-REFUSED' "$out"
  else
    pass=$((pass+1)); echo "PASS L1-live-dryrun skipped(no live probe path)"
  fi

  printf 'selftest: %d checks, %d failed (fixture=%s)\n' "$((pass+fail))" "$fail" "$T"
  [ "$fail" -eq 0 ]
}

# --- arg parsing -----------------------------------------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --hold-seconds) HOLD_SECONDS=$2; shift 2 ;;
    --stale-days) STALE_DAYS=$2; shift 2 ;;
    --root) ROOT=$(canon "$2"); shift 2 ;;
    -h|--help) usage 0 ;;
    stage|check|release|restore|status)
      SUBCMD=$1; shift
      [ $# -gt 0 ] && { TARGET=$1; shift; }
      ;;
    *) usage_err "unknown arg: $1" ;;
  esac
done

: "${ROOT:=${SOUJI_QUARANTINE_ROOT:-$PWD}}"
ROOT=$(canon "$ROOT")

if [ "${SELFTEST:-0}" = 1 ]; then selftest; exit $?; fi

case "$SUBCMD" in
  stage)   cmd_stage ;;
  status)  cmd_status "$TARGET" ;;
  check)   cmd_check ;;
  release) cmd_release ;;
  restore) cmd_restore ;;
  "")      usage_err "missing subcommand (stage|status|check|release|restore|--selftest)" ;;
esac
