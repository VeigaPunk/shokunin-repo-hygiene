# FinalCallerRuntime — round 20

## Scope and identity

Exercised the pinned build in the isolated clone only. The unique branch `souji-r20-FinalCallerRuntime` resolved to `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` (the required base). No production source was changed; this report is the only lane write.

The r20 fixture's actual caller matrix is round-13 verification, round-14 verification, round-14 targeted replay, and round-14 cache demonstration. Its AST-literal input inventories include the helper, caller/wrapper code, frozen fixtures, source inventory, and caller-specific evidence/knowledge paths. The targeted caller adds `census/round-14/verification-attempt-1.json` to round-14 inputs; round-13 prior evidence is included as an extra input. The matrix mutates actual inventoried inputs in isolated Git repos and invokes those four callers with a foreign synthetic `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE` decoy. It also checks helper refusal on malformed/short revisions and a protected census ancestor without traversing that ancestor.

## Executed commands and results

Working directory for every command below: `/var/tmp/souji-r20w2-FinalCallerRuntime/lane`.

1. `python3 -B tests/fixtures/r20-input-binding.py --root /var/tmp/souji-r20w2-FinalCallerRuntime/lane --baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812` — rc 0. The fixture reported all expected cases and exact inventory:

   `INVENTORY exact expected=43 observed=43 missing=- unexpected=- duplicates=0`

   `SUMMARY total=43 pass=43 fail=0 blocked=0 inventory=exact baseline_mismatches=8`

   The 43 passing case IDs were:

   - Helper: `helper-branch-refuse`, `helper-head-refuse`, `helper-input-snapshot-clean`, `helper-keep-only-refuse`, `helper-protected-census-ancestor-no-walk`, `helper-resolve-clean`, `helper-short-refuse`, `helper-walk-error-refuse`, `helper-ambient-GIT_DIR-redirection`.
   - Round 13: `r13-helper-dirty`, `r13-helper-syntax-invalid`, `r13-wrapper-dirty`, `r13-frozen-dirty`, `r13-sources-dirty`, `r13-admitted-knowledge-dirty`, `r13-counted-knowledge-added`, `r13-optional-prior-dirty`.
   - Round 14: `r14-helper-dirty`, `r14-helper-syntax-invalid`, `r14-wrapper-dirty`, `r14-frozen-dirty`, `r14-sources-dirty`.
   - Targeted replay: `targeted-helper-dirty`, `targeted-helper-syntax-invalid`, `targeted-wrapper-dirty`, `targeted-frozen-dirty`, `targeted-sources-dirty`, `targeted-prior-attempt-dirty`.
   - Demonstration: `demo-helper-dirty`, `demo-helper-syntax-invalid`, `demo-wrapper-dirty`, `demo-historical-input-dirty`.
   - Full-ID historical counters: `historical-r13-31984f473ce4bdab61a99b16cca194b28108cb81`, `historical-r13-6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6`, `historical-r14-a31642d14006830ec62edf40b0354c3699728c4a`, `historical-r14-552cae4204b3ab818419ad8adbfef3a4da29a3e0` (each reported full 40-hex ID, exit 0, inventory match).
   - Seven baseline tripwire pairs: `baseline-r13-helper`, `baseline-r13-sources`, `baseline-r13-new-knowledge`, `baseline-r14-helper`, `baseline-r14-frozen`, `baseline-targeted-wrapper`, `baseline-demo-helper`. All seven reported `baseline_tripwire=1 changed_exit2=1 changed_path_named=1 stdout_empty=1 output_absent=1`; the old baseline reached the producer while the altered candidate refused before output.

   The preregistered-baseline comparison reported 49 files and these eight differing SHA-256 identities (current / baseline):

   ```text
   LOG.md 5ed45a1633ca7a34951a5a20b26426a252494be24c4cd8f3283684a2fcb7b4ed / 1a6e78603de8f988598f4a7b45060b9baec91ebf4696daf46d383b2d0ec59f84
   census/round-13/run-verification.py c122d70a2283017b7428524ccf768e9841e7e9ca08099cef7a01897d004760b8 / 15ece20e66bba7ec12a7b482de680e9b4702728eefec10c386f87689c5d8ffb8
   census/round-14/cache-demonstration.py 373daa9d5d0ce18fb90fcf79d8a073e480eb52fe4a4c00850bb3b22599d926b2 / c5aab25aa1b2285181a16445697c9cb6cda34bd8f072cb164f3d903e3180e6c2
   census/round-14/run-targeted.py 33baa042f2bc6f12085775a29ac5a1ef94031ba216d6bd27f0e7b0a3688df405 / 2ca305e6180a90806586888bb5d2e4656e275f4ef38126ef34323dd54fc65f03
   census/round-14/run-verification.py 7d52d690733db433b97c702e5235da313a17de26e15e76b0565c44a0fafbe68f / ce5d3f021f517b6de311b990351708c8fd7f4c9a42dfc83d8677a32c2a9b6e24
   corpus/SOURCES.md 4bda35d5d5a78cd684a429093778adc1af31a41c3b63e78589f7ffbd4c524072 / 436b015c79386b0931641ffe01f4af4c416163e33f8ceed4fd1061a5da72ecff
   corpus/knowledge/process-residue-observations.md d2683a51075255a1df49a4ae8fcff5c2d21467b877dda98ef3228644276b1290 / 980e194e14f363f1706b1eac30747c608162fa8821edc1af43128a78e34fa83c
   tools/souji-rev-pin.py d3e9111b66f17242124df97db0327195c75a5c44252566d2130ff38c5755f32e / d00a947bbf457b4bd79e338f8c0aecc3407e5574c945bf2ec32ff2c157aebe40
   ```

   The fixture reports these as baseline differences, separately from its 43-case pass/fail inventory; they are retained here, not silently treated as a functional pass or adjudicated as authorized changes.

2. `python3 -B tools/souji-rev-pin.py --selftest` — rc 0; `SUMMARY total=11 failed=0`. Passing cases: `durable-clean-accept`, `keep-only-refuse`, `dirty-tree-refuse`, `head-symref-refuse`, `branch-name-refuse`, `short-id-refuse`, `no-measured-paths-refuse`, `path-escape-refuse`, `unknown-rev-refuse`, `historical-no-tree-check-accept`, `historical-tree-check-refuse`.

3. `python3 -B tests/fixtures/r19-rev-pin.py --tool tools/souji-rev-pin.py --tool-dir /var/tmp/souji-r20w2-FinalCallerRuntime/lane` — rc 0; `SUMMARY total=13 failed=0 base_discriminating=6`. Passing current cases: `durable-clean-accept` (exit 0), `keep-only-refuse`, `dirty-tree-refuse`, `head-refuse`, `branch-refuse`, `short-id-refuse`, and `no-paths-refuse` (each exit 2), `historical-no-tree-check` (exit 0), plus the five `wiring/` cases for round-13 verification, round-14 verification, targeted replay, and both count-claims callers. All six old-base controls discriminated the change: base exits 0 for keep-only, dirty-tree, head, branch, short-ID, and no-paths cases.

## Source identities

SHA-256 digests observed in the pinned clone:

```text
160f92c40c6ed62059c1a51f8323eaba7777669bf1cb40bd68c24e2b7d310aef  tests/fixtures/r20-input-binding.py
d3e9111b66f17242124df97db0327195c75a5c44252566d2130ff38c5755f32e  tools/souji-rev-pin.py
d87dc6e854d4edd0647ac483317a81df4fd5b78ca2d0d0dac8777fd70f9596df  tests/fixtures/r19-rev-pin.py
c122d70a2283017b7428524ccf768e9841e7e9ca08099cef7a01897d004760b8  census/round-13/run-verification.py
7d52d690733db433b97c702e5235da313a17de26e15e76b0565c44a0fafbe68f  census/round-14/run-verification.py
33baa042f2bc6f12085775a29ac5a1ef94031ba216d6bd27f0e7b0a3688df405  census/round-14/run-targeted.py
373daa9d5d0ce18fb90fcf79d8a073e480eb52fe4a4c00850bb3b22599d926b2  census/round-14/cache-demonstration.py
```

## Bounded result, risks, blockers

No failing case or unresolved runtime defect was observed in the assigned boundary. The evidence establishes isolated caller refusal on the tested input mutations and full-ID/historical replay behavior at this pinned build. The fixture deliberately tripwires producers in sandbox repos rather than running live suites; these results do not establish live suite success, host state, census state, or global certification. The eight baseline deltas above remain for L1's integration review. Protected census material and host state were not inspected. The outer clone/branch checkout occurred before the later parent instruction to pass child-only `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_TERMINAL_PROMPT=0`, `GIT_OPTIONAL_LOCKS=0`, `GIT_NO_LAZY_FETCH=1` and the prescribed Git `-c` options; those overrides were not supplied. I did not inspect global configuration or rerun Git mutation, so configured hook/maintenance side effects from outer setup cannot be ruled out; none were instrumented or observed.