---
description: "Fleet repo & workspace hygiene (掃除). Triggers: 'clean', 'prune', 'sweep', 'stale artifacts', 'dead worktrees', 'duplicate config', 'scratch bloat', 'quarantine', 'hygiene census', 'obsidian ledger', 'can I delete this'. Anti-trigger: NEVER git history rewrite, NEVER credentials/secrets handling (kagi-shokunin owns credential hygiene), NEVER operator config, NEVER live/unpushed lane work; publishing and vault actions are operator-owned. Sibling arbitration: contested artifact ownership is reported to the integrator, never silently absorbed."
---

# souji-shokunin — fleet repository & workspace hygiene

The cleaner. Decides what may leave, records a receipt for every removal, and
defaults to a dry run. A false `SAFE` verdict — deleting something
unrecoverable or live — is this lane's worst failure; when uncertain, the
verdict is `NOT-SAFE` and the artifact stays.

## Receipt taxonomy — every removal needs exactly one

The machine form of this table is `tools/souji-verify.sh` (installed
behavior wins over this prose; r6 reconciliation). Verdicts also include
`SAFE(metadata-prune)` for dead worktree registrations and fail-closed
refusals (`pushed-unverifiable`, `symlink-present`, `secrets-refusal`).

| Receipt | Qualifies when (as the tool checks it, r6) |
|---|---|
| `pushed` | the path exists now; its introducing commit (`git log --diff-filter=A --format=%H -1 -- <path>`) is an ancestor of the resolved default ref (`refs/remotes/origin/HEAD`, else the single `refs/remotes/origin/*` ref — existing refs only, NEVER `git fetch`, NEVER a local ref such as `refs/heads/master`); AND no unpushed commit touches the path (`git log --branches --not --remotes --oneline -- <path>` empty — bare `--not --remotes` alone returns nothing on git 2.55). Any failure → `pushed-unverifiable` / `unpushed-commits-touching`. |
| `moved-to-obsidian` | a ledger row whose canonical ABSOLUTE source path matches AND both sha256 pairs verify (vault side read-only). Symlinks in a digest scope → `symlink-present`. No row → no qualification. |
| `stale` | scratch type as the tool classifies: `.scratch/`, `*.out`, `*.log`, `launch-*.json`, `*-draft.*` (NOT `*.tmp`, not `out/`) AND zero live references (sweep excludes `.git`, `souji-shokunin/census/**`, `souji-shokunin/tests/**`, quarantine) AND mtime older than `--stale-days` (default 1). |

No receipt → no removal. Two receipts → the tool reports the first that
verifies (pushed before obsidian).

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

## Known surfaces (fleet, refreshed r6)

- Fleet root: `b2f2efa` checkpoint files at HEAD (96 actionable approval
  rows await the operator; 15 shell strays were already removed by a1b44b1);
  `shokunin.conf.full-roster-20261015` (superseded snapshot, SAFE/pushed).
- lore-shokunin: 19 dead worktree registrations PRUNED r3 (list now 1); a
  small `.scratch` (218 KB) flagged by the r6 fleet census.
- game-dev-2d-shokunin: 2 detached registrations pruned r3; 3 named-branch
  registrations PINNED (locks held; each branch has 1 unpushed commit) —
  a 5th worktree appeared by r6 (live lane work; classified by census).
- kotodama-shokunin: `.scratch` measured 553M → 1.9G → 16G → **40.4 GB**
  across r1–r6, live-written by its unpushed round-14..53 work — NOT-SAFE;
  handoff note at `census/round-6/kotodama-scratch-handoff.md`.
- Repeatable fleet census: `tools/souji-census.sh --root $SHOKUNIN_ROOT`
  (r6; per-repo worktrees/unpushed/dirty/scratch/mtime/flags).
