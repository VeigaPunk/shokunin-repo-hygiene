# SwarmScout14 — assimilation sweep

## Status
STATUS: PASS — all 68 staged entries swept, every hit read, one draft row per candidate, collision guard run; no staged entry admits as the C3 entry.

## Evidence
- Read: /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-31/records/preregistration.txt (C3 paragraph, line 20); /home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md (68 entries, 134 rows, "first staged id is **S109**" line 9); PROVINCE.md:63-65 (F1 definition) and the r30 boundary note ("the object-prune clock that follows a dropped keep ref is unmeasured here").
- `grep -rliE 'reflog|keep ref|refs/jj|prune|unreachable' .../merge/souji/knowledge/` → 45 of 68 files. `grep -ciE 'refs/jj|keep ref|jujutsu|\bjj\b'` → exactly 1 file: fleet-prune-safety-r28.md (3 lines). Reflog named in 11 files, incidentally.
- C3 L6 criterion: /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-31/c3-counter.py:149 `fresh = sorted(i for i in cited if i in rows and i not in base_rows and rows[i][9] == "2026-10-26")`. Staged rows opened 2026-10-23/24.
- Collision guard (scratch /fast/scratch/hyaku/souji-r31/SwarmScout14, since removed): lane 145 ids (S001-S221), staged 134 ids (S109-S242), `comm -12` = **37** collisions (S109-S132, S152, S210-S221). Neither side has duplicate ids (`uniq -d` empty).
- Name overlap, `for f in staged; [ -e lane/corpus/knowledge/$f ]`: 10 staged entries already exist in the lane by name (duplicate-verdict-identity, git-auto-maintenance-trigger-set, -r23, origin-record-durability-r28, origin-record-exclusivity-r28, origin-record-mechanism-set-r33, origin-record-writer-r27, quarantine-origin-record-fields-r24, quarantine-staging-no-copy-r23, repo-size-census-readonly) although MERGE-REPORT marks them new-file.
- Lane already holds S116 git-fsck and S117 git-prune (same pages as staged S113/S114) and S002/S063 gc grace/reachability.

## Findings
1. No staged entry measures object lifetime behind a dropped jj keep ref; the only staged text naming `refs/jj/keep/*` is fleet-prune-safety-r28.md (receipt-root rule: "refs/jj/keep/* ref, which Q28 requires to be NOT-SAFE"), a fleet census of 26 registrations, F1 but not C3.
2. Closest to C3: git-grace-period-at-release-r35.md (names `gc.pruneExpire` 2 weeks for unreachable loose objects separately from the worktree expiry; S226 git-config 2.56.0 and S227 git-gc 2.52.0). The lane already carries those claims via S002/S063 and git-grace-periods-and-expire-to.md. Draft: REJECT as entry, USE as source lead; flip if the C3 author re-opens a doc URL on 2026-10-26 and registers it as S222+.
3. Staged rows cannot satisfy C3 L6 as written: opened dates are 2026-10-23/24 and 37 ids collide; they would have to be re-opened and renumbered.
4. repo-size-census-readonly.md is a duplicate target path (lane copy cites S116/S117). Reject.
5. The git-reflog doc named as the C3 candidate is not in the staged set; sweeps of reflog-bearing entries (community recipes, vendor runbooks, fsck `--no-reflogs`) are history-rewrite or census material the PROVINCE refuses or places in F2.
6. Merge package is stale against the lane: id space starts at S109 but lane is at S221; adoption of any row needs renumbering plus rewriting every `source:` line in the cited entries.
7. Per-candidate admit/reject rows (12 rows, flip conditions): see delivery file.

## Deliveries
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/deliver-assim-sweep.md

No tools installed. Nothing written in shokuknow or elsewhere in the fleet.
