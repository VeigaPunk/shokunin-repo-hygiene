# S44executor36 — C3 regular-positive output-envelope probe

## Scope and evidence

- Axis: coverage (independent regular-positive arm for the `--json` output envelope).
- Read-only contract: `tools/souji-worktree-drift.py` module docstring lines 37–63 documents `--json OUT` and refusal classes; lines 53–63 include `JSON-INSIDE-MEASURED-TREE`, `JSON-IS-RECORD`, `JSON-NOT-REGULAR`, `JSON-HARDLINKED`, `JSON-TARGET-SYMLINK`, and `JSON-UNWRITABLE`. Its implementation writes the JSON after refusal checks (code lines 320–362, 430–447 in the inspected frozen file).
- Read-only fixture: `tests/fixtures/r38-drift-write-envelope.py` lines 23–30 names `json-written-regular`; lines 85–104 synthesize a one-repo fake fleet and invoke the actual tool; lines 211–223 assert `--json` outside measured trees yields valid JSON with `summary.record_repos == 1`.
- Candidate byte hashes copied from the two requested revisions using `git show` (no checkout or git mutation): base `55d7af6f5a22340f7a3de1c386e514ababfaa75f` = `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`; frozen candidate `d314fd6e85d62565344fa6c4b102f52f62297884` = `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d`.

## Bounded checks

Harness: seat-local `probe.py` imported the read-only r38 fixture's `fleet()` and `invoke()` helpers; created one synthetic git repo/record per run under seat scratch; called `python3 -B <tool> --root <fake-fleet> --record <record> --timeout 30 --json <regular-output-outside-root>`. It checked exit status, timeout, decoded JSON shape and one recorded repo, unchanged input record, unchanged files under the measured repo, and that the output is outside that repo. Both commands were run from the fleet root and wrote only under the assigned seat scratch/output paths.

Exact command (frozen):

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44executor36/probe.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-write-envelope.py /fast/scratch/hyaku/souji-r44/S44executor36/frozen2 /fast/scratch/hyaku/souji-r44/S44executor36/frozen-tool.py
```

Observed stdout:

```text
CASE regular-positive rc=0 hung=False elapsed=0.043s json_exists=True json_valid=True record_repos=1 summary={'drift_rows': 0, 'live_prunable': 0, 'live_regs': 1, 'live_repos': 1, 'record': '/fast/scratch/hyaku/souji-r44/S44executor36/frozen2/regular-positive/record.tsv', 'record_prunable': 0, 'record_regs': 1, 'record_repos': 1, 'unreachable': 0}
RECORD_UNCHANGED=True REPO_FILES_UNCHANGED=True JSON_OUTSIDE_REPO=True
STDOUT 'SUMMARY record=/fast/scratch/hyaku/souji-r44/S44executor36/frozen2/regular-positive/record.tsv record_repos=1 record_regs=1 record_prunable=0 live_repos=1 live_regs=1 live_prunable=0 drift_rows=0 unreachable=0\n'
RESULT PASS
```

Exact command (base):

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44executor36/probe.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-write-envelope.py /fast/scratch/hyaku/souji-r44/S44executor36/base2 /fast/scratch/hyaku/souji-r44/S44executor36/base-tool.py
```

Observed stdout:

```text
CASE regular-positive rc=0 hung=False elapsed=0.048s json_exists=True json_valid=True record_repos=1 summary={'drift_rows': 0, 'live_prunable': 0, 'live_regs': 1, 'live_repos': 1, 'record': '/fast/scratch/hyaku/souji-r44/S44executor36/base2/regular-positive/record.tsv', 'record_prunable': 0, 'record_regs': 1, 'record_repos': 1, 'unreachable': 0}
RECORD_UNCHANGED=True REPO_FILES_UNCHANGED=True JSON_OUTSIDE_REPO=True
STDOUT 'SUMMARY record=/fast/scratch/hyaku/souji-r44/S44executor36/base2/regular-positive/record.tsv record_repos=1 record_regs=1 record_prunable=0 live_repos=1 live_regs=1 live_prunable=0 drift_rows=0 unreachable=0\n'
RESULT PASS
```

## Finding, limits

Both base and frozen candidate write a valid JSON output for this regular, external output path, exit 0 without hanging, report one repository, and preserve the input record and measured repository files. Therefore the r44 leaf-symlink refusal cutover does **not** affect this regular-positive case; it only changes handling for a symlink leaf, a distinct negative case. This probe does not establish behavior for symlink targets, other refusal classes, or races, and is not a full r38/r44 fixture run. No tools installed or updated.
