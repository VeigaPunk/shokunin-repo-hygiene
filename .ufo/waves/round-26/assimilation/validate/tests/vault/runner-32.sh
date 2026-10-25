#!/usr/bin/env bash
# runner-32.sh — round-4 vault-verification runner (SEAT S32, "identical" runner).
#
# Independent by construction: builds its OWN fixtures under
# tests/vault/fixture-*-32/ and a test ledger at tests/vault/vrun-32-ledger.tsv;
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
#   5. CLI entry-point probe: obsidian-cli-inspector (timeout 5, --version /
#      --help only). The GUI launcher /usr/bin/obsidian is NEVER executed —
#      stat/grep/pgrep evidence only.
#   6. seat-specific (S32): the inspector is exercised in an ISOLATED config
#      (config/logs/db under /tmp) against this runner's own fixture vault,
#      never against the real vault; its describe "Hash" field is shown to be
#      a size:mtime pseudo-hash, not a sha256 oracle (reproduces the S35
#      finding); ~/.config/obsidian-cli-inspector is stat-checked before and
#      after to prove no config/log writes.
#
# Check IDs V1..V13 / A0..A4 / C1..C11 mirror the S39/S40 twins so the parent
# can diff vrun-32.json vs vrun-39/40.json row by row. D1..D4 are the
# S32-specific inspector rows (informational unless marked counted).
#
# usage: tests/vault/runner-32.sh [--seat N] [--tool PATH] [--results PATH]
#                                 [--vault PATH] [--wait SECS] [--keep]
#   --seat N    seat number (default 32) — suffixes fixtures and output name
#   --tool      tool under test; default: first existing of
#               tools/souji-vault-verify.sh, tools/obsidian-vault-verify.sh,
#               tools/vault-verify.sh, tools/souji-verify.sh
#               (with --wait, tools/souji-vault-verify.impl-*.sh are polled
#               first and the newest wins over the plain names)
#   --results   JSON report path (default <lane>/tests/results/vrun-<seat>.json)
#   --vault     real vault path (default /home/vgpnk/Documents/shokoknowledge)
#   --wait S    poll up to S seconds for tools/souji-vault-verify*.sh to land
#   --keep      keep the mktemp scratch dir (default: removed)
# exit: 0 all counted checks pass | 1 any counted check failed | 2 usage
#       | 3 tool missing (report written with status=blocked)
set -uo pipefail
export LC_ALL=C

SELF_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$SELF_DIR/../.." && pwd)       # lane repo root (this file lives in tests/vault/)
SEAT=32
TOOL=""
RESULTS=""
VAULT="/home/vgpnk/Documents/shokoknowledge"
KEEP=0
WAIT=0
TOOL_TIMEOUT=120

die_usage() { printf 'runner-32.sh: %s\n' "$1" >&2; exit 2; }
while [ $# -gt 0 ]; do
  case "$1" in
    --seat)    [ $# -ge 2 ] || die_usage "--seat needs a value"; SEAT=$2; shift 2;;
    --tool)    [ $# -ge 2 ] || die_usage "--tool needs a value"; TOOL=$2; shift 2;;
    --results) [ $# -ge 2 ] || die_usage "--results needs a value"; RESULTS=$2; shift 2;;
    --vault)   [ $# -ge 2 ] || die_usage "--vault needs a value"; VAULT=$2; shift 2;;
    --wait)    [ $# -ge 2 ] || die_usage "--wait needs a value"; WAIT=$2; shift 2;;
    --keep)    KEEP=1; shift;;
    -h|--help) sed -n '2,42p' "$0"; exit 0;;
    *) die_usage "unknown argument: $1";;
  esac
done

pick_tool() {
  local cand p newest="" newest_clean=""
  for p in "$ROOT"/tools/souji-vault-verify.impl-*.sh; do
    [ -f "$p" ] || continue
    if [ -z "$newest" ] || [ "$p" -nt "$newest" ]; then newest=$p; fi
    if bash -n "$p" 2>/dev/null; then
      if [ -z "$newest_clean" ] || [ "$p" -nt "$newest_clean" ]; then newest_clean=$p; fi
    fi
  done
  # prefer the newest syntax-clean impl; a broken newest impl is still reported
  # (tool.syntax fail) only when no clean impl exists
  [ -n "$newest_clean" ] && { printf '%s\n' "$newest_clean"; return 0; }
  [ -n "$newest" ] && { printf '%s\n' "$newest"; return 0; }
  for cand in "$ROOT/tools/souji-vault-verify.sh" "$ROOT/tools/obsidian-vault-verify.sh" \
              "$ROOT/tools/vault-verify.sh" "$ROOT/tools/souji-verify.sh"; do
    [ -f "$cand" ] && { printf '%s\n' "$cand"; return 0; }
  done
  return 1
}

if [ -z "$TOOL" ] && [ "$WAIT" -gt 0 ]; then
  deadline=$(( $(date +%s) + WAIT ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    if compgen -G "$ROOT/tools/souji-vault-verify*.sh" >/dev/null 2>&1; then break; fi
    sleep 10
  done
fi
[ -n "$TOOL" ] || TOOL=$(pick_tool || true)
[ -z "$RESULTS" ] && RESULTS="$ROOT/tests/results/vrun-$SEAT.json"

WORK=$(mktemp -d /tmp/souji32-vault.XXXXXX)
case "$WORK" in /tmp/souji32-vault.*) : ;; *) echo "refusing: WORK=$WORK" >&2; exit 9;; esac
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
if [ -n "$TOOL" ] && [ -f "$TOOL" ]; then
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

# ~/.config/obsidian-cli-inspector stat before (no config/log writes allowed)
CFG_DIR="$HOME/.config/obsidian-cli-inspector"
CFG_STAT_BEFORE=$(stat -c 'mtime=%Y size=%s' "$CFG_DIR" 2>/dev/null || echo absent)
CFG_DB_STAT_BEFORE=$(stat -c 'mtime=%Y size=%s' "$CFG_DIR/vault.db" 2>/dev/null || echo absent)

# ------------------------------------------------------------------ CLI runs
OUT_TEXT=""; OUT_ERR=""; OUT_CODE=0
RUN_ENV=(SOUJI_LEDGER="$LEDGER")
run_tool() {
  local rc=0
  OUT_TEXT=$(env "${RUN_ENV[@]}" timeout "$TOOL_TIMEOUT" bash "$TOOL" "$@" 2>"$BK/stderr") || rc=$?
  OUT_CODE=$rc
  OUT_ERR=$(cat "$BK/stderr" 2>/dev/null || true)
  { printf '### args:'; printf ' [%s]' "$@"; printf '\n--stdout--\n%s\n--stderr--\n%s\n--rc=%s\n' \
      "$OUT_TEXT" "$OUT_ERR" "$rc"; } >> "$BK/tool-output.all"
}
line_of() { printf '%s\n' "$OUT_TEXT" | awk -F'\t' -v t="$1" 'NF>=3 && $2==t {print; f=1} END{if(!f) exit 1}'; }

vnorm() { # verdict-vocabulary bridge: r2 SAFE/NOT-SAFE <-> r4 VERIFIED/NOT-VERIFIED
  local v=$1
  v=${v%%\(*}
  case "$v" in
    VERIFIED|SAFE) printf 'SAFE' ;;
    NOT-VERIFIED|NOT_VERIFIED|NOT-SAFE|NOT_SAFE) printf 'NOT-SAFE' ;;
    *) printf '%s' "$1" ;;
  esac
}

assert_line() { # id name target want-verdict receipt-regex evidence-regex [rc]
  # Accepts both output shapes:
  #   r2: VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence
  #   r4: VERIFIED|NOT-VERIFIED(reason)<TAB>path<TAB>receipt<TAB>evidence
  # Receipt/evidence regexes are matched against receipt+verdict / evidence+verdict
  # so a r4 reason embedded in the verdict field still satisfies an r2 evidence check.
  local id=$1 name=$2 tgt=$3 wv=$4 wre=${5:-} ere=${6:-} wrc=${7:-}
  local line
  if ! line=$(line_of "$tgt"); then
    record "$id" "$name" fail "line for '$tgt' -> $wv" "no line with field2=='$tgt' (rc=$OUT_CODE)" "$OUT_CODE" "$OUT_ERR"
    return 0
  fi
  local f1 v r e status=pass detail=""
  f1=$(printf '%s' "$line" | awk -F'\t' '{print $1}')
  if [ "$f1" = "VERDICT" ]; then
    v=$(printf '%s' "$line" | awk -F'\t' '{print $3}')
    r=$(printf '%s' "$line" | awk -F'\t' '{print $4}')
    e=$(printf '%s' "$line" | awk -F'\t' '{print $5}')
  else
    v=$f1
    r=$(printf '%s' "$line" | awk -F'\t' '{print $3}')
    e=$(printf '%s' "$line" | awk -F'\t' '{print $4}')
  fi
  if [ "$wv" != ANY ] && [ "$(vnorm "$v")" != "$(vnorm "$wv")" ]; then
    status=fail; detail="verdict=$v want=$wv; "
  fi
  if [ -n "$wre" ] && ! printf '%s\n%s' "$r" "$v" | grep -Eq "$wre"; then status=fail; detail="${detail}receipt='$r' !~ /$wre/; "; fi
  if [ -n "$ere" ] && ! printf '%s\n%s\n%s' "$e" "$v" "$r" | grep -Eq "$ere"; then status=fail; detail="${detail}evidence='$e' !~ /$ere/; "; fi
  if [ -n "$wrc" ] && [ "$OUT_CODE" != "$wrc" ]; then status=fail; detail="${detail}rc=$OUT_CODE want=$wrc; "; fi
  record "$id" "$name" "$status" "$wv r~/$wre/ e~/$ere/" "rc=$OUT_CODE line=$line" "$OUT_CODE" "$detail"
}

# ------------------------------------------------------------- tool presence
if [ "$TOOL_EXISTS" != true ]; then
  note "tool.present" "A0" "tool absent: ${TOOL:-none found under tools/}"
  for c in tool.syntax selftest.exit V1.fixture-ledger-match V2.fixture-edited-after-row \
           V3.fixture-source-sha-mismatch V4.fixture-vault-absent V5.real-vault-match \
           V6.real-vault-hash-mismatch V7.real-vault-file-absent V8.real-vault-dir-digest \
           V9.determinism V10.json-parse V11.batch-match V11.batch-edited V11.batch-absent; do
    record "$c" "P0" skip "tool missing" "not run" "" "no tool at ${TOOL:-none}"
  done
else
  note "tool.present" "A0" "path=$TOOL sha256=$TOOL_SHA syntax=$TOOL_SYNTAX mode=$(stat -c %A "$TOOL")"
  info_kv "tool.interface" "A3" "env vars referenced: ${ENV_VARS:-none}"
  if bash -n "$TOOL" 2>/dev/null; then
    record "tool.syntax" "A1" pass "bash -n exit 0" "exit 0" 0 ""
  else
    record "tool.syntax" "A1" fail "bash -n exit 0" "syntax error" 1 "$TOOL_SYNTAX"
  fi

  # --- tool's own selftest (must cover its F1-F10 + vault cases)
  TOOL_TIMEOUT=300 run_tool --selftest
  if [ "$OUT_CODE" = 0 ]; then
    record "selftest.exit" "A2" pass "exit 0" "exit=0 $(printf '%s' "$OUT_TEXT" | tail -1 | cut -c1-160)" 0 ""
  else
    record "selftest.exit" "A2" fail "exit 0" "exit=$OUT_CODE $(printf '%s' "$OUT_TEXT" | tail -1 | cut -c1-160)" "$OUT_CODE" "$OUT_ERR"
  fi
  TOOL_TIMEOUT=120

  # --- fixture-vault rows
  run_tool "$SP_KEPT"
  assert_line "V1.fixture-ledger-match" "V1" "$SP_KEPT" SAFE '^moved-to-obsidian$' 'vault=' 0
  run_tool "$SP_STALE"
  assert_line "V2.fixture-edited-after-row" "V2" "$SP_STALE" NOT-SAFE '^(none|.*)$' 'vault-sha-mismatch' 0
  run_tool "$SP_MIS"
  assert_line "V3.fixture-source-sha-mismatch" "V3" "$SP_MIS" NOT-SAFE '^(none|.*)$' 'source-sha-mismatch' 0
  run_tool "$SP_ABS"
  assert_line "V4.fixture-vault-absent" "V4" "$SP_ABS" NOT-SAFE '^(none|.*)$' 'vault-(unreachable|absent)' 0

  # --- REAL vault rows (read-only on the vault side)
  if [ "$REAL_OK" = true ]; then
    run_tool "$SP_HOME"
    assert_line "V5.real-vault-match" "V5" "$SP_HOME" SAFE '^moved-to-obsidian$' "$VAULT/Home\.md" 0
    run_tool "$SP_HOME_BAD"
    assert_line "V6.real-vault-hash-mismatch" "V6" "$SP_HOME_BAD" NOT-SAFE '^(none|.*)$' 'vault-sha-mismatch' 0
    run_tool "$SP_HOME_ABS"
    assert_line "V7.real-vault-file-absent" "V7" "$SP_HOME_ABS" NOT-SAFE '^(none|.*)$' 'vault-(unreachable|absent)' 0
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
  assert_line "V11.batch-edited" "V11" "$SP_STALE" NOT-SAFE '^(none|.*)$' 'vault-sha-mismatch' 0
  assert_line "V11.batch-absent" "V11" "$SP_ABS" NOT-SAFE '^(none|.*)$' 'vault-(unreachable|absent)' 0
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
PKG1=$(dpkg -S /usr/bin/obsidian 2>/dev/null || pacman -Qo /usr/bin/obsidian 2>/dev/null || echo unowned)
PKG2=$(dpkg -S /usr/bin/obsidian-cli-inspector 2>/dev/null || pacman -Qo /usr/bin/obsidian-cli-inspector 2>/dev/null || echo unowned)
info_kv "C9.pkg-owner" "C9" "obsidian: $PKG1 | inspector: $PKG2"
VAULT_HEAD=$(git --git-dir="$VAULT/.git" rev-parse HEAD 2>/dev/null || echo unknown)
info_kv "C10.vault-head" "C10" "vault HEAD=$VAULT_HEAD (read-only rev-parse)"
SOCK="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/.obsidian-cli.sock"
if [ -S "$SOCK" ]; then
  SOCK_OWNER=$(ss -xlp 2>/dev/null | grep -F "$SOCK" | head -1 | grep -oE 'pid=[0-9]+' | head -1)
  info_kv "C12.cli-socket" "C12" "PRESENT $SOCK ($SOCK_OWNER) — observed via ss only; this runner never connects or sends (socket use belongs to the CLI-recon seats)"
else
  info_kv "C12.cli-socket" "C12" "absent $SOCK (app not running or CLI never enabled)"
fi
IMPL_CENSUS=""
for p in "$ROOT"/tools/souji-vault-verify*.sh "$ROOT"/tools/obsidian-vault-verify*.sh "$ROOT"/tools/vault-verify*.sh; do
  [ -f "$p" ] || continue
  if bash -n "$p" 2>/dev/null; then s=ok; else s=BROKEN; fi
  IMPL_CENSUS="${IMPL_CENSUS}$(basename "$p")=$s "
done
info_kv "C13.impl-census" "C13" "round-4 candidates under tools/: ${IMPL_CENSUS:-none} (tool under test: $(basename "${TOOL:-none}"))"

# --- S32-specific: isolated inspector run against OUR fixture vault only -----
# Config/logs/db all live under $WORK; the real vault is never indexed here.
ISO="$WORK/iso"; mkdir -p "$ISO"
if [ -n "$CLI_BIN" ]; then
  cat > "$ISO/config.toml" <<EOF
vault_path = "$FXVAULT"
database_path = "$ISO/vault.db"
log_path = "$ISO/logs"
EOF
  IS1_OUT=$(timeout 10 "$CLI_BIN" -c "$ISO/config.toml" init init 2>&1); IS1_RC=$?
  record "D1.inspector-iso-init" "D1" "$([ "$IS1_RC" = 0 ] && echo pass || echo fail)" "exit 0 (fixture vault, db under /tmp)" \
    "rc=$IS1_RC $(printf '%s' "$IS1_OUT" | head -1 | cut -c1-120)" "$IS1_RC" ""
  IS2_OUT=$(timeout 30 "$CLI_BIN" -c "$ISO/config.toml" index index 2>&1); IS2_RC=$?
  IS_NOTES=$(printf '%s' "$IS2_OUT" | grep -oE '(Found [0-9]+ markdown files|Indexed [0-9]+ notes successfully)' | tr '\n' ' ')
  record "D2.inspector-iso-index" "D2" "$([ "$IS2_RC" = 0 ] && echo pass || echo fail)" "exit 0, indexes the fixture vault" \
    "rc=$IS2_RC ${IS_NOTES:-no-index-line} $(printf '%s' "$IS2_OUT" | tail -1 | cut -c1-120)" "$IS2_RC" ""
  DB_IN_TMP=$([ -f "$ISO/vault.db" ] && echo yes || echo no)
  IS3_OUT=$(timeout 10 "$CLI_BIN" -c "$ISO/config.toml" view describe "kept-$SEAT.md" 2>&1); IS3_RC=$?
  IS_HASH=$(printf '%s' "$IS3_OUT" | awk -F'[[:space:]]+' '/[Hh]ash/{print $NF; exit}')
  KEPT_SHA=$(sha256sum "$VP_KEPT" | cut -d' ' -f1)
  if [ -n "$IS_HASH" ] && [ "$IS_HASH" != "$KEPT_SHA" ]; then
    record "D3.inspector-hash-not-sha256" "D3" pass "describe Hash != sha256sum (pseudo-hash, not an oracle)" \
      "describe_hash=$IS_HASH sha256=$KEPT_SHA db_in_tmp=$DB_IN_TMP rc=$IS3_RC" "$IS3_RC" ""
  elif [ "$IS_HASH" = "$KEPT_SHA" ]; then
    record "D3.inspector-hash-not-sha256" "D3" fail "describe Hash != sha256sum" \
      "describe_hash=$IS_HASH equals sha256 (unexpected: inspector could be an oracle)" "$IS3_RC" ""
  else
    record "D3.inspector-hash-not-sha256" "D3" fail "describe Hash field present" \
      "no Hash field in describe output: $(printf '%s' "$IS3_OUT" | head -c 160)" "$IS3_RC" ""
  fi
  CFG_STAT_AFTER=$(stat -c 'mtime=%Y size=%s' "$CFG_DIR" 2>/dev/null || echo absent)
  CFG_DB_STAT_AFTER=$(stat -c 'mtime=%Y size=%s' "$CFG_DIR/vault.db" 2>/dev/null || echo absent)
  if [ "$CFG_STAT_BEFORE" = "$CFG_STAT_AFTER" ] && [ "$CFG_DB_STAT_BEFORE" = "$CFG_DB_STAT_AFTER" ]; then
    record "D4.no-userconfig-writes" "D4" pass "~/.config/obsidian-cli-inspector stat unchanged" \
      "dir=$CFG_STAT_AFTER db=$CFG_DB_STAT_AFTER" 0 ""
  else
    record "D4.no-userconfig-writes" "D4" fail "~/.config/obsidian-cli-inspector stat unchanged" \
      "dir ${CFG_STAT_BEFORE}->${CFG_STAT_AFTER} db ${CFG_DB_STAT_BEFORE}->${CFG_DB_STAT_AFTER}" 0 ""
  fi
  info_kv "D5.inspector-iso-artifacts" "D5" "iso dir kept in scratch: config=$(basename "$ISO/config.toml") db=$DB_IN_TMP logs=$(ls "$ISO/logs" 2>/dev/null | wc -l) files"
else
  for c in D1.inspector-iso-init D2.inspector-iso-index D3.inspector-hash-not-sha256 D4.no-userconfig-writes; do
    record "$c" "D1" skip "obsidian-cli-inspector present" "not in PATH" "" ""
  done
fi

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

# ------------------------------------------------------------------- report
mkdir -p "$(dirname "$RESULTS")"
python3 - "$RTSV" "$RESULTS" "$TOOL" "$TOOL_SHA" "$TOOL_SYNTAX" "$SPEC_SHA" "$RUNNER_SHA" \
        "$SEAT" "$LANE_HEAD" "$VAULT" "$VAULT_HEAD" "$FP_BEFORE_SUM" "$FP_AFTER_SUM" \
        "$LIVE_LEDGER_SHA_START" "$LIVE_LEDGER_SHA_END" "$LEDGER" "$ENV_VARS" "$WORK" "$ROOT" <<'PY'
import json, sys, collections, datetime, os

(tsv, out_path, tool, tool_sha, tool_syntax, spec_sha, runner_sha,
 seat, lane_head, vault, vault_head, fp_before, fp_after,
 ll_sha_start, ll_sha_end, test_ledger, env_vars, work, repo_root) = sys.argv[1:20]

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
    "tool": {"path": os.path.relpath(tool, repo_root) if tool and tool.startswith(repo_root) else tool,
             "exists": bool(tool and os.path.isfile(tool)), "sha256": tool_sha or None,
             "bash_syntax": tool_syntax},
    "spec": {"path": "tools/souji-verify.spec.md", "sha256": spec_sha},
    "vault": {"path": vault, "head": vault_head,
              "fingerprint_before": fp_before, "fingerprint_after": fp_after,
              "unchanged": fp_before == fp_after},
    "live_ledger": {"path": "corpus/knowledge/obsidian-ledger.tsv",
                    "sha256_start": ll_sha_start, "sha256_end": ll_sha_end,
                    "header_only": ll_sha_start == ll_sha_end},
    "test_ledger": os.path.relpath(test_ledger, repo_root) if test_ledger.startswith(repo_root) else test_ledger,
    "method": {
        "independence": "own fixtures under tests/vault/fixture-*-<seat>/ + own ledger tests/vault/vrun-<seat>-ledger.tsv; no other seat's fixtures or ledgers consumed",
        "vault_access": "read-only: sha256sum/find/stat/git-rev-parse only; no writes, no notes created, no git index-refresh commands run against the vault",
        "gui_policy": "the GUI launcher /usr/bin/obsidian is never executed; obsidian-cli-inspector probed with timeout 5 (--version/--help only); the isolated index run targets only the runner's own fixture vault with config/db/logs under the scratch dir",
        "env_passed_to_tool": ["SOUJI_LEDGER"],
        "env_overrides_declared_in_tool_source": env_vars.split() if env_vars.strip() else [],
        "tool_selection": "newest tools/souji-vault-verify.impl-*.sh else first existing of tools/souji-vault-verify.sh, tools/obsidian-vault-verify.sh, tools/vault-verify.sh, tools/souji-verify.sh (or --tool)",
    },
    "counts": {"total": len(checks), "pass": counts["pass"], "fail": counts["fail"],
               "skip": counts["skip"], "info": counts["info"]},
    "failed_checks": fails,
    "skipped_checks": skipped,
    "checks": checks,
}
with open(out_path, "w") as fh:
    json.dump(report, fh, indent=2)
    fh.write("\n")
print("runner-%s: status=%s exit=%d pass=%d fail=%d skip=%d info=%d tool=%s"
      % (seat, status, exit_code, counts["pass"], counts["fail"], counts["skip"],
         counts["info"], os.path.basename(tool) if tool else "none"))
if fails:
    print("failed: " + ", ".join(fails))
PY

exit "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["exit_code"])' "$RESULTS")"
