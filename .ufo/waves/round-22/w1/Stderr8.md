STATUS: PASS — Under base `census/round-21/run-acceptance.py`, a stderr made of one newline (`b"\n"`) on `r18-landing-pointers`, with return code 0 and passing stdout, is a false green: `matched` comes out `True`. After the repair the literal expected value is `matched: false`. Positive-control compatibility needs the real fixture's stderr to be exactly zero bytes. That last point is a source-only inference that this seat cannot check inside its read contract; L1 acceptance must observe it. Source-only review; nothing was executed.

## Axes
calibration (fixes a predicate false green), operability (no new inputs or arguments), coverage (one stderr/control combination the other seats did not take). No trade between axes.

## Vector (synthetic; source-inferred decision)

Step row: `make_steps` in `census/round-21/run-acceptance.py`, lines 299–300, which matches `census/round-21/step-inventory.json` lines 113–126:
`expected_summary = "SUMMARY\ttotal=11\tfailed=0"`, `pass_pattern = r"^CASE\tPASS\t"`, `pass_count = 11`, kind `summary` (the default).

| field | value |
|---|---|
| returncode | `0` |
| stdout | 11 lines starting with `CASE\tPASS\t`, then `SUMMARY\ttotal=11\tfailed=0\n` |
| stderr bytes | `b"\n"` (1 byte; sha256 `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b`) |
| base `matched` | `True` (false green) |
| expected changed `matched` | `False` |

### Base trace (lines 350–419, 481)
- `stderr = decode_exact(b"\n")` gives `"\n"`, which is truthy. The `surrogateescape` decoding is a bijection, so empty bytes map to `""` and only to `""`.
- `failure_lines(stdout + "\n" + "\n")` (line 353): the separator is added because both streams are non-empty. `splitlines()` produces only empty extra lines, none matching `FAIL\t`, `CASE\tFAIL\t` or `CASE\t…\tFAIL`, so `failures == []`.
- Line 367 gives `matched = True`. `summary_lines == [expected]`, the auxiliary lists are `[] == []`, and `baseline_mismatch_count` is not set. `pass_count` from `re.findall(..., re.MULTILINE)` is 11, so line 417 keeps `True`. The step is not `carry-invariant-probe`, so lines 418–419 are skipped. Line 481 records `True`.
- In this same runner, the counter branch (line 445) and the cache-demo branch (line 480) gate on `not stderr`. They would reject `"\n"`, so the summary branch is the only one that accepts it. That is the r21 HIGH finding (`.ufo/waves/round-21/w2/AttackRunnerStepResults.md` lines 11–15), applied here to the smallest non-empty stderr.

## Expected decision and why

`matched: false`. The repaired predicate MUST treat any non-empty stderr byte string as a failure, including a single newline.

- **Rejected inference (for SOURCES):** "whitespace-only stderr is benign, so `not stderr.strip()` is enough." This would make `"\n"` pass. It brings back a summary-only weaker rule than lines 445 and 480 apply. It also makes the predicate depend on byte content that the record only keeps as `stderr`/`stderr_sha256` and that the matrix signature leaves out (r21 review line 31). Rejected on consistency grounds: one stderr rule across all three kinds.
- Byte-exact emptiness (`not stderr_bytes`, which is equivalent to `not stderr`) is the only rule that matches the existing counter and cache-demo semantics without adding a whitespace exception.

## Draft repair (for L1 to integrate; F5 not touched)

Put the existing per-branch stderr gate on the common `matched` seed so that summary, counter and cache-demo share one rule, and drop the two duplicates:

```python
    matched = returncode == 0 and not failures and not stderr
```

with line 445 becoming `matched = matched and json_match` and line 480 becoming `matched = matched and demo_match`. A smaller alternative with the same decisions is to change only line 417:

```python
        matched = matched and summary_match and pass_match and not stderr
```

Both forms give `False` for this vector and change no counter or cache-demo decision.

## Compatibility requirement

1. **Positive control (real step):** after the repair, the committed `tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py` must still give `matched: true`. That requires its process stderr to be exactly 0 bytes (`stderr_sha256 == e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`). If the fixture writes even a trailing newline to stderr, the repaired runner turns this historical positive control red.
2. **Historical projection:** the retained r21 acceptance record's `r18-landing-pointers` entry must have `stderr == ""`. Only then does the repaired predicate reproduce its historical `matched: true`. A non-empty historical stderr would mean the repair changes an exact historical outcome, and that has to be disclosed rather than shown as an unchanged projection.
3. The same zero-byte requirement holds for every other summary step among the 18. This seat only analyzed `r18-landing-pointers`.

## Observed facts, inferences and gaps
- **Observed (source text):** the line references above, the inventory row, and the branch asymmetry.
- **Inference:** that the real fixture emits empty stderr. A typical fixture captures the gate subprocess's own stderr instead of passing it through, but that is unverified. [INFERENCE]
- **Unresolved, and outside this seat's read contract:** the fixture source (`tests/fixtures/r18-landing-pointers.py`) and the retained r21 acceptance output are not among the named files and were not opened. L1 acceptance after integration has to observe requirements 1 and 2.
- Confidence: high for the base `True` and changed `False` decisions (they follow from the source); unknown for the compatibility of the real control.

## Process
I read only the six named files; no directory, broad-glob or grep reads. No LSP device was available in this session, so the semantic trace is from reading source. No tests, builds or probes were run. No tools were installed.
