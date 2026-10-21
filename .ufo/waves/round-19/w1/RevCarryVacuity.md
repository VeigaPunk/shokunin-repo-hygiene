STATUS: DONE — arbitrary-prefix ellipsis matching is vacuous; source-line-boundary prefixes are the minimal guard, and wrapped lesson entries still require joining.

# Findings

The concrete source paragraph is the two physical lines in the carry fixture: `STATUS: PARTIAL — guarded repos measured and the` followed by `remaining arm never runs under a bound.` (`tests/fixtures/r19-carry-wrap.py:58-62`; the same source is specified in `.ufo/waves/round-18/w1/ScoutCarryWrap.md:120-128`). The following are **constructed adversarial lesson entries**, not observed test output. Each contains the required `open` carry token (`tools/souji-landing-gate.py:107-111`):

1. Mid-first-line cut:

   ```text
   - SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "STATUS: PARTIAL — guarded repos …" — open
   ```

   This stops after `guarded repos`, although the same source physical line continues with `measured and the`. A permissive matcher that accepts an ellipsis after a mid-line textual prefix would falsely carry it.

2. Arbitrarily short proper prefix:

   ```text
   - SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "STATUS: PARTIAL …" — open
   ```

   This is also a proper prefix of the paragraph, but not the end of any complete source physical line. Accepting any proper prefix followed by an ellipsis makes a one-clause label appear to carry the entire paragraph. The draft itself calls out this vacuity example (`.ufo/waves/round-18/w1/ScoutCarryWrap.md:92,179`).

For this two-line source, the only shorter **source-line-boundary** prefix is the complete first line. Accepting that prefix with an ellipsis is intentional, not vacuous: it marks the actual wrap. For contrast, the existing fixture's marked entry quotes that full first line and then `…` (`tests/fixtures/r19-carry-wrap.py:64-69,82-86`).

**Minimal non-vacuity guard:** derive candidate prefixes only by joining the first `k` complete source physical lines, for `1 <= k < len(block)`, and accept an ellipsis only immediately after one such exact normalized prefix (with the specified whitespace/closing-quote allowance). Do not accept an arbitrary proper textual prefix. The drafted rule has this guard in `ScoutCarryWrap.md:74-83,86-92`; the worktree implementation likewise iterates only `k in range(1, len(block))` and forms each prefix from `block[:k]` (`tools/souji-landing-gate.py:446-464`). A complete normalized paragraph remains a separate accepted case.

**`carry_entries` cannot be dropped while retaining per-physical-line lesson matching.** The wrapped-bullet fixture has the complete quote split after `remaining`, with `arm never runs under a bound." — open` on the next physical line (`tests/fixtures/r19-carry-wrap.py:94-100`). Without joining, neither line contains the complete paragraph: the first has text beyond the valid first-source-line cut but no ellipsis there, and the second lacks the initial `STATUS` prefix. Thus the entry would be falsely reported uncarried. The implementation joins prose continuation lines before applying `carries` (`tools/souji-landing-gate.py:431-443,497-510`). The join behavior is required; only the helper's name/placement could be removed if equivalent joining remains.

# Evidence

- Draft semantics and its explicit vacuity warning: `.ufo/waves/round-18/w1/ScoutCarryWrap.md:74-94,118-128,175-180`.
- Source and carry-token predicates: `tools/souji-landing-gate.py:107-125,407-464,497-518`.
- Wrapped-bullet fixture shape: `tests/fixtures/r19-carry-wrap.py:58-100`.
- These are static findings from the current worktree bytes. The fixture is not evidence that the gate was executed; no gate or fixture was run.
- No LSP device is mounted (`xd://lsp` returned “No such tool”); the literal `grep` lookup only located declarations. Semantic claims above are based on the directly read implementation and fixture, not grep output.

# Commands run

- Read the round-19 preregistration, round-18 carry-rule report, current gate implementation, and current carry fixture through file reads.
- Used a literal search to locate carry declarations after the LSP-availability check failed as noted above.
- No shell commands, tests, fixture, gate, census, or external-document requests were run.

# Contract compliance

Only this scoped report was written. No source/test files were changed; no subagents, git/jj mutations, installs, network requests, process signals, or census commands were used. No scratch files were created.
