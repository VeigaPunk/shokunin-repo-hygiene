#!/usr/bin/env bash
# Probe G2: the --timeout lower bound moved from "< 1" to "<= 1". Scenario: one healthy repo; --timeout 1.
# Pristine: accepted, SUMMARY printed (rc 0). Mutant: refused USAGE (rc 2). --timeout 0 is a control (both refuse).
set -eu
. /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42reviewer03/probe-lib.sh
probe_setup G2
mkdir -p -- "$SCR/fleet"
mkrepo "$SCR/fleet/alpha"
printf 'REPO\talpha\tregs=1\tprunable=0\n' > "$SCR/rec.tsv"
run_case pristine "$PRISTINE" 20 --root "$SCR/fleet" --record "$SCR/rec.tsv" --timeout 1
run_case mutant "$MUTANT" 20 --root "$SCR/fleet" --record "$SCR/rec.tsv" --timeout 1
run_case pristine-timeout0 "$PRISTINE" 20 --root "$SCR/fleet" --record "$SCR/rec.tsv" --timeout 0
run_case mutant-timeout0 "$MUTANT" 20 --root "$SCR/fleet" --record "$SCR/rec.tsv" --timeout 0
