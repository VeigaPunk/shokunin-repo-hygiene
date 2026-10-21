# MutateDirectivePrefix — round-20 final falsification

## Result

**KILLED.** The single assigned prefix-match mutant newly accepted a trailing denial, and the unchanged independent oracle rejected it through exactly `deliver-denial-trailing-text`. The identical complete fixture exited **0 / 1 / 0** on pristine / mutant / exactly restored auditor bytes. No unresolved defect was found by this bounded probe.

Axes: detector discrimination; exact grant parsing; unchanged oracle; byte-exact restoration; isolated execution. This is author-side advisory mutation evidence only, not non-author closure, certification, integration, or promotion.

## Isolation and pins

- Private scratch: `/var/tmp/souji-r20w2-MutateDirectivePrefix`.
- Independent clone: `/var/tmp/souji-r20w2-MutateDirectivePrefix/lane`.
- Unique branch: `souji-r20-MutateDirectivePrefix`.
- Observed branch commit: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`.
- Preregistered comparison auditor: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812:tools/souji-seat-audit.py`, saved as `/var/tmp/souji-r20w2-MutateDirectivePrefix/baseline-auditor.py`.
- Pristine committed bytes were saved before mutation as `/var/tmp/souji-r20w2-MutateDirectivePrefix/pristine-auditor.py`.
- No production source mutation, sibling artifact, source-wide search, transcript-command execution, process census, signals, package installation, configuration change, or additional test was performed. The sole lane write is this assigned report. The independent clone and snapshots are retained; no cleanup or deletion command was issued by this seat.

## Mutant and expected detector

Only `tools/souji-seat-audit.py:146`, inside `delivery_paths`, changed:

```diff
-        match = re.fullmatch(
+        match = re.match(
```

The remaining regex, parser logic, fixture, expectations, and baseline auditor were unchanged. The oracle's case at `tests/fixtures/r20-audit-contract.py:163-165` supplies a directive shaped as:

```text
DELIVER: <this synthetic seat's exact .patch path> is not authorized
```

Its expected result is `[('V-WRITE-SCOPE', 'major')]`. Prefix matching newly treats the path prefix as a positive grant despite the trailing denial. The detector must fail the named case rather than silently accepting this behavior.

## Actual detector command and outputs

Working directory for all three invocations:

```text
/var/tmp/souji-r20w2-MutateDirectivePrefix/lane
```

The exact command was identical in all three states:

```sh
python3 -B tests/fixtures/r20-audit-contract.py --tool tools/souji-seat-audit.py --base-tool /var/tmp/souji-r20w2-MutateDirectivePrefix/baseline-auditor.py
```

| State | Actual exit | Actual stdout summary |
| --- | ---: | --- |
| Pristine | 0 | `SUMMARY\ttotal=50\tpass=50\tfail=0\tbase_discriminating=11` |
| Mutant | 1 | `SUMMARY\ttotal=50\tpass=49\tfail=1\tbase_discriminating=11` |
| Restored | 0 | `SUMMARY\ttotal=50\tpass=50\tfail=0\tbase_discriminating=11` |

Exact discriminating stdout lines (tab separators preserved):

```text
Pristine:
CASE	PASS	deliver-denial-trailing-text	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]

Mutant:
CASE	FAIL	deliver-denial-trailing-text	violations=[] expected=[('V-WRITE-SCOPE', 'major')]

Restored:
CASE	PASS	deliver-denial-trailing-text	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
```

The mutated run had no other failing case. In all three runs, `oracle-exact-case-inventory` passed with `missing=[] extra=[]`; the comparison auditor reproduced all eleven specified broad-authorization cases. Thus the pristine detector was not already failing, and the mutation was behaviorally effective rather than merely a text edit. The mutant's `violations=[]` is direct evidence that the trailing denial became accepted.

## Digests and restoration evidence

All values below were actually obtained from the committed-byte extraction or `sha256sum` commands.

| Input/state | SHA-256 |
| --- | --- |
| Selected auditor, pristine | `a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636` |
| Saved pristine auditor, before mutation | `a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636` |
| Selected auditor, mutant | `226f59b7640264691baaf238fb952ded25d848742c9b5a24197fbd9dc48d53dc` |
| Selected auditor, restored | `a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636` |
| Saved pristine auditor, restoration check | `a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636` |
| Fixture, pristine / mutant / restored | `58a17169b72bb6b781b08d2f63426220234f383466d1a74ca5c982e1f2a5a434` |
| Comparison auditor, saved / mutant / restored | `62522acc350c23513f63d855231f82a9a6209b28b61535fb346e83cdf54e02e6` |

The inverse surgical edit restored `re.fullmatch` immediately after the mutated run. The SHA assertion below exited 0 and printed `tools/souji-seat-audit.py: OK`; the chained byte-for-byte `cmp --silent` also exited 0. The restored detector then passed all fifty cases. Restoration did not depend on the detector succeeding.

## Executed setup, extraction, and digest commands

### Scratch existence guard, clone, branch, and commit observation

Executed from `/var/tmp`, exit 0:

```sh
test ! -e /var/tmp/souji-r20w2-MutateDirectivePrefix && mkdir /var/tmp/souji-r20w2-MutateDirectivePrefix && git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r20w2-MutateDirectivePrefix/lane && git -C /var/tmp/souji-r20w2-MutateDirectivePrefix/lane switch --quiet -c souji-r20-MutateDirectivePrefix 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1 && git -C /var/tmp/souji-r20w2-MutateDirectivePrefix/lane rev-parse souji-r20-MutateDirectivePrefix
```

Stdout:

```text
1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1
```

The existence guard succeeded; the scratch was not reused.

### Read-only committed-byte extractions

Executed with the private clone as working directory:

```sh
git -C /var/tmp/souji-r20w2-MutateDirectivePrefix/lane show 12516f7dcdd5b165e5ee208d44a38d63b5bd5812:tools/souji-seat-audit.py
git -C /var/tmp/souji-r20w2-MutateDirectivePrefix/lane show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:tools/souji-seat-audit.py
```

Both extraction exits were 0. The baseline command was invoked first for inspection and again to capture exact bytes for its named snapshot; the pinned command captured the pristine snapshot. Captured stdout sizes were respectively 31,746 and 40,856 bytes; captured stderr was empty. An evaluator orchestration cell asserted UTF-8 round-trip identity, computed the hashes above, and passed the captured text to the specialized `write` tool. The write tool confirmed those same byte counts. No shell redirection or Python file-edit operation was used.

### Initial selected-source digests

Executed in the private clone, exit 0:

```sh
sha256sum tools/souji-seat-audit.py tests/fixtures/r20-audit-contract.py
```

Stdout was the pristine auditor and fixture hashes tabulated above.

### Saved-snapshot digests

Executed in the private clone before mutation, exit 0:

```sh
sha256sum /var/tmp/souji-r20w2-MutateDirectivePrefix/baseline-auditor.py /var/tmp/souji-r20w2-MutateDirectivePrefix/pristine-auditor.py
```

Stdout was the comparison and saved-pristine hashes tabulated above.

### Mutated digests

Executed in the private clone after the one-line mutation, exit 0:

```sh
sha256sum tools/souji-seat-audit.py tests/fixtures/r20-audit-contract.py /var/tmp/souji-r20w2-MutateDirectivePrefix/baseline-auditor.py
```

Stdout was the mutant auditor hash plus the unchanged fixture and comparison-auditor hashes tabulated above.

### Exact restoration assertion and digests

Executed in the private clone after the inverse one-line edit, exit 0:

```sh
printf '%s  %s\n' a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636 tools/souji-seat-audit.py | sha256sum --check && cmp --silent tools/souji-seat-audit.py /var/tmp/souji-r20w2-MutateDirectivePrefix/pristine-auditor.py && sha256sum tools/souji-seat-audit.py tests/fixtures/r20-audit-contract.py /var/tmp/souji-r20w2-MutateDirectivePrefix/baseline-auditor.py /var/tmp/souji-r20w2-MutateDirectivePrefix/pristine-auditor.py
```

Actual stdout:

```text
tools/souji-seat-audit.py: OK
a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636  tools/souji-seat-audit.py
58a17169b72bb6b781b08d2f63426220234f383466d1a74ca5c982e1f2a5a434  tests/fixtures/r20-audit-contract.py
62522acc350c23513f63d855231f82a9a6209b28b61535fb346e83cdf54e02e6  /var/tmp/souji-r20w2-MutateDirectivePrefix/baseline-auditor.py
a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636  /var/tmp/souji-r20w2-MutateDirectivePrefix/pristine-auditor.py
```

## Late-arriving setup limitation

After the three detector executions, exact restoration, and initial report write had completed, the coordinator instructed that outer Git clone/checkout commands use child-only `GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_OPTIONAL_LOCKS=0 GIT_NO_LAZY_FETCH=1` and Git options `-c maintenance.auto=false -c core.hooksPath=/dev/null -c core.fsmonitor=false`. The actual earlier clone/switch commands above did not include these newly specified neutralizations. Global configuration was not inspected, so this probe does not establish that operator hooks or automatic maintenance were disabled. The late instruction cannot be applied retroactively; no additional clone, checkout, or detector execution was performed. The behavioral outputs and restoration evidence above remain the observed results; compliance with the late setup-neutralization requirement is not claimed.

Tools installed or updated: none.

Report: .ufo/waves/round-20/final/MutateDirectivePrefix.md
