# R40w2sentinel05 — push/write scope

## Verdict: INCONCLUSIVE on attribution; SAFE for observed status comparison

Attack: whether round activity wrote outside the lane and its single permitted fleet report path. The fleet status lists unrelated untracked/added files across `.scratch/`, `lane3/`, and root outputs. The lane status is empty. Status snapshots do not establish which round/agent wrote those fleet paths, so attribution cannot be claimed from this evidence. No files were moved or deleted.

## Exact commands and output

Command: `git -C /home/vgpnk/Projects/shokunin status --porcelain`

Output:
```text
 A .scratch/closure-mado-r50.json
 A .scratch/closure-r54/manifest-entry.json
 A .scratch/closure-r54/work-c0/__pycache__/r18measure.cpython-314.pyc
 A .scratch/closure-r54/work-c0/coldread-precheck.sh
 A .scratch/closure-r54/work-c0/mirror/.ufo/evidence/round-18/measure.py
 A .scratch/closure-r54/work-c0/mirror/.ufo/evidence/round-21/coldread/measure.py
 A .scratch/closure-r54/work-c0/r18measure.py
 A .scratch/closure-r54/work-c1-base/__pycache__/r18measure.cpython-314.pyc
 A .scratch/closure-r54/work-c1-base/coldread-precheck.sh
 A .scratch/closure-r54/work-c1-base/mirror/.ufo/evidence/round-18/measure.py
 A .scratch/closure-r54/work-c1-base/mirror/.ufo/evidence/round-21/coldread/measure.py
 A .scratch/closure-r54/work-c1-base/r18measure.py
 A .scratch/closure-r54/work-c1/__pycache__/r18measure.cpython-314.pyc
 A .scratch/closure-r54/work-c1/coldread-precheck.sh
 A .scratch/closure-r54/work-c1/mirror/.ufo/evidence/round-18/measure.py
 A .scratch/closure-r54/work-c1/mirror/.ufo/evidence/round-21/coldread/measure.py
 A .scratch/closure-r54/work-c1/r18measure.py
 A .scratch/closure-r54/work-c2-base/strace-bash-witness-study.log
 A .scratch/closure-r54/work-c2-base/strace-context-capture.log
 A .scratch/closure-r54/work-c2-base/strace-env-diff.log
 A .scratch/closure-r54/work-c2-base/strace-evidence-disposition.log
 A .scratch/closure-r54/work-c2-base/strace-pin-disposition.log
 A .scratch/closure-r54/work-c2-base/strace-registry-check.log
 A .scratch/closure-r54/work-c2-base/strace-repeat-control.log
 A .scratch/closure-r54/work-c2/strace-bash-witness-study.log
 A .scratch/closure-r54/work-c2/strace-context-capture.log
 A .scratch/closure-r54/work-c2/strace-env-diff.log
 A .scratch/closure-r54/work-c2/strace-evidence-disposition.log
 A .scratch/closure-r54/work-c2/strace-pin-disposition.log
 A .scratch/closure-r54/work-c2/strace-registry-check.log
 A .scratch/closure-r54/work-c2/strace-repeat-control.log
 M .scratch/goal-20261028-hyaku-run11.md
 A .scratch/kasegi-r44/R44Critic5/run-tree-suite.err
 A .scratch/kasegi-r44/R44Critic5/run-tree-suite.txt
 A .scratch/kasegi-r44/R44Critic5/work4/j5-fixture/scratch/kasegi-r43-file
 A .scratch/kasegi-r44/R44Critic5/work4/j5-fixture/scratch/kasegi-r44.txt
 A .scratch/kasegi-r44/R44Critic5/work4/j5-fixture/scratch/kasegi-r45-link
 A .scratch/source-routing-queue.md
 A o.bin
 A oldrep1.out
 A oldrep2.out
?? .scratch/closure-r54/lane/
?? .scratch/closure-r54/work-c2-base/clone/
?? .scratch/closure-r54/work-c2/clone/
?? lane3/
```

Command: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain`

Output: empty (no porcelain lines).

## Attack locations
No instrument/fixture file lines attacked; assigned scope was status-based write-scope review. Every fleet path shown above is evidence of present uncommitted status, not attribution to this round. Scratch directory: not created; removed: not applicable.