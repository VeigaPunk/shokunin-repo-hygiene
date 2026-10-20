STATUS: DONE — draft-check complete; Q29–Q32 are not yet in QUALITY.md, and the admission pointers/tests below are required.

# Scope and basis

Axis judged: **calibration**. QUALITY.md:11–14 requires every criterion to cite the lesson that produced it, and defines a lesson pointer as an ID resolving under that round’s `## Mistakes`; supersession is append-only and names the row replaced. QUALITY.md currently ends at Q28 (line 72). The requested round-18 lesson is still a draft: `ScribeLessonDraft.md:1,3` says it was not written, and its measurements/pointers still contain `TBD-L1`. Therefore the following are admission requirements, not claims that the rows or checks have landed.

## Findings (admission-gating; draft-level, not implementation failures)

### Q29 — supersedes Q7 for lane/jj-colocated commits; Q7 remains for plain repos

- **Required lesson pointer:** `corpus/lessons/round-18.md`, `## Mistakes`, **R18-M3**. The draft R18-M3 identifies the hardcoded `--as souji` failure (`.ufo/waves/round-18/w1/ScribeLessonDraft.md:31`); that exact row must land. Add Q29 as a new row explicitly saying it supersedes Q7 only for the jj-colocated lane route; do not rewrite Q7, and retain Q7’s plain-repository rule.
- **Test column must name:** a focused test of the `souji-quarantine` emitted `CMD` recipe that proves the recipe works through `jj-lane.sh` in an isolated colocated repo under a non-`souji` recorded lane ID (and handles the documented `protocol` case if that is the emitted alternative), names both source and quarantine paths, and proves a plain Git repo retains the Q7 route. Give the exact committed fixture/selftest command. `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` is useful for the Q28 receipt behavior and its J6 plain-repo control, but is not sufficient alone: its documented cases concern receipt roots (`tests/fixtures/r17-jj-receipts.sh:14–42`), while the R18 defect is `q_jj_commit_recipe` (`tools/souji-quarantine.sh:246–250`). If Q29 also cites the R17 fixture, name it alongside—not instead of—the recipe regression.
- **Verdict:** partial until the focused command is named and covers the changed recipe; smallest fix is to land R18-M3 and add/name the focused assertion (for example, as an explicit new case in `souji-quarantine.sh --selftest`).

### Q30 — bounded per-repo census and session-isolated fixtures

- **Required lesson pointer:** `corpus/lessons/round-18.md`, `## Mistakes`, **R18-M2** for the 58 leaked blocked fixture processes (`ScribeLessonDraft.md:30`). However, the draft places the fleet-census FIFO hang only in Measurements (`:20`), not in a Mistakes row. Under QUALITY.md:11–14, a measurement/claim is not a valid `round-18 Mnn` pointer. Q30 combines both causes, so add a distinct `## Mistakes` entry for the whole-census FIFO hang/lost healthy rows (or explicitly expand M2 to record both), then cite the exact mistake ID(s). M2 alone does not support the per-repository isolation part.
- **Test column must name:** the exact committed FIFO-swap regression fixture invocation and the existing matrix command `python3 census/round-17/run-matrix.py --changed <rev> --output <f>`. The focused test must swap `.git/info/attributes` to a FIFO after the guard, assert the timed-out repo’s exact error row and `repo-timeout` diagnostic, exit 0, and preserved healthy-neighbour rows; it must also assert invalid timeout values exit 2. For fixture cleanup, run the red arm with session-isolated children, verify process-group termination and independently count zero blocked/orphan processes afterward. `bash -n`/ShellCheck or a generic matrix-green claim alone does not prove bounded behavior or cleanup. The draft already marks the after outcomes and 0 orphans as `TBD-L1` (`:20–21`).
- **Verdict:** partial until a Mistakes pointer covers both failures and the named fixture actually asserts the timeout and zero-residue outcomes.

### Q31 — authority-file pointers resolve (`LG-DANGLING-PTR`)

- **Required lesson pointer:** `corpus/lessons/round-18.md`, `## Mistakes`, **R18-M1**, for publishing uncommitted evidence paths (`ScribeLessonDraft.md:29`). Land that row and cite it; do not cite only the C2 claim or the changed gate’s zero-finding result.
- **Test column must name:** `python3 tools/souji-landing-gate.py --selftest` plus the exact round-18 invocation `python3 tools/souji-landing-gate.py --root <lane> --rev <rev> --round 18`. Its test cases must distinguish a missing repository-relative pointer (finding) from a resolving pointer (no finding), cover committed exemptions and fleet-only paths without misreporting them as lane findings, and verify the ≥18 scope does not alter the pinned historical replay: `python3 census/round-17/gate-replays.py`. The lesson draft lists the gate selftest and historical replay as still `TBD-L1` (`:22`).
- **Verdict:** partial until R18-M1 is landed and the test column names both behavioral gate cases and the historical replay guard.

### Q32 — process residue census is list-only

- **Required lesson pointer:** `corpus/lessons/round-18.md`, `## Mistakes`, **R18-M2**, because the 58 blocked orphan processes are the residue that motivated this governed surface (`ScribeLessonDraft.md:30`). Ensure the landed M2 retains that concrete evidence pointer.
- **Test column must name:** the exact committed fixture invocation that creates controlled current-uid examples for both predicates (deleted cwd and argv containing a missing path under `/var/tmp`, `/tmp`, or `/dev/shm`), runs `tools/souji-proc-census.sh`, and compares its rows/counts with an independent `ps` plus `/proc/<pid>/cwd` oracle. It must assert the stated fields and command redaction/truncation, and prove list-only behavior by checking that the observed processes remain untouched; all fixture-owned children must be cleaned up by the fixture. A help-text/source-marker check or comparison only against the census’s own output is insufficient. The round-18 lesson draft names this independent counter but leaves its result and read-only check `TBD-L1` (`:23`).
- **Verdict:** partial until the exact fixture command, independent oracle, and no-mutation assertion are named and measured.

# Verification and gaps

- Read `corpus/QUALITY.md:11–14,16–72`: the rule is lesson-ID-to-`## Mistakes`; the current last row is Q28.
- Read `.ufo/waves/round-18/w1/ScribeLessonDraft.md:20–31`: M1–M3 are draft-only, C1/C2/C3 checks are still `TBD-L1`, and no R18 Mistakes row currently records the whole-census FIFO hang.
- Read `tools/souji-quarantine.sh:246–250` and `tests/fixtures/r17-jj-receipts.sh:14–42`: the defect is in the emitted lane helper recipe; the existing R17 fixture’s stated cases do not claim that recipe coverage.
- Ran: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- corpus/QUALITY.md corpus/lessons/round-18.md` → no output.
- No executable tests were run. No tools were installed or updated.

Residual risk: no Q29–Q32 drafts or landed R18 lesson were available to review; these are the precise pointers and behavioral test contents needed before admission, not validation of future implementation.