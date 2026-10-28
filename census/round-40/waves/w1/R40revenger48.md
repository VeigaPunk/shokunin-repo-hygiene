# R40revenger48 — independent C3 coverage attack

Axes: **coverage** (whether the claim's branch assertions distinguish faults), **operability** (whether the harness can actually measure them), and **provenance** (whether the cited baseline is committed). This report is read-only analysis; no production or frozen claim changed.

## Explicit distinct edge case: decoder replacement of invalid UTF-8 in an otherwise valid record

**Verdict: bounded measurement plan; no concrete falsifier established from the committed r39 artifacts.** The r40 predicate includes invalid UTF-8 record bytes, and r39 fixture/counter artifacts establish a useful baseline but do not establish that the candidate exercises that exact decoding boundary. A potential defect is not itself a falsifier: r39 `parse_record` explicitly decodes with UTF-8 `"replace"`, so malformed bytes may either become a schema refusal (if in a record token) or be silently tolerated when attached to a syntactically valid row only if the byte sequence is placed in ignored/comment text. The latter is the distinct risk to test: an invalid byte in a comment line could be replaced and ignored, meaning a test that merely expects rejection of malformed record content would assert a different behavior from the actual parser contract.

### Evidence chain

- Frozen r40 claim: `census/round-40/preregistration.txt:10-11` requires behavioral cases for duplicate/multiple TOTAL rows, `--skip-unrecorded`, and invalid UTF-8 record bytes, with pristine pass, candidate mutant kills, and all base mutants surviving.
- Committed baseline is the frozen base revision named by preregistration, `0242085909fb6a4ee041c5443d76316ac6d59d4b`; `git rev-parse <rev>^{commit}` returned that full revision. Its tree contains `census/round-39/c3-counter.py`, `tests/fixtures/r39-drift-record-rules.py`, and `tests/fixtures/r38-drift-record.py`.
- `tools/souji-worktree-drift.py:131-149` opens bytes and decodes using `raw.decode("utf-8", "replace")`; `:152-166` then ignores blank/comment lines and rejects nonmatching other lines; `:167-179` rejects records with no REPO rows and checks TOTAL sums.
- `tools/souji-worktree-drift.py:370-383` shows `--skip-unrecorded` suppresses discovery-only drift rows; `:384-429` emits drift rows, summary and status. This is a separate, directly observable branch with an obvious test-design trap: it needs a discoverable but unrecorded repository; a no-extra-repo fixture cannot demonstrate the option.
- The r39 fixture `tests/fixtures/r39-drift-record-rules.py:3-15,87-111` exercises seven record behaviors including only one TOTAL row; no invalid bytes, duplicate/multiple TOTAL, or `--skip-unrecorded` case is present. Its runner sends `--record` and asserts process output.
- The committed r39 receipt `census/round-39/records/c3-after.txt:3-8` reports M11-M14 all killed, base_killed=no, pristine=ok, `cases=7`, fixture SHA `567c37a679f5`; these mutants are trailing-space, splitlines, outside-root, and indented-comment (counter anchors at `census/round-39/c3-counter.py:48-58`). It offers no evidence for any r40 newly named branch.
- The r39 counter at `census/round-39/c3-counter.py:87-103,145-186` scores fixture-produced `SUMMARY cases=... pass=... fail=...`, requires pristine case count >=6, and compares candidate against the base fixture. Thus a future r40 UTF-8 mutant needs its own fixture assertion plus a matching mutation that changes the observed outcome; merely supplying malformed bytes without asserting expected output is not coverage evidence.

### Bounded measurement plan

1. Against the frozen base and candidate revisions, extract the tool and fixtures into explicit seat scratch, never modify the lane's tracked artifacts. Use separate invalid-byte placements: (a) invalid byte in a REPO field, (b) invalid byte in a comment-only line preceding valid rows. Record exact bytes (e.g. `0xff`) and assert the actual intended contract for each; in particular, don't assume all malformed UTF-8 must be rejected because current decoder uses replacement.
2. Add a single-defect decoder mutant (strict UTF-8 decode instead of `errors="replace"`) and require the candidate fixture's own failure summary to show the corresponding assertion failure without traceback. This is discriminating only if the tested bytes cause distinct observable behavior under replacement vs strict decoding. Also run that same mutant against the r39 base fixture and require survival.
3. Separately for `--skip-unrecorded`, build a minimal repository root containing a recorded repo plus a valid discovered unrecorded repo. Assert ordinary mode reports `DRIFT\tUNRECORDED`, skip mode omits that row, and check the `drift_rows`/exit status difference; mutant should remove or invert only the skip gate. The r39 fixture's existing baseline cannot distinguish this option.
4. For multiple TOTAL, include duplicate identical TOTAL and conflicting TOTAL after valid REPO rows. The present parser overwrites `total` on each TOTAL line (`:162-165`), so test an explicit mutant that wrongly rejects a second TOTAL or ignores the final TOTAL. Include one case that pins the intended behavior, rather than infer semantics from the predicate's label.
5. Run the pristine and each declared mutant on candidate and base fixtures with the same counter protocol; preserve per-case summaries and hashes. Verdict is pass only for candidate pristine success + all intended candidate kills + zero base kills, with no crash-based false kill.

### Commands actually run

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/souji-shokunin`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --short` → `?? census/round-40/` (pre-existing untracked r40 census area observed; not changed).
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b^{commit}` → `0242085909fb6a4ee041c5443d76316ac6d59d4b`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only 0242085909fb6a4ee041c5443d76316ac6d59d4b tests/fixtures/ census/round-39/` → listed r39 counter and fixture paths (including both r39 and r38 fixtures).
- Read-only file reads: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt`; `census/round-39/c3-counter.py`; `census/round-39/records/c3-after.txt`; `census/round-39/records/final-tip-measure.txt`; `tests/fixtures/r39-drift-record-rules.py`; `tools/souji-worktree-drift.py`; `.ufo/waves/round-39/w1/W1SimpFixtures.md`.
- No LSP device was available in this seat's tool inventory; semantic line references above are direct source reads, not LSP claims.
- No tests, counter, or runtime were executed; no tool installed or updated.
