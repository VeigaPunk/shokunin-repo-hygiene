STATUS: DONE — Extended the bounded-census fixture through B12 against the refreshed 5efb519 snapshot; retained B1–B8.

## Axes

Operability is primary; the fixture also supplies calibration evidence for the timeout claim and coverage for status, attribute, config, ignore, and protected-path reads.

## Files and behavior

- Added only `tests/fixtures/r18-census-bounded.py` in `/var/tmp/souji-r18-FixtureR18Bounded/lane`.
- Delivered the scoped patch at `.ufo/waves/round-18/w1/FixtureR18Bounded.patch` (SHA-256 `3ae7ec936c433c1be96248239a32225d2b89baccca641d2f4c891a9ef1266879`, 49,632 bytes).
- The fixture supports `--census`, `--list`, `--json`, and repeatable debug-only `--case`. `EXPECTED_IDS` is B1–B8 (`tests/fixtures/r18-census-bounded.py:32`); the case definitions are at lines 814, 849, 886, 927, 1010, 1046, 1057, and 1067.
- Each census Popen uses `start_new_session=True` (`:486-517`) with a 40-second fixture deadline. On timeout it returns rc 124 as FAIL and SIGKILLs the private session's process groups by repeatedly rescanning `/proc/<pid>/stat` session/PGID fields (`:434-484`). B6 verifies that no census session processes remain and that each read-side FIFO has no reader via `O_WRONLY|O_NONBLOCK` → ENXIO (`:699-739`, `:1046-1055`).
- B1 injects `info/attributes` as a FIFO on the `status` call after the metadata guard and touches a tracked file; B2 performs the same swap on `check-attr` with a bound `filter.r18.clean` and `.gitattributes`; B3 swaps `.git/config` at the post-guard `status` call; B4 exercises independent static work-tree `.gitignore` and `.gitattributes` FIFOs without a swap; B5 sleeps two seconds in every Git shim call with a 30-second repo bound; B7 checks protected-namespace exit 2; B8 swaps `.git/config` from a PATH `cmp` shim during the list-phase config scan. Every injected case checks exact expected row classes and compares healthy `a`/`c` rows with a no-shim control. The bound is passed through `SOUJI_CENSUS_REPO_TIMEOUT` only, not a CLI option (8 seconds except B5's explicitly requested 30 seconds).

## Retained evidence

Base census extraction:

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tools/souji-census.sh > /var/tmp/souji-r18-FixtureR18Bounded/base-census.sh && sha256sum /var/tmp/souji-r18-FixtureR18Bounded/base-census.sh
006b98231f8d138b3bb13595cc3f9cd9133247d2e88b4683140735ca0759e9fd  /var/tmp/souji-r18-FixtureR18Bounded/base-census.sh
```

The selected revision command returned `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` for the clone's `HEAD`.

```text
PYTHONPYCACHEPREFIX=/var/tmp/souji-r18-FixtureR18Bounded/pycache python3 -m py_compile /var/tmp/souji-r18-FixtureR18Bounded/lane/tests/fixtures/r18-census-bounded.py
```

Observed: exit 0, no output. The same command was run after the final fixture edits.

```text
python3 /var/tmp/souji-r18-FixtureR18Bounded/lane/tests/fixtures/r18-census-bounded.py --list
B1
B2
B3
B4
B5
B6
B7
B8
```

Pinned-base runs (all use the extracted base census above):

| Exact command | Observed output | Verdict |
|---|---|---|
| `python3 /var/tmp/souji-r18-FixtureR18Bounded/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18Bounded/base-census.sh --case B1 --case B6 --json` | `CASE B1 FAIL`, expected census exit 0, observed fixture rc 124; `CASE B6 PASS`; `SUMMARY total=2 failed=1`. JSON retained the status-shim trigger. | Base falsifier red as required; cleanup holds. |
| `python3 /var/tmp/souji-r18-FixtureR18Bounded/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18Bounded/base-census.sh --case B2 --case B6 --json` | `CASE B2 FAIL`, expected exit 0, observed rc 124; control row `b` was `status-unverifiable`; B6 passed; summary failed=1. JSON retained the `check-attr` trigger. | Base falsifier red as required; cleanup holds. |
| `python3 /var/tmp/souji-r18-FixtureR18Bounded/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18Bounded/base-census.sh --case B3 --case B6 --json` | `CASE B3 FAIL`, expected exit 0, observed rc 124; JSON recorded `post_guard_status_hung: true` and the status-shim event; B6 passed; summary failed=1. | Post-guard config read is demonstrated on base; cleanup holds. |
| `python3 /var/tmp/souji-r18-FixtureR18Bounded/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18Bounded/base-census.sh --case B4 --case B6 --json` | `CASE B4 FAIL`, observed rc 124 for both independent static FIFOs; JSON recorded `base_hangs_on_ignore_fifo: true` and `base_hangs_on_attributes_fifo: true`; B6 passed; summary failed=1. | Both base hangs reproduced; cleanup holds. |
| `python3 /var/tmp/souji-r18-FixtureR18Bounded/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18Bounded/base-census.sh --case B5 --case B6 --json` | `CASE B5 PASS`, exit 0, one clean `slow` row, 13 Git shim calls, elapsed `26.325s` (<30s); B6 passed; `SUMMARY total=2 failed=0`. | Slow finite repo is measured, not killed. |
| `python3 /var/tmp/souji-r18-FixtureR18Bounded/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18Bounded/base-census.sh --case B7 --case B6 --json` | `CASE B7 PASS`, exit 2, no rows, stderr `souji-census: path-protected: credential-store (input: <protected>)`; B6 passed; `SUMMARY total=2 failed=0`. | Protected refusal preserved. |
| `python3 /var/tmp/souji-r18-FixtureR18Bounded/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18Bounded/base-census.sh --case B8 --case B6 --json` | `CASE B8 FAIL`, expected exit 0, observed rc 124; JSON retained the `cmp` event for `b/.git/config`; B6 passed; summary failed=1. | List-phase base falsifier red as required; cleanup holds. |

For each invocation, `B6 PASS` means the fixture found no process remaining in any census session and every registered FIFO probe returned ENXIO. Each FIFO case also validates that timeout rc 124 is a failure, not a skip. No processes were left by the fixture.

Relevant pinned-source evidence: `tools/souji-census.sh:546-585` guards fixed Git metadata; `:902-915` calls `guard_git_files` before `guard_git_config`; `:695-701` reads `.git/config` with `tr | cmp` during that guard; and `:1122-1129` invokes `git status` after the guard. These call sites explain B3 and B8's timing. B1/B2 trigger at `status`/`check-attr`, respectively, after the pre-access guard. B4's status read of work-tree ignore/attribute sources is confirmed by the two observed base timeouts.

An initial full-suite attempt exposed a fixture wiring defect: B1–B3 had not installed their Git shim, and non-FIFO candidate paths were incorrectly retained as FIFO resources. That attempt reported `SUMMARY total=7 failed=7`; it is not used as acceptance evidence. The fixture was corrected to install each shim and register only actual FIFOs, then the final per-case commands above were run.

## Verdict, fix, and residual risk

The pinned base fails B1–B4 and B8 by the outer 40-second timeout, as expected. B5 and B7 preserve their required behaviors, and B6 confirms cleanup after each tested case. The fixture checks the planned repaired contract: a timed-out repository emits its exact zero-valued `error` row, `repo-timeout 8s <repo>` diagnostic, and leaves neighbors equal to their no-shim control.

For the initial b5763415 phase, the smallest integration requirement was to cover B8's list-phase config scan, not only `census_one`. [Historical] That positive behavior was not tested against the b5763415 revision; the refreshed 5efb519 results below now exercise the integrated snapshot.

No tools were installed or updated.

## Refreshed W2 coverage (5efb519)

The updated clone is `/var/tmp/souji-r18-FixtureR18BoundedFix/lane` at `5efb519f00075d958c3d1109ef6fcb24c487eb87`. The extracted census SHA-256 is `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`. The fixture now creates a unique private scratch root per invocation with `tempfile.mkdtemp(prefix="souji-r18-FixtureR18Bounded.", dir="/var/tmp")`; B6 runs a real census before residue assertions, including when selected alone.

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5efb519f00075d958c3d1109ef6fcb24c487eb87:tools/souji-census.sh > /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh && sha256sum /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh
7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd  /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh
```

Added:

- B9: a Git shim blocks in `status` and handles SIGTERM without exiting. The 5efb519 census returned the exact `target` error row in 10.223s; the shim received SIGTERM and was killed 2.085s later. B6 passed.
- B10: sends SIGTERM and SIGKILL to the census supervisor PID only while the Git shim is blocked. Python observed SIGTERM returncode `-15` (shell status 143); the supervisor exited but left the worker/watchdog session alive. The fixture detected the stalled Git PID, then reaped the session. The SIGKILL arm returned `-9` and had no session processes after the 8s bound plus 2.5s observation window. B10 correctly fails on 5efb519; B6 passed after cleanup.
- B11: passes root and compare paths with a trailing newline whose newline-stripped prefixes are valid siblings. On 5efb519 the root arm returned 0 and measured the sibling; the compare arm returned 3 and emitted a diff instead of exit 2. B11 correctly fails.
- B12: creates a registered linked-worktree `.git` gitfile at `b` (owner hidden from the top-level scan), then swaps it to a FIFO after `list_repos` classifies the candidate but before its guard. It checks the timeout diagnostic, required `b` error row, and measured `a`/`c` neighbors. The 5efb519 snapshot emitted the diagnostic and measured `a`/`c`, but omitted `b` because preflight timeout row mapping covered only kind `repo`. A second B12 arm checks that an included root already in REPOS gets exactly one error row; it passed on 5efb519. A plain-path candidate is included and must remain absent from census rows.

Exact commands and observed results on the extracted 5efb519 census:

```text
python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh --case B1 --case B2 --case B3 --case B8 --case B6 --json
CASE B1 PASS; CASE B2 PASS; CASE B3 PASS; CASE B8 PASS; CASE B6 PASS
SUMMARY total=5 failed=0

python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh --case B4 --case B6 --json
CASE B4 PASS; CASE B6 PASS
SUMMARY total=2 failed=0

python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh --case B5 --case B6 --json
CASE B5 PASS; CASE B6 PASS; 13 Git calls at 2s each; elapsed=26.474s (<30s)
SUMMARY total=2 failed=0

python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh --case B7 --case B6 --json
CASE B7 PASS (exit 2, path-protected); CASE B6 PASS
SUMMARY total=2 failed=0

python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh --case B9 --case B6 --json
CASE B9 PASS; CASE B6 PASS; elapsed=10.223s; SIGTERM-to-SIGKILL=2.085s
SUMMARY total=2 failed=0

python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh --case B10 --case B6 --json
CASE B10 FAIL (TERM arm leaves worker/watchdog after parent exit; KILL arm clear after bound+2s); CASE B6 PASS
SUMMARY total=2 failed=1

python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh --case B11 --case B6 --json
CASE B11 FAIL (root arm exit 0; compare arm exit 3, both expected 2); CASE B6 PASS
SUMMARY total=2 failed=1

python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh --case B12 --case B6 --json
CASE B12 FAIL (gitfile preflight emitted rows a,c, omitted required b error row; included-root arm emitted exactly one error row); CASE B6 PASS
SUMMARY total=2 failed=1

python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18-FixtureR18BoundedFix/census-5efb.sh --case B6 --json
CASE B6 PASS; one real clean census row; SUMMARY total=1 failed=0
```

Final fixture syntax check:

```text
PYTHONPYCACHEPREFIX=/var/tmp/souji-r18-FixtureR18BoundedFix/pycache python3 -m py_compile /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py
```

Observed: exit 0, no output. `--list` returned B1–B12.
The exact listing command was:

```text
python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py --list
B1
B2
B3
B4
B5
B6
B7
B8
B9
B10
B11
B12
```

Delivered the updated patch at `.ufo/waves/round-18/w1/FixtureR18BoundedFix.patch` (SHA-256 `95ea0fad383eb2cbc83c4293dbb5d1ce593da953a44e2f009a4d338180eb11d5`, 26,260 bytes), diffed against 5efb519.

The mounted tools expose no LSP interface, so no LSP lookup/refactor was available. No tools were installed.

## W2 integration findings

- B10: smallest fix is to make the SIGTERM parent path synchronously stop and reap the active worker and watchdog before the census parent exits. The TERM arm returned -15 but retained the worker session after the parent exited; the SIGKILL arm was clean by the repo bound plus two-second grace.
- B11: reject the raw input string before line-based normalization for both `--root` and `--compare`; otherwise a trailing newline is stripped and selects the valid sibling.
- B12: map a timed-out `gitfile` preflight candidate to its sanitized error row and timeout diagnostic, while avoiding duplicates for paths already in REPOS and keeping `path`/plain candidates diagnostic-only.

Pinned-source anchors explain these findings: `tools/souji-census.sh:278-295` normalizes with a line-oriented `read`, while `:453-461` checks newline only after normalization; `:1425-1427` classifies `.git` file candidates as `gitfile`; `:1677-1680` records a preflight error row only for `kind=repo`; `:1691-1695` emits rows from REPOS. The included-root no-duplicate control covers `:1397-1404`. For B10, `:1477-1503` starts worker/watchdog groups and `:1495-1498` sends TERM then KILL after two seconds; the observed parent-TERM leak is consistent with parent EXIT cleanup at `:232-242` only removing the temporary directory. [INFERENCE] Adding explicit parent-signal lifecycle cleanup is the narrowest repair consistent with the captured B10 behavior.

Fixture source anchors: B1–B12 are pinned at `tests/fixtures/r18-census-bounded.py:32`; unique per-invocation scratch roots are created at `:114-118`; every census Popen starts a session at `:572-574`; the external-signal runner is at `:663-815`; B6 executes a census at `:1256-1268`; B9–B12 are at `:1319-1564`; and raw duplicate-row checks use `raw_repo_names` at `:1675-1684`.

All four new cases are retained as measured falsifiers on 5efb519; this seat changed only the fixture file.