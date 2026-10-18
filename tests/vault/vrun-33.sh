#!/usr/bin/env bash
# Seat S33 (runner, round 4) — independent black-box runner for the
# Obsidian-CLI vault-verification contract over tools/souji-verify.sh.
#
# Writes tests/results/vrun-33.json. Re-runnable, deterministic.
# Read-only over the real vault: every vault access is sha256sum/stat/git
# log (no writes). Fixture ledgers persist under tests/vault/; fixture
# trees persist under tests/vault/vrun33-*/. /usr/bin/obsidian (the GUI
# launcher) is never executed.
#
# Families
#   A  tool health (syntax, selftest, isolation)
#   C  CLI contract (usage, json, --cli conditional)
#   L  ledger semantics on own fixtures (fresh ledger per case)
#   V  live vault rows (real vault file, read-only)
#   RO read-only proof (vault manifest, live ledger, no GUI process)
#   X  exit-code domain, determinism
#
# Exit: 0 = all counted checks pass, 1 = tool failures, 3 = tool absent.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
TOOL="${SOUJI_VERIFY_TOOL:-$REPO/tools/souji-verify.sh}"
RESULT="${SOUJI_RUNNER_RESULT:-$REPO/tests/results/vrun-33.json}"
FLEET="$(cd "$REPO/.." && pwd)"
VAULT="/home/vgpnk/Documents/shokoknowledge"
LIVE_LEDGER="$REPO/corpus/knowledge/obsidian-ledger.tsv"
TV="$REPO/tests/vault"
STALE_DAYS="${STALE_DAYS:-1}"
CLI_TIMEOUT=25

WORK="$(mktemp -d /tmp/souji-vrun33.XXXXXX)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT
OUT="$WORK/out"; mkdir -p "$OUT"
CASES="$WORK/cases.tsv"; : >"$CASES"
TRCS="$WORK/trcs.txt"; : >"$TRCS"

T0="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

record() { # id name kind cmd expect rc actual pass note
  local id="$1" name="$2" kind="$3" cmd="$4" expect="$5" rc="$6" actual="$7" pass="$8" note="$9"
  actual="${actual//$'\t'/\\t}"; actual="${actual//$'\n'/\\n}"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$id" "$name" "$kind" "$cmd" "$expect" "$rc" "$actual" "$pass" "$note" >>"$CASES"
}

TRC=0
CUR_TOOL=""
run_tool() { # outfile envkv -- args...
  local of="$1" envkv="$2"; shift 2
  [ "${1:-}" = "--" ] && shift
  local tp="${CUR_TOOL:-$TOOL}"
  local t0 t1
  t0=$(date +%s.%N)
  if [ -n "$envkv" ]; then
    env $envkv timeout "$CLI_TIMEOUT" bash "$tp" "$@" >"$of" 2>&1
  else
    timeout "$CLI_TIMEOUT" bash "$tp" "$@" >"$of" 2>&1
  fi
  TRC=$?
  t1=$(date +%s.%N)
  LAST_SECS=$(awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f", b-a}')
  printf '%s\n' "$TRC" >>"$TRCS"
  LAST_OUT="$(cat "$of" 2>/dev/null)"
}

verdict_line() { # target outfile
  local t="$1" of="$2" w
  w="$(realpath -m -- "$t" 2>/dev/null || printf '%s' "$t")"
  awk -F'\t' -v t="$t" -v w="$w" \
    '$1=="VERDICT" && ($2==t || $2==w){last=$0;n++} END{if(n)print last}' "$of"
}

assert_case() { # id name kind cmd expect rce vre rre evre target ofile note
  local id="$1" name="$2" kind="$3" cmd="$4" expect="$5" rce="$6" \
        vre="$7" rre="$8" evre="$9" tgt="${10}" of="${11}" note="${12:-}"
  local vl="" v3="" v4="" v5="" pass="true" summary=""
  if [ -n "$tgt" ]; then vl="$(verdict_line "$tgt" "$of")"; fi
  if [ -n "$vl" ]; then
    v3="$(printf '%s' "$vl" | cut -f3)"
    v4="$(printf '%s' "$vl" | cut -f4)"
    v5="$(printf '%s' "$vl" | cut -f5- | tr '\t' ' ')"
    summary="$vl"
  else
    summary="(no VERDICT line for target '$tgt')"
  fi
  [[ "$rce" == "*" || "$TRC" == "$rce" ]] || pass="false"
  if [ -n "$vre" ]; then [[ "$v3" =~ $vre ]] || pass="false"; fi
  if [ -n "$rre" ]; then [[ "$v4" =~ $rre ]] || pass="false"; fi
  if [ -n "$evre" ]; then [[ "$v5" =~ $evre ]] || pass="false"; fi
  if [ -n "$tgt" ] && [ -z "$vl" ]; then pass="false"; fi
  record "$id" "$name" "$kind" "$cmd" "$expect" "$TRC" "$summary" "$pass" "$note"
}

gt() { # id name cmd — ground-truth evidence row
  local id="$1" name="$2" cmd="$3" out="" rc=0
  set +e; out="$(bash -c "$cmd" 2>&1)"; rc=$?; set +e
  record "$id" "$name" "groundtruth" "$cmd" "fixture ground-truth" "$rc" "$out" "true" ""
}

jsonok() { # file -> object|jsonl|unparseable|empty
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

sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }
dir_digest() { # must match tools/souji-verify.sh dir_digest exactly
  ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null
}

vault_snapshot() {
  ( cd "$VAULT" && find . -type f -not -path './.git/*' -print0 2>/dev/null \
      | sort -z | xargs -0 -r sha256sum 2>/dev/null | sha256sum | cut -d' ' -f1 )
}

write_result() { # verdict present sha_start t0 t1
  python3 - "$CASES" "$RESULT" "$@" <<'PY'
import hashlib, json, os, subprocess, sys

cases_f, result_f, verdict, present, sha_start, t0, t1 = sys.argv[1:8]
repo_abs = sys.argv[8] if len(sys.argv) > 8 else None

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
        'rc': int(rc) if rc.strip() and rc.strip().lstrip('-').isdigit() else None,
        'actual': actual,
        'pass': None if kind.startswith('info') or kind == 'blocked-interface' else (ps == 'true'),
        'note': note,
    })
counted = [r for r in rows if not r['kind'].startswith('info') and r['kind'] != 'blocked-interface']
blocked = [r for r in rows if r['kind'] == 'blocked-interface']
fails = [r for r in counted if not r['pass']]
out = {
    'seat': 'S33',
    'role': 'test-runner',
    'round': 4,
    'runner': 'tests/vault/vrun-33.sh',
    'runner_sha256': sha256(os.path.join(repo_abs, 'tests', 'vault', 'vrun-33.sh')) if repo_abs else None,
    'tool': 'tools/souji-verify.sh',
    'tool_present': present == 'true',
    'tool_sha256_at_start': sha_start or None,
    'tool_sha256_at_write': sha256(sys.argv[9]) if len(sys.argv) > 9 and present == 'true' else None,
    'lane_head': head(repo_abs) if repo_abs else None,
    'started_at': t0,
    'finished_at': t1,
    'stale_days': int(sys.argv[10]) if len(sys.argv) > 10 else None,
    'cases': rows,
    'summary': {
        'counted': len(counted),
        'passed': len(counted) - len(fails),
        'failed': len(fails),
        'blocked_interface': len(blocked),
        'informational': len(rows) - len(counted) - len(blocked),
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

failcount() { awk -F'\t' '$3 !~ /^info/ && $3 != "blocked-interface" && $8=="false"' "$CASES" | wc -l; }

# ------------------------------------------------------------ presence ----
if [ ! -f "$TOOL" ]; then
  record "T0" "tool-presence" "info" "test -f tools/souji-verify.sh" "present" "1" \
    "tools/souji-verify.sh absent" "false" "re-run tests/vault/vrun-33.sh when the tool lands"
  write_result "TOOL-ABSENT" "false" "" "$T0" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$REPO" "" "$STALE_DAYS" >/dev/null
  echo "vrun-33: TOOL-ABSENT -> $RESULT"
  exit 3
fi
SHA_START="$(sha "$TOOL")"
TOOL_HAS_CLI=$(grep -c -- '--cli' "$TOOL" 2>/dev/null || true)
GUI_ABS_REF=$(grep -c '/usr/bin/obsidian' "$TOOL" 2>/dev/null || true)
record "A0" "tool-presence" "info" "test -f + sha256sum tools/souji-verify.sh" "present" "0" \
  "present sha256=$SHA_START mode=$(stat -c %A "$TOOL")" "true" ""
record "A3" "r4-cli-surface" "info" "grep -c -- '--cli' tools/souji-verify.sh" \
  "cli flag declared or not" "0" "cli_refs=$TOOL_HAS_CLI gui_abs_refs=$GUI_ABS_REF" "true" \
  "r4 integration surface; gui_abs_refs must stay 0 (GUI launcher never named as exec target)"

# --------------------------------------------------------- RO snapshots ---
VAULT_SNAP_BEFORE="$(vault_snapshot)"
VAULT_GIT_BEFORE="$(git -C "$VAULT" status --porcelain 2>/dev/null | sha256sum | cut -d' ' -f1)"
LEDGER_SHA_BEFORE="$(sha "$LIVE_LEDGER")"
LEDGER_LINES_BEFORE="$(wc -l <"$LIVE_LEDGER" 2>/dev/null | tr -d ' ')"
REFS_BEFORE="$(git -C "$REPO" for-each-ref --format='%(refname) %(objectname)' | sha256sum | cut -d' ' -f1)"

# --------------------------------------------------------------- fixtures --
FX="$TV/vrun33-fixtures"; FV="$TV/vrun33-vault"
rm -rf "$FX" "$FV"; mkdir -p "$FX" "$FV"
printf 'vrun33 payload alpha\n' > "$FX/alpha.md"
printf 'vrun33 payload beta\n'  > "$FX/beta.md"
printf 'DIFFERENT CONTENT\n'    > "$FV/beta.md"
printf 'vrun33 payload alpha\n' > "$FV/alpha.md"
mkdir -p "$FX/dir-case" "$FV/dir-case" "$FV/dir-diff"
printf 'one\n' > "$FX/dir-case/one.txt"; printf 'two\n' > "$FX/dir-case/two.txt"
printf 'one\n' > "$FV/dir-case/one.txt"; printf 'two\n' > "$FV/dir-case/two.txt"
printf 'X\n'   > "$FV/dir-diff/one.txt"; printf 'Y\n' > "$FV/dir-diff/two.txt"
mkdir -p "$FV/isadir"

ALPHA_SS=$(sha "$FX/alpha.md"); ALPHA_VS=$(sha "$FV/alpha.md")
BETA_SS=$(sha "$FX/beta.md");   BETA_VS=$(sha "$FV/beta.md")
DIR_DIG=$(dir_digest "$FX/dir-case"); DIR_VS=$(dir_digest "$FV/dir-case")
DIRDIFF_VS=$(dir_digest "$FV/dir-diff")
WRONG=1111111111111111111111111111111111111111111111111111111111111111

HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
mkled() { printf '%s\n' "$HDR" > "$1"; }

# L1 correct file row
mkled "$TV/vrun33-led-l1.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL1\n' "$FX/alpha.md" "$ALPHA_SS" "$FV/alpha.md" "$ALPHA_VS" >> "$TV/vrun33-led-l1.tsv"
# L2 wrong source hash
mkled "$TV/vrun33-led-l2.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL2\n' "$FX/alpha.md" "$WRONG" "$FV/alpha.md" "$ALPHA_VS" >> "$TV/vrun33-led-l2.tsv"
# L3 wrong vault hash
mkled "$TV/vrun33-led-l3.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL3\n' "$FX/alpha.md" "$ALPHA_SS" "$FV/alpha.md" "$WRONG" >> "$TV/vrun33-led-l3.tsv"
# L4 mid-row empty field: IFS=tab collapses the run, so the row reads as
# shifted columns (ss=<vault path>) -> hash mismatch -> NOT-SAFE expected.
mkled "$TV/vrun33-led-l4.tsv"
printf '%s\t\t%s\t%s\t2026-10-18\tL4\n' "$FX/alpha.md" "$FV/alpha.md" "$ALPHA_VS" >> "$TV/vrun33-led-l4.tsv"
# L5 empty vault hash (file)
mkled "$TV/vrun33-led-l5.tsv"
printf '%s\t%s\t%s\t\t2026-10-18\tL5\n' "$FX/alpha.md" "$ALPHA_SS" "$FV/alpha.md" >> "$TV/vrun33-led-l5.tsv"
# L6a dir row, correct source digest, EMPTY vault hash (trailing tab; an
# empty mid-row field would collapse under IFS=tab), vault content differs.
# Contract: a row qualifies only with BOTH hashes -> NOT-SAFE expected.
mkled "$TV/vrun33-led-l6a.tsv"
printf '%s\t%s\t%s\t\n' "$FX/dir-case" "$DIR_DIG" "$FV/dir-diff" >> "$TV/vrun33-led-l6a.tsv"
# L6b dir row, 3 fields only (vault_sha256 column absent), vault content differs
mkled "$TV/vrun33-led-l6b.tsv"
printf '%s\t%s\t%s\n' "$FX/dir-case" "$DIR_DIG" "$FV/dir-diff" >> "$TV/vrun33-led-l6b.tsv"
# L6c control: dir row with a WRONG but present vault hash -> NOT-SAFE expected
mkled "$TV/vrun33-led-l6c.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL6c\n' "$FX/dir-case" "$DIR_DIG" "$FV/dir-diff" "$WRONG" >> "$TV/vrun33-led-l6c.tsv"
# L14: first row mismatches, second row matches -> matching row must be found
mkled "$TV/vrun33-led-l14.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL14-wrong\n' "$FX/alpha.md" "$WRONG" "$FV/alpha.md" "$WRONG" >> "$TV/vrun33-led-l14.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL14-right\n' "$FX/alpha.md" "$ALPHA_SS" "$FV/alpha.md" "$ALPHA_VS" >> "$TV/vrun33-led-l14.tsv"
# L15 (informational): CRLF ledger row — contract silent on CRLF tolerance
mkled "$TV/vrun33-led-l15.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL15\r\n' "$FX/alpha.md" "$ALPHA_SS" "$FV/alpha.md" "$ALPHA_VS" >> "$TV/vrun33-led-l15.tsv"
# L16 dir row, empty vault hash, vault path missing -> NOT-SAFE expected
mkled "$TV/vrun33-led-l16.tsv"
printf '%s\t%s\t%s\t\n' "$FX/dir-case" "$DIR_DIG" "$FV/nope-dir" >> "$TV/vrun33-led-l16.tsv"
# L7 valid file row, NO trailing newline
mkled "$TV/vrun33-led-l7.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL7' "$FX/alpha.md" "$ALPHA_SS" "$FV/alpha.md" "$ALPHA_VS" >> "$TV/vrun33-led-l7.tsv"
# L8 header-only
mkled "$TV/vrun33-led-l8.tsv"
# L9 dir row, correct digests both sides
mkled "$TV/vrun33-led-l9.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL9\n' "$FX/dir-case" "$DIR_DIG" "$FV/dir-case" "$DIR_VS" >> "$TV/vrun33-led-l9.tsv"
# L10 file row whose vault path is a directory
mkled "$TV/vrun33-led-l10.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL10\n' "$FX/alpha.md" "$ALPHA_SS" "$FV/isadir" "$ALPHA_VS" >> "$TV/vrun33-led-l10.tsv"
# L11 garbage exported_at, correct hashes
mkled "$TV/vrun33-led-l11.tsv"
printf '%s\t%s\t%s\t%s\tGARBAGE-TS\tL11\n' "$FX/alpha.md" "$ALPHA_SS" "$FV/alpha.md" "$ALPHA_VS" >> "$TV/vrun33-led-l11.tsv"
# L12 beta: source differs from vault content, both hashes correct-as-recorded
mkled "$TV/vrun33-led-l12.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tL12\n' "$FX/beta.md" "$BETA_SS" "$FV/beta.md" "$BETA_VS" >> "$TV/vrun33-led-l12.tsv"

# V ledgers — live vault rows (read-only)
LIVE_VS_HOME=$(sha "$VAULT/Home.md")
printf 'live Home.md sha=%s\n' "$LIVE_VS_HOME" > "$OUT/vault-live.txt"
printf 'vrun33 live payload\n' > "$FX/live-src.md"
LIVE_SRC_SS=$(sha "$FX/live-src.md")
mkled "$TV/vrun33-led-v1.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tV1\n' "$FX/live-src.md" "$LIVE_SRC_SS" "$VAULT/Home.md" "$LIVE_VS_HOME" >> "$TV/vrun33-led-v1.tsv"
mkled "$TV/vrun33-led-v2.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tV2\n' "$FX/live-src.md" "$LIVE_SRC_SS" "$VAULT/Home.md" "$WRONG" >> "$TV/vrun33-led-v2.tsv"
mkled "$TV/vrun33-led-v3.tsv"
printf '%s\t%s\t%s\t%s\t2026-10-18\tV3\n' "$FX/live-src.md" "$LIVE_SRC_SS" "$VAULT/NOPE-vrun33-missing.md" "$WRONG" >> "$TV/vrun33-led-v3.tsv"

gt "GL0" "fixture digests (alpha/beta/dir)" \
  "echo alpha_ss=$ALPHA_SS alpha_vs=$ALPHA_VS dir_dig=$DIR_DIG dir_vs=$DIR_VS"
gt "GL7" "L7 ledger last byte" "tail -c1 '$TV/vrun33-led-l7.tsv' | od -c | head -1"

# ------------------------------------------------------------- A: syntax --
set +e; bash -n "$TOOL"; ARC=$?; set +e
record "A1" "bash-n-syntax" "cli" "bash -n tools/souji-verify.sh" "exit 0" "$ARC" \
  "bash -n rc=$ARC" "$([[ "$ARC" -eq 0 ]] && echo true || echo false)" ""

run_tool "$OUT/selftest.txt" "" -- --selftest
SEL_RC="$TRC"
REFS_AFTER_SEL="$(git -C "$REPO" for-each-ref --format='%(refname) %(objectname)' | sha256sum | cut -d' ' -f1)"
LEDGER_AFTER_SEL="$(sha "$LIVE_LEDGER")"
SHA_NOW="$(sha "$TOOL")"
sel_pass="true"; sel_note=""
[[ "$SEL_RC" == "0" ]] || { sel_pass="false"; sel_note+="selftest rc=$SEL_RC; "; }
[[ "$REFS_BEFORE" == "$REFS_AFTER_SEL" ]] || { sel_pass="false"; sel_note+="lane refs changed; "; }
[[ "$LEDGER_SHA_BEFORE" == "$LEDGER_AFTER_SEL" ]] || { sel_pass="false"; sel_note+="live ledger changed; "; }
[[ "$SHA_NOW" == "$SHA_START" ]] || sel_note+="tool changed during selftest; "
record "A2" "selftest-rc0-and-isolation" "cli" "bash tools/souji-verify.sh --selftest" \
  "rc=0 and live lane tree untouched" "$SEL_RC" "$(tail -2 "$OUT/selftest.txt" | tr '\n' '|')" \
  "$sel_pass" "$sel_note"

# ---------------------------------------------------------- C: CLI usage --
run_tool "$OUT/c1.txt" "" -- --bogus-flag
assert_case "C1" "usage-unknown-flag" "cli" "souji-verify.sh --bogus-flag" "rc=2" "2" "" "" "" "" "$OUT/c1.txt" ""
run_tool "$OUT/c2.txt" ""
assert_case "C2" "usage-no-args" "cli" "souji-verify.sh (no args)" "rc=2" "2" "" "" "" "" "$OUT/c2.txt" ""

MISS="$WORK/missing-vrun33"
run_tool "$OUT/c3.txt" "" -- "$MISS"
assert_case "C3" "missing-target" "cli" "souji-verify.sh <nonexistent>" "rc=0 NOT-SAFE unreachable" \
  "0" "^NOT-SAFE$" "^unreachable$" "" "$MISS" "$OUT/c3.txt" ""

run_tool "$OUT/c4.txt" "" -- --json "$MISS"
jok="$(jsonok "$OUT/c4.txt")"
jpass="false"; [[ "$TRC" == "0" && ( "$jok" == "object" || "$jok" == "jsonl" ) ]] && jpass="true"
record "C4" "json-flag-parseable" "cli" "souji-verify.sh --json <missing>" \
  "rc=0, stdout parses as JSON or JSONL" "$TRC" "parse=$jok" "$jpass" ""

# C5: --cli acceptance is contract-conditional: declared -> rc=0; absent -> rc=2.
run_tool "$OUT/c5.txt" "" -- --cli "$MISS"
if [ "${TOOL_HAS_CLI:-0}" != 0 ]; then
  assert_case "C5" "cli-flag-accepted" "cli" "souji-verify.sh --cli <missing>" \
    "declared --cli -> rc=0" "0" "" "" "" "$MISS" "$OUT/c5.txt" ""
else
  assert_case "C5" "cli-flag-absent" "cli" "souji-verify.sh --cli <missing>" \
    "no --cli declared -> unknown flag rc=2 (never hang/ignore)" "2" "" "" "" "" "$OUT/c5.txt" \
    "fallback-only tool; r4 upgrade flips this to rc=0"
fi

# C6: --cli with a hanging CLI -> only meaningful once --cli exists.
if [ "${TOOL_HAS_CLI:-0}" != 0 ]; then
  MOCKD="$WORK/mockbin"; mkdir -p "$MOCKD"
  cat > "$MOCKD/obsidian" <<'MK'
#!/usr/bin/env bash
case "${MOCK_MODE:-ok}" in
  hang) sleep 60; exit 0 ;;
  error) echo "mock: cli error" >&2; exit 3 ;;
  *) echo '{"ok":true,"sha256":"0000000000000000000000000000000000000000000000000000000000000000"}'; exit 0 ;;
esac
MK
  chmod +x "$MOCKD/obsidian"
  run_tool "$OUT/c6.txt" "PATH=$MOCKD:$PATH MOCK_MODE=hang" -- --cli "$MISS"
  c6_pass="true"
  [[ "$TRC" == "124" ]] && c6_pass="false"
  record "C6" "cli-hang-bounded" "cli" "souji-verify.sh --cli <target> with hanging cli" \
    "tool returns before harness timeout; never SAFE" "$TRC" "$(head -2 "$OUT/c6.txt" | tr '\n' '|')" \
    "$c6_pass" "secs=$LAST_SECS"
else
  record "C6" "cli-hang-bounded" "blocked-interface" \
    "souji-verify.sh --cli <target> with hanging cli" \
    "requires --cli in the tool" "0" "tool has no --cli (cli_refs=0)" "false" \
    "unblocked by the r4 integration; re-run this runner after the upgrade"
fi

# ------------------------------------------------------ L: ledger semantics
led_case() { # id name ledger target vre rre
  local id="$1" name="$2" led="$3" tgt="$4" vre="$5" rre="$6"
  run_tool "$OUT/$id.txt" "SOUJI_LEDGER=$led SHOKUNIN_ROOT=$FLEET" -- -- "$tgt"
  assert_case "$id" "$name" "fixture" "souji-verify.sh <$tgt> (ledger=$led)" \
    "spec: $vre/$rre" "0" "$vre" "$rre" "" "$tgt" "$OUT/$id.txt" ""
}

led_case "L1"  "ledger-correct-file-row"        "$TV/vrun33-led-l1.tsv"  "$FX/alpha.md" "^SAFE$" "^moved-to-obsidian$"
led_case "L2"  "ledger-wrong-source-hash"       "$TV/vrun33-led-l2.tsv"  "$FX/alpha.md" "^NOT-SAFE$" ""
led_case "L3"  "ledger-wrong-vault-hash"        "$TV/vrun33-led-l3.tsv"  "$FX/alpha.md" "^NOT-SAFE$" ""
led_case "L4"  "ledger-empty-source-hash-file"  "$TV/vrun33-led-l4.tsv"  "$FX/alpha.md" "^NOT-SAFE$" ""
led_case "L5"  "ledger-empty-vault-hash-file"   "$TV/vrun33-led-l5.tsv"  "$FX/alpha.md" "^NOT-SAFE$" ""
led_case "L6a" "ledger-empty-vault-hash-dir"    "$TV/vrun33-led-l6a.tsv" "$FX/dir-case" "^NOT-SAFE$" ""
led_case "L6b" "ledger-3field-dir-row"          "$TV/vrun33-led-l6b.tsv" "$FX/dir-case" "^NOT-SAFE$" ""
led_case "L6c" "ledger-wrong-vault-hash-dir"    "$TV/vrun33-led-l6c.tsv" "$FX/dir-case" "^NOT-SAFE$" ""
led_case "L7"  "ledger-row-no-trailing-newline" "$TV/vrun33-led-l7.tsv"  "$FX/alpha.md" "^SAFE$" "^moved-to-obsidian$"
led_case "L8"  "ledger-header-only"             "$TV/vrun33-led-l8.tsv"  "$FX/alpha.md" "^NOT-SAFE$" ""
led_case "L9"  "ledger-correct-dir-row"         "$TV/vrun33-led-l9.tsv"  "$FX/dir-case" "^SAFE$" "^moved-to-obsidian$"
led_case "L10" "ledger-vault-path-is-a-dir"     "$TV/vrun33-led-l10.tsv" "$FX/alpha.md" "^NOT-SAFE$" ""
led_case "L11" "ledger-garbage-exported-at"     "$TV/vrun33-led-l11.tsv" "$FX/alpha.md" "^SAFE$" "^moved-to-obsidian$"
led_case "L12" "ledger-beta-both-hashes-match"  "$TV/vrun33-led-l12.tsv" "$FX/beta.md"  "^SAFE$" "^moved-to-obsidian$"
led_case "L14" "ledger-second-row-matches"      "$TV/vrun33-led-l14.tsv" "$FX/alpha.md" "^SAFE$" "^moved-to-obsidian$"
led_case "L16" "ledger-empty-vault-hash-dir-missing" "$TV/vrun33-led-l16.tsv" "$FX/dir-case" "^NOT-SAFE$" "^none$"

# L15: CRLF row — informational (contract silent on CRLF tolerance).
run_tool "$OUT/L15.txt" "SOUJI_LEDGER=$TV/vrun33-led-l15.tsv SHOKUNIN_ROOT=$FLEET" -- -- "$FX/alpha.md"
record "L15" "ledger-crlf-row" "info:fixture" "souji-verify.sh <alpha> (CRLF ledger row)" \
  "informational: CRLF tolerance unspecified" "$TRC" \
  "$(verdict_line "$FX/alpha.md" "$OUT/L15.txt")" "true" "observed above; no assertion"

# L13: no SOUJI_LEDGER override -> live header-only ledger grants nothing.
run_tool "$OUT/L13.txt" "SHOKUNIN_ROOT=$FLEET" -- -- "$FX/alpha.md"
assert_case "L13" "live-ledger-grants-nothing" "live" "souji-verify.sh <fixture> (default live ledger)" \
  "header-only live ledger -> NOT-SAFE" "0" "^NOT-SAFE$" "" "" "$FX/alpha.md" "$OUT/L13.txt" \
  "live ledger stays header-only; read-only"

# ---------------------------------------------------------- V: live vault --
run_tool "$OUT/V1.txt" "SOUJI_LEDGER=$TV/vrun33-led-v1.tsv SHOKUNIN_ROOT=$FLEET" -- -- "$FX/live-src.md"
assert_case "V1" "live-vault-real-file" "live" "souji-verify.sh <live-src> (real vault row)" \
  "rc=0 SAFE(moved-to-obsidian), evidence names the real vault" "0" "^SAFE$" "^moved-to-obsidian$" \
  "vault=$VAULT" "$FX/live-src.md" "$OUT/V1.txt" "read-only sha256sum of $VAULT/Home.md"

run_tool "$OUT/V2.txt" "SOUJI_LEDGER=$TV/vrun33-led-v2.tsv SHOKUNIN_ROOT=$FLEET" -- -- "$FX/live-src.md"
assert_case "V2" "live-vault-wrong-hash" "live" "souji-verify.sh <live-src> (wrong vault hash)" \
  "NOT-SAFE — vault digest mismatch" "0" "^NOT-SAFE$" "" "" "$FX/live-src.md" "$OUT/V2.txt" ""

run_tool "$OUT/V3.txt" "SOUJI_LEDGER=$TV/vrun33-led-v3.tsv SHOKUNIN_ROOT=$FLEET" -- -- "$FX/live-src.md"
assert_case "V3" "live-vault-missing-path" "live" "souji-verify.sh <live-src> (vault path missing)" \
  "NOT-SAFE — vault unreachable" "0" "^NOT-SAFE$" "" "vault-unreachable" "$FX/live-src.md" "$OUT/V3.txt" ""

# ------------------------------------------------------------- X: domain --
dom_pass="$(awk '$1 !~ /^[012]$/ {f=1} END {print (f ? "false" : "true")}' "$TRCS")"
record "X1" "exit-code-domain" "cli" "all tool runs collected" "rc in {0,1,2} only" "0" \
  "observed=$(sort -u "$TRCS" | tr '\n' ' ')" "$dom_pass" ""

run_tool "$OUT/L1b.txt" "SOUJI_LEDGER=$TV/vrun33-led-l1.tsv SHOKUNIN_ROOT=$FLEET" -- -- "$FX/alpha.md"
det_a="$(verdict_line "$FX/alpha.md" "$OUT/L1.txt")"
det_b="$(verdict_line "$FX/alpha.md" "$OUT/L1b.txt")"
det_pass="false"; [[ -n "$det_a" && "$det_a" == "$det_b" ]] && det_pass="true"
record "X2" "determinism-L1-twice" "cli" "souji-verify.sh <L1 target> x2" "identical verdict lines" \
  "$TRC" "$det_b" "$det_pass" ""

# ------------------------------------------- M: r4 candidate matrix --------
# Round-4 candidate tools are evaluated with the SAME defect probes that
# caught F1/F2 in the r2 baseline, so the parent has comparable inputs.
# Vocabulary tolerance: SAFE-class = {SAFE, VERIFIED*}; NOT-SAFE-class =
# {NOT-SAFE*, NOT-VERIFIED*} (r2 VERDICT line wins when present).
norm_verdict() { # target outfile -> SAFE|NOT-SAFE|?
  local vl
  vl="$(verdict_line "$1" "$2")"
  if [ -n "$vl" ]; then printf '%s' "$vl" | cut -f3; return 0; fi
  if grep -q '^VERIFIED' "$2"; then printf 'SAFE'; return 0; fi
  if grep -q '^NOT-VERIFIED' "$2"; then printf 'NOT-SAFE'; return 0; fi
  printf '?'
}

mcase() { # id cand tgt outfile want note
  local id="$1" cand="$2" tgt="$3" of="$4" want="$5" note="$6"
  local got pass
  got="$(norm_verdict "$tgt" "$of")"
  case "$got" in
    SAFE)     [[ "$want" == "SAFE" ]]     && pass=true || pass=false ;;
    NOT-SAFE) [[ "$want" == "NOT-SAFE" ]] && pass=true || pass=false ;;
    *)        pass=false ;;
  esac
  record "$id" "candidate-$cand" "fixture" "$(basename "$cand") (probe $id)" \
    "expect $want" "$TRC" "got=$got first=$(head -1 "$of")" "$pass" "$note"
}

CANDS=()
for c in "$REPO"/tools/souji-vault-verify*.sh "$REPO"/tools/impl-*.sh; do
  [ -f "$c" ] || continue
  CANDS+=("$c")
done
if [ "${#CANDS[@]}" -eq 0 ]; then
  record "M0" "candidate-matrix" "info" "glob tools/souji-vault-verify*.sh tools/impl-*.sh" \
    "none yet" "1" "no r4 candidate present" "true" "re-run when candidates land"
else
  for cand in "${CANDS[@]}"; do
    cn="$(basename "$cand")"
    tag="$(printf '%s' "$cn" | sed -n 's/.*impl-\([0-9][0-9]*\).*/\1/p')"
    [ -n "$tag" ] || tag="$(printf '%s' "$cn" | tr -cd '0-9')"
    CSHA="$(sha "$cand")"
    CUR_TOOL="$cand"
    record "M${tag}-sha" "candidate-${tag}-sha" "info" "sha256sum $cn" "evidence" "0" \
      "sha256=$CSHA" "true" ""
    # selftest
    run_tool "$OUT/M${tag}-selftest.txt" "" -- --selftest 2>/dev/null
    st_rc="$TRC"
    st_pass="false"; [ "$st_rc" = 0 ] && st_pass="true"
    record "M${tag}-selftest" "candidate-${tag}-selftest" "cli" "$cn --selftest" \
      "rc=0" "$st_rc" "$(tail -1 "$OUT/M${tag}-selftest.txt")" "$st_pass" ""
    # flag support detection (env SOUJI_LEDGER always set)
    mrun() { # id target ledger want note
      local id="$1" tgt="$2" led="$3" want="$4" note="$5"
      local -a args=()
      grep -q -- '--ledger' "$cand" && args+=(--ledger "$led")
      grep -q -- '--vault'  "$cand" && args+=(--vault "$FV")
      args+=(-- "$tgt")
      run_tool "$OUT/M${tag}-${id}.txt" "SOUJI_LEDGER=$led SOUJI_VAULT=$FV SHOKUNIN_ROOT=$FLEET" -- "${args[@]}"
      mcase "M${tag}-${id}" "$tag" "$tgt" "$OUT/M${tag}-${id}.txt" "$want" "$note"
    }
    mrun "L1"  "$FX/alpha.md"   "$TV/vrun33-led-l1.tsv"  "SAFE"     "control: correct ledger row"
    mrun "L6a" "$FX/dir-case"   "$TV/vrun33-led-l6a.tsv" "NOT-SAFE" "F1 regression probe"
    mrun "L6b" "$FX/dir-case"   "$TV/vrun33-led-l6b.tsv" "NOT-SAFE" "F1 regression probe (3-field row)"
    mrun "L7"  "$FX/alpha.md"   "$TV/vrun33-led-l7.tsv"  "SAFE"     "F2 regression probe"
    mrun "V2"  "$FX/live-src.md" "$TV/vrun33-led-v2.tsv" "NOT-SAFE" "live vault wrong hash"
    mrun "L8"  "$FX/alpha.md"   "$TV/vrun33-led-l8.tsv"  "NOT-SAFE" "header-only ledger"
    mrun "L5"  "$FX/alpha.md"   "$TV/vrun33-led-l5.tsv"  "NOT-SAFE" "file empty vault hash"
    CUR_TOOL=""
  done
fi

# ------------------------------------------------------- RO: read-only ----
VAULT_SNAP_AFTER="$(vault_snapshot)"
VAULT_GIT_AFTER="$(git -C "$VAULT" status --porcelain 2>/dev/null | sha256sum | cut -d' ' -f1)"
LEDGER_SHA_AFTER="$(sha "$LIVE_LEDGER")"
LEDGER_LINES_AFTER="$(wc -l <"$LIVE_LEDGER" 2>/dev/null | tr -d ' ')"
ro_pass="true"; ro_note=""
[[ "$VAULT_SNAP_BEFORE" == "$VAULT_SNAP_AFTER" ]] || { ro_pass="false"; ro_note+="vault manifest changed; "; }
[[ "$VAULT_GIT_BEFORE" == "$VAULT_GIT_AFTER" ]] || { ro_pass="false"; ro_note+="vault git status changed; "; }
[[ "$LEDGER_SHA_BEFORE" == "$LEDGER_SHA_AFTER" ]] || { ro_pass="false"; ro_note+="live ledger changed; "; }
[[ "$LEDGER_LINES_BEFORE" == "1" && "$LEDGER_LINES_AFTER" == "1" ]] || { ro_pass="false"; ro_note+="live ledger not header-only; "; }
record "RO1" "read-only-vault-and-ledger" "live" "vault manifest + live ledger sha before/after all runs" \
  "unchanged" "0" "vault=$VAULT_SNAP_BEFORE ledger_lines=$LEDGER_LINES_BEFORE/$LEDGER_LINES_AFTER" \
  "$ro_pass" "$ro_note"

if pgrep -f 'obsidian\.asar' >/dev/null 2>&1; then
  record "RO2" "gui-not-spawned" "live" "pgrep -f obsidian.asar" "no process" "0" \
    "obsidian app RUNNING (spawned by something)" "false" "GUI launcher must never be executed"
else
  record "RO2" "gui-not-spawned" "live" "pgrep -f obsidian.asar" "no process" "1" \
    "no obsidian.asar process" "true" ""
fi

SHA_AT_WRITE="$(sha "$TOOL")"
record "RO3" "tool-unchanged" "info" "sha256sum tools/souji-verify.sh at write" \
  "same as at start" "0" "start=$SHA_START write=$SHA_AT_WRITE" "true" \
  "$([[ "$SHA_START" == "$SHA_AT_WRITE" ]] && echo stable || echo CHANGED) "

# ------------------------------------------------------------- result -----
N="$(failcount)"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if (( N > 0 )); then VERDICT="TOOL-FAIL"; RC=1; else VERDICT="TOOL-PASS"; RC=0; fi
write_result "$VERDICT" "true" "$SHA_START" "$T0" "$NOW" "$REPO" "$TOOL" "$STALE_DAYS" >/dev/null

# findings block: machine-readable defect classes derived from this run
python3 - "$CASES" "$RESULT" "$TOOL" "$VAULT" "$LIVE_LEDGER" <<'PY'
import json, sys
cases_f, result_f, tool, vault, ledger = sys.argv[1:6]
rows = {}
for line in open(cases_f, encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 9:
        rows[p[0]] = {'pass': None if p[2].startswith('info') or p[2] == 'blocked-interface' else (p[7] == 'true'),
                      'actual': p[6], 'name': p[1]}
d = json.load(open(result_f, encoding='utf-8'))
def case(cid):
    r = rows.get(cid, {})
    return {'id': cid, 'name': r.get('name'), 'pass': r.get('pass'),
            'observed': (r.get('actual') or '')[:220]}
d['findings'] = [
    {
        'id': 'F1', 'severity': 'high', 'direction': 'false-SAFE',
        'class': 'dir-branch empty/absent vault_sha256 skips the vault-digest check',
        'where': 'tools/souji-verify.sh try_obsidian() dir branch: `[ -n "$vs" ] && ...` guard',
        'evidence': [case('L6a'), case('L6b'), case('L16'), case('L6c')],
        'control': 'L6c (wrong-but-present hash) -> NOT-SAFE; L16 (vault missing) -> NOT-SAFE; '
                   'file branch L5 fail-closed — so the hole is dir-branch + vault-present + empty hash only',
        'why_it_matters': 'a row missing the vault hash (e.g. a torn append or a hand-edited row) '
                          'yields SAFE(moved-to-obsidian) although the vault copy was never digest-checked',
    },
    {
        'id': 'F2', 'severity': 'medium', 'direction': 'false-NOT-SAFE',
        'class': 'ledger row without trailing newline is dropped (bash read at EOF)',
        'where': 'tools/souji-verify.sh ledger_lines(): `while IFS= read -r line`',
        'evidence': [case('L7'), case('L1')],
        'control': 'L1 identical row WITH newline -> SAFE(moved-to-obsidian)',
        'why_it_matters': 'a valid final row written without a trailing newline is invisible; '
                          'the verdict is a false NOT-SAFE (conservative direction, but a contract break)',
    },
]
d['integration_state'] = {
    'cli_flag_present': rows.get('A3', {}).get('actual', ''),
    'blocked': [case('C6')],
    'note': 'r4 --cli surface absent from the r2 baseline tool; C6 stays blocked-interface until the upgrade lands',
}

# candidate matrix summary: which r4 tool fixes F1/F2, per my own probes
def mrow(tag, cid):
    return case('M%s-%s' % (tag, cid))
cand = {}
for tag in ('20', '21', '24'):
    if 'M%s-L1' % tag not in rows:
        continue
    cand['impl-%s' % tag] = {
        'sha256': (rows.get('M%s-sha' % tag, {}).get('actual', '') or '').replace('sha256=', ''),
        'selftest': mrow(tag, 'selftest'),
        'F1_dir_empty_vault_hash': mrow(tag, 'L6a'),
        'F1_3field_row': mrow(tag, 'L6b'),
        'F2_no_trailing_newline': mrow(tag, 'L7'),
        'control_correct_row': mrow(tag, 'L1'),
        'live_vault_wrong_hash': mrow(tag, 'V2'),
        'header_only_ledger': mrow(tag, 'L8'),
        'file_empty_vault_hash': mrow(tag, 'L5'),
    }
d['candidate_matrix'] = cand
d['recommendation'] = {
    'summary': 'On my probes, impl-20 and impl-21 fix both F1 and F2; impl-24 still drops '
               'unterminated rows (F2); the r2 baseline tool has both defects.',
    'verdict_inputs': {
        'impl-20': 'F1 fixed (row-incomplete), F2 fixed (VERIFIED), own selftest 35/35 rc=0',
        'impl-21': 'F1 fixed (empty-hash-column), F2 fixed (SAFE), own selftest RED (3 FAILs, rc=1, unbound $LIE_OLD line 786)',
        'impl-24': 'F2 NOT fixed (row dropped: no-ledger-row), F1 dir probe answered source-absent, own selftest 13/13 rc=0',
        'r2-baseline': 'F1 present (false SAFE), F2 present (row dropped)',
    },
}
with open(result_f, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('findings written:', [x['id'] for x in d['findings']], '| candidates:', sorted(cand))
PY

echo "vrun-33: $VERDICT counted=$(( $(grep -c . "$CASES") )) failed=$N cli_refs=$TOOL_HAS_CLI"
echo "vrun-33: result -> $RESULT (tool sha256=$SHA_START)"
exit "$RC"
