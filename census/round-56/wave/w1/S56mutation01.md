# S56mutation01 — scoped findings (souji round 56, w1)

Full seat report: `.ufo/waves/round-56/w1/S56mutation01/S56mutation01-report.md`
Receipts: `.ufo/waves/round-56/w1/S56mutation01/receipts/`
Measured revision `cce21b555a617cadda782613ec1e9d3a0c12ac83`, base `fafe371694fea41c5d23f63083865d5ccf3f1d36`.
All eight frozen pins verified before probing (`receipts/pins.txt`, all MATCH). Read-only to the lane.

VERDICT: ATTACK-FOUND — 8/10 single-defect mutants killed, 2 survived.
VERDICT: SURVIVORS (M1 PAIR-FILING-HIDDEN emission; M7 LF-only numstat parse)

## Detector

`python3 -B <counter> --selftest --work <dir> --builder-sha256 2f26d6aa… --expected-sha256 48a7cc0e…`
over the 33 committed C1 fixtures; asserts `(exit code, first FINDING id)` per row.
Pristine baseline: `SELFTEST pass cases=33`, rc 0. Restored bytes after every mutant: `pass cases=33`,
`sha256 == 975d3520…63bcbbf179` (ten of ten).
Builder and expected TSV were copied byte-identical, so both committed pins verified — no pin bypass.
No run emitted `CANNOT-EVALUATE` (21 selftest logs + 2 differential logs + 3 probe logs, all clean).

## Mutants

| # | Defect | Verdict | Killing fixture |
|---|---|---|---|
| M1 | PAIR-FILING-HIDDEN emission deleted | **SURVIVED** | none possible (§1) |
| M2 | hidden-line filter dropped from pair filings | KILLED | F24-PAIR-HIDDEN-FILING (rc 1→0) |
| M3 | HTML opener back to any-indent `'<!--' in ln` | KILLED | F26-INDENT4-COMMENT-OPENER (rc 1→0); F29 (rc 0→1 CORRECTION-IN-FENCE) |
| M4 | HTML opener back to mid-line match (indent≤3) | KILLED | F29-PROSE-COMMENT-MENTION (rc 0→1) |
| M5 | CORRECTION-FILE-BINARY check deleted | KILLED | F28-NUL-CORRECTION-UNCHANGED (rc 1→0) |
| M6 | binary numstat read as 0 deletions | KILLED | F27-BINARY-NUMSTAT (rc 1→0) |
| M7 | `split('\n')` → `splitlines()` in numstat | **SURVIVED** | none — outside fixture reach (§2) |
| M8 | CORRECTION-IN-FENCE emission disabled | KILLED | F4, F7-TILDE-FENCE, F8, F9, F7-FF, F8b, F7-FF2 (expected finding lost) |
| M9 | `ZONE = 32` → `64` | KILLED | F10-STRADDLE (finding → MULTIPLE-ANNOTATIONS) |
| M10 | BOGUS-RECOMPUTED branch deleted | KILLED | F11 (rc 1→0), F20 (rc 1→0), F21 (finding changed) |

Each mutant is one hunk against committed bytes; diffs in `receipts/mutant-diffs.txt`, mutant sha256
in `receipts/mutants-index.tsv`, sources preserved in `receipts/mutants/`.

## §1 M1 — live, and unkillable under the frozen row grammar

Full-output differential over all 33 fixtures: exactly one changed, F24
(`receipts/logs/diffall-M1.txt`). On F24 the mutant loses `FINDING PAIR-FILING-HIDDEN` and prints
`pairhidden=0` instead of `pairhidden=1`; rc (1) and first finding (`UNFILED-SOURCES-ANNOTATION`)
are unchanged, so the detector passes.

`PAIR-FILING-HIDDEN` is emitted only inside `if not fil or not match:`, immediately *after* the
`UNFILED-SOURCES-ANNOTATION` finding on the same annotation — so it can never be the first finding
and can never change the exit code. The row grammar has three columns and the selftest asserts only
the first finding: **no fixture can kill M1**. C1 target T1's clause "F24 also prints
PAIR-FILING-HIDDEN" (and `pairhidden=`) therefore has zero selftest kill power and rests on a
hand-run measure-mode probe, which shows both present on pristine bytes.

Named limit → r57: add a fourth expected column (`expect_all_findings` or `expect_summary`) so F24
asserts `pairhidden=1`. No fixture is missing; a detector column is. No edit of frozen bytes.

## §2 M7 — live, disclosed, unreachable by any fixture

Full-output differential over all 33 fixtures: **zero** changed (`receipts/logs/diffall-M7.txt`).
Not an equivalent mutant: `probe-m7-nel.py` builds a scratch repo with a file named `a\u0085b.txt`
and repo-local `core.quotePath=false`, then runs both `numstat_deletions` implementations on the same
git bytes (`receipts/logs/probe-M7-nel.txt`):

```
numstat raw '1\t0\ta\x85b.txt\n' ; split('\n') → 1 record ; splitlines() → 2 records
pristine → [['a\u0085b.txt', 0]]      mutant → [['a', 0]]
```

The counter only ever passes four fixed ASCII path constants to `numstat_deletions`, so no
repo-level fixture can reach the shape; the missing piece is a parser/differential assertion on the
committed quotepath receipt. The frozen preregistration already de-claims this shape ("not a
reachable lane verdict … parser-hardening with a differential receipt, not a claim"), so the
survivor is consistent with the frozen scope — a coverage note, not a claim defect.

## §3 OBS-1 — frozen docstring contradicts frozen behaviour (r57, no edit)

The v5 "Named limits" paragraph says *"a line whose prose merely mentions `<!--` still opens a
region — the real lane's own SCORECARD.md hides its tail this way, disclosed"*. That is stale v4
text: v5 requires the opener to begin the line. Measured with the frozen `hidden_lines()`
(`receipts/logs/probe-OBS1-docstring.txt`): the F29 prose line → `hidden=[]`; the exact SCORECARD.md
line 1378 bytes at `cce21b55` → `hidden=[]`; a line that truly begins with `<!--` → `hidden=[1,2,3]`.
Behaviour matches C1 T4 and F29; only the prose is wrong. No C1 target is falsified.

## Compliance

Only `.ufo/waves/round-56/w1/S56mutation01/**` was written in the lane; everything else was scratch
under `/fast/scratch/hyaku/souji-r56/S56mutation01/` (deleted before yield, receipts copied out
first). Read-only git only (`show`, `rev-parse`, `status`) with `-C <abs path>`; the sole
init/add/commit calls were the committed fixture builder's, inside asserted scratch fixture roots
(`init_repo` verifies `rev-parse --show-toplevel`), which matches the L1's mid-run bounds
clarification — no contradiction. No tool installed. Disk guard at start: 405.5G free.
Lane observation (not mine): worktree showed `M SCORECARD.md`,
`M census/round-56/records/landing-suite-standing.txt`, HEAD `148f39a6…`; all claim evidence was read
from committed bytes at `cce21b55`.
