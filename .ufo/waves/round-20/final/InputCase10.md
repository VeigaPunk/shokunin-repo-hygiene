STATUS: PARTIAL — `r14-helper-syntax-invalid` does not establish its named reason. Source trace predicts the pinned caller satisfies this row only through the helper byte-equality gate, which `r14-helper-dirty` also exercises; the syntax-parse branch is never reached. The row predicate accepts any exit-2 refusal that names `tools/souji-rev-pin.py`, including a Git-lookup failure, and no baseline producer witness exists for it. The pinned caller refuses correctly for this input; the defect is in the falsifier row's label, predicate and witness coverage. Nothing was executed.

# Scope and method
- Pinned reads, all via `git show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<path>` (exit 0): `tests/fixtures/r20-input-binding.py`, `tools/souji-rev-pin.py`, `census/round-14/run-verification.py`. `rev-parse --verify` of the pin returned the full 40-hex ID. The fixture's `r14` spec is the only caller bound to `r14-*` rows, so the other three callers were not opened.
- Baseline, read-only: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812:census/round-14/run-verification.py` (exit 0); `cat-file -t 12516f7…:tools/souji-rev-pin.py` → `blob`.
- No code imported or run; no builds, tests, sandboxes or clones. One web search (CPython `SyntaxError` text formatting).
- Installs or updates: none.

# 1. Entrypoint (traced)
- Fixture `caller_command`, kind `r14`: `python3 -B census/round-14/run-verification.py --output census/round-20/r20-r14-helper-syntax-invalid.json`, cwd = synthetic repo. Env = `CLEAN_ENV` plus ambient `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` pointing at a decoy repo.
- Caller: `__main__` wrapper → `main()` → `output_path()` (validates `census/round-N/*.json`, parent exists, target absent) → `resolve_revision()`. Only after a successful gate do `resolve_durable`, `input_snapshot`, suite `run()` calls and the final `target.open("x")` execute.
- `resolve_revision()` order:
  1. `head = git("rev-parse", "HEAD")`, outside any `try`.
  2. In `try`: symlink / `is_file` check → `committed = git show head:tools/souji-rev-pin.py` → `if helper.read_bytes() != committed: raise ValueError("tools/souji-rev-pin.py differs from measured commit")`.
  3. Only after that: `spec.loader.exec_module(helper)`, `resolve_durable`, `input_snapshot`.
  4. `except (OSError, ValueError, SyntaxError, ImportError, CalledProcessError)` → stderr `run-verification: refused: %s (no record written)` → `SystemExit(2)`.
- Outer `__main__` wrapper passes `SystemExit` through.

# 2. Changed byte
- `mutate_and_call(..., invalid_syntax=True)` appends `b"\ndef r20_invalid(:\n"` to the sandbox copy of `tools/souji-rev-pin.py` after the clean commit; restored in `finally`.
- Not inert: it breaks parsing. This contradicts the fixture docstring ("inert comment/whitespace mutation"). Dirty rows use `inert_suffix`, a `# inert r20 input-binding mutation` comment.
- For this caller the byte gate runs before parsing, so the changed bytes are never parsed or imported. The refusal text is the same `ValueError` that `r14-helper-dirty` (comment appended) produces.

# 3. Input closure
- r14 `MEASURED_PATHS` contains `tools/souji-rev-pin.py`; `mutation_plan` asserts coverage via `covered_by_measured`. Closure requirement satisfied.
- Inputs reached on this row's path: the entry script (copied into the sandbox, so `ROOT` resolves to the sandbox), the sandbox helper bytes via `read_bytes`, and the sandbox HEAD blob via `git show`. Nothing else in the closure is reached.
- Consumption is byte-level only. This row never consumes the helper's syntax.
- Fixture caveat: closure bytes and `MEASURED_PATHS` are read from the `--root` working tree (`parse_path_list(root, …)`, `expand_closure(root, …)`), not from the pin. The row is pin-bound only when `--root` is a clean checkout at 1988860.

# 4. Predicate (`caller_refusal`, non-demo branch)
- PASS iff `returncode == 2` AND `"tools/souji-rev-pin.py" in stdout+stderr` AND the output file is absent AND `stdout == ""`.
- On the byte-gate refusal, stdout is never written, and the output file is written only at the end of `main()`. Source trace predicts all four conditions hold (not executed).
- The predicate does not check message text, exception class or refusal branch. Exit 2 is also produced by the outer wrapper for other `ValueError`s; the path check is what narrows it.

# 5. Can a prerequisite refusal masquerade?
- Yes, via Git. `CalledProcessError` from `git show <rev>:tools/souji-rev-pin.py` is caught by the same tuple, and its `str()` embeds the argv containing `tools/souji-rev-pin.py`. Exit 2 plus the path makes the row pass. Triggers: HEAD lacks the helper, or an ambient `GIT_DIR` redirects git. Today the `ENV` filter (drops every `GIT_*` key) blocks the redirect, and the fixture commits the helper, so neither fires.
- Other prerequisite refusals (`output_path`, `rev-parse HEAD`, durable-ref refusal, missing `census/round-20`) do not name the helper, so they fail the row correctly. The fixture creates `census/round-20`, so that case does not arise.
- The `nonregular revision helper tools/souji-rev-pin.py` message also names the path; it is unreachable for this row.

# 6. Behavioral or wiring?
- Behavioral at the process boundary: runs the real caller in a synthetic repo with a decoy ambient repo, and observes exit, stdout and file creation.
- Not behavioral about reason: any regression that keeps exit 2 and the path substring is invisible to this row.
- `helper-ambient-GIT_DIR-redirection` exercises the helper API, not this caller's `ENV` filter. No helper row covers the caller's filter.

# 7. Baseline producer witness
- None for this row. The `--baseline` pairs with helper inputs cover only `baseline-r14-helper`, which appends an inert comment. `TRIPWIRE_DRIVER` reports `producer` only when the pair's own ID reaches `run`.
- Pinned baseline `12516f7` r14 caller: no byte gate, and `resolve_revision()` runs `spec.loader.exec_module(module)` before `head = git(...)` and outside any `try`. A parse-invalid helper would therefore make the baseline exit 1 with an uncaught `SyntaxError` [INFERENCE from source; not executed]. A true red-before for the exit-2 predicate exists in source, but no pair records it, and the harness would report `exception`/`SyntaxError`, not `producer`.

# 8. Bounded counterexample (M3)
- Mutant, in a private copy of `census/round-14/run-verification.py`: replace the `ENV` comprehension that drops `GIT_*` keys with `ENV = dict(os.environ)`.
- Predicted (source trace, not executed): with the decoy `GIT_DIR` active, `git rev-parse HEAD` returns the decoy HEAD; `git show <decoy-HEAD>:tools/souji-rev-pin.py` fails with exit 128 [INFERENCE: path absent in decoy]; the `CalledProcessError` text embeds `tools/souji-rev-pin.py`; result is exit 2, empty stdout, no output.
- Result: `r14-helper-syntax-invalid` and `r14-helper-dirty` PASS despite broken ambient isolation. `r14-frozen-dirty`, `r14-sources-dirty` and `r14-wrapper-dirty` FAIL, because their paths are not named. Matrix-level detection survives only through those sibling rows.
- Secondary, same predicate weakness: delete only the byte gate and keep the import inside `try`. Predicted: `r14-helper-dirty` PASSES (via `input_snapshot`'s `changed=['tools/souji-rev-pin.py']`), while `r14-helper-syntax-invalid` FAILS, because CPython renders `SyntaxError` text with the basename only [INFERENCE: `SyntaxError_str` uses `my_basename`; search-indexed at https://github.com/python/cpython/blob/main/Objects/exceptions.c, not line-verified here]. A correct syntax refusal would fail this row.

# 9. Fix directions for L1 (not applied; read-only seat)
1. Make the syntax row reach its branch: commit the syntax-invalid helper into the sandbox HEAD, with no dirty mutation. The byte gate then passes, `exec_module` raises inside `try`, and the caller exits 2. Assert exit 2, `invalid syntax` text, empty stdout and no output. The pinned baseline's exit 1 then gives a real red-before.
2. Tighten dirty-helper rows to the exact reason (`differs from measured commit`) and reject Git-failure text (`Command '[`).
3. Add a caller-level ambient-`GIT_DIR` row whose predicate requires the byte-gate message, not a path substring.
4. Correct the docstring: `*-syntax-invalid` rows are not inert.
5. Pin the fixture to a committed root (pinned clone), or state the working-tree dependency.

# 10. Verdict
- Operable: deterministic, with no environment dependency beyond git and python; the row runs.
- Not discriminating for its name: it proves exit 2, empty stdout and no output for a changed helper, not syntax-invalid refusal. Keep it PARTIAL until fix 1 lands.
