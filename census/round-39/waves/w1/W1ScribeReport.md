# W1ScribeReport — round-39 report shape draft (souji, wave 1)

Seat: `W1ScribeReport`, role scribe, item W1ScribeReport. Lane `souji-shokunin`
(`/home/vgpnk/Projects/shokunin/souji-shokunin`). Contract read first:
`census/round-39/preregistration.txt` (freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`, lane base
`ed30b7f5b77939c9073348d810730bc4f355708d`).

Scope note: the report the shape describes lives at
`/home/vgpnk/Projects/shokunin/.ufo/reports/round-39/souji.md` — fleet-repo bytes, outside this
seat's write scope. The draft therefore lives in this seat note (section **Draft shape** below) and
was exercised in scratch. No fleet file was created, modified or deleted; nothing was committed.

## What the shape is bound to

The contract is executable, not prose: `tools/souji-report-contract.py` (seven predicates) plus
`tools/souji-pre-report-gate.sh --contract` (six gate checks, one of which runs the checker). The six
canonical headings are `SECTION_KEYS` at `tools/souji-report-contract.py:51-58`; the SHONEN rule is
`check_shonen_boxes` (`:153-167`, one box line per `SHONEN.md` box); the trend rule is `check_trends`
(`:169-193`, first token after the label must be one of `VERDICT_TOKENS` at `:49`); the stale-lane
rule is `check_stale_lane` (`:195-205`); the measurement rule is `check_measurements` (`:207-221`,
one table row with a backticked 7-64 hex commit and a second backticked span).

`SHONEN.md` carries four boxes (`SHONEN.md:5,7,9,11`), so the report's `## SHONEN` block must carry
exactly four box lines in that order.

Provenance of the instruments I ran (bytes at the lane working tree when I ran them):

| instrument | sha256 |
|---|---|
| `tools/souji-report-contract.py` | `a19c405a4454670415822f623c0dbac3d641991633b5495f4a62481f1f250ad5` |
| `tools/souji-pre-report-gate.sh` | `acdb88160fb8dea93f06b3276b5dc2d5fa5e85031852e8b3fbb4e76998b7ae66` |

Lane revision: `git rev-parse HEAD` printed `2201778e7736af82e7d8a42dec2494f115bf3923` when I began
and `d4c17557b92fd98044e4c8f0ddc79c6d75701b15` at my last provenance read (the L1 was landing bytes
concurrently; both readings equalled `git ls-remote --exit-code origin refs/heads/master`).

## Commands run, with observed output

Scratch: `S=/fast/scratch/hyaku/souji-r39/W1ScribeReport`, created with `mkdir -p`, `cd "$S"` before
every write, removed at the end (`rm -rf -- "$S"`, verified — see **Scratch** below).

### 1. Checker selftest (the predicates are exercised before I use them)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B tools/souji-report-contract.py --selftest
case-conforming=PASS observed=[] expected=[]
case-empty-code-span=PASS observed=[] expected=[]
case-missing-section=PASS observed=['sections'] expected=['sections']
case-section-order=PASS observed=['sections'] expected=['sections']
case-shonen-no-box-line=PASS observed=['shonen-boxes'] expected=['shonen-boxes']
case-trend-missing=PASS observed=['trends'] expected=['trends']
case-stale-lane-absent=PASS observed=['sections', 'stale-lane'] expected=['sections', 'stale-lane']
case-no-measured-commit=PASS observed=['measurements'] expected=['measurements']
case-no-evidence-pointer=PASS observed=['measurements', 'evidence'] expected=['measurements', 'evidence']
SUMMARY cases=9 pass=9 fail=0
rc=0
```

Verdict: **PASS** — the checker's own nine cases discriminate, including the section-order and
box-count predicates my draft rests on.

### 2. `grep -c '^## SHONEN'` on the draft

```
$ grep -c '^## SHONEN' "$S/souji.md"
1
rc=0
```

Verdict: **PASS** — exactly one canonical heading, which is what the gate's `shonen` check requires
(`tools/souji-pre-report-gate.sh:33-34`).

### 3. Report-contract checker on the draft

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-report-contract.py \
    --report "$S/souji.md" --shonen /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md
check-sections=PASS
check-shonen-boxes=PASS
check-trends=FAIL
detail-trends: missing verdicts: expansion,quality,discernment
check-stale-lane=PASS
check-measurements=PASS
check-claims=PASS
check-evidence=PASS
SUMMARY checks=7 pass=6 fail=1
rc=1
```

Verdict: **PASS as a shape draft, FAIL as a filed report** — and the single failure is the intended
one: the three trend lines carry `<verdict>` placeholders, because a verdict is a measurement and this
seat does not own one. The other six predicates (headings and order, four box lines, stale-lane,
measurement-row grammar, claim ids, evidence pointers) pass on the draft bytes.

### 4. Shape probe — the same bytes with the three placeholder tokens filled

The probe is a syntax probe only: it substitutes `unchanged` into the three placeholder slots to prove
the line grammar parses. It asserts no trend verdict and is not a filed artifact.

```
$ sed -e 's/^- expansion: <verdict>/- expansion: unchanged/' \
      -e 's/^- quality: <verdict>/- quality: unchanged/' \
      -e 's/^- discernment: <verdict>/- discernment: unchanged/' \
      "$S/souji.md" > "$S/souji-shape-probe.md"
$ python3 -B .../tools/souji-report-contract.py --report "$S/souji-shape-probe.md" --shonen .../SHONEN.md
check-sections=PASS
check-shonen-boxes=PASS
check-trends=PASS
check-stale-lane=PASS
check-measurements=PASS
check-claims=PASS
check-evidence=PASS
SUMMARY checks=7 pass=7 fail=0
rc=0
$ grep -c '^## SHONEN' "$S/souji-shape-probe.md"
1
```

Verdict: **PASS** — the draft's shape is contract-conformant; only data cells remain, and the checker
names exactly which ones (`trends`).

### 5. Report-contract gate (the pre-filing gate, `--contract`)

```
$ bash .../tools/souji-pre-report-gate.sh \
    --lane /home/vgpnk/Projects/shokunin/souji-shokunin --branch master \
    --report "$S/souji.md" \
    --prereg /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/preregistration.txt \
    --shonen /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md --contract
check-tip=PASS
check-report=PASS
check-shonen=PASS
check-clean=FAIL
detail-clean:  M census/round-39/c3-counter.py
 M tests/fixtures/r39-citation-rev.py
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
check-prereg=PASS
contract-check-sections=PASS
contract-check-shonen-boxes=PASS
contract-check-trends=FAIL
contract-detail-trends: missing verdicts: expansion,quality,discernment
contract-check-stale-lane=PASS
contract-check-measurements=PASS
contract-check-claims=PASS
contract-check-evidence=PASS
contract-SUMMARY checks=7 pass=6 fail=1
check-report-contract=FAIL
rc=1
```

The same command on the probe reads `contract-SUMMARY checks=7 pass=7 fail=0` and
`check-report-contract=PASS`, `check-clean=FAIL`, `rc=1`; a second run minutes later listed a smaller
dirty set (`?? census/round-39/make-cells.py` and four `?? census/round-39/records/*.txt`), because
other seats were still landing.

Verdict: **the contract arm PASSES on the shape; the gate is not green** — `check-clean` names
lane paths that are other seats' in-flight bytes at my run time (`census/round-39/c3-counter.py`,
`tests/fixtures/r39-citation-rev.py`, untracked receipts). That is the L1's landing precondition, not
a defect of the shape: no report may be filed while `check-clean` names a lane path.

### 6. Negative probes — the predicates my draft relies on are load-bearing

```
$ grep -v 'No cross-domain bleed' "$S/souji-shape-probe.md" > "$S/probe-missing-box.md"
$ python3 -B .../tools/souji-report-contract.py --report "$S/probe-missing-box.md" --shonen .../SHONEN.md
check-sections=PASS
check-shonen-boxes=FAIL
detail-shonen-boxes: box lines=3 expected 4
...
SUMMARY checks=7 pass=6 fail=1
rc=1

$ <probe-order.md: Trend verdicts section moved after Stale-lane>
check-sections=FAIL
detail-sections: heading order [7, 23, 33, 45, 71, 51] not canonical
...
SUMMARY checks=7 pass=6 fail=1
rc=1
```

Verdict: **PASS** — dropping one box line fails `shonen-boxes` (3 vs 4) and swapping two canonical
sections fails `sections` on order, so the draft's two most fragile rules are enforced, not decorative.

### 7. The gate on the real, not-yet-filed report path

```
$ bash .../tools/souji-pre-report-gate.sh --lane .../souji-shokunin --branch master \
    --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-39/souji.md \
    --prereg .../census/round-39/preregistration.txt --shonen .../SHONEN.md --contract
check-tip=PASS
check-report=FAIL
check-shonen=FAIL
detail-shonen: found 0 headings, expected 1
check-clean=FAIL
...
check-prereg=PASS
check-report-contract=FAIL
detail-report-contract: checker missing (...) or report empty
rc=1
```

Verdict: **PASS (the gate is non-vacuous)** — nothing is filed at the r39 report path yet
(`ls .ufo/reports/round-39/` shows sibling lanes' reports only), and the gate reports that rather
than passing silently. `check-tip=PASS` confirms the lane branch equals its remote ref at run time.

## Draft shape

The six canonical sections appear in `SECTION_KEYS` order; `## SHONEN`, `## Errata for round 38's
report` and `## Pre-filing checks` are additional headings (the checker constrains only the six and
requires exactly one `## SHONEN`). Every `<…>` is a data cell, never a number this seat invents.

````markdown
# souji — round 39 (hyaku run 11, attempt 1)

Lane `souji-shokunin`; base `ed30b7f5b77939c9073348d810730bc4f355708d`; freeze
`b769bfb84a264d8b284c09bc211d99f39a3e9126`; landing `<landing-40hex>`. Round shape: one v2 wave,
`<seats>` seats, `<dead>` dead, inside the 64–128 band — the dead count is copied from the waves
table in **Work performed**, never stated as a bare pair.

## Work performed

> INSTRUCTION: one paragraph per claim C1/C2/C3 giving its axis, its frozen predicate and an
> `Evidence:` pointer to a committed receipt at the landing revision; then one wave-1 paragraph
> naming the seat count, the dead count, the role mix, the attack share and every finding that
> changed an artifact, each finding by seat name.

- **C1 — calibration 7.** <claim paragraph, predicate quoted from `census/round-39/preregistration.txt`>
  Evidence: `census/round-39/records/<c1-after>.txt`.
- **C2 — operability 8.** <claim paragraph>
  Evidence: `census/round-39/records/<c2-after>.txt`.
- **C3 — coverage 8.** <claim paragraph>
  Evidence: `census/round-39/records/<c3-after>.txt`.
- **Wave 1 (`<seats>` seats, `<dead>` dead).** <role mix; attack share; reports
  `.ufo/waves/round-39/w1/`; findings that changed artifacts, by seat>.

## Landed changes

> INSTRUCTION: one table row per commit in `<base>..<landing>` — the range the round actually
> landed — each row naming the change, its `LOG.md` entry and the 40-hex commit; the table covers
> every commit in the range and no cell is a placeholder.

| change | LOG entry | commit |
|---|---|---|
| <change> | `LOG.md` §Round 39 <entry> | `<40hex>` |

## Before -> after measurements

> INSTRUCTION: one row per claim carrying the base reading from its committed control receipt, the
> landing reading, the exact counting command and the 40-hex revision the reading was measured at;
> every cell quotes a receipt or a command, and the revision cell is a hash.

| claim | axis | before (base `ed30b7f`) | after (landing) | counting command | measured commit |
|---|---|---|---|---|---|
| C1 | calibration 7 | `<c1-before SUMMARY line>` | `<c1-after SUMMARY line>` | `python3 -B census/round-39/c1-counter.py --root <lane> --rev <landing>` | `0000000000000000000000000000000000000000` |
| C2 | operability 8 | `<c2-before SUMMARY line>` | `<c2-after SUMMARY line>` | `python3 -B census/round-39/c2-counter.py --root <lane> --rev <landing>` | `0000000000000000000000000000000000000000` |
| C3 | coverage 8 | `<c3-before SUMMARY line>` | `<c3-after SUMMARY line>` | `python3 -B census/round-39/c3-counter.py --root <lane> --rev <landing>` | `0000000000000000000000000000000000000000` |

## Sources & frontier

> INSTRUCTION: give the census counting command with both exit codes and the before → after row
> count, then the rows added by tier, the rows touched old→new, the frontier rows advanced, the
> curation note and the assimilation verdict.

## Trend verdicts

> INSTRUCTION: exactly one line per trend in this order, each opening with the trend word, a colon
> and one verdict token from improved | harmed | unchanged | unprovable-but-better, then an em dash
> and the evidence that decides it.

- expansion: <verdict> — <evidence pointer>
- quality: <verdict> — <evidence pointer>
- discernment: <verdict> — <evidence pointer>

## Errata for round 38's report

> INSTRUCTION: one entry per fleet-side half of a routed r38 defect the lane cannot edit in place —
> the r38 report's own bytes — each entry quoting the false line verbatim, giving the corrected
> reading, and pointing to the lane artifact that carries it; the round's write scope excludes
> `.ufo/reports/round-38/`, so the correction lives here and in the r39 lesson.

- **E1 — r38 report's dead-seat line (R2).** The r38 opening line reads "4 + 0 dead"
  (`.ufo/reports/round-38/souji.md:7`), which its own waves table contradicts; the corrected reading is the one `census/round-39/c1-items.tsv` row
  `R39-C1-02` binds (tokens `w1-reports=42/42`, `w2-reports=32/32`, `dead=0`,
  `W2MutBattery`, `settled-after-closure`) and the lane bytes are
  `corpus/lessons/round-38.md` at anchor `R39-C1-02`.
- **E2 — r38 report's Landed-changes table (R15).** The r38 spot-check records that 9 of the 21
  commits in `ca4369a..fcdecaa` are named nowhere in the table, whose last row's commit cell is the
  placeholder `<integration>` (`.ufo/reports/round-38/souji.md:92`); the nine commits are those
  `census/round-39/c1-items.tsv` row `R39-C1-15` enumerates, and the covering table is
  `corpus/lessons/round-39.md` at anchor `R39-C1-15`.

## SHONEN

> INSTRUCTION: exactly four box lines, one per box of `SHONEN.md` in its order, each `- [~]` (or
> `- [x]` only where a non-author can check it) with the box text and the pointers that make it
> checkable.

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — <pointers>
- [~] At least one end-to-end domain task executed and logged in LOG.md — <pointers>
- [~] Instructions executable by an agent without oral context — <pointers>
- [~] No cross-domain bleed (PROVINCE.md still accurate) — <pointers>

## Stale-lane

> INSTRUCTION: one line stating whether another mission of this lane is open, with the evidence
> that decides it.

Stale-lane: <yes|no> — <reason and evidence pointer>

## Pre-filing checks

> INSTRUCTION: run both commands after the report bytes are final and before filing; paste their
> output lines into the filing note, and do not file while `check-clean` names a lane path.

```
grep -c '^## SHONEN' /home/vgpnk/Projects/shokunin/.ufo/reports/round-39/souji.md      # must print 1
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-pre-report-gate.sh \
  --lane /home/vgpnk/Projects/shokunin/souji-shokunin --branch master \
  --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-39/souji.md \
  --prereg /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/preregistration.txt \
  --shonen /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md --contract                # rc 0
```
````

Heading map as the checker sees it (draft bytes, `grep -n '^## '`):

```
8:## Work performed
24:## Landed changes
34:## Before -> after measurements
46:## Sources & frontier
52:## Trend verdicts
62:## Errata for round 38's report
80:## SHONEN
91:## Stale-lane
98:## Pre-filing checks
```

## Findings for the L1

1. **The errata section is the only place R2's and R15's fleet-side halves can close.** The
   preregistration's `Not claimed` block says so (`census/round-39/preregistration.txt:107-110`), and
   the lane's C1 rows bind only lane bytes: `R39-C1-02` anchors in `corpus/lessons/round-38.md`
   (`census/round-39/c1-items.tsv:8`), `R39-C1-15` in `corpus/lessons/round-39.md`
   (`:21`). Neither row can reach `.ufo/reports/round-38/souji.md:7` or `:92`.
2. **The r38 opening line is the exact sentence R2 convicts**, quoted above verbatim from
   `.ufo/reports/round-38/souji.md:7` (`4 + 0 dead`); its waves table on the same file says dead 0 in
   both waves. The draft's header instruction forbids repeating the bare pair, so the errata entry
   and the header cannot contradict each other.
3. **`<integration>` is a live placeholder in the r38 table** (`.ufo/reports/round-38/souji.md:92`);
   the draft's Landed-changes instruction forbids a placeholder commit cell in r39, which is R15's
   rule stated as a shape constraint rather than a reminder.
4. **Do not file while `check-clean=FAIL`.** My runs show the gate is sensitive to exactly this
   (two different dirty sets within minutes, both other seats' bytes).

## Disclosed limits

- **I measured no claim.** The draft's `trends` predicate fails on purpose; the `0000…0` cells in the
  measurements table are placeholders whose only function is to prove the row grammar parses
  (`check-measurements=PASS`). A zero hash is not a citation and no verdict line in this note is a
  trend verdict for round 39.
- **The shape is checked against today's checker bytes.** `tools/souji-report-contract.py` and
  `tools/souji-pre-report-gate.sh` are live files the L1 may still land; the sha256 pair above pins
  what my verdicts describe. If either changes, re-run the probe before trusting the shape.
- **The gate could not read a filed report**, because none exists (section 7); the shape is verified
  on a scratch copy, not on the real path. The `check-tip` reading is the only gate check that ran
  against the real lane state.
- **`## Pre-filing checks` is my addition, not a contract requirement.** The checker ignores it (its
  fenced block is masked); it exists so the filing step cannot be remembered wrongly.
- **Seat count and dead count are placeholders in the header.** The waves table rule is what the
  shape enforces; the numbers are wave-1 results I do not own.

## Scratch

`/fast/scratch/hyaku/souji-r39/W1ScribeReport` held `souji.md`, `souji-shape-probe.md`,
`probe-missing-box.md`, `probe-order.md`. Removed with `rm -rf -- "$S"`; `ls -d` afterwards reports
the path absent. No tree of mine is left on disk.

## Tool installs

None. `python3` (host), `git`, `grep`, `sed` were already present; pacman stayed paused and no
`uv tool`/`npx` install was needed.

## Verdict

**PASS for the seat's deliverable**: the six required sections, their order, one instruction sentence
per section, the four-line SHONEN block, the trend-verdict line grammar, the stale-lane line, the
errata section for R2/R15's fleet-side halves, the `grep -c '^## SHONEN'` check and the gate command
are all present in the draft and enforced by the lane's own checker (7/7 on the shape probe, 6/7 on
the unfilled draft with the one failure being the data the L1 must supply). **Not green for filing**:
`check-clean=FAIL` on other seats' in-flight bytes, and no report exists at the r39 path yet.
