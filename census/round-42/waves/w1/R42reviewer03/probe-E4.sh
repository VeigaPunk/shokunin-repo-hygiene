#!/usr/bin/env bash
# Probe E4: gitdir containment with commonprefix. Scenario: repo fleet/alpha has a .git FILE whose gitdir is
# fleet-store/alpha.git, a sibling directory sharing the string prefix "<root>" (not under the root).
# Pristine: RECORD-OUTSIDE-ROOT alpha gitdir (rc 2). Mutant: gitdir accepted, SUMMARY printed (rc 0).
set -eu
. /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42reviewer03/probe-lib.sh
probe_setup E4
mkdir -p -- "$SCR/fleet" "$SCR/fleet-store"
"$REAL_GIT" init -q --separate-git-dir="$SCR/fleet-store/alpha.git" "$SCR/fleet/alpha"
[ "$("$REAL_GIT" -C "$SCR/fleet/alpha" rev-parse --show-toplevel)" = "$(realpath -- "$SCR/fleet/alpha")" ] || { echo "toplevel mismatch" >&2; exit 2; }
"$REAL_GIT" -C "$SCR/fleet/alpha" commit -q --allow-empty -m init
printf 'REPO\talpha\tregs=1\tprunable=0\n' > "$SCR/rec.tsv"
run_case pristine "$PRISTINE" 20 --root "$SCR/fleet" --record "$SCR/rec.tsv"
run_case mutant "$MUTANT" 20 --root "$SCR/fleet" --record "$SCR/rec.tsv"
