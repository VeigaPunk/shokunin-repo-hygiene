STATUS: DONE — Q29–Q32 reviewed at 5efb519; Q7 and the r14 pin are intact, with calibration and test-spec gaps noted.

# RevQualityRows — round 18, wave 2

Attacked axis: **calibration**. Scope: `corpus/QUALITY.md` Q29–Q32 and their cited lesson/report evidence, command syntax, and claimed gate behavior.

## Findings (severity order)

### Moderate — Q29's printed helper invocation omits a required argument

`corpus/QUALITY.md:78` gives `jj-lane.sh commit <repo> --as <owner-id> -- <rel> <qpath>` as the owner-helper route. The helper's usage requires `-m <message>` (`/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh:12,54`), and its parser rejects a missing message (`:499-507`). The current quarantine recipe correctly emits `-m ...` (`tools/souji-quarantine.sh:276-279`), and the SKILL checklist gives that form (`SKILL.md:131`); copying Q29's form as written exits through usage instead of committing.

**Smallest fix:** include `-m <message>` before `--` in Q29's helper invocation.

### Moderate — Q31's unqualified “every” overstates the gate's pointer grammar

`corpus/QUALITY.md:80` says the gate resolves “every repo-relative path token.” The gate only searches `POINTER_PATH_RE` matches (`tools/souji-landing-gate.py:124-133,718-724`); it deliberately skips wildcard/placeholder forms and `round-N`. Round 18's own Gate decision records further limits: elided tokens and prose without a path prefix are not recognized, and fleet paths are checked against the fleet working tree rather than a revision (`corpus/lessons/round-18.md:27`). These limits make the unqualified completeness wording broader than observed behavior.

**Smallest fix:** qualify the guarantee as covering path tokens recognized by the gate's documented grammar and carry the known omissions/fleet-root limitation in Q31.

### Moderate — Q31's listed test does not exercise two explicit contracts

The Q31 test column names the external fixture and gate replays, but not the gate selftest. The external fixture documents committed-valid and malformed exemptions and the historical pointer replay (`tests/fixtures/r18-landing-pointers.py:15-19,254-306`); it does not assert an unused/stale exemption finding or `LG-FROZEN-MEASURED`. The in-tree gate selftest does contain those cases (`tools/souji-landing-gate.py:1375-1380,1480-1498`), but the column omits `python3 tools/souji-landing-gate.py --selftest`. The historical fixture uses a minimum pointer-finding assertion, so it does not make the measured finding a required assertion either.

**Smallest fix:** add the gate selftest command to Q31, or add exact stale-exemption and measured-commit assertions to `r18-landing-pointers.py`.

### Minor — Q29's baseline-red assertion is not run by its listed command

`corpus/QUALITY.md:78` lists `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` and then says J13 fails on b576341 tools. That command selects the current `tools` directory; it does not select b576341's tool bytes. The fixture's `--tool-dir` selects the implementation under test (`tests/fixtures/r17-jj-receipts.sh:51-58,107-131`). The committed paired records show the expected observation—baseline J13 FAIL at `census/round-18/jj-receipts-r18-baseb576341.txt:45`, changed J13 PASS at `census/round-18/jj-receipts-r18-changed.txt:45`—but the row's command does not reproduce the red arm.

**Smallest fix:** label the listed command as the changed arm and provide a second invocation selecting the baseline tool directory, or cite the committed baseline record as historical evidence rather than as part of the runnable command.

### Minor — Q32's `/proc` “only” list and signal wording do not describe all modes

`corpus/QUALITY.md:81` says the tool reads `/proc` stat, cmdline, cwd, fd and wchan “only,” but the implementation also reads `/proc/<pid>/status` to check UID (`tools/souji-proc-census.sh:141-151`), `/proc/stat` for boot time and `/proc/sys/kernel/random/boot_id` (`:261-275`). It also says the watchdog signal is the only signal souji tools send; `souji-proc-census.sh --selftest` sends SIGKILL to its own fixture groups (`:363-369`). The live listing remains list-only and the selftest cleanup targets its own children, so this is a scope/wording defect, not evidence that listed rows are signalled.

**Smallest fix:** name the additional status and boot metadata reads, and scope the no-signal/only-signal wording to the live listing path (excluding selftest-owned cleanup).

### Minor — Q32's live comparison and header-stub control are not fully specified as runnable checks

The Q32 test column runs the fixture against the real tool, then states that its live PID set equals `python3 census/round-18/leak-count.py` and that a header-only stub fails P1/P2 (`corpus/QUALITY.md:81`). The fixture accepts a selectable `--tool` and exercises P1/P2 (`tests/fixtures/r18-proc-census.sh:24-50,357-395`), but the column provides neither a stub input/command nor the live census invocation and comparison operation. `leak-count.py` emits a JSON `pids` array (`census/round-18/leak-count.py:123-169`), while the tool emits TSV; the equality check therefore needs an explicit extraction/comparison step to be reproducible from the column.

**Smallest fix:** list the live census and counter invocations plus the exact PID-set comparison, and make the header-only control a fixture-generated stub or provide its `--tool` invocation.

## Holds and evidence

- All Q29–Q32 lesson/report pointers resolve to committed records at the reviewed tree: Q29's R1/R4 in the round-17 spot-check and R18-M3; Q30's R18-M2/M4 and round-17 residual sentinel F3; Q31's R18-M1 and spot-check R2; Q32's R18-M2 and `CriticC3Authority.md`. In particular, the R17 sentinel F3 is present in `corpus/lessons/round-17.md:86`, the R18 Mistakes rows are at `corpus/lessons/round-18.md:15-18`, and spot-check R2/R4 are at `corpus/lessons/round-17-verifier-spotcheck.md:60,62`.
- Q29 does **not** rewrite Q7: `git diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- corpus/QUALITY.md` reported `1 file changed, 9 insertions(+), 0 deletions(-)`; the diff is the appended Round 18 section. Q7 remains unchanged and Q29 explicitly limits supersession to colocated repos.
- Q30's r14 exception is honest. `git diff --quiet b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- tests/fixtures/r14-census-boundary.py` returned `r14_fixture_diff_rc=0`. `sha256sum` of the working file and `git show` bytes at both b576341 and 5efb519 returned `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`, matching `NAMESPACE_SHA256` at `tools/souji-preservation-evidence.py:307`. Its declared R14C2-01..12 case set is preserved; no FIFO case was found in the fixture source. The `run-matrix.py` CLI requires the two arguments Q30 lists and its output is exclusive-create (`census/round-18/run-matrix.py:251-291`).
- Q31's baseline record `census/round-18/gate-pointers-before-b576341.json` contains 10 findings, including the named never-committed records and one `LG-FROZEN-MEASURED`; the historical fixture correctly expects exit 2 because b576341 has no round-18 reports while retaining pointer findings (`tests/fixtures/r18-landing-pointers.py:302-306`).

## Verification gaps / method

No test or gate command was executed: this review contract supplied no `ALLOWED-EXEC` authorization. LSP is not mounted (`read xd://lsp` returned “No such tool”); therefore no LSP status/references/definition/diagnostics were available. Conclusions above are from the reviewed source and committed records, not runtime verification. No tools were installed or updated.