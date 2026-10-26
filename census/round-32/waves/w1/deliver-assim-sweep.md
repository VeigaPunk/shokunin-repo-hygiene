# Assimilation sweep — shokuknow/merge/souji vs souji r32 (read-only; SwarmScout21)

Lane tip read: 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 (`git rev-parse HEAD`). Package: /home/vgpnk/Projects/shokuknow/merge/souji/ (MERGE-REPORT.md: "proposed rows accepted: **134**", "proposed knowledge entries: **68**", "first staged id is **S109**").

## 1. Sweep result in one paragraph

`grep -rliE 'cruft|mtime|pruneExpire|prune|TMPDIR|/var/tmp' knowledge` hits **43** of the 68 staged entries. Per-term file counts: `cruft` **0** files (entries) and **0** lines in SOURCES.append.md; `.mtimes|gitformat-pack|cruftPacks` **0** files in the whole package; `TMPDIR` **0** files; `/var/tmp` 6 files (fixture scratch paths, history only); `pruneExpire` 13 files; `mtime` 6 files; the remaining ~25 hits are the bare word `prune` = `git worktree prune` of stale worktree registrations (the package's subject, F1/F2 worktree-registration reclamation). **No staged entry or row covers cruft packs, object mtimes as a clock, or tool TMPDIR discipline.** The only object-expiry text is `gc.pruneExpire` stated as a second, unmeasured variable (S227, S238, fleet defaults S132).

## 2. Hard blockers that apply to every candidate (verified)

- **Id collision (guard run in scratch /fast/scratch/hyaku/souji-r32/AssimSweep/):** command `grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' <file> | grep -oE 'S[0-9]+' | sort`. Lane /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md: **146** ids (S001..S222, 0 duplicates). Staged SOURCES.append.md: **134** ids (S109..S242, 0 duplicates). `comm -12` collisions: **38** = S109-S132, S152, S210-S222. Spot-checked: same id, different source (e.g. lane S117 = git-prune(1) vs staged S117 = statx(2); lane S218 = link(2) vs staged S218 = git gc.txt v2.45.0; lane S220 = jj CLI reference v0.45.1 vs staged S220 = git maintenance.txt v2.45.0; lane S222 = git-reflog.adoc v2.56.0 vs staged S222 = Pro Git zh). Every `source: S1xx/S2xx` line in a staged entry therefore points at a different lane row: adopting verbatim silently mis-cites (QUALITY traceability). Renumber (lane max is S222; next free S223+, and C3 will use some) is mandatory.
- **Lane already holds equivalents under shifted ids:** lane S115 git-count-objects, S116 git-fsck, S117 git-prune, S128 git-fetch, S110 rename(2), S111 mv(1), S114 statx(2) = staged S112, S113, S114, S109, S116, S115, S117. The package predates those adoptions (MERGE-REPORT: "lane registry currently holds **108** rows"; the lane now holds 146).
- **Path collisions:** 10 of 68 staged paths already exist in lane corpus/knowledge with different bytes (`cmp`: DIFF for duplicate-verdict-identity, git-auto-maintenance-trigger-set, git-auto-maintenance-trigger-set-r23, origin-record-durability-r28, origin-record-exclusivity-r28, origin-record-mechanism-set-r33, origin-record-writer-r27, quarantine-origin-record-fields-r24, quarantine-staging-no-copy-r23, repo-size-census-readonly). Four are in the candidate set below. MERGE-REPORT checklist step 6 is a fold, not an overwrite.
- **Freshness:** every staged row is opened 2026-10-23/24. C3 leg L6 (census/round-32/c3-counter.py:229) needs a cited row absent at base with `rows[i][9] == "2026-10-26"`: no staged row qualifies without being re-opened and re-dated this round.
- **Recheck lines:** staged recheck commands point at fixtures not in the lane (`bash fixtures/r24-fleet-exposure.sh`, `python3 fixtures/r25-garbage-matrix.py`, ...; the fixtures live under shokuknow/lanes/souji/). Adopting them imports unrunnable rechecks.

## 3. Candidate table (admit/reject draft). Verdict = for souji r32 wave 1; PROVINCE = scope against souji PROVINCE.md (F1/F2 in scope; Core/Frontier text read)

Tier A — the only entries touching object expiry (nearest to C3 subject)

| candidate | claims | cited sources | PROVINCE | serves | verdict, reason, flip condition |
|---|---|---|---|---|---|
| git-grace-period-at-release-r35.md | `git gc` runs worktree prune `--expire 3.months.ago`; "`gc.pruneExpire` defaults to **2 weeks** and governs unreachable loose **objects**" (line 30) vs `gc.worktreePruneExpire` for registrations; plus `maintenance.worktree-prune.auto` integer lever | S226 git-config 2.56.0, S227 git-gc 2.52.0, S228 git-maintenance 2.56.0, S230 git-worktree 2.56.0 | in (F1) | C3 only as a pointer (documents the pruneExpire default, no mtime, no cruft, no measurement) | REJECT as entry for C3: does not say where a recent object lives (loose vs cruft), nothing on `.mtimes`, `gc.pruneExpire=never`, `gc.cruftPacks`; ids collide (S226-S230 do not collide with lane, but S227-cited rows opened 2026-10-24). FLIP: if the L1 wants a documented-default citation, re-open S227 this round (2026-10-26), renumber to S223+, cite as a secondary source in C3's Gate; never adopt the entry itself |
| prune-expiry-mechanism-r36.md | worktree.c `expire = TIME_MAX`; gc.c holds `3.months.ago` beside "the unrelated `2.weeks.ago` default for unreachable objects"; gc passes expiry as child argv | S237 builtin/worktree.c v2.48.0, S238 builtin/gc.c v2.48.0 | in (F1) | C3 weak: gc.c is the file that also holds cruft_packs and prune_expire handling, but this entry reads only the worktree-expiry lines (160-162, 206-209, 859-867) | REJECT as entry (worktree-registration subject; pinned v2.48.0, not the 2.56.0 C3 targets). FLIP: only if C3's author needs a gc.c primary source for the `gc.pruneExpire` object default: re-open S238 this round at v2.56.0, take the cruft/prune_expire lines, new row S223+, opened=2026-10-26 |
| git-grace-period-semantics-r34.md | worktree-registration expiry docs v2.45.0; explicitly: "It does not describe the `git gc --prune=<date>` expiry for *unreferenced objects*" (line 52-54) | S218 gc.txt v2.45.0, S219, S220 | in (F1) | none (self-excludes gc.pruneExpire) | REJECT for C3/C2. FLIP: none |
| fleet-maintenance-config-r24.md | fleet runs stock defaults incl. `gc.pruneExpire=2.weeks.ago`, `gc.auto=6700`, `gc.autoPackLimit=50`; no maintenance/gc key in any config | S132 census, S135 | in (F1) | C3 context only (the default clock the fixture's `gc-default` step runs under); not a source for mtime behaviour | REJECT (point-in-time fleet config census from 2026-10-23, own-work row ids collide S132/S135). FLIP: none for r32; re-census only if a later round targets fleet exposure |
| repo-size-census-readonly.md | `git prune` "prunes all unpacked objects unreachable"; "Only expire loose objects older than <time>"; unreachable packed objects remain; `--lost-found` writes | S112 count-objects, S113 fsck, S114 git-prune (lane holds as S115/S116/S117) | in (F2) | C3 partial: the loose-vs-packed split of prune is exactly why a cruft pack changes reach; the lane already holds the same facts as S117 | REJECT: path collides (lane copy differs), rows already held. FLIP: none; the C3 entry cites lane S117 directly |
| reclamation-deadline-kinds-r25.md | three deadline kinds; "an unreachable object must be old before GC frees it" (hosted 30 min); fleet's only deadline is git's own `gc.pruneExpire` / `gc.worktreePruneExpire` | S144 Forgejo cheat-sheet, S127, S132 | in (F2) | none | REJECT. FLIP: none |
| count-objects-garbage-semantics-r23.md / -r24.md | `garbage` counts files not objects (1 in a linked worktree, 0 main); "`garbage: 0` is not a health certificate"; r23 mentions index mtimes ageing toward the 3-month threshold | S130, S131, S112, S113, S127-S129 / S134, S138, S139 | in (F2) | none (no object clock) | REJECT. FLIP: none |

Tier B — worktree-registration mtime (admin-file/index mtime; not an object clock; do not serve C3)

| candidate | claims | sources | PROVINCE | serves | verdict / flip |
|---|---|---|---|---|---|
| fleet-prune-safety-r28.md | `should_prune_worktree()` gate is the registration's `index` mtime; default expiry selects 26; `--expire 2.weeks.ago`/`3.months.ago` select 0 | S165, S166, S160 worktree.c v2.56.0, S161 | in (F1) | none for C3 (mtime of `worktrees/<id>/index`, a different clock; at most a contrast sentence) | REJECT. FLIP: none |
| fleet-grace-period-exposure-r34.md | age measured from `worktrees/<id>/gitdir` admin-file mtime; all 40 prunable registrations past default | S221 | in (F1) | none | REJECT (stale fleet census; collides S221). FLIP: none |
| fleet-live-exposure-r25.md | live registrations' index mtimes recent; `git pull` reaches rebase trigger | S142, S143 | in (F1) | none | REJECT. FLIP: none |
| community-reclamation-practice-r28.md | community says prune on missing worktrees; "command's default expiry is `TIME_MAX`" | S163, S164, S160, S161 | in (F2) | none | REJECT. FLIP: none |
| duplicate-receipt-class-decision-r25.md | a second `cmp` at act time; fclones-style length/mtime is not identity | S145 | in (F3) | none | REJECT (F3 taxonomy decision stays operator-held). FLIP: none |

Tier C — scratch under literal `/var/tmp` (fixture evidence history; no entry teaches TMPDIR discipline)

| candidate | what it says | PROVINCE | serves | verdict / flip |
|---|---|---|---|---|
| fleet-exposure-r24.md, garbage-false-positive-modes-r25.md, garbage-false-positive-modes-r26.md, quarantine-staging-no-copy-r23.md, quarantine-staging-no-copy-r24.md | measurements ran with scratch at literal `/var/tmp` ("scratch /var/tmp/souji-r25-matrix.XXXXXX, no residue", "btrfs-reflink copy ... under `/var/tmp`"); `TMPDIR` appears in **0** staged files | in (F1/F2/F4) | C2 no: C2 items are lane tools/fixtures under /home/vgpnk/Projects/shokunin/souji-shokunin/tools and tests/fixtures, none of which is a staged file; these entries are the same literal-`/var/tmp` habit C2 removes | REJECT for C2 and C3. Adopting would import more literal-`/var/tmp` scratch records and rechecks. FLIP: only if a later round re-measures them under TMPDIR |
| repo-size-census-readonly.md | "what a `/var/tmp` write-safety fixture would have to establish" | in (F2) | none | REJECT (see tier A) |

Tier D — `prune` = worktree-registration prune only (no object clock, no TMPDIR): no relation to C2/C3

| candidate (all in PROVINCE F1/F2 as scoped by their `ground:` lines) | verdict |
|---|---|
| git-auto-maintenance-trigger-set.md, git-auto-maintenance-trigger-set-r23.md (prune a stale registration on fetch/merge/rebase/pull; S123 fixture) | REJECT for r32 (path collision with differing lane copies; ids collide S109-S124). FLIP: fold step per MERGE-REPORT checklist only after the L1 reconciles the two versions |
| fleet-config-scope-resolved-r26, fleet-live-exposure-r27, fleet-prune-census-drift-r33, fleet-prune-currency-r30, fleet-prune-durability-r28, fleet-prune-durability-complete-r32, fleet-prune-upstream-confirmed-r31, fleet-prune-expiry-selection-r35 (fleet censuses 2026-10-23/24, prunable-set counts 16/26/40) | REJECT: point-in-time fleet numbers, not C2/C3; F5/NAMESPACE holds make fresh adoption of "live" census claims unwise; re-measure rather than adopt. FLIP: a round whose claim is the fleet prunable set |
| prune-trigger-levers-r28, prune-expiry-behaviour-r29, prune-lever-paths-r30, prune-lever-matrix-r36, prune-scheduler-scan-r36, prune-upstream-durability-r36 (levers `maintenance.<task>.enabled`, `gc.worktreePruneExpire` values `now`/`never`; scheduler scan) | REJECT: worktree-prune levers; no object clock. FLIP: none for r32 |
| git-grace-period-japanese-r36, community-literature-zh-ja-r34, community-worktree-literature-r35, community-reclamation-practice-extended-r28, -r29, -r30, -r31 (ja/zh community and vendor pages) | REJECT: language-coverage rows (F2), recipes the lane refuses; no relation to C2/C3. FLIP: a coverage round targeting zh/ja F2 |

## 4. What would serve C3 / C2 (feeds the L1; not an admission)

- **C3:** the package has **0** rows on cruft packs or `.mtimes`, so the frozen candidate source (git Documentation/gitformat-pack.adoc v2.56.0) must be fetched fresh this round; nothing staged substitutes. Lane-held rows that C3 can already cite without new adoption: S063 (git-gc reachability + gc.pruneExpire at config/gc.adoc v2.56.0, per jj-dropped-keep-object-lifetime.md `source: S063`), S117 (git-prune: unpacked objects only), S002 (git-gc grace periods), S054 (jj git_backend.rs loose-ref mtime gate). Secondary-only, if re-opened and renumbered: staged S227/S238 for the second expiry variable.
- **C2:** no staged entry. Side observation (not a C2 item, entries are not tools): the lane's own entry corpus/knowledge/jj-dropped-keep-object-lifetime.md `recheck:` line already says `${TMPDIR:-/var/tmp}`, a fallback form the C2 rule lists ("`${TMPDIR:-/var/tmp}`").

## 5. Id-collision guard record

```
lane   SOURCES.md ids : 146  (unique 146, S001..S222)
staged SOURCES.append : 134  (unique 134, S109..S242)
comm -12              : 38   (S109-S132, S152, S210-S222)
```
Files: /fast/scratch/hyaku/souji-r32/AssimSweep/{lane.ids,append.ids,coll.ids} (scratch; removed at finish).
