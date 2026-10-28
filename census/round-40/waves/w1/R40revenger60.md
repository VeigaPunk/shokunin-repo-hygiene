# R40revenger60 — coverage claim attack: invalid-byte harness failure mode

- Seat: revenger (leaf; no dispatch)
- Distinct item 60 edge: **invalid UTF-8 fixture I/O / output-decoding failure**, specifically whether the proposed invalid-UTF-8 record case can be represented and scored as a fixture-owned behavioral case rather than crashing the fixture harness.
- Frozen claim read first: `census/round-40/preregistration.txt:10`.
- Scope: committed r39 evidence only; no candidate r40 fixture/counter existed in the lane inventory at inspection time. No production or frozen files changed.
- Tool installs/updates: none; pacman untouched.

## Evidence chain

1. Frozen C3 (`census/round-40/preregistration.txt:10`) requires behavioral cases for duplicate/multiple TOTAL rows, `--skip-unrecorded`, and invalid UTF-8 record bytes. Each declared mutant must be killed by the r40 fixture, pristine must pass, r39 baseline mutants survive, and fixture must have its own failure summary.
2. The committed r39 candidate fixture demonstrates its output-capture boundary at `tests/fixtures/r39-drift-record-rules.py:67-80`: it writes record data as text with UTF-8 encoding at lines 70-71 and launches the tool with `text=True` at lines 72-75, then judges the returned string and records a case result at lines 76-80. Its byte-oriented CRLF case uses valid UTF-8 bytes at lines 94-104. There is no invalid-byte input case in its enumerated `run_cases` at lines 83-114.
3. The r39 counter's score predicate (`census/round-39/c3-counter.py:87-103`) only counts a kill if the fixture returns exit 1, has a parsed `SUMMARY cases=...` with `fail>0`, and has no traceback. Thus a decode exception before fixture-owned result/summary is not a valid mutant kill under the existing scored contract.
4. The baseline receipt (`census/round-39/records/c3-before.txt:2-9`) records the pre-r39 fixture on the exact four M11-M14 controls as pristine, `cases=10`, `killed=0`, `survived=4`; after receipt `census/round-39/records/c3-after.txt:2-8` records r39 candidate outcomes, not the new r40 mutants or invalid-byte behavior.

## Failure mode and bounded measurement plan

A fixture can write malformed bytes correctly while its `subprocess.run(..., text=True)` output decoding raises `UnicodeDecodeError` if the target emits those bytes to stdout/stderr. Such a run can terminate before the fixture emits its required own summary. That is a harness/evidence failure, not evidence that the tool correctly or incorrectly classified invalid record bytes. Also, writing a Python `str` containing a lone surrogate via the current UTF-8 text path is not equivalent to injecting arbitrary invalid bytes; the case must use binary `write_bytes`/`write` input.

Bounded measurement at the explicit candidate revision: (a) build a record containing an invalid byte using a binary write; (b) run pristine and the declared invalid-byte mutant with byte-captured stdout/stderr (or explicit replacement decoding); (c) verify the fixture itself emits exactly one parseable `SUMMARY cases=... pass=... fail=...`, exits 0 pristine and exit 1 with `fail>0` under the mutant, with no uncaught traceback; (d) assert the observed tool classification/output for the invalid record using bytes-safe matching; (e) run the same mutant against the committed r39 baseline fixture and require it survives under the counter's established scoring rule. Keep the negative control distinct: a harness-crash case must not be counted as a kill merely because the subprocess exits nonzero.

The same plan should be applied separately to duplicate TOTAL and `--skip-unrecorded`; this seat's falsifiable attack is limited to the invalid-byte harness boundary and does not claim those branches are absent or defective.

## Commands and outputs actually observed

- `read /home/vgpnk/.omp/agent/RULES.md` — returned tooling rules; no installs performed.
- `read skill://godspeed` — returned skill instructions.
- `read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt` — returned frozen predicates, including C3 at line 10.
- `glob /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39` — listed committed r39 counter, fixture receipts and wave reports.
- `glob /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures` — listed `r39-drift-record-rules.py` and `r38-drift-record.py` among fixtures.
- `read .../tests/fixtures/r39-drift-record-rules.py:39-117` — returned the text write/subprocess capture and case list cited above.
- `read .../census/round-39/c3-counter.py:47-62` and `:86-191` — returned mutant definitions and scoring/control flow.
- `read .../census/round-39/records/c3-before.txt` and `.../records/c3-after.txt` — returned exact prior receipts cited above.
- No shell commands, fixture executions, candidate counter executions, scratch files, git/jj mutations, builds, tests, linters, or formatters were run. Those outcomes are **unrun, not pass**.

## Verdict

**C3 r40 coverage: NOT MEASURED; no concrete falsifier observed.** The committed r39 harness does not exercise invalid UTF-8 input and uses text-mode subprocess decoding, while r40's frozen claim explicitly adds invalid UTF-8 bytes and requires a fixture-owned failure summary. This establishes a concrete, bounded harness failure mode to test, not a claim that the absent r40 candidate fails. Candidate source and receipts are unavailable in the inspected lane snapshot, so pristine pass, mutant kills, and baseline survival remain unmeasured.
