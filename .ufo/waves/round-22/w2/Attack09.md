# SoujiR22.Attack09 — `stderr/r16-landing-gate/error` (want=False)

Seat: leaf, read-only, source-only. Code under attack: `4f83fd222ffbd8825340221a8c426550ef891191`
(working tree `census/round-21/run-acceptance.py` sha256 `00d0e9c2…e080a6` == `git show 4f83fd2:` bytes;
oracle `.py` `3c0776ae…a604` and `.json` `292442a6…0651` also equal pinned bytes). Base: `41553adb…a675`.
No tests, runs, probes, installs or mutations executed. Tooling: none installed/updated.

## STATUS

**Source-only PASS for this vector.** Three things hold, all from source: the expected decision `want=False` is correct under the frozen contract; the fixture really feeds the mutated stderr into `summarize_result`, with every other input taken unchanged from the real record; and the changed predicate rejects the vector only through the new `not stderr` conjunct (line 463). The base accepted this input, so the vector is a genuine before/after discriminator. The paired positive `positive/r16-landing-gate` is still accepted.

I found no concrete mismatch for this vector. One weakness is recorded below: on its own, this vector is the easiest of the stderr set. Limits: I reasoned over the source and executed nothing. The L1 run of all 214 vectors and of the 18-step acceptance is the runtime evidence.

## 1. Stored delta, reconstructed before inspecting the predicate

Oracle case at `tests/fixtures/r22-result-oracle.json:407-413`:
`{"id":"stderr/r16-landing-gate/error","want":false,"group":"stderr","step_name":"r16-landing-gate","stderr":"ERROR: synthetic producer incomplete\n"}`.
This is the only id of its kind: 1 occurrence among 214 `"id"` entries, with no duplicate ids.

The delta overrides only `stderr`. There is no `stdout`, `returncode`, `json_set` or `stdout_nested_array_depth` key.

Pinned public original record, from `census/round-21/final-out-S1.json`, `commands[8]` (`:1746-1755`), which is the only command named `r16-landing-gate`:
- `returncode: 0`; `stderr: ""` (`stderr_sha256` e3b0c442…b855, which is the empty string).
- `stdout`: 15 lines of the form `CASE\t<name>\tPASS\t…`, then `SUMMARY\ttotal=15\tfailed=0\n`. Extracting the stored string with `jq -j` and hashing it gives `705fc547…6426`, which equals the record's `stdout_sha256`, so the record is internally consistent.
- The receipt file sha256 `bc53a752…38fe` and the inventory sha256 `8b7b1cd8…1310` both equal the hashes bound in the oracle header (`oracle.json:3-6`). The oracle enforces this binding at `oracle.py:31-35`.

Frozen inventory step, `census/round-21/step-inventory.json:127-140`:
- `kind:"summary"`, `expected_summary:"SUMMARY\ttotal=15\tfailed=0"`, `pass_pattern:"^CASE\\t[^\\t]+\\tPASS\\t"`, `pass_count:15`.
- The step has no `<REVISION>`/`<REV>` token, so `replace_revision` (`oracle.py:40-47`) leaves it unchanged.
- The step has no `baseline_mismatch_count`, so the `cache-demo` branch (`oracle.py:84-85`) does not apply.

Reconstructed input to `summarize_result`:
- step: as listed above.
- returncode: `0`, from the record (`oracle.py:88`).
- stdout: the record's bytes (`oracle.py:68`, then `:89`).
- stderr: `b"ERROR: synthetic producer incomplete\n"`, 37 ASCII bytes (`oracle.py:90`, where `case.get('stderr', …)` takes the case value).

The fixture therefore does feed this input. It is a single-variable delta from the paired positive.

**Is the expected decision correct?** Yes. The contract at `oracle.json:8` says "Reject nonempty summary stderr". The preregistration names the defect "summary stderr accepted despite success". `corpus/lessons/round-22.md:7` requires "Summary stderr must be zero bytes", and `:16` (R22-M2) says to reject any nonempty summary stderr. The step is `kind:"summary"` and the stderr is nonempty, so the correct decision is `False`.

## 2. Changed predicate traced for this vector (`run-acceptance.py`)

1. Lines 393-394: `decode_exact` (`:223-224`, utf-8 with surrogateescape) gives `stderr="ERROR: synthetic producer incomplete\n"`.
2. Line 396: `failure_lines(stdout + "\n" + stderr)`. The rule at `:356-359` only catches lines starting with `FAIL\t` or `CASE\tFAIL\t`, or matching `^CASE\t[^\t]+\tFAIL(\t|$)`. Every stdout CASE line has PASS in field 3, and `ERROR: …` matches no pattern. Result: `failures=[]`.
3. Line 410: `matched = (0 == 0) and not [] = True`.
4. Lines 412-416: `summary_lines` (stdout only, `SUMMARY_RE` at `:118`) is `["SUMMARY\ttotal=15\tfailed=0"]`, which equals `[expected]`, so `summary_match=True`.
5. Lines 432-435: there are no `INVENTORY\t` lines and the expected list is empty, so `auxiliary_match=True`. Line 440 is skipped because there is no `baseline_mismatch_count`.
6. Lines 446-450: `re.findall(pass_pattern, stdout, MULTILINE)` finds 15 matches. None of the 15 case names contains a tab, so `pass_match=True`.
7. **Line 463**: `matched and summary_match and pass_match and not stderr`. The first three are True and `not stderr` is False, so `matched=False`.
8. Line 537: `bool(False)`. The oracle check at `oracle.py:97` is `type is bool and False is False`, so the vector passes.

The only conjunct that rejects this vector is `not stderr` at `:463`.

**Base (`41553adb`) for the same input:** line 417 was `matched = matched and summary_match and pass_match`, with the same `failure_lines` at base `:330-333`. Base therefore observes `True` and the vector fails on base. That is the claimed calibration before/after delta. The diff from base to code at this site adds exactly `and not stderr`.

**Attacks on `not stderr` itself, none of which succeeded:**
- `stderr` is always a `str` from `decode_exact`, so truthiness cannot be confused by type.
- surrogateescape is lossless, so the decoded string is empty exactly when the bytes are empty. This covers `"\n"`, BOM bytes and the lone `\x85` (the invalid-utf8 sibling at `oracle.json:4077-4082`), matching the lesson's "zero bytes, including whitespace and invalid UTF8".
- The conjunct sits inside the `kind=="summary"` branch, so all 12 summary steps are covered. The inventory has 12 summary, 5 counter and 1 cache-demo step, matching lesson `:16` "twelve summary steps".
- The counter and cache-demo branches already had `not stderr` (`:492`, `:536`).
- The live runner captures stderr separately (`:670-672`, `stderr=subprocess.PIPE`), so real producer stderr reaches the same predicate. The invocation-failure path at `:675` produces nonempty stderr and is rejected as well.

## 3. Paired positive `positive/r16-landing-gate` (`oracle.json:394-399`, want=True)

There are no overrides, so the record values are used: `rc=0`, `stderr=b""`. Steps 1-6 above are identical. At `:463`, `not ""` is True, so `matched=True`, which equals want.

No harm to operability: all 18 real records in `final-out-S1.json` have `stderr` length 0 and sha e3b0…b855, with `returncode` 0 and `matched` true. The strict-stderr rule therefore rejects none of the 18 real positive controls.

## 4. Drafted mutations (not executed)

- **M09-a.** At `run-acceptance.py:463`, delete `and not stderr`, reverting to the base predicate. Expected: `stderr/r16-landing-gate/error` becomes observed `True` against want `False`, so it is **KILLED**. The same applies to `…/blank`, `…/pass`, `…/warning` and `…/invalid-utf8`, and to every other summary-step stderr vector. `positive/r16-landing-gate` is unchanged (True).
- **M09-b (weakness probe).** Replace the conjunct with `and not stderr.strip()`. Expected: `stderr/r16-landing-gate/error` still observes `False`, so it **SURVIVES**. `stderr/r16-landing-gate/blank` (`"\n"`) observes `True`, so it is **KILLED**. A marker-style variant such as `and "ERROR" not in stderr` would likewise be passed by `/error` and killed by `/blank`, `/pass` and `/warning`.

Finding: `/error` on its own only separates "some stderr check" from "no stderr check". The zero-byte strictness that the lesson claims is carried by its siblings: blank, pass, warning and invalid-utf8. This is not a defect, because those siblings exist in the same frozen set, but it means `/error` must not be cited alone as evidence of zero-byte strictness.

## 5. Peripheral observation (no effect on this vector)

`r22-result-oracle.json` contains the JSON escape `"\udc85"` (`:4081`). Python's `json` accepts it, which is what the oracle loader uses (`oracle.py:29`). A strict parser does not: `jq` rejects the file at byte 164988. The oracle is therefore Python-decoder-specific. That is fine for this harness, but other tooling cannot re-read the file.

## Remaining unknowns

- There is no runtime confirmation. The L1 run of all 214 vectors is the authority on the observed booleans.
- The oracle trusts `record['stdout']` without rechecking it against `record['stdout_sha256']`; only the whole-file hash is bound. I confirmed by checksum that the two agree for this record, but the harness does not enforce it.
