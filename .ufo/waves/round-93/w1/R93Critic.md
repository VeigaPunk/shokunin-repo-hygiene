# R93Critic — souji r93 attack report (seat R93Critic, leaf, no subagents)

Scope: attack C1 and C2 wording, controls, chronology and certifying power. Lane read-only. Receipts and scripts under
`.ufo/waves/round-93/w1/R93Critic/` (`receipts/`, `scripts/`). Scratch clones under `/fast/scratch/hyaku/souji-r93/R93Critic/`
were deleted (6.6 GB) before this report. No git/jj mutation, no installs, no pacman/uv/npm.

## Verdict

NO-FALSIFICATION of any number. Every predicate and control number reproduces from committed bytes. C1's two targets are
bound, and only by the two rows, as the prediction says. C2's new fixture rejects the three named forgeries and also an unnamed
forgery (lookback-2) that the eight-edit probe does not contain. Five sentences overreach their instruments (listed below, not
falsified). C1 is a construction, not a blind test. C2 sits on coverage through the "edge classes" clause of AXES.md, but its
number is a count over a chosen set, not a fraction.

Counter-hygiene: one of my forgeries was wrong (G1: `max(cut - 3, 0) - 1` still reaches cut-3, so it is an equivalent mutant).
I replaced it with G1b before recording anything. G1 is not evidence of anything and is not claimed.

## Controls — do-nothing reach

C2 control, saved receipt `receipts/c2-control-out.txt` (r92 fixture, filed tool):
```
POSITIVE tool exit=0 tool_pass=20/20 pass
FORGERY F5 ... exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY F6 ... exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY F7 ... exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass
EXIT=1
```

C1 control (r92 population, same targets, r93 harness and search). Re-run output was printed to the session and not saved as a
file; the committed control is `census/round-93/controls/c1-control-r92-population.txt`. My re-run read:
```
SEARCH a491c22-<-to-<= line=491 killed=no rc=0
SEARCH h-ok-admits-one line=552 killed=no rc=0
SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0 scored=2 errored=0 killed=0 survived=2
EXIT=0
```

Also quoted from the committed file: r91 tool both arms, `SUMMARY cases=22 tool_pass=16 before_pass=16`, EXIT=1.

Both controls are red where the prereg says red.

## Chronology

```
2c82d362 2026-11-09 00:41:24  P1 instruments + c1-targets.json + c1-prediction.txt + KFF19/KFF20 + probe + S356 row
0d6442cc 2026-11-09 00:42:49  P2 controls
9a4ab88f 2026-11-09 00:43:29  F  preregistration (only file)
7bdb96b7 2026-11-09 00:45:06  A  after receipts
```
The order matches the prereg. Two construction caveats:

- P1 commits the prediction, the targets and the rows in ONE commit. The commit order cannot show the rows were designed before
  the targets were chosen. `c1-prediction.txt` says the targets were "named ... from reading the clauses".
- `controls/prefreeze-feasibility-note.txt` discloses that the C2 after arms (filed `inexact=0`, r91 `inexact=3096`) and the C1
  pristine harness were RUN before P1, with output "read in the session and NOT saved". Those numbers are not citable receipts.
  KFF19 was observed against the filed tool before the fixture was frozen. Nothing in the record shows how many fixture
  revisions preceded P1.

## C1 — construction verdict: CONSTRUCTION, with a verified residue

Constructed:
1. The targets are two survivors read off R92MutC1 (E1 and §3c). The population is built to those two clauses.
2. LD5 and LD6 are written from those two clauses, not from a neighbourhood sweep (prediction says so).
3. The predicted after (`killed=2`) is a statement about what the rows were designed to hit, not an out-of-sample prediction.

Verified by my re-runs (single-edit mutants of the pinned counter; `scripts/mut-hok.py`, `scripts/mut-width.py`):

| mutant | r93 population (66 rows) | r92 population (64 rows) |
|---|---|---|
| `h-ok-admits-one` (line 552 `>= len(pop) - 1`) | LD5 `got=UNRESOLVED rc=0 match=no`: killed | `SUMMARY rows=64 mismatches=0`, rc=0: survives |
| `a491c22` (`len(r) <= 3`, line 491) | LD6 `got=UNRESOLVED rc=1 match=no`: killed | `SUMMARY rows=64 mismatches=0`, rc=0: survives |

Both kills land on exactly the predicted row with the predicted class (LD5 rc 0 instead of 1; LD6 UNRESOLVED instead of MOVED,
because the width guard refuses P04's three-column row). Pristine r93 population (separability clone): `SUMMARY rows=66
mismatches=0 accepted=0 refused_true=0 errors=0`, `ROW LD5 ... rc=1 match=yes`, `ROW LD6 ... rc=0 match=yes`.

Unchosen neighbourhood (`receipts/unchosen-summary.txt`, `scripts/U*.py`, single-edit mutants NOT in the prediction):

| mutant | r93 | r92 | reading |
|---|---|---|---|
| U1 `== len(pop) and not unknown` → `... or not unknown` (admits unknown ids) | killed by 7 rows (LD1, LD1b, LD2, LD2b, LD1c, LD3, LD5) | killed by 6 rows | r92 already binds the unknown-id conjunct; the C1 claim is per target, not about the whole success test |
| U2 width `len(r) < 3` → `< 4` (refuses three-column rows) | killed by LD6 only | survives (rc=0) | LD6 binds a different spelling of the width guard, not only `<=` |
| U3 width `< 3` → `< 2` (admits two-column rows) | killed by LD2b | killed by LD2b (r90 row) | not an r93 contribution |
| U5 `== len(pop)` → `== len(pop) - 1` (rejects all-resolved) | killed by LD4r, LD5, LD6 | killed by LD4r | a tightening, not an admission; trivially killed |

So LD6 does bind the width guard's lower edge beyond the one spelling `<=` (U2), which is a point for C1's certifying power. U3
and U5 are killed by older rows and say nothing new. The h-ok relaxation survives r92 and is killed only by LD5 on r93.

What would have refuted C1, and did not happen:
- either target killed on the r92 population (control: neither is);
- LD5 or LD6 failing the pristine counter (neither does);
- a kill by a row other than LD5/LD6 (the mismatch lines name only LD5/LD6 for the two targets);
- a second relaxation of the same clause surviving LD5 (U1 is killed on r93; U2 is killed on r93). Not promised by the prereg, limit (i).

## C2 — axis verdict: coverage is defensible; the number is not a coverage fraction

AXES.md: coverage = "Fraction of the domain's real surfaces the skill governs (repo paths, tools, edge classes)". The claim names an
edge class (cut position across a well-formed sequence) and a command that shows it unmoved (the r92 fixture at 20/20 with F5-F7
passing; `rejected=5`, EXIT 1). That fits the "edge classes" clause.

Where it does not fit: the measured quantity is "forgeries rejected, 8 of 8" over a set of eight named edits chosen by the seat
(prereg C2 limit ii concedes the set is chosen). There is no surface denominator, so no 0-10 score can be re-derived. The honest
reading is "coverage of one edge class, demonstrated by eight named forgeries", not "coverage 8". The SCORECARD row should name the
surface moved and not carry a fraction.

Reference independence (the prompt's question):
- Implementation: the KFF19 reference block makes no codec or tool call (only comment text mentions the codec; checked by grep).
- Cross-check against Python's strict codec (`receipts/refcheck-output.txt`, `scripts/refcheck.py`):
  `REFCHECK compared=77305472 mismatches=0`, exhaustive over all 2- and 3-byte strings with a cut at every position, plus 2,000,000
  random 4-byte tuples at every cut. Reference and codec agree on the straddle rule over that domain.
- The tool's `_straddling_sequence` is codec-based, so the codec is common to tool and oracle. The reference independently checks
  the cut rule, not the decoder. A decoder bug would be shared by the tool and an oracle that agrees with it.
- The boundary table matches the S356 capture (`census/round-93/srcs/encoding.html` lines 3746-3819: E0 lower 0xA0, ED upper 0x9F,
  F0 lower 0x90, F4 upper 0x8F, default 0x80-0xBF).
- Shared constants: limit 200, head `limit//2`, keep `limit-head-1`, a three-byte back-scan. The reference copies these from the
  tool's contract, not from S356. "Independent" holds for the cut rule's logic, not for the excerpt format. A wrong excerpt format
  would pass both.

## Forgeries beyond the eight (certifying power of KFF19)

- G1b lookback-2 (head search looks at cut-1 and cut-2 only): `KFF19 ... inexact=796`, `SUMMARY cases=22 tool_pass=20`, EXIT 1.
  Rejected. Not in the eight. (`receipts/G1b.out`)
- G2-max3 (straddle end capped at start+3, so 4-byte sequences are never found): `KFF19 ... inexact=2388`, EXIT 1. Rejected.
  (`receipts/G2-max3.out`)

## Separability

(a) C1 without C2 (clone with `tests/fixtures/r93-k4-flagfail.py` and `census/round-93/c2-forgery-probe.py` removed;
`receipts/sepC1-final.txt`):
```
SEARCH a491c22-<-to-<= line=491 killed=yes rc=1
SEARCH h-ok-admits-one line=552 killed=yes rc=1
SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0 scored=2 errored=0 killed=2 survived=0
```
Pristine harness in the clone: `SUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=0`, LD5 `rc=1 match=yes`, LD6
`rc=0 match=yes`.

Reproduction caveat: first attempts in a plain git clone returned `errored` (rc=2) for both targets. The harness reads two
gitignored lane-disk paths: `census/operator-sweep-20261019/` (gitignored by `census/operator-sweep-*/`) and
`.ufo/waves/round-61/w1/S61ExecRealRecord/erratum-evidence.txt` (gitignored by `.ufo/waves/`). Stderr:
`C1-HARNESS-FATAL: fixture: FileNotFoundError ... erratum-evidence.txt` and `lane disk lacks census/operator-sweep-20261019`
(`receipts/sepC1-clone-*.err`). Under the kill rule that is `errored`, not a kill. The predicate says `--lane .`, so this is not
a falsification, but C1 is not reproducible from committed bytes alone. Lane-disk state is part of C1's instrument. The clone
was completed by copying ignored files from the lane (rsync, `.git`/`.jj` excluded); the C2 files were then removed again and
the rerun confirmed the removal.

(b) C2 after arm with the r92 C1 harness and population in the clone (`census/round-93/c1-false-row-harness.py` and
`c1-false-rows.tsv` replaced by the round-92 files; `receipts/sepC2-final.txt`):
```
POSITIVE tool exit=0 tool_pass=22/22 pass
FORGERY F1..F7 rejected=yes (F5, F6, F7 failed=KFF19)
FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass
```
EXIT 0. C2 needs no lane-disk files (committed bytes only), unlike C1.

## Sentences that claim more than their instrument enforces (not falsified; narrowing candidates for the L1)

1. C1 CLAIM: "Two counter edits survive every r92 row **because** no r92 run reaches their clause." The instrument measures
   survival (`killed=0 survived=2`); it does not measure reachability. "Because" is [INFERENCE]. Narrow to "survive every r92 row".
2. C1 CLAIM: "Two appended rows ... **bind both**." They bind the two spellings, not the clauses (U2 shows LD6 also binds a second
   spelling of the width guard, but nothing binds the clause as a whole). Prereg limit (i) says so; the CLAIM sentence does not.
3. C2 CLAIM: "an **independent** reference cut." Independent of the tool's code and the codec, yes; not of the excerpt format
   constants. Narrow to "independent of the tool's implementation".
4. C2 AXES wording "coverage 8": the count is 8 of 8 over a chosen set; no fraction is derivable. Narrow the SCORECARD wording to
   the edge class moved and the command; no number, or label as test-strength.
5. C1 reproducibility: not claimed, but a clean clone returns `errored` (rc 2). State the lane-disk dependency in the limits.

## Falsification list (explicit)

- FALSIFIES-NUMBER: none. Every number I re-ran matched the committed receipt or the prereg: C1 control killed=0 survived=2;
  C1 separability killed=2 survived=0; pristine 66/0 with LD5 rc=1 and LD6 rc=0; C2 control rejected=5 with F5-F7 at 20/20;
  C2 after rejected=8 and 22/22; r91 both arms 16/22; KFF19 inexact 0 (tool), 3096 (r91), 796 (G1b), 2388 (G2-max3).
- FALSIFIES-WORDING: none found. No sentence of either claim was contradicted by a reproducer. The five overreach sentences above
  are recorded for a narrowing amendment, not as falsifications.
- NO-FALSIFICATION of C1's "survive every r92 row" (rows 64, both targets, 0 mismatches) and of C2's "three forgeries pass the
  r92 fixture 20/20" (F5, F6, F7 at 20/20 in my control).

## Receipts index (`.ufo/waves/round-93/w1/R93Critic/`)

- `receipts/c2-control-out.txt`: C2 control, r92 fixture.
- `receipts/sepC1-final.txt`, `receipts/sepC1-clone-*.err`, `receipts/sepC1-clone-first-attempt.txt`: C1 separability and the clone failure.
- `receipts/sepC2-final.txt`, `receipts/F1..F7.out`, `receipts/N0.out`: C2 separability and per-forgery output.
- `receipts/mut-hok-r93.txt`, `mut-hok-r92.txt`, `mut-width-r93.txt`, `mut-width-r92.txt`: the two C1 targets on both populations.
- `receipts/unchosen-*.txt`, `receipts/unchosen-summary.txt`: unchosen C1 neighbourhood.
- `receipts/G1b.out`, `receipts/G2-max3.out`: extra C2 forgeries.
- `receipts/refcheck-output.txt`: reference vs codec cross-check.
- `scripts/`: mutant builders (`mut-hok.py`, `mut-width.py`, `U1-or-unknown.py`, `U2-width-lt4.py`, `U3-width-lt2.py`, `U5-eq-minus1.py`,
  `G1b-lookback2.py`, `G2-max3.py`), `run_u.sh`, `refcheck.py`. (`G1-lookback2.py` is the equivalent mutant, kept only for the record.)
