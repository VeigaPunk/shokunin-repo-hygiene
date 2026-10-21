STATUS: PARTIAL — `r14-helper-dirty` does not bind its refusal to the dirty-helper reason. Its refusal predicate is a bare substring match on `tools/souji-rev-pin.py` in exit-2 output, and the r14 caller's own `subprocess.CalledProcessError` from `git show HEAD:tools/souji-rev-pin.py` embeds that same path. A prerequisite failure on that route (for example an ambient repository redirect, the exact hazard the decoy exists to catch) would score PASS. The pinned r14 caller source agrees with the intended refusal on this pin; the defect is in the falsifier's predicate and control set, not in the pinned caller. Operability: the case is runnable on this pin with no fixture prerequisite gap, and its expected outcome is PASS (source-derived, not observed).

# InputCase09 — C2 caller-case falsifier `r14-helper-dirty`

Pin `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`; lane HEAD equals pin. Source-only. Nothing executed: no sandbox, clone, fixture run, or caller run. Every verdict below is source-derived unless marked observed.

## Chain traced

1. **Entrypoint.** `r20-input-binding.py` `caller_command` runs `python3 -B census/round-14/run-verification.py --output census/round-20/r20-r14-helper-dirty.json` with cwd = synthetic sandbox `<tmp>/r14`. Env = `CLEAN_ENV` plus `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` pointing at `ambient-decoy`, a second repo with one commit that lacks `tools/souji-rev-pin.py`.
2. **Inert byte.** `mutate_and_call("r14","helper-dirty")` appends `b"\n# inert r20 input-binding mutation\n"` to `tools/souji-rev-pin.py` in the sandbox worktree. It is not committed and is restored afterwards.
3. **Closure.** The pinned r14 `MEASURED_PATHS` has 13 entries, including `tools/souji-rev-pin.py` and the directory `tests/fixtures/r14-cache-frozen`. The fixture reads that list from the `--root` worktree, expands it from worktree bytes (`expand_closure`), and commits it into the sandbox. Checks: all 15 closure blobs (directory files included) hash-equal to pin; all are regular (100644/100755); no symlinks.
4. **Caller path at pin** (`census/round-14/run-verification.py`). `main()` → `output_path()` passes, because the fixture pre-creates `census/round-20` → `resolve_revision()`:
   - `ENV` drops every `GIT_*` key, so `git("rev-parse","HEAD")` ignores the decoy and returns the sandbox HEAD.
   - `helper.read_bytes() != check_output(["git","-C",ROOT,"show",HEAD+":tools/souji-rev-pin.py"])` → `ValueError("tools/souji-rev-pin.py differs from measured commit")`.
   - Caught by `except (OSError, ValueError, SyntaxError, ImportError, subprocess.CalledProcessError)` → stderr `run-verification: refused: tools/souji-rev-pin.py differs from measured commit (no record written)` → `SystemExit(2)`.
   - The helper module is never exec'd, `run()` is never reached, stdout is empty, and no output file is written.
5. **Predicate** (`caller_refusal`): `rc == 2 ∧ "tools/souji-rev-pin.py" ∈ stdout+stderr ∧ output absent ∧ stdout == ""`. Non-vacuous on the designed path: the caller honors `--output` and writes only at the end; suite lines reach stdout only via `run()`.

## Answers

- **Behavioral or wiring?** Behavioral at the process boundary: a real subprocess in a real git repo, with real mutated bytes, observed through rc, stdout, stderr and filesystem effects. The reason is only weakly observed: the designed message is never compared, only a path substring.
- **Can a prerequisite refusal masquerade?** Yes. `CalledProcessError` from `git show <HEAD>:tools/souji-rev-pin.py` carries its argv, including the helper path, in `str(exc)`. The same handler catches it, the caller exits 2, and the predicate passes. Two routes: (a) an ambient `GIT_*` redirect that survives scrubbing (the decoy has a commit, so `rev-parse HEAD` succeeds while `show` fails); (b) an operator HEAD that lacks the helper while the worktree has it. The `GIT_` scrub makes (a) dead on this pin, but nothing in the case tests the scrub.
- **Is the input consumed by this caller?** Yes, three ways: the byte compare (the only one this mutation reaches), module exec (after the compare), and `resolve_durable` → `input_snapshot` (tree_check, same closure). The snapshot would refuse with `changed=['tools/souji-rev-pin.py']`. Consequence: deleting the byte compare would not be killed by this case; the operator outcome is preserved, so this is acceptable.

## Bounded counterexample (source-derived, not run) — mutant M1

In `census/round-14/run-verification.py`, replace the `ENV` comprehension (drops `GIT_*`) with `ENV = dict(os.environ)`; change nothing else.

- Under the decoy env, `head` = decoy HEAD. `git show <decoyHEAD>:tools/souji-rev-pin.py` exits 128 → `CalledProcessError: Command '['git', '-C', '<sandbox>/r14', 'show', '<decoyHEAD>:tools/souji-rev-pin.py']' returned non-zero exit status 128.`
- Caught → stderr `run-verification: refused: Command '[…tools/souji-rev-pin.py…]' … (no record written)`, rc 2, stdout empty, no output.
- `r14-helper-dirty` → **PASS**, while the byte-compare branch never executes. [INFERENCE from source plus stdlib `CalledProcessError` text; not executed.]
- M1 does fail `r14-frozen-dirty`, `r14-sources-dirty` and `r14-wrapper-dirty`, because their changed paths are absent from the masquerade text. So the regression surfaces only through other cases; `r14-helper-dirty` cannot detect it alone.
- Same blind spot: `r14-helper-syntax-invalid`; `targeted-helper-dirty` and `targeted-helper-syntax-invalid`, since `run-targeted.py` calls the same `module.resolve_revision()`. The `demo-*` caller was not read.

## Baseline producer witness

- **No witness exists for `r14-helper-dirty` itself.** The only r14 helper pair is `baseline-r14-helper`, which runs only under `--baseline REV` (REV = `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`).
- **Old side (12516f7).** The old r14 caller has no helper byte check, and its `MEASURED_PATHS` (8 entries) omits `tools/souji-rev-pin.py`. The old helper's `resolve_durable(tree_check=True)` diffs only that list, so the mutated helper is not refused. `run()` is reached → `ProducerReached("baseline-r14-helper")`, status `producer`. This holds from source. The driver's `module.BASE = commit` override is required, because the old caller hardcodes `a31642d…`, which is absent from the sandbox.
- **Changed side.** The current caller refuses exactly as in `r14-helper-dirty`, so it inherits the same masquerade blind spot.
- **Vacuity.** On the baseline side, `output_absent` checks `census/round-20/baseline-r14-helper-baseline.json`, which the old caller never writes (it writes `census/round-14/verification.json` only after `run()`). It is always true there. Harmless, since `producer` precedes any write, but it is not evidence. The witness proves "not refused", not why.

## Other findings (ranked)

1. **No positive control (Medium).** No caller-level clean run exists anywhere in the fixture. The `helper-*-clean` cases exercise the helper API only, and both sides of every `invoke_tripwire` pair are mutated. A caller that refuses unconditionally with the helper path in its message passes all helper cases and the baseline changed side.
2. **Provenance (Low–Medium).** `make_sandbox` and `expand_closure` read `--root` worktree bytes, not pinned blobs. They match pin today (verified above), but the main matrix is not bound to the commit. Only the baseline pairs use git blobs.
3. **Adjacent: syntax case (Low).** `helper-syntax-invalid` is refused by the same byte compare before `exec_module`, so the broken helper is never compiled and syntax handling is never exercised.
4. **Knowledge gate (Info).** `main()` calls `choose_existing_admitted(root)` unconditionally before the matrix, so r14 is gated on an admitted corpus file. Satisfied on pin: `corpus/knowledge/dupe-finders-detect-then-act.md` sorts first, has source/verified-at/recheck on lines 1–3, and has no HELD marker. Not a live blocker.

## Proposed bounded fix

- Helper-first-check cases: require the exact text `refused: tools/souji-rev-pin.py differs from measured commit (no record written)` in stderr. The `CalledProcessError` form (`refused: Command '[…`) cannot match it.
- Add `r14-helper-clean-producer`: run the unmutated sandbox through the existing `invoke_tripwire(..., "r14", ROUND14, ...)`, and require `status == "producer"` and `witness == case_id`. Add the id to `expected_case_ids`.
- Pinned caller: no change required on this evidence.

## Verification gaps

- Nothing was executed. Every expectation is source-derived.
- The `demo` caller was not read in depth, so its helper-check exposure is unverified.
- `CalledProcessError` string content is from Python stdlib semantics, not observed.

## Tooling

No installs or updates. Read-only git only: `show`, `ls-tree`, `git grep` (named paths), `rev-parse`, `cat-file -e`, `hash-object` without `-w`. No index or object writes. No clones or sandboxes created. Sole write: this report.
