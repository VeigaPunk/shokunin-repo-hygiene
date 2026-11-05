# S65CriticClaims — souji round 65 critic of frozen claims C1 and C2

Seat: S65CriticClaims (leaf critic, no subagent dispatch). Lane master at review: `16da2445088ccca15aa32c66841d878ee57a8706`.
Mutating git/jj: none. Scratch `/fast/scratch/hyaku/souji-r65/S65CriticClaims/` removed before yield.
Tool installs: none. Copies of this report and receipts: `.ufo/waves/round-65/w1/S65CriticClaims/`.

## Verdict summary

| # | Item | Verdict | Severity |
|---|------|---------|----------|
| 1 | Chronology, git ancestry | HOLDS (ancestry proven) | — |
| 1b | Freeze-check `--chronology` arm "landed pre-freeze" (prereg sentence) | FALSE at frozen bytes | **H1** |
| 2 | Do-nothing adequacy and Q120/Q122 binding | HOLDS; C1 do-nothing is tautological for counts (see L4) | — |
| 3 | Predicate/counter/kill arithmetic | HOLDS (5 accept, 14 refuse, 12 base forgeries) | — |
| 4a | Q59 axis instrument | NOT RUN: `souji-axis-check.py` refuses (no MACHINE BLOCK) | **H2** |
| 4b | C1 axis (operability) | AGREE | — |
| 4c | C2 axis (calibration) and lowest-axis obligation | AXIS AGREES; obligation met formally, thin substantively | — |
| 5 | Causal separability | NOT SEPARABLE as written (C2 green depends on C1 landed writer bytes) | **M** (must be a named limit) |
| 6 | Wording drift | S3 "a file edited ... is refused" overclaims; C2 cannot see it | **H3** |
| 6b | Docstring escape of live-marker read | Two of four needles score live from a docstring | **M1** |
| 6c | V1 class is generic; V2 fixture contains no untracked file | Kill weaker than label implies | **M2** |

## 1. Chronology

Git ancestry, re-derived (`git merge-base --is-ancestor`), all TRUE:
- `2761f0aa` (instruments) is an ancestor of `d2850b3e` (freeze), and `3c5bfdc0` (controls) is a strict ancestor of `d2850b3e`.
- `d2850b3e` (freeze) → `022cf979` (writer+SKILL) → `40a371d8` (S2 literal) → `16da2445` (chronology arm) → HEAD.
- `40a371d8` is an ancestor of `16da2445`; the after receipts bind `40a371d8` (`census/round-65/records/c{1,2}-after.txt`), which is after the freeze.

Commit log, base..arm (`.ufo/waves/round-65/w1/S65CriticClaims/chronology-git-log.txt`):
```
2761f0aa 2026-11-05T09:57:05-03:00 round-65: instruments (c1/c2 counters, matrix, population, probes) + freeze-check chronology arm
3c5bfdc0 2026-11-05T10:36:32-03:00 round-65: do-nothing controls (C1 12 forgeries red, C2 findings=2 red) + SHA256SUMS pin
d2850b3e 2026-11-05T10:38:08-03:00 round-65: FREEZE — preregistration (C1 operability 19-row matrix, C2 calibration live-marker agreement)
022cf979 2026-11-05T10:40:42-03:00 round-65: land writer concealment refusals (visibility override, mode payload, symlink record, env) + SKILL statement corrections (R1)
40a371d8 2026-11-05T10:41:50-03:00 round-65: keep the S2 after-literal byte-contiguous in SKILL.md
16da2445 2026-11-05T10:43:16-03:00 round-65: land freeze-check --chronology arm (candidate bytes verified; missed the working-tree copy at the instruments commit)
```

Q122 (control bytes bound by content): `census/round-65/controls/c1-do-nothing.txt` blob `b8325c4a…` at `3c5bfdc0` equals blob at `d2850b3e`; `c2-do-nothing.txt` blob `b0d9973e…` likewise. `git diff --stat 3c5bfdc0 d2850b3e -- census/round-65/controls census/round-65/SHA256SUMS.txt` is empty. Q122 HOLDS.

Q120 (controls strictly before freeze, with exact bytes, commands, instrument digest, observed output): the receipts carry `rev=`, `instrument_sha256=` (c1 `6401b35d…`, c2 `afd4cb54…`), exact command, and slot sha `9fb55f35…` for the base writer. `SHA256SUMS.txt` at `3c5bfdc0` verified OK for all ten pinned files (`sha256sum -c` run from `git archive 3c5bfdc0`). Q120 HOLDS.

**H1 (High, record defect): the frozen preregistration states a false chronology.** Its preamble says `tools/souji-freeze-check.py --chronology` "landed pre-freeze" and that `--selftest` "stays … 52/52 with --chronology". At the freeze commit and every earlier commit, the CLI arm is absent:
- `git show <rev>:tools/souji-freeze-check.py | grep -c -- '--chronology'` → `2761f0aa 0`, `3c5bfdc0 0`, `d2850b3e 0`, `40a371d8 0`, `16da2445 11`.
- `add_argument("--chronology")` is absent before `16da2445`; the freeze-check selftest at `d2850b3e` runs `41/41` (`.ufo/waves/round-65/w1/S65CriticClaims/freeze-check-selftest-at-freeze.txt`). The 52/52 figure cannot have been produced at freeze.
- The `2761f0aa` commit message also claims the arm landed. The tree contradicts it.

Predicates are unaffected: no Target/Kill line depends on the freeze-check. The defect is a false sentence inside the frozen prereg, which cannot be amended. Severity High for the record; the closure judge must rule. The lesson must surface it under Q121 (`## Mistakes`).

## 2. Do-nothing adequacy (§9)

Reproduced independently (scratch counter run, receipts in deliver dir):
- C1 do-nothing (`base-writer` in the new slot): `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=12 new_honest=5 class_mismatches=12 regress=PASS`, `EXIT=1`. Body identical to `controls/c1-do-nothing.txt` except scratch paths.
- C1 after (`40a371d8:tools/souji-receipt-write.py`): `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0`. Body identical to `records/c1-after.txt` except scratch paths.
- C2 after: `MARKERS flag=1 inrun=1 env=1 unmerged=1`, `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0`.
- C2 do-nothing (base): `FINDING SCOPE-OVERREACH s2`, `FINDING GOVERNED-STATEMENT-UNRESOLVED s4`, `SUMMARY rows=4 findings=2 verdict=FAIL`, `EXIT=1`.
- C2 selftest: `SELFTEST pass cases=13 fail=0`, `STUB-ALWAYS-ZERO REJECTED`.

What the base cannot satisfy in each Target line:
- C1 Target needs `new_forgeries=0` (base 12), `class_mismatches=0` (base 12), `EXIT=0` (base 1). `new_honest=5`, `regress=PASS` and `rows`/`matrix=19` are satisfied by base, as expected for an honest-accept shape.
- C2 Target needs `findings=0` (base 2), `verdict=PASS` (base FAIL), `EXIT=0` (base 1). `rows=4` is satisfied by base.
- C2 cannot be turned green by wording alone: s2 and s4 claim writer markers the base blob lacks (SCOPE-OVERREACH), so a SKILL-only edit stays red. Verified by the `--selftest` case `do-nothing-base-s2-overreach-s4-unresolved`.

**L4 (Low):** C1's do-nothing arm is base-vs-base in the new slot, so `new_forgeries == base_forgeries` by construction. It proves that the base cannot pass; it does not test whether the counter discriminates partial candidates. Only the three selftest stubs (always-accept, always-refuse, refuse-without-token) test discrimination. Per-row mutant kill-power (remove one delta at a time) is not in the frozen instruments. The mutation-tester seats own that; I did not run it.

## 3. Predicate, counter and kill binding

- Matrix: 19 rows (A,B,C,D,T1–T5,N1–N4,V1,V2,MOD,SY1,SY2,P13) = 4+5+4+2+1+2+1 = 19. Accept rows A,B,T4,V2,SY1 = 5; refuse rows = 14. Base forgeries = refuse rows that base accepts: T1,T2,T3,T5,N1,N2,N3,N4,V1,MOD,SY2,P13 = 12. The SUMMARY arithmetic matches the Target.
- Counter `claim_upheld` = `new_forgeries==0 ∧ new_honest==n_accept ∧ class_mismatches==0 ∧ regress==PASS ∧ all_new_match`. The Kill rule (`new_honest<5`, `class_mismatches>0`, `regress=FAIL`, nonzero exit) is equivalent, because `all_new_match` failures force a nonzero exit.
- **L2 (Low):** the build-failure path (`CaseError`) increments no counter; only `all_new_match=False` flips `EXIT`. A SUMMARY line can read Target-shaped while `EXIT=1`. The Target's `EXIT=0` clause catches it, but SUMMARY text alone is not sufficient.
- C2: `SUMMARY rows=4 findings=N verdict=… ` with `rc = 0 if findings==0 else 1` matches the Kill rule.
- **L3 (Low):** the refusal class check is a substring of stderr, not a cause check. A writer that prints every class token in every refusal would pass the class column. Realistic writers do not do this; the counter has no defence against it.

## 4. Axis-of-surface (Q59)

**H2 (High, process):** Q59 says the axis check "must be an instrument" and must print `flags=0` before scoring. Running it:
```
$ python3 tools/souji-axis-check.py --prereg census/round-65/preregistration.txt --scorecard SCORECARD.md
souji-axis-check: refused: no `## MACHINE BLOCK ... END` section found
AXIS_CHECK_RC=2
```
The round-64 prereg also has no MACHINE BLOCK (`grep -c` = 0). The round-65 prereg therefore cannot pass the Q59 instrument. My hand review below is not a substitute under Q59. The lesson must record this under Q121.

- **C1 axis = operability: AGREE.** The claim changes a gate (the receipt writer) and is witnessed on a runnable fixture matrix over input edge classes. Q59's operability example applies directly.
- **C2 axis = calibration: AGREE.** The claim changes SKILL.md self-assessment statements and checks them against the writer bytes. Q59's "self-assessment-file change is a calibration surface" applies. It is not a coverage surface.
- **Lowest-axis obligation (C2, score 7):** met formally. C2 is declared on the lowest owned axis. Substantively it is thin: 4 SKILL.md rows checked by substring plus a lexical marker map. The calibration claim is supposed to catch overclaiming, and it misses the S3 overclaim in H3 below. I would score "formally met, substantively partial".

## 5. Causal separability (AXES rule: "each claim must be verifiable without the others having landed")

Argument for separability:
- C2's counter is revision-parametric. It reads only the bytes at one revision (`--rev`) plus the instrument population at `2761f0aa`. It does not consume C1's matrix or receipts. Its base-arm verdict (red) is produced without C1 landed.
- C1's counter does not read SKILL.md at all. C1 is verifiable without C2.

Argument against:
- C2's positive verdict requires the writer bytes to carry the C1 deltas. The REQUIRED sets (`closed_full` = flag+inrun+env, `inrun_landed` = inrun, `unmerged_refused` = unmerged) and the after-literals `S2_AFTER`/`S3_AFTER` name refusal tokens that exist only post-landing (`022cf979`). Without C1's landing, C2 can only be red. Its green is an artifact of C1's bytes.

Verdict: **NOT SEPARABLE as written.** The dependency is one-directional (C2 depends on C1; C1 does not depend on C2). The round must state this as a named limit. The prereg does not state it today. Q121 requires the lesson to surface it.

## 6. Wording drift traps

**H3 (High): the frozen S3 after-wording overclaims, and C2 cannot see it.** The pinned literal `S3_AFTER` (and SKILL.md line 839 at `40a371d8`) reads: "a flag set, or a file edited, while the wrapped command runs is refused with `RECEIPT-STATE-CHANGED-DURING-RUN`". The unqualified "a file edited" is contradicted by the bytes:
- Frozen matrix row T4 (`inrun-transient-restore`, `expect=accept`): a file edited and restored in-run is accepted (`CASE T4 … new=accept`, `census/round-65/records/c1-after.txt`). The statement says it is refused.
- My probe at `40a371d8` (`writer sha be344a7d…`, identical to the after slot): a gitignored file edited in-run was accepted, `rc=0`, receipt written (`.ufo/waves/round-65/w1/S65CriticClaims/ign-receipt-inrun-gitignored.txt`). The matrix has no ignored-file row, and the prereg's named limits do not mention ignored files.
- C2 passes this statement because the `inrun` marker is present. Its "agreement in both directions" claim covers marker presence, not statement breadth. The overclaim sits in exactly the direction C2 is supposed to calibrate.
- Recommended disposition: the lesson's Named limits must state that in-run detection is limited to status/index/tracked-and-untracked content visible to porcelain and to the snapshot, that transient edits restored before the snapshot are accepted (T4), and that gitignored in-run edits are accepted (probe above). The S2/S3 wording cannot be amended, so it must be qualified in the lesson.

**M1 (Medium): the live-marker read can be defeated by a docstring.** `live_markers` counts a needle live when its line contains `refuse(` or `return` as a substring. "returned" in a docstring therefore counts. Reproduced in scratch with the counter module imported read-only:
```
dead-in-docstring-with-'returned' markers: {'flag': False, 'inrun': False, 'env': True, 'unmerged': True}
```
The counter docstring names this limit ("a needle placed inside a docstring … ON a line that also carries … return … would still count live"), but the prereg Declared sentence ("the dead-token second-polarity mutant produces findings") is unqualified. The selftest dead-token mutant uses comments and plain literals only, so it does not exercise this path. Recommended: qualify the prereg sentence, or tighten the emission test to a real call or `return` statement.

**M2 (Medium): V1 kill is generic; V2 label overstates its fixture.**
- V1 `expected_class` is `lane worktree is dirty`, the pre-existing dirty-check message. Any dirty refusal satisfies the row, so the row does not show that the visibility override was the cause. The prereg's "refuses untracked-visibility concealment" is satisfied by the generic message.
- V2 is labelled `untracked-visibility-honest`, but its spec is `{"config_untracked_no": True}` only. The fixture contains no untracked file. It tests a clean tree with the concealing config, not an honest visible untracked file. The honest counterpart is not in the matrix.

**L1 (Low): regress fixture is taken from the lane clone's HEAD**, not the measured or base revision (`git clone --shared` of the lane root). A cross-check divergence against the base blob is reported but not fatal. Currently `match`. Recommended: bind the fixture to `--base-rev` or make divergence fatal.

**L5 (Low): N4/N2 dispute results are incomplete.** `census/round-65/probes/n4-n2-dispute-results.txt` has `head: cannot open '…/out.err'` lines for N4-R and N4-C, so stderr is empty for those lines; only rc and output existence are recorded.

## Items I did not run

- S297 source opening, knowledge entry and lesson drafts: scout/scribe seats own these.
- Per-row mutant kill-power of the writer deltas: mutation-tester seats own it.
- Sibling overlap: not in my scope.

## Named items for the lesson (Q121)

H1 (false chronology sentence), H2 (Q59 instrument refused), H3 (S3 overclaim vs T4 and gitignored in-run edits), M1 (docstring escape), M2 (V1 generic class, V2 fixture), the separability verdict (NOT SEPARABLE; C2 depends on C1's landed bytes), and L1–L5. Each needs a disposition in `## Mistakes` or `## Named limits`.
