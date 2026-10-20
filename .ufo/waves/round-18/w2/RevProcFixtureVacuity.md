STATUS: DONE — All three assigned stub variants were rejected by the r18 process-census fixture.

# Attacked claim

C3 fixture coverage: `tests/fixtures/r18-proc-census.sh` at `5efb519f00075d958c3d1109ef6fcb24c487eb87` should reject census implementations that list every process, omit reasons, or attach incorrect reasons to the right PIDs.

# Findings

No actionable vacuity finding in this scope. None of the three adversarial stubs passed (each fixture invocation exited 1). The fixture validates the boot-ID/header/row shape and rejects malformed or duplicate rows (`tests/fixtures/r18-proc-census.sh:188-208`); `complete_record` requires nonempty state, wchan, reason, and command (`:223-234`). The targeted checks then assert the exact `cwd-deleted`, `argv-path-gone:<path>`, and `fd-path-gone:<path>` reasons (`:365-374`, `:384-391`, `:439-445`, `:460-468`). Separate controls reject the live P3 row, require prefix selection to retain P2 but exclude P6, exclude fresh rows for `--min-age`, and omit P10 (`:398-408`, `:418-428`, `:471-472`).

# Executed probes

Isolated clone: `/var/tmp/souji-r18w2-RevProcFixtureVacuity/lane`, checked out detached at the assigned commit. Three test-only tool stubs were used; no lane files were edited. Each command below ran the named fixture against one stub:

1. `bash tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-RevProcFixtureVacuity/lane/stub-every-process.sh`
   - Output: `P1 PASS, P2 PASS, P3 FAIL, P4 FAIL, P5 FAIL, P6 PASS, P7 PASS, P8 PASS, P9 PASS, P10 FAIL, P11 PASS`; `SUMMARY total=11 failed=4`; exit 1.
   - Stub emitted a valid row for every `/proc` PID, including the P3 live control and P10 boundary, and ignored prefix/min-age filtering. Positive residue rows remained valid, so the failures specifically show the fixture rejects overbroad enumeration and ignored filters.
2. `bash tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-RevProcFixtureVacuity/lane/stub-no-reasons.sh`
   - Output: `P1 FAIL, P2 FAIL, P3 PASS, P4 PASS, P5 PASS, P6 FAIL, P7 PASS, P8 PASS, P9 FAIL, P10 PASS, P11 PASS`; `SUMMARY total=11 failed=4`; exit 1.
   - Stub selected only the four intended residue PIDs and honored prefix/age selection, but emitted an empty reason field. The reason-bearing record assertions rejected it.
3. `bash tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-RevProcFixtureVacuity/lane/stub-wrong-reasons.sh`
   - Output: `P1 FAIL, P2 FAIL, P3 PASS, P4 PASS, P5 PASS, P6 FAIL, P7 PASS, P8 PASS, P9 FAIL, P10 PASS, P11 PASS`; `SUMMARY total=11 failed=4`; exit 1.
   - Stub selected the same intended PIDs and honored prefix/age, but emitted `wrong-reason`; P1/P2/P6/P9 exact-reason assertions rejected it.

# Verification gaps and verdict

The LSP device is not mounted in this session (`read xd://lsp` returned “No such tool”; no LSP status/references/definition/diagnostics route was available). The assigned fixture was read from the exact commit and exercised only with the three allowed stubs; the real census tool was not run as part of this scoped attack. No tools were installed or updated.

Verdict: holds for the three assigned vacuity probes. Smallest fix: none indicated by these probes. Residual risk is limited to behaviors outside these three stub classes and was not evaluated here.