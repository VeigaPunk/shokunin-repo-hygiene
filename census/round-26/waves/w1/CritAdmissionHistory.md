# CritAdmissionHistory — round-26 claim pattern vs r23, r24, r25

Seat: read-only critic, leaf. Lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; reviewed
HEAD `166baa18f808071bc385187691713044a26bd663` (tip moved `c594901` -> `166baa1` during the
review; tool and fixture bytes unchanged across `c594901..166baa1`). Scratch
`/var/tmp/souji-r26-CritAdmissionHistory/` removed before yield. No installs or upgrades.

## Status

STATUS: PASS — review complete. C3 is honestly operability (a new runnable gate; no existing
tool bytes changed) and the closure will most likely admit it; but the round design does not
close the r25 axis-misattribution mode — it narrows it to the one spelling R2 can see — and it
partially repeats the r24 mode (green frozen counter over a narrower surface than the title).

## Evidence

| # | command | output excerpt | revision |
|---|---|---|---|
| E1 | frozen contract, machine block | `C3 / axis: operability / surface-class: instrument-acquisition` | prereg:17-19 at `89e0fce` |
| E2 | `git cat-file -e 0eca7c8:tools/souji-axis-check.py` | fatal, rc 128 (absent at base) | base |
| E3 | `git grep -q surface-class 0eca7c8` and `instrument-acquisition` | rc 1 both (vocabulary introduced by this round) | base |
| E4 | `python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md` | `claims=3 flags=0`, rc 0 | `166baa1` |
| E5 | tip fixture copied to scratch, only `SCRATCH_BASE` patched | `CASE 1 r25-c2-replica-fixture-expansion-on-operability PASS rc=1 claims=1 flags=2 rules=R2,R3`; `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0; the in-tree counter receipt `c3-after.tsv` records the same line | `c594901` fixture, `166baa1` tool |
| E6 | same claim block, `surface-class` swapped | instrument `0`; `bookkeeping-file` `FLAG C3 R2 ... allowed only on 'calibration'`; `measurement` `0`; duplicate `fixture-expansion` then `instrument-acquisition` `0` | synthetic probes |
| E7 | r25-C2 replica and r24-C2 replay | r25 replica `FLAG C2 R2`; r24 replay (`axis: calibration`, `instrument-acquisition`) `FLAG C2 R2` | synthetic probes |
| E8 | `git log --diff-filter=A -- tools/souji-coverage-agreement.py tools/souji-receipt-run.py tools/souji-record-agreement.py` | coverage-agreement added `1efe406` (r24); receipt-run and record-agreement added `4765250` (r23) | lane |
| E9 | all frozen counters at tip | C1 `markers=0`, `headings=17 44 78`; C2 `grounded_f1=2`, `registry_rows=132`; K2 `entries=2 ok=2 fail=0`; K4 `grounded=9 mapped=9 ... kill_violations=0`; C3 `claims=3 flags=0` | `166baa1` |

Located quotes (bytes opened this run):

- `.ufo/waves/round-26/preregistration.txt:153-154`: "Declared axis: operability. Surface
  class: instrument-acquisition (a new runnable gate + falsification fixture)."
- `corpus/QUALITY.md:143` (Q59): "a gate/runnable fixture on an input edge class is an
  operability surface"; and "a self-assessment-file change is a calibration surface".
- `corpus/lessons/round-25.md:10`: "W2 review shows the change is coverage of edge classes,
  not a change to runnable operability".
- `.ufo/waves/round-25/w2/CritC2Classification.md` §3: "Nothing changed about what is
  runnable, how it runs, or what outcome it produces for its declared scope".
- `SCORECARD.md:199`: "Axis misattribution harms calibration; no owned-axis score changes, no admission."

Historical outcome pointers:

- r25: honest stop, no admission (`SCORECARD.md:199`; `/home/vgpnk/Projects/shokunin/.ufo/reports/round-25/souji.md:5,136`).
- r24: no in-lane admission record. The fleet report's last trend verdict is "discernment —
  pending the non-author spot-check"; `SCORECARD.md` planned bullet says "r24 (planned r23) —
  done"; no `CloseSouji24` exists under `.ufo`.
- r23: same shape — `SCORECARD.md` says "r23 — done"; no `CloseSouji23` and no admission
  sentence in `.ufo/reports/round-23/souji.md`. Only r20/r21 carry explicit `CloseSouji` ids
  and "admitted" rows. The assignment's "r23 admitted" is not evidenced by the lane bytes.

Precedent pointers for the axis question:

- new runnable tool claimed on operability: r23 C2 `tools/souji-receipt-run.py`
  (`corpus/lessons/round-23.md:26`); r24 C3 runner refusals (`SCORECARD.md` Round 24 table).
- new or changed record-checking instrument claimed on calibration: r23 C1
  `tools/souji-record-agreement.py` (`corpus/lessons/round-23.md:8-9`); r24 C2
  `tools/souji-coverage-agreement.py` (`corpus/lessons/round-24.md:19`); r25 C1
  coverage-map kill rule (`SCORECARD.md` Round 25 measurements).
- the counter-case: r25 C2 fixture extension on operability, rejected because no runnable
  behaviour changed (round-25 lesson table row C2 and `CritC2Classification`).

## Findings

1. **C3 passes its own R2 literally, and operability is the better reading — but the
   instrument cannot certify that.** The surface changed is a new CLI plus a new fixture
   (`.ufo/waves/round-26/preregistration.txt:17-19`; `tools/souji-axis-check.py`;
   `tests/fixtures/r26-axis-check.py`); existing tool bytes are untouched, and the new command
   runs and produces the stated outcome. That is AXES.md operability ("Runnable artifacts ...
   commands that exist, scripts that run") and the r23-C2 precedent. The r25 test that rejected C2 ("no operability property
   changed") is false here, so this is not a fixture-expansion repeat. The dissenting reading is
   the converse precedent: the three prior instruments of that shape were booked to calibration
   (r23 C1, r24 C2, r25 C1). The tool cannot decide
   between the two because `surface-class` is claimant-declared: adding one line
   (`bookkeeping-file`) flips the same claim to `FLAG R2`, while `measurement`, an unknown
   string, or a duplicate line leaves it at `flags=0` (E6). **Predicted closure verdict: C3
   verifies and is admitted on operability**, with C1/C2 also green at the tip (E9). The
   `calibration-dressed` verdict is live but less likely: it requires the closure to prefer
   the record-checker precedent over the changed-surface rule that r25 used; if taken, C1 and
   C3 count as one claim (AXES.md: two claims on one axis count as one), the round has no
   operability move, and calibration is harmed by attribution — the r25 outcome again.
2. **r25 mode: narrowed to one spelling, not closed.** The tool and fixture catch the exact
   r25 shape: `fixture-expansion` on `operability` flags (E7) and fixture case 1 is the r25
   replica with the stub discriminator (E5). They do not catch the class: `measurement`
   (declared neutral) passes on any axis, an unlisted class passes, and a duplicate
   `surface-class:` line is last-wins, so appending a neutral line masks a prohibited one
   (E6). Fixture case 10 (`tests/fixtures/r26-axis-check.py:206-215`,
   `wellformed-surface-class-and-enumerate`) *blesses* `measurement` as a clean class. A future seat can therefore repeat r25 by relabelling, which is the same
   move the instrument exists to stop. Impacted: operability (gate contract), calibration
   (the gate is a spelling check, not a surface check).
3. **r24 mode partially recurs: title and counter are not the same surface.** The title
   "preregistration axis-of-surface checker" asserts a surface check; R2 checks only that the
   self-declared class is in a five-entry table (`tools/souji-axis-check.py:34-40,110-114`).
   The frozen K1 self-host is one-sided: the same round authored the prereg labels and the
   checker, so `flags=0` is consistency, not an independent audit. This is the R24-M25 pattern
   (a green frozen case set under a broader title), mitigated by the prereg's narrower wording
   ("axis/surface-class consistency"). Impacted: calibration, operability.
4. **Q59 and R2 do not unambiguously agree on the canonical case.** Q59's operability example
   is "a gate/runnable fixture on an input edge class" — text that also describes r25 C2's
   runnable fixture over four input edge classes, which R2 flags as coverage. The discriminator
   R2 relies on ("no runnable entry-command behaviour change") is absent from Q59's wording.
   Q59 landed post-data at `166baa1`; the frozen prereg only names "a QUALITY criterion beside
   Q58". A closure reading Q59 literally could re-legalise the very declaration r26 claims to
   have mined as a mistake (`corpus/lessons/round-26.md:95`). Impacted: calibration.
5. **The v2 wave does surface instrument defects early, but not axis defects.** W1 attack seats
   found the bypasses (`RevC3Design`, `CritClaims`) instead of W2, which is better than r25's
   late catch. No W1 seat challenged C3's axis; `CritClaims` endorsed operability. The design's
   early-attack property is real; its axis check remains a self-check by construction.

## Attack log

- **A1 — self-declared class decides the verdict (impacted: calibration, operability).**
  Counterexample: the identical C3 claim block scores `flags=0` as `instrument-acquisition`,
  `FLAG ... R2` as `bookkeeping-file`, `flags=0` as `measurement`, and `flags=0` with a
  prohibited class masked by a trailing neutral duplicate (E6). Smallest safe correction:
  record in the lesson that R2 is label consistency, not surface truth, and cite the probe;
  do not change the frozen C3 axis, predicate or case set.
- **A2 — the new rule retrospectively condemns r24 C2 (impacted: calibration, operability).**
  Replaying r24's calibration-valued instrument (a new tool of the same shape) as `axis: calibration` plus
  `instrument-acquisition` yields `FLAG C2 R2` (E7). Either r24 C2 was misattributed and never
  caught, or `instrument-acquisition -> operability only` is a new convention, not a derived
  precedent. Smallest safe correction: state the convention change explicitly; do not
  retro-score r24.
- **A3 — the r25 failure is caught only under its exact spelling (impacted: operability,
  calibration).** The neutral/unknown/duplicate bypasses (E6) mean a misdeclared surface class
  passes the gate that exists to catch it. Smallest safe correction: route four new cases
  (neutral-on-operability, unknown class, duplicate key, decoy machine block) to r27 as
  additions; never drop or re-specify the frozen 12 after scoring.
- **A4 — Q59's wording licenses the r25 shape (impacted: calibration).** See Finding 4.
  Smallest safe correction: rewrite Q59's operability example to name the discriminator (new
  or changed runnable entry command versus added test cases over an existing command) as a
  QUALITY-doc edit; no frozen claim predicate changes.
- **A5 — outcome baseline correction (impacted: calibration).** r23 and r24 are "done" in
  `SCORECARD.md`, not "admitted"; no `CloseSouji23/24` appears in `.ufo/reports` or the lane
  corpus (`.ufo/state` was not read). Comparisons
  should use their claim tables and reports, not an admission status the lane does not hold.
