STATUS: DONE — Added cwd/argv/fd residue classification with one reason per PID; selftest, live census, and JSON exclusive-create check passed.

# LeakCounter — WAVE 1 BUILD

## Scope and behavior

- Added `census/round-18/leak-count.py` in the assigned clone only. It scans `/proc` for the current real UID and counts each qualifying PID once. Classification precedence is `cwd-deleted` > `argv-path-gone` > `fd-path-gone`; `by_reason` reports those exact keys. Evidence: `census/round-18/leak-count.py:101-119,121-167`.
- The fd classifier considers `/proc/<pid>/fd/*` links ending in ` (deleted)` only when their target is under `/var/tmp/`, `/tmp/`, or `/dev/shm/` and the first scratch component is gone. Prefix matching requires the slash boundary, so `/tmpfoo/...` is not treated as `/tmp/...`. Evidence: `census/round-18/leak-count.py:37-50,68-89`.
- `by_prefix_family` now partitions counted PIDs using the family for the selected primary reason. Families are `r15-census-config`, `r17-census-hygiene`, and `other`. Evidence: `census/round-18/leak-count.py:121-167`.
- `--selftest` checks `/tmpfoo` boundary rejection, creates a blocked FIFO reader in a new session under `/var/tmp`, removes the directory, asserts one argv-path-gone PID, and kills/reaps its process group in `finally`. Evidence: `census/round-18/leak-count.py:172-235`.
- `--json OUT` exclusively creates the output file. Evidence: `census/round-18/leak-count.py:239-266`.
- Verdict: **holds for the executed selftest, live census, and exclusive-create probe**. No smallest fix identified.

## Retained evidence

Baseline read: `census/round-18/leaked-procs-before-1631.txt:1-58` contains 58 listed PIDs. In the updated live run, the `cwd-deleted` group is 58 and matches those baseline PIDs; the fd classifier additionally finds seven PIDs, for a total of 65. The seven additional fd-only PIDs were `1659, 1845, 1983, 2147, 863272, 2154933, 2257336`.

Selftest output:

```json
{
  "added_pid": 1752043,
  "after": 66,
  "before": 65,
  "selftest": "pass"
}
```

Final live read-only output:

```json
{
  "by_prefix_family": {
    "other": 7,
    "r15-census-config": 44,
    "r17-census-hygiene": 14
  },
  "by_reason": {
    "argv-path-gone": 0,
    "cwd-deleted": 58,
    "fd-path-gone": 7
  },
  "counted_at": "2026-10-20T20:12:24.594616+00:00",
  "pids": [
    1659,
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
  "total": 65,
  "uid": 1000
}
```

Exclusive-create probe output:

```text
first_rc=0
leak-count: [Errno 17] File exists: '/var/tmp/souji-r18-LeakCounter/proc-json-exclusive.json'
second_rc=1
```

The temporary JSON file was removed after the probe.

## Commands and outputs

Commands ran from `/home/vgpnk/Projects/shokunin` unless the command names its clone explicitly.

1. Clone and pin the assigned base:

```text
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18-LeakCounter/lane && git -C /var/tmp/souji-r18-LeakCounter/lane checkout --quiet --detach b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
```

Output: no stdout/stderr.

2. Final authorized fixture selftest:

```text
python3 /var/tmp/souji-r18-LeakCounter/lane/census/round-18/leak-count.py --selftest
```

Output is the selftest JSON shown above (`before=65`, `after=66`, PID `1752043`, `pass`).

3. Final authorized read-only live census:

```text
python3 /var/tmp/souji-r18-LeakCounter/lane/census/round-18/leak-count.py
```

Output is the full live JSON shown above (`total=65`, with 58 cwd and 7 fd detections).

4. Exclusive-create probe, with its temporary artifact cleanup:

```text
python3 /var/tmp/souji-r18-LeakCounter/lane/census/round-18/leak-count.py --json /var/tmp/souji-r18-LeakCounter/proc-json-exclusive.json; printf 'first_rc=%s\n' "$?"; python3 /var/tmp/souji-r18-LeakCounter/lane/census/round-18/leak-count.py --json /var/tmp/souji-r18-LeakCounter/proc-json-exclusive.json; printf 'second_rc=%s\n' "$?"; rm -- /var/tmp/souji-r18-LeakCounter/proc-json-exclusive.json
```

Output is the three lines shown above: first create succeeded; second failed with `EEXIST` and status 1; temporary file removed.

5. Scoped patch refresh:

```text
git -C /var/tmp/souji-r18-LeakCounter/lane diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- census/round-18/leak-count.py > /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-18/w1/LeakCounter.patch
```

Output: no stdout/stderr. The delivered patch contains only the assigned new file.

## Risks and blockers

- This is a point-in-time `/proc` scan; processes may start or exit during enumeration, and procfs access races are skipped for that PID.
- No blockers. No tools installed or updated.
