# LabAxisRun — C3 runnable probe (axis-check self-host on the round's own prereg)

Report: `.ufo/waves/round-26/w1/LabAxisRun.md`
Scope: hand-simulate the C3 rules R1–R4 on
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/preregistration.txt`, frozen at
`89e0fceeefcf28db313c94120be6d25e03c60094` (amendment 1 included), and state the expected
`claims=3 flags=N`. The frozen counter contract was read first, including the C3 rule text at
prereg:158-176.

## Status

STATUS: PASS — the manual parse and an independently written, spec-exact probe both yield
`claims=3 flags=0`, exit 0, on the round's own preregistration. No rule fires, so there is **no
self-host KILL finding**. Findings 5–8 are instrument/scope observations, not prereg defects;
Finding 7 is a C3-fixture literal outside my item and left to the L1.

## Evidence

Frozen input bytes (identity checked this run):

- `git rev-parse 89e0fce:.ufo/waves/round-26/preregistration.txt` -> `ebe015930576d953af363ef42cbb1a3e09cf7f98`;
  working-tree sha256 `cbfa4c5486118c243fca936d30f23a18c858eca305db84fc3aa4334b3c7d5832`;
  `git diff 89e0fce -- .ufo/waves/round-26/preregistration.txt` -> 0 lines (no post-freeze edit).
- Machine block is prereg:7-20. Claim blocks parsed:

```
7 : ## MACHINE BLOCK (tools/souji-axis-check.py parses exactly this section)
8 : CLAIM C1
9 : axis: calibration
10: surface-class: bookkeeping-file
11: enumerate: bash census/round-26/c1-counter.sh
12: CLAIM C2
13: axis: coverage
14: surface-class: knowledge-entry
15: enumerate: bash census/round-26/c2-counter.sh
16: CLAIM C3
17: axis: operability
18: surface-class: instrument-acquisition
19: enumerate: bash census/round-26/c3-counter.sh
20: END
```

Scorecard input: `SCORECARD.md` axes table rows at both the frozen rev and the live tip —
`:13 coverage 8`, `:14 calibration 7`, `:15 operability 8`; `## Retired` then `None.`
(`:167` at `89e0fce`, `:233` at tip `07f83e6`). Rows `:9-15` are byte-identical at `89e0fce` and at
the tip (line-range sha256 `f351789fab124d3a6a6dc9284d26cc18045f5069a2d728d97ca7ff36549bf346` at tip; a direct
`diff` of the frozen rev's rows `9-15` against the tip's prints nothing, so C1's landing leaves R3's
input unchanged).

### Manual parse (hand simulation)

| rule (prereg line) | requirement, verbatim-scoped | C1 | C2 | C3 | flags |
|---|---|---|---|---|---|
| R1 (`:162-163`) | declared axis is one of the lane's owned, non-retired axes | `calibration` — owned | `coverage` — owned | `operability` — owned | 0 |
| R2 (`:164-171`) | `bookkeeping-file` only on calibration; `knowledge-entry`/`registry-append` only on coverage; `instrument-acquisition` only on operability | `bookkeeping-file` on calibration — allowed | `knowledge-entry` on coverage — allowed | `instrument-acquisition` on operability — allowed | 0 |
| R3 (`:172-173`) | at least one claim declares the lowest-scoring non-retired axis | **yes: C1 declares `calibration` 7** (lowest; `coverage` 8, `operability` 8; retired set empty) | no | no | 0 |
| R4 (`:174-176`) | whole-word `all`/`every`/`complete`/`none`/`no` in a claim text without a same-claim `enumerate:` line | no whole-word hit; `enumerate:` present | no whole-word hit; `enumerate:` present | no whole-word hit; `enumerate:` present | 0 |

Answers to the item's four questions: R1 — yes, all three owned axes are declared, each exactly once
(`:9`, `:13`, `:17`). R2 — all three class/axis pairs are the allowed pairing. R3 — yes, calibration is
the lowest non-retired axis (7 vs 8/8) and **C1** declares it (`:9`). R4 — **no** whole-word hit in any
claim block.

Expected and observed result: **`claims=3 flags=0`**, exit 0.

### R4 per-block grep (the item's explicit check)

`sed -n '8,20p' preregistration.txt | grep -ciE '\b<w>\b'` for `w` in `all every complete none no`
-> `all: 0  every: 0  complete: 0  none: 0  no: 0`.

### Independent probe (not the seat's tool) and discriminators

`/var/tmp/souji-r26-LabAxisRun/axis-probe.py`, sha256
`35a678023344520e3e41e89d2b5dd4117424a18c31cb6964f2d5813fdc38f495`, written from the frozen rule text
only; every invocation used `python3 -B`.

```
python3 -B axis-probe.py --prereg <prereg> --scorecard <SCORECARD at 89e0fce or at tip> --arm {strict|prose|ci|cs}
claims=3 flags=0      (rc 0) on arms strict/prose/ci/cs with the frozen-rev scorecard,
                      and arms strict/prose again with the tip scorecard
```

Discriminator controls (proof the 0 is not vacuous; synthetic inputs only):

```
ctl/r25-c2-replica.txt      (fixture-expansion on operability)  -> claims=1 flags=2  rc 1
ctl/r1-wrong-axis.txt       (axis: quality)                     -> claims=1 flags=3  rc 1
ctl/r3-no-lowest.txt        (no claim on calibration)           -> claims=2 flags=1  rc 1
ctl/r4-no-enumerate.txt     (whole-word "every", no enumerate)   -> claims=1 flags=1  rc 1
ctl/malformed-missing-axis  (claim without axis: line)          -> refused, rc 2, no flag lines
```

Committed cross-check: `tools/souji-axis-check.py` (commit `0833de9`, blob `db326cd1…`, sha256
`14bc9632e88ef58f18108011f6645bd970cd825d0ffc1664369dc60b0d579332`) prints `claims=3 flags=0` rc 0 on
the same two inputs, `flags=2` rc 1 on the r25-C2 replica, rc 2 on the malformed control. Independent
implementation and committed tool agree on every case I ran.

Revisions: `89e0fce` (frozen prereg) -> tip moved during this run (`0833de9` -> `d6c13b0` -> `07f83e6`);
the verdict `claims=3 flags=0` was reproduced at each measured tip. No lane file, index, or jj state was
written; scratch was `/var/tmp/souji-r26-LabAxisRun/` and is removed. No tooling installed or upgraded.

## Findings

1. **R1 clean** — `calibration` (`:9`), `coverage` (`:13`), `operability` (`:17`); all three are the
   lane's owned set and the retired set is empty (`SCORECARD.md` `## Retired` -> `None.`). 0 flags.
2. **R2 clean** — the three declared classes map onto exactly their allowed axes (`:10` on `:9`,
   `:14` on `:13`, `:18` on `:17`). This is the r25-C2 misattribution shape avoided: r25's C2 declared an
   edge-class surface on operability; r26 declares each surface on its mapped axis. 0 flags.
3. **R3 clean and stable** — lowest non-retired axis is calibration 7 (`SCORECARD.md:14`;
   `:13` and `:15` are 8), declared by C1 at prereg`:9`. The axes rows are byte-identical between the
   frozen rev and the tip, so C1's SCORECARD surgery cannot flip this verdict. 0 flags.
4. **R4 clean** — zero whole-word `all`/`every`/`complete`/`none`/`no` occurrences inside the machine
   block; each claim carries `enumerate: bash census/round-26/cN-counter.sh` (`:11`, `:15`, `:19`).
5. **R4 scoping hazard (instrument operability, not a prereg defect)** — measured sensitivities:
   (a) a whole-file scan fires on 18 lines, including the header `"No axis may be harmed."`
   (prereg:5) and the rule's own definition line (prereg:175); (b) a prose-section-only scan finds no
   `enumerate:` in any CLAIM prose section (the line lives only in the machine block) and would flag
   all three claims — prose hit counts per claim: C1 `{none:1}`, C2 `{all:1, every:3, none:2, no:2}`,
   C3 `{all:1, every:2, complete:1, none:1, no:4}`. Either lax reading produces a **false KILL** on the
   round's own prereg. The frozen text resolves it toward block scoping (prereg:7 "parses exactly this
   section"; `:175` "same-claim `enumerate:` line"), and the committed tool follows that reading. Fixture
   cases should pin it, e.g. "prose contains `every`, block has `enumerate:` -> pass".
6. **Self-declaration limit of R2** — the check sees only the machine block. C2's prose declares
   `knowledge-entry + registry-append` (prereg:72) while its block declares `knowledge-entry` alone
   (`:14`). Both classes map to coverage, so no divergence this round; a seat that omits a class from the
   block hides it from R2.
7. **Observation outside my item (C3 K2 literal)** — the committed fixture prints
   `cases={len(CASES)} pass={npass}` (`tests/fixtures/r26-axis-check.py:219`) with 11 `dict(id=…)`
   entries in `CASES` (`:73`…) and prints `control=` only under `--stub` (`:221`), so a green run's last
   line is `cases=11 pass=11` [INFERENCE from committed bytes; I did not run the fixture — the editing
   wave owns its gate]. Frozen C3 K2 requires the last stdout line
   `cases=12 pass=12 control=FALSE-GREEN-REJECTED` (prereg:179, :199). L1 adjudicates.
8. **Hygiene residue in the lane tree** — `tools/__pycache__/souji-axis-check.cpython-314.pyc`
   (2026-10-25 14:25:48) and `tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc`
   (14:26:55) are present and untracked (`git status --porcelain`), i.e. lane Python was executed without
   `-B`. Untracked only today; a `git add -A` would land bytecode. Not mine to remove (write scope).

## Attack log

A1. **R4 is satisfiable by a non-counting line.** A claim text containing "every row must match all
records" passes with `enumerate: true` (`ctl/a1-dummy-enumerate.txt` -> `claims=1 flags=0`). R4 proves the
presence of a line, not that it counts the universal clause. Frozen text, so no predicate change is
proposed; a stricter future variant would require the `enumerate:` argument to be an existing path/argv at
the prereg revision.

A2. **R2's class vocabulary is closed, and R3 tests a declaration, not a surface.** `axis: calibration`
with `surface-class: measurement` (unlisted) passes all four rules (`flags=0`, `ctl/a2-neutral-class.txt`):
the frozen R2 names only the classes it flags, and R3 only requires the word `calibration` on one claim.
A nominal calibration claim on an unlisted surface class therefore satisfies the axis-floor rule without
touching a calibration surface. My first (over-strict) probe reading flagged unknown classes; that
divergence is recorded because both readings are defensible against the frozen text, and the closed-list
reading is the authoritative one.

A3. **R3 trusts its `--scorecard` argument with no revision pin.** The CLI is
`--prereg PATH --scorecard PATH` (prereg:157-159); a caller can pass any scorecard whose lowest axis
matches a claim already written. C1's kill rule protects the base SCORECARD lines 1-171 only inside C1.
Mitigation needs no predicate change: pass the blob extracted at the frozen rev — verified identical
verdict (my probe ran against both `git show 89e0fce:SCORECARD.md` and the tip file: `flags=0` both).
Discriminator: the r3-no-lowest control shows the rule does fire when no claim declares the lowest axis.

A4. **The self-host check alone cannot reject an always-green emitter.** A stub printing
`claims=3 flags=0` reproduces my result. Case 12's `control=FALSE-GREEN-REJECTED` arm is the only
discriminator, which is why Finding 7 (whether that arm is counted inside the printed `cases=` total)
matters to K2's literal. My probe carries its own five controls for the same reason.
