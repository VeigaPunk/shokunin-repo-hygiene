STATUS: PARTIAL — I traced the case from source alone: the r20-input-binding step, exit code 0, stdout fully conforming, and stderr carrying a `SUMMARY`-prefixed line. On base 41553adb the source gives `matched: True`, which is a false green. The repaired summarizer should give `matched: False`. One compatibility prerequisite is still open. It needs the real producer's success-path stderr, and the contract does not let me read `tests/fixtures/r20-input-binding.py`. Nothing was executed.

Seat: SoujiR22.Stderr4 (scout, leaf). Axes: calibration, operability, coverage.
Sources read: only the named files, `census/round-21/run-acceptance.py`, `census/round-21/step-inventory.json`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, plus a targeted grep of `corpus/QUALITY.md`. `census/round-14/cache-demonstration.py` was not needed for this question. No LSP device was used, because this question needs only intra-function control flow in one file. Every claim below comes from reading that source (SOURCE-INFERRED). None was executed.

## Step under test (frozen, `step-inventory.json` lines 49–71; `run-acceptance.py` lines 283–290)

- `kind`: summary
- `expected_summary` is a dict. The regex is `SUMMARY\ttotal=52\tpass=52\tfail=0\tblocked=0\tinventory=exact\tbaseline_mismatches=(\d+)`.
- `auxiliary_lines` is `["INVENTORY\texact\texpected=52 observed=52 missing=- unexpected=- duplicates=0"]`.
- `baseline_mismatch_group=1`, `baseline_mismatch_count=true`.
- `pass_pattern` is `^CASE\tpass\t` and `pass_count=52`.

## How the base source handles it (`summarize_result`)

1. Line 352: `summary_lines` is built from **stdout only**. A `SUMMARY` line on stderr never reaches `summary_lines` or `observed_summary` (line 364).
2. Line 353: `failure_lines` does scan stdout plus stderr, but it only recognises the `FAIL\t`, `CASE\tFAIL\t` and `CASE\t<x>\tFAIL` prefixes (lines 330–333). A line that starts with `SUMMARY` never matches.
3. Line 367 sets `matched = returncode == 0 and not failures`. Line 417 adds `summary_match and pass_match`. **The summary branch has no stderr term.** The counter branch (line 445) and the cache-demo branch (line 480) both have one.
4. Lines 642 and 655: `all_matched` and the exit code take each step's `matched` as is.
5. The replay-matrix signature (name, returncode, observed_summary, matched_counts, matched; AttackRunnerStepResults lines 29–31) leaves out stderr. So the three replay signatures stay equal, and the matrix cannot show this either.

## Literal vectors

Every vector shares this stdout control (P):
- returncode `0`;
- 52 lines matching `^CASE\tpass\t`;
- exactly one line `INVENTORY\texact\texpected=52 observed=52 missing=- unexpected=- duplicates=0`;
- exactly one line `SUMMARY\ttotal=52\tpass=52\tfail=0\tblocked=0\tinventory=exact\tbaseline_mismatches=0`;
- zero `BASELINE_MISMATCH\t` lines.

| id | stderr bytes | base `matched` | repaired `matched` | discriminating |
|---|---|---|---|---|
| P0 | empty | True | **True** | no (positive control) |
| S1 | `SUMMARY\ttotal=52\tpass=51\tfail=1\tblocked=0\tinventory=exact\tbaseline_mismatches=0\n` | True | **False** | yes |
| S2 | the stdout SUMMARY line duplicated verbatim, plus `\n` | True | **False** | yes |
| S3 | `SUMMARY FAIL\n` (space separator, still matches `SUMMARY_RE`) | True | **False** | yes |
| C1 | `CASE\tFAIL\tx\n` (vocabulary control) | False | False | no: line 353 already catches it |
| C2 | S1's stderr, with the stdout SUMMARY line removed | False | False | no: `summary_lines == []` fails line 376 |

S1, S2 and S3 all produce the same base record: `failure_lines=[]`, `observed_summary=[<the stdout SUMMARY>]`, `matched_counts.summary_lines=1`, `observed_pass_lines=52`, `baseline_mismatch_records=0`, `baseline_mismatches_reported=0`, `matched=True`.

## Compatibility requirements for the repair

1. **Predicate shape:** the gate MUST be "any non-empty stderr ⇒ `matched=False`" in the summary branch, matching lines 445 and 480. It MUST NOT be a `SUMMARY`/`ERROR` prefix pattern on stderr. A prefix pattern only special-cases one input: AttackRunner's `ERROR: self-test could not complete` example and arbitrary stderr text would stay green.
2. **Record projection unchanged for positive controls:**
   - Keep `summary_lines` and `observed_summary` stdout-only.
   - Keep the `matched_counts` key set unchanged.
   - Do not fold stderr into `summary_lines`. That would happen to reject S2 and S1 through the count check, but it changes `observed_summary` semantics and the matrix tuple.
   - With empty stderr, every field of the 18 real records stays byte-identical, so the historical outcome projections hold.
3. **Code-level gate, not a step key:** `inventory_projection` (lines 542–543) copies only named keys. A new per-step key such as `stderr_empty` would never be bound by the frozen inventory check (line 601), so the expectation would be unbound. A universal code gate needs no change to `step-inventory.json`.
4. **Positive-control prerequisite (UNRESOLVED):**
   - What is required: the real `r20-input-binding.py` must write zero stderr bytes on its success path at the measured revision. The same holds for the other ten summary-kind steps, `agreement-pin-check` included.
   - Why it is open: I cannot see it from the allowed sources.
   - How L1 settles it: from the all-18 real positive-control run.
   - If any real step writes success-path stderr, the repair turns a true positive red. That must be reported, not loosened.
5. **Strictness edge:** stderr consisting only of `b"\n"` or other whitespace is non-empty, so it is False under the repair. That matches counter and cache-demo semantics. Any tolerance would be a new, unreviewed policy.
6. **No interaction with F5:** the change is confined to `summarize_result` in `census/round-21/run-acceptance.py` (or its round-22 successor). The F5 parser/formatter and the 160-byte synthetic-only reason scope are untouched.

## Draft repair (source only, not applied)

Replace line 417 in `summarize_result`:

```python
        matched = matched and summary_match and pass_match and not stderr
```

## Remaining unknowns

- Whether real summary-kind producers emit stderr on success (requirement 4).
- Whether L1's round-22 runner is a new file or an edit of the round-21 one. That decides which digest pins in `INPUT_PATHS` must move.

Tools installed: none.

Report: .ufo/waves/round-22/w1/Stderr4.md
