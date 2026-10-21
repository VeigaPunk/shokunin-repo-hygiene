STATUS: PARTIAL — At 1988860 the r14 gate refuses an inert `corpus/SOURCES.md` change before any stdout or output, and the case predicate matches that path (source agreement; not executed). The fixture has no red-before witness for that input or for two other r14 inputs newly bound at 1988860 (F1). As wired, `r14-sources-dirty` cannot serve as a before/after C2 falsifier. This is a real oracle gap; the current refusal itself is sound.

# InputCase13 — `r14-sources-dirty` caller falsifier (source-only, read-only)

Pinned: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. One baseline comparison: preregistered `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`, read only for its r14 caller, helper and `MEASURED_PATHS`.
Nothing executed: no fixture, caller, helper or sandbox run. No installs. No writes outside this report.
Line refs: **F** = `tests/fixtures/r20-input-binding.py`; **C** = `census/round-14/run-verification.py`; **H** = `tools/souji-rev-pin.py` (1988860). **B:** prefix = same file at 12516f7.

## Case identity
- `r14-sources-dirty` = `mutate_and_call("r14", …, "sources-dirty", "corpus/SOURCES.md")` from F:753–757, run by `run_caller_matrix` F:768–781. Listed in `expected_case_ids` F:131.
- Applicable caller only: C (`caller_specs` F:1020–1021). Not `run-targeted.py`, not r13, not demo.
- Exactly one input is changed.

## Trace
1. **Entrypoint.** `caller_command` F:660–667 runs `python -B census/round-14/run-verification.py --output census/round-20/r20-r14-sources-dirty.json` with cwd = sandbox. The sandbox copy is the committed closure (`make_sandbox` F:291–307).
2. **Inert byte.** `mutate_and_call` F:700–730 appends `\n<!-- inert r20 input-binding mutation -->\n` (`inert_suffix` F:651–657, `.md` branch) to the uncommitted working file. HEAD keeps the clean blob. Restored in `finally`.
3. **Closure.** C:32–46 `MEASURED_PATHS`, with `corpus/SOURCES.md` at C:44. F derives the same list from C (F:982–983) and refuses a plan item that is not covered (F:733–735, 762–764). All 15 closure files exist at 1988860 (`ls-tree`; the `tests/fixtures/r14-cache-frozen` directory expands to 3 files).
4. **Gate order in C.**
   - `main()` C:127 → `output_path()` C:128. Valid: `census/round-20/` exists (F:306), target absent.
   - `resolve_revision()` C:129 → C:51–73.
   - C:18 strips `GIT_*`, so the fixture's decoy `GIT_DIR` (F:676–680) is inert. H:50–51 does the same for helper calls.
   - C:59–62 helper byte-equality to HEAD passes.
   - C:67 `resolve_durable` → H:226 `input_snapshot` raises H:177–178 `Refusal("measured inputs differ from <HEAD> (missing=[] added=[] changed=['corpus/SOURCES.md'])")`. C:68 is never reached.
   - C:70 catches it (`Refusal` is a `ValueError`, H:43). C:71–73 print to stderr and `SystemExit(2)`. C:175–179 does not catch `SystemExit`, so the process exits 2.
5. **Predicate** (`caller_refusal` F:686–697):
   - exit 2: yes.
   - `corpus/SOURCES.md` in stdout+stderr: yes, via `changed=[…]`.
   - output absent: yes. `target.open("x")` is C:170, unreached.
   - stdout empty: yes. Nothing prints to stdout before the gate; progress `print` is C:124, after the gate.
   - Source-level verdict: PASS expected. Not run.
6. **Bypass sensitivity.** If the gate were skipped, stdout would get `name: exit=…` lines (C:124) and output would be written (C:170), so the predicate fails. A post-run `checked_inputs` refusal (C:159) would print progress first and also fail the predicate. The predicate therefore requires the pre-run gate.

## Behavioral or wiring
- Behavioral. It runs the real entrypoint against a real byte change in an isolated synthetic repo. It is not wiring-only.
- The naming check is a bare substring: `changed_path in combined` (F:687, F:695). It does not assert the reason text (`measured inputs differ`), the exact `changed=` list, or empty `missing`/`added`.

## Prerequisite masquerade
- For this mutation: none reachable. Every prerequisite error on the path (helper missing or differs, git failure, output path, OSError) produces text without `corpus/SOURCES.md`, so the case would FAIL rather than pass. On this route the snapshot refusal is the only producer of the path string.
- Theoretical only: `unreadable measured input: <OSError>` (H:170–171) quotes the path, so a missing or unreadable file would satisfy the predicate. An inert byte edit cannot produce that state.

## Consumption
- Consumed by C only as a hashed closure member: pre-run gate (C:67–68) and post-run `checked_inputs` (C:75–79, C:159). No r14 step reads or executes it. It is absent from the `paths` list (C:130–132).
- `sources-contract` (C:152) runs an external validator with `--root /home/vgpnk/Projects/shokunin … souji`. It is outside the closure and outside `ROOT`. C:164–165 disclaim external commands. Whether it reads `ROOT/corpus/SOURCES.md` is unobserved [INFERENCE]; the external script was out of scope.
- Corollary: the case proves closure binding, not content consumption.
- C has no knowledge-corpus input (179 lines read in full).

## Baseline producer witness
- None for `r14-sources-dirty`. F:824–839 defines seven pairs. The r14 pairs cover only `tools/souji-rev-pin.py` (F:830–831) and `tests/fixtures/r14-cache-frozen` (F:832–833).
- `BASELINE_PAIR_CASE_IDS` (F:110–118) and `expected_case_ids` (F:121–143) agree with that omission. The F docstring (F:1–16) names no exclusion.

## Findings

### F1 — PARTIAL (oracle gap; blocks red-before claims, not the current refusal)
- B:C:31–40 `MEASURED_PATHS` has 8 entries and no `corpus/SOURCES.md`. The 1988860 list (C:32–46) adds 5: `tools/souji-rev-pin.py`, `census/round-14/run-targeted.py`, `tests/fixtures/r14-cache-frozen`, `corpus/SOURCES.md`, `census/round-13/verification.json`.
- Pairs cover 2 of the 5 (helper, frozen). Uncovered: `corpus/SOURCES.md`, `census/round-14/run-targeted.py`, `census/round-13/verification.json`. The sibling `baseline-r13-sources` (F:826–827) makes the omission inconsistent.
- Feasible, not executed:
  - All 15 current r14 closure files exist at 12516f7 (`ls-tree`), so the overlay guard F:384–387 does not fire.
  - B:C:51 calls `resolve_durable(root, head, paths)`, matching the baseline signature at B:H:86.
  - The baseline tree check is `git diff --quiet rev -- <old paths>` (B:H:136). It ignores `corpus/SOURCES.md`, so the old caller accepts a dirty file and reaches `run` (B:C:112). The producer witness follows [INFERENCE from source].
  - The current caller refuses the same input, so a pair would be a true red-before.
- Consequence: `r14-sources-dirty` shows only that the current caller refuses. Nothing in F shows the pre-r20 caller accepted the same dirty input.

### F2 — non-blocking; bounded counterexample to predicate sufficiency
- Counterexample: replace the gate with `print("run-verification: refused: inputs %s" % MEASURED_PATHS, file=sys.stderr); raise SystemExit(2)`.
- Result for `r14-sources-dirty`: exit 2 ✔, `corpus/SOURCES.md` named ✔, stdout empty ✔, output absent ✔ → **PASS**.
- Not caught by any case:
  - `run_caller_matrix` (F:768–781) runs only dirty plans. No r14 caller-level clean-accept run exists.
  - Clean controls exist only at helper level (`HELPER_DRIVER` F:466–473; `helper-*` F:626–631).
  - C has no gate-only seam. `main()` takes only `--output`. A clean run executes the whole suite (C:140–153).
  - F:569 shows the demo tripwire calls `main(["--gate", …])`; r14 has no equivalent.
- Reachability from current source: none. This bounds the predicate, not C.
- Tightening: require `"measured inputs differ from" in combined and "changed=['corpus/SOURCES.md']" in combined`.

### F3 — non-blocking; external consumer unobserved
- See Consumption above.

### F4 — non-blocking; operability coupling
- F:989 `choose_existing_admitted(root)` and F:990–999 closure expansion run before any caller. A failure in the r13 plan (F:745–752) aborts `run_caller_matrix` before r14 (F:1027). So `r14-sources-dirty` can be reported as blocked rather than evaluated, for prerequisites unrelated to r14.
- `read_text` at F:641 can raise `UnicodeDecodeError` outside the `FixturePrerequisite` handler (F:1031).
- `expand_closure` (F:212–248) reads the working tree of `--root`, not the pinned commit. Nothing checks that root HEAD equals 1988860 or that the tree is clean. The "pinned" falsifier is only as pinned as the checkout.

### F5 — out of case scope (noticed during trace)
- `input_snapshot`/`capture` (H:94–179) hashes bytes only. A mode-only change on a measured executable (e.g. 755→644) is not refused [source-level; not executed].

## Proposed changes for L1 (not applied; read-only seat)
1. In F:824–839 add `baseline-r14-sources` (changed `corpus/SOURCES.md`), plus pairs for `census/round-14/run-targeted.py` and `census/round-13/verification.json`. Extend F:110–118. Confirm each red-before by running `--baseline 12516f7…` before relying on it.
2. Tighten the r14 `caller_refusal` predicate per F2.
3. Choose one: add a gate-only seam to C for a clean-accept control, or record caller acceptance as untested.
4. Decouple r14 from the r13 prerequisites (F4), or document the coupling.

## Unknowns / not checked
- No execution. The baseline witness and the F2 counterexample are source-derived.
- Not read (out of scope): `scripts/sources-census.sh`; `corpus/knowledge` admission state; transitive inputs of `census/round-14/cache-demonstration.py`; host Python version (`hashlib.file_digest` needs ≥3.11).

## Commands executed (all read-only; all exit 0)
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:tests/fixtures/r20-input-binding.py | cat -n` (elided span re-read from artifact 36867:384–485)
- `git … show 1988860…:tools/souji-rev-pin.py | cat -n`
- `git … show 1988860…:census/round-14/run-verification.py | cat -n`
- `git … ls-tree -l 1988860… -- corpus/SOURCES.md tools/souji-rev-pin.py census/round-14/run-verification.py tests/fixtures/r20-input-binding.py`
- `git … ls-tree -r --name-only 1988860… -- <13 r14 closure paths>` → 15 files
- `git … cat-file -t 12516f7…` → commit
- `git … show 12516f7…:census/round-14/run-verification.py | cat -n`
- `git … ls-tree -r --name-only 12516f7… -- <13 r14 closure paths + tests/fixtures/r20-input-binding.py>` → 15 files; no r20 fixture at baseline
- `git … ls-tree -r --name-only 1988860… -- tests/fixtures/r14-cache-frozen census/round-13/verification.json` → 4 files
- `git … cat-file -t a31642d14006830ec62edf40b0354c3699728c4a` → commit
- `git … show 12516f7…:tools/souji-rev-pin.py | cat -n`

Trailer: `.ufo/waves/round-20/final/InputCase13.md` (relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`).
