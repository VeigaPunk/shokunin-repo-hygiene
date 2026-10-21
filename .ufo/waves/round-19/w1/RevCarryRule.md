STATUS: DONE — static review completed; the core two-direction rule is coherent, but the round gate preserves a known r16 false pass and the stated “no hidden known cut” expectation conflicts with replay preservation.

# Findings

## High — the r18 threshold leaves seven known r16 unmarked cuts green

`check_carry` selects the strict parser only for `round_no >= 18` and otherwise retains the old one-physical-line matcher (`tools/souji-landing-gate.py:496-517`). At r16 landing, seven wrapped STATUS paragraphs are carried only through their first physical line, with no ellipsis; the recorded replay is still exit 0 / no findings (`.ufo/waves/round-18/w1/ScoutCarryWrap.md:20-32,100-112`; `census/round-17/gate-replays-expected.json:53-58`). Strict matching would add those seven findings, while the r17 tip/landing rows show no strict-only delta (4/4 and 0/0 respectively; `ScoutCarryWrap.md:105-108`). Therefore the r18 gate does preserve the old pinned r16 result, but it does **not** avoid hiding every currently known r16 cut.

This is a decision conflict, not something the threshold can satisfy both ways: preserving the pinned r16 tuple leaves the seven cuts unreported in that historical run; surfacing them changes that tuple and requires an intentional expectation/record update. If pins are binding, C1 and the rule report should say the strict guarantee starts at round 18 and explicitly retain the seven r16 false passes as historical compatibility debt. Do not also claim that no known r16 cut is hidden. If no known cut may remain hidden, update the r16 expected finding multiset and disclose that the replay changes.

## Medium — add edge cases for both cut soundness and wrapping interactions

The four proposed/current cases are good core controls: unmarked cut rejected, source-wrap cut with `…` accepted, complete source paragraph accepted, and complete paragraph with lesson-side wrapping accepted (`tests/fixtures/r19-carry-wrap.py:58-100`; selftest cases at `tools/souji-landing-gate.py:2092-2171`). They do not yet exercise all branches stated in the rule/briefs. Add:

1. **`midline-ellipsis` (must fail):** source first line is `STATUS: PARTIAL — guarded repos measured and the`; lesson quote is only `STATUS: PARTIAL — guarded …`. Expect exit 1 / `LG-SEAT-UNCARRIED`. This proves an ellipsis at a shorter, non-source-line prefix is not accepted.
2. **`later-boundary-unmarked` (must fail) and `later-boundary-marked` (must pass):** use a three-line source paragraph and cut after its second physical line, respectively without and with an ellipsis. The existing tests exercise only `k=1`; the rule allows every `1 <= k < len(block)`.
3. **`ascii-ellipsis` (must pass):** use `...` at a valid source-line boundary. The executor brief promises both `…` and `...`, but the current four cases use only `…`.
4. **`marked-cut-bullet-wrapped` (must pass):** wrap the lesson bullet immediately after the quoted source-line prefix and put the ellipsis/closing quote on the continuation line. The existing wrapped-bullet case proves a complete quote joins, not this interaction. Include the explicit close-quote-before-ellipsis form (e.g. `"<full source line>" …`) so the draft’s optional-quote placement is unambiguous; the current marked case puts the ellipsis inside the straight quotes.
5. **`round-17-boundary` (scope control):** run a wrapped, unmarked synthetic case at `--round 17` as well as 18. If retaining compatibility, assert and label the round-17 legacy result as an intentional bypass, not as proof the cut is carried. The current fixture and new selftests exercise only round 18 (`r19-carry-wrap.py:149-150`; gate selftest at `souji-landing-gate.py:2107-2170`). The actual r17 tip/landing rows have no strict-only delta, but the five-entry replay runner does not include an r17 case (`census/round-17/gate-replays.py:69-78`).

## Low — make the external fixture’s base-arm oracle exact

The fixture reduces findings to a set of IDs, dropping both multiplicity and report path (`tests/fixtures/r19-carry-wrap.py:153-162`), and treats any nonzero number of base mismatches as sufficient discrimination (`:213-228`). **[INFERENCE]** The expected base behavior is specifically two mismatches: TC1 is the old false pass; TC4 is the old false fail because `open` is on a different lesson line from the source prefix. TC2/TC3 match the clean expectation. Expected changed-arm tally: `total=4 failed=0`; base tally: `base_discriminating=2` (not executed). Assert each case’s base exit and exact `(id,path)` multiset, rather than accepting an unrelated extra base regression as discrimination. The brief should state those exact base tallies.

Also describe replay preservation as **semantic**. `gate-replays.py` compares process/payload exit plus the `(finding id, path)` multiset (`:165-190`); it does not require byte-identical receipts. The existing replay evidence itself records `gate_sha256_match: false` alongside `match: true` (`census/round-17/gate-replays-4f48343.json:2-14`), and the r18 closure explicitly limits the claim to semantic exit/multiset (`corpus/lessons/round-18-verifier-spotcheck.md:82-84`). “No pinned replay changes” should mean those tuples do not change, not byte identity or an unchanged gate digest.

# Evidence

- Reviewed the worktree bytes of `tools/souji-landing-gate.py` (carry parser `:407-464`, branch `:496-528`, selftest `:1355-1364,2092-2171`) and `tests/fixtures/r19-carry-wrap.py` (`:75-100,147-162,197-228`); compared both to base `3ab2c81` with a read-only diff. The strict branch matches the drafted source-boundary rule, and `carry_entries` addresses the lesson-wrap false fail.
- The five pinned replay rounds are 15, 13, 14, 16 and 16 (`census/round-17/gate-replays.py:69-78`); their expected exit/finding values are in `gate-replays-expected.json:11-183`. **[INFERENCE]** Because all use `round_no < 18`, the current branch retains the old matching path for each and should preserve the comparator’s exit + `(id,path)` tuples. The replay runner was not run.
- The seven known r16 unmarked cuts and zero-finding r16 landing record are documented at `.ufo/waves/round-18/w1/ScoutCarryWrap.md:20-32`; its static replay table distinguishes r16 from r17 at `:100-112`.

# Commands run

- Read-only `git diff --unified=5 3ab2c81 -- tools/souji-landing-gate.py tests/fixtures/r19-carry-wrap.py census/round-17/gate-replays-expected.json census/round-17/gate-replays-4f48343.json`.
- Static file reads of the preregistration, work specification, current carry code/fixture, round-16/17 replay inputs and evidence, and the round-18 carry analysis.
- Attempted `read xd://lsp`; tool returned `No such tool: xd://lsp` and listed no LSP device. Thus no LSP status/references/definition/diagnostics were available. `grep` was used only to locate symbols/briefs; semantic findings above are based on the file reads and diff, not grep output.
- No selftest, fixture, replay, build, or other runtime was run; no tool was installed.

# Residual risk

Static review cannot establish that the new selftests or external fixture execute successfully. The historical r16 false-pass remains by design if replay preservation wins; the r18+ rule’s mid-line, later-boundary, ASCII-ellipsis and quote-layout edges are not presently executable acceptance cases.

# Verification gaps

Main should decide and record the r16 compatibility tradeoff, add the listed discriminators (especially the round-17 boundary and combined wrapped-marked case), then run the gate selftest, external carry fixture, and pinned replay runner once. Replay acceptance should be checked by exit and exact `(id,path)` multiset; no byte-identical receipt claim is supported.

# Contract compliance

Only this scoped report was written. No code, test, corpus, census, or protected lane file was edited; no git/jj mutation, subagent, signal, network access, or runtime execution occurred. Scratch was not created. Tool installs/updates: none.
