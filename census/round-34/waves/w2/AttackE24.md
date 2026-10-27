# AttackE24 — adversarial falsification of W1's E24 C1 finding

Seat SwarmCritic19, souji-r34 w2. Read-only; frozen artifacts untouched.

## Status

REPRODUCED — W1's E24 mismatch is real, deterministic, and independently re-executed by this
seat. The frozen statement `SUMMARY legs=9 fail=0` / exit 0 does not hold at the frozen base
`9c76c7222a8abff027af42e37f0d160d52526bba` (actual: `SUMMARY legs=9 fail=1`, rc 1). I tested
the benign-alternate explanations (measurement artifact, environment/load dependence, counter
binding defect, Q76 prior correction, wrong-item/argv freeze) and each is excluded by executed
evidence below. Under the frozen cause rules I confirm **no honest same-argv or argv-correction
route exists as of the frozen list revision** — the only row-writing cause for the cell has the
row's own argv *holding* at it. W1's "value drift" classification and "no prior correction"
claims both survive. Not a measurement artifact.

## Evidence

Frozen item (revisions per assignment; list file itself frozen at
`2b0171e2071fdc9c16a69bed12b0d040e574d8c8`):

- `census/round-34/c1-items.tsv:69` (at `2b0171e2…`): `E24  SCORECARD.md:305  0  SUMMARY legs=9
  fail=0  census/round-29/c3-integrity.py  {REV}  python3 -B census/round-29/c3-integrity.py
  --root . --rev {REV}`. Plain statement (no `ANYLINE:`/`COUNT:`/`RESULTS:` markers).
- Target cell `SCORECARD.md:305` (identical bytes at base and at list rev, verified:
  `git show 2b0171e2…:SCORECARD.md | awk 'NR==305'` == base line; the r29 C3 row claiming
  `integrity legs 9/9 (4 red at base)`, measured at `1dc678500c92164b0b2bea82b934dd03d1dfbf38`).
- W1 readings: `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:61` →
  `ITEM E24 MISMATCH original rc=1 expect_exit=0 predicate fails last=SUMMARY legs=9 fail=1
  rev=9c76c72…`; consolidated at `SwarmExecutor13.md:59` (mismatch table) and `:32,88`
  (id lists). Claimed class: value drift; no prior correction.

Executed probes this seat (read-only; instrument reads only committed blobs via `git cat-file`,
exports to its own `/var/tmp` temp dir which its `finally` removes; helper tools
`tools/souji-coverage-agreement.py` and `tools/souji-gate-check.py` are read-only in normal
operation — verified by source grep for write paths):

1. Base run (the frozen do-nothing probe):
   `python3 -B census/round-29/c3-integrity.py --root <lane> --rev 9c76c7222a8abff027af42e37f0d160d52526bba`
   → `L1 PASS f3_entries=2`; `L2 FAIL rows=153 coverage="grounded=18 mapped=18 dangling=0
   mismatches=0"`; `L3`–`L9 PASS`; `SUMMARY legs=9 fail=1 rev=9c76c72…`; `RC=1`.
   Byte-identical SUMMARY line to W1's committed reading.
2. Historical measurement rev:
   same command with `--rev 1dc678500c92164b0b2bea82b934dd03d1dfbf38`
   → `SUMMARY legs=9 fail=0 rev=1dc6785…`; `RC=0`. The recorded claim was true when measured.
3. Row-writing cause `de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b` (full sha resolved;
   `git rev-parse de874ee^1` = `1dc6785…`):
   same command with `--rev de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b`
   → `SUMMARY legs=9 fail=0`; `RC=0`. The row's own argv *holds* at the cause.
4. Root cause: `git show <rev>:corpus/SOURCES.md | grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`
   → 143 rows at `1dc6785…`, 153 rows at base. Set difference of S-numbers: new at base =
   `S220 S221 S222 S223 S224 S225 S226 S227 S228 S229` (S220/S221 introduced by `76c94eb`
   "round-30: C3 F1 keep-ref expiry entry…", per `git log -S "| S220" … -- corpus/SOURCES.md`).
   Instrument L2 hard-codes `len(rows)==143` and `grounded=15 mapped=15` (r29-era constants,
   `census/round-29/c3-integrity.py:57-58`), so registry growth alone flips L2 to FAIL.
5. Q76 sweep at base: `git show 9c76c72…:SCORECARD.md | grep -cE "SCORECARD\.md:305([^0-9]|$)"` → 0
   (rc 1); same pattern over `SKILL.md` at base → 0. No prior correction row for the cell.
6. Cause-branch audit (source, `census/round-34/c1-counter.py`):
   - statement binds to the run's LAST digit-bearing line (`:110`, `:144`, `:164`, `:312-313`);
     the run's last line is the SUMMARY line, so `fail=0` is tested against `fail=1` and fails;
     rc 1 ≠ exit 0 independently forces MISMATCH (verdict = exit_ok and ok, `:318`).
   - same-argv cause must touch `census/round-29/c3-integrity.py` with parent-holds/cause-fails
     (`:283-291`); argv-correction cause must have written the row's line and have the row's own
     argv already failing at it (`:292-300`).
7. File/cause history within list-rev ancestry
   (`git log --oneline 2b0171e2… -- census/round-29/c3-integrity.py`): only two commits —
   `1dc6785` (creates the file) and `de874ee` (round-29 end). `git log -S "integrity legs 9/9"
   2b0171e2… -- SCORECARD.md` → only `de874ee` introduced the row text; the exact line-305 text
   is absent from `1dc6785:SCORECARD.md` (grep -cF → 0) and line 305 is byte-identical at list
   rev and base. `git merge-base --is-ancestor` confirms `de874ee ≤ 2b0171e2` and `≤ 9c76c72`.

## Findings

1. **The mismatch is real and reproduced, not a measurement artifact.** Two independent
   executions (W1's do-nothing control and this seat's direct probe) produce the identical
   `SUMMARY legs=9 fail=1` line at base with rc 1. L2's inputs are committed blobs at the rev
   (registry row count and coverage counts), so the outcome is deterministic across hosts and
   load conditions — Q77-style load sensitivity is structurally impossible here.
2. **Root cause is post-r29 registry growth, exactly W1's "value drift" class.** The claim
   "integrity legs 9/9" was true at its measurement rev (executed: fail=0 at both `1dc6785` and
   the row writer `de874ee`). Between r29 and the r34 base, rows S220–S229 were appended to
   `corpus/SOURCES.md`; the r29 instrument hard-codes `rows==143 / grounded=15 mapped=15` in
   L2, so the legs 9/9 statement silently went stale. The SCORECARD row even discloses
   "measured at `1dc6785…`" — the frozen C1 statement binds that historical outcome to the r34
   base, which no longer satisfies it.
3. **No benign counter-explanation applies.** Not a git-wording drift (E09a class), not a
   missing/unresolvable pinned revision (G24/E14 class), not a notation/predicate-binding
   artifact (E14b/E25 class — replaying the frozen predicate against the recorded last line
   genuinely fails: the regex `SUMMARY legs=9 fail=0` does not match `…fail=1…`), and not the
   E32-style record inconsistency (the printed "predicate fails" is accurate here; rc mismatch
   alone forces the verdict anyway).
4. **Same-argv correction route: impossible as frozen.** Only `1dc6785` and `de874ee` touch the
   item file within the list-rev ancestry. At `1dc6785`'s parent the file does not exist (run
   cannot hold → `held` is not True); at `de874ee` the parent (`1dc6785`) holds True and the
   cause itself holds True (executed), so the required True→False transition never occurs.
   Judge branch `c1-counter.py:283-291` therefore rejects every candidate cause.
5. **Argv-correction route: blocked by the cause clause.** A historically faithful correction
   (pin `--rev 1dc6785…`, statement `SUMMARY legs=9 fail=0`) would *evaluate* correctly at base
   — the script reads blobs at the argv's rev — but the judge's argv-correction branch
   (`c1-counter.py:292-300`) requires the cause to have written the row's line AND the row's
   own argv to already fail at that cause. The unique row-writing cause is `de874ee`, and this
   seat executed the instrument there: it prints `SUMMARY legs=9 fail=0`, rc 0 — the row's own
   argv *held* at the cause → `BAD-CAUSE`. No later commit rewrites line 305 (append-only K2),
   so no alternative cause exists.
6. **Consequence for the lane's repair path (analysis, not execution):** E24 cannot be honestly
   restated from the current frozen state — neither correction kind has a valid cause. A future
   round could only create one by engineering a commit that simultaneously changes
   `census/round-29/c3-integrity.py` and flips the predicate (parent holds, cause fails);
   merely updating the instrument's stale r29 constants cannot serve, because at its parent the
   original predicate already fails. This narrows the lane's options more than W1 stated, but
   does not contradict W1: W1's scope was the mismatch and the absence of a *prior* correction,
   both of which are confirmed.
7. **Verdict:** W1's E24 finding survives adversarial falsification. The defect is genuine,
   source-attributable (S220–S229 registry growth vs. r29 hard-coded L2 constants), and
   unreachable under any other frozen clause. The impossibility of an honest restatement is
   executed evidence at the two candidate causes (probes 2 and 3), not merely source inference.

## Attack log

- Read the frozen list header and row (`c1-items.tsv:1-13,69`), the r29 C3 instrument
  (`census/round-29/c3-integrity.py` in full), the frozen counter's predicate/judge source
  (`c1-counter.py:110,142-169,239-323`), W1's do-nothing receipt, the consolidated mismatch
  table (`SwarmExecutor13.md`), and the Q76-honoring deliverable.
- Executed three bounded instrument probes (base, r29 measurement rev, row-writer cause) and
  five read-only git archaeology commands (row counts at two revs, S-number set difference,
  file history, `-S` pickaxe for the row text and S220, merge-base ancestry, line-305 identity
  across list rev/base, parent-absence grep). All output quoted above is actual output.
- Scratch: only small text captures under `/tmp` (scorecard/skill extracts, S-number lists);
  the instrument's own temp export under `/var/tmp` is created and removed by its `finally`.
  Nothing written to the lane or fleet root; no tools installed; no git/jj mutation; frozen
  items, predicates, and receipts untouched.
- Adversarial posture note: I attempted to falsify W1 via (a) environment/load artifact — refuted
  by determinism of blob-derived counts; (b) counter binding defect — refuted by source and by
  direct predicate replay; (c) Q76 prior correction — refuted by executed sweeps; (d) honest
  restatement routes the seat missed — both branches audited and blocked with executed probes;
  (e) W1 under-claiming — found one place where W1 was *conservative* (finding 6: the missing
  cause also blocks future restatement, which W1 did not state).

## Deliveries

- `.ufo/waves/round-34/w2/AttackE24.md` — this scoped adversarial review.
- `.ufo/waves/round-34/w2/SwarmCritic19.md` — seat report (same content, seat-scoped).
