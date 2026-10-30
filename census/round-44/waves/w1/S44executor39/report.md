# S44executor39 — C3 output-envelope probe

## Result
Axes: calibration / operability / coverage. C3 case outcome: the frozen candidate refuses a `--json` leaf symlink before writing through it; base `55d7af6` resolves and writes the target. Thus the cutover affects this case and prevents the unintended target write. The r38 envelope suite passes all 12 candidate cases.

## Exact evidence
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`; registration: `census/round-44/preregistration.txt` (C3 base `55d7af6f5a22340f7a3de1c386e514ababfaa75f`, frozen candidate `d314fd6e85d62565344fa6c4b102f52f62297884`). Contract inspected: `tools/souji-worktree-drift.py`, `run()` JSON guard at lines 320–360 and CLI `--json` at 451–466. It uses `lstat` and emits `JSON-TARGET-SYMLINK` for an existing leaf symlink before resolving/writing. Fixture: `tests/fixtures/r38-drift-write-envelope.py`; `fleet()` creates a temporary fake repo and record, and `json-symlink-refused` invokes the actual tool with `--json <symlink>` and checks refusal, no target file, and preserved symlink.

Command (fixture and tool snapshots extracted from the stated revisions; all fixture repository writes were under the dedicated scratch):

```sh
mkdir -p /fast/scratch/hyaku/souji-r44/S44executor39 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44executor39
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:tools/souji-worktree-drift.py > /fast/scratch/hyaku/souji-r44/S44executor39/base.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:tools/souji-worktree-drift.py > /fast/scratch/hyaku/souji-r44/S44executor39/frozen.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:tests/fixtures/r38-drift-write-envelope.py > /fast/scratch/hyaku/souji-r44/S44executor39/r38.py
python3 -B /fast/scratch/hyaku/souji-r44/S44executor39/r38.py --tool /fast/scratch/hyaku/souji-r44/S44executor39/frozen.py --base-tool /fast/scratch/hyaku/souji-r44/S44executor39/base.py --work /fast/scratch/hyaku/souji-r44/S44executor39
```

Observed stdout:

```text
case-fifo-json-refused=PASS
case-fifo-json-with-reader=PASS
case-record-alias-refused=PASS
case-record-hardlink-refused=PASS
case-docstring-enum=PASS
case-json-written-regular=PASS
case-json-inside-tree=PASS
case-json-hardlinked=PASS
case-json-symlink-refused=PASS
case-json-directory=PASS
case-record-outside-root=PASS
case-summary-still-exact=PASS
base-json-symlink-refused=FAIL rc=0 resolved_written=True exists=True
BASE-BEHAVIORAL failed=1 cases=json-symlink-refused
SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=1 behavioral_fail=1
```

Tool snapshot SHA-256: base `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`; frozen `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d`. Fixture snapshot SHA-256: `f494d0e0caf7e7b2b55e6b389822154e022b58aca7eb4a551b1d3483a341cbc7`.

## Limits
This is bounded to the r38 fixture's fake single-repository surface and JSON output cases. It does not establish behavior under concurrent path replacement, broader filesystem implementations, or other tool entry points. No tools installed; no production/frozen files changed. Fixture-generated work was removed by the fixture; the seat scratch was removed after recording this report.
