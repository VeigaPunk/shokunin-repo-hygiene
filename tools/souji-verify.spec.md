# souji-verify.sh — binding spec (round 2)

One bash tool, bash + coreutils + git + rg only. Read-only over every
surface it inspects. Fixes round-1 defects D1–D3 by construction.

## CLI

```
tools/souji-verify.sh [--selftest] [--stale-days N] [--json] <path>...
```

- default: print one line per target: `VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-reason<TAB>decisive-evidence`
- `--selftest`: build an isolated fixture git-repo under `mktemp -d`, run
  every fixture case below, assert exact verdict + receipt; exit 0 on all
  pass, 1 otherwise; never touches the live tree.
- `--stale-days N`: mtime threshold, default 1 (older than 1 day).
- exit codes: 0 = evaluated clean; 1 = selftest failure or evaluation
  error; 2 = usage. No other codes.

## Artifact kinds (D2: kind branches)

1. **repo-root** (a directory containing `.git`): SAFE only via
   moved-to-obsidian; else NOT-SAFE(unpushed/dirty counts reported in the
   evidence field: `unpushed=N dirty=M`).
2. **worktree-registration**: path equals a `worktree <path>` entry in
   `git -C <owner> worktree list --porcelain` for the repo that registers
   it (owner = the repo whose `.git/worktrees/` holds the admin dir; detect
   by scanning `$SHOKUNIN_ROOT/*-shokunin` and the fleet root).
   - dir absent AND unique commits = 0 (`git -C <owner> log --oneline
     <HEAD> --not --all | wc -l`) → `SAFE(metadata-prune)`
   - named branch with unpushed commits (`git -C <owner> log --oneline
     <branch> --not --remotes | wc -l` > 0) → `NOT-SAFE(unpushed-branch)`
   - dir present and dirty → `NOT-SAFE(dirty)`
3. **file/dir artifact** (default): receipts in order —
   - `pushed`: introducing commit `git log --diff-filter=A --format=%H -1
     -- <path>` is an ancestor of the default branch ref (D1: resolve with
     `git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null
     | sed 's@^origin/@@'`; fallback: the single local
     `refs/remotes/origin/*` branch ref if exactly one exists; else
     `NOT-SAFE(pushed-unverifiable)` — r5 amendment: local refs such as
     `refs/heads/master` can NEVER establish a pushed receipt).
     NO `git fetch` — existing refs only.
   - `moved-to-obsidian`: row in `corpus/knowledge/obsidian-ledger.tsv`
     with matching source path AND source sha256 AND vault path AND vault
     sha256 (`sha256sum` on both sides, vault side read-only). r5
     amendment: any symlink inside a digest scope fails closed
     (`NOT-SAFE(symlink-present)`) — dropped `-type l` entries produced a
     false-SAFE class.
   - `stale`: scratch type (`.scratch/`, `*.out`, `*.log`, checkpoint
     json/png, `*-draft.*`) AND zero live references (D3: `rg -l
     --no-ignore --basename <name> <repo> -g '!.git' -g
     '!souji-shokunin/census/**' -g '!souji-shokunin/tests/**' -g
     '!**/.ufo-quarantine/**'` returns 0 lines) AND mtime older than
     --stale-days.
   - none → `NOT-SAFE`.

## Safety rails (any violation = selftest failure)

- Never read a file whose basename matches `*.env`, `*credential*`,
  `*secret*`, `id_*`, `*.pem` — verdict such targets `NOT-SAFE(secrets-refusal)`.
- Never run `git fetch/push/commit/branch/checkout/reset/rebase`, never
  write outside `/tmp` mktemp dirs, never touch `.ufo/state`,
  `.ufo/watchdog.log`, `~/.config`.
- Empty/missing target → `NOT-SAFE(unreachable)` (exit stays 0).

## Fixture cases (--selftest must cover all)

F1 file introduced pre-default-branch-tip, ancestor → SAFE(pushed)
F2 file whose introducing commit is local-only → NOT-SAFE(pushed-unverifiable or none)
F3 repo with unpushed commits + dirty tree (kotodama-shaped) → NOT-SAFE
F4 worktree registration, dir absent, unique=0 → SAFE(metadata-prune)
F5 worktree registration, named branch, 1 unpushed commit → NOT-SAFE(unpushed-branch)
F6 ledger-matched file (ledger row + matching sha256 both sides) → SAFE(moved-to-obsidian)
F7 scratch file, no refs, old mtime → SAFE(stale)
F8 scratch file, but its basename appears in a census-like dir → still SAFE(stale) (D3)
F9 origin/HEAD missing, single origin branch ref → resolves branch, F1 re-check passes (D1)
F10 path containing `.env` → NOT-SAFE(secrets-refusal)
