#!/usr/bin/env bash
# Probe G3: --timeout default 20 -> 1. Scenario: a git wrapper on PATH makes "worktree list" take 2 s
# (real git otherwise). No --timeout on the command line.
# Pristine (default 20): clean, rc 0. Mutant (default 1): UNREACHABLE:list-timeout drift row, rc 1.
# Controls: pristine --timeout 1 also reports UNREACHABLE; mutant --timeout 20 is clean (the default is the only difference).
set -eu
. /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42reviewer03/probe-lib.sh
probe_setup G3
mkdir -p -- "$SCR/fleet"
mkrepo "$SCR/fleet/alpha"
printf 'REPO\talpha\tregs=1\tprunable=0\n' > "$SCR/rec.tsv"
slow_git_wrapper 'sleep 2'
run_case pristine "$PRISTINE" 60 --root "$SCR/fleet" --record "$SCR/rec.tsv"
run_case mutant "$MUTANT" 60 --root "$SCR/fleet" --record "$SCR/rec.tsv"
run_case pristine-timeout1 "$PRISTINE" 60 --root "$SCR/fleet" --record "$SCR/rec.tsv" --timeout 1
run_case mutant-timeout20 "$MUTANT" 60 --root "$SCR/fleet" --record "$SCR/rec.tsv" --timeout 20
