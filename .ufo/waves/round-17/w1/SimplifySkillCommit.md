STATUS: DONE — one 11-line `Committing under jj colocation` block with exact before/after; SKILL.md itself not edited (report-only seat).

# SimplifySkillCommit — SKILL.md commit recipes consolidated under jj colocation

Seat: leaf, round 17 wave 1. Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, HEAD
`5fa6017ddcae9f6bd4412df44765f6360cb16294`. Read-only throughout: no `jj` subcommand, no git
write, no tool run against a live directory, no lane/fleet file edited. Report path only.

## 1. Axes

| axis | what this proposal buys |
|---|---|
| coverage | The commit routes and identity rule in SKILL.md (`:58`, `:121`, `:123`) are replaced by one rule that covers both repo kinds, the tracked-move shape, the citable output and a landing witness. |
| consistency | The rule matches helper v2 as it is (`--as` lane id, both-path commits, `landed` only, phantom-deletion refusal); no second convention is introduced next to ScribeSkillJj's draft. |
| executability | Commands are the helper's documented CLI (`commit <lane-dir> --as <id> -m <msg> -- <path>...`) and the already-present guarded git form; nothing new to install. |
| brevity | 11 physical lines replace two recipes plus a standalone identity rule; the alternative draft expands the checklist to four lines and adds six separate diagnostic bullets (its Edits C-D). |
| minimality | Receipt queries (C3a/C3b) and tool code are untouched; PROVINCE.md needs no edit because it carries no commit recipe. |
| traceability | Every clause cites a helper line or an audit finding; the one behaviour not executed is marked `[INFERENCE]`. |

## 2. Verdict

| item | verdict | smallest fix |
|---|---|---|
| Recipes are duplicated and one branch is live-wrong | holds (defect) | apply Edit A + Edit B + Edit C |
| Proposed block is executable against helper v2 | holds (`[INFERENCE]` for the two-path commit; code-read, not run) | none |
| Plain-repo semantics preserved | holds | none |
| PROVINCE.md recipe absent | holds (nothing to replace) | none |
| Receipt/`unpushed` rules left alone | holds (out of this seat's scope) | C3a/C3b owners |

## 3. Evidence

| observation | command / read | result |
|---|---|---|
| Live lane is colocated | `ls -a` (named entries) | `.jj` present |
| HEAD is detached now | `git -C <lane> rev-parse --abbrev-ref HEAD` | `HEAD` |
| `@{u}` fails now | `git -C <lane> rev-parse --abbrev-ref '@{u}'` | `fatal: HEAD does not point to a branch` |
| jj keep refs exist | `git for-each-ref --format='%(refname)' refs/jj/keep/ \| wc -l` | `8` |
| durable refs available | `git for-each-ref --format='%(refname:short)' refs/heads refs/remotes` | `master origin origin/master` |
| Recipe 1 | `SKILL.md:58` | `git mv … made with the guarded form in the Pre-quarantine checklist` |
| Recipe 2 + identity | `SKILL.md:121,123` | `Lane identity: souji-shokunin …`; `git add … -c maintenance.auto=false commit …` |
| Recipe census | text search of `SKILL.md` for the five command tokens | exactly two commit recipes (`:58`, `:123`) plus the identity rule (`:121`); `:91-95` is the maintenance-prune hazard, not a recipe; `:35`/`:113` are receipt queries owned by C3a/C3b |
| No recipe in PROVINCE | grep of `PROVINCE.md` for commit/jj/quarantine | only `:28` (history rewrite refusal) and `:91` (quarantine sites unproved) |
| `--as` is the repo's lane id | `scripts/hyaku/jj-lane.sh:516-517` | `--as must be the lane id ($lane_id) or protocol` |
| helper needs its own init | `jj-lane.sh:521` | `snapshot.auto-track is not "none()" … (run: jj-lane.sh init)` |
| a branch-tip-only path is committed as a deletion | `jj-lane.sh:543-548` | `elif git cat-file -e "refs/heads/$branch:$q"` → included; otherwise `warn: skipping missing path` |
| no path at all → no commit | `jj-lane.sh:551` | `nothing to commit (no such paths)`, exit 0 |
| changed path outside the request → refusal | `jj-lane.sh:620-628` | `commit changed a path outside the request` |
| phantom deletion refused | `jj-lane.sh:650-653` | `commit would delete … but it exists on disk (nested repo?) — refusing` |
| commit lands and pushes | `jj-lane.sh:669` | `do_push "$branch" "$id" "$own" \|\| exit 3` |
| citable line is `landed` only | `jj-lane.sh:21-22`, `:58-60`, `:252`/`:258` | `landed <hash>` after `ls-remote` |
| helper is executable | `stat -c '%A'` | `-rwxr-xr-x` |
| cross-lane identity is refused at push | `jj-lane.sh:215-228` | `push range contains a foreign author/committer` |
| helper does not require both halves of a move | code read of `:620-656` | `path_ok` checks changed paths against the request; a one-sided move is not refused, so both paths are a caller duty. `[INFERENCE]` (not executed) |
| audit basis | `JjAuditSouji` F1-F4; `JjTrialSouji` step 4, hazards 1-4 | F1 source path dropped on v1; F2 `--branches --not --remotes` blind; F3 keep refs durable-looking; F4 index not a durable signal; trial: detached HEAD, `@{u}` failure, `git mv` staging not a signal |
| sibling overlap | `.ufo/waves/round-17/w1/ScribeSkillJj.md` Edits A-C | same two-branch direction and the same `cat-file` post-check; differences are shape (4-line checklist expansion vs one 11-line block), a separately retained identity bullet, and an index-discard rationale for plain `mv` that `JjAuditSouji` F4 does not show |

## 4. Exact before / after

Line numbers are HEAD `5fa6017` bytes, re-read this seat with a numbered read of `SKILL.md:50-60,70-80,110-128`.

### Edit A — `SKILL.md:58` (Removal flow step 3)

Before:

```text
3. `git mv` (or plain `mv` for untracked) into `<repo>/.ufo-quarantine/<utc-date>/...` — quarantine is a normal commit in the owning repo, made with the guarded form in the Pre-quarantine checklist.
```

After:

```text
3. `git mv` (or plain `mv` for untracked) into `<repo>/.ufo-quarantine/<utc-date>/...`: use plain `mv` when `<repo>/.jj` exists (jj owns the index; the helper reads the working copy), `git mv` otherwise. Quarantine is a normal commit in the owning repo, made by `Committing under jj colocation`; a tracked move names its old and new paths there.
```

Rationale: the old pointer would dangle once the checklist stops holding the recipe. `JjAuditSouji` F4 shows the git index is not a durable signal in a colocated repo, and the helper commits named paths from the working copy, so plain `mv` loses nothing there. On a plain repo `git mv` stays exactly as today.

### Edit B — insert after `SKILL.md:72`, before `SKILL.md:74` (`## Error patterns`)

This is the whole consolidated block: 11 physical lines, heading through last bullet.

```text
## Committing under jj colocation

HEAD detaches under a jj mutation, so `@{u}` can fail: name `refs/heads/<b>` and `refs/remotes/origin/<b>`, never HEAD.

- **`.jj` present** (this repo or any repo souji cleans): only the repo's own helper —
  `"$SHOKUNIN_ROOT/scripts/hyaku/jj-lane.sh" commit <repo> --as <repo lane id> -m "<receipt>: <evidence>" -- <path>...` —
  name BOTH paths of a tracked move, cite only `landed <hash>`, and verify `cat-file -e <landed>:<old>`
  fails while `<new>` succeeds. A change outside the named paths or a deletion of a disk file is
  refused; a refusal is a stop, never a git fallback.
- **`.jj` absent**: `git -C <repo> add -- <path>...` (never `-A`/`.`), then
  `git -C <repo> -c maintenance.auto=false commit -- <path>...`; identity `souji-shokunin <souji@shokunin.local>`.
```

Line count check: heading (1) + blank (2) + detached-HEAD rule (3) + blank (4) + five bullet lines (5-9) + two bullet lines (10-11). Each command sits on one physical line so it is paste-safe; only prose wraps.

### Edit C — `SKILL.md:118-124` (Pre-quarantine checklist)

Before:

```text
Pre-quarantine commit:
- [ ] Quarantine path is inside the owning repo (`.ufo-quarantine/<date>/`)
- [ ] Commit message names the receipt class and the evidence pointer
- [ ] Lane identity: `souji-shokunin <souji@shokunin.local>`
- [ ] Right repo: `git -C <repo> rev-parse --show-toplevel` prints the owning repo (never trust `cd`)
- [ ] Commit guarded and scoped: `git -C <repo> add -- <approved paths>` then `git -C <repo> -c maintenance.auto=false commit -- <same approved paths>` — never `git add -A` / `.`
- [ ] Pinned registrations stay pinned: `git -C <repo> worktree list --porcelain | awk '/^locked/{n++} END{print n+0}'` equals the pin count; pin new ones with `git -C <repo> worktree lock --reason "<why>" <worktree-path>`
```

After:

```text
Pre-quarantine commit:
- [ ] Quarantine path is inside the owning repo (`.ufo-quarantine/<date>/`)
- [ ] Commit message names the receipt class and the evidence pointer
- [ ] Right repo: `git -C <repo> rev-parse --show-toplevel` prints the owning repo (never trust `cd`)
- [ ] Commit form and identity: exactly one — `Committing under jj colocation` (repo's helper when `.jj` exists, guarded git otherwise); no second recipe
- [ ] Pinned registrations stay pinned: `git -C <repo> worktree list --porcelain | awk '/^locked/{n++} END{print n+0}'` equals the pin count; pin new ones with `git -C <repo> worktree lock --reason "<why>" <worktree-path>`
```

Deleted: the standalone `Lane identity: souji-shokunin …` bullet (`:121`) and the `git add`/`commit` recipe bullet (`:123`). Both rules survive in the block: the helper's `--as <repo lane id>` is the identity in a colocated repo (it refuses any other id, `jj-lane.sh:516-517`, and push refuses foreign authors, `:215-228`); the plain branch keeps `souji-shokunin <souji@shokunin.local>` and the `maintenance.auto=false` guard.

## 5. Why this shape, and how it relates to ScribeSkillJj

- **One authority per concern.** Commit recipes live in one place. Receipt queries (`SKILL.md:35`, `:113`, and the Error-pattern bullets) stay with C3a/C3b; this block does not restate `--not --all` or untouching-path queries, so the round cannot grow two versions of them.
- **No loss of plain-repo behaviour.** The plain branch is the old recipe with `<approved paths>` renamed `<path>...` and the `never -A/.` guard kept; a plain repo has no jj mutation to interleave, so the guarded form remains correct there.
- **Helper-only is the only route that lands.** `jj-lane.sh:510` refuses a repo without `.jj`, `:521` refuses a colocated repo it did not initialize, and every helper commit ends in `do_push` (`:669`). A raw `git commit` in a `.jj` repo is not blocked by jj, but a commit under a foreign identity blocks the owner's next helper push (`:215-228`); the block makes a raw commit a stop, not a route.
- **Post-check is the witness, not the helper's refusal.** `path_ok` (`:620-628`) rejects changed paths outside the request, but it does not require both halves of a move. Naming only `<qpath>` can commit the addition and leave the deletion in `@`; naming only `<old>` commits the deletion. Hence the block mandates both paths *and* the `cat-file -e` check at the landed hash. `ScribeSkillJj:§2.4` reaches the same conclusion independently; the block states it in one place and finding R1 below keeps the wording exact.
- **ScribeSkillJj reconciliation.** Its Edit A (plain `mv` under colocation) is adopted into Edit A; its rationale ("jj discards `git mv` staging on its next mutation") is replaced by the grounded statement that the index is not a durable signal (`JjAuditSouji` F4), because the two seat reports differ on whether a jj operation drops the staged entry (R5). Its Edit B (identity) and Edit C (route) are folded into the block, which is 11 lines in one place instead of a checklist expansion plus a separate identity bullet. Its Edit D error bullets are diagnostics, not recipes; they do not duplicate the block and can land independently under C3a/C3b.

## 6. Routed findings and disclosed tradeoffs

| id | finding | evidence | disposition |
|---|---|---|---|
| R1 | The one-sided-move hazard is a caller duty, not a helper refusal. `path_ok` (`jj-lane.sh:620-628`) checks changed paths against the request; a destination-only request can commit only the addition. | code read; not executed `[INFERENCE]` | The block mandates both paths and the `cat-file` post-check. Do not write "the helper refuses a one-sided move". |
| R2 | A helper commit is a landing, not a local commit: it pushes (`:669`) under the repo's lane identity. A quarantine commit in another lane's `.jj` repo therefore lands on that lane's branch with that lane's author. | `jj-lane.sh:669`, `:215-228` | Kept as the only route; disclose. If the owning lane must not receive a push from souji, the move waits for that lane's closure — there is no local-only helper mode. `--as` accepts `protocol` for closures; the block names the lane id as the normal case. |
| R3 | An uninitialized or otherwise refused `.jj` repo is a stop, not a git fallback. | `jj-lane.sh:510`, `:521` | Block wording: "a refusal is a stop, never a git fallback". |
| R4 | `tools/souji-quarantine.sh` still performs `git mv` (`:518`) and `git rm --cached` (`:566`) in action mode. The recipe's plain-`mv` preference for colocated repos is a SKILL-level rule; the tool's index writes are not made durable by jj (`JjAuditSouji` F4). | tool lines read | Out of this seat's write scope; routed to the quarantine action-tool owner. The `cat-file` post-check catches a half-landed move regardless of which verb ran. |
| R5 | Evidence divergence on index staging: `JjTrialSouji` hazard 4 says a `jj describe` drops the staged entry; `JjAuditSouji` F4 says a `jj st` snapshot did not. Different operations; neither was re-run here. | both reports | The block depends on neither observation: it avoids `git add` under `.jj` and witnesses with `cat-file`. Flagged for the C3(c) knowledge entry. |
| R6 | `PROVINCE.md` has no commit recipe to consolidate (only the history-rewrite refusal at `:28`). | grep of named file | No PROVINCE edit proposed; adding one would be a second authority. |
| R7 | Heading `HEAD detaches under a jj mutation` is observed live (detached now, `@{u}` fatal, 8 keep refs), not a universal state: an attached HEAD is possible before a mutation. | live read §3 | Wording says "under a jj mutation", not "always". |

Tradeoff: the file grows by 10 net lines (delete two checklist bullets; add the 11-line block plus its separating blank line; Edit A keeps one sentence at the same length), and a move commit costs one `cat-file` check. Against that, one authority replaces two, the colocated branch stops prescribing an index-based recipe that jj does not honour, and the landed hash is the cited object.

## 7. Commands run (exact)

All read-only; `jj` was never executed; no network. The lane path is abbreviated `…`; `2>/dev/null` and the `head`/`tr` pipe tails are omitted where they could not change the observed line.

```text
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
5fa6017ddcae9f6bd4412df44765f6360cb16294
$ git -C … rev-parse --abbrev-ref HEAD
HEAD
$ git -C … rev-parse --abbrev-ref '@{u}'
fatal: HEAD does not point to a branch
$ git -C … for-each-ref --format='%(refname)' refs/jj/keep/ | wc -l
8
$ git -C … for-each-ref --format='%(refname:short)' refs/heads refs/remotes
master origin origin/master
$ git -C … status --porcelain
?? .ufo/waves/round-17/
?? census/operator-sweep-20261019/
$ stat -c '%A %n' /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh
-rwxr-xr-x /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh
```

`census/operator-sweep-20261019/` is operator-owned and was not opened. The wave-1 report
directory already existed; nothing outside this report path was written.

Read with line selectors: `SKILL.md:1-240` and the exact ranges `:50-60`, `:70-80`,
`:110-128`; `scripts/hyaku/jj-lane.sh:1-60`, `:150-250`, `:500-700`, `:206-235`,
`:524-555`, `:615-675`; `PROVINCE.md:1-40`; `corpus/lessons/round-16-verifier-spotcheck.md`;
`.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md:1-140`;
`.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md:1-120`;
`.ufo/waves/round-17/w1/ScribeSkillJj.md`.

## 8. Limits

- The helper's two-path commit is read, not run: no `ALLOWED-EXEC` was granted to this seat and the contract forbids running lane tools against a real directory. The claim "naming both paths commits both halves" is `[INFERENCE]` from `jj-lane.sh:543-548` + `:620-656` + `:669`; the block's `cat-file` post-check is what makes a wrong inference visible at use time.
- No `SKILL.md` edit was applied; this report is the deliverable. The line numbers are bytes at `5fa6017`.
- The block does not cover receipt queries, census `unpushed`, or the tools' `--not --all` roots; those are C3a/C3b and are deliberately left with one owner each.

## 9. Tool installs

None. No package, binary or upgrade was installed or needed.
