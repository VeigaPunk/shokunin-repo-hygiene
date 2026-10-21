# Attack08 — `stderr/r18-landing-pointers/error` (want=False)

Seat: SoujiR22.Attack08 (scout, leaf, source-only). Code under attack: `4f83fd222ffbd8825340221a8c426550ef891191` (working tree HEAD; `census/round-21/run-acceptance.py` sha256 `00d0e9c2…a6`, identical to `git show 4f83fd2:` bytes).

## STATUS

**PASS (source-only).** The expected decision `want=False` is correct under the R22 contract. The fixture does feed exactly the stated input. The changed predicate rejects the vector, and only that predicate rejects it, so the vector is truly discriminating. The paired positive stays True. I found no concrete mismatch.

Evidence comes from reading source and pinned JSON, plus checksum/count fact pipelines over the stored receipt strings. I executed no runner, oracle, fixture, or test. Limits: the oracle is not provably independent by commit order (see F6). Live 18-step operability at `4f83fd2` is not observed here and belongs to L1.

## Input pins (observed)

| Item | Value |
|---|---|
| Oracle `r22-result-oracle.json` | sha256 `292442a6…0651` (equals the `4f83fd2:` blob) |
| Oracle driver `r22-result-oracle.py` | sha256 `3c0776ae…a604` (equals the `4f83fd2:` blob) |
| Receipt `census/round-21/final-out-S1.json` | sha256 `bc53a752…38fe`, equal to oracle `source_receipt_sha256` (oracle json line 4) |
| Frozen inventory `census/round-21/step-inventory.json` | sha256 `8b7b1cd8…1310`, equal to oracle `frozen_inventory_sha256` (line 6) |
| Receipt `measured_commit` | `ff425ab835614f38205426330b9cdb93fd267045` (receipt line 4725), equal to oracle `revision` (line 7); receipt `all_matched: true` (line 3) |

## 1. Stored delta and reconstruction (done before inspecting the changed predicate)

The stored vector is at oracle json lines 360–365: `step_name: r18-landing-pointers`, `want: false`, and a single override key, `stderr: "ERROR: synthetic producer incomplete\n"`. It has no `stdout`, `returncode`, `json_set`, or `stdout_nested_array_depth` keys (fact pipeline: extra keys = `['stderr']`).

**Pinned original record** (receipt lines 1555–1564):
- `returncode` is 0.
- `stderr` is `""` (sha `e3b0c442…`).
- `stdout` holds 11 `CASE\tPASS\t…` lines plus `SUMMARY\ttotal=11\tfailed=0`.
- Recomputed sha256 of the stored stdout string equals the stored `stdout_sha256` `1cacb86e…` (fact pipeline: `stdout_sha_ok True`).

**Frozen inventory step** (step-inventory.json lines 113–126):
- `kind: summary`
- `expected_summary: "SUMMARY\ttotal=11\tfailed=0"`
- `pass_pattern: "^CASE\\tPASS\\t"`, `pass_count: 11`
- No `<REV>` placeholders, so `replace_revision` is a no-op for this step.

**Reconstruction via the oracle driver** (`r22-result-oracle.py`):
- line 67: `record = records['r18-landing-pointers']`
- line 68: `stdout` is the record stdout (no override)
- lines 69–82: no depth or json_set mutation
- line 83: step is a deep copy of the inventory row
- lines 88–90: `returncode` is the record's 0, and `stderr` is the case override, encoded `utf-8/surrogateescape`
- line 97: pass requires `type(observed) is bool and observed is False`

The vector therefore equals the original public record with only stderr changed from `""` to the 37-byte `ERROR: synthetic producer incomplete\n`. **The fixture does feed that input.**

**Is the expected decision correct?** Yes. The oracle contract (json line 8) says "Reject nonempty summary stderr". The lesson (`corpus/lessons/round-22.md` line 7) says "Summary stderr must be zero bytes, including whitespace and invalid UTF8", and R22-M2 (line 16) says "reject any nonempty summary stderr". The preregistration names the defect "summary stderr accepted despite success". So a successful exit with a diagnostic on stderr must not be green, and `want=False` is correct.

## 2. Changed predicate, traced for this vector (`4f83fd2`)

Walking `summarize_result` (lines 390–538):

| Step | Lines | Result |
|---|---|---|
| Summary lines (`SUMMARY_RE`, line 118) | 395 | `['SUMMARY\ttotal=11\tfailed=0']` |
| `failure_lines(stdout+"\n"+stderr)` | 396, 356–359 | `[]`. `ERROR: …` is not `FAIL\t`/`CASE\tFAIL\t`/`CASE\t<x>\tFAIL`. The `vacuity-stub` line contains "failed: yes" but not `\tFAIL`. |
| `matched = returncode == 0 and not failures` | 410 | True |
| String expected: `summary_lines == [expected]` | 415–417 | True |
| Auxiliary `INVENTORY\t` lines vs `[]` | 432–435 | True |
| `baseline_mismatch_count` | 440 | absent, skipped |
| Pass count | 446–450 | 11 == 11, True |
| **`matched = matched and summary_match and pass_match and not stderr`** | **463** | **False**, because `not "ERROR: …\n"` is False |
| carry-invariant clause | 464 | not this step |
| `result["matched"] = bool(matched)` | 537 | False |

The driver sees observed False, which is the expected False, so the vector passes.

**Sole killer.** Every other conjunct is True, so line 463's `and not stderr` alone decides the vector. Without it the observed value would be True.

**Before arm.** The base `41553adb` (preregistered) line 417 and `ff425ab` both read `matched = matched and summary_match and pass_match`, with no stderr term in the summary branch. The base observes True, which differs from want, so the vector fails on the base. It discriminates as the preregistration intends. The counter and cache branches already had `not stderr` (base lines 445 and 480).

## 3. Paired positive `positive/r18-landing-pointers` (want=True)

Oracle json lines 347–351 have no overrides, so the inputs are the record's `rc=0`, `stderr=""`, and stdout. The trace is identical to section 2 except at line 463, where `not ""` is True, so observed True equals want and the positive passes. All 18 pinned receipt records carry `"stderr": ""` (receipt lines 214, 404, 597, 798, 989, 1180, 1370, 1561, 1752, 1941, 2134, 2325, 3381, 3618, 3855, 4100, 4345, 4560). Strict zero-byte stderr therefore costs no pinned positive.

## 4. Attack attempts

| ID | Attack | Outcome |
|---|---|---|
| F1 | Exception masking: a crash would give `observed=None` | Not a false pass. Driver line 97 requires bool identity. No exception is possible on this path (string expected, no int parse). |
| F2 | Failure-marker shortcut: stderr is rejected only by a FAIL-spelling list | Refuted. `ERROR:` matches no marker in 356–359, and rejection comes from line 463. This is consistent with the lesson's "rather than … expand marker spellings". |
| F3 | Decode laundering | `decode_exact` uses surrogateescape (line 224), so the nonempty bytes stay a nonempty str. No strip or normalize is applied before `not stderr`. |
| F4 | Step identity | Driver line 83 takes the inventory step and line 67 the record step, both keyed by `step_name`. The literal `argv` placeholders (`<PYTHON>`/`<ROOT>`) only reach `result["argv"]`/`command` and do not affect `matched`. |
| F5 | Separator injection | Line 396 joins stdout and stderr with `"\n"`, so the stderr text cannot glue onto the last stdout line to form a marker. Irrelevant here anyway. |
| F6 | Provenance and independence (weakness, not a decision mismatch) | The oracle json/py and the predicate change landed in the **same commit**, `36c78ba` (2026-10-21 10:57:50 -0300). `4f83fd2` then edited runner and oracle together, adding only two `decoder-depth` vectors. This vector is byte-identical at `36c78ba` (lines 360–365). Its "independently frozen" status rests on review, not on git ordering. Its literal value is still contract-derived (section 1), not producer-derived. |
| F7 | Coverage of this single vector | It kills deletion of `and not stderr` and any predicate that ignores `ERROR`-prefixed stderr. It cannot kill predicates such as `not stderr.strip()` or "reject only ERROR/FAIL prefixes". Those are covered by the siblings `/blank` (`"\n"`), `/pass` (`"PASS\t…"`), and `/warning`, all with want False and stderr-only deltas (fact pipeline). |

## 5. Drafted mutations (never executed)

| ID | Mutation at `run-acceptance.py` line 463 | Expected result |
|---|---|---|
| M1 | Replace with `matched = matched and summary_match and pass_match` | Killed by `stderr/r18-landing-pointers/error`: observed True, want False. The `/blank`, `/pass`, and `/warning` siblings also flip. `positive/r18-landing-pointers` still passes. |
| M2 | Replace with `... and not stderr.strip()` | Survives `/error`. Killed by `stderr/r18-landing-pointers/blank`. |

## Remaining unknowns

- Live behaviour at `4f83fd2`. Whether the real `tests/fixtures/r18-landing-pointers.py` produces empty stderr in L1's actual 18-step run is unobserved. That file is outside my named paths. The receipt only pins its sha `4e5bf7e1…` at `ff425ab`. [INFERENCE] If any interpreter warning reached stderr, line 463 would correctly turn the positive false. That is intended strictness, not harm.
- Not claimed: malicious-producer attestation, executed-command authentication, or universal malformed-input totality. F5 bytes and the 160-byte scope were not touched. Reap/NAMESPACE/exposure remain HELD, and certification is OFF/K5 HELD.

## Tooling

No installs or updates. Commands used: read-only `git show`/`diff`/`log`/`status`/`merge-base` on named paths, `sha256sum`, and one `python3 -B` JSON checksum/count pipeline over stored receipt and oracle strings. It ran no code under test.
