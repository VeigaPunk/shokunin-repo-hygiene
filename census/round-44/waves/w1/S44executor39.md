# S44executor39 — C3 output-envelope probe

Axes: calibration / operability / coverage. Result: frozen candidate refuses `--json` leaf symlink before writing through it; base `55d7af6` resolves/writes the symlink target. Cutover affects this case, preventing unintended target write. r38 fixture candidate results: 12/12 PASS; base `json-symlink-refused` fails behaviorally.

Evidence, command, full exact stdout, revision identifiers, tool/fixture SHA-256 hashes, scope, and limits: [`S44executor39/report.md`](S44executor39/report.md). Probe invoked actual extracted `tools/souji-worktree-drift.py` snapshots with `tests/fixtures/r38-drift-write-envelope.py`; fixture builds fake repositories in the designated scratch. No tool install. No production files changed.
