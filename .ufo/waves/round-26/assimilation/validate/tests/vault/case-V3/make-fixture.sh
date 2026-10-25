#!/usr/bin/env bash
# case-V3 fixture builder — souji-shokunin round 4, seat S11.
#
# Spec case V3: the source file's content differs from the ledger row's
# source_sha256. The vault copy still matches the row exactly, so the ONLY
# failing conjunct is the source-side hash. Expected verdict:
# NOT-VERIFIED(source-hash).
#
# Self-contained: builds a fake vault, a source tree, and its own test ledger
# under the fixture root. Never reads or writes the live ledger
# (corpus/knowledge/obsidian-ledger.tsv), the real vault
# (/home/vgpnk/Documents/shokoknowledge), or any sibling repo.
#
# Discriminator: the vault file's sha256 equals the row's vault_sha256, and
# the row's source_sha256 is the true digest of the export-time bytes; the
# current source file carries different bytes. So the case catches
#   (a) vault-side-only verification reporting VERIFIED/SAFE,
#   (b) class collapse to NOT-SAFE(none) instead of NOT-VERIFIED(source-hash),
#   (c) a tool that never re-reads the source and trusts the vault copy.
# The third target (matched control) must be VERIFIED, so the case cannot
# pass by always answering source-hash.
#
# Builds under --out (default: fresh mktemp -d):
#   source/src/edited-notes.md   primary target: edited after export
#   source/src/subtle-notes.md   one-byte edit (dropped trailing newline)
#   source/src/matched-notes.md  control: byte-identical to its vault copy
#   vault/edited-notes.md        export-time bytes, mode 0444
#   vault/subtle-notes.md        export-time bytes, mode 0444
#   vault/matched-notes.md       byte-identical to the source, mode 0444
#   ledger.tsv                   header + exactly 3 rows carrying the
#                                export-time digests (source side stale by
#                                construction for the two negatives)
#   expected.json                the case-dir template, @FIXTURE_ROOT@
#                                substituted
# and (only with --ledger FILE) a copy of ledger.tsv at FILE.
#
# Contract (mirrors the V4/V5 house shapes):
#   normal stdout: line 1 = single-line JSON {case,root,ledger,targets,expect};
#                  line 2 = FIXTURE_READY case-V3 <ROOT>;
#                  then KEY=VALUE lines.
#   --quiet stdout: FIXTURE_READY line + KEY=VALUE lines only.
#   stderr: key=value facts.
#   exit codes: 0 built, 1 build/assertion failure, 2 usage.
set -euo pipefail
export LC_ALL=C

case_name=case-V3
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
self=$(basename -- "$0")

# --- content sha256 constants ----------------------------------------------
# Source of truth is the content_*() functions below; --print-hashes prints
# the computed table. A mismatch is a build failure, never a warning.
SHA_EXPORTED="655cb8c2ea693fbe500b6c32a1f8cc5ff5f5ba0900ccb80606a0714f7be4aea8"      # 289 B
SHA_EDITED="bac6faf0d62df655f6700f5f530a76801c150322a8962dce4bd5785506abd845"        # 276 B
SHA_SUBTLE_EXPORT="e6a4c2fb6142dd29eaf544690593ff24f68055ccc06f56a8271b45e147d6005e" # 289 B
SHA_SUBTLE_SOURCE="45d91bb27469d389946266e6793fe7d492751110ad9dfc5d3cd51c9b2a9509e5" # 288 B
SHA_MATCHED="9f461f329c6568e871180cab3e05434ae9e7d01abeb094b96fcba1a65f529f44"       # 178 B
BYTES_EXPORTED=289
BYTES_EDITED=276
BYTES_SUBTLE_EXPORT=289
BYTES_SUBTLE_SOURCE=288
BYTES_MATCHED=178

# --- fixture file contents (exact bytes, LF, trailing newline) -------------
content_exported() {
  cat <<'EOF'
# Edited source notes (V3 source-hash mismatch)

Exported to the vault on 2026-10-18 with exactly these bytes; the ledger
row records this digest on both sides. The source copy was edited after
the export.

case-V3: the vault side still matches the row; only the source-side
sha256 fails.
EOF
}

content_edited() {
  cat <<'EOF'
# Edited source notes (V3 source-hash mismatch)

Exported to the vault on 2026-10-18, then edited in place: this revision
no longer matches the row's source_sha256, while the vault copy still
carries the exported bytes.

case-V3: the source-side hash is the failing conjunct.
EOF
}

content_subtle_export() {
  cat <<'EOF'
# Subtle edit notes (V3 source-hash, one byte)

Exported to the vault with this exact content, trailing newline included.
The source copy differs from the row's source_sha256 by exactly one byte:
the final newline is gone.

case-V3 subtle: byte-exact hashing must catch a one-byte change.
EOF
}

content_subtle_source() {
  # Export bytes minus the final newline: a one-byte edit.
  printf '%s' "$(content_subtle_export)"
}

content_matched() {
  cat <<'EOF'
# Matched control notes (V3)

Control pair for case-V3: the source copy and the vault copy are
byte-identical and both match the ledger row.

case-V3 control: expected VERIFIED.
EOF
}

sha_of() { sha256sum | cut -d' ' -f1; }
bytes_of() { wc -c | tr -d ' '; }

usage() {
  cat <<USAGE
usage: make-fixture.sh [--out DIR] [--ledger FILE] [--quiet]
                       [--print-ledger] [--print-hashes]

  --out DIR        fixture root (default: fresh mktemp -d). Re-running on an
                   existing case-V3 root (marker .case-V3-fixture) rebuilds
                   it; any other non-empty directory is refused.
  --ledger FILE    additionally write the test ledger to FILE (the canonical
                   ledger is always <ROOT>/ledger.tsv)
  --quiet          print only FIXTURE_READY + KEY=VALUE lines
  --print-ledger   print the concrete ledger rows (no header) and exit
  --print-hashes   print the content digest table and exit

stdout (default): line 1 single-line JSON {case,root,ledger,targets,expect};
                  then FIXTURE_READY case-V3 <ROOT>; then LEDGER=, TARGET=,
                  TARGET_SUBTLE=, TARGET_MATCHED=, VAULT_EDITED=,
                  VAULT_SUBTLE=, VAULT_MATCHED=, SOURCE_SHA256= (row value),
                  SOURCE_SHA256_ACTUAL= (current source), EXPECT= lines.
stderr:           key=value facts (fixture_root=, ledger=, ...).
Exit: 0 built (also for --print-*); 1 build or assertion failure; 2 usage.
USAGE
}

die() { printf '%s: %s\n' "$self" "$*" >&2; exit 1; }
usage_die() { printf '%s: %s\n' "$self" "$*" >&2; usage >&2; exit 2; }

expect_hash() {
  local id="$1" const="$2" computed="$3"
  if [ "$const" != "$computed" ]; then
    printf '%s: sha256 mismatch for %s\n  constant: %s\n  computed: %s\n  update SHA_* in make-fixture.sh and expected.json (--print-hashes prints the table)\n' \
      "$self" "$id" "$const" "$computed" >&2
    return 1
  fi
}

expect_bytes() {
  local id="$1" const="$2" computed="$3"
  if [ "$const" != "$computed" ]; then
    printf '%s: byte-count mismatch for %s: constant=%s computed=%s\n' \
      "$self" "$id" "$const" "$computed" >&2
    return 1
  fi
}

out=""
ledger_copy=""
quiet=0
do_print_ledger=0
do_print_hashes=0

while [ $# -gt 0 ]; do
  case "$1" in
    --out) [ $# -ge 2 ] || usage_die "--out requires a directory"; out=$2; shift 2 ;;
    --ledger) [ $# -ge 2 ] || usage_die "--ledger requires a file"; ledger_copy=$2; shift 2 ;;
    --quiet) quiet=1; shift ;;
    --print-ledger) do_print_ledger=1; shift ;;
    --print-hashes) do_print_hashes=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) usage_die "unknown option: $1" ;;
    *) [ -z "$out" ] || usage_die "unexpected extra argument: $1"; out=$1; shift ;;
  esac
done

if [ "$do_print_hashes" = 1 ]; then
  printf 'exported\t%s\t%s\n' "$(content_exported | sha_of)" "$(content_exported | bytes_of)"
  printf 'edited\t%s\t%s\n' "$(content_edited | sha_of)" "$(content_edited | bytes_of)"
  printf 'subtle-export\t%s\t%s\n' "$(content_subtle_export | sha_of)" "$(content_subtle_export | bytes_of)"
  printf 'subtle-source\t%s\t%s\n' "$(content_subtle_source | sha_of)" "$(content_subtle_source | bytes_of)"
  printf 'matched\t%s\t%s\n' "$(content_matched | sha_of)" "$(content_matched | bytes_of)"
  exit 0
fi

ledger_rows() { # $1 root
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$1/source/src/edited-notes.md" "$SHA_EXPORTED" \
    "$1/vault/edited-notes.md" "$SHA_EXPORTED" \
    "2026-10-18" "case-V3 source-hash-mismatch"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$1/source/src/subtle-notes.md" "$SHA_SUBTLE_EXPORT" \
    "$1/vault/subtle-notes.md" "$SHA_SUBTLE_EXPORT" \
    "2026-10-18" "case-V3 source-hash-subtle"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$1/source/src/matched-notes.md" "$SHA_MATCHED" \
    "$1/vault/matched-notes.md" "$SHA_MATCHED" \
    "2026-10-18" "case-V3 control matched"
}

if [ "$do_print_ledger" = 1 ]; then
  [ -n "$out" ] || usage_die "--print-ledger needs --out DIR"
  ledger_rows "$(cd -- "$out" 2>/dev/null && pwd -P || printf '%s' "$out")"
  exit 0
fi

command -v sha256sum >/dev/null 2>&1 || die "sha256sum is required"

# --- content assertions (before anything is built) --------------------------
expect_hash exported "$SHA_EXPORTED" "$(content_exported | sha_of)" || exit 1
expect_hash edited "$SHA_EDITED" "$(content_edited | sha_of)" || exit 1
expect_hash subtle-export "$SHA_SUBTLE_EXPORT" "$(content_subtle_export | sha_of)" || exit 1
expect_hash subtle-source "$SHA_SUBTLE_SOURCE" "$(content_subtle_source | sha_of)" || exit 1
expect_hash matched "$SHA_MATCHED" "$(content_matched | sha_of)" || exit 1
expect_bytes exported "$BYTES_EXPORTED" "$(content_exported | bytes_of)" || exit 1
expect_bytes edited "$BYTES_EDITED" "$(content_edited | bytes_of)" || exit 1
expect_bytes subtle-export "$BYTES_SUBTLE_EXPORT" "$(content_subtle_export | bytes_of)" || exit 1
expect_bytes subtle-source "$BYTES_SUBTLE_SOURCE" "$(content_subtle_source | bytes_of)" || exit 1
expect_bytes matched "$BYTES_MATCHED" "$(content_matched | bytes_of)" || exit 1

if [ -z "$out" ]; then
  tmp_base=${SOUJI_FIXTURE_TMPDIR:-${TMPDIR:-/tmp}}
  out=$(mktemp -d "${tmp_base%/}/souji-fixture-case-V3.XXXXXX")
else
  mkdir -p -- "$out" || die "cannot create --out directory: $out"
fi
out=$(cd -- "$out" && pwd -P) || die "cannot enter --out directory"

case "$out" in
  *'"'*|*'\'*|*'&'*|*'|'*) die "fixture path contains a JSON/sed-unsafe character: $out" ;;
esac
[ "$out" != "$here" ] || die "refusing to build into the case directory itself"

if [ -n "$(ls -A -- "$out")" ]; then
  if [ -e "$out/.case-V3-fixture" ]; then
    rm -rf -- "$out"
    mkdir -p -- "$out"
  else
    die "refusing non-empty directory without .case-V3-fixture marker: $out"
  fi
fi

printf 'case-V3 fixture\n' > "$out/.case-V3-fixture"

src_dir="$out/source/src"
src_edited="$src_dir/edited-notes.md"
src_subtle="$src_dir/subtle-notes.md"
src_matched="$src_dir/matched-notes.md"
vault_edited="$out/vault/edited-notes.md"
vault_subtle="$out/vault/subtle-notes.md"
vault_matched="$out/vault/matched-notes.md"
ledger="$out/ledger.tsv"

mkdir -p -- "$src_dir" "$out/vault"

content_exported > "$vault_edited"
content_edited > "$src_edited"
content_subtle_export > "$vault_subtle"
content_subtle_source > "$src_subtle"
content_matched > "$vault_matched"
content_matched > "$src_matched"
chmod 0444 -- "$vault_edited" "$vault_subtle" "$vault_matched"

# Offline repo context so the fixture root behaves like a real lane repo.
if [ ! -d "$out/.git" ] && command -v git >/dev/null 2>&1; then
  export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_TERMINAL_PROMPT=0
  git -C "$out" init -q -b master 2>/dev/null || git -C "$out" init -q
fi

{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  ledger_rows "$out"
} > "$ledger"

if [ -n "$ledger_copy" ]; then
  mkdir -p -- "$(dirname -- "$ledger_copy")"
  cp -f -- "$ledger" "$ledger_copy"
fi

# --- assertions (build fails loudly, never warns) ---------------------------
verify_file() { # path want-sha want-bytes
  local path="$1" want="$2" wantb="$3" got gotb
  got=$(sha256sum -- "$path" | cut -d' ' -f1)
  gotb=$(wc -c < "$path" | tr -d ' ')
  [ "$got" = "$want" ] || die "built file does not match declared sha256: $path (declared=$want computed=$got)"
  [ "$gotb" = "$wantb" ] || die "built file does not match declared byte count: $path (declared=$wantb computed=$gotb)"
}
verify_file "$vault_edited" "$SHA_EXPORTED" "$BYTES_EXPORTED"
verify_file "$src_edited" "$SHA_EDITED" "$BYTES_EDITED"
verify_file "$vault_subtle" "$SHA_SUBTLE_EXPORT" "$BYTES_SUBTLE_EXPORT"
verify_file "$src_subtle" "$SHA_SUBTLE_SOURCE" "$BYTES_SUBTLE_SOURCE"
verify_file "$vault_matched" "$SHA_MATCHED" "$BYTES_MATCHED"
verify_file "$src_matched" "$SHA_MATCHED" "$BYTES_MATCHED"

cmp -s -- "$src_edited" "$vault_edited" && die "primary source must differ from its vault copy"
cmp -s -- "$src_subtle" "$vault_subtle" && die "subtle source must differ from its vault copy"
cmp -s -- "$src_matched" "$vault_matched" || die "control source and vault copies must be byte-identical"

{
  IFS= read -r hdr
  IFS= read -r row1
  IFS= read -r row2
  IFS= read -r row3
  rest=$(cat)
} < "$ledger"
[ "$hdr" = "$(printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote')" ] \
  || die "ledger header mismatch"
[ -z "$rest" ] || die "ledger must hold exactly 3 data rows"
[ -n "$row1" ] && [ -n "$row2" ] && [ -n "$row3" ] || die "ledger rows missing"
IFS=$'\t' read -r r1_sp r1_ss r1_vp r1_vs _r1 <<< "$row1"
IFS=$'\t' read -r r2_sp r2_ss r2_vp r2_vs _r2 <<< "$row2"
IFS=$'\t' read -r r3_sp r3_ss r3_vp r3_vs _r3 <<< "$row3"
[ "$r1_sp" = "$src_edited" ] && [ "$r1_ss" = "$SHA_EXPORTED" ] \
  && [ "$r1_vp" = "$vault_edited" ] && [ "$r1_vs" = "$SHA_EXPORTED" ] \
  || die "row 1 (primary) fields mismatch"
[ "$r2_sp" = "$src_subtle" ] && [ "$r2_ss" = "$SHA_SUBTLE_EXPORT" ] \
  && [ "$r2_vp" = "$vault_subtle" ] && [ "$r2_vs" = "$SHA_SUBTLE_EXPORT" ] \
  || die "row 2 (subtle) fields mismatch"
[ "$r3_sp" = "$src_matched" ] && [ "$r3_ss" = "$SHA_MATCHED" ] \
  && [ "$r3_vp" = "$vault_matched" ] && [ "$r3_vs" = "$SHA_MATCHED" ] \
  || die "row 3 (control) fields mismatch"

# The two negatives fail ONLY on the source-side hash: the row's vault_sha256
# must equal the current vault file digest, and the row's source_sha256 must
# differ from the current source digest.
[ "$(sha256sum -- "$vault_edited" | cut -d' ' -f1)" = "$r1_vs" ] || die "primary vault digest must match the row"
[ "$(sha256sum -- "$src_edited" | cut -d' ' -f1)" != "$r1_ss" ] || die "primary source digest must differ from the row"
[ "$(sha256sum -- "$vault_subtle" | cut -d' ' -f1)" = "$r2_vs" ] || die "subtle vault digest must match the row"
[ "$(sha256sum -- "$src_subtle" | cut -d' ' -f1)" != "$r2_ss" ] || die "subtle source digest must differ from the row"

sed "s|@FIXTURE_ROOT@|$out|g" "$here/expected.json" > "$out/expected.json"
command -v python3 >/dev/null 2>&1 || die "python3 required for JSON validation"
python3 - "$out/expected.json" <<'PY' || die "substituted expected.json is not valid JSON"
import json, sys
json.load(open(sys.argv[1]))
PY

src_edited_sha=$(sha256sum -- "$src_edited" | cut -d' ' -f1)
src_subtle_sha=$(sha256sum -- "$src_subtle" | cut -d' ' -f1)

json=$(printf '{"case":"%s","schema":"souji-vault-fixture/1","root":"%s","ledger":"%s","targets":["%s","%s","%s"],"expect":[{"path":"%s","vault_path":"%s","verdict":"NOT-VERIFIED","reason":"source-hash","receipt":null,"verdict_string":"NOT-VERIFIED(source-hash)"},{"path":"%s","vault_path":"%s","verdict":"NOT-VERIFIED","reason":"source-hash","receipt":null,"verdict_string":"NOT-VERIFIED(source-hash)"},{"path":"%s","vault_path":"%s","verdict":"VERIFIED","reason":null,"receipt":"moved-to-obsidian","verdict_string":"VERIFIED"}]}' \
  "$case_name" "$out" "$ledger" "$src_edited" "$src_subtle" "$src_matched" \
  "$src_edited" "$vault_edited" "$src_subtle" "$vault_subtle" "$src_matched" "$vault_matched")

if [ "$quiet" = 1 ]; then
  printf 'FIXTURE_READY %s %s\n' "$case_name" "$out"
else
  printf '%s\n' "$json"
  printf 'FIXTURE_READY %s %s\n' "$case_name" "$out"
fi
printf 'LEDGER=%s\n' "$ledger"
printf 'TARGET=%s\n' "$src_edited"
printf 'TARGET_SUBTLE=%s\n' "$src_subtle"
printf 'TARGET_MATCHED=%s\n' "$src_matched"
printf 'VAULT_EDITED=%s\n' "$vault_edited"
printf 'VAULT_SUBTLE=%s\n' "$vault_subtle"
printf 'VAULT_MATCHED=%s\n' "$vault_matched"
printf 'SOURCE_SHA256=%s\n' "$SHA_EXPORTED"
printf 'SOURCE_SHA256_ACTUAL=%s\n' "$src_edited_sha"
printf 'SUBTLE_SHA256=%s\n' "$SHA_SUBTLE_EXPORT"
printf 'SUBTLE_SHA256_ACTUAL=%s\n' "$src_subtle_sha"
printf 'EXPECT=NOT-VERIFIED(source-hash)\n'
[ -z "$ledger_copy" ] || printf 'LEDGER_COPY=%s\n' "$ledger_copy"

{
  printf 'fixture_root=%s\n' "$out"
  printf 'case=%s\n' "$case_name"
  printf 'ledger=%s\n' "$ledger"
  printf 'primary_source=%s\n' "$src_edited"
  printf 'primary_source_sha256=%s\n' "$src_edited_sha"
  printf 'primary_row_source_sha256=%s\n' "$SHA_EXPORTED"
  printf 'primary_vault=%s\n' "$vault_edited"
  printf 'primary_vault_sha256=%s\n' "$SHA_EXPORTED"
  printf 'subtle_source=%s\n' "$src_subtle"
  printf 'subtle_source_sha256=%s\n' "$src_subtle_sha"
  printf 'subtle_row_source_sha256=%s\n' "$SHA_SUBTLE_EXPORT"
  printf 'control_source=%s\n' "$src_matched"
  printf 'control_vault=%s\n' "$vault_matched"
  printf 'expect_primary=NOT-VERIFIED(source-hash)\n'
  printf 'expect_subtle=NOT-VERIFIED(source-hash)\n'
  printf 'expect_control=VERIFIED\n'
  printf 'expected_json=%s\n' "$out/expected.json"
} >&2
