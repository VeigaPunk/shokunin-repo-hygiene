STATUS: DONE — the overlap scan found one production STATUS-carry parser and no separate parser needing the C1 paragraph rule.

# Findings

- **Only production carry parser: `tools/souji-landing-gate.py`.** `seat_failure_lines` intentionally discovers a STATUS marker on its starting physical line and returns its line number; `check_carry` uses that index to build `status_paragraph`, while `carry_entries` joins wrapped lesson bullets before `carries` compares them. The paragraph rule belongs in that comparison path and is already present for rounds 18+. It governs both `LG-SEAT-UNCARRIED` and the subsequent open/admitted decision (`LG-OPEN-ADMITTED`); it should not turn the marker-discovery step into a paragraph counter. `status_line_count` is a separate coverage count of STATUS starts, not a carry verdict, so it should remain line-based.
- **No second STATUS / LG-SEAT / LG-OPEN parser found in `tools/` or `tests/`.** The other relevant line-indexed parser is `tools/souji-seat-audit.py:249-255`: it parses one rendered `→ tool(args) ⇒ result` call per physical line using `CALL_RE`. That is an event/transcript grammar, not a STATUS quote or lesson bullet; C1 paragraph joining should not apply. Its per-line call identity is not duplicated by the carry work.
- **Test-side near matches are harnesses, not parsers.** `tests/fixtures/r16-landing-gate.py:165-174` splits and checks the gate's TSV output, not report quotes/bullets. Its synthetic round is 77, so the strict gate behavior applies to any wrap case it might add; its one-line cases do not establish another parser. Its separate round-15 historical replay must stay on legacy behavior under the `--round >= 18` gate. `tests/fixtures/r19-carry-wrap.py` constructs wrapped report/bullet inputs and reads JSON findings; it does not implement carry parsing.
- **Yes, the paragraph ground is already duplicated within r19 C1 coverage.** The preregistered C1 explicitly names the unmarked cut, ellipsis-marked cut, complete paragraph, and wrapped lesson bullet. The gate selftest and `r19-carry-wrap.py` exercise those same shapes. This scan therefore identifies no additional implementation surface; it is an overlap inventory, not a request to broaden the parser.

# Evidence

- `tools/souji-landing-gate.py:339-375` — STATUS start parsing and `seat_failure_lines` line-index output; `:383-395` — failure-section extraction; `:398-428` — physical marker count and source paragraph continuation; `:431-464` — wrapped carry-entry joining and paragraph matching; `:467-538` — strict round-gated caller and both findings.
- `tools/souji-landing-gate.py:122` — strict-wrap threshold; `:2092-2171` — selftest cases for unmarked cut, marked cut, complete paragraph, and wrapped bullet.
- `tools/souji-seat-audit.py:64,249-255` — anchored call-line parser; its input is tool-call events, not STATUS text.
- `tests/fixtures/r16-landing-gate.py:66-68,147-174,362-382` — synthetic round 77, historical round 15, and a gate-output row parser / one-line compatibility case.
- `tests/fixtures/r19-carry-wrap.py:2-25,58-100,147-162` — fixture purpose, four constructed carry cases, and JSON finding extraction.
- `.ufo/waves/round-19/preregistration.txt:7-28` — C1's declared paragraph rule, threshold, and named test commands.

# Commands run

- Read the round-19 preregistration and the current worktree bytes of the cited tools and fixtures.
- Searched `tools/` and `tests/` for line-index/split-lines patterns, `seat_failure_lines`, `LG-SEAT`, `LG-OPEN`, STATUS markers/parsing, and carry/bullet patterns. Broad line-index hits unrelated to STATUS/carry were excluded.
- No shell commands or tests/fixtures were executed; this report records static inspection only.

# Contract compliance

- Wrote only `.ufo/waves/round-19/w1/ConnCarryParsers.md`.
- No subagents, git/jj mutations, signals, network access, installs, or scratch files. Reviewed current worktree bytes; did not claim test execution or treat integrated code as verified by running it.