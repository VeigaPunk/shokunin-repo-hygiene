## Status
STATUS: PARTIAL — O_TMPFILE traced; first probe used inaccessible fake-tool path under bwrap and did not execute creation, so rerun corrected probe required.

## Evidence
- Frozen contract `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/preregistration.txt:81-88`: “file-creation witness: sandboxed run's strace creations >= half of base's” (quote 10 words).
- Witness parsing `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c2-counter.py:157-178`: trace lines must regex-match syscall name in `(open|creat|mkdir|rename|link|symlink|mknod|truncate)\(`, flags include `O_CREAT|O_WRONLY|O_RDWR|mkdir|creat`, and text path includes tmp/vt.
- Probe command used `strace -f -qq -e trace=%file ... bwrap ...`; `/proc/loadavg` at probe start: `26.05 13.83 6.84 29/7343 1389040`.
- O_TMPFILE observed trace excerpt: `openat(AT_FDCWD, "/fast/scratch/hyaku/souji-r34/ProbeWitnessRace/tmp", O_RDWR|O_CLOEXEC|O_TMPFILE, 0600) = 3`; it is a create with tmp path but parser's syscall-name regex does not match `openat(`. The earlier fake script was outside the sandbox-visible filesystem and execution did not reach its file creation; no result claimed for that case.

## Findings
1. [ATTACK, preliminary] O_TMPFILE creation uses `openat`, which the current regex misses because it expects `open(` rather than `openat(`; this could undercount genuine work and may deny a valid witness. Location: c2-counter.py:177-178. Confidence: high on parser behavior; low on full pass/fail impact until corrected probe.

## Attack log
- Hypothesis not yet fully adjudicated. Cheapest stricter-only amendment if reproduced: recognize `openat(` (and flag `O_TMPFILE`) in create matcher; do not alter frozen target/leg.

## Deliveries
- `.ufo/waves/round-34/w1/SwarmScout39.md`
