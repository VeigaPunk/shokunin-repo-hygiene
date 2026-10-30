# R43mutationtester02 — frozen C3 scoring-logic mutation probe

## Scope and detector
Axes: false-green resistance, discrimination by leg, exact-byte restoration, bounded cost.
Attacked only `census/round-43/c3-counter.py` at commit `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373`; no drift-tool mutation or lane modification.
14 single-defect counter copies were constructed; only M12 and M13 were fully scored. Other conclusions below are code-reading arguments, not executed passes.
Expected behavioral detector: on the committed absent-fixture state, require counter process exit **1**, not 0. Thus pristine rc=1 is a **passing negative control**, not a baseline test failure. M13 is killed by this external detector but exposes a false green in the mutated counter; M12 survives this specific detector. No inference that M12 is harmless.
The SUMMARY does not contain a target/overall rc field: exit status is captured separately. “rc=1” inside `n10_after=no-refusal rc=1` is the probe exit, not the counter exit.

## Mutation table
“rc 0?” column is **pinned absent fixture / hypothetical zero-kill fixture with other legs true**. The latter is conditional code analysis, not an executed candidate. Unchanged kill-count checks are the independent catch for most local gate defects, not proof that those local gates are mutation-covered.

| mutant | change | caught-by (leg / argument) | would target still read rc 0? |
|---|---|---|---|
| M01 | Own traceback ignored (L172) | [INFERENCE] stderr_discrimination own-crash arm: no-summary instead of fixture-traceback; target false. | No / No |
| M02 | All traceback frames treated as fixture-owned (L169) | [INFERENCE] stderr_discrimination forwarded-tool arm: fixture-traceback instead of KILL; target false. | No / No |
| M03 | SUMMARY fail >= 0 accepted as kill (L175) | [INFERENCE] selftest misses this. An exit-1 zero-fail fixture gets false kills for both MUTANTS and EQUIV; equiv_killed guard catches that uniform lie. Other selective lies not established. | No / possible only with selective lies; unproved |
| M04 | equiv_killed == 0 becomes >= 0 (L408) | [INFERENCE] equiv guard gone; zero-kill fixture still fails killed==16. A fixture genuinely killing 16 but also killing EQUIV is no longer rejected by this leg. | No / No |
| M05 | EQUIV candidate scoring uses empty population (L355) | [INFERENCE] equiv_killed remains 0; sniff control still uses EQUIV separately. Zero kills still rejected by killed==16. | No / No |
| M06 | old_killed accumulator always adds zero (L379) | [INFERENCE] old population kills disappear from target; killed==16 still rejects no-kill fixture. No selftest checks this accumulator. | No / No |
| M07 | oldscore maps empty population (L378) | [INFERENCE] no old evaluations, old_killed remains 0. prior_clean still checked independently. killed==16 rejects no-kill fixture. | No / No |
| M08 | N10 requires marker OR exit 2 (L243) | [INFERENCE] accepts marker with wrong rc or unrelated exit-2 refusal; no direct-probe selftest. Pinned observed rc=1 and no marker does not pass. killed==16 remains. | No / No |
| M09 | N10 accepts generic REFUSAL prefix (L243) | [INFERENCE] unrelated refusal exit 2 accepted; no direct-probe selftest. Pinned observed rc=1 remains rejected. killed==16 remains. | No / No |
| M10 | Shim threshold >= 1 instead of >= passed (L400) | [INFERENCE] one invocation can cover >=17 claimed passing cases; no shim selftest. killed==16 still rejects no-kill fixture. | No / No |
| M11 | Drop shim passed > 0 requirement (L400) | [INFERENCE] zero passing cases with zero shim calls can satisfy shim, but absent fixture initializes calls=-1. cases>=17 and killed==16 remain; no shim selftest. | No / No |
| M12 | First target AND becomes OR (L408) | OBSERVED rc=1 on absent fixture (external rejection detector survives mutant). [INFERENCE] killed==16 bypassed when RHS all true; cases/prior/N10/sniff/shim still reject absent state. | No / Yes if remaining legs true |
| M13 | Last target AND becomes OR (L410) | OBSERVED rc=0 on absent fixture: stderr_disc=True bypasses every other leg. External absent-fixture rejection detector kills this mutant; frozen internal gates miss it. | YES / YES |
| M14 | Require killed >= 0 instead of ==16 (L408) | [INFERENCE] kill-count guard tautological. Absent fixture still rejected by prior/cases/N10/sniff/shim. No-kill fixture may pass if remaining independent legs all true. | No / Yes if remaining legs true |

## Exact commands and observed outputs
Commands were launched with Python `asyncio.create_subprocess_exec`, `cwd` set to this seat's scratch root, inherited environment plus explicitly set TMPDIR, captured stdout/stderr, and a 180-second process bound. No timeout occurred. Pristine/M12/M13 ran concurrently in distinct work directories; restoration controls ran concurrently after exact restoration.
Read-only provenance command:
```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 census/round-43/c3-counter.py tests/fixtures/r43-drift-survivors.py
100755 blob 5429d5d9fd1752a34b900035770af6d81e9ab4ed	census/round-43/c3-counter.py
```
No fixture entry was printed. Frozen bytes loaded by:
```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c3-counter.py
```
Observed success; SHA256 `66188cccb23bd35df69238cc05c2b5d84612e89590f09537b9f5c498a388b63f` (21199 bytes).
Durable complete receipts: `.ufo/waves/round-43/w1/R43mutationtester02/scored-runs.json`.
Exact substitutions and all mutant hashes: `.ufo/waves/round-43/w1/R43mutationtester02/mutations.json`.

### pristine
```text
TMPDIR=/fast/scratch/hyaku/souji-r43/R43mutationtester02/tmp python3 -B /fast/scratch/hyaku/souji-r43/R43mutationtester02/counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 --scratch /fast/scratch/hyaku/souji-r43/R43mutationtester02/run-pristine
process_exit=1
SUMMARY mutants=16 killed=0 survived=16 crashed=0 timed_out=0 equiv=6 equiv_killed=0 old_killed=0 prior=0/9 cases=0 pass=0 fail=0 fails=- n10_before=no-fixture n10_after=no-refusal rc=1 sniff_eq_killed=0 shim=FAIL invocations=-1 stderr_discrimination=ok anchors=ok population=ok tool_sha=b2a603cf4247 load=12.25
stderr=''
sha256=66188cccb23bd35df69238cc05c2b5d84612e89590f09537b9f5c498a388b63f
```

### M12
```text
TMPDIR=/fast/scratch/hyaku/souji-r43/R43mutationtester02/tmp python3 -B /fast/scratch/hyaku/souji-r43/R43mutationtester02/M12.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 --scratch /fast/scratch/hyaku/souji-r43/R43mutationtester02/run-M12
process_exit=1
SUMMARY mutants=16 killed=0 survived=16 crashed=0 timed_out=0 equiv=6 equiv_killed=0 old_killed=0 prior=0/9 cases=0 pass=0 fail=0 fails=- n10_before=no-fixture n10_after=no-refusal rc=1 sniff_eq_killed=0 shim=FAIL invocations=-1 stderr_discrimination=ok anchors=ok population=ok tool_sha=b2a603cf4247 load=12.25
stderr=''
sha256=fffdf31bf208d097d0f99cacfa61caf1e42dc9ee72e341f3f75557ad1ae0f3ff
```

### M13
```text
TMPDIR=/fast/scratch/hyaku/souji-r43/R43mutationtester02/tmp python3 -B /fast/scratch/hyaku/souji-r43/R43mutationtester02/M13.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 --scratch /fast/scratch/hyaku/souji-r43/R43mutationtester02/run-M13
process_exit=0
SUMMARY mutants=16 killed=0 survived=16 crashed=0 timed_out=0 equiv=6 equiv_killed=0 old_killed=0 prior=0/9 cases=0 pass=0 fail=0 fails=- n10_before=no-fixture n10_after=no-refusal rc=1 sniff_eq_killed=0 shim=FAIL invocations=-1 stderr_discrimination=ok anchors=ok population=ok tool_sha=b2a603cf4247 load=12.25
stderr=''
sha256=7c6817bb6963cbd5373ba361fe917e7429bb602a5429c764330ca62412d28bb0
```

### M12-restored
```text
TMPDIR=/fast/scratch/hyaku/souji-r43/R43mutationtester02/tmp python3 -B /fast/scratch/hyaku/souji-r43/R43mutationtester02/M12.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 --scratch /fast/scratch/hyaku/souji-r43/R43mutationtester02/run-M12-restored
process_exit=1
SUMMARY mutants=16 killed=0 survived=16 crashed=0 timed_out=0 equiv=6 equiv_killed=0 old_killed=0 prior=0/9 cases=0 pass=0 fail=0 fails=- n10_before=no-fixture n10_after=no-refusal rc=1 sniff_eq_killed=0 shim=FAIL invocations=-1 stderr_discrimination=ok anchors=ok population=ok tool_sha=b2a603cf4247 load=12.25
stderr=''
sha256=66188cccb23bd35df69238cc05c2b5d84612e89590f09537b9f5c498a388b63f
```

### M13-restored
```text
TMPDIR=/fast/scratch/hyaku/souji-r43/R43mutationtester02/tmp python3 -B /fast/scratch/hyaku/souji-r43/R43mutationtester02/M13.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 --scratch /fast/scratch/hyaku/souji-r43/R43mutationtester02/run-M13-restored
process_exit=1
SUMMARY mutants=16 killed=0 survived=16 crashed=0 timed_out=0 equiv=6 equiv_killed=0 old_killed=0 prior=0/9 cases=0 pass=0 fail=0 fails=- n10_before=no-fixture n10_after=no-refusal rc=1 sniff_eq_killed=0 shim=FAIL invocations=-1 stderr_discrimination=ok anchors=ok population=ok tool_sha=b2a603cf4247 load=12.25
stderr=''
sha256=66188cccb23bd35df69238cc05c2b5d84612e89590f09537b9f5c498a388b63f
```

## Verdict and findings for L1 (no instrument fixes)
- **M13: external detector KILLED; internal false green demonstrated.** A single final `and`→`or` permits counter exit 0 with killed=0, survived=16, prior=0/9, cases=0, failed N10 and failed shim. The printed SUMMARY itself still exposes all red fields; consumers must not assume a mutated exit conjunction is protected by the selftest.
- **M12: SURVIVED the absent-fixture rejection detector** (rc=1 before, during, after). This detector is too weak to challenge deletion/bypass of just one gate while the absent fixture fails several other gates. A passing-state, gate-specific negative-control battery is needed to discriminate M03–M12/M14; no claim that such a battery currently exists.
- **M01/M02: argued caught** by the embedded stderr_discrimination selftest. **M03–M11/M14: full-run verdict INCONCLUSIVE/unrun**, with local lost behavior and independent zero-kill catch separated in the table.
- Code-reading finding in the frozen original: old_killed loop iterates all nine PRIOR fixtures (L358–379), although docstring says eight pre-r42 and PRE42 is defined but unused. The `fx_path == FIXTURE` skip never matches PRIOR. This is an original instrument discrepancy, not a mutation result; no runtime effect quantified here.
- Code-reading finding in the frozen original: n10_before is printed but absent from target L408–410. Its normative historical case requirement is not enforced by the conjunction. No candidate exploit was executed.

## Restoration and cleanup
Every mutant copy was restored to exact frozen bytes before deletion; M12/M13 were additionally rescored after restoration and both returned 1 with the original hash. Full per-mutant original/mutated/restored hashes and byte-equality results are retained in `.ufo/waves/round-43/w1/R43mutationtester02/restoration.json`. Mutation definitions persist, not scratch files. Scratch cleanup is performed after writing this report; the completion result records its outcome. No lane git/jj mutations, commits, installs, host changes, or other runtimes were used.

## Self-evaluation
Accuracy 4/5: exact receipts separate exit status from embedded probe rc; twelve mutants remain argued rather than scored by design. Completeness 5/5: fourteen defects cover all six requested areas and two full mutant scores plus restoration controls. Clarity 4/5: two meanings of mutant survival require explicit internal/external distinction. Actionability 4/5: gate-specific negative controls identified, not implemented in frozen instruments. Conciseness 4/5: five verbatim control receipts are longer than the requested two mutant SUMMARYs but preserve restoration evidence. Overall 4.2/5. Highest-impact improvement would be an L1-owned passing-state gate-isolation battery; user should agree that the evidence is bounded, not a production verdict.
