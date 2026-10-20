# RoundRunner — round 15 w1

Seat: `SoujiR15.RoundRunner` (executor, leaf). Axes: operability, calibration.
Owned files only: `census/round-15/run-verification.py` (new, 782 lines), `census/round-15/count-claims.py` (new, 42 lines). No commits, no execution, no tests — L1 owns acceptance after all waves land.

## Files changed

| Path | Action |
|---|---|
| `census/round-15/run-verification.py` | Created. Three-arm bounded verification runner. |
| `census/round-15/count-claims.py` | Created. Committed-bytes claim counter (`git ls-tree`/`git show` on a revision arg, default HEAD). Never traverses workspaces or operator sweeps. |

## Behavior

### run-verification.py

- Extracts **two** pinned tool snapshots into exclusively-created `/var/tmp` files (`tempfile.mkstemp`, O_EXCL): pre-harm `a31642d14006830ec62edf40b0354c3699728c4a` and harm baseline `cc2168325768d5356a82c039dcdf787377c55784` (literal constants, never `HEAD`-derived). Both verified with `git cat-file -e <rev>^{commit}` first.
- 11 checks + 1 C2 record check, all under `timeout --kill-after=10 <T>`:
  - `config-fixture-preharm|harm-baseline|installed` — `tests/fixtures/r15-census-config.py --tool <arm> --json` (240s).
  - `namespace-boundary-installed` — unchanged `tests/fixtures/r14-census-boundary.py --tool <installed>` (300s): fresh 12/12 retention proof with exact `R14C2-01..12` universe pinning. Per L1 correction, the pre-harm and harm namespace arms were **removed** — their r14 outcomes are established closure ground truth (`census/round-14/verification.json`, digests tracked unchanged) and are never rerun; prior results labeled historical.
  - `census-legacy-selftest` (300s), `census-shellcheck-warning` (120s), `preservation-checker-selftest` (240s), `count-claims-baseline` (snapshot-compared vs pinned `{40 rows, A36 B3 C1, mined23 queued15 rejected2}`), `count-claims-head`.
  - `preservation-checker-fixture` — external `python3 tests/fixtures/r15-preservation-evidence.py` (240s), and `preservation-checker-frozen` — `python3 tools/souji-preservation-evidence.py --frozen tests/fixtures/r15-preservation-frozen --root <lane>` (240s): the registry two-evidence gate. Frozen dir bound by tree digest plus per-file digests and parsed `expected.json` embedded in the result.
- **Could-not-evaluate, never red**: rc 124/137/126/127, spawn failure, or Traceback ⇒ `could_not_evaluate: true` and no evaluator can return true. Baseline red requires `CASE…FAIL` rows + consistent `SUMMARY` + exact failed-set equality with the pinned `EXPECTED_HARM_CASES` ten `{01,04,06,08,09,10,12,13,15,16}` + per-case refusal reason details (`observed_exit`/`observed_finding`). Pre-harm arm matches only the exact pinned matrix `EXPECTED_PREHARM_FAILS = {02,03,07,08,11,14,17,18,19,20}` (exit 1 + consistent summary + full 20-id universe + zero `BENIGN_RESTORATION_IDS` failures); any actual benign failure → `benign-failure-no-restoration` (unmatched); anything else → `observed-unclassified`. Green and namespace arms require exact `R15CFG-01..20` / `R14C2-01..12` universes.
- **Stream capture bounded**: 256 KiB in-memory cap per stream; `bytes_total`, `sha256` (full stream), `truncated` recorded. Raw stdout/stderr/argv are also embedded in the C2 record arms so the checker can independently reparse CASE/SUMMARY rows (producer-parsed fields are a cross-check, not the authority).
- **Bytes binding**: every dependency stamped `worktree_sha256` + `committed_sha256` (`git show <captured HEAD>:<path>`) + `matches_head`, before and after the suite; `HEAD` re-read at end; `census/round-14/verification.json` digest tracked. Untracked/at-write-time-missing sibling files report `exists:false`/`committed_sha256:null` — stated, never fabricated.
- **Exclusive output**: `--output` restricted to `census/round-15/*.json`; `os.open(O_CREAT|O_EXCL)` claimed up front; refusal on any existing name. Default `verification.json`.
- Every result row stamps `measured_commit` (captured HEAD) + `tool_commit` + `tool_sha256` (labeled per arm via `label_digests`).

### C2 record (declared consistency only)

Synthesized verbatim from captured runs into `<scratch>/r15-paired-evidence.json` **in AdmissionChecker's schema** (`souji-preservation-record-v1`, confirmed by peer message): `measured_commit`, `fixture`/`namespace_fixture` {path, sha256}, `runs.{baseline_preharm,baseline,changed}` each {tool:{commit,sha256}, argv, exit_code, timed_out, raw stdout/stderr + byte counts/digests/truncation flags, cases[{id,status lowercase}], summary{total,failed}}, `namespace_controls` = the installed namespace NRUN (same shape minus tool). Statuses lowercased per checker grammar; summaries recomputed from parsed rows; raw streams let the checker reparse independently. Fed to `souji-preservation-evidence.py --record FILE --root DIR`, expected 0; the record itself is embedded in the result for audit. The checker proves declared consistency only — the L1 measured run captures observed execution, not authenticated historical provenance.

### count-claims.py

Optional revision arg → `rev-parse`, `ls-tree -r`, `git show` only. Emits measured_commit, presence flags for r15 surfaces (config fixture, checker, preservation fixture, namespace fixture, runner, count-claims), source_rows/tiers/statuses, admitted/held knowledge.

## Coordination (completed)

- **AdmissionChecker**: authoritative record schema + CLI received and adopted verbatim (message in this wave). Baseline tool pins match: preharm `6a000c59…`, harm `fcff8b05…` — also pinned in my `EXPECTED_TOOL_DIGESTS` with `*_matches_pin` fields. Namespace fixture pin `e6a984b1…` recorded via `namespace_fixture_matches_pin`.
- **Pinned sets revised (ConfigFixture ruling)**: `EXPECTED_HARM_CASES` now ten ids `{01,04,06,08,09,10,12,13,15,16}` — R15CFG-09 reclassified refusal→benign (`extensions.partialClone` false/empty) and joined the harm set; it also joins `BENIGN_RESTORATION_IDS` (formula: harm set minus R15CFG-08 safety class). Runner constants updated to match.
- **Pre-harm matrix revised (fixture author)**: `EXPECTED_PREHARM_FAILS = {02,03,07,08,11,14,17,18,19,20}` — ten ids: a31642d also fails R15CFG-18 (doesn't clear inherited `GIT_*` env) and R15CFG-20 (no strict malformed-compare contract); R15CFG-05 stays PASS. Checker re-pinned verbatim.
- **ConfigFixture**: interface confirmed (`--tool/--case/--list/--json`, `CASE\tID\tPASS|FAIL`, `TOOL`/`TOOL-KIND`, `SUMMARY`). IDs stable: `EXPECTED_IDS = R15CFG-01..20`; `HARM_CASES` revised to ten `{01,04,06,08,09,10,12,13,15,16}` — pinned in my `EXPECTED_CONFIG_CASES`/`EXPECTED_HARM_CASES`; the harm arm requires exact failed-set equality plus per-case refusal reasons. JSON enrichment line parsed by my `parse_cases`.
- **CheckerSchema / CheckerCases**: universe discussion noted; `R15C1-*` names were checker-side proposals — the landed fixture emits `R15CFG-*`, which AdmissionChecker's pinned set is defined against ("pending ConfigFixture confirmation" → now R15CFG-01..20).
- Parent directives incorporated: pre-harm third arm (PASS/FAIL/PASS benign proof), 124/137/2/traceback never red, committed-bytes stamping + HEAD recheck, exclusive output, `git show`-only counting.

## No-query boundary disclosure

Early in this seat, before the reminder, `read` on directory paths `souji-shokunin/` and `souji-shokunin/census/` listed entry names including `census/operator-sweep-20261019/` (names only; the sweep dir itself was never read, globbed, or opened). `git status --porcelain` also surfaced it as `??`. No operator-sweep file was opened, copied, or staged. All subsequent reads used explicit known paths. No runtime probe/test executed — the only executions were `python3 -c "import ast; ast.parse(...)"` syntax checks on my two owned files (parse-only, no module run).

## Risks / residual

- **Sibling files absent at write time**: `tools/souji-preservation-evidence.py` and `tests/fixtures/r15-preservation-evidence.py` did not exist when the runner was written (ConfigFixture's file has since landed). If absent at L1 run time, checker checks classify `spawn-failure`/`could-not-evaluate` — honest, never green.
- **`--frozen --root` CLI combination**: checker invocation uses `--frozen DIR --root DIR`; AdmissionChecker stated `--frozen DIR` without `--root` — tolerance of the extra operand confirmed with the peer, unverified until its file lands.
- **Record binding rules confirmed**: AdmissionChecker tolerates the additive keys and binds them when present (argv must lack --case/--list tokens — mine never carry them; stdout_sha256/bytes_total must match declared text — mine do; truncated:true renders the arm unevaluable). The r14 verification.json is valid no-harm negative evidence under its checker (always exit 2).
- The r14 namespace fixture asserts the substring `path-protected` only (CheckerSchema F2 residual — reason-level refusal is unproven by R14C2 cases).
- Output claimed exclusively before the suite: a mid-run crash leaves an empty JSON that blocks that filename; L1 reruns with `--output verification-attempt-N.json`.

## Unrun checks (for L1 after waves land)
1. `python3 census/round-15/run-verification.py` → creates `census/round-15/verification.json`, expected exit 0 when all siblings landed and tool repaired.
2. `python3 census/round-15/run-verification.py` again → must refuse (FileExistsError path, exit nonzero, original JSON untouched).
3. `python3 census/round-15/count-claims.py cc2168325768d5356a82c039dcdf787377c55784` → expect `source_rows:40, A36 B3 C1, mined23 queued15 rejected2`.
4. `python3 census/round-15/count-claims.py HEAD` → r15 surface flags flip to 1 once committed.
5. Confirm `preservation-checker-record` exit 0 only when AdmissionChecker's landed CLI matches `--record FILE --root DIR`.

## Tooling

None installed or upgraded; `RULES.md` not needed (no install). Only stdlib Python, `git`, `timeout`, `shellcheck`, `bash` referenced at run time.
