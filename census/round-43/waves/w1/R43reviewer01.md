# R43reviewer01 — frozen-instrument review

Axes: calibration, operability, coverage. Verdict: **findings; do not treat these instruments as independently cleared**. Recommendation only, not admission or scoring. No instrument was edited.

Reviewed exact blobs at `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373`, not the moving working tree. Line numbers below refer to that revision. Frozen copies and reproducible bounded probes are in `.ufo/waves/round-43/w1/R43reviewer01/`.

## Findings (severity order)

P1 = breaks a central scoring guarantee; P2 = incorrect refusal, cleanup, or secondary contract; P3 = bounded/latent fixture issue. Mocked observations below are unit-level evidence, **not** candidate score receipts.

| File:line | Defect / instrument attacked | Concrete consequence / evidence | Severity |
|---|---|---|---|
| `census/round-43/c3-counter.py:133-139,393-399` | C3 shim source retains doubled percent operators: `fh.write('invoke %%s\\n' %% ' '.join(args))`; WRAPPER is never interpolated. | Compiling the literal frozen WRAPPER raises SyntaxError on line 4. An honest fixture cannot execute the wrapper to log its tool calls; absent log becomes zero invocations and `shim=FAIL`. This rejects behaviorally correct candidates. `probe-output.txt`, wrapper section. | P1 |
| `census/round-43/c3-counter.py:121-132,380-383,410` | C3 sniff control watches only MUTANTS anchors, although it is scored against EQUIV substitutions. | On the actual committed tool, **each of B3, B4, E5, E7, E9, H4 leaves every watched anchor present**. Thus the embedded sniff fixture passes all six and `sniff_eq_killed=0`, contradicting required `>=1`. An ordinary N10 fix preserving these regions still fails this unrelated control. `probe-output.txt` lists all six empty absent-anchor sets. Not a claim that arbitrary adversarial rearrangements can never influence overlaps. | P1 |
| `census/round-43/c1-counter.py:240,248-253` | C1 parses correction `derived` but excludes it from comparison and rederives the register value instead. | Replacing D1 prose `derived=rows=174` with `derived=rows=999` still produces `registered=3 rederived=3 junk=0` and returns 0 in the bounded probe. Historical blobs are real; only the append evaluator and successful diff result are injected. The candidate prose's numerical claim is never checked against either register or committed derivation. | P1 |
| `census/round-43/c2-counter.py:310,317,349-350` | C2 memorizer imports `hashlib, sys` but calls `os.path.exists`. Any nonzero hidden-control exit is accepted as rejection. | Executing the literal generated assignments gives exit 1 / `NameError: name 'os' is not defined`. The supposed memorizer discrimination control can read `REJECTED` because the control crashes before answering, not because the audit discriminates its memorized answers. `contracts-output.txt`. | P1 |
| `census/round-43/c3-counter.py:325-330,340-348,408-410` | C3 target ignores `n10_before`; primary-fixture success ignores its return code, case-line agreement, and cases/pass/fail consistency. | With unrelated legs explicitly injected green, main returns 0 while printing `n10_before=wrong-fails`; the primary fixture in that probe exits 1 while printing `cases=17 pass=17 fail=0`. This is a demonstrated SUMMARY/exit-contract disagreement, not a full score pass. `contracts-output.txt`. | P1 |
| `census/round-43/c1-counter.py:277-278,291-294` | C1 evaluator refusal collapses into target-unmet. | Injected declared-evidence exit 2 produces `new_mismatches=-1` and main returns **1**, not documented could-not-evaluate exit 2. `probe-output.txt`. | P2 |
| `census/round-43/c1-counter.py:198,219,272-286`; `census/round-43/c2-counter.py:261,273,290,401`; `census/round-43/c3-counter.py:288,303,325,420` | All three counters lack an outer error-to-refusal boundary and finally cleanup for their scoring workspace. | Actual CLI runs with `--scratch` naming a file all exit **1**, traceback FileExistsError, no SUMMARY. Injecting TimeoutExpired into C1 evaluation or OSError into C2 build / C3 fixture startup leaves respectively `r43c1-*`, `r43c2-*`, `r43c3-*` behind and propagates the exception. The outer probe removes everything afterward. A real timeout/I/O failure is not a candidate miss and must not leak its workspace. | P2 |
| `census/round-43/c2-counter.py:32,294-296,339-342,386-404` | C2 advertises candidate timeout as refusal but timeout branches simply mark legs red. | A timed-out visible candidate is appended as `<case>:timeout`; target then returns 1, not 2, and no `CANDIDATE-TIMEOUT` refusal is emitted. Hidden/selftest/tmpdir timeout branches likewise collapse infrastructure inability into a miss. Static control-flow evidence; no real hang induced. | P2 |
| `census/round-43/c3-counter.py:354-356,373-379,408-410` | C3 drops EQUIV and old-fixture timeout results from `timed_out`. | EQUIV `timed-out` is neither a kill nor a counted timeout; oldscore `timed-out` similarly contributes zero old kills. SUMMARY can report `timed_out=0` despite those executions timing out, weakening the documented zero-timeout gate. Static control-flow finding. | P2 |
| `census/round-43/c3-counter.py:73,358-379` | C3 defines PRE42 but never uses it; `fx_path == FIXTURE` cannot exclude r42 because FIXTURE is r43 and is not in PRIOR. | `old_killed` is accumulated over **nine** batteries, including r42, although the documented leg specifies eight pre-r42 batteries. At the pinned tool this may coincide numerically; on a changed tool it measures a stronger/different invariant and adds 16 unadvertised executions. Static finding, not a measured candidate regression. | P2 |
| `census/round-43/c2-counter.py:51,262-268` | Absent tool is documented as target unmet but handled as missing-input refusal. | A revision lacking TOOL_PATH returns 2, contrary to docstring exit-1 contract for absent tool. Static finding; no repository mutation used to construct such a revision. | P2 |
| `tests/fixtures/r43-correction-prose.py:128-131` | Fixture ignores checkout return code. | A valid repository root after failed checkout still returns success from clone(); subsequent edits/commits can test the clone's default HEAD instead of requested `--rev42/43`, skewing the reported discrimination result. A readable clone root does not establish revision identity. Static error-path finding. | P2 |
| `tests/fixtures/r43-correction-prose.py:189-191` | The r42 strip is prefix filtering, not a correction grammar (there is no strip regex). | Synthetic non-record prose `CORRECTION-DE is the literal marker described here, not a record.` is deleted. It also strips CORRECTION-SC, broader than the docstring's DE-only claim. At pinned R42_TIP the actual seven victims are five DE records plus two genuine SC records; **no observed ordinary non-correction prose loss at that pin**. `probe-output.txt` lists all victims. | P3 |
| `tests/fixtures/r43-correction-prose.py:165,182-207,238` | Fixture cleanup runs only on normal completion. | Uncaught checkout-following file/commit failure bypasses `shutil.rmtree(work)`, retaining clones/work. This is static evidence; full fixture exception execution was not run. | P3 |

## Cleared checks and bounded limitations

| File:line | Check cleared within reviewed scope | Consequence | Severity |
|---|---|---|---|
| `census/round-43/c1-counter.py:1-298` | No ThreadPoolExecutor or shared-worker state exists. Its SUMMARY fields and target predicate otherwise agree for an ordinary completed evaluation. | No C1 thread-collision finding; does not clear ignored derived prose or error classification above. | Clear, bounded |
| `census/round-43/c2-counter.py:279-308,392-404` | Visible/stub scoring is serial, each label/case owns its directory. No ThreadPoolExecutor exists. Printed leg booleans map directly to the returned target predicate. | No C2 in-process concurrency collision or final boolean/SUMMARY disagreement identified; leg truthfulness remains defective as above. | Clear, bounded |
| `census/round-43/c3-counter.py:308-320,349-383` | Within each executor invocation, distinct mutant ids own `mut_<id>.py` and distinct fixture workdirs. `map` is fully consumed and executor closed before a later stage reuses paths. oldscore binds fxb/tag defaults; per-fixture loop waits for completion. | No intrinsic concurrent workdir collision/shared-result counter mutation found. Generic fixtures still share scratch cwd/TMPDIR, so candidate-created fixed names or escaped subprocess descendants are not proven safe. No saturation claim is made. | Clear, bounded |
| `tests/fixtures/r43-correction-prose.py:122-141,164-209` | Normal pinned-revision write destinations are clone-local under --work; counters receive separate work-local scratch directories. No direct lane write identified. Git shared clones read source objects; normal commits write clone storage. | Inspected R42 lesson/register/SCORECARD and R43 register/SCORECARD modes are 100644, not symlinks; R43 lesson absent is created in clone. Mode receipt: `file-modes.txt`. Caller-supplied malicious work paths/revisions, inherited git hooks/config/environment, and transitive counter writes were not sandbox-audited. | Clear, bounded |

## Commands and observed evidence

These probes deliberately avoid full scoring, commits, and instrument changes. All subprocess git commands were read-only and named the absolute lane with `-C`. No tools installed or updated. No subagents dispatched.

1. Read `skill://godspeed`; attempted `read xd://lsp`: device answered **No such tool**. Thus status/references/definition/diagnostics were unavailable, not empty semantic results. Used frozen-source inspection and local Python probes instead; no grep output is represented as semantic proof.
2. Captured each exact frozen blob with:

   ```text
   git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c1-counter.py
   git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c2-counter.py
   git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c3-counter.py
   git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:tests/fixtures/r43-correction-prose.py
   ```

   Observed 298, 408, 425, 243 lines respectively; copies retain original basenames in the seat directory.
3. Ran via Python subprocess, cwd the seat directory:

   ```text
   python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43reviewer01/probe.py
   python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43reviewer01/contracts.py
   ```

   Each invocation explicitly supplied TMPDIR equal to the seat's assigned scratch root. Probe code also creates that root, sets tempfile's root explicitly, and removes it in finally. Exact nested git/show, CLI, and compile/injection operations are in the scripts. Final observed exits: both **0**; both print `scratch_removed=True`. Full final stdout/stderr: `probe-output.txt` and `contracts-output.txt` in the seat directory. An initial probe run had a missing PIPE attribute in the mock and did not exercise C1; corrected before collecting the final receipt. Its apparent C1 exceptions are not findings.
4. Mode inspection commands and full observed output are retained in `file-modes.txt` in the seat directory. Commands were `git -C <absolute lane> ls-tree <R42_TIP or frozen revision> <lesson> <register> SCORECARD.md`; all listed write targets are regular files and the R43 lesson is absent.

## Residual risk / verification gaps

No full counter/candidate score, 144-execution coverage leg, or discrimination fixture suite was run. This is an instrument code review plus bounded probes, not a candidate admission. C3's unconditional wrapper syntax error and ineffective sniff control should be surfaced to L1 as frozen-instrument defects, never repaired by a seat. C3 target mismatch evidence intentionally mocks unrelated green legs; do not cite it as a real successful score. Exception cleanup observations distinguish injected failures from actual CLI scratch-file failures. No resume path, same-identity rerouting implementation, or runtime saturation claim is present in these four reviewed files; those broader contracts are not cleared here.

Self-evaluation: accuracy 4 (some findings are static/injected, labelled); completeness 4 (all requested dimensions inspected, no full scoring); clarity 4 (bounded-clear rows separate from defects); actionability 4 (exact frozen locations and reproducible scripts, fixes reserved for L1); conciseness 4 (report detailed to retain evidence). Overall 4.0/5. Highest-impact next verification: L1 should independently reproduce the frozen WRAPPER compile failure and sniff/EQUIV anchor mismatch before interpreting C3 candidate reds.
