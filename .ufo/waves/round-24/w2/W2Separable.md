# W2Separable — causal separability of C1/C2/C3 as landed (round 24, wave 2 FALSIFY)

## Status
STATUS: PASS — the attack ran to completion. All three **counters** are separable: each prints its target in a scratch tree that lacks the other claims' files. The attack lands one level down. (1) Every round-24 receipt except the gate check verifies only because of the `COUNTS_RE` widening. That widening lives in C3's file, but it is not C3's claim. (2) C2's landed bytes depend on C1's entry. (3) C1's counter is blind to C1's own after-delta in 778747e: its target was already reached at the instruments commit 1efe406.

Verdict per claim:
- **C1: survives as a separable claim.** Its counter needs no C2 or C3 files. Its receipt needs the widening. Its 778747e tool delta cannot be attributed by the counter (finding 4).
- **C2: separable as a claim, not as landed bytes.** A C2-only tree reaches 0 mismatches. The landed tree minus C1's entry gives `DANGLING-MAP-PATH` 1. The landed figure 6/6 includes C1's entry plus a ground line that no claim owns.
- **C3: survives as a separable claim.** Its counter needs neither C1/C2 files nor the widening. Its receipt needs the widening.

## Evidence
Environment: git 2.56.0, Python 3.14.8. Scratch was `/var/tmp/souji-r24-W2Separable/` (a `git clone --no-local` of the lane, worktrees and commits made only there), and has since been removed. Lane master read at `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`. `git diff --stat 778747e c3ca7ad -- tools corpus tests` is empty, so the tip bytes equal the after-state for every counter input. Lane writes: this report only.

Runner variants (scratch files):
- `base` = `a65fac98:tools/souji-receipt-run.py`. It is identical to the 1efe406 runner (`git diff --stat a65fac98 1efe406 -- tools/souji-receipt-run.py` is empty).
- `tip` = the 778747e runner.
- `widen_only` = base plus the tip `COUNTS_RE` only.
- `sym_only` = tip with `COUNTS_RE` reverted to base.

The diffs were checked: each variant differs from its source in exactly the `COUNTS_RE` block.

E1 — `python3 -B runners/<v>.py verify --root <scratch clone> <receipt>` over the 9 round-24 receipts and the 5 round-23 receipts:

| receipt | base | widen_only | sym_only | tip |
|---|---|---|---|---|
| c1-after, c2-after, c2-fixture-after, c3-after, r13-recheck-receipt | rc=2 RECEIPT-COUNTS-ABSENT | ok | rc=2 RECEIPT-COUNTS-ABSENT | ok |
| c1-control-stub, c2-control-base, c3-control-base-runner (rev 1efe406) | rc=2 RECEIPT-COUNTS-ABSENT | ok | rc=2 RECEIPT-COUNTS-ABSENT | ok |
| gate-check-r24-entry (`entries=1 ok=1 … fail=0`) | ok | ok | ok | ok |
| 5 × round-23 (C3 case d) | ok | ok | ok | ok |

The counterfactual commits were built in the scratch clone. Commit ids are scratch-only and were deleted with the scratch. Each counter was run from that commit's worktree:

| tree | construction | C1 counter | C2 tool `--rev` | C2 fixture | C3 counter |
|---|---|---|---|---|---|
| 778747e (as landed) | — | 8/8, exit 0 | `grounded=6 mapped=6 dangling=0 mismatches=0` | 9/9 | `cases=8 pass=8 refusals=2/2 regress=5/5`, exit 0 |
| cf-noC3 | ca7fc1c, runner ← a65fac98 | 8/8, exit 0 | `grounded=6 mapped=6 … mismatches=0` | — | `pass=6 refusals=0/2 regress=5/5`, exit 1 |
| cf-C1only | 778747e, runner + README + git-repo-structure-readonly.md ← 1efe406 | 8/8, exit 0 | `grounded=5 mapped=2 mismatches=3` (MISSING: r25 readings, **new C1 entry**, repo-size-census) | — | `pass=6 refusals=0/2`, exit 1 |
| cf-C2lit | 778747e minus `corpus/knowledge/count-objects-linked-worktree-garbage.md` | — | `grounded=5 mapped=5 dangling=1 mismatches=1` (DANGLING-MAP-PATH README:516) | — | — |
| cf-C2only | 1efe406 + 778747e README, minus the one F2 cell naming C1's entry | 8/8 (instrument tool) | `grounded=4 mapped=4 dangling=0 mismatches=0`, exit 0 | 9/9 | `pass=6 refusals=0/2`, exit 1 |
| cf-C2onlyG | cf-C2only + the 778747e `ground: F2` line on git-repo-structure-readonly.md | — | `grounded=5 mapped=5 dangling=0 mismatches=0`, exit 0 | 9/9 | — |
| cf-noC2 | 778747e, README ← 1efe406 | — | `grounded=6 mapped=3 mismatches=3` | — | — |
| cf-C3only | 1efe406 + 778747e runner | 8/8 | — | — | `cases=8 pass=8 refusals=2/2 regress=5/5`, exit 0 |
| cf-C3sym | 1efe406 + `sym_only` runner (no widening) | — | — | — | `cases=8 pass=8 refusals=2/2 regress=5/5`, exit 0 |
| cf-C1inst | 778747e, `tools/souji-size-census.py` ← 1efe406 | 8/8, exit 0 | — | — | — |
| 1efe406 (instruments, as committed) | — | `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, exit 0 | `grounded=4 mapped=2 mismatches=2` | — | — |

The entry gate (the gate-check-r24-entry command, run verbatim) prints `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0`, rc 0, on both cf-C1only and 778747e.

C2 kill rule (amendment, per entry): no counterfactual removes or regrounds any of the 4 entries grounded at base. Every C2 row above is kill-rule-clean.

## Findings
1. **Receipt verifiability is carried by the widening, not by C3.** Location: 778747e `tools/souji-receipt-run.py` :63-71 (`COUNTS_RE`). With C3's file reverted (cf-noC3 / base runner), 8 of the 9 round-24 receipts refuse with `RECEIPT-COUNTS-ABSENT`. This covers both C1 receipts, both C2 receipts, and C3's own receipt. With C3's symmetry kept but the widening removed (`sym_only`), the result is identical. With the widening alone on the base runner (`widen_only`), all 14 verify ok. The amendment names this coupling as a non-C3 change, `preregistration-amendment-1.txt` :42: "Separate widening (not a C3 clause): verify's COUNTS_RE also accepts the round-24 counts lines". The prereg separability statement, `preregistration.txt` :119, "Each counter runs without the others' files.", holds for counters only. It does not hold for the Q55 receipts that carry them. Impacted axes: operability (C3 attribution), calibration of the scorecard's evidence chain.
2. **The control receipts could not be verified at their own commit.** Location: ce5971c `census/round-24/records/c{1,2,3}-control-*.tsv`, whose message reads "before any after-data". The runner committed at ce5971c is byte-identical to the base runner, which refuses all three (E1, base column). They became `verify=ok` only when 778747e landed the widening. The controls were committed before the after-data, but their verifiability arrived with the after-state commit. This is a provenance caveat, not tampering: `run` does not gate on `COUNTS_RE`, and the tool digests bind at 1efe406.
3. **C2's landed after-state is not separable from C1's file; C2 as a claim is.** Locations: 778747e `corpus/README.md` :516 (F2 entries cell) and :509, "the F2 row lands only in the same commit as". Removing only C1's entry gives mismatches=1 (DANGLING). Applying the README's own landing condition (cf-C2only: drop that cell) gives mismatches=0 with an unchanged tool and fixture (9/9). Coupling also runs the other way: C1 landed without C2's rows takes C2 from 2 to 3 mismatches (cf-C1only, cf-noC2), so C1 alone harms the calibration axis. The landed figure `grounded=6 mapped=6` contains two additions beyond C2-alone (`grounded=4 mapped=4`):
   - C1's entry;
   - a `ground: F2` line added to `corpus/knowledge/git-repo-structure-readonly.md` :4 inside the r13 re-verification edit, which belongs to no claim in the prereg separability list (`preregistration.txt` :117-119).

   `preregistration.txt` :121, "counter is evaluated at the landing tip whatever C1 lands", pre-discloses the first coupling. The ground-line addition is undisclosed as a C2 input. It makes C2 harder, not easier (+1 grounded, and it is mapped), so it is not gaming.
4. **C1's counter cannot see C1's own after-delta.** Location: 778747e `tools/souji-size-census.py`, a 65-line diff: allowlist env, `/usr/bin/git` plus `--no-optional-locks`, `core.hooksPath=/dev/null`, a 900 s timeout, and refusal of a subdirectory `--repo`. With that file reverted to 1efe406 (cf-C1inst), and at 1efe406 itself, the frozen fixture prints the target with exit 0. Grepping `tests/fixtures/r24-size-census.py` finds no case for subdirectory refusal, env allowlisting or timeouts. The fixture strips GIT_* itself (:42-43), so env leakage is untestable through it. The C1 verified state is attributable to 1efe406, and the 778747e hardening is unmeasured. The pre-control 8/8 score was also observed in wave 1, `.ufo/waves/round-24/w1/ExecSizeCensusFixture.md` :4: "scores the scratch reference tool AND the L1-integrated lane tool (`tools/souji-size-census.py`, read-only use) at `cases=8 pass=8". The amendment's disclosed-deviation list (`preregistration-amendment-1.txt` :4-5, "the L1 ran sanity executions of the C2 tool ... and the C3 fixture") does not name a C1 after-level run before the controls. `[INFERENCE]` That omission makes ce5971c's "before any after-data" inaccurate for C1. The prereg's C1 before-state (`preregistration.txt` :62, "at base the fixture and tool are absent") is still honest, because the tool and fixture first landed at 1efe406.
5. **C3 survives.** cf-C3only and cf-C3sym both print `cases=8 pass=8 refusals=2/2 regress=5/5`, exit 0, with C1's and C2's after-files absent. The C3 counter needs neither the widening nor any C1/C2 byte. Only the c3-after receipt needs the widening (finding 1).

## Attack log
- A1 (revert C3's file, keep C1/C2): the C1 counter, C2 tool and C2 fixture are unchanged at target. The C1/C2/C3/r13 receipts and the controls fail verify → **lands on receipts, not counters**.
- A2 (split C3 into symmetry vs widening): the receipt dependency follows the widening exactly. The C3 counter follows the symmetry exactly → **the coupling is a shared-file artifact; C3's claim is clean**.
- A3 (remove C1's entry from the landed tree): C2 → DANGLING 1 → **lands on C2's landed bytes**.
- A4 (C2 alone under the README landing condition): C2 → 0, fixture 9/9, kill rule clean → C2 claim survives.
- A5 (C1 alone, no C2 rows/C3 runner): C1 8/8 and the gate ok. C2 gets worse (2→3) → C1 survives. C1 is not harm-free on calibration without C2.
- A6 (C1 tool at its instrument version): 8/8 → **lands on C1 attribution**: the counter is blind to the 778747e delta.

## Smallest safe correction
No history rewrite and no predicate change.
- In the scorecard/lesson, state that every round-24 receipt (controls included) verifies only under the 778747e `COUNTS_RE` widening, independent of C3's symmetry, and that the controls were unverifiable at ce5971c.
- Report C2 as "0 mismatches at tip; C2-alone counterfactual 0 at grounded=4". Disclose the git-repo-structure-readonly `ground: F2` line as an unowned C2 input.
- Attribute C1's verified state to 1efe406, and label the 778747e envelope hardening as unmeasured by the frozen counter (a future fixture case, not a re-specification of the 8 frozen cases).
- Add the wave-1 pre-control C1 8/8 run to the disclosed-deviation record.

Tools installed: none.

Scope note: at the end of the run, `git status --short` in the lane showed uncommitted edits to `tools/souji-receipt-run.py`, `corpus/knowledge/count-objects-linked-worktree-garbage.md` and `corpus/knowledge/git-repo-structure-readonly.md`. None of them were present at the start of the run, and none are from this seat: every run here used committed bytes in a `--no-local` scratch clone. The findings above apply to 778747e/c3ca7ad and not to those working-tree edits.
