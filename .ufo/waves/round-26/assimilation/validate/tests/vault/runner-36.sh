#!/usr/bin/env bash
# runner-36.sh — round-4 vault-verification runner (SEAT S36, "identical" runner).
#
# Twin of tests/vault/runner-35.sh: check IDs V1..V13b / A0..A6 / C1..C11 are
# deliberately identical so the parent can diff vrun-35.json vs vrun-36.json.
# Additive differences, each documented in the report's method block:
#   (1) the S35 template's duplicated `assert_line selftest.exit` call is not
#       copied (it could only ever record a spurious fail for an empty target);
#       the plain exit check from the fixed runner-35.sh on disk is used;
#   (2) --wait SECS waits (bounded) for a round-4 candidate tool to appear;
#   (3) tool selection prefers tools/souji-vault-verify.sh, then the S35 chain;
#   (4) if tools/souji-vault-verify.impl-*.sh exist, a compact per-impl matrix
#       (selftest + V1..V4) is run and emitted as aggregator rows;
#   (5) seat-specific probes S1..S7 (S1..S5 mirror S35; S6 index-scale and
#       S7 live-app context are S36 additions).
#
# Independent by construction: builds its OWN fixtures under
# tests/vault/fixture-*-36/ and a test ledger at tests/vault/vrun-36-ledger.tsv;
# never consumes tests/fixtures/** or any other seat's ledger.
#
# What it verifies (round 4: Obsidian-CLI vault verification):
#   1. ledger-backed moved-to-obsidian receipts of the tool under test, on
#      fixture vault rows (match / edited-after-row / source-mismatch /
#      vault-absent);
#   2. the same receipt path against the REAL vault
#      (/home/vgpnk/Documents/shokoknowledge) — read-only: the vault-side
#      sha256 must be confirmed by the tool, and a deliberately wrong
#      vault hash must NOT yield SAFE;
#   3. the real vault is untouched by the whole battery (sha256 manifest
#      of every vault file before vs after; .obsidian/** excluded because the
#      desktop app is live and writes its own workspace files);
#   4. the live ledger corpus/knowledge/obsidian-ledger.tsv stays
#      header-only;
#   5. CLI entry-point probe: obsidian-cli-inspector (timeout 5, help and
#      --version only). The GUI launcher /usr/bin/obsidian is NEVER
#      executed — stat/grep/pgrep evidence only.
#
# usage: tests/vault/runner-36.sh [--seat N] [--tool PATH] [--results PATH]
#                                 [--vault PATH] [--wait SECS] [--keep]
#   --seat N    seat number (default 36) — suffixes fixtures and output name
#   --tool      tool under test; default: first existing of
#               tools/souji-vault-verify.sh, tools/obsidian-vault-verify.sh,
#               tools/vault-verify.sh, tools/souji-verify.sh
#   --results   JSON report path (default <lane>/tests/results/vrun-<seat>.json)
#   --vault     real vault path (default /home/vgpnk/Documents/shokoknowledge)
#   --wait      seconds to wait for a candidate tool (default 0)
#   --keep      keep the mktemp scratch dir (default: removed)
# exit: 0 all checks pass | 1 any counted check failed | 2 usage | 3 tool missing
set -euo pipefail
export LC_ALL=C

SELF_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$SELF_DIR/../.." && pwd)       # lane repo root (tests/vault -> lane)
SEAT=36
TOOL=""
RESULTS=""
VAULT="/home/vgpnk/Documents/shokoknowledge"
WAIT=0
KEEP=0
TOOL_TIMEOUT=120

die_usage() { printf 'runner-36.sh: %s\n' "$1" >&2; exit 2; }
while [ $# -gt 0 ]; do
  case "$1" in
    --seat)    [ $# -ge 2 ] || die_usage "--seat needs a value"; SEAT=$2; shift 2;;
    --tool)    [ $# -ge 2 ] || die_usage "--tool needs a value"; TOOL=$2; shift 2;;
    --results) [ $# -ge 2 ] || die_usage "--results needs a value"; RESULTS=$2; shift 2;;
    --vault)   [ $# -ge 2 ] || die_usage "--vault needs a value"; VAULT=$2; shift 2;;
    --wait)    [ $# -ge 2 ] || die_usage "--wait needs a value"; WAIT=$2; shift 2;;
    --keep)    KEEP=1; shift;;
    -h|--help) sed -n '2,52p' "$0"; exit 0;;
    *) die_usage "unknown argument: $1";;
  esac
done

pick_tool() {
  local cand
  for cand in "$ROOT/tools/souji-vault-verify.sh" "$ROOT/tools/obsidian-vault-verify.sh" \
              "$ROOT/tools/vault-verify.sh" "$ROOT/tools/souji-verify.sh"; do
    [ -f "$cand" ] && { printf '%s\n' "$cand"; return 0; }
  done
  return 1
}
if [ -z "$TOOL" ]; then
  WAIT_START=$(date +%s)
  while :; do
    TOOL=$(pick_tool || true)
    [ -n "$TOOL" ] && break
    now=$(date +%s)
    [ $(( now - WAIT_START )) -ge "$WAIT" ] && break
    sleep 10
  done
fi
[ -n "$TOOL" ] || { printf 'runner-36.sh: no tool found under tools/\n' >&2; exit 3; }
[ -z "$RESULTS" ] && RESULTS="$ROOT/tests/results/vrun-$SEAT.json"

WORK=$(mktemp -d /tmp/souji36-vault.XXXXXX)
case "$WORK" in /tmp/souji36-vault.*) : ;; *) echo "refusing: WORK=$WORK" >&2; exit 9;; esac
BK="$WORK/.runner"; mkdir -p "$BK"
cleanup() { [ "$KEEP" = 1 ] || rm -rf "$WORK"; }
trap cleanup EXIT

RTSV="$BK/results.tsv"; : > "$RTSV"
san_field() { local s=${1:-}; s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; printf '%s' "$s"; }
record() { # id name status expected observed exit detail
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(san_field "$1")" "$(san_field "$2")" "$(san_field "$3")" "$(san_field "$4")" \
    "$(san_field "$5")" "$(san_field "${6:-}")" "$(san_field "${7:-}")" >> "$RTSV"
}
note() { record "$1" "$2" info "$3" "" "" "${4:-}"; }
info_kv() { record "$1" "$2" info "" "" "" "$3"; }

# ------------------------------------------------------------------ fixtures
FXVAULT="$ROOT/tests/vault/fixture-vault-$SEAT"    # fixture vault (ledger target side)
FXSRC="$ROOT/tests/vault/fixture-src-$SEAT"        # source copies (removal target side)
LEDGER="$ROOT/tests/vault/vrun-$SEAT-ledger.tsv"
rm -rf "$FXVAULT" "$FXSRC"
mkdir -p "$FXVAULT" "$FXSRC"

payload_kept() { printf 'vrun-%s fixture payload: ledger-matched artifact\n' "$SEAT"; }
payload_stale() { printf 'vrun-%s fixture: vault copy edited after the row was written\n' "$SEAT"; }
payload_mis() { printf 'vrun-%s fixture: source sha mismatch row\n' "$SEAT"; }

SP_KEPT="$FXSRC/kept-$SEAT.md";   VP_KEPT="$FXVAULT/kept-$SEAT.md"
payload_kept > "$SP_KEPT";        cp "$SP_KEPT" "$VP_KEPT"
SHA_KEPT=$(sha256sum "$SP_KEPT" | cut -d' ' -f1)

SP_STALE="$FXSRC/stale-row-$SEAT.md"; VP_STALE="$FXVAULT/stale-row-$SEAT.md"
payload_stale > "$SP_STALE";          cp "$SP_STALE" "$VP_STALE"
SHA_STALE=$(sha256sum "$SP_STALE" | cut -d' ' -f1)
SHA_STALE_ROW=$(sha256sum "$VP_STALE" | cut -d' ' -f1)

SP_MIS="$FXSRC/mismatch-$SEAT.md"; VP_MIS="$FXVAULT/mismatch-$SEAT.md"
payload_mis > "$SP_MIS";           cp "$SP_MIS" "$VP_MIS"
SHA_MIS=$(sha256sum "$SP_MIS" | cut -d' ' -f1)
SHA_MIS_WRONG=$(printf 'not-the-content' | sha256sum | cut -d' ' -f1)

SP_ABS="$FXSRC/absent-$SEAT.md";  VP_ABS="$FXVAULT/absent-$SEAT.md"
printf 'vrun-%s fixture: vault side never created\n' "$SEAT" > "$SP_ABS"
SHA_ABS=$(sha256sum "$SP_ABS" | cut -d' ' -f1)

# --- real-vault rows (read-only: the vault side is only ever hashed)
REAL_OK=false
SHA_HOME=""
if [ -f "$VAULT/Home.md" ] && [ -r "$VAULT/Home.md" ]; then
  SHA_HOME=$(sha256sum "$VAULT/Home.md" | cut -d' ' -f1)
  REAL_OK=true
fi
SP_HOME="$FXSRC/real-home-$SEAT.md"
[ "$REAL_OK" = true ] && cp "$VAULT/Home.md" "$SP_HOME"
SP_HOME_BAD="$FXSRC/real-home-bad-$SEAT.md"
[ "$REAL_OK" = true ] && cp "$VAULT/Home.md" "$SP_HOME_BAD"
SP_HOME_ABS="$FXSRC/real-home-abs-$SEAT.md"
[ "$REAL_OK" = true ] && cp "$VAULT/Home.md" "$SP_HOME_ABS"

REAL_ATLAS=false
DIG_ATLAS=""
SP_ATLAS_DIR="$FXSRC/atlas-dir-$SEAT"
dig() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
          | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }
if [ -d "$VAULT/atlas" ] && [ -r "$VAULT/atlas" ]; then
  REAL_ATLAS=true
  mkdir -p "$SP_ATLAS_DIR"
  cp -r "$VAULT/atlas/." "$SP_ATLAS_DIR/"
  DIG_ATLAS=$(dig "$SP_ATLAS_DIR")
fi

# --- test ledger (rows use canonical absolute source paths, as the tool matches)
{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s fixture match\n' \
    "$SP_KEPT" "$SHA_KEPT" "$VP_KEPT" "$SHA_KEPT" "$SEAT"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s vault edited after row\n' \
    "$SP_STALE" "$SHA_STALE" "$VP_STALE" "$SHA_STALE_ROW" "$SEAT"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s source sha mismatch\n' \
    "$SP_MIS" "$SHA_MIS_WRONG" "$VP_MIS" "$SHA_MIS" "$SEAT"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s vault side absent\n' \
    "$SP_ABS" "$SHA_ABS" "$VP_ABS" "$SHA_ABS" "$SEAT"
  if [ "$REAL_OK" = true ]; then
    printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s REAL vault match (Home.md)\n' \
      "$SP_HOME" "$SHA_HOME" "$VAULT/Home.md" "$SHA_HOME" "$SEAT"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s REAL vault hash mismatch control\n' \
      "$SP_HOME_BAD" "$SHA_HOME" "$VAULT/Home.md" "0000000000000000000000000000000000000000000000000000000000000000" "$SEAT"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s REAL vault file absent (negative)\n' \
      "$SP_HOME_ABS" "$SHA_HOME" "$VAULT/absent-$SEAT.md" "$SHA_HOME" "$SEAT"
  fi
  if [ "$REAL_ATLAS" = true ]; then
    printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s REAL vault dir digest (atlas)\n' \
      "$SP_ATLAS_DIR" "$DIG_ATLAS" "$VAULT/atlas" "$DIG_ATLAS" "$SEAT"
  fi
} > "$LEDGER"
# the vault copy is edited AFTER the row was recorded -> row must not receipt
printf 'EDIT AFTER ROW (vrun-%s)\n' "$SEAT" >> "$VP_STALE"

# ------------------------------------------------- read-only vault fingerprint
vault_fingerprint() { # $1 out-file
  {
    [ -d "$VAULT" ] || { printf 'VAULT-ABSENT\n'; return 0; }
    find "$VAULT" -type f -not -path '*/.git/*' -not -path '*/.obsidian/*' -print0 \
      | sort -z | xargs -0 -r sha256sum 2>/dev/null
  } > "$1" 2>/dev/null || true
  printf 'files=%s manifest_sha=%s\n' \
    "$(grep -c . "$1" 2>/dev/null || true)" \
    "$(sha256sum "$1" 2>/dev/null | cut -d' ' -f1)"
}
FP_BEFORE_SUM=$(vault_fingerprint "$BK/vault-fp.before")

# --------------------------------------------------------------- tool state
TOOL_EXISTS=false; TOOL_SHA=""; TOOL_SYNTAX="missing"; ENV_VARS=""
if [ -f "$TOOL" ]; then
  TOOL_EXISTS=true
  TOOL_SHA=$(sha256sum "$TOOL" | cut -d' ' -f1)
  if bash -n "$TOOL" 2>"$BK/syntax.err"; then TOOL_SYNTAX=ok
  else TOOL_SYNTAX=$(head -c 300 "$BK/syntax.err"); fi
  ENV_VARS=$(rg -o --no-filename '\$\{?[A-Z][A-Z0-9_]{2,}\}?' "$TOOL" 2>/dev/null \
             | tr -d '${}' | sort -u | tr '\n' ' ' || true)
fi
SPEC="$ROOT/tools/souji-verify.spec.md"
SPEC_SHA=$([ -f "$SPEC" ] && sha256sum "$SPEC" | cut -d' ' -f1 || echo missing)
RUNNER_SHA=$(sha256sum "$0" | cut -d' ' -f1)
LANE_HEAD=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)
LIVE_LEDGER="$ROOT/corpus/knowledge/obsidian-ledger.tsv"
LIVE_LEDGER_SHA_START=$([ -f "$LIVE_LEDGER" ] && sha256sum "$LIVE_LEDGER" | cut -d' ' -f1 || echo missing)
LIVE_LEDGER_LINES_START=$([ -f "$LIVE_LEDGER" ] && wc -l < "$LIVE_LEDGER" || echo missing)

# GUI-process census (evidence that the runner never spawns the app)
GUI_BEFORE=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true)
GUI_BEFORE=${GUI_BEFORE:-0}

# ------------------------------------------------------------------ CLI runs
OUT_TEXT=""; OUT_ERR=""; OUT_CODE=0
RUN_ENV=(SOUJI_LEDGER="$LEDGER")
run_tool() {
  local rc=0
  OUT_TEXT=$(env "${RUN_ENV[@]}" timeout "$TOOL_TIMEOUT" bash "$TOOL" "$@" 2>"$BK/stderr") || rc=$?
  OUT_CODE=$rc
  OUT_ERR=$(cat "$BK/stderr" 2>/dev/null || true)
  printf '%s\n' "$rc" >> "$BK/rcs"
  { printf '### args:'; printf ' [%s]' "$@"; printf '\n--stdout--\n%s\n--stderr--\n%s\n--rc=%s\n' \
      "$OUT_TEXT" "$OUT_ERR" "$rc"; } >> "$BK/tool-output.all"
}
line_of() { printf '%s\n' "$OUT_TEXT" | awk -F'\t' -v t="$1" 'NF>=3 && $2==t {print; f=1} END{if(!f) exit 1}'; }

assert_line() { # id name target want-verdict receipt-regex evidence-regex [rc]
  local id=$1 name=$2 tgt=$3 wv=$4 wre=${5:-} ere=${6:-} wrc=${7:-}
  local line
  if ! line=$(line_of "$tgt"); then
    record "$id" "$name" fail "line for '$tgt' -> $wv" "no line with field2=='$tgt' (rc=$OUT_CODE)" "$OUT_CODE" "$OUT_ERR"
    return 0
  fi
  local v r e status=pass detail=""
  v=$(printf '%s' "$line" | awk -F'\t' '{print $3}')
  r=$(printf '%s' "$line" | awk -F'\t' '{print $4}')
  e=$(printf '%s' "$line" | awk -F'\t' '{print $5}')
  [ "$wv" = ANY ] || [ "$v" = "$wv" ] || { status=fail; detail="verdict=$v want=$wv; "; }
  if [ -n "$wre" ] && ! printf '%s' "$r" | grep -Eq "$wre"; then status=fail; detail="${detail}receipt='$r' !~ /$wre/; "; fi
  if [ -n "$ere" ] && ! printf '%s' "$e" | grep -Eq "$ere"; then status=fail; detail="${detail}evidence='$e' !~ /$ere/; "; fi
  if [ -n "$wrc" ] && [ "$OUT_CODE" != "$wrc" ]; then status=fail; detail="${detail}rc=$OUT_CODE want=$wrc; "; fi
  record "$id" "$name" "$status" "$wv r~/$wre/ e~/$ere/" "rc=$OUT_CODE line=$line" "$OUT_CODE" "$detail"
}

# ------------------------------------------------------------- tool presence
if [ "$TOOL_EXISTS" != true ]; then
  note "tool.present" "A0" "tool absent: $TOOL"
fi
if [ "$TOOL_EXISTS" = true ]; then
  note "tool.present" "A0" "path=$TOOL sha256=$TOOL_SHA syntax=$TOOL_SYNTAX mode=$(stat -c %A "$TOOL")"
  info_kv "tool.interface" "A3" "env vars referenced: ${ENV_VARS:-none}"
  bash -n "$TOOL" 2>/dev/null && record "tool.syntax" "A1" pass "bash -n exit 0" "exit 0" 0 "" \
    || record "tool.syntax" "A1" fail "bash -n exit 0" "syntax error" 1 "$TOOL_SYNTAX"

  # --- tool's own selftest (must cover its F1-F10 + vault cases)
  TOOL_TIMEOUT=300 run_tool --selftest
  if [ "$OUT_CODE" = 0 ]; then
    record "selftest.exit" "A2" pass "exit 0" "exit=0 $(printf '%s' "$OUT_TEXT" | tail -1 | cut -c1-160)" 0 ""
  else
    record "selftest.exit" "A2" fail "exit 0" "exit=$OUT_CODE $(printf '%s' "$OUT_TEXT" | tail -1 | cut -c1-160)" "$OUT_CODE" "$OUT_ERR"
  fi
  TOOL_TIMEOUT=120

  # --- fixture-vault rows (negatives: decisive criterion = NOT-SAFE verdict;
  #     the reason string is recorded in `observed`, not gated, so the runner
  #     stays implementation-tolerant while still catching any false-SAFE)
  run_tool "$SP_KEPT"
  assert_line "V1.fixture-ledger-match" "V1" "$SP_KEPT" SAFE '^moved-to-obsidian$' 'vault=' 0
  run_tool "$SP_STALE"
  assert_line "V2.fixture-edited-after-row" "V2" "$SP_STALE" NOT-SAFE '.*' '' 0
  run_tool "$SP_MIS"
  assert_line "V3.fixture-source-sha-mismatch" "V3" "$SP_MIS" NOT-SAFE '.*' '' 0
  run_tool "$SP_ABS"
  assert_line "V4.fixture-vault-absent" "V4" "$SP_ABS" NOT-SAFE '.*' '' 0

  # --- REAL vault rows (read-only on the vault side)
  if [ "$REAL_OK" = true ]; then
    run_tool "$SP_HOME"
    assert_line "V5.real-vault-match" "V5" "$SP_HOME" SAFE '^moved-to-obsidian$' "$VAULT/Home\.md" 0
    run_tool "$SP_HOME_BAD"
    assert_line "V6.real-vault-hash-mismatch" "V6" "$SP_HOME_BAD" NOT-SAFE '.*' '' 0
    run_tool "$SP_HOME_ABS"
    assert_line "V7.real-vault-file-absent" "V7" "$SP_HOME_ABS" NOT-SAFE '.*' '' 0
  else
    record "V5.real-vault-match" "V5" skip "SAFE moved-to-obsidian" "vault Home.md unreadable" "" "vault=$VAULT"
    record "V6.real-vault-hash-mismatch" "V6" skip "NOT-SAFE vault-sha-mismatch" "vault Home.md unreadable" "" ""
    record "V7.real-vault-file-absent" "V7" skip "NOT-SAFE vault-unreachable" "vault Home.md unreadable" "" ""
  fi
  if [ "$REAL_ATLAS" = true ]; then
    run_tool "$SP_ATLAS_DIR"
    assert_line "V8.real-vault-dir-digest" "V8" "$SP_ATLAS_DIR" SAFE '^moved-to-obsidian$' 'vault=' 0
  else
    record "V8.real-vault-dir-digest" "V8" skip "SAFE moved-to-obsidian" "vault atlas unreadable" "" ""
  fi

  # --- determinism + json + batch + exit-domain
  run_tool "$SP_HOME"
  DET_1="$OUT_TEXT"
  run_tool "$SP_HOME"
  if [ "$DET_1" = "$OUT_TEXT" ]; then record "V9.determinism" "V9" pass "identical line on rerun" "identical" "$OUT_CODE" ""
  else record "V9.determinism" "V9" fail "identical line on rerun" "differs" "$OUT_CODE" ""; fi

  run_tool --json "$SP_HOME"
  if printf '%s' "$OUT_TEXT" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
    record "V10.json-parse" "V10" pass "parses as JSON" "parsed" "$OUT_CODE" ""
  else
    record "V10.json-parse" "V10" fail "parses as JSON" "$(printf '%s' "$OUT_TEXT" | head -c 160)" "$OUT_CODE" ""
  fi

  run_tool "$SP_KEPT" "$SP_STALE" "$SP_ABS"
  assert_line "V11.batch-match" "V11" "$SP_KEPT" SAFE '^moved-to-obsidian$' 'vault=' 0
  assert_line "V11.batch-edited" "V11" "$SP_STALE" NOT-SAFE '.*' '' 0
  assert_line "V11.batch-absent" "V11" "$SP_ABS" NOT-SAFE '.*' '' 0
else
  for c in tool.syntax selftest.exit V1.fixture-ledger-match V2.fixture-edited-after-row \
           V3.fixture-source-sha-mismatch V4.fixture-vault-absent V5.real-vault-match \
           V6.real-vault-hash-mismatch V7.real-vault-file-absent V8.real-vault-dir-digest \
           V9.determinism V10.json-parse V11.batch-match V11.batch-edited V11.batch-absent; do
    record "$c" "P0" skip "tool missing" "not run" "" "no tool at $TOOL"
  done
fi

# --------------------------------------------------- live-ledger invariants
LIVE_LEDGER_SHA_END=$([ -f "$LIVE_LEDGER" ] && sha256sum "$LIVE_LEDGER" | cut -d' ' -f1 || echo missing)
LIVE_LEDGER_LINES_END=$([ -f "$LIVE_LEDGER" ] && wc -l < "$LIVE_LEDGER" || echo missing)
if [ "$LIVE_LEDGER_LINES_START" = 1 ] && [ "$LIVE_LEDGER_LINES_END" = 1 ] \
   && [ "$LIVE_LEDGER_SHA_START" = "$LIVE_LEDGER_SHA_END" ]; then
  record "V12.live-ledger-header-only" "V12" pass "header-only and unchanged" \
    "lines=1 sha=${LIVE_LEDGER_SHA_END:0:12}" 0 ""
else
  record "V12.live-ledger-header-only" "V12" fail "header-only and unchanged" \
    "lines ${LIVE_LEDGER_LINES_START}->${LIVE_LEDGER_LINES_END} sha ${LIVE_LEDGER_SHA_START:0:12}->${LIVE_LEDGER_SHA_END:0:12}" 0 ""
fi

# --------------------------------------------------- vault read-only check
FP_AFTER_SUM=$(vault_fingerprint "$BK/vault-fp.after")
if [ "$FP_BEFORE_SUM" = "$FP_AFTER_SUM" ]; then
  record "V13.vault-unchanged" "V13" pass "vault sha256 manifest identical" "$FP_BEFORE_SUM" 0 ""
else
  record "V13.vault-unchanged" "V13" fail "vault sha256 manifest identical" \
    "before[$FP_BEFORE_SUM] after[$FP_AFTER_SUM] (external writer?)" 0 ""
fi
cmp -s "$BK/vault-fp.before" "$BK/vault-fp.after" \
  && record "V13b.vault-filelist-identical" "V13" pass "per-file hashes identical" "$FP_BEFORE_SUM" 0 "" \
  || record "V13b.vault-filelist-identical" "V13" fail "per-file hashes identical" "differs" 0 ""

# ------------------------------------------------------------- CLI probes
probe_cli() { # id name cmd...
  local id=$1 name=$2; shift 2
  local out rc=0
  out=$(timeout 5 "$@" 2>&1) || rc=$?
  record "$id" "$name" "$([ "$rc" = 0 ] && echo pass || echo fail)" "exit 0" \
    "rc=$rc $(printf '%s' "$out" | head -1 | cut -c1-120)" "$rc" ""
  printf '%s\n' "$out" > "$BK/cli-$id.out"
}
CLI_BIN=$(command -v obsidian-cli-inspector || true)
if [ -n "$CLI_BIN" ]; then
  probe_cli "C1.inspector-version" "obsidian-cli-inspector --version" "$CLI_BIN" --version
  probe_cli "C2.inspector-index-help" "obsidian-cli-inspector index --help" "$CLI_BIN" index --help
  probe_cli "C3.inspector-search-help" "obsidian-cli-inspector search --help" "$CLI_BIN" search --help
  probe_cli "C4.inspector-diagnose-help" "obsidian-cli-inspector diagnose --help" "$CLI_BIN" diagnose --help
  info_kv "C5.inspector-binary" "C5" "which=$CLI_BIN mode=$(stat -c %A "$CLI_BIN") $(ls -l "$CLI_BIN" 2>/dev/null | awk '{print $3":"$4}')"
else
  record "C1.inspector-version" "C1" fail "obsidian-cli-inspector present" "not in PATH" "" ""
fi
SHIMS=$( { ls /home/vgpnk/.local/bin 2>/dev/null | grep -i obsidian || true; } | tr '\n' ' ')
SHIMS2=$( { ls /usr/local/bin 2>/dev/null | grep -i obsidian || true; } | tr '\n' ' ')
info_kv "C6.shim-search" "C6" "obsidian-named entries: ~/.local/bin=[${SHIMS:-none}] /usr/local/bin=[${SHIMS2:-none}]"
if [ -f /home/vgpnk/.config/obsidian/obsidian.json ]; then
  OBJSON=$(python3 - <<'PY' 2>/dev/null || true
import json
d=json.load(open('/home/vgpnk/.config/obsidian/obsidian.json'))
vs=d.get('vaults',{})
paths=[v.get('path') for v in vs.values() if isinstance(v,dict)]
print('cli=%s vaults=%d path=%s' % (d.get('cli'), len(vs), paths[0] if paths else 'none'))
PY
)
  info_kv "C7.obsidian-registry" "C7" "${OBJSON:-unparseable}"
else
  info_kv "C7.obsidian-registry" "C7" "~/.config/obsidian/obsidian.json absent"
fi
if [ -e /usr/bin/obsidian ]; then
  info_kv "C8.gui-launcher" "C8" "NOT EXECUTED: /usr/bin/obsidian mode=$(stat -c %A /usr/bin/obsidian) bytes=$(stat -c %s /usr/bin/obsidian) target=$(grep -o 'exec .*' /usr/bin/obsidian 2>/dev/null | head -1)"
else
  info_kv "C8.gui-launcher" "C8" "/usr/bin/obsidian absent"
fi
PKG1=$(pacman -Qo /usr/bin/obsidian 2>/dev/null | head -1 || echo unowned)
PKG2=$(pacman -Qo /usr/bin/obsidian-cli-inspector 2>/dev/null | head -1 || echo unowned)
info_kv "C9.pkg-owner" "C9" "obsidian: ${PKG1:-unowned} | inspector: ${PKG2:-unowned}"
VAULT_HEAD=$(git --git-dir="$VAULT/.git" rev-parse HEAD 2>/dev/null || echo unknown)
info_kv "C10.vault-head" "C10" "vault HEAD=$VAULT_HEAD (read-only rev-parse)"

# --------------------------------------------------- S36 seat-specific probes
# (a) the bundled CLI usage string, read out of the app asar with grep only
USAGE_LINE=$(grep -a -o -m1 'Usage: obsidian <command> \[options\]' /usr/lib/obsidian/obsidian.asar 2>/dev/null || true)
if [ -n "$USAGE_LINE" ]; then
  record "S1.bundled-cli-usage" "S1" pass "usage string present in app asar" "$USAGE_LINE" 0 ""
else
  record "S1.bundled-cli-usage" "S1" fail "usage string present in app asar" "not found" 1 "grep -a over /usr/lib/obsidian/obsidian.asar"
fi
SOCKET_DIR="${XDG_RUNTIME_DIR:-$HOME}"
# S2 is environment state, not a tool property: the socket only exists while an
# Obsidian instance is running. Recorded as info with the observed value.
if [ -S "$SOCKET_DIR/.obsidian-cli.sock" ]; then
  info_kv "S2.cli-daemon-socket" "S2" "PRESENT at $SOCKET_DIR/.obsidian-cli.sock (an Obsidian instance is live; CLI transport up)"
else
  info_kv "S2.cli-daemon-socket" "S2" "ABSENT at $SOCKET_DIR/.obsidian-cli.sock (no live Obsidian instance; CLI transport down, sha256sum is the only working path)"
fi
# (b) symlink trap: a follow-symlink walk of the vault explodes the file count
CNT_NOFOLLOW=$(find "$VAULT" -type f -not -path '*/.git/*' 2>/dev/null | wc -l)
CNT_FOLLOW=$(find -L "$VAULT" -type f -not -path '*/.git/*' 2>/dev/null | wc -l)
if [ "$CNT_FOLLOW" -gt "$(( CNT_NOFOLLOW * 2 ))" ]; then
  record "S3.symlink-trap" "S3" pass "vault walk must not follow symlinks" \
    "nofollow=$CNT_NOFOLLOW follow=$CNT_FOLLOW (top-level 'protocol' symlink)" 0 \
    "a find -L vault manifest would hash ~100k foreign files and report false changes"
else
  record "S3.symlink-trap" "S3" fail "vault walk must not follow symlinks" \
    "nofollow=$CNT_NOFOLLOW follow=$CNT_FOLLOW" 0 ""
fi
# (c) inspector Hash field is a size:mtime pseudo-hash, not a content digest.
# Own config + own database under $BK (never ~/.config, never the r2 scratch).
INSP_HASH=""; INSP_SHA=""; INSP_NOTES=""
if [ -n "$CLI_BIN" ] && [ "$REAL_OK" = true ]; then
  IDX_CFG="$BK/insp.toml"
  printf 'vault_path = "%s"\ndatabase_path = "%s/insp.db"\nlog_path = "%s/logs"\n' \
    "$VAULT" "$BK" "$BK" > "$IDX_CFG"
  mkdir -p "$BK/logs"
  timeout 20 "$CLI_BIN" -c "$IDX_CFG" init init >"$BK/insp-init.out" 2>&1 || true
  timeout 60 "$CLI_BIN" -c "$IDX_CFG" index index >"$BK/insp-index.out" 2>&1 || true
  INSP_NOTES=$(sed -n 's/^Indexed \([0-9][0-9]*\) notes successfully$/\1/p' "$BK/insp-index.out" | head -1)
  INSP_HASH=$(timeout 10 "$CLI_BIN" -c "$IDX_CFG" view describe Home.md 2>/dev/null \
              | awk -F': *' '/^Hash:/{print $2}' || true)
  INSP_SHA=$(sha256sum "$VAULT/Home.md" | cut -d' ' -f1)
  INSP_SIZE_HEX=$(printf '%x' "$(stat -c %s "$VAULT/Home.md")")
  if [ -n "$INSP_HASH" ] && [ "$INSP_HASH" != "$INSP_SHA" ] \
     && [ "${INSP_HASH%%:*}" = "$INSP_SIZE_HEX" ]; then
    record "S4.inspector-hash-not-sha256" "S4" pass "inspector Hash is a content sha256" \
      "inspector Hash='$INSP_HASH' = size_hex($INSP_SIZE_HEX):mtime_epoch vs content sha256=${INSP_SHA:0:12} -> NOT a content digest" 0 \
      "cannot serve as the vault-side sha256 oracle; sha256sum stays the verifier of record"
  elif [ -n "$INSP_HASH" ] && [ "$INSP_HASH" != "$INSP_SHA" ] \
       && ! printf '%s' "$INSP_SHA" | grep -q "^${INSP_HASH%%:*}"; then
    record "S4.inspector-hash-not-sha256" "S4" pass "inspector Hash is a content sha256" \
      "inspector Hash='$INSP_HASH' vs content sha256=${INSP_SHA:0:12} -> NOT a content digest" 0 \
      "cannot serve as the vault-side sha256 oracle; sha256sum stays the verifier of record"
  else
    record "S4.inspector-hash-not-sha256" "S4" fail "inspector Hash is a content sha256" \
      "inspector Hash='${INSP_HASH:-none}' sha256=${INSP_SHA:0:12}" 0 ""
  fi
else
  record "S4.inspector-hash-not-sha256" "S4" skip "inspector Hash probe" "inspector or vault unavailable" "" ""
fi
# (d) the tool must never shell out to the GUI launcher
if [ "$TOOL_EXISTS" = true ]; then
  if rg -q --no-ignore -e '/usr/bin/obsidian([^a-z-]|$)' -e 'exec electron43' "$TOOL" 2>/dev/null; then
    record "S5.no-gui-invocation" "S5" fail "tool never names the GUI launcher" "matched in $TOOL" 1 ""
  else
    record "S5.no-gui-invocation" "S5" pass "tool never names the GUI launcher" "no /usr/bin/obsidian or electron43 reference" 0 ""
  fi
else
  record "S5.no-gui-invocation" "S5" skip "tool absent" "not run" "" ""
fi
# (e) S36 addition: index-scale cross-check (inspector notes vs vault file count)
if [ -n "$INSP_NOTES" ]; then
  info_kv "S6.inspector-index-scale" "S6" \
    "indexed_notes=$INSP_NOTES vault_files_nofollow=$CNT_NOFOLLOW (inspector counts markdown notes; file count includes attachments)"
else
  info_kv "S6.inspector-index-scale" "S6" "index run not measured (inspector or vault unavailable)"
fi
# (f) S36 addition: live-app context (recorded, never touched)
LIVE_ELECTRON=$(pgrep -fc '/usr/lib/electron43/electron' 2>/dev/null || true)
info_kv "S7.live-app-context" "S7" \
  "electron processes matching /usr/lib/electron43/electron: ${LIVE_ELECTRON:-0}; GUI_BEFORE=$GUI_BEFORE (pgrep app.asar)"

# ------------------------------------------------------------- post checks
GUI_AFTER=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true)
GUI_AFTER=${GUI_AFTER:-0}
if [ "$GUI_BEFORE" = "$GUI_AFTER" ]; then
  record "C11.no-gui-spawn" "C11" pass "obsidian app process count unchanged" "before=$GUI_BEFORE after=$GUI_AFTER" 0 ""
else
  record "C11.no-gui-spawn" "C11" fail "obsidian app process count unchanged" "before=$GUI_BEFORE after=$GUI_AFTER" 0 "GUI process delta"
fi

if [ "$TOOL_EXISTS" = true ]; then
  TOOL_SHA_END=$(sha256sum "$TOOL" | cut -d' ' -f1)
  if [ "$TOOL_SHA" = "$TOOL_SHA_END" ]; then
    record "A4.tool-stable" "A4" pass "tool sha256 unchanged across run" "$TOOL_SHA_END" 0 ""
  else
    record "A4.tool-stable" "A4" fail "tool sha256 unchanged across run" "$TOOL_SHA->$TOOL_SHA_END" 0 ""
  fi
fi

# exit-code domain across every invocation (spec: {0,1,2} + fixture/usage codes)
if [ -s "$BK/rcs" ]; then
  RCDOM=$(sort -u "$BK/rcs" | tr '\n' ' ')
  case "$RCDOM" in
    *" 3 "*|"3 "*|*" 3"|*" 124 "*|*" 124"|*" 137 "*|*" 137")
      record "A5.exit-domain" "A5" fail "rcs subset of {0,1,2}" "observed: $RCDOM" 0 "unexpected rc" ;;
    *) record "A5.exit-domain" "A5" pass "rcs subset of {0,1,2}" "observed: $RCDOM" 0 "" ;;
  esac
fi

# fixture source/vault trees must be exactly as this runner built them
FX_OK=true
[ "$(cat "$SP_KEPT")" = "$(payload_kept)" ] || FX_OK=false
[ "$(cat "$VP_KEPT")" = "$(payload_kept)" ] || FX_OK=false
[ "$(cat "$SP_STALE")" = "$(payload_stale)" ] || FX_OK=false
if [ "$FX_OK" = true ]; then
  record "A6.fixtures-intact" "A6" pass "fixture files unchanged by tool runs" "intact" 0 ""
else
  record "A6.fixtures-intact" "A6" fail "fixture files unchanged by tool runs" "mutated" 0 ""
fi

# --------------------------------------------------- per-impl matrix (additive)
# S36 addition: if round-4 candidate impls exist, run the compact matrix
# (selftest + V1..V4) against each and emit aggregator rows.
IMPLLIST="$BK/impls.txt"; : > "$IMPLLIST"
for p in "$ROOT"/tools/souji-vault-verify.impl-*.sh "$ROOT"/tools/vault-verify.impl-*.sh; do
  [ -f "$p" ] && printf '%s\n' "$p" >> "$IMPLLIST"
done
: > "$BK/impl-rows.tsv"
while IFS= read -r impl; do
  [ -n "$impl" ] || continue
  iname="$(basename "$impl")"; iname="${iname%.sh}"
  isha=$(sha256sum "$impl" | cut -d' ' -f1)
  printf '%s\t%s\n' "$iname" "$isha" >> "$BK/impl-shas.tsv"
  st_rc=0
  st_out=$(env SOUJI_LEDGER="$LEDGER" timeout 300 bash "$impl" --selftest 2>&1) || st_rc=$?
  printf '%s\t%s\t%s\t%s\t%s\n' "$iname" "--selftest" \
    "$([ "$st_rc" -eq 0 ] && echo true || echo false)" "exit=$st_rc" "exit=0" >> "$BK/impl-rows.tsv"
  printf '%s' "$st_out" > "$BK/st-${iname}.log"
  for tgt in "$SP_KEPT" "$SP_STALE" "$SP_MIS" "$SP_ABS"; do
    case "$tgt" in "$SP_KEPT") caseid=V1; want=SAFE;; "$SP_STALE") caseid=V2; want=NOT-SAFE;; "$SP_MIS") caseid=V3; want=NOT-SAFE;; *) caseid=V4; want=NOT-SAFE;; esac
    got_rc=0
    got_out=$(env SOUJI_LEDGER="$LEDGER" timeout 60 bash "$impl" "$tgt" 2>&1) || got_rc=$?
    got_line=$(printf '%s\n' "$got_out" | grep -aE '^(VERDICT|VERIFIED|NOT-VERIFIED|SAFE|NOT-SAFE)' | head -1 || true)
    got_v=$(printf '%s' "$got_line" | awk -F'\t' '{print $1}')
    got_v="${got_v%%(*}"
    case "$got_v" in
      VERIFIED|NOT-VERIFIED|SAFE|NOT-SAFE) : ;;
      *) got_v=$(printf '%s' "$got_line" | awk -F'\t' '{print $3}'); got_v="${got_v%%(*}" ;;
    esac
    [ -z "$got_v" ] && got_v=$(printf '%s' "$got_line" | awk '{print $1}')
    got_v="${got_v%%(*}"
    # r4 impls answer VERIFIED/NOT-VERIFIED; r2 vocabulary is SAFE/NOT-SAFE.
    case "$got_v" in
      VERIFIED|SAFE) got_class=SAFE ;;
      NOT-VERIFIED|NOT-SAFE) got_class=NOT-SAFE ;;
      *) got_class="$got_v" ;;
    esac
    p=false
    if [ "$want" = SAFE ] && [ "$got_class" = SAFE ]; then p=true; fi
    if [ "$want" = NOT-SAFE ] && [ "$got_class" = NOT-SAFE ]; then p=true; fi
    [ -z "$got_line" ] && got_line="rc=$got_rc out=$(printf '%s' "$got_out" | head -c 120 | tr '\t\n' '  ')"
    got_line="${got_line//$'\t'/ }"
    got_line="${got_line//$'\n'/ }"
    printf '%s\t%s\t%s\t%s\t%s\n' "$iname" "$caseid" "$p" "$got_line" "$want" >> "$BK/impl-rows.tsv"
  done
done < "$IMPLLIST"

# ------------------------------------------------------------------- report
mkdir -p "$(dirname "$RESULTS")"
python3 - "$RTSV" "$RESULTS" "$TOOL" "$TOOL_SHA" "$TOOL_SYNTAX" "$SPEC_SHA" "$RUNNER_SHA" \
        "$SEAT" "$LANE_HEAD" "$VAULT" "$VAULT_HEAD" "$FP_BEFORE_SUM" "$FP_AFTER_SUM" \
        "$LIVE_LEDGER_SHA_START" "$LIVE_LEDGER_SHA_END" "$LEDGER" "$ENV_VARS" "$WORK" \
        "$CNT_NOFOLLOW" "$CNT_FOLLOW" "${INSP_HASH:-}" "${INSP_SHA:-}" "${INSP_NOTES:-}" \
        "$BK/impl-rows.tsv" "$BK/impl-shas.tsv" "$LIVE_LEDGER_LINES_START" "$LIVE_LEDGER_LINES_END" <<'PY'
import json, sys, collections, datetime, os
(tsv, out_path, tool, tool_sha, tool_syntax, spec_sha, runner_sha,
 seat, lane_head, vault, vault_head, fp_before, fp_after,
 ll_sha_start, ll_sha_end, test_ledger, env_vars, work,
 cnt_nofollow, cnt_follow, insp_hash, insp_sha, insp_notes,
 impl_rows_path, impl_shas_path, ll_lines_start, ll_lines_end) = sys.argv[1:28]

def san(s):
    return (s or "").replace(work, "<work>")

checks = []
for raw in open(tsv):
    if not raw.strip():
        continue
    f = (raw.rstrip("\n").split("\t") + [""] * 7)[:7]
    checks.append({
        "id": san(f[0]), "name": san(f[1]), "status": f[2],
        "expected": san(f[3]), "observed": san(f[4]),
        "exit_code": int(f[5]) if f[5].strip().lstrip("-").isdigit() else None,
        "detail": san(f[6]),
    })

counts = collections.Counter(c["status"] for c in checks)
fails = [c["id"] for c in checks if c["status"] == "fail"]
skipped = [c["id"] for c in checks if c["status"] == "skip"]
measured = [c for c in checks if c["status"] not in ("info", "skip")]
status = "blocked" if not measured else ("fail" if fails else "pass")
exit_code = 3 if not measured else (1 if fails else 0)

impl_rows = []
try:
    for raw in open(impl_rows_path):
        f = (raw.rstrip("\n").split("\t") + [""] * 5)[:5]
        if f[0]:
            impl_rows.append({"impl": f[0], "case": f[1], "pass": f[2] == "true",
                              "got": f[3], "want": f[4]})
except OSError:
    pass
impl_shas = {}
try:
    for raw in open(impl_shas_path):
        f = (raw.rstrip("\n").split("\t") + [""] * 2)[:2]
        if f[0]:
            impl_shas[f[0]] = f[1]
except OSError:
    pass

report = {
    "seat": "S%s" % seat,
    "role": "vault-runner",
    "round": 4,
    "runner": "tests/vault/runner-%s.sh" % seat,
    "runner_sha256": runner_sha,
    "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "status": status,
    "exit_code": exit_code,
    "lane_head": lane_head,
    "tool": {"path": os.path.relpath(tool, os.path.dirname(os.path.dirname(os.path.abspath(tsv)))) if tool else None,
             "exists": bool(tool and os.path.isfile(tool)), "sha256": tool_sha or None,
             "bash_syntax": tool_syntax},
    "spec": {"path": "tools/souji-verify.spec.md", "sha256": spec_sha},
    "vault": {"path": vault, "head": vault_head,
              "fingerprint_before": fp_before, "fingerprint_after": fp_after,
              "unchanged": fp_before == fp_after,
              "files_no_symlink_follow": int(cnt_nofollow or 0),
              "files_with_symlink_follow": int(cnt_follow or 0),
              "note": ".obsidian/** excluded from the fingerprint: the desktop app is live and writes its own workspace files"},
    "cli_finding": {
        "inspector_hash_field": insp_hash or None,
        "content_sha256_of_same_file": insp_sha or None,
        "indexed_notes": int(insp_notes) if (insp_notes or "").strip().isdigit() else None,
        "verdict": "obsidian-cli-inspector's Hash is a size_hex:mtime_epoch pseudo-hash, not a content digest; "
                   "it cannot serve as the vault-side sha256 oracle, so sha256sum remains the verifier of record",
    },
    "live_ledger": {"path": "corpus/knowledge/obsidian-ledger.tsv",
                    "sha256_start": ll_sha_start, "sha256_end": ll_sha_end,
                    "lines_start": int(ll_lines_start) if (ll_lines_start or "").strip().isdigit() else None,
                    "lines_end": int(ll_lines_end) if (ll_lines_end or "").strip().isdigit() else None,
                    "header_only": ll_sha_start == ll_sha_end and ll_lines_start == "1"},
    "test_ledger": os.path.relpath(test_ledger, os.path.dirname(os.path.dirname(os.path.abspath(tsv)))),
    "method": {
        "independence": "own fixtures under tests/vault/fixture-*-<seat>/ + own ledger tests/vault/vrun-<seat>-ledger.tsv; no other seat's fixtures or ledgers consumed",
        "vault_access": "read-only: sha256sum/find/stat/git-rev-parse only; no writes, no notes created, no git index-refresh commands run against the vault",
        "gui_policy": "the GUI launcher /usr/bin/obsidian is never executed; obsidian-cli-inspector probed with timeout 5 (--version/--help only); S4 uses an own config/db under the scratch dir",
        "env_passed_to_tool": ["SOUJI_LEDGER"],
        "env_overrides_declared_in_tool_source": env_vars.split() if env_vars.strip() else [],
        "tool_selection": "first existing of tools/souji-vault-verify.sh, tools/obsidian-vault-verify.sh, tools/vault-verify.sh, tools/souji-verify.sh (or --tool)",
        "twin": "check IDs V1..V13b/A0..A6/C1..C11 mirror tests/vault/runner-35.sh so vrun-35.json and vrun-36.json can be diffed; S36 additions: --wait for the r4 tool, souji-vault-verify-first tool selection, per-impl matrix (impl-rows below), S6 index-scale and S7 live-app info rows",
    },
    "counts": {"total": len(checks), "pass": counts["pass"], "fail": counts["fail"],
               "skip": counts["skip"], "info": counts["info"]},
    "failed_checks": fails,
    "skipped_checks": skipped,
    "checks": checks,
    "rows": impl_rows,
    "impls": {
        "count": len(impl_shas),
        "sha256": impl_shas,
        "rows": impl_rows,
        "rows_summary": {
            "total": len(impl_rows),
            "pass": sum(1 for r in impl_rows if r["pass"]),
            "fail": sum(1 for r in impl_rows if not r["pass"]),
        },
    },
}
with open(out_path, "w") as fh:
    json.dump(report, fh, indent=2)
    fh.write("\n")
print("runner-%s: status=%s exit=%d pass=%d fail=%d skip=%d info=%d tool=%s"
      % (seat, status, exit_code, counts["pass"], counts["fail"], counts["skip"],
         counts["info"], os.path.basename(tool)))
print("runner-%s: impl-matrix impls=%d rows=%d pass=%d" % (
    seat, len(impl_shas), len(impl_rows), sum(1 for r in impl_rows if r["pass"])))
if fails:
    print("failed: " + ", ".join(fails))
PY

exit "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["exit_code"])' "$RESULTS")"
