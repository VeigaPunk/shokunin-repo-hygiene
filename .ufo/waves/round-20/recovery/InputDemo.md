# InputDemo — C2 operability review

Observed source state: `HEAD` was `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`; `census/round-14/cache-demonstration.py` working bytes had SHA-256 `df9209ac21169087bb8c4f114608d17124ad4b092a318a65c88f9aea48b98697`. The inspected diff for this file was `bfcee0b..ffb58f8` (32 insertions, 7 deletions). This is source analysis only; no target, build, or test was run.

## Finding — High / C2 blocker: binding refusal still emits a JSON result on stdout

`census/round-14/cache-demonstration.py:1144-1155` handles `git_head()` refusing the initial revision/input snapshot by returning `emit(blocked_payload(...), 2)`. `emit()` unconditionally prints JSON to stdout (`:1106-1108`). The post-run drift path also prints a blocked payload instead of remaining silent (`:1217-1220`). Thus, with a dirty/missing bound input or a detected post-run change, the helper can exit 2 while writing JSON to its caller's stdout; a caller redirecting stdout to its external result destination receives bytes despite the C2 `exit 2/no output` and “no external result on binding refusal” requirements. This is a concrete source-level contract mismatch, not an observed execution.

**Counterexample/oracle:** in an isolated copy, dirty one path from `DEMO_MEASURED_PATHS` (for example `tools/souji-evidence-cache.py`), call the demo with captured stdout, and assert exit 2, empty stdout, and no result artifact. The current initial-refusal branch prints the blocked JSON, so the stdout assertion fails. Route refusal details to stderr and keep stdout/result emission exclusively on the successful/non-refusal path; apply the same no-output rule to the final drift branch.

## Input-byte scope checked

`DEMO_MEASURED_PATHS` (`:80-89`) includes the demo itself, default gate, census script, both named r14 fixtures, the current r13 runner, the revision helper, and `census/round-13/verification.json`. `git_head()` checks the helper against the selected commit and snapshots that set (`:194-211`); the historical JSON is actually read to construct historical entries (`:805-825`). The separately loaded baseline runner is identified by fixed `BASELINE_COMMIT`/`BASELINE_RUNNER` and its consumed source receives a `source_sha256` in the emitted baseline control (`:742-746`). Within this bounded source review, I found no missing default-gate or history input to nominate beyond the stdout/refusal defect.

## Residual risk and verification gaps

This review did not exercise dirty-input refusal, post-run drift, or any runtime behavior. No LSP device was available (`xd://lsp` returned “No such tool”); the source locations above come from direct bounded reads, not semantic-reference proof. No tools were installed or updated.

Report: `.ufo/waves/round-20/recovery/InputDemo.md`
