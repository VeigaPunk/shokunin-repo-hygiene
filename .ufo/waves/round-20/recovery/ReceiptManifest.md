# Receipt / manifest review — calibration

## Observation identity

Baseline `HEAD` observed: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. The six assigned source files were modified in the worktree. Their one-shot SHA-256 capture after the source read was:

- `tools/souji-seat-audit.py` — `08a006657357e94d9153a6279c723340d7b586aa806c2355ec206253f09133c6`
- `tools/souji-rev-pin.py` — `869d399ca1ec2868e9c794e438298a9dfd844eed76e5d477fa38b710f170e49d`
- `census/round-13/run-verification.py` — `385133127c65b09a718c7bc68b5f43a8aebffc9b9602d0578eca0a5093d346eb`
- `census/round-14/run-verification.py` — `34371fa99a0aafffc25780963f83de354c21a11660855a1d4feb2ed419c2e4d6`
- `census/round-14/run-targeted.py` — `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2`
- `census/round-14/cache-demonstration.py` — `df9209ac21169087bb8c4f114608d17124ad4b092a318a65c88f9aea48b98697`

The worktree changed during the concurrent read/hash window (initial and later hash captures differ); source findings below are limited to the read snapshot, notably `tools/souji-seat-audit.py#5B7D` and `tools/souji-rev-pin.py#B5D6`. Per assignment, I did not wait, poll, or reread for a later landing. No target code was executed.

## Findings

**No actionable defect against the preregistered C1 receipt contract.** The contract requests receipts bound to consumed auditor/spec/transcript bytes (`.ufo/waves/round-20/preregistration.txt:2`); it does not require the transcript manifest to serve as an authority that authenticates those files.

In the reviewed seat-audit snapshot, `run()` reads the auditor, spec, optional `MANIFEST.sha256`, and each present transcript as bytes (`tools/souji-seat-audit.py:354-390`), then re-reads consumed inputs for drift and emits a per-path SHA-256 mapping (`:401-414`). Its `input_scope` explicitly excludes historical execution and authenticated authorship (`:412-414`). This is a digest receipt for the bytes consumed in this invocation, not evidence that an earlier run used them.

## Residual risk / precise boundary

The auditor fingerprints the raw `MANIFEST.sha256` file but does not parse its entries or compare a listed transcript digest to the transcript bytes (`tools/souji-seat-audit.py:368-371, 401-414`). Thus a stale or forged manifest entry is not rejected: the manifest and transcript can both be fingerprinted while their relationship remains unchecked. Do not describe this behavior as manifest validation or transcript verification. This is a boundary of the implemented receipt, not a mismatch with the stated fingerprint-only C1 requirement. It also matches the round-19 lesson's distinction between verifying membership/counts and lacking exact input-byte provenance (`corpus/lessons/round-19-verifier-spotcheck.md:70`).

**One concrete oracle addition:** use a synthetic existing `S.txt` and a `MANIFEST.sha256` entry containing the wrong digest for `S.txt`; assert the receipt independently reports each file's actual raw-byte digest and explicitly labels the manifest relationship as unchecked (while making no execution/authorship claim). This locks the distinction between input fingerprinting and manifest-to-transcript verification.

## Verification gaps

Source-only review; no tests, builds, linters, smokes, or target execution were run. The `lsp` device is not mounted (`xd://lsp` returned “No such tool”), so no LSP status/references/definition/diagnostics checks were available. No tools were installed.