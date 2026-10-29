#!/usr/bin/env bash
# Probe G5: the "worktree list" nonzero return code is no longer reported. Scenario: a git wrapper makes
# "worktree list" exit 3 with no output (prune --dry-run still real); the record names regs=1.
# Pristine: DRIFT UNREACHABLE ... UNREACHABLE:list-rc=3 (rc 1). Mutant: list treated as 0 registrations,
# DRIFT REGS-CHANGED record=1 live=0 (rc 1).
set -eu
. /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42reviewer03/probe-lib.sh
probe_setup G5
mkdir -p -- "$SCR/fleet"
mkrepo "$SCR/fleet/alpha"
printf 'REPO\talpha\tregs=1\tprunable=0\n' > "$SCR/rec.tsv"
slow_git_wrapper 'exit 3'
run_case pristine "$PRISTINE" 60 --root "$SCR/fleet" --record "$SCR/rec.tsv"
run_case mutant "$MUTANT" 60 --root "$SCR/fleet" --record "$SCR/rec.tsv"
