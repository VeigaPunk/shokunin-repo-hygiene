# RevD7 — routed defect D7 verified against committed bytes

Lane base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`. Read-only seat; one scratch dir
`/var/tmp/souji-r23-RevD7/` (removed at end). No tool installed or upgraded this run. No lane
file written except this report.

## Status

STATUS: FAIL — D7 is real for M17 and reproducible, but the spot-check overstates it for M22, and
the round-23 planned repair (Q54 = an *uncommitted-round-work* criterion) targets D1's class, not
D7's, so it does not close the defect; the minimal closing repair is named in §3.

## Evidence

**E1 — the QUALITY.md half of the claim holds.** `corpus/QUALITY.md` is byte-identical at the r22
base, the r22 tip and the lane base:

```
$ git rev-parse 4edb25d:corpus/QUALITY.md 77d6595:corpus/QUALITY.md 1208bfb:corpus/QUALITY.md
4afdf00928a32ad8c6f5964a0c5cdb58f71315a8
4afdf00928a32ad8c6f5964a0c5cdb58f71315a8
4afdf00928a32ad8c6f5964a0c5cdb58f71315a8
$ git diff --quiet 4edb25d 77d6595 -- corpus/QUALITY.md; echo $?
0
```

Last row is `Q53` (`corpus/QUALITY.md:122`); no row after it, no `## Round 23` section, and no
criterion anywhere in the file mentions a section/heading/locator class (`grep -nE
'section|heading|locator'` returns only Q31/Q35/Q36, all about repo-relative *path* tokens).

**E2 — the `captured-by: none` set is M17, M19, M21 — not M17 and M22.**

```
$ git show 1208bfb:corpus/lessons/round-22.md | grep -nE 'Captured-by:\*?\*? none'
392:  locator-token check accepted the wrong one. *Captured-by:* none — the
412:  built in `/var/tmp`. *Captured-by:* none in the frozen fixture set.
429:  documents, same numbers. *Captured-by:* none mechanically; CORPUS.md rule 2
```

`corpus/lessons/round-22.md:447` (M22) reads verbatim:

```
credit `fails` (Q1, Q2). *Captured-by:* the coverage map plus QUALITY Q1/Q2 —
present as prose, not enforced before drafting.
```

M22 names two criteria. It is not a `captured-by: none` row; its real gap is that Q1/Q2 are not
executable before drafting — a different class from D7's. The lesson bytes are the same at the r22
tip and the lane base (`f892c915…` at both), so this is not a landing artefact.

**E3 — M17's class is live and uncaptured by the lane's own instrument.** The lane's gate-check
requires only a locator *token*: `tools/souji-gate-check.py:42`
`LOCATOR_RE = re.compile(r"(§|section|line |lines |paragraph|DESCRIPTION|OPTIONS|COMMANDS|SYNOPSIS|heading)", re.I)`
and `:87-89` apply it to the line with the snapshot path removed. `man7-mv.1.txt` has `SYNOPSIS`
(:54) and `DESCRIPTION` (:60) and **no** `OPTIONS` heading (`grep -nE '^OPTIONS'` → rc 1). Mutating
the committed entry's Gate locator to the invented section still passes:

```
$ git show 1208bfb:corpus/knowledge/quarantine-staging-no-copy-r23.md \
  | sed 's/§ DESCRIPTION, option --no-copy/§ OPTIONS, option --no-copy/' > /var/tmp/souji-r23-RevD7/mutant2.md
$ git show 1208bfb:tools/souji-gate-check.py > /var/tmp/souji-r23-RevD7/gate-check.py
$ python3 /var/tmp/souji-r23-RevD7/gate-check.py --round-date 2026-10-25 \
    --entries /var/tmp/souji-r23-RevD7/mutant2.md --snapshot-dir census/round-22/attempt2/sources
entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0      # EXIT=0
```

Control: the unmutated committed entry returns the same counts line, exit 0. So the mutant is
indistinguishable to the lane's gate — exactly M17's `Captured-by: none — the predicate only
requires a locator *token*, not that the heading exists.`

**E4 — a discriminating check exists and is cheap.** A 15-line read-only resolver over the Gate's
named snapshots (`§ <NAME>` must be a first-token heading line in one of them) separates the pair:

```
$ python3 /var/tmp/souji-r23-RevD7/locator-heading2.py /var/tmp/souji-r23-RevD7/mutant2.md
snapshots=4 headings=21 locators_bad=1 line-9:OPTIONS      # EXIT=1
$ python3 /var/tmp/souji-r23-RevD7/locator-heading2.py /var/tmp/souji-r23-RevD7/control.md
snapshots=4 headings=21 locators_bad=0                     # EXIT=0
```

**E5 — what the round actually plans.** `.ufo/waves/round-23/w1-spec.json` item `ScribeQuality`
(the only item that mentions `QUALITY.md`, of 41) instructs: *"Q54 (closes the spot-check's D7:
R22-M17/M22 recorded `captured-by: none` …): a round that ends with uncommitted lane-authored
round work, or whose report claims 'none uncommitted', must be caught by a named criterion"*, and
ends *"Do not edit QUALITY.md."* The frozen key set (`preregistration.txt:28-45`) is K1=D2, K2=D5,
K3=D4, K4=D1 — no key covers D6, D7 or D8.

## Findings

1. **D7 is real as stated for M17 only — overstated for M22.** `corpus/lessons/round-22.md:392`
   (M17) is a genuine `captured-by: none` row, and `corpus/QUALITY.md` gained no criterion
   base→tip (E1). But `:447` (M22) names "the coverage map plus QUALITY Q1/Q2"; the correct
   second `none` rows are M19 (`:412`) and M21 (`:429`), which the spot-check did not route.
   Verdict on the claim as written: **overstated** (one of two cited rows is mis-cited); verdict on
   the underlying class: **real and unclosed at the lane base**.
2. **The round-23 planned repair does not close D7.** Q54 as specified is an uncommitted-round-work
   criterion — that is D1's class, already counted by frozen key K4 (`preregistration.txt:41`), and
   the same item's own constraint ("no criterion may be a restatement of a counter's
   implementation") rejects it. Nothing in the plan writes the M17 class criterion; the item that
   would draft it is explicitly forbidden to edit `corpus/QUALITY.md`. Location:
   `.ufo/waves/round-23/w1-spec.json` item `ScribeQuality`.
3. **D7 is unmeasured this round, so a green C1 can coexist with D7 open.** No frozen key
   (K1–K4) reads `corpus/QUALITY.md` or the lesson's `captured-by` cells; C3's counter reads the
   knowledge entries and the register only. A `mismatches=0` C1 is therefore not evidence about
   D7. Location: `preregistration.txt:28-45`.
4. **The criterion, if drafted, lands nowhere.** The plan's delivery is
   `.ufo/waves/round-23/w1/ScribeQuality.md` (a wave seat report), while `LEARNING.md` step 3 asks
   for the criterion in `corpus/QUALITY.md` citing the lesson. No r23 item holds write authority
   for that file, so closure depends on an L1 append that the spec does not name.
5. **Landing-order constraint the plan would trip.** `tools/souji-landing-gate.py:922` lists
   `corpus/QUALITY.md` among the files whose repo-relative path tokens are resolved at REV
   (`LG-DANGLING-PTR`, Q31). A Q54 `check` cell naming a fixture or tool path that does not exist
   at the landing revision is a landing-gate finding, so the criterion and the bytes its check
   names must land in the same commit.
6. **M17's own `Flip` is the repair the round skipped.** `corpus/lessons/round-22.md:395-398`
   already states the next predicate revision "should require the named heading to appear in the
   snapshot (fixture: a Gate naming `§ OPTIONS` against a page without one must fail)" — i.e. the
   repair was specified a round ago and never landed; E3 shows it still fails today.

## 3. Exact minimal repair

**File and position.** Append to `corpus/QUALITY.md` after line 122 (`Q53`), as a new section
`## Round 23 criteria` with the established 5-column header (`| id | criterion | applies to |
check | motivating evidence |`) and exactly one row, `Q54`. Append-only: no existing row is
rewritten or superseded (QUALITY.md's own rules-of-this-file paragraph requires that), and no
lesson or spot-check byte changes.

**Wording constraints for the row.**

- The `criterion` cell must state the *class*, not the counter: a `§ <NAME>` locator in an entry
  Gate must match a heading line in one of the snapshots that Gate names; a locator-shaped token
  is not a location. It must carry its bound explicitly — the resolution binds the Gate's snapshot
  *set*, not the individual quote's line, so a section name carried only in prose is outside it.
- The `motivating evidence` cell must cite `corpus/lessons/round-22.md` M17 (the `captured-by: none`
  row) — `LEARNING.md` step 3 and QUALITY's own header require the lesson pointer — and may cite
  this report.
- It must **not** be the uncommitted-work criterion the spec proposes (D1's class, already K4), and
  must not restate any counter's implementation.
- The `check` cell must be one command that discriminates. Two legal shapes, both append-only:
  - **preferred (lands M17's Flip):** extend `tools/souji-gate-check.py` check3 so a `§ <NAME>`
    resolves against the named snapshot's heading lines, emitting
    `check3-locator-absent-from-snapshot`; add one selftest case (a Gate naming `§ OPTIONS` against
    `man7-mv.1.txt` must fail, the committed r23 entry must pass). The cell is then
    `` `python3 tools/souji-gate-check.py --selftest` `` (exit 0, new case present).
  - **zero-tool-change alternative:** commit the 15-line resolver demonstrated in E4 as
    `tests/fixtures/r23-locator-heading.py` and name it in the cell. It must be committed in the
    same commit as the Q54 row (finding 5).

**Commands that prove closure** (all at the landing tip, `REV`):

```
# 1. the criterion exists, once, appended
git show REV:corpus/QUALITY.md | grep -c '^| Q54 '
git diff <base> REV -- corpus/QUALITY.md        # one added section, no changed existing row

# 2. the class is now caught: the mutant that passes today must fail
git show REV:corpus/knowledge/quarantine-staging-no-copy-r23.md \
  | sed 's/§ DESCRIPTION, option --no-copy/§ OPTIONS, option --no-copy/' > /var/tmp/mutant.md
python3 tools/souji-gate-check.py --round-date 2026-10-25 --entries /var/tmp/mutant.md \
  --snapshot-dir census/round-22/attempt2/sources   # must exit nonzero: check3-locator-absent-from-snapshot

# 3. no false positive on the committed entry
python3 tools/souji-gate-check.py --round-date 2026-10-25 \
  --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
  --snapshot-dir census/round-22/attempt2/sources   # must stay exit 0
```

Command 2 is the closure proof: it exits 0 at the lane base (E3) and must exit nonzero after the
repair. Command 1 alone is a record check and would pass on a decorative criterion.

## 4. Filed-evidence and operator-file boundary

The repair is achievable **without** editing filed evidence or operator files. `corpus/QUALITY.md`
is lane-owned and its own rule is append-never-rewrite; `tools/souji-gate-check.py` is a lane tool
and a new revision is a new blob — the r22 receipts keep their own `tool_sha256`, and C2's verifier
compares each receipt against the blob at *its* named revision, so no historical receipt is
invalidated. The r22 lesson and the spot-check lesson stay byte-identical.

If the round refuses the tool edit (the r22 C2 claim measured those tool bytes), the append-only
alternative is the fixture-only check in §3 — still a new file, still no filed byte touched. What
the round must **not** do is the thing the spot-check's D1 already flags: leave the criterion in a
wave report and call D7 closed. `LEARNING.md` step 3's obligation is discharged only by a row in
`corpus/QUALITY.md`.

## Attack log

One counter is ungameable-wrong in a way that matters here, declared not edited: **C1's frozen key
set omits D6, D7 and D8** (`preregistration.txt:28-45`). A round can therefore report
`mismatches=0` on K1–K4 while every finding in the spot-check's §6 that is not D1/D2/D4/D5 remains
open — and D7's own repair is the cheapest of them. The honest report shape is to state that D7's
closure is *unmeasured* by the frozen counters and evidenced only by the §3 commands; do not widen
K1–K4 after data.

Residual risk: my heading resolver binds against the union of snapshots named in the Gate, so a
section name that exists in a sibling snapshot would pass; and E3's mutant is one entry, not a
sweep of every admitted Gate. Neither affects the verdict — the class is uncaptured at the base,
which is all D7 asserts.
