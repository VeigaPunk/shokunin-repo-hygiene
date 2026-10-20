# FixtureCacheAudit — souji r14 w1 (C1 evidence-cache fixture and gate)

Seat: FixtureCacheAudit (reviewer, leaf). Axes: calibration, operability.
Scope: static review of `tests/fixtures/r14-evidence-cache.py`, `tools/souji-evidence-cache.py`, and `tests/fixtures/r14-cache-frozen/`. No runs.

## Evidence status

- Code inspection: performed by reading source. Line numbers below refer to the files as read at audit time.
- Exercised evidence: none. The assignment forbids runs. No tools were installed or upgraded.
- Earlier "blocked" verdict (files absent) is superseded: CacheGate reported the files ready; they were read in full.

## Summary

One defect that breaks the fixture on its first run, plus documentation/contract drift and coverage gaps. Case count, literal expectations, `/var/tmp` scratch, and `--tool` discrimination are in place.

## Findings by severity

### F1 — HIGH — `--record PATH` success path crashes (arity mismatch)

- `tools/souji-evidence-cache.py:598-641` `_read_path_text`: every failure branch returns a 3-tuple `(text, reason, detail)`, but the success branch at line 637 is `return _read_fd_text(fd, limit)`. `_read_fd_text` (line 581-595) returns a 2-tuple `(text, reason)`.
- `tools/souji-evidence-cache.py:719-728` `_record_payload` unpacks `text, reason, detail = _read_path_text(...)` (line 724).
- Result by static trace: any readable regular JSON file passed as `--record PATH` or `--record @PATH` raises `ValueError: not enough values to unpack (expected 3, got 2)` inside `main()` (line 1577). `__main__` (line 1594-1597) catches it and prints `souji-evidence-cache: could-not-evaluate` plus `finding internal-error: ValueError: ...`, exit 2.
- Affected fixture and selftest cases (all expect success or a specific id, so each fails):
  - `tests/fixtures/r14-evidence-cache.py` `external-clean` (expects rc 0, reusable), `duplicate-json-keys` (expects only `record-malformed`; receives `internal-error`).
  - `_selftest` `record-path` (line 1460-1467, expects rc 0).
  - Selftest summary therefore cannot reach `N/N passed`, and the fixture's selftest check fails.
- The documented retention-runner integration form (fixture docstring line 5-6, tool docstring line 26-27) is the broken path.
- Fix (for CacheGate): in `_read_path_text`, replace the final `return _read_fd_text(fd, limit)` with `text, reason = _read_fd_text(fd, limit)` then `return text, reason, None`. Alternatively make `_record_payload` accept a 2-tuple. Either way, the arity contract must be one shape.

### F2 — MEDIUM — documented finding ids that are never emitted or unreachable (named-id contract drift)

- `dependency-duplicate`: listed in the tool docstring (line 139) under level 2. No `_add(..., "dependency-duplicate", ...)` exists in the code. Dead documented id, no case.
- `key-alias`: listed (line 139-140) and implemented at line 839-843, but unreachable. `_classify_rel` (line 445-475) returns the value unchanged for every accepted key, and JSON object keys are deduplicated by `_reject_duplicate_keys` before evaluation. Two distinct accepted strings can never alias. The docstring claim (line 96-97) "Two keys that normalize alike are refused (`key-alias`)" describes behavior the code does not have. No selftest case exists.
- Fix: delete `dependency-duplicate` and the `key-alias` branch and its docstring claim, or implement real normalization with a case. The shared interface requires named stable ids, so the emitted set and the documented set must match.

### F3 — MEDIUM — docstring overclaims the fd-walk TOCTOU property

- Tool docstring lines 93-94: "No path is reopened by name after the walk, so a swapped ancestor cannot redirect the read."
- Contradicted by code: `_resolve_root` opens the walked root path by name (`os.open(resolved, flags)`, line 699) after `_resolve_boundary`. `_read_path_text` opens the record by name after `os.lstat` (line 622). Ancestors of `--root` can be swapped between the lexical/walk check and the open.
- Scope: dependency reads beneath the root fd are fd-walked as claimed. The gap is the root and record-path open. Security adjudication belongs to SafetyCache; this seat records it as a docstring-versus-code mismatch.
- Fix: correct the docstring to the actual guarantee, or open the root via an fd walk from `/` with the same protection checks.

### F4 — LOW-MEDIUM — selftest coverage gaps against the documented contract

The fixture covers the spec's case list (verified: 22 literal cases, see below). The tool's own `--selftest` (32 cases) does not exercise these documented behaviors:

- `verdict-false-fail`: `matched=false` with `exit_code=0` (tool line 786-787). No case.
- `expected_exit` disagreement on `matched=true` with `exit_code=0` and `expected_exit=1` (tool line 781-785). No case; only the `exit_code=1` branch is tested (`false-pass`).
- Intermediate symlink ancestor (shared interface: "symlink ancestors"). Code path: `_open_dir_beneath` maps ELOOP to `symlink` (line 482-483), giving `path-symlink`. No case; only a leaf symlink is tested.
- Unexercised emitted ids: `dependencies-invalid` (array-valued dependencies), `record-schema` (missing name, boolean exit_code), `require-invalid`, `path-not-directory`, `root-not-directory`, `frozen-schema`, `frozen-malformed`, `frozen-unreadable`, `internal-error`. Some are hard to reach black-box; the selftest claims full coverage of its id list, so at least the first five are cheap to add.
- `dependency-device-escape` cannot be produced without a second device; state that limit rather than claim coverage.

### F5 — LOW — assertions are substring needles, not line-anchored

- Fixture `check` (line 85) and selftest (line 1519) use `needle in stdout`. Examples: `"dependencies: 2"` also matches `dependencies: 20`; `"souji-evidence-cache: reusable"` matches any line containing that text; `"measured_commit: " + COMMIT` matches a longer value.
- Calibration impact is small today because each status line is single-valued, but the measured-revision echo is the calibration axis. Recommend `re.search(r"(?m)^measured_commit: %s$" % COMMIT, stdout)`.

### F6 — LOW — operability note on the 1 GiB sparse fixture

- The selftest `too-large` case (tool lines 1420-1432) truncates a sparse `(1 << 30) + 1`-byte file under `/var/tmp`. On a filesystem without sparse-file support this allocates 1 GiB. Acceptable on the lane host; the assumption is recorded here. Timeouts by reading: selftest per-case subprocess 120 s (`_run_tool`), fixture selftest invocation 180 s.

## Verified by reading (no runs)

- Fixture literal cases: 22 `check(...)` calls (selftest, external-clean, changed-dependency, unchanged-unrelated-change, missing-dependency, symlink-dependency, malformed-hash, path-escape, matched-false, legacy-no-dependencies, empty-dependencies, duplicate-json-keys, nonregular-dependency, malformed-measured-commit, nonboolean-matched, require-undeclared, protected-root, protected-record, frozen-clean, frozen-tampered, frozen-verdict-mismatch, per-result-commit). `MIN_CASES = 20`; fixture asserts `len(results) >= 20`. Matches the claim.
- Expected ids and exit codes are literals (fixture lines 168-336). Not read back from the tool. Matches the requirement.
- `--tool` missing: `fixture: tool missing: <path>` and exit 2, before any scratch is created (lines 143-145). Matches.
- Scratch: `tempfile.mkdtemp(prefix=..., dir="/var/tmp")` (line 151), synthetic `HOME` under the scratch tree (line 155-164), `finally: shutil.rmtree` (line 337-338). No `/tmp` default, no `/dev/shm`, no `TMPDIR` fallback. Q4 static checks pass: fixture has no `TMPDIR:-/tmp`; `/var/tmp` is present.
- Tool selftest scratch: `tempfile.mkdtemp(dir="/var/tmp")` (line 1170), `finally: shutil.rmtree` (line 1522-1523). Synthetic HOME (line 1174-1177).
- Frozen snapshot: `expected.json` pins `record.json` and `dependency.txt`; `verdict: reusable`; `record.json` declares `dependency.txt` with the same digest; `measured_commit` is the fixture COMMIT. Consistent with `frozen_files: 2`.
- Frozen tamper and verdict-mismatch paths are copies under `/var/tmp`; the committed snapshot is never modified. Good.
- Credential-path cases (`protected`, `record-protected`, `root-protected`, `protected-root`) map to tool logic: component/pair checks at lines 312-327, lexical-first tree check in `_resolve_boundary` at lines 422-435, and root refusal at lines 692-696. Read as correct.

## Not verified statically

- The pins in `expected.json` (`875598b6...` for `dependency.txt`, `67221a33...` for `record.json`) cannot be confirmed without hashing. Hashing is a run; L1 must confirm with the command below. If `dependency.txt` has or lacks a trailing newline relative to the pin, `frozen-clean` fails.
- Whether `ELOOP` (not `ENOTDIR`) is returned for an intermediate symlink under `O_DIRECTORY|O_NOFOLLOW` on this kernel. Reasoning says ELOOP, so `path-symlink`; unverified until a case runs.

## Requests to CacheGate (ordered)

1. Fix F1 (`_read_path_text` arity). This is blocking: without it `external-clean`, `duplicate-json-keys`, and selftest `record-path` fail.
2. Resolve F2: remove or implement `dependency-duplicate` and `key-alias`, and make the docstring match.
3. Correct the F3 docstring claim, or fix the root/record open.
4. Add selftest cases for `verdict-false-fail`, `expected_exit` disagreement, intermediate symlink ancestor, and the cheap unexercised ids in F4.
5. Anchor the F5 needles.

## Final L1 commands (for after the fixes land; this seat ran none)

Run from `/home/vgpnk/Projects/shokunin/souji-shokunin`:

```
python3 -B -c 'import ast,sys; [ast.parse(open(p,encoding="utf-8").read(),p) for p in sys.argv[1:]]; print("parse-ok")' tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py
sha256sum tests/fixtures/r14-cache-frozen/dependency.txt tests/fixtures/r14-cache-frozen/record.json   # must equal expected.json pins
python3 -B tools/souji-evidence-cache.py --selftest; echo "selftest-exit=$?"   # expect 0; 32/32 passed after F1 fix
python3 -B tests/fixtures/r14-evidence-cache.py; echo "fixture-exit=$?"       # expect 0; 22 checks passed
python3 -B tests/fixtures/r14-evidence-cache.py --tool /var/tmp/r14-no-such-tool; echo "baseline-exit=$?"   # expect 2, 'fixture: tool missing:'
grep -c 'TMPDIR:-/tmp' tests/fixtures/r14-evidence-cache.py     # expect 0 (Q4)
grep -c '/var/tmp' tests/fixtures/r14-evidence-cache.py         # expect >= 1 (Q4)
grep -c '/dev/shm' tests/fixtures/r14-evidence-cache.py tools/souji-evidence-cache.py   # expect 0 (Q16)
ls -d /var/tmp/souji-r14-cache-* 2>/dev/null | wc -l            # expect 0 after runs (cleanup)
# no shellcheck step: the gate and fixture are Python; Q9 applies to shell scripts only.
```

Tool installs or upgrades by this seat: none.

## Re-review after CacheGate fixes (static, no runs)

- F1 (tuple blocker): CLOSED. `_read_path_text` success branch now unpacks `text, reason = _read_fd_text(fd, limit)` and returns `(text, None, None)`; `_record_payload`'s three-value unpack matches every branch.
- F2 (ids): CLOSED as documented. `dependency-duplicate` is gone from the docstring and code. `key-alias` is retained and labelled an unreachable defensive check. Accepted: dead branch with no case, but the id is documented as such, not claimed as tested.
- F3 (docstring): PARTLY CLOSED. Dependency reads are fd-walked with no name reopen. Root and record are now boundary-walked (`_resolve_boundary`), then opened by a per-component `O_NOFOLLOW` walk from `/` (`_open_no_symlink`, `_open_dir_component`, `_open_leaf_checked`). Symlink components are refused, not followed. Residual: the protection decision is string-based on the walked path, and the open is not bound to that decision. A directory renamed between the walk and the open can change what is read, although symlinks cannot. Docstring line ~230 ("closes the ancestor-swap race ... for the resolved root/record open") overstates this. Suggest: "symlink redirection is refused; directory-rename swaps between the protection check and the open are not closed." Routed to SafetyCache as the owner of that judgment.
- F4 (selftest coverage): CLOSED by reading. `false-fail` (matched=false with exit_code=0 → `verdict-false-fail`; early return on level-2 schema finding means no `matched-false` co-finding, matching the expected id set); `expected-exit-mismatch` (exit_code=0, expected_exit=1 → `verdict-false-pass`); `symlink-ancestor` (`linkdir` → `src`; `_open_dir_component` maps the ENOTDIR from `O_DIRECTORY|O_NOFOLLOW` on a symlink to `symlink` via lstat, so `path-symlink`). The ENOTDIR-versus-ELOOP question from my earlier report is resolved in code: both paths yield `symlink`. Still unexercised until a run.
- F5 (fixture needles): CLOSED for the fixture. `check(... exact_lines=...)` anchors `^...$` for the status lines, `measured_commit`, `dependencies: N`, `frozen_files: N`. Status lines are single-valued so the remaining substring needles on could-not-evaluate and stale cannot false-match. The gate's own selftest still uses substring needles (`"measured_commit: " + SELFTEST_COMMIT` etc.). Minor; the anchored form is recommended there too.
- Fixture check count: 22 `check(...)` call sites re-counted by grep. Matches the claim.
- Selftest count: not confirmed. The grep output was truncated before the last cases, so the claimed 39 is not verified by this seat.

Still unverified (requires L1 run): frozen pins `875598b6...` and `67221a33...` against `sha256sum`; the full selftest count; every expected id actually emitted.

Final L1 commands: as listed above; add `python3 -B tools/souji-evidence-cache.py --selftest | tail -n 1` to confirm `selftest: N/N passed` with N = 39.

## Addendum: second static re-review (no runs)

- F3 wording: CLOSED. The gate docstring (lines ~238-243) now states symlink redirection is refused for dependency reads and the resolved root/record open, and that a directory renamed or replaced by a different real directory between boundary walk and open is not detected for root/record. Dependencies re-check nlink/dev. This matches the code.
- F5 in gate selftest: adopted per CacheGate. Fixture `check(... exact_lines=...)` unchanged and correct.
- Fixture HOME setup moved inside `try` (lines 153-167); `base` is created before the `try`, so `finally` covers the cleanup path. Correct.
- Frozen copies use `symlinks=True` (lines 322, 330): a symlink inside the snapshot copy stays a symlink rather than being dereferenced. Correct for the tamper/mismatch cases.
- Selftest count: CacheGate reports 48 (was 39 in my earlier note); not verified by this seat. Fixture external count 22 re-checked by grep earlier.
- Nit (non-blocking): the protected-trees docstring (~line 122-124) uses shell-expansion notation `${PI_CONFIG_DIR:-.omp}` in prose. Reword to plain words to avoid confusion.

Still unverified (L1 runs only): frozen pins against `sha256sum`; `python3 -B tools/souji-evidence-cache.py --selftest | tail -n 1` expecting `selftest: 48/48 passed`; fixture `python3 -B tests/fixtures/r14-evidence-cache.py` expecting 22 checks passed.
