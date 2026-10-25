#!/usr/bin/env bash
# souji-quarantine — gate-checked quarantine ticket runner (round 8, seat S02).
#
# Independent implementation of the flow pre-staged in
# census/round-7/quarantine-plan.json (execution_plan_template) and the
# SKILL.md removal flow: gate recheck -> stage -> hold -> second check ->
# operator-gated retire. A ticket exists only when ALL THREE gates pass:
#
#   gate1  no local-only commit touches the path:
#          git -C <repo> log --branches --not --remotes --oneline -- <path>
#          prints NOTHING. (r6 pitfall: the bare `--not --remotes` form
#          silently returns NOTHING on git 2.55 when refs/remotes is empty;
#          the explicit `--branches --not --remotes` form stays fail-closed
#          in a zero-remote repo. The --selftest proves the explicit form.)
#   gate2  no dirty/untracked work over the path:
#          git -C <repo> status --porcelain=v1 --untracked-files=all -- <path>
#          prints NOTHING.
#   gate3  BOTH receipt engines agree: tools/souji-verify.sh --json and
#          tools/souji-vault-verify.sh --json each return verdict SAFE with
#          the SAME receipt class in {pushed, moved-to-obsidian, stale,
#          metadata-prune}, equal to --expect-receipt when given.
# Anything else is NOT-AUTHORIZED (fail-closed). Verdicts are data, never
# errors: --check/--plan/--verify-staged always exit 0.
#
# CLI
#   tools/souji-quarantine.impl-02.sh --check [--json]
#         [--expect-receipt CLASS] <path>...        # read-only gates
#   tools/souji-quarantine.impl-02.sh --plan <path> # read-only runbook
#   tools/souji-quarantine.impl-02.sh --stage [--dry-run] <path>
#   tools/souji-quarantine.impl-02.sh --verify-staged <original-path>
#   tools/souji-quarantine.impl-02.sh --retire --operator-signoff ID
#         [--hold-min-seconds N] <staged-path>
#   tools/souji-quarantine.impl-02.sh --selftest
# Global flags: --json, --dry-run, --expect-receipt CLASS,
# --operator-signoff ID, --hold-min-seconds N (default 450 = one driver
# tick; SKILL.md prefers 24h for anything not `pushed`).
#
# Mutation discipline (the live fleet is untouchable through this tool)
#   --stage/--retire MUTATE, but only when SOUJI_Q_SANDBOX is set AND the
#   canonical target lies inside it AND the sandbox itself resolves under
#   ${TMPDIR:-/tmp}. Otherwise the request is REFUSED (exit 1) before any
#   filesystem effect. --dry-run stages nothing and needs no sandbox. The
#   selftest is the only component that sets the variable, to its own
#   `mktemp -d` root. No `git mv`: staging is a plain mv, so the quarantine
#   shows up as ordinary deletions for the owning repo's parent/operator to
#   commit (AGENTS.md: quarantine is a normal commit in the owning repo —
#   that commit is never made by this tool).
#
# Staging layout
#   <repo>/.ufo-quarantine/<UTC-YYYY-MM-DD>/<repo-relative path with / -> __>
#   plus sidecar <dest>.souji-qrecord.json: original path, owning repo,
#   receipt class + both engine receipts at stage time, introducing commit,
#   vault path/sha for moved-to-obsidian rows, content digest of the staged
#   copy (file sha256, or a sorted manifest digest for directories), stage
#   epoch, hold floor. --verify-staged re-checks gate1 on the original path
#   (history-based, survives the mv), tolerates in gate2 ONLY the
#   quarantine's own ` D` deletion lines over the original, re-verifies the
#   digest, and re-runs the class-appropriate receipt check:
#     stale             -> BOTH engines re-run on the staged copy (mtime
#                          survives mv; both engines' sweeps exclude
#                          **/.ufo-quarantine/**)
#     pushed            -> the recorded introducing commit is still an
#                          ancestor of the resolved default ref
#     moved-to-obsidian -> the recorded vault side still re-hashes
#                          (vault read-only); the source side is the digest
#   --retire requires the second check to pass NOW, a nonempty operator
#   signoff, and the hold elapsed — waived only for receipt `pushed` (per
#   SKILL.md, pushed needs no hold beyond the second check) — then removes
#   ONLY the staged copy and its record, never anything else.
#
# Deliberate restrictions (fail-closed, not silent)
#   * --stage REFUSES receipt `metadata-prune` (stage-unsupported-receipt):
#     a worktree registration is retired with worktree tooling, not a file
#     mv. --check still classifies it; --retire never sees one.
#   * --stage REFUSES a nested stale target (path under a subdirectory):
#     flattening `dir/name` to `dir__name` breaks the engines' anchored
#     `launch-*`/`*-draft.*` scratch patterns, so the mandatory copy-side
#     receipt re-check could never pass. Root-level stale targets stage.
#   * --stage REFUSES moved-to-obsidian rows whose source or vault side is
#     not a regular file (dir-row re-verification needs dir-digest
#     machinery this tool does not duplicate).
#   * Known limitation (r7 caveat, unchanged): gate2 cannot see ignored
#     paths, so an ignored target's cleanliness is only as durable as its
#     .gitignore rule; a record + second check + operator signoff bound the
#     exposure, but the operator should confirm the ignore rule is itself
#     pushed before retiring.
#
# Safety rails
#   * Secret-shaped path components (*.env, .env.*, .envrc, *credential*,
#     *secret*, id_*, *.pem) are refused before anything is read.
#   * No git fetch/push/commit/branch/checkout/reset/rebase is ever run by
#     this tool on any repo; fixtures live under `mktemp -d` only;
#     .ufo/state, .ufo/watchdog.log and ~/.config are never touched; the
#     lane repo is never mutated.
#   * Exit codes: check/plan/verify-staged always 0 (verdict is data);
#     stage/retire 0 = performed, 1 = REFUSED, 2 = usage; selftest 0 = all
#     green, 1 = any failure; usage errors 2. No other codes.
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
TOOL_A="$REPO_ROOT/tools/souji-verify.sh"
TOOL_B="$REPO_ROOT/tools/souji-vault-verify.sh"

HOLD_MIN_SECONDS=450
MODE=""          # check | plan | stage | verify-staged | retire | selftest
JSON=0
DRY_RUN=0
EXPECT_RECEIPT=""
SIGNOFF=""

RECEIPTS_OK=" pushed moved-to-obsidian stale metadata-prune "
RECEIPTS_STAGABLE=" pushed moved-to-obsidian stale "

canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

json_field() { # $1 json text, $2 field -> value of "field" : "..." (space-tolerant)
  printf '%s\n' "$1" | sed -n 's/.*"'"$2"'"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1
}

json_num_field() { # $1 json text, $2 field -> value of "field" : 123
  printf '%s\n' "$1" | sed -n 's/.*"'"$2"'"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' | head -n1
}

usage() { # $1 exit code
  cat >&2 <<'USAGE'
usage: tools/souji-quarantine.impl-02.sh <MODE> [flags] <path>...
modes (exactly one):
  --check [--json] [--expect-receipt CLASS] <path>...
  --plan <path>
  --stage [--dry-run] <path>
  --verify-staged <original-path>
  --retire --operator-signoff ID [--hold-min-seconds N] <staged-path>
  --selftest
flags: --json --dry-run --expect-receipt CLASS --operator-signoff ID
       --hold-min-seconds N -h|--help
exit codes: check/plan/verify-staged 0; stage/retire 0 ok 1 refused 2 usage;
selftest 0 all-green 1 failure; usage 2.
mutations require SOUJI_Q_SANDBOX (mktemp root under $TMPDIR) — otherwise
REFUSED before any filesystem effect; the live fleet is untouchable.
USAGE
  exit "$1"
}

usage_err() { printf 'souji-quarantine: %s\n' "$1" >&2; usage 2; }

# ---------- argument parsing ----------
TARGETS=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --check|--plan|--stage|--verify-staged|--retire|--selftest)
      [ -z "$MODE" ] || usage_err "mode already set to --$MODE (saw --$1 too)"
      MODE=${1#--}; shift ;;
    --json) JSON=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --expect-receipt)
      [ "$#" -ge 2 ] || usage_err "--expect-receipt needs a value"
      EXPECT_RECEIPT=$2; shift 2 ;;
    --expect-receipt=*) EXPECT_RECEIPT=${1#*=}; shift ;;
    --operator-signoff)
      [ "$#" -ge 2 ] || usage_err "--operator-signoff needs a value"
      SIGNOFF=$2; shift 2 ;;
    --operator-signoff=*) SIGNOFF=${1#*=}; shift ;;
    --hold-min-seconds)
      [ "$#" -ge 2 ] || usage_err "--hold-min-seconds needs a value"
      case "$2" in ''|*[!0-9]*) usage_err "--hold-min-seconds wants an integer" ;; esac
      HOLD_MIN_SECONDS=$2; shift 2 ;;
    --hold-min-seconds=*)
      v=${1#*=}
      case "$v" in ''|*[!0-9]*) usage_err "--hold-min-seconds wants an integer" ;; esac
      HOLD_MIN_SECONDS=$v; shift ;;
    -h|--help) usage 0 ;;
    --) shift; while [ "$#" -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    -*) usage_err "unknown flag: $1" ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done
[ -n "$MODE" ] || usage_err "no mode given"

# ---------- shared probes ----------

# True when any path component is secret-shaped (case-insensitive).
is_secret_shaped() {
  local comp lc
  local IFS='/'
  set -f
  for comp in $1; do
    lc=${comp,,}
    case "$lc" in
      *.env|.env|*.env.*|.envrc|*credential*|*secret*|id_*|*.pem)
        set +f
        return 0 ;;
    esac
  done
  set +f
  return 1
}

# Nearest enclosing git toplevel of a path; empty if none.
find_repo_for() { # $1 path
  local p=$1 d top
  if [ -d "$p" ]; then d=$p; else d=$(dirname -- "$p"); fi
  d=$(canon_path "$d")
  if top=$(git -C "$d" rev-parse --show-toplevel 2>/dev/null) && [ -n "$top" ]; then
    canon_path "$top"
  fi
}

# gate1: unpushed commit count touching the path (explicit form ONLY —
# the bare `--not --remotes` form silently returns nothing on git 2.55
# when refs/remotes is empty).
gate1_count() { # $1 repo $2 path
  local out
  out=$(git -C "$1" log --branches --not --remotes --oneline -- "$2" 2>/dev/null || true)
  printf '%s\n' "$out" | grep -c . || true
}

# gate2: raw porcelain lines over the path.
gate2_lines() { # $1 repo $2 path
  git -C "$1" status --porcelain=v1 --untracked-files=all -- "$2" 2>/dev/null || true
}

# Default remote-tracking ref (spec r5: existing refs only, never fetch).
resolve_default_ref() { # $1 repo -> full refname; nonzero if unresolvable
  local short refs n
  if short=$(git -C "$1" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null) && [ -n "$short" ]; then
    printf 'refs/remotes/%s\n' "$short"
    return 0
  fi
  refs=$(git -C "$1" for-each-ref --format='%(refname)' 'refs/remotes/origin/' 2>/dev/null | grep -v '/HEAD$' || true)
  n=$(printf '%s\n' "$refs" | grep -c . || true)
  if [ "$n" = "1" ]; then
    printf '%s\n' "$refs"
    return 0
  fi
  return 1
}

# Run one receipt engine on a target; prints "<verdict> <receipt>".
run_engine() { # $1 engine $2 target
  local raw verdict receipt
  if ! raw=$(bash "$1" --json "$2" 2>/dev/null | head -n1); then
    raw=""
  fi
  if [ -z "$raw" ]; then
    printf 'ENGINE-ERROR none\n'
    return 0
  fi
  verdict=$(json_field "$raw" verdict)
  receipt=$(json_field "$raw" receipt)
  printf '%s %s\n' "${verdict:-ENGINE-ERROR}" "${receipt:-none}"
}

# gate3: dual-engine agreement. Sets G3_RECEIPT (agreed class or "none")
# and G3_REASON (always populated; "gate3-pass(...)" on success).
gate3_evaluate() { # $1 target
  local target=$1 a b
  a=$(run_engine "$TOOL_A" "$target")
  b=$(run_engine "$TOOL_B" "$target")
  A_VERDICT=${a%% *}; A_RECEIPT=${a#* }
  B_VERDICT=${b%% *}; B_RECEIPT=${b#* }
  G3_RECEIPT="none"
  if [ "$A_VERDICT" != "SAFE" ] || [ "$B_VERDICT" != "SAFE" ]; then
    G3_REASON="gate3-no-safe-receipt(a=$A_VERDICT/$A_RECEIPT,b=$B_VERDICT/$B_RECEIPT)"
    return 0
  fi
  if [ "$A_RECEIPT" != "$B_RECEIPT" ]; then
    G3_REASON="gate3-receipt-mismatch(a=$A_RECEIPT,b=$B_RECEIPT)"
    return 0
  fi
  case "$RECEIPTS_OK" in
    *" $A_RECEIPT "*) : ;;
    *) G3_REASON="gate3-unknown-receipt($A_RECEIPT)"; return 0 ;;
  esac
  if [ -n "$EXPECT_RECEIPT" ] && [ "$EXPECT_RECEIPT" != "$A_RECEIPT" ]; then
    G3_REASON="receipt-mismatch(expect=$EXPECT_RECEIPT,actual=$A_RECEIPT)"
    return 0
  fi
  G3_RECEIPT="$A_RECEIPT"
  G3_REASON="gate3-pass(a=SAFE/$A_RECEIPT,b=SAFE/$B_RECEIPT)"
}

# Owner repo of a worktree registration path (dir may be absent, so the
# walk-up probe cannot find it): scan the fleet root's lane repos' worktree
# lists. Read-only; mirrors how the receipt engines resolve the owner.
find_registration_owner() { # $1 canon path
  local d wt sroot
  sroot="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"
  [ -d "$sroot" ] || return 0
  for d in "$sroot"/*/; do
    d=${d%/}
    [ -e "$d/.git" ] || continue
    while IFS= read -r wt; do
      case "$wt" in
        "worktree "*) wt=${wt#worktree } ;;
        *) continue ;;
      esac
      if [ "$(canon_path "$wt")" = "$1" ]; then
        canon_path "$d"
        return 0
      fi
    done < <(git -C "$d" worktree list --porcelain 2>/dev/null)
  done
  return 0
}

# Full evaluation of one target. Sets E_AUTH(0/1) E_RECEIPT E_REASON
# E_REPO E_G1 E_G2 E_A_VERDICT E_A_RECEIPT E_B_VERDICT E_B_RECEIPT E_CANON.
evaluate_path() { # $1 target
  local target=$1 canon repo
  E_AUTH=0; E_RECEIPT="none"; E_REASON=""; E_REPO=""
  E_G1=""; E_G2=""
  E_A_VERDICT=""; E_A_RECEIPT=""; E_B_VERDICT=""; E_B_RECEIPT=""
  canon=$(canon_path "$target")
  E_CANON=$canon
  if is_secret_shaped "$canon"; then
    E_REASON="secrets-refusal"
    return 0
  fi
  repo=$(find_repo_for "$canon")
  if [ -z "$repo" ]; then
    repo=$(find_registration_owner "$canon")
  fi
  E_REPO=$repo
  if [ -z "$repo" ]; then
    # a missing path with no discoverable owner is unreachable; an existing
    # one with no owner genuinely has no repo to run gates against
    if [ ! -e "$canon" ]; then
      E_REASON="unreachable"
    else
      E_REASON="no-repo"
    fi
    return 0
  fi
  E_G1=$(gate1_count "$repo" "$canon")
  E_G2=$(gate2_lines "$repo" "$canon")
  gate3_evaluate "$canon"
  E_A_VERDICT=$A_VERDICT; E_A_RECEIPT=$A_RECEIPT
  E_B_VERDICT=$B_VERDICT; E_B_RECEIPT=$B_RECEIPT
  if [ "$E_G1" != "0" ]; then
    E_REASON="gate1-unpushed-touching(count=$E_G1)"
    return 0
  fi
  if [ -n "$E_G2" ]; then
    E_REASON="gate2-dirty-touching(lines=$(printf '%s\n' "$E_G2" | grep -c . || true))"
    return 0
  fi
  case "$G3_REASON" in
    "gate3-pass(a=SAFE/$G3_RECEIPT,b=SAFE/$G3_RECEIPT)") : ;;
    *) E_REASON="$G3_REASON"; return 0 ;;
  esac
  E_AUTH=1
  E_RECEIPT=$G3_RECEIPT
  E_REASON="all-gates-pass(a=$E_A_VERDICT/$E_A_RECEIPT,b=$E_B_VERDICT/$E_B_RECEIPT)"
  # a missing target is usually just unreachable — EXCEPT receipt
  # metadata-prune, whose defining condition is an absent dir
  if [ ! -e "$canon" ] && [ "$E_RECEIPT" != "metadata-prune" ]; then
    E_AUTH=0; E_RECEIPT="none"; E_REASON="unreachable"
  fi
}

emit_check_line() { # $1 target as given by the caller
  local target=$1 state g1s g2s g3s
  if [ "$E_AUTH" = "1" ]; then
    state=AUTHORIZED; g1s=pass; g2s=pass; g3s=pass
  else
    state=NOT-AUTHORIZED
    g1s=pass; g2s=pass; g3s=pass
    case "$E_REASON" in
      secrets-refusal|unreachable|no-repo) g1s=n/a; g2s=n/a; g3s=n/a ;;
      gate1-*) g1s=fail ;;
      gate2-*) g2s=fail ;;
      gate3-*|receipt-mismatch*) g3s=fail ;;
    esac
  fi
  if [ "$JSON" = "1" ]; then
    printf '{"path":"%s","authorized":%s,"verdict":"%s","receipt":"%s","gates":{"gate1":"%s","gate2":"%s","gate3":"%s"},"engines":{"a":{"verdict":"%s","receipt":"%s"},"b":{"verdict":"%s","receipt":"%s"}},"evidence":"%s"}\n' \
      "$(json_escape "$target")" \
      "$([ "$E_AUTH" = "1" ] && printf true || printf false)" \
      "$state" \
      "$(json_escape "$E_RECEIPT")" "$g1s" "$g2s" "$g3s" \
      "$(json_escape "$E_A_VERDICT")" "$(json_escape "$E_A_RECEIPT")" \
      "$(json_escape "$E_B_VERDICT")" "$(json_escape "$E_B_RECEIPT")" \
      "$(json_escape "$E_REASON")"
  else
    printf 'CHECK\t%s\t%s\t%s\t%s\n' "$target" "$state" "$E_RECEIPT" "$E_REASON"
  fi
}

# ---------- plan (read-only runbook) ----------
emit_plan() { # $1 target
  local target=$1 qdir dest record rel flat holdnote gate2disp
  evaluate_path "$target"
  qdir=$(date -u +%Y-%m-%d)
  if [ "$E_AUTH" = "1" ]; then
    rel=${E_CANON#"$E_REPO"/}
    flat=${rel//\//__}
    dest="$E_REPO/.ufo-quarantine/$qdir/$flat"
    record="$dest.souji-qrecord.json"
    if [ "$E_RECEIPT" = "pushed" ]; then
      holdnote="hold waived for pushed beyond the second check (SKILL.md)"
    else
      holdnote="hold >= ${HOLD_MIN_SECONDS}s floor (prefer 24h for non-pushed)"
    fi
  else
    dest="(not stageable: $E_REASON)"
    record="(not stageable)"
    holdnote="n/a"
  fi
  if [ -n "$E_G2" ]; then gate2disp="NONEMPTY(must be empty)"; else gate2disp="empty(ok)"; fi
  cat <<PLAN
PLAN $target
  repo:           ${E_REPO:-none}
  canonical:      $E_CANON
  gate1 unpushed: count=${E_G1:-n/a} (must be 0)
  gate2 dirty:    $gate2disp
  gate3 receipt:  $E_RECEIPT (a=$E_A_VERDICT/$E_A_RECEIPT b=$E_B_VERDICT/$E_B_RECEIPT)
  authorized:     $([ "$E_AUTH" = "1" ] && echo YES || echo "NO ($E_REASON)")
  quarantine dir: ${E_REPO:-<repo>}/.ufo-quarantine/$qdir/
  stage dest:     $dest
  record sidecar: $record
  hold policy:    $holdnote
  step_0_recheck: souji-quarantine.impl-02.sh --check --expect-receipt ${E_RECEIPT:-CLASS} "$E_CANON"
  step_1_stage:   souji-quarantine.impl-02.sh --stage "$E_CANON"   (needs SOUJI_Q_SANDBOX)
  step_2_hold:    leave .ufo-quarantine untouched; no commit, no delete
  step_3_recheck: souji-quarantine.impl-02.sh --verify-staged "$E_CANON"
  step_4_retire:  souji-quarantine.impl-02.sh --retire --operator-signoff <ID> "$dest"
PLAN
  printf 'PLAN-TAIL\t%s\t%s\t%s\t%s\n' "$target" \
    "$([ "$E_AUTH" = "1" ] && echo AUTHORIZED || echo NOT-AUTHORIZED)" \
    "$E_RECEIPT" "$E_REASON"
}

# ---------- content digests ----------
digest_of() { # $1 path -> sets D_VALUE D_KIND
  local p=$1
  if [ -f "$p" ]; then
    D_KIND=file
    D_VALUE=$(sha256sum -- "$p" 2>/dev/null | cut -d' ' -f1 || true)
  elif [ -d "$p" ]; then
    D_KIND=dir-manifest
    D_VALUE=$(cd "$p" && find . -type f -print0 2>/dev/null \
      | LC_ALL=C sort -z \
      | xargs -0 -r sha256sum 2>/dev/null \
      | sha256sum 2>/dev/null | cut -d' ' -f1 || true)
  else
    D_KIND=missing; D_VALUE=""
  fi
  if [ -z "$D_VALUE" ]; then D_KIND=missing; fi
}

# First ledger row whose source path matches; sets LV_VP / LV_VS.
ledger_row_for() { # $1 canonical source path $2 ledger path
  LV_VP=""; LV_VS=""
  local row sp ss vp vs
  [ -f "$2" ] || return 0
  while IFS= read -r row || [ -n "$row" ]; do
    [ -n "$row" ] || continue
    case "$row" in source_path$'\t'*) continue ;; esac
    IFS=$'\t' read -r sp ss vp vs _rest <<< "$row" || true
    if [ "$sp" = "$1" ]; then LV_VP=$vp; LV_VS=$vs; return 0; fi
  done < "$2"
  return 0
}

# ---------- mutation guards ----------
sandbox_check() { # $1 canonical target; refuses (exit 1) via caller context
  local canon=$1 sandbox tmpbase
  sandbox=${SOUJI_Q_SANDBOX:-}
  if [ -z "$sandbox" ]; then
    printf 'Q-REFUSED\t%s\tno-sandbox(SOUJI_Q_SANDBOX unset; live fleet untouchable)\n' "$canon" >&2
    return 1
  fi
  sandbox=$(canon_path "$sandbox")
  tmpbase=$(canon_path "${TMPDIR:-/tmp}")
  case "$sandbox" in
    "$tmpbase"|"$tmpbase"/*) : ;;
    *)
      printf 'Q-REFUSED\t%s\tsandbox-not-under-tmpdir(%s)\n' "$canon" "$sandbox" >&2
      return 1 ;;
  esac
  case "$canon" in
    "$sandbox"|"$sandbox"/*) return 0 ;;
    *)
      printf 'Q-REFUSED\t%s\toutside-sandbox(%s)\n' "$canon" "$sandbox" >&2
      return 1 ;;
  esac
}

# ---------- stage ----------
mode_stage() { # $1 target
  local target=$1 canon repo rel flat qdir dest record intro vp vs
  canon=$(canon_path "$target")

  if is_secret_shaped "$canon"; then
    printf 'STAGE-REFUSED\t%s\tsecrets-refusal\n' "$canon" >&2
    return 1
  fi
  if [ "$DRY_RUN" != "1" ]; then
    sandbox_check "$canon" || return 1
  fi

  evaluate_path "$canon"
  if [ "$E_AUTH" != "1" ]; then
    printf 'STAGE-REFUSED\t%s\t%s\n' "$canon" "$E_REASON" >&2
    return 1
  fi
  case "$RECEIPTS_STAGABLE" in
    *" $E_RECEIPT "*) : ;;
    *)
      printf 'STAGE-REFUSED\t%s\tstage-unsupported-receipt(%s)\n' "$canon" "$E_RECEIPT" >&2
      return 1 ;;
  esac

  repo=$E_REPO
  rel=${canon#"$repo"/}
  if [ "$rel" = "$canon" ] || [ -z "$rel" ]; then
    printf 'STAGE-REFUSED\t%s\ttarget-not-inside-owning-repo\n' "$canon" >&2
    return 1
  fi
  case "$rel" in
    .ufo-quarantine|".ufo-quarantine"/*)
      printf 'STAGE-REFUSED\t%s\talready-quarantined\n' "$canon" >&2
      return 1 ;;
  esac
  if [ "$E_RECEIPT" = "stale" ] && [ "$rel" != "$(basename -- "$rel")" ]; then
    printf 'STAGE-REFUSED\t%s\tnested-stale-unre-verifiable(flatten breaks scratch pattern)\n' "$canon" >&2
    return 1
  fi
  if [ "$E_RECEIPT" = "moved-to-obsidian" ]; then
    ledger_row_for "$canon" "${SOUJI_LEDGER:-$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv}"
    vp=$LV_VP; vs=$LV_VS
    if [ -z "$vp" ] || [ ! -f "$vp" ] || [ ! -f "$canon" ]; then
      printf 'STAGE-REFUSED\t%s\tobsidian-source-or-vault-not-regular-file\n' "$canon" >&2
      return 1
    fi
  fi

  qdir=$(date -u +%Y-%m-%d)
  flat=${rel//\//__}
  dest="$repo/.ufo-quarantine/$qdir/$flat"
  record="$dest.souji-qrecord.json"

  if [ "$DRY_RUN" = "1" ]; then
    printf 'STAGE-DRYRUN\t%s\t%s\t%s\t%s\n' "$canon" "$dest" "$record" "$E_RECEIPT"
    return 0
  fi

  if [ -e "$dest" ]; then
    printf 'STAGE-REFUSED\t%s\tdest-exists(%s)\n' "$canon" "$dest" >&2
    return 1
  fi

  intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$canon" 2>/dev/null | head -n1 || true)

  mkdir -p -- "$(dirname -- "$dest")"
  mv -- "$canon" "$dest"
  digest_of "$dest"

  local now nowiso
  now=$(date -u +%s)
  nowiso=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  {
    printf '{\n'
    printf '  "original": "%s",\n' "$(json_escape "$canon")"
    printf '  "repo": "%s",\n' "$(json_escape "$repo")"
    printf '  "rel": "%s",\n' "$(json_escape "$rel")"
    printf '  "receipt": "%s",\n' "$E_RECEIPT"
    printf '  "engine_a": "%s/%s",\n' "$E_A_VERDICT" "$E_A_RECEIPT"
    printf '  "engine_b": "%s/%s",\n' "$E_B_VERDICT" "$E_B_RECEIPT"
    printf '  "intro": "%s",\n' "$intro"
    printf '  "vault_path": "%s",\n' "$(json_escape "${vp:-}")"
    printf '  "vault_sha256": "%s",\n' "${vs:-}"
    printf '  "digest": "%s",\n' "$D_VALUE"
    printf '  "digest_kind": "%s",\n' "$D_KIND"
    printf '  "staged_at_epoch": %s,\n' "$now"
    printf '  "staged_at_iso": "%s",\n' "$nowiso"
    printf '  "hold_min_seconds": %s,\n' "$HOLD_MIN_SECONDS"
    printf '  "tool": "souji-quarantine.impl-02.sh"\n'
    printf '}\n'
  } > "$record"

  printf 'STAGED\t%s\t%s\t%s\t%s\t%s\n' "$canon" "$dest" "$record" "$E_RECEIPT" "$D_VALUE"
  return 0
}

# ---------- second check ----------
load_record() { # $1 record file -> sets R_* fields; 0 ok / 1 bad
  local f=$1 raw
  R_ORIG=""; R_REPO=""; R_RECEIPT=""; R_INTRO=""; R_DIGEST=""; R_KIND=""
  R_VP=""; R_VS=""; R_EPOCH=""
  [ -f "$f" ] || return 1
  raw=$(cat -- "$f" 2>/dev/null || true)
  [ -n "$raw" ] || return 1
  R_ORIG=$(json_field "$raw" original)
  R_REPO=$(json_field "$raw" repo)
  R_RECEIPT=$(json_field "$raw" receipt)
  R_INTRO=$(json_field "$raw" intro)
  R_DIGEST=$(json_field "$raw" digest)
  R_KIND=$(json_field "$raw" digest_kind)
  R_VP=$(json_field "$raw" vault_path)
  R_VS=$(json_field "$raw" vault_sha256)
  R_EPOCH=$(json_num_field "$raw" staged_at_epoch)
  if [ -z "$R_ORIG" ] || [ -z "$R_REPO" ] || [ -z "$R_RECEIPT" ] || [ -z "$R_DIGEST" ]; then
    return 1
  fi
}

# gate2 with the quarantine-mv waiver: only ` D <orig>` deletion lines over
# the original are tolerated (the staging's own footprint until the owning
# repo's operator commits the quarantine). Porcelain prints repo-relative
# paths, so the comparison runs against the relative form.
gate2_waived() { # $1 repo $2 orig canon -> 0 pass / 1 fail; sets W_DETAILS
  local out bad=0 line p rel
  W_DETAILS=""
  rel=${2#"$1"/}
  out=$(gate2_lines "$1" "$2")
  if [ -n "$out" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      case "$line" in
        " D "*)
          p=${line#" D "}
          case "$p" in
            "$rel"|"$rel"/*) : ;;
            *) bad=1; W_DETAILS="$W_DETAILS[$line]" ;;
          esac ;;
        *) bad=1; W_DETAILS="$W_DETAILS[$line]" ;;
      esac
    done <<< "$out"
  fi
  if [ "$bad" = "0" ]; then return 0; fi
  return 1
}

second_check() { # $1 original path -> sets SC_PASS(0/1) SC_EVID SC_RECORD SC_DEST
  local orig=$1 canon record f repo flat found=0
  canon=$(canon_path "$orig")
  SC_PASS=0; SC_EVID=""; SC_RECORD=""; SC_DEST=""
  if is_secret_shaped "$canon"; then
    SC_EVID="secrets-refusal"
    return 0
  fi
  repo=$(find_repo_for "$canon")
  if [ -n "$repo" ]; then
    flat=${canon#"$repo"/}
    flat=${flat//\//__}
    for f in "$repo"/.ufo-quarantine/*/"$flat.souji-qrecord.json"; do
      [ -e "$f" ] || continue
      if [ "$(json_field "$(cat -- "$f" 2>/dev/null || true)" original)" = "$canon" ]; then
        record=$f; found=1; break
      fi
    done
  else
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      if [ "$(json_field "$(cat -- "$f" 2>/dev/null || true)" original)" = "$canon" ]; then
        record=$f; found=1; break
      fi
    done < <(find "${SOUJI_Q_SANDBOX:-/nonexistent-souji-q}" -name '*.souji-qrecord.json' -type f 2>/dev/null)
  fi
  if [ "$found" != "1" ] || ! load_record "$record"; then
    SC_EVID="no-valid-record"
    return 0
  fi
  local dest; dest=${record%.souji-qrecord.json}
  if [ ! -e "$dest" ]; then
    SC_EVID="staged-copy-missing($dest)"
    return 0
  fi
  digest_of "$dest"
  if [ "$D_VALUE" != "$R_DIGEST" ] || [ "$D_KIND" != "$R_KIND" ]; then
    SC_EVID="digest-mismatch(record=${R_DIGEST:0:12},now=${D_VALUE:0:12})"
    return 0
  fi
  local g1
  g1=$(gate1_count "$R_REPO" "$R_ORIG")
  if [ "$g1" != "0" ]; then
    SC_EVID="gate1-regressed(count=$g1)"
    return 0
  fi
  if ! gate2_waived "$R_REPO" "$R_ORIG"; then
    SC_EVID="gate2-regressed($W_DETAILS)"
    return 0
  fi
  case "$R_RECEIPT" in
    stale)
      local a b
      a=$(run_engine "$TOOL_A" "$dest")
      b=$(run_engine "$TOOL_B" "$dest")
      if [ "$a" = "SAFE stale" ] && [ "$b" = "SAFE stale" ]; then
        SC_EVID="stale-reverified-on-copy(digest=${R_DIGEST:0:12})"
      else
        SC_EVID="stale-not-reverified(a=${a% *}/${a#* },b=${b% *}/${b#* })"
        return 0
      fi
      ;;
    pushed)
      local ref
      if [ -z "$R_INTRO" ]; then
        SC_EVID="record-missing-intro"
        return 0
      fi
      if ref=$(resolve_default_ref "$R_REPO") \
         && git -C "$R_REPO" merge-base --is-ancestor "$R_INTRO" "$ref" 2>/dev/null; then
        SC_EVID="pushed-reverified(intro=${R_INTRO:0:12},ref=$ref)"
      else
        SC_EVID="pushed-not-reverified(intro=${R_INTRO:0:12})"
        return 0
      fi
      ;;
    moved-to-obsidian)
      local vsha=""
      if [ -z "$R_VP" ] || [ ! -f "$R_VP" ]; then
        SC_EVID="vault-unreachable($R_VP)"
        return 0
      fi
      vsha=$(sha256sum -- "$R_VP" 2>/dev/null | cut -d' ' -f1 || true)
      if [ -n "$vsha" ] && [ "$vsha" = "$R_VS" ]; then
        SC_EVID="obsidian-reverified(vault=$(basename -- "$R_VP"),digest=${R_DIGEST:0:12})"
      else
        SC_EVID="vault-sha-mismatch"
        return 0
      fi
      ;;
    *)
      SC_EVID="unsupported-staged-receipt($R_RECEIPT)"
      return 0 ;;
  esac
  SC_PASS=1
  SC_RECORD=$record
  SC_DEST=$dest
}

mode_verify_staged() { # $1 original path (read-only; exit 0)
  local orig=$1 state
  second_check "$orig"
  if [ "$SC_PASS" = "1" ]; then state=PASS; else state=FAIL; fi
  if [ "$JSON" = "1" ]; then
    printf '{"path":"%s","second_check":"%s","evidence":"%s"}\n' \
      "$(json_escape "$orig")" "$state" "$(json_escape "$SC_EVID")"
  else
    printf 'SECOND-CHECK\t%s\t%s\t%s\n' "$orig" "$state" "$SC_EVID"
  fi
}

mode_retire() { # $1 staged path
  local dest=$1 canon record orig mtime now age
  canon=$(canon_path "$dest")

  if [ -z "$SIGNOFF" ]; then
    printf 'RETIRE-REFUSED\t%s\tempty-operator-signoff\n' "$canon" >&2
    return 1
  fi
  if is_secret_shaped "$canon"; then
    printf 'RETIRE-REFUSED\t%s\tsecrets-refusal\n' "$canon" >&2
    return 1
  fi
  sandbox_check "$canon" || return 1

  record="$canon.souji-qrecord.json"
  if ! load_record "$record"; then
    printf 'RETIRE-REFUSED\t%s\tno-valid-record(%s)\n' "$canon" "$record" >&2
    return 1
  fi
  orig=$R_ORIG

  second_check "$orig"
  if [ "$SC_PASS" != "1" ]; then
    printf 'RETIRE-REFUSED\t%s\tsecond-check-failed(%s)\n' "$canon" "$SC_EVID" >&2
    return 1
  fi

  # hold floor measured from the record's staging time (the mv preserves
  # the ORIGINAL file's mtime, which says nothing about how long the copy
  # has been held), waived only for `pushed` (SKILL.md)
  if [ "$R_RECEIPT" != "pushed" ]; then
    if [ -z "$R_EPOCH" ]; then
      printf 'RETIRE-REFUSED\t%s\trecord-missing-staged-at\n' "$canon" >&2
      return 1
    fi
    now=$(date -u +%s)
    age=$(( now - R_EPOCH ))
    if [ "$age" -lt "$HOLD_MIN_SECONDS" ]; then
      printf 'RETIRE-REFUSED\t%s\thold-not-elapsed(age=%ss,min=%ss)\n' "$canon" "$age" "$HOLD_MIN_SECONDS" >&2
      return 1
    fi
  fi

  rm -rf -- "$canon"
  rm -f -- "$record"
  printf 'RETIRED\t%s\t%s\t%s\tsignoff=%s\n' "$canon" "$R_RECEIPT" "$orig" "$SIGNOFF"
  return 0
}

# ---------- selftest ----------
run_selftest() {
  local pass=0 fail=0 t0
  TMP=$(mktemp -d)   # global on purpose: the EXIT trap outlives this function
  trap 'rm -rf "$TMP"' EXIT

  ok()  { pass=$((pass+1)); printf 'ok   %s\n' "$1"; }
  bad() { fail=$((fail+1)); printf 'FAIL %s | %s\n' "$1" "$2"; }
  assert_eq() { # label want got
    if [ "$2" = "$3" ]; then ok "$1"; else bad "$1" "want=[$2] got=[$3]"; fi
  }
  assert_contains() { # label needle haystack
    case "$3" in
      *"$2"*) ok "$1" ;;
      *) bad "$1" "missing [$2] in [${3:0:160}]" ;;
    esac
  }
  assert_lacks() { # label needle haystack
    case "$3" in
      *"$2"*) bad "$1" "unexpected [$2] in [${3:0:160}]" ;;
      *) ok "$1" ;;
    esac
  }
  q() { bash "$SELF" "$@"; }   # tool call with selftest env inherited

  export SOUJI_Q_SANDBOX="$TMP"
  export SHOKUNIN_ROOT="$TMP"              # engines never scan the live fleet
  export SOUJI_LEDGER="$TMP/ledger.tsv"    # engines never read the live ledger
  : > "$SOUJI_LEDGER"

  fx_init() { # $1 name -> echoes repo path (committed base.txt, NOT anchored)
    local r="$TMP/$1"
    git init -q -b master "$r"
    git -C "$r" config user.email fixture@souji.invalid
    git -C "$r" config user.name "souji fixture"
    printf 'base\n' > "$r/base.txt"
    git -C "$r" add base.txt
    git -C "$r" commit -qm 'base'
    printf '%s\n' "$r"
  }
  fx_anchor() { # $1 repo -> point origin refs at current HEAD (no fetch)
    git -C "$1" update-ref refs/remotes/origin/master HEAD
    git -C "$1" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  }

  printf '# fixtures under %s\n' "$TMP"

  # ---- T1: pushed happy path, full lifecycle (hold waived for pushed) ----
  local R1 D1 out rc
  R1=$(fx_init r1-shokunin)
  printf 'v1\n' > "$R1/keep.txt"
  git -C "$R1" add keep.txt
  git -C "$R1" commit -qm 'add keep.txt'
  fx_anchor "$R1"
  out=$(q --check "$R1/keep.txt"); assert_contains "T1 check AUTHORIZED" "AUTHORIZED	pushed" "$out"
  out=$(q --check --json "$R1/keep.txt")
  assert_contains "T1 check json authorized" '"authorized":true' "$out"
  assert_contains "T1 check json receipt" '"receipt":"pushed"' "$out"
  out=$(q --check --expect-receipt pushed "$R1/keep.txt")
  assert_contains "T1 expect pushed ok" "AUTHORIZED" "$out"
  out=$(q --check --expect-receipt stale "$R1/keep.txt")
  assert_contains "T1 expect stale mismatch" "NOT-AUTHORIZED" "$out"
  assert_contains "T1 expect stale reason" "receipt-mismatch(expect=stale,actual=pushed)" "$out"
  rc=0; out=$(q --stage "$R1/keep.txt" 2>&1) || rc=$?
  assert_eq "T1 stage exit" "0" "$rc"
  D1="$R1/.ufo-quarantine/$(date -u +%Y-%m-%d)/keep.txt"
  assert_contains "T1 stage line" "STAGED	$R1/keep.txt	$D1" "$out"
  if [ -f "$D1" ] && [ -f "$D1.souji-qrecord.json" ] && [ ! -e "$R1/keep.txt" ]; then
    ok "T1 staged layout"
  else
    bad "T1 staged layout" "dest=$([ -f "$D1" ] && echo y || echo n) record=$([ -f "$D1.souji-qrecord.json" ] && echo y || echo n) orig=$([ -e "$R1/keep.txt" ] && echo present || echo gone)"
  fi
  out=$(q --verify-staged "$R1/keep.txt")
  assert_contains "T1 second-check PASS" "SECOND-CHECK	$R1/keep.txt	PASS	pushed-reverified" "$out"
  # retire with default hold (450s): pushed waives the hold, not the checks
  rc=0; out=$(q --retire --operator-signoff op-t1 "$D1" 2>&1) || rc=$?
  assert_eq "T1 retire exit" "0" "$rc"
  assert_contains "T1 retired line" "RETIRED	$D1	pushed	$R1/keep.txt	signoff=op-t1" "$out"
  if [ ! -e "$D1" ] && [ ! -e "$D1.souji-qrecord.json" ]; then
    ok "T1 retire removed copy+record only"
  else
    bad "T1 retire removed copy+record only" "residue at $D1"
  fi

  # ---- T2: gate1 fail (local-only commit touches the file) ----
  local R2
  R2=$(fx_init r2-shokunin)
  printf 'a\n' > "$R2/keep.txt"
  git -C "$R2" add keep.txt; git -C "$R2" commit -qm c1
  fx_anchor "$R2"
  printf 'b\n' > "$R2/keep.txt"
  git -C "$R2" add keep.txt; git -C "$R2" commit -qm c2-local
  out=$(q --check "$R2/keep.txt")
  assert_contains "T2 gate1 NOT-AUTHORIZED" "NOT-AUTHORIZED" "$out"
  assert_contains "T2 gate1 reason" "gate1-unpushed-touching(count=1)" "$out"
  rc=0; out=$(q --stage "$R2/keep.txt" 2>&1) || rc=$?
  assert_eq "T2 stage refused exit" "1" "$rc"
  assert_contains "T2 stage refused reason" "STAGE-REFUSED	$R2/keep.txt	gate1-unpushed-touching" "$out"

  # ---- T3: gate2 fail (dirty tracked + untracked variants) ----
  local R3
  R3=$(fx_init r3-shokunin)
  printf 'a\n' > "$R3/keep.txt"
  git -C "$R3" add keep.txt; git -C "$R3" commit -qm c1
  fx_anchor "$R3"
  printf 'dirty\n' > "$R3/keep.txt"
  out=$(q --check "$R3/keep.txt")
  assert_contains "T3 gate2 dirty" "NOT-AUTHORIZED" "$out"
  assert_contains "T3 gate2 dirty reason" "gate2-dirty-touching" "$out"
  git -C "$R3" checkout -q -- keep.txt 2>/dev/null || git -C "$R3" restore -q "$R3/keep.txt" 2>/dev/null || printf 'a\n' > "$R3/keep.txt"
  printf 'untracked\n' > "$R3/extra.txt"
  out=$(q --check "$R3/extra.txt")
  assert_contains "T3 gate2 untracked" "NOT-AUTHORIZED" "$out"
  assert_contains "T3 gate2 untracked reason" "gate2-dirty-touching" "$out"

  # ---- T5: zero-remote repo fails closed on gate1 (r6 pitfall) ----
  local R5 pit
  R5=$(fx_init r5-shokunin)
  printf 'x\n' > "$R5/keep.txt"
  git -C "$R5" add keep.txt; git -C "$R5" commit -qm c1
  out=$(q --check "$R5/keep.txt")
  assert_contains "T5 zero-remote NOT-AUTHORIZED" "NOT-AUTHORIZED" "$out"
  assert_contains "T5 zero-remote gate1 fail-closed" "gate1-unpushed-touching(count=1)" "$out"
  pit=$(git -C "$R5" log --not --remotes --oneline -- "$R5/keep.txt" 2>/dev/null | grep -c . || true)
  printf 'info T5 bare-form count on git %s = %s (r6 pitfall reference)\n' "$(git --version | cut -d' ' -f3)" "$pit"
  rc=0; out=$(q --stage "$R5/keep.txt" 2>&1) || rc=$?
  assert_eq "T5 stage refused exit" "1" "$rc"

  # ---- T6: secrets refusal happens before any read ----
  local R6
  R6=$(fx_init r6-shokunin)
  printf 'SECRET=1\n' > "$R6/app.env"
  out=$(q --check "$R6/app.env")
  assert_contains "T6 check secrets-refusal" "NOT-AUTHORIZED" "$out"
  assert_contains "T6 check secrets reason" "secrets-refusal" "$out"
  rc=0; out=$(q --stage "$R6/app.env" 2>&1) || rc=$?
  assert_eq "T6 stage refused exit" "1" "$rc"
  assert_contains "T6 stage refused reason" "secrets-refusal" "$out"

  # ---- T7: no sandbox -> REFUSED before any effect ----
  local R7
  R7=$(fx_init r7-shokunin)
  printf 'v\n' > "$R7/keep.txt"
  git -C "$R7" add keep.txt; git -C "$R7" commit -qm c1
  fx_anchor "$R7"
  rc=0; out=$(env -u SOUJI_Q_SANDBOX bash "$SELF" --stage "$R7/keep.txt" 2>&1) || rc=$?
  assert_eq "T7 no-sandbox refused exit" "1" "$rc"
  assert_contains "T7 no-sandbox reason" "no-sandbox" "$out"
  if [ ! -e "$R7/.ufo-quarantine" ]; then ok "T7 no quarantine dir created"; else bad "T7" ".ufo-quarantine appeared"; fi
  # dry run needs no sandbox and touches nothing
  rc=0; out=$(env -u SOUJI_Q_SANDBOX bash "$SELF" --stage --dry-run "$R7/keep.txt" 2>&1) || rc=$?
  assert_eq "T7 dry-run exit (no sandbox)" "0" "$rc"
  assert_contains "T7 dry-run line" "STAGE-DRYRUN	$R7/keep.txt	$R7/.ufo-quarantine/$(date -u +%Y-%m-%d)/keep.txt" "$out"
  if [ ! -e "$R7/.ufo-quarantine" ]; then ok "T7 dry-run created nothing"; else bad "T7" "dry-run mutated"; fi

  # ---- T8: sandbox escape refused ----
  rc=0; out=$(env SOUJI_Q_SANDBOX="$TMP/elsewhere" bash "$SELF" --stage "$R7/keep.txt" 2>&1) || rc=$?
  assert_eq "T8 escape refused exit" "1" "$rc"
  assert_contains "T8 escape reason" "outside-sandbox" "$out"

  # ---- T9: stale happy path — ignored stale file (the shape that truly
  # classifies stale: committed scratch files get receipt `pushed` first).
  # Ignore durability: the .gitignore rule is itself in the pushed anchor. ----
  local R9 D9 m0 m1
  R9=$(fx_init r9-shokunin)
  printf 'launch-*.json\n' > "$R9/.gitignore"
  git -C "$R9" add .gitignore
  git -C "$R9" commit -qm 'ignore checkpoint json'
  fx_anchor "$R9"
  printf '{"seat":"selftest"}\n' > "$R9/launch-old.json"
  t0=$(( $(date +%s) - 3*86400 ))
  touch -d "@$t0" "$R9/launch-old.json"
  out=$(q --check "$R9/launch-old.json")
  assert_contains "T9 stale AUTHORIZED" "AUTHORIZED	stale" "$out"
  m0=$(stat -c %Y "$R9/launch-old.json")
  rc=0; out=$(q --stage "$R9/launch-old.json" 2>&1) || rc=$?
  assert_eq "T9 stage exit" "0" "$rc"
  D9="$R9/.ufo-quarantine/$(date -u +%Y-%m-%d)/launch-old.json"
  m1=$(stat -c %Y "$D9" 2>/dev/null || printf missing)
  assert_eq "T9 mtime preserved by mv" "$m0" "$m1"
  out=$(q --verify-staged "$R9/launch-old.json")
  assert_contains "T9 second-check PASS" "SECOND-CHECK	$R9/launch-old.json	PASS	stale-reverified-on-copy" "$out"
  # the moved file was ignored: the original leaves NO porcelain trace
  assert_eq "T9 gate2 empty after mv (ignored)" "" "$(git -C "$R9" status --porcelain=v1 --untracked-files=all -- launch-old.json)"
  # retire before the hold elapses -> REFUSED
  rc=0; out=$(q --retire --operator-signoff op-t9 "$D9" 2>&1) || rc=$?
  assert_eq "T9 retire hold refused exit" "1" "$rc"
  assert_contains "T9 retire hold reason" "hold-not-elapsed" "$out"
  if [ -f "$D9" ]; then ok "T9 hold refusal kept the copy"; else bad "T9" "copy vanished on refusal"; fi
  # retire with the floor lowered -> RETIRED
  rc=0; out=$(q --retire --hold-min-seconds 0 --operator-signoff op-t9 "$D9" 2>&1) || rc=$?
  assert_eq "T9 retire exit" "0" "$rc"
  assert_contains "T9 retired" "RETIRED	$D9	stale" "$out"

  # ---- T10: tampered staged copy -> second check FAILS, retire refused ----
  local R10 D10
  R10=$(fx_init r10-shokunin)
  printf '{"seat":"t10"}\n' > "$R10/launch-t.json"
  git -C "$R10" add launch-t.json; git -C "$R10" commit -qm c1
  fx_anchor "$R10"
  touch -d "@$t0" "$R10/launch-t.json"
  q --stage "$R10/launch-t.json" > /dev/null
  D10="$R10/.ufo-quarantine/$(date -u +%Y-%m-%d)/launch-t.json"
  printf 'tampered\n' >> "$D10"
  out=$(q --verify-staged "$R10/launch-t.json")
  assert_contains "T10 second-check FAIL" "SECOND-CHECK	$R10/launch-t.json	FAIL	digest-mismatch" "$out"
  rc=0; out=$(q --retire --hold-min-seconds 1 --operator-signoff op-t10 "$D10" 2>&1) || rc=$?
  assert_eq "T10 retire refused exit" "1" "$rc"
  assert_contains "T10 retire reason" "second-check-failed" "$out"
  if [ -f "$D10" ]; then ok "T10 refuse kept tampered copy (operator decision)"; else bad "T10" "tampered copy deleted without pass"; fi

  # ---- T13: plan is read-only ----
  local R13
  R13=$(fx_init r13-shokunin)
  printf 'v\n' > "$R13/keep.txt"
  git -C "$R13" add keep.txt; git -C "$R13" commit -qm c1
  fx_anchor "$R13"
  rc=0; out=$(q --plan "$R13/keep.txt" 2>&1) || rc=$?
  assert_eq "T13 plan exit" "0" "$rc"
  assert_contains "T13 plan steps" "step_4_retire:" "$out"
  assert_contains "T13 plan tail AUTHORIZED" "PLAN-TAIL	$R13/keep.txt	AUTHORIZED	pushed" "$out"
  if [ ! -e "$R13/.ufo-quarantine" ]; then ok "T13 plan created nothing"; else bad "T13" "plan mutated"; fi

  # ---- T14: usage errors exit 2 ----
  rc=0; out=$(bash "$SELF" 2>&1) || rc=$?
  assert_eq "T14 no-mode exit" "2" "$rc"
  rc=0; out=$(bash "$SELF" --check --plan "$R13/keep.txt" 2>&1) || rc=$?
  assert_eq "T14 two-modes exit" "2" "$rc"
  rc=0; out=$(bash "$SELF" --retire "$R13/keep.txt" 2>&1) || rc=$?
  assert_eq "T14 retire-without-signoff exit" "2" "$rc"

  # ---- T15: metadata-prune classifies but refuses to stage ----
  local R15 WT15
  R15=$(fx_init r15-shokunin)
  fx_anchor "$R15"
  WT15="$TMP/wt15-dir"
  git -C "$R15" worktree add -q "$WT15" -b wt15
  rm -rf "$WT15"
  out=$(q --check "$WT15")
  assert_contains "T15 metadata-prune AUTHORIZED" "AUTHORIZED	metadata-prune" "$out"
  rc=0; out=$(q --stage "$WT15" 2>&1) || rc=$?
  assert_eq "T15 stage refused exit" "1" "$rc"
  assert_contains "T15 stage reason" "stage-unsupported-receipt(metadata-prune)" "$out"

  # ---- T16: moved-to-obsidian full lifecycle (ignored source, file vault) ----
  local R16 V16 sh_src sh_vault
  R16=$(fx_init r16-shokunin)
  printf 'docs/notes.md\n' > "$R16/.gitignore"
  git -C "$R16" add .gitignore; git -C "$R16" commit -qm 'ignore docs'
  fx_anchor "$R16"
  mkdir -p "$R16/docs"
  printf 'kb-body\n' > "$R16/docs/notes.md"          # ignored -> gate2-clean
  V16="$TMP/vault16"
  mkdir -p "$V16"
  printf 'kb-body\n' > "$V16/notes.md"
  sh_src=$(sha256sum "$R16/docs/notes.md" | cut -d' ' -f1)
  sh_vault=$(sha256sum "$V16/notes.md" | cut -d' ' -f1)
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t%s\tselftest\n' "$(canon_path "$R16/docs/notes.md")" "$sh_src" "$(canon_path "$V16/notes.md")" "$sh_vault" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$SOUJI_LEDGER"
  out=$(q --check "$R16/docs/notes.md")
  assert_contains "T16 obsidian AUTHORIZED" "AUTHORIZED	moved-to-obsidian" "$out"
  rc=0; out=$(q --stage "$R16/docs/notes.md" 2>&1) || rc=$?
  assert_eq "T16 stage exit" "0" "$rc"
  local D16; D16="$R16/.ufo-quarantine/$(date -u +%Y-%m-%d)/docs__notes.md"
  out=$(q --verify-staged "$R16/docs/notes.md")
  assert_contains "T16 second-check PASS" "SECOND-CHECK	$R16/docs/notes.md	PASS	obsidian-reverified" "$out"
  rc=0; out=$(q --retire --hold-min-seconds 0 --operator-signoff op-t16 "$D16" 2>&1) || rc=$?
  assert_eq "T16 retire exit" "0" "$rc"
  if [ -f "$V16/notes.md" ]; then ok "T16 vault untouched (read-only)"; else bad "T16" "vault modified"; fi
  : > "$SOUJI_LEDGER"

  # ---- T17: stale candidate with a live reference -> gate3 refuses ----
  local R17
  R17=$(fx_init r17-shokunin)
  printf 'launch-*.json\n' > "$R17/.gitignore"
  git -C "$R17" add .gitignore
  git -C "$R17" commit -qm 'ignore'
  fx_anchor "$R17"
  printf 'hot\n' > "$R17/launch-hot.json"
  printf 'see launch-hot.json\n' > "$R17/pointer.md"
  git -C "$R17" add pointer.md
  git -C "$R17" commit -qm 'pointer'
  touch -d "@$t0" "$R17/launch-hot.json"
  out=$(q --check "$R17/launch-hot.json")
  assert_contains "T17 live-ref NOT-AUTHORIZED" "NOT-AUTHORIZED" "$out"
  assert_contains "T17 live-ref gate3 refuse" "gate3-no-safe-receipt" "$out"

  # ---- T12/T20: unreachable + verify-staged without a record ----
  out=$(q --check "$TMP/definitely/not/there")
  assert_contains "T12 unreachable" "NOT-AUTHORIZED" "$out"
  assert_contains "T12 unreachable reason" "unreachable" "$out"
  out=$(q --verify-staged "$R13/keep.txt")
  assert_contains "T20 no-record FAIL" "SECOND-CHECK	$R13/keep.txt	FAIL	no-valid-record" "$out"

  # ---- T18: nested stale refuses to stage (flattening breaks the pattern) ----
  local R18
  R18=$(fx_init r18-shokunin)
  printf 'launch-*.json\n' > "$R18/.gitignore"
  git -C "$R18" add .gitignore
  git -C "$R18" commit -qm 'ignore'
  fx_anchor "$R18"
  mkdir -p "$R18/sub"
  printf 'x\n' > "$R18/sub/launch-nested.json"
  touch -d "@$t0" "$R18/sub/launch-nested.json"
  out=$(q --check "$R18/sub/launch-nested.json")
  assert_contains "T18 nested stale classifies" "AUTHORIZED	stale" "$out"
  rc=0; out=$(q --stage "$R18/sub/launch-nested.json" 2>&1) || rc=$?
  assert_eq "T18 stage refused exit" "1" "$rc"
  assert_contains "T18 stage reason" "nested-stale-unre-verifiable" "$out"

  # ---- T19: non-stale nested dir still stages (pushed, flattening safe) ----
  local R19 D19
  R19=$(fx_init r19-shokunin)
  mkdir -p "$R19/lib"
  printf 'code\n' > "$R19/lib/mod.txt"
  git -C "$R19" add lib; git -C "$R19" commit -qm c1
  fx_anchor "$R19"
  rc=0; out=$(q --stage "$R19/lib/mod.txt" 2>&1) || rc=$?
  assert_eq "T19 nested pushed stage exit" "0" "$rc"
  D19="$R19/.ufo-quarantine/$(date -u +%Y-%m-%d)/lib__mod.txt"
  if [ -f "$D19" ]; then ok "T19 flattened dest exists"; else bad "T19" "missing $D19"; fi
  out=$(q --verify-staged "$R19/lib/mod.txt")
  assert_contains "T19 second-check PASS" "SECOND-CHECK	$R19/lib/mod.txt	PASS	pushed-reverified" "$out"

  printf 'SELFTEST seat=S02 tool=souji-quarantine.impl-02.sh passed=%d failed=%d\n' "$pass" "$fail"
  if [ "$fail" -gt 0 ]; then
    return 1
  fi
  return 0
}

# ---------- dispatch ----------
case "$MODE" in
  check)
    [ "${#TARGETS[@]}" -ge 1 ] || usage_err "--check needs at least one path"
    for t in "${TARGETS[@]}"; do
      evaluate_path "$t"
      emit_check_line "$t"
    done
    ;;
  plan)
    [ "${#TARGETS[@]}" -eq 1 ] || usage_err "--plan needs exactly one path"
    emit_plan "${TARGETS[0]}"
    ;;
  stage)
    [ "${#TARGETS[@]}" -eq 1 ] || usage_err "--stage needs exactly one path"
    mode_stage "${TARGETS[0]}"
    ;;
  verify-staged)
    [ "${#TARGETS[@]}" -eq 1 ] || usage_err "--verify-staged needs exactly one original path"
    mode_verify_staged "${TARGETS[0]}"
    ;;
  retire)
    [ "${#TARGETS[@]}" -eq 1 ] || usage_err "--retire needs exactly one staged path"
    [ -n "$SIGNOFF" ] || usage_err "--retire requires --operator-signoff ID"
    mode_retire "${TARGETS[0]}"
    ;;
  selftest)
    if run_selftest; then
      exit 0
    fi
    exit 1
    ;;
esac
exit 0
