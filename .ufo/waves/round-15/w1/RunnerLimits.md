# RunnerLimits — round 15 / w1 (C1 operability, C2 calibration)

Seat: `SoujiR15.RunnerLimits` (reviewer, leaf). Scope: runner command bounds, stderr capture, partial-failure preservation. Source inspection only; no tests, probes, builds, installs or edits. Tools installed or updated: none.

Line numbers are the r14 state read during this pass. `ConfigRepair` may already be editing `tools/souji-census.sh`; re-read before citing.

Tags: **[F]** observed in a cited line. **[I]** inference from source shape, not run. **[X]** claim taken from another seat's recorded probe or doc, not re-run here.

## Summary

- The census tool has **no command bound at all**. `grep -c timeout tools/souji-census.sh` = 0. Every git, find and du call is unbounded.
- Several census git reads **fail open or fail to zero**. A failed read becomes a valid-looking `0` or an absent value, and the census still exits 0.
- Git stderr is **discarded everywhere** (`2>/dev/null`). Refusals carry no diagnostic.
- Both r14 fixture runners **lose partial output on timeout**. One maps timeout to an honest failure (rc 1), the other to an uncaught traceback (rc 1). Neither maps it to could-not-evaluate (rc 2).
- The round-15 runner (`census/round-15/run-verification.py`) and the r15 fixtures do not exist yet. Section 4 gives the design acceptance they must meet.

## 1. Findings

### F1 — High, operability: census has no command bound
- **[F]** No `timeout` in `tools/souji-census.sh`. Unbounded calls include `git config` (:500, :511), `git worktree list` (:688, :836), `for-each-ref` and `rev-list` (:694, :698, :702), `git status` (:710-716), `du` (:731), `find` (:749-753) and `git rev-parse` (:859).
- **[I]** A stalled lock or mount hangs the whole census. The runner, not the tool, is the only bound.
- **Acceptance:** every census invocation in `run-verification.py` and in each r15 fixture runs under `timeout --kill-after=K T` with fixed literals. Options precede the duration. rc 124 or 137 maps to could-not-evaluate (rc 2), never to pass.
- **[X]** GNU timeout exits 124 without `--preserve-status` and supports `--kill-after` (S038 in `corpus/SOURCES.md:50`). BoundQuarantine reports that options after DURATION give rc 127 and that the group is killed on timeout. Not re-run.

### F2 — High, partial failure: fail-open second read of `core.worktree`
- **[F]** `tools/souji-census.sh:511` reads `wt=$(git config --file "$cfg" --no-includes --get core.worktree 2>/dev/null || true)`. Any failure of that second call leaves `wt` empty. The boundary check at :512-521 is then skipped.
- **[F]** The earlier `--list` read at :500 is a different call, so its success does not cover this one.
- **Acceptance:** read the values once, with `git config --file "$cfg" --no-includes --list -z`, and derive `core.worktree` from the same bytes. If the second read stays, accept only exit 1 (absent) and `protected_fail` on any other code. Do not use `|| true` on a guard read.
- **[I]** I did not check git's exit-code table for `--get` against this build. SourcesDraft owns the quote. Keep the single-read form regardless.

### F3 — High, partial failure: git failures become zero or false clean
- **[F]** `:688` `worktrees` = `git worktree list 2>/dev/null | grep -c . || true`. A failure becomes `0`.
- **[F]** `:694-698`: `nremotes` and `rev-list --count ... || printf '0'`. A failure becomes `unpushed=0` and `no-remote` or `has-remote`, with exit 0.
- **[F]** `:836`: `git worktree list --porcelain 2>/dev/null || true` silently drops linked-worktree flags (`wt-absent`, `wt-dirty`).
- **[F] Contrast:** `:716` maps a failed `git status` to `unverifiable`, which is the honest pattern. `:859` maps a failed `rev-parse` to an `error` row, but still exits 0.
- **Acceptance:** each of :688, :694-698 and :836 must return an explicit non-numeric token (for example `unverifiable`) on failure, using the :716 pattern, or the whole census must refuse. A zero from a failed read must never reach a row.
- **Scope note:** this is pre-existing r14 state outside the listed ConfigRepair families. Whether it is in C1 scope is for SoujiR15 to decide. It is the same partial-failure defect class, so I report it.

### F4 — Medium, stderr capture: git diagnostics discarded
- **[F]** `2>/dev/null` at :500, :511, :688, :694, :698, :702, :710-716 and :836. :859 uses `>/dev/null 2>&1`.
- **[F]** `:501` `protected_fail "git-config-unparsed"` prints only the label and path. The operator cannot see why git rejected the file.
- **Acceptance:** capture git stderr into a bounded `/var/tmp` temp file removed by trap. Emit at most one sanitized line. Do not echo config values (OutputLeak). Keep the existing `protected_fail` label contract.

### F5 — High, runner: r14 census fixture loses partial output and misclassifies timeout
- **[F]** `tests/fixtures/r14-census-boundary.py:391-402`. `subprocess.run(..., timeout=90)`. `TimeoutExpired` returns `Result(124, "", "timeout", ...)`. Partial stdout and stderr are discarded.
- **[F]** `:377-390` runs `strace` as the direct child. Only that child is killed, not the bash census or its git and find children.
- **[F]** `refusal_problems` (:484-485) reports `exit=124 want 2`. The case is an honest FAIL, and the run exits 1 (:729). Under the lane contract this should be could-not-evaluate (exit 2).
- **[F]** `:716-718` prints only `problems` for a failing case. The census stdout and stderr of that case are never shown.
- **[I]** SIGKILL to `strace` may detach tracees and leave them running. `cleanup()` then `rmtree`s the scratch under them. Verify before relying on it.
- **Acceptance:** run each case under GNU `timeout -k` (or a new session with a process-group kill). Map 124 and 137 to exit 2 with partial output written to an exclusively-created file. Print stdout and stderr for every failing case.

### F6 — High, runner: r14 evidence-cache fixture turns timeout into an uncaught traceback
- **[F]** `tests/fixtures/r14-evidence-cache.py:63-70`. `invoke()` calls `subprocess.run(..., timeout=180)` with no `except`.
- **[F]** The exception propagates through `check` and `run_case`. `finally` (:344-345) removes `base`. The results list is printed only at :347-357, so it is never printed.
- **[I]** The uncaught exception exits with status 1 (Python default). That is indistinguishable from honest failed checks (:364), and it is not 2. All earlier per-case diagnostics are lost.
- **Acceptance:** catch `TimeoutExpired` in `invoke`, record the case as could-not-evaluate with its partial output, and exit 2. Print results in a `finally`. The r15 config fixture must copy the r14 census fixture's `run_tool` shape, not this `invoke`.

### F7 — Medium, runner: cert-evidence selftest timeout drops partial output
- **[F]** `tools/souji-cert-evidence.py:1005-1015` catches `TimeoutExpired` and returns `(None, "", "TIMEOUT")`. The case is recorded as a failure (`_record` :1030-1061). Partial stdout is dropped, and the kill reaches only the direct child.
- **Assessment:** fail-closed and acceptable. Keep as lower priority. No change required for C1.

### F8 — Medium, runner: unbounded captured streams
- **[F]** `capture_output=True` with no size cap at `tests/fixtures/r14-census-boundary.py:396-398`, `tests/fixtures/r14-evidence-cache.py:66-68`, and `tools/souji-cert-evidence.py:1008-1009`.
- **[F]** `_record` and the fixture failure printers dump full stdout and stderr (`souji-cert-evidence.py:1049-1061`; `r14-evidence-cache.py:354-357`). A runaway stream floods memory and the log.
- **Acceptance:** `RoundRunner` and the r15 fixtures capture each stream to a file, keep at most a fixed byte cap, and record `bytes_total` and `truncated: true|false`. The C2 checker must reject a truncated stdout where a finding is needed.

### F9 — Medium, calibration: census exit 0 does not mean a complete census
- **[F]** Header :102-103: exit 0 = census emitted. Per-repo `error` rows (:859-861) and `unverifiable` values (:717) still exit 0.
- **Acceptance:** the RoundRunner and C2 checker judge census evidence from the verdict columns, not from exit 0. Any census row with `error` or `unverifiable` in a benign-config control makes that control not-green.

## 2. Preserved properties (verified by reading)

- **P1** `emit_census` buffers rows and prints only after all repos succeed (:982-994). A protected refusal (exit 2) therefore yields no partial TSV. Keep this.
- **P2** Refusals map to exit 2 via `if [ "$rc" = 2 ]; then exit 2` (:985-986). Keep.
- **P3** The r14 census fixture requires exit 2, empty stdout, and the `path-protected` finding (:484-491). Keep.
- **P4** Fixture cleanup runs in `finally` (:730-731 and :344-345). Keep, but see F5 and F6 for the live-child case.
- **P5** `souji-cert-evidence.py` `_record` retains stdout and stderr on failure (:1049-1061). Use this as the pattern for r15 output.

## 3. Unrun checks (not green)

Nothing was run. L1 should run after all seats land:

1. `grep -c 'timeout' tools/souji-census.sh`. Expected 0 at r14. After repair, at least one wrapper per runner invocation, not per tool call.
2. `grep -nE 'git .*2>/dev/null' tools/souji-census.sh`. Expected count unchanged or lower, with stderr captured.
3. `grep -nE '\|\| *true' tools/souji-census.sh`. Each remaining hit must be audited against F2 and F3.
4. Behavioural: a stalled-`git` shim on `PATH` inside a `/var/tmp` fixture. Expect bounded completion, rc 2 mapping, and retained partial output. Design only here.
5. `shellcheck -S warning tools/souji-census.sh`. Not run; treat as unverified.
6. `python3 tests/fixtures/r15-census-config.py --tool <baseline>` must go red for the timeout reason, and `--tool <installed>` green. Design only here.

## 4. Acceptance for the round-15 runner (design-only; sources not present)

- `census/round-15/run-verification.py` and `tests/fixtures/r15-census-config.py` do not exist yet. This is design-only.
- Every invocation: `timeout --kill-after=K T cmd` with literal K and T, options before DURATION. Group kill, or a documented residual if not.
- rc 124 or 137 → could-not-evaluate. Never pass. Partial stdout and stderr written to an exclusively-created `/var/tmp` file, with digest and byte count.
- Captured streams capped, with `truncated` recorded.
- Git stderr captured and sanitized, not dropped.
- Verification JSON created exclusively (`x` mode). No historical overwrite.
- Scratch removal waits for any killed process group. No `rmtree` under a live child.

## 5. Limits

- Source inspection only. No command was executed and no fixture was run.
- Python `subprocess` timeout semantics are an inference from the call shape, not from the CPython source. Verify before relying on it.
- The GNU timeout facts in F1 are [X] from S038 and BoundQuarantine. Not re-run.
- `--get` exit-code behaviour in git is not verified here (see F2).
- Line numbers are at read time and may shift under `ConfigRepair`'s edits.

## 6. Material findings sent to SoujiR15

F2, F3, F5 and F6 were sent as peer messages. Scope decision needed from SoujiR15 on whether F3 is inside C1.

## 7. Query-boundary disclosure

Two of my search calls used the whole lane root as `path`, which the boundary reminder forbids because it reaches the operator sweep. I did not open any operator-sweep file, and no further whole-root search was run after the reminder.

1. First grep, pattern `(?i)(timeout|stderr|max_output|output_limit|subprocess|runner|partial)`, path `/home/vgpnk/Projects/shokunin/souji-shokunin` (whole lane root), gitignore false. Violation. Visible results were round-13 wave files, LOG, SKILL, corpus, census/round-11 and census/round-12 paths. Whether census/operator-sweep-20261019 was traversed is not visible in the output.
2. Grep pattern `(?i)(value-blind|rejected-harmed|git config|config --get|partial failure|stderr capture)`, path `/home/vgpnk/Projects/shokunin/souji-shokunin` (whole lane root), gitignore false, skip 0. Violation, same visibility limit. Results cited from it: LOG.md:706, SKILL.md:217-218, round-13 and round-14 wave files.
3. The later grep for `promisor|rejected-harmed|value-blind|false.*refus` used explicit paths only (corpus, census/round-14, census/round-15, tests/fixtures, .ufo/waves/round-14, LOG.md, SCORECARD.md). Not a violation.

Non-violating calls: the top-level non-recursive glob of the lane root (`souji-shokunin/*`), globs limited to `.ufo/waves/round-15/**`, `census/round-15/**`, `.ufo/waves/round-14/**` and `tests/fixtures/**`, and all reads of explicit files.

Limitation: findings in this report that rely on those whole-root results are only corroborated by the explicit-file reads in sections 1 (F1-F9 cite tools/, tests/fixtures/ and round-14 wave files read directly). No further search was run after the reminder, and no runtime probe or test was executed at any point.
