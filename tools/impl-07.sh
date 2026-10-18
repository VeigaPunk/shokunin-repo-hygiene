#!/usr/bin/env bash
# impl-07.sh — souji-quarantine: receipt-window quarantine lifecycle (S07, round 8)
#
# Machine implementation of SKILL.md "Removal flow" steps 3-6 plus the r7
# quarantine-plan authorization rule, corrected by the r8 runner findings
# (results/qrun-23.json F1/F2): the second receipt check consumes PRE-MOVE
# evidence recorded at stage time and never re-derives a receipt from the
# moved path — a moved pushed file has no introducing commit, and a
# committed-then-restored quarantine poisons the receipt until push.
#
# Subcommands
#   plan     gates + receipt per target -> AUTHORIZED / NOT-AUTHORIZED tickets
#   runbook  the operator/lane action that would open each blocked gate
#   stage    re-verify ALL gates, then move into <repo>/.ufo-quarantine/<utc-date>/
#            (git mv when tracked, plain mv when untracked; NO commit) and
#            record the pre-move receipt evidence + sha256 in the manifest
#   check    second receipt check: hold elapsed + quarantine-copy sha identity
#            + original absent + no new unpushed commits touching the path
#            + (stale) still zero live references. PASS promotes the ticket.
#   delete   rm the quarantined copy; requires check PASS (status second-checked);
#            realpath escape-guarded to <repo>/.ufo-quarantine/<date>/
#   status   list manifest tickets of a repo
#
# Output grammar (TSV, one record per line; --json emits JSONL instead)
#   TICKET<TAB>path<TAB>AUTHORIZED|NOT-AUTHORIZED<TAB>receipt-or-block<TAB>evidence
#   STAGED<TAB>ticket<TAB>quarantine-path<TAB>receipt<TAB>sha256
#   CHECK<TAB>ticket<TAB>PASS|FAIL<TAB>detail
#   DELETED<TAB>ticket
#   REFUSED<TAB>path-or-ticket<TAB>reason
#   GATE<TAB>path<TAB>blocked-gates<TAB>owner<TAB>opening-action
#   TICKETS<TAB>ticket<TAB>status<TAB>orig-path<TAB>receipt<TAB>qpath
#   SELFTEST<TAB>pass=N<TAB>fail=N<TAB>fixture=<dir>
# Exit codes: 0 = evaluated clean (NOT-AUTHORIZED tickets still exit 0);
# 1 = refusal, failed check, or selftest failure; 2 = usage.
#
# Gates (r7 quarantine-plan.json authorization_rule, re-verified at every step)
#   gate1  git -C <repo> log --branches --not --remotes --oneline -- <path>
#          -> empty (explicit --branches form: bare --not --remotes returns
#          nothing on git 2.55 when refs/remotes is empty — r6 pitfall)
#   gate2  git -C <repo> status --porcelain=v1 --untracked-files=all -- <path>
#          -> empty, one documented exception: untracked(??) entries do NOT block a stale receipt (untracked aged scratch is exactly what the stale class authorizes; installed souji-verify behavior wins); tracked-dirty entries block every receipt.
#   gate3  receipt holds via tools/souji-verify.sh (installed behavior wins;
#          inline pushed/stale fallback only when that tool is absent).
#          metadata-prune receipts are reported by plan but refused at stage:
#          worktree registrations move via the git worktree machinery (r3), not
#          by file mv.
#
# Safety rails
#   - plan/runbook/status are read-only everywhere (safe against the live fleet).
#   - stage/check/delete MUTATE, and are refused BEFORE any filesystem effect
#     unless the owning repo's realpath is inside the fixture scope
#     ("$TMPDIR_DEFAULT" = realpath of ${TMPDIR:-/tmp}). This is the round-8
#     contract: the live fleet has no authorized targets and this tool cannot
#     touch it; there is no token override (a live-gated variant is a parent
#     integration decision, see impl-08.sh for that design).
#   - delete rm's strictly inside <repo>/.ufo-quarantine/<date>/ (realpath -P
#     prefix guard + date-shape guard); nothing outside is ever removed.
#   - Secret-shaped basenames (*.env, *credential*, *secret*, id_*, *.pem) are
#     never read: secrets-refusal. Symlinks in a digest scope: symlink-present.
#   - Targets containing tab/newline are refused (TSV-corruption guard).
#   - No git fetch/push/commit/branch/checkout/reset/rebase/worktree verbs; no
#     network; .ufo/state, .ufo/watchdog.log, ~/.config never opened.
#   - Hold: staged copies rest >= hold_seconds before check/delete. Defaults
#     450s for pushed, 86400s for anything else (SKILL.md flow 4-6). On the
#     fixture scope --hold-seconds N is honored in full (compressed-clock
#     testing); the flow must still complete within ONE receipt window
#     (qrun-23 F2).
#
# usage:
#   impl-07.sh --selftest [--keep]
#   impl-07.sh plan    [--json] [--stale-days N] <path>...
#   impl-07.sh runbook [--json] [--stale-days N] <path>...
#   impl-07.sh stage   [--json] [--stale-days N] [--hold-seconds N] <path>...
#   impl-07.sh check   --repo REPO --ticket ID [--json]
#   impl-07.sh delete  --repo REPO --ticket ID [--json]
#   impl-07.sh status  --repo REPO [--json]
#   impl-07.sh --help
set -euo pipefail
export LC_ALL=C

SELF_PATH=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/$(basename -- "${BASH_SOURCE[0]}")
SELF_DIR=${SELF_PATH%/*}
LANE_ROOT=$(cd "$SELF_DIR/.." && pwd)
VERIFY_TOOL=${SOUJI_VERIFY_TOOL:-$LANE_ROOT/tools/souji-verify.sh}
TMPDIR_SCOPE=$(realpath -- "${TMPDIR:-/tmp}" 2>/dev/null || printf '/tmp')
HOLD_PUSHED_DEFAULT=450
HOLD_OTHER_DEFAULT=86400
STALE_DAYS=1
JSON=0
KEEP=0
CMD=""
REPO_ARG=""
TICKET_ID=""
OP_HOLD=""

die_usage() { printf 'impl-07.sh: %s\n' "$1" >&2; exit 2; }
jesc() { local s=${1:-}; s=${s//\\/\\\\}; s=${s//\"/\\\"}; s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; s=${s//$'\r'/\\r}; printf '%s' "$s"; }
join_tab() { local out=$1 f; shift; for f in "$@"; do out+=$'\t'"$f"; done; printf '%s' "$out"; }
san() { local s=${1:-}; s=${s//$'\t'/ }; s=${s//$'\n'/ }; s=${s//$'\r'/ }; printf '%s' "$s"; }
say() { # record-type fields...  (printf-arg style: no $() nested inside escaped dquotes)
  local t=$1; shift
  if [ "$JSON" = 1 ]; then
    printf '{"rec":"%s"' "$(jesc "$t")"
    local f i=1
    for f in "$@"; do
      printf ',"f%s":"%s"' "$i" "$(jesc "$f")"
      i=$((i+1))
    done
    printf '}\n'
  else
    printf '%s\n' "$(join_tab "$t" "$@")"
  fi
}
warn() { printf 'impl-07.sh: %s\n' "$(san "$1")" >&2; }

# ---------------------------------------------------------------- CLI parsing
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) CMD=selftest; shift;;
    --keep) KEEP=1; shift;;
    --json) JSON=1; shift;;
    --stale-days) [ $# -ge 2 ] || die_usage "--stale-days needs a value"; STALE_DAYS=$2; shift 2;;
    --hold-seconds) [ $# -ge 2 ] || die_usage "--hold-seconds needs a value"; OP_HOLD=$2; shift 2;;
    --repo) [ $# -ge 2 ] || die_usage "--repo needs a value"; REPO_ARG=$2; shift 2;;
    --ticket) [ $# -ge 2 ] || die_usage "--ticket needs a value"; TICKET_ID=$2; shift 2;;
    --help|-h) sed -n '2,72p' "$SELF_PATH"; exit 0;;
    plan|runbook|stage|check|delete|status) CMD=$1; shift;;
    --) shift; break;;
    -*) die_usage "unknown argument: $1";;
    *) break;;
  esac
done
[ -n "$CMD" ] || { sed -n '52,72p' "$SELF_PATH" >&2; exit 2; }
case "$CMD" in
  check|delete|status) [ -n "$REPO_ARG" ] || die_usage "$CMD needs --repo REPO";;
esac
case "$CMD" in
  check|delete) [ -n "$TICKET_ID" ] || die_usage "$CMD needs --ticket ID";;
esac
case "$CMD" in
  stage) [ -n "$OP_HOLD" ] && { case "$OP_HOLD" in ''|*[!0-9]*) die_usage "--hold-seconds must be a non-negative integer";; esac; };;
esac

require_bins() {
  local c
  for c in git rg sha256sum realpath awk find sort xargs stat date; do
    command -v "$c" >/dev/null 2>&1 || { warn "missing required tool: $c"; exit 1; }
  done
}
require_bins

# ---------------------------------------------------------------- primitives
owning_repo() { # path -> worktree root on stdout, empty if none
  local p=$1 d
  if [ -d "$p" ]; then d=$p; else d=$(dirname -- "$p"); fi
  git -C "$d" rev-parse --show-toplevel 2>/dev/null || true
}
in_fixture_scope() { # repo_root -> 0 when inside TMPDIR_SCOPE
  local rp
  rp=$(realpath -P -- "$1" 2>/dev/null) || return 1
  case "$rp" in "$TMPDIR_SCOPE"/*) return 0;; *) return 1;; esac
}
bad_path_chars() { case "$1" in *$'\t'*|*$'\n'*|*$'\r'*) return 0;; *) return 1;; esac; }
is_secret_shaped() {
  local b=$1
  case "$b" in *.env|.*.env*|*credential*|*secret*|id_*|*.pem|*.key) return 0;; *) return 1;; esac
}
gate1_count() { # repo rel -> unpushed commits touching rel
  git -C "$1" log --branches --not --remotes --oneline -- "$2" 2>/dev/null | wc -l | tr -d ' '
}
gate2_tracked_count() { # repo rel -> porcelain entries touching rel, excluding untracked(??)
  git -C "$1" status --porcelain=v1 --untracked-files=all -- "$2" 2>/dev/null | grep -cv "^??" || true
}
gate2_untracked_count() { # repo rel -> untracked(??) porcelain entries touching rel
  git -C "$1" status --porcelain=v1 --untracked-files=all -- "$2" 2>/dev/null | grep -c "^??" || true
}
gate1_newer_than() { # repo rel epoch -> unpushed commits (committer time > epoch) touching rel
  git -C "$1" log --branches --not --remotes --format=%ct -- "$2" 2>/dev/null \
    | awk -v t="$3" '$1 > t' | wc -l | tr -d ' '
}
remote_ref_count() { git -C "$1" for-each-ref refs/remotes 2>/dev/null | wc -l | tr -d ' '; }
scratch_type() { # path -> "scratch" per souji-verify.spec.md classes, else ""
  local p=$1 b
  [ -e "$p" ] || { printf ''; return; }
  b=$(basename -- "$p")
  case "$p" in *.tmp) printf ''; return;; esac
  case "$b" in
    launch-*.json|*-draft.*|*.out|*.log) printf 'scratch'; return;;
  esac
  if [ -d "$p" ]; then case "$(basename -- "${p%/}")" in .scratch) printf 'scratch'; return;; esac; fi
  printf ''
}
repo_digest() { # path -> sha256 over content (file or sorted tree); "SYMLINK" on symlink
  local p=$1 links
  if [ -L "$p" ]; then printf 'SYMLINK'; return; fi
  if [ -f "$p" ]; then sha256sum -- "$p" | cut -d' ' -f1; return; fi
  links=$(find "$p" -type l 2>/dev/null | wc -l | tr -d ' ')
  if [ "${links:-0}" -gt 0 ]; then printf 'SYMLINK'; return; fi
  find "$p" -type f -print0 2>/dev/null | sort -z \
    | xargs -0 -r sha256sum 2>/dev/null | awk '{print $1}' | sha256sum | cut -d' ' -f1
}
live_refs() { # path -> live-reference count (self + D3 exclusions removed)
  local p=$1 name repo hits
  name=$(basename -- "$p")
  repo=$(owning_repo "$p"); [ -n "$repo" ] || repo=$PWD
  hits=$(rg -l --no-ignore --hidden -F "$name" "$repo" \
          -g '!.git' -g '!souji-shokunin/census/**' -g '!souji-shokunin/tests/**' \
          -g '!**/.ufo-quarantine/**' -g "!$p" 2>/dev/null | wc -l | tr -d ' ') || hits=0
  printf '%s' "${hits:-0}"
}
inline_receipt() { # path -> receipt or "" (verify-tool fallback; pushed/stale only)
  local p=$1 repo rel intro defref b t refs
  repo=$(owning_repo "$p"); b=$(basename -- "$p")
  is_secret_shaped "$b" && { printf ''; return; }
  [ -e "$p" ] || { printf ''; return; }
  [ -e "$p/.git" ] && { printf ''; return; }   # repo roots are not this tool's scope
  if [ -n "$repo" ]; then
    rel=${p#"$repo"/}; [ "$rel" = "$p" ] && rel=""
    intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$rel" 2>/dev/null || true)
    defref=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)
    if [ -z "$defref" ]; then
      refs=$(git -C "$repo" for-each-ref --format='%(refname:short)' refs/remotes/origin 2>/dev/null | grep -v ' HEAD$' || true)
      [ "$(printf '%s' "$refs" | grep -c .)" = 1 ] && defref=${refs##*/}
    fi
    if [ -n "$intro" ] && [ -n "$defref" ] \
       && git -C "$repo" merge-base --is-ancestor "$intro" "refs/remotes/origin/$defref" 2>/dev/null \
       && [ "$(gate1_count "$repo" "$rel")" -eq 0 ]; then
      printf 'pushed'; return
    fi
  fi
  t=$(scratch_type "$p")
  if [ -n "$t" ] && [ "$(live_refs "$p")" -eq 0 ] \
     && [ "$(find "$p" -maxdepth 0 -mtime +"$STALE_DAYS" 2>/dev/null | wc -l | tr -d ' ')" -ge 1 ]; then
    printf 'stale'; return
  fi
  printf ''
}
verify_receipt() { # path -> "receipt<TAB>evidence" or ""
  local p=$1 out verdict receipt ev
  if [ -n "$VERIFY_TOOL" ] && [ -f "$VERIFY_TOOL" ]; then
    out=$(env SHOKUNIN_ROOT="$(owning_repo "$p")" bash "$VERIFY_TOOL" --stale-days "$STALE_DAYS" -- "$p" 2>/dev/null | head -n1 || true)
    verdict=$(printf '%s' "$out" | awk -F'\t' '{print $3}')
    receipt=$(printf '%s' "$out" | awk -F'\t' '{print $4}')
    ev=$(printf '%s' "$out" | cut -f5-)
    if [ "$verdict" = "SAFE" ] && [ -n "$receipt" ] && [ "$receipt" != "none" ]; then
      printf '%s\t%s' "$receipt" "$ev"; return
    fi
    printf ''; return
  fi
  local r
  r=$(inline_receipt "$p")
  [ -n "$r" ] && printf '%s\tinline-fallback' "$r"
  printf ''
}

# manifest under the quarantine staging area (self-contained per owning repo)
q_root() { printf '%s/.ufo-quarantine' "$1"; }
manifest_path() { printf '%s/manifest.tsv' "$(q_root "$1")"; }
journal_path() { printf '%s/journal.log' "$(q_root "$1")"; }
journal() { # repo ticket event detail
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$2" "$3" "$(san "$4")" >> "$(journal_path "$1")"
}
manifest_get() { # repo ticket -> MF_* fields; rc 1 when absent
  MF_row=$(awk -F'\t' -v t="$2" '$1==t && !seen++ {print; exit}' "$(manifest_path "$1")" 2>/dev/null || true)
  [ -n "$MF_row" ] || return 1
  IFS=$'\t' read -r MF_ticket MF_date MF_orig MF_receipt MF_sha MF_evid MF_epoch MF_iso MF_hold MF_status MF_qpath <<<"$MF_row"
  return 0
}
manifest_set_status() { # repo ticket status
  awk -F'\t' -v t="$2" -v s="$3" 'BEGIN{OFS="\t"} $1==t {$10=s} {print}' \
    "$(manifest_path "$1")" > "$(manifest_path "$1").new" \
    && mv -f -- "$(manifest_path "$1").new" "$(manifest_path "$1")"
}

# ---------------------------------------------------------------- shared eval
EV_path=""; EV_repo=""; EV_rel=""; EV_g1=0; EV_g2=0; EV_g2t=0; EV_g2u=0; EV_receipt=""; EV_evid=""; EV_block=""
eval_target() { # path -> fills EV_*  (EV_path keeps the caller-given form; symlink checks use it)
  local p=$1 raw=$1
  EV_path=$raw; EV_repo=""; EV_rel=""; EV_g1=0; EV_g2=0; EV_g2t=0; EV_g2u=0; EV_receipt=""; EV_evid=""; EV_block=""
  bad_path_chars "$p" && { EV_block=malformed-path; return; }
  if [ ! -e "$p" ] && [ ! -L "$p" ]; then EV_block=unreachable; return; fi
  p=$(realpath -m -- "$p" 2>/dev/null) || p=$raw   # repo-relative strip needs an absolute path
  local b; b=$(basename -- "$p")
  if is_secret_shaped "$b"; then EV_block=secrets-refusal; return; fi
  EV_repo=$(owning_repo "$p")
  if [ -z "$EV_repo" ]; then EV_block=no-owning-repo; return; fi
  EV_rel=${p#"$EV_repo"/}
  if [ "$EV_rel" = "$p" ] || [ -z "$EV_rel" ]; then EV_block=repo-root-target; return; fi
  EV_g1=$(gate1_count "$EV_repo" "$EV_rel")
  EV_g2t=$(gate2_tracked_count "$EV_repo" "$EV_rel")
  EV_g2u=$(gate2_untracked_count "$EV_repo" "$EV_rel")
  local vr; vr=$(verify_receipt "$p")
  EV_receipt=${vr%%$'\t'*}
  EV_evid=${vr#*$'\t'}
  [ "$EV_evid" = "$vr" ] && EV_evid=""
  [ -n "$EV_receipt" ] || EV_block+=" no-receipt(g3)"
  [ "$EV_g1" -eq 0 ] || EV_block+=" unpushed-commits-touching(g1=$EV_g1)"
  [ "$EV_g2t" -eq 0 ] || EV_block+=" dirty-touching(g2=$EV_g2t)"
  if [ "$EV_g2u" -gt 0 ] && [ "$EV_receipt" != "stale" ]; then EV_block+=" untracked-blocks-receipt(g2u=$EV_g2u)"; fi
  EV_block=$(san "${EV_block# }")
}
emit_ticket() {
  local ev="g1=$EV_g1 g2t=$EV_g2t g2u=$EV_g2u g3=${EV_receipt:-none} repo=${EV_repo##*/} ${EV_evid:+ev=}$EV_evid"
  if [ -z "$EV_block" ]; then
    say TICKET "$EV_path" AUTHORIZED "$EV_receipt" "$(san "$ev")"
  else
    say TICKET "$EV_path" NOT-AUTHORIZED "blocked" "$(san "$EV_block | $ev")"
  fi
}

# ---------------------------------------------------------------- commands
cmd_plan() { local p; for p in "$@"; do eval_target "$p"; emit_ticket; done; }

cmd_runbook() { # derive the action that opens each blocked gate (read-only)
  local p
  for p in "$@"; do
    eval_target "$p"
    local blocked="" owner="" action=""
    if [ "$EV_g1" -gt 0 ]; then
      blocked+="g1 "; owner=operator
      action+="push ${EV_repo##*/}: $EV_g1 unpushed commit(s) touch the path; no receipt can hold until they land; "
    fi
    if [ "$EV_g2t" -gt 0 ]; then
      blocked+="g2 "; owner=${owner:-lane}
      action+="commit or revert the touching worktree changes; "
    fi
    if [ "$EV_g2u" -gt 0 ] && [ "$EV_receipt" != "stale" ] && [ -z "$(scratch_type "$p")" ]; then
      blocked+="g2u "; owner=${owner:-lane}
      action+="$EV_g2u untracked entr(y|ies) touch the path: only a stale receipt can carry untracked residue - confirm scratch-type + zero refs + age, else the candidate stays; "
    fi
    case "$EV_block" in
      unreachable) blocked+="exists "; owner=n-a; action+="target absent: nothing to authorize; ";;
      secrets-refusal) blocked+="secret "; owner=kagi-routed
        action+="credential-shaped path: route to kagi-shokunin; never read or remove here; ";;
      repo-root-target) blocked+="scope "; owner=n-a
        action+="receipt classes apply to paths inside a repo, not the repo root; ";;
    esac
    if [ -z "$EV_receipt" ] && [ -z "$(printf '%s' "$EV_block" | grep -E 'g1|g2t|unreachable|secret|repo-root|malformed|no-owning')" ]; then
      if [ "$(remote_ref_count "$EV_repo")" -eq 0 ] && [ -e "$EV_repo/$EV_rel" ]; then
        blocked+="g3 "; owner=operator
        action+="zero remote-tracking refs in ${EV_repo##*/} (origin absent or never pushed): pushed receipt unverifiable — create/push the remote (operator-owned), then re-plan; "
      elif [ -n "$(scratch_type "$p")" ]; then
        local refs; refs=$(live_refs "$p")
        if [ "${refs:-0}" -gt 0 ]; then
          blocked+="g3 "; owner=${owner:-lane}
          action+="stale blocked by $refs live reference(s): retire citations first (rg -l -F '$(basename -- "$p")' '${EV_repo##*/}'); "
        else
          blocked+="g3 "; owner=n-a
          local elig; elig=$(date -u -d "@$(( $(stat -c %Y "$p") + STALE_DAYS*86400 ))" +%FT%TZ 2>/dev/null || echo "mtime+${STALE_DAYS}d")
          action+="stale blocked by age: eligible after $elig — waiting is the only move; no action opens it early; "
        fi
      else
        blocked+="g3 "; owner=n-a
        action+="no receipt class applies (tracked, fresh, unledgered): candidate stays; "
      fi
    fi
    if [ -z "$blocked" ]; then
      blocked=none; owner=parent
      action="gates open: plan -> AUTHORIZED, then stage -> hold -> check -> delete within one receipt window"
    fi
    say GATE "$EV_path" "$(san "$blocked")" "$owner" "$(san "$action")"
  done
}

effective_hold() { # receipt -> seconds
  case "$1" in
    pushed) [ -n "$OP_HOLD" ] && { printf '%s' "$OP_HOLD"; return; }; printf '%s' "$HOLD_PUSHED_DEFAULT";;
    *) [ -n "$OP_HOLD" ] && { printf '%s' "$OP_HOLD"; return; }; printf '%s' "$HOLD_OTHER_DEFAULT";;
  esac
}

refuse() { # repo ticket-or-path reason
  say REFUSED "$2" "$3"
  journal "${1:-/none}" "-" refused "$(san "$2 :: $3")"
  FAIL_ANY=1
}

cmd_stage() {
  local p
  for p in "$@"; do
    eval_target "$p"
    if [ -n "$EV_block" ]; then
      case "$EV_block" in
        unreachable|secrets-refusal|malformed-path|repo-root-target|no-owning-repo)
          refuse "$EV_repo" "$p" "stage-denied: $EV_block"; continue;;
      esac
      if ! in_fixture_scope "$EV_repo"; then
        refuse "$EV_repo" "$p" "stage-denied: outside-fixture-scope(repo ${EV_repo##*/} is not under $TMPDIR_SCOPE; live fleet is never mutated by this tool)"
        continue
      fi
      refuse "$EV_repo" "$p" "stage-denied: $EV_block"; continue
    fi
    case "$EV_receipt" in
      pushed|stale|moved-to-obsidian) : ;;
      *) refuse "$EV_repo" "$p" "stage-denied: receipt-out-of-scope($EV_receipt): worktree registrations move via git worktree machinery (r3)"; continue;;
    esac
    if ! in_fixture_scope "$EV_repo"; then
      refuse "$EV_repo" "$p" "stage-denied: outside-fixture-scope(repo ${EV_repo##*/} is not under $TMPDIR_SCOPE; live fleet is never mutated by this tool)"
      continue
    fi
    local qroot qdir enc qpath sha hold epoch iso tid
    qroot=$(q_root "$EV_repo")
    qdir="$qroot/$(date -u +%F)"
    enc=${EV_rel//\//__}
    qpath="$qdir/$enc"
    if [ -e "$qpath" ] || [ -L "$qpath" ]; then
      refuse "$EV_repo" "$p" "stage-denied: quarantine-collision($enc)"; continue
    fi
    sha=$(repo_digest "$p")
    if [ "$sha" = "SYMLINK" ]; then refuse "$EV_repo" "$p" "stage-denied: symlink-present"; continue; fi
    hold=$(effective_hold "$EV_receipt")
    # PRE-MOVE evidence is captured here and is the second check's anchor
    # (qrun-23 F1: the receipt cannot be re-derived from the moved path).
    mkdir -p "$qdir"
    if git -C "$EV_repo" ls-files --error-unmatch -- "$EV_rel" >/dev/null 2>&1; then
      git -C "$EV_repo" mv -- "$EV_rel" "${qpath#"$EV_repo"/}" || { refuse "$EV_repo" "$p" "stage-denied: git-mv-failed"; continue; }
    else
      mv -- "$p" "$qpath" || { refuse "$EV_repo" "$p" "stage-denied: mv-failed"; continue; }
    fi
    epoch=$(date +%s); iso=$(date -u +%FT%TZ)
    tid="q$(date -u +%Y%m%dT%H%M%S)-$$-$RANDOM$RANDOM"
    if [ ! -f "$(manifest_path "$EV_repo")" ]; then
      printf 'ticket\tutc_date\torig_path\treceipt\tsha256\tpremove_evidence\tstage_epoch\tstage_iso\thold_seconds\tstatus\tqpath\n' \
        > "$(manifest_path "$EV_repo")"
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\tstaged\t%s\n' \
      "$tid" "$(date -u +%F)" "$EV_rel" "$EV_receipt" "$sha" "$(san "$EV_evid")" "$epoch" "$iso" "$hold" "${qpath#"$EV_repo"/}" \
      >> "$(manifest_path "$EV_repo")"
    journal "$EV_repo" "$tid" staged "$p -> $qpath (receipt=$EV_receipt hold=${hold}s sha=$sha ev=$EV_evid)"
    say STAGED "$tid" "$qpath" "$EV_receipt" "$sha"
  done
  [ "${FAIL_ANY:-0}" -eq 0 ] || exit 1
  return 0
}

cmd_check() { # second receipt check — consumes PRE-MOVE evidence (qrun-23 F1/F2)
  local repo=$REPO_ARG
  if ! in_fixture_scope "$repo"; then
    refuse "$repo" "$TICKET_ID" "check-denied: outside-fixture-scope"; exit 1
  fi
  if ! manifest_get "$repo" "$TICKET_ID"; then
    say CHECK "$TICKET_ID" FAIL "no-manifest-row"; exit 1
  fi
  local now; now=$(date +%s)
  local qabs="$repo/$MF_qpath"
  local fails=""
  [ "$MF_status" = "staged" ] || fails+="status=$MF_status(expected staged) "
  if [ $(( now - MF_epoch )) -lt "$MF_hold" ]; then
    fails+="hold-not-elapsed($(( now - MF_epoch ))s/${MF_hold}s) "
  fi
  if [ ! -e "$qabs" ]; then fails+="quarantine-copy-missing "; fi
  if [ -e "$qabs" ]; then
    local sha_now; sha_now=$(repo_digest "$qabs")
    if [ "$sha_now" = "SYMLINK" ]; then fails+="symlink-present(in-quarantine) "
    elif [ "$sha_now" != "$MF_sha" ]; then fails+="digest-drift(quarantine-copy-tampered) "; fi
  fi
  if [ -e "$repo/$MF_orig" ] || [ -L "$repo/$MF_orig" ]; then fails+="original-path-recreated(concurrent) "; fi
  local newg1; newg1=$(gate1_newer_than "$repo" "$MF_orig" "$MF_epoch")
  [ "${newg1:-0}" -eq 0 ] || fails+="new-unpushed-commits-touching(n=$newg1) "
  case "$MF_receipt" in
    stale)
      local refs; refs=$(live_refs "$repo/$MF_orig")
      [ "${refs:-0}" -eq 0 ] || fails+="receipt-lost(new-live-references=$refs) "
      ;;
    pushed)
      # anchored on pre-move evidence: intro commit ancestry cannot change
      # without a fetch (never run), the copy sha is verified above, and new
      # touching commits are caught by the g1-delta guard.
      ;;
    moved-to-obsidian)
      # ledger re-check is vault-side (read-only) and out of the fixture scope;
      # copy identity + g1-delta + hold carry the check. Documented limitation.
      ;;
    *) fails+="unknown-receipt($MF_receipt) ";;
  esac
  if [ -n "$fails" ]; then
    fails=$(san "$fails")
    journal "$repo" "$TICKET_ID" check-FAIL "$fails"
    say CHECK "$TICKET_ID" FAIL "$fails"
    exit 1
  fi
  manifest_set_status "$repo" "$TICKET_ID" second-checked
  local det="receipt=$MF_receipt anchor=pre-move hold=$(( now - MF_epoch ))s/${MF_hold}s sha=ok"
  journal "$repo" "$TICKET_ID" check-PASS "$det"
  say CHECK "$TICKET_ID" PASS "$det"
}

cmd_delete() {
  local repo=$REPO_ARG
  if ! in_fixture_scope "$repo"; then
    refuse "$repo" "$TICKET_ID" "delete-denied: outside-fixture-scope"; exit 1
  fi
  if ! manifest_get "$repo" "$TICKET_ID"; then
    say REFUSED "$TICKET_ID" "no-manifest-row"; exit 1
  fi
  if [ "$MF_status" != "second-checked" ]; then
    refuse "$repo" "$TICKET_ID" "delete-denied: status=$MF_status (second receipt check must PASS first)"
    exit 1
  fi
  local now; now=$(date +%s)
  if [ $(( now - MF_epoch )) -lt "$MF_hold" ]; then
    refuse "$repo" "$TICKET_ID" "delete-denied: hold-not-elapsed"; exit 1
  fi
  # escape guard: resolve the rm target and require it strictly inside
  # <repo>/.ufo-quarantine/<date>/, with a well-formed date dir and leaf name
  local qroot qdate leaf target
  case "$MF_date" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) : ;;
    *) refuse "$repo" "$TICKET_ID" "delete-denied: date-shape($MF_date)"; exit 1;;
  esac
  qroot=$(realpath -P -- "$(q_root "$repo")" 2>/dev/null) || { refuse "$repo" "$TICKET_ID" "delete-denied: no-quarantine-dir"; exit 1; }
  qdate=$(realpath -P -- "$qroot/$MF_date" 2>/dev/null) || { refuse "$repo" "$TICKET_ID" "delete-denied: no-date-dir"; exit 1; }
  leaf=$(basename -- "$MF_qpath")
  case "$leaf" in ""|"."|"..") refuse "$repo" "$TICKET_ID" "delete-denied: leaf-shape($leaf)"; exit 1;; esac
  case "$MF_qpath" in
    ..|../*|*/../*|*/..) refuse "$repo" "$TICKET_ID" "delete-denied: traversal-shape($MF_qpath)"; exit 1;;
  esac
  target=$(realpath -P -- "$qdate/$leaf" 2>/dev/null) || { refuse "$repo" "$TICKET_ID" "delete-denied: target-unresolvable"; exit 1; }
  case "$target" in
    "$qdate"/*) : ;;
    *) refuse "$repo" "$TICKET_ID" "delete-denied: quarantine-escape($target)"; exit 1;;
  esac
  [ "$qdate" != "$qroot" ] || { refuse "$repo" "$TICKET_ID" "delete-denied: date-dir-guard"; exit 1; }
  rm -rf -- "$target"
  manifest_set_status "$repo" "$TICKET_ID" deleted
  journal "$repo" "$TICKET_ID" deleted "rm $target (receipt=$MF_receipt sha=$MF_sha)"
  say DELETED "$TICKET_ID"
}

cmd_status() {
  local repo=$REPO_ARG mf
  mf=$(manifest_path "$repo")
  [ -f "$mf" ] || { say TICKETS "-" "no-manifest" "-" "-"; return 0; }
  awk -F'\t' 'NR>1 {print $1 "\t" $10 "\t" $3 "\t" $4 "\t" $11}' "$mf" | while IFS=$'\t' read -r t s o r q; do
    say TICKETS "$t" "$s" "$o" "$r" "$q"
  done
}

# ---------------------------------------------------------------- selftest
ST=""
WORK=""
record() { ST+="$1"$'\t'"$2"$'\t'"$(san "${3:-}")"$'\n'; printf '%s\t%s\t%s\n' "$1" "$2" "$(san "${3:-}")"; }
assert_contains() { # name needle haystack detail
  case "$3" in *"$2"*) record "$1" PASS "${4:-}"; return 0;; *) record "$1" FAIL "missing [$2] in [${3:0:220}] ${4:-}"; return 1;; esac
}
assert_eq() { # name expected observed detail
  if [ "$2" = "$3" ]; then record "$1" PASS "${4:-}"; return 0; fi
  record "$1" FAIL "expected=[$2] observed=[$3] ${4:-}"; return 1
}
run_tool() { bash "$SELF_PATH" "$@"; }

build_fixture() { # $1=dir -> repo at $1/work, bare origin at $1/origin.git; no push verb
  local d=$1
  git init -q --bare -b master "$d/origin.git"
  git clone -q "$d/origin.git" "$d/work" 2>/dev/null
  # c1 (pushed): lifecycle targets
  printf 'kept-v1\n' > "$d/work/data-kept.txt"
  mkdir -p "$d/work/data"
  printf 'kept-in-dir\n' > "$d/work/data/kept.txt"
  git -C "$d/work" add data-kept.txt data/kept.txt
  GIT_AUTHOR_DATE="2026-10-01T00:00:00+00:00" GIT_COMMITTER_DATE="2026-10-01T00:00:00+00:00" \
    git -C "$d/work" commit -q -m "c1 baseline"
  git -C "$d/work" update-ref refs/remotes/origin/master "$(git -C "$d/work" rev-parse HEAD)"
  git -C "$d/work" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  # c2 (pushed): gate2 target, then dirtied in the worktree
  printf 'clean-v1\n' > "$d/work/dirty-file.txt"
  git -C "$d/work" add dirty-file.txt
  GIT_AUTHOR_DATE="2026-10-01T00:00:00+00:00" GIT_COMMITTER_DATE="2026-10-01T00:00:00+00:00" \
    git -C "$d/work" commit -q -m "c2 dirty-file pushed shape"
  git -C "$d/work" update-ref refs/remotes/origin/master "$(git -C "$d/work" rev-parse HEAD)"
  printf 'dirty\n' >> "$d/work/dirty-file.txt"
  # c3 (UNPUSHED): gate1 target - introducing commit not on origin
  printf 'live-v1\n' > "$d/work/live-file.txt"
  git -C "$d/work" add live-file.txt
  GIT_AUTHOR_DATE="$(date -u +%FT%TZ)" GIT_COMMITTER_DATE="$(date -u +%FT%TZ)" \
    git -C "$d/work" commit -q -m "c3 live-file local-only"
  # untracked aged scratch (stale receipt) + aged non-scratch control
  printf 'stale log body\n' > "$d/work/launch-stale.json"
  touch -d '4 days ago' "$d/work/launch-stale.json"
  printf 'plain note\n' > "$d/work/plain-note.txt"
  touch -d '4 days ago' "$d/work/plain-note.txt"
}
 

cmd_selftest() {
  WORK=$(mktemp -d /tmp/souji07-selftest.XXXXXX) || { warn "mktemp failed"; exit 9; }
  case "$WORK" in "$TMPDIR_SCOPE"/souji07-selftest.*) : ;; *) warn "refusing WORK=$WORK"; exit 9;; esac
  # EXIT trap touches globals only (a trap reading function-locals goes unbound
  # under set -u — the defect class observed in sibling impl-08).
  trap 'chmod -R u+rwX "$WORK" 2>/dev/null || true; [ "$KEEP" = 1 ] || rm -rf -- "$WORK"' EXIT
  export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
  export GIT_TERMINAL_PROMPT=0 GIT_AUTHOR_NAME=souji07 GIT_AUTHOR_EMAIL=s07@fixture.local
  export GIT_COMMITTER_NAME=souji07 GIT_COMMITTER_EMAIL=s07@fixture.local
  local fx="$WORK/fx" fx0="$WORK/fx-zero" fx1="$WORK/fx-nohead" rc out tid qpath head_before
  build_fixture "$fx"
  git init -q -b master "$fx0"                       # zero-remote repo (r6 pitfall)
  printf 'z\n' > "$fx0/z.txt"
  git -C "$fx0" add z.txt
  GIT_AUTHOR_DATE="2026-10-01T00:00:00+00:00" GIT_COMMITTER_DATE="2026-10-01T00:00:00+00:00" \
    git -C "$fx0" commit -q -m z
  build_fixture "$fx1"
  git -C "$fx1/work" symbolic-ref -d refs/remotes/origin/HEAD   # D1 single-ref fallback

  # -- plan -------------------------------------------------------------
  out=$(run_tool plan "$fx/work/data-kept.txt" 2>/dev/null) || rc=$?
  assert_contains T01-plan-pushed $'\tAUTHORIZED\tpushed\t' "$out" || :
  out=$(run_tool plan "$fx/work/launch-stale.json" 2>/dev/null) || rc=$?
  assert_contains T02-plan-stale $'\tAUTHORIZED\t' "$out" "$out" || :
  assert_contains T02b-plan-stale-receipt $'\tstale\t' "$out" || :
  out=$(run_tool plan "$fx/work/plain-note.txt" 2>/dev/null) || rc=$?
  assert_contains T03-no-receipt-class "NOT-AUTHORIZED" "$out" "$out" || :
  assert_contains T03b-no-receipt-reason "no-receipt(g3)" "$out" || :
  out=$(run_tool plan "$fx/work/live-file.txt" 2>/dev/null) || rc=$?
  assert_contains T04-gate1-block "NOT-AUTHORIZED" "$out" || :
  assert_contains T04b-gate1-reason "unpushed-commits-touching(g1=" "$out" || :
  out=$(run_tool plan "$fx/work/dirty-file.txt" 2>/dev/null) || rc=$?
  assert_contains T05-gate2-block "NOT-AUTHORIZED" "$out" || :
  assert_contains T05b-gate2-reason "dirty-touching(g2=" "$out" || :
  out=$(run_tool plan "$fx0/z.txt" 2>/dev/null) || rc=$?
  assert_contains T06-zero-remote-fail-closed "NOT-AUTHORIZED" "$out" "$out" || :
  out=$(run_tool plan "$fx1/work/data-kept.txt" 2>/dev/null) || rc=$?
  assert_contains T07-single-ref-pushed $'\tpushed\t' "$out" "$out" || :
  printf 'K=V\n' > "$fx/work/app.env"
  out=$(run_tool plan "$fx/work/app.env" 2>/dev/null) || rc=$?
  assert_contains T08-secrets-refusal "secrets-refusal" "$out" || :
  mkdir -p "$fx/work/linkdir" && ln -s /etc/hostname "$fx/work/linkdir/dangle"
  out=$(run_tool plan "$fx/work/linkdir" 2>/dev/null) || rc=$?
  assert_contains T09-plan-symlink-block "NOT-AUTHORIZED" "$out" "$out" || :
  out=$(run_tool plan "$fx/work/ghost.txt" 2>/dev/null) || rc=$?
  assert_contains T10-unreachable "unreachable" "$out" || :
  out=$(run_tool plan "$fx/work" 2>/dev/null) || rc=$?
  assert_contains T11-repo-root-refused "repo-root-target" "$out" || :

  # -- full pushed lifecycle (tracked: git mv, NO commit) ----------------
  head_before=$(git -C "$fx/work" rev-parse HEAD)
  rc=0; out=$(run_tool stage --hold-seconds 1 "$fx/work/data-kept.txt" 2>/dev/null) || rc=$?
  assert_eq T12-stage-rc "0" "$rc" "$out" || :
  assert_contains T12b-stage-ok "STAGED" "$out" || :
  tid=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}')
  qpath=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $3}')
  assert_eq T13-original-gone "0" "$([ -e "$fx/work/data-kept.txt" ] && echo 1 || echo 0)" || :
  assert_eq T14-qpath-exists "1" "$([ -e "$qpath" ] && echo 1 || echo 0)" "qpath=$qpath" || :
  assert_contains T15-no-commit 'R  data-kept.txt ->' "$(git -C "$fx/work" status --porcelain)" "$(git -C "$fx/work" status --porcelain | head -1)" || :
  assert_eq T15b-head-unchanged "$head_before" "$(git -C "$fx/work" rev-parse HEAD)" "no commit verb ran" || :
  rc=0; out=$(run_tool check --repo "$fx/work" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T16-check-hold-refused "hold-not-elapsed" "$out" || :
  assert_eq T16b-check-refused-rc "1" "$rc" || :
  assert_eq T17-still-staged "0" "$([ -e "$fx/work/data-kept.txt" ] && echo 1 || echo 0)" "artifact stays in quarantine on refused check" || :
  sleep 1.3
  rc=0; out=$(run_tool check --repo "$fx/work" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T18-check-pass "PASS" "$out" || :
  assert_eq T18b-check-pass-rc "0" "$rc" || :
  assert_contains T18c-anchor "anchor=pre-move" "$out" || :
  rc=0; out=$(run_tool delete --repo "$fx/work" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T19-delete-ok "DELETED" "$out" || :
  assert_eq T19b-delete-rc "0" "$rc" || :
  assert_eq T20-qpath-gone "0" "$([ -e "$qpath" ] && echo 1 || echo 0)" || :
  out=$(run_tool delete --repo "$fx/work" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T21-redelete-refused "status=deleted" "$out" || :

  # -- stale lifecycle (untracked: plain mv), incl. a stale dir ----------
  mkdir -p "$fx/work/.scratch" && printf 'old scratch\n' > "$fx/work/.scratch/old-note.log"
  touch -d '4 days ago' "$fx/work/.scratch" "$fx/work/.scratch/old-note.log"
  rc=0; out=$(run_tool stage --hold-seconds 1 "$fx/work/launch-stale.json" "$fx/work/.scratch" 2>/dev/null) || rc=$?
  assert_eq T22-stale-stage-rc "0" "$rc" "$out" || :
  local tid_f tid_d
  tid_f=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}' | sed -n 1p)
  tid_d=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}' | sed -n 2p)
  assert_contains T23-stale-moved "STAGED" "$out" || :
  assert_eq T23b-staged-two "2" "$(printf '%s' "$out" | grep -c '^STAGED')" || :
  sleep 1.3
  rc=0; out=$(run_tool check --repo "$fx/work" --ticket "$tid_f" 2>/dev/null) || rc=$?
  assert_contains T24-stale-check-file "PASS" "$out" || :
  rc=0; out=$(run_tool check --repo "$fx/work" --ticket "$tid_d" 2>/dev/null) || rc=$?
  assert_contains T24b-stale-check-dir "PASS" "$out" || :
  run_tool delete --repo "$fx/work" --ticket "$tid_f" >/dev/null 2>&1 || :
  run_tool delete --repo "$fx/work" --ticket "$tid_d" >/dev/null 2>&1 || :
  assert_eq T25-stale-cleaned "0" "$(find "$fx/work/.ufo-quarantine" -mindepth 2 2>/dev/null | grep -c . || true)" "quarantine emptied of completed tickets" || :

  # -- tamper: quarantine copy modified -> check FAIL, delete refused ----
  printf 't-body\n' > "$fx/work/plain-note.txt"   # scratch-shape? no: plain
  rm -f "$fx/work/plain-note.txt"
  printf 't-body\n' > "$fx/work/tamper.log"
  touch -d '4 days ago' "$fx/work/tamper.log"
  out=$(run_tool stage --hold-seconds 1 "$fx/work/tamper.log" 2>/dev/null) || rc=$?
  tid=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}')
  qpath=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $3}')
  printf 'tampered\n' >> "$qpath"
  sleep 1.3
  rc=0; out=$(run_tool check --repo "$fx/work" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T26-tamper-caught "digest-drift" "$out" || :
  assert_eq T26b-tamper-rc "1" "$rc" || :
  out=$(run_tool delete --repo "$fx/work" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T27-delete-refused-after-fail "status=staged" "$out" || :
  assert_eq T27b-copy-preserved "1" "$([ -e "$qpath" ] && echo 1 || echo 0)" "tampered copy kept for forensics" || :

  # -- lane wakes mid-hold: new unpushed commit touching path -----------
  printf 'w-body\n' > "$fx/work/wake.log"
  touch -d '4 days ago' "$fx/work/wake.log"
  out=$(run_tool stage --hold-seconds 1 "$fx/work/wake.log" 2>/dev/null) || rc=$?
  tid=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}')
  printf 'new\n' > "$fx/work/data/wake-touch.txt"
  git -C "$fx/work" add data/wake-touch.txt
  # NOT touching wake.log's own path? data/ is a different path; make one that touches the same dir:
  printf 'new2\n' > "$fx/work/wake-2.txt"
  sleep 1.3
  rc=0; out=$(run_tool check --repo "$fx/work" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_eq T28-untouched-path-check-pass "0" "$rc" "different path stays PASS" || :
  # now commit a change that DOES touch the staged path's location
  printf 'gone\n' > "$fx/work/wake-gone.txt"; rm -f "$fx/work/wake-gone.txt"
  printf 'later\n' > "$fx/work/wake2.log"
  touch -d '4 days ago' "$fx/work/wake2.log"
  out=$(run_tool stage --hold-seconds 1 "$fx/work/wake2.log" 2>/dev/null) || rc=$?
  tid=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}')
  printf 'x\n' > "$fx/work/wake2.new"
  git -C "$fx/work" add wake2.new
  GIT_AUTHOR_DATE="$(date -u +%FT%TZ)" GIT_COMMITTER_DATE="$(date -u +%FT%TZ)" \
    git -C "$fx/work" commit -q -m "c5 mid-hold commit (touches repo, not path)"
  # commit touching the exact orig path: recreate + commit the deletion is too
  # exotic; use an unpushed commit whose pathspec hits the file's dir listing
  # the c5 commit touches other paths only; the gate is path-exact
  sleep 1.3
  rc=0; out=$(run_tool check --repo "$fx/work" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T29-midhold-other-commit-still-pass "PASS" "$out" || :
  # exact-path hit: commit an edit to the same-named file elsewhere? instead:
  # simulate by staging wake2.log, then committing a change to a file at the
  # SAME path is impossible (it is moved) — the g1-delta fires on new commits
  # whose pathspec matches orig: prove the guard fires via a fresh ticket on a
  # TRACKED file whose path gets an unpushed commit mid-hold.
  printf 'tracked-v1\n' > "$fx/work/midhold.txt"
  git -C "$fx/work" add midhold.txt
  GIT_AUTHOR_DATE="2026-10-01T00:00:00+00:00" GIT_COMMITTER_DATE="2026-10-01T00:00:00+00:00" \
    git -C "$fx/work" commit -q -m "c6 midhold pushed shape"
  git -C "$fx/work" update-ref refs/remotes/origin/master "$(git -C "$fx/work" rev-parse HEAD)"
  out=$(run_tool stage --hold-seconds 1 "$fx/work/midhold.txt" 2>/dev/null) || rc=$?
  tid=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}')
  printf 'tracked-v2\n' > "$fx/work/midhold-restored.txt"; rm -f "$fx/work/midhold-restored.txt"
  # make git history show an unpushed commit touching midhold.txt after stage:
  printf 'tracked-v2\n' > "$fx/work/midhold.txt"
  git -C "$fx/work" add midhold.txt
  GIT_AUTHOR_DATE="$(date -u +%FT%TZ)" GIT_COMMITTER_DATE="$(date -u +%FT%TZ)" \
    git -C "$fx/work" commit -q -m "c7 recreates orig path mid-hold"
  sleep 1.3
  rc=0; out=$(run_tool check --repo "$fx/work" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T30-midhold-new-commit-caught "original-path-recreated" "$out" || :
  assert_eq T30b-midhold-rc "1" "$rc" || :

  # -- unknown ticket ----------------------------------------------------
  rc=0; out=$(run_tool check --repo "$fx/work" --ticket q-nonexistent 2>/dev/null) || rc=$?
  assert_contains T31-unknown-ticket "no-manifest-row" "$out" || :
  assert_eq T31b-unknown-rc "1" "$rc" || :

  # -- LIVE RAIL: lane repo stage must refuse and create nothing ---------
  rc=0; out=$(run_tool stage "$LANE_ROOT/SKILL.md" 2>/dev/null) || rc=$?
  assert_contains T32-live-refused "outside-fixture-scope" "$out" || :
  assert_eq T32b-live-rc "1" "$rc" || :
  assert_eq T32c-lane-untouched "0" "$([ -e "$LANE_ROOT/.ufo-quarantine" ] && echo 1 || echo 0)" "no .ufo-quarantine in live lane" || :
  rc=0; out=$(run_tool check --repo "$LANE_ROOT" --ticket q-x 2>/dev/null) || rc=$?
  assert_contains T33-live-check-denied "outside-fixture-scope" "$out" || :
  assert_eq T33b-live-check-rc "1" "$rc" || :
  rc=0; out=$(run_tool delete --repo "$LANE_ROOT" --ticket q-x 2>/dev/null) || rc=$?
  assert_contains T34-live-delete-denied "outside-fixture-scope" "$out" || :
  assert_eq T34b-live-delete-rc "1" "$rc" || :
  rc=0; out=$(run_tool plan "$LANE_ROOT/SKILL.md" 2>/dev/null) || rc=$?
  assert_eq T35-plan-live-read-only-ok "0" "$rc" "plan is read-only and allowed on live fleet" || :

  # -- escape guard: forged manifest row pointing outside ----------------
  printf 'e-body\n' > "$fx/work/escape.log"
  touch -d '4 days ago' "$fx/work/escape.log"
  out=$(run_tool stage --hold-seconds 1 "$fx/work/escape.log" 2>/dev/null) || rc=$?
  tid=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}')
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    q-forged "$(date -u +%F)" "../../../etc" stale x forged 0 "$(date -u +%FT%TZ)" 0 second-checked \
    "$(date -u +%F)/../../etc/hostname" >> "$fx/work/.ufo-quarantine/manifest.tsv"
  rc=0; out=$(run_tool delete --repo "$fx/work" --ticket q-forged 2>/dev/null) || rc=$?
  assert_contains T36-escape-refused "delete-denied" "$out" || :
  assert_eq T36b-escape-rc "1" "$rc" || :
  assert_eq T36c-etc-hostname-intact "1" "$([ -f /etc/hostname ] && echo 1 || echo 0)" "guard target never removed" || :
  sleep 1.3
  run_tool check --repo "$fx/work" --ticket "$tid" >/dev/null 2>&1 || :
  rc=0; out=$(run_tool delete --repo "$fx/work" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_eq T37-legit-ticket-after-forge "0" "$rc" "$out" || :

  # -- runbook: gate-opening actions -------------------------------------
  printf 'rb-push\n' > "$fx/work/rb-push.txt"
  git -C "$fx/work" add rb-push.txt
  GIT_AUTHOR_DATE="2026-10-01T00:00:00+00:00" GIT_COMMITTER_DATE="2026-10-01T00:00:00+00:00" \
    git -C "$fx/work" commit -q -m "rb c2 pushed shape"
  git -C "$fx/work" update-ref refs/remotes/origin/master "$(git -C "$fx/work" rev-parse HEAD)"
  printf 'rb-g1\n' > "$fx/work/rb-g1.txt"
  git -C "$fx/work" add rb-g1.txt
  GIT_AUTHOR_DATE="$(date -u +%FT%TZ)" GIT_COMMITTER_DATE="$(date -u +%FT%TZ)" \
    git -C "$fx/work" commit -q -m "rb c1 unpushed"
  out=$(run_tool runbook "$fx/work/rb-g1.txt" 2>/dev/null) || rc=$?
  assert_contains T38-runbook-g1-operator "operator" "$out" "$out" || :
  assert_contains T38b-runbook-g1-push "push work" "$out" || :
  out=$(run_tool runbook "$fx0/z.txt" 2>/dev/null) || rc=$?
  assert_contains T39-runbook-no-remote "operator" "$out" || :
  assert_contains T39b-runbook-no-remote-action "unpushed commit" "$out" || :
  printf 'young\n' > "$fx/work/young.out"
  out=$(run_tool runbook "$fx/work/young.out" 2>/dev/null) || rc=$?
  assert_contains T40-runbook-young-stale "eligible after" "$out" || :
  out=$(run_tool runbook "$fx/work/app.env" 2>/dev/null) || rc=$?
  assert_contains T41-runbook-secret-kagi "kagi" "$out" || :
  out=$(run_tool runbook "$fx/work/rb-push.txt" 2>/dev/null) || rc=$?
  assert_contains T42-runbook-open-gates "gates open" "$out" || :

  # -- status + json + usage ---------------------------------------------
  rc=0; out=$(run_tool status --repo "$fx/work" 2>/dev/null) || rc=$?
  assert_eq T43-status-rc "0" "$rc" || :
  assert_contains T43b-status-has-deleted "deleted" "$out" || :
  out=$(run_tool --json plan "$fx/work/dirty-file.txt" 2>/dev/null) || rc=$?
  printf '%s' "$out" | python3 -c 'import json,sys
n=0
for line in sys.stdin:
    json.loads(line); n+=1
assert n>=1' && assert_eq T44-json-parseable "0" "$?" || record T44-json-parseable FAIL "python jsonl validation"
  rc=0; run_tool >/dev/null 2>&1 || rc=$?
  assert_eq T45-usage-noargs "2" "$rc" || :
  rc=0; run_tool --bogus-flag >/dev/null 2>&1 || rc=$?
  assert_eq T45b-usage-badflag "2" "$rc" || :
  rc=0; run_tool check --ticket q-x >/dev/null 2>&1 || rc=$?
  assert_eq T45c-usage-check-needs-repo "2" "$rc" || :
  rc=0; run_tool stage --hold-seconds abc "$fx/work/data/kept.txt" >/dev/null 2>&1 || rc=$?
  assert_eq T45d-usage-bad-hold "2" "$rc" || :
  rc=0; run_tool --help >/dev/null 2>&1 || rc=$?
  assert_eq T45e-help-rc "0" "$rc" || :

  # -- inline fallback (verify tool hidden) -------------------------------
  out=$(SOUJI_VERIFY_TOOL="" run_tool plan "$fx1/work/data-kept.txt" 2>/dev/null)
  assert_contains T46-inline-pushed $'\tpushed\t' "$out" "$out" || :
  printf 'fb\n' > "$fx/work/fallback.log"
  touch -d '4 days ago' "$fx/work/fallback.log"
  out=$(SOUJI_VERIFY_TOOL="" run_tool plan "$fx/work/fallback.log" 2>/dev/null)
  assert_contains T46b-inline-stale $'\tstale\t' "$out" || :

  # -- cwd independence + no residue --------------------------------------
  rc=0; ( cd / && run_tool --help >/dev/null 2>&1 ) || rc=$?
  assert_eq T47-cwd-independent "0" "$rc" "--help from /" || :
  rc=0; ( cd / && run_tool plan "$fx/work/dirty-file.txt" >/dev/null 2>&1 ) || rc=$?
  assert_eq T47b-plan-cwd-independent "0" "$rc" "read-only plan from foreign cwd" || :
  # -- keep/cleanup semantics via child runs (non-recursive) --------------
  if [ "${SOUJI07_NO_NEST:-0}" = "1" ]; then
    record T48-fixture-cleaned SKIP "nested run: verified by the parent run"
  else
    local kout kdir
    kout=$( { SOUJI07_NO_NEST=1 bash "$SELF_PATH" --selftest --keep 2>/dev/null || true; } | tail -n1)
    kdir=$(printf '%s' "$kout" | awk -F'fixture=' '{print $2}')
    assert_eq T49-keep-honored "1" "$([ -d "$kdir" ] && echo 1 || echo 0)" "kdir=$kdir" || :
    rm -rf -- "$kdir"
    kout=$( { SOUJI07_NO_NEST=1 bash "$SELF_PATH" --selftest 2>/dev/null || true; } | tail -n1)
    kdir=$(printf '%s' "$kout" | awk -F'fixture=' '{print $2}')
    assert_eq T48-fixture-cleaned "0" "$([ -d "$kdir" ] && echo 1 || echo 0)" "kdir=$kdir" || :
  fi

  # -- emit ----------------------------------------------------------------
  local pass fail
  pass=$(printf '%s' "$ST" | awk -F'\t' '$2=="PASS"' | wc -l | tr -d ' ')
  fail=$(printf '%s' "$ST" | awk -F'\t' '$2=="FAIL"' | wc -l | tr -d ' ')
  printf 'SELFTEST\tpass=%s\tfail=%s\tfixture=%s\n' "$pass" "$fail" "$WORK"
  [ "${fail:-0}" -eq 0 ] || exit 1
  exit 0
}

FAIL_ANY=0
case "$CMD" in
  plan)    [ $# -ge 1 ] || die_usage "plan needs target paths"; cmd_plan "$@";;
  runbook) [ $# -ge 1 ] || die_usage "runbook needs target paths"; cmd_runbook "$@";;
  stage)   [ $# -ge 1 ] || die_usage "stage needs target paths"; cmd_stage "$@";;
  check)   cmd_check;;
  delete)  cmd_delete;;
  status)  cmd_status;;
  selftest) cmd_selftest;;
esac
exit 0
