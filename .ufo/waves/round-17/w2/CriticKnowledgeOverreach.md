STATUS: DONE — the draft is not admissible as written: 3 claims contradict landed code or measured state, 5 are miscalibrated against their own sources, 3 cite sources with no planned S-row, and 4 sections belong to the fleet helper or host-tooling domains. A 14-claim minimal version is drafted in §5.

# CriticKnowledgeOverreach — round 17 w2 (attacks `corpus/knowledge/jj-colocation-receipts.md`)

Target: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/jj-colocation-receipts.md`. The file is untracked (`git ls-files --error-unmatch` → "did not match"). sha256 `2e4ea0447a63c39659728b993b7f3d94aea17a966cd87edc3757f8c2d216e9d5`, mtime 13:35:33. The landed code ddb7347 is from 14:22:08, so **the draft predates the code it describes**.
Axes judged: **coverage** (is every claim classified, with nothing missing that landed evidence now supports) and **calibration** (does each claim's label match the strength and version of its evidence).

## 1. Version check: 0.46 docs vs the host's 0.45.1

- `~/.local/bin/jj --version` → `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`.
- `curl -fsSL https://docs.jj-vcs.dev/versions.json` → `v0.46.0 ['latest']`, then `v0.45.1`. Every URL in the draft is `/latest/`, so every docs citation points at **0.46.0**, not the host's version.
- I re-fetched each quoted page at `/v0.45.1/` and `/latest/` and grepped for the draft's quoted sentences:

| page | quoted sentences in 0.45.1 | page diff |
|---|---|---|
| git-compatibility | all present (colocation default, import/export every command, mix allowed, interleaving, detached HEAD, `refs/jj/` GC ref, staging ignored, hooks No, .gitattributes No, git gc not tested, submodules) | 0.46 adds the "In the same working copy (colocated)" subsection; 0.45.1 has the older `--git-repo` paragraph |
| technical/concurrency | present; the sha256 of the context block is identical (`2a942b0d…`) in both | none in the quoted block |
| bookmarks | present (`maps its bookmarks`, `all associated bookmarks will be deleted`, `no concept of an`) | byte count identical |
| config | present (`match the ignore patterns are tracked by default` at 0.45.1 line 5203; `jj config edit --repo`) | 115338 vs 112065 bytes |
| working-copy | present (`implicitly tracked by default`) | 22106 vs 21613 bytes |
| git-comparison | present (`keeps track of all visible heads`) | identical |

**Verdict: holds in content, fails in anchoring.** Every quote is also true at 0.45.1, but the citations float. `recheck:` runs `curl …/latest/git-compatibility/ | grep -c 'refs/jj/'`, which already re-checks 0.46.0, a version the host does not run. It will keep passing while the host stays on 0.45.1, so it cannot detect drift in either direction.

**w1 source rows anchored at v0.46.0.** `SrcJjKeepRefs.md:30-36,46` and `SrcJjNestedRepo.md:15,32-34` pin their tag-source claims at v0.46.0. I re-anchored each one at v0.45.1 (raw GitHub at tag v0.45.1):

- `lib/src/local_working_copy.rs:821` defines `RESERVED_DIR_NAMES = [".git", ".jj"]`. Lines `:1637-1640` hold "we ignore all nested repos entirely" and the `symlink_metadata().is_ok()` presence loop.
- `lib/src/git_backend.rs:100` defines `NO_GC_REF_NAMESPACE = "refs/jj/keep/"`. Lines `:493-498` are inside `import_head_commits`: "Create no-gc ref even if known to the extras table". Line `:900` is `recreate_no_gc_refs`; line `:1558` is `fn gc`.
- `lib/src/git.rs:94,96` define `refs/jj/remote-tags/` and `refs/jj/root`.
- `docs/technical/architecture.md:78-80` names the `refs/jj/keep/` namespace and "To prevent GC…".
- `CHANGELOG.md` at v0.45.1: `:1218` is `## [0.36.0]` and `:1268` is "Sub-repos are no longer tracked…".
- `cli-reference` at v0.45.1: line 9732 "Run backend-dependent garbage collection."; line 9737 "…older than 2 weeks are pruned."

So every planned S054/S056 claim holds at the host version, provided the row anchors cite `@v0.45.1` and not `@v0.46.0`.

**0.46-only behaviour the entry must not import.** The 0.46.0 CHANGELOG says "Jujutsu can now colocate workspaces besides the default one by creating Git worktrees" (`jj workspace add --[no-]colocate`). The draft does not claim this, which is correct. The entry should still mark it as out of scope: once the host moves to 0.46, jj will create **git worktrees**, which is a new population for the absent-worktree `metadata-prune` path. That upgrade decision is tsukuroi's (§4).

## 2. Counterexamples: claims contradicted by landed code or measured state (calibration, coverage)

**K1 — Operating rule 5 and Limits ¶4 contradict landed ddb7347.**
- Draft :92 says: add `--glob=refs/jj/keep/*`; "Hidden rewritten predecessors that touched the target also refuse". Draft :101 says "no fixture … proves it".
- Landed code (`git show ddb7347:tools/souji-verify.sh`, `:63-76` comment and `:241-255` `jj_keep_novel`): a keep-only commit refuses only when its object at `<rel>` is absent from `rev-list --objects --remotes -- <rel>`. "Deletions and metaedit/rebase predecessors carrying an already-pushed blob do not refuse". The probe is gated on `refs/jj/keep/`.
- The same function is at `souji-vault-verify.sh:433`, and at `souji-quarantine.sh:977` with call sites `:341,1017,1341`.
- The rule as drafted describes the rejected design: a broad refusal on any touching predecessor.
- Fixture: `tests/fixtures/r17-jj-receipts.sh` is committed (769 lines in ddb7347).
- **Fix:** rewrite rule 5 to the landed novelty rule, citing `tools/souji-verify.sh:241-255@ddb7347`. Delete "proposed, not yet landed" and Limits ¶4.

**K2 — §6 misattributes the dirty=0 measurement.**
- Draft :53 says "the census … did not count intent-to-add ` A` entries; the auto-tracked clone reported `dirty=0`", citing JjTrialSouji.md:62 and :80.
- The 152 auto-tracked files were all under `census/operator-sweep-20261019/` (JjTrialSouji.md:29). The census status call **pathspec-excludes** `census/operator-sweep-*`, both at the trial snapshot (`git show cbf688a:tools/souji-census.sh` :949-953) and at ddb7347 (:1115-1122).
- The count is `printf '%s\n' "$st" | grep -c .`, which counts every porcelain line, including ` A` (ddb7347 census.sh:1127).
- dirty=0 is therefore explained by the operator-sweep exclusion, not by blindness to intent-to-add entries. JjTrial itself only said "apparently" (:62).
- **Fix:** drop the claim. If needed, replace it with: "auto-track all() staged 152 intent-to-add entries in a single sandbox (JjTrial:29-31); the census exclusion of `census/operator-sweep-*` hid them".

**K3 — §4 consequence cites a correct `unpushed=0` as if it were a false negative.**
- JjTrialSouji.md:59 is the colocated lane **after** a helper commit and push (step 4: `ahead=0`, remote tip = pushed hash, :46, :51). `unpushed=0` there is true.
- The only keep-only false negative is JjAuditSouji.md:97-104 (sandbox), plus the committed fixture J1/J9 and the live souji keep-only commits (ScoutKeepOnlySouji §5).
- **Fix:** cite J1/J9 and JjAudit F2, not JjTrial:59.

**K4 — Operating rule 4 vs code.**
- The rule says "Do not use `--all`, `--not --all`". ddb7347 still has `log --oneline "$head" --not --all` at `souji-verify.sh:390` and `souji-vault-verify.sh:568`. L1 calls these dead, shadowed sites.
- A knowledge rule that the governed tools visibly break is a provenance trap for the next reader.
- **Fix:** add "(dead sites at verify:390 and vault:568 are shadowed by the `--exclude='refs/jj/'` roots at :854 and :1061)", or have the code remove them.

## 3. Miscalibrated claims (label stronger or weaker than the evidence)

| § | draft claim | defect | evidence | correction |
|---|---|---|---|---|
| §1:15 | "Colocated concurrency is untested" | over-generalised | The quote sits under "Syncing with rsync, NFS, Dropbox, etc" and is about multi-computer sync, especially colocated (concurrency page, identical in both versions) | "Sharing a colocated repo through rsync/NFS/Dropbox is not thoroughly tested", or drop it (no planned S-row, §4) |
| §10:75 | "jj does not garbage-collect its own store yet" | adopts a stale doc sentence | v0.45.1 cli-reference: "Run backend-dependent garbage collection." and "older than 2 weeks are pruned"; CHANGELOG §0.14.0 (SrcJjKeepRefs.md:33,77) | "`jj util gc` (manual; default 2-week expiry) deletes keep refs outside the operation-log head set, then runs git gc (`git_backend.rs:900,1558@v0.45.1`)" |
| §3:27-28 + Limits :98 | keep refs only for "commits created by jj"; retention "not documented … [INFERENCE]" | under-claims, now answerable | Import also writes keep refs (`git_backend.rs:493-498@v0.45.1`). Holder semantics: architecture.md:78-80. Removal: only `jj util gc`. Planned S054 covers this | Upgrade to sourced. The residual gap (exact moment a specific hidden commit's ref disappears) stays a limit (SrcJjKeepRefs.md:24) |
| §2:22 | `@-` is "[INFERENCE] … the jj model" | under-claims | git-compatibility (0.45.1 and 0.46): "Convince jj to update .git/HEAD to point to the working-copy commit's parent" | Sourced, by S051 |
| §7:58,100 | nested `.git` is "observed only" from one sandbox; submodules as "analogue" | under-claims; the submodule analogue also misleads | CHANGELOG 0.36.0 :1268@v0.45.1 + `RESERVED_DIR_NAMES` presence check (an empty dir suffices). Live: 4 of 6 souji keep-only commits carry the p6repo phantom deletions (ScoutKeepOnlySouji.md:1,55-58,72) | Cite S056 and the source. Drop the submodule analogue (tracker shows a gitlink `.git` file also triggers it, SrcJjNestedRepo.md:67) |
| §9:70 | "a later jj or git gc can make the evidence unreplayable" | mechanism wrong | git gc cannot prune a keep-ref'd commit. Loss requires `jj util gc` (or op abandon) to drop the ref first | "after `jj util gc` drops its keep ref, git gc may prune it" |
| §2:23 | "(§6)" | wrong cross-reference | measured_commit is §9 | §9 |
| Limits :99 | "None is in a committed fixture" | stale | `tests/fixtures/r17-jj-receipts.sh` committed at ddb7347. J9 runs real jj; the record header `JJ /home/vgpnk/.local/bin/jj jj 0.45.1-7c41cdeb…` binds tool sha256s equal to the ddb7347 blobs (92743004…, bbca35a1…, 24c7cf05…) | Cite the fixture. **Caveat:** J1–J8 synthesise keep refs with `git update-ref`, so they prove the tools' behaviour, not jj's. Only J9 shows jj behaviour, from one host and one version |

**Evidence-binding defects behind the fixture claim:**
- (a) `census/round-17/jj-receipts-{base5fa6017,ddb7347}.txt` are **untracked**. `git ls-tree -r --name-only ddb7347 census/round-17/` lists only 5 files: gate-replays-expected.json, gate-replays.py, run-matrix.py, seat-audit-replay.py, transcript-manifest.py. The wave context calls them landed records; they are not.
- (b) The per-case J9 detail prints `jj=jj`, because `${JJ_VERSION%% *}` keeps the first word (fixture :735, :748). Only the header line (:227) carries the version.
- **Smallest fix:** commit the records with the round, and change both to `${JJ_VERSION#jj }`.

## 4. Classification: one sandbox, docs silent, other domains

**Rests on one sandbox only (jj 0.45.1, git 2.56.0, one host).** Admissible only as `observed (single sandbox)` and never as a rule basis on its own:
- §4 index reset on jj mutation. The docs say only "staging area will be ignored"; reset-on-mutation is **not stated** (SrcJjGitCompat.md:1). Two sandboxes saw it (JjAudit F4, JjTrial :79), both on the same host and version.
- §6 152-file auto-track count (JjTrial:29-31).
- §8 helper move failure. Observed against helper **v1** (JjAudit:57 cites `jj-lane.sh:191-199,230`); today's helper is a different revision (sha256 `3369dc27…`, last commit 14df5b9). That observation is history, not current behaviour.
- §11 hook/filter/eol bypass (JjAudit:172). It is doc-corroborated ("Hooks: No", ".gitattributes: No"), so it is admissible as sourced, with the observation as corroboration.
- §2 HEAD attach-then-detach after the helper's init (JjTrial:23,48). The init half is helper behaviour.

**Docs silent (must be labelled `not stated`, or carried by source/CHANGELOG rows):**
- Branch mapping: git-compatibility § Branches is literally "TODO: Describe how branches are mapped" (both versions). The bookmarks page carries it.
- Index reset on jj mutation.
- Exact retention timing of a specific keep ref.
- Nested `.git`: the guide pages are silent; CHANGELOG 0.36.0 and the source speak.
- Whether `--exclude='refs/jj/'` covers every jj namespace. Source-answered: keep/, remote-tags/, root (git.rs:94,96; git_backend.rs:100 @v0.45.1).

**Cited sources with no planned S-row (S051–S063):**
- docs `git-comparison` (§3:28) and `technical/concurrency` (§1:15).
- The three own-work rows (JjAudit, JjTrial, helper source).

CORPUS.md:163-165 requires the `source:` line to cite its S### row. Either add rows or drop the claims; the minimal version in §5 drops them.

**Belongs to other domains (point to them, do not assert them here):**
- **Fleet helper (hyaku, `scripts/hyaku/jj-lane.sh`, outside the lane):**
  - all of §8;
  - §7 "The helper refuses this shape";
  - §6 rule "set `snapshot.auto-track = none()` on every colocated lane". The helper's init sets it (JjTrial:22), so it is a helper/fleet policy;
  - JjTrial hazards 6 and 8 (`cp -a` repo identity, working-copy author);
  - operating rule 2's helper mandate.
  
  The draft also pins helper line numbers (`:544-549`, `:618-619`) in a mutable file outside the lane, and the observed failure came from a different revision. I confirmed today's lines read "Deleted or renamed-away path present in the branch tip: include it" and "Phantom deletion: refuse a committed deletion…". Souji may state only the consumer contract: a quarantine move must land as one commit containing both paths, verified by `git show --name-status <pushed>`.
- **tsukuroi host tooling:**
  - the jj binary, its version and channel (`~/.local/bin/jj`);
  - any 0.45.1 → 0.46 upgrade, which changes colocation semantics (workspace colocation creates git worktrees);
  - the `verified-at` host pin.

  The entry should record "observed on host jj 0.45.1-7c41cdeb" and leave upgrade gating to tsukuroi.
- **Souji's own (keep):** receipt roots, keep-ref novelty, HEAD-pin evidence, the census dirty/unpushed semantics, and Q7 `maintenance.auto=false`. Q7 is confirmed at `git show ddb7347:corpus/QUALITY.md:31`.

## 5. Minimal admissible version — claim list

Scope line: *jj 0.45.1-7c41cdeb on this host, git 2.56.0. Docs are cited at `/v0.45.1/`, source and CHANGELOG at tag `v0.45.1`. 0.46.0 is out of scope.*

| # | claim | label | anchor |
|---|---|---|---|
| 1 | `jj git init`/`clone` colocate by default; import/export run on every jj command; mixing jj and git is allowed | sourced | S051 git-compatibility § Colocated |
| 2 | jj usually leaves git HEAD detached, at the working-copy commit's parent (`@-`); there is no current bookmark | sourced | S051 (detached HEAD + "update .git/HEAD to point to the working-copy commit's parent"); S055 bookmarks |
| 3 | jj ignores git's staging area. Index answers (`ls-files`, `git add` staging) are not a stable signal across jj calls | sourced (ignore) + observed single sandbox (reset) | S051; JjAudit F4 as observation only |
| 4 | jj writes `refs/jj/keep/<id>` for operation-log heads, including imported commits; its other `refs/jj/` names are `remote-tags/` and `root` | sourced (code) | S054 `git_backend.rs:100,493-498`, `git.rs:94,96` @v0.45.1; architecture.md:78-80 |
| 5 | Only manual `jj util gc` removes keep refs (default 2-week expiry), then runs git gc. Exact per-commit timing is not stated | sourced + limit | S054 `git_backend.rs:900,1558`; cli-reference v0.45.1 |
| 6 | `git rev-list --all` includes every `refs/*` and HEAD, so `<head> --not --all` is empty for a keep-only head | sourced (git) + fixture | S060; r17-jj-receipts J3/J9 |
| 7 | Bookmarks map to branches; an unbookmarked jj commit is invisible to `--branches --not --remotes` | sourced + fixture | S055; J1/J9 (J9 = real jj 0.45.1) |
| 8 | Receipt roots exclude `refs/jj/` (`for-each-ref --exclude='refs/jj/'`); other refs (stash, original) stay roots | landed rule | `souji-verify.sh:854`, `vault:1061`, `quarantine:1155` @ddb7347; S058/S060 |
| 9 | A keep-only commit touching the target refuses only if its blob is absent from pushed history. Deletions and already-pushed predecessors do not refuse; plain repos run nothing new | landed rule + fixture | `jj_keep_novel` verify:241-255 @ddb7347; J1–J8 (git-emulated), J6 byte-identity, J9 (real jj) — **records must be committed first** |
| 10 | Any directory containing a `.git` or `.jj` entry (an empty dir suffices) is skipped by the jj snapshot; tracked files beneath report `D` and can be committed as deletions | sourced (CHANGELOG + code) + live observation | S056 CHANGELOG:1268, `local_working_copy.rs:821,1637-1640` @v0.45.1; ScoutKeepOnlySouji (4 live keep-only commits) |
| 11 | `snapshot.auto-track` defaults to tracking all new non-ignored files | sourced | S053 config, S052 working-copy |
| 12 | jj does not run git hooks or apply `.gitattributes` (filters/eol), so git-side hooks and attributes do not guard jj writes | sourced + observed | S051 Hooks/.gitattributes; JjAudit F7 |
| 13 | `git gc` is "not tested" with jj; keep `-c maintenance.auto=false` (Q7) | sourced + own rule | S051; S063; QUALITY.md:31 |
| 14 | Evidence must not pin `HEAD` in a colocated lane; it must pin a commit on `refs/heads`, `refs/tags` or `refs/remotes`. Sites: `run-verification.py:384`, `cache-demonstration.py:166` (still `HEAD` at ddb7347) | own rule | git show ddb7347 |

**Pointers, not claims:**
- Helper commit/move contract → hyaku helper docs.
- auto-track `none()` policy and seat provisioning → helper.
- jj version and upgrade → tsukuroi.

**Dropped:**
- §1 "concurrency untested" (miscalibrated, no row).
- git-comparison "visible heads" (no row; superseded by #4/#5).
- §6 ITA/dirty=0 (misattributed, K2).
- §4 JjTrial:59 citation (K3).
- Old rule 5 (K1).
- The submodule analogue.

**`recheck:`**
```
jj --version | grep -q '^jj 0\.45\.1' && curl -fsSL https://docs.jj-vcs.dev/v0.45.1/git-compatibility/ | grep -c 'refs/jj/'
bash tests/fixtures/r17-jj-receipts.sh   # expect SUMMARY failed=0; J9 needs jj
```
On a version mismatch the entry is stale and goes to tsukuroi/L1.

## 6. Verdict

**Fails as drafted. Admissible after correction.**
- The sourced quotes all hold at host 0.45.1.
- The defects are:
  - stale against landed code (K1, K4);
  - two misattributed observations (K2, K3);
  - a stale doc sentence adopted (§10);
  - an over-generalised concurrency claim;
  - under-claims that S054 and S056 now settle;
  - helper and host claims outside souji's domain;
  - uncommitted fixture records.

Smallest safe correction: replace the claim body with the 14-row list in §5, re-anchor the URLs to `/v0.45.1/` and the tags to `@v0.45.1`, commit `census/round-17/jj-receipts-*.txt`, and fix the `jj=jj` field. No tool change is needed beyond that one-line fixture field fix.

## 7. Commands run (all read-only)

```
~/.local/bin/jj --version                       → jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5
curl -fsSL https://docs.jj-vcs.dev/versions.json → v0.46.0 [latest], v0.45.1, v0.45.0 …
curl /latest|/v0.45.1 {technical/concurrency,bookmarks,config,working-copy,git-comparison}/ | grep -nF <quotes>   (table §1)
read https://docs.jj-vcs.dev/{latest,v0.45.1}/git-compatibility/               (diff noted §1)
curl raw.githubusercontent.com/jj-vcs/jj/v0.46.0/CHANGELOG.md (0.46.0 section grep) → workspace colocation via git worktrees
curl raw…/v0.45.1/{lib/src/local_working_copy.rs,lib/src/git_backend.rs,lib/src/git.rs,docs/technical/architecture.md,CHANGELOG.md} | grep  (lines in §1)
curl docs.jj-vcs.dev/v0.45.1/cli-reference/ | grep 'Run backend-dependent…' '2 weeks'  → 9732, 9737
git -C souji-shokunin show ddb7347:tools/souji-{verify,vault-verify,quarantine}.sh | grep jj_keep_novel/--exclude/--not --all ; sed 50-80,241-275,380-395
git show ddb7347:tools/souji-census.sh | sed -n 1108,1130p ; git show cbf688a:tools/souji-census.sh (status pathspec 949-953)
git show ddb7347:tests/fixtures/r17-jj-receipts.sh (24-34,126-140,198-227,705-760)
git show ddb7347:corpus/QUALITY.md (Q7 :31); git show ddb7347:census/round-13/run-verification.py:384, census/round-14/cache-demonstration.py:166
git ls-files --error-unmatch corpus/knowledge/jj-colocation-receipts.md → not tracked; sha256sum/stat of it
git ls-tree -r --name-only ddb7347 census/round-17/ → 5 files, no jj-receipts records
grep '^JJ\t' census/round-17/jj-receipts-ddb7347.txt ; grep J6/J9/SUMMARY both records
git show ddb7347:tools/souji-*.sh | sha256sum → equals record TOOL lines
sed -n 540-552,612-622 scripts/hyaku/jj-lane.sh ; sha256sum it ; git log -1 -- it → 14df5b9
read exact files: JjAuditSouji.md, JjTrialSouji.md, w1/{ScribeSourcesRows,ScribeKnowledgeJj,SrcJjKeepRefs,SrcJjNestedRepo,ScoutKeepOnlySouji}.md (+ first lines of 10 w1 reports); non-recursive listing of w1/
```

Tooling: no install or upgrade. No jj command other than `--version`; no git write; no lane tool run.
