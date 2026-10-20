#!/usr/bin/env bash
# souji-quarantine (impl-01) — the receipt-gated quarantine flow as a tool.
# souji-shokunin round 8, seat S01.
#
# Turn the r7 execution_plan_template into one bash tool. Receipt authority is
# tools/souji-verify.sh (the lane engine, invoked as a child with explicit
# SHOKUNIN_ROOT/SOUJI_LEDGER context — never re-implemented here). Removal
# authority stays with the operator/parent: this tool only ever deletes from
# inside <repo>/.ufo-quarantine/<utc-date>/, never from the live tree.
#
# CLI
#   tools/souji-quarantine.impl-01.sh [--dry-run] [--hold seconds]
#        [--list FILE] [--selftest] <repo> <target>...
#
#   <repo>     the git repo the targets belong to (must contain .git/).
#   <target>   path(s) inside <repo>; relative paths resolve from cwd.
#   --list F   targets come as TSV rows `path<TAB>receipt` (a literal
#              `path	receipt` header line is allowed and skipped). The
#              listed receipt is an authorization pin: stage 1 must re-derive
#              SAFE with EXACTLY that receipt, else NOT-AUTHORIZED
#              (receipt-mismatch). --list and positional targets are
#              exclusive. Malformed rows are usage errors (exit 2).
#   --hold N   hold window seconds between staging and the second check
#              (default 450; --hold 0 allowed for fixtures).
#   --dry-run  stage-1 verdicts are computed for real (the engine is
#              read-only); every later stage prints its exact commands plus
#              verdict predictions and NOTHING is created, moved or slept.
#   --selftest builds a mktemp fixture git fleet (tracked + untracked files
#              with pushed receipts via fake remote refs, stale scratch,
#              moved-to-obsidian ledger rows, a NOT-SAFE target and a tamper
#              case) and asserts full state transitions. Exit 0/1.
#
# Stages, per target
#   1  Receipt re-derivation: souji-verify must say SAFE with a receipt.
#      Otherwise the target is NOT-AUTHORIZED and is left untouched.
#      SAFE(metadata-prune) means there is no object to stage -> SKIPPED.
#      Extra pre-flight refusals (fail-closed, NOT-AUTHORIZED): secret-shaped
#      paths, symlinks, targets outside <repo>, targets under
#      .ufo-quarantine/ or .git/, quarantine-path collisions, and tracked
#      targets whose worktree copy is dirty (r7 gate2; the pushed receipt
#      pins commits, not uncommitted edits).
#   2  Stage: mkdir -p <repo>/.ufo-quarantine/<utc-date>/ and move the target
#      there preserving its repo-relative path. Tracked files: `git mv`
#      (index records the rename; this tool never commits). Untracked: plain
#      `mv`.
#   3  Hold window (--hold seconds, default 450).
#   4  SECOND receipt re-derivation from quarantine, two prongs:
#      prong1  souji-verify is re-run against the quarantine path with the
#              original repo context. For the stale class the receipt is
#              path-local (the .scratch component and the mtime survive the
#              move) so prong1 SAFE(stale) is BINDING there. For pushed and
#              moved-to-obsidian the receipt is keyed to the ORIGINAL path
#              (introducing commit / ledger row), so a prong1 NOT-SAFE is
#              expected and recorded as `prong1-tolerated
#              class-not-path-local`, and prong2 carries the re-derivation.
#      prong2  class-aware re-derivation against the original context:
#              pushed           - current default-origin ancestry holds, no
#                                 unpushed commit touches the original rel
#                                 path, and quarantine bytes match the intro blob.
#              moved-to-obsidian- ledger row still resolves without ledger
#                                 drift during rechecking; quarantine bytes hash
#                                 to source_sha256 AND the vault copy still
#                                 hashes to vault_sha256 (dirs: manifest digests,
#                                 symlink-present fails closed).
#      Universal pins for every class: quarantine content digest == stage-1
#      content digest, and mtime unchanged. Any pin/prong failure -> the
#      second check FAILS.
#   5  Delete from quarantine only if the second check PASSED (rm of the
#      staged copy; after a git-mv staging the index entry of the quarantine
#      path is dropped best-effort so the net index shows the original as
#      staged-deleted; empty quarantine date dirs are rmdir'd). On failure the
#      copy STAYS in quarantine and the target is reported ABORTED.
#
# Output: one token per stage, TAB-separated (fields are sanitized):
#   QVERDICT	stage1	<path>	SAFE|NOT-SAFE	<receipt>	<evidence>
#   QSTAGE	stage2	<path>	<method>	<quarantine-path>
#   QSTAGE	stage3	<path>	<seconds>
#   QVERDICT	stage4-prong1	<qpath>	SAFE|NOT-SAFE	<receipt>	<evidence>
#   QVERDICT	stage4-second	<path>	PASS|FAIL	<class-evidence>
#   QSTAGE	stage5	<path>	DELETED|ABORTED	<evidence>
#   CMD	<path>	<command that would run / ran>
#   RESULT	<path>	DELETED|ABORTED|NOT-AUTHORIZED|SKIPPED|
#                   STAGE2-FAILED|DRY-RUN-PASS|DRY-RUN-BLOCKED
#                	<receipt|reason>	<evidence>
#   SUMMARY	total=N deleted=N aborted=N unauthorized=N skipped=N
#                	stage2failed=N dryrun-pass=N dryrun-blocked=N
#
# Exit codes: 0 = every target ended DELETED/SKIPPED/DRY-RUN-PASS;
#             1 = internal error; 2 = usage;
#             3 = at least one target NOT-AUTHORIZED, ABORTED or
#                 STAGE2-FAILED (or DRY-RUN-BLOCKED under --dry-run);
#             4 = live-fleet guard refusal (see below). No other codes.
#
# Safety rails
#   * Live-fleet guard: mutation (any non-dry-run invocation) is refused with
#     exit 4 when <repo> lies inside the live fleet root (the parent of this
#     repo) unless SOUJI_QUARANTINE_ALLOW_LIVE=1 is set explicitly.
#     --dry-run is always allowed anywhere (it changes nothing).
#   * Nothing is ever deleted outside <repo>/.ufo-quarantine/. The original
#     tree is only mutated by the stage-2 move.
#   * Secret-shaped basenames (*.env, .env.*, .envrc, *credential*, *secret*,
#     id_*, *.pem) are refused before anything is read or moved.
#   * No fetch/push/rebase/history rewrite is ever executed; on fixtures the
#     only index ops are mv/rm --cached. The tool never commits.
#   * .ufo/state and .ufo/watchdog.log are never read; no secret-shaped file
#     is read.
#
# Q8 bounds (r13)
#   Every per-target staging move and digest runs under a fixed GNU
#   `timeout --kill-after=10` bound: file digest 120s, directory digest 300s,
#   staging mv/git-mv 60s, receipt engine 120s, special-file scan 60s.
#   Hitting a bound is fail-closed: stage 1 -> NOT-AUTHORIZED
#   (digest-timeout / engine-error), stage 2 -> STAGE2-FAILED
#   (mv-timeout / git-mv-timeout) with the original and any partial
#   quarantine residue reported and never auto-undone; stage 4 -> ABORTED
#   (pin=FAIL digest-timeout). A staging/pin timeout never advances to
#   deletion. A timed-out git mv may leave <repo>/.git/index.lock: reported,
#   NEVER removed here. Stage-5 deletion is not newly time-bounded by Q8.
#   Digest targets must be regular files or directories whose whole subtree
#   is regular files + directories. Symlink/FIFO/socket/device targets and
#   descendants are refused before any read (stage-1 pre-flight), and
#   staging requires target and quarantine on one device (`stat -c %d`):
#   a cross-device mv would copy-then-unlink, so a bound hit could leave the
#   LIVE source half-removed. Cross-device staging is NOT-AUTHORIZED.
#
# Env
#   SOUJI_VERIFY_BIN            receipt-engine override for fixtures (default:
#                               this tool's repo tools/souji-verify.sh; there
#                               is no sibling-candidate fallback — QUALITY Q6)
#   SOUJI_Q_SHOKUNIN_ROOT       fleet root handed to the engine (default:
#                               parent dir of <repo>)
#   SOUJI_Q_LEDGER              ledger handed to the engine (default: this
#                               repo's corpus/knowledge/obsidian-ledger.tsv)
#   SOUJI_Q_STALE_DAYS          engine --stale-days (default 1)
#   SOUJI_QUARANTINE_ALLOW_LIVE set to 1 to mutate a live-fleet repo anyway
#   SOUJI_Q_TEST_HOOK           test-only hook (script; $1 = quarantine path)
#                               executed right after staging; honored only
#                               when SOUJI_Q_SELFTEST_ACTIVE=1 (selftest
#                               children).
set -euo pipefail
export LC_ALL=C

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
LIVE_FLEET_ROOT="$(dirname -- "$REPO_ROOT")"

# Q6 (r13): the receipt engine is ALWAYS the installed tree's
# tools/souji-verify.sh unless the operator pins SOUJI_VERIFY_BIN (fixtures
# do). The r10-era automatic cand-merge-verify.sh fallback is removed: it
# silently selected sibling candidate bytes that are not the installed
# engine, so a no-relay verdict measured a relay candidate instead of the
# bytes it certified (round-11 relay defect; QUALITY Q6). Selection must
# never depend on which candidate happens to sit next to this tool.
VERIFY_BIN="${SOUJI_VERIFY_BIN:-$REPO_ROOT/tools/souji-verify.sh}"
LEDGER_DEFAULT="$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"

HOLD=450
DRYRUN=0
SELFTEST=0
LIST_FILE=""
REPO=""
TARGETS=()
STALE_DAYS="${SOUJI_Q_STALE_DAYS:-1}"

SV_ROOT=""
SV_LEDGER=""
RC=0
N_TOTAL=0 N_DELETED=0 N_ABORTED=0 N_UNAUTH=0 N_SKIPPED=0 N_S2FAIL=0
N_DRYPASS=0 N_DRYBLOCK=0

V_RAW="" V_VERDICT=ERROR V_RECEIPT=engine-error V_EV=not-run
ERRTMP=""

usage() { sed -n '2,139p' "$SELF" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
usage_err() { printf 'souji-quarantine: %s\n' "$1" >&2; usage 2; }

canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

sanitize_field() {
  local s=${1:-}
  s=${s//$'\t'/ }; s=${s//$'\n'/ }; s=${s//$'\r'/ }
  printf '%s' "$s"
}

is_secret_shaped() { # any component in the r2 refusal list
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

emit() { # any number of fields, TAB-joined, sanitized
  local out="" f
  for f in "$@"; do
    f=$(sanitize_field "$f")
    if [ -z "$out" ]; then out=$f; else out="$out"$'\t'"$f"; fi
  done
  printf '%s\n' "$out"
}

# ------------------------------------------------------ stage machinery ----

git_tracked() { # $1 repo $2 repo-relative path -> 0 when tracked in HEAD/index
  git -C "$1" ls-files --error-unmatch -- "$2" >/dev/null 2>&1
}

git_dirty_tracked() { # $1 repo $2 rel -> porcelain output (may be empty)
  git -C "$1" --no-optional-locks status --porcelain -- "$2" 2>/dev/null || true
}

ledger_row_for() { # $1 canon source path -> "ss<TAB>vp<TAB>vs" or empty
  local want=$1 row sp ss vp vs crlf
  [ -f "$SV_LEDGER" ] || return 0
  while IFS= read -r row || [ -n "$row" ]; do
    crlf=${row%$'\r'}
    [ -n "$crlf" ] || continue
    case "$crlf" in source_path$'\t'*) continue ;; esac
    IFS=$'\t' read -r sp ss vp vs _rest <<< "$crlf"
    [ -n "$sp" ] || continue
    [ "$(canon_path "$sp")" = "$want" ] || continue
    printf '%s\t%s\t%s\n' "${ss:-}" "${vp:-}" "${vs:-}"
    return 0
  done <"$SV_LEDGER"
  return 0
}

q_default_ref() {
  local repo=$1 ref refs only="" line
  ref=$(git -C "$repo" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null) || ref=""
  case "$ref" in
    refs/remotes/origin/*)
      if git -C "$repo" show-ref --verify --quiet "$ref" 2>/dev/null; then
        printf '%s\n' "$ref"; return 0
      fi ;;
  esac
  refs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null) || return 1
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    [ "$line" = refs/remotes/origin/HEAD ] && continue
    [ -z "$only" ] || return 1
    only=$line
  done <<< "$refs"
  [ -n "$only" ] || return 1
  printf '%s\n' "$only"
}

# second_check: prong1 + prong2 + pins for one staged target.
# In:  CT QPATH REL CLASS PIN_SHA PIN_MTIME METHOD (globals set by caller)
# Out: SC_PASS=1|0, SC_EV (evidence string)
s18_second_check() {
  SC_PASS=0
  local ev="" ok=1
  local now_sha="" now_mtime dig_rc=0
  now_sha=$(content_digest "$QPATH") || dig_rc=$?
  now_mtime=$(stat -c %Y -- "$QPATH" 2>/dev/null || true)
  if [ "$dig_rc" -eq 0 ] && [ -n "$now_sha" ] && [ "$now_sha" = "$PIN_SHA" ]; then
    ev="pin=ok"
  else
    ok=0
    case "$dig_rc" in
      2) ev="pin=FAIL symlink-present-in-quarantine" ;;
      124|137) ev="pin=FAIL digest-timeout rc=$dig_rc" ;;
      *) ev="pin=FAIL digest-mismatch stage1=${PIN_SHA:0:12} now=${now_sha:0:12}" ;;
    esac
  fi
  if [ -n "$now_mtime" ] && [ "$now_mtime" = "$PIN_MTIME" ]; then
    ev="$ev mtime=ok"
  else
    ok=0
    ev="$ev mtime=FAIL stage1=$PIN_MTIME now=${now_mtime:-none}"
  fi

  local intro="" blob_sha="" unpushed_n="" row ss vp vs vault_sha vault_rc=0 ledger_pin=""
  case "$CLASS" in
    pushed)
      intro=$(git -C "$CREPO" log --diff-filter=A --format=%H -1 -- "$REL" 2>/dev/null | head -1 || true)
      if [ -z "$intro" ]; then
        ok=0; ev="$ev class=FAIL no-introducing-commit"
      else
        ev="$ev intro=${intro:0:12}"
        local current_ref
        if current_ref=$(q_default_ref "$CREPO") && git -C "$CREPO" merge-base --is-ancestor "$intro" "$current_ref" 2>/dev/null; then
          ev="$ev default-ref=ok"
        else
          ok=0; ev="$ev class=FAIL default-ref-unverifiable-or-not-ancestor"
        fi
        if unpushed_n=$(git -C "$CREPO" log --branches --not --remotes --oneline -- "$REL" 2>/dev/null | wc -l); then
          unpushed_n=${unpushed_n// /}
        else
          unpushed_n=unverifiable
        fi
        if [ "${unpushed_n:-1}" = 0 ]; then
          ev="$ev unpushed-touching=0"
        else
          ok=0; ev="$ev class=FAIL unpushed-touching=$unpushed_n"
        fi
        if [ "$ISDIR" = 0 ]; then
          blob_sha=$(git -C "$CREPO" cat-file blob "$intro:$REL" 2>/dev/null | timeout --kill-after=10 120 sha256sum | cut -d' ' -f1 || true)
          if [ -n "$blob_sha" ] && [ "$blob_sha" = "$PIN_SHA" ]; then
            ev="$ev intro-blob=ok"
          else
            ok=0; ev="$ev class=FAIL intro-blob-mismatch blob=${blob_sha:0:12}"
          fi
        else
          ev="$ev intro-blob=dir-pin-only"
        fi
      fi
      ;;
    moved-to-obsidian)
      ledger_pin=$(file_sha "$SV_LEDGER") || ledger_pin=""
      row=$(ledger_row_for "$CT")
      if [ -z "$row" ]; then
        ok=0; ev="$ev class=FAIL ledger-row-gone"
      else
        ss=${row%%$'\t'*}; local rest=${row#*$'\t'}
        vp=${rest%%$'\t'*}; vs=${rest#*$'\t'}
        if [ "$ISDIR" = 0 ]; then
          vault_sha=$(file_sha "$vp") || vault_sha=""
          if [ -n "$ss" ] && [ "$now_sha" = "$ss" ]; then ev="$ev source-sha=ok"; else ok=0; ev="$ev class=FAIL source-sha-mismatch"; fi
          if [ -n "$vs" ] && [ "$vault_sha" = "$vs" ]; then ev="$ev vault-sha=ok"; else ok=0; ev="$ev class=FAIL vault-sha-mismatch vault=${vp:-none}"; fi
        else
          vault_sha=$(dir_digest "$vp") || vault_rc=$?
          if [ "$vault_rc" -eq 2 ]; then vault_sha=""; fi
          if [ -n "$ss" ] && [ "$now_sha" = "$ss" ]; then ev="$ev source-digest=ok"; else ok=0; ev="$ev class=FAIL source-digest-mismatch"; fi
          if [ -n "$vs" ] && [ "$vault_sha" = "$vs" ]; then ev="$ev vault-digest=ok"; else ok=0; ev="$ev class=FAIL vault-digest-mismatch vault=${vp:-none}"; fi
        fi
      fi
      ;;
    stale)
      # prong1 IS the re-derivation for this class (checked below)
      ev="$ev class=stale-via-prong1"
      ;;
    *)
      ok=0; ev="$ev class=FAIL unknown-receipt-$CLASS"
      ;;
  esac

  if [ "$CLASS" = moved-to-obsidian ]; then
    if [ -z "$ledger_pin" ] || [ "$(file_sha "$SV_LEDGER")" != "$ledger_pin" ]; then
      ok=0; ev="$ev class=FAIL ledger-changed"
    fi
  fi

  # prong1 verdict was stored by the caller in P1_VERDICT/P1_RECEIPT/P1_EV.
  if [ "$CLASS" = stale ]; then
    if [ "$P1_VERDICT" = SAFE ] && [ "$P1_RECEIPT" = stale ]; then
      ev="$ev prong1=SAFE(stale) binding"
    else
      ok=0
      ev="$ev class=FAIL prong1=$P1_VERDICT($P1_RECEIPT) expected-SAFE(stale)"
    fi
  else
    ev="$ev prong1=$P1_VERDICT($P1_RECEIPT) prong1-tolerated class-not-path-local"
  fi

  SC_PASS=$ok
  SC_EV=${ev# }
  return 0
}

block_one() { # $1 raw path, $2 receipt/reason, $3 evidence — refusal result
  if [ "$DRYRUN" = 1 ]; then
    emit RESULT "$1" DRY-RUN-BLOCKED "$2" "$3"
    N_DRYBLOCK=$((N_DRYBLOCK + 1))
  else
    emit RESULT "$1" NOT-AUTHORIZED "$2" "$3"
    N_UNAUTH=$((N_UNAUTH + 1))
  fi
  RC=3
  return 0
}

# flow_one: run all stages for one target.
# $1 raw target path, $2 listed receipt ("" when none)
s18_flow_one() {
  local raw=$1 listed=${2:-}
  case "$raw" in
    /*) : ;;
    *) raw="$REPO/$raw" ;;   # repo-relative targets
  esac
  N_TOTAL=$((N_TOTAL + 1))

  run_verify "$raw"
  emit QVERDICT stage1 "$raw" "$V_VERDICT" "$V_RECEIPT" "$V_EV"
  if [ "$V_VERDICT" != SAFE ]; then
    block_one "$raw" "$V_RECEIPT" "stage1=$V_VERDICT($V_RECEIPT)"
    return 0
  fi
  local class=$V_RECEIPT stage1_ev=$V_EV
  if [ "$class" = metadata-prune ]; then
    emit RESULT "$raw" SKIPPED metadata-prune "nothing-to-stage stage1=$stage1_ev"
    N_SKIPPED=$((N_SKIPPED + 1))
    return 0
  fi
  if [ -n "$listed" ] && [ "$listed" != "$class" ]; then
    block_one "$raw" receipt-mismatch "listed=$listed engine=$class"
    return 0
  fi
  case "$class" in
    pushed|moved-to-obsidian|stale) : ;;
    *)
      block_one "$raw" "unexpected-receipt-$class" "$stage1_ev"
      return 0 ;;
  esac

  local ct crepo rel qdate qdir qpath
  ct=$(canon_path "$raw")
  if is_secret_shaped "$ct"; then
    block_one "$raw" secrets-refusal "secret-shaped path component"
    return 0
  fi
  crepo=$Q_CREPO
  if [ "$ct" = "$crepo" ]; then
    block_one "$raw" target-is-repo-root ""
    return 0
  fi
  case "$ct" in
    "$crepo"/*) rel=${ct#"$crepo"/} ;;
    *)
      block_one "$raw" outside-repo "repo=$crepo"
      return 0 ;;
  esac
  case "$rel" in
    .ufo-quarantine|.ufo-quarantine/*|.git|.git/*)
      block_one "$raw" forbidden-prefix "$rel"
      return 0 ;;
    ''|.*/*|./*)
      : ;;
  esac
  case "$rel" in
    */..*|*../*)
      block_one "$raw" dotdot-in-relpath "$rel"
      return 0 ;;
  esac
  qdate=$(date -u +%F)
  qdir="$crepo/.ufo-quarantine/$qdate"
  qpath="$qdir/$rel"

  if [ ! -e "$ct" ] && [ ! -L "$ct" ]; then
    block_one "$raw" unreachable "missing path"
    return 0
  fi
  if [ -L "$raw" ] || [ -L "$ct" ]; then
    block_one "$raw" symlink-refused ""
    return 0
  fi
  if [ -e "$qpath" ] || [ -L "$qpath" ]; then
    block_one "$raw" quarantine-collision "$qpath"
    return 0
  fi

  local isdir=0
  [ -d "$ct" ] && isdir=1

  local tracked=0 method=mv
  if git_tracked "$crepo" "$rel"; then
    tracked=1; method=git-mv
    local st
    st=$(git_dirty_tracked "$crepo" "$rel")
    if [ -n "$st" ]; then
      block_one "$raw" dirty-tracked \
        "r7-gate2 porcelain=$(printf '%s' "$st" | head -1)"
      return 0
    fi
  fi

  local pin_sha="" pin_mtime pin_rc=0
  pin_sha=$(content_digest "$ct") || pin_rc=$?
  if [ "$pin_rc" -ne 0 ] || [ -z "$pin_sha" ]; then
    case "$pin_rc" in
      2) block_one "$raw" special-file-refused "stage1-pin $(q_special_detail "$ct")" ;;
      124|137) block_one "$raw" digest-timeout "stage1-pin rc=$pin_rc bound=120s-file/300s-dir" ;;
      *) block_one "$raw" digest-failed "stage1-pin rc=$pin_rc" ;;
    esac
    return 0
  fi
  pin_mtime=$(stat -c %Y -- "$ct" 2>/dev/null || true)

  CT=$ct CREPO=$crepo REL=$rel QPATH=$qpath CLASS=$class ISDIR=$isdir
  PIN_SHA=$pin_sha PIN_MTIME=$pin_mtime METHOD=$method

  if [ "$DRYRUN" = 1 ]; then
    emit CMD "$raw" "mkdir -p -- $(printf '%q' "$qdir/$(dirname -- "$rel")")"
    if [ "$tracked" = 1 ]; then
      emit CMD "$raw" "timeout --kill-after=10 60 git -C $(printf '%q' "$crepo") mv -- $(printf '%q' "$rel") $(printf '%q' "$qpath")"
    else
      emit CMD "$raw" "timeout --kill-after=10 60 mv --no-copy -T -- $(printf '%q' "$ct") $(printf '%q' "$qpath")"
    fi
    emit CMD "$raw" "sleep $HOLD   # hold window"
    emit CMD "$raw" "receipt engine second check on $(printf '%q' "$qpath") (context repo=$crepo)"
    if [ "$tracked" = 1 ]; then
      emit CMD "$raw" "git -C $(printf '%q' "$crepo") rm --cached --quiet -- $(printf '%q' "$qpath")   # after rm"
    fi
    emit CMD "$raw" "rm -rf -- $(printf '%q' "$qpath")"
    emit RESULT "$raw" DRY-RUN-PASS "$class" "stage1=$stage1_ev"
    N_DRYPASS=$((N_DRYPASS + 1))
    return 0
  fi

  # ---- stage 2: stage into quarantine (bounded) ---------------------------
  if ! mkdir -p -- "$qdir/$(dirname -- "$rel")" 2>/dev/null; then
    emit RESULT "$raw" STAGE2-FAILED mkdir-failed "qdir=$qdir"
    N_S2FAIL=$((N_S2FAIL + 1)); RC=3
    return 0
  fi
  local mv_rc=0
  if [ "$tracked" = 1 ]; then
    timeout --kill-after=10 60 git -C "$crepo" mv -- "$rel" "$qpath" 2>"$ERRTMP" || mv_rc=$?
  else
    timeout --kill-after=10 60 mv --no-copy -T -- "$ct" "$qpath" 2>"$ERRTMP" || mv_rc=$?
  fi
  if [ "$mv_rc" -ne 0 ]; then
    q_stage2_fail "$raw" "$method" "$mv_rc" "$ct" "$qpath" "$crepo"
    return 0
  fi
  emit QSTAGE stage2 "$raw" "$method" "$qpath"

  # test-only hook (fixtures): simulate tampering between stage 2 and 4
  if [ -n "${SOUJI_Q_TEST_HOOK:-}" ] && [ "${SOUJI_Q_SELFTEST_ACTIVE:-}" = "1" ]; then
    if ! bash "$SOUJI_Q_TEST_HOOK" "$qpath" 2>"$ERRTMP"; then
      emit QSTAGE stage2-hook "$raw" hook-failed \
        "$(sanitize_field "$(head -c 200 "$ERRTMP" || true)")"
    fi
  fi

  # ---- stage 3: hold window -----------------------------------------------
  emit QSTAGE stage3 "$raw" "$HOLD"
  if [ "$HOLD" -gt 0 ]; then
    sleep "$HOLD"
  fi

  # ---- stage 4: second receipt re-derivation ------------------------------
  run_verify "$qpath"
  P1_VERDICT=$V_VERDICT P1_RECEIPT=$V_RECEIPT P1_EV=$V_EV
  emit QVERDICT stage4-prong1 "$qpath" "$P1_VERDICT" "$P1_RECEIPT" "$P1_EV"

  second_check
  if [ "$SC_PASS" = 1 ]; then
    emit QVERDICT stage4-second "$raw" PASS "$SC_EV"
  else
    emit QVERDICT stage4-second "$raw" FAIL "$SC_EV"
    emit QSTAGE stage5 "$raw" ABORTED "left-in-quarantine qpath=$qpath"
    emit RESULT "$raw" ABORTED "$class" "$SC_EV"
    N_ABORTED=$((N_ABORTED + 1)); RC=3
    return 0
  fi

  # ---- stage 5: delete only after the successful second check -------------
  if ! rm -rf -- "$qpath" 2>/dev/null; then
    emit QSTAGE stage5 "$raw" ABORTED "rm-failed residue-may-be-partial qpath=$qpath"
    emit RESULT "$raw" ABORTED "$class" "rm-failed residue-may-be-partial $SC_EV"
    N_ABORTED=$((N_ABORTED + 1)); RC=3
    return 0
  fi
  if [ "$tracked" = 1 ]; then
    git -C "$crepo" rm --cached --quiet -- "$qpath" 2>/dev/null || \
      emit QSTAGE stage5-index "$raw" index-cleanup-skipped "$qpath"
  fi
  # prune now-empty parents of the staged copy up to (not including) qdir
  local rmp="$(dirname -- "$qpath")"
  while [ "$rmp" != "$qdir" ] && [ "$rmp" != "$crepo" ] && [ "$rmp" != "/" ]; do
    rmdir --ignore-fail-on-non-empty "$rmp" 2>/dev/null || break
    rmp=$(dirname -- "$rmp")
  done
  rmdir --ignore-fail-on-non-empty "$qdir" 2>/dev/null || true
  rmdir --ignore-fail-on-non-empty "$crepo/.ufo-quarantine" 2>/dev/null || true
  emit QSTAGE stage5 "$raw" DELETED "second-check=pass receipt=$class"
  emit RESULT "$raw" DELETED "$class" "$SC_EV"
  N_DELETED=$((N_DELETED + 1))
  return 0
}

run_mode() {
  SV_ROOT="${SOUJI_Q_SHOKUNIN_ROOT:-$(dirname -- "$(canon_path "$REPO")")}"
  SV_LEDGER="${SOUJI_Q_LEDGER:-$LEDGER_DEFAULT}"
  Q_CREPO=$(canon_path "$REPO")

  if [ ! -d "$Q_CREPO/.git" ]; then
    usage_err "not a git repo: $REPO"
  fi
  if [ ! -f "$VERIFY_BIN" ]; then
    printf 'souji-quarantine: receipt engine missing: %s\n' "$VERIFY_BIN" >&2
    exit 1
  fi

  # Live-fleet guard: mutation inside the real fleet is refused unless the
  # operator says so explicitly. Dry-run (runbook) is always allowed.
  if [ "$DRYRUN" = 0 ]; then
    case "$Q_CREPO" in
      "$LIVE_FLEET_ROOT" | "$LIVE_FLEET_ROOT"/*)
        if [ "${SOUJI_QUARANTINE_ALLOW_LIVE:-}" = "1" ]; then
          emit GUARD note live-fleet-overridden "SOUJI_QUARANTINE_ALLOW_LIVE=1 repo=$Q_CREPO"
        else
          emit GUARD refusal live-fleet-mutation-forbidden \
            "repo=$Q_CREPO fleet=$LIVE_FLEET_ROOT re-run-with---dry-run-or-set-SOUJI_QUARANTINE_ALLOW_LIVE=1"
          exit 4
        fi ;;
    esac
  else
    case "$Q_CREPO" in
      "$LIVE_FLEET_ROOT" | "$LIVE_FLEET_ROOT"/*)
        emit GUARD note live-fleet-dry-run "no mutation will occur repo=$Q_CREPO" ;;
    esac
  fi

  if [ -n "$LIST_FILE" ]; then
    local nul_prefix
    if IFS= read -r -d '' nul_prefix <"$LIST_FILE"; then
      usage_err "list contains a NUL byte"
    fi
    local line n=0 path rcpt header_skipped=0
    while IFS= read -r line || [ -n "$line" ]; do
      line=${line%$'\r'}
      [ -n "$line" ] || continue
      if [ "$header_skipped" = 0 ] && [ "$line" = "path"$'\t'"receipt" ]; then
        header_skipped=1
        continue
      fi
      case "$line" in
        *$'\t'*) path=${line%%$'\t'*}; rcpt=${line#*$'\t'} ;;
        *) usage_err "list row without receipt column: $line" ;;
      esac
      case "$rcpt" in
        *$'\t'*|'') usage_err "list row malformed: $line" ;;
      esac
      flow_one "$path" "$rcpt"
      n=$((n + 1))
    done <"$LIST_FILE"
    [ "$n" -gt 0 ] || usage_err "list file has no rows: $LIST_FILE"
  else
    local t
    for t in "${TARGETS[@]}"; do
      flow_one "$t" ""
    done
  fi

  emit SUMMARY "total=$N_TOTAL" "deleted=$N_DELETED" "aborted=$N_ABORTED" \
    "unauthorized=$N_UNAUTH" "skipped=$N_SKIPPED" "stage2failed=$N_S2FAIL" \
    "dryrun-pass=$N_DRYPASS" "dryrun-blocked=$N_DRYBLOCK"
  return 0
}

# ------------------------------------------------------------- selftest ----

ST_TMP="" ST_FLEET="" ST_REPO="" ST_LEDGER=""
ST_PASS=0 ST_FAIL=0

# cand-merge-quarantine.sh -- round-10 S15 composed candidate.
# S17 quarantine flow (NUL list gate, default-ref recheck, ledger pin,
# engine-record parsing) with the S18 shared hardening layer inlined after
# it. Renames: base flow_one -> s18_flow_one and base second_check ->
# s18_second_check, which the guard's containment wrappers delegate to.
# ---- S18 shared hardening (round-9 S18 guard), inlined by r10 S15 ----
S18_KIND=quarantine
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

# Q8 (r13): digests read regular files only and every read is bounded.
# file_sha propagates the bound status (124/137) so callers can report a
# timeout instead of a mismatch; 1 is unreadable, 2 is non-regular/symlink.
file_sha() {
  local out="" rc=0
  s18_path_ok "$1" && [ -f "$1" ] && [ ! -L "$1" ] || return 1
  out=$(timeout --kill-after=10 120 sha256sum -- "$1" 2>/dev/null) || { rc=$?; return "$rc"; }
  printf '%s' "${out%% *}"
}

# A directory digest hashes a whole subtree. One outer bound covers
# find/sort/xargs/sha256sum together, and GNU timeout signals the process
# group, so no grandchild survives the window (M44: orphaned sha256sum).
dir_digest() {
  local d=$1
  s18_path_ok "$d" && [ -d "$d" ] && s18_scope_ok "$d" || return 2
  timeout --kill-after=10 300 bash -c '
    set -o pipefail
    cd -- "$1" || exit 3
    find . -path ./.git -prune -o -type f -print0 \
      | LC_ALL=C sort -z | xargs -0 -r sha256sum | sha256sum | cut -d" " -f1
  ' _ "$d" 2>/dev/null
}

content_digest() { # $1 path -> digest on stdout
  # rc: 0 ok · 1 unreadable · 2 symlink/special (incl. descendants) ·
  #     124/137 bounded timeout · 3 dir unreadable
  local out="" rc=0
  if [ -L "$1" ]; then return 2; fi
  if [ -d "$1" ]; then
    out=$(dir_digest "$1") || { rc=$?; return "$rc"; }
    [ -n "$out" ] && printf '%s' "$out"
    return 0
  fi
  [ -f "$1" ] || return 2
  out=$(file_sha "$1") || { rc=$?; return "$rc"; }
  printf '%s' "$out"
}

q_special_type() { # $1 existing path -> type on stdout; rc 0 regular|directory
  local t
  if [ -L "$1" ]; then printf 'symlink'; return 1; fi
  t=$(stat -c %F -- "$1" 2>/dev/null) || { printf 'unstatable'; return 1; }
  case "$t" in
    'regular file'|'regular empty file'|directory) printf '%s' "$t"; return 0 ;;
  esac
  printf '%s' "${t// /-}"
  return 1
}

# Q8: a directory whose subtree holds a symlink, FIFO, socket or device is
# unstageable — the manifest digest cannot cover it (find -type f skips it)
# and a read could block. First offender on stdout; rc 2 = scan bound hit.
q_first_special() { # $1 dir -> offender path (maybe empty)
  local out="" rc=0
  out=$(timeout --kill-after=10 60 find "$1" -path "$1/.git" -prune -o \
    \( -type l -o -type p -o -type s -o -type b -o -type c \) -print -quit 2>/dev/null) || rc=$?
  if [ "$rc" -eq 124 ] || [ "$rc" -eq 137 ]; then
    printf 'scan-timeout'
    return 2
  fi
  if [ -n "$out" ]; then printf '%s' "$out"; return 1; fi
  if [ "$rc" -ne 0 ]; then printf 'scan-failed rc=%s' "$rc"; return 3; fi
  return 0
}

q_special_detail() { # $1 path -> short token naming why the digest refused it
  local t="" out=""
  t=$(q_special_type "$1" 2>/dev/null || true)
  case "$t" in
    directory)
      out=$(q_first_special "$1" 2>/dev/null || true)
      printf 'descendant=%s' "${out:-unknown}" ;;
    '') printf 'unstatable' ;;
    *) printf 'type=%s' "$t" ;;
  esac
}

# Stage-2 failure: report the bound status, the original's presence and any
# partial quarantine residue. Nothing is moved back and nothing is deleted.
q_stage2_fail() { # $1 raw $2 method $3 rc $4 source $5 qpath $6 repo
  local raw=$1 method=$2 rc=$3 ct=$4 qpath=$5 crepo=$6
  local residue=none source=absent reason ev
  if [ -e "$qpath" ] || [ -L "$qpath" ]; then residue=$qpath; fi
  if [ -e "$ct" ] || [ -L "$ct" ]; then source=present; fi
  if [ "$rc" -eq 124 ] || [ "$rc" -eq 137 ]; then
    reason="$method-timeout"
  else
    reason="$method-failed"
  fi
  ev="rc=$rc source=$source residue=$residue"
  if [ "$method" = git-mv ] \
    && { [ -e "$crepo/.git/index.lock" ] || [ -L "$crepo/.git/index.lock" ]; }; then
    ev="$ev index-lock=present-never-removed"
  fi
  ev="$ev stderr=$(sanitize_field "$(head -c 200 "$ERRTMP" 2>/dev/null || true)")"
  emit QSTAGE stage2-failed "$raw" "$reason" "$ev"
  emit RESULT "$raw" STAGE2-FAILED "$reason" "$ev"
  N_S2FAIL=$((N_S2FAIL + 1)); RC=3
  return 0
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
  local target=$1 isdir=$2 row source_sha vault_sha
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
  local target=$1 repo=$2 intro ref status touching
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
    if ! refs=$(git -C "$owner" for-each-ref --format='%(objectname)' 2>/dev/null); then
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
      timeout --kill-after=10 120 bash "$VERIFY_BIN" --stale-days "$STALE_DAYS" -- "$t" 2>"$ERRTMP") || rc=$?
    if [ "$rc" -eq 124 ] || [ "$rc" -eq 137 ]; then
      V_EV="receipt-engine-timeout rc=$rc bound=120s"
      return 0
    fi
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
    # Q8 pre-flight: digestable targets are regular files or directories
    # whose whole subtree is regular files + directories. Special files are
    # refused before any read or move, so a FIFO/device can neither block a
    # digest nor be staged. Missing paths still fall through to the engine
    # (metadata-prune/unreachable), and symlinks keep their own refusal.
    if [ -e "$raw" ] && [ ! -L "$raw" ]; then
      local spd="" sprc=0 ct_dev="" repo_dev=""
      if ! q_special_type "$raw" >/dev/null 2>&1; then
        N_TOTAL=$((N_TOTAL + 1))
        block_one "$raw" special-file-refused "$(q_special_detail "$raw")"
        return 0
      fi
      if [ -d "$raw" ]; then
        spd=$(q_first_special "$raw") || sprc=$?
        if [ "$sprc" -ne 0 ]; then
          N_TOTAL=$((N_TOTAL + 1))
          case "$sprc" in
            2) block_one "$raw" special-scan-timeout "bound=60s $spd" ;;
            3) block_one "$raw" special-scan-failed "$spd" ;;
            *) block_one "$raw" special-descendant "offender=$spd" ;;
          esac
          return 0
        fi
      fi
      # A cross-device mv would copy-then-unlink; if the bound fired during
      # the unlink the LIVE source could be left half-removed. Refuse.
      ct_dev=$(stat -c %d -- "$(dirname -- "$raw")" 2>/dev/null || true)
      repo_dev=$(stat -c %d -- "$Q_CREPO" 2>/dev/null || true)
      if [ -z "$ct_dev" ] || [ -z "$repo_dev" ] || [ "$ct_dev" != "$repo_dev" ]; then
        N_TOTAL=$((N_TOTAL + 1))
        block_one "$raw" cross-device-staging \
          "target-dev=${ct_dev:-unknown} repo-dev=${repo_dev:-unknown}"
        return 0
      fi
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
      local ref object touching intro
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
st_ok() { ST_PASS=$((ST_PASS + 1)); st_note "PASS $*"; }
st_bad() { ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $*"; }

st_check() { # $1 id, $2 ok(0/1), $3 detail
  if [ "$2" = 1 ]; then st_ok "$1 ($3)"; else st_bad "$1 ($3)"; fi
}

st_commit() { # $1 repo, $2 parent(sha|""), $3 message -> sha (plumbing only)
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

st_flow() { # $1 id, $2 want-rc, rest = tool args; sets ST_OUT ST_RC
  local id=$1 want=$2; shift 2
  local rc=0
  ST_OUT=$(env SOUJI_Q_SELFTEST_ACTIVE=1 SOUJI_Q_LEDGER="$ST_LEDGER" \
    "$SELF" --hold 0 "$@" 2>&1) || rc=$?
  ST_RC=$rc
  st_check "$id rc" "$([ "$ST_RC" = "$want" ] && echo 1 || echo 0)" \
    "got=$ST_RC want=$want"
  return 0
}

st_build_fixtures() {
  ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-quarantine-selftest.XXXXXX")
  ST_FLEET="$ST_TMP/fleet"
  ST_REPO="$ST_FLEET/qa-shokunin"
  ST_LEDGER="$ST_TMP/ledger.tsv"
  mkdir -p "$ST_FLEET"
  local R=$ST_REPO
  git init -q --initial-branch=master "$R"
  git -C "$R" symbolic-ref HEAD refs/heads/master

  # c1: tracked files that will earn pushed receipts
  mkdir -p "$R/keep" "$R/local"
  printf 'pushed payload 1\n' > "$R/keep/pushed.txt"
  printf 'pushed payload 2\n' > "$R/keep/pushed2.txt"
  printf 'dry-run payload\n' > "$R/keep/dry-pushed.txt"
  printf 'dirty base\n' > "$R/keep/dirty.txt"
  local c1; c1=$(st_commit "$R" "" "c1 tracked base")
  # fake remote refs -> pushed receipts are establishable
  git -C "$R" update-ref refs/remotes/origin/master "$c1"
  git -C "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$R" update-ref refs/heads/master "$c1"
  # c2: local-only commit touching local/unpushed.txt (NOT-SAFE candidate)
  printf 'local-only payload\n' > "$R/local/unpushed.txt"
  local c2; c2=$(st_commit "$R" "$c1" "c2 local-only work")
  git -C "$R" update-ref refs/heads/master "$c2"
  # dirty tracked file: committed at c1, modified in the worktree (gate2 FAIL)
  printf 'dirty base + uncommitted edit\n' > "$R/keep/dirty.txt"
  # clean branch for the metadata-prune registration (fully pushed)
  git -C "$R" update-ref refs/heads/wt-clean "$c1"
  local adm="$R/.git/worktrees/wt-inside"
  mkdir -p "$adm"
  printf 'ref: refs/heads/wt-clean\n' > "$adm/HEAD"
  printf '../..\n' > "$adm/commondir"
  printf '%s\n' "$R/wt-inside/.git" > "$adm/gitdir"

  # untracked fixtures (created AFTER the commits so add -A never saw them)
  mkdir -p "$ST_TMP/vault" "$R/.scratch"
  printf 'obsidian payload A\n' > "$R/keep/obs.txt"
  printf 'obsidian payload A\n' > "$ST_TMP/vault/obs.txt"
  printf 'obsidian payload B\n' > "$R/keep/obs2.txt"
  printf 'obsidian payload B\n' > "$ST_TMP/vault/obs2.txt"
  printf 'plain untracked note\n' > "$R/notes.txt"
  printf 'stale scratch junk\n' > "$R/.scratch/old-report.out"
  touch -d '3 days ago' "$R/.scratch/old-report.out"

  local fs
  fs=$(printf '%s\n' "$(file_sha "$R/keep/obs.txt")")
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-18\tselftest-A\n' \
      "$R/keep/obs.txt" "$fs" "$ST_TMP/vault/obs.txt" "$fs"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tselftest-B\n' \
      "$R/keep/obs2.txt" "$(file_sha "$R/keep/obs2.txt")" \
      "$ST_TMP/vault/obs2.txt" "$(file_sha "$R/keep/obs2.txt")"
  } > "$ST_LEDGER"
  return 0
}

run_selftest() {
  if [ "${SOUJI_Q_SELFTEST_ACTIVE:-0}" = "1" ]; then
    printf 'souji-quarantine: refusing nested --selftest\n' >&2
    exit 1
  fi
  command -v rg >/dev/null 2>&1 || { printf 'souji-quarantine: rg missing (engine dep)\n' >&2; exit 1; }
  st_build_fixtures
  trap 'rm -rf -- "$ST_TMP"; rm -f -- "$ERRTMP"' EXIT
  local R=$ST_REPO

  # live-lane sentinels: untouched before/after (H3)
  local live_porcelain_before live_log_sha_before live_q_before
  live_porcelain_before=$(git -C "$REPO_ROOT" --no-optional-locks status --porcelain 2>/dev/null | grep -c . || true)
  live_log_sha_before=$(file_sha "$REPO_ROOT/LOG.md")
  live_q_before=no
  [ -e "$REPO_ROOT/.ufo-quarantine" ] && live_q_before=yes

  local out=""

  # ---- G1: live-fleet guard (fires before anything else; no live reads) ---
  local grc=0
  out=$(env -u SOUJI_QUARANTINE_ALLOW_LIVE -u SOUJI_Q_LEDGER \
    "$SELF" --hold 0 "$REPO_ROOT" no-such-live-target.txt 2>&1) || grc=$?
  st_check "G1 guard rc=4" "$([ "$grc" = 4 ] && echo 1 || echo 0)" "got=$grc"
  st_check "G1 guard token" \
    "$(printf '%s' "$out" | grep -aq 'live-fleet-mutation-forbidden' && echo 1 || echo 0)" "guard line"
  st_check "G1 live lane untouched" \
    "$([ "$(file_sha "$REPO_ROOT/LOG.md")" = "$live_log_sha_before" ] && echo 1 || echo 0)" "sha"

  # ---- D1: dry-run authorized target changes nothing ----------------------
  st_flow "D1 dry-run pushed" 0 --dry-run "$R" keep/dry-pushed.txt
  out=$ST_OUT
  st_check "D1 result token" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'RESULT\t%s\tDRY-RUN-PASS\tpushed' "$R/keep/dry-pushed.txt")" && echo 1 || echo 0)" \
    "DRY-RUN-PASS pushed"
  st_check "D1 prints commands" \
    "$(printf '%s' "$out" | grep -aqF 'git -C' && printf '%s' "$out" | grep -aqF 'rm -rf' && echo 1 || echo 0)" "CMD lines"
  st_check "D1 no quarantine dir" "$([ ! -e "$R/.ufo-quarantine" ] && echo 1 || echo 0)" "absent"
  st_check "D1 file still present" "$([ -f "$R/keep/dry-pushed.txt" ] && echo 1 || echo 0)" "present"

  # ---- D2: dry-run NOT-SAFE target is blocked -----------------------------
  st_flow "D2 dry-run NOT-SAFE" 3 --dry-run "$R" local/unpushed.txt
  out=$ST_OUT
  st_check "D2 blocked token" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'RESULT\t%s\tDRY-RUN-BLOCKED' "$R/local/unpushed.txt")" && echo 1 || echo 0)" \
    "DRY-RUN-BLOCKED"

  # ---- D3: dry-run --list with one pass + one receipt mismatch ------------
  local LF="$ST_TMP/list-mixed.tsv"
  printf 'path\treceipt\n' > "$LF"
  printf '%s\tpushed\n' "$R/keep/dry-pushed.txt" >> "$LF"
  printf '%s\tstale\n' "$R/keep/obs.txt" >> "$LF"
  st_flow "D3 dry-run list mixed" 3 --dry-run --list "$LF" "$R"
  out=$ST_OUT
  st_check "D3 pass row" \
    "$(printf '%s' "$out" | grep -aqF 'DRY-RUN-PASS' && echo 1 || echo 0)" "DRY-RUN-PASS present"
  st_check "D3 mismatch row" \
    "$(printf '%s' "$out" | grep -aqF 'receipt-mismatch' && echo 1 || echo 0)" "receipt-mismatch present"
  st_check "D3 obs.txt untouched" "$([ -f "$R/keep/obs.txt" ] && echo 1 || echo 0)" "present"

  # ---- N*: NOT-AUTHORIZED paths leave everything in place -----------------
  st_flow "N1 tracked-unpushed" 3 "$R" local/unpushed.txt
  out=$ST_OUT
  st_check "N1 result token" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'RESULT\t%s\tNOT-AUTHORIZED\tnone' "$R/local/unpushed.txt")" && echo 1 || echo 0)" \
    "NOT-AUTHORIZED none"
  st_check "N1 file untouched" "$([ -f "$R/local/unpushed.txt" ] && echo 1 || echo 0)" "present"
  st_check "N1 no quarantine dir" "$([ ! -e "$R/.ufo-quarantine" ] && echo 1 || echo 0)" "absent"

  st_flow "N2 nonexistent" 3 "$R" nope/ghost.txt
  st_check "N2 unreachable token" \
    "$(printf '%s' "$ST_OUT" | grep -aqF 'NOT-AUTHORIZED	unreachable' && echo 1 || echo 0)" "unreachable"

  local dirty_sha_before; dirty_sha_before=$(file_sha "$R/keep/dirty.txt")
  st_flow "N3 dirty-tracked" 3 "$R" keep/dirty.txt
  st_check "N3 dirty-tracked token" \
    "$(printf '%s' "$ST_OUT" | grep -aqF 'NOT-AUTHORIZED	dirty-tracked' && echo 1 || echo 0)" "dirty-tracked"
  st_check "N3 content unchanged" \
    "$([ "$(file_sha "$R/keep/dirty.txt")" = "$dirty_sha_before" ] && echo 1 || echo 0)" "sha same"

  st_flow "N4 untracked-no-receipt" 3 "$R" notes.txt
  st_check "N4 result token" \
    "$(printf '%s' "$ST_OUT" | grep -aqF "$(printf 'RESULT\t%s\tNOT-AUTHORIZED\tnone' "$R/notes.txt")" && echo 1 || echo 0)" \
    "NOT-AUTHORIZED none"
  st_check "N4 file untouched" "$([ -f "$R/notes.txt" ] && echo 1 || echo 0)" "present"

  # ---- P1: pushed receipt, tracked, full state transition -----------------
  st_flow "P1 pushed full flow" 0 "$R" keep/pushed.txt
  out=$ST_OUT
  st_check "P1 DELETED pushed" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'RESULT\t%s\tDELETED\tpushed' "$R/keep/pushed.txt")" && echo 1 || echo 0)" \
    "RESULT DELETED pushed"
  st_check "P1 stage2 git-mv" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'QSTAGE\tstage2\t%s\tgit-mv' "$R/keep/pushed.txt")" && echo 1 || echo 0)" \
    "git-mv"
  st_check "P1 stage4-second PASS" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'QVERDICT\tstage4-second\t%s\tPASS' "$R/keep/pushed.txt")" && echo 1 || echo 0)" \
    "second-check PASS"
  st_check "P1 prong1 recorded" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'QVERDICT\tstage4-prong1')" && echo 1 || echo 0)" \
    "prong1 line"
  st_check "P1 original gone" "$([ ! -e "$R/keep/pushed.txt" ] && echo 1 || echo 0)" "absent"
  st_check "P1 quarantine empty" "$([ ! -e "$R/.ufo-quarantine" ] && echo 1 || echo 0)" "rmdir'd"
  local porc; porc=$(git -C "$R" --no-optional-locks status --porcelain)
  st_check "P1 index shows staged deletion" \
    "$(printf '%s' "$porc" | grep -qF 'keep/pushed.txt' && echo 1 || echo 0)" "porcelain keeps path"

  # ---- P2: stale receipt, untracked, engine re-derives from quarantine ----
  st_flow "P2 stale full flow" 0 "$R" .scratch/old-report.out
  out=$ST_OUT
  st_check "P2 DELETED stale" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'RESULT\t%s\tDELETED\tstale' "$R/.scratch/old-report.out")" && echo 1 || echo 0)" \
    "RESULT DELETED stale"
  st_check "P2 prong1 binding SAFE(stale)" \
    "$(printf '%s' "$out" | grep -aqF 'prong1=SAFE(stale) binding' && echo 1 || echo 0)" \
    "prong1 binding"
  st_check "P2 original gone" "$([ ! -e "$R/.scratch/old-report.out" ] && echo 1 || echo 0)" "absent"

  # ---- P3: moved-to-obsidian, untracked, prong1 tolerated -----------------
  st_flow "P3 obsidian full flow" 0 "$R" keep/obs.txt
  out=$ST_OUT
  st_check "P3 DELETED obsidian" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'RESULT\t%s\tDELETED\tmoved-to-obsidian' "$R/keep/obs.txt")" && echo 1 || echo 0)" \
    "RESULT DELETED moved-to-obsidian"
  st_check "P3 prong1 tolerated" \
    "$(printf '%s' "$out" | grep -aqF 'prong1-tolerated class-not-path-local' && echo 1 || echo 0)" \
    "tolerated token"
  st_check "P3 vault still intact" "$([ -f "$ST_TMP/vault/obs.txt" ] && echo 1 || echo 0)" "vault present"
  st_check "P3 original gone" "$([ ! -e "$R/keep/obs.txt" ] && echo 1 || echo 0)" "absent"

  # ---- SKIP1: metadata-prune has no object to stage ------------------------
  st_flow "SKIP1 metadata-prune" 0 "$R" wt-inside
  st_check "SKIP1 result token" \
    "$(printf '%s' "$ST_OUT" | grep -aqF "$(printf 'RESULT\t%s\tSKIPPED\tmetadata-prune' "$R/wt-inside")" && echo 1 || echo 0)" \
    "SKIPPED metadata-prune"

  # ---- L1: real --list mode with the receipt pin --------------------------
  local LR="$ST_TMP/list-real.tsv"
  printf 'path\treceipt\n' > "$LR"
  printf '%s\tpushed\n' "$R/keep/pushed2.txt" >> "$LR"
  st_flow "L1 real list flow" 0 --list "$LR" "$R"
  out=$ST_OUT
  st_check "L1 DELETED pushed" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'RESULT\t%s\tDELETED\tpushed' "$R/keep/pushed2.txt")" && echo 1 || echo 0)" \
    "RESULT DELETED pushed"
  st_check "L1 original gone" "$([ ! -e "$R/keep/pushed2.txt" ] && echo 1 || echo 0)" "absent"

  # ---- A1: tamper between stage 2 and stage 4 -> ABORTED, kept ------------
  local HOOK="$ST_TMP/tamper-hook.sh"
  printf '#!/usr/bin/env bash\nprintf "TAMPERED" >> "$1"\n' > "$HOOK"
  local arc=0
  out=$(env SOUJI_Q_SELFTEST_ACTIVE=1 SOUJI_Q_LEDGER="$ST_LEDGER" \
    SOUJI_Q_TEST_HOOK="$HOOK" "$SELF" --hold 0 "$R" keep/obs2.txt 2>&1) || arc=$?
  st_check "A1 rc=3" "$([ "$arc" = 3 ] && echo 1 || echo 0)" "got=$arc"
  st_check "A1 ABORTED token" \
    "$(printf '%s' "$out" | grep -aqF "$(printf 'RESULT\t%s\tABORTED' "$R/keep/obs2.txt")" && echo 1 || echo 0)" \
    "RESULT ABORTED"
  st_check "A1 integrity evidence" \
    "$(printf '%s' "$out" | grep -aqF 'digest-mismatch' && echo 1 || echo 0)" "pin FAIL evidence"
  st_check "A1 kept in quarantine" \
    "$([ -f "$R/.ufo-quarantine/$(date -u +%F)/keep/obs2.txt" ] && echo 1 || echo 0)" "file stays staged"
  st_check "A1 vault untouched" "$([ -f "$ST_TMP/vault/obs2.txt" ] && echo 1 || echo 0)" "vault present"

  # ---- usage ---------------------------------------------------------------
  local rc=0
  "$SELF" --bogus "$R" x >/dev/null 2>&1 || rc=$?
  st_check "U1 unknown flag rc=2" "$([ "$rc" = 2 ] && echo 1 || echo 0)" "got=$rc"
  rc=0; "$SELF" --hold abc "$R" x >/dev/null 2>&1 || rc=$?
  st_check "U2 bad hold rc=2" "$([ "$rc" = 2 ] && echo 1 || echo 0)" "got=$rc"
  rc=0; "$SELF" >/dev/null 2>&1 || rc=$?
  st_check "U3 no repo rc=2" "$([ "$rc" = 2 ] && echo 1 || echo 0)" "got=$rc"
  rc=0; "$SELF" --list "$ST_TMP/definitely-missing.tsv" "$R" >/dev/null 2>&1 || rc=$?
  st_check "U4 missing list rc=2" "$([ "$rc" = 2 ] && echo 1 || echo 0)" "got=$rc"
  rc=0; printf 'badrow\n' > "$ST_TMP/bad.tsv"; "$SELF" --list "$ST_TMP/bad.tsv" "$R" >/dev/null 2>&1 || rc=$?
  st_check "U5 malformed list row rc=2" "$([ "$rc" = 2 ] && echo 1 || echo 0)" "got=$rc"

  # ---- audits ---------------------------------------------------------------
  local n
  n=$(grep -cE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase)( |$)' "$SELF" || true)
  n=${n// /}
  st_check "H1 no forbidden git subcommand" "$([ "${n:-1}" = 0 ] && echo 1 || echo 0)" "count=$n"
  case "$ST_TMP" in
    "${TMPDIR:-/tmp}"/*) st_ok "H2 fixtures under mktemp ($ST_TMP)" ;;
    *) st_bad "H2 fixtures not under mktemp" ;;
  esac
  local live_porcelain_after live_log_sha_after live_q_after
  live_porcelain_after=$(git -C "$REPO_ROOT" --no-optional-locks status --porcelain 2>/dev/null | grep -c . || true)
  live_log_sha_after=$(file_sha "$REPO_ROOT/LOG.md")
  live_q_after=no; [ -e "$REPO_ROOT/.ufo-quarantine" ] && live_q_after=yes
  st_check "H3 live lane porcelain unchanged" \
    "$([ "$live_porcelain_before" = "$live_porcelain_after" ] && echo 1 || echo 0)" \
    "before=$live_porcelain_before after=$live_porcelain_after"
  st_check "H3 live LOG.md unchanged" \
    "$([ "$live_log_sha_before" = "$live_log_sha_after" ] && echo 1 || echo 0)" "sha same"
  st_check "H3 no live .ufo-quarantine" \
    "$([ "$live_q_before" = no ] && [ "$live_q_after" = no ] && echo 1 || echo 0)" "absent before+after"

  local r9_out r9_rc=0
  r9_out=$(bash "$SCRIPT_DIR/souji-round9-selftest.sh" quarantine "$SELF") || r9_rc=$?
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
  [ "$ST_FAIL" -eq 0 ]
}

# ------------------------------------------------------------------- main --

ERRTMP=$(mktemp "${TMPDIR:-/tmp}/souji-quarantine.err.XXXXXX") || exit 1
trap 'rm -f -- "$ERRTMP"' EXIT

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --dry-run|--dryrun) DRYRUN=1; shift ;;
    --hold)
      [ "$#" -ge 2 ] || usage_err "--hold needs seconds"
      HOLD=$2; shift 2 ;;
    --hold=*) HOLD=${1#*=}; shift ;;
    --list)
      [ "$#" -ge 2 ] || usage_err "--list needs a TSV path"
      LIST_FILE=$2; shift 2 ;;
    --list=*) LIST_FILE=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    --)
      shift
      while [ "$#" -gt 0 ]; do
        if [ -z "$REPO" ]; then REPO=$1; else TARGETS+=("$1"); fi
        shift
      done ;;
    -*)
      usage_err "unknown flag: $1" ;;
    *)
      if [ -z "$REPO" ]; then REPO=$1; else TARGETS+=("$1"); fi
      shift ;;
  esac
done

case "$HOLD" in ''|*[!0-9]*) usage_err "--hold must be a non-negative integer" ;; esac
case "$STALE_DAYS" in ''|*[!0-9]*) usage_err "SOUJI_Q_STALE_DAYS must be a non-negative integer" ;; esac

if [ "$SELFTEST" = 1 ]; then
  run_selftest || exit 1
  exit 0
fi

[ -n "$REPO" ] || usage_err "no <repo> given"
if [ -n "$LIST_FILE" ] && [ "${#TARGETS[@]}" -gt 0 ]; then
  usage_err "--list and positional targets are exclusive"
fi
if [ -z "$LIST_FILE" ] && [ "${#TARGETS[@]}" -eq 0 ]; then
  usage_err "no <target> given"
fi
if [ -n "$LIST_FILE" ] && [ ! -f "$LIST_FILE" ]; then
  usage_err "list file not found: $LIST_FILE"
fi

run_mode
exit "$RC"
