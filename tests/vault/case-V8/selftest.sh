#!/usr/bin/env bash
# case-V8 selftest — seat S16, souji-shokunin round 4.
#
# Builds the case-V8 fixture in a fresh mktemp dir, asserts the fixture
# invariants (space-bearing basenames, pinned sha256 constants, TAB-columned
# ledger row with literal spaces), then runs the installed r2 tool
# tools/souji-verify.sh against the target:
#   armed   (per-case ledger)        -> SAFE + moved-to-obsidian
#   disarmed (header-only ledger)    -> NOT-SAFE (the row is the receipt)
#   control (space-bearing pair, no row, armed ledger) -> NOT-SAFE
#
# Read-only over the lane and the real vault: writes only under /tmp.
# usage: selftest.sh [--tool PATH] [--keep]
# exit: 0 all checks pass; 1 any check failed; 2 usage; 3 tool missing
set -uo pipefail
export LC_ALL=C

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LANE_ROOT="$(cd -- "$HERE/../../.." && pwd)"
TOOL="$LANE_ROOT/tools/souji-verify.sh"
KEEP=0
while [ $# -gt 0 ]; do
  case "$1" in
    --tool) [ $# -ge 2 ] || { echo "selftest: --tool needs a value" >&2; exit 2; }; TOOL=$2; shift 2 ;;
    --keep) KEEP=1; shift ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "selftest: unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -f "$TOOL" ] || { echo "selftest: tool missing: $TOOL" >&2; exit 3; }

WORK=$(mktemp -d "${TMPDIR:-/tmp}/souji-v8-selftest.XXXXXX")
cleanup() { [ "$KEEP" = 1 ] || rm -rf -- "$WORK"; }
trap cleanup EXIT

PASS=0 FAIL=0
ok()   { PASS=$((PASS+1)); printf 'PASS %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf 'FAIL %s: %s\n' "$1" "$2"; }
check() { # id, condition-rc, detail
  if [ "$2" -eq 0 ]; then ok "$1"; else bad "$1" "$3"; fi
}

# --- build -------------------------------------------------------------------
BUILD_OUT=$(bash "$HERE/make-fixture.sh" --out "$WORK/fx" --ledger "$WORK/ledger-V8.tsv" 2>"$WORK/build.err")
BUILD_RC=$?
check "build.exit0" "$BUILD_RC" "builder rc=$BUILD_RC; stderr: $(tail -3 "$WORK/build.err" | tr '\n' ' ')"
[ "$BUILD_RC" -eq 0 ] || { printf 'selftest: build failed; work kept at %s\n' "$WORK" >&2; KEEP=1; exit 1; }

ROOT=$(printf '%s\n' "$BUILD_OUT" | sed -n 's/^FIXTURE_READY V8 //p')
check "build.ready-line" "$([ -n "$ROOT" ] && [ -d "$ROOT" ] && echo 0 || echo 1)" "no FIXTURE_READY V8 <ROOT> directory line: $BUILD_OUT"
[ -n "$ROOT" ] && [ -d "$ROOT" ] || exit 1

SRC="$ROOT/source/meeting notes 2026-10.md"
VLT="$ROOT/vault/Meeting Notes 2026-10.md"
CTL_SRC="$ROOT/source/control notes.md"
CTL_VLT="$ROOT/vault/Control Notes.md"
SHA_NOTE="2fc29f1f563835d0e66139afa269b4de51355859ed30232b41847a2862f1084e"
SHA_CTL="3f5d8d2f08280a356f765ef393a762ac8bf93d423103b569347a12ad50ee1ab1"
LEDGER="$WORK/ledger-V8.tsv"

sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

# --- fixture invariants ------------------------------------------------------
[ -f "$SRC" ] && [ -f "$VLT" ] && [ -f "$CTL_SRC" ] && [ -f "$CTL_VLT" ]
check "fixture.files-exist" $? "one of the space-bearing files is missing"
for f in "$SRC" "$VLT" "$CTL_SRC" "$CTL_VLT"; do
  case "$(basename -- "$f")" in *" "*) : ;; *) bad "fixture.basename-space" "no space in $(basename -- "$f")"; ;; esac
done
ok "fixture.basename-space (all four)"
[ "$(sha "$SRC")" = "$SHA_NOTE" ] && [ "$(sha "$VLT")" = "$SHA_NOTE" ]
check "fixture.sha256-target" $? "target pair hash != $SHA_NOTE (src=$(sha "$SRC") vlt=$(sha "$VLT"))"
[ "$(sha "$CTL_SRC")" = "$SHA_CTL" ] && [ "$(sha "$CTL_VLT")" = "$SHA_CTL" ]
check "fixture.sha256-control" $? "control pair hash != $SHA_CTL"
cmp -s -- "$SRC" "$VLT"; check "fixture.pair-identical" $? "source and vault copies differ"
[ "$(stat -c %a -- "$VLT")" = "444" ]; check "fixture.vault-mode-0444" $? "vault file mode is $(stat -c %a -- "$VLT")"

# ledger: header + exactly one row, 6 TAB fields, both path fields with spaces
[ "$(head -1 "$LEDGER")" = "$(printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote')" ]
check "ledger.header" $? "ledger header row missing/malformed"
[ "$(wc -l < "$LEDGER" | tr -d ' ')" = "2" ]
check "ledger.one-row" $? "ledger line count is $(wc -l < "$LEDGER" | tr -d ' ') (want 2: header + 1 row)"
ROW=$(sed -n 2p "$LEDGER")
[ "$(printf '%s' "$ROW" | awk -F'\t' 'NF==6' | wc -l | tr -d ' ')" = "1" ]
check "ledger.six-tab-columns" $? "row does not have exactly 6 TAB-separated fields"
[ "$(printf '%s' "$ROW" | cut -f1)" = "$SRC" ] && [ "$(printf '%s' "$ROW" | cut -f3)" = "$VLT" ]
check "ledger.path-columns-space-exact" $? "row path fields != target paths (field1='$(printf '%s' "$ROW" | cut -f1)')"

# --- r2 tool, armed ----------------------------------------------------------
run_tool() { # ledger target -> stdout line on fd1
  env SOUJI_LEDGER="$1" bash "$TOOL" --stale-days 1 -- "$2" 2>/dev/null
}
LINE=$(run_tool "$LEDGER" "$SRC" | grep -a "	$SRC	" | head -1)
[ -n "$LINE" ] && [ "$(printf '%s' "$LINE" | awk -F'\t' '{print $3}')" = "SAFE" ] \
  && [ "$(printf '%s' "$LINE" | awk -F'\t' '{print $4}')" = "moved-to-obsidian" ]
check "armed.target-SAFE-moved" $? "armed line: ${LINE:-<none>}"

# --- r2 tool, disarmed (header-only ledger) ---------------------------------
HDR_ONLY="$WORK/ledger-header-only.tsv"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$HDR_ONLY"
LINE=$(run_tool "$HDR_ONLY" "$SRC" | grep -a "	$SRC	" | head -1)
[ -n "$LINE" ] && [ "$(printf '%s' "$LINE" | awk -F'\t' '{print $3}')" = "NOT-SAFE" ]
check "disarmed.target-NOT-SAFE" $? "disarmed line: ${LINE:-<none>}"

# --- r2 tool, armed, auxiliary control (no row) ------------------------------
LINE=$(run_tool "$LEDGER" "$CTL_SRC" | grep -a "	$CTL_SRC	" | head -1)
[ -n "$LINE" ] && [ "$(printf '%s' "$LINE" | awk -F'\t' '{print $3}')" = "NOT-SAFE" ]
check "armed.control-NOT-SAFE" $? "control line: ${LINE:-<none>}"

# --- live ledger untouched ---------------------------------------------------
LIVE="$LANE_ROOT/corpus/knowledge/obsidian-ledger.tsv"
[ "$(wc -l < "$LIVE" | tr -d ' ')" = "1" ]
check "live-ledger.header-only" $? "live ledger has $(wc -l < "$LIVE" | tr -d ' ') lines (want 1)"

printf 'SELFTEST %s: pass=%s fail=%s\n' "$([ "$FAIL" -eq 0 ] && echo PASS || echo FAIL)" "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
