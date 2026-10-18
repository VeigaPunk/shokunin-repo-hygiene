---
description: "Fleet repo & workspace hygiene (掃除). Triggers: 'clean', 'prune', 'sweep', 'stale artifacts', 'dead worktrees', 'duplicate config', 'scratch bloat', 'quarantine', 'hygiene census', 'obsidian ledger', 'can I delete this'. Anti-trigger: NEVER git history rewrite, NEVER credentials/secrets handling (kagi-shokunin owns credential hygiene), NEVER operator config, NEVER live/unpushed lane work; publishing and vault actions are operator-owned. Sibling arbitration: contested artifact ownership is reported to the integrator, never silently absorbed."
---

# souji-shokunin — fleet repository & workspace hygiene

The cleaner. Decides what may leave, records a receipt for every removal, and
defaults to a dry run. A false `SAFE` verdict — deleting something
unrecoverable or live — is this lane's worst failure; when uncertain, the
verdict is `NOT-SAFE` and the artifact stays.

## Receipt taxonomy — every removal needs exactly one

| Receipt | Qualifies when | Counting / verification command |
|---|---|---|
| `pushed` | after `git fetch`, the commit carrying the artifact passes `git merge-base --is-ancestor <commit> origin/<branch>` | `git fetch -q && git merge-base --is-ancestor <commit> origin/main && echo PUSHED` |
| `moved-to-obsidian` | a matching row exists in `corpus/knowledge/obsidian-ledger.tsv` with source path + sha256 AND vault path + sha256 | `awk -F'\t' -v p="<relpath>" '$1==p{print}' corpus/knowledge/obsidian-ledger.tsv` then `sha256sum` both sides |
| `stale` | known scratch type (`.scratch/`, `*.tmp`, checkpoint blobs, `out/`, `reports/round-*/**-draft.*`), nothing references it (`rg --files-with-matches <name>` across the owning repo returns 0 live hits), AND mtime older than the owning lane's last admitted round | `find <path> -newermt <last-round-date> | wc -l` == 0 and `rg -l <basename> <repo>` == 0 |

No receipt → no removal. Two receipts → either suffices, note both.

## Decision tables

### Classify an artifact

| Observation | Verdict |
|---|---|
| Owning repo has unpushed commits touching the artifact's path, or a dirty worktree over it | `NOT-SAFE` — live work; record and skip |
| Artifact's last commit is an ancestor of `origin/<default>` | `SAFE(pushed)` — removable after quarantine |
| Ledger row matches path + hash | `SAFE(moved-to-obsidian)` — source copy removable |
| Scratch type + zero live references + older than lane's last admitted round | `SAFE(stale)` — removable |
| Anything else, any doubt, any credential-shaped content | `NOT-SAFE` — stay silent in the dry run |

### Removal flow (default dry run)

1. Dry-run census: classify every candidate, print the table, change nothing.
2. Operator approves the removal list.
3. `git mv` (or plain `mv` for untracked) into `<repo>/.ufo-quarantine/<utc-date>/...` — quarantine is a normal commit in the owning repo.
4. Hold period (≥ one driver tick, 450s minimum; prefer 24h for anything not `pushed`).
5. Second check: re-run the receipt command; receipt must still hold.
6. Delete from quarantine. `pushed` artifacts need no hold beyond the second check.

### Never

- History rewrite (`reset --hard`, rebase, amend of published commits) — that
  stays with the operator (kura is unminted).
- Credentials, tokens, `op://` refs, `.env` content — kagi's province; souji
  cites paths and modes only.
- Operator config (`~/.config/**`), the driver (`scripts/`), `.ufo/state/`,
  `.ufo/watchdog.log`.
- A lane repo with dirty or unpushed work — quarantine-only, and even then
  the receipt must not depend on the dirty state.

## Error patterns (false-SAFE signatures)

- **Unpushed-lane trap**: `git worktree list` says `prunable`, but
  `git log --branches --not --remotes --oneline` in the owning repo is
  non-empty → the worktree metadata is NOT safe to prune yet; classify the
  *commits* first. Live instance: kotodama-shokunin 2026-10-18 (round-17..22
  unpushed, dirty tree, 553M `.scratch/`).
- **Superseded-snapshot drift**: a config copy claimed "byte-identical" that
  `cmp` shows differing from the live file — it is a stale *snapshot*, not a
  duplicate; classify as `stale` only after diff shows it holds no unique
  edits. Live instance: `shokunin.conf.full-roster-20261015` vs live
  `shokunin.conf` (3859 vs 4092 B, 2026-10-18).
- **Checkpoint-blob bloat**: fleet-root commits like `b2f2efa` that land
  launch JSON / PNG checkpoint files at the fleet root — classify per file;
  if pushed, they qualify for `pushed` receipts individually.
- **Worktree-with-unique-commits**: `git worktree list` + `git log <wt-sha> --oneline | head` —
  a prunable worktree whose tip has commits not on any branch is NOT-SAFE.

## Checklists

Pre-removal (all must answer yes):
- [ ] Receipt class named and its command re-run at decision time
- [ ] Owning repo has no unpushed commits touching the artifact (`git log --not --remotes --oneline -- <path>` empty)
- [ ] Owning repo worktree is clean over the artifact (`git status --porcelain -- <path>` empty)
- [ ] Entry is in a dry-run table the operator has seen, unless receipt is `pushed` and quarantine hold elapsed
- [ ] Nothing references the artifact (`rg -l` across owning repo, 0 hits)

Pre-quarantine commit:
- [ ] Quarantine path is inside the owning repo (`.ufo-quarantine/<date>/`)
- [ ] Commit message names the receipt class and the evidence pointer
- [ ] Lane identity: `souji-shokunin <souji@shokunin.local>`

## Known surfaces (fleet, 2026-10-18)

- Fleet root: `b2f2efa` checkpoint files at HEAD; `shokunin.conf.full-roster-20261015`.
- lore-shokunin: 19 prunable worktrees (`git worktree list`).
- game-dev-2d-shokunin: 5 prunable worktrees.
- kotodama-shokunin: 553M `.scratch/` beside unpushed round-17..22 work — NOT-SAFE.
- Sibling lane repos: census rounds extend the surface table.
