# R94Critic — falsification walk on the frozen r94 claims (C1 calibration 7, C2 operability 8)

Contract read first: `census/round-94/preregistration.txt` (F). Lane base `eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536`;
instruments P1 `24cd67b0eff2cf3ec98cbfe74e3f4ef3fdaab88a`; controls P2 `39d4163a66c350f219287530a5aed6ac9d5e7224`.
This seat wrote only its own seat dir + this report, ran everything under
`/fast/scratch/hyaku/souji-r94/R94Critic/` (deleted before yield; text receipts copied into `receipts/`).
No git/jj mutation anywhere; frozen `census/`, `tests/`, `tools/`, `corpus/` untouched; no tool installs
(`python3 -B` only, per the round tooling note). Live re-runs of both predicates reproduce the frozen numbers
exactly (receipts in `receipts/`), so nothing below disputes the *numbers*. The dispute is about what the
numbers prove.

## Exponents of erosion, named before I start

- **C1:** the counted quantity moves 2 → 0 "crash fixtures scored killed" while the two semantic kills and the
  survivor stay put. Candidate attacks: (a) a no-sentinel rule that also reaches `errored=2` on the five
  fixtures; (b) a fixture-fitted probe that reaches C2's 10/10 without discipline; (c) setup failures outside
  C2's ten arms where the r94 probe still exits 1; (d) universal words in the prereg the counters do not
  enumerate; (e) whether each claim stands without the other.
- **C2:** a "setup failure reads as a surviving forgery" defect is supposed to be fixed by moving setup errors
  onto exit 2. Candidate attacks mirror (b)/(c)/(d).

## C1 — axis calibration 7

**Fit: yes.** The axis is "the lane's self-assessment vs observed state". The r93 search's `verdict()` said
`killed=yes` for a mutant whose counter had in fact raised an uncaught exception and printed nothing further
toward a verdict — self-assessment ("a row caught this mutant") diverged from observed state ("it crashed").
The r94 rule measures exactly that divergence and re-labels it `errored`. Stryker's Runtime-error state (S357)
makes the same distinction, so the axis is honestly used. One caveat, disclosed in the prereg's stated limit
(i), worth keeping on the record: both crash targets are *hand-written* fixtures to the frozen counter, not
generated mutants, so the calibration improvement is demonstrated on simulated crashes. Fair as a probe of the
kill rule (they exercise the same pathway: `sys.excepthook` → `rc=70`), but the "before 2, after 0" numbers
are about fixtures, not about any generated-mutant population. The claim never asserts otherwise.

**Cheap alternative kill rules (seat assignment item 1).** I re-ran the r93-rule control myself
(`receipts/c1-control-rereceipt.txt`; identical output to the frozen `controls/c1-control-r93-rule.txt`: the two
crash fixtures `killed=yes`, `errored=0 killed=4 survived=1`) and kept the five `harness.out` files
(`receipts/harness-out-control/`). On those no-sentinel outputs I evaluated candidate verdicts offline
(`receipts/offline-rule-eval.py` + `.out`):

| rule (no sentinel) | errored | killed | survived | meets predicate |
|---|---|---|---|---|
| `match=error` row present (the principled "errors aren't kills" rule) | 0 | 4 | 1 | no |
| row count thresholds (`match=no` ≥ 2 / ≥ 10) | 1 / 0 | 3 / 4 | 1 | no |
| `got=-` row present | 1 | 3 | 1 | no |
| all 66 rows `rc=1` | 1 | 3 | 1 | no |
| **composite: `got=-` present OR all rows `rc=1`** | **2** | **2** | **1** | **yes** |

The composite rule is cheap (one pass over the 66 ROW lines), uses no `sitecustomize`, no sentinel, no new
exit codes, and meets the C1 predicate *exactly* on the five fixtures. It is also **not principled**: it is a
two-legged conjunct fitted to these two fixtures. `h-crash-late` is the only mutant whose every one of 66 rows
reads `rc=1` (a genuine multi-clause mutant could do the same), and `h-crash-index` is the only one with a
`got=-` row (a counter that verdicts on every row but crashes at the end would score neither leg). Flip it
around: a real mutant that mismatches two rows the way `h-crash-late` does would be scored `errored` — an
illusion of calibration with no crash behind it. Stryker's "a test failed" vs "the run resulted in an error"
distinction needs the *counter's* fate, which the harness's ROW lines do not carry in no-sentinel form (the
counter's stderr is piped away and surfaced only as 200 chars of `detail=` on `match=error` rows; my control
outputs contain zero `match=error`, zero `Traceback`, zero `FATAL` — verified by grep).

**What this does and does not do to the claim.** The filed forgery pair (FA blanket refusal, FB no-sentinel)
does not include the composite rule, and FB is precisely "the r93 rule scored through r94 code". So the
predicate `errored=2 killed=2 survived=1` does **not** by itself prove the crash sentinel is what did the
work; a fitted harness-output pattern reaches the same numbers. The claim's *causal* wording ("a crash
sentinel … and the r94 rule … scores both crash fixtures errored") is still true of the filed instrument —
I re-ran the predicate and got `errored=2 killed=2 survived=1` with `# crash-sentinel rc=70 check=pass`
(`receipts/c1-after-receipt.txt`), and the mechanism is real (in the `after` outputs the crash fixtures'
ROW lines read `rc=70` exactly where the sentinel is supposed to put them). The gap is a *weakness of the
predicate as evidence*, not a falsehood in the claim: the number is necessary, and this wave's own artifact
shows it is not sufficient to prove the mechanism. The prereg's stated limit (i) ("the claim is about these
five verdicts") already bounds the claim to exactly the ground this rule exploits, so I record this as a
predicate-strength caveat rather than a wording falsification. Smallest safe correction the L1 could adopt:
add a third forgery — "FC: no sentinel + composite pattern rule (`got=-` or all-`rc=1` → `errored`)" — to
`c1-forgery-controls.py`; it would score `errored=2 killed=2 survived=1` like the filed rule and so would need
to be *refused by a stronger measurement* (e.g. a third hand fixture that crashes with `match=no` only on
expect-`rc=1` rows, which the composite would spare). Until such a fixture exists, "the number proves the
sentinel" over-reaches; the honest sentence is "the sentinel + rule achieves it, and the filed FA/FB variants
do not".

## C2 — axis operability 8

**Fit: yes.** A probe that exits 1 both when a forgery survives and when its setup is broken makes the exit
code unusable as a workable signal — the operator cannot tell "reject this forgery" from "fix my harness".
Moving setup failures onto exit 2 with a `C2-FORGERY-FATAL:` line is operability, plain as bottled. The
number (10 conforming arms) is honestly a *count of a surface the L1 chose*, and the prereg says so in limit
(i). The question is whether the count can be reached without the discipline the surface is meant to measure.
It can (see first): the result is that the counter measures *arm-fitness* as much as *discipline*, and the
r94 probe's real discipline is demonstrated by the code, not by the 10.

**Cheapest probe edit reaching 10/10 without setup discipline (seat assignment item 2).** I copied the frozen
probe into scratch and added a ~15-line special case at `main()` entry keyed on
`os.path.basename(abspath(--work))`: arm names `P1`/`S1` print the pass summary and exit 0, `P2` prints the
fail summary and exit 1, anything starting with `S` prints `C2-FORGERY-FATAL:` and exits 2. The unedited probe
body is untouched and never runs under the arms counter. Under the frozen arms counter this probe scores
`ARMS-SUMMARY arms=10 conform=10`, exit 0 (`receipts/probe-cheap.py`, `receipts/c2-cheap-armname-receipt.txt`,
sha256 `19e3bfa27747769333cc80c7e7b51f2b11846cbbcfa52ab39f0393bb5c3af935`). It runs **no forgery, opens no
fixture, writes no file** on any arm. So "10 conforming arms" is satisfiable by arm-name fitting alone, and
the cheap edit is in fact *total voter fraud*: unlike the real probe it would survive any input shaped like
an arm but is useless off the surface (off-arm it falls through to the real body and inherits its binary-tool
failure below). This does not make the frozen probe undisciplined — I read its `main()` and it really does
check `--work` emptiness, file readability and the SUMMARY line before running anything, under the same arms —
but it means the C2 predicate, taken alone, certifies the *arms counter + the surface*, not the discipline.
The prereg's limit (i) already says the ten arms are "chosen by the L1", so the credit for the discipline
belongs to the code + GA/GB forgeries (each one-edit probe was refused by exactly the arm it targeted),
with the count as a smoke test. Recorded as a methodology caveat, not a wording falsification; the smallest
safe correction that does not widen any claim: none needed for the claim, but a *future* counter should
randomize arm directory names. Note my cheap special-case probe does fit the one named extra in limit (i)
that I could not test directly: it does not emulate unreadable files, hangs or disk-full either, so it is
not even that kind of cheat — it is a plain constant-fold of the arm set.

**Counterexamples the prereg's limit (i) names (seat assignment: "other setup failures … are the wave's to
try").** Probing the frozen r94 probe directly, each with its own `--work` under scratch:

1. **A readable-but-present binary (non-UTF-8) `--tool` file → exit 1 with a `UnicodeDecodeError` traceback,
   no `C2-FORGERY-FATAL:` line** (`receipts/c1.err`). The probe checks `os.path.isfile` + `os.R_OK` and then
   `open(..., encoding="utf-8").read()` raises. This is the exact failure class the claim says is fixed — "a
   setup failure is indistinguishable from a surviving forgery" — via a readable, present file that the
   readability gate waves through. Uncaught exceptions in the probe are uniformly exit 1 in Python
   (interpreter default), so *every* unhandled setup exception reads as a surviving forgery; the r94 probe
   handles the eight enumerated arms and lets everything else escape as exit 1.
2. Unreadable-but-present `--fixture` (`chmod 000`) → exit 2 `C2-FORGERY-FATAL: --fixture … is not a readable
   regular file` (`receipts/c2.err`). Conforming; covered by the `os.access(R_OK)` gate.
3. `--work` a symlink to an empty dir → the `isdir`/`listdir` gates follow the symlink and the probe runs
   normally (positive control + forgeries, verdict lines printed). It did not refuse; it also did not corrupt
   anything. Arguably conforming in *effect* (an empty dir reached), but it is not "an existing empty
   directory" in the spelling the probe claims. Worth one line in limit (i).
4. A fixture whose SUMMARY line reorders the fields (`SUMMARY tool_pass=1 cases=1 before_pass=0`) → exit 2
   `C2-FORGERY-FATAL: the fixture printed no SUMMARY line for the positive control (exit 0)`
   (`receipts/c4.err`). Conforming as designed — the strict regex answers "no SUMMARY line" — though the
   fixture printed one; the failure message mis-describes a malformed-but-present line. Cosmetic.

Item 1 is a genuine residual defect in the claimed class, but is it a *falsification of the stated wording*?
The claim's countable sentence is "refuses every other **setup arm** with exit 2" — `setup arm` is defined by
the ten-arm enumeration in the same paragraph (P1, P2, S1–S8), and "every other" = the eight setup arms.
The binary-tool input is not one of those arms, and limit (i) lists its family ("unreadable-but-present
files") among the things "the wave's to try", which is the wave telling us what is *not* claimed. So: the
defect is real, the wording is not falsified, and the amendment-worthy sentence is the probe's docstring, which
is broader than the claim: "Every setup failure exits 2 with one `C2-FORGERY-FATAL:` line" (c2-forgery-probe.py
line 5). That sentence is, strictly, false in the wave's own evidence — counterexample 1. It is inside the
frozen instrument, which this wave must not edit; the L1 should note the docstring overclaims by one universal
("every") and that the smallest safe correction is to narrow that sentence (or catch the decode). Since the
prereg's own sentence is the narrower "every other setup arm", the claim itself stands. Verdict on the
underlying probe: residual defect, routed onward (a one-line `try/except (OSError, UnicodeDecodeError)` →
FATAL/2 around the `open(...).read()` calls, or narrowing the docstring). Recorded below as the one
FALSIFIES-WORDING I can defend — against a docstring sentence inside the frozen instrument, not against the
prereg's counted sentence.

## Separability (seat assignment item 3)

Independent, both directions, by file census: the C1 predicate command names only C1/controls files
(`c1-survivor-search.py`, `c1-targets.json`, the r93 harness/population/counter); the C2 predicate names only
`c2-setup-arms.py`, `c2-forgery-probe.py`, the two fixtures, the tool and the r92 before-tool. No import, no
shared scratch, no shared helper between the two searches (each freezes its own arms). Either claim verifies
with the other unlanded. The only shared substrate is the lane disk the harness clones (read-only for the
search; the C2 probe never touches it). Nothing in either predicate conditions on the other's verdict.

## Prereg-vs-claims universal words (seat assignment item 4)

Checked the prereg sentence by sentence for `every/all/always/never` and its counters:
- "every ITEM line is printed" — descriptive of the h-crash-late fixture, accurate.
- "every receipt prints its instruments' full sha256" — future-tense promise about receipts; the controls/
  receipts do print full sha256 (`c1-control-r93-rule.txt`, `c2-control-r93-probe.txt`): enumerated warmth,
  hold.
- "No work does not reach errored=2" / "No work does not reach 10" — `No work` = the do-nothing control, one
  named thing; holds.
- "refuses every other setup arm" — universal over exactly the 8 enumerated setup arms; holds for the
  enumerated 8 (confirmed live: `receipts/c2-after-receipt.txt`, non-conforming: none), and the unenumerated
  family is pushed to limit (i).
- FA "every non-zero exit errored" — descriptive of an edit, accurate.
The probe docstring's "Every setup failure exits 2…" is the one universal the instruments do not enumerate and
cannot honour (counterexample 1 above); the prereg's wording wisely avoids that universal, so this is a
docstring defect to amend, not a claim falsification.

## FALSIFIES-WORDING (one, scoped) and NO-FALSIFICATION (the claim sentences)

```
The c2-forgery-probe.py frozen instrument (P1) states: "Every setup failure exits 2 with one
`C2-FORGERY-FATAL:` line on stderr: --fixture/--tool/--before not a readable regular file; …"
Reproducer: .ufo/waves/round-94/w1/R94Critic/receipts/c1.err — a readable regular binary --tool file passes
the isfile+R_OK gate and then raises UnicodeDecodeError in open(...).read(); exit 1, traceback, no FATAL line.
```

```
FALSIFIES-WORDING (instrument docstring, not the prereg's counted claims):
census/round-94/c2-forgery-probe.py line 5 — "Every setup failure exits 2 with one `C2-FORGERY-FATAL:` line on
stderr".
Reproducer (copied receipt): .ufo/waves/round-94/w1/R94Critic/receipts/c1.err
```

C1 counted sentence ("both crash fixtures errored while the two semantic kills killed and the survivor
surviving", before-2/after-0) — `NO-FALSIFICATION`; re-ran live and matched. C2 counted sentence ("10
conforming arms; refuses every other setup arm with exit 2") — `NO-FALSIFICATION` of the enumerated arms;
re-ran live and matched (`receipts/c2-after-receipt.txt`), with the one residual-defect family beyond the
enumeration (a readable-but-present non-UTF-8 tool) documented above for r95. Both do-nothing controls
reproduced (r93 rule `killed=4`; r93 probe arms `conform=3` from the frozen receipts). No amendment needed to
`plans/round-94.md` for the claims themselves; the only amendment I recommend is narrowing that one docstring
sentence (or catching the decode) in a future instrument commit.

## Receipts in this seat dir

- `receipts/c1-after-receipt.txt` — my live C1 predicate re-run (`errored=2 killed=2 survived=1`, exit 0)
- `receipts/c1-control-rereceipt.txt` — my live r93-rule re-run (`killed=4`, exit 0), same as frozen control
- `receipts/harness-out-control/*.harness-out`, `receipts/harness-out-after/*.harness-out` — the 10 harness
  outputs the offline rules ran over
- `receipts/offline-rule-eval.py` + `.out` — candidate-rule evaluation (composite rule meets the predicate)
- `receipts/c2-after-receipt.txt` — my live C2 predicate re-run (`arms=10 conform=10`, exit 0)
- `receipts/probe-cheap.py` + `receipts/c2-cheap-armname-receipt.txt` — arm-name-fitted probe scoring 10/10
  without running a single forgery
- `receipts/c1.err` (binary tool, exit 1 + traceback — the FALSIFIES-WORDING exhibit), `receipts/c2.err`
  (unreadable fixture, conforms), `receipts/c4.err` (reordered SUMMARY, conforms with a mis-worded line)
