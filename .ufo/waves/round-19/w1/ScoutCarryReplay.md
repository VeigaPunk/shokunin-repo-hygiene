STATUS: DONE — committed replay semantics and wrap-rule impact resolved.

# Findings

- **Comparison semantics:** `compare()` checks (1) expected exit against both the observed subprocess return code and the JSON payload's `exit`, and (2) exact multiset equality of `(finding id, path)` pairs. Pair order is ignored; duplicate multiplicity is significant. It does **not** byte-compare output: stdout, stderr, summaries, or gate bytes are not part of the per-replay verdict comparison. The expected-vs-observed gate SHA match is recorded separately and does not gate `all_match`; the round-18 record has `gate_sha256_match: false` while overall `match: true`.
- **Five `(name, rev, round)` replay tuples, in runner order; expected verdicts:**
  1. `(r15-landing, b410186, 15)` — exit 1, 5 findings: 2× `LG-FROZEN-MEASURED`, one each `LG-FROZEN-PIN`, `LG-PARSE-REG`, `LG-SEAT-UNCARRIED`.
  2. `(r13-admitted, a31642d, 13)` — exit 0, no findings.
  3. `(r14-landing, cc21683, 14)` — exit 0, no findings.
  4. `(r16-landing, 6ff91f5, 16)` — exit 0, no findings.
  5. `(r16-precarry, 79bbe7a, 16)` — exit 1, 29 `LG-SEAT-UNCARRIED` findings.
- **Wrap impact:** applied unconditionally, only `r16-landing` changes: its 7 unmarked wrapped STATUS cuts become 7 `LG-SEAT-UNCARRIED` findings (and therefore exit 1 instead of 0). The other four retain their old verdicts: r13 exit 0/0 findings; r14 exit 0/0; r15 exit 1/5 findings (including its existing `LG-SEAT-UNCARRIED`); r16-precarry exit 1/29. With strict matching gated at `--round >= 18`, none of these five replay verdicts change: all their rounds are 13–16, so they take the old branch.

# Evidence

- The three assigned replay evidence files were read from the lane, and a read-only `git diff --quiet 3ab2c81 -- <three paths>` returned identical-to-base; these reads therefore match the committed base bytes. Tuple declarations: `census/round-17/gate-replays.py:72-77`; expected outcomes/findings: `census/round-17/gate-replays-expected.json:11-185`; observed round-18 record: `census/round-18/gate-replays-final-4800fd7.json:3-14,17-23,44-55,71-99,124-155,274-276`.
- Exact comparison implementation: `census/round-17/gate-replays.py:165-190`; SHA diagnostic and return path: `:295-296,299-335`.
- Replay impact is recorded in the committed prior carry-wrap analysis `.ufo/waves/round-18/w1/ScoutCarryWrap.md:96-112` (table rows at `:100-107`, strict-only effect and gated recommendation at `:110-112`). It records the seven wrapped r16-landing cuts and unchanged 0/0/1/29 replay counts elsewhere.
- Current carry branch constants/selection: `tools/souji-landing-gate.py:121-123,496-518`; exit meaning is documented at `:1002-1005`.
- LSP was not available in this seat's tool inventory. Grep was used only to locate source anchors; conclusions above come from the source/file reads and the recorded replay-impact analysis.

# Commands run

- Read the preregistration, the three assigned files, the relevant carry-gate section, and the prior carry-wrap analysis; no runner or gate execution.
- `wc -l` on the three assigned files: 341, 185, and 326 lines respectively.
- Read-only `git diff --quiet 3ab2c81 -- census/round-17/gate-replays.py census/round-17/gate-replays-expected.json census/round-18/gate-replays-final-4800fd7.json` — identical to base.
- `grep` source searches to locate tuple, comparator, round-gate, and result lines.

# Contract compliance

No subagents, mutations, runner/gate/tests, network access, scratch files, or tool installs. Only this scoped report was written.