STATUS: PASS

# CritC1Axis — does C1 move calibration, or tidy the paperwork?

Seat `L1Souji22.CritC1Axis`. Read-only against the lane: no git/jj write, no
signal, no install, no mutating cleanup. Base revision `4edb25d` (preregistration).
The lane moved during review (`d6a75ba` -> `af73b8b`); every number below names
its revision. Full command/output transcripts: `w1/evidence/CritC1Axis.md` (E1–E13).
The preregistration's counters and kill rules are untouched by this review; the
verdict below is the review vocabulary my item defines, not a prereg verdict.

## Verdict

**`bookkeeping-only`.**

C1's counter passes: at the committed tip `af73b8b`, the committed instrument
(`sha256 58ddbfef…`) prints `assertions=59 resolved=59 skipped=36 mismatches=0`,
exit 0. The claim is not void and the capability is real. But the movement is
record accuracy, not calibration: **zero verdict-bearing cells changed**. Every
capability "what it can now do" column is byte-identical from base to tip; the
axis scores are unchanged (8 / 7 / 8); seven *evidence-pointer* columns changed
and one capability row was added (the instrument itself). Under this lane's own
history, that is the shape it has always recorded as `improved … numeric delta 0`
(r13–r21), never as a calibration score move. The one substantive catch — a
`## Planned` note claiming a banked artifact that never existed — is a Q10/Q17
record correction: it withdraws an *availability* claim, not any verdict.

## Counterexample (executed, committed bytes only)

1. **The row's own set-conservation sentence is false.** SCORECARD L14 at
   `af73b8b`: "repaired to 0 mismatches over **the same 56 assertions** at the
   final tip". The committed instrument at that same tip: `assertions=59`. The
   token multiset delta base→tip is 7 removed / 9 added (E3): `AXES.md`,
   `reason-after.txt`, the obsidian path, the r21 row's two revision tokens, the
   `census/round-14/verification*.json` glob and the short `31984f4` leave; the
   full `31984f47…`, `4edb25d…` ×3, `census/round-21/reason-after.txt`, the
   before-receipt ×2, the spot-check lesson, `d7266c5` and the literal
   `verification.json` enter. The counters at `2a130b4` also read 56 at both
   ends, but with five different tokens. "Same count" was mistaken for "same
   set" — inside the row whose subject is exactly that mistake.
2. **Two of three "repairs" left the enumerated set rather than resolving**
   (`skipped` 33 -> 36). `AXES.md` -> `/home/vgpnk/Projects/shokunin/AXES.md`
   fails `PATH_RE` and becomes an uncountable skip; the obsidian path was
   de-backticked and is invisible to the span scanner. Only
   `reason-after.txt` -> `census/round-21/reason-after.txt` is an address repair.
   The AXES repair satisfies **none** of the preregistration's three permitted
   branches: no revision holds an absolute host path, the cell still presents the
   path as the axes authority (evidence role not dropped), and no receipt was
   supplied.
3. **The schema rewards the least checkable spelling.** `../AXES.md` matches
   class A and can never resolve (`git show HEAD:../AXES.md` rc 128), so a
   *correct* fleet reference is a permanent mismatch while an absolute host path
   is skipped and green. The lane's own Q31 grammar already has a `fleet`
   classification; the frozen enum does not.
4. **Zero verdict-bearing cells changed** (the axis question, measured):
   22/22 capability claim columns byte-identical; axis score column 7 -> 7;
   7 evidence columns changed; 1 new capability row. The single content edit is
   the `## Planned` sentence that now says the banked file is absent.
5. Minor, same class: the repair pass also narrowed
   `census/round-14/verification*.json` (which **resolved**, 3 matches) to
   `census/round-14/verification.json`, dropping two receipts from a capability's
   evidence without a mismatch justifying it; and the committed cell recorded
   `assertions=56` while the committed instrument measured 59 at `af73b8b` (the
   worktree already carries 59, uncommitted).

## Strongest argument each way

**For axis-move.** AXES.md defines calibration's signal as "SHONEN.md/SCORECARD
entries match observed repo state". That signal literally moved: 3/56 declared
assertions did not match committed bytes at base and 0 do at tip, with a frozen
enum, a before receipt and a selftest that rejects the always-zero control and
two counter mutants. One mismatch was a false provenance claim ("banked in X",
X never existed) — withdrawing it is "gaps named honestly / overreach caught",
the axis's own wording. And the instrument is not redundant: at base the lane's
landing gate returned 4 findings, **none in SCORECARD.md**, because its grammar
covers only `census/ tests/ tools/ corpus/ .ufo/waves/` (E8). Kengaku's clause
(d) was applied to a claim whose own scorecard rubric demanded a scored probe;
souji has no such rubric row, so applying that precedent by mood rather than by
rubric would be unfair.

**For bookkeeping-only.** The lane's calibration score has been 7 since r5
(17 rounds). The two moves it ever made rest on *verdict accuracy*: r3 (+1) on a
blind-pair re-derivation of the lane's own verdicts (0/21 disagreements), r5 (+1)
on a verification round that found three material per-verdict defects
(false-SAFE class). Every instrument acquisition since — r13 declared-evidence
validator, r14 cache eligibility, r16 landing gate, r17 seat audit, r18 pointer
gate, r19 carry gate, r20/r21 auditor oracles — is recorded `improved, numeric
delta 0`. The flight recorder is explicit (`SCORECARD.md:31-33`): a rule-coverage
count is "not calibration proof". This claim changes no verdict, no confidence,
no capability text — it repairs addresses. The lane's own lesson agrees: M15's
`captured-by` is **Q10, "the bookkeeping matches the repo"**, not a calibration
criterion, and the class was already stated by **Q17** ("prose naming a fixture
is not a substitute for the file") since r13; the audit widens Q17's enforcement
to one more file, it does not add a criterion. Finally, 8 is the saturation line,
so 7→8 would declare calibration saturated on pointer hygiene, with no mapping
from "M=0" to a number.

The precedent settles the tie the same way: kengaku's critic called the
state/ledger repair "useful bookkeeping" that does not verify the registered
axis-move, and the later overrule credited C2 only after outside disagreements
became lessons and grounded criteria — a judgment change, not a state repair.

## What single observable settles it

**V = the number of verdict-bearing cells whose content changes as a direct
consequence of a mismatch repair**, where verdict-bearing means the axis `score`
column, the verdict/observation column, a capability "what it can now do" cell,
or an admission/boundary statement. Measured by joining each mismatch line of the
before `--format tsv` to its SCORECARD row/column and diffing base vs tip
restricted to those columns (the join I ran in E5 is three lines of Python; the
same map can be committed as a receipt).

- V = 0 -> the audit corrected addresses; **bookkeeping**.
- V >= 1 -> the lane's self-assessment verdict changed because of a finding;
  **axis-move** (the r3/r5 shape).

For C1: **V = 0** (executed, E5). Bounded caveat: if the operator rules that the
AXES.md *signal line* is itself the calibration rubric, then V is irrelevant and
the move is admissible at delta 0 or +1. That is a rubric ruling I cannot derive
from bytes; it is the one premise on which this verdict could be overruled, and
it should be stated as a ruling rather than left implicit.

Instrument-side counterpart, needed before V can ever be measured next round:
**fixture 8 — a declaration whose only evidence token is absolutised,
de-backticked or prefix-glued must still be found** (`mismatch:evaded`,
`control=FALSE-ESCAPE-REJECTED`). The current selftest has no such fixture, so
the three reclassifications used by the landed repair are unpunished by
construction.

## What the claim must add (this round or the next)

To keep C1 as landed, without a calibration score move:
1. Replace "the same 56 assertions" with the set delta — 56 -> 59, 7 retired /
   9 added, `skipped` 33 -> 36 — and re-derive at the **landing** tip (the
   committed cell already lags by 3 at `af73b8b`).
2. Pin the instrument in the counter line (`sha256 58ddbfef…`). With `--root .`
   the script that runs is the *worktree* copy while the declaration is read from
   `--rev`; the worktree digest changed twice during this review and one
   mid-write candidate returned `mismatches=1` on bytes the committed tool scores
   0 (E1). Unpinned, the claim is not reproducible.
3. Either make the two evasions countable (fixture 8; fleet class via
   `--fleet-root`, so `../AXES.md` resolves as `fleet` and the absolute path is
   not the cheapest green) or record them as exemption rows with reasons in
   `corpus/pointer-exemptions.tsv` — not as silent skips. Today the AXES repair
   is non-conforming to the prereg's own target text.
4. Correct M15's `captured-by` to Q17 (evidence fragment must resolve) and
   restore the narrowed `verification*.json` citation or record why it shrank.
5. Record `score 7, numeric delta 0` and withdraw the 7→8 proposal, unless (6).

To become an axis-move (this round if a seat can land it, otherwise r23):
6. Exhibit one finding that changes a **verdict**: a capability or axis row whose
   sole evidence pointer dangles and whose statement is therefore downgraded or
   withdrawn (the r5 shape), or a measurement number that fails re-derivation
   from its named commit and forces the row's confidence down (the r3 shape).
   `AuditReadme.tsv` already lists 9 same-class mismatches in `corpus/README.md`,
   unrepaired; if one of those index rows carries a capability claim, repairing
   it and showing the claim change is the cheapest available instance.

## Impacted axes

- **calibration (primary):** no move; the proposed 7→8 is unsupported. As landed,
  C1 also *adds* three small defects of its own class — a false set-conservation
  sentence, a stale counter cell at the committed tip, and a non-conforming
  repair — so by AXES.md's "a trade anywhere is not an improvement" it cannot be
  admitted as an improvement until those are fixed. Score stays 7.
- **coverage:** untouched by C1; bounded note only — the same defect class stays
  open in `corpus/README.md` (9 rows, peer-measured) and the "sha256" assertion
  kind contributes zero assertions on this file's layout (class C requires digest
  and path in one cell).
- **operability:** no harm; the tool is read-only, `/var/tmp`-scoped, and its
  selftest is 8/8. The unpinned-instrument clause is a reproducibility
  qualification, not a regression.
- **depth / freshness / adjacency:** not owned by this lane; no claim made.
- **No axis harmed** holds only after corrections 1–4; C1 as committed mildly
  harms calibration.

## Smallest safe correction

1. In SCORECARD L14: replace the "same 56 assertions" sentence with the measured
   set delta and the landing-tip counts; pin `sha256 58ddbfef…` beside the counter.
2. Add fixture 8 (`FALSE-ESCAPE`) and report `mismatch:evaded` for absolutised /
   de-backticked / prefix-glued tokens; re-run and record the obsidian and AXES
   tokens as findings with an exemption row or a resolving spelling.
3. Give the enum a `fleet` class (`--fleet-root`) so `../AXES.md` is a resolvable
   fleet citation rather than a permanent mismatch.
4. Re-point M15's `captured-by` to Q17; restore `verification*.json` or record
   the narrowing.
5. Withdraw 7→8 (`score 7`, delta 0) or attach the mapping from counter result to
   score that PROTOCOL.md requires ("a score no reader can re-derive is an
   opinion").

## Limits

- I did not re-execute the peers' 12 predicate probes; I reproduced the counter
  runs, the token-set diff, the skip delta, the escape regex behaviour, the
  landing-gate run, the capability-column diff, and the score history myself.
  `AuditReadme.tsv`'s 9 rows are source-read, not re-derived.
- Numbers are as of `af73b8b` (06:53–06:57Z, 2026-10-25); the lane is moving and
  the worktree instrument and SCORECARD were mid-edit.
- The transient `mismatches=1` reading (E1) is attributed to a mid-write
  candidate, **not** reported as a defect of committed bytes.
- Scratch: one `/var/tmp` extraction of the committed tool plus token lists for
  byte-exact A/B work, all removed; no lane file written; no tool installed.

Report: .ufo/waves/round-22/attempt2/w1/CritC1Axis.md
