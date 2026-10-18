#!/usr/bin/env bash
# impl-08.sh — souji-quarantine: gate-checked quarantine lifecycle (S08, round 8)
#
# Implements the r7 pre-staged execution_plan_template
# (census/round-7/quarantine-plan.json) as an executable, fail-closed tool:
#
#   plan    gates+receipt for targets, emit AUTHORIZED / NOT-AUTHORIZED tickets
#   stage   re-verify ALL gates, then mv target into <repo>/.ufo-quarantine/<utc-date>/
#   check   second receipt check after the hold window (SKILL.md removal flow 5)
#   delete  rm the quarantined copy, escape-guarded (flow 6)
#   runbook derive the operator-owned action that would open each blocked gate
#
# Output grammar (TSV, one record per line; --json emits JSONL with fields
# record,f1..f5):
#   TICKET<TAB>path<TAB>AUTHORIZED|NOT-AUTHORIZED<TAB>receipt-or-block<TAB>evidence
#   STAGED<TAB>ticket<TAB>quarantine-path<TAB>receipt<TAB>sha256
#   REFUSED<TAB>path-or-ticket<TAB>reason
#   CHECK<TAB>ticket<TAB>PASS|FAIL<TAB>detail
#   DELETED<TAB>ticket
#   GATE<TAB>path<TAB>blocked-gates<TAB>owner<TAB>opening-action
#
# Gates (authorization_rule, r7 quarantine-plan.json — re-verified at every step):
#   gate1  git -C <repo> log --branches --not --remotes --oneline -- <path> -> empty
#   gate2  git -C <repo> status --porcelain=v1 --untracked-files=all -- <path> -> empty
#   gate3  receipt holds via tools/souji-verify.sh (installed behavior wins;
#          inline pushed/stale fallback ONLY when that tool is absent; any other
#          class is then receipt-unverifiable — fail-closed)
#
# Safety rails (violation = refusal or selftest failure):
#   - Mutations (stage/check/delete) NEVER touch a repo whose root is outside
#     /tmp unless env SOUJI_OPERATOR_TOKEN is set AND --operator-token matches
#     (operator sign-off). Refusal happens BEFORE any mkdir/mv/rm.
#   - delete resolves its rm target under <repo>/.ufo-quarantine/<date>/ with a
#     realpath guard that also rejects crafted manifest dates (".."); nothing
#     outside .ufo-quarantine is ever removed.
#   - Secret-shaped basenames (*.env, *credential*, *secret*, id_*, *.pem) are
#     never read: secrets-refusal. Symlink inside a digest scope: symlink-present.
#   - The TOOL never runs git fetch/push/commit/branch/checkout/reset/rebase or
#     any network verb. (The --selftest HARNESS commits inside its mktemp
#     fixtures only, as the round-2 runners do.) .ufo/state, .ufo/watchdog.log,
#     ~/.config are never opened.
#   - Hold: staged copies rest >= hold_seconds before check/delete. Defaults
#     450s (pushed) / 86400s (other). --hold-seconds applies in full only to
#     /tmp fixture repos; live repos get max(default, N).
#
# Known-scope limits (honest, v1): file/dir artifacts only — worktree
# metadata-prune targets are out of scope (plan reports them via gate evidence
# on the owning repo; runbook prints their opening action); receipts obsidian
# and metadata-prune are delegated to souji-verify.sh when present and refused
# as unverifiable by the inline fallback.
#
# Fixture scope (round-8 universal rule): everything is proven on mktemp
# fixture repos via --selftest. The live fleet has no authorized targets; the
# selftest proves the tool refuses to mutate the lane repo (nothing created).
#
# usage:
#   impl-08.sh --selftest [--keep]
#   impl-08.sh plan    [--json] [--stale-days N] [--root REPO] <path>...
#   impl-08.sh runbook [--json] [--stale-days N] [--root REPO] <path>...
#   impl-08.sh stage   [--json] [--stale-days N] [--hold-seconds N]
#                      [--operator-token T] [--root REPO] <path>...
#   impl-08.sh check   [--json] --repo REPO --ticket ID
#   impl-08.sh delete  [--json] --repo REPO --ticket ID [--operator-token T]
#   impl-08.sh --help
# exit: 0 = evaluated clean (NOT-AUTHORIZED tickets still exit 0); 1 = refusal,
#       failed check, or selftest failure; 2 = usage.
set -euo pipefail
export LC_ALL=C

SELF_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")
SELF_DIR=${SELF_PATH%/*}
LANE_ROOT=$(cd "$SELF_DIR/.." && pwd)
VERIFY_TOOL=${SOUJI_VERIFY_TOOL:-$LANE_ROOT/tools/souji-verify.sh}
HOLD_PUSHED_DEFAULT=450
HOLD_OTHER_DEFAULT=86400
STALE_DAYS=1
JSON=0
KEEP=0
FAIL_RC=0
CMD=""
ROOT_OVERRIDE=""
OP_TOKEN=""
HOLD_OVERRIDE=""
TICKET_ID=""

san() { local s=${1:-}; s=${s//$'\t'/ }; s=${s//$'\n'/ }; s=${s//$'\r'/ }; printf '%s' "$s"; }
warn() { printf 'impl-08.sh: %s\n' "$(san "$1")" >&2; }
die_usage() { warn "$1"; exit 2; }
jesc() { local s=${1:-}; s=${s//\\/\\\\}; s=${s//\"/\\\"}; s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; s=${s//$'\r'/\\r}; printf '%s' "$s"; }
say() { # record f1 f2 ...  -> TSV line, or JSONL {"record":..,"f1":..}
  if [ "$JSON" = 1 ]; then
    local out="{\"record\":\"$(jesc "$1")\"" a b i=1; shift
    for a in "$@"; do out+=",\"f$i\":\"$(jesc "$a")\""; i=$((i+1)); done
    printf '%s}\n' "$out"
  else
    local out=$1; shift; local a
    for a in "$@"; do out+=$'\t'"$(san "$a")"; done
    printf '%s\n' "$out"
  fi
}

# ---------------------------------------------------------------- CLI parsing
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest)       CMD=selftest; shift;;
    --keep)           KEEP=1; shift;;
    --json)           JSON=1; shift;;
    --stale-days)     [ $# -ge 2 ] || die_usage "--stale-days needs a value"; STALE_DAYS=$2; shift 2;;
    --root|--repo)    [ $# -ge 2 ] || die_usage "$1 needs a value"; ROOT_OVERRIDE=$2; shift 2;;
    --ticket)         [ $# -ge 2 ] || die_usage "--ticket needs a value"; TICKET_ID=$2; shift 2;;
    --operator-token) [ $# -ge 2 ] || die_usage "--operator-token needs a value"; OP_TOKEN=$2; shift 2;;
    --hold-seconds)   [ $# -ge 2 ] || die_usage "--hold-seconds needs a value"; HOLD_OVERRIDE=$2; shift 2;;
    --help|-h)        sed -n '7,66p' "$SELF_PATH"; exit 0;;
    plan|runbook|stage|check|delete) CMD=$1; shift;;
    --) shift;;
    -*) die_usage "unknown argument: $1";;
    *) break;;
  esac
done
[ -n "$CMD" ] || { sed -n '54,66p' "$SELF_PATH" >&2; exit 2; }
case "$CMD" in
  check|delete) [ -n "$TICKET_ID" ] || die_usage "$CMD needs --ticket ID";;
  plan|runbook|stage) [ $# -ge 1 ] || die_usage "$CMD needs target paths";;
esac

require_tools() { local c; for c in git rg sha256sum realpath stat find sort awk grep; do
  command -v "$c" >/dev/null 2>&1 || { warn "missing required tool: $c"; exit 1; }; done; }
require_tools

is_secret_shaped() { case "$1" in *.env|*credential*|*secret*|id_*|*.pem) return 0;; *) return 1;; esac; }
bad_path_chars()   { case "$1" in *$'\t'*|*$'\n'*|*$'\r'*) return 0;; *) return 1;; esac; }
is_fixture_root()  { case "$1" in /tmp/*) return 0;; *) return 1;; esac; }

owning_repo() { # path -> worktree root (may be absent path inside a repo)
  local p=$1 dir
  if [ -d "$p" ]; then dir=$p; else dir=$(dirname "$p"); fi
  git -C "$dir" rev-parse --show-toplevel 2>/dev/null || true
}

# live-mutation rail: rc0 = allowed; rc1 = reason on stdout
mutation_allowed() { # repo_root token_arg
  local repo=$1 token=${2:-} env_tok=${SOUJI_OPERATOR_TOKEN:-}
  if is_fixture_root "$repo"; then return 0; fi
  if [ -z "$env_tok" ]; then
    printf 'live-operator-token-required (repo %s outside /tmp; set SOUJI_OPERATOR_TOKEN + --operator-token)' "$repo"; return 1
  fi
  if [ -z "$token" ] || [ "$token" != "$env_tok" ]; then printf 'operator-token-mismatch'; return 1; fi
  return 0
}

gate1_count() { git -C "$1" log --branches --not --remotes --oneline -- "$2" 2>/dev/null | wc -l | tr -d ' '; }
gate2_count() { git -C "$1" status --porcelain=v1 --untracked-files=all -- "$2" 2>/dev/null | wc -l | tr -d ' '; }
gate1_newer_than() { git -C "$1" log --branches --not --remotes --format=%ct -- "$2" 2>/dev/null \
  | awk -v t="$3" '$1 > t' | wc -l | tr -d ' '; }

scratch_type() { # path -> "scratch" or "" (souji-verify.spec.md stale classes)
  local p=$1 b
  [ -e "$p" ] || { printf ''; return; }
  b=$(basename "$p")
  case "$b" in *.tmp) printf ''; return;; esac
  case "$b" in
    launch-*.json|*-draft.*|*.out|*.log|*checkpoint*.json|*checkpoint*.png) printf 'scratch'; return;;
  esac
  if [ -d "$p" ]; then case "$(basename "${p%/}")" in .scratch) printf 'scratch'; return;; esac; fi
  printf ''
}

repo_digest() { # path -> sha256 (file) or tree digest; prints SYMLINK on links in scope
  local p=$1
  [ -L "$p" ] && { printf 'SYMLINK'; return; }
  if [ -f "$p" ]; then sha256sum "$p" | cut -d' ' -f1; return; fi
  if [ "$(find "$p" -type l 2>/dev/null | wc -l | tr -d ' ')" -gt 0 ]; then printf 'SYMLINK'; return; fi
  find "$p" -type f -print0 2>/dev/null | sort -z | xargs -0 -r sha256sum 2>/dev/null \
    | sha256sum | cut -d' ' -f1
}

live_refs() { # path -> count of referencing files (D3 exclusions, self excluded)
  local p=$1 name repo hits=0
  name=$(basename "$p")
  repo=$(owning_repo "$p"); [ -n "$repo" ] || repo=$PWD
  hits=$(rg -l --no-ignore --hidden -F "$name" "$repo" \
        -g '!.git' -g '!souji-shokunin/census/**' -g '!souji-shokunin/tests/**' \
        -g '!**/.ufo-quarantine/**' 2>/dev/null \
        | grep -Fvx -- "$p" | grep -Fvx -- "${p#"$repo"/}" | grep -Fvx -- "./${p#"$repo"/}" \
        | wc -l | tr -d ' ') || hits=0
  printf '%s' "$hits"
}

default_ref() { # repo -> branch name of resolved origin default (existing refs only)
  local d
  d=$(git -C "$1" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@') || d=""
  if [ -z "$d" ]; then
    local o
    o=$(git -C "$1" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null \
        | grep -v '/HEAD$' | sed 's@^refs/remotes/origin/@@')
    [ "$(printf '%s\n' "$o" | grep -c . || true)" -eq 1 ] && d=$o
  fi
  printf '%s' "$d"
}

inline_receipt() { # path -> receipt or "" (fallback when souji-verify.sh absent)
  local p=$1 repo rel intro d t
  is_secret_shaped "$(basename "$p")" && { printf ''; return; }
  [ -e "$p" ] || { printf ''; return; }
  [ -d "$p" ] && [ -e "$p/.git" ] && { printf ''; return; } # repo-root: not this tool
  repo=$(owning_repo "$p")
  if [ -n "$repo" ]; then
    rel=${p#"$repo"/}; [ "$rel" = "$p" ] && rel=""
    intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$rel" 2>/dev/null || true)
    d=$(default_ref "$repo")
    if [ -n "$intro" ] && [ -n "$d" ] \
       && git -C "$repo" merge-base --is-ancestor "$intro" "origin/$d" 2>/dev/null \
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

verify_receipt() { # path -> receipt or ""
  local p=$1 out verdict receipt
  if [ -n "$VERIFY_TOOL" ] && [ -f "$VERIFY_TOOL" ]; then
    out=$(bash "$VERIFY_TOOL" --stale-days "$STALE_DAYS" "$p" 2>/dev/null | head -n1 || true)
    verdict=$(printf '%s' "$out" | cut -f3)   # grammar: VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence
    receipt=$(printf '%s' "$out" | cut -f4)
    if [ "$verdict" = "SAFE" ] && [ -n "$receipt" ] && [ "$receipt" != "none" ]; then printf '%s' "$receipt"; return; fi
    printf ''; return
  fi
  inline_receipt "$p"
}

# ---------------------------------------------------------------- target eval
eval_target() { # sets EV_path EV_repo EV_rel EV_g1 EV_g2 EV_receipt EV_block EV_ev
  local p=$1
  EV_path=$p; EV_repo=""; EV_rel=""; EV_g1=0; EV_g2=0; EV_receipt=""; EV_block=""; EV_ev=""
  if bad_path_chars "$p"; then EV_block=malformed-path; return; fi
  if [ ! -e "$p" ] && [ ! -L "$p" ]; then EV_block=unreachable; return; fi
  if is_secret_shaped "$(basename "$p")"; then EV_block=secrets-refusal; return; fi
  EV_repo=${ROOT_OVERRIDE:-$(owning_repo "$p")}
  if [ -z "$EV_repo" ]; then EV_block=no-owning-repo; return; fi
  EV_rel=${p#"$EV_repo"/}; [ "$EV_rel" = "$p" ] && EV_rel=""
  EV_g1=$(gate1_count "$EV_repo" "$EV_rel")
  EV_g2=$(gate2_count "$EV_repo" "$EV_rel")
  EV_receipt=$(verify_receipt "$p")
  [ "$EV_g1" -eq 0 ] || EV_block+=" unpushed-commits-touching(g1=$EV_g1)"
  [ "$EV_g2" -eq 0 ] || EV_block+=" dirty-touching(g2=$EV_g2)"
  [ -n "$EV_receipt" ] || EV_block+=" no-receipt(g3)"
  EV_ev="g1=$EV_g1 g2=$EV_g2 g3=${EV_receipt:-none}"
  EV_block=$(san "${EV_block# }")
}

# ---------------------------------------------------------------- subcommands
cmd_plan() { local p; for p in "$@"; do eval_target "$p"
  if [ -z "$EV_block" ]; then say TICKET "$EV_path" AUTHORIZED "$EV_receipt" "$EV_ev"
  else say TICKET "$EV_path" NOT-AUTHORIZED "blocked" "$EV_block | $EV_ev"; fi; done; }

cmd_runbook() {
  local p
  for p in "$@"; do
    eval_target "$p"
    local blocked="" owner="" action="" st refs elig
    if [ "$EV_block" = unreachable ]; then
      say GATE "$EV_path" "exists" "n-a" "target absent: nothing to authorize"; continue
    fi
    case "$EV_block" in secrets-refusal)
      say GATE "$EV_path" "secret" "kagi-routed" "credential-shaped path: route to kagi-shokunin; never read or remove here"; continue;; esac
    if [ "$EV_g1" -gt 0 ]; then
      blocked+="g1 "; owner=operator
      action+="push ${EV_repo##*/} (${EV_g1} unpushed commit(s) touch this path — receipts cannot hold until they land); "
    fi
    if [ "$EV_g2" -gt 0 ]; then
      blocked+="g2 "; owner=${owner:-lane-owner}
      action+="commit or revert the touching worktree changes; "
    fi
    st=$(scratch_type "$p")
    if [ -n "$st" ]; then
      refs=$(live_refs "$p")
      if [ "$refs" -gt 0 ]; then
        blocked+="ref "; owner=${owner:-lane-owner}
        action+="stale blocked by $refs live reference(s): retire citations (rg -l -F '$(basename "$p")' <repo>); "
      fi
      if [ "$(find "$p" -maxdepth 0 -mtime +"$STALE_DAYS" 2>/dev/null | wc -l | tr -d ' ')" -lt 1 ]; then
        blocked+="age "
        elig=$(date -u -d "@$(( $(stat -c %Y "$p") + STALE_DAYS * 86400 ))" +%FT%TZ 2>/dev/null || echo "mtime+${STALE_DAYS}d")
        action+="stale blocked by age: eligible after $elig — waiting is the only opener; "
      fi
    fi
    if [ -z "$EV_receipt" ]; then
      blocked+="g3 "
      if [ "$(git -C "$EV_repo" for-each-ref refs/remotes 2>/dev/null | wc -l | tr -d ' ')" -eq 0 ]; then
        owner=${owner:-operator}
        action+="no remote-tracking refs exist locally (pushed unverifiable): restore/push origin — operator-owned — then re-run plan; "
      elif [ -z "$st" ]; then
        owner=${owner:-n-a}
        action+="no receipt class applies (tracked, fresh, unledgered): candidate stays; "
      fi
    fi
    if [ -z "$blocked" ]; then
      say GATE "$EV_path" "none" "n-a" "gates open; authorize via plan, then stage->hold->check->delete"
    else
      say GATE "$EV_path" "$(san "${blocked% }")" "${owner:-n-a}" "$(san "${action%; }")"
    fi
  done
}

manifest_path() { printf '%s/.ufo-quarantine/manifest.tsv' "$1"; }
journal_path()  { printf '%s/.ufo-quarantine/journal.log' "$1"; }
journal() { printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$2" "$3" "$(san "$4")" >> "$(journal_path "$1")"; }

effective_hold() { # receipt -> seconds; --hold-seconds full only on /tmp fixtures
  local base
  case "$1" in pushed) base=$HOLD_PUSHED_DEFAULT;; *) base=$HOLD_OTHER_DEFAULT;; esac
  if [ -n "$HOLD_OVERRIDE" ] && [ "$HOLD_OVERRIDE" -ge 1 ] 2>/dev/null \
     && [ -n "${CUR_REPO:-}" ] && is_fixture_root "$CUR_REPO"; then
    printf '%s' "$HOLD_OVERRIDE"; return
  fi
  if [ -n "$HOLD_OVERRIDE" ] && [ "$HOLD_OVERRIDE" -gt "$base" ] 2>/dev/null; then printf '%s' "$HOLD_OVERRIDE"; return; fi
  printf '%s' "$base"
}

cmd_stage() {
  local p allowed reason="" tid
  for p in "$@"; do
    eval_target "$p"
    if [ -n "$EV_block" ]; then
      say REFUSED "$p" "stage-denied: $EV_block"
      # round rule: no live-lane writes — journal only where .ufo-quarantine already exists
      if [ -n "$EV_repo" ] && [ -d "$EV_repo/.ufo-quarantine" ]; then
        journal "$EV_repo" "-" stage-refused "$p :: $EV_block"
      fi
      FAIL_RC=1; continue
    fi
    CUR_REPO=$EV_repo
    reason=""; allowed=$(mutation_allowed "$EV_repo" "$OP_TOKEN") || reason=$allowed
    if [ -n "$reason" ]; then
      say REFUSED "$p" "$reason"
      if [ -d "$EV_repo/.ufo-quarantine" ]; then journal "$EV_repo" "-" stage-refused "$p :: $reason"; fi
      FAIL_RC=1; continue
    fi
    local qroot qdir enc qpath sha hold epoch iso
    qroot="$EV_repo/.ufo-quarantine"; qdir="$qroot/$(date -u +%F)"
    enc=${EV_rel//\//__}; [ -n "$enc" ] || enc=repo-root
    qpath="$qdir/$enc"
    if [ -e "$qpath" ]; then
      say REFUSED "$p" "stage-denied: quarantine-collision($enc)"; journal "$EV_repo" "-" stage-refused "$p :: collision"
      FAIL_RC=1; continue
    fi
    sha=$(repo_digest "$p")
    if [ "$sha" = "SYMLINK" ]; then
      say REFUSED "$p" "stage-denied: symlink-present"; journal "$EV_repo" "-" stage-refused "$p :: symlink"
      FAIL_RC=1; continue
    fi
    hold=$(effective_hold "$EV_receipt")
    mkdir -p "$qdir"
    mv -- "$p" "$qpath"
    epoch=$(date +%s); iso=$(date -u +%FT%TZ)
    tid="q$(date -u +%Y%m%dT%H%M%S)-$$-$RANDOM"
    if [ ! -f "$(manifest_path "$EV_repo")" ]; then
      printf 'ticket\tutc_date\torig_path\treceipt\tsha256\tstage_epoch\tstage_iso\thold_seconds\tstatus\tqpath\n' \
        > "$(manifest_path "$EV_repo")"
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$tid" "$(date -u +%F)" "$EV_rel" "$EV_receipt" "$sha" "$epoch" "$iso" "$hold" staged "${qpath#"$EV_repo"/}" \
      >> "$(manifest_path "$EV_repo")"
    journal "$EV_repo" "$tid" staged "$p -> $qpath receipt=$EV_receipt hold=${hold}s sha=$sha"
    say STAGED "$tid" "$qpath" "$EV_receipt" "$sha"
  done
}

manifest_get() { # repo ticket -> MF_* ; rc1 if row missing
  MF_row=$(awk -F'\t' -v t="$2" '$1==t && !seen++ {print; exit}' "$(manifest_path "$1")" 2>/dev/null || true)
  [ -n "$MF_row" ] || return 1
  local dummy
  IFS=$'\t' read -r MF_ticket MF_date MF_orig MF_receipt MF_sha MF_epoch MF_iso MF_hold MF_status MF_qpath <<< "$MF_row"
  return 0
}

cmd_check() {
  local repo=$ROOT_OVERRIDE
  [ -n "$repo" ] || die_usage "check needs --repo REPO"
  manifest_get "$repo" "$TICKET_ID" || { say CHECK "$TICKET_ID" FAIL "no-manifest-row"; exit 1; }
  local now fails="" qpath sha_now newg1 refs r2 intro d
  now=$(date +%s)
  qpath="$repo/$MF_qpath"
  [ "$MF_status" = staged ] || fails+="status=$MF_status(expected staged) "
  if [ $(( now - MF_epoch )) -lt "$MF_hold" ]; then fails+="hold-not-elapsed($(( now - MF_epoch ))s/${MF_hold}s) "; fi
  if [ ! -e "$qpath" ]; then fails+="quarantine-copy-missing "; fi
  if [ -e "$qpath" ]; then
    sha_now=$(repo_digest "$qpath")
    if [ "$sha_now" = "SYMLINK" ]; then fails+="symlink-present(in-quarantine) "
    elif [ "$sha_now" != "$MF_sha" ]; then fails+="digest-drift(quarantine-copy-tampered) "; fi
  fi
  if [ -e "$repo/$MF_orig" ]; then fails+="original-path-recreated(concurrent) "; fi
  newg1=$(gate1_newer_than "$repo" "$MF_orig" "$MF_epoch")
  [ "$newg1" -eq 0 ] || fails+="new-unpushed-commits-touching(n=$newg1) "
  r2=""
  case "$MF_receipt" in
    pushed)
      intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$MF_orig" 2>/dev/null || true)
      d=$(default_ref "$repo")
      if [ -n "$intro" ] && [ -n "$d" ] && git -C "$repo" merge-base --is-ancestor "$intro" "origin/$d" 2>/dev/null; then
        r2=pushed
      else fails+="receipt-lost(pushed-no-longer-ancestor) "; fi
      ;;
    stale)
      refs=$(live_refs "$repo/$MF_orig")
      if [ "${refs:-0}" -gt 0 ] 2>/dev/null; then fails+="receipt-lost(new-live-references=$refs) "; else r2=stale; fi
      ;;
    *) fails+="unknown-receipt($MF_receipt) ";;
  esac
  if [ -n "$fails" ]; then
    journal "$repo" "$TICKET_ID" check-FAIL "$(san "$fails")"
    say CHECK "$TICKET_ID" FAIL "$(san "$fails")"
    exit 1
  fi
  awk -F'\t' -v t="$TICKET_ID" 'BEGIN{OFS="\t"} $1==t{$9="second-checked"} {print}' \
    "$(manifest_path "$repo")" > "$(manifest_path "$repo").new" && mv -f -- "$(manifest_path "$repo").new" "$(manifest_path "$repo")"
  journal "$repo" "$TICKET_ID" check-PASS "receipt=$r2 held=$(( now - MF_epoch ))s/${MF_hold}s"
  say CHECK "$TICKET_ID" PASS "receipt=$r2 held=$(( now - MF_epoch ))s/${MF_hold}s"
}

cmd_delete() {
  local repo=$ROOT_OVERRIDE
  [ -n "$repo" ] || die_usage "delete needs --repo REPO"
  # authorization rail FIRST: a live-repo delete is refused before anything is read or touched
  local reason="" allowed now qc qdate rel enc target
  allowed=$(mutation_allowed "$repo" "$OP_TOKEN") || reason=$allowed
  if [ -n "$reason" ]; then
    say REFUSED "$TICKET_ID" "$reason"
    # round rule: no live-lane writes — journal only where .ufo-quarantine already exists
    if [ -d "$repo/.ufo-quarantine" ]; then journal "$repo" "$TICKET_ID" delete-refused "$reason"; fi
    exit 1
  fi
  manifest_get "$repo" "$TICKET_ID" || { say REFUSED "$TICKET_ID" "no-manifest-row"; exit 1; }
  now=$(date +%s)
  if [ "$MF_status" != second-checked ]; then
    say REFUSED "$TICKET_ID" "delete-denied: status=$MF_status (second receipt check must pass first)"
    journal "$repo" "$TICKET_ID" delete-refused "status=$MF_status"; exit 1
  fi
  if [ $(( now - MF_epoch )) -lt "$MF_hold" ]; then
    say REFUSED "$TICKET_ID" "delete-denied: hold-not-elapsed"
    journal "$repo" "$TICKET_ID" delete-refused "hold"; exit 1
  fi
  # escape guard: target must resolve to <qc>/<single-date-dir>/<basename>
  if ! qc=$(realpath -P -- "$repo/.ufo-quarantine" 2>/dev/null); then
    say REFUSED "$TICKET_ID" "delete-denied: no-quarantine-dir"; exit 1
  fi
  if ! qdate=$(realpath -P -- "$qc/$MF_date" 2>/dev/null); then
    say REFUSED "$TICKET_ID" "delete-denied: bad-date-dir"; journal "$repo" "$TICKET_ID" delete-refused "bad-date"; exit 1
  fi
  rel=${qdate#"$qc"/}
  if [ -z "$rel" ] || case "$rel" in */*) true;; *) false;; esac; then
    say REFUSED "$TICKET_ID" "delete-denied: date-dir-guard($rel)"; journal "$repo" "$TICKET_ID" delete-refused "date-dir-guard"; exit 1
  fi
  enc=${MF_qpath##*/}
  if ! target=$(realpath -P -- "$qdate/$enc" 2>/dev/null); then target="$qdate/$enc-nonexistent"; fi
  if [ "$target" != "$qdate" ] && case "$target" in "$qdate"/*) false;; *) true;; esac; then
    say REFUSED "$TICKET_ID" "delete-denied: quarantine-escape"; journal "$repo" "$TICKET_ID" delete-refused "escape"; exit 1
  fi
  [ "$target" != "$qdate" ] || { say REFUSED "$TICKET_ID" "delete-denied: date-dir-target"; exit 1; }
  rm -rf -- "$target"
  awk -F'\t' -v t="$TICKET_ID" 'BEGIN{OFS="\t"} $1==t{$9="deleted"} {print}' \
    "$(manifest_path "$repo")" > "$(manifest_path "$repo").new" && mv -f -- "$(manifest_path "$repo").new" "$(manifest_path "$repo")"
  journal "$repo" "$TICKET_ID" deleted "rm $target receipt=$MF_receipt sha=$MF_sha"
  say DELETED "$TICKET_ID"
}

# ---------------------------------------------------------------- selftest
ST=""
record() { ST+="$1"$'\t'"$2"$'\t'"$(san "${3:-}")"$'\n'; }
assert_eq() { # name expected observed [detail]
  if [ "$2" = "$3" ]; then record "$1" PASS "${4:-}"; else record "$1" FAIL "expected=[$2] observed=[$3] ${4:-}"; return 1; fi
}
assert_contains() { # name needle haystack [detail]
  case "$3" in *"$2"*) record "$1" PASS "${4:-}";; *) record "$1" FAIL "missing [$2] in [$(san "${3:0:160}")]"; return 1;; esac
}
run_tool() { bash "$SELF_PATH" "$@"; }
commit_at() { GIT_AUTHOR_DATE="$2" GIT_COMMITTER_DATE="$2" git -C "$1" commit -q -m "$3"; }
wire_origin() { git -C "$1" update-ref refs/remotes/origin/master "$(git -C "$1" rev-parse HEAD)"; }
future() { date -u -d "+$1 min" +%FT%T+00:00; }

cmd_selftest() {
  WORK=$(mktemp -d /tmp/souji08-selftest.XXXXXX)
  case "$WORK" in /tmp/souji08-selftest.*) : ;; *) warn "refusing WORK=$WORK"; exit 9;; esac
  trap 'chmod -R u+rwX "$WORK" 2>/dev/null || true; [ "$KEEP" = 1 ] || rm -rf "$WORK"' EXIT
  export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
  export GIT_TERMINAL_PROMPT=0
  export GIT_AUTHOR_NAME=souji08 GIT_AUTHOR_EMAIL=s08@fixture.local
  export GIT_COMMITTER_NAME=souji08 GIT_COMMITTER_EMAIL=s08@fixture.local
  local fx="$WORK/fxA" out rc tid qpath

  git init -q -b master "$fx"
  mkdir -p "$fx/data"
  printf 'kept-v1\n' > "$fx/data/kept.txt"
  printf 't0-v1\n'    > "$fx/data/t0.txt"
  printf 'scratch log v1\n' > "$fx/note.log"
  git -C "$fx" add data/kept.txt data/t0.txt note.log
  commit_at "$fx" "2026-10-14T00:00:00+00:00" "c1: pushed base"
  touch -d '3 days ago' "$fx/note.log"
  git clone -q --bare "$fx" "$fx.origin.git"
  git -C "$fx" remote add origin "$fx.origin.git"
  wire_origin "$fx"
  git -C "$fx" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

  # T1/T2 plan: pushed + stale authorized
  out=$(run_tool plan "$fx/data/kept.txt" 2>/dev/null)
  assert_contains T1-plan-pushed "AUTHORIZED" "$out" "$out" || FAIL_RC=1
  assert_contains T1-plan-pushed-receipt "$(printf '\tpushed\t')" "$out" || FAIL_RC=1
  out=$(run_tool plan "$fx/note.log" 2>/dev/null)
  assert_contains T2-plan-scratch "AUTHORIZED" "$out" "$out" || FAIL_RC=1
  # installed behavior: pushed verifies before stale, so a committed scratch
  # file reports pushed — accept any non-none receipt
  case "$(printf '%s' "$out" | cut -f4)" in
    pushed|stale) record T2-plan-scratch-receipt PASS "receipt=$(printf '%s' "$out" | cut -f4)";;
    *) record T2-plan-scratch-receipt FAIL "receipt=[$(printf '%s' "$out" | cut -f4)]"; FAIL_RC=1;;
  esac

  # T3 gate1: local-only commit touching target -> blocked
  printf 'kept-v2\n' > "$fx/data/kept.txt"
  git -C "$fx" add data/kept.txt
  commit_at "$fx" "2026-10-18T00:00:00+00:00" "c2: local-only edit"
  out=$(run_tool plan "$fx/data/kept.txt" 2>/dev/null)
  assert_contains T3-gate1-block "NOT-AUTHORIZED" "$out" || FAIL_RC=1
  assert_contains T3-gate1-reason "unpushed-commits-touching" "$out" || FAIL_RC=1

  # T4 gate2: untracked file -> dirty-touching -> blocked (r7 rule)
  printf 'dirty\n' > "$fx/data/dirty.txt"
  out=$(run_tool plan "$fx/data/dirty.txt" 2>/dev/null)
  assert_contains T4-gate2-block "NOT-AUTHORIZED" "$out" || FAIL_RC=1
  assert_contains T4-gate2-reason "dirty-touching" "$out" || FAIL_RC=1
  rm -f "$fx/data/dirty.txt"

  # T5 full pushed lifecycle: stage -> hold-refusal -> check -> delete
  out=$(run_tool stage --hold-seconds 1 "$fx/data/t0.txt" 2>/dev/null)
  assert_contains T5-stage "STAGED" "$out" "$out" || FAIL_RC=1
  tid=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}')
  qpath=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $3}')
  assert_eq T5-qpath-exists "1" "$([ -e "$qpath" ] && echo 1 || echo 0)" "$qpath" || FAIL_RC=1
  assert_eq T5-original-gone "0" "$([ -e "$fx/data/t0.txt" ] && echo 1 || echo 0)" || FAIL_RC=1
  rc=0; out=$(run_tool check --repo "$fx" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T5-check-hold-refused "hold-not-elapsed" "$out" "$out" || FAIL_RC=1
  assert_eq T5-check-hold-rc "1" "$rc" || FAIL_RC=1
  sleep 1.3
  rc=0; out=$(run_tool check --repo "$fx" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T5-check-pass "PASS" "$out" || FAIL_RC=1
  assert_eq T5-check-pass-rc "0" "$rc" || FAIL_RC=1
  rc=0; out=$(run_tool delete --repo "$fx" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T5-delete "DELETED" "$out" "$out" || FAIL_RC=1
  assert_eq T5-delete-rc "0" "$rc" || FAIL_RC=1
  assert_eq T5-copy-gone "0" "$([ -e "$qpath" ] && echo 1 || echo 0)" || FAIL_RC=1
  out=$(run_tool delete --repo "$fx" --ticket "$tid" 2>/dev/null || true)
  assert_contains T5-redelete-refused "status=deleted" "$out" || FAIL_RC=1

  # T6 stale lifecycle end-to-end
  out=$(run_tool stage --hold-seconds 1 "$fx/note.log" 2>/dev/null)
  assert_contains T6-stale-stage "STAGED" "$out" "$out" || FAIL_RC=1
  tid=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}')
  qpath=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $3}')
  sleep 1.3
  out=$(run_tool check --repo "$fx" --ticket "$tid" 2>/dev/null) || true
  assert_contains T6-stale-check "PASS" "$out" || FAIL_RC=1
  run_tool delete --repo "$fx" --ticket "$tid" >/dev/null 2>&1 || FAIL_RC=1
  assert_eq T6-stale-deleted "0" "$([ -e "$qpath" ] && echo 1 || echo 0)" || FAIL_RC=1

  # T7 tamper: quarantined copy modified -> check FAIL, delete refused, copy preserved
  printf 't7\n' > "$fx/t7.txt"; git -C "$fx" add t7.txt
  commit_at "$fx" "$(future 5)" "c3: t7 pushed-shape"; wire_origin "$fx"
  out=$(run_tool stage --hold-seconds 1 "$fx/t7.txt" 2>/dev/null)
  tid=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}')
  qpath=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $3}')
  printf 'tampered\n' >> "$qpath"
  sleep 1.3
  rc=0; out=$(run_tool check --repo "$fx" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T7-tamper-caught "digest-drift" "$out" "$out" || FAIL_RC=1
  assert_eq T7-tamper-rc "1" "$rc" || FAIL_RC=1
  out=$(run_tool delete --repo "$fx" --ticket "$tid" 2>/dev/null || true)
  assert_contains T7-delete-refused "status=staged" "$out" || FAIL_RC=1
  assert_eq T7-copy-preserved "1" "$([ -e "$qpath" ] && echo 1 || echo 0)" "tampered copy kept for forensics" || FAIL_RC=1
  T7_TICKET=$tid

  # T8 new unpushed commit mid-hold touching path -> check FAIL
  printf 't8\n' > "$fx/data/t8.txt"; git -C "$fx" add data/t8.txt
  commit_at "$fx" "$(future 7)" "c4: t8 pushed-shape"; wire_origin "$fx"
  out=$(run_tool stage --hold-seconds 1 "$fx/data/t8.txt" 2>/dev/null)
  tid=$(printf '%s' "$out" | awk -F'\t' '$1=="STAGED"{print $2}')
  git -C "$fx" rm -q --cached data/t8.txt
  printf 't8-local\n' > "$fx/data/t8-local.txt"; git -C "$fx" add data/t8-local.txt
  commit_at "$fx" "$(future 9)" "c5: local-only, touches data/t8.txt + t8-local"
  sleep 1.3
  rc=0; out=$(run_tool check --repo "$fx" --ticket "$tid" 2>/dev/null) || rc=$?
  assert_contains T8-new-unpushed-caught "new-unpushed-commits-touching" "$out" "$out" || FAIL_RC=1
  assert_eq T8-rc "1" "$rc" || FAIL_RC=1

  # T9 secrets / symlink / unreachable refusals
  printf 'K=V\n' > "$fx/app.env"
  out=$(run_tool plan "$fx/app.env" 2>/dev/null)
  assert_contains T9-secrets-refusal "secrets-refusal" "$out" || FAIL_RC=1
  mkdir -p "$fx/linkdir"; ln -sf /etc/hostname "$fx/linkdir/dangling"
  assert_eq T9-symlink-refused "SYMLINK" "$(repo_digest "$fx/linkdir")" || FAIL_RC=1
  out=$(run_tool plan "$fx/ghost.txt" 2>/dev/null)
  assert_contains T9-unreachable "unreachable" "$out" || FAIL_RC=1

  # T10 LIVE-REPO RAIL: lane target refused, lane tree untouched; token mismatch refused
  out=$(run_tool stage "$LANE_ROOT/LOG.md" 2>/dev/null) || true
  assert_contains T10-live-stage-refused "stage-denied" "$out" "$out" || FAIL_RC=1
  assert_eq T10-lane-untouched "0" "$([ -e "$LANE_ROOT/.ufo-quarantine" ] && echo 1 || echo 0)" \
    "no .ufo-quarantine created in live lane" || FAIL_RC=1
  out=$(SOUJI_OPERATOR_TOKEN=right run_tool delete --repo "$LANE_ROOT" --ticket qnone --operator-token wrong 2>/dev/null) || true
  assert_contains T10-token-mismatch "operator-token-mismatch" "$out" "$out" || FAIL_RC=1
  assert_eq T10-lane-still-untouched "0" "$([ -e "$LANE_ROOT/.ufo-quarantine" ] && echo 1 || echo 0)" \
    "rail refusal journals nothing into the live lane" || FAIL_RC=1

  # T11 crafted-manifest escape attempts: root file must survive
  printf 'root-treasure\n' > "$fx/rootfile"
  printf 'qcraft1\t..\tdata/t8.txt\tstale\tx\t0\t2026-01-01T00:00:00Z\t0\tsecond-checked\t../rootfile\n' \
    >> "$fx/.ufo-quarantine/manifest.tsv"
  out=$(run_tool delete --repo "$fx" --ticket qcraft1 2>/dev/null) || true
  assert_contains T11-dotdot-date-refused "date-dir-guard" "$out" "$out" || FAIL_RC=1
  assert_eq T11-rootfile-survives-1 "1" "$([ -e "$fx/rootfile" ] && echo 1 || echo 0)" || FAIL_RC=1
  printf 'qcraft2\t1970-01-01\tdata/t8.txt\tstale\tx\t0\t0\t0\tsecond-checked\t1970-01-01/../../../rootfile\n' \
    >> "$fx/.ufo-quarantine/manifest.tsv"
  out=$(run_tool delete --repo "$fx" --ticket qcraft2 2>/dev/null) || true
  assert_eq T11-rootfile-survives-2 "1" "$([ -e "$fx/rootfile" ] && echo 1 || echo 0)" \
    "traversal basename can only resolve inside the date dir" || FAIL_RC=1

  # T12 runbook: gate-opening actions derived live
  out=$(run_tool runbook "$fx/data/t8-local.txt" 2>/dev/null)
  assert_contains T12-runbook-push "push fxA" "$out" "$out" || FAIL_RC=1
  assert_contains T12-runbook-owner "$(printf '\toperator\t')" "$out" || FAIL_RC=1
  printf 'young\n' > "$fx/young.out"
  out=$(run_tool runbook "$fx/young.out" 2>/dev/null)
  assert_contains T12-runbook-age "eligible after" "$out" "$out" || FAIL_RC=1
  out=$(run_tool runbook "$fx/data/kept.txt" 2>/dev/null)
  assert_contains T12-runbook-kept-open "gates open" "$out" "kept.txt fully pushed after wire-forward — runbook reports gates open" || FAIL_RC=1

  # T13 inline fallback (verify tool hidden): pushed still authorized on clean target
  printf 't13\n' > "$fx/data/t13.txt"; git -C "$fx" add data/t13.txt
  commit_at "$fx" "$(future 11)" "c6: t13 pushed-shape"; wire_origin "$fx"
  out=$(SOUJI_VERIFY_TOOL=/nonexistent-verify-tool run_tool plan "$fx/data/t13.txt" 2>/dev/null)
  assert_contains T13-inline-pushed "AUTHORIZED" "$out" "$out" || FAIL_RC=1

  # T14 --json shape
  out=$(run_tool --json plan "$fx/data/t13.txt" 2>/dev/null | head -n1)
  if printf '%s' "$out" | grep -qF '"record":"TICKET"' \
     && printf '%s' "$out" | grep -qF '"AUTHORIZED"' \
     && printf '%s' "$out" | grep -q '^{' \
     && printf '%s' "$out" | grep -q '}$'; then
    record T14-json-shape PASS "jsonl ticket shape"
  else
    record T14-json-shape FAIL "got [$(san "$out")]"
    FAIL_RC=1
  fi

  local pass fail
  pass=$(printf '%s' "$ST" | awk -F'\t' '$2=="PASS"' | wc -l | tr -d ' ')
  fail=$(printf '%s' "$ST" | awk -F'\t' '$2=="FAIL"' | wc -l | tr -d ' ')
  printf '%s' "$ST"
  printf 'SELFTEST\tpass=%s\tfail=%s\tfixtures=%s\n' "$pass" "$fail" "$WORK"
  [ "$fail" -eq 0 ] || return 1
  return 0
}

case "$CMD" in
  plan)    cmd_plan "$@";;
  runbook) cmd_runbook "$@";;
  stage)   cmd_stage "$@"; exit $(( FAIL_RC != 0 ? 1 : 0 ));;
  check)   cmd_check;;
  delete)  cmd_delete;;
  selftest) cmd_selftest || exit 1;;
esac
exit 0
