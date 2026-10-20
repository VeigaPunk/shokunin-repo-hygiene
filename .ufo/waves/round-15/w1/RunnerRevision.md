# RunnerRevision — round 15 w1 (reviewer)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Axes: operability, calibration.
Scope: runner measured commit/digest, temporary baseline naming, output exclusive create, no old-JSON mutation.
Mode: SOURCE INSPECTION ONLY. No tests, probes, builds, linters, or git subcommands were run. No file outside this report was edited. No tool was installed or upgraded.

## Status of the target

No round-15 runner exists in the tree. `census/round-15/` contains only `claims.json`. The reviewed sources are therefore:

- `census/round-13/run-verification.py` (452 lines, working-tree version with the gate-based retention branch). This is the only runner with exclusive output, per-row dependencies, and retention.
- `census/round-14/run-verification.py` (95 lines) and `census/round-14/run-targeted.py` (57 lines). These are the round-14 runners, which have no retention.
- `tools/souji-evidence-cache.py`, the gate the retention branch calls.

Findings below are against these sources. Section 4 gives the acceptance the round-15 runner must meet. Those items are design-only until the executor lands that runner.

## 1. Findings by severity

### H1 — High · calibration · measured commit is a HEAD label, not a bytes binding

- `census/round-13/run-verification.py:384-385` sets `CURRENT_REV = git rev-parse HEAD` once. Each row is stamped with it at `:238`.
- Dependency digests are read from the working tree at `:214`, `:231`, and `:235`. A dirty dependency therefore gets labelled with a commit that does not contain its bytes.
- `census/round-14/run-verification.py:54`, `:85` do the same: HEAD at start, no re-check after.
- `census/round-14/verification-plan.json:87` requires a clean target pathspec and a HEAD check before and after. `:117` and `:126-127` make a dirty pathspec "could-not-evaluate". Neither runner implements this.
- Retention then reuses such a row (`:201-212`). The gate only checks that `measured_commit` is 40 lowercase hex (`tools/souji-evidence-cache.py:875-880`). Its docstring (`:208-210`) says it cannot detect a mislabelled commit. So a green row can be retained with a revision that never measured its bytes.
- Same root for `run-targeted.py:23` (uses `module.git` HEAD, `:51` policy text says "unchanged green observations remain", but the targeted run's own rows are labelled with a HEAD that may differ from the attempt-1 HEAD).

Acceptance: before the suite, `git status --porcelain --untracked-files=all -- <every dependency and command path>` must be empty, and `git rev-parse HEAD` must be captured. Each dependency's digest must equal `git show <HEAD>:<path>` at measure time. HEAD must be re-read after. Any failure yields could-not-evaluate and no `measured_commit` row. Also verify the commit with `git cat-file -e <rev>^{commit}`.

### H2 — High · calibration · matching is exit-code-only; expected-red can pass on a traceback

- `census/round-14/run-verification.py:44-45`: `matched = code == expected`.
- `:71`: `census-boundary-red-before` expects exit 1. An uncaught Python exception also exits 1, so a traceback in the baseline arm counts as "expected red".
- `census/round-13/run-verification.py:404`: `quarantine-red-before`, `expected=1`, has the same hole.
- `census/round-14/verification-plan.json:79-83` defines a taxonomy: `expected_red` requires named baseline cases failing for the stated reason; fixture exit 2 is could-not-evaluate, not red; traceback is fail. The runner implements none of this.
- Round-13 already has the right pattern at `:416-417`: a required stdout finding token gates the match. It is applied only to the historical replay rows.
- Exit 2, 124, 126, 127 from a fixture are recorded as `matched=False` and the run exits 1. They are not recorded as could-not-evaluate.

Acceptance: outcome class per row (`pass` / `expected_red` / `fail` / `could_not_evaluate`). Expected-red rows require named case tokens in stdout or stderr and no `Traceback`. Exit 2, 124, 126, 127 map to could-not-evaluate.

### H3 — High · calibration · artifact digests do not cover every command input; baseline is digested after the run

- `census/round-14/run-verification.py:55-57` hash only six paths. Not covered:
  - `census/round-14/check-timeout-anchor.py` (used at `:75-76`).
  - `tests/fixtures/r14-cache-frozen/` (used at `:68`; contains `record.json`, `expected.json`, `dependency.txt`).
- So `artifacts_unchanged_during_run` (`:86`, `:92`) overstates coverage.
- `:81` digests the baseline once, after all commands. A baseline mutated during the run is recorded with its final bytes, not the bytes tested. The baseline is created `chmod 0o700` (`:64`), so its owner can write it.
- `run-targeted.py:28`, `:43` repeat the same `paths` omission.

Acceptance: derive the subject set from the command list (as `dependency_map` does in round-13), not a hand-written list. Digest each subject before and after each row. Digest the baseline before and after each baseline-using row.

### M4 — Medium · operability/calibration · round-13 retention dependency model fails open

`census/round-13/run-verification.py`, `dependency_map` (`:87-126`) and `attempt_reuse` (`:175-197`):

1. Symlink arguments are dropped silently (`:107-108`). An unresolvable argument is dropped (`:111-112`). A missing-now-created file is never bound. None of these make the row non-reusable.
2. An argument resolving outside ROOT is dropped (`:113-114`). Such a row is protected only if its name is in the hard-coded `REUSE_EXEMPT` set (`:51`, `:177-178`). A new external-input check not added to that set becomes reusable with unbound inputs. The safe rule is to refuse reuse when any argument is external, symlinked, absent, or unresolved, computed from the command itself.
3. Only argv is walked. Transitive or env-supplied inputs are not bound. The round-13 retention intent (`.ufo/waves/round-14/w1/RetentionIntent.md:33`, which cites `r13-quarantine-bounds.sh:13-29`) names `tools/souji-verify.sh` as a dependency reached via `SOUJI_VERIFY_BIN`, but the runner never sets that variable (`ENV`, `:52-55`) and walks only argv. The round-9 helper is added only for `.sh-selftest` (`:96-99`). `.ufo/waves/round-14/w1/RetentionAttack.md` CE-4 gives `souji-verify.sh:1270`, `souji-vault-verify.sh:1576`, `souji-quarantine.sh:1610` as further examples. The gate states it has no transitivity (`tools/souji-evidence-cache.py:217-220`).
4. The runner docstring (`:16-22`) implies a complete binding. It is not complete.

Acceptance: per-check declared dependency list including transitive repo files. Unknown or external inputs make the row non-reusable (`external-input` reason). Keep `REUSE_EXEMPT` only as a second line, not the primary defence.

### M5 — Medium · operability · output is not exclusively created in the round-14 runners

- Good: `census/round-13/run-verification.py:446` uses `output.open("x")`. `validate_output` (`:279-318`) refuses existing files, symlinks, historical paths, protected paths, and closed rounds. Prior evidence is read-only: `:386`, `validate_previous` `:321-339`. The historical JSON is never written.
- `census/round-14/run-verification.py:51-53` checks `target.exists()` then `:91` `target.write_text(...)`. This is check-then-write, not exclusive create. The output path is fixed (no `--output`).
- `census/round-14/run-targeted.py:21-22` and `:53`: same pattern.
- The round-15 spec requires "exclusively-created verification JSON" (`.ufo/waves/round-15/w1-spec.json` line 37, AdmissionChecker item).

Acceptance: `open(path, "x")` or `O_CREAT|O_EXCL` on the output, with the round-13 `validate_output` guards. Do not copy the round-14 check-then-write.

### M6 — Medium · operability · any exception discards all rows

- `census/round-13/run-verification.py:126` and `:231` call `digest()` with no handling. A dependency that vanishes or is unreadable raises out of `execute`, is caught at `:376-379`, and returns exit 2 with no output written. All already-measured rows are lost.
- `:448`/`:446-447` write only after every check completes.

Acceptance: a per-row exception records that row as could-not-evaluate with the exception text and the run continues to write output. (Cross-ref RunnerLimits seat for timeouts and stderr.)

### M7 — Medium · calibration · multi-hop retention loses its provenance chain

- `census/round-13/run-verification.py:206-208`: `retained = dict(prior)` then `retained["retained_from"] = PREVIOUS_SOURCE` and `retained["reuse"] = reuse`. A row already retained once (carrying an earlier `retained_from`) is retained again and the earlier hop is overwritten.
- Only `measured_commit` survives as the measurement identity. The first attempt that produced the bytes is not recorded.

Acceptance: refuse to retain a row that already carries `retained_from` unless the chain is kept as a list. Or record `retained_chain`.

### L8 — Low · calibration · baseline naming is fine; baseline bytes are not bound per row

- Naming: `TemporaryDirectory(prefix="souji-r13-before.", dir="/var/tmp")` (`:400-404`), `souji-r14-verification-*` (`census/round-14/run-verification.py:61`), `souji-r14-targeted-*` (`run-targeted.py:30`). `mkdtemp` makes each name unique and owner-only. No collision found.
- Missing: the round-13 record has no baseline digest. The round-14 record has one digest taken after the run (see H3). The BASE blob identity (`git rev-parse BASE:path`) is not recorded.
- Gate-related: `retention_gate.sha256` (`:439`) is taken at record time, not once before the first gate decision. `artifacts` (`:390-393`) does include the gate, so a mid-run gate edit is still detected by `artifacts_unchanged_during_run`. Low.

Acceptance: per baseline-using row, record `baseline_sha256` before and after and the BASE blob id.

### L9 — Low · calibration · gate's measured_commit check is format-only

`tools/souji-evidence-cache.py:875-880` checks 40 lowercase hex. It does not check existence, ancestry, or that the commit contains the dependency bytes. This is documented (`:208-210`) but not enforced. The runner side (H1) must do it.

## 2. Confirmed no-harm (round-13 working tree)

- Old JSON is never mutated: `PREVIOUS` read at `:386`; `HISTORICAL_VERIFICATION` only read or refused (`:40`, `:316`).
- Retention refuses legacy, empty, unstable, non-matched, missing-revision and external-mutable rows (`:177-190`). Gate exit 1 or 2 never yields a retained source (`:193-196`).
- No top-level revision is inherited (`:184`).
- Output exclusive create at `:446`.

## 3. Unrun checks (for L1, not executed by this seat)

- Negative control for M4.2: a synthetic row with an absolute `/var/tmp` argument not in `REUSE_EXEMPT` must be refused reuse (currently it is reused).
- Negative control for H2: a red-before arm whose stderr contains `Traceback` must not match.
- Negative control for H1: a dirty dependency must yield no `measured_commit` row.
- Negative control for H3: mutate `census/round-14/check-timeout-anchor.py` during a run; `artifacts_unchanged_during_run` must report false.

## 4. Acceptance for the round-15 runner (design-only; no round-15 runner in tree)

A1. Preflight: dependency pathspec clean; HEAD captured before and re-read after; dependency bytes equal `git show <HEAD>:<path>`. Failure → could-not-evaluate, no row labelled.
A2. Per row: `measured_commit`, dependency digests before and after, `dependencies_stable`. No top-level revision inheritance.
A3. Outcome classes per H2. Expected-red needs named tokens and no `Traceback`.
A4. Output via `open("x")`; `validate_output`-style guards; no write to any `census/round-13|14` JSON; previous read-only.
A5. Subject set derived from the commands, digests before and after per row (H3). Baseline digest before and after, BASE blob id recorded.
A6. Retention: none in round-15 unless the full gate integration is in place (same-execution digests, closing re-gate, `retained_from` plus gate sha, no multi-hop). Otherwise a fresh full run with `retained_from` absent on every row.
A7. Per-row exception handling (M6).

## 5. Messages

Findings H1–H3 and A1–A6 are sent to SoujiR15 as a short message after this file is written.

## 6. Boundary disclosure (SoujiR15 no-query reminder)

Two calls this seat made touched the operator-sweep tree, before the reminder arrived. Neither was repeated. Nothing under `census/operator-sweep-20261019/` was opened, copied, edited, or moved.

- Glob of the whole lane root (`/home/vgpnk/Projects/shokunin/souji-shokunin`, default child listing). This returned directory and file names, including the names of `census/operator-sweep-20261019/` entries and `results/` children. Names only; no file content was read.
- Recursive case-insensitive grep for `(?i)runner` over the whole lane root with `gitignore: false`. The search walked `census/`, including `census/operator-sweep-20261019/`. The displayed hits came from `.ufo/waves/round-13|14` and `corpus/`, `tests/`, `tools/`, and `census/round-13|14` paths; no operator-sweep path was among the visible lines. The output was capped at 200 results, so I cannot confirm that no operator-sweep file matched or was read internally.

Limitation: the grep may have read operator-sweep file contents while searching; this seat cannot verify otherwise. All findings in sections 1-5 rely only on explicitly named source files and round-13/14/15 evidence paths.
