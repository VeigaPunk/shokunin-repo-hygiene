# S44executor40 — C3 missing-parent output-envelope probe

Axes: calibration / operability / coverage. This is coverage evidence for the `--json` output-envelope behavior; no score delta is inferred.

## Inputs and commands

Read the r44 preregistration, `tools/souji-worktree-drift.py` (frozen candidate), `tests/fixtures/r38-drift-write-envelope.py`, and the new `tests/fixtures/r44-drift-symlink-refusal.py`. The tool JSON contract documents regular-file output, refusal for non-regular/symlink targets and output/input aliases. The r38 fixture retains the 12-case legacy envelope, with its old symlink-resolved assertion explicitly replaced by `json-symlink-refused`.

Extracted byte-exact tool blobs from `55d7af6f5a22340f7a3de1c386e514ababfaa75f` and freeze `d314fd6e85d62565344fa6c4b102f52f62297884` to private scratch. Before any git operation, `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel` printed `/home/vgpnk/Projects/shokunin/souji-shokunin`.

Commands run:

```sh
python3 -B tests/fixtures/r44-drift-symlink-refusal.py --tool /fast/scratch/hyaku/souji-r44/S44executor40/freeze-tool.py --work /fast/scratch/hyaku/souji-r44/S44executor40/work
python3 -B tests/fixtures/r38-drift-write-envelope.py --tool /fast/scratch/hyaku/souji-r44/S44executor40/freeze-tool.py --base-tool /fast/scratch/hyaku/souji-r44/S44executor40/base-tool.py --work /fast/scratch/hyaku/souji-r44/S44executor40/work
```

Exact output:

```text
case-dangling-symlink-refused=PASS
case-outside-symlink-refused=PASS
case-subdir-symlink-refused=PASS
case-symlink-dir-refused=PASS
case-regular-json-written=PASS
case-parent-symlink-ok=PASS
SUMMARY cases=6 pass=6 fail=0
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

I also ran a direct missing-parent probe using `--root <scratch>/missing-parent-root --record <scratch>/record.tsv --json <scratch>/absent-parent/out.json`, with one synthetic REPO row and matching TOTAL. Exact output, first freeze candidate and then base tool:

```text
rc=2
stdout='DRIFT\tREGS-CHANGED\talpha\trecord=0 live=1\nSUMMARY record=/fast/scratch/hyaku/souji-r44/S44executor40/record.tsv record_repos=1 record_regs=0 record_prunable=0 live_repos=1 live_regs=1 live_prunable=0 drift_rows=1 unreachable=0\n'
stderr="REFUSAL JSON-UNWRITABLE: [Errno 2] No such file or directory: 'absent-parent'\n"
parent_exists=False target_exists=False
```

Both base and candidate produced exactly that missing-parent outcome: exit 2, no parent or target created, and `JSON-UNWRITABLE` refusal. Candidate byte SHA-256: `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d`; base byte SHA-256: `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`.

## Finding / limits

The tested cutover does not affect the missing-parent case; the base and freeze candidate both refuse without creating the requested path. The cutover is visible on the intended leaf-symlink case: the candidate's r38 legacy suite passes all 12 cases, while the base fails the symlink-refusal behavioral case by resolving/writing through the symlink. The r44 six-case fixture independently confirms dangling/existing/subdirectory/directory leaf-link refusal and positive regular-leaf plus symlinked-parent behavior.

This is a bounded synthetic probe, not a whole-suite verification. The r38 base arm reports only one failure here (its explicit behavioral symlink discriminator); it does not establish all preregistration base-count expectations. No tool was installed or updated. No production or shared files were modified. No scratch cleanup has yet been performed in the captured command evidence; removed below before handoff.
