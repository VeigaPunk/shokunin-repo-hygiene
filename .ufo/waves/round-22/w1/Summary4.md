STATUS: PASS — r20-input-binding literal success contract derived from source; one positive stdout vector (expected matched=true), one unique wrong-summary vector (expected matched=false), and the stderr-policy impact are given below. Source-inferred only: nothing was executed.

Scope: read only `census/round-21/run-acceptance.py` (base bytes as present in checkout), `census/round-21/step-inventory.json`, `.ufo/waves/round-22/preregistration.txt`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, and a targeted search of `corpus/QUALITY.md` (no relevant hit). Public source opened: https://docs.python.org/3/library/stdtypes.html (str.splitlines boundaries; numeric literal note 6 "digits 0-9 or any Unicode equivalent (Nd)"; bool is an int subclass). `tests/fixtures/r20-input-binding.py` was NOT read (not a named file), so real fixture output is unobserved.

## 1. Literal success contract (observed in source)

Step row: `run-acceptance.py` lines 284-290 == frozen `step-inventory.json` lines 49-71 (row index 3), `kind` defaults to `summary`.

`summarize_result` (lines 347-419), summary branch, sets `matched` true iff ALL of:

| # | Predicate | Source |
|---|---|---|
| C1 | `returncode == 0` | l.367 |
| C2 | `failure_lines(stdout + ("\n" if stdout and stderr) + stderr)` empty: no line starting `FAIL\t` or `CASE\tFAIL\t`, none matching `^CASE\t[^\t]+\tFAIL(?:\t|$)` (case-sensitive) | l.330-333, 353 |
| C3 | exactly one stdout line (via `str.splitlines`) matching `^(?:SUMMARY|SELFTEST)(?:\t| ).*$`, and it `re.fullmatch`es `SUMMARY\ttotal=52\tpass=52\tfail=0\tblocked=0\tinventory=exact\tbaseline_mismatches=(\d+)` | l.118, 352, 376-380 |
| C4 | the list of stdout lines starting `INVENTORY\t` equals exactly `["INVENTORY\texact\texpected=52 observed=52 missing=- unexpected=- duplicates=0"]` (tab after `INVENTORY` and `exact`, single spaces elsewhere) | l.381, 386-390 |
| C5 | `int(group 1)` == count of stdout lines starting `BASELINE_MISMATCH\t` (`baseline_mismatch_count: true` only on this step) | l.382-398 |
| C6 | `len(re.findall(r"^CASE\tpass\t", stdout, re.MULTILINE)) == 52` (exact equality, not ≥) | l.400-404 |
| — | stderr content NOT consulted except through C2 | l.367-419 (no `not stderr`) |

`revision` and `root` are unused in the summary branch, so a synthetic oracle can call `summarize_result(steps[3], ...)` with the frozen inventory row and a dummy root/revision without touching the filesystem (source-inferred).

## 2. Positive vector (expected `matched == True`)

```python
import json
from pathlib import Path
step = json.loads(Path("census/round-21/step-inventory.json").read_text())["steps"][3]
assert step["name"] == "r20-input-binding"
POSITIVE_STDOUT = (
    "INVENTORY\texact\texpected=52 observed=52 missing=- unexpected=- duplicates=0\n"
    + "".join("CASE\tpass\tbinding-%02d\n" % i for i in range(1, 53))
    + "BASELINE_MISMATCH\tbinding-01\n"
    + "SUMMARY\ttotal=52\tpass=52\tfail=0\tblocked=0\tinventory=exact\tbaseline_mismatches=1\n"
).encode("utf-8")
POSITIVE = dict(returncode=0, stdout=POSITIVE_STDOUT, stderr=b"", expected_matched=True)
```

Derivation: C1 rc 0; C2 no FAIL-shaped line (case IDs `binding-NN` never equal `FAIL`); C3 one SUMMARY line, fullmatch, group=`1`; C4 exact one INVENTORY line; C5 1 == 1 BASELINE_MISMATCH line; C6 52 `CASE\tpass\t` matches. `baseline_mismatches=1` (not 0) is chosen so C5 is exercised non-trivially; with `=0` and no mismatch lines the cross-check passes vacuously. Expected `matched_counts`: summary_lines 1, observed_pass_lines 52, observed_auxiliary_lines 1, baseline_mismatch_records 1, baseline_mismatches_reported 1.

## 3. Uniquely relevant wrong-summary vector (expected `matched == False`)

Only this step carries `baseline_mismatch_count`, so the discriminating negative is a summary whose reported mismatch count disagrees with the emitted records:

```python
WRONG_BASELINE_STDOUT = POSITIVE_STDOUT.replace(b"BASELINE_MISMATCH\tbinding-01\n", b"")
WRONG_BASELINE = dict(returncode=0, stdout=WRONG_BASELINE_STDOUT, stderr=b"", expected_matched=False)
```

Every other predicate still holds (C1-C4, C6); only C5 fails (reported 1 vs 0 records), so this isolates the r20-specific cross-check. Base behavior (source-inferred): rejected correctly → before/after both `False`; it's a retained control, not a defect demonstration. Alternatives in the same family, each failing exactly one predicate: drop the INVENTORY line (C4); drop `CASE\tpass\tbinding-52` (C6, 51 ≠ 52); drop the SUMMARY line (C3, and reported=None ≠ 1).

## 4. Stderr policy impact

- **Base false green (source-inferred):** `POSITIVE` with `stderr=b"Traceback (most recent call last):\nRuntimeError: binding check aborted\n"` and rc 0 → C2 finds no FAIL-shaped line → `matched == True`. This is the admitted summary-stderr defect, and it applies to r20-input-binding unchanged. Expected after repair: `False`.
- **Repair risk for the real positive control:** if the repair adds `and not stderr` to the summary branch (mirroring counter l.445 / cache-demo l.480), the real r20-input-binding run must emit zero stderr bytes. The fixture takes `--root` and `--baseline <commit>` and plausibly shells out to git [INFERENCE: fixture not read]; any inherited git/Python warning on stderr would turn the retained real positive control red. L1 SHOULD confirm from the actual acceptance record that `commands[3].stderr_sha256 == e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty) before adopting a strict empty-stderr policy for all summary steps.
- **Already-covered stderr case:** stderr containing `CASE\tFAIL\t...` or `FAIL\t...` already fails at base via C2 — not a new discriminating vector.

## 5. Bounded additional findings (no claim; outside the three admitted defects)

- LOW, malformed-data crash path (source-inferred + recalled doc): `int(baseline_match.group(1))` (l.385) on a `baseline_mismatches=` value of more than 4300 ASCII digits raises `ValueError` under CPython ≥3.11's default integer-string conversion limit. That limit is recalled from Python docs and was not visible in this round's fetch (the stdtypes page truncated before that section). In `main` that becomes a whole-run refusal (exit 2, no output file; l.652-654). A synthetic oracle calling `summarize_result` directly sees an uncaught exception. This conflicts with the preregistered "reject malformed producer data without a crash". A minimal code-side fix (inventory regex stays frozen): `try: int(...) except ValueError: reported = None`.
- LOW, leniency: `\d` matches Unicode Nd digits and `int()` accepts them (docs note 6), so `baseline_mismatches=١` (U+0661) with one record is accepted. Fixing it in the regex changes frozen inventory bytes, so it's out of scope here.
- LOW, case-sensitive failure vocabulary: an extra `CASE\tfail\tx` line (lowercase, matching this fixture's lowercase `pass` style) alongside 52 pass lines and the literal summary is not a failure line and leaves the pass count at 52, so it's accepted. Getting there requires a self-contradicting producer summary, which falls under the preregistration's disclaimed malicious-producer scope.
- Info: C3/C4/C5 split with `str.splitlines` (also breaks on `\r`, `\x0b`, `\x0c`, `\x1c`-`\x1e`, `\x85`, `\u2028`, `\u2029`), while C6 uses `re.MULTILINE` (`\n` only). A CRLF variant of `POSITIVE` still matches. Exotic separators can make the two views disagree; no false green was constructed from this.

## Verification / provenance

Nothing was executed: no tests, builds, probes, or summarizer calls. No LSP device was available in this session, so definitions were traced by reading the named file directly; no broad grep was used. No tools were installed or updated, and RULES.md was not read because no install was needed. No files were written except this report.

Report: .ufo/waves/round-22/w1/Summary4.md
