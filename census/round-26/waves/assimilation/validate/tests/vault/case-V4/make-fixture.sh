#!/usr/bin/env bash
# case-V4 fixture builder — souji-shokunin round 4, seat S12.
#
# Spec case V4: the ledger row points at a vault path that does not exist.
# Expected verdict: NOT-VERIFIED(vault-absent).
#
# Self-contained: builds a source file (present, hash-matching the row), an
# absent vault path whose parent directory exists, and its own test ledger
# under the fixture root. Never reads or writes the live ledger
# (corpus/knowledge/obsidian-ledger.tsv), the real vault
# (/home/vgpnk/Documents/shokoknowledge), or any sibling repo.
#
# Discriminator: the source side is fully present and hash-matching (the
# source file's sha256 equals the row's source_sha256 and vault_sha256).
# The ONLY failing conjunct is the vault path's presence — so this case
# catches (a) a harness that skips the vault-side existence/hash check and
# reports SAFE/VERIFIED from the source side alone, (b) class collapse to
# NOT-SAFE(none)/NOT-SAFE(unreachable) instead of the distinct
# NOT-VERIFIED(vault-absent), and (c) a false vault-absent on a
# vault-present pair (control in selftest.sh).
set -euo pipefail
export LC_ALL=C

case_name=case-V4
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
self=$(basename -- "$0")

# Fixed content digest: the exported bytes. Asserted at build time.
SHA_ROUND_TRIP="d9cae6dfd163e93e34fcc1c9d90a3b910160a3fb2981b7dc2741ba3bdbe3ab2d"

content_round_trip() {
  cat <<'EOF'
# Vault-absent notes (V4 vault-absent)

Exported to the vault on 2026-10-18; the ledger row records both sides.
The vault-side path does not exist — the recorded copy was never created
or has since been removed. The source copy is the only surviving bytes.

case-V4: the ledger row's vault_path is absent.
EOF
}

usage() {
  cat <<'USAGE'
usage: make-fixture.sh [--out DIR] [--ledger FILE] [--quiet]
                       [--print-ledger] [--print-hashes]

  --out DIR        fixture root (default: fresh mktemp -d). Re-running on an
                   existing case-V4 root (marker .case-V4-fixture) rebuilds
                   it; any other non-empty directory is refused.
  --ledger FILE    additionally write the test ledger to FILE (the canonical
                   ledger is always <ROOT>/ledger.tsv)
  --quiet          print only FIXTURE_READY + KEY=VALUE lines
  --print-ledger   print the concrete ledger rows (no header) and exit
  --print-hashes   print the content digest table and exit

stdout (default): line 1 single-line JSON {case,root,ledger,targets,expect};
                  then FIXTURE_READY case-V4 <ROOT>; then LEDGER=, TARGET=,
                  VAULT=, SOURCE_SHA256=, VAULT_SHA256=, EXPECT= lines.
stderr:           key=value facts (fixture_root=, ledger=, source_path=, ...).
Exit: 0 built (also for --print-*); 1 build or assertion failure; 2 usage.
USAGE
}

die() { printf '%s: %s\n' "$self" "$*" >&2; exit 1; }

out=""
ledger_copy=""
quiet=0
do_print_ledger=0
do_print_hashes=0

while [ $# -gt 0 ]; do
  case "$1" in
    --out) [ $# -ge 2 ] || die "--out requires a directory"; out=$2; shift 2 ;;
    --ledger) [ $# -ge 2 ] || die "--ledger requires a file"; ledger_copy=$2; shift 2 ;;
    --quiet) quiet=1; shift ;;
    --print-ledger) do_print_ledger=1; shift ;;
    --print-hashes) do_print_hashes=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) die "unknown option: $1" ;;
    *) [ -z "$out" ] || die "unexpected extra argument: $1"; out=$1; shift ;;
  esac
done

if [ "$do_print_hashes" = 1 ]; then
  tmp=$(mktemp "${TMPDIR:-/tmp}/case-V4.hash.XXXXXX")
  trap 'rm -f -- "$tmp"' EXIT
  content_round_trip > "$tmp"
  got=$(sha256sum -- "$tmp" | cut -d' ' -f1)
  bytes=$(wc -c < "$tmp" | tr -d ' ')
  printf 'SHA_ROUND_TRIP=%s bytes=%s\n' "$got" "$bytes"
  [ "$got" = "$SHA_ROUND_TRIP" ] || die "content digest mismatch: got $got want $SHA_ROUND_TRIP"
  exit 0
fi

if [ -z "$out" ]; then
  tmp_base=${SOUJI_FIXTURE_TMPDIR:-${TMPDIR:-/tmp}}
  out=$(mktemp -d "${tmp_base%/}/souji-fixture-case-V4.XXXXXX")
else
  mkdir -p -- "$out" || die "cannot create --out directory: $out"
fi
out=$(cd -- "$out" && pwd -P) || die "cannot enter --out directory"

case "$out" in
  *'"'*|*'\'*|*'&'*|*'|'*) die "fixture path contains a JSON/sed-unsafe character: $out" ;;
esac
[ "$out" != "$here" ] || die "refusing to build into the case directory itself"

if [ -n "$(ls -A -- "$out")" ]; then
  if [ -e "$out/.case-V4-fixture" ]; then
    rm -rf -- "$out"
    mkdir -p -- "$out"
  else
    die "refusing non-empty directory without .case-V4-fixture marker: $out"
  fi
fi

printf 'case-V4 fixture\n' > "$out/.case-V4-fixture"

src="$out/source/round-trip-notes.md"
vault="$out/vault/round-trip-notes.md"
ledger="$out/ledger.tsv"

mkdir -p -- "$out/source" "$out/vault"

payload=$(mktemp "$out/.payload.XXXXXX")
content_round_trip > "$payload"
got=$(sha256sum -- "$payload" | cut -d' ' -f1)
[ "$got" = "$SHA_ROUND_TRIP" ] || die "content digest mismatch: got $got want $SHA_ROUND_TRIP"
cp -- "$payload" "$src"
rm -f -- "$payload"
chmod 0444 -- "$src"

# Offline repo context so the fixture root behaves like a real lane repo.
if [ ! -d "$out/.git" ] && command -v git >/dev/null 2>&1; then
  export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_TERMINAL_PROMPT=0
  git -C "$out" init -q -b master 2>/dev/null || git -C "$out" init -q
fi

{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$src" "$SHA_ROUND_TRIP" "$vault" "$SHA_ROUND_TRIP" "2026-10-18" "case-V4 vault-absent"
} > "$ledger"

if [ -n "$ledger_copy" ]; then
  mkdir -p -- "$(dirname -- "$ledger_copy")"
  cp -f -- "$ledger" "$ledger_copy"
fi

# --- assertions (build fails loudly, never warns) ---------------------------
[ -f "$src" ] || die "source file must exist: $src"
[ "$(sha256sum -- "$src" | cut -d' ' -f1)" = "$SHA_ROUND_TRIP" ] || die "source digest mismatch"
[ ! -e "$vault" ] || die "vault path must NOT exist: $vault"
[ -d "$out/vault" ] || die "vault parent dir must exist: $out/vault"
{
  IFS= read -r hdr
  IFS= read -r row
  rest=$(cat)
} < "$ledger"
[ "$hdr" = "$(printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote')" ] \
  || die "ledger header mismatch"
[ -z "$rest" ] || die "ledger must hold exactly one data row"
IFS=$'\t' read -r r_sp r_ss r_vp r_vs _r_at _r_note <<< "$row"
[ "$r_sp" = "$src" ] || die "ledger source_path mismatch"
[ "$r_ss" = "$SHA_ROUND_TRIP" ] || die "ledger source_sha256 mismatch"
[ "$r_vp" = "$vault" ] || die "ledger vault_path mismatch"
[ "$r_vs" = "$SHA_ROUND_TRIP" ] || die "ledger vault_sha256 mismatch"

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

json=$(printf '{"case":"%s","schema":"souji-vault-fixture/1","root":"%s","ledger":"%s","targets":["%s"],"expect":[{"path":"%s","vault_path":"%s","verdict":"NOT-VERIFIED","reason":"vault-absent","receipt":null,"verdict_string":"NOT-VERIFIED(vault-absent)"}]}' \
  "$case_name" "$out" "$ledger" "$src" "$src" "$vault")

if [ "$quiet" = 1 ]; then
  printf 'FIXTURE_READY %s %s\n' "$case_name" "$out"
else
  printf '%s\n' "$json"
  printf 'FIXTURE_READY %s %s\n' "$case_name" "$out"
fi
printf 'LEDGER=%s\n' "$ledger"
printf 'TARGET=%s\n' "$src"
printf 'VAULT=%s\n' "$vault"
printf 'SOURCE_SHA256=%s\n' "$SHA_ROUND_TRIP"
printf 'VAULT_SHA256=%s\n' "$SHA_ROUND_TRIP"
printf 'EXPECT=NOT-VERIFIED(vault-absent)\n'
[ -z "$ledger_copy" ] || printf 'LEDGER_COPY=%s\n' "$ledger_copy"

{
  printf 'fixture_root=%s\n' "$out"
  printf 'ledger=%s\n' "$ledger"
  printf 'source_path=%s\n' "$src"
  printf 'vault_path=%s\n' "$vault"
  printf 'vault_present=no\n'
  printf 'source_present=yes\n'
  printf 'sha256=%s\n' "$SHA_ROUND_TRIP"
} >&2

exit 0
