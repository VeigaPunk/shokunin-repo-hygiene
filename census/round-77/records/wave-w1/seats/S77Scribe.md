# S77Scribe — round-77 corpus text (SOURCES S321/S322, two knowledge sections)

VERDICT: drafts delivered and validated (census EXIT=0); every source and count re-derived. 4 findings (1 MEDIUM, 3 LOW), none blocking.
Live worktree already carries L1 drafts of the same rows/sections (corpus/SOURCES.md:280-281, knowledge/filter-filemode-witness.md tail, untracked knowledge/self-assessment-pointer-resolution.md); my drafts differ only where noted. Lane files not edited.

## Sources re-fetched (own)
- `curl -sSL` both URLs: HTTP 200; dir.c 115474 B sha256 53e5ed2b…20a6; git-add.adoc 16586 B sha256 42089b80…65db; `cmp` vs census/round-77/srcs/ both equal (DIR-CMP-OK, ADD-CMP-OK).
- Quote offsets in whitespace-normalized capture (method reproduces S320's published 2355): S321 27673, lines 1164-1167, 13 words; S322 2581, line 78, 5 words.

## Claims re-derived (own runs, not L1 receipts)
- C1 base control: `SUMMARY rows=16 mismatches=9 errors=0 hangs=8` EXIT=1, gate sha 90bdd8c7… == prereg (controls/c1-K-a-do-nothing.txt:38-39); after: `rows=16 mismatches=0 errors=0 hangs=0` EXIT=0 (records/c1-after.txt:30-31); r76 30/30 (:44-45), r36 21/21 (:31-32), r27 `cases=4 pass=4` (:17-18).
- C2: own counter runs → base `resolved=0 unresolved=35` EXIT=1, after (ledger) `resolved=35 …` EXIT=0; ledger composition 10 MOVED/8 FLEET/6 TOKEN/3 LOCAL-POLICY/3 ABSENT/1 QUARANTINED + 4 CAPTURED = 35; captures present at A (cat-file -e).
- Own pointer-check runs: `missing=35` at d4f51563, `missing=31` at ef04ca6c (files=6 checked=2198 skipped=142); receipts records/c2-pointer-check-after.txt:38.

## Validate (acceptance)
- `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <scratch>/corpus/SOURCES.md --root <scratch>` → EXIT=0, 86 pre-existing W04 duplicate-URL warnings, no E codes, final `ok` (S77Scribe/census-validate.txt).
- Fixture: `git archive ef04ca6c corpus tools SKILL.md`, rows inserted after S320, knowledge entry (b) written at corpus/knowledge/self-assessment-pointer-resolution.md. First run's five E11s (tools/souji-size-census.py, SKILL.md) were fixture absences, not row defects.

## Findings
- MEDIUM: the gate's work-tree branch does not follow symlinks (`find … ! -type f`, gate blob W :82-83) while the rule says "a symlink counts by its target" (`[[ -e && ! -f ]]` :72, config :80). Own fixture: find count=1, bracket test=no. Outcome matches git's O_NOFOLLOW per-directory reader (dir.c:1778), so behaviour is defensible but the rule text is false for work-tree sources; no frozen row covers it.
- LOW: prereg/teaches say git "checks the file type only afterwards"; add_patterns has no regularity test — dir.c's only two S_ISREG (:2361,:2385) map d_type, and the sole fstat (:1169) supplies st_size. Blocking-open claim stands; my draft states it precisely.
- LOW: live rows say `fetched 2026-11-07`, `opened 2026-11-07`, `r77 rows n1-n10`; population has n1-n8 + n10 (no n9). Host local 2026-11-06 23:19 / UTC 2026-11-07 and E08 uses `date -u`, so validate passes either way.
- LOW: base pointer-check `missing=35` has no committed receipt (only prereg §C2 + c2-population.tsv header); reproduced in 1.3 s here — worth recording before the report.

## Files written (seat dir .ufo/waves/round-77/w1/S77Scribe/)
S77Scribe.md, sources-rows.md, knowledge-r77.md, census-validate.txt. Scratch /fast/scratch/hyaku/souji-r77/S77Scribe removed. No tools installed; no lane file, git or jj mutation.
