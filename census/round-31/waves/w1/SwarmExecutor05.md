# SwarmExecutor05 — C1 bindings for L30–L41 (round 31, wave 1)

## Status

STATUS: PASS — all 12 assigned capability-cell items (L30–L41) are bound by append-only supersession rows and the frozen counter reads MATCH for every one, twice, unbound=0 mismatches=0 at the scratch landing commit `af9c0806c2df687b90560af1577cde9ed1ff917a` built on lane tip `1b811368461785040e955f41f9c97e62f61fd67c`.

## Evidence

Preregistration read first: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-31/records/preregistration.txt` (base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, prereg `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, controls `ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc`). Counter contract read from the docstring of `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-cells.py:1-42` and the run/record predicates at `:196-260`.

1. Base enumeration (measured, not copied): `python3 -B tools/souji-capability-cells.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --scratch /fast/scratch/hyaku/souji-r31/C1BindE/cntbase` → `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=9f17a1ef…` (matches the frozen baseline), with L30/L31/L36/L38/L40 MATCH, L32/L33/L35 RUN-MISMATCH, L34/L37/L39/L41 UNBOUND.
2. Lane tip: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse master` = `1b811368461785040e955f41f9c97e62f61fd67c`; `git diff --stat 9f17a1e..1b81136 -- SCORECARD.md` is empty, so the base bytes are a prefix of the tip file and append-only holds.
3. Provenance: for each item the base SCORECARD line was read (`git show 9f17a1e:SCORECARD.md`, lines 171–175, 313–314, 355), the writing commit named with `git log -S`/`git blame`, and the record it cites read (`census/round-24/records/c1-control-stub.tsv`, `census/round-29/records/c1-fixture-red-before.txt`, `census/round-29/records/c2-fixture-red-before.txt`, `census/round-30/records/c2-fixture-red-before.txt`); all four blob OIDs are identical at base and tip.
4. Acceptance: scratch clone `/fast/scratch/hyaku/souji-r31/C1BindE/clone` (`git clone -q --no-local … ; git remote remove origin`, detached at `1b81136`, scratch identity via `git -C`), rows appended under `### Round 31 capability-cell supersessions`, committed `af9c080`. Counter with `--root <clone> --rev af9c0806c2df687b90560af1577cde9ed1ff917a --base 9f17a1e… --list-rev 1d45496a… --only L30,…,L41 --scratch /fast/scratch/hyaku/souji-r31/C1BindE/cnt` run twice, byte-identical:
   `SUMMARY items=12 bound_run=8 bound_record=4 unbound=0 mismatches=0 partial=1 rev=af9c0806c2df687b90560af1577cde9ed1ff917a`, RC=0; every ITEM line `MATCH`.

Observed run lines at the measured revision: `selftest=8/8` (L30); `selftest=8/8` (L31); `selftest=15/15` (L32); `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` (L33); `cases=9 pass=9 control=FALSE-GREEN-REJECTED` (L35); `cases=20 pass=20 control=FALSE-GREEN-REJECTED` (L36); `cases=15 pass=15 control=TAMPER-REJECTED` (L38); `cases=7 pass=7 control=FALSE-GREEN-REJECTED` (L40).

## Findings

1. `SCORECARD.md:173` (L32): the cell states 9/9 but the committed fixture prints `selftest=15/15` at `1b81136`; the row restates 15/15. Location: `SCORECARD.md:173`, `tests/fixtures/r23-record-agreement.py`.
2. `SCORECARD.md:174` (L33): the cell states 8/8 but the fixture prints `cases=12 pass=12 …`; the row restates the printed line. Location: line 174, `tests/fixtures/r24-size-census.py`.
3. `SCORECARD.md:175` (L35): the cell's command is incomplete — the fixture requires `--tool`; observed rc=2, `error: the following arguments are required: --tool`. The row supplies `--tool tools/souji-coverage-agreement.py`, the fixture's own usage line at `tests/fixtures/r24-coverage-agreement.py:14` (`python3 -B tests/fixtures/r24-coverage-agreement.py --tool <path>`), and binds 9/9 as `cases=9 pass=9`. This corrects the invocation, not the predicate.
4. `SCORECARD.md:174:4/8` (L34), `:313:8/20` (L37), `:314:8/15` (L39), `:355:3/7` (L41) are base/red-before counts with no command beside them. Each is bound to the pre-round receipt the writing round itself cited, in the receipt's own notation with the base integers preserved: `census/round-24/records/c1-control-stub.tsv` `cases=8 pass=4` (cited at `corpus/lessons/round-24.md:18`); `census/round-29/records/c1-fixture-red-before.txt` `cases=20 pass=8` (cited at `corpus/lessons/round-29.md:60`); `census/round-29/records/c2-fixture-red-before.txt` `cases=15 pass=8` (cited at `corpus/lessons/round-29.md:61`); `census/round-30/records/c2-fixture-red-before.txt` `cases=7 pass=3` (named by the cell and at `corpus/lessons/round-30.md:65`). Each round K is in the item's `rounds` set, no path component is `waves` or `transcripts`, and each blob is unchanged base→tip.
5. L30/L31/L36/L38/L40 already matched through their base-cell commands; their rows restate the same literal explicitly so the binding lives in the cell record, not only in the base row. Removing those five rows would not break them.
6. Global target is not yet met by this seat alone: other items in `census/round-31/c1-cells.tsv` remain for other seats; this delivery covers exactly L30–L41 and shows 12/12 MATCH under the frozen counter.

## Risk / hand-off notes

- The L1 must append the rows after the base SCORECARD bytes (any position in the tail is read; the last row per id wins). The row text is in the delivery file verbatim.
- L32/L33 literals are grown-count restatements measured at `1b81136`; if any wave-2 commit changes those fixtures, the literal must be re-measured — the counter would then report RUN-MISMATCH.
- No tool installs/upgrades; no pacman transaction; no writes outside the lane wave directory; no git/jj mutation in the lane.
- Scratch `/fast/scratch/hyaku/souji-r31/C1BindE` removed after copying this delivery (below).

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/deliver-c1-bind-L30-L41.md` — exact supersession rows, provenance table, record-OID checks, L35 disclosure, and the two acceptance runs.
- This report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/SwarmExecutor05.md`.
