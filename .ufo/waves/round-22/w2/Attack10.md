# Attack10 — `stderr/carry-invariant-probe/error` (want=False) + paired positive

Seat: SoujiR22.Attack10 (leaf, source-only, no execution of runner/oracle/probe).
Code under attack: `4f83fd222ffbd8825340221a8c426550ef891191` (= HEAD; named paths clean).

## STATUS

**Source-only PASS for this vector.** The stored delta reconstructs exactly from the pinned
public record and frozen inventory. Want=False is correct under the preregistered C1 defect
("summary stderr accepted despite success") and lesson R22-M2. The fixture really does feed the
synthetic stderr into `summarize_result`. The vector isolates the new `and not stderr` term:
it evaluates to False on the changed code and True on base `41553adb`, so it discriminates.
The paired positive evaluates to True on both base and changed code, so the guard does no harm
there. This is hand evaluation of source only. No runtime evidence was produced; L1's
214-decision run stays authoritative. Two adjacent findings outside this vector are listed
below (an invalid-UTF-8 coverage gap and an unpinned runner digest). Neither changes this
vector's verdict.

## Input binding (checksums only)

| file | sha256 | binding |
|---|---|---|
| `census/round-21/final-out-S1.json` | `bc53a752…38fe` | = oracle `source_receipt_sha256` |
| `census/round-21/step-inventory.json` | `8b7b1cd8…1310` | = oracle `frozen_inventory_sha256` |
| `census/round-21/run-acceptance.py` | `00d0e9c2…80a6` | = `git show 4f83fd2:` blob |
| `tests/fixtures/r22-result-oracle.json` | `292442a6…0651` | = `git show 4f83fd2:` blob, 214 cases |

The vector bytes and the paired-positive bytes are identical in oracle commits `36c78ba`,
`3223172` and `4f83fd2` (the case count went from 212 to 214 elsewhere in the file).

## 1. Reconstruction of the stored delta (done before inspecting the predicate)

Oracle entry (`r22-result-oracle.json:456-461`) overrides only `stderr`:
`"ERROR: synthetic producer incomplete\n"`.

All other fields come from the pinned public record and the frozen inventory:
- **Record** (`final-out-S1.json:1935-1943`, the only `carry-invariant-probe` entry under
  `commands`): `returncode=0`, `stderr=""`,
  `stdout="SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0\n"`.
- **Step** (`step-inventory.json:141-152`): `kind="summary"`, `expected_summary` is that same
  SUMMARY string, `pass_pattern=null`, `pass_count=0`. It contains no `<REVISION>` tokens, so
  `replace_revision` is a no-op. This matches the runner's own definition at
  `run-acceptance.py:330-332`.

The effective input is therefore the real positive with exactly one change: the stderr channel
goes from 0 bytes to 37 bytes. The delta is a single-axis mutation.

### Does the fixture actually feed that input?

Yes. `r22-result-oracle.py:67-68` selects the record by `step_name`. Lines 68, 84 and 87-91
then call `module.summarize_result(step, case.get('returncode', 0), stdout.encode(...),
case['stderr'].encode('utf-8','surrogateescape'), revision, ROOT)`. None of the override keys
(`stdout_nested_array_depth`, `json_set`, `cache-demo`) apply. The oracle's grading line
(`:97`) is `type(observed) is bool and observed is case['want']`, and the runner returns
`bool(matched)` (`run-acceptance.py:537`), so the type check holds.

### Is want=False correct?

Yes. The preregistration's C1 lists "summary stderr accepted despite success" as an admitted
open defect. Lesson `round-22.md:7` says "Summary stderr must be zero bytes". R22-M2
(`round-22.md:16`) says to "reject any nonempty summary stderr rather than suppress warnings or
expand marker spellings". A producer that exits 0 with a correct SUMMARY but writes `ERROR:` to
stderr is the canonical false green. Rejecting it is the correct literal decision.

## 2. Attack on the changed predicate (hand trace, `run-acceptance.py`)

| line | evaluation for this vector |
|---|---|
| 393-394 | `decode_exact` (surrogateescape) round-trips both channels byte-exactly |
| 395 | `summary_lines` uses **stdout only**, so it is `[expected]`; the stderr text cannot add a SUMMARY line |
| 396, 356-359 | `failure_lines("SUMMARY…\n\nERROR: synthetic producer incomplete\n")`: `ERROR:` does not match `FAIL\t`, `CASE\tFAIL\t` or `^CASE\t[^\t]+\tFAIL(\t\|$)`, so the result is `[]` |
| 410 | `matched = (0 == 0) and not [] = True` |
| 415-417 | expected is a string, so `summary_match = ([expected] == [expected]) = True` |
| 432-436 | there are no `INVENTORY\t` lines and `expected_auxiliary = []`, so this stays True |
| 440 | `baseline_mismatch_count` is absent, so this check is skipped |
| 446-450 | `pattern=None`, so `pass_count = 0 == 0` and `pass_match = True` |
| **463** | `True and True and True and not "ERROR: …\n"`, which gives **False** |
| 464-465 | the VIOLATION check is applied with `and`, so the result stays False (stdout has no `VIOLATION\t`) |
| 537 | `matched = False`, which equals want=False. **Agrees** |

**Discrimination against base.** Base `41553adb` (the same file bytes as `1957154`; empty diff)
has line 417 `matched = matched and summary_match and pass_match` with no stderr term. Every
other term evaluates as above, so base returns **True**, which disagrees with want=False. The
vector kills the base predicate.

The marker list does not catch this stderr text (`failure_lines` finds nothing), so the
`not stderr` term at line 463 is the only thing that flips the decision. The vector is not
redundant with `failure_lines`.

**Paired positive** (`positive/carry-invariant-probe`, `r22-result-oracle.json:443-447`). It
uses the record values unchanged (`stderr=""`). Line 463 evaluates `not "" = True`, so the
result is True and agrees with want=True. Base also returns True, so the vector is a no-harm
control and is not meant to discriminate. The no-harm property also holds across the public
receipt: `final-out-S1.json` contains no non-empty `"stderr"` value, so the strict guard cannot
flip any of the 18 recorded real positives.

## 3. Concrete limits and mismatches (not defects in this vector's verdict)

1. **This vector alone cannot separate `not stderr` from narrower guards.**
   `not stderr.strip()` and `not stderr.startswith("ERROR")` would both still return False here.
   The sibling vectors close that gap: `/blank` (`"\n"`) kills the `strip` variant, and `/pass`
   plus `/warning` kill marker-list variants. Calibration of the "zero bytes" claim therefore
   depends on the whole stderr group, not on this vector.
2. **Invalid-UTF-8 stderr is claimed but has no vector.** `round-22.md:7` claims the
   zero-bytes rule applies "including whitespace and invalid UTF8". The oracle JSON contains no
   `\udcXX` surrogate-escaped stderr case, and the oracle would encode one to raw bytes at
   `r22-result-oracle.py:90`. The code would reject such input: `decode_exact` produces a
   non-empty surrogate string and line 463 returns False. The claim is source-true but
   oracle-uncovered.
3. **The runner digest is reported but not enforced.** `r22-result-oracle.py:104` only records
   `runner_sha256`; it never compares it against an expected value. L1 must confirm the
   receipt's `runner_sha256` equals `00d0e9c2fda2fde2d21cb74b1a1dd5b1db7b1ea679cdfd4239d91aa186e080a6`.
   Otherwise a 214/214 result does not bind to `4f83fd2`.
4. **Out of scope / unknown.** The real `census/round-19/probe-carry-invariants.py` was not
   read (not a named path). Whether a future real run could emit benign stderr, such as Python
   warnings, and become a strict-guard false negative is unresolved. The pinned record shows
   0-byte stderr.

## 4. Drafted mutation (not executed)

- **M-A10-1:** at `run-acceptance.py:463`, delete `and not stderr`, which restores base line 417.
  - Expected killed vector: `stderr/carry-invariant-probe/error` (observed True vs want False).
    The same mutation also kills the `/blank`, `/pass` and `/warning` carry vectors and the
    corresponding vectors for the other summary steps.
  - Expected survivor: `positive/carry-invariant-probe` (True).
- **Control mutation M-A10-2:** change line 463 to `not stderr.strip()`. This vector should
  **survive** (False), while `stderr/carry-invariant-probe/blank` should be killed. That
  demonstrates limit 1.

## Evidence and limits

- Exercised: reading the named files, hand evaluation, and `sha256sum`. Also `git show` and
  `git diff` on the named paths at `41553adb`, `1957154`, `36c78ba`, `3223172` and `4f83fd2`,
  plus a JSON parse of the pinned oracle blobs to compare vector bytes and count cases.
- Not exercised: the oracle, the runner, the probe, tests or builds.
- Python documentation S104-S106 was not re-opened: those sources cover JSON typing, not the
  stderr predicate.
- Tools installed or updated: none.
