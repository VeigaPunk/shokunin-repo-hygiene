# ExecCoverageFixture — round 24 wave 1, C2 fixture draft

## Status
STATUS: PASS — fixture draft delivered. It scores a scratch reference tool 9/9, rejects the always-zero control (0/9), and kills 10 out of 10 targeted mutants. Scratch has been removed.

## Delivery
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-24/w1/r24-coverage-agreement.py` (368 lines, sha256 `42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44`). The L1 copies it to `tests/fixtures/r24-coverage-agreement.py`.
- CLI: `python3 -B tests/fixtures/r24-coverage-agreement.py --tool <path>`. It uses one `tempfile.mkdtemp(dir="/var/tmp", prefix="souji-r24-coverage-")`, removed in `finally` and on SIGINT/SIGTERM/SIGHUP. `git init/add/commit` run only inside the scratch, with GIT_CONFIG_GLOBAL/SYSTEM=/dev/null and every `GIT_*` env var stripped. The tool runs as `python3 -B <tool> --root <case-repo> --rev <full40>` with cwd set to the scratch root, so the tool must honour `--root`.
- Output: one `case=` line per case (expected and observed values), then one `control case=` line per case, then the last line `cases=C pass=P control=FALSE-GREEN-REJECTED|FALSE-GREEN-ACCEPTED`. Exit codes: 0 iff P==C and the control is rejected; 1 otherwise; 2 on a usage error. If the tool file is absent, every case scores FAIL (`TOOL-ABSENT`); the case is not run, so a missing file cannot pass case 9 through python's own exit 2.

Each case asserts:
- exactly one counts line;
- `grounded`, `dangling` and `mismatches` equal the expected values;
- the multiset of MISMATCH (class, basename of path) pairs matches;
- the number of rows equals `mismatches`, and the DANGLING rows equal `dangling`;
- exit 0 when mismatches==0, and non-zero (not a timeout) otherwise.

Cases (each repo's base holds `a-f2.md` grounded F2 and `b-f3.md` grounded F3, mapped in an `entries` table and an `entries / runnable evidence` table; the F2 status cell carries an escaped `\|`, copied from README:40):

| n | name | expected | extra decoys inside the case |
|---|---|---|---|
| 1 | clean-map | grounded=2 dangling=0 mismatches=0 exit 0 | `--rev` is commit 1; HEAD (commit 2) adds an unmapped grounded entry, which catches a tool that reads HEAD |
| 2 | missing-from-map | MISSING-FROM-MAP c-f2.md, 1 | c-f2.md is named in two non-map tables (header3 `notes`; header1 `round`) |
| 3 | status-column-only | MISSING-FROM-MAP c-f2.md, 1 | — |
| 4 | other-ground-row | MISSING-FROM-MAP c-f2.md, 1 | the F2 entry appears only in the F3 row's entries cell |
| 5 | dangling-map-path | DANGLING-MAP-PATH ghost.md, 1 | a missing `knowledge/ghost-status.md` in a status cell and a missing `../tools/absent-tool.py` in an entries cell are both not counted |
| 6 | ground-token | grounded=7, MISSING-FROM-MAP d-f2.md, 1 | `F2 caveat, …` counts as F2; `F21 …` does not; `F1-jj …` counts as F1; a bare `F7` cell counts; an entry grounded F21 is satisfied by the F21 row |
| 7 | worktree-fix-uncommitted | MISSING-FROM-MAP c-f2.md, 1 | the fix is in both the working tree and the index; `--rev` is HEAD |
| 8 | ungrounded-entry | grounded=2 mismatches=0 exit 0 | one entry has no ground line; one has `ground: core — receipts` |
| 9 | rev-not-full40 | exit 2 for each of: 12-hex prefix, `HEAD`, 39-hex + `z` | — |

## Evidence
All commands below ran this session in `/var/tmp/souji-r24-ExecCoverageFixture` (since removed), on git 2.56.0 and Python 3.14.8. The lane HEAD was `f9db2181647d91470a724a12d626bd6106805076`.

1. `python3 -B <fixture> --tool ref-tool.py` (scratch reference, written to the C2 text):
```
case=1 name=clean-map expect: grounded=2 mapped=* dangling=0 mismatches=0 rows=[none] exit=0 ; got: grounded=2 mapped=2 dangling=0 mismatches=0 rows=[none] exit=0 -> pass
case=2 name=missing-from-map expect: grounded=3 mapped=* dangling=0 mismatches=1 rows=[MISSING-FROM-MAP:c-f2.md] exit=nonzero ; got: grounded=3 mapped=2 dangling=0 mismatches=1 rows=[MISSING-FROM-MAP:c-f2.md] exit=1 -> pass
case=3 name=status-column-only expect: grounded=3 mapped=* dangling=0 mismatches=1 rows=[MISSING-FROM-MAP:c-f2.md] exit=nonzero ; got: grounded=3 mapped=2 dangling=0 mismatches=1 rows=[MISSING-FROM-MAP:c-f2.md] exit=1 -> pass
case=4 name=other-ground-row expect: grounded=3 mapped=* dangling=0 mismatches=1 rows=[MISSING-FROM-MAP:c-f2.md] exit=nonzero ; got: grounded=3 mapped=2 dangling=0 mismatches=1 rows=[MISSING-FROM-MAP:c-f2.md] exit=1 -> pass
case=5 name=dangling-map-path expect: grounded=2 mapped=* dangling=1 mismatches=1 rows=[DANGLING-MAP-PATH:ghost.md] exit=nonzero ; got: grounded=2 mapped=2 dangling=1 mismatches=1 rows=[DANGLING-MAP-PATH:ghost.md] exit=1 -> pass
case=6 name=ground-token expect: grounded=7 mapped=* dangling=0 mismatches=1 rows=[MISSING-FROM-MAP:d-f2.md] exit=nonzero ; got: grounded=7 mapped=6 dangling=0 mismatches=1 rows=[MISSING-FROM-MAP:d-f2.md] exit=1 -> pass
case=7 name=worktree-fix-uncommitted expect: grounded=3 mapped=* dangling=0 mismatches=1 rows=[MISSING-FROM-MAP:c-f2.md] exit=nonzero ; got: grounded=3 mapped=2 dangling=0 mismatches=1 rows=[MISSING-FROM-MAP:c-f2.md] exit=1 -> pass
case=8 name=ungrounded-entry expect: grounded=2 mapped=* dangling=0 mismatches=0 rows=[none] exit=0 ; got: grounded=2 mapped=2 dangling=0 mismatches=0 rows=[none] exit=0 -> pass
case=9 name=rev-not-full40 expect: exit=2 for --rev in ['d42791e10f4d', 'HEAD', 'd42791e10f4dd237d13b1b4717dc5e260daf731z'] ; got: exits=[2, 2, 2] -> pass
control case=1 got: grounded=0 mapped=0 dangling=0 mismatches=0 rows=[none] exit=0 -> FAIL
  ... (control cases 2-8 identical shape, all FAIL)
control case=9 got: exits=[0, 0, 0] -> FAIL
cases=9 pass=9 control=FALSE-GREEN-REJECTED
fixture_exit=0
```
After the run, `ls -d /var/tmp/souji-r24-coverage-*` found 0 entries, so the fixture removed its own scratch.

2. Mutants: each one is the scratch reference with a single edit. The table gives the fixture's last line and the cases that failed.

| mutant | last line | failing cases |
|---|---|---|
| m1 reads HEAD instead of `--rev` | `cases=9 pass=8` | 1 |
| m2 reads README from the working tree | `cases=9 pass=8` | 7 |
| m3 naive split on every pipe | `cases=9 pass=1` | 1–8 |
| m4 ground cell `^F(\d)` with no boundary | `cases=9 pass=8` | 6 |
| m5 no 40-hex shape check | `cases=9 pass=8` | 9 (exits=[0, 0, 2]) |
| m6 scans the status column as well | `cases=9 pass=7` | 3, 5 |
| m7 accepts a row of any ground | `cases=9 pass=7` | 4, 6 |
| m8 counts any backticked path as dangling | `cases=9 pass=2` | 1–3, 5–8 |
| m9 ignores the third header cell | `cases=9 pass=8` | 2 |
| m10 boundary `-` or end of cell only | `cases=9 pass=1` | 1–8 |

Every mutant run exited 1. With the always-zero emitter as `--tool`, the last line was `cases=9 pass=0 control=FALSE-GREEN-REJECTED` (exit 1). With an absent tool path, it was `cases=9 pass=0 control=FALSE-GREEN-REJECTED` (exit 1). With no arguments, argparse printed `error: the following arguments are required: --tool` (exit 2).

3. The scratch reference run read-only on the lane (`git ls-tree`/`git show` only) gave the same result at both revisions:
```
== rev=a65fac98964b445758e94c805728c9a19d302ff8
MISMATCH	MISSING-FROM-MAP	corpus/knowledge/count-objects-garbage-readings-r25.md	ground F2
MISMATCH	MISSING-FROM-MAP	corpus/knowledge/repo-size-census-readonly.md	ground F2
grounded=4 mapped=2 dangling=0 mismatches=2
== rev=f9db2181647d91470a724a12d626bd6106805076
(identical)
```
At HEAD f9db218, `git ls-tree` shows that neither `tools/souji-coverage-agreement.py` nor `tests/fixtures/r24-coverage-agreement.py` exists yet.

4. Cross-check against the peer's tool draft. I re-ran this myself after `ExecCoverageTool` reported a result: `python3 -B .ufo/waves/round-24/w1/r24-coverage-agreement.py --tool .ufo/waves/round-24/w1/souji-coverage-agreement.py` (cwd /var/tmp; tool sha256 `71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897`, fixture sha256 unchanged `42259756…`) printed `cases=9 pass=9 control=FALSE-GREEN-REJECTED` and exited 0. The observed values match the reference line for line; the tool's MISMATCH path field is `corpus/knowledge/<name>`. Afterwards there were 0 `/var/tmp/souji-r24-coverage-*` directories. The peer reports that the lane's untracked `tools/souji-coverage-agreement.py` (sha 629fbd4a) is an older draft. I did not check that copy; the L1 should score the re-copied file. The tool accepts uppercase 40-hex revs. The fixture does not test case, because the frozen text does not say whether uppercase should be refused.

## Findings
1. This is a case-3 shape in the real lane. `corpus/README.md:68` at base names the two F2 entries only in the status cell; the entries cell holds `knowledge/git-repo-structure-readonly.md` only. Verbatim from the status cell: "**r23: the read side now holds three entries** (`git-repo-structure-readonly.md`, `repo-size-census-readonly.md`, `count-objects-garbage-readings-r25.md`)". [INFERENCE] The real tool's base control should read `grounded=4 … mismatches=2`. Under the kill rule, reaching 0 means adding these names to an F2 row's entries cell; deleting or un-grounding an entry is not allowed.
2. ATTACK (undefined counter term): `mapped` is named in the C2 counts line ("grounded=G mapped=M dangling=D mismatches=X", preregistration.txt:80), but the frozen text never defines it. The fixture prints `mapped` and does not assert it, so any value passes. This is not a predicate change; it is disclosed as a residual.
3. Exit 2 for a non-40-hex rev comes from the L1 task, not the frozen C2 text: preregistration.txt:80 states only "exit 0 iff X==0". For mismatch cases the fixture accepts any non-zero exit except a timeout, because the frozen text does not pin a code.
4. Escaped pipes: the real map has backslash-escaped pipe characters inside a status cell (README:40, the F2 row's `ls corpus/knowledge … grep -ciE` sweep command). The fixture copies this into every case, so a naive cell splitter fails 8 of 9 cases (m3). The frozen text does not mention it, but the tool has to parse that file. I sent this note to `L1Souji24.ExecCoverageTool`.
5. Basename matching is ambiguous. "whose basename appears in NO entries-column cell" (preregistration.txt:83) reads as a substring test, so `a.md` would match `ba.md`. The fixture does not pin this, because no case set defines it.
6. Control label: the task wrote `ACCEPTED`; the fixture prints `FALSE-GREEN-ACCEPTED` to match the C1 counter's spelling. A smarter emitter that prints a correct `grounded` with `mismatches=0` would still fail cases 2–7, since each of them requires at least one mismatch.
7. Tool anomaly, not a lane issue: the Read tool refused 7.6 KB and 23 KB files as "exceeds maximum allowed characters (100000 characters)". I read them with `sed`/`head` instead.

## Risks / blockers
- None blocking. The scratch reference is not a delivery; the real tool belongs to `ExecCoverageTool`. No lane file was written outside the two w1 paths, there were no git or jj mutations in the lane, and no tools were installed.
- Checks for the L1 after copying: `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` (target `cases=9 pass=9 control=FALSE-GREEN-REJECTED`, exit 0), and the same command with the always-zero stub as `--tool` (expect pass=0, exit 1).
