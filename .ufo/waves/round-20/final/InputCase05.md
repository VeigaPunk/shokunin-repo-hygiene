# InputCase05: `r13-sources-dirty` (C2 caller-case falsifier, source-only)

Author-side advisory. Not non-author closure or promotion. No SHONEN marks.
Judged on: operability.

## Verdict

Source agreement. I found no blocking counterexample for `r13-sources-dirty` at build pin `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. The case is a behavioral refusal oracle for the round-13 runner's `corpus/SOURCES.md` binding. Its baseline pair (`baseline-r13-sources`, baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`) is a valid red-before witness. Four non-blocking residuals are in section 9.

## Scope and method

- Attacked entry: `mutation_plan("r13")` → `("sources-dirty", "corpus/SOURCES.md", False)` in `tests/fixtures/r20-input-binding.py`, which yields case id `r13-sources-dirty`. Applicable caller only: `census/round-13/run-verification.py`.
- Reads: `git -C <lane> show <pin>:<named path>` for the fixture, `tools/souji-rev-pin.py`, the round-13 runner, `corpus/SOURCES.md` (the attacked input), and the baseline round-13 runner and helper. Also `git ls-tree --name-only` and `git cat-file -e/-t` on named paths. All exited 0.
- Pinned sha256: fixture `160f92c40c6ed62059c1a51f8323eaba7777669bf1cb40bd68c24e2b7d310aef`; `tools/souji-rev-pin.py` `d3e9111b66f17242124df97db0327195c75a5c44252566d2130ff38c5755f32e`; `census/round-13/run-verification.py` `c122d70a2283017b7428524ccf768e9841e7e9ca08099cef7a01897d004760b8`; `corpus/SOURCES.md` `4bda35d5d5a78cd684a429093778adc1af31a41c3b63e78589f7ffbd4c524072`.
- Not executed: no fixture run, no caller run, no import, no working-tree read, no install or update (none needed). No verification was run.

## 1. Entrypoint trace (1988860)

The fixture runs the round-13 runner with cwd set to a sandbox repo under `/var/tmp/souji-r20-input-binding-*/r13`. Its env is `CLEAN_ENV` plus `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` pointing at a decoy repository:

`python3 -B census/round-13/run-verification.py --round 20 --output census/round-20/r20-r13-sources-dirty.json --retry-failed --previous census/round-13/verification.json`

Caller order:
1. `main()` parses arguments, then `validate_output(20, …)`. `closed_round_floor()` returns 20 (the fixture creates `census/round-20/`), so the round is not closed. Path, parent and name checks pass. Nothing is printed and nothing is written.
2. `--retry-failed` → `validate_previous()` accepts the copied `census/round-13/verification.json`.
3. `execute()` sets `PREVIOUS_SOURCE`, then calls `resolve_revision()`. That happens before `json.loads(previous)` and before any `run()`. Because the case uses `--retry-failed`, it also shows the binding precedes prior-result retention.
4. `resolve_revision()` compares the committed and working bytes of `tools/souji-rev-pin.py` (equal in the sandbox by construction), builds `INPUT_PATHS` from `MEASURED_PATHS` plus the previous file, and calls `resolve_durable()`. That checks refs/heads/main reachability, then its internal `input_snapshot()`.
5. `input_snapshot()` finds the committed blob sha ≠ the working sha for `corpus/SOURCES.md` and raises `Refusal("measured inputs differ from <rev> (missing=[] added=[] changed=['corpus/SOURCES.md'])")`.
6. `resolve_revision()` catches it (`ValueError`), prints `run-verification: refused: … (no record written)` to stderr, and raises `SystemExit(2)`. `SystemExit` is not an `Exception`, so `main()`'s generic handler (also exit 2) is bypassed.

The predicate `returncode == 2 and specific and output_absent and no_suite_output` holds by source. Exit is 2, stdout is empty, stderr names `corpus/SOURCES.md`, and the only `open("x")` is at the end of `execute()`, which is never reached.

## 2. Inert changed byte

`inert_suffix(".md")` appends `\n<!-- inert r20 input-binding mutation -->\n`. The census parser splits on `|` and needs 13 cells with an `S\d+` id, so this line has one cell. The census counts are unchanged and only the byte binding can refuse. That makes this a pure binding oracle. The `finally` block restores the file, so no state leaks into later cases.

## 3. Input closure

- `corpus/SOURCES.md` is a literal in the 1988860 round-13 `MEASURED_PATHS`, so `mutation_plan`'s `covered_by_measured` guard passes. Removing it from the caller would make the fixture block (`FixturePrerequisite`), not pass.
- Pre-mutation guards (`is_symlink`, `is_file`, `read_bytes`) mean the attacked file is a regular, readable, non-symlink file.
- All 23 round-13 closure entries (22 `MEASURED_PATHS` plus the `--previous` extra) exist at 1988860 (`ls-tree`).

## 4. Consumption

- Static: `execute()` reads `ROOT/"corpus/SOURCES.md"` into `census` (rows, tiers, statuses) and writes it to the record as `sources`. The record's `input_sha256` also carries the SOURCES digest from `input_snapshot`. The input is therefore consumed and bound at the start and end snapshots.
- Not behaviorally exercised: the case refuses before any producer runs, and the baseline witness stops at the first producer. Consumption rests on source reading only.

## 5. Behavioral or wiring?

- Refusal: behavioral. A real subprocess runs the entrypoint on a mutated synthetic repository, and the refusal comes from the caller's own `input_snapshot`.
- Input selection: partly wiring. The name is hard-coded in the fixture and must appear in the caller's literal, otherwise the fixture blocks.
- Decoy: `GIT_DIR` points at another repository. If ambient `GIT_*` were honored, the refusal text would not name `corpus/SOURCES.md`, so the case would FAIL. It therefore also discriminates repository-selection redirection.

## 6. Masquerade analysis

The predicate is path presence (`changed_path in stdout+stderr`) plus exit 2, empty stdout and no output. The SOURCES-naming exit-2 routes at 1988860 are:
- `unreadable measured input`, `symlink`/`nonregular measured input`, or `missing`/`added` for SOURCES. These would satisfy the predicate. They are not reachable here, because the pre-mutation guards and the symlink-free sandbox rule them out.
- `could-not-evaluate` from `main()` (exit 2). It fires only after `resolve_revision()` passes, so it is unreachable in a refusal case.
- `validate_output` and `validate_previous` messages name only the output or previous path. Helper refusals (`does not resolve`, `not reachable`, `differs from measured commit`) do not name SOURCES, so they FAIL rather than masquerade.

Conclusion: no reachable masquerade for this case. The predicate is still weaker than the claim, and exit 2 is shared with the generic `could-not-evaluate` path, so only the message text discriminates.

## 7. Baseline producer witness (12516f7)

- The baseline round-13 `MEASURED_PATHS` has 12 entries and omits `corpus/SOURCES.md`, the helper and the knowledge directory. The fixture places SOURCES in the baseline sandbox as an extra and mutates it there. The baseline runner's own binding does not include it.
- Baseline `resolve_revision()` calls the baseline helper's `resolve_durable(…, MEASURED_PATHS)`, which runs a tracked-path `git diff --quiet <rev> -- <12 paths>`. SOURCES is not among those paths, so the check passes.
- Baseline `execute()` reaches `results.append(run("evidence-selftest", …))` first. The driver replaces `run` with a producer that raises `ProducerReached`, a `BaseException` that `except Exception` does not catch. Result: `status == "producer"`, witness equal to the case id, output absent.
- Baseline `execute()` still reads SOURCES after the producers (rows → `sources`), so a baseline record would embed unbound SOURCES bytes. That is the defect the case guards.
- The changed side refuses as in section 1.
- Prerequisites: all 23 round-13 closure entries plus `tests/fixtures/r13-cert-frozen/expected.json` exist at 12516f7 (`ls-tree`), and the baseline runner, helper and SOURCES exist (`cat-file`). The pair is runnable, not blocked.
- The witness cannot be faked: `baseline_reached` requires `status == "producer"`, so any refusal or exception on the baseline side fails the pair.

## 8. Counterexample attempts that failed

- Remove SOURCES from the caller's literal: the fixture blocks, with no false pass.
- Ambient `GIT_DIR` honored: the case FAILs, with no false pass.
- Unreadable, symlinked or deleted SOURCES: blocked by pre-checks, or FAIL.
- Malformed `--previous` JSON: not parsed until after the binding.
- Round-closed or output-exists refusals: name other paths, so FAIL.
- Inert suffix: census-neutral, so the refusal is attributable to the binding alone.

## 9. Residuals (non-blocking; L1 decision)

R1. Tighten the predicate to the exact deterministic text `missing=[] added=[] changed=['corpus/SOURCES.md']`. That removes every SOURCES-naming masquerade route, including future ones, and attributes the refusal to the single mutation.

R2. Endpoint-only binding (bounded counterexample). The census is read mid-run, after every `run()` call. The bound digests are taken only at start (`INPUT_SHA256`) and end (`inputs_after`). A concurrent writer that sets SOURCES to bytes B and restores the committed bytes A before the end snapshot gets no refusal. `sources` then derives from B, while the record claims `input_sha256[SOURCES] = sha(A)` and carries the literal `inputs_unchanged_during_run=True`. The helper docstring excludes filesystem races, but the record flag name overclaims. Fix options: read SOURCES once at the start snapshot and derive the census from those bytes, or rename the flag to `inputs_unchanged_at_endpoints`. The static dirty case is refused before any read, so this does not affect `r13-sources-dirty`.

R3. Root dependence. Closure bytes come from `--root`'s working tree (`expand_closure` and the `make_overlay_sandbox` overlays); `git show` is used only for the baseline. The verdict covers pinned bytes only if the fixture runs from a clean checkout at 1988860. Not verified here.

R4. Over-declaration, unverified. `LOG.md`, `census/round-10/cert-16.json` and `tools/cand-census-03.sh` are declared but not read directly by the caller's own code. If no measured subcommand reads them, editing them refuses the round-13 runner. L1 should confirm.

## 10. Checks for L1 (not executed here)

- From a clean checkout at 1988860: `python3 tests/fixtures/r20-input-binding.py --baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. Expect `CASE pass r13-sources-dirty`, `CASE pass baseline-r13-sources` and `INVENTORY exact`.
- If R1 is adopted, the `r13-sources-dirty` detail should contain `changed=['corpus/SOURCES.md']`.
