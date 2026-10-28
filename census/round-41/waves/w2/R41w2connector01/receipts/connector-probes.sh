#!/usr/bin/env bash
# R41w2connector01 probes. The lane and the sibling fleet trees are read-only here; every mutation is
# made in a fresh `git clone --shared` under the seat scratch and committed in that clone only.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
KAS=/home/vgpnk/Projects/shokunin/kasegi-shokunin/corpus/instruments/freeze-check.py
MORI_ROOT=/home/vgpnk/Projects/shokunin/mori-shokunin
TIP=1d41c13574db80fdd9a4bde490b712da7ce2a85f
FZ=$LANE/tools/souji-freeze-check.py
PRE=census/round-41/preregistration.txt
S=/fast/scratch/hyaku/souji-r41/R41w2connector01
mkdir -p "$S"
W=$(mktemp -d -p "$S" probes.XXXX) || exit 2
trap 'rm -rf -- "$W"' EXIT
export GIT_AUTHOR_NAME=conn GIT_AUTHOR_EMAIL=conn@example.invalid
export GIT_COMMITTER_NAME=conn GIT_COMMITTER_EMAIL=conn@example.invalid

clone() {  # clone NAME -> $W/NAME, guarded
  git clone -q --shared "$LANE" "$W/$1" || { echo "clone failed: $1"; exit 2; }
  [ "$(git -C "$W/$1" rev-parse --show-toplevel)" = "$W/$1" ] || { echo "toplevel guard failed: $1"; exit 2; }
}

echo "# tip=$(git -C "$LANE" rev-parse HEAD) expected=$TIP"
echo "# tool sha256: $(sha256sum "$FZ" | cut -c1-64)"
echo "## P0a freeze-check on r41 prereg at tip"
python3 -B "$FZ" --root "$LANE" --prereg "$PRE" --rev "$TIP"; echo "rc=$?"
echo "## P0b freeze-check on r40 prereg at tip (retro arm)"
python3 -B "$FZ" --root "$LANE" --prereg census/round-40/preregistration.txt --rev "$TIP" > "$W/r40.txt"; rc=$?
tail -n 1 "$W/r40.txt"; echo "rc=$rc findings=$(grep -c '^FINDING' "$W/r40.txt")"

echo "## M1 C1 Target line edited after freeze (rule 1 says frozen)"
clone m1; C=$W/m1
sed -i 's/^Target: SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0/Target: SUMMARY items=3 mismatched=0 corrected=0 uncorrected=3/' "$C/$PRE"
git -C "$C" diff --stat; git -C "$C" commit -qam m1
python3 -B "$FZ" --root "$C" --prereg "$PRE" --rev "$(git -C "$C" rev-parse HEAD)"; echo "rc=$?"

echo "## M2 C1 Control file appended after freeze (rule 1 says frozen)"
clone m2; C=$W/m2
printf 'EXIT=0\n' >> "$C/census/round-41/controls/c1-control.txt"
git -C "$C" commit -qam m2
python3 -B "$FZ" --root "$C" --prereg "$PRE" --rev "$(git -C "$C" rev-parse HEAD)"; echo "rc=$?"

echo "## M3 C1 Counter appended after freeze (positive control: must be FROZEN-EDITED)"
clone m3; C=$W/m3
printf '# edited\n' >> "$C/census/round-41/c1-counter.py"
git -C "$C" commit -qam m3
python3 -B "$FZ" --root "$C" --prereg "$PRE" --rev "$(git -C "$C" rev-parse HEAD)"; echo "rc=$?"

echo "## M4 C1 Kill line edited after freeze"
clone m4; C=$W/m4
sed -i 's/^Kill: any item uncorrected, any junk line/Kill: none/' "$C/$PRE"
git -C "$C" commit -qam m4
python3 -B "$FZ" --root "$C" --prereg "$PRE" --rev "$(git -C "$C" rev-parse HEAD)"; echo "rc=$?"

echo "## P1 probe claim C4 whose Target no counter prints (does the tool replay Targets?)"
clone c4; C=$W/c4
cat >> "$C/$PRE" <<'EOF'

## C4 — demonstration (connector probe, not a claim)
Base: 7eebc183f2685d1ea9b004b4de22c09a8a4035a7
Counter: census/round-41/c2-cases.tsv sha256=4854335abdd479423d01d435a4fbe2e8f82d432a58414df945da8b48930e75c6
Population: census/round-41/c3-sites.tsv sha256=be363c0de5d332dc4223bdf6ccf5f2035e6e38af9cc30735463b07b5d2e764ea
Control: census/round-41/controls/c3-control.txt
Target: SUMMARY items=999 impossible=1 (exit 0) never printed by any counter
Kill: none
EOF
git -C "$C" commit -qam p1
python3 -B "$FZ" --root "$C" --prereg "$PRE" --rev "$(git -C "$C" rev-parse HEAD)"; echo "rc=$?"
echo "### same claim through the kasegi replay tool (base = the C4 clone, counter cat-only)"
cat > "$W/kas.json" <<'EOF'
{"schema": "kasegi-round-claims-v2", "claims": [{"id": "P1", "counter_cmd": "cat {tree}/census/round-41/controls/c3-control.txt", "expect_before": "SUMMARY items=999 impossible=1 (exit 0) never printed by any counter", "expect_after": "EXIT=0"}]}
EOF
mkdir -p "$W/kw"
python3 -B "$KAS" --claims "$W/kas.json" --tool-root "$W" --base "$C" --work "$W/kw"; echo "rc=$?"

echo "## X1 mori-freeze-order selftest under the seat scratch (refusal expected: TMPDIR must sit inside its checkout)"
mkdir -p "$W/mori"
( cd "$MORI_ROOT" && TMPDIR="$W/mori" python3 -B tools/mori-freeze-order.py --selftest ); echo "rc=$?"

echo "## X2 committed C2 counter at tip"
( cd "$LANE" && TMPDIR="$W/c2" && mkdir -p "$W/c2" && TMPDIR="$W/c2" python3 -B census/round-41/c2-counter.py --root "$LANE" --rev "$TIP" --scratch "$W/c2" ); echo "rc=$?"
