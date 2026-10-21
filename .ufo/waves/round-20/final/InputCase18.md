# InputCase18 - demo-helper-dirty (C2 caller-case falsifier), source-only

STATUS: PARTIAL - The demo-helper-dirty predicate (`returncode == 2` and `"tools/souji-rev-pin.py"` in stdout+stderr and stdout empty) is reason-blind. A prerequisite refusal that names the helper path passes this case without any dirty-byte comparison having run (CE-1 below, source-constructed, not executed). A residue regression in the caller (CE-2) is invisible in both default and `--baseline` modes, and a producer-before-refusal regression is invisible in default mode. The pinned caller's current behaviour agrees with the expected refusal (source trace only; nothing was executed).

## Scope and method

- Read-only. Pinned sources were read with `git show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<path>`: `tests/fixtures/r20-input-binding.py`, `tools/souji-rev-pin.py`, and `census/round-14/cache-demonstration.py`. The last is the only applicable caller; r13, r14 and targeted have no demo case.
- Baseline witness: `git show 12516f7dcdd5b165e5ee208d44a38d63b5bd5812:census/round-14/cache-demonstration.py` and `:tools/souji-rev-pin.py`.
- Non-blob checks, all read-only: `git rev-parse HEAD` (lane HEAD = 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1); `git ls-tree` on named paths at both commits; `git hash-object --no-filters` (no `-w`) on four named working-tree files. Those four match the pinned blobs: cache-demonstration.py `b302186942e5`, souji-rev-pin.py `8da7da9c2d62`, souji-evidence-cache.py `82de0e07239f`, census/round-13/verification.json `879d96b42867`.
- Not run: no fixture, caller, helper or gate execution; no import; no git writes; no operator-sweep, fleet or proc paths read. The one census file hashed, census/round-13/verification.json, is a named demo input read only by `git hash-object`.
- Tool installs: none.

## 1. Trace: entrypoint to refusal

Fixture side (`run_caller_matrix` -> `mutation_plan("demo")` -> `mutate_and_call("demo-helper-dirty")`):
- Sandbox `top/demo` comes from `make_sandbox` over the working-tree closure of the 8 `DEMO_MEASURED_PATHS` entries. It is committed, so HEAD is clean.
- Inert byte: `tools/souji-rev-pin.py` becomes original + `b"\n# inert r20 input-binding mutation\n"`. It is restored in `finally`.
- Invocation: `python -B census/round-14/cache-demonstration.py`, no arguments, cwd = sandbox. Env = CLEAN_ENV plus `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` pointing at an unrelated decoy repository.
- Predicate (demo branch of `caller_refusal`): `returncode == 2 and "tools/souji-rev-pin.py" in (stdout+stderr) and stdout == ""`. There is no output-path check, because `caller_command` returns `None` for demo.

Caller side:
1. `__main__` calls `sys.exit(main())`. `main` takes no arguments. The gate is `LANE/tools/souji-evidence-cache.py`, where `LANE = Path(__file__).resolve().parents[2]` is the sandbox.
2. `inspect_gate` reads gate bytes and stat only. `tracked_at(BASELINE_COMMIT, ...)` runs `cat-file -e` and returns False without error.
3. `git_head()`:
   - `git -C LANE rev-parse --verify HEAD` with `env=GIT_ENV`, which does not inherit GIT_DIR. Returns the sandbox HEAD.
   - `helper.parent.is_symlink()`, `helper.is_symlink()` and `helper.is_file()` all pass.
   - `committed = check_output(git -C LANE show HEAD:tools/souji-rev-pin.py, env=GIT_ENV)`.
   - `helper.read_bytes() != committed` raises `ValueError("tools/souji-rev-pin.py differs from measured commit")`. It is caught and returned as `(None, "durable revision refused: tools/souji-rev-pin.py differs from measured commit")`.
4. `main`: `initial_commit is None`, so it writes `cache-demonstration: refused: durable revision refused: tools/souji-rev-pin.py differs from measured commit (no record written)` to stderr and returns 2.
5. Not reached on this path: the helper import (`spec_from_file_location` comes after the compare), `resolve_durable` and `input_snapshot`, `mkdtemp`, `run_demonstration`, `emit`. Nothing is written to stdout or to disk before `return 2`.

Source agreement: exit 2, the path on stderr, empty stdout, no residue. This is predicted from source and was not executed.

## 2. Consumption and input closure

- Consumed: yes. `tools/souji-rev-pin.py` is the first input read after the gate check. Its dirty working-tree bytes are compared against the HEAD blob before anything else.
- The inert byte is a Python comment, and the helper is never executed on this path. The refusal is exact-byte, not semantic.
- Closure: DEMO_MEASURED_PATHS (8 entries) covers every direct read of the caller: the gate (read and exec), the helper, the caller itself, the migrated import of `census/round-13/run-verification.py`, and the legacy `census/round-13/verification.json` section. `tools/souji-census.sh` and `tests/fixtures/r14-*` are listed but not read by this file. That over-inclusion is harmless. All 8 exist at 1988860.
- The caller's compare runs before `input_snapshot`. `input_snapshot` would also refuse, because HELPER is in the list. So this case does not show which check fires (F4).

## 3. Behavioral or wiring

- Refusal branch: behavioral. It runs the real entrypoint in a real git sandbox with a real byte mutation.
- No producer and no residue: not observed in default mode. The default matrix has no producer tripwire, and the demo case skips output checks. In `--baseline` mode, `output=""` makes `output_absent` trivially true.

## 4. Findings (severity order)

F1 - HIGH - Prerequisite masquerade (CE-1). The predicate accepts any exit-2, empty-stdout refusal that names the helper path. Bounded counterexample, source-constructed and not executed: drop `env=GIT_ENV` from either git call in `git_head`. The fixture injects `GIT_DIR=<decoy>` for every caller, and the decoy is a real repository with a commit. Git is then redirected to the decoy. Either way, the `git show <sha>:tools/souji-rev-pin.py` that follows exits 128 (the sha is absent from the repository it reads, or the decoy tree lacks the path). `subprocess.CalledProcessError` is caught by `git_head`'s `except`, and its text embeds `['git', '-C', ..., 'show', '<sha>:tools/souji-rev-pin.py']`. The result is `durable revision refused: Command ... returned non-zero exit status 128.` Exit 2, stdout empty, path named: demo-helper-dirty PASSES with no byte comparison. The pinned code sanitizes both calls, so this is a regression the case cannot see, not a present failure. The decoy is the only env-sanitization sentinel, and this case does not distinguish its outcome.

F2 - HIGH - The no-output conjunct is not observed for demo in either mode, and the no-producer conjunct only in `--baseline` mode (CE-2). The demo predicate has no output check, and the tripwire's `output_absent` is vacuous for demo. Counterexample: move `mkdtemp` above `git_head()` and return 2 without cleanup. That leaves `/var/tmp/souji-r14-cache-demo.*` behind, and demo-helper-dirty still PASSES in both modes, because the producer tripwire never fires. Only a residue check catches this. A producer that runs before the refusal is caught only by the `--baseline` tripwire, so default mode lacks that witness too.

F3 - MEDIUM - Constant or inverted refusal passes, and there is no clean control. Inverting the compare (`==`) lets dirty bytes through. `resolve_durable` -> `input_snapshot` then refuses with `measured inputs differ from <rev> (... changed=['tools/souji-rev-pin.py'])`, which still passes. A caller that always refuses with the helper-name message also passes this case. It is caught only collaterally, by wrapper-dirty and historical-input-dirty, which expect other path names. The demo matrix has no clean run, so nothing shows the compare accepts clean input.

F4 - MEDIUM - Mechanism-blind. Deleting the caller's compare entirely still passes, because `input_snapshot` refuses the same dirty helper. No matrix case observes whether the caller's own compare exists.

F5 - MEDIUM - Adjacent masquerade, same caller and input. demo-helper-syntax-invalid never reaches the syntax path. The byte compare refuses first with `differs from measured commit`, so that sibling passes as if it were a syntax refusal. To exercise `SyntaxError`, the invalid bytes must be committed into the sandbox first.

F6 - LOW - Evidence quality. The demo detail string hard-codes `refusal_on_stderr=1` whatever the outcome. The baseline tripwire reports `output_absent=1` for demo, which is vacuous.

F7 - LOW - Provenance. Default-mode sandboxes copy working-tree bytes through `expand_closure(root, ...)`, not pinned blobs. Nothing asserts that the lane tree equals 1988860. This is true today for the four blobs checked, but the fixture does not verify it.

F8 - LOW - A blocked top-level run exits 2, the same code as a caller refusal. Operators must read `SUMMARY blocked=1` and the INVENTORY line.

What holds: the early refusal before `mkdtemp`, the exact-byte inert mutation, the env sanitization in the caller, and the decoy injection as a design are all sound. The defects are in the predicate and in what the case observes.

## 5. Baseline producer witness (`baseline-demo-helper`)

Valid red-before for this input (source trace):
- Tripwire names exist in the pinned caller: `BASELINE_COMMIT` (module constant), `run_demonstration` (module global, looked up at call time after `mkdtemp`), and `main(argv)`.
- The 12516f7 caller has `DEMO_MEASURED_PATHS` with 6 entries. It omits the helper and `census/round-13/verification.json`. Its `git_head` calls the r19 `resolve_durable(LANE, HEAD, 6 paths)`, which runs `git diff --quiet HEAD -- <6 paths>`. The dirty helper is outside that set, so it is accepted. Execution reaches `mkdtemp`, then `run_demonstration`, where the tripwire raises `ProducerReached("baseline-demo-helper")`.
- The changed run in the pair uses the pinned caller, which refuses with exit 2, the path named and empty stdout. That is the expected green.
- The changed sandbox's prerequisites are met. Every current DEMO path exists at 12516f7 (checked with ls-tree). Its other closure bytes come from 12516f7, for example run-verification.py `e9b79525` against pinned `b5107ef`. That does not affect this refusal path.
- This witness inherits F1 and F2: the predicate is reason-blind and the output conjunct is vacuous.

## 6. Bounded fixes (for the fixture owner; not applied)

- R1: For demo-helper-dirty, require stderr to contain `tools/souji-rev-pin.py differs from measured commit` and stdout to equal `""`. This kills CE-1 and the F3 texts. It also makes the case specific to the caller compare, which is the intended choice and should be stated.
- R2: Add a clean demo control with no mutation. Expect exit 2 with stdout JSON `"reason": "baseline-unavailable"`, because the synthetic sandbox lacks commit a31642d. Also require that stderr lacks `differs from measured commit`. This proves the helper gate accepted clean bytes.
- R3: Add a residue check for demo, listing `/var/tmp/souji-r14-cache-demo.*` before and after the case, since TMP_BASE is hard-coded. Alternatively, add a default-mode producer tripwire. This kills CE-2 in both modes.
- R4: Remove the hard-coded `refusal_on_stderr=1` and measure where the refusal was written. Drop the vacuous demo `output_absent`.
- R5: Before the matrix, assert that the working-tree closure bytes equal the pinned 1988860 blobs, or label default-mode results as working-tree results.
- R6: To exercise the syntax branch (F5), commit the invalid helper into the sandbox first, so the compare passes and `exec_module` raises `SyntaxError`.

## 7. Verification gaps

- Nothing was executed. Every predicted outcome above is a source trace, so the live result of demo-helper-dirty under the current code is not observed.
- The baseline pair was not executed.
- The gate internals and the migrated runner's imports were read only where the caller references them directly.

Trailer: `.ufo/waves/round-20/final/InputCase18.md`, relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`.
