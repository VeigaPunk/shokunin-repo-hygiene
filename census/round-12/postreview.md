# r12 post-integration re-derivation

Authors: W2RoundSouji-8.R12PostReviewer (reviewer) and W2RoundSouji-8.R12PostCritic (critic), read-only L2 seats; transcribed verbatim by the L1 (session-scoped `agent://` outputs; this committed copy is the durable form). 2026-10-19. Dispositions: `corpus/lessons/round-12.md` `## Gate`.

## Reviewer

## Post-integration re-derivation (R12PostReviewer): round-12 Gate

**Result: the admits hold on content, but the Gate fails its own checks in four places.** Defects are listed at the end. I wrote nothing in the lane (14 uncommitted paths are the lane's own work). Scratch dirs were removed.

### Table: verdict per item

| # | Item | Verdict | Reason | Evidence |
|---|---|---|---|---|
| 1 | **K1** admit (ART C1) | **Agree** | Every cited line checks against the v2.55.0 tree. The `--auto` path runs without the weekly schedule. The prune is gated by `worktree_prune_condition` and the 3-month index-mtime rule. Q1 ✓, Q2 ✓ (tagged), Q3 ✓ (fixture 2→1; M53 is flagged as unobserved), Q4 ✓ (3× `/var/tmp`, hard-coded root, trap). | `gc.c:162` `"3.months.ago"`; `gc.c:1916-1919` `SCHEDULED \| MANUAL`, `WEEKLY`; `gc.c:1772` `!task->auto_condition(cfg)`; `gc.c:1741-1744` `worktree_prune_condition`; `gc.c:1989` `if (!(strategy.tasks[i].type & type))`; `gc.c:1992` `if (opts->schedule)`; `commit.c:1965` `run_auto_maintenance(the_repository, quiet);`; `run-command.c:1980-1981` `maintenance run --auto`; `worktree.c:954-956` `locked` skip; `worktree.c:~1004` `st.st_mtime <= expire` |
| 2 | **K3** admit (ART C4) | **Agree on content; disagree on Q1/Q2 form** | Quotes and negative claim check out. Q2 fails literally: cites `main @ a74f90d`, not a tag. The `v0.35.0` tag's `dedupe.rs` is byte-identical (same sha), so it is a citation fix, not a content error. Q1 fails for rmlint/jdupes/fdupes: no version in the body, and none installed. | Tag `v0.35.0` and `main` both `dedupe.rs` sha `040f78e35e25f559`. `dedupe.rs:814-849` (non-regular and length skips; `modified_before` bail-out); `dedupe.rs:895-902` doc comment; `main.rs:184-186` default to header timestamp; recheck `1 1 1`; rmlint `WILL NOT DELETE ANY FILES` count 1; jdupes README `:250-252` "immediately before scanning or taking action", `:144` `-Q`, `:152` `-t` TOCTTOU. Grep of `partition()` (`:798` onward): no hash/compare call, only error text at `:809-810`. |
| 3 | **K5** admit (ART C6) | **Agree on behaviour; disagree on Q2/Q4 evidence form** | Behaviour reproduced on this host. Q2's "committed fixture" is not met: the fixture is an uncommitted scratch script; only the one-line recheck is reproducible. Q4 got a `/dev/shm` clause written after this entry surfaced the need (see defect 3). S025 (GNU manual) could not be fetched (gnu.org unreachable), so that quote is unverified. | host `mv --no-copy` → `Invalid cross-device link`, exit 1; my strace shows `renameat2(... RENAME_NOREPLACE) = 0`; recheck device lines `31 /var/tmp`, `57 /tmp`, `33 /dev/shm`; `rm --help` count 2 |
| 4 | **ART C3 reject** (size census) | **Agree with reject; reason premise is stale** | The stated "unresolved, untested write/lock behaviour" is no longer strictly true: a scratch run on 2.55.0 left `.git` unchanged (names, sizes, mtimes), with and without `GIT_OPTIONAL_LOCKS=0`. Lock-taking was not sampled. The reject still holds on grounds that stand regardless: EXPERIMENTAL and "not intended for machine parsing" (S005), and Q2 needs a committed fixture. The ART §9 text is not in this checkout (`fleet-ledger/` absent), so I could not re-read §4/§9. | scratch `before.txt`/`after-olo0.txt` diff empty; no `*.lock` after; S005 row `roff :44` (not refetched) |
| 5 | **Spot-check: ≥2 quotes per K1/K3/K5** | **Agree (done)** | Checked ≥2 per entry (see rows 1–3). | — |
| 6 | **SOURCES S030** (C, rejected) | **Agree** | Quote matches: the page recommends `git gc --aggressive --prune=now` monthly, and offers filter-branch. Tier C is right for an undated community blog. | onenine.com: "running git gc --aggressive --prune=now on a monthly basis helps…" |
| 7 | **SOURCES S032** (A, rejected) | **Agree** | Installed man page WARNING matches: "plethora of pitfalls… its use is not recommended" (roff ~:46). Refusal grounded at `PROVINCE.md:28` ("Git history rewrite in any repo"). | `zcat git-filter-branch.1.gz`; PROVINCE.md:28 |
| 8 | **SOURCES S029** (B, mined) | **Agree** | Quote matches exactly: "Common choices of soft deletion delays are 15, 30, 45, or 60 days." | sre.google/sre-book/data-integrity |
| 9 | **SOURCES S014** (B, community, queued) | **Agree** | Quote and date match (2026-02-02). Minor: row says "a Git contributor"; the page attributes it to GitLab; author not checked. | gitlab.com/blog/whats-new-in-git-2-53-0 |
| 10 | **SOURCES S002** (A, mined) | **Agree** | `--prune=now … increases the risk of corruption` and `gc.worktreePruneExpire → git worktree prune --expire 3.months.ago` both match. | git-scm.com/docs/git-gc |
| 11 | **SOURCES S025** (A, mined) | **Unverified** | gnu.org unreachable at check time (curl 28). | — |
| 12 | **SOURCES S031** (own-work, tier A) | **Disagree (open)** | Tier rules live in `SOURCES-CONTRACT-v1` in fleet-ledger, absent from this checkout, so I cannot confirm A is allowed for own-work. Flag it for contract review. | `SOURCES.md:39` |
| 13 | **C1 counts** | **Agree** | Both counts reproduced. My hand-count was off by one (24 `none` cells, not 23). | see below |
| 14 | **C2 counts** | **Agree** | 5/5 entries have the three headers in the first 3 lines. Baseline was 0. | see below |
| 15 | **C3 counts** | **Disagree** | Claim "0→≥2" is false: the measured value is 1 (line 99 only). | see below |
| 16 | **Mistakes audit** (8 rows, captured-by changed from `none`) | **5 agree, 3 disagree** | See the audit table below. | — |

### Mistakes audit (captured-by changed from `none`)

| Row | Cited criterion | Verdict | Reason |
|---|---|---|---|
| M06 | Q11 | Agree (conditional) | "Runner rejects a schema-variant shard" names the check; no runner here to run it. |
| M10 | Q4 | **Disagree** | Q4's test is `grep -c '/var/tmp' ≥ 1`. A fixture with a `${TMPDIR:-/tmp}` default and any `/var/tmp` mention passes. That is M10's exact before-shape (`tests/runner-23.sh:38`). The quota preflight M10 names is not in Q4. |
| M23 | Q5 | **Disagree** | Q5's test only checks that the Gate names a re-deriver and records agree/disagree. It does not test the "critical role has a second seat" clause, so M23 (32/128 seat failures) passes. |
| M27 | SKILL.md:21 (not a QUALITY criterion) | **Disagree** | Pointer is a pre-r12 prose/tool refusal, not a criterion. Nothing runs it. The +1 in C1 is a relabel, not a new capture. |
| M37 | Q10 | Agree (weak) | Names the class; test is "one grep per surface, recorded", which is process-level and specifies no command. |
| M42 | Q7(b) + `git show --stat` | Agree | Would show the `e20f4fa` sweep in the stat. |
| M45 | Q13 | Agree | `git show --stat` shows root-level debris. |
| M51 | Q7(c) + gate | Agree (gap) | Catches plain `git commit` only if the commit is LOG-recorded. Misses other triggers (K1 Limits: `am`, `fetch`, `merge`, `rebase`). |

### Counting outputs (verbatim)

**C1 (lesson command):**
```
before: 28/52      (census/round-12/mistakes.md)
after:  52/53      (corpus/lessons/round-12.md)
dangling-Q check: (no output)
```

**sources-census.sh:**
```
33
0
A=29 B=3 C=1 
mined=18 queued=13 rejected=2 
(no output from the duplicate-id, enum/tier-inflation, or missing-used-by checks)
```

**C2:**
```
3 corpus/knowledge/dupe-finders-detect-then-act.md
3 corpus/knowledge/git-auto-maintenance-prunes-worktrees.md
3 corpus/knowledge/git-grace-periods-and-expire-to.md
3 corpus/knowledge/quarantine-same-filesystem-rename.md
3 corpus/knowledge/trash-spec-restorable-quarantine.md
```
Baseline (`census/round-12/baseline.txt`): `ls corpus/knowledge/*.md | wc -l` → `0`; `grep -lE "^source:" … | wc -l` → `0`.

**C3:**
```
git_version=git version 2.55.0
id=SOUJI-R12-MAINT-plain-commit-sync case=plain-commit-sync before=2 after=1 expect=1 verdict=PASS
id=SOUJI-R12-MAINT-plain-commit-default case=plain-commit-default before=2 after=1 expect=1 verdict=PASS
id=SOUJI-R12-MAINT-auto-off case=auto-off before=2 after=2 expect=2 verdict=PASS
id=SOUJI-R12-MAINT-locked case=locked before=2 after=2 expect=2 verdict=PASS
id=SOUJI-R12-MAINT-fresh case=fresh before=2 after=2 expect=2 verdict=PASS
id=SOUJI-R12-MAINT-maintenance-auto case=maintenance-auto before=2 after=1 expect=1 verdict=PASS
exit=0
```
`grep -cE 'maintenance\.auto|add -A|pathspec' SKILL.md` → **`1`** (baseline `0`). Claimed `≥2`: not met.

### Defects to fix before commit (ranked)

1. **C3 claim is false.** The lesson/claim says `0→≥2`; the measured value is `0→1`. Either correct the claim or add the second checklist row it describes.
2. **Gate cites a nonexistent file and leaves its check open.** `census/round-12/postreview.md` (lesson lines 113, 129) does not exist. Line 128 says the spot-check is "pending". Q5 needs this table recorded in the Gate (agree/disagree with cause). Line 44 says "After (this file): see the report and LOG r12"; the after-count `52/53` must be written in the lesson itself.
3. **QUALITY Q4 was rewritten after the entry needed it.** The `/dev/shm` clause was added when K5 surfaced the need (lesson admits this). QUALITY's header rule: criteria are "superseded by a new row that names the row it replaces, never rewritten." Fix: split it into a dated new row, or drop the clause and have K5 commit its fixture.
4. **K3 citation form.** Cite `dedupe.rs@v0.35.0:<line>` (content is identical), not `main @ a74f90d`. Add versions for rmlint/jdupes/fdupes (docs-only, none installed) so Q1 holds.
5. **K5 evidence form.** Commit the recheck as a fixture under `tests/fixtures/` (Q2 requires a committed fixture). Re-verify S025 when gnu.org is reachable.
6. **K1 Limits** cites `/var/tmp/souji-r12-verify/`, a scratch dir outside the repo. Move that evidence into `census/round-12/` or drop the claim.
7. **Captured-by criteria that don't catch their class.** M10 (Q4 test too weak), M23 (Q5 test skips the second-seat clause), M27 (not a criterion; pre-existing prose). Tighten the tests or recategorise these rows.
8. **C1 calibration.** M43 is counted "captured" by Q8, but Q8's own check fails today (`grep -c timeout tools/souji-quarantine.sh` → `0`). State in the lesson that C1 counts criterion existence, not enforcement, or recount.
9. **Lesson overstates the change.** "Changed only the captured-by cell of the 24 rows" is slightly off: M25's evidence cell was rewritten (disclosed as escape-fix) and M39's captured text changed. Disclose both.
10. **S031 tier** (own-work at A): confirm against `SOURCES-CONTRACT-v1` (not in this checkout).

### Residual risk and verification gaps

- fleet-ledger (ART §4/§9 and the SOURCES contract) is absent from this checkout. The C3 reject and tier rules could only be judged against the lesson's restatement.
- S025 and K5's GNU manual quotes are unverified (network).
- K1's `git-maintenance.1.txt` line cites and K3's fdupes `-D`/`-I` quotes were not re-opened.
- C3 flip test: I sampled before/after `.git` state only. Transient lock files were not observed; a single small repo was used.

## Critic

## Ranked findings

1. **High — C2 still depends on C3’s gate.**  
   The Gate admits K1 using “Q4 (gate under `/var/tmp`)” (`corpus/lessons/round-12.md:117`), admits S031 as a SOURCES row (`:123`), and S031 is the maintenance-guard fixture/result. K1 also uses that fixture for corroboration. Thus C2’s admitted evidence is not verifiable with C3’s gate absent, despite the independence statement at `:12–14`. C2 does separate from C1’s Q5–Q14; the unresolved dependency is C3.  
   **Axes:** coverage, calibration.  
   **Smallest fix:** Base K1 admission on the reopened Git sources, not Q4’s C3 fixture; keep S031 optional or outside K1/C2’s admission evidence.

2. **High — C1’s 52/53 is a reproducible annotation count, not evidence of effective capture.**  
   I ran the counting logic: **52/53**. But the lesson says the author changed the 24 previously-`none` cells after QUALITY existed (`round-12.md:34–44`), and the count treats any non-`none` pointer as captured. The mappings are often relevant, but some tests do not establish they would catch recurrence: M43 maps to Q8, whose test can be satisfied by a `timeout` elsewhere in the tool; M52 maps to Q10, whose test is only “one grep per surface,” while the current SCORECARD still has the stated drift. The lesson does not record the resulting 52/53; it says “see the report and LOG r12,” but `LOG.md` has no r12 entry. The promised post-integration `census/round-12/postreview.md` is absent, and the Gate still says the spot-check is pending (`round-12.md:128–130`).  
   **Axis:** calibration.  
   **Smallest fix:** Record the exact command, file, and output; label 52/53 as *mapped criteria* rather than demonstrated catches; complete and record the independent inventory/mapping audit. Strengthen Q8’s test to verify the timeout is on the per-target path and exercise a timeout failure.

3. **High — Current-state claims remain stale or contradictory.**  
   `SCORECARD.md:26–40` still plans only through r5; `:50–53` still says r9 defects are reproduced and ties advisory receipts to r10. `LOG.md:349–360` records r11 closed the last r9 defect class, certification still withheld because evidence integrity failed, and the 12-round goal was cancelled. The scoreboard was not changed. In `corpus/README.md`, the active index still says every round lesson has a Gate (`:17–18`) and Known gaps still says there is no census or gate tool (`:22–23`); the appended corrections (`:53–55`) acknowledge those statements are false but do not remove or qualify the active claims.  
   **Axis:** calibration.  
   **Smallest fix:** Update the active README statements and append an r12 LOG amendment; bring Planned and the certification explanation in SCORECARD up to the r11 state, keeping certification **OFF**.

4. **Medium — The new SKILL checklist and gate self-test still have operability gaps.**  
   `SKILL.md:100` gives `git worktree lock --reason "<why>"` without the required worktree operand; the Git synopsis requires `git worktree lock [--reason <string>] <worktree>` ([Git documentation](https://git-scm.com/docs/git-worktree)). The same row’s `grep -c '^locked'` prints `0` but exits 1 when there are no locked registrations; the lane’s current `worktree list --porcelain` has no `locked` record. Separately, `--selftest` in the fixture only prints `selftest=on` and runs the same cases (`:59–62`); it does not assert a separately pinned expected finding ID, as PROTOCOL’s Gate standard requires.  
   **Axis:** operability.  
   **Smallest fix:** Add `<worktree-path>` to the lock command; use a zero-count-safe counter; make self-test assert the pinned IDs as well as the exit/result.

5. **Medium — Corpus count/negative-claim rules are not fully met.**  
   `corpus/README.md:32` gives “33 rows” without its command/date, and the C2 claim in `round-12.md:12–14` gives “5” entries on “three” frontier rows without a count command. The source census itself reproduces 33 rows, malformed rows 0, and the tier/status histograms, but that command/output is not attached to those corpus counts. The F2 “no entry” claim in README `:40` has no bounded absence sweep. SOURCES rule 1’s per-row Gate grounding is present, and rule 2 is consistent with the lesson’s statement that all rows are new and no in-place changes occurred. Rule 5 is mostly satisfied—including a specific S033 sweep—but S013’s “no release since v1.5.0” (`SOURCES.md:21`) has no bounded release/tag sweep recorded.  
   **Axes:** calibration, coverage.  
   **Smallest fix:** Attach command and date to the counts; record bounded sweeps for F2 and S013 or narrow those negative claims.

## Pre-landing critique disposition

- **Fixed:** The fixture now hard-codes `/var/tmp`, enforces `before=2`, prints the Git version, and includes a default-detached case. All six cases passed on each of my **three** runs; no flakiness observed.
- **Fixed in part:** The operational checklist and registry row were added, but the lock invocation and self-test assertion gaps above remain.
- **Not fixed:** C2’s C3 dependency and the stale SCORECARD/README state.
- **Explicitly carried but incomplete:** The Gate labels the non-author spot-check pending; no postreview file is present. C1 therefore is not yet durably re-derived in the lane.

## Claim verdicts

- **C1 — holds-if-fixed.** The 52/53 arithmetic reproduces, but it is self-graded mapping coverage, not demonstrated capture; independent review and durable result evidence remain outstanding.
- **C2 — falsified as declared.** Its admission evidence still includes C3’s fixture.
- **C3 — holds-if-fixed.** The fixture behavior is supported and passed three runs, but the checklist command and stable-ID self-test need correction.

**Axis harm found:** calibration, coverage, and operability. **No elegance harm found:** SKILL.md grew 1,581 bytes (6,985 → 8,566), and the diff is a durable hazard row, pre-quarantine decision rows, and gate registration—not general prose bloat.
