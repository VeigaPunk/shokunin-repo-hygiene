STATUS: DONE — base carry matching is physical-line based; identified the selftest round-16 default.

# Findings

- **Base reviewed:** `tools/souji-landing-gate.py` at `3ab2c81479f5004c8bc91946eea482caec45408f`.
- Carry-path map:
  - `CARRY_TOKEN_RE` is defined at line 110; case-insensitively it recognizes whole-word `open` or `resolved@` followed by at least seven hexadecimal characters. The carry check uses it at line 431.
  - `norm_line()` is lines 316–322: NFC normalization, removal of `*` and backticks, whitespace collapse, and trimming. It is applied to the source marker at line 427 and each lesson line at line 430.
  - `seat_failure_lines()` is lines 350–361; called by `check_carry()` at line 425. It uses `splitlines()` and tests each physical line independently. `status_value()` (325–331) and `is_failure_line()` (334–347) accept a line whose stripped text matches the STATUS prefix and whose first value word is in the failure vocabulary; fence delimiters and table rows are excluded.
  - `failures_section_lines()` is lines 369–381; called at line 411. After `lesson_lines()` removes HTML comments and splits into lines (364–366), this returns physical lines beneath `## Seat-reported failures` up to the next heading.
  - `check_carry()` is lines 393–449 and is called by `evaluate()` at lines 1028–1030. It normalizes each yielded source line, then compares that needle against each separately normalized lesson line and requires the carry token on that same lesson line (429–433).
- **Finding on wrapping:** Confirmed for an ordinary wrapped STATUS paragraph, with a qualification: this code does not parse paragraphs at all. The source is split into physical lines, so the first line is tested as a marker and later continuation text is omitted unless a continuation independently begins with a failure STATUS line. Lesson bullets are likewise not joined; a wrapped lesson entry cannot satisfy the full source paragraph through cross-line comparison. Thus “only the first physical line is matched” describes ordinary wrapping, not every possible input.
- **Smallest seam:** The central comparison seam is `check_carry()` lines 425–432: replace the per-line source needle and lesson-line comparison with paragraph-aware source and joined carry entries. The current collectors at lines 350–361 and 369–381 expose physical lines only; if paragraph formation is kept in those helpers, both interfaces must be updated to yield joined logical entries.
- **Selftest round-16 hardcode:** `run_selftest()` defines its nested `check()` helper with `round_no=16` at lines 1265–1267. Its `evaluate()` call forwards that default at lines 1270–1271. The literal is the helper’s default argument, not a separate `evaluate(..., 16)` call.

# Evidence

- Base lines above were read from `git show 3ab2c81:tools/souji-landing-gate.py`, saved temporarily under `/var/tmp/souji-r19-ScoutCarryCode-2/`, then searched and read in focused ranges.
- The LSP device is unavailable in the mounted tools (`xd://lsp` returned “No such tool”); the source search was followed by focused line reads, so these are direct source observations rather than LSP semantic results.
- The preregistration’s C1 before/after statement is at `.ufo/waves/round-19/preregistration.txt:7–27`.

# Commands run

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3ab2c81:tools/souji-landing-gate.py > /var/tmp/souji-r19-ScoutCarryCode-2/souji-landing-gate.py`
- Used the search tool on the base copy for carry symbols and round-16/selftest references; read only the relevant base-source ranges and C1 preregistration lines.
- No tests or executable scripts were run.

# Contract compliance

- Wrote only this scoped report; no lane source, tests, or other report files were changed.
- Read-only source inspection; no git/jj mutations, installs, network access, or process signaling. Temporary scratch was removed after inspection.
