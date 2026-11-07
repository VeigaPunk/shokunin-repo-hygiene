# Misroot sweep plan — souji round 27 (L1 executable)

Prepared by ExecMisrootPlan (leaf). Purpose: recover byte-exact any file this round's
souji seats wrote at the fleet root (misroot), delete the fleet copy, and record it under
Mistakes. Run this after all r27 seats land, before the round report is finalized.

## Step 0 — sweep (read-only)

```
git -C /home/vgpnk/Projects/shokunin status --porcelain
```

No pathspec. Only `??` (untracked) entries are candidates. `M`/`A`/`D`/`R` entries are
never touched. If file names with spaces/quotes appear, re-run with `--porcelain=v1 -z` and
parse on NUL; the mandated observation command is the one above.

## Step 1 — classify every untracked entry

Protected exclusions — leave alone, never read/copy/delete (any `??` under these is
orchestrator/operator/other-lane state, not a misroot):

- `.ufo/state/` (orchestrator run state, incl. `*.report-baseline`)
- `.scratch/` (orchestrator-owned; NEVER a misroot; do not read contents)
- `MANIFEST.json`, `scripts/`, `templates/` (fleet orchestrator material)
- any `*-shokunin/` directory (sibling lane repos)
- `.ufo/waves/*/*-scratch/`

For every other `??` entry `P` (file, or recursively for a directory), candidate test:

```
grep -qE 'souji' "$P" && grep -qE 'round-27' "$P"
```

Both tokens must hit the same file under `P`. Then ownership check (ALL must pass):

1. The matching file's basename matches a member report path in
   `.ufo/waves/round-27/w1/swarm-registry.json`, or its first lines carry a seat header
   (`# <Name>` / `STATUS:`) naming a registry member.
2. Its mtime falls inside the round-27 wave window (registry `createdAt` 2026-10-25T17:54Z
   through sweep time).
3. Its content names no other lane (only `souji`).

Any failure → DO NOT move: leave the file, name it in the L1 report as unresolved.

## Step 2 — recover each candidate (byte-exact copy → cmp → delete fleet copy)

```
src=/home/vgpnk/Projects/shokunin/$P
dst=/home/vgpnk/Projects/shokunin/souji-shokunin/$P
mkdir -p "$(dirname "$dst")"
cp --preserve=mode,timestamps "$src" "$dst"
cmp "$src" "$dst" && echo "CMP-OK $P"
rm "$src"
test ! -e "$src" && echo "FLEET-COPY-DELETED $P"
```

Guardrails:

- Reject `P` containing `..` or starting with `/` (normalize first; never path-traverse).
- Destination must live under `/home/vgpnk/Projects/shokunin/souji-shokunin/`.
- If `$dst` already exists with different bytes → stop for that file, report the conflict,
  do not clobber.
- After all candidates: re-run Step 0; expect no new `??` besides pre-existing
  non-candidates; verify lane `git -C /home/vgpnk/Projects/shokunin/souji-shokunin
  status --porcelain` shows the landed copies.

## Step 3 — record under Mistakes

Add one row to `corpus/lessons/round-27.md` `## Mistakes` (round-15 format
`id | class | evidence pointer | captured-by | fix`):

```
R27-M<nn> | misroot | <fleet path> copied byte-exact to <lane path>; cmp OK; fleet copy deleted (fleet HEAD ecd8086c) | L1 misroot sweep | relocated into lane; fleet copy removed
```

If the round-27 lesson does not exist at integration time, keep the same row verbatim in the
round report's `## Mistakes` section until L1 creates the lesson.

## Initial state (observed 2026-10-25 before plan)

Fleet porcelain shows one untracked entry: `?? .ufo/waves/round-33/` (single entry
`falsify`, no `souji`/`round-27` token) → zero candidates; no move owed. Fleet `.gitignore`
ignores `*-shokunin/`, so lane bytes inside any lane repo are invisible to porcelain; the
sweep proves absence only at visible fleet paths (round-23 W2Misroot precedent).
