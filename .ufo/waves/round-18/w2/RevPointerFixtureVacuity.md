STATUS: DONE — Synthetic controls reject the simple broad mutants; historical replay is correct but its minimum-only assertion permits over-reporting.

# Attacked claim: C2 pointer-fixture calibration

Axes reviewed: detecting no findings, over-reporting, and ignored exemptions; correctness and discrimination of the b576341 round-18 replay.

## Findings, by severity

### Low — Historical replay accepts arbitrarily many extra findings

`tests/fixtures/r18-landing-pointers.py:144-164` compares exact `(finding ID, path)` multisets by default, but when `minimum=True` it only checks that each expected count is not below its threshold; it does not reject extra occurrences or other finding IDs. The historical invocation at `:282-306` uses this lower-bound mode, asks for six selected dangling-pointer occurrences, and separately requires exit 2 and six source/detail fragments.

The b576341 replay record already documents why exit 2 is correct: `census/round-18/gate-pointers-before-b576341.json:1-3` reports `no .md reports under .ufo/waves/round-18/` and `exit: 2`. The gate's `check_carry` raises on that condition (`tools/souji-landing-gate.py:388-395`); for round 18+, `evaluate` runs pointer checking first, catches the carry error without discarding pointer findings, and computes exit 2 (`:970-1024`). The record's findings and summary (`gate-pointers-before-b576341.json:4-54,78-90`) show 10 total findings, including the six selected pointer occurrences; therefore the exit-2 result does not imply that pointers were skipped.

**Discrimination:** this historical assertion does reject a silent/no-pointer gate: it requires the six pointer counts, source fragments, and exit 2. But a gate that additionally flags every citation (or duplicates findings) can pass this historical case, because the extra output is unconstrained. The fixture's other synthetic exact-match cases reject a general always-flag behavior, so this is a historical-case coverage gap, not a reason a broad mutant can pass the complete fixture. Smallest improvement: pin the exact `LG-DANGLING-PTR` multiset for the historical revision (including the other baseline pointer rows), while allowing only the known non-pointer finding classes/counts needed for that replay.

## Direct attack questions

- **Flags everything:** it can pass individual positive cases whose candidate pointers are all absent, and can pass the historical case under `minimum=True`. It cannot pass the complete fixture as a blanket behavior: `knowledge-committed-target` (`:207-214`), `round-range-expands` (`:236-245`), and `exemption-honored` (`:254-262`) require exit 0 and an empty finding multiset. The final summary fails if any case fails (`:331-333`).
- **Flags nothing:** it can pass clean cases, and the intentional `vacuity-stub` case itself passes when its stub is silent (`:308-327`). It cannot pass the complete fixture: `skill-uncommitted-target` and `brace-one-missing` require exact positive findings (`:198-205`, `:226-234`); historical replay also requires its six minimum counts (`:282-306`). The stub case specifically verifies that the positive assertion rejects rc 0/no output; it does not replace those selected-gate cases.
- **Ignores exemptions:** an otherwise-correct gate that ignores the valid committed exemption will emit a dangling-pointer finding and exit 1 for `exemption-honored`, which requires no findings and exit 0 (`:254-262`). The malformed-exemption case separately requires exit 2 (`:264-273`).

## Verdict

**Partial for historical exactness; holds for the complete fixture against the three simple mutant classes.** The round-18 exit-2 expectation is correct and remains discriminating against a silent/no-findings gate, but the historical pointer assertion is only a lower bound and cannot establish that the historical replay avoided over-reporting.

## Evidence and verification gaps

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `5efb519f00075d958c3d1109ef6fcb24c487eb87`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- .ufo/waves/round-18 corpus/pointer-exemptions.tsv census/round-17/gate-replays-ddb7347.json census/round-17/jj-receipts-ddb7347.txt` → no output. This corroborates the absent round-18 report tree and the selected old citation targets at the replay revision.
- Read-only source and record inspection only; the fixture and gate were not executed. No `ALLOWED-EXEC` authorization was supplied. The committed replay record cited above was inspected, not regenerated.
- LSP is unavailable in this session: `read xd://lsp` returned `No such tool: xd://lsp` and listed the mounted devices without an LSP device. No references/definition/diagnostics calls were possible; text search was only used to locate source sections, not as semantic proof.
