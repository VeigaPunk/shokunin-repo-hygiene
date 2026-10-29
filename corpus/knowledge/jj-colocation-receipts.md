source: see `## Source rows` (S051–S063). jj claims cite the v0.45.1 tag; git claims cite the v2.56.0 tag; lane observations cite the lane report by file:line and are labelled `observed`.
verified-at: 2026-10-20 — jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5 (`jj --version`); git 2.56.0 (`git --version`). jj and git sources read at tags v0.45.1 and v2.56.0 on 2026-10-20. In-lane fixture `tests/fixtures/r17-jj-receipts.sh` run on the landed tools (committed record `census/round-17/jj-receipts-4f48343.txt`, tool digests = 4f48343 bytes; r18 correction: this line first cited a `ddb7347` record that was never committed) and base 5fa6017 (`census/round-17/jj-receipts-base5fa6017.txt`).
recheck: `jj --version; git --version`. Source: `curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs | grep -n 'NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/"'` (expect line 100). Behaviour, from the lane root: `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` (expect exit 0 and `SUMMARY total=35 failed=0 skipped=2` — the two J6 identity cases SKIP without `--baseline-dir`; r18 correction: this line said `total=20 … skipped=0`, the wave-1 shape; needs `git`, `rg`, `timeout`; J9 needs `jj` on PATH and is a SKIP, not a pass, without it). Base arm: `--tool-dir <tools/ of 5fa6017>` (expect failed > 0; the committed base record shows 13). The fixture works in a `mktemp -d` under `/var/tmp` with an EXIT trap and never touches a live lane path.

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
- **Rule (landed, `jj_keep_novel`).** For a pushed receipt, a keep-only commit `C` that touches the target refuses only when `C:<rel>` exists and its blob is absent from the object list of remote-reachable history for `<rel>` (`git rev-list --objects --remotes -- <rel>`; the pathspec limits the tree walk, S060 `list-objects.c@v2.56.0:106-115`). Deletions (no blob at `<rel>`) and blobs already published do not refuse. The receipt names the refusal with the token `jj-keep-novel`. Implemented as `jj_keep_novel` in `tools/souji-verify.sh`, `tools/souji-vault-verify.sh` and `tools/souji-quarantine.sh` (identical bodies), called from the live (last-defined) receipt functions only.
- **Failure case of the old rule (base 5fa6017).** J3, a keep-only commit with novel content, returned `SAFE(pushed)` (`census/round-17/jj-receipts-base5fa6017.txt`). It returns `NOT-SAFE` on the landed tools (`census/round-17/jj-receipts-4f48343.txt`).
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

- **Sub-repos are ignored.** "Sub-repos are no longer tracked. Any directory containing `.jj` or `.git` is ignored. Note that Git submodules are unaffected by this." — S056 (`CHANGELOG.md@v0.45.1:1268-1269`, section `[0.36.0] - 2025-12-03`) — `sourced`
- **Submodules, the nearest docs statement.** "They will not show up in the working copy, but they will not be lost either." — S051 — `sourced`. The docs read do not describe a plain nested `.git` directory beyond S056.
- **Observed:** `tests/vault/vadv54-run/p/p6repo/` contains an empty `.git/`. `jj status` reported `D p6repo/one.txt` and `D p6repo/inner/keep.txt` for files that exist on disk and that git tracks normally. A `jj commit` with a directory pathspec over `tests/vault/vadv54-run` committed those deletions (commit c31a345, JjTrialSouji.md:76). `observed (n=1; lane report)`
- **[INFERENCE]** S056 is the likely mechanism: the directory contains `.git`, so jj ignores it and reports its tracked files as deleted. The fleet helper's own comment gives the same mechanism (`scripts/hyaku/jj-lane.sh:618-619`). The fixture has no nested-`.git` case, so this is untested in-lane.
- **Observed (this lane, round 17):** removing the empty stub did not clear the hazard. With `snapshot.auto-track = "none()"` the snapshot had already recorded `D p6repo/one.txt` and `D p6repo/inner/keep.txt` in `@`, and files that reappear on disk are not re-tracked, so `@` kept the deletions and every later helper commit left one more keep-held commit carrying them (16 keep-only commits, 14 with the two phantom deletions, read-only `git rev-list --glob='refs/jj/keep/*' --not --branches --remotes --tags` at 16:10 -03). A helper call naming the two files (`jj-lane.sh commit … -- <both files>`, which runs `jj file track` on named files) re-tracked them: it printed `nothing to commit` (content equals the tip) and `jj --ignore-working-copy status` no longer lists them. `observed (n=1)`
- **Rule.** Use exact file paths in a jj commit pathspec under any tree that may contain nested `.git`. Do not commit a directory pathspec over such a tree (§8). The vault harness (`tests/vault/vadv54-harness.sh`) creates the empty stub only around case P6 and removes it on exit; the at-rest stub in this lane was moved out of the tracked tree in round 17 (`corpus/lessons/round-17.md`).

## 8. Helper-only commits must name both paths of a move

- **Observed failure:** `jj-lane.sh commit` given only the source of a `git mv` warned "skipping missing path", committed nothing for it, and pushed the destination only. The pushed tree still held the old path (JjAuditSouji.md:58-72, F1 at :55). A pure deletion printed "nothing to commit (no such paths)" and the file stayed in the pushed tree (:77-84). `observed (jj 0.45.1, git 2.56.0; lane report)`
- **Helper source (`scripts/hyaku/jj-lane.sh`, read in this seat, not executed).** `:544-549` includes a missing path only when it is present in the branch tip, otherwise it warns "skipping missing path". `:618-619` refuses a committed deletion of a file that still exists on disk (the nested empty `.git` case). That check runs after `jj commit` has created the commit (`:604` vs `:618-654`), so a refused attempt still leaves a keep-held commit (§3); this lane holds four such phantom-deletion commits (`corpus/lessons/round-17.md`). The helper is fleet-owned; souji records the hazard and does not change it.
- **Rule.** A quarantine move is one helper commit naming BOTH the old and the new path. Do not split source and destination across commits. Do not commit a directory pathspec that may hide a nested `.git` (§7).

## 9. Evidence that records HEAD

- **Observed:** `census/round-13/run-verification.py:384` and `census/round-14/cache-demonstration.py:166` record `HEAD` as the measured commit (`rev-parse HEAD`, JjAuditSouji.md:156-158). In a colocated lane that commit can be a detached, unbookmarked jj commit held only by keep refs; a later jj or git gc can make the evidence unreplayable. `observed (lane report; source lines read at ddb7347)`
- **Rule.** Pin an explicit commit that is on `refs/heads`, `refs/tags` or `refs/remotes`, or refuse the record.

## 10. Git's own GC is not validated on colocated repositories

- **jj does not garbage-collect its own store yet.** "There's no garbage collection and repacking of Jujutsu's own data structures yet" — S051 (v0.45.1 `docs/git-compatibility.md`, GC bullet) — `sourced`
- **git gc is untested with jj.** "It should be safe to run `git gc` in the Git repo, but it's not tested" — S051 — `sourced`
- **What git gc does.** It removes unreachable objects, and its `--prune` date defaults to two weeks ago (S063, `git-gc.adoc@v2.56.0:18, 81-83`). jj's `util gc` runs `git gc --prune=@<keep_newer>` (`lib/src/git_backend.rs@v0.45.1:977`), so the two prune clocks are linked — S054 — `sourced`
- **Consequence.** The auto-maintenance worktree-prune risk in `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md` applies to colocated lanes without a jj-specific test. Keep `-c maintenance.auto=false` on every plain-repo receipt-gated commit (`corpus/QUALITY.md` Q7); colocated repos commit only through the owning lane's helper (Q29, r18). A receipt that relies on keep refs inherits both gaps.

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
- **Lane observations, not fixtures.** §2 (detached HEAD), §4 observed counts, §5, §7 nested `.git`, §8, §9, §11 rest on JjAuditSouji and JjTrialSouji, run in sandbox repositories at jj 0.45.1 and git 2.56.0. They were not re-run in round 17.
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

- **F-1 Base SAFE where NOT-SAFE is correct (fixture).** At 5fa6017: J1 and J1-vault, an absent-worktree head held only by `refs/jj/keep/*`, returned `SAFE(metadata-prune)` (`census/round-17/jj-receipts-base5fa6017.txt:15-16`); J3, J3-vault and J3-quarantine, a keep-only commit with novel content, returned `SAFE(pushed)` (`:19-21`); J9-file and J9-worktree, real jj 0.45.1 keep refs, returned `SAFE` (`:28-29`). Landed tools (4f48343 bytes): `NOT-SAFE` for all of these (`census/round-17/jj-receipts-4f48343.txt:18-19, 22-24, 31-32`).
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
- **S056** — jj CHANGELOG at tag — `CHANGELOG.md@v0.45.1` (`## [0.36.0] - 2025-12-03` at `:1218`, bullet at `:1268-1269`: sub-repos containing `.jj` or `.git` are ignored). Used in §7.
- **S057** — git-config `status.showUntrackedFiles` / `git status -u`. Not cited by any claim in this entry (census D1 material).
- **S058** — git-worktree `config.worktree` and git-config includes. Not cited by any claim in this entry.
- **S059** — gitrepository-layout and `info/attributes`. Not cited by any claim in this entry (§11 cites S051 for `.gitattributes`).
- **S060** — git rev-list — `Documentation/rev-list-options.adoc@v2.56.0` (`:168-172`, `--all` and `--branches`); `list-objects.c@v2.56.0:106-115` (pathspec in object tree walk). Used in §§3, 4.
- **S061** — Python `str.lstrip` / `removeprefix`. Not cited by any claim in this entry.
- **S062** — `fifo(7)` / `open(2)`. Not cited by any claim in this entry.
- **S063** — git-gc — `Documentation/git-gc.adoc@v2.56.0` (`:18` unreachable removal; `:81-83` `--prune` default two weeks). Used in §10.

Lane reports (cited inline by file and line, not S-rows): JjAuditSouji.md (byte-exact lane copy `census/round-42/jj-w1-reports/`; original in the fleet repo at fleet path `.ufo/waves/hyaku/jj-w1/reports/`, fleet commit f47ad6ba8d30), JjTrialSouji.md (same), fixture outputs `census/round-17/jj-receipts-{base5fa6017,4f48343}.txt`.

## Admission status

candidate — pending round-17 gate
