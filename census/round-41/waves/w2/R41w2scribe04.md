# R41w2scribe04 — round 41 wave 2 scribe evidence report

Seat: R41w2scribe04 (role scribe, leaf member, no subagent dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Tip: `1d41c13574db80fdd9a4bde490b712da7ce2a85f` (`git rev-parse --show-toplevel` in the lane prints the lane path; working tree clean at start and end of this seat).

Deliverables:
- Scorecard draft: `.ufo/waves/round-41/w2/R41w2scribe04/scorecard-r41.md` (measurements table, capability rows, Planned (appended at round 41), owned-axis statement). `SCORECARD.md` itself was not edited; the lane has no round-41 block yet.
- Re-run receipts: `.ufo/waves/round-41/w2/R41w2scribe04/rerun/*.txt` (12 files, listed below).
- Scratch: `/fast/scratch/hyaku/souji-r41/R41w2scribe04/` was used for the reruns and deleted before this yield (`ls` after `rm -rf` reports no such file).

## Commands run and output

### 1. Lane, log and receipts state

```
git rev-parse --show-toplevel  -> /home/vgpnk/Projects/shokunin/souji-shokunin
git log --oneline -3           -> 1d41c13 round-41: measurement receipts for C1, C2, C3, R1 / 31e4d3e ... / 119c26f ...
git status --short             -> (empty)
git ls-files census/round-41/records census/round-41/controls -> c1-after.txt c2-after.txt c3-after.txt census/round-41/records/census-before.txt r1-after.txt shim-audit.txt; 8 control files
git log --format='%h %s' -- census/round-41/records/{c1,c2,c3,r1}-after.txt  -> 1d41c13 (c1), 31e4d3e (c2, c3, r1 and shim-audit.txt)
```

Landed commit chain (`git log --format='%h %s' 1d41c13 -5`): `1d41c13` receipts for C1..R1; `31e4d3e` C1 corrections lesson, S258 row, snapshots, shim audit; `119c26f` C2 tool; `97eeb01` R1 fixture; `a114412` C3 fixture. Each landing commit's stat: C2 tool +215; R1 fixture +170; C3 fixture +91; `31e4d3e` 9 files +3271.

### 2. Frozen-blob identity (`git show <rev>:<path> | sha256sum`, first 16 hex)

Identical in every row across the instrument commit `6682b98`, the freeze commit `e2a74312` and the tip `1d41c13`:

```
census/round-41/c1-counter.py   8860dc7af55848db
census/round-41/c1-items.tsv    2d2a548e253b7863
census/round-41/c2-counter.py   85ffe2638a5ed0c8
census/round-41/c2-cases.tsv    4854335abdd47942
census/round-41/c3-counter.py   9ef99e8f20805501
census/round-41/c3-sites.tsv    be363c0de5d332dc
census/round-41/r1-counter.py   8352eed44705066d
tools/souji-worktree-drift.py   b2a603cf42472b45   (full: b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6, matches preregistration Rule 1)
```

Further checks:
- `git diff --quiet e2a7431 1d41c13 -- census/round-41/controls census/round-41/c1-counter.py ... census/round-41/preregistration.txt tools/souji-worktree-drift.py` -> exit 0: "frozen-set unchanged freeze->tip".
- `git diff --quiet 6682b98 e2a7431 -- <counters, populations, tool>` -> exit 0: "counters/pops/tool unchanged instr->freeze".
- `git show --stat e2a7431` adds `census/round-41/controls/*` (8 files) and `preregistration.txt`; the controls exist at the freeze commit.
- Pinned tool at the measured commits: `tools/souji-freeze-check.py@119c26f` sha `3c3e80baedd8` (matches `tool_sha=3c3e80baedd8` in c2-after); `tests/fixtures/r41-refusal-sites.py@a114412` sha `f32022e28fe2` (matches `fixture_sha=f32022e28fe2` in c3-after); `tests/fixtures/r41-drift-record-order.py@97eeb01` sha `a2880a914106` (matches `fixture_sha=a2880a914106` in r1-after).
- Ancestry: `git merge-base --is-ancestor {119c26f,a114412,97eeb01} 31e4d3e` -> all ancestors; `31e4d3e` ancestor of `1d41c13`.
- `git diff --stat 6682b98 1d41c13 -- SCORECARD.md` -> empty; `SCORECARD.md` blob at the tip equals the blob at `6682b98` (`b0e5597319a144c2` by sha256), so no round-41 block exists yet.
- `sha256sum -c census/round-41/sources/SHA256SUMS` -> `git-v2.55.0-builtin-worktree.c: OK`, `git-v2.56.0-builtin-worktree.c: OK`.
- `git show 1d41c13:corpus/SOURCES.md | grep '^| S258 '` returns the S258 row (v2.56.0 `builtin/worktree.c`).

### 3. Counter re-runs at the measured commits (seat, 2026-10-28)

```
python3 -B census/round-41/c1-counter.py --root <lane> --rev 31e4d3e758bb903808a9270018d7e5be99ce38a4
  -> SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1 ; EXIT=0
python3 -B census/round-41/c2-counter.py --root <lane> --rev 119c26fa3bbb85e215824de9538bd2eb34e9f874 --scratch <s>/c2
  -> SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8 ; EXIT=0
python3 -B census/round-41/c3-counter.py --root <lane> --rev a1144120611b00091ac4839559d8ebf38aa9a83a --scratch <s>/c3
  -> SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f32022e28fe2 ; EXIT=0
python3 -B census/round-41/r1-counter.py --root <lane> --rev 97eeb01e73a9baa3e4191b9052fed9e505c70215 --scratch <s>/r1
  -> SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106 ; EXIT=0
```

Each line equals the corresponding `census/round-41/records/*-after.txt` SUMMARY line (exact string match, trailing spaces stripped). Two earlier attempts failed for seat-side reasons and were redone, not counted: the first batch used an unset shell variable and wrote to `/`, and the second passed a `--scratch` path that did not exist yet (`REFUSAL COULD-NOT-EVALUATE: --scratch (or TMPDIR) must name a directory`, rc 2). Both were fixed by setting the paths explicitly and creating the scratch subdirectories.

### 4. Do-nothing controls re-run at the instrument commit `6682b98175b995ee4646ffd1ea6bd8a12cd353dd`

```
c1-counter.py --rev 6682b98...  -> SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=0 rewritten=0 sourced=0 ; EXIT=1
c2-counter.py --rev 6682b98...  -> PRISTINE FAIL TOOL-ABSENT tools/souji-freeze-check.py ; SUMMARY cases=21 pass=0 fail=21 ... tool_sha=absent ; EXIT=1
c3-counter.py --rev 6682b98...  -> PRISTINE FAIL FIXTURE-ABSENT tests/fixtures/r41-refusal-sites.py ; SUMMARY sites=19 probes=0 pristine=FAIL killed=0 survived=19 ... fixture_sha=absent ; EXIT=1
r1-counter.py --rev 6682b98...  -> PRISTINE FAIL FIXTURE-ABSENT tests/fixtures/r41-drift-record-order.py ; SUMMARY mutants=11 killed=0 survived=11 pristine=FAIL ... fixture_sha=absent ; EXIT=1
```

Each equals the first SUMMARY line of the matching `census/round-41/controls/*-control.txt`.

### 5. Stub and junk controls in scratch clones (`score-candidate.sh`, allowlisted dests only)

```
bash census/round-41/score-candidate.sh c1 <s>/sc-c1 corpus/lessons/round-41.md=census/round-41/controls/c1-junk-round-41.md
  -> SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=3 rewritten=0 sourced=0 ; EXIT=1
bash census/round-41/score-candidate.sh c2 <s>/sc-c2 tools/souji-freeze-check.py=census/round-41/controls/c2-stub-clean.py
  -> SUMMARY cases=21 pass=2 fail=19 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL tool_sha=5ccb4fb2705b ; EXIT=1
bash census/round-41/score-candidate.sh c3 <s>/sc-c3 tests/fixtures/r41-refusal-sites.py=census/round-41/controls/c3-stub-fixture.py
  -> SUMMARY sites=19 probes=21 pristine=ok killed=0 survived=19 misattributed=0 docclasses=10 ... fixture_sha=6ed213bd68cc ; EXIT=1
bash census/round-41/score-candidate.sh r1 <s>/sc-r1 tests/fixtures/r41-drift-record-order.py=census/round-41/controls/r1-stub-fixture.py
  -> SUMMARY mutants=11 killed=8 survived=3 pristine=ok regress=8/8 new_killed=0/3 old_fixtures_killed_new=0 prior=6/6 cases=8 ... fixture_sha=4768a5d6a21a ; EXIT=1
```

Each equals the matching SUMMARY line in the control files. The scratch clones were scored in `<s>` only; nothing was committed to the lane.

### 6. Rerun output files (in seat directory)

`rerun/c1-rerun.txt`, `rerun/c2-rerun.txt`, `rerun/c3-rerun.txt`, `rerun/r1-rerun.txt` (measured commits); `rerun/c1-ctl-rerun.txt`, `rerun/c2-ctl-rerun.txt`, `rerun/c3-ctl-rerun.txt`, `rerun/r1-ctl-rerun.txt` (instrument-commit controls); `rerun/c1-junk-rerun.txt`, `rerun/c2-stub-rerun.txt`, `rerun/c3-stub-rerun.txt`, `rerun/r1-stub-rerun.txt` (stub and junk controls).

### 7. Cleanup

`rm -rf -- /fast/scratch/hyaku/souji-r41/R41w2scribe04` then `ls -d` -> "No such file or directory". `git status --short` in the lane -> empty. No tool was installed or upgraded in this seat; no mutating git/jj command was run; `~/.local/bin` and PATH directories were not touched.

## Findings

1. The four claim targets reproduce at their measured commits (section 3) and the controls reproduce at `6682b98` and in the stub/junk clones (sections 4 and 5). Every receipt SUMMARY line matches the re-run exactly.
2. The frozen counters, populations, pinned tool and preregistration are unchanged from the instrument commit through the freeze to the tip (section 2). The controls were created in the freeze commit `e2a7431`, not after it.
3. The lesson's named limits (N1 to N12, M41-3) are real and are carried into the scorecard as limits, not as admission credit. N11 (`K1 cited-no-row S146`, registry red at the freeze tip) is taken from the lesson; this seat did not re-run `tools/souji-registry-agreement.py`.
4. Scorecard wording issue found and fixed in the draft: the first R1 row said "all-PASS-free stub" where the control file records a stub fixture; corrected to "stub fixture" before yield.
5. The receipts for C2, C3 and R1 were committed at `31e4d3e`, one commit after their measured tool/fixture landings. Each measured revision is an ancestor of `31e4d3e`. The scorecard states this rather than calling the receipts measured at their own commits.

## Verdict

- C1 (calibration): target met as recorded and re-run at `31e4d3e`: `items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`, rc 0. Limits N1 to N4 and M41-3 stand; the counter can be fooled by shape-only artifacts, and the scorecard says so.
- C2 (operability): target met as recorded and re-run at `119c26f`: `cases=21 pass=21 fail=0`, rc 0; tool-absent control `pass=0`, always-clean stub `pass=2`.
- C3 (coverage): target met as recorded and re-run at `a1144120`: `killed=19 survived=0 misattributed=0 docclasses=10`, rc 0; absent-fixture and all-PASS stub controls both red.
- R1 (residual, not a claim): green at `97eeb01`: `killed=11 survived=0 regress=8/8 new_killed=3/3 prior=6/6`, rc 0.
- Owned axis scores unchanged (calibration 7, operability 8, coverage 8); no reproducible 0–10 mapping; no score delta claimed.
- Admission: not claimed by this seat. The admission rule needs every claim verified and no axis harmed; this seat verified the claims at the measured commits and did not assess axis harm beyond the lesson's listed limits. That determination belongs to the L1 landing and the judge.
- Scribe deliverable (scorecard draft at `.ufo/waves/round-41/w2/R41w2scribe04/scorecard-r41.md`): complete for the requested blocks. Checks the L1 should run after landing it into `SCORECARD.md`: a fresh `git show 1d41c13:SCORECARD.md` diff against the draft, and the census validation the frozen plan names (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`). This seat did not run the census.
