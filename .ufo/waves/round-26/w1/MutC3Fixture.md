# MutC3Fixture — mutation test of the C3 fixture design (round 26, wave 1)

## Status
STATUS: PASS — mutation probe executed on the w1 C3 pair (tools/souji-axis-check.py +
tests/fixtures/r26-axis-check.py). Bleeding finding: the **as-shipped fixture fails its own
frozen K2** (`cases=12 pass=6`), and 5 survivor-class holes remain even after the one-word
fixture correction. All lane bytes untouched (hashes unchanged); scratch lives under
/var/tmp/souji-r26-MutC3Fixture only.

## Evidence
- Baseline, pristine w1 pair (fixture `--tool` w1/souji-axis-check.py):
  `python3 -B .../w1/r26-axis-check.py --tool .../w1/souji-axis-check.py`
  → rc=1, last line `cases=12 pass=6 control=FALSE-GREEN-REJECTED` (` FAIL ` on cases 3, 6,
  7, 8, 9, 10; cases 1, 2, 4, 5, 11, 12 pass).
- Root-cause probe: `parse_scores` on the fixture's own SCORECARD constant → `{'operability': 8, 'coverage': 8}` (calibration 7 row dropped).
- Self-host (read-only, real lane prereg + SCORECARD.md): rc=0, `claims=3 flags=0`.
- Corrected fixture (scratch-only edit: calibration-row prose `lowest non-retired axis` →
  `lowest-scoring axis`): rc=0, `cases=12 pass=12 control=FALSE-GREEN-REJECTED`.
- Mutant matrix under the corrected fixture (rc≠0 ⇒ KILLED):
  - KILLED: R1skip (case 3), R2partial-fixtureexp-only (cases 5/6), R3skip (case 7),
    R4skip (case 8), flaglines-on-stderr (counts-vs-lines consistency), rc-always-0 (rc checks).
  - SURVIVED 12/12 (+ real self-host rc=0): R3hardcoded-lowest, R3retired-rows-counted,
    R2drop-knowledge-registry, R4partial-no-none-dropped, R4filescoped-enumerate.
- Stub-control variants (patched fixture only): stub-exit2, stub-silent-exit2,
  stub-claims9-flags0 → all still `control=FALSE-GREEN-REJECTED`, rc=1.
- Lane bytes: SHA-256 w1/souji-axis-check.py `0805afff…`, w1/r26-axis-check.py
  `220eed2e…` — identical before/after campaign.
- Tooling: no installs (none required). Amends 1-2 touch C1/C2 only; C3's frozen 12-case set
  is unamended.

## Findings
1. **Baseline K2 breach (highest severity)** — the w1 fixture as shipped cannot pass its own
   frozen contract: 6/12 cases fail. Cause: fixture line 60 synthetic calibration row prose
   `synthetic row: lowest non-retired axis` contains the substring `retired`, and the tool's
   score parser (w1/souji-axis-check.py:140,142) skips every line whose text contains
   `retired`. Calibration 7 vanishes; R3 then sees lowest=8 {operability,coverage}, so case 7
   misses its expected R3 flag and clean cases 2/9/10 get spurious R3 flags (also corrupting
   exact_rules cases 3/6/8). One-word fixture fix restores 12/12. Location: w1/r26-axis-check.py:60,
   w1/souji-axis-check.py:142.
2. **R3 computed-vs-hardcoded is untested** — a tool that hardcodes `lowest="calibration"`
   survives all 12 cases and the real self-host. Every fixture world shares one static scorecard
   (calibration 7). Only a second scorecard (lowest ≠ calibration) can kill this. Location:
   w1/r26-axis-check.py:39-46 (single SCORECARD constant).
3. **R2 pair coverage gap** — `knowledge-entry` and `registry-append` wrong-axis violations are
   never exercised (cases cover only fixture-expansion, bookkeeping-file, instrument-acquisition).
   A tool dropping those two mappings from SURFACE_AXIS (w1/souji-axis-check.py:39) survives 12/12
   and self-host.
4. **R4 double hole** — (a) file-scoped enumerate (any `enumerate:` in the file satisfies every
   claim) survives: no two-claim universal-leak case exists; (b) the word list
   (w1/souji-axis-check.py:48) is never exercised by bare `no`/`none` alone — dropping both words
   survives. Probe confirms the pristine tool does flag `none`-only clauses correctly; the case
   set just cannot tell.
5. **Discriminator bypass (unknown-class rename)** — case 1 pins only the literal pair
   (fixture-expansion + operability). Any renamed/typo'd class (e.g. `surface-class: receipt-binding`
   on operability, or `instrument-aquisition` on calibration) is neutral by design → zero flags,
   exit 0, and a partial tool "passes" it. The frozen set *forces* neutrality via cases 7/10
   (exact_rules reject any extra flag). Legal per the frozen R2 text (only the four named classes
   are constrained).
6. **Retired-row counting untested** — no fixture world contains a retired/`retired` row, so a
   tool that counts retired rows is behaviorally identical everywhere (survives 12/12 + self-host).
7. **Control arm is sound** — always-green stub passes only benign single-claim cases 9/10, fails
   case 1 (discriminator), control REJECTED. Exit-2, silent-exit-2, and claims=9 stub variants are
   rejected identically; robust even under a last-line-only comparison that keeps rc + min_flags.
   Optional strengthening: a second control stub exiting 2 (guards rc-dishonest tools); no contract
   change needed.

## Attack log
- A1 — predicate/contract self-attack: the shipped pair cannot produce the frozen K2 literal
  (`cases=12 pass=12`); with the current w1 bytes C3's green-after receipt would fail at landing.
  Report to L1; the fix is a fixture-literal change (stricter/scoped), tool behavior unchanged.
- A2 — discriminator attack: class-rename to an unconstrained token evades R2 entirely
  (receipt-binding-on-operability legal today); case 1 defends only the exact replica literal.
- A3 — survivor propagation: R3hardcoded-lowest, R3retired-rows-counted, R2drop-knowledge-registry,
  R4partial-no-none-dropped, R4filescoped-enumerate all pass 12/12 AND the real self-host
  (`claims=3 flags=0`); none affects the round's own well-formed prereg, so K1 would stay green.
- A4 — control-arm probe: exit-2/silent stubs still rejected (control survives), so no red-arm
  regression from adding a second stub.
