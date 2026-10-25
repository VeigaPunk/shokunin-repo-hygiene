# W2Trend — souji r24 wave 2 (FALSIFY): attack on the planned trend verdicts

## Status
STATUS: PASS — I attacked all three planned verdicts against bytes at lane tip `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface` (after-state `778747e`, after-receipts `ca7fc1c`). Two of the planned readings are falsified as worded.
- **expansion**: the "new edge class" has no map row. 0 new map ground is confirmed.
- **quality**: the new entry narrows an *admitted* entry and leaves it unmarked. That is a live `harmed` trigger.
- **discernment**: it cannot be self-graded, and the drafted Q56 cites a lesson that does not exist yet.

Verdicts I would assign: **expansion `unprovable-but-better`**; **quality `harmed` at the tip as landed, `improved (bounded)` after a small append-only fix**; **discernment pending the outside spot-check (expect `improved`)**.

## Evidence
All commands were run from `/home/vgpnk/Projects/shokunin/souji-shokunin` on host `git version 2.56.0`, at the tip unless noted. Tools installed: none. Scratch: none created.

| Command | Output excerpt |
|---|---|
| `git log --oneline a65fac9..master` | f9db218, 1efe406, ce5971c, 778747e, ca7fc1c, c3ca7ad |
| `git diff --stat a65fac9 778747e -- corpus SCORECARD.md PROVINCE.md SKILL.md` | README +30, SOURCES +4, new `count-objects-linked-worktree-garbage.md` +145, `git-repo-structure-readonly.md` +3; **SCORECARD.md, PROVINCE.md, SKILL.md unchanged** (last SCORECARD commit is `94fe809 round-23`) |
| `git diff a65fac9 778747e -- corpus/README.md` | the r24 table has exactly one ground row, `F2 repository size census`. Both other rows are marked "not a ground". There is no `F2-wt`/edge-class row |
| `grep -E 'grounded=' census/round-24/records/c2-{control-base,after}.tsv` | base `grounded=4 mapped=2 dangling=0 mismatches=2`; after `grounded=6 mapped=6 dangling=0 mismatches=0` |
| `git diff a65fac9 778747e -- corpus/knowledge/git-repo-structure-readonly.md` | `+ground: F2 — repository size census (structure census of refs-rooted reachable objects)` was added to an existing entry, plus a Re-verification paragraph. The `verified-at:` line is unchanged: "2026-10-20; host Git 2.55.0" |
| `verify --root . census/round-24/records/{r13-recheck-receipt,c1-after,c2-after,c3-after,gate-check-r24-entry}.tsv` | all five `verify=ok rev=778747eb…` |
| `r13-recheck-receipt.tsv` stdout | `selftest=PASS ids=5/5` on `git version 2.56.0` |
| `sed -n` on `census/round-24/sources/*` (after `sha256sum -c SHA256SUMS`, 6/6 OK) | path.c@v2.56.0 :90 "Not considered garbage for report_linked_checkout_garbage"; :111 `{ 0, 1, 1, "refs" },`; :112 `refs/bisect` and :114 `refs/worktree` are both `{ 0, 1, 0, … }`. path.c@v2.30.0 :123 `{ 0, 1, 1, "refs" },`. count-objects.c :118 `report_linked_checkout_garbage(the_repository);` and :152 `(unsigned long)(size_garbage / 1024));`. git-worktree.1 :140 and :170, git-count-objects.1 :28 match the Gate quotes |
| `MANWIDTH=2000 man git-gc \| grep -oE '…' \| sort -u` (the corrected recheck of `git-grace-periods-and-expire-to.md`) | `2.weeks.ago`, `3.months.ago`, `default is 15 days`, `default is 60 days`, `defaults to 30 days`, `defaults to 90 days`. The same six values the entry recorded on 2.55.0 |
| `curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/builtin/gc.c \| grep -cE 'strategy = geometric_strategy;\|"3\.months\.ago"'` (the recheck of `git-auto-maintenance-prunes-worktrees.md`) | `2` (expected 2) |
| read-only `sha256sum` + `sed -n '16p;24p'` of `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/garbage-false-positive-modes-r26.md` | prefix `2ce3dc3178eecfc0`, which equals ScoutPkgEntries' digest. :16 "1. **Nothing else does.** Four arms, git 2.56.0:"; :24 "2. **So the trigger is exclusively the linked-worktree path**" |
| `grep -nE '^\| S11[23] \|' corpus/SOURCES.md` | :132 S112 is gio(1); :133 S113 is "GLib GIO g_file_trash() method reference". fsck is lane S116 (:136) |
| `awk` kind histogram over SOURCES rows | `code 9, docs 105, community 4, own-work 3, book 1, spec 1`. S037 (`builtin/repo.c@v2.55.0`, r13) was already `code` |
| `git cat-file -e 778747e:<p>` for ProbeLinkedModes.md, ProbeGarbageKinds.md, ScoutPkgEntries.md, c1-after.tsv, size-census-lane.txt | all **NO** at 778747e; all yes at the tip |
| `git cat-file -e master:corpus/lessons/round-24.md` | **NOT tracked at tip** (file absent) |
| `git diff -- corpus/QUALITY.md` (uncommitted working tree, someone else's work) | Q56 drafted; its motivating cell is "`lessons/round-23-verifier-spotcheck.md` routed defect … `lessons/round-24.md` R24-M1" |

## Findings

### Expansion. Verdict: `unprovable-but-better`. Never `improved`, never `harmed`.

1. **The "new edge class F2 linked-worktree garbage" does not exist in the map.**
   - Location: `corpus/README.md` § Round 24 table (appended at :504ff). The only ground row is `F2 repository size census`.
   - The new entry's front matter (`count-objects-linked-worktree-garbage.md:8`) reads `ground: F2 — repository size census`.
   - The r17 precedent that granted `improved` had its own row and a PROVINCE boundary. `round-17-verifier-spotcheck.md:143`: "covers new ground (F1-jj, PROVINCE boundary)". r24 has neither, and PROVINCE.md is unchanged.
   - The r23 closure's reading applies unchanged. `round-23-verifier-spotcheck.md:34`: "LEARNING's `improved` rule requires net entries on ground the map did not hold; F2 remains the same map ground."
   - **0 new map ground: confirmed.** Calling it an "edge class" in the lesson or SCORECARD would be a label with no map row behind it.
2. **`grounded` 4→6 is not 2 new F2 entries.** One of the +2 is a relabel. r24 added a `ground: F2` line to the pre-existing `git-repo-structure-readonly.md:4`. The only new file is `count-objects-linked-worktree-garbage.md`. Any "F2 entries 2→4" or "grounded +2" reported as growth overstates expansion. The honest figure is 3→4 files, with a front-matter normalization disclosed separately.
3. **The debris-census capability is not admitted at the tip.**
   - SCORECARD.md is unchanged since `94fe809` (r23), and its Capabilities table (:63ff) has no count-objects/fsck debris row.
   - If the closing commit adds one, it is distinct from `repository structure census` (r13), which covers refs-rooted reachable metrics.
   - The closure precedents split on whether a capability alone earns `improved`. `round-16-verifier-spotcheck.md:128`: "No knowledge entry or frontier row advanced, so the LEARNING 'improved' predicate is not met". `round-18-verifier-spotcheck.md:139` granted `improved`, but with "F5 is newly observed" and SOURCES 63→78.
   - r24 is shaped like r16/r23, not r18: one domain capability, +4 rows (S120–S123), no new ground, and no frontier row moved into Core (PROVINCE and SKILL unchanged).
4. **"New kind of source" is not available.** `code` rows predate r24 (S037 at r13, 9 code rows in total).
5. **Not `harmed`.**
   - Gate-check receipt: `entries=1 ok=1 … fail=0`, `verify=ok`.
   - I re-read every quote-type Gate ADMIT against the committed snapshots, and all are byte-exact.
   - One residual: item 4's sparse-checkout observation is labelled "uncommitted", yet it is committed at the tip in `ScribeEntry.md:25` (a seat table, not a receipt). The label is stale, not a failed bar. LOW.

### Quality. Verdict: `harmed` at the tip as landed (a fixable defect, not a tradeoff); `improved (bounded)` after the correction below.

6. **The strongest counterexample: an admitted F2 claim is narrowed by r24's own entry and left unmarked.**
   - `repo-size-census-readonly.md` claim 1 (:15-20) says `garbage`/`size-garbage` "are unrecognised files, so a size census that ignores them under-reports disk use."
   - r24's admitted entry shows that, in a healthy linked worktree, `garbage: 1` counts the private gitdir's `refs` **directory**. That is documented structure (S123 § DETAILS), not debris, and it adds 0 bytes.
   - The new entry's census rule (item 7) is precisely to *read past* that count. ProbeGarbageKinds `d38` also shows a directory counted ("counted (`!S_ISREG`); dir adds 0 bytes").
   - So the old claim's "unrecognised files" and "under-reports disk use" are false for those cases.
   - `repo-size-census-readonly.md` has no r24 diff, and the new entry calls the relation "extends" (`count-objects-linked-worktree-garbage.md:120-121`), not narrows.
   - LEARNING.md:34 `harmed` when "an entry is found false or stale and left unmarked". r16 closure precedent (`round-16-verifier-spotcheck.md:129`): "The r15 harm was 'an entry found false and left unmarked'".
7. **A second unmarked staleness in the same entry.**
   - `repo-size-census-readonly.md:53-55` still says the `/var/tmp` write-safety fixture "is still owed".
   - The sequential no-write envelope now exists: `c1-after.tsv` reads `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` with `verify=ok`. Only concurrency remains owed.
   - Claim 3 (`--lost-found` writes) got its first empirical binding from case 7, but the entry does not cite it.
8. **The planned "the new entry supersedes/narrows staged claims" is not the quality observable.**
   - The four staged package files (r25/r26/r27/semantics-r23) were never admitted `corpus/knowledge/` entries. LEARNING.md:34 is "a weaker *entry* is superseded".
   - Narrowing staged candidates is a gate decision, which is discernment.
   - Counting the same rejects under both quality and discernment is double-counting.
9. **The stale-entry re-verification is real.**
   - `r13-recheck-receipt.tsv` reports `verify=ok` with `selftest=PASS ids=5/5` on 2.56.0, using the entry's unchanged `recheck:`.
   - However, `git-repo-structure-readonly.md:2` `verified-at:` still reads "2026-10-20; host Git 2.55.0". The observable "`verified-at` freshness" is not updated in the field a reader checks.
   - Also, the `.out` file committed in 778747e (`petQHu`) and the receipt (`wUrYU8`) are two different runs. Only the receipt is bound.
10. **Cheap headroom left on the table.** The two other 2.55.0-pinned entries (`git-grace-periods-and-expire-to.md`, `git-auto-maintenance-prunes-worktrees.md`) are marked "pending recheck (routed to r17)", so they are not `harmed`. Their own rechecks pass today on 2.56.0 (Evidence rows 7–8: same six values; `2`). These are my seat runs, not receipts, so they do not count as round evidence until the L1 receipts them.

### Discernment. Verdict: pending the outside spot-check. The lane MUST NOT self-grade. Expect `improved` if a non-author re-opens one admit and one reject.

11. **No W2 seat can supply the verdict.** LEARNING.md:45-46: "A subagent the lane dispatched is still the lane." This seat included. My agreements below are a prediction, not the spot-check.
12. **The gate sample survives falsification.**
    - All Gate quote-ADMITs are byte-exact at the cited lines. Two sample admits: path.c@v2.56.0 :111 and :90, and count-objects.c :152.
    - Reject r26: staged :16 "**Nothing else does.**" and :24 "exclusively the linked-worktree path" match the stated reason. Lane S113 is g_file_trash (SOURCES:133), which confirms the pointer defect.
    - The prereg bound "at most 2 admitted, at least 1 rejected" holds. r27 and the r25 matrix are admitted. The r25 headline, r26, semantics-r23 and the provenance cells are rejected.
13. **Slice verdicts are not gate decisions.** `census/round-24/records/slice-verdicts.tsv` holds 7 `accepted`, 1 `unverifiable`, 0 rejected. These are campaign-register ids that its own header flags as "NOT lane registry ids", and none is appended. Counting them as admits or rejects for discernment would be a category error.
14. **Q56 would create a discernment-`harmed` trigger if it lands as drafted.**
    - Q56 is uncommitted. It cites `lessons/round-24.md` R24-M1, which is absent at the tip. LEARNING.md:35 `harmed` when "a criterion is added with no lesson behind it".
    - Q56 also does not come from a gate disagreement: the r23 closure agreed 3/3, and the routed :41 item is a map/prose calibration defect. So it serves calibration, not discernment's "disagreement → criterion" path.

### Low
15. **The after-state is not self-contained.** At `778747e` the new entry cites `.ufo/waves/round-24/w1/{ProbeLinkedModes,ProbeGarbageKinds,ScoutPkgEntries}.md` and `census/round-24/records/c1-after.tsv`, and none of these exists at that rev. They land at `ca7fc1c`/`c3ca7ad`. Every citation resolves at the tip, but anyone reading at 778747e sees dangling pointers.

## Attack log
- **A1 — quality (axes: depth, freshness).** Counterexample: findings 6–7. Smallest safe correction, append-only, before close: add a dated `r24` note under `repo-size-census-readonly.md` claim 1 and the :53-55 bullet. The note states three things:
  - `garbage` also counts directories, and inside a linked worktree it counts private-gitdir structure (`refs`, `refs/bisect`, `refs/worktree`, `info`). Ignoring that sweep is correct; see `knowledge/count-objects-linked-worktree-garbage.md`.
  - The sequential no-write envelope is fenced by `tests/fixtures/r24-size-census.py` (receipt `c1-after.tsv`); concurrency stays owed.
  - Separately, update `git-repo-structure-readonly.md` `verified-at:` to name the 2.56.0 receipt, and keep the 2.55.0 origin text.

  With these appended, I would grade `quality: improved (bounded)`: one stale entry re-verified under a verified receipt, plus one admitted claim narrowed and marked by a code-grounded entry.
- **A2 — expansion (axes: coverage, adjacency).** Counterexample: findings 1–2. Correction: the lesson and SCORECARD must say "F2 same ground; 3→4 entry files; `grounded` +1 new and +1 front-matter normalization". Claim `unprovable-but-better` on the capability path and leave the `improved` question to the closure.
  - Do NOT mint an `F2-wt` row after data. Doing so is the A3 row-split game that w1 ReviewAxesTrend named.
  - If a debris-census capability row is added, its wording must match the exercised boundary (Q23): sequential, synthetic `/var/tmp` cases plus one lane-bound run; no concurrency; no fleet figure.
- **A3 — discernment (axis: calibration).** Counterexample: findings 13–14. Correction:
  - Land Q56 only in the same commit as `corpus/lessons/round-24.md` carrying R24-M1.
  - Exclude slice verdicts from the admit/reject sample.
  - Leave the trend verdict blank (pending) for the non-author closure.
- No predicate, target or case set is proposed for change. A1 to A3 are record/marking defects, all fixable without touching C1/C2/C3 counters.
