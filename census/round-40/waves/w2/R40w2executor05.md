# R40w2executor05 — C3 counter run at landed rev, base 0242085

Scratch: /fast/scratch/hyaku/souji-r40/w2/R40w2executor05 (removed by `trap rm -rf` on every command; checked absent at the end).
Installs: none.

## Attacked
- census/round-40/c3-counter.py:96-120 (`score`, kill + failing-name attribution), :123-207 (`main`), :55-68 (anchors + MUTANTS M15-M18)
- tests/fixtures/r40-drift-record-branches.py:94-123 (8 cases), :126-146 (summary/exit)
- tools/souji-worktree-drift.py:147 (decode anchor)

## Commands and real output

### A. Counter as it sits on disk (HEAD 549d9ec, includes 8a5fbdb attribution fix), rev = landed 128e412
```
TMPDIR=$S python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c3-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e \
  --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S
```
```
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
exit=0
```
Same output with --rev 549d9ec53a1f5932337ff14438fcd22b0621828d (tool_sha/fixture_sha identical → tool and fixtures unchanged between the two revs).

### B. Counter bytes AS LANDED at 128e412 (`git show 128e412:census/round-40/c3-counter.py > $S/c3-landed.py`), same args
```
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
exit=0
```
Counter history: `git log --oneline -- census/round-40/c3-counter.py` → 8a5fbdb (fix), 128e412 (landed).

### C. Extra probe (not a declared mutant): strict decode `.decode("utf-8")` at tools/souji-worktree-drift.py:147
Fixture `--tool strict.py` → case-invalid-utf8-in-repo-name=FAIL, case-invalid-utf8-in-comment=FAIL, `SUMMARY cases=8 pass=6 fail=2`, exit 1. The comment case, which none of M15-M18 exercises, does detect a decode change — it is a live case.

## Findings
1. Verdict SAFE for the preregistered C3 predicate: pristine ok, 4/4 mutants killed, base_killed=0, fixture emits its own `SUMMARY cases=8 pass=.. fail=..`, counter exit 0. Reproduced at both 128e412 and 549d9ec.
2. FALSIFIED (cosmetic, repaired): at the landed 128e412 the counter docstring (c3-counter.py:24-27 "prints the failing case names") was false — the filter `l.endswith("FAIL")` (landed line 116-117) never matches a FAIL line, since failing cases print `=FAIL <detail>`, so every MUTANT line showed `failing=-` (output B). Kill verdicts were unaffected. Repaired in 8a5fbdb (`"=FAIL" in l.split(" ",1)[0]`), output A shows names populated.
3. Weak spots (no falsifier): case `good` and `skip-unrecorded-suppresses` are the identical record+flags (fixture :99-104, :111-112), so M16 failing=4 counts duplicates; `total-duplicate-identical` is not killed by M15 (identical rows agree), it only pins that identical duplicates are accepted.

## Verdict
C3 run: SAFE (command A). Attribution defect at 128e412: FALSIFIED then repaired (command B vs A).
