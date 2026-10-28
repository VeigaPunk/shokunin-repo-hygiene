# R41sentinel02 — C2 protocol safety review (crafted preregistrations)

Seat: R41sentinel02 (role: sentinel), wave r41 w1. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, freeze `e2a74312af4233963e44e4dbb38838ece07b8bd2`. Leaf seat, no subagents. Read-only against the lane: the only files I wrote are inside this seat directory (`.ufo/waves/round-41/w1/R41sentinel02/`). No git mutation, no install, no lane write.

## Verdict

NOT READY to land any C2 candidate unmodified. The six executor candidates (`R41executor07`..`12`, `souji-freeze-check.py`) mostly hold the security line: across 54 crafted preregistrations none of them read outside the repository through a crafted path, executed prereg-named content, wrote outside `--root`, or hung on a worktree FIFO/device. Four operability defects remain that the frozen C2 counter does not measure:

1. **R41S-02 (all six, top finding):** a missing or non-numeric `Round:` line silently disables the pre-freeze DISPATCH check. A pre-freeze dispatch file yields rc 0 and no finding.
2. **R41S-01 (executor08 only):** any `../`-leading path kills its persistent `git cat-file --batch`; the next write raises `BrokenPipeError` (rc 1, traceback, no finding).
3. **R41S-03 (all six):** a legal repo path containing a space is rejected as COUNTER-/POPULATION-MISSING or FIELD-MISSING (false findings).
4. **R41S-06 (all six):** no size or claim cap (2000 claims: 4.6–8.4 s without strace; 300 MiB Population: peak RSS 0.63–1.25 GB).

I did not score any candidate with the frozen counter (`census/round-41/score-candidate.sh c2 …`); the claim measurement is the L1's. This report is advice on operability and safety, not a score.

## Candidates under test (sha256 of the bytes tested)

| candidate | sha256 |
|---|---|
| R41executor07 | 3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b |
| R41executor08 | 9cc2f0eee1a60fc004d1ee0abfb1c9885daf0c5f4487267a0864ea57d22ff0c0 |
| R41executor09 | e0bec95b77a08c7cab1d45a7c4d4d1fa7f1f15e5191d95bdde15fbe39661f7ba |
| R41executor10 | 25048ab435d57c6786e7ee38b737a4d2137abf365ec79a972af312f98571329e |
| R41executor11 | b9ed293cee386a75532938c8ca4d2f6cb0347a093bb4713a9eadb188a689890d |
| R41executor12 | 67924e50acec17fb16344c05ad30463b367c59a315ae1c120bed706bffe24c95 |

Pinned tool `tools/souji-freeze-check.py` is absent at the lane tip (`ls` returned "No such file or directory"); the candidates were exercised directly. Git 2.56.0, Python 3.14.8.

## Method

- Driver: `attack_fixtures.py` (this seat). Builds one scratch repo per case under `/fast/scratch/hyaku/souji-r41/R41sentinel02/fx/<case>` (every git call `-C`; toplevel asserted before commit). A sentinel file `OUTSIDE-SECRET.txt` (content `OUTSIDE-SECRET-r41\nEXIT=1\n`) sits in `fx/`, outside every fixture repo; a naive read that escapes would match its digest and come out clean.
- Each candidate runs as `python3 -B <cand> --root <fixture> --prereg <arg> --rev <tip>` under `strace -f -qq -e trace=openat,execve` in its own process group, timeout 60 s. Recorded: rc, FINDING classes, traceback, hang, opens outside the repo, opens inside the worktree (outside `.git`), shell execs, marker files (`PWN*`/`PWNED*`) in cwd/fx/fixture.
- Positive control for the detector: `naive_worktree_control.py` (deliberately naive worktree reader) is flagged `READ-OUTSIDE/DEVICE` on the `../OUTSIDE-SECRET.txt` read (`receipts/control-positive.json`). Without it the zero-escape results would be unfalsified.
- Naive-primitive probe (`receipts/naive-primitives.json`): what a straightforward implementation does with the same path strings: worktree `open()` (4 MiB cap, 5 s timeout), `git cat-file -t REV:path`, `git log --diff-filter=A -- path` and without `--`, and `shell=True`.
- Expectations were fixed before the run per case (`accept` in `receipts/candidates.json` `meta.cases`). Two were corrected after the first run, disclosed in "Corrections" below.

## Commands actually run (exact) and observed output

```
$ git --version ; python3 --version
git version 2.56.0
Python 3.14.8
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel HEAD
/home/vgpnk/Projects/shokunin/souji-shokunin
e2a74312af4233963e44e4dbb38838ece07b8bd2
$ ls tools/souji-freeze-check.py
ls: cannot access 'tools/souji-freeze-check.py': No such file or directory
$ strace -qq -e trace=openat -o <scratch>/strace-probe.txt true ; echo rc=$?
rc=0                                   (strace already installed at /usr/bin/strace; no install performed)
$ TMPDIR=<scratch> python3 -B .ufo/waves/round-41/w1/R41sentinel02/attack_fixtures.py   # run 1
... cases=54 candidates=6 runs=324 fails=23        (first-run fixture bug, see Corrections)
$ TMPDIR=<scratch> python3 -B .ufo/waves/round-41/w1/R41sentinel02/attack_fixtures.py   # run 2 (after corrections)
cases=54 candidates=6 runs=324 fails=11           -> receipts/run2.log, receipts/matrix.txt
$ python3 -B control/run_control.py   (positive control; argv fix applied before this run)
verdict FAIL READ-OUTSIDE/DEVICE, escape_opens [".../fx/trav-counter-rel/../OUTSIDE-SECRET.txt"]  -> receipts/control-positive.json
$ printf '%s:../OUTSIDE-SECRET.txt\n' "$H" | git cat-file --batch
fatal: '../OUTSIDE-SECRET.txt' is outside repository at '.../fx/trav-counter-rel'      rc=128
$ git -C <fx/dash-counter> log --diff-filter=A --format=%H --output=<F> -- --output=<F>
-rw-r--r-- ... 0 bytes                              (pathspec form: nothing written)
$ git -C <fx/dash-counter> log --diff-filter=A --format=%H --output=<F>
-rw-r--r-- ... 82 bytes                             (no `--`: git writes its log into the named file)
$ python3 -B targeted.py   -> receipts/targeted.json, receipts/targeted.log
$ python3 -B targeted2.py  -> receipts/targeted2.json, receipts/targeted2.log
$ sha256sum .../R41executor{07..12}/souji-freeze-check.py   -> table above
```

Full per-cell results: `receipts/candidates.json` (324 rows, `results[]`, keyed by `case` + `candidate`). Matrix: `receipts/matrix.txt` (run 2).

## Matrix (run 2; cells that are not PASS)

| case | 07 | 08 | 09 | 10 | 11 | 12 | what happened |
|---|---|---|---|---|---|---|---|
| trav-counter-rel | ok | **FAIL crash** | ok | ok | ok | ok | 08: BrokenPipeError |
| trav-counter-dotslash | ok | **FAIL crash** | ok | ok | ok | ok | 08: BrokenPipeError |
| trav-pop-rel | ok | **FAIL crash** | ok | ok | ok | ok | 08: BrokenPipeError |
| second-claim-bad | ok | **FAIL crash** | ok | ok | ok | ok | 08: BrokenPipeError |
| counter-trailing-slash | ok | ok | ok | **FAIL lenient** | ok | ok | 10 accepts `census/c1.py/` (normpath) |
| space-path | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | false findings (R41S-03) |
| sym-pop-outside | ok | ok | ok | ok | ok | ok | POPULATION-DIGEST + POPULATION-EMPTY, no read of target |
| shell-meta-names | ok | ok | ok | ok | ok | ok | no execution (`PWNED-*` markers absent) |
| dash-* (4 cases) | ok | ok | ok | ok | ok | ok | no marker written |
| wt-fifo / wt-devzero / wt-outside-c1 / wt-tamper | ok | ok | ok | ok | ok | ok | blob-only verdicts |
| huge-claims / huge-population | ok | ok | ok | ok | ok | ok | see R41S-06 |

Silent-pass cells that are PASS in the matrix only because of the accept set `ANY` (R41S-02): `no-round-line` (all six rc 0 with a pre-freeze dispatch file committed), `round-word-before` (all six rc 0), `round-traversal-before` (07, 09, 10, 11, 12 rc 0; 08 flags C0 DISPATCH-BEFORE-FREEZE). Control: `round-missing-before-control` (Round 41 present, same dispatch file) gives C0 DISPATCH-BEFORE-FREEZE from all six.

Per-candidate summary:
- **executor07**: no security failure; space-path false finding; silent on missing/bad Round.
- **executor08**: four `..`-path crashes (R41S-01); space-path; silent on missing/bad Round (but flags `round-traversal-before`).
- **executor09**: space-path (FIELD-MISSING); silent on missing/bad Round.
- **executor10**: trailing-slash leniency (R41S-04); space-path; silent on missing/bad Round.
- **executor11**: space-path; silent on missing/bad Round.
- **executor12**: space-path (FIELD-MISSING); silent on missing/bad Round; refuses a non-UTF-8 prereg (rc 2, "not valid UTF-8") where 07–11 accept it (rc 0). Both are non-crash.

## Findings for the executors' candidates (required behaviour)

**R41S-01 — crash on `..` paths (executor08).** `census/c1.py` style batching: `git cat-file --batch` exits rc 128 on `fatal: '../X' is outside repository`; the persistent `Batch.get` writes to the dead pipe and raises `BrokenPipeError` (traceback, rc 1, no finding). Cases: `trav-counter-rel`, `trav-counter-dotslash`, `trav-pop-rel`, `second-claim-bad`. Required: no traceback for any prereg text; a fatal path becomes COUNTER-/POPULATION-MISSING (or is rejected before git sees it); the batch process's liveness is checked, or `cat-file blob` is used per path. Evidence: `receipts/candidates.json` rows with `"traceback": true`.

**R41S-02 — silent pass when Round is missing or non-numeric (all six; top finding).** The DISPATCH check is keyed on `Round: <N>`. When the line is absent or not `\d+` the check is skipped and the run exits 0 even with `.ufo/waves/round-41/w1-dispatch.json` committed before FREEZE-REV. Cases: `no-round-line`, `round-word-before`, `round-traversal-before`. Required: N undefined must be a refusal (rc 2, COULD-NOT-EVALUATE) or a named finding, never rc 0. `Round: 41/../../x` contains the digits 41; whether N=41 (grammar's "digits" wording) or refusal is an L1 decision. The frozen grammar has no finding class for this; the L1 must name one, or the check is silently optional. Control evidence: `receipts/targeted.json`, case `round-missing-before-control`.

**R41S-03 — legal path with a space is a false finding (all six).** `Counter: census/my counter.py sha256=…` against a committed blob of that exact name yields COUNTER-MISSING (07, 08, 10, 11: `\S+` / `split()[0]`) or FIELD-MISSING (09, 12). Required: the path is everything before ` sha256=`; the blob exists; clean. Not a security issue; fail-closed, but a future lane with a spaced file name cannot be frozen.

**R41S-04 — non-canonical path accepted (executor10).** `Counter: census/c1.py/` is accepted because `posixpath.normpath` strips the trailing slash (candidate line 113), while `git cat-file` on the literal string fails with `fatal: path 'census/c1.py/' does not exist`. Required: a path that is not the tree path spelled exactly must be COUNTER-MISSING. Low severity; relevant because the digest is then checked against a normalised spelling the reviewer did not write.

**R41S-05 — duplicate key silently ignored (grammar gap, all six).** A claim with two `Counter:` lines (the second being `../OUTSIDE-SECRET.txt`) gives rc 0 with no finding in all six; the first line wins and the second is never looked at. Required: a duplicate key is a finding (the grammar names none; L1 decision). Without it the reader and the tool see different counters.

**R41S-06 — no size or claim cap (all six; grammar gap).**
- 2000 claim blocks: 4.6–8.4 s per candidate without strace (08: 0.21 s, batch reuse). Under strace the same run took 15–34 s (`receipts/candidates.json`, `huge-claims`; `receipts/targeted.json`, `timing_no_strace`).
- 300 MiB Population blob: all six clean in 0.41–0.66 s; peak RSS (child `ru_maxrss`) 633–1250 MB (`receipts/targeted2.json`, `rss_300MiB`). Memory scales roughly 2–4× blob size [INFERENCE from two points, 50 MiB and 300 MiB; not measured at 4 GiB].
- Required: a size cap (`git cat-file -s` first; refuse above a stated limit with rc 2) or streamed hashing; a claim-count cap or batched git calls. None of this has a documented class.

**R41S-07 — option injection via `git log` without `--` (naive hazard; all six candidates safe).** Verified: `git log --diff-filter=A --format=%H --output=<F>` writes 82 bytes into `<F>` (a file outside the repo). With the `--` separator the same path is a pathspec and nothing is written (0 bytes). All six candidates pass `--` or `--literal-pathspecs`/`:(literal)`; the four `dash-*` cases produced no marker. Required: every git argv that takes a repo path puts `--` before it; Base/digest values are validated against the regex before any git call.

**R41S-08 — naive-reader hazards (for any implementation that reads the worktree or runs a shell).** Naive probe, `receipts/naive-primitives.json`:
- symlink blob → sentinel: `open()` follows it, reads `OUTSIDE-SECRET`, digest matches → a naive tool reports clean (`sym-counter-outside`, `trav-control-abs`).
- worktree FIFO at Population path: blocked in open, killed at 5 s (`wt-fifo-pop`).
- worktree `/dev/zero`: 4 MiB cap reached, unbounded (`wt-devzero-pop`).
- directory as Counter: `IsADirectoryError` (`dir-counter`, `submodule-counter`); 300-byte component: `OSError ENAMETOOLONG` (`name-too-long`). Uncaught, each is a traceback.
- `shell=True` with `git cat-file -t REV:<path>`: `census/$(touch${IFS}PWNED-EXEC).py` and the `;`/backtick forms create `PWNED-EXEC`, `PWNED-SEMI.tsv`, `PWNED-BT` in cwd (`shell-meta-names`).
- All six candidates: zero worktree opens, zero shell execs, zero opens outside the repo in the strace traces (`receipts/candidates.json`, `worktree_opens`, `shell_execs`, `escape_opens`).
Required: blob-only reads through git plumbing (`cat-file`), no `shell=True`, no `open()` of any path derived from the prereg.

## Confirmed safe on the crafted battery (all six candidates)

Path traversal (`../`, `census/../../`, `./../`, absolute) for Counter, Population, Control and `--prereg` (rc 2 refusal or NO-CLAIMS); symlink blobs for Counter, Population, Control and `--prereg` (no read of the target; digest/NO-CLAIMS/CONTROL-NOT-RED); gitlink/submodule and directory as Counter/Population (COUNTER-/POPULATION-MISSING); overlong names; `.git/config`; glob `census/*.py`; Base as `main`, `HEAD~0`, 12-char prefix, `--output=` (BASE-UNRESOLVED); `Base` uppercase (BASE-UNRESOLVED, six agree); worktree-only FIFO, `/dev/zero`, symlink-to-sentinel and tampered content (all clean, blob-only); post-freeze symlink dispatch and symlink loop `loop -> ..` (no hang, no read); shell metacharacters in names (data, no exec); 50 MiB Population blob; 32-digit EXIT (`EXIT=0` and `EXIT=00` give CONTROL-NOT-RED in all six); non-ASCII path (clean); CRLF prereg (clean in all six); non-UTF-8 byte in prereg (rc 2 in 12, rc 0 in 07–11).

## Corrections to my own expectations (disclosed)

1. **Run 1 → run 2, `shell-meta-names`:** the first fixture put spaces inside `$( )` and `touch PWNED`, so it tested the space-path defect, not execution. Fixed by writing `${IFS}` (no spaces); the case now exercises execution.
2. **`sym-pop-outside` accept set:** the first accept set was `POPULATION-MISSING` or `POPULATION-DIGEST`. The six candidates return `POPULATION-DIGEST` + `POPULATION-EMPTY`, which the grammar supports (a one-line blob has fewer than 2 non-blank lines). I widened the accept set after seeing the run-1 output. It does not affect any security verdict: the outcome is still no read of the target.

Run 1 had 23 FAIL cells; run 2 has 11. The 11 are the cells listed in the matrix (4 crashes, 6 space-path, 1 trailing-slash). The corrections did not change any of them.

## Limits

- Timings in the matrix are under strace and overstate cost; the non-strace timings are in `targeted.json`.
- RSS is the child's `ru_maxrss` via `RUSAGE_CHILDREN` for one run per candidate; not averaged.
- The sentinel-based escape test relies on digests matching the sentinel; a read that escapes without matching would still be caught by the strace `escape_opens` check.
- I did not exercise the frozen counter or any lane-landed commit; the verdict above is about the candidates' behaviour on these inputs, not the C2 measurement.

## Receipts (inside this seat directory)

- `attack_fixtures.py` — driver (this seat).
- `receipts/candidates.json` — 324 rows; `meta` holds the candidate sha256s, case table and accept sets.
- `receipts/matrix.txt`, `receipts/run2.log` — run 2 matrix and log.
- `receipts/naive-primitives.json` — naive worktree/git/shell probe per case.
- `receipts/control-positive.json`, `receipts/naive_worktree_control.py`, `receipts/run_control.py` — positive control for the strace detector.
- `receipts/targeted.json`, `receipts/targeted.log` — Round cases, control, no-strace timings.
- `receipts/targeted2.json`, `receipts/targeted2.log` — non-UTF-8 counter path, 300 MiB RSS.

Scratch `/fast/scratch/hyaku/souji-r41/R41sentinel02/` (fixtures, runs, sentinels) is deleted after these receipts were copied; the driver regenerates every fixture.

## Tooling

No installation or upgrade. `strace` (`/usr/bin/strace`) and `git 2.56.0` were already present and used as-is.

## Lane state

Read-only on the lane. The lane's `git status` shows two untracked files I did not create (`census/round-41/records/c3-after.txt`, `census/round-41/records/r1-after.txt`); I left them alone.
