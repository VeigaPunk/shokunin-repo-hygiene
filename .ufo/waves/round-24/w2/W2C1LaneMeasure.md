# W2C1LaneMeasure — r24 w2 FALSIFY: `census/round-24/size-census-lane.txt`

## Status
STATUS: PASS — every check asked for was run. The `rev=`/`tool_sha256=` header **survives**. The no-fleet/no-cleanup bound **survives**. The *description* of `unreachable=1093` is **falsified in part**: U is mostly loose trees written at commit time, not jj keep refs or the cruft pack, and `--no-reflogs` adds 0 objects. The tool was re-run once, read-only, and its +8 drift is fully explained.

## Evidence
All commands ran on the lane with git 2.56.0. `master` = `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface` (this is the wave-1 reports commit, one past `ca7fc1c`). `git diff --stat ca7fc1c master -- census/ corpus/ tools/ tests/` is empty, so the artifact and the tool are unchanged at the tip.

1. Header digest:
   - `git show 778747eb…:tools/souji-size-census.py | sha256sum` → `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d`. This equals the header `tool_sha256=`, and the working-tree `sha256sum tools/souji-size-census.py` gives the same value.
   - `git log -- tools/souji-size-census.py` lists only `778747e` and `1efe406`, so the `rev=778747e` blob is the last tool change.
   - The artifact landed in `ca7fc1c` (`git log -- census/round-24/size-census-lane.txt`).
2. One tool re-run: `python3 -B tools/souji-size-census.py --repo /home/vgpnk/Projects/shokunin/souji-shokunin` at 09:38:48Z with HEAD `c3ca7ad` → rc=0, empty stderr:
   ```
   count.count=5855  count.size=40680  count.in_pack=1544  count.packs=3  count.size_pack=8791
   garbage=0 size_garbage=0 unreachable=1101 alternates=0
   ```
   A `.git` manifest (`find .git -printf '%p %y %m %s %T@'`, sorted) taken before and after the run had an empty `diff`. `ls .git/lost-found` → "No such file or directory".
3. Decomposition, read-only, with `GIT_OPTIONAL_LOCKS=0 -c gc.auto=0 -c maintenance.auto=false`. No `--lost-found` anywhere; the before/after manifests again had an empty diff, and there was still no lost-found.
   - `fsck --unreachable --no-reflogs --no-progress` → 1101. `fsck --unreachable --no-progress` (reflogs as roots) → 1101. `comm` of the two OID sets: 0 only in the first, 0 only in the second.
   - Types: `999 tree`, `102 blob`, `0 commit`.
   - Store, from `git show-index` per pack:
     - cruft `pack-4e7d760b…` (has `.mtimes`): 71 objects, 71 in U, all blobs;
     - `pack-6f97363d…`: 0 in U; `pack-f9f38aac…`: 0 in U;
     - loose: 1030 (999 trees + 31 blobs).
   - Loose-U mtime by day: 10-18 31, 10-20 152, 10-21 507, 10-25 340. Every one of the 999 loose U trees has an mtime within 1 s of some `git log --all --format=%ct` commit time (hit=999). The 31 misses are the 31 loose blobs.
4. Drift, 1093 → 1101:
   - 77 loose files are newer than the census `utc=2026-10-25T09:34:49Z` (`find .git/objects/?? -newermt`). That matches count 5778 → 5855; `in_pack` and `packs` are unchanged.
   - Exactly 8 of the 77 are in U, all trees: four with mtime 09:34:57Z (= `ca7fc1c` committer time) and four with mtime 09:35:24Z (= `c3ca7ad` committer time).
   - Each of the 8 holds only the paths its commit added. For example, `2c7e01a4…` = `records` + `size-census-lane.txt`, and `b994d9fa…` = the 6 `c*-after`/gate/r13 receipts. The chains run `census`→`round-24`→`records` and `.ufo`→`waves`→`round-24`→`w1`.
   - Keep refs went 425 (ScoutLaneMeasure) → 443 now.
5. Receipt check: `python3 -B tools/souji-receipt-run.py verify --root /home/vgpnk/Projects/shokunin/souji-shokunin census/round-24/size-census-lane.txt` → `RECEIPT-MALFORMED	header order or fences do not match receipt v1`, rc=2.
6. Records search:
   - `git grep -n -E '1093|size-census-lane' master` (excluding `census/operator-sweep-*` and rounds ≤23) found these lane records: `corpus/README.md:516`, `corpus/knowledge/count-objects-linked-worktree-garbage.md:93`, and `preregistration.txt:67`, plus wave-1 seat reports.
   - No record outside the artifact quotes the number `1093`. `SCORECARD.md`/`LOG.md`: no hit.

## Findings
1. **[Medium, calibration] Line 1 attributes U to the wrong mechanisms.** `size-census-lane.txt:1` says: "not a plain-clone figure (jj keep refs + cruft pack; see .ufo/waves/round-24/w1/ScoutLaneMeasure.md)". Measured at the re-run, U = 999 loose trees written at commit times, 31 loose blobs, and 71 cruft-pack blobs.
   - Back-computed at census time: 991 + 31 + 71 = 1093. [INFERENCE: this assumes no object left U between the runs; no ref change touches these trees, and only +77 objects were added.]
   - So the cruft pack is 6.5% of U, and keep refs only *lower* U. ScoutLaneMeasure.md:60 has the direction right: "They also suppress `unreachable`". The header gives no direction.
   - The cited scout's Finding 4 inference is falsified for most of U: "U therefore counts old debris that was already packed away, not new debris" (ScoutLaneMeasure.md Finding 4). 1022/1093 objects were loose; 340 of them were written on 10-25.
   - The figure itself is true. Only its gloss is wrong.
2. **[Low, calibration] `--no-reflogs` is not mentioned, and its effect here is zero.** ExecSizeCensusTool.md:99 says: "Objects reachable only from reflogs are therefore counted as unreachable". On this lane at this moment, the reflog-only set is empty (Evidence 3). No commit is unreachable, because keep refs and branches cover every commit. The header's silence on `--no-reflogs` therefore does not misstate 1093.
3. **[Low, operability / Q55] The artifact cannot be checked by the lane's verifier.** It lacks `receipt=v1`, and its `rc=` line comes after the stdout fence, so `verify` refuses it (`RECEIPT-MALFORMED`, Evidence 5).
   - The Q55 row (`corpus/QUALITY.md`) says: "A count quoted in a lane record must name a receipt that binds the revision and the sha256 of the bytes that produced it."
   - No record quotes 1093 today (Evidence 6), so Q55 is not tripped. But the header digest is only manually true, and any future quote of the figure would have no verifiable receipt to cite.
4. **[Low, calibration] The figure was stale when it landed, and the header does not bind repository state.**
   - `rev=` is the tool's revision. HEAD and dirty state at the run are not recorded. [INFERENCE: HEAD was `778747e`, committed 09:33:39Z, before the 09:34:49Z run.]
   - The commit that landed the artifact (`ca7fc1c`, 09:34:57Z, 8 s later) itself added 4 unreachable trees. So U was 1097 at the moment the file was committed.
   - Line 1's "at the moment of the run" discloses this; ScoutLaneMeasure.md also says "A rerun after any jj or git activity will differ".
5. **[Survives] No fleet figure and no cleanup recommendation.**
   - `preregistration.txt:66-67`: "It is a figure about this repo only; no fleet figure is claimed."
   - `corpus/README.md:516`: "one lane-bound measurement, no fleet figure".
   - Entry `count-objects-linked-worktree-garbage.md:97-99`: "No fleet figure. Nothing outside this lane was read." The same entry at `:119`: "No cleanup advice."
   - No lane record turns U into prunable/gc/cleanup advice. This seat also proposes none: the commit-time trees in Finding 1 are reported as composition, not as candidates for removal.

## Attack log
| # | Attack | Command | Result |
|---|---|---|---|
| A1 | Header `tool_sha256` is not the blob at `rev=` | `git show 778747e:tools/souji-size-census.py` piped to `sha256sum` | survives (digests equal) |
| A2 | The tool changed after `rev=` | `git log -- tools/souji-size-census.py`; `diff --stat ca7fc1c master` | survives |
| A3 | The re-run writes to `.git` or creates lost-found | manifest diff before/after; `ls .git/lost-found` | survives (empty diff, absent) |
| A4 | U is driven by keep refs / cruft / `--no-reflogs` as described | fsck ± reflogs, per-pack `show-index`, types | **falsified in part** (Finding 1, 2) |
| A5 | Drift is unexplained | `find -newermt`, tree mtimes vs committer times | survives (+77 objects, +8 U trees from 2 commits) |
| A6 | The artifact verifies as a receipt | `souji-receipt-run.py verify` | **falsified** (RECEIPT-MALFORMED; Finding 3) |
| A7 | A lane record turns it into a fleet or cleanup figure | `git grep` over lane records | survives (Finding 5) |

## Residual risk / gaps
- [INFERENCE] What writes the commit-time partial trees is not identified (jj or the L1's commit helper). It is observed at 2/2 commits and matched for all 999 loose U trees by mtime.
- Overlap between the keep-ref-only objects and the U stores was not computed.
- Disclosure: one exploratory `Grep` over `census/**` printed a few incidental lines from `census/operator-sweep-2026101{8,9}/` files. Those contents were not used, and every later search excluded them.
- Scratch was used only at `/var/tmp/souji-r24-W2C1LaneMeasure/` and was removed. No lane writes other than this report.
- Tools installed or updated: none.
