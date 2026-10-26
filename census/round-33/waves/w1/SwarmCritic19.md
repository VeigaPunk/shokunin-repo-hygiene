# SwarmCritic19 — C1 K21 falsification (round 33, w1)

## Status
STATUS: PASS — K21 HOLDS: the frozen argv prints `cases=7 pass=7 control=FALSE-GREEN-REJECTED`, rc=0, identically on two runs at 2d9bca55 with fresh TMPDIR (deterministic); the predicate is neither lax nor stricter (base gate and two synthetic tool regressions each break it); the counter prints AGREE. Two out-of-set residuals re-derived and both current.

## Evidence
All runs in scratch `/fast/scratch/hyaku/souji-r33/AuditK21/` (clone of the lane, origin removed, detached at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`, `rev-parse --show-toplevel` = the clone). Scratch tree removed after the run.

1. Determinism, frozen argv at 2d9bca55:
```
$ cd /fast/scratch/hyaku/souji-r33/AuditK21/c
$ TMPDIR=.../t1 python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py
CASE D1 PASS exit=0 reports=2 status=2 findings=0
...
CASE D7 PASS exit=1 reports=1 status=1 findings=1
cases=7 pass=7 control=FALSE-GREEN-REJECTED      # run1 rc=0
                                                  # run2 (fresh TMPDIR) rc=0, byte-identical output
$ env -u TMPDIR python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py
PREREQ FAIL TMPDIR is unset (build synthetic repos under $TMPDIR)
cases=0 pass=0 control=FALSE-GREEN-ACCEPTED       # rc=2
```
2. Counter, exactly as assigned:
```
$ python3 -B .../census/round-33/c1-counter.py --root .../souji-shokunin \
    --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch .../cnt --only K21
ITEM	K21	AGREE	original	rc=0 expect_exit=0 predicate holds last=cases=7 pass=7 control=FALSE-GREEN-REJECTED
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
counter rc=0
```
3. Tool regressions against the same fixture (base gate = `git show 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b:tools/souji-landing-gate.py`, sha256 `02b58f81…f785cd`, matches `census/round-30/records/c2-fixture-red-before.txt`): three runs, all `cases=7 pass=3 control=FALSE-GREEN-REJECTED`, rc=1. Mutant A (`_pointer_candidates` also accepts the capture-mapped *directory*): `CASE D6 FAIL … capture-directory-only resolution`, `cases=7 pass=6`, rc=1. Mutant B (suppress `census/round-*` dangling pointers): `CASE D5 FAIL … missing LG-DANGLING-PTR for census/round-29/does-not-exist.md`, `cases=7 pass=6`, rc=1. In all five runs the control line stayed `FALSE-GREEN-REJECTED`.
4. Residual "base gate 3/7" (§Findings 4) and "seven uncarried" (§Findings 5) re-derived as shown there.

Row cell at SCORECARD.md:355 (base 6017a482), verbatim fragments: `cases=7 pass=7 control=FALSE-GREEN-REJECTED` (base gate 3/7, and, second cell: and ignores template tokens; it surfaced round 29's seven uncarried seat failures.

## Findings
1. **Deterministic.** Two runs at the measured revision with distinct fresh TMPDIR dirs printed byte-identical 7×`CASE Dk PASS` + `cases=7 pass=7 control=FALSE-GREEN-REJECTED`, rc=0. Both TMPDIR dirs were empty after the run (fixture `finally` removes its scratch). Location: `tests/fixtures/r30-landing-gate-discovery.py:main/finally`; `tools/souji-landing-gate.py` (gate temp dir honours caller TMPDIR).
2. **The row's printed argv is incomplete for a bare shell.** With TMPDIR unset the same argv exits 2 and prints `cases=0 pass=0 control=FALSE-GREEN-ACCEPTED` — the fixture's own prerequisite (`prerequisites()`, "TMPDIR is unset"). The counter injects `TMPDIR=<fresh dir under --scratch>` for every item, so AGREE is consistent with the counter's documented run environment, but the row at SCORECARD.md:355 prints no `TMPDIR=` prefix (unlike K24/K25 `TMPDIR={SCRATCH}`). Not a nondeterminism and not a mismatch; a reader reproducing the row text alone gets rc=2. Severity: LOW, textual.
3. **Predicate is faithful — neither lax nor stricter.** The predicate is the row's own line (`cases=7 pass=7 control=FALSE-GREEN-REJECTED`) plus exit 0, which the fixture documents as its only success exit (`Exit 0 iff every case passes and the control is rejected; 1 otherwise`). Live judges: the pre-fix gate drops to 3/7 and two pinned shortcuts (capture-directory-only resolution; blanket suppression of real `census/round-*` pointers) each drop the count to 6/7 — a regressed tool cannot pass the predicate without also satisfying the judges it regresses. No conjunct is stricter than the cell: the cell states that exact line and nothing else for this command.
4. **Out-of-set residual "base gate 3/7" — not stale.** The cell's parenthetical `(base gate 3/7, census/round-30/records/c2-fixture-red-before.txt)` reproduces: base gate blob at 9420341d, sha256 `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd` (exactly the record's), run through the frozen fixture at 2d9bca55 → `cases=7 pass=3 control=FALSE-GREEN-REJECTED`, rc=1 (3 runs, identical), matching record line 32. Location: `census/round-30/records/c2-fixture-red-before.txt:32`.
5. **Out-of-set residual "seven uncarried seat failures" — not stale.** Second cell, SCORECARD.md:355. Re-derived with the current gate at 2d9bca55 against a clone at rev `76c94eb41fc38093d7143a016006b6275e102d5d`, `--round 29 --fleet-root <fleet>`: 7 `LG-SEAT-UNCARRIED` rows on exactly the record's seven files (`census/round-29/waves/w1/` SwarmCritic49/51/53, SwarmExecutor17, SwarmReviewer40/42/43), `SUMMARY findings=7 … checked_reports=86`, rc=1 — identical to `census/round-30/records/m1-r29-carry-red-before.txt`. Without `--fleet-root` the same run gives `findings=10` (3 extra LG-DANGLING-PTR on `../.ufo/waves/hyaku/jj-w1/…` fleet pointers, absent by construction); that is an environment difference of the re-derivation, not a stale count in the cell.
6. **Residual one hop from the cell (record wording).** `c2-fixture-red-before.txt:4-5` states its 554-line copy is byte-identical to the committed fixture; at 2d9bca55 the committed fixture is sha256 `70f0fca5f2bab9a75a691d0a2de2c5e551216ee92178935af29c2f82b4d000db`, 555 lines (the 68447af blob is `e8303393…`, 554 lines = the record). The only change is the boundary docstring, made by 98e5203 (r32 C2, scratch from TMPDIR). The record is a historical receipt, so no mismatch; a reader checking byte identity now finds it superseded.
7. **Control conjunct carries no tool signal.** In every run (current gate, base gate, mutant A, mutant B) the always-zero emitter was rejected on D1,D2,D3,D5,D6 — `control=FALSE-GREEN-REJECTED` is a property of the fixture's judging, not of the gate. Only `pass=7` discriminates; the predicate is still faithful to the cell (the cell states the control line), but that conjunct cannot expose a gate regression.

## Attack log
- Attack 1 (determinism): two runs, fresh TMPDIR each; plus one TMPDIR-unset run. Result: identical where the counter's env applies; rc=2 only under the missing prerequisite. HOLDS (not NONDETERMINISTIC).
- Attack 2 (lax predicate): replaced the tool with the historical pre-fix gate → 3/7 rc=1; two synthetic shortcuts (capture-dir-only resolution, blanket suppression) → 6/7 rc=1 each. The predicate rejects all three. Not LAX.
- Attack 3 (stricter predicate): compared the frozen predicate to the cell text; identical line + the fixture's documented success exit. Not STRICT.
- Attack 4 (hidden stale counts in the cell): re-derived "base gate 3/7" (3 runs) and "seven uncarried" (rev 76c94eb). Both current. Byte-identity wording in the pointed-at record is superseded by 98e5203 (label above, out-of-set).
- Verdict: **HOLDS**. Smallest safe correction for the two LOW residuals (not required to save the item): append a restatement-free note is not allowed by the frozen format, so the L1 may record, outside SCORECARD.md, that the row's argv requires `TMPDIR` and that the r30 record's byte-identity line predates 98e5203.
- No frozen predicate/target/counter/item/leg was changed or proposed for change. No lane write beyond this report; lane `git status --porcelain` empty after the runs.

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic19.md` (this report)
- Scratch `/fast/scratch/hyaku/souji-r33/AuditK21` created and removed (verified absent). No tool installs or upgrades.
