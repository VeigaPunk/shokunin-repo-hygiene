# MutateReasonMask — bounded C3 mutation probe

## Verdict and axes

**KILLED.** The unchanged synthetic detector passed on pristine bytes, failed on the assigned formatter mutant, and passed again after exact source-byte restoration. This is evidence that this detector catches this particular regression, not certification of C3 or an integration/closure decision.

Axes: secret-pattern/provenance leak detection; 160-byte reason bound; control-byte/non-secret compatibility; isolated, reversible execution. No contract or detector changes were made.

Frozen oracle read first: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-21/preregistration.txt`, especially C3 lines 21–25. Also read `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-21/clarification-before-measurement.txt`. This probe did not perform corpus work.

## Isolation and observed revision

Exclusive scratch: `/var/tmp/souji-r21-MutateReasonMask`.
Clone: `/var/tmp/souji-r21-MutateReasonMask/lane`.
Branch: `r21/MutateReasonMask`.
Observed HEAD: `522dcd768ca90afe166532d37d306d3df70aeea5`.
All detector, hash, baseline-extraction, and diff commands used cwd `/var/tmp/souji-r21-MutateReasonMask/lane`.

Provisioning command (exit 0):

```sh
mkdir /var/tmp/souji-r21-MutateReasonMask && git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r21-MutateReasonMask/lane && git -C /var/tmp/souji-r21-MutateReasonMask/lane switch -c r21/MutateReasonMask 522dcd768ca90afe166532d37d306d3df70aeea5 && git -C /var/tmp/souji-r21-MutateReasonMask/lane rev-parse HEAD
```

Literal output:

```text
Switched to a new branch 'r21/MutateReasonMask'
522dcd768ca90afe166532d37d306d3df70aeea5
```

Baseline-extraction command (exit 0; invoked with subprocess, stdout written unchanged by the write tool to `/var/tmp/souji-r21-MutateReasonMask/base-6ff3413-souji-proc-census.sh`):

```sh
git -C /var/tmp/souji-r21-MutateReasonMask/lane show 6ff3413bba9c8430c3b0bc4d2052e21d0407183f:tools/souji-proc-census.sh
```

The baseline file is source input to the fixture; it was not executed as the proc tool. The fixture extracts exact historical function bodies and substitutes a synthetic cmdline input path. Every execution of the current proc tool was through the fixture's `--reason-only argv|fd --prefix ...` calls. No census, proc selftest, live `/proc` observation, process signal, other runtime, or subagent was invoked. No tools were installed or updated.

## Mutant and expected detector

Mutated only `/var/tmp/souji-r21-MutateReasonMask/lane/tools/souji-proc-census.sh`, at `format_reason()` (original lines 250–255). Replaced the formatter body with a local kind/path binding and the requested raw assignment, bypassing secret provenance, pattern masking/control replacement, and truncation. All callers and the fixture stayed unchanged.

Expected detector: `/var/tmp/souji-r21-MutateReasonMask/lane/tests/fixtures/r21-reason-canary.sh`, with the exact `6ff3413bba9c8430c3b0bc4d2052e21d0407183f` baseline source. Expected failures: synthetic canary leaks and reasons exceeding 160 bytes. The control-byte cases also failed in the actual run.

Exact mutation diff, captured by the following command (exit 0):

```sh
git -C /var/tmp/souji-r21-MutateReasonMask/lane diff 522dcd768ca90afe166532d37d306d3df70aeea5 -- /var/tmp/souji-r21-MutateReasonMask/lane/tools/souji-proc-census.sh
```

```diff
diff --git c/tools/souji-proc-census.sh w/tools/souji-proc-census.sh
index a1bddfe..7ff9031 100755
--- c/tools/souji-proc-census.sh
+++ w/tools/souji-proc-census.sh
@@ -248,10 +248,8 @@ redact_command() {
 }
 
 format_reason() {
-  local kind=$1 path=$2 secret=${3:-0}
-  if ((secret)); then path='[REDACTED]'; fi
-  redact_secrets "$kind-path-gone:$path"
-  REDACTED_REASON=${REDACTED_FIELD:0:160}
+  local kind=$1 path=$2
+  REDACTED_REASON="$kind-path-gone:$path"
 }
 
 # The stream parser is shared by the census and the /proc-free fixture mode.
```

## Same bounded detector, three phases

The exact same command was executed once per phase, in order pristine → mutated → restored:

```sh
bash /var/tmp/souji-r21-MutateReasonMask/lane/tests/fixtures/r21-reason-canary.sh --tool /var/tmp/souji-r21-MutateReasonMask/lane/tools/souji-proc-census.sh --base /var/tmp/souji-r21-MutateReasonMask/base-6ff3413-souji-proc-census.sh
```

| Phase | Detector exit | Observed result |
| --- | ---: | --- |
| Pristine integrated build | 0 | 27/27 cases passed; no leaks; maximum 160 bytes |
| Assigned mutant | 1 | 23 failures; 19 synthetic leaks; maximum 454 bytes |
| Restored exact bytes | 0 | 27/27 cases passed; no leaks; maximum 160 bytes |

Literal pristine summary:

```text
SUMMARY	total=27	pass=27	fail=0	leaks=0	base_leaks=19	max_reason_bytes=160
```

Literal mutant CASE and SUMMARY lines (DETAIL payload lines omitted; these are all 27 case outcomes, including every failed case name):

```text
CASE	FAIL	argv-github	exit=0	leak=1	base_leak=1	bytes=83
CASE	FAIL	argv-openai	exit=0	leak=1	base_leak=1	bytes=82
CASE	FAIL	argv-aws	exit=0	leak=1	base_leak=1	bytes=82
CASE	FAIL	argv-slack	exit=0	leak=1	base_leak=1	bytes=84
CASE	FAIL	argv-password	exit=0	leak=1	base_leak=1	bytes=88
CASE	FAIL	argv-userinfo	exit=0	leak=1	base_leak=1	bytes=96
CASE	FAIL	argv-token-marker	exit=0	leak=1	base_leak=1	bytes=87
CASE	FAIL	argv-bearer	exit=0	leak=1	base_leak=1	bytes=101
CASE	FAIL	fd-github	exit=0	leak=1	base_leak=1	bytes=81
CASE	FAIL	fd-openai	exit=0	leak=1	base_leak=1	bytes=80
CASE	FAIL	fd-aws	exit=0	leak=1	base_leak=1	bytes=80
CASE	FAIL	fd-slack	exit=0	leak=1	base_leak=1	bytes=82
CASE	FAIL	fd-password	exit=0	leak=1	base_leak=1	bytes=86
CASE	FAIL	fd-userinfo	exit=0	leak=1	base_leak=1	bytes=94
CASE	FAIL	fd-token-marker	exit=0	leak=1	base_leak=1	bytes=85
CASE	FAIL	fd-bearer	exit=0	leak=1	base_leak=1	bytes=99
CASE	FAIL	token-equals	exit=0	leak=1	base_leak=1	bytes=71
CASE	FAIL	token-next	exit=0	leak=1	base_leak=1	bytes=71
CASE	FAIL	password-equals	exit=0	leak=1	base_leak=1	bytes=71
CASE	pass	argv-plain	exit=0	leak=0	base_leak=0	bytes=67
CASE	FAIL	argv-controls	exit=0	leak=0	base_leak=0	bytes=67
CASE	FAIL	argv-bound	exit=0	leak=0	base_leak=0	bytes=454
CASE	pass	fd-plain	exit=0	leak=0	base_leak=0	bytes=65
CASE	FAIL	fd-controls	exit=0	leak=0	base_leak=0	bytes=65
CASE	FAIL	fd-bound	exit=0	leak=0	base_leak=0	bytes=452
CASE	pass	no-gone-argv	exit=3	leak=0	base_leak=0	bytes=0
CASE	pass	no-gone-fd	exit=3	leak=0	base_leak=0	bytes=0
SUMMARY	total=27	pass=4	fail=23	leaks=19	base_leaks=19	max_reason_bytes=454
```

Literal restored summary:

```text
SUMMARY	total=27	pass=27	fail=0	leaks=0	base_leaks=19	max_reason_bytes=160
```

The 19 canary/provenance failures, two control failures, and two bound failures account for all 23 mutant failures. Both plain-path and both no-gone cases still passed. The no-gone child exit 3 is expected fixture behavior, not a detector-process failure.

## Byte restoration evidence

The inverse hashline edit restored the original formatter body before the third detector execution. The restored source readback tag returned to `2EB7` from mutant tag `6D80`. SHA-256 was measured independently before mutation, during mutation, and after restoration.

Pristine hash command (exit 0):

```sh
sha256sum /var/tmp/souji-r21-MutateReasonMask/lane/tools/souji-proc-census.sh /var/tmp/souji-r21-MutateReasonMask/lane/tests/fixtures/r21-reason-canary.sh
```

Mutated and restored hash command (executed once in each phase; both exit 0):

```sh
sha256sum /var/tmp/souji-r21-MutateReasonMask/lane/tools/souji-proc-census.sh /var/tmp/souji-r21-MutateReasonMask/lane/tests/fixtures/r21-reason-canary.sh /var/tmp/souji-r21-MutateReasonMask/base-6ff3413-souji-proc-census.sh
```

| Input | Pristine SHA-256 | Mutated SHA-256 | Restored SHA-256 |
| --- | --- | --- | --- |
| Proc tool | `3bc403440d67e2e8a096f52e3953cfb32a5a415c8e032d91d386c95f792fafb5` | `98f774325db3775786cb4cdd38de2a85cb7bf7e53df13b9e8c661ebb317f1f5b` | `3bc403440d67e2e8a096f52e3953cfb32a5a415c8e032d91d386c95f792fafb5` |
| Canary fixture | `46a60e32c86301c8a4bb70bc83a04591749c6466c33cc5ef112a4f5d885add39` | `46a60e32c86301c8a4bb70bc83a04591749c6466c33cc5ef112a4f5d885add39` | `46a60e32c86301c8a4bb70bc83a04591749c6466c33cc5ef112a4f5d885add39` |

Exact baseline source SHA-256 at extraction, during mutation, and after restoration: `37c3316a1fd8cdda18cbefdc7692d3d3f388e5783e8fe19085f5d932a8ceba64`.

Only the assigned scratch source was mutated and restored. Production source and lane VCS were not changed; this report is the only delivered artifact, with no patch delivery. No broader finding or closure ruling is claimed.
