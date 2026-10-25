STATUS: PASS

# CritC1Axis — does C1 move calibration, or tidy the paperwork?

Seat `L1Souji22.CritC1Axis`. Read-only against the lane: no git/jj write, no
signal, no install, no mutating cleanup. Base revision `4edb25d` (preregistration).
The lane moved during review (`d6a75ba` -> `af73b8b` -> `c9f1fe3`); every number
names its revision. Transcripts: `w1/evidence/CritC1Axis.md` (E1–E13). The
preregistration's counters and kill rules are untouched; the verdict below is this
item's vocabulary, not a prereg verdict.

## Verdict

**`bookkeeping-only`.**

C1's counter passes: with the instrument committed at `c9f1fe3`
(`sha256 65817d0d…`) the named tip `5fdd5d54` prints
`assertions=60 resolved=60 skipped=38 mismatches=0`, exit 0, and the base prints
`mismatches=3`. The claim is not void and the capability is real (its selftest is
8/8 and it covers a class the landing gate missed — E8). But the movement is
record accuracy, not calibration: **zero verdict-bearing cells changed**. All 24
capability "what it can now do" columns are byte-identical base→tip; the axis
scores are unchanged (8 / 7 / 8); seven *evidence-pointer* columns changed and one
capability row was added (the instrument itself). That is the shape this lane has
always recorded as `improved … numeric delta 0` (r13–r21), never as a calibration
score move. The lane reached the same place on the score — the row now says
"Score 7 unchanged" — but the axis-move reading is still wrong for the reasons
below, and two of C1's own numbers still do not re-derive.

## Tip movement during review (kept, not overwritten)

At `af73b8b` the row said "repaired to 0 mismatches over **the same 56
assertions**" and proposed **7→8**; the committed instrument measured 59 at that
same tip, so both statements were false as committed. At `c9f1fe3` the lane
replaced the sentence ("The assertion SET moved … this is a same-class
before/after, not a same-set victory"), conceded that one repair "names a fleet
file absolutely and therefore leaves class A", named four enum limits, re-derived
the counter cell, and held the score at 7. Those two defects are repaired; the
findings below are what remains.

## Counterexample (executed, current bytes)

1. **The row's set numbers do not re-derive.** Committed row: "**5 base tokens
   retired, 6 added**". Same declared bytes, same pair of revisions
   (`4edb25d` → `5fdd5d54`): with the instrument committed at `c9f1fe3`,
   retirement/addition is **6/11** (N 55 → 60); with the instrument committed at
   `a211e4d` (`58ddbfef`), **7/11** (N 56 → 60). Neither is 5/6. Superseded
   snapshots survive even though the counter cell was re-derived — Q10's "prose
   numbers equal table numbers" fails inside the row that exists to enforce that
   class.
2. **Before and after are measured with different instruments.** The row records
   base `assertions=56` (instrument `58ddbfef`) and tip `assertions=60`
   (instrument `65817d0d`); the committed instrument run over the *same* base
   bytes yields 55. No tool digest appears in SCORECARD (`grep` for
   `65817d0d`/`58ddbfef` → 0). With `--root .` the script that runs is the
   **worktree** copy while the declaration is read from `--rev`; during this
   review three different on-disk byte states produced `mismatches=1`, then 0, on
   bytes the committed tool scores 0 (E1). Unpinned, the before→after includes an
   instrument change it does not disclose.
3. **Two of three "repairs" left the enumerated set instead of resolving**
   (`skipped` 33 → 38 at the current tip). `AXES.md` → an absolute host path
   (uncountable: `PATH_RE` rejects it); the obsidian path de-backticked
   (invisible to the span scanner). Only `reason-after.txt` →
   `census/round-21/reason-after.txt` is an address repair. The AXES repair
   satisfies none of the preregistration's three permitted branches — no revision
   holds an absolute host path, the cell still presents it as the axes authority,
   no receipt is supplied — and the row now concedes it.
4. **Zero verdict-bearing cells changed** (the axis question, measured at
   `c9f1fe3`): 24/24 capability claim columns identical, 0 changed, 1 new row;
   axis score column 7 → 7; 7 evidence columns changed. The only content edit is
   the `## Planned` sentence recording that a claimed banked file is absent.
5. **The repair pass edited a cell that was not defective**: the
   `census/round-14/verification*.json` glob resolved at base ("3 match(es)") and
   was narrowed to `census/round-14/verification.json`, dropping two receipts from
   a capability's evidence with no mismatch to justify it.

## Strongest argument each way

**For axis-move.** AXES.md defines calibration's signal as "SHONEN.md/SCORECARD
entries match observed repo state". That signal moved: 3/56 declared assertions
did not resolve at base, 0 do at tip, with a frozen enum, a before receipt, and a
selftest that rejects the always-zero control and two counter mutants. One
mismatch was a false provenance claim ("banked in X"; X never existed) — catching
and withdrawing it is "gaps named honestly / overreach caught", the axis's own
words, not a spelling fix. The instrument is not redundant: at base the lane's
own landing gate returned 4 findings, **none in SCORECARD.md** (E8). And
kengaku's clause (d) was applied to a claim whose scorecard rubric demanded a
scored probe; souji has no such rubric row, so importing that ruling by mood
rather than by rubric would be unfair.

**For bookkeeping-only.** Calibration has been 7 since r5 (17 rounds). Both moves
it ever made rest on *verdict accuracy*: r3 (+1) on a blind-pair re-derivation of
the lane's own verdicts (0/21 disagreements); r5 (+1) on a verification round that
found three material per-verdict defects (false-SAFE class). Every instrument
acquisition since — r13 declared-evidence validator, r14 cache eligibility, r16
landing gate, r17 seat audit, r18 pointer gate, r19 carry gate, r20/r21 auditor
oracles — is recorded `improved, numeric delta 0`. The flight recorder states the
test explicitly: a rule-coverage count is "not calibration proof"
(`SCORECARD.md:31-33`). This claim changes no verdict, no confidence, no
capability text — it repairs addresses. The lane's own lesson agrees: M15's
`captured-by` is **Q10, "the bookkeeping matches the repo"**, and the rule was
already stated by **Q17** ("prose naming a fixture is not a substitute for the
file") since r13; the audit widens Q17's enforcement to one more file, it does not
add a criterion. Finally, 8 is the saturation line, so 7→8 would have declared
calibration saturated on pointer hygiene with no mapping from "M=0" to a number.

The precedent resolves the tie the same way: kengaku's critic called the
state/ledger repair "useful bookkeeping" that does not verify the registered
axis-move, and the later overrule credited C2 only after outside disagreements
became lessons and grounded criteria — a judgment change, not a state repair.

## What single observable settles it

**V = the number of verdict-bearing cells whose content changes as a direct
consequence of a mismatch repair**, where verdict-bearing means the axis `score`
column, the verdict/observation column, a capability "what it can now do" cell, or
an admission/boundary statement. Measured by joining each mismatch line of the
before `--format tsv` to its SCORECARD row/column and diffing base vs tip
restricted to those columns (the join used in E5 is a few lines of stdlib Python
and can be committed as a receipt).

- V = 0 → the audit corrected addresses; **bookkeeping**.
- V ≥ 1 → a verdict changed because of a finding; **axis-move** (the r3/r5 shape).

For C1: **V = 0** (executed, E5). Bounded caveat: if the operator rules that the
AXES.md *signal line* is itself the calibration rubric, then V is irrelevant and
the move is admissible at delta 0 or +1. That is a rubric ruling I cannot derive
from bytes; it is the one premise on which this verdict could be overruled, and
it should be stated as a ruling rather than left implicit.

Instrument-side counterpart, needed before V can ever be measured: **fixture 8 —
a declaration whose only evidence token is absolutised, de-backticked or
prefix-glued must still be a finding** (`mismatch:evaded`,
`control=FALSE-ESCAPE-REJECTED`), plus an itemised skip ledger. Today `skipped` is
a bare integer and the eight fixtures contain no escape control.

## What the claim must add (this round or the next)

Still open after `c9f1fe3`:
1. Make the row's set numbers re-derive: state the pair actually measured
   (6 retired / 11 added with the committed scanner; 7/11 with the prior one) and
   pin `sha256 65817d0d…` beside the counter. A before number without its
   instrument is not a receipt.
2. Leave the two escaped tokens countable: fixture 8 plus a fleet class
   (`--fleet-root`), so `../AXES.md` resolves as `fleet` rather than being a
   permanent mismatch and the absolute host path is not the cheapest green; or
   record both as exemption rows with reasons in
   `corpus/pointer-exemptions.tsv`, never as silent skips.
3. Correct M15's `captured-by` to Q17 (evidence fragment must resolve) and
   restore the narrowed `verification*.json` citation, or record why it shrank.
4. To become an axis-move (this round if a seat can still land it, otherwise r23):
   exhibit one finding that changes a **verdict** — a capability or axis row whose
   sole evidence pointer dangles and whose statement is therefore downgraded or
   withdrawn (the r5 shape), or a measurement number that fails re-derivation from
   its named commit and forces the row's confidence down (the r3 shape).
   `AuditReadme.tsv` already lists 9 same-class mismatches in `corpus/README.md`,
   unrepaired; if one of those index rows carries a capability claim, repairing it
   and showing the claim change is the cheapest available instance.

## Impacted axes

- **calibration (primary):** no move; score stays 7. As committed, C1 also carries
  two defects of its own class (non-re-deriving set numbers; an unpinned,
  version-dependent before number), so by AXES.md's "a trade anywhere is not an
  improvement" it cannot be admitted as an *improvement* until those are fixed.
- **coverage:** untouched by C1, bounded note only — the same defect class stays
  open in `corpus/README.md` (9 rows, peer-measured), and the "sha256" assertion
  kind contributes zero assertions on this file's layout (class C needs digest and
  path in one cell).
- **operability:** no harm; the tool is read-only, `/var/tmp`-scoped, selftest 8/8.
  The unpinned-instrument issue is a reproducibility qualification, not a
  regression.
- **depth / freshness / adjacency:** not owned; no claim made.
- **No axis harmed** holds only after corrections 1–2.

## Smallest safe correction

1. SCORECARD L14: replace "5 base tokens retired, 6 added" with the re-derived
   pair for the committed scanner (6/11), and pin `sha256 65817d0d…` in the
   counter cell; re-derive the counter at the landing tip.
2. Add fixture 8 (`FALSE-ESCAPE`) and emit `mismatch:evaded` for absolutised /
   de-backticked / prefix-glued tokens, with an itemised skip ledger; then re-run
   and record the obsidian and AXES tokens as findings (exemption row or resolving
   spelling).
3. Give the enum a `fleet` class so `../AXES.md` is a resolvable fleet citation.
4. Re-point M15's `captured-by` to Q17; restore or justify the narrowed glob.
5. Keep the score at 7 (`numeric delta 0`) unless (6) lands; if 7→8 is ever
   proposed again, attach the mapping from counter result to score that
   PROTOCOL.md requires ("a score no reader can re-derive is an opinion").

## Limits

- I did not re-execute the peers' predicate probes; I reproduced the counter runs,
  the token-set diffs, the skip deltas, the escape regex behaviour, the
  landing-gate run, the capability-column diff, the score history and the named-tip
  reproduction myself. `AuditReadme.tsv`'s 9 rows are source-read.
- Numbers are as of `c9f1fe3` (review window 06:53–07:10Z, 2026-10-25); the lane
  was moving throughout and the worktree instrument changed three times.
- The transient `mismatches=1` reading (E1) is attributed to a mid-write
  candidate, **not** reported as a defect of committed bytes.
- Scratch: `/var/tmp` extractions of committed tool bytes and token lists for
  byte-exact A/B work, all removed; no lane file written; no tool installed.

Report: .ufo/waves/round-22/attempt2/w1/CritC1Axis.md
