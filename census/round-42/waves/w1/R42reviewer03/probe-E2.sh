#!/usr/bin/env bash
# Probe E2: record-row containment with commonprefix instead of commonpath.
# Case 1 (refusal path): row "../fleet-sib" is a real repo in a sibling directory sharing the string prefix
#   "<root>". Pristine refuses at the row check (RECORD-OUTSIDE-ROOT "../fleet-sib resolves outside").
#   Mutant passes the row check and is refused one step later by the unchanged gitdir check
#   ("../fleet-sib gitdir resolves outside"): same rc 2, different message.
# Case 2 (success path): row "../fleet-sib2" is a sibling directory whose .git FILE points at a gitdir
#   inside the root. Pristine refuses (rc 2, row resolves outside). Mutant accepts the row and the repo
#   is measured: SUMMARY printed, rc 0.
set -eu
. /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42reviewer03/probe-lib.sh
probe_setup E2
mkdir -p -- "$SCR/fleet"
mkrepo "$SCR/fleet-sib"
printf 'REPO\t../fleet-sib\tregs=1\tprunable=0\n' > "$SCR/rec.tsv"
run_case case1-pristine "$PRISTINE" 20 --root "$SCR/fleet" --record "$SCR/rec.tsv"
run_case case1-mutant "$MUTANT" 20 --root "$SCR/fleet" --record "$SCR/rec.tsv"

"$REAL_GIT" init -q --separate-git-dir="$SCR/fleet/sib.git" "$SCR/fleet-sib2"
"$REAL_GIT" -C "$SCR/fleet-sib2" commit -q --allow-empty -m init
printf 'REPO\t../fleet-sib2\tregs=1\tprunable=0\n' > "$SCR/rec2.tsv"
run_case case2-pristine "$PRISTINE" 20 --root "$SCR/fleet" --record "$SCR/rec2.tsv"
run_case case2-mutant "$MUTANT" 20 --root "$SCR/fleet" --record "$SCR/rec2.tsv"
