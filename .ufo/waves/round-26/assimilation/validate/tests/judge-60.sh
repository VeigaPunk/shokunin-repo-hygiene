#!/usr/bin/env bash
# tests/judge-60.sh — round-2 SEAT S60 "final judge": independent fixture battery
# for tools/souji-verify.sh against the binding spec tools/souji-verify.spec.md.
#
# Usage: tests/judge-60.sh [--candidate PATH] [--out PATH] [--wait SECONDS]
#   candidate default: <lane repo>/tools/souji-verify.sh
#   out default:       <lane repo>/tests/results/final-60.json
# Exit: 0 = every hard case passed; 1 = candidate absent or any hard case failed
#       or a rail was violated; 2 = usage error.
#
# Safety: all fixture state lives under one mktemp -d; the live tree is only
# read (hashes/status). The harness itself never runs fetch/push/reset/rebase
# against any repository; fixture setup uses init/add/commit/worktree/update-ref
# inside the mktemp universe only. Never touches .ufo/state, .ufo/watchdog.log,
# ~/.config (HOME and XDG_CONFIG_HOME are redirected into the mktemp dir).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CANDIDATE="$REPO_ROOT/tools/souji-verify.sh"
OUT="$REPO_ROOT/tests/results/final-60.json"
SPEC="$REPO_ROOT/tools/souji-verify.spec.md"
WAIT=0

while [ $# -gt 0 ]; do
  case "$1" in
    --candidate) CANDIDATE="$2"; shift 2;;
    --out)       OUT="$2"; shift 2;;
    --wait)      WAIT="$2"; shift 2;;
    -h|--help)   sed -n '2,14p' "$0"; exit 0;;
    *) echo "judge-60: usage: judge-60.sh [--candidate PATH] [--out PATH] [--wait SECONDS]" >&2; exit 2;;
  esac
done

# ---------------------------------------------------------------- wait+stability
if [ ! -s "$CANDIDATE" ] && [ "$WAIT" -gt 0 ]; then
  echo "judge-60: waiting up to ${WAIT}s for candidate $CANDIDATE" >&2
  deadline=$(( $(date +%s) + WAIT ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    [ -s "$CANDIDATE" ] && break
    sleep 5
  done
fi
if [ -s "$CANDIDATE" ]; then
  last=""; stable=0; deadline=$(( $(date +%s) + 90 ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    cur="$(stat -c '%Y:%s' "$CANDIDATE" 2>/dev/null || echo gone)"
    if [ "$cur" = "$last" ]; then stable=$((stable+1)); else stable=0; last="$cur"; fi
    [ "$stable" -ge 2 ] && break
    sleep 3
  done
fi

WORK="$(mktemp -d /tmp/judge-60.XXXXXX)"
mkdir -p "$WORK/tmp"
FINALIZED=0

san()  { printf '%s' "$1" | tr '\n' ' ' | tr -d '\t'; }
emit() { printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$(san "$1")" "$(san "$2")" "$(san "$3")" "$(san "$4")" "$(san "$5")" "$(san "$6")" >> "$WORK/cases.tsv"; }
meta() { printf '%s\t%s\n' "$1" "$(san "$2")" >> "$WORK/meta.tsv"; }
rp()   { if [ -n "$1" ]; then realpath -m -- "$1" 2>/dev/null || printf '%s' "$1"; else printf ''; fi; }

write_json() {
  J60_WORK="$WORK" J60_OUT="$OUT" python3 - <<'PY' || true
import json, os, sys
work = os.environ['J60_WORK']; out = os.environ['J60_OUT']
meta = {}
with open(os.path.join(work, 'meta.tsv')) as fh:
    for ln in fh:
        ln = ln.rstrip('\n')
        if ln:
            k, _, v = ln.partition('\t'); meta[k] = v
cases = []
try:
    lines = open(os.path.join(work, 'cases.tsv')).read().splitlines()
except FileNotFoundError:
    lines = []
p = f = i = 0
for ln in lines:
    if not ln:
        continue
    parts = (ln.split('\t') + [''] * 6)[:6]
    c = {'id': parts[0], 'kind': parts[1], 'expected': parts[2],
         'actual': parts[3], 'result': parts[4], 'detail': parts[5]}
    cases.append(c)
    if parts[4] == 'pass': p += 1
    elif parts[4] == 'fail': f += 1
    else: i += 1
doc = {
    'seat': 'S60',
    'role': 'final judge — independent fixture battery (round 2)',
    'generated_at_utc': meta.get('generated_at_utc', ''),
    'spec': {'path': meta.get('spec_path', ''), 'sha256': meta.get('spec_sha256', '')},
    'harness': {'path': meta.get('harness_path', ''), 'sha256': meta.get('harness_sha256', '')},
    'candidate': {
        'path': meta.get('candidate_path', ''),
        'present': meta.get('candidate_present', '') == 'yes',
        'sha256': meta.get('candidate_sha256', ''),
        'bytes': meta.get('candidate_bytes', ''),
        'selftest_exit': meta.get('candidate_selftest_exit', ''),
    },
    'lane_repo': meta.get('lane_repo', ''),
    'lane_head_before': meta.get('lane_head_before', ''),
    'lane_head_after': meta.get('lane_head_after', ''),
    'lane_tracked_dirty_after': meta.get('lane_tracked_dirty_after', ''),
    'fixture_universe': meta.get('fixture_universe', ''),
    'rails': {
        'static_git_write_scan': meta.get('rail_static', ''),
        'ufo_state_touched': meta.get('rail_ufo_state', ''),
        'watchdog_stat_before': meta.get('rail_watchdog_before', ''),
        'watchdog_stat_after': meta.get('rail_watchdog_after', ''),
    },
    'cases': cases,
    'summary': {'total': len(cases), 'passed': p, 'failed': f, 'informational': i,
                'hard_failures': meta.get('hard_failures', '')},
    'verdict': meta.get('verdict', 'FAIL'),
}
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w') as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)
    fh.write('\n')
print('judge-60: wrote %s (cases=%d pass=%d fail=%d info=%d) verdict=%s'
      % (out, len(cases), p, f, i, doc['verdict']))
PY
}

finalize() {
  if [ "$FINALIZED" -eq 0 ]; then
    FINALIZED=1
    meta generated_at_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    meta lane_head_after "$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo '')"
    meta lane_tracked_dirty_after "$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null | grep -v '^??' | wc -l || true)"
    meta rail_watchdog_after "$(stat -c '%Y:%s' "$WATCHDOG" 2>/dev/null || echo 'absent')"
    if [ "${FAIL_HARD:-1}" -eq 0 ]; then meta verdict PASS; else meta verdict FAIL; fi
    meta hard_failures "${FAIL_HARD:-1}"
    write_json
  fi
}
trap 'rc=$?; finalize || true; rm -rf "$WORK"; exit "$rc"' EXIT

FAIL_HARD=0
hard_fail() { FAIL_HARD=$((FAIL_HARD + 1)); }

mkdir -p "$(dirname "$OUT")" "$WORK/origins" "$WORK/vault" "$WORK/wt"
FLEET_REAL="$(cd "$REPO_ROOT/.." && pwd)"
WATCHDOG="$FLEET_REAL/.ufo/watchdog.log"
UFO_STATE="$FLEET_REAL/.ufo/state"

meta seat S60
meta harness_path "tests/judge-60.sh"
meta harness_sha256 "$(sha256sum "$REPO_ROOT/tests/judge-60.sh" | awk '{print $1}')"
meta spec_path "tools/souji-verify.spec.md"
meta spec_sha256 "$(sha256sum "$SPEC" 2>/dev/null | awk '{print $1}')"
meta lane_repo "$REPO_ROOT"
meta lane_head_before "$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo '')"
meta rail_watchdog_before "$(stat -c '%Y:%s' "$WATCHDOG" 2>/dev/null || echo 'absent')"
UFO_BEFORE=""
if [ -d "$UFO_STATE" ]; then
  UFO_BEFORE="$(find "$UFO_STATE" -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -1)"
fi

# ------------------------------------------------------------- candidate absence
if [ ! -s "$CANDIDATE" ]; then
  meta candidate_path "$CANDIDATE"
  meta candidate_present no
  meta candidate_sha256 ""
  meta candidate_bytes ""
  meta candidate_selftest_exit ""
  meta fixture_universe "(not built — candidate absent)"
  meta rail_static "not-run"
  meta rail_ufo_state "not-run"
  emit C0 candidate "candidate present and judged" "tools/souji-verify.sh absent or empty" fail "candidate missing at judge time"
  hard_fail
  exit 1
fi

meta candidate_path "$CANDIDATE"
meta candidate_present yes
meta candidate_sha256 "$(sha256sum "$CANDIDATE" | awk '{print $1}')"
meta candidate_bytes "$(stat -c %s "$CANDIDATE")"

# ------------------------------------------------------------------- fixture env
export HOME="$WORK/home"
export XDG_CONFIG_HOME="$WORK/home/.config"
export GIT_CONFIG_NOSYSTEM=1
mkdir -p "$HOME" "$XDG_CONFIG_HOME"
G() { git -c user.name=judge -c user.email=judge@shokunin.local -c commit.gpgsign=false -c advice.detachedHead=false "$@"; }
ginit() { G init -q "$1"; G -C "$1" symbolic-ref HEAD refs/heads/master; }
gc() { local r="$1" m="$2"; shift 2; G -C "$r" add -- "$@"; G -C "$r" commit -q -m "$m"; }
origin_for() { local o="$WORK/origins/$2.git"; G init -q --bare "$o"; printf '%s\n' "$1/.git/objects" > "$o/objects/info/alternates"; G -C "$1" remote add origin "$o"; }
set_tip() { # repo sha with_head
  G -C "$1" update-ref refs/remotes/origin/master "$2"
  local o; o="$(G -C "$1" remote get-url origin)"
  G -C "$o" update-ref refs/heads/master "$2"
  if [ "$3" = yes ]; then G -C "$1" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master; fi
}

FLEET="$WORK/fleet"
mkdir -p "$FLEET"
ginit "$FLEET"; printf 'fleet note\n' > "$FLEET/fleet-note.txt"; gc "$FLEET" c1 "$FLEET/fleet-note.txt"
origin_for "$FLEET" fleet; set_tip "$FLEET" "$(G -C "$FLEET" rev-parse HEAD)" yes

# lane-alpha: clean, pushed, origin/HEAD present — F1 (pushed), F10 (secret-shaped pushed)
LA="$FLEET/lane-alpha"; mkdir -p "$LA/docs" "$LA/notes"; ginit "$LA"
printf 'keep\n' > "$LA/docs/keep.txt"; gc "$LA" c1 "$LA/docs/keep.txt"
printf 'beta\n' > "$LA/notes/beta.md"; gc "$LA" c2 "$LA/notes/beta.md"
printf 'env-fixture\n' > "$LA/app.env"; gc "$LA" c3 "$LA/app.env"
origin_for "$LA" lane-alpha; set_tip "$LA" "$(G -C "$LA" rev-parse HEAD)" yes

# lane-delta: clean tree, one unpushed introducing commit — F2
LD="$FLEET/lane-delta"; mkdir -p "$LD"; ginit "$LD"
printf 'base\n' > "$LD/base.txt"; gc "$LD" c1 "$LD/base.txt"
origin_for "$LD" lane-delta; set_tip "$LD" "$(G -C "$LD" rev-parse HEAD)" yes
printf 'local only\n' > "$LD/local-only.txt"; gc "$LD" c2-local-only "$LD/local-only.txt"

# lane-charlie: clean, pushed, NO origin/HEAD, single origin ref — F9 (D1 fallback)
LC="$FLEET/lane-charlie"; mkdir -p "$LC/docs"; ginit "$LC"
printf 'keep9\n' > "$LC/docs/keep9.txt"; gc "$LC" c1 "$LC/docs/keep9.txt"
printf 'more9\n' > "$LC/docs/more9.txt"; gc "$LC" c2 "$LC/docs/more9.txt"
origin_for "$LC" lane-charlie; set_tip "$LC" "$(G -C "$LC" rev-parse HEAD)" no

# lane-bravo: repo-root case, 3 unpushed commits + dirty (2 modified, 1 untracked) — F3
LB="$FLEET/lane-bravo"; mkdir -p "$LB"; ginit "$LB"
printf 'a\n' > "$LB/a.txt"; printf 'b\n' > "$LB/b.txt"; gc "$LB" c1 "$LB/a.txt" "$LB/b.txt"
origin_for "$LB" lane-bravo; set_tip "$LB" "$(G -C "$LB" rev-parse HEAD)" yes
printf '2\n' >> "$LB/a.txt"; gc "$LB" c2 "$LB/a.txt"
printf '3\n' >> "$LB/a.txt"; gc "$LB" c3 "$LB/a.txt"
printf '4\n' >> "$LB/a.txt"; gc "$LB" c4 "$LB/a.txt"
printf 'dirty-a\n' >> "$LB/a.txt"; printf 'dirty-b\n' >> "$LB/b.txt"; printf 'stray\n' > "$LB/stray.txt"

# lane-echo: clean, pushed; scratch targets + census-like mentions — F7, F7b, F8, F11
LE="$FLEET/lane-echo"; mkdir -p "$LE/.scratch" "$LE/souji-shokunin/census/round-1" "$LE/souji-shokunin/tests"; ginit "$LE"
printf 'base\n' > "$LE/base.txt"; gc "$LE" c1 "$LE/base.txt"
printf 'old scratch payload\n' > "$LE/.scratch/alpha-old.out"
printf 'fresh scratch payload\n' > "$LE/.scratch/fresh-recent.out"
printf 'zeta payload\n' > "$LE/.scratch/zeta-scratch.out"
printf 'threshold payload\n' > "$LE/.scratch/threshold-old.out"
# scratch targets stay untracked on purpose: a committed scratch file would
# legitimately earn the pushed receipt and never reach the stale receipt (F7).
printf 'mentions zeta-scratch.out in a lane census fixture\n' > "$LE/souji-shokunin/census/round-1/hit.json"
printf 'mentions zeta-scratch.out in a lane tests fixture\n' > "$LE/souji-shokunin/tests/hit2.json"
origin_for "$LE" lane-echo; set_tip "$LE" "$(G -C "$LE" rev-parse HEAD)" yes
touch -d '2020-01-01 00:00:00' "$LE/.scratch/alpha-old.out" "$LE/.scratch/zeta-scratch.out"
touch -d '30 days ago' "$LE/.scratch/threshold-old.out"

# lane-foxtrot: ledger cases — F6 (match) and F6b (sha mismatch); sources untracked
LF="$FLEET/lane-foxtrot"; mkdir -p "$LF/notes"; ginit "$LF"
printf 'base\n' > "$LF/base.txt"; gc "$LF" c1 "$LF/base.txt"
origin_for "$LF" lane-foxtrot; set_tip "$LF" "$(G -C "$LF" rev-parse HEAD)" yes
printf 'preserved content\n' > "$LF/notes/kept-copy.md"
printf 'preserved content\n' > "$WORK/vault/beta-preserved.md"
printf 'changed after export\n' > "$LF/notes/mismatch.md"
printf 'original before change\n' > "$WORK/vault/mismatch.md"
KEEP_SHA="$(sha256sum "$LF/notes/kept-copy.md" | awk '{print $1}')"
KEEP_V_SHA="$(sha256sum "$WORK/vault/beta-preserved.md" | awk '{print $1}')"
MIS_SRC_SHA="$(sha256sum "$WORK/vault/mismatch.md" | awk '{print $1}')"
MIS_V_SHA="$(sha256sum "$WORK/vault/mismatch.md" | awk '{print $1}')"
LEDGER="$FLEET/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv"
mkdir -p "$(dirname "$LEDGER")"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$LEDGER"
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$LF/notes/kept-copy.md" "$KEEP_SHA" "$WORK/vault/beta-preserved.md" "$KEEP_V_SHA" "2026-10-18" "judge fixture" >> "$LEDGER"
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$LF/notes/mismatch.md" "$MIS_SRC_SHA" "$WORK/vault/mismatch.md" "$MIS_V_SHA" "2026-10-18" "judge fixture (source changed after export)" >> "$LEDGER"

# fleet-level census-like mentions (search-root = fleet reading of D3)
mkdir -p "$FLEET/souji-shokunin/census/round-1" "$FLEET/souji-shokunin/tests"
printf 'mentions zeta-scratch.out in the fleet census fixture\n' > "$FLEET/souji-shokunin/census/round-1/hit.json"
printf 'mentions zeta-scratch.out in the fleet tests fixture\n' > "$FLEET/souji-shokunin/tests/hit.json"

# worktree registrations — F4 (absent dir, unique=0) and F5 (named branch, 1 unpushed)
WO="$FLEET/wtowner-fixture-shokunin"; mkdir -p "$WO"; ginit "$WO"
printf 'wt base\n' > "$WO/base.txt"; gc "$WO" c1 "$WO/base.txt"
origin_for "$WO" wtowner; set_tip "$WO" "$(G -C "$WO" rev-parse HEAD)" yes
WTC1="$(G -C "$WO" rev-parse HEAD)"
G -C "$WO" worktree add -q --detach "$WORK/wt/wt-absent" "$WTC1"
rm -rf "$WORK/wt/wt-absent"
G -C "$WO" worktree add -q -b wt-fixture "$WORK/wt/wt-branch" "$WTC1"
printf 'extra\n' > "$WORK/wt/wt-branch/extra.txt"
G -C "$WORK/wt/wt-branch" add extra.txt
G -C "$WORK/wt/wt-branch" commit -q -m 'unpushed work'

# candidate copy inside the fixture universe (realistic layout: <fleet>/souji-shokunin/tools)
CANDBIN_FIXTURE="$FLEET/souji-shokunin/tools/souji-verify.sh"
mkdir -p "$(dirname "$CANDBIN_FIXTURE")"
cp -- "$CANDIDATE" "$CANDBIN_FIXTURE"
meta fixture_universe "$FLEET"

# ------------------------------------------------------------------- invocation
OUT_TEXT=""; RC=0
run_cand() {
  set +e
  OUT_TEXT="$(cd "$FLEET" && env -i PATH="$PATH" HOME="$HOME" XDG_CONFIG_HOME="$XDG_CONFIG_HOME" TMPDIR="$WORK/tmp" SHOKUNIN_ROOT="$FLEET" LC_ALL=C TERM=dumb timeout -k 5 60 bash "$CANDBIN_FIXTURE" "$@" 2>"$WORK/stderr.log")"
  RC=$?
  set -e
}
find_line() {
  awk -F'\t' -v t="$1" -v r="$2" '$1=="VERDICT" && ($2==t || (r!="" && $2==r)) {print; exit} END{exit 1}' <<<"$OUT_TEXT"
}
f3() { awk -F'\t' '{print $3}' <<<"$1"; }
f4() { awk -F'\t' '{print $4}' <<<"$1"; }
f5() { awk -F'\t' '{print $5}' <<<"$1"; }
nf() { awk -F'\t' '{print NF}' <<<"$1"; }

PRE=()
expect() { # id kind hard|info target want3 want4-alternatives(""=any) evidence-regex(""=skip)
  local id="$1" kind="$2" hard="$3" t="$4" want3="$5" want4="$6" evre="${7:-}"
  run_cand ${PRE[@]+"${PRE[@]}"} "$t"
  local line="" actual="exit=$RC"
  line="$(find_line "$t" "$(rp "$t")" || true)"
  local ok=1 why=""
  if [ -z "$line" ]; then
    ok=0; why="no-VERDICT-line"; actual="$actual; no VERDICT line"
  else
    local g3 g4 g5 gnf
    g3="$(f3 "$line")"; g4="$(f4 "$line")"; g5="$(f5 "$line")"; gnf="$(nf "$line")"
    actual="$actual; fields=$gnf verdict=$g3 receipt=$g4 evidence=$(printf '%.90s' "$g5")"
    [ "$RC" -eq 0 ] || { ok=0; why+="exit=$RC "; }
    [ "$gnf" -ge 5 ] || { ok=0; why+="fields=$gnf "; }
    [ "$g3" = "$want3" ] || { ok=0; why+="verdict=$g3 "; }
    if [ -n "$want4" ]; then
      case " $want4 " in *" $g4 "*) ;; *) ok=0; why+="receipt=$g4 ";; esac
    fi
    if [ -n "$evre" ]; then
      printf '%s' "$g5" | grep -Eq "$evre" || { ok=0; why+="evidence!~/$evre/ "; }
    fi
  fi
  local exp="$want3 ${want4:-(any)}${evre:+ evidence~$evre}"
  if [ "$ok" -eq 1 ]; then
    emit "$id" "$kind" "$exp" "$actual" pass ""
  else
    if [ "$hard" = hard ]; then emit "$id" "$kind" "$exp" "$actual" fail "$why"; hard_fail
    else emit "$id" "$kind" "$exp" "$actual" info "$why"; fi
  fi
}

# ------------------------------------------------------------------ F1..F13
expect F1  file  hard "$LA/docs/keep.txt"                  SAFE     "pushed"
expect F2  file  hard "$LD/local-only.txt"                 NOT-SAFE "pushed-unverifiable none"
expect F3  root  hard "$LB"                                NOT-SAFE "" "unpushed=3.*dirty=[2-3]"
expect F4  worktree hard "$WORK/wt/wt-absent"              SAFE     "metadata-prune"
expect F5  worktree hard "$WORK/wt/wt-branch"              NOT-SAFE "unpushed-branch"
expect F6  file  hard "$LF/notes/kept-copy.md"             SAFE     "moved-to-obsidian"
expect F6b file  hard "$LF/notes/mismatch.md"              NOT-SAFE ""
expect F7  file  hard "$LE/.scratch/alpha-old.out"         SAFE     "stale"
expect F7b file  hard "$LE/.scratch/fresh-recent.out"      NOT-SAFE ""
expect F8  file  hard "$LE/.scratch/zeta-scratch.out"      SAFE     "stale"
expect F9  file  hard "$LC/docs/keep9.txt"                 SAFE     "pushed"
expect F10 file  hard "$LA/app.env"                        NOT-SAFE "secrets-refusal"
expect F11 file  hard "$LE/.scratch/threshold-old.out"     SAFE     "stale"
PRE=(--stale-days 60)
expect F11b file hard "$LE/.scratch/threshold-old.out"     NOT-SAFE ""
PRE=()
expect F12 file  hard "$LA/no-such-file.txt"               NOT-SAFE "unreachable"
expect F13 file  hard ""                                   NOT-SAFE "unreachable"
# F5 guard: owner must actually register the path (fixture sanity, hard)
WT_COUNT="$(G -C "$WO" worktree list --porcelain | grep -c '^worktree ' || true)"
if [ "$WT_COUNT" -ge 3 ]; then
  emit FSAN worktree "3 worktree registrations in owner" "worktree-count=$WT_COUNT" pass ""
else
  emit FSAN worktree "3 worktree registrations in owner" "worktree-count=$WT_COUNT" fail "fixture broken"
  hard_fail
fi

# ------------------------------------------------------------------ CLI cases
# C1: no args -> usage exit 2
run_cand
if [ "$RC" -eq 2 ]; then emit C1 cli "no args -> exit 2" "exit=$RC" pass ""
else emit C1 cli "no args -> exit 2" "exit=$RC" fail "expected exit 2"; hard_fail; fi
# C2: unknown flag -> usage exit 2
run_cand --bogus-flag
if [ "$RC" -eq 2 ]; then emit C2 cli "unknown flag -> exit 2" "exit=$RC" pass ""
else emit C2 cli "unknown flag -> exit 2" "exit=$RC" fail "expected exit 2"; hard_fail; fi
# C3: --json emits machine-readable JSON naming both targets and verdicts.
# Spec names the flag but not a schema: accept a single document or JSON-lines.
run_cand --json "$LA/docs/keep.txt" "$LB"
JSON_CHECK="$(J60_STDOUT="$OUT_TEXT" J60_RC="$RC" python3 - <<'PY' || true
import json, os, sys
raw = os.environ.get('J60_STDOUT', '')
rc = os.environ.get('J60_RC', '')
need = [('lane-alpha/docs/keep.txt', 'SAFE'), ('lane-bravo', 'NOT-SAFE')]
try:
    docs = [json.loads(raw)]
    mode = 'single-document'
except Exception:
    lines = [ln for ln in raw.splitlines() if ln.strip()]
    if not lines:
        print('FAIL empty-output rc=%s' % rc); sys.exit(0)
    try:
        docs = [json.loads(ln) for ln in lines]
        mode = 'jsonl(%d)' % len(docs)
    except Exception as exc:
        print('FAIL invalid-json rc=%s err=%s' % (rc, exc)); sys.exit(0)
s = json.dumps(docs)
missing = [n for n, w in need if n not in s or w not in s]
if rc != '0':
    print('FAIL exit=%s' % rc)
elif missing:
    print('FAIL missing=%s' % ','.join(missing))
else:
    print('OK exit=0 %s, both targets and verdicts present' % mode)
PY
)"
case "$JSON_CHECK" in
  OK*) emit C3 cli "--json machine-readable (doc or jsonl) + both targets" "$JSON_CHECK" pass "";;
  *)   emit C3 cli "--json machine-readable (doc or jsonl) + both targets" "$JSON_CHECK" fail "json contract"; hard_fail;;
esac
# I1 (informational): relative path from the fleet root
PRE=(); OUT_TEXT_SAVE="$OUT_TEXT"
run_cand "lane-alpha/docs/keep.txt"
LREL="$(find_line "lane-alpha/docs/keep.txt" "$(rp "$LA/docs/keep.txt")" || true)"
if [ -n "$LREL" ] && [ "$(f3 "$LREL")" = SAFE ] && [ "$(f4 "$LREL")" = pushed ]; then
  emit I1 file "relative-path SAFE pushed (spec-silent)" "exit=$RC verdict=$(f3 "$LREL") receipt=$(f4 "$LREL")" pass ""
else
  emit I1 file "relative-path SAFE pushed (spec-silent)" "exit=$RC line=$(printf '%.60s' "${LREL:-none}")" info "spec does not mandate relative-path handling"
fi

# --------------------------------------------------------------- rails (hard/info)
# R1 static scan: no fetch/push/reset/rebase/pull/remote-update invocations (non-comment)
STATIC_HITS="$(grep -vE '^[[:space:]]*#' "$CANDIDATE" | grep -nE '(^|[^[:alnum:]_])git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?(fetch|push|reset|rebase|pull)([^[:alnum:]_-]|$)|git[[:space:]]+remote[[:space:]]+update' || true)"
if [ -z "$STATIC_HITS" ]; then
  emit R1 rail "no git fetch/push/reset/rebase/pull in source" "clean" pass ""
else
  emit R1 rail "no git fetch/push/reset/rebase/pull in source" "$(printf '%.120s' "$STATIC_HITS")" fail "static git-write scan"
  hard_fail
fi
# R1b informational: other git-write verbs (legit inside the tool's own mktemp fixtures)
SOFT_HITS="$(grep -vE '^[[:space:]]*#' "$CANDIDATE" | grep -cE '(^|[^[:alnum:]_])git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?(commit|checkout|branch)([^[:alnum:]_-]|$)' || true)"
emit R1b rail "git commit/checkout/branch occurrences (info)" "occurrences=$SOFT_HITS" info "allowed only inside the tool's own mktemp selftest fixtures"
# R2 lane repo must be untouched by the battery (hard)
LANE_DIRTY_NOW="$(git -C "$REPO_ROOT" status --porcelain | grep -v '^??' | wc -l || true)"
LANE_HEAD_NOW="$(git -C "$REPO_ROOT" rev-parse HEAD)"
if [ "$LANE_DIRTY_NOW" -eq 0 ] && [ "$LANE_HEAD_NOW" = "$(git -C "$REPO_ROOT" rev-parse HEAD)" ]; then
  emit R2 rail "lane repo tracked state untouched by battery" "tracked-dirty=$LANE_DIRTY_NOW" pass ""
else
  emit R2 rail "lane repo tracked state untouched by battery" "tracked-dirty=$LANE_DIRTY_NOW" fail "live tree modified"; hard_fail
fi
# R3 informational: .ufo state/watchdog untouched
if [ -d "$UFO_STATE" ]; then
  UFO_AFTER="$(find "$UFO_STATE" -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -1)"
  if [ "$UFO_AFTER" = "${UFO_BEFORE:-}" ]; then emit R3 rail ".ufo/state untouched (info)" "max-mtime unchanged" pass ""
  else emit R3 rail ".ufo/state untouched (info)" "max-mtime changed (concurrent wave writes possible)" info "informational"; fi
else
  emit R3 rail ".ufo/state untouched (info)" "state dir absent" info "not applicable"
fi
meta rail_static "$( [ -z "$STATIC_HITS" ] && echo clean || echo "violation" )"
meta rail_ufo_state "${UFO_AFTER:-${UFO_BEFORE:-n/a}}"

# C5: candidate's own --selftest (spec: exit 0, never touches the live tree)
HEAD_BEFORE_C5="$(git -C "$REPO_ROOT" rev-parse HEAD)"
DIRTY_BEFORE_C5="$(git -C "$REPO_ROOT" status --porcelain | grep -v '^??' | wc -l || true)"
set +e
(cd "$REPO_ROOT" && env -i PATH="$PATH" HOME="$HOME" XDG_CONFIG_HOME="$XDG_CONFIG_HOME" TMPDIR="$WORK/tmp" SHOKUNIN_ROOT="$FLEET" LC_ALL=C TERM=dumb timeout -k 5 240 bash "$CANDIDATE" --selftest >"$WORK/selftest.out" 2>"$WORK/selftest.err")
SRC=$?
set -e
meta candidate_selftest_exit "$SRC"
HEAD_AFTER_C5="$(git -C "$REPO_ROOT" rev-parse HEAD)"
DIRTY_AFTER_C5="$(git -C "$REPO_ROOT" status --porcelain | grep -v '^??' | wc -l || true)"
if [ "$SRC" -eq 0 ] && [ "$HEAD_AFTER_C5" = "$HEAD_BEFORE_C5" ] && [ "$DIRTY_AFTER_C5" -eq "$DIRTY_BEFORE_C5" ]; then
  emit C5 selftest "candidate --selftest exits 0, live tree untouched" "exit=$SRC head-stable dirty=$DIRTY_AFTER_C5" pass ""
else
  emit C5 selftest "candidate --selftest exits 0, live tree untouched" "exit=$SRC head-stable=$([ "$HEAD_AFTER_C5" = "$HEAD_BEFORE_C5" ] && echo yes || echo no) dirty=$DIRTY_AFTER_C5" fail "selftest contract"; hard_fail
fi

if [ "$FAIL_HARD" -eq 0 ]; then exit 0; fi
exit 1
