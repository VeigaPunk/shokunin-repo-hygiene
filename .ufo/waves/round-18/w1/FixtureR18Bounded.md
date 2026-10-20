STATUS: DONE — Added the round-18 bounded-census falsifier and exercised all cases against the pinned base census.

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

Smallest integration requirement: the watchdog boundary must also cover the B8 list-phase config scan (and produce that repo's error row/diagnostic), not only work performed by `census_one`; B8 swaps config during `guard_git_config` before census row measurement begins. [INFERENCE] The repaired census behavior is not verified here because this seat ran only the pinned base revision; L1 should run this fixture against the integrated census after landing.

No tools were installed or updated.