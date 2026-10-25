# W2C1Rerun — C1 after-state rerun (round 24, wave 2 FALSIFY)

## Status
STATUS: PASS — verdict **survives**. In a scratch clone at ca7fc1c, the tip prints the C1 target line with exit 0. The stub control at 1efe406 prints `pass=4` and no target line. Both receipts verify with the runner, and the per-CASE lines match each receipt byte-for-byte.

## Evidence
Scratch: `/var/tmp/souji-r24-W2C1Rerun/` (`git clone -q --no-local <lane> lane`, `git checkout --detach ca7fc1cb6dd1333096c6f3bdbad304686691d126`; a second clone `ctl` detached at 1efe406e7f39b8fe736be2a566053703a571ffc0). git 2.56.0, Python 3.14.8. Nothing was run in the lane except read-only `git rev-parse/log/diff/cat-file` and `souji-receipt-run.py verify`. No tools were installed.

Lane `master` is now c3ca7ad (wave-1 reports commit). The C1 blobs are identical at 778747e, ca7fc1c and c3ca7ad: fixture `fe08f3aa…`, tool `a710dfa3…`, stub `0250c622…`. The only paths that differ between 778747e and ca7fc1c are the 7 added `census/round-24/records/*` and `size-census-lane.txt` files.

1. Tip run (rev ca7fc1c): `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py`
   - Exit code: `rc=0`
   - Last line: `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`
   - Fixture sha256 `373ef1f0…084f`, equal to the receipt's `tool_sha256`.
2. Stub control (rev 1efe406): `python3 -B tests/fixtures/r24-size-census.py --tool census/round-24/controls/stub-size-census.py`
   - Exit code: `rc=1`
   - Last line: `cases=8 pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`. The target line is absent.
   - Cases 2, 3, 5 and 6 FAIL; cases 1, 4, 7 and 8 PASS.
3. Per-CASE comparison: I extracted the receipt stdout blocks with awk and ran `diff` against my reruns. Tip vs `c1-after.tsv`: `IDENTICAL`. Stub vs `c1-control-stub.tsv`: `IDENTICAL`. The comparison covers all 9 lines of each, including the counts, the `manifest_changed` values, and `stub_failed=dangling,garbage,alternates`.
4. Runner verify, using both the lane runner (root = lane) and the clone runner (root = clone):
   - `c1-after.tsv`: `verify=ok rev=778747eb… tool=tests/fixtures/r24-size-census.py tool_sha256=373ef1f0…`, rc=0 under both runners.
   - `c1-control-stub.tsv`: `verify=ok rev=1efe406e… tool_sha256=373ef1f0…`, rc=0 under both runners.
5. Robustness reruns at the tip:
   - Repeatability: 5 reruns, all rc=0 with stdout sha256 `03856d4261f82c66`.
   - Hostile git environment (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_OBJECT_DIRECTORY`, `GIT_CONFIG_PARAMETERS=gc.auto=1`): 8/8.
   - Hostile `HOME/.gitconfig` (gc.auto=1, maintenance.auto=true, untrackedCache, writeCommitGraph, defaultBranch=trunk): output identical to the plain tip run.
   - Locale `LC_ALL=tr_TR.UTF-8`: 8/8.
   - Leftovers: zero `/var/tmp/souji-r24-census-*` directories remain after the runs.
6. Base control: `git cat-file -e a65fac98…:tests/fixtures/r24-size-census.py` and `…:tools/souji-size-census.py` both fail (ABSENT), so the do-nothing state is `cases=0`.

## Findings
1. **The target reproduces.** preregistration.txt line 64: "After target: `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, exit 0." The tip run (Evidence 1) and the receipt (Evidence 3) both show this line.
2. **The stub control reproduces without the target line.** preregistration.txt lines 62–63: "the cheapest skip-the-work control (the case-8 stub as --tool) is scored by the same fixture and must NOT print the target line". Evidence 2 shows `pass=4` and rc=1. The stub source at 1efe406 only prints `garbage=0 size_garbage=0 unreachable=0 alternates=0`.
3. **Low, an attribution residual rather than a falsification: the counter moved at the instruments commit, not the after-state.** The tool as it stood at 1efe406 (`c901585c`) already scores `cases=8 pass=8 … rc=0` through the same fixture (rerun in the `ctl` clone). The after-state's 65-line diff to `tools/souji-size-census.py` (1efe406→778747e) adds:
   - an allowlisted child env
   - `/usr/bin/git` with `--no-pager --no-lazy-fetch --no-optional-locks`
   - `core.hooksPath=/dev/null`
   - a 900 s timeout
   - a top-level-only `--repo` check

   The frozen fixture measures none of these. For example, `--repo <repo>/sub` gives rc=2 (refused) with the tip tool and rc=0 (`unreachable=1`) with the 1efe406 tool, yet both score 8/8. So the receipt at 778747e attests the C1 target, but says nothing about the after-state hardening. Any claim that the hardening is counter-verified would be unsupported. I am not proposing a counter change; this is reported only as an attribution limit.
4. **Fixture discrimination spot-check (mutants in scratch, lane untouched):**
   - `m1`: `count-objects` run via `-C <path>` instead of `--git-dir=<common>`. Caught: `pass=6`. Case 3 linked shows `counts=2,2,…` and case 4 shows `counts=1,…`.
   - `m3`: an added separate `fsck --lost-found` call. Caught: `pass=6`. Cases 2 and 5 show `manifest_changed=4`, and case 2 shows `lost_found_dir=True`.
   - `m2`: `--lost-found` added to the existing `fsck --unreachable` call. Scored 8/8, but it is an **equivalent mutant**. A direct probe on git 2.56.0 shows `git fsck --lost-found --unreachable` prints `unreachable blob <oid>` and creates no `.git/lost-found`, while a plain `git fsck --lost-found` prints `dangling blob <oid>` and writes `.git/lost-found/other/<oid>`. This is not a fixture gap, though the tool's "never run" docstring claim is enforced by code text, not by git behavior. [INFERENCE: matches fsck's unreachable branch returning before the lost-found write; I did not open builtin/fsck.c this run.]

## Attack log
| # | Attack | Result |
|---|---|---|
| A1 | Tip rerun in a `--no-local` clone at ca7fc1c | survives (8/8, rc=0) |
| A2 | Stub control at 1efe406 | survives (`pass=4`, rc=1, target absent) |
| A3 | Byte diff of per-CASE lines vs both receipts | survives (identical) |
| A4 | Runner verify, lane runner and clone runner | survives (both receipts `verify=ok`) |
| A5 | Blob drift between receipt rev 778747e and tips ca7fc1c/c3ca7ad | survives (identical blobs) |
| A6 | Repeatability ×5, hostile GIT_* env, hostile HOME gitconfig, Turkish locale | survives |
| A7 | Mutants m1 and m3 | killed by the fixture; m2 is equivalent (git behavior) |
| A8 | Is the after-state needed for the target? | no: the 1efe406 tool already scores 8/8 (Finding 3, residual) |

Residual risk: the hardening introduced at 778747e is not measured by the counter (Finding 3). The `m2` path relies on git's fsck flag interaction, not on the tool's own guard. Scratch `/var/tmp/souji-r24-W2C1Rerun/` was removed before finishing.
