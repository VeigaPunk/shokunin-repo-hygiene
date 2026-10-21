# MutateReplayOutput — bounded mutation probe

STATUS: COMPLETE. Verdict: **KILLED**. Author-side advisory evidence only; not integration or certification.

## Axes and frozen target

- Primary axis: C2 operability, specifically refusal of output paths inside the source repository (including its `.git` directory).
- Probe safeguards: detector discrimination and byte-exact restoration, without invoking runner main with source-internal output.
- Oracle read first: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-21/preregistration.txt`, C2; also read the pre-measurement clarification.
- Isolated clone: `/var/tmp/souji-r21-MutateReplayOutput/lane`.
- Branch: `r21/MutateReplayOutput`.
- Observed base: `522dcd768ca90afe166532d37d306d3df70aeea5`.
- Prior runner: exact `census/round-21/run-acceptance.py` bytes from `8513d6ac97076f34ff94a3fc1979c13e69c2d19a`, saved as `/var/tmp/souji-r21-MutateReplayOutput/lane/prior8513-run-acceptance.py`. Its file SHA-256 equals the extracted git bytes SHA-256.

## Setup commands actually executed

```text
cwd=/var/tmp
mkdir /var/tmp/souji-r21-MutateReplayOutput
exit=0

cwd=/var/tmp/souji-r21-MutateReplayOutput
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r21-MutateReplayOutput/lane
exit=0

cwd=/var/tmp/souji-r21-MutateReplayOutput/lane
git -C /var/tmp/souji-r21-MutateReplayOutput/lane switch -c r21/MutateReplayOutput 522dcd768ca90afe166532d37d306d3df70aeea5 && git -C /var/tmp/souji-r21-MutateReplayOutput/lane rev-parse HEAD
exit=0
Switched to a new branch 'r21/MutateReplayOutput'
522dcd768ca90afe166532d37d306d3df70aeea5

cwd=/var/tmp/souji-r21-MutateReplayOutput/lane
git -C /var/tmp/souji-r21-MutateReplayOutput/lane show 8513d6ac97076f34ff94a3fc1979c13e69c2d19a:census/round-21/run-acceptance.py
exit=0
```

The extraction command's captured stdout was written with the write tool, not executed.

## Mutant and expected detector

Deleted only the two-line source-containment refusal in `output_path` at original lines 239–240 of `/var/tmp/souji-r21-MutateReplayOutput/lane/census/round-21/run-acceptance.py`. All other checks remained unchanged. Expected detector: `/var/tmp/souji-r21-MutateReplayOutput/lane/tests/fixtures/r21-replay-boundaries.py`, with the prior8513 runner as `--base-tool`; only `source-root` and `source-git` should fail after the deletion.

Exact diff command (exit 0; cwd is the isolated clone):

```text
git -C /var/tmp/souji-r21-MutateReplayOutput/lane diff 522dcd768ca90afe166532d37d306d3df70aeea5 -- /var/tmp/souji-r21-MutateReplayOutput/lane/census/round-21/run-acceptance.py
```

Exact observed diff:

```diff
diff --git c/census/round-21/run-acceptance.py w/census/round-21/run-acceptance.py
index ed28edd..4a3351f 100755
--- c/census/round-21/run-acceptance.py
+++ w/census/round-21/run-acceptance.py
@@ -236,8 +236,6 @@ def output_path(raw: str, root: Path) -> Path:
     if parent != candidate.parent or not parent.is_dir():
         raise Refusal("output parent must be an existing canonical non-symlink directory")
     candidate = parent / candidate.name
-    if candidate == root or root in candidate.parents:
-        raise Refusal("output must be outside the source repository")
     if candidate.exists() or candidate.is_symlink():
         raise Refusal("refusing existing output: " + str(candidate))
     return candidate
```

## Same behavioral detector on pristine, mutated, restored bytes

All three invocations used this exact command, with cwd `/var/tmp/souji-r21-MutateReplayOutput/lane`:

```text
python3 -B /var/tmp/souji-r21-MutateReplayOutput/lane/tests/fixtures/r21-replay-boundaries.py --tool /var/tmp/souji-r21-MutateReplayOutput/lane/census/round-21/run-acceptance.py --base-tool /var/tmp/souji-r21-MutateReplayOutput/lane/prior8513-run-acceptance.py
```

### Pristine — exit 0

```text
CASE	pass	source-root	expected=False	actual=False	base=True
CASE	pass	source-git	expected=False	actual=False	base=True
CASE	pass	relative	expected=False	actual=False	base=True
CASE	pass	outside	expected=True	actual=True	base=True
CASE	pass	existing	expected=False	actual=False	base=False
CASE	pass	parent-symlink	expected=False	actual=False	base=False
CASE	pass	ancestor-symlink	expected=False	actual=False	base=True
CASE	pass	missing-parent	expected=False	actual=False	base=False
SUMMARY	total=8	pass=8	fail=0	base_discriminating=4
```

### Mutated — exit 1

```text
CASE	FAIL	source-root	expected=False	actual=True	base=True
CASE	FAIL	source-git	expected=False	actual=True	base=True
CASE	pass	relative	expected=False	actual=False	base=True
CASE	pass	outside	expected=True	actual=True	base=True
CASE	pass	existing	expected=False	actual=False	base=False
CASE	pass	parent-symlink	expected=False	actual=False	base=False
CASE	pass	ancestor-symlink	expected=False	actual=False	base=True
CASE	pass	missing-parent	expected=False	actual=False	base=False
SUMMARY	total=8	pass=6	fail=2	base_discriminating=4
```

### Restored — exit 0

```text
CASE	pass	source-root	expected=False	actual=False	base=True
CASE	pass	source-git	expected=False	actual=False	base=True
CASE	pass	relative	expected=False	actual=False	base=True
CASE	pass	outside	expected=True	actual=True	base=True
CASE	pass	existing	expected=False	actual=False	base=False
CASE	pass	parent-symlink	expected=False	actual=False	base=False
CASE	pass	ancestor-symlink	expected=False	actual=False	base=True
CASE	pass	missing-parent	expected=False	actual=False	base=False
SUMMARY	total=8	pass=8	fail=0	base_discriminating=4
```

All three detector runs had empty stderr. Literal failed case names were `source-root` and `source-git`, and no others. The pristine run passed, so this is a killed mutant rather than an inconclusive baseline failure. The restored detector stdout exactly equals pristine stdout.

## Hashes and restoration evidence

The same hash command ran before mutation, while mutated, and after restoration; all three exits were 0:

```text
sha256sum /var/tmp/souji-r21-MutateReplayOutput/lane/census/round-21/run-acceptance.py /var/tmp/souji-r21-MutateReplayOutput/lane/tests/fixtures/r21-replay-boundaries.py /var/tmp/souji-r21-MutateReplayOutput/lane/prior8513-run-acceptance.py
```

pristine-hashes:

```text
6a395c13bc156abedd7c8819b109036352d4a8cef158fdda54bace6d842ca560  /var/tmp/souji-r21-MutateReplayOutput/lane/census/round-21/run-acceptance.py
3fc1d18c28188d5f3c2f842f5fda2a4d98b460a40ecdf699aa6f57baa59aac27  /var/tmp/souji-r21-MutateReplayOutput/lane/tests/fixtures/r21-replay-boundaries.py
2ac2eaa720f5581ab5db0292b8170282818157ea5e13f57bcd3a3f8395578171  /var/tmp/souji-r21-MutateReplayOutput/lane/prior8513-run-acceptance.py
```

mutated-hashes:

```text
291df3ba415587543c18deb9e407c73242b58eee63ff8aac63e888fecead5742  /var/tmp/souji-r21-MutateReplayOutput/lane/census/round-21/run-acceptance.py
3fc1d18c28188d5f3c2f842f5fda2a4d98b460a40ecdf699aa6f57baa59aac27  /var/tmp/souji-r21-MutateReplayOutput/lane/tests/fixtures/r21-replay-boundaries.py
2ac2eaa720f5581ab5db0292b8170282818157ea5e13f57bcd3a3f8395578171  /var/tmp/souji-r21-MutateReplayOutput/lane/prior8513-run-acceptance.py
```

restored-hashes:

```text
6a395c13bc156abedd7c8819b109036352d4a8cef158fdda54bace6d842ca560  /var/tmp/souji-r21-MutateReplayOutput/lane/census/round-21/run-acceptance.py
3fc1d18c28188d5f3c2f842f5fda2a4d98b460a40ecdf699aa6f57baa59aac27  /var/tmp/souji-r21-MutateReplayOutput/lane/tests/fixtures/r21-replay-boundaries.py
2ac2eaa720f5581ab5db0292b8170282818157ea5e13f57bcd3a3f8395578171  /var/tmp/souji-r21-MutateReplayOutput/lane/prior8513-run-acceptance.py
```

Immediately after the mutant detector, the edit tool reinserted exactly the two removed lines into the isolated runner. Its source snapshot tag returned from `39E4` to the original `7203`; the restored runner SHA-256 equals pristine (`6a395c13bc156abedd7c8819b109036352d4a8cef158fdda54bace6d842ca560`). Fixture and prior-runner hashes also remained unchanged. No lane production source or sibling source was edited. Only this report is delivered; no patch is delivered.

## Bounded conclusion and safety

The assigned two-line deletion is detected by the existing boundary fixture: pristine 8/8, mutant 6/8, restored 8/8. This establishes sensitivity to this mutation only, not general runner correctness.

The detector imports the two runners and calls `output_path` directly; runner main was never invoked, including with any source-internal output. No acceptance inventory, proc tool, live `/proc`, census, signal operation, or additional runtime was invoked. No tools were installed or upgraded. Probe complete; no production fix attempted.
