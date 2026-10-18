#!/usr/bin/env bash
# tests/vault/vadv-49/make-fixtures.sh — seat S49 (adversarial, round 4) fixtures.
#
# Builds fixture trees + test ledgers for the three assigned attacks against
# the round-4 vault verifiers (tools/souji-vault-verify.impl-*.sh):
#   (a) ledger row whose source_path is a symlink to the vault file
#   (b) uppercase hex sha256 in the ledger
#   (c) ledger TSV with a comment line starting '#'
#
# Everything is built under --out (default tests/vault/vadv-49/fixture) and
# the ledgers land in tests/vault/vadv-49/. The live ledger
# corpus/knowledge/obsidian-ledger.tsv and the real vault
# /home/vgpnk/Documents/shokoknowledge are never touched.
set -euo pipefail
export LC_ALL=C
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
OUT="$HERE/fixture"
while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT="${2:?--out needs a value}"; shift 2 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) printf 'usage: %s [--out DIR]\n' "$0" >&2; exit 2 ;;
  esac
done
rm -rf -- "$OUT"; mkdir -p -- "$OUT"
sha_of() { sha256sum -- "$1" | cut -d' ' -f1; }
hdr() { printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'; }
row() { printf '%s\t%s\t%s\t%s\t2026-10-18\t%s\n' "$1" "$2" "$3" "$4" "$5"; }
repogit() { git -C "$1" init -q 2>/dev/null || true; }
up() { printf '%s' "$1" | tr 'a-f' 'A-F'; }

PAYLOAD='vadv-49 alpha payload'
WRONG='vadv-49 other payload'

# ---- control: plain pair, all four conjuncts match -> VERIFIED ------------
C="$OUT/control"; mkdir -p "$C/source" "$C/vault"
printf '%s\n' "$PAYLOAD" > "$C/source/alpha.txt"
printf '%s\n' "$PAYLOAD" > "$C/vault/alpha.txt"
repogit "$C"
PSHA=$(sha_of "$C/source/alpha.txt")
hdr > "$HERE/ledger-control.tsv"
row "$C/source/alpha.txt" "$PSHA" "$C/vault/alpha.txt" "$PSHA" control >> "$HERE/ledger-control.tsv"

# ---- attack a: source_path is a symlink to the vault file ----------------
# a1: the row's source_path IS the symlink; the symlink target IS the vault
#     copy. A receipt here would self-certify (source == vault's other name).
#     Defensive: NOT-VERIFIED.
C="$OUT/a1"; mkdir -p "$C/source" "$C/vault"
printf '%s\n' "$PAYLOAD" > "$C/vault/alpha.txt"
ln -s ../vault/alpha.txt "$C/source/link.txt"
repogit "$C"
hdr > "$HERE/ledger-a1.tsv"
row "$C/source/link.txt" "$PSHA" "$C/vault/alpha.txt" "$PSHA" a1-symlink-source >> "$HERE/ledger-a1.tsv"

# a2: the row's source_path is a symlink to a decoy OUTSIDE the vault (same
#     bytes). Defensive: NOT-VERIFIED (symlinked source must not receive a
#     preservation receipt).
C="$OUT/a2"; mkdir -p "$C/source" "$C/vault" "$C/elsewhere"
printf '%s\n' "$PAYLOAD" > "$C/vault/alpha.txt"
printf '%s\n' "$PAYLOAD" > "$C/elsewhere/decoy.txt"
ln -s ../elsewhere/decoy.txt "$C/source/link.txt"
repogit "$C"
hdr > "$HERE/ledger-a2.tsv"
row "$C/source/link.txt" "$PSHA" "$C/vault/alpha.txt" "$PSHA" a2-symlink-decoy >> "$HERE/ledger-a2.tsv"

# a3: canonicalization leak — invoke the tool on the symlink, but the ledger
#     row's source_path is the symlink's canonical target (a self-move row:
#     source == vault_path). Defensive: NOT-VERIFIED.
hdr > "$HERE/ledger-a3.tsv"
row "$OUT/a1/vault/alpha.txt" "$PSHA" "$OUT/a1/vault/alpha.txt" "$PSHA" a3-canonical-leak >> "$HERE/ledger-a3.tsv"

# a4: mirror attack — vault_path is a symlink back to the source file. A
#     VERIFIED here is a data-loss trap: removing the source leaves a
#     dangling vault copy. Defensive: NOT-VERIFIED.
C="$OUT/a4"; mkdir -p "$C/source" "$C/vault"
printf '%s\n' "$PAYLOAD" > "$C/source/alpha.txt"
ln -s ../source/alpha.txt "$C/vault/copy.txt"
repogit "$C"
hdr > "$HERE/ledger-a4.tsv"
row "$C/source/alpha.txt" "$PSHA" "$C/vault/copy.txt" "$PSHA" a4-circular-vault >> "$HERE/ledger-a4.tsv"

# a5: the purest self-certification — no symlink at all: the row's source_path
#     and vault_path are the SAME path. A VERIFIED here certifies a phantom
#     move (the vault "copy" is the artifact itself). Defensive: NOT-VERIFIED.
C="$OUT/a5"; mkdir -p "$C/source"
printf '%s\n' "$PAYLOAD" > "$C/source/self.txt"
repogit "$C"
ASHA=$(sha_of "$C/source/self.txt")
hdr > "$HERE/ledger-a5.tsv"
row "$C/source/self.txt" "$ASHA" "$C/source/self.txt" "$ASHA" a5-self-row >> "$HERE/ledger-a5.tsv"

# ---- attack b: uppercase hex sha256 --------------------------------------
C="$OUT/b"; mkdir -p "$C/source" "$C/vault"
printf '%s\n' "$PAYLOAD" > "$C/source/alpha.txt"
printf '%s\n' "$PAYLOAD" > "$C/vault/alpha.txt"
repogit "$C"
PSHA=$(sha_of "$C/source/alpha.txt"); VSHA=$(sha_of "$C/vault/alpha.txt")
WSHA=$(printf '%s\n' "$WRONG" | sha256sum | cut -d' ' -f1)
hdr > "$HERE/ledger-b1.tsv"; row "$C/source/alpha.txt" "$(up "$PSHA")" "$C/vault/alpha.txt" "$(up "$VSHA")" b1-upper-match >> "$HERE/ledger-b1.tsv"
hdr > "$HERE/ledger-b2.tsv"; row "$C/source/alpha.txt" "$(up "$WSHA")" "$C/vault/alpha.txt" "$VSHA" b2-upper-wrong >> "$HERE/ledger-b2.tsv"
hdr > "$HERE/ledger-b3.tsv"; row "$C/source/alpha.txt" "$PSHA" "$C/vault/alpha.txt" "$(up "$VSHA")" b3-upper-vault >> "$HERE/ledger-b3.tsv"
hdr > "$HERE/ledger-b4.tsv"; row "$C/source/alpha.txt" "$PSHA" "$C/vault/alpha.txt" "$(up "$WSHA")" b4-upper-vault-wrong >> "$HERE/ledger-b4.tsv"

# ---- attack c: '#' comment lines ------------------------------------------
C="$OUT/c"; mkdir -p "$C/source" "$C/vault"
printf '%s\n' "$PAYLOAD" > "$C/source/alpha.txt"
printf '%s\n' "$PAYLOAD" > "$C/source/#weird.txt"
printf '%s\n' "$PAYLOAD" > "$C/vault/alpha.txt"
repogit "$C"
PSHA=$(sha_of "$C/source/alpha.txt"); VSHA=$(sha_of "$C/vault/alpha.txt")
hdr > "$HERE/ledger-c1.tsv"; printf '# vadv-49 comment line between header and row\n' >> "$HERE/ledger-c1.tsv"; row "$C/source/alpha.txt" "$PSHA" "$C/vault/alpha.txt" "$VSHA" c1-comment-then-row >> "$HERE/ledger-c1.tsv"
hdr > "$HERE/ledger-c2.tsv"; printf '#%s\t%s\t%s\t%s\t2026-10-18\tc2-commented-out-row\n' "$C/source/alpha.txt" "$PSHA" "$C/vault/alpha.txt" "$VSHA" >> "$HERE/ledger-c2.tsv"
{ printf '# lead comment before header\n'; hdr; row "$C/source/alpha.txt" "$PSHA" "$C/vault/alpha.txt" "$VSHA" c3-comment-before-header; } > "$HERE/ledger-c3.tsv"
hdr > "$HERE/ledger-c4.tsv"; printf '   # indented comment line\n' >> "$HERE/ledger-c4.tsv"; row "$C/source/alpha.txt" "$PSHA" "$C/vault/alpha.txt" "$VSHA" c4-indented-comment >> "$HERE/ledger-c4.tsv"
hdr > "$HERE/ledger-c5.tsv"; row "$C/source/#weird.txt" "$PSHA" "$C/vault/alpha.txt" "$VSHA" c5-hash-in-path >> "$HERE/ledger-c5.tsv"

printf 'FIXTURES_READY %s\n' "$OUT"
