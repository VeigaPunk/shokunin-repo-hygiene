#!/usr/bin/env bash
# runner-37.sh — round-4 vault-verification runner (SEAT S37, "identical" runner).
#
# Independent by construction: builds its OWN fixtures under
# tests/vault/fixture-*-<seat>/ and a test ledger at tests/vault/vrun-<seat>-ledger.tsv;
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
#      of every vault file before vs after);
#   4. the live ledger corpus/knowledge/obsidian-ledger.tsv stays
#      header-only;
#   5. CLI entry-point probe: obsidian-cli-inspector (timeout 5, help and
#      --version only). The GUI launcher /usr/bin/obsidian is NEVER
#      executed — stat/pgrep evidence only.
#   6. additive candidate matrix: every tools/souji-vault-verify.impl-*.sh
#      that exists is run through a compact case battery (selftest, fixture
#      rows, real-vault rows, dir digest, negatives) and the outcome is
#      emitted as `rows` [{impl, case, pass, got, want, rc, cmd, detail}]
#      for the S57 aggregator — the matrix never gates this seat's status.
#
# usage: tests/vault/runner-37.sh [--seat N] [--tool PATH] [--results PATH]
#                                 [--vault PATH] [--keep]
#   --seat N    seat number (default 37) — suffixes fixtures and output name
#   --tool      tool under test; default: first existing of
#               tools/souji-vault-verify.sh, tools/obsidian-vault-verify.sh,
#               tools/vault-verify.sh, tools/souji-verify.sh (impl-*.sh
#               candidates are NOT auto-selected; they run in the matrix)
#   --results   JSON report path (default <lane>/tests/results/vrun-<seat>.json)
#   --vault     real vault path (default /home/vgpnk/Documents/shokoknowledge)
#   --keep      keep the mktemp scratch dir (default: removed)
# exit: 0 all checks pass | 1 any counted check failed | 2 usage | 3 tool missing
set -euo pipefail
export LC_ALL=C

SELF_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$SELF_DIR/../.." && pwd)       # lane repo root (this file lives in tests/vault/)
SEAT=37
TOOL=""
RESULTS=""
VAULT="/home/vgpnk/Documents/shokoknowledge"
KEEP=0
TOOL_TIMEOUT=120

die_usage() { printf 'runner-37.sh: %s\n' "$1" >&2; exit 2; }
while [ $# -gt 0 ]; do
  case "$1" in
    --seat)    [ $# -ge 2 ] || die_usage "--seat needs a value"; SEAT=$2; shift 2;;
    --tool)    [ $# -ge 2 ] || die_usage "--tool needs a value"; TOOL=$2; shift 2;;
    --results) [ $# -ge 2 ] || die_usage "--results needs a value"; RESULTS=$2; shift 2;;
    --vault)   [ $# -ge 2 ] || die_usage "--vault needs a value"; VAULT=$2; shift 2;;
    --keep)    KEEP=1; shift;;
    -h|--help) sed -n '2,28p' "$0"; exit 0;;
    *) die_usage "unknown argument: $1";;
  esac
done

if [ -z "$TOOL" ]; then
  for cand in "$ROOT/tools/souji-vault-verify.sh" "$ROOT/tools/obsidian-vault-verify.sh" \
              "$ROOT/tools/vault-verify.sh" "$ROOT/tools/souji-verify.sh"; do
    [ -f "$cand" ] && { TOOL=$cand; break; }
  done
fi
[ -n "$TOOL" ] || { printf 'runner-37.sh: no tool found under tools/\n' >&2; exit 3; }
[ -z "$RESULTS" ] && RESULTS="$ROOT/tests/results/vrun-$SEAT.json"

WORK=$(mktemp -d /tmp/souji37-vault.XXXXXX)
case "$WORK" in /tmp/souji37-vault.*) : ;; *) echo "refusing: WORK=$WORK" >&2; exit 9;; esac
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
if [ "$REAL_OK" = true ]; then cp "$VAULT/Home.md" "$SP_HOME"; fi
SP_HOME_BAD="$FXSRC/real-home-bad-$SEAT.md"
if [ "$REAL_OK" = true ]; then cp "$VAULT/Home.md" "$SP_HOME_BAD"; fi
SP_HOME_ABS="$FXSRC/real-home-abs-$SEAT.md"
if [ "$REAL_OK" = true ]; then cp "$VAULT/Home.md" "$SP_HOME_ABS"; fi

REAL_ATLAS=false
DIG_ATLAS=""
SP_ATLAS_DIR="$FXSRC/atlas-dir-$SEAT"
if [ -d "$VAULT/atlas" ] && [ -r "$VAULT/atlas" ]; then
  REAL_ATLAS=true
  mkdir -p "$SP_ATLAS_DIR"
  cp -r "$VAULT/atlas/." "$SP_ATLAS_DIR/"
  dig() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
            | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }
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
: > "$BK/rcs"
RUN_ENV=(SOUJI_LEDGER="$LEDGER")
run_tool() {
  local rc=0
  OUT_TEXT=$(env "${RUN_ENV[@]}" timeout "$TOOL_TIMEOUT" bash "$TOOL" "$@" 2>"$BK/stderr") || rc=$?
  OUT_CODE=$rc
  printf '%s\n' "$rc" >> "$BK/rcs"
  OUT_ERR=$(cat "$BK/stderr" 2>/dev/null || true)
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

  # --- fixture-vault rows (negatives: decisive criteria = NOT-SAFE verdict AND
  #     the ledger path was actually consulted (evidence names the obsidian
  #     ground of refusal); the exact wording is recorded, gated loosely)
  run_tool "$SP_KEPT"
  assert_line "V1.fixture-ledger-match" "V1" "$SP_KEPT" SAFE '^moved-to-obsidian$' 'vault=' 0
  run_tool "$SP_STALE"
  assert_line "V2.fixture-edited-after-row" "V2" "$SP_STALE" NOT-SAFE '.*' 'obsidian=.*vault' 0
  run_tool "$SP_MIS"
  assert_line "V3.fixture-source-sha-mismatch" "V3" "$SP_MIS" NOT-SAFE '.*' 'obsidian=.*source' 0
  run_tool "$SP_ABS"
  assert_line "V4.fixture-vault-absent" "V4" "$SP_ABS" NOT-SAFE '.*' 'obsidian=.*vault' 0

  # --- REAL vault rows (read-only on the vault side)
  if [ "$REAL_OK" = true ]; then
    run_tool "$SP_HOME"
    assert_line "V5.real-vault-match" "V5" "$SP_HOME" SAFE '^moved-to-obsidian$' "$VAULT/Home\.md" 0
    run_tool "$SP_HOME_BAD"
    assert_line "V6.real-vault-hash-mismatch" "V6" "$SP_HOME_BAD" NOT-SAFE '.*' 'obsidian=.*vault' 0
    run_tool "$SP_HOME_ABS"
    assert_line "V7.real-vault-file-absent" "V7" "$SP_HOME_ABS" NOT-SAFE '.*' 'obsidian=.*vault' 0
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
  assert_line "V11.batch-edited" "V11" "$SP_STALE" NOT-SAFE '.*' 'obsidian=.*vault' 0
  assert_line "V11.batch-absent" "V11" "$SP_ABS" NOT-SAFE '.*' 'obsidian=.*vault' 0
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
PKG1=$(pacman -Qo /usr/bin/obsidian 2>/dev/null || dpkg -S /usr/bin/obsidian 2>/dev/null || echo unowned)
PKG2=$(pacman -Qo /usr/bin/obsidian-cli-inspector 2>/dev/null || dpkg -S /usr/bin/obsidian-cli-inspector 2>/dev/null || echo unowned)
info_kv "C9.pkg-owner" "C9" "obsidian: $PKG1 | inspector: $PKG2"
VAULT_HEAD=$(git --git-dir="$VAULT/.git" rev-parse HEAD 2>/dev/null || echo unknown)
info_kv "C10.vault-head" "C10" "vault HEAD=$VAULT_HEAD (read-only rev-parse)"

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

# ------------------------------------------- additive candidate matrix
# Runs every tools/souji-vault-verify.impl-*.sh (round-4 candidates) through a
# compact battery against THIS seat's fixtures. Rows feed the S57 aggregator
# (vrun-*.json -> rows[] {impl, case, pass, ...}); the matrix never gates this
# seat's status and never touches any candidate's file.
MATRIX="$BK/matrix.tsv"
printf 'impl\tcase\tpass\tgot\twant\trc\tcmd\tdetail\n' > "$MATRIX"
EMPTY_LEDGER="$WORK/empty-ledger.tsv"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$EMPTY_LEDGER"

norm_verdict() { # SAFE/VERIFIED(x) -> POSITIVE | NOT-SAFE/NOT-VERIFIED(x) -> NEGATIVE
  case "$1" in
    NOT-VERIFIED*|NOT-SAFE*) printf 'NEGATIVE\n' ;;
    VERIFIED*|SAFE*)         printf 'POSITIVE\n' ;;
    *)                       printf 'NONE\n' ;;
  esac
}
verdict_for() { # <outfile> <target> [<canonical-target>] -> raw verdict token
  local f=$1; shift
  local v="" t
  for t in "$@"; do
    v=$(awk -F'\t' -v t="$t" 'NF>=3 && $2==t && ($3=="SAFE"||$3=="NOT-SAFE"){print $3; exit}' "$f")
    [ -n "$v" ] && break
  done
  if [ -z "$v" ]; then
    for t in "$@"; do
      v=$(awk -F'\t' -v t="$t" 'NF>=2 && $2==t {print $1; exit}' "$f")
      [ -n "$v" ] && break
    done
  fi
  printf '%s' "${v:-NONE}"
}
matrix_selftest() { # <impl> <impl-sha>
  local impl=$1 isha=$2 out rc p
  out="$BK/mx-$(basename "$impl" .sh)-selftest.out"
  rc=0
  ( cd "$ROOT" && timeout 120 bash "$impl" --selftest >"$out" 2>&1 ) || rc=$?
  p=0; [ "$rc" = 0 ] && p=1
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(basename "$impl" .sh)" "--selftest" "$p" "exit=$rc" "exit=0" "$rc" \
    "bash $(basename "$impl") --selftest" "sha256=${isha:0:12} tail=$(tail -1 "$out" | cut -c1-120 | tr '\t' ' ')" \
    >> "$MATRIX"
}
matrix_case() { # <impl> <impl-sha> <ledger> <target> <POSITIVE|NEGATIVE> <case-id>
  local impl=$1 isha=$2 lg=$3 tgt=$4 want=$5 id=$6 out rc v got p canon
  out="$BK/mx-$(basename "$impl" .sh)-$id.out"
  canon=$(readlink -m -- "$tgt" 2>/dev/null || printf '%s' "$tgt")
  rc=0
  ( cd "$ROOT" && env SOUJI_LEDGER="$lg" timeout 60 bash "$impl" "$tgt" >"$out" 2>&1 ) || rc=$?
  case $rc in
    124|126|127) v="rc=$rc"; got=NONE ;;
    *) v=$(verdict_for "$out" "$tgt" "$canon"); got=$(norm_verdict "$v") ;;
  esac
  p=0; [ "$got" = "$want" ] && p=1
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(basename "$impl" .sh)" "$id" "$p" "${v//$'\t'/ }" "$want" "$rc" \
    "bash $(basename "$impl") $tgt" "sha256=${isha:0:12}" >> "$MATRIX"
}
for impl in "$ROOT"/tools/souji-vault-verify.impl-*.sh; do
  [ -f "$impl" ] || continue
  ISHA=$(sha256sum "$impl" | cut -d' ' -f1)
  matrix_selftest "$impl" "$ISHA"
  matrix_case "$impl" "$ISHA" "$LEDGER"       "$SP_KEPT"  POSITIVE fixture-ledger-match
  matrix_case "$impl" "$ISHA" "$LEDGER"       "$SP_STALE" NEGATIVE fixture-edited-after-row
  matrix_case "$impl" "$ISHA" "$LEDGER"       "$SP_MIS"   NEGATIVE fixture-source-sha-mismatch
  matrix_case "$impl" "$ISHA" "$LEDGER"       "$SP_ABS"   NEGATIVE fixture-vault-absent
  if [ "$REAL_OK" = true ]; then
    matrix_case "$impl" "$ISHA" "$LEDGER" "$SP_HOME"     POSITIVE real-vault-match
    matrix_case "$impl" "$ISHA" "$LEDGER" "$SP_HOME_BAD" NEGATIVE real-vault-hash-mismatch
    matrix_case "$impl" "$ISHA" "$LEDGER" "$SP_HOME_ABS" NEGATIVE real-vault-file-absent
  fi
  if [ "$REAL_ATLAS" = true ]; then
    matrix_case "$impl" "$ISHA" "$LEDGER" "$SP_ATLAS_DIR" POSITIVE real-vault-dir-digest
  fi
  matrix_case "$impl" "$ISHA" "$EMPTY_LEDGER" "$SP_KEPT" NEGATIVE header-only-ledger
done
MX_N=$(($(grep -c . "$MATRIX" || true) - 1)); MX_N=${MX_N:-0}
MX_P=$(awk -F'\t' 'NR>1 && $3=="1"' "$MATRIX" | wc -l | tr -d ' ')
note "matrix.candidates" "M0" "candidate rows=$MX_N pass=$MX_P impls=$(awk -F'\t' 'NR>1{print $1}' "$MATRIX" | sort -u | tr '\n' ' ')"

# ------------------------------------------------------------------- report
mkdir -p "$(dirname "$RESULTS")"
TOOL_EXISTS_STR=$([ "$TOOL_EXISTS" = true ] && echo 1 || echo 0)
python3 - "$RTSV" "$RESULTS" "$TOOL" "$TOOL_SHA" "$TOOL_SYNTAX" "$SPEC_SHA" "$RUNNER_SHA" \
        "$SEAT" "$LANE_HEAD" "$VAULT" "$VAULT_HEAD" "$FP_BEFORE_SUM" "$FP_AFTER_SUM" \
        "$LIVE_LEDGER_SHA_START" "$LIVE_LEDGER_SHA_END" "$LEDGER" "$ENV_VARS" "$WORK" "$ROOT" \
        "$TOOL_EXISTS_STR" "$MATRIX" <<'PY'
import json, sys, collections, datetime, os

(tsv, out_path, tool, tool_sha, tool_syntax, spec_sha, runner_sha,
 seat, lane_head, vault, vault_head, fp_before, fp_after,
 ll_sha_start, ll_sha_end, test_ledger, env_vars, work, root, tool_exists_str,
 matrix_tsv) = sys.argv[1:22]

def san(s):
    return (s or "").replace(work, "<work>")

def rel(p):
    if not p:
        return None
    ap = os.path.abspath(p)
    return ap[len(root) + 1:] if ap.startswith(root + os.sep) else ap

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
    "tool": {"path": rel(tool),
             "exists": bool(tool and os.path.isfile(tool)), "sha256": tool_sha or None,
             "bash_syntax": tool_syntax},
    "spec": {"path": "tools/souji-verify.spec.md", "sha256": spec_sha},
    "vault": {"path": vault, "head": vault_head,
              "fingerprint_before": fp_before, "fingerprint_after": fp_after,
              "unchanged": fp_before == fp_after},
    "live_ledger": {"path": "corpus/knowledge/obsidian-ledger.tsv",
                    "sha256_start": ll_sha_start, "sha256_end": ll_sha_end,
                    "header_only": ll_sha_start == ll_sha_end},
    "test_ledger": rel(test_ledger),
    "method": {
        "independence": "own fixtures under tests/vault/fixture-*-<seat>/ + own ledger tests/vault/vrun-<seat>-ledger.tsv; no other seat's fixtures or ledgers consumed",
        "vault_access": "read-only: sha256sum/find/stat/git-rev-parse only; no writes, no notes created, no git index-refresh commands run against the vault",
        "gui_policy": "the GUI launcher /usr/bin/obsidian is never executed; obsidian-cli-inspector probed with timeout 5 (--version/--help only)",
        "env_passed_to_tool": ["SOUJI_LEDGER"],
        "env_overrides_declared_in_tool_source": env_vars.split() if env_vars.strip() else [],
        "tool_selection": "first existing of tools/souji-vault-verify.sh, tools/obsidian-vault-verify.sh, tools/vault-verify.sh, tools/souji-verify.sh (or --tool); tools/souji-vault-verify.impl-*.sh candidates run in the additive matrix, never as the selected tool",
        "candidate_matrix": "every tools/souji-vault-verify.impl-*.sh runs --selftest + 8 fixture/real-vault/dir-digest/negative cases with SOUJI_LEDGER pointed at this seat's ledger; rows are additive and never gate this seat's status",
    },
    "counts": {"total": len(checks), "pass": counts["pass"], "fail": counts["fail"],
               "skip": counts["skip"], "info": counts["info"]},
    "failed_checks": fails,
    "skipped_checks": skipped,
    "checks": checks,
}
rows = []
try:
    with open(matrix_tsv) as fh:
        header = fh.readline().rstrip("\n").split("\t")
        for raw in fh:
            if not raw.strip():
                continue
            f = (raw.rstrip("\n").split("\t") + [""] * 8)[:8]
            rows.append({
                "impl": f[0], "case": f[1],
                "pass": f[2] == "1", "got": san(f[3]), "want": f[4],
                "rc": int(f[5]) if f[5].strip().lstrip("-").isdigit() else None,
                "cmd": san(f[6]), "detail": san(f[7]),
            })
except OSError:
    pass
if rows:
    report["rows"] = rows
    report["candidate_matrix"] = {
        "rows": len(rows),
        "pass": sum(1 for r in rows if r["pass"]),
        "impls": sorted({r["impl"] for r in rows}),
        "cases": sorted({r["case"] for r in rows}),
    }
if tool_exists_str != "1":
    report["status"] = "blocked"
    report["exit_code"] = 3
with open(out_path, "w") as fh:
    json.dump(report, fh, indent=2)
    fh.write("\n")
print("runner-%s: status=%s exit=%d pass=%d fail=%d skip=%d info=%d tool=%s"
      % (seat, report["status"], report["exit_code"], counts["pass"], counts["fail"],
         counts["skip"], counts["info"], os.path.basename(tool)))
if fails:
    print("failed: " + ", ".join(fails))
PY

exit "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["exit_code"])' "$RESULTS")"
