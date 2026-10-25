# SonicReadmeMap — coverage-map row enumeration at the round-26 freeze

Seat: mechanical enumeration (read-only). Frozen revision:
`89e0fceeefcf28db313c94120be6d25e03c60094` (prereg freeze + amendment 1; ancestor of
`master`). No file in the lane was written except this report; no `git` mutation, no
signal, no write outside the lane. Scratch `/var/tmp/souji-r26-SonicReadmeMap/` removed
at exit.

## Status

STATUS: PASS — every coverage-map row at the frozen revision is enumerated below from
committed bytes (12 rows matched by the assigned regex, 21 map rows total across 7
`ground`-headed tables); the F1 row is `:39`, the superseded F2 row is `:40`; the map-side
C2 counter (K4) reconciles to the amended after-literal at the observed tip.

## Evidence

### E1 — size and shape of the frozen blob

```
$ git show 89e0fceeefcf28db313c94120be6d25e03c60094:corpus/README.md | wc -l
558
$ git show 89e0fceeefcf28db313c94120be6d25e03c60094:corpus/README.md | grep -cE '^\|'
40
```

### E2 — the assigned regex, raw output (rev 89e0fce)

Command: `git show 89e0fceeefcf28db313c94120be6d25e03c60094:corpus/README.md | grep -nE '^\| F[0-9]|^\| receipts'`

```
38:| receipts: pushed / moved-to-obsidian / stale | core (SKILL.md, tools/) | `knowledge/obsidian-ledger.tsv` (operator-fed, header-only) |
39:| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md` |
40:| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19); superseded by Round 24 F2 row (:517) | — |
41:| F3 duplicate verdicts | frontier, entry held | `knowledge/dupe-finders-detect-then-act.md` |
42:| F4 restorable quarantine, file-system semantics | frontier; layout held, staging primitive + record read side admitted r22 (see § Round22 attempt 2) | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md`, `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md` |
68:| F2 repository size census | bounded structure-census capability acquired; wider size attribution remains frontier. **r23: the read side now holds three entries** (`git-repo-structure-readonly.md`, `repo-size-census-readonly.md`, `count-objects-garbage-readings-r25.md`); the write-safety fixture and any measurement remain owed (see § Round 23) | `knowledge/git-repo-structure-readonly.md` (S035/S036/S037); `../tools/souji-repo-structure.sh`; `../tests/fixtures/r13-repo-structure.sh`; `../census/round-13/verification.json` |
216:| F1-jj jj-colocated lane repos (edge class of F1) | Core (candidate, admission pending closure): bounded receipt-root rule — durable roots exclude exactly `refs/jj/*`; keep-only novel-content refusal; plain repos byte-identical. F1 itself stays frontier; keep-ref expiry unmeasured | `knowledge/jj-colocation-receipts.md`; `../tests/fixtures/r17-jj-receipts.sh`; `../census/round-17/jj-receipts-base5fa6017.txt`, `../census/round-17/jj-receipts-4f48343.txt` (changed arm 0 failed; r18 correction: was a `ddb7347` record name never committed) |
217:| F2 caveat, disclosed only: colocated repos inflate structure counts versus a plain clone (`references.others.count` 15 from `refs/jj/keep/*`; `objects.commits.count` 55 vs 44, sandbox) — no F2 capability claimed | observed, not claimed | `../../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` step 5; `../../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` F3 |
242:| F5 process residue | frontier (tool + gate, no knowledge entry): own-uid residue listed, never signalled | `../tools/souji-proc-census.sh`; `../tests/fixtures/r18-proc-census.sh`; `../census/round-18/leak-count.py`; `../census/round-18/proc-census-live-1721.tsv` |
274:| F5 process residue | **Core for the observation surface** (outside admission pending): first admitted `knowledge/` entry, list-only, no reap authority | `knowledge/process-residue-observations.md` (S082–S085; S075/S076 rechecked); `../tools/souji-proc-census.sh`; `../tests/fixtures/r18-proc-census.sh` |
517:| F2 repository size census | frontier; read side (three entries, r13/r23) plus a write-safety debris census (r24 C1): `count-objects -v` read against the common git dir so a linked worktree's `garbage: 1` is not reported, `fsck` unreachable count without `--lost-found`, alternates counted; `--lost-found`, promisor/partialClone and non-repositories refused (exit 2). Fixture cases 1-6 assert the common-dir `.git` manifest unchanged across the tool run (case 7 proves the detector sees `fsck --lost-found`, case 8 rejects a stub); a tool that restores directory mtimes after writing is invisible to that manifest; the counter does not cover an `extensions.partialClone`-only repo or bare/subdirectory inputs (the tool refuses or handles them). Formerly: the 8 frozen fixture cases fence the no-write envelope; one lane-bound measurement, no fleet figure | `knowledge/git-repo-structure-readonly.md` (S035–S037); `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118–S119); `knowledge/count-objects-linked-worktree-garbage.md` (r24, assimilated); `../tools/souji-size-census.py`; `../tests/fixtures/r24-size-census.py`; `../census/round-24/size-census-lane.txt` |
544:| F2 repository size census | frontier; five sourced entries now cover the read-side facts, r24 debris counter, and r25 common-directory envelope. C2 refusal fixture: 12/12 (8 inherited plus bare/nonempty, bare/empty, subdirectory, partialClone-only); red on pre-fix 1efe406 is 11/12 (subdirectory), while the actual bare regression at 778747e is 10/12 (bare cases 9–10). Seven of twenty tool-clause mutants survive the 12-case fixture; their survivors are disclosed in `corpus/lessons/round-25.md`. C3 structure fixture: selftest=PASS ids=7/7 (was 5/5), including common-dir and colocated/plain checks. Limits: the r25 fixture checks exit/stderr but not manifest equality on cases 11–12; atime/ctime are excluded; content changes remain detected by hashes, but transient byte-identical writes/deletes with restored directory mtime can escape. No size baseline, deletion authority, or F2 promotion to Core is claimed. | `knowledge/git-repo-structure-readonly.md` (SOURCES S035–S037); `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118–S119); `knowledge/count-objects-linked-worktree-garbage.md` (SOURCES S120–S123); `knowledge/git-repo-structure-common-dir.md` (SOURCES S124–S126); `../tests/fixtures/r24-size-census.py`; `../tests/fixtures/r13-repo-structure.sh`; `../census/round-25/sources/` |
```

12 lines matched. Raw byte lengths of the two long rows: `:517` = 1220 chars, `:544` =
1355 chars.

### E3 — exact line numbers asked for

- F1 row: `corpus/README.md:39` at 89e0fce.
- Superseded F2 row: `corpus/README.md:40` at 89e0fce (self-declares "superseded by Round
  24 F2 row (:517)").

### E4 — every `ground`-headed table and every row in it (rev 89e0fce)

Derived by parsing contiguous `|` blocks and keeping blocks whose first cell is `ground`
(the instrument's own map definition, `tools/souji-coverage-agreement.py:4-8`: first cell
`ground`, third cell begins `entries`). First-cell text is printed as parsed; where a cell
is longer than the display width it is elided at the marked `(` — full row bytes for the
rows also matched by E2 are there verbatim.

```
36  [ground]   <- table 1
38  [receipts: pushed / moved-to-obsidian / stale]
39  [F1 git-native housekeeping vs receipts]
40  [F2 repository size census]
41  [F3 duplicate verdicts]
42  [F4 restorable quarantine, file-system semantics]
66  [ground]   <- table 2
68  [F2 repository size census]
69  [Certification evidence integrity]
70  [Quarantine operation bounds]
214 [ground]   <- table 3
216 [F1-jj jj-colocated lane repos (edge class of F1)]
217 [F2 caveat, disclosed only: colocated repos inflate structure counts versus a plain clone (
238 [ground]   <- table 4
240 [Bounded census reads (Core census surface; not F2)]
241 [Evidence-pointer integrity (calibration of authority files)]
242 [F5 process residue]
272 [ground]   <- table 5
274 [F5 process residue]
275 [Carry truncation (landing gate)]
276 [Durable revision stamps]
277 [Seat-audit authorized shapes]
515 [ground]   <- table 6
517 [F2 repository size census]
518 [Coverage-map agreement (calibration of this file; not a ground)]
519 [Receipt verify/run symmetry (r23 residuals)]
542 [ground]   <- table 7
544 [F2 repository size census]
```

21 map rows in 7 tables. Composition: 1 `receipts` row, 11 F-rows (F1×2 at `:39`,`:216`;
F2×5 at `:40`,`:68`,`:217`,`:517`,`:544`; F3×1 at `:41`; F4×1 at `:42`; F5×2 at
`:242`,`:274`), 9 non-F rows (`:69`,`:70`,`:240`,`:241`,`:275`,`:276`,`:277`,`:518`,
`:519`).

### E5 — grounded-entry census at 89e0fce and where each is mapped

`for f in $(git ls-tree --name-only 89e0fce corpus/knowledge/ | grep -v '\.tsv$'); do git show 89e0fce:$f | grep -m1 -E '^ground:' ...; done` plus a per-name line locator in the README:

| knowledge entry | ground @89e0fce | cited by README line(s) (every match, not only map rows) |
|---|---|---|
| `count-objects-garbage-readings-r25.md` | F2 | 68, 480, 517, 544 |
| `count-objects-linked-worktree-garbage.md` | F2 | 517, 544 |
| `git-repo-structure-common-dir.md` | F2 | 544 |
| `git-repo-structure-readonly.md` | F2 | 68, 517, 525, 544 |
| `repo-size-census-readonly.md` | F2 | 68, 478, 517, 544 |
| `quarantine-origin-record-fields-r24.md` | F4 | 42, 432 |
| `quarantine-staging-no-copy-r23.md` | F4 | 42, 429 |
| `dupe-finders-detect-then-act.md` | (no `ground:`) | 41 |
| `git-auto-maintenance-prunes-worktrees.md` | (no `ground:`) | 39 |
| `git-grace-periods-and-expire-to.md` | (no `ground:`) | 39 |
| `jj-colocation-receipts.md` | (no `ground:`) | 216 |
| `process-residue-observations.md` | (no `ground:`) | 274 |
| `quarantine-same-filesystem-rename.md` | (no `ground:`) | 42 |
| `trash-spec-restorable-quarantine.md` | (no `ground:`) | 42 |

Grounded total at 89e0fce = 7 (F2 5 + F4 2); **zero** `ground: F1` entries.

### E6 — map-side counter K4 at the freeze revision

```
$ python3 -B tools/souji-coverage-agreement.py --root . \
    --rev 89e0fceeefcf28db313c94120be6d25e03c60094 \
    --base-rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd
grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0
exit=0
```

Identical to the committed base receipt `census/round-26/records/c2-k4-base.tsv`
(`rev=0eca7c8a...`, `tool_sha256=bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f`,
same counts line): the freeze commit added no map row and no grounded entry.

### E7 — map-side counter K4 and the F1 ground census at observed tips

```
$ python3 -B tools/souji-coverage-agreement.py --root . \
    --rev d6fe8a1125a9723e7593df7b8b90ee6c05cdf9ff \
    --base-rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd
grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0
exit=0
```

```
$ R=07f83e69979b1032f9de4fe876739a8dccc7242b
$ python3 -B tools/souji-coverage-agreement.py --root . --rev $R \
    --base-rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd
grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0
k4_exit=0
$ git grep -l '^ground: F1' $R -- corpus/knowledge/ | sed "s/$R://"
corpus/knowledge/git-auto-maintenance-trigger-set-r23.md
corpus/knowledge/git-auto-maintenance-trigger-set.md
k1_count=2
```

Each revision above was the lane's `master` head at the moment of its own measurement (the
wave was committing while this seat ran). Both counts lines equal the amended C2
after-literal (`preregistration-amendment-1.txt`: grounded=9 / kill_tested=7).

### E8 — README delta freeze → tip 07f83e69

```
$ R=07f83e69979b1032f9de4fe876739a8dccc7242b
$ git diff --stat 89e0fceeefcf28db313c94120be6d25e03c60094 $R -- corpus/README.md
 corpus/README.md | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)

$ git diff -U0 89e0fceeefcf28db313c94120be6d25e03c60094 $R -- corpus/README.md | grep -E '^@@'
@@ -39 +39 @@ when the file exists, not before.
@@ -46 +46 @@ when the file exists, not before.

$ git diff -U0 89e0fceeefcf28db313c94120be6d25e03c60094 $R -- corpus/README.md | grep -E '^[+-]\| F1'
-| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md` |
+| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md` |

$ git show $R:corpus/README.md | awk 'NR==39{n=gsub(/\|/,"|"); print "39: pipes="n}'
39: pipes=4
```

`git show 07f83e69:corpus/README.md` is still 558 lines.

### E9 — target of the tip's Frontier bullet

```
$ R=07f83e69979b1032f9de4fe876739a8dccc7242b
$ git show $R:corpus/README.md | awk 'NR==46'
- F1 git-native housekeeping vs receipts — next: the trigger set and the measured prune are now held (round-26 entries `knowledge/git-auto-maintenance-trigger-set{,-r23}.md`, S128-S132); remaining: keep-ref expiry unmeasured, fleet exposure numerator re-census.

$ git show $R:corpus/SOURCES.md | awk -F'|' 'NR>=149&&NR<=153{for(i=2;i<=5;i++) gsub(/^ +| +$/,"",$i); printf "%d\t%s\t%s\t%s\t%d chars\n", NR,$2,$4,$5,length($0)}'
149	S128	docs	A	642 chars
150	S129	code	A	840 chars
151	S130	code	A	705 chars
152	S131	own-work	A	948 chars
153	S132	own-work	A	751 chars
```

The grep form (`grep -nE '^\|[[:space:]]*S1(28|29|30|31|32)[[:space:]]*\|'`) matched the same
five rows at `:149`–`:153`; each is a single line of the width printed above, so only
id/type/tier are reproduced here rather than the long claim and note cells.

### E10 — prefix-form completeness check

`grep -nE '^[ >*+-]*\|[[:space:]]*(\*{0,2})?(F[0-9]|receipts)'` on the frozen blob returned
the same 12 rows as E2 — no blockquote-prefixed or bullet-prefixed table row exists. All 40
`^|` lines are accounted for: 7 header rows + 7 separator rows + 21 map rows (E4) + the
5-row claim table at `:454-458`.

## Findings

1. **`corpus/README.md:39` (rev 89e0fce) is the F1 row, and it names exactly two entries,
   neither grounded.** `git-auto-maintenance-prunes-worktrees.md` and
   `git-grace-periods-and-expire-to.md` carry no `ground:` front-matter line (E5). Hence the
   base has zero F1-grounded entries — consistent with C2 K1 base `0` and with K4's
   `grounded=7` being entirely F2 (5) + F4 (2).
2. **`corpus/README.md:40` is the superseded F2 row** and self-labels:
   "superseded by Round 24 F2 row (:517)". It is still a live map row for the instrument
   (it matches `^F2` followed by space), so its entries cell `—` contributes no path.
3. **F2 is the most-duplicated ground: 5 rows** (`:40`, `:68`, `:217`, `:517`, `:544`), of
   which `:217` is a caveat row that claims no capability ("observed, not claimed") and
   `:544` is the current five-entry row. Per F<k> mapping is a set union, so duplication is
   harmless to K4 but a reader looking for "the F2 row" has no single row.
4. **`corpus/README.md:240` is a non-F row inside a `ground` table** and is therefore *not*
   a map row to the instrument (`GROUND_TOKEN = ^F<k>` followed by space/`-`/end,
   `tools/souji-coverage-agreement.py:31`), even though a naive `^\| F[0-9]` scan also
   misses it. Any future census driven by regex alone under- or over-counts here; E4 is the
   honest inventory.
5. **`corpus/README.md:517` carries a stale prose count inside a frozen row**: it says "read
   side (three entries, r13/r23)" while its own entries column names four knowledge paths
   (`git-repo-structure-readonly`, `repo-size-census-readonly`,
   `count-objects-garbage-readings-r25`, `count-objects-linked-worktree-garbage`). `:544`
   is the corrected row ("five sourced entries", five paths). The superseding `:544` row
   covers it, but the disagreement is visible at `:517` alone.
6. **`:517` (1220 chars) and `:544` (1355 chars) are single-line rows.** Line-anchored
   `^\|` enumeration (E2) and the instrument's per-line parse both depend on that; wrapping
   either row would silently drop it from the map census. This is the operability constraint
   any r26+ map edit inherits.
7. **The freeze→tip README delta is exactly two lines, `:39` and `:46`** (E8): `:39` gains
   the two new trigger-set entry paths, `:46` gains the frontier next-step text. No other
   map row changed, line numbers did not shift, and `:39` still has 3 cells / 4 pipes — no
   literal `|` was introduced into the entries cell.
8. **K4 is at its amended after-literal at both observed tips** (`d6fe8a11`,
   `07f83e69`): `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7
   kill_violations=0`, exit 0 (E7). The two new grounded entries are exactly
   `git-auto-maintenance-trigger-set.md` and `git-auto-maintenance-trigger-set-r23.md`
   (E7's `git grep` count = 2), and both are named by the F1 row at `:39`.
9. **The tip's Frontier bullet (`:46`) cites `S128-S132`, and all five rows exist**
   (`corpus/SOURCES.md:149-153`, E9). The bullet writes the entries as
   `knowledge/git-auto-maintenance-trigger-set{,-r23}.md` — brace shorthand, not a literal
   path. The instrument only reads backticked paths inside `ground` table rows, so this is
   not a dangling path for K4; a path-scanning reader outside the instrument would see a
   non-existent name.
10. **K4 at the freeze revision is byte-equal to the base receipt** (`grounded=7 mapped=7
    dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, E6), so amendment 1's
    corrected literals are not disturbed by the freeze commit and the base arm remains
    reproducible at the freeze rev as well as at `0eca7c8`.

## Lane state at run time (not this seat's writes)

`git status --porcelain` (lane) showed, besides this report:
`M tools/souji-axis-check.py`, `?? tools/__pycache__/` (`souji-axis-check.cpython-314.pyc`,
mtime 14:25), `?? tests/fixtures/__pycache__/` (`r26-axis-check.cpython-314.pyc`, mtime
14:26), `?? census/operator-sweep-20261019/`. The two `__pycache__` trees belong to another
seat's C3 runs (they name the axis-check tool/fixture, and their mtimes precede this seat's
first command); every lane Python invocation in this seat used `python3 -B` and none of
these paths was created, modified or removed here. Flagged for the integrator's hygiene
pass, not deleted by this seat.

## Attack log

n/a — this seat is a mechanical enumeration, not an attack. No predicate, target or case set
is challenged here; findings 5, 6 and 9 are map-hygiene observations at named lines, not
counter defects.
