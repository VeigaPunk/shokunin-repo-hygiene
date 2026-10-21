# MutateRepeatedRead — round-20 final falsification

Verdict: **KILLED**. Removing only the differing-repeated-read refusal caused the required `receipt-spec-transcript-alias` case to fail. The complete detector passed on pristine and exact restored bytes. This is a bounded mutation-calibration result, not certification, integration, or promotion.

## Axes and scope

- Detector discrimination: the named alias case must distinguish the specified mutant from the pinned source.
- Isolation and mutation fidelity: one two-line behavioral deletion in this seat's independent clone; fixture, expected values, and baseline auditor unchanged.
- Restoration fidelity: restore the saved source exactly and assert SHA-256 equality before the third identical detector run.

Scratch: `/var/tmp/souji-r20w2-MutateRepeatedRead`.
Clone: `/var/tmp/souji-r20w2-MutateRepeatedRead/lane`.
Branch: `souji-r20-MutateRepeatedRead`.
Observed branch commit: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`.
Preregistered old-auditor commit: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`.

## Isolation and pinned inputs

The following setup command exited 0. Its leading checks required scratch not to exist (including a dangling symlink), and only then created the private clone and branch:

```sh
test ! -e /var/tmp/souji-r20w2-MutateRepeatedRead && test ! -L /var/tmp/souji-r20w2-MutateRepeatedRead && mkdir /var/tmp/souji-r20w2-MutateRepeatedRead && git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r20w2-MutateRepeatedRead/lane && git -C /var/tmp/souji-r20w2-MutateRepeatedRead/lane switch --quiet -c souji-r20-MutateRepeatedRead 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1 && git -C /var/tmp/souji-r20w2-MutateRepeatedRead/lane rev-parse souji-r20-MutateRepeatedRead
```

Exact stdout:

```text
1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1
```

Both read-only extraction commands were executed with captured stdout and exited 0, with empty stderr:

```sh
git -C /var/tmp/souji-r20w2-MutateRepeatedRead/lane show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:tools/souji-seat-audit.py
git -C /var/tmp/souji-r20w2-MutateRepeatedRead/lane show 12516f7dcdd5b165e5ee208d44a38d63b5bd5812:tools/souji-seat-audit.py
```

The write tool saved their exact UTF-8-round-tripped bytes as `/var/tmp/souji-r20w2-MutateRepeatedRead/pristine-souji-seat-audit.py` (40,856 bytes) and `/var/tmp/souji-r20w2-MutateRepeatedRead/baseline-auditor.py` (31,746 bytes). Initial `sha256sum` confirmed the clone's auditor matched the saved pristine source before any mutation. No network extraction or package installation was used.

## Mutant and expected detector

At pinned `tools/souji-seat-audit.py:379-380`, the surgical edit removed exactly:

```python
        if key in input_bytes and input_bytes[key] != data:
            raise ValueError("audit input changed during repeated read: %s" % path)
```

It retained `input_bytes[key] = data`, the return, the nonregular-input refusal, and all final read-window checks.

Expected detector: `receipt-spec-transcript-alias` in `tests/fixtures/r20-audit-contract.py:442-474`. The fixture makes the spec and transcript use the same resolved pathname, supplies spec JSON on its first read and transcript bytes on subsequent reads, and requires the repeated-read refusal on read two. Without the guard, the map assignment can overwrite the earlier consumed bytes and the final check can match only the later bytes. This explanation is source-derived; the observed discrimination is recorded below.

## Three complete detector runs

Working directory for each run: `/var/tmp/souji-r20w2-MutateRepeatedRead/lane`.
The exact same command was executed once in each state, without filtering or modifying the fixture:

```sh
python3 -B tests/fixtures/r20-audit-contract.py --tool tools/souji-seat-audit.py --base-tool /var/tmp/souji-r20w2-MutateRepeatedRead/baseline-auditor.py
```

| State | Actual exit | Exact stdout summary | Named alias case |
| --- | ---: | --- | --- |
| Pristine | 0 | `SUMMARY\ttotal=50\tpass=50\tfail=0\tbase_discriminating=11` | PASS |
| Mutated | 1 | `SUMMARY\ttotal=50\tpass=49\tfail=1\tbase_discriminating=11` | FAIL; sole failing case |
| Restored | 0 | `SUMMARY\ttotal=50\tpass=50\tfail=0\tbase_discriminating=11` | PASS |

The `\t` notation in the table denotes the literal tab separators printed by the fixture. Exact relevant output lines, with literal tabs:

Pristine:

```text
CASE	PASS	receipt-spec-transcript-alias	same_path=True reads=2 refused=True
CASE	PASS	oracle-exact-case-inventory	missing=[] extra=[]
SUMMARY	total=50	pass=50	fail=0	base_discriminating=11
```

Mutated:

```text
CASE	FAIL	receipt-spec-transcript-alias	same_path=True reads=3 refused=False
CASE	PASS	oracle-exact-case-inventory	missing=[] extra=[]
SUMMARY	total=50	pass=49	fail=1	base_discriminating=11
```

Restored:

```text
CASE	PASS	receipt-spec-transcript-alias	same_path=True reads=2 refused=True
CASE	PASS	oracle-exact-case-inventory	missing=[] extra=[]
SUMMARY	total=50	pass=50	fail=0	base_discriminating=11
```

All other cases printed PASS on all three runs, including the four ordinary drift cases and `drift-auditor-after-import`. All three runs reproduced the eleven preregistered old-auditor overauthorization observations. Those old-auditor observations are intentionally passing discrimination checks, not a failed pristine detector. The mutant's observed third alias read and missing refusal demonstrate effective execution of the changed behavior; the verdict does not rely solely on a changed file hash.

## Digests and exact restoration

Observed SHA-256 values:

| Bytes | SHA-256 |
| --- | --- |
| Pristine clone auditor and saved pristine copy | `a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636` |
| Mutated clone auditor | `f60be236e841f783804222b9a13400e921ae92377fbd188ade670fb053c0e00c` |
| Restored clone auditor | `a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636` |
| Unchanged complete fixture | `58a17169b72bb6b781b08d2f63426220234f383466d1a74ca5c982e1f2a5a434` |
| Unchanged extracted old auditor | `62522acc350c23513f63d855231f82a9a6209b28b61535fb346e83cdf54e02e6` |

The pristine and mutant hash commands exited 0:

```sh
sha256sum tools/souji-seat-audit.py tests/fixtures/r20-audit-contract.py /var/tmp/souji-r20w2-MutateRepeatedRead/pristine-souji-seat-audit.py /var/tmp/souji-r20w2-MutateRepeatedRead/baseline-auditor.py
sha256sum tools/souji-seat-audit.py tests/fixtures/r20-audit-contract.py /var/tmp/souji-r20w2-MutateRepeatedRead/baseline-auditor.py
```

After the mutant's exit 1, the write tool replaced only the private clone auditor with the saved pristine content. The following restoration commands exited 0:

```sh
sha256sum /var/tmp/souji-r20w2-MutateRepeatedRead/lane/tools/souji-seat-audit.py /var/tmp/souji-r20w2-MutateRepeatedRead/pristine-souji-seat-audit.py /var/tmp/souji-r20w2-MutateRepeatedRead/lane/tests/fixtures/r20-audit-contract.py /var/tmp/souji-r20w2-MutateRepeatedRead/baseline-auditor.py
cmp -- /var/tmp/souji-r20w2-MutateRepeatedRead/lane/tools/souji-seat-audit.py /var/tmp/souji-r20w2-MutateRepeatedRead/pristine-souji-seat-audit.py
```

The captured restored digest was explicitly asserted equal to the saved pristine-byte digest. Actual assertion output:

```text
ASSERT restored_sha256 == pristine_sha256: PASS a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636
```

`cmp` produced empty stdout and stderr, establishing byte-for-byte equality in addition to digest equality. The restored detector run then passed all 50 cases.

No production source, sibling artifact, expected value, or fixture was edited. No other tests, transcript commands, process census, signals, agents, installs, or host configuration changes were run. Only this advisory report was written in the production lane. No unresolved defect was found by this assigned probe; the result is limited to this one mutant and this complete detector.

## Process limit: late clone neutralization instruction

The instruction to neutralize child Git system/global configuration, prompts, optional locks, lazy fetch, maintenance, hooks, and fsmonitor arrived after the clone, branch creation, three detector runs, exact restoration, and original report were complete. Those neutralizations were **not applied** to the outer clone/branch commands. Their exact actual command evidence above is retained; there is no retroactive sanitized-environment claim. No global configuration was inspected, and no clone, detector, or other probe was rerun after the late instruction. This is a process limit on the outer Git setup; the observed branch, source digests, detector results, and exact restoration evidence remain as recorded. Main was notified.

Report: .ufo/waves/round-20/final/MutateRepeatedRead.md
