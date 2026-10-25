# ExecAxisTool — round 26 C3 tool draft (operability, instrument-acquisition)

## Status

STATUS: PASS — C3 tool draft delivered at `.ufo/waves/round-26/w1/souji-axis-check.py` (227 lines,
stdlib only: `argparse`, `re`, `sys`); 19 throwaway-world executions under
`/var/tmp/souji-r26-ExecAxisTool/` reproduce every frozen CLI/rule branch (exit 0 no flags, exit 1
per flag, exit 2 with stderr reason and empty stdout). The function of C3 is implemented and
self-tested; K1/K2 at the tip and the 12-case fixture are the L1's integration runs, not claimed
here. Scratch removed.

## Evidence

Lane revisions (read-only): base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; working-tree HEAD
`4453128`. Base literal re-confirmed:

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e 0eca7c8:tools/souji-axis-check.py
fatal: path 'tools/souji-axis-check.py' exists on disk, but not in '0eca7c8a...'   (rc 128)
```

Delivered draft: `sha256 0805afff649a2f893542bd7f8e2e676408bb934a7cf3255d13b46d921c3d121b`,
8288 bytes, mode 0755; `wc -l` = 227 (bound: <=300).

All runs: `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/souji-axis-check.py
--prereg <scratch> --scorecard <scratch>` from outside any repo; scratch files only.

| case (scratch world) | rc | stdout |
|---|---|---|
| well-formed 3-claim mirror of the frozen block | 0 | `claims=3 flags=0` |
| frozen machine-block bytes, /var/tmp copy (smoke preview, not claim evidence) | 0 | `claims=3 flags=0` |
| r25-C2 replica: C2 operability + fixture-expansion | 1 | `FLAG C2 R2 surface-class=fixture-expansion requires axis=coverage (declared axis=operability)` then `claims=3 flags=1` |
| R1 wrong axis (C3 `docs`, `measurement`) | 1 | `FLAG C3 R1 axis=docs not in {calibration,operability,coverage}` then `claims=3 flags=1` |
| R3 no claim on calibration (all 8s) | 1 | `FLAG PREREG R3 lowest_axis=calibration score=7 declared by no claim` then `claims=3 flags=1` |
| R4 universal clause, no `enumerate:` | 1 | `FLAG C1 R4 universal word(s) every,no without an enumerate: line` then `claims=3 flags=1` |
| R4 universal clause with `enumerate:` | 0 | `claims=3 flags=0` |
| neutral classes (`receipt-binding`, `measurement`, unknown `gizmo-class`) | 0 | `claims=3 flags=0` |
| compound wrong classes (`knowledge-entry/registry-append` on calibration, `bookkeeping-file` on coverage) | 1 | 3 x `FLAG ... R2 ...` then `claims=3 flags=3` |
| retired-section row after `## Retired` (axes-window scoping) | 0 | `claims=3 flags=0` |
| retired axis row (`goto 3`) inside the axes table | 0 | `claims=3 flags=0` |
| scorecard with no `## Axes` heading + `## Retired` section (`goto 3`) | 0 | `claims=3 flags=0` |
| same fallback scorecard with the R3-wrong prereg | 1 | `FLAG PREREG R3 lowest_axis=calibration score=7 declared by no claim` |
| no `## MACHINE BLOCK` | 2 | stdout `''`, stderr `souji-axis-check: refused: no '## MACHINE BLOCK' section in ...` |
| CLAIM with no `axis:` line | 2 | stdout `''`, stderr `souji-axis-check: refused: CLAIM C1 declares no 'axis:' line` |
| block not terminated by `END` | 2 | stdout `''`, stderr `... is not terminated by an 'END' line` |
| unparseable scorecard table (`| calibration | high |`) | 2 | stdout `''`, stderr `... no parseable axes table rows ...` |
| missing prereg file | 2 | stdout `''`, stderr `... cannot read prereg ...: No such file or directory` |
| usage (`--prereg` without value) | 2 | stdout `''`, argparse usage on stderr |

The frozen machine block was also extracted (read-only) and compared: my mirror's claim lines are
byte-identical to `CLAIM C1`..`enumerate: bash census/round-26/c3-counter.sh` (comparison printed
`body-identical: True`). The tool was never pointed at the lane's real preregistration or SCORECARD.

## Findings

1. **Delivered draft** — `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/souji-axis-check.py`.
   Parses only the `## MACHINE BLOCK` marker line through `END`; prose after `END` is ignored
   (verified: the fixture's trailing sentence carries `every`/`all`/`no` and produces no flag).
   Rules emit in frozen order R1 (per claim), R2 (per claim, per surface token), R3 (once), R4
   (per claim). Counts line is last.

2. **Coordination collision — pre-existing untracked C3 artifacts in the lane tree.** At my first
   inspection (before any write) the lane already held untracked
   `tools/souji-axis-check.py` (5494 B, 155 lines, mtime 14:24:43, sha256
   `a3fb1859b61ce962409a3fd20e400c402f7a2561aee0f523b94a8c50db358f40`) and
   `tests/fixtures/r26-axis-check.py` (10200 B, mtime 14:26:38, sha256
   `2ffc18289fc82b9075ad3580cb9bec6a80384061c7d294b5aa17dbf9ca93c8da`). I inspected the tool's
   declared surface read-only and did not modify, copy over, or delete either. Two independent C3
   implementations now exist; the L1 (sole integrator) must choose one before landing. My draft's
   behaviour is the one evidenced above; the other file's is not evidenced by me.

3. **Stray bytecode from a sibling run.** Untracked `tools/__pycache__/` (mtime 14:25:48) and
   `tests/fixtures/__pycache__/` (mtime 14:26:55) are in the lane tree. They are not mine: every
   execution I performed used `python3 -B`, and my tool imports only stdlib, so running it writes
   no bytecode. They must be resolved by the L1 before landing (a hygiene lane should not commit
   them); I did not delete them (not mine to remove).

4. **R2 tokenisation** — `surface-class:` values are split on `+`, `,`, `/` and each token checked
   independently. Single-token machine-block values behave exactly as frozen; the split only widens
   coverage for the prose form `knowledge-entry + registry-append` (C2's declared pair) and never
   invents a flag. `receipt-binding`, `measurement` and unknown tokens are neutral.

5. **R3 flag identity** — R3 is not claim-scoped, but the frozen stdout shape requires a `<claim>`
   field, so the R3 line uses `PREREG` (`FLAG PREREG R3 <detail>`). On score ties the detail lists
   all lowest axes joined with `+`, and any one of them declared by any claim satisfies R3.

6. **R3 scorecard reading** — if a `## Axes` heading exists the scan is scoped to that section (up
   to the next heading); otherwise it falls back to a global scan. Rows require a bare integer
   second cell, so the Round 24/25 measurement tables (`| C1 ... | calibration 7 | ...`) are never
   read as axis rows. Rows inside a `## Retired` section, or carrying the word `retired`, are
   skipped — verified inside the axes table (a lower-scored `goto 3` row is ignored, so calibration
   7 stays the target) and in the fallback path.

7. **Refusal contract** — exit 2 prints no stdout at all (no counts line, no flag line), only
   `souji-axis-check: refused: <reason>` on stderr; argparse keeps its own exit-2 usage path. No
   partial parse is reported.

8. **R4 matching** — whole-word by `\b`, case-insensitive, first-occurrence-ordered word list in the
   detail; presence of an `enumerate:` line in the same block exempts the whole block. `[INFERENCE]`
   the case-insensitive reading is compatible with the frozen 12-case set (case 8 lower-case without
   enumerate flagged; case 9 with enumerate passes — both reproduced); the frozen text names the
   words in lower case and does not forbid the wider match. If the fixture binds case-sensitive
   semantics, one regex flag changes it.

9. **R1/R2 interaction** — an unowned axis does not short-circuit R2; R2 evaluates the declared axis
   (the R1 case emits only its R1 flag because `measurement` is neutral). Ordering follows the frozen
   "Checks, in order".

## Attack log

Not an attack item: C3 is the operability instrument, and no frozen predicate, target or case set is
challenged. Bounded-envelope notes for the L1, none requesting a change:

- R3 is satisfiable by a claim that merely *declares* the lowest axis; the tool cannot see intent.
  R2 is what makes a mis-declaration costly, so the pair must stay together.
- R4 sees only claim-block text inside `## MACHINE BLOCK` (frozen: "parses the `## MACHINE BLOCK`
  section only"), so a universal clause in the prose below `END` is invisible. This round's own C1
  prose contains such clauses (e.g. "exactly three headings"); it is out of scope by construction.
- The instrument does not check that `enumerate:` names a *countable* command, only that the line
  exists (frozen R4 wording). A claim can carry a vacuous `enumerate:` today; that is the declared
  rule, not a defect.

## Notes

- Tooling: nothing installed or upgraded (no `pacman`, no `uv`/`npx`); stdlib only.
- Scratch `/var/tmp/souji-r26-ExecAxisTool/` removed after the runs.
- Writes: only this report and `w1/souji-axis-check.py`. No `git` mutation, no `rm`/`mv`, no
  `agent://all`, no read of forbidden paths.
- Checks the L1 still owns: copy to `tools/souji-axis-check.py`, K1 self-hosting run
  (`claims=3 flags=0`) at the tip, K2 `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, red/green
  receipts `c3-before.tsv`/`c3-after.tsv`, and the choice between the two C3 implementations
  (finding 2).
