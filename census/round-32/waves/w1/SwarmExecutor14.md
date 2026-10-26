# SwarmExecutor14 — r32 C2 items T17, T18 (scratch: `/fast/scratch/hyaku/souji-r32/C2Fix20/`, clone `c`, origin removed)

## Status
STATUS: PARTIAL — **T17 PASS** (needs one file beyond the named set: `tools/souji-seat-audit.py`); **T18 FAIL 48/52**, and the remaining four failures are structural: its `--baseline` red-before arms execute entrypoint bytes pinned at `12516f7…`, which create scratch under a literal `/var/tmp` before the stub producer, so no revision of live files can satisfy the frozen predicate. Both named fixtures are patched, host-behaviour-identical, and delivered.

## Evidence
All lane commands run with `python3 -B`; scratch `TMPDIR=/fast/scratch/hyaku/souji-r32/C2Fix20/tmp`; revisions: base `85b61a151923986e7e6b48f7084b9122561b5f3d`, named-files commit `b281f975dbb57597de2f9ce1fad3b4ba51dcd1f8`, named+transitive `32d1428f6d84290c1d7526b9957f54e7c85a8650`.

1. Counter at the named-files-only commit (proves the named set alone is insufficient):
```
ITEM	T17	FAIL	base=rc0:W345:SUMMARY total=66 pass=66 fail=0 base_discriminating=0	sbox=rc1:W346:SUMMARY total=66 pass=59 fail=7 base_discriminating=0	regress
ITEM	T18	FAIL	base=rc0:W4235:SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=26	sbox=rc1:W4204:SUMMARY total=52 pass=40 fail=12 blocked=0 inventory=exact baseline_mismatches=26	regress
SUMMARY items=2 pass=0 fail=2 partial=1 rev=b281f975dbb57597de2f9ce1fad3b4ba51dcd1f8
```
2. Counter at the delivered commit:
```
ITEM	T17	PASS	base=rc0:W345:SUMMARY total=66 pass=66 fail=0 base_discriminating=0	sbox=rc0:W346:SUMMARY total=66 pass=66 fail=0 base_discriminating=0
ITEM	T18	FAIL	base=rc0:W4232:SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=26	sbox=rc1:W4249:SUMMARY total=52 pass=48 fail=4 blocked=0 inventory=exact baseline_mismatches=26	regress
SUMMARY items=2 pass=1 fail=1 partial=1 rev=32d1428f6d84290c1d7526b9957f54e7c85a8650
```
`python3 -B …/census/round-32/c2-counter.py --root <clone> --rev <rev> --base 85b61a1… --list-rev 3ec84fc8… --only T17,T18 --scratch <scratch>/cnt`
3. The four surviving T18 failures (sandbox run of the patched fixture, same argv/env as the counter):
```
CASE	FAIL	baseline-r14-helper	baseline_tripwire=0 changed_exit2=1 changed_path_named=1 stdout_empty=1 output_absent=1
CASE	FAIL	baseline-r14-frozen	baseline_tripwire=0 changed_exit2=1 changed_path_named=1 stdout_empty=1 output_absent=1
CASE	FAIL	baseline-targeted-wrapper	baseline_tripwire=0 changed_exit2=1 changed_path_named=1 stdout_empty=1 output_absent=1
CASE	FAIL	baseline-demo-helper	baseline_tripwire=0 changed_exit2=1 changed_path_named=1 stdout_empty=1 output_absent=1
SUMMARY	total=52	pass=48	fail=4	blocked=0	inventory=exact baseline_mismatches=26
```
4. Named commands, once with `TMPDIR` set and once with it unset (run from the clone at `32d1428f`):
```
T17 TMPDIR set    rc=0  SUMMARY	total=66	pass=66	fail=0 base_discriminating=0
T17 TMPDIR unset  rc=0  SUMMARY	total=66	pass=66	fail=0 base_discriminating=0
T18 TMPDIR set    rc=0  SUMMARY	total=52	pass=52	fail=0 blocked=0 inventory=exact baseline_mismatches=26
T18 TMPDIR unset  rc=0  SUMMARY	total=52	pass=52	fail=0 blocked=0 inventory=exact baseline_mismatches=26
```
5. No-harm on the auditor tool (item T10): selftest output byte-identical, base blob `85b61a1…` vs patched clone, `diff` empty, both `SELFTEST	pass=118	fail=0`, rc 0. Counter verdict for T10 is unchanged by my hunk: `ITEM T10 FAIL base=rc0:W60:SELFTEST pass=118 fail=0 sbox=rc1:W0/W1:PASS h8-trunc-header-rel` at `b281f97` and at `32d1428f` alike (T10's own defect, see finding 4).
6. Both delivery diffs apply cleanly at base: `git -C <base clone at 85b61a1…> apply --check deliver-SwarmExecutor14.diff` → ok; same for `deliver-SwarmExecutor14-transitive.diff` → ok.

## Findings
1. **T17 scratch root** — `tests/fixtures/r20-audit-contract.py:433` (base) `top = Path(tempfile.mkdtemp(prefix="souji-r20-audit-contract.", dir="/var/tmp"))`; docstring `:4-5` claimed a `/var/tmp` scratch. Fixed: `dir=` dropped (tempfile honours `TMPDIR`), docstring says `temporary directory (honouring TMPDIR)`. Synthetic case strings that merely name `/var/tmp` (`:120`, `:228-364`) are auditor *data* and are untouched.
2. **T17 needs the auditor's grant grammar** — with the fixture fixed alone, the sandbox world lives under `TMPDIR` and the auditor refuses every `OWN ONLY` path outside two hard-coded roots, so seven cases flip to `V-WRITE-SCOPE` (`own-only-exact`, `own-only-exact-nonfinal`, and the five `mv-*` cases). Root cause is `tools/souji-seat-audit.py:128` (base): `ABS_RE = re.compile(` — the pattern admits only `home` and `var/tmp`. Fix: build the alternative root set from `tempfile.gettempdir()` as well (`OWN_ROOTS`, keeping `home` and `var/tmp` first), so the caller's scratch root is a declared write root. This is the same C2 class (a lane tool pinned to the old scratch root); measured effect: `T17` 59/66 → 66/66 in the sandbox, 66/66 on the host with `TMPDIR` set and unset, auditor selftest byte-identical (evidence 5).
3. **T18 scratch root** — `tests/fixtures/r20-input-binding.py:31` (base) `TMP_ROOT = Path("/var/tmp")`, child env `:48-49` `HOME`/`TMPDIR` both `/var/tmp`, and `:1258` `tempfile.TemporaryDirectory(prefix="souji-r20-input-binding-", dir=TMP_ROOT)`. Fixed: `TMP_ROOT = Path(tempfile.gettempdir())`, child `HOME`/`TMPDIR` both `str(TMP_ROOT)` (previously one and the same directory, so the parent/child relation is preserved), comment states the single carried value. Host parity: 52/52 and the same SUMMARY line with `TMPDIR` set and unset; `baseline_mismatches=26` unchanged (pre-existing digest drift against `12516f7…`, identical at base).
4. **T18's called entrypoints also pinned scratch (live code)** — `census/round-13/run-verification.py:54` `ENV.update(TMPDIR="/var/tmp", …)`, `:200` `"w", prefix="souji-r13-retention.", suffix=".json", dir="/var/tmp",`, `:464` `TemporaryDirectory(… dir="/var/tmp")`; `census/round-14/run-verification.py:19`, `:136`; `census/round-14/run-targeted.py:57`; `census/round-14/cache-demonstration.py:99` `TMP_BASE = "/var/tmp"` and `:107` `"TMPDIR": TMP_BASE,`. All now derive from `tempfile.gettempdir()`; scope/report text that names `/var/tmp` (`run-verification.py:169`, `run-targeted.py:83`, `cache-demonstration.py:10,79,514,1011,1055,1121`) is untouched data. Measured effect inside the sandbox: 40/52 → 48/52.
5. **T18 structural blocker (unfixable by live files)** — `tests/fixtures/r20-input-binding.py`'s baseline arms read entrypoint bytes at `--baseline 12516f7…` (`make_git_sandbox(…, root, revision, …)`), and the pinned blobs create scratch before the stub producer: `census/round-14/run-verification.py` at `12516f7…:18` `ENV.update(TMPDIR="/var/tmp", …)` and `:93` `with tempfile.TemporaryDirectory(prefix="souji-r14-verification-", dir="/var/tmp") as temp:`; `run-targeted.py:30`; `cache-demonstration.py:95` `TMP_BASE = "/var/tmp"`; `round-13/run-verification.py:54,174,436`. Direct reproduction against the pinned bytes, inside the counter's sandbox:
```
python3 -B census/round-14/run-verification.py   (clone checked out at 12516f7dcdd5b165e5ee208d44a38d63b5bd5812, /var/tmp read-only)
    _os.mkdir(file, 0o700)
OSError: [Errno 30] Read-only file system: '/var/tmp/souji-r14-verification-po55pdlr'
pinned-r14-rc=1
```
   The r13 arms survive only because `run()` is called before their `TemporaryDirectory`; r14/targeted/demo create scratch first, so the tripwire never fires (`baseline_tripwire=0`). Since the pinned revision is immutable, those four arms cannot reach the producer under a read-only `/var/tmp` at any rev.
6. **T10 pre-existing, not mine** — `tools/souji-seat-audit.py`'s own selftest still creates a `/var/tmp` scratch directory; that item fails identically before and after my hunk (evidence 5). My hunk is at `:128-134` only and does not touch it; the T10 seat's fix will be adjacent but not conflicting.

## Attack log
ATTACK (item enumeration, not counter logic). **C2 item T18 is unsatisfiable as frozen.** `census/round-32/c2-items.tsv` T18 (`python3 -B tests/fixtures/r20-input-binding.py --baseline 12516f7…`, files `tests/fixtures/r20-input-binding.py`) requires the sandboxed run to print the base run's last line. Its own baseline arms must execute entrypoint bytes at `12516f7…`, and those bytes create `/var/tmp` scratch before the stubbed producer (finding 5, reproduced), so the sandbox necessarily aborts four cases. Reproduced state: `48/52` at `32d1428f` with every live caller repaired; `40/52` at `b281f97`; `52/52` outside the sandbox. Routes to `PASS` that I did **not** take because they void the measurement: repinning `--baseline` (item-set change, and the arms stop being red-before), overwriting the baseline checkout with current bytes (destroys the red-before witness), or redirecting the pinned code's `tempfile` inside the driver (measures edited historical code). Consequence for the L1: C2 `fail=0` over 27 items is unreachable this round without a logged item-set decision; the counter itself is correct and no predicate needs changing. Not gameable in the other direction: T17's `PASS` is not obtained by dropping work (sandbox `W346` ≥ base `W345`) and not by touching data strings.

## Deliveries
- `.ufo/waves/round-32/w1/deliver-r20-audit-contract.py` — `tests/fixtures/r20-audit-contract.py` whole (T17, named).
- `.ufo/waves/round-32/w1/deliver-r20-input-binding.py` — `tests/fixtures/r20-input-binding.py` whole (T18, named).
- `.ufo/waves/round-32/w1/deliver-souji-seat-audit.py` — `tools/souji-seat-audit.py` whole (T17 requirement, beyond the enumerated files).
- `.ufo/waves/round-32/w1/deliver-r13-run-verification.py`, `deliver-r14-run-verification.py`, `deliver-r14-run-targeted.py`, `deliver-r14-cache-demonstration.py` — the four called entrypoints whole (T18 live-call chain; lifts 40/52 → 48/52, optional).
- `.ufo/waves/round-32/w1/deliver-SwarmExecutor14.diff` — `git -C <clone> diff 85b61a1… 32d1428f -- tests/fixtures/r20-audit-contract.py tests/fixtures/r20-input-binding.py`.
- `.ufo/waves/round-32/w1/deliver-SwarmExecutor14-transitive.diff` — same range over `tools/souji-seat-audit.py` and the four entrypoints; apply order matters only for `tools/souji-seat-audit.py` if the T10 seat also edits it.
- No tool installs or upgrades were needed; scratch `/fast/scratch/hyaku/souji-r32/C2Fix20` removed after the copies above. Lane untouched (no git/jj mutation, no writes outside `.ufo/waves/round-32/w1/`).
