# S44executor65 — C3 frozen counter run

Axes: calibration / operability / coverage. Assignment: coverage; no source or counter changes made.

## Commands and retained receipts

Run from fleet-root process context (all command paths absolute); both invocations used `python3 -B` and the assigned scratch directory:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor65
```

Observed stdout: `SUMMARY surface=ok tool_class=ok legacy=ok legacy_case=ok legacy_base=ok battery=ok battery_clean=REJECTED battery_refuse=REJECTED prior=5/5`; exit 0. Exact stdout/stderr/exit are in `c3.stdout.txt`, `c3.stderr.txt`, `c3.exit.txt`.

Missing-instrument control:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 55d7af6f5a22340f7a3de1c386e514ababfaa75f --scratch /fast/scratch/hyaku/souji-r44/S44executor65
```

Observed stdout: `SUMMARY surface=RED tool_class=RED legacy=ok legacy_case=RED legacy_base=RED battery=RED battery_clean=RED battery_refuse=RED prior=5/5`; exit 1. Exact output retained in `missing-fixture.stdout.txt`, `missing-fixture.stderr.txt`, `missing-fixture.exit.txt`. This is the registered base/do-nothing revision, not a fabricated missing-file mutation; counter code checks fixture blobs at `--rev`, so absent r44 battery yields RED. Notably `prior=5/5` remains green at base because the five prior fixture suites and their pinned behavior are available there.

## Scope and semantic observations

- Frozen `c3-surface.tsv` has five prior-suite rows: r36, r37 discrimination, r37 escapes, r41 refusal-sites, r42 drift-conditions. `PRIOR` in the counter likewise has five entries. `prior=5/5` therefore means five fixture invocations passed, not five behavioral cases; it is not an 8/9 case-coverage claim.
- The older r36 fixture documents nine cases (match, regs-changed, prunable-changed, absent, malformed, total-mismatch, empty, unrecorded, read-only). That single fixture is a multi-case suite; the counter's prior tally intentionally counts it once. Its in-counter prior arm verifies exit 0 only for r36, r37 discrimination and r42. It additionally checks the r37 escapes control token and r41 `probes=21 pass=21 fail=0` summary. Thus `prior=5/5` is not evidence that the counter independently validates every expected case/result across all historical suites; it delegates case semantics to fixtures.
- The legacy r38 suite declares 12 cases, including the r44 `json-symlink-refused` case. Counter separately checks total cases/pass/fail, the changed case identifier, and a discriminating r37 base arm (`base_fail>=7`, `behavioral_fail>=4`, and the symlink case named). This is stronger than a bare zero exit.
- The new r44 battery documents six cases: dangling/outside/subdirectory/directory leaf symlinks refused, regular leaf written, and symlinked parent accepted. Counter also requires clean and always-refusing stubs to be rejected, guarding both negative and positive behavior. No additional probes beyond the registered frozen counter were run.

## Boundaries / limitations

Counter result is observed only at the exact specified freeze and base revisions. No tests/build/lint, source edits, installs, git/jj mutations, or sibling/shared-bookkeeping edits. `prior=5/5` is fixture-level accounting, not historical aggregate-case parity with any 8/9 figure; fixtures may evolve independently, and the counter does not enumerate each prior fixture's individual cases. No admission or certification conclusion is made.
