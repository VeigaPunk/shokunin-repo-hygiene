STATUS: DONE — Aligned the blind counter with the refined cwd/argv/fd predicate and passed the synthetic selftest and live census.

# LeakCounterFix — W1 follow-up

## Scope and behavior

- Updated only `census/round-18/leak-count.py` in the refreshed private clone based at `5efb519`.
- Cwd classification is unrestricted by scratch prefix. It requires a `readlink` target ending in ` (deleted)` and compares the target path inode against `/proc/<pid>/cwd`; an existing literal pathname ending in that text is not considered deleted. Evidence: `census/round-18/leak-count.py:50-63,117-127`.
- Argv candidates are only full absolute argv elements or `--option=/absolute` values. Embedded substrings are ignored. Both the candidate and its first scratch component must be missing via `os.path.exists`, so a dangling symlink counts as missing. Prefix matching is component-bounded. Evidence: `census/round-18/leak-count.py:35-47,66-81`.
- FD candidates are `/proc/<pid>/fd/*` links ending in ` (deleted)`, excluded when the raw target and proc fd link resolve to the same device/inode, then checked against the scratch prefixes and missing top-level directory. Evidence: `census/round-18/leak-count.py:50-63,84-105`.
- Classification is one row per PID with `cwd-deleted` > `argv-path-gone` > `fd-path-gone` precedence. The census skips its own PID and ancestor PIDs. Evidence: `census/round-18/leak-count.py:117-202`.
- Synthetic selftests cover a literal live cwd suffix, a literal live fd suffix, an actual deleted fd, embedded argv text that must not match, full-absolute and `--option=/absolute` argv forms, a dangling top-level symlink, and `/tmpfoo` component-boundary rejection. The existing FIFO fixture also verifies +1 detection and process-group cleanup. Evidence: `census/round-18/leak-count.py:205-374`.
- Verdict: **holds for the executed selftest and live census**. No smallest fix identified.

## Retained evidence

Baseline `census/round-18/leaked-procs-before-1631.txt:1-58` has 58 PIDs; the live `cwd-deleted` cohort matches those 58. Six additional live PIDs were classified `fd-path-gone`: `1845, 1983, 2147, 863272, 2154933, 2257336`.

Selftest output:

```json
{
  "added_pid": 2400870,
  "after": 70,
  "before": 69,
  "selftest": "pass"
}
```

Final live output:

```json
{
  "by_prefix_family": {
    "other": 6,
    "r15-census-config": 44,
    "r17-census-hygiene": 14
  },
  "by_reason": {
    "argv-path-gone": 0,
    "cwd-deleted": 58,
    "fd-path-gone": 6
  },
  "counted_at": "2026-10-20T21:37:28.326304+00:00",
  "pids": [
    1845,
    1983,
    2147,
    185592,
    185605,
    289650,
    289668,
    365980,
    366021,
    562276,
    562277,
    562279,
    574643,
    574984,
    574987,
    574989,
    596478,
    596479,
    596480,
    597162,
    597357,
    597358,
    597359,
    598877,
    598890,
    639553,
    639568,
    812467,
    812480,
    863272,
    918756,
    918769,
    1026787,
    1026800,
    1242228,
    1242241,
    1555085,
    1555223,
    2154933,
    2257336,
    2475440,
    2475453,
    2572254,
    2572307,
    2629870,
    2629891,
    2650283,
    2650499,
    2764974,
    2764987,
    2800031,
    2800121,
    2984182,
    2984195,
    3050160,
    3050173,
    3139964,
    3139977,
    3252942,
    3252974,
    3848039,
    3848052,
    4037294,
    4037365
  ],
  "total": 64,
  "uid": 1000
}
```

## Commands and outputs

Commands ran from `/home/vgpnk/Projects/shokunin` unless stated otherwise.

1. Create and pin the refreshed private clone:

```text
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18-LeakCounterFix/lane && git -C /var/tmp/souji-r18-LeakCounterFix/lane checkout --quiet --detach 5efb519
```

Output: no stdout/stderr.

2. Confirm the assigned file is tracked at this base:

```text
git -C /var/tmp/souji-r18-LeakCounterFix/lane ls-files -- census/round-18/leak-count.py
```

Output:

```text
census/round-18/leak-count.py
```

3. Run the requested synthetic/FIFO selftest:

```text
python3 /var/tmp/souji-r18-LeakCounterFix/lane/census/round-18/leak-count.py --selftest
```

Output is the selftest JSON shown above (`before=69`, `after=70`, PID `2400870`, `pass`).

4. Run the requested read-only live census:

```text
python3 /var/tmp/souji-r18-LeakCounterFix/lane/census/round-18/leak-count.py
```

Output is the full live JSON shown above (`total=64`; 58 cwd and 6 fd detections).

5. Write the scoped patch against the requested base:

```text
git -C /var/tmp/souji-r18-LeakCounterFix/lane diff 5efb519 -- census/round-18/leak-count.py > /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-18/w1/LeakCounterFix.patch
```

Output: no stdout/stderr. The patch contains only the assigned file.

## Risks and blockers

- `/proc` is a point-in-time interface: processes can start/exit during enumeration, and access races are skipped for the affected PID.
- No blockers. No tools installed or updated.
