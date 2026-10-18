#!/usr/bin/env bash
# case-V2 selftest — proves the fixture encodes the V2 tamper expectation and
# that the expectation is discriminating in both directions.
#
# Checks:
#   T1  build invariants: source present, vault present 0444, vault digest is
#       the tamper digest (91d9f779...) with the SAME byte count as the source,
#       ledger = header + 3 rows, row vault_sha256 carries the export-time
#       digest (59bea10a...)
#   T2  substituted expected.json parses, has no placeholder left, and matches
#       the built paths and verdicts
#   T3  tool behavior on the primary tamper target: never VERIFIED/SAFE; the
#       reason/evidence must name a vault-side hash mismatch. The round-2 sha
#       is recognized and its exact class pinned (NOT-SAFE, obsidian=vault-sha-
#       mismatch in evidence); any other candidate is held to the r4
#       NOT-VERIFIED(vault-hash-mismatch) contract.
#   T4  tamper-direction control: restore the vault copy to the export-time
#       bytes and re-run — the same row must now verify (SAFE/VERIFIED), so the
#       case cannot pass by answering mismatch unconditionally.
#   T5  live surfaces untouched: corpus/knowledge/obsidian-ledger.tsv still
#       header-only and unchanged; the real vault is never read from or
#       written to.
#
# Usage: bash selftest.sh [--keep] [--out JSON] [--tool PATH]
#   default: fresh mktemp -d fixture, reaped on exit; exit 0 all pass, 1 fail.
set -euo pipefail
export LC_ALL=C

here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
lane=$(cd -- "$here/../../.." && pwd)
tool="$lane/tools/souji-verify.sh"
live_ledger="$lane/corpus/knowledge/obsidian-ledger.tsv"

SHA_TAMPER_SOURCE=59bea10a81540fd2252880d03f32ce22761d82b997ca276f58150223c1a90bd7
SHA_TAMPER_VAULT=91d9f779647195141205fd585456e4bfbaef72f6ceef89c9c95375eddcf997e4
SHA_SUBTLE_SOURCE=a0d7a278477b87ea36f42d1ad27bd777ee791f1594200500f172c2b7b7344b96
SHA_SUBTLE_VAULT=f1ebc6ec0aa343dd04c172a2e3f47ee603ad28ceae27243fa9a79b93e03b7423
SHA_MATCHED=2aa2322dc2298a6dba5f7005108ef4a196ce59f94ef0ee98600b2c70640f277b
R2_SHA=7efda63bd7607009f98604356baf2fabeff1e3d8ca2b946be47bf22cd32c6820

keep=0
out_json=""
while [ $# -gt 0 ]; do
  case "$1" in
    --keep) keep=1; shift ;;
    --out) out_json=$2; shift 2 ;;
    --tool) tool=$2; shift 2 ;;
    -h|--help) sed -n '2,24p' "$0"; exit 0 ;;
    *) echo "usage: selftest.sh [--keep] [--out JSON] [--tool PATH]" >&2; exit 2 ;;
  esac
done

tmp=$(mktemp -d "${TMPDIR:-/tmp}/case-V2-selftest.XXXXXX")
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
ck_ok() { # ck_ok NAME CONDITION
  if [ "$2" = 0 ]; then
    pass=$((pass+1)); results+=("PASS	$1	ok")
  else
    fail=$((fail+1)); results+=("FAIL	$1	condition-false")
  fi
}

live_before=$(sha256sum -- "$live_ledger" | cut -d' ' -f1 2>/dev/null || echo absent)
live_rows_before=$(wc -l < "$live_ledger" 2>/dev/null || echo 0)

# --- T1: build invariants ---------------------------------------------------
root="$tmp/root"
bash "$here/make-fixture.sh" --out "$root" --quiet > "$tmp/build.out" 2> "$tmp/build.err"
src="$root/source/src/tamper-notes.md"
vault="$root/vault/tamper-notes.md"
src_subtle="$root/source/src/subtle-notes.md"
vault_subtle="$root/vault/subtle-notes.md"
src_matched="$root/source/src/matched-notes.md"
vault_matched="$root/vault/matched-notes.md"
ledger="$root/ledger.tsv"

ck T1.source_present yes "$([ -f "$src" ] && echo yes || echo no)"
ck T1.source_digest "$SHA_TAMPER_SOURCE" "$(sha256sum -- "$src" | cut -d' ' -f1)"
ck T1.vault_present yes "$([ -f "$vault" ] && echo yes || echo no)"
ck T1.vault_mode 444 "$(stat -c %a "$vault")"
ck T1.vault_digest "$SHA_TAMPER_VAULT" "$(sha256sum -- "$vault" | cut -d' ' -f1)"
ck T1.same_byte_count "$(wc -c < "$src")" "$(wc -c < "$vault")"
ck T1.subtle_one_byte_shorter "$(( $(wc -c < "$src_subtle") - $(wc -c < "$vault_subtle") ))" 1
ck T1.control_byte_identical "$SHA_MATCHED/$SHA_MATCHED" \
  "$(sha256sum -- "$src_matched" | cut -d' ' -f1)/$(sha256sum -- "$vault_matched" | cut -d' ' -f1)"
ck T1.ledger_lines 4 "$(wc -l < "$ledger")"
ck T1.marker yes "$([ -f "$root/.case-V2-fixture" ] && echo yes || echo no)"

row_vs=$(awk -F'\t' -v p="$vault" '$3==p{print $4}' "$ledger")
row_ss=$(awk -F'\t' -v p="$src" '$1==p{print $2}' "$ledger")
ck T1.row_source_sha "$SHA_TAMPER_SOURCE" "$row_ss"
ck T1.row_vault_sha_is_export_time "$SHA_TAMPER_SOURCE" "$row_vs"
ck_ok T1.row_vault_sha_differs_from_actual "$([ "$row_vs" != "$SHA_TAMPER_VAULT" ] && echo 0 || echo 1)"

# --- T2: substituted expected.json -----------------------------------------
exp="$root/expected.json"
ck T2.expected_present yes "$([ -f "$exp" ] && echo yes || echo no)"
python3 - "$exp" "$src" "$vault" "$ledger" <<'PY' && t2=0 || t2=1
import json, sys
d = json.load(open(sys.argv[1]))
assert d["case"] == "case-V2", d["case"]
assert d["schema"] == "souji-vault-fixture/1", d.get("schema")
assert "@FIXTURE_ROOT@" not in json.dumps(d), "placeholder left"
assert d["ledger"] == sys.argv[4], d["ledger"]
assert d["targets"][0] == sys.argv[2], d["targets"]
assert d["expect"][0]["path"] == sys.argv[2]
assert d["expect"][0]["vault_path"] == sys.argv[3]
assert d["expect"][0]["verdict"] == "NOT-VERIFIED"
assert d["expect"][0]["reason"] == "vault-hash-mismatch"
assert d["expect_string"] == "NOT-VERIFIED(vault-hash-mismatch)"
assert d["expect"][1]["reason"] == "vault-hash-mismatch"
assert d["expect"][2]["verdict"] == "VERIFIED"
assert d["declared_ledger_rows"][0]["source_path"] == sys.argv[2]
assert d["vault_side"]["tamper_notes"]["sha256_actual"] != d["vault_side"]["tamper_notes"]["sha256_recorded_in_row"]
PY
ck T2.expected_matches_build 0 "$t2"

# --- T3/T4: tool behavior ---------------------------------------------------
if [ -x "$tool" ] || [ -f "$tool" ]; then
  tool_sha=$(sha256sum -- "$tool" | cut -d' ' -f1)

  line=$(SOUJI_LEDGER="$ledger" SHOKUNIN_ROOT="$root" bash "$tool" "$src" 2>/dev/null | head -1 || true)
  verdict=$(printf '%s' "$line" | awk -F'\t' '{print $3}')
  reason=$(printf '%s' "$line" | awk -F'\t' '{print $4}')
  evidence=$(printf '%s' "$line" | cut -f5-)

  case "$verdict" in SAFE|VERIFIED) ck T3.no_false_verified fail pass ;; *) ck T3.no_false_verified pass pass ;; esac
  # the vault-side mismatch must be visible somewhere in reason or evidence
  if printf '%s %s' "$reason" "$evidence" | grep -qiE 'vault[-_]?(hash|sha|digest)[-_]?mismatch|vault[-_]?(hash|sha|digest)[-_]?drift'; then
    ck T3.vault_mismatch_named yes yes
  else
    ck T3.vault_mismatch_named yes "no (line: $line)"
  fi

  if [ "$tool_sha" = "$R2_SHA" ]; then
    # Measured 2026-10-18: the round-2 tool classifies the tamper as
    # NOT-SAFE(none) with obsidian=vault-sha-mismatch in the evidence field;
    # it cannot express NOT-VERIFIED(vault-hash-mismatch). That is the delta
    # the r4 vault harness must close.
    ck T3.r2_verdict NOT-SAFE "$verdict"
    ck T3.r2_evidence_substr yes "$(printf '%s' "$evidence" | grep -q 'vault-sha-mismatch' && echo yes || echo no)"
  else
    ck T3.r4_verdict NOT-VERIFIED "$verdict"
    case "$reason" in
      vault-hash-mismatch|vault-sha-mismatch|vault-digest-mismatch|vault-hash-drift) ck T3.r4_reason ok ok ;;
      *) ck T3.r4_reason "vault-*-mismatch" "$reason" ;;
    esac
  fi

  # control: the matched pair must still verify
  linec=$(SOUJI_LEDGER="$ledger" SHOKUNIN_ROOT="$root" bash "$tool" "$src_matched" 2>/dev/null | head -1 || true)
  vc=$(printf '%s' "$linec" | awk -F'\t' '{print $3}')
  case "$vc" in SAFE|VERIFIED) ck T3.control_verified pass pass ;; *) ck T3.control_verified "SAFE|VERIFIED" "$vc" ;; esac

  # --- T4: tamper-direction control -----------------------------------------
  # Rewrite the vault copy with the export-time bytes; the same row must now
  # verify, so the case cannot pass by answering mismatch unconditionally.
  chmod 0644 -- "$vault"
  cp -- "$src" "$vault"
  chmod 0444 -- "$vault"
  ck T4.vault_restored "$SHA_TAMPER_SOURCE" "$(sha256sum -- "$vault" | cut -d' ' -f1)"
  line2=$(SOUJI_LEDGER="$ledger" SHOKUNIN_ROOT="$root" bash "$tool" "$src" 2>/dev/null | head -1 || true)
  v2=$(printf '%s' "$line2" | awk -F'\t' '{print $3}')
  r2=$(printf '%s' "$line2" | awk -F'\t' '{print $4}')
  case "$v2" in SAFE|VERIFIED) ck T4.control_verified pass pass ;; *) ck T4.control_verified "SAFE|VERIFIED" "$v2" ;; esac
  if printf '%s' "$r2" | grep -qiE 'mismatch|drift'; then
    ck T4.control_not_mismatch "no mismatch reason" "$r2"
  else
    ck T4.control_not_mismatch "no mismatch reason" "no mismatch reason"
  fi
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
    printf '{\n  "case": "case-V2",\n  "fixture_root": "%s",\n  "pass": %d,\n  "fail": %d,\n  "results": [\n' "$root" "$pass" "$fail"
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
