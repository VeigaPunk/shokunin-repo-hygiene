PROCESS LIMIT: The outer clone/checkout ran without the child-environment and Git command overrides specified in the parent’s later neutralization note. That note arrived after setup and all three authorized detector runs. The parent subsequently clarified that it is prospective, not a request to repeat results: the actual command evidence, observed outputs, source hashes and restoration evidence stand. No retroactive clean-environment claim is made.

# Round 20 final falsification — MutateProtectedAncestor

VERDICT: KILLED. The assigned two-line guard mutation was effective: the pristine complete detector passed, the mutant failed only `helper-protected-census-ancestor-no-walk`, and exact restored bytes passed the same complete detector. No input-boundary code defect was found by this one probe; the setup process limit above is disclosed separately. Author-side advisory only; not certification, integration, non-author closure, or promotion.

## Axes and scope

- Primary axis: C2 operability / bounded actual caller input validation.
- Supporting axes: behavioral detector sensitivity; isolated execution and exact restoration.
- Pinned build: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`.
- Preregistered comparison baseline: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`.
- Private scratch: `/var/tmp/souji-r20w2-MutateProtectedAncestor`.
- Private branch: `souji-r20-MutateProtectedAncestor`.
- Assigned invariant: `input_snapshot` must refuse bare `census` before Git or a filesystem walk can expand the protected ancestor. The operator-sweep child refusal must remain intact.

## Observed setup and source preservation

Prospective setup neutralization, received after this probe: outer clone/checkout should use child-only `GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_OPTIONAL_LOCKS=0 GIT_NO_LAZY_FETCH=1` and Git flags `-c maintenance.auto=false -c core.hooksPath=/dev/null -c core.fsmonitor=false`. Those overrides were not applied to the already-completed outer setup. No global configuration was inspected, no absence of operator hook/maintenance execution is claimed, and no additional clone, checkout, detector run or root probe was performed after either parent clarification. The specified fixture already sanitizes its own child environments. The actual branch base remains the full ID recorded below. The parent explicitly directed retaining these original results without rerunning or recreating the clone.

Executed setup (exit 0):

```sh
test ! -e /var/tmp/souji-r20w2-MutateProtectedAncestor && test ! -L /var/tmp/souji-r20w2-MutateProtectedAncestor && mkdir /var/tmp/souji-r20w2-MutateProtectedAncestor && git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r20w2-MutateProtectedAncestor/lane && git -C /var/tmp/souji-r20w2-MutateProtectedAncestor/lane switch --quiet --create souji-r20-MutateProtectedAncestor 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1 && git -C /var/tmp/souji-r20w2-MutateProtectedAncestor/lane rev-parse souji-r20-MutateProtectedAncestor
```

Observed stdout:

```text
1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1
```

The fixture was inspected with this named-file, read-only production command (exit 0):

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:tests/fixtures/r20-input-binding.py
```

Pristine helper bytes were captured by this read-only command (exit 0), SHA-256 matched the original clone file, and the write tool saved all 15,357 bytes to `/var/tmp/souji-r20w2-MutateProtectedAncestor/pristine-souji-rev-pin.py` before mutation:

```sh
git -C /var/tmp/souji-r20w2-MutateProtectedAncestor/lane show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:tools/souji-rev-pin.py
```

Historical input-binding helper extraction was also read-only (exit 0), captured stdout was written with the write tool to the named private baseline file `/var/tmp/souji-r20w2-MutateProtectedAncestor/baseline-souji-rev-pin.py` (11,549 bytes); no network or historical-helper execution:

```sh
git -C /var/tmp/souji-r20w2-MutateProtectedAncestor/lane show 12516f7dcdd5b165e5ee208d44a38d63b5bd5812:tools/souji-rev-pin.py
```

Historical helper SHA-256: `d00a947bbf457b4bd79e338f8c0aecc3407e5574c945bf2ec32ff2c157aebe40`. This assigned input-binding fixture has no separate auditor runtime; its specified `--baseline` arm exercised the historical caller comparisons.

## Single mutant

Only `tools/souji-rev-pin.py`, `input_snapshot`, lines 110–111 in the private clone changed, using the surgical edit tool:

```diff
-                parts[0] == "census" and (len(parts) == 1
-                or parts[1].startswith("operator-sweep-"))):
+                parts[0] == "census" and len(parts) > 1
+                and parts[1].startswith("operator-sweep-")):
```

This removes only the bare ancestor refusal, retaining the short-circuited operator-sweep child refusal and the existing `.git`/`.jj` refusal. The fixture, expected values, reports used as inputs, and other source files were not mutated.

Expected detector: `helper-protected-census-ancestor-no-walk`. Its driver replaces both helper `_git` and `os.walk` with rejecting tripwires before passing bare `census` in a fixture-created synthetic repository. Passing requires a `Refusal` containing `protected measured path` and zero Git/walk calls. Thus the assigned counterexample does not traverse a real protected path. The mutant's observed case failure below is the behavioral evidence; no unreported internal tripwire counter or exception is claimed.

## Exact three-run command and actual outputs

Working directory for every run: `/var/tmp/souji-r20w2-MutateProtectedAncestor/lane`. The identical complete command ran exactly once for each state:

```sh
python3 -B tests/fixtures/r20-input-binding.py --root /var/tmp/souji-r20w2-MutateProtectedAncestor/lane --baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812
```

| State | Actual exit | Cases | Exact failing case | Inventory | stderr |
| --- | ---: | --- | --- | --- | --- |
| Pristine | 0 | 43 pass / 0 fail | none | 43 expected / 43 observed; no omissions, extras, duplicates | empty |
| Mutant | 1 | 42 pass / 1 fail | `helper-protected-census-ancestor-no-walk` | 43 expected / 43 observed; no omissions, extras, duplicates | empty |
| Exact restored | 0 | 43 pass / 0 fail | none | 43 expected / 43 observed; no omissions, extras, duplicates | empty |

Exact relevant stdout, pristine:

```text
CASE	pass	helper-protected-census-ancestor-no-walk	actual helper API; ambient GIT_DIR points at a different synthetic repository
INVENTORY	exact	expected=43 observed=43 missing=- unexpected=- duplicates=0
SUMMARY	total=43	pass=43	fail=0	blocked=0	inventory=exact	baseline_mismatches=8
```

Exact relevant stdout, mutant:

```text
CASE	FAIL	helper-protected-census-ancestor-no-walk	actual helper API; ambient GIT_DIR points at a different synthetic repository
INVENTORY	exact	expected=43 observed=43 missing=- unexpected=- duplicates=0
SUMMARY	total=43	pass=42	fail=1	blocked=0	inventory=exact	baseline_mismatches=8
```

Exact relevant stdout, restored:

```text
CASE	pass	helper-protected-census-ancestor-no-walk	actual helper API; ambient GIT_DIR points at a different synthetic repository
INVENTORY	exact	expected=43 observed=43 missing=- unexpected=- duplicates=0
SUMMARY	total=43	pass=43	fail=0	blocked=0	inventory=exact	baseline_mismatches=8
```

All three runs reported `BASELINE_SUMMARY` with baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`, 49 closure files and 8 byte mismatches. Those are the fixture's old-vs-current byte comparison receipts, not failed cases: pristine and restored actually exited 0. The same seven historical/current tripwire pairs and four full-ID historical counter cases passed in every run. No standalone counter, helper, suite, or other test command was invoked outside the specified fixture.

Full actual stdout/stderr are retained only in this seat's scratch:

| State | stdout file | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| pristine | `/var/tmp/souji-r20w2-MutateProtectedAncestor/pristine-detector.stdout` | 7289 | `ba4c4a75a37f70f2f941f7c1838d0c963cf60db2b4dc34f5f6ee76560cca094f` |
| mutant | `/var/tmp/souji-r20w2-MutateProtectedAncestor/mutant-detector.stdout` | 7289 | `1578f98e5c397395a2eed1d49ab329dd91836d8ca2c5c0d0b4e214cef3c7cdce` |
| restored | `/var/tmp/souji-r20w2-MutateProtectedAncestor/restored-detector.stdout` | 7289 | `ba4c4a75a37f70f2f941f7c1838d0c963cf60db2b4dc34f5f6ee76560cca094f` |

The corresponding `pristine-detector.stderr`, `mutant-detector.stderr`, and `restored-detector.stderr` files are each zero bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Digests and exact restoration

Observed SHA-256 values:

| File/state | SHA-256 |
| --- | --- |
| Helper, pristine before mutation | `d3e9111b66f17242124df97db0327195c75a5c44252566d2130ff38c5755f32e` |
| Helper, effective mutant before mutant run | `f28adc07de3c58e5fff3b83e4272e25f578fee554fcf6aa08938dcccca1fa4b9` |
| Helper, restored before restored run | `d3e9111b66f17242124df97db0327195c75a5c44252566d2130ff38c5755f32e` |
| Helper, final after restored run | `d3e9111b66f17242124df97db0327195c75a5c44252566d2130ff38c5755f32e` |
| Saved pristine helper | `d3e9111b66f17242124df97db0327195c75a5c44252566d2130ff38c5755f32e` |
| Fixture, pristine/mutant/restored/final | `160f92c40c6ed62059c1a51f8323eaba7777669bf1cb40bd68c24e2b7d310aef` |

The mutant was restored in the detector orchestration's `finally` block using the write tool and the exact saved pristine bytes, not a reconstructed reverse patch. Observed write: 15,357 bytes, original helper snapshot identity restored. An explicit SHA equality assertion passed before the restored run and again after it.

Initial/mutant/final source digest command (exit 0 each):

```sh
sha256sum tools/souji-rev-pin.py tests/fixtures/r20-input-binding.py
```

The pre-restored-run digest command (exit 0) additionally checked both saved inputs:

```sh
sha256sum tools/souji-rev-pin.py tests/fixtures/r20-input-binding.py ../pristine-souji-rev-pin.py ../baseline-souji-rev-pin.py
```

No production source changes, sibling writes, subagents, package installs, host/global configuration changes, process census, signals, protected material traversal, or additional test runs. Only the assigned report was written in the production lane. This result is one bounded mutation kill, not proof of every input-boundary property or authority to alter any held gate.

Report: .ufo/waves/round-20/final/MutateProtectedAncestor.md
