# R93Sentinel: robustness of the r93 row types, search changes and KFF19/KFF20 fixture

Seat: sentinel (leaf, no dispatch). Scope: the ledger-drop/ledger-trim writer, the search's path guards and `_reap`,
the r93 fixture's KFF19 cost and exception handling, and the /tmp path audit. Reproducers are text files in
`.ufo/waves/round-93/w1/R93Sentinel/repro/`. Scratch under `/fast/scratch/hyaku/souji-r93/R93Sentinel/` was deleted
before this yield. Nothing in the lane, the fleet root, MANIFEST, .ufo/state or the frozen census/tests/tools/corpus
was written. Tools: none installed; the host's own `/usr/bin/strace` and `/usr/bin/time` were used read-only.

## Verdict
- FALSIFIES-WORDING: one sentence on the kill rule (finding M1), with reproducer. It does not change either
  target's verdict.
- FALSIFIES-NUMBER: none. Both C1 targets are killed by a semantic mismatch, and KFF19 measures 14,586 payloads
  with 0 inexact.
- NO-FALSIFICATION for the C2 numbers (`rejected=8`, `22/22`). The probe's exception handling (M2) can only
  under-count rejections, never inflate them.

## FALSIFIES-WORDING

### M1 (MEDIUM): the r93 kill rule still scores a counter's uncaught exception as "killed"
- Exact sentences:
  1. `census/round-93/c1-survivor-search.py` docstring, lines 4-7: "a harness exit 2, or an exit 1 whose only failing
     rows are `match=error` (the counter crashed, rc 2), is `errored`". The parenthetical is false. A Python counter
     that raises an uncaught exception exits **rc 1**, not rc 2, and the harness records it as `match=no`.
  2. The prereg KILL RULE, "(r93, tighter than r84-r92)": the rule is literally met by a crash, so it is not
     tighter for crashes that exit 1.
- Reproducer: `repro/counter-crash3.py` (the frozen r87 counter plus `if len(r) == 3: raise RuntimeError('crash-probe')`
  before the width guard) run through the unchanged r93 harness on the pinned r93 population:
  `python3 -B census/round-93/c1-false-row-harness.py --counter <seat>/repro/counter-crash3.py --lane . --fleet-root <fleet> --work <empty> --population census/round-93/c1-false-rows.tsv`.
  Output (`repro/h-crash3.out`): `ROW LD6 ... expect=MOVED/0 got=- rc=1 match=no`, harness rc 1. `verdict()` returns
  **yes (killed)**. The crash is a traceback on stderr, not a counted `errored`.
- Effect on the claim: none on the numbers. The two targets are killed semantically:
  - h-ok-admits-one (`repro/h-h-ok.out`): `ROW LD5 ... got=UNRESOLVED rc=0 match=no`. Note the kill is by the EXIT
    code only (status matched); this is the prereg's stated limit (iii).
  - a491c22-<-to-<= (`repro/h-a491.out`): `ROW LD6 ... got=UNRESOLVED rc=1 match=no` (MOVED expected).
- Effect on the search: a crash-only generated mutant would be counted `killed=yes`, which inflates the "killed"
  column for any generated mutant that crashes. Fix for L1 to decide: score `killed` only when the failing ROW has
  `got` in the resolving or asserted classes (not `got=-`), or treat any harness `rc=1` whose counter stderr is a
  traceback as `errored`. The filed search was not changed by this seat.

## HIGH
None.

## MEDIUM

### M2 (MEDIUM, instrument robustness, conservative direction): in-process exceptions escape the r93 fixture's scorer
- `tests/fixtures/r93-k4-flagfail.py` `score()` catches only `(OSError, SubprocessError, KeyError, SyntaxError,
  ValueError, AttributeError)`. KFF18, KFF19 and the module-level `exec_module` of the tool run IN the fixture process,
  so an `IndexError`, `TypeError`, `RuntimeError` etc. in the tool crashes the whole fixture. Subprocess cases (the
  `run_case` ones) are not affected: an exception there yields no MISMATCH rows and the case scores fail.
- Reproducers (`repro/tool-IndexError.py`, `repro/tool-ValueError.py`, the filed tool plus a raise at the top of
  `_one_line_bytes` for `len(raw) == 230`):
  - `IndexError`: fixture rc 1, `IndexError: probe: forced IndexError` on stderr, **no SUMMARY line**.
  - `ValueError`: caught, `CASE KFF19 tool=fail`, `SUMMARY cases=22 tool_pass=21 before_pass=16`, rc 1.
- Probe effect (`repro/c2-probe-plus-F8.py` = the probe plus one forgery F8 that does exactly that, output
  `repro/probe-F8.out`): `FORGERY F8 ... exit=1 tool_pass=-/- rejected=no`, and
  `FORGERY-SUMMARY forgeries=9 rejected=8 positive=pass`, exit 1. A crashing forgery is therefore reported as NOT
  rejected. Rejection requires a SUMMARY line, so an exception cannot inflate the count. The C2 counts are unaffected.
- Corroboration of the claim (same run): F5, F6 and F7 each fail only `KFF19` (`tool_pass=21/22`), F1-F4 and N0 fail
  several cases, and the filed tool passes `22/22`.
- Fix (not applied): catch `Exception` in `score()` for in-process cases, or run the tool in a subprocess as the
  other cases do.

## LOW

### L1 (LOW): `_reap` follows a symlinked mutant directory and deletes outside `--work`
- `_reap` deletes `os.path.join(work, e, "w")` for every entry `e`. Python's `rmtree` does not follow a symlink
  at the last component, but it does follow symlinks in the parent path. With `work/m0000 -> outA`, the call deletes
  `outA/w`. Reproduced: `outA/w/keepA.txt` is gone after `_reap(work)`.
- Reachability: low. The emptiness check and `os.makedirs(d)` (which refuses an existing entry) stop a symlink from
  pre-existing. Only a concurrent writer replacing `work/mNNNN` after `makedirs` gets there. Checks that hold: a
  symlinked `work/m0001/w -> outB/w` is NOT deleted (`outB/w/keepB.txt` survives), and a symlink inside `w`
  pointing at an outside directory is NOT followed (`outC/keep.txt` survives). A real `m0002/w` is removed.
- Fix (not applied): resolve `d` with `os.path.realpath` and assert it lies under `realpath(work)` before `rmtree`.

### L2 (LOW): the /tmp guard is a prefix test and misses the exact roots
- Search, harness, probe and fixture all use `realpath(...).startswith(("/tmp/", "/var/tmp/", "/dev/shm/"))`, which
  refuses `/tmp/x` but not `/tmp`, `/var/tmp` or `/dev/shm` themselves. `--work /tmp` is refused only because
  `/tmp` is non-empty (`C1-SEARCH-FATAL: --work ... g4link is not empty`, reproduced with a symlink to `/tmp`). On an
  empty `/tmp` the search would create `m0000` directly in `/tmp`.
- Fix: refuse `realpath(x) in ("/tmp", "/var/tmp", "/dev/shm")` as well.

### L3 (LOW): the frozen ledger is read from the lane without a sha pin or a printed hash
- The harness pins and prints the harness, the population and the counter. It does not pin or print
  `census/round-77/c2-pointer-ledger.tsv`, which LD5, LD6 and all ledger rows read from `--lane`. Working-tree
  sha256 at this seat: `011faa0e96333b28af0418df8f56a5cbb169ed71aa0e9f688ee6d97d7aa39ba5`. A changed ledger changes
  the verdicts, so the change is not silent, but a reader cannot tell which ledger produced a run.

### L4 (LOW, latent): the writer's line split uses `str.splitlines`
- `ledger-drop/trim` splits the ledger with `splitlines(keepends=True)`, which also splits on `\x0c`, `\x1c`-`\x1e`,
  `\x85`, `\u2028` and `\u2029`. The counter reads with a different splitter. The frozen r77 ledger contains none of
  these (checked: no occurrences), so there is no effect today. A future ledger row carrying one would make the
  harness and the counter disagree on what a row is.

## NO FINDING (what was tried)

Writer (`ledger-drop`, `ledger-trim`). I ran a scratch harness copy (`repro/harness-h2.py`) that pins a two-row
population (LD5 and LD6, copied byte-for-byte from the r93 population), skips the fixture build (the LD rows judge the
lane at BASE), and reads the base ledger from `$R93S_LEDGER`. Eight ledger variants (`repro/led-*.tsv`, `repro/pop-ld.tsv`):

| variant | edit | result |
|---|---|---|
| base | none | LD5 UNRESOLVED rc1 match=yes; LD6 MOVED rc0 match=yes; rc 0 |
| dup | P04 row duplicated | `C1-HARNESS-FATAL: LD5: item P04 is not exactly one 4+-column row`, rc 2 |
| three | P04 row cut to 3 columns (frozen ledger) | same FATAL, rc 2 (setup, as required) |
| comment | `#P04 ...` comment line added before the real row | comment NOT edited; LD5 and LD6 match=yes, rc 0 |
| commentonly | the only P04 line commented out | FATAL, rc 2 |
| prefixspace | leading space before P04 | FATAL, rc 2 |
| nonl | P04 row moved last, no trailing newline | match=yes both, rc 0 |
| crlf | P04 row ends in `\r\n` | match=yes both, rc 0 |

- The edited ledger always goes to `<--work>/ledger-<rid>.tsv` (verified in each run's work dir). Nothing is written
  under the lane.
- Only the item's own row is removed or trimmed. The `#` comment is excluded by the `startswith("#")` test, so a
  comment starting with the item id is never edited.

Search guards (each run, each refused with rc 2 before any directory is created; no artefact in /tmp afterwards):
`--work /tmp/...`, `--emit /tmp/...`, `--work` symlink to `/tmp/...`, `--emit` through a symlink to `/tmp`, harness
`--work` through a symlink to `/tmp`, probe `--work /tmp/...`, fixture `--work` through a symlink to `/tmp`, and
`--work` containing a pre-existing `m0000` symlink ("is not empty"). `--emit` under /tmp is refused. The
`--work`-symlink-to-/tmp case is refused by realpath. The exact-root gap is L2.

Cost of KFF19: `case_exact` on the filed tool takes 0.49 s per call (two arms per fixture run). It sweeps 14,586
payloads and reports `inexact=0`. The full fixture run is 5.2 s wall (`/usr/bin/time` maxrss 23.7 MB). The probe runs
the fixture 9 times, about 45 s of fixture time at this load.

/tmp audit: no r93 instrument, counter or tool uses `tempfile`, `mkstemp` or `gettempdir`. Evidence:
- `strace -f -e trace=file` over a full harness run (filed counter, r93 population, 17 s) and over a full fixture run,
  both with `TMPDIR` set to a scratch dir. Path arguments under `/tmp`, `/var/tmp` or `/dev/shm`: 0 in both. `TMPDIR`
  references: 0 in both.
- The 66 python child processes of the harness run (counter and tool runs) make 0 write-ish syscalls (O_WRONLY, O_RDWR,
  O_CREAT, O_TRUNC, mkdir, unlink, rename, symlink, link).
- The harness run makes 0 write-open, mkdir, unlink, rename or symlink calls on absolute lane paths. The git
  checkouts and symlink creations in the trace are relative to the scratch fixture (which is correct: the fixture
  is `git clone` of the lane into scratch).

Fixture exception path: a subprocess-case crash scores fail, because `run_case` yields no MISMATCH rows (reasoned
from the code; I did not run a subprocess-crash injection). An in-process `ValueError` is caught and scored (M2).

rmtree on a work tree (`_reap`): symlinks inside `w` are unlinked, not followed (see L1). Scratch trees with
symlinked content are safe.

## Reproduction (from the lane root, `<seat>` = `.ufo/waves/round-93/w1/R93Sentinel`)
- Writer variant: `R93S_LEDGER=<seat>/repro/led-dup.tsv python3 -B <seat>/repro/harness-h2.py --counter census/round-87/c1-pointer-counter.py --lane . --fleet-root <fleet> --work <empty> --population <seat>/repro/pop-ld.tsv`
  (the scratch harness stubs the fixture build and reads the base ledger from the env var. It is a scratch copy, not a filed instrument.)
- M1: `python3 -B census/round-93/c1-false-row-harness.py --counter <seat>/repro/counter-crash3.py --lane . --fleet-root <fleet> --work <empty> --population census/round-93/c1-false-rows.tsv`, then read the `ROW LD6` line.
- M2: `python3 -B tests/fixtures/r93-k4-flagfail.py --tool <seat>/repro/tool-IndexError.py --before census/round-92/controls/c2-before-tool.py --work <empty>`
- M2 probe: `python3 -B <seat>/repro/c2-probe-plus-F8.py --fixture tests/fixtures/r93-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>`

## Cleanup
`/fast/scratch/hyaku/souji-r93/R93Sentinel` removed. Seat dir holds only this report and `repro/` (text files, about
300 KB). No git or jj command was run against any repo.
