### TABLE 1 — single-point counter mutants

| `A01` | CASES | dup-target expectation class KEY-DUPLICATE -> FIELD-MISSING (expectation no longer the r42 class) | pass=36 fail=1 / (unchanged) | FALSE RED on the landed tool |
| `A02` | CASES | heading-valid-tail expects 6 FIELD-MISSING -> 5 | pass=36 fail=1 / pass=23 fail=14 | FALSE RED on the landed tool |
| `A03` | CASES | population-empty expectation POPULATION-EMPTY -> POPULATION-DIGEST | pass=36 fail=1 / pass=23 fail=14 | FALSE RED on the landed tool |
| `A04` | CASES | counter-symlink expectation COUNTER-SYMLINK -> COUNTER-DIGEST (the r41 tool's actual class: weakens the control's rejection, reddens the landed tool) | pass=36 fail=1 / pass=25 fail=12 | FALSE RED on the landed tool |
| `A05` | CASES | population-symlink expectation POPULATION-SYMLINK -> POPULATION-DIGEST (r41 emits the pair DIGEST+EMPTY, so the stub still fails but for a different reason) | pass=36 fail=1 / (unchanged) | FALSE RED on the landed tool |
| `A06` | CASES | dispatch-spec-before claim label C0 -> C1 (prereg-wide label no longer prereg-wide) | pass=36 fail=1 / (unchanged) | FALSE RED on the landed tool |
| `A07` | CASES | clean case expects no finding -> expects NO-CLAIMS | pass=36 fail=1 / pass=23 fail=14 | FALSE RED on the landed tool |
| `A08` | CASES | case_ok drops the want_rc / want-class comparison entirely (counter accepts any non-crashing tool that prints a SUMMARY: vacuity) | (unchanged) / pass=37 fail=0 | correct |
| `B01` | build | the duplicated key is never written (dup fixture becomes a clean prereg) | pass=34 fail=3 / (unchanged) | FALSE RED on the landed tool |
| `B02` | build | base_side fixture points Base at the main tip (BASE-NOT-ANCESTOR can no longer occur) | pass=36 fail=1 / pass=23 fail=14 | FALSE RED on the landed tool |
| `B03` | build | dispatch_before fixture writes a name the dispatch rule does not match (w1-notes.json) | pass=36 fail=1 / pass=23 fail=14 | FALSE RED on the landed tool |
| `B04` | build | the counter symlink is replaced by a regular file copy (the symlink case becomes a clean counter) | pass=36 fail=1 / (unchanged) | FALSE RED on the landed tool |
| `B05` | build | the prereg tail is never appended (the four malformed-heading fixtures lose their heading) | pass=32 fail=5 / pass=23 fail=14 | FALSE RED on the landed tool |
| `B06` | build | the post-freeze counter edit is a no-op rewrite of identical bytes (FROZEN-EDITED fixture becomes clean) | NO SUMMARY (counter crashed) / NO SUMMARY (counter crashed) | COUNTER CRASHED (no SUMMARY; exit 1/1) |
| `C01` | leg:real | real leg drops the claims=3 requirement (only 'no findings' is left) | (unchanged) / (unchanged) | correct |
| `C02` | leg:retro | retro leg accepts >=1 finding instead of >=3 | (unchanged) / (unchanged) | correct |
| `C03` | leg:retro | retro leg demands exit 0 instead of exit 1 | retro=FAIL / retro=FAIL | FALSE RED on the landed tool |
| `C04` | leg:retro_clean | retro_clean leg drops the no-findings requirement | (unchanged) / (unchanged) | correct |
| `C05` | leg:selftest | selftest leg accepts >=1 self-test case instead of >=12 | (unchanged) / (unchanged) | correct |
| `C06` | leg:selftest | selftest leg drops pass==cases | (unchanged) / (unchanged) | correct |
| `C07` | leg:patches | only patch P1 is injected (patches=1/3) | patches=1/3 / (unchanged) | FALSE RED on the landed tool |
| `C08` | leg:patches | a patch counts as detected unless it timed out (an always-green selftest now counts 3/3: the control's patches leg is vacuous) | (unchanged) / patches=3/3 | correct |
| `C09` | verdict | the met() gate drops the requirement that the built-in clean stub is REJECTED | (unchanged) / (unchanged) | correct |
| `C10` | verdict | the met() gate drops the patches==3 requirement | (unchanged) / (unchanged) | correct |
| `D01` | stubs | STUB_CLEAN announces claims=0 instead of claims=1 | (unchanged) / (unchanged) | correct |
| `D02` | stubs | STUB_FINDINGS emits FIELD-MISSING instead of NO-CLAIMS | (unchanged) / (unchanged) | correct |
| `D03` | stubs | a stub that passes every case is still labelled REJECTED (sp <= sn): the stub-rejection gate is vacuous | (unchanged) / (unchanged) | correct |
| `E01` | SITECUSTOMIZE | P1 no longer reverses the digest (the patch is inert: the tool's own digest logic is not exercised) | patches=2/3 / (unchanged) | FALSE RED on the landed tool |
| `E02` | SITECUSTOMIZE | P2 matches a diff-filter the tool never uses (the patch is inert) | patches=2/3 / (unchanged) | FALSE RED on the landed tool |
| `E03` | SITECUSTOMIZE | P3 matches a git subcommand the tool never runs (the patch is inert) | patches=2/3 / (unchanged) | FALSE RED on the landed tool |
| `E04` | SITECUSTOMIZE | PYTHONPATH is emptied, so sitecustomize never loads (no patch reaches the tool) | patches=0/3 / (unchanged) | FALSE RED on the landed tool |
| `E05` | SITECUSTOMIZE | the patch id is passed under a different env name than sitecustomize reads (the two halves of the patch mechanism are coupled by a literal) | patches=0/3 / (unchanged) | FALSE RED on the landed tool |
| `E06` | SITECUSTOMIZE | the patch id default is P1 instead of empty (dead branch: sitecustomize is only on PYTHONPATH when a patch is requested) | (unchanged) / (unchanged) | correct |
| `F01` | run_tool | the FINDING regex captures only the claim label, never the class (the class multiset is never compared) | NO SUMMARY (counter crashed) / NO SUMMARY (counter crashed) | COUNTER CRASHED (no SUMMARY; exit 1/1) |
| `F02` | run_tool | the SUMMARY regex loses its anchors (a second SUMMARY line anywhere would be read) | (unchanged) / (unchanged) | correct |
| `F03` | refusal | the unresolved-revision refusal check drops the no-crash requirement | (unchanged) / (unchanged) | correct |
| `F04` | refusal | the absent-prereg refusal check drops the no-crash requirement | (unchanged) / (unchanged) | correct |
| `G01` | CASES | one case is deleted from the table (the counter's own case count drops below the target) | cases=36 pass=36 / cases=36 fail=12 | FALSE RED on the landed tool |
| `G02` | CASES | the PRISTINE FAIL case count is off by one (dead path while the tool is present) | (unchanged) / (unchanged) | correct |
| `G03` | leg:retro | the retro leg reads the r41 preregistration instead of the r40 one | retro=FAIL / retro=FAIL | FALSE RED on the landed tool |
| `G04` | leg:retro_clean | the retro_clean leg reads the r40 preregistration instead of the r41 one | retro_clean=FAIL / retro_clean=FAIL | FALSE RED on the landed tool |
| `G05` | leg:real | the real leg reads the r40 preregistration instead of this round's | real=FAIL / real=FAIL | FALSE RED on the landed tool |
| `G06` | build:prereg_text | the emitted claim block omits the Kill key (every fixture claim is short one key) | pass=3 fail=34 / pass=3 fail=34 | FALSE RED on the landed tool |
| `G07` | build:prereg_text | the emitted heading loses its em dash (the tool's heading grammar still accepts it) | (unchanged) / (unchanged) | correct |
| `G08` | build:prereg_text | the emitted heading becomes a level-3 heading (no claim block is opened at all) | pass=4 fail=33 / pass=4 fail=33 | FALSE RED on the landed tool |
| `G09` | case_ok | the summary findings count check is weakened to a tautology (the class multiset check is the only one left) | (unchanged) / (unchanged) | correct |
| `G10` | case_ok | the class multiset comparison becomes a set comparison (duplicate identical findings are forgiven) | (unchanged) / (unchanged) | correct |
| `G11` | build | the duplicated key always carries the identical value (the 'differs' variant is never built) | (unchanged) / (unchanged) | correct |
| `G12` | build | the fixture git identity is removed (the fixture commit cannot be made) | NO SUMMARY (counter crashed) / NO SUMMARY (counter crashed) | COUNTER CRASHED (no SUMMARY; exit 1/1) |
| `G13` | tool_sha | the tool digest printed in SUMMARY is a constant instead of the scored bytes' digest | tool_sha=000000000000 / tool_sha=000000000000 | correct |
| `G14` | verdict | the met() gate accepts any case count at or above 30 (the 37-case table is not pinned) | (unchanged) / (unchanged) | correct |
| `G15` | run_tool | the crash detector is narrowed to the word Traceback anywhere in stderr | (unchanged) / (unchanged) | correct |
| `H01` | refusal | the unresolved-revision refusal check is made trivially true (the stub-rejection label is then carried by nothing else) | (unchanged) / (unchanged) | correct |
| `H02` | run_tool | the per-case tool timeout is 1 second (the TimeoutExpired is not handled in run_tool) | (unchanged) / (unchanged) | correct |
| `H03` | git helper | a failed git call no longer raises (a broken fixture is silently scored) | (unchanged) / (unchanged) | correct |
| `H04` | build | the fixture-root assertion (git rev-parse --show-toplevel == the fixture dir) is dropped | (unchanged) / (unchanged) | correct |
| `H05` | build:commit | only census/ is staged by the fixture commit (the .ufo/waves files never enter the tree) | NO SUMMARY (counter crashed) / NO SUMMARY (counter crashed) | COUNTER CRASHED (no SUMMARY; exit 1/1) |
| `H06` | case_ok | the crash check is dropped from the per-case verdict | (unchanged) / (unchanged) | correct |
| `H07` | score_tool | the per-case result list is not returned (the counter reports a case count it never ran) | (unchanged) / (unchanged) | correct |
| `H08` | verdict | the met() gate stops requiring the second stub (control_findings) to be REJECTED | (unchanged) / (unchanged) | correct |

### TABLE 2 — stacked mutants (two or three single-point changes together)

| `S1` | STACK A08+C08+C10 | case-set check removed + patch leg counts a green selftest + patches==3 dropped from the verdict gate | (unchanged) / pass=37 fail=0 patches=3/3 | FALSE GREEN on the r41 control (vacuity) |
| `S2` | STACK A08+C08 | case-set check removed + patch leg counts a green selftest | (unchanged) / pass=37 fail=0 patches=3/3 | FALSE GREEN on the r41 control (vacuity) |
| `S3` | STACK A08+C10 | case-set check removed + patches==3 dropped from the verdict gate | (unchanged) / pass=37 fail=0 | FALSE GREEN on the r41 control (vacuity) |
| `S4` | STACK G01+G14 | one case deleted from the table + the verdict gate accepts any count >= 30 | cases=36 pass=36 / cases=36 fail=12 | correct |

### no-SUMMARY-change set (verbatim SUMMARY, both artifacts)

`C01`, `C02`, `C04`, `C05`, `C06`, `C09`, `C10`, `D01`, `D02`, `D03`, `E06`, `F02`, `F03`, `F04`, `G02`, `G07`, `G09`, `G10`, `G11`, `G14`, `G15`, `H01`, `H02`, `H03`, `H04`, `H06`, `H07`, `H08`
count: 28

### landed-only-identical set

`A08`, `C01`, `C02`, `C04`, `C05`, `C06`, `C08`, `C09`, `C10`, `D01`, `D02`, `D03`, `E06`, `F02`, `F03`, `F04`, `G02`, `G07`, `G09`, `G10`, `G11`, `G14`, `G15`, `H01`, `H02`, `H03`, `H04`, `H06`, `H07`, `H08` count: 30

### control-only-identical set

`A01`, `A05`, `A06`, `B01`, `B04`, `C01`, `C02`, `C04`, `C05`, `C06`, `C07`, `C09`, `C10`, `D01`, `D02`, `D03`, `E01`, `E02`, `E03`, `E04`, `E05`, `E06`, `F02`, `F03`, `F04`, `G02`, `G07`, `G09`, `G10`, `G11`, `G14`, `G15`, `H01`, `H02`, `H03`, `H04`, `H06`, `H07`, `H08` count: 39
