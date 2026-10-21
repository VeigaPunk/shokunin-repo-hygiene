STATUS: PARTIAL — The source-level reconstruction below is complete, but I made one scope error: an early pinned `git grep` included `census/round-18` alongside the named source paths, and its output included committed census snapshot/TSV rows. I do not use, cite, or reproduce any of those rows. This was not a live `/proc` scan or fixture run; the search nonetheless violated the historical-snapshot prohibition.

# Reason-field redaction: reconstructed intent and r21 fit

## Reconstructed contract and evidence chain

- `git log --format='%h %s' 544c8358039a07e8b45e6db72312da5c8d965275 -- tools/souji-proc-census.sh` returned the introduction commit `3f822e8` (round-18 build) and the follow-up `4800fd7` (round-18 falsifier fixes).
- In the `3f822e8` addition, `sanitize_field` replaces control bytes with spaces. Separately, `redact_command` sanitizes controls, applies the command-secret patterns, and writes a 160-byte-limited `REDACTED_CMD`. Its call site is `redact_command "$CMD_RAW"`; argv/fd reason construction instead sanitizes `PROC_GONE_PATH` / `PROC_FD_GONE_PATH`, embeds the resulting path in `argv-path-gone:` / `fd-path-gone:`, and sanitizes the complete reason before output. The output comment calls out a “redacted cmd,” not a redacted reason. At pinned `544c835`, these sites remain at `tools/souji-proc-census.sh:188-227,346-368,377`.
- The round-18 fixture makes that split observable: its argv-row assertion requires `reason == "argv-path-gone:" + path` (`tests/fixtures/r18-proc-census.sh:306-313`), while the secret predicate checks `secret not in command`. The fd case likewise expects its complete path (`:625-630`). The census selftest checks exact argv/fd reason paths (`tools/souji-proc-census.sh:603,614`) and checks secret canaries against `row_cmd` (`:604-609`), not against the reason.
- `git show 4800fd7 -- tools/souji-proc-census.sh` expands command redaction patterns and adds command-only synthetic redaction probes/checks. It does not route the reason through `redact_command`; reason-path matching remains exact. Round-18 lesson R18-M9 describes the remaining credential-shape gap as missed redaction controls in P1-P11, but does not identify reason-path redaction as covered.
- Round-20’s final F5 ruling resolves the omission: `corpus/lessons/round-20.md:353-360` says the reason-field issue is a real source-level defect, cmd canaries did not redact argv/fd paths in reason, universal claims were superseded, and historical exposure was unmeasured. Its `:370` finding records that reason received control-byte replacement only, had no secret-pattern redaction or length bound, and the fixture canaries/checks reached `cmd` only. No private-value probe or historical-exposure assessment was performed or authorized.

## Intent and divergence

**Observed:** the implementation separates generic TSV/control-byte sanitation from command-text secret redaction. The reason carries the full path that identifies the residue; existing fixture expectations explicitly depend on that path being intact. Redaction tests were scoped to the command column, so the reason path was not in their redaction oracle.

**[INFERENCE]** The best-supported original intent is to keep a useful, exact non-secret residue locator in `reason` while making the free-form argv command safe for logging. The source and tests support that field-specific contract, but neither commit diff nor the round-18 lesson documents an affirmative decision that reason paths are exempt from privacy protection. Treat the missing redaction as a coverage/design blind spot—not as a demonstrated deliberate security exception. The last-known-good invariant is exact non-secret path identification plus control-byte replacement; the divergence is that a secret-shaped path carried through argv/fd bypasses command redaction and is emitted raw in the reason. This is a static source finding, not an observed private-value leak.

## Does the frozen r21 design preserve it?

Yes, for the intended useful case: preregistration C3 (`.ufo/waves/round-21/preregistration.txt:21-26`) keeps prior control-byte replacement, requires secret argv candidates to become `argv-path-gone:[REDACTED]`, applies the command redaction patterns to path text, bounds the reason to 160 bytes, and explicitly retains byte-exact non-secret path output for the existing argv/fd expectations. Its synthetic `--reason-only` interface is specified to use the same functions as census mode while exiting before `/proc` or boot-id reads; canaries are fabricated, and no live scan is authorized. That preserves diagnostic path value without preserving secret values and directly closes the missed field boundary.

**Bounded design caveat:** the literal requirement “whole reason field bounded to 160 bytes” cannot coexist with “non-secret paths stay byte-exact” for a non-secret path whose prefixed reason exceeds 160 bytes. The frozen wording does not state an exception or precedence. A synthetic non-secret overlength-path case is needed to establish whether r21 satisfies both clauses; I did not execute or modify anything. This does not change the intent for ordinary paths that fit the cap.

The preregistration is design/acceptance authority, not evidence that an implementation or fixture already passes. No build, test, selftest, census, or target execution was run.

## Commands and scope note

Executed read-only commands included:

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %s' 544c8358039a07e8b45e6db72312da5c8d965275 -- tools/souji-proc-census.sh`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3f822e8 -- tools/souji-proc-census.sh`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 4800fd7 -- tools/souji-proc-census.sh`
- The clean, bounded source/fixture search used for line mapping was `git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n -E 'sanitize_field|redact_command|reason|row_reason|row_cmd|secret' 544c8358039a07e8b45e6db72312da5c8d965275 -- tools/souji-proc-census.sh tests/fixtures/r18-proc-census.sh`.

The earlier erroneous search used the same pattern and revision but also included `census/round-18` in its pathspec. Its snapshot output is void for this report and is not reproduced. No runtime behavior or exit status is claimed from the source review.

**Confidence:** High on code flow, exact-path test expectations, and the r20 diagnosis; medium on the historical intent inference; high that the r21 contract intends to preserve non-secret path observability while adding field-specific redaction, subject to the stated 160-byte boundary caveat.