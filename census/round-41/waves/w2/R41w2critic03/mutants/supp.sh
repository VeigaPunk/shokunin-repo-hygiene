#!/bin/bash
# Supplementary behavioural probes (scratch only). Usage: supp.sh <tool.py> <variant-name>
set -u
TOOL="$1"; V="$2"
S=/fast/scratch/hyaku/souji-r41/R41w2critic03
W="$S/supp/$V"
rm -rf "$W"; mkdir -p "$W/root" "$W/o" "$W/rootx"
export TMPDIR="$W"
git -C "$W/root/a" init -q 2>/dev/null || { mkdir -p "$W/root/a" && git -C "$W/root/a" init -q; }
git -C "$W/rootx" init -q
mkdir -p "$W/root/bad/.git"
mkdir -p "$W/o/real"; ln -s "$W/o/real" "$W/o/link"
printf 'REPO\ta\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n' > "$W/o/good.rec"
printf 'REPO\ta\tregs=1\tprunable=0\nTOTAL\trepos=2\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n' > "$W/o/two_total.rec"
printf 'REPO\t../rootx\tregs=1\tprunable=0\n' > "$W/o/sibling.rec"
printf 'REPO\tbad\tregs=0\tprunable=0\nREPO\ta\tregs=1\tprunable=0\n' > "$W/o/bad.rec"
mkfifo "$W/o/fifo.rec"
ln "$W/o/good.rec" "$W/o/alias.json"
run() {  # name, then args
  local name="$1"; shift
  local out err rc
  out=$(timeout 5 python3 -B "$TOOL" "$@" 2>"$W/err.txt"); rc=$?
  err=$(head -c 300 "$W/err.txt" | tr '\n' ' ')
  echo "[$V] $name rc=$rc stdout_summary=$(printf '%s' "$out" | grep -o 'SUMMARY.*unreachable=[0-9]*' | sed 's/SUMMARY record=[^ ]* //') stderr=${err:-none}"
}
run A-good-json-write   --root "$W/root" --record "$W/o/good.rec" --skip-unrecorded --json "$W/o/out_good.json"
echo "[$V] A-good-json-file: $(head -c 200 "$W/o/out_good.json" 2>/dev/null | tr '\n' ' ')" 
run B-fifo-record       --root "$W/root" --record "$W/o/fifo.rec" --skip-unrecorded
run C-two-total         --root "$W/root" --record "$W/o/two_total.rec" --skip-unrecorded
run D-sibling-prefix    --root "$W/root" --record "$W/o/sibling.rec" --skip-unrecorded
run E-record-hardlink   --root "$W/root" --record "$W/o/good.rec" --skip-unrecorded --json "$W/o/alias.json"
run F-json-under-root   --root "$W/root" --record "$W/o/good.rec" --skip-unrecorded --json "$W/root/o.json"
run G-json-under-repo-a --root "$W/root" --record "$W/o/good.rec" --skip-unrecorded --json "$W/root/a/o.json"
run H-symlink-component --root "$W/root" --record "$W/o/good.rec" --skip-unrecorded --json "$W/o/link/x.json"
echo "[$V] H-symlink-target-exists: $(ls "$W/o/real" 2>/dev/null | tr '\n' ' ')"
run I-unreachable-json  --root "$W/root" --record "$W/o/bad.rec" --skip-unrecorded --json "$W/o/out_bad.json"
echo "[$V] I-unreachable-json-field: $(grep -o '"unreachable": [0-9]*' "$W/o/out_bad.json" 2>/dev/null)"
rm -rf "$W"
