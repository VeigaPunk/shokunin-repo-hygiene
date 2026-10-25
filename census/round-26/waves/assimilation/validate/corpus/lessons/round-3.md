# Round 3 — prune gate
Candidates: 21 worktree registrations + 111 approval targets.
Admitted: C1 (coverage), C2 (calibration).
Rejected: 3 gd2d named-branch registrations (withheld — unpushed commits).
Spot-check: 21 author + 21 blind tickets, 0 disagreements; 7 gate seats.

## What worked

- **Lock-preserve selective prune**: `git worktree lock` on the 3 pinned
  registrations, repo-wide prune, unlock — removed exactly the 2
  authorized gd2d registrations. This is the house pattern for any future
  selective prune; `--expire` is NOT-SAFE (S52: mtime luck).
- **Gate seat ladder**: verify tickets → blind pairs → sweep/pin audits →
  execution plans → consistency → final tally. 0 blocking disagreements.
- **Artifact-scoped dirty/unpushed gate** (SKILL.md pre-removal checklist):
  what matters is whether unpushed work touches the artifact, not the
  owning repo's global state. Record the operator override: a stricter
  reading flips all authorizations — ask via L0 if ever in doubt.

## Findings

- 15 of the 111 approval targets were already removed by fleet commit
  a1b44b1 (unpushed) — the approval list contract must tolerate
  already-removed rows; final list re-cut to 96 actionable rows.
- 4 approval shards used 3 different schemas — next round: one TSV schema
  enforced by the seat template.
- `/tmp` accumulates fixture residue (~2,100 dirs from r2) — host hygiene
  candidate, route to tsukuroi/operator (outside fleet artifacts).
- r87-M1-myth prune leaves 8 unreachable blobs in lore's object store
  (reproducible from the tracked patch) — harmless until a future gc;
  noted for kura/operator when history tooling lands.
