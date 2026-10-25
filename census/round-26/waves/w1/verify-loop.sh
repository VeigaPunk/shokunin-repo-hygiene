#!/usr/bin/env bash
# souji round 26 — post-integration verify loop (claims C1/C2/C3).
#
# Every counter, gate and census command below is transcribed from the FROZEN
# contract `.ufo/waves/round-26/preregistration.txt` (plus amendment 1, which
# corrected C2's K4 after-literal, and amendment 2, which reads C1's protected
# regions as byte-content spans). Do not "fix" a command here after a claim has
# scored: a wrong or gameable counter is an ATTACK report, never an edit.
#
# Read-only: creates, moves and deletes nothing. Every git call is read-only
# with GIT_OPTIONAL_LOCKS=0 and never fetches; the two committed-bytes tools are
# given the tip resolved at run time. Receipt verification hashes blobs only.
#
# Output: `CHECK <name> PASS|FAIL <raw value>` per command, then SUMMARY.
# Exit:   0 every check PASS · 1 at least one FAIL · 2 setup refusal.
#
# Usage:  bash /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/verify-loop.sh
#         SOUJI_LANE=<lane> bash verify-loop.sh    # for an exercised copy
set -u
export LC_ALL=C
export GIT_OPTIONAL_LOCKS=0

LANE=${SOUJI_LANE:-/home/vgpnk/Projects/shokunin/souji-shokunin}
FLEET=/home/vgpnk/Projects/shokunin
BASE=0eca7c8a5d10bcbfdae50d0c390d277deec63bfd
ROUND=26
ROUND_DATE=2026-10-25
EXPECT_ROWS=132
CENSUS=/home/vgpnk/Projects/shokunin/scripts/sources-census.sh

# receipts named by the prereg, each required to `verify=ok`
RECEIPTS="
census/round-26/records/c1-before.tsv
census/round-26/records/c1-after.tsv
census/round-26/records/c2-before.tsv
census/round-26/records/c2-after.tsv
census/round-26/records/c2-k4-base.tsv
census/round-26/records/c2-k4-after.tsv
census/round-26/records/c2-gate.tsv
census/round-26/records/c3-before.tsv
census/round-26/records/c3-after.tsv
"

checks=0
fails=0

refuse() { printf 'REFUSED %s\n' "$*" >&2; exit 2; }
is_num() { case $1 in '' | *[!0-9]*) return 1 ;; *) return 0 ;; esac; }

# replace newlines with ';' so a CHECK stays one line
flat() {
  local s
  s=$(printf '%s' "$1" | tr '\n' ';')
  printf '%s' "${s%;}"
}

# first whitespace-separated `key=value` -> value, from any line
kv() {
  printf '%s\n' "$1" | tr -s '[:space:]' '\n' | awk -F= -v k="$2" '$1==k{print substr($0, length(k)+2); exit}'
}

clip() {
  local s=$1 n=${2:-300}
  if [ "${#s}" -gt "$n" ]; then printf '%s...' "${s:0:n}"; else printf '%s' "$s"; fi
}

emit() { # <name> <PASS|FAIL> <raw...>
  checks=$((checks + 1))
  local raw
  raw=$(flat "$3")
  [ -n "$raw" ] || raw='(empty)'
  if [ "$2" = PASS ]; then
    printf 'CHECK %s PASS %s\n' "$1" "$raw"
  else
    fails=$((fails + 1))
    printf 'CHECK %s FAIL %s\n' "$1" "$raw"
  fi
}

# ---------------------------------------------------------------- setup -----
[ -d "$LANE" ] || refuse "lane not a directory: $LANE"
top=$(git -C "$LANE" rev-parse --show-toplevel 2>/dev/null) || refuse "not a git repository: $LANE"
[ "$(realpath -e -- "$top")" = "$(realpath -e -- "$LANE")" ] || refuse "git toplevel $top is not $LANE"
[ -f "$LANE/SCORECARD.md" ] || refuse "SCORECARD.md absent in $LANE"
cd "$LANE" || refuse "cannot cd $LANE"

tip=$(git -C "$LANE" rev-parse HEAD 2>/dev/null) || tip=""
if printf '%s' "$tip" | grep -qE '^[0-9a-f]{40}$'; then
  emit tip PASS "$tip"
else
  emit tip FAIL "tip=${tip:-none}"
  tip=""
fi

# Counters read the WORKTREE; the gate tools read COMMITTED bytes at --rev.
# Uncommitted edits to the claim bytes make those two views disagree, so a
# green counter over a dirty file is not a green claim.
dirty=$(git -C "$LANE" status --porcelain -- SCORECARD.md corpus/SOURCES.md corpus/README.md corpus/knowledge 2>&1)
if [ -z "$dirty" ]; then
  emit clean-claim-surfaces PASS "dirty=0"
else
  emit clean-claim-surfaces FAIL "dirty=$(clip "$(flat "$dirty")" 240)"
fi

# -------------------------------------------------------- the three counters
c1=$(bash census/round-26/c1-counter.sh 2>&1)
c1_rc=$?
c1_m=$(kv "$c1" markers)
c1_h=$(printf '%s\n' "$c1" | awk -F'=' '/^headings=/{sub(/^headings=/,""); print; exit}')
# K2's kill rule is an ORDER, not merely three ascending line numbers: the
# counter prints NR in file order, so the heading NAMES must read 25,24,23.
c1_order=$(grep -nE '^### Round (23|24|25) measurements' SCORECARD.md 2>/dev/null \
  | sed -E 's/^[0-9]+:### Round ([0-9]+) measurements.*/\1/' | tr '\n' ' ')
c1_order=${c1_order% }
c1_ok=1
[ "$c1_rc" -eq 0 ] || c1_ok=0
[ "$c1_m" = 0 ] || c1_ok=0
[ "$c1_order" = "25 24 23" ] || c1_ok=0
read -r -a h <<< "$c1_h"
if [ "$c1_ok" -eq 1 ]; then
  [ "${#h[@]}" -eq 3 ] || c1_ok=0
fi
if [ "$c1_ok" -eq 1 ]; then
  is_num "${h[0]}" && is_num "${h[1]}" && is_num "${h[2]}" || c1_ok=0
fi
if [ "$c1_ok" -eq 1 ]; then
  [ "${h[0]}" -lt "${h[1]}" ] && [ "${h[1]}" -lt "${h[2]}" ] || c1_ok=0
fi
if [ "$c1_ok" -eq 1 ]; then
  emit c1-counter PASS "rc=$c1_rc markers=$c1_m headings=$c1_h order=$c1_order"
else
  emit c1-counter FAIL "rc=$c1_rc markers=${c1_m:-none} headings=${c1_h:-none} order=${c1_order:-none}"
fi

c2=$(bash census/round-26/c2-counter.sh 2>&1)
c2_rc=$?
c2_g=$(kv "$c2" grounded_f1)
c2_r=$(kv "$c2" registry_rows)
if [ "$c2_rc" -eq 0 ] && [ "$c2_g" = 2 ] && [ "$c2_r" = "$EXPECT_ROWS" ]; then
  emit c2-counter PASS "rc=$c2_rc grounded_f1=$c2_g registry_rows=$c2_r"
else
  emit c2-counter FAIL "rc=$c2_rc grounded_f1=${c2_g:-none} registry_rows=${c2_r:-none} expect_grounded_f1=2 expect_rows=$EXPECT_ROWS"
fi

c3=$(bash census/round-26/c3-counter.sh 2>&1)
c3_rc=$?
c3_tool=$(kv "$c3" axis_check_tool)
c3_claims=$(kv "$c3" claims)
c3_flags=$(kv "$c3" flags)
c3_axrc=$(kv "$c3" axis_check_exit)
c3_cases=$(kv "$c3" cases)
c3_pass=$(kv "$c3" pass)
c3_ctl=$(kv "$c3" control)
c3_fxrc=$(kv "$c3" fixture_exit)
if [ "$c3_rc" -eq 0 ] && [ "$c3_tool" = present ] && [ "$c3_claims" = 3 ] && [ "$c3_flags" = 0 ] \
  && [ "$c3_axrc" = 0 ] && [ "$c3_cases" = 12 ] && [ "$c3_pass" = 12 ] \
  && [ "$c3_ctl" = FALSE-GREEN-REJECTED ] && [ "$c3_fxrc" = 0 ]; then
  emit c3-counter PASS "rc=$c3_rc tool=$c3_tool claims=$c3_claims flags=$c3_flags axis_check_exit=$c3_axrc cases=$c3_cases pass=$c3_pass control=$c3_ctl fixture_exit=$c3_fxrc"
else
  emit c3-counter FAIL "rc=$c3_rc tool=${c3_tool:-none} claims=${c3_claims:-none} flags=${c3_flags:-none} axis_check_exit=${c3_axrc:-none} cases=${c3_cases:-none} pass=${c3_pass:-none} control=${c3_ctl:-none} fixture_exit=${c3_fxrc:-none}"
fi

# ------------------------------------------------------------ C2 K2: gate ---
gate_out=$(python3 -B tools/souji-gate-check.py --root . --round-date "$ROUND_DATE" \
  --entries corpus/knowledge/git-auto-maintenance-trigger-set.md \
  corpus/knowledge/git-auto-maintenance-trigger-set-r23.md \
  --snapshot-dir census/round-26/sources \
  --slice census/round-26/records/empty-slice \
  --slice-verdicts census/round-26/records/empty-verdicts 2>&1)
gate_rc=$?
gate_e=$(kv "$gate_out" entries)
gate_ok=$(kv "$gate_out" ok)
gate_f=$(kv "$gate_out" fail)
if [ "$gate_rc" -eq 0 ] && [ "$gate_e" = 2 ] && [ "$gate_ok" = 2 ] && [ "$gate_f" = 0 ]; then
  emit c2-gate PASS "rc=$gate_rc entries=$gate_e ok=$gate_ok fail=$gate_f"
else
  gate_detail=$(printf '%s\n' "$gate_out" | grep -m1 '^FAIL' || true)
  [ -n "$gate_detail" ] || gate_detail=$(printf '%s\n' "$gate_out" | awk 'NF{print; exit}')
  emit c2-gate FAIL "rc=$gate_rc entries=${gate_e:-none} ok=${gate_ok:-none} fail=${gate_f:-none} first=$(clip "$(flat "$gate_detail")" 200)"
fi

# ------------------------------------------------------------ C2 K3: census --
k3_out=$("$CENSUS" validate --root "$FLEET" souji 2>&1)
k3_rc=$?
k3_err=$(printf '%s\n' "$k3_out" | awk -F'\t' '$2 ~ /^E[0-9]/{n++} END{print n+0}')
k3_warn=$(printf '%s\n' "$k3_out" | awk -F'\t' '$2 ~ /^W[0-9]/{n++} END{print n+0}')
k3_ok=$(printf '%s\n' "$k3_out" | awk -F'\t' '$2=="ok"{n++} END{print n+0}')
if [ "$k3_rc" -eq 0 ] && [ "$k3_err" -eq 0 ] && [ "$k3_ok" -ge 1 ]; then
  emit c2-k3 PASS "rc=$k3_rc ok=$k3_ok errors=$k3_err warnings=$k3_warn"
else
  emit c2-k3 FAIL "rc=$k3_rc ok=$k3_ok errors=$k3_err warnings=$k3_warn"
fi

# --------------------------------------------------- C2 K4: coverage agreement
if [ -n "$tip" ]; then
  k4_out=$(python3 -B tools/souji-coverage-agreement.py --root . --rev "$tip" --base-rev "$BASE" 2>&1)
  k4_rc=$?
else
  k4_out="tip unresolved"
  k4_rc=2
fi
k4_grounded=$(kv "$k4_out" grounded)
k4_mapped=$(kv "$k4_out" mapped)
k4_dangling=$(kv "$k4_out" dangling)
k4_mm=$(kv "$k4_out" mismatches)
k4_tested=$(kv "$k4_out" kill_tested)
k4_kv=$(kv "$k4_out" kill_violations)
if [ "$k4_rc" -eq 0 ] && [ "$k4_grounded" = 9 ] && [ "$k4_mapped" = 9 ] \
  && [ "$k4_dangling" = 0 ] && [ "$k4_mm" = 0 ] && [ "$k4_tested" = 7 ] && [ "$k4_kv" = 0 ]; then
  emit c2-k4 PASS "rc=$k4_rc grounded=$k4_grounded mapped=$k4_mapped dangling=$k4_dangling mismatches=$k4_mm kill_tested=$k4_tested kill_violations=$k4_kv"
else
  emit c2-k4 FAIL "rc=$k4_rc grounded=${k4_grounded:-none} mapped=${k4_mapped:-none} dangling=${k4_dangling:-none} mismatches=${k4_mm:-none} kill_tested=${k4_tested:-none} kill_violations=${k4_kv:-none} (expect 9/9/0/0/7/0)"
fi

# ---------------------------------------------------- landing gate, round 26 --
if [ -n "$tip" ]; then
  lg_out=$(python3 -B tools/souji-landing-gate.py --root . --rev "$tip" --round "$ROUND" \
    --base "$BASE" --fleet-root "$FLEET" 2>&1)
  lg_rc=$?
else
  lg_out="tip unresolved"
  lg_rc=2
fi
lg_find=$(kv "$lg_out" findings)
lg_reg=$(kv "$lg_out" checked_reg)
lg_reason=""
if [ "$lg_rc" -eq 2 ]; then
  lg_reason=$(printf '%s\n' "$lg_out" | grep -m1 '^COULD-NOT-EVALUATE' | awk -F'\t' '{print $2}')
fi
if [ "$lg_rc" -eq 0 ] && [ "$lg_find" = 0 ]; then
  emit landing-gate PASS "rc=$lg_rc findings=$lg_find checked_reg=$lg_reg"
else
  lg_first=$(printf '%s\n' "$lg_out" | awk -F'\t' '$1 !~ /^SUMMARY$/ && $1 != "" {print $1" "$2; exit}')
  emit landing-gate FAIL "rc=$lg_rc findings=${lg_find:-none} checked_reg=${lg_reg:-none}${lg_reason:+ reason=$lg_reason}${lg_first:+ first=$(clip "$(flat "$lg_first")" 200)}"
fi

# ------------------------------------- six manual SOURCES census greps + rows
# transcribed from CORPUS.md § Census (fleet root), run from the lane root
c_rows=$(grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md 2>&1)
if is_num "$c_rows" && [ "$c_rows" = "$EXPECT_ROWS" ]; then
  emit census-rows PASS "rows=$c_rows"
else
  emit census-rows FAIL "rows=$(clip "$(flat "$c_rows")" 120) expect=$EXPECT_ROWS"
fi

c_mal=$(awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' corpus/SOURCES.md 2>&1)
if [ "$c_mal" = 0 ]; then
  emit census-malformed PASS "malformed=$c_mal"
else
  emit census-malformed FAIL "malformed=$(clip "$(flat "$c_mal")" 120)"
fi

c_tier=$(awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md 2>&1)
c_tier_sum=$(printf '%s' "$c_tier" | tr -s '[:space:]' '\n' | awk -F= 'NF==2{n+=$2} END{print n+0}')
c_tier_bad=$(printf '%s' "$c_tier" | tr -s '[:space:]' '\n' | awk -F= 'NF==2 && $1 !~ /^[ABC]$/{print ($1=="" ? "EMPTY" : $1)}' | tr '\n' ' ')
c_tier_bad=${c_tier_bad% }
if [ "$c_tier_sum" = "$EXPECT_ROWS" ] && [ -z "$c_tier_bad" ]; then
  emit census-tier-hist PASS "tier=$c_tier sum=$c_tier_sum"
else
  emit census-tier-hist FAIL "tier=$(clip "$(flat "$c_tier")" 160) sum=$c_tier_sum bad_keys=${c_tier_bad:-none} expect_sum=$EXPECT_ROWS"
fi

c_status=$(awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md 2>&1)
c_status_sum=$(printf '%s' "$c_status" | tr -s '[:space:]' '\n' | awk -F= 'NF==2{n+=$2} END{print n+0}')
c_status_bad=$(printf '%s' "$c_status" | tr -s '[:space:]' '\n' | awk -F= 'NF==2 && $1 !~ /^(queued|mined|rejected)$/{print ($1=="" ? "EMPTY" : $1)}' | tr '\n' ' ')
c_status_bad=${c_status_bad% }
if [ "$c_status_sum" = "$EXPECT_ROWS" ] && [ -z "$c_status_bad" ]; then
  emit census-status-hist PASS "status=$c_status sum=$c_status_sum"
else
  emit census-status-hist FAIL "status=$(clip "$(flat "$c_status")" 160) sum=$c_status_sum bad_keys=${c_status_bad:-none} expect_sum=$EXPECT_ROWS"
fi

c_dup=$(awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' corpus/SOURCES.md 2>&1 | sort | uniq -d)
if [ -z "$c_dup" ]; then
  emit census-duplicate-ids PASS "duplicates=0"
else
  emit census-duplicate-ids FAIL "duplicates=$(clip "$(flat "$c_dup")" 160)"
fi

c_enum=$(awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {i=$2;k=$4;t=$5;s=$9; gsub(/[[:space:]]/,"",i); gsub(/[[:space:]]/,"",k); gsub(/[[:space:]]/,"",t); gsub(/[[:space:]]/,"",s); if (t !~ /^[ABC]$/) print "tier", i, t; if (s !~ /^(queued|mined|rejected)$/) print "status", i, s; if (k !~ /^(spec|docs|paper|code|tool|dataset|talk|book|community|own-work)$/) print "kind", i, k; if (t=="A" && k=="community") print "tier-inflation", i}' corpus/SOURCES.md 2>&1)
if [ -z "$c_enum" ]; then
  emit census-enum PASS "violations=0"
else
  emit census-enum FAIL "violations=$(clip "$(flat "$c_enum")" 200)"
fi

c_used=$(awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {s=$9; gsub(/[[:space:]]/,"",s); if (s=="mined") {n=split($12, a, /[,;]/); for (j=1;j<=n;j++) {p=a[j]; gsub(/^[[:space:]]+|[[:space:]]+$/,"",p); if (p!="" && p!="—") print p}}}' corpus/SOURCES.md 2>&1 | while read -r p; do [ -e "$p" ] || echo "missing: $p"; done)
if [ -z "$c_used" ]; then
  emit census-usedby PASS "missing=0"
else
  emit census-usedby FAIL "missing=$(clip "$(flat "$c_used")" 200)"
fi

# ------------------------------------------------ receipts: each verify=ok ---
r_ok=0
r_fail=0
r_missing=""
r_bad=""
for r in $RECEIPTS; do
  if [ ! -f "$r" ]; then
    r_fail=$((r_fail + 1))
    r_missing="$r_missing $(basename "$r")"
    continue
  fi
  if python3 -B tools/souji-receipt-run.py verify --root . "$r" >/dev/null 2>&1; then
    r_ok=$((r_ok + 1))
  else
    r_fail=$((r_fail + 1))
    r_bad="$r_bad $(basename "$r")"
  fi
done
if [ "$r_fail" -eq 0 ]; then
  emit receipts PASS "verify_ok=$r_ok fail=0"
else
  emit receipts FAIL "verify_ok=$r_ok fail=$r_fail unverified=${r_bad# }${r_missing:+ missing=${r_missing# }}"
fi

# ---------------------------------------------------------------- summary ----
printf 'SUMMARY checks=%s pass=%s fail=%s tip=%s\n' \
  "$checks" "$((checks - fails))" "$fails" "${tip:-none}"
[ "$fails" -eq 0 ] || exit 1
exit 0
