# SwarmCritic54 — round 29: causal separability and axis attribution (attack seat)

Lane `souji-shokunin`; base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; prereg freeze
`b8cb4b31ce80e2e3314b88e85d40ea9873180804`. Read-only seat: this report plus a scratch clone
under `/var/tmp/souji-r29-SwarmCritic54.L7o6ch/` (removed at seat end). No lane bytes changed.

## Status

STATUS: PASS — assigned attack executed on ten synthetic partial-landing states; separability
holds at the counter level, but two landing blockers and one counter-gaming path are proven with
measured counterexamples (findings 1-3), plus one ordering rule the L1 must follow (finding 7).

## Evidence

Reading anchors (verbatim, opened this run; no pipe characters in any quoted span):

- `/home/vgpnk/Projects/shokunin/AXES.md:31` — "**causally separable** — each verifiable without the others having landed —"
- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/records/preregistration.txt:7` — "drop the failing records only -> uncovered 14 (fails)"
- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/records/preregistration.txt:9` — "the C1 counter at the C3 landing commit still `mismatches=0`"
- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/records/preregistration.txt:13` — "each counter is evaluable at its own landing commit without the others"
- `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:28` — "E09 invalid recheck (ISO date, NNd, or symbolic cadence)"
- `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:582` — "function symbolic(s) { return s ~ /^[A-Za-z][A-Za-z0-9 _-]*$/ }"
- `census/round-29/stale-statements.tsv:2` — phrase `2 malformed newline-path records` at `SCORECARD.md:23`
- `census/round-29/stale-statements.tsv:1` — phrase `two newline-containing path rows are improperly formatted` at `LOG.md:1758`
- `.ufo/waves/round-29/w1/deliver-sources-rows.md:44` — recheck cell `on-release — re-read the man-pages 6.x \`statx(2)\` page`

Method: scratch clone at `b8cb4b3`, throwaway identity configured inside the clone only, then one
branch per partial landing. Every counter was read as frozen (identical tool blobs as the lane's),
against full-40 revisions with `--root <scratch>`. The two C1/C3 landing patches were built only
from delivered files in `.ufo/waves/round-29/w1/` (rows at `deliver-sources-rows.md:44-47`, entries
`deliver-duplicate-verdict-identity.md` / `deliver-duplicate-verdict-byte-equality.md`, corrections
`deliver-c1-corrections.md`, README row `deliver-readme-f3-row.md`, snapshots `w1/sources/`,
gate inputs `w1/assimilation/quarantine-slice` + `deliver-slice-verdicts.tsv`, cell edits
`deliver-c1-usedby-changes.tsv`). The C2 state is synthetic on purpose (finding 4): the receipt is
regenerated from committed blobs with GNU-escaped records and a `symlinks.tsv`.

Separability matrix (each cell measured this run; `f/u/fv` = failed/uncovered/floor_violations):

| state (scratch commit) | C1 mm | C2 f/u/fv rc | C3 entries / rows / coverage |
|---|---|---|---|
| base `691dd29` | 10 (k1=6 k2=4) rc1 | 152/14/0 rc1 | 0 / 139 / 13-13 mm0 |
| C1 only `2e959a2` | 0 rc0 | 152/14/0 rc1 | 0 / 139 / 13-13 mm0 |
| C3 only `ded95a0` | 10 rc1 | 152/14/0 rc1 | 2 / 143 / 15-15 mm0 |
| C3 only, recheck fixed `b40a41a` | 10 rc1 | 152/14/0 rc1 | 2 / 143 / 15-15 mm0; census rc0 |
| C2 only (receipt rewrite) `f8c7b31` | 10 rc1 | 0/0/0 rc0 | 0 / 139 / 13-13 mm0 |
| C2 only, records dropped, no symlinks.tsv `da5af84` | — | 0/14/0 rc1 | — |
| C1 then C2 `f26e730` | 0 rc0 | 0/0/0 rc0 | 0 / 139 / 13-13 mm0 |
| C1 then C3 fixed `7bd175f` | 0 rc0 | 152/14/0 rc1 | 2 / 143 / 15-15 mm0; census rc0 |
| C1 + C3 + round-29 tail appends `50a9db9` | 0 rc0 | — | — |
| C1 + newest-first SCORECARD insert `4c582fb` | 1 (K2 moved) rc1 | — | — |

Representative commands (run against the scratch clone; `$C` = clone root, `$L` = lane root):

```
python3 -B $L/tools/souji-registry-agreement.py --root $C --rev <rev> --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
python3 -B $L/census/round-29/c2-counter.py --root $C --rev <rev>
git -C $C grep -lE '^ground: F3' <rev> -- corpus/knowledge/ | wc -l
git -C $C show <rev>:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
python3 -B $L/tools/souji-coverage-agreement.py --root $C --rev <rev>
python3 -B $L/tools/souji-gate-check.py --root $C --round-date 2026-10-25 --entries <two entries> --snapshot-dir census/round-29/sources --slice census/round-29/records/quarantine-slice --slice-verdicts census/round-29/records/slice-verdicts.tsv
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $C/corpus/SOURCES.md
```

Base reproduction of the frozen numbers, in the lane: C1 `SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29…`
rc 1; C2 `r26 records=1382 failed=152 uncovered=14 floor_violation=0` with
`SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0` rc 1. Both match the prereg.
`python3 -B tools/souji-axis-check.py --prereg census/round-29/records/preregistration.txt --scorecard SCORECARD.md`
prints `claims=3 flags=0` rc 0 — the declared axis/surface pairs and the lowest-axis obligation pass.

## Findings

### 1. BLOCKER — the four appended C3 rows are invalid registry rows under the census (E09 ×4)

- Counterexample: the delivered S216-S219 recheck cells carry prose after the cadence, e.g.
  `on-release — re-read the man-pages 6.x \`statx(2)\` page` (S216, S218),
  `365d — re-fetch the author-hosted PDF, compare its sha256, and re-read § Abstract and § 2` (S217),
  `on-release — re-read the man7 cmp(1) page after a diffutils release` (S219). The census accepts
  only ISO, `NNd`, or a symbolic token in `^[A-Za-z][A-Za-z0-9 _-]*$` (`scripts/sources-census.sh:582`,
  branch at `:665`), so all four rows yield `E09` and the registry exits 1.
- Evidence: scratch state `ded95a0` (base + the four rows, two entries, snapshots, README F3 row,
  gate inputs): `validate --file $C/corpus/SOURCES.md` emitted
  `E09 S216 recheck=on-release — re-read the man-pages 6.x statx(2) page` … `E09 S219 …`, rc 1.
  With the four cells reduced to the bare cadence (state `b40a41a`): rc 0, zero `E` lines, census
  `rows 143`, and every other C3 counter unchanged (`2 / 143 / 15-15 mm0`, gate
  `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`). No `E11`/`E04`/`E08` appears, so the rows
  and used-by paths are otherwise well-formed; the delivered rows measure 11 columns (13 splits).
- Impacted axes: coverage (C3's own acceptance `sources-census.sh validate … rc 0` is red at its
  landing commit) and calibration (the delivery's "cells left unchanged" list omits `recheck`).
- Smallest safe correction: at landing set the four recheck cells to `on-release`, `365d`,
  `on-release`, `on-release`. Nothing is lost: each entry's front-matter `recheck:` line already
  carries the re-read instruction. Log the four old→new cell changes as the prereg requires.
- Scope note: the prereg command is `validate --root <fleet> souji` (lane worktree); I ran `--file`
  on the same bytes because the rows are not landed yet. The rule is cell-local (`:663-667`), so the
  finding transfers. Location: `.ufo/waves/round-29/w1/deliver-sources-rows.md:44-47`.

### 2. BLOCKER — a round-29 SCORECARD section placed by the file's own convention kills C1

- Counterexample: `SCORECARD.md` records rounds newest-first (Round 28 at `:17`, Round 27 at `:27`).
  Inserting a six-line "### Round 29 measurements" section above Round 28 moved the frozen phrase
  from `SCORECARD.md:23` to `:29`; K2 then reported `K2 phrase-moved-or-edited SCORECARD.md:23`
  with `SUMMARY k1=0 k2=1 mismatches=1` rc 1 (state `4c582fb`). The kill rule names this exact
  class ("a repair that edits a stale phrase in place (K2 flags phrase-moved-or-edited)"), so a
  correct C1 repair plus a conventional bookkeeping insert is scored as a dead claim.
- Evidence: the negative state above; and the positive variant (state `50a9db9`: Round 29 section
  and a round-29 LOG line appended at the two file tails) keeps the phrase at `SCORECARD.md:23`,
  `LOG.md:1758` intact, and returns `SUMMARY k1=0 k2=0 mismatches=0` rc 0.
- Impacted axes: calibration (C1 kill rule), no other axis.
- Smallest safe correction: every round-29 addition goes at the file tail. No insertion above
  `LOG.md:1758`, `SCORECARD.md:23`, `corpus/lessons/round-28.md:22/:40`. Record the deliberate
  newest-first deviation in the round-29 SCORECARD section and in LOG. The C1 correction blocks may
  sit before or after the round-29 section at the tail; K2 only needs marker-after-phrase.

### 3. C3's acceptance depends on C1 having landed (separability holds for evaluation, not acceptance)

- Counterexample: C3's frozen acceptance includes "the C1 counter at the C3 landing commit still
  `mismatches=0`" (`preregistration.txt:9`). At the C3-only landing commit `ded95a0` the C1 counter
  reads exactly the base ten (`k1=6 k2=4 mismatches=10`), so the clause fails unless C1 precedes.
  The Q59 line (`:13`) says "each counter is evaluable at its own landing commit without the others",
  which is true only of evaluation: all five C3 counters hit target at `ded95a0`.
- Evidence: measured both sides — C3-only `10`; C1-then-C3 fixed (`7bd175f`) `0`. The coupling is
  one-directional: C1-only leaves C3 at `0 / 139 / 13-13 mm0`, so C1 is independently measurable.
  Residual shared read: `tools/souji-gate-check.py` step 5 resolves the entries' `source:` ids
  against the worktree `corpus/SOURCES.md` (the tool has no `--rev`), i.e. it reads a file C1 edits;
  it passed in both the C1-absent and C1-present trees, so nothing is required beyond the pre-report
  gate's clean-tree precondition.
- Impacted axes: coverage (C3 acceptance) and calibration (C1 final-tip reading). No axis is harmed;
  the defect is a landing-order coupling, not a predicate error.
- Smallest safe correction: no amendment. Order the commits C1-records, then C3; take C1's
  "again at the final tip" reading at/after the C3 commit. The clause is stricter-only and is
  satisfiable exactly as frozen.

### 4. ATTACK — the C2 counter is green with the instrument byte-identical: it measures the receipt, not instrument-acquisition

- Counterexample: state `f8c7b31` changes only `census/round-26/waves/manifest.sha256` and a new
  `census/round-26/waves/symlinks.tsv` (2 files). `tools/souji-wave-evidence-capture.sh` is blob
  `c63a9f0…` at both `f8c7b31` and base. The counter prints
  `r26 records=1231 failed=0 uncovered=0 floor_violation=0` and
  `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0` rc 0 — the defect's 152 failed
  records are simply absent from the rewritten manifest.
- Junk control defeated: the frozen junk control is "drop the failing records only -> uncovered 14
  (fails)" (`preregistration.txt:7`). Measured (`da5af84`, no `symlinks.tsv`):
  `records=1230 failed=0 uncovered=14` rc 1. Adding the 14-line `symlinks.tsv` (`f8c7b31`) flips it
  to `uncovered=0` rc 0. The floor cannot catch it either: committed regular files minus
  `manifest.sha256` is 1230, the floor value, so "drop everything not committed" lands on the floor
  with zero margin (1231 with `symlinks.tsv` included as a record). Nothing in the frozen counter
  reads the improved tool's `excluded.tsv`, where the real fix accounts those 152 paths.
- Impacted axes: operability (declared surface `instrument-acquisition`; the counter evidences a
  receipt) and calibration (a receipt that silently loses 152 captured paths contradicts the
  receipt's own claim).
- Smallest safe correction (stricter-only, no predicate change): C2's landing note must evidence the
  instrument, not only the counter — (a) quote the fixture run `cases=N pass=N control=TAMPER-REJECTED`
  with N>6 and the nested-`.gitignore` / ignored-name / symlink cases, and (b) show the committed r26
  receipt accounting for the 152 dropped records (the tool's `excluded.tsv` rows or
  `deliver-c2-152-classification.tsv` as landed), so the counter's green cannot stand alone.

### 5. K2 is content-blind; after the r26 recapture the corrections are true only through their revision qualifier

- Counterexample: at the C1-then-C2 tip `f26e730` the C1 counter reads `k1=0 k2=0 mismatches=0`
  while the tip's r26 receipt holds 1231 records with 0 absent paths, and the landed corrections
  still say the receipt holds 1382 records with 152 absent — true only because every correction line
  starts with "measured at rev 691dd292…". K2 checks just the `R29-CORRECTION ` prefix and the
  `file:line` tag after the phrase (`tools/souji-registry-agreement.py:95-97`), so a landing that
  dropped the qualifier would pass K2 while the sentence was false at the tip.
- Evidence: measured at `f26e730` (C1 counter 0; `git show <rev>:census/round-26/waves/manifest.sha256`
  has 1231 records; the correction lines are present in both `SCORECARD.md` and `LOG.md`).
- Impacted axes: calibration.
- Smallest safe correction: land the four correction blocks verbatim (qualifier included) and make
  C2's supersession note name the r26 receipt and cross-reference those `R29-CORRECTION` lines.
  Cite the tip commit in C1's final-tip reading. C1-before-C2 and C2-before-C1 both satisfy this;
  the cross-reference is what makes the tip coherent.

### 6. C1's `bookkeeping-file` label holds only if the fixture stays out of the measured commit

- Counterexample: at the prereg commit `b8cb4b3` the instrument exists
  (`tools/souji-registry-agreement.py`) but its fixture does not (`git ls-tree … -- tests/fixtures`
  lists `r28-wave-evidence-capture.sh`, no `r29-registry-agreement.py`). The delivered fixture is
  the kill rule's anti-vacuity check (12 cases plus an always-zero-emitter control). If it lands in
  the same commit as the record repair, the "bookkeeping-file" commit also ships an executable test —
  a surface mix no declared `surface-class` covers, and one `tools/souji-axis-check.py` cannot see
  because R2 trusts the declared label.
- Evidence: my synthetic C1 landing (`2e959a2`) touches exactly `LOG.md`, `SCORECARD.md`,
  `corpus/SOURCES.md`, `corpus/lessons/round-28.md` — 4 files, no executable — and reaches
  `k1=0 k2=0 mismatches=0`. The C1 tool itself predates the repair by one commit, which is the lane's
  instrument convention (the counter is the measuring device, not the claim).
- Impacted axes: calibration (axis-of-surface honesty).
- Smallest safe correction: land `tests/fixtures/r29-registry-agreement.py` in its own commit (before
  or after the records repair), never inside the C1 measured commit; name it as measurement surface
  in the round report. The lane has landed a tool with its fixture in one commit before — the r16
  subject reads "landing gate, its held-out fixture" (commit `7a79dc2`) — so the shape is not new;
  the point here is that for C1's declared `bookkeeping-file` the measured commit must stay
  records-only.

### 7. Ordering rule the L1 must follow (composite of findings 2, 3, 6)

1. Fixture commit: `tests/fixtures/r29-registry-agreement.py` — separate from the measured commit.
2. C1 records commit: the six `used-by`/`status` cell edits from `deliver-c1-usedby-changes.tsv`
   plus the four correction blocks verbatim, all appended at file tails. Measure C1 here; must be
   `mismatches=0` rc 0. This commit must precede step 3.
3. C3 landing commit: rows S216-S219 with bare `recheck` cadence, the two entries, the README F3 row,
   the snapshots and gate inputs. Measure entries `2`, rows `143`, coverage `15/15 mm0`, gate `ok=2`,
   census `rc 0`, and C1 counter `0` at this same commit (the frozen C3 clause).
4. C2 landing commit: improved tool + extended fixture + recaptured r26 (+ `symlinks.tsv` + the 152
   accounting). Counter-independent of steps 2-3, so it may come before or after them; its note
   carries the fixture run, the accounting for the 152, and the r26 supersession cross-reference
   (findings 4, 5).
5. r29 capture commit after the wave evidence is final: C2 counter must show `manifests=4` with zeros.
6. Final tip: re-measure C1 (`0`) and the C3 targets at the tip commit and cite it. At every step,
   nothing is inserted above the four frozen anchors.
   Verified composite end state for steps 2+3: `7bd175f` — C1 `k1=0 k2=0 mismatches=0`, C3
   `2 / 143 / 15-15 mm0`, census rc 0, C2 still at its base numbers (not yet landed).

## Attack log

- ATTACK-1 — C2 counter gaming (finding 4). Status: proven, unfixable after data without an
  amendment; the frozen counter cannot distinguish instrument repair from receipt rewrite, and the
  frozen junk control is defeated by one 14-line `symlinks.tsv`. Impacted axes: operability,
  calibration. Response: no predicate change proposed; the landing note must carry the fixture run
  and the 152-path accounting. Not a reason to reject C2; a reason not to accept its counter alone.
- ATTACK-2 — K2 anchor brittleness and content-blindness (findings 2, 5). Status: proven. Absolute
  `file:line` anchors turn a pure line shift into a kill, and the marker check does not verify the
  revision qualifier. Impacted axis: calibration. Response: landing discipline (tail appends,
  verbatim corrections, cross-referenced supersession), not an amendment.
- ATTACK-3 — declared separability vs the frozen C3 clause (finding 3). Status: proven against
  `AXES.md:31` and `preregistration.txt:13`, resolved by ordering. Impacted axes: coverage,
  calibration. Response: C1-before-C3; the clause is stricter-only and remains in force unchanged.

Not attacked / out of scope: the content of the two F3 entries and the S216-S219 wording (other
seats' remit), the capture tool's internals, `considerthese/` (absent), quarantine and K5.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmCritic54.md` — this report. No other file written; scratch
  `/var/tmp/souji-r29-SwarmCritic54.L7o6ch/` removed at seat end. No tool installs or upgrades.
