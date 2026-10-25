#!/usr/bin/env bash
# souji-quarantine.impl-06 — quarantine-flow runner + gate-opening runbook
# (round 8, seat S06).
#
# Machine-implements the round-7 execution_plan_template and
# authorization_rule (census/round-7/quarantine-plan.json): ticket, stage,
# hold, second-check, delete — fail-closed, dry-run by default, and a
# read-only runbook that says what would open each blocked gate.
#
# Authorization rule (a ticket exists only if ALL hold):
#   gate1  git -C <repo> log --branches --not --remotes --oneline -- <path>
#          prints nothing (no unpushed commits touch the path)
#   gate2  git -C <repo> status --porcelain=v1 --untracked-files=all --
#          <path> prints nothing (nothing dirty or untracked touches it)
#   gate3  receipt pair agrees: tools/souji-verify.sh (tool A) prints
#          SAFE and tools/souji-vault-verify.sh (tool B) prints SAFE +
#          VERIFIED(...) with the SAME receipt class for the target
#   pair   a pair verdict file (--pair-file) shows author AND blind seats
#          both SAFE with the same receipt for the target
# Any gate failure, receipt mismatch, or undocumented input =>
# NOT-AUTHORIZED. Staging re-verifies every gate at execution time
# (TOCTOU guard): a ticket that went stale between ticket and stage
# refuses.
#
# CLI
#   tools/impl-06.sh ticket  [--json] [--stale-days N] [--pair-file F]
#                            <path>...
#   tools/impl-06.sh stage   [--execute] [--json] [--stale-days N]
#                            [--pair-file F] <path>...
#   tools/impl-06.sh second-check [--execute] [--json] <staged-entry-path>
#   tools/impl-06.sh delete  [--execute] [--json] <staged-entry-path>
#   tools/impl-06.sh runbook [--json] [--stale-days N] [--pair-file F]
#                            <path>...
#   tools/impl-06.sh --selftest | -h | --help
#
# ticket        read-only: run gate1/gate2/gate3/pair and report
#               AUTHORIZED or NOT-AUTHORIZED per target. Mutates nothing.
# stage         default dry-run: print the exact plan (gate table + the
#               mv commands) and mutate nothing. --execute performs
#               step_1: mkdir -p <repo>/.ufo-quarantine/<YYYY-MM-DD>/,
#               mv <path> <dir>/<path with / -> __>, and write a manifest
#               sidecar <staged-name>.manifest.sq06.txt next to it.
#               Requires an AUTHORIZED
#               ticket re-verified at execution time.
# second-check  step_3: re-hash the staged entry against its manifest
#               sidecar, confirm the original path is still absent and
#               gate1 on the original path is still empty, then stamp
#               <staged-name>.second-check-pass beside it. Per entry —
#               several entries may share one date dir. Default dry-run.
# delete        step_4: requires the entry's stamped
#               <staged-name>.second-check-pass. Removes ONLY that staged
#               entry and marks its manifest deleted=true. Default
#               dry-run. Never rm outside the staged entry itself.
# runbook       read-only, safe on live trees: per gate PASS/FAIL plus
#               the operator action that would open it (push master /
#               restore origin / wait out the stale window / retire live
#               citations / unlock worktrees / complete ledger+vault).
#               Tools never perform these actions — they are
#               operator-owned by AGENTS.md.
#
# Exit codes
#   0  evaluated (ticket verdicts may be NOT-AUTHORIZED; dry-runs)
#   1  selftest failure or internal evaluation error
#   2  usage
#   3  authorization/consistency refusal (no ticket at execution time,
#      pair/manifest inconsistency, second-check hash mismatch, delete
#      without second-check stamp, staged-name collision)
#   4  SAFETY refusal: --execute against a repo not under a mktemp-style
#      fixture root (no `tmp.*' path component), or secret-shaped target
#      on a mutating subcommand
#
# Safety rails
#   * MUTATION IS FIXTURE-ONLY: any --execute (or delete/second-check
#     write) hard-refuses unless the target's git repo root path contains
#     a `tmp.*' component (the mktemp -d convention). The live fleet and
#     this lane repo can therefore never be mutated by this tool. Dry-run
#     and ticket/runbook never write anywhere.
#   * Secret-shaped path components (*.env, .env*, *credential*,
#     *secret*, id_*, *.pem) are refused before anything is read:
#     ticket => NOT-AUTHORIZED(secrets-refusal); mutating subcommand =>
#     exit 4.
#   * No git fetch/push/commit/branch/checkout/reset/rebase is ever run
#     by this tool. The --selftest fixtures are built with plumbing
#     (init/add/write-tree/commit-tree/update-ref/symbolic-ref) and live
#     under mktemp -d only. `.ufo/state', `.ufo/watchdog.log' and
#     ~/.config are never touched; no file outside the fixture (or the
#     caller's stdout) is ever written.
#   * NOT-AUTHORIZED is the safe default, not an error (exit stays 0),
#     matching souji-verify semantics.
#
# Pair verdict file (--pair-file), TSV, one row per target:
#   <path>	<author-verdict>	<author-receipt>	<blind-verdict>	<blind-receipt>
# Rows whose path does not equal the target are ignored; a missing row is
# an undocumented pair => NOT-AUTHORIZED(pair-missing).
#
# manifest sidecar <staged-name>.manifest.sq06.txt (flat k=v, written at
# stage time, appended by second-check/delete): sq06_manifest, created_at,
# repo_root, original_path, rel_path, staged_name, receipt, gate1,
# gate1_evidence, gate2, gate2_evidence, tool_a, tool_b, pair_file,
# sha256, secondcheck_method, and later secondcheck_at, secondcheck,
# deleted_at, deleted.
#
# Deviations from the round-7 template text, and why:
#   D-a  The pair agreement is carried as a TSV verdict file, not JSON:
#        the house toolchain is bash + coreutils + git + rg only, and a
#        fixed 5-column TSV is exactly parseable without a JSON parser.
#   D-b  step_0_recheck's "re-run the receipt tool once more on the
#        quarantined copy" is implemented as byte re-hash + gate1
#        stability on the ORIGINAL path instead: the copy lives under
#        .ufo-quarantine/**, which the receipt engines' reference sweep
#        excludes by design, so a copy re-verify would measure the
#        exclusion, not the receipt. Recorded in the manifest as
#        secondcheck_method=hash+gate1-stability.
#   D-c  `delete' requires the entry's stamped <staged-name>.
#        .second-check-pass file (the template's operator sign-off remains
#        external to the tool and is never simulated by it).
#   D-d  Fixture gate for --execute is the `tmp.*' path-component
#        convention of `mktemp -d` defaults rather than a parsed
#        mktemp registry: simple, deny-by-default, and matches the
#        round-8 directive ("only mutate mktemp fixture repos").
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SHOKUNIN_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"
TOOL_A="${SQ_TOOL_A:-$SCRIPT_DIR/souji-verify.sh}"
TOOL_B="${SQ_TOOL_B:-$SCRIPT_DIR/souji-vault-verify.sh}"

STALE_DAYS=1
JSON=0
EXECUTE=0
PAIR_FILE=""
SUBCMD=""
TARGETS=()

secret_refusal() { # $1 = path -> 0 if secret-shaped component present
  local p rest comp
  p=$1
  rest=$p
  while [ -n "$rest" ]; do
    comp=${rest%%/*}
    case "$comp" in
      *.env|.env*|*credential*|*secret*|id_*|*.pem) return 0 ;;
    esac
    case "$rest" in */*) rest=${rest#*/} ;; *) rest="" ;; esac
  done
  return 1
}

repo_root_of() { # $1 = abs path -> echo repo root or empty
  local p dir
  p=$1
  if [ -d "$p/.git" ]; then printf '%s' "$p"; return 0; fi
  dir=$p
  while :; do
    dir=$(dirname -- "$dir")
    if [ "$dir" = "/" ]; then return 1; fi
    if [ -d "$dir/.git" ]; then printf '%s' "$dir"; return 0; fi
  done
}

is_fixture_root() { # $1 = repo root -> 0 if any component matches tmp.*
  local rest comp
  rest=$1
  while [ -n "$rest" ]; do
    comp=${rest%%/*}
    case "$comp" in
      tmp.*) return 0 ;;
    esac
    case "$rest" in */*) rest=${rest#*/} ;; *) rest="" ;; esac
  done
  return 1
}

gate1_lines() { # repo, rel -> stdout lines (empty = pass)
  git -C "$1" log --branches --not --remotes --oneline -- "$2" 2>/dev/null || true
}

gate2_lines() { # repo, rel -> stdout lines (empty = pass)
  git -C "$1" status --porcelain=v1 --untracked-files=all -- "$2" 2>/dev/null || true
}

# run one receipt tool on one target; echo its VERDICT line
tool_verdict_line() { # $1 = tool, $2 = target
  local out line
  out=$("$1" --stale-days "$STALE_DAYS" "$2" 2>/dev/null || true)
  line=$(printf '%s\n' "$out" | awk -F'\t' -v p="$2" \
    '$1=="VERDICT" && $2==p { print; exit }')
  printf '%s' "$line"
}

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

now_iso() { date --iso-8601=seconds; }

usage() { # $1 = exit code
  sed -n '2,119p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "$1"
}

usage_err() { printf 'impl-06: %s\n' "$1" >&2; usage 2; }

# pair file lookup: path -> "aVer aRcpt bVer bRcpt" or empty
pair_row() { # $1 = path
  [ -n "$PAIR_FILE" ] || return 1
  [ -f "$PAIR_FILE" ] || return 1
  awk -F'\t' -v p="$1" '!/^#/ && $1==p { print $2 "\t" $3 "\t" $4 "\t" $5; exit }' \
    "$PAIR_FILE" 2>/dev/null
}

# Evaluate all gates + toolpair for one target.
# Sets: G1 G1EV G2 G2EV TA_V TA_R TB_V TB_R TB_VER PR RECEIPT TICKET TICKET_REASON
eval_target() { # $1 = abs target path
  local tpath=$1 repo rel prowl crow
  local tav tar tbv tbr tbver prov parr pbvr
  TICKET=NOT-AUTHORIZED
  TICKET_REASON=none
  RECEIPT=none
  G1=FAIL G1EV=not-in-git-repo
  G2=FAIL G2EV=not-in-git-repo
  TA_V=? TA_R=? TB_V=? TB_R=? TB_VER=? PR=missing

  if secret_refusal "$tpath"; then
    TICKET_REASON=secrets-refusal
    TA_V=NOT-SAFE TA_R=secrets-refusal TB_V=NOT-SAFE TB_R=secrets-refusal TB_VER=refused
    G1=SKIP G2=SKIP
    return 0
  fi
  if [ ! -e "$tpath" ]; then
    TICKET_REASON=unreachable
    TA_V=NOT-SAFE TA_R=unreachable TB_V=NOT-SAFE TB_R=unreachable TB_VER=no
    G1=SKIP G2=SKIP
    return 0
  fi

  repo=$(repo_root_of "$tpath" || true)
  if [ -z "$repo" ]; then
    TICKET_REASON=gate1-not-in-repo
    TA_V=? TA_R=no-repo TB_V=? TB_R=no-repo TB_VER=no
    return 0
  fi
  rel=${tpath#"$repo"/}
  [ "$rel" != "$tpath" ] || rel=$tpath

  prowl=$(gate1_lines "$repo" "$rel")
  if [ -z "$prowl" ]; then G1=PASS G1EV="unpushed-touching=0"; else
    G1=FAIL G1EV="unpushed-touching=$(printf '%s\n' "$prowl" | wc -l | tr -d ' ')"
  fi
  crow=$(gate2_lines "$repo" "$rel")
  if [ -z "$crow" ]; then G2=PASS G2EV="dirty-touching=0"; else
    G2=FAIL G2EV="dirty-touching=$(printf '%s\n' "$crow" | wc -l | tr -d ' ')"
  fi

  local aout bout la lb bline2
  aout=$("$TOOL_A" --stale-days "$STALE_DAYS" "$tpath" 2>/dev/null || true)
  bout=$("$TOOL_B" --stale-days "$STALE_DAYS" "$tpath" 2>/dev/null || true)
  la=$(printf '%s\n' "$aout" | awk -F'\t' -v p="$tpath" \
    '$1=="VERDICT" && $2==p { print; exit }')
  lb=$(printf '%s\n' "$bout" | awk -F'\t' -v p="$tpath" \
    '$1=="VERDICT" && $2==p { print; exit }')
  TA_V=$(printf '%s' "$la" | cut -f3)
  TA_R=$(printf '%s' "$la" | cut -f4)
  TB_V=$(printf '%s' "$lb" | cut -f3)
  TB_R=$(printf '%s' "$lb" | cut -f4)
  bline2=$(printf '%s\n' "$bout" | sed -n '2p')
  case "$bline2" in
    VERIFIED\(*) TB_VER=$(printf '%s' "$bline2" | sed 's/^VERIFIED(//; s/)$//');;
    *) TB_VER=no;;
  esac

  if [ "$G1" = PASS ] && [ "$G2" = PASS ] \
     && [ "$TA_V" = SAFE ] && [ "$TB_V" = SAFE ] \
     && [ "$TB_VER" != no ] && [ "$TA_R" = "$TB_VER" ]; then
    RECEIPT=$TA_R
    PR=same
    # pair file half
    local prow pav par pbv pbr
    if prow=$(pair_row "$tpath"); then
      pav=$(printf '%s' "$prow" | cut -f1); par=$(printf '%s' "$prow" | cut -f2)
      pbv=$(printf '%s' "$prow" | cut -f3); pbr=$(printf '%s' "$prow" | cut -f4)
      if [ "$pav" = SAFE ] && [ "$pbv" = SAFE ] \
         && [ "$par" = "$pbr" ] && [ "$par" = "$RECEIPT" ]; then
        TICKET=AUTHORIZED
        TICKET_REASON="pair-ok receipt=$RECEIPT"
      else
        TICKET_REASON=pair-mismatch
      fi
    else
      TICKET_REASON=pair-missing
    fi
  elif [ "$G1" != PASS ]; then
    TICKET_REASON="gate1-fail($G1EV)"
  elif [ "$G2" != PASS ]; then
    TICKET_REASON="gate2-fail($G2EV)"
  else
    TICKET_REASON="receipt-mismatch(A=$TA_V/$TA_R B=$TB_V/$TB_VER)"
  fi
}

emit_ticket_json() { # $1 = target
  printf '{"path":"%s","ticket":"%s","reason":"%s","gate1":"%s","gate1_evidence":"%s","gate2":"%s","gate2_evidence":"%s","tool_a":"%s/%s","tool_b":"%s/%s","tool_b_verified":"%s","pair":"%s","receipt":"%s"}\n' \
    "$(json_escape "$1")" "$TICKET" "$(json_escape "$TICKET_REASON")" \
    "$G1" "$(json_escape "$G1EV")" "$G2" "$(json_escape "$G2EV")" \
    "$TA_V" "$TA_R" "$TB_V" "$TB_R" "$TB_VER" "$PR" "$RECEIPT"
}

emit_ticket_text() { # $1 = target
  printf 'TICKET\t%s\t%s\t%s\n' "$1" "$TICKET" "$TICKET_REASON"
  printf 'GATES\t%s (%s)\t%s (%s)\n' "$G1" "$G1EV" "$G2" "$G2EV"
  printf 'TOOLS\tA=%s/%s\tB=%s/%s\tB-verified=%s\tpair=%s\n' \
    "$TA_V" "$TA_R" "$TB_V" "$TB_R" "$TB_VER" "$PR"
}

remediation_lines() { # $1 = target; print operator actions for blocked gates
  case "$TICKET_REASON" in
    secrets-refusal)
      printf '  - secrets-refusal: no runbook; refusal is permanent\n';;
    gate1-fail*)
      printf '  - gate1: operator pushes the branches touching the path to origin, or abandons those local commits (tool never does this)\n';;
    gate2-fail*)
      printf '  - gate2: operator commits or cleans the dirty/untracked paths touching the target (tool never does this)\n';;
    receipt-mismatch*)
      case "$TA_R:$TB_VER" in
        pushed-unverifiable*:*|*:no)
          : ;;
      esac
      if [ "$TA_R" = pushed-unverifiable ] || [ "$TB_R" = pushed-unverifiable ]; then
        printf '  - pushed unverifiable: operator restores a live origin (remote-tracking refs present) or pushes the introducing commit\n'
      fi
      if [ "$TA_R" = stale ] || [ "$TB_R" = stale ] || [ "$TA_V" = NOT-SAFE ]; then
        printf '  - stale window: keep the tree quiescent until mtime age exceeds stale-days=%s and no live reference cites the basename (LOG/census/tests excluded from the sweep)\n' "$STALE_DAYS"
      fi
      if [ "$TA_R" = moved-to-obsidian ] || [ "$TB_R" = moved-to-obsidian ]; then
        printf '  - moved-to-obsidian: complete the ledger row and the vault copy so both sides re-hash to the row (operator-owned)\n'
      fi
      printf '  - pair: author and blind seats must both emit SAFE with the same receipt class for this target\n';;
    pair-missing)
      printf '  - pair: supply --pair-file documenting author+blind SAFE verdicts for this target\n';;
    pair-mismatch)
      printf '  - pair: the verdict file disagrees with the tool pair; re-adjudicate before staging\n';;
    unreachable)
      printf '  - target absent: nothing to quarantine\n';;
    gate1-not-in-repo)
      printf '  - target is not inside a git repo; no receipt class applies\n';;
  esac
}

open_gate_json() { # single-line remediation for JSON
  case "$TICKET_REASON" in
    gate1-fail*)    printf 'push-touching-branches-or-abandon (operator-owned)';;
    gate2-fail*)    printf 'commit-or-clean-touching-paths (operator-owned)';;
    receipt-mismatch*)
      if [ "$TA_R" = pushed-unverifiable ] || [ "$TB_R" = pushed-unverifiable ]; then
        printf 'restore-origin-or-push-introducing-commit (operator-owned)'
      else
        printf 'stale-window-or-ledger-vault-completion-then-re-adjudicate (operator-owned)'
      fi;;
    pair-missing)   printf 'supply-pair-verdict-file';;
    pair-mismatch)  printf 're-adjudicate-pair-verdicts';;
    secrets-refusal) printf 'none-permanent-refusal';;
    unreachable)    printf 'none-target-absent';;
    gate1-not-in-repo) printf 'none-not-in-git-repo';;
    *)              printf 'none';;
  esac
}

cmd_runbook() { # targets already parsed
  local t
  for t in "${TARGETS[@]}"; do
    t=$(readlink -m -- "$t")
    eval_target "$t"
    if [ "$JSON" = 1 ]; then
      printf '{"path":"%s","ticket":"%s","reason":"%s","gate1":"%s","gate2":"%s","tool_a":"%s/%s","tool_b":"%s/%s","receipt":"%s","open_gate":"%s"}\n' \
        "$(json_escape "$t")" "$TICKET" "$(json_escape "$TICKET_REASON")" \
        "$G1" "$G2" "$TA_V" "$TA_R" "$TB_V" "$TB_VER" "$RECEIPT" \
        "$(json_escape "$(open_gate_json)")"
    else
      printf 'RUNBOOK\t%s\n' "$t"
      printf '  gate1 %s (%s)\n  gate2 %s (%s)\n' "$G1" "$G1EV" "$G2" "$G2EV"
      printf '  gate3 toolA=%s/%s toolB=%s verified-receipt=%s pair=%s\n' \
        "$TA_V" "$TA_R" "$TB_V" "$TB_VER" "$PR"
      printf '  ticket %s (%s)\n' "$TICKET" "$TICKET_REASON"
      if [ "$TICKET" != AUTHORIZED ]; then
        printf '  open-gate:\n'
        remediation_lines "$t"
      fi
    fi
  done
}

cmd_ticket() {
  local t
  for t in "${TARGETS[@]}"; do
    t=$(readlink -m -- "$t")
    eval_target "$t"
    if [ "$JSON" = 1 ]; then emit_ticket_json "$t"; else emit_ticket_text "$t"; fi
  done
}

manifest_get() { # $1 = manifest file, $2 = key
  grep -m1 "^$2=" "$1" 2>/dev/null | cut -d= -f2-
}

fixture_guard() { # $1 = repo root; exit 4 when not a tmp.* fixture
  if is_fixture_root "$1"; then return 0; fi
  printf 'impl-06: SAFETY-REFUSAL: --execute refused: repo root %s has no tmp.* fixture component; this tool mutates mktemp fixture repos only\n' "$1" >&2
  exit 4
}

cmd_stage() {
  local t repo rel grepo
  for t in "${TARGETS[@]}"; do
    t=$(readlink -m -- "$t")
    if [ "$EXECUTE" = 1 ]; then
      # SAFETY before authorization: a non-fixture repo is refused even if
      # the ticket would fail anyway (the refusal class must not be masked).
      grepo=$(repo_root_of "$t" || true)
      if [ -n "$grepo" ]; then fixture_guard "$grepo"; fi
    fi
    eval_target "$t"
    if [ "$JSON" = 1 ]; then emit_ticket_json "$t"; else emit_ticket_text "$t"; fi
    if [ "$TICKET" != AUTHORIZED ]; then
      if [ "$EXECUTE" = 1 ]; then
        printf 'impl-06: refusal: target not authorized at execution time (%s)\n' "$TICKET_REASON" >&2
        exit 3
      fi
      continue
    fi
    if secret_refusal "$t"; then
      [ "$EXECUTE" = 1 ] || continue
      printf 'impl-06: SAFETY-REFUSAL: secret-shaped target\n' >&2
      exit 4
    fi
    repo=$(repo_root_of "$t")
    rel=${t#"$repo"/}
    local date_dir staged_name
    date_dir=$(date +%F)
    staged_name=$(printf '%s' "$rel" | tr '/' '_')
    if [ "$EXECUTE" != 1 ]; then
      printf 'PLAN(dry-run) mkdir -p %s/.ufo-quarantine/%s\n' "$repo" "$date_dir"
      printf 'PLAN(dry-run) mv %s %s/.ufo-quarantine/%s/%s\n' "$t" "$repo" "$date_dir" "$staged_name"
      printf 'PLAN(dry-run) write %s/.ufo-quarantine/%s/%s.manifest.sq06.txt\n' "$repo" "$date_dir" "$staged_name"
      printf 'PLAN(dry-run) hold: no commit, no delete; second-check after the hold window; delete needs its stamp + operator sign-off\n'
      continue
    fi
    fixture_guard "$repo"
    local qdir
    qdir=$repo/.ufo-quarantine/$date_dir
    if [ -e "$qdir/$staged_name" ]; then
      printf 'impl-06: refusal: staged name already exists: %s\n' "$qdir/$staged_name" >&2
      exit 3
    fi
    mkdir -p -- "$qdir"
    local digest
    digest=$(sha256sum -- "$t" | awk '{print $1}')
    mv -- "$t" "$qdir/$staged_name"
    {
      printf 'sq06_manifest=1\n'
      printf 'created_at=%s\n' "$(now_iso)"
      printf 'repo_root=%s\n' "$repo"
      printf 'original_path=%s\n' "$t"
      printf 'rel_path=%s\n' "$rel"
      printf 'staged_name=%s\n' "$staged_name"
      printf 'receipt=%s\n' "$RECEIPT"
      printf 'gate1=%s\ngate1_evidence=%s\n' "$G1" "$G1EV"
      printf 'gate2=%s\ngate2_evidence=%s\n' "$G2" "$G2EV"
      printf 'tool_a=%s/%s\ntool_b=%s/%s\n' "$TA_V" "$TA_R" "$TB_V" "$TB_VER"
      printf 'pair_file=%s\n' "${PAIR_FILE:--}"
      printf 'sha256=%s\n' "$digest"
      printf 'secondcheck_method=hash+gate1-stability\n'
    } > "$qdir/$staged_name.manifest.sq06.txt"
    printf 'STAGED\t%s -> %s\tsha256=%s\treceipt=%s\n' \
      "$t" "$qdir/$staged_name" "$digest" "$RECEIPT"
  done
}

require_entry() { # $1 = staged entry path -> manifest sidecar in M_ANIFEST
  local entry=$1
  M_ANIFEST=$entry.manifest.sq06.txt
  if [ ! -f "$M_ANIFEST" ]; then
    printf 'impl-06: refusal: no manifest sidecar: %s\n' "$M_ANIFEST" >&2
    exit 3
  fi
  if [ ! -d "$(dirname -- "$entry")" ]; then
    printf 'impl-06: refusal: quarantine date-dir missing: %s\n' "$(dirname -- "$entry")" >&2
    exit 3
  fi
  local repo
  repo=$(manifest_get "$M_ANIFEST" repo_root)
  [ -n "$repo" ] || { printf 'impl-06: refusal: manifest missing repo_root\n' >&2; exit 3; }
  if [ "$EXECUTE" = 1 ]; then fixture_guard "$repo"; fi
}

cmd_second_check() { # $1 = staged entry path
  local entry=$1
  require_entry "$entry"
  local orig repo
  repo=$(manifest_get "$M_ANIFEST" repo_root)
  orig=$(manifest_get "$M_ANIFEST" original_path)
  local checks plan stamp
  plan=""
  checks=0
  stamp=$entry.second-check-pass
  if [ ! -f "$entry" ]; then checks=1; plan="$plan staged-entry-missing"; fi
  if [ -e "$orig" ]; then checks=1; plan="$plan original-resurrected"; fi
  if [ -n "$(gate1_lines "$repo" "$(manifest_get "$M_ANIFEST" rel_path)")" ]; then
    checks=1; plan="$plan gate1-no-longer-empty"
  fi
  if [ -f "$entry" ]; then
    local digest digest_now
    digest=$(manifest_get "$M_ANIFEST" sha256)
    digest_now=$(sha256sum -- "$entry" | awk '{print $1}')
    [ "$digest_now" = "$digest" ] || { checks=1; plan="$plan sha-mismatch"; }
  fi
  if [ "$EXECUTE" != 1 ]; then
    printf 'PLAN(dry-run) second-check %s: %s\n' "$entry" \
      "${plan:-would stamp ${stamp##*/}}"
    return 0
  fi
  if [ "$checks" != 0 ]; then
    printf 'impl-06: refusal: second-check failed:%s\n' "$plan" >&2
    exit 3
  fi
  if [ -f "$stamp" ]; then
    printf 'impl-06: refusal: second-check already stamped: %s\n' "$stamp" >&2
    exit 3
  fi
  printf 'secondcheck_at=%s\nsecondcheck=PASS\n' "$(now_iso)" >> "$M_ANIFEST"
  : > "$stamp"
  printf 'SECOND-CHECK PASS\t%s\tsha256=%s\n' "$entry" "$(manifest_get "$M_ANIFEST" sha256)"
}

cmd_delete() { # $1 = staged entry path
  local entry=$1
  require_entry "$entry"
  local stamp
  stamp=$entry.second-check-pass
  if [ "$EXECUTE" != 1 ]; then
    printf 'PLAN(dry-run) delete %s (requires %s + operator sign-off)\n' \
      "$entry" "${stamp##*/}"
    return 0
  fi
  if [ ! -f "$stamp" ]; then
    printf 'impl-06: refusal: delete requires a stamped second-check (%s absent)\n' "$stamp" >&2
    exit 3
  fi
  if [ ! -e "$entry" ]; then
    printf 'impl-06: refusal: staged entry already gone: %s\n' "$entry" >&2
    exit 3
  fi
  rm -rf -- "$entry"
  printf 'deleted_at=%s\ndeleted=true\n' "$(now_iso)" >> "$M_ANIFEST"
  printf 'DELETED\t%s\n' "$entry"
}

selftest_main() {
  local pass=0 fail=0 FX NOFX rc out digest pre_sha
  T=$(mktemp -d "${TMPDIR:-/tmp}/sq06-selftest.XXXXXX")
  trap 'rm -rf -- "$T"' EXIT
  export SHOKUNIN_ROOT="$T"
  export SOUJI_LEDGER="$T/no-ledger.tsv"
  export GIT_AUTHOR_NAME=S06 GIT_AUTHOR_EMAIL=s06@fixture
  export GIT_COMMITTER_NAME=S06 GIT_COMMITTER_EMAIL=s06@fixture
  export GIT_AUTHOR_DATE='2026-10-15T10:00:00 -0300'
  export GIT_COMMITTER_DATE='2026-10-15T10:00:00 -0300'

  ok() { # $1 name, $2 rc(0=ok), $3 detail
    if [ "$2" = 0 ]; then pass=$((pass+1)); printf 'ok %s\n' "$1"
    else fail=$((fail+1)); printf 'FAIL %s %s\n' "$1" "${3:-}"; fi
  }
  expect_rc() { # $1 = wanted code, rest = command; sets C_RC, never aborts
    set +e
    "${@:2}" >/dev/null 2>&1
    C_RC=$?
    set -e
  }

  # --- fixture repos (plumbing only) -------------------------------------
  FX=$T/tmp.fixt.a/repo
  NOFX=$T/notmp/repo
  mkdir -p "$FX" "$NOFX"
  git -C "$FX" init -q && git -C "$FX" config core.autocrlf false
  fx_commit() { # $1 fx, $2 parent-sha or empty -> new sha (all changes)
    local tree sha
    git -C "$1" add -A
    tree=$(git -C "$1" write-tree)
    if [ -n "$2" ]; then sha=$(git -C "$1" commit-tree -p "$2" "$tree")
    else sha=$(git -C "$1" commit-tree "$tree"); fi
    git -C "$1" update-ref refs/heads/master "$sha"
    printf '%s' "$sha"
  }
  printf 'v1\n' > "$FX/old-pushed-scratch.log"
  C1=$(fx_commit "$FX" "")
  printf 'base\n' > "$FX/base.txt"
  printf 'v1\n' > "$FX/dirty.txt"
  printf 'rel\n' > "$FX/release.txt"
  C2=$(fx_commit "$FX" "$C1")
  git -C "$FX" update-ref refs/remotes/origin/master "$C2"
  git -C "$FX" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  printf 'local-only\n' > "$FX/local-only.txt"
  C3=$(fx_commit "$FX" "$C2")   # master=C3 beyond origin=C2
  printf 'v1-dirty\n' >> "$FX/dirty.txt"      # uncommitted worktree change
  printf 'junk\n' > "$FX/fresh-untracked.log" # untracked, stale-type
  touch -d '3 days ago' "$FX/old-pushed-scratch.log" "$FX/fresh-untracked.log"
  printf 'SECRET=1\n' > "$FX/secret.env"
  # second repo with NO tmp.* component (must be refused on --execute)
  printf 'x\n' > "$NOFX/note.txt"
  git -C "$NOFX" init -q
  git -C "$NOFX" add -A
  ntree=$(git -C "$NOFX" write-tree)
  nsha=$(git -C "$NOFX" commit-tree "$ntree")
  git -C "$NOFX" update-ref refs/heads/master "$nsha"

  PAIR_HAPPY=$T/pair-happy.tsv
  PAIR_BAD=$T/pair-bad.tsv
  printf '%s\tSAFE\tpushed\tSAFE\tpushed\n' "$FX/old-pushed-scratch.log" > "$PAIR_HAPPY"
  printf '%s\tSAFE\tpushed\tSAFE\tpushed\n' "$FX/base.txt" >> "$PAIR_HAPPY"
  printf '%s\tSAFE\tpushed\tSAFE\tpushed\n' "$FX/release.txt" >> "$PAIR_HAPPY"
  printf '%s\tSAFE\tpushed\tNOT-SAFE\tpushed-unverifiable\n' "$FX/old-pushed-scratch.log" > "$PAIR_BAD"

  # --- usage -------------------------------------------------------------
  expect_rc 2 bash "$SELF"; ok "usage-no-subcommand-exit2" "$([ "$C_RC" -eq 2 ] && echo 0 || echo 1)"
  expect_rc 2 bash "$SELF" ticket --nope; ok "usage-unknown-flag-exit2" "$([ "$C_RC" -eq 2 ] && echo 0 || echo 1)"

  # --- ticket: happy path needs pair file --------------------------------
  out=$(bash "$SELF" ticket "$FX/old-pushed-scratch.log" 2>&1); rc=$?
  ok "ticket-no-pair-pair-missing" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'NOT-AUTHORIZED	pair-missing' && echo 0 || echo 1)" "$out"
  ok "ticket-no-pair-gates-pass" "$(printf '%s' "$out" | grep -q 'GATES	PASS' && echo 0 || echo 1)" "$out"
  ok "ticket-toolA-SAFE-pushed" "$(printf '%s' "$out" | grep -q 'A=SAFE/pushed' && echo 0 || echo 1)" "$out"
  ok "ticket-toolB-verified-pushed" "$(printf '%s' "$out" | grep -q 'B=SAFE/pushed	.*B-verified=pushed' && echo 0 || echo 1)" "$out"

  out=$(bash "$SELF" ticket --pair-file "$PAIR_HAPPY" "$FX/old-pushed-scratch.log" 2>&1); rc=$?
  ok "ticket-authorized-with-pair" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'AUTHORIZED' && echo 0 || echo 1)" "$out"

  out=$(bash "$SELF" ticket --pair-file "$PAIR_BAD" "$FX/old-pushed-scratch.log" 2>&1); rc=$?
  ok "ticket-pair-mismatch-refused" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'NOT-AUTHORIZED	pair-mismatch' && echo 0 || echo 1)" "$out"

  # --- gate failures ------------------------------------------------------
  out=$(bash "$SELF" ticket --pair-file "$PAIR_HAPPY" "$FX/dirty.txt" 2>&1); rc=$?
  ok "ticket-gate2-dirty-refused" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'NOT-AUTHORIZED	gate2-fail' && echo 0 || echo 1)" "$out"
  out=$(bash "$SELF" ticket "$FX/local-only.txt" 2>&1); rc=$?
  ok "ticket-gate1-unpushed-refused" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'NOT-AUTHORIZED	gate1-fail' && echo 0 || echo 1)" "$out"

  # lore shape: tools say SAFE(stale) but gate2 (untracked) dominates
  out=$(bash "$SELF" ticket "$FX/fresh-untracked.log" 2>&1); rc=$?
  ok "ticket-untracked-stale-gate2-dominates" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'NOT-AUTHORIZED	gate2-fail' && echo 0 || echo 1)" "$out"
  ok "ticket-untracked-stale-toolA-observed" "$(printf '%s' "$out" | grep -qE 'A=(SAFE/stale|NOT-SAFE/[a-z-]+)' && echo 0 || echo 1)" "$out"

  out=$(bash "$SELF" ticket "$FX/secret.env" 2>&1); rc=$?
  ok "ticket-secrets-refusal" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'NOT-AUTHORIZED	secrets-refusal' && echo 0 || echo 1)" "$out"

  out=$(bash "$SELF" ticket "$FX/absent-thing.txt" 2>&1); rc=$?
  ok "ticket-unreachable" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'NOT-AUTHORIZED	unreachable' && echo 0 || echo 1)" "$out"

  # --- json ---------------------------------------------------------------
  out=$(bash "$SELF" ticket --json --pair-file "$PAIR_HAPPY" "$FX/old-pushed-scratch.log" 2>&1); rc=$?
  ok "ticket-json-shape" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q '"ticket":"AUTHORIZED"' && printf '%s' "$out" | grep -q '"receipt":"pushed"' && echo 0 || echo 1)" "$out"

  # --- stage dry-run mutates nothing --------------------------------------
  out=$(bash "$SELF" stage --pair-file "$PAIR_HAPPY" "$FX/old-pushed-scratch.log" 2>&1); rc=$?
  ok "stage-dryrun-exit0-plan" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'PLAN(dry-run) mv' && echo 0 || echo 1)" "$out"
  ok "stage-dryrun-no-quarantine" "$([ ! -e "$FX/.ufo-quarantine" ] && echo 0 || echo 1)"

  # --- stage --execute refusals -------------------------------------------
  expect_rc 3 bash "$SELF" stage --execute --pair-file "$PAIR_HAPPY" "$FX/dirty.txt"
  ok "stage-execute-unauthorized-exit3" "$([ "$C_RC" -eq 3 ] && echo 0 || echo 1)"
  expect_rc 3 bash "$SELF" stage --execute "$FX/old-pushed-scratch.log"
  ok "stage-execute-no-pair-exit3" "$([ "$C_RC" -eq 3 ] && echo 0 || echo 1)"
  expect_rc 4 bash "$SELF" stage --execute --pair-file "$PAIR_HAPPY" "$NOFX/note.txt"
  ok "stage-execute-non-fixture-exit4" "$([ "$C_RC" -eq 4 ] && echo 0 || echo 1)"
  ok "stage-execute-non-fixture-no-write" "$([ ! -e "$NOFX/.ufo-quarantine" ] && echo 0 || echo 1)"

  # --- stage --execute happy path ------------------------------------------
  pre_sha=$(sha256sum -- "$FX/old-pushed-scratch.log" | awk '{print $1}')
  QD=$FX/.ufo-quarantine/$(date +%F)
  out=$(bash "$SELF" stage --execute --pair-file "$PAIR_HAPPY" "$FX/old-pushed-scratch.log" 2>&1); rc=$?
  ok "stage-execute-staged" "$([ $rc -eq 0 ] && [ -f "$QD/old-pushed-scratch.log" ] && [ ! -e "$FX/old-pushed-scratch.log" ] && echo 0 || echo 1)" "$out"
  ok "stage-execute-manifest-sha" "$([ "$(sha256sum -- "$QD/old-pushed-scratch.log" | awk '{print $1}')" = "$pre_sha" ] && [ "$(grep -m1 '^sha256=' "$QD/old-pushed-scratch.log.manifest.sq06.txt" | cut -d= -f2)" = "$pre_sha" ] && echo 0 || echo 1)"
  ok "stage-execute-manifest-receipt" "$(grep -m1 '^receipt=pushed$' "$QD/old-pushed-scratch.log.manifest.sq06.txt" >/dev/null && echo 0 || echo 1)"

  out=$(bash "$SELF" ticket "$FX/old-pushed-scratch.log" 2>&1); rc=$?
  ok "ticket-post-stage-unreachable" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'NOT-AUTHORIZED	unreachable' && echo 0 || echo 1)" "$out"

  # --- second-check (entry-scoped: sidecar + stamp per staged entry) --------
  out=$(bash "$SELF" second-check "$QD/old-pushed-scratch.log" 2>&1); rc=$?
  ok "secondcheck-dryrun-no-stamp" "$([ $rc -eq 0 ] && [ ! -f "$QD/old-pushed-scratch.log.second-check-pass" ] && echo 0 || echo 1)" "$out"
  out=$(bash "$SELF" second-check --execute "$QD/old-pushed-scratch.log" 2>&1); rc=$?
  ok "secondcheck-execute-pass" "$([ $rc -eq 0 ] && [ -f "$QD/old-pushed-scratch.log.second-check-pass" ] && grep -q '^secondcheck=PASS$' "$QD/old-pushed-scratch.log.manifest.sq06.txt" && echo 0 || echo 1)" "$out"
  expect_rc 3 bash "$SELF" second-check --execute "$QD/old-pushed-scratch.log"
  ok "secondcheck-execute-twice-exit3" "$([ "$C_RC" -eq 3 ] && echo 0 || echo 1)"

  # --- delete -----------------------------------------------------------------
  out=$(bash "$SELF" delete "$QD/old-pushed-scratch.log" 2>&1); rc=$?
  ok "delete-dryrun-keeps-entry" "$([ $rc -eq 0 ] && [ -f "$QD/old-pushed-scratch.log" ] && echo 0 || echo 1)" "$out"
  out=$(bash "$SELF" delete --execute "$QD/old-pushed-scratch.log" 2>&1); rc=$?
  ok "delete-execute-removes-entry" "$([ $rc -eq 0 ] && [ ! -e "$QD/old-pushed-scratch.log" ] && grep -q '^deleted=true$' "$QD/old-pushed-scratch.log.manifest.sq06.txt" && echo 0 || echo 1)" "$out"
  expect_rc 3 bash "$SELF" delete --execute "$QD/old-pushed-scratch.log"
  ok "delete-execute-twice-exit3" "$([ "$C_RC" -eq 3 ] && echo 0 || echo 1)"

  # --- tamper: second-check must catch byte change -----------------------------
  expect_rc 0 bash "$SELF" stage --execute --pair-file "$PAIR_HAPPY" "$FX/base.txt"
  if [ -f "$QD/base.txt" ]; then printf 'tampered\n' >> "$QD/base.txt"; fi
  expect_rc 3 bash "$SELF" second-check --execute "$QD/base.txt"
  ok "secondcheck-tamper-exit3" "$([ "$C_RC" -eq 3 ] && [ ! -f "$QD/base.txt.second-check-pass" ] && echo 0 || echo 1)"

  # --- delete without second-check stamp refuses -------------------------------
  expect_rc 0 bash "$SELF" stage --execute --pair-file "$PAIR_HAPPY" "$FX/release.txt"
  ok "stage-third-target" "$([ -f "$QD/release.txt" ] && echo 0 || echo 1)"
  expect_rc 3 bash "$SELF" delete --execute "$QD/release.txt"
  ok "delete-without-stamp-exit3" "$([ "$C_RC" -eq 3 ] && [ -f "$QD/release.txt" ] && echo 0 || echo 1)"

  # --- per-entry isolation: release.txt can still complete its flow -------------
  out=$(bash "$SELF" second-check --execute "$QD/release.txt" 2>&1); rc=$?
  ok "secondcheck-entry-isolation" "$([ $rc -eq 0 ] && [ -f "$QD/release.txt.second-check-pass" ] && echo 0 || echo 1)" "$out"
  out=$(bash "$SELF" delete --execute "$QD/release.txt" 2>&1); rc=$?
  ok "delete-entry-isolation" "$([ $rc -eq 0 ] && [ ! -e "$QD/release.txt" ] && [ -f "$QD/base.txt" ] && echo 0 || echo 1)" "$out"

  # --- runbook -------------------------------------------------------------------
  out=$(bash "$SELF" runbook "$FX/local-only.txt" 2>&1); rc=$?
  ok "runbook-text-gate-lines" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'RUNBOOK' && printf '%s' "$out" | grep -q 'open-gate:' && echo 0 || echo 1)" "$out"
  out=$(bash "$SELF" runbook --json "$FX/dirty.txt" 2>&1); rc=$?
  ok "runbook-json-open-gate" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q '"open_gate":' && echo 0 || echo 1)" "$out"

  # live-tree dry surface: runbook on a real lane file (read-only), no writes
  LIVE=$REPO_ROOT/tools/souji-verify.spec.md
  out=$(SHOKUNIN_ROOT="$(dirname -- "$REPO_ROOT")" bash "$SELF" runbook "$LIVE" 2>&1); rc=$?
  ok "runbook-live-read-only" "$([ $rc -eq 0 ] && printf '%s' "$out" | grep -q 'RUNBOOK' && [ ! -e "$REPO_ROOT/.ufo-quarantine" ] && echo 0 || echo 1)" "$out"
  expect_rc 4 bash "$SELF" stage --execute --pair-file "$PAIR_HAPPY" "$LIVE"
  ok "stage-execute-live-lane-exit4" "$([ "$C_RC" -eq 4 ] && [ ! -e "$REPO_ROOT/.ufo-quarantine" ] && echo 0 || echo 1)"

  printf 'SUMMARY selftest pass=%d fail=%d\n' "$pass" "$fail"
  [ "$fail" -eq 0 ]
}

SELFTEST=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --execute) EXECUTE=1; shift ;;
    --stale-days) [ "$#" -ge 2 ] || usage_err "--stale-days needs a value"; STALE_DAYS=$2; shift 2 ;;
    --stale-days=*) STALE_DAYS=${1#*=}; shift ;;
    --pair-file) [ "$#" -ge 2 ] || usage_err "--pair-file needs a value"; PAIR_FILE=$2; shift 2 ;;
    --pair-file=*) PAIR_FILE=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    -*) usage_err "unknown flag: $1" ;;
    *) if [ -z "$SUBCMD" ]; then SUBCMD=$1; else TARGETS+=("$1"); fi; shift ;;
  esac
done

if [ "$SELFTEST" = 1 ]; then
  selftest_main
  exit $?
fi

case "$SUBCMD" in
  ticket|stage|runbook) ;;
  second-check|delete) ;;
  "") usage_err "no subcommand (ticket|stage|second-check|delete|runbook|--selftest)" ;;
  *) usage_err "unknown subcommand: $SUBCMD" ;;
esac

case "$SUBCMD" in
  second-check|delete)
    [ "${#TARGETS[@]}" -eq 1 ] || usage_err "$SUBCMD takes exactly one staged entry path"
    [ -d "$(dirname -- "${TARGETS[0]}")" ] || usage_err "no quarantine date-dir: $(dirname -- "${TARGETS[0]}")"
    ;;
  *)
    [ "${#TARGETS[@]}" -ge 1 ] || usage_err "no targets given"
    ;;
esac

if [ -n "$PAIR_FILE" ] && [ ! -f "$PAIR_FILE" ]; then
  usage_err "pair file not found: $PAIR_FILE"
fi

case "$SUBCMD" in
  ticket)       cmd_ticket ;;
  stage)        cmd_stage ;;
  runbook)      cmd_runbook ;;
  second-check) cmd_second_check "${TARGETS[0]}" ;;
  delete)       cmd_delete "${TARGETS[0]}" ;;
esac
exit 0
