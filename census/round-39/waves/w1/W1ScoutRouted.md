# W1ScoutRouted — r38 spot-check fact sheet (R1-R16)

Seat: W1ScoutRouted. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Source: corpus/lessons/round-38-verifier-spotcheck.md, Routed defects.
Frozen items: census/round-39/c1-items.tsv.
Prereg: census/round-39/preregistration.txt (freeze b769bfb, base ed30b7f5b77939c9073348d810730bc4f355708d).

Axes: quote fidelity, command reproducibility, lane-vs-fleet classification, mapping completeness. No frozen file edited. No git mutation.

Demonstrations use base ed30b7f (r38 tip fcdecaa is an ancestor) or fleet report 6afdd3c6. HEAD at write time was 2201778, worktree dirty. Do not re-run R10/R11 on the worktree tools.

Scratch /fast/scratch/hyaku/souji-r39/W1ScoutRouted was removed after the runs below.

## Mapping gap

The 16 C1 rows are not R1-R16. The prereg says so. The items header still says "one row per routed defect." Items 01-09 are R1-R9, item 10 is R12, items 11-13 split R13, items 14-16 are R14-R16. R10 and R11 have no C1 item; they are C2 (L4 and L1/L2). corpus/lessons/round-39.md at HEAD skips them: R9 at line 65, R12 at line 68.

- R39-C1-03 file census/round-39/records/waves-wait.txt is absent. Lesson gloss: wait for WAVE-DONE and receipt it. It does not edit the fleet filing note.
- R39-C1-04 file census/round-39/records/waves-capture.txt is absent. Spot-check said commit .ufo/waves. The item wants a SUMMARY line (records=, failed=0, uncovered=0). The lesson says census/round-39/waves/, a different path. The frozen item wins.
- census/round-39/cells.tsv is absent, so the C1 register leg has no file.

HEAD already has the anchor for items 01, 02, 05-16 (git grep R39-C1- HEAD). Not re-scored with c1-counter.py.

| routed | item | accused file | item writes | lane or fleet |
|---|---|---|---|---|
| R1 | 01 | fleet report lines 116-127; lesson lines 64, 158, 256 | lesson append | lesson lane; report fleet errata |
| R2 | 02 | fleet report line 7 and waves table | lesson append | report half fleet errata (prereg names R2) |
| R3 | 03 | fleet Filing note | waves-wait.txt (absent) | note stays fleet; item is a new lane receipt |
| R4 | 04 | lane .ufo/waves/round-38 | waves-capture.txt (absent) | lane; item does not commit the waves |
| R5 | 05 | fleet 068f75dc; report ledger row 8 | round-39 lesson | prompt and ledger stay fleet |
| R6 | 06 | lane SKILL.md | SKILL.md | lane |
| R7 | 07 | lane consumers-after files | lesson line; receipts not rewritten | lane |
| R8 | 08 | lane r38 prereg lines 218-220 | appended A10 | lane |
| R9 | 09 | lane r38 prereg rule edit | appended A11 | lane |
| R10 | none | lane souji-worktree-drift.py | C2 L4 | lane |
| R11 | none | lane citation tool; SKILL exit cell | C2 L1/L2; SKILL cell is not a C2 leg | lane |
| R12 | 10 | lane SCORECARD.md | one appended line | lane |
| R13 | 11, 12, 13 | LOG 1855, LOG 1862, QUALITY 209 | three appends | lane |
| R14 | 14 | c1-vacuity2.txt and c1-vacuity5.txt | lesson; vacuity5 has no must-token | lane |
| R15 | 15 | fleet Landed-changes table | lesson lists nine hashes | report half fleet errata (prereg names R15) |
| R16 | 16 | round-36.md line 23 | appended correction | lane |

## R1

Spot-check: report lines 116-127 read "162 to 167", "A times 5", "rows touched none", "44 W04"; the tip measures 162 to 170, 8 rows added (6 mined, 2 rejected, three supersessions), and 47 W04. The lesson stops at "167 to 169" (round-38.md lines 64, 158, 256); S246 appears in no lesson byte.

Command: git show ed30b7f:corpus/SOURCES.md piped to the row grep. Output: 170.
Command: git show ed30b7f:corpus/lessons/round-38.md piped to grep -c S246. Output: 0.

Base lesson line 64: Registry grep count 162 to 167. Line 158: 162 rows to 167 rows and A times 5. Line 256: 167 to 169 (under Gate corrections).

Base status cells: S239-S242, S244, S245 mined; S243, S246 rejected; S244-S246 carry supersedes.

Census on a scratch mirror of the base SOURCES blob (other paths symlinked to the lane), not the dirty worktree:

```
scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin MIRROR
census_rc=0
W04: 47
1 ok
47 W04
```

Fleet report lines 121-127 still say 167, A times 5, 44 W04. Verdict: confirmed. Item 01 anchor is at HEAD line 285. Report sentences stay fleet errata.

## R2

Spot-check: opening line says "4 + 0 dead"; waves table says w1 dead 0 / w2 dead 0; disk shows 42/42 and 31/32 (W2MutBattery absent).

Report line 7: 42 + 32 = 74 seats, 4 + 0 dead. Lines 64-70: both waves "0 dead".

```
w1 md count: 43
w2 md count: 32
w1-spec.json items: 42
extra: W1ScribeReport-fleetroot-draft.md (not in the spec)
W2MutBattery.md mtime: 2026-10-28 14:38:15.662640460 -0300
report 6afdd3c6 committer: 2026-10-28 14:20:17 -0300
```

Spec-matched w1 is 42/42. W2MutBattery exists now, 18 minutes after the report. "31/32" was true at closure and is not true of this disk. The lesson's "14:39" matches w2-results.json (14:39:39), not the seat file. Verdict: report sentence confirmed; current disk is 32/32. Item 02 is HEAD line 287. Report opening is fleet errata.

## R3

Spot-check: Filing note records 11 of 32 at filing and no w2-results.json; at closure 31 on disk (27 written after the report author timestamp). Late findings unintegrated.

Report lines 257-265 say that. Item 03 does not name the report.

```
w2-results.json mtime: 2026-10-28 14:39:39.792142465 -0300
```

W2 report mtimes vs author timestamp 2026-10-28T14:15:01-03:00: 28 after, 4 at or before (W2RevC1, W2RevC2, W2RevC3, W2RevSources). The "27" was not re-derived. Current mtimes, not a filing-time reconstruction. Verdict: filing-note text confirmed; 27-count not confirmed (observed 28). waves-wait.txt still absent.

## R4

Spot-check: .ufo/waves/ is gitignored, so round-38 specs, dispatches, results and seat reports exist only on this host. Commit them.

```
git check-ignore -v round-38 w1-spec.json, w1-results.json, w2/W2MutBattery.md
.gitignore:1:.ufo/waves/   (all three)
git ls-files .ufo/waves/round-38 | wc -l
0
git ls-files .ufo/waves | wc -l
3026
```

Round-38 is untracked. Older wave paths are tracked. Verdict: confirmed for round-38. The item does not ask for that commit. Lane, not fleet. waves-capture.txt absent.

## R5

Spot-check: 068f75dc adds .ufo/prompts/souji-round-38.md under souji-shokunin; ledger row 8 says not repeated, this round committed no .ufo/prompts/ path. Erratum the ledger; leave prompts to the integrator.

```
068f75dc246eb4bde280db1c7e7b547c34fb55e0 souji-shokunin 2026-10-28 13:24:11 -0300
.ufo/prompts/souji-round-38.md | 689 insertions
```

Report line 170 is that "not repeated" sentence. Verdict: confirmed. Item 05 is HEAD lesson line 49. Prompt and ledger stay fleet.

## R6

Spot-check: SKILL.md gains only r38-counter-arms; the other four r38 names are absent (grep count 0).

```
git show ed30b7f:SKILL.md | grep -cE 'r38-(citation-commit|drift-write-envelope|drift-record|drift-mutants)'
0
```

Base line 251 is only r38-counter-arms. Verdict: confirmed at base. HEAD line 283 is the item-06 anchor. Row text at HEAD was not diffed against the must-tokens.

## R7

Spot-check: consumers-after files run --base-tool /fast/scratch/hyaku/souji-r38/final/drift-r36.py. Cite the revision. Blob is 5f0dd45:tools/souji-worktree-drift.py.

```
consumers-after5.txt line 14: python3 -B tests/fixtures/r37-drift-escapes.py --base-tool /fast/scratch/hyaku/souji-r38/final/drift-r36.py
5f0dd45 commit = 5f0dd453ffecb3eca763699e27783b207246a2e9
git cat-file -t of that path = blob
```

after2/3/4/6 name other scratch dirs. Item 07 is a lesson line (5f0dd45, cites-a-revision, must not contain /fast/scratch), not a rewrite of the receipts. Verdict: confirmed.

## R8

Spot-check: prereg lines 218-220 name a7-counter-fixes.txt, not a7-counter-fixes2.txt; r38-counter-arms.py is in neither prereg nor lesson. Append A10.

Base lines 218-220 end at census/round-38/records/a7-counter-fixes.txt.

```
prereg r38-counter-arms: 0
lesson r38-counter-arms: 0
prereg a7-counter-fixes2: 0
```

a7-counter-fixes.txt occurs twice. Verdict: confirmed at base. HEAD line 229 is A10.

## R9

Spot-check: diff 4090ee5..fcdecaa replaces "must be tighter-only." with "is tighter-only unless stated otherwise." Restore by appended amendment.

```
4090ee5 line 121: tighter-only.
fcdecaa line 120: is tighter-only unless
```

Same relaxed sentence at base line 120. Verdict: confirmed. HEAD line 231 is A11.

## R10 — no C1 item

Spot-check: docstring says RECORD-MISSING is "the record path cannot be read", but a missing record prints REFUSAL RECORD-MALFORMED, not a regular file, rc 2.

Base docstring lines 44-46 say that. parse_record: ENOENT raises RECORD-MALFORMED; other OSError raises RECORD-MISSING.

Base blob, not the worktree file:

```
python3 -B drift-base.py --root LANE --record SCRATCH/nope.tsv
rc=2
REFUSAL RECORD-MALFORMED: /fast/scratch/hyaku/souji-r39/W1ScoutRouted/nope.tsv is not a regular file
```

chmod 000 then restored to 644:

```
rc=2
REFUSAL RECORD-MISSING: Errno 13 Permission denied on unreadable.tsv
```

Verdict: confirmed on the base blob. That docstring phrase is absent at HEAD (git grep printed nothing). HEAD tool not re-run. C2 L4, not a C1 row. Lane.

## R11 — no C1 item

Spot-check: every merge-base nonzero collapses to "not an ancestor"; a mistyped rev yields mismatches=20 and rc 1, not exit 2. SKILL exit row never declares the case.

Base: non-40-hex --rev returns 2 USAGE; a 40-hex value is never cat-file -e on REV commit. Receipt ancestry nonzero becomes RECEIPT-REV-NOT-ANCESTOR.

Base SKILL exit cell: 2 usage / malformed register / non-40-hex rev / non-regular or symlinked register.

Base blob, --rev 1dac38dc08e050401d9fc7fe7593334007d9c881 (the tool blob, 40 hex, not a commit), --register census/round-38/cells.tsv (10 rows), --register-rev fcdecaa:

```
rc=1
FILE-ABSENT 10
RECEIPT-REV-NOT-ANCESTOR 10
SUMMARY cells=10 mismatches=20
```

The token not-a-commit is already rc 2, REFUSAL USAGE: --rev must be 40-hex. An absolute register path misses the git path and returns USAGE rc 2; the relative path is the one that hits the bug.

Verdict: confirmed on the base blob. HEAD citation tool has REFUSAL REV-UNRESOLVED at lines 50, 249, 256. Not re-run. C2 L1/L2. The SKILL exit sentence is not a C2 leg. Lane.

## R12

Spot-check: four pointer blocks, three finality labels; last is "Final tip 99efe06", two commits behind the tip, and it drops vacuity and the eight-consumer arms.

Base SCORECARD:

```
line 695 receipt pointer update
line 706 final receipt pointers
line 718 measured-revision block (final)
line 729 filed-state measurement
line 731 Final tip 99efe0676f439309a52f001b71bf0ba2ed8af47f
```

Line 729 names c1-after8, c2-after7, c3-arms-filed. No vacuity, no consumers. Line 718 names c1-vacuity6.txt and consumers-after6.txt.

```
git rev-list --count 99efe06..fcdecaa
2
```

Verdict: confirmed. Item 10 is HEAD line 739. Lane.

## R13

Spot-check: LOG line 1855 cases=9 pass=3 fail=6 (no r37 receipt carries it), LOG line 1862, QUALITY line 209 "(0)" reads fail as the escape count.

Base LOG 1855 contains cases=9 pass=3 fail=6 base_fail=6. Line 1862 says letters still read cells=9 / cases=6 base_fail at least 3 against receipts at cells=11 / cases=9 base_fail=6.

```
c2-before SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9
c2-after  SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9
c1-after  SUMMARY cells=11 mismatches=0
```

git grep of cases=9 pass=3 fail=6 at ed30b7f hit only LOG 1855 and the r37 spot-check quoting it. No r37 receipt.

QUALITY 209 ends c2-before.txt (4 escapes) vs c2-after.txt (0). escapes=9 on both arms; fail=0 is the after failure count. Verdict: confirmed. Items 11-13 at HEAD LOG 1875, 1877, QUALITY 222. Lane.

## R14

Spot-check: vacuity2 says row 1 token was replaced by mismatches=99, but mismatches=9 needs all three rows (R38-C1-1/7/10), three classes each; one row would be mismatches=3. vacuity5 names no operation.

vacuity2 first line is that sentence. Body mismatches those three ids, three classes each, then SUMMARY cells=10 mismatches=9 rc=1.

vacuity5 is three lines: a comment with no operation, SUMMARY cells=10 mismatches=9, rc=1.

Item 14 is the lesson (HEAD line 289), not an edit of either receipt. No must-token mentions vacuity5. Verdict: confirmed. vacuity5 half has no item token. Lane.

## R15

Spot-check: 9 of 21 commits in ca4369a..fcdecaa are absent from the report (6949319, 78ea25a, f10a3a8, 20eea73, a512efb, 9b9e2f8, cb5737a, be66886, c5050ea), and the last cell is the integration placeholder.

git log --oneline ca4369a..fcdecaa is 21 commits. Counts in 6afdd3c6 report:

```
6949319 0
78ea25a 0
f10a3a8 0
20eea73 0
a512efb 0
9b9e2f8 0
cb5737a 0
be66886 0
c5050ea 0
4090ee5 4
integration placeholder 1
```

Verdict: confirmed. Item 15 is HEAD lesson line 53. Report table stays fleet errata.

## R16

Spot-check: no appended correction for the in-place rewrite of round-36.md line 23; the file is untouched this round.

Base line 23 is the cases=21 pass=21 fail=0 control=STUB-REJECTED command.

```
git diff --numstat ca4369a fcdecaa -- corpus/lessons/round-36.md
```

Empty. Verdict: confirmed. Item 16 is HEAD line 176. Lane.

## Verdict

| check | verdict |
|---|---|
| R1 170 rows, S246=0, lesson 167/169, census rc 0, W04=47 | confirmed |
| R2 "4 + 0 dead"; W2MutBattery after the report | confirmed; disk now 32/32, not 31/32 |
| R3 filing note | text confirmed; "27" not re-derived (observed 28) |
| R4 round-38 untracked | confirmed; older .ufo/waves tracked (3026) |
| R5 068f75dc and ledger row 8 | confirmed |
| R6 four names absent at base SKILL.md | confirmed |
| R7 scratch path; 5f0dd45 is a blob | confirmed |
| R8 a7-counter-fixes.txt; counter-arms count 0 | confirmed |
| R9 tighter-only rewritten in place | confirmed |
| R10 missing path MALFORMED rc 2; EACCES MISSING rc 2 | confirmed on base blob |
| R11 blob --rev rc 1 mismatches=20 | confirmed on base blob |
| R12 Final tip 99efe06 is 2 behind fcdecaa; drops vacuity and consumers | confirmed |
| R13 cases=9 pass=3 fail=6 in no r37 receipt; Q84 (0) vs escapes=9 | confirmed |
| R14 vacuity2 is three rows / 9 mismatches; vacuity5 names no operation | confirmed |
| R15 nine hashes absent; integration placeholder once | confirmed |
| R16 round-36.md numstat empty ca4369a..fcdecaa | confirmed |
| items equal R1-R16 | false |

R10 and R11 close under C2 or they do not close. Items 03 and 04 still need files at the c1-items.tsv paths, not at census/round-39/waves/.
