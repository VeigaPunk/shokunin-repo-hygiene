# S44executor29 — C3 existing-file JSON envelope probe

Axes: calibration / operability / coverage. Scope: coverage of the `--json` output envelope using only the assigned C3 legacy fixture and refusal battery. No production files or frozen counters changed. No tools installed.

## Evidence and exact commands

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`; scratch: `/fast/scratch/hyaku/souji-r44/S44executor29`.

Commands run (the `--work` directories were created first under scratch):

```sh
python3 -B "$LANE/tests/fixtures/r38-drift-write-envelope.py" --tool "$LANE/tools/souji-worktree-drift.py" --work "$PWD/current-legacy"
python3 -B "$LANE/tests/fixtures/r44-drift-symlink-refusal.py" --tool "$LANE/tools/souji-worktree-drift.py" --work "$PWD/current-battery"
git -C "$LANE" show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:tools/souji-worktree-drift.py > base-tool.py
python3 -B "$LANE/tests/fixtures/r38-drift-write-envelope.py" --tool "$PWD/base-tool.py" --work "$PWD/base-legacy"
git -C "$LANE" show d314fd6e85d62565344fa6c4b102f52f62297884:tools/souji-worktree-drift.py > frozen-tool.py
sha256sum base-tool.py frozen-tool.py "$LANE/tools/souji-worktree-drift.py"
python3 -B "$LANE/tests/fixtures/r38-drift-write-envelope.py" --tool "$PWD/frozen-tool.py" --work "$PWD/frozen-legacy"
```

Exact observed results:

- Current lane tool + r38: all 12 cases PASS; `SUMMARY cases=12 pass=12 fail=0`.
- Current lane tool + r44 battery: all 6 cases PASS (dangling leaf symlink, outside leaf symlink, subdirectory leaf symlink, symlink-to-directory refusal, regular-file write positive, symlinked parent positive); `SUMMARY cases=6 pass=6 fail=0`.
- Base `55d7af6f5a22340f7a3de1c386e514ababfaa75f` tool + r38: 11 PASS, `case-json-symlink-refused=FAIL rc=0 resolved_written=True exists=True`; `SUMMARY cases=12 pass=11 fail=1` (exit 1).
- SHA-256: base tool `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`; frozen candidate and current lane tool both `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d`.
- Frozen candidate bytes + r38: all 12 PASS; `SUMMARY cases=12 pass=12 fail=0`.

The read-only probe of the tool contract documents existing JSON destinations as refused when under `--root` or a measured repository, identical/hardlinked to the input record, non-regular, hardlinked, or a leaf symlink; valid external regular-file destinations are written. The r44 contract specifically refuses leaf symlinks before resolving them, and preserves a symlinked parent as a permitted destination path. The legacy fixture's normal regular output success and symlink refusal case provide the positive and negative `--json` checks; the r44 fixture adds the leaf/parent symlink boundary checks. Existing target preservation is directly checked by the fixture's hardlink and victim-content assertions; the symlink check asserts the link stays a symlink and resolved target is not created.

## Result, limits

Observed cutover affects this case: base revision follows and writes through a leaf symlink (`rc=0`); frozen/current candidate refuses it (`JSON-TARGET-SYMLINK`, `rc=2` per fixture contract) without writing through it. Frozen bytes exactly match the current lane tool. The assigned fixture cases passed for those bytes. This is a bounded fixture-level behavior result only; no independent whole-suite, build, lint, or additional repository checks were run. Initial attempt with a non-existent `--work` directory exited 2 (`usage: --work must name an existing directory`); created the three required directories in scratch and reran successfully. No other limitations observed.
