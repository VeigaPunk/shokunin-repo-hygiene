#!/bin/bash
# Read-only chronology evidence for round-60 control receipts (lane repo at c7228424).
L=/home/vgpnk/Projects/shokunin/souji-shokunin
FZ=2670e96af1b81c7aa793acc34d40361b4beecff8
SP=c7228424c3919ecf142bab1aec8181722d86467b
PRE=3b5525099356e15ff9d17b7fbd2835c2d3512eee
RV=d05a00019835dee5b9bb8fe738add080434c4d67
cd /tmp
run(){ echo "\$ $*"; "$@"; echo "EXIT=$?"; echo; }
echo "## A. object existence"
run git -C "$L" rev-parse --show-toplevel
run git -C "$L" cat-file -t $SP
run git -C "$L" cat-file -t $FZ
run git -C "$L" cat-file -t $PRE
run git -C "$L" cat-file -t $RV
echo "## B. adding commit of each r60 receipt and of the preregistration (oldest = freeze)"
for p in census/round-60/controls/c1-do-nothing.txt census/round-60/controls/c2-do-nothing.txt census/round-60/preregistration.txt; do
  run git -C "$L" log --diff-filter=A --no-renames --full-history --format='%H %cI %s' -- "$p"
done
run git -C "$L" show -s --format='%H %cI %s' $FZ
run git -C "$L" log --diff-filter=A --no-renames --full-history --format='%H' -- census/round-60/preregistration.txt
echo "## C. ancestry of each adding commit relative to the freeze commit (strict = add != freeze AND is-ancestor)"
for p in census/round-60/controls/c1-do-nothing.txt census/round-60/controls/c2-do-nothing.txt; do
  ADD=$(git -C "$L" log --diff-filter=A --no-renames --full-history --format='%H' -- "$p" | tail -n 1)
  echo "receipt=$p add=$ADD"
  run git -C "$L" merge-base --is-ancestor "$ADD" "$FZ"
  if [ "$ADD" = "$FZ" ]; then echo "STRICT=NO (adding commit IS the freeze commit)"; else echo "STRICT=YES"; fi; echo
done
echo "## D. receipt blobs at the claimed commit (3b55 is the commit the prereg prose names)"
run git -C "$L" cat-file -e $FZ:census/round-60/controls/c1-do-nothing.txt
run git -C "$L" cat-file -e $FZ:census/round-60/controls/c2-do-nothing.txt
run git -C "$L" cat-file -e $PRE:census/round-60/controls/c1-do-nothing.txt
run git -C "$L" cat-file -e $PRE:census/round-60/controls/c2-do-nothing.txt
run git -C "$L" ls-tree -r --name-only $PRE census/round-60/controls
run git -C "$L" ls-tree -r --name-only $FZ census/round-60/controls
run git -C "$L" show --stat --format='%H %s' $FZ
echo "## E. the preregistration prose that names 3b55 (freeze commit blob)"
run git -C "$L" show $FZ:census/round-60/preregistration.txt
run git -C "$L" merge-base --is-ancestor $PRE $FZ
echo "## F. routed-defect claims at spot-check commit"
run git -C "$L" grep -c freeze-record-substance-binding $SP -- corpus/README.md
run grep -c freeze-record-substance-binding "$L/corpus/README.md"
run ls -l "$L/census/round-60/w1/S60ExecFreezeArm/byte-identical.txt"
run ls -l "$L/census/round-60/wave/w1/S60ExecFreezeArm/byte-identical.txt"
run grep -l S60CriticRound -r "$L/census/round-60/wave/w1/"
run cmp "$L/census/round-60/wave/w1/S60CriticRound.md" "$L/census/round-60/wave/w1/S60CriticRound/S60CriticRound.md"
run grep -n freeze-record-substance-binding "$L/corpus/lessons/round-60-verifier-spotcheck.md"
