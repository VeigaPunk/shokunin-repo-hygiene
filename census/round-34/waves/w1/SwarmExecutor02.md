# SwarmExecutor02 — r34 w1, C1 slice 2/12 (G05, G07, G09, G11, G12)

## Status

STATUS: PARTIAL — 3/5 items AGREE at base and tip (G07, G09, G12); G11 is a genuine value drift and
its `same`-argv restatement row was drafted and validated (AGREE) in a scratch clone; G05 cannot be
restated honestly — two frozen-instrument defects (a predicate that no revision can satisfy, and a
`where` pointer one line short) make its only admissible correction bind a foreign cause. That is
reported as an ATTACK with a reproduced state and a mechanically valid, explicitly disclaimed row.

## Evidence

Base `9c76c7222a8abff027af42e37f0d160d52526bba`; list-rev `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`;
lane HEAD at read time `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.

```
export TMPDIR=/fast/scratch/hyaku/souji-r34/RestateC1s2/tmp
flock /fast/scratch/hyaku/souji-r34/RestateC1s2/ser.lock \
  python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c72… --list-rev 2b0171e… \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s2/cnt --only G05,G07,G09,G11,G12
```

```
ITEM	G05	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=gate-replays: wrote record to …/G05.69ncemxk/s/g5.json load=2.84
ITEM	G07	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=12 failed=0 load=6.94
ITEM	G09	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0 load=7.91
ITEM	G11	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=SUMMARY total=45 pass=45 fail=0 blocked=0 inventory=exact baseline_mismatches=not-requested load=7.91
ITEM	G12	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=32 pass=32 fail=0 base_discriminating=14 load=7.83
SUMMARY items=5 agree=3 mismatches=2 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba
```

Load `/proc/loadavg` before `2.84 2.72 1.92`, after `7.83 4.61 2.74`. Tip run
(`--rev 51acb5f… --only G05,G11`, then `--only G07,G09,G12`) reproduces every verdict with
`rc=0` and identical last lines. Counter sha256 at list-rev
`1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`; items TSV sha256
`5de3678206dcc091d2a2f911f0fe085021c90431d1e40edeea9dd15765b06127`.

Scratch restatement validations (frozen counter, scratch clones, throwaway identity
`scratch <scratch@invalid>`, origin removed, `rev-parse --show-toplevel` checked before each commit):

```
G11 row @ 9d220d05b2887ca7ef77bc69ab892b9501638b94 -> ITEM G11 AGREE restated rc=0 … load=57.62, EXIT=0
G05 row @ d94df9ca5313457da695811b859802c900def1f9 -> ITEM G05 AGREE restated rc=0 … load=57.37, EXIT=0
```

## Findings

1. **G05 (SKILL.md:219) — MISMATCH, cause is the instrument, not the row.** The frozen argv at base
   prints all five frozen ANYLINE targets verbatim (`r15-landing b410186 15 1 5 True`,
   `r13-admitted a31642d 13 0 0 True`, `r14-landing cc21683 14 0 0 True`,
   `r16-landing 6ff91f5 16 0 0 True`, `r16-precarry 79bbe7a 16 1 29 True`, `RC=0`), i.e. the
   SKILL.md row's claim is accurate. The counter's `frozen_pred` builds
   `flat_lines = [collapse(x) for x in lines]` and matches `ANYLINE:` regexes against those
   collapsed strings, so a pattern containing `\t` can never match
   (`collapse('r15-landing\tb410186…') -> 'r15-landing b410186 …'`; the space-spelled conjunct
   matches, the frozen one returns `(False, 'predicate fails')`). Consequence: G05 cannot agree at
   any revision. Location: `census/round-34/c1-counter.py`, `frozen_pred` (ANYLINE and COUNT both
   read `flat_lines`).
2. **Same defect, second victim in the frozen set: G17b** (`COUNT:^SCENARIO\t…$==3`). Corroborating
   counter run at tip: `ITEM G17b MISMATCH original rc=1 expect_exit=0 predicate fails
   last=MATRIX scenarios=3 replayed=0 summaries_equal=True` — its run also exits 1, so the collapse
   defect is reachable there only after that is fixed; flagged for the owning seat and the L1.
3. **`where` pointers are one line short for 20 of the 23 SKILL.md items** (my five: G05 219→220,
   G07 222→223, G09 230→231, G11 234→235, G12 236→237; e.g. list-rev
   `SKILL.md:219 = | r16-landing-gate | …`, `SKILL.md:220 = | r17-gate-replays | …`). Harmless for
   agreeing items and for `same`-argv restatements (the cell is copied verbatim), but it breaks the
   argv-correction cause test, which reads `SKILL.md` at `where` and requires the cause to have
   written *that* line (finding 4). Location: `census/round-34/c1-items.tsv` column 2 vs
   `SKILL.md` at list-rev.
4. **G05's correction route is therefore not honestly available.** Executed search for exact-line
   writers of the frozen `where` line yields exactly one commit,
   `4f9a4e8388fc09e7a02a140bf397fe6329005b6f` (r16 honesty corrections; line absent at parent
   `a6ec7810…`, present at the cause), at which `census/round-17/gate-replays.py` is ABSENT — so
   "the row's own argv already failed there" is vacuous. A row binding that commit compiles and
   passes (validated above), but attributes the r17 row's correction to an r16 row's writer.
5. **G11 (SKILL.md:234) — genuine value drift, cause `4f30f23e26bff29dfc18807298300402bc148cae`**
   (round-20 close; parent `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`). Executed: parent
   `INVENTORY exact expected=36 observed=36` + `SUMMARY total=36 pass=36 fail=0`, cause
   `expected=45 observed=45` + `SUMMARY total=45 pass=45 fail=0`; the cause diffstats to
   `265 insertions(+), 11 deletions(-)` on `tests/fixtures/r20-input-binding.py` and touches the
   item's file. Later commit `98e5203d…`, base and tip all print 45. Row drafted and validated.
6. **No prior correction, supersession or binding row exists for any of the five cells** in
   `SCORECARD.md` at base (grep receipts per item in the delivery files; the only `read-root` hits,
   lines 440-441, are the r33 N06/N07 rows for `SCORECARD.md:159` over
   `census/round-21/oracle-acceptance.json`). No item is AGREE via Q76; the three AGREEs are
   original-predicate agreements.

## Attack log

**ATTACK-1 (frozen counter, `frozen_pred`): `ANYLINE:`/`COUNT:` regexes are matched against
whitespace-collapsed lines, so any predicate spelling a tab separator is unsatisfiable — a frozen
predicate that no repo state can ever satisfy.** Reproduced state: G05's frozen argv at base prints
the five pinned rows with real tabs (`repr` of the matching line: `'r15-landing\tb410186\t15\t1\t5\tTrue'`)
yet `frozen_pred` returns `(False, 'predicate fails')`; the same conjunct spelled with spaces matches
the collapsed line (`True`). Instrument is revision-independent: identical MISMATCH at base and at
tip `51acb5f`. Affected items: G05, G17b (2/60). Effect: frozen target `agree=60` is unreachable on
the bytes frozen at `2b0171e` unless a restatement row is used for each.

**ATTACK-2 (frozen item table + counter `judge`, argv-correction branch): the `where` off-by-one lets
a correction bind a cause that wrote a *different* row, so "the cause wrote the row's line" is
satisfiable by an unrelated commit.** Reproduced state: for G05 the frozen `where` `SKILL.md:219`
addresses the r16-landing-gate row; the sole exact-line writer is `4f9a4e83` (r16), where
`census/round-17/gate-replays.py` does not exist; a row naming it as cause passes the counter
(`ITEM G05 AGREE restated`, EXIT=0) while proving nothing about the r17-gate-replays row. Sweep:
20/23 SKILL items carry a `where` one line short.

Attack remediation is the L1's alone (no amendment is admissible now: data exists). Options laid out
in `deliver-c1-G05.md`: land the disclaimed row, or route G05/G17b as defects and accept the missed
target.

## Deliveries

- `.ufo/waves/round-34/w1/deliver-c1-G05.md` — MISMATCH + ATTACK-1/ATTACK-2 with reproduced state;
  mechanically valid row (validated, not recommended as honest).
- `.ufo/waves/round-34/w1/deliver-c1-G07.md` — AGREE at base and tip; no row.
- `.ufo/waves/round-34/w1/deliver-c1-G09.md` — AGREE at base and tip; no row.
- `.ufo/waves/round-34/w1/deliver-c1-G11.md` — MISMATCH, value-drift cause, validated `same`-argv row.
- `.ufo/waves/round-34/w1/deliver-c1-G12.md` — AGREE at base and tip; no row.

Checks the L1 should run after integration: the frozen counter over all 60 items at the C1 landing
commit and at the tip; `python3 tests/fixtures/r34-c1-junk.py` unchanged; re-read of the G05 ruling
before landing any restatement row for it. No tool install or upgrade was performed this seat; no
lane file outside `.ufo/waves/round-34/w1/` was written; scratch
`/fast/scratch/hyaku/souji-r34/RestateC1s2/` removed after receipts were copied.
