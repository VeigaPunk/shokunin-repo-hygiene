# Attack03 — exact stderr vector and equality-mutant draft

STATUS: **source-only PASS** for the assigned negative `stderr/r20-audit-contract/error`, its paired positive, and the fixture's input wiring: the literal expected decisions are justified and the changed predicate agrees by source tracing. No concrete mismatch was found in this pair. This is not a runtime PASS or a C1 admission decision. The mutation is drafted only; its empirical verdict is **INCONCLUSIVE / NOT RUN**. No detector, test, build, formatter, producer, scanner, or other runtime was invoked.

Axes: **calibration** is the challenged axis; **operability** and **coverage** are no-harm constraints. The leaf performed only named-source inspection, pinned-source hashing, and this sole report write. No delegation, peer contact, production edit, or scratch mutation occurred.

## Source keys and pinning

All line citations below resolve through these absolute paths:

- **A** — `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-21/run-acceptance.py`
- **F** — `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r22-result-oracle.py`
- **O** — `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r22-result-oracle.json`
- **I** — `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-21/step-inventory.json`
- **R** — `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-21/final-out-S1.json` — public acceptance output, not a process snapshot
- **P** — `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/preregistration.txt`
- **S** — `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`

The stored delta, frozen step, and pinned original output were inspected and the input reconstructed **before inspecting A's changed predicate**. `git show` of the exact named R and I paths at preregistered base `41553adb139d06511dc386bb3ce4326aebfba675`, piped only to `sha256sum`, produced the hashes declared in O:4 and O:6. Current R and I have those same hashes. Current A, F, and O also hash-identically to their exact named paths at candidate `4f83fd222ffbd8825340221a8c426550ef891191`. Thus the cited local lines are bound to the candidate and pinned public inputs, not merely presumed current equivalents.

## 1. Independent reconstruction and correctness of the expectation

O:119–125 stores precisely:

```json
{
  "id": "stderr/r20-audit-contract/error",
  "want": false,
  "group": "stderr",
  "step_name": "r20-audit-contract",
  "stderr": "ERROR: synthetic producer incomplete\n"
}
```

There is **no stdout or return-code override**. I:34–47 freezes this step as `kind="summary"`, with:

- exact expected summary `SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11`;
- pass pattern `^CASE\tPASS\t` and pass count `78`;
- argv `["<PYTHON>", "-B", "<ROOT>/tests/fixtures/r20-audit-contract.py", "--tool", "<ROOT>/tools/souji-seat-audit.py", "--base-tool", "<BASELINE>"]`.

The named public original record is R:591–600. Its actual input-bearing fields are return code `0` (R:596), empty stderr (R:597), and the full stdout string at R:599. That stdout contains the 78 `CASE\tPASS\t` records and the one exact terminal summary above; its **stored**, not newly recomputed, stdout SHA-256 is `78d90ab393083c4bc70c8dbe0ab1440076c8b7126d5a4bdc06ebc61b9ba5443c` (R:600). The full R:599 string, rather than an abbreviated regenerated transcript, defines the reconstruction.

The reconstructed negative invocation is therefore:

```text
step         = I.steps[name == "r20-audit-contract"]
returncode   = 0
stdout_bytes = R.commands[name == "r20-audit-contract"].stdout encoded as UTF-8/surrogateescape
stderr_bytes = b"ERROR: synthetic producer incomplete\n"
revision     = "ff425ab835614f38205426330b9cdb93fd267045"
root         = F.ROOT
```

The revision is literal O:7. This particular step contains no revision placeholder, so revision substitution does not change its frozen expectations. The original record's prior `matched` field is **not** used to establish the expected answer.

**Expected decision: correct, `False`.** The preregistered contract explicitly identifies successful-summary stderr acceptance as a defect (P:1), and the independently stored oracle contract explicitly rejects nonempty summary stderr (O:8). A successful-looking stdout and zero exit status cannot override this synthetic nonempty error stream. This conclusion comes from that declared contract and reconstructed input, not from copying A's answer.

The paired positive is exactly `positive/r20-audit-contract`, literal `want=true`, with no overrides (O:107–111). It supplies the same complete stdout and return code, but preserves R:597's empty stderr. Its expected decision is correspondingly correct, `True`.

## 2. Does the fixture actually feed that input?

**Yes, by source inspection.** F:28–37 checks the public receipt and frozen-inventory SHA-256 values before decoding either. F:58–60 selects records and frozen steps by their names; F:61–68 selects the exact case and defaults stdout to the public record. Neither the nested-array nor JSON-mutation branch applies to this negative or its positive (F:69–82).

F:83 makes a fresh copy of the frozen step. Only cache-demo steps receive the additional measured-commit adjustment (F:84–85), which does not apply here. The actual call at F:87–91 passes:

- `case.get('returncode', record['returncode'])`, hence `0`;
- the unchanged stdout encoded with UTF-8/surrogateescape;
- **`case.get('stderr', record['stderr'])`**, hence the literal synthetic error stream for the negative, not the old empty stream;
- O's revision and F's root.

For the paired positive, the same defaults preserve the original empty stderr. No original `matched`, `failure_lines`, or `matched_counts` value is forwarded to the predicate. F:92 and F:97 then require the returned `matched` to be a real Boolean identical to the literal expectation. This is an input-wiring finding, not a claim that this fixture was executed.

## 3. Attack on the changed predicate and paired positive

Source-derived decisions, **not observed runtime outputs**:

| Decision component | Assigned negative | Paired positive |
| --- | --- | --- |
| Decoded stdout / return code | Original full stdout / `0` | Same |
| Decoded stderr | `ERROR: synthetic producer incomplete\n` | Empty string |
| Recognized failure lines | None | None |
| Exact summary / auxiliary inventory | Match / empty equals empty | Same |
| Pass-pattern count | `78 == 78` | Same |
| Summary stderr conjunct | False | True |
| Final `matched` | **False** | **True** |

The important adversarial distinction is that **`ERROR:` is not a recognized failure-line prefix**: A:356–359 recognizes `FAIL\t`, `CASE\tFAIL\t`, and the specified later-column CASE/FAIL form, not this error line. Thus merely combining stderr into `failure_lines` (A:396) would not reject the assigned input. The negative depends on the new summary-path stderr condition, rather than obtaining an accidental rejection from the existing failure detector.

A:223–224 and A:393–394 preserve the error stream as a nonempty decoded string. A:118 and A:395 derive summary lines only from stdout. The frozen literal summary matches at A:415–417; no `INVENTORY\t` rows are present, so the auxiliary comparison at A:432–436 also matches. The frozen step does not request baseline-mismatch counting. A:446–450 yields the expected 78 pass-pattern matches from the unchanged stdout.

The initial condition at A:410 is true for both reconstructed inputs: zero return code and no recognized failure lines. At **A:463**, `matched and summary_match and pass_match and not stderr` rejects the negative and preserves the positive. The special carry-invariant branch at A:464–465 does not apply to this step. A:537–538 returns a Boolean result, so F:97's strict Boolean check also agrees with each literal expectation.

**Concrete mismatch: none found for the assigned pair.** In particular, the fixture does not put the mutation in the wrong stream or preserve the original empty stderr accidentally. Conversely, this pair alone does not establish every other nonempty-stderr case, all 214 vectors, producer authenticity, or universal malformed-input totality.

## 4. One bounded mutation draft — ordinary equality replacing type-exact comparison

**Draft only; do not apply in this leaf.** At A:377, replace the single condition:

```python
if type(observed) is not type(expected):
```

with:

```python
if observed != expected:
```

Keep A:378–387 unchanged. This is one behavior-bearing comparison change: it removes exact decoded-type rejection and substitutes ordinary Python value equality. The remaining scalar return at A:387 is already ordinary `observed == expected`.

**Exact expected killing case:** `scalar/r13-counter-31984f4/F2_entry/bool` (O:3040–3051), literal `want=false`, setting only `F2_entry` to JSON `false`. I:208–227 requires the exact counter object with integer `F2_entry: 0` and `exact_json=true`. R:3617–3620 supplies zero exit status, empty stderr, and the original counter stdout. F:72–82 actually replaces that field and JSON-serializes it, so the Boolean is not converted into integer zero by the fixture.

[INFERENCE — static prediction] With pristine A, the Boolean leaf fails A:377 because `bool` is not `int`; the detector should observe `False`, matching the literal expectation. With the drafted condition, ordinary `False == 0` equality permits both the enclosing dictionary value comparison and that scalar leaf. All other fields are unchanged. The Boolean/numeric equality hazard is also the explicit subject of S:125; that registry entry was read, but its external documentation was not reopened in this leaf.

[INFERENCE — static prediction] A:472–473 then accepts the mutated exact JSON comparison. `numeric_leaves` excludes Boolean leaves (A:370–371), but its resulting count discrepancy is only diagnostic in A:480–490: A:492 does not require those counts to match. With zero exit status and empty stderr, the drafted mutant therefore returns `matched=True`. F:97 rejects that against literal `want=False`.

**Expected bounded detector:** F with `--case scalar/r13-counter-31984f4/F2_entry/bool`, against pristine, isolated-mutated, and restored copies of the same runner bytes. No such calls were made here. The predicted single-case results are:

| Runner bytes | Expected detector fields | Expected outcome |
| --- | --- | --- |
| Pristine candidate | `expected=false, observed=false, exception=null, pass=true` | `total=1, pass=1, fail=0`; exit `0` |
| Drafted mutant | `expected=false, observed=true, exception=null, pass=false` | `total=1, pass=0, fail=1`; `finding_id="R22-RESULT-CONTRACT"`; exit `1` |
| Exact restored candidate | Same as pristine | Same as pristine |

These fields and exits are predictions from F:97–111, not invented detector output. The assigned stderr negative and its positive use the summary branch, not `json_exact`; they are not themselves killers for this equality mutation. The separately named scalar vector is the exact proposed killer.

Mutation output: **none — unexecuted**. Verdict: **empirically INCONCLUSIVE / NOT RUN; statically predicted killed by the named scalar vector**. A baseline failure, if L1 later observes one, would make that mutation experiment inconclusive rather than killed.

## 5. Byte preservation, tools, and limits

No source bytes were changed, so there are no actual mutated bytes or restoration operation to claim. Two `sha256sum` observations, before and after the source review, produced identical values for every input below. The pinned-source hash comparisons described above were also observed.

| Absolute source path | SHA-256 before = after |
| --- | --- |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-21/run-acceptance.py` | `00d0e9c2fda2fde2d21cb74b1a1dd5b1db7b1ea679cdfd4239d91aa186e080a6` |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r22-result-oracle.py` | `3c0776ae1df8cd487380a8a94203848e3a24c5bc910762a23f63fc335697a604` |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r22-result-oracle.json` | `292442a6ec078b7cc20526b4ba7ab1300eb08bc9cc4dbaf9894472120dcd0651` |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-21/step-inventory.json` | `8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310` |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-21/final-out-S1.json` | `bc53a75285a4fafdb6f4f8c2de0a4068fa87494c2745faa1ef6af11ec25738fe` |

Tools installed/updated: **none**; no installation channel or version change applies. All pacman transactions remained paused. Hashing and `git show` were read-only source-identity operations, not behavioral probes.

This report makes no all-214 or actual-18-step execution claim and grants no admission. F5 bytes and its 160-byte synthetic-only scope were not modified or reassessed. Reap/NAMESPACE/exposure assessment remains HELD; certification remains OFF and K5 HELD. No malicious-producer attestation is inferred.

Report: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/w2/Attack03.md
