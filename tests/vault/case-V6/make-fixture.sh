#!/usr/bin/env bash
# tests/vault/case-V6/make-fixture.sh — builder for case-V6 (round 4, seat S14).
#
# Case: ledger TSV with CRLF line endings + a valid row. Expected: the row
# still parses -> VERIFIED (explicit CRLF-handling verdict). Full contract in
# expected.json (schema souji-vault-fixture/1).
#
# Modes:
#   default (no --out): the CASE DIRECTORY itself is the fixture root —
#     materializes src/, vault/ and the ledgers in place (all gitignored).
#     This is the mode runner-28's probes[] loader expects (it resolves
#     probes[].ledger relative to the case dir after running the builder
#     without --out); it never overwrites the tracked expected.json template.
#   --out DIR: builds a self-contained fixture root under DIR (default mode
#     for runner-26/29, which pass --out and resolve probes[] against it).
#
# Builds (in <ROOT>):
#   src/payload.md            source-side payload
#   vault/payload.md          byte-identical vault-side copy (mode 0444)
#   ledger-crlf.tsv           header + valid row, CRLF end-to-end   <- primary
#   ledger-lf-control.tsv     same row, LF endings (control)
#   ledger-crlf-truncated.tsv CRLF row truncated after the 4 hash columns
#   ledger.tsv                copy of the primary (runner-28 first-choice name)
#   .case-V6-fixture          marker (only in --out mode)
#   expected.json             contract with @FIXTURE_ROOT@ substituted
#                             (only in --out mode; the template is tracked)
# and (re)writes --ledger (default tests/vault/ledger-V6.tsv) as a byte copy
# of the primary CRLF ledger (atomic rename).
#
# Writes ONLY: <ROOT>/** and <LEDGER> (plus, in default mode, the case dir
# itself). Never touches the live ledger corpus/knowledge/obsidian-ledger.tsv,
# the real vault, or any sibling repo.
#
# stdout contract:
#   default: line 1 = JSON {case,root,targets,expect,ledger,sha256};
#            line 2 = FIXTURE_READY V6 <ROOT>; then human facts
#   --quiet: FIXTURE_READY V6 <ROOT> + KEY=VALUE lines only
# exit: 0 ok | 1 build/assertion failure | 2 usage
set -euo pipefail

CASE_ID=V6
SELF="${BASH_SOURCE[0]}"
HERE="$(cd -- "$(dirname -- "$SELF")" && pwd -P)"
LANE_ROOT="$(cd -- "$HERE/../../.." && pwd -P)"
EXPECTED_JSON="$HERE/expected.json"
MARKER=.case-V6-fixture

PAYLOAD='case-V6 payload (CRLF ledger fixture)'
PAYLOAD_SHA=127ac886a92b2d75784d8bbf12834d514aae8e334417a21d5b272b82f09eaece
EXPORTED_AT=2026-10-18
NOTE='case-V6 CRLF fixture row'
HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

OUT=""
LEDGER=""
OUT_GIVEN=0
QUIET=0
PRINT_ROW=0
PRINT_HASHES=0

usage() {
  cat <<EOF
usage: $SELF [--out DIR] [--ledger FILE] [--quiet] [--print-row] [--print-hashes]
  --out DIR        fixture root (default: this case directory, materialized
                   in place — all generated files are gitignored). With --out,
                   a self-contained root is built under DIR; re-running on an
                   existing dir carrying the $MARKER marker rebuilds it
  --ledger FILE    ledger copy to (re)write (default: $LANE_ROOT/tests/vault/ledger-V6.tsv)
  --quiet          print FIXTURE_READY + KEY=VALUE lines only
  --print-row      print the concrete CRLF ledger row for --out and exit
  --print-hashes   print the sha256 constants and exit
EOF
}
die() { printf '%s: %s\n' "$SELF" "$*" >&2; exit 1; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --out) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; OUT=$2; OUT_GIVEN=1; shift 2 ;;
    --ledger) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; LEDGER=$2; shift 2 ;;
    --quiet) QUIET=1; shift ;;
    --print-row) PRINT_ROW=1; shift ;;
    --print-hashes) PRINT_HASHES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

for v in "$OUT" "$LEDGER"; do
  case "$v" in
    *$'\t'*|*$'\n'*|*'"'*|*'&'*|*\\*) die "--out/--ledger must not contain tabs, newlines, quotes, ampersands or backslashes" ;;
  esac
done

[ -n "$LEDGER" ] || LEDGER="$LANE_ROOT/tests/vault/ledger-V6.tsv"

if [ "$PRINT_HASHES" = 1 ]; then
  printf 'PAYLOAD_SHA256=%s\n' "$PAYLOAD_SHA"
  printf 'note: the payload is fixed; ledger rows embed per-root absolute paths, so ledger sha256 varies per build root\n'
  exit 0
fi

if [ "$PRINT_ROW" = 1 ]; then
  [ "$OUT_GIVEN" = 1 ] || { usage >&2; exit 2; }
  out_abs="$(readlink -m -- "$OUT")"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$out_abs/src/payload.md" "$PAYLOAD_SHA" "$out_abs/vault/payload.md" "$PAYLOAD_SHA" "$EXPORTED_AT" "$NOTE"
  exit 0
fi

if [ "$OUT_GIVEN" = 0 ]; then
  OUT="$HERE"
  SUBSTITUTE_EXPECTED=0
else
  SUBSTITUTE_EXPECTED=1
  if [ -e "$OUT" ] && [ ! -d "$OUT" ]; then die "--out exists and is not a directory: $OUT"; fi
  mkdir -p -- "$OUT"
  out_abs="$(cd -- "$OUT" && pwd -P)"
  [ "$out_abs" != "$HERE" ] || die "--out must not be this case directory; omit --out for in-place materialization"
  if [ -n "$(ls -A -- "$OUT" 2>/dev/null)" ] && [ ! -e "$OUT/$MARKER" ]; then
    die "--out exists, is non-empty and carries no $MARKER marker; refusing to delete: $OUT"
  fi
  rm -rf -- "$OUT"/* "$OUT"/.[!.]* 2>/dev/null || true
fi
OUT="$(cd -- "$OUT" && pwd -P)"
[ "$SUBSTITUTE_EXPECTED" = 1 ] && touch -- "$OUT/$MARKER"
mkdir -p -- "$OUT/src" "$OUT/vault"

# clear previous payloads first: vault/payload.md is chmod 0444, which would
# block an in-place rebuild (default mode) from overwriting it
rm -f -- "$OUT/src/payload.md" "$OUT/vault/payload.md"
printf '%s\n' "$PAYLOAD" > "$OUT/src/payload.md"
printf '%s\n' "$PAYLOAD" > "$OUT/vault/payload.md"
chmod 0444 -- "$OUT/vault/payload.md"

SRC="$OUT/src/payload.md"
VP="$OUT/vault/payload.md"
SS="$(sha256sum -- "$SRC" | cut -d' ' -f1)"
VS="$(sha256sum -- "$VP" | cut -d' ' -f1)"
[ "$SS" = "$PAYLOAD_SHA" ] || die "payload sha drift: $SS != $PAYLOAD_SHA"
[ "$VS" = "$SS" ] || die "source/vault payload mismatch"

row6=$(printf '%s\t%s\t%s\t%s\t%s\t%s' "$SRC" "$SS" "$VP" "$VS" "$EXPORTED_AT" "$NOTE")
row4=$(printf '%s\t%s\t%s\t%s' "$SRC" "$SS" "$VP" "$VS")

write_ledgers() { # $1 dir — rows embed the CURRENT root paths
  local d=$1
  { printf '%s\r\n' "$HDR"; printf '%s\r\n' "$row6"; } > "$d/ledger-crlf.tsv"
  { printf '%s\n'   "$HDR"; printf '%s\n'   "$row6"; } > "$d/ledger-lf-control.tsv"
  { printf '%s\r\n' "$HDR"; printf '%s\r\n' "$row4"; } > "$d/ledger-crlf-truncated.tsv"
  cp -f -- "$d/ledger-crlf.tsv" "$d/ledger.tsv"
}

write_ledgers "$OUT"
if [ "$SUBSTITUTE_EXPECTED" = 1 ]; then
  # runner-28 resolves probes[].ledger against the case dir while resolving
  # probes[].target against its own --out root, so refresh the case-dir copies
  # (gitignored) to carry rows pointing at this --out root.
  write_ledgers "$HERE"
fi

mkdir -p -- "$(dirname -- "$LEDGER")"
ledger_tmp="$(mktemp "${LEDGER}.tmp.XXXXXX")"
cp -f -- "$OUT/ledger-crlf.tsv" "$ledger_tmp"
chmod 0644 -- "$ledger_tmp"
mv -f -- "$ledger_tmp" "$LEDGER"

# --- fixture invariants (fail loudly if the bytes are not as claimed) --------
cr_count() { tr -cd '\r' < "$1" | wc -c | tr -d ' '; }
line_count() { wc -l < "$1" | tr -d ' '; }

[ "$(cr_count "$OUT/ledger-crlf.tsv")" -eq 2 ] || die "crlf ledger does not carry exactly 2 CR"
[ "$(line_count "$OUT/ledger-crlf.tsv")" -eq 2 ] || die "crlf ledger line count != 2"
[ "$(grep -c $'\r$' "$OUT/ledger-crlf.tsv" || true)" -eq 2 ] || die "crlf ledger has a line not ending in CR"
[ "$(cr_count "$OUT/ledger-lf-control.tsv")" -eq 0 ] || die "lf control carries CR"
[ "$(cr_count "$OUT/ledger-crlf-truncated.tsv")" -eq 2 ] || die "truncated ledger does not carry 2 CR"
[ "$(awk -F'\t' 'END{print NF}' "$OUT/ledger-crlf.tsv")" -eq 6 ] || die "crlf row is not 6 columns"
[ "$(awk -F'\t' 'END{print NF}' "$OUT/ledger-crlf-truncated.tsv")" -eq 4 ] || die "truncated row is not 4 columns"
[ "$(sha256sum -- "$LEDGER" | cut -d' ' -f1)" = "$(sha256sum -- "$OUT/ledger-crlf.tsv" | cut -d' ' -f1)" ] || die "ledger copy differs from the primary"

if [ "$SUBSTITUTE_EXPECTED" = 1 ]; then
  sed "s|@FIXTURE_ROOT@|$OUT|g" "$EXPECTED_JSON" > "$OUT/expected.json"
  if grep -q '@FIXTURE_ROOT@' "$OUT/expected.json"; then die "expected.json still carries @FIXTURE_ROOT@ after substitution"; fi
else
  # in-place mode must leave the tracked template untouched
  grep -q '@FIXTURE_ROOT@' "$EXPECTED_JSON" || die "tracked expected.json template lost its @FIXTURE_ROOT@ placeholder"
fi

TARGET="$SRC"
if [ "$QUIET" = 1 ]; then
  printf 'FIXTURE_READY %s %s\n' "$CASE_ID" "$OUT"
  printf 'FIXTURE_ROOT=%s\n' "$OUT"
  printf 'LEDGER=%s\n' "$LEDGER"
  printf 'LEDGER_CRLF=%s\n' "$OUT/ledger-crlf.tsv"
  printf 'TARGET=%s\n' "$TARGET"
  printf 'VAULT=%s\n' "$VP"
  printf 'PAYLOAD_SHA256=%s\n' "$SS"
  printf 'EXPECT=VERIFIED(moved-to-obsidian)\n'
else
  printf '{"case":"%s","root":"%s","targets":["%s"],"expect":"VERIFIED(moved-to-obsidian)","ledger":"%s","sha256":"%s"}\n' \
    "$CASE_ID" "$OUT" "$TARGET" "$OUT/ledger-crlf.tsv" "$SS"
  printf 'FIXTURE_READY %s %s\n' "$CASE_ID" "$OUT"
  printf 'fixture_root=%s\n' "$OUT"
  printf 'source=%s\n' "$SRC"
  printf 'vault_copy=%s\n' "$VP"
  printf 'ledger_crlf=%s (CR=%s lines=%s)\n' "$OUT/ledger-crlf.tsv" "$(cr_count "$OUT/ledger-crlf.tsv")" "$(line_count "$OUT/ledger-crlf.tsv")"
  printf 'ledger_lf_control=%s (CR=%s)\n' "$OUT/ledger-lf-control.tsv" "$(cr_count "$OUT/ledger-lf-control.tsv")"
  printf 'ledger_crlf_truncated=%s\n' "$OUT/ledger-crlf-truncated.tsv"
  printf 'ledger_copy=%s\n' "$LEDGER"
  printf 'mode=%s\n' "$([ "$SUBSTITUTE_EXPECTED" = 1 ] && printf 'out' || printf 'in-place')"
fi
exit 0
