# S44executor31 — C3 output-envelope probe

Axes: calibration / operability / coverage. Result: C3's leaf-symlink refusal cutover changes this case as intended; this is coverage evidence only, not admission or authorization to delete any target.

## Scope and evidence

Read `census/round-44/preregistration.txt`, `census/round-44/c3-counter.py`, `census/round-44/c3-surface.tsv`, the `tools/souji-worktree-drift.py` refusal contract (docstring lines 12–21, 53–63), and `tests/fixtures/r38-drift-write-envelope.py` (case inventory lines 14–30 and CLI lines 32–41). C3 specifies refusal of the final `--json` symlink path (`JSON-TARGET-SYMLINK`) instead of resolving/writing through it; the fixture explicitly turns `json-symlink-resolved` into `json-symlink-refused`.

Candidate = current lane tool bytes, SHA-256 `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d`. Base = `55d7af6f5a22340f7a3de1c386e514ababfaa75f:tools/souji-worktree-drift.py`, extracted with `git show` to private scratch, SHA-256 `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`.

Exact first command (from the seat scratch directory; isolated fake repositories were created by the fixture under the named private work directory):

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-write-envelope.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --base-tool /fast/scratch/hyaku/souji-r44/S44executor31/base-tool.py --work /fast/scratch/hyaku/souji-r44/S44executor31/work
```

Observed output (RC=0):

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
RC=0
```

Thus all 12 fixture cases pass for the candidate. For the 55d7 base, the same fixture's base arm establishes this symlink case fails because it follows the link and writes the resolved destination (`resolved_written=True`); it does not refuse it.

Exact reversed-arm confirmation command:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-write-envelope.py --tool /fast/scratch/hyaku/souji-r44/S44executor31/base-tool.py --base-tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work /fast/scratch/hyaku/souji-r44/S44executor31/work
```

Observed output (RC=1; expected for deliberately testing old base as candidate): all cases except symlink passed; `case-json-symlink-refused=FAIL rc=0 resolved_written=True exists=True`; `SUMMARY cases=12 pass=11 fail=1 base_cases=12 base_fail=0 behavioral_fail=0`. This independently confirms the candidate fails no base-behavioral case, while the 55d7 tool fails this specific refusal contract. In both directions the fake repositories/record and JSON-target fixtures were private; the fixture asserted whether the symlink target was unintentionally written. No real repository or measured target was supplied as the fixture repository.

## Limits

This was the requested isolated r38 output-envelope fixture, not the full C3 counter or unrelated suite. The registered counter's stronger legacy-base thresholds use the r37 blob, not the 55d7 base requested here; this result does not claim those thresholds. It also does not establish frozen revision identity from current worktree state; the candidate hash above identifies the exact bytes exercised. No tools installed.

Receipts: `r38-envelope.txt`, `base-arm.txt`.
