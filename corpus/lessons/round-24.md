# Round 24 — F2 write-safety census, coverage-map agreement, receipt verify/run symmetry

Author: SoujiR24 (lane identity `souji-shokunin <souji@shokunin.local>`). Lane base
`a65fac98964b445758e94c805728c9a19d302ff8`. Preregistration `.ufo/waves/round-24/preregistration.txt` (frozen at
`f9db2181647d91470a724a12d626bd6106805076`), plus the append-only `.ufo/waves/round-24/preregistration-amendment-1.txt` (landed in
`1efe406e7f39b8fe736be2a566053703a571ffc0`). Inbound: `corpus/lessons/round-23-verifier-spotcheck.md` (routed: map table vs prose for F2)
and SCORECARD `r24 — planned`. After-state `778747eb671f8e85ef5387bc3d7023337b30467c`; after-receipts
`ca7fc1cb6dd1333096c6f3bdbad304686691d126`.

## Claim and boundary

Three claims on three axes. Each has a do-nothing control receipt committed before the after-state
(`ce5971c9fe7a04f958f06c7b1933e07ffbc9ddd3`) and an after receipt at `778747e`. All nine round-24 receipts are `verify=ok` under the
landed runner. `census/round-24/records/slice-verdicts.tsv` is a gate table, not a receipt.

| claim | axis | before (control) | after | counter digest (control = after) |
|---|---|---|---|---|
| C1 F2 write-safety debris census | coverage (8) | fixture and tool absent at base (`git cat-file -e a65fac9:tests/fixtures/r24-size-census.py` rc 128). Stub control: `cases=8 pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` rc=1, no target line — `census/round-24/records/c1-control-stub.tsv` | `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` rc=0 — `census/round-24/records/c1-after.tsv` | fixture `373ef1f0…` |
| C2 coverage-map agreement | calibration (7) | `grounded=4 mapped=2 dangling=0 mismatches=2` rc=1 at `--rev a65fac98964b445758e94c805728c9a19d302ff8` (2 × `MISSING-FROM-MAP`: `count-objects-garbage-readings-r25.md`, `repo-size-census-readonly.md`) — `census/round-24/records/c2-control-base.tsv` | `grounded=6 mapped=6 dangling=0 mismatches=0` rc=0 — `census/round-24/records/c2-after.tsv`. Fixture `cases=9 pass=9 control=FALSE-GREEN-REJECTED` — `census/round-24/records/c2-fixture-after.tsv` | tool `71b89eb3…` |
| C3 receipt verify/run symmetry | operability (8) | `cases=8 pass=6 refusals=0/2 regress=5/5` rc=1, base runner bytes `e13d0c83…` — `census/round-24/records/c3-control-base-runner.tsv` | `cases=8 pass=8 refusals=2/2 regress=5/5` rc=0 — `census/round-24/records/c3-after.tsv` | fixture `f8c4c391…` |

Each counter's bytes are identical in its control and after receipts. Wave 2 re-derived all three
targets in `/var/tmp` clones at `ca7fc1c` (`W2C1Rerun`, `W2C2Rerun`, `W2C3Rerun`: survive).

**C1 detail** (all from `c1-after.tsv`):

- Case 3 reads `counts=1,2,0,0` on both the main and the linked arm (2048-byte junk).
- Case 4 reads `counts=0,0,0,0` with `raw_linked_garbage=1`, the witness read after the tool.
- Case 6 refuses three arms with exit 2.
- Case 7 reads `manifest_changed=4 lost_found_other_oid=True`.
- Case 8 kills the stub on `dangling,garbage,alternates`.

Lane-bound figure: `census/round-24/size-census-lane.txt` (rev `778747e…`, tool `09bb8e0d…`) prints
`garbage=0 size_garbage=0 unreachable=1093 alternates=0`. It is this repository at one moment: no
fleet figure. It is not a v1 receipt (`verify` → `RECEIPT-MALFORMED`; `W2C1LaneMeasure` F3). Its
line-1 attribution "(jj keep refs + cruft pack)" is falsified in part: at a re-run, U = 999 loose
trees, 31 loose blobs and 71 cruft-pack blobs, with an explained drift of +8 (`W2C1LaneMeasure` F1, F4).

**C2 detail.** The amended per-entry kill rule holds: 4/4 entries grounded at base are present at the
tip with the same F<k> (E4; `W2C2Rerun`). The `grounded` count goes from 4 to 6. That is one new entry
plus `git-repo-structure-readonly.md`, re-grounded from body prose to a header `ground: F2` line: a
format change, not new coverage (`W2C2Rerun` F2, `W2Trend` F2). In files, F2 goes from 3 entries to 4.

**C3 detail** (from `c3-after.tsv`):

- Case a refuses a commit on no ref and a commit held only by `refs/jj/keep/r24-fixture` (`RECEIPT-REV-NOT-DURABLE`).
- Case b refuses an absent path and a substring-only path (`RECEIPT-TOOL-NOT-IN-ARGV`).
- The five r23 receipts still verify.

**Also landed.** Gate `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0` (`census/round-24/records/gate-check-r24-entry.tsv`).
`git-repo-structure-readonly.md`'s unchanged recheck printed `selftest=PASS ids=5/5` on git 2.56.0
(`census/round-24/records/r13-recheck-receipt.tsv`; `W2Reverify` reproduced it: survives).

**Boundary — C1.**

- 8/8 is not a proven no-write envelope. An mtime-restoring write is invisible because ctime is excluded (amendment-1 limit). Only cases 1–6 compare a manifest; case 7 is the detector (`W2ReadmeRow` F3).
- The counter is blind to the after-state's 65-line tool delta (allowlisted env, hooks off, 900 s timeout, top-level `--repo`). The `1efe406` tool already scores 8/8 (`W2C1Rerun` F3, `W2Separable` F4).
- The fixture kills 4 of 11 tool-clause mutants (`uncovered=7`, `W2C1MutTool`). Unpinned: unreachable vs dangling semantics, the env allowlist, top-level refusal, stderr-is-failure, the alternates source, the timeout.
- The after-state tool refuses every bare repository with exit 2 "not a repository". This is a regression against `1efe406` and against the frozen CLI, and the fixture is blind to it (`W2C1TopLevel` F1, F3).
- Case 6's partialClone arm uses a `--filter=blob:none` clone, which on git 2.56.0 carries no `extensions.partialClone`. A tool that ignores that key scores 8/8 (`W2C1Amend` F2). The landed tool still refuses it.
- Case 4 creates linked worktrees in one DWIM mode (`tests/fixtures/r24-size-census.py:169,184`), so it is not a committed witness for any of the five admitted creation modes (`W2Rejects` F14).
- 4 of the 8 cases re-score rules held at base or do not depend on the tool, so they are quality and operability content, not coverage (`W2C1Axis` F3).
- The envelope survived every exec and write vector tried (`W2C1Envelope`).

**Boundary — C2.**

- C2 certifies entries cells only, over 6 grounded of 13 `.md` entries at the tip. `corpus/README.md:40` still reads "frontier, no entry" (E13). It is superseded for the entries column at :504-ff.
- README :532 "counts any recurrence as a mismatch" is false: the tool never reads status prose (`W2ReadmeRow` F1).
- The per-entry kill rule is enforced by hand only (`W2C2Rerun` F3).
- Two fixture mutants survive without changing lane numbers (`W2C2Mut`).
- The calibration-axis reading survives narrowly: the counter reads the index column, not the status column where the map's self-assessment lives (`W2C2Calib`).
- At the scored rev `778747e`, README :516 names `census/round-24/size-census-lane.txt`, which first exists at `ca7fc1c` (`W2C2Game` F4, `W2ReadmeRow` F2).

**Boundary — C3.**

- C3 binds the `tool=` label to the recorded argv text, not to the executed program (amendment-1 limit; `RevR23Residuals` A1).
- C3 takes 2 of 20 enumerated r23 residuals.
- The fixtures kill 4 of 13 clause mutants (`uncovered=9`, `W2C3Mut`). The amendment's verify-side symmetry clauses (`COMMAND-REFUSED`, `RECEIPT-MALFORMED`, `TOOL-PATH-REDACTED`) have no counter case (`W2C1Amend` F7).
- **The title "verify/run symmetry" is falsified.** The counter target is still met. On receipts
  `run` wrote with exit 0, `verify` refuses 19 of 36 argv shapes. One newline shape forges the header:
  `run` recorded rc=3 with no counts, yet `verify=ok` on a header reading rc=0 and `cases=9 pass=9`.
  Case c tests one clean shape only (`W2C3Symmetry` F1–F4, F7). Report C3 as "two named r23
  residuals closed (`refusals=2/2`)", never as symmetry.
- **Harm outside the frozen cases** (the frozen kill rule is not triggered):
  - the per-element redaction leaks bearer tokens the base redacted (`W2C3Redact` F1, HIGH);
  - tip `run` writes `--token=`/`password=` receipts that tip `verify` refuses (`W2C3Rerun` F1, HIGH);
  - `verify` accepts a counts line found only in stderr, or as a decoy (`W2C3CountsRE` F1–F2).

  `run --out` is a deny-list that can truncate HARD-BOUND paths (`W2Scope` F1, pre-existing, in a file r24 modified).

**Boundary — all claims.** No fleet figure, no deletion authority, no history rewrite, no credentials,
no live `/proc` census, no operator-sweep contents. Certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged.

## Process deviations

1. **Control receipts were not committed at freeze.** The freeze `f9db218` (06:14:49) holds none
   (`CritPrereg` F12). The controls ran at 09:29:39–41Z and were committed in `ce5971c` (06:29:45),
   before `778747e` (06:33:39) and before the after receipts (09:34:44Z onward). This is a deviation, not
   compliance. The frozen remedy says "before any after-data", and the amendment rewrote it as "before
   any after-receipt", which is weaker (`W2C1Amend` F1). After-data did exist earlier (deviation 2).
2. **Pre-control after-data.** Amendment-1 discloses L1 runs of the C2 tool at base (`mismatches=2`)
   and the C3 fixture (base runner 6/8; patched runner 8/8 `refusals=2/2`) as "not claim evidence".
   The "patched runner" was the landing bytes `9df0738c…` (`ExecReceiptFixture.md:81`), so `c3-after.tsv`
   reproduces a result observed before the controls. Its target line was pinned after that observation
   (`W2C1Amend` F3). A C1 run of the L1-integrated lane tool printed the 8/8 target line at
   06:28:39, before the amendment commit and the stub control, and it is not disclosed
   (`ExecSizeCensusFixture.md:39`; `W2C1Amend` F4). The prereg's "a counter edit after any seat
   scored is a deviation reported as such" applies: wave-1 seats scored drafts and mocks before the
   amendment re-specified cases 3–6 (`W2C1Amend` F5, a stricter-direction breach).
3. **Amendment-1 "every change stricter" is false for two bullets.** These are the control-timing
   remedy (deviation 1) and the `COUNTS_RE` widening, which is a loosening that every r24 receipt
   needs (`W2C1Amend` F6). The other changes are stricter and survive case by case (`W2C1Amend` F8–F10):
   - C1: a common-dir manifest with `st_mtime_ns`; case 3 at 2048 B plus a linked arm; manifests in cases 4–5; the witness read after the tool; GIT_* stripped; git ≥ 2.46.0.
   - C2: a set-based kill rule; a backticked entries-cell mapping; fixture 9/9 as a verdict condition.
   - C3: a pinned line; two case-a instances; `run` refuses TOOL-NOT-IN-ARGV and TOOL-PATH-REDACTED.
4. **The controls could not verify at their own commit.** The runner at `ce5971c` equals the base
   runner, which refuses all three controls with `RECEIPT-COUNTS-ABSENT`. They verify only since
   `778747e` landed the `COUNTS_RE` widening (`W2Separable` F2). Eight of the nine r24 receipts depend on
   that widening (`W2Separable` F1).
5. **The instruments commit carries the freeze's author time.** `1efe406` has author date 06:14:49,
   the same as `f9db218`, and committer date 06:29:29 (E11).
6. **Controls are bound to the instruments revision.** All three carry `rev=1efe406…`. C2 reads
   `--rev a65fac9…`, and the C3 runner bytes at `1efe406` equal the `a65fac9` blob `e13d0c83…` (E9).
7. **The after-state is not self-contained.** At `778747e` the entry cites `.ufo/waves/round-24/w1/{ProbeLinkedModes,
   ProbeGarbageKinds,ScoutPkgEntries}.md` and `census/round-24/records/c1-after.tsv`, and README cites
   `size-census-lane.txt`. None of these exists until `ca7fc1c` or `c3ca7ad` (`W2Trend` F15,
   `W2Rejects` F15, `W2EntryGate` F5). The gate checker does not resolve them.
8. **The r13 recheck exists twice.** The `.out` in `778747e` (`…petQHu`, mtime 06:22) and the receipt in
   `ca7fc1c` (`…wUrYU8`) are two executions. Only the receipt is bound (`W2Reverify` F3).
9. **The tip moved past the receipts.** `c3ca7ad` adds only wave-1 reports and changes no measured
   bytes (`W2C2Rerun` F1). `d3666c3` commits the inherited late round-23 seat updates (`W2K1.md`,
   `W2D3.md`) under `.ufo/waves/round-23/w2/`; neither touches the corpus, census, tools or receipts.
10. **Uncommitted at draft time.**
    - `corpus/QUALITY.md` (Q56) and `.ufo/waves/round-24/make-spec.py`.
    - Wave-1 seat scratch left in `/var/tmp` (R24-M14).
    - The inherited `.ufo/waves/round-23/w2/W2K1.md` and `W2D3.md` (06:08:37 and 06:09:40, after
      round 23's `complete`) are now committed at `d3666c3` ("inherited late round-23 seat updates …
      verbatim, superseding the 2f96bf4 text; not round-24 claim evidence") — the separate labelled
      commit `W2Inherited` asked for. They remain not round-24 claim evidence.

## Mistakes

Witness legend: **SHOWN** means executed and failing on the defect, with the runner named; **NONE**
means no executable witness exists. Line numbers are at `c3ca7ad`; `d3666c3` touches only
`.ufo/waves/round-23/w2/`, so the corpus/census/tools line numbers are unchanged.

| id | class | evidence | captured-by | fix | failure witness |
|---|---|---|---|---|---|
| R24-M1 | calibration — coverage-map entries column not updated while its status prose was | `corpus/lessons/round-23-verifier-spotcheck.md:41` "reconcile the current map table with its own “read side now holds three” prose"; `corpus/README.md:68` | none (Q10 SCORECARD-only; Q31 path existence) | C2 tool + fixture; r24 F2 row; Q56 | **SHOWN**: `mismatches=2` (`c2-control-base.tsv`) → `0` (`c2-after.tsv`). |
| R24-M2 | calibration — a superseded map row reads as current | `corpus/README.md:40` status "frontier, no entry", entries `—` (E13) | none (C2 reads entries cells only) | append-only "superseded by :504" on the :40 status | **NONE**. C2 is green with :40 unchanged. |
| R24-M3 | calibration — a multi-site correction claimed but not swept | `corpus/lessons/round-23.md:171-172` "12/12" vs `corpus/README.md:468` "eight of its nine", `LOG.md:1583-1584` "ten of its eleven", `round-23.md:23` and `SCORECARD.md:21` "11/11" | none | correct in place; append `superseded by` in LOG | **NONE**. Unchanged at c3ca7ad. |
| R24-M4 | calibration — a filed receipt rewritten in place | `git diff 4765250 c0eeaa7 -- census/round-23/records/agreement-control-base.txt` (`tool_sha256=` → `tool-digest=`) | Q55 append-only clause, no check | disclosed here; `superseded by` note | **NONE**. |
| R24-M5 | operability — `verify` accepted a non-durable rev | `corpus/lessons/round-23.md:159-160` | Q37, write side only | C3 case a | **SHOWN**: case a FAIL in `c3-control-base-runner.tsv` → PASS in `c3-after.tsv`. |
| R24-M6 | operability — `tool=` not bound to argv | `corpus/lessons/round-23.md:160` | Q6/Q55 bind bytes only | C3 case b | **SHOWN**: case b FAIL → PASS (same receipts). Binds recorded text only. |
| R24-M7 | calibration — Q55 cannot see a quoted value disagreeing with its receipt | `.ufo/waves/round-23/w2/W2Q55.md:259-281` | Q55 in name only | open: a value clause in Q55 | **NONE**. |
| R24-M8 | calibration — the documented command does not reproduce its cell | `corpus/README.md:456` lacks `--no-worktree`; `SCORECARD.md:21` has it | none | add `--no-worktree` | **NONE**. Open. |
| R24-M9 | discernment — a corrected reject reason is false of the repo | `corpus/lessons/round-22.md:478-479` "no staging tool exists"; `tools/souji-quarantine.sh:569,595` | none (Q1/Q2 quote-only) | append-only correction | **SHOWN as defect** (ScribeLessonMistakes E6); not fixed. |
| R24-M10 | calibration — r23 Mistakes clauses falsified by wave 2 and left open | `corpus/lessons/round-23.md:64`, `:68` against `.ufo/waves/round-23/w2/W2Lesson.md:62-72`, `:86-90` | Q25(c) carries `STATUS:` lines only | append-only corrections | **NONE**. |
| R24-M11 | scope — a fixture's run flipped its counter (R23-M8 recurrence) | `.ufo/waves/round-23/w2/W2Scorecard.md:154-171` | R23-M8 | repaired in r23 (`sys.dont_write_bytecode`) | **SHOWN by r23** K4 row; `W2Scope`: no new `__pycache__` in a65fac9..ca7fc1c. |
| R24-M12 | calibration — the r23 lesson says last-wins closed shadowing; a post-fence counts line still shadows stdout | `corpus/lessons/round-23.md:144-146` (E15); `tools/souji-record-agreement.py:117-119` docstring vs :121/:126; `STDOUT_FENCE` :70 unused; tool `dd53c228…` unchanged a65fac9→c3ca7ad (E9) | none: the r23 fixture's synthetic receipts have no fences; reverting last-wins or deleting `receipt-rev-object` keeps it 12/12 (`W2R23F4` F4) | anchor `counts_of` to the stdout section of fenced receipts (`W2R23F4` F5 diff); three fixture variants; append-only correction of `round-23.md:144-147` citing the inherited W2K1 commit | **SHOWN** by `ScoutInherited` E6 at a65fac9 (`mismatches=7` + trailing line → `mismatches=0` rc=0) and by `W2R23F4` at ca7fc1c. Three false passes: post-fence line, stderr-only counts, and one untampered `run` receipt. No committed figure is wrong (0 of 17 fenced receipts carry counts outside stdout). |
| R24-M13 | operability — `run` prints the first counts match; `verify` scans both fences | `tools/souji-receipt-run.py:251-253` `COUNTS_RE.search(proc.stdout)`; `:294` presence check over `_body` (stdout + stderr) | none | one shared helper: last non-empty stdout line, anchored, the stdout slice ending at the stderr fence (`W2C3CountsRE` F6) | **SHOWN** by this seat (E6: c2-fixture-after first match = case 1's `grounded=2 mapped=2 dangling=0 mismatches=0`; first ≠ last in 5/9) and by `W2C3CountsRE` (stderr-only line verifies). No record misled (E7). |
| R24-M14 | scope — a seat report claims scratch removal that did not happen | `.ufo/waves/round-24/w1/ScribeEntry.md:6`; `/var/tmp/souji-r24-ScribeEntry3/` not disclosed (`W2Misroot` F2–F3) | none | the L1 removes the leftovers; append-only report correction | **SHOWN** by this seat (E10). |
| R24-M15 | scope — `run --out` is a deny-list, so it can truncate HARD-BOUND paths | `tools/souji-receipt-run.py:165-180` (`W2Scope` F1) | none | allow-list `--out` under `/var/tmp/` | **SHOWN by W2Scope** (mirrored tree). |
| R24-M16 | operability/security — the C3 per-element redaction regressed | `tools/souji-receipt-run.py:242`: `[REDACTED]` brackets make `shlex.join` quote the element, and the joined-line `authorization:\s*bearer\s+` no longer matches (`W2C3Redact` F1) | none: no fixture argv holds a secret shape (`W2C3Mut` F4) | drop the joined-line pass; refuse a secret span that crosses argv elements (`W2C3Redact` remediation) | **SHOWN by W2C3Redact**: 4 hand-built argv; 256 and 227 tip-only leaks per 200k fuzz cases; 3 leaking receipts pass `verify`. |
| R24-M17 | discernment — Gate reject reasons false of the repo (R23-M6/R24-M9 class) | entry Gate provenance REJECT "this lane's ids for those numbers name other documents": the lane has no S130–S153 (`W2Rejects` F13, `W2EntryGate` F2). r23 REJECT "S131 is quarantined payload-absent" vs `slice-verdicts.tsv` "S131 accepted" (`W2Rejects` F8, `W2EntryGate` F4). The provenance flip is already met (`W2EntryGate` F3) | none: the gate tool checks quotes, not reasons; three refs ADMIT quotes are checked only on fragments split by the embedded `"` (`W2EntryGate` F1) | append-only Gate corrections | **SHOWN by W2Rejects / W2EntryGate** (`rg` over SOURCES rc=1). Each reject still stands on another true reason. |
| R24-M18 | calibration — evidence cited as committed is absent at the measured revision (Q17) | deviation 7 | Q17 has no executing check in the gate (`gate-check-r24-entry.tsv` is green) | land the cited evidence with, or before, the citing commit | **SHOWN by W2EntryGate / W2Rejects** (`git ls-tree` at 778747e). |
| R24-M19 | calibration — a committed witness cited for more than it runs | entry Gate: r25 five-mode matrix "with C1 case 4 as the committed witness"; case 4 runs one DWIM mode, none of the five (E14; `W2Rejects` F14) | none | restate: case 4 witnesses DWIM add; the five modes are seat-measured (`W2EntryClaims` reproduced all five reading 1) | **SHOWN** (E14). |
| R24-M20 | calibration — the admitted entry overstates its mechanism | entry :26-27 "the git that created the worktree does not change the count" — a 2.30.0-created worktree reads 0 under the 2.56.0 reader (`W2EntryClaims` F1). Also: item 7 omits the `GIT_COMMON_DIR`-unset precondition (`git --git-dir=<common>` read `garbage: 6` with it exported; `W2SrcPath` F2); line 2 label (`W2SrcPath` F1); "twelve planted kinds" names 11 (`W2EntryClaims` F4); S123 cited for § DETAILS outside its § REFS anchor (`W2SrcCountWt` F3, `W2Registry` F5) | none | append-only entry corrections before landing | **SHOWN by W2EntryClaims / W2SrcPath** (git 2.56.0 and 2.30.0 probes). |
| R24-M21 | calibration — an admitted entry narrowed by r24 and left unmarked | `repo-size-census-readonly.md:15-20` "unrecognised files, so a size census that ignores them under-reports disk use"; r24's entry shows a healthy linked worktree counts private-gitdir structure, which the census correctly reads past (`W2Trend` F6). `git-repo-structure-readonly.md:2` `verified-at:` still names 2.55.0 (`W2Reverify` F1) | none | dated r24 note under claim 1; refresh `verified-at:` with the 2.56.0 receipt | **NONE** (a marking defect). LEARNING `harmed` trigger while unmarked. |
| R24-M22 | calibration — two slice-verdict tables disagree (R23-M4 recurrence) | `census/round-24/records/slice-verdicts.tsv` vs `.ufo/waves/round-24/assimilation/slice-verdicts.tsv`: 7 of 8 rows differ, with no mapping; S118 `unverifiable` vs its own evidence cell and its scout's `present`; S126 and S138 `present`→`accepted` unexplained (`W2Slice` F1–F4) | none: `souji-gate-check.py` tests class membership only, so swapping every class stays green (`W2Slice` F5) | one table, or a documented mapping; S118 re-classed or reason stated | **SHOWN by W2Slice** (class-swap stays rc 0). |
| R24-M23 | calibration — registry `used-by` not swept | S115 omits the citing entry (E3; `W2Registry` F1); S120 and S122 list a tool path, outside CORPUS L107's definition (`W2Registry` F2) | `validate` checks that paths exist, not completeness | apply S115 old→new; decide the tool-path convention | **SHOWN** by this seat (E3). |
| R24-M24 | coverage — a tool regression invisible to the frozen fixture | `tools/souji-size-census.py:131-146`: `--show-toplevel` in the same `rev-parse` exits 128 for bare repos (`W2C1TopLevel` F1) | none: no bare, subdir or enclosing case (`W2C1TopLevel` F3) | split the `rev-parse`; disclose the exit-2 widening (F7) | **SHOWN by W2C1TopLevel**; deleting the refusal also scores 8/8. |
| R24-M25 | calibration — a claim title asserts more than its counter can witness | prereg :95 "Receipt verify/run symmetry"; amendment-1 :39 "Symmetry made literal". `CritPrereg` F8 warned pre-data ("retitle to 'two named r23 residuals'"). The title was kept, and `verify` refuses 19 of 36 `run`-written shapes, with one header forge (`W2C3Symmetry` F1–F4) | none: case c checks one clean `run → verify` shape (`W2C3Symmetry` F7) | report C3 as two residuals closed. The forge and quote-eating fixes go in a later round as preregistered cases, not as a post-scoring counter edit | **SHOWN by W2C3Symmetry** (36-shape matrix; `cases=8 pass=8` unchanged). |

## Gate

### Opened sources (2026-10-25)

Quotes are copied from the committed snapshots under `census/round-24/sources/`
(`sha256sum -c SHA256SUMS` 6/6 OK, E5). The live raw files equal the snapshots: `W2SrcPath` E2–E3
(path.c, both tags) and `W2SrcCountWt` F1–F2 (count-objects.c, git-worktree).

- **S120 mined** — https://github.com/git/git/blob/v2.56.0/path.c (tag commit `a018953688f1b10bddf91bff8747068f5f4746a4`), snapshot `census/round-24/sources/git-v2.56.0-path.c` `f98ba344…21d2`. Line 90: "Not considered garbage for report_linked_checkout_garbage". Line 111: `{ 0, 1, 1, "refs" },`.
- **S121 mined** — https://github.com/git/git/blob/v2.30.0/path.c (tag commit `71ca53e8125e36efbda17293c50027d31681a41f`), snapshot `census/round-24/sources/git-v2.30.0-path.c` `7c5b0710…2d4a`. Line 102: "Not considered garbage for report_linked_checkout_garbage". Line 123: `{ 0, 1, 1, "refs" },`.
- **S122 mined** — https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c, snapshot `census/round-24/sources/git-v2.56.0-builtin-count-objects.c` `ec13ae40…e03e`. Line 118: "report_linked_checkout_garbage(the_repository);". Line 152: "(unsigned long)(size_garbage / 1024));".
- **S123 mined** — https://git-scm.com/docs/git-worktree § REFS, installed man page git 2.56.0-1, snapshot `census/round-24/sources/git-worktree.1.txt` `624821a6…b51a`. Line 140: "There are exceptions, however: refs inside refs/bisect, refs/worktree and refs/rewritten are not shared." Bound: the teaches cell holds on the files ref backend only (`W2SrcCountWt` F5). § DETAILS is anchored by S003, not S123 (R24-M20).
- **S115 re-cited** (row unchanged) — https://git-scm.com/docs/git-count-objects § OPTIONS, snapshot `census/round-24/sources/git-count-objects.1.txt` line 28: "garbage: the number of files in the object database that are neither valid loose objects nor valid packs".

Registry `119 → 123` rows (E2). `validate` exits 0 with no E lines (`W2Registry`).

**In-place change to log: S115 `used-by`.** Old `corpus/knowledge/repo-size-census-readonly.md` → new
`corpus/knowledge/repo-size-census-readonly.md, corpus/knowledge/count-objects-linked-worktree-garbage.md`. **Not applied at `c3ca7ad`**
(E3). It is a landing precondition (R24-M23).

### Id collisions and renumbering

Pre-append (prereg :130, frozen): reg-ids 119, staged-ids 134, collisions 11, all different documents
(`ScoutCollisionMap` F1). Post-append: reg-ids 123, staged-ids 134, collisions 15. Lane S120–S123
collide with staged S120–S123, and all four pairs name different documents (`W2Collisions` F1, F5).
By-document map:

| staged | lane | document |
|---|---|---|
| S153 | S120 | path.c@v2.56.0 |
| S153 | S121 | path.c@v2.30.0 |
| — | S122 | builtin/count-objects.c@v2.56.0 |
| — (staged S230 is a different URL) | S123 | git-worktree § REFS |

Hazard: the bare "S123" in `corpus/lessons/round-22.md` L298, L351, L363 and
`round-22-verifier-spotcheck.md` L199 means the staged own-work row (`W2Collisions` F6). It needs a
disambiguation note. The staged 134-id list is pinned by the committed `staged-ids` file, not by a
shokuknow commit (`W2Collisions` F7).

### Assimilation decisions (entry `corpus/knowledge/count-objects-linked-worktree-garbage.md` `## Gate`)

- **ADMIT** — staged `garbage-false-positive-modes-r27`, re-sourced to S120–S123. Its quotes are byte-exact (`W2SrcPath` A5, `W2Trend` F12). Its "reader-decides" wording is overstated (R24-M20).
- **ADMIT** — staged `garbage-false-positive-modes-r25`, five-mode matrix as lane-measured. Content survives: all five modes read 1 (`W2EntryClaims`). Provenance is falsified: case 4 runs none of the five modes, and the cited seat report was absent at `778747e` (`W2Rejects` D; R24-M18, M19).
- **REJECT** — r25 headline (no second trigger) and its directory-size reason. The locator should be staged lines 48-50, not 1-30 (`W2EntryGate` F6).
- **REJECT** — staged `garbage-false-positive-modes-r26`. All four reasons are true of the staged bytes (`W2Rejects` A1–A4).
- **REJECT** — staged `count-objects-garbage-semantics-r23`. It stands on fleet claims, the id collision, "only two fields" and directory size (`W2Rejects` F7, F9–F11). The "S131 payload-absent" reason is stale (R24-M17).
- **REJECT** — staged provenance cells (S130 S131 S134 S141 S147 S153). Its first clause is true; "lane ids name other documents" is false (R24-M17).

2 admitted, 3 entries rejected, plus the provenance cells. That is within "At most 2 admitted, at least
1 rejected". Gate receipt `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0` (`gate-check-r24-entry.tsv`).
It does not check reasons, line numbers, or the classes of slice verdicts (R24-M17, M22).

### Quarantine-slice verdicts (`census/round-24/records/slice-verdicts.tsv`; campaign register ids)

| id | gate verdict | basis (gate cell, abridged) | wave-2 note |
|---|---|---|---|
| S114 | accepted | git-prune sentence present; `[1]` vs `(1)` | survives |
| S118 | unverifiable | DOI → IEEE 202, 0 bytes, twice; quote in IEEE staging + PDF mirror; venue cell wrong | contradicts its own cell; `accepted` under r22 definitions (`W2Slice` F1) |
| S123 | accepted | shokuknow output `510722c1` matches; not lane-re-derivable | cell supports digest, not quote class (`W2Slice` F3) |
| S124 | accepted | output `1634d206`, probe `11df88f1`; quote drops `NOREPLACE_new=0(ok)` | maps without contradiction |
| S126 | accepted | gtk quote verbatim; register quote truncated at 120 | r22 and the detail table say `present` (`W2Slice` F4) |
| S131 | accepted | census `1ac71c4f` matches; fleet census, never appended | as S123 |
| S133 | accepted | `a53f1e30`, `a4506492` match; 8 mounts, 7 paths | as S123 |
| S138 | accepted | qiita markdown line 17 | as S126 |

Tally: 7 accepted, 1 unverifiable, 0 rejected (`slice_verdicts=8 slice_total=8`). These are not lane
admits or rejects, and they are excluded from the discernment sample (`W2Trend` F13).

### Rejected scope

- No claim that a receipt authenticates execution.
- No fleet figure.
- No claim that C1's 8/8 proves a no-write envelope or covers the after-state hardening.
- No claim that C2 covers ungrounded entries or status cells.
- No claim that C3 closes r23 residuals beyond R1 and R2, or that C3 left `run` and `verify` symmetric outside the frozen cases.
- No `F2-wt` row minted after data (`W2Trend` A2).
- No F2 promotion to core.

## Q56 (proposal text)

The uncommitted draft in `corpus/QUALITY.md` matches this text in substance. This version pins the two
definitions wave 2 found unpinned (`W2C2Mut` M4, M3b). **Land it only in the same commit as this
lesson** (Finding 5).

| id | criterion | applies to | check | motivating evidence |
|---|---|---|---|---|
| Q56 | Declared coverage equals entry files. Every `corpus/knowledge/*.md` entry whose front matter (the lines before its first `#` heading) carries `ground: F<k>` is named, as a backticked `knowledge/<file>` path, in the entries column of a `corpus/README.md` coverage-map row whose ground cell starts with the token F<k> (F<k> followed by a space, `-`, or end of cell). A mention in a status cell or prose does not map it. Every backticked `knowledge/<name>` in an entries cell exists at the revision. A new grounded entry and its map row land in the same commit. Every entry grounded at the base revision is present at the tip with the same F<k>; grounding may be added, never removed to pass. | knowledge entries with a `ground:` line; README coverage-map tables (header `ground` / … / `entries…`) at every landing | `python3 -B tools/souji-coverage-agreement.py --root . --rev <full40>` exits 0 (`mismatches=0`); `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` → `cases=9 pass=9 control=FALSE-GREEN-REJECTED`; the base-vs-tip grounded set is listed in the landing record. Failure witness: the same tool at `a65fac98964b445758e94c805728c9a19d302ff8` reports `mismatches=2` (`census/round-24/records/c2-control-base.tsv`) | `lessons/round-23-verifier-spotcheck.md:41`; `lessons/round-24.md` R24-M1 |

Limits:

- It does not capture R24-M2 (status cells) or R24-M3 (fixture-count prose).
- The per-entry clause has no tool enforcement (`W2C2Rerun` F3).
- Q56 serves calibration. It is not the discernment "disagreement → criterion" path: the r23 closure agreed 3/3 (`W2Trend` F14).

## Wave-2 seat reports (35 of 35 landed)

- Survive: `W2C1Rerun`, `W2C1Envelope`, `W2C1Axis` (coverage-move holds, qualified), `W2C1MutFixture`, `W2C2Rerun`, `W2C2Mut`, `W2C2Game`, `W2C2Calib` (survives-narrow), `W2Collisions`, `W2SrcPath`, `W2Reverify`, `W2Separable` (counters separable; receipts carried by the widening), `W2Misroot`, `W2Inherited`.
- PARTIAL: `W2C1MutTool` (uncovered=7), `W2C3Mut` (uncovered=9), `W2C3Rerun` (HIGH run→verify asymmetry), `W2EntryClaims`, `W2EntryGate`, `W2Rejects`, `W2Registry`, `W2Slice`, `W2SrcCountWt`, `W2ReadmeRow`, `W2Scope`.
- FAIL: `W2C1Amend`, `W2C1TopLevel`, `W2C3CountsRE`, `W2C3Redact`, `W2C3Symmetry`, `W2R23F4`.
- Scribe or critic drafts: `W2ScorecardDraft`, `W2Trend`, this seat.
- Open conflict: `W2C3Redact` F4 (newline in argv: verify fails closed) vs `W2C3Symmetry` F2 (a newline shape forges a `verify=ok` header). Both may hold for different shapes; the non-author should re-run both witnesses.

`W2ScorecardDraft` F2: the r23 C2 grep counter now reads 15 files at the tip, and one of them
(`size-census-lane.txt`) fails `verify`. F3: "re-run the r23 counters at the new tip" has no receipt.

## Seat-reported failures (wave 1)

Wave 1 had 38 seats: 32 `PASS`, 6 `PARTIAL`, 0 `FAIL`, 0 without a `STATUS:` line. Verbatim heads:

- `.ufo/waves/round-24/w1/CritC3Value.md` "STATUS: PARTIAL — the draft keeps regress=5/5, and the durability refusal is a real, symmetric gain." — accepted (amendment-1 C3 `run` refusals). The redaction concern it raised recurs as R24-M16.
- `.ufo/waves/round-24/w1/CritPrereg.md` "STATUS: PARTIAL. No defect would invalidate the round yet." — accepted (amendment-1; deviations 1–3).
- `.ufo/waves/round-24/w1/ProbeAlternates.md` "STATUS: PARTIAL — clause 1 (`alternate:` line, absolutized) CONFIRMED; clause 2 (fsck ignores alternate-only objects) FALSIFIED" — accepted: `census.unreachable_scope=includes-alternates`; `c1-after.tsv` case 5 reads `unreachable=3`.
- `.ufo/waves/round-24/w1/ReviewQualityBar.md` "STATUS: PARTIAL — the bar, the commit list and the exact gate command are complete." — the gate ran (`gate-check-r24-entry.tsv`). Its fleet-root read is disclosed (`W2Scope` F2).
- `.ufo/waves/round-24/w1/ScribeEntry.md` "STATUS: PARTIAL. The entry below follows every L1 decision." — the fixture landed (`c1-after.tsv`). Its scratch claim is false (R24-M14).
- `.ufo/waves/round-24/w1/ScribeLessonMistakes.md` "STATUS: PARTIAL — 11 mistake rows mined, every pointer opened this run, Q-next (Q56) proposed." — R24-M1's witness is now SHOWN (`c2-control-base.tsv`).

## Trend verdicts (draft; the non-author closure rules)

- **expansion — `unprovable-but-better`.**
  - F2 is held ground, and files go from 3 to 4. `grounded` +2 is +1 new entry and +1 front-matter normalization (`W2Trend` F1–F2).
  - The debris-census capability is not admitted in SCORECARD at the tip (`W2Trend` F3).
  - The predicate's capability reading is routed to the fleet (`ReviewAxesTrend` A1).
  - Not `harmed`.
- **quality — `harmed` as landed; `improved (bounded)` only after append-only marking.**
  - For: `git-repo-structure-readonly.md` re-verified on 2.56.0 (`r13-recheck-receipt.tsv` `selftest=PASS ids=5/5`; `W2Reverify` survives).
  - Against: the admitted `repo-size-census-readonly.md` claim 1 is narrowed by r24's own entry and left unmarked, which is LEARNING's `harmed` trigger (R24-M21; `W2Trend` F6).
  - Against: the new entry carries falsified or overstated sentences (R24-M20).
  - Required before close: the R24-M21 note, the `verified-at:` refresh, and the R24-M20 corrections. Staged-candidate narrowing is a gate decision and is not counted here (`W2Trend` F8).
- **discernment — pending the non-author spot-check; not self-graded.**
  - Sample available: 2 admits and 3 rejects. Every ADMIT quote is byte-exact (`W2EntryGate`).
  - Two reject reasons are false as written (R24-M17).
  - Slice verdicts are excluded (`W2Trend` F13).
  - Q56 must land with this lesson, or LEARNING's "criterion with no lesson" `harmed` trigger applies (`W2Trend` F14).

## Post-wave-2 repairs (L1, landed in the final round-24 commit; supersede the open items above)

Each repair answers a wave-2 finding; none edits a frozen counter, case set or target. Every
claim counter was re-run on the final bytes and re-receipted (`census/round-24/records/*-final.tsv`).

- **R24-M24 (C1 bare-repo regression, `W2C1TopLevel` FAIL)** — fixed: `resolve()` asks
  `--show-toplevel` only for non-bare repositories; a non-empty bare repo reports
  `invoked_from=bare` again, an empty bare repo exits 1 on fsck's documented `notice: No default
  references`, a subdirectory still exits 2. The docstring no longer says discovery "cannot walk
  up": a planted gitfile or `core.worktree` that makes git report PATH as a top level is followed.
- **R24-M16 + `W2C3Symmetry` (C3 asymmetry and leak)** — fixed in `run`: `cmd=` is the shlex.join
  of per-element-redacted argv (no second whole-line pass); a command whose secret-shaped content
  a whole-line pass would treat differently is refused (`CMD-SECRET-SHAPED`); an argv element with
  a newline/CR is refused (`CMD-NEWLINE`, the receipt-header forgery `W2C3Symmetry` built is now
  refused); checked-out tool bytes that differ from the committed blob are refused
  (`TOOL-CHECKOUT-DIFFERS`). Cost, disclosed: commands carrying `password=`/`--token=`-shaped
  arguments get no receipt (the base wrote them redacted). Cross-element secrets that no redaction
  pattern matches (`--token` `abc`) were unredacted at base too and remain a pre-existing gap.
- **R24-M13 + `W2C3CountsRE` (counts widening accepted decoys)** — fixed: `run` and `verify` share
  `counts_line()`, which takes the last STDOUT line that starts with a counts line (anchored, with a
  trailing boundary). stderr-only, prose-buried, `subcases=`/`pass=9xyz` decoys are refused
  `RECEIPT-COUNTS-ABSENT`; the r23 fixture (counts line, then a label line) stays 8/8. Residual: a
  receipt whose final counts line was deleted still verifies on an earlier per-case counts line.
- **R24-M15 (`run --out` deny-list)** — fixed: `--out` must resolve under `/var/tmp/`
  (`OUT-OUTSIDE-VAR-TMP`).
- **R24-M12 (r23 record-agreement last-wins hole, the round's mined mistake)** — fixed in
  `tools/souji-record-agreement.py`: a fenced receipt's counts are read only between
  `--- stdout ---` and `--- stderr ---`. Failure witness (`W2R23F4`, scratch): the committed tool
  printed `mismatches=0` rc 0 on a receipt whose stdout reads `mismatches=7`; with the fix the same
  receipt yields two `value-disagree` rows, and an extended fixture scores 14/15 on the old tool and
  15/15 on the fix. The committed fixture stays 12/12 and the lane reads `mismatches=0`; the three
  extra fixture cases are not committed this round (routed to r25).
- **R24-M17/M19/M20 (entry and Gate)** — corrected in
  `corpus/knowledge/count-objects-linked-worktree-garbage.md`: the reader decides what is counted
  but the writer decides what exists (a git-2.30.0-created worktree has no private `refs` and reads
  0); item 3 scoped to 2.56.0; the bisect count follows the leftover directory; the files-backend
  scope of the `refs/worktree` readings; btrfs directory sizes; alternate pack junk counted from the
  borrower; the r25 admit relabelled to one fixture-committed spelling plus seat-observed modes;
  the false provenance and S131 reject clauses rewritten; the `GIT_COMMON_DIR` precondition.
  Gate re-run: `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0`; Q54 `locators_bad=0`.
- **R24-M21 (admitted entry narrowed and unmarked)** — marked: `repo-size-census-readonly.md` gains
  an appended `## Round 24 narrowing` (claim 1 narrowed; the sequential fixture exists, concurrency
  still owed). `git-repo-structure-readonly.md`'s `verified-at:` now names the 2.56.0 receipt.
- **R24-M22/M23 (slice and registry sweep)** — S118 re-graded `accepted` per round-22 definitions
  (re-cite to the IEEE record), the vocabulary mapping recorded; S115 `used-by` now lists the new
  entry; S123's scope widened to the § DETAILS sentence it is cited for.
- **README § Round 24** — the false "counts any recurrence" sentence, the landing-condition claim
  and the "8 cases fence" overstatement replaced with what the bytes show (`W2ReadmeRow`).
- **Q56** — landed in `corpus/QUALITY.md` in the same commit as this lesson.

Not repaired this round (routed to r25): C1 fixture cases for bare/subdirectory/`extensions.partialClone`-only
inputs and for the 778747e envelope hardening (unmeasured by the counter, `W2Separable`/`W2C1Rerun`);
a C2 `--base` arm automating the per-entry kill rule (`W2C2Rerun`); C2 status-column blindness
(`W2C2Calib`); C3 fixture cases for the uncounted run/verify refusals (`W2C3Mut` uncovered=9);
the three r23 record-agreement fixture cases; the stale README :40 row; `PROVINCE.md` still lists the
unreachable census as frontier.

## Trend verdicts (L1 self-reading after repairs; the non-author closure rules)

- **expansion — `unprovable-but-better`.** One new entry on held F2 ground (files 3 → 4) plus a
  front-matter normalisation; a new debris-census tool and edge class, not new map ground.
- **quality — `improved` (bounded).** A stale entry re-verifies on git 2.56.0 (receipt
  `r13-recheck-receipt.tsv`, `selftest=PASS ids=5/5`, header refreshed), and an admitted entry the
  round narrowed is marked rather than left contradicted. Bound: the marking landed after wave 2
  found it unmarked.
- **discernment — not self-graded.** Sample for the closure: 2 admits (r27 re-sourced, r25 partial)
  and 3 rejects (r25 headline, r26, r23) plus a provenance reject; two reject reasons were false as
  first written and are corrected above.
