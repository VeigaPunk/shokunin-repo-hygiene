# Round 9 — S17 fix implementor

Status: **S08's seven minimal repair proposals applied and verified on their demonstrated scenarios. Overall live-use safety remains BLOCKED by other fresh findings.** The required `sleep 600` completed (600.002 seconds) before consuming S08 evidence. The final formal handoff is `census/round-9/seat-08.json`.

Axes: fail-closed safety, fresh reproducibility, regression coverage, sibling-tool consistency. No numeric score or fleet-wide safety promotion is inferred.

## Confirmed defects and installed repairs

S17 freshly reran S08's complete 13-scenario audit against the canonical tools before editing: **7/7 claimed root causes reproduced, 0 NOT-REPRODUCED claims; 6 unsafe-authorization classes plus 1 distinct read-only-write class.** Same-target concurrency and interrupted-hold retention were passing controls, not defects. Evidence: `/var/tmp/souji-r9-s08-evidence.LAANXV/results.json`.

1. **S03-D1, failed Git queries become zero worktree commits:** both verification siblings now check pipeline status and emit `NOT-SAFE(git-unverifiable)` rather than `SAFE(metadata-prune)` after discovery loses Git. Quarantine inherits that refusal. Its pushed second-check history query is also explicitly status-checked.
2. **S03-D2, Turkish locale bypasses ID_* refusal:** both siblings export `LC_ALL=C`; quarantine already did. Reproduction uses a genuinely compiled Turkish locale and an empty aged directory, not a secret-shaped regular file.
3. **S04-F1, NUL erasure changes path/receipt authority:** quarantine scans the entire list for NUL before parsing or executing any row, then exits 2 on invalid bytes. Regression cases cover path NUL, receipt-pin NUL, and NUL after an otherwise valid prefix; no prefix is moved.
4. **S05-D1, default-origin receipt disappears during hold:** quarantine re-resolves the current default-origin ref and rechecks introducing-commit ancestry. Rollback or missing origin refs produce `ABORTED`, retaining staged bytes even if a backup remote keeps the broad any-remote query at zero.
5. **S06-D1, ancestor receipt destroys a nested dirty/unpushed repository:** both siblings refuse directory scopes containing nested `.git` entries, including gitfiles, and refuse scan failures. The scan also refuses a `.ufo` directory rather than traversing driver state/log surfaces. Original targets containing nested work remain untouched.
6. **S06-D2, supposedly read-only verification replaces the index:** both siblings export `GIT_OPTIONAL_LOCKS=0`, overriding a caller's optional-lock setting. Independent strace/index-hash checks now show no index.lock creation or index replacement. Census was a passing unchanged control.
7. **R9-S07-C01, captured ledger row survives receipt revocation:** source/vault checks pin the ledger content hash before row capture and compare it again before SAFE; quarantine performs the corresponding before/after comparison inside the second check. Changed/unhashable ledgers refuse or abort. File and directory-manifest paths have regressions.

The ledger fingerprint repair closes the demonstrated in-check atomic replacement schedule, **not arbitrary last-check-to-delete races or ABA changes**. Writer-coordinated locking/generation remains necessary for an atomic current-authority guarantee.

## Files changed

Only these repository paths were written by S17:

- `tools/souji-quarantine.sh`: NUL-list gate, default-ref re-derivation, checked history probe, ledger-drift gate, updated behavior description, expanded selftest. Removed the unused argument from an inherited malformed selftest printf without changing its assertion.
- `tools/souji-verify.sh`: locale/read-only exports, nested-scope refusal, checked worktree queries, ledger-drift gate, expanded selftest.
- `tools/souji-vault-verify.sh`: corresponding sibling fixes, startup ledger fingerprint and per-receipt validation, expanded selftest.
- `tools/souji-round9-selftest.sh`: shared Bash-only fixture regression runner; **must accompany the three tools for `--selftest`**. No production helper dependency was introduced.
- `census/round-9/fixes-17.md`: this assigned evidence fragment; parent integrates shared bookkeeping.

`tools/souji-census.sh`, historical implementations, S18's suffixed candidates, LOG.md and shared scorecards were not edited. All destructive calls and Git mutations were against new fixture repositories under `/var/tmp`; no live artifact was quarantined or removed, no forbidden live Git operation ran, and no GUI launcher was used.

## Selftests and independent end-to-end replay

All standard selftests were run again after the final code changes, with explicit fixture Git identities and `TMPDIR=/var/tmp`. Vault's default advisory executable was `/bin/false`; inherited honest/hanging/lying shims still exercised their intended cases.

| Tool | Baseline | Final | New regression checks |
|---|---:|---:|---:|
| souji-verify | 24/24 | **40/40** | 16 |
| souji-vault-verify | 35/35 | **51/51** | 16 |
| souji-quarantine | 63/63 | **91/91** | 28 |
| Total | 122/122 | **182/182** | 60 |

All three final commands exit 0. The 60 regression checks are not vacuous: run directly against S08's frozen original tools, the same runner exits 1 with **9, 9 and 22 failed assertions**, respectively. Those expected baseline failures are evidence, not current-deliverable test failures.

The Turkish locale source is optional for portability: an unavailable localedef/source produces an explicit SKIP and no credit for those two checks. **No skips occurred on this host**; locale activation and refusal both passed for all three tools.

Additional final checks, all exit 0:

- `bash -n` on all four changed shell files.
- `shellcheck -S error` on all four changed shell files.
- Full `shellcheck tools/souji-round9-selftest.sh` (the new helper is lint-clean).
- `git diff --check`.

Inherited warning-level ShellCheck findings remain in the three older tools; this is not a warning-free claim. The pre-existing SC2182 error was removed.

The exact independent S08 fixture functions were replayed against the installed final bytes with fixed-behavior/end-state assertions: **13/13 scenario groups pass**, including real hold-window ref mutation, scheduled in-check ledger replacement, strace, concurrent callers and SIGKILL preservation. Final proof directory: `/var/tmp/souji-r9-s17-final.Mv7VFi/`.

- `fixed.json`: complete post-fix independent records and final hashes.
- `replay_fixed.py`, `probe.py`, `peer_probes.py`: runnable independent replay; the latter two are extracted verbatim from S08's durable JSON fragment.
- `{verify,vault,quarantine}-selftest.log`: final standard suite output.
- `baseline-{verify,vault,quarantine}-regressions.log`: expected red runs against frozen vulnerable bytes.
- `residual-s18-battery.json`: separate broad residual-safety measurement.

Commands from the lane repository:

```bash
export GIT_AUTHOR_NAME=souji-selftest GIT_AUTHOR_EMAIL=souji-selftest@example.invalid
export GIT_COMMITTER_NAME=souji-selftest GIT_COMMITTER_EMAIL=souji-selftest@example.invalid
TMPDIR=/var/tmp bash tools/souji-verify.sh --selftest
TMPDIR=/var/tmp SOUJI_CLI_BIN=/bin/false bash tools/souji-vault-verify.sh --selftest
TMPDIR=/var/tmp bash tools/souji-quarantine.sh --selftest
python3 -B /var/tmp/souji-r9-s17-final.Mv7VFi/replay_fixed.py
```

Every replay builds fresh fixture roots. S08's original `run_adjudication.py` deliberately asserts vulnerable behavior and is not a green test suite for repaired tools.

## Counts and rubric verdicts

Within the **same S08 scenario universe**, before -> after:

- Direct verifier false-SAFE endpoint/scenario outcomes: **10 -> 0**.
- False-DELETE scenarios: **7 -> 0**.
- Propagated unsafe metadata SAFE/SKIPPED, without deletion: **1 -> 0**.
- Read-only index-write scenarios: **2 -> 0** (separate side-effect class, not false-SAFE/DELETE).
- Engine-to-engine safety verdict disagreements: **0 -> 0**; shared wrong verdicts explain why baseline agreement was not safety.
- Ancestor/descendant contradiction pairs: **4 -> 0**.
- Revoked-receipt/delete contradiction scenarios: **3 -> 0**.
- Malformed-list authorization contradiction variants: **2 -> 0**.

These are different, overlapping comparison units and must not be summed into unique defects or combined with another seat's denominator.

Rubric verdicts: fresh reproducibility **PASS**; S08 demonstrated-scenario remediation **PASS**; inherited positive-flow compatibility **PASS**; read-only inspection **PASS on measured probes**; calibration **IMPROVED by bounded disclosure, not numerically scored**; coverage **UNCHANGED at fleet level**; operability **IMPROVED for the repaired conditions**; arbitrary concurrent-writer atomicity **NOT PROVEN**; overall deployment safety **BLOCKED**.

## Remaining work / integration warning

A fresh run of S18's separate 37-check battery against canonical tools improved from **9/37 to 12/37**, with **28 -> 25 unsafe outcomes** and **0 positive-flow compatibility failures**. All six positive directory checks still pass. This battery is broader than S08's seven minimal proposals and is not a passed safety gate. Raw baseline: `/var/tmp/souji-r9-s17-baseline.mECtJL.json`; final: `/var/tmp/souji-r9-s17-final.Mv7VFi/residual-s18-battery.json`.

The remaining 25 outcomes comprise 18 false-SAFE engine outcomes and 7 unsafe quarantine deletions, including dirty/detached pushed content, incomplete directory receipt closure, hidden references, young descendants, tracked-to-stale fallback, unique detached-worktree history, self/missing-digest ledgers, quarantine symlink escape, TSV path injection and vault aliasing. These are explicitly **not fixed or cleared by S17**; S18 supplies an independent broader candidate set for parent integration.

Do not replace canonical tools wholesale with S18's older frozen wrappers without merging these S08 repairs, particularly the NUL-list and ledger-generation gates. Re-run both case universes on the final integrated bytes before any live-use clearance. No live removal is authorized by this fragment.

Final SHA-256:

```text
4baa8d955c531fcc73edc6b62021cb9531a31e1baed8aa853ba957b204d1cfc1  tools/souji-verify.sh
ea43bb0f9b9fe96cc26451df1a41d2df97d2d044852f122c987c209b6ec7b7a7  tools/souji-vault-verify.sh
f6f8516c15ab654f7e5f2dc2a7840eef0b53b9f9433e2ff70a64490b35fde68f  tools/souji-quarantine.sh
dd7c636ebe39e70c489516500440a311167b5280d18c3a5e9db1399d2f62e5c2  tools/souji-round9-selftest.sh
```
