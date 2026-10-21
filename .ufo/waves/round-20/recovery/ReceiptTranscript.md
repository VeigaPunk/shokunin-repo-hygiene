# ReceiptTranscript — adversarial calibration review

## Scope and observed bytes

Read-only static review of transcript receipt production and the missing-transcript denominator. No target code, test, build, or fixture was executed; no files other than this assigned report were written. The observed repository HEAD was `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`; the initial working-tree status showed the reviewed production files modified. The initial parallel byte capture reported these SHA-256 values:

| Path | SHA-256 observed in initial capture |
|---|---|
| `tools/souji-seat-audit.py` | `86c678de98fd2d37e4ab4b33d286da741291d6258d03adc38ba9fe084b1d296c` |
| `tools/souji-rev-pin.py` | `869d399ca1ec2868e9c794e438298a9dfd844eed76e5d477fa38b710f170e49d` |
| `census/round-13/run-verification.py` | `945cf6ecd5f4472c2556eb6f0b26e0a42193268a158cf3a0a8d776c00ef1d0cc` |
| `census/round-14/run-verification.py` | `bde95f972e09de393d32b1aa840bc2282f1677c147399ae7ed24c6558f525f73` |
| `census/round-14/run-targeted.py` | `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2` |
| `census/round-14/cache-demonstration.py` | `706200486d0938322a773116ae01377f3a56ec82443415e0d1956cd126c95bd6` |

The audit source changed between its first source read and a later targeted literal search: that later result was snapshot `[souji-seat-audit.py#5B7D]` and showed added symlink refusal (`:376-377`) and `input_scope` (`:413-414`) relative to the first read. The initial SHA above is therefore not asserted to fingerprint that later snapshot. Findings below are limited to control flow visible in both observations; no waiting or polling was done. No `lsp` device was present in the mounted tool inventory, so no LSP status/references/definition/diagnostics were available; line anchors use literal search as fallback, not semantic proof.

## Findings

### HIGH — The transcript denominator is only the spec item list; unlisted transcript files are silently omitted

`tools/souji-seat-audit.py:368-371` consumes and fingerprints `MANIFEST.sha256` as bytes, but does not parse its entries. At `:372-380`, the run initializes `missing_transcripts` and iterates only `spec["items"]`; it reads a transcript only for each item name. At `:410-414`, the receipt hashes only paths placed in `input_bytes` by those reads. There is no reconciliation of the manifest roster or `*.txt` files in the transcript directory against the spec roster. Consequently a transcript file present in the directory but not named in the spec is neither audited nor included in `input_sha256`, and does not affect `missing_transcripts`. A clean listed transcript plus an additional unlisted transcript can therefore produce `missing_transcripts=[]` while the receipt omits bytes in the supplied transcript set.

**Concrete oracle delta:** add one synthetic case with a one-item spec (`A`), `A.txt`, and an additional `B.txt` listed in `MANIFEST.sha256`. Require `run()` to refuse or explicitly report `B` as unconsumed and bind its digest; the current source has no path that can do so. Keep the spec, manifest, and transcript set equality check explicit so the expected denominator is falsifiable.

**STATUS: OPEN** — C1 cannot claim complete transcript-set binding from these receipts until the expected roster and consumed transcript set are reconciled. The round-19 lesson records a historical 170-entry manifest and matching spec/result/transcript seat-name sets; that is historical evidence, not a fresh test of this current code path.

### MEDIUM — Sequential rechecks permit a transcript to drift after its own check while the run still reports all inputs unchanged

`tools/souji-seat-audit.py:401-412` re-reads each path once in insertion order, compares it with the originally consumed bytes, then sets `inputs_unchanged_during_run=True`. The comparison for an earlier transcript is complete before later inputs are re-read. **[INFERENCE]** If an earlier transcript is changed after its comparison while a later input is still being checked, no subsequent check revisits the earlier transcript; `run()` can return the original digest and the `True` flag despite the on-disk bytes having changed before return/output. This is a check-window race, not an observed execution.

**Adversarial oracle:** use a deterministic read hook on a two-transcript fixture to replace the first transcript immediately after its second read while the second transcript is being re-read. Require refusal before receipt output (or narrow the result field to claim only that each individual comparison matched). No such race test was run here.

**STATUS: OPEN** — the source's sequential recheck does not establish an atomic whole-input snapshot. This is an inference from ordering, not a claim of a reproduced failure.

## Residual risk and verification gaps

- Missing transcripts are listed and rechecked for appearance at `tools/souji-seat-audit.py:407-409`, but the CLI exit status remains based only on major violations at `:646-647`. A consumer must inspect `missing_transcripts`; exit 0 alone is not a complete-transcript verdict.
- A spec with duplicate item names is not visibly rejected before the name-keyed `seats` mapping is populated. Duplicate names can make a row count differ from the number of spec items; this was not exercised.
- The prior round-19 transcript-manifest match is a historical receipt reported in `corpus/lessons/round-19-verifier-spotcheck.md`, not fresh execution or independent current-byte validation. The current review performed no runtime verification.