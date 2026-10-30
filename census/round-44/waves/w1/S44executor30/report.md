# S44executor30 — C3 dangling `--json` output-envelope probe

## Axes
- **Calibration:** paired byte-pinned base/candidate behavior on the dangling-leaf case.
- **Operability:** refusal is bounded and does not materialize/write the symlink target.
- **Coverage:** legacy envelope and dedicated six-case refusal battery exercised.

## Evidence and commands
All generated repos/tools were under `/fast/scratch/hyaku/souji-r44/S44executor30/`; no production or sibling files were written. The lane root is `/home/vgpnk/Projects/shokunin/souji-shokunin`. Frozen revision was `d314fd6e85d62565344fa6c4b102f52f62297884`; registered base was `55d7af6f5a22340f7a3de1c386e514ababfaa75f`.

Tool blob SHA-256 values (from `git show <rev>:tools/souji-worktree-drift.py | sha256sum`):
- base `55d7af6f5a22340f7a3de1c386e514ababfaa75f`: `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`
- frozen candidate `d314fd6e85d62565344fa6c4b102f52f62297884`: `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d`
- The revisions differ at the tool bytes; the frozen commit resolved exactly as requested. `git rev-parse --show-toplevel` returned `/home/vgpnk/Projects/shokunin/souji-shokunin`.

Command, with frozen candidate as `--tool` and registered base as `--base-tool`:
```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-write-envelope.py --tool frozen-tool.py --base-tool base55-tool.py --work base55-compare
```
Exact output:
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
This direct registered-base comparison demonstrates that base 55d7 resolves/writes the dangling link's target, while the frozen candidate satisfies the renamed refusal case. The historical r37 control comparison, required by the r38 fixture's own arm, also passed its registered discrimination: `base_fail=7 behavioral_fail=4`, with `json-symlink-refused` among the behavioral failures.

Dedicated probe command:
```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r44-drift-symlink-refusal.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work battery
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
```
The battery's dangling case asserts rc 2, `JSON-TARGET-SYMLINK`, and no target created; the positive regular-file and symlinked-parent cases confirm the documented success paths remain usable. The r38 frozen-candidate legacy envelope passed all 12 cases, including ordinary regular output.

The frozen C3 counter command was also run:
```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor30
```
Exact stdout/error summary:
```text
SUMMARY surface=ok tool_class=ok legacy=ok legacy_case=ok legacy_base=ok battery=ok battery_clean=REJECTED battery_refuse=REJECTED prior=4/5
```
It exited 1 because its full acceptance target requires `prior=5/5`. This is a residual counter-level blocker, not a failure of the assigned dangling/legacy-output probes. Manual prior-fixture probes exercised separately returned pass summaries for r36 (12/12), r37 discrimination (6/6), r41 (21/21), and r42 (13/13); r37 escapes also passed its registered r36 control arm (`base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`). Why the counter still reports 4/5 is not identified from its summary-only output. The counter code skips prior fixtures on live-vs-frozen digest mismatch and checks fixture-specific summaries; all five fixture hashes I compared live to frozen were identical. Do not infer the unreported failing leg from this evidence.

## Finding / scope
**The cutover affects this case:** frozen candidate refuses a dangling final-component symlink without creating/writing its target; registered 55d7 base follows the dangling link and creates/writes the target (`rc=0`). Normal regular `--json` output and a symlinked parent directory that resolves to a regular leaf still succeed in the candidate. The evidence supports the defensive caller-output contract only; it authorizes no deletion and makes no admission/closure claim.

## Limits / blockers
The assigned dangling and r38 probes passed, but the exact C3 counter remains red at `prior=4/5`; its summary does not disclose which prior arm failed. Broader suite/build/lint checks were not run. No tools were installed or updated.