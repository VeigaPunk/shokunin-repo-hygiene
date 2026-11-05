# S60MutMutation — mutation test of the two round-60 instruments

Seat: `S60MutMutation` (mutation-tester, leaf). Lane `souji-shokunin` at
`1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4`; no lane file was edited, no git/jj mutation was run
in the lane, no `agent://all` message was sent.

Deliverable: this report plus `mutants/` (15 full mutant files, 15 unified diffs, two generators),
`harness/` (triplet driver and the two supplementary probes), `results/` (per-mutant
`pristine.txt` / `mutant.txt` / `restored.txt` / `triplet.json`, the tool-selftest cross-check, the
base-recorder baseline, and the divergence probes).

## 1. Instruments under test (bytes actually executed)

| instrument | path | sha256 |
|---|---|---|
| C1 substance arm | `.ufo/waves/round-60/w1/S60ExecFreezeArm/souji-freeze-check.py` | `928745cd7f294320e6a37551334f32f43eb409728169bb5d8606c8b7054cb24e` |
| C2 hardened writer | `.ufo/waves/round-60/w1/S60ExecRecorder/souji-receipt-write.py` | `b916a4fd28206ac80208bc22027abc31778d8b893e8f3744270d612684b53e9f` |

The production paths (`tools/souji-freeze-check.py`, `tools/souji-receipt-write.py`) are still at
base (no `--substance` arm; the writer does not exist), so the sibling candidates were the
instruments, per the seat spec. The writer changed under me at 20:56 (revision added the missing
`chunks.append(chunk)` and the `command=` field); the mutants were regenerated from the final bytes
and every C2 number below is from that re-run against `b916a4fd…`. The arm bytes did not change.

## 2. Fixtures (detectors)

| fixture | path | sha256 |
|---|---|---|
| C1 8-case matrix runner | `.ufo/waves/round-60/w1/S60ExecMatrix/c1-counter.py` | `96ec711aa48359248c0ee4e7b9392e0e10f39a232fb526191635834b7e54b715` |
| C1 case builder | `.ufo/waves/round-60/w1/S60ExecMatrix/build-matrix.py` | `7ea29c3b004b6c03a2e867f70e2eeca5cd211899321085762e0aabe36fc576e2` |
| C1 matrix | `.ufo/waves/round-60/w1/S60ExecMatrix/c1-matrix.tsv` | `7973d52030f9bf7d34867c2a46527708556cf82765c1e5b4a5f087bcb310132d` |
| C2 8-case fixture | `.ufo/waves/round-60/w1/S60ExecRecorderFix/r60-receipt-write.py` | `d5291501e8ce828e26aabaea69853fe3223297f2d5ac249aee62f73bb294c114` |

The C2 fixture is the owner's frozen bytes (they announced `d5291501…`); earlier bytes
`3d949978…` had a self-contradictory case 2 (pre-created OUT then asserted OUT absent) and were not
used for any verdict.

## 3. Method

`harness/triplet.py` installs exact bytes at the path the fixture executes, then runs
pristine → mutant → restored on the same fixture, recording argv, combined output, exit code and
the sha256 of the instrument before and after every run.

* `PASS` = fixture exit 0 (all its cases passed, both stubs rejected), `FAIL` = fixture exit ≠ 0.
* `KILLED` = `pristine=PASS mutant=FAIL restored=PASS`; `SURVIVED` = mutant PASS with a passing
  baseline; `INCONCLUSIVE` = baseline (pristine or restored) did not pass.
* Restoration is byte-exact and proved by hash, not by `git checkout`:
  `ALL_RESTORATIONS_EXACT True` over all 15 triplets (`restored.sha_after == pristine.sha_before ==
  triplet.pristine_sha`).

Exact argv (one representative run each; every triplet in `results/*/*/triplet.json` carries its own
`ARGV` line):

```
python3 -B .../S60ExecMatrix/c1-counter.py --root .../souji-shokunin \
  --matrix .../S60ExecMatrix/c1-matrix.tsv --base-tool-rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 \
  --rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 --work <work> --new-tool <dest>/c1-tool.py
python3 -B .../S60ExecRecorderFix/r60-receipt-write.py --tool <dest>/c2-tool.py --work <work>
```

Pristine baselines: C1 `SUMMARY matrix=8 forgeries_accepted=5 honest_accepted=3 stubs=REJECTED`,
exit 0. C2 `SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`,
exit 0. Both reproduced on every triplet's pristine and restored run.

## 4. C1 — `--substance` arm against the frozen 8-case matrix

| mutant | defect | pristine/mutant/restored rc | verdict | killed by |
|---|---|---|---|---|
| `c1-m1-digest-skipped` | keeps the `instrument_sha256=` presence check, never compares it to the Counter digest | 0/1/0 | **KILLED** | `forgery-digest` → `new=accept` |
| `c1-m2-digest-self` | `want = isum` (receipt-internal self-consistency instead of Counter bytes) | 0/1/0 | **KILLED** | `forgery-digest` → `new=accept` |
| `c1-m3-rev-at-freeze` | drops `cid == freeze or`, so the freeze commit counts as before-freeze | 0/0/0 | **SURVIVED** | — |
| `c1-m4-command-skipped` | never checks that `command=` mentions the Counter path | 0/1/0 | **KILLED** | `forgery-command-other` → `new=accept` |
| `c1-m5-instrument-name-ignored` | never checks `instrument=` equals the declared Counter path | 0/0/0 | **SURVIVED** | — |
| `c1-m6-command-missing-skipped` | does not refuse a receipt with no `command=` line | 0/0/0 | **SURVIVED** | — |
| `c1-m7-rev-missing-skipped` | does not refuse a receipt with no `rev=` line | 0/1/0 | **KILLED** | `forgery-rev-missing` → `new=accept` |
| `c1-m8-rev-invalid-skipped` | treats an unresolvable `rev=` as acceptable | 0/1/0 | **KILLED** | `forgery-rev-at-freeze` → `new=accept` |

5 killed / 3 survived.

## 5. C2 — hardened writer against the frozen 8-case fixture

| mutant | defect | pristine/mutant/restored rc | verdict | killed by |
|---|---|---|---|---|
| `c2-m1-direct-stream` | opens OUT and streams into it before the wrapped command runs (no temp+rename) | 0/1/0 | **KILLED** | cases 3 (in-flight), 4 (kill residue), 5 |
| `c2-m2-overwrite-skip` | removes the OUT-exists refusal before and after the command | 0/0/0 | **SURVIVED** | — |
| `c2-m3-bound-ignored` | captures without enforcing `--max-bytes` | 0/1/0 | **KILLED** | case 5 → `tool rc=0 (want 2)` |
| `c2-m4-dirty-skip` | never consults `git status` | 0/1/0 | **KILLED** | case 8 → `tool rc=0 (want 2)` |
| `c2-m5-rev-short-accept` | accepts a 7..40 hex prefix | 0/1/0 | **KILLED** | case 6 → `tool rc=0 (want 2)` |
| `c2-m6-digest-worktree` | digests the worktree bytes, not the committed blob at rev (equality check removed) | 0/0/0 | **SURVIVED** | — |
| `c2-m7-command-omitted` | omits the `command=` field | 0/1/0 | **KILLED** | case 1 → `command= line missing/wrong` |

5 killed / 2 survived.

## 6. Surviving mutants — the exact assertion each fixture is missing

### 6.1 `c1-m3-rev-at-freeze` — the matrix row is mislabelled and never exercises the at-freeze branch

`matrix/forgery-rev-at-freeze/ctl.txt` carries `rev=freezemark`, a **tag name**, not a 40-hex id.
The arm resolves `cid = repo.commit(rv) if FULL40.match(rv) else None`, so the receipt is refused as
`CONTROL-REV-INVALID`, not `CONTROL-REV-NOT-BEFORE-FREEZE`. Direct evidence (rebuilt case repo):

```
$ python3 -B .../S60ExecFreezeArm/souji-freeze-check.py --root work/c1/c1-m3-rev-at-freeze/forgery-rev-at-freeze \
    --prereg pre.txt --rev <freeze> --substance
FINDING C1 CONTROL-REV-INVALID ctl.txt rev='freezemark' does not resolve to a commit
SUMMARY claims=1 findings=1
EXIT=1
```

Missing assertion: a receipt whose `rev=` is the literal **40-hex freeze commit id** must be
refused as `CONTROL-REV-NOT-BEFORE-FREEZE`. Two consequences:

1. The matrix row labelled `rev-at-freeze` is covered by the `CONTROL-REV-INVALID` arm; the
   `cid == freeze` branch is never reached. `c1-counter.py` only compares accept/refuse and never
   asserts the finding class, so the mislabel is invisible to the claim.
2. The branch is unreachable **by construction** through the receipt interface: the Control receipt
   is read as the blob at FREEZE, and a file committed in the freeze commit cannot contain that
   commit's own id. The arm's own `--selftest --substance` (`substance-rev-not-before`) also only
   reaches the non-ancestor disjunct. So no fixture of this shape can kill this mutant; the honest
   finding is the mislabelled row, not a missing case that could be added cheaply.

### 6.2 `c1-m5-instrument-name-ignored` — no case has `instrument=` naming a different file

No matrix case carries a valid digest/rev/command with `instrument=` pointing at another tool.
Probe (`harness/probe_c1.py`, rebuilds `honest-1`, rewrites only `instrument=counter.py` →
`instrument=other-tool.py`, runs both tools on the same repo):

```
edit=instrument-name pristine_exit=1 findings=CONTROL-INSTRUMENT-MISMATCH mutant_exit=0
MISSING-ASSERTION-CONFIRMED
```

Missing assertion: one refuse row where `instrument=` is a valid but different repo path.
(The arm's own selftest does have it: `substance-instrument-mismatch`.)

### 6.3 `c1-m6-command-missing-skipped` — no case omits `command=` while the other fields are valid

`forgery-kind-only` lacks `command=` too, but also lacks `instrument=`/`instrument_sha256=`/`rev=`,
so the other refusals fire first and the mutant still refuses. Probe (rebuilds `honest-1`, deletes
only the `command=` line):

```
edit=command-missing pristine_exit=1 findings=CONTROL-COMMAND-MISSING mutant_exit=0
MISSING-ASSERTION-CONFIRMED
```

Missing assertion: a refuse row with valid instrument/digest/rev and no `command=` line.
(The arm's selftest has it: `substance-command-missing`.)

### 6.4 `c2-m2-overwrite-skip` — case 2 is masked by the dirty-tree guard

Case 2 pre-creates `OUT` **inside** the fixture repo (`<repo>/receipt.txt`). That makes the worktree
dirty, so any writer with a dirty-tree guard refuses with exit 2 before the overwrite guard can be
exercised; the mutant passes case 2 for the wrong reason. Probe with OUT **outside** the repo
(`harness/probe_c2.py --mode overwrite-outside`, fresh repo, same argv shape):

```
pristine: rc=2 out_unchanged=True  out_sha256=372f0c7628e2…  DIVERGENCE
mutant:   rc=0 out_unchanged=False out_sha256=1719648c1445…  MUTANT-OVERWROTE
```

Missing assertion: case 2 must place OUT outside the fixture repo (or commit OUT first) so that the
overwrite refusal is the only guard that can produce exit 2.

### 6.5 `c2-m6-digest-worktree` — no case where the committed blob differs from the worktree file

Case 1's digest check only passes because the worktree instrument equals the committed blob; the
mutant binds to the worktree bytes and still matches. No case uses `--allow-dirty` with a rewritten
instrument. Probe (`--mode worktree-digest`: instrument committed as A, worktree rewritten to B,
run with `--allow-dirty`):

```
pristine: rc=2 committed_sha256=8f513b9f361a… receipt_sha256=None            DIVERGENCE
mutant:   rc=0 committed_sha256=8f513b9f361a… receipt_sha256=fd28f207992f…  MUTANT-WRONG-DIGEST
```

Missing assertion: one case with a modified worktree instrument (and `--allow-dirty`) asserting the
receipt's `instrument_sha256` equals the **committed** blob's digest.

## 7. Cross-check: the instruments' own selftests are stronger than the frozen fixtures

| mutant | frozen fixture | tool's own `--selftest` | killing selftest case |
|---|---|---|---|
| `c1-m1-digest-skipped` | KILLED | fail=1, rc=1 | `substance-digest-mismatch` |
| `c1-m3-rev-at-freeze` | SURVIVED | pass=12 fail=0, rc=0 | (unreachable — see 6.1) |
| `c1-m5-instrument-name-ignored` | SURVIVED | fail=1, rc=1 | `substance-instrument-mismatch` |
| `c1-m6-command-missing-skipped` | SURVIVED | fail=1, rc=1 | `substance-command-missing` |
| `c2-m1-direct-stream` | KILLED | pass=10 fail=2, rc=1 | `atomic-signal`, `max-bytes` |
| `c2-m2-overwrite-skip` | SURVIVED | pass=11 fail=1, rc=1 | `overwrite: existing OUT byte-identical, no temp file` |
| `c2-m6-digest-worktree` | SURVIVED | pass=10 fail=2, rc=1 | `always-write`/`always-refuse` stub rejection |

Pristine controls: arm `SELFTEST cases=12 pass=12 fail=0` rc=0; writer `SELFTEST cases=12 pass=12
fail=0` rc=0. So three of the five surviving mutants are killed by the instrument's own tests: the
external fixtures, not the instruments, are the weaker detector.

## 8. Observed baseline (C2 claim's comparator), same frozen fixture

`census/round-57/record-receipt.sh` (sha256 `84148011abc9…`), `--tool` positional style:

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
`base-run.txt`; the direction is in the base's favour, so the C2 claim's margin is 8 vs 4, not 8 vs 3.

## 9. Named limits

1. The detector is the fixture's **exit code**; per-case assertions are not re-derived here. A
   fixture-level bug can therefore masquerade as a kill. Mitigated only by the fact that pristine
   and restored both pass on every triplet.
2. Mutants are single-defect source edits applied to exact anchors; multi-defect interactions are not
   explored, and a mutant that is semantically equivalent would show as SURVIVED.
3. Timing cases 3/4 run on an unloaded host (32 cores); under heavy load a pristine run could fail
   and the triplet would be reported INCONCLUSIVE. No such case was observed.
4. `c1-m3` is unreachable by construction (6.1) — the survivor there is a labelling/coverage finding,
   not something a new matrix row can fix without changing the arm's rev grammar.
5. The C2 fixture's kill-residue case kills the process group at 0.4 s of a 1 s command; it cannot
   observe a window between `fsync` and `rename` (no fixture can without an injectable hook).
6. Case 2's masking (6.4) also means the fixture's `ALWAYS-WRITE` stub rejection over case 2 is not
   evidence about the overwrite guard.
7. `--max-bytes` bound is tested with a single 2 MiB zero stream; a non-UTF8 or single-huge-line
   stream is the reviewer's attack surface, not tested here.
8. Restoration is by byte copy with sha256 proof; the lane worktree and index were never touched.
9. Writer bytes moved once during the wave (af9327 → b916a4); all reported numbers are the re-run on
   `b916a4fd…`. Mutants `mutants/c2/*.py` are derived from those bytes only.

## 10. Commands and exit codes actually run

```
# pristine baselines
python3 -B .../c1-counter.py ... --new-tool .../S60ExecFreezeArm/souji-freeze-check.py   -> EXIT=0
python3 -B .../r60-receipt-write.py --tool .../S60ExecRecorder/souji-receipt-write.py      -> EXIT=0
# mutant generation (aborts if any anchor is not unique)
python3 build_mutants_c1.py .../S60ExecFreezeArm/souji-freeze-check.py mutants/c1         -> EXIT=0 (8 files)
python3 build_mutants_c2.py .../S60ExecRecorder/souji-receipt-write.py mutants/c2         -> EXIT=0 (7 files)
# triplets
python3 triplet.py --label <m> --fixture "<fixture argv with {work}>" --pristine <P> \
    --mutant mutants/<c>/<m>.py --dest <dest>/<tool>.py --work <work> --outdir results/<c>/<m>
# supplementary probes
python3 probe_c1.py --build-matrix .../build-matrix.py --case-dir .../matrix/honest-1 \
    --pristine <arm> --mutant mutants/c1/c1-m5-instrument-name-ignored.py --edit instrument-name ...
python3 probe_c1.py ... --mutant mutants/c1/c1-m6-command-missing-skipped.py --edit command-missing ...
python3 probe_c2.py --tool <writer|mutant> --outdir ... --mode overwrite-outside
python3 probe_c2.py --tool <writer|mutant> --outdir ... --mode worktree-digest
# tool selftests
python3 -B <tool> --selftest --substance           (C1)   -> pristine rc=0; mutants rc=1 except m3
python3 -B <tool> --selftest --work <dir>          (C2)   -> pristine rc=0; m1/m2/m6 rc=1
# base comparator
python3 -B .../r60-receipt-write.py --tool .../census/round-57/record-receipt.sh --work ... -> EXIT=1
```

Environment: Python 3.14.8, git 2.56.0, no network. No tool was installed or upgraded for this seat
(all pacman transactions remain paused; nothing needed).

## 11. Artifact inventory

```
S60MutMutation.md
mutants/c1/*.py                 8 full mutant files (arm)
mutants/c2/*.py                 7 full mutant files (writer)
mutants/diffs/*.diff            15 unified diffs against the tested pristine bytes
mutants/build_mutants_c1.py     generator (exact-anchor, single-occurrence)
mutants/build_mutants_c2.py
harness/triplet.py              pristine/mutant/restored driver with hash proof
harness/probe_c1.py             survivor-divergence probe (C1)
harness/probe_c2.py             survivor-divergence probe (C2)
results/c1/<mutant>/            pristine.txt, mutant.txt, restored.txt, triplet.json
results/c2/<mutant>/
results/selftests/              tool-selftest cross-check outputs
results/base-recorder-c2.txt    base recorder on the frozen fixture (4/8)
results/probes/                 probe receipts and the edited case fixtures
```
