#!/usr/bin/env bash
# s30-adjudicate.sh — S30 runner follow-up: adjudicate S55's FAILs.
#
# Hypothesis: S55's false-SAFE FAILs (S05/S07/S08/S09/S11a-d/S12/S13/S14/
# S15/S16/T03/T04/T05/T10/T13) come from a shared multi-row ledger where an
# earlier VALID row for the same source path decides the verdict — the tool
# returns SAFE on the first fully-matching row by design ("a matching row
# exists"), so a later bad row for the same path cannot flip it. The probe
# expected the last/bad row to decide.
#
# Method: replay each failing case with an ISOLATED single-row ledger.
# All fixtures under /tmp; read-only over the lane and the real vault.
set -uo pipefail
export LC_ALL=C

REPO=/home/vgpnk/Projects/shokunin/souji-shokunin
TOOL=$REPO/tools/souji-verify.sh
W=/tmp/s30-adjudicate
rm -rf "$W"; mkdir -p "$W/src" "$W/vault" "$W/fleet"
SRC=$W/src; VLT=$W/vault

sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }
dir_digest() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }

# fixtures
printf 's30 adj payload alpha\n' > "$SRC/file-alpha.md"
printf 's30 adj payload beta\n'  > "$SRC/file-beta.md"
cp "$SRC/file-alpha.md" "$VLT/file-alpha.md"
printf 'DIFFERENT VAULT CONTENT\n' > "$VLT/file-beta.md"
mkdir -p "$SRC/dir-case" "$VLT/dir-case"
printf 'one\n' > "$SRC/dir-case/one.txt"; printf 'two\n' > "$SRC/dir-case/two.txt"
cp -r "$SRC/dir-case/." "$VLT/dir-case/"

A=$SRC/file-alpha.md;  VA=$VLT/file-alpha.md
B=$SRC/file-beta.md;   VB=$VLT/file-beta.md
D=$SRC/dir-case;       VD=$VLT/dir-case
A_SHA=$(sha "$A"); B_SHA=$(sha "$B"); VA_SHA=$(sha "$VA"); VB_SHA=$(sha "$VB")
D_DIG=$(dir_digest "$D"); VD_DIG=$(dir_digest "$VD")
WRONG=1111111111111111111111111111111111111111111111111111111111111111
HDR='source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

say() { printf '%s\n' "$*"; }
RES=$W/verdicts.tsv; : > "$RES"

run_case() { # id desc ledger target expect  (expect: SAFE|NOT-SAFE)
  local id=$1 desc=$2 led=$3 tgt=$4 want=$5
  local out rc=0
  out=$(env SHOKUNIN_ROOT="$W/fleet" SOUJI_LEDGER="$led" timeout 20 \
        bash "$TOOL" --stale-days 1 -- "$tgt" 2>&1) || rc=$?
  local v; v=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{print $3}')
  local r; r=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1{print $4}')
  local res=FAIL; [ "$v" = "$want" ] && res=PASS
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$res" "$want" "$v" "$r" "$desc" >> "$RES"
  say "$(printf '%-4s %-4s want=%-8s got=%-8s rc=%s  %s' "$id" "$res" "$want" "${v:-NO-VERDICT}" "$rc" "$desc")"
}

# --- isolated single-row ledgers (one row = one case) -----------------------
one_row() { # file sp ss vp vs exp note -> header + exactly one tab-separated row
  local f=$1; shift
  printf "$HDR\n" > "$f"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$@" >> "$f"
}
# L_A_bad_src: source hash wrong (S05/S12/T13-isolated) -> NOT-SAFE
one_row "$W/L_bad_src.tsv" "$A" "$WRONG" "$VA" "$VA_SHA" "2026-10-18" "bad-src"
run_case A1 "isolated: source hash wrong (S05)" "$W/L_bad_src.tsv" "$A" NOT-SAFE
# L_bad_vault: vault hash wrong (S06-isolated) -> NOT-SAFE
one_row "$W/L_bad_vault.tsv" "$B" "$B_SHA" "$VB" "$WRONG" "2026-10-18" "bad-vault"
run_case A2 "isolated: vault hash wrong (S06)" "$W/L_bad_vault.tsv" "$B" NOT-SAFE
# L_empty_src: source hash empty (S07) -> NOT-SAFE
one_row "$W/L_empty_src.tsv" "$A" "" "$VA" "$VA_SHA" "2026-10-18" "empty-src"
run_case A3 "isolated: source hash empty (S07)" "$W/L_empty_src.tsv" "$A" NOT-SAFE
# L_empty_vault: vault hash empty (S08) -> NOT-SAFE
one_row "$W/L_empty_vault.tsv" "$A" "$A_SHA" "$VA" "" "2026-10-18" "empty-vault"
run_case A4 "isolated: vault hash empty (S08)" "$W/L_empty_vault.tsv" "$A" NOT-SAFE
# L_both_empty: both empty file (S09) -> NOT-SAFE
one_row "$W/L_both_empty.tsv" "$A" "" "$VA" "" "2026-10-18" "both-empty"
run_case A5 "isolated: both hashes empty file (S09)" "$W/L_both_empty.tsv" "$A" NOT-SAFE
# L_dir_empty: dir row both empty (S11a) -> NOT-SAFE
one_row "$W/L_dir_empty.tsv" "$D" "" "$VD" "" "2026-10-18" "dir-both-empty"
run_case A6 "isolated: dir both hash cols empty (S11a)" "$W/L_dir_empty.tsv" "$D" NOT-SAFE
# L_dir_ok: dir digests correct (S10) -> SAFE
one_row "$W/L_dir_ok.tsv" "$D" "$D_DIG" "$VD" "$VD_DIG" "2026-10-18" "dir-ok"
run_case A7 "isolated: dir digests correct (S10)" "$W/L_dir_ok.tsv" "$D" SAFE
# L_vault_missing: correct hashes, vault path missing (S14) -> NOT-SAFE
one_row "$W/L_vault_missing.tsv" "$A" "$A_SHA" "$VLT/no-such-file.md" "$VA_SHA" "2026-10-18" "vault-missing"
run_case A8 "isolated: vault path missing (S14)" "$W/L_vault_missing.tsv" "$A" NOT-SAFE
# L_vault_is_dir: file row, vault path is a dir (S15) -> NOT-SAFE
one_row "$W/L_vault_is_dir.tsv" "$A" "$A_SHA" "$VD" "$VA_SHA" "2026-10-18" "vault-is-dir"
run_case A9 "isolated: vault path is a dir (S15)" "$W/L_vault_is_dir.tsv" "$A" NOT-SAFE
# L_reordered: columns reordered (S16) -> NOT-SAFE
one_row "$W/L_reordered.tsv" "$A" "$A_SHA" "$VA" "2026-10-18" "reordered"
run_case A10 "isolated: columns reordered (S16)" "$W/L_reordered.tsv" "$A" NOT-SAFE
# L_nonl: valid row WITHOUT trailing newline (S55 U4) -> record direction
{
  printf "$HDR\n"
  printf '%s\t%s\t%s\t%s\t%s\t%s' "$A" "$A_SHA" "$VA" "$VA_SHA" "2026-10-18" "unterminated"
} > "$W/L_nonl.tsv"
run_case A11 "isolated: valid row, NO trailing newline (U4)" "$W/L_nonl.tsv" "$A" SAFE

# --- confound replication: shared ledger, valid row FIRST (S55 S05 shape) ---
{
  printf "$HDR\n"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$A" "$A_SHA" "$VA" "$VA_SHA" "2026-10-18" "valid-row-first"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$A" "$WRONG" "$VA" "$VA_SHA" "2026-10-18" "bad-row-second"
} > "$W/L_shared_valid_first.tsv"
run_case B1 "shared ledger, valid row FIRST then bad row (S05 shape)" \
  "$W/L_shared_valid_first.tsv" "$A" SAFE
# --- confound replication: bad row FIRST, valid row second ------------------
{
  printf "$HDR\n"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$A" "$WRONG" "$VA" "$VA_SHA" "2026-10-18" "bad-row-first"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$A" "$A_SHA" "$VA" "$VA_SHA" "2026-10-18" "valid-row-second"
} > "$W/L_shared_bad_first.tsv"
run_case B2 "shared ledger, bad row FIRST then valid row" \
  "$W/L_shared_bad_first.tsv" "$A" SAFE
# --- bad row first, no valid row at all (isolated bad) ----------------------
one_row "$W/L_only_bad.tsv" "$A" "$WRONG" "$VA" "$VA_SHA" "2026-10-18" "only-bad"
run_case B3 "ledger with ONLY the bad row" "$W/L_only_bad.tsv" "$A" NOT-SAFE

say ""
say "== summary =="
awk -F'\t' '{n++; if($2=="PASS")p++; else {f++; print "FAIL: "$1" want="$3" got="$4}} END{printf "total=%d pass=%d fail=%d\n", n, p, f+0}' "$RES"
