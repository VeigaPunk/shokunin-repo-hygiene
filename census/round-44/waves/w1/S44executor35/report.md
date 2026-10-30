# S44executor35 — C3 hardlink-input envelope probe

Axes: calibration / operability / coverage. This probe addresses coverage of the hardlink-input refusal contract; no numerical axis delta claimed.

## Scope and evidence

Read the frozen round-44 preregistration, C3 counter description, `tools/souji-worktree-drift.py` JSON refusal contract, and the r38 fixture's hardlink cases. The contract documents that `--json` aliasing the `--record` input by inode is refused as `JSON-IS-RECORD`, protecting record bytes. A separate output-hardlink case refuses with `JSON-HARDLINKED`.

Ran the actual r38 fixture against tool bytes extracted from the two named revisions. `base-r38.out` and `frozen-r38.out` retain the complete stdout; `commands.txt` records revisions and invocations.

Base command (tool at `55d7af6f5a22340f7a3de1c386e514ababfaa75f`):
`python3 -B r38-fixture.py --tool base-tool.py --work base-work --base-tool base-tool.py`
Observed fixture result: `SUMMARY cases=12 pass=11 fail=1 base_cases=12 base_fail=1 behavioral_fail=1`; failure was solely `json-symlink-refused` (`rc=0 resolved_written=True exists=True`). Within that run, `case-record-hardlink-refused=PASS` and `case-json-hardlinked=PASS`.

Frozen command (tool at `d314fd6e85d62565344fa6c4b102f52f62297884`):
`python3 -B r38-fixture.py --tool frozen-tool.py --work frozen-work --base-tool base-tool.py`
Observed process exit 0 and `SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=1 behavioral_fail=1`. Both hardlink cases remained `PASS`; the symlink case changed to `PASS` against frozen tool while the base comparison still reports the expected symlink behavioral failure.

The input-hardlink scenario creates a hardlink to the record and passes it as `--json`; fixture assertions require exit 2, `JSON-IS-RECORD`, and unchanged original record bytes. The output-hardlink scenario requires exit 2 and `JSON-HARDLINKED`. Their PASS results establish both documented refusals and no record-input overwrite for this fixture. The JSON output contract also retains its success behavior: `case-json-written-regular=PASS` (regular output gets valid JSON with summary `record_repos == 1`).

## Finding / limitation

No observed behavior change in hardlink-input or hardlinked-output cases between base and frozen tool. The r44 cutover affects the leaf-symlink case, not these hardlink cases. Evidence is the bounded 12-case r38 fixture, not a full C3 counter run. Tool version/install: none. Scratch was removed; retained artifacts are `base-r38.out`, `frozen-r38.out`, and `commands.txt` alongside this report.
