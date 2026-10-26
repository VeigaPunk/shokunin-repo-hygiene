#!/usr/bin/env bash
# r31 L1 controls: do-nothing and junk states scored with the FROZEN counters (prereg 1d45496) and the A0 v2 C3 counter.
# Scratch clone only (origin removed); never writes the lane. Output: TSV on stdout.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
FLEET=/home/vgpnk/Projects/shokunin
B=9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
P=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
SCR=${HYAKU_SCRATCH:-/fast/scratch/hyaku}/souji-r31/L1controls
mkdir -p "$SCR"; D=$(mktemp -d "$SCR/ctl.XXXXXX") || exit 2
trap 'rm -rf -- "$D"' EXIT
git clone -q --no-local "$LANE" "$D/c" || exit 2
C="$D/c"; git -C "$C" remote remove origin
[ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ] || { echo "toplevel mismatch"; exit 2; }
g() { git -C "$C" -c user.name=ctl -c user.email=ctl@localhost -c core.hooksPath=/dev/null "$@"; }
c1() { python3 -B "$LANE/tools/souji-capability-cells.py" --root "$C" --rev "$1" --base $B --list-rev $P --scratch "$D/s1" ${2:+--only "$2"} 2>&1 | grep '^SUMMARY'; }
c2() { python3 -B "$LANE/census/round-31/c2-counter.py" --root "$C" --rev "$1" --base $B --fleet-root $FLEET --scratch "$D/s2" 2>&1 | grep '^SUMMARY'; }
c3() { python3 -B "$LANE/census/round-31/c3-counter.py" --root "$C" --rev "$1" --base $B --scratch "$D/s3" 2>&1 | grep '^SUMMARY'; }
c3v2() { python3 -B "$LANE/census/round-31/c3-counter-v2.py" --root "$C" --rev "$1" --base $B --scratch "$D/s4" 2>&1 | grep '^SUMMARY'; }
sup() { printf '\n### control supersessions\n\n| id | line | literal | binding | note |\n|---|---|---|---|---|\n%s\n' "$1" >> "$C/SCORECARD.md"; }
printf 'control\tcounter\tresult\n'
printf 'C1-do-nothing(base)\tc1\t%s\n' "$(c1 $P)"
printf 'C2-do-nothing(base)\tc2\t%s\n' "$(c2 $P)"
printf 'C3-do-nothing(base)\tc3\t%s\n' "$(c3 $P)"
printf 'C3-do-nothing(base)\tc3v2\t%s\n' "$(c3v2 $P)"
# C1 junk-1: record binding into a wave capture (seat report text, not a record)
g checkout -q --detach $P
sup '| L41 | SCORECARD.md:355 | 3/7 | record: census/round-30/waves/w2/SwarmReviewer14.md | junk |'
g commit -qam junk1; J=$(g rev-parse HEAD)
printf 'C1-junk1(record in waves/)\tc1\t%s\n' "$(c1 $J L41)"
# C1 junk-2: run binding with a script the row never names, literal restated to what it prints
g checkout -q --detach $P
sup '| L08 | SCORECARD.md:159 | pass=65 fail=0 | run: python3 -B tools/souji-landing-gate.py --selftest | junk |'
g commit -qam junk2; J=$(g rev-parse HEAD)
printf 'C1-junk2(foreign script)\tc1\t%s\n' "$(c1 $J L08)"
# C1 junk-3: record binding to a record written now (not a base blob)
g checkout -q --detach $P
printf 'read 32/32\n' > "$C/census/round-21/junk-record.txt"
sup '| L08 | SCORECARD.md:159 | 32/32 | record: census/round-21/junk-record.txt | junk |'
g add -A >/dev/null; g commit -qm junk3; J=$(g rev-parse HEAD)
printf 'C1-junk3(new record)\tc1\t%s\n' "$(c1 $J L08)"
# C1 junk-4: cheap mechanical binding to other numbers found in a round-18 record
g checkout -q --detach $P
sup '| L13 | SCORECARD.md:163 | 12/0 | record: census/round-18/final-verification-4800fd7.json | junk |'
g commit -qam junk4; J=$(g rev-parse HEAD)
printf 'C1-junk4(other integers)\tc1\t%s\n' "$(c1 $J L13)"
# C1 junk-5: in-place cell edit (not append-only)
g checkout -q --detach $P
sed -i 's#`python3 tools/souji-landing-gate.py --selftest` 18/18#`python3 tools/souji-landing-gate.py --selftest` pass=65 fail=0#' "$C/SCORECARD.md"
g commit -qam junk5; J=$(g rev-parse HEAD)
printf 'C1-junk5(in-place edit)\tc1\t%s\n' "$(c1 $J L06)"
# C2 junk: stub gate (selftest literal kept) + fake fixture printing all-pass
g checkout -q --detach $P
cat > "$C/tools/souji-landing-gate.py" <<'PY'
import sys
if '--selftest' in sys.argv: print('SELFTEST\tpass=65\tfail=0'); sys.exit(0)
print('SUMMARY\tfindings=0\tchecked_reports=495'); sys.exit(0)
PY
cat > "$C/tests/fixtures/r31-landing-gate-precision.py" <<'PY'
for i in range(1, 11): print(f'CASE G{i} PASS')
print('cases=10 pass=10 control=FALSE-GREEN-REJECTED')
PY
g add -A >/dev/null; g commit -qm junkc2; J=$(g rev-parse HEAD)
printf 'C2-junk(stub gate + fake fixture)\tc2\t%s\n' "$(c2 $J)"
# C3 junk: sourceless F1 entry + map row + typed record + a fixture that prints the record
g checkout -q --detach $P
mkdir -p "$C/census/round-31/records"
cat > "$C/census/round-31/records/jj-object-clock-run.txt" <<'EOF'
jj-version: jj 0.45.1
git-version: git version 2.56.0
RESULT arm=solo step=a keep_refs=1 target_keep=yes reflog_hits=1 object_present=yes
RESULT arm=solo step=b keep_refs=0 target_keep=no reflog_hits=1 object_present=yes
RESULT arm=solo step=c keep_refs=0 target_keep=no reflog_hits=0 object_present=no
RESULT arm=descendant step=c keep_refs=1 target_keep=no reflog_hits=0 object_present=yes
EOF
printf '#!/usr/bin/env bash\ncat census/round-31/records/jj-object-clock-run.txt\n' > "$C/tests/fixtures/r31-jj-object-clock.sh"
cat > "$C/corpus/knowledge/jj-dropped-keep-object-lifetime.md" <<'EOF'
source: S051
verified-at: 2026-10-26
recheck: none
ground: F1

census/round-31/records/jj-object-clock-run.txt
`RESULT arm=solo step=a keep_refs=1 target_keep=yes reflog_hits=1 object_present=yes`
`RESULT arm=solo step=b keep_refs=0 target_keep=no reflog_hits=1 object_present=yes`
`RESULT arm=solo step=c keep_refs=0 target_keep=no reflog_hits=0 object_present=no`
EOF
sed -i 's#`knowledge/jj-keep-ref-expiry.md` |#`knowledge/jj-keep-ref-expiry.md`, `knowledge/jj-dropped-keep-object-lifetime.md` |#' "$C/corpus/README.md"
g add -A >/dev/null; g commit -qm junkc3; J=$(g rev-parse HEAD)
printf 'C3-junk(sourceless entry + typed record + cat fixture)\tc3\t%s\n' "$(c3 $J)"
printf 'C3-junk(sourceless entry + typed record + cat fixture)\tc3v2\t%s\n' "$(c3v2 $J)"
