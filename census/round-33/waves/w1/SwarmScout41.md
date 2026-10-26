# SwarmScout41 — assimilation sweep (r33 w1)

## Status
STATUS: PASS — sweep and id-collision check done; verdict `Assimilation: none` (0 ADMIT-CANDIDATE, 12 hits all REJECT). Delivery: `.ufo/waves/round-33/w1/deliver-assim-sweep.md`.

## Evidence
- Read `/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md` (134 rows, 68 entries); `find knowledge -type f | wc -l` = 68 (read-only; nothing written there).
- Case-insensitive grep over the 68 entries: TMPDIR 0, tempfile 0, mkdtemp 0, mktemp 0, gettempdir 0, trailing slash 0, selftest 0, capabilit 0, SCORECARD 0, EROFS/read-only mount 0, currency 3 files (git remote-ref freshness, plus the substring in "concurrency"), scratch 8 files (git-prune probe locations). Same words over `SOURCES.append.md` (pathname resolution, proc_pid_fd, gettempdir, tempfile, mkdtemp, TMPDIR): 0.
- Id-collision (round prompt `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-33.md:517-538`, 0-3-space pattern), registry from `git show 2d9bca55a9f042a2c9ed60a797a8069e74c41f46:corpus/SOURCES.md`, in `/fast/scratch/hyaku/souji-r33/AssimSweep/A/`:
  `147 reg-ids`, `134 staged-ids`, `39 collisions` = S109-S132, S152, S210-S223 (registry max S223; staged S109-S242). Indented-fixture proof: 0-3 pattern -> `S002 S109`; column-zero pattern -> `S109` (S002 missed). Registry has 0 indented rows. Round 32 read 146/134/38.
- Tools used: grep, comm, awk, git read-only. No installs.

## Findings
1. No staged entry serves C1: zero capability or SCORECARD hits; the 3 "currency" hits are git remote-ref staleness (`fleet-prune-currency-r30.md:25` "remote-side currency that round 9 could assert for all 26 can now be asserted for 24") or a substring false hit (`fleet-live-exposure-r27.md:45`). REJECT.
2. No staged entry serves C2: no TMPDIR/tempfile/mkdtemp/trailing-slash content. The `scratch` hits record where a probe ran. Two (`garbage-false-positive-modes-r25.md:3` "scratch /var/tmp/souji-r25-matrix.XXXXXX, no residue"; `-r26.md:3` "scratch under /var/tmp, removed by the trap") show the hard-coded-root pattern QUALITY Q71 forbids. REJECT.
3. Per-hit table with 12 located quotes: deliverable §2.
4. 10 staged paths already exist at 2d9bca55 in `corpus/knowledge/` (listed in deliverable §2); 2 dangling citations (S022) in MERGE-REPORT.md.
5. 39 id collisions: any later adoption must renumber from S224 by document. None this round: no append.
6. The round-33 mechanism sources for C2 (POSIX repeated slashes, proc_pid_fd(5), Python tempfile TMPDIR search) are absent from the package; the lane has to open them itself.

## Deliveries
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-33/w1/deliver-assim-sweep.md`
- Scratch `/fast/scratch/hyaku/souji-r33/AssimSweep` removed after writing (see end of this run).
