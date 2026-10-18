#!/usr/bin/env bash
# case-V8 fixture builder — souji-shokunin round 4, seat S16.
#
# Case V8 (space-bearing names): a fake Obsidian vault file and a source file
# whose basenames both contain spaces — and they are deliberately DIFFERENT
# names (source `meeting notes 2026-10.md`, vault `Meeting Notes 2026-10.md`,
# the shape a real Obsidian export produces when the note title is applied).
# A ledger row in tests/vault/ledger-V8.tsv matches source path + source
# sha256 + vault path + vault sha256 (all four conjuncts, each path carrying
# literal spaces). Expected: VERIFIED (receipt moved-to-obsidian). Under the
# r2 vocabulary the installed tools/souji-verify.sh reports SAFE +
# moved-to-obsidian for the same inputs — see expected.json "crosscheck".
#
# An auxiliary no-row control pair (source `control notes.md` / vault
# `Control Notes.md`, byte-identical, no ledger row) lives in the same tree:
# the row is the receipt, so it must stay NOT-VERIFIED even though the vault
# copy exists. It is declared under expected.json "auxiliary_checks", not in
# "targets".
#
# Builds under --out (default: fresh mktemp -d):
#   source/meeting notes 2026-10.md   candidate source file (fixed bytes)
#   vault/Meeting Notes 2026-10.md    byte-identical copy, mode 0444
#   source/control notes.md           control source (fixed bytes)
#   vault/Control Notes.md            byte-identical control copy, mode 0444
#   ledger.tsv                        copy of the ledger written to --ledger
#   expected.json                     @FIXTURE_ROOT@-substituted copy
# and (re)writes --ledger (default tests/vault/ledger-V8.tsv) as
#   header row + exactly one data row carrying this build's absolute paths.
# The live ledger corpus/knowledge/obsidian-ledger.tsv is never touched, and
# nothing outside --out and --ledger is written. No network.
# Deterministic: fixed content; the built bytes are asserted against the
# declared sha256 constants and cross-checked against expected.json; a drift
# is a hard failure, never a warning. Paths vary per run (mktemp root); the
# CONTENT digests are the pinned constants.
#
# Contract (mirrors the V1/V4/V5 house shapes):
#   normal stdout: line 1 = JSON {case,root,targets,expect,vault,ledger,sha256}
#                  line 2 = FIXTURE_READY V8 <absolute target path>
#   --quiet stdout: KEY=VALUE lines + the FIXTURE_READY line (runners parse
#                  the root from it)
#   stderr: KEY=VALUE block + human notes
#   exit codes: 0 ok, 1 build/assertion failure, 2 usage
set -euo pipefail
export LC_ALL=C

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LANE_ROOT="$(cd -- "$HERE/../../.." && pwd)"
SELF="$(basename -- "$0")"
EXPECTED_JSON="$HERE/expected.json"
CASE=case-V8
CASE_ID=V8

# --- content sha256 constants ----------------------------------------------
# Source of truth is content_note()/content_ctl() below; `--print-hashes`
# prints the table. A mismatch is a build failure, never a warning.
SHA_NOTE="2fc29f1f563835d0e66139afa269b4de51355859ed30232b41847a2862f1084e"
NOTE_BYTES=225
SHA_CTL="3f5d8d2f08280a356f765ef393a762ac8bf93d423103b569347a12ad50ee1ab1"
CTL_BYTES=143

# Space-bearing names are the point of this case. Builder-relative:
SRC_REL="source/meeting notes 2026-10.md"
VLT_REL="vault/Meeting Notes 2026-10.md"
SRC_CTL_REL="source/control notes.md"
VLT_CTL_REL="vault/Control Notes.md"

content_note() {
  cat <<'EOF'
# Vault note V8 - space-bearing names

Source file and vault copy are byte-identical; both basenames contain
spaces, and the ledger row carries the same absolute paths.
case-V8: expected VERIFIED (receipt moved-to-obsidian).
EOF
}

content_ctl() {
  cat <<'EOF'
# Vault note V8 - control with spaces

Byte-identical pair with no ledger row: the row is the receipt.
case-V8 control: expected NOT-VERIFIED.
EOF
}

sha_of() { sha256sum | cut -d' ' -f1; }

usage() {
  cat <<EOF
usage: $SELF [--out DIR] [--ledger FILE] [--quiet] [--skip-ledger]
             [--print-row] [--print-hashes]

  --out DIR       fixture root (default: fresh mktemp -d); re-running on an
                  existing $CASE root rebuilds it, any other non-empty
                  directory is refused
  --ledger FILE   ledger to (re)write (default: $LANE_ROOT/tests/vault/ledger-V8.tsv)
  --quiet         print only KEY=VALUE lines on stdout (plus FIXTURE_READY)
  --skip-ledger   build the tree but write no ledger anywhere
  --print-row     print the concrete ledger row for --out and exit
  --print-hashes  print the content sha256 table and exit
EOF
}

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

expect_hash() {
  local id="$1" const="$2" computed="$3"
  if [ "$const" != "$computed" ]; then
    printf '%s: sha256 mismatch for %s\n  constant: %s\n  computed: %s\n  update SHA_NOTE/SHA_CTL in make-fixture.sh and expected.json (--print-hashes prints the table)\n' \
      "$SELF" "$id" "$const" "$computed" >&2
    return 1
  fi
}

assert_expected_json() {
  [ -f "$EXPECTED_JSON" ] || { echo "$SELF: note: $EXPECTED_JSON not found; skipping declaration cross-check" >&2; return 0; }
  local rc=0
  grep -qF -- "$SHA_NOTE" "$EXPECTED_JSON" || { echo "$SELF: expected.json does not declare sha256 $SHA_NOTE" >&2; rc=1; }
  grep -qF -- 'meeting notes 2026-10.md' "$EXPECTED_JSON" || { echo "$SELF: expected.json does not declare the source name" >&2; rc=1; }
  grep -qF -- 'Meeting Notes 2026-10.md' "$EXPECTED_JSON" || { echo "$SELF: expected.json does not declare the vault name" >&2; rc=1; }
  grep -qF -- "$CASE_ID" "$EXPECTED_JSON" || { echo "$SELF: expected.json does not declare case $CASE_ID" >&2; rc=1; }
  return "$rc"
}

OUT=""
LEDGER="$LANE_ROOT/tests/vault/ledger-V8.tsv"
QUIET=0
SKIP_LEDGER=0
PRINT_ROW=0
PRINT_HASHES=0
while [ $# -gt 0 ]; do
  case "$1" in
    --out) [ $# -ge 2 ] || { echo "$SELF: --out needs a value" >&2; exit 2; }; OUT="$2"; shift 2 ;;
    --ledger) [ $# -ge 2 ] || { echo "$SELF: --ledger needs a value" >&2; exit 2; }; LEDGER="$2"; shift 2 ;;
    --quiet) QUIET=1; shift ;;
    --skip-ledger) SKIP_LEDGER=1; shift ;;
    --print-row) PRINT_ROW=1; shift ;;
    --print-hashes) PRINT_HASHES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "$SELF: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$OUT" in *$'\t'*|*$'\n'*) echo "$SELF: --out must not contain tabs or newlines" >&2; exit 2 ;; esac
case "$LEDGER" in *$'\t'*|*$'\n'*) echo "$SELF: --ledger must not contain tabs or newlines" >&2; exit 2 ;; esac

if [ "$PRINT_HASHES" = 1 ]; then
  printf 'note\t%s\t%s\n' "$(content_note | sha_of)" "$(content_note | wc -c | tr -d ' ')"
  printf 'ctl\t%s\t%s\n' "$(content_ctl | sha_of)" "$(content_ctl | wc -c | tr -d ' ')"
  exit 0
fi

ledger_row() { # $1 root
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$1/$SRC_REL" "$SHA_NOTE" \
    "$1/$VLT_REL" "$SHA_NOTE" \
    "2026-10-18" "case-V8 space-bearing names"
}

if [ "$PRINT_ROW" = 1 ]; then
  [ -n "$OUT" ] || { echo "$SELF: --print-row needs --out DIR" >&2; exit 2; }
  ledger_row "$(readlink -m -- "$OUT")"
  exit 0
fi

command -v sha256sum >/dev/null 2>&1 || { echo "$SELF: sha256sum is required" >&2; exit 1; }

if ! expect_hash note "$SHA_NOTE" "$(content_note | sha_of)"; then exit 1; fi
if [ "$(content_note | wc -c | tr -d ' ')" != "$NOTE_BYTES" ]; then
  echo "$SELF: note content byte count drifted from $NOTE_BYTES" >&2; exit 1
fi
if ! expect_hash ctl "$SHA_CTL" "$(content_ctl | sha_of)"; then exit 1; fi
if [ "$(content_ctl | wc -c | tr -d ' ')" != "$CTL_BYTES" ]; then
  echo "$SELF: control content byte count drifted from $CTL_BYTES" >&2; exit 1
fi
assert_expected_json

if [ -z "$OUT" ]; then
  OUT="$(mktemp -d "${TMPDIR:-/tmp}/souji-vault-V8.XXXXXX")"
fi
if [ -e "$OUT" ] && [ ! -d "$OUT" ]; then
  echo "$SELF: --out exists and is not a directory: $OUT" >&2
  exit 2
fi
if [ -d "$OUT" ]; then
  if [ -f "$OUT/.case-V8-fixture" ]; then
    rm -rf -- "$OUT"
  elif [ -n "$(ls -A -- "$OUT" 2>/dev/null || true)" ]; then
    echo "$SELF: --out exists, is non-empty and carries no .case-V8-fixture marker; refusing to delete: $OUT" >&2
    exit 2
  fi
fi
mkdir -p -- "$OUT"
OUT="$(readlink -m -- "$OUT")"
printf 'case-V8 fixture root; safe to delete\n' > "$OUT/.case-V8-fixture"

mkdir -p -- "$OUT/source" "$OUT/vault"
content_note > "$OUT/$SRC_REL"
content_note > "$OUT/$VLT_REL"
content_ctl  > "$OUT/$SRC_CTL_REL"
content_ctl  > "$OUT/$VLT_CTL_REL"
chmod 0444 -- "$OUT/$VLT_REL" "$OUT/$VLT_CTL_REL"

# --- case invariant: every path this case deals in contains a space --------
for f in "$OUT/$SRC_REL" "$OUT/$VLT_REL" "$OUT/$SRC_CTL_REL" "$OUT/$VLT_CTL_REL"; do
  case "$(basename -- "$f")" in
    *" "*) : ;;
    *) echo "$SELF: case-V8 invariant broken: basename has no space: $f" >&2; exit 1 ;;
  esac
done

# --- per-file verification (computed bytes vs declared constant) -----------
verify_file() {
  local path="$1" want="$2" got
  got="$(sha256sum -- "$path" | cut -d' ' -f1)"
  if [ "$got" != "$want" ]; then
    echo "$SELF: built file does not match declared sha256: $path" >&2
    echo "  declared: $want" >&2
    echo "  computed: $got" >&2
    exit 1
  fi
}
verify_file "$OUT/$SRC_REL" "$SHA_NOTE"
verify_file "$OUT/$VLT_REL" "$SHA_NOTE"
verify_file "$OUT/$SRC_CTL_REL" "$SHA_CTL"
verify_file "$OUT/$VLT_CTL_REL" "$SHA_CTL"
cmp -s -- "$OUT/$SRC_REL" "$OUT/$VLT_REL" || { echo "$SELF: source and vault copies differ" >&2; exit 1; }
cmp -s -- "$OUT/$SRC_CTL_REL" "$OUT/$VLT_CTL_REL" || { echo "$SELF: control copies differ" >&2; exit 1; }

# Fixture root behaves like a real repo (offline, no commits, no refs).
git init -q -b master "$OUT" 2>/dev/null || git init -q "$OUT" 2>/dev/null || true

# --- ledger -----------------------------------------------------------------
LEDGER_ABS=""
if [ "$SKIP_LEDGER" = 0 ]; then
  LEDGER_ABS="$(readlink -m -- "$LEDGER")"
  mkdir -p -- "$(dirname -- "$LEDGER_ABS")"
  L_TMP="$LEDGER_ABS.tmp.$$"
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    ledger_row "$OUT"
  } > "$L_TMP"
  mv -f -- "$L_TMP" "$LEDGER_ABS"
  cp -- "$LEDGER_ABS" "$OUT/ledger.tsv"
fi

# @FIXTURE_ROOT@-substituted expected.json copy for runners that read it
# from the root (V4/V5 convention). Substitution uses a sed delimiter that
# cannot appear in a POSIX path.
if [ -f "$EXPECTED_JSON" ]; then
  sed "s|@FIXTURE_ROOT@|$OUT|g" -- "$EXPECTED_JSON" > "$OUT/expected.json"
fi

TARGET="$OUT/$SRC_REL"
VAULT_FILE="$OUT/$VLT_REL"
CTL_TARGET="$OUT/$SRC_CTL_REL"
CTL_VAULT="$OUT/$VLT_CTL_REL"

if [ "$QUIET" = 1 ]; then
  printf 'FIXTURE_ROOT=%s\n' "$OUT"
  printf 'SOURCE_FILE=%s\n' "$TARGET"
  printf 'VAULT_FILE=%s\n' "$VAULT_FILE"
  printf 'CONTROL_SOURCE=%s\n' "$CTL_TARGET"
  printf 'CONTROL_VAULT=%s\n' "$CTL_VAULT"
  printf 'LEDGER_FILE=%s\n' "${LEDGER_ABS:-<skipped>}"
  printf 'SHA256=%s\n' "$SHA_NOTE"
  printf 'TARGET=note:%s\n' "$TARGET"
  # Third token is the ROOT (never the target): the target path contains
  # spaces, and runners parse this line with `FIXTURE_READY\s+\S+\s+(\S+)`.
  printf 'FIXTURE_READY %s %s\n' "$CASE_ID" "$OUT"
  exit 0
fi

{
  printf 'FIXTURE_ROOT=%s\n' "$OUT"
  printf 'SOURCE_FILE=%s\n' "$TARGET"
  printf 'VAULT_FILE=%s\n' "$VAULT_FILE"
  printf 'CONTROL_SOURCE=%s\n' "$CTL_TARGET"
  printf 'CONTROL_VAULT=%s\n' "$CTL_VAULT"
  printf 'LEDGER_FILE=%s\n' "${LEDGER_ABS:-<skipped>}"
  printf 'SHA256=%s\n' "$SHA_NOTE"
  printf 'EXPECTED_JSON=%s\n' "$EXPECTED_JSON"
} >&2

printf '{"case":"%s","root":"%s","targets":["%s"],"expect":[{"path":"%s","verdict":"VERIFIED","receipt":"moved-to-obsidian"}],"vault":"%s","ledger":"%s","sha256":"%s"}\n' \
  "$CASE_ID" "$(json_escape "$OUT")" "$(json_escape "$TARGET")" "$(json_escape "$TARGET")" \
  "$(json_escape "$VAULT_FILE")" "$(json_escape "${LEDGER_ABS:-}")" "$SHA_NOTE"
# Third token is the ROOT (never the target): the target path contains
# spaces, and runners parse this line with `FIXTURE_READY\s+\S+\s+(\S+)`.
printf 'FIXTURE_READY %s %s\n' "$CASE_ID" "$OUT"

cat >&2 <<EOF
$CASE fixture built — space-bearing names, expected VERIFIED (receipt moved-to-obsidian).

Source and vault basenames both contain spaces and are deliberately
different names (source `$SRC_REL`, vault `$VLT_REL`). The files are
byte-identical (sha256 $SHA_NOTE) and the ledger row in
${LEDGER_ABS:-<ledger skipped>}
matches source path + source sha256 + vault path + vault sha256 — with the
literal spaces in both path fields.

Auxiliary no-row control (NOT in targets): $CTL_TARGET
and $CTL_VAULT are byte-identical but carry no ledger row — the row is the
receipt, so it must stay NOT-VERIFIED even with the vault copy present.

Evaluate the target by its exact absolute path (ledger matching is
path-exact; quote it — it contains spaces):
  "$TARGET"

Disarmed check (no matching row -> NOT-VERIFIED / NOT-SAFE): point the
tool's ledger override at a header-only ledger instead of
${LEDGER_ABS:-<ledger skipped>}.

The live ledger corpus/knowledge/obsidian-ledger.tsv was not touched.
EOF
