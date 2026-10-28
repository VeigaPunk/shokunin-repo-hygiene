## Corrections to filed round-40 statements

Each line below corrects one filed round-40 statement. The filed text is not rewritten. The `derived` value is the frozen counter's own derivation (`census/round-41/c1-counter.py`) at `bffcc0f660ff36eb8add3f61582748a7af019a5b`, re-derived from committed bytes.

CORRECTION I1 file=corpus/lessons/round-40.md filed=9-rows derived=rows=2,v2.56.0=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=S258

I1 — the round-40 assimilation gate (`corpus/lessons/round-40.md` line 49) says `worktree.c` "appears in 9 rows" of `corpus/SOURCES.md`. At the measured revision the registry holds 2 rows whose cells contain `worktree.c` (S009 and S033) and 0 rows containing `v2.56.0/worktree.c`. S009 cites `worktree.c` at tag v2.55.0 only, so the lane held git's prune gate at v2.55.0, not at v2.56.0. The source token names the registry row that cites git v2.56.0 `worktree.c` (tier A, mined, opened 2026-10-28); that row is not in this file and is not evidence in this file.

CORRECTION I3 file=SCORECARD.md filed=like-for-like derived=before=6,after=3 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-

I3 — the round-40 C1 row of `SCORECARD.md` (line 791) reads `c1-before.txt` and `c1-after-h.txt` as one before-to-after measurement. The two receipts ran over different register files: `c1-before.txt` names `--register census/round-39/cells.tsv` and reports `register_cells=6`; `c1-after-h.txt` names `--register census/round-40/cells.tsv` and reports `register_cells=3`. The register arm is not like-for-like, so the before-to-after pair cannot be read as a single change.

CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-

I4 — the round-40 entry of `LOG.md` (line 1909) records the two dead seats (R40w2reviewer01 and R40w2reviewer04) with the provider error text "your prompt was flagged as potentially violating our usage policy". Under `census/round-40/waves/` at the measured revision, that text occurs 0 times across the 136 committed files. The error text is recorded in `LOG.md` only; the committed wave evidence does not carry it.
