STATUS: DONE — six isolated C2 mutants probed and restored; four killed by the detector pair, two survived.

# Attacked claim and axes

**C2 calibration**, specifically whether the delivered pointer selftest and external fixture discriminate plausible pointer-gate regressions. Probe dimensions: mutation sensitivity, round-boundary/false-positive control, and reproducible containment/restoration. This report does not adjudicate or integrate the round, and does not claim a defect in the pristine gate from a surviving mutant.

Revision: `5efb519f00075d958c3d1109ef6fcb24c487eb87`. Only the private clone's `tools/souji-landing-gate.py` was mutated. Each experiment contained one defect; the exact original bytes and both detectors were restored before the next experiment. No subagent dispatched, no lane source fixed, no real-fleet gate run, no network write, and no process signalled.

## Result table

`S` = `python3 .../tools/souji-landing-gate.py --selftest`; `F` = `python3 .../tests/fixtures/r18-landing-pointers.py --tool .../tools/souji-landing-gate.py`. Columns contain actual summary output and detector process exit codes, not the exit code of an individual gate case.

| Mutant | Smallest mutation, landed file:line | Expected discriminator | S output; rc; verdict | F output; rc; verdict | Pair verdict |
|---|---|---|---|---|---|
| M1 | `_pointer_paths`, `tools/souji-landing-gate.py:742`: `normalized = part`, bypassing source-relative `../` normalization | `relative-pointer-normalization` and `relative-pointer-escape` selftests, lines 1272–1290 | `SELFTEST pass=51 fail=2`; 1; killed | `SUMMARY total=11 failed=0`; 0; survived | **killed** |
| M2 | `evaluate`, line 973: `if round_no >= 18:` → `if True:` | `pointer-round-17-disabled` (1474–1478) and external `round-17-no-pointer-finding` (`tests/fixtures/r18-landing-pointers.py:275-280`) | `SELFTEST pass=51 fail=2`; 1; killed | `SUMMARY total=11 failed=1`; 1; killed | **killed** |
| M3 | `evaluate`, lines 991–999: delete the unused-exemption finding loop | `pointer-stale-exemptions`, selftest lines 1367–1378 | `SELFTEST pass=52 fail=1`; 1; killed | `SUMMARY total=11 failed=0`; 0; survived | **killed** |
| M4 | `_trim_pointer_token`, line 706: replace suffix regex with `r":\d+$"`, supporting a single line but not ranges/comma lists | External `lesson-line-suffix-resolves`, fixture lines 216–224 | `SELFTEST pass=53 fail=0`; 0; survived | `SUMMARY total=11 failed=1`; 1; killed | **killed** |
| M5 | `check_pointers`, lines 844–864: move the two-line tree-existence guard after the fleet-existence branch | A lane/fleet same-path collision must remain lane-resolved, not `fleet`; no such discriminator fired | `SELFTEST pass=53 fail=0`; 0; survived | `SUMMARY total=11 failed=0`; 0; survived | **survived** |
| M6 | `check_pointers`, lines 865–866: match exemption prefixes and mark matching exemption rows used | A cited exact exempt path plus a different prefix-sharing path must not exempt both; no such discriminator fired | `SELFTEST pass=53 fail=0`; 0; survived | `SUMMARY total=11 failed=0`; 0; survived | **survived** |

Combined detector pair: **4 killed / 2 survived / 0 inconclusive** after establishing the working sandbox. Selftest alone: 3 killed / 3 survived. External fixture alone: 2 killed / 4 survived. These are results for the six specified defects only, not a general coverage percentage.

# Findings and smallest fixes

## 1. Both detectors miss lane-before-fleet precedence (M5)

The pristine tree guard at `tools/souji-landing-gate.py:844-845` precedes the fleet classification at lines 849–864. Moving it after that branch survived both detectors. The current selftest creates only a fleet-only target (`tools/souji-landing-gate.py:1419-1428`) and asserts its JSON (`1430-1458`), so those assertions do not distinguish overlap from fleet-only existence. The external fixture's `Gate.run` interface (`tests/fixtures/r18-landing-pointers.py:116-125`) never supplies `--fleet-root`.

[INFERENCE from the mutant, not an additional executed scenario] If a cited path exists both in the committed lane tree and under the supplied fleet root, M5 increments `ptr_fleet` and emits a fleet classification for a lane-resolved path. Both existing controls still pass.

**Smallest fix:** add one same-path lane/fleet collision case to the selftest, assert no `fleet` item for that citation and `ptr_fleet == 0`, and preserve the existing fleet-only case. This is a proposed detector addition, not an implemented fix.

## 2. Both detectors miss prefix-widened exemptions (M6)

The pristine exact-membership check is `tools/souji-landing-gate.py:865-867`. The mutation was exactly:

```python
            if any(path.startswith(exempt) for exempt in exemptions):
                used_exemptions.update(exempt for exempt in exemptions if path.startswith(exempt))
```

The rest of the branch was unchanged. Attribution deliberately records the matched exemption row, so a stale-exemption side effect does not accidentally kill the prefix defect. Existing exemption controls exercise an exact match (`tools/souji-landing-gate.py:1355-1364`; `tests/fixtures/r18-landing-pointers.py:254-262`), not a competing prefix-sharing path.

[INFERENCE from the mutant, not an additional executed scenario] An exemption `corpus/runtime` also suppresses `corpus/runtime-extra` in M6 and is considered used. The committed exemption grammar need not change for this error.

**Smallest fix:** cite both `corpus/runtime` and `corpus/runtime-extra` with only the first path exempted; assert one `LG-DANGLING-PTR` for the second path and one exempt occurrence. This single case isolates exact-match semantics without depending on a stale-exemption finding. Not implemented here.

## 3. The two detectors are complementary, not interchangeable

M1 and M3 survive the external fixture while dying in selftest. M4 survives selftest while dying in the external fixture. The selftest's suffix case uses a single `:42` reference (`tools/souji-landing-gate.py:1318-1325`); the external fixture uses `:12-14` (`tests/fixtures/r18-landing-pointers.py:216-224`). The external historical assertion uses `minimum=True` (fixture lines 144–156, 305–306), so it can still pass despite M1 introducing additional wrong relative-path findings. Its synthetic exemption cases cover honor/malformed input, not stale rows (254–273).

**Smallest operational correction:** retain both existing commands as distinct evidence. To improve each detector independently, add relative/stale controls externally and a range-suffix control internally. The two combined-suite survivors above are the priority coverage findings.

# Exact execution and containment

Clone command, successful with no stdout/stderr:

```sh
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18w2-MutPointerGate/lane && git -C /var/tmp/souji-r18w2-MutPointerGate/lane checkout --quiet --detach 5efb519f00075d958c3d1109ef6fcb24c487eb87
```

Every valid detector invocation used the following exact prefix, followed by one of the two exact commands below. Working directory was `/var/tmp/souji-r18w2-MutPointerGate/lane`; each invocation had a **300-second tool deadline**. S and F ran concurrently against stable bytes; mutations did not overlap.

```sh
bwrap --die-with-parent --unshare-net --ro-bind / / --dev /dev --bind /var/tmp/souji-r18w2-MutPointerGate /var/tmp --bind /var/tmp/souji-r18w2-MutPointerGate /var/tmp/souji-r18w2-MutPointerGate --ro-bind /var/tmp/souji-r18w2-MutPointerGate/lane /home/vgpnk/Projects/shokunin/souji-shokunin --setenv HOME /nonexistent-fixture-home --setenv GIT_CONFIG_NOSYSTEM 1 --chdir /var/tmp/souji-r18w2-MutPointerGate/lane --

python3 /var/tmp/souji-r18w2-MutPointerGate/lane/tools/souji-landing-gate.py --selftest

python3 /var/tmp/souji-r18w2-MutPointerGate/lane/tests/fixtures/r18-landing-pointers.py --tool /var/tmp/souji-r18w2-MutPointerGate/lane/tools/souji-landing-gate.py
```

The first bind redirects hard-coded `/var/tmp` scratch creation into this seat's host directory; the second preserves the clone's absolute path. The final read-only bind maps the fixture's hard-coded historical `LANE` to the **private clone**, not the live repository. Neither detector's source/locator bytes were patched. Networking was unshared. Synthetic git writes and gate snapshot files therefore stayed in the private scratch area. The historical replay read `b576341` objects from the clone.

### Baseline infrastructure failure, excluded from mutant scoring

The initial two pristine attempts used the same prefix **without `--dev /dev`**. Both exited 1 before cases could run; the exact decisive error was:

```text
fatal: could not open '/dev/null' for reading and writing: Permission denied
```

The selftest raised `EvalError: selftest git init failed`; the fixture raised `RuntimeError: git init -q -b main failed`. These attempts are **inconclusive environment failures**, not killed mutants. Adding the device mount, without editing either detector, produced the passing pristine controls below; all scored mutated/restored runs used that corrected prefix.

## Pristine and restoration outputs

Each successful invocation exited 0. `R0` is the pristine baseline. `Rn` is the exact-byte restoration immediately after Mn and, for n < 6, the pristine control immediately before the next mutant.

| Stage | Actual S summary | Actual F summary | Gate SHA-256 |
|---|---|---|---|
| R0 | `SELFTEST\tpass=53\tfail=0` | `SUMMARY\ttotal=11\tfailed=0` | H0 |
| R1 | `SELFTEST\tpass=53\tfail=0` | `SUMMARY\ttotal=11\tfailed=0` | H0 |
| R2 | `SELFTEST\tpass=53\tfail=0` | `SUMMARY\ttotal=11\tfailed=0` | H0 |
| R3 | `SELFTEST\tpass=53\tfail=0` | `SUMMARY\ttotal=11\tfailed=0` | H0 |
| R4 | `SELFTEST\tpass=53\tfail=0` | `SUMMARY\ttotal=11\tfailed=0` | H0 |
| R5 | `SELFTEST\tpass=53\tfail=0` | `SUMMARY\ttotal=11\tfailed=0` | H0 |
| R6 | `SELFTEST\tpass=53\tfail=0` | `SUMMARY\ttotal=11\tfailed=0` | H0 |

## Actual failing case outputs

Pass-only output is summarized in the tables; these are all failing case lines from the six mutants, with original tab-separated fields preserved.

M1, S:

```text
CASE	FAIL	relative-pointer-normalization	exit=1 ids=['LG-DANGLING-PTR'] paths=['../census/round-18/missing.json'] fleet=[] err=None
CASE	FAIL	relative-pointer-escape	exit=1 ids=['LG-DANGLING-PTR'] paths=['../../census/round-18/missing.json'] fleet=[] err=None
SELFTEST	pass=51	fail=2
```

M2, S:

```text
CASE	FAIL	pointer-round-17-disabled	exit=1 ids=['LG-DANGLING-PTR'] paths=['census/round-17/missing.json'] fleet=[] err=None
CASE	FAIL	missing-cited-path	exit=1 ids=['LG-DANGLING-PTR', 'LG-MISSING-REG'] paths=['tools/gone.sh', 'tools/gone.sh'] fleet=[] err=None
SELFTEST	pass=51	fail=2
```

M2, F:

```text
CASE	FAIL	round-17-no-pointer-finding	exit=1 findings=Counter({('LG-DANGLING-PTR', 'census/round-18/x.json'): 1}) FAIL(exit=1 expected=0; findings=Counter({('LG-DANGLING-PTR', 'census/round-18/x.json'): 1}) expected=Counter())
SUMMARY	total=11	failed=1
```

M3, S:

```text
CASE	FAIL	pointer-stale-exemptions	exit=0 ids=[] paths=[] fleet=[] err=None
SELFTEST	pass=52	fail=1
```

M4, F:

```text
CASE	FAIL	lesson-line-suffix-resolves	exit=1 findings=Counter({('LG-DANGLING-PTR', 'census/round-18/source.md:12-14'): 1}) FAIL(exit=1 expected=0; findings=Counter({('LG-DANGLING-PTR', 'census/round-18/source.md:12-14'): 1}) expected=Counter())
SUMMARY	total=11	failed=1
```

# Hashes, restoration, and cleanup

The command `sha256sum /var/tmp/souji-r18w2-MutPointerGate/lane/tools/souji-landing-gate.py` was run at every mutated and restored stage. Every mutant's before/after hashes were H0; the intervening hashes differed as follows:

| Bytes | SHA-256 |
|---|---|
| H0: pristine and all six restorations | `f8a2ebe7695e600959ebfcd060ba99b6558a2f1149cbdcff8ad01a1467f2d27a` |
| M1 mutated | `ba6a2716c88d99f2675ee86fc87dfcdb29da86a79030c1e773b8f3a6c3bb9b14` |
| M2 mutated | `30f370c6775f92f5e1c6640f1c4e9cd5ed1aff054c137f7cfbbc1376f8fa92f0` |
| M3 mutated | `acbcdb54d8d51fad9e4228f1a40346202edfd748cd322df69e58b298351fdd64` |
| M4 mutated | `55be5f87365b46689a1214051668ba158e4327a54edaec75c103c3329c12a1b1` |
| M5 mutated | `ce9a1649fec5dbfcd2e896c59b8cbc0cd81a628fe241e81ad1d83402d31c5691` |
| M6 mutated | `e91d197fd501a549e11e5143feeded04d1a6bf13502ad00996b8b16b79456f18` |
| External fixture, initial and final, never edited | `66b503aa0f0f8692ceb3054486d869c1c1fa9ae638a64d5bbe3b1630a76b47ed` |

Restoration used inverse surgical edits, including reinsertion of the exact captured stale-finding block and relocation of the original two-line tree guard. Final two-file `sha256sum` output:

```text
f8a2ebe7695e600959ebfcd060ba99b6558a2f1149cbdcff8ad01a1467f2d27a  /var/tmp/souji-r18w2-MutPointerGate/lane/tools/souji-landing-gate.py
66b503aa0f0f8692ceb3054486d869c1c1fa9ae638a64d5bbe3b1630a76b47ed  /var/tmp/souji-r18w2-MutPointerGate/lane/tests/fixtures/r18-landing-pointers.py
```

Cleanup command, exit 0:

```sh
rm -rf -- /var/tmp/souji-r18w2-MutPointerGate && test ! -e /var/tmp/souji-r18w2-MutPointerGate && printf 'CLEANUP\t/var/tmp/souji-r18w2-MutPointerGate\tabsent\n'
```

Actual output:

```text
CLEANUP	/var/tmp/souji-r18w2-MutPointerGate	absent
```

Tools already installed: bubblewrap 0.13.1, Python 3.14.8, git 2.56.0. **No tool installed or updated.** No pacman transaction or service restart.

## Scoped verdict

**Partial detector sensitivity:** the pair catches normalization removal, round-gate removal, stale-finding removal, and the single-line-only suffix regression. It misses fleet-before-tree classification and prefix-widened exemptions. The smallest corrective action is the two focused test additions above, not a change to the pointer contract. All assigned probes are complete; original bytes were restored and the isolated checkout removed. No landed source change is proposed as a demonstrated bug fix.
