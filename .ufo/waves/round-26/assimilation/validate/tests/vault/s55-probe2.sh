#!/usr/bin/env bash
# S55 adversarial probe v2 (round 4) — isolated ledgers, one probe per row.
#
# v1 flaw (recorded): rows for the same source_path shared one ledger, so an
# earlier valid row satisfied try_obsidian and masked later probes; and the
# SAFE matcher used a substring case, which also matched "NOT-SAFE".
# v2 gives every probe its own ledger file and parses the verdict field.
#
# Read-only over the real vault: sha256sum/stat/find -printf only.
set -uo pipefail

REPO=/home/vgpnk/Projects/shokunin/souji-shokunin
TOOL=$REPO/tools/souji-verify.sh
REALVAULT=/home/vgpnk/Documents/shokoknowledge
LIVE_LEDGER=$REPO/corpus/knowledge/obsidian-ledger.tsv
TV=$REPO/tests/vault
SRC=$TV/s55-src
VLT=$TV/s55-vault
RAW=$TV/s55-raw
LD=$RAW/ledgers
TMP=/tmp/s55-fx
FLEET=$TMP/fleet

mkdir -p "$SRC" "$VLT" "$RAW" "$LD" "$TMP" "$FLEET"
LOG=$RAW/probe2-log.txt
PROBES=$RAW/probes2.tsv
: > "$LOG"
printf 'id\tfamily\texpect\tobserved\tresult\tledger\ttarget\texit\tevidence\tnote\n' > "$PROBES"

say() { printf '%s\n' "$*"; }
saylog() { printf '%s\n' "$*" >> "$LOG"; }

sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }
dir_digest() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }
HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
WRONG_SHA=1111111111111111111111111111111111111111111111111111111111111111
WRONG_DIGEST=0000000000000000000000000000000000000000000000000000000000000000
EMPTY_SHA=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

# ---- fixture factory: unique pair per probe --------------------------------
pair() { # $1 name -> sets P_SRC P_VLT P_SS P_VS
  local n=$1
  P_SRC="$SRC/$n.md"; P_VLT="$VLT/$n.md"
  printf 'payload for %s\n' "$n" > "$P_SRC"
  cp "$P_SRC" "$P_VLT"
  P_SS=$(sha "$P_SRC"); P_VS=$(sha "$P_VLT")
}
mkled() { # $1 ledger-path, rest = printf-format rows
  local f=$1; shift
  { printf '%s\n' "$HDR"; local r; for r in "$@"; do printf '%b\n' "$r"; done; } > "$f"
}

run_probe() { # id family expect ledger target note
  local id=$1 fam=$2 expect=$3 ledger=$4 target=$5 note=${6:-}
  local out status v r ev t0 t1 ms
  t0=$(date +%s%N)
  set +e
  out=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$ledger" timeout 20 \
        "$TOOL" --stale-days 1 -- "$target" 2>&1)
  status=$?
  set -e
  t1=$(date +%s%N); ms=$(( (t1 - t0) / 1000000 ))
  v=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{print $3}')
  r=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{print $4}')
  ev=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{$1="";$2="";$3="";$4="";sub(/^\t\t\t\t/,"");print}')
  [ -n "$v" ] || v="NO-VERDICT"
  [ -n "$r" ] || r="none"
  local observed="$v($r)" result
  if [ "$observed" = "$expect" ]; then result=PASS; else result=FAIL; fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s [%sms]\n' \
    "$id" "$fam" "$expect" "$observed" "$result" "$ledger" "$target" "$status" "$ev" "$note" "$ms" >> "$PROBES"
  printf '%-6s %-4s exit=%-2s %-22s %-24s %s\n' "$id" "$result" "$status" "$expect" "$observed" "$ev" >> "$LOG"
  say "$(printf '%-6s %-4s exit=%-2s %-22s %-24s %s' "$id" "$result" "$status" "$expect" "$observed" "$ev")"
}

say "== S55 probe v2 =="
say "tool sha : $(sha "$TOOL")"
say "proc sha : $(sha /proc/version) (stat size $(stat -c %s /proc/version))"
say ""

say "== S family — exported_at only differs / hash columns decide =="
pair p01; L=$LD/p01.tsv
mkled "$L" "$P_SRC\t$P_SS\t$P_VLT\t$P_VS\t\tno-timestamp"
run_probe S01 s "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "exported_at empty, hashes ok"
pair p02; L=$LD/p02.tsv
mkled "$L" "$P_SRC\t$P_SS\t$P_VLT\t$P_VS\tnot-a-timestamp\tgarbage"
run_probe S02 s "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "exported_at garbage, hashes ok"
pair p03; L=$LD/p03.tsv
mkled "$L" "$P_SRC\t$P_SS\t$P_VLT\t$P_VS"
run_probe S03 s "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "exported_at column absent (5 fields)"
pair p04; L=$LD/p04.tsv
mkled "$L" "$P_SRC\t$P_SS\t$P_VLT\t$P_VS\t2026-10-18T12:00:00-03:00\tbaseline"
run_probe S04 s "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "baseline valid timestamp"
pair p05; L=$LD/p05.tsv
mkled "$L" "$P_SRC\t$WRONG_SHA\t$P_VLT\t$P_VS\t2026-10-18\tx"
run_probe S05 s "NOT-SAFE(none)" "$L" "$P_SRC" "source hash WRONG"
pair p06; L=$LD/p06.tsv
mkled "$L" "$P_SRC\t$P_SS\t$P_VLT\t$WRONG_SHA\t2026-10-18\tx"
run_probe S06 s "NOT-SAFE(none)" "$L" "$P_SRC" "vault hash WRONG"
pair p07; L=$LD/p07.tsv
mkled "$L" "$P_SRC\t\t$P_VLT\t$P_VS\t2026-10-18\tx"
run_probe S07 s "NOT-SAFE(none)" "$L" "$P_SRC" "source hash EMPTY (file)"
pair p08; L=$LD/p08.tsv
mkled "$L" "$P_SRC\t$P_SS\t$P_VLT\t\t2026-10-18\tx"
run_probe S08 s "NOT-SAFE(none)" "$L" "$P_SRC" "vault hash EMPTY (file)"
pair p09; L=$LD/p09.tsv
mkled "$L" "$P_SRC\t\t$P_VLT\t\t2026-10-18\tx"
run_probe S09 s "NOT-SAFE(none)" "$L" "$P_SRC" "both hashes EMPTY (file)"
# dir rows
DSRC=$SRC/dirA; DVLT=$VLT/dirA
rm -rf "$DSRC" "$DVLT"; mkdir -p "$DSRC" "$DVLT"
printf 'one\n' > "$DSRC/one.txt"; printf 'two\n' > "$DSRC/two.txt"
cp "$DSRC/one.txt" "$DVLT/"; cp "$DSRC/two.txt" "$DVLT/"
DD=$(dir_digest "$DSRC"); DV=$(dir_digest "$DVLT")
L=$LD/s10.tsv; mkled "$L" "$DSRC\t$DD\t$DVLT\t$DV\tgarbage\tx"
run_probe S10 s "SAFE(moved-to-obsidian)" "$L" "$DSRC" "dir digests correct"
L=$LD/s11a.tsv; mkled "$L" "$DSRC\t\t$DVLT\t\t2026-10-18\tx"
run_probe S11a s "NOT-SAFE(none)" "$L" "$DSRC" "DIR both hash cols EMPTY"
L=$LD/s11b.tsv; mkled "$L" "$DSRC\t\t$DVLT\t$DV\t2026-10-18\tx"
run_probe S11b s "NOT-SAFE(none)" "$L" "$DSRC" "DIR source hash EMPTY"
L=$LD/s11c.tsv; mkled "$L" "$DSRC\t$DD\t$DVLT\t\t2026-10-18\tx"
run_probe S11c s "NOT-SAFE(none)" "$L" "$DSRC" "DIR vault hash EMPTY"
L=$LD/s11d.tsv; mkled "$L" "$DSRC\t\t$DVLT\t$WRONG_DIGEST\t2026-10-18\tx"
run_probe S11d s "NOT-SAFE(none)" "$L" "$DSRC" "DIR src EMPTY + vault digest WRONG"
L=$LD/s12.tsv; mkled "$L" "$DSRC\t$WRONG_DIGEST\t$DVLT\t$DV\t2026-10-18\tx"
run_probe S12 s "NOT-SAFE(none)" "$L" "$DSRC" "DIR source digest WRONG"
L=$LD/s13.tsv; mkled "$L" "$DSRC\t$DD\t$DVLT\t$WRONG_DIGEST\t2026-10-18\tx"
run_probe S13 s "NOT-SAFE(none)" "$L" "$DSRC" "DIR vault digest WRONG"
# path/column shape
pair p14; L=$LD/s14.tsv
mkled "$L" "$P_SRC\t$P_SS\t$VLT/absent.md\t$P_VS\t2026-10-18\tx"
run_probe S14 s "NOT-SAFE(none)" "$L" "$P_SRC" "vault path missing"
pair p15; L=$LD/s15.tsv
mkled "$L" "$P_SRC\t$P_SS\t$DVLT\t$P_VS\t2026-10-18\tx"
run_probe S15 s "NOT-SAFE(none)" "$L" "$P_SRC" "vault path is a DIR (file row)"
pair p16; L=$LD/s16.tsv
mkled "$L" "$P_SRC\t$P_SS\t$P_VLT\t2026-10-18\tx"
run_probe S16 s "NOT-SAFE(none)" "$L" "$P_SRC" "columns shifted (4 fields)"
pair p17; L=$LD/s17.tsv
printf '' > "$SRC/empty17.md"; printf '' > "$VLT/empty17.md"
mkled "$L" "$SRC/empty17.md\t$EMPTY_SHA\t$VLT/empty17.md\t$EMPTY_SHA\t2026-10-18\tx"
run_probe S17 s "SAFE(moved-to-obsidian)" "$L" "$SRC/empty17.md" "empty file + empty digest"
pair p18; L=$LD/s18.tsv
run_probe S18 s "NOT-SAFE(none)" "$L" "$P_SRC" "header-only ledger"
pair p19; L=$LD/s19.tsv
{ printf '%s\r\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tcrlf\r\n' "$P_SRC" "$P_SS" "$P_VLT" "$P_VS"; } > "$L"
run_probe S19 s "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "CRLF ledger, hashes ok"
pair p20; L=$LD/s20.tsv
mkled "$L" "$P_SRC\t$P_SS\t$P_SRC\t$P_SS\t2026-10-18\tx"
run_probe S20 s "NOT-SAFE(none)" "$L" "$P_SRC" "SELF-RECEIPT vault_path==source_path"
pair p21; L=$LD/s21.tsv
mkled "$L" "$P_SRC\t$P_SS\t$TMP/unrelated.md\t$P_VS\t2026-10-18\tx"
cp "$P_SRC" "$TMP/unrelated.md"
run_probe S21 s "NOT-SAFE(none)" "$L" "$P_SRC" "vault_path outside any vault (arbitrary file)"
pair p22; L=$LD/s22.tsv
mkled "$L" "$P_SRC\t$(printf '%s' "$P_SS" | tr 'a-f' 'A-F')\t$P_VLT\t$P_VS\t2026-10-18\tx"
run_probe S22 s "NOT-SAFE(none)" "$L" "$P_SRC" "uppercase hex hash"
pair p23; L=$LD/s23.tsv
mkled "$L" "$SRC/nonexistent.md\t$P_SS\t$P_VLT\t$P_VS\t2026-10-18\tx"
run_probe S23 s "NOT-SAFE(unreachable)" "$L" "$SRC/nonexistent.md" "source path absent (tool short-circuits)"
# coverage-loss: a LEGIT row whose source_path is non-canonical
pair p26; L=$LD/s26.tsv
mkled "$L" "$SRC/./p26.md\t$P_SS\t$P_VLT\t$P_VS\t2026-10-18\tx"
run_probe S26 s "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "ledger source_path = <dir>/./p26.md (non-canonical)"
pair p27; L=$LD/s27.tsv
mkled "$L" "$SRC/p27.md/../p27.md\t$P_SS\t$P_VLT\t$P_VS\t2026-10-18\tx"
run_probe S27 s "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "ledger source_path contains .. (non-canonical)"
pair p28; L=$LD/s28.tsv
ln -sfn "$SRC/p28.md" "$TMP/s55-link-src.md"
mkled "$L" "$TMP/s55-link-src.md\t$P_SS\t$P_VLT\t$P_VS\t2026-10-18\tx"
run_probe S28 s "SAFE(moved-to-obsidian)" "$L" "$TMP/s55-link-src.md" "source reached via symlink (canon mismatch?)"
pair p24; L=$LD/s24.tsv
mkled "$L" "$P_SRC\t$P_SS\t$P_VLT\t$P_VS\t2026-10-18\textra\tmore\tfields"
run_probe S24 s "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "extra trailing columns"
pair p25; L=$LD/s25.tsv
{ printf '%s\t%s\t%s\t%s\t2026-10-18\tno-header\n' "$P_SRC" "$P_SS" "$P_VLT" "$P_VS"; } > "$L"
run_probe S25 s "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "no header row (data first)"

say ""
say "== T family — stat quirks (fuse/overlay sim via /proc/version) =="
PROC_SHA=$(sha /proc/version)
pair t01; L=$LD/t01.tsv
rm -f "$VLT/procversion.md"; cp /proc/version "$VLT/procversion.md"
mkled "$L" "$P_SRC\t$P_SS\t$VLT/procversion.md\t$PROC_SHA\t2026-10-18\tx"
run_probe T01 t "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "vault=procversion copy, real hash"
L=$LD/t02.tsv; mkled "$L" "/proc/version\t$PROC_SHA\t/proc/version\t$PROC_SHA\t2026-10-18\tx"
run_probe T02 t "SAFE(moved-to-obsidian)" "$L" "/proc/version" "src=vault=/proc/version, real hash"
L=$LD/t03.tsv; mkled "$L" "$SRC/t03.md\t$P_SS\t/proc/version\t$WRONG_SHA\t2026-10-18\tx"
pair t03x >/dev/null 2>&1 || true
run_probe T03 t "NOT-SAFE(none)" "$L" "/proc/version" "target=/proc/version, ledger vault hash WRONG"
pair t10; L=$LD/t10.tsv
mkled "$L" "$P_SRC\t$P_SS\t/proc/version\t$EMPTY_SHA\t2026-10-18\tx"
run_probe T10 t "NOT-SAFE(none)" "$L" "$P_SRC" "vault=/proc/version, EMPTY-FILE digest bait"
L=$LD/t13.tsv; mkled "$L" "/proc/version\t$EMPTY_SHA\t$VLT/procversion.md\t$PROC_SHA\t2026-10-18\tx"
run_probe T13 t "NOT-SAFE(none)" "$L" "/proc/version" "source=/proc/version, empty-file digest bait"
pair t14; L=$LD/t14.tsv
mkled "$L" "$P_SRC\t$P_SS\t/dev/null\t$(sha /dev/null)\t2026-10-18\tx"
run_probe T14 t "NOT-SAFE(none)" "$L" "$P_SRC" "vault=/dev/null (size 0) with /dev/null digest"
pair t04; L=$LD/t04.tsv
FIFO=$TMP/fifo-vault2; [ -p "$FIFO" ] || mkfifo "$FIFO"
mkled "$L" "$P_SRC\t$P_SS\t$FIFO\t$P_SS\t2026-10-18\tx"
run_probe T04 t "NOT-SAFE(none)" "$L" "$P_SRC" "vault=FIFO (must not hang)"
pair t05; L=$LD/t05.tsv
ln -sfn "$TMP/nope-target" "$TMP/dangling2"
mkled "$L" "$P_SRC\t$P_SS\t$TMP/dangling2\t$P_SS\t2026-10-18\tx"
run_probe T05 t "NOT-SAFE(none)" "$L" "$P_SRC" "vault=dangling symlink"
pair t06; L=$LD/t06.tsv
mkled "$L" "$P_SRC\t$P_SS\t$TMP/symlink2\t$P_VS\t2026-10-18\tx"
ln -sfn "$P_VLT" "$TMP/symlink2"
run_probe T06 t "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "vault=symlink to real file"
pair t07; L=$LD/t07.tsv
rm -f "$VLT/mode000b.md" "$SRC/mode000b.md"
printf 'mode000\n' > "$VLT/mode000b.md"; chmod 000 "$VLT/mode000b.md"
printf 'mode000\n' > "$SRC/mode000b.md"
mkled "$L" "$SRC/mode000b.md\t$(sha "$SRC/mode000b.md")\t$VLT/mode000b.md\t$(sha "$SRC/mode000b.md")\t2026-10-18\tx"
run_probe T07 t "NOT-SAFE(none)" "$L" "$SRC/mode000b.md" "vault=mode-000 file (unreadable to us)"
pair t08; L=$LD/t08.tsv
touch -d '2030-01-01 00:00:00' "$P_VLT"
mkled "$L" "$P_SRC\t$P_SS\t$P_VLT\t$P_VS\t2026-10-18\tx"
run_probe T08 t "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "vault mtime 2030, hashes ok"
pair t09; L=$LD/t09.tsv
mkled "$L" "$P_SRC\t$P_SS\t$P_VLT\t$P_VS\t2026-10-18\tx"
printf 'mutated\n' >> "$P_VLT"
run_probe T09 t "NOT-SAFE(none)" "$L" "$P_SRC" "vault mutated after ledger write"
pair t11; L=$LD/t11.tsv
run_probe T11 t "NOT-SAFE(none)" "$L" "$FIFO" "target=FIFO"
ln -sfn "$TMP/loopB" "$TMP/loopA"; ln -sfn "$TMP/loopA" "$TMP/loopB"
run_probe T12 t "NOT-SAFE(none)" "$L" "$TMP/loopA" "target=symlink loop"
pair t15; L=$LD/t15.tsv
mkled "$L" "$P_SRC\t$P_SS\t$VLT/sub/../$(basename "$P_VLT")\t$P_VS\t2026-10-18\tx"
run_probe T15 t "SAFE(moved-to-obsidian)" "$L" "$P_SRC" "vault path with .. (ledger must use canonical paths)"
say "  (T15 is an observation probe: non-canonical vault_path in the ledger)"

say ""
say "== U family — concurrent ledger read while another process appends =="
verdict_of() { printf '%s\n' "$1" | awk -F'\t' 'NR==1{print $3}'; }

# U1 — writer appends valid rows for OTHER paths; target has NO row
pair u1a; pair u1b
u1b_src=$P_SRC; u1b_vlt=$P_VLT; u1b_ss=$P_SS; u1b_vs=$P_VS
LU=$LD/u1.tsv; mkled "$LU"
( i=0; while [ $i -lt 400 ]; do
    printf '%s\t%s\t%s\t%s\t2026-10-18\twriter\n' "$u1b_src" "$u1b_ss" "$u1b_vlt" "$u1b_vs" >> "$LU" 2>/dev/null
    i=$((i+1)); done ) &
W=$!
u_safe=0; u_other=0; u_err=0
for i in $(seq 1 25); do
  out=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$LU" timeout 20 "$TOOL" --stale-days 1 -- "$SRC/u1a.md" 2>&1); st=$?
  [ $st -ne 0 ] && u_err=$((u_err+1))
  [ "$(verdict_of "$out")" = "SAFE" ] && u_safe=$((u_safe+1)) || u_other=$((u_other+1))
done
wait $W 2>/dev/null
res=$([ "$u_safe" = 0 ] && [ "$u_err" = 0 ] && echo PASS || echo FAIL)
printf 'U1\tu\tNOT-SAFE x25\tSAFE=%d other=%d exit_err=%d\t%s\t%s\t%s\t-\t%s\t%s\n' \
  "$u_safe" "$u_other" "$u_err" "$res" "$LU" "$SRC/u1a.md" "writer appends valid rows for another path" >> "$PROBES"
say "U1  $res runs=25 SAFE=$u_safe other=$u_other exit_err=$u_err"

# U2 — torn writes: partial row, pause, tail with WRONG digest (final row wrong)
pair u2
LU=$LD/u2.tsv; mkled "$LU"
( i=0; while [ $i -lt 250 ]; do
    printf '%s\t\t%s' "$SRC/u2.md" "$VLT/u2.md" >> "$LU"
    sleep 0.004
    printf '\t%s\t2026-10-18\ttorn\n' "$WRONG_DIGEST" >> "$LU"
    sleep 0.002
    i=$((i+1)); done ) &
W=$!
u_safe=0; u_other=0; u_err=0; u_first=""
for i in $(seq 1 220); do
  out=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$LU" timeout 20 "$TOOL" --stale-days 1 -- "$SRC/u2.md" 2>&1); st=$?
  [ $st -ne 0 ] && u_err=$((u_err+1))
  if [ "$(verdict_of "$out")" = "SAFE" ]; then
    u_safe=$((u_safe+1)); [ -n "$u_first" ] || u_first=$(printf '%s\n' "$out" | head -1)
  else u_other=$((u_other+1)); fi
done
wait $W 2>/dev/null
res=$([ "$u_safe" = 0 ] && echo PASS || echo FAIL)
printf 'U2\tu\tNOT-SAFE x220 (torn)\tSAFE=%d other=%d exit_err=%d first_SAFE=%s\t%s\t%s\t-\t%s\t%s\n' \
  "$u_safe" "$u_other" "$u_err" "${u_first:-none}" "$res" "$LU" "$SRC/u2.md" \
  "torn concurrent append; every complete row has WRONG vault digest" >> "$PROBES"
say "U2  $res runs=220 SAFE=$u_safe other=$u_other exit_err=$u_err"
[ -n "$u_first" ] && say "    first false-SAFE: $u_first"

# U3 — static torn final line without newline
pair u3; LU=$LD/u3.tsv
mkled "$LU" "$SRC/u3.md\t\t$VLT/u3.md\t$WRONG_DIGEST\t2026-10-18\tunterminated"
run_probe U3 u "NOT-SAFE(none)" "$LU" "$SRC/u3.md" "torn final line, no trailing newline"
# U4 — VALID row without trailing newline (last-line-dropped check)
pair u4; LU=$LD/u4.tsv
u4_ss=$P_SS; u4_vs=$P_VS
{ printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tno-trailing-newline' "$SRC/u4.md" "$u4_ss" "$VLT/u4.md" "$u4_vs"; } > "$LU"
run_probe U4 u "SAFE(moved-to-obsidian)" "$LU" "$SRC/u4.md" "valid row, no trailing newline"
# U5 — ledger replaced via mv while reading
pair u5; LU=$LD/u5.tsv; mkled "$LU"
( i=0; while [ $i -lt 150 ]; do
    { printf '%s\n' "$HDR"; printf '%s\t\t%s\t\t2026-10-18\treplaced\n' "$SRC/u5.md" "$VLT/u5.md"; } > "$TMP/u5-next.tsv"
    mv -f "$TMP/u5-next.tsv" "$LU"
    i=$((i+1)); done ) &
W=$!
u_safe=0; u_other=0; u_err=0
for i in $(seq 1 60); do
  out=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$LU" timeout 20 "$TOOL" --stale-days 1 -- "$SRC/u1a.md" 2>&1); st=$?
  [ $st -ne 0 ] && u_err=$((u_err+1))
  [ "$(verdict_of "$out")" = "SAFE" ] && u_safe=$((u_safe+1)) || u_other=$((u_other+1))
done
wait $W 2>/dev/null
res=$([ "$u_safe" = 0 ] && [ "$u_err" = 0 ] && echo PASS || echo FAIL)
printf 'U5\tu\tNOT-SAFE x60\tSAFE=%d other=%d exit_err=%d\t%s\t%s\t%s\t-\t%s\t%s\n' \
  "$u_safe" "$u_other" "$u_err" "$res" "$LU" "$SRC/u1a.md" "ledger replaced via mv during read" >> "$PROBES"
say "U5  $res runs=60 SAFE=$u_safe other=$u_other exit_err=$u_err"
# U6 — valid row appended mid-run flips verdict (eventual consistency, observation)
pair u6; LU=$LD/u6.tsv; mkled "$LU"
u6_ss=$P_SS; u6_vs=$P_VS
before=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$LU" "$TOOL" --stale-days 1 -- "$SRC/u6.md" 2>&1 | awk -F'\t' '{print $3}')
printf '%s\t%s\t%s\t%s\t2026-10-18\tlate\n' "$SRC/u6.md" "$u6_ss" "$VLT/u6.md" "$u6_vs" >> "$LU"
after=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$LU" "$TOOL" --stale-days 1 -- "$SRC/u6.md" 2>&1 | awk -F'\t' '{print $3}')
res=$([ "$before" = "NOT-SAFE" ] && [ "$after" = "SAFE" ] && echo PASS || echo FAIL)
printf 'U6\tu\tNOT-SAFE then SAFE\tbefore=%s after=%s\t%s\t%s\t%s\t-\t%s\t%s\n' \
  "$before" "$after" "$res" "$LU" "$SRC/u6.md" "row appended between runs (expected flip)" >> "$PROBES"
say "U6  $res before=$before after=$after"
# U7 — parallel readers + concurrent appends
pair u7; LU=$LD/u7.tsv; mkled "$LU"
( i=0; while [ $i -lt 500 ]; do
    printf '%s\t%s\t%s\t%s\t2026-10-18\twriter\n' "$SRC/u7.md" "$WRONG_DIGEST" "$VLT/u7.md" "$WRONG_DIGEST" >> "$LU"
    i=$((i+1)); done ) &
W=$!
for k in $(seq 1 8); do
  ( s=0; for i in $(seq 1 30); do
      o=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$LU" timeout 20 "$TOOL" --stale-days 1 -- "$SRC/u1a.md" 2>&1)
      [ "$(printf '%s\n' "$o" | awk -F'\t' '{print $3}')" = "SAFE" ] && s=$((s+1))
    done; printf '%s\n' "$s" > "$TMP/u7-$k.count" ) &
done
wait $W 2>/dev/null
wait
u7_safe=$(cat "$TMP"/u7-*.count 2>/dev/null | paste -sd+ | bc)
[ -n "$u7_safe" ] || u7_safe=0
res=$([ "$u7_safe" = 0 ] && echo PASS || echo FAIL)
printf 'U7\tu\t0 SAFE across 8x30\tSAFE=%s\t%s\t%s\t%s\t-\t%s\t%s\n' \
  "$u7_safe" "$res" "$LU" "$SRC/u1a.md" "8 parallel readers x30, writer appends wrong-digest rows" >> "$PROBES"
say "U7  $res SAFE=$u7_safe (8 readers x 30 runs)"

say ""
say "== read-only proof over the real vault =="
V_SNAP1=$(find "$REALVAULT" -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LIVE_1=$(sha "$LIVE_LEDGER"); LIVE_N1=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
H1=$(sha "$REALVAULT/Home.md")
V_SNAP2=$(find "$REALVAULT" -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LIVE_2=$(sha "$LIVE_LEDGER"); LIVE_N2=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
say "vault snapshot : $V_SNAP1"
say "vault snapshot2: $V_SNAP2"
say "live ledger    : $LIVE_1 lines=$LIVE_N1  ->  $LIVE_2 lines=$LIVE_N2"
say "vault Home.md  : $H1"
RO=$([ "$V_SNAP1" = "$V_SNAP2" ] && [ "$LIVE_1" = "$LIVE_2" ] && echo UNCHANGED || echo CHANGED)
say "READ-ONLY: $RO"
printf 'RO\tproof\tUNCHANGED\t%s\t%s\t%s\t%s\t-\t%s\t%s\n' \
  "$RO" "$([ "$RO" = UNCHANGED ] && echo PASS || echo FAIL)" "$LIVE_LEDGER" "$REALVAULT" \
  "vault_before=$V_SNAP1 vault_after=$V_SNAP2 ledger=$LIVE_1/$LIVE_2 lines=$LIVE_N1/$LIVE_N2" \
  "vault + live ledger byte-identical before/after all probes" >> "$PROBES"

say ""
say "== summary =="
say "NOTE: S20/S21/S26/S27/S28 are EXPECTED-to-be-NOT-SAFE-by-design probes; the"
say "      tool returning SAFE there is a genuine false-SAFE, not a probe artifact."
awk -F'\t' 'NR>1 && $5=="FAIL"{print "FAIL "$1" want="$3" got="$4}' "$PROBES" >> "$LOG"
awk -F'\t' 'NR>1 && $5=="FAIL"{print "FAIL "$1" want="$3" got="$4}' "$PROBES"
say "PASS=$(awk -F'\t' 'NR>1 && $5=="PASS"' "$PROBES" | wc -l | tr -d ' ') FAIL=$(awk -F'\t' 'NR>1 && $5=="FAIL"' "$PROBES" | wc -l | tr -d ' ')"
say "raw   : $LOG"
say "probes: $PROBES"
