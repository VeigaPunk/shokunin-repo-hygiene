# R42w2mutationtester07 — mutation test of the r42 C2 counter (`census/round-42/c2-counter.py`)

Seat: R42w2mutationtester07 (role mutation-tester, wave 2, falsify). Judged on operability. Leaf seat; no subagent dispatch.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Tip under attack: `3105a63b23481fccf7df58e74d14a6681e0ea0c8`.
Frozen counter: `census/round-42/c2-counter.py` sha256 `fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1` (the preregistration pin; unchanged at the end of this seat).
Landed tool: `tools/souji-freeze-check.py` at the tip, `tool_sha=9ddd596b98fb` (first 12 hex of its sha256).
Control: `census/round-42/controls/c2-stub-tool.py` (the r41 tool plus an always-green `--selftest`; `tool_sha=6e1c564a94b5`).

## Verdict

**Falsified at the counter level.** The landed tool was not mutated; every finding below is about the frozen counter that scores it.

- Of 60 single-point counter mutants, 28 change no SUMMARY field for either artifact. Of those 28, 8 are behaviour-identical to the frozen counter and 20 are blind spots.
- Two single-point mutants (`A08`, `C08`) and three stacks (`S1`–`S3`) read the r41 control as `cases=37 pass=37` or `patches=3/3`, the vacuity pattern the brief names.
  `S1`–`S3` also flip the control's exit to 0, so the counter reports the r41 tool target-met.
- The built-in stub gate (`stubs[label] = "REJECTED" if sp < sn`) is carried by the case table and the refusal rows. With `A08` (case expectations unchecked) and both refusal
  rows forced true, both stubs score 37/37 and the counter prints `control_clean=ACCEPTED` (W1, exit 1). Flipping the one comparison to `sp <= sn` (`D03`, W2) prints
  `control_clean=REJECTED` for two stubs that pass every row, and exits 0 on the landed tool.
- `G14` moves the 37-case pin into `met()` alone; `G14`+`G01` (`S4`) is a green landed tool with 36 cases.
- The frozen counter is not edited (preregistration rule 1); these are named limits for the L1.

## What was tested

- The frozen counter was read, and each mutant written as a unique-anchor replacement of it (anchor count checked to be exactly 1 before writing) under `mutants/<id>.py`.
  The mutants cover the CASES expectation table (A), the `build()` fixture helpers (B), the five legs and the verdict gate (C), the built-in stubs (D), the `SITECUSTOMIZE`
  text and patch injection (E), and `run_tool`, the refusal checks and the harness (F, G, H). `mutants/` holds 65 counter files (BASE, 60 singles, 4 stacks) plus 5 probe files (V1–V3, W1, W2).
- Four stacks (`S1`–`S4`) combine two or three singles and are reported apart from the single-point count. Probes `V1`–`V3`, `W1`, `W2` are reported in the findings.
- Each mutant (and the pristine BASE, through the same harness) was run as `python3 -B mutants/<id>.py --root <clone at 3105a63…> --rev 3105a63… --tool <artifact> --scratch <dir>`
  against both artifacts: the landed tool `tools/souji-freeze-check.py` and the control `census/round-42/controls/c2-stub-tool.py`.
- Each SUMMARY is compared verbatim to the pristine SUMMARY for that artifact, `tool_sha` included. A change of any field is a change.
- For every mutant that changes no SUMMARY field, the per-case FAIL set was also compared with pristine; all 28 match.

## Pristine baseline (the same harness)

```
landed  (rc=0): SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb
control (rc=1): SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=0/3 tool_sha=6e1c564a94b5
```

The landed line matches the tool digest recorded in `census/round-42/records/c2-after.txt` (`tool_sha=9ddd596b98fb`). The control line matches control B in
`census/round-42/controls/c2-control.txt` (`pass=24 … patches=0/3`, `tool_sha=6e1c564a94b5`). The 13 control failures are the 13 cases the r41 tool cannot pass.

## Table — counter mutants

Columns: mutant | region | change | SUMMARY diff vs pristine for landed / control (exit code in parentheses) | verdict.
`unchanged` means the SUMMARY line is byte-identical to the pristine one. Full SUMMARY lines per mutant are in `receipts/<id>.landed.txt` and `receipts/<id>.control.txt`
(stacks `S1`–`S4` in `receipts/S*.txt`; the W and V probes in `receipts/W*.landed.txt`, `receipts/V*_*.txt`).

| mutant | region | change | landed / control SUMMARY diff | verdict |
|---|---|---|---|---|
| `A01` | CASES | dup-target expectation class KEY-DUPLICATE -> FIELD-MISSING (expectation no longer the r42 class) | `pass=36 fail=1 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `A02` | CASES | heading-valid-tail expects 6 FIELD-MISSING -> 5 | `pass=36 fail=1 (rc=1)` / `pass=23 fail=14 (rc=1)` | CAUGHT: false red on the landed tool |
| `A03` | CASES | population-empty expectation POPULATION-EMPTY -> POPULATION-DIGEST | `pass=36 fail=1 (rc=1)` / `pass=23 fail=14 (rc=1)` | CAUGHT: false red on the landed tool |
| `A04` | CASES | counter-symlink expectation COUNTER-SYMLINK -> COUNTER-DIGEST (the r41 tool's actual class: weakens the control's rejection, reddens the landed tool) | `pass=36 fail=1 (rc=1)` / `pass=25 fail=12 (rc=1)` | CAUGHT: false red on the landed tool |
| `A05` | CASES | population-symlink expectation POPULATION-SYMLINK -> POPULATION-DIGEST (r41 emits the pair DIGEST+EMPTY, so the stub still fails but for a different reason) | `pass=36 fail=1 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `A06` | CASES | dispatch-spec-before claim label C0 -> C1 (prereg-wide label no longer prereg-wide) | `pass=36 fail=1 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `A07` | CASES | clean case expects no finding -> expects NO-CLAIMS | `pass=36 fail=1 (rc=1)` / `pass=23 fail=14 (rc=1)` | CAUGHT: false red on the landed tool |
| `A08` | CASES | case_ok drops the want_rc / want-class comparison entirely (counter accepts any non-crashing tool that prints a SUMMARY: vacuity) | `unchanged (rc=0)` / `pass=37 fail=0 (rc=1)` | VACUITY on the r41 tool: control SUMMARY reads cases=37 pass=37 (case set no longer checked); exit stays 1 only because the patches leg still reads 0/3 |
| `B01` | build | the duplicated key is never written (dup fixture becomes a clean prereg) | `pass=34 fail=3 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `B02` | build | base_side fixture points Base at the main tip (BASE-NOT-ANCESTOR can no longer occur) | `pass=36 fail=1 (rc=1)` / `pass=23 fail=14 (rc=1)` | CAUGHT: false red on the landed tool |
| `B03` | build | dispatch_before fixture writes a name the dispatch rule does not match (w1-notes.json) | `pass=36 fail=1 (rc=1)` / `pass=23 fail=14 (rc=1)` | CAUGHT: false red on the landed tool |
| `B04` | build | the counter symlink is replaced by a regular file copy (the symlink case becomes a clean counter) | `pass=36 fail=1 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `B05` | build | the prereg tail is never appended (the four malformed-heading fixtures lose their heading) | `pass=32 fail=5 (rc=1)` / `pass=23 fail=14 (rc=1)` | CAUGHT: false red on the landed tool |
| `B06` | build | the post-freeze counter edit is a no-op rewrite of identical bytes (FROZEN-EDITED fixture becomes clean) | `NO SUMMARY (rc=1)` / `NO SUMMARY (rc=1)` | CRASH: no-op rewrite makes git commit fail in the fixture builder; no SUMMARY, exit 1 on both artifacts (a false red) |
| `C01` | leg:real | real leg drops the claims=3 requirement (only 'no findings' is left) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: real leg no longer requires claims=3; a tool under-counting claims on the real prereg passes |
| `C02` | leg:retro | retro leg accepts >=1 finding instead of >=3 | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: retro leg accepts one finding where the leg requires >=3 of the 19 pre-grammar findings |
| `C03` | leg:retro | retro leg demands exit 0 instead of exit 1 | `retro=FAIL (rc=1)` / `retro=FAIL (rc=1)` | CAUGHT: false red on the landed tool |
| `C04` | leg:retro_clean | retro_clean leg drops the no-findings requirement | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, equivalent under the exit rule (exit 0 already implies findings=0) |
| `C05` | leg:selftest | selftest leg accepts >=1 self-test case instead of >=12 | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: self-test floor of 1 case instead of 12; a 5-case self-test passes |
| `C06` | leg:selftest | selftest leg drops pass==cases | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: a self-test that prints pass != cases with fail=0 passes |
| `C07` | leg:patches | only patch P1 is injected (patches=1/3) | `patches=1/3 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `C08` | leg:patches | a patch counts as detected unless it timed out (an always-green selftest now counts 3/3: the control's patches leg is vacuous) | `unchanged (rc=0)` / `patches=3/3 (rc=1)` | VACUITY on the r41 tool: control SUMMARY reads patches=3/3 (an always-green selftest is credited with three patches); exit stays 1 only because pass=24 |
| `C09` | verdict | the met() gate drops the requirement that the built-in clean stub is REJECTED | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR alone, blind spot: the clean-stub REJECTED requirement is only observable when a stub is accepted (see W1/W2) |
| `C10` | verdict | the met() gate drops the patches==3 requirement | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR alone, blind spot: patches==3 is observable only in combination with A08 (S3, V3) |
| `D01` | stubs | STUB_CLEAN announces claims=0 instead of claims=1 | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: the stub's claims= count is never compared by case_ok |
| `D02` | stubs | STUB_FINDINGS emits FIELD-MISSING instead of NO-CLAIMS | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: the stub's finding class is never compared; a stub only has to fail |
| `D03` | stubs | a stub that passes every case is still labelled REJECTED (sp <= sn): the stub-rejection gate is vacuous | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR alone, blind spot: the stub gate `sp <= sn` is invisible while both stubs fail cases; it flips the landed exit only with A08 and both refusal rows forced (probe W2) |
| `E01` | SITECUSTOMIZE | P1 no longer reverses the digest (the patch is inert: the tool's own digest logic is not exercised) | `patches=2/3 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `E02` | SITECUSTOMIZE | P2 matches a diff-filter the tool never uses (the patch is inert) | `patches=2/3 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `E03` | SITECUSTOMIZE | P3 matches a git subcommand the tool never runs (the patch is inert) | `patches=2/3 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `E04` | SITECUSTOMIZE | PYTHONPATH is emptied, so sitecustomize never loads (no patch reaches the tool) | `patches=0/3 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `E05` | SITECUSTOMIZE | the patch id is passed under a different env name than sitecustomize reads (the two halves of the patch mechanism are coupled by a literal) | `patches=0/3 (rc=1)` / `unchanged (rc=1)` | CAUGHT: false red on the landed tool |
| `E06` | SITECUSTOMIZE | the patch id default is P1 instead of empty (dead branch: sitecustomize is only on PYTHONPATH when a patch is requested) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, equivalent on this host: no sitecustomize is injected when no patch id is set; the default branch is unreached |
| `F01` | run_tool | the FINDING regex captures only the claim label, never the class (the class multiset is never compared) | `NO SUMMARY (rc=1)` / `NO SUMMARY (rc=1)` | CRASH: IndexError in run_tool (group 2 removed); no SUMMARY, exit 1 on both artifacts (a false red) |
| `F02` | run_tool | the SUMMARY regex loses its anchors (a second SUMMARY line anywhere would be read) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: SUMMARY regex unanchored; a second SUMMARY line is not seen |
| `F03` | refusal | the unresolved-revision refusal check drops the no-crash requirement | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: refusal row without the no-crash requirement |
| `F04` | refusal | the absent-prereg refusal check drops the no-crash requirement | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: refusal row without the no-crash requirement |
| `G01` | CASES | one case is deleted from the table (the counter's own case count drops below the target) | `cases=36 pass=36 (rc=1)` / `cases=36 fail=12 (rc=1)` | CAUGHT: landed reads cases=36; met() requires n==37 and the tool is red |
| `G02` | CASES | the PRISTINE FAIL case count is off by one (dead path while the tool is present) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, equivalent: the +1 count is used only on the PRISTINE FAIL path, unreached while the tool is present |
| `G03` | leg:retro | the retro leg reads the r41 preregistration instead of the r40 one | `retro=FAIL (rc=1)` / `retro=FAIL (rc=1)` | CAUGHT: false red on the landed tool |
| `G04` | leg:retro_clean | the retro_clean leg reads the r40 preregistration instead of the r41 one | `retro_clean=FAIL (rc=1)` / `retro_clean=FAIL (rc=1)` | CAUGHT: false red on the landed tool |
| `G05` | leg:real | the real leg reads the r40 preregistration instead of this round's | `real=FAIL (rc=1)` / `real=FAIL (rc=1)` | CAUGHT: false red on the landed tool |
| `G06` | build:prereg_text | the emitted claim block omits the Kill key (every fixture claim is short one key) | `pass=3 fail=34 (rc=1)` / `pass=3 fail=34 (rc=1)` | CAUGHT: false red on the landed tool |
| `G07` | build:prereg_text | the emitted heading loses its em dash (the tool's heading grammar still accepts it) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, equivalent: fixture heading text only; `## C1 claim 1` is still a valid claim heading to the grammar |
| `G08` | build:prereg_text | the emitted heading becomes a level-3 heading (no claim block is opened at all) | `pass=4 fail=33 (rc=1)` / `pass=4 fail=33 (rc=1)` | CAUGHT: false red on the landed tool |
| `G09` | case_ok | the summary findings count check is weakened to a tautology (the class multiset check is the only one left) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, equivalent: redundant with the class-multiset comparison in case_ok |
| `G10` | case_ok | the class multiset comparison becomes a set comparison (duplicate identical findings are forgiven) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: multiset compared as set; no case expects a duplicated identical finding |
| `G11` | build | the duplicated key always carries the identical value (the 'differs' variant is never built) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, equivalent under the table: dup-base-differs still duplicates Base with a differing value; same expected class |
| `G12` | build | the fixture git identity is removed (the fixture commit cannot be made) | `NO SUMMARY (rc=1)` / `NO SUMMARY (rc=1)` | CRASH: git identity removed; fixture commit fails; no SUMMARY, exit 1 on both artifacts (a false red) |
| `G13` | tool_sha | the tool digest printed in SUMMARY is a constant instead of the scored bytes' digest | `tool_sha=000000000000 (rc=0)` / `tool_sha=000000000000 (rc=1)` | SUMMARY-only: tool_sha field changes, met() ignores it, so the provenance field is unpinned; verdict unchanged |
| `G14` | verdict | the met() gate accepts any case count at or above 30 (the 37-case table is not pinned) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR alone, blind spot: the 37-case pin is only in met(); with G01 it gives a green landed tool (S4) |
| `G15` | run_tool | the crash detector is narrowed to the word Traceback anywhere in stderr | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, equivalent on this host: no case stderr differs between the two crash strings |
| `H01` | refusal | the unresolved-revision refusal check is made trivially true (the stub-rejection label is then carried by nothing else) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: unresolved-rev refusal forced true; the landed tool refuses, so a non-refusing tool passes this row |
| `H02` | run_tool | the per-case tool timeout is 1 second (the TimeoutExpired is not handled in run_tool) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: 1 s run_tool timeout never reached on this host; run_tool has no timeout handler |
| `H03` | git helper | a failed git call no longer raises (a broken fixture is silently scored) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot on a healthy host: failed git no longer raises; no fixture fails |
| `H04` | build | the fixture-root assertion (git rev-parse --show-toplevel == the fixture dir) is dropped | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot on a healthy host: fixture-root assertion never fires |
| `H05` | build:commit | only census/ is staged by the fixture commit (the .ufo/waves files never enter the tree) | `NO SUMMARY (rc=1)` / `NO SUMMARY (rc=1)` | CRASH: only census/ staged, prereg.txt is not committed; fixture commit fails; no SUMMARY, exit 1 on both artifacts (a false red) |
| `H06` | case_ok | the crash check is dropped from the per-case verdict | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, blind spot: crash check dropped from case_ok; no case crashes at BASE |
| `H07` | score_tool | the per-case result list is not returned (the counter reports a case count it never ran) | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR, equivalent by construction: len(results) is always len(CASES)+2 |
| `H08` | verdict | the met() gate stops requiring the second stub (control_findings) to be REJECTED | `unchanged (rc=0)` / `unchanged (rc=1)` | SURVIVOR alone, blind spot: control_findings REJECTED requirement only observable with an accepted stub |
| `S1` | STACK A08+C08+C10 | case-set check removed + patch leg counts a green selftest + patches==3 dropped from the verdict gate | `unchanged (rc=0)` / `pass=37 fail=0 patches=3/3 (rc=0)` | WRONG GREEN on the r41 tool: control rc=0 with cases=37 pass=37 patches=3/3 |
| `S2` | STACK A08+C08 | case-set check removed + patch leg counts a green selftest | `unchanged (rc=0)` / `pass=37 fail=0 patches=3/3 (rc=0)` | WRONG GREEN on the r41 tool: control rc=0 with cases=37 pass=37 patches=3/3 |
| `S3` | STACK A08+C10 | case-set check removed + patches==3 dropped from the verdict gate | `unchanged (rc=0)` / `pass=37 fail=0 (rc=0)` | WRONG GREEN on the r41 tool: control rc=0 with cases=37 pass=37 patches=0/3 (patches not required) |
| `S4` | STACK G01+G14 | one case deleted from the table + the verdict gate accepts any count >= 30 | `cases=36 pass=36 (rc=0)` / `cases=36 fail=12 (rc=1)` | WRONG GREEN on the landed tool: rc=0 with cases=36 pass=36 (the 37 pin is not in the gate) |

## Counts

- Single-point mutants: 60 (A 8, B 6, C 10, D 3, E 6, F 4, G 15, H 8). Stacks: 4.
- Mutants that change no SUMMARY field for either artifact (single-point): 28 — `C01`, `C02`, `C04`, `C05`, `C06`, `C09`, `C10`, `D01`, `D02`, `D03`, `E06`, `F02`, `F03`, `F04`, `G02`, `G07`, `G09`, `G10`, `G11`, `G14`, `G15`, `H01`, `H02`, `H03`, `H04`, `H06`, `H07`, `H08`.
  Of these, 8 are equivalent to the frozen counter and 20 are blind spots (see the verdict column).
- Single-point mutants that flip the landed tool red: 29. Of these, four crash the harness with no SUMMARY (`B06`, `F01`, `G12`, `H05`).
- Single-point mutants that flip the control to exit 0: 0.
- Mutants whose control SUMMARY reads `cases=37 pass=37` (the vacuity criterion as stated): `A08`, `S1`, `S2`, `S3`.


## Findings

### F1 — vacuity: the case set is not what the stub gate measures (A08, C08, S1–S3)

- **Attacks:** the stub-rejection gate (`stubs[label] = "REJECTED" if sp < sn`) and the `case_ok` expectation check.
- **A08** (`case_ok` keeps only `not crash and summ is not None`): the control reads `cases=37 pass=37 fail=0 … patches=0/3`. The verdict stays red only because the patches
  leg reads 0/3. Receipt `receipts/A08.control.txt`. This is the brief's example: a counter that reads `cases=37 pass=37` on the r41 tool.
- **S2** (`A08`+`C08`): control `cases=37 pass=37 … patches=3/3`, exit **0** on the r41 tool; the counter declares the r41 tool target-met. `S1` (`A08`+`C08`+`C10`) and
  `S3` (`A08`+`C10`) also give control exit 0. Receipts `receipts/S1.control.txt`, `S2.control.txt`, `S3.control.txt`.
- **C08** (any non-timeout patch exit counts as detected): the control reads `patches=3/3` with `pass=24`, exit 1. The always-green selftest is credited with three patches.
  Receipt `receipts/C08.control.txt`.
- **Stub gate under A08.** Probe `scripts/probe_stub.py` (receipt `receipts/stub-probe.txt`): at BASE the stubs score sp=4/37 (`control_clean`) and sp=0/37
  (`control_findings`). Under A08 they score sp=35/37 each; the two failing rows are the refusal rows. The stub's REJECTED label is carried by the refusal rows, not by the case table.
- **Probe W1/W2** (`scripts/probe_d03.py`; receipts `receipts/W1.landed.txt`, `W2.landed.txt`). Both are A08 with both refusal rows forced true, so both stubs score 37/37.
  W1 keeps the frozen stub rule `sp < sn`: `control_clean=ACCEPTED control_findings=ACCEPTED`, exit 1. W2 adds `D03` (`sp <= sn`): `control_clean=REJECTED control_findings=REJECTED`,
  exit **0** on the landed tool. A stub that passes every row is labelled REJECTED. W2 is four edits (A08, two refusal rows, D03): a stacked finding. Within it, A08 is visible
  in the control SUMMARY, the two refusal rows (`H01`, `F04`) and `D03` are single-point survivors.
- **Probe V3** (`A08`+`H01`+`F04`, `scripts/probe_vacuity.py`): control `cases=37 pass=37`, exit 1 (patches still 0/3). `V1` is `A08` again and `V2` is `S2`; their receipts are `receipts/V*_*.txt`.

### F2 — the case-count pin lives only in met() (G14, S4)

- `G01` (one case deleted) is caught by `n == 37` in `met()`. `G14` (`n >= 30`) alone survives, since n is always 37. `S4` (`G01`+`G14`) gives the landed tool
  `cases=36 pass=36` and exit **0**. The pin is not in `case_ok` or the table, so loosening the gate makes a dropped case green. Receipts `receipts/S4.landed.txt`, `G01.landed.txt`.

### F3 — tool_sha is outside the verdict (G13)

- `G13` (tool digest printed as `000000000000`) changes the SUMMARY on both artifacts and leaves the verdict unchanged. `tool_sha` is the only provenance field in the
  SUMMARY and `met()` does not read it, so a SUMMARY can name the wrong tool bytes and still meet the target. Receipts `receipts/G13.*.txt`.

### F4 — survivors: defects the case table does not detect

The 28 no-change mutants split into 8 equivalents (`C04`, `E06`, `G02`, `G07`, `G09`, `G11`, `G15`, `H07`) and 20 blind spots. The ones that matter for the wave:

- `H01`, `F03`, `F04`: refusal rows never observed failing; a tool that stops refusing an unresolved revision or an absent prereg is not distinguished from the landed one.
- `H02`: no case runs long enough to reach a 1-second timeout on this host; `run_tool` has no timeout handler, so a hung child is covered by no row.
- `C01`, `C02`, `C05`: the real, retro and selftest floors are one-sided; a tool that under-reports claims, under-finds on the pre-grammar prereg, or self-tests 5 cases passes.
- `G10`: the multiset is compared as a set; no case expects a duplicated identical finding, so a tool that double-reports a class is not seen.
- `D01`, `D02`: the stubs' claim count and finding class are never compared; a stub only has to fail, so its SUMMARY text is outside the stub gate.
- `H06`: the crash check is dropped from `case_ok`; no case crashes at BASE, so a crashing child with a matching exit code is not separated from a clean one.

### F5 — crashes read as red on both artifacts (B06, F01, G12, H05)

Four harness mutants crash `score_tool` (no SUMMARY, exit 1 on both artifacts). They are caught, but as a red verdict with no counter line to explain it; a counter crash
is indistinguishable from a target miss to the caller.

## Named limits for the L1 (proposed additions to the wave-2 list; nothing edited)

- **N-C2d** (F1) the case-set check and the patches leg do not carry the stub gate: under A08 the control's `cases=37 pass=37` is printed; under A08+C08 the r41 tool exits 0.
  The stub's REJECTED label rests on refusal rows and on `sp < sn`; W2 shows that `sp <= sn` turns two passing stubs into REJECTED.
- **N-C2e** (F2) the 37-case pin lives only in `met()`; a loosened gate plus one dropped case is green (S4).
- **N-C2f** (F3) `tool_sha` is printed but not part of the verdict.
- **N-C2g** (F4) twenty single-point survivors (table): refusal rows, timeout, the real/retro/selftest floors, the stub claim and class, and the crash check are not pinned by the table.
- **N-C2h** (F5) harness crashes produce the same exit code as a target miss and no SUMMARY.

## Integrity and what was not done

- The frozen counter, the landed tool, the control and every other tracked file were read only. No tracked file was written. The lane working tree was clean
  (`git status --porcelain` empty) when read. Git was used only as `clone`, `checkout` and `rev-parse`/`show` on a scratch clone.
- Mutants and probes ran in a clone of the lane at the tip, in `/fast/scratch/hyaku/souji-r42/R42w2mutationtester07/`. That clone and every fixture directory were deleted
  at the end of the seat. Evidence is in this seat directory (`mutants/`, `receipts/`, `scripts/`).
- No tool was installed or upgraded.
- Not run: the wave-2 held-out audit and any cross-seat comparison; the `score-candidate.sh` path. The seat scored through the counter's own `--tool` option against a clone,
  which is the same counter and the same tool bytes.

## Commands run (outputs in `receipts/`)

```
git clone --quiet --no-hardlinks /home/vgpnk/Projects/shokunin/souji-shokunin clone-tip      # scratch only
git -C clone-tip checkout --quiet 3105a63b23481fccf7df58e74d14a6681e0ea0c8
python3 -B …/census/round-42/c2-counter.py --root clone-tip --rev 3105a63… --scratch <scratch>                 # pristine landed: 37/37
python3 -B …/census/round-42/c2-counter.py --root clone-tip --rev 3105a63… --tool census/round-42/controls/c2-stub-tool.py --scratch <scratch>   # pristine control: 24/37
python3 -B scripts/driver.py     # 37 mutants (A-F) x 2 artifacts + BASE           -> receipts/results.json
python3 -B scripts/driver_g.py   # 15 G singles + 4 stacks x 2 artifacts           -> receipts/results-g.json
python3 -B scripts/driver_h.py   # 8 H singles x 2 artifacts                       -> receipts/results-h.json
python3 -B scripts/analyse_all.py                                                   # SUMMARY diffs, no-change set, exit codes
python3 -B scripts/mktables.py   > receipts/tables-from-mktables.md
python3 -B scripts/probe_stub.py > receipts/stub-probe.txt
python3 -B scripts/probe_vacuity.py                                                 # V1 V2 V3 receipts
python3 -B scripts/probe_d03.py                                                     # W1 W2 receipts
python3 -B scripts/make_report.py                                                   # writes this file from the receipts
sha256sum census/round-42/c2-counter.py   # fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1 (unchanged)
```

The scripts were run from the scratch directory and copied unchanged into `scripts/`.
