## Corrections to filed round-40 statements

CORRECTION I1 file=corpus/lessons/round-40.md filed=9-rows derived=rows=2,v2.56.0=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=S258
Filed (round-40.md § Assimilation gate, line 49): "`worktree.c` appears in 9 rows of". Re-derived at bffcc0f: 2 registry rows name worktree.c (S009, S033), 0 name v2.56.0/worktree.c. Re-derive: `git show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/SOURCES.md | grep -E '^\|\s*S[0-9]{3,}\s*\|' | grep -c 'worktree\.c'` gives 2; the same with `grep -c 'v2\.56\.0/worktree\.c'` gives 0. The sourced claim is registry row S258: git v2.56.0 builtin/worktree.c, tier A, mined, opened 2026-10-28.

CORRECTION I3 file=SCORECARD.md filed=like-for-like derived=before=6,after=3 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-
Filed (SCORECARD.md line 791): the r40 C1 before->after row. Re-derived at bffcc0f: the before receipt has register_cells=6 and the after receipt has register_cells=3, so the arms ran over different register files and are not like-for-like. Re-derive: `git show bffcc0f660ff36eb8add3f61582748a7af019a5b:census/round-40/records/c1-before.txt | grep -o 'register_cells=[0-9]*'` gives 6; `git show bffcc0f660ff36eb8add3f61582748a7af019a5b:census/round-40/records/c1-after-h.txt | grep -o 'register_cells=[0-9]*'` gives 3.

CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-
Filed (LOG.md line 1909): two dead seats with the provider error "your prompt was flagged as potentially violating our usage policy". Re-derived at bffcc0f: that text occurs 0 times in the committed census/round-40/waves/ tree (136 files). Re-derive: `git grep -c -F 'flagged as potentially' bffcc0f660ff36eb8add3f61582748a7af019a5b -- census/round-40/waves/` prints nothing, so the count is 0.
