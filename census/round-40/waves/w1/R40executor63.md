# R40executor63 — C3 coverage attack

## Explicit edge case: byte-decoding failure can escape before the `RECORD-MALFORMED` refusal contract

**Verdict: Concrete independent edge-case measurement plan; prior committed evidence shows invalid UTF-8 behavior is not merely theoretical, but does not execute the r40 fixture or falsify its frozen claim.**

### Frozen target and distinct axis

Read `census/round-40/preregistration.txt` first. Its lines 10–11 require behavioral C3 coverage for invalid UTF-8 record bytes, plus duplicate/multiple TOTAL and `--skip-unrecorded`; candidate mutants must die, pristine pass and r39 baseline mutants survive. This report examines the **invalid UTF-8 decode boundary specifically** (exception behavior and potential false-positive kill attribution), not the other C3 branches.

### Exact retained evidence

Committed r39 analysis `.ufo/waves/round-39/w1/W1MutDriftRules.md`:

- Lines 31 and 43 inventory `decode("utf-8", "replace")` as previously untested.
- Lines 90–95 give its concrete N4 defect: replacing `"replace"` with `"strict"` makes invalid record bytes raise `UnicodeDecodeError` and produce a traceback; both r39 record fixtures pass the mutant unchanged (`cases=7` and `cases=10`). The distinguishing probe observed pristine drift output including `��` versus a mutant traceback.
- Lines 121–127 specify N4 as a single-defect replacement at the decode call; lines 203–205 explain the behavior. This is direct prior measurement, but it is **not** an r40 C3 receipt or execution.

Committed r39 C3 evidence in `census/round-39/records/c3-after.txt:2-8` reports M11–M14 and `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7`; its frozen mutant definitions and fixture cover trailing whitespace, CRLF, outside-root and indented-comment behavior, not invalid UTF-8 (see `census/round-39/c3-counter.py` MUTANTS and `tests/fixtures/r39-drift-record-rules.py`). Thus invalid UTF-8 is a genuinely distinct historical gap, but round-40's explicit promise remains unmeasured here.

### Bounded measurement plan / failure mode

At the candidate r40 revision, identify the new invalid-UTF-8 fixture case and its declared single-defect mutant from the committed candidate artifacts. Run the pristine tool and that mutant against that case in isolation (same fixture harness/work contract); capture case name, stdout/stderr, exit status, and fixture `SUMMARY`. The intended mutant must make exactly one decode-policy change. A discriminating case should establish that pristine behavior is accepted and that the mutant is rejected by the fixture's own named case with nonzero failures, exit 1, and no traceback. If the only observed failure is a traceback, or another case fails first, that is not evidence of the intended refusal contract. Then run the normal C3 counter for the full frozen predicate and the r39 base arm; report the exact receipt lines. This plan does not establish that the planned candidate is implemented or passes.

### Commands actually run and outputs

1. `read /home/vgpnk/.omp/agent/RULES.md` — read required tooling instructions; no install/update.
2. `read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt` — read frozen C3 predicate (lines 10–11).
3. `glob /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39` — listed committed r39 records/fixtures artifacts.
4. `grep` over `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39` for `skip-unrecorded|TOTAL|invalid UTF-8|mutant` — found C3 counter, r39 receipts, and historical fixture evidence; excerpts above are from committed files.
5. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --short` — output:
   `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`
   `?? census/round-40/`
   No git/jj/index mutation was performed; the untracked census path was present and left untouched.
6. Read `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-39/w1/W1MutDriftRules.md` — read prior probe results cited above.
7. Read `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w1/R40scribe16.md` — confirmed this report takes a distinct C3 edge case, not the peer's C1 axis.

### Limits and final verdict

No r40 counter, candidate fixture, mutant, or C3 receipt was run/read as present; therefore pristine-pass, mutant-killed, base-mutants-survive, TOTAL multiplicity, and `--skip-unrecorded` are **unverified, not pass**. Prior committed r39 evidence supports invalid UTF-8 as a concrete uncovered parser behavior, and its strict-decode single-defect variant has a measurable traceback signature. **No concrete falsifier of the frozen r40 claim is established; bounded plan only.**

Read-only investigation; no production files or fixtures changed. The sole write is this assigned report. Scratch not used. No tools installed or updated.
