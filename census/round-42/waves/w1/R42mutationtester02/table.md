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
