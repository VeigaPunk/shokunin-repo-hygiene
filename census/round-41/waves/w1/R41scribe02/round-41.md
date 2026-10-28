## Corrections to filed round-40 statements

Appended in round 41. The round-40 text is not rewritten. Each CORRECTION line carries the value that the frozen counter `census/round-41/c1-counter.py` derives at `bffcc0f660ff36eb8add3f61582748a7af019a5b`, the revision the round-40 spot-check measured.

### I1 — `corpus/lessons/round-40.md` § Assimilation gate: "`worktree.c` appears in 9 rows"

Why the filed statement was wrong: at bffcc0f the registry holds two rows whose text contains `worktree.c` (S009 cites the file as a v2.55.0 source; S033 names it in its notes cell), not nine, and no row contains `v2.56.0/worktree.c`. The round-40 spot-check's "1 row" also undercounts; the counter's row count is 2.

Counting command (the counter's derivation, run by hand; a plain `grep -c 'worktree\.c'` over the file gives 3 lines, one of them the non-row bullet at line 240, which is not counted):

```
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/SOURCES.md | grep -E '^\| S[0-9]+ ' | grep -c 'worktree\.c'
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/SOURCES.md | grep -E '^\| S[0-9]+ ' | grep -c 'v2\.56\.0/worktree\.c'
```

CORRECTION I1 file=corpus/lessons/round-40.md filed=9-rows derived=rows=2,v2.56.0=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=S258

Source S258 is the tier-A mined registry row for git v2.56.0 `worktree.c`, opened 2026-10-28, drafted by another seat. It is not in the scratch clone that the scorer uses, so the scorer reports `sourced=0` for this line.

### I3 — `SCORECARD.md` r40 C1 row: "like-for-like" before→after

Why the filed statement was wrong: the two arms ran over different register files. `c1-before.txt` (measured_at `0242085`) used `--register census/round-39/cells.tsv` and reports `register_cells=6`; `c1-after-h.txt` (measured_at `dc8bd47`) used `--register census/round-40/cells.tsv` and reports `register_cells=3`. The register-arm before→after is therefore not like-for-like.

Counting command:

```
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:census/round-40/records/c1-before.txt | grep -o 'register_cells=[0-9]*' | head -1
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:census/round-40/records/c1-after-h.txt | grep -o 'register_cells=[0-9]*' | head -1
```

CORRECTION I3 file=SCORECARD.md filed=like-for-like derived=before=6,after=3 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-

### I4 — `LOG.md` r40 entry: dead-seat provider error recorded in the wave evidence

Why the filed statement was wrong: the LOG.md r40 entry says two dead seats failed with the provider error `flagged as potentially violating our usage policy` and that "all wave evidence is captured under `census/round-40/waves/`". The error text occurs in LOG.md only; none of the 136 committed files under `census/round-40/waves/` at bffcc0f contains it, so the evidence the sentence points to does not record it.

Counting command:

```
git ls-tree -r --name-only bffcc0f660ff36eb8add3f61582748a7af019a5b census/round-40/waves/ | while read -r f; do git show "bffcc0f660ff36eb8add3f61582748a7af019a5b:$f" | grep -c 'flagged as potentially'; done | awk '{s+=$1} END{print s+0}'
```

CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-
