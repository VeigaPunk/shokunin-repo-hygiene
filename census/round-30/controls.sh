#!/usr/bin/env bash
# r30 L1 controls: do-nothing and junk states scored with the FROZEN counters (prereg d4928ec).
# Scratch clone only (origin removed); never writes the lane. Output: TSV on stdout.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
FLEET=/home/vgpnk/Projects/shokunin
B=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b
P=d4928ec86b667e3d1ed0adb07fb088e500cf1631
SCR=${HYAKU_SCRATCH:-/fast/scratch/hyaku}/souji-r30/L1controls
mkdir -p "$SCR"; D=$(mktemp -d "$SCR/ctl.XXXXXX") || exit 2
trap 'rm -rf -- "$D"' EXIT
git clone -q --no-local "$LANE" "$D/c" || exit 2
C="$D/c"; git -C "$C" remote remove origin
[ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ] || { echo "toplevel mismatch"; exit 2; }
g() { git -C "$C" -c user.name=ctl -c user.email=ctl@localhost -c core.hooksPath=/dev/null "$@"; }
c1() { python3 -B "$LANE/tools/souji-capability-agreement.py" --root "$C" --rev "$1" --base $B --list-rev $P --scratch "$D/s1" ${2:+--only "$2"} 2>&1 | grep '^SUMMARY'; }
c2() { python3 -B "$LANE/census/round-30/c2-counter.py" --root "$C" --rev "$1" --base $B --fleet-root $FLEET --scratch "$D/s2" 2>&1 | grep '^SUMMARY'; }
c3() { python3 -B "$LANE/census/round-30/c3-counter.py" --root "$C" --rev "$1" --scratch "$D/s3" 2>&1 | grep '^SUMMARY'; }
printf 'control\tcounter\tresult\n'
printf 'C1-do-nothing(base)\tc1\t%s\n' "$(c1 $B)"
printf 'C2-do-nothing(base)\tc2\t%s\n' "$(c2 $B)"
printf 'C3-do-nothing(base)\tc3\t%s\n' "$(c3 $B)"
# C1 junk-1: correction lines for R05/R10 with an invented observed value
g checkout -q --detach $B
printf '\nR30-CORRECTION SCORECARD.md:158 R05 rc=0 observed=SELFTEST pass=18 fail=0\nR30-CORRECTION SCORECARD.md:167 R10 rc=0 observed=11/0\n' >> "$C/SCORECARD.md"
g commit -qam junk1; J=$(g rev-parse HEAD)
printf 'C1-junk1(invented observed, R05+R10)\tc1\t%s\n' "$(c1 $J R05,R10)"
# C1 junk-2: stated literals edited in place to what the command prints (not append-only)
g checkout -q --detach $B
python3 - "$C/SCORECARD.md" <<'PY'
import sys
p=sys.argv[1]; t=open(p).read()
t=t.replace("`python3 tools/souji-landing-gate.py --selftest` 18/18","`python3 tools/souji-landing-gate.py --selftest` SELFTEST pass=65 fail=0")
open(p,'w').write(t)
PY
g commit -qam junk2; J=$(g rev-parse HEAD)
printf 'C1-junk2(in-place edit, R05)\tc1\t%s\n' "$(c1 $J R05)"
# C1 junk-3: correction with a substituted command that prints the stated literal
g checkout -q --detach $B
printf '\nR30-CORRECTION SCORECARD.md:158 R05 cmd=echo 18/18 rc=0 observed=18/18\n' >> "$C/SCORECARD.md"
g commit -qam junk3; J=$(g rev-parse HEAD)
printf 'C1-junk3(cmd substitution, R05)\tc1\t%s\n' "$(c1 $J R05)"
# C2 junk: stub gate (prints checked_reports=86, never a pointer finding) + fake fixture that prints all-pass
g checkout -q --detach $B
cat > "$C/tools/souji-landing-gate.py" <<'PY'
import sys
if '--selftest' in sys.argv: print('SELFTEST\tpass=65\tfail=0'); sys.exit(0)
print('SUMMARY\tfindings=0\tchecked_reports=86'); sys.exit(0)
PY
cat > "$C/tests/fixtures/r30-landing-gate-discovery.py" <<'PY'
for i in range(1, 8): print(f'CASE D{i} PASS')
print('cases=7 pass=7 control=FALSE-GREEN-REJECTED')
PY
g add -A >/dev/null; g commit -qm junkc2; J=$(g rev-parse HEAD)
printf 'C2-junk(stub gate + fake fixture)\tc2\t%s\n' "$(c2 $J)"
# C3 junk: a sourceless F1 entry named in the F1 map row, with the run-record path string but no record
g checkout -q --detach $B
cat > "$C/corpus/knowledge/jj-keep-ref-expiry.md" <<'EOF'
source: S051
verified-at: 2026-10-26
recheck: none
ground: F1

refs/jj/keep and util gc. census/round-30/records/jj-keep-expiry-run.txt
EOF
sed -i 's#`knowledge/git-auto-maintenance-trigger-set-r23.md` |#`knowledge/git-auto-maintenance-trigger-set-r23.md`, `knowledge/jj-keep-ref-expiry.md` |#' "$C/corpus/README.md"
g add -A >/dev/null; g commit -qm junkc3; J=$(g rev-parse HEAD)
printf 'C3-junk(sourceless F1 entry + map row)\tc3\t%s\n' "$(c3 $J)"
