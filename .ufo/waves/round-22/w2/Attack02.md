# Attack02 — revision-helper summary stderr vector

## Axes and status

Axes: **C1 calibration** (reject the assigned false green); **operability no-harm** (retain its paired real positive); **coverage no-harm** (identify whether the frozen oracle would detect removal of the relevant guard). No additional axis or admission decision is claimed.

**STATUS: PASS, source-only, for the assigned vector pair.** The literal `want=False` for `stderr/revision-helper-selftest/error` is correct under the preregistered nonempty-summary-stderr contract. The fixture forwards exactly the reconstructed input, rather than silently retaining the original empty stderr. The changed predicate rejects that input and preserves `positive/revision-helper-selftest` by source derivation. No concrete oracle/input/predicate mismatch was found for this pair. Behavioral execution and experimental mutation killing are **not evaluated**: all predicted decisions below are marked `[INFERENCE]`; no tests, acceptance commands, imports, or mutation probes were run.

## Evidence and source identity

Source references below resolve to these exact absolute paths:

- **O**: `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r22-result-oracle.json`
- **D**: `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r22-result-oracle.py`
- **R**: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-21/final-out-S1.json` — the allowed PUBLIC acceptance output only.
- **I**: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-21/step-inventory.json`
- **P**: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-21/run-acceptance.py`
- **C**: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/preregistration.txt`

Observed SHA-256 values (static byte identity, not behavioral results):

| Source | SHA-256 | Pin compared with the named working file |
|---|---|---|
| P | `00d0e9c2fda2fde2d21cb74b1a1dd5b1db7b1ea679cdfd4239d91aa186e080a6` | `4f83fd222ffbd8825340221a8c426550ef891191` |
| D | `3c0776ae1df8cd487380a8a94203848e3a24c5bc910762a23f63fc335697a604` | `4f83fd222ffbd8825340221a8c426550ef891191` |
| O | `292442a6ec078b7cc20526b4ba7ab1300eb08bc9cc4dbaf9894472120dcd0651` | `4f83fd222ffbd8825340221a8c426550ef891191` |
| R | `bc53a75285a4fafdb6f4f8c2de0a4068fa87494c2745faa1ef6af11ec25738fe` | `41553adb139d06511dc386bb3ce4326aebfba675` |
| I | `8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310` | `41553adb139d06511dc386bb3ce4326aebfba675` |

The public record and inventory were opened from the pinned base with `git show`, and their relevant record/step and hashes were established **before inspecting the changed predicate**. O:3–8 independently names those same input digests and the empty-summary-stderr expectation. This review checks the assigned frozen expectation and its implementation, not the historical independence/authorship chronology of the fixture.

## 1. Stored delta and independent reconstruction

**Stored delta:** O:72–77 contains exactly:

```json
{
  "id": "stderr/revision-helper-selftest/error",
  "want": false,
  "group": "stderr",
  "step_name": "revision-helper-selftest",
  "stderr": "ERROR: synthetic producer incomplete\n"
}
```

It does not override stdout or return code. The paired positive is O:58–63: `positive/revision-helper-selftest`, literal `want=true`, the same step, and no input overrides.

**Frozen step:** I:20–31 specifies `kind="summary"`, `expected_summary="SUMMARY total=11 failed=0"`, `pass_pattern="^CASE\\tpass\\t"`, and `pass_count=11`. Its frozen argv is `["<PYTHON>", "-B", "<ROOT>/tools/souji-rev-pin.py", "--selftest"]`. There is no revision placeholder in this step, so D:40–47's revision substitution does not change it. The argv is metadata for this summarizer call, not a command the oracle executes.

**Pinned public original:** R:219–227 identifies the original helper command and expected summary; R:398–407 supplies return code `0`, stderr `""`, and stdout with SHA-256 `428a32176879a3d520f0dfbdb2e65454961335f38ef55f4a07841de051a3fcf8`. Its complete stdout is the following byte string; `\t` and `\n` denote actual tab and newline bytes, including the final newline:

```text
CASE\tpass\tdurable-clean-accept\n
CASE\tpass\tkeep-only-refuse\n
CASE\tpass\tdirty-tree-refuse\n
CASE\tpass\thead-symref-refuse\n
CASE\tpass\tbranch-name-refuse\n
CASE\tpass\tshort-id-refuse\n
CASE\tpass\tno-measured-paths-refuse\n
CASE\tpass\tpath-escape-refuse\n
CASE\tpass\tunknown-rev-refuse\n
CASE\tpass\thistorical-no-tree-check-accept\n
CASE\tpass\thistorical-tree-check-refuse\n
SUMMARY total=11 failed=0\n
```

Thus the assigned negative is the frozen summary step plus **original return code 0, original stdout unchanged, and only stderr replaced by `b"ERROR: synthetic producer incomplete\n"`**. The paired positive has the same step/return code/stdout and `stderr=b""`. Both calls receive revision `ff425ab835614f38205426330b9cdb93fd267045` from O:7 and the repository root from D:17,87–91.

**Expected decisions:** The negative's literal false is correct because C:1 preregisters rejection of summary stderr despite apparent success, and O:8 states rejection of nonempty summary stderr. Exit 0 and the original successful stdout therefore do not rescue it. This is a bounded acceptance rule, not a claim that every program universally treats any diagnostic as failure, or that the synthetic text proves actual producer incompleteness. The positive's literal true is consistent with retaining the original real outputs: its stderr is empty and its summary/pass records exactly meet I:21–25.

## 2. Does the fixture actually feed that input?

**Yes, by source inspection.** D:28–37 checks the source/inventory bytes against O's digests before parsing; the observed file hashes above match those pins. D:58–60 selects the record and frozen step by name. D:67–68 takes stdout from the original when the case has no stdout override. Neither assigned case has `json_set` or nested-array mutation, so D:69–82 does not alter it. D:83 makes an independent step copy, and the cache-only adjustment at D:84–85 is inapplicable.

D:87–91 calls the actual `summarize_result` with original return code, encoded original stdout, and **`case.get('stderr', record['stderr']).encode('utf-8', 'surrogateescape')`**. Consequently the error case supplies the nonempty error stream including its newline, while the positive supplies the original empty stream. There is no strip, normalization, marker filtering, or wrong-channel substitution in that forwarding. The source record's old `matched=true` and precomputed counts are not passed as the decision: D:92 reads the newly returned `result['matched']`, and D:97 requires both a real bool and identity with the case's literal `want`. The desired decision is not passed into the predicate.

## 3. Attack on the changed predicate and paired positive

Relevant changed source: P:118 (summary recognition), P:223–224 (exact UTF-8/surrogateescape decoding), P:356–359 (failure markers), P:390–465 (summary branch), and P:537–538 (boolean result).

`[INFERENCE]` Source-derived trace:

| Predicate component | Assigned error vector | Paired positive |
|---|---|---|
| Decoded stderr | `"ERROR: synthetic producer incomplete\n"` | `""` |
| Failure-marker list, P:356–359,396 | `[]`: `ERROR:` is not any recognized `FAIL` form | `[]` |
| Initial `returncode == 0 and not failures`, P:410 | true | true |
| Summary list, P:395,415–416 | exactly `["SUMMARY total=11 failed=0"]` | same |
| Auxiliary lines, P:417,432–436 | expected/observed `[]`, match true | same |
| Pass count, P:446–450 | 11, expected 11, match true | same |
| Raw-stderr guard, P:463 | `not stderr` is false | `not stderr` is true |
| Final boolean `matched`, P:537 | **false** | **true** |

The baseline-mismatch-count condition is absent from this frozen step; the `carry-invariant-probe` special case at P:464–465 is not selected. The error is therefore rejected specifically by the summary stderr guard, not accidentally by the limited FAIL-marker recognizer. The same guard does not reject the genuine empty-stderr positive. No concrete mismatch was found within this vector pair.

## 4. One bounded mutation draft — not applied or executed

**Mutant:** At P:463 only, remove the final summary stderr conjunct:

```python
# Original
matched = matched and summary_match and pass_match and not stderr
# Draft mutant
matched = matched and summary_match and pass_match
```

No failure-marker changes and no counter/cache guard changes belong to this mutation.

**Exact expected killing case:** `stderr/revision-helper-selftest/error` in O:72–77. The bounded detector is D with that exact `--case` selector and the supplied runner. `[INFERENCE]` With the conjunct removed, every remaining acceptance term is true for the reconstructed input; the returned `matched` becomes true despite literal `want=false`. D:97 then records a mismatch. The paired positive `positive/revision-helper-selftest` remains true, showing why a positive-only detector would miss this defect.

| Stage | Error case: predicted observed / expected | Positive: predicted observed / expected |
|---|---|---|
| Pristine changed source | false / false | true / true |
| Draft mutant | **true / false** | true / true |
| Exact restoration | false / false | true / true |

All table entries are `[INFERENCE]`, not actual outputs. For an isolated error-case detector invocation, the predicted pristine/restored receipt is `total=1, pass=1, fail=0`, exit 0; the predicted mutant receipt is `total=1, pass=0, fail=1`, `finding_id="R22-RESULT-CONTRACT"`, exit 1 (D:97–111).

**Actual detector output:** none; execution is prohibited for this seat. **Mutation verdict: INCONCLUSIVE / unexecuted**, with an exact source-derived expected kill, not an observed killed mutant. No pristine baseline failure or survival claim is asserted.

**Restoration evidence:** No scratch copy or production file was mutated, so no restoration operation was necessary. The observed source hash is P's pinned hash above. Mutated/restored hashes and a post-restoration hash are not available because those byte states were never created; none is fabricated. The only authored file is this report.

## Limits and tooling

Only the assigned negative, paired positive, and one mutation draft are assessed. No all-214 result, real 18-step run, broader malformed-input totality, producer provenance, certification, F5 byte comparison, reap/NAMESPACE/exposure reassessment, or runtime operability result is claimed. The F5 160-byte synthetic-only boundary and certification OFF/K5 HELD remain unchanged in scope. No delegation, peer contact, background jobs, process inspection, production edits, Git/jj mutation, or behavioral execution occurred. Tools installed or updated: **none**; no pacman transaction was attempted.

Report: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/w2/Attack02.md
