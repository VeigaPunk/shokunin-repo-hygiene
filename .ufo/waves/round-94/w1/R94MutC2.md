# R94MutC2 — C2 mutation probe (souji round 94)

Mutation-test of the r94 forgery probe's setup checks and the arms counter.
Probe mutants scored with the pristine r94 arms counter via the C2 predicate
command (probe substituted); counter mutants scored via the same arms driver
on both the r94 and the r93 probe. Baseline (pristine probe + pristine
counter): `ARMS-SUMMARY arms=10 conform=10`, exit 0 (receipt-baseline-r94.txt).

## Method
11 one-edit probe mutants (each setup check removed or rc 2→1; both
`res is None` checks; `exist_ok` True→False) + 5 one-edit counter mutants
(S2/S4/P2 want codes, `and`→`or` conform, stream choice). Receipts:
`.ufo/waves/round-94/w1/R94MutC2/receipt-<mutant>.txt` (11 probe + 10 counter
runs + baseline). Scratch work dirs under `/fast/scratch/hyaku/souji-r94/R94MutC2/`,
deleted before yield. No frozen file modified.

## Probe mutants (pristine counter, r94 probe)

| mutant | edit | arms conform | vs predicate (want 10) | verdict |
|---|---|---|---|---|
| M01-remove-nonempty | delete non-empty --work check | 9, S2 exit 0 | <10 | killed |
| M02-remove-filecheck | delete not-a-dir --work check | 9, S3 exit 1 no FATAL line | <10 | killed |
| M03-filecheck-rc1 | not-a-dir rc 2→1 | 9, S3 exit 1 | <10 | killed |
| M04-readable-rc1 | readable-file rc 2→1 | 7, S4=S5=S6 exit 1 | <10 | killed |
| **M05-remove-posNone** | **delete positive-control `res is None` check** | **10 (rc 0)** | 10 | **SURVIVED** |
| M06-posNone-rc1 | positive `res is None` rc 2→1 | 9, S7 exit 1 | <10 | killed |
| M07-remove-forgNone | forgery `res is None` → `rejected=no`, continue | 9, S8 exit 1 no line | <10 | killed |
| M08-forgNone-rc1 | forgery `res is None` rc 2→1 | 9, S8 exit 1 | <10 | killed |
| M09-no-exist-ok | `exist_ok` True→False | 9, S1 exit 1 (FileExistsError) | <10 | killed |
| **M10-editonce-rc1** | **edit-applies-once rc 2→1** | **10 (rc 0)** | 10 | **SURVIVED** |
| **M11-remove-tmp** | **delete /tmp /var/tmp /dev/shm --work check** | **10 (rc 0)** | 10 | **SURVIVED** |

8/11 killed. Survivors (findings; classes distinct):

- **M05 — masked by downstream check (defense-in-depth, NOT a coverage hole).**
  With the positive-control `res is None` check removed, S7 (mute fixture, no
  SUMMARY ever) still ends rc 2: the probe prints `POSITIVE … fail`, runs F1
  against the same mute fixture, and the *forgery-loop* `res is None` check
  fires `C2-FORGERY-FATAL: … forgery F1 …` rc 2. The positive check is
  redundant for every in-counter arm; classifying it as a finding that the
  predicate does not pin the positive-path discipline (only the loop-path
  one), not as a claim falsification — the claim only promises the 10 arms.
  Direct repro in report (mute fixture, mutant probe): prints
  `POSITIVE tool exit=1 tool_pass=-/- fail` then F1 FATAL, `rc=2`.
- **M10 — arm-coverage hole (edit-once path untested).** No arm exercises a
  tool/before whose forgery `old` string occurs ≠ 1×. Direct repro (mutant
  probe, tool `x = 1\n`): `C2-FORGERY-FATAL: F3 edit does not apply exactly
  once` with `rc=1` vs pristine `rc=2`. Falsifiable only by a hand-written
  arm. Does not falsify the C2 number (10/10 stands); it shows the 10-arm
  coverage does not bind this setup check.
- **M11 — arm-coverage hole + defense-in-depth redundancy.** No arm passes a
  valid-file set with --work under /tmp. Direct repro (mutant probe, valid
  files, --work /tmp/R94MutC2-tmp-probe): probe proceeds (no /tmp FATAL) and
  the positive control's fixture run prints no SUMMARY under /tmp, so it
  still exits rc 2 — via the positive FATAL, not the /tmp FATAL. The /tmp
  check changes which FATAL line fires, not the exit code; the predicate
  cannot catch its removal. (The pristine probe's /tmp check is thus
  belt-and-suspenders w.r.t. exit codes; its value is the distinct FATAL
  line/diagnosis.)

## Arms-counter mutants

| mutant | edit | on r94 probe | on r93 probe | verdict |
|---|---|---|---|---|
| C01-S2-want0 | S2 want 2→0 | 9 (S2 exit 2 vs 0) | 2 | killed; r93 stays <10 (not a broken counter) |
| C02-S4-want1 | S4 want 2→1 | 9 (S4 exit 2 vs 1) | 3 | killed; r93 stays <10 |
| **C03-conform-or** | **`ok = rc == want and has` → `or`** | **10 (rc 0)** | **3** | **SURVIVED on r94; no false-pass on r93** |
| C04-P2-want0 | P2 want 1→0 | 9 (P2 exit 1 vs 0) | 2 | killed; r93 stays <10 |
| C05-stream-swap | FATAL/stdout stream choice swapped | 0 | 0 | killed both |

4/5 killed; **C03 survived on r94**. Why: under `or`, on the r94 probe every
arm happens to satisfy both conjuncts anyway (conform=10), so the mutant is
observationally identical on r94 outputs. On r93 it does NOT manufacture a
false 10/10 (still 3: P1, P2, S2 pass `rc==want or has` — S2 exit 2 + has
FATAL → conform under `or`; r93's 7 failing arms exit 1 without the FATAL
line, with `rc != want`, so still non-conform). Counter weakness: the
conform test does not verify the AND of exit-code and output-line; a probe
that hits right codes without the required line (or vice versa) would pass
mutated counter. Not an r93 false-pass, but a real gap: it weakens exactly
the `C2-FORGERY-FATAL:`-line half of the predicate.

## FALSIFIES assessment

**NO-FALSIFICATION** of either claim's stated wording/numbers: pristine run
reproduced `ARMS-SUMMARY arms=10 conform=10` exit 0; no survivor changes any
stated sentence — all three probe survivors and C03 are coverage/masking
findings inside the prereg's declared limits (ten arms, L1-chosen; stated
limit (i) explicitly invites other setup failures). M10/M11/C03 are recorded
here as findings for the L1's amendment ledger, not as wording falsifications.

## Findings summary for L1
1. Arm-coverage holes: edit-once exit (M10) and /tmp --work exit (M11) are
   untestable by the 10 arms — propose arms S9 (bad-tool edit-miss) and S10
   (valid files, /tmp --work) if the claim's wording ever wants them.
2. Positive `res is None` check is redundant under the counter (M05);
   removing it still yields discipline via the forgery-loop check.
3. Counter conform test (`and` vs `or`) is not itself pinned by the C2
   predicate (C03); the `C2-FORGERY-FATAL:` line requirement rides on the
   un-mutated counter's `and`.
