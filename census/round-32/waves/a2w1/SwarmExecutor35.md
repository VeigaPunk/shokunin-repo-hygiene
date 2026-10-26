# SwarmExecutor35 — r32 a2w1, C2 + C3 re-measured at the current lane tip

## Status

STATUS: PARTIAL — both frozen counters ran to completion at the lane tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`; C3 meets its target under v1 and v2 (exit 0), C2 does not (`pass=25 fail=2`, exit 1). C2's T12 verdict is, additionally, not reproducible across runs of the same fixture at the same revision.

## Evidence

Tip resolved before any measurement: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse master` → `4e56c48b8fc828f9aba2746e324dc46aa538bdbf` (the salvage commit). All three counters were run unmodified with `python3 -B`, `--base 85b61a151923986e7e6b48f7084b9122561b5f3d`, `--list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`; every one clones git objects at `--rev`, so the lane's dirty working tree (see Finding 5) does not enter the measurement. Raw stdout of all three runs is delivered whole in `.ufo/waves/round-32/a2w1/deliver-tip-measure.txt`; host load at the time was 17.01 19.63 19.54 on 32 cores.

1. C2, full run (no `--only`), 355 s:

```
$ python3 -B census/round-32/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 4e56c48b8fc828f9aba2746e324dc46aa538bdbf --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
    --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --scratch /fast/scratch/hyaku/souji-r32/RemeasureTip/c2
ITEM	T12	FAIL	base=rc0:W5463:selftest: 69 checks, 0 failed	sbox=rc1:W6070:selftest: 69 checks, 4 failed	regress
ITEM	T18	FAIL	base=rc0:W4232:SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=26	sbox=rc0:W4230:SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=32	regress
SUMMARY items=27 pass=25 fail=2 rev=4e56c48b8fc828f9aba2746e324dc46aa538bdbf
EXIT=1
```

   The other 25 items are `PASS`; no other item line is non-PASS. So **C2 `fail=0` does NOT hold at the tip** (and per `census/round-32/records/c2-after-v1.txt` it did not hold at its landing commit `98e5203d…` either: `pass=26 fail=1`, T18 FAIL).

2. C3 v1 (frozen instrument), 6.9 s — every leg PASS, no non-PASS leg line:

```
SUMMARY legs=14 fail=0 f1_entries=5 rev=4e56c48b8fc828f9aba2746e324dc46aa538bdbf
EXIT=0
```

3. C3 v2 (amendment A1), 7.3 s — every leg L1–L17 PASS:

```
SUMMARY legs=17 fail=0 f1_entries=5 rev=4e56c48b8fc828f9aba2746e324dc46aa538bdbf
EXIT=0
```

   So **C3 holds at the tip** under both instruments (`legs=14 fail=0 f1_entries=5` and `legs=17 fail=0 f1_entries=5`).

4. T12 re-run directly, outside the counter, in a `--no-local` clone checked out at `4e56c48…`, with the counter's own sandbox (`bwrap --dev-bind / / --ro-bind <empty> /tmp --ro-bind <empty> /var/tmp --ro-bind <empty> /dev/shm --chdir <clone>`, `TMPDIR` a private dir under `/fast/scratch`): `bash tools/souji-census.sh --selftest` → `selftest: 69 checks, 0 failed`, exit 0, three times — plain (44.06 s), with one core pinned and contended by a spinner (60.05 s), and wrapped in the counter's exact strace arguments `strace -f -qq -o <log> -e trace=mkdir,mkdirat,creat,open,openat,openat2` (91.29 s).

5. T18 anchor drift, isolated: the same fixture run against the `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` baseline prints 26 `BASELINE_MISMATCH` lines in the base clone and 32 in the tip clone (both runs `total=52 pass=52 fail=0`); the six extra paths, `comm -13` of the two sorted path lists, are exactly

```
corpus/knowledge/jj-abandoned-object-mtime-clock.md
tools/souji-census.sh
tools/souji-cert-evidence.py
tools/souji-evidence-cache.py
tools/souji-repo-structure.sh
tools/souji-round9-selftest.sh
```

   (no path disappeared). All six are round-32's own landed files: C3's knowledge entry and five files C2 edited.

## Findings

1. **C2 does not meet `fail=0` at the tip.** `census/round-32/records/c2-after-v1.txt` claims 26/27 at the landing commit; re-derived at the tip the frozen counter reads `pass=25 fail=2`, exit 1 (Evidence 1). Two items fail, for two unrelated reasons (Findings 2 and 3).

2. **T18's frozen anchor is a repo-content fingerprint, so the round's own landings move it.** `tests/fixtures/r20-input-binding.py:1137-1167` (`compare_baseline`) counts every closure file whose sha256 differs from the pinned baseline and prints it into the summary line: `print("BASELINE_MISMATCH\t%s\tcurrent=%s\tbaseline=%s" %` (`tests/fixtures/r20-input-binding.py:89`) increments `self.baseline_mismatches` (`:88`), and the counter compares that whole line for equality. Measured: 26 at base, 32 at tip, the six added paths being C2's five fixed tools plus C3's entry (Evidence 5). Consequence: T18 cannot pass at any tip that contains the round's own work; the item measures byte drift from a 2026-10-21 revision, not TMPDIR operability. This is the miss already recorded at `census/round-32/records/amendments.txt:27` — "`baseline_mismatches=<n>`, a count of closure files that differ from a pinned 2026-10-21 revision`" — and my measurement confirms it independently.

3. **T12's PASS/FAIL is not a property of the landed bytes.** Four readings of `bash tools/souji-census.sh --selftest` at the same tip revision `4e56c48…`:

   | source | base line | sandbox line |
   |---|---|---|
   | this seat, full counter | `rc0 … 69 checks, 0 failed` | `rc1 … 69 checks, 4 failed` |
   | `census/round-32/records/a2-l1-salvage-tip-measure.txt` (item 2, rev `4e56c48…`) | `rc1:W4488:FAIL raw LF path refusal exits: root=2 compare=2` | `rc1:W5929:selftest: 69 checks, 2 failed` |
   | this seat, direct sandbox replay ×3 | — | `69 checks, 0 failed`, exit 0, three times |

   The predicate is `ok_a = rc1 == rc0 and s1 == s0 and s0 != "NONE"` (`census/round-32/c2-counter.py:174`), an exact string compare of the last digit-bearing line, and that line's value is produced by wall-clock-bounded checks — e.g. `st_bad "watchdog wall time ${timeout_ms}ms (want < 6000ms)"` (`tools/souji-census.sh:2541`, observed margin 3979 ms of 6000 ms in a passing run) and the nine 2-second Git calls (18 458 ms in a passing run). At the top of the run the base line itself flips between `rc0 … 0 failed` and `rc1 … 2 failed` on the identical base commit. Mechanism (load-sensitive timing, not bytes) is `[INFERENCE]`: I could not force a failing sandbox run at load 17 with one contended core, so I did not reproduce the exact count; the *variance* is directly observed in all four readings above. Net effect: C2's `fail=0` is a host-state property for T12, and a T12 FAIL is not evidence that the landed fix regressed.

4. **C3 holds at the tip and is not disturbed by anything landed after it.** Both instruments pass all legs at `4e56c48…` (Evidence 2 and 3), including L15 (live recent/old gc probe), L16 (shim exit-status reality) and L17 (live re-fetch of every snapshot). Minor, harmless: leg L12's printed `git_calls` count is not run-stable — 369 (v1) and 368 (v2) in this measurement, 366 and 365 in `census/round-32/records/a2-l1-salvage-tip-measure.txt`, at the same revision; the leg's predicate does not compare the count (`census/round-32/c3-counter.py:261` checks exit 0, equal RESULT lines and the presence of each required call shape), so no target moves. `[INFERENCE]` the variance is the fixture's own git auto-maintenance/repack call count.

5. **Working tree was dirty during the measurement (observation, not a defect of the claims).** `git -C … status --porcelain` at tip time: ` M SKILL.md`, ` M tests/fixtures/r15-preservation-frozen/expected.json`, ` M tests/fixtures/r15-preservation-frozen/record.json`, ` M tools/souji-receipt-run.py`, `?? census/round-32/records/a2-l1-salvage-tip-measure.txt`. All three counters read objects at `--rev` through `clone --no-local`, so no measured number depends on these edits; the L1 should know they are pending in the tree it will land from.

## Attack log

A1 — **T18 is unsatisfiable while the round lands its own work** (frozen item set, not counter logic). Reproduced state: Evidence 5 (26 → 32, six named paths, fixture exit 0 in both runs). Impacted axis: operability (C2's target), with coverage (C3) as the co-cause. Smallest safe correction is the L1's to choose and must be stricter-only and logged: either remove/replace T18 in `census/round-32/c2-items.tsv` by an amendment (the target `fail=0` stays over the reduced set), or keep it and record C2 as a measured miss on T18 alone. My measurement cannot make T18 pass without reverting C2 and C3.

A2 — **T12's verdict is decided by host state, not by the landed diff.** Reproduced state: the four readings in Finding 3 (same rev `4e56c48…`, same argv, base and sandbox lines both moving) plus three direct replays that pass. Impacted axis: operability. Because `ok_a` compares exact summary strings (`census/round-32/c2-counter.py:174`) and the selected line is a wall-clock-bounded self-test count, any seat measuring T12 under fleet load can flip it. Smallest safe correction (L1's call): treat T12's FAIL as `COULD-NOT-EVALUATE` for this round rather than a regression, or amend the item to a count-free line; a T12 PASS obtained at low load must not be read as evidence either.

## Deliveries

- `.ufo/waves/round-32/a2w1/deliver-tip-measure.txt` — raw stdout of the C2 full run, C3 v1 and C3 v2 with exit codes, argv and revisions.
- `.ufo/waves/round-32/a2w1/SwarmExecutor35.md` — this report.

No tool installs or upgrades were needed. Scratch `/fast/scratch/hyaku/souji-r32/RemeasureTip` (two `--no-local` clones, base `85b61a1…` and tip `4e56c48…`, origin removed) removed after the delivery file was written. No git/jj mutation, no writes outside `.ufo/waves/round-32/a2w1/`; lane working tree left exactly as found.
