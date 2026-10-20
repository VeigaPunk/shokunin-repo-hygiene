STATUS: DONE — corrected draft of corpus/knowledge/jj-colocation-receipts.md is below (report only; the entry itself is not written); every claim re-grounded against jj v0.45.1 / git v2.56.0 source, in-lane fixture outputs at ddb7347 and 5fa6017, or a labelled lane observation.

Seat: `SoujiR17-3.ScribeKnowledgeFinal-2` · 2026-10-20 · lane `/home/vgpnk/Projects/shokunin/souji-shokunin` · landed rev ddb7347 · base 5fa6017 · leaf seat, no subagents, no commits, no `jj` writes, no lane tool executed. Axis: **coverage**.

## 0. Tooling record

- Nothing installed or upgraded. Host already has `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5` (`~/.local/bin/jj`) and `git version 2.56.0`.
- Source reads were web/read-only (`raw.githubusercontent.com` at tags `v0.45.1` and `v2.56.0`, via `curl -fsSL … | grep -n` piped, no file written).

## 1. Changes applied to the draft (what was wrong, what replaces it)

| # | Draft said | Correction | Ground |
|---|---|---|---|
| 1 | `source:` / Source rows `S0??`, own-work rows | Numbered S051–S063 (context plan); lane reports cited inline by file:line only | context numbering |
| 2 | verified-at "jj docs read 2026-10-20", no tag | Pinned: jj v0.45.1 tag, git v2.56.0 tag, host versions, fixture rev ddb7347 | `jj --version`, `git --version`, fixture TOOL/JJ lines |
| 3 | recheck via `docs.jj-vcs.dev/latest` | Recheck pins the tag source line `git_backend.rs:100` and runs the in-lane fixture (red at base, green at landed) | CriticC3 §4 Q1, Q4/Q16 |
| 4 | §1 "colocated concurrency is untested" quoted `technical/concurrency` | Replaced by the git-compatibility sentence (NFS/Dropbox sharing); concurrency page has no S-row | v0.45.1 `docs/git-compatibility.md:158-165` |
| 5 | §3 keep refs "for abandoned or hidden predecessors" (implied narrow) | Every commit jj writes through the keep-ref creation paths gets one (visible or hidden) | CriticC3 §3.3; `git_backend.rs:868-870, 497, 1466` |
| 6 | §3 `refs/jj/bookmarks` not mentioned; entry silent on other namespaces | Lists the only v0.45.1 `refs/jj/` namespaces: keep, remote-tags, root; bookmarks map to refs/heads and refs/remotes | `lib/src/git.rs:90-96` |
| 7 | §3 lifetime "[INFERENCE] from observed counts" only | Adds the source mechanism (`recreate_no_gc_refs`, 14-day `util gc` default, `op abandon` doc) and labels only the timing as inference | `git_backend.rs:902-953, 928-937, 1558-1564`; `gc.rs:55` and doc comment |
| 8 | §3 "the `git log --oneline HEAD --not --all` probe is keep-ref evidence" (JjAuditSouji F3) | Withdrawn: empty by construction because `--all` includes HEAD | S060 `rev-list-options.adoc@v2.56.0:168-169` |
| 9 | §4 unfiltered `--glob` rule with no novelty test | Landed rule (b'): refuse only when the keep-only commit's blob at the target is absent from remote history; over-refusal figures disclosed as the rejected proposal | CriticC3 §3.1; `souji-verify.sh:241-256` |
| 10 | Operating rule 4 "durable roots: refs/heads, refs/tags, refs/remotes" | Landed rule: every ref except `refs/jj/*` is an absent-worktree root (keeps `refs/stash`), never HEAD | `souji-verify.sh:854`; fixture J7 PASS at ddb7347 |
| 11 | §7 "not described in any jj page"; no mechanism | S056 (CHANGELOG 0.36.0) says directories containing `.jj` or `.git` are ignored; this is the likely mechanism for the observed phantom `D` lines, labelled inference; fixture has no nested-.git case | `CHANGELOG.md@v0.36.0` line 1268-1269 |
| 12 | §8 helper facts | Re-read: helper includes a path only if in branch tip (`:544-549`), refuses committed phantom deletions (`:618-619`) | `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh` |
| 13 | §10 git GC generic | Cites S063 (unreachable removal, 2-week prune default) and jj's `git gc --prune=@<keep_newer>` call | `git-gc.adoc@v2.56.0:18, 81-83`; `git_backend.rs:977` |
| 14 | Failure case "`tools/souji-verify.sh:351`, `tools/souji-vault-verify.sh:517` `log HEAD --not --all`" | Removed: those sites are in shadowed definitions (ddb7347 `souji-verify.sh:390` sits in the definition at :372, overridden by :1051). Failure cases now come from measured fixture outputs | `git show ddb7347:tools/souji-verify.sh`; CriticC3 §3.2 |
| 15 | Limits: "none is in a committed fixture" | Corrected: fixture `tests/fixtures/r17-jj-receipts.sh` covers §3 (J1–J2), §4 (J3–J5, J9), §6 plain-repo identity (J6, J8), stash root (J7); §2, §5, §7–§9, §11 remain lane observations | fixture outputs |
| 16 | Admission status "candidate — pending round-17 gate" | Kept; see §8 below on what `count-claims.py` will read | CriticC3 §2 |

Dropped rather than sourced: `git-comparison` "visible heads" quote (no S-id), the "rewritten predecessors under refs/jj/keep" wording (too narrow), the JjTrial "jj-owned index reset" hazard 4 (contradicts JjAudit F4; CriticC3 §4).

## 2. Verification performed (read-only; outputs quoted)

- `jj --version` → `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`; `git --version` → `git version 2.56.0`.
- v0.45.1 `lib/src/git_backend.rs`: `100:const NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/";`; `497: .edit_references(head_ids.iter().copied().map(to_no_gc_ref_update))`; `870:fn to_no_gc_ref_update`, doc "Used for preventing GC of commits we create" (`868-869`); `902:fn recreate_no_gc_refs`; `928-937` racy comment; `977: .arg(format!("--prune=@{} +0000", keep_newer.as_secs()))`; `1466: .edit_reference(to_no_gc_ref_update(&id))`; `1558-1564: fn gc … all_heads_for_gc() … recreate_no_gc_refs(&git_repo, new_heads, keep_newer)`.
- v0.45.1 `cli/src/commands/util/gc.rs`: `55: None => SystemTime::now() - Duration::from_secs(14 * 86400)`; `repo.store().gc(repo.index(), keep_newer)?` at `65`; doc "run `jj op abandon ..<some old operation>` before `jj util gc`".
- v0.45.1 `lib/src/git.rs`: `90-96` reserved and namespace constants (`refs/remotes/`, `refs/jj/remote-tags/`, `refs/jj/root`).
- v0.45.1 `docs/git-compatibility.md`: colocation default line; `38` .gitattributes No; `40` Hooks No (#405); `44-46` Detached HEAD; `52-54` GC; `158` "Jujutsu will ignore Git's staging area."; `163-165` concurrency sentence; `229` "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC."
- v0.45.1 `docs/bookmarks.md`: `11-12` "There is currently no concept of an active/current/checked-out bookmark."; `16` "Jujutsu maps its bookmarks to Git branches when interacting with Git repos."; `160` "When a commit has been abandoned, all associated bookmarks will be deleted."
- v0.45.1 `docs/working-copy.md:14` "added files are implicitly tracked by default."; v0.45.1 `docs/config.md` "Paths to automatically track": "All new files in the working copy that don't match the ignore patterns are tracked by default."
- v0.45.1 `CHANGELOG.md:1218` `## [0.36.0] - 2025-12-03`; `1268-1269` "Sub-repos are no longer tracked. Any directory containing `.jj` or `.git` is ignored. Note that Git submodules are unaffected by this."
- v2.56.0 `Documentation/rev-list-options.adoc:168-169` "Pretend as if all the refs in `refs/`, along with `HEAD`, are listed…"; `172-173` the `refs/heads` form. `Documentation/git-gc.adoc:18` "removing unreachable objects"; `81-83` `--prune=<date>` default 2 weeks. `list-objects.c:106-115` pathspec applied in the object tree walk (so `rev-list --objects -- <rel>` is path-limited).
- Landed tree `git show ddb7347:tools/souji-verify.sh`: `241-256 jj_keep_novel`, `694 try_pushed` with the call at `719`, `854` the `for-each-ref --exclude='refs/jj/'` root query; `390 log --oneline head --not --all` sits inside the definition at `372` that is overridden by the later `evaluate_worktree` at `1051` (shadowed, dead). Vault: `433 jj_keep_novel`, calls `914`, `1205`; `1061` `--exclude='refs/jj/'`. Quarantine: `977 jj_keep_novel`, call `341`; it runs `souji-verify.sh` as its receipt engine (`VERIFY_BIN`, `:176`).
- Base `git show 5fa6017:tools/souji-verify.sh:809` `for-each-ref --format='%(objectname)'` (no pattern: keep refs are roots at base).
- Fleet helper `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh`: `grep -nE 'op abandon|util gc'` → none; `544-549` "skipping missing path"; `618-619` phantom-deletion comment ("a nested empty .git dir makes jj see deletions").
- Census HEAD pins: `census/round-13/run-verification.py:384` `revision = git("rev-parse", "HEAD")`; `census/round-14/cache-demonstration.py:166` `["git", "-C", str(LANE), "rev-parse", "--verify", "HEAD"]`.
- Fixture outputs: `census/round-17/jj-receipts-base5fa6017.txt` `SUMMARY total=18 failed=7 skipped=2` (J1, J1-vault, J3, J3-vault, J3-quarantine, J9-file, J9-worktree FAIL; J6 SKIP); `census/round-17/jj-receipts-ddb7347.txt` `SUMMARY total=20 failed=0 skipped=0` (J6 identical=yes; J1/J3/J9 NOT-SAFE; J2/J4/J5 as expected; J7 SAFE).
- Knowledge namespace at ddb7347: `corpus/knowledge/` has `git-auto-maintenance-prunes-worktrees.md` (cross-link valid) and six other entries.

## 3. Corrected full text of `corpus/knowledge/jj-colocation-receipts.md` (draft; not written to the lane)

````markdown
source: see `## Source rows` (S051–S063). jj claims cite the v0.45.1 tag; git claims cite the v2.56.0 tag; lane observations cite the lane report by file:line and are labelled `observed`.
verified-at: 2026-10-20 — jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5 (`jj --version`); git 2.56.0 (`git --version`). jj and git sources read at tags v0.45.1 and v2.56.0 on 2026-10-20. In-lane fixture `tests/fixtures/r17-jj-receipts.sh` run at landed revision ddb7347 (`census/round-17/jj-receipts-ddb7347.txt`) and base 5fa6017 (`census/round-17/jj-receipts-base5fa6017.txt`).
recheck: `jj --version; git --version`. Source: `curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs | grep -n 'NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/"'` (expect line 100). Behaviour, from the lane root: `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` (expect exit 0 and `SUMMARY total=20 failed=0 skipped=0`; needs `git`, `rg`, `timeout`; J9 needs `jj` on PATH and is a SKIP, not a pass, without it). Base arm: `--tool-dir <tools/ of 5fa6017>` (expect `failed=7`). The fixture works in a `mktemp -d` under `/var/tmp` with an EXIT trap and never touches a live lane path.

# jj colocation changes what receipt-gated hygiene can trust

A jj-colocated repository (`.jj/` and `.git/` at one root) is jj's default for `jj git init` and `jj git clone`. The git refs, HEAD and index a receipt reads are then written by jj as well as by git. This entry records which git-side signals stay valid, which stop meaning what they meant, and the operating rules that follow. It is a knowledge entry: it does not change a gate by itself. The round-17 receipt tools implement the rules in §§3, 4 and 6; the Limits section says what the fixture does and does not show.

## 1. What jj does to the git store

- **Colocation is the default.** "This is the default for Git-backed workspace created with `jj git init` or `jj git clone`." — S051 (`docs/git-compatibility.md@v0.45.1`, "Colocated Jujutsu/Git workspaces") — `sourced`
- **Import and export run on every command.** "Jujutsu will import and export from and to the Git repo on every `jj` command automatically." — S051 — `sourced`
- **Mixing is permitted.** "It is allowed to mix `jj` and `git` commands in such a workspace in any order." — S051 — `sourced`
- **The same section names the risk.** "Interleaving `jj` and `git` commands increases the chance of confusing branch conflicts" — S051 — `sourced`
- **Shared-filesystem concurrency is untested.** "In general, such use of Jujutsu is not currently thoroughly tested." is said of colocated workspaces shared over NFS or Dropbox (S051, v0.45.1 lines 163–165). The docs do not say whether a single-user colocated lane is covered by that statement; this entry does not claim it is.

## 2. Detached HEAD (`@-`)

- **jj leaves git HEAD detached.** "`jj` commands will usually put the Git repo in a "detached HEAD" state" — S051 — `sourced`
- **There is no current bookmark.** "There is currently no concept of an active/current/checked-out bookmark." — S055 (`docs/bookmarks.md@v0.45.1`) — `sourced`
- **Observed:** after `jj-lane.sh init`, HEAD was attached to `refs/heads/master`; after the first jj mutation it was detached at the just-committed hash (JjTrialSouji.md:23, :48; `git rev-parse @{u}` failed, :78). `observed (jj 0.45.1, git 2.56.0; lane report)`
- **[INFERENCE]** the detached commit is the parent of the new working-copy commit, `@-`. The observation shows HEAD at the committed change; the `@-` label is the jj model, not a printed fact.
- **Consequence:** any check that resolves `@{u}`, reads `symbolic-ref HEAD`, or assumes HEAD sits on a branch is wrong in a colocated lane. The receipt code uses explicit refs for its roots; `measured_commit` pins that read HEAD are the exception (§9).

## 3. Refs jj holds under `refs/jj/`

- **Docs.** "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC." — S051 (`docs/git-compatibility.md@v0.45.1:229`) — `sourced`
- **Source: the namespace.** `NO_GC_REF_NAMESPACE` is `refs/jj/keep/` (`lib/src/git_backend.rs@v0.45.1:100`). `to_no_gc_ref_update` builds one keep ref per commit id, documented "Used for preventing GC of commits we create" (`:868-870`). It is called on the write paths at `:497` and `:1466`. So every commit jj writes through those paths gets a keep ref, visible or hidden, not only abandoned predecessors — S054 — `sourced`
- **Source: other `refs/jj/` namespaces at v0.45.1.** `refs/jj/remote-tags/` (remote tags fetched temporarily) and `refs/jj/root` (placeholder for an unborn HEAD) (`lib/src/git.rs@v0.45.1:94, 96`). Bookmarks are not stored under `refs/jj/`; they map to `refs/heads` and remote bookmarks to `refs/remotes/` (S055; `git.rs:90-92`). — S054, S055 — `sourced`
- **Source: lifetime, as far as the code goes.** `gc` (`git_backend.rs:1558-1564`) calls `recreate_no_gc_refs` (`:902-953`) with `all_heads_for_gc()`. Keep refs for current heads are kept. Other keep refs are deleted when their loose-ref file is older than the threshold. The source comment calls that timestamp check "still racy on re-import" (`:928-937`). `jj util gc` uses a 14-day threshold by default (`cli/src/commands/util/gc.rs@v0.45.1:55`), and its doc says to run `jj op abandon ..<some old operation>` first (same file, doc comment). — S054 — `sourced`
- **[INFERENCE]** a commit hidden by a rewrite keeps its keep ref until its operation is abandoned, `jj util gc` runs, and the ref is older than the threshold. The docs read do not state this; the timing is the inference, not the mechanism.
- **Observed:** an unbookmarked `jj commit` left HEAD detached with `refs/jj/keep/<sha>` as its only containing ref (JjAuditSouji.md:103-104). JjTrialSouji.md:61 counts 15 keep refs after one commit cycle. `observed (jj 0.45.1, git 2.56.0; lane report)`
- **Roots: the git query semantics.** "Pretend as if all the refs in `refs/`, along with `HEAD`, are listed on the command line as _<commit>_." describes `--all`; "Pretend as if all the refs in `refs/heads` are listed on the command line as _<commit>_." describes `--branches` (S060, `rev-list-options.adoc@v2.56.0:168-172`). — `sourced`
- **Consequence.** `git log <head> --not --all` is empty for every head, because `--all` includes HEAD and every ref. That output says nothing about keep refs and is not evidence for them; JjAuditSouji F3 (:122-128) is withdrawn as evidence. A keep-only head must not be judged by `--all` or by `refs/jj/*`.
- **Rule (landed).** An absent-worktree receipt takes every ref except `refs/jj/*` as a root (`for-each-ref --exclude='refs/jj/'`), and never HEAD (§9). This keeps `refs/stash` and `refs/original` as roots in plain repositories too (fixture J7).

## 4. Unbookmarked commits are invisible to branch-based unpushed checks

- **Bookmarks map to branches only.** "Jujutsu maps its bookmarks to Git branches when interacting with Git repos." — S055 — `sourced`
- **Abandoned commits lose their bookmarks.** "When a commit has been abandoned, all associated bookmarks will be deleted." — S055 — `sourced`
- **Observed:** after an unbookmarked `jj commit`, `git log --branches --not --remotes --oneline` and `git rev-list --count --branches --not --remotes` both returned nothing, while `git status --porcelain -uall` was empty (JjAuditSouji.md:97-102). `observed (jj 0.45.1, git 2.56.0; lane report)`
- **Consequence.** `--branches --not --remotes` reports "no unpushed work" for a commit held only by a keep ref. The census `unpushed` column is branch-based and reads 0 here (JjTrialSouji.md:59). This is disclosed and ungoverned (§11).
- **Rule (landed, `jj_keep_novel`).** For a pushed receipt, a keep-only commit `C` that touches the target refuses only when `C:<rel>` exists and its blob is absent from the object list of remote-reachable history for `<rel>` (`git rev-list --objects --remotes -- <rel>`; the pathspec limits the tree walk, S060 `list-objects.c@v2.56.0:106-115`). Deletions (no blob at `<rel>`) and blobs already published do not refuse. The receipt names the refusal with the token `jj-keep-novel`. Implemented at `tools/souji-verify.sh:241-256`, `tools/souji-vault-verify.sh:433`, `tools/souji-quarantine.sh:977`.
- **Failure case of the old rule (base 5fa6017).** J3, a keep-only commit with novel content, returned `SAFE(pushed)` (`census/round-17/jj-receipts-base5fa6017.txt:19`). It returns `NOT-SAFE` at ddb7347 (`jj-receipts-ddb7347.txt:22`).
- **Failure case of the unfiltered proposal (rejected).** Refusing on every keep-only commit that touches the path would have refused 1,877 paths on four live colocated lanes (souji, kama, tameshi, mado), of which 0 held novel keep-only content. `observed (read-only git on live lanes, 2026-10-20; lane review, not in a committed fixture)`.

## 5. The index is not a signal

- **jj ignores the staging area.** "Jujutsu will ignore Git's staging area." — S051 (`docs/git-compatibility.md@v0.45.1:158`) — `sourced`
- **Observed:** `git add` then an unrelated `jj st` kept the entry; `jj commit` then cleared the index; `git mv` produced `R` in git and jj recorded the rename, but the index entry was not what jj committed (JjAuditSouji.md:136-152). `observed (jj 0.45.1, git 2.56.0; lane report)`
- **Observed:** `git add` then `jj describe` left the file back at `??` (JjTrialSouji.md:79).
- **Consequence.** `git add -- <paths> && git commit -- <paths>` cannot coexist with interleaved jj calls. `git ls-files --error-unmatch` and `git rm --cached` answers can change between two steps of one operation (JjAuditSouji.md:154).

## 6. Auto-track must be `none()`

- **Default tracks new files.** "All new files in the working copy that don't match the ignore patterns are tracked by default." — S053 (`docs/config.md@v0.45.1`, "Paths to automatically track") — `sourced`
- **Implicit tracking.** "added files are implicitly tracked by default." — S052 (`docs/working-copy.md@v0.45.1:14`) — `sourced`
- **Observed:** with `snapshot.auto-track="all()"` the first `jj status` added 152 files from an untracked directory; `git status` went from 1 to 152 ` A` entries (JjTrialSouji.md:29-31). With `none()` the same tree stayed at one line (JjTrialSouji.md:22, :24). `observed (jj 0.45.1, git 2.56.0; lane report)`
- **Observed:** the census counts `??` as dirty but not intent-to-add ` A` entries; the auto-tracked clone reported `dirty=0` (JjTrialSouji.md:62; hazard 5 at :80).
- **Rule.** Set `snapshot.auto-track = "none()"` on every colocated lane, in the repository config (the `snapshot` settings, S053). Measured effect: no index spam (JjTrialSouji.md:88).

## 7. Nested `.git` produces phantom deletions

- **Sub-repos are ignored.** "Sub-repos are no longer tracked. Any directory containing `.jj` or `.git` is ignored. Note that Git submodules are unaffected by this." — S056 (`CHANGELOG.md@v0.36.0`, 2025-12-03, line 1268) — `sourced`
- **Submodules, the nearest docs statement.** "They will not show up in the working copy, but they will not be lost either." — S051 — `sourced`. The docs read do not describe a plain nested `.git` directory beyond S056.
- **Observed:** `tests/vault/vadv54-run/p/p6repo/` contains an empty `.git/`. `jj status` reported `D p6repo/one.txt` and `D p6repo/inner/keep.txt` for files that exist on disk and that git tracks normally. A `jj commit` with a directory pathspec over `tests/vault/vadv54-run` committed those deletions (commit c31a345, JjTrialSouji.md:76). `observed (n=1; lane report)`
- **[INFERENCE]** S056 is the likely mechanism: the directory contains `.git`, so jj ignores it and reports its tracked files as deleted. The fleet helper's own comment gives the same mechanism (`scripts/hyaku/jj-lane.sh:618-619`). The fixture has no nested-`.git` case, so this is untested in-lane.
- **Rule.** Use exact file paths in a jj commit pathspec under any tree that may contain nested `.git`. Do not commit a directory pathspec over such a tree (§8). The vault harness creates the empty stub only around case P6 and removes it on exit (per L1; the landed state was not re-checked in this seat).

## 8. Helper-only commits must name both paths of a move

- **Observed failure:** `jj-lane.sh commit` given only the source of a `git mv` warned "skipping missing path", committed nothing for it, and pushed the destination only. The pushed tree still held the old path (JjAuditSouji.md:58-72, F1 at :55). A pure deletion printed "nothing to commit (no such paths)" and the file stayed in the pushed tree (:77-84). `observed (jj 0.45.1, git 2.56.0; lane report)`
- **Helper source (`scripts/hyaku/jj-lane.sh`, read in this seat, not executed).** `:544-549` includes a missing path only when it is present in the branch tip, otherwise it warns "skipping missing path". `:618-619` refuses a committed deletion of a file that still exists on disk (the nested empty `.git` case). Per CriticC3 §3.4 (not re-read here), that check runs after `jj commit` has created the commit, so a refused attempt still leaves a keep-held commit (§3).
- **Rule.** A quarantine move is one helper commit naming BOTH the old and the new path. Do not split source and destination across commits. Do not commit a directory pathspec that may hide a nested `.git` (§7).

## 9. Evidence that records HEAD

- **Observed:** `census/round-13/run-verification.py:384` and `census/round-14/cache-demonstration.py:166` record `HEAD` as the measured commit (`rev-parse HEAD`, JjAuditSouji.md:156-158). In a colocated lane that commit can be a detached, unbookmarked jj commit held only by keep refs; a later jj or git gc can make the evidence unreplayable. `observed (lane report; source lines read at ddb7347)`
- **Rule.** Pin an explicit commit that is on `refs/heads`, `refs/tags` or `refs/remotes`, or refuse the record.

## 10. Git's own GC is not validated on colocated repositories

- **jj does not garbage-collect its own store yet.** "There's no garbage collection and repacking of Jujutsu's own data structures yet" — S051 (v0.45.1 `docs/git-compatibility.md`, GC bullet) — `sourced`
- **git gc is untested with jj.** "It should be safe to run `git gc` in the Git repo, but it's not tested" — S051 — `sourced`
- **What git gc does.** It removes unreachable objects, and its `--prune` date defaults to two weeks ago (S063, `git-gc.adoc@v2.56.0:18, 81-83`). jj's `util gc` runs `git gc --prune=@<keep_newer>` (`lib/src/git_backend.rs@v0.45.1:977`), so the two prune clocks are linked — S054 — `sourced`
- **Consequence.** The auto-maintenance worktree-prune risk in `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md` applies to colocated lanes without a jj-specific test. Keep `-c maintenance.auto=false` on every receipt-gated commit (`corpus/QUALITY.md` Q7). A receipt that relies on keep refs inherits both gaps.

## 11. What jj does not carry over to git hooks or attributes

- **Hooks: no.** "There's #405 specifically for providing the checks from pre-commit.com" — S051 (`docs/git-compatibility.md@v0.45.1:40`) — `sourced`
- **`.gitattributes`: no.** ".gitattributes: No." with a pointer to "adding support for at least the `eol` attribute" — S051 (`:38`) — `sourced`
- **Observed:** a `pre-commit` hook did not run under `jj commit`; a `filter.f.clean` was not applied; `eol=crlf` was ignored (JjAuditSouji.md:172). `observed (jj 0.45.1, git 2.56.0; lane report)`
- **Consequence.** A git-side hook or attribute is not a guard on the jj write path. The census's filter-driver checks (QUALITY Q21 family) do not cover writes made by jj.

## Operating rules (receipt-gated lanes)

1. Set `snapshot.auto-track = "none()"` before first use (§6).
2. Commit with the helper and an exact pathspec that names every changed path, both sides of a move (§8). No `git add` before a jj call (§5).
3. Never pass a directory pathspec over a tree that can contain nested `.git` (§7).
4. Absent-worktree receipts take every ref except `refs/jj/*` as a root (`for-each-ref --exclude='refs/jj/'`), never HEAD. Do not use `--all`, `--not --all`, or `refs/jj/*` as a root (§3).
5. A keep-only commit that touches the target refuses a pushed receipt only when its blob at the target path is novel to remote history (`jj_keep_novel`, §4). Receipts that rely on it disclose the `jj-keep-novel` token.
6. Do not pin `HEAD` in evidence (§9).
7. Plain repositories (no `refs/jj/`) must produce byte-identical verify and vault output; fixture J6 checks it.

## Limits

- **Keep-ref lifetime.** The docs read do not state it. The timing in §3 is an inference from source and from observed keep-ref counts. The lane helper (`scripts/hyaku/jj-lane.sh`) contains neither `jj op abandon` nor `jj util gc`, so hidden keep-held commits in lanes are not pruned by the lane tooling. That is an observation of the helper, not a jj guarantee.
- **Git-emulated fixture.** J1–J8 synthesize `refs/jj/keep/<sha>` with `git update-ref`. They test how the receipt tools handle a `refs/jj/keep` namespace, not jj's own behaviour. J9 uses jj 0.45.1 to create real keep refs; it is one run per landing. The fixture runs the CLIs, so only the last-defined functions are measured.
- **Lane observations, not fixtures.** §2 (detached HEAD), §4 observed counts, §5, §7 nested `.git`, §8, §9, §11 rest on JjAuditSouji and JjTrialSouji, run in sandbox repositories at jj 0.45.1 and git 2.56.0. They were not re-run in the round-17 scribe seat.
- **n=1 observations.** The metaedit-predecessor case (change-id `yurlroyq…`, live read-only, 2026-10-20) and the phantom-deletion commit c31a345 are single instances.
- **Counts drift.** tameshi keep-only commits were 12 at JjAuditSouji:107 and 13 at the live read.
- **Nested `.git` mechanism.** The S056 explanation (§7) is an inference; no fixture covers it.
- **Ungoverned residue (frontier; disclosed, not fixed here):**
  - census `unpushed` column is branch-based (§4);
  - `souji-repo-structure.sh` ref and object inflation (JjTrialSouji.md:57, 61: `references.others.count=15`; commits 55 vs 44);
  - `measured_commit` is the detached `@-` (§9; JjAuditSouji F5);
  - index ownership and `git mv` (§5; F4);
  - hook, filter and eol bypass (§11; F7);
  - intent-to-add invisibility when `snapshot.auto-track` is not `none()` (§6; JjTrialSouji hazard 5);
  - lock hygiene (F6);
  - `util gc` pruning of hidden keep-held commits (Limits, first bullet).

## Failure cases (Q3)

- **F-1 Base SAFE where NOT-SAFE is correct (fixture).** At 5fa6017: J1 and J1-vault, an absent-worktree head held only by `refs/jj/keep/*`, returned `SAFE(metadata-prune)` (`census/round-17/jj-receipts-base5fa6017.txt:15-16`); J3, J3-vault and J3-quarantine, a keep-only commit with novel content, returned `SAFE(pushed)` (`:19-21`); J9-file and J9-worktree, real jj 0.45.1 keep refs, returned `SAFE` (`:28-29`). Landed at ddb7347: `NOT-SAFE` for all of these (`census/round-17/jj-receipts-ddb7347.txt:18-19, 22-24, 31-32`).
- **F-2 Over-refusal of the unfiltered keep-only rule (lane review).** See §4; rejected by the novelty test.
- **F-3 Helper commit leaves the moved source at the old path.** JjAuditSouji.md:55-86 (F1).
- **F-4 Phantom deletions committed through a directory pathspec.** JjTrialSouji.md:76, commit c31a345 (n=1).
- **F-5 A vacuous probe read as evidence.** `git log --oneline HEAD --not --all` (JjAuditSouji.md:122-128) is empty by construction (§3). It is not keep-ref evidence.

## Source rows

- **S051** — jj Git compatibility — `https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/git-compatibility.md` (rendered: https://docs.jj-vcs.dev/v0.45.1/git-compatibility/). Read at tag v0.45.1: colocation, detached HEAD, staging area, `refs/jj/` GC ref, hooks, attributes, submodules, GC. Used in §§1, 2, 3, 5, 7, 10, 11.
- **S052** — jj Working copy — `https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/working-copy.md` (line 14). Used in §6.
- **S053** — jj Configuration — `https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/config.md` ("Paths to automatically track"; `git.colocate`). Used in §6.
- **S054** — jj source at tag — `lib/src/git_backend.rs@v0.45.1` (`:100, 497, 868-870, 902-953, 928-937, 977, 1466, 1558-1564`); `cli/src/commands/util/gc.rs@v0.45.1` (`:55, 65`, doc comment); `lib/src/git.rs@v0.45.1` (`:90-96`). Used in §§3, 10.
- **S055** — jj Bookmarks — `https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/bookmarks.md` (`:11-12, 16, 160`). Used in §§2, 4.
- **S056** — jj CHANGELOG at tag — `CHANGELOG.md@v0.36.0` (`## [0.36.0] - 2025-12-03`, bullet at `:1268-1269`: sub-repos containing `.jj` or `.git` are ignored). Used in §7.
- **S057** — git-config `status.showUntrackedFiles` / `git status -u`. Not cited by any claim in this entry (census D1 material).
- **S058** — git-worktree `config.worktree` and git-config includes. Not cited by any claim in this entry.
- **S059** — gitrepository-layout and `info/attributes`. Not cited by any claim in this entry (§11 cites S051 for `.gitattributes`).
- **S060** — git rev-list — `Documentation/rev-list-options.adoc@v2.56.0` (`:168-172`, `--all` and `--branches`); `list-objects.c@v2.56.0:106-115` (pathspec in object tree walk). Used in §§3, 4.
- **S061** — Python `str.lstrip` / `removeprefix`. Not cited by any claim in this entry.
- **S062** — `fifo(7)` / `open(2)`. Not cited by any claim in this entry.
- **S063** — git-gc — `Documentation/git-gc.adoc@v2.56.0` (`:18` unreachable removal; `:81-83` `--prune` default two weeks). Used in §10.

Lane reports (cited inline by file and line, not S-rows): JjAuditSouji.md (`.ufo/waves/hyaku/jj-w1/reports/`), JjTrialSouji.md (same), fixture outputs `census/round-17/jj-receipts-{base5fa6017,ddb7347}.txt`.

## Admission status

candidate — pending round-17 gate
````

## 4. Notes for L1 (integration; not edits made here)

- **Counting trap.** Committing this file without a `HELD` heading moves `count-claims.py` (`census/round-14/count-claims.py:19-20, 26`) to `admitted_knowledge 6`. Report it as `admitted_knowledge 6 (author inventory; admission pending closure)`, as r13 did. The entry cannot certify itself (CriticC3 §2).
- **Tool prose to fix (out of this entry).** `souji-vault-verify.sh` worktree note says "working-copy bookmarks under `refs/jj/bookmarks`"; no such namespace exists at v0.45.1 (`git.rs:90-96`). Replace with the S055 / `refs/heads` wording.
- **Dead sites.** The `--not --all` and `log HEAD --not --all` queries are in shadowed definitions (`souji-verify.sh:390` under `:372`; `souji-vault-verify.sh` likewise). Delete or label them; do not count them as enforcement.
- **Quarantine comment.** `souji-quarantine.sh:116` says `for-each-ref --exclude='refs/jj/'` covers its roots. The effective root query is in its receipt engine (`souji-verify.sh`, run as a child); the comment should say so.
- **Scope wording** for the SKILL/PROVINCE drafts: "bounded receipt-root rule for jj-colocated lanes (Core); jj-colocated repositories otherwise frontier", listing §11 residue (CriticC3 §7).
- **Fixture coverage.** J1–J9 are git-emulated except J9. Do not describe them as jj behaviour in SKILL or README text.
- **Not verified here.** The landed-state of `tests/vault/vadv54-harness.sh` (stub creation around P6), the `count-claims.py` output, and the `corpus/QUALITY.md` Q7/Q21 references were not re-read in this seat.

## 5. Out of scope (not touched)

- No file in the lane written. No commit, no `jj` invocation, no lane tool run, no `census/operator-sweep-20261019/` opened, no `MANIFEST.json`, `.ufo/state`, or fleet repo written.
- Only this report file was written.
