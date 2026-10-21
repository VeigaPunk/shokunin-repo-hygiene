STATUS: DONE — derived carry fixture outcomes; identified vacuity and counter-assertion gaps

# Findings

## Medium — base-arm vacuity guard can pass without the intended false-pass discriminator

`tests/fixtures/r19-carry-wrap.py:213-225` increments `base_failed` for any base result that differs from the changed-arm expectation, then rejects only `base_failed == 0`. It does not require the unmarked-cut case itself to discriminate. The base implementation at `tools/souji-landing-gate.py@3ab2c81:393-449` matches the source marker against each physical lesson line and requires the carry token on that same line. Static derivation gives two base mismatches: TC1 is a false pass (exit 0, no finding), and TC4 is a false fail (exit 1, `LG-SEAT-UNCARRIED`). Thus TC4 alone can satisfy the current vacuity guard even if the base arm no longer demonstrates TC1's intended false pass. Require the exact TC1 base result (exit 0, IDs `[]`) and changed result (exit 1, IDs `[LG-SEAT-UNCARRIED]`); preferably assert the complete base signature in the table below as well.

## Low — the external fixture discards the requested counter fields

`tests/fixtures/r19-carry-wrap.py:147-162` extracts only the process exit and finding IDs from JSON, and `:202-219` compares only those values. The `summary` fields are never checked, so counter regressions can leave all fixture cases green. If the fixture is intended to evidence that each carry stimulus was actually counted, assert all four counters per run.

# Evidence

`tools/souji-landing-gate.py:364-375,398-404` identifies one failure-channel marker and counts STATUS-opening lines; `:421-464` joins wrapped paragraphs and lesson entries and applies whole-paragraph or line-end-ellipsis matching; `:467-539` counts the report files, markers, statuses, and heading; `:1128-1138,1172-1188` emits those counters and derives exit status from findings/errors. `tests/fixtures/r19-carry-wrap.py:58-100,117-144` supplies one report and lesson with the same single failure marker in each of its four cases. Its `SKILL.md` fixture paths and lesson citation resolve to files it creates (`:44-55,126-133`), so no unrelated missing-reference or parse finding is expected.

Static expected matrix (`checked_markers / checked_reports / status_lines / carry_heading`):

| Case | Changed gate: exit / finding IDs | Counters | Base gate (`3ab2c81`): exit / finding IDs |
|---|---|---|---|
| TC1 `wrap-unmarked` | 1 / `[LG-SEAT-UNCARRIED]` | 1 / 1 / 1 / 1 | 0 / `[]` |
| TC2 `wrap-marked` | 0 / `[]` | 1 / 1 / 1 / 1 | 0 / `[]` |
| TC3 `wrap-complete` | 0 / `[]` | 1 / 1 / 1 / 1 | 0 / `[]` |
| TC4 `wrap-bullet-wrapped` | 0 / `[]` | 1 / 1 / 1 / 1 | 1 / `[LG-SEAT-UNCARRIED]` |

Derivation: `check_carry` scans one `.md` report under the round-18 wave prefix; its `STATUS: PARTIAL` line is one status line and one failure marker, and the lesson contains the exact carry heading (`tools/souji-landing-gate.py:98-110,339-375,467-539`; fixture `:58-100,126-133`). The changed gate rejects only the unmarked cut; the marked cut satisfies the ellipsis predicate, the complete quote matches the normalized full paragraph, and the wrapped lesson continuation is joined. The base's line-local matching silently accepts TC1 because the quoted source first line and `open` are on the same bullet line, but fails TC4 because the source phrase and `open` are split across the bullet's two physical lines (`tools/souji-landing-gate.py@3ab2c81:393-449`).

All four changed-arm expectations in the ExecCarryFixture brief are consistent with the harness (`.ufo/waves/round-19/w1-spec.json:53`). The brief does not state exact base tallies; if an expected base count of one mismatch was intended, it is wrong: the derived base count is two. The fixture's `SUMMARY` is statically expected to be `total=4 failed=0 base_discriminating=2` when all changed cases meet the table (`tests/fixtures/r19-carry-wrap.py:197-228`); this was not run.

# Commands run

- Read the preregistration, wave spec, fixture, current gate, and base gate source; used literal source searches to locate relevant fields.
- Read-only `git show 3ab2c81:tools/souji-landing-gate.py` with line numbering; no fixture, gate, selftest, build, or test was executed.
- Attempted to access `xd://lsp`; the device is not mounted in this session, so LSP status/references/definition/diagnostics were unavailable. Source reads, not grep, support the semantic conclusions above.

# Contract compliance

Wrote only this scoped report. No subagents, lane tools, tests, live census, signal calls, network access, or tool installations. No git/jj mutations.