# S44executor32 — C3 output-envelope probe

## Axes
- **Coverage:** exercises the legacy r38 output-envelope cases, including the `--json` leaf-symlink case.
- **Calibration:** compares the frozen candidate with the preregistered base `55d7af6f5a22340f7a3de1c386e514ababfaa75f`.
- **Operability:** fixture-generated isolated fake repositories and a bounded direct run; no production writes.

## Evidence
Read `census/round-44/preregistration.txt` (C3 lines 22–28), `census/round-44/c3-counter.py` (C3 contract and CLI), frozen candidate `d314fd6e85d62565344fa6c4b102f52f62297884`, and `tests/fixtures/r38-drift-write-envelope.py`. The fixture documents the changed contract at its `json-symlink-refused` case: refuse leaf symlinks with `JSON-TARGET-SYMLINK`; neither link nor target receives JSON; dangling links are also refused. Its other cases guard regular JSON success, FIFO, aliases/hardlinks, directory, measured-tree and record handling, and exact summary.

Copied source blobs to isolated scratch from the exact revisions and ran:

```sh
mkdir -p /fast/scratch/hyaku/souji-r44/S44executor32 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44executor32
# git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 55d7af6f5a22340f7a3de1c386e514ababfaa75f^{commit}
# git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse d314fd6e85d62565344fa6c4b102f52f62297884^{commit}
# both resolved respectively to the exact requested full revisions
# git show BASE:tools/souji-worktree-drift.py > tool-base.py
# git show FREEZE:tools/souji-worktree-drift.py > tool-freeze.py
# git show FREEZE:tests/fixtures/r38-drift-write-envelope.py > r38.py
sha256sum tool-base.py tool-freeze.py r38.py
```

Exact source SHA-256s:
- `tool-base.py`: `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`
- `tool-freeze.py`: `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d`
- `r38.py`: `f494d0e0caf7e7b2b55e6b389822154e022b58aca7eb4a551b1d3483a341cbc7`

Actual bounded invocation (fixture builds its temporary repository/fleet surfaces and calls each selected tool with its concrete `--json` targets):

```sh
python3 -B /fast/scratch/hyaku/souji-r44/S44executor32/r38.py \
  --tool /fast/scratch/hyaku/souji-r44/S44executor32/tool-freeze.py \
  --base-tool /fast/scratch/hyaku/souji-r44/S44executor32/tool-base.py \
  --work /fast/scratch/hyaku/souji-r44/S44executor32/work
```

Observed stdout, verbatim:

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

## Finding / limitation
The frozen tool passes all 12 cases. Specifically, the symlink refusal check observes exit 2 with the documented refusal token and intact link/absent resolved target (as encoded in the fixture assertion). The same case fails on base `55d7af6` because it exits 0 and writes the resolved target. Thus the cutover **does affect this case** and discriminates the refusal behavior. This comparison is intentionally the preregistered C3 base; it is not the `r37` base (`4c257b7…`) used by the full C3 counter's stronger `legacy_base` thresholds. The observed one base failure does not establish that counter leg. This probe does not run the full C3 battery/prior suites, does not certify admission, and does not alter frozen counters.

Scratch cleanup: the scratch directory was removed after capturing this report. No tool install or production/fleet/shared-bookkeeping edit was made.
