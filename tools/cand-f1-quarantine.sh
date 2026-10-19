#!/usr/bin/env bash
# souji-quarantine (candidate, cluster-F)
#
# round-10 S11 cluster-F candidate, derived from the installed S17-patched
# tools/souji-quarantine.sh (base sha256 f6f8516c15ab654f7e5f2dc2a7840eef0b53b9f9433e2ff70a64490b35fde68f).
#
# Cluster-F repairs carried here:
#   F1 registration ownership by gitdir resolution, not by owner-name pattern.
#      The fleet scan enumerates every repo dir under $SHOKUNIN_ROOT (dot dirs
#      skipped) and asks Git itself for the registration list, so an owner
#      named without the -shokunin suffix can no longer hide a worktree.
#      The scan runs in the current shell (a subshell would lose the
#      incomplete-scan flag) and an unreadable candidate owner dir makes every
#      non-root target refuse instead of falling through to artifact receipts.
#   F2 repository roots whose `.git` is a FILE (git init --separate-git-dir)
#      are classified as repository roots by resolving the gitfile through
#      Git (gitdir == git-common-dir => root), so they can never receive the
#      pushed / stale artifact receipts. A linked-worktree root is refused
#      with its own token instead of being judged as a scratch artifact.
#   F3 (quarantine only) stage 4 revalidates the CURRENT default ref: the
#      remote snapshot at that ref must still be the exact object authorized
#      at stage 1, so a default-ref re-point during the hold can no longer
#      authorize deleting a path whose remote content moved or vanished.
#
# Selftest: every pre-existing case of the base tool is preserved verbatim
# (including the shared r9 corpus runner); the S11F*/S11Q* cases appended
# below are the fresh regressions for the classes above.
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
# Env
#   SOUJI_VERIFY_BIN            receipt engine (default <repo of this
#                               tool>/tools/souji-verify.sh)
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

usage() { sed -n '2,119p' "$SELF" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
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

file_sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1 || true; }

dir_digest() { # manifest digest; ANY symlink in scope fails closed (rc 2)
  local d=$1
  if ( cd -- "$d" 2>/dev/null && find . -path './.git' -prune -o -type l -print -quit 2>/dev/null | grep -q . ); then
    return 2
  fi
  ( cd -- "$d" 2>/dev/null && find . -path './.git' -prune -o -type f -print0 \
      | LC_ALL=C sort -z | xargs -0 -r sha256sum 2>/dev/null | sha256sum | cut -d' ' -f1 ) 2>/dev/null
  return 0
}

content_digest() { # $1 path -> digest on stdout; rc 2 when symlink in scope
  if [ -L "$1" ]; then return 2; fi
  if [ -d "$1" ]; then dir_digest "$1"; else file_sha "$1"; fi
}

emit() { # any number of fields, TAB-joined, sanitized
  local out="" f
  for f in "$@"; do
    f=$(sanitize_field "$f")
    if [ -z "$out" ]; then out=$f; else out="$out"$'\t'"$f"; fi
  done
  printf '%s\n' "$out"
}

# ------------------------------------------------------- receipt engine ----

run_verify() { # $1 target -> V_VERDICT/V_RECEIPT/V_EV (V_RAW kept whole)
  local t=$1 rc=0
  V_RAW=$(SHOKUNIN_ROOT="$SV_ROOT" SOUJI_LEDGER="$SV_LEDGER" \
    bash "$VERIFY_BIN" --stale-days "$STALE_DAYS" -- "$t" 2>"$ERRTMP") || rc=$?
  if [ "$rc" -ne 0 ] || [[ "$V_RAW" != VERDICT$'\t'* ]]; then
    V_VERDICT=ERROR
    V_RECEIPT=engine-error
    V_EV="receipt-engine-rc=$rc stderr=$(sanitize_field "$(head -c 200 "$ERRTMP" 2>/dev/null || true)")"
    return 0
  fi
  local rest
  rest=${V_RAW#*$'\t'}
  rest=${rest#*$'\t'}                 # drop echoed path
  V_VERDICT=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  V_RECEIPT=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  V_EV=$rest
  return 0
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
second_check() {
  SC_PASS=0
  local ev="" ok=1
  local now_sha now_mtime
  now_sha=$(content_digest "$QPATH"); local dig_rc=$?
  now_mtime=$(stat -c %Y -- "$QPATH" 2>/dev/null || true)
  if [ "$dig_rc" -ne 2 ] && [ -n "$now_sha" ] && [ "$now_sha" = "$PIN_SHA" ]; then
    ev="pin=ok"
  else
    ok=0
    if [ "$dig_rc" -eq 2 ]; then
      ev="pin=FAIL symlink-present-in-quarantine"
    else
      ev="pin=FAIL digest-mismatch stage1=${PIN_SHA:0:12} now=${now_sha:0:12}"
    fi
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
        # S11 F3: the ancestry prong alone is not enough. The default ref may
        # have been re-pointed during the hold at a commit that MODIFIES or
        # DELETES the staged path; the remote snapshot at the CURRENT default
        # ref must still be the exact object that was authorized at stage 1.
        local snap_rc=0 stage_rc=0 snap_blob="" stage_blob=""
        if [ -n "${current_ref:-}" ]; then
          if snap_blob=$(git -C "$CREPO" rev-parse --verify --quiet "$current_ref:$REL" 2>/dev/null); then
            snap_rc=0
          else
            snap_rc=1
          fi
          if stage_blob=$(git -C "$CREPO" rev-parse --verify --quiet "$intro:$REL" 2>/dev/null); then
            stage_rc=0
          else
            stage_rc=1
          fi
          if [ "$snap_rc" -ne 0 ] || [ "$stage_rc" -ne 0 ] || [ -z "$snap_blob" ] || [ -z "$stage_blob" ]; then
            ok=0; ev="$ev class=FAIL default-snapshot-unverifiable"
          elif [ "$snap_blob" = "$stage_blob" ]; then
            ev="$ev default-snapshot=ok"
          else
            ok=0; ev="$ev class=FAIL default-snapshot-moved"
          fi
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
          blob_sha=$(git -C "$CREPO" cat-file blob "$intro:$REL" 2>/dev/null | sha256sum | cut -d' ' -f1 || true)
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
      ledger_pin=$(file_sha "$SV_LEDGER")
      row=$(ledger_row_for "$CT")
      if [ -z "$row" ]; then
        ok=0; ev="$ev class=FAIL ledger-row-gone"
      else
        ss=${row%%$'\t'*}; local rest=${row#*$'\t'}
        vp=${rest%%$'\t'*}; vs=${rest#*$'\t'}
        if [ "$ISDIR" = 0 ]; then
          vault_sha=$(file_sha "$vp")
          if [ -n "$ss" ] && [ "$now_sha" = "$ss" ]; then ev="$ev source-sha=ok"; else ok=0; ev="$ev class=FAIL source-sha-mismatch"; fi
          if [ -n "$vs" ] && [ "$vault_sha" = "$vs" ]; then ev="$ev vault-sha=ok"; else ok=0; ev="$ev class=FAIL vault-sha-mismatch vault=${vp:-none}"; fi
        else
          vault_sha=$(dir_digest "$vp"); vault_rc=$?
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
flow_one() {
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
  # S11 F1/F2: refuse, independently of the receipt engine, any target that
  # is itself a Git repository or worktree root. Registration ownership is
  # not decided by the owner's name, and an ancestor receipt must never
  # authorize removing a nested repository's work.
  if [ -d "$ct" ] && [ -e "$ct/.git" ]; then
    block_one "$raw" nested-repo-root \
      "target is a Git repository/worktree root; judge it through its own owner repo"
    return 0
  fi
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

  local pin_sha pin_mtime
  pin_sha=$(content_digest "$ct")
  pin_mtime=$(stat -c %Y -- "$ct" 2>/dev/null || true)

  CT=$ct CREPO=$crepo REL=$rel QPATH=$qpath CLASS=$class ISDIR=$isdir
  PIN_SHA=$pin_sha PIN_MTIME=$pin_mtime METHOD=$method

  if [ "$DRYRUN" = 1 ]; then
    emit CMD "$raw" "mkdir -p -- $(printf '%q' "$qdir/$(dirname -- "$rel")")"
    if [ "$tracked" = 1 ]; then
      emit CMD "$raw" "git -C $(printf '%q' "$crepo") mv -- $(printf '%q' "$rel") $(printf '%q' "$qpath")"
    else
      emit CMD "$raw" "mv -- $(printf '%q' "$ct") $(printf '%q' "$qpath")"
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

  # ---- stage 2: stage into quarantine -------------------------------------
  if ! mkdir -p -- "$qdir/$(dirname -- "$rel")" 2>/dev/null; then
    emit RESULT "$raw" STAGE2-FAILED mkdir-failed "qdir=$qdir"
    N_S2FAIL=$((N_S2FAIL + 1)); RC=3
    return 0
  fi
  if [ "$tracked" = 1 ]; then
    if ! git -C "$crepo" mv -- "$rel" "$qpath" 2>"$ERRTMP"; then
      emit RESULT "$raw" STAGE2-FAILED git-mv-failed \
        "$(sanitize_field "$(head -c 200 "$ERRTMP" || true)")"
      N_S2FAIL=$((N_S2FAIL + 1)); RC=3
      return 0
    fi
  else
    if ! mv -- "$ct" "$qpath" 2>"$ERRTMP"; then
      emit RESULT "$raw" STAGE2-FAILED mv-failed \
        "$(sanitize_field "$(head -c 200 "$ERRTMP" || true)")"
      N_S2FAIL=$((N_S2FAIL + 1)); RC=3
      return 0
    fi
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

  # ---- stage 5: delete from quarantine ------------------------------------
  if ! rm -rf -- "$qpath" 2>/dev/null; then
    emit QSTAGE stage5 "$raw" ABORTED "rm-failed qpath=$qpath"
    emit RESULT "$raw" ABORTED "$class" "rm-failed $SC_EV"
    N_ABORTED=$((N_ABORTED + 1)); RC=3
    return 0
  fi
  if [ "$tracked" = 1 ]; then
    if ! git -C "$crepo" rm --cached --quiet -- "$qpath" 2>/dev/null; then
      emit QSTAGE stage5-index "$raw" index-cleanup-skipped "$qpath"
    fi
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

  if [ ! -d "$Q_CREPO/.git" ] && [ ! -f "$Q_CREPO/.git" ]; then
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
  ST_TMP=$(mktemp -d "${TMPDIR:-/var/tmp}/souji-quarantine-selftest.XXXXXX")
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

  # ---- S11 (round 10) cluster-F regressions --------------------------------
  # The F1/F3 repairs live in the receipt engine as well, so these cases pin
  # the candidate engine explicitly (stage 1 authority is the engine's).
  local S11_ENGINE="$ST_TMP/s11-engine-verify.sh"
  cp -- "$SCRIPT_DIR/cand-f1-verify.sh" "$S11_ENGINE"
  local S11_SAVED_ENGINE="${SOUJI_VERIFY_BIN:-}"
  export SOUJI_VERIFY_BIN="$S11_ENGINE"

  # F1: a worktree registration owned by a dir whose name lacks -shokunin.
  # The registration is visible now, so the engine refuses the worktree root
  # (unpushed branch) and quarantine never stages it.
  local OW="$ST_FLEET/owner" OWT="$ST_TMP/s11-owner-wt"
  git init -q --initial-branch=master "$OW"
  printf 'owner base\n' > "$OW/kept.txt"
  local o1; o1=$(st_commit "$OW" "" "o1 owner base")
  git -C "$OW" update-ref refs/remotes/origin/master "$o1"
  git -C "$OW" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$OW" update-ref refs/heads/master "$o1"
  printf 'owner private\n' > "$OW/p.txt"
  local o2; o2=$(st_commit "$OW" "$o1" "o2 owner local work")
  git -C "$OW" update-ref refs/heads/private "$o2"
  local OWA="$OW/.git/worktrees/s11-present"
  mkdir -p "$OWA" "$OWT"
  printf 'ref: refs/heads/private\n' > "$OWA/HEAD"
  printf '../..\n' > "$OWA/commondir"
  printf '%s\n' "$OWT/.git" > "$OWA/gitdir"
  printf 'gitdir: %s\n' "$OWA" > "$OWT/.git"
  git -C "$OWT" read-tree HEAD >/dev/null 2>&1
  git -C "$OWT" checkout-index -a >/dev/null 2>&1
  printf 'untracked live work\n' > "$OWT/active.txt"
  st_flow "S11Q1 non-shokunin owner worktree" 3 "$OW" "$OWT"
  st_check "S11Q1 refused before staging" \
    "$(printf '%s' "$ST_OUT" | grep -aqF 'NOT-AUTHORIZED	unpushed-branch' && echo 1 || echo 0)" "unpushed-branch"
  st_check "S11Q1 live work intact" "$([ -f "$OWT/active.txt" ] && echo 1 || echo 0)" "active.txt present"
  st_check "S11Q1 no quarantine" "$([ ! -e "$OW/.ufo-quarantine" ] && echo 1 || echo 0)" "absent"

  # F2: a gitfile repository root is accepted as <repo> (no usage error), and
  # when its own root is authorized by a ledger row the independent root gate
  # refuses it with target-is-repo-root.
  local GF="$ST_TMP/s11-gitfile-shokunin" GFA="$ST_TMP/s11-git-admin"
  git init -q --initial-branch=master --separate-git-dir="$GFA" "$GF"
  printf 'payload\n' > "$GF/keep.txt"
  git -C "$GF" add -A >/dev/null 2>&1
  local gtr g1; gtr=$(git -C "$GF" write-tree)
  g1=$(printf 'g1\n' | git -C "$GF" commit-tree "$gtr")
  git -C "$GF" update-ref refs/remotes/origin/master "$g1"
  git -C "$GF" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$GF" update-ref refs/heads/master "$g1"
  local GV="$ST_TMP/s11-git-vault"; mkdir -p "$GV"
  printf 'payload\n' > "$GV/keep.txt"
  printf '%s\t%s\t%s\t%s\t2026-10-18\ts11-git-dir\n' \
    "$GF" "$(dir_digest "$GF")" "$GV" "$(dir_digest "$GV")" >> "$ST_LEDGER"
  st_flow "S11Q2 gitfile root target" 3 "$GF" "$GF"
  st_check "S11Q2 root refused by root gate" \
    "$(printf '%s' "$ST_OUT" | grep -aqF 'NOT-AUTHORIZED	target-is-repo-root' && echo 1 || echo 0)" "root gate"
  st_check "S11Q2 repo accepted as <repo>" \
    "$(printf '%s' "$ST_OUT" | grep -aqF 'not a git repo' && echo 0 || echo 1)" "no usage error"

  # F1/F2 defense in depth: a NESTED gitfile repository inside a ledger-
  # preserved scratch dir would pass stage 1 as moved-to-obsidian; quarantine
  # must still refuse to stage a repository root.
  local NR="$ST_FLEET/nested-owner-shokunin"
  git init -q --initial-branch=master "$NR"
  printf 'outer\n' > "$NR/kept.txt"
  local r1; r1=$(st_commit "$NR" "" "r1 outer")
  git -C "$NR" update-ref refs/remotes/origin/master "$r1"
  git -C "$NR" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$NR" update-ref refs/heads/master "$r1"
  local NI="$NR/.scratch/inner" NIA="$ST_TMP/s11-inner-admin"
  git init -q --initial-branch=master --separate-git-dir="$NIA" "$NI"
  printf 'inner payload\n' > "$NI/inner.txt"
  git -C "$NI" add -A >/dev/null 2>&1
  local ntr n1; ntr=$(git -C "$NI" write-tree)
  n1=$(printf 'n1\n' | git -C "$NI" commit-tree "$ntr")
  git -C "$NI" update-ref refs/heads/master "$n1"
  local NV="$ST_TMP/s11-inner-vault"; mkdir -p "$NV"
  printf 'inner payload\n' > "$NV/inner.txt"
  printf '%s\t%s\t%s\t%s\t2026-10-18\ts11-inner-dir\n' \
    "$NI" "$(dir_digest "$NI")" "$NV" "$(dir_digest "$NV")" >> "$ST_LEDGER"
  touch -d '3 days ago' "$NR/.scratch"
  st_flow "S11Q5 nested gitfile root" 3 "$NR" "$NR/.scratch/inner"
  st_check "S11Q5 nested-repo-root token" \
    "$(printf '%s' "$ST_OUT" | grep -aqF 'NOT-AUTHORIZED	nested-repo-root' && echo 1 || echo 0)" "token"
  st_check "S11Q5 inner work intact" "$([ -f "$NI/inner.txt" ] && echo 1 || echo 0)" "inner.txt present"
  st_check "S11Q5 no quarantine" "$([ ! -e "$NR/.ufo-quarantine" ] && echo 1 || echo 0)" "absent"

  # F3: the default ref is re-pointed during the hold at a commit whose tip
  # no longer contains the staged path. Stage 4 must ABORT and keep the copy.
  local F3="$ST_TMP/s11-f3-shokunin"
  git init -q --initial-branch=master "$F3"
  printf 'seed\n' > "$F3/seed.txt"
  local s1; s1=$(st_commit "$F3" "" "s1 seed")
  git -C "$F3" update-ref refs/remotes/origin/master "$s1"
  git -C "$F3" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$F3" update-ref refs/heads/master "$s1"
  printf 'payload\n' > "$F3/note.txt"
  local n2; n2=$(st_commit "$F3" "$s1" "n2 note")
  git -C "$F3" update-ref refs/heads/master "$n2"
  git -C "$F3" update-ref refs/remotes/origin/master "$n2"
  rm -- "$F3/note.txt"
  git -C "$F3" add -A >/dev/null 2>&1
  local ltr l1; ltr=$(git -C "$F3" write-tree)
  l1=$(printf 'legacy drops note\n' | git -C "$F3" commit-tree "$ltr" -p "$n2")
  printf 'payload\n' > "$F3/note.txt"
  git -C "$F3" add -A >/dev/null 2>&1
  local H3="$ST_TMP/s11-f3-hook.sh"
  printf '#!/usr/bin/env bash\nset -eu\ngit -C %q update-ref refs/remotes/origin/legacy %s\ngit -C %q symbolic-ref --delete refs/remotes/origin/HEAD\ngit -C %q update-ref -d refs/remotes/origin/master\n' \
    "$F3" "$l1" "$F3" "$F3" > "$H3"
  chmod +x "$H3"
  local arc=0
  ST_OUT=$(env SOUJI_Q_SELFTEST_ACTIVE=1 SOUJI_Q_LEDGER="$ST_LEDGER" \
    SOUJI_Q_TEST_HOOK="$H3" "$SELF" --hold 0 "$F3" note.txt 2>&1) || arc=$?
  ST_RC=$arc
  st_check "S11Q3 rc=3" "$([ "$ST_RC" = 3 ] && echo 1 || echo 0)" "got=$ST_RC"
  st_check "S11Q3 ABORTED token" \
    "$(printf '%s' "$ST_OUT" | grep -aqF "$(printf 'RESULT\t%s/note.txt\tABORTED' "$F3")" && echo 1 || echo 0)" "aborted"
  st_check "S11Q3 snapshot prong evidence" \
    "$(printf '%s' "$ST_OUT" | grep -aqF 'default-snapshot' && echo 1 || echo 0)" "snapshot"
  st_check "S11Q3 copy retained" \
    "$([ -f "$F3/.ufo-quarantine/$(date -u +%F)/note.txt" ] && echo 1 || echo 0)" "staged copy stays"
  st_check "S11Q3 content recoverable" \
    "$([ "$(cat "$F3/.ufo-quarantine/$(date -u +%F)/note.txt" 2>/dev/null)" = "payload" ] && echo 1 || echo 0)" "payload in quarantine"

  # F3 control: the default ref may advance freely while the snapshot at the
  # staged path is unchanged -- that must still delete.
  local C3="$ST_TMP/s11-f3-ctl-shokunin"
  git init -q --initial-branch=master "$C3"
  printf 'seed\n' > "$C3/seed.txt"
  local c1; c1=$(st_commit "$C3" "" "c1 seed")
  git -C "$C3" update-ref refs/remotes/origin/master "$c1"
  git -C "$C3" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$C3" update-ref refs/heads/master "$c1"
  printf 'payload\n' > "$C3/note.txt"
  local c2; c2=$(st_commit "$C3" "$c1" "c2 note")
  git -C "$C3" update-ref refs/heads/master "$c2"
  git -C "$C3" update-ref refs/remotes/origin/master "$c2"
  printf 'unrelated\n' > "$C3/other.txt"
  local c3; c3=$(st_commit "$C3" "$c2" "c3 other")
  git -C "$C3" update-ref refs/heads/master "$c3"
  local H4="$ST_TMP/s11-f3-ctl-hook.sh"
  printf '#!/usr/bin/env bash\nset -eu\ngit -C %q update-ref refs/remotes/origin/master %s\n' "$C3" "$c3" > "$H4"
  chmod +x "$H4"
  arc=0
  ST_OUT=$(env SOUJI_Q_SELFTEST_ACTIVE=1 SOUJI_Q_LEDGER="$ST_LEDGER" \
    SOUJI_Q_TEST_HOOK="$H4" "$SELF" --hold 0 "$C3" note.txt 2>&1) || arc=$?
  ST_RC=$arc
  st_check "S11Q4 control rc=0" "$([ "$ST_RC" = 0 ] && echo 1 || echo 0)" "got=$ST_RC"
  st_check "S11Q4 control DELETED" \
    "$(printf '%s' "$ST_OUT" | grep -aqF 'DELETED	pushed' && echo 1 || echo 0)" "deleted"
  st_check "S11Q4 snapshot ok evidence" \
    "$(printf '%s' "$ST_OUT" | grep -aqF 'default-snapshot=ok' && echo 1 || echo 0)" "snapshot ok"
  st_check "S11Q4 control copy gone" "$([ ! -e "$C3/note.txt" ] && echo 1 || echo 0)" "absent"
  if [ -n "$S11_SAVED_ENGINE" ]; then export SOUJI_VERIFY_BIN="$S11_SAVED_ENGINE"; else unset SOUJI_VERIFY_BIN; fi

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
    "${TMPDIR:-/var/tmp}"/*) st_ok "H2 fixtures under mktemp ($ST_TMP)" ;;
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

ERRTMP=$(mktemp "${TMPDIR:-/var/tmp}/souji-quarantine.err.XXXXXX") || exit 1
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
