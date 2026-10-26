# SwarmCritic33 — attack on C1 (r32, wave 1)

## Status

STATUS: PASS — attack completed with reproduced states. Binding/withdrawing the 44 integers is **bookkeeping, not
calibration**: the v1 surface is fully gamed by a mechanical first-match search (target met, `unbound=0
mismatches=0 withdrawn=4`), and the v2 target is unreachable within its own frozen rules (6 items cannot bind under
any row shape, 11 more have no binding under the cell's own command, cap 8).

## Evidence

All scoring ran in a private clone at `/fast/scratch/hyaku/souji-r32/AttackC1/r.tfGalF/c` (origin removed;
`git -C … rev-parse --show-toplevel` printed that path), `TMPDIR=/fast/scratch/hyaku/souji-r32/AttackC1/tmp`, lane
base `85b61a151923986e7e6b48f7084b9122561b5f3d`, list-rev `3ec84fc81b3243429c834a051880b0bcde06291c`. The lane was
read-only for this seat. Every `rev=` below is a **scratch-clone** commit, not a lane commit.

1. Enumeration reproducibility.
   `python3 -B census/round-32/c1-enumerate.py --root . --rev 85b61a15…` → 45 lines; `diff` against
   `census/round-32/c1-items.tsv` at `3ec84fc8…` is empty (`ENUM-IDENTICAL`).

2. Mechanical binder on the **v1 surface** (any `census/round-K/` blob in the item's rounds, integer at digit
   boundaries plus a unit substring on one line, first match, no citation, no adjacency): 44 rows; state
   `rev=46445aa88287c38a3aac8cf8372ec8d77601b4ce`
   ```
   SUMMARY items=44 bound_run=0 bound_record=40 bound_field=0 withdrawn=4 unbound=0 mismatches=0
   ```
   → **v1 target met** (`withdrawn=4 <= 8`). The same bytes scored under v2:
   ```
   SUMMARY items=44 bound_run=0 bound_record=5 bound_field=0 withdrawn=4 unbound=0 mismatches=35
   ```

3. Mechanical binder on the **v2 surface** (citation + adjacency + multi-key field + run, cell argv only); state
   `rev=876d346798bec214721d61e90dcfec13701cd0a6`
   ```
   SUMMARY items=44 bound_run=1 bound_record=15 bound_field=3 withdrawn=8 unbound=14 mismatches=17
   ```
   The 14 unbound: N20 N21 N22 N23 N24 N28 N29 N30 N31 N33 N34 N38 N43 L29; plus `BAD-ROW(literal)` on N25 N26.

4. Counterexample states, one item each, scored with `--only`:
   - `A-genuine rev=d068644ee695eec8e666f83805efa3ba5634564a` — row id `N12`, line `SCORECARD.md:161`, literal
     `13 fail`, kind `record`, target `census/round-17/jj-receipts-base5fa6017.txt:51`.
     v1 `MATCH`; v2 `RECORD-MISMATCH`.
   - `B-unrelated rev=2185c8bd0c782c0c4d48918de80ae5465cd6223d` — same id/line/literal, kind `field`, target
     `census/round-17/c1-matrix.json arms.r14-harm.r17-hygiene.failed=13`.
     v1 `MATCH`; v2 `MATCH`.
   - `C-false-withdrawal rev=68a7f7753020c490ebef8c7050880ca0eec6cb81` — `N11`, kind `withdrawn`, reason
     `no observable in the cited census surface shows this count`. v1 `WITHDRAWN`; v2 `WITHDRAWN`.

5. Impossible-row states (`rev=217a7862d75028c989ac5c002216ce14b9a02bf4`): `N25` literal `13 k1`, `N26` literal
   `0 k1`, `N42` literal `495 r26` → `BAD-ROW(literal)` under both counters; `N19` (unitless) → v1
   `BAD-ROW(unitless-record)`, and with the cell's own command (`python3 -B tools/souji-coverage-agreement.py
   --root . --rev <full40>`) → `BAD-ROW(run-shape)`.

6. Unit discrimination (`units.py`, v1 surface over every eligible `census/round-K/` blob): mean 86.25 candidate
   lines per item; 22 of 44 items have ≥10; L29 2878 lines in 34 files, N08 (`3 tp`) 121/28, N16 (`12 base`) 93/21,
   N17 (`11 base`) 78/23.

7. Mask audit (`maskaudit.py`): every `N/M` and `cases=N pass=N` run hidden by mask M2 on lines ≤355 is covered by
   an r31 item (no uncovered occurrence), so the mask set itself loses nothing. Integers in the **description** cell
   are never enumerated: 64 (line 147), 160 (165), 18 (169, 170), 6 and 13 (175), 40 and 41 (422), 26 and 111 (424).

8. Run route, cell argv, base blob: `python3 -B tools/souji-capability-cells.py --root . --rev 24f343c8…
   --base 9f17a1ef… --list-rev 1d45496a…` in 37.0 s prints
   `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`.

9. Cited-surface probes (base blob, cell argv, scratch TMPDIR, cwd = clone): r19-seat-audit-shapes →
   `SUMMARY total=17 failed=0 base_discriminating=12`; r20-audit-contract → `SUMMARY total=66 pass=66 fail=0
   base_discriminating=0` (also with `--tool tools/souji-seat-audit.py`); r24-coverage-agreement `--tool …` →
   `cases=9 pass=9 control=FALSE-GREEN-REJECTED`; r29-registry-agreement → `cases=20 pass=20
   control=FALSE-GREEN-REJECTED` (also `--no-control` → `control=TOLERATED`); r31-landing-gate-precision →
   `cases=10 pass=10 control=FALSE-GREEN-REJECTED`; r28-wave-evidence-capture.sh → `cases=15 pass=15
   control=TAMPER-REJECTED`, and that fixture parses no CLI arguments.

## Findings

1. **v1 binds citations, not truth** — `census/round-32/c1-counter.py:15-44`. 40 record bindings from a first-match
   search over a mean of 86 candidate lines per item; 11 of 44 land in round amendment logs
   (`census/round-31/records/amendments.txt` 6, `census/round-29/records/amendments.txt` 5) and 18 of 44 in
   restatement carriers (amendment logs, the r31 item table, after-state records). Sharpest instance: N38 (`3 pass`)
   bound to `census/round-31/c1-cells.tsv:43`, where the only standalone `3` is the digit of the word `python3` —
   v1 returns MATCH because it asks only for the integer at digit boundaries plus the unit substring somewhere on
   the line.
2. **A0(a) has a universal-glob hole** — `c1-counter-v2.py:152` (`cited`). Line 161 contains `refs/jj/*`; the
   tokeniser yields the token `*`, and `fnmatch(basename, "*")` is true for every file, so N12's citation gate is
   void. Reproduced in Evidence 4 (`B-unrelated` MATCH on `arms.r14-harm.r17-hygiene.failed=13`, which is 13 failed
   cases of 26 in the r14-harm matrix arm, not the cell's 13 failed tools of 33). Scope: 1 of the 14 item lines.
3. **A0(b) rejects the cell's own record and accepts the wrong one** — `c1-counter-v2.py:161` (`adjacent`).
   `census/round-17/jj-receipts-base5fa6017.txt:51` states `SUMMARY total=33 failed=13 skipped=2`, the cell's 13
   tools, but `fail` is not within three non-alphanumeric bytes of 13 inside `failed=13`, so v2 returns
   RECORD-MISMATCH while the unrelated arm passes (Evidence 4). The stricter amendment is less accurate.
4. **`field` carries no adjacency and no quantity identity** — `c1-counter-v2.py:337-350`. Only a key-name substring
   (`:344`) and an integer value are checked, so a value under any container of a cited JSON binds (Evidence 4).
5. **Digit-bearing unit words are unwinnable** — `c1-counter.py:15` literal rule. N25/N26 (`k1`) and N42 (`r26`)
   must put the unit in the literal, which then adds an integer, so the integer count never matches:
   `BAD-ROW(literal)` on every row shape under both counters (Evidence 5). Three items can only be withdrawn.
6. **Single-digit literals collide with any rev-bearing argv** — `c1-counter-v2.py:311`. `lit in " ".join(argv)` is a
   plain substring test, so literal `0` is rejected by any argv holding `0`, i.e. by any full40 revision. N19 (`0`,
   unitless) has no cited JSON for `field` and is unwinnable by `run` with the cell's command (Evidence 5).
7. **The one calibration-relevant finding is inexpressible** — `census/round-13/verification.json:250` states
   `"rows": 37,` and `:257` `"mined": 20,`, while the cell (line 151) asserts `33 rows` and `mined=16` as "re-derived
   at r13". The cell's own cited record contradicts it. `record` cannot state the correction (`:323`
   `BAD-ROW(record-shape)` requires the literal's integers to equal the item's), the cell names no script (run
   impossible), and `corpus/SOURCES.md` is outside the record path rule. Legal verdicts: UNBOUND (target fails) or a
   false withdrawal.
8. **Counts of things are unrepresentable** — N11's 401 is the length of `prior_verdicts` in the cited
   `census/round-21/oracle-acceptance.json`, and `field` resolves only integer leaves, so a list length cannot bind;
   N43's 17 is the number of `RESULT` lines in the cited record; N22's 1381 lives in `census/round-26/waves`, which
   the record path rule excludes by component (`waves`), and the only cited script prints
   `cases=15 pass=15 control=TAMPER-REJECTED` last (Evidence 9).
9. **Withdrawal is unfalsifiable prose** — `c1-counter-v2.py:296` accepts any reason of ≥8 words. Evidence 4's false
   reason was accepted as WITHDRAWN while the cited file holds the 401-element list. The cap is a quota on honesty,
   not a check of it.
10. **Shared-occurrence makes line 422 unwinnable by record** — `c1-counter-v2.py:300`. Eight items (N27–N34) resolve
    only to two lines (`census/round-31/records/c1-after-a4.txt:43`, `census/round-31/records/c1-before.txt:43`), and
    no two items may share an occurrence, so at most 2 of 8 can bind by record; the rest must use `run` (Evidence 8).
11. **The enumeration is column-selected** — `c1-enumerate.py:57` reads only `cells[3]`; count integers in the
    description cell stay outside the 44 (Evidence 7). C1 therefore repeats the r31 "notation-selected" defect it was
    raised to fix, one level down.
12. **The honest floor exceeds the cap** — 6 items cannot bind under any row shape (N02, N03, N11: record, field and
    run all have zero candidates; N25, N26, N42: literal rule), and 11 more have no binding under the cell's own
    command (N15, N17, N18, N19, N20, N21, N22, N23, N24, N38, N43 — Evidence 5, 9). 17 > 8, so landing depends on
    choosing argv and revisions until the wanted digits appear — output shopping, not calibration.

## Attack log

- (1) Cheap mechanical binder: **lands** on v1 (target met, Evidence 2); v2 resists the first-match search but two
  holes are proven exploitable (Findings 2–4).
- (2) Unit words too common: **confirmed** — mean 86.25 candidate lines per item, 22/44 with ≥10 (Evidence 6). All
  discrimination comes from A0(a), not from the unit word; with a bare `*` present, A0(a) carries nothing either.
- (3) Withdrawal cap dishonest: **confirmed** — a false reason is accepted (Evidence 4C) and the cap sits below the
  proven floor (Finding 12). Withdrawing a stale count would be calibration; the cap turns that honest act into a
  scarce quota, pushing seats to bind instead of admit staleness.
- (4) Masks hide counts: **partly** — the mask set loses nothing in the evidence cell (Evidence 7), but the column
  scope hides count integers (Finding 11).
- Verdict on the assigned question: **bookkeeping**. v1 verifies that some eligible file restates the digits next to
  the word; v2 verifies that the cell's own pointer does so, which is closer to calibration, but it accepts a wrong
  number for the same item it rejects the right one for (Findings 2–3), cannot express the two corrections it would
  have to make (Finding 7), cannot read three counts at all (Findings 5, 6, 8), and its only honest exit is
  unfalsifiable prose (Finding 9). C1 should land as target-not-met; no amendment after data.
- Smallest safe corrections, for r33 (stricter-only, target-neutral): A1 reject a citation token that is a bare `*` or
  only glob metacharacters (`c1-counter-v2.py:152`); A2 require the `field` key's terminal segment to occur on the
  item's base line (`:344`); A3 compare integers after removing the unit substring from the literal, so `k1`/`r26`
  items are representable (`c1-counter.py:15`); A4 make the withdrawal reason a located claim (path plus line the
  counter can check for the integer's absence), so a false reason fails.

## Deliveries

- `.ufo/waves/round-32/w1/SwarmCritic33.md` (this report). No other lane file written. Scratch
  `/fast/scratch/hyaku/souji-r32/AttackC1` removed after this report was written; no lane revision, index or jj state
  touched.
