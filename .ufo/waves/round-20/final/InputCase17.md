STATUS: PARTIAL — The `--baseline` tripwire cannot certify any targeted refusal. `census/round-14/run-targeted.py` is driven through `module.main()`, which bypasses its only exit-2 handler, so a correct refusal is recorded as `exception` and `baseline-targeted-wrapper` FAILs deterministically. The prior input `census/round-14/verification-attempt-1.json` has no baseline pair at all, so the C2 boundary claim for it has no red-before witness. Operability verdict: the matrix case runs and is sensitive to the prior binding; the targeted baseline path cannot pass as written.

# InputCase17 — `targeted-prior-attempt-dirty` (read-only C2 falsifier)

Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Source-only seat: nothing built, imported, run, or installed. Impacted axes: operability (judged); C2 boundary completeness; baseline witness.

## Evidence (executed, read-only)
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:tests/fixtures/r20-input-binding.py` — exit 0
- same form, `:tools/souji-rev-pin.py` — exit 0
- same form, `:census/round-14/run-targeted.py` — exit 0 (applicable caller)
- `git -C … ls-tree 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1 -- census/round-14/verification-attempt-1.json census/round-13/verification.json census/round-14/run-targeted.py` — exit 0: 100644 blob `c04188f6…`; 100644 blob `879d96b4…`; 100755 blob `4a5250cd…`.
- Not opened (outside the ONLY bound): `census/round-14/run-verification.py`, imported by the applicable caller as `module`. Items depending on it are tagged **[UNVERIFIED-R14]**.

## Trace
- **Case mapping.** `mutation_plan("targeted")` entry `("prior-attempt-dirty", R14_PRIOR)` → `caller_command` kind `targeted` → `census/round-14/run-targeted.py`. The other three callers are not involved.
- **Entrypoint.** `python3 -B census/round-14/run-targeted.py --output <r20 path>`, cwd = sandbox. Module level loads `run-verification.py` outside any handler. `main()` takes no argv. Its only refusal handler sits in `if __name__ == "__main__":` (OSError/ValueError/RuntimeError → stderr, exit 2).
- **Inert byte.** `" \n"` appended after `commit_all`, restored in `finally`. JSON stays valid and bytes change, so a parse refusal cannot be the reason. Sound design.
- **Input closure.** Fixture closure = r14 literal `MEASURED_PATHS` + prior, set-equal to the wrapper's runtime binding `[*module.MEASURED_PATHS, prior]`. Read by the wrapper but outside the binding: six `paths` (hashed as `before`/`after`), `census/round-13/verification.json`, the r14 import file, and `module.BASE:tools/souji-census.sh`. Fixture coverage checks assert only TARGETED, HELPER, R14_FROZEN, `corpus/SOURCES.md`, and the prior. The prior check is tautological, since the fixture adds it itself.
- **Order in `main()`.** `output_path()` → append prior → `resolve_revision()` → `before` → `historical_before` → `git show BASE` → six producers → `after` → `checked_inputs` → record write → return 0/1.
- **Sandbox reachability.** `caller_refusal` never sets `module.BASE`; only the tripwire driver does. The fresh repo lacks that commit, so `git show` raises CalledProcessError, which is not in the handler tuple: exit 1. [INFERENCE: BASE is a lane commit absent from the sandbox.] Consequences: no matrix run reaches a producer or the record write. A PASS therefore requires a handled exception naming the prior, raised before `git show`. The only such site is `resolve_revision()` **[UNVERIFIED-R14]**.
- **Predicate.** exit==2 needs a handled exception type; the helper's `Refusal` is a ValueError, so it qualifies. The prior-path substring is the only real discriminator, and it accepts any mention of the path. stdout-empty is vacuous for this wrapper, whose only print goes to stderr. output-absent is vacuous: the write is unreachable, and the wrapper ignores `--output` (only r14 `output_path()` could honor it) **[UNVERIFIED-R14]**.
- **Baseline witness.** None for the prior. `BASELINE_PAIR_CASE_IDS` lists 7 pairs, none for the prior. `baseline-targeted-wrapper` mutates `run-targeted.py`, not the prior. The tripwire target `module.module.run` exists and would fit.

## Answers
1. **Behavioral or wiring?** Behavioral at process level: real entrypoint, real r14 resolve, real byte snapshot, isolated repo. The verdict is one substring plus one exit code, with no clean control. It is behavioral but uncontrolled.
2. **Can a prerequisite refusal masquerade?** The wrapper has no prior-specific prerequisite of its own, and the byte mutation can only yield `changed=`. The open channel is r14- or git-originated text that echoes the prior pathspec under the decoy `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE` the matrix injects. No clean run exists to exclude it **[UNVERIFIED-R14]**.
3. **Is the input consumed by this caller?** Yes, as a bound digest, not semantically. The appended entry feeds the r14 snapshot; success records `prior_evidence_sha256=inputs_after[prior]`; the prior's content is never read. Removing the append should FAIL the case (exit 1 at `git show`, or exit 2 naming another path), provided r14's literal does not already list the prior. The fixture never checks that.

## Counterexample (bounded, deterministic)
Driver branch `kind == "targeted"`: `module.module.BASE = commit; module.module.run = producer; sys.argv = [...]; result = module.main()`, inside a `try` whose last clause is `except BaseException → status="exception"`.

The refusal is raised out of `main()`, where no handler runs. Nothing reaches stderr, so `changed_path_named` is False, and `changed_refused` requires status in (exit, return), so it is False. `baseline-targeted-wrapper` FAILs even when the changed wrapper refuses correctly. It can pass only if the refusal arrives as `SystemExit(2)` with the path on stderr, which would require r14 to bypass the handled types **[UNVERIFIED-R14]**. The same direct `module.main()` pattern applies to kind `r14`; r13 and demo are unverified.

Smallest safe correction: wrap `module.main()` in the targeted and r14 branches with `except (OSError, ValueError, RuntimeError) as exc:`, write `refused: %s` to stderr, and set `status="exit"`, `exit_code=2`. Alternatively, run the file via `runpy.run_path(script, run_name="__main__")` after patching the module object.

## Gaps (ranked)
1. **No red-before for the prior** (blocks the C2 claim). Add `baseline-targeted-prior`: mutate `R14_PRIOR` in both sandboxes; the old wrapper must reach the producer tripwire; the new one must exit 2 with `changed=['census/round-14/verification-attempt-1.json']`. This needs the driver fix first. If the old wrapper already refused, the prior boundary was not new in r20, which is also a finding.
2. **No clean control.** Run the identical invocation without mutation under the same decoy env; it must not name the prior. This closes the masquerade channel.
3. **Predicate tightening.** Match `changed=['<prior>']`, not any mention. Drop or repair output-absent, which is vacuous because the wrapper ignores `--output`.
4. **Direct reads outside the snapshot.** The six `paths`, `census/round-13/verification.json`, and the r14 import file are hashed from the working tree before and after the run but never compared to the revision. A dirty pre-run copy is recorded as `installed_sha256` with no refusal. A mid-run change yields a written record and exit 1, because the write precedes `return 0 if … else 1`. The helper contract says to refuse before writing a record.
5. **Literal `inputs_unchanged_during_run=True`.** The record hard-codes it. The prior is checked only at start and end. A change-and-restore during the producers is invisible if `checked_inputs` is end-state only **[UNVERIFIED-R14]**. Not reachable in the matrix.

## Source agreements
- The fixture closure equals the wrapper's binding set for the prior.
- The prior is tracked at the pin, so the helper's `ls-tree` expected side includes it.
- The helper's snapshot of a regular file is correct for this mutation: committed blob digest versus `O_NOFOLLOW` file digest; mismatch raises `Refusal` with `changed=[…]`, which the case's substring check accepts.
- The mutation keeps JSON valid, so a validity refusal cannot be mistaken for the intended reason.

## Checks for L1 (not run here)
- `--baseline 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`: expect `baseline-targeted-wrapper` FAIL, per the driver analysis above.
- One read of `census/round-14/run-verification.py` (`resolve_revision`, `checked_inputs`, `output_path`, `ENV`, `BASE`, `MEASURED_PATHS`, and how `run` fails) closes every [UNVERIFIED-R14] item.

No tools installed or updated. No build, test, or runtime execution.
