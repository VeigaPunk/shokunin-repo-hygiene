# S59Scout — r59 read-only recon: r58 outside routed items, current SKILL assessment row, claim population, baselines, residual list

Date 2026-11-04. Leaf scout; **no production edits, no fleet/sibling edits, no commits/pushes, no mutating jj**. Every repo read is revision-scoped (`git -C LANE show <rev>:<path>`) or digest-checked against the frozen commit. Fixture Git calls used explicit `-C <scratch fixture>` after asserting `git rev-parse --show-toplevel` prints that fixture directory. No tooling installs (nothing needed; RULES.md channel check: **no install, no update — pacman untouched**). Own scratch `/fast/scratch/hyaku/souji-r59/S59Scout/`; own delivery `.ufo/waves/round-59/w1/S59Scout/` (receipts + `SHA256SUMS`).

## 1. Frozen claim read first (preregistration, controls, chronology)

Read `census/round-59/preregistration.txt` (18 lines, full) before any other lane surface. C1 is ONE bounded calibration claim: registry-kind mismatch `assertions=1 mismatches=1` → `mismatches=0` for the unique current assessment-comparison registry row; **not** parser repair, not general registry certification, not new coverage/capability. Numeric score unchanged (no mapping). `Before:` line records `REGISTRY-KIND-MISMATCH EXIT=1` at base `da5af55b5ea0a2a38edea05635a13416c698e6e7`.

Chronology verified (own reading, `git log --format='%h %cI %s'`):

| commit | committer time | content |
|---|---|---|
| `74455b72` | 2026-11-04T15:33:00-03:00 | executed controls retained (before.txt, c1-counter.py, controls.json, controls.py, controls-run.txt, sources-before.txt) |
| `19f44552` | 2026-11-04T15:33:21-03:00 | predicate freeze (population.tsv, preregistration.txt) |

`git merge-base --is-ancestor 74455b7 19f4455` → 0 (controls commit **is** an ancestor of the freeze, i.e. strictly before it); same for base `da5af55b`. So the r58 chronology failure (control committed *after* freeze) is not repeated here: controls precede the freeze by 21 s in committer time and by ancestry. Freeze commit adds only `population.tsv` + `preregistration.txt`; the controls commit adds the six control/instrument files — no overlap, no amendment.

Frozen bytes (own sha256 over `git show 19f4455:<path>` **and** over the worktree file — identical in every case, so the frozen counter/population/controls are unamended post-freeze):

- `census/round-59/c1-counter.py` `2c4d45aab440ef713f22a8d3b210e651d6e7047451cab26f9d4316f5a6451a6d` (matches prereg `Counter:` line)
- `census/round-59/population.tsv` `c2e24c9961dd8d54794b3dea1e959ead1072c493c095874d661d59bc0ef9adb0` (matches prereg `Population:` line)
- `census/round-59/controls.json` `1ec401ec00e88297fa9216dc515bdadc3901fa24bcd9c6cef9eb998fc2f9116c`
- `census/round-59/preregistration.txt` `8ca0c77503962f8d99d9a652db8d8906c3a00b9eb3e088238ec7cf479bca6ae3`
- receipts: `counter-at-base.out`, `counter-at-freeze.out` in my delivery dir.

Own re-execution of the frozen counter (public CLI, lane root, no writes):

| rev | stdout | rc |
|---|---|---|
| base `da5af55b…` | `FINDING REGISTRY-KIND-MISMATCH` / `SUMMARY assertions=1 mismatches=1` | 1 |
| freeze `19f4455…` | `FINDING REGISTRY-KIND-MISMATCH` / `SUMMARY assertions=1 mismatches=1` | 1 |

Both reproduce `census/round-59/before.txt` (EXIT=1). The frozen counter's own `--selftest --work DIR` (public path, own scratch) ran the four committed control cases green: unchanged→rc1, prose-forgery→rc1, duplicate-forgery→rc2, positive→rc0, `passed 4`, EXIT=0 — consistent with `census/round-59/controls.json` and `controls-run.txt` (EXIT=0). This is the *classification* counter's selftest; it is not the assessment comparator's selftest (see §3).

## 2. Claim population: exactly one kind mismatch — confirmed, and the population is one row

`census/round-59/population.tsv` holds a header plus **exactly one item line**: `R58-KIND | SKILL.md r58 assessment comparison | verdict comparator reads committed matrices and SCORECARD expectations | gate`. The frozen counter implements exactly one assertion over exactly one selected row: it collects lines starting `| r59 assessment comparison |`, falls back to `| r58 assessment comparison |`, requires `len(rows)==1 and len(row[0])==10` (else `FINDING REGISTRY-ROW-SHAPE`, rc 2), then compares `row[2]` (the kind cell) to `gate`; mismatch → `FINDING REGISTRY-KIND-MISMATCH`, rc 1.

At base and at freeze, SKILL.md contains **exactly one** `| r58 assessment comparison |` row (SKILL.md:776) and **zero** `| r59 assessment comparison |` rows, and that row's kind cell is `evidence`. Observed vs expected therefore differ on exactly one cell of exactly one row → the claim population is genuinely one kind mismatch. **Confirmed.**

Counter semantics re-derived from the frozen source (read-only, `census/round-59/c1-counter.py`): it reads `SKILL.md` at `--rev` via `git show`, counts classification only, and never executes the comparator it classifies. So a truthful kind edit legitimately passes; the counter is not execution authentication. The prereg's own `Kill:` line already says so.

### Independent row-selection probe matrix (own fixture, counter bytes untouched)

Receipt `row-selection-probe.txt` (11 cases) and `naming-shape-probes.txt` (4 cases). Each case wrote a synthetic SKILL.md into an isolated fixture git repo (toplevel asserted), committed, and ran the frozen counter with `--root <fixture> --rev <commit>`:

| case | rows present | rc | counter output |
|---|---|---|---|
| P1 | base r58 row verbatim (`evidence`) | 1 | REGISTRY-KIND-MISMATCH |
| P2 | r58 kind=`gate`, no r59 row | 0 | mismatches=0 |
| P3 | r58 `evidence` + r59 `gate` | 0 | mismatches=0 |
| P4 | r58 `gate` + r59 `gate` | 0 | mismatches=0 |
| P5 | r58 `gate` + r59 `evidence` | 1 | REGISTRY-KIND-MISMATCH |
| P6 | two r59 rows | 2 | REGISTRY-ROW-SHAPE |
| P7 | two r58 rows | 2 | REGISTRY-ROW-SHAPE |
| P8 | r59 `gate` only, no r58 row | 0 | mismatches=0 |
| P9 | r59 `gate` row with 9 fields (wrong shape) | 2 | REGISTRY-ROW-SHAPE |
| P10 | r59 `gate` + r58 `evidence` + prose forgery line | 0 | mismatches=0 |
| P11 | r59 `gate` + two r58 rows + prose forgery | 0 | mismatches=0 |

Planning-relevant consequences of these observed semantics (each is a property of the frozen counter, not a proposal):

- The counter selects the **r59-prefixed row when present** and ignores the r58 row entirely (P3, P8, P10, P11: a stale `evidence` r58 row coexisting with an r59 `gate` row still yields mismatches=0). So a green counter after the fix does **not** by itself prove the r58 row was reclassified; if the r59 row is added while the r58 row keeps kind `evidence`, the counter reads green while the historical row is still misclassified. The prereg's implementation line ("classify r58 comparator as historical gate; supersede with r59 assessment-gate.py") and the "unique current row" wording must be resolved by L1 explicitly: either (a) reclassify the r58 row's kind cell in place and register no r59 row, or (b) add the r59 row **and** reclassify the r58 row. Only (b) satisfies both the r58 defect text ("registered as `evidence`… correct registry classification") and a counter reading that stays honest after the fix. [INFERENCE — the frozen counter does not adjudicate this; L1 decides.]
- **Shape sensitivity**: the r59 row must carry exactly the 8 registry columns (10 pipe fields) or the counter refuses with `REGISTRY-ROW-SHAPE` rc 2 (P9) — a shape slip is a *could-not-evaluate*, not a clean pass.
- **Name sensitivity**: the counter matches the prefix string `| r59 assessment comparison |` exactly; a row named `| r59 assessment comparison gate |` is not selected and the counter falls back to the r58 row (N2 → rc 1). Naming is part of the predicate.
- Prose forgery ("This comparator is a gate.") is not a counter input at all (P10/P11 → 0): the counter reads only the table cell, so prose-level claims carry no weight for this claim. That matches the frozen control case named `prose-forgery` (still rc 1, because its fixture kept the wrong kind cell).

## 3. Missing selftest is a separate conformance debt, not part of this claim

Distinct from the kind mismatch, and confirmed as separate by the r58 outside routed defect 2 itself (`corpus/lessons/round-58-verifier-spotcheck.md:65`: "Correct registry classification **and** provide isolated self-invocation rc/finding tests; external discrimination fixtures do not replace the required gate selftest").

Observed facts:

- `census/round-58/c1-counter.py` (the r58 assessment comparator) has **no** `--selftest` mode: its CLI is exactly `--root` and `--rev`, both `required=True`; usage error exits **2** (argparse), which its own SKILL verdict map already declares as `2 CLI usage`. `grep -c selftest` on that file = 0.
- The current SKILL row (SKILL.md:776) self-test cell states this as a live debt: `external discrimination fixture supplied with the round; counter has no self-invocation certification`.
- PROTOCOL `## Gate standard` requires: "Every gate exposes a self-invocation mode over isolated fixtures (temp trees, no network, no live-tree write) asserting both the exit code and a stable expected finding-id, with the expected values committed in the owning repo and independent of the recomputation."
- `census/round-58/c2-gate.py` (the other r58 gate) **does** satisfy that shape: `census/round-58/c2-selftest.txt` shows 17 named cases with `pass rc=… want_rc=… findings=… want_findings=…` and `SELFTEST control=FALSE-GREEN-REJECTED stub_meets=4 discriminated=13 cases=17`, `EXIT=0`, against the committed expected table `census/round-58/c2-selftest-expected.tsv` (17 data rows) — this is the in-lane precedent shape for the successor's selftest.
- The frozen r59 `c1-counter.py` *does* have a `--selftest` (it delegates to `controls.py` over an isolated fixture). That selftest proves the **classification** instrument's discrimination; it is not the assessment comparator's selftest and cannot substitute for it.

Conclusion: the population is exactly one kind mismatch, and the absent assessment-gate selftest is a **separate conformance debt** that the prereg assigns to the implementation line (new `assessment-gate.py` preserving the two matrix-derived note comparisons *and* adding public isolated self-invocation with rc and stable finding assertions). The frozen counter will read `mismatches=0` either way — it does not certify the selftest exists. That selftest gap must be closed by the new gate, and any claim that "r59 satisfied the gate standard" must rest on that gate's own committed selftest, not on the classification counter.

## 4. r58 outside routed items — complete read

Read in full: `corpus/lessons/round-58-verifier-spotcheck.md` (68 lines, outside/non-author closure by hyaku; `admitted=false`, `rejected-honest-stop`) and `corpus/lessons/round-58.md` (79 lines, lane lesson). The outside spot-check's §"Routed defects — souji next round" carries exactly **three** routed items (lines 64–66):

1. **Preserve the honest-stop**: r58 C2's pre-freeze control commitment failed (freeze `e7f64f3` 11:44:19 vs executable oracle/control `1880343` 11:50:15, and the r58 C1 freeze receipt lacked command/revision/digest headers). Requirement: the next new claim must retain a revision/instrument-bound do-nothing control **before** predicate freeze and any scoring; later replays never backdate it. → **Addressed in r59** (see §1: controls `74455b7` precede freeze `19f4455` by commit ancestry and 21 s committer time; the four control cases retain exact input bytes/revisions, commands, instrument digest, expected and observed rc/findings). Also captured as the lane's own new `Q120` (worktree `corpus/QUALITY.md:316`, uncommitted sibling edit — not mine).
2. **Registry classification + selftest** (the one routed defect r59's C1 targets). Two halves: (i) the r58 comparator is registered `evidence` but "reads/compares persisted expectations and returns a verdict, meeting PROTOCOL's gate definition" — a status-neutral conformance defect, independent of the reproduced two-note result; (ii) provide isolated self-invocation rc/finding tests; "external discrimination fixtures do not replace the required gate selftest". → (i) is r59 C1; (ii) is the selftest half analysed in §3 and assigned to the new gate. Note the outside verdict explicitly separates this from the two-note result, so r59 C1 must not be read as re-admitting r58's C1/C2.
3. **Keep inherited debts OPEN**: visibility-parser (second opener, code-span/escape/link/TAB/lazy paragraph), recorder dirty-tree/overwrite, capture-counter row-set meta-test, historical receipt bindings, atomic-read/resource, diagnostic debts. → **Unchanged in r59**; see §7 residual list.

Also read for completeness: r58 outside §Claim re-checks (C1 independently re-measured 2→0 with 36-row matrices, 34 identical, exit-zero 10 and 8; C2 3/8→8/8 but **unprovable** for the missing pre-freeze control), §Axis verdicts (calibration improved / operability **unprovable** / coverage unchanged), §Discernment spot-check (S284 admit, S285 reject, both re-opened; SOURCES regex independently 207→209), §Learning trends (expansion unchanged, quality improved, discernment improved), and the lane lesson's §Scope and residuals (certification OFF, K5 HELD, assimilation none, `considerthese/` absent, mass-id-drift hold retained). The lane's r58 close-out is honestly recorded as a non-author rejected-honest-stop; nothing in r59 reopens it.

## 5. Current SKILL assessment row (verbatim, freeze rev)

`SKILL.md:776` at `19f4455` (section `## Round 58 current receipt interface`, SKILL.md:769; table header at :773):

```
| r58 assessment comparison | evidence | `python3 -B census/round-58/c1-counter.py --root LANE --rev FULL40` | 0 two corrections agree with committed matrix-derived values; 1 discrepancy data or unstructured input error; 2 CLI usage | external discrimination fixture supplied with the round; counter has no self-invocation certification | two historical r57 matrices and exact note templates in `census/round-58/c1-counter.py` | read-only git blobs; no writes | souji |
```

Observed: kind cell = `evidence`; entry command is a real, re-runnable verdict script (exit 1 on mismatch, exit 2 on usage — measured: usage error exit 2), i.e. by PROTOCOL's own definition ("a committed, re-runnable verdict script a lane owns: it reads surfaces, compares them against expected values persisted in its own repo, and returns a verdict") it meets the **gate** definition, which is exactly the routed defect 2 (i). The lane's own registry preamble (SKILL.md:204) states the inverse rule for `evidence` rows: "`evidence` rows are measurement producers, not gates … a row whose self-test cannot fail is a `probe` or an `evidence` row, never a `gate`" — the comparator *can* fail (exit 1), so `evidence` is the wrong kind cell.

Two self-consistency facts about the r58 comparator, useful for the new gate's derivation (own re-derivation, independent of the counter's code path, at base `da5af55b`): the two `census/round-57/records/c1-matrix-v{5,6}.tsv` matrices hold **36 data rows each** (37 lines with header; columns `fixture,counter,rev,base,exit,finding,findings_all,SUMMARY`), per-matrix `exit=='0'` counts are **10 and 8** (combined 18), and pairwise identical `exit`+`findings_all` = **34**; the two differing pairs are `B4-INLINE-NBSP-OPENER` and `C4-INLINE-CLOSED-COMMENT` (both `exit` 0→1). The two exact note templates the counter requires are present in SCORECARD.md at base and read (verbatim):
- `R58-CALIBRATION carry_identical=34 supersedes the r57 SCORECARD claim "all 33 carry-over rows".`
- `R58-CALIBRATION exit_zero=10,8 counted separately per matrix; the r57 two-file awk command emits the combined total 18, not the pair.`

A successor gate that preserves "its two matrix-derived note comparisons" must keep these derivations and these exact note strings byte-identical, or the existing `census/round-58/c1-counter.py` reading (measured at base and freeze: `assertions=2 mismatches=0 carry_identical=34 exit_zero=10,8`, EXIT=0 — reproduced in this recon) will no longer hold for the same input.

## 6. Baselines — source row counts and latest legacy scores

Receipt `baselines.txt`; counts use the outside spot-check's own regex `^ {0,3}\|\s*S[0-9]{3,}\s*\|` over committed blobs.

- SOURCES rows at base `da5af55b`: **209**. At freeze `19f4455`: **209** (unchanged by r59 so far). Worktree: **211** — the delta is uncommitted sibling edits (S286/S287 + a Round59 note line) present in the shared worktree; **not mine, untouched by this seat**. r58's own ledger: 207→209.
- Sources census, read-only (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`): **EXIT=0**, `souji ok …/corpus/SOURCES.md`, 64 W04 duplicate-url-across-scopes warnings at freeze (`census/round-59/sources-before.txt`: 64 duplicate-url lines + `souji ok` + `EXIT=0`); the same run now also reports W04 for S286/S287 (same URL, two scopes) — expected, not an error.
- Latest owned legacy scores (SCORECARD.md:13–15 at freeze): **coverage 8, calibration 7, operability 8** — unchanged across r24–r58 rounds; the lane records "no reproducible 0–10 mapping exists", so r59 C1 claims **no** numeric delta (prereg: "Numeric score unchanged: no mapping"). r59's axis is calibration (lowest owned legacy score 7).
- Registry inventory at freeze (`registry-kinds.txt`): 91 rows matching `| r…`; kinds: **gate 79, evidence 8, probe 3, tool 1**. The eight `evidence` rows are `r17-census-matrix, r18-census-matrix, r18-leak-count, r21-acceptance (r22 result-contract repair), r56 matrix runner, r57 receipt recorder, r57 matrix runner, r58 assessment comparison`. **Only the r58 assessment comparison is in this round's scope**; the other seven `evidence` rows are matrix runners/recorders/producers whose zero-exit semantics differ, and re-grading them is out of scope for a one-row population claim (recorded as a residual, §7).
- Latest committed QUALITY ids at freeze: Q116/Q117/Q118 (the worktree's Q119/Q120 are uncommitted sibling edits, not mine).

## 7. Residual list — open, unchanged by this round

Every item below is a **debt that stays open**; r59 C1 closes none of them, and none may be described as closed by the kind correction.

1. Visibility-parser debts: second opener, code-span/escape/link/TAB, lazy paragraph (r58 outside routed 3; r58 lesson §Scope and residuals).
2. Recorder dirty-tree / overwrite debt (r57 receipt recorder, SKILL.md:766 `evidence` row; r58 lesson).
3. Capture-counter row-set meta-test debt.
4. Historical receipt bindings; receipt-confinement atomicity and resource/intake bounds; diagnostic escaping.
5. C1 scale/diagnostics debt (scale of corrections, diagnostic byte counts).
6. Certification OFF and K5 HELD; assimilation none; r46 mass-id-drift hold; `considerthese/` absent in the lane root.
7. The seven other `evidence` registry rows (§6) — not re-graded here; a registry-wide kind audit is a separate claim, not this one-row population.
8. The r58 C2 operability claim remains **unprovable** (missing pre-freeze committed control); r59's chronology-compliant controls do not retroactively satisfy it.
9. Frozen counter scope limit: `census/round-59/c1-counter.py` measures one cell of one row and never executes the comparator it classifies — "it is not execution authentication" (prereg line 12). A green counter is not evidence that the new gate exists, runs, or self-tests.
10. Worktree state at this seat's reading: `M corpus/SOURCES.md`, `M corpus/QUALITY.md`, `?? corpus/lessons/round-59.md` — uncommitted sibling/L1 in-flight edits; this seat edited none of them, and the frozen digests above are unaffected.

## 8. Bounded planning data-walk (for L1 and the implementing seat; no edits made here)

1. **Registry edit site**: SKILL.md row 776, kind cell `[2]`, in the `## Round 58 current receipt interface` table (header at :773). Decide the shape question from §2: reclassify r58 row kind `evidence` → `gate` **and** register the successor `| r59 assessment comparison |` row with exactly 8 columns (10 pipe fields) whose name string starts exactly `| r59 assessment comparison |` (N2 shows a different name silently falls back to the r58 row).
2. **New instrument**: `census/round-59/assessment-gate.py` derived from `census/round-58/c1-counter.py` — preserve the two matrix-derived note derivations verbatim (36 rows/matrix, `exit=='0'` → 10,8, pairwise identical → 34, the two exact `R58-CALIBRATION` note strings), preserve `--root/--rev` result semantics (0 clean / 1 mismatch / 2 usage), add a stable finding id for mismatches>0, and add a public `--selftest --work DIR` mode asserting rc **and** stable finding ids over isolated fixtures (PROTOCOL Gate standard; in-lane precedent `census/round-58/c2-gate.py` + `c2-selftest-expected.tsv` + `c2-selftest.txt` 17/17).
3. **Committed expected values**: the selftest's expected rc/findings must be committed in the lane (e.g. a `census/round-59/*-selftest-expected.tsv`) and be *independent of the recomputation*; the freeze rule forbids amending counter/population/controls after scoring, so new expectation files are additions, not edits.
4. **Independent negative fixture**: the prereg's production-trial line requires running the new public gate over a committed lane snapshot **and** an isolated fixture with one correction omitted, so actual gate behaviour supports the classification (not just the label).
5. **Reuse the frozen controls as the classification discriminator** — they already bind the four independent cases; do not re-freeze a new counter.
6. **Registry row content**: self-test command + spelling, pinned-value path, write scope, owner per PROTOCOL §Registry; verdict map must declare any code beyond 0/1 (e.g. 2 usage, and the new mismatch finding id).
7. **Measurement discipline**: name the measured commit; do not claim admission (non-author closure owns that); no `[x]` SHONEN marks; no new score mapping.
8. **Do not** broaden: no parser repair, no registry-wide kind sweep, no closure of §7 items.

## 9. Limitations of this recon

- I did not execute the new assessment gate (it does not exist at freeze) and did not score any candidate; no implementation, no candidate measurement, no admission claim.
- The row-selection/shape/name matrices are *properties of the frozen counter* measured on synthetic fixture SKILL.md files in my own scratch. They characterise the instrument; they do not evaluate any proposed landing.
- The counter's verdict semantics were read from source and confirmed by probe; I did not audit its `git show` failure modes (e.g. a missing rev) — the counter would raise, not print a finding, which the prereg does not cover for the counter side. [INFERENCE from the code path, not measured.]
- Legacy score values, source-row counts and registry-kind counts are point-in-time readings at `19f4455`; the worktree already moves (SOURCES 211).
- The eight `evidence` registry rows other than r58's were listed, not assessed.

## Evidence index

Delivery `.ufo/waves/round-59/w1/S59Scout/` (digests in `SHA256SUMS`):
`counter-at-base.out` (frozen counter at base, rc 1), `counter-at-freeze.out` (frozen counter at freeze, rc 1), `frozen-digests.txt` (sha256 of counter/population/controls/prereg/before/sources-before at freeze and in the worktree), `registry-kinds.txt` (91 rows; gate 79 / evidence 8 / probe 3 / tool 1; one r58 assessment row; zero r59 rows), `baselines.txt` (sources rows 209 base / 209 freeze / 211 worktree; legacy scores 7/8/8), `row-selection-probe.txt` (11 cases), `naming-shape-probes.txt` (4 cases). Own scratch `/fast/scratch/hyaku/souji-r59/S59Scout/` (fixture repos + selftest work) removed before yield; receipts preserved above.

No production, fleet, sibling, or registry file was edited by this seat; no commit, push, or jj mutation was performed.
