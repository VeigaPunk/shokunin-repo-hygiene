# MutateArgProvenance — bounded mutation probe

**Verdict: KILLED.** The pristine and restored integrated source each passed the same 27-case reason canary; the assigned one-line mutant failed exactly `token-equals`, `token-next`, and `password-equals`, leaking their fabricated canary. This is advisory evidence for this detector's sensitivity to argv-provenance loss, not certification of C3 or the integrated build.

## Axes and frozen oracle

- **Coverage:** detect loss of the secret-bearing argv provenance bit after path extraction (C3 r2).
- **Harm guards:** preserve the same detector and baseline bytes; execute only synthetic `--reason-only` tool calls; restore the scratch source byte-for-byte; do not change production or siblings.
- Read the frozen preregistration and pre-measurement clarification at their named absolute paths before measurement. C3 requires the selected secret-bearing argv path to emit `argv-path-gone:[REDACTED]`, even when extraction removes the secret marker.
- Observed clone base: `522dcd768ca90afe166532d37d306d3df70aeea5`; branch: `r21/MutateArgProvenance`.

## Setup commands and exits

Exclusive creation, cwd `/var/tmp`, exit **0**:

```text
mkdir -- /var/tmp/souji-r21-MutateArgProvenance
```

Clone, cwd `/var/tmp/souji-r21-MutateArgProvenance`, exit **0**:

```text
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r21-MutateArgProvenance/lane
```

All subsequent command executions used cwd `/var/tmp/souji-r21-MutateArgProvenance/lane`.

```text
git -C /var/tmp/souji-r21-MutateArgProvenance/lane switch -c r21/MutateArgProvenance 522dcd768ca90afe166532d37d306d3df70aeea5 && git -C /var/tmp/souji-r21-MutateArgProvenance/lane rev-parse HEAD
```

Exit **0**, literal output:

```text
Switched to a new branch 'r21/MutateArgProvenance'
522dcd768ca90afe166532d37d306d3df70aeea5
```

The fixture requires exact historical function bodies. This subprocess command exited **0** with empty stderr:

```text
git -C /var/tmp/souji-r21-MutateArgProvenance/lane show 6ff3413bba9c8430c3b0bc4d2052e21d0407183f:tools/souji-proc-census.sh
```

Its captured UTF-8 stdout was written through the Eval `write` helper to `/var/tmp/souji-r21-MutateArgProvenance/base-proc-census.sh` (24,706 bytes). The historical file was only used as the canary's extraction input; it was not executed as a census.

## Mutant and expected detector

Only `/var/tmp/souji-r21-MutateArgProvenance/lane/tools/souji-proc-census.sh:278` was edited. The selected path's provenance assignment in `read_argv_stream()` was replaced with zero. `format_reason()` therefore receives a false secret bit; for the three provenance cases the extracted path no longer contains `--token`, `--password`, or another secret-pattern marker, so path-text regex redaction cannot recover the lost classification.

Expected detector: the unchanged `/var/tmp/souji-r21-MutateArgProvenance/lane/tests/fixtures/r21-reason-canary.sh` must fail at least `token-equals`, `token-next`, and `password-equals` under the mutant, with pristine and restored bytes passing.

Exact diff command, exit **0**:

```text
git -C /var/tmp/souji-r21-MutateArgProvenance/lane diff 522dcd768ca90afe166532d37d306d3df70aeea5 -- /var/tmp/souji-r21-MutateArgProvenance/lane/tools/souji-proc-census.sh
```

Literal diff:

```diff
diff --git c/tools/souji-proc-census.sh w/tools/souji-proc-census.sh
index a1bddfe..d01c790 100755
--- c/tools/souji-proc-census.sh
+++ w/tools/souji-proc-census.sh
@@ -275,7 +275,7 @@ read_argv_stream() {
       for prefix in "${PREFIXES[@]}"; do
         if top_level_scratch_gone "$candidate" "$prefix"; then
           PROC_GONE_PATH=$candidate
-          PROC_GONE_SECRET=$secret
+          PROC_GONE_SECRET=0
           break
         fi
       done
```

## Same detector: pristine / mutated / restored

The detector command was identical in all three phases:

```text
bash /var/tmp/souji-r21-MutateArgProvenance/lane/tests/fixtures/r21-reason-canary.sh --tool /var/tmp/souji-r21-MutateArgProvenance/lane/tools/souji-proc-census.sh --base /var/tmp/souji-r21-MutateArgProvenance/base-proc-census.sh
```

The pristine command was executed after the three-file `sha256sum` command below in one `&&` chain; that chain exited **0**. Mutated and restored detector exits were captured directly as **1** and **0**, respectively.

| Source phase | Detector exit | Literal summary |
| --- | ---: | --- |
| Pristine integrated source | 0 | `SUMMARY\ttotal=27\tpass=27\tfail=0\tleaks=0\tbase_leaks=19\tmax_reason_bytes=160` |
| Assigned mutant | 1 | `SUMMARY\ttotal=27\tpass=24\tfail=3\tleaks=3\tbase_leaks=19\tmax_reason_bytes=160` |
| Restored source | 0 | `SUMMARY\ttotal=27\tpass=27\tfail=0\tleaks=0\tbase_leaks=19\tmax_reason_bytes=160` |

In the table, `\t` represents the literal tab separators. Raw summary lines, in phase order:

```text
SUMMARY	total=27	pass=27	fail=0	leaks=0	base_leaks=19	max_reason_bytes=160
SUMMARY	total=27	pass=24	fail=3	leaks=3	base_leaks=19	max_reason_bytes=160
SUMMARY	total=27	pass=27	fail=0	leaks=0	base_leaks=19	max_reason_bytes=160
```

Literal mutant failure output (the fixture's generated prefix is synthetic):

```text
CASE	FAIL	token-equals	exit=0	leak=1	base_leak=1	bytes=71
DETAIL b'argv-path-gone:/var/tmp/souji-r21-canary-5c4fa56f5651/SOUJIR21FAKE80123\n' b''
CASE	FAIL	token-next	exit=0	leak=1	base_leak=1	bytes=71
DETAIL b'argv-path-gone:/var/tmp/souji-r21-canary-5c4fa56f5651/SOUJIR21FAKE80123\n' b''
CASE	FAIL	password-equals	exit=0	leak=1	base_leak=1	bytes=71
DETAIL b'argv-path-gone:/var/tmp/souji-r21-canary-5c4fa56f5651/SOUJIR21FAKE80123\n' b''
```

The other 24 mutant cases passed. The three failures were leaks/mismatched required redaction, not tool crashes: each tool invocation returned 0 and emitted the raw fabricated value. The whole-reason 160-byte guard still held. Both pristine and restored runs showed all three provenance cases passing with `leak=0` and `bytes=25`.

## Hashes and restoration evidence

Before mutation and after restoration, the following identical command exited **0**:

```text
sha256sum /var/tmp/souji-r21-MutateArgProvenance/lane/tools/souji-proc-census.sh /var/tmp/souji-r21-MutateArgProvenance/lane/tests/fixtures/r21-reason-canary.sh /var/tmp/souji-r21-MutateArgProvenance/base-proc-census.sh
```

Literal output in both phases:

```text
3bc403440d67e2e8a096f52e3953cfb32a5a415c8e032d91d386c95f792fafb5  /var/tmp/souji-r21-MutateArgProvenance/lane/tools/souji-proc-census.sh
46a60e32c86301c8a4bb70bc83a04591749c6466c33cc5ef112a4f5d885add39  /var/tmp/souji-r21-MutateArgProvenance/lane/tests/fixtures/r21-reason-canary.sh
37c3316a1fd8cdda18cbefdc7692d3d3f388e5783e8fe19085f5d932a8ceba64  /var/tmp/souji-r21-MutateArgProvenance/base-proc-census.sh
```

During mutation, this command exited **0**:

```text
sha256sum /var/tmp/souji-r21-MutateArgProvenance/lane/tools/souji-proc-census.sh
```

Literal output:

```text
3e2ea0ad1e6be1451e5feb68a929edf464e2f66c7bce89bc66a6a2239821b9d3  /var/tmp/souji-r21-MutateArgProvenance/lane/tools/souji-proc-census.sh
```

Restoration replaced only the assigned scratch line with its original `PROC_GONE_SECRET=$secret` bytes using the edit tool. The restored source SHA-256 equals the pristine SHA-256; fixture and historical baseline hashes are also unchanged. The restored detector returned to 27/27 passing.

No production source or sibling was edited; no patch is delivered. No live `/proc` content, credentials, historical census snapshots, operator-owned directory, selftest, or process signals were used. The canary invokes the proc tool only through `--reason-only` with synthetic stdin. No tool was installed or upgraded. The bounded assigned probe is complete.
