STATUS: DONE — M1, M3, M4 and M6 have resolving committed evidence; M2 overstates r14 cleanup and its r15 red/green proof is L1-only; M5’s output is L1-only.

# R18-M1..M6 calibration review

**Attacked claim:** `corpus/lessons/round-18.md@5efb519`, `## Mistakes`, lines 15–20. Axis: calibration. Scope is the evidence pointers, capture attribution, and the asserted failure demonstrations; no lane files were changed and no lane code was executed.

## Findings

### MEDIUM — M2 incorrectly attributes session cleanup to the r14 fixture

`corpus/lessons/round-18.md:16` says the fix is session-wide SIGKILL “in the r14/r15/r17 fixtures and the r18 runner.” That is false for r14. `tests/fixtures/r14-census-boundary.py:391-402` calls `subprocess.run(..., timeout=90)` and on `TimeoutExpired` returns `Result(124, ...)`; it does not create a private session or kill/reap descendants. The file is byte-identical to b576341:

```text
sha256sum tests/fixtures/r14-census-boundary.py
  e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2
 git show b576341:tests/fixtures/r14-census-boundary.py | sha256sum
  e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2
```

By contrast, `tests/fixtures/r15-census-config.py:297-310,803-839` and `tests/fixtures/r17-census-hygiene.py:149-200,318-354` implement fixture-side session cleanup. `census/round-18/run-matrix.py:165-196` also cleans the matrix runner’s suite session, so a fixture invoked through that runner can be contained externally; that does not make r14 itself a session-cleaning fixture or establish the same behavior for a direct fixture invocation.

**Smallest fix:** qualify M2: r15/r17 use fixture-side cleanup; r14 remains pinned to b576341 and is only covered by the outer round-18 runner. Do not claim a direct r14 fixture fix.

### MEDIUM — M2’s `r15 2 → 0` demonstration is not in its cited evidence; `captured-by: none` is inaccurate

The linked `ScoutPyTimeoutLeak.md:1,29-46` attributes 44 observed processes to r15 and diagnoses the direct-child timeout behavior; `RevC3Premise.md:22-42` corroborates the 58 observed processes and their long-lived FIFO wait. Those reports are discovery evidence, so “none” at `corpus/lessons/round-18.md:16` does not describe who captured the mistake. The row should name the scout and premise review (or define `captured-by` as a prior automated control and use that meaning consistently).

There is a committed r17 forced-hang report: `.ufo/waves/round-18/w1/FixtureReapR17.md:22-50` gives base/patched commands and records 4 residue processes → 0. It is not linked from M2’s evidence-pointer cell, and its commands use temporary test-copy files (`:24-26,31,39`), so it is a committed narrative record rather than a self-contained checkout replay.

I found no committed output in the M2 pointers that shows the exact claimed **r15 base fixture 2 → fixed 0** result. The committed `census/round-18/c1-matrix-worktree.json:76-216` instead records 44 matching r15 PIDs remaining after the changed-arm suite (pre-existing residue) and `session_cleanup.killed: []`; it does not record the claimed per-run `2 → 0` delta. The exact r15 number is therefore **L1-asserted within the inspected evidence**, not independently substantiated by the cited record. The matrix’s 44 lingering PIDs must not be read as 44 new leaks from that suite, but they also are not a zero-residue result.

**Smallest fix:** link `FixtureReapR17.md` from M2; include a committed r15 red/green receipt or a complete reproducible command/result for the 2→0 claim; identify the scout/reviewer capture. Keep the observed 58-process inventory distinct from the fixture-specific test delta.

### LOW — M5’s `captured-by` omits the stated L1 discovery

`corpus/lessons/round-18.md:19` says the baseline command produced `KeyError: 'checked_measured'` and `rc 1` “(L1, `/var/tmp/souji-r18-L1int`)” but labels `captured-by` as `none`. The table’s own accompanying explanation only establishes that the earlier selftest did not exercise the CLI error path; it does not erase the L1 manual reproduction. The current selftest source adds `cli-unknown-rev-exit2` and `cli-bad-exemption-exit2` checks at `tools/souji-landing-gate.py:1390-1417`, but source presence is not a retained execution result.

The command is reproducible against a b576341 checkout (`python3 tools/souji-landing-gate.py --root <checkout-at-b576341> --rev deadbeef --round 17`), but the traceback/exit output is **only L1-asserted**: there is no committed output record among the cited paths. `stat -c '%F %n' /var/tmp/souji-r18-L1int` returned `directory /var/tmp/souji-r18-L1int`, not a committed transcript.

**Smallest fix:** change `captured-by` to “L1 manual CLI repro; prior selftest omitted this path,” and keep the claim identified as a reproduced command unless its output is committed.

## Pointer and demonstration audit

- **M1 holds on its stated seven gate findings.** The committed `census/round-18/gate-pointers-before-b576341.json:4-54` records seven dangling citations: SKILL.md twice, README once, and the knowledge entry four times. Its summary is 10 findings overall (`:78-90`), including two non-record paths and one frozen-measured finding. `RevengeDdb7347Pointers.md:53-70` gives the source inventory and R2 correction. The evidence/report paths resolve at 5efb519; the corrected `*-4f48343.*` records are present there. `git cat-file -e` confirmed the old `*-ddb7347.*` target paths are absent at both b576341 and 5efb519. The “7 citations” claim is accurate for the gate’s listed pointers; `RevengeDdb7347Pointers.md:55-62` separately notes historical `LOG.md:916`, which is not one of those seven findings and is handled by an append-only correction as `round-18.md:60` says.
- **M3 holds.** `census/round-18/jj-receipts-r18-baseb576341.txt:45` records J13 FAIL with `--as souji`; `jj-receipts-r18-changed.txt:45` records J13 PASS with `--as kama`. Both records are committed. The capture attribution to closure R1 resolves to `corpus/lessons/round-17-verifier-spotcheck.md:149`; the linked `RevengeRecipeAsSouji.md` is committed.
- **M4 holds.** In the committed matrix, r17-base B4 and B8 fail (`c1-matrix-worktree.json:1680-1683,1696-1699`), while the changed arm passes both (`:378-380,394-396`). The named ScoutOpenSites, ScoutWorktreeFifo and CriticRoundAdmission reports resolve at 5efb519 and support the broader-open-site and list-phase rationale. Capture attribution is consistent.
- **M6’s pointer and attribution resolve.** `MatrixR18.md:55-57` is an explicit self-disclosure naming the four pids; its session-only synthetic-child exercise is described at `:27-32`. `census/round-18/run-matrix.py:87-140,165-196` implements the session-ID-limited cleanup. The raw synthetic output is described in the committed report rather than linked as a committed JSON artifact; the incident itself remains a seat self-disclosure, as the table honestly states.

## Verification and residual risk

- All M1–M4 and M6 report/record paths named in the table were checked with `git cat-file -e` against 5efb519 and returned `PRESENT`. The corrected R17 record targets also returned `PRESENT`; the two old `-ddb7347` target paths returned `ABSENT` at both baseline and tip.
- `read xd://lsp` returned `No such tool: xd://lsp`; no LSP server/status was available. I used exact-file reads for evidence; literal grep was only a fallback locator, not semantic proof.
- No fixtures or gate commands were executed in this review. The baseline M5 output and M2’s specific r15 `2 → 0` output remain L1 assertions; M2’s r17 `4 → 0` has the separate committed FixtureReapR17 report. Matrix records and source support the M1/M3/M4 demonstrations; M6 is supported by its committed self-disclosure and test report.

**Verdict: PARTIAL.** M1, M3 and M4 meet the pointer and demonstration check; M6 has honest self-disclosure and a committed test narrative. M2’s r14 fix attribution is false, its r15 numerical red/green claim is not evidenced by the linked record, and its capture field omits the reports that found it. M5’s command is reproducible, but its reported failure output is L1-only and its capture field should name that repro.