#!/usr/bin/env bash
# S55 decisive probe #2 — false-SAFE under CONCURRENT APPEND (assignment item u).
#
# Chain: a dir row is written in two separate write() calls:
#   (1) "source_path \t source_sha256 \t vault_path \n"     <- valid 3-field row
#   (2) "\t vault_sha256 \t exported_at \t note \n"          <- tail with the digest
# Between (1) and (2) the tool sees a complete 3-field row: vault_sha256 absent
# -> the vault-digest check is skipped (D1) -> SAFE even when the vault content
# does NOT match. Reproduce with a paced writer and a wrong final digest.
set -uo pipefail
REPO=/home/vgpnk/Projects/shokunin/souji-shokunin
TOOL=$REPO/tools/souji-verify.sh
RAW=$REPO/tests/vault/s55-raw
W=/tmp/s55-dec3
rm -rf "$W"; mkdir -p "$W/fleet" "$W/src/dirZ" "$W/vault/dirZ"
OUT=$RAW/probes4.tsv
printf 'id\tdescription\texpect\tobserved\tresult\tnote\n' > "$OUT"
HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
WRONG_DIGEST=0000000000000000000000000000000000000000000000000000000000000000

dd() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }
verdict() { printf '%s\n' "$1" | awk -F'\t' 'NR==1{print $3"("$4")"}'; }

printf 'z1\n' > "$W/src/dirZ/z1.txt"
cp "$W/src/dirZ/z1.txt" "$W/vault/dirZ/z1.txt"
printf 'VAULT-EXTRA-NOT-PRESERVED\n' > "$W/vault/dirZ/extra.txt"
DD=$(dd "$W/src/dirZ"); DV=$(dd "$W/vault/dirZ")
echo "source digest = $DD"
echo "vault  digest = $DV   (DIFFER=$([ "$DD" = "$DV" ] && echo no || echo yes))"
echo ""

# ---- E1: paced two-write torn append, final row has a WRONG digest ---------
LU=$RAW/e1.tsv; printf '%s\n' "$HDR" > "$LU"
( i=0; while [ $i -lt 150 ]; do
    printf '%s\t%s\t%s\n' "$W/src/dirZ" "$DD" "$W/vault/dirZ" >> "$LU"   # write 1
    sleep 0.010
    printf '\t%s\t2026-10-18\ttail\n' "$WRONG_DIGEST" >> "$LU"            # write 2
    sleep 0.004
    i=$((i+1)); done ) &
Wr=$!
safe=0; other=0; err=0; first=""
for i in $(seq 1 260); do
  out=$(env SHOKUNIN_ROOT="$W/fleet" SOUJI_LEDGER="$LU" timeout 20 "$TOOL" --stale-days 1 -- "$W/src/dirZ" 2>&1); st=$?
  [ $st -ne 0 ] && err=$((err+1))
  case "$(verdict "$out")" in
    SAFE*) safe=$((safe+1)); [ -n "$first" ] || first=$(printf '%s\n' "$out" | head -1) ;;
    *) other=$((other+1)) ;;
  esac
done
wait $Wr 2>/dev/null
res=$([ "$safe" = 0 ] && echo PASS || echo FAIL)
printf 'E1\ttorn two-write append, final vault digest WRONG\tsafe=0\tsafe=%d other=%d err=%d\t%s\tfirst_SAFE=%s\n' \
  "$safe" "$other" "$err" "$res" "${first:-none}" >> "$OUT"
printf 'E1    %-4s runs=260 SAFE=%d other=%d exit_err=%d\n' "$res" "$safe" "$other" "$err"
[ -n "$first" ] && printf '      first false-SAFE: %s\n' "$first"

# ---- E2: static proof of the same window (no concurrency needed) -----------
LU2=$RAW/e2.tsv
{ printf '%s\n' "$HDR"
  printf '%s\t%s\t%s\n' "$W/src/dirZ" "$DD" "$W/vault/dirZ"
  printf '\t%s\t2026-10-18\ttail\n' "$WRONG_DIGEST"; } > "$LU2"
out=$(env SHOKUNIN_ROOT="$W/fleet" SOUJI_LEDGER="$LU2" "$TOOL" --stale-days 1 -- "$W/src/dirZ")
v=$(verdict "$out")
res=$([ "${v%%(*}" = "SAFE" ] && echo FAIL || echo PASS)
printf 'E2\tsame ledger after the tail lands (digest WRONG)\tNOT-SAFE(none)\t%s\t%s\tfinal state is detected\n' "$v" "$res" >> "$OUT"
printf 'E2    %-4s final-state verdict = %s\n' "$res" "$v"

# ---- E3: control — same two-write pattern, vault content IS preserved -------
cp "$W/src/dirZ/z1.txt" "$W/vault/dirZ2/z1.txt" 2>/dev/null || { mkdir -p "$W/vault/dirZ2"; cp "$W/src/dirZ/z1.txt" "$W/vault/dirZ2/z1.txt"; }
DV2=$(dd "$W/vault/dirZ2")
LU3=$RAW/e3.tsv
{ printf '%s\n' "$HDR"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tx\n' "$W/src/dirZ" "$DD" "$W/vault/dirZ2" "$DV2"; } > "$LU3"
out=$(env SHOKUNIN_ROOT="$W/fleet" SOUJI_LEDGER="$LU3" "$TOOL" --stale-days 1 -- "$W/src/dirZ")
v=$(verdict "$out")
res=$([ "${v%%(*}" = "SAFE" ] && echo PASS || echo FAIL)
printf 'E3\tcontrol: vault exact copy, full row\tSAFE(moved-to-obsidian)\t%s\t%s\tlegit case still SAFE\n' "$v" "$res" >> "$OUT"
printf 'E3    %-4s control verdict = %s\n' "$res" "$v"

# ---- E4: how many complete rows in e1 were wrong at any moment -------------
echo ""
echo "== summary =="
awk -F'\t' 'NR>1{printf "%-3s %-4s want=%s got=%s\n",$1,$5,$3,$4}' "$OUT"
printf 'PASS=%s FAIL=%s\n' "$(awk -F'\t' 'NR>1 && $5=="PASS"' "$OUT" | wc -l | tr -d ' ')" \
  "$(awk -F'\t' 'NR>1 && $5=="FAIL"' "$OUT" | wc -l | tr -d ' ')"
echo "probes: $OUT"
