#!/usr/bin/env bash
# case-V7 fixture builder — souji-shokunin round 4, seat S15.
#
# Spec case V7: a ledger row carries extra columns beyond the 6 canonical
# (source_path, source_sha256, vault_path, vault_sha256, exported_at, note).
# Expected: VERIFIED — the canonical positions decide, extra columns are
# ignored, the note (column 6) is still read, and hash checking is not
# weakened.
#
# Payload pairs live in payload/source/src/*.md and payload/vault/*.md beside
# this script; their digests are asserted at build time so a drifted payload
# fails loudly:
#   extra-cols-notes.md     7-column row (extra exported_by=…) -> VERIFIED (primary)
#   extra-cols-8-notes.md   8-column row (extra + empty trailing) -> VERIFIED
#   six-cols-notes.md       6-column row control -> VERIFIED
#   extra-cols-mismatch.md  7-column row, vault copy edited after export
#                           -> NOT-VERIFIED(vault-hash-mismatch)
#
# Self-contained: builds a fake vault + fake source tree + its own test
# ledger under the fixture root. Never reads or writes the live ledger
# (corpus/knowledge/obsidian-ledger.tsv), the real vault
# (/home/vgpnk/Documents/shokoknowledge), or any sibling repo. No git
# fetch/push/commit/branch/checkout/reset/rebase is ever run (git init only,
# offline, no commits).
#
# Contract (mirrors the V1/V2/V4/V5 house shapes):
#   normal stdout: line 1 = JSON {case,schema,root,ledger,targets,expect}
#                  line 2 = FIXTURE_READY case-V7 <ROOT>
#                  then KEY=VALUE lines
#   --quiet stdout: FIXTURE_READY + KEY=VALUE lines only
#   stderr: key=value facts + human notes
#   exit codes: 0 built; 1 build/assertion failure; 2 usage
set -euo pipefail
export LC_ALL=C

case_name=case-V7
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
self=$(basename -- "$0")

# --- payload digest constants (source of truth: the payload/ tree; asserted
# below and by --print-hashes so a drifted payload fails loudly) --------------
SHA_SIX="ada33bd81eeab6375081b16fe83dc8db9418131bc62e97a68b6439ac6a68a781"
SHA_EXTRA7="1543cfa1785f270374b6f16407440152cbfd27dd08b1ad1f24f71267ab456206"
SHA_EXTRA8="f2b8420064e81b6efc0eab1917cbb4ff6a088cef150251c66d4b3545a36eef53"
SHA_MISMATCH_SRC="2ceca233cfc70cfd9a07e6e889ea21951c9ee433250cc6b6cc0cd6e9bf3f4239"
SHA_MISMATCH_VLT="6e28bf53541405576602483a415a368a088845fe63f683085a379d7d2b1b632f"

P_SRC="$here/payload/source/src"
P_VLT="$here/payload/vault"
P_SIX="$P_SRC/six-cols-notes.md"
P_X7="$P_SRC/extra-cols-notes.md"
P_X8="$P_SRC/extra-cols-8-notes.md"
P_MM="$P_SRC/extra-cols-mismatch.md"
P_V_SIX="$P_VLT/six-cols-notes.md"
P_V_X7="$P_VLT/extra-cols-notes.md"
P_V_X8="$P_VLT/extra-cols-8-notes.md"
P_V_MM="$P_VLT/extra-cols-mismatch.md"

usage() {
  cat <<'USAGE'
usage: make-fixture.sh [--out DIR] [--ledger FILE] [--quiet]
                       [--print-ledger] [--print-hashes]

  --out DIR        fixture root (default: fresh mktemp -d). Re-running on an
                   existing case-V7 root (marker .case-V7-fixture) rebuilds
                   it; any other non-empty directory is refused.
  --ledger FILE    additionally write the test ledger to FILE (the canonical
                   ledger is always <ROOT>/ledger.tsv)
  --quiet          print only FIXTURE_READY + KEY=VALUE lines on stdout
  --print-ledger   print the concrete ledger rows (no header) and exit
  --print-hashes   print the payload digest table and exit

stdout (default): line 1 single-line JSON {case,schema,root,ledger,targets,
                  expect}; then FIXTURE_READY case-V7 <ROOT>; then LEDGER=,
                  TARGET=, VAULT=, EXPECT=, NOTE_EXPECTED= and per-target
                  TARGET_2..4 / EXPECT_2..4 lines.
stderr:           key=value facts (fixture_root=, ledger=, primary_path=, ...).
Exit: 0 built (also for --print-*); 1 build or assertion failure; 2 usage.
USAGE
}

die() { printf '%s: %s\n' "$self" "$*" >&2; exit 1; }
die_usage() { printf '%s: %s\n' "$self" "$*" >&2; exit 2; }

sha_of() { sha256sum -- "$1" | cut -d' ' -f1; }
bytes_of() { wc -c < "$1" | tr -d ' '; }

print_hashes() {
  local f bad=0
  for f in "$P_SIX" "$P_X7" "$P_X8" "$P_MM" "$P_V_SIX" "$P_V_X7" "$P_V_X8" "$P_V_MM"; do
    [ -f "$f" ] || die "payload file missing: $f"
    printf '%s\t%s\t%s bytes\n' "${f#"$here/"}" "$(sha_of "$f")" "$(bytes_of "$f")"
  done
  [ "$(sha_of "$P_SIX")" = "$SHA_SIX" ] || bad=1
  [ "$(sha_of "$P_X7")" = "$SHA_EXTRA7" ] || bad=1
  [ "$(sha_of "$P_X8")" = "$SHA_EXTRA8" ] || bad=1
  [ "$(sha_of "$P_MM")" = "$SHA_MISMATCH_SRC" ] || bad=1
  [ "$(sha_of "$P_V_SIX")" = "$SHA_SIX" ] || bad=1
  [ "$(sha_of "$P_V_X7")" = "$SHA_EXTRA7" ] || bad=1
  [ "$(sha_of "$P_V_X8")" = "$SHA_EXTRA8" ] || bad=1
  [ "$(sha_of "$P_V_MM")" = "$SHA_MISMATCH_VLT" ] || bad=1
  [ "$bad" = 0 ] || die "payload digest mismatch against the constants above"
  return 0
}

# --- argument parsing --------------------------------------------------------
out=""
ledger_copy=""
quiet=0
do_print_ledger=0
do_print_hashes=0

while [ $# -gt 0 ]; do
  case "$1" in
    --out) [ $# -ge 2 ] || die_usage "--out requires a directory"; out=$2; shift 2 ;;
    --ledger) [ $# -ge 2 ] || die_usage "--ledger requires a file"; ledger_copy=$2; shift 2 ;;
    --quiet) quiet=1; shift ;;
    --print-ledger) do_print_ledger=1; shift ;;
    --print-hashes) do_print_hashes=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) die_usage "unknown option: $1" ;;
    *) [ -z "$out" ] || die_usage "unexpected extra argument: $1"; out=$1; shift ;;
  esac
done

if [ "$do_print_hashes" = 1 ]; then
  print_hashes
  exit 0
fi

command -v sha256sum >/dev/null 2>&1 || die "sha256sum is required"

if [ -z "$out" ]; then
  out=$(mktemp -d "${TMPDIR:-/tmp}/souji-fixture-case-V7.XXXXXX")
else
  mkdir -p -- "$out" || die "cannot create --out directory: $out"
fi
out=$(cd -- "$out" && pwd -P) || die "cannot enter --out directory"

case "$out" in
  *'"'*|*'\'*|*'&'*|*'|'*|*$'\t'*|*$'\n'*) die "fixture path contains a JSON/sed-unsafe character: $out" ;;
esac
[ "$out" != "$here" ] || die "refusing to build into the case directory itself"

if [ -n "$(ls -A -- "$out")" ]; then
  if [ -e "$out/.case-V7-fixture" ]; then
    rm -rf -- "$out"
    mkdir -p -- "$out"
  else
    die "refusing non-empty directory without .case-V7-fixture marker: $out"
  fi
fi

printf 'case-V7 fixture\n' > "$out/.case-V7-fixture"

src_p="$out/source/src/extra-cols-notes.md";   vlt_p="$out/vault/extra-cols-notes.md"
src_8="$out/source/src/extra-cols-8-notes.md"; vlt_8="$out/vault/extra-cols-8-notes.md"
src_c="$out/source/src/six-cols-notes.md";     vlt_c="$out/vault/six-cols-notes.md"
src_m="$out/source/src/extra-cols-mismatch.md"; vlt_m="$out/vault/extra-cols-mismatch.md"
ledger="$out/ledger.tsv"

mkdir -p -- "$out/source/src" "$out/vault"

# --- payload copy + per-file digest verification -----------------------------
verify_file() { # $1 path, $2 wanted sha256
  local got
  got="$(sha_of "$1")"
  [ "$got" = "$2" ] || die "built file does not match declared sha256: $1 (got $got want $2)"
}

cp -- "$P_X7" "$src_p"; cp -- "$P_V_X7" "$vlt_p"
cp -- "$P_X8" "$src_8"; cp -- "$P_V_X8" "$vlt_8"
cp -- "$P_SIX" "$src_c"; cp -- "$P_V_SIX" "$vlt_c"
cp -- "$P_MM" "$src_m"; cp -- "$P_V_MM" "$vlt_m"
chmod 0444 -- "$vlt_p" "$vlt_8" "$vlt_c" "$vlt_m"

verify_file "$src_p" "$SHA_EXTRA7"; verify_file "$vlt_p" "$SHA_EXTRA7"
verify_file "$src_8" "$SHA_EXTRA8"; verify_file "$vlt_8" "$SHA_EXTRA8"
verify_file "$src_c" "$SHA_SIX";    verify_file "$vlt_c" "$SHA_SIX"
verify_file "$src_m" "$SHA_MISMATCH_SRC"; verify_file "$vlt_m" "$SHA_MISMATCH_VLT"
cmp -s -- "$src_m" "$vlt_m" && die "mismatch pair must differ on the vault side"

# --- offline repo context so repo-discovery code paths behave ----------------
if [ ! -d "$out/.git" ] && command -v git >/dev/null 2>&1; then
  export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_TERMINAL_PROMPT=0
  git -C "$out" init -q -b master 2>/dev/null || git -C "$out" init -q
fi

# --- test ledger: header + 4 rows (7 / 8 / 6 / 7 columns) --------------------
{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$src_p" "$SHA_EXTRA7" "$vlt_p" "$SHA_EXTRA7" "2026-10-18" "case-V7 extra-cols" "exported_by=souji-fixture"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$src_8" "$SHA_EXTRA8" "$vlt_8" "$SHA_EXTRA8" "2026-10-18" "case-V7 extra-cols-8" "exported_by=souji-fixture" ""
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$src_c" "$SHA_SIX" "$vlt_c" "$SHA_SIX" "2026-10-18" "case-V7 six-cols control"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$src_m" "$SHA_MISMATCH_SRC" "$vlt_m" "$SHA_MISMATCH_SRC" "2026-10-18" "case-V7 extra-cols mismatch" "exported_by=souji-fixture"
} > "$ledger"

if [ -n "$ledger_copy" ]; then
  mkdir -p -- "$(dirname -- "$ledger_copy")"
  cp -f -- "$ledger" "$ledger_copy"
fi

# --- ledger shape assertions -------------------------------------------------
row_nf() { awk -F'\t' -v n="$1" 'NR==n {print NF; exit}' "$ledger"; }
[ "$(row_nf 1)" = 6 ] || die "header must have 6 columns, got $(row_nf 1)"
[ "$(row_nf 2)" = 7 ] || die "row 1 (extra-cols) must have 7 columns, got $(row_nf 2)"
[ "$(row_nf 3)" = 8 ] || die "row 2 (extra-cols-8) must have 8 columns, got $(row_nf 3)"
[ "$(row_nf 4)" = 6 ] || die "row 3 (six-cols control) must have 6 columns, got $(row_nf 4)"
[ "$(row_nf 5)" = 7 ] || die "row 4 (mismatch) must have 7 columns, got $(row_nf 5)"
[ "$(awk 'NF' "$ledger" | wc -l | tr -d ' ')" = 5 ] || die "ledger must hold header + exactly 4 data rows"

# --- substituted expected.json ----------------------------------------------
sed "s|@FIXTURE_ROOT@|$out|g" "$here/expected.json" > "$out/expected.json"
command -v python3 >/dev/null 2>&1 \
  || die "python3 required for JSON validation"
python3 - "$out/expected.json" <<'PY' || die "substituted expected.json is not valid JSON"
import json, sys
json.load(open(sys.argv[1]))
PY

if [ "$do_print_ledger" = 1 ]; then
  tail -n +2 "$ledger"
  exit 0
fi

# --- output contract ---------------------------------------------------------
json=$(printf '{"case":"%s","schema":"souji-vault-fixture/1","root":"%s","ledger":"%s","targets":["%s","%s","%s","%s"],"expect":[{"path":"%s","verdict":"VERIFIED","receipt":"moved-to-obsidian"},{"path":"%s","verdict":"VERIFIED","receipt":"moved-to-obsidian"},{"path":"%s","verdict":"VERIFIED","receipt":"moved-to-obsidian"},{"path":"%s","verdict":"NOT-VERIFIED","reason":"vault-hash-mismatch","receipt":null}]}' \
  "$case_name" "$out" "$ledger" "$src_p" "$src_8" "$src_c" "$src_m" "$src_p" "$src_8" "$src_c" "$src_m")

if [ "$quiet" = 1 ]; then
  printf 'FIXTURE_READY %s %s\n' "$case_name" "$out"
else
  printf '%s\n' "$json"
  printf 'FIXTURE_READY %s %s\n' "$case_name" "$out"
fi
printf 'LEDGER=%s\n' "$ledger"
printf 'TARGET=%s\n' "$src_p"
printf 'VAULT=%s\n' "$vlt_p"
printf 'SOURCE_SHA256=%s\n' "$SHA_EXTRA7"
printf 'VAULT_SHA256=%s\n' "$SHA_EXTRA7"
printf 'EXPECT=VERIFIED\n'
printf 'NOTE_EXPECTED=case-V7 extra-cols\n'
printf 'TARGET_2=%s\n' "$src_8"
printf 'EXPECT_2=VERIFIED\n'
printf 'TARGET_3=%s\n' "$src_c"
printf 'EXPECT_3=VERIFIED\n'
printf 'TARGET_4=%s\n' "$src_m"
printf 'EXPECT_4=NOT-VERIFIED(vault-hash-mismatch)\n'
[ -z "$ledger_copy" ] || printf 'LEDGER_COPY=%s\n' "$ledger_copy"

{
  printf 'fixture_root=%s\n' "$out"
  printf 'case=%s\n' "$case_name"
  printf 'ledger=%s\n' "$ledger"
  printf 'rows=4 columns=7,8,6,7\n'
  printf 'primary_path=%s\n' "$src_p"
  printf 'primary_note=case-V7 extra-cols\n'
  printf 'expect=VERIFIED VERIFIED VERIFIED NOT-VERIFIED(vault-hash-mismatch)\n'
  printf 'expected_json=%s\n' "$out/expected.json"
} >&2
