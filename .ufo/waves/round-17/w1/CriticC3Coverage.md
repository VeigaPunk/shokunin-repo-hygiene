STATUS: DONE — C3 is partly a real coverage gain and partly relabelled receipt-safety work; (b) as specified over-refuses on every live colocated lane; the knowledge entry is inadmissible unless it is grounded in jj source at a tag and an in-lane committed fixture

Seat `SoujiR17-3.CriticC3Coverage` · 2026-10-20 · lane base `5fa6017` (= live HEAD) · static review and read-only git only. No lane tool, fixture, selftest, census or `count-claims.py` was executed (none is `ALLOWED-EXEC` for this seat). No `jj` was run. Nothing was installed or updated.

Axes: **coverage** (judged), plus operability and calibration where C3 affects them.

## 1. Is "jj-colocated repositories as a governed edge class" coverage, or relabelled operability?

Verdict: **partial**. The repository shape is genuinely new. Most of the C3 *diff* is receipt-verdict correctness, and that is safety/operability work.

- **The shape is new and live.**
  - At base, `PROVINCE.md`, `SKILL.md`, `corpus/SOURCES.md` and `corpus/README.md` have zero jj mentions: `git show 5fa6017:<f> | grep -ciE 'jj|jujutsu|coloc'` returned no matches for any of them.
  - The lane itself is now colocated. `stat .jj` shows a directory. `for-each-ref refs/jj` shows 8 refs, all under `refs/jj/keep/`.
  - Three other lanes have keep refs too. `for-each-ref --format=%(refname) refs/jj/keep/` gives kama 22, tameshi 27, mado 39.
  - So this is a new edge class of an existing Work surface (`PROVINCE.md:21`, "`<lane>-shokunin/` for every rostered lane"). It is not a new `## Owns` surface.
- **What actually counts as coverage.** Per `PROVINCE.md:50-52`, a frontier row moves to Core "only with an admitted `corpus/knowledge/` entry and a SKILL rule". `SCORECARD.md:105` adds "Source-row growth is not knowledge growth". So only these parts are coverage:
  - (c), the knowledge entry;
  - (d), the SKILL/PROVINCE rule;
  - a coverage-map row (`corpus/README.md:38-42` holds the F1–F4 table; it has no jj row);
  - new fixture *shapes*.
- **What is not coverage.** (a), (b) and (e) change receipt verdicts. They are operability/safety changes. Counting them as coverage, and *also* as safety evidence, would double-count one diff. Keep them as evidence that the SKILL rule is enforced, not as coverage units.
- **Plan drift (disclose).** `SCORECARD.md` `## Planned` names r17 option (b) "coverage/frontier: F2 size attribution". C3 replaces that with jj. The 2026-10-20 operator directive justifies the change, but the report should state the substitution.

## 2. Which counting command shows coverage moved, and why it cannot certify the move

- **`census/round-14/count-claims.py:19-20,26` is an inventory, not an admission check.** It computes `admitted_knowledge = len(knowledge) - len(held)`. Here `knowledge` is every `corpus/knowledge/*.md` at the revision, and `held` matches only `^## Admission status.*\bHELD\b`.
  - At base, `git ls-tree --name-only 5fa6017 corpus/knowledge/` lists 6 `.md` files. Only `quarantine-same-filesystem-rename.md:51` carries a HELD heading, so the counter would say admitted 5, HELD 1. That matches `SCORECARD.md:13`.
  - **Counterexample:** committing *any* `corpus/knowledge/jj-colocation-receipts.md` without a HELD heading moves the counter to 6. That includes a stub and an entry that fails every Q-row. Even an honest "candidate, pending closure" status heading counts as admitted.
  - So "5→6" is author inventory only. Report it as `admitted_knowledge 6 (author inventory; admission pending closure)`, as r13 did (`corpus/README.md:90-91`, "4→5", admitted by CloseSoujiR13).
  - The entry is still absent from the worktree (`stat corpus/knowledge/jj-colocation-receipts.md` → No such file).
- **Counters that do show movement** (each with its command and revision):
  1. `python3 census/round-14/count-claims.py <landing>`: `admitted_knowledge`, `held_knowledge` and `source_rows`. The tier/status Counter must show the new jj rows.
  2. Coverage-map row: `git show <rev>:corpus/README.md | grep -cE '^\| F[0-9]'` (4 at base), or a Core row naming the entry.
  3. PROVINCE surface: `git show <rev>:PROVINCE.md | grep -ciE 'jj|coloc'` (0 at base). Add it as a Frontier row (e.g. F5) with only the bounded receipt-root rule moved to Core, mirroring r13 F2 (`PROVINCE.md:73-80`, "F2 as a whole stays frontier").
  4. Fixture shapes: the number of distinct committed jj shapes in an in-lane fixture (see §5), each red at base and green when changed.
- **Scope limit for wording.** Calling the whole edge class "governed" overreaches. The following stay ungoverned and must be listed as frontier residue:
  - census `unpushed` column (`souji-census.sh` branch-based; disclosed);
  - `souji-repo-structure.sh` ref/object inflation (JjTrialSouji:57,61: `references.others.count=15`, commits 55 vs 44);
  - `measured_commit` = detached `@-` (JjAuditSouji F5);
  - index ownership / `git mv` (F4);
  - hook/filter/eol bypass (F7);
  - intent-to-add invisibility under auto-track ≠ none (JjTrialSouji hazard 5);
  - lock hygiene (F6).

## 3. Counterexamples against the claimed mechanics

### 3.1 (b) refuses pushed, clean files on every colocated lane (operability harm; affects whether "governed" is honest)

**Live counterexample (read-only git on the lane):**
```
$ git -C souji log --branches --not --remotes --format=%h -- corpus/lessons/round-16-verifier-spotcheck.md | wc -l
0
$ git -C souji log --glob='refs/jj/keep/*' --branches --not --remotes --format=%h -- corpus/lessons/round-16-verifier-spotcheck.md
1e0d8d1 719154d
$ git -C souji cat-file -p 1e0d8d1 / 719154d   (first lines)
tree 8506f3269fa58b6ce686e6b2afc94d04c7ffe187 · parent c46eabf · author Joao Pedro Veiga … · change-id yurlroyqvvttpsvlvokzpwtxyullxoxy
tree 8506f3269fa58b6ce686e6b2afc94d04c7ffe187 · parent c46eabf · author protocol-shokunin … · change-id yurlroyqvvttpsvlvokzpwtxyullxoxy
$ git -C souji diff --stat 719154d 5fa6017
 tests/vault/vadv54-run/p/p6repo/{inner/keep.txt,one.txt} | 2 insertions
```
- The file is on `origin/master` at `5fa6017`. The two keep-only commits are the working-copy commit before and after the helper's `metaedit --update-author` (`scripts/hyaku/jj-lane.sh:596-605`), split into `5fa6017` by `jj commit -- <paths>`.
- So the hidden predecessors come from the **normal helper path**, not only from phantom deletions. Every helper commit stamps `@` before the split. I infer (from helper source plus this one observed commit; not executed) that each helper commit leaves at least one keep-held predecessor touching every committed path.
- **Lifetime.** `recreate_no_gc_refs` keeps a ref for every `index.all_heads_for_gc()` head (`lib/src/git_backend.rs@v0.45.1:1558-1564`, `:900-953`). Hidden commits stay heads until `jj op abandon ..<op>` and then `jj util gc` (`cli/src/commands/util/gc.rs@v0.45.1:28-29`; default expiry 14 days, `:54-55`).
- `jj-lane.sh` contains neither `op abandon` nor `util gc` (my grep of the file, pattern including `op abandon|util gc`, matched neither). So the refusal is effectively permanent in lanes, not transient.

**Fleet exposure.** These are exposure counts, not observed verdicts. Method: read-only `git log --raw --no-abbrev --no-renames --glob=refs/jj/keep/* --not --branches --tags --remotes` per lane, minus paths already refused by the base `--branches --not --remotes` query. Each path is classified by whether any keep-only blob is absent from `git log --raw --remotes` history for that path.

| lane | keep refs | paths newly refused by (b) | of which every keep-only version is already in remote history | deletion-only | keep-only *novel* content |
|---|---:|---:|---:|---:|---:|
| souji | 8 | 3 | 1 | 2 (p6repo phantom) | **0** |
| kama | 22 | 188 | 188 | 0 | **0** |
| tameshi | 27 | 914 | 914 | 0 | **0** |
| mado | 39 | 772 | 772 | 0 | **0** |

- Across the 4 live colocated lanes, (b) adds 1,877 refusable paths (1,875 already-pushed content plus 2 phantom deletions) and **0** true jj-only-content positives.
- A coarser `--name-only` pass gave tameshi 140. The 914 figure counts both sides of renames (`--no-renames`).
- **Byte-identity holds only for plain repos** (no keep refs, so `--glob` adds nothing). On colocated lanes, base `SAFE(pushed)` becomes `NOT-SAFE` for helper-committed files.
- The claim's disclosure ("hidden rewritten predecessors that touched the target also refuse") states the fact. It hides that this covers *every* helper-committed path and has zero live true positives. By the reasoning of Q22 (`corpus/QUALITY.md:56`, "honest disclosure cannot cancel an existing supported-domain contraction"), that is an operability contraction on the jj lanes, not a free safety gain.
- **Smallest safe correction.** Refuse on a keep-only commit `C` touching the target only when `git rev-parse -q --verify C:<rel>` exists **and** that blob/tree is not among the target's blobs in remote history. Remote history means `git log --remotes --format= --raw --no-abbrev -- <rel>`, column 4.
  - Deletions (blob absent) and metaedit/rebase predecessors (identical blob) then do not refuse. Novel content that only jj holds still refuses.
  - Keep the `jj-keep-unpushed` evidence note.
  - If the lane rejects this, it must publish the table above (re-derived at landing) as a measured operability contraction, not a disclosed tradeoff.

### 3.2 (a) is not byte-identical for plain repos, and part of the edited site list is dead code

- **The effective authority is the roots variant.** The `--not --all` sites live in shadowed definitions, and bash binds the *last* definition:
  - `souji-verify.sh` `evaluate_worktree` (worktree :342, base :333) is redefined at :1013 (→ `s18_evaluate_worktree_one` :798); `try_pushed` :228 is redefined at :664.
  - `souji-vault-verify.sh` `evaluate_worktree` :536 is redefined at :1229; `try_pushed` :430 is redefined at :880 (worktree line numbers).
  - So the claimed sites verify :234/:351 and vault :412/:517 are dead. The in-flight vault edits to `--not --all` and to the old `try_pushed` `--glob` change no behaviour.
  - Q19 (`QUALITY.md:43`): "Use the actual effective helper definitions, not a shadowed duplicate." Do not count dead sites. Delete the duplicates, or label them dead.
- **`--all` is wider than the claim states** (`refs/jj/*`, `refs/stash`, `HEAD`). `rev-list-options.adoc@v2.56.0:167-169` says "all the refs in `refs/`, along with `HEAD`". Without `--single-worktree` it also adds every *other* worktree's HEAD: `revision.c@v2.56.0:2846-2853` calls `other_head_refs`, which reads `worktrees/<id>/HEAD` for every registration (`worktree.c:602-624`). `get_linked_worktree` (`worktree.c:152-155`) lists any registration whose `gitdir` file is still readable, which includes one whose directory is gone.
  - So the dead `log <head> --not --all` is vacuous even in plain git: it subtracts the absent registration's own HEAD. This is my inference from source; I did not execute it.
  - The executor's header comment (`souji-verify.sh` worktree +10-11) under-describes `--all` the same way.
- **False provenance in the sandbox evidence.** JjAuditSouji F3 (`:122-128`) offers `git log --oneline HEAD --not --all → (no output)` as the keep-ref mask. That output is empty by definition, because `--all` includes `HEAD`. It is not evidence about keep refs, and the knowledge entry must not cite it. The real exposure is source-evident without a sandbox: the effective `for-each-ref --format='%(objectname)'` with no pattern (verify :809, vault :997, quarantine :1069 at base) lists `refs/jj/keep/*`.
- **Plain-repo verdict change.** The effective roots today are *all* refs. Restricting them to heads/tags/remotes also drops `refs/stash`, `refs/original/*`, `refs/prefetch/*`, `refs/pull/*` and `refs/bisect/*`.
  - Example: `git stash` in a linked worktree (stash parent = HEAD), then delete its directory. Base: SAFE(metadata-prune), which is correct, because the commit stays reachable. Changed: NOT-SAFE.
  - The executor's comment "Repositories without refs/jj produce byte-identical verdicts and evidence" (`souji-verify.sh` worktree header) is therefore false for (a). Either keep `refs/stash` and `refs/original` as roots in plain repos, or add a fixture case and disclose the contraction.

### 3.3 Unsourced jj semantics already in in-flight prose

- `souji-vault-verify.sh` (worktree, r17 note) says "working-copy bookmarks under `refs/jj/bookmarks`". At v0.45.1 the only `refs/jj/` namespaces in source are:
  - `refs/jj/keep/` (`lib/src/git_backend.rs:100`);
  - `refs/jj/remote-tags/` ("temporarily fetched" remote tags) and `refs/jj/root` (unborn placeholder), at `lib/src/git.rs:93-96`.
  - Bookmarks export to `refs/heads`, and remote bookmarks to `refs/remotes/` (`git.rs:91-92`). Drop the `refs/jj/bookmarks` claim or source it.
- "jj stores rewritten/abandoned predecessors under refs/jj/keep" is too narrow. The function behind `refs/jj/keep/` creates one for every commit jj writes (`git_backend.rs:868-871`, "Used for preventing GC of commits we create"). Visible commits get them too: the lane has keep refs on `5fa6017` and `c46eabf`, which are on `master`.

### 3.4 (e) is an untracked fix that can come back

- `tests/vault/vadv54-run/p/p6repo/.git` is already gone (`stat` → No such file). The two paths stay tracked (`git ls-files`).
- The stub came from the harness itself: base `tests/vault/vadv54-harness.sh:176` `mkdir -p "$P/p6repo/.git"`. The in-flight harness diff creates it only around case P6 and removes it with `rmdir` plus an EXIT trap. That is good.
- But the stub's removal is not committed evidence, and an interrupted run between `mkdir` and `rmdir` (e.g. SIGKILL) recreates the hazard.
- The helper refuses phantom deletions only *after* `jj commit` has made the commit (`jj-lane.sh:604`, check at `:618-654`). Each refusal therefore leaves another keep-held phantom-deletion commit, which feeds 3.1.
- The live phantom commits stay keep-held: `0254661`, `1e0d8d1`, `719154d` and `41ab059` all `D p6repo/{one.txt,inner/keep.txt}` (`git show --name-status`), matching the claim's "6 keep-only, 4 phantom".

## 4. What would make `corpus/knowledge/jj-colocation-receipts.md` inadmissible under `corpus/QUALITY.md`

| Q | inadmissible if | grounding available now |
|---|---|---|
| Q1 (:25) | `verified-at:` omits the jj version, or its `recheck:` cannot run on the host version. Seats may not run `jj`, so L1 must record `jj --version`. | JjAuditSouji:20 says jj `0.45.1-7c41cdeb`. `~/.local/bin/jj` is 31,077,192 B, mtime 2026-10-03. Upstream v0.46.0 shipped 2026-10-07 (GitHub releases API). `git_backend.rs` differs between tags (sha256 v0.45.1 `95147270…`, v0.46.0 `8767abb9…`), though `NO_GC_REF_NAMESPACE` (:100) and `recreate_no_gc_refs` (:899/901) are still present. |
| Q2 (:26) | The entry rests on docs. The docs say only "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC." (`docs/git-compatibility.md@v0.45.1:229`) and are silent on lifetime. It must cite source at a tag. | `lib/src/git_backend.rs@v0.45.1:100, 868-871, 900-953, 1558-1564`; `cli/src/commands/util/gc.rs@v0.45.1:28-29, 34-35, 54-57`; `lib/src/git.rs@v0.45.1:91-96`. The claim says "documentation rows". Docs-only rows fail Q2, so source rows are needed. |
| Q3 (:27) | No documented failure case of the deletion mechanism. | `jj util gc` deletes non-head keep refs, then runs `git gc --prune=@<keep_newer>` (`git_backend.rs:900-953, 970-977`). The race comment ("this is still racy on re-import", `:928-937`). `docs/git-compatibility.md@v0.45.1`, "There may still be bugs when interleaving mutating `jj` and `git` commands". |
| Q4/Q16 (:28,:40) | The recheck or fixture is the `/fast/scratch/jj-wave/*` sandbox (JjAuditSouji:22, JjTrialSouji:3), which is not `/var/tmp`, has no trap, and is persistent. | A git-only fixture under `mktemp -d /var/tmp/...` with a trap. It synthesizes `refs/jj/keep/<sha>` with `git update-ref` and needs no jj. |
| Q17 (:41) | Evidence is the fleet-repo reports `.ufo/waves/hyaku/jj-w1/reports/*`. They are not contained in the lane revision, and prose naming a fixture is not a fixture. | A committed in-lane fixture file at the measured revision, resolved by the round Gate. |
| Q23 (:57) | Wording claims jj behaviour from a fixture that only emulates jj's refs with git, or generalizes the n=1 metaedit observation. | Label it "tools' handling of a `refs/jj/keep` namespace (git-emulated)". Keep jj semantics to the source rows plus the dated live read-only observation in §3.1 (change-id `yurlroyq…`), stated as n=1. |
| Q2/Q23 | It cites JjAuditSouji F3 `HEAD --not --all → empty` as keep-ref evidence. | Vacuous; see §3.2. |
| Q12 (:36) | It recommends any keep-ref cleanup (`jj op abandon`/`jj util gc`) without recording residue. | Out of scope unless prescribed. |

Additional overreach risks:
- **jj semantics from one sandbox.** The audit and trial ran one jj version, in one sandbox, at two moments. The live counts already drifted: tameshi keep-only commits were 12 at JjAuditSouji:107 and 13 now.
- **Keep-ref semantics without a source.** The "jj-owned index reset on every mutation" (JjTrial hazard 4 vs JjAudit F4, "snapshot did not reset the staged entry") is contradictory between the two reports. Keep it out of the entry, or source it.
- **"detached HEAD; no `@{u}`".** Sourced: docs `:44-45` and `:146`. Base SKILL has no `@{u}` use, so the SKILL recipe is preventive and should say so.

## 5. Fixture shapes that would show coverage moved

Use one committed fixture, run red at base and green when changed, all git-only, under `/var/tmp` with a trap. Every case must exercise the *effective* functions.

- **J1** Absent-worktree head held only by `refs/jj/keep/<sha>`. Base SAFE(metadata-prune); changed NOT-SAFE.
- **J2** Control: the same head is also on `refs/heads`. SAFE in both arms.
- **J3** Keep-only commit with *novel* target content. Changed refuses.
- **J4** Keep-only commit whose blob equals the pushed blob (metaedit predecessor). This is the precision decision in §3.1: SAFE with the correction, refused without it. Record which.
- **J5** Keep-only phantom deletion of the target. Same decision as J4.
- **J6** Plain repo with no `refs/jj`: full stdout byte-identical between arms.
- **J7** Plain repo, absent-worktree head held only by `refs/stash`. Pins the (a) plain-repo verdict, kept or disclosed.
- **J8** `refs/jj/root` / `refs/jj/remote-tags/*` present, no keep refs. No change.

## 6. Commands run (read-only) and outputs used above

- `git -C <lane> ls-tree --name-only 5fa6017 corpus/knowledge/ …` → 6 `.md` + `obsidian-ledger.tsv`.
- Per-entry `git show 5fa6017:corpus/knowledge/<f>.md | grep -nE '^## |verified-at|recheck|HELD'` → only K5 (`quarantine-same-filesystem-rename.md:51`) is HELD.
- `git show 5fa6017:{PROVINCE,SKILL}.md | grep -nEi 'jj|coloc|@\{u\}|…'`, and `corpus/SOURCES.md | grep -niE 'jj|jujutsu'` → no jj matches. The anchored S-row count gave 50.
- `git -C <lane> rev-list --count --all --not --branches --tags --remotes` → `6`. `for-each-ref refs/jj` → 8 keep refs (listed). `show --name-status` per keep-only commit → 4 with `D p6repo/*`; `1e0d8d1` and `719154d` also `A corpus/lessons/round-16-verifier-spotcheck.md`.
- The §3.1 log, cat-file and diff commands, with outputs as quoted.
- Python (eval kernel, `subprocess` read-only `git log/rev-list/for-each-ref/rev-parse/ls-tree` only) produced the §3.1 table. A first, coarser `--name-only` pass gave souji 3, kama 188, tameshi 140, mado 772.
- `git diff 5fa6017 -- tools/ tests/ …` (in-flight worktree edits, read only): changed `regenerate.py`, `vadv54-harness.sh`, `souji-seat-audit.py`, `souji-vault-verify.sh`, `souji-verify.sh`.
- grep (tool) over exact files: `souji-verify.sh`, `souji-vault-verify.sh`, `souji-quarantine.sh` (function definitions and root queries); `scripts/hyaku/jj-lane.sh` (metaedit :596-605, phantom refusal :618-654; no `op abandon`/`util gc`); `tests/vault/vadv54-harness.sh`.
- Web, read-only:
  - `raw.githubusercontent.com/jj-vcs/jj/v0.45.1/{docs/git-compatibility.md, lib/src/git_backend.rs, lib/src/git.rs, cli/src/commands/util/gc.rs}`; v0.46.0 `git_backend.rs` (sha256 compared); GitHub releases API (v0.46.0 2026-10-07, v0.45.1 2026-09-03).
  - `raw.githubusercontent.com/git/git/v2.56.0/{Documentation/rev-list-options.adoc, revision.c, worktree.c}`.
- Not run: `count-claims.py`, any lane tool, selftest or fixture, `jj`. The vacuity in §3.2 and the generalization in §3.1 are **inferences** from source and one observation, not executions.

## 7. Verdict and smallest fixes

- **C3 as coverage: partial.** It holds once the knowledge entry is admitted by closure, with Q1/Q2/Q3/Q4/Q17/Q23 grounding as in §4, plus a coverage-map or PROVINCE row and J1–J8. "5→6" from `count-claims.py` is author inventory and cannot certify itself.
- **(b): fails its precision premise** on all 4 live colocated lanes: 1,877 newly refusable paths, 0 jj-only-content positives.
  - Fix: add a blob-novelty filter for keep-only commits (§3.1).
  - Otherwise: report the table as an operability contraction for the judge.
- **(a): holds for jj**, but it is not byte-identical for plain repos (stash- and original-held heads), and 4 of the cited sites are dead shadowed code.
  - Fix: keep `refs/stash`/`refs/original` roots, or add J7 and disclose.
  - Count only the effective sites; drop or mark the dead duplicates.
- **Prose:** remove `refs/jj/bookmarks`; describe keep refs as "every jj-written commit", not "abandoned predecessors"; do not cite JjAuditSouji F3's `HEAD --not --all` output.
- **Scope wording:** "bounded receipt-root rule for jj-colocated lanes (Core); jj-colocated repositories otherwise frontier", listing the residue from §2.
