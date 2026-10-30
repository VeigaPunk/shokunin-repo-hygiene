# R43scout02 — C3 committed consumer pre-flight

Axes: nine-fixture coverage; pinned-byte reproducibility; leaf-symlink flip discrimination. No lane code or frozen instrument was changed. No tools installed or updated.

## Baseline table (observed)

Fixture paths below are relative to `tests/fixtures/`. Every fixture's current bytes equalled its blob at frozen commit `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373`. Tool: `tools/souji-worktree-drift.py` extracted from **619a75034dd6324e1a725f73034c59f7bf9558ef**, SHA-256 `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`.

| fixture | pinned exit | SUMMARY | json-path case? | flip-risk |
|---|---:|---|---|---|
| r36-worktree-drift.py | 0 | `SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED` | Yes: `json-inside-tree`, ordinary nonexistent leaf within measured tree (217–227). | No: no symlinked JSON leaf. |
| r37-drift-discrimination.py | 0 | `SUMMARY cases=6 pass=6 fail=0` | No; invocation has no `--json` (83–87). | No. |
| r38-drift-record.py | 0 | `SUMMARY cases=10 pass=10 fail=0` | No; invocation has no `--json` (74–122). | No. |
| r38-drift-write-envelope.py | 0 | `SUMMARY cases=12 pass=12 fail=0` | Yes: FIFO, record alias/hardlink, regular, inside tree, hardlinked output, **leaf symlink**, directory (127–258). | **YES: `json-symlink-resolved` (240–250) requires rc 0 and a written resolved target. N10 refusal would make this fail.** |
| r39-drift-record-rules.py | 0 | `SUMMARY cases=7 pass=7 fail=0` | No `--json`; outside-root traversal case (105–107). | No. |
| r40-drift-record-branches.py | 0 | `SUMMARY cases=8 pass=8 fail=0` | No `--json`; extra argument is only `--skip-unrecorded` (94–120). | No. |
| r41-drift-record-order.py | 0 | `SUMMARY cases=12 pass=12 fail=0` | No `--json`; root-repository/basename discovery cases (122–140). | No: no JSON target supplied, including root-specific cases. |
| r41-refusal-sites.py | 0 | `SUMMARY probes=21 pass=21 fail=0` | Yes: P10a/b, P11, P15–P18 (61–70): FIFO, directory, device, record, inside tree, hardlink, unwritable parent. | No: P02b's symlink loop is a **record** path, not `--json` (33, 53). |
| r42-drift-conditions.py | 0 | `SUMMARY cases=13 pass=13 fail=0` | Yes: regular old JSON truncation and absent JSON leaf for replacement-character case (161–190); root/gitdir sibling-prefix guards (75–90). | No: symlinked-child case (144–151) is discovery-only and passes no `--json`. |

**Pinned nonzero baseline flags: none.** All final baselines exited 0, with empty stderr.

## Finding attacking the C3 compatibility requirement

**Observed, high confidence:** `tests/fixtures/r38-drift-write-envelope.py:240–250`, symbol `run_cases`, explicitly creates a dangling leaf symlink with `os.symlink(resolved, target)`, passes that leaf as `--json`, and asserts `rc == 0`, `os.path.isfile(resolved)`, and that the resolved path itself is not a link. Its baseline receipt records `case-json-symlink-resolved=PASS`.

**Inference, high confidence:** a fix that refuses *every* leaf-symlink `--json` before existing guards with exit 2 necessarily flips that case. Therefore N10 plus all nine **unchanged** committed fixtures remaining green is incompatible at this consumer. This is a finding for L1, not a fixture/instrument fix by this seat. No candidate was run or scored here.

Definition/caller trace, textual fallback: pinned `tools/souji-worktree-drift.py:439–454` (`main`) parses `--json`, calls `run(args)`, and turns `Refusal` into exit 2. `run:283–348` establishes `root_real`, record and gitdir containment, then resolves `args.json` at line 326 before alias/containment guards; `run:419–435` writes through `open_nofollow`. Thus the old success is resolved-target writing, not O_NOFOLLOW accepting the original leaf. The fixture call chain is `main` → `run_cases` → `invoke` (fixture lines 93–102, 240–250, 279–291). LSP unavailable: `read xd://lsp` returned `No such tool: xd://lsp`; no semantic-server claims are made.

Additional consumer caveat, outside the table's leaf-only flip criterion: `r38-drift-write-envelope.py:170–207` statically checks refusal class documentation (`docstring-enum`). A new literal `raise Refusal("JSON-TARGET-SYMLINK: ...")` without the class in the module docstring would also fail that static case. This does not remove the behavioral conflict above.

## Exact execution and retained evidence

All runs used non-root UID 1000 and cwd `/fast/scratch/hyaku/souji-r43/R43scout02`. Raw per-fixture argv, environment-prefix command, exit, stdout and stderr are retained in `.ufo/waves/round-43/w1/R43scout02/<fixture>.receipt.json` (one for each table row). These seat-local receipts are evidence; scratch paths below specify reproduction commands only, not surviving evidence.

Setup was `mkdir -p /fast/scratch/hyaku/souji-r43/R43scout02/guard /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43scout02`.

Tool extraction command, executed by `subprocess.run(..., capture_output=True, check=True)` with stdout written byte-for-byte to the named scratch file:

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 619a75034dd6324e1a725f73034c59f7bf9558ef:tools/souji-worktree-drift.py
```

For every fixture in the table, committed-byte comparison executed this command and compared its stdout bytes to the lane file (all nine comparisons printed `frozen_bytes_match True`):

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:tests/fixtures/<fixture>
```

The exact baseline command template (all nine concrete expansions are recorded in their receipts) was:

```text
TMPDIR=/fast/scratch/hyaku/souji-r43/R43scout02/<fixture-without-.py> PYTHONPATH=/fast/scratch/hyaku/souji-r43/R43scout02/guard python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/<fixture> --tool /fast/scratch/hyaku/souji-r43/R43scout02/pinned-tool.py --work /fast/scratch/hyaku/souji-r43/R43scout02/<fixture-without-.py>
```

Commands ran concurrently with `ThreadPoolExecutor(max_workers=9)`, capturing stdout/stderr. `TMPDIR` and `--work` were explicitly set per invocation. The original fixture drivers were not edited. To enforce the assignment's Git safety requirement, scratch-only `sitecustomize.py` guarded fixture `subprocess.run`: `git init PATH` became `git -C PATH init` after creating that directory; before add/commit/worktree mutation it asserted `git -C PATH rev-parse --show-toplevel == realpath(PATH)` and scratch containment. Git identities remained in fixtures' per-command environments, never exported. The retained exact guard source is `.ufo/waves/round-43/w1/R43scout02/guard.py.txt`.

Initial guard attempts are **not baselines**: an overly broad check also guarded read-only `worktree list`, and the first init rewrite omitted directory creation. Initial receipts are preserved as `<fixture>.initial-guard.receipt.json`: r36 exited 1 (`11/12`), r42 exited 1 (`0/13`, init errors), others exited 0. Correcting only that scratch guard and rerunning the nine identical fixture commands produced the table above. This distinguishes harness errors from pinned-tool failures.

**Verdict:** baseline surface is green; exactly one existing behavioral case requires acceptance of the JSON leaf symlink N10 intends to refuse. Remaining unknown: how L1 will reconcile that frozen compatibility conflict. All scratch files are removed before handoff; retained artifacts are confined to this seat's report and directory.
