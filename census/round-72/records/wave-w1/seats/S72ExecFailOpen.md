# S72ExecFailOpen — WM7 reachability (souji r72 w1)
VERDICT: WM7 is REACHABLE on git 2.56.0: a crafted index path makes `git check-attr` exit 128 while
`git ls-files` exits 0; the r72 writer refuses, the WM7 mutant writes a receipt over a forged same-size
tracked file hidden by a clean driver. HIGH.
Commands (scratch /fast/scratch/hyaku/souji-r72/S72ExecFailOpen): `bash final-table.sh > trigger-table.txt`;
`bash run-final-demo.sh > wm7-demo.txt`; `diff -u writer-base.py writer-WM7.py > wm7-mutant.diff`; writer runs
`python3 -B {writer-base,writer-WM7,writer-base-r70}.py --root <fx> --rev <HEAD> --instrument g.txt --out <fx>/<o> --allow-dirty --command true`.
Trigger table (19 probes, ls_rc=0 every row; full text trigger-table.txt): T1 .gitattributes dir rc=0 |
T2 dangling symlink rc=0 (ELOOP warning) | T3 symlink->FIFO rc=0 (ELOOP, no hang) | T3b real FIFO rc=124
hang | T4 info/attributes 000 rc=0 (Permission denied) | T4b dir rc=0 | T5 8MiB line rc=0 | T5b 128MiB
rc=0 | T6 invalid macro rc=0 | T7 attributesFile dir rc=0 | T7b missing rc=0 | T8 non-UTF8 path rc=0 |
T9 attr.tree missing object rc=0 | T9b attr.tree HEAD rc=0 | T10 attributesFile=/dev/zero (ulimit 256M)
rc=128 "fatal: Out of memory, getdelim failed" | T11 core.worktree nonexistent rc=128 "fatal: this
operation must be run in a work tree" | T11b core.worktree regular file rc=128 same | T12 bare+worktree
rc=0 (warning) | T13 crafted index path ../ev rc=128 "fatal: '../ev' is outside repository at '<top>'".
WM7 vs writer for each rc!=0 trigger (wm7-vs-writer.txt, wm7-demo.txt): T11/T11b both refuse earlier at
"cannot read index flags ... cannot change to '<core.worktree>'" (top from rev-parse is the bogus
worktree), so WM7 is never reached; T10 real refuses at check-attr, WM7 proceeds but status re-reads
/dev/zero and refuses "cannot read worktree status ... Out of memory"; T13 real rc=2 "refused: cannot read
filter attributes ... fatal: '../ev' is outside repository", WM7 rc=0 and writes a receipt, base writer
8b9345b1 rc=0 and writes a receipt (base_expect=accept). Forgery: worktree f.txt "BBBB\n" vs HEAD blob
"AAAA\n"; status with driver empty, driver off " M f.txt".
Evidence: tools/souji-receipt-write.py:169-170 (0bf098dd) is the branch; setup.c:147-155 (git v2.56.0)
is the prefix_path die; attr.c:1203-1227 shows a bad attr.tree is ignored. Writer sha b7790001...244d at
0bf098dd and base writer sha 118597e0...e71f at 8b9345b1 verified. Committed C1/C2 receipts' SUMMARY/EXIT
lines match the frozen claims (grep only; this seat did not re-run the harness).
Findings:
HIGH  WM7 reachable via a crafted index entry whose path escapes the worktree (../ev): check-attr rc 128,
      ls-files rc 0; WM7 writes a receipt over a clean-driver-forged tracked file while the r72 writer
      refuses. Requires writing .git/index directly (update-index/mktree/read-tree reject the path) and --allow-dirty.
MEDIUM Writer hang: a repo-provided FIFO at .gitattributes or core.attributesFile blocks check-attr
      forever (subprocess.run has no timeout); WM7 does not change it (rc=124).
MEDIUM Memory DoS: core.attributesFile=/dev/zero drives check-attr to OOM (rc 128 under a 256M limit);
      status re-reads it, so WM7 still writes no receipt.
LOW   core.worktree bogus config: check-attr rc 128, but the writer refuses earlier at index flags.
LOW   Correction: a .gitattributes symlink to a FIFO does not hang (open_nofollow -> ELOOP warning, rc 0);
      a real FIFO does hang.
Files written under .ufo/waves/round-72/w1/: S72ExecFailOpen.md; S72ExecFailOpen/{trigger-table.txt,
wm7-demo.txt, wm7-vs-writer.txt, wm7-mutant.diff, proposed-row-WM7.md, add-index-entry.py, patch-index.py}.
