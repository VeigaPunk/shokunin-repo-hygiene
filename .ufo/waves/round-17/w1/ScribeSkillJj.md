STATUS: DONE — two-branch quarantine rule, jj error-pattern bullets and the Pre-quarantine/Pre-removal edits drafted as exact before/after blocks; SKILL.md not edited (report only).

# ScribeSkillJj — SKILL.md jj-colocation draft (round 17, wave 1)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` · file under draft: `SKILL.md` (sha-anchored read `A82F`) · seat: leaf scribe, no delegation, no commits, no jj, no git writes.

## 1. Method and commands run

Read-only. No jj subcommand was run. No package, binary or tool was installed or upgraded (Tooling directive: nothing needed).

| # | Command / read | Result used |
|---|---|---|
| 1 | `read souji-shokunin/SKILL.md:1-203`, `:198-240` | line anchors for :58, :103-107, :113, :121, :123 |
| 2 | `read .ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` (1-400) | F1–F8, recommendations 1–6, risk table |
| 3 | `read .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` | hazards 1–8 (nested `.git`, `cp -a`, detached HEAD, index reset) |
| 4 | `read scripts/hyaku/jj-lane.sh` (1-300) and `:520-560`, `:612-662` | helper v2 deletion/rename handling, `--as` rule, `landed` line |
| 5 | `grep` on `jj-lane.sh` for `cmd_commit|landed|--as|foreign author` | :12, :18-22, :252/:258, :500, :516-517, :221-223 |
| 6 | `read souji-shokunin/PROVINCE.md` | context only; no edit proposed |
| 7 | `stat -c '%F %n'` on `souji-shokunin/tests/vault/vadv54-run/p/p6repo/.git` and `souji-shokunin/.jj` | see §2 — the stub is ABSENT, and `.jj` is PRESENT |

Exact `stat` output (command 7):
```
stat: cannot stat '/home/vgpnk/Projects/shokunin/souji-shokunin/tests/vault/vadv54-run/p/p6repo/.git': No such file or directory (os error 2)
directory /home/vgpnk/Projects/shokunin/souji-shokunin/.jj
```

## 2. Observed facts that change the draft

1. **The lane is colocated now.** `souji-shokunin/.jj` exists (command 7). `JjAuditSouji` §1 recorded "no `.jj` in the live lane at audit time". The current SKILL.md quarantine recipe (:58, :123) is therefore live-wrong for this repo, not prospective. The two-branch rule below is needed now.
2. **The nested stub is gone at draft time.** `JjTrialSouji` hazard 1 and recommendation 1 name `tests/vault/vadv54-run/p/p6repo/.git` (empty dir). `stat` reports ENOENT. The Vadv54StubFix seat may have removed it. The phantom-deletion rule stays in the draft because any nested `.git` triggers it (see Error bullet 3).
3. **Helper v2 handles deletions; the F1 failure is not reproduced here.** `JjAuditSouji` F1 observed a dropped source path on an earlier helper. The current helper accepts an absent path when it is in the branch tip (`scripts/hyaku/jj-lane.sh:543-546`, `git cat-file -e refs/heads/$branch:$q`) and still prints `warn: skipping missing path` when it is in neither (:548). A path in neither location yields `nothing to commit (no such paths)`, exit 0 (:551). The F1 fix is therefore by code reading only [INFERENCE]; it was not executed in this seat.
4. **One-sided requests are NOT refused by the helper.** The `path_ok` / rename logic (:620-656) checks that changed paths lie under the requested paths. It does not require both halves of a move. Naming only `<qpath>` commits only the addition; naming only `<rel>` commits only the deletion. Each leaves the other half uncommitted in `@`. The draft therefore requires BOTH paths and a post-check (`cat-file`), not a helper refusal. (A earlier draft line claiming a refusal was wrong; corrected here.)
5. **`--as` must be the owning lane's id.** `jj-lane.sh:516-517`: `--as` must equal the repo's lane id or `protocol`. `push_preflight` (:218-227) refuses foreign authors at push. So a souji seat cannot land a quarantine commit in another lane's colocated repo under `--as souji`; the owning lane's helper (or `--as protocol`) is the only route.
6. **Citable output is `landed <hash>` only.** Header :21-22 and `report_landed` (:252, :258). Do not cite `committed`/`pushed` lines.

## 3. Exact edits (before / after) — `SKILL.md`, line numbers from read `A82F`

### Edit A — :58 (Removal flow step 3)

Before (line 58):
```text
3. `git mv` (or plain `mv` for untracked) into `<repo>/.ufo-quarantine/<utc-date>/...` — quarantine is a normal commit in the owning repo, made with the guarded form in the Pre-quarantine checklist.
```
After (line 58):
```text
3. Move into `<repo>/.ufo-quarantine/<utc-date>/...`: plain repo → `git mv` (or `mv` for untracked); colocated repo (`<repo>/.jj` present) → plain `mv` only, because jj owns the index and discards `git mv` staging on its next mutation. Then commit BOTH the old and new paths by the two-branch rule in the Pre-quarantine checklist. Quarantine is a normal commit in the owning repo.
```

### Edit B — :121 (Pre-quarantine identity)

Before (line 121):
```text
- [ ] Lane identity: `souji-shokunin <souji@shokunin.local>`
```
After (line 121):
```text
- [ ] Lane identity: `souji-shokunin <souji@shokunin.local>` in the souji repo; in a colocated repo the identity is the owning lane's id passed as `--as` (the helper refuses any other id except `protocol`).
```

### Edit C — :123 (Pre-quarantine commit route) — two-branch rule

Before (line 123):
```text
- [ ] Commit guarded and scoped: `git -C <repo> add -- <approved paths>` then `git -C <repo> -c maintenance.auto=false commit -- <same approved paths>` — never `git add -A` / `.`
```
After (line 123, expands to three lines):
```text
- [ ] Commit route is chosen by repo kind (`test -d <repo>/.jj`); never `git add -A` / `.`; never `cp -a` a `.jj` repo.
  - [ ] Plain repo (no `.jj`): `git -C <repo> add -- <rel> <qpath>` then `git -C <repo> -c maintenance.auto=false commit -- <rel> <qpath>`. Both the old path `<rel>` and the new path `<qpath>` are named in both commands; a destination-only commit splits the move.
  - [ ] Colocated repo (`<repo>/.jj` present): owning lane's helper `scripts/hyaku/jj-lane.sh commit <repo> --as <owner-id> -m "<receipt class + evidence pointer>" -- <rel> <qpath>`. Name BOTH paths: a one-sided request commits only that half and leaves the other in `@` (the helper does not refuse it). Post-check, both must hold: `git -C <repo> cat-file -e <landed>:<rel>` FAILS and `git -C <repo> cat-file -e <landed>:<qpath>` SUCCEEDS. Cite only the `landed <hash>` line the helper prints after `ls-remote` verification.
```

### Edit D — :107 (Error patterns: insert after the last bullet, before the blank line and `## Checklists`)

Before (lines 103-109, the last bullet and heading context):
```text
- **Phantom fixture / wrong-byte verdict** (r13, round-12 K5 and r11 relay):
  ...
  `tests/fixtures/r13-cert-frozen/`. This is not a replacement safety suite.

## Checklists
```
After (insert these bullets between :107 and the blank line):
```text
- **jj: all-refs roots count `refs/jj/keep` as durable** (colocated repos, r17): `git log <head> --not --all`, `for-each-ref` over all refs, and `rev-list --not <all-ref-oids>` treat `refs/jj/keep/*` as durable, so a keep-only head reads as reachable and can earn `SAFE(metadata-prune)`. Durable roots are `refs/heads`, `refs/tags` and `refs/remotes` only. Live exposure: the tameshi, game-dev-2d and kotodama worktree registrations (`JjAuditSouji` F3).
- **jj: `--branches --not --remotes` misses unbookmarked commits**: a jj commit leaves HEAD detached and moves no branch, so the query returns empty for work that exists. Include `--glob='refs/jj/keep/*'` and HEAD in the revision set (conservative: hidden rewritten predecessors that touched the path also refuse). Plain repos without `refs/jj` are not changed by the keep glob (`JjAuditSouji` F2).
- **jj: nested `.git` → phantom deletions**: a directory containing a `.git` (even an empty stub) is a nested repo to jj; its files show as `D` and a directory pathspec commits those deletions. Use file-exact pathspecs; never commit a directory that contains a nested `.git`. The trial's stub `tests/vault/vadv54-run/p/p6repo/.git` is absent at this draft, but the rule holds for any nested `.git` (`JjTrialSouji` hazard 1).
- **jj: detached HEAD**: under colocation `git rev-parse @{u}` fails and `git branch --show-current` prints nothing. Read the branch tip with `git rev-parse refs/heads/<b>`; never `@{u}`; read the remote with `refs/remotes/origin/<b>` (`JjTrialSouji` hazard 3).
- **jj: index is not durable**: `git mv` / `git add` staging is discarded by the next jj mutation; `git diff --cached` is not a safety signal in a colocated repo (`JjAuditSouji` F4).
- **jj: `cp -a` of a `.jj` repo**: copies the repo identity and jj prints "repo appears to have been copied". Create a seat worktree with `git clone` from origin and `jj-lane.sh init <dir> <id>`, never `cp -a` (`JjTrialSouji` step 3).

```
(Note: the last line of the inserted block is a blank line, so the existing blank line before `## Checklists` stays a single blank line; the post-edit file has the `## Checklists` heading after exactly one blank line.)

## 4. Optional edit (beyond the requested scope; recommended)

### Edit E — :113 (Pre-removal: unpushed check)

Before (line 113):
```text
- [ ] Owning repo has no unpushed commits touching the artifact (`git log --not --remotes --oneline -- <path>` empty)
```
After (line 113):
```text
- [ ] Owning repo has no unpushed commits touching the artifact, including unbookmarked jj commits (`git log --branches --glob='refs/jj/keep/*' HEAD --not --remotes --oneline -- <path>` empty). This is more conservative than the old form in plain repos too, because `--branches` adds non-HEAD branches.
```
Rationale: the old form reads HEAD only (implicit) and misses keep-only side commits (`JjAuditSouji` F2). The `--branches` addition changes plain-repo output (more refusals), which is the conservative direction.

## 5. Tool-level dependencies (not SKILL edits; for the C3 seats)

- The receipt taxonomy row `pushed` (SKILL.md:35) and the Error bullets above describe `--branches --not --remotes` and `--not --all` behavior that the tools implement (`tools/souji-verify.sh:234,321,351,671,952`, `tools/souji-vault-verify.sh:412,487,517,859,1140`, `tools/souji-quarantine.sh:299,931,1073,1251`). The SKILL draft documents the required behavior; the tool edits belong to the C3a/C3b executors. Until they land, the prose must not be read as the tool's current behavior.
- Census `unpushed` stays branch-based by declaration (`JjAuditSouji` F2 / claim C3); disclose it, do not change it.

## 6. Verdict per item

| Item | Verdict | Smallest fix |
|---|---|---|
| :58 quarantine step | holds after Edit A | apply Edit A |
| :121 identity | holds after Edit B | apply Edit B |
| :123 commit route | holds after Edit C; the one-sided helper behavior is inferred from `jj-lane.sh:620-656` read, not executed | apply Edit C; re-verify helper with a sandbox run before relying on the post-check |
| Error bullets (6) | holds, each cites a JjAudit/JjTrial finding | apply Edit D |
| :113 pre-removal | holds, optional | apply Edit E or defer |

## 7. Not done / limits

- No file edited: `SKILL.md` was not changed (report-only seat).
- Helper F1 fix and the one-sided split behavior are code-read only; no sandbox run was executed in this seat (contract forbids running souji tools against real directories, and no jj run was permitted).
- The draft does not change `PROVINCE.md`, `corpus/knowledge/`, or any tool.
- Installations: none.
