# FinalEvidencePlan — round 14, w1

Seat: `SoujiR14.FinalEvidencePlan` (executor, leaf). Lane root:
`/home/vgpnk/Projects/shokunin/souji-shokunin`. Axes: calibration and operability.

Owned deliverables:

- `census/round-14/verification-plan.json` — the machine-readable plan.
- this report.

No other file was written. No commit, no delegation, no runtime change.

## Evidence class

**Code inspection only.** This seat executed no command from the plan: no
selftest, fixture, census, ShellCheck, source census, build, lint, formatter,
smoke run or deletion. Every expected literal below is derived from the landed
source at the digest shown, or from the owning executor's report where that
report itself says it is pre-run. Nothing in this report is an observed run
result. Certification stays OFF.

Tools installed or upgraded by this seat: **none**, and none are needed:
ShellCheck 0.11.0, Python 3.14.7, bash 5.3.15, git 2.55.0 and GNU coreutils
9.11 are already present, and the C2 report records `strace` present. The
host-safety directive is reflected in the plan's ShellCheck check: if a tool
were absent, first run `pacman -Sp --print-format '%n %v' <pkg>` and proceed
only when every listed package is not installed; never `-Sy`/`-Syu`/`-U`/`-R`,
downgrade or restart services; record version, channel and reason. No install
was performed here.

## Artifacts read at hand-off

| path | sha256 when the plan was finalized |
|---|---|
| `tools/souji-evidence-cache.py` | `dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6` |
| `tests/fixtures/r14-evidence-cache.py` | `95b371ab667a61aebb673b003dda87ed2ade40d286706fa2bdf5785522b6d26a` |
| `tests/fixtures/r14-cache-frozen/{record,expected}.json` | pinned by `expected.json`; record `67221a33…`, dependency `875598b6…` |
| `tools/souji-census.sh` | still moving during hand-off (CensusBoundary's report pinned `2cf44ee9…`; the tree changed after). L1 must read the committed bytes, hash them, and re-derive the selftest count. No digest here is a final pin. |
| `tests/fixtures/r14-census-boundary.py` | `bdcbfbc01e1d1063f2cfdaefb431ebaa3df720c79419ea69bbe63d03a5d18634` at report write; CensusBoundary's report pinned the earlier `d712ac79…` |
| `census/round-14/cache-demonstration.py` | `fc6f69a00a0bb4702e650936691aa0e347bb1fa9a809e3552d8f9371fba29d8a` |
| `corpus/SOURCES.md` (working tree) | 40 source rows; S038–S040 landed |
| `census/round-14/verification-plan.json` | `7da18f6c079f146165383d5a8914f57280bee4962204c5c808513ee8f575a414` |

CacheGate's report independently confirms `selftest: 39/39` as its older
target and 39→48 cases after review fixes; the final landed tool has **48**
`cases.append` sites. CensusBoundary's report pins the final C2 bytes above and
states the pre-run red/green targets. Both are cited as report evidence, not as
exercised evidence.

## Plan shape

Schema `souji-round-verification-plan-v1`, 10 checks, one harness preamble and
one postamble. Every entry gives an absolute executable, absolute artifact
paths (or the exported `$R` / `$SCRATCH`), environment pins, timeout, expected
exit, expected literals/ids and a failure class. `$SCRATCH` is
`mktemp -d /var/tmp/souji-r14-verify.XXXXXX`, cleaned by an EXIT trap.

Outcome taxonomy in the plan:

- **pass** — declared pass exit and every literal matches;
- **expected_red** — the pre-r14 baseline fails the C2 refusal cases for
  observed access-before-refusal reasons; this is a pass of the test, not of
  the baseline tool;
- **fail** — ran and contradicted the contract (wrong exit, missing/extra id,
  timeout, traceback);
- **could_not_evaluate** — absent/non-regular/symlinked artifact, unpinned
  digest, missing prerequisite, fixture setup exit 2, zero cases. Never a pass.

No `--retry-failed`, no retained green, no prior result reuse. The plan says
this explicitly; `census/round-13/run-verification.py`'s retainer reuses a green
without comparing measurement-time dependency digests, so it is excluded.

## Checks and unrun expectations

### C-R14V-00 — preflight and byte identity

Commands: repo toplevel must be the lane; `HEAD` captured as a 40-hex
`MEASURED_COMMIT`; `git status --porcelain -- tools tests census/round-14`
must be empty; every artifact must be a regular non-symlink file; before/after
sha256 maps must match; each `git show $MEASURED_COMMIT:<path>` digest must
equal the installed file digest.

Expectation: exit 0. Any dirty target path, missing committed artifact or
digest mismatch is **could-not-evaluate**, not a pass; a run before the L1
commit cannot name the bytes it measured.

### C-R14V-01 — Q4/Q16 isolation statics

`grep -c 'TMPDIR:-/tmp'` over both fixtures must sum to 0; each fixture must
contain `/var/tmp`; no actual `/dev/shm` use (`mktemp`/`dir=`/`TMPDIR=`)
may appear in either fixture, the C1 gate or the demo. Docstrings that say
"no /dev/shm" are not uses and do not fail the check. Expectation: all exit 0.

### C-R14V-02 — C1 gate `--selftest`

Command: `/usr/bin/timeout --kill-after=10 180 /usr/bin/python3 -B
$R/tools/souji-evidence-cache.py --selftest`.

Expectation: exit 0; final line `selftest: 48/48 passed`; no `FAIL `,
`selftest-unavailable` or traceback. A second command asserts the printed
denominator equals the landed `cases.append` count (48 at inspection) and is
at least 48, so a zero-case or shrunken suite cannot pass.

The plan carries the 48-case id/exit mapping read from the source, including:
`dependency-digest-mismatch` (1), `dependency-missing` (1), `matched-false`
(1), and the level-2 ids `path-symlink`, `path-escape`, `path-absolute`,
`path-protected`, `record-protected`, `root-protected`, `root-symlink`,
`key-noncanonical`, `key-invalid-encoding`, `verdict-false-pass`,
`verdict-false-fail`, `dependency-undeclared`, `dependencies-invalid`,
`require-invalid`, `root-not-directory`, `record-unreadable`, `path-invalid`,
`path-not-directory`, `frozen-unreadable`, `frozen-malformed`,
`frozen-schema`, `snapshot_tampered`, `frozen-incomplete`,
`snapshot-verdict-mismatch`. The mapping is a snapshot at digest `dd279ba9`;
if L1's committed digest differs, re-derive it. The command still checks
non-vacuity, but the snapshot is not evidence for added cases.

Exit 1 or a missing/extra id = fail. Exit 2 with `selftest-unavailable` =
could-not-evaluate. The plan also requires `/var/tmp/souji-r14-cache-selftest.*`
to be gone after the run.

### C-R14V-03 — committed C1 frozen snapshot

`--frozen tests/fixtures/r14-cache-frozen` must exit 0 with
`souji-evidence-cache: reusable`, `record_name: r14-cache-frozen`,
`measured_commit: 0123456789abcdef0123456789abcdef01234567`,
`dependencies: 1`, `frozen_files: 2`. A copied fixture with one appended byte
in `dependency.txt` must exit 2 with `finding snapshot_tampered:` and
`souji-evidence-cache: could-not-evaluate`. The lane fixture must stay
unmodified. The pins are literals:
`dependency.txt 875598b6f830e010b5fc1c6db42528ef127423623e1af60d276be6527623366a`,
`record.json 67221a338ef4ada7505d26a41cc634fcbabb1e6b64e8ef47138e7b766871df41`.

### C-R14V-04 — cache demonstration

`/usr/bin/python3 -B census/round-14/cache-demonstration.py --gate
$R/tools/souji-evidence-cache.py` must exit 0 and emit one JSON document.
Assertions in the plan: schema `souji-r14-cache-demonstration-v1`, status
`ok`, `failed_checks == []`, `advisories == []`, all `checks` true,
`producer_executions_new_policy == 3`, `producer_executions_old_policy == 1`,
gate `sha256` equal to the installed gate digest and to `sha256_after`,
`regular true` / `symlink false`, record unchanged, dependency bytes changed
while alpha/record/gate stayed unchanged, isolation under `/var/tmp`, cleaned
with empty residue, `deletion_certification == "OFF"`, and
`measured_commit == $MEASURED_COMMIT`.

Per-case: `unchanged` exits 0, retains without a producer,
`result.result_origin == "retained-from-record"`, executions still 1;
`dependency-modified` exits 1, not reusable, executions 2, gate findings
include `dependency-digest-mismatch`; `legacy-no-dependencies` exits 2, not
reusable, executions 3, findings include `dependencies-legacy`. The three gate
invocations must carry one identical `measured_commit`.

The demo records the gate digest itself; a blocked payload (exit 2: missing
gate, unavailable measured commit, unavailable isolation) is
**could-not-evaluate**, not a reusable result.

### C-R14V-05 — legacy census selftest

`TMPDIR=/var/tmp bash tools/souji-census.sh --selftest`, outer
`timeout --kill-after=10 180`. Expectation: exit 0; final line matching
`^selftest: 66 checks, 0 failed$`; the printed fixture base
`(/var/tmp/souji-census-selftest.XXXXXX)`; the two new boundary PASS lines
`PASS protected root refused before access (exit 2, path-protected)` and
`PASS protected compare alias refused (exit 2, path-protected)`; no `/tmp`
base and no residue under `/var/tmp`.

66 is derived from 63 `st_ok`/`st_bad` call sites in `run_selftest`, one of
which runs once for each of four malformed-baseline files. The baseline had 59
sites; no legacy check was removed. If C2's final selftest differs, re-count
sites and loop multiplicities; this plan's floor is 66, so a lost check fails.

### C-R14V-06 — ShellCheck warning gate

`shellcheck --version` must print `version: 0.11.0`; `shellcheck -S warning
$R/tools/souji-census.sh` must exit 0 with empty stdout and stderr. Any SC code
at warning severity is a fail. Absent ShellCheck is **could-not-evaluate**
(install by the RULES channel and record tool/version/channel/reason).

### C-R14V-07 — source census, S038–S040

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji` must exit 0; final line
`souji<TAB>ok<TAB>/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`;
no `souji<TAB>E**` line. W-codes are advisory and must be recorded; the
baseline had W04 for S035/S036, and S038 now shares the gnu.org timeout URL
with S034 across scopes, so an additional W04 is possible and not a failure.

Registry expectations at plan time: 40 rows; A=36, B=3, C=1; mined=23,
queued=15, rejected=2; S038, S039 and S040 each once, tier A, mined, opened
2026-10-20; S034 still present once. `git diff --numstat $BASE --
corpus/SOURCES.md` must show **zero deleted lines** and at least three
inserted lines. (The earlier expected `1 0` assumed S038 alone; the landed
registry also contains S039 and S040, so the plan checks 0 deletions and ≥3
insertions instead.)

S039's source cell cites the C1 gate sha256; the plan asserts that string
equals `sha256sum tools/souji-evidence-cache.py` at run time. The S038 anchor
is re-read at the vendor source: `/usr/share/info/coreutils.info.gz` lines
15319–15320 must contain the `KILL` sentence and 15363–15365 must contain
`124 if COMMAND times out`.

A later S041 changes the counts and must be re-derived, not hidden. An absent
S039/S040 at L1 time means the registry changed after this plan; re-derive.

### C-R14V-08 — external C1 fixture

`/usr/bin/python3 -B tests/fixtures/r14-evidence-cache.py --tool
$R/tools/souji-evidence-cache.py --frozen-dir
$R/tests/fixtures/r14-cache-frozen` must exit 0, final line
`fixture: 22/22 checks passed`, with exactly the 22 named `ok` lines
(`selftest`, `external-clean`, `changed-dependency`,
`unchanged-unrelated-change`, `missing-dependency`, `symlink-dependency`,
`malformed-hash`, `path-escape`, `matched-false`,
`legacy-no-dependencies`, `empty-dependencies`, `duplicate-json-keys`,
`nonregular-dependency`, `malformed-measured-commit`, `nonboolean-matched`,
`require-undeclared`, `protected-root`, `protected-record`, `frozen-clean`,
`frozen-tampered`, `frozen-verdict-mismatch`, `per-result-commit`) and no
`FAIL`/traceback. The plan also asserts the printed denominator equals the
landed `check(results, …)` call count minus the definition (22) and is at
least 22.

Red prerequisite arm: `--tool $SCRATCH/absent-cache.py` must exit **2** with
`fixture: tool missing:`; the plan records this as a prerequisite refusal, not
a gate pass. This deliberately corrects the GateRegistry draft, which expected
exit 1 with all cases FAIL; the landed fixture returns 2.

### C-R14V-09 — C2 boundary red/green

Baseline materialization: `git show
$BASE:tools/souji-census.sh` to `$SCRATCH/souji-census.baseline.sh`, chmod
700, regular non-symlink, sha256
`6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`.

Green: run the fixture with `--tool $R/tools/souji-census.sh`. Expect exit 0;
first line
`TOOL<TAB>/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh<TAB>sha256=<64hex>`;
nine `CASE<TAB>R14C2-0[1-9]<TAB>PASS<TAB>ok`; final
`SUMMARY<TAB>total=9<TAB>failed=0`; empty stderr; no canary; the TOOL digest
must equal `sha256sum tools/souji-census.sh`.

Red: run the same fixture with the baseline path. Expect fixture exit 1,
`TOOL` digest equal to the a31642d digest, `R14C2-01` through `R14C2-06` and
`R14C2-09` FAIL, `R14C2-07` and `R14C2-08` PASS, and
`SUMMARY<TAB>total=9<TAB>failed=7`. At least one failure detail must show
`strace store access`, `forbidden tool invoked` or `exit=… want 2`; a
`tool not readable` red is not a red. CensusBoundary's report independently
states this same red set and green result as pre-run targets.

Case meanings, from the fixture: 01 store root; 02 store descendant
(`sessions`, mode 000); 03 `$HOME` ancestor; 04 root symlink into the store;
05 `--compare` direct and alias; 06 gitfile / `.git` symlink / commondir
aliases; 07 safe normal green control; 08 `.scratch` symlink green control
with `scratch_bytes=0`; 09 inherited `GIT_*` redirects. The fixture uses a
synthetic HOME, PATH spies and `strace -f`; exit 2 is setup failure
(**could-not-evaluate**), not a pass or a red.

## Postamble

Recompute the sha256 map, compare it byte-for-byte, require `HEAD` to equal
`$MEASURED_COMMIT`, require the target pathspec still clean, and re-check
`git show $MEASURED_COMMIT:<path>` for the tools/fixtures. Any drift makes the
measured-commit claims **could-not-evaluate**.

## Risks and open items

1. **C1 bytes moved during the wave.** The tool grew from 23→31→39→48 selftest
   cases while this plan was being written. The final mapping is the 48-case
   source at `dd279ba9`; CacheGate's report confirms the 48-case selftest and
   22-case fixture. If the committed digest differs, re-derive before trusting
   the mapping; do not reuse stale ids.
2. **C2 bytes kept moving after its report.** CensusBoundary's report pinned
   `2cf44ee9…` / `d712ac79…`; the working tree reached `9aefdcbc…` (census) and
   `bdcbfbc0…` (fixture) while this plan was being finalized. The plan's C2
   expectations are interface-stable (9 ids, same red/green set), but the
   selftest floor 66 and the `TOOL` digest comparison must be re-derived from
   L1's committed bytes. A digest mismatch is not a pass.
3. **The source registry is larger than the wave contract predicted.** S038,
   S039 and S040 are already present (40 rows, not 38). S039 cites the C1
   implementation digest, and S040 adds a Python pathlib row. The plan verifies
   the observed state and avoids the SourceLedger-only 38-row/1-insertion
   expectation. A later row changes the counts.
4. **GateRegistry drafts are not expectations.** Its proposed `SOUJI-R14-*`
   ids, `R14C1-*` ids, missing-tool exit 1 and red cases `-01/-05/-08` do not
   match the landed code. This plan uses the landed ids; the red cases are
   `-01..-06` and `-09`, with `-07/-08` green controls.
5. **C2 residuals** (from CensusBoundary): hardlinked object files/arbitrary
   hardlinks into the store are not detectable without stat'ing the store; the
   guard and later access are not atomic; unsupported local configs fail
   closed; `git status` may read/hash tracked content. These are nonclaims, not
   passes.
6. **C1 limits** (from CacheGate): digest eligibility over declared
   dependencies only; no completeness/transitivity, no historical execution
   proof, runtime inputs unmeasured, point-in-time verdict. The frozen fixture
   pins its inputs but `expected.json` is the caller's trust anchor.
7. **No retained green.** The plan forbids `--retry-failed` and prior-result
   reuse; all checks are fresh at the measured commit. If L1 chooses to retain
   anything, it must route through `tools/souji-evidence-cache.py` with
   measurement-time dependency digests and record exit/findings; the simplest
   correct choice is zero retention.
8. **No runs by this seat.** All expected values are source-inspected. The C2
   fixture's setup requires `strace`; absence is could-not-evaluate. The
   census selftest floor of 66 is derived, not printed by this seat.

## Final L1 command set

The authoritative exact strings are `census/round-14/verification-plan.json`
(`harness`, each `checks[].commands[].shell`, `postamble`). In order:

1. `C-R14V-00` preflight/byte identity.
2. `C-R14V-01` isolation statics.
3. `C-R14V-02` `tools/souji-evidence-cache.py --selftest`.
4. `C-R14V-03` frozen clean + tampered.
5. `C-R14V-08` external C1 fixture installed arm + missing-tool refusal.
6. `C-R14V-09` C2 fixture installed green, then baseline red.
7. `C-R14V-04` cache demonstration.
8. `C-R14V-05` legacy census selftest.
9. `C-R14V-06` ShellCheck `-S warning`.
10. `C-R14V-07` sources validate/histogram/append-only/S039 digest/S038
    locator.
11. Postamble digest and HEAD re-check.

Do not run `census/round-13/run-verification.py --retry-failed` for this
evidence. Do not write `census/operator-sweep-*`. Do not touch the real
credential store; every C2 case uses synthetic `/var/tmp` bytes.
