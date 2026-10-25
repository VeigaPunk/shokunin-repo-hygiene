#!/usr/bin/env bash
# S55 cross-tool harness v2 — families s / t / u against every round-4 tool.
#
# v1 flaw (recorded): it passed --ledger/--vault to tools that do not accept
# them (r2-installed, impl-21) -> every case came back EXIT-2, and two oracles
# (C3, C5) were mis-specified. v2 uses per-tool argv and strict oracles.
#
# Per-tool argv:
#   r2-installed  SOUJI_LEDGER=<L> bash <tool> --stale-days 1 -- <target>
#   impl-20       bash <tool> --ledger <L> --vault <V> --fallback <target>
#   impl-24       bash <tool> --ledger <L> --vault <V> --fallback <target>
#   impl-21       SOUJI_LEDGER=<L> bash <tool> <target>
#
# Oracle: VERIFIED is only correct when the ledger row is fully self-consistent
# AND the vault copy exists with bytes whose digest equals the row's
# vault_sha256. Every deviation must be NOT-VERIFIED. A case marked WARN is an
# observation with a defensible alternative reading (not scored).
set -uo pipefail

REPO=/home/vgpnk/Projects/shokunin/souji-shokunin
REALVAULT=/home/vgpnk/Documents/shokoknowledge
LIVE_LEDGER=$REPO/corpus/knowledge/obsidian-ledger.tsv
RAW=$REPO/tests/vault/s55-raw
W=/tmp/s55-cross2
OUT=$RAW/cross2.tsv

rm -rf "$W"; mkdir -p "$W/fleet" "$W/src" "$W/vault" "$W/ledgers"
printf 'id\ttool\texpect\tobserved\tresult\tnote\n' > "$OUT"

sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }
dd() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }
HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
WRONG_SHA=1111111111111111111111111111111111111111111111111111111111111111
WRONG_DIGEST=0000000000000000000000000000000000000000000000000000000000000000
EMPTY_SHA=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

classify() {
  local o=$1 line
  line=$(printf '%s\n' "$o" | grep -aE '^[[:space:]]*(VERIFIED|NOT-VERIFIED|VERDICT|SAFE|NOT-SAFE)' | head -1)
  [ -n "$line" ] || { printf 'NO-VERDICT\n'; return 0; }
  case "$line" in
    *NOT-VERIFIED*|*NOT-SAFE*) printf 'NOT-VERIFIED\n' ;;
    *VERIFIED*|*SAFE*)         printf 'VERIFIED\n' ;;
    *) printf 'NO-VERDICT\n' ;;
  esac
}

invoke() { # $1 tool, $2 ledger, $3 target -> stdout; sets RC
  case "$1" in
    */souji-verify.sh)
      env SHOKUNIN_ROOT="$W/fleet" SOUJI_LEDGER="$2" timeout 30 bash "$1" --stale-days 1 -- "$3" 2>&1 ;;
    */impl-21.sh)
      env SHOKUNIN_ROOT="$W/fleet" SOUJI_LEDGER="$2" timeout 30 bash "$1" "$3" 2>&1 ;;
    *)
      env SHOKUNIN_ROOT="$W/fleet" SOUJI_LEDGER="$2" SOUJI_VAULT="$W/vault" \
        timeout 30 bash "$1" --ledger "$2" --vault "$W/vault" --fallback "$3" 2>&1 ;;
  esac
}

run_case() { # id expect ledger target note
  local id=$1 expect=$2 ledger=$3 target=$4 note=${5:-}
  local tool name out st got result
  for tool in $TOOLS; do
    name=$(basename "$tool")
    case "$name" in souji-verify.sh) name=r2-installed ;; impl-21.sh) name=impl-21 ;;
      souji-vault-verify.impl-20.sh) name=impl-20 ;; souji-vault-verify.impl-24.sh) name=impl-24 ;; esac
    [ -f "$tool" ] || { printf '%s\t%s\t%s\tTOOL-ABSENT\tSKIP\t%s\n' "$id" "$name" "$expect" "$note" >> "$OUT"; continue; }
    set +e; out=$(cd "$REPO" && invoke "$tool" "$ledger" "$target"); st=$?; set -e
    if [ $st -eq 124 ]; then got=TIMEOUT
    elif [ $st -ge 2 ]; then got="EXIT-$st"
    else got=$(classify "$out"); fi
    if [ "$expect" = "WARN" ]; then result=WARN
    elif [ "$got" = "$expect" ]; then result=PASS
    else result=FAIL; fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$name" "$expect" "$got" "$result" "$note" >> "$OUT"
    printf '%-5s %-13s %-4s want=%-13s got=%-13s %s\n' "$id" "$name" "$result" "$expect" "$got" "$note"
  done
}

TOOLS="$REPO/tools/souji-verify.sh $REPO/tools/souji-vault-verify.impl-20.sh $REPO/tools/souji-vault-verify.impl-24.sh $REPO/tools/impl-21.sh"

# ---- fixtures --------------------------------------------------------------
printf 'cross alpha\n' > "$W/src/fa.md"; cp "$W/src/fa.md" "$W/vault/fa.md"
printf 'cross beta\n'  > "$W/src/fb.md"; printf 'VAULT DIFFERS\n' > "$W/vault/fb.md"
FA_SS=$(sha "$W/src/fa.md"); FA_VS=$(sha "$W/vault/fa.md")
FB_SS=$(sha "$W/src/fb.md"); FB_VS=$(sha "$W/vault/fb.md")
mkdir -p "$W/src/dx" "$W/vault/dx" "$W/src/dy" "$W/vault/dy"
printf '1\n' > "$W/src/dx/1.txt"; printf '2\n' > "$W/src/dx/2.txt"
cp "$W/src/dx/1.txt" "$W/vault/dx/"; cp "$W/src/dx/2.txt" "$W/vault/dx/"
printf 'EXTRA\n' > "$W/vault/dx/extra.txt"
DX_SS=$(dd "$W/src/dx"); DX_VS=$(dd "$W/vault/dx")
cp "$W/src/dx/1.txt" "$W/vault/dy/"; cp "$W/src/dx/2.txt" "$W/vault/dy/"
cp "$W/src/dx/1.txt" "$W/src/dy/1.txt"; cp "$W/src/dx/2.txt" "$W/src/dy/2.txt"
DY_SS=$(dd "$W/src/dy"); DY_VS=$(dd "$W/vault/dy")
mkled() { local f=$1; shift; { printf '%s\n' "$HDR"; local r; for r in "$@"; do printf '%b\n' "$r"; done; } > "$f"; }

echo "fa file src=$FA_SS vault=$FA_VS (match)"
echo "fb file src=$FB_SS vault=$FB_VS (DIFFER)"
echo "dx dir  src=$DX_SS vault=$DX_VS (DIFFER)"
echo "dy dir  src=$DY_SS vault=$DY_VS (match)"
echo ""

echo "== baselines =="
L=$W/ledgers/c0.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$W/vault/fa.md\t$FA_VS\t2026-10-18\tx"
run_case C0 VERIFIED "$L" "$W/src/fa.md" "baseline file true-positive"
L=$W/ledgers/c1.tsv; mkled "$L" "$W/src/fb.md\t$FB_SS\t$W/vault/fb.md\t$FB_VS\t2026-10-18\tx"
run_case C1 WARN "$L" "$W/src/fb.md" "row self-consistent but vault bytes differ from source (ambiguity: WARN)"
L=$W/ledgers/c1b.tsv; mkled "$L" "$W/src/fb.md\t$FB_SS\t$W/vault/fb.md\t$WRONG_SHA\t2026-10-18\tx"
run_case C1b NOT-VERIFIED "$L" "$W/src/fb.md" "file, STALE vault digest"

echo ""
echo "== family s: exported_at / hash columns =="
L=$W/ledgers/c10.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$W/vault/fa.md\t$FA_VS\t\tx"
run_case C10 VERIFIED "$L" "$W/src/fa.md" "exported_at EMPTY, hashes ok"
L=$W/ledgers/c11.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$W/vault/fa.md\t$FA_VS\tnot-a-timestamp\tx"
run_case C11 VERIFIED "$L" "$W/src/fa.md" "exported_at GARBAGE, hashes ok"
L=$W/ledgers/c11b.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$W/vault/fa.md\t$FA_VS"
run_case C11b VERIFIED "$L" "$W/src/fa.md" "exported_at column ABSENT (5 fields)"
L=$W/ledgers/c9.tsv; mkled "$L" "$W/src/fa.md\t$(printf '%s' "$FA_SS" | tr 'a-f' 'A-F')\t$W/vault/fa.md\t$FA_VS\t2026-10-18\tx"
run_case C9 NOT-VERIFIED "$L" "$W/src/fa.md" "uppercase hex hash"

echo ""
echo "== family s/t: dir rows and empty hash columns =="
L=$W/ledgers/c2.tsv; mkled "$L" "$W/src/dx\t$DX_SS\t$W/vault/dx"
run_case C2 NOT-VERIFIED "$L" "$W/src/dx" "DIR, vault_sha256 column ABSENT, vault DIFFERS"
L=$W/ledgers/c3.tsv; mkled "$L" "$W/src/dy\t$DY_SS\t$W/vault/dy"
run_case C3 NOT-VERIFIED "$L" "$W/src/dy" "DIR, vault hash ABSENT (strict: never a receipt)"
L=$W/ledgers/c4.tsv; mkled "$L" "$W/src/dx\t$DX_SS\t$W/vault/dx\t\t2026-10-18\tx"
run_case C4 NOT-VERIFIED "$L" "$W/src/dx" "DIR, trailing EMPTY vault hash, vault DIFFERS"
L=$W/ledgers/c5.tsv; mkled "$L" "$W/src/dx\t$DX_SS\t$W/vault/dx\t$WRONG_DIGEST\t2026-10-18\tx"
run_case C5 NOT-VERIFIED "$L" "$W/src/dx" "DIR, STALE vault digest, vault DIFFERS"
L=$W/ledgers/c5b.tsv; mkled "$L" "$W/src/dy\t$DY_SS\t$W/vault/dy\t$DY_VS\t2026-10-18\tx"
run_case C5b VERIFIED "$L" "$W/src/dy" "DIR, both digests correct (true-positive)"

echo ""
echo "== family s: empty hash columns on FILES =="
L=$W/ledgers/c6.tsv; mkled "$L" "$W/src/fb.md\t$FB_SS\t$W/vault/fb.md"
run_case C6 NOT-VERIFIED "$L" "$W/src/fb.md" "FILE, vault hash column ABSENT, vault DIFFERS"
L=$W/ledgers/c6b.tsv; mkled "$L" "$W/src/fb.md\t$FB_SS\t$W/vault/fb.md\t\t2026-10-18\tx"
run_case C6b NOT-VERIFIED "$L" "$W/src/fb.md" "FILE, trailing EMPTY vault hash, vault DIFFERS"
L=$W/ledgers/c6c.tsv; mkled "$L" "$W/src/fa.md\t\t$W/vault/fa.md\t$FA_VS\t2026-10-18\tx"
run_case C6c NOT-VERIFIED "$L" "$W/src/fa.md" "FILE, source hash EMPTY"
L=$W/ledgers/c6d.tsv; mkled "$L" "$W/src/fa.md\t\t$W/vault/fa.md\t\t2026-10-18\tx"
run_case C6d NOT-VERIFIED "$L" "$W/src/fa.md" "FILE, BOTH hash columns EMPTY"

echo ""
echo "== family s: receipt semantics =="
L=$W/ledgers/c7.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$W/src/fa.md\t$FA_SS\t2026-10-18\tx"
run_case C7 NOT-VERIFIED "$L" "$W/src/fa.md" "self-move (source == vault path)"
L=$W/ledgers/c7d.tsv; mkled "$L" "$W/src/dy\t$DY_SS\t$W/src/dy\t$DY_SS\t2026-10-18\tx"
run_case C7d NOT-VERIFIED "$L" "$W/src/dy" "self-move, DIRECTORY"
L=$W/ledgers/c8.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$W/outside.md\t$FA_VS\t2026-10-18\tx"
cp "$W/src/fa.md" "$W/outside.md"
run_case C8 WARN "$L" "$W/src/fa.md" "vault_path outside the vault root (ambiguity: WARN)"

echo ""
echo "== family t: stat quirks (/proc/version = size 0, real content) =="
PS=$(sha /proc/version)
L=$W/ledgers/c13.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t/proc/version\t$PS\t2026-10-18\tx"
run_case C13 VERIFIED "$L" "$W/src/fa.md" "vault=/proc/version, REAL hash"
L=$W/ledgers/c14.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t/proc/version\t$EMPTY_SHA\t2026-10-18\tx"
run_case C14 NOT-VERIFIED "$L" "$W/src/fa.md" "vault=/proc/version, EMPTY-FILE digest bait"
L=$W/ledgers/c13b.tsv; mkled "$L" "/proc/version\t$PS\t/proc/version\t$PS\t2026-10-18\tx"
run_case C13b WARN "$L" "/proc/version" "self-move on /proc/version (ambiguity: WARN)"
FIFO=$W/fifo; [ -p "$FIFO" ] || mkfifo "$FIFO"
L=$W/ledgers/c15.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$FIFO\t$FA_VS\t2026-10-18\tx"
run_case C15 NOT-VERIFIED "$L" "$W/src/fa.md" "vault=FIFO (must not hang)"
ln -sfn "$W/nope" "$W/dangling"
L=$W/ledgers/c16.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$W/dangling\t$FA_VS\t2026-10-18\tx"
run_case C16 NOT-VERIFIED "$L" "$W/src/fa.md" "vault=dangling symlink"
rm -f "$W/vault/m000.md"; printf 'm000\n' > "$W/vault/m000.md"; chmod 000 "$W/vault/m000.md"
printf 'm000\n' > "$W/src/m000.md"; M000=$(sha "$W/src/m000.md")
L=$W/ledgers/c17.tsv; mkled "$L" "$W/src/m000.md\t$M000\t$W/vault/m000.md\t$M000\t2026-10-18\tx"
run_case C17 NOT-VERIFIED "$L" "$W/src/m000.md" "vault file mode 000 (unreadable)"
rm -f "$W/vault/fut.md"; printf 'fut\n' > "$W/vault/fut.md"; touch -d '2030-01-01' "$W/vault/fut.md"
printf 'fut\n' > "$W/src/fut.md"; FUT=$(sha "$W/src/fut.md")
L=$W/ledgers/c18.tsv; mkled "$L" "$W/src/fut.md\t$FUT\t$W/vault/fut.md\t$FUT\t2026-10-18\tx"
run_case C18 VERIFIED "$L" "$W/src/fut.md" "vault mtime 2030, hashes match"
rm -f "$W/vault/empt.md" "$W/src/empt.md"; : > "$W/vault/empt.md"; : > "$W/src/empt.md"
L=$W/ledgers/c18b.tsv; mkled "$L" "$W/src/empt.md\t$EMPTY_SHA\t$W/vault/empt.md\t$EMPTY_SHA\t2026-10-18\tx"
run_case C18b VERIFIED "$L" "$W/src/empt.md" "genuine empty file, empty digest"

echo ""
echo "== family u: ledger shape / concurrency =="
L=$W/ledgers/c12.tsv
{ printf '%s\n' "$HDR"; printf '%s\t\t%s\t%s\t2026-10-18\tunterminated' "$W/src/dx" "$W/vault/dx" "$WRONG_DIGEST"; } > "$L"
run_case C12 NOT-VERIFIED "$L" "$W/src/dx" "torn final line, no trailing newline"
L=$W/ledgers/c12b.tsv
{ printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t2026-10-18\tno-newline' "$W/src/dy" "$DY_SS" "$W/vault/dy" "$DY_VS"; } > "$L"
run_case C12b VERIFIED "$L" "$W/src/dy" "VALID row, no trailing newline"
L=$W/ledgers/c19.tsv; mkled "$L"
run_case C19 NOT-VERIFIED "$L" "$W/src/fa.md" "header-only ledger"
run_case C20 NOT-VERIFIED "$W/ledgers/absent.tsv" "$W/src/fa.md" "ledger file missing"
L=$W/ledgers/c21.tsv; mkled "$L" "$W/src/ghost.md\t$FA_SS\t$W/vault/fa.md\t$FA_VS\t2026-10-18\tx"
run_case C21 NOT-VERIFIED "$L" "$W/src/ghost.md" "target absent"
L=$W/ledgers/c23.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$W/vault/absent.md\t$FA_VS\t2026-10-18\tx"
run_case C23 NOT-VERIFIED "$L" "$W/src/fa.md" "vault path absent"
L=$W/ledgers/c24.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$W/vault/dy\t$FA_VS\t2026-10-18\tx"
run_case C24 NOT-VERIFIED "$L" "$W/src/fa.md" "file row, vault path is a DIR"
L=$W/ledgers/c25.tsv; mkled "$L" "$W/src/fa.md\t$FA_SS\t$W/vault/fa.md\t$FA_VS\t2026-10-18\textra\tmore"
run_case C25 VERIFIED "$L" "$W/src/fa.md" "extra trailing columns"

echo ""
echo "== C22: torn concurrent append, DIR target, every complete row WRONG =="
L=$W/ledgers/c22.tsv; printf '%s\n' "$HDR" > "$L"
( i=0; while [ $i -lt 120 ]; do
    printf '%s\t%s\t%s\n' "$W/src/dx" "$DX_SS" "$W/vault/dx" >> "$L"
    sleep 0.010
    printf '\t%s\t2026-10-18\ttail\n' "$WRONG_DIGEST" >> "$L"
    sleep 0.004
    i=$((i+1)); done ) &
WP=$!
for tool in $TOOLS; do
  name=$(basename "$tool")
  case "$name" in souji-verify.sh) name=r2-installed ;; impl-21.sh) name=impl-21 ;;
    souji-vault-verify.impl-20.sh) name=impl-20 ;; souji-vault-verify.impl-24.sh) name=impl-24 ;; esac
  [ -f "$tool" ] || continue
  s=0; n=0
  for i in $(seq 1 40); do
    out=$(cd "$REPO" && invoke "$tool" "$L" "$W/src/dx"); n=$((n+1))
    [ "$(classify "$out")" = "VERIFIED" ] && s=$((s+1))
  done
  res=$([ "$s" = 0 ] && echo PASS || echo FAIL)
  printf 'C22\t%s\tsafe=0\tverified=%d/%d\t%s\tconcurrent torn append; complete rows carry a WRONG digest\n' \
    "$name" "$s" "$n" "$res" >> "$OUT"
  printf '%-5s %-13s %-4s verified=%d/%d (want 0)\n' C22 "$name" "$res" "$s" "$n"
done
wait $WP 2>/dev/null

echo ""
echo "== read-only proof =="
V1=$(find "$REALVAULT" -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LV1=$(sha "$LIVE_LEDGER"); LN1=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
V2=$(find "$REALVAULT" -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LV2=$(sha "$LIVE_LEDGER"); LN2=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
RO=$([ "$V1" = "$V2" ] && [ "$LV1" = "$LV2" ] && echo UNCHANGED || echo CHANGED)
echo "vault      : $V1 -> $V2"
echo "live ledger: $LV1 (lines=$LN1) -> $LV2 (lines=$LN2)"
echo "READ-ONLY  : $RO"

echo ""
echo "== tool hashes =="
for tool in $TOOLS; do [ -f "$tool" ] && printf '%-38s %s\n' "$(basename "$tool")" "$(sha "$tool")"; done

echo ""
echo "== summary by tool (WARN excluded from both) =="
for tool in $TOOLS; do
  name=$(basename "$tool")
  case "$name" in souji-verify.sh) name=r2-installed ;; impl-21.sh) name=impl-21 ;;
    souji-vault-verify.impl-20.sh) name=impl-20 ;; souji-vault-verify.impl-24.sh) name=impl-24 ;; esac
  p=$(awk -F'\t' -v n="$name" '$2==n && $5=="PASS"' "$OUT" | wc -l | tr -d ' ')
  f=$(awk -F'\t' -v n="$name" '$2==n && $5=="FAIL"' "$OUT" | wc -l | tr -d ' ')
  w=$(awk -F'\t' -v n="$name" '$2==n && $5=="WARN"' "$OUT" | wc -l | tr -d ' ')
  printf '%-13s PASS=%-3s FAIL=%-3s WARN=%-3s\n' "$name" "$p" "$f" "$w"
done
echo ""
echo "== failures (false-VERIFIED first) =="
awk -F'\t' '$5=="FAIL" && $4=="VERIFIED"{printf "FALSE-VERIFIED %-13s %-5s %s\n",$2,$1,$6}' "$OUT"
echo "--"
awk -F'\t' '$5=="FAIL" && $4!="VERIFIED"{printf "%-15s %-13s %-5s want=%-13s got=%-13s %s\n","under-verified",$2,$1,$3,$4,$6}' "$OUT"
echo "results: $OUT"
