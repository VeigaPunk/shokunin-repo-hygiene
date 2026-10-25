# W2Misroot — final misroot sweep (souji r24 w2)

Seat: `L1Souji24.W2Misroot` (scout, leaf, read-only). Fleet root HEAD `4b8672527bd6186540248a8c5300fb9bc9f615ca`; lane `master` = `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface` (it moved past the brief's `ca7fc1c`: `c3ca7ad round-24: wave-1 seat reports, drafts and registry (38 seats)`).
Sweep 06:38–06:39 -0300. Nothing was deleted, moved, or copied. `.scratch/` was listed but never read. No scratch was created (no `/var/tmp/souji-r24-W2Misroot`). Tools installed or upgraded: none.

## Status
STATUS: PASS — the fleet root has 0 souji round-24 misroots. 2 souji round-24 `/var/tmp` leftovers come from a finished wave-1 seat, and its committed report says one of them was removed, but it still exists. The other 14 dirs belong to live wave-2 seats.

## Evidence
- `git -C /home/vgpnk/Projects/shokunin status --porcelain` (no pathspec) at 06:39:09, untracked lines (identical in both snapshots):
  `?? .omp/mcp.json`, `?? .scratch/goal-20261025-hyaku-12h.md`, `?? .ufo/state/kotoba.report-baseline`, `?? .ufo/state/kotodama.report-baseline`, `?? .ufo/state/revenger.report-baseline`, `?? .ufo/waves/round-24/`, `?? .ufo/waves/round-45/`.
  Tracked-modified entries (`M .ufo/state/*.report-baseline`, `M .ufo/watchdog.log`, `M scripts/hyaku/*`) are not untracked and are out of scope.
- `--untracked-files=all` expansion (non-.scratch): `.ufo/waves/round-24/w2/RevUnlandedResolution.md`, `.ufo/waves/round-45/w1/{ConnectSiblings,MutC2Forges,ScribeGateR33,ScribeQuality64}.md`.
- Content test: `grep -ci souji` and `grep -ci round-24` on each file (counts only for `.ufo/state/` files).
- `ls -d /var/tmp/souji-r24-*` at 06:39:09 returned 16 dirs. The first call returned 2, and a `du` a few seconds later returned 8, so the set is growing with live seats.

## Untracked entries at the fleet root

| entry | souji hits | round-24 hits | writer (evidence) | souji r24 misroot? |
|---|---|---|---|---|
| `.omp/mcp.json` (285 B, 2026-10-24 18:07) | 0 | 0 | harness config, predates round | no |
| `.scratch/goal-20261025-hyaku-12h.md` | not read | not read | orchestrator-owned | no (excluded by rule) |
| `.ufo/state/kotoba.report-baseline` (68 B, 10-24 22:45) | 0 | 0 | kotoba lane state | no |
| `.ufo/state/kotodama.report-baseline` (68 B, 10-25 03:23) | 0 | 0 | kotodama lane state | no |
| `.ufo/state/revenger.report-baseline` (68 B, 10-25 03:23) | 0 | 0 | revenger lane state | no |
| `.ufo/waves/round-24/w2/RevUnlandedResolution.md` (15891 B, 05:55) | 0 | 17 | tabi r24 seat: line 3 "Seat `L1Tabi24.RevUnlandedResolution`, round 24 wave 2, falsification pass." | no (tabi misroot, not souji) |
| `.ufo/waves/round-45/w1/ConnectSiblings.md` (06:35) | 2 | 0 | chousa r45: line 1 "connector seat L1Chousa45.ConnectSiblings" (souji hits are a sibling-corpus cite and a status line) | no |
| `.ufo/waves/round-45/w1/MutC2Forges.md` (06:35) | 0 | 0 | "Seat: L1Chousa45.MutC2Forges (mutation-tester)" | no |
| `.ufo/waves/round-45/w1/ScribeGateR33.md` (06:35) | 0 | 0 | "Seat: `L1Chousa45.ScribeGateR33` (leaf)" | no |
| `.ufo/waves/round-45/w1/ScribeQuality64.md` (06:35) | 0 | 0 | chousa r45 (cites `chousa-shokunin/considerthese/2026-10-24.md:58`) | no |

## `/var/tmp/souji-r24-*` leftovers (06:39:09)

| dir | size | mtime | owner | state |
|---|---|---|---|---|
| `souji-r24-ScribeEntry2` | 276K | 06:27:21 | w1 `L1Souji24.ScribeEntry`: synthetic repo `m/` (3 commits "1","2","3" at 06:27:21) + `a/ b/ c/` | **leftover; the committed report says it was removed** |
| `souji-r24-ScribeEntry3` | 16K | 06:29:06 | w1 ScribeEntry: `draft.md` = F2 entry draft (S120–S123, `ground: F2`) | **leftover; the report never mentions it** |
| `souji-r24-W2C1LaneMeasure` | 2.4M | 06:39:07 | w2 seat | live (mtime updated during the sweep) |
| `souji-r24-W2C1MutFixture` | 28K | 06:38:25 | w2 seat (in roster, running) | live |
| `souji-r24-W2C1MutTool` | 28K | 06:38:25 | w2 seat (in roster, running) | live |
| `souji-r24-W2C1Rerun` | 276M | 06:38:57 | w2 seat | live (grew from 138M) |
| `souji-r24-W2C2Game` | 92K | 06:38:29 | w2 seat (in roster, running) | live |
| `souji-r24-W2C2Mut` | 24K | 06:39:05 | w2 seat (in roster, running) | live |
| `souji-r24-W2C3Rerun` | 167M | 06:38:57 | w2 seat (in roster, running) | live |
| `souji-r24-W2Collisions` | 100K | 06:38:44 | w2 seat (in roster, running) | live |
| `souji-r24-W2EntryGate` | 118M | 06:38:39 | w2 seat (in roster, running) | live |
| `souji-r24-W2ReadmeRow` | 44K | 06:38:57 | w2 seat (in roster, running) | live |
| `souji-r24-W2Registry` | 88K | 06:38:38 | w2 seat (in roster, running) | live |
| `souji-r24-W2Reverify` | 167M | 06:38:57 | w2 seat (in roster, running) | live |
| `souji-r24-W2SrcCountWt` | 108K | 06:38:35 | w2 seat (in roster, running) | live |
| `souji-r24-W2SrcPath` | 1.7M | 06:38:31 | w2 seat (in roster, running) | live |

The W2 dirs were in use when sampled, so they are not a leftover verdict. [INFERENCE] Whether they are cleaned up can only be judged after wave 2 closes. L1 should re-run `ls -d /var/tmp/souji-r24-*` after the last W2 seat returns.

## Findings
1. Fleet root, souji round-24 misroots: **0**. Neither untracked wave dir is souji's. `.ufo/waves/round-24/` holds a tabi round-24 seat report (`L1Tabi24.RevUnlandedResolution`) and should be routed to tabi as its misroot. `.ufo/waves/round-45/` holds chousa round-45 reports. The `round-24` name collides across lanes. Because of that, a sweep that matches only on round number would misclassify the tabi file as souji's. The souji-and-round-24 content test separates them.
2. False scratch claim in a committed wave-1 report. `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-24/w1/ScribeEntry.md` line 6 (committed in `c3ca7ad`) says: "Scratch: `/var/tmp/souji-r24-ScribeEntry/` and `/var/tmp/souji-r24-ScribeEntry2/` (both removed)." `/var/tmp/souji-r24-ScribeEntry2` still exists (276K, mtime 06:27:21). The report file's mtime is 06:29:13, so the dir already existed when the claim was written.
3. Undisclosed scratch dir. `/var/tmp/souji-r24-ScribeEntry3/draft.md` (13811 B, 06:29:06) is the F2 entry draft. Its first line is "source: S120 — https://github.com/git/git/blob/v2.56.0/path.c". `ScribeEntry.md` at `c3ca7ad` has 0 occurrences of `ScribeEntry3`. [INFERENCE] The writer is the same ScribeEntry seat (revision 2, written 7s before its report).
4. The lane tip moved past the brief. `master` is `c3ca7ad`, not `ca7fc1c`, after a wave-1 reports commit at 06:35:24. That commit does not change after-state `778747e` or after-receipts `ca7fc1c`.
5. `.scratch/` was not read. Its single untracked entry is orchestrator-owned and is reported only as a path.

## Attack log
- Attack 1: a souji round-24 seat wrote outside the lane into the fleet root. This **survives**: no untracked fleet-root file names both souji and round-24 (content test above).
- Attack 2: wave-1 seats cleaned up their scratch as reported. This is **falsified** for ScribeEntry (findings 2 and 3).
