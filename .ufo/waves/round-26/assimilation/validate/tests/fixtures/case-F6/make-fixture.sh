#!/usr/bin/env bash
# case-F6 fixture builder — souji-shokunin round 2, seat S04.
#
# Spec: tools/souji-verify.spec.md, fixture case
#   F6 ledger-matched file (ledger row + matching sha256 both sides)
#      -> SAFE(moved-to-obsidian)
#
# Builds under --out (default: fresh mktemp -d):
#   source/           git repo holding the candidate files. Their introducing
#                     commit sits on branch `export-prep`, which is NOT an
#                     ancestor of the resolved default branch (origin/HEAD ->
#                     origin/main), so the `pushed` receipt cannot fire.
#   vault/            fake Obsidian vault: byte-identical / near-miss copies,
#                     files mode 0444 (read-only signal for the tool).
#   ledger-inject.txt the 3 concrete ledger rows that arm this case; the same
#                     bytes are written to tests/results/ledger-inject.txt
#                     (override with --inject).
#
# The runner appends the payload rows to corpus/knowledge/obsidian-ledger.tsv
# before evaluating the targets and restores the ledger afterwards. This
# script never touches the live ledger. Expected verdicts and the declared
# rows live in expected.json; the contract is documented in README.md.
#
# Git plumbing only: init / add / write-tree / commit-tree / update-ref /
# symbolic-ref. No fetch, push, commit, branch, checkout, reset or rebase is
# run anywhere here (round rule), and nothing outside --out and --inject is
# written. Deterministic: fixed author/committer identity and dates, fixed
# file bytes; content sha256 values are asserted against the constants below
# and cross-checked against expected.json.
set -euo pipefail
export LC_ALL=C

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LANE_ROOT="$(cd -- "$HERE/../../.." && pwd)"
SELF="$(basename -- "$0")"
EXPECTED_JSON="$HERE/expected.json"

# --- content sha256 constants ----------------------------------------------
# Source of truth is the content_*() functions below; `--print-hashes` prints
# the computed table. A mismatch is a build failure, never a warning.
SHA_LEDGER_MATCH="d095e2ad302dc62d5a0b0ba8c7be9d7ba7dc868d40157a3b4609da071858ff65"
SHA_NOT_EXPORTED="48e1fd44784875a1fc3cc783fe4e5cc21284e396a3eaf1964590fb71023a168d"
SHA_MISMATCH_SOURCE="6ad80b965e37eed124bbc5344c497bfcaf4ce73646183dae67baacb2216e4692"
SHA_MISMATCH_EXPORTED="4dc5dd0a7df3e2f08724a3f753c785d0d15ea356808ded4b13db67aa6496ebc4"
SHA_DRIFT_SOURCE="94953f18b6ac6dd4fd65fd38e4e19183a65676fe532f04f9691e4f60d469bca4"
SHA_DRIFT_VAULT="efbfc7f3752e34f790b25b56b0e2a5d16fffae67b2a2eccde3c04b17f967cb28"

# --- fixture file contents (exact bytes, LF, trailing newline) -------------
content_ledger_match() {
  cat <<'EOF'
# Heredoc quorum notes

Working notes on heredoc quoting, exported to the vault before quarantine.
case-F6: byte-identical on both sides.
EOF
}

content_not_exported() {
  cat <<'EOF'
# Not-exported notes

A byte-identical vault copy exists, but no ledger row was recorded.
case-F6: the row is the receipt, not the copy.
EOF
}

content_mismatch_source() {
  cat <<'EOF'
# Ledger mismatch notes

Edited after export. The ledger row still carries the pre-edit hash.
case-F6: source-side hash mismatch.
EOF
}

content_mismatch_exported() {
  cat <<'EOF'
# Ledger mismatch notes

Pre-edit content, exported to the vault.
case-F6: source-side hash mismatch.
EOF
}

content_drift_source() {
  cat <<'EOF'
# Vault drift notes

Exported with exactly this content; the vault copy was edited later.
case-F6: vault-side hash drift.
EOF
}

content_drift_vault() {
  cat <<'EOF'
# Vault drift notes

Edited inside the vault after export; the ledger row still carries the
pre-drift vault hash.
case-F6: vault-side hash drift.
EOF
}

usage() {
  cat <<EOF
usage: $SELF [--out DIR] [--inject FILE] [--quiet] [--print-injection] [--print-hashes]

  --out DIR          fixture root (default: fresh mktemp -d); re-running on an
                     existing case-F6 root rebuilds it, any other non-empty
                     directory is refused
  --inject FILE      injection payload path (default:
                     $LANE_ROOT/tests/results/ledger-inject.txt)
  --quiet            print only KEY=VALUE / TARGET=<id>:<path> lines
  --print-injection  print the concrete ledger rows for --out and exit
  --print-hashes     print the content sha256 table and exit
EOF
}

sha_of() {
  sha256sum | cut -d' ' -f1
}

content_for() {
  case "$1" in
    ledger-match) content_ledger_match ;;
    not-exported) content_not_exported ;;
    mismatch-source) content_mismatch_source ;;
    mismatch-exported) content_mismatch_exported ;;
    drift-source) content_drift_source ;;
    drift-vault) content_drift_vault ;;
    *) echo "$SELF: unknown content token: $1" >&2; return 2 ;;
  esac
}

computed_hashes() {
  printf 'ledger-match\t%s\n' "$(content_for ledger-match | sha_of)"
  printf 'not-exported\t%s\n' "$(content_for not-exported | sha_of)"
  printf 'mismatch-source\t%s\n' "$(content_for mismatch-source | sha_of)"
  printf 'mismatch-exported\t%s\n' "$(content_for mismatch-exported | sha_of)"
  printf 'drift-source\t%s\n' "$(content_for drift-source | sha_of)"
  printf 'drift-vault\t%s\n' "$(content_for drift-vault | sha_of)"
}

expect_hash() {
  local id="$1" const="$2" computed="$3"
  if [ "$const" != "$computed" ]; then
    printf 'make-fixture.sh: sha256 mismatch for %s\n  constant: %s\n  computed: %s\n  update SHA_* in make-fixture.sh and expected.json (--print-hashes prints the table)\n' \
      "$id" "$const" "$computed" >&2
    return 1
  fi
}

assert_constants() {
  local rc=0
  expect_hash ledger-match      "$SHA_LEDGER_MATCH"     "$(content_for ledger-match | sha_of)"     || rc=1
  expect_hash not-exported      "$SHA_NOT_EXPORTED"     "$(content_for not-exported | sha_of)"     || rc=1
  expect_hash mismatch-source   "$SHA_MISMATCH_SOURCE"  "$(content_for mismatch-source | sha_of)"  || rc=1
  expect_hash mismatch-exported "$SHA_MISMATCH_EXPORTED" "$(content_for mismatch-exported | sha_of)" || rc=1
  expect_hash drift-source      "$SHA_DRIFT_SOURCE"     "$(content_for drift-source | sha_of)"     || rc=1
  expect_hash drift-vault       "$SHA_DRIFT_VAULT"      "$(content_for drift-vault | sha_of)"      || rc=1
  return "$rc"
}

assert_expected_json() {
  [ -f "$EXPECTED_JSON" ] || { echo "$SELF: note: $EXPECTED_JSON not found; skipping declaration cross-check" >&2; return 0; }
  local rc=0 h
  for h in "$SHA_LEDGER_MATCH" "$SHA_NOT_EXPORTED" "$SHA_MISMATCH_SOURCE" \
           "$SHA_MISMATCH_EXPORTED" "$SHA_DRIFT_SOURCE" "$SHA_DRIFT_VAULT"; do
    grep -qF -- "$h" "$EXPECTED_JSON" || { echo "$SELF: expected.json does not declare sha256 $h" >&2; rc=1; }
  done
  local p
  for p in source/src/heredoc-quorum-notes.md source/src/not-exported-notes.md \
           source/src/hash-mismatch-notes.md source/src/vault-drift-notes.md; do
    grep -qF -- "$p" "$EXPECTED_JSON" || { echo "$SELF: expected.json does not declare path $p" >&2; rc=1; }
  done
  return "$rc"
}

row() {
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6"
}

ledger_rows() {
  local root="$1"
  row "$root/source/src/heredoc-quorum-notes.md" "$SHA_LEDGER_MATCH" \
      "$root/vault/heredoc-quorum-notes.md" "$SHA_LEDGER_MATCH" \
      "2026-10-18" "case-F6 ledger-match"
  row "$root/source/src/hash-mismatch-notes.md" "$SHA_MISMATCH_EXPORTED" \
      "$root/vault/hash-mismatch-notes.md" "$SHA_MISMATCH_EXPORTED" \
      "2026-10-18" "case-F6 source-hash-mismatch"
  row "$root/source/src/vault-drift-notes.md" "$SHA_DRIFT_SOURCE" \
      "$root/vault/vault-drift-notes.md" "$SHA_DRIFT_SOURCE" \
      "2026-10-18" "case-F6 vault-hash-drift"
}

OUT=""
INJECT=""
QUIET=0
PRINT_INJECTION=0
PRINT_HASHES=0
while [ $# -gt 0 ]; do
  case "$1" in
    --out) [ $# -ge 2 ] || { echo "$SELF: --out needs a value" >&2; exit 2; }; OUT="$2"; shift 2 ;;
    --inject) [ $# -ge 2 ] || { echo "$SELF: --inject needs a value" >&2; exit 2; }; INJECT="$2"; shift 2 ;;
    --quiet) QUIET=1; shift ;;
    --print-injection) PRINT_INJECTION=1; shift ;;
    --print-hashes) PRINT_HASHES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "$SELF: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[ -n "$INJECT" ] || INJECT="$LANE_ROOT/tests/results/ledger-inject.txt"

case "$OUT" in *$'\t'*|*$'\n'*) echo "$SELF: --out must not contain tabs or newlines" >&2; exit 2 ;; esac
case "$INJECT" in *$'\t'*|*$'\n'*) echo "$SELF: --inject must not contain tabs or newlines" >&2; exit 2 ;; esac

if [ "$PRINT_HASHES" = 1 ]; then
  computed_hashes
  exit 0
fi

if [ "$PRINT_INJECTION" = 1 ]; then
  [ -n "$OUT" ] || { echo "$SELF: --print-injection needs --out DIR" >&2; exit 2; }
  ledger_rows "$OUT"
  exit 0
fi

command -v git >/dev/null 2>&1 || { echo "$SELF: git is required" >&2; exit 1; }
command -v sha256sum >/dev/null 2>&1 || { echo "$SELF: sha256sum is required" >&2; exit 1; }

assert_constants
assert_expected_json

if [ -z "$OUT" ]; then
  OUT="$(mktemp -d "${TMPDIR:-/tmp}/souji-case-F6.XXXXXX")"
fi
if [ -e "$OUT" ] && [ ! -d "$OUT" ]; then
  echo "$SELF: --out exists and is not a directory: $OUT" >&2
  exit 2
fi
if [ -d "$OUT" ]; then
  if [ -f "$OUT/.case-F6-fixture" ]; then
    rm -rf -- "$OUT"
  elif [ -n "$(ls -A -- "$OUT" 2>/dev/null || true)" ]; then
    echo "$SELF: --out exists, is non-empty and carries no .case-F6-fixture marker; refusing to delete: $OUT" >&2
    exit 2
  fi
fi
mkdir -p -- "$OUT"
printf 'case-F6 fixture root; safe to delete\n' > "$OUT/.case-F6-fixture"

SRC="$OUT/source"
VAULT="$OUT/vault"
mkdir -p -- "$SRC/src" "$VAULT"

# --- source repo ------------------------------------------------------------
export GIT_AUTHOR_NAME="souji-fixture"
export GIT_AUTHOR_EMAIL="fixture@shokunin.local"
export GIT_COMMITTER_NAME="souji-fixture"
export GIT_COMMITTER_EMAIL="fixture@shokunin.local"
export GIT_AUTHOR_DATE="2026-10-18T00:00:00+0000"
export GIT_COMMITTER_DATE="2026-10-18T00:00:00+0000"

printf '# case-F6 source repo\n\nFixture repo for souji-verify.spec.md case F6.\n' > "$SRC/README.md"
git init -q -- "$SRC"
git -C "$SRC" config core.autocrlf false
git -C "$SRC" config core.excludesFile /dev/null
git -C "$SRC" config user.name "souji-fixture"
git -C "$SRC" config user.email "fixture@shokunin.local"
git -C "$SRC" symbolic-ref HEAD refs/heads/main

git -C "$SRC" add -A
T1="$(git -C "$SRC" write-tree)"
C1="$(git -C "$SRC" commit-tree "$T1" -m "fixture: initial import")"
git -C "$SRC" update-ref refs/heads/main "$C1"
git -C "$SRC" update-ref refs/remotes/origin/main "$C1"
git -C "$SRC" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
git -C "$SRC" remote add origin https://example.invalid/souji-case-F6.git

content_for ledger-match > "$SRC/src/heredoc-quorum-notes.md"
content_for not-exported > "$SRC/src/not-exported-notes.md"
content_for mismatch-source > "$SRC/src/hash-mismatch-notes.md"
content_for drift-source > "$SRC/src/vault-drift-notes.md"

git -C "$SRC" add -A
T2="$(git -C "$SRC" write-tree)"
C2="$(git -C "$SRC" commit-tree "$T2" -p "$C1" -m "fixture: export-prep notes")"
git -C "$SRC" update-ref refs/heads/export-prep "$C2"
git -C "$SRC" symbolic-ref HEAD refs/heads/export-prep

# --- fake vault -------------------------------------------------------------
content_for ledger-match > "$VAULT/heredoc-quorum-notes.md"
content_for not-exported > "$VAULT/not-exported-notes.md"
content_for mismatch-exported > "$VAULT/hash-mismatch-notes.md"
content_for drift-vault > "$VAULT/vault-drift-notes.md"
chmod 0444 -- "$VAULT"/*.md

# --- per-file verification (computed bytes vs declared constants) ----------
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
verify_file "$SRC/src/heredoc-quorum-notes.md" "$SHA_LEDGER_MATCH"
verify_file "$VAULT/heredoc-quorum-notes.md" "$SHA_LEDGER_MATCH"
verify_file "$SRC/src/not-exported-notes.md" "$SHA_NOT_EXPORTED"
verify_file "$VAULT/not-exported-notes.md" "$SHA_NOT_EXPORTED"
verify_file "$SRC/src/hash-mismatch-notes.md" "$SHA_MISMATCH_SOURCE"
verify_file "$VAULT/hash-mismatch-notes.md" "$SHA_MISMATCH_EXPORTED"
verify_file "$SRC/src/vault-drift-notes.md" "$SHA_DRIFT_SOURCE"
verify_file "$VAULT/vault-drift-notes.md" "$SHA_DRIFT_VAULT"

# --- injection payload ------------------------------------------------------
ledger_rows "$OUT" > "$OUT/ledger-inject.txt"
mkdir -p -- "$(dirname -- "$INJECT")"
cp -- "$OUT/ledger-inject.txt" "$INJECT"

# --- pushed-receipt probe (informational; proves the F6 gate is the ledger) -
INTRODUCING="$(git -C "$SRC" log --diff-filter=A --format=%H -1 -- src/heredoc-quorum-notes.md)"
PROBE="not-pushed"
if [ -z "$INTRODUCING" ]; then
  PROBE="none(introducing-commit-missing)"
elif git -C "$SRC" merge-base --is-ancestor "$INTRODUCING" refs/remotes/origin/main; then
  PROBE="pushed"
fi

if [ "$QUIET" = 1 ]; then
  printf 'FIXTURE_ROOT=%s\n' "$OUT"
  printf 'SOURCE_REPO=%s\n' "$SRC"
  printf 'VAULT_DIR=%s\n' "$VAULT"
  printf 'INJECT_FILE=%s\n' "$INJECT"
  printf 'TARGET=ledger-match:%s\n' "$SRC/src/heredoc-quorum-notes.md"
  printf 'TARGET=not-exported:%s\n' "$SRC/src/not-exported-notes.md"
  printf 'TARGET=source-hash-mismatch:%s\n' "$SRC/src/hash-mismatch-notes.md"
  printf 'TARGET=vault-hash-drift:%s\n' "$SRC/src/vault-drift-notes.md"
  printf 'PUSHED_PROBE=%s\n' "$PROBE"
  exit 0
fi

cat <<EOF
case-F6 fixture built — ledger-matched file qualifies SAFE(moved-to-obsidian)
only when a ledger row matches source path + source sha256 + vault path +
vault sha256 (all four).

FIXTURE_ROOT=$OUT
SOURCE_REPO=$SRC
VAULT_DIR=$VAULT
INJECT_FILE=$INJECT
EXPECTED_JSON=$EXPECTED_JSON
LEDGER_FILE=corpus/knowledge/obsidian-ledger.tsv  (lane-relative)
GIT_OBJECTS=initial=$C1 export-prep=$C2

TARGETS (evaluate by the exact absolute path shown; disarmed = no ledger row)
  ledger-match          $SRC/src/heredoc-quorum-notes.md
      armed SAFE(moved-to-obsidian) | disarmed NOT-SAFE
  not-exported          $SRC/src/not-exported-notes.md
      armed NOT-SAFE (vault copy exists but no row) | disarmed NOT-SAFE
  source-hash-mismatch  $SRC/src/hash-mismatch-notes.md
      armed NOT-SAFE (row carries the pre-edit source hash) | disarmed NOT-SAFE
  vault-hash-drift      $SRC/src/vault-drift-notes.md
      armed NOT-SAFE (row carries the pre-drift vault hash) | disarmed NOT-SAFE

PUSHED_RECEIPT_PROBE=$PROBE (introducing commit $C2 sits on export-prep, not on
origin/main; origin/HEAD -> origin/main resolves to $C1)

ARM (runner only; this script never writes the live ledger)
  cd $LANE_ROOT
  cp corpus/knowledge/obsidian-ledger.tsv /tmp/case-F6-ledger.bak
  cat $INJECT >> corpus/knowledge/obsidian-ledger.tsv
DISARM
  cp /tmp/case-F6-ledger.bak corpus/knowledge/obsidian-ledger.tsv

The payload holds 3 tab-separated rows in the ledger column order
(source_path, source_sha256, vault_path, vault_sha256, exported_at, note);
the header row of the live ledger must not be duplicated.
EOF
