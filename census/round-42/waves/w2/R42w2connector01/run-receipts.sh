#!/usr/bin/env bash
# R42w2connector01 receipts runner. Read-only over the lane tip; writes only under the seat dir and the seat scratch.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
S=/fast/scratch/hyaku/souji-r42/R42w2connector01
SEAT=$LANE/.ufo/waves/round-42/w2/R42w2connector01
R=$SEAT/receipts
P=$SEAT/probes
TIP=3105a63b23481fccf7df58e74d14a6681e0ea0c8
BASE=bf618f6c5c09d302994871c94903abbea2deb60d
INSTR=b7408095543579ac71b33ecf7b80b0cb8ef45036
W=$LANE/census/round-42/waves/w1
mkdir -p "$S/fresh" "$R"
cd "$LANE" || exit 2
[ "$(git rev-parse --show-toplevel)" = "$LANE" ] || { echo "toplevel mismatch"; exit 2; }
export TMPDIR="$S"
: > "$R/index.txt"
rec() {
  local n=$1; shift
  { echo "\$ $*"; "$@"; echo "EXIT=$?"; } > "$R/$n.out" 2>&1
  echo "$n | $(grep -E '^SUMMARY|^SELFTEST|^EXIT=' "$R/$n.out" | tail -2 | tr '\n' ' ')" | tee -a "$R/index.txt"
}
rec 01-c1-tip           python3 -B census/round-42/c1-counter.py --root . --rev $TIP --scratch $S
rec 02-c2-tip           python3 -B census/round-42/c2-counter.py --root . --rev $TIP --scratch $S
rec 03-c3-tip           python3 -B census/round-42/c3-counter.py --root . --rev $TIP --scratch $S
rec 04-r1-tip           python3 -B census/round-42/r1-counter.py --root . --rev $TIP --scratch $S
rec 05-c1-controlA      python3 -B census/round-42/c1-counter.py --root . --rev $INSTR --scratch "$S/fresh"
rec 06-P1-c2-verbatim-stub  bash census/round-42/score-candidate.sh c2 "$S" tools/souji-freeze-check.py="$P/c2-target-verbatim.py"
rec 07-P1-c3-fail-stub      bash census/round-42/score-candidate.sh c3 "$S" tests/fixtures/r42-drift-conditions.py="$P/c3-summary-fail.py"
rec 08-P1-c1-k1-substance-wrong bash census/round-42/score-candidate.sh c1 "$S" census/round-42/c1-register.tsv="$W/R42critic01/k1/c1-register.tsv" corpus/lessons/round-42.md="$W/R42critic01/k1/round-42.md"
rec 09-P1-c1-h0-honest  bash census/round-42/score-candidate.sh c1 "$S" census/round-42/c1-register.tsv="$W/R42critic01/h0/c1-register.tsv" corpus/lessons/round-42.md="$W/R42critic01/h0/round-42.md"
rec 10-P1-c2-K5b-shape-table bash census/round-42/score-candidate.sh c2 "$S" tools/souji-freeze-check.py="$W/R42critic02/K5b-shape-table.py"
rec 11-P1-c3-byte-presence bash census/round-42/score-candidate.sh c3 "$S" tests/fixtures/r42-drift-conditions.py="$W/R42critic06/attacks/byte-presence-fixture.py"
rec 12-P9-c2-K4-crash-as-patch bash census/round-42/score-candidate.sh c2 "$S" tools/souji-freeze-check.py="$W/R42critic02/K4-assert-crash-selftest.py"
rec 13-P9-c3-K6-forwards-traceback bash census/round-42/score-candidate.sh c3 "$S" tests/fixtures/r42-drift-conditions.py="$W/R42critic04/k6-forwards-traceback.py"
rec 14-P2-target-diff   python3 -B "$P/p2-target-diff.py" "$LANE" "$R"
rec 15-P3-end-census    bash -c "grep -c '^| S[0-9]' corpus/SOURCES.md; git log --format='%h %s' -S'| S259 |' -- corpus/SOURCES.md; git log --format='%h %s' -- census/round-42/records/census-before.txt; ls census/round-42/records; bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin souji | grep -E '^souji.rows|^souji.W04'; bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji > \"$S/validate-tip.txt\" 2>&1; echo validate-exit=\$?; grep -c W04 \"$S/validate-tip.txt\""
rec 16-P4-modified-under-round42 git log --diff-filter=M --name-only --format='COMMIT %h %s' $BASE..$TIP -- census/round-42 tools/souji-worktree-drift.py
rec 17-P4-pinned-tool-sha bash -c "git show $TIP:tools/souji-worktree-drift.py | sha256sum"
rec 18-P5-scratch-paths bash -c "git grep -n -E '/fast/scratch|/tmp/|/var/tmp' $TIP -- census/round-42/controls census/round-42/records census/round-42/*.py census/round-42/*.sh census/round-42/*.txt corpus/lessons/round-42.md; echo ---; ls -d /fast/scratch/hyaku/souji-r42/L1 2>&1"
rec 19-P6-numstat-append-only git diff --numstat $BASE $TIP -- corpus/SOURCES.md SCORECARD.md corpus/lessons/round-42.md corpus/pointer-exemptions.tsv corpus/README.md corpus/knowledge/jj-colocation-receipts.md census/round-42/preregistration.txt
rec 20-P7-cited-source-rows bash -c "grep -c '^| S259 ' corpus/SOURCES.md; grep -c '^| S146 ' corpus/SOURCES.md; grep -n 'S146' corpus/knowledge/origin-record-exclusivity-r28.md | head -2 | cut -c1-120"
rec 21-P7-registry-agreement python3 -B tools/souji-registry-agreement.py --root . --rev $TIP --list-rev $BASE
rec 22-P8-adding-commits bash "$P/p8-adding-commits.sh" "$LANE"
rec 23-P10-SCORECARD-839 bash -c "git show $BASE:SCORECARD.md | sed -n 839p | sha256sum; git show $TIP:SCORECARD.md | sed -n 839p | sha256sum; grep -n 'CORRECTION-SC' corpus/lessons/round-42.md | cut -c1-110"
rec 24-P10-C2-sabotage  bash "$P/c2-sabotage-run.sh" "$S" "$LANE" "$TIP"
rec 25-P11-lesson-pointers bash "$P/p11-pointers.sh" "$LANE" "$TIP"
echo DONE
