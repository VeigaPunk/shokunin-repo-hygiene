#!/usr/bin/env bash
# case-V1 fixture builder — souji-shokunin round 4, seat S09.
#
# Case V1 (clean pair): a fake Obsidian vault with note.md, a source file with
# identical bytes, and a ledger row in tests/vault/ledger-V1.tsv matching
# source path + source sha256 + vault path + vault sha256 (all four conjuncts).
# Expected: VERIFIED (receipt moved-to-obsidian). Under the r2 vocabulary the
# installed tools/souji-verify.sh reports SAFE + moved-to-obsidian for the same
# inputs — see expected.json "crosscheck".
#
# Builds under --out (default: fresh mktemp -d):
#   source/note.md     candidate source file (fixed bytes, sha256 constant below)
#   vault/note.md      byte-identical copy, mode 0444 (read-only signal)
#   ledger.tsv         header row + one data row with this build's absolute paths
#   expected.json      @FIXTURE_ROOT@-substituted copy of the declaration
# and (re)writes --ledger (default tests/vault/ledger-V1.tsv) as the same
# header + one row. The live ledger corpus/knowledge/obsidian-ledger.tsv is
# never touched, and nothing outside --out and --ledger is written. No network.
# Deterministic: fixed content; the built bytes are asserted against the
# declared sha256 constant and cross-checked against expected.json; a drift is
# a hard failure, never a warning.
#
# Contract (mirrors the V1/V4/V5/V8 house shapes):
#   normal stdout: line 1 = JSON {case,root,targets,expect,vault,ledger,sha256}
#                  line 2 = FIXTURE_READY V1 <ROOT>  (third token is the ROOT)
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
CASE=case-V1
CASE_ID=V1

# --- content sha256 constant -----------------------------------------------
# Source of truth is content_note() below; `--print-hashes` prints the table.
# A mismatch is a build failure, never a warning.
SHA_NOTE="a63192a11325e61f3aebfd483c34f21c05c5bf815bc83cef7866a92b8132f840"
NOTE_BYTES=161

content_note() {
  cat <<'EOF'
# Vault note V1

Byte-identical pair: this source file and its vault copy. One ledger row
matches both paths and both sha256 values. Expected verdict: VERIFIED.
EOF
}

sha_of() { sha256sum | cut -d' ' -f1; }

usage() {
  cat <<EOF
usage: $SELF [--out DIR | DIR] [--ledger FILE] [--quiet] [--skip-ledger]
             [--print-row] [--print-hashes]

  --out DIR       fixture root (default: fresh mktemp -d); re-running on an
                  existing $CASE root (marker .case-V1-fixture) rebuilds it,
                  any other non-empty directory is refused
  --ledger FILE   ledger copy path (default: $LANE_ROOT/tests/vault/ledger-V1.tsv);
                  the canonical ledger is always <ROOT>/ledger.tsv
  --quiet         print only FIXTURE_READY + KEY=VALUE lines on stdout
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
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

expect_hash() {
  local id="$1" const="$2" computed="$3"
  if [ "$const" != "$computed" ]; then
    printf '%s: sha256 mismatch for %s\n  constant: %s\n  computed: %s\n  update SHA_NOTE in make-fixture.sh and expected.json (--print-hashes prints the table)\n' \
      "$SELF" "$id" "$const" "$computed" >&2
    return 1
  fi
}

assert_expected_json() {
  [ -f "$EXPECTED_JSON" ] || { echo "$SELF: note: $EXPECTED_JSON not found; skipping declaration cross-check" >&2; return 0; }
  local rc=0
  grep -qF -- "$SHA_NOTE" "$EXPECTED_JSON" || { echo "$SELF: expected.json does not declare sha256 $SHA_NOTE" >&2; rc=1; }
  grep -qF -- 'source/note.md' "$EXPECTED_JSON" || { echo "$SELF: expected.json does not declare source/note.md" >&2; rc=1; }
  grep -qF -- 'vault/note.md' "$EXPECTED_JSON" || { echo "$SELF: expected.json does not declare vault/note.md" >&2; rc=1; }
  grep -qF -- "$CASE_ID" "$EXPECTED_JSON" || { echo "$SELF: expected.json does not declare case $CASE_ID" >&2; rc=1; }
  return "$rc"
}

OUT=""
LEDGER="$LANE_ROOT/tests/vault/ledger-V1.tsv"
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
    --) shift; break ;;
    -*) echo "$SELF: unknown argument: $1" >&2; usage >&2; exit 2 ;;
    *) [ -z "$OUT" ] || { echo "$SELF: unexpected extra argument: $1" >&2; exit 2; }; OUT="$1"; shift ;;
  esac
done

case "$OUT" in *$'\t'*|*$'\n'*) echo "$SELF: --out must not contain tabs or newlines" >&2; exit 2 ;; esac
case "$LEDGER" in *$'\t'*|*$'\n'*) echo "$SELF: --ledger must not contain tabs or newlines" >&2; exit 2 ;; esac

if [ "$PRINT_HASHES" = 1 ]; then
  printf 'note\t%s\t%s\n' "$(content_note | sha_of)" "$(content_note | wc -c | tr -d ' ')"
  exit 0
fi

ledger_row() { # $1 root
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$1/source/note.md" "$SHA_NOTE" \
    "$1/vault/note.md" "$SHA_NOTE" \
    "2026-10-18" "case-V1 clean pair"
}

if [ "$PRINT_ROW" = 1 ]; then
  [ -n "$OUT" ] || { echo "$SELF: --print-row needs --out DIR" >&2; exit 2; }
  ledger_row "$(readlink -m -- "$OUT")"
  exit 0
fi

command -v sha256sum >/dev/null 2>&1 || { echo "$SELF: sha256sum is required" >&2; exit 1; }

if ! expect_hash note "$SHA_NOTE" "$(content_note | sha_of)"; then exit 1; fi
if [ "$(content_note | wc -c | tr -d ' ')" != "$NOTE_BYTES" ]; then
  echo "$SELF: content byte count drifted from $NOTE_BYTES" >&2; exit 1
fi
assert_expected_json

if [ -z "$OUT" ]; then
  OUT="$(mktemp -d "${TMPDIR:-/tmp}/souji-vault-V1.XXXXXX")"
fi
if [ -e "$OUT" ] && [ ! -d "$OUT" ]; then
  echo "$SELF: --out exists and is not a directory: $OUT" >&2
  exit 2
fi
if [ -d "$OUT" ]; then
  if [ -f "$OUT/.case-V1-fixture" ]; then
    rm -rf -- "$OUT"
  elif [ -n "$(ls -A -- "$OUT" 2>/dev/null || true)" ]; then
    echo "$SELF: --out exists, is non-empty and carries no .case-V1-fixture marker; refusing to delete: $OUT" >&2
    exit 2
  fi
fi
mkdir -p -- "$OUT"
OUT="$(readlink -m -- "$OUT")"
case "$OUT" in
  *'"'*|*'\'*|*'&'*|*'|'*) echo "$SELF: --out path contains a JSON/sed-unsafe character: $OUT" >&2; exit 2 ;;
esac
[ "$OUT" != "$HERE" ] || { echo "$SELF: refusing to build into the case directory itself" >&2; exit 2; }

printf 'case-V1 fixture root; safe to delete\n' > "$OUT/.case-V1-fixture"

mkdir -p -- "$OUT/source" "$OUT/vault"
content_note > "$OUT/source/note.md"
content_note > "$OUT/vault/note.md"
chmod 0444 -- "$OUT/vault/note.md"

# Offline repo context so the fixture root behaves like a real lane repo and
# the pushed receipt must fall through to the ledger (no commits: `git log
# --diff-filter=A` finds nothing).
if [ ! -d "$OUT/.git" ] && command -v git >/dev/null 2>&1; then
  export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_TERMINAL_PROMPT=0
  git -C "$OUT" init -q -b master 2>/dev/null || git -C "$OUT" init -q 2>/dev/null || true
fi

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
verify_file "$OUT/source/note.md" "$SHA_NOTE"
verify_file "$OUT/vault/note.md" "$SHA_NOTE"
cmp -s -- "$OUT/source/note.md" "$OUT/vault/note.md" || { echo "$SELF: source and vault copies differ" >&2; exit 1; }

# --- ledger -----------------------------------------------------------------
LEDGER_ABS=""
if [ "$SKIP_LEDGER" = 0 ]; then
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    ledger_row "$OUT"
  } > "$OUT/ledger.tsv"
  LEDGER_ABS="$(readlink -m -- "$LEDGER")"
  if [ "$LEDGER_ABS" != "$OUT/ledger.tsv" ]; then
    mkdir -p -- "$(dirname -- "$LEDGER_ABS")"
    cp -f -- "$OUT/ledger.tsv" "$LEDGER_ABS"
  fi
fi

# @FIXTURE_ROOT@-substituted expected.json copy for runners that read it
# from the root (V4/V5/V8 convention). Substitution uses a sed delimiter that
# cannot appear in a POSIX path (checked above).
if [ -f "$EXPECTED_JSON" ]; then
  sed "s|@FIXTURE_ROOT@|$OUT|g" -- "$EXPECTED_JSON" > "$OUT/expected.json"
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$OUT/expected.json" <<'PY' || { echo "$SELF: substituted expected.json is not valid JSON" >&2; exit 1; }
import json, sys
json.load(open(sys.argv[1]))
PY
  fi
fi

TARGET="$OUT/source/note.md"
VAULT_FILE="$OUT/vault/note.md"

if [ "$QUIET" = 1 ]; then
  printf 'FIXTURE_ROOT=%s\n' "$OUT"
  printf 'SOURCE_FILE=%s\n' "$TARGET"
  printf 'VAULT_DIR=%s\n' "$OUT/vault"
  printf 'VAULT_FILE=%s\n' "$VAULT_FILE"
  printf 'LEDGER_FILE=%s\n' "${LEDGER_ABS:-<skipped>}"
  printf 'SHA256=%s\n' "$SHA_NOTE"
  printf 'TARGET=note:%s\n' "$TARGET"
  # Third token is the ROOT (never the target): runners parse this line with
  # `FIXTURE_READY\s+\S+\s+(\S+)` and take the token as the fixture root.
  printf 'FIXTURE_READY %s %s\n' "$CASE_ID" "$OUT"
  exit 0
fi

{
  printf 'FIXTURE_ROOT=%s\n' "$OUT"
  printf 'SOURCE_FILE=%s\n' "$TARGET"
  printf 'VAULT_DIR=%s\n' "$OUT/vault"
  printf 'VAULT_FILE=%s\n' "$VAULT_FILE"
  printf 'LEDGER_FILE=%s\n' "${LEDGER_ABS:-<skipped>}"
  printf 'SHA256=%s\n' "$SHA_NOTE"
  printf 'EXPECTED_JSON=%s\n' "$EXPECTED_JSON"
} >&2

printf '{"case":"%s","root":"%s","targets":["%s"],"expect":[{"path":"%s","verdict":"VERIFIED","receipt":"moved-to-obsidian"}],"vault":"%s","ledger":"%s","sha256":"%s"}\n' \
  "$CASE_ID" "$(json_escape "$OUT")" "$(json_escape "$TARGET")" "$(json_escape "$TARGET")" \
  "$(json_escape "$VAULT_FILE")" "$(json_escape "${LEDGER_ABS:-}")" "$SHA_NOTE"
# Third token is the ROOT (never the target): runners parse this line with
# `FIXTURE_READY\s+\S+\s+(\S+)` and take the token as the fixture root.
printf 'FIXTURE_READY %s %s\n' "$CASE_ID" "$OUT"

cat >&2 <<EOF
$CASE fixture built — clean pair, expected VERIFIED (receipt moved-to-obsidian).

The source file and the fake vault copy are byte-identical
(sha256 $SHA_NOTE), and the ledger row in
${LEDGER_ABS:-<ledger skipped>}
matches source path + source sha256 + vault path + vault sha256.
The live ledger corpus/knowledge/obsidian-ledger.tsv was not touched.

Evaluate the target by its exact absolute path (ledger matching is path-exact):
  $TARGET

Disarmed check (no matching row -> NOT-VERIFIED / NOT-SAFE): point the tool's
ledger override at a header-only ledger instead of
${LEDGER_ABS:-<ledger skipped>}.
EOF
