# SwarmScout21 — assimilation sweep

## Status
STATUS: PASS — sweep done read-only; 43 candidates tabled, id-collision guard run (146 lane, 134 staged, 38 collisions); delivery written. Nothing in the package serves C2 or C3 directly: recommend REJECT for all in wave 1.

## Evidence
- Revision: lane tip `git rev-parse HEAD` = 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1; package /home/vgpnk/Projects/shokuknow/merge/souji (read only).
- `grep -rliE 'cruft|mtime|pruneExpire|prune|TMPDIR|/var/tmp' knowledge | wc -l` -> 43. Per term: cruft 0 entries, 0 rows in SOURCES.append.md; `.mtimes|gitformat-pack|cruftPacks` 0 files; TMPDIR 0 files; `/var/tmp` 6 files; pruneExpire 13 files; mtime 6 files.
- Guard (scratch /fast/scratch/hyaku/souji-r32/AssimSweep/): lane 146 ids, staged 134 ids, `comm -12` 38 = S109-S132, S152, S210-S222.
- Path collisions staged vs lane corpus/knowledge: 10 of 68 (all `cmp` DIFF).
- Fresh-row rule: census/round-32/c3-counter.py:229 requires `opened == 2026-10-26` and absent at base; all staged rows are opened 2026-10-23/24.
- Quotes: MERGE-REPORT.md "first staged id is **S109**"; git-grace-period-at-release-r35.md "`gc.pruneExpire` defaults to **2 weeks** and governs unreachable loose"; git-grace-period-semantics-r34.md "It does not describe the `git gc --prune=<date>` expiry for *unreferenced".

## Findings
1. No staged entry or row covers cruft packs, `.mtimes`, `gc.cruftPacks` or object mtime as a clock: C3 needs a fresh gitformat-pack row; nothing to adopt. (grep counts above.)
2. Object-expiry content is limited to `gc.pruneExpire` as a second variable: git-grace-period-at-release-r35.md:30-32, prune-expiry-mechanism-r36.md:31-33, fleet-maintenance-config-r24.md:21-22. Documentation only, no measurement.
3. Every `prune` hit beyond those is worktree-registration pruning; the mtime hits are `worktrees/<id>/index` or `gitdir` mtimes (fleet-prune-safety-r28.md:44-46, fleet-grace-period-exposure-r34.md:34), a different clock.
4. No staged entry teaches TMPDIR discipline (0 files contain TMPDIR); 6 record literal `/var/tmp` fixture scratch (opposite of C2). No C2 item (census/round-32/c2-items.tsv) is a staged file.
5. Adoption poison: 38 id collisions with differing sources, 10 path collisions with differing bytes, rechecks pointing at fixtures absent from the lane. Lane already holds count-objects/fsck/prune/fetch/rename/mv/statx under shifted ids (S115/S116/S117/S128/S110/S111/S114).
6. Usable for C3 without adoption: lane rows S063, S117, S002, S054 (see deliver file section 4). Optional secondary: re-open staged S227/S238 this round, renumber S223+.
7. Side observation: corpus/knowledge/jj-dropped-keep-object-lifetime.md recheck uses `${TMPDIR:-/var/tmp}` (an entry line, not a C2 item).

## Deliveries
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-assim-sweep.md

Tools installed: none.
