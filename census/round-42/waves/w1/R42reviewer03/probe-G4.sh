#!/usr/bin/env bash
# Probe G4: the list-timeout handler re-raises instead of returning UNREACHABLE:list-timeout.
# Scenario: git wrapper makes "worktree list" take 2 s; --timeout 1 forces the list call to time out.
# Pristine: DRIFT UNREACHABLE row + SUMMARY, rc 1. Mutant: uncaught subprocess.TimeoutExpired traceback, no DRIFT/SUMMARY, rc 1.
set -eu
. /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42reviewer03/probe-lib.sh
probe_setup G4
mkdir -p -- "$SCR/fleet"
mkrepo "$SCR/fleet/alpha"
printf 'REPO\talpha\tregs=1\tprunable=0\n' > "$SCR/rec.tsv"
slow_git_wrapper 'sleep 2'
run_case pristine "$PRISTINE" 60 --root "$SCR/fleet" --record "$SCR/rec.tsv" --timeout 1
run_case mutant "$MUTANT" 60 --root "$SCR/fleet" --record "$SCR/rec.tsv" --timeout 1
