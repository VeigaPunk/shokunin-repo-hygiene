#!/usr/bin/env bash
# S74ExecEvade r74 (wave w1): minimal reproduction of route h-envconfig-filter against
# tools/souji-pre-report-gate.sh at ec13ba7fac9085005dca2e69ee12a2933d2c22a5 (r74 C1 candidate).
set -u
lane=/home/vgpnk/Projects/shokunin/souji-shokunin
seat=$lane/.ufo/waves/round-74/w1/S74ExecEvade
mkdir -p /fast/scratch/hyaku/souji-r74/S74ExecEvade
S=$(mktemp -d -p /fast/scratch/hyaku/souji-r74/S74ExecEvade "repro.XXXXXX")
[ -n "$S" ] && [ -d "$S" ] || exit 1
trap 'rm -rf -- "$S"' EXIT
mkdir -p "$S/gate"
git -C "$lane" show ec13ba7fac9085005dca2e69ee12a2933d2c22a5:tools/souji-pre-report-gate.sh > "$S/gate/souji-pre-report-gate.sh"
git -C "$lane" show ec13ba7fac9085005dca2e69ee12a2933d2c22a5:tools/souji-receipt-write.py > "$S/gate/souji-receipt-write.py"
python3 -B "$seat/probe.py" --gate-copy "$S/gate" --work "$S/work" --routes h-envconfig-filter
