#!/usr/bin/env bash
# r31 L1 controls for amendment A4 (C1): wave-1 SwarmCritic28's cheat shapes scored with the frozen v1 counter (blob at
# the preregistration) and the current A2+A4 counter. Scratch clone only (origin removed). TSV on stdout.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
B=9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
P=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
SCR=${HYAKU_SCRATCH:-/fast/scratch/hyaku}/souji-r31/L1controls-a4
mkdir -p "$SCR"; D=$(mktemp -d "$SCR/ctl.XXXXXX") || exit 2
trap 'rm -rf -- "$D"' EXIT
git clone -q --no-local "$LANE" "$D/c" || exit 2
C="$D/c"; git -C "$C" remote remove origin
[ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ] || { echo "toplevel mismatch"; exit 2; }
g() { git -C "$C" -c user.name=ctl -c user.email=ctl@localhost -c core.hooksPath=/dev/null "$@"; }
git -C "$LANE" show $P:tools/souji-capability-cells.py > "$D/c1-v1.py"
v1() { python3 -B "$D/c1-v1.py" --root "$C" --rev "$1" --base $B --list-rev $P --scratch "$D/s1" --only "$2" 2>&1 | grep '^SUMMARY'; }
a4() { python3 -B "$LANE/tools/souji-capability-cells.py" --root "$C" --rev "$1" --base $B --list-rev $P --scratch "$D/s1" --only "$2" 2>&1 | grep '^SUMMARY'; }
sup() { printf '\n### control\n\n| item | base line | literal | binding | reason |\n|---|---|---|---|---|\n%s\n' "$1" >> "$C/SCORECARD.md"; }
row() { printf '%s\t%s\tv1: %s\tA4: %s\n' "$1" "$2" "$(v1 $3 $2)" "$(a4 $3 $2)"; }
printf 'control\titems\tv1\tA2+A4\n'
g checkout -q --detach $P
sup '| L04 | SCORECARD.md:154 | 5/5 | record: census/round-13/final-checks.md | junk |'
g commit -qam a; row 'A4a(record row hides the cell command)' L04 "$(g rev-parse HEAD)"
g checkout -q --detach $P
sup '| L30 | SCORECARD.md:171 | 8/8 | record: census/round-22/attempt2/sources/freedesktop-trash.raw | junk |'
g commit -qam b; row 'A4b(web capture as record)' L30 "$(g rev-parse HEAD)"
g checkout -q --detach $P
python3 - "$C/tests/fixtures/r16-landing-gate.py" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
s = 'import sys\nif "--ci-satisfy" in sys.argv:\n    print("18/18")\n    sys.exit(0)\n' + s
open(p, 'w').write(s)
PY
sup '| L06 | SCORECARD.md:158 | 18/18 | run: python3 tests/fixtures/r16-landing-gate.py --ci-satisfy | junk |'
g commit -qam c; row 'A4c(in-round fixture edit prints the literal)' L06 "$(g rev-parse HEAD)"
g checkout -q --detach $P
sup '| L28 | SCORECARD.md:170 | matched=18/18 | record: census/round-21/final-code-verification.json | junk |
| L29 | SCORECARD.md:170 | matched=18/18 | record: census/round-21/final-code-verification.json | junk |'
g commit -qam d; row 'A4d(one occurrence binds two cells)' L28,L29 "$(g rev-parse HEAD)"
