# SwarmMutationTester26 — mutation test of tests/fixtures/r30-jj-keep-expiry.sh (r30 w2)

Target: `tests/fixtures/r30-jj-keep-expiry.sh` at lane tip `9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`, against the C3 v2 E3 replay leg and the v1 L8 leg. Detector = faithful reimplementation of exactly those two legs, run on pristine, 9 mutants, and restored bytes in a scratch clone (`git clone -q --no-local`, origin removed, HEAD == tip, clean tree). No mutant ever touched a lane repo; the fixture's own rule — "Builds jj-colocated repositories ONLY under $TMPDIR, never in a lane or fleet repo" — held throughout.

## Status

STATUS: PASS — the attack ran end-to-end (baseline + 9 mutants + restored, all under the frozen E3/L8 legs); 4 mutants killed, 5 survived. Survival is a coverage finding about the legs' kill power, not a change to any frozen predicate.

## Evidence

- Detector fidelity — E3: "exits 0 and its `jj-version:`, `git-version:` and `RESULT ` lines equal, in order" (census/round-30/c3-counter-v2.py:12-14; implementation `e3 = p.returncode == 0 and got and got == keep(rec)` at :73). L8: "has a line starting `jj-version: jj 0.45.1` and >= 3 lines starting `RESULT `" (census/round-30/c3-counter.py:20-21; implementation :119-123).
- Toolchain matches the committed record exactly: host `jj --version` = `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`, git 2.56.0 (record census/round-30/records/jj-keep-expiry-run.txt:1-2). Baseline pristine: `rc=0 E3=PASS L8=PASS kept=10 rec_kept=10` — the replay is byte-identical to the committed record on the kept lines, so every mutant verdict is meaningful.
- L8 = PASS on all 11 arms: it reads only committed blobs (record + entry at tip; `run = blob(R, V, RUN)` at census/round-30/c3-counter.py:119) and never the fixture, so it is structurally invariant under fixture mutants — verified empirically on every run.
- Restoration: after the sweep the clone's fixture sha256 `6c5424819cde0e51ea42766341a0b3791d5039879766823d302cccb1b0fa6550` == pristine == the committed blob at tip (`git cat-file blob 9dcd3676…:tests/fixtures/…`), and the detector re-run on restored bytes passed (`restored` receipt). Lane working-tree file: same sha, `git status --porcelain` for that path empty — the lane was never modified.
- No tools installed or updated this run (operator directive 2026-10-19: nothing to record); no pacman transaction.

## Findings

1. **[COVERAGE] E3 cannot detect a fixture that fabricates its measurements.** M3 replaced `result()`'s measurement with canned lines copied verbatim from the committed record (real jj/git work still executed): `rc=0 E3=PASS`, output byte-identical to the record. The replay leg binds "these lines were printed", not "they were measured"; a fixture that skips the work and echoes the record would pass identically (version lines match this host). Located: census/round-30/c3-counter-v2.py:73-74.
2. **[COVERAGE] No frozen leg exercises the fixture's scratch guard.** M4 deleted the TMPDIR guard block (tests/fixtures/r30-jj-keep-expiry.sh:29-36): `E3=PASS` because the detector always sets TMPDIR. Extra probe (labeled, not a frozen leg): with TMPDIR unset, pristine refuses rc=2 `ERROR: TMPDIR is unset or empty; refusing to run` while the mutant dies rc=1 `TMPDIR: unbound variable` at the mktemp line — the mutation is behavior-bearing but invisible to both legs. The lane-containment arm (TMPDIR resolving inside the lane) cannot be probed without running against a lane repo, which the fixture and this seat forbid; it stays untested by design.
3. **[COVERAGE, mechanism measured] Steps 4 and 8 cannot evidence `--expire=now`; packedness, not the threshold, is the lever there.** M5 (step-4 `--expire=now` → default) and M8 (step-8 same) both survived with byte-identical output. Scratch probe (receipt probe.out): `git gc --prune=now` packs all 8 keep refs (`loose_files 8→0, packed_lines 8`), after which DEFAULT-threshold `jj util gc` still removes the same 2 refs (`keep 8→6, target_keep yes→no`); and step 7's own default gc packs the control repo's refs while keeping all 8 (`loose_files 8→0, packed_lines 8, keep=8`). So the loose-ref mtime age gate — "Check timestamp of loose ref, but this is still racy on re-import" (entry Gate, S054, git_backend.rs:929-937) — is inert for packed refs, confirming the entry's inference "the metadata probe fails for a packed ref and the ref goes regardless of age" (corpus/knowledge/jj-keep-ref-expiry.md, claim 2) — which the entry had hedged as "this path was read, not measured — the fixture's refs are loose". That hedge is wrong for steps 4-5 and 8: those refs are packed by the preceding gc (step 3's `git gc --prune=now`; step 7's own gc). Consequently the fixture header's "followed by --expire=now on the same repository (step 8) to show the threshold is the lever" is falsified as a lever claim for step 8; the threshold is observable only as step-7 survival (M9 killed there).
4. **[DEGENERATE] M6 (count all refs instead of `refs/jj/keep/*`) is vacuous in this fixture.** Probe C's full ref list shows the only refs in these repositories are `refs/jj/keep/*`, so the two counters coincide at every step and the mutant's output is byte-identical to the record. Survival carries no information beyond that coincidence; in any repo with non-keep refs the mutant would be killed at step 1.
5. **[HOLDS] The record binds the gc events and the order.** Skipping step-4's gc (M1) or all three gc calls (M7) is killed at the first affected RESULT line (step 4: keep_refs 8≠6, target_keep yes≠no; M7 also steps 5 and 8); swapping steps 7↔8 (M2) is killed by line order and by step-7's values (6/no vs 8/yes). The committed record `RESULT step=4-util-gc-expire-now keep_refs=6 object_present=yes note=target_keep=no cmd=jj-util-gc-expire-now` is a real constraint on fixture behavior.

## Attack log

| # | Mutant (smallest behavior-bearing point) | Expected | Actual | Verdict |
|---|---|---|---|---|
| M1 | skip step-4 `JJ util gc --expire=now` (repo 1) | E3 kills at step 4 | E3 FAIL, step-4 line 8/yes vs 6/no | KILLED (E3, step 4) |
| M2 | swap steps 7↔8 execution order (control repo) | E3 kills on order/values | E3 FAIL, step-8 line at position 9, step-7 values 6/no | KILLED (E3, control order) |
| M3 | hard-code RESULT lines from the committed record | E3 or L8 kills | rc=0, E3 PASS, byte-identical output | SURVIVED — coverage finding 1 |
| M4 | drop TMPDIR guard block (lines 29-36) | E3 kills (guard refusal) | E3 PASS with TMPDIR set; extra probe shows rc 2→1, message change | SURVIVED — coverage finding 2 |
| M5 | step-4 `--expire=now` → default threshold | E3 kills at step 4 (8/yes) | E3 PASS, step-4 line byte-identical (packed refs defeat age gate; probe A) | SURVIVED — coverage finding 3 |
| M6 | `keep_count` counts all refs, not `refs/jj/keep/*` | E3 kills at step 1 | E3 PASS, byte-identical (only keep refs exist; probe C) | SURVIVED — degenerate, finding 4 |
| M7 | skip all three `JJ util gc` calls (steps 4, 5, 8) | E3 kills at step 4 | E3 FAIL at steps 4, 5, 8 | KILLED (E3, steps 4/5/8) |
| M8 | step-8 `--expire=now` → default threshold | E3 kills at step 8 | E3 PASS, byte-identical (refs packed by step 7's own gc; probe B) | SURVIVED — coverage finding 3 |
| M9 | step-7 default → `--expire=now` (mirror of M8) | E3 kills at step 7 | E3 FAIL, step-7 line 6/no vs 8/yes | KILLED (E3, step 7) |

Per attacked item: gc-event binding HOLDS (M1, M7); step order HOLDS (M2); measurement authenticity BROKEN as a leg property (M3); scratch-guard coverage BROKEN under frozen legs (M4); threshold attribution at steps 4 and 8 BROKEN (M5, M8); step-7 threshold sensitivity HOLDS (M9); ref-set scoping DEFECT-NOT-FATAL (M6 vacuous). L8 killed nothing and can kill nothing fixture-side (reads committed bytes only).

## Deliveries

- .ufo/waves/round-30/w2/SwarmMutationTester26.md — this report
- .ufo/waves/round-30/w2/SwarmMutationTester26-receipts/ — detector.sh, probe.sh, probe.out, baseline/m1-m9/restored raw outputs and kept-line files, m4 unset-TMPDIR probes, DETECTOR-SUMMARIES.txt, HASH-LEDGER.txt

Scratch /fast/scratch/hyaku/souji-r30/MutateJjFixture/ removed after receipt copy. No lane file, jj state, or git index touched; no sibling's source modified.
