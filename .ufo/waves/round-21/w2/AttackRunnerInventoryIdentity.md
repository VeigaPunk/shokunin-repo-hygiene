# AttackRunnerInventoryIdentity — C2 source-only review

Axes reviewed: C2 operability (repository-source identity, frozen step identity, and replay evidence fidelity).

STATUS: PARTIAL — the frozen 18-step projection has no static identity mismatch, but the advertised any-repository boundary has a concrete false refusal, and the replay record overstates what its source-state comparison proves. No code was executed.

## Findings

### Moderate — A repository containing `--rev` is refused if its `HEAD` is unborn or invalid

`census/round-21/run-acceptance.py`, `main()` calls `source_state(source)` before cloning. `source_state()` requires `git rev-parse --verify HEAD^{commit}` to succeed and raises `Refusal` otherwise; the outer handler returns exit 2. This adds a valid-`HEAD` precondition beyond the preregistered C2 contract that `--root` may be any local repository containing the requested revision and need not have `HEAD == --rev`.

Concrete counterexample: a bare mirror has `refs/heads/measurement` pointing at the requested full commit, but its symbolic `HEAD` points at a not-yet-created `refs/heads/main`. The requested commit is present and reachable from the advertised branch, so an explicit checkout of that full commit is possible, but the runner refuses before reaching its clone/checkout path because the source `HEAD` does not resolve. `census/round-21/replay-matrix.sh` covers a normal clone with mismatched `HEAD`, a normal bare clone, and the lane; those scenarios do not exercise a repository with an unborn/invalid `HEAD`.

### Low — `source_unchanged` is broader than `source_state()`'s evidence

In `run-acceptance.py`, `source_state()` records only `HEAD`, bare status, and (for non-bare sources) `git status --porcelain --untracked-files=no`; for bare sources it records an empty status. It does not fingerprint refs or repository contents. `main()` nevertheless emits `"source_unchanged": true` whenever the before/after `source_state` dictionaries compare equal. For example, a change to an untracked file in a non-bare source, or a change to a non-`HEAD` ref in a bare source, is not represented by that comparison. The replay matrix separately hashes refs, but its state is not a full repository-content digest either. The result supports only “the fields in `source_state` were unchanged,” not an unqualified claim that the source repository was unchanged. This identifies an evidence-label limitation, not an observed source mutation.

## Frozen inventory check

Static comparison of the pinned r20 runner (`5ff75657427c4793fbf1f124d794f1c99359d74e:census/round-20/run-acceptance.py`), r21 `make_steps()`, and `census/round-21/step-inventory.json` found no mismatch in the 18 step names, arguments after placeholder normalization, or literal expected summaries/counts. The agreement-pin step's `--root` changes from the replay root to the private historical-agreement staging root; `inventory_projection()` normalizes both to `<ROOT>`, as the frozen inventory specifies. This is source comparison only, not an observed replay pass.

## Verification gaps

- No scripts, tests, or other code were run, as required for this source-only assignment.
- The `xd://lsp` device was unavailable (the mounted-device response reported “No such tool”); no LSP semantic checks were possible. No grep output is used as semantic evidence.
- No tool was installed or updated.