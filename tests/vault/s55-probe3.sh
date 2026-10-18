#!/usr/bin/env bash
# S55 decisive probes — the vault-digest-absent false-SAFE (family s/u tie-in).
# Read-only over the real vault; writes only under tests/vault/ and /tmp.
set -uo pipefail
REPO=/home/vgpnk/Projects/shokunin/souji-shokunin
TOOL=$REPO/tools/souji-verify.sh
RAW=$REPO/tests/vault/s55-raw
W=/tmp/s55-dec2
rm -rf "$W"; mkdir -p "$W/fleet" "$W/src/dirX" "$W/vault/dirX" "$W/vault/dirX2" "$W/src/dirY" "$W/vault/dirY"
OUT=$RAW/probes3.tsv
printf 'id\tdescription\texpect\tobserved\tresult\tnote\n' > "$OUT"

dd() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }
sha() { sha256sum -- "$1" | cut -d' ' -f1; }
HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

# dirX: vault has an EXTRA file -> digests differ (content NOT preserved)
printf 'one\n' > "$W/src/dirX/one.txt"; printf 'two\n' > "$W/src/dirX/two.txt"
cp "$W/src/dirX/one.txt" "$W/vault/dirX/"; cp "$W/src/dirX/two.txt" "$W/vault/dirX/"
printf 'EXTRA\n' > "$W/vault/dirX/extra.txt"
DD_X=$(dd "$W/src/dirX"); DV_X=$(dd "$W/vault/dirX")
# dirX2: exact copy -> digests equal
cp "$W/src/dirX/one.txt" "$W/vault/dirX2/"; cp "$W/src/dirX/two.txt" "$W/vault/dirX2/"
DD_X2=$(dd "$W/src/dirX"); DV_X2=$(dd "$W/vault/dirX2")
# dirY: identical dirs, for the torn-row test
printf 'y1\n' > "$W/src/dirY/y1.txt"; cp "$W/src/dirY/y1.txt" "$W/vault/dirY/"
DD_Y=$(dd "$W/src/dirY"); DV_Y=$(dd "$W/vault/dirY")

echo "dirX  source=$DD_X vault=$DV_X  DIFFER=$([ "$DD_X" = "$DV_X" ] && echo no || echo yes)"
echo "dirX2 source=$DD_X2 vault=$DV_X2  DIFFER=$([ "$DD_X2" = "$DV_X2" ] && echo no || echo yes)"
echo ""

probe() { # id desc expect ledger target note
  local id=$1 desc=$2 expect=$3 ledger=$4 target=$5 note=${6:-}
  local out status v r ev observed result
  set +e
  out=$(env SHOKUNIN_ROOT="$W/fleet" SOUJI_LEDGER="$ledger" timeout 20 "$TOOL" --stale-days 1 -- "$target" 2>&1)
  status=$?
  set -e
  v=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{print $3}')
  r=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{print $4}')
  ev=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{$1="";$2="";$3="";$4="";sub(/^\t\t\t\t/,"");print}')
  [ -n "$v" ] || v="NO-VERDICT"; [ -n "$r" ] || r="none"
  observed="$v($r)"
  [ "$observed" = "$expect" ] && result=PASS || result=FAIL
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$desc" "$expect" "$observed" "$result" "$note" >> "$OUT"
  printf '%-5s %-4s exit=%-2s %-24s %-24s %s\n' "$id" "$result" "$status" "$expect" "$observed" "$ev"
}

# D1 — 3-field DIR row: vault_sha256 column ABSENT; vault content DIFFERS
L=$RAW/d1.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\n' "$W/src/dirX" "$DD_X" "$W/vault/dirX"; } > "$L"
probe D1 "dir row, vault_sha256 column ABSENT, vault differs" "NOT-SAFE(none)" "$L" "$W/src/dirX" \
  "3-field row; read collapses missing columns -> vs empty -> digest check skipped"

# D2 — 4-field DIR row with trailing empty vault_sha256; vault DIFFERS
L=$RAW/d2.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t\t2026-10-18\tx\n' "$W/src/dirX" "$DD_X" "$W/vault/dirX"; } > "$L"
probe D2 "dir row, trailing EMPTY vault hash, vault differs" "NOT-SAFE(none)" "$L" "$W/src/dirX" "trailing-tab row"

# D3 — control: 3-field DIR row where vault IS an exact copy
L=$RAW/d3.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\n' "$W/src/dirX" "$DD_X2" "$W/vault/dirX2"; } > "$L"
probe D3 "control: 3-field dir row, vault exact copy" "SAFE(moved-to-obsidian)" "$L" "$W/src/dirX" "same shape, content preserved"

# D4 — control: vault digest present but STALE (equals source digest, vault has extra file)
L=$RAW/d4.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tx\n' "$W/src/dirX" "$DD_X" "$W/vault/dirX" "$DD_X"; } > "$L"
probe D4 "control: vault digest present but stale, vault differs" "NOT-SAFE(none)" "$L" "$W/src/dirX" "expected detection"

# D5 — FILE row, 3 fields (vault hash absent), vault file differs
printf 'alpha\n' > "$W/src/f.md"; printf 'BETA-DIFFERENT\n' > "$W/vault/f.md"
L=$RAW/d5.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\n' "$W/src/f.md" "$(sha "$W/src/f.md")" "$W/vault/f.md"; } > "$L"
probe D5 "file row, vault hash absent, vault differs" "NOT-SAFE(none)" "$L" "$W/src/f.md" "file branch fails closed"

# D6 — DIR row, vault hash absent AND vault dir missing
L=$RAW/d6.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\n' "$W/src/dirX" "$DD_X" "$W/vault/nope"; } > "$L"
probe D6 "dir row, vault hash absent, vault missing" "NOT-SAFE(none)" "$L" "$W/src/dirX" "unreachable"

# D7 — DIR row, vault hash absent, SOURCE hash also absent (2-field)
L=$RAW/d7.tsv; { printf '%s\n' "$HDR"; printf '%s\t%s\n' "$W/src/dirX" "$W/vault/dirX"; } > "$L"
probe D7 "dir row, both hashes absent (2-field)" "NOT-SAFE(none)" "$L" "$W/src/dirX" "read collapse shifts columns"

echo ""
echo "== D8: torn concurrent append, DIRECTORY target =="
# Writer appends a 3-field dir row (head), pauses, then appends the tail with a
# WRONG vault digest. Every COMPLETE row is wrong; only the torn 3-field head
# can produce a verdict, and if that verdict is SAFE it is a false-SAFE.
LU=$RAW/d8.tsv; printf '%s\n' "$HDR" > "$LU"
( i=0; while [ $i -lt 200 ]; do
    printf '%s\t%s\t%s' "$W/src/dirY" "$DD_Y" "$W/vault/dirY" >> "$LU"
    sleep 0.004
    printf '\t0000000000000000000000000000000000000000000000000000000000000000\t2026-10-18\ttorn\n' >> "$LU"
    sleep 0.002
    i=$((i+1)); done ) &
Wr=$!
safe=0; other=0; err=0; first=""
for i in $(seq 1 200); do
  out=$(env SHOKUNIN_ROOT="$W/fleet" SOUJI_LEDGER="$LU" timeout 20 "$TOOL" --stale-days 1 -- "$W/src/dirY" 2>&1); st=$?
  [ $st -ne 0 ] && err=$((err+1))
  if [ "$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{print $3}')" = "SAFE" ]; then
    safe=$((safe+1)); [ -n "$first" ] || first=$(printf '%s\n' "$out" | head -1)
  else other=$((other+1)); fi
done
wait $Wr 2>/dev/null
res=$([ "$safe" = 0 ] && echo PASS || echo FAIL)
printf 'D8\ttorn append, dir target, complete rows all WRONG\tsafe=0\tsafe=%d other=%d err=%d\t%s\t%s\n' \
  "$safe" "$other" "$err" "$res" "first_SAFE=${first:-none}" >> "$OUT"
printf 'D8    %-4s runs=200 SAFE=%d other=%d exit_err=%d\n' "$res" "$safe" "$other" "$err"
[ -n "$first" ] && printf '      first false-SAFE: %s\n' "$first"

echo ""
echo "== summary =="
awk -F'\t' 'NR>1 && $5=="FAIL"{print "FAIL "$1" want="$3" got="$4}' "$OUT"
printf 'PASS=%s FAIL=%s\n' "$(awk -F'\t' 'NR>1 && $5=="PASS"' "$OUT" | wc -l | tr -d ' ')" \
  "$(awk -F'\t' 'NR>1 && $5=="FAIL"' "$OUT" | wc -l | tr -d ' ')"
echo "probes: $OUT"
