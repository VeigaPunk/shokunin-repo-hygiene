STATUS: DONE — 17 isolated single mutants: 10 killed, 7 survived; over-firing duplicate-parse survivor falsifies D6 calibration; all copies restored exactly and all 34 restoration detector runs passed.
# MutateGateExact — round 17 wave 2
## Scoped verdict
**Fails — D6 calibration, not a claim that the pristine gate currently emits bad findings.** The same landed selftest and external fixture both accept M03, which emits every cited-script parse finding twice. The selftest reports `SELFTEST\tpass=28\tfail=0`; the fixture reports `SUMMARY\ttotal=15\tfailed=0`. In the external fixture, `unterminated-case` grows from `lg_rows=1` to `lg_rows=2`, and `py-compile-defects` grows from 2 to 4, yet both remain PASS. This is a non-equivalent over-firing survivor, so it fails the task's explicit D6 condition.
**Combined result:** 10 killed / 7 survived / 0 inconclusive mutants. The selftest alone kills the same 10; the external fixture kills 2 (fence inclusion and always-firing measured mismatch). Successful pristine baselines and successful exact-byte restoration runs bracket every mutant result. Two initial sandbox-startup failures occurred before Python ran and are disclosed separately, not counted as mutant kills.
## Findings and smallest fixes (all gate line references are at ddb7347)
### F1 — Exact id sets still erase duplicate findings (fails)
- `tools/souji-landing-gate.py:858-864` builds a set of ids, and finding cardinality is optional. The cited-shell and cited-Python cases at `:904` and `:910` omit `expect_n`. M03 adds exactly one duplicate append at `:630` and survives both detectors.
- Control: M01 adds the *different* id `LG-SEAT-UNCARRIED` at the same point and is killed by the selftest (26 pass / 2 fail). M02 duplicates a seat finding and is killed where `expect_n=1` exists (24 pass / 4 fail). Thus the survivor is specifically the unasserted multiplicity, not a failed baseline or a globally disabled test.
- Smallest fix: add `expect_n=1` to the two cited-script positive cases. The maintainable closure is to require exact cardinality/id multiplicity for every positive case, rather than default to a set-only assertion. The external fixture's `tests/fixtures/r16-landing-gate.py:177-194` likewise checks only selected need/absent predicates; it accepts all three M01/M02/M03 over-firings.
### F2 — SUMMARY observability is only partially tested (partial)
- Literal-zero evaluation counters at `tools/souji-landing-gate.py:650` (`checked_pins`), `:658` (`checked_markers`), `:659` (`checked_reports`) and an inserted reset after `:661` (`checked_reg`) all survive both detectors (M11–M14).
- M17 changes only the TSV SUMMARY measured-count argument at `:687` to 0 and also survives both. `run_selftest().check()` at `:857` inspects `evaluate()` directly; it never exercises `emit()` serialization at `:676-724`. External assertions at `tests/fixtures/r16-landing-gate.py:486-495` require `findings=0`, not exact branch counts.
- Controls: M10 (`checked_measured` increment), M15 (`status_lines`) and M16 (`carry_heading`) are killed by their existing in-memory count assertions.
- Smallest fix: add exact positive/zero expectations for *all* documented counters in the existing clean/marker synthetic worlds, and parse emitted TSV SUMMARY from at least one measured-branch CLI run. Do not equate the currently exercised three count fields with complete SUMMARY coverage. The fixture suppresses raw child SUMMARY rows, so this report does not fabricate child count output; the evidence is the exact mutations plus both detectors' observed acceptance.
### F3 — S3 test poisons too late to detect a lost startup filter (partial)
- The production snapshot is built at `tools/souji-landing-gate.py:130-144`. The ambient test sets `os.environ` only at `:1175-1176`, after that snapshot was made. M09 removes only the selector filter, retaining the snapshot and the no-lazy-fetch/no-replace flags, and still gets 28/0 and 15/0.
- Control: full S3 forwarding reversion M08 is killed: ambient-git-dir returns exit 2 with `fatal: not a git repository: '/nonexistent/souji-r17.git'` (27 pass / 1 fail).
- Smallest fix: in the existing selftest, invoke the gate as a child with GIT_DIR/GIT_WORK_TREE already poisoned at process start, against an already-built scratch repository, and assert requested-root resolution. This is a test-coverage defect; it does not assert that the unmutated filtering comprehension is wrong. No extra poisoned-at-start detector was run here.
### Challenged guards that held
- S1 reversion M06 was killed by measured-tree-path-exit2: mutant exit 1 with `LG-FROZEN-MEASURED` and `LG-FROZEN-PIN`, versus pristine exit 2.
- S2 reversion M07 was killed: null and empty `files` report clean (two observed FAIL rows), then non-object `files` raises `AttributeError`; the detector exits 1 before a final SELFTEST line. This is not reported as a completed 28-case run.
- The fence inclusion regression M04 was killed by selftest cardinality and external negative-control SeatF; always-firing measured check M05 was killed by clean-measured and the external clean world. No production fixes were applied by this seat.
## Axes, bounds, and detector method
- Axes: over-firing precision; under-firing/guard sensitivity; exit-2 totality; SUMMARY observability; byte restoration; scratch isolation.
- Gate bytes: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb7347:tools/souji-landing-gate.py`, captured as UTF-8 and copied exactly with the write tool helper. Length 50199 bytes; SHA-256 `c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f`. Every one of 17 copies began from those same bytes. Mutants are independent, never cumulative.
- Fixture: `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool <copy>`. Its executed bytes hash `eb7ad2045c37884ade042bbcd18d34a00fb1ac62ec9977251cfd0b735e7ec69b`, equal to its bytes at ddb7347. No fixture modification.
- Per run the two allowed detectors were `python3 <copy> --selftest` and `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool <copy>`, under existing `/usr/bin/bwrap`. A read-only host root, network namespace, and writable `/var/tmp` bind to a distinct subdirectory of `/var/tmp/souji-r17-MutateGateExact/runs/` confine the programs' hard-coded temporary directories to this seat's scratch without modifying pristine gate/fixture bytes. The scratch source tree is bound read-only back at `/var/tmp/souji-r17-MutateGateExact` inside the sandbox.
- Wrapper environment inherited the session environment after removing GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES and GIT_COMMON_DIR; it set `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR=/var/tmp`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`. The selftest's own S3 case still adds its documented poison.
- Detectors ran concurrently, maximum 6 processes at once, each with a 180-second deadline. There were 70 completed detector executions: 2 pristine, 34 mutated, 34 restored. No timeout. Baseline and restored results are 28/0 selftest and 15/0 fixture. No git write or jj invocation in a lane/fleet repository; historical fixture replay uses only committed lane reads.
- Tools installed/updated: none. No source, fixture, documentation or contract was changed; only this requested report persists.
## Mutant matrix
`S` = built-in selftest; `F` = external fixture. A kill requires a passing pristine baseline and a failing mutant detector; restoration also passed. `S pass/fail` and `F total/failed` below are actual detector output fields.
| Mutant | Mutation site at ddb7347 | S rc; pass/fail | F rc; total/failed | Verdict |
|---|---|---|---|---|
| M01-extra-seat-id | `tools/souji-landing-gate.py:630` | 1; SELFTEST pass=26 fail=2 | 0; SUMMARY total=15 failed=0 | **KILLED** |
| M02-duplicate-seat | `tools/souji-landing-gate.py:409` | 1; SELFTEST pass=24 fail=4 | 0; SUMMARY total=15 failed=0 | **KILLED** |
| M03-duplicate-parse | `tools/souji-landing-gate.py:630` | 0; SELFTEST pass=28 fail=0 | 0; SUMMARY total=15 failed=0 | **SURVIVED** |
| M04-fence-inclusion | `tools/souji-landing-gate.py:313` | 1; SELFTEST pass=27 fail=1 | 1; SUMMARY total=15 failed=1 | **KILLED** |
| M05-always-measured-mismatch | `tools/souji-landing-gate.py:567` | 1; SELFTEST pass=25 fail=3 | 1; SUMMARY total=15 failed=1 | **KILLED** |
| M06-S1-revert | `tools/souji-landing-gate.py:190-209` | 1; SELFTEST pass=27 fail=1 | 0; SUMMARY total=15 failed=0 | **KILLED** |
| M07-S2-revert | `tools/souji-landing-gate.py:458-467` | 1; no SELFTEST: 2 FAIL rows then AttributeError | 0; SUMMARY total=15 failed=0 | **KILLED** |
| M08-S3-revert-forwarding | `tools/souji-landing-gate.py:161,200,548,741` | 1; SELFTEST pass=27 fail=1 | 0; SUMMARY total=15 failed=0 | **KILLED** |
| M09-S3-unfiltered-snapshot | `tools/souji-landing-gate.py:130-142` | 0; SELFTEST pass=28 fail=0 | 0; SUMMARY total=15 failed=0 | **SURVIVED** |
| M10-measured-counter-zero | `tools/souji-landing-gate.py:555` | 1; SELFTEST pass=26 fail=2 | 0; SUMMARY total=15 failed=0 | **KILLED** |
| M11-pins-counter-zero | `tools/souji-landing-gate.py:650` | 0; SELFTEST pass=28 fail=0 | 0; SUMMARY total=15 failed=0 | **SURVIVED** |
| M12-markers-counter-zero | `tools/souji-landing-gate.py:658` | 0; SELFTEST pass=28 fail=0 | 0; SUMMARY total=15 failed=0 | **SURVIVED** |
| M13-reports-counter-zero | `tools/souji-landing-gate.py:659` | 0; SELFTEST pass=28 fail=0 | 0; SUMMARY total=15 failed=0 | **SURVIVED** |
| M14-registry-counter-zero | `tools/souji-landing-gate.py:661` | 0; SELFTEST pass=28 fail=0 | 0; SUMMARY total=15 failed=0 | **SURVIVED** |
| M15-status-counter-zero | `tools/souji-landing-gate.py:397` | 1; SELFTEST pass=23 fail=5 | 0; SUMMARY total=15 failed=0 | **KILLED** |
| M16-heading-counter-zero | `tools/souji-landing-gate.py:661` | 1; SELFTEST pass=26 fail=2 | 0; SUMMARY total=15 failed=0 | **KILLED** |
| M17-wire-measured-zero | `tools/souji-landing-gate.py:687` | 0; SELFTEST pass=28 fail=0 | 0; SUMMARY total=15 failed=0 | **SURVIVED** |

## Exact mutations and expected detectors
### M01-extra-seat-id

- Site: `tools/souji-landing-gate.py:630` at ddb7347.
- Mutant: Append an extra `LG-SEAT-UNCARRIED` on a cited-script parse failure.
- Expected detector: Exact ids in `nonparsing-cited-sh` / `nonparsing-cited-py`.
- Mutated SHA-256: `2e5fb856afe703d710f923777252962a6dc312f031fbd9de05951b5da1b24137`.
### M02-duplicate-seat

- Site: `tools/souji-landing-gate.py:409` at ddb7347.
- Mutant: Append the identical `LG-SEAT-UNCARRIED` twice.
- Expected detector: `expect_n=1` on uncarried, bold, fence and table cases.
- Mutated SHA-256: `c3ce53c8b184ac13349083c0a5b07671b8a833a70c967a57289182f7dab8e28c`.
### M03-duplicate-parse

- Site: `tools/souji-landing-gate.py:630` at ddb7347.
- Mutant: Append the identical `LG-PARSE-REG` twice.
- Expected detector: Cited-script cases should reject two findings instead of one; currently only the id set is required.
- Mutated SHA-256: `7bfe3edd95645be94d7ec6a0ade723fd735a56f0c694a608718e0ddaca1365bd`.
### M04-fence-inclusion

- Site: `tools/souji-landing-gate.py:313` at ddb7347.
- Mutant: Replace `if in_fence or in_table:` with `if in_table:`.
- Expected detector: `status-in-fence` cardinality; external `marker-rewordings` negative control SeatF.
- Mutated SHA-256: `9a4e6c372ae59ca19f0ff9abb50a994af5703a907601decb119838f26fc59c90`.
### M05-always-measured-mismatch

- Site: `tools/souji-landing-gate.py:567` at ddb7347.
- Mutant: Replace `elif sha256(blob) != pinned:` with `elif sha256(blob):` (always truthy).
- Expected detector: `clean-measured`, measured finding cardinalities; external `clean-all-green`.
- Mutated SHA-256: `1a2de3e7c1cf289321d8438120db878795c22f24b3cd915d829cda42365b6195`.
### M06-S1-revert

- Site: `tools/souji-landing-gate.py:190-209` at ddb7347.
- Mutant: Restore the old direct `cat-file blob REV:path`; map every nonzero rc to absent. Keep the independent S3 environment fix.
- Expected detector: `measured-tree-path-exit2` must stay exit 2 with no findings.
- Mutated SHA-256: `3fbc7009a263892167f3fcf41b27927296a987f453db8e85761cfe96921f7200`.
### M07-S2-revert

- Site: `tools/souji-landing-gate.py:458-467` at ddb7347.
- Mutant: Restore `files = expected.get("files") or {}` and remove the shape/empty guard.
- Expected detector: `files-null-exit2`, `files-empty-exit2`, `files-nonobject-exit2` must all stay exit 2.
- Mutated SHA-256: `23cc3fab5e4651824e2cdda691560dc6b0dc2e165f00f51c9cd3f7f617a5b520`.
### M08-S3-revert-forwarding

- Site: `tools/souji-landing-gate.py:161,200,548,741` at ddb7347.
- Mutant: Remove `env=GIT_ENV` from all three production git subprocess sites and restore selftest repo creation to `dict(os.environ)`; one S3 forwarding reversion.
- Expected detector: `ambient-git-dir` must resolve the requested scratch root despite poisoned ambient selectors.
- Mutated SHA-256: `310be94da02a4156a1dc1e5040f0cafcd829690109d517c50c427804e4a71645`.
### M09-S3-unfiltered-snapshot

- Site: `tools/souji-landing-gate.py:130-142` at ddb7347.
- Mutant: Replace the repository-selector-filtering comprehension with `GIT_ENV = dict(os.environ)`; retain both no-lazy-fetch/no-replace flags.
- Expected detector: Poisoned-at-process-start environment should be rejected; current selftest poisons only after the environment snapshot exists.
- Mutated SHA-256: `e176cef67b417dfda163a934442bc9e870edc65d976570fe429d9ed830393f3b`.
### M10-measured-counter-zero

- Site: `tools/souji-landing-gate.py:555` at ddb7347.
- Mutant: Replace `n_measured += 1` with `n_measured += 0`.
- Expected detector: `checked_measured=2` assertions in clean-measured and frozen-measured.
- Mutated SHA-256: `e83f0527c2d8e5a0c1772142c963ad08a2d057e9022fbfb59dec0f9832375869`.
### M11-pins-counter-zero

- Site: `tools/souji-landing-gate.py:650` at ddb7347.
- Mutant: Replace `result["checked_pins"] = n_pins` with literal 0.
- Expected detector: Exact positive frozen-pin comparison counter in an existing synthetic case.
- Mutated SHA-256: `2b193d30481ad0bb04235b2e2ec8a2aa46d442ae680a3411d7b07223f2e59fbf`.
### M12-markers-counter-zero

- Site: `tools/souji-landing-gate.py:658` at ddb7347.
- Mutant: Replace `result["checked_markers"] = n_markers` with literal 0.
- Expected detector: Exact positive marker count on an existing failure-channel case.
- Mutated SHA-256: `da48b8402e919bf30a4a64088bf3c3f2669bad6476082189a3dbabe163f6ddc9`.
### M13-reports-counter-zero

- Site: `tools/souji-landing-gate.py:659` at ddb7347.
- Mutant: Replace `result["checked_reports"] = n_reports` with literal 0.
- Expected detector: Exact positive report count on an existing report-bearing case.
- Mutated SHA-256: `8bc0cb0b11abd6a2e7395111428bc0dabb3be59066567cbe82edeb4d3ac52a8c`.
### M14-registry-counter-zero

- Site: `tools/souji-landing-gate.py:661` at ddb7347.
- Mutant: Insert `result["checked_reg"] = 0` after the branch counts are assigned.
- Expected detector: Exact positive registry comparison count on an existing cited-script case.
- Mutated SHA-256: `4a5852181d76d3773e05cc40599ebfa5bddd714eb4e389e6c4ae9b9e90b59965`.
### M15-status-counter-zero

- Site: `tools/souji-landing-gate.py:397` at ddb7347.
- Mutant: Replace `n_status += status_line_count(text)` with `n_status += 0`.
- Expected detector: Existing `status_lines` assertions, including fenced lines.
- Mutated SHA-256: `923f0904b25475f11d2da13fb73867c84376969f457aab301ad8502061b0d8aa`.
### M16-heading-counter-zero

- Site: `tools/souji-landing-gate.py:661` at ddb7347.
- Mutant: Replace the Boolean `carry_heading` count assignment with literal 0.
- Expected detector: Existing carried-open and carried-resolved `carry_heading=1` assertions.
- Mutated SHA-256: `230302ba712f884e6fe7bde9d0dd218ad48749f0deb8588bc48a24c59be76aa8`.
### M17-wire-measured-zero

- Site: `tools/souji-landing-gate.py:687` at ddb7347.
- Mutant: In TSV SUMMARY interpolation only, serialize literal 0 instead of `result["checked_measured"]`; evaluation and JSON construction remain unchanged.
- Expected detector: Serialized SUMMARY count assertion on a measured branch, not merely an in-memory result assertion.
- Mutated SHA-256: `94238e2111b4e54661bfbb4b38db7a6cb10c2a0331dd781997cc25d8fc5aef5d`.

## Restoration and hash evidence
All initial and restored gate copies have SHA-256 `c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f`; every mutated hash differs from it. Each of the 17 mutant paths was replaced wholesale with the exact originally captured source text after probing, then checked by sha256sum and byte-for-byte cmp against the untouched pristine copy. All 17 cmp commands returned 0 with empty stdout/stderr. All 34 post-restoration detector runs returned 0. The fixture hash was unchanged.

### Pre-restoration hashes (mutated copies plus pristine and fixture)

```text
sha256sum /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M01-extra-seat-id.py /var/tmp/souji-r17-MutateGateExact/M02-duplicate-seat.py /var/tmp/souji-r17-MutateGateExact/M03-duplicate-parse.py /var/tmp/souji-r17-MutateGateExact/M04-fence-inclusion.py /var/tmp/souji-r17-MutateGateExact/M05-always-measured-mismatch.py /var/tmp/souji-r17-MutateGateExact/M06-S1-revert.py /var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py /var/tmp/souji-r17-MutateGateExact/M08-S3-revert-forwarding.py /var/tmp/souji-r17-MutateGateExact/M09-S3-unfiltered-snapshot.py /var/tmp/souji-r17-MutateGateExact/M10-measured-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M11-pins-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M12-markers-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M13-reports-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M14-registry-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M15-status-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M16-heading-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M17-wire-measured-zero.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/pristine.py
2e5fb856afe703d710f923777252962a6dc312f031fbd9de05951b5da1b24137  /var/tmp/souji-r17-MutateGateExact/M01-extra-seat-id.py
c3ce53c8b184ac13349083c0a5b07671b8a833a70c967a57289182f7dab8e28c  /var/tmp/souji-r17-MutateGateExact/M02-duplicate-seat.py
7bfe3edd95645be94d7ec6a0ade723fd735a56f0c694a608718e0ddaca1365bd  /var/tmp/souji-r17-MutateGateExact/M03-duplicate-parse.py
9a4e6c372ae59ca19f0ff9abb50a994af5703a907601decb119838f26fc59c90  /var/tmp/souji-r17-MutateGateExact/M04-fence-inclusion.py
1a2de3e7c1cf289321d8438120db878795c22f24b3cd915d829cda42365b6195  /var/tmp/souji-r17-MutateGateExact/M05-always-measured-mismatch.py
3fbc7009a263892167f3fcf41b27927296a987f453db8e85761cfe96921f7200  /var/tmp/souji-r17-MutateGateExact/M06-S1-revert.py
23cc3fab5e4651824e2cdda691560dc6b0dc2e165f00f51c9cd3f7f617a5b520  /var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py
310be94da02a4156a1dc1e5040f0cafcd829690109d517c50c427804e4a71645  /var/tmp/souji-r17-MutateGateExact/M08-S3-revert-forwarding.py
e176cef67b417dfda163a934442bc9e870edc65d976570fe429d9ed830393f3b  /var/tmp/souji-r17-MutateGateExact/M09-S3-unfiltered-snapshot.py
e83f0527c2d8e5a0c1772142c963ad08a2d057e9022fbfb59dec0f9832375869  /var/tmp/souji-r17-MutateGateExact/M10-measured-counter-zero.py
2b193d30481ad0bb04235b2e2ec8a2aa46d442ae680a3411d7b07223f2e59fbf  /var/tmp/souji-r17-MutateGateExact/M11-pins-counter-zero.py
da48b8402e919bf30a4a64088bf3c3f2669bad6476082189a3dbabe163f6ddc9  /var/tmp/souji-r17-MutateGateExact/M12-markers-counter-zero.py
8bc0cb0b11abd6a2e7395111428bc0dabb3be59066567cbe82edeb4d3ac52a8c  /var/tmp/souji-r17-MutateGateExact/M13-reports-counter-zero.py
4a5852181d76d3773e05cc40599ebfa5bddd714eb4e389e6c4ae9b9e90b59965  /var/tmp/souji-r17-MutateGateExact/M14-registry-counter-zero.py
923f0904b25475f11d2da13fb73867c84376969f457aab301ad8502061b0d8aa  /var/tmp/souji-r17-MutateGateExact/M15-status-counter-zero.py
230302ba712f884e6fe7bde9d0dd218ad48749f0deb8588bc48a24c59be76aa8  /var/tmp/souji-r17-MutateGateExact/M16-heading-counter-zero.py
94238e2111b4e54661bfbb4b38db7a6cb10c2a0331dd781997cc25d8fc5aef5d  /var/tmp/souji-r17-MutateGateExact/M17-wire-measured-zero.py
eb7ad2045c37884ade042bbcd18d34a00fb1ac62ec9977251cfd0b735e7ec69b  /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
```
### Post-restoration hashes

```text
sha256sum /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M01-extra-seat-id.py /var/tmp/souji-r17-MutateGateExact/M02-duplicate-seat.py /var/tmp/souji-r17-MutateGateExact/M03-duplicate-parse.py /var/tmp/souji-r17-MutateGateExact/M04-fence-inclusion.py /var/tmp/souji-r17-MutateGateExact/M05-always-measured-mismatch.py /var/tmp/souji-r17-MutateGateExact/M06-S1-revert.py /var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py /var/tmp/souji-r17-MutateGateExact/M08-S3-revert-forwarding.py /var/tmp/souji-r17-MutateGateExact/M09-S3-unfiltered-snapshot.py /var/tmp/souji-r17-MutateGateExact/M10-measured-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M11-pins-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M12-markers-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M13-reports-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M14-registry-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M15-status-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M16-heading-counter-zero.py /var/tmp/souji-r17-MutateGateExact/M17-wire-measured-zero.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/pristine.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M01-extra-seat-id.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M02-duplicate-seat.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M03-duplicate-parse.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M04-fence-inclusion.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M05-always-measured-mismatch.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M06-S1-revert.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M08-S3-revert-forwarding.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M09-S3-unfiltered-snapshot.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M10-measured-counter-zero.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M11-pins-counter-zero.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M12-markers-counter-zero.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M13-reports-counter-zero.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M14-registry-counter-zero.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M15-status-counter-zero.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M16-heading-counter-zero.py
c7e8eea554b73f8183833af42e6ab9d78e66681ad41eb15394e0befdf728917f  /var/tmp/souji-r17-MutateGateExact/M17-wire-measured-zero.py
eb7ad2045c37884ade042bbcd18d34a00fb1ac62ec9977251cfd0b735e7ec69b  /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
```
### Exact byte comparisons

```text
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M01-extra-seat-id.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M02-duplicate-seat.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M03-duplicate-parse.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M04-fence-inclusion.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M05-always-measured-mismatch.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M06-S1-revert.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M08-S3-revert-forwarding.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M09-S3-unfiltered-snapshot.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M10-measured-counter-zero.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M11-pins-counter-zero.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M12-markers-counter-zero.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M13-reports-counter-zero.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M14-registry-counter-zero.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M15-status-counter-zero.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M16-heading-counter-zero.py
exit=0 stdout='' stderr=''
cmp -- /var/tmp/souji-r17-MutateGateExact/pristine.py /var/tmp/souji-r17-MutateGateExact/M17-wire-measured-zero.py
exit=0 stdout='' stderr=''
```

## Other setup commands and observed outputs
```text
command -v python3 bwrap unshare git
/usr/bin/python3
/usr/bin/bwrap
/usr/bin/unshare
/usr/bin/git
```
`git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5fa6017:tools/souji-landing-gate.py` was read to ground the S1/S2/S3 reversions. Observed old behavior: direct cat-file failures return None; `files = expected.get("files") or {}`; git subprocesses inherit their environment. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff 5fa6017 ddb7347 -- tools/souji-landing-gate.py` reported 1 file changed, 323 insertions and 88 deletions. These commands were read-only. Exact named-file reads inspected the fixture CLI and mutation sites; the report destination was absent when checked.

## Sandbox startup attempts (not detector kills)
The first wrapper used a source mount destination directly under read-only `/`; bwrap rejected it before starting Python. Correcting the destination to the scratch-bound `/var/tmp` made both pristine baselines pass.

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/pristine-before-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /mutation-sources --chdir /var/tmp -- python3 /mutation-sources/pristine.py --selftest
exit=1
stdout:
stderr:
bwrap: Can't create file /mutation-sources: Read-only file system
```

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/pristine-before-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /mutation-sources --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /mutation-sources/pristine.py
exit=1
stdout:
stderr:
bwrap: Can't create file /mutation-sources: Read-only file system
```

## Full captured detector commands and outputs
The following stdout/stderr are verbatim captures, not reconstructed expected output. The same two detector entrypoints run on common pristine bytes, each single mutant, and every restored path. Paths and synthetic commit ids in output are preserved as observed.

### pristine / baseline / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/pristine-baseline-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/pristine.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### pristine / baseline / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/pristine-baseline-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/pristine.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M01-extra-seat-id / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M01-extra-seat-id-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M01-extra-seat-id.py --selftest
exit=1
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	FAIL	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG', 'LG-SEAT-UNCARRIED'] err=None
CASE	FAIL	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG', 'LG-SEAT-UNCARRIED'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=26	fail=2
stderr:
```

### M01-extra-seat-id / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M01-extra-seat-id-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M01-extra-seat-id.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=6
CASE	unterminated-case	PASS	exit=1 lg_rows=2
CASE	py-compile-defects	PASS	exit=1 lg_rows=4
CASE	truncated-heredoc	PASS	exit=1 lg_rows=2
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M02-duplicate-seat / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M02-duplicate-seat-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M02-duplicate-seat.py --selftest
exit=1
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	FAIL	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	FAIL	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	FAIL	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	FAIL	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=24	fail=4
stderr:
```

### M02-duplicate-seat / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M02-duplicate-seat-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M02-duplicate-seat.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=6
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=2
CASE	marker-rewordings	PASS	exit=1 lg_rows=8
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=2
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M03-duplicate-parse / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M03-duplicate-parse-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M03-duplicate-parse.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M03-duplicate-parse / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M03-duplicate-parse-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M03-duplicate-parse.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=6
CASE	unterminated-case	PASS	exit=1 lg_rows=2
CASE	py-compile-defects	PASS	exit=1 lg_rows=4
CASE	truncated-heredoc	PASS	exit=1 lg_rows=2
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M04-fence-inclusion / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M04-fence-inclusion-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M04-fence-inclusion.py --selftest
exit=1
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	FAIL	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=27	fail=1
stderr:
```

### M04-fence-inclusion / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M04-fence-inclusion-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M04-fence-inclusion.py
exit=1
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	FAIL	exit=1 lg_rows=5 FAIL(unexpected LG-SEAT-UNCARRIED ~ SeatF)
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=1
stderr:
```

### M05-always-measured-mismatch / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M05-always-measured-mismatch-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M05-always-measured-mismatch.py --selftest
exit=1
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	FAIL	clean-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	FAIL	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	FAIL	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=25	fail=3
stderr:
```

### M05-always-measured-mismatch / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M05-always-measured-mismatch-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M05-always-measured-mismatch.py
exit=1
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=6
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=3
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	FAIL	exit=1 lg_rows=2 FAIL(exit=1 want 0 (stderr=); missing SUMMARY ~ findings=0; unexpected LG-FROZEN-MEASURED ~ )
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=1
stderr:
```

### M06-S1-revert / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M06-S1-revert-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M06-S1-revert.py --selftest
exit=1
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	FAIL	measured-tree-path-exit2	exit=1 ids=['LG-FROZEN-MEASURED', 'LG-FROZEN-PIN'] err=None
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=27	fail=1
stderr:
```

### M06-S1-revert / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M06-S1-revert-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M06-S1-revert.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M07-S2-revert / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M07-S2-revert-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py --selftest
exit=1
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	FAIL	files-null-exit2	exit=0 ids=[] err=None
CASE	FAIL	files-empty-exit2	exit=0 ids=[] err=None
stderr:
Traceback (most recent call last):
  File "/var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py", line 1231, in <module>
    sys.exit(main())
             ~~~~^^
  File "/var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py", line 1219, in main
    return run_selftest()
  File "/var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py", line 1044, in run_selftest
    check(case_name, repo, 2, rev=rev,
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
          expect_err="'files' is absent, falsy or not an object")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py", line 848, in check
    res = evaluate(repo, rev, 16, base=base)
  File "/var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py", line 639, in evaluate
    pin_findings, n_pins, n_measured = check_frozen_pins(root, tree, resolved)
                                       ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py", line 461, in check_frozen_pins
    for key, pinned in sorted(files.items()):
                              ^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'items'
```

### M07-S2-revert / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M07-S2-revert-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M08-S3-revert-forwarding / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M08-S3-revert-forwarding-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M08-S3-revert-forwarding.py --selftest
exit=1
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	FAIL	ambient-git-dir	exit=2 resolved=None err=cannot resolve revision '35b985146c45a7d9144a866d732de4265849915a': git rev-parse --verify failed (rc=128): fatal: not a git repository: '/nonexistent/souji-r17.git'
SELFTEST	pass=27	fail=1
stderr:
```

### M08-S3-revert-forwarding / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M08-S3-revert-forwarding-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M08-S3-revert-forwarding.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M09-S3-unfiltered-snapshot / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M09-S3-unfiltered-snapshot-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M09-S3-unfiltered-snapshot.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M09-S3-unfiltered-snapshot / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M09-S3-unfiltered-snapshot-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M09-S3-unfiltered-snapshot.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M10-measured-counter-zero / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M10-measured-counter-zero-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M10-measured-counter-zero.py --selftest
exit=1
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	FAIL	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	FAIL	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=26	fail=2
stderr:
```

### M10-measured-counter-zero / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M10-measured-counter-zero-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M10-measured-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M11-pins-counter-zero / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M11-pins-counter-zero-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M11-pins-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M11-pins-counter-zero / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M11-pins-counter-zero-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M11-pins-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M12-markers-counter-zero / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M12-markers-counter-zero-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M12-markers-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M12-markers-counter-zero / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M12-markers-counter-zero-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M12-markers-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M13-reports-counter-zero / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M13-reports-counter-zero-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M13-reports-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M13-reports-counter-zero / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M13-reports-counter-zero-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M13-reports-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M14-registry-counter-zero / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M14-registry-counter-zero-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M14-registry-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M14-registry-counter-zero / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M14-registry-counter-zero-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M14-registry-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M15-status-counter-zero / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M15-status-counter-zero-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M15-status-counter-zero.py --selftest
exit=1
stdout:
CASE	FAIL	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	FAIL	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	FAIL	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	FAIL	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	FAIL	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=23	fail=5
stderr:
```

### M15-status-counter-zero / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M15-status-counter-zero-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M15-status-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M16-heading-counter-zero / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M16-heading-counter-zero-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M16-heading-counter-zero.py --selftest
exit=1
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	FAIL	carried-open	exit=0 ids=[] err=None
CASE	FAIL	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=26	fail=2
stderr:
```

### M16-heading-counter-zero / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M16-heading-counter-zero-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M16-heading-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M17-wire-measured-zero / mutated / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M17-wire-measured-zero-mutated-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M17-wire-measured-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M17-wire-measured-zero / mutated / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M17-wire-measured-zero-mutated-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M17-wire-measured-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M01-extra-seat-id / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M01-extra-seat-id-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M01-extra-seat-id.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M01-extra-seat-id / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M01-extra-seat-id-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M01-extra-seat-id.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M02-duplicate-seat / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M02-duplicate-seat-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M02-duplicate-seat.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M02-duplicate-seat / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M02-duplicate-seat-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M02-duplicate-seat.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M03-duplicate-parse / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M03-duplicate-parse-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M03-duplicate-parse.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M03-duplicate-parse / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M03-duplicate-parse-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M03-duplicate-parse.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M04-fence-inclusion / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M04-fence-inclusion-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M04-fence-inclusion.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M04-fence-inclusion / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M04-fence-inclusion-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M04-fence-inclusion.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M05-always-measured-mismatch / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M05-always-measured-mismatch-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M05-always-measured-mismatch.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M05-always-measured-mismatch / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M05-always-measured-mismatch-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M05-always-measured-mismatch.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M06-S1-revert / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M06-S1-revert-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M06-S1-revert.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M06-S1-revert / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M06-S1-revert-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M06-S1-revert.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M07-S2-revert / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M07-S2-revert-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M07-S2-revert / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M07-S2-revert-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M07-S2-revert.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M08-S3-revert-forwarding / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M08-S3-revert-forwarding-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M08-S3-revert-forwarding.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M08-S3-revert-forwarding / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M08-S3-revert-forwarding-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M08-S3-revert-forwarding.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M09-S3-unfiltered-snapshot / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M09-S3-unfiltered-snapshot-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M09-S3-unfiltered-snapshot.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M09-S3-unfiltered-snapshot / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M09-S3-unfiltered-snapshot-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M09-S3-unfiltered-snapshot.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M10-measured-counter-zero / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M10-measured-counter-zero-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M10-measured-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M10-measured-counter-zero / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M10-measured-counter-zero-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M10-measured-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M11-pins-counter-zero / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M11-pins-counter-zero-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M11-pins-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M11-pins-counter-zero / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M11-pins-counter-zero-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M11-pins-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M12-markers-counter-zero / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M12-markers-counter-zero-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M12-markers-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M12-markers-counter-zero / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M12-markers-counter-zero-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M12-markers-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M13-reports-counter-zero / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M13-reports-counter-zero-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M13-reports-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M13-reports-counter-zero / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M13-reports-counter-zero-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M13-reports-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M14-registry-counter-zero / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M14-registry-counter-zero-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M14-registry-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M14-registry-counter-zero / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M14-registry-counter-zero-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M14-registry-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M15-status-counter-zero / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M15-status-counter-zero-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M15-status-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M15-status-counter-zero / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M15-status-counter-zero-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M15-status-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M16-heading-counter-zero / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M16-heading-counter-zero-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M16-heading-counter-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M16-heading-counter-zero / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M16-heading-counter-zero-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M16-heading-counter-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

### M17-wire-measured-zero / restored / selftest

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M17-wire-measured-zero-restored-selftest /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /var/tmp/souji-r17-MutateGateExact/M17-wire-measured-zero.py --selftest
exit=0
stdout:
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	clean-measured	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-PARSE-CHANGED'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0 ids=[] err=None
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	frozen-measured-absent	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	measured-tree-path-exit2	exit=2 ids=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE	pass	files-null-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE	pass	files-empty-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE	pass	files-nonobject-exit2	exit=2 ids=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	bold-uncarried	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-fence	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	status-in-table	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	benign-status-words	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2 ids=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1): 
CASE	pass	no-skill-exit2	exit=2 ids=[] err=no SKILL.md at 27f249e2e45e504574523b946f56bbba560c7fbf
CASE	pass	ambient-git-dir	exit=0 resolved=35b985146c45
SELFTEST	pass=28	fail=0
stderr:
```

### M17-wire-measured-zero / restored / fixture

```text
/usr/bin/bwrap --die-with-parent --unshare-net --ro-bind / / --proc /proc --dev /dev --bind /var/tmp/souji-r17-MutateGateExact/runs/M17-wire-measured-zero-restored-fixture /var/tmp --ro-bind /var/tmp/souji-r17-MutateGateExact /var/tmp/souji-r17-MutateGateExact --chdir /var/tmp -- python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r17-MutateGateExact/M17-wire-measured-zero.py
exit=0
stdout:
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
stderr:
```

## Scratch removal

```text
rm -r -- /var/tmp/souji-r17-MutateGateExact
exit=0
stdout=''
stderr=''
```

Scratch removal completed only after all exact-byte restoration and detector evidence above had been captured. No scratch artifacts are retained.
