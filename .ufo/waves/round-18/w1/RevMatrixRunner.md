STATUS: DONE — static review found round-18 coverage, gating, and timeout-cleanup gaps

Axes: operability (judged axis); coverage (suite/arm selection); calibration (what the record says passed).

## Findings

### High — A suite timeout can leave a nested session running

`census/round-17/run-matrix.py:89-108` does the right thing for the suite process group: `start_new_session=True`, then `killpg(p.pid, SIGKILL)` on timeout. That does not clean up process groups created by the fixture. The selected `r17-hygiene` fixture does exactly that for each census invocation (`tests/fixtures/r17-census-hygiene.py:293-317`): it starts the child in a new session and only its parent fixture enforces the 60-second kill. If the matrix's 900-second suite timeout fires while that fixture is waiting on a census invocation, the matrix kills the fixture's group but not the nested session; the fixture can no longer perform its own timeout cleanup. The r14/r15 fixtures also use `subprocess.run(..., timeout=90)` for their census invocations (`tests/fixtures/r14-census-boundary.py:392-404`, `tests/fixtures/r15-census-config.py:781-793`); those timeout handlers do not signal a process group, so descendant cleanup is not guaranteed when a timeout is caught and the suite continues.

**Smallest fix:** make timeout ownership cover all nested census process groups, including when the outer suite is terminated (for example, register nested groups with a supervisor and reap them on both timeout paths). Keep a bounded wait after signaling; do not assume killing the suite's group reaches a new session.

### High — `invalid_suites` and exit status ignore failed arm preflights

The runner records `bash -n`, warning-level ShellCheck, and `--selftest` results (`census/round-17/run-matrix.py:206-218`), but computes `invalid_suites` only from each fixture's `valid` field (`:232-241`). Thus a nonzero syntax/lint/selftest result (or missing selftest summary, recorded as nulls) can coexist with all suites valid, an empty `invalid_suites`, and exit 0. This is the round-17 open finding recorded at `corpus/lessons/round-17.md:65`. The schema documents `invalid_suites` as suite-only (`census/round-17/run-matrix.py:31-55`), so adding arm-health failures to that list without changing the schema would also misstate its contract.

**Smallest fix:** record and gate arm checks separately (including absent/malformed selftest output), add that result to the record, and make the runner nonzero if any required arm check fails; bump/document the record schema if its shape changes.

### High — The round-18 behavior is not selected by this matrix

Arm and suite inventory are hard-coded: `ARMS` contains pre-harm, r14-harm, and r16 only (`census/round-17/run-matrix.py:71-72`); `FIXTURES` contains only r17-hygiene, r15-config, and r14-namespace (`:73-78`). The run loop selects every mapping key for every arm (`:189-220`), but discovers no new suites. Therefore an r18 fixture for the per-repository watchdog/process-group guarantee is not exercised unless explicitly added, and there is no pinned r17 arm to compare with the r18 changed arm. The existing r17 fixture's FIFO case checks the older timeout behavior, not the new per-repository timeout/row contract.

**Smallest fix:** add an r18 fixture to `FIXTURES` with its selector and add the pinned r17 revision as an arm; keep the changed arm for the candidate. The printed/recorded arm and suite names should make those roles explicit.

### Medium — Arm bytes and recorded revision can identify different commits

For a non-`WORKTREE` arm, the tool bytes are fetched using the supplied symbolic revision at `census/round-17/run-matrix.py:200-202`, and that revision is resolved independently afterward at `:203`. If a branch/tag moves between those commands, the record's full `rev` can name a different commit from the commit that supplied the recorded `sha256`. The existing record schema explicitly associates `rev` and `sha256` for each arm (`:42-49`), so this breaks provenance.

**Smallest fix:** resolve the supplied ref once to a full commit OID, then use that same OID for both `git show` and the recorded `rev`.

### Medium — Case validation can accept malformed synthetic/duplicate rows

`suite()` stores parsed rows in a dict keyed by case ID (`census/round-17/run-matrix.py:113-122`), so duplicate IDs overwrite earlier rows. It then treats any `id-set` row as synthetic regardless of verdict (`:122-128`); it never requires that this reserved row be `FAIL`. A fixture output containing `CASE id-set PASS` plus a consistent passing summary can be marked valid, and duplicate output rows can be hidden by the dict. This weakens the schema's stated exact-row and synthetic-drift contract (`:14-23`).

**Smallest fix:** reject duplicate case IDs, require at most one `id-set` row and require it to be `FAIL`, and require exactly one well-formed summary line.

## Residual risk

`FIXTURES` is an explicit allowlist, which is deterministic and appropriate if updated for each new suite; it is not self-discovering. The record sample `census/round-17/c1-matrix-4f48343.json` has top-level `invalid_suites` but no separate invalid-arm-check field, consistent with the code path above.

## Verification gaps

Static review only; no matrix or fixture subprocess was run. `read xd://lsp` returned `No such tool` (lsp is not mounted), so there was no LSP status/references/diagnostics. Literal `grep` was used only to locate fixture subprocess/session calls, not as semantic proof.

Read-only evidence collected:
- `read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-17/run-matrix.py:1-132` and `:133-246` — arm map, suite map/parser, runner, gates, record schema.
- `read /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-17.md:60-72` — line 65 records the ungated checks as open.
- `grep 'subprocess\.(run|Popen)|start_new_session|setsid|killpg|timeout='` on the three named fixture files — r17 inner Popen uses a new session and killpg; r14/r15 census wrappers use `subprocess.run` timeouts.
- `read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-17/c1-matrix-4f48343.json?q=keys` — observed schema-2 top-level keys include `arms`, `invalid_suites`, and no invalid-arm-check field.
