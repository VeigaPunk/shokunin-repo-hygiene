# R42mutationtester02 — mutation report on the frozen C2 counter (souji round 42, wave 1)

Seat: R42mutationtester02 (mutation-tester, leaf, no subagents). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Freeze commit afe17f416eec04dcf3f480b580a8f928de61d19d (base bf618f6c5c09d302994871c94903abbea2deb60d). Instruments commit b7408095543579ac71b33ecf7b80b0cb8ef45036.

## Verdict

Operability: the frozen counter `census/round-42/c2-counter.py` runs deterministically under every mutant and gives the predicted baseline on both scored tools (fail=13 split). Of 103 single-point mutants of CASES, build(), the case and leg functions and main(), 56 are killed (53 by the scored invocations on the base tool and the stub, 3 only by invocations outside the scored harness), 17 are equivalent, and 30 survive. The 30 survivors are named limits NL-* below: each is a field, branch or check the counter does not read, so a tool exhibiting that defect would not be reported by this counter. No frozen file was edited; no candidate was written; nothing was committed or landed.

Survivor count: **30** named-limit survivors (17 equivalent mutants are not counted). Under the scored invocations alone 33 survive, 3 of which are killed by the out-of-harness probes.

## Frozen inputs (checked at the freeze commit)

- `census/round-42/c2-counter.py` at afe17f4: sha256 `fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1` (matches preregistration). Copy used for mutation: `.ufo/waves/round-42/w1/R42mutationtester02/c2-counter.py` (same sha).
- `census/round-42/c2-cases.tsv` at afe17f4: sha256 `148b7b87411eb282e0207cf5471d55be81e03d4a26ffafd96df37b4db4fd4511` (matches).
- Base tool `tools/souji-freeze-check.py` at afe17f4 (identical blob at bf618f6 and b7408095): sha256 `8131847bcfc5ecef513eb608a67ec18feab44f7a8b6c094824b082ffe52a76e2`.
- Stub `census/round-42/controls/c2-stub-tool.py` at afe17f4: sha256 `6e1c564a94b58e5106118ef73cbcea7abe5f60935f69792eba6f490c9ca66a01` (the r41 checker with an always-green `--selftest`, `_stub_selftest` prints `SELFTEST cases=12 pass=12 fail=0`).

## Method

1. Scratch clone `git clone -q --shared` of the lane into `/fast/scratch/hyaku/souji-r42/R42mutationtester02/clone` (HEAD afe17f4); `git -C CLONE rev-parse --show-toplevel` printed the clone path. The lane was only read (log, cat-file, show, ls-tree).
2. Each of the 103 mutants (`mutants/M01.py`..`M103.py`, manifest with sha256-16 in `mutants/manifest.tsv`) was made by one exact `str.replace` of a string that occurs exactly once in the frozen counter (`mutate.py`; all compile).
3. Each mutant ran twice: `python3 -B MUT.py --root CLONE --rev afe17f4 --scratch RUN --tool <tool>` with `<tool>` = the base tool path and the stub path (`run.sh`). Baselines: the unmutated counter on the same two tools.
4. Killed = any difference in the printed output or exit code against the baseline on at least one tool. Verdict kill = exit code, SUMMARY field, a case PASS/FAIL flip, a real/retro/retro_clean/selftest status, or no SUMMARY (traceback). Text-only kill = a case detail, a SUMMARY text field (tool_sha) or the suppressed case lines, with verdicts unchanged.
5. Probes (`probes.sh`): invocations the scored harness never makes (default `--tool`, a 7-char `--rev`, an absent `--tool`, a missing `--scratch`), run for the original and for the three mutants that scored runs did not kill.

## Baseline receipts (unmutated counter)

Base tool (`receipts/out/base-base.out`):
```
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=19 summary=(3, 19)
retro_clean ok rc=0 findings=0 summary=(3, 0)
selftest FAIL rc=2 summary=None
SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=FAIL patches=0/3 tool_sha=8131847bcfc5
```
Stub (`receipts/out/base-stub.out`):
```
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=19 summary=(3, 19)
retro_clean ok rc=0 findings=0 summary=(3, 0)
selftest ok rc=0 summary=(12, 12, 0)
SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=0/3 tool_sha=6e1c564a94b5
```
Both tools: `pass=24 fail=13`, the 13 red cases being dup-base-differs, dup-counter-identical, dup-target, heading-nospace, heading-lowercase, heading-spaced-digit, heading-suffix, dispatch-spec-before, dispatch-attempts-before, dispatch-dispatched-before, dispatch-results-before, counter-symlink, population-symlink. This matches the preregistration's stated split. `selftest=FAIL` on base (no `--selftest`), `selftest=ok` on the stub, `patches=0/3` on both.

## Commands run and their output

- `git -C LANE log -3 --format='%H %s'` → `afe17f416eec...` (freeze), `b7408095...`, `410316c9...`.
- `git -C LANE show <rev>:tools/souji-freeze-check.py | sha256sum` at bf618f6 and b7408095 → both `8131847b...`.
- `git clone -q --shared LANE CLONE` → clone root check OK.
- `run.sh` with the unmutated counter on both tools (`base-base`, `base-stub`): 4.9 s wall, run in parallel; outputs above.
- `python3 -B mutate.py` → `mutants 103`, every `old` string `count==1`, every mutant `py_compile`d.
- `run.sh` over 103 mutants × 2 tools = 206 runs (xargs -P 4). All 206 `.rc` files present and non-empty (checked).
- `python3 -B analyze.py` → `TOTAL 103 verdict-killed 47 text-only 6 survived 50` (raw first classification: it counts the M94 tool_sha field and the M97 suppressed case lines as verdict changes; `gen_report.py` reclassifies both as text-only and marks M99/M100/M102 as probe-only).
- `python3 -B gen_report.py` → counts killed-verdict 45, killed-text 8, probe-only 3, equivalent 17, named-limit survivors 30 (103 total). Table below.
- `bash probes.sh` → `PROBES_DONE`:
- `orig-default-tool`: exit 1; stdout last line: `SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=FAIL patches=0/3 tool_sha=`; stderr last line: ``
- `M102-default-tool`: exit 1; stdout last line: `SUMMARY cases=37 pass=0 fail=37 control_clean=n/a control_findings=n/a real=FAIL retro=FAIL retro_clean=FAIL selftest=FAIL patches=0/3 tool_sha=absent`; stderr last line: ``
- `orig-shortrev`: exit 2; stdout last line: ``; stderr last line: `REFUSAL COULD-NOT-EVALUATE: --rev must name a resolvable full40 commit`
- `M100-shortrev`: exit 1; stdout last line: `SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL retro_clean=FAIL selftest=FAIL patches=0/3 tool`; stderr last line: ``
- `orig-absent-tool`: exit 1; stdout last line: `SUMMARY cases=37 pass=0 fail=37 control_clean=n/a control_findings=n/a real=FAIL retro=FAIL retro_clean=FAIL selftest=FAIL patches=0/3 tool_sha=absent`; stderr last line: ``
- `M98-absent-tool`: exit 1; stdout last line: `SUMMARY cases=37 pass=0 fail=37 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL retro_clean=FAIL selftest=FAIL patches=0/3 tool_`; stderr last line: ``
- `orig-badscratch`: exit 2; stdout last line: ``; stderr last line: `REFUSAL COULD-NOT-EVALUATE: --scratch (or TMPDIR) must name a directory`
- `M99-badscratch`: exit 1; stdout last line: ``; stderr last line: `FileNotFoundError: [Errno 2] No such file or directory: '/fast/scratch/hyaku/souji-r42/R42mutationtester02/no-such-dir/souji-r42-c2.7k2otmgo'`
- Default-invocation check: `receipts/out/probe-orig-default-tool.out` is byte-identical to `base-base.out` (`cmp` returned 0).

## Survivor classes (named limits)

Each NL is a survivor of the scored invocations on the base tool and the stub, with the code evidence the counter contains. None is proposed as an edit to the frozen counter (per the seat rules); they are routed to the L1 as named limits.

- NL-SPACING (M09, M10, M13): the counter never builds a `Key:value` line without a space, a blank line inside a claim block, or a double space before `sha256=`. The tool accepts all three (`KEYLINE` uses `[ \t]*`; `PATH_SHA` uses `[ \t]+`). No scored case pins the grammar.
- NL-VALUE (M14): the `Target:` value is written but never read by the tool or compared with the counter's output.
- NL-RECEIPT (M32): the green control receipt's `corrected=` count is written but the tool reads only the last `EXIT=` line.
- NL-FIELDNAME (M19, M38): `run_tool` keeps only `(claim, class)` (`re.finditer(r"^FINDING (\S+) (\S+)")`) and `case_ok` compares classes, so a FIELD-MISSING for the wrong key passes every FIELD-MISSING case.
- NL-BASERED (M24, M34, M47, M48): the dispatch-*-before fixtures and the symlink fixtures are red on both scored tools with identical printed detail; a fixture change inside them (wave path, file name, link target) is invisible to scored tools. M48 (negative fixture renamed to a dispatch-pattern name) is detectable only by a tool implementing the widened name rule.
- NL-MULTISET (M56): `got == sorted(want)` replaced by a set comparison survives: both tools produce the exact multiplicities (six C2 FIELD-MISSING in heading-valid-tail), so no scored case decides on multiplicity.
- NL-SUMCOUNT (M57): `summ[1] == len(want)` is never cross-checked against the FINDING lines; no scored tool prints an inconsistent SUMMARY count.
- NL-CRASH (M58): the traceback guard is never triggered; neither scored tool emits a traceback.
- NL-REFUSAL-RC (M61): the unresolved-rev check accepts rc 1 as well as rc 2; both scored tools return 2 and no scored tool returns 1.
- NL-SELFTEST (M70, M71): the `fail == 0` condition and the rc-0-or-1 acceptance are never exercised (the stub reports `fail=0` and exits 0; the base has no selftest).
- NL-PATCHLEG (M74, M75, M76, M77, M78): the P2/P3 injection targets, the P1 digest reversal, the PYTHONPATH and the selector are all invisible to the scored tools: base gates `patches` on a selftest that does not exist, and the always-green stub exits 0 under every patch, so both give `patches=0/3` regardless. Only a tool with a real, sensitive `--selftest` can expose these.
- NL-REAL (M79, M83): the real leg checks only the claims count, and the round-41 preregistration is also clean on both tools, so pointing the real leg at it is not observed.
- NL-STUB (M84, M85, M86): the STUB_CLEAN/STUB_FINDINGS text and exit codes are never printed; the control verdict is only a pass count.
- NL-ACCEPTED (M87): the `ACCEPTED` branch of the stub verdict requires a tool that passes all 37 cases; neither scored tool does.
- NL-MET (M89, M90): the exit code is an AND over nine conjuncts; each scored tool fails at least two of them, so dropping one leaves exit 1.

Equivalent (17): M02, M06, M08, M16, M17, M27, M29, M33, M37, M39, M65, M66, M67, M95, M96, M101, M103. Each is a change that the counter's inputs or the tool's documented grammar cannot distinguish (for example M29: KEY-DUPLICATE is value-independent by the docstring; M95/M96: both stubs are REJECTED, so the label or argument swap yields the same tokens).

Probe-only kills (3): M99, M100, M102. Each mutant is invisible to the scored runs because the scored runs pass a valid 40-hex `--rev`, an existing `--scratch`, and an explicit `--tool`. The probes show the frozen counter refuses (rc 2) where the mutant does not. Note that `score-candidate.sh` runs the counter without `--tool`, so the default path (M102) is exercised by the real scorer but not by the scored harness here.

## Table

Columns: mutant id, change, killed?, the printed field that changed (union over both tools), notes. Killed by scored runs unless marked probe. `YES (text only)` means the verdicts did not change.

| mutant id | change | killed? | which printed field changed | notes |
|---|---|---|---|---|
| M01 | sha256 -> sha1 in digest helper | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x21 (case-clean); case detail x13 (case-dup-base-differs) | digest algorithm change breaks every digest-bearing claim (40-hex digest fails grammar) |
| M02 | digest encoding utf-8 -> ascii | no - equivalent | none | EQUIV: all digested fixtures (COUNTER, POPULATION constants) are ASCII; encoding never differs |
| M03 | default Round 42 -> 41 | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-dispatch-before-freeze) | tool scopes dispatch files by the Round: line; round-41 default flips dispatch-before-freeze |
| M04 | Round line emitted with empty value | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x21 (case-clean); case detail x13 (case-dup-base-differs) | empty Round: value -> FIELD-MISSING C0 Round on every fixture |
| M05 | claim heading numbered n+1 | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x15 (case-field-missing-base); case detail x2 (case-counter-symlink) | claim headings numbered n+1; expected C1 labels no longer appear |
| M06 | heading em dash -> hyphen | no - equivalent | none | EQUIV: heading tail after `## C<digits>` is not read by the tool |
| M07 | key tuple drops Kill | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x21 (case-clean); case detail x13 (case-dup-base-differs) | Kill key never written -> FIELD-MISSING on every clean fixture |
| M08 | None-filter removed (identity no-op) | no - equivalent | none | EQUIV: no claim value is None (drop/blank use pop/assignment) |
| M09 | key line separator without space | no - survived (named limit) | none | NAMED LIMIT NL-SPACING: Key:value without space is accepted by the tool; no case pins it |
| M10 | claim lines joined by blank line | no - survived (named limit) | none | NAMED LIMIT NL-SPACING: blank lines inside a claim block are accepted; no case pins it |
| M11 | __extra read with None default (crash when absent) | YES (verdict) | no SUMMARY (output replaced: traceback/abort); case lines suppressed | crash: __extra default None raises TypeError in every fixture (no output) |
| M12 | Counter digest taken from population | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x18 (case-clean); case detail x12 (case-dup-base-differs) | Counter digest taken from population -> COUNTER-DIGEST on clean |
| M13 | Counter path with double space before sha256 | no - survived (named limit) | none | NAMED LIMIT NL-SPACING: double space before sha256= accepted by `[ \t]+`; no case pins it |
| M14 | Target value changed (fixture only) | no - survived (named limit) | none | NAMED LIMIT NL-VALUE: Target value is never read by the tool or the counter |
| M15 | Control path points at a missing file | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x20 (case-clean); case detail x13 (case-dup-base-differs) | Control path missing -> CONTROL-MISSING on clean |
| M16 | counter_digest sentinel 63 zeros + 1 | no - equivalent | none | EQUIV: any non-matching digest gives the same COUNTER-DIGEST class |
| M17 | population_digest sentinel changed | no - equivalent | none | EQUIV: any non-matching digest gives the same POPULATION-DIGEST class |
| M18 | population override inverted | YES (verdict) | no SUMMARY (output replaced: traceback/abort); case lines suppressed | inverted population override -> KeyError crash in clean fixture |
| M19 | two_claims: bad claim drops Target instead of Kill | no - survived (named limit) | none | NAMED LIMIT NL-FIELDNAME: missing key is compared by class only; run_tool keeps claim+class, not the key |
| M20 | two_claims: claim order reversed | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-two-claims-one-bad) | two-claims order swapped -> C1 FIELD-MISSING where C2 is expected |
| M21 | counter_missing guard inverted | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x20 (case-clean); case detail x12 (case-dup-base-differs) | COUNTER-MISSING on clean fixture |
| M22 | frozen edit becomes a no-op (commit fails) | YES (verdict) | no SUMMARY (output replaced: traceback/abort); case lines suppressed | no-op 'edit' makes git commit fail -> RuntimeError (output replaced) |
| M23 | early dispatch written under round-41 | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-dispatch-before-freeze) | dispatch file written outside round-42 path; base no longer sees it |
| M24 | early wave files written under round-43 | no - survived (named limit) | none | NAMED LIMIT NL-BASERED: wave-file path change in dispatch-*-before fixtures; base and stub are FAIL there with identical detail, so the fixture change is invisible to scored tools |
| M25 | side branch named main (checkout fails) | YES (verdict) | no SUMMARY (output replaced: traceback/abort); case lines suppressed | branch name clash -> checkout fails -> crash |
| M26 | base-not-ancestor claim uses the ancestor base | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-base-not-ancestor) | base-not-ancestor claim uses an ancestor base -> case flips PASS->FAIL |
| M27 | base-unresolved sentinel f*40 | no - equivalent | none | EQUIV: any unresolvable sha yields BASE-UNRESOLVED |
| M28 | fixture tip returned as freeze commit | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x2 (case-frozen-edited-counter) | tip returned as freeze commit: frozen-edited fixtures no longer see the edit |
| M29 | dup sentinel string changed (identical-vs-differs unobservable) | no - equivalent | none | EQUIV: KEY-DUPLICATE is defined by key repetition alone (value-independent); the sentinel does not change the class |
| M30 | default control becomes the green receipt | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x19 (case-clean); case detail x13 (case-dup-base-differs) | green receipt as default control -> CONTROL-NOT-RED on clean |
| M31 | CONTROL_RED last line EXIT=0 | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x19 (case-clean); case detail x13 (case-dup-base-differs) | EXIT=0 last line in red receipt -> control-not-red fixtures disturbed |
| M32 | CONTROL_GREEN corrected=0 (EXIT=0 kept) | no - survived (named limit) | none | NAMED LIMIT NL-RECEIPT: corrected= count of the green receipt is never read (tool reads only the final EXIT line) |
| M33 | COUNTER constant text changed (digest follows) | no - equivalent | none | EQUIV: the COUNTER constant and its digest are derived from one value; only digest equality is checked |
| M34 | counter symlink target dangling | no - survived (named limit) | none | NAMED LIMIT NL-SYMLINK-TARGET: dangling link reads as COUNTER-DIGEST on base; target name not pinned and case is red on base |
| M35 | counter symlink not created | YES (text only) | case detail x1 (case-counter-symlink) | counter-symlink fixture without the symlink -> COUNTER-MISSING (detail only; verdict FAIL both before and after) |
| M36 | population symlink not created | YES (text only) | case detail x1 (case-population-symlink) | population-symlink fixture without the symlink -> detail only; verdict FAIL both before and after |
| M37 | tail default newline (blank line) | no - equivalent | none | EQUIV: a trailing blank line is ignored by the tool |
| M38 | drop() removes the wrong key (Base always) | no - survived (named limit) | none | NAMED LIMIT NL-FIELDNAME: every drop fixture removes Base; FIELD-MISSING checked by class, so the key is never verified |
| M39 | blank() writes a space instead of empty | no - equivalent | none | EQUIV: tool strips values, so one space is FIELD-EMPTY like the empty value |
| M40 | clean expects rc 1 | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-clean) | clean expects rc 1 -> FAIL on base and stub |
| M41 | no-claims expects C1 class | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-no-claims) | no-claims expects a C1 class -> FAIL |
| M42 | field-missing-base expects C2 class | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-field-missing-base) | field-missing-base expects C2 -> FAIL |
| M43 | dup-target want class FIELD-EMPTY (verdict same, detail differs) | YES (text only) | case detail x1 (case-dup-target) | dup-target wants FIELD-EMPTY: FAIL on both, only the printed want changes |
| M44 | heading-valid-tail expects 5 copies | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-heading-valid-tail) | heading-valid-tail expects 5 copies; multiset exact -> FAIL |
| M45 | counter-symlink expects COUNTER-DIGEST | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-counter-symlink) | counter-symlink expects COUNTER-DIGEST: base case flips FAIL->PASS (fail 13->12) |
| M46 | dispatch-names-after expects rc 1 | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-dispatch-names-after) | dispatch-names-after expects rc 1 -> PASS->FAIL |
| M47 | dispatch-spec-before fixture file renamed .txt | no - survived (named limit) | none | NAMED LIMIT NL-BASERED: dispatch-spec-before fixture renamed; base/stub red with identical detail (the names are not printed) |
| M48 | dispatch-notes-before negative fixture renamed to a dispatch name | no - survived (named limit) | none | NAMED LIMIT NL-BASERED: negative fixture renamed to a dispatch-pattern name; base/stub PASS. Only a tool that implements the widened name rule would fail it |
| M49 | dispatch-attempts-before want class changed | YES (text only) | case detail x1 (case-dispatch-attempts-before) | dispatch-attempts-before wants DISPATCH-AFTER: FAIL both, only the printed want changes |
| M50 | population-symlink fixture uses missing mutation | YES (text only) | case detail x1 (case-population-symlink) | population-symlink fixture as population_missing: detail only |
| M51 | population-empty fixture no longer empty | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-population-empty) | population-empty fixture no longer empty -> POPULATION-EMPTY absent -> FAIL |
| M52 | two-claims-one-bad want C1 class | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-two-claims-one-bad) | two-claims wants C1 -> FAIL |
| M53 | base-not-ancestor expects rc 0 | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-base-not-ancestor) | base-not-ancestor wants rc 0 -> FAIL |
| M54 | frozen-edited-population expects POPULATION-DIGEST | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-frozen-edited-population) | frozen-edited-population wants POPULATION-DIGEST -> PASS->FAIL |
| M55 | case_ok rc comparison inverted | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x22 (case-clean) | rc comparison inverted -> 35 of 37 cases flip |
| M56 | case_ok multiset compared as set | no - survived (named limit) | none | NAMED LIMIT NL-MULTISET: set vs multiset; base and stub produce exact multiplicities, so no scored case decides on multiplicity |
| M57 | case_ok SUMMARY count check weakened | no - survived (named limit) | none | NAMED LIMIT NL-SUMCOUNT: SUMMARY findings count compared with len(want), never with the FINDING lines; no scored tool prints an inconsistent count |
| M58 | case_ok crash check removed | no - survived (named limit) | none | NAMED LIMIT NL-CRASH: crash guard unexercised; no scored tool emits a traceback |
| M59 | case_ok detail truncated to 24 chars | YES (text only) | case detail x13 (case-dup-base-differs) | detail truncated to 24 chars: FAIL lines shorter, verdict unchanged |
| M60 | unresolved-prereg probe uses an existing prereg | YES (verdict) | SUMMARY.fail; SUMMARY.pass; case verdict flips x1 (case-absent-prereg) | absent-prereg probe uses an existing prereg -> FAIL |
| M61 | unresolved-rev check weakened to != 0 | no - survived (named limit) | none | NAMED LIMIT NL-REFUSAL-RC: unresolved rev accepted with rc 1 as well as 2; no scored tool exits 1 here |
| M62 | score_tool total drops one | YES (verdict) | SUMMARY.cases; SUMMARY.fail | cases total off by one -> cases=36 |
| M63 | score_tool drops absent-prereg result | YES (verdict) | SUMMARY.cases; SUMMARY.pass | absent-prereg probe dropped from the total -> cases=36 |
| M64 | FINDING regex without re.M | YES (verdict) | SUMMARY.fail; SUMMARY.pass; SUMMARY.retro; case verdict flips x1 (case-heading-valid-tail); case detail x1 (case-population-symlink); retro | FINDING regex without re.M: only the first finding is read (retro findings 19->1, population-symlink detail) |
| M65 | FINDING class group relaxed to uppercase only | no - equivalent | none | EQUIV: the class tokens of both tools are uppercase; the relaxed group matches the same tokens |
| M66 | SUMMARY regex trailing-space tolerance removed | no - equivalent | none | EQUIV: neither tool prints trailing whitespace on the SUMMARY line |
| M67 | run_tool timeout 300 -> 30 (no hang observed) | no - equivalent | none | EQUIV: no scored run approaches 30 s (about 10 s wall); the timeout is never hit |
| M68 | SELFTEST regex pass group single digit | YES (verdict) | SUMMARY.selftest; selftest | stub selftest line no longer matches (pass=12 needs two digits) -> selftest FAIL on stub |
| M69 | selftest case threshold 12 -> 13 | YES (verdict) | SUMMARY.selftest; selftest | selftest threshold 13 -> stub selftest FAIL |
| M70 | selftest fail==0 condition weakened | no - survived (named limit) | none | NAMED LIMIT NL-SELFTEST: fail==0 condition; the stub reports fail=0 only, so the condition is never exercised |
| M71 | selftest exit code 0 or 1 accepted | no - survived (named limit) | none | NAMED LIMIT NL-SELFTEST: selftest rc 1 accepted; no scored tool exits 1 from --selftest |
| M72 | patches counted without selftest gate | YES (verdict) | SUMMARY.patches | patch count without the selftest gate: base's argparse rc 2 counted -> base 3/3 |
| M73 | patched exit code only 124 counted | YES (verdict) | SUMMARY.patches | only 124 counted as patched failure: always-green stub -> 3/3 |
| M74 | P2 targets --diff-filter=D instead of A | no - survived (named limit) | none | NAMED LIMIT NL-PATCHLEG: P2 injection dead; both scored tools give 0/3 by construction, so the patch leg is invisible |
| M75 | P3 misspelled merge-base target | no - survived (named limit) | none | NAMED LIMIT NL-PATCHLEG: P3 injection dead; same invisibility |
| M76 | P1 digest reversal made identity | no - survived (named limit) | none | NAMED LIMIT NL-PATCHLEG: P1 reversal made identity; same invisibility |
| M77 | PYTHONPATH not pointed at patch dir | no - survived (named limit) | none | NAMED LIMIT NL-PATCHLEG: patch dir not on PYTHONPATH; same invisibility |
| M78 | patch selector env value wrong | no - survived (named limit) | none | NAMED LIMIT NL-PATCHLEG: patch selector value wrong; same invisibility |
| M79 | real leg checks SUMMARY claims only | no - survived (named limit) | none | NAMED LIMIT NL-REAL: real leg checks claims only; both scored tools have findings=0 anyway |
| M80 | retro threshold 3 -> 20 findings | YES (verdict) | SUMMARY.retro; retro | retro threshold 20: base has 19 findings -> retro FAIL |
| M81 | retro_clean expects (1,0) | YES (verdict) | SUMMARY.retro_clean; retro_clean | retro_clean expects (1,0) -> FAIL on both |
| M82 | RETRO_PATH points at round-41 | YES (verdict) | SUMMARY.retro; retro | RETRO_PATH on round-41: rc 0, so retro FAIL |
| M83 | PREREG_PATH points at round-41 | no - survived (named limit) | none | NAMED LIMIT NL-REAL: the round-41 prereg is also clean on base and stub (real=ok), so the path change is not observed |
| M84 | stub clean text claims findings=1 | no - survived (named limit) | none | NAMED LIMIT NL-STUB: stub text never printed; control verdict is a pass count only |
| M85 | stub findings receipt exit 0 | no - survived (named limit) | none | NAMED LIMIT NL-STUB: stub findings exit code never observed |
| M86 | stub clean exit 1 | no - survived (named limit) | none | NAMED LIMIT NL-STUB: stub clean exit code never observed |
| M87 | stub verdict threshold <= (ACCEPTED branch unreachable) | no - survived (named limit) | none | NAMED LIMIT NL-ACCEPTED: ACCEPTED branch needs a tool passing all 37 cases; neither scored tool does |
| M88 | stub verdict threshold sn-40 (kills stubs) | YES (verdict) | SUMMARY.control_clean; SUMMARY.control_findings | stub threshold sn-40: both stubs flip to ACCEPTED |
| M89 | met conjunct patches==3 dropped | no - survived (named limit) | none | NAMED LIMIT NL-MET: AND conjunct; base and stub fail >=2 conjuncts, so dropping one leaves exit 1 |
| M90 | met conjunct passed==n dropped | no - survived (named limit) | none | NAMED LIMIT NL-MET: AND conjunct passed==n; same |
| M91 | met forced True | YES (verdict) | exit 1->0 | met forced True -> exit 0 |
| M92 | exit code inverted | YES (verdict) | exit 1->0 | exit code inverted -> exit 0 |
| M93 | SUMMARY pass and fail arguments swapped | YES (verdict) | SUMMARY.fail; SUMMARY.pass | SUMMARY pass/fail values swapped |
| M94 | SUMMARY tool_sha prefix 11 chars | YES (text only) | SUMMARY.tool_sha | tool_sha prefix changed (SUMMARY text) |
| M95 | SUMMARY stub labels swapped (both REJECTED) | no - equivalent | none | EQUIV: both stubs are REJECTED; swapping the label order yields the same tokens |
| M96 | SUMMARY stub args swapped (both REJECTED) | no - equivalent | none | EQUIV: both stubs are REJECTED; swapping the arguments yields the same tokens |
| M97 | candidate case lines suppressed (verbose off) | YES (text only) | case lines suppressed | candidate case lines suppressed; SUMMARY and exit unchanged (text-only kill) |
| M98 | pristine check inverted | YES (verdict) | SUMMARY.control_clean; SUMMARY.control_findings; SUMMARY.fail; SUMMARY.pass; SUMMARY.real; SUMMARY.retro; SUMMARY.retro_clean; SUMMARY.tool_sha; case lines suppressed; SUMMARY.selftest | pristine check inverted: present tool reported absent (no case lines) |
| M99 | scratch dir refusal guard weakened | no (scored); YES by probe | probe-only: exit 2->1 + traceback | PROBE KILL: scratch guard weakened; invocation with a missing scratch dir gives a FileNotFoundError traceback (rc 1) where the frozen counter refuses (rc 2). Not reached by any scored run |
| M100 | rev format guard (`not REV.match`) dropped from the refusal test | no (scored); YES by probe | probe-only: exit 2->1 (full run) | PROBE KILL: rev guard dropped; a 7-char short rev (afe17f4) runs the whole counter (rc 1) where the frozen counter refuses (rc 2). Not reached by any scored run |
| M101 | scratch cleanup removed (not observed) | no - equivalent | none | EQUIV for printed output: scratch cleanup removed; the leaked directory is not observed by the harness |
| M102 | default tool path misnamed (default invocation only) | no (scored); YES by probe | probe-only: PRISTINE TOOL-ABSENT, all cases red | PROBE KILL: default TOOL_PATH misnamed; the default invocation (used by score-candidate.sh) prints PRISTINE FAIL TOOL-ABSENT. Scored runs pass --tool explicitly, so they cannot see it |
| M103 | REV regex without end anchor (equivalent for 40-hex) | no - equivalent | none | EQUIV: cat-file rejects any non-commit string, so a 41-char rev refuses identically |

Survivors (not killed by any invocation, not equivalent): 30 (all NL-* above). Equivalent: 17. Killed: 56 (53 scored, of which 8 text-only; 3 probe-only).

## Residuals and what the L1 should know (not edits)

- The 13 base-red cases give the counter no independent kill path for fixture mutations; only a conforming r42 tool can detect them (NL-BASERED). The L1 should treat the base and stub scores as shape checks, not as evidence that a fixture edit is caught.
- The patches leg (NL-PATCHLEG) cannot distinguish a sensitive selftest from an always-green one using these two tools; the 0/3 receipt for the stub is the only observed value.
- No tool-behaviour defect was observed: the base tool and the stub gave identical output across all 206 scored runs except where the mutated counter itself changed the printed text. Every mutant is an edit to the counter copy only.

## Tools and installs

No tools were installed or upgraded. Interpreter and git were the system ones (python3, git). Scratch: `/fast/scratch/hyaku/souji-r42/R42mutationtester02` (clone, runs, outputs); deleted before yield after the receipts were copied to `.ufo/waves/round-42/w1/R42mutationtester02/receipts/`.

## Receipts (seat directory)

- `R42mutationtester02/c2-counter.py` (mutation base copy, sha fa44392d…)
- `R42mutationtester02/mutants/M01.py`..`M103.py`, `mutants/manifest.tsv`
- `R42mutationtester02/receipts/out/` (`base-base`, `base-stub`, `<id>-base`, `<id>-stub`, `probe-*` .out/.err/.rc)
- `R42mutationtester02/receipts/{run.sh,probes.sh,mutate.py,analyze.py,gen_report.py,ids.txt,analyze.txt,table.md}`
