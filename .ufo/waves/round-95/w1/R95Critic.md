# R95Critic — R95 critic report (skeleton, in progress)
Status: DONE (final yield follows; scratch /fast/scratch/hyaku/souji-r95/R95Critic deleted; no background processes of this seat remain)
## C1 after-predicate (reproduced by critic)
- Run: python3 -B census/round-95/c1-survivor-search.py --ids census/round-95/c1-targets.json --jobs 5 --work /fast/scratch/hyaku/souji-r95/R95Critic/c1r95
- Result: `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`, `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1`, EXIT 0. Matches prereg predicate exactly. Receipt: .ufo/waves/round-95/w1/R95Critic/c1-after-receipt.txt

## Inherited control receipts (L1-filed, P2, this critic did not re-run)
- C1 do-nothing control census/round-95/controls/c1-control-r94-rule.txt: errored=2 killed=5 survived=3, h-sysexit/h-osexit/h-sigkill killed=yes, h-atexit/h-thread killed=no, EXIT 0. Copied: c1-control-receipt.txt.
- C2 do-nothing control census/round-95/controls/c2-control-r94-probe.txt: ARMS-SUMMARY arms=16 conform=12 (S9/S10/S11 exit=1, S12 exit=hung), EXIT 1. My own re-run (c2ctl2) is still in progress at time of writing.
- C2 forgeries census/round-95/controls/c2-forgery-controls.txt: GA conform=15, GB conform=14, GC conform=15, refused 3/3, EXIT 0. My own re-run (c2forg) in progress.
- C1 forgeries (my re-run, bg_2350): FA errored=9 killed=0, FB errored=1 killed=6, FC errored=6 killed=3, refused 3/3, EXIT 0. Receipt: c1-forgery-receipt.txt (this run's own copy).

## C1 cheap-rule test (item 1: alternative rule NOT the sentinel)
- Alternative rule R1: `errored iff the harness printed no ROW line` (the "no ITEM line printed" family). Implemented in c1-noitem-rule.py (verdict() replaced; HOOK/CHECK untouched so the check line still passes).
- Result (my run, receipt c1-cheap-rule-receipt.txt): `# crash-sentinel rc=70 check=pass ...` identical, but `SEARCH-SUMMARY ... errored=0 killed=9 survived=1` — all five crash-channel fixtures killed=yes. Predicate requires errored=7 killed=2 survived=1. Cheap rule FAILS the predicate.
- Why: the harness prints one ROW per population row even when the counter crashed on that row (got=- rc=70 / rc=-9 / rc=1), so "no ROW" never fires on these fixtures. The real discriminator is the ROW rc (70 or negative), i.e. the FORGERY FC leg the prereg already binds. A "stderr non-empty" rule is not even computable: score() discards the harness stderr for verdict() (it reads only stdout `out`), so that rule would need harness changes, i.e. it would falsify "harness unchanged".

## C1 axis-fit (calibration)
- Calibration here means: the search's verdict (self-assessment) vs observed state (the counter died). The r94 rule counted a crash as killed=yes / survived — a self-assessment that disagrees with observed state. The defect is exactly a calibration defect; the knowledge entry (mutant-crash-is-not-a-kill.md) frames it as Stryker's "Runtime error" state being counted as killed. Axis: CONFIRMED by the claim's own wording ("the r94 kill rule reads that status as a verdict").
- Is h-sysexit a crash? On the counter it is: `raise SystemExit("h-sysexit")` replaces the ledger read, so the counter dies mid-run before printing most ITEM lines; harness rows show got=-. The sentinel distinguishes it from the counter's declared exit (sys.exit(main(...)) at top level, RAISE first seen in <module>) via sys.monitoring RAISE + atexit. The prereg's STATED LIMIT (ii) discloses the false-positive class (a counter legitimately calling sys.exit inside its own helper scores errored). So "the same exit status a semantic failure could give" is true of the RAW status (1), but h-sysexit's status is 1 only after starting the process; the semantic-failure exit-1 paths of the unmutated counter print a full SUMMARY/ITEM set and their rows carry match=no — the search distinguishes the two by whether the sentinel fires, which is precisely the calibration repair. Charge: NOT a crash in the raw-status sense, IS a crash in the "counter stopped before judging" sense, and the claim says so ("killed=yes with every row got=-" in the knowledge table; prereg (ii) bounds the over-broad case).

## C2 axis-fit (operability) + cheapest probe edit
- Operability = the probe's exit-code contract is usable: setup failures must not read as "a forgery survived" (exit 1) or hang. The counted quantity (conforming arms of 16) is the right shape for operability-by-conformance. CONFIRMED.
- Cheapest edit reaching 16/16 without real setup discipline: c2-cheap-catchall.py — hard-coded `if "fixture-hang"/"fixture-mute"/"fixture-crash" in fixture: raise Fatal` at the head of run(), everything else via the pre-existing catch-all. Receipt c2-cheap-probe-receipt.txt: arms=16 conform=16 EXIT 0 wall 55s (real probe 122s, because S12 waits for the 120s timeout). Analysis: c2-cheap-probe-notes.txt.
- Implication: the counted quantity binds exit codes, not setup-correctness. But the prereg's STATED LIMITS (i)(iii) already say the claim is "conforming arms of 16 — before 12, after 16", and that the catch-all "is not bound by any arm" and S12 "measures only that the probe ends with exit 2 before the counter's 300 s". The cheap copy satisfies the counted quantity while violating the spirit; that is a ROBUSTNESS observation about the metric, not a falsification of any frozen sentence (no sentence claims general setup correctness). The do-nothing + forgery controls (GA/GB/GC) show the predicate rejects the most obvious gaming (verdict-exit collapse, errors=replace, no timeout); filename-substring gaming is a further, unbound class the limits disclose.

## Separability (item 3)
- C1 verified with C2 not landed and vice versa: YES, both directions.
  - C1 predicate imports: argparse, concurrent.futures, hashlib, io, json, os, re, shutil, signal, subprocess, sys, tempfile?, tokenize — all stdlib. Cross-refs C2: 0 (`grep -c "c2-" census/round-95/c1-survivor-search.py` = 0). The C1 do-nothing control (c1-control-r94-rule.py) imports only importlib.util/os/sys and is the frozen r94 search + hand edits. C1 texts (AUTHORITATIVE claim) live in census/round-95/c1-*.py + c1-targets.json; C2 files: census/round-95/c2-*.py.
  - C2 predicate imports: stdlib only. Cross-refs C1: 0 (`grep -c "c1-" census/round-95/c2-forgery-probe.py` = 0; `grep -c "c1-" census/round-95/c2-setup-arms.py` = 0). C2 control file census/round-94/c2-forgery-probe.py is disjoint from census/round-94/c1-survivor-search.py.
  - Positive arms: the C1 predicate USES the verdicts of the five r94 targets as its positive control inside itself; the C2 predicate uses P1/P2 in its 16 arms. Neither carries the other's "positive" requirement. File sets: P1 = census/round-95/{c1-survivor-search,c1-targets,c1-control-r94-rule,c1-forgery-controls}.py (+ r87 counter + r93 harness/population, all pre-P1); P2 = census/round-95/{c2-forgery-probe,c2-setup-arms,c2-forgery-controls}.py (+ r94 probe, r92/r93 fixtures, filed tool, r92 before-tool). Disjoint except the lane itself.
  - One shared touch: MY own seat ran C1 after + C1 forgeries + C2 after + C2 cheap probe concurrently (bg_2349/bg_2350/bg_2351, c2cheap import) — the runs share only the lane working dir read-only + /fast/scratch trees; no work-dir key collision (each --work under /fast/scratch/hyaku/souji-r95/R95Critic/*). The frozen instruments do not interact at runtime.
- Verdict: separable. Either predicate can be run with --probe/--search absent and still decide its claim.

## Universal words in the prereg (item 4)
Grep `all|every|never|always|any` on census/round-95/preregistration.txt:
- "never repaired silently (Amendment 59)" — process rule, not a claim quantity. Not falsifiable by counters.
- "all five errored" (C1 claim) — ENUMERATED: the ten ids in census/round-95/c1-targets.json, each scored and printed SEARCH ... killed=errored. Bound.
- "keeps the verdicts of the five r94 targets" — ENUMERATED: five ids, each scored and printed (killed=yes/no per id).
- "every receipt prints its instruments' full sha256 or names them" — ENUMERATED by the receipts themselves (each header line lists sha256; verified on my runs).
- "FA (verdict never returns "yes") ... Turning every failure into exit 2 ... a rule without the sentinel" — these describe the forgery edits and their effects; each prints its SEARCH/ARM lines. ENUMERATED by the forgery receipts.
- "not a census of every generated mutant" — explicit LIMIT, not claimed. Good.
- "any os._exit call" (C1 sentinel description) — UNIVERSAL beyond the fixture: the hook replaces os._exit so ANY call exits 70; the CHECK script exercises it once (osexit=70). A counter that calls os._exit(0) (normal exit) would be scored errored — an untested case. The prereg bounds this at (ii)/(iii) only partially ("a non-Python child", "signals other than SIGKILL"). Verdict: "any" is literally true of the hook (it replaces the name), but the CLAIM's predicate only tests one os._exit(1) fixture. Not falsified as a claim about the ten ids; a reviewer can reasonably ask a narrowing note on "any os._exit call" → "an os._exit(1) call in the fixtures". Filed as a robustness observation, NOT a FALSIFIES-WORDING (the sentence sits in the instrument description, and the predicate's ten ids are each enumerated).
- "any other exception into exit 2, which no arm binds" (C2 limit (i)) — disclosed as unbound. Good.
- "the twelve arms the r94 probe conforms on (P1, P2, S1-S8, S13 ... S14)" — ENUMERATED (16-arm counter prints each ARM line). Bound.
- S13 "names an absent /tmp path it never creates" — verified by the arm itself (the counter checks lexists before running). Bound.
Verdict: every universal that carries claim weight is enumerated by the predicate's ids/arms; the two unbound universals ("any os._exit", "any other exception") are disclosed in the limits. No all/every/never sentence is falsified by the counters.

## Universal-word probe (hook file-shape, my own probes)
- Reproduced (hook-universals.txt, hooktest/): with real script files (harness shape): helper sys.exit(3) -> rc=70 (foreign SystemExit, limit (ii) discloses exactly this); top-level sys.exit(1) -> rc=1 and sys.exit(main()) -> rc=5 (declared, kept). "-c" probe earlier masked the helper leg (__file__ absent); the file-shape probe supersedes it.
- "any os._exit call": os._exit(0) -> rc=70 SOUJI-R95-CRASH os._exit(0). The hook replaces os._exit wholesale, so the word "any" is literally true; but a NORMAL os._exit(0) exit reads errored, and no fixture tests it. LIMIT (iii) does not name os._exit(0). Robustness note only (no frozen sentence claims a normal os._exit(0) is scored survived). Recommend the L1 record a one-line narrowing note in plans/round-95.md; not a FALSIFIES-WORDING.

## Number re-derivation (critic's own runs, not inherited)
- C1 after (bg_2303): errored=7 killed=2 survived=1, check line exact, EXIT 0 (wall 79s). Receipt c1-after-receipt.txt.
- C1 do-nothing (bg_2349): errored=2 killed=5 survived=3, h-sysexit/h-osexit/h-sigkill killed=yes, h-atexit/h-thread killed=no, EXIT 0 (wall 92s). Receipt c1-control-receipt.txt. Note: my run used --jobs 5 and the control wrapper prints the frozen r94 search sha256 97b8defa... — same as the P2 file.
- C1 forgeries (bg_2350): FA errored=9 killed=0 survived=1; FB errored=1 killed=6 survived=3; FC errored=6 killed=3 survived=1; refused 3/3 EXIT 0 (wall 195s). Receipt c1-forgery-receipt.txt.
- C2 after (bg_2351): arms=16 conform=16 EXIT 0 (wall 122s). Receipt c2-after-receipt.txt.
- C2 do-nothing: L1-filed receipt census/round-95/controls/c2-control-r94-probe.txt says conform=12 (S9/S10/S11 exit=1, S12 exit=hung) EXIT 1; my own re-run (c2ctl2, --jobs 4, started 02:54, pid 23640) is still hung on S12 at time of writing (pid 25819 on fixture-hang.py since 02:54 — consistent with the filed receipt: the r94 probe has no timeout, so the counter kills it at 300 s). My c2ctl2 worker (nohup, launched from a temporary shell) survives the session shell; I will not claim its receipt until it finishes. Inherited filed value stands as the control evidence.
- C2 forgeries: L1-filed census/round-95/controls/c2-forgery-controls.txt: GA conform=15, GB conform=14, GC conform=15, refused 3/3 EXIT 0. My own re-runs: first attempt timed out at 120s (timeout 120 < arms wall ~122s + 3 GA/GB/GC arms runs), second attempt (bg_2426, c2forg2) still in progress at time of writing. I will attach it when it lands; nothing in the filed receipt is contradicted by my partial runs (all arms seen so far conform as filed).
- Pins verified by sha256sum on committed bytes: c1-survivor-search.py 6066508f..., c1-targets.json fb40bf4e..., c2-forgery-probe.py bd83e120..., c2-setup-arms.py dd2da59b... — all match prereg INSTRUMENTS pins.

## Counterexample attempted and why it does not fire (Strongest known counterexample)
- "The cheapest probe edit reaches 16/16" counter: the filed forgery controls GA/GB/GC. My cheap c2-cheap-catchall.py reaches 16/16, BUT so what? The prereg's counted quantity is explicitly "conforming arms of 16 — before 12, after 16", and C2 LIMIT (i) says "the probe's catch-all turns any other exception into exit 2, which no arm binds". The claim NEVER asserts that a caught exception is necessarily a setup error rather than a verdict — it asserts the exit-code discipline on the sixteen arms. A catch-all-that-exits-2 is exactly the r95 probe's documented behaviour. The cheap copy satisfies the counted quantity by construction. Counterexample does NOT fire as a wording falsification.
- Same for C1: "an alternative rule reaches the predicate" counter: my R1 reaches errored=0 killed=9 — nowhere near the predicate errored=7 killed=2 survived=1. The predicate's two positive arms (a127c26 survived, h-ok-admits-one + a491c22 killed) inside the ten ids make the naive "always errored" / "always killed" rules fail. Counterexample does NOT fire.

## Verdict section (per claim, per item)
C1:
  - Predicate re-derived (my run): PASS (errored=7 killed=2 survived=1, check line exact, EXIT 0).
  - Do-nothing control re-derived (my run): PASS (errored=2 killed=5 survived=3, per-channel verdicts as prereg states).
  - Forgeries re-derived (my run): FA/FB/FC refused 3/3. PASS.
  - Axis fit (calibration): CONFIRMED (self-assessment vs observed state; knowledge entry mutant-crash-is-not-a-kill.md).
  - h-sysexit is a crash: CONFIRMED in the "counter stopped before judging" sense (rows got=-, knowledge table); raw status 1 alone is not the discriminator, the sentinel is. Limit (ii) covers the false-positive class. No contradiction.
  - Cheap alternative rule (no ITEM / no ROW): FAILS the predicate (errored=0 killed=9). The sentinel's ROW-rc leg is required.
  - Universals: enumerated except "any os._exit call" (os._exit(0) -> rc=70, untested, LIMIT (iii) does not name it). Robustness note only.
C2:
  - Predicate re-derived (my run): PASS (arms=16 conform=16, EXIT 0).
  - Do-nothing control: filed receipt conform=12 EXIT 1 stands; my re-run still hung at 300s kill deadline (consistent). Not independently re-derived at time of writing — L1's filed value is the evidence.
  - Forgeries: filed receipt GA=15 GB=14 GC=15 refused 3/3 EXIT 0 stands; my re-run in progress. Not independently re-derived at time of writing.
  - Axis fit (operability): CONFIRMED (exit-code contract; routed defect 3 is an operability defect).
  - Cheap edit reaching 16/16: YES (c2-cheap-catchall.py, receipt c2-cheap-probe-receipt.txt, 55s vs 122s). Implies: the counted quantity binds exit codes only; disclosed by limits (i)(iii). Not a falsification.
Separability: CONFIRMED both directions (stdlib-only, zero cross-refs, disjoint file sets, positives inside each predicate).
Universals: every claim-carrying universal is enumerated; unbound ones are disclosed. No falsification.

FALSIFIES-WORDING: none found. FALSIFIES-NUMBER: none found.
NO-FALSIFICATION — with what was tried (cheap rules in both directions, cheap probe special-case, hook universal probes on os._exit(0) and helper-sys.exit, cross-ref / separability grep, pins).
Robustness notes for the L1 (never widened; recorded in plans/round-95.md only if the L1 chooses):
  1. "any os._exit call (incl. os._exit(0))" — the hook turns a normal os._exit(0) into rc=70/errored; untested, LIMIT (iii) does not name it. Recommend a one-line narrowing note.
  2. The C2 counted quantity (16/16) can be reached by filename-substring special-casing + catch-all (my cheap probe) in 55s vs 122s. Limits (i)(iii) already disclose the class; no action needed beyond noting.

## Files written by this seat (absolute paths; absolute UTF-8 evidence paths)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic.md (this report; Report: trailer below)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/c1-after-receipt.txt (C1 after, my run bg_2303)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/c1-control-receipt.txt (C1 do-nothing, my run bg_2349)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/c1-forgery-receipt.txt (C1 forgeries, my run bg_2350)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/c1-noitem-rule.py (cheap C1 rule variant; sha256 10d1b431cec41a42c15213586c2aeed7376f132283855ee6cc03953002ef4b9d)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/c1-cheap-rule-receipt.txt (cheap C1 rule run, errored=0 killed=9)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/c1-noitem-rule-notes.txt
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/c2-after-receipt.txt (C2 after, my run bg_2351)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/c2-cheap-catchall.py (cheap C2 probe; sha256 3ef46230a9b26e32e3ed2dd63bd5b7b90b7b1764f971f53f91b8baa1a6db94a6)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/c2-cheap-probe-receipt.txt (cheap C2 probe run, conform=16, 55s)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/c2-cheap-probe-notes.txt
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-95/w1/R95Critic/hook-universals.txt (os._exit(0)/helper-sys.exit probes, file-shape)

Scratch (to be deleted before yield): /fast/scratch/hyaku/souji-r95/R95Critic/ (c1r95/c1ctl/c1forg/c1cheap/c2arms/c2cheap/c2ctl/c2ctl2/c2forg/c2forg2/hooktest + .txt receipts).

Report: .ufo/waves/round-95/w1/R95Critic.md
- C2 do-nothing: my own re-run now COMPLETE (c2ctl2): ARMS-SUMMARY arms=16 conform=12 (S9/S10/S11 exit=1, S12 exit=hung), EXIT 1. Matches filed receipt exactly. (My earlier "still in progress" note now stale.)
- C2 forgeries: my re-run (c2forg2) shows GA conform=15 refused=yes, GB conform=14 refused=yes before the 300s timeout killed the GC arm run. Partial re-derivation confirms the filed receipt (GA=15, GB=14); GC=15 not re-derived in this run but matches the filed receipt's pattern. Filed receipt stands as the GC evidence.

Updated final verdicts:
C2 do-nothing control: PASS (my run conform=12). C2 forgeries: PASS as filed (GA/GB re-derived by me; GC filed, not re-derived due to timeout — same value, no contradiction).

- Additional receipts (added after verdict): c2-control-receipt.txt (C2 do-nothing, my run c2ctl2, conform=12), c2-forgery-receipt.txt (C2 forgeries, partial-then-filed; GA/GB re-derived, GC as filed)
