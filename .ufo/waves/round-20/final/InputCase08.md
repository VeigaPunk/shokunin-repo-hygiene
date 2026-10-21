STATUS: PARTIAL — `r13-optional-prior-dirty` refuses the dirty prior for the right mechanical reason on the pinned runner, but it is not a sufficient operability falsifier. Its predicate accepts any exit-2 refusal that prints `census/round-13/verification.json`, so a one-line over-refusal in `validate_previous` passes it while `--retry-failed` is unusable. It has no unmutated control, so it shows neither admission nor consumption of the prior. It has no baseline producer witness, and the tripwire's r13 branch omits `--retry-failed --previous`, so a baseline pair cannot be added as-is. Bounded correction in §7.

# InputCase08 — `r13-optional-prior-dirty` caller-case falsifier (read-only, source-only)

Operability verdict: PARTIAL. The dirty-prior refusal is real on the pinned runner. The case is fast, deterministic, and writes nothing to the lane, but its oracle is not reason-exact, has no clean control, and has no baseline witness.

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`. Pinned build `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Preregistered baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. Prior `census/round-13/verification.json` is blob `879d96b4…` at both commits. Pinned runner blob `b5107ef5…`, pinned helper blob `8da7da9c…`.

Scope: read-only `git show`, `git ls-tree`, `git cat-file -t`, and grep/sed over named files at the two commits (§9). No runtime, no fixture or runner execution, no imports, no git writes, no status checks, no installs, no subagents.

## 1. Entrypoint trace (pinned)

- Fixture `caller_command` (`tests/fixtures/r20-input-binding.py` 660–666) runs from cwd = synthetic repo `/var/tmp/souji-r20-input-binding-*/r13` (built by `make_sandbox` 291–). Command: `python3 -B census/round-13/run-verification.py --round 20 --output census/round-20/r20-r13-optional-prior-dirty.json --retry-failed --previous census/round-13/verification.json`. Ambient `GIT_DIR`, `GIT_WORK_TREE`, and `GIT_INDEX_FILE` point at a decoy repo.
- Runner `main` (405). `validate_output` (342) accepts. `closed_round_floor` (327) is 20 in the sandbox because `make_sandbox` creates `census/round-20`, so round 20 is not closed.
- `validate_previous` (384; refusals 389–401) accepts: regular, lane-contained, not a symlink, resolves to itself.
- `execute` (445): 447 sets `PREVIOUS_SOURCE = census/round-13/verification.json`; 448 calls `resolve_revision()` (121).
- `resolve_revision`: 136–138 sets `INPUT_PATHS = MEASURED_PATHS + [prior]`. 140 calls `resolve_durable(..., INPUT_PATHS)`, which runs the helper's `input_snapshot` (helper 94). That compares `ls-tree` blob digests with working-tree digests. The prior mismatches, so the helper raises `Refusal` (helper 177): `measured inputs differ from <HEAD> (missing=[] added=[] changed=['census/round-13/verification.json'])`.
- 144 prints that refusal to stderr. 146 raises `SystemExit(2)`. The output file is opened only at 516, so none is created. Nothing reaches stdout.
- Decoy: the runner's module-level ENV block strips `GIT_*`, and the helper's `_env()` (helper 47) does the same. If that regressed, `show HEAD:tools/souji-rev-pin.py` would fail in the decoy and the message would not name the prior, so the case would fail. The decoy is not a masquerade route.

## 2. Inert changed byte

- `inert_suffix` (651–657) returns `b" \n"` for `.json` (654). `mutate_and_call` (700–726) appends it after the top-level JSON value of the prior. Its guard (716) requires a regular file. Bytes are restored in `finally`.
- The change is parse-inert and digest-changing. The only thing the runner can observe is the digest at 140–141. The JSON is never parsed, because the refusal precedes line 450.

## 3. Relevant input closure

- Runtime binding under `--retry-failed`: the pinned 22-entry `MEASURED_PATHS` plus the prior (136–138). Without `--retry-failed`, `PREVIOUS_SOURCE` is None (447), so the prior is neither bound nor read.
- Fixture closure: `parse_path_list` (166) takes the AST literal of `MEASURED_PATHS`, and `r13_extras = [R13_PRIOR]` (988) adds the prior. That equals the runtime closure for this case.
- Fidelity caveat: the default oracle reads the live `--root` working tree (`parse_path_list` 166, `expand_closure` 212, `make_sandbox` 291–294), not the pin. The dirty verdict is unaffected, because the sandbox commits whatever prior bytes it has and the mutation is relative to that commit. Pin equivalence is not enforced. Not verified: whether the lane is clean, since no status check was run.

## 4. Predicate (fixture 673–696)

- Accept condition: `returncode == 2`, AND `census/round-13/verification.json` appears in stdout+stderr, AND output is absent, AND stdout is empty. The detail string (696) records exit, path flag, output flag, and suite-stdout flag. It records no refusal text.
- The pinned dirty path satisfies it.
- Also accepted, with the same observables:
  - `validate_previous` refusals. The print at 430 uses `args.previous`, which is the same path.
  - Helper refusals that print the relative path (symlink or nonregular measured input) or an OSError (absolute path, unreadable input).
  - "added" or "missing" for the prior.
  - `could-not-evaluate` with the path in the exception text.
- Rejected: any stdout (suite lines or retention prints), an output file created, or a refusal that does not name the prior (for example the decoy's `CalledProcessError`).
- Binding-removal check (by reading, not executed): deleting 137–138 lets the runner reach `run("evidence-selftest")` at 460, which prints to stdout, so the case FAILS. The case is therefore a valid one-sided falsifier for under-binding.

## 5. Baseline producer witness

- Fixture: none. `BASELINE_PAIR_CASE_IDS` (110–117) lists seven pairs: r13 helper, sources, and new-knowledge; r14 helper and frozen; targeted wrapper; demo helper. `run_baseline_pairs` (818; pairs 824–832) has no optional-prior pair. Baseline mode runs only with `--baseline`.
- The tripwire r13 branch (548–552) calls `module.run = producer` and `module.main(["--round","20","--output",output])`. It passes no `--retry-failed` and no `--previous`. No tripwire in the fixture exercises the optional prior on either side.
- Source-predicted red-before (not executed) on `12516f7d`:
  - `MEASURED_PATHS` (line 92, 12 entries) excludes the prior.
  - `resolve_revision` (108–116) binds only MEASURED.
  - The baseline helper's `resolve_durable` (86–149) checks only `git diff --quiet <rev> -- <measured>`.
  - `execute` parses the prior at 422, computes `before` digests at 430 (all seven `tools/souji-*` artifacts exist at that commit), and reaches `run("evidence-selftest")` at 432, which is a producer under the tripwire.
  - The pinned caller refuses. A baseline pair is feasible.
- Adding the pair as-is would FAIL on the changed side. Without `--retry-failed`, the pinned runner does not bind the prior and reaches the producer, so `changed_exit2=0`. Its baseline "producer" would also be reached without the prior involved, which is a false witness. The driver fix in §7 is a prerequisite.

## 6. Answers to the item questions

- Behavioral or wiring? Behavioral. It runs the pinned entrypoint as a subprocess, and the refusal is raised by the runner's resolver, not by wiring inspection. It is one-sided: it shows a dirty prior is bound. It shows no admission of a clean prior, no parse, and no consumption.
- Can a prerequisite refusal masquerade as the required reason? Yes. See the counterexample in §7. A present-but-untracked prior would also masquerade: the snapshot reports `added=` naming the prior, and the case passes. That is not reachable in the pinned construction. It would require `make_sandbox` to stop committing extras, or an ignore rule to exclude the file. The guard at 716 rejects only absent or nonregular targets. An absent prior raises `FixturePrerequisite` (blocked, not pass).
- Is the input consumed by this caller? Yes. `PREVIOUS = json.loads(previous.read_text())` (450) feeds `run()` retention (264–270) and is recorded as `prior_attempt` (514). The case refuses before 450, so it does not observe consumption. Non-blocking: the digest (141) and the parse (450) are separate reads. A persistent change is caught at 499–500; a change reverted inside that window is not. The helper's stated boundary excludes filesystem races.

## 7. Counterexample and bounded correction

Counterexample (source-only, not executed): insert `return None, "previous-disabled"` as the first statement of `validate_previous` (after 384). `main` (427–431) then prints `run-verification: refusing previous 'census/round-13/verification.json': previous-disabled` to stderr and returns 2. The case reports `CASE pass r13-optional-prior-dirty` with `exit=2 changed_path_named=1 output_absent=1 suite_stdout_absent=1`. That is the same line as the pinned pass. The binding at 136–138 is never reached, `--retry-failed` is unusable for clean and dirty priors, and the case still passes.

Correction (fixture only; no runner edit):

1. Reason-exact predicate for this case. Require stderr to contain `measured inputs differ from ` and `changed=['census/round-13/verification.json']`. Put the first refusal line into the CASE detail.
2. Unmutated control on the same sandbox and argv. Run it through the tripwire and require `status == "producer"` with first run name `evidence-selftest` (record `args[0]` in `producer`). That proves admission, and that the parse at 450 precedes the first run at 460. This requires the r13 tripwire branch (551–552) to pass `--retry-failed --previous census/round-13/verification.json`. That is harmless for the three existing r13 pairs: their changed sides refuse on their own inputs, and their baseline sides still parse the prior and reach the producer.
3. Add `("baseline-r13-optional-prior", "r13", ROUND13, old_r13, [], "r13", R13_PRIOR, False)` to `pairs` (824–832) and the ID to `BASELINE_PAIR_CASE_IDS` (110–117).

Predicted with the correction (not executed): the dirty case is reason-exact, the control reaches `evidence-selftest`, the new pair shows baseline producer and changed exit 2, and the §7 counterexample fails the case.

## 8. Unverified and outside scope

- Every outcome above is source-derived `[INFERENCE]`. Nothing was executed.
- `gate_reuse` passes every `INPUT_SHA256` key, including the prior, as `--require` to `tools/souji-evidence-cache.py`. Whether the gate then refuses retention for legacy priors whose `dependencies` lack the prior was not inspected, because it is outside the named files. The failure mode would be fail-closed re-execution, not unsafe. L1 may want that gate checked.
- The r14 caller files were not inspected, per item scope.

## 9. Commands executed (read-only; all exit 0)

- `git -C <lane> show 1988860…:` for `tests/fixtures/r20-input-binding.py`, `tools/souji-rev-pin.py`, and `census/round-13/run-verification.py`. Grep over the four named candidate callers, to confirm which one consumes `r13-optional-prior-dirty`.
- `git -C <lane> ls-tree -l 1988860… -- census/round-13/verification.json tests/fixtures/r13-cert-frozen tools/souji-rev-pin.py census/round-13/run-verification.py`.
- `git -C <lane> cat-file -t 12516f7d…` returned `commit`.
- `git show 12516f7d…:census/round-13/run-verification.py | sed -n 88,125p` and `sed -n 416,440p`, plus grep anchors.
- `git ls-tree 12516f7d… -- <closure paths>`. The seven `tools/souji-*` artifacts and `census/round-13/verification.json` (blob `879d96b4…`) are present.
- `git show 12516f7d…:tools/souji-rev-pin.py | sed -n 86,149p`.
- Grep anchors over the pinned runner, helper, and fixture.

No builds, tests, fixture runs, imports, git writes, status checks, installs, or subagents.

## 10. Checks for L1 (not run here)

- After the correction: run the default fixture and `--baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. Confirm that the CASE detail carries the refusal text, that the unmutated control reaches `evidence-selftest`, and that the new pair reports `baseline_tripwire=1 changed_exit2=1`.
- Mutation checks: deleting lines 137–138 must fail this case. The §7 over-refusal must fail it after the correction.

Author-side advisory only. Not non-author closure or promotion. No [x] marks.
