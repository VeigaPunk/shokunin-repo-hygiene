# S44executor27 — C3 fixture candidate

**Result:** implemented `r44-drift-symlink-refusal.py` in this seat's output directory. The fixture exercises six real subprocess cases; it does not inspect tool source. It prints one `SUMMARY cases=N pass=N fail=0` line and exits 0 only when all six cases pass.

## Axes

- **Coverage:** four leaf-symlink refusal variants (dangling target, existing file target, nested leaf, directory target) plus ordinary-leaf and symlinked-parent positive controls.
- **Operability:** CLI is `python3 -B <fixture> --tool PATH --work DIR`; each case creates an isolated temporary synthetic Git fleet under the supplied existing work directory and cleans it in `finally`.
- **Calibration:** refusal requires rc 2 and the `JSON-TARGET-SYMLINK` token; filesystem assertions check no dangling destination creation, existing victim byte preservation, and directory integrity. Positive cases require output creation and parseable JSON, or successful write through a symlinked parent.

## Evidence

Candidate command:

`python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44executor27/r44-drift-symlink-refusal.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work /fast/scratch/hyaku/souji-r44/S44executor27/work-tip`

Observed output:

```text
case-dangling-leaf-refused=PASS
case-existing-file-leaf-refused=PASS
case-nested-leaf-refused=PASS
case-directory-target-refused=PASS
case-ordinary-output-written=PASS
case-symlinked-parent-allowed=PASS
SUMMARY cases=6 pass=6 fail=0
TIP_EXIT=0
```

Always-clean control command used the same fixture with `--tool /fast/scratch/hyaku/souji-r44/S44executor27/clean.py --work /fast/scratch/hyaku/souji-r44/S44executor27/work-clean`; control prints `SUMMARY claims=1 findings=0` and exits zero. Observed result:

```text
case-dangling-leaf-refused=FAIL rc=0 output=['SUMMARY claims=1 findings=0']
case-existing-file-leaf-refused=FAIL rc=0 output=['SUMMARY claims=1 findings=0']
case-nested-leaf-refused=FAIL rc=0 output=['SUMMARY claims=1 findings=0']
case-directory-target-refused=FAIL rc=0 output=['SUMMARY claims=1 findings=0']
case-ordinary-output-written=FAIL rc=0 output=['SUMMARY claims=1 findings=0']
case-symlinked-parent-allowed=FAIL rc=0 output=['SUMMARY claims=1 findings=0']
SUMMARY cases=6 pass=0 fail=6
CLEAN_EXIT=1
```

Always-refuse control command used the fixture with `--tool /fast/scratch/hyaku/souji-r44/S44executor27/refuse.py --work /fast/scratch/hyaku/souji-r44/S44executor27/work-refuse`; it unconditionally emits the refusal token and exits 2. Observed result:

```text
case-dangling-leaf-refused=PASS
case-existing-file-leaf-refused=PASS
case-nested-leaf-refused=PASS
case-directory-target-refused=PASS
case-ordinary-output-written=FAIL rc=2 output=['REFUSAL JSON-TARGET-SYMLINK: stub refuses everything', 'SUMMARY record=stub record_repos=0 live_repos=0 drift_rows=0 unreachable=0']
case-symlinked-parent-allowed=FAIL rc=2 output=['REFUSAL JSON-TARGET-SYMLINK: stub refuses everything', 'SUMMARY record=stub record_repos=0 live_repos=0 drift_rows=0 unreachable=0']
SUMMARY cases=6 pass=4 fail=2
REFUSE_EXIT=1
```

This meets the frozen C3 counter's battery checks (`exit 0`, cases >= 6, fail=0; both controls must be rejected with rc 1 and fail>0). No tools were installed or updated. No frozen counter, production file, sibling path, shared bookkeeping, git index, or jj state was changed.

## Limitations

Only the assigned fixture and its actual-tool/negative-control behavior were exercised. No broader suite was run. The fixture checks externally observable behavior and does not claim race-hardening or guarantees beyond these path and output cases.
