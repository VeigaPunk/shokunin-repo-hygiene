# SwarmCritic25 — souji r34 w2 seat report (AttackE32)

Seat assignment: adversarially falsify the W1 finding for AttackE32 (C1 item E32). Lane
`/home/vgpnk/Projects/shokunin/souji-shokunin`; base `9c76c7222a8abff027af42e37f0d160d52526bba`;
frozen list `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`. Full analysis with all byte-level
evidence and the executed replay: `AttackE32.md` (same directory).

## Status

W1's E32 verdict claim survives falsification; two of W1's three E32 sub-findings do not.
E32's mismatch is real, deterministic, and permanent under honest play; no honest
rule-conforming route exists. W1 finding 7 is falsified (misquoted evidence); the genuine
receipt anomaly W1 missed is identified (no verdict impact).

## Evidence

- Frozen row `census/round-34/c1-items.tsv:76` (byte-identical at list revisions
  `2b0171e2…` and `2b591924…`): exit `0`, predicate `SUMMARY items=27 pass=26 fail=1`,
  files `census/round-32/c2-counter.py`, argv pins `--base 85b61a15… --list-rev 3ec84fc…`.
- `SCORECARD.md:478` @ base: the r32 C2 row itself documents the landing `pass=26 fail=1` as
  not reproduced and "T12's base flips under load".
- `census/round-32/c2-counter.py:186`: `return 0 if failed == 0 else 1` ⇒ `fail=1 ⇒ rc=1`;
  `rc=0 ⇒ fail=0` ⇒ the frozen predicate fails. The frozen (exit=0, fail=1) pair is a
  logical contradiction at any revision, any load.
- Three byte-verified readings, all MISMATCH: committed
  `census/round-34/records/controls-c1-do-nothing.txt:60` (`predicate holds`,
  `pass=26 fail=1`, load 10.15 — consistent); W1 `deliver-c1-do-nothing-check.txt:65`
  (`predicate fails`, `pass=25 fail=2`, load 32.35 — consistent); W1
  `deliver-q76-honoring.txt:69` (`predicate holds`, `pass=25 fail=2`, load 36.63 —
  impossible label).
- Executed this seat (no clone, in-process import of the frozen counter):
  `frozen_pred("SUMMARY items=27 pass=26 fail=1", ["SUMMARY items=27 pass=25 fail=2"], …)`
  → `(False, 'predicate fails')`; against `pass=26 fail=1` → `(True, 'predicate holds')`.
  The q76 receipt's E32 label cannot be produced by the frozen counter from frozen inputs.
- Restatement gates `census/round-34/c1-counter.py:243-323`: same-argv BAD-CAUSE requires the
  frozen original to hold at the cause's parent (never true, per the contradiction above);
  argv-correction requires an honest corrected argv (none exists — the row's argv is not
  broken; sole eligible cause `9da5e9a5…` is mechanically valid but repairs nothing);
  Q76 clear (0 prior rows bind cell `SCORECARD.md:478`); restated statement must equal the
  collapsed last digit-bearing line, which flips with host load (T12 leg, unsandboxed base
  run of `tools/souji-census.sh --selftest`).
- C1 write scope (`census/round-34/preregistration.txt:62-67`) forbids `tools/` edits, so
  the T12 load flip cannot be honestly repaired.

## Findings

1. **W1 verdict (E32 MISMATCH) — reproduced, real, robust.** Not an artifact; deterministic
   via the frozen exit/statement contradiction, stronger than W1's value-drift framing.
2. **No honest route.** Same-value restatement categorically blocked by the value-drift gate;
   argv-correction blocked by the absence of any honest defect; load flip makes any single
   quoted statement unstable across regimes; scope forbids the tool repair that could
   stabilize it. E32 can never honestly AGREE ⇒ frozen `agree=60` unreachable via this item.
3. **W1 finding 7 falsified.** It quotes the committed record as `predicate fails
   last=SUMMARY items=27 pass=26 fail=1`; the record actually reads `predicate holds` on
   that line and is internally consistent. The real anomaly — SwarmCritic19's q76 receipt
   showing `predicate holds` against `pass=25 fail=2` — is impossible under the frozen
   counter (executed replay) and was missed by W1. No verdict impact (rc=1 dominates);
   report-fidelity defect only.
4. **W1 finding 6 confirmed but moot.** Load sensitivity is real and mechanistically
   explained; but load is auto-recorded under Q77 and no honest restatement exists, so the
   "record the load beside the restatement" advice never becomes operative.

## Attack log

Read-only inspection only: `git show`/`grep`/`sed` over frozen revisions and W1 receipts;
one in-process `importlib` replay of the frozen `c1-counter.py` `frozen_pred` (main() is
`__main__`-guarded, so no counter code executed); no fixture run, no clone, no scratch
created (0 MB used), no lane file modified, no commit/push. The 30+ min host-load-dependent
c2-counter run was not repeated: both load regimes are already bound by the committed record
and two W1 reruns, and the decisive gates were proven from frozen source plus the executed
predicate replay.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/AttackE32.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/SwarmCritic25.md`
