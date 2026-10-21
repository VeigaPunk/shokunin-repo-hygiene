STATUS: PARTIAL — The pinned round-14 caller refuses the `r14-frozen-dirty` mutation at the right point and for the right reason, so this row does not refute the production caller. The oracle that grades the row is not sufficient operability evidence, which blocks an operability PASS until fixed: (1) no fixture row reaches a current caller's success path (`checked_inputs`, the exclusive record write) or runs an unmodified sandbox through a current caller, so a caller that can never write a record still passes C2; (2) the row's pass predicate is a substring test over stdout+stderr, so any exit-2 refusal that names the frozen file passes regardless of reason. Both defects are in `tests/fixtures/r20-input-binding.py`. The production caller and helper need no change for this row.

## Scope and method
- Pinned commit `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` (`git cat-file -t` → `commit`). All source reads via `git show` / `git ls-tree` at that commit.
- Blobs read: `tests/fixtures/r20-input-binding.py` = `ea6efacc623f933c5ef956fe81ecdf49269e892b` (1038 lines); `tools/souji-rev-pin.py` = `8da7da9c2d627d7675976a5f4093f0d8f25d689c` (404 lines); `census/round-14/run-verification.py` = `6b2899be54b517da85a67eb1f670558a8eaad3ee` (179 lines); `tests/fixtures/r14-cache-frozen/expected.json` = `15cf46d63ea390086dd87fe5dfe11b24a2bde4e5` (249 bytes).
- `git ls-tree -r -l` on the 13 `MEASURED_PATHS` entries: every leaf is a `100644`/`100755` blob (no symlinks, no submodules). `tests/fixtures/r14-cache-frozen` holds exactly `dependency.txt`, `expected.json`, `record.json`.
- Executed: only the git reads above and `wc -l` / `cat-file -s`; all returned successfully. No fixture, caller, helper, or cache tool was executed or imported. Other callers and `census/operator-sweep-20261019/` were not read. No installs or updates. No writes outside this report.

## Axes
- A1 refusal correctness of the pinned caller: PASS for this row.
- A2 discrimination (can the predicate fail a wrong caller): WEAK. See CE-2, CE-3.
- A3 success-path coverage (does C2 ever observe a record being written): ABSENT. See CE-1.
- A4 provenance (are the tested bytes the pinned bytes): NOT ENFORCED. See Other findings.

## Applicable caller
The matrix entry `name="r14"`, `script=census/round-14/run-verification.py`, `kind="r14"`, plan item `("frozen-dirty", "tests/fixtures/r14-cache-frozen/expected.json")`. Row id = `"r14" + "-" + "frozen-dirty"`. The `targeted-frozen-dirty` row belongs to `run-targeted.py` and is not traced here.

## Trace
1. Sandbox (`make_sandbox`, under a /var/tmp TemporaryDirectory): `expand_closure` copies the 15 regular files behind the 13 measured entries (12 single files plus the 3 frozen-directory files) from `--root`, runs `git init --initial-branch=main`, commits them, and creates an empty `census/round-20/`.
2. Mutation (`mutate_and_call`): appends `b" \n"` (`inert_suffix` for `.json`) to `tests/fixtures/r14-cache-frozen/expected.json`, uncommitted. This is JSON-equivalent but byte-different, which is the right mutation for a byte-exact binding. It is restored byte-exactly in `finally`.
3. Invocation (`caller_command`, `caller_refusal`): `python3 -B census/round-14/run-verification.py --output census/round-20/r20-r14-frozen-dirty.json`, cwd = sandbox, env = `CLEAN_ENV` plus `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE` pointing at an unrelated decoy repository.
4. Pinned caller path:
   a. `main()` → `output_path()`: validates `census/round-N/<new>.json`; the file is absent and the parent exists. Nothing is written.
   b. `resolve_revision()`: `git rev-parse HEAD` (outside its `try`); the helper's working bytes equal `HEAD:tools/souji-rev-pin.py`; helper loaded; `resolve_durable(ROOT, HEAD, MEASURED_PATHS)` passes (40-hex, resolves, ancestor of `refs/heads/main`).
   c. Inside `resolve_durable`, `input_snapshot` compares committed blobs (`ls-tree -r -z --full-tree`) against the working tree (`os.walk` of the directory entry) and raises `Refusal("measured inputs differ from <HEAD> (missing=[] added=[] changed=['tests/fixtures/r14-cache-frozen/expected.json'])")`.
   d. `Refusal` subclasses `ValueError`; `resolve_revision` catches it, writes `run-verification: refused: ... (no record written)` to stderr, and raises `SystemExit(2)`. The `__main__` handler does not catch `SystemExit`, so the process exits 2.
   e. Never reached: `commands`/`run` (the only stdout producer), `checked_inputs`, and `target.open("x")`.
   f. The caller's `ENV` and the helper's `_env()` both strip every `GIT_*` variable, so the decoy has no effect.
5. Predicate (non-demo branch of `caller_refusal`): `returncode == 2 and "tests/fixtures/r14-cache-frozen/expected.json" in stdout+stderr and output_absent and stdout == ""`. The pinned result satisfies all four, so the row PASSes.

## Answers to the assigned questions
- Behavioral or wiring? Behavioral at the process boundary: a real subprocess, real Git objects, a real byte change, the real helper. The pass criterion is refusal-only and text-based, and the row never observes the caller accepting anything.
- Can a prerequisite refusal masquerade as the required reason? In the pinned caller, prerequisite refusals (helper differs, HEAD not durable, output path invalid, git failure) name no frozen file, so they FAIL the row instead of passing it. The masquerade channel is the snapshot itself: any refusal that names the full file path passes, including `missing=[...]`, `added=[...]`, `symlink measured input <file>`, `nonregular ... input <file>`, and `unreadable measured input: <OSError carrying the absolute path>`. The predicate cannot separate `changed` from these. The pinned inert append cannot reach them, so the pinned PASS is not a masquerade. A directory-level refusal (`symlink measured directory tests/fixtures/r14-cache-frozen`) lacks the file path and fails the row.
- Is the input consumed by this caller? Not directly. The caller never opens `expected.json`. It binds the whole `tests/fixtures/r14-cache-frozen` directory by hash at start, re-hashes it in `checked_inputs` before the record write, and passes the directory to the child step `tools/souji-evidence-cache.py --frozen`. [INFERENCE: that child reads `expected.json`; the tool was not read.] The row therefore proves refusal before consumption. It does not show what the child reads, and the closure is the caller's declared list, not an observed read set.
- Exit 2 / no stdout / no output: satisfied as traced. The no-output check covers only the named output path; nothing checks the rest of the tree.
- Baseline producer witness: `baseline-r14-frozen` is the only frozen producer witness. The tripwire driver replaces `run` with a raiser of `ProducerReached("baseline-r14-frozen")`. `run` is first reached after the snapshot, so `status == "producer"` shows the old caller's resolve step accepted the tree, which holds only when the frozen directory is not in the old caller's measured set. It is a sound witness, but baseline-only and old-caller-only. The driver does not assert that `run` exists before replacing it; if it does not, the old `main()` runs real suite commands in the sandbox and the pair FAILs. It cannot falsely PASS.

## Counterexamples (bounded)
- CE-1 (success-path blind spot; realistic). Make `checked_inputs` raise `Refusal` unconditionally in the pinned caller. The r14 dirty rows still refuse in `resolve_revision` with identical outcomes, and the r14 baseline pair still stops at `run`. The r14 rows keep their outcomes and C2 stays green while the caller can never write a record. No fixture row reaches the end of `main()`: every PASSing matrix row requires empty stdout, and `run` prints on every return, so no PASSing row completed a suite command.
- CE-2 (refusal-only blind spot). A caller wrapper that prints its file-level closure to stderr and exits 2 unconditionally passes `r14-frozen-dirty` (exit 2, path present, stdout empty, no output), and passes every other r14 dirty row. No row runs an unmodified sandbox through a current caller: every `caller_refusal` and `invoke_tripwire` call operates on a mutated tree (baseline pairs mutate both sides), and `helper_controls` exercises only the helper API on the r13 closure.
- CE-3 (reason blind spot; hypothetical plan variant, not in the pinned fixture). Replace `expected.json` with a symlink, or delete it, instead of appending a byte. The caller refuses with `symlink measured input tests/fixtures/r14-cache-frozen/expected.json` (or `missing=[...]`); the substring predicate passes, and the row still reads `frozen-dirty`.

## Other findings (lower severity)
- Provenance. `--root` defaults to the lane working tree. Both the closure (`parse_path_list`, `expand_closure`) and the caller bytes come from it. The fixture never checks that root HEAD equals `1988860…` or that root is clean, and prints no digest or HEAD. The row attests to whatever bytes root held when it ran.
- Exit-code overlap. `summary(blocked=True)` returns 2, the same code as a caller refusal. A blocked run cannot add a row, so it cannot pass `r14-frozen-dirty`, but the exit code alone does not separate "blocked" from "refused".
- Out-of-row closure. The caller's `sources-contract` step runs `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` against the parent corpus, which is outside `MEASURED_PATHS` (disclosed in `input_scope`). `run_historical_counters` executes `census/round-13/count-claims.py` and `census/round-14/count-claims.py` with `cwd=--root`. I did not read those scripts, so whether they write is unverified.

## Verified clean
- Pinned caller: no path lets dirty frozen bytes reach `run`, stdout, or the output path.
- `input_snapshot` covers all three frozen files, including untracked and ignored files (`os.walk` without gitignore), and refuses symlinks at each path component and at leaves.
- The row's predicate requires the full file path, so directory-level refusals and refusals about other files cannot pass it.
- Fixture mutations apply only inside its /var/tmp sandboxes and are restored in `finally`.

## Recommended fixes (fixture only; for L1)
1. Per caller, add `<name>-clean-accepted`: an unmodified sandbox run through the existing tripwire driver. Expect `status == "producer"`, witness `<name>-clean-accepted`, and output absent.
2. Add a success-path row: replace `run` with a non-executing stub returning matched result dicts of the same shape. Expect exit 0, the exact output file present, and `measured_commit == HEAD`. This exercises `checked_inputs` and the exclusive write without running suite code.
3. Add a post-run row: the same stub appends a byte to `expected.json` before returning. Expect exit 2, the `measured input set changed` refusal, and no output file.
4. Tighten the frozen predicate to `"changed=['<path>']" in combined and "missing=[] added=[]" in combined`, and apply the same shape to other single-file dirty rows.
5. Record root HEAD and `git status --porcelain` for the closure in the SUMMARY line, or refuse in pinned mode unless root HEAD equals the pin.

## Checks for L1 (not run here)
- `python3 tests/fixtures/r20-input-binding.py --root <clean checkout at 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1>`. Expect `r14-frozen-dirty` PASS, matching this trace. After fixes 1–3, expect the new rows to PASS, and a deliberately broken `checked_inputs` to FAIL.

Advisory author-side report; not non-author closure or promotion. No `[x]` marks.
