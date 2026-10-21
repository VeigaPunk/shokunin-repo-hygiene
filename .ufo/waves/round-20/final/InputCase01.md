# InputCase01 — C2 caller-case falsifier `r13-helper-dirty` (read-only, static)

- Seat: SoujiR20-2.InputCase01 (leaf, no dispatch). Attempt 1.
- Pinned build: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. All reads via
  `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show <pin>:<path>`. No runtime, no imports, no builds; no file outside this report written.
- Godspeed axes: A1 case→caller binding fidelity · A2 predicate strength (behavioral vs wiring) · A3 masquerade resistance (prerequisite refusal passing as the required reason) · A4 input-consumption proof (byte receipt) · A5 baseline witness integrity.

## 1. Applicable caller (A1)

`r13-helper-dirty` is produced only by the fixture's own id construction
`cases.add(name + "-" + case_name, …)` (`tests/fixtures/r20-input-binding.py` L722-724) from spec `{"name": "r13", …, "script": ROUND13}` (L1019-1031) and plan entry `("helper-dirty", HELPER, False)` (L739-742, guard `covered_by_measured` L763-765). So the unique caller is
`census/round-13/run-verification.py`, mutated input is `tools/souji-rev-pin.py`. The three r14 files are excluded by construction, not by name similarity; nothing r14-specific is claimed here.

## 2. Actual entrypoint and refusal path (A1, A4)

Fixture invocation (`caller_command`, L660-671): real subprocess
`python3 -B census/round-13/run-verification.py --round 20 --output census/round-20/r20-r13-helper-dirty.json --retry-failed --previous census/round-13/verification.json`, cwd = synthetic repo, env = CLEAN_ENV plus decoy `GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE`.

Caller chain: `main()` (L455+) → arg/output/prior validation (stderr-only refusals, `return 2`; sandbox has `census/round-20/` created at L303 so `--round 20` passes the `closed_round_floor` check) → `execute()` → `resolve_revision()` (L123-148):
- L131-132: `if helper.read_bytes() != committed:` (committed = `git show HEAD:tools/souji-rev-pin.py`) → `raise ValueError("tools/souji-rev-pin.py differs from measured commit")`.
- The caller's ENV (L46-55) strips all `GIT_*` except the three config vars, so the fixture's decoy selectors are dropped — the refusal comes from the sandbox repo state itself, not ambient redirection.
- L144-147: caught → stderr `run-verification: refused: tools/souji-rev-pin.py differs from measured commit (no record written)` → `SystemExit(2)`.

The inert byte: `inert_suffix(".py")` = `b"\n# inert r20 input-binding mutation\n"` appended to the working-tree helper only (L651-658, L700-731; HEAD stays clean; restored in `finally`). Syntactically inert to Python; decisive to the caller because the caller's C2 boundary is whole-file byte equality, not AST equality. The changed byte is consumed at L131 (`read_bytes()`) — that is the consumed-byte receipt; no per-byte diff is recorded (whole-file equality only).

Consumption is double: after byte equality the caller `exec_module`s the helper (L133-137) and uses `resolve_durable`/`input_snapshot` both pre-run and post-run (`inputs_after` check before writing the record). Helper = measured input *and* measuring instrument.

## 3. exit2 / no-stdout / no-output predicate (A2)

`caller_refusal` (L673-698), non-demo branch: PASS requires
`returncode == 2 AND "tools/souji-rev-pin.py" in (stdout+stderr) AND output file absent AND stdout == ""`.
Holds by design here: refusal message is stderr-only and names the full relative path; nothing prints to stdout before `resolve_revision` returns (per-check prints live in `run()`, which is never reached); the output file is opened `"x"` only at the end of `execute()`. This is a **real behavioral invocation** of the actual entrypoint with real bytes and real exit status — not wiring inspection (docstring L21-28 is accurate on this point).

## 4. Masquerade: can a prerequisite refusal pass as the required reason? (A3)

Per-case predicate is refusal-*shaped*, not refusal-*caused*: it checks that the caller's output names the changed path, not that the byte-equality comparison executed. Any caller exit-2 whose stderr contains the substring `tools/souji-rev-pin.py` satisfies `specific`. `resolve_revision` catches `(OSError, ValueError, SyntaxError, ImportError, CalledProcessError)` uniformly into the same stderr shape.

**Bounded counterexample (predicate-shape masquerade, no-`--baseline` mode):** if `git show HEAD:tools/souji-rev-pin.py` inside the sandbox raised `CalledProcessError` (blob unreachable / repository corruption), `str(exc)` embeds the failed command list containing `HEAD:tools/souji-rev-pin.py`, so the caller exits 2, names the path, writes no stdout and no output — `r13-helper-dirty` records PASS while the working-tree-vs-HEAD comparison under test never ran. Inventory checks cannot catch it (case name still present, exactly once).

Reachability bound: inside this fixture the channel is closed by construction — `expand_closure` refuses symlinks/non-regular inputs (L212-249), `commit_all` commits the helper blob (L280-289), files are written readable by the same user, and the sibling `helper-controls` arm (L595-633) proves the identical closure bytes accept at the helper API (`input-snapshot-clean`, `resolve-clean`) in a separate sandbox before the matrix runs. So the counterexample requires breaking fixture construction invariants that other arms would surface — but **the `r13-helper-dirty` case alone never attributes its refusal**. Causal closure exists only with `--baseline REV`: pair `baseline-r13-helper` (L833-835) applies the same mutation to both repos and expects the old caller to reach the suite producer (`status=="producer"`, witness==case id, output absent, L866-873) while the current caller refuses exit-2-named-stdout-empty (L874-880) — red-before evidence that the refusal is caused by the new dirty-input boundary, not by a broken sandbox. Round mode uses the preregistered baseline (`12516f7dcdd5b165e5ee208d44a38d63b5bd5812`), so in the round's actual configuration the masquerade channel is closed. [INFERENCE on baseline-arm semantics: the producer-reached expectation can only hold if the baseline-revision caller lacks the dirty-helper refusal; baseline-revision source was not read — outside this seat's named-path authorization.]

## 5. Baseline producer witness (A5)

Two witnesses, both `--baseline`-gated (L1000-1002, L1016-1017):
1. Byte witness: `compare_baseline` (L884-911) sha256-compares every closure file against the baseline revision's blobs, printing `BASELINE_MATCH`/`BASELINE_SUMMARY … mismatches=N`.
2. Producer witness: `baseline-r13-helper` tripwire pair (§4).

Observation (bounded, advisory): `Cases.summary` (L92-115) computes the exit code from case failures and inventory only — `baseline_mismatches` is printed but never affects the return value. A `--baseline` run with real byte drift against the preregistered baseline exits 0 with `BASELINE_SUMMARY … mismatches>0`. The mismatch is a report line, not a gate result. Flagging for C1 calibration review; no other seat's scope assumed.

## 6. Verdict

- Behavioral, not wiring: YES — actual entrypoint, actual argv, actual bytes, actual exit codes (§3).
- Masquerade possible? Per-case: shape-only attribution (counterexample §4); closed in-fixture by construction plus sibling control arms, and causally closed only in `--baseline` mode, which is the round's mode.
- Input actually consumed by this caller? YES — byte-equality consumption at `run-verification.py` L131 is decisive for any byte delta including the inert suffix; plus exec-consumption after equality (§2).

No blocking defect found for `r13-helper-dirty` under the fixture's construction; findings above are author-side advisory for L1.

---
Trailer (paths relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`):
- Report: `.ufo/waves/round-20/final/InputCase01.md`
- Sources read at `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`:
  - `tests/fixtures/r20-input-binding.py`
  - `census/round-13/run-verification.py`
  - `tools/souji-rev-pin.py` (structure map only: `Refusal`, `_git`, `input_snapshot`, `resolve_durable` at L43/64/94/182)
- Excluded by construction: `census/round-14/run-verification.py`, `census/round-14/run-targeted.py`, `census/round-14/cache-demonstration.py` (different fixture spec names; no r14 claims made).
- Method: `git show` piped reads only; no execution, no imports, no builds, no writes besides this report.
