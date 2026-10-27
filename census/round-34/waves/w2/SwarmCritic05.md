# SwarmCritic05 — r34 w2 seat report (target: AttackG21)

## Status

CONFIRMED with refinement. W1's G21 finding — frozen argv broken by fixture `cwd=/var/tmp`, honest cause
`1dc6785` counter-rejected, unrelated r27 cause `6cb22dc` counter-accepted — survives adversarial review.
Every claim link re-derived from committed bytes at base `9c76c7222a8abff027af42e37f0d160d52526bba` and
frozen list/counter `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`. One diagnostic sentence refined: the root
cause is a stale item line number (245 vs the row's true base position 246), not a 0-based items file.
No honest rule-conforming route; the false-accept key is unique. Evidence review only — no executions performed.

## Evidence

- Frozen row `census/round-34/c1-items.tsv:38` pins `SKILL.md:245`; `git show 9c76c72:SKILL.md | grep -n "^| souji-registry-agreement |"` → **246** (line 245 is the `souji-pre-report-gate` row). Row was at 245 at `4d9bf02^`; `4d9bf02` (r33 integration, ancestor of base) inserted lines above.
- Counter `census/round-34/c1-counter.py:293-301` (at 2b0171e): `line_text = blob(root, list_rev, "SKILL.md").split("\n")[lineno-1]` with lineno=245 → the pre-report-gate row; rejection when the text is in the cause's parent or not in the cause.
- Honest cause `1dc678500c92164b0b2bea82b934dd03d1dfbf38`: parent `b8620071...` already contains line-245 text (`grep -cF`=1) → rejected; parent lacks line-246 text (=0), cause has it (=1) → would pass if the line were correct.
- Bogus cause `6cb22dc20c9fdb3c7a49eaa1accabca339054c17`: parent `2706527...` lacks line-245 text (=0), cause has it (=1); `git log -S "<line-245 text>" -- SKILL.md` → only 6cb22dc (unique key). Fixture absent at 6cb22dc → the "row's argv failed at the cause" check passes vacuously.
- Fixture `tests/fixtures/r29-registry-agreement.py:140-142,18` (base and 1dc6785): tool subprocess `cwd=BASE=/var/tmp/souji-r29-c1-fixture` → relative `--tool` ENOENT; committed control `census/round-34/records/controls-c1-do-nothing.txt:22` records exactly that (`MISMATCH original rc=1`).
- Counter executes restated argv via `bash -c` with cwd=clone → W1's `$PWD`-based correction resolves; W1's two counter executions (honest → `BAD-CAUSE`, bogus → `AGREE ... last=cases=20 pass=20 control=FALSE-GREEN-REJECTED`) are recorded in `.ufo/waves/round-34/w1/deliver-c1-G21.md` and `w1-results.json` (SwarmExecutor04, SwarmExecutor01 L1).
- Q76: no base SCORECARD row binds G21 (`grep -n G21` = 0 hits); L36 (:401, cell :313) uses the default-tool form and does not bind the SKILL row.
- Freeze drift: G21's TSV row and all of `c1-counter.py` byte-identical between 2b591924 and 2b0171e.

## Findings

1. W1's defect claim is real, deterministic, and reachable — no measurement artifact (unique `-S` forgery key; deterministic code path; committed control record).
2. Gate inversion confirmed: honest cause rejected, false provenance accepted; with the item line at 246, W1's exact proposed row passes every frozen check (verified link-by-link), so the smallest safe correction is a frozen-list renumber (L1 ruling), not a counter indexing change.
3. All alternate honest routes closed: `same` (original argv never holds), true-cause argv-correction (line check), `where`-renumber (`BAD-ROW(where or kind)` + frozen TSV), L36 prior-correction (non-binding; arithmetic unchanged).
4. W1's "0-based items file" phrasing refined: number was correct at `4d9bf02^`, stale at the pinned base. Executor13's "environment-conditioned mismatch" note is compatible, not contradictory.
5. Probes not run: live counter/clones (77 MB > 50 MB scratch ceiling), live fixture (shared `/var/tmp` path, Q77 race risk with live peers). Execution claims rest on W1's committed receipts; everything else is committed-bytes derivation.

## Attack log

- Read W1 G21 deliverable + w1-results.json G21 lines (Executor01/04/13, Scribe35), frozen TSV/counter/prereg/Q75-Q78, committed do-nothing control, base SCORECARD 313/401.
- Read-only probes only: `git show`/`grep -n`/`grep -cF`/`git log -S`/`diff` at pinned revisions (row positions at 9c76c72/2b0171e/4d9bf02/4d9bf02^/1dc6785; both cause transitions; pickaxe uniqueness; fixture cwd presence/absence; freeze-drift diff).
- Falsification attempts that failed: alternate numbering convention; four honest-route constructions; artifact theory of the bogus acceptance; freeze-revision drift.
- No lane/frozen/other-repo mutations; no commits.

## Deliveries

- `.ufo/waves/round-34/w2/AttackG21.md`
- `.ufo/waves/round-34/w2/SwarmCritic05.md` (this file)
