# Round 15 — ReportContract (w1 seat, design-only)

Seat: `SoujiR15.ReportContract` (scribe). Axes judged: operability, calibration.
Mode: source inspection only. No tests, builds, linters, probes, edits outside this report, or commits. Tool installs: none.
Label: **design-only**. The round-15 implementation has not landed (see §1). Every requirement below is a proposed obligation for the round-15 closure report, not an observed result.

## 0. Summary

- The closure report must keep the round-14 closure shape: six `##` sections in order (§3), a Step-1 conformance block, the source census before/after (§4), the operator path proof (§5), and per-axis verdicts with routed defects.
- The round-14 routed defects 1–5 (`corpus/lessons/round-14-verifier-spotcheck.md:160`) are the required inputs. None may be dropped silently.
- The operator path `census/operator-sweep-20261019/` stays untouched (§5). This seat's own search touched it once; disclosed in §9.
- No lane source contains the phrase "stale-lane clause". §6 is a proposed clause built from existing rules. L1 must adopt or reject it explicitly.
- Material findings are in §8. They are sent to `SoujiR15`.

## 1. Observed lane state (read-only at observation)

Commands: `git --no-optional-locks -C <lane> rev-parse HEAD`, `log -3`, `status --porcelain`, `rev-list --count '@{u}..HEAD'`, `diff --cached --name-only`; `ls`; file reads.

- HEAD `cc2168325768d5356a82c039dcdf787377c55784`. This equals the round-15 baseline in `census/round-15/claims.json`. Ahead count `0`. Nothing staged.
- HEAD commit `cc21683` is authored by `protocol-shokunin <protocol@shokunin.local>`, not `souji-shokunin`. Its subject is the round-14 verifier spot-check. Prior round commits `69c1604`, `42d0b7b` are `souji-shokunin`.
- Untracked at observation:
  - `.ufo/waves/round-15/` (spec, dispatch, assignments, registry)
  - `census/operator-sweep-20261019/` (operator-authored, protected)
  - `census/round-15/` (`claims.json`; sibling-written `before.json`; in-flight `lesson-draft.md`)
  - `corpus/lessons/round-15.md` (17-line stub: `## Mistakes` at :5, `## Gate` at :13)
- `census/operator-sweep-20261018/` also exists. Round-14's wave contract named it protected. Not inspected.
- Not present yet (design-only status):
  - `tools/souji-preservation-evidence.py`
  - `tests/fixtures/r15-census-config.py`
  - `tests/fixtures/r15-preservation-evidence.py`
  - `census/round-15/run-verification.py`
  - `census/round-15/count-claims.py`
- Current gate source is unchanged from baseline: `tools/souji-census.sh` `guard_git_config` at :493–522. Refusals at :504–507 (key-name substring match, value-blind) and :514 (`~` in `core.worktree`). Callers at :581, :613, :628, :650, :665. The status call at :711 already forces `-c core.hooksPath=/dev/null`.

## 2. Claims and axis map

| claim | axis (spec) | spec order | note |
|---|---|---|---|
| C1 | operability | first | Repair value-blind round-14 config refusals; keep namespace gains; keep benign and mixed-fleet rows. |
| C2 | calibration | second | Independent paired preservation-evidence checker. |

- `census/round-15/claims.json` is `{round, baseline, claims:[{id,axis,claim}]}` only. Round-14 `census/round-14/claims.json` also carried per-claim `counting_command`, `score_delta` and `limits` (`census/round-14/claims.json` C1/C2 blocks). SCORECARD requires a counting command per observation (`SCORECARD.md:3–6`). **Finding F1** (§8).
- Ordering decision for L1: the round-14 dispatch uses a lowest-axis rule, and calibration is lowest at 7 (`SCORECARD.md` calibration row). The round-15 spec puts operability first on the basis of round-14 routed defect 1, "admission-blocking operational trade" (`corpus/lessons/round-14-verifier-spotcheck.md:160`). The closure must state this basis explicitly. **Finding F6** (§8).

## 3. Report section and checklist obligations

Round-14 closure section order, verified by heading grep (`corpus/lessons/round-14-verifier-spotcheck.md`):

1. `## Decision` (:5)
2. `## Step-1 conformance` (:11)
3. `## Independent measurements over committed bytes` (:44), with `### C1` and `### C2` subsections
4. `## Discernment spot-check and source reopening` (:108)
5. `## Per-axis and trend verdicts` (:143)
6. `## Routed defects and review adjudication` (:158)

The round-14 closure calls these "the six required sections in order". The canonical template text is not in lane source, so this list is the observed precedent [to-verify against any template the operator supplies].

Checklist. Each item must be answered yes with the exact command and output, or marked `unrun`:

- [ ] **Decision:** status, `admitted` true/false, verdict per claim, reviewed-before and reviewed-after hashes (`cc21683…` through the closing HEAD). State the C1-first ordering basis (§2).
- [ ] **Step-1:** `rev-parse --show-toplevel`; `rev-parse HEAD`; `status --porcelain`; `rev-list --count '@{u}..HEAD'`; path-scoped `log` of the report file; the operator-sweep status line verbatim.
- [ ] **Independent measurements:** committed bytes via `git show <rev>:<path>`, not working-tree reads. Before/after table with the counting command for C1 and C2, exit code, and measured revision.
- [ ] **C1 red/green (benign):** a benign local-config control (for example a harmless `core.hooksPath=/dev/null` in the repo's own config) on the baseline tool fails, and the repaired tool passes with the same fixture bytes.
- [ ] **C1 mixed fleet:** a repository with the benign config and an unaffected sibling in one run. The unaffected row must appear in the repaired output (round-14 routed defect 1; Q22).
- [ ] **C1 namespace retention:** the round-14 twelve-case credential-namespace set still passes on the repaired tool (round-14 baseline 2/12 → 12/12, `corpus/lessons/round-14.md`).
- [ ] **C2 checker:** the independent checker is run on declared paired evidence with four negatives: green-only, weakened control, missing baseline arm, mismatched fixture digest. Each must exit non-zero with a named finding. Its verdict must be able to fail independently of the C1 repair (ClaimSeparation).
- [ ] **Discernment and outside sampling:** the round-14 disagreement is carried verbatim (`corpus/lessons/round-14-verifier-spotcheck.md:117` C2 row; `:148` operability `harmed`). Disagreements are never resolved by majority. The re-deriving seat is named (Q5).
- [ ] **Per-axis verdicts:** calibration, operability, coverage, depth, freshness, adjacency, in the round-14 table shape. Numeric deltas stated; no score inflation from fixture or source counts.
- [ ] **Routed defects:** round-14 items 1–5 (`corpus/lessons/round-14-verifier-spotcheck.md:160–…`), each with a current-round response or an explicit `not addressed`.
- [ ] **SHONEN:** the four lines `SHONEN.md:5,7,9,11` stay `[~]`. The author writes no `[x]`. Any `[x]` requires a non-author verifier named in the closure.
- [ ] **Commits (Q7):** `rev-parse --show-toplevel` first; named pathspecs only (`commit -- <paths>`); `-c maintenance.auto=false`; identity `souji-shokunin <souji@shokunin.local>`.
- [ ] **Bookkeeping (Q10):** `SCORECARD.md:48` `## Planned` must name `r16` (currently `:66` reads `r15 (planned r14)`). The certification note at `SCORECARD.md:97` must name round 15 (currently "Current r14 state"). Prose numbers must match table rows.
- [ ] **SKILL gate registry (`SKILL.md:118`):** new rows for any new tool or fixture, with name, kind, entry command, verdict map, self-test command, pinned-value path, write scope and owner. Retained-evidence prose (`SKILL.md:182`) updated for C2 limits.
- [ ] **QUALITY:** Q22–Q24 are present at `corpus/QUALITY.md:56–58` at the final grep. They were not present at this seat's first read, which ended at Q21 (`:50`). Closure verifies each row cites a lesson and that no older row was rewritten in place (QUALITY header rule).
- [ ] **Lesson:** `corpus/lessons/round-15.md` must carry `## Mistakes` and `## Gate` with admitted and rejected candidates and the re-deriving seat. The stub's R15-M1..M3 line citations were not re-verified here (§9).
- [ ] **Hygiene (Q4, Q9, Q13):** all fixture scratch under `/var/tmp` only, never `/tmp`, `/dev/shm`, or a live path. `shellcheck -S warning` exit 0 on every changed shell file. No new root-level files; evidence under `census/round-15/`.
- [ ] **Unrun checks** are listed as `unrun`. Seat source inspection is not acceptance (Q24). L1 runs the named acceptance once, after all seats finish.

## 4. Source census inclusion

- Command (fleet-root script; outside lane, referenced, not read by this seat):
  `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
- Start: `census/round-15/before.json` (observed, sibling-written). `measured_commit` `cc21683…`; rows 40 (tiers A36/B3/C1; mined 23, queued 15, rejected 2); command exit 0; stdout:
  ```
  souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
  souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
  souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
  souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
  ```
  This seat did not re-run it.
- End: `census/round-15/end-sources.json` (to be written at closure). Required shape, mirroring `census/round-14/end-sources.json`: exact stdout, exit code, `SOURCES.md` SHA-256, measured revision.
- W04 lines are advisory correction-URL duplicates. They are copied verbatim and never hidden. A W04 is not a failed required exit condition.
- Any new source row (for example C2 Git-config sources, S041+ per the SourcesDraft seat) changes the counts. Counts are re-derived by `count-claims` at both revisions, never copied from prior output (round-13 lesson, `## Final measured gate decisions` region).

## 5. Inherited operator path — untouched

- `census/operator-sweep-20261019/` is operator-authored, untracked, and present since baseline. It is not opened, read, edited, moved, staged, copied, committed or deleted by any seat or by L1.
- `census/operator-sweep-20261018/` is also protected (named in the round-14 contract).
- It is excluded from every `git add` and commit pathspec. It is not round evidence.
- Closure proof: `git -C <lane> status --porcelain -- census/operator-sweep-20261019` still shows only `?? census/operator-sweep-20261019/`; `git -C <lane> diff --cached --name-only` is empty before every commit.
- Precedent: `corpus/lessons/round-13.md:73` ("The sole initial untracked path ... is OPERATOR-authored: not edited, moved, committed or deleted. L1 did not inspect its contents").
- This seat's own deviation is disclosed in §9.

## 6. Stale-lane clause (proposed; not present in lane source)

Grep for `stale-lane` / `stale lane` in lane source (excluding `census/operator-sweep-*` and `census/round-1/`) returned no governing clause. The clause below is proposed for the closure report. It is built from existing rules; it is not a finding.

1. An observation is current only at its own measured revision. A prior-round result is cited with that revision and is never relabelled as a new execution (round-14 closure item 5; Q20 principle).
2. A digest-bound claim is current only if the digest equals the installed bytes at the measured commit (Q6). Otherwise the claim is `stale` for that observation.
3. Lane bookkeeping that is stale at closing (SCORECARD `## Planned`, certification note, `corpus/README.md` Known gaps) is corrected in the closing commit (Q10; round-12 M52).
4. Mid-flight working-tree additions are not inherited into a round's evidence (`corpus/lessons/round-13.md:69–73`, `## Scope, wave and inherited state`).
5. Round-15 untracked files at baseline (`.ufo/waves/round-15/`, `census/round-15/`, `corpus/lessons/round-15.md`) are this round's own in-flight work. The closure states which were committed and which were left untracked.

L1 must adopt or reject each item explicitly in the closure Decision.

## 7. Acceptance needed (design-only, for L1)

- Closure report contains every §3 item with exact outputs; unrun checks are labelled `unrun`.
- Source census before and end files present, per §4.
- Operator path proof per §5.
- Stale-lane decision per §6 recorded.
- Round-14 routed items 1–5 each answered.
- C1 red/green benign and mixed-fleet controls, and C2 negative controls, each as a committed fixture with a named expected finding set and pinned bytes. Their observations come from L1's single acceptance run, not from seat source review.

## 8. Material findings (sent to SoujiR15)

- **F1** — `census/round-15/claims.json` lacks per-claim `counting_command`, `score_delta` and `limits` present in `census/round-14/claims.json`. Route: L1 / RoundRunner (owns `census/round-15/count-claims.py`).
- **F2** — `SCORECARD.md:66` still reads `r15 (planned r14)` and `:97` reads "Current r14 state". Q10 requires the closing commit to update both.
- **F3** — This seat's first broad search read files beneath `census/operator-sweep-20261019/` (see §9). Recorded as a process deviation; no use made of any content.
- **F4** — `corpus/lessons/round-15.md` and `census/round-15/lesson-draft.md` are in-flight sibling writes. Closure must reconcile them against the final Gate; they are not evidence.
- **F5** — Q22 requires the C1 fixture to show benign-control baseline failure and changed success, with mixed-fleet rows preserved. ConfigFixture's acceptance must match this exactly.
- **F6** — Ordering: C1 is operability by spec, while the lowest axis is calibration (7). L1 must record the basis in the Decision.
- **F7** — Round-14 closure located the lane report at fleet-root `.ufo/reports/round-14/souji.md` (`corpus/lessons/round-14-verifier-spotcheck.md:16` Step-1 log command). The round-15 equivalent is not named in lane source. Route: L1 to confirm the destination path before closure.

## 9. Process deviations, unrun checks and limits

- **Deviation (operator path), exact calls.** (a) Lane-root `_glob` over `.`, which listed operator-sweep filenames (names only). (b) `grep -n -i "stale\|Report:\|trailer\|census output\|operator-sweep\|inherit" -r --include=*.md --include=*.json --include=*.py --include=*.sh .` piped through `grep -v` filters. It recursed into `census/operator-sweep-20261019/` and read file contents; output lines from that path were filtered before display. (c) `ls census/` and `ls` of `census/round-*` directories during discovery (names only). Nothing was quoted, copied, edited, staged, or used. Later searches used `--exclude-dir=operator-sweep-20261019`. No further access after the IRC boundary reminder.
- **Unrun.** No test, build, linter, probe, fixture or sources-census run. The fleet-root census script is referenced, not executed or read.
- **Not re-verified.** The stub's R15-M1..M3 rows (`corpus/lessons/round-15.md:9–11`) and `corpus/lessons/round-14.md` process-deviation text were not re-derived here. Only the Q22–Q24 presence was checked.
- **External docs.** None opened; none required for this design-only report.

## 10. Tool installs

None. No tool was installed or upgraded. Git commands were read-only with `--no-optional-locks`.
