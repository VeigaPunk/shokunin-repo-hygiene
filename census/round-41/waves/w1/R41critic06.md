# R41critic06 — claim-sizing attack on the r41 preregistration (C1, C2, C3)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · freeze e2a74312af4233963e44e4dbb38838ece07b8bd2 · instruments 6682b98175b995ee4646ffd1ea6bd8a12cd353dd · base 7eebc183f2685d1ea9b004b4de22c09a8a4035a7 · measured-revision for C1 bffcc0f660ff36eb8add3f61582748a7af019a5b.

Seat scope: read-only attack plus scratch controls. Nothing in the lane, the frozen counters, populations, controls, the pinned tool, or the preregistration was edited. Attack candidates and outputs live only under `.ufo/waves/round-41/w1/R41critic06/`. Scratch under `/fast/scratch/hyaku/souji-r41/R41critic06` (removed before this report). No git mutation was run. Tooling: nothing installed.

Rule source. The addendum "section 9" is not a tracked file in the lane. I applied the four rules the assignment enumerates (one concrete after-state; no universal clauses; a do-nothing control the target cannot be reached by; axis named by the surface changed). Round-40 lessons paraphrase §9 as "one concrete after-state and one re-derivable counter" (`corpus/lessons/round-40.md:116`, `:123`). The axis precedent is `corpus/lessons/round-25-verifier-spotcheck.md:34`, `:60`, `:79`: refusal-surface probes are coverage, and a runnable checklist is operability. The round-25 calibration precedent is `:176-179`: a calibration claim counts mismatches rather than asserting.

## Verdicts

| Claim | Target reachable by a skip-the-work control? | Axis label | Sizing verdict |
|---|---|---|---|
| C1 calibration | **Yes.** Copied counter values plus one fabricated registry row (S258) meet the full target, with no source opened. | Weak. The measured after-state is correction-line presence. The mismatch count is 3 before and after, so the axis it names does not move. | **Fails the §9 control test.** Named limit for the L1. |
| C2 operability | **Yes, partially.** A tool that silently drops the `*.ready` dispatch rule still meets the full 21/21 target. The population file is never read. | Right (a runnable checklist is operability, r25 precedent). | Gap in the counter's coverage of its own grammar. Named limit for the L1. |
| C3 coverage | **Yes, fully.** A fixture that never executes the tool and only attests the source labels meets 19/19 killed. | Right (refusal-surface probes are coverage, r25 precedent). The predicate's word "reaches" is not what the counter measures. | **Fails the §9 control test as measured.** Named limit for the L1. |

The do-nothing controls in the preregistration (C1 corrected=0; C2 tool absent and the always-clean stub at 2/21; C3 fixture absent and the PASS-all stub) do fail as written. Every reachable route above is a partial-work control, not the do-nothing one.

## C1 — calibration

Attack control A (`c1/lesson-control-sourced.md`, `c1/SOURCES-control.md`). This is the copied counter output plus one fabricated tier-A row. The row is `| S258 | git builtin/worktree.c at tag v2.56.0 — … | code | A | … | v2.56.0 builtin/worktree.c (control text) | control | mined | 2026-10-28 | - | r41-control |` appended to the tip `corpus/SOURCES.md`. No git source was fetched. Its only purpose is to satisfy the cell-text check in `sourced()` (`c1-counter.py:96-107`).

Scored with the frozen harness:

```
bash census/round-41/score-candidate.sh c1 /fast/scratch/hyaku/souji-r41/R41critic06 corpus/lessons/round-41.md=…/c1/lesson-control-sourced.md corpus/SOURCES.md=…/c1/SOURCES-control.md
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=1 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1
EXIT=0
```

Output file: `c1/score-sourced.out`. This meets the whole target.

Attack control B (`c1/lesson-control-unsourced.md`): identical except `source=-` on I1.

```
SUMMARY items=3 mismatched=3 corrected=2 uncorrected=1 junk=0 rewritten=0 sourced=0
EXIT=1
```

Output file: `c1/score-unsourced.out`. The sourced leg is therefore load-bearing, but only as a text check on a registry row.

What the attacks show:

1. The `sourced` leg checks cell text (tier `A`, status `mined`, opened `2026-10-28`, and both `v2.56.0` and `worktree.c` appear), not provenance. A fabricated row passes. The row also is not required to be a new row or to carry a snapshot. The preregistration's "a new tier-A mined registry row opened 2026-10-28" is therefore not measured as a source.
2. The I1/I3/I4 derived values are deterministic at the measured revision. A correction can be produced by copying the counter's ITEM output rather than by any re-derivation. The counter cannot tell the two apart. The do-nothing control and the junk control do fail, correctly.
3. `mismatched=3` and `items=3` are constants under every compliant candidate, because the filed text is never rewritten (`rewritten=0`). The only after-state variable is `corrected`, which counts appended lines. The surface changed is `corpus/lessons/round-41.md`, a correction ledger, not the calibrated statements. Under the r25 precedent, a calibration claim should count mismatches; this one asserts corrections. The axis label is therefore the weakest of the three.
4. I3's derivation is a proxy. Unequal `register_cells=` values are read as "different register files" (`c1-counter.py:79-85`). The round-40 spot-check (`corpus/lessons/round-40-verifier-spotcheck.md:33`) identifies the register inputs themselves (`census/round-39/cells.tsv` vs `census/round-40/cells.tsv`). The counter never reads those inputs. This is a named limit.

Verdict C1: **sizing fails the control test; axis label weak.** The target is reachable by a copy-and-fabricated-row control. The counter cannot distinguish that from the claimed work.

## C2 — operability

Attack control C (`c2/score-stub-clean.out`): the always-clean stub, scored with the frozen harness, reproduces the preregistration's "2 of 21" figure.

```
case-clean=PASS
case-clean-dispatch-after=PASS
… (17 FAIL lines)
SUMMARY cases=21 pass=2 fail=19 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL tool_sha=5ccb4fb2705b
EXIT=1
```

This is the expected do-nothing result. It fails.

Attack control D (`c2/freeze-check-executor09-copy.py`, byte-identical to `.ufo/waves/round-41/w1/R41executor09/souji-freeze-check.py`, sha256 `e0bec95b…f7ba`). This is another seat's candidate, scored by me as a reference only.

```
case-… all 21 PASS
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=e0bec95b77a0
EXIT=0
```

Output file: `c2/score-executor09-copy.out`. Note that the copy is a real implementation and is not a skip control.

Attack control E (`c2/freeze-check-mutant-no-ready.py`): the copy with one line changed at line 202, `if not (base.endswith("-dispatch.json") or base.endswith(".ready")):` becomes `if not base.endswith("-dispatch.json"):`. That is, the tool silently drops the `*.ready` half of the DISPATCH-BEFORE-FREEZE rule (frozen grammar, `c2-counter.py:38`).

```
case-… all 21 PASS
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=cce81f366798
EXIT=0
```

Output file: `c2/score-mutant-no-ready.out`. The mutant meets the full target. Cause: the counter's dispatch cases (`c2-counter.py:195`, `:211`) only write `w1-dispatch.json`. No case writes a `*.ready` file.

Attack control F (population pin). `c2-counter.py` never reads `census/round-41/c2-cases.tsv`. `grep -n "cases.tsv\|open(" census/round-41/c2-counter.py` returns only fixture-write calls. The prereg's `Population: census/round-41/c2-cases.tsv sha256=4854335…` is therefore not enforced. The in-code `CASES` tuple is what runs. The `.tsv` happens to mirror it at 21 rows, but nothing compares them.

What the attacks show:

1. The counter's 19 synthetic cases cover all 14 documented finding classes except the `*.ready` branch of DISPATCH-BEFORE-FREEZE. A tool that ignores `.ready` files passes the full target.
2. The C2 population pin is cosmetic. The counter neither reads nor cross-checks the `.tsv` against its in-code cases.
3. The always-clean stub and tool-absent controls fail, correctly. The attacks that pass are partial implementations, not do-nothing controls.

Axis label: **right.** The surface changed is a prose freeze rule replaced by a runnable command (`tools/souji-freeze-check.py`). This matches the r25 precedent that runnable checklists are operability.

Verdict C2: **label right; sizing has a coverage gap in the counter.** The target can be met by a tool that drops a documented branch. Named limit for the L1. Do not edit the frozen counter.

## C3 — coverage

Attack control G (`c3/source-attest-fixture.py`). The fixture never runs the tool and imports no subprocess. It applies the counter's own `SITE_RE` to the `--tool` source text, finds the nth refusal label, and asserts the frozen class for that site (table transcribed from `c3-sites.tsv`). Each probe id is PASS iff its site's label matches.

```
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f0734534e084
EXIT=0
```

Output file: `c3/score-source-attest.out`. This meets the whole target.

Why it works: the counter's mutation (`c3-counter.py:102-105`) rewrites one label to `ZZ-MUTANT` in the source. The source-reading fixture then reports exactly that site's probes FAIL, and that is a kill. The counter never checks that any refusal is triggered at runtime, never mutates behaviour, and never mutates a trigger. Only the label is perturbed.

What the attack shows:

1. "Reaches every refusal site" in the predicate is not what the counter measures. It measures label sensitivity of the fixture's verdict to source text. A fixture that never executes `tools/souji-worktree-drift.py` scores 19/19.
2. The killing rule is per-site exact-set equality (`c3-counter.py:139-145`), so the source-reading fixture is not a stub. It must map each site to the right probes. That is cheap to write and is exactly the fault the predicate says to catch.

Axis label: **right.** The surface changed is a refusal-site probe battery (`tests/fixtures/…`) and r25 treats this as coverage.

Verdict C3: **label right; sizing fails the control test as measured.** A skip-the-work fixture meets the target. Named limit for the L1. Strengthening would need a behaviour mutation (disable or reroute the site) that a source reader cannot satisfy. That is a new counter, not an edit to this one.

## Limits named for the L1 (not edited here)

- C1: `sourced()` checks registry cell text only. Provenance is not measured. A fabricated row meets the target (`c1/score-sourced.out`).
- C1: `mismatched` is invariant under every compliant candidate. The after-state measures correction-line presence. Axis wording should be reconsidered (r25 calibration precedent).
- C1: I3's derivation infers "different register files" from unequal `register_cells=` counts. The register inputs are not read.
- C2: the `*.ready` branch of the DISPATCH rule is untested. A tool that drops it meets 21/21 (`c2/score-mutant-no-ready.out`).
- C2: `census/round-41/c2-cases.tsv` is pinned in the prereg but never read by the counter.
- C3: the counter mutates labels only. A source-reading fixture meets 19/19 with zero runtime refusals (`c3/score-source-attest.out`).

## Commands run (all read-only against the lane, or in seat/scratch)

```
git -C <lane> log --oneline -3 ; git -C <lane> rev-parse HEAD
git -C <lane> show e2a74312af4233963e44e4dbb38838ece07b8bd2:corpus/SOURCES.md > .../c1/SOURCES-tip.md
git -C <lane> show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/SOURCES.md | grep -n "S258\|^| S25[6-9]"   # S258 absent at measured rev; only S256, S257
git -C <lane> show bffcc0f…:census/round-40/records/c1-before.txt | head   # register_cells=6 receipt
git -C <lane> show bffcc0f…:census/round-40/records/c1-after-h.txt | head   # register_cells=3 receipt
git -C <lane> merge-base --is-ancestor 7eebc18… e2a7431… && echo base-ancestor-of-freeze   # printed
git -C <lane> log --oneline --diff-filter=A -- census/round-41/preregistration.txt          # e2a7431
git -C <lane> status --porcelain -- census tools tests corpus SKILL.md                      # empty
sha256sum tools/souji-worktree-drift.py census/round-41/{c2,c3}-counter.py census/round-41/{c2-cases,c3-sites,c1-items}.tsv   # all match the prereg pins
bash <lane>/census/round-41/score-candidate.sh c1 <scratch> corpus/lessons/round-41.md=… corpus/SOURCES.md=…   # sourced control  → EXIT=0
bash <lane>/census/round-41/score-candidate.sh c1 <scratch> corpus/lessons/round-41.md=…                        # unsourced control → EXIT=1
bash <lane>/census/round-41/score-candidate.sh c2 <scratch> tools/souji-freeze-check.py=<lane>/census/round-41/controls/c2-stub-clean.py   # EXIT=1, 2/21
bash <lane>/census/round-41/score-candidate.sh c2 <scratch> tools/souji-freeze-check.py=…/freeze-check-executor09-copy.py   # EXIT=0, 21/21
bash <lane>/census/round-41/score-candidate.sh c2 <scratch> tools/souji-freeze-check.py=…/freeze-check-mutant-no-ready.py  # EXIT=0, 21/21
bash <lane>/census/round-41/score-candidate.sh c3 <scratch> tests/fixtures/r41-refusal-sites.py=…/source-attest-fixture.py  # EXIT=0, 19/19
grep -n '"dispatch-before-freeze"\|"clean-dispatch-after"\|\.ready' census/round-41/c2-counter.py
grep -n "cases.tsv\|open(" census/round-41/c2-counter.py
rm -rf /fast/scratch/hyaku/souji-r41/R41critic06   # scratch removed
```

Procedure note. An early chained launch of five background scores failed with `bash: c1: No such file or directory` because a `&&` chain put the variable assignments in a background job. Those failure outputs were overwritten by a clean re-run with explicit paths. The `score-sourced.out` file came from the first, correctly-formed run (identical command). An earlier `set -e` in the persistent shell aborted one later call with no output. It was reset with `set +e` and the call re-run. The `freeze-check-executor09-copy.py` file was accidentally edited once. It was restored from the original with `cp`, and its sha256 was re-verified as `e0bec95b…f7ba`. Its `executor09` score (`c2/score-executor09-copy.out`) was taken before that accidental edit.

Installs/updates: none.

## Not assessed

- R1 (residual M19-M21): not a claim; out of this seat's scope.
- The attack controls under `c1/` contain a fabricated registry row (S258). They are control artifacts for scoring only. They are not candidates and must not land.

## Verdict (overall)

Sizing is not sound as frozen. Each of C1, C2, C3 is reachable by a partial-work control that passes the full target: C1 by a copied correction plus a fabricated row, C2 by a tool that drops the `*.ready` dispatch branch, and C3 by a fixture that never executes a refusal. Axis labels are right for C2 and C3. The C1 label is weak because the after-state does not move the mismatch the axis names. All six limits above are named for the L1 and are not edited here.
