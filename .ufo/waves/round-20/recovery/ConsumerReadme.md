# Consumer README review — operability

## Finding

**No actionable defect found in the reviewed README count-command examples.** In `corpus/README.md` the Round 20 “Current full-ID counter commands” block uses five lower-case 40-hex arguments (`:304–308`): `31984f473ce4bdab61a99b16cca194b28108cb81`, `6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6`, `a31642d14006830ec62edf40b0354c3699728c4a`, `552cae4204b3ab818419ad8adbfef3a4da29a3e0`, and `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`. The earlier count examples at `:91–92` and `:140–141` are also full IDs. The README says these current commands replace historical strings without rewriting historical LOG, lesson, or `counts.json` bytes (`:301–315`).

This syntax is consistent with `tools/souji-rev-pin.py:34–35` (`^[0-9a-f]{40}$`; durable namespaces exclude `refs/jj`) and the r13/r14 counters’ explicit-revision handling (`census/round-13/count-claims.py:11,16–35`; `census/round-14/count-claims.py:12,17–35`). The source documents that historical counters read the selected committed revision, while their default `HEAD` path is not a substitute for the explicit command examples.

## Concrete oracle improvement

Add a narrow README regression oracle: parse the current Round 20 fenced command block and require exactly five `count-claims.py` invocations with one argument each matching `[0-9a-f]{40}`. As a counterexample mutation, truncate one argument to seven characters and require the oracle to fail; separately assert the pre-existing historical text remains unchanged. This would catch a return to the short-ID operability harm without rewriting the historical records. This is a proposed oracle, not a test run or a claim that the five commands were executed here.

## Residual risk and verification gaps

- **Source-only:** no counter command or target code was executed. Full-ID syntax is observed; current durable-ref resolution and resulting count values were not freshly verified. Historical receipts are not fresh execution.
- LSP was unavailable (`xd://lsp` returned “No such tool”). Text search was used only to locate relevant source lines; conclusions above rely on the subsequent source reads, not grep output as semantic proof.
- Assignment baseline supplied: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. The observed reads were working-tree snapshots, not proven to equal that commit or current HEAD. Read snapshot tags: `corpus/README.md#A028`, `tools/souji-rev-pin.py#B5D6`, `census/round-13/run-verification.py#654A`, `census/round-13/count-claims.py#87BA`, `census/round-14/run-verification.py#312B`, `census/round-14/run-targeted.py#D8E0`, `census/round-14/cache-demonstration.py#CA59`, and `census/round-14/count-claims.py#C292`. The single follow-up checksum call observed these working-file SHA-256 values (not a Git revision mapping):
  - `corpus/README.md`: `91c9a77a4c62f3253d89208a5c2fe150a65bcf3d60e639ca391e48ba7cebdddd`
  - `tools/souji-rev-pin.py`: `d3e9111b66f17242124df97db0327195c75a5c44252566d2130ff38c5755f32e`
  - `census/round-13/run-verification.py`: `72f35605dbda4b2f06b44aa5ad63c8bfc93ff5276628f66475dccb5708df4633`
  - `census/round-14/run-verification.py`: `70aa1ba2f503781ea0359756ef204ae5323e270b044f2856b8c3aab657eba96d`
  - `census/round-14/run-targeted.py`: `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2`
  - `census/round-14/cache-demonstration.py`: `df9209ac21169087bb8c4f114608d17124ad4b092a318a65c88f9aea48b98697`
  - `census/round-13/count-claims.py`: `9c69174ec3345db43633fc04ff79691d6d96e2f9ec9ed795ce5c6047007f0021`
  - `census/round-14/count-claims.py`: `64d967e0d0ec9ae66e14fcc1c7c9411caf3af4755793b8ac8bb9b305f9c0b516`

No source, historical record, fleet, or operator-owned file was edited.