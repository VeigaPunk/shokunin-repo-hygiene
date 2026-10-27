# AttackG23 — adversarial falsification of the W1 G23 finding (r34 w2, seat SwarmReviewer06)

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`; base `9c76c7222a8abff027af42e37f0d160d52526bba`;
frozen list / C2 re-pin `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; lane HEAD at review time
`51acb5fb6fa38a6b593b3badb674cec559d7eb2c`. Read-only seat: no lane file was edited except this
report and `SwarmReviewer06.md` in `.ufo/waves/round-34/w2/`. Scratch (cleaned to 648 KB after the
probes): `/fast/scratch/hyaku/souji-r34/AttackG23/SwarmReviewer06/`.

## Status

- **Upheld (reproduced):** W1's concrete finding for G23 is real. The frozen item mismatches at base
  (`rc=1`, `manifests=8 … uncovered=1` vs frozen `exit=0`, `manifests=7 … uncovered=0`), and W1's
  proposed restatement row (`.ufo/waves/round-34/w1/deliver-c1-G23.md:40`) is **valid under every
  frozen rule** (cause, argv, exit, statement, Q76). I reproduced the engine acceptance independently:
  `ITEM G23 AGREE restated` (probe commit `9d3fb8730e934a4a7fffd88a8d99e283190f09f4`).
- **Falsified (reproduced):** W1's sibling report `.ufo/waves/round-34/w1/deliver-c1-mismatch-classification.md`
  verdict on G23 — "same-value | no honest cause | **unreachable**" (:53), contributing to its headline
  "**0 of the 7 mismatches has an honest restatement the frozen counter would accept**" (:56) and
  "six SKILL items (…G23…) have no accepted restatement" (:148) — is **wrong for G23**. The
  argv-correction branch admits an honest, rule-conforming restatement whose cause is the *true author
  of the item's own registry row* (not a foreign neighbour, unlike G21). W1 is internally
  inconsistent; the G23 slice deliverable, not the classification report, is correct.
- **No route missed:** the accepted route is the *unique* rule-conforming route for G23 (proved below
  by uniqueness of the qualifying cause and by a negative control). No honest alternative
  (value-drift, Q76 prior binding, original-agree) exists.

## Evidence

Frozen item (`git show 2b0171e2071fdc9c16a69bed12b0d040e574d8c8:census/round-34/c1-items.tsv`, line 39, tabs):

```
G23	SKILL.md:247	0	SUMMARY manifests=7 failed=0 uncovered=0 floor_violations=0	census/round-29/c2-counter.py	{REV}	python3 -B census/round-29/c2-counter.py --root . --rev {REV}
```

Base do-nothing record for G23 — `census/round-34/records/controls-c1-do-nothing.txt:23` (untracked
wave record; run against attempt-1 freeze `2b591924f607940febbb99f922cc9bb090508eb6`, whose G23 row is
byte-identical — 1 match for `^G23\t`):

```
ITEM	G23	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba load=12.10
```

Committed summary `census/round-34/records/controls.txt:3` (landed at tip `51acb5f`, "round-34: record
frozen control outcomes"): `SUMMARY items=60 agree=35 mismatches=25 restated=0; rc=1`.

Rules applied (frozen bytes):
- `census/round-34/c1-counter.py:292-300` — argv-correction cause check: `line_text` is the **where-cell
  line** at `--list-rev`; cause must have it absent at parent and present at cause (:293-298), and the
  frozen (exit, predicate) must already **fail at the cause** (:299-300).
- `c1-counter.py:267-268` — corrected argv must name one of the item's files (basename match).
- `c1-counter.py:311-313` — restated statement must equal the run's collapsed LAST digit-bearing line.
- `census/round-34/preregistration.txt` (at 2b0171e) :48-57 — restatement cells, executed cause
  ("argv correction: the cause wrote the row and the row's argv already failed at the cause"), Q76
  ("a prior correction row already binding an item makes it AGREE"); :138-145 — amendment A1 (a)-(c).
- Q76 binding: no `### Round 34 registry restatements` section exists at base (do-nothing `restated=0`;
  grep of `git show 9c76c72:SCORECARD.md` finds no G23 row, no section). The only "correction" rows at
  base are `R29-CORRECTION` (`SCORECARD.md:295-297` at base), which bind the round-29 claim cell
  `SCORECARD.md:23`, not the G23 registry row — and `load_restatements` reads only the frozen section.

Facts established from history (all executed):
- SKILL.md is byte-identical at base and at the list revision (`git diff 9c76c72 2b0171e --stat` lists
  only `census/round-34/*` and `tests/fixtures/r34-*`). At base: `SKILL.md:245` `souji-pre-report-gate`,
  `:246` `souji-registry-agreement`, `:247` `souji-wave-evidence-capture v2 (committed-bytes)`,
  `:248` `r29-c2-counter` → the frozen `where` cell 247 is **one low** (W1 ATTACK A1 confirmed).
- `git log -S 'souji-wave-evidence-capture v2 (committed-bytes)' -- SKILL.md` → only
  `1dc678500c92164b0b2bea82b934dd03d1dfbf38`; `git log -S 'r29-c2-counter' -- SKILL.md` → only
  `1dc6785`. Blob check: at `1dc6785` the SKILL.md registry carries both rows (lines 227/228 there);
  at its parent `b86200714069022954a3b498cf697d894119b45e` **neither row exists**. So the accepted
  cause `1dc6785` wrote **both** the where-cell line and the item's own `r29-c2-counter` row — it is
  the true author of the row the argv/predicate describe, exactly what the preregistration's "the
  cause wrote the row" requires. Unlike G21 (foreign cause `6cb22dc`), nothing foreign is involved.
- Uniqueness of the cause: any qualifying cause must have line 247's text absent at parent and present
  at cause; the text has exactly one introducer (`1dc6785`) and is never removed/re-added (single `-S`
  hit), so no other commit qualifies.
- Value-drift branch impossible: item files = `census/round-29/c2-counter.py`; its entire history at
  base is the single commit `b8cb4b31ce80e2e3314b88e85d40ea9873180804`, and
  `git cat-file -e b8cb4b31^:census/round-29/c2-counter.py` fails ("exists on disk, but not in
  'b8cb4b31^'") → the original cannot hold at that parent. The true drift commits touch no item file:
  `git diff-tree --name-only -r d65a5c4328896742d2ec951f7156c6a70aa9325a -- SKILL.md census/round-29/c2-counter.py`
  is empty (92 files touched, none of the two), and `af7fd250c8a862130f88b8f77ad29debf343e54d` touches
  only `census/round-33/waves/w1-results.json`.
- Measurement is not an artifact: `census/round-33/waves/manifest.sha256` at base has 89 records and
  contains no `w1-results` line, while `git ls-tree -r --name-only 9c76c72 census/round-33/waves/`
  contains `census/round-33/waves/w1-results.json` (added at `af7fd25`) — matching the r29 counter's
  uncovered contract (`census/round-29/c2-counter.py:7-10`: committed paths under the waves dir with
  no manifest record). `uncovered=1` is genuine under the frozen instrument.

## Findings

1. **F1 — W1's proposed G23 restatement is valid and engine-accepted (REPRODUCED).** Probe commit
   `9d3fb8730e934a4a7fffd88a8d99e283190f09f4` (parent = lane tip `51acb5f…`, append-only SCORECARD.md,
   W1's row verbatim) → `ITEM G23 AGREE restated rc=1 expect_exit=1 statement is the run's last
   digit-bearing line …`, `SUMMARY items=1 agree=1 mismatches=0 restated=1`, rc=0. Every frozen
   sub-rule checked out: cause (author of the row, ancestor of the list revision, argv already failing
   there), argv (runs the row's own script `census/round-29/c2-counter.py`), exit (1 = measured rc),
   statement (collapsed last digit-bearing line), Q76 (no prior binding row).
2. **F2 — the route is unique; negative control (REPRODUCED).** Same row with cause
   `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (the commit that wrote the row's *script* but not its
   registry text) → `ITEM G23 MISMATCH restated BAD-CAUSE(cause did not write the row's line)`
   (probe `98d2129cd5e3f72a76aeeca6db04f08e563d1c1c`). Combined with the single-introducer history of
   line 247, `1dc6785` is the only cause the frozen counter can accept — no honest route was missed
   and none other exists (value-drift and Q76 alternatives are impossible, see Evidence).
3. **F3 — W1's executed readings reproduce exactly (REPRODUCED).** r29 counter at cause `1dc6785`:
   `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 …` rc=0 (so the frozen predicate
   manifests=7 already failed at the row's authoring commit); at `4d9bf02`: `manifests=7 … uncovered=0`
   rc=0 (the enumeration-time value was honest; `4d9bf02` is correctly not a cause); at base:
   `manifests=8 … uncovered=1` rc=1.
4. **F4 — no measurement artifact (REPRODUCED).** `manifests=8 / uncovered=1` follows from committed
   bytes (89-record manifest vs tree containing `w1-results.json`), not from a counter defect or
   environment condition. The residual is round 33's own unrecorded wave-1 capture, as W1 stated.
5. **F5 — W1 classification report falsified for G23 (REPRODUCED by F1/F2).**
   `deliver-c1-mismatch-classification.md:53` lists G23 as "same-value | no | unreachable" and
   :56-57/:148-149 conclude no honest restatement exists and that G23 helps make
   `SUMMARY items=60 agree=60 mismatches=0` unreachable. The report analyzed only the value-drift
   branch for G23 (its §2 row says "same-value") and never tested the argv-correction branch, even
   though its own §3.6 experiment shows that branch binds to the where-cell line. The counter-accepted
   G23 restatement above is honest (its cause authored the item's own row), so the "0 of 7" headline
   and the "≥6 items can never agree" count are wrong by at least one item (G23). Per-item verdicts
   for G05/G11/G17a/G17b/G21/G24 remain those seats' scope; this report does not reopen them.
6. **F6 — the off-by-one is harmless *for G23's cause binding* (INFERENCE, source-level).** Because
   `1dc6785` authored both the where-cell line (247) and the item's real row (248), the counter's
   where-cell-based cause check accepts the correct commit for the correct reason. The gameable
   foreign-cause accept demonstrated for G21 (classification §3.6) does not transfer to G23. This is
   consistent with the uncommitted SKILL.md lesson row in the lane worktree ("off-by-one `where`
   cells for 21/22 SKILL registry items…"): the defect is real at the list level, but it does not
   taint G23's restatement.

## Attack log

All probes executed in scratch; counter = frozen `census/round-34/c1-counter.py`
(sha256 `1ad8c86c…` == `2b0171e:census/round-34/c1-counter.py`, per W1's do-nothing record header;
no frozen artifact altered). Probes used plumbing-only commits (no worktree, throwaway identity
`w2probe <probe@w2.invalid>`), so no lane bytes changed.

1. Probe A (validate W1's row) — clone `--no-local --no-checkout` of the lane into scratch; append
   after `git show 51acb5f…:SCORECARD.md` exactly:

   ```
   ### Round 34 registry restatements

   | G23 | SKILL.md:247 | restated | 1 | `python3 -B census/round-29/c2-counter.py --root . --rev 9c76c7222a8abff027af42e37f0d160d52526bba` | `SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba` | 1dc678500c92164b0b2bea82b934dd03d1dfbf38 | w2 SwarmReviewer06 probe: unpinned argv stale at authoring; r33 added the 8th manifest (d65a5c4) with census/round-33/waves/w1-results.json unrecorded (af7fd25); the argv pins the round base revision so the reading is reproducible |
   ```

   commit-tree over a temp index at parent `51acb5f…` → `9d3fb8730e934a4a7fffd88a8d99e283190f09f4`;
   then

   ```
   flock $S/w.lock env TMPDIR=$S/tmp GIT_CONFIG_NOSYSTEM=1 python3 -B \
     /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
     --root $S/rep/p --rev 9d3fb8730e934a4a7fffd88a8d99e283190f09f4 \
     --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch $S/cnt --only G23
   ```

   Output (load-before `1.83 1.53 2.00`):

   ```
   ITEM	G23	AGREE	restated	rc=1 expect_exit=1 statement is the run's last digit-bearing line last=SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba load=1.83
   SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=9d3fb8730e934a4a7fffd88a8d99e283190f09f4
   rc=0
   ```

   The append-only and statement/exit/cause checks all passed inside the frozen counter (a violation
   would have printed COULD-NOT-EVALUATE or BAD-ROW/BAD-CAUSE instead of AGREE).
2. Probe B (negative control) — identical row, cause `b8cb4b31ce80e2e3314b88e85d40ea9873180804`
   (script author, wrote no SKILL.md line) → probe `98d2129cd5e3f72a76aeeca6db04f08e563d1c1c`:

   ```
   ITEM	G23	MISMATCH	restated	BAD-CAUSE(cause did not write the row's line)
   SUMMARY items=1 agree=0 mismatches=1 restated=1 partial=1 rev=98d2129cd5e3f72a76aeeca6db04f08e563d1c1c
   ```
3. Probe C (cause reading) — `git worktree add --detach` of `1dc6785` and of `4d9bf02` in the scratch
   clone; `TMPDIR=$S/tmp GIT_CONFIG_NOSYSTEM=1 PATH=/usr/bin:/bin python3 -B census/round-29/c2-counter.py --root . --rev <rev>`:

   ```
   == at cause 1dc6785:  SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=1dc678500c92164b0b2bea82b934dd03d1dfbf38   rc=0
   == at 4d9bf02:        SUMMARY manifests=7 failed=0 uncovered=0 floor_violations=0 rev=4d9bf0256f6f61a49ebfec55a524556090015f60   rc=0
   ```
4. History/blob checks (all `git log -S` / `git cat-file` / `git diff-tree` / `git show`, read-only):
   single introducers of both registry row texts; parent `b862007` lacks both rows; `b8cb4b31^` lacks
   the script; `d65a5c4`/`af7fd25` touch no item file; manifest (89 records, no `w1-results`) vs tree
   (contains `census/round-33/waves/w1-results.json`); base vs list-rev SKILL.md byte-identical;
   attempt-1 freeze `2b59192` carries the same G23 item row.

Attack attempts that **failed to falsify** W1 (i.e., attacks on the finding, all repelled by the
frozen bytes): Q76 prior-binding hunt (none), value-drift cause hunt (impossible), alternate causes
(script author rejected, Probe B), statement/exit cheating (not needed — the honest row passes),
measurement-artifact hypothesis (refuted by manifest-vs-tree bytes).

## Deliveries

- `.ufo/waves/round-34/w2/AttackG23.md` — this report.
- `.ufo/waves/round-34/w2/SwarmReviewer06.md` — seat-scoped findings (same verdicts).

Residual risk / verification gaps: I ran `--only G23`, not the full 60-item counter; overall C1-target
reachability is other seats' scope — this report corrects only G23's contribution to it. The lane
worktree is dirty (`M SKILL.md` with uncommitted r34 rows; `records/*` untracked); all probes read
committed bytes, so this had no effect. Counter-level holes not re-tested here (e.g. the wildcard
`*`-exit survivor from W1 `deliver-c1-attacks.txt` — the G23 row deliberately uses the concrete exit 1).
No tool installs were performed. Scratch left at 648 KB (clones/worktrees removed).
