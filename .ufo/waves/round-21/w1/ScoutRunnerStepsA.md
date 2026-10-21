# Acceptance steps 1–6: source-only relocatability audit

STATUS: PARTIAL — The six step programs were inspected statically at `544c8358039a07e8b45e6db72312da5c8d965275`; none was executed. The committed r20 acceptance *wrapper* itself prevents a fresh-clone replay: it fixes `LANE` to `/home/vgpnk/Projects/shokunin/souji-shokunin` and rejects a different `--root` (`census/round-20/run-acceptance.py:24, 498–511`), then requires `HEAD == --rev` (`:513–519`). Thus, through this wrapper, each of steps 1–6 has a **No** verdict for a fresh clone at a detached revision: the wrapper refuses before dispatch (`:535–543`). This is distinct from whether each program, run on its own, is relocatable; those intrinsic verdicts are below.

## Step order

`make_steps` establishes the first six as: 1 `auditor-selftest`, 2 `revision-helper-selftest`, 3 `r20-audit-contract`, 4 `r20-input-binding`, 5 `r19-seat-audit-shapes`, 6 `r19-carry-wrap` (`run-acceptance.py:279–300`). All are passed absolute paths under the wrapper's `root`; step 3 additionally receives its extracted baseline auditor (`:272–278, 280–300`).

## Per-step findings

### 1. `auditor-selftest` — `tools/souji-seat-audit.py --selftest`

- **Root:** none for this invocation. `--selftest` returns through `selftest()` before the normal `--spec/--transcripts/--lane` path (`tools/souji-seat-audit.py:725–740`). The auditor does read its own source at `Path(__file__)` for its import-time digest (`:71–73`), but does not infer a repository root.
- **Reads:** its own source; synthetic spec and transcript files that the selftest creates under `/var/tmp` and then passes to `run()` (`:442–493, 630–660`). The generated cases are `spec.json`, `spec2.json`, `grants.json`, `S.txt`, `A.txt`, and `B.txt`; no real lane/spec/transcript store is opened. The `run()` function also checks for `MANIFEST.sha256` if present, but these selftest cases do not create one (`:446–449`).
- **Writes:** only temporary directories/files under `/var/tmp`, removed by `TemporaryDirectory`; no repository writes (`:630–660, 665–720`).
- **Git / HEAD / history:** no Git command in this selftest; no `HEAD == rev` or history dependency.
- **Network / `/proc`:** no source-level network or `/proc` access.
- **Intrinsic verdict:** **Yes** for a detached/fresh clone, assuming Python and writable `/var/tmp`; this step does not depend on that clone's location or history.

### 2. `revision-helper-selftest` — `tools/souji-rev-pin.py --selftest`

- **Root:** none for this invocation. `main()` dispatches `--selftest` before using the normal `--root` argument (`tools/souji-rev-pin.py:378–397`). The selftest creates its own repository under `/var/tmp` (`:252–281`).
- **Reads:** only the synthetic repository's `tool.sh` and `record.json` inputs plus their Git object/tree data; it exercises file/symlink/tree checks and revision resolution (`:96–181, 277–281`). It does not read the caller's checkout as an input.
- **Writes:** a disposable `/var/tmp/souji-rev-pin-selftest-*` repository, its Git metadata, `tool.sh`, and `record.json`; it appends synthetic mutations and then removes the temp tree (`:232–249, 252–281, 288–316, 358–372`).
- **Git / HEAD / history:** local synthetic-only `git init`, `config`, `add`, `commit`, `rev-parse`, `checkout`, and `update-ref` (`:232–249, 288–316, 358–360`). The tests deliberately exercise a synthetic detached commit held only at `refs/jj`, but require no history from the caller clone. No caller `HEAD == rev` requirement.
- **Network / `/proc`:** no source-level network or `/proc` access.
- **Intrinsic verdict:** **Yes**, with Git installed and writable `/var/tmp`; the detached state of the source clone is irrelevant.

### 3. `r20-audit-contract` — `tests/fixtures/r20-audit-contract.py`

- **Root:** derived from the fixture's own location: `Path(__file__).resolve().parents[2]`; relative `--tool` paths resolve against that root (`tests/fixtures/r20-audit-contract.py:404–428`). The wrapper supplies the clone's absolute auditor path and an absolute temporary `--base-tool` (`run-acceptance.py:284`).
- **Reads:** the selected auditor module and optional baseline auditor (`:82–90, 414–428`); for each synthetic case, `run()` consumes a synthetic `spec.json`, transcript `Seat.txt` (and `Neighbor.txt` in neighbor cases), and `transcripts/MANIFEST.sha256` under `/var/tmp` (`:93–142, 386–402, 433–493`). The auditor's receipt path also reads its own source. It does not need source files outside the fixture root plus the supplied auditor paths.
- **Writes:** all generated worlds and receipt/drift variants under a fresh `/var/tmp/souji-r20-audit-contract.*` directory, including `spec.json`, transcript files, `MANIFEST.sha256`, `auditor-variant.py` / `auditor-stale-copy.py`; the directory is removed in `finally` (`:93–142, 433–438, 497–660`). No writes under the clone.
- **Git / HEAD / history:** no Git command in the fixture. The runner, not this fixture, extracts the base auditor from `BASELINE` with `git show` (`run-acceptance.py:250–269`); that wrapper-level extraction requires the baseline object in its repository.
- **Network / `/proc`:** no source-level network or `/proc` access; it calls the auditor only against synthetic inputs.
- **Intrinsic verdict:** **Yes**, provided the clone contains the fixture and selected auditor and the runner supplies its extracted base file. The fixture itself has no source-clone HEAD or history requirement.

### 4. `r20-input-binding` — `tests/fixtures/r20-input-binding.py`

- **Root:** `--root` is the source root; absent that argument it defaults to `Path(__file__).resolve().parents[2]` (`tests/fixtures/r20-input-binding.py:30, 1220–1232`). The wrapper passes `--root <root>` and `--baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (`run-acceptance.py:287–294`). No literal lane path or current-HEAD equality test is in this fixture.
- **Reads from the supplied root:** parses `MEASURED_PATHS` from `census/round-13/run-verification.py`, `census/round-14/run-verification.py`, and `DEMO_MEASURED_PATHS` from `census/round-14/cache-demonstration.py` (`:172–201, 1234–1252`). It then reads each declared closure and all leaves of its declared directories (`:218–254`). The fixed closures are the r13 and r14 lists in `run-acceptance.py:30–72`; they include the `tests/fixtures/r13-cert-frozen`, `tests/fixtures/r14-cache-frozen`, `census/round-13/replay-fragments`, and `corpus/knowledge` directories, plus the listed regular files. The r13 closure includes its prior `census/round-13/verification.json`; the r14 closure includes `census/round-14/verification-attempt-1.json`; targeted adds that r14 prior (`:37–42, 1238–1247`). `choose_existing_admitted()` additionally enumerates `corpus/knowledge/*.md` and reads candidates until it finds an admitted-form record (`:779–793`).
  - Exact r13 closure: `tools/souji-verify.sh`, `tools/souji-vault-verify.sh`, `tools/souji-quarantine.sh`, `tools/souji-census.sh`, `tools/souji-cert-evidence.py`, `tools/souji-repo-structure.sh`, `tools/souji-evidence-cache.py`, `tests/fixtures/r13-cert-evidence.py`, `tests/fixtures/r13-repo-structure.sh`, `tests/fixtures/r13-quarantine-bounds.sh`, directory `tests/fixtures/r13-cert-frozen`, `census/round-13/run-verification.py`, `tools/souji-rev-pin.py`, `tools/souji-round9-selftest.sh`, `corpus/SOURCES.md`, directory `corpus/knowledge`, `LOG.md`, `census/round-13/replay-wrong-bytes.json`, `census/round-13/replay-candidate.json`, directory `census/round-13/replay-fragments`, `census/round-10/cert-16.json`, `tools/cand-census-03.sh`, `census/round-13/verification.json`, and `census/round-13/count-claims.py` (`run-acceptance.py:30–55`).
  - Exact r14 closure: `tools/souji-evidence-cache.py`, `tools/souji-census.sh`, `tests/fixtures/r14-evidence-cache.py`, `tests/fixtures/r14-census-boundary.py`, `census/round-14/cache-demonstration.py`, `census/round-14/check-timeout-anchor.py`, `census/round-14/run-verification.py`, `census/round-13/run-verification.py`, `tools/souji-rev-pin.py`, `census/round-14/run-targeted.py`, directory `tests/fixtures/r14-cache-frozen`, `corpus/SOURCES.md`, `census/round-13/verification.json`, `census/round-14/verification-attempt-1.json`, and `census/round-14/count-claims.py` (`run-acceptance.py:56–72`). The demo closure is selected from its own measured-path declaration within this set; the targeted caller's added r14 prior is already present.
- **Git reads / history:** with `--baseline`, it resolves the supplied baseline object, enumerates matching paths in that tree, and reads those blobs (`:1137–1165`); this needs the exact `12516…` commit object locally. It also runs four historical `count-claims.py` probes with the full commit IDs `31984f…`, `6f8ee0…`, `a31642…`, and `552cae…` (`:1168–1217`; invocations at `:1199–1205`). The r13 counter calls the revision helper with `tree_check=False` (`census/round-13/count-claims.py:12–31`), and the r14 counter does likewise (`census/round-14/count-claims.py:11–35`); the helper still requires a full commit ID and reachability from a durable `refs/heads`, `refs/tags`, or `refs/remotes` ref (`tools/souji-rev-pin.py:184–228`). Therefore the root clone needs those historical commits and reachable durable refs; a shallow clone lacking them is insufficient. **It does not require root `HEAD` to equal the detached tested revision.**
- **Other Git commands:** synthetic `/var/tmp` repositories use `git init`, `add`, `commit`, `rev-parse`, `switch --detach` / `switch main`, and `update-ref` (`:263–294, 428–449`). Source-root baseline comparison uses `rev-parse`, `ls-tree`, and `show` (`:1137–1151`).
- **Writes:** it copies the declared input closures into temporary Git sandboxes, mutates only those synthetic copies, creates baseline/changed overlay sandboxes and a decoy repo, and writes runner outputs under those temporary repos' `census/round-20/`; all are under `/var/tmp` and cleaned up (`:297–416, 428–449, 861–891, 1054–1119, 1258–1284`). It does not write the supplied root.
- **Network / `/proc`:** the fixture itself has no direct network or `/proc` I/O. It does spawn the copied r13/r14/targeted/cache entrypoints and historical counters on synthetic repositories (`:828–858, 951–966, 1199–1217`); these are program executions not performed in this audit, so their transitive effects are outside this fixture-only source finding.
- **Intrinsic verdict:** **Yes, conditionally**: a detached clone works if its current tree has the required inputs and it retains the named baseline/historical commit objects and durable refs. It does not require `HEAD == --rev`. The acceptance wrapper still independently prevents replay from a non-lane root.

### 5. `r19-seat-audit-shapes` — `tests/fixtures/r19-seat-audit-shapes.py`

- **Root:** derives `lane_root` from `__file__` (`fixture_dir` → two parent directories); relative `--tool` is resolved there (`tests/fixtures/r19-seat-audit-shapes.py:40–53`). The wrapper supplies an absolute auditor path (`run-acceptance.py:295–297`).
- **Reads:** the selected auditor file; the base auditor blob from `git show <base-rev>:tools/souji-seat-audit.py` (default base `3ab2c81479f5004c8bc91946eea482caec45408f`); and generated synthetic `spec.json`, `transcripts/Seat.txt`, and `audit-{changed,base}.json` files under `/var/tmp` (`:42–69, 94–132`). The imported auditor reads its own source and those synthetic specs/transcripts (`tools/souji-seat-audit.py:71–73, 442–493`); it checks whether `transcripts/MANIFEST.sha256` exists but the fixture does not create that manifest (`:446–449`; fixture writes at `:94–113`).
- **Writes:** extracted `base-auditor.py`, per-case synthetic transcripts/specs, and per-arm audit JSON, all within its temporary `/var/tmp/souji-r19-audit-shapes.*` tree; that tree is deleted (`:55–69, 94–127, 156–157`). No clone writes.
- **Git / HEAD / history:** the only source-clone Git access is `git -C <lane_root> show <base-rev>:tools/souji-seat-audit.py` (`:58–67`); the base commit object must exist locally, but the source clone need not have `HEAD == rev` or the entire history. No other Git command in the fixture.
- **Network / `/proc`:** no source-level network or `/proc` access; it runs the auditor against synthetic paths only (`:94–147`).
- **Intrinsic verdict:** **Yes**, if the base commit object is available. A detached clone is fine; a shallow clone missing `3ab2c814…` is not.

### 6. `r19-carry-wrap` — `tests/fixtures/r19-carry-wrap.py`

- **Root:** derives repository root by taking three parent directories from `__file__`; relative `--tool` resolves there (`tests/fixtures/r19-carry-wrap.py:171–184`). The wrapper supplies the absolute landing-gate path (`run-acceptance.py:298–300`).
- **Reads:** selected gate file; `git show <base-rev>:tools/souji-landing-gate.py` (default `3ab2c81479f5004c8bc91946eea482caec45408f`); and generated `changed.json` / `base.json` results for four synthetic worlds (`:171–202, 204–227`). Each world contains only generated `SKILL.md`, `tools/good.sh`, `tools/good.py`, `census/round-1/run.py`, `tests/fixtures/fx.py`, `.ufo/waves/round-18/w1/SeatWrap.md`, and `corpus/lessons/round-18.md` (`:117–144`).
- **Writes:** `base-gate.py`, those synthetic world files, temporary Git metadata, and output JSON files, all under `/var/tmp/souji-r19-carry-wrap.*`; the full temporary tree is deleted (`:186–202, 204–239`). No clone writes.
- **Git / HEAD / history:** source-clone access is only `git -C <root_dir> show <base-rev>:tools/souji-landing-gate.py` (`:191–200`), so the base object must be available. The fixture creates each synthetic repo with `git init`, `add`, `commit`, and `rev-parse HEAD`, then passes that synthetic commit to the gate (`:104–144, 147–168`). No source-clone `HEAD == rev` or full-history requirement.
- **Network / `/proc`:** no source-level network or `/proc` access; the docstring also states no network, signals, or live census (`:24–26`). The gate receives only the generated synthetic Git worlds.
- **Intrinsic verdict:** **Yes**, if the base gate commit object is available. Detached source HEAD is immaterial; a shallow clone missing `3ab2c814…` is not.

## Verdict summary

| Step | Program alone at a fresh detached clone | Through the committed r20 runner |
|---|---|---|
| 1 `auditor-selftest` | Yes; no source-root/history dependency | **No** — runner rejects non-literal lane root / nonmatching HEAD |
| 2 `revision-helper-selftest` | Yes; private temporary Git repo only | **No** — same runner preflight |
| 3 `r20-audit-contract` | Yes; root derived from `__file__`, no Git in fixture | **No** — same runner preflight |
| 4 `r20-input-binding` | Yes, only with required baseline/historical commits and durable refs; no HEAD equality | **No** — same runner preflight |
| 5 `r19-seat-audit-shapes` | Yes, if base commit `3ab2c814…` is present | **No** — same runner preflight |
| 6 `r19-carry-wrap` | Yes, if base commit `3ab2c814…` is present | **No** — same runner preflight |

No programs, tests, builds, or linters were run for this source-only audit; all pass/fail values above are static relocatability judgments, not observed acceptance results.