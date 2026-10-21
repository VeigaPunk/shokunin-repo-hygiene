# ConsumerSkill — current counter/recheck full-ID review

## Finding

**No actionable product defect found in the assigned SKILL full-ID cutover.** This is a source-only finding, not a behavioral pass.

- `SKILL.md:296-315` directs current historical-counter use to the Round 20 full-40 durable-ID index in `corpus/README.md`, says counters read committed inputs, and explicitly retains the HEAD/branch/short/keep-only refusals. `SKILL.md:254-276` documents the r13 consumer/output contract; `SKILL.md:127-128` names only the resolver self-test, not a short-ID invocation.
- `corpus/README.md:299-315` supplies five current counter invocations and marks them as replacements while preserving old LOG/lesson/counts.json bytes. Their arguments at `:304-308` are written as 40-character lowercase hex IDs. The earlier executable counter examples at `:91-92`, `:140-142`, and `:284-288` are likewise full-length; the cited Round 19 count is a historical correction, not a shortened current command.
- The called resolver contract matches that documentation: `tools/souji-rev-pin.py:34` defines `^[0-9a-f]{40}$`; `:182-224` rejects non-full IDs, requires a resolvable commit and reachability from the durable namespaces (not `refs/jj`), and allows the no-tree-check path only for consumers reading committed bytes. Its CLI at `:376-400` requires `--rev` and returns 2 on refusal. This establishes source-level consistency, not that every listed object currently resolves or is durable.

### Concrete oracle improvement

Add a static documentation-oracle case that follows the pointer in `SKILL.md:309` to the README's “Current full-ID counter commands” block, parses each command's revision argument, and requires `^[0-9a-f]{40}$`. Mutate one current example, e.g. shorten the `b5763415…` argument at `corpus/README.md:308` to `b576341`; require the oracle to fail before invoking any counter. This directly catches reintroduction of the reported short-ID documentation regression without rewriting historical command text.

## Residual risk and verification gaps

- No counter, resolver, runner, fixture, test, or target code was executed. In particular, existence/durable reachability of the five documented IDs and runtime refusal behavior were not freshly verified; this is not a claim of full C2 runner-binding completion.
- No LSP device is mounted (`read xd://lsp` returned “No such tool”); therefore no LSP status, references, definition, or diagnostics were available. The finding rests on bounded source reads, not grep as semantic proof.
- No tools were installed or updated.
- **STATUS: OPEN — scope deviation.** I issued one recursive `grep` rooted at the repository with `gitignore=false` before recognizing the strict file allowlist. That exceeded the permitted bounded reads and may have traversed excluded census content; I cannot certify otherwise. I do not cite or use that search output as evidence, and performed no further repository-wide search. No operator-sweep content is reproduced here.
- The prior round-19 report/evidence was not edited. This report is the only file written for this item.

## Observed source snapshot

At the final checksum observation, `git rev-parse HEAD` was `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. Working-byte SHA-256 values after the source reads:

- `SKILL.md`: `2d33b8717650c23fcd5182a7fef016962ebee189d42f90b46f4f0d8b8c682c9a`
- `corpus/README.md`: `91c9a77a4c62f3253d89208a5c2fe150a65bcf3d60e639ca391e48ba7cebdddd`
- `tools/souji-rev-pin.py`: `d3e9111b66f17242124df97db0327195c75a5c44252566d2130ff38c5755f32e`

These identify the observed worktree bytes; HEAD alone is not asserted to contain them.