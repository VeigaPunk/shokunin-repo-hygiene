STATUS: PASS — I derived the literal success contract for `r20-audit-contract` from source, built one valid positive vector and one wrong-summary vector specific to this step, and identified what the stderr policy change does to it. Everything here is SOURCE-INFERRED: nothing was run.

## Observed contract (source)

- **Step definition.** `census/round-21/run-acceptance.py` `make_steps`, lines 280–282, matches the frozen row in `census/round-21/step-inventory.json`, lines 33–48:
  - name: `r20-audit-contract`
  - argv: `<PYTHON> -B <ROOT>/tests/fixtures/r20-audit-contract.py --tool <ROOT>/tools/souji-seat-audit.py --base-tool <BASELINE>`
  - expected_summary (string): `SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11`
  - pass_pattern `^CASE\tPASS\t`, which is uppercase and differs from the lowercase `pass` pattern used by the revision-helper, input-binding and r19 steps.
  - pass_count `78`, with no `baseline_mismatch_count` and no `record_checks`.
  - `kind` is absent from `make_steps`, so `step.get("kind", "summary")` makes it `summary`; the frozen row records `"kind": "summary"`.
- **Success predicate.** `summarize_result` evaluates the summary branch (lines 347–419). `matched` is true only when all of these hold:
  1. `returncode == 0`.
  2. `failure_lines(stdout + "\n"? + stderr)` is empty (lines 330–333 and 353). The checker looks for lines that start with `FAIL\t` or `CASE\tFAIL\t`, or that match `^CASE\t[^\t]+\tFAIL(\t|$)`. It scans stdout and stderr joined together.
  3. `summary_lines == [expected]`. Here `summary_lines` is every line from `stdout.splitlines()` that matches `^(?:SUMMARY|SELFTEST)(?:\t| ).*$` (lines 118 and 352). So exactly one such line must exist, and it must be byte-equal to the expected string.
  4. Stdout contains no line starting with `INVENTORY\t`. The expected string gives `expected_auxiliary = []`, so the observed list must also be empty (lines 375 and 385–390).
  5. `len(re.findall(r"^CASE\tPASS\t", stdout, re.MULTILINE)) == 78`. The count must be exactly 78, and it is taken over stdout only (lines 400–404).
  6. Stderr is never checked for emptiness in this branch. The only stderr effect is through `failure_lines`. By contrast, the counter branch (line 445) and the cache-demo branch (line 480) both require `not stderr`.
- **Aggregation.** `all_matched = all(item["matched"] ...)` (line 642). The process exits `0 if all_matched else 1` (line 655).

## Positive stdout vector (expected decision: PASS on base and on the changed implementation)

The vector is return code `0`, stderr `b""`, and this stdout:

```text
CASE\tPASS\tsynthetic-01\n
... (synthetic-02 … synthetic-77, one per line) ...
CASE\tPASS\tsynthetic-78\n
SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11\n
```

Here `\t` means a real tab byte. Expected `matched_counts` are `summary_lines=1`, `observed_pass_lines=78`, `observed_auxiliary_lines=0`, and `failure_lines=[]`.

Two constraints on the case IDs:
- No ID may be `FAIL`. A line such as `CASE\tPASS\tFAIL\t…` would match `^CASE\t[^\t]+\tFAIL(\t|$)` and turn the vector red.
- The IDs must not create any `SUMMARY`/`SELFTEST`/`INVENTORY\t`-prefixed line.

## Wrong-summary vector specific to this step (expected decision: FAIL on base and on the changed implementation)

The vector `r20-summary-missing-base-discriminating` has return code `0` and stderr `b""`. Its stdout is the same 78 `CASE\tPASS\t` lines, followed by `SUMMARY\ttotal=78\tpass=78\tfail=0\n`, so the `base_discriminating=11` field is missing.

This is the step-unique contract element. `r20-audit-contract` is the only step whose acceptance depends on `--base-tool` discrimination, written as a tab-separated `base_discriminating` field. The r19 steps use space-separated `base_discriminating=` with other values. A producer that silently skipped the baseline comparison would still emit 78 passing cases.

The failure mechanism is check 3 above: `summary_lines` is `["SUMMARY\ttotal=78\tpass=78\tfail=0"]`, not `[expected]`, so `summary_match` is false. The pass count stays 78, which isolates the summary check from the pass-count check.

This vector is a no-loosening control, not a base false-green: base already rejects it. If L1 prefers a pass-count control, use 78 lowercase `CASE\tpass\t` lines with the correct SUMMARY line. That vector is also unique to this step's uppercase pattern: `observed_pass_lines=0`, so it FAILs on both base and the changed implementation.

## Stderr policy impact

- **Base false-green (source-inferred).** The positive stdout above with return code `0` and stderr `b"error: base tool comparison aborted\n"` gives an empty `failure_lines`, a summary match, and a pass match. The base decision is therefore matched=True and `all_matched` can stay true. This step is exposed to admitted defect "summary stderr accepted despite success".
- **What base already rejects.** If the stderr text contains a failure marker line, such as `CASE\tFAIL\tx`, base already rejects it, because stderr is joined into `failure_lines`. A discriminating vector must use non-marker stderr.
- **Repair.** Under the repair (summary branch requires `not stderr`, matching counter/cache), the expected decision for the stderr vector is FAIL. The positive vector stays PASS because its stderr is `b""`.
- **Real positive-control risk [INFERENCE, unresolved].** The real `r20-audit-contract` step stays green after the repair only if the real fixture writes nothing to stderr. It drives both the current and the baseline auditor. I did not read or run `tests/fixtures/r20-audit-contract.py` because it was not on the permitted file list, so whether its real stderr is empty is unobserved. L1's acceptance run must confirm `stderr == ""` for this step, or the repair will turn one of the 18 real positive controls red.

## Draft oracle rows (report-only)

This draft loads the frozen row, so the vectors stay bound to the committed inventory instead of a duplicated literal. For the summary kind, `summarize_result` does not use `revision` or `root`.

```python
import json
from pathlib import Path

def r20_step(root: Path) -> dict:
    rows = json.loads((root / "census/round-21/step-inventory.json").read_bytes())["steps"]
    (row,) = [row for row in rows if row["name"] == "r20-audit-contract"]
    return row

R20_PASS_LINES = b"".join(b"CASE\tPASS\tsynthetic-%02d\n" % i for i in range(1, 79))
R20_SUMMARY = b"SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11\n"

# (vector id, returncode, stdout, stderr, expected base matched, expected changed matched)
R20_VECTORS = (
    ("r20-positive", 0, R20_PASS_LINES + R20_SUMMARY, b"", True, True),
    ("r20-summary-missing-base-discriminating", 0,
     R20_PASS_LINES + b"SUMMARY\ttotal=78\tpass=78\tfail=0\n", b"", False, False),
    ("r20-summary-stderr", 0, R20_PASS_LINES + R20_SUMMARY,
     b"error: base tool comparison aborted\n", True, False),
)
```

## Scope and gaps

- Scalar-type equality and cache-check identity do not apply to this step: it is `summary` kind with a string `expected_summary`, compared as exact strings.
- CRLF behavior was not used in any vector. `splitlines` would strip `\r\n`, and MULTILINE `^` still matches after `\n`, so a CRLF variant of the positive vector would also PASS on base. This is source-inferred and not part of any recommended vector.
- No `lsp` device was available in this session for Python semantic tracing, and no grep was used as semantic proof. All findings come from direct reads of the named files.
- Files read: `census/round-21/run-acceptance.py`, `census/round-21/step-inventory.json`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, plus a targeted grep of `corpus/QUALITY.md`. `census/round-14/cache-demonstration.py` was not needed.
- No tools were installed, and no tests, builds or probes were run.

Report: .ufo/waves/round-22/w1/Summary3.md
