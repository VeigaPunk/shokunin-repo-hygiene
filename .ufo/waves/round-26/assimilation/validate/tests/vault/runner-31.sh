#!/usr/bin/env bash
# tests/vault/runner-31.sh — S31 round-4 vault-verification runner ("identical" contract).
#
# Independent by construction: builds its OWN fixtures + per-case ledgers under
# mktemp -d /tmp/souji31-vault.XXXXXX (never under the lane tree, so the
# pushed-receipt branch of legacy tools cannot fire on the fixtures, and no
# other seat's fixtures/ledgers are consumed).
#
# What it verifies (round 4: Obsidian-CLI vault verification):
#   F1  ledger row + both sides byte-identical            -> SAFE / VERIFIED (moved-to-obsidian)
#   F2  vault copy edited after the row was written       -> NOT-SAFE, vault sha mismatch
#   F3  ledger row source sha256 wrong                    -> NOT-SAFE, source sha mismatch
#   F4  ledger row vault path absent                      -> NOT-SAFE, vault absent/unreachable
#   F5  ledger row source path absent (vault present)     -> NOT-SAFE (never SAFE)
#   F6  header-only ledger (no row)                       -> NOT-SAFE
#   F7  batch: matched + absent targets in one call       -> both lines correct
#   F8  determinism: rerun byte-identical                 -> identical
#   F9  CRLF ledger with a valid row                      -> SAFE / VERIFIED
#   F10 empty vault_sha256 column bait                    -> NOT-SAFE (false-SAFE guard)
#   F11 vault path is a FIFO                              -> NOT-SAFE, must not hang
#   F12 dir row with wrong digest                         -> NOT-SAFE (false-SAFE guard)
#   F13 dir row with correct digest                       -> info (dir support recorded)
#   F14 REAL vault match (/home/vgpnk/Documents/shokoknowledge/Home.md) -> SAFE (read-only)
#   F15 REAL vault row with wrong vault hash              -> NOT-SAFE
#   F16 REAL vault file absent (negative)                 -> NOT-SAFE
#   F17 REAL vault atlas dir digest                       -> info
#   S1  tool --selftest                                   -> exit 0
#   S2  live ledger corpus/knowledge/obsidian-ledger.tsv  -> header-only and unchanged
#   S3  real vault fingerprint                            -> unchanged before vs after
#   S4  GUI process count                                 -> unchanged (launcher never executed)
#   S5  tool sha256                                       -> stable across the battery
#   C1/C2 obsidian-cli-inspector --version / --help       -> exit 0 within timeout 5
#   C3/C4 GUI launcher + registry                         -> info, /usr/bin/obsidian never executed
#
# Vocabulary tolerance: r4 tools emit VERIFIED / NOT-VERIFIED; the installed r2
# tool emits VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence. Both
# are normalized (VERIFIED=SAFE, NOT-VERIFIED=NOT-SAFE) and the observed
# vocabulary is recorded per row.
#
# usage: tests/vault/runner-31.sh [--tool PATH] [--impls "17 18"] [--wait SECS]
#                                 [--results PATH] [--vault PATH] [--keep]
#   --tool      single tool under test (overrides discovery)
#   --impls     only tools/souji-vault-verify.impl-<n>.sh for these numbers
#   --wait      seconds to poll for tools/souji-vault-verify*.sh (default 0)
#   --results   JSON report path (default <lane>/tests/results/vrun-31.json)
#   --vault     real vault path (default /home/vgpnk/Documents/shokoknowledge)
#   --keep      keep the mktemp scratch dir
# exit: 0 all counted checks pass | 1 any counted check failed | 2 usage | 3 no tool found
set -uo pipefail
export LC_ALL=C

SELF_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$SELF_DIR/../.." && pwd)
SEAT=31
TOOL_OVERRIDE=""
IMPL_FILTER=""
WAIT=0
RESULTS="$ROOT/tests/results/vrun-$SEAT.json"
VAULT="/home/vgpnk/Documents/shokoknowledge"
KEEP=0
TOOL_TIMEOUT=60
SELFTEST_TIMEOUT=240
CLI_TIMEOUT=5

die_usage() { printf 'runner-31.sh: %s\n' "$1" >&2; exit 2; }
while [ $# -gt 0 ]; do
  case "$1" in
    --tool)    [ $# -ge 2 ] || die_usage "--tool needs a value"; TOOL_OVERRIDE=$2; shift 2;;
    --impls)   [ $# -ge 2 ] || die_usage "--impls needs a value"; IMPL_FILTER=$2; shift 2;;
    --wait)    [ $# -ge 2 ] || die_usage "--wait needs a value"; WAIT=$2; shift 2;;
    --results) [ $# -ge 2 ] || die_usage "--results needs a value"; RESULTS=$2; shift 2;;
    --vault)   [ $# -ge 2 ] || die_usage "--vault needs a value"; VAULT=$2; shift 2;;
    --keep)    KEEP=1; shift;;
    -h|--help) sed -n '2,45p' "$0"; exit 0;;
    *) die_usage "unknown argument: $1";;
  esac
done

WORK=$(mktemp -d /tmp/souji31-vault.XXXXXX)
case "$WORK" in /tmp/souji31-vault.*) : ;; *) echo "refusing: WORK=$WORK" >&2; exit 9;; esac
BK="$WORK/.runner"; mkdir -p "$BK"
cleanup() { [ "$KEEP" = 1 ] || rm -rf "$WORK"; }
trap cleanup EXIT

RTSV="$BK/results.tsv"; : > "$RTSV"
san() { local s=${1:-}; s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; s=${s//$'\r'/\\r}; printf '%s' "$s"; }
record() { # id case status expected observed rc detail
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(san "$1")" "$(san "$2")" "$(san "$3")" "$(san "$4")" \
    "$(san "$5")" "$(san "${6:-}")" "$(san "${7:-}")" >> "$RTSV"
}
sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }
dir_digest() { ( cd "$1" 2>/dev/null && find . -type f -print0 | sort -z \
    | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }

# ------------------------------------------------------------------ discovery
# Candidates: tools/souji-vault-verify.impl-<n>.sh, plus bare tools/impl-<n>.sh
# (seats S17..S24 landed some candidates at the short path). --impls filters
# both families by number. The bare impl-21.sh lacks the exec bit upstream
# (peer S30 works around it); bash-invocation makes that irrelevant here.
impl_paths() {
  local p n
  for p in "$ROOT"/tools/souji-vault-verify.impl-*.sh "$ROOT"/tools/impl-*.sh; do
    [ -e "$p" ] || continue
    if [ -n "$IMPL_FILTER" ]; then
      n="${p##*impl-}"; n="${n%.sh}"
      case " $IMPL_FILTER " in *" $n "*) printf '%s\n' "$p" ;; esac
    else
      printf '%s\n' "$p"
    fi
  done | sort -u
}
canonical_path() {
  local c
  for c in "$ROOT/tools/souji-vault-verify.sh" "$ROOT/tools/obsidian-vault-verify.sh" \
           "$ROOT/tools/vault-verify.sh"; do
    [ -f "$c" ] && { printf '%s\n' "$c"; return 0; }
  done
  return 1
}

if [ "$WAIT" -gt 0 ] && [ -z "$TOOL_OVERRIDE" ]; then
  deadline=$(( $(date +%s) + WAIT ))
  while :; do
    n=$(impl_paths | wc -l)
    [ "$n" -gt 0 ] && break
    [ "$(date +%s)" -ge "$deadline" ] && break
    sleep 15
  done
fi

TOOLS=()
if [ -n "$TOOL_OVERRIDE" ]; then
  [ -f "$TOOL_OVERRIDE" ] || { printf 'runner-31.sh: tool not found: %s\n' "$TOOL_OVERRIDE" >&2; exit 3; }
  TOOLS=("$TOOL_OVERRIDE")
else
  while IFS= read -r p; do [ -n "$p" ] && TOOLS+=("$p"); done < <(impl_paths)
  if c=$(canonical_path); then TOOLS+=("$c"); fi
  if [ "${#TOOLS[@]}" -eq 0 ] && [ -f "$ROOT/tools/souji-verify.sh" ]; then
    TOOLS=("$ROOT/tools/souji-verify.sh")
  fi
fi
[ "${#TOOLS[@]}" -gt 0 ] || { printf 'runner-31.sh: no tool found under tools/\n' >&2; exit 3; }

# ------------------------------------------------------------------ fixtures
FX="$WORK/fx"; LGD="$WORK/ledgers"
mkdir -p "$FX/src" "$FX/vault" "$LGD" "$WORK/tmp"
HDR='source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
led() { local f=$LGD/$1.tsv; printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$f"; printf '%s' "$f"; }
row() { printf '%s\t%s\t%s\t%s\t2026-10-18\t%s\n' "$1" "$2" "$3" "$4" "$5"; }

# F1 matched pair
S1="$FX/src/f1-match.md"; V1="$FX/vault/f1-match.md"
printf 'vrun-31 F1 payload: matched pair\n' > "$S1"; cp "$S1" "$V1"
SHA1=$(sha "$S1"); L1=$(led f1); row "$S1" "$SHA1" "$V1" "$SHA1" f1 >> "$L1"

# F2 vault edited after the row was written
S2="$FX/src/f2-stale.md"; V2="$FX/vault/f2-stale.md"
printf 'vrun-31 F2 payload: row written at export time\n' > "$S2"; cp "$S2" "$V2"
SHA2=$(sha "$S2"); L2=$(led f2); row "$S2" "$SHA2" "$V2" "$SHA2" f2 >> "$L2"
printf 'EDIT AFTER ROW\n' >> "$V2"

# F3 source sha256 wrong in the row
S3="$FX/src/f3-mis.md"; V3="$FX/vault/f3-mis.md"
printf 'vrun-31 F3 payload\n' > "$S3"; cp "$S3" "$V3"
SHA3=$(sha "$S3"); WRONG=1111111111111111111111111111111111111111111111111111111111111111
L3=$(led f3); row "$S3" "$WRONG" "$V3" "$SHA3" f3 >> "$L3"

# F4 vault path absent
S4="$FX/src/f4-abs.md"
printf 'vrun-31 F4 payload\n' > "$S4"
SHA4=$(sha "$S4"); L4=$(led f4); row "$S4" "$SHA4" "$FX/vault/f4-never.md" "$SHA4" f4 >> "$L4"

# F5 source path absent (vault present)
V5="$FX/vault/f5-srcgone.md"
printf 'vrun-31 F5 payload: source gone, vault kept\n' > "$V5"
SHA5=$(sha "$V5"); L5=$(led f5); row "$FX/src/f5-never.md" "$SHA5" "$V5" "$SHA5" f5 >> "$L5"

# F6 header-only ledger
L6=$(led f6)

# F9 CRLF ledger, valid row
S9="$FX/src/f9-crlf.md"; V9="$FX/vault/f9-crlf.md"
printf 'vrun-31 F9 payload\n' > "$S9"; cp "$S9" "$V9"
SHA9=$(sha "$S9"); L9="$LGD/f9.tsv"
{ printf '%s\r\n' "$(printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote')"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tcrlf\r\n' "$S9" "$SHA9" "$V9" "$SHA9"; } > "$L9"

# F10 empty vault_sha256 column (bait)
S10="$FX/src/f10-emptyhash.md"; V10="$FX/vault/f10-emptyhash.md"
printf 'vrun-31 F10 payload\n' > "$S10"; cp "$S10" "$V10"
SHA10=$(sha "$S10"); L10=$(led f10); row "$S10" "$SHA10" "$V10" "" f10 >> "$L10"

# F11 FIFO vault path
S11="$FX/src/f11-fifo.md"
printf 'vrun-31 F11 payload\n' > "$S11"
SHA11=$(sha "$S11"); FIFO="$WORK/tmp/f11-fifo-vault"
[ -p "$FIFO" ] || mkfifo "$FIFO"
L11=$(led f11); row "$S11" "$SHA11" "$FIFO" "$SHA11" f11 >> "$L11"

# F12/F13 dir rows
DS="$FX/src/f12-dir"; DV="$FX/vault/f12-dir"
mkdir -p "$DS" "$DV"
printf 'one\n' > "$DS/one.txt"; printf 'two\n' > "$DS/two.txt"
cp "$DS/one.txt" "$DS/two.txt" "$DV/"
DD=$(dir_digest "$DS"); DVD=$(dir_digest "$DV")
L12=$(led f12); row "$DS" "$DD" "$DV" "$WRONG" f12 >> "$L12"
L13=$(led f13); row "$DS" "$DD" "$DV" "$DVD" f13 >> "$L13"

# F14/F15/F16 real-vault rows (read-only on the vault side)
REAL_OK=false; SHA_HOME=""
if [ -f "$VAULT/Home.md" ] && [ -r "$VAULT/Home.md" ]; then
  REAL_OK=true; SHA_HOME=$(sha "$VAULT/Home.md")
  cp "$VAULT/Home.md" "$FX/src/f14-home.md"
  cp "$VAULT/Home.md" "$FX/src/f15-homebad.md"
  cp "$VAULT/Home.md" "$FX/src/f16-homeabs.md"
fi
L14=$(led f14); L15=$(led f15); L16=$(led f16)
if [ "$REAL_OK" = true ]; then
  row "$FX/src/f14-home.md" "$SHA_HOME" "$VAULT/Home.md" "$SHA_HOME" f14 >> "$L14"
  row "$FX/src/f15-homebad.md" "$SHA_HOME" "$VAULT/Home.md" "$WRONG" f15 >> "$L15"
  row "$FX/src/f16-homeabs.md" "$SHA_HOME" "$VAULT/f16-absent-$SEAT.md" "$SHA_HOME" f16 >> "$L16"
fi

# F17 real vault atlas dir digest (info)
REAL_ATLAS=false; L17=$(led f17); DIG_ATLAS=""; DS17=""
if [ -d "$VAULT/atlas" ] && [ -r "$VAULT/atlas" ]; then
  REAL_ATLAS=true
  DS17="$FX/src/f17-atlas"; mkdir -p "$DS17"
  cp -r "$VAULT/atlas/." "$DS17/" 2>/dev/null || true
  DIG_ATLAS=$(dir_digest "$DS17")
  row "$DS17" "$DIG_ATLAS" "$VAULT/atlas" "$(dir_digest "$VAULT/atlas")" f17 >> "$L17"
fi

# --------------------------------------------------------- vault fingerprint
vault_fp() {
  local out=$1
  { [ -d "$VAULT" ] || { printf 'VAULT-ABSENT\n'; return 0; }
    find "$VAULT" -type f -not -path '*/.git/*' -not -path '*/.obsidian/*' -print0 \
      | sort -z | xargs -0 -r sha256sum 2>/dev/null; } > "$out" 2>/dev/null || true
  printf 'files=%s manifest_sha=%s\n' "$(grep -c . "$out" 2>/dev/null || echo 0)" "$(sha "$out")"
}
FP_BEFORE=$(vault_fp "$BK/vault-fp.before")
LIVE="$ROOT/corpus/knowledge/obsidian-ledger.tsv"
LL_SHA0=$([ -f "$LIVE" ] && sha "$LIVE" || echo missing)
LL_LINES0=$([ -f "$LIVE" ] && wc -l < "$LIVE" | tr -d ' ' || echo missing)
GUI0_PIDS=$(pgrep -f '/usr/lib/obsidian/app\.asar' 2>/dev/null | sort -n || true)
GUI0=$(printf '%s\n' "$GUI0_PIDS" | grep -c . || true); GUI0=${GUI0:-0}
RUNNER_SHA=$(sha "$0")
LANE_HEAD=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)

# ------------------------------------------------------------- tool invocation
OUT_TEXT=""; OUT_RC=0; INV_MODE=""
# parse_for: "verdict<TAB>reason<TAB>evidence"; the raw matched line lands in
# $BK/parsed.line (a tab-bearing line cannot survive as a tab-separated field).
parse_for() { # $1 file, $2 target
  awk -F'\t' -v t="$2" -v linefile="$BK/parsed.line" '
    {
      line=$0; v=""; p=""; r=""; e=""
      if ($1=="VERDICT")            { p=$2; v=$3; r=$4; e=$5 }
      else if ($1=="VERIFIED" || $1=="NOT-VERIFIED" || $1=="SAFE" || $1=="NOT-SAFE") { p=$2; v=$1; r=$3; e=$4 }
      else if ($1 ~ /^(VERIFIED|NOT-VERIFIED)\([^)]*\)$/) { v=substr($1,1,index($1,"(")-1); r=substr($1,index($1,"(")+1,length($1)-index($1,"(")-1); p=$2; e=$3 }
      else if ($1 ~ /^(VERIFIED|NOT-VERIFIED|SAFE|NOT-SAFE)[ ]/) { n=split($1,a," "); v=a[1]; p=a[2]; r=substr($1, length(v)+length(p)+3); e=$2 }
      else next
      if (p==t) { print v "\t" r "\t" e; print line > linefile; exit }
    }' "$1"
}
parsed_line() { [ -f "$BK/parsed.line" ] && cat "$BK/parsed.line" || printf ''; }
invoke_final() { # tool target...
  local tool=$1; shift
  local m rc t
  for m in env-positional flags env-flags; do
    rc=0
    case "$m" in
      env-positional) OUT_TEXT=$(env SOUJI_LEDGER="${CUR_LEDGER:-}" timeout "$TOOL_TIMEOUT" bash "$tool" "$@" 2>"$BK/stderr") || rc=$? ;;
      flags)          OUT_TEXT=$(timeout "$TOOL_TIMEOUT" bash "$tool" --ledger "${CUR_LEDGER:-}" --fallback "$@" 2>"$BK/stderr") || rc=$? ;;
      env-flags)      OUT_TEXT=$(env SOUJI_LEDGER="${CUR_LEDGER:-}" timeout "$TOOL_TIMEOUT" bash "$tool" --ledger "${CUR_LEDGER:-}" --fallback "$@" 2>"$BK/stderr") || rc=$? ;;
    esac
    OUT_RC=$rc
    printf '%s\n' "$OUT_TEXT" > "$BK/out.raw"
    t=$(parse_for "$BK/out.raw" "$1")
    if [ -n "$t" ] || [ "$OUT_RC" = 124 ]; then INV_MODE="$m"; return 0; fi
    if [ "$OUT_RC" != 2 ] && [ "$OUT_RC" != 0 ]; then INV_MODE="$m"; return 0; fi
  done
  INV_MODE="unparsed"
}

check() { # id case expect_verdict reason_regex target ledger note [extra_timeout]
  # $case is the fixture label (F1..F17); the tool name is carried in $INAME.
  local id=$1 case=$2 wv=$3 wre=$4 tgt=$5 lgr=$6 note=${7:-}
  CUR_LEDGER="$lgr"
  invoke_final "$TOOL" "$tgt"
  local parsed v r e line text status detail=""
  parsed=$(parse_for "$BK/out.raw" "$tgt")
  v=$(printf '%s' "$parsed" | awk -F'\t' '{print $1}')
  r=$(printf '%s' "$parsed" | awk -F'\t' '{print $2}')
  e=$(printf '%s' "$parsed" | awk -F'\t' '{print $3}')
  line=$(parsed_line)
  text="$r $e $line"
  if [ -z "$parsed" ]; then
    if [ "$OUT_RC" = 124 ]; then
      record "$id" "$INAME" fail "$wv /$wre/" "TIMEOUT rc=124 mode=$INV_MODE" "$OUT_RC" "$note"
      return 0
    fi
    record "$id" "$INAME" fail "$wv /$wre/" "no verdict line (rc=$OUT_RC mode=$INV_MODE) out=$(printf '%s' "$OUT_TEXT" | head -c 160)" "$OUT_RC" "$note"
    return 0
  fi
  [ "$v" = "VERIFIED" ] && v=SAFE
  [ "$v" = "NOT-VERIFIED" ] && v=NOT-SAFE
  if [ "$v" = "$wv" ]; then
    if [ -z "$wre" ] || printf '%s' "$text" | grep -Eq "$wre"; then
      record "$id" "$INAME" pass "$wv /$wre/" "rc=$OUT_RC mode=$INV_MODE line=$line" "$OUT_RC" "$note"
    else
      record "$id" "$INAME" fail "$wv /$wre/" "verdict ok but reason mismatch: $line" "$OUT_RC" "$note"
    fi
  else
    record "$id" "$INAME" fail "$wv /$wre/" "verdict=$v line=$line" "$OUT_RC" "$note"
  fi
}

# ------------------------------------------------------------------ battery
: > "$BK/battery.log"
for TOOL in "${TOOLS[@]}"; do
  INAME=$(basename "$TOOL"); INAME=${INAME%.sh}
  TOOL_SHA=$(sha "$TOOL")
  printf '=== %s sha=%s\n' "$INAME" "$TOOL_SHA" >> "$BK/battery.log"
  bash -n "$TOOL" 2>"$BK/syntax.err" \
    && record "tool.syntax" "$INAME" pass "bash -n exit 0" "exit 0" 0 "" \
    || record "tool.syntax" "$INAME" fail "bash -n exit 0" "syntax error: $(head -c 200 "$BK/syntax.err")" 1 ""

  # S1 selftest
  st_rc=0
  st_out=$(env SOUJI_LEDGER="${CUR_LEDGER:-}" timeout "$SELFTEST_TIMEOUT" bash "$TOOL" --selftest 2>&1) || st_rc=$?
  printf '%s\n' "$st_out" > "$BK/selftest-$INAME.log"
  if [ "$st_rc" = 2 ]; then
    record "S1.selftest" "$INAME" skip "exit 0" "rc=2 (no --selftest) $(printf '%s' "$st_out" | tail -1 | cut -c1-120)" 2 ""
  elif [ "$st_rc" = 0 ]; then
    record "S1.selftest" "$INAME" pass "exit 0" "rc=0 $(printf '%s' "$st_out" | tail -1 | cut -c1-140)" 0 ""
  else
    record "S1.selftest" "$INAME" fail "exit 0" "rc=$st_rc $(printf '%s' "$st_out" | tail -1 | cut -c1-140)" "$st_rc" ""
  fi

  check "F1.ledger-match"          F1  SAFE     'moved-to-obsidian|ledger' "$S1"  "$L1"  "matched pair"
  check "F2.vault-edited-after-row" F2 NOT-SAFE 'vault.*(sha.*mismatch|mismatch)|sha-mismatch' "$S2" "$L2" "vault copy edited after export"
  check "F3.source-sha-mismatch"   F3  NOT-SAFE 'source.*(sha.*mismatch|mismatch)|sha-mismatch' "$S3" "$L3" "row source sha wrong"
  check "F4.vault-absent"          F4  NOT-SAFE 'vault.*(absent|unreachable|missing)' "$S4" "$L4" "vault path never created"
  check "F5.source-absent"         F5  NOT-SAFE '' "$FX/src/f5-never.md" "$L5" "source gone, vault kept"
  check "F6.header-only-ledger"    F6  NOT-SAFE '' "$S1" "$L6" "header-only ledger"
  check "F9.crlf-ledger-valid-row" F9  SAFE     'moved-to-obsidian|ledger' "$S9"  "$L9"  "CRLF ledger, valid row"
  check "F10.empty-vault-hash"     F10 NOT-SAFE '' "$S10" "$L10" "empty vault_sha256 bait"
  check "F11.fifo-vault"           F11 NOT-SAFE '' "$S11" "$L11" "vault path is a FIFO (must not hang)"
  check "F12.dir-wrong-digest"     F12 NOT-SAFE '' "$DS"  "$L12" "dir row, wrong vault digest"

  # F7 batch: matched + absent in one invocation
  CUR_LEDGER="$L1"
  invoke_final "$TOOL" "$S1" "$S4"
  b1=$(parse_for "$BK/out.raw" "$S1"); b2=$(parse_for "$BK/out.raw" "$S4")
  if [ -z "$b2" ]; then
    CUR_LEDGER="$L4"; invoke_final "$TOOL" "$S4"; b2=$(parse_for "$BK/out.raw" "$S4")
    note="batch absent-line missing; retried as single target"
  else
    note="batch single invocation"
  fi
  bv1=$(printf '%s' "$b1" | awk -F'\t' '{print $1}'); bv2=$(printf '%s' "$b2" | awk -F'\t' '{print $1}')
  [ "$bv1" = "VERIFIED" ] && bv1=SAFE; [ "$bv2" = "NOT-VERIFIED" ] && bv2=NOT-SAFE
  if [ "$bv1" = SAFE ] && [ "$bv2" = NOT-SAFE ]; then
    record "F7.batch" "$INAME" pass "match=SAFE absent=NOT-SAFE" "match=$bv1 absent=$bv2" 0 "$note"
  else
    record "F7.batch" "$INAME" fail "match=SAFE absent=NOT-SAFE" "match=${bv1:-none} absent=${bv2:-none} rc=$OUT_RC" "$OUT_RC" "$note"
  fi

  # F8 determinism
  CUR_LEDGER="$L1"; invoke_final "$TOOL" "$S1"; d1="$OUT_TEXT"
  CUR_LEDGER="$L1"; invoke_final "$TOOL" "$S1"; d2="$OUT_TEXT"
  if [ "$d1" = "$d2" ] && [ -n "$d1" ]; then
    record "F8.determinism" "$INAME" pass "identical rerun" "identical" 0 ""
  else
    record "F8.determinism" "$INAME" fail "identical rerun" "differs" 0 ""
  fi

  # F13/F17 info rows
  CUR_LEDGER="$L13"; invoke_final "$TOOL" "$DS"
  p13=$(parse_for "$BK/out.raw" "$DS"); v13=$(printf '%s' "$p13" | awk -F'\t' '{print $1}')
  record "F13.dir-correct-digest" "$INAME" info "SAFE if dirs supported" "${v13:-none} mode=$INV_MODE" "$OUT_RC" "info only"
  if [ "$REAL_ATLAS" = true ]; then
    CUR_LEDGER="$L17"; invoke_final "$TOOL" "$DS17"
    p17=$(parse_for "$BK/out.raw" "$DS17"); v17=$(printf '%s' "$p17" | awk -F'\t' '{print $1}')
    record "F17.real-atlas-dir" "$INAME" info "SAFE if dirs supported" "${v17:-none} mode=$INV_MODE" "$OUT_RC" "real vault read-only"
  fi

  # F14/F15/F16 real vault (read-only)
  if [ "$REAL_OK" = true ]; then
  check "F14.real-vault-match"      F14 SAFE     'moved-to-obsidian|ledger' "$FX/src/f14-home.md"  "$L14" "real vault Home.md"
    check "F15.real-vault-wrong-hash" F15 NOT-SAFE ''         "$FX/src/f15-homebad.md" "$L15" "wrong vault hash must not verify"
    check "F16.real-vault-absent"     F16 NOT-SAFE ''         "$FX/src/f16-homeabs.md" "$L16" "vault file absent"
  else
    record "F14.real-vault-match" "$INAME" skip "SAFE" "vault Home.md unreadable" "" "$VAULT"
    record "F15.real-vault-wrong-hash" "$INAME" skip "NOT-SAFE" "vault Home.md unreadable" "" ""
    record "F16.real-vault-absent" "$INAME" skip "NOT-SAFE" "vault Home.md unreadable" "" ""
  fi

  # S5 tool sha stable
  if [ "$(sha "$TOOL")" = "$TOOL_SHA" ]; then
    record "S5.tool-stable" "$INAME" pass "sha unchanged" "$TOOL_SHA" 0 ""
  else
    record "S5.tool-stable" "$INAME" fail "sha unchanged" "$TOOL_SHA -> $(sha "$TOOL")" 0 ""
  fi
done

# ------------------------------------------------------------ shared invariants
LL_SHA1=$([ -f "$LIVE" ] && sha "$LIVE" || echo missing)
LL_LINES1=$([ -f "$LIVE" ] && wc -l < "$LIVE" | tr -d ' ' || echo missing)
if [ "$LL_LINES1" = 1 ] && [ "$LL_SHA0" = "$LL_SHA1" ]; then
  record "S2.live-ledger-header-only" "-" pass "lines=1 unchanged" "lines=1 sha=${LL_SHA1:0:12}" 0 ""
else
  record "S2.live-ledger-header-only" "-" fail "lines=1 unchanged" \
    "lines $LL_LINES0->$LL_LINES1 sha ${LL_SHA0:0:12}->${LL_SHA1:0:12}" 0 ""
fi

FP_AFTER=$(vault_fp "$BK/vault-fp.after")
if [ "$FP_BEFORE" = "$FP_AFTER" ] && cmp -s "$BK/vault-fp.before" "$BK/vault-fp.after"; then
  record "S3.vault-unchanged" "-" pass "manifest identical" "$FP_AFTER" 0 ""
else
  record "S3.vault-unchanged" "-" fail "manifest identical" "before[$FP_BEFORE] after[$FP_AFTER]" 0 ""
fi

GUI_AFTER_PIDS=$(pgrep -f '/usr/lib/obsidian/app\.asar' 2>/dev/null | sort -n || true)
GUI1=$(printf '%s\n' "$GUI_AFTER_PIDS" | grep -c . || true); GUI1=${GUI1:-0}
# Attribute any delta: only a GUI process descending from THIS runner is a
# spawn by the runner (parallel seats launch their own processes legitimately).
gui_descends_from_runner() { # $1 pid
  local p=$1 d=0
  while [ -n "$p" ] && [ "$p" != 1 ] && [ "$p" != 0 ] && [ "$d" -lt 60 ]; do
    [ "$p" = "$$" ] && return 0
    p=$(awk '{print $4}' "/proc/$p/stat" 2>/dev/null) || return 1
    d=$((d+1))
  done
  return 1
}
RUNNER_SPAWNED=""
for p in $(comm -13 <(printf '%s\n' "$GUI0_PIDS") <(printf '%s\n' "$GUI_AFTER_PIDS") 2>/dev/null | grep -v '^$' || true); do
  gui_descends_from_runner "$p" && RUNNER_SPAWNED="$RUNNER_SPAWNED $p"
done
if [ -z "${RUNNER_SPAWNED// /}" ]; then
  record "S4.no-gui-spawn" "-" pass "no GUI process descends from this runner" \
    "before=$GUI0 after=$GUI1 new=$(comm -13 <(printf '%s\n' "$GUI0_PIDS") <(printf '%s\n' "$GUI_AFTER_PIDS") 2>/dev/null | grep -vc '^$' || echo 0) (external deltas attributed, if any)" 0 ""
else
  record "S4.no-gui-spawn" "-" fail "no GUI process descends from this runner" \
    "runner-spawned pids:$RUNNER_SPAWNED before=$GUI0 after=$GUI1" 0 ""
fi

# ------------------------------------------------------------------ CLI probes
CLI=$(command -v obsidian-cli-inspector 2>/dev/null || true)
if [ -n "$CLI" ]; then
  c1_rc=0; c1_out=$(timeout "$CLI_TIMEOUT" "$CLI" --version 2>&1) || c1_rc=$?
  [ "$c1_rc" = 0 ] && record "C1.inspector-version" "-" pass "exit 0" "rc=0 $(printf '%s' "$c1_out" | head -1 | cut -c1-100)" 0 "" \
    || record "C1.inspector-version" "-" fail "exit 0" "rc=$c1_rc $(printf '%s' "$c1_out" | head -1 | cut -c1-100)" "$c1_rc" ""
  c2_rc=0; c2_out=$(timeout "$CLI_TIMEOUT" "$CLI" --help 2>&1) || c2_rc=$?
  [ "$c2_rc" = 0 ] && record "C2.inspector-help" "-" pass "exit 0" "rc=0 $(printf '%s' "$c2_out" | head -1 | cut -c1-100)" 0 "" \
    || record "C2.inspector-help" "-" fail "exit 0" "rc=$c2_rc" "$c2_rc" ""
else
  record "C1.inspector-version" "-" fail "obsidian-cli-inspector present" "not in PATH" "" ""
  record "C2.inspector-help" "-" skip "exit 0" "not in PATH" "" ""
fi
if [ -e /usr/bin/obsidian ]; then
  record "C3.gui-launcher" "-" info "never executed" "mode=$(stat -c %A /usr/bin/obsidian) bytes=$(stat -c %s /usr/bin/obsidian)" "" ""
else
  record "C3.gui-launcher" "-" info "never executed" "/usr/bin/obsidian absent" "" ""
fi
if [ -f /home/vgpnk/.config/obsidian/obsidian.json ]; then
  OBJ=$(python3 - <<'PY' 2>/dev/null || true
import json
d=json.load(open('/home/vgpnk/.config/obsidian/obsidian.json'))
vs=d.get('vaults',{})
paths=[v.get('path') for v in vs.values() if isinstance(v,dict)]
print('cli=%s vaults=%d path=%s' % (d.get('cli'), len(vs), paths[0] if paths else 'none'))
PY
)
  record "C4.obsidian-registry" "-" info "registry readable" "${OBJ:-unparseable}" "" ""
else
  record "C4.obsidian-registry" "-" info "registry readable" "obsidian.json absent" "" ""
fi

# ------------------------------------------------------------------- report
mkdir -p "$(dirname "$RESULTS")"
TOOL_LIST=$(printf '%s\n' "${TOOLS[@]}")
python3 - "$RTSV" "$RESULTS" "$WORK" "$VAULT" "$FP_BEFORE" "$FP_AFTER" \
        "$LL_SHA0" "$LL_SHA1" "$LL_LINES0" "$LL_LINES1" "$GUI0" "$GUI1" \
        "$LANE_HEAD" "$RUNNER_SHA" "$SEAT" "$TOOL_LIST" "$WAIT" "$IMPL_FILTER" <<'PY'
import json, sys, collections, datetime, os
(tsv, out_path, work, vault, fp_b, fp_a, ll_s0, ll_s1, ll_n0, ll_n1,
 gui0, gui1, lane_head, runner_sha, seat, tool_list, wait_s, impl_filter) = sys.argv[1:19]

def san(s):
    return (s or "").replace(work, "<work>")

checks = []
for raw in open(tsv):
    if not raw.strip():
        continue
    f = (raw.rstrip("\n").split("\t") + [""] * 7)[:7]
    checks.append({"id": san(f[0]), "case": san(f[1]), "status": f[2],
                   "expected": san(f[3]), "observed": san(f[4]),
                   "exit_code": int(f[5]) if f[5].strip().lstrip("-").isdigit() else None,
                   "detail": san(f[6])})
counts = collections.Counter(c["status"] for c in checks)
fails = [c["id"] for c in checks if c["status"] == "fail"]
skips = [c["id"] for c in checks if c["status"] == "skip"]
measured = [c for c in checks if c["status"] not in ("info", "skip")]
status = "blocked" if not measured else ("fail" if fails else "pass")
exit_code = 3 if not measured else (1 if fails else 0)

tools = []
for t in tool_list.splitlines():
    t = t.strip()
    if t:
        tools.append({"path": t, "exists": os.path.isfile(t)})

# aggregator-friendly row list (S57 aggregate.py: impl/case/pass/got/want)
rows = [{
    "impl": "-", "case": "--meta", "kind": "meta", "pass": None,
    "seat": "S%s" % seat, "role": "vault-runner", "round": 4,
    "runner": "tests/vault/runner-%s.sh" % seat, "runner_sha256": runner_sha,
    "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "status": status, "exit_code": exit_code, "lane_head": lane_head,
    "tools": tools, "wait_seconds": int(wait_s), "impl_filter": impl_filter or None,
    "counts": {"total": len(checks), "pass": counts["pass"], "fail": counts["fail"],
               "skip": counts["skip"], "info": counts["info"]},
    "failed_checks": fails, "skipped_checks": skips,
    "vault": {"path": vault, "fingerprint_before": fp_b, "fingerprint_after": fp_a,
              "unchanged": fp_b == fp_a},
    "live_ledger": {"path": "corpus/knowledge/obsidian-ledger.tsv",
                    "sha256_start": ll_s0, "sha256_end": ll_s1,
                    "lines_start": ll_n0, "lines_end": ll_n1, "header_only": ll_s0 == ll_s1 and ll_n1 == "1"},
    "gui_procs": {"before": gui0, "after": gui1},
    "method": {
        "independence": "own fixtures + per-case ledgers under mktemp -d /tmp/souji31-vault.*; no peer fixtures or ledgers consumed",
        "vocabulary": "VERIFIED/NOT-VERIFIED and SAFE/NOT-SAFE both accepted and normalized; observed line recorded verbatim",
        "invocation": "env SOUJI_LEDGER + positional, then --ledger/--fallback, then env + flags; first form with a parseable verdict line wins",
        "vault_access": "read-only sha256sum/find/stat; /usr/bin/obsidian never executed; inspector probed with timeout 5",
    },
    "checks": checks,
}]
for c in checks:
    impl = c["case"] if c["case"] != "-" else "-"
    rows.append({"impl": impl, "case": c["id"], "kind": "check",
                 "pass": None if c["status"] in ("info", "skip") else c["status"] == "pass",
                 "status": c["status"], "got": c["observed"], "want": c["expected"],
                 "exit_code": c["exit_code"], "note": c["detail"]})
with open(out_path, "w") as fh:
    json.dump(rows, fh, indent=1)
    fh.write("\n")
print("runner-%s: status=%s exit=%d pass=%d fail=%d skip=%d info=%d tools=%s"
      % (seat, status, exit_code, counts["pass"], counts["fail"], counts["skip"],
         counts["info"], ",".join(os.path.basename(t["path"]) for t in tools)))
if fails:
    print("failed: " + ", ".join(fails))
PY

exit "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[0]["exit_code"])' "$RESULTS")"
