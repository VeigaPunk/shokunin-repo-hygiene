# R40w2critic07 — attack on the r40 C3 fixture's expectations (`tests/fixtures/r40-drift-record-branches.py`)

Seat: R40w2critic07 (critic, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Landed revisions: instrument commit 128e412b0ced3c243dc27c3dd3332054a611bc2e; HEAD 556c24a5cacf208c5144c459838712594a43e1f2 (fixture and tool bytes at HEAD equal the working tree; `git status` showed no change to them). Base: 0242085909fb6a4ee041c5443d76316ac6d59d4b.
Scratch: /fast/scratch/hyaku/souji-r40/w2/R40w2critic07/ (removed at the end; see last section).
Installs: none. No pacman. No lane file was written; the only lane write is this report.

## Axes attacked

1. Each of the eight cases vs the pristine tool: does the expectation match the behaviour the tool has, and is that behaviour specified anywhere?
2. Does the fixture kill the mutants the C3 counter declares (M15-M18) and the mutants the counter does not declare that sit on the same branches?
3. Does the fixture report its own failure summary when a mutant changes the output encoding?

Files attacked: `tests/fixtures/r40-drift-record-branches.py` (cases at :100-120, `run_record` :72-91, `subprocess.run(... text=True)` at :85), `tools/souji-worktree-drift.py` (decode :147, record parse :152-179, ROW/TOTAL regex :87-88, ABSENT :355-356, skip guard :370, docstring RECORD-MALFORMED list :33-61), `census/round-40/c3-counter.py` (score() :96-120, MUTANTS :61-69), `corpus/knowledge/drift-record-invalid-utf8-r40.md`.

## Commands and real output

### 0. Identity of attacked bytes
```
$ git -C .../souji-shokunin show HEAD:tools/souji-worktree-drift.py > $S/pristine.py && cmp $S/pristine.py tools/souji-worktree-drift.py && echo "tool==HEAD"
tool==HEAD
$ git show HEAD:tests/fixtures/r40-drift-record-branches.py | cmp - tests/fixtures/r40-drift-record-branches.py && echo "fixture==HEAD"
fixture==HEAD
```

### 1. The eight cases against the pristine tool
```
$ python3 -B $S/r40fix.py --tool $S/pristine.py --work $S/pw; echo "rc=$?"
case-good=PASS
case-total-duplicate-identical=PASS
case-total-conflicting-second=PASS
case-total-repos-disagrees=PASS
case-skip-unrecorded-suppresses=PASS
case-unrecorded-without-flag=PASS
case-invalid-utf8-in-repo-name=PASS
case-invalid-utf8-in-comment=PASS
SUMMARY cases=8 pass=8 fail=0
rc=0
```
Every expectation matches the pristine tool. The question is what each expectation rests on (section 3).

### 2. The C3 counter, as landed (read-only; scratch via --scratch)
```
$ python3 -B census/round-40/c3-counter.py --root $L --rev 556c24a5cacf208c5144c459838712594a43e1f2 --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S/c3
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
rc=0
```
The four declared mutants are killed and the r39 base fixture kills none of them. This part of the C3 predicate holds.

### 3. Extra mutants of the same branches (mine, built in scratch from the pristine bytes by exact-anchor replacement)
Scored with the counter's own `score()` (imported from a scratch copy of the landed counter) against the candidate fixture and the r39 base fixture:
```
$ python3 -B $S/score.py
M15_first_total.py                 r40-killed=True  | r39-base-killed=False
M16_always_scan.py                 r40-killed=True  | r39-base-killed=False
M17_ignore.py                      r40-killed=True  | r39-base-killed=False
M18_no_repos_check.py              r40-killed=True  | r39-base-killed=False
P1_refuse_any_disagreeing_total.py r40-killed=False [rc=0 fails=0 crash=False failing=-] | r39-base-killed=False
P2_backslashreplace.py             r40-killed=False [rc=0 fails=0 crash=False failing=-] | r39-base-killed=False
P3_surrogateescape.py              r40-killed=False [NO-SUMMARY rc=1] | r39-base-killed=False
P4_strict_refuse.py                r40-killed=True  [rc=1 fails=2 failing=invalid-utf8-in-repo-name,invalid-utf8-in-comment] | r39-base-killed=False
P5_single_total.py                 r40-killed=True  [rc=1 fails=1 failing=total-duplicate-identical] | r39-base-killed=False
```
P1 = refuse any TOTAL that disagrees with an earlier TOTAL. P2 = `decode("utf-8","backslashreplace")`. P3 = `decode("utf-8","surrogateescape")`. P4 = strict UTF-8, refused as RECORD-MALFORMED. P5 = exactly one TOTAL row allowed.

### 4. Probe of the tool on the multiple-TOTAL and invalid-byte records
`python3 -B $S/probe.py <tool>` (records written under $S/probe-root; `--skip-unrecorded` passed):
```
== tool pristine.py
P-first-conflict-then-agree rc=0 'SUMMARY ... record_repos=2 ... drift_rows=0 unreachable=0\n'
P-agree-then-conflict rc=2 'REFUSAL RECORD-MALFORMED: TOTAL repos=1 but 2 REPO rows\n'
P-utf8-name rc=1 'DRIFT\tABSENT\tal�pha\trecorded regs=1\nSUMMARY ...'
== tool P2_backslashreplace.py
P-utf8-name rc=1 'DRIFT\tABSENT\tal\\xffpha\trecorded regs=1\nSUMMARY ...'
== tool P1_refuse_any_disagreeing_total.py
P-first-conflict-then-agree rc=2 'REFUSAL RECORD-MALFORMED: line 4 TOTAL disagrees with an earlier TOTAL\n'
== tool P4_strict_refuse.py
P-utf8-name rc=2 'REFUSAL RECORD-MALFORMED: ... P-utf8-name.tsv is not valid UTF-8\n'
```

### 5. P3 crash (the fixture cannot report it)
`python3 -B r40fix.py --tool P3 ...` exits 1 with a traceback on stderr:
```
File ".../r40fix.py", line 150, in <module>
File ".../r40fix.py", line 140, in main
File ".../r40fix.py", line 114, in run_cases        # the invalid-utf8-in-repo-name call
File ".../r40fix.py", line 85, in run_record        # subprocess.run(..., text=True)
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 15
```
No `SUMMARY cases=` line is printed, so `score()` (census/round-40/c3-counter.py:109-110) returns NO-SUMMARY and the mutant is scored `killed=no` (:118 requires the fixture's own summary), although the fixture did detect a change (rc 1 from the tool's output, case 7 never reached its verdict).

## Per-case verdict (fixture expectation vs tool behaviour)

| case (fixture line) | expectation | pristine | what the expectation rests on | status |
|---|---|---|---|---|
| good (:100-101) | rc 0, record_repos=2 | matches | tool :370 skip, normal summary | SAFE |
| total-duplicate-identical (:102-103) | rc 0 (duplicate identical TOTAL accepted) | matches | last-wins with no duplicate check (tool :169-178). Not stated in the tool contract (docstring :33-61 lists TOTAL only as "a TOTAL row that disagrees"). P5 (one TOTAL allowed) fails it. | pinned implementation behaviour, not a documented contract |
| total-conflicting-second (:104-106) | rc 2, RECORD-MALFORMED | matches | refused only because the LAST TOTAL is the conflicting one (:171). | SAFE for what it asserts; the mechanism is order-dependent (see gap below) |
| total-repos-disagrees (:107-109) | rc 2, RECORD-MALFORMED | matches | tool :170-171 | SAFE; killed M18 |
| skip-unrecorded-suppresses (:110-111) | rc 0, SUMMARY | matches | tool :370 | SAFE; token check is weak (SUMMARY only), rc carries the claim |
| unrecorded-without-flag (:112-113) | rc 1, UNRECORDED | matches | tool :370-383 | SAFE |
| invalid-utf8-in-repo-name (:114-116) | rc 1, ABSENT | matches | decode `replace` (tool :147) yields U+FFFD; ABSENT (:355-356). The expectation asserts neither the U+FFFD name nor the handler. P2 (backslashreplace) passes it; P4 (strict refusal) fails it. | expectation depends on the decode choice; under-asserted |
| invalid-utf8-in-comment (:117-120) | rc 0, record_repos=2 | matches | comment skip (tool :153) after `replace`. P4 fails it. | pinned tolerance of invalid bytes; no documented contract states it (see knowledge entry limits) |

Specific findings:

- **F1 — first conflicting TOTAL accepted (tool contract violated, not covered by any case).** Probe: a record with `TOTAL repos=1 regs=1 prunable=0` followed by `TOTAL repos=2 regs=2 prunable=0` gets rc 0 and `drift_rows=0` from the pristine tool. The tool docstring (:47-48) says a TOTAL row that disagrees is RECORD-MALFORMED. The mirror order (agree then conflict) is refused (rc 2). The fixture only has the second-conflicting arm (:104-106), so the order dependence is invisible to it. P1 (refuse any disagreeing TOTAL pair) survives both the r40 and r39 fixtures. Kill condition for C3's "multiple TOTAL rows" branch: not met by the landed fixture.
- **F2 — the documented U+FFFD outcome is not asserted (P2 survives).** The docstring (:12-14), the knowledge entry, and the case name say the byte becomes U+FFFD. Case 7 asserts only rc 1 and the token `ABSENT`. P2 (`backslashreplace`) reports `al\xffpha` and still passes; the output differs (`al�pha` vs `al\xffpha`). The C3 counter's M17 (`ignore`) is the only decode mutant it declares.
- **F3 — cases 2, 7, 8 pin the implementation, not a stated contract (P4, P5 fail them).** A tool that refuses invalid UTF-8 as RECORD-MALFORMED (P4, verified rc 2 on the probe record) fails cases 7 and 8. A tool that allows one TOTAL row (P5) fails case 2. Neither contract appears in the tool's docstring (:33-61) or in the knowledge entry's Claim/Limits sections, which describe the `replace` handler as observed behaviour. So the expectation is the pristine behaviour, not a verified requirement. This is a risk for a future correct tool; the verdict is INCONCLUSIVE on whether tolerance is intended.
- **F4 — fixture harness cannot report on non-UTF-8 tool output (P3).** `run_record` runs the tool with `text=True` (fixture :85), so any tool output containing a raw invalid byte raises inside the fixture (traceback at :85 via :114) and no `SUMMARY cases=` line is printed. The counter's `score()` then scores a detected mutant as `killed=no` (NO-SUMMARY). This breaks the C3 predicate "fixture must have its own failure summary" for that mutant class.

## Verdict

**FALSIFIED** (scope: the eight case expectations as a C3 coverage predicate).

- The expectations match the pristine tool: all eight PASS (section 1). Four declared mutants are killed and the r39 base kills none (section 2). Those parts are SAFE.
- Falsifiers: F1 (`TOTAL` order dependence, P1 survives, pristine rc 0 on a disagreeing TOTAL), F2 (U+FFFD outcome unasserted, P2 survives), F4 (P3 fixture crash scored as survived). Command evidence: section 3, section 4 probe, section 5.
- Expectations that would fail a stricter but defensible tool: cases 2, 7, 8 (P4, P5). Whether tolerance/duplicates are intended is not documented, so that part is INCONCLUSIVE.

## Not done / limits
- Only the eight cases and the TOTAL/UTF-8/skip branches were attacked; the r39 base fixture was run only as a control (base_killed=no for every mutant).
- P1-P5 are my scratch mutants, not declared by the counter; the counter's MUTANTS list was not edited (it is frozen).
- No lane file other than this report was written. Untracked files `census/round-40/records/c{1,2,3}-after-d.txt` in the lane were already present and belong to other seats; they were not touched.

## Scratch
Scratch directory /fast/scratch/hyaku/souji-r40/w2/R40w2critic07 removed at the end of the seat (command and result recorded in the final yield).
