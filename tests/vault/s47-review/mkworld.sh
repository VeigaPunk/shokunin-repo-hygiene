#!/usr/bin/env bash
# S47 reviewer — independent fixture world for round-4 vault verification.
# Writes ONLY under $W (/tmp scratch). Never touches the real vault or the
# live ledger. Every ledger lives in its own file (one probe = one ledger)
# to avoid cross-probe masking (S55 v1 lesson).
set -euo pipefail
W="${1:?usage: mkworld.sh <world-dir>}"
rm -rf "$W"; mkdir -p "$W"

SRC="$W/src"; VLT="$W/vault"; LD="$W/ledgers"
mkdir -p "$SRC" "$VLT" "$LD"

sha() { sha256sum -- "$1" | cut -d' ' -f1; }
HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
mkled() { # mkled <file> <rows...>
  local f=$1; shift
  { printf '%s\n' "$HDR"; local r; for r in "$@"; do printf '%b\n' "$r"; done; } > "$f"
}

# ---- payload pairs ---------------------------------------------------------
pair() { # pair <name> -> files src/<n>.md vault/<n>.md
  local n=$1
  printf 'payload for %s\nline two\n' "$n" > "$SRC/$n.md"
  cp "$SRC/$n.md" "$VLT/$n.md"
}

pair matched;            M_S=$(sha "$SRC/matched.md");   M_V=$(sha "$VLT/matched.md")
pair vaulttamper;        VT_S=$(sha "$SRC/vaulttamper.md")
printf 'edited inside vault\n' >> "$VLT/vaulttamper.md"; VT_V_ROW=$VT_S
VT_V_NOW=$(sha "$VLT/vaulttamper.md")
pair sourcetamper;       ST_V=$(sha "$VLT/sourcetamper.md"); ST_S_ROW=$ST_V
printf 'source edited after export\n' >> "$SRC/sourcetamper.md"
pair subtle;             SU_S=$(sha "$SRC/subtle.md")
printf 'payload for subtle\nline two' > "$VLT/subtle.md"   # trailing newline dropped
SU_V=$(sha "$VLT/subtle.md")
pair absentvault;        AB_S=$(sha "$SRC/absentvault.md")
rm -f "$VLT/absentvault.md"
pair absentsource;       AS_V=$(sha "$VLT/absentsource.md")
AS_S_ROW=$AS_V
rm -f "$SRC/absentsource.md"                                # source absent, vault present
pair emptypair;          : > "$SRC/emptypair.md"; : > "$VLT/emptypair.md"
E_S=$(sha "$SRC/emptypair.md"); E_V=$(sha "$VLT/emptypair.md")
pair future;             FU_S=$(sha "$SRC/future.md")
cp "$SRC/future.md" "$VLT/future.md"
touch -d '2030-01-01 00:00:00' "$VLT/future.md"
pair crlfpair;           CR_S=$(sha "$SRC/crlfpair.md"); CR_V=$(sha "$VLT/crlfpair.md")

# symlink-to-real + loop + fifo
ln -sfn "$VLT/matched.md" "$W/symlink-ok"
ln -sfn "$W/loop-b" "$W/loop-a"; ln -sfn "$W/loop-a" "$W/loop-b"
FIFO="$W/fifo-vault"; [ -p "$FIFO" ] || mkfifo "$FIFO"

# mode-000 vault file (correct bytes behind the mode)
pair mode000; MOD_S=$(sha "$SRC/mode000.md")
cp "$SRC/mode000.md" "$VLT/mode000.md"; chmod 000 "$VLT/mode000.md"

# traversal: vault path escaping the vault root; source bytes == /etc/hostname
cp /etc/hostname "$SRC/traversal.md"
TR_S=$(sha "$SRC/traversal.md"); TR_V=$(sha /etc/hostname)

# secrets-shaped source (content must never be echoed)
printf 'SECRET_CANARY_S47=do-not-print-4f9a2c\n' > "$SRC/canary.env"
CAN_S=$(sha "$SRC/canary.env")
printf 'SECRET_CANARY_S47=do-not-print-4f9a2c\n' > "$VLT/canary.env"
CAN_V=$(sha "$VLT/canary.env")

# same-path row (source == vault path)
pair samepath;           SP=$(sha "$SRC/samepath.md")

# ---- ledgers (one per probe) ----------------------------------------------
mkled "$LD/L1.tsv"  "$SRC/matched.md\t$M_S\t$VLT/matched.md\t$M_V\t2026-10-18\tmatched"
mkled "$LD/L2.tsv"  "$SRC/vaulttamper.md\t$VT_S\t$VLT/vaulttamper.md\t$VT_V_ROW\t2026-10-18\tvault-tamper"
mkled "$LD/L3.tsv"  "$SRC/sourcetamper.md\t$ST_S_ROW\t$VLT/sourcetamper.md\t$ST_V\t2026-10-18\tsource-tamper"
mkled "$LD/L4.tsv"  "$SRC/absentvault.md\t$AB_S\t$VLT/absentvault.md\t$AB_S\t2026-10-18\tvault-absent"
mkled "$LD/L5.tsv"  "$SRC/absentsource.md\t$AS_S_ROW\t$VLT/absentsource.md\t$AS_V\t2026-10-18\tsource-absent"
mkled "$LD/L6.tsv"                                                    # header only
mkled "$LD/L7.tsv"  "$SRC/matched.md\t$M_S\t$VLT/matched.md\t0000000000000000000000000000000000000000000000000000000000000000\t2026-10-18\twrong-vault-hash"
mkled "$LD/L8.tsv"  "$SRC/matched.md\t\t$VLT/matched.md\t\t2026-10-18\tempty-hash-cols"
mkled "$LD/L8b.tsv" "$SRC/matched.md\t$M_S\t$VLT/matched.md\t\t2026-10-18\tempty-vault-hash"
mkled "$LD/L8c.tsv" "$SRC/matched.md\t\t$VLT/matched.md\t$M_V\t2026-10-18\tempty-source-hash"
mkled "$LD/L9.tsv"  "$SRC/subtle.md\t$SU_S\t$VLT/subtle.md\t$SU_S\t2026-10-18\tsubtle-newline"
mkled "$LD/L10.tsv" "$SRC/crlfpair.md\t$CR_S\t$VLT/crlfpair.md\t$CR_V\t2026-10-18\tcrlf-ok"
mkled "$LD/L12.tsv" "$SRC/matched.md\t$M_S\t$VLT/matched.md"          # 3-col malformed
mkled "$LD/L13.tsv" "$SRC/traversal.md\t$TR_S\t/etc/hostname\t$TR_V\t2026-10-18\ttraversal"
mkled "$LD/L14.tsv" "$SRC/canary.env\t$CAN_S\t$VLT/canary.env\t$CAN_V\t2026-10-18\tsecrets"
mkled "$LD/L15.tsv" "$SRC/matched.md\t$M_S\t$W\t$M_S\t2026-10-18\tvault-is-dir"
mkled "$LD/L17.tsv" "$SRC/samepath.md\t$SP\t$SRC/samepath.md\t$SP\t2026-10-18\tsame-path"
mkled "$LD/L18.tsv" "$SRC/future.md\t$FU_S\t$VLT/future.md\t$(sha "$VLT/future.md")\t2026-10-18\tfuture-mtime"
mkled "$LD/L19.tsv" "$SRC/emptypair.md\t$E_S\t$VLT/emptypair.md\t$E_V\t2026-10-18\tempty-pair"
mkled "$LD/L20.tsv" "$SRC/mode000.md\t$MOD_S\t$VLT/mode000.md\t$MOD_S\t2026-10-18\tmode000"
mkled "$LD/L21.tsv" "$SRC/matched.md\t$M_S\t$W/symlink-ok\t$M_V\t2026-10-18\tsymlink-ok"
mkled "$LD/L22.tsv" "$SRC/matched.md\t$M_S\t$W/loop-a\t$M_S\t2026-10-18\tsymlink-loop"
mkled "$LD/L23.tsv" "$SRC/matched.md\t$M_S\t$FIFO\t$M_S\t2026-10-18\tfifo"
# duplicate rows: first correct, second wrong (must not be poisoned by order)
mkled "$LD/L24.tsv" "$SRC/matched.md\t$M_S\t$VLT/matched.md\t$M_V\t2026-10-18\tdup-good" \
                    "$SRC/matched.md\t$M_S\t$VLT/matched.md\t0000000000000000000000000000000000000000000000000000000000000000\t2026-10-18\tdup-bad"
# duplicate rows: first wrong, second correct (matching row exists -> VERIFIED ok)
mkled "$LD/L25.tsv" "$SRC/matched.md\t$M_S\t$VLT/matched.md\t0000000000000000000000000000000000000000000000000000000000000000\t2026-10-18\tdup-bad" \
                    "$SRC/matched.md\t$M_S\t$VLT/matched.md\t$M_V\t2026-10-18\tdup-good"
# CRLF ledger variant with correct rows (parse tolerance)
sed 's/$/\r/' "$LD/L10.tsv" > "$LD/L26.tsv"
# missing ledger file path (runner points at nonexistent file)
# (no file created on purpose: L27)

# ---- expectations ----------------------------------------------------------
cat > "$W/expected.tsv" <<EOF
L1	V	matched
L2	N	vault-tamper
L3	N	source-tamper
L4	N	vault-absent
L5	N	source-absent
L6	N	header-only
L7	N	wrong-vault-hash
L8	N	empty-hash-cols
L8b	N	empty-vault-hash
L8c	N	empty-source-hash
L9	N	subtle-newline
L10	V	crlf-ok
L12	N	malformed-3col
L13	N	traversal
L14	R	secrets-refusal
L15	N	vault-is-dir
L17	I	same-path
L18	V	future-mtime
L19	V	empty-pair
L20	N	mode000
L21	I	symlink-ok
L22	N	symlink-loop
L23	N	fifo
L24	I	dup-good-first
L25	I	dup-good-second
L26	I	crlf-ledger
L27	N	ledger-missing
EOF
# targets per probe
cat > "$W/targets.tsv" <<EOF
L1	$SRC/matched.md
L2	$SRC/vaulttamper.md
L3	$SRC/sourcetamper.md
L4	$SRC/absentvault.md
L5	$SRC/absentsource.md
L6	$SRC/matched.md
L7	$SRC/matched.md
L8	$SRC/matched.md
L8b	$SRC/matched.md
L8c	$SRC/matched.md
L9	$SRC/subtle.md
L10	$SRC/crlfpair.md
L12	$SRC/matched.md
L13	$SRC/traversal.md
L14	$SRC/canary.env
L15	$SRC/matched.md
L17	$SRC/samepath.md
L18	$SRC/future.md
L19	$SRC/emptypair.md
L20	$SRC/mode000.md
L21	$SRC/matched.md
L22	$SRC/matched.md
L23	$SRC/matched.md
L24	$SRC/matched.md
L25	$SRC/matched.md
L26	$SRC/crlfpair.md
L27	$SRC/matched.md
EOF
printf 'WORLD_READY %s\n' "$W"

# ---- late additions (v3.1): spaces, CRLF-truncated, reason fidelity -------
pair "space pair"
printf 'space payload\n' > "$SRC/meeting notes 2026-10.md"
cp "$SRC/meeting notes 2026-10.md" "$VLT/Meeting Notes 2026-10.md"
SPC_S=$(sha "$SRC/meeting notes 2026-10.md"); SPC_V=$(sha "$VLT/Meeting Notes 2026-10.md")
mkled "$LD/L29.tsv" "$SRC/meeting notes 2026-10.md\t$SPC_S\t$VLT/Meeting Notes 2026-10.md\t$SPC_V\t2026-10-18\tspace-names"
# CRLF truncated row: last field is vault_sha256 and carries the CR
{ printf '%s\n' "$HDR"
  printf '%s\t%s\t%s\t%s' "$SRC/crlfpair.md" "$CR_S" "$VLT/crlfpair.md" "$CR_V"
} | sed 's/$/\r/' > "$LD/L30.tsv"
printf 'L29\tV\tspace-names\n' >> "$W/expected.tsv"
printf 'L30\tN\tcrlf-truncated\n' >> "$W/expected.tsv"
printf 'L29\t%s/meeting notes 2026-10.md\n' "$SRC" >> "$W/targets.tsv"
printf 'L30\t%s/crlfpair.md\n' "$SRC" >> "$W/targets.tsv"
echo "WORLD_EXTENDED"

# ---- v3.2 additions: 5-col tolerated row (L31), dir-pair (L32) ------------
{ printf '%s\n' "$HDR"
  printf '%s\t%s\t%s\t%s\t2026-10-18' "$SRC/matched.md" "$M_S" "$VLT/matched.md" "$M_V"
} > "$LD/L31.tsv"
# dir pair: identical trees, dir digest per runner-39 convention
mkdir -p "$SRC/dirpair" "$VLT/dirpair"
printf 'one\n' > "$SRC/dirpair/one.txt"; cp "$SRC/dirpair/one.txt" "$VLT/dirpair/one.txt"
printf 'two\n' > "$SRC/dirpair/two.txt"; cp "$SRC/dirpair/two.txt" "$VLT/dirpair/two.txt"
ddg() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }
DIG_S=$(ddg "$SRC/dirpair"); DIG_V=$(ddg "$VLT/dirpair")
mkled "$LD/L32.tsv" "$SRC/dirpair\t$DIG_S\t$VLT/dirpair\t$DIG_V\t2026-10-18\tdir-pair"
printf 'L31\tV\t5col-row\n' >> "$W/expected.tsv"
printf 'L32\tI\tdir-pair\n' >> "$W/expected.tsv"
printf 'L31\t%s/matched.md\n' "$SRC" >> "$W/targets.tsv"
printf 'L32\t%s/dirpair\n' "$SRC" >> "$W/targets.tsv"
echo WORLD_V32

# ---- v3.3: separate 5-col (newline-terminated) from unterminated rows ----
# L31 redo: 5-col row WITH trailing newline (exported_at absent)
{ printf '%s\n' "$HDR"
  printf '%s\t%s\t%s\t%s\t2026-10-18\n' "$SRC/matched.md" "$M_S" "$VLT/matched.md" "$M_V"
} > "$LD/L31.tsv"
# L33: 6-col row WITHOUT trailing newline
{ printf '%s\n' "$HDR"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tunterminated' "$SRC/matched.md" "$M_S" "$VLT/matched.md" "$M_V"
} > "$LD/L33.tsv"
printf 'L33\tV\tno-trailing-newline\n' >> "$W/expected.tsv"
printf 'L33\t%s/matched.md\n' "$SRC" >> "$W/targets.tsv"
echo WORLD_V33
