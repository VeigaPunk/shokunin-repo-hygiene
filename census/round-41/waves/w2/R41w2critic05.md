# R41w2critic05 — falsify R1 (record-order fixture) at tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f

Role: critic. Scope: `tests/fixtures/r41-drift-record-order.py` (blob at 97eeb01aa4a8, landed) against the pinned tool
`tools/souji-worktree-drift.py` (sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6) and the base tool
`git show 7eebc183f2685d1ea9b004b4de22c09a8a4035a7:tools/souji-worktree-drift.py` (sha256 e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76).
Only behavioural difference pinned vs base: `git diff 7eebc18 1d41c13 -- tools/souji-worktree-drift.py` is 9 insertions / 2 deletions, confined to
the TOTAL loop (`totals` list, line 171, and `for total in totals:`, line 176). Everything else (root discovery, repo_path, measure) is identical.
Fixture sha256 a2880a91410611c7ed8bd6c472957f88745e3c61d9044e1ba3ff53386a47d234 (matches counter `fixture_sha=a2880a914106`).

Receipts (copied to `.ufo/waves/round-41/w2/R41w2critic05/receipts/`, checksums in `receipts/SHA256SUMS.txt`): all scripts, all output files,
the base tool copy (`receipts/base-tool.py`), the pinned copy, the fixture snapshot, and `receipts/mutants/`. Scripts reference the scratch
copy of the base tool (`/fast/scratch/hyaku/souji-r41/R41w2critic05/base-tool.py`), which is deleted after this report; use `receipts/base-tool.py`.

## 1. The R1 fixture on both tools

Command: `python3 -B tests/fixtures/r41-drift-record-order.py --tool <tool> --work /fast/scratch/hyaku/souji-r41/R41w2critic05/fx-*`

- pinned: `case-*=PASS` x12, `SUMMARY cases=12 pass=12 fail=0`, exit 0.
- base: `SUMMARY cases=12 pass=7 fail=5`, exit 1. Failing: total-first-bad-repos, total-first-bad-regs, total-first-bad-prunable,
  total-middle-bad, total-before-rows-then-bad (base accepts rc=0). Only total-agreeing-pair and the six root cases pass on base.
  So the TOTAL arm discriminates the fix; the root arms do not (identical on both tools, as expected from the diff).

Fixture coverage shape (verified by reading the bodies): in every disagreeing-TOTAL case the disagreeing row is NOT the last TOTAL row
(the last row is always GOOD). Only 2-TOTAL and 3-TOTAL records; no 4+.

## 2. Differential testing, pinned vs base, plus an independent oracle

Oracle (in `diff_total.py`): refuse iff malformed line, no REPO rows, duplicate REPO, or ANY TOTAL row disagrees (pinned rule).
Base rule: refuse iff the LAST TOTAL row disagrees.

a) Random records (`diff_total.py WORK 400 SEED`, seeds 1,2,3; 1200 records; plain root and a root that is a `.git`-DIR repo; random
   TOTAL count 0-4, random order, random comments, random perturbation of one TOTAL field, random `--skip-unrecorded`):
   - pinned rc agrees with oracle on 1200/1200; base rc agrees with base-oracle on 1200/1200; tracebacks 0.
   - differing records: 129 + 122 + 148 = 399. All are the expected class (a non-last TOTAL decides). UNEXPECTED: 0.
     Seed 1: `STATS {'runs': 400, 'same': 271, 'differ_expected': 129, 'differ_unexpected': 0, ...}`; seed 2: same 278 / 122 / 0; seed 3: same 252 / 148 / 0.

b) Exhaustive TOTAL-pattern sweep (`exhaust_total.py`): every sequence of 2 and 3 TOTAL rows over {good, repos-wrong, regs-wrong, prunable-wrong},
   all interleavings with 2 REPO rows: 80 patterns, 736 records, tracebacks 0.
   - 504 records differ, in 54 pattern classes:
     - class A (18 patterns): base accepts (rc 0), pinned refuses (rc 2). Last TOTAL good, an earlier one bad.
     - class B (36 patterns): both refuse (rc 2), different TOTAL field named (pinned names the first bad TOTAL, base the last).
   - pinned rc = 2 on every one of the 504 differing records (oracle-correct); no record where pinned accepts and base refuses.
   - Of the 54 classes, only 5 are asserted by a fixture case (`R.`, `g.`, `P.`, `.g.`, `.R.`; the case bodies are at
     fixture lines 110-121). **49 of the 54 differing classes have no case asserting them**, including every class where the disagreeing
     TOTAL is at index 0 of 3 or the last TOTAL is the one that decides (e.g. `P..`, `R..`, `.P.`, `RR.` family, `PR.`, `gR.`).
     Pinned is oracle-correct on all of them, so these are coverage gaps, not pinned defects.

c) Root variants (`probe.py`, `probe2.py`, `diff_fileroot.py`): `.git`-dir root (named / unnamed / skip), `.git`-FILE root with gitdir
   inside root (`git init --separate-git-dir`), `.git`-FILE root with gitdir outside root, and a `.git`-FILE child (control).
   Random records against the `.git`-FILE root: `STATS {'runs': 150, 'identical': 111, 'differ_total_class': 39, 'differ_other': 0, 'tracebacks': 0}`.

## 3. Findings

### F1 — a surviving TOTAL mutant that R1 alone does not kill (`all-but-last`, `totals[:-1]`)
`mutate.py` builds TOTAL-loop mutants. Results (`receipts/mutant-matrix.txt`):
- `mut-all-but-last` vs r41 fixture: **12/12 PASS** (survives). vs r40: 2 fail (killed). vs r39: 7/7 (survives). vs r36: 11/12 (killed). vs r38-record: 7/10 (killed). vs r38-write-envelope: 12/12 (survives).
- So the r41 fixture's own claim ("every TOTAL row is checked against the REPO rows, wherever it sits") is only backed for
  non-last positions. A last-position disagreeing TOTAL is killed by r40, r36 and r38-record, never by R1's own cases.

### F2 — a surviving TOTAL mutant that NO committed fixture kills (`last-two`, `totals[-2:]`)
- `mut-last-two` survives every committed fixture that uses `--tool` (r36 12/12, r37-discrimination 6/6, r38-record 10/10, r38-write-envelope 12/12, r39 7/7, r40 8/8, r41 12/12; `receipts/mutant-matrix.txt`). Only a record with
  three or more TOTAL rows and a disagreeing TOTAL at index <= n-3 distinguishes it.
- Exact record (`receipts/last-two-and-d2.txt`, run in `/fast/scratch/.../p3`): `REPO alpha`, `REPO beta`, `TOTAL repos=1 regs=2 prunable=0`, `TOTAL repos=2 regs=2 prunable=0`,
  `TOTAL repos=2 regs=2 prunable=0`, run with `--skip-unrecorded`:
  - pinned: `REFUSAL RECORD-MALFORMED: TOTAL repos=1 but 2 REPO rows`, rc=2
  - mut-last-two: `SUMMARY ... drift_rows=0`, rc=0
- The r1-counter M19 mutant is `totals[-1:]` only; neither `all-but-last` nor `last-two` is in its mutant table, so the counter
  cannot see this gap.

### F3 — root `.git` FILE: named root reads ABSENT, unnamed root is silently skipped (pre-existing; identical on pinned and base)
Probe (`probe.py` section B2, `probe2.py`): root created with `git init --separate-git-dir <root>/.store <root>`, so `<root>/.git` is a FILE.
`git -C root rev-parse --is-inside-work-tree` → `true`; `git worktree list --porcelain` lists it. Child `alpha` (also a FILE) is measured correctly (control D2: `drift_rows=0`).
- Record names the root basename: pinned and base both print `DRIFT ABSENT seproot recorded regs=1`, rc=1, `live_repos=1`. A live work tree
  reads ABSENT (the docstring defines ABSENT as "not a git work tree now"). 53 of 150 random records with the root named (`diff_fileroot.py`) show this.
- Record does not name root, `--skip-unrecorded` absent: `drift_rows=0`, rc=0. The docstring promises UNRECORDED for "a git work tree under --root the record does not name".
- Cause: `repo_path` line 212 (`os.path.isdir(os.path.join(root, ".git"))`) and `discover` line 233 (`os.path.isdir(...)`) test the root with `isdir` only,
  while the child branches (lines 210, 231) accept `isfile`. Base has the same lines.
- Coverage: no committed fixture uses a root `.git` FILE (grep of tests/fixtures/*.py: the only `gitdir:` writes are for child `alpha`/broken children).
  R1's docstring says "a --root that is a git work tree", which this variant is, so R1's root-arm claim is broader than its fixture.
- Not introduced by the R1 change, so it does not harm an axis; it is a routed defect for the next round, and it is a coverage hole for R1.

### F4 — hermeticity (fixture)
Run and passing (12/12 each): cwd `/` (absolute work), cwd = scratch with relative `--work` and absolute tool, cwd = lane with relative tool path and work outside lane,
4 concurrent instances sharing one `--work` (all 12/12, zero leftover dirs), stale planted `souji-r41-order.*` tree (`stale tree untouched`, sha-stable), `TMPDIR=/nonexistent`
plus `GIT_DIR`/`GIT_WORK_TREE` pointing at the lane and a `GIT_CONFIG_COUNT` injection (fixture ENV whitelist neutralises all of them), umask 077/0022/0002, three sequential runs.
- umask 0277 and a read-only `--work` (chmod 500): uncaught `PermissionError` traceback, process exit 1 — the same exit code as a mismatch. Setup failure is not reported as
  "could not evaluate" (exit 2). The r1-counter kill test needs a `SUMMARY` line and no traceback, so it is not fooled; a human reading the exit code would be.
  Minor; not a claim defect.
- `r37-drift-escapes.py` does not accept `--tool` (exits 1 on pristine with `control=NO-BASE-TOOL`); it was not usable for mutant scoring and I did not rely on it.

### Committed counter (confirms the frozen numbers, no new defect)
`python3 -B census/round-41/r1-counter.py --root <lane> --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch <scratch>`:
`SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106`, exit 0.
(receipt: `receipts/r1c-run.txt`). The counter target is met; F1 and F2 are outside its mutant table.

## 4. Verdict

- Correctness of the pinned TOTAL rule: **holds** on 1200 random + 736 exhaustive records (zero oracle disagreements, zero unexpected differences from base,
  zero tracebacks). No pinned record was found on which pinned is wrong.
- R1 coverage claim ("every TOTAL row checked wherever it sits"; "root in discovery" for any git work tree): **partially falsified**.
  - F1: R1's own cases do not kill the all-but-last mutant (killed only by r40).
  - F2: the last-two mutant survives every committed fixture; 49 of 54 differing TOTAL classes are unasserted.
  - F3: a `.git`-FILE root is unasserted and misreported (pre-existing, routed).
- Hermeticity: **holds** for cwd, concurrency, stale scratch, env injection; setup failures exit 1 with a traceback (minor).

Recommended for the L1/integrator (not applied here; seats never edit the lane): add a fixture case with a disagreeing LAST TOTAL row and a
3-TOTAL case with the disagreeing row at index 0 (so `all-but-last` and `last-two` both die), and either add the `.git`-file root arm or narrow the
docstring to "a git work tree whose `.git` is a directory". F3 belongs to a routed defect for repo_path/discover.

Tools installed: none. Lane writes: none (`git --no-optional-locks status --porcelain` clean after all runs; the counter ran against `--rev`, read-only).
Scratch: /fast/scratch/hyaku/souji-r41/R41w2critic05 (deleted after receipts were copied).
