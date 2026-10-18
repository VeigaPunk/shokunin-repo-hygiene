#!/usr/bin/env bash
# case-V4 selftest — proves the fixture encodes the V4 expectation and that
# the expectation is discriminating.
#
# Checks:
#   T1  build invariants: vault absent (parent present), source present 0444,
#       source digest == row source_sha256 == row vault_sha256 == fixed
#       constant, ledger = header+1 row
#   T2  substituted expected.json parses and matches the built paths
#   T3  class-collapse gap: the round-2 tool (tools/souji-verify.sh) pointed at
#       the fixture ledger reports NOT-SAFE(none) with an
#       obsidian=vault-unreachable note — i.e. it cannot express
#       NOT-VERIFIED(vault-absent); this is the delta the r4 vault harness
#       must close, and the case fails if the tool ever reports SAFE/VERIFIED
#   T4  false-vault-absent control: materialize the vault file (byte-identical
#       to the source copy) and re-run; the same row must now verify —
#       SAFE(moved-to-obsidian) — so the case cannot pass by always answering
#       vault-absent
#   T5  live surfaces untouched: corpus/knowledge/obsidian-ledger.tsv still
#       header-only (and unchanged), real vault not read from or written to
#
# Usage: bash selftest.sh [--keep] [--out JSON]
#   default: fresh mktemp -d fixture, reaped on exit; exit 0 all pass, 1 fail.
set -euo pipefail
export LC_ALL=C

here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
lane=$(cd -- "$here/../../.." && pwd)
tool="$lane/tools/souji-verify.sh"
live_ledger="$lane/corpus/knowledge/obsidian-ledger.tsv"

keep=0
out_json=""
while [ $# -gt 0 ]; do
  case "$1" in
    --keep) keep=1; shift ;;
    --out) out_json=$2; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "usage: selftest.sh [--keep] [--out JSON]" >&2; exit 2 ;;
  esac
done

tmp=$(mktemp -d "${TMPDIR:-/tmp}/case-V4-selftest.XXXXXX")
cleanup() { [ "$keep" = 1 ] || rm -rf -- "$tmp"; }
trap cleanup EXIT

pass=0; fail=0; results=()
ck() { # ck NAME EXPECTED ACTUAL
  if [ "$2" = "$3" ]; then
    pass=$((pass+1)); results+=("PASS	$1	$3")
  else
    fail=$((fail+1)); results+=("FAIL	$1	want=$2 got=$3")
  fi
}

live_before=$(sha256sum -- "$live_ledger" | cut -d' ' -f1 2>/dev/null || echo absent)
live_rows_before=$(wc -l < "$live_ledger" 2>/dev/null || echo 0)

# --- T1: build invariants ---------------------------------------------------
root="$tmp/root"
bash "$here/make-fixture.sh" --out "$root" --quiet > "$tmp/build.out" 2> "$tmp/build.err"
src="$root/source/round-trip-notes.md"
vault="$root/vault/round-trip-notes.md"
ledger="$root/ledger.tsv"

ck T1.vault_absent no "$([ -e "$vault" ] && echo yes || echo no)"
ck T1.vault_parent_present yes "$([ -d "$root/vault" ] && echo yes || echo no)"
ck T1.source_present yes "$([ -f "$src" ] && echo yes || echo no)"
ck T1.source_mode 444 "$(stat -c %a "$src")"
ck T1.source_digest \
  d9cae6dfd163e93e34fcc1c9d90a3b910160a3fb2981b7dc2741ba3bdbe3ab2d \
  "$(sha256sum -- "$src" | cut -d' ' -f1)"
ck T1.ledger_lines 2 "$(wc -l < "$ledger")"
ck T1.marker yes "$([ -f "$root/.case-V4-fixture" ] && echo yes || echo no)"

row_sp=$(awk -F'\t' 'NR==2{print $1}' "$ledger")
row_ss=$(awk -F'\t' 'NR==2{print $2}' "$ledger")
row_vp=$(awk -F'\t' 'NR==2{print $3}' "$ledger")
row_vs=$(awk -F'\t' 'NR==2{print $4}' "$ledger")
ck T1.row_source_path "$src" "$row_sp"
ck T1.row_vault_path "$vault" "$row_vp"
ck T1.row_source_sha "$(sha256sum -- "$src" | cut -d' ' -f1)" "$row_ss"
ck T1.row_vault_sha "$(sha256sum -- "$src" | cut -d' ' -f1)" "$row_vs"

# --- T2: substituted expected.json -----------------------------------------
exp="$root/expected.json"
ck T2.expected_present yes "$([ -f "$exp" ] && echo yes || echo no)"
python3 - "$exp" "$src" "$vault" <<'PY' && t2=0 || t2=1
import json, sys
d = json.load(open(sys.argv[1]))
assert d["case"] == "case-V4", d["case"]
assert "@FIXTURE_ROOT@" not in json.dumps(d), "placeholder left"
assert d["targets"] == [sys.argv[2]], d["targets"]
assert d["expect"][0]["path"] == sys.argv[2]
assert d["expect"][0]["vault_path"] == sys.argv[3]
assert d["expect"][0]["verdict"] == "NOT-VERIFIED"
assert d["expect"][0]["reason"] == "vault-absent"
assert d["expect_string"] == "NOT-VERIFIED(vault-absent)"
assert d["declared_ledger_rows"][0]["source_path"] == sys.argv[2]
assert d["declared_ledger_rows"][0]["vault_path"] == sys.argv[3]
# substring-veto self-collision guard: bare VERIFIED must not be in
# must_not_be, because runner-26/28 apply must_not_be tokens as substrings
# and "VERIFIED" is a substring of the correct answer "NOT-VERIFIED(...)".
assert "VERIFIED" not in d.get("must_not_be", []), d.get("must_not_be")
assert "NOT-VERIFIED(vault-absent)" not in d.get("must_not_be", []), d.get("must_not_be")
for _tok in d.get("must_not_be", []):
    assert _tok not in d["expect_string"], f"must_not_be token {_tok!r} collides with correct answer"
PY
ck T2.expected_matches_build 0 "$t2"

# --- T3: round-2 tool behavior (class-collapse gap) -------------------------
if [ -x "$tool" ] || [ -f "$tool" ]; then
  line=$(SOUJI_LEDGER="$ledger" SHOKUNIN_ROOT="$root" bash "$tool" "$src" 2>/dev/null | head -1 || true)
  verdict=$(printf '%s' "$line" | awk -F'\t' '{print $3}')
  reason=$(printf '%s' "$line" | awk -F'\t' '{print $4}')
  evidence=$(printf '%s' "$line" | awk -F'\t' '{print $5}')
  ck T3.round2_verdict NOT-SAFE "$verdict"
  # The round-2 tool has no vault-absent class: the ledger row's vault path
  # fails its file test and the row is skipped, ending at NOT-SAFE(none) with
  # an obsidian=vault-unreachable note (observed 2026-10-18, tools/souji-verify.sh,
  # fixture root /tmp/souji-fixture-case-V4.*). That is precisely the
  # class-collapse the r4 vault harness must refine into
  # NOT-VERIFIED(vault-absent) by distinguishing "vault path absent" from
  # "no receipt at all".
  ck T3.round2_reason none "$reason"
  case "$evidence" in
    *vault-unreachable*) ck T3.round2_note_vault_unreachable yes yes ;;
    *) ck T3.round2_note_vault_unreachable yes "$evidence" ;;
  esac
  # never SAFE/VERIFIED for a vault-absent row
  case "$verdict" in SAFE|VERIFIED) ck T3.no_false_verified fail pass ;; *) ck T3.no_false_verified pass pass ;; esac

  # --- T4: false-vault-absent control ---------------------------------------
  cp -- "$src" "$vault"
  chmod 0444 -- "$vault"
  ck T4.vault_materialized yes "$([ -f "$vault" ] && echo yes || echo no)"
  ck T4.vault_sha_matches_row yes \
    "$([ "$(sha256sum -- "$vault" | cut -d' ' -f1)" = "$row_vs" ] && echo yes || echo no)"
  line2=$(SOUJI_LEDGER="$ledger" SHOKUNIN_ROOT="$root" bash "$tool" "$src" 2>/dev/null | head -1 || true)
  v2=$(printf '%s' "$line2" | awk -F'\t' '{print $3}')
  r2=$(printf '%s' "$line2" | awk -F'\t' '{print $4}')
  ck T4.control_verdict SAFE "$v2"
  ck T4.control_receipt moved-to-obsidian "$r2"
else
  ck T3.tool_present yes no
fi

# --- T5: live surfaces untouched -------------------------------------------
live_after=$(sha256sum -- "$live_ledger" | cut -d' ' -f1 2>/dev/null || echo absent)
live_rows_after=$(wc -l < "$live_ledger" 2>/dev/null || echo 0)
ck T5.live_ledger_unchanged "$live_before" "$live_after"
ck T5.live_ledger_rows "$live_rows_before" "$live_rows_after"
ck T5.live_ledger_header_only 1 "$live_rows_after"

printf '%s\n' "${results[@]}"
printf 'SELFTEST %s pass=%d fail=%d fixture_root=%s\n' \
  "$([ "$fail" = 0 ] && echo PASS || echo FAIL)" "$pass" "$fail" "$root"

if [ -n "$out_json" ]; then
  {
    printf '{\n  "case": "case-V4",\n  "fixture_root": "%s",\n  "pass": %d,\n  "fail": %d,\n  "results": [\n' "$root" "$pass" "$fail"
    first=1
    for r in "${results[@]}"; do
      st=${r%%	*}; rest=${r#*	}; nm=${rest%%	*}; dt=${rest#*	}
      [ "$first" = 1 ] || printf ',\n'
      first=0
      printf '    {"status": "%s", "check": "%s", "detail": "%s"}' "$st" "$nm" "$dt"
    done
    printf '\n  ]\n}\n'
  } > "$out_json"
fi

[ "$fail" = 0 ]
