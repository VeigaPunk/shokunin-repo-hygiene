# W1CritC1Axis — C1 axis attribution: calibration, or quality/bookkeeping?

seat: W1CritC1Axis (critic, leaf; no subagents). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`,
lane base `ed30b7f5b77939c9073348d810730bc4f355708d`, freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`,
lane HEAD while measuring `d4c1755` (`round-39: C3/scratch — honour the caller's TMPDIR…`).
Read-only on the lane: every write below is either this report or a scratch git fixture under
`/fast/scratch/hyaku/souji-r39/W1CritC1Axis/` (removed before yield). No tool installed or upgraded
(nothing needed; pacman untouched). No mutating git/jj command ran anywhere: the two fixture repos
are `git -C "$D" init` + `commit` inside `$D` after `rev-parse --show-toplevel` printed `$D`.

## Verdict in one paragraph

**The attribution is right: C1 is a calibration claim, not a quality/bookkeeping claim booked to the
wrong axis.** The surface it changes is the lane's self-assessment corpus — the r39 C1 commits touch
`LOG.md`, `SCORECARD.md`, `SKILL.md`, `census/round-38/preregistration.txt`, `corpus/QUALITY.md` and
three lesson files, and no tool or fixture — and the measured delta is the count of those statements
that disagree with committed bytes (`open=16 → 0`). That is exactly the surface class Q59 assigns to
calibration ("a self-assessment-file change is a calibration surface"), the AXES.md calibration signal
("SCORECARD entries match observed repo state"), and the class of every souji calibration claim from
r29 to r38. The do-nothing control is real: the frozen counter bytes at the freeze and at the base both
read `open=16`, rc 1 (re-derived here, `items_sha=d892b74f8358` identical to the committed receipt).
Two things in the claim's *wording* are wrong and are calibration defects of the same class C1 exists
to police, not attribution errors: (1) the sentence "the 16 routed defects become one counter" is
contradicted by the round's own routed table — the 16 item rows cover **14** of the 16 routed defects
(R13 carries three rows) and **R10/R11 are C2's legs**; (2) the honest verdict is **surface repaired,
quality untested** — every one of the 16 was found by a non-author spot-check and the round adds no
self-detection mechanism, while 6 of the 16 rows also move freshness (R13), coverage (R4, R6) and
conduct (R3) surfaces. The item arm also cannot witness a *false* correction (demonstrated below), so
the register arm — still uncommitted at `d4c1755` — is the only half that re-derives a value.

## 1. Definition and the r25 lesson, applied

| source | text that governs the label |
|---|---|
| `AXES.md` (fleet) | calibration = "Self-assessment quality: gaps named honestly, confidence graded, overreach caught" / signal "SHONEN.md/SCORECARD entries match observed repo state"; freshness = "Drift detection — skill claims re-verified against live surfaces; stale items flagged or fixed"; coverage = "Fraction of the domain's real surfaces the skill governs (repo paths, tools, edge classes)"; operability = "Runnable artifacts: checklists that are executable, commands that exist, scripts that run" |
| `corpus/QUALITY.md:143` (Q59) | "the declared axis must correspond to the actual class of surface the claim changes (… a knowledge-registry change is a coverage surface; **a self-assessment-file change is a calibration surface**). A claim whose axis and surface class are incompatible is a misattribution defect, and the check must be an instrument, not a hand review." |
| `corpus/lessons/round-25.md:10` (the attribution lesson) | r25 C2 = "**unprovable on the declared axis**. W2 review shows the change is coverage of edge classes, not a change to runnable operability; the frozen axis is not relabeled." Closing line: "the axis-misattribution harms calibration." |

The r25 test, made explicit, is two questions: **what surface moved**, and **what quantity the
before→after counts**. r25 failed it because the moved surface was fixture cases (edge classes =
coverage) while the declared axis was runnable operability, and the tool's runnability was unchanged.
C1 answers both questions inside calibration: the moved surface is self-assessment files (Q59:
calibration), and the counted quantity is statement-vs-state disagreement, i.e. AXES.md's calibration
signal itself. So this is **not** the r25 failure mode and `unprovable on the declared axis` is **not**
the honest verdict here. What C1 cannot claim is the other half of the axis definition (quality of the
assessment act) — see F1/F4.

Lane precedent, for consistency: every SCORECARD calibration row from r29 on counts agreement between
a self-assessment cell and a committed record — r29 registry/record agreement, r30/r31/r32/r33
capability-cell binding, r34/r35 registry/outcome agreement, r36 coverage-map binding, r37/r38
citation reconciliation (`SCORECARD.md:303,344,412,477,512,539,552,562,628,666`), and the round's own
planned r39 calibration item is the register's commit arm (`SCORECARD.md:686`). C1 is the same
instrument family with a wider item set; the label does not change kind.

## 2. The surface the round changes

```
$ git diff --name-only ed30b7f5b77939c9073348d810730bc4f355708d..HEAD
LOG.md
PROVINCE.md
SCORECARD.md
SKILL.md
census/round-38/preregistration.txt
census/round-39/c1-counter.py
census/round-39/c1-items.tsv
census/round-39/c2-counter.py
census/round-39/c3-counter.py
census/round-39/preregistration.txt
census/round-39/records/c1-before.txt
census/round-39/records/c2-before.txt
census/round-39/records/c3-before.txt
corpus/QUALITY.md
corpus/SOURCES.md
corpus/lessons/round-36.md
corpus/lessons/round-38.md
corpus/lessons/round-39.md
tests/fixtures/r39-citation-rev.py
tests/fixtures/r39-drift-record-rules.py
tools/souji-citation-reconcile.py
tools/souji-worktree-drift.py
```

The three C1 landing commits alone, which is what the axis label is about:

```
$ git show --stat --oneline c0b007b 50972f0 094e531
c0b007b round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows, gate-registry rows
 LOG.md | 6 ++   SCORECARD.md | 4 ++   SKILL.md | 11 +++   census/round-38/preregistration.txt | 4 ++
 corpus/QUALITY.md | 4 ++   corpus/SOURCES.md | 5 ++   corpus/lessons/round-36.md | 4 ++
 corpus/lessons/round-38.md | 8 +++   corpus/lessons/round-39.md | 133 +++++
 9 files changed, 179 insertions(+)
50972f0 round-39: C1 — single-line anchor bullets for R5/R7/R15 closures
 corpus/lessons/round-39.md | 16 +++-------------   (3 insertions, 13 deletions)
094e531 round-39: C1 — R7 line names the reaped path as $HYAKU_SCRATCH, not a literal scratch root
 corpus/lessons/round-39.md | 2 +-   (1 insertion, 1 deletion)
```

Verdict: **self-assessment files only — no tool, no fixture, no gate behaviour.** Note the commit
subject itself says "14 routed-defect corrections" while the round's Claims bullet says 16 (F1), and
that `corpus/SOURCES.md` (+5, the three r39 source rows) is a knowledge-registry append, which Q59
maps to coverage — it is the round's frontier work, not part of C1's item set, so it is a coupling of
the commit, not of the claim.

## 3. The control: the counter that stays unmoved if the work is skipped

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ TMPDIR=/fast/scratch/hyaku/souji-r39/W1CritC1Axis python3 -B census/round-39/c1-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv \
    --scratch /fast/scratch/hyaku/souji-r39/W1CritC1Axis
ITEM R39-C1-01 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-01'
… (all sixteen rows OPEN: ANCHOR-ABSENT / FILE-ABSENT) …
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```

Same counter bytes and the same items file, at the freeze commit that introduced them:

```
$ … --rev b769bfb84a264d8b284c09bc211d99f39a3e9126 …
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
pipe-rc=1
```

At the lane HEAD while this seat measured (`d4c1755`):

```
$ … --rev $(git rev-parse HEAD) …
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
head-pipe-rc=1
```

Verdicts: (a) **the surface is instrumented and cannot be satisfied by doing nothing** — base and
freeze both read `open=16`, rc 1, and the `items_sha` matches the committed `c1-before.txt` byte for
byte, so the control is re-derivable today; (b) at HEAD the item arm is mid-flight (`open=2`, the two
wave-capture receipts) and **the register half is not measurable at all** — `census/round-39/cells.tsv`
does not exist (`ls census/round-39/cells.tsv` → "No such file or directory"), so
`register_cells>=6 commit_distinct>=2` has no reading yet. That is state, not a verdict on the frozen
predicate; the register arm is also the only half that re-derives a value (F2).

## 4. What the counter does **not** re-derive (truth checks I ran in its place)

The counter binds tokens; it never reads the receipt a correction line quotes:

```
$ grep -n "receipt\|SOURCES\|W04\|LOG\|QUALITY\|SCORECARD" census/round-39/c1-counter.py
8:  carried `commit == receipt_rev`, so the live register never exercised the commit arm's revision
21: differs from `receipt_rev`, and the frozen `tools/souji-citation-reconcile.py` bytes at `--rev` are
130: """Row count and the rows whose commit differs from receipt_rev (8-column schema)."""
137: if parts[:7] == ["id", "file", "anchor", "expected", "stale", "receipt", "receipt_rev"]:
```

All four hits are the register leg. So I re-derived the cited values myself:

```
$ git show fcdecaaf293f0fee3c39cc148ae91389e04ef63c:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
170
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji | grep -c W04
47
$ grep -c S246 corpus/lessons/round-38.md
1
$ tail -2 census/round-37/records/c2-before.txt
SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
rc=1
$ tail -2 census/round-37/records/c2-after.txt
SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
rc=0
```

Verdicts: C1-01's `SOURCES-rows=170` / `SOURCES-added=8` / `W04=47` are **true** at `fcdecaa`; S246
is now named in the r38 lesson (the R1 defect's "appears in no lesson byte" is closed); the integers
C1-11/C1-12/C1-13 quote (`cases=12 pass=3 fail=9 base_fail=9`, `cases=12 pass=12 fail=0 base_fail=9`,
`escapes=9` on both arms) are **true**. The repairs are honest corrections, not token-shaped prose —
but the predicate does not know that, which is F2.

## 5. Counterexamples (scratch git fixtures, `$D` asserted by `rev-parse --show-toplevel`)

Fixture 1 — the frozen row shape against a *false* correction and against a *retained* contradiction
(`$D` = `/fast/scratch/hyaku/souji-r39/W1CritC1Axis/demo-truth.*`, doc `log.md`, items `demo2-items.tsv`):

```
ITEM D-TRUE CLOSED          (line: "the receipt prints fail=9"      — true)
ITEM D-FALSE CLOSED         (line: "the receipt prints fail=6"      — false, same token shape)
ITEM D-RETAIN CLOSED        (line: "SOURCES-rows=170 … ; the same block still reads SOURCES-rows=167")
ITEM D-RETAIN-NEG OPEN PREDICATE-MISSING log.md missing=[] hits=1   (same line, mustnot=SOURCES-rows=167)
SUMMARY items=4 open=1 …
```

Verdict: the item arm has **no truth channel** — a correction that asserts a wrong value closes
exactly like the right one — and because all 16 frozen rows carry `mustnot = -`, a line that still
asserts the stale value passes. A `mustnot` token would catch it (row 4), so this is a fixable
instrument gap, not a tradeoff.

Fixture 2 — the real C1-11 row shape, whose `must` tokens are the **stale** integers
(`demo-vacuity.*`, doc quoting `cases=9 pass=3 fail=6` plus a correction line):

```
ITEM DEMO-1 CLOSED          (must = LOG-line-1855,cases=9,fail=6 — satisfied by quoting the stale values)
ITEM DEMO-2 OPEN PREDICATE-MISSING log.md missing=['receipt-prints-fail=6'] hits=1
```

Verdict: for C1-11 and C1-12 the corrected integers are **not in `must`** (`LOG-line-1862` alone for
C1-12), so `CLOSED` there evidences that an annotation exists and names the stale cell — not that any
value was corrected. The landed text is truthful (§4); the instrument would read the same on a false
annotation.

## 6. The lane's own attribution instrument is dead (Q59 check column)

```
$ python3 -B tools/souji-axis-check.py --prereg census/round-39/preregistration.txt --scorecard SCORECARD.md
souji-axis-check: refused: no `## MACHINE BLOCK ... END` section found
rc=2
$ for n in 26 27 28 33 34 35 36 37 38 39; do … grep -c 'MACHINE BLOCK' census/round-$n/preregistration.txt; done
r33: 0  r34: 0  r35: 0  r36: 0  r37: 0  r38: 0  r39: 0
$ grep -c "MACHINE BLOCK" census/round-28/records/preregistration.txt
1
$ python3 -B tools/souji-axis-check.py --prereg census/round-27/records/preregistration.txt --scorecard SCORECARD.md
claims=3 flags=0
rc=0
$ grep -c "souji-axis-check" SKILL.md
0
```

Verdict: Q59's check ("exits 0 and prints `flags=0` … before scoring", and "the check must be an
instrument, not a hand review") **cannot run on the r39 contract** — the frozen prereg has no machine
block, and the tool has no SKILL registry row. So C1's axis attribution is hand-reviewed, which is the
thing Q59 forbids; the same registry-row class as R6 that C1 closes for four other counters. This does
not make the label wrong (I applied the rule by hand in §1), it makes the round's own calibration
argument un-instrumented.

## 7. Claim scope: 16 rows are not 16 defects

`corpus/lessons/round-39.md:56-72` (the routed table) maps each defect to its item and gives
`R10 → C2`, `R11 → C2`; `corpus/lessons/round-39.md:12-13` says "The 16 routed defects become one
counter: 16 anchored single-line predicates"; `census/round-39/preregistration.txt:25` says "C1 closes
each routed defect in lane bytes"; `:111` correctly says "C1 claims the 16 items its frozen list
enumerates".

Counting the table: items cover R1, R2, R3, R4, R5, R6, R7, R8, R9, R12, R13(×3), R14, R15, R16 =
**14 distinct defects in 16 rows**; R10 and R11 are C2's behavioural legs. So C1 closes **14 of the 16**
routed defects and C2 closes the other two, and `items=16 open=0` is a *row* count
that coincides with the defect count. A reader who re-derives "16 defects closed" from `items=16` is
wrong by two — and that is a self-assessment mismatch introduced by the round that exists to remove
them.

## Findings

| # | counterexample | evidence | impacted axis | smallest safe correction |
|---|---|---|---|---|
| F1 | The claim "the 16 routed defects become one counter" is false; the round's own table sends R10/R11 to C2 and gives R13 three rows, so 16 rows = 14 distinct defects; the other two (R10/R11) are C2's legs | `corpus/lessons/round-39.md:12-13` vs `:56-72`; `census/round-39/preregistration.txt:25` vs `:111`; commit subject `c0b007b` says "14 routed-defect corrections" | **calibration** (the claim's own honesty) | Restate the Claims bullet and the report line as "14 of the 16 routed defects, in 16 anchored rows; R10/R11 are C2's legs". Text only — the frozen predicate, items file and counter are untouched. |
| F2 | The item arm cannot distinguish a truthful correction from a false one, and cannot see a retained stale value | `grep` of the counter (register leg only); fixture 1 (`D-TRUE`/`D-FALSE` both CLOSED, `D-RETAIN` CLOSED); fixture 2 (C1-11's `must` = the stale integers); all 16 rows `mustnot = -` | **calibration** (instrument) | Disclose as a named limit now ("the item arm asserts presence, not truth; the register arm is the value-re-deriving half"); in r40 put the corrected integer in `must` and the stale literal in `mustnot` for literal-repair rows. Never edit the frozen items file in r39. |
| F3 | Q59's attribution instrument cannot run on the round's contract | `axis-check` refuses the r39 prereg, rc 2; machine blocks absent r33–r39, present r26–r28; no `souji-axis-check` SKILL row | **calibration** | Disclose the hand review; r40 restores a `## MACHINE BLOCK` at freeze time and adds the tool's registry row. |
| F4 | The bundle is not axis-pure: R13's three rows are freshness' "stale items flagged or fixed" surface, R4 (wave evidence committed) and R6 (registry rows) are coverage's governed-surface class, R3 is conduct/protocol | AXES.md freshness/coverage lines; Q59 "knowledge-registry change is a coverage surface"; the prereg itself already concedes R3 ("15 of them are the class calibration exists to police") | calibration attribution is **not** harmed if named; freshness/coverage would lose credit if the row books 16/16 as calibration mismatches | Book it as a calibration-anchored bundle and name the tail (3 freshness, 2 coverage, 1 conduct) in the SCORECARD/LOG row. |
| F5 | At `d4c1755` the item arm reads `open=2` and the register arm reads `cells=0` because `cells.tsv` is uncommitted | §3 outputs; `ls census/round-39/cells.tsv` → No such file | none yet (state, not verdict) | Land `cells.tsv` and the two wave receipts before the claim is read; no predicate change. |

No axis is harmed by the label itself. The calibration **score** must not move: no reproducible 0–10
mapping exists (lane convention since r25), and nothing here measures self-detection.

## Recommended honest verdict line (prose only; the frozen predicate is not rewritten)

> **C1 calibration 7 — surface repaired, quality untested.** 16 anchored self-assessment corrections
> close 14 of the 16 routed r38 defects (R10/R11 are C2's legs; R13 takes three rows), measured on the
> surface Q59 assigns to calibration: the base arm re-read `open=16`, rc 1, and the freeze arm reads
> the same, so a do-nothing round cannot satisfy it. The mismatches were found by a non-author
> spot-check and the round adds no self-detection mechanism, so the axis' quality clause does not
> move; the row books a calibration-anchored bundle with a named tail (R13 → freshness, R4/R6 →
> coverage, R3 → conduct). The item arm asserts presence, not truth (no truth channel, `mustnot = -`
> on all 16, C1-11/C1-12 `must` = the stale integers); the value-re-deriving half is the register arm,
> uncommitted at `d4c1755`. Score unchanged.

## Commands run (complete index)

1. `git rev-parse HEAD`; `ls census/round-39/cells.tsv` — lane state.
2. `c1-counter.py --rev ed30b7f… --items c1-items.tsv --register cells.tsv --scratch …` — base control (§3).
3. `c1-counter.py --rev b769bfb… …` — freeze arm (§3).
4. `c1-counter.py --rev $(git rev-parse HEAD) …` — HEAD arm (§3).
5. `git diff --name-only ed30b7f…..HEAD`; `git show --stat --oneline c0b007b 50972f0 094e531` (§2).
6. `git show fcdecaa:corpus/SOURCES.md | grep -cE '^\|…S[0-9]{3,}…'` → 170; `scripts/sources-census.sh validate … | grep -c W04` → 47; `grep -c S246 corpus/lessons/round-38.md` → 1 (§4).
7. `tail -2 census/round-37/records/c2-before.txt` / `c2-after.txt` (§4).
8. `grep -n "receipt\|SOURCES\|W04\|LOG\|QUALITY\|SCORECARD" census/round-39/c1-counter.py` (§4).
9. Fixture 1: `mktemp -d`, `git -C $D init -q`, `rev-parse --show-toplevel` = `$D`, `commit`, `c1-counter.py --root $D --rev … --items demo2-items.tsv --min-cells 0 --min-commit-distinct 0` (§5).
10. Fixture 2: same shape, real C1-11 tokens, `demo-items.tsv` (§5).
11. `tools/souji-axis-check.py --prereg census/round-39/preregistration.txt --scorecard SCORECARD.md`; machine-block survey r26–r39; `grep -c souji-axis-check SKILL.md` (§6).
12. `sed -n '10,20p'`, `'38,80p'` of `corpus/lessons/round-39.md`; `grep -n "routed defect" census/round-39/preregistration.txt` (§7).
13. `sed -n '1,16p' corpus/lessons/round-25.md`; `grep -n Q59 corpus/QUALITY.md`; fleet `AXES.md` (§1).
14. Scratch `/fast/scratch/hyaku/souji-r39/W1CritC1Axis/` removed after the runs (no tree left on disk).
