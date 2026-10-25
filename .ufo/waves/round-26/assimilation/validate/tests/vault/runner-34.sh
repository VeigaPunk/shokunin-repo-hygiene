#!/usr/bin/env bash
# tests/vault/runner-34.sh — round-4 vault-verification runner (SEAT S34,
# "identical" runner). Writes tests/results/vrun-34.json.
#
# Runs the SAME battery over every candidate tool matching
# tools/souji-vault-verify*.sh (default glob; --impls to narrow), plus the
# installed tools/souji-verify.sh as a baseline when no candidate exists yet.
# Emits rows [{impl, case, pass, got, want}] (S57 aggregator schema) plus a
# flat checks[] list and the harness invariants.
#
# Independent by construction: builds its OWN fixtures under a mktemp -d in
# /tmp and its OWN test ledger at tests/vault/vrun-34-ledger.tsv; never
# consumes tests/fixtures/** or any other seat's ledger or fixtures.
#
# What it verifies (round 4: Obsidian-CLI vault verification):
#   1. ledger-backed moved-to-obsidian receipts of the tool under test on
#      fixture vault rows (match / edited-after-row / source-mismatch /
#      vault-absent / source-absent);
#   2. the same receipt path against the REAL vault
#      (/home/vgpnk/Documents/shokoknowledge) — read-only: the vault side is
#      only ever hashed, and a deliberately wrong vault hash must NOT be SAFE;
#   3. the real vault is untouched by the whole battery (sha256 manifest of
#      every vault file before vs after);
#   4. the live ledger corpus/knowledge/obsidian-ledger.tsv stays header-only
#      and byte-identical;
#   5. CLI entry-point probe: obsidian-cli-inspector (timeout 5, help/version
#      only). The GUI launcher /usr/bin/obsidian is NEVER executed — stat and
#      pgrep evidence only.
#
# Verdict tolerance: the r2 vocabulary (VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<...>)
# and the r4 vocabulary (VERIFIED / NOT-VERIFIED(...) single token or tab line)
# are both accepted; SAFE-class == {SAFE, VERIFIED*}, NOT-SAFE-class ==
# {NOT-SAFE*, NOT-VERIFIED*}.
#
# usage: tests/vault/runner-34.sh [--seat N] [--tool PATH] [--impls GLOB]
#                                 [--results PATH] [--vault PATH]
#                                 [--wait SECS] [--keep]
#   --seat N    seat number (default 34) — suffixes ledger and output name
#   --tool      single tool under test (skips the candidate glob)
#   --impls     glob under tools/ (default impl-*.sh)
#   --results   JSON report path (default <lane>/tests/results/vrun-<seat>.json)
#   --vault     real vault path (default /home/vgpnk/Documents/shokoknowledge)
#   --wait      seconds to wait for at least one tool (default 0)
#   --keep      keep the mktemp scratch dir (default: removed)
# exit: 0 matrix complete | 1 no rows produced | 2 usage | 3 no tool found
set -uo pipefail
export LC_ALL=C

SELF_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$SELF_DIR/../.." && pwd)       # lane repo root (runner lives in tests/vault/)
SEAT=34
TOOL=""
IMPL_GLOB=""
RESULTS=""
VAULT="/home/vgpnk/Documents/shokoknowledge"
WAIT=0
KEEP=0
TOOL_TIMEOUT=120

die_usage() { printf 'runner-%s.sh: %s\n' "$SEAT" "$1" >&2; exit 2; }
while [ $# -gt 0 ]; do
  case "$1" in
    --seat)    [ $# -ge 2 ] || die_usage "--seat needs a value"; SEAT=$2; shift 2;;
    --tool)    [ $# -ge 2 ] || die_usage "--tool needs a value"; TOOL=$2; shift 2;;
    --impls)   [ $# -ge 2 ] || die_usage "--impls needs a value"; IMPL_GLOB=$2; shift 2;;
    --results) [ $# -ge 2 ] || die_usage "--results needs a value"; RESULTS=$2; shift 2;;
    --vault)   [ $# -ge 2 ] || die_usage "--vault needs a value"; VAULT=$2; shift 2;;
    --wait)    [ $# -ge 2 ] || die_usage "--wait needs a value"; WAIT=$2; shift 2;;
    --keep)    KEEP=1; shift;;
    -h|--help) sed -n '2,46p' "$0"; exit 0;;
    *) die_usage "unknown argument: $1";;
  esac
done

impl_paths() {
  local p rp seen=""
  if [ -n "$TOOL" ]; then
    [ -f "$TOOL" ] && printf '%s\n' "$TOOL"
    return 0
  fi
  if [ -n "$IMPL_GLOB" ]; then
    for p in "$ROOT"/tools/$IMPL_GLOB; do
      [ -f "$p" ] && printf '%s\n' "$p"
    done | sort -u -V
    return 0
  fi
  # Two naming conventions are in flight this round (tools/impl-NN.sh,
  # tools/souji-vault-verify.impl-NN.sh); dedupe by realpath so a symlink
  # alias (impl-21.sh -> souji-vault-verify.impl-21.sh) runs once, not twice.
  # Canonical names first so the alias never shadows the real file.
  for p in "$ROOT"/tools/souji-vault-verify*.sh "$ROOT"/tools/impl-*.sh; do
    [ -f "$p" ] || continue
    rp=$(readlink -f -- "$p")
    case " $seen " in *" $rp "*) continue ;; esac
    seen="$seen $rp"
    printf '%s\n' "$p"
  done | sort -u -V
}
fallback_paths() {
  local cand
  for cand in \
    "$ROOT/tools/souji-vault-verify.sh" \
    "$ROOT/tools/obsidian-vault-verify.sh" \
    "$ROOT/tools/vault-verify.sh" \
    "$ROOT/tools/souji-verify.sh"; do
    [ -f "$cand" ] && { printf '%s\n' "$cand"; return 0; }
  done
  return 1
}

# ---- wait for at least one tool --------------------------------------------
deadline=$(( $(date +%s) + WAIT ))
while :; do
  n=$(impl_paths | wc -l)
  [ "$n" -gt 0 ] && break
  [ "$(date +%s)" -ge "$deadline" ] && break
  sleep 5
done
if [ "$(impl_paths | wc -l)" -eq 0 ] && [ -z "$TOOL" ]; then
  fallback_paths > "$(mktemp -u /tmp/souji34-fb.XXXXXX)" 2>/dev/null || true
  FB=$(fallback_paths || true)
  if [ -n "$FB" ]; then
    TOOL="$FB"
    printf 'runner-%s: no candidate matched %s; using fallback baseline %s\n' "$SEAT" "$IMPL_GLOB" "$TOOL" >&2
  fi
fi
[ "$(impl_paths | wc -l)" -gt 0 ] || { printf 'runner-%s.sh: no tool found under tools/\n' "$SEAT" >&2; exit 3; }
[ -z "$RESULTS" ] && RESULTS="$ROOT/tests/results/vrun-$SEAT.json"

WORK=$(mktemp -d "/tmp/souji34-vault.XXXXXX")
case "$WORK" in /tmp/souji34-vault.*) : ;; *) echo "refusing: WORK=$WORK" >&2; exit 9;; esac
BK="$WORK/.runner"; mkdir -p "$BK"
cleanup() { [ "$KEEP" = 1 ] || rm -rf "$WORK"; }
trap cleanup EXIT

RTSV="$BK/checks.tsv"; : > "$RTSV"     # harness-level checks
ROWS="$BK/rows.tsv"; : > "$ROWS"       # impl<TAB>case<TAB>pass<TAB>got<TAB>want
san_field() { local s=${1:-}; s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; printf '%s' "$s"; }
record() { # id name status expected observed exit detail
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(san_field "$1")" "$(san_field "$2")" "$(san_field "$3")" "$(san_field "$4")" \
    "$(san_field "$5")" "$(san_field "${6:-}")" "$(san_field "${7:-}")" >> "$RTSV"
}
row() { # impl case pass got want
  printf '%s\t%s\t%s\t%s\t%s\n' \
    "$(san_field "$1")" "$(san_field "$2")" "$(san_field "$3")" \
    "$(san_field "$4")" "$(san_field "$5")" >> "$ROWS"
}
note() { record "$1" "$2" info "$3" "" "" "${4:-}"; }
info_kv() { record "$1" "$2" info "" "" "" "$3"; }

# ------------------------------------------------------------------ fixtures
FX="$WORK/fx"
FXVAULT="$FX/vault"      # fixture vault (ledger target side)
FXSRC="$FX/src"          # source copies (evaluation target side)
LEDGER="$ROOT/tests/vault/vrun-$SEAT-ledger.tsv"
mkdir -p "$FXVAULT" "$FXSRC"

SP_KEPT="$FXSRC/kept-$SEAT.md";   VP_KEPT="$FXVAULT/kept-$SEAT.md"
printf 'vrun-%s fixture payload: ledger-matched artifact\n' "$SEAT" > "$SP_KEPT"
cp "$SP_KEPT" "$VP_KEPT"
SHA_KEPT=$(sha256sum "$SP_KEPT" | cut -d' ' -f1)

SP_STALE="$FXSRC/stale-row-$SEAT.md"; VP_STALE="$FXVAULT/stale-row-$SEAT.md"
printf 'vrun-%s fixture: vault copy edited after the row was written\n' "$SEAT" > "$SP_STALE"
cp "$SP_STALE" "$VP_STALE"
SHA_STALE=$(sha256sum "$SP_STALE" | cut -d' ' -f1)

SP_MIS="$FXSRC/mismatch-$SEAT.md"; VP_MIS="$FXVAULT/mismatch-$SEAT.md"
printf 'vrun-%s fixture: source sha mismatch row\n' "$SEAT" > "$SP_MIS"
cp "$SP_MIS" "$VP_MIS"
SHA_MIS=$(sha256sum "$SP_MIS" | cut -d' ' -f1)
SHA_MIS_WRONG=$(printf 'not-the-content' | sha256sum | cut -d' ' -f1)

SP_ABS="$FXSRC/absent-$SEAT.md"; VP_ABS="$FXVAULT/absent-$SEAT.md"
printf 'vrun-%s fixture: vault side never created\n' "$SEAT" > "$SP_ABS"
SHA_ABS=$(sha256sum "$SP_ABS" | cut -d' ' -f1)

SP_GONE="$FXSRC/never-created-$SEAT.md"   # source-absent row target (never created)

# --- real-vault rows (read-only: the vault side is only ever hashed)
REAL_OK=false; SHA_HOME=""
if [ -f "$VAULT/Home.md" ] && [ -r "$VAULT/Home.md" ]; then
  SHA_HOME=$(sha256sum "$VAULT/Home.md" | cut -d' ' -f1)
  REAL_OK=true
fi
SP_HOME="$FXSRC/real-home-$SEAT.md";        [ "$REAL_OK" = true ] && cp "$VAULT/Home.md" "$SP_HOME"
SP_HOME_BAD="$FXSRC/real-home-bad-$SEAT.md";[ "$REAL_OK" = true ] && cp "$VAULT/Home.md" "$SP_HOME_BAD"
SP_HOME_ABS="$FXSRC/real-home-abs-$SEAT.md";[ "$REAL_OK" = true ] && cp "$VAULT/Home.md" "$SP_HOME_ABS"

REAL_ATLAS=false; DIG_ATLAS=""; SP_ATLAS_DIR="$FXSRC/atlas-dir-$SEAT"
dig() { ( cd "$1" 2>/dev/null && find . -path './.git' -prune -o -type f -print0 \
          | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }
if [ -d "$VAULT/atlas" ] && [ -r "$VAULT/atlas" ]; then
  REAL_ATLAS=true
  mkdir -p "$SP_ATLAS_DIR"
  cp -r "$VAULT/atlas/." "$SP_ATLAS_DIR/" 2>/dev/null || true
  DIG_ATLAS=$(dig "$SP_ATLAS_DIR")
fi

# --- test ledger (rows use canonical absolute source paths, as the tool matches)
{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s fixture match\n' \
    "$SP_KEPT" "$SHA_KEPT" "$VP_KEPT" "$SHA_KEPT" "$SEAT"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s vault edited after row\n' \
    "$SP_STALE" "$SHA_STALE" "$VP_STALE" "$SHA_STALE" "$SEAT"
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
  # source-absent row (case-V5 shape): every conjunct passes except source
  # presence — the row's source path does not exist at evaluation time
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvrun-%s source absent row\n' \
    "$SP_GONE" "$SHA_KEPT" "$VP_KEPT" "$SHA_KEPT" "$SEAT"
} > "$LEDGER"
# the vault copy is edited AFTER the row was recorded -> the row must not receipt
printf 'EDIT AFTER ROW (vrun-%s)\n' "$SEAT" >> "$VP_STALE"

# ------------------------------------------------- read-only vault fingerprint
vault_fingerprint() { # $1 out-file
  {
    [ -d "$VAULT" ] || { printf 'VAULT-ABSENT\n'; return 0; }
    find "$VAULT" -type f -not -path '*/.git/*' -not -path '*/.obsidian/*' -print0 2>/dev/null \
      | sort -z | xargs -0 -r sha256sum 2>/dev/null
  } > "$1" 2>/dev/null || true
  printf 'files=%s manifest_sha=%s\n' \
    "$(grep -c . "$1" 2>/dev/null || true)" \
    "$(sha256sum "$1" 2>/dev/null | cut -d' ' -f1)"
}
FP_BEFORE_SUM=$(vault_fingerprint "$BK/vault-fp.before")

# ------------------------------------------------------------ harness state
SPEC="$ROOT/tools/souji-verify.spec.md"
SPEC_SHA=$([ -f "$SPEC" ] && sha256sum "$SPEC" | cut -d' ' -f1 || echo missing)
RUNNER_SHA=$(sha256sum "$0" | cut -d' ' -f1)
LANE_HEAD=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)
LIVE_LEDGER="$ROOT/corpus/knowledge/obsidian-ledger.tsv"
LIVE_LEDGER_SHA_START=$([ -f "$LIVE_LEDGER" ] && sha256sum "$LIVE_LEDGER" | cut -d' ' -f1 || echo missing)
LIVE_LEDGER_LINES_START=$([ -f "$LIVE_LEDGER" ] && wc -l < "$LIVE_LEDGER" || echo missing)

GUI_BEFORE=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true)
GUI_BEFORE=${GUI_BEFORE:-0}

# ------------------------------------------------------------- per-tool run
OUT_TEXT=""; OUT_ERR=""; OUT_CODE=0
run_tool() { # run_tool args... — escalate across env-only and flag interfaces
  local rc=0
  OUT_TEXT=$(env SOUJI_LEDGER="$LEDGER" timeout "$TOOL_TIMEOUT" bash "$TOOL" "$@" 2>"$BK/stderr") || rc=$?
  if [ "$rc" -eq 2 ]; then
    OUT_TEXT=$(env SOUJI_LEDGER="$LEDGER" timeout "$TOOL_TIMEOUT" bash "$TOOL" --ledger "$LEDGER" "$@" 2>"$BK/stderr") || rc=$?
  fi
  if [ "$rc" -eq 2 ]; then
    local tgt="${*: -1}"
    OUT_TEXT=$(env SOUJI_LEDGER="$LEDGER" timeout "$TOOL_TIMEOUT" bash "$TOOL" --ledger "$LEDGER" --fallback "$tgt" 2>"$BK/stderr") || rc=$?
  fi
  OUT_CODE=$rc
  OUT_ERR=$(cat "$BK/stderr" 2>/dev/null || true)
  { printf '### tool=%s args:' "$TOOL"; printf ' [%s]' "$@"; printf '\n--stdout--\n%s\n--stderr--\n%s\n--rc=%s\n' \
      "$OUT_TEXT" "$OUT_ERR" "$rc"; } >> "$BK/tool-output.all"
}
# verdict extraction, tolerant of both output conventions:
#   A (r2 form):      VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence
#   B (r4 form):      VERIFIED|NOT-VERIFIED(reason)<TAB>path<TAB>receipt<TAB>evidence
#   C (single token): VERIFIED(...) | NOT-VERIFIED(...) | SAFE(...) | NOT-SAFE(...)
# Returns "verdict<TAB>receipt<TAB>evidence" or nonzero.
line_of() {
  local t="$1" l f1
  l=$(printf '%s\n' "$OUT_TEXT" | awk -F'\t' -v t="$t" 'NF>=3 && $2==t {print; f=1} END{if(!f) exit 1}')
  if [ -n "$l" ]; then
    f1=$(printf '%s' "$l" | awk -F'\t' '{print $1}')
    if [ "$f1" = "VERDICT" ]; then
      # convention A: VERDICT <path> <verdict> <receipt> <evidence>
      printf '%s\t%s\t%s\n' \
        "$(printf '%s' "$l" | awk -F'\t' '{print $3}')" \
        "$(printf '%s' "$l" | awk -F'\t' '{print $4}')" \
        "$(printf '%s' "$l" | awk -F'\t' '{print $5}')"
      return 0
    fi
    case "$f1" in
      VERIFIED|VERIFIED\(*|NOT-VERIFIED|NOT-VERIFIED\(*|SAFE|SAFE\(*|NOT-SAFE|NOT-SAFE\(*)
        # convention B: <verdict> <path> <receipt> <evidence>
        printf '%s\t%s\t%s\n' \
          "$f1" \
          "$(printf '%s' "$l" | awk -F'\t' '{print $3}')" \
          "$(printf '%s' "$l" | awk -F'\t' '{print $4}')"
        return 0 ;;
    esac
    return 1
  fi
  # single-token line: VERIFIED / NOT-VERIFIED(...) possibly with a leading path field
  l=$(printf '%s\n' "$OUT_TEXT" | grep -aE '^(VERIFIED|NOT-VERIFIED|SAFE|NOT-SAFE)(\(|$)' | head -1)
  [ -n "$l" ] || return 1
  printf '%s\t\t\n' "${l%%$'\t'*}"
}
vclass() { # SAFE | NOT-SAFE | OTHER
  case "${1:-}" in
    SAFE|SAFE\(*|VERIFIED|VERIFIED\(*|VERIFIED[[:space:]]*) printf 'SAFE' ;;
    NOT-SAFE|NOT-SAFE\(*|NOT-VERIFIED|NOT-VERIFIED\(*|NOT-VERIFIED[[:space:]]*) printf 'NOT-SAFE' ;;
    *) printf 'OTHER' ;;
  esac
}
assert_case() { # impl id target want-class receipt-regex evidence-regex [rc]
  local impl=$1 id=$2 tgt=$3 wv=$4 wre=${5:-} ere=${6:-} wrc=${7:-}
  local parsed
  if ! parsed=$(line_of "$tgt"); then
    row "$impl" "$id" false \
      "no verdict line for target (rc=$OUT_CODE out=$(printf '%s' "$OUT_TEXT" | head -c 120 | tr '\t\n' '  '))" \
      "$wv"
    return 0
  fi
  local v r e got pass_=true detail=""
  v=$(printf '%s' "$parsed" | cut -f1)
  r=$(printf '%s' "$parsed" | cut -f2)
  e=$(printf '%s' "$parsed" | cut -f3)
  got=$(vclass "$v")
  [ "$wv" = ANY ] || [ "$got" = "$wv" ] || { pass_=false; detail="verdict=$v class=$got want=$wv; "; }
  if [ -n "$wre" ] && ! printf '%s' "$r" | grep -Eq "$wre"; then pass_=false; detail="${detail}receipt='$r' !~ /$wre/; "; fi
  if [ -n "$ere" ] && ! printf '%s' "$e" | grep -Eq "$ere"; then pass_=false; detail="${detail}evidence='$e' !~ /$ere/; "; fi
  if [ -n "$wrc" ] && [ "$OUT_CODE" != "$wrc" ]; then pass_=false; detail="${detail}rc=$OUT_CODE want=$wrc; "; fi
  row "$impl" "$id" "$pass_" "rc=$OUT_CODE v=$v r=$r e=$e $detail" \
    "$wv r~/$wre/ e~/$ere/ rc=$wrc"
}

: > "$BK/impls.txt"
impl_paths > "$BK/impls.txt"
while IFS= read -r tp; do
  [ -n "$tp" ] || continue
  SRC_TOOL="$tp"
  impl="$(basename "$tp")"; impl="${impl%.sh}"
  SHIPPED_MODE=$(stat -c %A "$tp")
  TOOL_SHA=$(sha256sum "$tp" | cut -d' ' -f1)
  # Candidates may ship mode 644 while their selftests self-invoke (env $SELF).
  # Run an executable copy from scratch (r2 reviewer precedent); the shipped
  # mode and sha256 are recorded so the lane can chmod the installed winner.
  TOOL="$BK/$impl.sh"
  cp -p "$tp" "$TOOL"; chmod u+x "$TOOL"
  printf '%s\n' "$tp" >> "$BK/impls-run.txt"
  TOOL_SYNTAX="missing"
  bash -n "$TOOL" 2>"$BK/syntax.err" && TOOL_SYNTAX=ok || TOOL_SYNTAX=$(head -c 300 "$BK/syntax.err")
  ENV_VARS=$(rg -o --no-filename '\$\{?[A-Z][A-Z0-9_]{2,}\}?' "$TOOL" 2>/dev/null \
             | tr -d '${}' | sort -u | tr '\n' ' ' || true)
  record "tool.present[$impl]" "A0" info "path=$tp shipped_mode=$SHIPPED_MODE sha256=$TOOL_SHA syntax=$TOOL_SYNTAX" "" ""
  info_kv "tool.interface[$impl]" "A3" "env vars referenced: ${ENV_VARS:-none}"

  # --- tool's own selftest
  TOOL_TIMEOUT=300 run_tool --selftest
  row "$impl" "--selftest" "$([ "$OUT_CODE" = 0 ] && echo true || echo false)" \
    "exit=$OUT_CODE $(printf '%s' "$OUT_TEXT" | tail -1 | cut -c1-120)" "exit=0"
  printf '%s' "$OUT_TEXT" > "$BK/st-${impl}.log"
  TOOL_TIMEOUT=120

  # --- fixture-vault rows
  run_tool "$SP_KEPT"
  assert_case "$impl" "V1.fixture-ledger-match" "$SP_KEPT" SAFE '^moved-to-obsidian$' 'vault=' 0
  run_tool "$SP_STALE"
  assert_case "$impl" "V2.fixture-edited-after-row" "$SP_STALE" NOT-SAFE '' '' 0
  run_tool "$SP_MIS"
  assert_case "$impl" "V3.fixture-source-sha-mismatch" "$SP_MIS" NOT-SAFE '' '' 0
  run_tool "$SP_ABS"
  assert_case "$impl" "V4.fixture-vault-absent" "$SP_ABS" NOT-SAFE '' '' 0

  # --- REAL vault rows (read-only on the vault side)
  if [ "$REAL_OK" = true ]; then
    run_tool "$SP_HOME"
    assert_case "$impl" "V5.real-vault-match" "$SP_HOME" SAFE '^moved-to-obsidian$' "$VAULT/Home\.md" 0
    run_tool "$SP_HOME_BAD"
    assert_case "$impl" "V6.real-vault-hash-mismatch" "$SP_HOME_BAD" NOT-SAFE '' '' 0
    run_tool "$SP_HOME_ABS"
    assert_case "$impl" "V7.real-vault-file-absent" "$SP_HOME_ABS" NOT-SAFE '' '' 0
  else
    row "$impl" "V5.real-vault-match" null "vault Home.md unreadable" "SAFE"
    row "$impl" "V6.real-vault-hash-mismatch" null "vault Home.md unreadable" "NOT-SAFE"
    row "$impl" "V7.real-vault-file-absent" null "vault Home.md unreadable" "NOT-SAFE"
  fi
  if [ "$REAL_ATLAS" = true ]; then
    run_tool "$SP_ATLAS_DIR"
    assert_case "$impl" "V8.real-vault-dir-digest" "$SP_ATLAS_DIR" SAFE '^moved-to-obsidian$' 'vault=' 0
  else
    row "$impl" "V8.real-vault-dir-digest" null "vault atlas unreadable" "SAFE"
  fi

  # --- source-absent row (case-V5 delta): the vault side hashes correctly, so
  #     a vault-side-only verifier would answer SAFE — the false-SAFE this
  #     check exists to catch. The r2 NOT-SAFE(unreachable) is an acceptable
  #     class answer; SAFE is not.
  run_tool "$SP_GONE"
  assert_case "$impl" "V14.source-absent-row" "$SP_GONE" NOT-SAFE '' '' 0

  # --- determinism + json + batch
  run_tool "$SP_HOME"; DET_1="$OUT_TEXT"
  run_tool "$SP_HOME"
  row "$impl" "V9.determinism" "$([ "$DET_1" = "$OUT_TEXT" ] && echo true || echo false)" \
    "$([ "$DET_1" = "$OUT_TEXT" ] && echo identical || echo differs)" "identical"
  run_tool --json "$SP_HOME"
  if printf '%s' "$OUT_TEXT" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null \
     || printf '%s\n' "$OUT_TEXT" | python3 -c 'import json,sys
for ln in sys.stdin:
    if ln.strip(): json.loads(ln)' 2>/dev/null; then
    row "$impl" "V10.json-parse" true "parsed" "parses as JSON (object or jsonl)"
  else
    row "$impl" "V10.json-parse" false "$(printf '%s' "$OUT_TEXT" | head -c 120 | tr '\n' ' ')" "parses as JSON (object or jsonl)"
  fi
  run_tool "$SP_KEPT" "$SP_STALE" "$SP_ABS"
  assert_case "$impl" "V11.batch-match" "$SP_KEPT" SAFE '^moved-to-obsidian$' 'vault=' 0
  assert_case "$impl" "V11.batch-edited" "$SP_STALE" NOT-SAFE '' '' 0
  assert_case "$impl" "V11.batch-absent" "$SP_ABS" NOT-SAFE '' '' 0

  TOOL_SHA_END=$(sha256sum "$SRC_TOOL" | cut -d' ' -f1)
  row "$impl" "A4.tool-stable" "$([ "$TOOL_SHA" = "$TOOL_SHA_END" ] && echo true || echo false)" \
    "$TOOL_SHA_END" "$TOOL_SHA"
done < "$BK/impls.txt"

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

# ------------------------------------------------------------------- report
mkdir -p "$(dirname "$RESULTS")"
python3 - "$RTSV" "$ROWS" "$RESULTS" "$SPEC_SHA" "$RUNNER_SHA" \
        "$SEAT" "$LANE_HEAD" "$VAULT" "$VAULT_HEAD" "$FP_BEFORE_SUM" "$FP_AFTER_SUM" \
        "$LIVE_LEDGER_SHA_START" "$LIVE_LEDGER_SHA_END" "$LEDGER" "$WORK" "$BK/impls-run.txt" <<'PY'
import json, sys, collections, datetime, os

(tsv, rows_path, out_path, spec_sha, runner_sha,
 seat, lane_head, vault, vault_head, fp_before, fp_after,
 ll_sha_start, ll_sha_end, test_ledger, work, impls_path) = sys.argv[1:17]

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

rows = []
for raw in open(rows_path):
    if not raw.strip():
        continue
    f = (raw.rstrip("\n").split("\t") + [""] * 5)[:5]
    p = f[2]
    rows.append({"impl": f[0], "case": f[1],
                 "pass": True if p == "true" else (False if p == "false" else None),
                 "got": san(f[3]), "want": f[4]})

impls = [l.strip() for l in open(impls_path) if l.strip()]
impl_names = [os.path.splitext(os.path.basename(p))[0] for p in impls]
shas = {}
for p in impls:
    try:
        import hashlib
        shas[os.path.splitext(os.path.basename(p))[0]] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    except OSError:
        pass

summary = {}
for r in rows:
    s = summary.setdefault(r["impl"], {"pass": 0, "fail": 0, "null": 0})
    if r["pass"] is True:
        s["pass"] += 1
    elif r["pass"] is False:
        s["fail"] += 1
    else:
        s["null"] += 1

counts = collections.Counter(c["status"] for c in checks)
harness_fails = [c["id"] for c in checks if c["status"] == "fail"]
candidate_fails = [f'{r["impl"]}:{r["case"]}' for r in rows if r["pass"] is False]
status = "fail" if (harness_fails or candidate_fails) else ("blocked" if not rows else "pass")
exit_code = 1 if not rows else 0

report = {
    "seat": "S%s" % seat,
    "role": "vault-runner",
    "kind": "identical-matrix",
    "round": 4,
    "runner": "tests/vault/runner-%s.sh" % seat,
    "runner_sha256": runner_sha,
    "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "status": status,
    "exit_code": exit_code,
    "lane_head": lane_head,
    "impls": impl_names,
    "impl_shas": shas,
    "spec": {"path": "tools/souji-verify.spec.md", "sha256": spec_sha},
    "vault": {"path": vault, "head": vault_head,
              "fingerprint_before": fp_before, "fingerprint_after": fp_after,
              "unchanged": fp_before == fp_after},
    "live_ledger": {"path": "corpus/knowledge/obsidian-ledger.tsv",
                    "sha256_start": ll_sha_start, "sha256_end": ll_sha_end,
                    "header_only": ll_sha_start == ll_sha_end},
    "test_ledger": san(test_ledger),
    "method": {
        "independence": "own fixtures under a mktemp -d in /tmp + own ledger tests/vault/vrun-<seat>-ledger.tsv; no other seat's fixtures or ledgers consumed",
        "vault_access": "read-only: sha256sum/find/stat/git-rev-parse only; no writes, no notes created",
        "gui_policy": "the GUI launcher /usr/bin/obsidian is never executed; obsidian-cli-inspector probed with timeout 5 (--version/--help only)",
        "verdict_tolerance": "SAFE-class == {SAFE, VERIFIED*}; NOT-SAFE-class == {NOT-SAFE*, NOT-VERIFIED*}; tab and single-token outputs both parsed",
        "invocation": "SOUJI_LEDGER env + plain target first; escalates to --ledger and --ledger --fallback on exit 2",
        "tool_selection": "glob tools/souji-vault-verify*.sh (or --tool/--impls); falls back to installed tools/souji-verify.sh when no candidate exists",
    },
    "counts": {"checks_total": len(checks), "checks_pass": counts["pass"],
               "checks_fail": counts["fail"], "checks_info": counts["info"],
               "rows_total": len(rows),
               "rows_pass": sum(1 for r in rows if r["pass"] is True),
               "rows_fail": sum(1 for r in rows if r["pass"] is False)},
    "harness_failed_checks": harness_fails,
    "candidate_failed_rows": candidate_fails,
    "summary": summary,
    "rows": rows,
    "checks": checks,
}
with open(out_path, "w") as fh:
    json.dump(report, fh, indent=2)
    fh.write("\n")
print("runner-%s: status=%s rows=%d pass=%d fail=%d impls=%s"
      % (seat, status, len(rows),
         sum(1 for r in rows if r["pass"] is True),
         sum(1 for r in rows if r["pass"] is False),
         ",".join(impl_names)))
if harness_fails:
    print("harness failed: " + ", ".join(harness_fails))
if candidate_fails:
    print("candidate failed rows: " + ", ".join(candidate_fails[:20]) + ("..." if len(candidate_fails) > 20 else ""))
PY

exit "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["exit_code"])' "$RESULTS")"
