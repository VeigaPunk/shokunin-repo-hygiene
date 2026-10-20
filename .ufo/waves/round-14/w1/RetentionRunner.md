# RetentionRunner — C1 consumer demonstration + historical caller migration

Seat: `SoujiR14.RetentionRunner` (executor, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Axes: calibration (primary), operability. Wave: `souji-r14-w1`.

## Shipped files (only these)

| path | state | sha256 at write time |
|---|---|---|
| `census/round-14/cache-demonstration.py` | new, executable | `fc6f69a00a0bb4702e650936691aa0e347bb1fa9a809e3552d8f9371fba29d8a` |
| `census/round-13/run-verification.py` | migrated (retention + explicit-output CLI) | `624ebaef8715babb86e7cec8e24a180c628712bdf0e6873d3fe53df3232a8d04` |
| `.ufo/waves/round-14/w1/RetentionRunner.md` | this report | — |

No commit, no push, no production data change, no historical JSON rewrite, no tool install/upgrade.

## Code inspection vs exercised evidence (no mixing)

Exercised by this seat, read-only:

- `git show a31642d:census/round-13/run-verification.py` → sha256 `4a304b1d4b9e2daeb455d77dcadad9601b568f04ae0ff3447965f83cabf0e81e`, byte-identical to the pre-migration working file; that object is what the demonstration compiles.
- `census/round-13/verification.json` read: exactly 4 results carry `retained_from` (`evidence-frozen`, `structure-selftest`, `historical-replay-wrong-bytes`, `historical-replay-candidate`), all `matched=true`, all per-result `measured_commit=6ed10a7c…`, none carrying `dependencies`.
- `tools/souji-evidence-cache.py` read (not executed): CLI accepts a regular JSON path for `--record`; exits 0/1/2; emits `finding <id>: …`; ids used: `dependency-digest-mismatch` (level 1) and `dependencies-legacy` (level 2); success line `souji-evidence-cache: reusable`; echoes `measured_commit: <record value>`. The gate was still being edited by CacheGate during this wave (observed digests `e33be2ad…` → `4408474f…` → `dc60c14b…` → `b4b50d00…` → `f8f541f7…`), so the demonstration records the digest it actually invokes instead of pinning a constant; it is untracked at baseline `a31642d`.
- `ast.parse` syntax-only check of both edited files (both parsed).
- Peer coordination: CacheGate confirmed `--record` as a regular JSON file path and the exact success/failure output shape.

Not exercised here (deliberately, L1 owns post-integration gates): neither edited file was run; the gate was never invoked; no fixture/test/selftest/build/lint/shellcheck ran; the historical suite was not re-executed. All claims below about runtime behaviour are code-inspection predictions with named expected values, not observed results.

## `census/round-14/cache-demonstration.py` (the supported current-round consumer)

Single JSON document on stdout. Exit 0 = all checks pass, 1 = red, 2 = blocked prerequisite.

Isolation: `tempfile.mkdtemp(dir="/var/tmp")` only; fixture `observations/{alpha,beta}.txt`, record(s), producer results and markers all live in that tree; default cleanup removes it and reports `cleaned`/residue; `--keep` is opt-in. No repo write, no credentials, no operator sweep, no `/dev/shm`. Gate path defaults to the installed `tools/souji-evidence-cache.py`; its sha256 is recorded before and after, plus whether the installed default is tracked at `a31642d`.

Producer is a real harmless subprocess (`python -c` reads only the isolated fixture and prints `r14-producer <rel>=<sha256> …`). `matched` is `exit==0` **and** exact expected-stdout equality; dependency digests are captured before and after the producer and `dependencies_stable` is persisted. Lane HEAD is labelled `harness_revision`; `measured_commit_scope` states the synthetic bytes are not in that commit. `producer_kind` states it proves the fixture observation only.

Sequence and expected values:

1. `initial-fresh` — producer execution 1; record built from the result's own `measured_commit` and digests; executions=1.
2. `unchanged` — gate `--root <fixture> --record <record.json>` → exit 0, no findings, `souji-evidence-cache: reusable`, record's `measured_commit` echoed; retained result keeps `measured_commit` and `dependencies` verbatim, `result_origin=retained-from-record`, no producer; executions=1.
3. `dependency-modified` — append one marker to `observations/beta.txt` only; record bytes, alpha bytes and gate bytes unchanged. Gate → exit 1, findings exactly `("dependency-digest-mismatch",)`, `souji-evidence-cache: stale`; policy re-executes producer (execution 2) and persists the new digest.
4. `legacy-no-dependencies` — matched record without `dependencies`: gate → exit 2, findings exactly `("dependencies-legacy",)`, `souji-evidence-cache: could-not-evaluate`; producer execution 3.
5. `historical-legacy` — the four real retained greens above are turned into in-memory legacy records (name/matched/`measured_commit` only) and each gate call must exit 2 with exactly `dependencies-legacy`; source JSON is never written.

Authentic red-before: `git show a31642d:census/round-13/run-verification.py` → `ast.parse` → the single top-level `run()` FunctionDef is compiled and executed with `PREVIOUS`, `PREVIOUS_RESULTS`, `RETRY_NAMES`, `CURRENT_REV`, `ROOT`, `ENV` supplied; `subprocess` is replaced by a raising tripwire; the command is a harmless marker producer. On the same stale matched-green record the baseline branch returns a retained dict (`retained_from` set, `measured_commit` preserved, no `exit_code`, marker absent) while the declared dependency digest no longer matches — the stale-green retention defect, reproduced from committed bytes, not emulated.

Migrated-caller exercise: the migrated `census/round-13/run-verification.py` is imported read-only with `sys.argv` reset to the module path (module import defines code only; no flags parsed, no output write) and its actual `attempt_reuse(name, prior)` is called directly. Because the record's synthetic dependencies live under the isolated fixture, the demo rebinds the module's `ROOT` to that fixture for these calls (recorded as `root_rebound_to_fixture`); `GATE` stays the absolute installed gate path, and the gate label is a module constant decoupled from `ROOT` so rebinding cannot corrupt it. Results: unchanged record → reusable/retained; stale record → refused with exit 1 and `dependency-digest-mismatch`; legacy → `prior-dependencies-legacy`; missing per-result revision → `prior-measured-commit-missing`; unstable capture → `prior-dependencies-unstable`; `sources-contract` → `external-mutable-command`.

Unsafe-policy control (hypothetical, labelled): retaining whenever `matched is true` would keep the stale green and the legacy green, 1 producer execution instead of the new policy's 3.

33 named checks (plus `isolation_cleaned` appended only on cleanup failure), including exact finding ids/status lines, per-result measured-commit preservation, record/gate byte stability, execution-log/disk agreement, isolation confinement and exact gate digest before/after.

## `census/round-13/run-verification.py` migration (code only; old JSON untouched)

- `--retry-failed` reuses a prior result only when all hold: name not externally-mutable; `matched is True`; its **own** 40-hex `measured_commit` present (never top-level/newer fallback); `dependencies_stable is True`; non-empty `dependencies`; and the gate exits 0 for a temporary `/var/tmp` record built from those stored values.
- Retained copies keep the original per-result `measured_commit` and stored `dependencies`; they add `retained_from` (actual source path) and `reuse` evidence (gate exit, sha256, findings). Digests are never recomputed into a prior record.
- New results persist `dependencies` = runner itself + literal existing lane tool/fixture/manifest paths named on the command line (recursive contents of a named fixture directory include `expected.json`); external absolute paths, `.git`-style and `census/operator-sweep-*` paths are excluded; the lane is never scanned wholesale. `dependencies_stable` = before/after capture equality. Tool selftests also bind `tools/souji-round9-selftest.sh`; each tested tool binds itself.
- Always re-executed: `sources-contract`, `shellcheck-warning`, `quarantine-red-before` (`reuse_eligible=false`, no gate call). The old hand-maintained `quarantine-red-before` retry coupling is deleted; fixture binding now drives it.
- Every main execution now requires explicit `--round N` and `--output census/round-<N>/<new>.json`; invocation without them exits 2 before any check. A round below the highest existing `census/round-N` directory is refused (`round-closed`), so current bytes cannot write a round-13-labelled file into the closed directory. The output must be new (exclusive create, `FileExistsError` → exit 2), lane-contained, in the exact round directory, with a real existing non-symlink parent, no symlink component, and no protected/operator-sweep path; the historical evidence path is refused explicitly. `round` in the output is the actual option, not 13. Any exception after validation (git failure, malformed `--previous` JSON, missing `results`, write failure) is reported as `could-not-evaluate` exit 2, never as a red check exit 1.
- `--retry-failed` reads prior evidence (default `census/round-13/verification.json`) only after the same lane/symlink/protection validation; it never writes that file. `prior_attempt` records the actual previous path read, and per-result revisions are never replaced by the top-level one.
- Top-level output gains `retention_gate {path, sha256, policy}`; `souji-evidence-cache.py` joins the pre/post artifact digest map. `GATE_LABEL` is a module constant so the gate's lane-relative label never depends on a mutable `ROOT` global. No historical JSON is read for writing; nothing here was executed.

## Exact L1 commands (post-commit)

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin
# Commit the wave first (gate included), then run and verify the gate bytes actually used:
python3 census/round-14/cache-demonstration.py > /var/tmp/r14-cache-demo.json
git show HEAD:tools/souji-evidence-cache.py | sha256sum
python3 -c 'import json; print(json.load(open("/var/tmp/r14-cache-demo.json"))["gate"]["sha256"])'
#   expect exit 0, status "ok", failed_checks [], isolation.cleaned true,
#   and the two printed digests identical (the gate changed repeatedly mid-wave).
python3 census/round-14/cache-demonstration.py --gate /var/tmp/absent-r14-gate.py
#   red-before discriminator: expect exit 2, status "blocked", reason "gate-missing".
python3 census/round-14/cache-demonstration.py --keep   # optional; JSON names the kept /var/tmp tree.
```

Do **not** run `census/round-13/run-verification.py` for this wave. Its main path now refuses without `--round N --output census/round-N/<new>.json` (exit 2 before any check) and never overwrites an existing file; if a later round deliberately re-executes it, the command is `python3 census/round-13/run-verification.py --round <N> --output census/round-<N>/verification.json [--retry-failed --previous census/round-13/verification.json]`. Historical commands remain tied to their own measured revisions. The narrow synthetic demonstration above is the intended measurement; main's r14 runner performs no retention.

## Risks, limitations, blockers

- Expected runtime values are unobserved until L1 runs; gate digest may legitimately change if CacheGate edits again before commit — the demonstration records the digest it actually used rather than a constant.
- The producer is real but synthetic; `harness_revision`/`measured_commit_scope` prevent reading lane HEAD as provenance for the /var/tmp bytes. No historical execution is proven or re-executed.
- The migrated `attempt_reuse` decision is exercised directly; `run()`'s re-execution branch and the full suite remain code-inspected only. Dependency capture is conservative, not complete (runtime tools/env excluded; external-mutable commands exempted).
- Demonstration assumes the gate's documented output lines and finding ids; any drift fails checks red rather than being masked.
- No blockers. Gate implementation was present at write time; it is untracked at baseline `a31642d`, which is recorded explicitly.
