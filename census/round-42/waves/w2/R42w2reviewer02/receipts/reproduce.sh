#!/usr/bin/env bash
# R42w2reviewer02 — reproduction of the round-42 lesson Mistakes (M42-1..M42-6) and the Q103-Q105 rows.
# Read-only on the lane: every git mutation is in a scratch clone under $S (toplevel asserted), every tool
# runs with explicit --root/--scratch. Output: receipts/reproduce.txt (the seat directory only).
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
SEAT="$LANE/.ufo/waves/round-42/w2/R42w2reviewer02"
FLEET=/home/vgpnk/Projects/shokunin
S=/fast/scratch/hyaku/souji-r42/R42w2reviewer02/run
TIP=3105a63b23481fccf7df58e74d14a6681e0ea0c8
BASE=bf618f6c5c09d302994871c94903abbea2deb60d
R41TIP=0c9581a44a2e
PATCH_REPOINT=51f204fb7c633b691a3ca9cd8c0bf025f6e0a093
PATCH_REPOINT0=e95b13beb5b690f0bf80034c12c1ac7b6650bb45
FREEZE=afe17f416eec04dcf3f480b580a8f928de61d19d
INSTR=b7408095543579ac71b33ecf7b80b0cb8ef45036
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
mkdir -p "$S" "$SEAT/receipts" || exit 2
trap 'rm -rf -- "$S"' EXIT
export TMPDIR="$S"
OUT="$SEAT/receipts/reproduce.txt"
: > "$OUT"
cd "$LANE" || exit 2

say() { printf '\n## %s\n' "$*" >> "$OUT"; }
run() { printf '$ %s\n' "$*" >> "$OUT"; "$@" >> "$OUT" 2>&1; printf 'rc=%s\n' "$?" >> "$OUT"; }
runsh() { printf '$ %s\n' "$1" >> "$OUT"; bash -c "$1" >> "$OUT" 2>&1; printf 'rc=%s\n' "$?" >> "$OUT"; }

# clone helper: mkclone NAME REV SRC DEST  -> $S/NAME with DEST replaced by SRC and committed (clone only)
mkclone() {
  local C="$S/$1"
  git clone -q --shared "$LANE" "$C" || return 2
  [ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ] || { echo "toplevel mismatch $C"; return 2; }
  git -C "$C" checkout -q "$2" || return 2
  cp "$3" "$C/$4" || return 2
  git -C "$C" add -A && git -C "$C" commit -q --allow-empty -m candidate || return 2
  git -C "$C" rev-parse HEAD
}

say "M42-2 / Q103: gate both modes at base, at the two repoint commits and at the r41 tip and the landed tip"
run python3 -B tools/souji-landing-gate.py --root "$LANE" --rev "$BASE" --round 41
run python3 -B tools/souji-landing-gate.py --root "$LANE" --rev "$BASE" --round 41 --fleet-root "$FLEET"
run python3 -B tools/souji-landing-gate.py --root "$LANE" --rev "$PATCH_REPOINT0" --round 41
run python3 -B tools/souji-landing-gate.py --root "$LANE" --rev "$PATCH_REPOINT0" --round 41 --fleet-root "$FLEET"
run python3 -B tools/souji-landing-gate.py --root "$LANE" --rev "$PATCH_REPOINT" --round 41
run python3 -B tools/souji-landing-gate.py --root "$LANE" --rev "$PATCH_REPOINT" --round 41 --fleet-root "$FLEET"
run python3 -B tools/souji-landing-gate.py --root "$LANE" --rev "$R41TIP" --round 41
run python3 -B tools/souji-landing-gate.py --root "$LANE" --rev "$R41TIP" --round 41 --fleet-root "$FLEET"
run python3 -B tools/souji-landing-gate.py --root "$LANE" --rev "$TIP" --round 41
run python3 -B tools/souji-landing-gate.py --root "$LANE" --rev "$TIP" --round 41 --fleet-root "$FLEET"

say "M42-1: declared-evidence counts at base, the round tip, the r22 / r23 / r24 / r25 / r30 / r35 / r38 tips and r22 attempt-2 tip"
for r in "$BASE" "$TIP" 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd 9301d98c1c689c79741f0f1ba1f171138d20af07 d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7 a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc 94b5e96ab72b40622449af2dfe7c5b6d73118176 ed30b7f5b77939c9073348d810730bc4f355708d "$R41TIP"; do
  run python3 -B tools/souji-declared-evidence.py --root "$LANE" --rev "$r" --file SCORECARD.md --format counts
done
runsh "git grep -n -E 'resolved=420|assertions=490|skipped=810' $TIP -- . ; echo grep-exit=\$?"
runsh "git grep -n 'assertions=' $TIP -- corpus/lessons/round-42.md | cut -c1-160"

say "M42-3 / Q104: C1 counter at the landed tip, control A at the instruments commit, forged control via score-candidate"
run python3 -B census/round-42/c1-counter.py --root "$LANE" --rev "$TIP" --scratch "$S"
run python3 -B census/round-42/c1-counter.py --root "$LANE" --rev "$INSTR" --scratch "$S"
run bash census/round-42/score-candidate.sh c1 "$S" census/round-42/c1-register.tsv=census/round-42/controls/c1-forged-register.tsv

say "M42-3: blank-line sentinel. base+nonblank, base+blank, tip+nonblank, bad row at line 840 (no blank), bad row at line 841 (blank-prefixed)"
{ git -C "$LANE" show "$BASE:SCORECARD.md"; printf '| probe | test | x | r42 |'; } > "$S/base-nonblank.md"
{ git -C "$LANE" show "$BASE:SCORECARD.md"; printf '\n| probe | test | x | r42 |'; } > "$S/base-blank.md"
{ git -C "$LANE" show "$TIP:SCORECARD.md"; printf '| probe | test | x | r42 |'; } > "$S/tip-nonblank.md"
{ git -C "$LANE" show "$BASE:SCORECARD.md"; printf '| probe row | `no/such/path/does-not-exist.md` | x | r42 |'; } > "$S/base-bad840.md"
{ git -C "$LANE" show "$BASE:SCORECARD.md"; printf '\n\n| probe row | `no/such/path/does-not-exist.md` | x | r42 |'; } > "$S/base-bad841.md"
run bash census/round-42/score-candidate.sh c1 "$S" SCORECARD.md="$S/base-nonblank.md"
run bash census/round-42/score-candidate.sh c1 "$S" SCORECARD.md="$S/base-blank.md"
run bash census/round-42/score-candidate.sh c1 "$S" SCORECARD.md="$S/tip-nonblank.md"
run bash census/round-42/score-candidate.sh c1 "$S" SCORECARD.md="$S/base-bad840.md"
run bash census/round-42/score-candidate.sh c1 "$S" SCORECARD.md="$S/base-bad841.md"
run python3 -B census/round-42/c1-counter.py --root "$LANE" --rev "$TIP" --scratch "$S"

say "M42-2 (correction): the literal three-row R1 candidate (../ spelling) scored and gated in a clone at the landed tip"
{ git -C "$LANE" show "$BASE:corpus/pointer-exemptions.tsv"
  printf '%s\t%s\n' '../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md' 'fleet-repo wave report resolved only under --fleet-root; cited by corpus/README.md:217 (R41-D-LG-DANGLING | round-42)'
  printf '%s\t%s\n' '../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md' 'fleet-repo wave report resolved only under --fleet-root; cited by corpus/README.md:217 (R41-D-LG-DANGLING | round-42)'
  printf '%s\t%s\n' '.ufo/waves/hyaku/jj-w1/reports/' 'fleet-repo wave report directory; cited by corpus/knowledge/jj-colocation-receipts.md:148 (R41-D-LG-DANGLING | round-42)'
} > "$S/r1-literal.tsv"
REVL=$(mkclone r1lit "$TIP" "$S/r1-literal.tsv" corpus/pointer-exemptions.tsv) && {
  printf 'literal clone rev=%s\n' "$REVL" >> "$OUT"
  run python3 -B "$S/r1lit/tools/souji-landing-gate.py" --root "$S/r1lit" --rev "$REVL" --round 41
  run python3 -B "$S/r1lit/tools/souji-landing-gate.py" --root "$S/r1lit" --rev "$REVL" --round 41 --fleet-root "$FLEET"
}
run bash census/round-42/score-candidate.sh r1 "$S" corpus/pointer-exemptions.tsv="$S/r1-literal.tsv"

say "M42-2 (correction): the loader-admissible variant (.ufo/waves spelling) gated in a clone at the base"
{ git -C "$LANE" show "$BASE:corpus/pointer-exemptions.tsv"
  printf '%s\t%s\n' '.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md' 'fleet-repo wave report file resolved only under --fleet-root; cited by corpus/README.md:217 (R41-D-LG-DANGLING | round-42)'
  printf '%s\t%s\n' '.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md' 'fleet-repo wave report file resolved only under --fleet-root; cited by corpus/README.md:217 (R41-D-LG-DANGLING | round-42)'
  printf '%s\t%s\n' '.ufo/waves/hyaku/jj-w1/reports/' 'fleet-repo wave report directory; cited by corpus/knowledge/jj-colocation-receipts.md:148 (R41-D-LG-DANGLING | round-42)'
} > "$S/r1-variant.tsv"
REVV=$(mkclone r1var "$BASE" "$S/r1-variant.tsv" corpus/pointer-exemptions.tsv) && {
  printf 'variant clone rev=%s\n' "$REVV" >> "$OUT"
  run python3 -B "$S/r1var/tools/souji-landing-gate.py" --root "$S/r1var" --rev "$REVV" --round 41
  run python3 -B "$S/r1var/tools/souji-landing-gate.py" --root "$S/r1var" --rev "$REVV" --round 41 --fleet-root "$FLEET"
}

say "C2 / freeze: freeze check at the freeze commit"
run python3 -B tools/souji-freeze-check.py --root "$LANE" --prereg census/round-42/preregistration.txt --rev "$FREEZE"

say "M42-4 / C3 survey: the seven extra mutants against the eight prior drift fixtures (survey-prior.py at the lane)"
run python3 -B census/round-42/records/survey-prior.py --lane "$LANE" --scratch "$S"

say "M42-4: pristine prior fixtures at the landed tip (the prior=8/8 leg), run one by one"
git -C "$LANE" show "$TIP:tools/souji-worktree-drift.py" > "$S/pristine.py"
for f in r36-worktree-drift r37-drift-discrimination r38-drift-record r38-drift-write-envelope r39-drift-record-rules r40-drift-record-branches r41-drift-record-order r41-refusal-sites; do
  git -C "$LANE" show "$TIP:tests/fixtures/$f.py" > "$S/$f.py"
  W=$(mktemp -d -p "$S" w.XXXXXX)
  printf '$ python3 -B %s.py --tool pristine.py --work <dir>\n' "$f" >> "$OUT"
  TMPDIR="$W" python3 -B "$S/$f.py" --tool "$S/pristine.py" --work "$W" > "$S/o.txt" 2>&1; rc=$?
  grep -E '^SUMMARY' "$S/o.txt" | tail -1 >> "$OUT"; printf 'rc=%s\n' "$rc" >> "$OUT"
done

say "M42-4: F1 (the r41 'equivalent' mutant) against r36-worktree-drift.py, three runs"
python3 - "$S/pristine.py" "$S/F1.py" <<'PYEOF'
import sys
src = open(sys.argv[1]).read()
old = "alias = record_abs == json_target"
assert src.count(old) == 1, src.count(old)
open(sys.argv[2], "w").write(src.replace(old, "alias = False"))
PYEOF
for i in 1 2 3; do
  W=$(mktemp -d -p "$S" w.XXXXXX)
  printf '$ python3 -B r36-worktree-drift.py --tool F1.py --work <dir>   (run %s)\n' "$i" >> "$OUT"
  TMPDIR="$W" python3 -B "$S/r36-worktree-drift.py" --tool "$S/F1.py" --work "$W" > "$S/o.txt" 2>&1; rc=$?
  grep -E '^SUMMARY' "$S/o.txt" | tail -1 >> "$OUT"; printf 'rc=%s (rc 1 would mean killed)\n' "$rc" >> "$OUT"
done

say "M42-5: preregistration misstatements — freeze-commit adds/modifies, control receipt history, digests, Target strings"
runsh "git -C $LANE show --name-status --format= $FREEZE -- census/round-42/controls census/round-42/c2-cases.tsv census/round-42/preregistration.txt"
runsh "git -C $LANE show $TIP:census/round-42/c1-counter.py | sha256sum; git -C $LANE show $INSTR:census/round-42/c1-counter.py | sha256sum; git -C $LANE show 410316c:census/round-42/c1-counter.py | sha256sum"
runsh "git -C $LANE show 410316c:census/round-42/controls/c1-control.txt; echo grep-rc=\$?"
runsh "git -C $LANE log --format='%h %s' -- census/round-42/controls/c1-control.txt | cut -c1-90"
runsh "git -C $LANE show b740809:census/round-42/controls/c1-control.txt | grep -n class_ok"
runsh "sed -n '5p;20p;30p;41p;51p' $LANE/census/round-42/preregistration.txt | cut -c1-220"
runsh "git -C $LANE show b740809 --stat --format=%h | cat"

say "C1 CORRECTION digests (lesson lines 14, 68, 92, 175)"
runsh "git -C $LANE show 778747eb671f8e85ef5387bc3d7023337b30467c:tools/souji-size-census.py | sha256sum"
runsh "git -C $LANE show 1efe406e7f39b8fe736be2a566053703a571ffc0:tests/fixtures/r24-coverage-agreement.py | sha256sum"
runsh "git -C $LANE show 1efe406e7f39b8fe736be2a566053703a571ffc0:tools/souji-coverage-agreement.py | sha256sum"
runsh "git -C $LANE show $BASE:tools/souji-coverage-agreement.py | sha256sum"
runsh "git -C $LANE show 604cd441:tools/souji-coverage-agreement.py | sha256sum; git -C $LANE merge-base --is-ancestor 604cd441 $BASE; echo ancestor-of-base-rc=\$?; git -C $LANE merge-base --is-ancestor 7e4dbef94061578fca2f58621f87908c886cc431 $BASE; echo 7e4dbef-ancestor-of-base-rc=\$?"
runsh "git -C $LANE ls-tree -r --name-only $BASE | grep '/c2-after.tsv\$'"
runsh "git -C $LANE log --format='%h %s' -1 $TIP | cat; git -C $LANE grep -c '^| S259 ' $TIP -- corpus/SOURCES.md; git -C $LANE grep -c '^| S' $TIP -- corpus/SOURCES.md"
runsh "for c in \$(git -C $LANE log --format=%H -- tools/souji-declared-evidence.py); do h=\$(git -C $LANE show \$c:tools/souji-declared-evidence.py | sha256sum | cut -d' ' -f1); case \$h in 65817d0d*) echo \$h;; esac; done"

say "M42-6: sitecustomize premise — S259 snapshot quote lines and the probe receipts"
runsh "grep -n 'attempt is made to import a module named' $LANE/census/round-42/sources/python-3-library-site.html | cut -c1-120; grep -n 'automatic' $LANE/census/round-42/sources/python-3-library-site.html | head -3 | cut -c1-160; sha256sum $LANE/census/round-42/sources/python-3-library-site.html"
runsh "grep -n -i 'unreach\\|-I\\b' $LANE/census/round-42/records/c2-after.txt | head -3; echo grep-done"

say "census start receipt (frontier step)"
runsh "head -4 $LANE/census/round-42/records/census-before.txt"

say "done"
