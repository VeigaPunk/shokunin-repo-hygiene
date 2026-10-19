# S18 — independent hardening implementation

Axes: false-SAFE/DELETE prevention; preservation-receipt continuity; fail-closed parsing and filesystem containment; compatibility. Lane rubric: calibration and operability improved on the measured fixture battery; fleet coverage unchanged. No numerical score assigned.

## Result

**15 freshly scripted adversarial families, 31 tool-case checks: 28 unsafe baseline outcomes (20 false-SAFE, 8 false-DELETE), 3 correct refusals. S18 candidates: 31/31 correct refusals, zero unsafe outcomes.** Six additional positive directory checks pass, including real pushed-directory and stale-directory deletion flows. All 122 inherited selftest assertions pass (24 + 35 + 63).

Cross-engine contradictions: **2 -> 0** on 11 adversarial pairs (legacy verifier accepts a self-copy ledger row and a missing directory-vault digest; vault verifier refuses both). Consumer/authority contradiction: **1 -> 0** (tab-containing pathname forges SAFE/stale inside quarantine's TSV parser although the engine's actual verdict is NOT-SAFE). These are counts within this battery, not fleet-wide claims.

Installed tools were NOT replaced. S18 uses independent suffixed candidates so S17 can work without shared-file races. The installed verify/vault/quarantine/census SHA-256 values remain identical to this seat's initial snapshots.

## Fresh confirmed cases

Each row is a separate fixture construction in `tools/souji-round9-s18-test.py`, run again against frozen original bytes and then S18 candidates. “Both” means verify and vault-verify.

| Fixture family | Fresh original outcome | S18 outcome |
|---|---|---|
| `dirty-pushed` | Both SAFE/pushed for uncommitted changed bytes | Both NOT-SAFE |
| `detached-unpushed` | Both SAFE/pushed for a detached-only modifying commit | Both NOT-SAFE; HEAD participates in unpushed history |
| `directory-untracked-child` | Both SAFE/pushed although a child has no remote copy; quarantine correctly refuses | Both NOT-SAFE; quarantine still refuses |
| `directory-ignored-child` | Both SAFE/pushed; quarantine DELETED an ignored sole-copy child | Both NOT-SAFE; source retained |
| `hidden-live-reference` | Both SAFE/stale; quarantine DELETED despite `.active-reference` | Both NOT-SAFE; source retained |
| `stale-directory-fresh-child` | Both SAFE/stale; quarantine DELETED a recently written descendant | Both NOT-SAFE; source retained |
| `stale-unpushed-fallback` | Both SAFE/stale after rejecting the pushed receipt; quarantine DELETED committed local-only content | Both NOT-SAFE; no tracked-to-stale fallback |
| `worktree-unique-detached-head` | Both SAFE/metadata-prune: `--all` includes the very worktree HEAD being tested | Both NOT-SAFE, `unique=1`; compare against durable refs only |
| `worktree-invalid-head` | Both SAFE/metadata-prune: failed git history command becomes a zero line count | Both NOT-SAFE/history-unverifiable |
| `ledger-self-copy` | Legacy SAFE/moved-to-obsidian for the only copy; vault verifier correctly refuses | Both refuse |
| `ledger-missing-vault-directory-digest` | Legacy SAFE/moved-to-obsidian with no vault digest and an empty vault directory; vault verifier correctly refuses | Both refuse |
| `quarantine-root-symlink` | DELETED through `.ufo-quarantine -> outside`, creating fixture paths outside the repository | NOT-AUTHORIZED/containment; source retained and outside directory empty |
| `tab-path-verdict-injection` | A fresh non-scratch file named `fresh<TAB>SAFE<TAB>stale<TAB>no-receipt.txt` is DELETED with no actual receipt | NOT-AUTHORIZED before engine invocation; source retained |
| `default-receipt-revoked-during-hold` | DELETED after origin's default ref is replaced with an unrelated root while another remote keeps the commit reachable | ABORTED/default-ancestry=FAIL; staged bytes retained |
| `vault-replaced-with-quarantine-alias` | DELETED after the vault file becomes a symlink to the staged sole copy | ABORTED; nonindependent row rejected and staged bytes retained |

The all-empty directory-digest row initially tried was **NOT-REPRODUCED**: TSV whitespace collapse already caused refusal. The distinct missing-*vault*-digest case above was freshly reproduced and is counted. Initial quarantine runs from copied tools hit their recalculated `/var/tmp` live-root guard and were not counted as defects; the final harness explicitly permits only its own asserted `/var/tmp` fixture repositories.

## Files and patch shape

All paths below are relative to `souji-shokunin/`; these are the only repository files written by S18:

- `tools/souji-guard.r9-s18.sh`: shared late-loaded overrides. Literal Git pathspecs and optional-lock suppression; protected/control/symlink path refusal; strict complete independent ledger rows; current default-ref snapshot and target-cleanliness checks including ignored files; detached-HEAD history; hidden/binary-safe live-reference sweeps excluding protected surfaces; recursive directory ages and per-descendant references; checked worktree graph queries against durable refs; strict exact-path/single-record quarantine parsing; quarantine ancestor containment; post-hold default-ref/object/ancestry and vault independence checks.
- `tools/souji-verify.r9-s18.sh`: frozen verify candidate, delegates safety rules to the guard, preserves built-in tests and output contract.
- `tools/souji-vault-verify.r9-s18.sh`: corresponding vault candidate, preserves advisory CLI behavior and refusal vocabulary.
- `tools/souji-quarantine.r9-s18.sh`: corresponding quarantine candidate, defaults to the S18 verifier; preserves real move/hold/recheck/delete flow and tests. An inherited malformed selftest `printf` was corrected without weakening its assertion.
- `tools/souji-round9-s18-test.py`: reproducible fixture builder, attack/compatibility battery and JSON evidence. It asserts fixture containment before setting the copied-tool live-root override. Git mutations are fixture-only plumbing; no fetch/push/commit/branch operation.
- `census/round-9/fixes-18.md`: this evidence/handoff.

`tools/souji-census.sh`, shared bookkeeping, live lane contents, secret-shaped files and `.ufo` driver state/logs were not modified. The candidate runtime guards are loaded after inherited function definitions; **the guard must ship alongside all three candidates**.

## Reproduction and verification

From the lane repository, this builds NEW fixtures each time (all fixture roots are created under `/var/tmp`):

```bash
freeze=$(mktemp -d -p /var/tmp souji-r9-s18-original.XXXXXX)
cp tools/souji-{verify,vault-verify,quarantine,census}.sh "$freeze/"
python3 tools/souji-round9-s18-test.py --tool-dir "$freeze" --suffix '' --observe
python3 tools/souji-round9-s18-test.py
TMPDIR=/var/tmp bash tools/souji-verify.r9-s18.sh --selftest
TMPDIR=/var/tmp bash tools/souji-vault-verify.r9-s18.sh --selftest
TMPDIR=/var/tmp bash tools/souji-quarantine.r9-s18.sh --selftest
for f in tools/souji-{guard,verify,vault-verify,quarantine}.r9-s18.sh; do bash -n "$f" || exit; done
shellcheck -x -S error -P tools tools/souji-{verify,vault-verify,quarantine}.r9-s18.sh
```

Measured final run: baseline **9/37 pass**, 28 false-SAFE/DELETE, 0 compatibility failures; S18 **37/37 pass**, 0 false-SAFE/DELETE, 0 compatibility failures. All negative verifier results are valid JSON/NOT-SAFE with exit 0; all nine negative quarantine flows exit 3 and preserve original or staged bytes. Positive directory flows exit 0 and actually delete only staged copies. Built-in selftests: **24/24, 35/35, 63/63**, all exit 0. Four `bash -n` checks and error-severity ShellCheck pass. This is not a claim of warning-free ShellCheck: inherited/shared-variable warnings remain.

Captured final output directory: `/var/tmp/souji-r9-s18.ewsExS/` (`baseline.json`, `hardened.json`, `verify-selftest.log`, `vault-selftest.log`, `quarantine-selftest.log`). Fresh final fixture roots: baseline `/var/tmp/souji-r9-s18-battery.z1socmqv`; candidate `/var/tmp/souji-r9-s18-battery.5f3eantb`. Retained fixtures are evidence, not live repositories.

Original SHA-256 prefixes, unchanged at final verification: verify `a91049c96e5f`, vault `53f92421b254`, quarantine `5780ad751aa4`, census `11bf9cdf8d4f`. Candidate prefixes: guard `3b06a946d731`, verify `bab5942543de`, vault `f135f5ad7738`, quarantine `45335ff5ca66`, battery `03319ac9982b`.

## Rubric / handoff

- Fresh reproduction: **MET** for all 15 counted families; unconfirmed/all-empty-row hypothesis explicitly excluded.
- Candidate safety improvement: **MET on the measured battery** (28 unsafe outcomes eliminated, 0 remaining there).
- Compatibility/non-harm: **MET on 122 inherited assertions + 6 positive directory checks**; no general security proof implied.
- Calibration: **IMPROVED** (two engine contradictions and one parser/authority contradiction closed in S18 candidates).
- Operability: **IMPROVED** (all measured valid flows preserved; structured fail-closed refusals for reproduced attacks).
- Fleet coverage: **UNCHANGED / not exercised**; no fleet mutation or fleet-wide counter change claimed.
- Installation/integration: **PENDING parent selection**. Do not overwrite S17's work or mark installed safety fixed merely because this candidate passes. Census hardening, full hostile-filesystem atomicity and exhaustive concurrent-race testing are outside this seat's verified deliverable.
