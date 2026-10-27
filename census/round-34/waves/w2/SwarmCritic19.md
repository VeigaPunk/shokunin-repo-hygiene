# SwarmCritic19 — r34 w2 seat report (AttackE24: C1 item E24)

Scoped adversarial falsification of W1's E24 finding. Full detail in `AttackE24.md`; this is the
seat-scoped summary. Read-only; frozen artifacts untouched.

## Status

REPRODUCED — W1's E24 mismatch is real and I independently re-executed it: at the frozen base
`9c76c72…` the frozen argv prints `SUMMARY legs=9 fail=1` (rc 1) instead of the frozen
statement `SUMMARY legs=9 fail=0` (exit 0). No benign alternate explanation survives executed
scrutiny, and under the frozen cause rules there is **no honest restatement route** as of the
frozen list revision. W1's classification (value drift, no prior correction) is confirmed; W1
was if anything conservative — the same cause analysis shows a future honest restatement is
also blocked (see Findings 6).

## Evidence

- Frozen row `census/round-34/c1-items.tsv:69` (list rev `2b0171e2…`): E24 =
  `SCORECARD.md:305`, exit 0, statement `SUMMARY legs=9 fail=0`, argv
  `python3 -B census/round-29/c3-integrity.py --root . --rev {REV}`. Target cell is the r29 C3
  row claiming `integrity legs 9/9 (4 red at base)`.
- W1 committed reading `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:61` and
  `SwarmExecutor13.md:59` — E24 MISMATCH, rc 1 vs 0, last line `SUMMARY legs=9 fail=1`.
- My probes (executed):
  1. `--rev 9c76c7222a8abff027af42e37f0d160d52526bba` → `L2 FAIL rows=153
     coverage="grounded=18 mapped=18 …"`, `SUMMARY legs=9 fail=1`, RC 1 — matches W1 exactly.
  2. `--rev 1dc678500c92164b0b2bea82b934dd03d1dfbf38` (the SCORECARD-recorded measurement rev)
     → `SUMMARY legs=9 fail=0`, RC 0 — the claim was true when recorded.
  3. `--rev de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b` (the unique row-writing cause; parent =
     `1dc6785…`) → `SUMMARY legs=9 fail=0`, RC 0 — the row's own argv holds at the cause.
  4. Registry rows in `corpus/SOURCES.md`: 143 at `1dc6785…` vs 153 at base; new = S220–S229
     (S220/S221 from `76c94eb`, round-30). Instrument L2 hard-codes `rows==143 /
     grounded=15 mapped=15` (`census/round-29/c3-integrity.py:57-58`).
  5. Q76 sweeps at base: zero hits for `SCORECARD.md:305` in SCORECARD.md and SKILL.md.
  6. Cause branches in `census/round-34/c1-counter.py:283-300`; statement binding to the last
     digit-bearing line `:110,144,164,312-313`. File history within list-rev ancestry touches
     `c3-integrity.py` only at `1dc6785` and `de874ee`; `-S "integrity legs 9/9"` names
     `de874ee` as sole introducer; line 305 is byte-identical at list rev and base and absent
     at the parent.

## Findings

1. Real, deterministic defect — not environment, load (L2 counts committed blobs), counter
   binding, or record-text artifact (predicate replay against the recorded line genuinely
   fails; rc mismatch alone forces MISMATCH).
2. Root cause: post-r29 registry growth S220–S229 vs the instrument's r29 hard-coded L2
   constants — precisely W1's "value drift" class.
3. Same-argv route impossible: no ancestor-of-list-rev commit touching the item file has the
   required parent-holds/cause-fails transition (`1dc6785`'s parent lacks the file; `de874ee`
   holds at both parent and cause — executed).
4. Argv-correction route blocked: the unique row-writing cause `de874ee` has the row's own
   argv holding (executed, probe 3), so `c1-counter.py:299-300` rejects it
   (`BAD-CAUSE(the row's own argv held at the cause)`). Even a historically faithful
   `--rev 1dc6785…` pin fails only on this clause.
5. Verdict: W1's E24 finding survives adversarial falsification; impossibility of an honest
   route is executed evidence, not inference.
6. Note beyond W1: because neither correction kind currently has a valid cause, the lane
   cannot honestly restate E24 without first engineering a commit that touches
   `census/round-29/c3-integrity.py` and flips the predicate in one step; merely refreshing the
   stale constants cannot serve as cause. This tightens W1's "reachable only by appended
   restatements" — for E24 even that is currently cause-blocked.

## Attack log

- Read frozen list header/row, the r29 instrument in full, the frozen counter's predicate and
  judge source, W1's do-nothing receipt, the consolidated mismatch table, and the Q76
  deliverable.
- Executed 3 bounded instrument probes (read-only over committed bytes; temp export confined
  to `/var/tmp` and removed by the script) and 6 read-only git archaeology commands; all
  quoted output is actual.
- Attempted falsifications (a)–(e) all refuted or absorbed; see AttackE24.md for the full
  log. No lane/fleet-root writes, no installs, no git/jj mutation; scratch confined to small
  text captures under `/tmp`.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE24.md` — full scoped adversarial review.
- `.ufo/waves/round-34/w2/SwarmCritic19.md` — this seat report.
