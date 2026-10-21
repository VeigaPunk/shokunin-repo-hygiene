# InputCase15 — C2 caller-case falsifier `targeted-wrapper-dirty`

Seat: SoujiR20-2.InputCase15. Pinned commit: 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1. Baseline witness read at 12516f7dcdd5b165e5ee208d44a38d63b5bd5812.
Applicable caller: `census/round-14/run-targeted.py` (fixture kind `targeted`). Read only as its imported dependency: `census/round-14/run-verification.py`. Other callers not inspected.
Axes: predicate sufficiency, binding consumption, baseline witness, operability (judged axis).

**Verdict: source agreement.** At the pinned commit the case refuses for the designed reason. No blocking defect in this case. Operability: as a refusal probe it is operable (refusal happens before any suite command); as an acceptance proof it is not (no clean control; the accept path is a 90 s timeout with orphan risk, gap 5). Gaps below are non-blocking.

## 1. Trace (source-level; not executed)

| Step | Where | What happens |
|---|---|---|
| Entrypoint | fixture:660 `caller_command`; :673–684 `caller_refusal` | `python3 -B census/round-14/run-targeted.py --output census/round-20/r20-targeted-wrapper-dirty.json`; cwd = synthetic sandbox; env = CLEAN_ENV plus ambient GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE pointing at a decoy repo |
| Inert byte | fixture:651 `inert_suffix`; :700 `mutate_and_call` | `.py` suffix: `b"\n# inert r20 input-binding mutation\n"` appended to the sandbox wrapper. Guard `is_symlink() or not is_file()` at :715. Restored in `finally` |
| Closure | run-verification.py:32–46; fixture:987 | 13 MEASURED_PATHS entries; the wrapper is entry 10 (run-verification.py:42). targeted adds `census/round-14/verification-attempt-1.json` at runtime (run-targeted.py:23–24, mirrored at fixture:987). Prerequisite `covered_by_measured` at fixture:733/:763 |
| Import, before binding | run-targeted.py:16–18 | `exec_module` of run-verification.py runs its module-level code: BASE, ENV, MEASURED_PATHS, defs. No writes |
| Pre-binding | run-targeted.py:21 → run-verification.py:82–100 | `output_path()`: argparse reads `--output`; parent `census/round-20` exists (created by fixture:306) |
| Binding | run-targeted.py:25 → run-verification.py:51–73 → tools/souji-rev-pin.py:182, :226, :94 | `resolve_durable(ROOT, HEAD, MEASURED_PATHS)` → `input_snapshot`: committed blob sha256 vs working-tree sha256 |
| Refusal | rev-pin:177 → run-verification.py:71–73 | stderr: `run-verification: refused: measured inputs differ from <sandbox HEAD> (missing=[] added=[] changed=['census/round-14/run-targeted.py']) (no record written)`. `SystemExit(2)` escapes run-targeted.py:65, which catches only OSError/ValueError/RuntimeError → exit 2 |
| Predicate | fixture:687–698 | exit==2 AND `"census/round-14/run-targeted.py" in stdout+stderr` AND stdout=="" AND output absent. All four hold on this trace |

Stdout is empty because nothing prints before refusal. The suite progress print in `run()` is never reached. The output path is never created.

## 2. Answers

**Behavioral or wiring?** Behavioral at the process boundary. The real wrapper, the real r14 runner and the real rev-pin digest comparison decide the refusal. Wiring only for membership: the wrapper is refused because run-verification.py:42 lists it. The wrapper never checks its own bytes. The oracle is textual (substring). It is precise in practice, because the only input-binding message naming the wrapper is `changed=[...]`, but the predicate does not pin that family.

**Can a prerequisite refusal masquerade as the required reason?** Not in the shipped matrix. Exit-2 paths reachable from this caller:
- output_path ValueErrors (run-verification.py:82–100): none names the wrapper.
- argparse usage error: names only the basename `run-targeted.py`, not the relative path. No match.
- helper committed-bytes mismatch (run-verification.py:51–73): names the helper.
- resolve_durable rev/durable refusals (rev-pin:182–225): no path in the message.
- input_snapshot symlink/nonregular/unreadable refusals (rev-pin:139, :143, :156, :159, :171): name the wrapper if the wrapper is the failing entry.
- interpreter cannot open the entry script: CPython exit 2 with the path in stderr. [INFERENCE: not executed]

The last two categories are excluded before invocation, by checked_components (fixture:198–206, symlink refusal) and the `is_symlink/is_file` guard (fixture:715).

**Bounded counterexample.** If the sandbox wrapper were a symlink, or were unopenable at invocation, the tuple (exit 2, path named, empty stdout, no output) is produced with no digest comparison, and the predicate passes. The predicate itself does not exclude this. Only the pre-invocation guard at fixture:715 does. A refactor that moves or drops that guard silently turns this case into a masquerade-PASS.

**Is the input consumed by this caller?** Yes, twice.
- As program text: the interpreter compiles and runs run-targeted.py, and executes run-verification.py's module code, before any binding (run-targeted.py:16–18 precede :25). Inert bytes cannot distinguish "refused before execution" from "refused after import". The pinned module-level code has no side effects, so no record or output precedes the refusal.
- As a digest: at start (run-verification.py:67 → rev-pin:226), and again after the suite (run-targeted.py:46 `checked_inputs` → run-verification.py:75–79). This case exercises only the start check, because the dirty byte exists before launch.

## 3. Baseline producer witness (`baseline-targeted-wrapper`; fixture:818, checks :867–870)

- 12516f7 is an ancestor of 1988860 (`merge-base --is-ancestor` exit 0) and contains every current closure path (ls-tree).
- Baseline runner MEASURED_PATHS has 8 entries and omits the wrapper. Baseline wrapper blob f5b6d6e7, runner blob 8613de04, helper blob 332d4f09. Baseline rev-pin tree check is `git diff --quiet <rev> -- <paths>` over those 8 paths only (tracked-only). The dirty wrapper is outside that set. So `resolve_revision` returns, the old wrapper reaches `module.run`, and TRIPWIRE_DRIVER `producer` raises `ProducerReached("baseline-targeted-wrapper")`, which sets `baseline_reached`.
- The overlay sandbox (baseline corpus plus current wrapper, runner and helper) refuses at the wrapper, which sets `changed_refused`. The pair is red-before / green-after by source. [derived; not executed]
- Minor: the baseline output_absent check is vacuous for the old wrapper, which ignores `--output` and targets census/round-14/verification.json. The tripwire prevents any write, so no false pass results.

## 4. Non-blocking gaps (most consequential first)

1. **Textual predicate** (fixture:687). Pin the reason family instead: stderr contains `refused: measured inputs differ from` and `changed=['census/round-14/run-targeted.py']`. This closes the §2 counterexample without relying on the guards.
2. **No caller-level clean control.** The helper controls (fixture:621–631) run on the r13 closure only. Nothing shows that the 14-entry targeted closure resolves clean in a sandbox, so attribution rests on text. Cheap control: `resolve_durable(sandbox, HEAD, targeted_paths)` returns a 40-hex id, with no suite run.
3. **Pre-start only.** No case dirties a measured input during the run, so the post-suite `checked_inputs` (run-targeted.py:46) is untested by any case. `inputs_unchanged_during_run=True` (run-targeted.py:51) is a literal, justified only because :46 raises on change.
4. **Provenance.** The fixture copies from the lane working tree, not the pinned commit: DEFAULT_ROOT (fixture:30), `expand_closure(root, …)` (fixture:998), `make_sandbox` from root (fixture:291–306). The matrix output prints no subject revision; the only commit id is the sandbox HEAD inside refusal text. A run is pinned to 1988860 only when root is a clean checkout or export of it.
5. **Failure-mode operability.** [INFERENCE: not executed] `caller_refusal` `timeout=90` (fixture:683) kills only the direct child. r14 `run()` uses `start_new_session=True` (run-verification.py:108), so suite grandchildren survive a regression that accepts the wrapper and can race TemporaryDirectory cleanup.
6. **Exit-code contract hole** (adjacent, not this case). `git("rev-parse","HEAD")` in resolve_revision runs before its try block. An unborn or non-repo root raises CalledProcessError, giving a traceback and exit 1, not the documented 2. [derived from source]
7. **Blocked-exit collision.** Fixture prerequisite blocks return 2 (fixture:978, :1033), the same status as the refusal under test. Only the `prerequisite` CASE line distinguishes them.
8. **Precondition.** rev-pin `capture()` uses `hashlib.file_digest` (Python 3.11+). Host Python version not verified.
9. **Unverified boundary.** run-targeted.py:36–41 runs cache-demonstration.py, the census/round-13 runner, the census-boundary fixture and shellcheck as children. Whether cache-demonstration's own closure is a subset of the targeted 14-entry closure was not examined (single-caller scope). Route to the demo-caller falsifier / L1.

## 5. Verification performed

Source-only. No fixture, caller, helper or Python code executed; no imports. Read-only git against the pinned commit or the named baseline:
- `cat-file -s` (six sizes)
- `show` of: fixture; tools/souji-rev-pin.py; census/round-14/run-targeted.py; census/round-14/run-verification.py; and baseline run-targeted.py, run-verification.py, souji-rev-pin.py
- `log -1`, `cat-file -t`
- one non-recursive `ls-tree` of census/round-14/ plus named files at 1988860
- `ls-tree` of named paths at 12516f7
- `merge-base --is-ancestor` (exit 0)
- file-scoped `grep -n` on named files

Content of census/round-13/* and census/round-14/cache-demonstration.py was not read (sizes only). No census/operator-sweep path touched. Tooling: none installed.
