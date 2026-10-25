#!/usr/bin/env bash
# s61-judge.sh — S61 final-judge battery (round 4, Obsidian-CLI vault verification).
#
# Judges any candidate tool (default: tools/souji-vault-verify.sh if present,
# else tools/souji-verify.sh) against:
#   A. the case-V* fixtures (via each builder) with their ledgers;
#   B. S61's own independent probes distilled from the wave's defect set:
#      P1 valid ledger row, trailing newline      -> SAFE/moved-to-obsidian
#      P2 same row WITHOUT trailing newline       -> SAFE/moved-to-obsidian (defect if NOT-SAFE)
#      P3 3-field DIR row, vault differs          -> NOT-SAFE (defect if SAFE)
#      P4 4-field DIR row, empty vault hash, differs -> NOT-SAFE
#      P5 self-receipt vault_path==source_path    -> NOT-SAFE preferred (advisory)
#      P6 vault path outside any vault root       -> advisory
#      P7 vault copy tampered after row           -> NOT-SAFE(vault-sha-mismatch)
#      P8 source tampered after row               -> NOT-SAFE(source-sha-mismatch)
#      P9 real vault Home.md + matching row       -> SAFE/moved-to-obsidian
#      P10 real vault Home.md + wrong vault sha   -> NOT-SAFE
#   C. safety rails: live ledger header-only + byte-identical; real vault
#      manifest unchanged; never executes /usr/bin/obsidian.
#
# Read-only over the real vault. Writes only under /tmp and its --out JSON.
# usage: s61-judge.sh [--tool PATH] [--out PATH] [--json]
# exit: 0 battery complete (per-probe verdicts in JSON) | 2 usage | 3 no tool
set -uo pipefail
export LC_ALL=C

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LANE="$(cd -- "$HERE/../.." && pwd)"
TOOL=""
OUT="/tmp/s61/vfinal-61-battery.json"
REALVAULT="/home/vgpnk/Documents/shokoknowledge"
LIVE_LEDGER="$LANE/corpus/knowledge/obsidian-ledger.tsv"

while [ $# -gt 0 ]; do
  case "$1" in
    --tool) TOOL=${2:?}; shift 2;;
    --out)  OUT=${2:?}; shift 2;;
    --json) shift;;
    *) printf 's61-judge: unknown arg %s\n' "$1" >&2; exit 2;;
  esac
done

if [ -z "$TOOL" ]; then
  for c in "$LANE/tools/souji-vault-verify.sh" "$LANE/tools/vault-verify.sh" "$LANE/tools/souji-verify.sh"; do
    [ -f "$c" ] && { TOOL=$c; break; }
  done
fi
[ -f "${TOOL:-/nonexistent}" ] || { printf 's61-judge: no tool\n' >&2; exit 3; }

W=$(mktemp -d /tmp/s61-judge.XXXXXX)
trap 'rm -rf "$W"' EXIT
mkdir -p "$W/fleet"

TOOL_SHA=$(sha256sum "$TOOL" | cut -d' ' -f1)
printf 'tool=%s sha=%s\n' "$TOOL" "${TOOL_SHA:0:16}"

PROBES="$W/probes.tsv"
printf 'id\tdesc\texpect\tobserved\tresult\tnote\n' > "$PROBES"

sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }
dir_digest() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }

run_tool() { # ledger target -> sets OBS_V OBS_R OBS_E OBS_C
  local ledger=$1 target=$2 out f1
  # always invoke via bash: candidates may land non-executable (0644)
  out=$(env SHOKUNIN_ROOT="$W/fleet" SOUJI_LEDGER="$ledger" timeout 20 bash \
        "$TOOL" --stale-days 1 -- "$target" 2>&1); OBS_C=$?
  # shape-agnostic: some candidates lead with the verdict token in field 1
  f1=$(printf '%s\n' "$out" | awk -F'\t' 'NF>=3{print $1; exit}')
  case "$f1" in
    VERIFIED|NOT-VERIFIED*|SAFE|NOT-SAFE)
      OBS_V=$f1
      OBS_R=$(printf '%s\n' "$out" | awk -F'\t' 'NF>=3{print $3; exit}')
      OBS_E=$(printf '%s\n' "$out" | awk -F'\t' 'NF>=3{$1="";$2="";$3="";sub(/^\t\t\t/,"");print;exit}');;
    *)
      OBS_V=$(printf '%s\n' "$out" | awk -F'\t' 'NF>=3{print $3; exit}')
      OBS_R=$(printf '%s\n' "$out" | awk -F'\t' 'NF>=3{print $4; exit}')
      OBS_E=$(printf '%s\n' "$out" | awk -F'\t' 'NF>=3{$1="";$2="";$3="";$4="";sub(/^\t\t\t\t/,"");print;exit}');;
  esac
  # normalize r4 vocabulary (VERIFIED / NOT-VERIFIED(reason)) to r2 tokens
  case "$OBS_V" in
    VERIFIED) OBS_V=SAFE;;
    NOT-VERIFIED*) OBS_V=NOT-SAFE;;
  esac
  [ "$OBS_V" = "SAFE" ] || [ "$OBS_V" = "NOT-SAFE" ] || OBS_V=${OBS_V:-NO-VERDICT}
  OBS_R=${OBS_R:-none}
}

probe() { # id desc expect ledger target note [allow_any]
  local id=$1 desc=$2 expect=$3 ledger=$4 target=$5 note=${6:-} any=${7:-}
  run_tool "$ledger" "$target"
  local observed="$OBS_V($OBS_R)" result
  if [ "$observed" = "$expect" ]; then result=PASS
  elif [ -n "$any" ]; then result=OBSERVED
  else result=FAIL; fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$desc" "$expect" "$observed" "$result" "$note" >> "$PROBES"
  printf '%-4s %-8s %-26s %s\n' "$id" "$result" "$observed" "$desc"
}

HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

# ---------- B. own probes ---------------------------------------------------
FX="$W/fx"; mkdir -p "$FX/src" "$FX/vault"
printf 's61 payload\n' > "$FX/src/a.md"; cp "$FX/src/a.md" "$FX/vault/a.md"
SA=$(sha "$FX/src/a.md"); SV=$(sha "$FX/vault/a.md")
L=$W/p1.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tp1\n' "$FX/src/a.md" "$SA" "$FX/vault/a.md" "$SV"; } > "$L"
probe P1 "valid row with newline" "SAFE(moved-to-obsidian)" "$L" "$FX/src/a.md"
L=$W/p2.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tp2' "$FX/src/a.md" "$SA" "$FX/vault/a.md" "$SV"; } > "$L"
probe P2 "valid row WITHOUT trailing newline" "SAFE(moved-to-obsidian)" "$L" "$FX/src/a.md"

# dir probes
mkdir -p "$FX/dsrc" "$FX/dvlt"; printf 'one\n' > "$FX/dsrc/one.txt"; cp "$FX/dsrc/one.txt" "$FX/dvlt/"; printf 'EXTRA\n' > "$FX/dvlt/extra.txt"
DD=$(dir_digest "$FX/dsrc")
L=$W/p3.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\n' "$FX/dsrc" "$DD" "$FX/dvlt"; } > "$L"
probe P3 "3-field DIR row, vault differs" "NOT-SAFE(none)" "$L" "$FX/dsrc" "missing vault hash col must not mean SAFE"
L=$W/p4.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t\t2026-10-18\tp4\n' "$FX/dsrc" "$DD" "$FX/dvlt"; } > "$L"
probe P4 "4-field DIR row, empty vault hash, differs" "NOT-SAFE(none)" "$L" "$FX/dsrc"

# self receipt
L=$W/p5.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tself\n' "$FX/src/a.md" "$SA" "$FX/src/a.md" "$SA"; } > "$L"
probe P5 "self-receipt vault_path==source_path" "NOT-SAFE(none)" "$L" "$FX/src/a.md" "advisory if SAFE" any
# outside vault
mkdir -p "$W/outside"; cp "$FX/src/a.md" "$W/outside/a.md"
L=$W/p6.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tout\n' "$FX/src/a.md" "$SA" "$W/outside/a.md" "$SA"; } > "$L"
probe P6 "vault path outside any vault root" "NOT-SAFE(none)" "$L" "$FX/src/a.md" "advisory if SAFE" any

# tamper vault / source after row
printf 'TAMPERED\n' > "$FX/vault/a.md"
L=$W/p7.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tp7\n' "$FX/src/a.md" "$SA" "$FX/vault/a.md" "$SV"; } > "$L"
probe P7 "vault tampered after row" "NOT-SAFE(none)" "$L" "$FX/src/a.md" "expect vault-sha-mismatch note"
cp "$FX/src/a.md" "$FX/vault/a.md"
printf 'SRC-TAMPERED\n' >> "$FX/src/a.md"
L=$W/p8.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tp8\n' "$FX/src/a.md" "$SA" "$FX/vault/a.md" "$SV"; } > "$L"
probe P8 "source tampered after row" "NOT-SAFE(none)" "$L" "$FX/src/a.md" "expect source-sha-mismatch note"

# ---------- real vault ------------------------------------------------------
V_SNAP1=$(find "$REALVAULT" -type f -not -path '*/.git/*' -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LED1=$(sha "$LIVE_LEDGER"); LEDL1=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
HOMES=$(sha "$REALVAULT/Home.md")
cp "$REALVAULT/Home.md" "$W/home-copy.md"
L=$W/p9.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tlive\n' "$W/home-copy.md" "$HOMES" "$REALVAULT/Home.md" "$HOMES"; } > "$L"
probe P9 "real vault Home.md, matching row" "SAFE(moved-to-obsidian)" "$L" "$W/home-copy.md"
L=$W/p10.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tlive-bad\n' "$W/home-copy.md" "$HOMES" "$REALVAULT/Home.md" "2222222222222222222222222222222222222222222222222222222222222222"; } > "$L"
probe P10 "real vault Home.md, wrong vault sha" "NOT-SAFE(none)" "$L" "$W/home-copy.md"
V_SNAP2=$(find "$REALVAULT" -type f -not -path '*/.git/*' -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LED2=$(sha "$LIVE_LEDGER"); LEDL2=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')

# ---------- A. fixtures -----------------------------------------------------
FIXTURES="$W/fixtures.json"
printf '[]\n' > "$FIXTURES"
for cdir in "$LANE"/tests/vault/case-V*; do
  cid=$(basename "$cdir"); b="$cdir/make-fixture.sh"
  [ -f "$b" ] || continue
  out=$(bash "$b" --quiet 2>/dev/null) || { printf 'fixture %s: builder failed\n' "$cid"; continue; }
  kv() { printf '%s\n' "$out" | sed -n "s/^$1=//p" | head -1; }
  root=$(kv FIXTURE_ROOT); [ -n "$root" ] || root=$(kv ROOT)
  led=$(kv LEDGER); [ -n "$led" ] || led=$(kv LEDGER_FILE)
  tgt=$(kv TARGET); [ -n "$tgt" ] || tgt=$(kv SOURCE_FILE)
  tgt=${tgt#note:}; tgt=${tgt%%,*}
  exp=$(kv EXPECT)
  if [ -z "$tgt" ] || [ ! -e "$tgt" ]; then
    printf 'fixture %-8s skipped (target not resolvable: %s)\n' "$cid" "${tgt:-<none>}"
    printf '%s\t%s\t%s\t%s\t%s\tfixture-skipped\n' "$cid" "${exp:-?}" "SKIP" "OBSERVED" "target not resolvable" >> "$PROBES"
    continue
  fi
  [ -n "$led" ] && [ -f "$led" ] || led=$LIVE_LEDGER
  run_tool "$led" "$tgt"
  printf 'fixture %-8s got=%-8s/%-22s expect=%s\n' "$cid" "$OBS_V" "$OBS_R" "${exp:-?}"
  printf '%s\t%s\t%s\t%s\t%s\tfixture\n' "$cid" "$(printf '%s' "$exp" | head -c 40)" "$OBS_V($OBS_R)" "OBSERVED" "" >> "$PROBES"
done

# ---------- JSON out --------------------------------------------------------
python3 - "$PROBES" "$OUT" "$TOOL" "$TOOL_SHA" "$V_SNAP1" "$V_SNAP2" "$LED1" "$LED2" "$LEDL1" "$LEDL2" <<'PY'
import json, sys
probes, out, tool, tsha, vs1, vs2, l1, l2, ll1, ll2 = sys.argv[1:11]
rows = []
with open(probes) as f:
    hdr = f.readline()
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) < 6: p += ['']*(6-len(p))
        rows.append(dict(zip(['id','desc','expect','observed','result','note'], p)))
summary = {
  'probes': len(rows),
  'pass': sum(1 for r in rows if r['result']=='PASS'),
  'fail': sum(1 for r in rows if r['result']=='FAIL'),
  'observed_advisory': sum(1 for r in rows if r['result']=='OBSERVED'),
}
doc = {
  'seat': 'S61',
  'role': 'final-judge battery (independent)',
  'round': 4,
  'tool': tool, 'tool_sha256': tsha,
  'summary': summary,
  'probes': rows,
  'rails': {
    'real_vault_manifest_before': vs1, 'real_vault_manifest_after': vs2,
    'vault_unchanged': vs1 == vs2,
    'live_ledger_sha_before': l1, 'live_ledger_sha_after': l2,
    'live_ledger_header_only': ll1 == '1' and ll2 == '1',
    'live_ledger_unchanged': l1 == l2,
  },
}
json.dump(doc, open(out,'w'), indent=1)
print(json.dumps(summary))
print('vault_unchanged', vs1==vs2, 'ledger_header_only', ll1=='1' and ll2=='1')
PY
