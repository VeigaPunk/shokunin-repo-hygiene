# InputCase06: `r13-admitted-knowledge-dirty` (C2 caller-case falsifier)

Pinned source: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Read-only, source-only. Sources were read only through `git show`, `git ls-tree -r --name-only`, and `git cat-file -t` on the pinned commit. Nothing was executed, imported, built, or installed.

**Result:** Source agreement. For the pinned caller, the case reaches the content-binding refusal before any suite output or measurement record: exit 2, changed path named on stderr, stdout empty, output absent. I found no blocking defect, so there is no `STATUS: PARTIAL`. Section 7 gives one bounded counterexample showing the predicate is not reason-specific. The gaps in Sections 8 and 10 are non-blocking.

## 1. Applicable caller

- `mutate_and_call` names each case `name + "-" + case_name`. `mutation_plan` adds `admitted-knowledge-dirty` only inside `if name == "r13"`. The r13 spec in `main` is `{"name": "r13", "script": ROUND13, "kind": "r13", ...}`.
- Applicable caller: `census/round-13/run-verification.py`. The r14, targeted, and demo callers do not generate this case and were not read.

## 2. Entrypoint trace (`census/round-13/run-verification.py`)

1. Invocation from `caller_command`: `python3 -B census/round-13/run-verification.py --round 20 --output census/round-20/r20-r13-admitted-knowledge-dirty.json --retry-failed --previous census/round-13/verification.json`. Working directory is the sandbox. Environment is `CLEAN_ENV` plus a decoy `GIT_DIR`, `GIT_WORK_TREE`, and `GIT_INDEX_FILE`.
2. `main()`: `validate_output(20, ...)` passes (sandbox has `census/round-20`, floor is 20, name is a new `.json`). `validate_previous(...)` passes (regular file, not a symlink).
3. `execute()` sets `PREVIOUS_SOURCE = "census/round-13/verification.json"` and calls `resolve_revision()`.
4. `resolve_revision()`: `head = git("rev-parse", "HEAD")` (`ENV` drops ambient `GIT_*`). Helper bytes must equal `git show head:tools/souji-rev-pin.py`. `INPUT_PATHS = MEASURED_PATHS + [PREVIOUS_SOURCE]`. `resolve_durable` passes (durable through `refs/heads/main`). `input_snapshot` then finds a content mismatch and raises `Refusal`, a `ValueError` subclass.
5. The `except (OSError, ValueError, ...)` handler runs `print("run-verification: refused: %s (no record written)", file=sys.stderr)` and then `raise SystemExit(2)`. `SystemExit` is not an `Exception`, so `main`'s `except Exception` does not rewrite it.
6. Expected stderr, from the helper's message format: `run-verification: refused: measured inputs differ from <HEAD> (missing=[] added=[] changed=['corpus/knowledge/dupe-finders-detect-then-act.md']) (no record written)`.

## 3. Inert changed byte

- Target from `choose_existing_admitted(root)`: the first sorted `corpus/knowledge/*.md` whose first three lines begin `source:`, `verified-at:`, `recheck:`, and that does not contain `## Admission status — HELD`. At the pin, the first sorted file is `dupe-finders-detect-then-act.md`. Its first three lines match, and it has no HELD heading. Selected target: `corpus/knowledge/dupe-finders-detect-then-act.md`. This assumes the working tree matches the pin for that file.
- Mutation: append `\n<!-- inert r20 input-binding mutation -->\n` (the `.md` branch of `inert_suffix`). The header lines are unchanged, so the caller's admitted classification does not change. Only bytes differ. The original bytes are restored in `finally`.

## 4. Relevant input closure

- r13 `MEASURED_PATHS` has 22 entries. It includes the directory `corpus/knowledge`, `corpus/SOURCES.md`, `tools/souji-rev-pin.py`, `census/round-13/run-verification.py`, the seven `tools/souji-*` artifacts, `LOG.md`, and others.
- The fixture closure is the same list plus `census/round-13/verification.json`. As a set, it equals the caller's `INPUT_PATHS`.
- Pinned `corpus/knowledge` contains eight `*.md` files and `obsidian-ledger.tsv`. All nine lie inside the bound directory.

## 5. Consumption

- Consumed: `execute()` reads `(ROOT / "corpus/knowledge").glob("*.md")` (non-recursive) and writes `admitted_entries` into the record. The consumed set is a subset of the bound set.
- Bound twice: before the suite in `resolve_revision`, and after the suite through `inputs_after != INPUT_SHA256`, which raises `Refusal` before `output.open("x")`.
- Over-bound: `obsidian-ledger.tsv` and `LOG.md` lie inside the bound set but this file does not read them. Edits to either block this runner.
- Direct reads not covered by the closure:
  - `closed_round_floor()` lists `census/` and reads its `round-N` directory names. This is a policy input, not a measured one. Changing it can only cause a refusal, which is fail-closed. It is not recorded.
  - `os.environ` is read. The record declares this as unattested (`input_scope`).
- `git show BASE:tools/souji-quarantine.sh` reads an immutable commit object, so it needs no binding.

## 6. Predicate (`caller_refusal`)

`returncode == 2 and changed_path in (stdout + stderr) and output_absent and stdout == ""`

- Exit 2: `SystemExit(2)`. Holds.
- Path named: `changed=[...]`. Holds.
- Stdout empty: the refusal writes only to stderr. Suite lines (`name: exit=...`) come only after `resolve_revision`. Holds.
- Output absent: `open("x")` is reached only after the suite. Holds.

The predicate holds for the pinned caller.

## 7. Behavioral or wiring; masquerade

- Behavioral: the case runs the real entrypoint, the real helper, and real git objects in an isolated repository. A caller that did not bind the admitted directory would reach the suite and print to stdout, failing the predicate. So the case discriminates against a non-binding caller.
- Wiring component: the refusal fires because `corpus/knowledge` is declared in `MEASURED_PATHS`. The case proves enforcement of the declared closure. It does not prove that the declared closure equals the consumed reads.
- Masquerade in the current matrix: not reachable. Pre-run refusals that do not name the admitted path (`validate_output`, `validate_previous`, helper-bytes mismatch, `git rev-parse` `CalledProcessError` reported as `could-not-evaluate`) produce FAIL, not PASS. Only `input_snapshot` refusals name the path. The fixture's mutation (append to a committed, readable, regular file) reaches only the `changed=` branch.
- Bounded counterexample (source-derived, not executed): replace the sandbox copy of `corpus/knowledge/dupe-finders-detect-then-act.md` with a symlink to any file. `input_snapshot.capture()` raises `Refusal("symlink measured input corpus/knowledge/dupe-finders-detect-then-act.md")`. The caller exits 2, prints that path to stderr, leaves stdout empty, and creates no output. The predicate PASSes, yet the byte-binding branch never ran. `chmod 000` produces `unreadable measured input: ... corpus/knowledge/dupe-finders-detect-then-act.md` with the same pass.
- Clean state: the fixture has no caller-level clean run. The helper-level `helper-input-snapshot-clean` runs `input_snapshot` over the identical r13 closure (the `helper-controls` sandbox, `r13_paths + r13_extras`). A clean-state refusal naming the path would appear as a separate FAIL and the run would exit 1. It cannot pass silently.

## 8. Baseline producer witness and coverage gaps

- Baseline witness: none. The seven `BASELINE_PAIR_CASE_IDS` are `baseline-r13-helper`, `baseline-r13-sources`, `baseline-r13-new-knowledge`, `baseline-r14-helper`, `baseline-r14-frozen`, `baseline-targeted-wrapper`, and `baseline-demo-helper`. None covers admitted knowledge. No clean tripwire runs against the current caller either.
- Consequence: the case shows that the current caller refuses. It does not show that the R19 caller would have run the suite on this input. The r20 helper docstring describes the new capability as "additions and omissions", so modification of a tracked admitted entry may already have been refused by R19. [INFERENCE: the baseline commit is outside the pinned-commit read rule and was not inspected.] Treat this case as a regression guard unless L1 checks the baseline.
- Omission coverage: no case in any caller deletes a measured input, although the helper has a `missing=` branch and its docstring claims omissions. For this file, deleting the admitted entry would refuse with `missing=['corpus/knowledge/dupe-finders-detect-then-act.md']`, but nothing tests that.
- HELD entries: a dirty HELD file is refused by the same directory binding, but the matrix does not exercise it.
- Closure completeness: transitive reads by suite children are not bound by the pre-run snapshot. The fixture cannot show completeness. [INFERENCE: suite sources were not read.]

## 9. Operability

- The admitted-entry binding needs only `git` and lane-local files. The pre-run refusal does not invoke shellcheck or the external `sources-census.sh`.
- Deterministic: the chooser sorts its candidates, and the case refuses before the suite, so its outcome does not depend on suite timing.
- `choose_existing_admitted` can raise `UnicodeDecodeError`, which is not `FixturePrerequisite`, when a non-UTF-8 `*.md` sorts before the first admitted entry. That escapes the prerequisite handler as a traceback. Not triggered at the pin.
- Regression mode: if a caller proceeds, `subprocess.run(timeout=90)` kills only the caller. Suite children started with `start_new_session=True` can outlive it and race the restore. The case still FAILs (fail-closed). [INFERENCE about process lifetime; not executed.]
- Directory-granular binding means an edit to `LOG.md` or `obsidian-ledger.tsv` forces a commit before any run. This is a design cost and is untested.
- Out-of-scope nit: `admitted_entries` comes from unsorted `Path.glob`, so record order depends on the filesystem.

## 10. Recommended edits (not applied; read-only seat)

1. Make the predicate reason-specific. Require `"changed=['%s']" % relative` and `"measured inputs differ from"` in the combined output. The symlink counterexample would then FAIL.
2. Add an `admitted-knowledge-deleted` case that expects `missing=['<path>']`.
3. Optional: add a baseline pair for admitted modification, but only if L1 finds that R19 bound directory contents.

## 11. Verification performed

- Executed: none. No builds, tests, or runtime.
- Read-only git on the pin: `git show` for the fixture, the helper, the r13 caller, and `corpus/knowledge/dupe-finders-detect-then-act.md`. `git ls-tree -r --name-only` for `corpus/knowledge`, `census/round-13/verification.json`, and `tests/fixtures/r13-cert-frozen`. `git cat-file -t 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` returned `commit`.
- Not read: the r14 `run-verification.py`, `run-targeted.py`, and `cache-demonstration.py` (not applicable to this case). Baseline `12516f7bcdd5b165e5ee208d44a38d63b5bd5812` (outside the pinned-commit rule).
- Installs: none. Writes: this report only.

Path (relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`): `.ufo/waves/round-20/final/InputCase06.md`
