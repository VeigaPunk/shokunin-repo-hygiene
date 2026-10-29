#!/usr/bin/env bash
# Probe B1: parse_record without O_NONBLOCK. Scenario: the --record path is a FIFO with no writer.
# Pristine: refused at once (RECORD-MALFORMED, rc 2). Mutant: os.open blocks; killed by timeout (rc 124).
set -eu
. /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42reviewer03/probe-lib.sh
probe_setup B1
mkdir -p -- "$SCR/fleet"
mkfifo "$SCR/rec.fifo"
run_case pristine "$PRISTINE" 5 --root "$SCR/fleet" --record "$SCR/rec.fifo"
run_case mutant "$MUTANT" 5 --root "$SCR/fleet" --record "$SCR/rec.fifo"
