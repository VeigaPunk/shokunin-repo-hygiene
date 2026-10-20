STATUS: DONE — one souji L0 line (round-16) is unanswered; C1-D2 redeems only part of it, C3 touches no L0 decision, and two new L0 lines (sweep-dir disposition, jj-gc policy) plus one append-only status addendum are warranted.

Seat `SoujiR17-3.RevL0Status` · 2026-10-20 · lane `souji-shokunin` · read-only. No lane tool, gate, census, `jj`, or git write was run. Tool installs/updates: none.

## 1. Every `souji |` line in `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md`

Command: `grep -n '^\s*souji\s*|' .ufo/l0-questions.md` → exactly one match.

- **Line 59** (`souji | round-16`), answer **none**. Verbatim:
  > `souji | round-16 | Operator scope call on the census contractions round 16 keeps versus pre-harm a31642d ... (a) git-metadata guards that refuse the whole fleet run (symlinked or hardlinked .git metadata, including a hook or git-new-workdir symlink leaving the gitdir; gitfile/commondir/alternates) plus r16's new `info/attributes` whole-run guard; (b) GIT_CONFIG_GLOBAL/GIT_CONFIG_SYSTEM forced to /dev/null, so global ignore, `status.showUntrackedFiles` and `safe.directory` are not honoured; (c) a bound filter driver skipping status for that repo (dirty=0, status-unverifiable); (d) `~user`/`%(prefix)`/unresolvable config paths degraded to an `error` row; (e) `status --ignore-submodules=all`, which can hide a dirty submodule. Accept each as an intended safety cost, or require it narrowed back toward pre-harm behaviour (e.g. (a) to a per-repo `error` row)? Round 17 will narrow (a) to per-repo rows unless told otherwise.`

Answer-channel check: `grep -n 'L0 ANSWER' .ufo/l0-questions.md` → 2 hits (lines 52, 53), both the planner-taxonomy answers bundled inside the kama r11 and tsukuroi r12 lines. Neither concerns souji. The round-17 prompt (`.ufo/prompts/souji-round-17.md:131-138`) only defines the side channel and carries no ruling. The round-16 closure (`corpus/lessons/round-16-verifier-spotcheck.md`, Routed defect 8) records the item as `Operator (not lane)`, i.e. explicitly open.

Durability: the line landed in fleet commit `273d6a6` (`round-16: souji L0 question`, author `souji-shokunin <souji@shokunin.local>`) and is an ancestor of `origin/master` (tip `6f0828b`). The file is tracked (`git ls-files --error-unmatch .ufo/l0-questions.md`). So the question is durable; only the answer is missing.

## 2. Does C1-D2 change what the open question asks the operator to decide?

**Yes — it consumes part of the question's own default option, and it does not close it.**

The question ends with a forward commitment: *"Round 17 will narrow (a) to per-repo rows unless told otherwise."* C1-D2 (declared) narrows **one** entry of `guard_git_files`, `info/attributes`, to a per-repository `error` row with exit 0 and a stderr `git-metadata-unsupported` line. The other seven entries in the same loop keep whole-run refusal:

- `tools/souji-census.sh:522` (current bytes) iterates `config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates`;
- `:526-532` calls `protected_fail "git-metadata-hardlink"` / `"git-metadata-nonregular"` for each;
- `guard_git_files` is entered under `|| exit 2` at `:790`, `:831`, `:849`, `:873`, `:891`.

Consequence for L0: the answer space of item (a) is now asymmetric. If the operator answers "narrow (a)", seven entries plus the symlink scan are still contrary to the answer; if the operator answers "accept", accepting the severity is no longer uniform because attributes is already degraded. Because the file is append-only and the lane cannot edit line 59, the accurate instrument is a **round-17 status addendum line** (see §5(iii)), not a new question.

D1 also narrows one clause of item (b). With an explicit `--untracked-files=normal`, `status.showUntrackedFiles` can no longer neutralize the census status call: git-status(1) (served "last updated in 2.53.0", re-opened 2026-10-20) documents `-u[<mode>]`/`--untracked-files[=<mode>]` with `normal` = "Show untracked files and directories" and says *"The default can be changed using the `status.showUntrackedFiles` configuration variable"* — the config changes only the default, so the explicit flag wins and the one-line directory collapse is preserved. Item (b)'s other two hazards (global ignore, `safe.directory`) remain live; the GLOBAL/SYSTEM-to-`/dev/null` decision is unchanged.

C1-D2 otherwise does **not** touch items (c), (d), (e): filter-driver handling, config-path degradation, and `--ignore-submodules=all` are unchanged by the declared census diff.

**Precision finding for the same answer space (calibration).** The `status.showUntrackedFiles` false-clean shape is not census-only. Repo-local `status.showUntrackedFiles=no` also hides untracked entries from the dirty predicates that feed receipts in the other tools: those calls pass no untracked mode, and `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` cannot suppress repository-local config. Eight production call sites:

- `tools/souji-verify.sh:322`, `:366`, `:820`;
- `tools/souji-vault-verify.sh:488`, `:532`, `:1008`;
- `tools/souji-quarantine.sh:220`, `:1080` (and selftest sites `:1424`, `:1515`, `:1598`).

Mitigating fact: in `evaluate_repo_root` and `evaluate_worktree` the verdict stays `NOT-SAFE` even when `dirty=0` (`souji-verify.sh:311-330`, `:366-375`; `souji-vault-verify.sh:485-500`, `:532-542`), so this is a false **receipt label** (`none` instead of `dirty`), not a safety inversion. Still, an operator answering (b) should be told the fix class is lane-wide; the census-only D1 would leave those eight production status calls carrying the same shape. Smallest fix: pass `--untracked-files=normal` at those calls, or scope D1 explicitly as census-only in the lesson.

## 3. Does C3 change what the open question asks the operator to decide?

**No.** The r16 question is scoped to census contractions versus `a31642d`. The declared C3 edits are in `souji-verify.sh`, `souji-vault-verify.sh` and `souji-quarantine.sh` (durable-root lists, unpushed-touching refsets) plus knowledge/SKILL text; none of (a)–(e) is rewritten by them.

Two C3 facts are worth recording because they change lane behavior the operator's jj directive authorized, without asking a new decision:

1. **Conservative refusals.** Adding `--glob=refs/jj/keep/*` to the unpushed-touching checks means a hidden rewritten predecessor that touched the target now refuses. That is stricter, aligns with the operator's 2026-10-20 "lanes use jj, colocated" directive, and is disclosed in C3(b). It needs no operator ruling.
2. **Durable-root narrowing is one-way safe.** C3(a) makes an absent worktree head held only by `refs/jj/keep` `NOT-SAFE` instead of `SAFE(metadata-prune)`. If `refs/jj/keep` is later pruned, the tools fail closed. That is the correct direction and needs no ruling.

Residual inconsistency to disclose, not to ask: the census `unpushed` column stays branch-based (C3(e) says so), so in a colocated lane it can report `unpushed=0` for a commit only `refs/jj/keep` holds, while verify/vault now refuse that same shape. The tools disagree on the same question. This is a lane design choice with a disclosed reason (keep refs include hidden predecessors); it does not need an L0 decision.

State note on C3(e): the claimed empty stub `tests/vault/vadv54-run/p/p6repo/.git` is **absent in the live tree at my read** (`stat` → No such file; `p6repo` directory mtime `2026-10-20 13:33`; `git ls-files` still shows the two tracked files `one.txt`, `inner/keep.txt`). The jj trial (`JjTrialSouji.md`, hazard 1) documents the stub as present and reproduces the phantom deletion in a sandbox. If a build step removed it, the removal is untracked and therefore invisible in the round diff and uncommittable as-is; if a test recreates it, the hazard returns silently. Smallest durable fix: a tracked guard (e.g. a fixture assertion that no `p6repo/.git` exists, or a tracked `.jjignore`-safe note), not an untracked `rm`.

## 4. Advice on new L0 questions

### (i) Untracked `census/operator-sweep-20261019/` — **yes, file one line**

Measured at read time:

| item | observed |
|---|---|
| dir | `census/operator-sweep-20261019/`, mtime `2026-10-19 22:46:54 -0300`, 29 entries (excluding `.`/`..`) |
| untracked files | `git ls-files --others --exclude-standard -- census/operator-sweep-20261019 \| wc -l` → **152** |
| size | 4.3M |
| ownership | operator-authored, unopened, untouched (`LOG.md:556`, `:745`) |
| census handling | pathspec-excluded from the dirty count (`tools/souji-census.sh:1039-1041`: `:(exclude,glob)census/operator-sweep-*` and two siblings) |
| sibling | `census/operator-sweep-20261018/` is **tracked** (15 files, 5.3M) |
| ignore coverage | no root `.gitignore` in the lane (`stat .gitignore` → No such file) |

The lane cannot resolve this itself: the content is operator-authored, the census already treats it as out of scope, but `git status` shows it every round, and the r16 closure/lesson routed the disposition to the operator (D8) without an L0 line existing. The disposition is now inconsistent across siblings (one sweep tracked, one not), which is exactly what an operator should settle. Suggested one-line question with options:

- (a) commit the 20261019 sweep as an operator snapshot (and state whether future sweeps are committed);
- (b) leave untracked and add `/census/operator-sweep-*/` to a lane `.gitignore` (the jj trial's recommendation 3) — smallest fix, keeps `git status` informative only about lane-authored work;
- (c) delete/move it out of the lane.

Recommended default if unanswered: (b), because the census already excludes the path and the main hazard is accidental `git add -A` ingestion; but never commit the content without the operator naming it (the lane must not read operator material).

### (ii) Running `jj util gc` on lanes (`refs/jj/keep` growth) — **yes, file one policy line, low urgency**

Evidence that this is a real, currently operator-only decision:

- `refs/jj/keep` exists precisely as GC protection: *"To prevent GC from deleting commits that are still reachable from the operation log, the `GitBackend` stores a ref for each commit in the operation log in the `refs/jj/keep/` namespace"* (`https://docs.jj-vcs.dev/latest/technical/architecture/`, re-opened 2026-10-20).
- The reclaimer is `jj util gc` (`cli/src/commands/util/gc.rs`, main, re-opened 2026-10-20): *"By default, only obsolete objects and operations older than 2 weeks are pruned"*; `--expire` accepts only `now`; its doc comment says *"To garbage-collect old operations and the commits/objects referenced by them, run `jj op abandon ..<some old operation>` before `jj util gc`."* Version caveat: the lane's jj is `0.45.1-7c41cdeb` per the trial; the source read is `main`, so the exact 0.45.1 surface is [INFERENCE] from the matching man-page synopsis (`jj util gc [--expire]`).
- Live scale is small: `.jj` = 344K, one op head, 8 `refs/jj/keep` refs, of which **6 are not ancestors of `master`** (only `5fa6017` and `c46eabf` are). Fleet readings in `JjAuditSouji.md` F2: *"tameshi 12, kama 10, mado 16 (7/12/21 keep refs, zero tags)"*. Nothing is near the 2-week default today (the lane `.jj` directory mtime is 12:29:49 today), so there is no emergency.
- Why a decision is needed at all: no seat and no lane executor may run `jj`; the helper has no gc/abandon path (`grep -n 'gc\b\|abandon\|util ' scripts/hyaku/jj-lane.sh` → no matches). Only the operator can reclaim.
- Why gc is not harmless: once old operations are abandoned/pruned, keep refs no longer protect their commits and the objects become collectable ([INFERENCE] from the architecture statement plus `backend.gc(new_heads, keep_newer)`). Two lane artifacts can then become unreplayable: `census/round-13/run-verification.py:384` and `census/round-14/cache-demonstration.py:166` pin `HEAD` as `measured_commit`, and in a colocated repo `HEAD` is detached `@-` and can be keep-only (JjAudit F5).

Suggested policy question: who may run `jj util gc` (and the prerequisite `jj op abandon`) on colocated lanes; what `--expire`/retention window applies; and is every lane evidence pin required to move to `refs/heads/*` before the first gc. Recommended default: no gc until a lane crosses a stated threshold (e.g. `.jj` > 100M or keep refs > 100); the pins-to-durable-refs precondition is a lane fix the lane can do now without waiting.

### (iii) Anything else — one addendum, no second new question

Append one round-17 status line to the L0 queue (append-only; precedent: tsukuroi r17 `CORRECTION`, kama r1 addendum) so line 59 is not answered against a stale inventory:

1. C1-D2 narrowed **only** `info/attributes`; `config/HEAD/index/packed-refs/commondir/info/exclude/objects/info/alternates` and the symlink scan still abort the run (cites `tools/souji-census.sh:519-532`, `:790/:831/:849/:873/:891`).
2. D1 adds explicit `--untracked-files=normal`, retiring the `status.showUntrackedFiles` clause of (b) at the census call; global ignore and `safe.directory` remain.
3. The same false-clean shape remains in `souji-verify.sh:322/:366/:820`, `souji-vault-verify.sh:488/:532/:1008`, `souji-quarantine.sh:220/:1080`; the operator's ruling on (b) should be read as covering those calls or the lane must state it will sweep them separately.
4. C3 does not alter (a)–(e); the census `unpushed` column stays branch-based by disclosure.

No new L0 question is needed for: the p6repo fixture stub (lane-side; see §3), gate-evidence pinning (D6), carry format (D5), wording (D7), seat-audit transcript reproducibility (D4), or C3's conservative refusal. Those are lane defects, not operator decisions.

## 5. Commands run (exact) and observed output

Lane-relative paths ran with cwd the lane root; fleet-repo queries use an absolute path or `git -C`.

```
grep -n '^\s*souji\s*|' /home/vgpnk/Projects/shokunin/.ufo/l0-questions.md -> 59:souji | round-16 | ...
grep -n 'L0 ANSWER\|operator-sweep\|refs/jj\|jj util gc\|landfill\|colocat' /home/vgpnk/Projects/shokunin/.ufo/l0-questions.md
                                                       -> 52,53 only (kama r11, tsukuroi r12 planner answers)
git -C /home/vgpnk/Projects/shokunin log -S 'souji | round-16' --format='%h %ad %s' -- .ufo/l0-questions.md
                                                       -> 273d6a6 2026-10-20 12:29 round-16: souji L0 question
git log -1 --format='%an <%ae> %h %s' 273d6a6          -> souji-shokunin <souji@shokunin.local> 273d6a6 ...
git merge-base --is-ancestor 273d6a6 origin/master     -> exit 0 ("on origin/master"), tip 6f0828b
sha256sum tools/souji-census.sh                        -> 64a60fd0b0ed4101... (r16 bytes; `git diff --stat` empty at 5fa6017)
grep -n 'guard_git_files' tools/souji-census.sh        -> 519, 790, 831, 849, 873, 891
read tools/souji-census.sh:505-545                 -> loop over 8 metadata paths, hardlink/nonregular -> protected_fail
read tools/souji-census.sh:1025-1055               -> count_dirty status call, no untracked-files mode (declared D1 not landed at read)
grep -n 'status --porcelain' tools/souji-{verify,vault-verify,quarantine,census}.sh
                                                       -> verify 322,366,658,820; vault 488,532,846,1008; quarantine 220,919,1080,1424,1515,1598; census 1037
git for-each-ref --format='%(refname)' refs/jj/keep    -> 8 refs; 6 not ancestors of master
stat -c '%y' .jj; du -sh .jj                           -> 2026-10-20 12:29:49; 344K; op_heads/heads count 1
git ls-files --others --exclude-standard -- census | wc -l -> 301 (152 sweep-20261019, 145 round-16, 4 round-17)
stat -c '%y %s' census/operator-sweep-20261019          -> 2026-10-19 22:46:54, 29 entries (excluding `.`/`..`), 4.3M
git ls-files census/operator-sweep-20261018 | wc -l     -> 15 tracked files (5.3M)
stat .gitignore                                        -> No such file
stat tests/vault/.../p6repo/.git                       -> No such file (p6repo mtime 2026-10-20 13:33)
grep -n 'p6repo\|nested' tools/souji-vault-verify.sh    -> 586-589 nested-metadata gate only; no fixture creator
grep -n 'gc\b\|abandon\|util ' scripts/hyaku/jj-lane.sh -> no matches
```

Documentation re-opened (all read-only, 2026-10-20): `https://git-scm.com/docs/git-status` (`-u` semantics/default); `https://docs.jj-vcs.dev/latest/technical/architecture/` (keep-ref purpose); `https://raw.githubusercontent.com/jj-vcs/jj/main/cli/src/commands/util/gc.rs` (gc semantics and 2-week default). `https://man.archlinux.org/man/jj-util-gc.1.en` failed to fetch (ECONNRESET); its search snippet was used only as a synopsis cross-check, not as evidence.

## 6. Verdict

| question | verdict |
|---|---|
| every `souji \|` line listed | **holds** (one, line 59) |
| operator answer exists | **fails** (none; two `L0 ANSWER` strings belong to other lanes) |
| C1-D2 changes an open decision | **partial** — it redeems the question's stated round-17 default for `info/attributes` only; the remaining seven guards and the symlink scan keep exit 2, so the item stays open and needs a status addendum |
| C3 changes an open decision | **no** — different tools and subject; conservative refusals are consistent with the operator's jj directive; census `unpushed` divergence is disclosed |
| new question for sweep dir | **recommended** |
| new question for `jj util gc` | **recommended, low urgency** (policy + expire + pin preconditions) |
| new question otherwise | **no**; one append-only round-17 status addendum instead |

## 7. Residual risk and verification gaps

- I did not run the census, any gate, or `jj`; all L0 advice is from source bytes, committed history, and documentation. C1/C2/C3 are **declared, not landed** at my read (`tools/souji-census.sh` still `64a60fd0…`, `git diff --stat` empty, `census/round-17/run-matrix.py` present but `tests/fixtures/r17-census-hygiene.py` not yet created) — other seats own build verification and that state may change after this read.
- The jj-gc mechanism is partly [INFERENCE]: gc source read is `main`, lane runs `0.45.1`; I did not execute gc to confirm which keep refs it drops.
- Transcript count discrepancy for C2 (outside L0 scope): the mission text says `/var/tmp/souji-r16/transcripts` holds w1 70 + w2 77, but both that directory and the lane copy at `census/round-16/transcripts/` hold **65 w1 + 79 w2 = 144** files (manifest 144 lines; copied 13:34-13:35 with preserved 11:53 mtimes). The manifest and lane copy are untracked at my read; if C2 claims 70/77 it is off by the measured 65/79.
- `.ufo/l0-questions.md` is live (tsukuroi appended at 13:04, tabi at 13:04); the inventory above is as of this read.
