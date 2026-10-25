# Round 26 — axis-of-surface documentation drafts (C3, operability)

Scribe: `ScribeAxisDocs`. Read-only seat: nothing in this file has been inserted into the lane.
Source of truth: `.ufo/waves/round-26/preregistration.txt` claim C3 (+ amendments 1 and 2, neither of which
touches C3). All line anchors below were read in this run from the bytes named; the delivery is
copy-paste text, not a landed edit.

Frozen anchors used throughout:

- `corpus/QUALITY.md` has 142 lines; `## Round 25 criteria` at :137, table header at :139,
  separator at :140, Q57 at :141, Q58 at :142 (EOF).
- `SKILL.md` gate registry: header at :177, separator at :178, last row (`r22-mutation-adequacy`)
  at :223, blank :224, `Sources for this skill` at :225.
- `corpus/lessons/round-25.md`: C2 claim row at :10, boundary paragraph at :13, `## Gate` at :25,
  `### Opened sources and curation (2026-10-25)` at :27, `## Mistakes` at :48.
- `corpus/lessons/round-26.md` does not exist yet (`ls corpus/lessons/` shows no round-26 file).

---

## (a) `corpus/QUALITY.md` — Q59 criterion row

**Lands at:** `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md`, appended at EOF
after existing line 142 (the Q58 row). Insert, verbatim:

```
## Round 26 criteria

| id | criterion | applies to | check | motivating evidence |
|---|---|---|---|---|
| Q59 | Extends Q58's re-derivation rule to axis attribution: every frozen claim declares a surface class, and the class fixes the axis it may be declared on — `bookkeeping-file` on calibration, `knowledge-entry` and `registry-append` on coverage, `fixture-expansion` on coverage, `instrument-acquisition` on operability. A claim whose declared axis disagrees with its surface class is a preregistration defect found before any after-data, never a licence to relabel the axis after scoring; the r25-C2 shape, fixture-expansion frozen on operability and later judged unprovable there, is the motivating failure. | frozen round preregistrations carrying `axis:` and `surface-class:` lines in the machine block | `python3 -B tools/souji-axis-check.py --prereg <round preregistration> --scorecard SCORECARD.md` exits 0 with `flags=0` on the round's own prereg, and the r25-C2 replica (fixture-expansion declared on operability) exits 1 with an R2 FLAG line; R1/R3/R4 are separate predicates of the same instrument and are not claimed by Q59 | corpus/lessons/round-25.md C2 claim row; corpus/lessons/round-26.md R26-M1 |
```

Column mapping: the task names the columns "criterion / applies-to / test / lesson"; the block named
for the shape is the Round 25 criteria block, whose literal header is
`| id | criterion | applies to | check | motivating evidence |` (:139). This row mirrors that header
exactly. Rounds 14–20 use the older `| id | criterion | applies-to | test | lesson |` shape
(:23, :47, :54, :62, :69, :76, :88, :96); do not mix the two.

Placement note (one decision for the integrator): prereg C3 says "a QUALITY criterion beside Q58",
which is satisfied by Q59 immediately following Q58 at EOF. Every round since r14 owns its own
`## Round N criteria` section (headings :45 :52 :60 :67 :74 :86 :94 :107 :116 :124 :131 :137), and no
later round has ever inserted a row into an earlier round's block, so a new `## Round 26 criteria`
heading is the only placement that keeps authorship honest. If the integrator instead reads "beside
Q58" as "inside the Round 25 table", the identical row appended after :142 with no new heading is the
fallback; that alternative attributes the criterion to r25.

Landing preconditions (grounded, not stylistic):

1. No cell may contain a literal or escaped `|` — the r26 C2 kill rule forbids it registry-wide and
   the table is pipe-parsed by eye and by the landing gate. The row above contains none.
2. `corpus/lessons/round-26.md` must exist at the graded revision. `tools/souji-landing-gate.py`
   :905–:990 scans `corpus/QUALITY.md` (:922) as a pointer source with `POINTER_PATH_RE`
   (:141–:146, roots include `corpus/`) and emits `LG-DANGLING-PTR` for any `corpus/...` path absent
   from the tree. A Q59 row citing `corpus/lessons/round-26.md` at a tip without that file is a
   finding. Land the lesson file first, or in the same commit.

---

## (b) `SKILL.md` — Gate-registry rows

**Lands at:** `/home/vgpnk/Projects/shokunin/souji-shokunin/SKILL.md`, gate registry table, appended
after existing line 223 (last row `r22-mutation-adequacy`), before blank :224 and
`Sources for this skill` :225. Column shape copied from :177–:178 (8 columns: name, kind, entry
command, verdict map, self-test command, pinned-value path, write scope, owner). Insert, verbatim:

```
| souji-axis-check | gate | `python3 -B tools/souji-axis-check.py --prereg PATH --scorecard PATH` | 0 clean: stdout `claims=C flags=F` with F=0, every claim's axis owned and non-retired, every surface-class on its class's axis, at least one claim on the lowest-scoring owned axis, no universal quantifier without a counting `enumerate:` line; 1 any flag, one `FLAG <claim> <rule> <detail>` line per finding; 2 could-not-evaluate usage or malformed input (unreadable prereg, no `## MACHINE BLOCK ... END` section, no CLAIM block, a CLAIM without `axis:`, scorecard without a parseable `## Axes` table) | `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py`; no embedded selftest, so a self-test that cannot fail never qualifies this row as a gate | literal case ids, expected exit and required rule id in the fixture; `census/round-26/records/c3-after.tsv` pins `claims=3 flags=0` at the measured revision | reads the named prereg and scorecard only, never writes them; fixture worlds are isolated under `/var/tmp` | souji |
| r26-axis-check | gate | `python3 -B tests/fixtures/r26-axis-check.py --tool PATH` | 0 every frozen case passes and the control arm prints `control=FALSE-GREEN-REJECTED`; 1 any case mismatch, or a stub that always prints `flags=0` is accepted as green; 2 could-not-evaluate missing prerequisite, unusable `--tool` path or usage | same command; the full case set runs in isolated `/var/tmp` worlds, the control arm reruns every must-flag/refuse case through the always-green stub | fixture literal case ids, expected exit, minimum flag count and required rule id per case; `census/round-26/records/c3-after.tsv` | isolated `/var/tmp/souji-r26-axischeck.*` only; reads the selected tool, never a fleet path | souji |
```

Both rows are `gate` under the registry's own rule (:175): a row whose self-test cannot fail is a
`probe` or an `evidence` row, and this fixture's control arm is required to fail a green stub.

**Blocking precondition for these two rows.** They are drafted to the frozen contract, and the frozen
K2 literal is `cases=12 pass=12 control=FALSE-GREEN-REJECTED` from
`python3 -B tests/fixtures/r26-axis-check.py --tool PATH`. The working-tree fixture at this run does
not produce that literal (see Findings in the report and the divergence section below), so the
self-test and verdict cells above would be false if the row landed today. The row must land only
after C3 conforms, or be rewritten to the landed bytes with the divergence disclosed.

---

## (c) Surface-class taxonomy — knowledge-adjacent paragraph

**Lands at:** `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-26.md`, under
`## Gate`, as a single prose paragraph immediately before `### Opened sources and curation
(2026-10-25)` (the r25 equivalent sits between `## Gate` :25 and that subsection :27). Text, one
paragraph:

The rule encodes a four-way taxonomy of the byte surface a claim changes, each class bound to exactly
one owned lane axis: `bookkeeping-file` (a self-assessment or ledger file checked against observed
repo state) to calibration; `knowledge-entry` and `registry-append` (corpus entries and
source-registry rows) to coverage; `instrument-acquisition` (a new runnable gate plus its
falsification fixture) to operability; and `fixture-expansion` (edge-class or fixture work only, with
no change to runnable entry-command behaviour) to coverage. The binding is the mechanical form of the
r25 C2 finding: C2 declared a fixture-expansion surface on the frozen operability axis and the round
judged the result "unprovable on the declared axis" because "W2 review shows the change is coverage
of edge classes, not a change to runnable operability" (`corpus/lessons/round-25.md:10`), with "C2's
actual surface is coverage, which overlaps C3; it cannot be silently reassigned" (:13). The taxonomy
therefore converts a post-hoc judgment into a pre-freeze refusal: a claim may not be frozen on an axis
whose evidence type cannot falsify it, and no axis may be relabelled after scoring. The instrument's
R2 is exactly this mapping (`tools/souji-axis-check.py:34-39`), and the preregistration names it as
"the r25-C2 shape made mechanical" (C3, rule R2). Two further class names, `receipt-binding` and
`measurement`, sit in the implementation's neutral set (`tools/souji-axis-check.py:41`) but in no
frozen claim; they are not part of the encoded taxonomy and are reported as a finding rather than
documented here as a rule.

Quote provenance (all opened this run, all ≤25 words, no `|`):

- `corpus/lessons/round-25.md:10` — "W2 review shows the change is coverage of edge classes, not a
  change to runnable operability" (17 words).
- `corpus/lessons/round-25.md:10` — "unprovable on the declared axis" (6 words).
- `corpus/lessons/round-25.md:13` — "C2's actual surface is coverage, which overlaps C3; it cannot be
  silently reassigned" (15 words).
- `.ufo/waves/round-26/preregistration.txt`, C3 rule R2 — "This is the r25-C2 shape made mechanical."
  (7 words).

---

## Divergences observed (affect the drafts above, not the contract)

Byte-identical at `44531281914ddd200432cdc7dae8ad958c5447e3` (first read) and at
`d6c13b0f00066cbb342fdc50167849a5f1c726e5` (HEAD at close): `git diff --stat HEAD` is empty for both
paths, so both files are committed, not stray. Items 1–6 describe the landed bytes
`tools/souji-axis-check.py` sha256 `14bc9632e88ef58f18108011f6645bd970cd825d0ffc1664369dc60b0d579332`
and `tests/fixtures/r26-axis-check.py` sha256
`2ffc18289fc82b9075ad3580cb9bec6a80384061c7d294b5aa17dbf9ca93c8da`.

1. The fixture runs **11** cases, not the frozen 12, and prints `cases=11 pass=11` with **no**
   `control=` line in its normal mode (`tests/fixtures/r26-axis-check.py:198-220`). The frozen K2
   literal `cases=12 pass=12 control=FALSE-GREEN-REJECTED` cannot be produced by these bytes.
2. `--tool PATH` is accepted but ignored — the tool path is the constant `TOOL`; the stub arm is
   `--stub` instead (`tests/fixtures/r26-axis-check.py:198-201`). The frozen K2 command therefore
   runs and passes silently rather than selecting the file under test.
3. The control arm is a `--stub` rerun, not frozen case 12, and prints `control=FALSE-GREEN-REJECTED`
   only in that mode (`:31`). It does reject the always-green stub (observed: `cases=11 pass=4`,
   `control=FALSE-GREEN-REJECTED`, rc 1), so the control mechanism works even though its spelling and
   arity differ from the frozen case set.
4. The frozen discriminator (case 1 = an r25-C2 replica on operability) is absent; case 1 is instead
   "axis not owned" (R1) (`tests/fixtures/r26-axis-check.py:70-78`). The rule itself does fire: a
   synthetic replica (fixture-expansion on operability, plus one calibration claim) prints
   `FLAG C1 R2 surface-class 'fixture-expansion' declared on 'operability'; allowed only on 'coverage'`
   and `claims=2 flags=1`, rc 1 — observed this run.
5. R4 semantics differ from the frozen text. Frozen: a universal quantifier in claim text *without* a
   same-claim `enumerate:` line is flagged, and case 9 says a universal clause *with* enumerate
   passes. Landed: a missing `enumerate:` is flagged unconditionally, and a quantifier **inside** the
   `enumerate:` value is flagged (`tools/souji-axis-check.py:124-140`), which is the opposite of frozen
   case 9.
6. `NEUTRAL_SURFACES = {"receipt-binding", "measurement"}`
   (`tools/souji-axis-check.py:41`) admits surface classes the frozen contract never names, and a claim
   using one of them bypasses R2 entirely. That is an escape hatch in a rule whose purpose is to make
   the axis/surface binding unbypassable.

The tool's own frozen-prereg check does hold: `python3 -B tools/souji-axis-check.py --prereg
.ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md` printed `claims=3 flags=0`, rc 0.

### Resolution path observed at HEAD (unlanded drafts, executed from `w1/`)

- `.ufo/waves/round-26/w1/r26-axis-check.py` sha256
  `220eed2e15f3154d8a6909cac57f325862d0d472a4e3bab6d88ce48776e1d88d` is the 12-case fixture the
  frozen K2 describes (11 named cases plus a case-12 control arm; case 1 is
  `r25-c2-replica-fixture-expansion-on-operability`). Run against the **landed** tool it prints
  `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0 — the frozen literal, produced today. It is
  not at the landing path, so K2 as written still fails.
- `.ufo/waves/round-26/w1/souji-axis-check.py` sha256
  `0805afff649a2f893542bd7f8e2e676408bb934a7cf3255d13b46d921c3d121b` is the tool draft
  `ExecAxisTool.md` tells the L1 to copy into `tools/`. It scores **6/12** against that same fixture
  (rc 1): case 7 emits no R3 flag at all (rc 0 where rc 1 is required), and cases 3, 6, 8, 9, 10 each
  gain an extra R3 flag. Copying it over the landed tool would break K2. The landed tool (sha
  `14bc9632…`) is the copy that pairs with the 12-case fixture.
- `census/round-26/records/c3-control.tsv` binds rev `d2e6253` with `cases=11 pass=4` and
  `control=FALSE-GREEN-REJECTED`, rc 1 — the round's own control receipt records the 11-case set.
  `c3-after.tsv` (rev `d2e6253`) binds only the K1 half (`claims=3 flags=0`); no committed receipt
  records a `cases=12 pass=12` positive arm.
- R4 discrimination: the landed tool's claim parser reads only `axis`, `surface-class` and `enumerate`
  (`tools/souji-axis-check.py:72`), so a `text:` line is invisible to it; its universal-word scan
  covers the `enumerate:` value (`:120`). Frozen case 8 therefore passes through the
  missing-`enumerate` branch, not through a quantifier match. [INFERENCE, not executed as a mutant:
  a tool with the universal-word scan deleted would still score 11/11 on the landed fixture, because
  no case contains a `text:` quantifier together with an `enumerate:` line and an otherwise clean
  axis/surface pair.]

