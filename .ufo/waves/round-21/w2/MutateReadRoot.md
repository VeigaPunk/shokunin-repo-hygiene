# MutateReadRoot — C1 calibration mutation probe

Author-side advisory only; no integration, shipping, or claim certification.

## Axes and scope

- **Calibration / detector sensitivity:** the frozen synthetic fixture must reject a classifier that never emits `V-READ-ROOT`.
- **Compatibility / specificity guard:** negative cases and non-`V-READ-ROOT` verdicts must remain unchanged.
- **Isolation / restoration:** mutate only the assigned private clone and restore the source byte-for-byte.

Oracle read first: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-21/preregistration.txt`, C1 lines 4–13. Also read `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-21/clarification-before-measurement.txt`. No corpus census was performed.

Assigned scratch: `/var/tmp/souji-r21-MutateReadRoot`; clone and every detector/diff/hash command cwd: `/var/tmp/souji-r21-MutateReadRoot/lane`. Setup necessarily ran before that clone existed, with cwd `/var/tmp`.

## Setup and pinned inputs

Executed setup command, exit **0**:

```sh
mkdir /var/tmp/souji-r21-MutateReadRoot && git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r21-MutateReadRoot/lane && git -C /var/tmp/souji-r21-MutateReadRoot/lane switch -c r21/MutateReadRoot 522dcd768ca90afe166532d37d306d3df70aeea5 && git -C /var/tmp/souji-r21-MutateReadRoot/lane rev-parse HEAD
```

Literal output:

```text
Switched to a new branch 'r21/MutateReadRoot'
522dcd768ca90afe166532d37d306d3df70aeea5
```

Retrieved the historical comparison auditor with this command via Python `subprocess.run(..., cwd=clone, capture_output=True)`, exit **0**:

```sh
git -C /var/tmp/souji-r21-MutateReadRoot/lane show 6ff3413bba9c8430c3b0bc4d2052e21d0407183f:tools/souji-seat-audit.py
```

Its captured UTF-8 stdout was written using the file-write tool to `/var/tmp/souji-r21-MutateReadRoot/lane/tools/souji-seat-audit.baseline-6ff.py`. Observed SHA-256: `b2fa68e2e98dae9d046c11775737337fb99b0db94fb5042017e4c8a56fc83389`.

## Mutant and exact diff

One added behavior-bearing statement after the docstring makes `implicit_root_read` unconditionally return `None`. The remainder of the function stays parseable and unreachable. No detector or baseline bytes were changed.

Executed diff command, exit **0**:

```sh
git -C /var/tmp/souji-r21-MutateReadRoot/lane diff --no-ext-diff 522dcd768ca90afe166532d37d306d3df70aeea5 -- /var/tmp/souji-r21-MutateReadRoot/lane/tools/souji-seat-audit.py
```

Exact output:

```diff
diff --git c/tools/souji-seat-audit.py w/tools/souji-seat-audit.py
index 6cf3a85..8baf1cb 100755
--- c/tools/souji-seat-audit.py
+++ w/tools/souji-seat-audit.py
@@ -376,6 +376,7 @@ def target_verdict(target: str | None, truncated: bool, is_header: bool,
 
 def implicit_root_read(tool: str, args: str, lane: str, fleet: str) -> str | None:
     """Return a visible outside-lane relative target, never guess past a cut."""
+    return None
     if tool == "grep":
         if " @ " in args:
             target = args.rsplit(" @ ", 1)[1]
```

## Expected detector and actual outputs

Expected outcome from the assigned mutation: **14 failures**, not a pass, because the 14 literal positive cases lose the new class while the baseline comparator never had that class.

The following exact bounded detector command was run once on pristine bytes, once on mutated bytes, and once after restoration, always from the clone cwd:

```sh
python3 /var/tmp/souji-r21-MutateReadRoot/lane/tests/fixtures/r21-read-root.py --tool /var/tmp/souji-r21-MutateReadRoot/lane/tools/souji-seat-audit.py --base-tool /var/tmp/souji-r21-MutateReadRoot/lane/tools/souji-seat-audit.baseline-6ff.py
```

| Source state | Exit | Literal summary line |
| --- | ---: | --- |
| Pristine | 0 | `SUMMARY	total=32	pass=32	fail=0	base_discriminating=14` |
| Mutated | 1 | `SUMMARY	total=32	pass=18	fail=14	base_discriminating=14` |
| Restored | 0 | `SUMMARY	total=32	pass=32	fail=0	base_discriminating=14` |

Literal mutated failure rows, including every failed case name:

```text
CASE	FAIL	relative-read	expected=True observed=False preserved=True
CASE	FAIL	relative-range	expected=True observed=False preserved=True
CASE	FAIL	relative-raw	expected=True observed=False preserved=True
CASE	FAIL	relative-comma	expected=True observed=False preserved=True
CASE	FAIL	implicit-grep	expected=True observed=False preserved=True
CASE	FAIL	relative-grep	expected=True observed=False preserved=True
CASE	FAIL	relative-glob	expected=True observed=False preserved=True
CASE	FAIL	dot-glob	expected=True observed=False preserved=True
CASE	FAIL	semicolon	expected=True observed=False preserved=True
CASE	FAIL	escape-read	expected=True observed=False preserved=True
CASE	FAIL	parent-read	expected=True observed=False preserved=True
CASE	FAIL	dot-read	expected=True observed=False preserved=True
CASE	FAIL	attempt-error	expected=True observed=False preserved=True
CASE	FAIL	truncated-pattern-visible-target	expected=True observed=False preserved=True
```

The other 18 mutated cases passed. All 32 mutated case rows reported `preserved=True`; the 14 failures were absent expected `V-READ-ROOT` classifications, not import/parse errors or changed preexisting class verdicts.

## Before, mutated, and restored hashes

Pristine hash command, exit **0**:

```sh
sha256sum /var/tmp/souji-r21-MutateReadRoot/lane/tools/souji-seat-audit.py /var/tmp/souji-r21-MutateReadRoot/lane/tests/fixtures/r21-read-root.py
```

Mutated and restored hash command, executed once in each state, both exits **0**:

```sh
sha256sum /var/tmp/souji-r21-MutateReadRoot/lane/tools/souji-seat-audit.py /var/tmp/souji-r21-MutateReadRoot/lane/tests/fixtures/r21-read-root.py /var/tmp/souji-r21-MutateReadRoot/lane/tools/souji-seat-audit.baseline-6ff.py
```

| Input | Pristine SHA-256 | Mutated SHA-256 | Restored SHA-256 |
| --- | --- | --- | --- |
| `/var/tmp/souji-r21-MutateReadRoot/lane/tools/souji-seat-audit.py` | `e1298b9348f42406af59be885dcfac146c8939c8d389fd2109532b9fe397687c` | `b20a1a10552b85e21328e973ab3588cd9587d4d59da8763bbf8d88a3a2020b27` | `e1298b9348f42406af59be885dcfac146c8939c8d389fd2109532b9fe397687c` |
| `/var/tmp/souji-r21-MutateReadRoot/lane/tests/fixtures/r21-read-root.py` | `00d9347a26738d073d5799aa0815301fe7062dd42921b03540dd29679c470e9b` | `00d9347a26738d073d5799aa0815301fe7062dd42921b03540dd29679c470e9b` | `00d9347a26738d073d5799aa0815301fe7062dd42921b03540dd29679c470e9b` |
| `/var/tmp/souji-r21-MutateReadRoot/lane/tools/souji-seat-audit.baseline-6ff.py` | `b2fa68e2e98dae9d046c11775737337fb99b0db94fb5042017e4c8a56fc83389` (captured historical bytes) | `b2fa68e2e98dae9d046c11775737337fb99b0db94fb5042017e4c8a56fc83389` | `b2fa68e2e98dae9d046c11775737337fb99b0db94fb5042017e4c8a56fc83389` |

Restoration removed only the added statement from the scratch source using the surgical-edit tool. For an additional exact-byte comparison, executed the following command via Python subprocess, exit **0**:

```sh
git -C /var/tmp/souji-r21-MutateReadRoot/lane show 522dcd768ca90afe166532d37d306d3df70aeea5:tools/souji-seat-audit.py
```

Compared its captured bytes with the restored scratch source; literal result:

```text
RESTORED_EQUALS_PINNED_BYTES: True
PINNED_SHA256: e1298b9348f42406af59be885dcfac146c8939c8d389fd2109532b9fe397687c
```

## Verdict and boundaries

**KILLED.** The pristine detector passed, the assigned mutant produced exactly the expected 14 behavioral failures, and the identical restored detector passed. Restoration was exact. This is evidence for this one mutation's detection, not certification of C1 or other claims.

Only this report is delivered; no patch or production-source modification. No sibling source edits, lane VCS mutations, process signals, live `/proc` reads, proc-tool executions, or additional runtime invocations. No tools installed or upgraded. Probe stopped after the assigned mutation/restoration sequence.
