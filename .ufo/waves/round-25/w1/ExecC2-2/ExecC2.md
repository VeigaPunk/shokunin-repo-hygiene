# ExecC2 (seat L1Souji25.ExecC2-2) — r25 C2 size-census fixture extension

## Status
STATUS: PASS. The draft adds frozen cases 9–12 and leaves the r24 cases 1–8 byte-identical. Results: tip tool cases=12 pass=12 rc 0; OLD 1efe406 blob 11/12 (fails case 11); r24 subset 8/8; stub control rejected.

## Draft
- `.ufo/waves/round-25/w1/ExecC2-2/r24-size-census.py`, sha256 `9c8a512f94d5682efee725dc7ed7519c127fde6a775a038ec3292374970bd528`. Integration target: `tests/fixtures/r24-size-census.py` (L1 integrates; tests/ untouched).
- What changed against the committed fixture (sha256 `373ef1f0…084f`):
  - The docstring gained 3 lines.
  - `Scratch` gained three appended methods: `invoke` (returns rc, stdout, stderr and the manifest delta), `bare`, and `commit_bare` (plumbing: hash-object, mktree, commit-tree, update-ref).
  - New top-level helpers: `tool_counts` and `describe_full`.
  - New cases `case_bare_nonempty`, `case_bare_empty`, `case_subdir` and `case_partialclone_only`, appended to `CASES` as numbers 9–12.
  - Unchanged: the control stays case 8 and the last-line format is the same.
- Case predicates, matching prereg :66–:73:
  - 9: rc==0, the last line is the counts line, stdout has the line `census.invoked_from=bare`, and the bare git-dir manifest is unchanged.
  - 10: rc==1, stderr contains `git failure` and `No default references`, and no stdout line fullmatches the counts regex.
  - 11: `--repo <repo>/sub`; rc==2 and stderr contains `--repo must name the repository itself`.
  - 12: `s.repo()` (init + commit) plus `extensions.partialClone=origin`. A setup guard requires no `.promisor` pack and no `remote.*` config. rc==2 and stderr contains `partial-clone repository`.
- Cases 10–12 print `manifest_changed=N` but do not gate on it, because it is not in the frozen C2 predicates.

## Evidence
All runs used git 2.56.0. Scratch was `/var/tmp/souji-r25-ExecC2/r25/`, and each case used its own mkdtemp under /var/tmp (the fixture's `SCRATCH_PARENT`, removed in `finally`). Receipts are in `.ufo/waves/round-25/w1/ExecC2-2/receipts/`. They are not in `ExecC2-receipts/`, which a concurrent `ExecC2` seat also writes to (see Findings 4).

| arm | tool (sha256) | last line | rc | receipt |
|---|---|---|---|---|
| green | tools/souji-size-census.py (`c5690681…6eb3`) | cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED | 0 | c2-green.tsv |
| red | 1efe406:tools/souji-size-census.py (`7ad5cc76…4578`) | cases=12 pass=11 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED | 1 | c2-red.tsv |
| regressed (extra) | 778747e:tools/souji-size-census.py (`09bb8e0d…ed6d`) | cases=12 pass=10 … | 1 | c2-regressed.tsv |
| stub (extra) | stub emitter (`eb8d67e0…96d1`) | cases=12 pass=4 control=FALSE-GREEN-REJECTED … | 1 | c2-stub.tsv |
| subset | committed fixture on tip tool | cases=8 pass=8 …; CASE 1–8 lines diff-identical to the draft's | 0 | c2-subset.tsv |

Commands, with F=`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-25/w1/r24-size-census.py`:
- green: `python3 -B $F --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-size-census.py` → rc 0. Excerpt: `CASE 9 bare-nonempty PASS exit=0 counts=0,0,0,0 manifest_changed=0 invoked_from_bare=True`, `CASE 10 bare-empty PASS exit=1 … stderr_no_default_references=True stdout_counts_line=False`, `CASE 11 subdir PASS exit=2 …`, `CASE 12 partialClone-only PASS exit=2 …`.
- red: `python3 -B $F --tool <git show 1efe406e7f39b8fe736be2a566053703a571ffc0:tools/souji-size-census.py>` → rc 1. The failing case is `CASE 11 subdir FAIL exit=0 counts=0,0,0,0 manifest_changed=0 stderr_must_name_repo=False`: the old blob censuses the enclosing repo. Cases 9, 10 and 12 PASS.
- regressed: `CASE 9 bare-nonempty FAIL exit=2 … invoked_from_bare=False` and `CASE 10 bare-empty FAIL exit=2 …`. This is the R24-M24 bare-refusal regression.
- subset: `diff <(grep -E '^CASE [1-8] ' green.out) <(grep -E '^CASE [1-8] ' base-green.out)` → empty (SUBSET-IDENTICAL), and 8 CASE 1–8 PASS lines.
- byte-identity: an AST source-segment compare of the committed fixture against the draft. `Scratch` (original body contained), `scratch`, `manifest`, `resolve_alternates`, `changed`, `describe`, `case_clean` … `case_control`, `run`, `precondition` and `main` are all IDENTICAL. The only removed lines are docstring line 1, docstring line 7 and the closing line of the `CASES` list.
- Revisions: lane HEAD was `6e4737e` at start and `1814de557f76cf0a199fd062247b47c0b791f5e4` when the receipts were written. The 1814de5 commit (prereg amendment 1 + receipts) touches neither the tool nor the fixture.

## Findings
1. The red arm discriminates on subdir, not on the bare cases. prereg :80 says "fixture must fail >=1 of cases 9–12 (the bare cases discriminate)". Against 1efe406, cases 9 and 10 PASS and only case 11 FAILs. The bare cases discriminate the 778747e blob (cases 9 and 10 FAIL), not the named OLD blob. The ">=1 of 9–12" predicate is still met, so only the parenthetical is wrong.
2. Case 12 is constructed with a commit (`s.repo()`), not a bare `git init`. Without the refusal, the tool would then exit 0 with a counts line, instead of exit 1 on `No default references`. That keeps the rc==2 discrimination from being satisfied by a coincidental fsck failure. Prereg :72 reads "init + `extensions.partialClone=origin` config"; [INFERENCE] the commit is within "init".
3. The pre-amendment base receipt was non-verbatim. At 6e4737e, `census/round-25/records/c2-control-base.tsv` showed `CASE 2 … counts=0,0,0,0` and `CASE 6 … counts=None … promisor_unset[exit=0 …]`, both as PASS. The fixture code prints lowercase `none`, and `case_refusal` requires `code_c == 2`, so those bytes could not come from that fixture. At 1814de5 the file was replaced with output that matches my own base run (`counts=0,0,1,0`; `promisor_unset[exit=2 counts=none …]`). Resolved; noted for the lesson.
4. A path collision occurred. Another seat registered as `ExecC2` (swarm-registry.json :80) works concurrently in `/var/tmp/souji-r25-ExecC2/` (files from 09:28–09:30 that I did not create) and in `w1/ExecC2-receipts/` (`c2-mid.tsv` and a fixture copy with sha256 `5bd7e74f…4238`). At 12:32 UTC the ExecC2 seat asked over IRC that a duplicate holder use a distinct path. I moved my draft, report and receipts to `w1/ExecC2-2/`; the draft sha256 was unchanged by the move. The receipts' `fixture=` and `cmd=` fields still show the pre-move path `w1/r24-size-census.py`, and their recorded `fixture_sha256` identifies the same bytes. I left its files untouched, and messaged L1Souji25 and ExecC2.

5. The two drafts were written independently and their results agree. The ExecC2 seat's draft is `w1/r24-size-census.py`, sha256 `5bd7e74f…4238`, with receipts in `w1/ExecC2-receipts/`. Over IRC at 12:35 UTC it reported tip 12/12 rc 0, 1efe406 11/12 failing only case 11, 778747e 10/12 failing cases 9 and 10, and the stub 4/12. Those are the same per-case verdicts as mine. It also raised Findings 1 and 2 on its own. Either draft can be integrated by hash. My seed copy to `w1/r24-size-census.py` at 09:29 local may have overwritten an earlier ExecC2 write there. ExecC2 has since restored its version, and no bytes of either draft were lost.

## Attack log
- A1, against the prereg wording (Finding 1): "the bare cases discriminate" is false for the named red-arm blob 1efe406. If L1 wants the bare cases to be red-witnessed, the 778747e receipt (`c2-regressed.tsv`) is the witness. The frozen predicate is unchanged.
- A2, a gap in the counter: cases 10–12 do not gate on the no-write manifest. A tool that refused correctly but wrote to the git dir would still pass them. Case 6 does gate on `not delta`. Disclosed, not changed, because adding it would re-specify a frozen predicate.
- A3, stub strength: the stub fails 8 of 12 cases (2, 3, 5, 6, 9, 10, 11, 12), and the control case 8 still checks only `CASES[1:5]`, which is unchanged.

## Housekeeping
- Tools installed: none.
- Scratch: my `/var/tmp/souji-r25-ExecC2/r25/` was removed after the receipts were written. The other files in `/var/tmp/souji-r25-ExecC2/` belong to the concurrent ExecC2 seat and were left alone.
