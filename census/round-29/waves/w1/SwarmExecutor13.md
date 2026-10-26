# SwarmExecutor13 — C1 instrument over lane history (r29 w1)

## Status
STATUS: PASS — `tools/souji-registry-agreement.py` run over the 12 assigned commits and over all 210 revisions of `souji-shokunin`; all six base K1 mismatches are traced to a single introducing commit each with a mechanism, no assigned revision returned rc 2, and the counter is shown to fail on real history (187 revisions rc 1, 0 revisions at mismatches=0).

Contract read first: `census/round-29/records/preregistration.txt` (C1 defines K1 as used-by/cited-by agreement and K2 as the four frozen stale statements, read from `b8cb4b31ce80e2e3314b88e85d40ea9873180804`). Lane base for every measurement below is `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; HEAD read at start was `b8cb4b31ce80e2e3314b88e85d40ea9873180804`.

## Evidence

All commands run read-only with `--root /home/vgpnk/Projects/shokunin/souji-shokunin`; the tool reads only `git cat-file`/`ls-tree` bytes, never the working tree.

1. Revision list (as assigned):
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format=%H -12 691dd29211c53d0ef94fa072394cb9c8a69fe92e
→ 691dd29…fe92e, fec846d…00eb, de478b4…a014, ed270c4…931c, 765fe8b…b8bd, 0c96332…b612,
  3a2a80d…83c4, c973d1a…c1c0, 6cb22dc…4c17, 2706527…8275, 50443f5…f856, e78ac7c…06ba
```

2. Per-commit run, `python3 -B tools/souji-registry-agreement.py --root <lane> --rev <hash> --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804` (delivered verbatim in `deliver-c1-history.tsv`):
```
r28: 691dd29 k1=6 k2=4 | fec846d k1=6 k2=4 | de478b4 k1=6 k2=4 | ed270c4 k1=6 k2=4 | 765fe8b k1=6 k2=4 | 0c96332 k1=5 k2=4
r27: 3a2a80d k1=5 k2=4 | c973d1a k1=5 k2=4 | 6cb22dc k1=5 k2=4
r26: 2706527 k1=5 k2=4 | 50443f5 k1=5 k2=4 | e78ac7c k1=5 k2=4
rc=1 for all twelve.
```
K1 set is identical on all twelve except S215: five `cited-not-in-used-by` (S075, S076, S022, S024, S025) plus, from `765fe8b` onward, `used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md`. The six base mismatches reproduce exactly at base `691dd29` (`SUMMARY k1=6 k2=4 mismatches=10`), and also at the prereg commit `b8cb4b3` (`k1=6 k2=4 mismatches=10`, rc 1).

3. Introduction of each mismatch (`git log -S <id> -- corpus/SOURCES.md` and `-S <id> -- <entry>`):
```
S215 SOURCES.md: 765fe8b only        entry git-auto-maintenance-trigger-set.md: 0833de9 (creation, no S215 ever added)
S075 SOURCES.md: 74f9adb (r18)       entry process-residue-observations.md: 005f3d3 (creation), 1988860
S076 SOURCES.md: 74f9adb (r18)       entry process-residue-observations.md: 005f3d3 (creation), 1988860
S022 SOURCES.md: d7266c5, a211e4d, 6cb22dc, 765fe8b   entry quarantine-origin-record-fields-r24.md: a211e4d (creation)
S024/S025 SOURCES.md: d7266c5        entry quarantine-same-filesystem-rename.md: pre-r12, unchanged
```
Field-level check of the r12 edit (`git show 2a363a0^:corpus/SOURCES.md` vs `2a363a0:corpus/SOURCES.md`): S024/S025 `status` mined→queued and `used-by` `corpus/knowledge/quarantine-same-filesystem-rename.md`→`—`. S215 row first exists at `765fe8b`, whose diff appends it; the entry blob is unchanged in that commit (`git show 765fe8b -- corpus/knowledge/git-auto-maintenance-trigger-set.md` is empty).

4. Could-not-evaluate: none of the 12. Full-history sweep `for h in $(git rev-list --reverse HEAD)` (210 revisions) → `187 rc=1`, `23 rc=2`, `0 rc=0`. Every rc 2 is pre-registry (23 ancestors of `d7266c5`, root `ccbb1326204bbf21034820430e9923cb96ef4c17`), message `COULD-NOT-EVALUATE corpus/SOURCES.md absent at rev`; first rc 1 is `d7266c5e9493a3c78687af68d438c2584f75b3c0` itself. Other rc 2 arms exercised: `--rev 691dd29` → `COULD-NOT-EVALUATE rev must be a full 40-hex revision`; `--rev 000…0` → `COULD-NOT-EVALUATE git cat-file -e … fatal: Not a valid object name`, both rc 2.

5. Historical variation (same sweep): k1 distribution over the 187 evaluable revisions `0:2, 2:43, 4:43, 5:75, 6:10, 7:14`; k2 = 4 on every evaluable revision; revisions with `mismatches=0`: 0.

6. K2 line-anchor behaviour: `git show <rev>:LOG.md | wc -l` → 1741 at `e78ac7c`, 1750 at `765fe8b`, 1767 at base; `SCORECARD.md:23` at `765fe8b` is the C3 pre-report-gate row, not the frozen phrase. Hence at r26/r27 revisions K2 prints `file-missing corpus/lessons/round-28.md:22/:40` and `phrase-moved-or-edited LOG.md:1758` / `SCORECARD.md:23`, and only at base does it print the four intended `uncorrected` lines.

7. Coverage measurement at base (`git show 691dd29:corpus/SOURCES.md`, 13-column split, 139 rows): `usedby_empty=21`, `usedby_no_knowledge_path=50` (all 50 are `corpus/lessons/`-only), `usedby_multi=12`.

## Findings

1. **Six mismatches, four introducing commits, three mechanisms** (locations: `corpus/SOURCES.md` at each rev named):
   - `K1 used-by-no-cite S215` — introduced `765fe8bd602ac679d01e7a0790711485209ab8bd` (r28 C2/assimilation commit). Row appended with `used-by=corpus/knowledge/git-auto-maintenance-trigger-set.md`; that entry's `source:` lines are S128/S129/S130 and it never cites S215. The row text was staged by `.ufo/waves/round-28/w1/SwarmExecutor08.md:24`, which justified used-by only by entry existence; the entry was never updated. Mechanism class: **row appended, entry not updated**.
   - `K1 cited-not-in-used-by S075`, `S076` — introduced `005f3d376e5b421c57c4405be37fb10e7ab49381` (r19, F5 process-residue entry added). The entry's front-matter `source:` line cites S075/S076; both rows' used-by stayed `corpus/lessons/round-18.md`. Mechanism class: **entry added without row update**.
   - `K1 cited-not-in-used-by S022` — introduced `a211e4d1bf6ea592670d16269f34e9f67f33e8b3` (r22 commit that adds `quarantine-origin-record-fields-r24.md`, whose filename says r24). S022 used-by stayed `corpus/knowledge/trash-spec-restorable-quarantine.md`. Mechanism class: **entry added without row update**.
   - `K1 cited-not-in-used-by S024`, `S025` — introduced `2a363a03d880288fa3df38f411c3b7154fba7def` ("round-12: post-review fixes"). The used-by cell was edited from the entry path to `—` (status mined→queued) while the entry kept citing both rows. Mechanism class: **used-by cell edited later**. This is the earliest of the six and the only one created by a repair commit rather than an append.

2. **The counter is evaluable and can pass and fail on real history.** k1=0 on exactly two revisions — `d7266c5` (registry creation) and `de9187e` (r12 after-numbers) — and the first failure is `2a363a0`, i.e. the instrument detects a real regression introduced by a post-review fix. No revision in the whole history reaches `mismatches=0`, because K2 is base-anchored (finding 4). So C1's before/after pair (10→0) is measurable on history, not only on fixtures.

3. **The same defect classes existed and were repaired in earlier rounds, which the new counter scores retroactively.** `S086`–`S088` were appended at `4be24d5` (r19) with used-by naming the F5 entry before the entry cited them: k1=7 on 14 revisions (r19), cleared at `1988860` (r20). `S115` was cited by `count-objects-linked-worktree-garbage.md` at `778747e` (r24) while the row did not list it: k1=6 on 4 revisions, cleared at `315422b` (r24 final, "S115/S123 rows"). Relevant to calibration honesty: the r19 non-author spot-check `12516f7` passed a revision this counter scores k1=7.

4. **K2 is a base-anchored check, not a historical regression detector.** Its frozen anchors (`LOG.md:1758`, `SCORECARD.md:23`) only align at base; on older revisions the classification flips to `phrase-moved-or-edited`/`file-missing` (evidence item 6). This fails closed (it can never report 0 wrongly) but it means a K2 verdict on any revision other than the base is an artefact of file length, and any future insertion above line 1758 of `LOG.md` turns `uncorrected` into a false `phrase-moved-or-edited`.

5. **rc 2 never appears for the twelve assigned commits**; it appears only for the 23 pre-registry revisions, where `corpus/SOURCES.md` does not exist. A history sweep must start at `d7266c5`, or treat rc 2 as "not yet evaluable", never as "no mismatches".

6. **The S215 defect was already documented at base.** `corpus/lessons/round-28-verifier-spotcheck.md:61` at `691dd29` states: "`source:` lines cite S128/S129/S130 and never S215 (`git grep -c S215` → no match). Used-by is one-directional." So base k1=6 contains one openly-reported defect (r28 rejected-honest-stop routed it), and my attribution agrees with it. The sibling r29 repair table `.ufo/waves/round-29/w1/deliver-c1-usedby-changes.tsv` covers the same six rows 1:1 (five used-by extensions, one used-by drop), consistent with these introductions.

7. **Instrument asymmetry at base (measured in evidence item 7):** 50 of 139 rows have used-by paths only under `corpus/lessons/`, and 21 rows have an empty used-by. K1 accepts a lesson path as satisfying `used-by` (its predicate is "exists and names the row id", which a lesson can do), so a row can pass K1 without being tied to any admitted knowledge entry.

## Attack log

No attack action was executed against the lane; these are instrument observations from the history run (data only, no predicate changed).

- **A1 (gameable-to-pass, in-spec):** K1's used-by arm accepts any committed path, including `corpus/lessons/*.md`. An author can clear a `used-by-missing`/`no-cite` mismatch by appending a citation of the row id to a lesson instead of linking the row to the knowledge entry that is supposed to consume it (S075/S076 are exactly this shape at base: lesson-only used-by). Suggested stricter-only amendment for the L1: require at least one `corpus/knowledge/` path in `used-by` for rows whose teaches scope is a knowledge claim — not applied by me.
- **A2 (fails closed, false-fail):** K2's fixed line anchors make a legitimate insertion above `LOG.md:1758` flip `uncorrected` to `phrase-moved-or-edited`, i.e. the repair would be scored as an in-place edit. It cannot be gamed to 0. The r26/r27 classifications in evidence item 6 are live instances of this artefact.
- **A3 (blind spot, not exercised):** a row with `used-by` `—` and no entry citing it is invisible to K1 in both directions; 21 such rows exist at base, but all currently admitted entries' citations mean the visible six are the whole defect set. No counter change proposed.

## Deliveries
- `.ufo/waves/round-29/w1/deliver-c1-history.tsv` — 12 assigned commits, columns `commit, round, k1, k2`.
- `.ufo/waves/round-29/w1/deliver-c1-introduction.tsv` — six mismatches, columns `mismatch, introducing_commit, mechanism`.
- `.ufo/waves/round-29/w1/SwarmExecutor13.md` (this report).

Scope notes: no file outside `.ufo/waves/round-29/w1/` was written; no git/jj mutation, no deletion; read-only `git log/show/rev-parse/cat-file/ls-tree/grep` only. No tools installed or upgraded. Scratch `/var/tmp/souji-r29-SwarmExecutor13/` (sweep table + base SOURCES copy) removed before yield. Not run (parent's gate): the lane's build/lint/test/verification passes.
