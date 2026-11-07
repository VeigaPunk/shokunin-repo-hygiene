#!/usr/bin/env bash
# S79Sentinel r79: recreate the two gate/writer pairs the reproducers read (read-only git show).
set -u
S=/fast/scratch/hyaku/souji-r79/S79Sentinel
L=/home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p "$S/gw1" "$S/gbase" || exit 1
git -C "$L" show c8c3fbca5ac44184feac3a01ee964139f86c02a4:tools/souji-pre-report-gate.sh > "$S/gw1/souji-pre-report-gate.sh" || exit 1
git -C "$L" show c8c3fbca5ac44184feac3a01ee964139f86c02a4:tools/souji-receipt-write.py > "$S/gw1/souji-receipt-write.py" || exit 1
git -C "$L" show e65538e73c7f1a8f7570bc24a2215da8a90043f3:tools/souji-pre-report-gate.sh > "$S/gbase/souji-pre-report-gate.sh" || exit 1
git -C "$L" show e65538e73c7f1a8f7570bc24a2215da8a90043f3:tools/souji-receipt-write.py > "$S/gbase/souji-receipt-write.py" || exit 1
sha256sum "$S/gw1/souji-pre-report-gate.sh" "$S/gbase/souji-pre-report-gate.sh"
