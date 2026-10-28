# R40revenger36 — C3 coverage attack

## Named distinct edge: conflicting duplicate TOTAL rows (first-invalid/last-valid)

**Verdict: bounded measurement plan; no falsifier established against the not-yet-present r40 fixture.** The frozen claim names “duplicate/multiple TOTAL rows” but does not specify whether it means rejecting all duplicates, validating every TOTAL row, or merely recognizing multiple-row input. The r39 parser has a concrete order-sensitive gap that should be measured: it overwrites `total` each time a matching TOTAL is encountered, then validates only the final value. Thus an inconsistent first TOTAL followed by a consistent last TOTAL is accepted by the record parser. This is a distinct case from a straightforward duplicate-identical TOTAL or multiple-rows count test.

## Evidence chain

- Frozen contract: `census/round-40/preregistration.txt`, C3 paragraph (2.2 KB file): requires coverage cases for duplicate/multiple TOTAL rows, `--skip-unrecorded`, and invalid UTF-8 bytes; requires pristine pass, all declared single-defect mutants killed, and all mutants survive r39 base fixture.
- Committed control source: `tools/souji-worktree-drift.py`, lines 150–179 (search result anchor `#10E8`): initializes `total = None`; each TOTAL match assigns a new dict at lines 162–165; only afterward lines 169–178 compares that single dict to rows. This is direct implementation evidence of last-TOTAL-wins.
- Committed r39 fixture: `tests/fixtures/r39-drift-record-rules.py`, lines 40–42 and 87–93 (anchor `#7EED`): creates a single canonical TOTAL and tests one TOTAL-before-rows arrangement, not conflicting duplicate totals. Its own header says r38 addressed TOTAL/duplicate rules, but the inspected r39 case list itself does not exercise the first-invalid/last-valid ordering.

## Exact commands actually run

1. `read /home/vgpnk/.omp/agent/RULES.md` — read successfully.
2. `read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt` — read successfully.
3. `ls /home/vgpnk/Projects/shokunin/souji-shokunin && ls /home/vgpnk/Projects/shokunin/souji-shokunin/census && ls /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39 2>/dev/null; ls /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40 2>/dev/null` — confirmed r40 contains preregistration only; r39 files listed.
4. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -8` — output began `be4cb61 round-39 verifier spot-check ...`, `0242085 round-39: lesson ...`.
5. `ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/ /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/ /home/vgpnk/Projects/shokunin/souji-shokunin/tools/` — listed r39 instruments and r40 preregistration; output truncated for tools listing.
6. `grep -rn "c3" /home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md | sed -n 1,20p` — confirmed prior scorecard C3 entries; not used as semantic proof for this edge.
7. `grep -rn "TOTAL|skip-unrecorded|decode\\(|errors=" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r39-drift-record-rules.py` — showed parser lines 147, 150–179 and r39 fixture lines 87–111.

## Bounded discriminating probe for whoever measures r40

Use the same valid two-REPO body as the r39 fixture (`ROWS` and `TOTAL` at `tests/fixtures/r39-drift-record-rules.py:40–42`). Feed `TOTAL(repos=99, regs=2, prunable=0) + ROWS + TOTAL(repos=2, regs=2, prunable=0)` and then reverse the two TOTAL rows. Record each exact exit/output. A robust duplicate-row contract should either reject both inputs as duplicate TOTALs or validate every TOTAL and reject the inconsistent one regardless of order; last-row-only validation will accept the first ordering and reject the reverse. Run this probe against pristine r40 tool/fixture, each declared mutant, and the r39 base fixture; preserve fixture-owned `SUMMARY` and exit status. Do not claim this probe was run here: r40 fixture/tool and mutants were not present in the inspected round-40 directory.

No production files or frozen claim were changed. No verification run or tool installation was performed.