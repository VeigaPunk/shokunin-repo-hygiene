#!/usr/bin/env bash
# r30 L1 amended controls: the stricter instruments A1-A3 scored on the do-nothing base and on the wave-1 cheat states
# (rebuilt here deterministically; scratch clone only, origin removed; never writes the lane).
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
FLEET=/home/vgpnk/Projects/shokunin
B=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b
P=d4928ec86b667e3d1ed0adb07fb088e500cf1631
SCR=${HYAKU_SCRATCH:-/fast/scratch/hyaku}/souji-r30/L1controls-amended
mkdir -p "$SCR"; D=$(mktemp -d "$SCR/ctl.XXXXXX") || exit 2
trap 'rm -rf -- "$D"' EXIT
git clone -q --no-local "$LANE" "$D/c" || exit 2
C="$D/c"; git -C "$C" remote remove origin
[ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ] || { echo "toplevel mismatch"; exit 2; }
g() { git -C "$C" -c user.name=ctl -c user.email=ctl@localhost -c core.hooksPath=/dev/null "$@"; }
c1() { python3 -B "$LANE/tools/souji-capability-agreement.py" --root "$C" --rev "$1" --base $B --list-rev $P --scratch "$D/s1" ${2:+--only "$2"} 2>&1 | grep '^SUMMARY'; }
c2() { python3 -B "$LANE/census/round-30/c2-counter-v2.py" --root "$C" --rev "$1" --base $B --fleet-root $FLEET --scratch "$D/s2" 2>&1 | grep '^SUMMARY'; }
c3() { python3 -B "$LANE/census/round-30/c3-counter-v2.py" --root "$C" --rev "$1" --scratch "$D/s3" 2>&1 | grep '^SUMMARY'; }
printf 'control\tcounter\tresult\n'
printf 'C1-A3-do-nothing(base)\tc1-A3\t%s\n' "$(c1 $B)"
printf 'C2-A1-do-nothing(base)\tc2-v2\t%s\n' "$(c2 $B)"
printf 'C3-A2-do-nothing(base)\tc3-v2\t%s\n' "$(c3 $B)"
# C1 bypass (SwarmCritic24 A1): cmd= wrapper sharing the script path
g checkout -q --detach $B
printf '\nR30-CORRECTION SCORECARD.md:158 R05 cmd=python3 -c pass tools/souji-landing-gate.py rc=0 observed=NONE\n' >> "$C/SCORECARD.md"
g commit -qam bypass; J=$(g rev-parse HEAD)
printf 'C1-A3-bypass(cmd=python3 -c pass, R05)\tc1-A3\t%s\n' "$(c1 $J R05)"
# C1 banner correction: R16 recorded with its argparse error
g checkout -q --detach $B
printf '\nR30-CORRECTION SCORECARD.md:175 R16 rc=2 observed=r24-coverage-agreement.py: error: the following arguments are required: --tool\n' >> "$C/SCORECARD.md"
g commit -qam banner; J=$(g rev-parse HEAD)
printf 'C1-A3-banner(R16 argparse error recorded)\tc1-A3\t%s\n' "$(c1 $J R16)"
# C2 cheat (SwarmCritic25 A): base gate with a --round 29 early return + a fixture that recognises the stub
g checkout -q --detach $B
python3 - "$C/tools/souji-landing-gate.py" <<'PY'
import sys
p = sys.argv[1]; t = open(p).read()
stub = ("import sys as _s\nif '--round' in _s.argv and _s.argv[_s.argv.index('--round') + 1] == '29':\n"
        "    print('SUMMARY\\tfindings=0\\tchecked_reports=86'); _s.exit(0)\n# R30STUB\n")
i = t.index('\nimport ') + 1
open(p, 'w').write(t[:i] + stub + t[i:])
PY
cat > "$C/tests/fixtures/r30-landing-gate-discovery.py" <<'PY'
import sys
tool = open(sys.argv[sys.argv.index('--tool') + 1]).read()
ok = 'R30STUB' in tool
for i in range(1, 8): print(f'CASE D{i} {"PASS" if ok else "FAIL"}')
print(f'cases=7 pass={7 if ok else 0} control=FALSE-GREEN-REJECTED')
PY
g add -A >/dev/null; g commit -qm stubc2; J=$(g rev-parse HEAD)
printf 'C2-A1-cheat(stub gate + recognising fixture)\tc2-v2\t%s\n' "$(c2 $J)"
