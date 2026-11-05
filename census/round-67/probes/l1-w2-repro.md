# round-67 L1 pre-freeze probes (2026-11-05, host git 2.56.0)

L1 scratch: /fast/scratch/hyaku/souji-r67/l1/ (removed at landing). Lane base at probe time:
3639087917eaeb28719d7603110a6ec22782100e (master, clean, pushed; carries the round-66 landed
writer tools/souji-receipt-write.py, sha256 a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc).
These probes are feasibility measurements for the r67 matrix design; they are not claim evidence.
The frozen counters (census/round-67/c1-counter.py W1-W3, controls) carry the claim measurements.

## P1 — the r66 W2 route reproduces at the r67 base (base writer accepts a hidden mode change)

Fixture (scratch, Q4 shape): `git init` repo D; seed f.txt mode 755 tracked, instr.sh 755; commit;
chmod 644 f.txt (tracked mode change); cp -a D D-copy; `git -C D-copy config core.fileMode false`.

- `git -C D status --porcelain` → ` M f.txt` (visible without the redirect).
- Writer with `GIT_COMMON_DIR=<D-copy>/.git`, no `--allow-dirty`:
  `RECORD ... rc=0` — accepted, exit 0, receipt written (the dirty check read the redirected
  config and saw clean).
- Same run without the env var: `refused: lane worktree is dirty (git status --porcelain
  non-empty); pass --allow-dirty to override`, exit 2.

Conclusion: the r66 W2 named limit is live at the r67 base; the W1 row (redirect + mode change +
no --allow-dirty → base accept / candidate refuse RECEIPT-ENV-COMMONDIR-MISMATCH) is realizable.

## P2 — GIT_DIR and GIT_WORK_TREE are NOT open routes at the base

With `GIT_DIR=<D-copy>/.git` (same copy, same hidden mode change) the base writer refuses dirty
(rc 2); with `GIT_WORK_TREE=/home/vgpnk/Projects/shokunin` likewise rc 2. Mechanism: the writer's
git-call env builder scrubs both names on every call (`tools/souji-receipt-write.py` line ~91:
`env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE") ...}`).
GIT_COMMON_DIR is not in that scrub list — that is the r67 candidate's second delta (refuse on
mismatch at writer start, scrub on every git call).

## P3 — equal-value GIT_COMMON_DIR is honest (no-trade row W3)

`GIT_COMMON_DIR=$(git -C D rev-parse --git-common-dir | realpath)` with a clean tree: writer
accepts rc 0 on the base slot (the C1 control's W3 row shows base_honest including W3). The
candidate's value-aware comparison must keep this accepted (Q22: a harmless, already-neutralized
value must not abort).

## P4 — the first M10-bound selftest case was vacuous (caught pre-freeze, fixed in the counter bytes)

The first draft of `m10-s5-assertion-line-not-live` used the `redirects_closed` claim on a writer
stub with no cdred marker: the finding fired on the absent cdred regardless of the token rule, so
the reverted-rule mutant still passed --selftest 17/17 — the exact vacuity class of the r66 M4
case, produced fresh by this lane. Caught by running the c2-mutate.py reverted-rule recipe before
any commit (mutant selftest EXIT=0 with the draft). Fix: the frozen case binds claim `env_closed`
(needs only envcfg+envred, the two markers the stub bears). Measured on the frozen bytes:
repaired --selftest EXIT=0 (17/17); reverted-rule mutant `--selftest` prints
`SELFTEST-CASE m10-s5-assertion-line-not-live: findings=0 want=1 MISMATCH`, `pass cases=17 fail=1`,
`EXIT=1`. Mined as round-67 M-row material (captured-by: none — the catch was the recipe run, a
process the r66 round did not run for its own case).

## P5 — C2 target derivation against the pinned state (sanity; the receipt rerun lands in records/)

Population census/round-67/c2-statements.tsv (this round's instruments commit), SKILL.md and
writer bytes at c13fbb4e1b563a78278ddc14316c20252e9a6d8d (pinned historical state):
the r67 counter must print exactly `FINDING SCOPE-OVERREACH s5 ...`, `SUMMARY rows=5 findings=1
verdict=FAIL`, `EXIT=1`; the round-66 counter (frozen bytes ac2157e6..., r66 population at
4576f101...) prints `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0` on the same state.
Both runs' committed receipts bind these literals.
