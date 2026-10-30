# R43executor11 — S35 timeout mutant timing

Hypothesis under test: `case-gitdir-probe-honors-timeout` reliably distinguishes pristine from S35, with pristine <12s and mutant >=20s on every run, including under load.

## Commands / method

- Read `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/c3-counter.py:79-112` and confirmed S35 substitution: replace `got = git(["rev-parse", "--absolute-git-dir"], resolved, args.timeout)` with `got = git(["rev-parse", "--absolute-git-dir"], resolved, 20)`.
- Read pinned pristine bytes with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 619a75034dd6324e1a725f73034c59f7bf9558ef:tools/souji-worktree-drift.py`; changed only the exact S35 expression in the scratch mutant. Created an isolated repository with `git init`, replaced `.git/HEAD` by a FIFO, and supplied a one-row REPO/TOTAL record.
- Ran both tool files serially 10 times each, then with 16 spawned `bash -c 'while :; do :; done'` CPU spinners 10 times each; tool args on each invocation: `python3 -B <pristine.py|mutant.py> --root <scratch>/repo --record <scratch>/record --timeout 1`. Python `time.monotonic()` measured wall elapsed; recorded subprocess return code and output. Spinners were terminated and waited by their own recorded `Popen` handles in `finally`. Scratch was removed in `finally`.
- Experiment driver was a Python Eval cell (not a shell command); source inputs and exact arguments above identify its operations. No tools installed.

## Results

Elapsed seconds / process rc. All 40 runs emitted `DRIFT\tUNREACHABLE\trepo\tUNREACHABLE:list-timeout`, summary `drift_rows=2 unreachable=1`, and returned 1. This output is identical for pristine and mutant.

| Tool | Load | Run | Elapsed (s) | rc |
|---|---|---:|---:|---:|
| pristine | serial | 1 | 1.034 | 1 |
| pristine | serial | 2 | 1.035 | 1 |
| pristine | serial | 3 | 1.032 | 1 |
| pristine | serial | 4 | 1.039 | 1 |
| pristine | serial | 5 | 1.041 | 1 |
| pristine | serial | 6 | 1.037 | 1 |
| pristine | serial | 7 | 1.030 | 1 |
| pristine | serial | 8 | 1.031 | 1 |
| pristine | serial | 9 | 1.032 | 1 |
| pristine | serial | 10 | 1.035 | 1 |
| mutant | serial | 1 | 1.033 | 1 |
| mutant | serial | 2 | 1.033 | 1 |
| mutant | serial | 3 | 1.033 | 1 |
| mutant | serial | 4 | 1.033 | 1 |
| mutant | serial | 5 | 1.035 | 1 |
| mutant | serial | 6 | 1.037 | 1 |
| mutant | serial | 7 | 1.037 | 1 |
| mutant | serial | 8 | 1.032 | 1 |
| mutant | serial | 9 | 1.037 | 1 |
| mutant | serial | 10 | 1.032 | 1 |
| pristine | loaded | 1 | 1.037 | 1 |
| pristine | loaded | 2 | 1.041 | 1 |
| pristine | loaded | 3 | 1.043 | 1 |
| pristine | loaded | 4 | 1.043 | 1 |
| pristine | loaded | 5 | 1.046 | 1 |
| pristine | loaded | 6 | 1.046 | 1 |
| pristine | loaded | 7 | 1.046 | 1 |
| pristine | loaded | 8 | 1.047 | 1 |
| pristine | loaded | 9 | 1.053 | 1 |
| pristine | loaded | 10 | 1.047 | 1 |
| mutant | loaded | 1 | 1.056 | 1 |
| mutant | loaded | 2 | 1.048 | 1 |
| mutant | loaded | 3 | 1.047 | 1 |
| mutant | loaded | 4 | 1.055 | 1 |
| mutant | loaded | 5 | 1.050 | 1 |
| mutant | loaded | 6 | 1.057 | 1 |
| mutant | loaded | 7 | 1.053 | 1 |
| mutant | loaded | 8 | 1.044 | 1 |
| mutant | loaded | 9 | 1.054 | 1 |
| mutant | loaded | 10 | 1.044 | 1 |

## Verdict

**Hypothesis falsified; finding attacks C3 frozen S35 mutant `timeout-fifo-head` / `case-gitdir-probe-honors-timeout`.** Mutant never approached >=20s: all mutant runs were ~1.03–1.06s, indistinguishable from pristine. Likely the FIFO stalls the earlier `git worktree list` probe, which already receives `--timeout 1`, so execution does not reach the mutated absolute-git-dir probe. The fixture's scenario therefore does not reliably exercise S35's changed timeout argument; the claimed timing separation is absent on these runs. Increase margin alone cannot resolve an unexercised mutation; the fixture needs an observable that reaches the `rev-parse --absolute-git-dir` call.

Report contains the observed trial record; scratch removed at experiment completion. No lane/source files changed besides this report.