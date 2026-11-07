#!/usr/bin/env bash
# souji r76 wave-repair tally probes (L1), computed verdicts. Usage: tally-probes.sh TALLY_I TALLY_R LANE
# Each arm runs a tally over the r75 honest set with ONE slot replaced; exit 0 = accepted, 1 = rejected.
#   selftest-off: X09 slot = the X09 receipt with its command= flag renamed --selftest-off (S76Reviewer LOW:
#     substring test). Expected I=accept (false green), R=reject.
#   selftest-moved: X09 slot = S76ExecC2's F3 receipt: --selftest moved after the --work path. As an unquoted
#     argv line it still carries a whole --selftest token, so both tallies accept; rec.sh's command= line loses
#     quoting, so a flag inside a quoted path cannot be told from a real one (stated limit, not repaired).
#   by-name: X09 slot = M08's receipt bytes under the file name c2-after-X09-selftest.txt (S76CriticClaims'
#     filename-cheat separability case). Expected I=reject and R=reject (binding reads bytes, not names).
#   honest: the r75 set unchanged. Expected I=accept, R=accept.
# Prints ROW lines and SUMMARY arms=<n> as_expected=<k>; exit 0 iff all as expected.
set -u
TI=${1:?usage}; TR=${2:?usage}; L=${3:?usage}
r=$L/census/round-75/records; w=$L/census/round-76/records/wave-repair/cases
n=0 ok=0
run() {  # run TALLY X09-RECEIPT
  python3 -B "$1" --counter "$L/census/round-75/c1-counter.py" --edits "$L/census/round-75/c2-mutants.json" \
    --edits "$L/census/round-74/c2-survivors.json" --pristine "$r/c2-after-pristine-selftest.txt" \
    --mutant "X09=$2" --mutant "P1=$r/c2-after-P1-selftest.txt" --mutant "M08=$r/c2-after-M08-selftest.txt" \
    --mutant "M14=$r/c2-after-M14-selftest.txt" --mutant "M15=$r/c2-after-M15-selftest.txt" \
    --mutant "M17=$r/c2-after-M17-selftest.txt" >/dev/null 2>&1
  echo $?
}
row() { n=$((n+1)); local got=$([[ $3 == 0 ]] && echo accept || echo reject); [[ $got == "$4" ]] && ok=$((ok+1))
  printf 'ROW %s tally=%s rc=%s got=%s expect=%s match=%s\n' "$1" "$2" "$3" "$got" "$4" "$([[ $got == "$4" ]] && echo yes || echo no)"; }
row selftest-off I "$(run "$TI" "$w/reX09-selftest-off.txt")" accept
row selftest-off R "$(run "$TR" "$w/reX09-selftest-off.txt")" reject
row selftest-moved I "$(run "$TI" "$w/reX09-selftest-in-path.txt")" accept
row selftest-moved R "$(run "$TR" "$w/reX09-selftest-in-path.txt")" accept
row by-name I "$(run "$TI" "$w/byname/c2-after-X09-selftest.txt")" reject
row by-name R "$(run "$TR" "$w/byname/c2-after-X09-selftest.txt")" reject
row honest I "$(run "$TI" "$r/c2-after-X09-selftest.txt")" accept
row honest R "$(run "$TR" "$r/c2-after-X09-selftest.txt")" accept
printf 'SUMMARY arms=%s as_expected=%s\n' "$n" "$ok"
(( ok == n ))
