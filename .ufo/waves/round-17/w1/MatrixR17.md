# W1 · MatrixR17 — `census/round-17/run-matrix.py` (new)

Item: generalized r16 runner for round-17 arms. OWN ONLY `census/round-17/run-matrix.py`.
Lane tip at write: `refs/heads/master` = bare `HEAD` = `5fa6017ddcae9f6bd4412df44765f6360cb16294`.
Runner sha256: `2a46ae127ea8f8a4d90ed29ff6cada7d51e9b4272961a43b3a28536c4e943e8d` (final bytes).

## Verdict

Runner implemented and executed end-to-end **against stub fixtures** — the real
`tests/fixtures/r17-census-hygiene.py` is not yet landed (fixture seat still in flight),
so the default lane `tests/fixtures` path correctly refuses (`missing fixtures`, exit 2).
The `--fixture-dir` override added for exactly this case directed all three suites to
stubs under `/var/tmp/souji-r17-MatrixR17/fixtures/`. **Re-run with real fixtures once
`r17-census-hygiene.py` lands**; the counting command is:

```
python3 census/round-17/run-matrix.py --changed <rev|WORKTREE> --output <new.json>
```

## Changes vs the r16 runner (rev `2815712b…`)

Every open finding from `.ufo/waves/round-16/w2/RevMatrixRunnerFinal.md` is closed:

| Finding | r16 defect | r17 fix |
|---|---|---|
| F1 (Medium) | `rc in (0,1)` + `failed=0` read a post-SUMMARY teardown crash as PASS | `valid` requires `rc == (1 if failed else 0)`; a teardown traceback (rc 1, failed 0) is invalid, not green. |
| F2 (Low-Med) | `fixtures_dirty` recorded but never gated | computed *before* any arm runs; non-empty → refuse exit 2 with the porcelain lines, unless `--allow-dirty-fixtures` (flag recorded as `allow_dirty_fixtures`; dirty string still recorded). |
| F3 (Low) | fixture `id-set` row made `len(cases) != total` → mislabeled "could not evaluate" | `synthetic` id-set rows subtracted from the case count and added to the failed bound: `len(cases) - synthetic == total`, `failed <= total + synthetic`. An id-set drift is a *valid red* suite carrying the `id-set` case detail — the id-set comparison row is computed and stored. |
| F4 (Low) | no schema marker; stale pre-gate record confused consumers | `record_schema: 2`; full output schema documented in the docstring. |
| nit | `run()` leaked `OSError` | `OSError` on spawn → `(127, "", "cannot run …")`; no traceback out of `main()`. |
| nit | loop var `a` shadowed argparse namespace | renamed to `arm_name`. |

Peer-routed additions this wave:

- **Per-fixture selector** (ConnGateRegistryRows): `FIXTURES` maps each suite key to
  `(filename, argv selector)` — `r17-hygiene`→`--census`, `r15-config`/`r14-namespace`→`--tool`.
- **Process-group timeout kill** (SentinelFifoHostile): `run()` uses `Popen`
  + `start_new_session=True`; on timeout it `os.killpg(SIGKILL)`s the whole group, so a
  fixture-spawned `git` blocked on a hostile fifo cannot orphan. (The memory-bomb class —
  symlink to /dev/zero on guardless arms — is a fixture-side concern; the runner keeps a
  900 s suite cap and reports rc 124 as an invalid suite, not a green row.)
- **Branch-tip pin** (CriticHonestyWhyNot): `lane_head` records
  `git rev-parse refs/heads/master`; bare `HEAD` is recorded separately as `git_head`
  (detached under jj colocation).

Record contract per assignment: `fixtures_sha256` (run-level, per suite) plus per-arm
census `sha256` and resolved `rev`; `changed_rev` derived; refuses to overwrite `--output`
(exit 2, observed); scratch under `/var/tmp/souji-r17-matrix.*` removed in `finally`
(observed: no dir remains). Exit semantics (matching the registry row kind `evidence`):
0 = record written and every suite valid (a red arm is data, never a failure code);
2 = could-not-evaluate/invalid suite, unknown rev, dirty fixtures without the flag, or
refused overwrite; 1 = runner/OS error. Arm set: pre-harm `a31642d`, r14-harm `cc21683`,
r16 `5fa6017`, changed. Suite keys: `r17-hygiene`, `r15-config`, `r14-namespace`
(r14 namespace fixture = `tests/fixtures/r14-census-boundary.py`, same as r16).

## Commands run (ALLOWED-EXEC scope)

```
python3 -m py_compile census/round-17/run-matrix.py          → clean
python3 census/round-17/run-matrix.py --changed 5fa6017 \
    --output /var/tmp/souji-r17-MatrixR17/m.json \
    --fixture-dir /var/tmp/souji-r17-MatrixR17/fixtures      → exit 0 (ran twice: v1 and final bytes)
```

Stubs: three identical differential fixtures accepting either `--census` or `--tool`,
FAILing `STUB-1` when the extracted census lacks the literal `--untracked-files` (D1
probe) and always PASSing `STUB-2`; each emits `SUMMARY total=2`. All four arms lack the
flag → each suite `2/1fail`, `valid: true`.

### Arm/totals table (stub fixtures, observed output)

| arm | census sha256 | bash -n | shellcheck | selftest | r17-hygiene | r15-config | r14-namespace |
|---|---|---|---|---|---|---|---|
| pre-harm `a31642d` | `6a000c59fe74…` | 0 | 0 findings | 36/0 | 2/1fail | 2/1fail | 2/1fail |
| r14-harm `cc21683` | `fcff8b057b3e…` | 0 | 0 findings | 38/0 | 2/1fail | 2/1fail | 2/1fail |
| r16 `5fa6017` | `64a60fd0b0ed…` | 0 | 0 findings | 38/0 | 2/1fail | 2/1fail | 2/1fail |
| changed `5fa6017` | `64a60fd0b0ed…` | 0 | 0 findings | 38/0 | 2/1fail | 2/1fail | 2/1fail |

Record provenance (final run): `invalid_suites: []`, `fixtures_dirty: null` (fixtures
outside lane — override path, recorded as `fixture_dir`), `lane_head`=`git_head`=`5fa6017…`,
`runner_sha256 2a46ae12…`, `record_schema: 2`, git 2.56.0, bash 5.3.20, shellcheck 0.11.0,
python 3.14.8.

Refusal paths observed: re-run to same `--output` → `refusing to overwrite`, exit 2;
default fixtures without `r17-census-hygiene.py` → `missing fixtures`, exit 2.
Not exercised: the dirty-fixture refusal (no writable lane fixture path for a stub);
the gate code path is identical to the missing-fixture refusal.

## Risks / blockers

- **Fixture dependency**: real-matrix numbers cannot be produced until
  `r17-census-hygiene.py` lands; re-run the counting command then. The stub run proves
  machinery, not claim evidence. The `--census` selector is per the fixture spec via
  ConnGateRegistryRows — if FixtureR17Census instead grows a `--tool` alias, update the
  FIXTURES tuple (one line).
- `fixtures_dirty` gate fires on `??` untracked too — intentional (fixture byte-identity
  is the claim's comparison basis); pass `--allow-dirty-fixtures` for exploratory runs.
- Suite `stderr_tail` is record-only (non-gating), matching r16 scope.
- Files changed: `census/round-17/run-matrix.py` only (plus this report).
- Tool installs: none (python3, shellcheck, git, bash already present).
- `/var/tmp/souji-r17-MatrixR17/` deleted after the run; regenerate the record with the
  same command if needed.

STATUS: DONE — runner written, compile-clean, executed end-to-end on stub fixtures via `--fixture-dir`; all r16 findings closed plus three peer-routed seams (selector, killpg, branch tip); pending only a real-fixture re-run once `r17-census-hygiene.py` lands.
