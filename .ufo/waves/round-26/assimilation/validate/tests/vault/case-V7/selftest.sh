#!/usr/bin/env bash
# case-V7 selftest — proves the fixture encodes the V7 expectation and that
# the expectation is discriminating.
#
# Checks:
#   T1  build invariants: 4 payload pairs present, digests equal the five
#       constants, vault copies mode 0444, mismatch pair differs
#   T2  ledger shape: header + 4 rows with 7/8/6/7 columns; column 6 recovers
#       the four declared notes
#   T3  substituted expected.json parses; every target/expect path exists in
#       the built root; expect verdicts are 3x VERIFIED + 1x NOT-VERIFIED
#   T4  r2 baseline (tools/souji-verify.sh, SOUJI_LEDGER seam): the three
#       matched rows (7/8/6 columns) report SAFE + moved-to-obsidian (extra
#       columns ignored), the edited-vault row reports NOT-SAFE with
#       vault-sha-mismatch — the class delta (VERIFIED vocabulary + note
#       recording) is what the r4 harness must add
#   T5  disarmed control: with a header-only ledger every target reports
#       NOT-SAFE(none) — the row is the receipt
#   T6  live surfaces untouched: corpus/knowledge/obsidian-ledger.tsv still
#       header-only and unchanged; real vault not read from or written to
#
# Usage: bash selftest.sh [--keep] [--out JSON] [--tool PATH]
#   --tool PATH   probe this tool instead of tools/souji-verify.sh
#   default: fresh mktemp -d fixture, reaped on exit; exit 0 all pass, 1 fail.
set -euo pipefail
export LC_ALL=C

here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
lane=$(cd -- "$here/../../.." && pwd)
tool="$lane/tools/souji-verify.sh"
live_ledger="$lane/corpus/knowledge/obsidian-ledger.tsv"

keep=0
out_json=""
while [ $# -gt 0 ]; do
  case "$1" in
    --keep) keep=1; shift ;;
    --out) out_json=$2; shift 2 ;;
    --tool) tool=$2; shift 2 ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "usage: selftest.sh [--keep] [--out JSON] [--tool PATH]" >&2; exit 2 ;;
  esac
done

tmp=$(mktemp -d "${TMPDIR:-/tmp}/case-V7-selftest.XXXXXX")
cleanup() { [ "$keep" = 1 ] || rm -rf -- "$tmp"; }
trap cleanup EXIT

pass=0; fail=0; results=()
ck() { # ck NAME EXPECTED ACTUAL
  if [ "$2" = "$3" ]; then
    pass=$((pass+1)); results+=("PASS	$1	$3")
  else
    fail=$((fail+1)); results+=("FAIL	$1	want=$2 got=$3")
  fi
}

live_before=$(sha256sum -- "$live_ledger" | cut -d' ' -f1 2>/dev/null || echo absent)
live_rows_before=$(wc -l < "$live_ledger" 2>/dev/null || echo 0)

# --- T1/T2/T3: build --------------------------------------------------------
root="$tmp/root"
bash "$here/make-fixture.sh" --out "$root" --quiet > "$tmp/build.out" 2> "$tmp/build.err"
ck T1.builder_exit 0 "$?"

p_src="$root/source/src/extra-cols-notes.md";   p_vlt="$root/vault/extra-cols-notes.md"
e8_src="$root/source/src/extra-cols-8-notes.md"; e8_vlt="$root/vault/extra-cols-8-notes.md"
c_src="$root/source/src/six-cols-notes.md";      c_vlt="$root/vault/six-cols-notes.md"
m_src="$root/source/src/extra-cols-mismatch.md"; m_vlt="$root/vault/extra-cols-mismatch.md"
ledger="$root/ledger.tsv"

sha() { sha256sum -- "$1" | cut -d' ' -f1; }
ck T1.pair7_identical "$(sha "$p_src")" "$(sha "$p_vlt")"
ck T1.pair8_identical "$(sha "$e8_src")" "$(sha "$e8_vlt")"
ck T1.pair_control_identical "$(sha "$c_src")" "$(sha "$c_vlt")"
ck T1.mismatch_differs_yes "$([ "$(sha "$m_src")" != "$(sha "$m_vlt")" ] && echo yes || echo no)" yes
for v in "$p_vlt" "$e8_vlt" "$c_vlt" "$m_vlt"; do
  mode=$(stat -c %a -- "$v")
  ck "T1.vault_mode_$(basename "$v")" 444 "$mode"
done

ck T2.header_cols 6 "$(awk -F'\t' 'NR==1 {print NF; exit}' "$ledger")"
ck T2.row1_cols 7 "$(awk -F'\t' 'NR==2 {print NF; exit}' "$ledger")"
ck T2.row2_cols 8 "$(awk -F'\t' 'NR==3 {print NF; exit}' "$ledger")"
ck T2.row3_cols 6 "$(awk -F'\t' 'NR==4 {print NF; exit}' "$ledger")"
ck T2.row4_cols 7 "$(awk -F'\t' 'NR==5 {print NF; exit}' "$ledger")"
notes=$(awk -F'\t' 'NR>1 {print $6}' "$ledger" | paste -sd'|')
ck T2.notes_recovered \
  "case-V7 extra-cols|case-V7 extra-cols-8|case-V7 six-cols control|case-V7 extra-cols mismatch" \
  "$notes"

python3 - "$root/expected.json" "$root" <<'PY' || { fail=$((fail+1)); results+=("FAIL	T3.expected_json	not parseable"); }
import json, sys, os
doc = json.load(open(sys.argv[1]))
root = sys.argv[2]
ts = doc["targets"]; ex = doc["expect"]
assert len(ts) == 4, len(ts)
assert len(ex) == 4, len(ex)
for t in ts:
    assert t.startswith(root + "/"), t
    assert os.path.exists(t), t
vs = [e["verdict"] for e in ex]
assert vs == ["VERIFIED", "VERIFIED", "VERIFIED", "NOT-VERIFIED"], vs
print("ok")
PY
ck T3.expected_json_valid yes yes

# --- T4: r2 baseline --------------------------------------------------------
if [ -x "$tool" ] || [ -f "$tool" ]; then
  r2out=$(SOUJI_LEDGER="$ledger" SHOKUNIN_ROOT="$root" bash "$tool" \
    "$p_src" "$e8_src" "$c_src" "$m_src" 2>/dev/null)
  line7=$(printf '%s\n' "$r2out" | awk -F'\t' -v t="$p_src" '$2==t {print $3" "$4}')
  line8=$(printf '%s\n' "$r2out" | awk -F'\t' -v t="$e8_src" '$2==t {print $3" "$4}')
  linec=$(printf '%s\n' "$r2out" | awk -F'\t' -v t="$c_src" '$2==t {print $3" "$4}')
  linem=$(printf '%s\n' "$r2out" | awk -F'\t' -v t="$m_src" '$2==t {print $3" "$4" "$5}')
  ck T4.r2_row7_extra_cols "$line7" "SAFE moved-to-obsidian"
  ck T4.r2_row8_extra_cols "$line8" "SAFE moved-to-obsidian"
  ck T4.r2_row6_control "$linec" "SAFE moved-to-obsidian"
  ck T4.r2_row4_mismatch "$(printf '%s' "$linem" | awk '{print $1" "$2}')" "NOT-SAFE none"
  ck T4.r2_mismatch_reason \
    "$(printf '%s' "$linem" | grep -q 'vault-sha-mismatch' && echo yes || echo no)" yes
else
  ck T4.tool_present missing "$tool"
fi

# --- T5: disarmed control ---------------------------------------------------
disarmed=$(mktemp "$tmp/disarmed.XXXXXX")
head -1 "$ledger" > "$disarmed"
dout=$(SOUJI_LEDGER="$disarmed" SHOKUNIN_ROOT="$root" bash "$tool" \
  "$p_src" "$e8_src" "$c_src" "$m_src" 2>/dev/null || true)
d_safe=$(printf '%s\n' "$dout" | awk -F'\t' '$3=="SAFE"' | wc -l | tr -d ' ')
ck T5.disarmed_no_safe 0 "$d_safe"
d_none=$(printf '%s\n' "$dout" | awk -F'\t' '$3=="NOT-SAFE" && $4=="none"' | wc -l | tr -d ' ')
ck T5.disarmed_all_none 4 "$d_none"

# --- T6: live surfaces ------------------------------------------------------
live_after=$(sha256sum -- "$live_ledger" | cut -d' ' -f1 2>/dev/null || echo absent)
live_rows_after=$(wc -l < "$live_ledger" 2>/dev/null || echo 0)
ck T6.live_ledger_unchanged "$live_before" "$live_after"
ck T6.live_ledger_header_only 1 "$live_rows_after"

# --- report -----------------------------------------------------------------
printf 'SELFTEST %s pass=%s fail=%s\n' \
  "$([ "$fail" -eq 0 ] && echo PASS || echo FAIL)" "$pass" "$fail"
for r in "${results[@]}"; do printf '%s\n' "$r"; done

if [ -n "$out_json" ]; then
  mkdir -p -- "$(dirname -- "$out_json")"
  {
    printf '{\n'
    printf '  "case": "case-V7",\n'
    printf '  "seat": "S15",\n'
    printf '  "fixture_root": "%s",\n' "$root"
    printf '  "tool": "%s",\n' "$tool"
    printf '  "pass": %s,\n  "fail": %s,\n' "$pass" "$fail"
    printf '  "results": [\n'
    first=1
    for r in "${results[@]}"; do
      status=${r%%$'\t'*}; rest=${r#*$'\t'}
      name=${rest%%$'\t'*}; detail=${rest#*$'\t'}
      [ "$first" = 1 ] || printf ',\n'
      first=0
      printf '    {"check": "%s", "status": "%s", "detail": "%s"}' "$name" "$status" "$detail"
    done
    printf '\n  ]\n}\n'
  } > "$out_json"
fi

[ "$fail" -eq 0 ]
