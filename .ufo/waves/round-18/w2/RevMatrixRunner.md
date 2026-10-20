STATUS: DONE — static operability review of `census/round-18/run-matrix.py` at `5efb519f00075d958c3d1109ef6fcb24c487eb87`; no code executed.

## Attacked claim and axes

C1 measurement-runner operability: arm selection/extraction and identity, fixture selector wiring, run validity versus test failure, process-session cleanup and residue accounting, record schema, and exclusive output creation.

## Findings (by severity)

### P2 — Residue counts are host-global and can be attributed to the wrong arm

`census/round-18/run-matrix.py:53-59` configures fixed per-fixture substring needles, not per-invocation identifiers. `leftover_processes()` scans every same-UID `/proc/*/cmdline` and returns any PID containing that needle (`:143-162`); it does not restrict matches to the just-finished run or subtract a pre-run baseline. The suite path calls it immediately after session cleanup (`:210-212`), and each fixture is invoked once per arm (`:394-397`). The same unscoped approach is used for selftest leftovers (`:377-391`).

This can misattribute a prior-arm or concurrent matrix's escaped child to the current arm. The bounded fixture uses the shared `/var/tmp/souji-r18-FixtureR18Bounded/fixture.` prefix (`tests/fixtures/r18-census-bounded.py:35,111-112`) and passes fixture-root paths in census child argv (`:498-502`), so a child left by one arm continues matching the same runner needle in later arms. The recorded per-arm `leftover_procs` values therefore are not reliable per-arm leak counts when residue remains.

**Smallest fix:** make the fixture scratch/argv marker unique to each arm-and-suite invocation and count only that marker (or record a PID+start-time baseline and report only newly observed matches, explicitly treating concurrent matching runs as unresolved).

### P3 — Mutable `--changed` refs are resolved twice

The runner resolves `args.changed` once to `changed_rev` for the top-level record (`census/round-18/run-matrix.py:297-301`), but builds the final arm from the original `args.changed` (`:335`) and resolves it again when extracting the tool (`:343-350`). If `--changed` is a branch or movable tag and changes between these points, `record.changed_rev` identifies one commit while the `changed` arm's `rev` and `sha256` identify another. This breaks the record's same-identity claim for a supported revision selector.

**Smallest fix:** use the already resolved `changed_rev` in the `changed` arm when the selector is not `WORKTREE`; keep `WORKTREE` as the explicit copy-from-worktree case.

## Reviewed behavior that holds statically

- The four fixture mappings use the expected selectors: bounded/r17 `--census`, r15/r14 `--tool` (`:53-59`). The corresponding fixture parsers accept those options; r17 explicitly aliases `--tool` to `--census` (`tests/fixtures/r17-census-hygiene.py:1213-1216`).
- Fixture validity is distinct from fixture failure: a run is valid only when the summary, non-synthetic case count, failure count, and expected exit code agree (`:225-232`). A structurally valid failing fixture remains recorded data; missing, timed-out, malformed, or otherwise invalid suites enter `invalid_suites` (`:201-208,410-420`). `bash -n`/ShellCheck/selftest nonzero results are retained as check results; inability to run or timeout is what the `ran`/`invalid_suites` path detects (`:357-387,410-420`). This matches the stated failure-versus-unrunnable distinction.
- Session cleanup is restricted to same-UID processes whose `/proc/<pid>/stat` session ID equals the runner-created session ID; it rechecks start time before signaling and uses pidfds when available (`:71-140`). Escaped-session descendants are not killed, as required by the stated policy.
- Schema is explicitly `record_schema: 3` and records resolved arm revision/hash, tool versions, fixture hashes, check/suite details, and `invalid_suites` (`:307-324,352-355,410-421`). The saved `census/round-18/c1-matrix-worktree.json:1760-1764` also has schema 3 and an empty `invalid_suites` list; this is a read-only artifact observation, not a rerun.
- Output creation is exclusive: the early existence check improves diagnostics, while the final `open(out, "x")` is the race-safe no-overwrite guard (`:265-270,423-429`).
- This runner has one fixture Python interpreter (`sys.executable`) and records `sys.version`; no alternate-runtime selector or saturation metric is present. No runtime rerouting/saturation claim is made by this file.

## Verdict

**FAILS (partial operability):** the suite flags, validity rules, same-session cleanup, schema, and exclusive-create mechanics hold by inspection, but per-arm residue attribution is unsound under persistent/concurrent matching processes, and mutable `--changed` selectors can produce a record/arm identity mismatch. Fix both before relying on the matrix as per-arm evidence.

## Residual risk and verification gaps

- The LSP device is unavailable (`xd://lsp` returned “No such tool” and the mounted-device list did not include it), so semantic references/definition/diagnostics could not be checked. The diff is a single newly added standalone runner; no caller claim is made beyond its documented CLI.
- No runtime/tests were executed: this review had no `ALLOWED-EXEC` authorization. The conclusions above are static; in particular, cross-arm contamination and the mutable-ref race were derived from the code paths, not dynamically reproduced.
- No tool was installed or updated.

## Commands and observed outputs

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --no-ext-diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- census/round-18/run-matrix.py`
  - `census/round-18/run-matrix.py | 441 ++++++++++++++++++++++++`
  - `1 file changed, 441 insertions(+), 0 deletions(-)`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5efb519f00075d958c3d1109ef6fcb24c487eb87:census/round-18/run-matrix.py | sha256sum`
  - `da61f6be8f6f544be60fe6bcd883b0afecfb36c72fa8f78faa82816e65a73846  -`
- `sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-18/run-matrix.py && git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files -- census/round-18/run-matrix.py`
  - `da61f6be8f6f544be60fe6bcd883b0afecfb36c72fa8f78faa82816e65a73846  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-18/run-matrix.py`
  - `5efb519f00075d958c3d1109ef6fcb24c487eb87`
  - `census/round-18/run-matrix.py`
