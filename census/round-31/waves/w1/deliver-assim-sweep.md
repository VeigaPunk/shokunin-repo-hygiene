# Assimilation sweep — shokuknow/merge/souji vs C3 (jj dropped-keep object lifetime)

Seat SwarmScout14, round 31 wave 1. Read-only over /home/vgpnk/Projects/shokuknow/merge/souji/ (MERGE-REPORT.md, SOURCES.append.md, 68 staged entries); nothing written there.

## Headline

- No staged entry measures object lifetime behind a dropped jj keep ref. Sweep: `grep -ciE 'refs/jj|keep ref|jujutsu|\bjj\b'` over the 68 staged entries hits exactly one file, `fleet-prune-safety-r28.md` (3 lines), and those lines are a fleet safety classification, not object lifetime.
- Broad grep `reflog|keep ref|refs/jj|prune|unreachable` hits 45 of 68 entries; the large majority are the *worktree-registration* prune family (not objects) [INFERENCE from reading the 12 entries above, not counted]. Reflog is named in 11 entries, always incidentally (vendor runbooks, history-rewrite recipes, `fsck --no-reflogs`).
- C3's L6 requires a cited row absent at base AND `opened=2026-10-26` (c3-counter.py:149 `rows[i][9] == "2026-10-26"`). Every staged row is opened 2026-10-23/24, so no staged row satisfies L6 verbatim. Using one means re-opening the URL this round and registering it under a fresh id.
- Id-collision guard (scratch only): lane ids 145, staged ids 134, `comm -12` = **37 collisions**: S109-S132, S152, S210-S221. Lane max is S221; any adopted staged row must be renumbered to S222+ and every citing entry rewritten. 10 of 68 staged entries already exist by name in the lane (below).

## Candidate table (subject touches object pruning / reflog / keep refs / gc reachability)

PROVINCE F1 = "git-native housekeeping vs receipts — git's own deleters (`maintenance --auto` worktree-prune, gc/reflog grace periods) acting on surfaces souji gates" (PROVINCE.md:63-65). PROVINCE.md r30 boundary note says the object-prune clock behind a dropped keep ref is unmeasured.

| # | staged entry | what it claims | cited sources | F1 scope | serves C3 | draft | reason | flip condition |
|---|---|---|---|---|---|---|---|---|
| 1 | repo-size-census-readonly.md | count-objects/fsck/prune are three census instruments; `fsck --lost-found` writes; `prune` leaves packed unreachable; fsck default heads include index+reflogs | S112 S113 S114 (git 2.56.0 man pages) | ground F2, not F1 | no (census instruments; no jj, no clock) | REJECT | same target path already in lane (`corpus/knowledge/repo-size-census-readonly.md`, cites S116/S117 = same pages); staged S113/S114 duplicate lane S116/S117; ids collide | none; only fold per checklist step 6 if lane text lacks a claim (lane text carries the same 4 points) |
| 2 | git-grace-period-at-release-r35.md | at 2.56.0: `gc.worktreePruneExpire` 3.months.ago; `gc.pruneExpire` 2 weeks governs unreachable loose objects; gc prunes reflog/rerere/stale worktrees; `maintenance.worktree-prune.auto` int default 512 | S226 git-config/2.56.0, S227 git-gc/2.52.0, S228, S230 | F1 | partial: the only staged text naming the object expiry (2 weeks) separately from the worktree expiry; no keep ref, no reflog-vs-descendant measurement | REJECT as entry; USE as source lead | lane already holds the object-expiry claims (S002 "loose objects 2 weeks, reflog 90 days (30 if unreachable)"; S063 reachability; `git-grace-periods-and-expire-to.md`); S226 git-config 2.56.0 URL is not in the lane registry | flips to usable if the C3 author re-opens the git-config/2.56.0 (or git-reflog/git-gc 2.56 doc) URL on 2026-10-26, takes a located quote for `gc.reflogExpire`/`gc.pruneExpire`, and registers it as S222+ |
| 3 | git-grace-period-semantics-r34.md | gc runs `worktree prune --expire 3.months.ago`; `now`/`never`; `--expire` one age filter; task switch reach | S218 S219 S220 (v2.45.0 docs source) | F1 | no (worktree registrations; its own "does not establish" says `gc.pruneExpire` objects are out) | REJECT | wrong subject; pinned v2.45.0 not 2.56.0; ids S218/S219/S220 collide with lane rows (link(2), jj CLI reference, operation-log) | none for C3; for general F1 adoption after renumbering |
| 4 | prune-expiry-mechanism-r36.md | manual `worktree prune` expire defaults to TIME_MAX, reads no config; gc.c passes 3.months.ago as an argument; `2.weeks.ago` default is a sibling field for objects | S237 S238 (v2.48.0 source) | F1 | no (worktree prune mechanism) | REJECT | wrong subject; v2.48.0 pin | none |
| 5 | fleet-prune-safety-r28.md | 26 prunable registrations all SAFE(metadata-prune), receipt roots = every ref except `refs/jj/*`; none held only by a `refs/jj/keep/*` ref (Q28 NOT-SAFE); auto path inert | S165 S166 (own-work evidence files under shokuknow lanes/), S160 S161 (v2.56.0 source) | F1 | context only: it is the sole staged text naming `refs/jj/keep/*`, but states the rule not a lifetime measurement | REJECT | fleet census snapshot of other lanes' repos (stale, 26 vs later 40); evidence files are outside the lane; its ids S160/S161/S165/S166 do not collide with lane ids | none; C3 must be a scratch measurement |
| 6 | count-objects-garbage-semantics-r23.md | `garbage` is debris not graph state; fleet census; vendor GC grace (30 min, 90 % lock); Atlassian reflog-expire then `gc --prune=now` | S112 S113 S127-S131 | F2 | no | REJECT | wrong ground; vendor tier-B behaviour; lane already has `count-objects-linked-worktree-garbage.md` / `count-objects-garbage-readings-r25.md` | none |
| 7 | community-reclamation-practice-extended-r28 / -r28 / -r29 / -r30 / -r31 (5 files) | community recipes: filter-branch/BFG, reflog expire, aggressive prune, then push | tier-C community rows S163 S164 S174 S181 S183 etc. | adjacent: history rewrite is PROVINCE Refuses | no | REJECT | the recipe is what the lane refuses; tier C; no jj | none |
| 8 | git-grace-period-japanese-r36.md | Japanese statements of the same worktree grace clause | S240 S241 S242 | F1 (worktree) | no | REJECT | wrong subject; S242 evidence file is a shokuknow-local decoded copy | none |
| 9 | prune-lever-matrix-r36 / prune-lever-paths-r30 / prune-expiry-behaviour-r29 / prune-trigger-levers-r28 / fleet-prune-expiry-selection-r35 | worktree-prune selection under expiry/config levers, fleet counts | S185 S194 S229 S235 | F1 (worktree) | no | REJECT | wrong subject (registrations, not objects); fleet counts stale | none |
| 10 | reclamation-deadline-kinds-r25 / r26 / r27 | hosted services' GC grace (unreachable AND older than N), Gitea `fsck --unreachable` cron | S127 S128 S150 S214 S215 | F2 adjacent | no | REJECT | self-hosted service policy, not git/jj | none |
| 11 | fleet-exposure-r24, fleet-live-exposure-r25/r27, fleet-maintenance-config-r24, git-auto-maintenance-trigger-set(-r23), community-worktree-literature-r35 | mention reflogs or `pruneExpire` incidentally in worktree-prune/trigger context | various | F1 (worktree) | no | REJECT | two trigger-set entries already in lane by name; others fleet snapshots | none |
| 12 | remaining 20-odd `prune` hits (gitlab-reclamation-*, near-duplicate-*, origin-record-*, quarantine-*, duplicate-*, garbage-false-positive-*) | reclamation settings / duplicate verdicts / origin records; `prune` or `unreachable` appears only incidentally | various | F2/F3/F4 or off-province | no | REJECT | off subject | none |

## Verdict for C3

No staged entry is admissible as the C3 entry, and none is usable verbatim as its source row (opened date and id collision). The only staged material of value is a lead: S226/S227 show git-scm.com serves git-config for 2.56.0 and git-gc (2.52.0 newest). C3's candidate git `Documentation/git-reflog.adoc` at v2.56.0 (preregistration C3 paragraph) is not in the staged set at all. The C3 author should open a fresh row this round and measure with real jj 0.45.1 + git 2.56.0 in scratch; nothing from shokuknow substitutes. The lane-held rows S002/S063/S054/S220/S221 remain citable (preregistration allows them) but do not satisfy L6 alone.

## Id-collision guard (verbatim)

```
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' <lane>/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort   -> 145 ids (S001..S221, 0 duplicates)
same over shokuknow/merge/souji/SOURCES.append.md                                                 -> 134 ids (S109..S242, 0 duplicates)
comm -12 lane.ids staged.ids | wc -l                                                              -> 37
colliding ids: S109-S132 (24), S152, S210-S221 (12)
```

Consequence: the merge package's "first staged id is S109" (MERGE-REPORT.md:9) predates the lane's own growth to S221; the 134 staged rows cannot be appended as written.
