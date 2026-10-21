# InputCase16: `targeted-frozen-dirty` (C2 caller-case falsifier, read-only)

Seat: SoujiR20-2.InputCase16 (leaf, source-only). Pin: 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1 (`cat-file -t` returns `commit`). Sources read only with `git show` and `git ls-tree` at the pin: `tests/fixtures/r20-input-binding.py`, `tools/souji-rev-pin.py`, `census/round-14/run-targeted.py` (applicable caller). Also `ls-tree` of `tests/fixtures/r14-cache-frozen/` and `census/round-14/verification-attempt-1.json`. Not opened, per the ONLY-applicable-caller bound: the other three callers and `census/round-14/run-verification.py`. Nothing was executed, imported, built, or installed. Advisory, author-side only.

STATUS: PARTIAL. `targeted-frozen-dirty` does not establish its required reason or its ordering. Its predicate (rc 2, relative-path substring, empty stdout, no record) accepts M1, a prerequisite refusal that names the same path, and M2, a suite-then-refuse run (conditional on r14). No producer tripwire or clean control is applied to this row. The only targeted baseline witness, `baseline-targeted-wrapper`, cannot pass as written, because its driver bypasses the caller's exit-2 mapping (O1). `run-targeted.py` has no pre-suite input check of its own. The refusal-before-suite property is inherited from `module.resolve_revision()` in the r14 runner, which I did not open.

## Answers

- **Behavioral or wiring?** Behavioral at the subprocess boundary, but only for the tuple (rc, stdout, stderr substring, record absence). It does not observe the refusal class or whether any suite command ran. Closure membership of the frozen file is wiring, taken from the fixture's own static parse.
- **Can a prerequisite refusal masquerade?** Yes (M1). The ordering analogue is M2.
- **Is the input consumed by this caller?** Not by `run-targeted.py`. It never opens or names `tests/fixtures/r14-cache-frozen/*`. The file reaches the caller only through the r14 closure (`module.MEASURED_PATHS` → `resolve_revision()` / `checked_inputs()` → `input_sha256` in the record). Whether a suite command reads it is never exercised, because the designed refusal precedes all commands.
- **Baseline producer witness?** None. The seven `--baseline` pairs contain no targeted frozen pair. The nearest, `baseline-r14-frozen`, exercises the r14 entrypoint, not this caller.

## 1. Entrypoint trace [SOURCE]

- Row invocation (`caller_command` / `caller_refusal`): `python3 -B census/round-14/run-targeted.py --output census/round-20/r20-targeted-frozen-dirty.json`, cwd = sandbox `<tmp>/targeted`, env = `CLEAN_ENV` plus `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` pointing at a decoy repo.
- `run-targeted.py` does no argv parsing. Nothing in that file reads `--output`.
- Import time, outside any `try`: `spec_from_file_location("r14_verify", ROOT/"census/round-14/run-verification.py")` and `exec_module`. A load error here is uncaught and exits 1, not 2.
- `main()` order:
  1. `target = module.output_path()` (r14; unverified).
  2. `module.MEASURED_PATHS = [*module.MEASURED_PATHS, "census/round-14/verification-attempt-1.json"]`.
  3. `revision = module.resolve_revision()`. This is the only pre-run gate in this file.
  4. Hash six working-tree `paths` and `census/round-13/verification.json`.
  5. `TemporaryDirectory` and `git show BASE:tools/souji-census.sh`.
  6. Six `module.run(...)` commands, including `cache-consumer-red-green`, `census-boundary`, `census-legacy-selftest`, `census-shellcheck-warning`.
  7. `inputs_after = module.checked_inputs(revision)`. This is the only post-run gate.
  8. Record write. `inputs_unchanged_during_run=True` is a literal.
- `if __name__ == "__main__":` wraps `main()` in `except (OSError, ValueError, RuntimeError)`, which prints `run-targeted: refused: %s (no record written)` to stderr and raises `SystemExit(2)`. The helper's `Refusal` subclasses `ValueError`, so the designed refusal reaches exit 2 here. No other path returns 2: `main()` returns 0 or 1, and uncaught exceptions exit 1.

## 2. Inert changed byte [SOURCE]

- `inert_suffix` for `.json` is `b" \n"`, appended to `tests/fixtures/r14-cache-frozen/expected.json`. This is JSON whitespace, a semantic no-op, but a byte change. The helper binds bytes (`hashlib.file_digest(..., "sha256")` against blob bytes), so refusal is the correct expected outcome. The mutation design is sound for a byte binding.
- Pinned facts: `expected.json` is blob `15cf46d6…`, 249 bytes. The directory also holds `dependency.txt` (30 B) and `record.json` (231 B). The row mutates one of three members.

## 3. Relevant input closure

- Fixture: `targeted_paths = list(dict.fromkeys([*r14_paths, R14_PRIOR]))`. Runtime: `module.MEASURED_PATHS = [*module.MEASURED_PATHS, prior]`. These agree [SOURCE]. Agreement is conditional on r14 defining `MEASURED_PATHS` as one top-level literal, since `parse_path_list` returns the first top-level assignment and ignores later rebinding [UNVERIFIED].
- `mutation_plan` checks coverage against the fixture's own derived list, not against the caller's runtime value.
- Extras mismatch [SOURCE]: the baseline targeted pair uses extras `[TARGETED, R13_PRIOR]`, while the matrix targeted row uses `[]`. `run-targeted.py` reads `census/round-13/verification.json` and six working-tree files after the revision gate. If any of those are absent from r14's closure, a clean run exits 2 through `FileNotFoundError`, which looks like a refusal. The fixture has no clean control, so nothing would notice [INFERENCE].
- Not pinned [SOURCE]: `expand_closure` reads `--root` working-tree bytes and then commits them as "clean". The row is bound to 1988860 only if `--root` is a clean pinned checkout. Only `--baseline` uses commit bytes (`make_git_sandbox`).

## 4. Predicate: rc 2, no stdout, no output [SOURCE]

`returncode == 2 and "tests/fixtures/r14-cache-frozen/expected.json" in (stdout+stderr) and census/round-20/r20-targeted-frozen-dirty.json absent and stdout == ""`

- rc 2 comes only from the `__main__` mapping (§1).
- The substring matches any text containing the relative path. That includes absolute sandbox paths in OSError messages. This is the weakest link (M1).
- The output-absent check looks at a path the file never reads. The real record path comes from r14's `output_path()` [UNVERIFIED]. The record is written only after the post-run gate, so absence holds for any refusal before that point. The check does not test the property it names.
- Empty stdout holds only if r14's `module.run` captures child output [UNVERIFIED].
- Designed-path prediction [INFERENCE]: `run-targeted: refused: measured inputs differ from <rev> (missing=[] added=[] changed=['tests/fixtures/r14-cache-frozen/expected.json']) (no record written)`. This assumes r14 propagates the helper's message.

## 5. Bounded counterexamples

**M1, prerequisite refusal naming the same path passes.** Source-verified in `tools/souji-rev-pin.py`, with no r14 dependency beyond calling the helper.

- Mutant: in the sandbox, delete `tests/fixtures/r14-cache-frozen/expected.json`, or replace it with a symlink. Keep the row's predicate exactly as written.
- Path through `resolve_durable` → `input_snapshot`:
  - Deletion, file-granular closure: `os.lstat` raises FileNotFoundError inside the `try`. It is re-raised as `Refusal("unreadable measured input: [Errno 2] No such file or directory: '<sandbox>/tests/fixtures/r14-cache-frozen/expected.json'")`.
  - Deletion, directory-granular closure: `missing=['tests/fixtures/r14-cache-frozen/expected.json']`.
  - Symlink: `Refusal("symlink measured input tests/fixtures/r14-cache-frozen/expected.json")`.
- Each is a `ValueError`, so `__main__` yields rc 2, a stderr containing the path, empty stdout, and no record. **Row passes** [INFERENCE]. The required reason, bytes that differ from HEAD (`changed=`), is absent. The predicate cannot tell a missing or unreadable input from a dirty one.

**M2, suite-then-refuse passes.** Conditional on r14's `resolve_revision()` lacking a working-tree comparison [UNVERIFIED].

- Mutant: remove only the pre-run binding, and keep `checked_inputs(revision)` after the six commands. A dirty-input run executes all six `module.run` commands, then refuses on the path: rc 2, path present, stdout empty if `module.run` captures output, no record. **Row passes** [INFERENCE]. The fixture docstring requires refusal "before suite output or a measurement record is produced", and this row cannot observe suite execution. The only mechanism that does is the producer tripwire, which this row does not use.
- Stakes: if r14 currently calls `resolve_durable` with `tree_check=False`, production would already behave like M2, and this row would still pass [INFERENCE].

**Checked, not a masquerade.** A caller that resolves HEAD through an inherited `GIT_DIR` would get the decoy commit. That commit cannot resolve in the sandbox, because the helper's `_env()` strips `GIT_*`. The refusal would then not name the frozen path, and the row would FAIL [INFERENCE]. The decoy detects ambient-environment leaks.

## 6. Baseline producer witness

- None for `targeted-frozen-dirty`. The seven pairs are r13-helper, r13-sources, r13-new-knowledge, r14-helper, r14-frozen (r14 entrypoint), targeted-wrapper (`TARGETED` only), and demo-helper.
- The only targeted pair, `baseline-targeted-wrapper`, cannot pass as written (O1).

## 7. O1: harness defect on the targeted tripwire path [SOURCE]

- `TRIPWIRE_DRIVER`'s targeted branch loads the script under the name `r20_tripwire_targeted` and calls `module.main()`. Because `__name__ != "__main__"`, the exit-2 mapping in `run-targeted.py` never runs.
- On the changed side, the dirty wrapper makes `resolve_revision()` raise `ValueError` [INFERENCE: assumes r14 raises rather than calling `sys.exit`]. The exception reaches the driver's `except BaseException`, which records `status="exception"`, `exit_code=None`, and an empty stderr, because nothing printed the refusal.
- `changed_refused` requires `status in ("exit","return")`, `exit_code == 2`, and `changed_path_named`. None hold, so `baseline-targeted-wrapper` FAILs by construction. `--baseline` therefore cannot be green for the targeted caller.
- Fix shape: the targeted branch must mirror the production `__main__` mapping, printing `run-targeted: refused: …` to stderr and exiting 2 for OSError, ValueError, and RuntimeError. Alternatively, run the script with `run_name="__main__"` behind a hook.

## 8. Consumption

- The frozen file's only effect in this caller is a closure hash through r14 (`input_sha256`). No command in the static `commands` list maps to it. A dirty closure member refuses the whole run, so the caller has no per-input selection policy. The row therefore proves closure binding. It does not prove consumption.

## 9. Unverified dependencies (r14, not opened per bound)

- `resolve_revision()`: does it do the working-tree snapshot? This decides M2 and whether the pre-suite property holds at all.
- `checked_inputs()`: does it compare to the revision and name the path? This sets M2's reason text.
- `output_path()`: does it read argv? This decides whether `--output` is consumed and whether the no-output check addresses the real record.
- `MEASURED_PATHS`: a literal that contains `R14_FROZEN`, the six `paths`, and `census/round-13/verification.json`.
- `run` and `ENV`: `run` captures child output, and `ENV` strips `GIT_*`.
- Whether r14 raises rather than `sys.exit` on refusal (O1 depends on it).

## 10. Proposed changes for L1 (not applied)

1. Replace the substring predicate for targeted rows with the helper's exact refusal shape: `differ from`, `changed=['<path>']`, `missing=[]`, `added=[]`. Treat the deletion and symlink mutants as separate rows that must not pass this one.
2. Run the changed side of `targeted-frozen-dirty` through the producer tripwire, with the `__main__` mapping mirrored (this also fixes O1). Require `status in ("exit","return")`, `exit_code == 2`, and no producer reached.
3. Add an unmutated clean control per caller: producer reached, rc not 2. This proves non-vacuity and exposes missing closure members (§3).
4. Add a targeted red-before pair for `R14_FROZEN`, or document `baseline-r14-frozen` as the shared-closure witness with an explicit reason.
5. Build matrix sandboxes from the pinned commit with `make_git_sandbox`, not from the `--root` working tree.
6. Reconcile the targeted extras: `R13_PRIOR` is in the baseline pair and absent from the matrix.

## Checks not run

- No runtime execution, import, sandbox build, or tests. Every outcome above is source-derived. Predicted outcomes are marked [INFERENCE].
- Installs or updates: none.
