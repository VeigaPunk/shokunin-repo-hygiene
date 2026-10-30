# S44reviewer21 — C2 h5 scoped review

Axes: calibration / operability (assigned) / coverage. No score delta or admission claimed.

**Result:** frozen scenario 5 (`h5-control-symlink-exit0-text`) passes independently derived multiset `{C1:CONTROL-SYMLINK × 1}` and tool exit 1, in both repaired r44 v2 and historical r43. The Control symlink's committed blob is present, but its `120000` mode triggers the symlink finding before parsing target text `EXIT=0` as a receipt (`tools/souji-freeze-check.py:88-90,223-237`). No actionable production defect found in this scope.

**Killed single-defect mutant:** changing only the Control-symlink finding class at checker line 229 from `CONTROL-SYMLINK` to `CONTROL-NOT-RED` leaves tool exit 1 but makes the selected v2 audit fail (audit exit 1, `SUMMARY scenarios=1 pass=0 fail=1`). Both baseline selected audits exit 0, `SUMMARY scenarios=1 pass=1 fail=0`. Historical h5 is unchanged; this does not repair or erase historical h4/h6 red.

Full independent derivation, exact commands/output, limitations, frozen input hashes, tool versions and self-evaluation: [S44reviewer21/report.md](S44reviewer21/report.md).

Retained receipts: `S44reviewer21/v2-baseline.json`, `S44reviewer21/r43-baseline.json`, `S44reviewer21/v2-mutant.json`, `S44reviewer21/frozen-sha256.json`, `S44reviewer21/mutant-change.txt`; bounded reproducible driver: `S44reviewer21/probe.py`.

**Residual risks / gaps:** only h5 exercised, not full counters/suites. Class comparison does not establish detail/SUMMARY correctness. LSP unavailable (`xd://lsp`: `No such tool`); textual checks are not semantic proof. No production changes, installs, service restarts or shared bookkeeping mutations. Existing Python 3.14.8/git 2.56.0 used. Scratch cleanup observed: `SCRATCH_REMOVED=True`. Recommendation only, no integration or admission decision.
