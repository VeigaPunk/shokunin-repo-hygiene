#!/usr/bin/env bash
# S55 adversarial probe (round 4) — Obsidian-CLI vault verification.
#
# Target under test: tools/souji-verify.sh (the installed r2 artifact).
# Read-only over the real vault: every vault access here is `sha256sum`/`stat`/
# `find -printf` (read-only). Nothing is written outside tests/vault/ and /tmp.
#
# Families
#   S  exported_at column only differs / hash columns decide (s)
#   T  stat quirks — /proc/version (stat size 0) simulates a fuse/overlay
#      mount whose size metadata disagrees with content (t)
#   U  concurrent ledger append while another process reads (u)
set -uo pipefail

REPO=/home/vgpnk/Projects/shokunin/souji-shokunin
TOOL=$REPO/tools/souji-verify.sh
REALVAULT=/home/vgpnk/Documents/shokoknowledge
LIVE_LEDGER=$REPO/corpus/knowledge/obsidian-ledger.tsv
TV=$REPO/tests/vault
SRC=$TV/s55-src
VLT=$TV/s55-vault
RAW=$TV/s55-raw
TMP=/tmp/s55-fx
FLEET=$TMP/fleet

mkdir -p "$SRC" "$VLT" "$RAW" "$TMP" "$FLEET"
LOG=$RAW/probe-log.txt
PROBES=$RAW/probes.tsv
: > "$LOG"
printf 'id\tfamily\texpect\tobserved\tresult\tledger\ttarget\texit\tevidence\tnote\n' > "$PROBES"

log() { printf '%s\n' "$*" | tee -a "$LOG" >/dev/null; printf '%s\n' "$*" >> "$LOG"; }
say() { printf '%s\n' "$*"; }

sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

# --- fixture payloads -------------------------------------------------------
printf 's55 payload alpha\n'            > "$SRC/file-alpha.md"
printf 's55 payload beta\n'             > "$SRC/file-beta.md"
printf ''                               > "$SRC/file-empty.md"
mkdir -p "$SRC/dir-case" "$SRC/dir-other"
printf 'one\n'                          > "$SRC/dir-case/one.txt"
printf 'two\n'                          > "$SRC/dir-case/two.txt"
printf 'other\n'                        > "$SRC/dir-other/other.txt"

printf 's55 payload alpha\n'            > "$VLT/file-alpha.md"
printf 'DIFFERENT VAULT CONTENT\n'      > "$VLT/file-beta.md"
printf ''                               > "$VLT/file-empty.md"
mkdir -p "$VLT/dir-case" "$VLT/dir-other"
printf 'one\n'                          > "$VLT/dir-case/one.txt"
printf 'two\n'                          > "$VLT/dir-case/two.txt"
printf 'other\n'                        > "$VLT/dir-other/other.txt"

# stat-quirk fixture: content of /proc/version copied to a normal file
cp /proc/version "$VLT/procversion-copy"
PROC_SHA=$(sha "$SRC/../s55-vault/procversion-copy")
EMPTY_SHA=$(sha "$SRC/file-empty.md")

SRC_A=$SRC/file-alpha.md;   VA_A=$VLT/file-alpha.md
SRC_B=$SRC/file-beta.md;    VA_B=$VLT/file-beta.md
SRC_E=$SRC/file-empty.md;   VA_E=$VLT/file-empty.md
SRC_D=$SRC/dir-case;        VA_D=$VLT/dir-case
SRC_DO=$SRC/dir-other;      VA_DO=$VLT/dir-other
SRC_A_SHA=$(sha "$SRC_A");  VA_A_SHA=$(sha "$VA_A")
SRC_B_SHA=$(sha "$SRC_B");  VA_B_SHA=$(sha "$VA_B")
DIR_SHA=$(sha "$SRC_D")     # not a digest of the dir; recomputed properly below
dir_digest() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }
SRC_D_DIGEST=$(dir_digest "$SRC_D"); VA_D_DIGEST=$(dir_digest "$VA_D")
SRC_DO_DIGEST=$(dir_digest "$SRC_DO"); VA_DO_DIGEST=$(dir_digest "$VA_DO")
WRONG_DIGEST=0000000000000000000000000000000000000000000000000000000000000000
WRONG_SHA=1111111111111111111111111111111111111111111111111111111111111111

HDR='source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$TV/s55-ledger-s.tsv"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$TV/s55-ledger-t.tsv"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$TV/s55-ledger-u.tsv"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$TV/s55-ledger-none.tsv"
LS=$TV/s55-ledger-s.tsv; LT=$TV/s55-ledger-t.tsv; LU=$TV/s55-ledger-u.tsv; LN=$TV/s55-ledger-none.tsv

# S rows ---------------------------------------------------------------------
# S01 hashes correct, exported_at empty          -> SAFE  (hashes decide)
printf '%s\t%s\t%s\t%s\t\tno-timestamp\n'                "$SRC_A" "$SRC_A_SHA" "$VA_A" "$VA_A_SHA" >> "$LS"
# S02 hashes correct, exported_at garbage
printf '%s\t%s\t%s\t%s\tnot-a-timestamp\tgarbage\n'      "$SRC_A" "$SRC_A_SHA" "$VA_A" "$VA_A_SHA" >> "$LS"
# S03 hashes correct, exported_at column ABSENT (5-col row)
printf '%s\t%s\t%s\t%s\n'                                "$SRC_A" "$SRC_A_SHA" "$VA_A" "$VA_A_SHA" >> "$LS"
# S04 hashes correct, exported_at valid (baseline)
printf '%s\t%s\t%s\t%s\t2026-10-18T12:00:00-03:00\tbaseline\n' "$SRC_A" "$SRC_A_SHA" "$VA_A" "$VA_A_SHA" >> "$LS"
# S05 source hash wrong, exported_at valid
printf '%s\t%s\t%s\t%s\t2026-10-18T12:00:00-03:00\tsrc-wrong\n' "$SRC_A" "$WRONG_SHA" "$VA_A" "$VA_A_SHA" >> "$LS"
# S06 vault hash wrong, exported_at empty
printf '%s\t%s\t%s\t%s\t\tvault-wrong\n'                 "$SRC_B" "$SRC_B_SHA" "$VA_B" "$WRONG_SHA" >> "$LS"
# S07 source hash EMPTY, vault hash correct
printf '%s\t%s\t%s\t%s\t2026-10-18T12:00:00-03:00\tsrc-empty-hash\n' "$SRC_A" "" "$VA_A" "$VA_A_SHA" >> "$LS"
# S08 vault hash EMPTY, source hash correct
printf '%s\t%s\t%s\t%s\t2026-10-18T12:00:00-03:00\tvault-empty-hash\n' "$SRC_A" "$SRC_A_SHA" "$VA_A" "" >> "$LS"
# S09 both hashes EMPTY (file target)
printf '%s\t\t%s\t\t2026-10-18T12:00:00-03:00\tboth-empty-hash\n' "$SRC_A" "$VA_A" >> "$LS"
# S10 DIR row, digests correct, exported_at garbage
printf '%s\t%s\t%s\t%s\tgarbage\t dir-baseline\n'        "$SRC_D" "$SRC_D_DIGEST" "$VA_D" "$VA_D_DIGEST" >> "$LS"
# S11a DIR row, BOTH hash columns EMPTY
printf '%s\t\t%s\t\t2026-10-18\tdir-both-empty\n'        "$SRC_D" "$VA_D" >> "$LS"
# S11b DIR row, source digest EMPTY, vault digest correct
printf '%s\t\t%s\t%s\t2026-10-18\tdir-src-empty\n'       "$SRC_D" "$VA_D" "$VA_D_DIGEST" >> "$LS"
# S11c DIR row, source digest correct, vault digest EMPTY
printf '%s\t%s\t%s\t\t2026-10-18\tdir-vault-empty\n'     "$SRC_D" "$SRC_D_DIGEST" "$VA_D" >> "$LS"
# S11d DIR row, source digest EMPTY, vault digest WRONG
printf '%s\t\t%s\t%s\t2026-10-18\tdir-src-empty-vault-wrong\n' "$SRC_D" "$VA_D" "$WRONG_DIGEST" >> "$LS"
# S12 DIR row, source digest WRONG, vault digest correct
printf '%s\t%s\t%s\t%s\t2026-10-18\tdir-src-wrong\n'     "$SRC_D" "$WRONG_DIGEST" "$VA_D" "$VA_D_DIGEST" >> "$LS"
# S13 DIR row, vault digest WRONG
printf '%s\t%s\t%s\t%s\t2026-10-18\tdir-vault-wrong\n'   "$SRC_D" "$SRC_D_DIGEST" "$VA_D" "$WRONG_DIGEST" >> "$LS"
# S14 file row, correct hashes but vault path missing
printf '%s\t%s\t%s\t%s\t2026-10-18\tvault-missing\n'     "$SRC_A" "$SRC_A_SHA" "$VLT/no-such-file.md" "$VA_A_SHA" >> "$LS"
# S15 file row, vault path is a DIR
printf '%s\t%s\t%s\t%s\t2026-10-18\tvault-is-dir\n'      "$SRC_A" "$SRC_A_SHA" "$VA_D" "$VA_A_SHA" >> "$LS"
# S16 file row, columns reordered (exported_at in vault_sha256 position)
printf '%s\t%s\t%s\t%s\t2026-10-18\treordered\n'         "$SRC_A" "$SRC_A_SHA" "$VA_A" "2026-10-18" >> "$LS"
# S17 empty file, empty-file digest both sides (legit empty artifact)
printf '%s\t%s\t%s\t%s\t2026-10-18\tempty-file\n'        "$SRC_E" "$EMPTY_SHA" "$VA_E" "$EMPTY_SHA" >> "$LS"

# T rows ---------------------------------------------------------------------
PROC_REAL=$(sha /proc/version)
# T01 source = /proc/version (stat size 0), vault = content copy, correct hashes
printf '%s\t%s\t%s\t%s\t2026-10-18\tproc-source\n' "$SRC_A" "$SRC_A_SHA" "$VLT/procversion-copy" "$PROC_REAL" >> "$LT"
# T02 vault = /proc/version, source = /proc/version, both hashes real
printf '%s\t%s\t%s\t%s\t2026-10-18\tproc-vault\n' /proc/version "$PROC_REAL" /proc/version "$PROC_REAL" >> "$LT"
# T03 vault = /proc/version, hash WRONG
printf '%s\t%s\t%s\t%s\t2026-10-18\tproc-vault-wrong\n' "$SRC_A" "$SRC_A_SHA" /proc/version "$WRONG_SHA" >> "$LT"
# T10 vault = /proc/version but hash = empty-file digest (stat-size shortcut bait)
printf '%s\t%s\t%s\t%s\t2026-10-18\tproc-empty-digest-bait\n' "$SRC_A" "$SRC_A_SHA" /proc/version "$EMPTY_SHA" >> "$LT"
# T13 source = /proc/version with empty-file digest (same bait, source side)
printf '%s\t%s\t%s\t%s\t2026-10-18\tproc-source-empty-bait\n' /proc/version "$EMPTY_SHA" "$VLT/procversion-copy" "$PROC_REAL" >> "$LT"
# T08 vault file with FUTURE mtime, correct hash (mtime must not matter)
printf 'future\n' > "$VLT/future-mtime.md"; touch -d '2030-01-01 00:00:00' "$VLT/future-mtime.md"
printf 'future\n' > "$SRC/future-mtime.md"
printf '%s\t%s\t%s\t%s\t2026-10-18\tfuture-mtime\n' "$SRC/future-mtime.md" "$(sha "$SRC/future-mtime.md")" "$VLT/future-mtime.md" "$(sha "$VLT/future-mtime.md")" >> "$LT"
# T07 vault file mode 000, correct hash
printf 'mode000\n' > "$VLT/mode000.md"; chmod 000 "$VLT/mode000.md"
printf 'mode000\n' > "$SRC/mode000.md"
printf '%s\t%s\t%s\t%s\t2026-10-18\tmode000\n' "$SRC/mode000.md" "$(sha "$SRC/mode000.md")" "$VLT/mode000.md" "$(sha "$SRC/mode000.md")" >> "$LT"

# /tmp-only T fixtures: FIFO, symlinks, loop
FIFO=$TMP/fifo-vault; [ -p "$FIFO" ] || mkfifo "$FIFO"
ln -sfn "$TMP/does-not-exist" "$TMP/dangling-link"
ln -sfn "$VA_A" "$TMP/symlink-ok"
ln -sfn "$TMP/loop-b" "$TMP/loop-a"; ln -sfn "$TMP/loop-a" "$TMP/loop-b"
printf '%s\t%s\t%s\t%s\t2026-10-18\tfifo-vault\n'     "$SRC_A" "$SRC_A_SHA" "$FIFO" "$SRC_A_SHA" >> "$LT"
printf '%s\t%s\t%s\t%s\t2026-10-18\tdangling-vault\n' "$SRC_A" "$SRC_A_SHA" "$TMP/dangling-link" "$SRC_A_SHA" >> "$LT"
printf '%s\t%s\t%s\t%s\t2026-10-18\tsymlink-vault\n'  "$SRC_A" "$SRC_A_SHA" "$TMP/symlink-ok" "$SRC_A_SHA" >> "$LT"
printf '%s\t%s\t%s\t%s\t2026-10-18\tloop-vault\n'     "$SRC_A" "$SRC_A_SHA" "$TMP/loop-a" "$SRC_A_SHA" >> "$LT"

say "== S55 probe: fixtures built =="
say "tool      : $TOOL"
say "tool sha  : $(sha "$TOOL")"
say "proc sha  : $PROC_REAL  (stat says size $(stat -c %s /proc/version))"
say "ledgers   : $LS $LT $LU $LN"
say ""

# --- probe runner -----------------------------------------------------------
run_probe() { # id family expect ledger target note
  local id=$1 fam=$2 expect=$3 ledger=$4 target=$5 note=${6:-}
  local out status v r ev
  set +e
  out=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$ledger" timeout 15 \
        "$TOOL" --stale-days 1 -- "$target" 2>&1)
  status=$?
  set -e
  v=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{print $3}')
  r=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{print $4}')
  ev=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{$1="";$2="";$3="";$4="";sub(/^\t\t\t\t/,"");print}')
  [ -n "$v" ] || v="NO-VERDICT"
  [ -n "$r" ] || r="none"
  local observed="$v($r)"
  local result
  if [ "$observed" = "$expect" ]; then result=PASS; else result=FAIL; fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$id" "$fam" "$expect" "$observed" "$result" "$ledger" "$target" "$status" "$ev" "$note" >> "$PROBES"
  printf '%-6s %-4s exit=%-2s want=%-22s got=%-22s %s\n' "$id" "$result" "$status" "$expect" "$observed" "$ev" >> "$LOG"
  say "$(printf '%-6s %-4s exit=%-2s want=%-22s got=%-22s %s' "$id" "$result" "$status" "$expect" "$observed" "$ev")"
}

say "== S family: exported_at only differs / hashes decide =="
run_probe S01 s "SAFE(moved-to-obsidian)"  "$LS" "$SRC_A" "exported_at empty"
run_probe S02 s "SAFE(moved-to-obsidian)"  "$LS" "$SRC_A" "exported_at garbage"
run_probe S03 s "SAFE(moved-to-obsidian)"  "$LS" "$SRC_A" "exported_at column absent"
run_probe S04 s "SAFE(moved-to-obsidian)"  "$LS" "$SRC_A" "baseline valid ts"
run_probe S05 s "NOT-SAFE(none)"           "$LS" "$SRC_A" "source hash wrong"
run_probe S06 s "NOT-SAFE(none)"           "$LS" "$SRC_B" "vault hash wrong"
run_probe S07 s "NOT-SAFE(none)"           "$LS" "$SRC_A" "source hash empty"
run_probe S08 s "NOT-SAFE(none)"           "$LS" "$SRC_A" "vault hash empty"
run_probe S09 s "NOT-SAFE(none)"           "$LS" "$SRC_A" "both hashes empty (file)"
run_probe S10 s "SAFE(moved-to-obsidian)"  "$LS" "$SRC_D" "dir digests correct"
run_probe S11a s "NOT-SAFE(none)"          "$LS" "$SRC_D" "dir both hash cols empty"
run_probe S11b s "NOT-SAFE(none)"          "$LS" "$SRC_D" "dir source hash empty"
run_probe S11c s "NOT-SAFE(none)"          "$LS" "$SRC_D" "dir vault hash empty"
run_probe S11d s "NOT-SAFE(none)"          "$LS" "$SRC_D" "dir src empty + vault wrong"
run_probe S12 s "NOT-SAFE(none)"           "$LS" "$SRC_D" "dir source digest wrong"
run_probe S13 s "NOT-SAFE(none)"           "$LS" "$SRC_D" "dir vault digest wrong"
run_probe S14 s "NOT-SAFE(none)"           "$LS" "$SRC_A" "vault path missing"
run_probe S15 s "NOT-SAFE(none)"           "$LS" "$SRC_A" "vault path is a dir"
run_probe S16 s "NOT-SAFE(none)"           "$LS" "$SRC_A" "columns reordered"
run_probe S17 s "SAFE(moved-to-obsidian)"  "$LS" "$SRC_E" "empty file, empty digest"
run_probe S18 s "NOT-SAFE(none)"           "$LN" "$SRC_A" "header-only ledger"

say ""
say "== T family: stat quirks (fuse/overlay simulation via /proc/version) =="
run_probe T01 t "SAFE(moved-to-obsidian)"  "$LT" "$SRC_A" "vault=procversion-copy"
run_probe T02 t "SAFE(moved-to-obsidian)"  "$LT" /proc/version "src+vault=/proc/version, real hashes"
run_probe T03 t "NOT-SAFE(none)"           "$LT" "$SRC_A" "vault=/proc/version, wrong hash"
run_probe T10 t "NOT-SAFE(none)"           "$LT" "$SRC_A" "vault=/proc/version, empty-file digest bait"
run_probe T13 t "NOT-SAFE(none)"           "$LT" /proc/version "source=/proc/version, empty digest bait"
run_probe T04 t "NOT-SAFE(none)"           "$LT" "$SRC_A" "vault=FIFO (must not hang)"
run_probe T05 t "NOT-SAFE(none)"           "$LT" "$SRC_A" "vault=dangling symlink"
run_probe T06 t "SAFE(moved-to-obsidian)"  "$LT" "$SRC_A" "vault=symlink to real file"
run_probe T07 t "NOT-SAFE(none)"           "$LT" "$SRC_A" "vault=mode 000 file"
run_probe T08 t "SAFE(moved-to-obsidian)"  "$LT" "$SRC/future-mtime.md" "vault mtime in 2030"
run_probe T11 t "NOT-SAFE(none)"           "$LT" "$TMP/fifo-vault" "target=FIFO"
run_probe T12 t "NOT-SAFE(none)"           "$LT" "$TMP/loop-a" "target=symlink loop"

say ""
say "== U family: concurrent append while reading =="
# U1: writer appends valid rows for OTHER paths while we probe a WRONG-hash target
( i=0; while [ $i -lt 300 ]; do
    printf '%s\t%s\t%s\t%s\t2026-10-18\twriter\n' "$SRC_DO" "$SRC_DO_DIGEST" "$VA_DO" "$VA_DO_DIGEST" >> "$LU"
    i=$((i+1)); done ) &
W1=$!
u1_safe=0; u1_other=0; u1_err=0
for i in $(seq 1 25); do
  out=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$LU" timeout 15 "$TOOL" --stale-days 1 -- "$SRC_B" 2>&1); st=$?
  [ $st -ne 0 ] && u1_err=$((u1_err+1))
  case "$out" in *"SAFE"*) u1_safe=$((u1_safe+1)) ;; *) u1_other=$((u1_other+1)) ;; esac
done
wait $W1 2>/dev/null
printf 'U1\tu\tNOT-SAFE(none) x25\tSAFE=%d other=%d exit_err=%d\t%s\t%s\t%s\t-\t%s\t%s\n' \
  "$u1_safe" "$u1_other" "$u1_err" \
  "$([ "$u1_safe" = 0 ] && [ "$u1_err" = 0 ] && echo PASS || echo FAIL)" \
  "$LU" "$SRC_B" "valid rows appended for other paths" >> "$PROBES"
say "U1  $( [ "$u1_safe" = 0 ] && [ "$u1_err" = 0 ] && echo PASS || echo FAIL ) runs=25 safe=$u1_safe notsafe_or_other=$u1_other exit_err=$u1_err"

# U2: torn write — writer emits sp<TAB><TAB>vp, pauses, then <TAB>WRONGDIGEST<TAIL>
# Final complete row has a WRONG vault digest => a SAFE can only come from the
# torn intermediate state (empty hash columns).
: > "$LU"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$LU"
( i=0; while [ $i -lt 250 ]; do
    printf '%s\t\t%s' "$SRC_D" "$VA_D" >> "$LU"
    sleep 0.004
    printf '\t%s\t2026-10-18\ttorn\n' "$WRONG_DIGEST" >> "$LU"
    sleep 0.002
    i=$((i+1)); done ) &
W2=$!
u2_safe=0; u2_notsafe=0; u2_err=0; u2_first=""
for i in $(seq 1 220); do
  out=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$LU" timeout 15 "$TOOL" --stale-days 1 -- "$SRC_D" 2>&1); st=$?
  [ $st -ne 0 ] && u2_err=$((u2_err+1))
  v=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{print $3}')
  if [ "$v" = "SAFE" ]; then
    u2_safe=$((u2_safe+1))
    [ -n "$u2_first" ] || u2_first=$(printf '%s\n' "$out" | head -1)
  else
    u2_notsafe=$((u2_notsafe+1))
  fi
done
wait $W2 2>/dev/null
printf 'U2\tu\tNOT-SAFE(none) x220 (torn row)\tSAFE=%d NOT-SAFE=%d exit_err=%d first_SAFE=%s\t%s\t%s\t-\t%s\t%s\n' \
  "$u2_safe" "$u2_notsafe" "$u2_err" "$u2_first" \
  "$([ "$u2_safe" = 0 ] && echo PASS || echo FAIL)" \
  "$LU" "$SRC_D" "torn concurrent append; final row vault digest WRONG" >> "$PROBES"
say "U2  $( [ "$u2_safe" = 0 ] && echo PASS || echo FAIL ) runs=220 safe=$u2_safe notsafe=$u2_notsafe exit_err=$u2_err"
[ -n "$u2_first" ] && say "    first false-SAFE line: $u2_first"

# U3: static torn final line, no trailing newline
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$LU"
printf '%s\t\t%s\t%s\t2026-10-18\tunterminated' "$SRC_D" "$VA_D" "$WRONG_DIGEST" >> "$LU"
run_probe U3 u "NOT-SAFE(none)" "$LU" "$SRC_D" "static torn final line, no newline"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$LU"
printf '%s\t%s\t%s\t%s\t2026-10-18\tunterminated-valid' "$SRC_D" "$SRC_D_DIGEST" "$VA_D" "$VA_D_DIGEST" >> "$LU"
run_probe U4 u "SAFE(moved-to-obsidian)" "$LU" "$SRC_D" "valid row, no trailing newline (false NOT-SAFE?)"

# U5: ledger replaced (rename) while reading
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$LU"
( i=0; while [ $i -lt 120 ]; do
    { printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
      printf '%s\t\t%s\t\t2026-10-18\treplaced\n' "$SRC_D" "$VA_D"; } > "$TMP/u5-next.tsv"
    mv -f "$TMP/u5-next.tsv" "$LU"
    i=$((i+1)); done ) &
W3=$!
u5_err=0; u5_notsafe=0; u5_safe=0
for i in $(seq 1 60); do
  out=$(env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$LU" timeout 15 "$TOOL" --stale-days 1 -- "$SRC_B" 2>&1); st=$?
  [ $st -ne 0 ] && u5_err=$((u5_err+1))
  case "$out" in *"SAFE"*) u5_safe=$((u5_safe+1)) ;; *) u5_notsafe=$((u5_notsafe+1)) ;; esac
done
wait $W3 2>/dev/null
printf 'U5\tu\tNOT-SAFE(none) x60\tSAFE=%d other=%d exit_err=%d\t%s\t%s\t%s\t-\t%s\t%s\n' \
  "$u5_safe" "$u5_notsafe" "$u5_err" \
  "$([ "$u5_safe" = 0 ] && [ "$u5_err" = 0 ] && echo PASS || echo FAIL)" \
  "$LU" "$SRC_B" "ledger replaced via mv during read" >> "$PROBES"
say "U5  $( [ "$u5_safe" = 0 ] && [ "$u5_err" = 0 ] && echo PASS || echo FAIL ) runs=60 safe=$u5_safe other=$u5_notsafe exit_err=$u5_err"

say ""
say "== read-only proof over the real vault =="
V_SNAP1=$(find "$REALVAULT" -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LIVE_1=$(sha "$LIVE_LEDGER"); LIVE_LINES=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
V_SAMPLE=$(sha "$REALVAULT/Home.md")
say "vault snapshot before : $V_SNAP1"
say "live ledger sha       : $LIVE_1  lines=$LIVE_LINES"
say "vault Home.md sha     : $V_SAMPLE"
V_SNAP2=$(find "$REALVAULT" -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LIVE_2=$(sha "$LIVE_LEDGER"); LIVE_LINES2=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
say "vault snapshot after  : $V_SNAP2"
say "live ledger sha after : $LIVE_2  lines=$LIVE_LINES2"
if [ "$V_SNAP1" = "$V_SNAP2" ] && [ "$LIVE_1" = "$LIVE_2" ]; then
  say "READ-ONLY: UNCHANGED (vault + live ledger byte-identical before/after)"
  RO=UNCHANGED
else
  say "READ-ONLY: CHANGED — investigate"
  RO=CHANGED
fi
printf 'RO\tproof\tUNCHANGED\t%s\t%s\t%s\t%s\t-\t%s\t%s\n' \
  "$([ "$RO" = UNCHANGED ] && echo PASS || echo FAIL)" "$LIVE_LEDGER" "$REALVAULT" \
  "vault_snap_before=$V_SNAP1 vault_snap_after=$V_SNAP2 ledger_lines=$LIVE_LINES/$LIVE_LINES2" \
  "read-only proof (note: sibling seats may also read concurrently)" >> "$PROBES"

say ""
say "== summary =="
awk -F'\t' 'NR>1 && $5=="PASS"{p++} NR>1 && $5=="FAIL"{f++; print "FAIL: "$1" want="$3" got="$4}' "$PROBES" | tee -a "$LOG"
say "PASS=$(awk -F'\t' 'NR>1 && $5=="PASS"' "$PROBES" | wc -l | tr -d ' ') FAIL=$(awk -F'\t' 'NR>1 && $5=="FAIL"' "$PROBES" | wc -l | tr -d ' ')"
say "raw: $LOG"
say "probes: $PROBES"
