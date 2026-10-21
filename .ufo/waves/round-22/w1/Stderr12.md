STATUS: PASS — agreement-pin-check × timeout-returncode analysed from source only. Every timeout-shaped non-zero/None return code yields literal `matched = False` on base AND on any stderr-repaired summarizer (non-discriminating negative controls); the only discriminating timeout-adjacent vector is return code 0 with non-empty stderr (base `True` → changed `False`). Nothing was executed; no tools installed.

Seat: SoujiR22.Stderr12 (leaf scout). Base 41553adb139d06511dc386bb3ce4326aebfba675 as named by the wave; files read are the working-tree bytes of the named paths (revision binding of those bytes NOT independently checked — no git/build/test run).

## Observed source facts (read, not executed)

1. Step definition — `census/round-21/run-acceptance.py:310-311` and frozen row `census/round-21/step-inventory.json:169-185`: `agreement-pin-check` is `kind` summary (default), `expected_summary: ""`, `pass_pattern: null`, `pass_count: 0`, `record_checks: 1`.
2. No timeout exists in the runner. Step execution `run-acceptance.py:613-619` calls `subprocess.run(step["argv"], cwd=root, env=CHILD_ENV, stdout=PIPE, stderr=PIPE)` with no `timeout=`; only `OSError` is caught (→ `returncode=None`, stderr `"invocation failed: ..."`). A "timeout return code" can therefore only reach `summarize_result` as (a) a code the child itself returns (e.g. a coreutils `timeout` wrapper inside it), (b) a negative signal number if the child is killed, or (c) a synthetic oracle vector.
3. Summary-branch gate — `run-acceptance.py:367` `matched = returncode == 0 and not failures`; `:417` `matched = matched and summary_match and pass_match`. No stderr term in the summary branch (counter `:445` and cache-demo `:480` have `and not stderr`). This is the admitted r21 defect (`.ufo/waves/round-21/w2/AttackRunnerStepResults.md:11-15`).
4. For this step every stdout predicate is vacuous on empty stdout: `summary_lines == []` (`:373`, `expected` is `""`), `observed_auxiliary == []` (`:386-389`), `baseline_mismatch_count` absent (`:394`), pattern `None` → `pass_count 0 == 0` (`:400-404`). `record_checks` is only copied into `matched_counts` (`:415`), never gated.
5. `failure_lines` (`:330-333`) recognises only `FAIL\t`, `CASE\tFAIL\t`, `CASE\t<x>\tFAIL`; a timeout diagnostic such as `timeout: sending signal TERM to command ...` is not matched.
6. `main` catches `(OSError, ValueError, RuntimeError, Refusal, KeyError)` only (`:652`).

## Public authority opened this seat

- Python `subprocess` docs, https://docs.python.org/3/library/subprocess.html: `CompletedProcess.returncode` "A negative value -N indicates that the child was terminated by signal N (POSIX only)"; `run(timeout=...)` kills the child and re-raises `TimeoutExpired`; `TimeoutExpired` is a "Subclass of `SubprocessError`" and "Exceptions defined in this module all inherit from `SubprocessError`" (not `OSError`).
- coreutils `timeout(1)` (coreutils 9.11), https://man7.org/linux/man-pages/man1/timeout.1.html: exit 124 on timeout without `--preserve-status`; 125 timeout itself fails; 126/127 cannot invoke/find; 137 KILL (128+9); `--preserve-status` exits with COMMAND's status even on timeout; `-v` diagnoses the sent signal "to standard error".
- (gnu.org manual URL returned HTTP 403; man7 copy used instead.)
- `False == 0` / bool-subclass-of-int: language semantics, NOT re-opened by this seat — L1's preregistered authority (preregistration.txt) covers it. [INFERENCE until cited by L1's SOURCES row.]

## Literal vectors for the synthetic result oracle (agreement-pin-check row)

All vectors call `summarize_result(step, rc, stdout, stderr, REV, ROOT)` with the exact agreement-pin-check step dict. "changed" = base summary branch plus an exact-emptiness stderr term (`and not stderr`, same predicate as counter/cache branches). Expected values derive from items 3–5 above.

| id | returncode | stdout | stderr | base matched | changed matched | discriminating |
|---|---|---|---|---|---|---|
| T1 | `124` | `b""` | `b""` | `False` | `False` | no |
| T2 | `124` | `b""` | `b"timeout: sending signal TERM to command 'verify'\n"` | `False` | `False` | no |
| T3 | `137` | `b""` | `b""` | `False` | `False` | no |
| T4 | `-15` | `b""` | `b""` | `False` | `False` | no |
| T5 | `-9` | `b""` | `b""` | `False` | `False` | no |
| T6 | `None` | `b""` | `b"invocation failed: FileNotFoundError: x"` | `False` | `False` | no |
| T7 | `0` | `b""` | `b"timeout: sending signal TERM to command 'verify'\n"` | `True` | `False` | YES |
| T8 | `0` | `b""` | `b"\n"` | `True` | `False` | YES |
| P1 | `0` | `b""` | `b""` | `True` | `True` | positive control |

T7 is the source-grounded shape of `timeout --preserve-status -v` around a child that traps TERM and exits 0 (man7 timeout(1)); T8 pins exact emptiness (a `.strip()` predicate would wrongly keep `True`).

```python
AGREEMENT_STEP = {"name": "agreement-pin-check", "argv": ["<PYTHON>"],
                  "expected_summary": "", "pass_pattern": None,
                  "pass_count": 0, "record_checks": 1}
TIMEOUT_VECTORS = (
    # id,   returncode, stdout, stderr,                                          base,  changed
    ("T1", 124,  b"", b"",                                                       False, False),
    ("T2", 124,  b"", b"timeout: sending signal TERM to command 'verify'\n",     False, False),
    ("T3", 137,  b"", b"",                                                       False, False),
    ("T4", -15,  b"", b"",                                                       False, False),
    ("T5", -9,   b"", b"",                                                       False, False),
    ("T6", None, b"", b"invocation failed: FileNotFoundError: x",                False, False),
    ("T7", 0,    b"", b"timeout: sending signal TERM to command 'verify'\n",     True,  False),
    ("T8", 0,    b"", b"\n",                                                     True,  False),
    ("P1", 0,    b"", b"",                                                       True,  True),
)
```

## Compatibility requirements for the changed summarizer

C1. Keep the strict `returncode == 0` gate first and unchanged: T1–T6 MUST stay `False`. They are non-discriminating (base already `False`) and MUST NOT be counted as evidence for the stderr repair; only T7/T8 discriminate.
C2. The stderr term MUST be exact emptiness (`not stderr` on the decoded string), matching `:445`/`:480`; no strip, no marker vocabulary.
C3. Real positive control: `agreement-pin-check` must still be `matched: True` in L1's 18-step acceptance. That requires `census/round-19/verify-agreement-pin.py` (original bytes staged by `historical_agreement_root`) to write zero stderr bytes on success. UNVERIFIED — that file is outside this seat's named read set; L1's acceptance run is the only check. If it emits benign stderr, the repair turns a retained positive control red (preregistration forbids losing any of the 18).
C4. Do not add `timeout=` to the step `subprocess.run` as part of this claim: `TimeoutExpired` is not in `main`'s except tuple (`:652`), so a timed-out step would crash with a traceback and no record — contrary to "reject malformed producer data without a crash" — and it is outside the three admitted defects.
C5. Oracle encoding: supply `returncode` as a Python `int` or `None`, never JSON `true`/`false`. Base `returncode == 0` accepts `False` (bool is an int subclass) — real `subprocess` never yields a bool, so this matters only if vectors are JSON-decoded. Hardening the gate to `type(returncode) is int` would be an additional claim; L1's call, not recommended under "no additional axis claim".
C6. Step dicts may gain keys without breaking the frozen inventory compare only if the keys are outside the projection tuple at `:542-543`; changing `expected_summary`/`kind`/`pass_*`/`record_checks` for this row breaks `step-inventory.json` equality (`:600-602`).

## Bounded residual (not fixed by the stderr repair)

- A timeout swallowed into return code 0 with empty stdout/stderr is indistinguishable from P1 and stays `True`/`True`: agreement-pin-check has no positive stdout witness and `record_checks: 1` is reported, not enforced. Disclose as a limit; do not claim the repair detects timeouts.

## Verification gaps

- Source-inferred only: no runner, oracle, test, or Python snippet executed; all expected booleans come from reading `run-acceptance.py:330-419`.
- `verify-agreement-pin.py` success stderr behaviour unknown (C3).
- LSP: not available in this session; no definition/reference results claimed. Text reading of named files only; no grep/glob used.
- No tool installs or updates.

Report: .ufo/waves/round-22/w1/Stderr12.md
