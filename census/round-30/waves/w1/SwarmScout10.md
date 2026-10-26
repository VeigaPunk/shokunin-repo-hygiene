# SwarmScout10 — jj op-log / keep-ref expiry (round 30, wave 1, scout)

## Status
STATUS: PASS — all four asked quotes located (one is a located NEGATIVE for operation-log.md/FAQ.md, answered from other v0.45.1 docs and source); the abandon -> gc -> prune order measured with real jj 0.45.1 in scratch (5 cases). Two [INFERENCE] items remain unexplained (marked).

## Evidence
- Opened this run (curl to scratch, bytes read): `https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/` + `docs/operation-log.md`, `docs/FAQ.md`, `docs/git-compatibility.md`, `docs/technical/architecture.md`, `cli/src/commands/operation/abandon.rs`, `cli/src/commands/util/gc.rs`, `lib/src/git_backend.rs`, `lib/src/index.rs`, `lib/src/op_store.rs`, `lib/src/simple_op_store.rs`. Line numbers are of those files at tag v0.45.1.
- Negative sweep: `grep -n -i -E "abandon|garbage|\bgc\b|disk|keep|prune|unreachable|reachab"` over `docs/operation-log.md` printed NO lines. Over `docs/FAQ.md` it matched only `jj abandon` (line 31-32, 465-468) and "keep my scratch files" prose; no `op abandon`, `gc`, keep-ref or disk-use statement.
- Tool: `jj --version` = `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`; `git --version` = 2.56.0 (same as the knowledge entry). No install performed.
- Measurement receipt (scratch fixtures only, `JJ_CONFIG=/dev/null`, colocated repos under `/fast/scratch/hyaku/souji-r30/SwarmScout10/`, scratch removed afterwards): `.ufo/waves/round-30/w1/SwarmScout10-keepref-measure.txt` (scripts verbatim plus output). No lane repo touched; no jj/git call outside scratch.
- Revision: lane base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b (not modified; not a claim about lane tooling).

## Findings

### Q1 What an operation holds alive
1. Op log content: "Each operation object contains a snapshot of how the repo looked at the end of the operation. We call this snapshot a "view" object." — `docs/operation-log.md` ("Introduction", first paragraph).
2. The view includes the heads: "as well as the set of heads in the repo, and the current working-copy commit in each workspace" — `docs/operation-log.md` same paragraph.
3. Commits are held in the git store by a ref per op-log commit: "the `GitBackend` stores a ref for each commit in the operation log in the `refs/jj/keep/` namespace" — `docs/technical/architecture.md:78-80`. Docs also say: "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC." — `docs/git-compatibility.md:229`.
4. Predecessors are held through the op history too: "Previous versions of a change (or predecessors) are also discarded if they become unreachable from the operation history." — `cli/src/commands/operation/abandon.rs:40-41`.
5. `operation-log.md` itself says NOTHING about keep refs, abandon or GC (negative sweep above).

### Q2 What `jj op abandon` does to history
6. "It will abandon the specified operation and all its ancestors. The descendants will be reparented onto the root operation." — `abandon.rs:34-35`. It "Abandon[s] operation history": it rewrites op-store pointers only (code `op_walk::reparent_range`, `update_op_heads`, `abandon.rs:108-135`); it does not touch git refs.
7. Abandoned commits are not deleted by abandon: "The abandoned operations, commits, and other unreachable objects can later be garbage collected by using `jj util gc` command." — `abandon.rs:41-43`.
8. Cannot abandon the head operation (`abandon.rs:93-104`, error "Cannot abandon the current operation").
9. Measured: after `op abandon ..@-`, op log shrank from 7 ops to 2 (`Abandoned 5 operations and reparented 1 descendant operations.`) while `git for-each-ref refs/jj/keep` still listed the hidden commit and `git cat-file -t` still printed `commit` (receipt case 1, "after abandon: keepref=1 obj=commit").

### Q3 Are abandoned commits still reachable through the op log?
10. No document states it directly. From 4/6/7: once the op that records them is abandoned, they are "unreachable from the operation history" and become GC candidates. In the other direction, while an op holding them survives they stay held.
11. Measured (case 2 vs case 5, same shape, jj 0.45.1): a working-copy commit `W1` rewritten to `W2` by `jj describe` stays held by its keep ref after `op abandon ..@-` plus `jj util gc --expire now` when the rewrite op is the HEAD op (keep=1, obj=commit). With one more op after the rewrite, the same sequence deletes the keep ref and git prunes the object (keep=0, `git cat-file` fails). [INFERENCE] the surviving head op still records `W2` with predecessor `W1`, so `W1` stays in the index heads that `all_heads_for_gc` returns (`lib/src/index.rs:141-148`); the code read does not show where predecessors live, so this is not proven.
12. Measured contrast (cases 1 and 3): a rewrite of `@-` (`jj describe -r @- ...`) with the rewrite op as HEAD op did NOT keep the old commit: keep ref removed after abandon + `util gc --expire now`. Why the two head-op cases differ is unexplained here [INFERENCE: rewrite of `@` vs `@-`].

### Q4 Garbage collection and disk use statements
13. jj's own data: "There's no garbage collection and repacking of Jujutsu's own data structures yet" — `docs/git-compatibility.md:54-55` (issue 12). Index tables: "There's no garbage collection of unreachable tables yet." — `docs/technical/architecture.md:216`.
14. git gc: "It should be safe to run `git gc` in the Git repo, but it's not tested" — `docs/git-compatibility.md:52-53`.
15. `jj util gc` is described only by its help: "To garbage-collect old operations and the commits/objects referenced by them, run `jj op abandon ..<some old operation>` before `jj util gc`." — `cli/src/commands/util/gc.rs:28-29`; "By default, only obsolete objects and operations older than 2 weeks are pruned." — `gc.rs:34-35`; `--expire` accepts only `now` (`gc.rs:54-58`).
16. Disk use: the only statement is performance, not space: gc is suggested "to speed up the import (that command includes packing the Git refs)" — `docs/git-compatibility.md:145-146`. There is NO statement on disk-use growth or on how fast the op log or keep refs accumulate in `operation-log.md`, `FAQ.md` or `git-compatibility.md` at v0.45.1.
17. Source of the keep-ref deletion rule: `recreate_no_gc_refs` "Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other unreachable and non-head refs." — `lib/src/git_backend.rs:900-901`; `gc` passes `index.all_heads_for_gc()` (`:1558-1564`); a ref not a current head survives only when its LOOSE file mtime is newer than the threshold (`:929-945`), and the comment admits "existing packed ref won't be demoted to loose ref" (`:931`). Then `git gc --prune=@<keep_newer> +0000` runs (`:970-978`). The op store removes op/view files unless "objects created after `keep_newer` will be preserved" — `lib/src/op_store.rs:484-487`.

### Order of events (measured; the "why" parts are [INFERENCE])
18. keep ref disappears only when ALL hold: (a) no surviving operation records the commit as a head/predecessor (needs `jj op abandon ..<old>`; abandon alone changes no git ref, case 1); (b) `jj util gc` runs at the head operation; (c) the ref is not protected by the age guard: a LOOSE keep ref younger than the threshold (default 14 days) survives (case 1, default gc kept it: keep=1), but `--expire now` removes it, and a PACKED keep ref has no mtime guard at all and was deleted by a DEFAULT 14-day `jj util gc` on a ref seconds old (case 4: `git pack-refs --all` then `jj util gc` → keep=0). [INFERENCE] anything that packs refs (`git gc`, auto-maintenance, jj's own `util gc` "packing the Git refs") flips the ref from age-guarded to unguarded; the code read at `:939-946` skips the guard when `loose_ref_path.metadata()` fails, which fits the observation.
19. Object deletion is a SEPARATE later step: the keep-ref delete is `recreate_no_gc_refs`, then `git gc --prune=@<keep_newer>`. After keep-ref delete the commit object was still present in cases 1, 3, 4 (case 1 and 3: `obj=commit`), and gone in cases 2-after-extra-op and 5 (`git cat-file` fails). [INFERENCE, case 1/3] object survived because the commit had been git HEAD and the colocated HEAD reflog ("export from jj" entries, `git reflog show HEAD`) still referenced it; case 5's commit was never HEAD and had no reflog entry. In case 4 `util gc` default prunes only objects older than 14 days, so a fresh object survives by age.
20. `util gc --expire now` run in the same second as the ref write did not prune (case 1 first run); a 2 s sleep was used in later cases. [INFERENCE] git prune is `older than` the timestamp, not `at or before`; not isolated.

### Meaning for a souji receipt that relies on a keep-only commit
(`corpus/knowledge/jj-colocation-receipts.md` §4, Operating rule 5 at line 102; §3 lifetime inference at line 31; Limits line 108.) All [INFERENCE] unless a case number is cited.
21. Rule 5's `jj_keep_novel` only refuses when it can SEE the keep-only commit through `refs/jj/keep/*` (entry §3, §4). If the ref is gone, the commit is invisible to the guard even while its object still sits unreferenced in the store (case 1/3: keep=0, `obj=commit`): the receipt then reads as no keep-only commit touches the target and can return SAFE for a path whose only copy of novel content is that commit. Failure mode is a silently dropped refusal, not a false refusal.
22. If the object has also been pruned (cases 2-extra-op and 5), the novel content is unrecoverable; a receipt `SAFE(pushed)` that was true before is now moot because the commit cannot be inspected at all, and any later quarantine/delete based on it was irreversible.
23. The entry's §3 inference "keeps its keep ref until its operation is abandoned, `jj util gc` runs, and the ref is older than the threshold" is incomplete in two ways measured here: (i) a ref that has been packed is NOT protected by the 14-day age guard (case 4), so a DEFAULT `jj util gc` can delete a seconds-old non-head keep ref once packed; (ii) a rewrite recorded in the head operation keeps the old commit held after abandon (case 2) while a rewrite of `@-` does not (cases 1, 3). The §10 sentence "jj's `util gc` runs `git gc --prune=@<keep_newer>`" is confirmed at `git_backend.rs:977`.
24. Practical receipt rule suggested by the data (not a landed change): treat a keep-held commit as protected only while no `jj op abandon`/`jj util gc` can run on that repo; the lane helper `scripts/hyaku/jj-lane.sh` contains neither (entry Limits line 108, observation not re-checked here), but an operator or other tool running `jj util gc` would drop the guard silently. Rule 6 (never pin HEAD in evidence) is separately reinforced by case 1/3: HEAD reflog kept an object alive after its keep ref was removed, a hold git expires on its own clock (default reflog expiry not measured here).

### Candidate input for C3 (`jj-keep-ref-expiry.md`) — observations only, not edits
- Measured RESULT lines available from the receipt: case 1 (abandon alone keeps ref and object), case 4 (packed ref deleted by default-threshold gc), case 5 vs case 2 (head-op rewrite holds, extra op releases and git prunes), case 1/3 (keep ref gone while object survives via HEAD reflog).
- Unmeasured: reflog expiry timing, non-`now` thresholds (jj only accepts `now`, `gc.rs:57`), multi-workspace, push/fetch effects.

## Attack log
Not an attack item. No counter predicate was tested or found gameable. Note for the L1: C3's fixture must `sleep` >= 1-2 s between the keep-ref write and `jj util gc --expire now` or the git prune step can appear not to run (case 1 first run; 20).

## Deliveries
- `.ufo/waves/round-30/w1/SwarmScout10.md` (this report)
- `.ufo/waves/round-30/w1/SwarmScout10-keepref-measure.txt` (scripts and output of the five scratch cases; `jj-version:` line present)
- Scratch `/fast/scratch/hyaku/souji-r30/SwarmScout10/` removed (`ls` shows 0 matches).
