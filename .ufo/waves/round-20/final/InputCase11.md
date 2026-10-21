# InputCase11: C2 caller-case falsifier `r14-wrapper-dirty`

Seat: SoujiR20-2.InputCase11. Leaf, read-only, source-only. No subagents, no builds, tests, smokes or imports, no installs. No listing, search or read of the lane root, census or operator-sweep paths, and no `git status` or `git log` in the lane.

Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` (verified as `commit`). Preregistered baseline: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (verified as `commit`).

Sources, all via `git -C <lane> show <rev>:<path> | cat -n`, exit 0:
- `tests/fixtures/r20-input-binding.py` @1988860, 1039 lines, fully covered.
- `tools/souji-rev-pin.py` @1988860, 404 lines. Called "helper" below.
- `census/round-14/run-verification.py` @1988860, 179 lines. This is the applicable caller. Called "wrapper" below.
- `census/round-14/run-verification.py` @12516f7, 127 lines, for the baseline check.
- `tools/souji-rev-pin.py` @12516f7, 323 lines, for the baseline check.

Not opened, because they are not applicable: round-13 runner, `run-targeted.py`, `cache-demonstration.py`.

Axes checked: (A) behavioral or wiring; (B) consumption; (C) reason-specificity of the predicate; (D) masquerade surface; (E) baseline red-before witness; (F) operability of pin, root and interpreter.

## Verdict

- **Source agreement.** `r14-wrapper-dirty` runs the real entrypoint in a subprocess. The inert byte is consumed by the production snapshot gate before any suite command, stdout, or record write. The predicate passes for the reason it names.
- **No blocking defect. No `STATUS: PARTIAL`.** I found no current false pass.
- **Weakness, non-blocking:** the four-clause predicate is mostly a generic prerequisite-refusal signature. In this sandbox, a clean run also satisfies three of the four clauses, because it stops at a missing BASE commit. Only the path substring discriminates. The exact tightening is in section 6.
- **No baseline producer witness exists, or can exist, for this input.** The R19 helper already refuses a dirty tracked wrapper with exit 2. It just does not name the path.

## 1. Applicable caller

Fixture `mutation_plan` (L743): `("wrapper-dirty", script, False)`. For kind `r14`, `script = ROUND14 = census/round-14/run-verification.py`. The case id `r14-wrapper-dirty` is registered at fixture L130.

## 2. Trace: fixture to entrypoint to gate

1. `mutate_and_call` (L700-730) reads the wrapper (L717). It appends `b"\n# inert r20 input-binding mutation\n"` (`inert_suffix` L651-657, `.py` branch). It calls `caller_refusal`, then restores the original in `finally` (L729-730).
2. `caller_command` (L666-667) and `caller_refusal` (L673-697) run `python3 -B census/round-14/run-verification.py --output census/round-20/r20-r14-wrapper-dirty.json` with `cwd` set to the sandbox. The environment is `CLEAN_ENV` plus a decoy `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE`.
3. Wrapper import. `ROOT = Path(__file__).resolve().parents[2]` (wrapper L16) is the sandbox. `ENV` drops every `GIT_*` key from `os.environ` (L18). Wrapper git calls therefore ignore the decoy.
4. `__main__` (L174-179) calls `main()` (L127). First `output_path()` (L128; argparse and validation at L82-100; creates nothing), then `resolve_revision()` (L129).
5. `resolve_revision()` (L51-73):
   - `head = git("rev-parse","HEAD")` at L54, outside the `try`.
   - Helper byte check against `git show head:tools/souji-rev-pin.py` (L57-62).
   - Helper import (L63-66).
   - `module.resolve_durable(str(ROOT), head, MEASURED_PATHS)` at L67, which calls `input_snapshot` (helper L226).
   - On mismatch, helper `Refusal` (L172-178).
6. `Refusal(ValueError)` (helper L43) is caught at L70. stderr (L71-72) receives:
   `run-verification: refused: measured inputs differ from <head> (missing=[] added=[] changed=['census/round-14/run-verification.py']) (no record written)`
   Then `SystemExit(2)` (L73). This bypasses `__main__`'s except tuple (L177), so the process exits 2.
7. Never reached on this input: `before` hashes (L133), `git show BASE` (L138), any `run()` (L155; its stdout `print` is at L124), and the record `open("x")` (L170).

## 3. Consumption: is the input actually consumed by this caller?

Yes.
- `MEASURED_PATHS` (wrapper L32-46) includes `census/round-14/run-verification.py` at L39.
- The fixture's static parse (fixture L166-195: one top-level literal) and the runtime call (wrapper L67-68) use the same 13-entry list.
- The snapshot reads working-tree bytes with `O_NOFOLLOW` and `hashlib.file_digest` (helper L139-144). It reads HEAD blobs through `ls-tree` and `cat-file` (helper L116-129). The digests differ, so `changed=` names the wrapper (helper L176).
- Python executing the same bytes is incidental. The appended comment does not change behavior.

## 4. Behavioral or wiring?

- **Behavioral at the process boundary.** The verdict comes from exit code, stdout, stderr and output-file absence, observed from a real subprocess of the real entrypoint.
- **Wiring only gates the case.** `covered_by_measured` (fixture L762-764) and the ast literal parse decide whether the case runs at all. If the self-entry were removed, the fixture would BLOCK via `FixturePrerequisite`, not pass silently. If the runtime stopped consuming the literal, it would emit stdout or write output and the case would FAIL.

## 5. Predicate and masquerade surface (fixture L693-697)

Clauses: `rc == 2` (SystemExit(2)); `stdout_empty` (no stdout before the refusal; argparse is silent on success; `run()` prints only after a command, at L124); `output_absent` (the record is opened only at L170); and `specific`, a substring test (L687) for `census/round-14/run-verification.py` in stdout plus stderr.

**a) Reachable masquerade in the current matrix: none found.** I enumerated every exit-2 path reachable in this sandbox:
- `output_path`: no wrapper path in its message.
- `rev-parse`: no path.
- Helper byte check: names `tools/souji-rev-pin.py`.
- Snapshot: names the wrapper. This is the intended refusal.
- BASE show: names only `tools/souji-census.sh` and git's own error text.

The decoy cannot reach any wrapper or helper git call. The wrapper strips `GIT_*` at L18, and the helper's `_env()` strips them at L47-61.

**b) The triple is not a reason test.** In this sandbox, a clean run with no mutation reaches L138. The synthetic repo has a single commit, so `git show a31642d...:tools/souji-census.sh` fails and raises `CalledProcessError`. That is caught at L177: exit 2, empty stdout, output absent, and no wrapper path in the message. Only `specific` fails, which is the correct outcome, but for a prerequisite reason. The matrix has no caller-clean control (`mutation_plan` L738-765, `run_caller_matrix` L768-781). So the path substring is the only discriminator between this case's intended refusal and a BASE prerequisite refusal.

**c) Bounded counterexample to predicate sufficiency (latent; not produced by the current matrix).** Suppose the entrypoint cannot be opened when Python starts, for example unreadable mode applied between the inert write and the invocation. CPython then fails before `main()` with `can't open file '...census/round-14/run-verification.py': [Errno 13] ...` and exits 2 `[INFERENCE: CPython's file-open failure path returns 2; not executed in this seat]`. All four clauses pass, and neither `resolve_revision` nor `input_snapshot` ever runs. `mutate_and_call` cannot produce this today, because it reads the file at L717 before writing text and never changes modes. Helper prerequisite messages that name the path pass the same way: `unreadable measured input: ...<abs>/census/round-14/run-verification.py` (helper L171), and `symlink measured input census/round-14/run-verification.py` (helper L139, L156, L159).

## 6. Proposed correction (not applied; production untouched)

Replace the path-only clause for this case with the snapshot-specific text that the pinned helper emits at helper L177-178:
- `"measured inputs differ from " in combined`
- `"changed=['census/round-14/run-verification.py']" in combined`

This excludes BASE-missing refusals (no snapshot text), unreadable and symlink refusals (different prefixes), and CPython can't-open failures (no snapshot text). It touches only this case. The pinned helper emits this exact text for this mutation, which I derived from source and did not execute. So no current PASS should flip. This is the smallest safe move. It improves axes C and D and harms none.

## 7. Baseline witness (12516f7)

- The baseline wrapper already self-binds. Its `MEASURED_PATHS` includes `census/round-14/run-verification.py` at L38. So self-binding is not new in R20.
- The baseline helper's `resolve_durable` runs `git diff --quiet rev -- paths` (L136). A dirty tracked wrapper gives exit 1, then `Refusal("tracked measured paths differ from ...")` (L137-141), then exit 2. No path is named. So the baseline refuses this input, and a producer tripwire cannot witness it. The seven `BASELINE_PAIR_CASE_IDS` (fixture L110-118) omit it, which is consistent with that.
- The baseline helper's `_env()` keeps `GIT_*` (L45-53). Under this case's decoy environment, the baseline refuses earlier, at `rev-parse --verify`, with "does not resolve to a commit", also with no path. So the baseline's red for this case reflects missing path naming plus ambient redirection. It does not reflect acceptance of the dirty byte.
- The baseline `MEASURED_PATHS` (L31-40) lacks `tools/souji-rev-pin.py`, `census/round-14/run-targeted.py`, `tests/fixtures/r14-cache-frozen`, `corpus/SOURCES.md` and `census/round-13/verification.json`. Those are the R19 closure gaps. They are not this case.

## 8. Operability caveats for L1 (none blocks this case)

1. **Root binding.** `expand_closure` (fixture L212-248) copies `--root` working-tree bytes into a synthetic commit. It does not read blobs at 1988860, and it does not check the root's HEAD or cleanliness. This case's PASS therefore describes whatever wrapper bytes `--root` holds. For pin-bound acceptance, run the fixture from a clean clone at 1988860.
2. **Interpreter.** The pinned helper calls `hashlib.file_digest` (helper L144), which needs Python 3.11 or later (stdlib fact). On an older interpreter this raises `AttributeError`, which is outside the wrapper's except tuple. That exits 1 with a traceback and FAILs, rather than masquerading. The host interpreter was not probed `[INFERENCE]`.
3. **No caller can complete in its sandbox.** BASE `a31642d...` is absent from every synthetic sandbox, so every caller case observes only refusals. A true clean control would need BASE present in the sandbox. That is out of scope here.
4. **External inputs outside the closure.** The wrapper declares these "not attested" (L164-165): `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (L109), `shellcheck` (L106), and `python3` and `bash` from PATH. They are not part of this case.

## 9. Checks for L1 (not run by this seat)

- From a clean clone at 1988860, run `python3 -B tests/fixtures/r20-input-binding.py` and confirm `CASE pass r14-wrapper-dirty`.
- If the section 6 tightening is adopted, the same run should still PASS `r14-wrapper-dirty`, now with the stricter token.

## 10. Execution record

- `git -C <lane> cat-file -t 1988860...` returned `commit` (exit 0). `rev-parse --verify --quiet ...^{commit}` returned `1988860...` (exit 0).
- `git -C <lane> show 1988860...:<path> | cat -n` for the three pinned files (exit 0). `wc -l` on the wrapper returned 179.
- `git -C <lane> cat-file -t 12516f7...` returned `commit` (exit 0). `git show 12516f7...:census/round-14/run-verification.py | cat -n` and `git show 12516f7...:tools/souji-rev-pin.py | cat -n` (exit 0).
- No builds, tests, smokes, imports or target-code execution. No installs. The only write is this report.
