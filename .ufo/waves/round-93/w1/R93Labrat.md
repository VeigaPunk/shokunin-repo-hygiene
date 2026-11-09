# R93Labrat — interrupt-path probe (souji r93, C1 search)

## Hypothesis H
Sending SIGTERM (and separately SIGINT), 6s into a running
`census/round-93/c1-survivor-search.py` (r93 population, `--ids` = 4 generated
ids, `--jobs 2`) makes it exit 130 within 30 s with zero `m*/w` dirs left under
`--work` and no surviving harness/counter process of that run.

## Setup
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (read-only; never mutated).
- Search r93: `census/round-93/c1-survivor-search.py`
  sha256 `6089260be7d18c5f48c5bf1289e159efba534f2ef1c5d730f9b4f356d37ed71d`
- Search r92 (control): `census/round-92/c1-survivor-search.py`
  sha256 `c393d941eb2eb13de8acba81665b0378347ae4f77b620cc2da890854ec4c9cc4`
  (no SIGINT/SIGTERM handler — only `signal` import is used for the timeout killpg, line 98.)
- Harness r93 sha256 `1868a570b9100559...`, r92 `818f84d96a88288d...`;
  populations r93 `d6439f65a632cf83...`, r92 `f66341fc2867f6b5...`
- Counter: `census/round-87/c1-pointer-counter.py` sha256 `fd0a8e244a5e0afe...`
- `--ids` = first 4 generated ids
  (`a127c26-True-to-False`, `a156c46-not-to-drop`, `a162c27-True-to-False`,
  `a165c13-and-to-or`), sha256 `deafb4884e1cbe236f7f420e1331084a06fb1c07b1b8f49019ebfac6c559c67d`.
  Each arm ran with `--jobs 2`, `--work /fast/scratch/hyaku/souji-r93/R93Labrat/work-<arm>`,
  signal sent at t=6s (2 harness trees live, ~720 MB on disk), measured:
  rc, elapsed-after-signal, `w_dirs`, `du -sk`, ps filtered by work path,
  re-checked 1 s later.
- Driver + raw JSON receipts:
  `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-93/w1/R93Labrat/driver.py`,
  `results-r93.json`, `results-r92.json`, `results-kill.json`, `ids4.json`.

## r93 arms — H CONFIRMED (4/4)

| arm | sig | rc | elapsed post-signal | w_dirs PRE | w_dirs POST | w_dirs POST+1s | du POST (KB) | ps POST |
|-----|-----|----|--------------------|-----------|-------------|---------------|--------------|---------|
| r93-term-1 | SIGTERM | 130 | 0.51 s | 2 | 0 | 0 | 80 | empty |
| r93-term-2 | SIGTERM | 130 | 0.63 s | 2 | 0 | 0 | 80 | empty |
| r93-int-1  | SIGINT  | 130 | 0.54 s | 2 | 0 | 0 | 80 | empty |
| r93-int-2  | SIGINT  | 130 | 0.51 s | 2 | 0 | 0 | 80 | empty |

All four exited 130 in <1 s after the signal; the pre-signal
`du` was ~737,700 KB (two ~0.7 GB clones) and post-signal the work dir held
only the 80 KB `mXXXX/harness.out` stubs. Output closed with
`C1-SEARCH-INTERRUPTED: signal 15; live harness groups killed, work trees deleted`
(SIGTERM) / `C1-SEARCH-INTERRUPTED: ; ...` (SIGINT; the `KeyboardInterrupt`
from `_stop` carries no signal-number text, but rc=130 and the message are identical).
A preliminary single SIGTERM run before the batch gave the same numbers
(rc=130, 0.48 s, 2→0).

## r92 control arms — no signal handling, as expected

| arm | sig | rc | elapsed post-signal | w_dirs PRE→POST→POST+1s | du POST (KB) | ps POST | ps POST+1s |
|-----|-----|----|--------------------|--------------------------|--------------|---------|------------|
| r92-term-1 | SIGTERM | -15 (default kill) | 0.18 s | 2→2→2 | 737,788 | 2 live harness/counter rows | empty |
| r92-term-2 | SIGTERM | -15 | 0.20 s | 2→2→2 | 737,756 | 2 live rows | empty |
| r92-int-1  | SIGINT  | driver 30 s timeout → SIGKILL (rc=-9) | 30.21 s | 2→1→1 | 369,196 | empty | empty |
| r92-int-2  | SIGINT  | -2, `KeyboardInterrupt` traceback | 27.42 s | 2→0→0 | 188 | empty | empty |

- SIGTERM on r92 killed the search outright (rc -15); both harness trees
  (737,788 / 737,756 KB) were stranded, with live harness+counter processes
  still running immediately after. The orphaned harnesses later
  finished/stopped on their own — ps at POST+1 s was empty, but the trees
  remained. The driver deleted the stranded work trees after measuring.
- SIGINT on r92 raised an uncaught `KeyboardInterrupt` inside
  `cf.ThreadPoolExecutor` cleanup but the workers ran to completion first:
  int-1 exceeded the 30 s driver wait (forced SIGKILL at 30.21 s, leaving
  1 tree, 369,196 KB); int-2 exited -2 after 27.42 s with trees eventually
  cleaned by the normal `score()` `finally` (0 dirs, 188 KB). Either way rc ≠ 130
  and the timing is "wait for the current mutants" rather than a prompt reap.

## SIGKILL on r93 (stated residual)

| arm | sig | rc | elapsed | w_dirs PRE→POST→POST+1s | du POST (KB) |
|-----|-----|----|---------|--------------------------|--------------|
| r93-kill-1 | SIGKILL | -9 | 0.20 s | 2→2→2 | 737,744 |

As expected, SIGKILL stranded both trees (~720 MB) plus 2 live
harness/counter processes at POST (still running; gone by POST+1 s as they
finished independently). Nothing can run cleanup on SIGKILL — this is the
r92-era residual the round does not claim to fix, and the probe confirms it
remains: an external watchdog/reaper would be needed to reclaim those trees.

## Verdict
- **H CONFIRMED for the r93 search**: SIGTERM and SIGINT each exit 130 in
  ~0.5 s with zero `m*/w` dirs, 80 KB residual, and no surviving
  harness/counter processes of the run (4/4 arms).
- Control behaves as designed: the r92 search has no interrupt path
  (SIGTERM strands trees + live processes; SIGINT is a slow traceback).
- SIGKILL strands trees on both searches — expected, not a new finding.

Reproducers: `.ufo/waves/round-93/w1/R93Labrat/driver.py` (re-run with
`python3 driver.py r93|r92|kill`); raw numbers in `results-*.json` beside it.

NO-FALSIFICATION
------------
Nothing in this probe falsifies a sentence of C1 or C2. The search's docstring
change 3 ("SIGINT/SIGTERM stop the search, kill every live harness process group
and delete every per-mutant work tree before exit (exit 130)") is confirmed
verbatim for SIGTERM/SIGINT; SIGKILL stranding is an unstated residual, not a
contradiction of that sentence. No claim number or wording is touched.
