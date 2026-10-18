#!/usr/bin/env bash
# Seat S32 (test-runner, round 2) — independent black-box verification of
# tools/souji-verify.sh against tools/souji-verify.spec.md.
# Writes tests/results/runner-32.json. Re-runnable, deterministic.
# All fixtures live under mktemp -d; every live surface is read-only.
# Exit: 0 = all counted checks pass, 1 = tool failures, 3 = tool absent.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
TOOL="${SOUJI_VERIFY_TOOL:-$REPO/tools/souji-verify.sh}"
RESULT="${SOUJI_RUNNER_RESULT:-$REPO/tests/results/runner-32.json}"
FLEET="$(cd "$REPO/.." && pwd)"
KOTODAMA="$FLEET/kotodama-shokunin"
STALE_DAYS="${STALE_DAYS:-1}"

WORK="$(mktemp -d /tmp/souji-r32.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT
OUT="$WORK/out"; mkdir -p "$OUT"
CASES="$WORK/cases.tsv"; : >"$CASES"
TRCS="$WORK/trcs.txt"; : >"$TRCS"

GIT="git -c commit.gpgsign=false -c user.name=r32 -c user.email=r32@test \
  -c init.defaultBranch=master -c core.hooksPath=/dev/null -c advice.detachedHead=false"

T0="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

record() { # id name kind cmd expect rc actual pass note
  local id="$1" name="$2" kind="$3" cmd="$4" expect="$5" rc="$6" actual="$7" pass="$8" note="$9"
  actual="${actual//$'\t'/\\t}"; actual="${actual//$'\n'/\\n}"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$id" "$name" "$kind" "$cmd" "$expect" "$rc" "$actual" "$pass" "$note" >>"$CASES"
}

TRC=0
run_at() { # toolpath outfile envkv arg...
  local tp="$1" of="$2" envkv="$3"; shift 3
  set +e
  if [[ -n "$envkv" ]]; then env "$envkv" bash "$tp" "$@" >"$of" 2>&1; else bash "$tp" "$@" >"$of" 2>&1; fi
  TRC=$?
  set -e
  printf '%s\n' "$TRC" >>"$TRCS"
}

verdict_line() { # target outfile -> last matching VERDICT line (or empty)
  local t="$1" of="$2" w
  if [[ "$t" == "@ANY" ]]; then
    awk -F'\t' '$1=="VERDICT"{last=$0;n++} END{if(n)print last}' "$of"
    return 0
  fi
  w="$(realpath -m -- "$t" 2>/dev/null || printf '%s' "$t")"
  awk -F'\t' -v t="$t" -v w="$w" \
    '$1=="VERDICT" && ($2==t || $2==w){last=$0;n++} END{if(n)print last}' "$of"
}

assert_case() { # id name kind cmd expect rce vre rre evre target ofile note
  local id="$1" name="$2" kind="$3" cmd="$4" expect="$5" rce="$6" \
        vre="$7" rre="$8" evre="$9" tgt="${10}" of="${11}" note="${12:-}"
  local vl="" v3="" v4="" v5="" pass="true" summary=""
  if [[ -n "$tgt" ]]; then vl="$(verdict_line "$tgt" "$of")"; fi
  if [[ -n "$vl" ]]; then
    v3="$(printf '%s' "$vl" | cut -f3)"
    v4="$(printf '%s' "$vl" | cut -f4)"
    v5="$(printf '%s' "$vl" | cut -f5- | tr '\t' ' ')"
    summary="$vl"
  else
    summary="(no VERDICT line for target '$tgt')"
  fi
  [[ "$rce" == "*" || "$TRC" == "$rce" ]] || pass="false"
  if [[ -n "$vre" ]]; then [[ "$v3" =~ $vre ]] || pass="false"; fi
  if [[ -n "$rre" ]]; then [[ "$v4" =~ $rre ]] || pass="false"; fi
  if [[ -n "$evre" ]]; then [[ "$v5" =~ $evre ]] || pass="false"; fi
  if [[ -n "$tgt" && -z "$vl" ]]; then pass="false"; fi
  record "$id" "$name" "$kind" "$cmd" "$expect" "$TRC" "$summary" "$pass" "$note"
}

gt() { # id name cmd  — records fixture ground-truth evidence (always pass)
  local id="$1" name="$2" cmd="$3" out="" rc=0
  set +e; out="$(bash -c "$cmd" 2>&1)"; rc=$?; set -e
  record "$id" "$name" "groundtruth" "$cmd" "fixture ground-truth" "$rc" "$out" "true" ""
}

jsonok() { # file -> object|jsonl|unparseable|empty (always exit 0)
  python3 - "$1" <<'PY'
import json, sys
s = open(sys.argv[1], encoding='utf-8', errors='replace').read().strip()
if not s:
    print('empty'); raise SystemExit(0)
try:
    json.loads(s); print('object'); raise SystemExit(0)
except Exception:
    pass
try:
    for ln in s.splitlines():
        if ln.strip():
            json.loads(ln)
    print('jsonl'); raise SystemExit(0)
except Exception:
    pass
print('unparseable')
PY
}

write_result() { # verdict present sha_start seldays t0 t1 tool repo
  python3 - "$CASES" "$RESULT" "$@" <<'PY'
import hashlib, json, os, subprocess, sys

cases_f, result_f, verdict, present, sha_start, seldays, t0, t1, tool_abs, repo_abs = sys.argv[1:11]

def sha256(p):
    try:
        with open(p, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None

def head(p):
    try:
        r = subprocess.run(['git', '-C', p, 'rev-parse', 'HEAD'],
                           capture_output=True, text=True)
        return r.stdout.strip() or None
    except Exception:
        return None

rows = []
for line in open(cases_f, encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) < 9:
        continue
    pid, name, kind, cmd, expect, rc, actual, ps, note = p[:9]
    rows.append({
        'id': pid, 'name': name, 'kind': kind, 'cmd': cmd, 'expect': expect,
        'rc': int(rc) if rc.strip() else None, 'actual': actual,
        'pass': None if kind.startswith('info') else (ps == 'true'),
        'note': note,
    })
counted = [r for r in rows if not r['kind'].startswith('info')]
fails = [r for r in counted if not r['pass']]
out = {
    'seat': 'S32',
    'role': 'test-runner',
    'runner': 'tests/runner-32.sh',
    'runner_sha256': sha256(os.path.join(repo_abs, 'tests', 'runner-32.sh')),
    'tool': 'tools/souji-verify.sh',
    'tool_present': present == 'true',
    'tool_sha256_at_start': sha_start or None,
    'tool_sha256_at_write': sha256(tool_abs) if present == 'true' else None,
    'lane_head': head(repo_abs),
    'started_at': t0,
    'finished_at': t1,
    'stale_days': int(seldays),
    'cases': rows,
    'summary': {
        'counted': len(counted),
        'passed': len(counted) - len(fails),
        'failed': len(fails),
        'informational': len(rows) - len(counted),
    },
    'failed_cases': [r['id'] for r in fails],
    'verdict': verdict,
}
os.makedirs(os.path.dirname(result_f), exist_ok=True)
with open(result_f, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
    f.write('\n')
print(result_f)
PY
}

failcount() { awk -F'\t' '$3 !~ /^info/ && $8=="false"' "$CASES" | wc -l; }

cfile() { # repo relpath content [msg]
  local r="$1" p="$2" c="$3" m="${4:-commit}"
  mkdir -p "$r/$(dirname "$p")"
  printf '%s\n' "$c" >"$r/$p"
  $GIT -C "$r" add -- "$p"
  $GIT -C "$r" commit -q -m "$m"
}

# ---------------------------------------------------------------- presence
if [[ ! -f "$TOOL" ]]; then
  record "T0" "tool-presence" "info" "test -f tools/souji-verify.sh" "present" "1" \
    "tools/souji-verify.sh absent; harness re-runnable" "false" \
    "waited per seat plan; re-run tests/runner-32.sh when the tool lands"
  write_result "TOOL-ABSENT" "false" "" "$STALE_DAYS" "$T0" \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$TOOL" "$REPO" >/dev/null
  echo "runner-32: TOOL-ABSENT (tools/souji-verify.sh not present) -> $RESULT"
  exit 3
fi
SHA_START="$(sha256sum "$TOOL" | cut -d' ' -f1)"
record "A0" "tool-presence" "info" "test -f + sha256sum tools/souji-verify.sh" "present" "0" \
  "present sha256=$SHA_START mode=$(stat -c %A "$TOOL")" "true" ""

# ------------------------------------------------------------- A: syntax/selftest
set +e; bash -n "$TOOL"; ARC=$?; set -e
record "A1" "bash-n-syntax" "cli" "bash -n tools/souji-verify.sh" "exit 0" "$ARC" \
  "bash -n rc=$ARC" "$([[ "$ARC" -eq 0 ]] && echo true || echo false)" ""

refs_b="$(git -C "$REPO" for-each-ref --format='%(refname) %(objectname)')"
ledger_b="$(sha256sum "$REPO/corpus/knowledge/obsidian-ledger.tsv" | cut -d' ' -f1)"
run_at "$TOOL" "$OUT/selftest.txt" "" --selftest
refs_a="$(git -C "$REPO" for-each-ref --format='%(refname) %(objectname)')"
ledger_a="$(sha256sum "$REPO/corpus/knowledge/obsidian-ledger.tsv" | cut -d' ' -f1)"
sha_now="$(sha256sum "$TOOL" | cut -d' ' -f1)"
sel_pass="true"; sel_note=""
[[ "$TRC" == "0" ]] || { sel_pass="false"; sel_note+="selftest rc=$TRC; "; }
[[ "$refs_b" == "$refs_a" ]] || { sel_pass="false"; sel_note+="lane refs changed during selftest; "; }
[[ "$ledger_b" == "$ledger_a" ]] || { sel_pass="false"; sel_note+="ledger changed during selftest; "; }
[[ "$sha_now" == "$SHA_START" ]] || sel_note+="tool file changed during selftest (concurrent writer?); "
record "A2" "selftest-rc0-and-isolation" "cli" "bash tools/souji-verify.sh --selftest" \
  "rc=0 and live lane tree untouched" "$TRC" "$(tail -4 "$OUT/selftest.txt" | tr '\n' '|')" \
  "$sel_pass" "$sel_note"

# ------------------------------------------------------------- C: CLI contract
run_at "$TOOL" "$OUT/c_bogus.txt" "" --bogus-flag
assert_case "C1" "usage-unknown-flag" "cli" "souji-verify.sh --bogus-flag" "rc=2" "2" "" "" "" "" "$OUT/c_bogus.txt" ""
run_at "$TOOL" "$OUT/c_noargs.txt" ""
assert_case "C2" "usage-no-args" "cli" "souji-verify.sh (no args)" "rc=2" "2" "" "" "" "" "$OUT/c_noargs.txt" ""

MISS="/tmp/souji-r32-missing-target-296f"
run_at "$TOOL" "$OUT/c_missing.txt" "" "$MISS"
assert_case "C3" "missing-target" "cli" "souji-verify.sh <nonexistent>" "rc=0 NOT-SAFE unreachable" \
  "0" "^NOT-SAFE$" "^unreachable$" "" "$MISS" "$OUT/c_missing.txt" ""
run_at "$TOOL" "$OUT/c_empty.txt" "" ""
assert_case "C4" "empty-target" "cli" "souji-verify.sh ''" "rc=0 NOT-SAFE unreachable" \
  "0" "^NOT-SAFE$" "^unreachable$" "" "@ANY" "$OUT/c_empty.txt" ""

run_at "$TOOL" "$OUT/c_sd.txt" "" --stale-days
assert_case "C5" "usage-stale-days-missing-value" "cli" "souji-verify.sh --stale-days" "rc=2" "2" "" "" "" "" "$OUT/c_sd.txt" ""
run_at "$TOOL" "$OUT/c_sd2.txt" "" --stale-days abc "$MISS"
assert_case "C6" "info-stale-days-nonnumeric" "info:cli" "souji-verify.sh --stale-days abc <missing>" \
  "usage error preferred" "*" "" "" "" "" "$OUT/c_sd2.txt" "informational: spec silent on validation"

run_at "$TOOL" "$OUT/c_json.txt" "" --json "$MISS"
jok="$(jsonok "$OUT/c_json.txt")"
jpass="false"; [[ "$TRC" == "0" && ( "$jok" == "object" || "$jok" == "jsonl" ) ]] && jpass="true"
record "C7" "json-flag-parseable" "cli" "souji-verify.sh --json <missing>" \
  "rc=0, stdout parses as JSON or JSONL" "$TRC" \
  "parse=$jok first=$(head -1 "$OUT/c_json.txt")" "$jpass" "schema unspecified; parse-only check"

# ------------------------------------------------------------- D: fixtures
# F1: file introduced pre-default-tip, ancestor of origin/master -> SAFE(pushed)
F1="$WORK/f1"; R1="$F1/repo"
$GIT init -q "$R1"
cfile "$R1" kept.txt "kept-content" "add kept"
S1="$($GIT -C "$R1" rev-parse master)"
$GIT -C "$R1" update-ref refs/remotes/origin/master "$S1"
$GIT -C "$R1" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
gt "G1a" "F1 origin/HEAD resolves" "git -C '$R1' symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's@^origin/@@'"
gt "G1b" "F1 introducing commit ancestor check" \
  "git -C '$R1' merge-base --is-ancestor \$(git -C '$R1' log --diff-filter=A --format=%H -1 -- kept.txt) refs/remotes/origin/master && echo ANCESTOR:true"
pushd "$F1" >/dev/null; run_at "$TOOL" "$OUT/f1.txt" "SHOKUNIN_ROOT=$F1" "$R1/kept.txt"; popd >/dev/null
assert_case "F1" "pushed-ancestor (origin/HEAD)" "fixture" "souji-verify.sh <f1/repo/kept.txt>" \
  "rc=0 SAFE(pushed)" "0" "^SAFE$" "^pushed$" "" "$R1/kept.txt" "$OUT/f1.txt" ""
nf="$(verdict_line "$R1/kept.txt" "$OUT/f1.txt" | awk -F'\t' '{print NF}')"
record "F1fmt" "verdict-line-field-count" "info" "awk -F'\\t' NF" "5" "" "nf=$nf" "true" \
  "VERDICT<TAB>path<TAB>verdict<TAB>receipt<TAB>evidence"

# F1 determinism: second run identical line
pushd "$F1" >/dev/null; run_at "$TOOL" "$OUT/f1b.txt" "SHOKUNIN_ROOT=$F1" "$R1/kept.txt"; popd >/dev/null
det_a="$(verdict_line "$R1/kept.txt" "$OUT/f1.txt")"
det_b="$(verdict_line "$R1/kept.txt" "$OUT/f1b.txt")"
det_pass="false"; [[ -n "$det_a" && "$det_a" == "$det_b" ]] && det_pass="true"
record "X2" "determinism-f1-twice" "cli" "souji-verify.sh <f1 target> x2" "identical verdict lines" \
  "$TRC" "$det_b" "$det_pass" ""

# F9: origin/HEAD missing, single origin branch ref -> resolves, SAFE(pushed)
F9="$WORK/f9"; R9="$F9/repo"
$GIT init -q "$R9"
cfile "$R9" kept.txt "kept-content" "add kept"
S9="$($GIT -C "$R9" rev-parse master)"
$GIT -C "$R9" update-ref refs/remotes/origin/master "$S9"
gt "G9a" "F9 origin ref count" "git -C '$R9' for-each-ref refs/remotes/origin --format='%(refname)' | wc -l"
pushd "$F9" >/dev/null; run_at "$TOOL" "$OUT/f9.txt" "SHOKUNIN_ROOT=$F9" "$R9/kept.txt"; popd >/dev/null
assert_case "F9" "pushed-single-origin-ref (no origin/HEAD)" "fixture" "souji-verify.sh <f9/repo/kept.txt>" \
  "rc=0 SAFE(pushed) via single origin ref fallback" "0" "^SAFE$" "^pushed$" "" "$R9/kept.txt" "$OUT/f9.txt" ""

# F2: introducing commit is local-only -> NOT-SAFE(pushed-unverifiable|none)
F2="$WORK/f2"; R2="$F2/repo"
$GIT init -q "$R2"
cfile "$R2" base.txt "base" "base"
SB2="$($GIT -C "$R2" rev-parse master)"
$GIT -C "$R2" update-ref refs/remotes/origin/master "$SB2"
cfile "$R2" local-only.txt "x" "local-only add"
gt "G2a" "F2 local-only not ancestor" \
  "git -C '$R2' merge-base --is-ancestor \$(git -C '$R2' log --diff-filter=A --format=%H -1 -- local-only.txt) refs/remotes/origin/master; echo rc=\$?"
pushd "$F2" >/dev/null; run_at "$TOOL" "$OUT/f2.txt" "SHOKUNIN_ROOT=$F2" "$R2/local-only.txt"; popd >/dev/null
assert_case "F2" "pushed-unverifiable-local-commit" "fixture" "souji-verify.sh <f2/repo/local-only.txt>" \
  "rc=0 NOT-SAFE(pushed-unverifiable|none)" "0" "^NOT-SAFE$" "^(pushed-unverifiable|none)$" "" "$R2/local-only.txt" "$OUT/f2.txt" ""

# F3: kotodama-shaped repo root — unpushed commits + dirty tree -> NOT-SAFE
F3="$WORK/f3"; R3="$F3/fake-shokunin"
$GIT init -q "$R3"
cfile "$R3" base.txt "base" "base"
SB3="$($GIT -C "$R3" rev-parse master)"
$GIT -C "$R3" update-ref refs/remotes/origin/master "$SB3"
cfile "$R3" extra.txt "e" "unpushed add"
printf 'edited\n' >>"$R3/base.txt"
printf 'u\n' >"$R3/untracked.bin"
gt "G3a" "F3 unpushed commits" "git -C '$R3' log --branches --not --remotes --oneline | wc -l"
gt "G3b" "F3 dirty entries" "git -C '$R3' status --porcelain | wc -l"
pushd "$F3" >/dev/null; run_at "$TOOL" "$OUT/f3.txt" "SHOKUNIN_ROOT=$F3" "$R3"; popd >/dev/null
assert_case "F3" "kotodama-shape repo-root" "fixture" "souji-verify.sh <f3/fake-shokunin>" \
  "rc=0 NOT-SAFE, evidence unpushed=N dirty=M (N,M>0)" "0" "^NOT-SAFE$" "" \
  "unpushed=[1-9][0-9]* dirty=[1-9][0-9]*" "$R3" "$OUT/f3.txt" ""

# F4: worktree registration, dir absent, unique=0 -> SAFE(metadata-prune)
F4="$WORK/f4"; FX4="$F4/fleet"; R4="$FX4/fake-shokunin"
$GIT init -q "$R4"
cfile "$R4" base.txt "base" "base"
S4="$($GIT -C "$R4" rev-parse master)"
$GIT -C "$R4" update-ref refs/remotes/origin/master "$S4"
$GIT -C "$R4" update-ref refs/heads/wt-a "$S4"
$GIT -C "$R4" worktree add -q "$F4/wt-a" wt-a
rm -rf "$F4/wt-a"
gt "G4a" "F4 worktree registrations" "git -C '$R4' worktree list --porcelain | grep -c '^worktree '"
gt "G4b" "F4 worktree unique commits vs --all" "git -C '$R4' log --oneline '$S4' --not --all | wc -l"
pushd "$F4" >/dev/null
run_at "$TOOL" "$OUT/f4.txt" "SHOKUNIN_ROOT=$FX4" "$F4/wt-a"
popd >/dev/null
assert_case "F4" "worktree-absent-unique0" "fixture" "souji-verify.sh <f4/wt-a> (dir deleted)" \
  "rc=0 SAFE(metadata-prune)" "0" "^SAFE$" "^metadata-prune$" "" "$F4/wt-a" "$OUT/f4.txt" ""

# F5: worktree registration, named branch, 1 unpushed commit -> NOT-SAFE(unpushed-branch)
F5="$WORK/f5"; FX5="$F5/fleet"; R5="$FX5/fake-shokunin"
$GIT init -q "$R5"
cfile "$R5" base.txt "base" "base"
SB5="$($GIT -C "$R5" rev-parse master)"
$GIT -C "$R5" update-ref refs/remotes/origin/master "$SB5"
cfile "$R5" feat.txt "f" "feat commit"
C5="$($GIT -C "$R5" rev-parse master)"
$GIT -C "$R5" update-ref refs/heads/wt-b "$C5"
$GIT -C "$R5" worktree add -q "$F5/wt-b" wt-b
gt "G5a" "F5 wt-b unpushed commits" "git -C '$R5' log --oneline wt-b --not --remotes | wc -l"
pushd "$F5" >/dev/null
run_at "$TOOL" "$OUT/f5.txt" "SHOKUNIN_ROOT=$FX5" "$F5/wt-b"
popd >/dev/null
assert_case "F5" "worktree-unpushed-branch" "fixture" "souji-verify.sh <f5/wt-b> (dir present)" \
  "rc=0 NOT-SAFE(unpushed-branch)" "0" "^NOT-SAFE$" "^unpushed-branch$" "" "$F5/wt-b" "$OUT/f5.txt" ""

# F6: ledger-matched file -> SAFE(moved-to-obsidian); run tool copy beside fixture ledger
F6="$WORK/f6"; L6="$F6/souji-shokunin"
mkdir -p "$L6/tools" "$L6/corpus/knowledge" "$F6/src" "$F6/vault"
cp "$TOOL" "$L6/tools/souji-verify.sh"
printf 'ob-artifact-bytes\n' >"$F6/src/artifact.bin"
cp "$F6/src/artifact.bin" "$F6/vault/artifact.bin"
SS="$(sha256sum "$F6/src/artifact.bin" | cut -d' ' -f1)"
VS="$(sha256sum "$F6/vault/artifact.bin" | cut -d' ' -f1)"
{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$F6/src/artifact.bin" "$SS" "$F6/vault/artifact.bin" "$VS" "2026-10-18" "runner-32"
} >"$L6/corpus/knowledge/obsidian-ledger.tsv"
gt "G6a" "F6 sha equality" "echo s=\$(sha256sum '$F6/src/artifact.bin' | cut -d' ' -f1) v=\$(sha256sum '$F6/vault/artifact.bin' | cut -d' ' -f1)"
pushd "$F6" >/dev/null
run_at "$L6/tools/souji-verify.sh" "$OUT/f6.txt" "SHOKUNIN_ROOT=$F6" "$F6/src/artifact.bin"
popd >/dev/null
assert_case "F6" "ledger-match" "fixture" "souji-verify.sh(copy) <f6/src/artifact.bin>" \
  "rc=0 SAFE(moved-to-obsidian)" "0" "^SAFE$" "^moved-to-obsidian$" "" "$F6/src/artifact.bin" "$OUT/f6.txt" \
  "tool copy sha256=$(sha256sum "$L6/tools/souji-verify.sh" | cut -d' ' -f1)"

# F6b (info): ledger row with relative source_path
{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "src/artifact.bin" "$SS" "$F6/vault/artifact.bin" "$VS" "2026-10-18" "relative-path variant"
} >"$L6/corpus/knowledge/obsidian-ledger.tsv"
pushd "$F6" >/dev/null
run_at "$L6/tools/souji-verify.sh" "$OUT/f6b.txt" "SHOKUNIN_ROOT=$F6" "$F6/src/artifact.bin"
popd >/dev/null
assert_case "F6b" "info-ledger-relative-source-path" "info:fixture" "souji-verify.sh(copy) <f6/src/artifact.bin>" \
  "relative vs absolute source_path convention" "*" "" "" "" "$F6/src/artifact.bin" "$OUT/f6b.txt" \
  "ledger convention not fixed by spec; informational"

# F7: scratch file, no refs, old mtime -> SAFE(stale)
F7="$WORK/f7"; FX7="$F7/fleet"; R7="$FX7/fake-shokunin"
$GIT init -q "$R7"
cfile "$R7" base.txt "base" "base"
SB7="$($GIT -C "$R7" rev-parse master)"
$GIT -C "$R7" update-ref refs/remotes/origin/master "$SB7"
mkdir -p "$R7/.scratch"
printf 'throwaway bytes\n' >"$R7/.scratch/old32.out"
touch -d '3 days ago' "$R7/.scratch/old32.out"
gt "G7a" "F7 content references in owning repo" "rg -l --no-ignore -F old32.out '$R7' -g '!.git' | wc -l"
gt "G7b" "F7 mtime older than 1 day" "find '$R7/.scratch/old32.out' -mtime +1 | wc -l"
pushd "$F7" >/dev/null
run_at "$TOOL" "$OUT/f7.txt" "SHOKUNIN_ROOT=$FX7" "$R7/.scratch/old32.out"
popd >/dev/null
assert_case "F7" "stale-scratch-no-refs" "fixture" "souji-verify.sh <f7/.../.scratch/old32.out>" \
  "rc=0 SAFE(stale)" "0" "^SAFE$" "^stale$" "" "$R7/.scratch/old32.out" "$OUT/f7.txt" ""

# F8: scratch file, basename appears in census-like dir -> still SAFE(stale) (D3)
F8="$WORK/f8"; FX8="$F8/fleet"; R8="$FX8/fake-shokunin"
$GIT init -q "$R8"
cfile "$R8" base.txt "base" "base"
SB8="$($GIT -C "$R8" rev-parse master)"
$GIT -C "$R8" update-ref refs/remotes/origin/master "$SB8"
mkdir -p "$R8/.scratch"
printf 'throwaway\n' >"$R8/.scratch/launch-s32-tmp.json"
touch -d '3 days ago' "$R8/.scratch/launch-s32-tmp.json"
mkdir -p "$FX8/souji-shokunin/census/round-2"
printf '{"note":"sweep mention: launch-s32-tmp.json"}\n' >"$FX8/souji-shokunin/census/round-2/seat-99.json"
gt "G8a" "F8 census-like references exist" "rg -l --no-ignore -F launch-s32-tmp.json '$FX8' -g '!.git' | wc -l"
pushd "$F8" >/dev/null
run_at "$TOOL" "$OUT/f8.txt" "SHOKUNIN_ROOT=$FX8" "$R8/.scratch/launch-s32-tmp.json"
popd >/dev/null
assert_case "F8" "stale-census-pollution (D3)" "fixture" "souji-verify.sh <f8/.../.scratch/launch-s32-tmp.json>" \
  "rc=0 SAFE(stale) despite census mention" "0" "^SAFE$" "^stale$" "" "$R8/.scratch/launch-s32-tmp.json" "$OUT/f8.txt" ""

# F10: secrets-shaped basename and .env path component -> NOT-SAFE(secrets-refusal)
mkdir -p "$WORK/secrets.env"; printf 'DECOY-NOT-A-SECRET\n' >"$WORK/secrets.env/inner.txt"
printf 'DECOY-NOT-A-SECRET\n' >"$WORK/foo.env"
run_at "$TOOL" "$OUT/f10a.txt" "" "$WORK/foo.env"
assert_case "F10a" "secrets-basename-refusal" "fixture" "souji-verify.sh <foo.env>" \
  "rc=0 NOT-SAFE(secrets-refusal)" "0" "^NOT-SAFE$" "^secrets-refusal$" "" "$WORK/foo.env" "$OUT/f10a.txt" ""
run_at "$TOOL" "$OUT/f10b.txt" "" "$WORK/secrets.env/inner.txt"
assert_case "F10b" "secrets-path-component-divergence" "info:fixture" "souji-verify.sh <secrets.env/inner.txt>" \
  "rc=0 NOT-SAFE(secrets-refusal) [strict reading]" "0" "^NOT-SAFE$" "^secrets-refusal$" "" "$WORK/secrets.env/inner.txt" "$OUT/f10b.txt" \
  "spec-ambiguous: rail text scopes refusal to basenames; F10 says 'path containing .env'; divergence recorded, not counted; NOT-SAFE either way (no false-SAFE)"

# ------------------------------------------------------------- L: live surfaces (read-only)
if [[ -d "$KOTODAMA" ]]; then
  pushd "$FLEET" >/dev/null; run_at "$TOOL" "$OUT/l1.txt" "" "$KOTODAMA"; popd >/dev/null
  assert_case "L1" "live-gate-kotodama" "live" "souji-verify.sh <kotodama-shokunin>" \
    "rc=0 NOT-SAFE with unpushed>0 (dirty>=0)" "0" "^NOT-SAFE$" "" \
    "unpushed=[1-9][0-9]* dirty=[0-9]+" "$KOTODAMA" "$OUT/l1.txt" \
    "round-2 named gate (MINT.md): must be NOT-SAFE on kotodama unpushed state"
  gt "GL1" "L1 ground-truth kotodama counts" \
    "echo unpushed=\$(git -C '$KOTODAMA' log --branches --not --remotes --oneline | wc -l) dirty=\$(git -C '$KOTODAMA' status --porcelain | wc -l)"
else
  record "L1" "live-gate-kotodama" "info:live" "test -d kotodama-shokunin" "present" "1" "absent" "false" ""
fi

L3=""
for cand in "$FLEET/prior-owners.json" "$FLEET"/launch-*.json "$FLEET/interactive-wall.png"; do
  [[ -f "$cand" ]] && { L3="$cand"; break; }
done
if [[ -n "$L3" ]]; then
  rel="${L3#"$FLEET"/}"
  l3anc=1
  set +e
  bash -c "cd '$FLEET' && sha=\$(git log --diff-filter=A --format=%H -1 -- '$rel') && git merge-base --is-ancestor \"\$sha\" refs/remotes/origin/master" >/dev/null 2>&1
  l3anc=$?
  set -e
  gt "GL3" "L3 ground-truth ancestry vs origin/master" \
    "cd '$FLEET' && sha=\$(git log --diff-filter=A --format=%H -1 -- '$rel') && git merge-base --is-ancestor \"\$sha\" refs/remotes/origin/master; echo rc=\$?"
  if [[ "$l3anc" == "0" ]]; then
    pushd "$FLEET" >/dev/null; run_at "$TOOL" "$OUT/l3.txt" "" "$L3"; popd >/dev/null
    assert_case "L3" "live-pushed-file" "live" "souji-verify.sh <$rel>" \
      "rc=0 SAFE(pushed) — round-1 verified ancestor" "0" "^SAFE$" "^pushed$" "" "$L3" "$OUT/l3.txt" ""
  else
    pushd "$FLEET" >/dev/null; run_at "$TOOL" "$OUT/l3.txt" "" "$L3"; popd >/dev/null
    record "L3" "live-pushed-file" "info:live" "souji-verify.sh <$rel>" \
      "precondition failed (not ancestor of origin/master)" "$TRC" \
      "$(verdict_line "$L3" "$OUT/l3.txt")" "false" "ground-truth says not pushed; tool not asserted"
  fi
else
  record "L3" "live-pushed-file" "info:live" "fleet-root candidate search" "candidate exists" "1" "none found" "false" ""
fi

# ------------------------------------------------------------- X: exit-code domain
dom_pass="$(awk '$1 !~ /^[012]$/ {f=1} END {print (f ? "false" : "true")}' "$TRCS")"
record "X1" "exit-code-domain" "cli" "all tool runs collected" "rc in {0,1,2} only" "0" \
  "observed=$(sort -u "$TRCS" | tr '\n' ' ')" "$dom_pass" ""

# ------------------------------------------------------------- result
N="$(failcount)"
# groundtruth rows are evidence, but a failing groundtruth means my fixture is wrong -> count them
gtfail="$(awk -F'\t' '$3=="groundtruth" && $6!="0"' "$CASES" | wc -l)"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if (( N > 0 )); then
  VERDICT="TOOL-FAIL"; RC=1
else
  VERDICT="TOOL-PASS"; RC=0
fi
write_result "$VERDICT" "true" "$SHA_START" "$STALE_DAYS" "$T0" "$NOW" "$TOOL" "$REPO" >/dev/null
echo "runner-32: $VERDICT counted=$(( $(grep -c . "$CASES") )) failed=$N gtfail_nonzero_rc=$gtfail"
echo "runner-32: result -> $RESULT (tool sha256=$SHA_START)"
exit "$RC"
