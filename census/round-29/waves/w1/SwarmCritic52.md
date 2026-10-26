# SwarmCritic52 — attack on the r29 w1 plan (spec generator + frozen prereg)

## Status

STATUS: PASS — the plan's counters, role mix and write scopes check out numerically, but the wave has one unassigned C2 obligation (round-29 receipt at the final tip), one dirty tracked source file that a byte-exact r26 recapture would launder, and a 6-item broken input path; the C3 landing artefacts are authored twice with no precedence rule. All four are one-line corrections, listed per item below.

## Evidence

- Contract read first: `census/round-29/records/preregistration.txt` (30 lines, claims at 1-9) at lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; prereg commit `b8cb4b31ce80e2e3314b88e85d40ea9873180804`.
- Workflow plan: `.ufo/waves/round-29/make-spec.py` (121 lines) and rendered `.ufo/waves/round-29/w1-spec.json` + `w1-dispatch.json`.
- Counters re-run by me at base (`cd <lane>; python3 -B …`, verbatim tail):
  - `tools/souji-registry-agreement.py --root <lane> --rev 691dd29… --list-rev b8cb4b3…` → `SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e`, rc 1.
  - `census/round-29/c2-counter.py --root <lane> --rev 691dd29…` → `r26 records=1382 failed=152 uncovered=14 floor_violation=0`, `SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29…`, rc 1.
  - `tools/souji-coverage-agreement.py --root <lane> --rev 691dd29…` → `grounded=13 mapped=13 dangling=0 mismatches=0`, rc 0.
  - `git show 691dd29…:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → `139`; `git grep -lE '^ground: F3' 691dd29… -- corpus/knowledge/ | wc -l` → `0`.
- Spec census (parsed from `w1-spec.json`): 68 items, roles `executor 21, scribe 10, reviewer 8, critic 8, scout 7, mutation-tester 6, connector 3, sentinel 2, simplifier 2, revenger 1`; 45 distinct `{W}/deliver-*` names, no duplicate target; 27 items deliver findings only; 3 items reference another item's deliverable by name.
- Run-7 routing that defines the shares (`/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md:152-156`): reviewer/mutation-tester→m_zfl; scriptor-flash roles "executor/labrat/scribe/sonic/simplifier/critic/revenger/sentinel"; attack share "reviewer/critic/mutation-tester/labrat".
- `git -C <lane> status --porcelain --untracked-files=no` → ` M .ufo/waves/round-26/w1/ScribeGateDraft.md`.
- Scratch (`/var/tmp/souji-r29-SwarmCritic52.K2vifR`, `git init` + `rev-parse --show-toplevel` verified) `check-ignore --no-index` probes, and a read-only `find`/`check-ignore --stdin -z` sweep of `.ufo/waves/round-26` (1383 regular files, 17 symlinks, 5 nested `.gitignore`).
- No tool installed; no lane write, no git/jj mutation, no network. Scratch removed.

## Findings

1. **C2's final-tip clause is unassigned.** The frozen C2 target requires `manifests=4` with "round 29 captured by the improved tool" (`preregistration.txt:7`), but no item touches the round-29 receipt: across all 68 rendered prompts the string `census/round-29/waves` appears zero times, and the round-end checklist item's command list (`deliver-landing-checklist.md` "git status", `jj-lane.sh state`, ls-remote, SHONEN count, census, misroot sweep, landing gate) omits `souji-wave-evidence-capture.sh <lane> 29` + commit. Without that step C2's kill rule ("the r29 manifest absent") fires at the tip no matter how good r26 is. Location: `preregistration.txt:7`; `.ufo/waves/round-29/w1-spec.json` item `PreReportGateReadiness`.

2. **A byte-exact r26 recapture would launder an unreviewed edit.** `.ufo/waves/round-26/w1/ScribeGateDraft.md` is a *tracked* lane file (committed at `166baa1`, 2026-10-25 14:37) and a committed receipt record: manifest line `8f25ae21f6009a889f308cb690f9dda2a2932af7743bc4c68f1534b34071bac0  ./w1/ScribeGateDraft.md`, matching the base blob (`git show 691dd29…:.ufo/waves/round-26/w1/ScribeGateDraft.md | sha256sum` = `8f25ae…`). The worktree copy is now `a7f30602248fc803eed8157f7a62d326152335e1936cc6bfaabf422cae9700dc` (`sha256sum`), mtime `2026-10-25 20:45:43`, i.e. after the prereg commit; the inserted text ("Inbound coordination: `ExecEntryF15` … round-31 …") has never been committed (`git log -S 'Inbound coordination'` empty). A recapture from the live worktree records `a7f306…`, the manifest then matches the new receipt, and the frozen counter prints `failed=0` — the C2 kill rules cannot see it, and `C2Classify152` only compares the 152 *absent* records, so a drifted *covered* record stays invisible. `.ufo/waves/` being gitignored does not protect files added to the index before the rule.

3. **C3's landing artefacts are authored twice with no precedence rule.** The four rows are produced by `SourcesRows` (`deliver-sources-rows.md`) *and* `C3MirrorValidate` (`deliver-sources-append-block.md`) *and* inserted by `C3RehearseAdmit`; the two entries are produced by `EntryIdentity`/`EntryByteEquality` (`deliver-entry-*.md`) *and* by `C3RehearseAdmit` (`deliver-duplicate-verdict-*.md`); the F3 README row by `ReadmeProvinceF3` *and* `C3RehearseAdmit`. The only end-to-end green in the wave (`F3=2`, rows 143, `grounded=15 mapped=15`, gate `entries=2 ok=2`) is the rehearsal's green **over its own bytes**, so unless the L1 re-runs every C3 counter at the landing commit it will carry a green that refers to different bytes — the r28 failure class (receipt verified against a proxy) re-created at the integration layer. Locations: spec items `EntryIdentity`, `EntryByteEquality`, `SourcesRows`, `ReadmeProvinceF3`, `C3MirrorValidate`, `C3RehearseAdmit`.

4. **The v2 capture's ignore decision depends on the destination being wiped first, and no fixture case covers that.** Base tool clears the receipt (`tools/souji-wave-evidence-capture.sh:98 rm -rf -- "$dst"`), and the specimen receipt still holds 5 committed nested `.gitignore` files (`git ls-tree -r 691dd29… -- census/round-26/waves | grep -c '\.gitignore$'` → `5`). Measured in scratch: a nested `fixture/` rule in the destination worktree *does* ignore `sub/fixture/b` (`sub/.gitignore:1:fixture/`), and renaming to `.gitignore.captured` clears it. So a v2 implementer that copies first (or that keeps the receipt dir) re-excludes exactly the 138 fixture files the fix exists to capture — while fixture case (7) stays green, because a fresh scratch repo has no stale destination `.gitignore`. Requirement (g) preserves "exit codes and promises", not the wipe.

5. **Exclusion is the only load-bearing surface for the r26 fix, and its size is measurable.** With the lane root rules alone (`.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/`), exactly 4 of 1383 source files land in `excluded.tsv` (all `…/__pycache__/*.cpython-314.pyc`); the remaining 1379 are captured, which clears the frozen `records>=1230`/floor 1230. So C2's target is reachable by *accounting*, and the frozen counter never reads `excluded.tsv` (`preregistration.txt:7` defines `failed`/`uncovered` only). This is permitted by the frozen text, but nothing on the wave pins what "accounted" means.

6. **`C1Fixture` names a flag the instrument does not have.** `tools/souji-registry-agreement.py` accepts only `--root/--rev/--list-rev/--stale-list` (grep `add_argument`, lines 102-105); the item's control says the always-zero emitter is "passed as `--tool`". The precedent is the fixture's own flag (`tests/fixtures/r25-coverage-agreement.py --tool …`), so the intent is recoverable, but as written a seat may patch the instrument — which the same item forbids.

7. **C1 kill rule (iii) has no independent attacker.** Kill rule (iii) is "the fixture accepts an always-zero emitter" (`preregistration.txt:5`); the only seat that runs that control is `C1Fixture`, i.e. the author of the artefact under test. `AttackC1` and `ReDeriveC1` do not exercise the delivered fixture.

8. **The prereg's row listing order contradicts the item id mapping.** `preregistration.txt:7` writes "Four new rows S216-S219 (statx, link, cmp, Broder …)"; the spec binds `S216 statx, S217 Broder, S218 link, S219 cmp` (items `C3CollisionGuard`, `C3MirrorValidate`, `SourcesRows`). Reading the frozen text as an ordering yields three wrong ids, which would break bidirectional K1 at the tip. The prereg is frozen and needs no amendment — the mapping must be recorded once by the L1 and used by `LessonGateF3`, which does not bind ids.

9. **Role shares are compliant (checked, not assumed).** Attack seats = reviewer 8 + critic 8 + mutation-tester 6 = 22/68 = 32.4% ≥ 25% floor. Flash = executor 21 + scribe 10 + simplifier 2 + critic 8 + revenger 1 + sentinel 2 = 44/68 = 64.7% ≥ 50%, matching the prereg's `44 of 68`. Both match the run-7 routing map; no violation.

10. **Write permissions and deliverable paths.** `{W}` exists and is in use (51 seat reports and 38 delivery files present at check time); `{W}/sources` and `{W}/assimilation` are creatable children of it. Two deliverables have no stated final path (`results-summary.py`, `sources-diff.py`) → mark wave-only or name a path. Three landing paths the frozen gate command needs do not exist and no item creates them at those paths: `census/round-29/sources` (absent from `ls census/round-29/`; `C3SnapshotPin` writes `{W}/sources/`), `census/round-29/records/quarantine-slice` (absent; `C3SliceGate` writes `{W}/assimilation/quarantine-slice`), `census/round-29/records/slice-verdicts.tsv` (absent; C3SliceGate delivers `{W}/deliver-slice-verdicts.tsv`).

11. **Six items cite a prompt path that does not exist.** `{L}/.ufo/prompts/souji-round-29.md` is missing (`ls` → no such file; `.ufo/` holds only `quarantine/` and `waves/`), while the real brief is `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md` (545 lines, §6 item 9 at line 417, item 10 at 437-545). Citing items: `C3MirrorValidate`, `C3SliceGate`, `PreReportGateReadiness`, `SliceRecheck`, `AuditPreregQ`, `MutateGuardAndRows`. Already observed live by a seat: `.ufo/waves/round-29/w1/SwarmExecutor10.md:16-17` — "`souji-shokunin/.ufo/prompts/souji-round-29.md` does not exist — `ls` reports".

## Item table

Verdict vocabulary: genuine / overlap-with:X / unsatisfiable-dependency / no-integration-value. "missing-input" is carried in the correction column (F11 above). No hard unsatisfiable dependency exists; three soft ones carry fallbacks.

| item | verdict | minimum correction |
|---|---|---|
| C1Fixture | genuine | say "the fixture's own `--tool`"; instrument has no such flag (F6) |
| C1UsedByRepair | genuine | — |
| C2ToolV2 | genuine | keep the `rm -rf` of the receipt before the ignore decision (F4); write escaped records per `escape-matrix.tsv`; refuse absolute symlink targets instead of committing them |
| C2FixtureV2 | overlap-with:C2ToolV2 (soft dep, base-tool fallback) | add a case: pre-existing nested `.gitignore` already in the destination + a source `.gitignore` at the same relpath |
| C2CheckIgnoreProbe | overlap-with:C2Classify152 (same 152-by-rule attribution) | keep as the algorithm authority; note it lands *after* the tool, so the L1 must diff it against the landed `check-ignore` sequence |
| C2Classify152 | genuine | extend from the 152 to "every source file vs the base manifest", else a drifted covered record (F2) is invisible |
| C2SymlinkClass | genuine | — |
| C2UutilsEscape | genuine | advisory to a concurrently written writer: the L1 must check the landed tool against the matrix |
| C3CollisionGuard | genuine | — |
| C3MirrorValidate | overlap-with:SourcesRows (same four rows) | precedence (see below); missing-input path (F11) |
| C3SliceGate | genuine | missing-input path (F11); slice + verdicts must also be placed at the prereg's `census/round-29/records/` paths (F10) |
| BaselineGates | genuine | pin the pre-landing `r28-wave-evidence-capture.sh` blob sha, since `C2FixtureV2` replaces that file |
| HistoryC1Sweep | genuine | — |
| HistoryC2Sweep | genuine | — |
| C3SnapshotPin | genuine | its `{W}/sources/` output must be copied to `census/round-29/sources/` before the entries' `snapshot:` field can resolve (F10) |
| C3RehearseAdmit | overlap-with:EntryIdentity+EntryByteEquality+SourcesRows+ReadmeProvinceF3 | label its green toolchain-only unless it consumes the delivered scribe files at finish; do not let it be the provenance of the C3 landing |
| PreReportGateReadiness | genuine | add the r29 capture+commit step (F1); do not restore or re-commit the dirty tracked file (F2/A3) |
| QCriteriaRedBefore | genuine | — |
| StaleStatementSweep | genuine | — |
| SeatResultsTool | genuine | no final path given: mark wave-only (F10) |
| SourcesDiffTool | genuine | no final path given: mark wave-only (F10) |
| C1Corrections | genuine | add "never edit the lane; deliver blocks only" (shared context has the rule, the item does not) and name one measurement revision for all three blocks |
| EntryIdentity | overlap-with:C3RehearseAdmit (same target file) | precedence (F3) |
| EntryByteEquality | overlap-with:C3RehearseAdmit (same target file) | precedence (F3); keep the raw-HTML check for cmp(1) |
| SourcesRows | overlap-with:C3MirrorValidate (duplicate authoring) | this item holds the id binding and must win; drop the second paste-ready copy (F3, F8) |
| LessonGateF3 | genuine | placeholders `<collisions=N>`/`<verdict>` are L1 fill; do not derive ids from the prereg's listing order (F8) |
| ReadmeProvinceF3 | genuine | — |
| QualityCriteria | overlap-with:CrossLaneAndHistory (supersession verdict arrives concurrently) | mark Q60-Q62 "subject to `pattern-map.tsv`" so a duplicate criterion is not landed as new |
| MistakesRows | genuine | `<landed-hash>` placeholders stay visible |
| ScorecardLogSkeleton | genuine | — |
| ReportSkeleton | genuine | the `{L}/.ufo/prompts/../../../…` path resolves to the fleet file but should be written plainly |
| OpenStatx | overlap-with:VerifySourcesQuotes | keep `Verify*` as the authority; scouts are corroboration |
| OpenLink | overlap-with:VerifySourcesQuotes | keep only its unique part (whether `stat(2)` is the better anchor for `%d:%i`) |
| OpenCmp | overlap-with:VerifySourcesQuotes | as OpenStatx |
| OpenBroder | overlap-with:VerifyBroder | as OpenStatx |
| F3RejectCandidates | genuine | — |
| SiblingOverlapScan | genuine | — |
| SliceRecheck | genuine | missing-input path (F11) |
| ReDeriveC1 | genuine | also run the delivered fixture with an always-zero emitter (F7) |
| ReDeriveC2 | genuine | — |
| VerifySourcesQuotes | genuine | — (byte-exact gate form is the authority) |
| VerifyBroder | genuine | — |
| AuditPreregQ | genuine | missing-input path; its "section 6 item 9 is not present at that number" is wrong — item 9 is at fleet line 417; keep the fallback pointer only |
| ReviewControls | genuine | — |
| DefectDisposition | genuine | — |
| CalibrationLedger | genuine | report-only; this is the calibration evidence base |
| AttackC1 | genuine | add the delivered-fixture zero-emitter run (F7) |
| AttackC2 | genuine | cross-checks `ReviewControls`' C2 states; keep both |
| AttackC3 | genuine | — |
| ScopeCriticF3 | genuine | — |
| AttackKillSemantics | genuine | — |
| AttackWavePlan | genuine (this report) | — |
| AssimilationContractCritic | genuine | — |
| SeparabilityAxes | genuine | its ordering rule is binding: entries and their cited rows land in one commit, or K1 fails at that commit |
| MutateC1Forward | genuine | — |
| MutateC1ReverseK2 | genuine | — |
| MutateC2Counter | genuine | — |
| MutateCaptureFixtureBase | genuine | its survivor list must be replayed against the *landed* v2 fixture |
| MutateC3Gates | genuine | missing-input path (F11) for its `{L}/.ufo/prompts` lines 477-484 |
| MutateGuardAndRows | genuine | missing-input path (F11) |
| CredScanR26 | genuine | must cover the 1379 files that will now be committed, not just the 152 |
| CredScanInputs | genuine | — |
| CrossClaimOverlap | genuine | — |
| CrossSourcePatterns | genuine | — |
| CrossLaneAndHistory | genuine | trains the Q60-Q62 supersession answer that `QualityCriteria` needs (see its row) |
| RevengeCaptureFailure | genuine | — |
| SpecHygiene | overlap-with:AttackWavePlan (counts/paths vs overlaps/deps/kill coverage) | keep — checks are disjoint; neither is padding |
| LaneRootStrayCensus | genuine | propose-only, nothing moved (correct for this lane) |

Verdict counts: 55 genuine, 13 overlap-with, 0 unsatisfiable-dependency, 0 no-integration-value (4 scouts are low-value corroboration). Attack share 22/68 = 32.4%; flash 44/68 = 64.7%. No kill rule is entirely unattacked except C1(iii) (F7) and C2's final-tip clause (F1).

## Attack log

- **A1 — unassigned final-tip obligation.** C2's `manifests=4` cannot be produced by any seat; the only artefact path for it (`census/round-29/waves`) appears in zero prompts. Fix: one line in `PreReportGateReadiness` — `bash tools/souji-wave-evidence-capture.sh <lane> 29 && git add census/round-29/waves && python3 -B census/round-29/c2-counter.py --root <lane> --rev <tip>` with expected `manifests=4 failed=0 uncovered=0 floor_violations=0`.
- **A2 — the recapture launders a dirty source (strongest counterexample).** Measured: the worktree copy of a *tracked, receipt-covered* r26 file no longer equals its base blob or its manifest record (F2), and no counter in the wave can detect it. Cheapest fix: capture r26 from committed bytes — `git -C <lane> archive <base> .ufo/waves/round-26 | tar -x -C <scratch>/src` and run the tool against that tree — or, if the worktree must be the source, require `git -C <lane> status --porcelain -- .ufo/waves` to be empty and log the dirty blob in the lesson; never restore it.
- **A3 — the proposed remedy is itself a boundary violation.** `deliver-landing-checklist.md` tells the L1 to "commit it under the round-26 entry" or "restore it from the branch". Committing bakes foreign text into the r26 record; restoring overwrites a file no seat created (the act the 2026-10-25 fleet incident was about). Reject both; A2's second option is the only safe handling.
- **A4 — destination-wipe ordering / fixture blind spot.** Measured: a nested destination `.gitignore` still applies to the ignore decision, so a copy-then-check v2 puts the 138 fixture files into `excluded.tsv` and still returns `failed=0 uncovered=0`; the fixture cannot see it because it starts from an empty repo. Fix: state "clear the receipt dir (as `tools/souji-wave-evidence-capture.sh:98` does) before the ignore decision" and add the stale-destination case.
- **A5 — accounting vs capture.** Only 4 `.pyc` are excluded once nested rules are neutralised (measured over 1383 files), so the r26 target is met by accounting, not by capturing everything; the frozen counter never reads `excluded.tsv`. Fix (stricter-only, no predicate change): require a `summary.tsv` count line `excluded=<n> renames=<n> symlinks=<n>` so the exclusion set is reviewable at the landing commit.
- **A6 — self-test as the only test of C1's fixture control.** Fix: `ReDeriveC1` (or the L1) runs the delivered fixture with an always-zero emitter and records the non-zero exit.
- **A7 — rehearsal-green ≠ landed-bytes.** `C3RehearseAdmit` proves the toolchain against entries it wrote itself, and snapshots at `{W}/sources/` while the entries point at `census/round-29/sources/`; if the L1 lands the scribes' entries without re-running `souji-gate-check.py`/`souji-coverage-agreement.py`/the C1 counter at that commit, the reported green is false provenance. Fix: state that the rehearsal is toolchain-only, and that the three counters are re-run on the landing commit.
- **A8 — id-mapping drift.** Frozen prose lists sources in the order (statx, link, cmp, Broder) while the items bind S217=Broder, S218=link, S219=cmp. No amendment (the prereg fixes ids, not an order); the L1 records the mapping once and `LessonGateF3` uses it.
- **A9 — permission wording.** `C1Corrections` says "append at the tail of each file" with no "do not edit the lane"; the shared context forbids it, but the per-item text is the one a seat reads last.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmCritic52.md` (this report; the item's required table and corrections are inside it — no separate delivery file was named).
