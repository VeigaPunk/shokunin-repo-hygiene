#!/usr/bin/env bash
# case-V2 fixture builder — souji-shokunin round 4, seat S10.
#
# Spec case V2: a vault file whose content differs from what the ledger's
# vault sha256 says (tamper case). Expected verdict:
#   NOT-VERIFIED with a reason naming a vault-side hash mismatch
#   (primary target: NOT-VERIFIED(vault-hash-mismatch)).
#
# Self-contained: builds a fake source tree + fake vault + its own test
# ledger under the fixture root. Never reads or writes the live ledger
# (corpus/knowledge/obsidian-ledger.tsv), the real vault
# (/home/vgpnk/Documents/shokokunin... → /home/vgpnk/Documents/shokoknowledge),
# or any sibling repo. No git fetch/push/commit/branch/checkout/reset/rebase
# is ever run (git init only, offline, no commits).
#
# What the fixture proves:
#   tamper-notes.md  source matches the row; the vault copy is the SAME byte
#                    count with different bytes -> only the vault-side
#                    conjunct fails (catches vault-skip and size shortcuts).
#   subtle-notes.md  same shape, but the vault copy is exactly one byte
#                    shorter (dropped trailing newline) -> catches coarse
#                    comparisons.
#   matched-notes.md control: both sides byte-identical to the row ->
#                    a correct tool must still return VERIFIED.
set -euo pipefail
export LC_ALL=C

case_name=case-V2
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
self=$(basename -- "$0")

# --- content digests (source of truth: the payload/ tree shipped beside this
# script; asserted at build time so a drifted payload fails loudly) ----------
SHA_TAMPER_SOURCE="59bea10a81540fd2252880d03f32ce22761d82b997ca276f58150223c1a90bd7"
SHA_TAMPER_VAULT="91d9f779647195141205fd585456e4bfbaef72f6ceef89c9c95375eddcf997e4"
SHA_SUBTLE_SOURCE="a0d7a278477b87ea36f42d1ad27bd777ee791f1594200500f172c2b7b7344b96"
SHA_SUBTLE_VAULT="f1ebc6ec0aa343dd04c172a2e3f47ee603ad28ceae27243fa9a79b93e03b7423"
SHA_MATCHED="2aa2322dc2298a6dba5f7005108ef4a196ce59f94ef0ee98600b2c70640f277b"

PAYLOAD_TAMPER_SRC="$here/payload/source/src/tamper-notes.md"
PAYLOAD_TAMPER_VLT="$here/payload/vault/tamper-notes.md"
PAYLOAD_SUBTLE_SRC="$here/payload/source/src/subtle-notes.md"
PAYLOAD_SUBTLE_VLT="$here/payload/vault/subtle-notes.md"
PAYLOAD_MATCHED_SRC="$here/payload/source/src/matched-notes.md"
PAYLOAD_MATCHED_VLT="$here/payload/vault/matched-notes.md"

usage() {
  cat <<'USAGE'
usage: make-fixture.sh [--out DIR] [--ledger FILE] [--quiet]
                       [--print-ledger] [--print-hashes] [--selftest]

  --out DIR        fixture root (default: fresh mktemp -d). Re-running on an
                   existing case-V2 root (marker .case-V2-fixture) rebuilds
                   it; any other non-empty directory is refused.
  --ledger FILE    additionally write the test ledger to FILE (the canonical
                   ledger is always <ROOT>/ledger.tsv)
  --quiet          print only FIXTURE_READY + KEY=VALUE lines
  --case-copy      additionally write the substituted expected.json into this
                   case directory (default: only the built root gets the
                   substituted copy; the case-dir copy stays in placeholder
                   form so it never points at a reaped temp root)
  --print-ledger   print the concrete ledger rows (no header) and exit
  --print-hashes   print the payload digest table and exit
  --selftest       build into a fresh mktemp root, assert fixture coherence
                   (A1-A8), print PASS/FAIL per assertion; exit 0 on all pass

stdout (default): line 1 single-line JSON {case,schema,root,ledger,targets,
                  expect}; then FIXTURE_READY case-V2 <ROOT>; then LEDGER=,
                  TARGET=, VAULT=, SOURCE_SHA256=, VAULT_SHA256=, EXPECT=.
stderr:           key=value facts (fixture_root=, ledger=, source_path=, ...).
Exit: 0 built (also for --print-*/--selftest pass); 1 build or assertion
      failure; 2 usage.
USAGE
}

die() { printf '%s: %s\n' "$self" "$*" >&2; exit 1; }

sha_of() { sha256sum -- "$1" | cut -d' ' -f1; }
bytes_of() { wc -c < "$1" | tr -d ' '; }

print_hashes() {
  local f bad=0
  for f in "$PAYLOAD_TAMPER_SRC" "$PAYLOAD_TAMPER_VLT" "$PAYLOAD_SUBTLE_SRC" \
           "$PAYLOAD_SUBTLE_VLT" "$PAYLOAD_MATCHED_SRC" "$PAYLOAD_MATCHED_VLT"; do
    [ -f "$f" ] || die "payload file missing: $f"
    printf '%s\t%s\t%s bytes\n' "${f#"$here/"}" "$(sha_of "$f")" "$(bytes_of "$f")"
  done
  [ "$(sha_of "$PAYLOAD_TAMPER_SRC")" = "$SHA_TAMPER_SOURCE" ] || bad=1
  [ "$(sha_of "$PAYLOAD_TAMPER_VLT")" = "$SHA_TAMPER_VAULT" ] || bad=1
  [ "$(sha_of "$PAYLOAD_SUBTLE_SRC")" = "$SHA_SUBTLE_SOURCE" ] || bad=1
  [ "$(sha_of "$PAYLOAD_SUBTLE_VLT")" = "$SHA_SUBTLE_VAULT" ] || bad=1
  [ "$(sha_of "$PAYLOAD_MATCHED_SRC")" = "$SHA_MATCHED" ] || bad=1
  [ "$(sha_of "$PAYLOAD_MATCHED_VLT")" = "$SHA_MATCHED" ] || bad=1
  [ "$bad" = 0 ] || die "payload digest mismatch against the constants above"
  return 0
}

# --- argument parsing -------------------------------------------------------
out=""
ledger_copy=""
quiet=0
case_copy=0
do_print_ledger=0
do_print_hashes=0
do_selftest=0

while [ $# -gt 0 ]; do
  case "$1" in
    --out) [ $# -ge 2 ] || die "--out requires a directory"; out=$2; shift 2 ;;
    --ledger) [ $# -ge 2 ] || die "--ledger requires a file"; ledger_copy=$2; shift 2 ;;
    --quiet) quiet=1; shift ;;
    --case-copy) case_copy=1; shift ;;
    --print-ledger) do_print_ledger=1; shift ;;
    --print-hashes) do_print_hashes=1; shift ;;
    --selftest) do_selftest=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) die "unknown option: $1" ;;
    *) [ -z "$out" ] || die "unexpected extra argument: $1"; out=$1; shift ;;
  esac
done

if [ "$do_print_hashes" = 1 ]; then
  print_hashes
  exit 0
fi

# --- build ------------------------------------------------------------------
if [ "$do_selftest" = 1 ]; then
  out=$(mktemp -d "${TMPDIR:-/tmp}/souji-fixture-case-V2-selftest.XXXXXX")
elif [ -z "$out" ]; then
  tmp_base=${SOUJI_FIXTURE_TMPDIR:-${TMPDIR:-/tmp}}
  out=$(mktemp -d "${tmp_base%/}/souji-fixture-case-V2.XXXXXX")
else
  mkdir -p -- "$out" || die "cannot create --out directory: $out"
fi
out=$(cd -- "$out" && pwd -P) || die "cannot enter --out directory"

case "$out" in
  *'"'*|*'\'*|*'&'*|*'|'*) die "fixture path contains a JSON/sed-unsafe character: $out" ;;
esac
[ "$out" != "$here" ] || die "refusing to build into the case directory itself"

if [ -n "$(ls -A -- "$out")" ]; then
  if [ -e "$out/.case-V2-fixture" ]; then
    rm -rf -- "$out"
    mkdir -p -- "$out"
  else
    die "refusing non-empty directory without .case-V2-fixture marker: $out"
  fi
fi

printf 'case-V2 fixture\n' > "$out/.case-V2-fixture"

print_hashes >&2 || exit 1

src_tamper="$out/source/src/tamper-notes.md"
src_subtle="$out/source/src/subtle-notes.md"
src_matched="$out/source/src/matched-notes.md"
vault_tamper="$out/vault/tamper-notes.md"
vault_subtle="$out/vault/subtle-notes.md"
vault_matched="$out/vault/matched-notes.md"
ledger="$out/ledger.tsv"

mkdir -p -- "$out/source/src" "$out/vault"
cp -- "$PAYLOAD_TAMPER_SRC" "$src_tamper"
cp -- "$PAYLOAD_TAMPER_VLT" "$vault_tamper"
cp -- "$PAYLOAD_SUBTLE_SRC" "$src_subtle"
cp -- "$PAYLOAD_SUBTLE_VLT" "$vault_subtle"
cp -- "$PAYLOAD_MATCHED_SRC" "$src_matched"
cp -- "$PAYLOAD_MATCHED_VLT" "$vault_matched"
chmod 0444 -- "$vault_tamper" "$vault_subtle" "$vault_matched"

# Offline repo context so the fixture root behaves like a real lane repo.
if [ ! -d "$out/.git" ] && command -v git >/dev/null 2>&1; then
  export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_TERMINAL_PROMPT=0
  git -C "$out" init -q -b master 2>/dev/null || git -C "$out" init -q
fi

# Ledger rows record the EXPORT-TIME hashes: for the tamper rows that is the
# source bytes' digest, so the vault side is the failing conjunct.
{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$src_tamper" "$SHA_TAMPER_SOURCE" "$vault_tamper" "$SHA_TAMPER_SOURCE" \
    "2026-10-18" "case-V2 vault-tamper"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$src_subtle" "$SHA_SUBTLE_SOURCE" "$vault_subtle" "$SHA_SUBTLE_SOURCE" \
    "2026-10-18" "case-V2 vault-tamper-subtle"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$src_matched" "$SHA_MATCHED" "$vault_matched" "$SHA_MATCHED" \
    "2026-10-18" "case-V2 control matched"
} > "$ledger"

if [ -n "$ledger_copy" ]; then
  mkdir -p -- "$(dirname -- "$ledger_copy")"
  cp -f -- "$ledger" "$ledger_copy"
fi

# --- substituted expected.json ----------------------------------------------
# Written to BOTH the built root (self-describing fixture) and this case
# directory (runner-28 reads the case-dir expected.json).
tmp_exp=$(mktemp "$out/.expected.XXXXXX")
sed "s|@FIXTURE_ROOT@|$out|g" "$here/expected.template.json" > "$tmp_exp"
command -v python3 >/dev/null 2>&1 \
  || die "python3 required for JSON validation"
python3 - "$tmp_exp" <<'PY' || die "substituted expected.json is not valid JSON"
import json, sys
json.load(open(sys.argv[1]))
PY
mv -f -- "$tmp_exp" "$out/expected.json"
if [ "$case_copy" = 1 ]; then
  cp -f -- "$out/expected.json" "$here/expected.json"
fi

# --- fixture assertions (A1-A8; build fails loudly, never warns) ------------
assert_fixture() {
  local rc=0
  check() { # check <name> <desc> <actual> <expected>
    if [ "$3" = "$4" ]; then printf 'PASS %s\n' "$1"
    else printf 'FAIL %s (got=%s want=%s)\n' "$1" "$3" "$4"; rc=1; fi
  }
  check A1 "source tamper digest" "$(sha_of "$src_tamper")" "$SHA_TAMPER_SOURCE"
  check A2 "vault tamper digest differs, same byte count" \
    "$(sha_of "$vault_tamper")/$([ "$(bytes_of "$vault_tamper")" = "$(bytes_of "$src_tamper")" ] && echo same || echo diff)" \
    "$SHA_TAMPER_VAULT/same"
  check A3 "subtle vault is one byte shorter" \
    "$(sha_of "$vault_subtle")/$(( $(bytes_of "$src_subtle") - $(bytes_of "$vault_subtle") ))" \
    "$SHA_SUBTLE_VAULT/1"
  check A4 "matched pair byte-identical" "$(sha_of "$src_matched")/$(sha_of "$vault_matched")" "$SHA_MATCHED/$SHA_MATCHED"
  check A5 "ledger row count" "$(($(wc -l < "$ledger") - 1))" "3"
  check A6 "ledger tamper vault_sha256 is the export-time digest" \
    "$(awk -F'\t' -v p="$vault_tamper" '$3==p{print $4}' "$ledger")" "$SHA_TAMPER_SOURCE"
  check A7 "vault files read-only (0444)" \
    "$(stat -c %a "$vault_tamper")/$(stat -c %a "$vault_subtle")/$(stat -c %a "$vault_matched")" "444/444/444"
  check A8 "no live-ledger contact (fixture ledger is inside the root)" \
    "$(case "$ledger" in "$out"/*) echo inside;; *) echo outside;; esac)" "inside"
  return "$rc"
}

if [ "$do_selftest" = 1 ]; then
  assert_fixture
  rc=$?
  printf 'SELFTEST %s: %s\n' "$case_name" "$([ "$rc" = 0 ] && echo PASS || echo FAIL)"
  rm -rf -- "$out"
  exit "$rc"
fi

# --- emitted contract -------------------------------------------------------
if [ "$do_print_ledger" = 1 ]; then
  tail -n +2 "$ledger"
  exit 0
fi

json=$(printf '{"case":"%s","schema":"souji-vault-fixture/1","root":"%s","ledger":"%s","targets":["%s","%s","%s"],"expect":[{"path":"%s","vault_path":"%s","verdict":"NOT-VERIFIED","reason":"vault-hash-mismatch","receipt":null,"verdict_string":"NOT-VERIFIED(vault-hash-mismatch)"},{"path":"%s","vault_path":"%s","verdict":"NOT-VERIFIED","reason":"vault-hash-mismatch","receipt":null,"verdict_string":"NOT-VERIFIED(vault-hash-mismatch)"},{"path":"%s","vault_path":"%s","verdict":"VERIFIED","reason":null,"receipt":"moved-to-obsidian","verdict_string":"VERIFIED"}]}' \
  "$case_name" "$out" "$ledger" \
  "$src_tamper" "$src_subtle" "$src_matched" \
  "$src_tamper" "$vault_tamper" \
  "$src_subtle" "$vault_subtle" \
  "$src_matched" "$vault_matched")

if [ "$quiet" = 1 ]; then
  printf 'FIXTURE_READY %s %s\n' "$case_name" "$out"
else
  printf '%s\n' "$json"
  printf 'FIXTURE_READY %s %s\n' "$case_name" "$out"
fi
printf 'LEDGER=%s\n' "$ledger"
printf 'TARGET=%s\n' "$src_tamper"
printf 'TARGET_SUBTLE=%s\n' "$src_subtle"
printf 'TARGET_CONTROL=%s\n' "$src_matched"
printf 'VAULT=%s\n' "$vault_tamper"
printf 'SOURCE_SHA256=%s\n' "$SHA_TAMPER_SOURCE"
printf 'VAULT_SHA256=%s\n' "$SHA_TAMPER_VAULT"
printf 'EXPECT=NOT-VERIFIED(vault-hash-mismatch)\n'
printf 'EXPECT_CONTROL=VERIFIED\n'
[ -z "$ledger_copy" ] || printf 'LEDGER_COPY=%s\n' "$ledger_copy"

{
  printf 'fixture_root=%s\n' "$out"
  printf 'case=%s\n' "$case_name"
  printf 'ledger=%s\n' "$ledger"
  printf 'source_path=%s\n' "$src_tamper"
  printf 'source_sha256=%s\n' "$SHA_TAMPER_SOURCE"
  printf 'vault_path=%s\n' "$vault_tamper"
  printf 'vault_sha256_actual=%s\n' "$SHA_TAMPER_VAULT"
  printf 'vault_sha256_recorded=%s\n' "$SHA_TAMPER_SOURCE"
  printf 'expect=NOT-VERIFIED(vault-hash-mismatch)\n'
  printf 'expect_control=VERIFIED\n'
  printf 'expected_json=%s\n' "$out/expected.json"
} >&2
