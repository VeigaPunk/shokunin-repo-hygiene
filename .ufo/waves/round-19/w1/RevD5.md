STATUS: DONE — D5 is a bounded stale-PID-risk reduction; its remaining signal races must stay disclosed, and fixture output contracts are unchanged.

# Findings

- **Low, non-blocking — per-PID TOCTOU remains.** Yes: each helper reads `/proc/<pid>/stat` to capture `(session,starttime)`, rereads it, then calls `os.kill(pid, SIGKILL)` as a separate operation. A process can exit and that PID be reused after the second read but before `kill`; the tuple check narrows the interval, not atomically binds the signal target. For normal use this is cleanup of a fixture-created session (`start_new_session=True` in both wrappers), so **[INFERENCE]** the residual is not a material routine operability hazard for the fixture-owned worker. It is still possible under PID churn and is not an absolute no-collateral-signal guarantee.
- **Residual disclosure — process-group signal is outside the recheck.** Both helpers also call `os.killpg(session_id, SIGKILL)` after the per-PID loop. That operation has no `(pid,starttime)` validation; ordinarily it targets the fixture's original process group, but a stale/reused group ID is not ruled out if the original group has disappeared before that call. Do not describe the member recheck as protecting all cleanup signals.
- **No fixture output-contract change in the diff.** The edits are confined to process identity parsing and timeout cleanup in the two fixture helpers. The `EXPECTED_IDS` declarations remain the same (`R15CFG-*` and `R17-*`); their `SUMMARY total=… failed=…` emission remains unchanged. Thus IDs and summary shape are unchanged. Fixture runs were not performed, so dynamic `failed` counts—especially if a timeout occurs—are not asserted.

**Minimal safe wording:** “The helper snapshots each session member's `(pid,starttime)`, rereads `/proc` immediately before `os.kill`, and skips a missing or mismatched member; this narrows but does not close the check-to-signal PID-reuse race. The subsequent `killpg(session_id, SIGKILL)` is a separate, unguarded cleanup signal.” Avoid saying that every recycled PID is necessarily skipped or that the tuple guarantees identity.

# Evidence

- `tests/fixtures/r15-census-config.py:269-312` — parses session plus field-22 starttime, captures members, rechecks before `os.kill`, then calls `os.killpg`; `:315-329` — timeout wrapper starts a new session and invokes cleanup.
- `tests/fixtures/r17-census-hygiene.py:151-194` — same snapshot/recheck/per-PID signal and following group signal; `:199-224` — timeout wrapper uses `start_new_session=True` and invokes cleanup.
- `tests/fixtures/r15-census-config.py:129-151` and `tests/fixtures/r17-census-hygiene.py:73-79` — pinned expected case-id declarations; `r15-census-config.py:1610` and `r17-census-hygiene.py:1335` — unchanged SUMMARY emitters.
- `git diff 3ab2c81 -- tests/fixtures/r15-census-config.py tests/fixtures/r17-census-hygiene.py` — only the two process-cleanup implementations changed; no case-id or SUMMARY-emitter hunk.
- LSP was unavailable in the mounted toolset: `read xd://lsp` returned “No such tool.” The source review is based on the actual diff and file reads; text search was used only to locate relevant declarations, not as semantic proof.

# Commands run

- `git status --short && git diff --name-only 3ab2c81`
- `git diff --unified=5 3ab2c81 -- tests/fixtures/r15-census-config.py tests/fixtures/r17-census-hygiene.py`
- `git diff --unified=0 3ab2c81 -- tests/fixtures/r15-census-config.py tests/fixtures/r17-census-hygiene.py`
- Text searches for `kill_session`, `starttime`, `EXPECTED_IDS`, and fixture case/summary markers, followed by targeted source reads.
- No fixtures, tests, census commands, or live-process probes were run.

# Contract compliance

Read `/home/vgpnk/.omp/agent/RULES.md` first. Read-only review; no subagents, installs, network access, live `/proc` reads, signals, or git/jj mutations. Wrote only this assigned report. No checks were run; summary counts are therefore unverified.