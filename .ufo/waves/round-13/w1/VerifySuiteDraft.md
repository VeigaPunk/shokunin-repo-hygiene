# R13 w1 — VerifySuiteDraft (executor, leaf)

Scope: own `census/round-13/final-checks.md` only; inventory installed tool selftest modes and
isolated environment controls; author bounded final checks for L1. No test, build, lint, formatter,
gate, fixture or tool selftest was executed. No tools installed or upgraded. Certification remains
OFF. This seat is not an independent non-author verifier.

## Files changed

- `census/round-13/final-checks.md` — new, 519 lines, sha256
  `925a175c3bac835675f89f31e92c1aebe1625c72dfa8a9868dc5541471302c18`.
- `.ufo/waves/round-13/w1/VerifySuiteDraft.md` — this report.

Nothing else was written or edited; no commits; operator sweep not read; no secrets.

## What the deliverable contains

Seven bounded checks (`FC-1..FC-7`) plus a preamble/postamble and an inventory of every installed
selftest. Commands are absolute, use `env -C` instead of `cd`, pin `TMPDIR=/var/tmp`, fix `HOME`,
`PATH`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, unset `GIT_DIR`-family variables,
and bound every run with `timeout`.

1. **FC-1 red-before** — extracts `31984f4:tools/souji-quarantine.sh` to
   `mktemp -d /var/tmp/...`, asserts its sha256 is `141c0fdc…`, then runs
   `tests/fixtures/r13-quarantine-bounds.sh --tool <baseline> --verify <lane engine>` expecting exit
   1 (`R13Q8-01 PASS`, `02/03 FAIL` with rc 1/2, `04/05 HANG` with `rc=124`, `SUMMARY total=5
   failed=4 hung=2`) and the same fixture against the fixed tool expecting exit 0 (`5/5 PASS`,
   `failed=0 hung=0`).
2. **FC-2 gate** — `tools/souji-cert-evidence.py --selftest` expecting exit 0 and
   `selftest: 36/36 passed` with the named reject cases; the external black-box harness
   `tests/fixtures/r13-cert-evidence.py` expecting exit 0 and `fixture: 5/5 checks passed`; then
   `--frozen` on the 7-file fixture (`clean`, `frozen_files=7`) and a tampered copy (`exit 2`,
   `snapshot_tampered`). A real-bytes four-fragment manifest run is conditional on
   `census/round-13/cert-manifest.json`; absence is NOT-RUN, never green.
3. **FC-3 size** — `tests/fixtures/r13-repo-structure.sh --selftest --probe
   tools/souji-repo-structure.sh` expecting `selftest=PASS ids=5/5` (baseline mode `4/4`).
4. **FC-4 ShellCheck** — `shellcheck -S warning` (0.11.0) on the four changed/new shell files;
   exit 0 and empty output, with a HEAD-baseline comparison if the baseline warned.
5. **FC-5 source census** — `env -C "$R" TMPDIR=/var/tmp bash census/round-12/sources-census.sh`,
   expected HEAD `33 / malformed 0 / A=29 B=3 C=1 / mined=16 queued=15 rejected=2` versus post-C3
   `33-or-34 rows / mined=18 queued=13(–14)`; the stored r12 `mined=18 queued=13` is explicitly
   rejected as the baseline. Adds a `git ls-files --error-unmatch` check for every mined used-by
   path so an untracked F2 entry cannot satisfy `[ -e ]`.
6. **FC-6 regression** — the four installed selftests plus the r12 maintenance gate, with the
   quarantine G1/H2/H3 lines and CertProtocol's static floors (verify 38, vault 49, census 36,
   quarantine 75).
7. **FC-7 live guard** — real lane path, `--hold 0`, nonexistent target, expect exit 4 and
   `live-fleet-mutation-forbidden`, with `LOG.md` sha and `.ufo-quarantine` sentinels.

## Facts observed (code read, not executed)

- Whole-tool TMPDIR override: `tools/souji-verify.sh:490`, `tools/souji-vault-verify.sh:680`,
  `tools/souji-quarantine.sh:672` all execute `export TMPDIR="${TMPDIR:-/var/tmp}"` at top level
  (appended S18 block), while their selftest mktemps still read `${TMPDIR:-/tmp}`
  (`verify:1105`, `vault:1308`, `quarantine:1360`). The exported value wins when `TMPDIR` is unset;
  an inherited `TMPDIR=/tmp` wins over the override and silently moves fixtures to `/tmp`.
- `tools/souji-census.sh` has no override; `:418` and `:516` read `${TMPDIR:-/tmp}` and the trap is
  `:517`. Bare invocation therefore defaults to `/tmp` — a Q4 gap in an installed tool.
- Live guard is location-derived: `SCRIPT_DIR` → `REPO_ROOT` (`:147-149`) → `LIVE_FLEET_ROOT`
  (`:149`). Refusal/exit 4 is `:603-614`; dry-run note `:616-621`. G1 proves it inside
  `--selftest` (`:1440-1447`, live sentinels `:1600-1612`). A baseline copy under `/var/tmp`
  computes a `/var/tmp` guard root; the bounds fixture sets `SOUJI_QUARANTINE_ALLOW_LIVE=1` for its
  disposable repos, so the red run never depends on the guard.
- Baseline Q8 absence on HEAD bytes: `grep -c timeout` → 0; no special-file preflight; duplicate
  `file_sha` at `:184`/`:722` and `dir_digest` at `:186`/`:727` (later wins); unbounded engine
  (`:215`), `git mv` (`:529`), `mv` (`:536`), pin digest (`:498`). On a FIFO the effective
  `[ -f ]` guard (`:723`) makes the baseline exit silently (rc 1 target, rc 2 descendant), not hang.
- Fixed quarantine: single digest helpers (`file_sha:712`, `dir_digest:722`, `content_digest:733`),
  bounds `timeout --kill-after=10` at 120 s file / 300 s dir / 60 s scan / 60 s staging / 120 s rm,
  special-file preflight `:1191-1222` (`special-file-refused`, `special-descendant`,
  `special-scan-timeout`, `cross-device-staging`), and the Q6 sibling-engine fallback removed
  (`VERIFY_BIN` is `:158`).
- Gate at `9a2ed8aa`: 31 `case(` + 1 inline `root-not-directory` + 4 `frozen_case(` = 36 cases;
  final line `selftest: N/N passed` (`:1478`); fixture required at `:1150`; mkdtemp
  `dir="/var/tmp"` `:1155`; external harness `tests/fixtures/r13-cert-evidence.py` reports
  `fixture: 5/5 checks passed` (`selftest`, `external-clean`, `external-digest-mismatch`,
  `frozen-clean`, `frozen-tampered`). `tests/fixtures/r13-cert-frozen` has 2 fragments and 7 pinned
  files, so the clean frozen summary is `fragments=2 … frozen_files=7`, not CertProtocol's future
  `13`.
- Size fixture at `b6bf5205` pins 4 ids baseline and 5 with `--probe` (adds
  `SOUJI-R13-STRUCT-promisor-refusal`), final `selftest=PASS ids=5/5`; hard-coded
  `mktemp -d /var/tmp/...` `:159`, trap `:162`, `env -i` allowlist, `HOME` under WORK.
- Bounds fixture at `e8e7e9a1`: `CASE<TAB>id<TAB>PASS|FAIL|HANG<TAB>detail`,
  `SUMMARY<TAB>total=N<TAB>failed=M<TAB>hung=H`, exit 0/1/2, scratch `:84`, trap `:86`, no literal
  live path (grep for `/home/vgpnk|Projects/shokunin` returns nothing). `finish_case` maps
  rc 124/137 to `HANG` and counts it in both `failed` and `hung` (`:106-122`).

## Inference (marked as such)

- The baseline's 04/05 red verdicts: `finish_case` maps the fixture's outer 20 s bound
  (`rc=124/137`) to `HANG` and counts it in both `failed` and `hung`; the red summary is therefore
  `total=5 failed=4 hung=2`. This is a code-path inference, not an observed run.
- The fixed tool's green 04/05 semantics follow from the landed tokens: staging `timeout` maps
  rc 124 to `STAGE2-FAILED mv-timeout`, digest `timeout` maps to `NOT-AUTHORIZED digest-timeout`.
  These are code-path inferences, not an observed run.
- `file_sha`/`dir_digest` shadowing means the first definitions are dead; the effective FIFO
  behavior was inferred from the `[ -f ]` guard and matches SafetyPaths' independent reading.

## Risks and blockers

- The real-bytes C1 claim is NOT-RUN until `census/round-13/cert-manifest.json` + four committed
  fragments exist. The gate's selftest alone is synthetic-artifact coverage; it does not prove the
  installed bytes were measured. Do not mark C1 installed-byte certified without FC-2b.
- Every literal in the doc is tied to the sha256 table. Files changed repeatedly during drafting
  (gate 1377→1525 lines, size fixture 3→4 baseline / 5 probe ids, bounds fixture FAIL→HANG
  vocabulary); L1 must re-derive N and ids if a hash differs. The gate's `--selftest` exits 2 if
  the frozen fixture is removed.
- The bounds fixture is new and unexecuted by this seat; FC-1's red/green values are from its code
  and BoundQuarantine's contract, not a run. Its `SOUJI_QUARANTINE_ALLOW_LIVE=1` is safe only
  because the fixture creates its own `mktemp` repos and names no live path; FC-1 asserts both.
- `tools/souji-census.sh` remains non-Q4-compliant when invoked bare (`/tmp` default); the suite
  pins `TMPDIR=/var/tmp` but the tool is still a debt.
- Q8's literal QUALITY regex is unsatisfiable with GNU timeout option order; FC-1 uses the
  behavioral fixture plus a corrected static regex and says not to report the literal regex as
  passing.
- C3's admissible bound is narrower than ReviewSize's full matrix: the landed fixture covers one
  normal repo plus promisor/partialClone refusals; no link/bare/worktree/corrupt shapes, no
  syscall trace, no atime/ctime. C3 must not be widened.

## Final checks for L1 (not run here)

Run the file's `FC-0` preamble, then FC-7, FC-1 (red then green), FC-2, FC-3, FC-5, FC-4, FC-6,
then the postamble. The key literals: baseline quarantine sha `141c0fdc…`; red exit 1 with
`SUMMARY total=5 failed=4`; green exit 0 with `5/5 PASS`; gate `35/35 passed` and frozen
`frozen_files=7`; size `ids=5/5`; census HEAD `mined=16 queued=15 rejected=2`; ShellCheck exit 0.
