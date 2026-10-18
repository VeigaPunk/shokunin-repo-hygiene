#!/usr/bin/env bash
# tests/vault/case-V6/selftest.sh — assertions for case-V6 (CRLF ledger fixture).
#
# Builds the fixture in both modes (in-place default for the runner-28 probes[]
# loader, --out for runner-26/29), then checks the fixture invariants and the
# CRLF-handling verdicts against the tool under test (default:
# tools/souji-verify.sh, the round-2 artifact; --tool PATH points at an r4
# candidate such as tools/souji-vault-verify.sh).
#
# The r2 tool speaks SAFE/NOT-SAFE; r4 candidates speak VERIFIED/NOT-VERIFIED.
# Assertions are class-agnostic: the verdict class must be the verified side
# (SAFE or VERIFIED) / the unverified side (NOT-SAFE or NOT-VERIFIED), and the
# receipt/evidence tokens are checked verbatim.
#
# usage: selftest.sh [--tool PATH] [--out JSON] [--keep]
#   --tool PATH   tool under test (default <lane>/tools/souji-verify.sh)
#   --out JSON    result file (default <lane>/tests/results/v6-selftest.json)
#   --keep        keep the scratch dir (default: removed)
# exit: 0 all checks pass | 1 any check failed | 2 usage
set -uo pipefail
export LC_ALL=C

SELF="${BASH_SOURCE[0]}"
HERE="$(cd -- "$(dirname -- "$SELF")" && pwd -P)"
LANE="$(cd -- "$HERE/../../.." && pwd -P)"
TOOL="$LANE/tools/souji-verify.sh"
OUT="$LANE/tests/results/v6-selftest.json"
KEEP=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --tool) [ "$#" -ge 2 ] || { echo "$SELF: --tool needs a value" >&2; exit 2; }; TOOL=$2; shift 2 ;;
    --out)  [ "$#" -ge 2 ] || { echo "$SELF: --out needs a value" >&2; exit 2; }; OUT=$2; shift 2 ;;
    --keep) KEEP=1; shift ;;
    -h|--help) sed -n '2,18p' "$SELF"; exit 0 ;;
    *) echo "$SELF: unknown arg $1" >&2; exit 2 ;;
  esac
done

[ -f "$TOOL" ] || { echo "$SELF: tool not found: $TOOL" >&2; exit 2; }

TMP="$(mktemp -d "${TMPDIR:-/tmp}/case-V6-selftest.XXXXXX")"
ROOT="$TMP/root"
SCRATCH_LEDGER="$TMP/ledger-V6.tsv"
cleanup() { [ "$KEEP" = 1 ] || rm -rf "$TMP"; }
trap cleanup EXIT

PASS=0; FAIL=0
declare -a NOTES=()
note() { printf '%s\n' "$*"; NOTES+=("$*"); }
ok()   { PASS=$((PASS+1)); note "PASS $1${2:+ $2}"; }
bad()  { FAIL=$((FAIL+1)); note "FAIL $1${2:+ $2}"; }

LIVE_LEDGER="$LANE/corpus/knowledge/obsidian-ledger.tsv"
LIVE_SHA_BEFORE="$(sha256sum -- "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1 || echo missing)"
LIVE_LINES_BEFORE="$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ' || echo 0)"
TEMPLATE_SHA_BEFORE="$(sha256sum -- "$HERE/expected.json" | cut -d' ' -f1)"

# ---- T1: builder (--out mode) ---------------------------------------------
build_out="$(bash "$HERE/make-fixture.sh" --out "$ROOT" --ledger "$SCRATCH_LEDGER" --quiet 2>&1)"
build_rc=$?
if [ "$build_rc" -eq 0 ] && [ -e "$ROOT/.case-V6-fixture" ] \
   && [ -f "$ROOT/src/payload.md" ] && [ -f "$ROOT/vault/payload.md" ] \
   && [ -f "$ROOT/ledger-crlf.tsv" ] && [ -f "$ROOT/ledger-lf-control.tsv" ] \
   && [ -f "$ROOT/ledger-crlf-truncated.tsv" ] && [ -f "$ROOT/ledger.tsv" ] \
   && [ -f "$ROOT/expected.json" ]; then
  ok T1 "builder --out rc=0, fixture files present (root=$ROOT)"
else
  bad T1 "builder --out rc=$build_rc; out=$(printf '%s' "$build_out" | head -c 300)"
fi

crlf="$ROOT/ledger-crlf.tsv" lf="$ROOT/ledger-lf-control.tsv" trunc="$ROOT/ledger-crlf-truncated.tsv"
cr_count() { tr -cd '\r' < "$1" | wc -c | tr -d ' '; }
line_count() { wc -l < "$1" | tr -d ' '; }
cr_ended() { grep -c $'\r$' "$1" || true; }

# ---- T2/T3/T4: byte invariants -------------------------------------------
if [ "$(cr_count "$crlf")" -eq 2 ] && [ "$(line_count "$crlf")" -eq 2 ] && [ "$(cr_ended "$crlf")" -eq 2 ]; then
  ok T2 "CRLF ledger: CR=2 lines=2, every line ends CR LF"
else
  bad T2 "CRLF ledger invariant broken: CR=$(cr_count "$crlf") lines=$(line_count "$crlf") cr-ended=$(cr_ended "$crlf")"
fi
if [ "$(cr_count "$lf")" -eq 0 ] && [ "$(line_count "$lf")" -eq 2 ]; then
  ok T3 "LF control: CR=0 lines=2"
else
  bad T3 "LF control carries CR=$(cr_count "$lf") lines=$(line_count "$lf")"
fi
if [ "$(cr_count "$trunc")" -eq 2 ] && [ "$(awk -F'\t' 'END{print NF}' "$trunc")" -eq 4 ] && [ "$(awk -F'\t' 'END{print NF}' "$crlf")" -eq 6 ]; then
  ok T4 "truncated ledger: CR=2, 4 columns (CRLF row: 6 columns)"
else
  bad T4 "truncated ledger shape wrong: CR=$(cr_count "$trunc") NF=$(awk -F'\t' 'END{print NF}' "$trunc")"
fi

# ---- verdict helpers -------------------------------------------------------
class_of() { # stdin: one output line -> verified|unverified|?
  local line cls
  line="$(head -1)"
  case "$line" in
    VERDICT*) cls="$(printf '%s' "$line" | awk -F'\t' '{print $3}')" ;;
    *) cls="${line%%[[:space:]]*}" ;;
  esac
  case "$cls" in
    SAFE|VERIFIED) printf 'verified\n' ;;
    NOT-SAFE|NOT-VERIFIED) printf 'unverified\n' ;;
    *) printf '?\n' ;;
  esac
}

run_tool() { # $1 ledger, $2 target -> stdout
  SOUJI_LEDGER="$1" "$TOOL" "$2" 2>&1
}

# ---- T5: CRLF ledger, valid row -> verified side, moved-to-obsidian --------
out_crlf="$(run_tool "$crlf" "$ROOT/src/payload.md")"
cls_crlf="$(printf '%s\n' "$out_crlf" | class_of)"
if [ "$cls_crlf" = verified ] && printf '%s' "$out_crlf" | grep -q 'moved-to-obsidian' && printf '%s' "$out_crlf" | grep -q 'ledger-row'; then
  ok T5 "CRLF valid row -> verified side with moved-to-obsidian receipt"
else
  bad T5 "CRLF row not verified: class=$cls_crlf out=$(printf '%s' "$out_crlf" | head -c 300)"
fi

# ---- T6: LF control output byte-identical to CRLF output -------------------
out_lf="$(run_tool "$lf" "$ROOT/src/payload.md")"
if [ "$out_crlf" = "$out_lf" ]; then
  ok T6 "CRLF vs LF control output byte-identical"
else
  bad T6 "CRLF and LF outputs differ: crlf=$(printf '%s' "$out_crlf" | head -c 200) lf=$(printf '%s' "$out_lf" | head -c 200)"
fi

# ---- T7: truncated CRLF row -> unverified side, sha mismatch evidence ------
out_tr="$(run_tool "$trunc" "$ROOT/src/payload.md")"
cls_tr="$(printf '%s\n' "$out_tr" | class_of)"
if [ "$cls_tr" = unverified ] && printf '%s' "$out_tr" | grep -q 'vault-sha-mismatch'; then
  ok T7 "truncated CRLF row -> unverified side with vault-sha-mismatch"
else
  bad T7 "truncated row verdict wrong: class=$cls_tr out=$(printf '%s' "$out_tr" | head -c 300)"
fi

# ---- T8: disarmed (header-only ledger) -> unverified, no receipt -----------
EMPTY_LEDGER="$TMP/ledger-empty.tsv"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$EMPTY_LEDGER"
out_empty="$(run_tool "$EMPTY_LEDGER" "$ROOT/src/payload.md")"
cls_empty="$(printf '%s\n' "$out_empty" | class_of)"
if [ "$cls_empty" = unverified ] && ! printf '%s' "$out_empty" | grep -q 'moved-to-obsidian'; then
  ok T8 "disarmed: header-only ledger -> unverified side, no moved-to-obsidian"
else
  bad T8 "disarmed ledger verdict wrong: class=$cls_empty out=$(printf '%s' "$out_empty" | head -c 300)"
fi

# ---- T9: live ledger untouched ---------------------------------------------
LIVE_SHA_AFTER="$(sha256sum -- "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1 || echo missing)"
LIVE_LINES_AFTER="$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ' || echo 0)"
if [ "$LIVE_SHA_BEFORE" = "$LIVE_SHA_AFTER" ] && [ "$LIVE_LINES_AFTER" -eq 1 ]; then
  ok T9 "live ledger untouched (sha $LIVE_SHA_AFTER, header-only)"
else
  bad T9 "live ledger changed: before=$LIVE_SHA_BEFORE after=$LIVE_SHA_AFTER lines=$LIVE_LINES_AFTER"
fi

# ---- T10: idempotent rebuild on the same --out -----------------------------
sha1_payload="$(sha256sum -- "$ROOT/src/payload.md" | cut -d' ' -f1)"
sha1_ledger="$(sha256sum -- "$crlf" | cut -d' ' -f1)"
rebuild_out="$(bash "$HERE/make-fixture.sh" --out "$ROOT" --ledger "$SCRATCH_LEDGER" --quiet 2>&1)"
rebuild_rc=$?
sha2_payload="$(sha256sum -- "$ROOT/src/payload.md" | cut -d' ' -f1)"
sha2_ledger="$(sha256sum -- "$crlf" | cut -d' ' -f1)"
if [ "$rebuild_rc" -eq 0 ] && [ "$sha1_payload" = "$sha2_payload" ] && [ "$sha1_ledger" = "$sha2_ledger" ]; then
  ok T10 "rebuild on same --out byte-identical (payload=$sha2_payload)"
else
  bad T10 "rebuild not idempotent: rc=$rebuild_rc payload $sha1_payload -> $sha2_payload ledger $sha1_ledger -> $sha2_ledger"
fi

# ---- T11: in-place (default) mode — the runner-28 probes[] contract --------
def_out="$(bash "$HERE/make-fixture.sh" --quiet 2>&1)"
def_root="$(printf '%s\n' "$def_out" | awk -F= '/^FIXTURE_ROOT=/{print $2; exit}')"
if [ "$def_root" = "$HERE" ] \
   && [ -f "$HERE/src/payload.md" ] && [ -f "$HERE/vault/payload.md" ] \
   && [ -f "$HERE/ledger-crlf.tsv" ] && [ -f "$HERE/ledger-lf-control.tsv" ] \
   && [ -f "$HERE/ledger-crlf-truncated.tsv" ] && [ -f "$HERE/ledger.tsv" ]; then
  ok T11 "in-place default mode materializes the case dir (root=$HERE)"
else
  bad T11 "in-place default mode broken: root=$def_root"
fi

# ---- T12: tracked expected.json template untouched by either mode ----------
TEMPLATE_SHA_AFTER="$(sha256sum -- "$HERE/expected.json" | cut -d' ' -f1)"
if [ "$TEMPLATE_SHA_BEFORE" = "$TEMPLATE_SHA_AFTER" ] && grep -q '@FIXTURE_ROOT@' "$HERE/expected.json" \
   && grep -q 'souji-vault-fixture/1' "$HERE/expected.json" \
   && grep -q '"probes"' "$HERE/expected.json" \
   && grep -q 'ledger-crlf.tsv' "$HERE/expected.json"; then
  ok T12 "tracked expected.json template unchanged and still declares schema + probes + @FIXTURE_ROOT@"
else
  bad T12 "tracked expected.json changed or malformed (before=$TEMPLATE_SHA_BEFORE after=$TEMPLATE_SHA_AFTER)"
fi

# ---- T13: --out root expected.json substituted -----------------------------
if [ -f "$ROOT/expected.json" ] && ! grep -q '@FIXTURE_ROOT@' "$ROOT/expected.json" \
   && grep -q "$ROOT" "$ROOT/expected.json" && grep -q '"probes"' "$ROOT/expected.json"; then
  ok T13 "--out root expected.json substituted with root paths"
else
  bad T13 "--out root expected.json wrong (missing, unsubstituted, or lacking probes)"
fi

# ---- T14: probes[] ledgers resolve under BOTH roots ------------------------
probe_ok=1
for rel in ledger-crlf.tsv ledger-lf-control.tsv ledger-crlf-truncated.tsv; do
  [ -f "$ROOT/$rel" ] || probe_ok=0
  [ -f "$HERE/$rel" ] || probe_ok=0
done
if [ "$probe_ok" = 1 ]; then
  ok T14 "all three probe ledgers exist under --out root and case dir"
else
  bad T14 "probe ledger missing under one of the roots"
fi

# ---- T15: tool sha recorded ------------------------------------------------
TOOL_SHA="$(sha256sum -- "$TOOL" | cut -d' ' -f1)"
note "tool=$TOOL sha256=$TOOL_SHA"

# ---- emit JSON -------------------------------------------------------------
mkdir -p -- "$(dirname -- "$OUT")"
jesc() { local s=$1; s=${s//\\/\\\\}; s=${s//\"/\\\"}; s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}; printf '%s' "$s"; }
{
  printf '{\n'
  printf '  "case": "case-V6",\n'
  printf '  "name": "ledger-crlf-line-endings",\n'
  printf '  "generated_at": "%s",\n' "$(date -Iseconds)"
  printf '  "tool": "%s",\n' "$TOOL"
  printf '  "tool_sha256": "%s",\n' "$TOOL_SHA"
  printf '  "fixture_root_out": "%s",\n' "$ROOT"
  printf '  "fixture_root_inplace": "%s",\n' "$HERE"
  printf '  "live_ledger_sha256": "%s",\n' "$LIVE_SHA_AFTER"
  printf '  "live_ledger_header_only": %s,\n' "$([ "$LIVE_LINES_AFTER" -eq 1 ] && printf true || printf false)"
  printf '  "observed": {\n'
  printf '    "crlf_ledger_line": "%s",\n' "$(jesc "$(printf '%s' "$out_crlf" | head -1)")"
  printf '    "lf_control_line": "%s",\n' "$(jesc "$(printf '%s' "$out_lf" | head -1)")"
  printf '    "crlf_truncated_line": "%s",\n' "$(jesc "$(printf '%s' "$out_tr" | head -1)")"
  printf '    "disarmed_line": "%s"\n' "$(jesc "$(printf '%s' "$out_empty" | head -1)")"
  printf '  },\n'
  printf '  "checks": [\n'
  first=1
  for n in "${NOTES[@]}"; do
    [ "$first" = 1 ] || printf ',\n'
    first=0
    printf '    "%s"' "$(jesc "$n")"
  done
  printf '\n  ],\n'
  printf '  "pass": %s,\n  "fail": %s,\n' "$PASS" "$FAIL"
  printf '  "verdict": "%s"\n' "$([ "$FAIL" -eq 0 ] && printf 'SELFTEST PASS' || printf 'SELFTEST FAIL')"
  printf '}\n'
} > "$OUT"

printf '%s\n' "---"
printf 'case-V6 selftest: pass=%s fail=%s -> %s\n' "$PASS" "$FAIL" "$OUT"
[ "$FAIL" -eq 0 ] || exit 1
printf 'SELFTEST PASS\n'
exit 0
