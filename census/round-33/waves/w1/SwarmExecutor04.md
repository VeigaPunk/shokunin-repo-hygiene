## Status

STATUS: PASS — K04's one honest restatement row is drafted, its cause is executed (value drift, cause `728b2ce`), and the counter reads `ITEM K04 AGREE` / `mismatches=0` on a scratch landing commit at the preregistration revision; the move is growth, not a regression.

## Evidence

All runs in scratch clone `/fast/scratch/hyaku/souji-r33/RestateK04/c` (`git clone -q --no-local` of the lane, origin removed, `rev-parse --show-toplevel` = the clone), detached at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; `TMPDIR` fresh per run; `GIT_CONFIG_NOSYSTEM=1`; cwd = clone root. SCORECARD.md is byte-identical at base `6017a48` and at `2d9bca5` (`cmp` clean, 494 lines), so line 155 is the same row at both.

1. Frozen argv, 3 runs, fresh TMPDIR each:
   `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh`
   → `rc=0` three times, stderr empty, identical lines apart from the mkdtemp suffix; summary line each time
   `selftest=PASS ids=7/7`. Whitelist check: `\b5/5\b` False, `\btotal=5\b` False, `\bfailed=0\b` False → the frozen
   predicate fails while exit still matches 0. The row states `→ 5/5`.
2. Cause hunt (`git log --reverse -- tests/fixtures/r13-repo-structure.sh tools/souji-repo-structure.sh` → three
   commits, `6ed10a7`, `728b2ce`, `98e5203`); argv run at each and at each parent:
   `6ed10a7` → 5/5 holds; `679e2d0` (first parent of `728b2ce`) → 5/5 holds; `728b2ce` → 7/7 **fails**; `98e5203` → fails.
   First failure `728b2ce71acbe574ae3036b456724d0a3d6f8f08`; `git show --name-only` names
   `tests/fixtures/r13-repo-structure.sh`; `merge-base --is-ancestor 728b2ce 2d9bca5` true.
3. Counter on the scratch landing commit `4f7fd6370106022f20dad3fe9d1d11b020e13e6e`:
   `ITEM	K04	AGREE	restated	rc=0 expect_exit=0 statement is an output line last=selftest=PASS ids=7/7`
   `SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=4f7fd637...`, counter rc=0.
4. Falsifiers: do-nothing at list-rev → `MISMATCH original … predicate fails`, rc=1; non-causal cause `98e5203` →
   `BAD-CAUSE(original at parent=False at cause=False; need True/False)`, rc=1; substring statement `` `ids=7/7` `` →
   `statement is not a digit-bearing output line`, rc=1.

Row (verbatim, `ROW-BEGIN`/`ROW-END` in the delivery):
`| K04 | SCORECARD.md:155 | restated | 0 | same | `selftest=PASS ids=7/7` | 728b2ce71acbe574ae3036b456724d0a3d6f8f08 | selftest grew from 5 to 7 cases at 728b2ce: round-25 added the linked-common-dir and colocated-vs-plain probe cases, all PASS |`

## Findings

1. SCORECARD.md:155 (base `6017a48`) states `→ 5/5` for `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh`; at `2d9bca5` the same argv exits 0 and prints `selftest=PASS ids=7/7`. Value drift, not an argv defect: the argv is unchanged and still green.
2. Cause `728b2ce71acbe574ae3036b456724d0a3d6f8f08` (round-25, 2026-10-25) added two probe cases to `tests/fixtures/r13-repo-structure.sh` (+242/−7), `emit SOUJI-R13-STRUCT-linked-common-dir` and `emit SOUJI-R13-STRUCT-colocated-vs-plain`, extending the expected-id list; its own new comment fixes the final lines at `ids=6/6` (baseline) / `ids=7/7` (`--probe`). `tools/souji-repo-structure.sh` is untouched by the cause.
3. The move is GROWTH: the five originally certified cases (`manifest-control`, `write-free`, `object-metrics`, `bogus-repo`, `promisor-refusal`) are the same five ids in the same order as the 5/5 run at `6ed10a7`, and the two added cases PASS too (all seven `verdict=PASS`). Nothing is lost; no regression is restated away.
4. Column choice: the statement is the summary line `selftest=PASS ids=7/7`, because the row's claim is the selftest's pass count; `same` is correct for the run cell (the argv itself is current) and the cause is the value-drift commit the counter can execute.
5. The row was proved under both the bare heading `### Round 33 capability currency` (scratch `4f7fd63`, canonical) and `### Round 33 capability currency (C1, appended)` (scratch `2b41f5f`); both AGREE, so the L1 can land any single shared heading for the wave. My delivered block's table header is `| id | row | status | exit | run | statement | cause | reason |`, matching the K18 delivery already in this wave (counter ignores header rows).
6. Not mine to land: the tip reading and the re-pin/landing commits belong to the L1; this report proves only the scratch landing commit.

## Attack log

None. No frozen predicate, target, counter, item or leg is proposed for change; the row is an append-only restatement in the section the preregistration allows.

## Deliveries

* `.ufo/waves/round-33/w1/deliver-c1-K04.md` — the row between `ROW-BEGIN`/`ROW-END`, the full appended block, and all receipts above.
* `.ufo/waves/round-33/w1/SwarmExecutor04.md` — this report.

Tooling: no install or upgrade was needed. Scratch `/fast/scratch/hyaku/souji-r33/RestateK04` removed after the receipts were copied; no file in the lane outside `.ufo/waves/round-33/w1/` was written.
