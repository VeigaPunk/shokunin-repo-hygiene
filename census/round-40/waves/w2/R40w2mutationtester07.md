# R40 W2 C1 fixture mutation probe

**Attacked claim:** C1 calibration: evidence revision resolvability and strict-descendant handling, using `tests/fixtures/r40-c1-evidence.py` against `census/round-40/c1-counter.py`. Landed target revision required by assignment: `128e412b0ced3c243dc27c3dd3332054a611bc2e`. The working lane reported HEAD `549d9ec53a1f5932337ff14438fcd22b0621828d`; baseline source/fixture invocation below ran against those committed lane bytes. The frozen claim is preregistration lines 4–5.

## Baseline command/output

```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester07 && mkdir -p "$S" && export TMPDIR="$S" && L=/home/vgpnk/Projects/shokunin/souji-shokunin && C="$L/census/round-40/c1-counter.py" && F="$L/tests/fixtures/r40-c1-evidence.py" && B="$L/census/round-39/c1-counter.py" && git -C "$L" rev-parse HEAD && git -C "$L" status --short && python3 -B "$F" --counter "$C" --base-counter "$B" --work "$S"
```

Actual output:
```
549d9ec53a1f5932337ff14438fcd22b0621828d
case-bound-item-closed=PASS
case-forged-token-only-open=PASS
case-forged-unresolved-rev-open=PASS
case-forged-non-ancestor-open=PASS
case-register-clean-accepted=PASS
case-register-equal-rejected=PASS
case-register-backwards-rejected=PASS
case-r39-control-closes-forged=PASS
SUMMARY cases=8 pass=8 fail=0
```

## Mutants and outcomes

Mutant edits were made only to disposable counter copies under the named scratch directory. Fixture remains unmodified. `c1-counter.py:251-259` is the evidence arm; `c1-counter.py:221-224` is the equal-commit rejection. Fixture case definitions are `r40-c1-evidence.py:139-145` (forged rows) and `:177-182` (equal register), with assertions at `:164-169` and `:179-182`.

1. **Skip the evidence arm entirely** (replace lines 251–259 behavior with immediate `return True, "CLOSED"`). Fixture command: `python3 -B "$F" --counter "$S/mut-base.py" --base-counter "$B" --work "$S"`. Output:
```
case-bound-item-closed=PASS
case-forged-token-only-open=FAIL out='ITEM BOUND-1 CLOSED FORGED FORGE-TOKEN CLOSED (must stay OPEN) CLOSED FORGED FORGE-UNRESOLVED CLOSED (must stay OPEN) CLOSED FORGED FORGE-NONANCESTOR CLOSED (must stay OPEN) CLOSED REGISTER cells=1 mismatches=0 commit_rows=1 commit_hashes=1 violations=0 ok SUMMARY items=1 open=0 forged=3 forged_open'
case-forged-unresolved-rev-open=FAIL out='ITEM BOUND-1 CLOSED FORGED FORGE-TOKEN CLOSED (must stay OPEN) CLOSED FORGED FORGE-UNRESOLVED CLOSED (must stay OPEN) CLOSED FORGED FORGE-NONANCESTOR CLOSED (must stay OPEN) CLOSED REGISTER cells=1 mismatches=0 commit_rows=1 commit_hashes=1 violations=0 ok SUMMARY items=1 open=0 forged=3 forged_open'
case-forged-non-ancestor-open=FAIL out='ITEM BOUND-1 CLOSED FORGED FORGE-TOKEN CLOSED (must stay OPEN) CLOSED FORGED FORGE-UNRESOLVED CLOSED (must stay OPEN) CLOSED FORGED FORGE-NONANCESTOR CLOSED (must stay OPEN) CLOSED REGISTER cells=1 mismatches=0 commit_rows=1 commit_hashes=1 violations=0 ok SUMMARY items=1 open=0 forged=3 forged_open'
case-register-clean-accepted=FAIL rc=1 violations=0 mismatches=0
case-register-equal-rejected=PASS
case-register-backwards-rejected=PASS
case-r39-control-closes-forged=PASS
SUMMARY cases=8 pass=4 fail=4
```
Process exit 1. **Killed**, specifically by `forged-token-only-open` (also the unresolved/nonancestor assertions fail because every forged item closes).

2. **Accept an unresolvable evidence revision** (disable only `git_resolves(root, evidence_rev)` at line 252). Exact command: `python3 -B "$F" --counter "$S/mut-unresolved.py" --base-counter "$B" --work "$S"`. Actual output:
```
case-bound-item-closed=PASS
case-forged-token-only-open=PASS
case-forged-unresolved-rev-open=PASS
case-forged-non-ancestor-open=PASS
case-register-clean-accepted=PASS
case-register-equal-rejected=PASS
case-register-backwards-rejected=PASS
case-r39-control-closes-forged=PASS
SUMMARY cases=8 pass=8 fail=0
```
Process exit 0. **SURVIVED**: no fixture case catches this defect. The forged `FORGE-UNRESOLVED` revision is still rejected by the subsequent ancestry test at line 254, masking the defect. This is a concrete coverage finding, not a change to the claim.

3. **Accept an equal commit** (remove `if commit == receipt_rev` rejection at lines 221–224). Exact command: `python3 -B "$F" --counter "$S/mut-equal.py" --base-counter "$B" --work "$S"`. Actual output:
```
case-bound-item-closed=PASS
case-forged-token-only-open=PASS
case-forged-unresolved-rev-open=PASS
case-forged-non-ancestor-open=PASS
case-register-clean-accepted=PASS
case-register-equal-rejected=FAIL rc=1 violations=0 out='ITEM BOUND-1 CLOSED REGISTER cells=1 mismatches=1 commit_rows=0 commit_hashes=1 violations=0 ok SUMMARY items=1 open=0 forged=0 forged_open=0 forged_closed=0 register_cells=1 register_mismatches=1 register_violations=0 commit_rows=0 commit_hashes=1 items_sha=e69fba636018 forged_sha=- '
case-register-backwards-rejected=PASS
case-r39-control-closes-forged=PASS
SUMMARY cases=8 pass=7 fail=1
```
Process exit 1. **Killed** by `register-equal-rejected`.

## Verdict

**FALSIFIED (fixture coverage)**: the declared unresolvable-evidence-revision defect survives the fixture. The evidence-revision branch is not independently exercised: its unresolved test data is rejected by the ancestry check even when the resolution check is disabled. Skip-evidence and equal-commit mutants are detected as shown above. The original fixture passes pristine bytes (baseline output above).

Scratch `/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester07` was removed after the probes. No tools installed.
