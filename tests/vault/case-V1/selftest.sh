#!/usr/bin/env bash
# case-V1 selftest — souji-shokunin round 4, seat S09.
#
# Builds the case-V1 fixture in an isolated mktemp root and asserts every
# declared invariant (T1), the r2-tool crosscheck in both directions (T2),
# the three conjunct negatives (T3), determinism (T4), and that the live
# ledger corpus/knowledge/obsidian-ledger.tsv stays header-only and unchanged
# (T5). Writes only under mktemp roots and --out (default
# tests/results/v1-selftest.json). Never touches the live ledger, the real
# vault, or any sibling repo.
#
# usage: selftest.sh [--keep] [--out JSON] [--tool PATH]
# exit: 0 all checks pass; 1 any check failed; 2 usage
set -uo pipefail
export LC_ALL=C

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LANE_ROOT="$(cd -- "$HERE/../../.." && pwd)"
MAKER="$HERE/make-fixture.sh"
OUT="$LANE_ROOT/tests/results/v1-selftest.json"
TOOL="$LANE_ROOT/tools/souji-verify.sh"
KEEP=0
LIVE_LEDGER="$LANE_ROOT/corpus/knowledge/obsidian-ledger.tsv"
SHA_NOTE="a63192a11325e61f3aebfd483c34f21c05c5bf815bc83cef7866a92b8132f840"

while [ $# -gt 0 ]; do
  case "$1" in
    --keep) KEEP=1; shift ;;
    --out) [ $# -ge 2 ] || { echo "usage: $0 [--keep] [--out JSON] [--tool PATH]" >&2; exit 2; }; OUT="$2"; shift 2 ;;
    --tool) [ $# -ge 2 ] || { echo "usage: $0 [--keep] [--out JSON] [--tool PATH]" >&2; exit 2; }; TOOL="$2"; shift 2 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "usage: $0 [--keep] [--out JSON] [--tool PATH]" >&2; exit 2 ;;
  esac
done

WORK="$(mktemp -d "${TMPDIR:-/tmp}/case-V1-selftest.XXXXXX")"
cleanup() { [ "$KEEP" = 1 ] || rm -rf "$WORK"; }
trap cleanup EXIT

RTSV="$WORK/results.tsv"; : > "$RTSV"
pass_n=0; fail_n=0
check() { # id status detail
  local id="$1" status="$2" detail="$3"
  printf '%s\t%s\t%s\n' "$status" "$id" "$detail" >> "$RTSV"
  if [ "$status" = PASS ]; then pass_n=$((pass_n+1)); else fail_n=$((fail_n+1)); fi
}
sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

# live-ledger fingerprint before anything runs
LIVE_SHA_BEFORE="$(sha "$LIVE_LEDGER" 2>/dev/null || echo missing)"
LIVE_LINES_BEFORE="$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ' || echo 0)"

# ---------------------------------------------------------------- T1 build
ROOT="$WORK/root"
BOUT="$(bash "$MAKER" --out "$ROOT" --ledger "$WORK/ledger-copy.tsv" 2>"$WORK/build.err")"
BRC=$?
[ "$BRC" = 0 ] && check "T1.builder_exit" PASS "0" || check "T1.builder_exit" FAIL "rc=$BRC $(tail -1 "$WORK/build.err" 2>/dev/null)"

READY_TOKEN="$(printf '%s\n' "$BOUT" | sed -n 's/^FIXTURE_READY[[:space:]]\+[^[:space:]]\+[[:space:]]\+\([^[:space:]]*\)$/\1/p' | head -1)"
if [ -n "$READY_TOKEN" ] && [ -d "$READY_TOKEN" ]; then
  check "T1.ready_token_is_root" PASS "$READY_TOKEN"
else
  check "T1.ready_token_is_root" FAIL "token='$READY_TOKEN' not a directory"
fi
[ "$READY_TOKEN" = "$ROOT" ] && check "T1.ready_token_matches_out" PASS "$ROOT" || check "T1.ready_token_matches_out" FAIL "token=$READY_TOKEN out=$ROOT"

SRC="$ROOT/source/note.md"; VLT="$ROOT/vault/note.md"
[ -f "$SRC" ] && check "T1.source_present" PASS "$SRC" || check "T1.source_present" FAIL "missing"
[ -f "$VLT" ] && check "T1.vault_present" PASS "$VLT" || check "T1.vault_present" FAIL "missing"
[ "$(sha "$SRC")" = "$SHA_NOTE" ] && check "T1.source_digest" PASS "$SHA_NOTE" || check "T1.source_digest" FAIL "$(sha "$SRC")"
[ "$(sha "$VLT")" = "$SHA_NOTE" ] && check "T1.vault_digest" PASS "$SHA_NOTE" || check "T1.vault_digest" FAIL "$(sha "$VLT")"
cmp -s -- "$SRC" "$VLT" && check "T1.byte_identical" PASS "cmp=0" || check "T1.byte_identical" FAIL "differ"
MODE="$(stat -c %a "$VLT" 2>/dev/null || echo '?')"
[ "$MODE" = 444 ] && check "T1.vault_mode_0444" PASS "444" || check "T1.vault_mode_0444" FAIL "$MODE"
[ -f "$ROOT/.case-V1-fixture" ] && check "T1.marker" PASS "yes" || check "T1.marker" FAIL "no"
[ -f "$ROOT/ledger.tsv" ] && [ "$(wc -l < "$ROOT/ledger.tsv" | tr -d ' ')" = 2 ] \
  && check "T1.root_ledger_header_plus_one_row" PASS "2 lines" \
  || check "T1.root_ledger_header_plus_one_row" FAIL "$(wc -l < "$ROOT/ledger.tsv" 2>/dev/null)"
[ -f "$WORK/ledger-copy.tsv" ] && [ "$(wc -l < "$WORK/ledger-copy.tsv" | tr -d ' ')" = 2 ] \
  && check "T1.ledger_copy_written" PASS "$WORK/ledger-copy.tsv" \
  || check "T1.ledger_copy_written" FAIL "missing or wrong length"
if [ -f "$ROOT/expected.json" ]; then
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$ROOT/expected.json" "$ROOT" <<'PY' && check "T1.substituted_expected_json" PASS "valid, placeholder-free, paths under root" || check "T1.substituted_expected_json" FAIL "python check failed"
import json, sys
doc = json.load(open(sys.argv[1]))
root = sys.argv[2]
raw = open(sys.argv[1]).read()
assert "@FIXTURE_ROOT@" not in raw, "placeholder left in substituted copy"
assert doc["expect"][0]["verdict"] == "VERIFIED"
assert doc["expect"][0]["receipt"] == "moved-to-obsidian"
assert doc["targets"][0] == root + "/source/note.md"
PY
  else
    check "T1.substituted_expected_json" FAIL "python3 unavailable"
  fi
else
  check "T1.substituted_expected_json" FAIL "no <ROOT>/expected.json"
fi

# ledger row matches both sides
if [ -f "$ROOT/ledger.tsv" ]; then
  ROW="$(sed -n '2p' "$ROOT/ledger.tsv")"
  IFS=$'\t' read -r r_sp r_ss r_vp r_vs _r_at _r_note <<< "$ROW"
  [ "$r_sp" = "$SRC" ] && [ "$r_vp" = "$VLT" ] && [ "$r_ss" = "$SHA_NOTE" ] && [ "$r_vs" = "$SHA_NOTE" ] \
    && check "T1.row_four_conjuncts" PASS "sp/ss/vp/vs all match" \
    || check "T1.row_four_conjuncts" FAIL "sp=$r_sp ss=$r_ss vp=$r_vp vs=$r_vs"
else
  check "T1.row_four_conjuncts" FAIL "no ledger"
fi

# ---------------------------------------------------- T2 r2-tool crosscheck
if [ -f "$TOOL" ]; then
  ARMED="$(env SOUJI_LEDGER="$ROOT/ledger.tsv" bash "$TOOL" "$SRC" 2>/dev/null | head -1)"
  printf '%s' "$ARMED" | grep -qE '	SAFE	moved-to-obsidian	' \
    && check "T2.armed_safe_moved" PASS "$ARMED" \
    || check "T2.armed_safe_moved" FAIL "$ARMED"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$WORK/empty-ledger.tsv"
  DISARMED="$(env SOUJI_LEDGER="$WORK/empty-ledger.tsv" bash "$TOOL" "$SRC" 2>/dev/null | head -1)"
  printf '%s' "$DISARMED" | grep -qE '	NOT-SAFE	' \
    && check "T2.disarmed_not_safe" PASS "$DISARMED" \
    || check "T2.disarmed_not_safe" FAIL "$DISARMED"
else
  check "T2.armed_safe_moved" FAIL "tool missing: $TOOL"
  check "T2.disarmed_not_safe" FAIL "tool missing: $TOOL"
fi

# ------------------------------------------------------- T3 conjunct negatives
NEG="$WORK/neg"
# A: vault copy corrupted AFTER the row was written -> vault-sha-mismatch
rm -rf "$NEG"; bash "$MAKER" --out "$NEG" --skip-ledger --quiet >/dev/null 2>&1
chmod u+w "$NEG/vault/note.md" 2>/dev/null
printf 'corrupt\n' >> "$NEG/vault/note.md"
{ printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'; bash "$MAKER" --print-row --out "$NEG"; } > "$WORK/negA.tsv"
LINEA="$(env SOUJI_LEDGER="$WORK/negA.tsv" bash "$TOOL" "$NEG/source/note.md" 2>/dev/null | head -1)"
printf '%s' "$LINEA" | grep -q 'vault-sha-mismatch' \
  && check "T3.vault_hash_conjunct" PASS "$LINEA" || check "T3.vault_hash_conjunct" FAIL "$LINEA"
# B: source edited AFTER the row was written -> source-sha-mismatch
rm -rf "$NEG"; bash "$MAKER" --out "$NEG" --skip-ledger --quiet >/dev/null 2>&1
{ printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'; bash "$MAKER" --print-row --out "$NEG"; } > "$WORK/negB.tsv"
printf 'edited\n' >> "$NEG/source/note.md"
LINEB="$(env SOUJI_LEDGER="$WORK/negB.tsv" bash "$TOOL" "$NEG/source/note.md" 2>/dev/null | head -1)"
printf '%s' "$LINEB" | grep -q 'source-sha-mismatch' \
  && check "T3.source_hash_conjunct" PASS "$LINEB" || check "T3.source_hash_conjunct" FAIL "$LINEB"
# C: vault file removed -> vault-unreachable
rm -rf "$NEG"; bash "$MAKER" --out "$NEG" --skip-ledger --quiet >/dev/null 2>&1
rm -f "$NEG/vault/note.md"
{ printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'; bash "$MAKER" --print-row --out "$NEG"; } > "$WORK/negC.tsv"
LINEC="$(env SOUJI_LEDGER="$WORK/negC.tsv" bash "$TOOL" "$NEG/source/note.md" 2>/dev/null | head -1)"
printf '%s' "$LINEC" | grep -q 'vault-unreachable' \
  && check "T3.vault_presence_conjunct" PASS "$LINEC" || check "T3.vault_presence_conjunct" FAIL "$LINEC"

# ------------------------------------------------------------- T4 determinism
D_A="$WORK/det-a"; D_B="$WORK/det-b"
bash "$MAKER" --out "$D_A" --skip-ledger --quiet >/dev/null 2>&1
bash "$MAKER" --out "$D_B" --skip-ledger --quiet >/dev/null 2>&1
cmp -s "$D_A/source/note.md" "$D_B/source/note.md" && [ "$(sha "$D_A/vault/note.md")" = "$(sha "$D_B/vault/note.md")" ] \
  && check "T4.determinism_two_roots" PASS "byte-identical" \
  || check "T4.determinism_two_roots" FAIL "builds differ"
bash "$MAKER" --out "$D_A" --skip-ledger --quiet >/dev/null 2>&1 \
  && check "T4.marker_rebuild" PASS "exit 0" || check "T4.marker_rebuild" FAIL "rc=$?"
mkdir -p "$WORK/refuse" && touch "$WORK/refuse/x"
bash "$MAKER" --out "$WORK/refuse" >/dev/null 2>&1; RRC=$?
[ "$RRC" = 2 ] && check "T4.refuse_non_marker_dir" PASS "exit 2" || check "T4.refuse_non_marker_dir" FAIL "exit=$RRC"

# --------------------------------------------------- T5 live ledger untouched
LIVE_SHA_AFTER="$(sha "$LIVE_LEDGER" 2>/dev/null || echo missing)"
LIVE_LINES_AFTER="$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ' || echo 0)"
[ "$LIVE_SHA_BEFORE" = "$LIVE_SHA_AFTER" ] && [ "$LIVE_LINES_AFTER" = "$LIVE_LINES_BEFORE" ] && [ "$LIVE_LINES_AFTER" = 1 ] \
  && check "T5.live_ledger_untouched_header_only" PASS "sha=$LIVE_SHA_AFTER lines=1" \
  || check "T5.live_ledger_untouched_header_only" FAIL "before=$LIVE_SHA_BEFORE/$LIVE_LINES_BEFORE after=$LIVE_SHA_AFTER/$LIVE_LINES_AFTER"

# ------------------------------------------------------------------- emit
TOTAL=$((pass_n+fail_n))
{
  printf '{\n "case": "case-V1",\n "fixture_root": "%s",\n "pass": %s,\n "fail": %s,\n "results": [\n' \
    "$ROOT" "$pass_n" "$fail_n"
  first=1
  while IFS=$'\t' read -r status id detail; do
    [ "$first" = 1 ] || printf ',\n'; first=0
    esc=${detail//\\/\\\\}; esc=${esc//\"/\\\"}; esc=${esc//$'\t'/\\t}
    printf '  {"status": "%s", "check": "%s", "detail": "%s"}' "$status" "$id" "$esc"
  done < "$RTSV"
  printf '\n ]\n}\n'
} > "$OUT.tmp.$$"
mv -f "$OUT.tmp.$$" "$OUT"

if [ "$fail_n" = 0 ]; then
  printf 'SELFTEST PASS pass=%s fail=%s -> %s\n' "$pass_n" "$fail_n" "$OUT"
  exit 0
fi
printf 'SELFTEST FAIL pass=%s fail=%s -> %s\n' "$pass_n" "$fail_n" "$OUT" >&2
exit 1
