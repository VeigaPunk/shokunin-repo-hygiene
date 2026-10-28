# W1ConnDuplicates — do the 16 new C1 correction lines duplicate existing corrections?

seat: W1ConnDuplicates (connector, leaf) · round 39 wave 1 · judged axis: **calibration**
lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
read at: lane base `ed30b7f5b77939c9073348d810730bc4f355708d`, then HEAD `2201778e7736af82e7d8a42dec2494f115bf3923`,
then HEAD `e9958ee517668fa8aa8a86a8b936b5b2ad56473e` with three dirty files (see §0)

## 0. Moving target — disclosed before any verdict

The lane changed under this seat while it ran. `git status --porcelain` at `e9958ee`:

```
 M LOG.md
 M SKILL.md
 M corpus/QUALITY.md
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
```

`git diff --stat` → `LOG.md | 4 ++--`, `SKILL.md | 16 ++++----`, `corpus/QUALITY.md | 2 +-`.
The three dirty files are exactly the three lines I first read (`R39-C1-11`, `R39-C1-12`,
`R39-C1-13`), and they were **rewritten in place in the working tree** between my first and second
reads. Example, `git diff -U0 LOG.md`:

```
-R39-C1-11 — LOG-line-1855 (the r37 C2 bullet) states `cases=9` and `fail=6`; no r37 receipt carries those integers — ...
+R39-C1-11 — LOG-line-1855 (the r37 C2 bullet) carries the superseded before-arm letters `cases=9 pass=3 fail=6 base_fail=6` ...
```

Every verdict below is against the **current working-tree bytes** at `e9958ee` (the state the L1
will land); where the earlier committed text differed materially I say so. The C1 counter reads
`git show <rev>:<file>`, so **none of these lines is scored until the L1 commits them** — the item
legs I quote in §5 are the working-tree state, not a landed reading.

## 1. Existing correction inventory (the surfaces the task named)

| surface | block | lines | cells it corrects |
|---|---|---|---|
| `SCORECARD.md` | r34 restatements `E04` / `E18` | 529–530 | `SCORECARD.md:21` (r28 gate), `SCORECARD.md:71` (repo-structure selftest) |
| `SCORECARD.md` | r26 `K18` | 506 | `SCORECARD.md:175` |
| `SCORECARD.md` | r30 `R30-CORRECTION` | 335 | `SCORECARD.md:175` |
| `SCORECARD.md` | `### Round 37 receipt reconciliation` `R37-C1-1..4,10,11` | 603–620 | r36 C2/C3 after cells, capability rows, `SKILL.md:247` |
| `SCORECARD.md` | `R38-C1-1..6` | 655–660 | **r37** C2 after/before, C3 after/before, C1 after ×2 |
| `SCORECARD.md` | r38 pointer/finality blocks | 692–735 | r38 receipts; finality labels `78ea25a`→`4bda5f6`→`cb5737a`→`99efe06` |
| `LOG.md` | r37 adjudication + frozen-predicate supersession | 1861–1862 | the r37 frozen predicate letters; states receipts `cells=11` / `cases=9 base_fail=6` |
| `LOG.md` | `R38-C1-7`, `R38-C1-8`, `R38-C1-9` | 1868–1870 | **LOG-line-1855** (escapes / base_fail / fail) |
| `corpus/QUALITY.md` | `R38-C1-10` | 220 | **`QUALITY.md:209`** (Q84 evidence cell) |
| `corpus/lessons/round-36.md` | `## Correction (r37)` (`R37-C1-7`) | 168–172 | the r36 Claims line — states "The Claims line is corrected **in place**" |
| `corpus/lessons/round-38.md` | `### Gate corrections` | 247–256 | S239/S242 → S244/S245; "Registry grep count **167 → 169**" |
| `corpus/lessons/round-38.md` | `## Claims corrections` | 258–268 | Counter pointers; ten-vs-eleven cells; `a7-counter-fixes` regenerated |
| `census/round-38/preregistration.txt` | `A7` (own text) | 200–222 | says `a7-counter-fixes` "is regenerated at the tip because its first label named a revision that predates the A7 commit" |

`E04`/`E18` and every `R37-C1-*` row are **disjoint** from the 16 r39 cells: they correct
`SCORECARD.md:21/71/175` and the r36 C2/C3 cells, none of which any r39 item names.

## 2. Duplicate-correction table

`adds` = does the new line add a **commit binding** (a resolvable revision on the line, carrying the
corrected value), a **corrected value**, or **nothing**.

| new id | cell corrected | existing correction on that cell | adds | duplicate? |
|---|---|---|---|---|
| R39-C1-01 | `round-38.md:156-166` `## Frontier` (162→167, A×5, touched none) + r38 report Frontier row | none in lane bytes; value already in `census/round-39/records/census-before.txt` (`rows=170`, `W04=47`) | corrected value (170 / added=8 / W04=47) **+ commit `fcdecaa`** | no — but see §4.1 (conflicts with the same file's `169`) |
| R39-C1-02 | r38 report opening "4 + 0 dead" + waves table | `LOG.md:1870` already states "Wave 1 (42 seats, 0 dead)" | corrected value (42/42, 32/32, dead=0); no commit | partial (dead=0/42 already in LOG) |
| R39-C1-03 | `census/round-39/records/waves-wait.txt` | none | **nothing** — file absent, item OPEN | no |
| R39-C1-04 | `census/round-39/records/waves-capture.txt` | none | **nothing** — file absent, item OPEN | no |
| R39-C1-05 | r37 LOG ledger row 8 ("not repeated — no `.ufo/prompts/` path") | none (spot-check R5 is routing only) | commit `068f75dc` — **resolves only in the fleet repo**, not the lane (§4.3) | no |
| R39-C1-06 | `SKILL.md` four missing r38 counter rows | none (rows landed in `c0b007b`, same round) | **nothing** beyond registry state; no commit | no |
| R39-C1-07 | r38 `consumers-after*.txt` base-arm scratch path | spot-check R7 already names `5f0dd45:tools/souji-worktree-drift.py` | commit `5f0dd45` (verified present) — **already R7's binding** | partial (value + binding from R7) |
| R39-C1-08 | r38 prereg `A7` evidence pointer | `A7`'s own text (regenerated at tip) + `SCORECARD.md:727` already names `a7-counter-fixes2.txt` | corrected receipt name (duplicate) + new instrument `r38-counter-arms.py`; no commit | partial |
| R39-C1-09 | r38 prereg rule sentence (in-place rewrite of "must be tighter-only.") | none — A0's clarification *is* the defect | corrected rule text; no commit | no |
| R39-C1-10 | SCORECARD r38 finality labels (`99efe06`) | none — the blocks are the defect | corrected value `fcdecaa` **+ commit binding (verified, §4.2)** | no |
| R39-C1-11 | **`LOG.md:1855`** (r37 C2 bullet) | **`R38-C1-7`, `R38-C1-8`, `R38-C1-9`** (`LOG.md:1868-1870`); `R38-C1-1` (`SCORECARD.md:655`) | before-arm value `cases=12 pass=3 fail=9 base_fail=9 escapes=9` + commits `861c2ba`, `8edcb04`, `02b4339` | **YES — same cell, 4th correction on it** |
| R39-C1-12 | **`LOG.md:1862`** | values already carried by `R38-C1-2` (`base_fail=9`) and `SCORECARD.md:629` (`cells=11`, `cases=12`) | corrected value (all already in lane bytes) + commits `02b4339`; adds the A1/A2 target list | **YES — value duplicate** |
| R39-C1-13 | **`QUALITY.md:209`** (Q84 evidence cell "(4 escapes) vs (0)") | **`R38-C1-10`** (`QUALITY.md:220`) already moved the before half to `escapes=9 @ 861c2ba` | after-arm value (`escapes=9`; the `0` is `fail`); `4` has no carrier; commits `861c2ba`, `02b4339` | **YES — same cell; disclosed inside the line** |
| R39-C1-14 | `census/round-38/records/c1-vacuity2.txt` self-description | spot-check R14 states the identical analysis (three rows × three classes → `mismatches=3`) | **nothing** (restates R14); no commit | duplicate of the routing text |
| R39-C1-15 | r38 report Landed-changes table | spot-check R15 lists the identical nine hashes; `78ea25a`/`cb5737a` already in SCORECARD/LOG | **nothing** (same nine; verified in range, 0 hits in the report) | duplicate of R15 |
| R39-C1-16 | `corpus/lessons/round-36.md:23` in-place rewrite | **`## Correction (r37)`** in the same file already discloses "The Claims line is corrected in place" and binds `1e771ed` | classification only ("in-place edit is a routed defect"); no value, no commit | **YES — disclosure duplicate** |

## 3. New lines that duplicate an existing correction (named)

1. **R39-C1-11** — the clearest duplicate. `LOG.md:1868-1870` already carries three appended r38
   corrections of the *same* bullet (`R38-C1-7` escapes, `R38-C1-8` base_fail, `R38-C1-9` fail), and
   `SCORECARD.md:655` (`R38-C1-1`) already declared the bullet's before column superseded. The r39
   line is the fourth correction of one bullet. It does add real content the r38 rows missed (the
   before-arm triple and the case count 9→12), but it never names `R38-C1-7/8/9` as superseded — it
   only says "this line supersedes its before-arm letters only".
2. **R39-C1-13** — same cell as `R38-C1-10` (`QUALITY.md:209`). Unlike (1) it *does* chain: "so
   `R38-C1-10` above already moved the before half to `escapes=9` @ `861c2ba`". Acceptable as an
   extension, but the cell is counted twice if any later register binds `QUALITY.md:209`.
3. **R39-C1-12** — same values as `R38-C1-2` / `SCORECARD.md:629`; the only new thing is that the
   stale clause lives on `LOG.md:1862`. No commit value is added that the lane did not hold.
4. **R39-C1-16** — `corpus/lessons/round-36.md:170-172` already recorded the in-place edit of the
   Claims line and bound it to `1e771ed`; the new line adds a policy sentence and no evidence.
5. **R39-C1-14 / R39-C1-15** — verbatim restatements of the spot-check's R14 and R15 text (same
   `mismatches=3` analysis; same nine hashes). They are the correct *locus* (lane bytes instead of
   fleet bytes), but they add no value or binding that the lane did not already hold.

## 4. Cross-checks on what the new lines assert

### 4.1 C1-01 — corrected value right, locus wrong, and it leaves a third count unreconciled

- `git show fcdecaa:corpus/SOURCES.md | grep -c "^| S[0-9]"` → `170`; at base
  `census-before.txt` → `rows=170`, `W04=47`. Corrected value confirmed.
- Row-count history I measured: `42ea92e`→156, `78ea25a`→167, `4bda5f6`→169, `cb5737a`→169,
  `99efe06`→170, `fcdecaa`→170, `ed30b7f`→170. So `round-38.md` now carries **three** row counts —
  167 (Frontier), **169** (`### Gate corrections`: "Registry grep count 167 → 169"), 170 (new line) —
  and the new line reconciles only the first. **Verdict: FAIL (calibration, minor)** — an
  unreconciled third value in the same file.
- Locus: the new line says the `## Frontier` block reads `"44 W04"`. It does not — `W04` appears
  once in that lesson, at line 67, as "the census warns W04, which is allowed", with no count. `44
  W04` is the **r38 report's** Frontier row (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md:126`:
  "44 W04 duplicate-URL warnings"). **Verdict: FAIL (misattributed locus)** — the token is real but
  belongs to fleet bytes, which is precisely why the correction is needed; the sentence should say so.

### 4.2 C1-10 — commit binding verified

```
$ git cat-file -t fcdecaa            → commit
$ git merge-base --is-ancestor fcdecaa HEAD → (0) fcdecaa ancestor-of-HEAD=yes
$ git diff --stat 99efe06 fcdecaa -- tools/ tests/ census/round-38/cells.tsv census/round-38/c1-counter.py
  → (empty)
$ git diff --stat 99efe06 fcdecaa    → SCORECARD.md 8+, census/round-38/records/{c1-after4,c1-after8,
  c1-vacuity3,c2-after7,c3-arms-filed,consumers-after3}.txt  → 7 files, 61 insertions(+)
```
"Instruments byte-identical from `99efe06` to `fcdecaa`, only additive SCORECARD/receipt bytes
differ" holds. **Verdict: PASS.** This is the strongest line of the 16 and the one I would keep
verbatim.

### 4.3 C1-05 — the commit it binds does not exist in the audited repo

```
$ git cat-file -t 068f75dc                      → fatal: Not a valid object name 068f75dc
$ git log --all --oneline | grep 068f75dc       → (none)
$ git -C /home/vgpnk/Projects/shokunin cat-file -t 068f75dc → commit
$ git -C /home/vgpnk/Projects/shokunin show --stat --oneline 068f75dc
  068f75dc round-38: souji dispatch evidence (hyaku inline attempt 1)
   .ufo/prompts/souji-round-38.md | 689 +++++++++++++++++++++++++++++++++++++++++
```
The line calls `068f75dc` "the r38 **lane** commit". It is a **fleet** commit, and it is the one
that added the prompt. The erratum's *fact* is right; its binding is repo-mismatched, so a
lane-scoped reconciler (`--root <lane>`) would read `COMMIT-UNRESOLVED` for it.
**Verdict: FAIL (binding unresolvable in the audited repo).** Fix: say "fleet commit `068f75dc`
(`/home/vgpnk/Projects/shokunin`)" or drop the hash.

### 4.4 C1-02 — value verified, locus claim unsupported

- `w1-results.json` → `w1 seats 42`, `w1 results 42`; `w2 seats 32`, `w2 results 32`. Values 42/42
  and 32/32 confirmed on disk. (`w1` holds 43 `*.md`; the extra is `W1ScribeReport-fleetroot-draft.md`,
  not a seat report — the count is 42 only if the draft is excluded, which the line does not say.)
- The line says "its waves table said w2 31/32". The report's table
  (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md:204`) reads
  `| w2 | 32 launched (11 reports at filing) | ... | 0 reported |`; `grep -n "31/32" <report>` → no
  match. `31` is the spot-check's own on-disk count at closure. **Verdict: FAIL (misattributed
  locus)**; the corrected numbers are right.

### 4.5 C1-11 / C1-12 / C1-13 — the rewritten lines' new bindings check out

```
$ git show 8edcb04:census/round-37/records/c2-before.txt | grep "SUMMARY"
  SUMMARY cases=9 pass=3 fail=6 base_fail=6 control=ESCAPE-REPRODUCED      (header: "final 9-case fixture")
$ git show 861c2ba:census/round-37/records/c2-before.txt | grep -c "^case-"  → 12   (8edcb04 → 9)
$ diff <(git show 8edcb04:...c2-before.txt|grep ^case-) <(git show 861c2ba:...|grep ^case-)
  8a9,11 > case-json-gitfile-write=FAIL > case-json-symlink-child=FAIL > case-record-symlink=FAIL
$ git rev-parse 861c2ba:census/round-37/records/c2-before.txt → ac576bdf07e54bcc385d2ddc187d5e62092c9386
$ git show 02b4339:census/round-37/records/c2-after.txt | sed -n '15p'
  SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
$ git show 02b4339:census/round-37/records/c1-after.txt | sed -n '3p'   → SUMMARY cells=11 mismatches=0
$ git show 02b4339:census/round-37/preregistration.txt | sed -n '18p;39p'
  Target (frozen): `SUMMARY cells=9 mismatches=0`, rc 0, ...
  Target (frozen): `SUMMARY cases=6 pass=6 fail=0 base_fail>=3
$ git grep -n "escapes=4" HEAD -- .   → only census/round-38/cells.tsv:2 and :11 (the stale columns)
```
Every integer and line number the rewritten C1-11/12/13 claim is reproducible from committed
bytes. **Verdict: PASS** on those three lines' evidence — and note this evidence was **absent** in
the first version I read (`states cases=9 and fail=6`, no commits).

### 4.6 C1-15 — nine hashes verified in range and absent from the report

```
$ git rev-list --count ca4369a..fcdecaa → 21
$ for c in 6949319 78ea25a f10a3a8 20eea73 a512efb 9b9e2f8 cb5737a be66886 c5050ea;
    do git merge-base --is-ancestor $c fcdecaa && ! git merge-base --is-ancestor $c ca4369a; done
  → all nine "in-range"
$ for c in ...; do grep -c "$c" /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md; done
  → 0 for all nine
```
**Verdict: PASS** on the fact; duplicate of spot-check R15 (§3.5).

## 5. Item state at the audited revision (context for the table)

```
$ TMPDIR=/fast/scratch/hyaku/souji-r39/W1ConnDuplicates python3 -B census/round-39/c1-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
    --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch <S>
ITEM R39-C1-01 CLOSED
...
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
...
ITEM R39-C1-16 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```
`census/round-39/cells.tsv` does not exist (`ls census/round-39/` → `c1-counter.py c1-items.tsv
c2-counter.py c3-counter.py make-cells.py preregistration.txt records`), so the register arm
(`register_cells>=6`, `commit_distinct>=2`) is **unmeasurable at this moment**. `make-cells.py`
would emit six rows (`REG-01..06`) with `commit` = the landing and `receipt_rev` = late/freeze —
i.e. `commit != receipt_rev` on all six, which is what C1 needs; that part is sound by construction.
`census/round-39/waves/` is also absent (C1-04's disposition table says evidence goes there).

## 6. Risks (second-order, calibration axis)

1. **`LOG.md:1855` now has two corrections with different `fail` values and no chain.** `R38-C1-9`
   (committed) says the receipt "carries `fail=0`"; `R39-C1-11` says the bullet should have carried
   `fail=9` (before arm). Both are true of different arms, and only the r39 line states a scope. A
   reader or matcher keyed on `fail=` gets two answers with no way to order them.
2. **`round-38.md` carries 167 / 169 / 170** with no supersession chain (§4.1).
3. **`cases=9` becomes a token with two subjects in `LOG.md`.** R39-C1-11 uses it as the stale r37
   C2 letter; `make-cells.py` `REG-05` will use `cases=9` as the stale r39 C3 letter ("`cases=7`
   ... the stale reading `cases=9`"). Same file, adjacent lines, opposite dispositions; only the
   anchor disambiguates. Currently `grep -c "cases=9" LOG.md` → 5 (lines 1667, 1855, 1862, 1875, 1877).
4. **C1-05's hash is fleet-scoped** (§4.3) — harmless only while no register row cites it.
5. **Two of the 16 lines are unanchored** (C1-03, C1-04) and one of them is required by the round's
   own disposition table ("captured into `census/round-39/waves/` with a verify receipt"); the
   directory does not exist yet.

## 7. Commands run (exact, absolute where it matters)

| # | command | key output |
|---|---|---|
| 1 | `ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/ /…/records/` | 6 records + 5 scripts + `__pycache__`; **no `cells.tsv`, no `waves-*`** |
| 2 | `grep -n "R39-C1-" SCORECARD.md LOG.md corpus/QUALITY.md SKILL.md corpus/lessons/round-3{6,8,9}.md` | 16 anchored lines, one per item |
| 3 | `grep -n "R38-C1-" SCORECARD.md` / `sed -n '600,640p;690,745p' SCORECARD.md` | R38-C1-1..6 at 655–660; finality blocks at 718/730; R39-C1-10 at 739 |
| 4 | `grep -rn "E04\|E18" SCORECARD.md LOG.md corpus/QUALITY.md` | E04 → `SCORECARD.md:21`, E18 → `:71` (disjoint from the 16) |
| 5 | `sed -n '1826,1885p' LOG.md` | r37 adjudication 1861–1862; R38-C1-7/8/9 at 1868–1870; R39-C1-11/12 at 1875/1877 |
| 6 | `sed -n '205,225p' corpus/QUALITY.md`; `grep -n "^| Q8[3-8]"` | Q84 at 209; R38-C1-10 at 220; R39-C1-13 at 222 |
| 7 | `sed -n '18,30p;155,178p' corpus/lessons/round-36.md` | r37 `## Correction (r37)` 168–172; R39-C1-16 at 176 |
| 8 | `sed -n '156,180p;245,292p' corpus/lessons/round-38.md` | Frontier 156–166; Gate corrections 247–256; R39-C1-01/02/14 at 285/287/289 |
| 9 | `cat corpus/lessons/round-39.md` | R39-C1-05/07/15 at 49/51/53 + closure table |
| 10 | `sed -n '118,145p;200,235p' census/round-38/preregistration.txt` | A0 + clarification; A7; A10/A11 at 229/231 |
| 11 | `git diff --stat 99efe06 fcdecaa`; `git diff --stat 99efe06 fcdecaa -- tools/ tests/ …` | 7 files/61 insertions; **empty** for instruments |
| 12 | `git merge-base --is-ancestor fcdecaa HEAD` | `fcdecaa ancestor-of-HEAD=yes` |
| 13 | `for c in 42ea92e 78ea25a 4bda5f6 cb5737a 99efe06 fcdecaa ed30b7f; do git show $c:corpus/SOURCES.md \| grep -c "^\| S[0-9]"; done` | 156, 167, 169, 169, 170, 170, 170 |
| 14 | `git cat-file -t 068f75dc` (lane) / `git -C /home/vgpnk/Projects/shokunin cat-file -t 068f75dc` | `fatal: Not a valid object name` / `commit` |
| 15 | `git show --stat --oneline 068f75dc` (fleet) | `.ufo/prompts/souji-round-38.md \| 689 +++` |
| 16 | `git cat-file -e 5f0dd45:tools/souji-worktree-drift.py` | `blob-present` |
| 17 | `git rev-list --count ca4369a..fcdecaa`; per-hash ancestor + `grep -c` in the r38 report | 21; nine in-range; 0 hits each |
| 18 | `python3 -c "json.load(open('.ufo/waves/round-38/w{1,2}-results.json'))"` | `w1 seats 42 / results 42`, `w2 seats 32 / results 32` |
| 19 | `ls .ufo/waves/round-38/w1/*.md \| wc -l` | 43 (42 seat reports + `W1ScribeReport-fleetroot-draft.md`) |
| 20 | `grep -n "31/32" /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md` | **no match** (table reads `32 launched (11 reports at filing)`) |
| 21 | `grep -n "44\b" …/round-38/souji.md` | line 126: `44 W04 duplicate-URL warnings` |
| 22 | `git log --oneline -S"r38-citation-commit" -- SKILL.md` | `c0b007b round-39: C1 — 14 routed-defect corrections …` |
| 23 | `git show 8edcb04/861c2ba:…/c2-before.txt`; `git show 02b4339:…/{c2-after,c1-after}.txt`; `git show 02b4339:…preregistration.txt` | `cases=9 … fail=6`; `cases=12 pass=3 fail=9 …`; line 15/line 3 as quoted; lines 18/39 as quoted |
| 24 | `git rev-parse 861c2ba:census/round-37/records/c2-before.txt` | `ac576bdf07e54bcc385d2ddc187d5e62092c9386` |
| 25 | `git grep -n "escapes=4" HEAD -- .` | only `census/round-38/cells.tsv:2` and `:11` |
| 26 | `TMPDIR=<S> python3 -B census/round-39/c1-counter.py … --rev 2201778e…` | `items=16 open=2`, C1-03/04 `FILE-ABSENT`, `register_cells=0`, rc 1 |
| 27 | `git rev-parse HEAD`; `git log --oneline -3`; `git status --porcelain`; `git diff --stat` | HEAD moved 2201778 → e9958ee; 3 dirty files |
| 28 | `cat census/round-39/make-cells.py` | 6 rows `REG-01..06`, `commit` ≠ `receipt_rev` on all six |

## 8. Verdicts

| check | verdict |
|---|---|
| existing-correction inventory over the four named files + lessons 36/37/38/39 | **PASS** (13 blocks, §1) |
| every new line mapped to a cell | **PASS** (16/16, §2) |
| duplicates named | **PASS** — 5 duplicate cells (C1-11, C1-12, C1-13, C1-16, C1-15/14); 3 partials (C1-02, C1-07, C1-08) |
| commit bindings on new lines verified | **MIXED** — C1-01/07/10/11/12/13/15 verified; **C1-05 unresolvable in the lane**; 8 lines carry no binding at all (C1-02/03/04/06/08/09/14/16) |
| locus claims in new lines | **FAIL (minor)** — C1-01 "44 W04" and C1-02 "w2 31/32" are the r38 report's / spot-check's bytes, not the blocks the lines name |
| unreconciled values introduced | **FAIL (minor)** — `round-38.md` now carries 167/169/170; `LOG.md:1855` carries `fail=0` and `fail=9` with no chain |
| item anchors present at the audited revision | **FAIL** — C1-03, C1-04 `FILE-ABSENT` (2 of 16 OPEN) |
| register arm measurable | **NOT MEASURABLE** — `census/round-39/cells.tsv` absent; `make-cells.py` would satisfy `commit != receipt_rev` on all six rows |

**Connector bottom line (calibration):** the 16 lines are not redundant as a set — 8 of them carry
evidence the lane did not hold before (C1-01's 170/8/W04=47, C1-10's `fcdecaa` binding, C1-11's
before-arm triple, C1-13's `escapes=4`-has-no-carrier, C1-05's fleet-commit identification, C1-07's
blob revision, C1-08's instrument, C1-09's restated rule). But **four lines land on cells the lane
already corrected** (C1-11, C1-13, C1-12, C1-16) and **two restate the routing document verbatim**
(C1-14, C1-15), and three of the sixteen leave a reader unable to order the corrections (LOG 1855
`fail`, `round-38.md` 169-vs-170). The cheapest single fix that improves calibration without
touching any predicate: add one clause to `R39-C1-11` naming `R38-C1-7/8/9` as its predecessors and
one to `R39-C1-01` naming the file's own `169` line as superseded, and reword C1-05's
"r38 lane commit" to "fleet commit".

## 9. Scratch, tooling, limits

- Scratch: `/fast/scratch/hyaku/souji-r39/W1ConnDuplicates` (created with `mkdir -p`; held only
  `lines.txt`, the anchored-line dump). **Removed at the end of this seat** (`rm -rf`), so it is not
  on disk. No `/tmp` use, no clone, no mutating git/jj command (only `log/show/diff/status/rev-parse/
  cat-file/merge-base/grep`).
- Tooling: **nothing installed or upgraded**; pacman not invoked (host-wide pause respected).
- Limits: (a) I audited the working tree, not a landed revision — the L1's landing will re-score
  these lines from `git show`, and the three dirty lines may change again; (b) I did not re-run the
  r38/r37 fixtures, so "the corrected value is what the receipt prints" is asserted from the receipt
  bytes, not from a re-execution; (c) I did not read the fleet repo's r38 report beyond the lines
  quoted (write scope forbids it anyway); (d) `cells.tsv` does not exist, so no register row of the
  r39 round could be duplicate-checked — my table covers the 16 item lines only, plus a note on
  `make-cells.py`'s six planned rows.
