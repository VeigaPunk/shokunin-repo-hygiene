STATUS: PARTIAL — `targeted-helper-dirty` is sound at the pin, but the falsifier's refusal predicate is path-only. Consequently `targeted-helper-syntax-invalid` is reported PASS for the dirty-byte reason, and the syntax refusal is never exercised. This is a false green for the syntax property in the C2 inventory and blocks any claim that counts syntax refusal. L1 must not count that case until the predicate pins the typed reason and the syntax variant commits an invalid helper.

# InputCase14 — `targeted-helper-dirty` (read-only C2 caller-case falsifier)

- Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` — `round-20: exact auditor grants and complete caller inputs` (2026-10-21T06:49:01-03:00).
- Author-side advisory only; not closure, promotion, or a SHONEN mark. Installs/updates: none.
- Axes: operability (judged); reason specificity; pin-exactness; red-before and positive-witness coverage.

## Method and limits
- Pin-only reads (`git -C … show | cat-file | ls-tree`, all EXIT=0): fixture `tests/fixtures/r20-input-binding.py`; helper `tools/souji-rev-pin.py`; applicable caller `census/round-14/run-targeted.py` and its import `census/round-14/run-verification.py`; prerequisite blobs (`census/round-14/verification-attempt-1.json`, `cache-demonstration.py`, `check-timeout-anchor.py`, `census/round-13/run-verification.py`, `census/round-13/verification.json`, `corpus/SOURCES.md`, `tools/souji-census.sh`, `tools/souji-evidence-cache.py`, `tests/fixtures/r14-*`, `tests/fixtures/r14-cache-frozen/*`). All are regular blobs (100644/100755); no symlinks or submodules.
- Applicability: the fixture's `mutation_plan("targeted")` maps `targeted-helper-dirty` to `run-targeted.py`. `round-13/run-verification.py` and `round-14/cache-demonstration.py` were fetched in the same batch only to confirm applicability; they own other case IDs and were not analyzed.
- Nothing executed; no verification exercised. "PASS" below means predicted by static trace. No `census/operator-sweep-20261019` paths and no lane roots were opened.

## Verdict
- Predicted PASS at the pin.
- Behavioral: a real subprocess runs the real wrapper and the real r14 guard in a fresh `/var/tmp` sandbox. No stubs in this case.
- Source agreement: the fixture's expected refusal (exit 2, path named, no output, empty stdout) matches the pinned path `run-targeted.py` → `module.resolve_revision()` → helper byte compare, line for line.
- The required reason is the caller's own byte guard. No prerequisite refusal precedes it for this mutation.
- Weak spots: the predicate cannot tell that reason from another refusal naming the same path, and the case has no producer witness.

## Trace
1. Entrypoint: cwd = sandbox `targeted` repo; argv `<sys.executable> -B census/round-14/run-targeted.py --output census/round-20/r20-targeted-helper-dirty.json`; env = `CLEAN_ENV` plus `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE` pointing at a decoy repo.
2. Wrapper import: loads r14 as `r14_verify`. The r14 `ENV` drops every `GIT_*` key, so the decoy has no effect.
3. Wrapper `main()`:
   a. `module.output_path()`: argparse over `sys.argv`; new path under existing `census/round-20`; passes.
   b. Extends `module.MEASURED_PATHS` with `census/round-14/verification-attempt-1.json`.
   c. `module.resolve_revision()`: `git rev-parse HEAD`; helper is regular; `git show <head>:tools/souji-rev-pin.py`; `helper.read_bytes() != committed` → `ValueError("tools/souji-rev-pin.py differs from measured commit")` → stderr `run-verification: refused: tools/souji-rev-pin.py differs from measured commit (no record written)` → `SystemExit(2)`.
4. Never reached: helper `input_snapshot`, helper `exec_module`, any `module.run`, `checked_inputs`, and the final `target.open("x")`.
5. Inert byte: `b"\n# inert r20 input-binding mutation\n"` appended after `sys.exit(main())` in `tools/souji-rev-pin.py`. Comment-only; changes the bytes. `mutate_and_call` restores the original in `finally`.

## Input closure and consumption
- Fixture targeted set = r14 `MEASURED_PATHS` + `R14_PRIOR`. Runtime set is identical. The helper is an r14 `MEASURED_PATHS` entry, so `covered_by_measured` passes.
- The helper is consumed in four steps: byte compare, `exec_module`, `resolve_durable`, `input_snapshot`; `checked_inputs` then runs at the end. This case reaches only the first step. If the byte compare were removed, the helper's own snapshot would still refuse with the path named. The verdict would hold, but the case cannot attribute the refusal to the byte guard.
- Bytes come from the `--root` working tree (`expand_closure(root, …)`), not `git show 1988860…`. Only `--baseline` uses pinned git bytes. The default run is therefore not pin-exact, and its output prints neither root HEAD nor closure digests.

## Predicate
`rc == 2` and `"tools/souji-rev-pin.py"` in stdout+stderr and output absent and stdout empty. All four hold on the predicted trace. The path check is a substring match; the reason string is never checked, and the CASE detail omits the caller's stderr.

## Masquerade analysis
- (a) This mutation: none reachable. Pre-guard prerequisites (argv, output path, `rev-parse HEAD`, helper presence and regularity) all pass in the sandbox.
- (b) Would pass the predicate if they occurred: `CalledProcessError` from `git show <head>:tools/souji-rev-pin.py` (its text contains the path); `OSError` from `read_bytes()`; `nonregular revision helper tools/souji-rev-pin.py`. The fixture never creates these states.
- (c) Live at the pin, sibling `targeted-helper-syntax-invalid`: appends `\ndef r20_invalid(:` to the already-committed helper, so the byte guard fires first with the identical refusal → PASS. `exec_module` never parses the invalid text. False green.
- (d) Counterfactual for this case: if r14 stopped stripping `GIT_*`, `rev-parse HEAD` returns the decoy HEAD, `git show` fails, and the refusal is a `CalledProcessError` naming `tools/souji-rev-pin.py` → PASS, though the dirty guard never ran. Latent today.

## Baseline producer witness
None for the targeted helper. Nearest:
- `baseline-targeted-wrapper`: changed path is the wrapper, not the helper; uses the real `module.module.run` tripwire.
- `baseline-r14-helper`: r14 entrypoint, same guard function.
So the targeted entrypoint has no red-before witness for its helper gate. Default mode has no clean→producer positive control for any caller, so an always-refuse caller would pass this case.

## Findings (ranked, operability)
1. Predicate is path-only, so it masquerades (c) and (d). Require the typed reason string per case.
2. False green: `targeted-helper-syntax-invalid`. Static reading of `round-13` and `round-14` finds the same guard text and path-only predicate, so their `*-helper-syntax-invalid` cases share the false green. `demo` not analyzed.
3. No positive control per entrypoint in default mode.
4. Not pin-exact: closure comes from the working tree; root HEAD and digests are neither checked nor printed.
5. Diagnostics: on FAIL, the CASE detail shows booleans only, not the caller's stderr.

## Bounded counterexample
Case `targeted-helper-syntax-invalid` is PASS today, though the syntax property is never exercised. Evidence: `mutate_and_call(..., invalid_syntax=True)` writes `original + b"\ndef r20_invalid(:\n"` into the committed helper, so `helper.read_bytes() != committed` fires first in `resolve_revision()`. Expected by name: refusal from the syntax path. Predicted: byte-guard refusal, PASS.

## Minimal correction (proposed, not applied)
1. Predicate: for `helper-dirty`, require stderr to contain `tools/souji-rev-pin.py differs from measured commit (no record written)`; put the first stderr line in the CASE detail.
2. Syntax variant: commit the invalid helper in a separate fresh sandbox so the byte guard passes; require `refused: invalid syntax (` from the exec step, exit 2.
3. Positive control: in default mode, run the targeted wrapper on a clean sandbox with `module.run` patched to a tripwire (the `TRIPWIRE_DRIVER` targeted branch already sets `module.module.BASE`); require status `producer`.
4. Pin-exactness: refuse unless root HEAD is `1988860…` and the closure equals `git show` bytes; print root HEAD and closure digests in the summary.

## Checks for L1 (not run here)
- After integration, on a clean checkout at the pin: `python3 tests/fixtures/r20-input-binding.py`.
- Expect `targeted-helper-dirty` PASS. Expect `targeted-helper-syntax-invalid` to pass for the wrong reason until fixed.

Trailer: `.ufo/waves/round-20/final/InputCase14.md` (relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`).
