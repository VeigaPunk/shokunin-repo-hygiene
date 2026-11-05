# S67ConnectorOverlap — shokuknow assimilation scan (read-only)

Read: `/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md` (and its `.json`, `SOURCES.append.md`, `knowledge/`).
Read-only; nothing written.

## What the staged package is

- `MERGE-REPORT.md` header: staged by `corpus-expansion-1`; "Nothing was written into the lane repo"; 134 rows accepted,
  68 knowledge entries; "lane registry currently holds **108** rows; first staged id is **S109**" (MERGE-REPORT.md:5-9).
- Staged themes by name (knowledge file names): `git-auto-maintenance-trigger-set` (-r23), `repo-size-census-readonly`,
  `quarantine-staging-no-copy` (-r23/-r24), `duplicate-verdict-identity` / `duplicate-verdict-taxonomy-r24`,
  `count-objects-garbage-semantics-r23/r24`, `garbage-false-positive-modes-r25..r27`, `fleet-maintenance-config-r24`,
  `fleet-exposure-r24`, `fleet-live-exposure-r25/r27`, `fleet-prune-*-r28..r33`, `prune-trigger-levers-r28`,
  `prune-lever-paths-r30`, `prune-lever-matrix-r36`, `prune-expiry-mechanism-r36`, `prune-upstream-durability-r36`,
  `origin-record-*` (r26..r33), `near-duplicate-*` (r28..r33), `community-*` (reclamation, worktree, zh-ja),
  `gitlab-reclamation-*`, `git-grace-period-*` (r34..r36), `reclamation-deadline-kinds-r25..r27`.

## Topic check (the four assigned routes)

Grep over the package (`MERGE-REPORT.md`, `MERGE-REPORT.json`, `SOURCES.append.md`, `knowledge/`):

| route | hits | verdict |
|---|---|---|
| receipt-writer env routes (`GIT_COMMON_DIR`, `GIT_CONFIG_*`, `RECEIPT-ENV`, `receipt-writer`) | 0 for `GIT_COMMON_DIR`, `RECEIPT-ENV`, `receipt-writer`, `GIT_CONFIG_PARAMETERS` | no match |
| common-dir resolution | `commondir` appears only in `count-objects-garbage-semantics-r24.md` (common_list in git's path.c) and `garbage-false-positive-modes-r25.md:31-33` (`different_commondir` decides whether the `garbage` sweep fires) | adjacent, census-side only |
| mode bits (`core.fileMode`, file mode, permission bits) | 0 | no match |
| statement-agreement counters | 0 (the word "statement" appears only in prose) | no match |

Assimilation verdict (one line for the report): **none matches**
(adjacent only: `corpus/knowledge/garbage-false-positive-modes-r25.md` §3, `count-objects-garbage-semantics-r24.md`, which
concern the census's `count-objects` sweep under linked worktrees, not the writer's GIT_COMMON_DIR route).

## Staleness and id collision (noted, not actioned)

- The package is pinned to a 108-row baseline; the lane now holds 222 registry rows (`corpus/SOURCES.md`; r66 landing).
- Staged ids S109–S236 collide with ids the lane already holds: `corpus/SOURCES.md:144` holds `| S109 | souji round-2 RENAME_NOREPLACE probe…`
  and an existing `| S236 |` row. The package cannot be appended as staged; the adopt checklist's renumber step is required
  before any use.
- Two knowledge entries cite `S022`, which is not in the package (MERGE-REPORT "Dangling citations"); this is a pre-existing
  gap in the package.

## considerthese

- `test -d /home/vgpnk/Projects/shokunin/souji-shokunin/considerthese` → **absent** (`ls` reports "No such file or directory").
  Nothing to list. The round-66 lesson records the same absence (`corpus/lessons/round-66.md` Gate, "Assimilation: none").
  Sibling lanes kumitate, kake and kama do have `considerthese/` directories; souji does not.
