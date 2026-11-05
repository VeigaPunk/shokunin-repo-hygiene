# S60MutMutation — mutation test of the two round-60 instruments

Seat `S60MutMutation` (mutation-tester, leaf). Lane `souji-shokunin` at
`1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4`; no lane file was edited, no git/jj mutation was run
in the lane, no `agent://all` message was sent.

Deliverable: this report plus `mutants/` (20 full mutant files, 20 unified diffs, two generators),
`harness/` (triplet driver and the two supplementary probes), `results/` (per-mutant
`pristine.txt` / `mutant.txt` / `restored.txt` / `triplet.json`, the tool-selftest cross-check, the
base-recorder baseline, and the divergence probes).

## 1. Instruments under test (bytes actually executed)

| instrument | path | sha256 |
|---|---|---|
| C1 substance arm | `tools/souji-freeze-check.py` | `05e9a59149704b25236a3eea4e543006b7bec30f72d8093935ba23f611fbb8a8` |
| C2 hardened writer | `tools/souji-receipt-write.py` | `367a0ca3bdea35714f1c1dba7bca407f05e8ec8d8f6e9c16f071d6e20e503d2c` |

Both instruments were still candidates when this seat started (production was at base
`1e8bfd87`, the writer absent). The L1 integrated and then amended them (commits `3b552509`,
`2670e96a`) while this seat was running, so the whole suite was re-derived and re-run against the
**production bytes above**; the earlier candidate-era numbers are superseded and are not reported.
Every mutant file in `mutants/` is a full copy of the production bytes with one defect.

## 2. Fixtures (detectors)

| fixture | path | sha256 |
|---|---|---|
| C1 8-case matrix runner | `.ufo/waves/round-60/w1/S60ExecMatrix/c1-counter.py` | `96ec711aa48359248c0ee4e7b9392e0e10f39a232fb526191635834b7e54b715` |
| C1 case builder | `.ufo/waves/round-60/w1/S60ExecMatrix/build-matrix.py` | `7ea29c3b004b6c03a2e867f70e2eeca5cd211899321085762e0aabe36fc576e2` |
| C1 matrix | `.ufo/waves/round-60/w1/S60ExecMatrix/c1-matrix.tsv` | `7973d52030f9bf7d34867c2a46527708556cf82765c1e5b4a5f087bcb310132d` |
| C2 8-case fixture | `.ufo/waves/round-60/w1/S60ExecRecorderFix/r60-receipt-write.py` | `d5291501e8ce828e26aabaea69853fe3223297f2d5ac249aee62f73bb294c114` |

The C2 fixture is the owner's frozen bytes (announced `d5291501…`). Earlier bytes `3d949978…` had a
self-contradictory case 2 (pre-created OUT then asserted OUT absent); no verdict below comes from
them.

## 3. Method

`harness/triplet.py` installs exact bytes at the path the fixture executes, then runs
pristine → mutant → restored on the same fixture, recording argv, combined output, exit code and the
sha256 of the instrument before and after every run.

* `PASS` = fixture exit 0 (all cases pass, both control stubs rejected); `FAIL` = fixture exit ≠ 0.
* `KILLED` = `pristine=PASS mutant=FAIL restored=PASS`; `SURVIVED` = mutant PASS with a passing
  baseline; `INCONCLUSIVE` = baseline (pristine or restored) did not pass — none occurred.
* Restoration is byte-exact and proved by hash, not by `git checkout`:
  `ALL_RESTORATIONS_EXACT True` over all 20 triplets
  (`restored.sha_after == pristine.sha_before == triplet.pristine_sha`).

Exact argv (every triplet in `results/*/*/triplet.json` carries its own `ARGV` line):

```
python3 -B .../S60ExecMatrix/c1-counter.py --root .../souji-shokunin \
  --matrix .../S60ExecMatrix/c1-matrix.tsv --base-tool-rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 \
  --rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 --work <work> --new-tool <dest>/c1-tool.py
python3 -B .../S60ExecRecorderFix/r60-receipt-write.py --tool <dest>/c2-tool.py --work <work>
```

Pristine baselines, identical on every pristine and restored run: C1
`SUMMARY matrix=8 forgeries_accepted=5 honest_accepted=3 stubs=REJECTED`, exit 0; C2
`SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, exit 0.

## 4. C1 — `--substance` arm against the frozen 8-case matrix

| mutant | defect | pristine/mutant/restored rc | verdict | killed by |
|---|---|---|---|---|
| `c1-m1-digest-skipped` | keeps the `instrument_sha256=` presence check, never compares it to the Counter digest | 0/1/0 | **KILLED** | `forgery-digest` → `new=accept` |
| `c1-m2-digest-self` | `want = isum` (receipt-internal self-consistency instead of Counter bytes) | 0/1/0 | **KILLED** | `forgery-digest` → `new=accept` |
| `c1-m3-rev-at-freeze` | drops `cid == freeze or`, so the freeze commit counts as before-freeze | 0/0/0 | **SURVIVED** | — |
| `c1-m4-command-skipped` | never checks `command=` against the Counter path | 0/1/0 | **KILLED** | `forgery-command-other` → `new=accept` |
| `c1-m5-instrument-name-ignored` | never checks `instrument=` equals the declared Counter path | 0/0/0 | **SURVIVED** | — |
| `c1-m6-command-missing-skipped` | does not refuse a receipt with no `command=` line | 0/0/0 | **SURVIVED** | — |
| `c1-m7-rev-missing-skipped` | does not refuse a receipt with no `rev=` line | 0/1/0 | **KILLED** | `forgery-rev-missing` → `new=accept` |
| `c1-m8-rev-invalid-skipped` | treats an unresolvable `rev=` as acceptable | 0/1/0 | **KILLED** | `forgery-rev-at-freeze` → `new=accept` |
| `c1-m9-command-substring` | reverts amendment 2: `command=` only has to *contain* the Counter path (decoy `xcounter.py` satisfies it) | 0/0/0 | **SURVIVED** | — |
| `c1-m10-duplicates-ignored` | reverts amendment 2: conflicting duplicate binding lines are not refused | 0/0/0 | **SURVIVED** | — |

5 killed / 5 survived.

## 5. C2 — hardened writer against the frozen 8-case fixture

| mutant | defect | pristine/mutant/restored rc | verdict | killed by |
|---|---|---|---|---|
| `c2-m1-direct-stream` | opens OUT and streams into it before the wrapped command runs (no temp+link publication) | 0/1/0 | **KILLED** | cases 3 (in-flight), 4 (kill residue), 5 |
| `c2-m2-overwrite-skip` | removes the OUT-exists refusal and publishes with `os.replace` | 0/0/0 | **SURVIVED** | — |
| `c2-m3-bound-ignored` | captures without enforcing `--max-bytes` | 0/1/0 | **KILLED** | case 5 → `tool rc=0 (want 2)` |
| `c2-m4-dirty-skip` | never consults `git status` | 0/1/0 | **KILLED** | case 8 → `tool rc=0 (want 2)` |
| `c2-m5-rev-short-accept` | accepts a 7..40 hex prefix | 0/1/0 | **KILLED** | case 6 → `tool rc=0 (want 2)` |
| `c2-m6-digest-worktree` | digests the worktree bytes, not the committed blob (equality check removed) | 0/0/0 | **SURVIVED** | — |
| `c2-m7-command-omitted` | omits the `command=` field | 0/1/0 | **KILLED** | case 1 → `command= line missing/wrong` |
| `c2-m8-link-to-replace` | publishes with `os.replace` instead of EEXIST-safe `os.link` (TOCTOU) | 0/0/0 | **SURVIVED** | — |
| `c2-m9-no-stale-sweep` | no longer sweeps a `*.tmp` left by an earlier SIGKILL | 0/0/0 | **SURVIVED** | — |
| `c2-m10-outside-outdir-allowed` | never refuses an OUT directory outside the lane root | 0/0/0 | **SURVIVED** | — |

5 killed / 5 survived.

## 6. Surviving mutants — the exact assertion each fixture is missing

Each survivor was confirmed behaviourally distinct with a probe that runs pristine and mutant on the
same rebuilt repo (`harness/probe_c1.py`, `harness/probe_c2.py`); receipts in `results/probes/`.

### 6.1 `c1-m3-rev-at-freeze` — the matrix row is mislabelled and never reaches the at-freeze branch

`matrix/forgery-rev-at-freeze/ctl.txt` carries `rev=freezemark`, a **tag name**, not a 40-hex id.
The arm resolves `cid = repo.commit(rv) if FULL40.match(rv) else None`, so the receipt is refused as
`CONTROL-REV-INVALID`, not `CONTROL-REV-NOT-BEFORE-FREEZE`:

```
$ python3 -B tools/souji-freeze-check.py --root <rebuilt case> --prereg pre.txt --rev <freeze> --substance
FINDING C1 CONTROL-REV-INVALID ctl.txt rev='freezemark' does not resolve to a commit
SUMMARY claims=1 findings=1
EXIT=1
```

Missing assertion: a receipt whose `rev=` is the literal **40-hex freeze commit id** must be refused
as `CONTROL-REV-NOT-BEFORE-FREEZE`. Two consequences:

1. The matrix row labelled `rev-at-freeze` is covered by the `CONTROL-REV-INVALID` arm;
   `c1-counter.py` only compares accept/refuse and never asserts the finding class, so the mislabel
   is invisible to the claim.
2. The `cid == freeze` branch is unreachable **by construction** through the receipt interface: the
   Control receipt is read as the blob at FREEZE, and a file committed in the freeze commit cannot
   contain that commit's own id. The arm's own selftest also only reaches the non-ancestor disjunct.
   So this survivor is a labelling/coverage finding, not a case that can be added cheaply.

### 6.2 `c1-m5-instrument-name-ignored` — no case has `instrument=` naming a different file

```
edit=instrument-name pristine_exit=1 findings=CONTROL-INSTRUMENT-MISMATCH mutant_exit=0
MISSING-ASSERTION-CONFIRMED
```

Missing assertion: one refuse row where `instrument=` is a valid but different repo path (digest,
rev and command otherwise honest). The arm's own selftest has it (`substance-instrument-mismatch`).

### 6.3 `c1-m6-command-missing-skipped` — no case omits `command=` while the other fields are valid

`forgery-kind-only` lacks `command=` too, but also lacks `instrument=`/`instrument_sha256=`/`rev=`,
so the other refusals fire first and the mutant still refuses.

```
edit=command-missing pristine_exit=1 findings=CONTROL-COMMAND-MISSING mutant_exit=0
MISSING-ASSERTION-CONFIRMED
```

Missing assertion: a refuse row with valid instrument/digest/rev and no `command=` line. The arm's
own selftest has it (`substance-command-missing`).

### 6.4 `c1-m9-command-substring` — amendment 2 (argv-token naming) has no test at all

The amended arm requires the Counter to appear as an **argv token** (`command_names`), so
`python3 -B xcounter.py` is a decoy. The matrix's only command forgery names an unrelated tool, which
substring matching also refuses. Probe on `honest-1` with `command=python3 -B xcounter.py --selfcheck`:

```
edit=command-decoy pristine_exit=1 findings=CONTROL-COMMAND-MISMATCH mutant_exit=0
MISSING-ASSERTION-CONFIRMED
```

Missing assertion: a refuse row whose `command=` contains the Counter path as a **substring of a
longer token** (e.g. `xcounter.py`, `counter.py.decoy`). Neither the frozen matrix nor
`--selftest --substance` covers it (see §7), so amendment 2 currently ships untested.

### 6.5 `c1-m10-duplicates-ignored` — amendment 2 (duplicate binding lines) has no test at all

Probe on `honest-1` with a second, conflicting `rev=` line inserted before the final `EXIT=1`:

```
edit=duplicate-rev pristine_exit=1 findings=CONTROL-REV-DUPLICATE mutant_exit=0
MISSING-ASSERTION-CONFIRMED
```

Missing assertion: a refuse row carrying two conflicting `rev=` (and likewise `instrument=`,
`instrument_sha256=`, `command=`) lines. Neither the matrix nor the arm's selftest covers it.

### 6.6 `c2-m2-overwrite-skip` — case 2 is masked by the dirty-tree guard

Case 2 pre-creates `OUT` **inside** the fixture repo (`<repo>/receipt.txt`), which makes the worktree
dirty, so the dirty-tree guard refuses with exit 2 before the overwrite guard can be exercised. Probe
with OUT inside the root but **committed** (tree clean, same argv shape):

```
pristine: rc=2 out_unchanged=True  out_sha256=372f0c7628e2…  DIVERGENCE
mutant:   rc=0 out_unchanged=False out_sha256=26139e37a3fc…  MUTANT-OVERWROTE
```

Missing assertion: case 2 must commit OUT first (or otherwise keep the tree clean) so that only the
overwrite guard can produce exit 2.

### 6.7 `c2-m6-digest-worktree` — no case where the committed blob differs from the worktree file

Case 1's digest check passes only because the worktree instrument equals the committed blob. Probe
(instrument committed as A, worktree rewritten to B, `--allow-dirty`):

```
pristine: rc=2 committed_sha256=8f513b9f361a… receipt_sha256=None            DIVERGENCE
mutant:   rc=0 committed_sha256=8f513b9f361a… receipt_sha256=fd28f207992f…  MUTANT-WRONG-DIGEST
```

Missing assertion: one case with a modified worktree instrument and `--allow-dirty`, asserting the
receipt's `instrument_sha256` equals the **committed** blob's digest.

### 6.8 `c2-m8-link-to-replace` — no concurrent-creator case (TOCTOU)

Probe: start the tool with `sleep 1`, create OUT at 0.4 s with known racer bytes.

```
pristine: rc=2 racer_bytes_survived=True   DIVERGENCE
mutant:   rc=0 racer_bytes_survived=False  MUTANT-CLOBBERED
```

Missing assertion: a case where another process creates OUT between the pre-check and publication,
asserting the tool exits 2 and the racer's bytes survive. This is exactly the property amendment 3
added; the fixture cannot see it.

### 6.9 `c2-m9-no-stale-sweep` — no recovery-from-residue case

Probe: pre-create `<out>.deadbeef.tmp`, then run normally (`--allow-dirty`).

```
pristine: rc=0 residue=[]                        DIVERGENCE
mutant:   rc=0 residue=['receipt.txt.deadbeef.tmp']  MUTANT-LEFT-RESIDUE
```

Missing assertion: a case that plants a leftover temp and asserts the next write sweeps it. Case 4
only checks residue immediately after a kill, never the next write.

### 6.10 `c2-m10-outside-outdir-allowed` — no OUT-outside-root case

Probe: OUT in a directory outside the lane root.

```
pristine: rc=2 out_exists=False  DIVERGENCE
mutant:   rc=0 out_exists=True   MUTANT-WROTE-OUTSIDE
```

Missing assertion: a case whose OUT directory resolves outside the root, expecting exit 2 and no OUT.
This is amendment 3's confinement rule; it currently ships untested by the fixture.

## 7. Cross-check: do the instruments' own selftests kill the survivors?

| mutant | frozen fixture | own `--selftest` | killing selftest case |
|---|---|---|---|
| `c1-m1-digest-skipped` | KILLED | fail=1 rc=1 | `substance-digest-mismatch` |
| `c1-m2-digest-self` | KILLED | fail=1 rc=1 | `substance-digest-mismatch` |
| `c1-m3-rev-at-freeze` | SURVIVED | pass=12 fail=0 rc=0 | (unreachable — §6.1) |
| `c1-m4-command-skipped` | KILLED | fail=1 rc=1 | `substance-command-mismatch` |
| `c1-m5-instrument-name-ignored` | SURVIVED | fail=1 rc=1 | `substance-instrument-mismatch` |
| `c1-m6-command-missing-skipped` | SURVIVED | fail=1 rc=1 | `substance-command-missing` |
| `c1-m7-rev-missing-skipped` | KILLED | fail=1 rc=1 | `substance-rev-missing` |
| `c1-m8-rev-invalid-skipped` | KILLED | fail=1 rc=1 | `substance-rev-invalid` |
| `c1-m9-command-substring` | SURVIVED | pass=12 fail=0 rc=0 | **none** |
| `c1-m10-duplicates-ignored` | SURVIVED | pass=12 fail=0 rc=0 | **none** |
| `c2-m1-direct-stream` | KILLED | fail=2 rc=1 | `atomic-signal`, `max-bytes` |
| `c2-m2-overwrite-skip` | SURVIVED | fail=1 rc=1 | `overwrite: existing OUT byte-identical, no temp file` |
| `c2-m3-bound-ignored` | KILLED | fail=1 rc=1 | `max-bytes` |
| `c2-m4-dirty-skip` | KILLED | fail=1 rc=1 | dirty-tree case |
| `c2-m5-rev-short-accept` | KILLED | pass=12 fail=0 rc=0 | none (fixture only) |
| `c2-m6-digest-worktree` | SURVIVED | fail=2 rc=1 | `always-write`/`always-refuse` stub rejection |
| `c2-m7-command-omitted` | KILLED | fail=1 rc=1 | receipt-shape case |
| `c2-m8-link-to-replace` | SURVIVED | pass=12 fail=0 rc=0 | **none** |
| `c2-m9-no-stale-sweep` | SURVIVED | pass=12 fail=0 rc=0 | **none** |
| `c2-m10-outside-outdir-allowed` | SURVIVED | pass=12 fail=0 rc=0 | **none** |

Pristine controls: arm `SELFTEST cases=12 pass=12 fail=0` rc=0; writer `SELFTEST cases=12 pass=12
fail=0` rc=0. Six mutants survive **both** detectors — `c1-m3`, `c1-m9`, `c1-m10`, `c2-m8`,
`c2-m9`, `c2-m10` — i.e. every amendment added after the fixtures were frozen (amendment 2's decoy
and duplicate rules, amendment 3's TOCTOU, sweep and confinement rules) plus the unreachable
at-freeze branch. Three more (`c1-m5`, `c1-m6`, `c2-m2`, `c2-m6`) are caught by the tool's own
selftest but not by the frozen external fixture.

## 8. Observed baseline (C2 claim's comparator), same frozen fixture

`census/round-57/record-receipt.sh` (sha256 `84148011abc9…`), positional style:

```
CASE 1 clean-write fail      CASE 5 bound fail
CASE 2 overwrite fail        CASE 6 rev-short pass
CASE 3 atomic-in-flight pass CASE 7 instrument-absent pass
CASE 4 kill-residue pass     CASE 8 dirty-tree fail
SUMMARY cases=8 pass=4 fail=4 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED
EXIT=1
```

The frozen claim says the base is 3/8; on the frozen fixture bytes it is **4/8** (passes 3, 4, 6, 7 —
its `$(...)` buffering is atomic-in-effect and kill-clean). This matches the fixture owner's own
`base-run.txt`; the direction favours the base, so the C2 margin is 8 vs 4, not 8 vs 3.

## 9. Named limits

1. The detector is the fixture's **exit code**; per-case assertions are not re-derived here. A
   fixture-level bug could masquerade as a kill — mitigated only by pristine and restored passing on
   every triplet.
2. Mutants are single-defect source edits applied to exact, uniqueness-checked anchors; multi-defect
   interactions are not explored and a semantically equivalent edit would show as SURVIVED.
3. Timing cases 3/4 run on an unloaded 32-core host; under load a pristine run could fail and the
   triplet would be reported INCONCLUSIVE. None occurred.
4. `c1-m3` is unreachable by construction (§6.1); the survivor there is a labelling/coverage finding.
5. The kill-residue case kills the process group at 0.4 s of a 1 s command; no fixture can observe a
   window between `fsync` and publication without an injectable hook, so `c2-m8` needs a
   concurrent-creator case, not a timing tweak.
6. Case 2's masking (§6.6) also means the fixture's `ALWAYS-WRITE` stub rejection over case 2 is not
   evidence about the overwrite guard.
7. `--max-bytes` is exercised with one 2 MiB zero stream; non-UTF8 and single-huge-line streams are
   the reviewer's attack surface, not covered here.
8. The production instruments changed under this seat (candidate → integrated → amended); all numbers
   are the re-run on `05e9a591…` / `367a0ca3…`. A later L1 edit invalidates these verdicts and needs
   a fresh triplet run.
9. Restoration is by byte copy with sha256 proof; the lane worktree and index were never touched.
10. Probes rebuild their own fixture repos from the frozen case files; they do not modify the
    delivered fixtures.

## 10. Commands and exit codes actually run

```
# pristine baselines (production bytes)
python3 -B .../c1-counter.py ... --new-tool tools/souji-freeze-check.py        -> EXIT=0
python3 -B .../r60-receipt-write.py --tool tools/souji-receipt-write.py        -> EXIT=0
# mutant generation (aborts unless every anchor occurs exactly once)
python3 build_mutants_c1.py tools/souji-freeze-check.py mutants/c1             -> EXIT=0 (10 files)
python3 build_mutants_c2.py tools/souji-receipt-write.py mutants/c2            -> EXIT=0 (10 files)
# triplets (20 runs)
python3 triplet.py --label <m> --fixture "<fixture argv with {work}>" --pristine <tool> \
    --mutant mutants/<c>/<m>.py --dest <dest>/<tool>.py --work <work> --outdir results/<c>/<m>
# probes
python3 probe_c1.py --build-matrix .../build-matrix.py --case-dir .../matrix/honest-1 \
    --pristine tools/souji-freeze-check.py --mutant mutants/c1/<m>.py --edit <mode> --outdir ...
python3 probe_c2.py --tool <writer|mutant> --outdir ... --mode <overwrite-committed|worktree-digest|race-create|stale-temp|outside-outdir>
# tool selftests
python3 -B tools/souji-freeze-check.py --selftest --substance     -> rc=0 (12/12)
python3 -B tools/souji-receipt-write.py --selftest --work <dir>   -> rc=0 (12/12)
# base comparator
python3 -B .../r60-receipt-write.py --tool census/round-57/record-receipt.sh --work ... -> EXIT=1
```

Environment: Python 3.14.8, git 2.56.0, no network. No tool was installed or upgraded for this seat
(all pacman transactions remain paused; nothing was needed).

## 11. Artifact inventory

```
S60MutMutation.md
mutants/c1/*.py                 10 full mutant files (arm, production bytes)
mutants/c2/*.py                 10 full mutant files (writer, production bytes)
mutants/diffs/*.diff            20 unified diffs against the tested pristine bytes
mutants/build_mutants_c1.py     generator (exact-anchor, single-occurrence)
mutants/build_mutants_c2.py
harness/triplet.py              pristine/mutant/restored driver with hash proof
harness/probe_c1.py             survivor-divergence probe (C1: 4 edit modes)
harness/probe_c2.py             survivor-divergence probe (C2: 5 modes)
results/c1/<mutant>/            pristine.txt, mutant.txt, restored.txt, triplet.json
results/c2/<mutant>/
results/selftests/              20 mutant selftest outputs + 2 pristine controls
results/base-recorder-c2.txt    base recorder on the frozen fixture (4/8)
results/probes/                 probe receipts and the edited case fixtures
```
