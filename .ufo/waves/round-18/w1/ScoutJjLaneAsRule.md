STATUS: DONE — `--as` acceptable values are exactly the owning repo's recorded lane id or `protocol`; `q_jj_commit_recipe` hardcodes `souji`, so its printed runbook fails in 7 of the fleet's 8 jj lanes.

# Scope

R1 scout. Files read: `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh` (:80-143, :185-235, :370-480, :479-543, rest by grep), `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane-selftest.sh` (grep only), `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh` (:1-123, :200-273, :519-583, :599-643, :1540-1580, rest by grep). No edits. No commits. No tool installs (none needed).

# 1. Exact rule for an acceptable `--as`, and where the lane id lives

**Interface.** `jj-lane.sh commit <lane-dir> --as <id> -m <message> [--allow-large] -- <path>...` (`jj-lane.sh:54`). `--as`, `-m` and at least one path are mandatory; otherwise `usage`/exit 2 (`:495-507`). `--as` is a commit-only option (push takes none; `cmd_push` re-derives `lane_id` itself at `:690`).

**Syntax gate.** `case $id in *[!a-z0-9-]*) err "bad --as id: $id"; exit 64` (`jj-lane.sh:508`). So the id must be non-empty and consist only of lowercase `a-z`, digits `0-9`, `-`. Same charset is enforced for the id at `init` (`:372`, "bad lane id", exit 64).

**Identity gate.** `[ "$id" = "$lane_id" ] || [ "$id" = protocol ] || { err "--as must be the lane id ($lane_id) or protocol: $id"; exit 1; }` (`jj-lane.sh:516-517`). `lane_id` comes from `lane_id_jj` (`:106-111`): read the **repo-level jj `user.name`** and strip the literal suffix `-shokunin`; any other `user.name` shape returns failure and commit aborts with "no lane identity recorded (run: jj-lane.sh init)" (`:515`).

**Where it is stored.** `init` writes three repo-scoped records (`jj-lane.sh:426-440`):
- `jj config set --repo user.name "<id>-shokunin"` (`:427`) and `user.email "<id>@shokunin.local"` (`:428`) — the value `lane_id_jj` reads back;
- `jj config set --repo revset-aliases."trunk()" "<branch>@origin"` (`:429`) — the branch `lane_branch_jj` (`:90-96`, strips `@origin`, validates via `valid_branch`) reads back, with `git config lane.branch` as the pure-git mirror (`:439`);
- `git config lane.id "<id>"` (`:440`) — the git-side id mirror.

Physically, jj 0.45.1 keeps the repo-level config **outside the repository**: `jj config path --repo` on the souji lane printed `/home/vgpnk/.config/jj/repos/acda0786460d4a89c9c1/config.toml` (there is no `.jj/repo/config.toml`). The git mirror (`lane.id`) is inside `<repo>/.git/config` and is therefore the portable in-repo record.

**Observed values (read-only, this host):**

| repo | jj `user.name` | `git config lane.id` | acceptable `--as` |
|---|---|---|---|
| souji-shokunin | souji-shokunin | souji | `souji` or `protocol` |
| tabi-shokunin | tabi-shokunin | tabi | `tabi` or `protocol` |
| mado-shokunin | mado-shokunin | mado | `mado` or `protocol` |
| mori-shokunin | mori-shokunin | mori | `mori` or `protocol` |
| tsukuroi-shokunin | tsukuroi-shokunin | tsukuroi | `tsukuroi` or `protocol` |
| kaidoku-shokunin | kaidoku-shokunin | kaidoku | `kaidoku` or `protocol` |
| tameshi-shokunin | tameshi-shokunin | tameshi | `tameshi` or `protocol` |
| kama-shokunin | kama-shokunin | kama | `kama` or `protocol` |

(`/home/vgpnk/Projects/shokunin/*/.jj` matches exactly these eight repos; all eight carry both `user.name=<id>-shokunin` and `lane.id=<id>`.)

**Rule, stated once:** an acceptable `--as` value is per-repo, never global — it MUST equal the lane id recorded in that repository (jj repo `user.name` minus `-shokunin`, equivalently `git config lane.id`) or the literal `protocol`. `souji` is acceptable only in `souji-shokunin`.

**Second enforcement point.** Even if the `--as` gate were bypassed, `push_preflight` (`:196`) refuses to push when any commit in the push range carries an author/committer other than `<lane_id>-shokunin`/`<lane_id>@shokunin.local` or the `protocol-shokunin` pair (`:218-229`). So the owning lane's identity is required, not merely tolerated.

# 2. What `q_jj_commit_recipe` prints, and what consumes it

**Definition** (`tools/souji-quarantine.sh:246-251`), verbatim shape:

```
jj-lane.sh commit <repo> --as souji -m <message> -- <source-rel> <qpath-rel>
```

- `$1` is `$crepo`, i.e. `Q_CREPO=$(canon_path "$REPO")` (`:639`; `canon_path` = `readlink -m`, `:200`) — an absolute, symlink-normalized repo path.
- `$2` is `rel`, the target path with `"$Q_CREPO/"` stripped (`:1270`).
- `$3` is `qpath` with `"$crepo/"` stripped (`:1271`), i.e. `.ufo-quarantine/<UTC-date>/<rel>`.
- Message is `souji-quarantine: stage <rel> into quarantine`.
- All four substituted fields pass through `printf '%q'`; the message is quoted as one word. Callers append two spaces + `# jj owns the index; commit the move through the lane helper naming BOTH the source and the quarantine path -- never a git index/commit recipe`.

Rendered sample (bash `printf` semantics, not an execution of the tool):

```
jj-lane.sh commit /home/vgpnk/Projects/shokunin/foo-shokunin --as souji -m souji-quarantine:\ stage\ docs/a\ b.txt\ into\ quarantine -- docs/a\ b.txt .ufo-quarantine/2026-10-20/docs/a\ b.txt
```

**Use: operator runbook text, advisory only.** Call sites are `:549` (dry-run plan) and `:574` (live stage-2, after the worktree rename). Both do `emit CMD "$raw" "<recipe>…# comment"`, and `emit` joins fields with TABs (`:223-229`), so the row shape is `CMD<TAB><target path><TAB><recipe>  # <explanation>` — the third field of the documented `CMD	<path>	<command that would run / ran>` stream (`:85`). The tool never executes it, never parses it back, never commits, and never invokes the `jj` binary at all (grep for `$JJ_BIN` / `jj --ignore-working-copy` / helper invocation in the tool: no hits); the header states the move is worktree-only under colocation and that "the tool never commits" (`:45-49`, `:100-104`).

**Blast radius.** Only definition + those two call sites (`git grep q_jj_commit_recipe -- tools tests census` → `:246`, `:549`, `:574`). No fixture asserts the recipe: the dry-run check at `:1564` only requires a `git -C` token and an `rm -rf` token in the CMD output. `tools/souji-quarantine.impl-03.sh` is a separate round-8 candidate CLI and does not contain the recipe.

# 3. Verdict: FAILS (fails closed, 7/8 lanes)

The emitted command is refused by the helper in every jj lane except `souji-shokunin`'s own:

- `tools/souji-quarantine.sh:247` hardcodes `--as souji`.
- In e.g. `tabi-shokunin`, `lane_id_jj` yields `tabi` (`jj-lane.sh:106-111`; observed `user.name=tabi-shokunin`, `lane.id=tabi`), so `--as souji` hits `:516-517` and exits 1 with `--as must be the lane id (tabi) or protocol: souji`.
- The refusal happens after `take_lock` and `cd` (`:510-517`), i.e. an operator pasting the runbook line gets a one-line error and exit 1; nothing is committed, so no damage — a usability/operability defect, not a safety one.
- It also contradicts the lane's own documented rule: `SKILL.md:128` says the helper "refuses any `--as` but the lane id or `protocol`". Round-17 lesson R1 (`corpus/lessons/round-17-verifier-spotcheck.md:149`) already names this exact defect and asks for the owner id plus a fixture assertion; per the probe contract the helper was not executed here (commits forbidden), so the refusal is cited from the deterministic shell path above rather than observed at runtime.

# 4. Smallest fix

Replace the hardcoded id with the repo's recorded lane id, validated against the helper's own charset, falling back to the universally accepted `protocol`:

```bash
q_jj_lane_id() { # $1 repo -> owning lane id, or protocol when unknown
  local id
  id=$(git -C "$1" config --get lane.id 2>/dev/null || true)
  case $id in ''|*[!a-z0-9-]*) id=protocol ;; esac
  printf '%s' "$id"
}

q_jj_commit_recipe() { # $1 repo, $2 source rel, $3 qpath rel -> operator recipe
  printf 'jj-lane.sh commit %s --as %s -m %s -- %s %s' \
    "$(printf '%q' "$1")" "$(q_jj_lane_id "$1")" \
    "$(printf '%q' "souji-quarantine: stage $2 into quarantine")" \
    "$(printf '%q' "$2")" "$(printf '%q' "$3")"
}
```

Why this and not `jj config get user.name`:

- `lane.id` is written by `init` (`jj-lane.sh:440`) from the id it already validated (`:372`), is present in all eight lanes, and lives inside the repo; the jj repo config lives outside the repo (`~/.config/jj/repos/<hash>/config.toml`), so it cannot be read portably from the checkouts.
- The quarantine tool currently has no `jj` dependency; this keeps it that way (one `git config --get`, read-only, no lock).
- `protocol` is explicitly accepted by the commit gate (`:516`) and by `push_preflight` (`:218-229`). It is a defensive fallback only: v2 is the first helper that records `lane.id` (`-S lane.id` → `14df5b9` only; v1 `67a3123` wrote `snapshot.auto-track` at its `:152` but neither `lane.id` nor `lane.branch`, and `commit` would already refuse such a lane at `:513-514` for the missing branch). All eight current lanes carry `lane.id`, so the fallback should never fire today; it costs one `case` and keeps the runbook executable if a `lane.id` is ever hand-removed.

Add the assertion round-17 R1 asks for: extend the selftest fixture fleet (`:1465+`) with one colocated repo (`.jj` plus `.git`; `q_jj_colocated` only checks existence, `:244`), set `git config lane.id testlane`, run `--dry-run` on a tracked target, and assert the `CMD` third field contains `--as testlane` and does not contain `--as souji`; a second repo without `lane.id` should assert `--as protocol`.

# Evidence: commands run

```
jj --ignore-working-copy -R .../souji-shokunin config get user.name            -> souji-shokunin
jj --ignore-working-copy -R .../souji-shokunin config get 'revset-aliases."trunk()"' -> master@origin
jj --ignore-working-copy config path --repo   (read-only path query)           -> /home/vgpnk/.config/jj/repos/acda0786460d4a89c9c1/config.toml
git -C <each lane> config --get lane.id                                        -> souji|tabi|mado|mori|tsukuroi|kaidoku|tameshi|kama
jj --ignore-working-copy -R <each lane> config get user.name                   -> <id>-shokunin for all eight
git -C souji-shokunin grep -n "q_jj_commit_recipe" -- tools tests census       -> :246,:549,:574 only
git -C souji-shokunin grep -n "as souji" -- tools tests census corpus SKILL.md -> tool :247; SKILL.md:128 (rule text); round-17 lesson :149
git -C souji-shokunin grep -n "--as\|lane_id\|lane.id" tools/souji-quarantine.sh -> :247 only
grep -n on jj-lane.sh                                                          -> :54,:366-372,:506-517,:690
ls -la .ufo/waves/round-18/w1                                                   -> drop dir present
```

# Remaining unknowns

- The helper's refusal was not executed (commit is a write; forbidden for this seat). The exit-1 path is read from `jj-lane.sh:515-517`, not observed.
- Whether any out-of-tree operator note (outside the lane, e.g. a chat runbook) copies the literal `--as souji` recipe text. In-tree literal mentions: `tools/souji-quarantine.sh:247` (the defective emitter), `SKILL.md:128` (correct example — the souji lane committing through the helper), and the frozen receipt `census/round-13/commit-scope.json:27` (`scripts/hyaku/fleet-commit.sh --as souji` for the souji lane, a different helper and a correct use). Nothing else in `tools/`, `tests/`, `census/`, `corpus/` emits or asserts the quarantine recipe string.
- No non-jj lane is affected: the recipe is emitted only under `q_jj_colocated` (`:548`, `:573`).
