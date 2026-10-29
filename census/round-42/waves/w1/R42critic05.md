# R42critic05 — attack on C3 (coverage): frozen scoring harness

Seat: R42critic05 (critic, leaf, no subagents). Lane freeze commit `afe17f416eec04dcf3f480b580a8f928de61d19d` (HEAD, verified with `git -C <lane> rev-parse HEAD`). No lane file was written; no git mutation was run in the lane (`git show` reads only). Candidates and evidence live only under `.ufo/waves/round-42/w1/R42critic05/`. Scratch `/fast/scratch/hyaku/souji-r42/R42critic05/` was removed before this report. Tools installed: none.

## 1. Frozen hashes (read via `git -C <lane> show HEAD:<path> | sha256sum`)

| path | sha256 (prefix) | matches prereg |
|---|---|---|
| census/round-42/c3-counter.py | bf0ebf4fef0cf007… | yes (`bf0ebf4f…`) |
| census/round-42/c3-mutants.tsv | 2f6f8df39ed6dd66… | yes (`2f6f8df3…`) |
| tools/souji-worktree-drift.py | b2a603cf42472b45… | yes (`b2a603cf…`) |

## 2. Harness reading (counter lines cited from HEAD copy)

- Kill = `cases is not None and rc == 1 and failed > 0 and not crash` (`killed`, c3-counter.py:151-153). `crash` = `"Traceback (most recent call last)" in proc.stderr` only (line 140). stdout is never checked for tracebacks.
- Timeout: `subprocess.run(..., timeout=300)` (literal count in file = 1, line 138); `TimeoutExpired` returns `(124, None, None, None, True)` (lines 145-146). `cases is None` ⇒ not killed. A hang is a survivor; the 300 s limit never counts as a kill. Confirmed in §4 (HANG).
- Protocol regex `^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)` (line 57), `m[-1]` used (last SUMMARY wins). Case lines `case-<name>=PASS|FAIL` are documented in the docstring but never read; the counter scores a fixture that prints no case lines (K1, K2, K3, K4 print none or only SUMMARY).
- Pristine gate: `clean()` plus `cand_pre[1] >= 13` (line 220). It does not require `passed == number of case lines`.
- Scratch: every mutant is written to `scratch/mut-<id>.py` (line 214) and `pristine.py`, prior fixtures to `scratch/fx-*.py`, all in one shared directory `scratch = mkdtemp(dir=scratch_root)` (line 200). Fixtures receive `--tool` inside that directory, so they can read `dirname(tool)/pristine.py`, read the basename `mut-<id>.py`, and write into sibling `mut-*.py` files. Writes are not hashed or re-verified. Work dirs (`--work`) are unique per run (line 132), so the work-dir part of "parallel runs sharing state" is sound; the scratch-dir part is not.
- Anchors (line 191-199): compares `{id: sha256(old)}` only, against population rows with `len(f) >= 3`. Population holds 13 MUTANT rows and no EQUIV rows (`cat census/round-42/c3-mutants.tsv`), so EQUIV `old` strings are checked for uniqueness only, and the `new` strings and descriptions of all mutants are unpinned. The counter does not hash itself or the population at run time; the only runtime pin is the tool (`PRISTINE_SHA256`, line 50).

## 3. Candidates (each scored with `score-candidate.sh c3 <scratch> tests/fixtures/r42-drift-conditions.py=<file>`)

Commands: `bash census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42critic05 tests/fixtures/r42-drift-conditions.py=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42critic05/<file>` (with `TMPDIR` set explicitly to the scratch root). EXIT captured with `echo EXIT=$?`. Logs: `evidence/`.

| candidate | SUMMARY (counter, verbatim) | reaches target? | shim: tool invocations (per run) | the gap |
|---|---|---|---|---|
| K1-basename-dispatch.py (no tool call, no case lines; kills by `--tool` basename `mut-<id>.py`) | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` (EXIT=0, evidence/K1-score.log) | **yes** | 0 (shim rc 0) | Mutant id leaks through the `--tool` filename; the counter does not hide or rename mutant files. Fixture never observes the tool. Outside check: execution-count shim (wrap `--tool` in a logging shim, require ≥1 invocation per case) AND re-score with mutant files renamed to opaque tokens (the score must not change). |
| K2-sibling-bytes.py (byte-diff of `--tool` against sibling `pristine.py`, keyword filter on the diff lines; never invokes the tool) | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` (EXIT=0, evidence/K2-score.log) | **yes** | 0 (shim rc 1: a non-mutant wrapper is killed; [INFERENCE] because the keyword filter hits unrelated pristine lines inside the same diff block) | Byte sniffing as a kill rule; the EQUIV table has only 6 rows, so a byte filter tuned to the frozen anchors passes the counter. Shows the counter's `equiv_killed` check is a sample, not a proof. Outside check: execution-count shim (flags K2: 0 invocations) and a differential-output check on each kill (the failing case's tool output must differ from pristine's for the same argv; see §4 DIFF). |
| K3-token-invoke-bytes.py (13 `--help` invocations to pass a count shim; outputs ignored; kill = K2 byte filter) | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` (EXIT=0, evidence/K3-score.log) | **yes** | 13 (shim rc 1; passes the count shim) | Passes an execution-count shim alone: invocation is not observation. Outside check: differential-output check. For K3 only H1 and H2 change `--help` output (DIFF table), so the other 11 of its 13 kills have no observed difference on their failing case and are flagged. |
| K4-sibling-tamper.py (a mutant run rewrites sibling `mut-<id>.py` in the shared scratch with a wrapper that exits 3 on env `R42_PROBE=1` and otherwise `execv`s pristine; its own probe sets `R42_PROBE=1`) | batch-1 run: `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` (rc not captured); reps 1-4 (EXIT=0 each): same SUMMARY, old_killed=0; batch-2 run: `… prior=8/8 old_killed=2 equiv=6 equiv_killed=0 anchors=ok cases=13 …` (EXIT=1, evidence/K4-score-run-with-prior-kills.log) | **yes in 5 of 6 runs**; the batch-2 miss is old_killed=2 (r36 kills E2, G3), not caused by the candidate's kills | 13 (shim rc 0; passes the count shim) | Shared writable scratch: a fixture can overwrite other mutants' bytes, and the counter never re-hashes them. Kill is caused by the planted wrapper, not by the mutant (control below). Label-gated (needs `mut-` basename and the id list), so the L1's label audit is the only defence here. Outside check: sha256 each `mut-*.py` before and after each candidate run (must equal the anchor-generated bytes), and give each candidate run its own copy of the mutant tree. |
| K4-control-nopoison.py (K4 with the poison block removed) | `SUMMARY mutants=13 killed=0 survived=13 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` (EXIT=1, evidence/K4-control-nopoison-score.log) | no (by design) | 13 | Confirms that the K4 kills come from the planted wrapper alone. |

Race/flake observations from the same scoring runs (not a candidate, a frozen-battery property):

| run | SUMMARY (verbatim, relevant fields) | EXIT | cause (evidence) |
|---|---|---|---|
| K4 batch-2 (concurrent with 4 other scorings) | `old_killed=2`: prior r36 killed E2 and G3 | 1 | Prior-fixture kill of mutants that are killed by no prior fixture in K1-K3 or the no-poison control at identical bytes. §4 shows a truncated mutant file is a kill for r36, and §4 also shows r36 flakes under load without any tamper. |
| control `K4-control-nopoison` under 4-way concurrency (load ctl4) | `old_killed=1` (r36 kills G4) | 1 | No tamper in this run; concurrency only. |
| K1 under 2-way concurrency (k1load1) | `SUMMARY mutants=13 killed=13 … old_killed=1 equiv=6 equiv_killed=0 anchors=ok` (G5 killed by r36) | 1 | Same: no tamper, concurrency only. A K1 candidate would have reached target without the flake. |
| K1 batch-1 (concurrent with K2-K4) | `EQUIV B4 candidate=survived prior=r36-worktree-drift.py` (SUMMARY still target-met, equiv_killed=0) | not captured (met by inspection) | Prior r36 kill of an EQUIV mutant under concurrency; no effect on the target fields, but the prior column is not reproducible. |

Load-free checks of r36 on the same bytes: mut-G4 ×10, mut-G5 ×10, mut-B4 ×12 isolated → all `fail=0`; mut-B4 ×8 concurrent and pristine ×8 concurrent → all `fail=0`. So the flake did not reproduce in my own 8-way test; the cause of the in-counter flake was not isolated [INFERENCE: load-dependent timing in r36 or in the counter's 8-worker pool combined with concurrent scorings].

## 4. Harness checks (direct observations)

- **Timeout is never a kill.** Scratch copy of the counter with `timeout=3` and the candidate replaced by a fixture that sleeps 3600 s on any tool whose bytes differ from `pristine.py` (evidence/harness-hang-fixture.py, evidence/patch-hang-t3.diff, evidence/harness-timeout3-hang-score.log): `SUMMARY mutants=13 killed=0 survived=13 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247`. All 19 candidate runs hit the timeout and survived. The exit code was not captured for this run; by the counter's rule (killed=0 ⇒ target unmet) it is 1. The 300 s literal is the same code path.
- **Truncated mutant file is a kill for a prior fixture.** `r36-worktree-drift.py` against an empty `mut-*.py`: `SUMMARY cases=12 pass=1 fail=11` rc=1; against pristine: `pass=12 fail=0` rc=0; against a delegating wrapper with env unset: `pass=12 fail=0` rc=0 (evidence/r36-*.out, *.stderr). So a window during rewrite is a real kill path for K4-style tamper.
- **Anchors compare old strings only.** Scratch copy with G2 `new` changed from `<=1` to `<=2` (evidence/patch-newaltered.diff): `SUMMARY … anchors=ok` (evidence/anchors-new-altered-score.log; fixture was the r41 probe, so killed=0 is expected). The `new` text is not pinned.
- **Protocol regex.** `python3 -c` on `SUMMARY probes=13 pass=0 fail=13` → matched `('13','0','13')`; `SUMMARY cases=13 pass=13 fail=0` → accepted. Case lines are never checked (K1 prints none and is scored).
- **Differential check (outside the counter).** `evidence/diffprobe2.py` (copied from scratch; it needs a scratch dir with the counter copy and pristine.py to re-run) builds each of the 19 frozen mutants from the frozen MUTANTS/EQUIV tables and runs 15 probes (help, noroot, norec, missing, fifo, big, timeout1, bytes, sib, escape-gitdir, unrecorded-link, bad-list-rc, slowgit-default, slowgit-t1, json-tail) against pristine and mutant, comparing rc, stdout, last stderr line and the JSON file. Output (evidence/diffprobe2.out, rc 0, 186 s):
  - MUTANT B1 observable_on=fifo; E2 observable_on=sib; E4 observable_on=escape-gitdir; G2 observable_on=timeout1,slowgit-t1; G3 observable_on=slowgit-default; G4 observable_on=slowgit-t1; G5 observable_on=big,timeout1,bytes,unrecorded-link,bad-list-rc,slowgit-default,json-tail; H1 observable_on=help,noroot; H2 observable_on=help,norec; I1 observable_on=big,timeout1,bytes,unrecorded-link,bad-list-rc,slowgit-default,slowgit-t1,json-tail; J9 observable_on=big; M1 observable_on=json-tail; D4 observable_on=bytes.
  - EQUIV B3, B4, E5, E7, E9, H4: observable_on=- (none of 15 probes).
  So all 13 MUTANT rows have an observable difference on some probe and no EQUIV row does on this set. This is evidence that the target is behaviourally reachable, not a candidate. A landing fixture would have to embed path-normalised expected outputs.
- **Execution-count shim** (evidence/shimrun.sh, shim-*.sum): a logging `--tool` shim, one line per invocation: K1 `tool_invocations=0 rc=0`; K2 `tool_invocations=0 rc=1`; K3 `tool_invocations=13 rc=1`; K4 `tool_invocations=13 rc=0`. The shim flags K1 and K2 and passes K3 and K4. K3 and K4 need the differential check.
- **Scope of the tool's mutant set.** Only the 13 MUTANTS are in the population; K4's label list and K1's label set are copies of that list.

## 5. Verdict

**C3 harness: gameable.** The frozen counter reports `SUMMARY mutants=13 killed=13 … equiv_killed=0 anchors=ok` and EXIT 0 for three candidates that never observe the tool's behaviour (K1, K2, K3) and for one that rewrites sibling mutant files in the shared scratch (K4, 5 of 6 runs). It has no execution-count check, no case-line cross-check, no re-hash of `mut-*.py`, no isolation of scratch, and no pinning of the `new` strings or descriptions. The counter's score also changed under concurrent scoring, in step with prior-fixture (r36) kills that did not occur in isolation: 3 of about 19 concurrent scorings I ran changed a target field (old_killed=1 or 2), and two of those three had no tamper. The cause of the r36 flake was not isolated.

The 300 s timeout is sound (a hang is a survivor). Parallel work dirs are sound. The scratch dir is not.

Checks the L1 should run outside the counter before landing (each is a single command or small script):
1. Execution-count shim: `--tool` pointed at a logging wrapper; require ≥1 invocation per case (catches K1, K2).
2. Differential-output check: for each kill, the failing case's output must differ from pristine's for the same argv (catches K3; the probe set in `evidence/diffprobe2.py` is one such oracle).
3. Opaque names and integrity: rename `mut-<id>.py` to random tokens and re-score; sha256 every `mut-*.py` and `pristine.py` before and after each candidate run (catches K1 and K4).
4. Repeat-score serially on a quiet host, three times; any `old_killed` or `prior` change means the score is not measured (the r36 flake).
5. Hash the counter and population at run time (or at least confirm the freeze sha before landing); pin `new` strings and descriptions in the population as well as `old`.

## 6. Limits (named, not fixed)

- The crash check reads stderr only (c3-counter.py:140). A fixture that forwards the tool's stderr can turn a real behavioural kill into a non-kill when the tool prints a traceback (G4 `raise` path [INFERENCE from code; not run, my standalone attempt used a record whose repo had no `.git` and so never called git, and that artifact was removed]).
- Kill attribution: `killed()` does not require the failing case to be a condition-level probe. Any caught exception that reports `fail>0` with rc 1 counts (K-series did not exercise this; [INFERENCE] from code).
- The EQUIV rows are checked only by counting in the counter's table; the equivalence claim itself was not re-proven here. The differential above found none of 15 probes distinguishes them.

## 7. Commands run (summary; full logs under evidence/)

- `git -C <lane> rev-parse HEAD`; `git -C <lane> show HEAD:<path> | sha256sum` for 4 paths.
- `score-candidate.sh c3 <scratch> …` for K1, K2, K3, K4 (batch 1 concurrent, batch 2 concurrent with K4-control, four K4 repeats), K4-control-nopoison (batch 2 and load), K1 load ×2, K4 control load ×4.
- Scratch-copy counter patches: timeout=3 + hang fixture (HANG); G2 `new` altered (ANCH).
- Direct tool runs: `python3 -B <tool> …` for the mechanism and differential checks; `r36-worktree-drift.py` against pristine, empty, and wrapper files; r36 isolated and concurrent loops on mut-B4, mut-G4, mut-G5.
- `diffprobe2.py` (15 probes × 25 tool variants).
- Scratch removed (`rm -rf`) after copying receipts.
