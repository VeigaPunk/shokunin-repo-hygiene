#!/usr/bin/env bash
# cand-census-07.sh — round 11, seat S07 (census fix implementor).
#
# Reproduces and verifies the fix for the three cert-16 unsafe cases, all of
# one root cause: souji-census.sh --compare accepted an empty / blank-only /
# headerless prior census as a clean "no diff" baseline (exit 0), violating
# the fail-closed contract (rubric-final.md OPS08; K10 comparison:
# "malformed baseline" must refuse).
#
#   cert-16 final22/empty-census-compare  (census-rc=0, census_ok=false)
#   cert-16 s16-fresh/J14                 (zero-byte prior, exit_expected
#                                          nonzero, exit_actual=0)
#   cert-16 s16-fresh/V07                 (prior bytes "\n", exit_actual=0)
#
# The fix lives in load_census(): a header line is REQUIRED. Blank lines
# before the header no longer consume position 1; after the read loop,
# saw_header=0 is a usage error (exit 2). Header-only baselines, wrong
# headers, missing files, and real-fleet diff exits are unchanged.
#
# Usage:
#   cand-census-07.sh            run the full battery (default)
#   cand-census-07.sh --shas     print frozen-before/frozen-after shas
#   cand-census-07.sh --selftest run the fixed census's built-in selftest
#
# Fixtures are created ONLY under mktemp -p /var/tmp (host /tmp disk quota).
# The live lane is read for hashes and never written.
set -uo pipefail

LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
FROZEN_BEFORE_SHA=11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381
FROZEN_AFTER_SHA=3f9f85f064fec55a499376a536a6e9b2bd9f6ad8e5836ab93b44c13dd4c631ac

WORK=${S07_WORK:-/var/tmp/s07-work}
FROZEN=$WORK/census-frozen.sh
FIXED=$WORK/census-fixed.sh

export TMPDIR=/var/tmp
LC_ALL=C
export LC_ALL

PASS=0
FAIL=0
ok() { PASS=$((PASS + 1)); printf 'PASS %s\n' "$*"; }
bad() { FAIL=$((FAIL + 1)); printf 'FAIL %s\n' "$*"; }
chk_rc() { # $1 label, $2 want, $3 got
  if [ "$3" = "$2" ]; then ok "$1 (rc=$3)"; else bad "$1 want-rc=$2 got-rc=$3"; fi
}
mkf() { mktemp -d -p /var/tmp s07-cand-XXXXXXXX; }
clean() { rm -rf -- "$1"; }

freeze() {
  mkdir -p "$WORK"
  if [ ! -f "$FROZEN" ]; then
    cp -- "$LANE/tools/souji-census.sh" "$FROZEN"
    chmod +x "$FROZEN"
  fi
  if [ ! -f "$FIXED" ]; then
    printf 'cand-census-07: fixed census bytes missing: %s\n' "$FIXED" >&2
    printf '  generate them with the seat-07 patch (load_census header-required) first\n' >&2
    exit 1
  fi
  chmod +x "$FIXED" 2>/dev/null || true
}

print_shas() {
  printf 'frozen-before  %s  (%s)\n' "$FROZEN_BEFORE_SHA" \
    "$(sha256sum -- "$LANE/tools/souji-census.sh" | cut -d' ' -f1)"
  printf 'frozen-after   %s  (%s)\n' "$FROZEN_AFTER_SHA" "$(sha256sum -- "$FIXED" | cut -d' ' -f1)"
}

# --- the three cert-16 unsafe cases, against the FIXED bytes ----------------

repro_j14() { # zero-byte prior, empty fleet root -> must NOT exit 0
  local B rc
  B=$(mkf)
  mkdir -p "$B/empty-fleet"
  : > "$B/empty-prior.tsv"
  bash "$FIXED" --root "$B/empty-fleet" --compare "$B/empty-prior.tsv" \
    > "$B/out" 2> "$B/err"
  rc=$?
  chk_rc "J14 zero-byte-prior refuses" 2 "$rc"
  if grep -q 'compare file is empty or has no census header' "$B/err"; then
    ok "J14 refusal names the empty baseline"
  else
    bad "J14 refusal text missing: $(head -1 "$B/err")"
  fi
  # usage_err prints the usage block to stdout (pre-existing behavior for all
  # usage errors); what must NOT appear is a diff TSV (no header row).
  if grep -q $'^repo\tfield\tbefore\tafter\tchange$' "$B/out"; then
    bad "J14 emitted a diff TSV on stdout (want none)"
  else
    ok "J14 emitted no diff TSV on stdout"
  fi
  clean "$B"
}

repro_v07() { # prior bytes "\n" -> must NOT exit 0
  local B rc
  B=$(mkf)
  mkdir -p "$B/empty-fleet"
  printf '\n' > "$B/near-empty.tsv"
  bash "$FIXED" --root "$B/empty-fleet" --compare "$B/near-empty.tsv" \
    > "$B/out" 2> "$B/err"
  rc=$?
  chk_rc "V07 newline-only-prior refuses" 2 "$rc"
  if grep -q 'compare file is empty or has no census header' "$B/err"; then
    ok "V07 refusal names the empty baseline"
  else
    bad "V07 refusal text missing: $(head -1 "$B/err")"
  fi
  clean "$B"
}

repro_final22() { # the final-22 recipe, judged on census-rc like the certifier
  local B rc
  B=$(mkf)
  mkdir "$B/empty-root"
  : > "$B/empty.tsv"
  bash "$FIXED" --root "$B/empty-root" --compare "$B/empty.tsv" >/dev/null 2>&1
  rc=$?
  if [ "$rc" != 0 ]; then
    ok "final22 empty-census-compare census-rc=$rc (nonzero, census_ok=true)"
  else
    bad "final22 empty-census-compare census-rc=0 (census_ok=false)"
  fi
  clean "$B"
}

# --- regression: the contract's non-violating paths are unchanged -----------

regress_battery() {
  local B rc
  # header-only prior vs empty fleet: exit 0, header-only diff
  B=$(mkf); mkdir "$B/r"
  printf 'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags\n' \
    > "$B/p.tsv"
  bash "$FIXED" --root "$B/r" --compare "$B/p.tsv" > "$B/out" 2>/dev/null
  rc=$?
  chk_rc "hdr-only-vs-empty-fleet" 0 "$rc"
  if [ "$(cat "$B/out")" = "repo	field	before	after	change" ]; then
    ok "hdr-only diff is header-only"
  else
    bad "hdr-only diff not header-only: $(cat "$B/out")"
  fi
  clean "$B"

  # header + blank lines + no rows vs empty fleet: exit 0
  B=$(mkf); mkdir "$B/r"
  printf 'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags\n\n\n' \
    > "$B/p.tsv"
  bash "$FIXED" --root "$B/r" --compare "$B/p.tsv" >/dev/null 2>&1
  rc=$?
  chk_rc "hdr+blanks-vs-empty" 0 "$rc"
  clean "$B"

  # blank-only prior (3 blank lines): exit 2
  B=$(mkf); mkdir "$B/r"; printf '\n\n\n' > "$B/p.tsv"
  bash "$FIXED" --root "$B/r" --compare "$B/p.tsv" >/dev/null 2>&1
  rc=$?
  chk_rc "blank-only-prior" 2 "$rc"
  clean "$B"

  # CRLF blank-only prior: exit 2
  B=$(mkf); mkdir "$B/r"; printf '\r\n\r\n' > "$B/p.tsv"
  bash "$FIXED" --root "$B/r" --compare "$B/p.tsv" >/dev/null 2>&1
  rc=$?
  chk_rc "crlf-blank-prior" 2 "$rc"
  clean "$B"

  # wrong header: exit 2 (pre-existing)
  B=$(mkf); mkdir "$B/r"; printf 'nope\n' > "$B/p.tsv"
  bash "$FIXED" --root "$B/r" --compare "$B/p.tsv" >/dev/null 2>&1
  rc=$?
  chk_rc "wrong-header" 2 "$rc"
  clean "$B"

  # missing file: exit 2 (pre-existing)
  B=$(mkf); mkdir "$B/r"
  bash "$FIXED" --root "$B/r" --compare "$B/absent.tsv" >/dev/null 2>&1
  rc=$?
  chk_rc "missing-file" 2 "$rc"
  clean "$B"

  # real fleet vs header-only prior: exit 3 (added rows)
  B=$(mkf); mkdir -p "$B/fleet/r1"; git init -q -b main "$B/fleet/r1"
  printf 'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags\n' \
    > "$B/p.tsv"
  bash "$FIXED" --root "$B/fleet" --compare "$B/p.tsv" >/dev/null 2>&1
  rc=$?
  chk_rc "hdr-only-vs-real-fleet" 3 "$rc"
  clean "$B"

  # leading blank line then header then rows: tolerated, exit 3
  B=$(mkf); mkdir -p "$B/fleet/r1"; git init -q -b main "$B/fleet/r1"
  printf '\nrepo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags\n' \
    > "$B/p.tsv"
  bash "$FIXED" --root "$B/fleet" --compare "$B/p.tsv" >/dev/null 2>&1
  rc=$?
  chk_rc "leading-blank-then-hdr" 3 "$rc"
  clean "$B"

  # self-compare on an empty root: exit 0
  B=$(mkf)
  bash "$FIXED" --root "$B" > "$B/c.tsv" 2>/dev/null
  bash "$FIXED" --root "$B" --compare "$B/c.tsv" >/dev/null 2>&1
  rc=$?
  chk_rc "self-compare-empty-root" 0 "$rc"
  clean "$B"
}

# --- built-in selftest on the fixed bytes -----------------------------------

builtin_selftest() {
  local out rc
  out=$(bash "$FIXED" --selftest 2>&1)
  rc=$?
  chk_rc "built-in selftest exit" 0 "$rc"
  if printf '%s' "$out" | grep -q 'selftest: 32 checks, 0 failed'; then
    ok "built-in selftest 32 checks, 0 failed"
  else
    bad "built-in selftest tail: $(printf '%s' "$out" | tail -1)"
  fi
}

# --- the defect must exist on the frozen-before bytes (fresh repro) ---------

defect_on_frozen() {
  local B rc
  B=$(mkf); mkdir "$B/r"; : > "$B/p.tsv"
  bash "$FROZEN" --root "$B/r" --compare "$B/p.tsv" >/dev/null 2>&1
  rc=$?
  if [ "$rc" = 0 ]; then
    ok "frozen-before bytes show the defect (empty prior accepted, rc=0)"
  else
    bad "frozen-before bytes do NOT show the defect (rc=$rc) — repro stale"
  fi
  clean "$B"
}

# --- main -------------------------------------------------------------------

case "${1:-}" in
  --shas) print_shas; exit 0 ;;
esac

freeze

printf 'cand-census-07 — cert-16 census-empty-compare fix verification\n'
printf 'frozen-before %s\n' "$FROZEN_BEFORE_SHA"
printf 'frozen-after  %s\n' "$(sha256sum -- "$FIXED" | cut -d' ' -f1)"
if [ "$(sha256sum -- "$FIXED" | cut -d' ' -f1)" != "$FROZEN_AFTER_SHA" ]; then
  printf 'cand-census-07: WARNING fixed bytes differ from frozen-after sha\n' >&2
fi
printf '\n'

defect_on_frozen
repro_j14
repro_v07
repro_final22
regress_battery
builtin_selftest

printf '\ncand-census-07: %d checks, %d failed\n' "$((PASS + FAIL))" "$FAIL"
if [ "$FAIL" -gt 0 ]; then exit 1; fi
exit 0
