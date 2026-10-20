STATUS: DONE — helper contract is commit+push under the owning lane's identity; SKILL/AGENTS quarantine recipes are not executable through it and one direct-jj route is self-poisoning under C3(b); replacement blocks drafted.

# ConnHelperDocs — `scripts/hyaku/jj-lane.sh` × SKILL.md / AGENTS.md (round 17, wave 1)

Seat: leaf connector, no delegation, no commits, no `jj` invoked, no git writes.
Read-only inputs: helper header+implementation, `SKILL.md`, `AGENTS.md`, `PROVINCE.md`, `JjAuditSouji.md` (F1–F8), live lane state, peer drafts `ScribeSkillJj.md` (same wave).
Installations: none (nothing needed; no pacman/uv/npx transaction was attempted).

## 1. Axes

| axis | what this seat can move | direction |
|---|---|---|
| C3 coverage (jj edge class) | docs must split plain-git vs `.jj` at the exact point of *write*, not just at read | needed |
| C2 calibration | prose that claims a local quarantine commit via the helper is a false claim (the tool pushes) | needed |
| C1 operability | a recipe that would run `git` against a fake/nested `.git`, or `jj` with default auto-track, is an operability regression | guarded |

No axis is harmed by the blocks below; the only rejected move (route quarantine through `jj-lane.sh commit`) would harm C2 and PROVINCE's no-publish boundary.

## 2. Live facts used (commands and exact output)

| command | output |
|---|---|
| `git worktree list` (souji lane) | `/home/vgpnk/Projects/shokunin/souji-shokunin 5fa6017 (detached HEAD)` |
| `git rev-parse --short=12 HEAD` / `refs/heads/master` | `5fa6017ddcae` / `5fa6017ddcae` |
| `git symbolic-ref -q HEAD \|\| echo SYMBOLIC_HEAD=absent` | `SYMBOLIC_HEAD=absent` |
| `git for-each-ref refs/jj/keep` | 8 refs (`0254661 1e0d8d1 41ab059 5fa6017 719154d c46eabf dcc1512 dd2e322`) |
| `ls -A .jj` / `ls -A .jj/repo` | `.gitignore repo working_copy` / `config-id index op_heads op_store store submodule_store workspace_store` — **no `config.toml`** |
| `grep -n 'user\.name\|auto-track' ~/.config/jj/config.toml` | no match (file exists, 187 B) |
| `stat tests/vault/vadv54-run/p/p6repo/.git` | `No such file or directory` (stub absent now) |
| `git ls-tree -r --name-only HEAD -- tests/vault/vadv54-run/p/p6repo` | `.../inner/keep.txt`, `.../one.txt` (the two files C3(e) says jj phantom-deletes) |
| `git check-ignore -q .ufo` / `.ufo/state` | rc=1 / rc=1 — **not ignored**; no root `.gitignore` exists (`ls .gitignore` → No such file) |
| `find .ufo -type f \| wc -l` | 302 |
| `stat .jj .git` (fleet root) | `.jj` absent, `.git` directory → fleet root is plain git |
| `stat .jj/.git` for kama/mado/tameshi-shokunin | `.jj`=dir, `.git`=dir for all three (colocated siblings are live souji targets) |

Helper anchors (711 lines): usage/exit map `:8-10,:54-60`; contract bullets `:16-30`; `lane_realdir` `:74-89`; `lane_branch_jj`/`lane_id_jj` `:90-113`; identity unset `:32-33`; push preflight identity gate `:196-227`; `report_landed` `:234-259`; `do_push` `:346-367`; `cmd_commit` guards `:500-521`, path canonicalization/refusals `:525-552`, deletion inclusion `:543-546` (warn `:548`, empty `:551`), track/diff `:556-578`, same-tip/re-anchor `:580-598`, identity stamp `:599-606`, commit+hash `:607-611`, sweep guards `:609-657`, bookmark set `:658-660`, push `:669`; dispatch `:707-708`.

## 3. Contradictions (helper contract vs souji docs)

Each row is a real conflict between shipped text and shipped code; none is smoothed into a score.

| id | docs say | helper does | consequence |
|---|---|---|---|
| **X1** | SKILL:58/123 make quarantine "a normal commit in the owning repo"; PROVINCE Refuses "publishing … operator-owned"; SKILL:61-62 puts a hold period before deletion | `commit` ends `do_push "$branch" "$id" "$own" || exit 3` (`:669`); no `--no-push` exists (arg loop `:499-505`; dispatch `:707-708`); only `landed <hash>` is citable, printed after `git ls-remote` (`:21-22,:234-259`) | Routing the quarantine commit through the helper **publishes** it; on a repo with no/refusing origin the helper still made the commit then exits 3, and the doc's citable line never appears. A hold-period artifact must not be pushed. |
| **X2** | AGENTS:20 "Commit as `souji-shokunin <souji@shokunin.local>`" | `--as` must equal the repo's recorded lane id or `protocol` (`:516-517`); `push_preflight` rejects any other author/committer in the push range (`:216-227`) | `--as souji` fails in a sibling repo ("--as must be the lane id (<owner>) or protocol"); `--as <owner>` mislabels authorship; `--as protocol` writes `protocol-shokunin`, contradicting AGENTS:20 and souji's own evidence discipline. |
| **X3** | SKILL/AGENTS never mention helper preconditions; a reader is told "use the guarded form" | `commit` requires `.jj` (`:514`), repo jj config `snapshot.auto-track = "none()"` (`:519-521`), `user.name=<id>-shokunin` (`:104-113`), `revset-aliases."trunk()"` (`:92-101`), and working copy base == branch tip (`:586-598`) | Live souji lane has **no `.jj/repo/config.toml`** and no jj `user.name` anywhere → `commit` exits 1 "no lane identity recorded (run: jj-lane.sh init)". `init` is the only writer (`:518-519`), snapshots with `jj status` (`:385-390`), requires `origin/<branch>` (`:392-410`) and refuses staged entries — souji must not initialize a repo it merely cleans (AGENTS:3-4, PROVINCE Refuses). |
| **X4** | The recipe branch point is implied as "the repo" (`git -C <repo> rev-parse --show-toplevel`, SKILL:122) | `lane_realdir` requires `<dir>/.git` to be a **directory** (`:76`) and refuses worktrees/submodules; but souji's surfaces include worktree registrations (SKILL:79-83, :124) and a nested empty `.git` is a directory yet not a repo (live: `p6repo/.git` ENOENT; when present `git -C` fails) | `test -d .git` alone is not a repo test, and the helper cannot write the worktree case at all. The doc branch must be `git rev-parse --git-dir` success **then** `test -d <repo>/.jj`. |
| **X5** | SKILL:58 "`git mv` (or plain `mv` for untracked)" | jj owns the index; `jj commit` resets staged entries, `git mv` staging is not what jj commits (`JjAuditSouji` F4, observed) | In a colocated repo `git mv` produces ` D <rel>` residue after the jj commit; the deletion half can be silently lost. Rule must flip: plain `mv` + both paths. |
| **X6** | SKILL:123 `git add -- <paths>` + `-c maintenance.auto=false commit -- <paths>` | The jj analogue of the maintenance guard is `--config 'snapshot.auto-track="none()"'` on every snapshotting call (`:29,:68,:556-578`) plus a pathspec commit; a plain `git commit` in a colocated repo moves git HEAD while jj leaves `refs/heads/<branch>` behind (`JjAuditSouji` F2) | The git recipe is not merely redundant in a colocated repo: it creates the unbookmarked-commit state X7 depends on. `maintenance.auto=false` is a git-only guard and must not be presented as covering the jj route. |
| **X7** | SKILL:61-62 second check "receipt must still hold" | `jj commit` does not advance `refs/heads/<branch>`; the helper has to do it explicitly (`:658-660`), and F2 observed `--branches --not --remotes` empty with the commit held only by `refs/jj/keep` | Under C3(b) (keep refs included in `unpushed-touching`), a quarantine commit made by a **direct** `jj commit` becomes an "unpushed commit touching the path" forever: the hold-period second check can never pass and quarantine can never be emptied. The commit must move the durable branch in the same recipe. |
| **X8** | SKILL:113 uses HEAD implicitly; D5/F5 habit is `rev-parse HEAD` as `measured_commit` | Under colocation HEAD is detached on `@-` (live: detached at `master` tip); `@{u}` and `branch --show-current` are unusable | `HEAD` is not a durable pin; the citable refs are `refs/heads/<branch>` and the helper's `landed`. |
| **X9** | no doc text on jj auto-track | The helper treats "repo missing `snapshot.auto-track = none()`" as never-initialized (`:518-521`), and its init is the only writer of that key; [INFERENCE] jj's own default is `all()`. With no root `.gitignore`, with no root `.gitignore`, `.ufo` (302 files) is untracked but **not ignored**; helper refuses any named path under `.ufo` (`:532-533`) while `.ufo-quarantine/**` is allowed (patterns are exact `.ufo`) | A bare `jj` call in this lane tracks every wave report into `@`; a later pathspec commit is then rejected by `path_ok` ("changed a path outside the request", `:620-643`). Every snapshotting call in these docs must carry the auto-track config. |
| **X10** | AGENTS:9 "Never rewrite history"; SKILL:65-67 same | Push recovery rebases only the unpushed range and prints `rewritten <old> -> <new>` (`:22,:251-252`) | Not a souji action, but the docs must say so and must add: a `rewritten` line invalidates the pre-rebase hash as citable. |
| **X11** | AGENTS:3-4 "sibling repos … read-only — census them, never modify them" | SKILL:58 requires a commit **inside** the owning (sibling) repo | Blanket vs carve-out; without a one-sentence exception the two rules cannot both hold. |
| **X12** | AGENTS:20 names the git identity form only | Identity is per command/repo config in jj (`:19-20,:599-606,:427-428`) and the helper unsets `JJ_USER`/`JJ_EMAIL` because env beats config (`:32-33`) | In a colocated repo the git config identity is not what stamps the commit; AGENTS:20 as written is unexecutable there. |
| **X13** (peer draft) | `ScribeSkillJj.md` Edit C routes the colocated quarantine commit through `jj-lane.sh commit … --as <owner-id>` and cites `landed`, post-checking `<landed>:<rel>` | X1–X3 above | That block is not applicable: it publishes, it needs the owner's identity/init, and for a local quarantine commit no `landed` line exists. Must be replaced by the direct-jj block (B2) or by a helper route only where the owning lane itself owns the push. |

## 4. Replacement text blocks (short, paste-ready)

### A — SKILL.md, Removal flow step 3 (replaces line 58)

```text
3. Move into `<repo>/.ufo-quarantine/<utc-date>/...`, then commit BOTH paths (old `<rel>` and new `<qpath>`) by the two-branch rule below. Plain repo: `git mv` (or `mv` for untracked). Colocated repo (`test -d <repo>/.jj`): plain `mv` only — jj owns the index and a `git mv` staging entry is discarded by the next jj mutation. Quarantine is a local commit in the owning repo; it is never pushed.
```

### B — SKILL.md, Pre-quarantine checklist commit item (replaces line 123)

```text
- [ ] Repo kind is resolved first: `git -C <repo> rev-parse --git-dir` must succeed (a nested empty `.git` directory is not a repo), then `test -d <repo>/.jj` selects the route. Never `git add -A` / `.`.
- [ ] Plain repo (no `.jj`): `git -C <repo> add -- <rel> <qpath>` then `git -C <repo> -c maintenance.auto=false commit -- <rel> <qpath>`; both paths in both commands.
- [ ] Colocated repo (`.jj` present), direct jj — no `git add`, `git commit`, `git mv`:
      `mv -- <rel> <qpath>`; then from the repo root, with `JJ_USER`/`JJ_EMAIL` unset:
      `jj --config 'snapshot.auto-track="none()"' --config user.name=souji-shokunin --config user.email=souji@shokunin.local file track -- 'root-file:"<qpath>"'`
      `jj --config 'snapshot.auto-track="none()"' --config user.name=souji-shokunin --config user.email=souji@shokunin.local commit -m "<receipt class + evidence pointer>" -- 'root-file:"<rel>"' 'root-file:"<qpath>"'`
      `jj --ignore-working-copy bookmark set <branch> -r @-`   # durable: a jj commit alone does not move refs/heads/<branch>
      Post-check all three: `git -C <repo> rev-parse refs/heads/<branch>` is the new commit id; `git -C <repo> ls-tree -r --name-only <commit> -- <rel>` is empty; `… -- <qpath>` lists the file. Never commit a directory pathspec (nested `.git` → phantom deletions); never cite `HEAD`.
- [ ] `jj-lane.sh commit` is NOT this recipe: it ends in a push (`do_push … || exit 3`), requires the repo's own lane id and `jj-lane.sh init`, and prints the citable `landed` line only after `ls-remote`. Use it only when the owning lane itself is the pusher; a souji quarantine commit is local and cites the commit id.
```

### C — SKILL.md, `pushed` row (replaces the query fragment at line 35)

```text
AND no unpushed commit touches the path (`git log [HEAD] --branches --glob='refs/jj/keep/*' --not --remotes --oneline -- <path>` empty; plain repos without `refs/jj` are unchanged by the glob; keep refs include hidden rewritten predecessors, so a jj-held commit that touched the path refuses conservatively)
```

### D — SKILL.md, Error patterns (one bullet, after the phantom-fixture bullet)

```text
- **jj helper is a publisher, not a commit** (r17): `scripts/hyaku/jj-lane.sh commit` ends in `do_push` (exit 3 = commit kept, push failed), requires a repo initialized by `jj-lane.sh init` (`snapshot.auto-track="none()"`, `user.name=<lane>-shokunin`, `trunk()` alias), refuses `--as` values other than the recorded lane id or `protocol`, refuses a `.git` that is a file (worktrees), and treats `.ufo`, `.git`, `.jj` as never committable (`.ufo-quarantine/**` is allowed). It is not the quarantine route.
```

### E — AGENTS.md (three line replacements)

```text
- Work only within this repo and its PROVINCE.md scope; sibling repos and domain source trees are read-only — census them; the ONLY write is the single local quarantine commit authorized by a dry run the operator has seen, naming both paths of the move.
- Never rewrite history — including a `jj` bookmark or working-copy rewrite; never touch credentials or operator config; never touch an artifact whose owning lane has dirty or unpushed work. (`jj-lane.sh push` recovery may print `rewritten <old> -> <new>` for an unpublished commit; that is the owning lane's action, is not citable as landed, and is outside souji's authority.)
- Commit as `souji-shokunin <souji@shokunin.local>` — in this repo and in any colocated repo, stamp identity per command (`--config user.name=souji-shokunin --config user.email=souji@shokunin.local` with `JJ_USER`/`JJ_EMAIL` unset); git config identity alone does not stamp a jj commit.
```

### F — note to carry into the jj knowledge entry (C3c owner)

```text
Quarantine write contract: plain repo → `git add`/`git -c maintenance.auto=false commit` naming both paths. Colocated repo → plain `mv`; `jj file track` the destination under `snapshot.auto-track="none()"`; `jj commit` naming both paths; `jj bookmark set <branch> -r @-` so C3(b)'s keep-ref-inclusive unpushed check can clear; verify with `git ls-tree` on the branch tip. `jj-lane.sh commit` is a lane-lane publisher (own identity, own init, own push) and is not usable by souji for a local quarantine commit.
```

## 5. Verdict

| claim / surface | verdict | basis |
|---|---|---|
| helper `commit` is local | **fails** | `:669`; no `--no-push` in the parser |
| SKILL:58 `git mv` is valid under colocation | **fails** | F4 + index ownership; X5 |
| SKILL:123 is a valid guarded form for a colocated taking repo | **fails** | X6 |
| helper is usable in this lane today | **fails** | no `.jj/repo/config.toml`, no jj `user.name` → exit 1 (`:104-113,:519-521`) |
| C3(b) + direct `jj commit` allows the hold-period second check to pass | **fails** unless the durable branch is moved | X7 |
| `.ufo-quarantine/**` is committable by the helper guard | **holds** | case patterns `:532-533` match `.ufo` exactly |
| helper deletion/rename handling (v2) | **holds by code reading** (`:543-546`, `:620-657`); not executed here | helper v2; the F1 shape is covered, phantom deletions refused |
| doc branch instruction `test -d <repo>/.jj` | **holds with a pre-gate** | X4; needed for the nested-stub surface |

Smallest fix set, in order: apply A, B, C, D, E; do **not** apply `ScribeSkillJj.md` Edit C as written (replace with B2); amend Edit B's `--as <owner-id>` sentence to the direct-jj identity form.

## 6. Risks

- The helper is fleet-owned (`scripts/`, PROVINCE Refuses). No block above asks for a helper change; if the fleet later adds `--no-push`/a local commit mode, block B's last item should be re-read (it is written to stay true either way: it describes today's `commit`).
- `jj bookmark set <branch> -r @-` presumes `refs/heads/<branch>` exists. If it does not (detached-only repo), the recipe must refuse rather than invent a branch — the plain-git route with an explicit `git update-ref`-free commit is not available either (souji must not create refs). Add: "no branch → NOT-SAFE / route to operator".
- Passing `--config 'snapshot.auto-track="none()"'` still snapshots the working copy; files created between `file track` and `commit` are untracked and stay out (safe), but any *tracked* modification outside the two named paths makes `jj commit <paths>` split it into `@` (not an error) — the post-check `ls-tree` is the falsifier, not the exit code.
- `.ufo` unignored (302 files) means any operator/agent `jj st` in this lane mutates `@`; docs cannot prevent that, only warn. A `.gitignore` line for `.ufo/` in the lane would remove the trap but is a repo-policy change outside this seat (and would change census dirty rows — C1 surface); do not add it unilaterally.

## 7. Verification (for L1, after applying blocks; none of this was run against a real repo)

1. `bash -n scripts/hyaku/jj-lane.sh` (unchanged; helper untouched).
2. Doc text: `grep -n 'jj-lane.sh' SKILL.md AGENTS.md` — every hit must carry the push caveat; `grep -n 'git mv' SKILL.md` — only the plain-repo arm.
3. Falsifier for X1: read `:669` and the arg loop `:499-505` — no flag suppresses `do_push`.
4. Falsifier for X7: after a sandbox direct-jj quarantine commit, `git -C <sb> rev-parse refs/heads/<b>` must equal the commit id (bookmark moved) and `git log --branches --glob='refs/jj/keep/*' --not --remotes --oneline -- <rel>` must be empty.
5. Falsifier for X5: `git -C <sb> ls-tree -r --name-only <commit> -- <rel>` empty **and** `-- <qpath>` non-empty (the F1 check).
6. Plain-repo byte-identity: the same two `ls-tree` checks plus `git log --branches --not --remotes -- <rel>` unchanged when `refs/jj` is absent.
7. Fixture stub: create an empty `<sb>/nested/.git` next to two tracked files and confirm a directory pathspec is refused / phantom `D` appears — this is the r17-census-hygiene fixture's ground truth, not a claim of this seat.
