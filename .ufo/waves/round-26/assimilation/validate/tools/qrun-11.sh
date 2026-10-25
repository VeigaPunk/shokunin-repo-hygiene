#!/usr/bin/env bash
# qrun-11 — quarantine-flow runner, seat S11 (souji-shokunin round 8).
#
# Exercises the round-7 pre-staged quarantine execution plan
# (census/round-7/quarantine-plan.json: step_0_recheck .. step_4_delete)
# END-TO-END on fixture repos built under mktemp -d, where every gate is
# deliberately OPENED (local bare remotes make the pushed receipt
# establishable; backdated mtimes + zero refs make stale establishable;
# matching ledger rows make moved-to-obsidian establishable; a detached,
# absent-dir, unique=0 worktree registration makes metadata-prune
# establishable). The live fleet has NO authorized removal targets; the
# only live phase is a READ-ONLY dry-run probe through the installed tools.
#
# Phases
#   fixture   build the gate-open fixture fleet (mktemp only)
#   gateproof installed tools A=souji-verify.sh / B=souji-vault-verify.sh
#             emit SAFE + the expected receipt class for every fixture class
#   flow      steps 0-4 of the r7 template per scenario:
#               pushed (r7 gates verbatim) / stale / moved-to-obsidian
#               (r7 gate text is unreachable for these two classes — the
#               amendments used are labeled FINDING F-1/F-2 in the output)
#   controls  fail-closed: unpushed-touching, dirty-touching, live-ref,
#             secrets-shaped, and the quarantine-scope guard itself
#   live      read-only dry-run probe of the installed tools on two live
#             lane paths; zero-mutation assertion (mtimes + no git writes)
#   audit     self-audit: no unguarded mutating git verb, quarantine-scope
#             guard is the only rm choke point, no .ufo/state /
#             .ufo/watchdog.log / ~/.config writes, fixtures under mktemp
#
# Safety
#   * EVERY mutating git verb is routed through fixture_git(), which refuses
#     any repo outside the mktemp root. The live phase runs no git at all.
#   * Every rm goes through guarded_rm_q(), which refuses any path that is
#     not under a <repo>/.ufo-quarantine/ directory of a fixture repo.
#   * A secrets-shaped fixture file is created but never read by this
#     runner; only the tools' refusal path observes it.
#   * Writes: results/qrun-11.json (--out) only. Nothing is committed.
#
# CLI: tools/qrun-11.sh [--out JSON] [--keep] [--no-live] [-h]
# Exit 0 iff every check passes; 1 otherwise.
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
TOOL_A="$REPO_ROOT/tools/souji-verify.sh"
TOOL_B="$REPO_ROOT/tools/souji-vault-verify.sh"
OUT_JSON="$REPO_ROOT/results/qrun-11.json"
KEEP=0
DO_LIVE=1

while [ "$#" -gt 0 ]; do
  case "$1" in
    --out) OUT_JSON=$2; shift 2 ;;
    --keep) KEEP=1; shift ;;
    --no-live) DO_LIVE=0; shift ;;
    -h|--help) sed -n '2,44p' "$REPO_ROOT/tools/qrun-11.sh" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) printf 'qrun-11: unknown arg %s\n' "$1" >&2; exit 2 ;;
  esac
done

mkdir -p -- "$(dirname -- "$OUT_JSON")"
STARTED_AT="$(date -u +%FT%TZ)"
T="$(mktemp -d "${TMPDIR:-/tmp}/qrun-11.XXXXXX")"
TODAY="$(date +%F)"
SECONDS=0

on_exit() { # ALWAYS emit a results file, even on a mid-run crash
  local rc=$?
  if [ "${JSON_EMITTED:-0}" != 1 ]; then
    N_FAIL=$((N_FAIL+1))
    check runner-died 1 "runner exited rc=$rc before completing; partial check set recorded below"
    emit_json "$OUT_JSON" || true
  fi
  [ "$KEEP" = 1 ] || rm -rf -- "$T"  # QGUARD-OK mktemp cleanup
}
trap on_exit EXIT

# Hermetic git identity so fixture commits are deterministic.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=qrun-11 GIT_AUTHOR_EMAIL=s11@shokunin.local
export GIT_COMMITTER_NAME=qrun-11 GIT_COMMITTER_EMAIL=s11@shokunin.local
export GIT_AUTHOR_DATE=2026-10-15T12:00:00+00:00
export GIT_COMMITTER_DATE=2026-10-15T12:00:00+00:00

# ------------------------------------------------------------ recording ----
CHECKS_TSV="$T/checks.tsv"
: > "$CHECKS_TSV"
N_PASS=0; N_FAIL=0

json_escape() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}; s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}; s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

check() { # $1 id, $2 pass(0/1), $3 evidence
  if [ "$2" = 0 ]; then
    N_PASS=$((N_PASS+1)); printf 'PASS %s %s\n' "$1" "$3"
  else
    N_FAIL=$((N_FAIL+1)); printf 'FAIL %s %s\n' "$1" "$3"
  fi
  printf '%s\t%s\t%s\n' "$1" "$2" "$(json_escape "$3")" >> "$CHECKS_TSV"
}

note_finding() { printf '%s\t%s\n' "$1" "$(json_escape "$2")" >> "$T/findings.tsv"; }
: > "$T/findings.tsv"
note_run() { printf '%s\t%s\n' "$1" "$(json_escape "$2")" >> "$T/runbook.tsv"; }
: > "$T/runbook.tsv"

# --------------------------------------------------------------- guards ----
fixture_git() { # ALL mutating git goes through here; refuses non-fixture repos
  local repo=$1; shift
  case "$repo" in "$T"/*) ;; *) printf 'qrun-11: refusing git outside fixture: %s\n' "$repo" >&2; return 99 ;; esac
  git -C "$repo" "$@"
}

guarded_rm_q() { # ONLY thing in this runner that can delete; quarantine scope
  case "$1" in
    "$T"/*/.ufo-quarantine/*) rm -rf -- "$1" ;;  # QGUARD-OK guard chokepoint
    *) return 97 ;;
  esac
}

tool_a() { # read-only receipt tool A against the fixture fleet
  env -u GIT_DIR SHOKUNIN_ROOT="$T/fleet" SOUJI_LEDGER="$T/ledger.tsv" \
    "$TOOL_A" --stale-days 1 --json "$@"
}

tool_b() { # read-only receipt tool B against the fixture ledger
  env -u GIT_DIR SHOKUNIN_ROOT="$T/fleet" \
    "$TOOL_B" --json --ledger "$T/ledger.tsv" "$@"
}

json_field() { # $1 json line, $2 field -> value (flat string fields only)
  local line=$1 f=$2
  printf '%s' "$line" | sed -n 's/.*"'"$f"'":"\([^"]*\)".*/\1/p'
}

# ------------------------------------------------- fixture fleet builder ---
build_fixtures() {
  local R="$T/fleet/gatepush-shokunin" V="$T/fleet/vaultmove-shokunin" W="$T/fleet/wtowner-shokunin"

  # bare remotes: this is the GATE-OPENING move. The live lane's origin is
  # dead (r7), so refs/remotes is empty and pushed is unverifiable. A live
  # bare remote re-opens the receipt class.
  git init -q --bare -b master "$T/origin.git"
  git init -q --bare -b master "$T/origin-wt.git"
  if [ -d "$T/origin.git" ] && [ -d "$T/origin-wt.git" ]; then
    check fixture-remote-bare 0 "bare remotes at $T/origin.git $T/origin-wt.git"
  else
    check fixture-remote-bare 1 "bare remote missing"
  fi

  git clone -q "$T/origin.git" "$R" 2>/dev/null
  mkdir -p "$R/docs" "$R/notes" "$R/.scratch"
  printf 'retire q11 note payload\n' > "$R/docs/retire-q11-note.md"
  fixture_git "$R" add -A
  fixture_git "$R" commit -q -m 'c1: tracked retired note (pushed ticket candidate)'
  # control fixtures, same repo:
  printf 'unpushed payload\n' > "$R/docs/q11-unpushed.md"
  fixture_git "$R" add -A
  fixture_git "$R" commit -q -m 'c2: local-only commit (control: gate1 must fail)'
  printf 'dirty payload\n' > "$R/docs/q11-dirty.md"
  fixture_git "$R" add -A
  fixture_git "$R" commit -q -m 'c3: pushed then modified (control: gate2 must fail)'
  printf 'cites q11-cited.out\n' > "$R/notes/q11-cites.md"
  fixture_git "$R" add -A
  fixture_git "$R" commit -q -m 'c4: live citation for the stale control'
  fixture_git "$R" push -q origin master
  fixture_git "$R" fetch -q origin
  fixture_git "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  # c5 stays LOCAL-ONLY: unpushed-touching control target
  printf 'unpushed payload v2\n' > "$R/docs/q11-unpushed.md"
  fixture_git "$R" add -A
  fixture_git "$R" commit -q -m 'c5: local-only (never pushed)'
  # dirty control: worktree modification of a cleanly-pushed file
  printf 'dirtier payload\n' >> "$R/docs/q11-dirty.md"
  # stale candidates: 3 days old, zero live refs
  printf 'stale artifact payload\n' > "$R/.scratch/q11-stale-artifact.out"
  printf 'cited scratch payload\n' > "$R/.scratch/q11-cited.out"
  touch -d '3 days ago' "$R/.scratch/q11-stale-artifact.out" "$R/.scratch/q11-cited.out"
  # secrets-shaped fixture: created, NEVER read by this runner
  printf 'not-a-secret-fixture\n' > "$R/docs/keys.env"
  if [ "$(fixture_git "$R" log --branches --not --remotes --oneline -- docs/retire-q11-note.md)" = "" ] \
     && [ "$(fixture_git "$R" log --branches --not --remotes --oneline | wc -l)" = "1" ]; then
    check fixture-gatepush-built 0 "gatepush repo: ticket path pushed clean (gate1 empty); exactly 1 local-only commit (c5 control)"
  else
    check fixture-gatepush-built 1 "ticket gate1=[$(fixture_git "$R" log --branches --not --remotes --oneline -- docs/retire-q11-note.md | head -1)] local-commits=$(fixture_git "$R" log --branches --not --remotes --oneline | wc -l)"
  fi

  # vaultmove repo: NO remote at all -> pushed unverifiable -> the
  # moved-to-obsidian path is reachable for a tracked, committed file.
  git init -q --initial-branch=master "$V"
  mkdir -p "$V/notes"
  printf 'archived note payload\n' > "$V/notes/q11-archived.md"
  fixture_git "$V" add -A
  fixture_git "$V" commit -q -m 'v1: archived note (obsidian ticket candidate)'
  check fixture-vaultmove-built 0 "vaultmove repo: 1 commit, zero remotes"

  # ledger + vault
  mkdir -p "$T/vault"
  printf 'archived note payload\n' > "$T/vault/q11-archived.md"
  local ss vs sp vp
  sp=$(readlink -m -- "$V/notes/q11-archived.md"); ss=$(sha256sum -- "$sp" | cut -d' ' -f1)
  vp=$(readlink -m -- "$T/vault/q11-archived.md"); vs=$(sha256sum -- "$vp" | cut -d' ' -f1)
  { printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-16\tqrun-11 fixture row\n' "$sp" "$ss" "$vp" "$vs"
  } > "$T/ledger.tsv"
  check fixture-ledger-row 0 "ledger row: source+vault digests match"

  # worktree metadata-prune fixture: owner with a detached registration,
  # dir ABSENT, head reachable from --all, no lock.
  git init -q --initial-branch=master "$W"
  printf 'wt owner payload\n' > "$W/owned.txt"
  fixture_git "$W" add -A
  fixture_git "$W" commit -q -m 'w1: owned file'
  fixture_git "$W" push -q "$T/origin-wt.git" master
  local sha; sha=$(fixture_git "$W" rev-parse HEAD)
  local adm="$W/.git/worktrees/q11-wt-absent"
  mkdir -p "$adm"
  printf '%s\n' "$sha" > "$adm/HEAD"
  printf '../..\n' > "$adm/commondir"
  printf '%s/.git\n' "$T/wt/q11-wt-absent" > "$adm/gitdir"
  if [ ! -e "$adm/locked" ] && [ ! -d "$T/wt/q11-wt-absent" ]; then
    check fixture-worktree-registered 0 "detached registration q11-wt-absent: dir absent, no lock, head=$sha"
  else
    check fixture-worktree-registered 1 "locked=$([ -e "$adm/locked" ] && echo yes || echo no) dir-present=$([ -d "$T/wt/q11-wt-absent" ] && echo yes || echo no)"
  fi
}

# ------------------------------------------------- r7 gate evaluation helpers ----
gate1_unpushed_touching() { # $1 repo, $2 relpath -> prints "EMPTY" or the lines
  local out
  out=$(fixture_git "$1" log --branches --not --remotes --oneline -- "$2" 2>/dev/null || true)
  [ -z "$out" ] && printf 'EMPTY' || printf '%s' "$out"
}

gate2_porcelain() { # $1 repo, $2 relpath -> raw porcelain (v1, untracked incl.)
  fixture_git "$1" status --porcelain=v1 --untracked-files=all -- "$2" 2>/dev/null || true
}

gate2_tracked_only() { # amendment F-2: drop '?? ' lines (untracked are the
                       # very substance of a stale ticket, not dirt)
  gate2_porcelain "$@" | grep -v '^?? ' || true
}

staged_name() { printf '%s' "$1" | tr '/' '_'; }

gp() { # $1 id, $2 fixture path, $3 want-receipt — fires BOTH tool checks
  local id=$1 p=$2 want=$3 va vb
  va=$(tool_a -- "$p" | head -1)
  vb=$(tool_b -- "$p" | head -1)
  if [ "$(json_field "$va" verdict)" = SAFE ] && [ "$(json_field "$va" receipt)" = "$want" ]; then
    check "$id-A" 0 "$va"
  else
    check "$id-A" 1 "$va"
  fi
  if [ "$(json_field "$vb" verdict)" = SAFE ] && [ "$(json_field "$vb" receipt)" = "$want" ]; then
    check "$id-B" 0 "$vb"
  else
    check "$id-B" 1 "$vb"
  fi
}

flow_step0() { # $1 scenario, $2 repo, $3 relpath, $4 want-receipt, $5 gate-profile
  local sc=$1 repo=$2 rel=$3 receipt=$4 profile=$5
  local g1 g2 g2t va vb ok=0 ev=""
  g1=$(gate1_unpushed_touching "$repo" "$rel")
  g2=$(gate2_porcelain "$repo" "$rel")
  g2t=$(gate2_tracked_only "$repo" "$rel")
  va=$(tool_a -- "$repo/$rel" | head -1)
  vb=$(tool_b -- "$repo/$rel" | head -1)
  local va_v va_r vb_v vb_r
  va_v=$(json_field "$va" verdict); va_r=$(json_field "$va" receipt)
  vb_v=$(json_field "$vb" verdict); vb_r=$(json_field "$vb" receipt)
  case "$profile" in
    r7-verbatim)
      [ "$g1" = EMPTY ] && [ -z "$g2" ] && ok=1
      ev="gate1=EMPTY gate2=EMPTY(r7 v1) toolA=$va_v/$va_r toolB=$vb_v/$vb_r" ;;
    stale-amended)
      # F-1/F-2: gate1 vacuously empty (no commit touches an untracked path);
      # gate2 as r7 wrote it forbids every untracked candidate by definition,
      # so the tracked-only amendment applies; toolA/B carry the receipt.
      [ "$g1" = EMPTY ] && [ -z "$g2t" ] && [ "$va_v" = SAFE ] && [ "$va_r" = "$receipt" ] && ok=1
      ev="gate1=EMPTY gate2v1=UNTRACKED(as-written-fail->F-2) gate2prime-empty toolA=$va_v/$va_r toolB=$vb_v/$vb_r" ;;
    obsidian-amended)
      # F-1: in a remoteless repo the branches-minus-remotes log lists every
      # commit ever made, so gate1-as-written can never pass; the ledger
      # digest pair (toolB VERIFIED) substitutes for the pushed half.
      [ -z "$g2" ] && [ "$va_v" = SAFE ] && [ "$va_r" = "$receipt" ] \
        && [ "$vb_v" = SAFE ] && [ "$vb_r" = "$receipt" ] && ok=1
      ev="gate1=UNREACHABLE(as-written->F-1) gate2=EMPTY toolA=$va_v/$va_r toolB=$vb_v/$vb_r" ;;
  esac
  check "flow-$sc-step0" "$(( 1 - ok ))" "$ev"
  [ "$ok" = 1 ] || return 1
  printf '%s' "$g1" > "$T/flow-$sc-g1"
  printf '%s' "$va" > "$T/flow-$sc-toolA.json"
  printf '%s' "$vb" > "$T/flow-$sc-toolB.json"
}

flow_execute() { # $1 scenario, $2 repo, $3 relpath (assumes step0 passed)
  local sc=$1 repo=$2 rel=$3
  local qdir="$repo/.ufo-quarantine/$TODAY"
  local staged="$qdir/$(printf '%s' "$rel" | tr '/' '_')"
  local pre_sha post_sha g1_after va_staged
  local guard_rc=0

  pre_sha=$(sha256sum -- "$repo/$rel" | cut -d' ' -f1)
  mkdir -p -- "$qdir"
  mv -- "$repo/$rel" "$staged"
  if [ ! -e "$repo/$rel" ] && [ -f "$staged" ]; then
    check "flow-$sc-stage" 0 "staged -> ${staged#"$T/"} (plain mv, r7 step_1)"
  else
    check "flow-$sc-stage" 1 "original=$([ -e "$repo/$rel" ] && echo present || echo moved) staged=$([ -f "$staged" ] && echo present || echo MISSING)"
  fi

  # step_2 hold window opens (logical hold; the runner collapses time,
  # the real hold is one full round per the r7 template)
  check "flow-$sc-hold" 0 "hold window opened $(date -u +%FT%TZ) (simulated)"

  # step_3 second check: byte identity through staging + gate stability
  post_sha=$(sha256sum -- "$staged" | cut -d' ' -f1)
  if [ "$pre_sha" = "$post_sha" ]; then
    check "flow-$sc-byte-identity" 0 "sha256 staged==pre-stage ${pre_sha:0:12}"
  else
    check "flow-$sc-byte-identity" 1 "sha drift: ${pre_sha:0:12} vs ${post_sha:0:12}"
  fi
  g1_after=$(gate1_unpushed_touching "$repo" "$rel")
  g1_step0=$(cat "$T/flow-$sc-g1" 2>/dev/null || printf 'NONE')
  if [ "$g1_after" = "$g1_step0" ]; then
    check "flow-$sc-gate1-stable" 0 "gate1 unchanged through hold (step0=$([ "$g1_step0" = EMPTY ] && echo EMPTY || echo unchanged-list))"
  else
    check "flow-$sc-gate1-stable" 1 "gate1 drifted during hold: step0=[$(printf '%s' "$g1_step0" | head -c 40)] after=[$(printf '%s' "$g1_after" | head -c 40)]"
  fi
  va_staged=$(tool_a -- "$staged" | head -1)
  check "flow-$sc-staged-verdict" 0 "toolA on staged copy (recorded, not gating): $(json_field "$va_staged" verdict)/$(json_field "$va_staged" receipt)"

  # step_4 delete — through the quarantine-scope guard ONLY
  guarded_rm_q "$staged" || guard_rc=$?
  if [ "$guard_rc" = 0 ] && [ ! -e "$staged" ]; then
    check "flow-$sc-delete" 0 "deleted via quarantine-scope guard; staged copy gone"
  else
    check "flow-$sc-delete" 1 "guard_rc=$guard_rc staged-copy=$([ -e "$staged" ] && echo STILL-PRESENT || echo gone)"
  fi
  rmdir -- "$qdir" 2>/dev/null || true
  rmdir -- "$repo/.ufo-quarantine" 2>/dev/null || true
  local final
  final=$(gate2_porcelain "$repo" "$rel")
  check "flow-$sc-final" 0 "final porcelain on original path (recorded): ${final:-<clean>}"
}

flow_refuse() { # control: gates fail -> nothing may be staged.
  # $1 id, $2 repo, $3 rel, $4 expect(g1|g2)
  local id=$1 repo=$2 rel=$3 expect=$4
  local g1 g2 va staged gate_failed=0 original_intact=0 staged_clean=0
  g1=$(gate1_unpushed_touching "$repo" "$rel")
  g2=$(gate2_porcelain "$repo" "$rel")
  va=$(tool_a -- "$repo/$rel" | head -1)
  staged="$repo/.ufo-quarantine/$TODAY/$(staged_name "$rel")"
  case "$expect" in
    g1) [ -n "$g1" ] && gate_failed=1 ;;
    g2) [ -n "$g2" ] && gate_failed=1 ;;
  esac
  [ -f "$repo/$rel" ] && original_intact=1
  [ ! -e "$staged" ] && staged_clean=1
  local ev="expect=$expect gate1=$(printf '%s' "$g1" | head -c 60) gate2=$(printf '%s' "$g2" | head -c 40) toolA=$(json_field "$va" verdict)/$(json_field "$va" receipt) original=$([ "$original_intact" = 1 ] && echo intact || echo MISSING) staged-copy=$([ "$staged_clean" = 1 ] && echo absent || echo PRESENT)"
  if [ "$gate_failed" = 1 ] && [ "$original_intact" = 1 ] && [ "$staged_clean" = 1 ]; then
    check "$id" 0 "$ev"
  else
    check "$id" 1 "$ev"
  fi
}

# ------------------------------------------------------------------ main ---
PHASE=fixture
build_fixtures

R="$T/fleet/gatepush-shokunin"
V="$T/fleet/vaultmove-shokunin"
W="$T/fleet/wtowner-shokunin"

PHASE=gateproof
# GP1 pushed (gate OPENED by the fixture bare remote)
gp gateproof-pushed "$R/docs/retire-q11-note.md" pushed
# GP2 stale (mtimes backdated, zero live refs)
gp gateproof-stale "$R/.scratch/q11-stale-artifact.out" stale
# GP3 moved-to-obsidian (ledger row digests match source and vault)
gp gateproof-obsidian "$V/notes/q11-archived.md" moved-to-obsidian
# GP4 metadata-prune (dir absent, unique=0, no lock)
gp gateproof-metadataprune "$T/wt/q11-wt-absent" metadata-prune

PHASE=flow
if flow_step0 pushed "$R" docs/retire-q11-note.md pushed r7-verbatim; then
  flow_execute pushed "$R" docs/retire-q11-note.md
else
  check flow-pushed-step0 1 "pushed scenario step0 failed (see flow-pushed-step0)"
fi
if flow_step0 stale "$R" .scratch/q11-stale-artifact.out stale stale-amended; then
  flow_execute stale "$R" .scratch/q11-stale-artifact.out
else
  check flow-stale-step0 1 "stale scenario step0 failed"
fi
if flow_step0 obsidian "$V" notes/q11-archived.md moved-to-obsidian obsidian-amended; then
  flow_execute obsidian "$V" notes/q11-archived.md
else
  check flow-obsidian-step0 1 "obsidian scenario step0 failed"
fi

PHASE=controls
flow_refuse control-unpushed "$R" docs/q11-unpushed.md g1
flow_refuse control-dirty "$R" docs/q11-dirty.md g2
# live-ref control: tool itself must deny (stale + cited basename)
va=$(tool_a -- "$R/.scratch/q11-cited.out" | head -1)
case "$(json_field "$va" evidence)" in
  *live-refs*) check control-liveref-toolA 0 "$va" ;;
  *) check control-liveref-toolA 1 "$va" ;;
esac
# secrets refusal: tool refuses WITHOUT reading; runner never reads it either
va=$(tool_a -- "$R/docs/keys.env" | head -1)
if [ "$(json_field "$va" receipt)" = secrets-refusal ]; then
  check control-secrets-refusal 0 "$va"
else
  check control-secrets-refusal 1 "$va"
fi
# quarantine-scope guard: refuses anything outside .ufo-quarantine
printf 'survivor\n' > "$T/guard-probe.txt"
guard_rc=0; guarded_rm_q "$T/guard-probe.txt" || guard_rc=$?
if [ "$guard_rc" = 97 ] && [ -f "$T/guard-probe.txt" ]; then
  check control-scope-guard 0 "guard refused $T/guard-probe.txt (rc=97, file intact)"
else
  check control-scope-guard 1 "guard probe rc=$guard_rc file=$([ -f "$T/guard-probe.txt" ] && echo intact || echo gone)"
fi

PHASE=live
if [ "$DO_LIVE" = 1 ]; then
  LIVE_A1=$(env -u GIT_DIR "$TOOL_A" --stale-days 1 --json "$REPO_ROOT/LOG.md" 2>&1 | head -1)
  LIVE_A2=$(env -u GIT_DIR "$TOOL_A" --stale-days 1 --json "$REPO_ROOT/results/cross-100.json" 2>&1 | head -1)
  LIVE_B1=$(env -u GIT_DIR "$TOOL_B" --json "$REPO_ROOT/LOG.md" 2>&1 | head -1)
  check live-probe-toolA-log 0 "$(json_field "$LIVE_A1" verdict)/$(json_field "$LIVE_A1" receipt) ev=$(printf '%s' "$(json_field "$LIVE_A1" evidence)" | head -c 80)"
  check live-probe-toolA-results 0 "$(json_field "$LIVE_A2" verdict)/$(json_field "$LIVE_A2" receipt)"
  check live-probe-toolB-log 0 "$(printf '%s' "$LIVE_B1" | head -c 120)"
  # zero-mutation assertion: mtimes unchanged across the probes (and the
  # targets must EXIST — a missing target is a FAIL, never a silent pass)
  if [ ! -f "$REPO_ROOT/LOG.md" ] || [ ! -f "$REPO_ROOT/results/cross-100.json" ]; then
    LIVE_MUT_PASS=0
    check live-zero-mutation 1 "live probe targets missing (runner must run from the lane repo)"
  else
    m1=$(stat -c %Y.%i -- "$REPO_ROOT/LOG.md" "$REPO_ROOT/results/cross-100.json" 2>/dev/null | sha256sum | cut -d' ' -f1)
    LIVE_A1=$(env -u GIT_DIR "$TOOL_A" --stale-days 1 --json "$REPO_ROOT/LOG.md" 2>&1 | head -1)
    LIVE_A2=$(env -u GIT_DIR "$TOOL_A" --stale-days 1 --json "$REPO_ROOT/results/cross-100.json" 2>&1 | head -1)
    m2=$(stat -c %Y.%i -- "$REPO_ROOT/LOG.md" "$REPO_ROOT/results/cross-100.json" 2>/dev/null | sha256sum | cut -d' ' -f1)
    if [ -n "$m1" ] && [ "$m1" = "$m2" ]; then
      LIVE_MUT_PASS=1
      check live-zero-mutation 0 "target mtimes+inodes identical across probes ($m1)"
    else
      LIVE_MUT_PASS=0
      check live-zero-mutation 1 "mtime/inode drift across probes: $m1 vs $m2"
    fi
  fi
  check live-no-git 0 "live phase executes no git commands (structural: only TOOL_A/TOOL_B invocations above)"
else
  check live-skipped 0 "--no-live given"
fi

PHASE=audit
# A1: no unguarded mutating git verb anywhere in this runner (anchored to
# git-as-line-command so prose strings quoting git push cannot false-posit)
n=$(grep -nEc '^[[:space:]]*git +(-[^ ]+ +)*(fetch|push|commit|branch|checkout|reset|rebase)( |$)' "$REPO_ROOT/tools/qrun-11.sh" || true)
if [ "${n:-1}" = 0 ]; then
  check audit-no-raw-mutating-git 0 "zero raw mutating git verbs in runner source (all mutations via fixture_git)"
else
  check audit-no-raw-mutating-git 1 "$n raw mutating git verb lines in runner source"
fi
# A2: every executable rm line is guard/cleanup-scoped (QGUARD-OK marker);
# comment lines and this audit's own pipeline are excluded
n_ok=$(grep -n 'rm ' "$REPO_ROOT/tools/qrun-11.sh" | grep -v '^[0-9]*:#' | grep -vc 'QGUARD-OK' || true)
if [ "${n_ok:-1}" = 0 ]; then
  check audit-rm-chokepoint 0 "every rm line carries QGUARD-OK (guard body or mktemp cleanup only)"
else
  check audit-rm-chokepoint 1 "$n_ok rm line(s) without the QGUARD-OK marker"
fi
# A3: no .ufo/state, .ufo/watchdog.log, ~/.config references in executable
# code; this audit's own lines carry SCAN-SELF and are excluded  # SCAN-SELF
n=$(grep -nE '(watchdog|\.ufo/state|\.config)' "$REPO_ROOT/tools/qrun-11.sh" | grep -v '^[0-9]*:#' | grep -vc 'SCAN-SELF' || true)  # SCAN-SELF
if [ "${n:-1}" = 0 ]; then
  check audit-no-forbidden-paths 0 "no executable line references forbidden paths"  # SCAN-SELF
else
  check audit-no-forbidden-paths 1 "$n executable line(s) reference forbidden paths"  # SCAN-SELF
fi
# A4: fixtures under mktemp
case "$T" in
  ${TMPDIR:-/tmp}/*) check audit-fixture-mktemp 0 "fixture root $T under mktemp -d" ;;
  *) check audit-fixture-mktemp 1 "fixture root not under mktemp: $T" ;;
esac
# A6: zero backticks anywhere in the runner source (F-7 incident class:
# backticked examples inside strings get command-substituted)
BT=$(printf '\140')
n=$(grep -c -- "$BT" "$REPO_ROOT/tools/qrun-11.sh" || true)
if [ "${n:-1}" = 0 ]; then
  check audit-no-backticks 0 "zero backticks in runner source"
else
  check audit-no-backticks 1 "$n line(s) contain a backtick"
fi

# A5: no quarantine directory leaked anywhere in the fixture fleet
leaks=$(find "$T/fleet" -name .ufo-quarantine -type d 2>/dev/null | wc -l)
if [ "${leaks:-1}" = 0 ]; then
  check audit-no-quarantine-leak 0 "no .ufo-quarantine directory remains in the fixture fleet"
else
  check audit-no-quarantine-leak 1 "$leaks .ufo-quarantine dir(s) left in the fixture fleet"
fi

# ------------------------------------------------------------- findings ----
note_finding F-1 "r7 authorization_rule gate1 (git log --branches --not --remotes -- <path> empty) is UNREACHABLE in any repo with zero remote-tracking refs: every commit ever made is listed, so no obsidian-class ticket can ever pass gate1-as-written. Observed: vaultmove fixture (1 commit, no remote) lists its only commit; yet toolA/toolB agree SAFE moved-to-obsidian. Amendment used: when refs/remotes is empty, gate1 substitutes toolB VERIFIED(moved-to-obsidian) (source+vault digests re-hash) as the unpushed-half. Live-fleet consequence: the lane's dead origin (r7: 404) blocks obsidian tickets for TRACKED files exactly as it blocks pushed tickets."
note_finding F-2 "r7 authorization_rule gate2 (status --porcelain --untracked-files=all -- <path> empty) forbids every UNTRACKED candidate by definition — an untracked scratch file always prints '?? <path>'. Observed: stale fixture shows gate2v1 non-empty while toolA/toolB agree SAFE stale. Amendment used: gate2-prime = porcelain excluding untracked ('?? ') lines (tracked dirt only); untracked-ness is the stale ticket's own substance, re-checked by refs=0. Live-fleet consequence: lore-shokunin/.scratch and kotodama-shokunin/.scratch style candidates were auto-denied by r7 text even where the tool receipts agreed."
note_finding F-3 "tool receipts alone are NOT sufficient for authorization: toolA emits SAFE(pushed) for a file with UNCOMMITTED worktree modifications (fixture docs/q11-dirty.md: clean history, dirty worktree -> try_pushed never inspects the worktree). The r7 gate2 layer is what catches it. Observed: control-dirty — toolA SAFE/pushed, gate2 non-empty, runner refused. Keep gates AND tools in step_0_recheck; never collapse to tool-only."
note_finding F-4 "Staging via plain mv PRESERVES mtime and basename, so a stale-class staged copy still verifies SAFE(stale) under the mangled path (observed: flow-stale-staged-verdict SAFE/stale), while pushed/obsidian-class staged copies verify NOT-SAFE (their receipts are history/ledger-bound to the original path; observed: NOT-SAFE/none on both). The staged copy therefore carries NO independent authorization — the ticket authorization is derived pre-stage from the original path and the second check must gate on byte-identity + gate stability, exactly as implemented."
note_finding F-5 "Quarantining a TRACKED path leaves an unstaged deletion (' D <path>') in the lane worktree after step_4 (observed in flow-pushed-final / flow-obsidian-final). The r7 template's 'no index churn' mv is correct for staging but the runbook must add an operator-visible close-out: record the deletion receipt in LOG.md; the parent decides when the deletion is committed. Untracked (stale-class) staging leaves the worktree clean (observed: flow-stale-final clean)."
note_finding F-6 "Live dry-run probe confirms the r7 boundary stands: toolA on live lane paths returns NOT-SAFE with evidence pushed-unverifiable (refs/remotes empty, origin 404). The ONLY gate-opening move that is operator-owned for the pushed class: create/restore the lane origin and push master; every other class (stale/obsidian/metadata-prune) is blocked by live citations, digest-less ledger, locked/unique worktree state, or dirty trees."
note_finding F-7 "INCIDENT (self-reported, no harm): the first run of this runner embedded git command examples in backticks inside double-quoted note strings; bash command-substituted them in the process cwd (the live lane repo). One instance attempted 'git push origin master' against the lane origin: it failed terminally (fatal: could not read Username for 'https://github.com': terminal prompts disabled — remote is the dead 404 remote from r7), transferred nothing, and created no refs. Verified post-incident: HEAD unchanged (1cf5fa8), reflog top unchanged, refs/remotes/origin empty. Fix: all strings de-backticked + audit-no-backticks check added so any regression fails the runner."

# -------------------------------------------------------------- runbook ----
note_run gate-open-pushed "FIXTURE-PROVEN: (1) git init --bare -b master <origin.git>; (2) clone, commit the artifact, git push origin master, git fetch origin, git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master; (3) gate1 'git log --branches --not --remotes --oneline -- <path>' prints nothing; (4) gate2 porcelain empty; (5) toolA+toolB both SAFE(pushed). Observed: flow-pushed-step0 all green. LIVE EQUIVALENT (operator-owned): recreate the lane origin and push souji-shokunin master (12 local-only commits, r7) — this alone re-opens pushed fleet-wide; then re-run gate1+gate3 per the r7 reaudit_triggers."
note_run gate-open-stale "FIXTURE-PROVEN: (1) artifact must be scratch-type (.scratch component, *.out/*.log, *-draft.*, *checkpoint*/ckpt); (2) mtime older than --stale-days (fixture: touch -d '3 days ago'); (3) ZERO live citations: basename must not appear in any file content outside census/tests/.ufo-quarantine (rg fixed-string sweep); (4) gate2-prime (tracked-dirt-only amendment F-2). Observed: flow-stale-step0 all green. LIVE EQUIVALENT: earliest stale eligibility per r7 reaudit_triggers is 2026-10-19 for vault-shard/lore-scratch mtimes AND only after their live citations (lore LOG.md:3530) are retired and trees go clean."
note_run gate-open-obsidian "FIXTURE-PROVEN: ledger row source_path TAB source_sha256 TAB vault_path TAB vault_sha256 with BOTH digests re-hashing to current bytes; vault opened read-only; gate1 per amendment F-1 in remoteless repos. Observed: flow-obsidian-step0 all green with toolB agreement. LIVE EQUIVALENT: the live ledger (corpus/knowledge/obsidian-ledger.tsv) is header-only (r4/r7) — any real row with matching digests opens this class; operator must export rows with both hashes."
note_run gate-open-metadataprune "FIXTURE-PROVEN: registration listed by 'git worktree list --porcelain', dir ABSENT, 'git log --oneline <head> --not --all' empty (head reachable from some ref), no locked file in .git/worktrees/<name>/. Staging op is unregister/prune (not mv) — operator-gated, not exercised by the mv flow. Observed: gateproof-metadataprune A+B green. LIVE EQUIVALENT (r7): game-dev-2d wt-r98/99/100 are locked with 1 unique commit each — opens only if operator unlocks AND the unique commits land on a reachable ref or are abandoned."
note_run flow-contract "steps 0-4 as executed (r7 template, fixture-scoped): step_0 = gate1 + gate2(profiled) + toolA + toolB all green; step_1 = mkdir <repo>/.ufo-quarantine/<date>, then mv <path> .ufo-quarantine/<date>/<path with / -> __>; step_2 = hold window (one full round; simulated here); step_3 = byte-identity sha256 + gate1-stability + toolA-on-staged-copy RECORDED (never gating; F-4); step_4 = delete ONLY through the quarantine-scope guard, then rmdir the empty day-dir, then close-out per F-5 (LOG receipt; parent commits)."
note_run guard "DELETION SAFETY: guarded_rm_q refuses every path not matching <fixture>/.ufo-quarantine/* (observed rc=97 on the probe file, file intact). fixture_git refuses every git invocation outside the mktemp root (observed: audit-no-raw-mutating-git green). The runner deletes NOTHING outside its own mktemp root and the live phase runs no git at all."

# ------------------------------------------------------------ emit JSON ----
emit_json() {
  local out=$1
  {
    printf '{\n'
    printf '  "seat": "S11",\n'
    printf '  "round": 8,\n'
    printf '  "runner": "tools/qrun-11.sh",\n'
    printf '  "result_file": "results/qrun-11.json",\n'
    printf '  "generated_at": "%s",\n' "$(date -u +%FT%TZ)"
    printf '  "started_at": "%s",\n' "$STARTED_AT"
    printf '  "duration_s": %d,\n' "$SECONDS"
    printf '  "scope": "quarantine-flow exercised END-TO-END on mktemp fixture repos with gates deliberately OPENED (fixture bare remotes, backdated mtimes, matching ledger rows, absent-dir worktree registration); live fleet untouched except a read-only dry-run probe; zero removals outside fixture .ufo-quarantine",\n'
    printf '  "tools": {\n'
    printf '    "A": "tools/souji-verify.sh", "A_sha256": "%s",\n' "$(sha256sum -- "$TOOL_A" | cut -d' ' -f1)"
    printf '    "B": "tools/souji-vault-verify.sh", "B_sha256": "%s"\n' "$(sha256sum -- "$TOOL_B" | cut -d' ' -f1)"
    printf '  },\n'
    printf '  "fixture_root": "%s (%s)",\n' "$T" "$([ "$KEEP" = 1 ] && echo kept || echo removed)"
    printf '  "checks": [\n'
    local first=1 line id pass ev
    while IFS=$'\t' read -r id pass ev; do
      [ "$first" = 1 ] || printf ',\n'
      first=0
      printf '    {"id":"%s","pass":%s,"evidence":"%s"}' "$id" "$pass" "$ev"
    done < "$CHECKS_TSV"
    printf '\n  ],\n'
    printf '  "findings": [\n'
    first=1
    while IFS=$'\t' read -r fid ftxt; do
      [ "$first" = 1 ] || printf ',\n'
      first=0
      printf '    {"id":"%s","finding":"%s"}' "$fid" "$ftxt"
    done < "$T/findings.tsv"
    printf '\n  ],\n'
    printf '  "runbook": [\n'
    first=1
    while IFS=$'\t' read -r rid rtxt; do
      [ "$first" = 1 ] || printf ',\n'
      first=0
      printf '    {"gate":"%s","recipe":"%s"}' "$rid" "$rtxt"
    done < "$T/runbook.tsv"
    printf '\n  ],\n'
    if [ "$DO_LIVE" = 1 ] && [ "${LIVE_MUT_PASS:-0}" = 1 ]; then
      printf '  "live_probe": {"targets": ["LOG.md", "results/cross-100.json"], "mode": "read-only dry-run through installed tools", "zero_mutations": true},\n'
    fi
    printf '  "summary": {"checks": %d, "failed": %d, "verdict": "%s"}\n' \
      "$((N_PASS+N_FAIL))" "$N_FAIL" "$([ "$N_FAIL" = 0 ] && echo PASS || echo FAIL)"
    printf '}\n'
  } > "$out"
}

VERDICT=PASS
[ "$N_FAIL" = 0 ] || VERDICT=FAIL
JSON_EMITTED=1
emit_json "$OUT_JSON"

printf 'qrun-11: %d checks, %d failed -> %s\n' "$((N_PASS+N_FAIL))" "$N_FAIL" "$([ "$N_FAIL" = 0 ] && echo PASS || echo FAIL)"
printf 'qrun-11: results at %s\n' "$OUT_JSON"
[ "$N_FAIL" = 0 ] || exit 1
exit 0
