#!/bin/bash
# Minimal repro: a preregistration PATH containing a glob metacharacter makes the tool take an EARLIER
# commit (one that added a different file matching the glob) as FREEZE-REV.
# usage: repro-glob-freeze.sh <tool> <scratch-root>
set -eu
TOOL=${1:?tool}; SCR=${2:?scratch}
D=$(mktemp -d -p "$SCR")
trap 'rm -rf "$D"' EXIT
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null TMPDIR="$SCR" HOME="$SCR" LC_ALL=C
export GIT_AUTHOR_NAME=fx GIT_AUTHOR_EMAIL=fx@example.invalid GIT_COMMITTER_NAME=fx GIT_COMMITTER_EMAIL=fx@example.invalid
git -C "$D" init -q -b main
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ]
mkdir -p "$D/census"
echo base > "$D/README.md"; git -C "$D" add -A; git -C "$D" commit -q -m base
BASE=$(git -C "$D" rev-parse HEAD)
echo decoy > "$D/census/prea.txt"; git -C "$D" add -A; git -C "$D" commit -q -m decoy       # NOT the preregistration
printf 'c\n' > "$D/census/counter.py"; printf 'h\nr\n' > "$D/census/pop.tsv"; printf 'EXIT=1\n' > "$D/census/ctl.txt"
cat > "$D/census/pre[ab].txt" <<EOT
Round: 7
## C1
Base: $BASE
Counter: census/counter.py sha256=a3a5e715f0cc574a73c3f9bebb6bc24f32ffd5b67b387244c2c909da779a1478
Population: census/pop.tsv sha256=bc0405cffdbb957b8790ce8d5ced0091b4d0b2f32bee8f8a5ffc143032bda4f8
Control: census/ctl.txt
Target: t
Kill: k
EOT
git -C "$D" add -A; git -C "$D" commit -q -m freeze
TIP=$(git -C "$D" rev-parse HEAD)
echo "--- glob-named prereg 'census/pre[ab].txt' (expected: clean, exit 0):"
python3 -B "$TOOL" --root "$D" --prereg 'census/pre[ab].txt' --rev "$TIP" && echo "exit=0" || echo "exit=$?"
# control: identical repo history but the prereg is renamed to a glob-free name in the freeze commit
git -C "$D" checkout -q "$BASE"; git -C "$D" checkout -q -b ctl
mkdir -p "$D/census"; echo decoy > "$D/census/prea.txt"; git -C "$D" add -A; git -C "$D" commit -q -m decoy
printf 'c\n' > "$D/census/counter.py"; printf 'h\nr\n' > "$D/census/pop.tsv"; printf 'EXIT=1\n' > "$D/census/ctl.txt"
git -C "$D" show "$TIP:census/pre[ab].txt" > "$D/census/pre-ab.txt"
git -C "$D" add -A; git -C "$D" commit -q -m freeze
CTIP=$(git -C "$D" rev-parse HEAD)
echo "--- control: same content, glob-free name census/pre-ab.txt (expected clean, exit 0):"
python3 -B "$TOOL" --root "$D" --prereg 'census/pre-ab.txt' --rev "$CTIP" && echo "exit=0" || echo "exit=$?"

# ---- part B: the same defect hides a real violation (false GREEN) ----
# counter/population/control exist before the decoy, so only the dispatch rule can fire; a dispatch-class file is
# committed IN the freeze commit (rule: added by FREEZE-REV or an ancestor => DISPATCH-BEFORE-FREEZE).
E=$(mktemp -d -p "$SCR"); trap 'rm -rf "$D" "$E"' EXIT
git -C "$E" init -q -b main
[ "$(git -C "$E" rev-parse --show-toplevel)" = "$E" ]
mkdir -p "$E/census" "$E/.ufo/waves/round-7"
echo base > "$E/README.md"; printf 'c\n' > "$E/census/counter.py"; printf 'h\nr\n' > "$E/census/pop.tsv"; printf 'EXIT=1\n' > "$E/census/ctl.txt"
git -C "$E" add -A; git -C "$E" commit -q -m base; B2=$(git -C "$E" rev-parse HEAD)
echo decoy > "$E/census/prea.txt"; git -C "$E" add -A; git -C "$E" commit -q -m decoy
echo '{}' > "$E/.ufo/waves/round-7/w1-spec.json"
sed "s/^Base: .*/Base: $B2/" "$D/census/pre-ab.txt" > "$E/census/pre[ab].txt" 2>/dev/null || git -C "$D" show "$TIP:census/pre[ab].txt" | sed "s/^Base: .*/Base: $B2/" > "$E/census/pre[ab].txt"
git -C "$E" add -A; git -C "$E" commit -q -m freeze; T2=$(git -C "$E" rev-parse HEAD)
echo "--- B1 glob-named prereg + dispatch file in freeze commit (expected: DISPATCH-BEFORE-FREEZE, exit 1):"
python3 -B "$TOOL" --root "$E" --prereg 'census/pre[ab].txt' --rev "$T2" && echo "exit=0" || echo "exit=$?"
F=$(mktemp -d -p "$SCR"); trap 'rm -rf "$D" "$E" "$F"' EXIT
git -C "$F" init -q -b main
[ "$(git -C "$F" rev-parse --show-toplevel)" = "$F" ]
mkdir -p "$F/census" "$F/.ufo/waves/round-7"
echo base > "$F/README.md"; printf 'c\n' > "$F/census/counter.py"; printf 'h\nr\n' > "$F/census/pop.tsv"; printf 'EXIT=1\n' > "$F/census/ctl.txt"
git -C "$F" add -A; git -C "$F" commit -q -m base; B3=$(git -C "$F" rev-parse HEAD)
echo decoy > "$F/census/prea.txt"; git -C "$F" add -A; git -C "$F" commit -q -m decoy
echo '{}' > "$F/.ufo/waves/round-7/w1-spec.json"
git -C "$E" show "$T2:census/pre[ab].txt" | sed "s/^Base: .*/Base: $B3/" > "$F/census/pre-ab.txt"
git -C "$F" add -A; git -C "$F" commit -q -m freeze; T3=$(git -C "$F" rev-parse HEAD)
echo "--- B2 control: glob-free prereg name census/pre-ab.txt, otherwise identical (expected and actual: DISPATCH-BEFORE-FREEZE, exit 1):"
python3 -B "$TOOL" --root "$F" --prereg 'census/pre-ab.txt' --rev "$T3" && echo "exit=0" || echo "exit=$?"
