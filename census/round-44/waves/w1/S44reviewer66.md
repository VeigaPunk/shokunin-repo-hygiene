# S44reviewer66 scoped findings

Full report and exact receipts: [S44reviewer66/report.md](S44reviewer66/report.md).

Result: one P2 regression. New `os.lstat` at `tools/souji-worktree-drift.py:328` catches only FileNotFoundError; non-directory and looping-symlink parents now emit an uncaught traceback/exit 1 instead of the base's JSON-UNWRITABLE refusal/exit 2. Both reproduced against frozen and base blobs. Intended leaf-refusal cutover and preserved regular/parent-symlink behavior observed. No broad source edits in assigned tool/r38 diff. No whole-suite or admission claim.
