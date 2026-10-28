# R40revenger12 — C3 coverage attack

## Verdict

**C3 is not yet falsified as a whole, but its frozen predicate has concrete trap doors.** A literal “duplicate TOTAL rows must be refused” test fails the committed base tool's pristine behavior. A byte-presence-only invalid-UTF-8 case also fails pristine because parsing is position-dependent. Under the inherited r39 scoring rule, a strict UTF-8 decode mutant crashes and is not counted as killed. These are bounded, directly reproducible constraints for the candidate fixture and mutant list.

**Distinct item-12 angle — position-dependent replacement tolerance (“mojibake-tolerant accept”):** the base parser replaces invalid UTF-8, then its schema accepts the replacement character inside a REPO name and skips it in comments. Invalid bytes are refused only when placed in a schema-constrained field. A class-only fixture can therefore claim invalid-byte coverage while missing important decoder defects.

No production files or frozen claims were changed. The only lane write is this assigned report.

## Evidence chain and falsifiers

Base revision `0242085909fb6a4ee041c5443d76316ac6d59d4b` is the preregistration's stated round-39 verified tip. `git cat-file -t` returned `commit`; the lane root check returned `/home/vgpnk/Projects/shokunin/souji-shokunin`. The committed `tools/souji-worktree-drift.py` bytes were extracted to scratch; `git diff --stat <base> -- tools/souji-worktree-drift.py` was empty (working-tree tool bytes matched base).

### 1. Duplicate TOTAL is accepted, last row wins

Source: committed base tool, `parse_record()` at extracted `tool-base.py:120-157` (original tool lines shown by `read` around 120-157). Each TOTAL match assigns `total = {...}` and continues; there is no duplicate-TOTAL check. Only after the loop is the retained `total` checked against REPO rows. By contrast, REPO names are checked for duplicates immediately.

Executed probes against the extracted base tool, using two committed-shape alpha/beta repositories:

- `R1 dup-TOTAL identical x2`: **rc=0**, `record_repos=2 ... drift_rows=0`.
- `R2 dup-TOTAL first-bad last-good`: **rc=0**, `record_repos=2 ... drift_rows=0`.
- `R3 dup-TOTAL first-good last-bad`: **rc=2**, `REFUSAL RECORD-MALFORMED: TOTAL repos=9 but 2 REPO rows`.

Thus a refusal-expecting duplicate-TOTAL case fails the pristine candidate and triggers the frozen C3 kill condition. A passing case must assert the current last-wins behavior (including an order-sensitive pair); this does not by itself falsify coverage, but it constrains it. Further, any declared mutant that breaks single-TOTAL validation (for example, removing the TOTAL consistency check) is already killed by r39 base-fixture cases `total-repos-mismatch`, `total-regs-mismatch`, and `total-prunable-mismatch`; it would violate `base_killed=0`. A base-surviving duplicate mutant must preserve single-TOTAL behavior, e.g. first-wins.

### 2. Invalid UTF-8 is position-dependent

Source: base `parse_record()` decodes with `decode("utf-8", "replace")`; then it skips blank/comment lines, matches `ROW` whose name group is `[^	]+`, and rejects other schema mismatches. The ROW regex is at original tool lines near its declaration; parser behavior is at `parse_record()`.

Executed probes:

- `R4 0xFF in REPO name`: **rc=1**, drift row `DRIFT\tABSENT\ta�b\trecorded regs=1` (replacement character in the name was accepted as a row; the other fleet repos were also reported unrecorded).
- `R5 0xFF in regs field`: **rc=2**, `RECORD-MALFORMED: line 1 does not match the census schema`.
- `R6 0xFF in comment line`: invalid byte was skipped as comment content; the one recorded alpha repo passed, with only unrecorded beta reported.

Therefore “invalid UTF-8 record bytes are refused” is false for the committed base tool and would fail pristine if tested literally. A passing fixture must locate invalid bytes in a schema-constrained position to assert refusal, and should separately assert name-position replacement if it intends to cover byte-decoding behavior rather than only schema rejection.

The committed r39 scoring contract is explicit in `census/round-39/c3-counter.py:64-79`: a kill is `returncode == 1 and fails > 0 and not crash`; traceback makes `crash=True`. I applied three one-line decode variants to a scratch copy and ran the same invalid-byte probes:

- strict decode: **rc=1 with traceback** on both name- and schema-position probes; per r39 scoring this is **not killed**. If r40 declares this mutant while retaining this scoring rule, it necessarily survives.
- ignore decode: schema-position probe changes from refusal (rc=2) to acceptance/drift (rc=1); a corresponding fixture can kill it.
- latin-1 decode: schema-position probe still yields the same schema refusal class; name-position probe remains accepted, but the drift name changes from `a�b` to `aÿb`. A fixture checking only rc or `ABSENT` class will not distinguish this mutant. Exact name/output evidence is required to kill it.

This establishes the item-12 failure mode: a coarse invalid-byte test may pass pristine while leaving a decoder mutant alive; the counter's no-traceback kill rule also makes strict-decode a non-kill.

### 3. `--skip-unrecorded` behavior and r39 control

Source: base tool `run()` around original lines 367-384 gates discovery of unrecorded repositories with `if not args.skip_unrecorded`; CLI defines the flag with `action="store_true"` near line 438.

With a real unrecorded `gamma` repository and alpha/beta in the record:

- without flag: **rc=1**, `DRIFT UNRECORDED gamma` and `drift_rows=1`;
- with `--skip-unrecorded`: **rc=0**, `drift_rows=0`.

Control evidence: committed `tests/fixtures/r38-drift-record.py` (used as r39 base fixture) lists ten cases at extracted `fixture-r38-base.py:86-117`; none passes `--skip-unrecorded`, includes duplicate TOTAL, or supplies invalid UTF-8 bytes. Committed r39 candidate fixture `tests/fixtures/r39-drift-record-rules.py:83-111` has seven cases for trailing whitespace, TOTAL-before-REPO ordering, CRLF, outside-root, indented comment, TOTAL-only, and good record; no skip flag or invalid UTF-8. Its TOTAL ordering case is not a duplicate-TOTAL case. This supports the frozen control for these three branch classes.

## Exact commands and observed outputs

All commands below were actually run. Scratch was `/fast/scratch/hyaku/souji-r40/R40revenger12` with explicit `TMPDIR`; fixture git commands used `git -C <exact-repository-dir> ...`, checked `rev-parse --show-toplevel` before committing, and committed only inside scratch.

1. `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse --show-toplevel && git log --oneline -3 && git cat-file -t 0242085909fb6a4ee041c5443d76316ac6d59d4b && git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py | wc -l`
   Output: lane root as above; tip `be4cb61`; base object type `commit`; source length `451` lines.
2. `git show <base>:tools/souji-worktree-drift.py`, `git show <base>:tests/fixtures/r39-drift-record-rules.py`, and `git show <base>:tests/fixtures/r38-drift-record.py` were saved under scratch. Output line counts: `451`, `141`, `149`; `git diff --stat <base> -- tools/souji-worktree-drift.py` produced no diff.
3. `export TMPDIR=/fast/scratch/hyaku/souji-r40/R40revenger12 && python3 -B "$TMPDIR/probe_c3.py" 2>&1`
   Output included the P1/P2/P3/P4 results recorded above. The first attempt failed before running probes because scratch fixture commits lacked git author identity; I added fixture-local author/committer environment values (no global config change) and reran successfully.
4. `export TMPDIR=... && cd "$TMPDIR" && grep -n "skip\|TOTAL\|xff\|\\\\x\|b\"\|b'" fixture-r39.py | head -25; grep -c "run_case\|def case" fixture-r39.py; python3 -B fixture-r38-base.py --tool tool-base.py --work "$TMPDIR"; python3 -B fixture-r39.py --tool tool-base.py --work "$TMPDIR"`
   Relevant outputs: r39 fixture source documents its existing cases; `run_case` count `9`; r38 fixture `SUMMARY cases=10 pass=10 fail=0`; r39 fixture `SUMMARY cases=7 pass=7 fail=0`.

## Bounded measurement plan

To keep the frozen C3 predicate measurable rather than fail its own controls:

1. Duplicate TOTAL: pristine assertions must match last-wins acceptance and last-row consistency (e.g. first inconsistent/last consistent accepted; first consistent/last inconsistent refused). Declare a mutant that changes only multi-TOTAL ordering (first-wins) so single-TOTAL r39 controls survive.
2. `--skip-unrecorded`: include an actual unrecorded git repo; assert default emits its UNRECORDED row and the flag suppresses it.
3. Invalid UTF-8: include a schema-position byte to kill a crash-free ignore mutant, and assert the exact replacement-bearing name/output for a name-position byte to distinguish latin-1. Do not declare strict-decode as a mutant under the no-traceback kill rule; if declared, classify it as a required survivor/falsifier rather than claiming it is killed.
4. Keep the base fixture arm: all selected mutants must be shown to survive its own failure-summary contract, not merely inferred from their names.

No tools were installed or updated.