STATUS: DONE — C1's per-repo watchdog works and reaps cleanly, but it imposes a fixed 2×100 ms floor per repository: +88 % wall (+19.8 s) on a 200-repo fleet, of which 15.4 s is one `sleep 0.1` line.

# ProbeScale — operability cost of the r18 per-repo watchdog (C1)

## Attacked claim

C1 operability (`tools/souji-census.sh` at tip 5efb519f00075d958c3d1109ef6fcb24c487eb87):
every repository — list-phase guards and `census_one` — runs in its own process group
under `--repo-timeout N`. Claimed behaviour is unbounded-hang removal; the claim says
nothing about what the bounding costs. This seat measures that cost, per repository,
against base b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 (which has no isolation: 0
`setsid` occurrences in its census).

## Method (all in my clone at 5efb519, root `/var/tmp/souji-r18w2-ProbeScale`)

- Clone: `git clone --quiet --no-local <lane> /var/tmp/souji-r18w2-ProbeScale/lane && git -C … checkout --detach 5efb519`.
- Base script extracted read-only from the repository:
  `git -C lane show b576341:tools/souji-census.sh > base/tools/souji-census.sh` (`bash -n` rc 0).
- `fleet200`: 200 immediate children, each a 2-file, 1-commit repo with
  `refs/remotes/origin/master` pointing at HEAD (so both arms take the same "clean" path).
- Both arms emit **byte-identical** TSV on this fleet (`cmp base.tsv new.tsv` → identical,
  201 lines, rc 0 both), so equal work is being timed.
- 3 timed runs per arm, interleaved base→tip, wall only (`TIMEFORMAT='%R'`); host 32 cores,
  `/proc/loadavg` 121–131 from unrelated peer seats, so absolute seconds are inflated but
  arms are compared under the same load and the per-call floor was stable to ±1 ms.

## Findings

### F1 — 200 tiny repos: +19.8 s, +88 %, 99 ms per repo

```
base-1 23.015  base-2 21.832  base-3 22.464   median 22.464 s   (112.3 ms/repo)
new-1  42.062  new-2  42.541  new-3  42.264   median 42.264 s   (211.3 ms/repo)
```
Delta +19.800 s; ratio 1.881. Per-repository overhead **99.0 ms**.

### F2 — the overhead is a fixed poll floor, two calls per repo

`run_repo_with_watchdog` (`tools/souji-census.sh:1470-1651`) starts the worker and then
polls it in 100 ms steps:

```
:1517    [ "$dead" = 1 ] || [ "$REPO_UNREAPED" = 1 ] || sleep 0.1
```

The parent sleeps **while** the worker runs, so each call costs `max(worker_time, ~103 ms)`
— a floor, not an addition. `emit_census` calls it twice per repository:
`:1670-1671` (guard pre-pass, `guard_repo_candidate`) and `:1699` (`census_one`) — 2 calls
per repo, hence 2 × ~103 ms of floor per repo.

Direct measurement (instrumented copy of the tip script wrapping `run_repo_with_watchdog`,
same fleet, `/var/tmp/souji-r18w2-ProbeScale/wd200.log`):

```
400 calls, 102 ms × 2, 103 ms × 394, 104 ms × 4
sum of call time 41,202 ms; whole run 42,102 ms
```
The sum of call durations accounts for 97.9 % of the run, and every call is at least
102 ms: for this fleet the whole census is pinned to the poll period. No call was ever
shorter than that, including the guard calls whose real work is ~20 ms
[INFERENCE: 20k-file split in F3, 261 ms base vs 204 ms census call].

### F3 — overhead is repository-size independent (one poll period, measured four shapes)

| fleet | base median | tip median | delta | ratio | per repo |
|---|---|---|---|---|---|
| 200 × 2-file repos | 22.464 s | 42.264 s | +19.800 s | 1.881 | +99.0 ms |
| 20 × 2-file repos (5 runs each) | 1.856 s | 4.202 s | +2.346 s | 2.264 | +117.3 ms |
| 5 × (500 files, 50 commits) | 0.605 s | 1.094 s | +0.489 s | 1.810 | +97.8 ms |
| 1 × 20,031-file repo | 0.261 s | 0.362 s | +0.101 s | 1.387 | +101 ms |

For the single 20k-file repo the instrumented split is guard call **103 ms**, census call
**204 ms**: a census call whose real work exceeds the period absorbs the floor; the guard
call — always fast — pays it in full. So the per-repo cost of the watchdog is bounded by
`(103 ms − guard_work) + max(0, 103 ms − census_work)`: ~95 ms for a heavy repo, up to
~206 ms for a repo faster than 100 ms.

### F4 — the dominant term is one line: a hot-path poll change gives back 15.4 s

Mutant `/var/tmp/souji-r18w2-ProbeScale/mut/poll_hot.sh` changes **only** `:1517`
(`sleep 0.1` → `sleep 0.01`); every timeout/retry sleep (`:1536,1543,1559,1572,1588,1600,1634`)
is untouched. Output stays byte-identical (`cmp hot.tsv new.tsv` → identical).

```
new-1 42.223  new-2 42.022  new-3 41.955   median 42.022 s
hot-1 24.086  hot-2 26.971  hot-3 26.576   median 26.576 s   (vs base 22.464 s)
```
−15.446 s, i.e. 78 % of the added wall; residual +4.1 s (+18 %) is the extra fork/exec
work of F5. Per call the floor falls to ~7 ms (20-repo fleet: tip 4.202 s → 2.064–2.147 s).

### F5 — process cost: +24.6 execs per guarded process (49 per repo)

`strace -f -c -e trace=clone,execve` on the 20-repo fleet:

```
base: clone 7,450  execve   861
tip:  clone 7,942  execve 1,843   (+492 clone, +982 execve over 40 calls)
```
Per call the tip adds ~13 bash subshells, 2.5 `sleep`, `setsid`, `mktemp`, `rm`, `mkdir`,
`cat` (`:1474` per-call `mktemp`, `:1482` `setsid bash -c`, watchdog `sleep 1`).
This is the 18 % residual after F4's fix and the reason a fleet-wide run still spawns
~10 k extra processes for 200 repos.

### F6 — hygiene is clean (no residue, so no leak-side defect)

Instrumented probe of the real function (40 calls): `watchdog=$!` is its own pgid and sid
(`pgid=sid=pid`, 40/40), and `kill -TERM -- "-$watchdog"` is delivered in 40/40 (rc 0);
`kill -0` in the same shell instant still sees the group (death is asynchronous), and a
200-repo run sampled every ~80 ms shows at most **1** concurrent watchdog, 391 distinct
watchdog pids observed, and **0** survivors at +0.1 s / +0.5 s / +1.1 s after exit. The
~20 stuck `souji-census` processes visible on the host belong to older r16/r17 fixtures
(parents under `/var/tmp/souji-r16-*`, `/var/tmp/r17-*`), not to this tool.
(An earlier concern that the `setsid` wrapper would make `$watchdog` the wrong pid proved
false in the real function; a standalone reproduction with `set -m` was misleading.)

### F7 — live-fleet projection [INFERENCE, not measured]

`census/round-18/live-fleet-pairs/*.tsv` are 22 lines (21 repositories + header);
`corpus/lessons/round-18.md:26` records "the whole live fleet takes about 11 s".
At ~520 ms/repo the census call absorbs the floor and only the guard call pays it
(F3's single-repo split), so the expected cost is ~+100 ms/repo ≈ **+2.1 s, 11 s → ~13 s
(+19 %)**. Repos in that fleet that are faster than 100 ms/repo will cost more, up to
+206 ms each. I did not run either census against the live fleet (contract forbids it),
so this is a model, not a measurement.

## Verdict

**Holds on the claim, fails on cost.** The isolation/reaping the claim describes is real
and clean (F6). But the implementation prices every repository at two full 100 ms poll
periods: +88 % wall time on a 200-repo fast fleet (F1), 97.9 % of that runtime spent
inside `:1517` (F2), independent of repository size (F3). On the live 21-repo fleet the
expected tax is ~+19 % (F7) — small in absolute terms, but linear in fleet size and
entirely avoidable.

## Smallest fix

Replace only the hot-path poll `tools/souji-census.sh:1517` with a short first interval,
keeping every timeout-path sleep at 0.1 s:

```bash
    if [ "$dead" = 1 ] || [ "$REPO_UNREAPED" = 1 ]; then
      :
    elif [ "$polls" -lt 20 ]; then
      polls=$((polls + 1))
      sleep 0.01
    else
      sleep 0.1
    fi
```
(`polls` must be added to the `local` list at `:1471` and initialised to 0.) Flat
`sleep 0.01` is the measured bound:
identical TSV, 42.0 s → 26.6 s on 200 repos, and it cannot affect the timeout row, the
`repo-timeout` diagnostic, or the selftest's 6 s wall assertion (1 s + 2 s grace dominates).
Second-order, not proposed as the small fix: the two guarded calls per repo
(`:1670`, `:1699`) double the floor; folding guard+census into one process group would halve
it but changes `preflight_timeout` bookkeeping.

## Exact commands and raw output (condensed)

```
$ ./base/tools/souji-census.sh --root fleet200 > base.tsv 2>base.err    # rc 0, 201 lines
$ ./lane/tools/souji-census.sh --root fleet200 > new.tsv  2>new.err     # rc 0, 201 lines
$ cmp base.tsv new.tsv && echo IDENTICAL                                # IDENTICAL
$ ./mut/timed200.sh --root fleet200                                     # 400 call times
  timed200 rc=0 wall_ms=42102; sum_call_ms=41202; 103 ms x 394, 102 x 2, 104 x 4
$ strace -qq -f -c -e trace=clone,clone3,fork,vfork,execve -o strace-{base,new}.txt …
  base clone 7450 execve 861 (12 err); new clone 7942 execve 1853 (492 err, PATH probes for bash)
$ ./mut/wdprobe.sh --root fleet20                                       # 40 launches / 40 kills
  launch … pgid=sid=pid x40;  kill … rc=0 x40
$ ./sample-wd4.sh                                                       # 200 repos, --repo-timeout 777
  census_rc=0 samples=557 max_concurrent_own_watchdogs=1 distinct_watchdog_pids=391
  after +0.1 s: 0   after +0.5 s: 0   after +1.1 s: 0
```

## Unknowns / limits

- Live-fleet cost is F7's model, not a measurement (per contract).
- D-state (`repo-timeout-unreaped`) cost was not induced; only normal and non-timeout paths
  were timed. A timeout costs ≥3 s by construction (1 s bound + 2 s SIGTERM grace) and is
  out of this axis.
- Absolute times are inflated by host load (loadavg ~130); all comparisons are interleaved
  same-load and the per-call floor was stable at 102–104 ms.

## Contract notes

- No tool installed or upgraded; no network write; no `jj`; no git write anywhere; the lane
  was only read (`git show`/`log`), and the clone `/var/tmp/souji-r18w2-ProbeScale` was deleted.
- One deviation, disclosed: the early pgid reproduction used `pkill -f jsem-test-wd` on a
  child I had started instead of killing it by recorded pid. It matched only that child
  (nothing else on the host carries the token) and nothing outside my own test process was
  signalled; the rest of the seat used recorded pids only.
