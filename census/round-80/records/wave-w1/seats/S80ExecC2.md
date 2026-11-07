# S80ExecC2 — C2 falsification (souji-quarantine signal handling)

Verdict: C2 CLAIM HOLDS. Every frozen C2 predicate reproduced from committed bytes; no falsification found.
Revs: base f80f9368 (tool e2f2d083), candidate/W2 836dac3e (tool 67ec160b), verify e6cb3f93, vault 5cb0fb13 — all
sha256 verified via `git show <rev>:<path> | sha256sum`; counter 32cf0c72, population ca5e2387, probe 16580aa0,
variants 6d04211f/2682b8ff match preregistration binds. HEAD=a4aa8880.

## Runs (census/round-80/c2-signal-counter.py --tool-dir D --work W, from lane root; receipts in receipts/)
1. Candidate foreground: `SUMMARY rows=15 mismatches=0 errors=0 orphans=0` EXIT=0; row-for-row identical to
   census/round-80/records/c2-after.txt (normalized secs/ign/survivors/tmpleft). rc=143/130/129, signal_line=y,
   tmpleft=0, survivors=0 on all q-rows. `# launch pid=3838864 pgid=3838777 sid=3838777 sigign=0000000001001000`.
2. Candidate launched with `&` from driver script: `SUMMARY rows=15 mismatches=0 errors=0 orphans=0` EXIT=0.
   Driver sigign=0000000001000004; counter `# launch pid=103321 pgid=103020 sid=103020 sigign=0000000001001006`
   — SIGINT ignored at counter start (async-job inheritance), yet no ERROR and all rows match: per-child
   reset=INT,QUIT,TERM,HUP neutralizes it (counter doc "run it in the foreground or not" verified).
   Per-row `ign=0000000000000004` on all 12 signal rows in runs 1-2 (only QUIT ignored in tool children).
3. Base tool: `SUMMARY rows=15 mismatches=12 errors=0 orphans=12` EXIT=1; normalized-identical to
   census/round-80/controls/c2-K-a-do-nothing.txt. INT rows: exited=n rc=None, orphans (survivors 4-9, tmpleft=1).
4. Controls reproduced, sha256 of variant tool dirs match receipt binds: K-b 12 mismatches/12 orphans EXIT=1,
   K-c 12/12 EXIT=1 (survivors>0 tmpleft=0 — front died correctly, worker session survived), rows identical to
   receipts. Base stays red, controls stay red: conjunct holds.
5. r13: `SUMMARY total=5 failed=0 hung=0` EXIT=0. r17 (W2 tool dir incl. vault-verify): `SUMMARY total=35
   failed=0 skipped=2` EXIT=0. Both match receipts.
6. Domain trial v3 replay (`census/round-80/probes/domain-trial.sh <base> <cand> W`): base_rc=0 cand_rc=0,
   stdout sha256 14fbcd5a... BOTH arms, 3 RESULT lines each, signal_lines=0, tmpleft 0/0, `TRIAL identical=yes`
   — matches census/round-80/records/c2-domain-trial.txt. NOT vacuous: engine+ledger pinned, arms in identical
   `<W>/<arm>/tools/` layout (v2 location skew fixed), requires 3 RESULT lines/arm + byte-compare (v1 vacuity
   fixed), and it exercises real stage-1 children (engine verdicts, sha256sum, find|sort digests). Coverage
   bound (by design, not a defect): --dry-run prints but never executes the bounded children (mv/sleep
   450/second-check) in either arm, so the trial proves no-signal output/exit stability only; the kill path is
   covered by counter rows q1-q12, not by the trial.

## Selftest (assignment item 3)
- Candidate `git show` copy, mode 0644: `selftest: 81 checks, 51 failed` — EXACTLY reproduces
  records/c2-regress-selftest.txt; every flow FAIL is got=126 (inner `"$SELF"` exec EACCES) + R9-runner-missing.
  L1's mechanism claim ("selftest runs $SELF directly") CONFIRMED.
- Candidate copy chmod 0755: `81 checks, 47 failed` — chmod alone does NOT go green; remaining fails are
  `souji-quarantine: receipt engine missing: <copydir>/souji-verify.sh` (engine is a tool-dir sibling).
- 0755 + round9 sibling: `108 checks, 68 failed` (ROUND9 6/22). 0755 + engine + round9 siblings:
  `108 checks, 68 failed` — now `GUARD refusal live-fleet-mutation-forbidden ... fleet=$S`: a scratch copy
  derives its fleet root from its own location, and TMPDIR-under-scratch fixtures then sit "inside the fleet".
- Base tool 0644 copy: `selftest: 81 checks, 51 failed` — identical to candidate 0644. The diagnosis
  conclusion in records/diagnosis/selftest-base-mode0644-copy.txt (BASE copy fails identically) is TRUE; I
  reproduced it from the true base blob e2f2d083.
- Only the installed-tree layout (lane tools/, TMPDIR outside the derived fleet root) reaches
  `selftest: 108 checks, 0 failed` as in records/c2-regress-selftest-committed-mode.txt — reproduced conjunct.

## Findings
- MEDIUM: records/diagnosis/selftest-base-mode0644-copy.txt does not pin the executed bytes: its rec.sh `# bind`
  line names the lane-relative tools/souji-quarantine.sh (67ec160b) while command= runs the scratch copy, so the
  receipt cannot distinguish base from candidate bytes. Conclusion independently verified true (81/51 from base).
- LOW: preregistration selftest conjunct `TMPDIR=<scratch> bash <candidate> --selftest` -> 108/0 is
  layout-sensitive: a bare blob copy in scratch gives 81/51 (0644), 81/47 (0755), 108/68 (with siblings, guard
  refusal). Replayers must run it from the installed tree as the L1 receipts did, else the conjunct looks red.
- LOW (process): my K-b and K-c replays ran concurrently (setsid returned early); both outputs match their
  receipts row-for-row, so no verdict impact. Tooling installed: none.

## Files written (seat dir)
.ufo/waves/round-80/w1/S80ExecC2.md (this report) and receipts/: cand-fg.txt, cand-bg.txt, base.txt, kb.txt,
kc.txt, r13.txt, r17.txt, st-cand0644.txt, st-cand0755.txt, st-cand0755r9.txt, st-candfull.txt, st-base0644.txt,
domain-trial.txt. Scratch /fast/scratch/hyaku/souji-r80/S80ExecC2 removed before yield; no stray processes.
