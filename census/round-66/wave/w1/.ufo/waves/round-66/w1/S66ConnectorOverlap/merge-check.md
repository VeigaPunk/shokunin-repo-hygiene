# merge-check — S66ConnectorOverlap (souji round 66, post-freeze w1)

Target: `/home/vgpnk/Projects/shokuknow/merge/souji/` — READ-ONLY. No campaign tool was run there;
nothing was written into shokuknow.

## What exists

- `MERGE-REPORT.md` (17.4 KB) — present, read in full. Header: "Merge package — souji. Staged by
  `corpus-expansion-1`. **Nothing was written into the lane repo.**"
- `MERGE-REPORT.json` (29.5 KB) — machine twin of the same package.
- `SOURCES.append.md` (166.3 KB) — the 134 proposed rows to append to `corpus/SOURCES.md`
  (ids S109+, first staged id S109; lane registry currently holds 108).
- `knowledge/corpus/` — the 68 proposed knowledge entries.

## Package numbers (from MERGE-REPORT.md)

- proposed rows accepted: **134**, refused: **0**; proposed knowledge entries: **68**.
- rows by round: round1=14, round10=9, round11=3, round12=3, round13=14, round14=10, round15=9,
  round16=8, round2=9, round3=9, round4=5, round5=6, round6=5, round7=10, round8=11, round9=9.

## Staged theme names (the 68 knowledge files, grouped by subject)

1. Git auto-maintenance trigger set (+ its r23 re-parse): fetch/merge/rebase/pull auto-maintenance,
   worktree-prune task, `pull.rebase` route.
2. Repo-size census instruments; `count-objects` garbage semantics; garbage false-positive modes.
3. Quarantine staging (no-copy/`RENAME_NOREPLACE`), per-item origin records (fields, GLib writer,
   O_EXCL+rename, durability, GVFS format, exclusivity).
4. Duplicate verdict family: identity, taxonomy, receipt-class decision (deferred), near-duplicate
   threshold/operating point/relations/literature (incl. zh-ja community records).
5. Fleet maintenance config & exposure: stock defaults, prune triggers/levers/lever matrix,
   expiry behaviour/mechanism, prune durability/currency/upstream safety, fleet prune census drift,
   grace-period exposure and `git gc --prune` argument semantics (EN+JA sources).
6. Reclamation deadlines: three-plus deadline kinds, self-hosted shapes, GitLab `housekeeping_*`
   settings/config/name-window/phantom, community reclamation practice (EN + zh-ja).
7. Scheduler scan (nothing runs a prune).

## Term scan over the package directory (MERGE-REPORT.md, MERGE-REPORT.json, SOURCES.append.md, knowledge/)

Alternation, case-sensitive: `GIT_CONFIG_COUNT|GIT_OBJECT_DIRECTORY|GIT_REPLACE_REF_BASE|
core\.excludesFile|status\.showUntrackedFiles|RECEIPT-INDEX|receipt writer|st_mode|setuid|setgid|
sticky|showUntracked` → **No matches found** (zero hits in the whole merge package).

## Named themes touching round-66 ground?

- receipt-writer **env routes** (E1–E6 class): **none.** No staged row or entry mentions any
  `GIT_*` env variable or git config injection.
- **untracked visibility** (`status.showUntrackedFiles`, `core.excludesFile`, `.gitignore`,
  `.git/info/exclude`): **none.** The prune/worktree rows talk about `$GIT_DIR/worktrees`
  registration pruning and grace periods, not about worktree status reads.
- **mode bits** (setuid/setgid/sticky, permission-bit recording): **none.**

## Flags found in the package (informational, not round-66 ground)

- Dangling citations: `quarantine-origin-record-fields-r23.md` and `-r24.md` cite `S022`, which is
  not in the package.
- Three staged rows (S143, S169, S170) point at pages the lane's registry already holds (S042/S057,
  S002/S063, S001) — duplicate-target warnings for the operator's adopt checklist.

## Verdict

The staged souji merge package is entirely gc/prune/quarantine/duplicate-threshold ground. **No
staged theme touches receipt-writer env routes, untracked visibility, or mode bits** — zero overlap
with round-66 C1 (operability matrix rows E1–E6, MOD2/MOD3, SY3) or C2 (SKILL.md statement
population s1–s5). Adopting the package cannot perturb this round's frozen claims.
