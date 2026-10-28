# Round 37 — receipt citations, the drift tool's write envelope, and fixture discrimination

author: souji L1 (SoujiR37), hyaku run 11. Lane base `0d974ffcb7dfb70617947531cab2d7e96cd8f9fd`;
frozen contract `census/round-37/preregistration.txt` (freeze commit
`d5c6498c5f72a63c9df32b26ee143e8d775eebbd`); landing revision
`e987a27c960baa74c08abe7f7ccbd980d9d88460`. The round repairs three defect classes the round-36
non-author spot-check routed (`corpus/lessons/round-36-verifier-spotcheck.md`, Routed defects 1,
3 and 4).

## Claims

- **C1 calibration (score 7, the lowest non-retired axis).** Every routed self-assessment cell that
  quotes an after-value is either corrected in place (current-registry cells: SKILL gate registry,
  lesson Claims) or superseded by an append-only row (frozen measurement rows and the r36 frozen
  predicate sentence), and each correction carries a value the cited receipt actually holds at a
  commit where it exists. Counter:
  `python3 -B tools/souji-citation-reconcile.py --root <lane> --rev <landing> --register census/round-37/citation-cells.tsv`
  → `SUMMARY cells=11 mismatches=0`, rc 0 (amendment A1 added the two `cases=8` selftest cells and
  `--register-rev` pins the register). Base control (`census/round-37/records/c1-before.txt`):
  `cells=11 mismatches=9`, rc 1 (the frozen nine-cell register reads 9; the two added cells are
  absent at the base) — the same receipts resolve at the base revision, but no correction
  line exists, so the counter's citation arm is what moves.
- **C2 operability (score 8).** The F1 drift tool's write envelope matches its docstring: `--root`
  is a containment boundary (RECORD-OUTSIDE-ROOT), the child git process gets a whitelisted
  environment with config discovery neutralised (no inherited `GIT_*`, `GIT_CONFIG_NOSYSTEM=1`,
  `GIT_CONFIG_GLOBAL/SYSTEM=/dev/null`), and `--json` is refused inside every measured repository
  and written through an `O_NOFOLLOW` descriptor on the resolved path. Counter:
  `python3 -B tests/fixtures/r37-drift-escapes.py --base-tool <r36 blob>` →
  `SUMMARY cases=9 pass=9 fail=0 base_fail=6 control=ESCAPE-REPRODUCED`, rc 0; the r36 regression
  fixture stays `cases=12 pass=12 fail=0 control=STUB-REJECTED`. Base control
  (`census/round-37/records/c2-before.txt`): the same fixture against the r36 tool bytes reads
  `cases=9 pass=3 fail=6 base_fail=6`, rc 1 — six escapes reproduce (amendment A2 added the
  hardlink and measured cases).
- **C3 coverage (score 8).** The drift tool's fixture surface discriminates its fields: six frozen
  single-defect mutants (the routed survivor `live_repos = len(rows) - unreachable`, a
  `drift_rows` counter that drops UNRECORDED, an unrecorded-loop failure that is not counted
  unreachable, a one-sided REGS-CHANGED, an absent row reported UNREACHABLE, and an exit code
  that ignores drift) are all killed by `tests/fixtures/r37-drift-discrimination.py`. Counter:
  `python3 -B tests/fixtures/r37-drift-mutants.py --fixture tests/fixtures/r37-drift-discrimination.py`
  → `SUMMARY mutants=6 killed=6 survived=0`, rc 0. Base control
  (`census/round-37/records/c3-before.txt`): the same battery against the r36 fixture blob reads
  `killed=4 survived=2` (M1 and M2 survive the 12/12 fixture).

## Gate

New sources opened this round (targets: `census/round-37/preregistration.txt` C2; all read from the
installed man pages at `git 2.56.0-1` and the live git-scm pages):

| id | source (URL) | access | located quote (≤25 words) | verdict |
|---|---|---|---|---|
| S236 | git(1) ENVIRONMENT — GIT_TRACE_REFS — https://git-scm.com/docs/git#Documentation/git.txt-GITTRACEREFS | 2026-10-28 | “Enables trace messages for operations on the ref database.” (§ ENVIRONMENT, `man git` line 1212) | **admit** — a child that inherits the variable writes a trace file the caller did not request; this is the W2 mechanism the escape fixture reproduces on the r36 blob |
| S237 | git(1) ENVIRONMENT — GIT_CONFIG_NOSYSTEM — https://git-scm.com/docs/git#Documentation/git.txt-GITCONFIGNOSYSTEM | 2026-10-28 | “Whether to skip reading settings from the system-wide $(prefix)/etc/gitconfig file.” (§ ENVIRONMENT, `man git` line 1153) | **admit** — the manual adds it “can be used … to create a predictable environment for a picky script”; that is exactly the child env the C2 repair builds |
| S238 | git-config(1) § GIT_CONFIG_COUNT — https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT | 2026-10-28 | “all environment pairs … up to that number will be added to the process’s runtime configuration” | **reject** — a `GIT_CONFIG_COUNT`-injected `trace2.eventTarget` wrote no trace file on git 2.56.0 (`census/round-37/records/c2-after.txt` (`case-env-witness=PASS`) and the independent positive
control in `.ufo/waves/round-37/w1/W1ScribeGate.md` (a config-file `trace2.eventTarget` wrote
9812 bytes; the env-injected one wrote none)), so env config does not reach trace2 initialisation on this surface; flip: a reproducible trace2 write via env config at a named git version |

Row changes: S236 and S237 are new tier-A `mined` rows, S238 is new and `rejected`; no existing
row's `status`, `recheck` or `used-by` cell changed. `used-by` for S236/S237 is this lesson (C2
rests on both rows; that satisfies the sourced-claim requirement). The registry grep count moved
159 → 162; the census command is in the report.

## Mistakes

### M1 — never-true numbers cited as receipts (calibration)

**Class:** a frozen prereg predicate sentence and five self-assessment cells (SCORECARD r36
measurement rows and capability rows, the SKILL gate registry, the round lesson's Claims section)
quoted after-values that never lived in the named receipt, and their measured-commit cells named a
commit where the receipt does not exist.
**Evidence pointer:** `corpus/lessons/round-36-verifier-spotcheck.md` Routed defects 1;
`census/round-37/records/c1-before.txt` (`cells=9 mismatches=9` at the base revision).
**Captured-by:** none at r36 — its gate checked that receipts were *named*, never that the quoted
number matched the receipt bytes, and the prereg's own sentence was exempted from its own rule.
The capture is now mechanised: `tools/souji-citation-reconcile.py` binds a citation arm (one
anchored line, expected present, stale absent) and a receipt arm (the blob at a commit where it
exists carries the same token) for every register row.
**Fix:** `census/round-37/citation-cells.tsv` plus the corrections committed with the landing
(`SCORECARD.md` `### Round 37 receipt reconciliation`, the two SKILL registry cells, the r36
lesson `## Correction`, and appended `R37-C1-8`/`R37-C1-9` blocks in the r36 prereg). Shown able to
fail: `c1-before.txt` reads 9 mismatches with the same counter at the base revision; `c1-after.txt`
reads 0 at the landing.

### M2 — new instrument defects found before after-data (disclosed)

**Class:** the first draft of `tests/fixtures/r37-drift-discrimination.py` added a worktree to a
repository it had not created (the prunable case crashed), and `tests/fixtures/r37-drift-mutants.py`
counted any non-zero fixture exit as a kill, so a crashing fixture would have scored as killed.
**Evidence pointer:** the first local runs (traceback at the worktree-add line; `killed=yes` for a
fixture that printed no SUMMARY).
**Captured-by:** no committed rule at the time; the battery now requires a `SUMMARY cases=` line
with `fail>0` before it records a kill, and a manual per-mutant run names the failing case.
**Fix:** `make_repo(alpha)` before `worktree add`; the battery's summary gate. Both are in the
landing commit `e987a27`. No claim after-data was taken before the repair; the frozen mutants,
targets and predicate sentences did not change.

## Frontier

SOURCES census before → after: 159 rows, rc 0 → 162 rows, rc 0 (`census/round-37/records/`), with
the command and both exit codes in the round report. Rows added by tier: A ×3 (S236, S237 admitted;
S238 rejected); touched old→new: none. No coverage-map entries were re-grounded (`ground: F<k>`
lines unchanged), so no F row advances: the two admitted rows ground the C2 repair, not new
frontier ground. Mined mistake: M1. Assimilation: none — no `merge/souji/` theme was adopted this
round (the package's staged entries do not touch citations or the drift envelope; adopting one
would not serve a frozen claim).

## Named limits (disclosed, status-neutral)

- The C1 counter's `receipt_rev` arm is not discriminated by the fixture or the live register:
  all nine original rows cite receipts that are blob-identical at the landing revision, and the
  fixture commits its receipt at the same revision it registers. A mutant that ignores
  `receipt_rev` survives (`.ufo/waves/round-37/w1/W1MutCounter.md`); routed to r38 with a
  base-committed/head-deleted receipt case.
- The `42ea92e` measured-commit cells are corrected in prose (`SCORECARD.md` reconciliation
  paragraph), not by a register row: the schema binds an expected token to both a citation line
  and a receipt blob, and a commit id is in neither. Routed to r38 for a commit arm.
- A FIFO `--record` is now refused (A2.4); other special files are not exercised.
- `--record X --json X` still overwrites the record when the record lies outside `--root`
  (`.ufo/waves/round-37/w1/W1ExecConsumers.md` F2); the target is outside every measured tree, so
  the C2 claim does not cover it. Routed to r38.
- The `--json` `O_NOFOLLOW` descriptor guards the final component only; a parent-directory swap is
  outside the fixture's deterministic reach (W1MutTool M9 survives). Named, not claimed.
- The r37 discrimination fixture does not exercise the `TOTAL` cross-checks (W1MutTool M7
  survives the r37 fixture and dies on the r36 fixture); C3's frozen six mutants do not include
  it. Routed to r38.
