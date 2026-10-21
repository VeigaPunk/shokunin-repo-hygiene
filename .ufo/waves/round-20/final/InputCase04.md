# InputCase04: `r13-frozen-dirty` C2 caller-case falsifier

Scope: read-only source inspection at pin `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. No runtime, no import, no fixture or caller execution, no installs or updates. Writes: this report only. Not read: census roots, `census/operator-sweep-*`, the round-14 callers.

**Verdict:** source agreement for the case as written. The pinned round-13 caller refuses the inert frozen mutation at its input gate, before any suite line and before output creation, with exit 2 and the exact changed path. No blocking defect, so no `STATUS: PARTIAL`. The predicate is path-substring only, so other refusals on the same path also satisfy it (bounded counterexample in section 4).

## 0. Exercised reads

- `git show 1988860ed28a…:tests/fixtures/r20-input-binding.py`, `…:tools/souji-rev-pin.py`, `…:census/round-13/run-verification.py`: returned content, no error.
- `git ls-tree -r --full-tree 1988860… -- tests/fixtures/r13-cert-frozen`: 8 blobs.
- `git ls-tree 1988860… -- <23 declared closure paths>`: all 23 present.
- `git rev-parse`: commit `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`; fixture blob `ea6efacc623f933c5ef956fe81ecdf49269e892b`; rev-pin blob `8da7da9c2d627d7675976a5f4093f0d8f25d689c`; run-verification blob `b5107ef576c15686db5632e272c87fa8aa5f8b96`.

Applicable caller: `r13-frozen-dirty` is emitted only by `mutation_plan("r13")` (`("frozen-dirty", R13_FROZEN, False)`), so the sole caller read is `census/round-13/run-verification.py`.

## 1. Entrypoint, mutation, closure

- Sandbox: `make_sandbox(top, "r13", root, r13_paths, ["census/round-13/verification.json"])`. The closure is the caller's literal `MEASURED_PATHS` (22 entries, AST-parsed) plus the prior, committed into a fresh synthetic repo under `/var/tmp`.
- Frozen closure: 8 blobs under `tests/fixtures/r13-cert-frozen/`. `expected.json` is blob `514494f1b504f833bf635075cff905c8e1d05256`, mode 100644. `installed/fixture-{alpha,beta}.sh` are mode 100755.
- Mutation: `expected.json` gets `b" \n"` appended (`inert_suffix`, `.json`). That is whitespace after a JSON document: inert to a parser, a byte change to the gate. Restored in `finally`.
- Invocation: `python3 -B census/round-13/run-verification.py --round 20 --output census/round-20/r20-r13-frozen-dirty.json --retry-failed --previous census/round-13/verification.json`, cwd = sandbox, with GIT_* pointed at a decoy. The decoy is inert: the caller's `ENV` strips GIT_* except three keys, and the helper's `_env()` strips all GIT_*.

## 2. Refusal trace

1. `main`: `validate_output` and `validate_previous` pass. The sandbox has `census/round-20` (floor 20, so round 20 is open) and a regular prior.
2. `execute` → `resolve_revision()` is the first step that can refuse. Nothing has printed to stdout yet; `run()` is the only stdout writer in `execute`.
3. `resolve_durable` finds HEAD durable via `refs/heads/main`, then `input_snapshot(ROOT, HEAD, INPUT_PATHS)` compares committed blob SHA-256 with working-tree SHA-256. Mismatch → `Refusal("measured inputs differ from <HEAD> (missing=[] added=[] changed=['tests/fixtures/r13-cert-frozen/expected.json'])")`.
4. `Refusal` subclasses `ValueError`. `resolve_revision` catches it, prints to stderr with `(no record written)`, then `raise SystemExit(2)`. `main` catches only `FileExistsError` and `Exception`, so `SystemExit` propagates and the exit code is 2.
5. Predicate: exit 2 ✓; path present in stdout+stderr ✓; stdout empty ✓; `census/round-20/r20-r13-frozen-dirty.json` absent ✓. The only `output.open("x")` sits after the suite loop.

Result: the predicate holds for the intended reason at the pin. This is a source-only trace; runtime was not observed.

Fail-open detection: if the gate were bypassed, the first `run()` prints `evidence-selftest: exit=…` to stdout, so the stdout predicate fails. The predicate reliably detects acceptance.

## 3. Behavioural or wiring; consumption

- Behavioural: runs the real `main()` on a real changed byte. Acceptance is caught by the stdout predicate.
- Wiring: `covered_by_measured` checks the AST-declared list. Omitting the frozen directory yields `FixturePrerequisite` → blocked. That is fail-closed, not a pass.
- Consumption: not observed. The caller never opens `expected.json`. It passes the directory as argv to `run("evidence-frozen", ["python3", "tools/souji-cert-evidence.py", "--frozen", "tests/fixtures/r13-cert-frozen"])`, and `dependency_map` binds the directory's recursive files into that record. Whether the child reads `expected.json` is outside the named sources: [INFERENCE]. The case refuses before any child runs, so it can never exercise consumption.
- No caller-level clean control exists. A clean sandbox run executes four in-sandbox suites (`evidence-selftest`, `evidence-frozen`, `evidence-external-fixture`, `structure-selftest`), then fails at `git show 31984f47…:tools/souji-quarantine.sh` because the fresh repo lacks BASE, and exits 2 as could-not-evaluate. The only clean-side evidence for the frozen closure is helper-level: `helper-input-snapshot-clean` and `helper-resolve-clean`.

## 4. Masquerade: bounded counterexample (predicate, not caller)

The predicate is `changed_path in combined`. These states of the same closure also satisfy it, with exit 2, empty stdout, no output, and no inert byte change evaluated:

- (a) Unlink `expected.json` and replace it with `symlink_to("evidence/alpha.txt")`. `capture()` raises `symlink measured input tests/fixtures/r13-cert-frozen/expected.json`. **Bounded counterexample: the case passes for a non-byte reason.**
- (b) Unlink `expected.json`. Refusal: `missing=['tests/fixtures/r13-cert-frozen/expected.json']`.
- (c) chmod 000 as non-root. Refusal: `unreadable measured input: [Errno 13] Permission denied: '<abs>/…/expected.json'`.
- (d) Content-independent: a broken directory walk marks all 8 frozen members missing, and the named path appears.

The current content-only mutation cannot reach (a) through (d), so the case passes for the right reason today. It cannot prove that reason on its own.

Tightened predicate: require `"missing=[] added=[] changed=['tests/fixtures/r13-cert-frozen/expected.json']"` and `"(no record written)"` in stderr. Both strings come from the code as read.

## 5. Baseline producer witness

None for `r13-frozen-dirty`. The seven baseline pairs are `baseline-r13-helper`, `baseline-r13-sources`, `baseline-r13-new-knowledge`, `baseline-r14-helper`, `baseline-r14-frozen`, `baseline-targeted-wrapper`, `baseline-demo-helper`. The only frozen pair is r14's, so red-before for the r13 frozen input is not witnessed. Whether the baseline r13 caller measured the frozen directory is not checked, because that source is not a named file.

## 6. Boundary note (non-blocking; documented scope)

`input_snapshot` compares content SHA-256 only. It never compares working-tree mode with committed 100644/100755, so mode-only drift is accepted, and the fixture has no mode variant. In the closure, 14 top-level blobs and the two `installed/*.sh` are 100755. The caller's own invocations go through `python3` or `bash`, so exec-bit drift does not change them. A child that execs directly would be affected: [INFERENCE], unverified. The helper's documented contract is "exact committed blob bytes", so this sits inside stated scope. L1 decision: bind mode, or state bytes-only in the record.

## 7. Adjacent: same caller, same predicate

`r13-helper-syntax-invalid` never reaches the syntax path. `resolve_revision` compares helper bytes to committed before importing, so the appended invalid line triggers `tools/souji-rev-pin.py differs from measured commit`. The case passes on the byte diff, not on a SyntaxError.

## 8. Operability for L1

- The closure source is the `--root` working tree, not the pin, and the sandbox commits whatever the root contains. Run the fixture from a clean detached clone at 1988860.
- All 23 declared inputs are tracked at the pin, so the closure is complete at 1988860. The gate checks working-tree equality at run time.
- Checks for L1: run `tests/fixtures/r20-input-binding.py` from the clean pin clone and confirm `r13-frozen-dirty` passes. Apply the tightened predicate (section 4) before citing the case as reason-specific evidence.

Installs or updates: none. Trailer: `.ufo/waves/round-20/final/InputCase04.md` (relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`).
