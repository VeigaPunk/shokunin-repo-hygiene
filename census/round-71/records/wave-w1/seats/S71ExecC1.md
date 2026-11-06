# S71ExecC1 — C1 reproduction (round 71, w1)

Verdict: C1 REPRODUCED from committed bytes. All five runs re-emitted every ^(CASE|SUMMARY|EXIT=) line byte-identically to the receipts; chronology holds; no frozen number was falsified.

Commands (from /home/vgpnk/Projects/shokunin/souji-shokunin, SCRATCH=/fast/scratch/hyaku/souji-r71/S71ExecC1):
 1 python3 -B census/round-71/c1-counter.py --root <lane> --matrix census/round-71/c1-matrix.tsv --base-rev 8b9345b1… --rev a1db6c85… --tool tools/souji-receipt-write.py --work $SCRATCH/c1
 2 same with --new-tool controls/base-writer-8b9345b1.py (and F1/F2/F3 variants); 4 runs in parallel, ~21 s each
 3 diff of ^(CASE|SUMMARY|EXIT=) lines vs records/c1-after.txt and controls/c1-{do-nothing,F1,F2,F3}*.txt
 4 git merge-base --is-ancestor, git log --format='%H %ci', git diff --quiet/--stat

Observed (decisive lines):
 candidate: SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS / EXIT=0
 do-nothing: new_forgeries=7 class_mismatches=7 / EXIT=1 ; F1: new_forgeries=0 new_honest=16 class_mismatches=11 / EXIT=1
 F2: new_forgeries=5 class_mismatches=5 / EXIT=1 ; F3: new_forgeries=5 class_mismatches=5 / EXIT=1
 REGRESS base=PASS new=PASS on all five runs.
 CASE AS1 new_findings=lane worktree is dirty; AS2/FM2 new_findings=RECEIPT-STATE-CHANGED-DURING-RUN; FC1/FC2/FC3 new_findings=RECEIPT-FILTER-DRIVER-SET; ASh/FCh/FCh2/FMh new=accept (all base=accept).
 Diff: IDENTICAL 72/72 lines for all five pairs (candidate vs c1-after and each control vs its receipt). Full-file diff = 10 lines, all of them the receipt header (rev/instrument/instrument_sha256/command) or seat scratch paths; every CASE and # detail line matches.
 Executed bytes: slots/base.py sha256 118597e0… = git 8b9345b:tools/souji-receipt-write.py = controls/base-writer-8b9345b1.py; slots/new.py sha256 56b6be03… = git a1db6c8:tools/souji-receipt-write.py = lane worktree writer (git diff cand..after empty, rc=0).
 Re-derivation (own parser over CASE + # detail, using counter's class rule at c1-counter.py:1127): every SUMMARY field reproduced for all five runs; leftovers F2=FC1 FC2 FC3 FM1 FM2, F3=AS1 AS2 FC1 FC2 FC3, F1 over-refused ASh FCh2 FMh; 59 carried rows: 0 differ between candidate and base-writer runs; matrix = 70 data rows + header.
 Chronology: freeze->candidate rc=0, candidate->after rc=0; aa91d1c 2026-11-06 16:47:23, a1db6c8 16:48:52, 52e8c3f 16:53:48; git diff --quiet 8b9345b aa91d1c -- tools/souji-receipt-write.py rc=0; git diff --stat aa91d1c 52e8c3f -- <c1-counter, c1-matrix, c2-harness, c2-mutants, controls, preregistration> empty rc=0; lane instrument sha256 == freeze blobs (counter 7e5a694a, matrix e1a3c00b, harness 6c7bf41d, mutants 3e4945bf, prereg 0f5d05f1); `git status --porcelain -- census/round-71 tools/` empty.

Findings:
 LOW c1-counter.py:1127 — class_mismatches increments for any expect=refuse row not both refusing and echoing its class, so a forged row counts in both new_forgeries and class_mismatches; the do-nothing arm's "7 -> 0" class target is not independent evidence of the forgery target (F1's 11 is genuinely class-only). Numbers themselves reproduce; no change requested.
 No drift, no unreproducible number. Installs: none.

Files written (seat dir): .ufo/waves/round-71/w1/S71ExecC1/evidence.txt (all CASE/SUMMARY/EXIT lines, diffs, slot shas), .ufo/waves/round-71/w1/S71ExecC1.md. Scratch /fast/scratch/hyaku/souji-r71/S71ExecC1 removed.
