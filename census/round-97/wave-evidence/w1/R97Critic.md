# R97Critic — round 97 wave 1 critic report

Seat: R97Critic. Targets: falsify C1 / C2 wording, axis fit, separability, do-nothing controls.
All reproducers below are under `.ufo/waves/round-97/w1/R97Critic/` (seat dir) unless absolute scratch path given.
Frozen instruments were never modified; scratch was `/fast/scratch/hyaku/souji-r97/R97Critic/` (deleted before yield).

## 1. C1 — "calibration": does the predicate measure self-assessment vs observed state, or only rc's on 14 fixed files?

Claim sentence tested: "The r97 search ... replaces the immediate clear with a RERAISE-aware pending-clear latch ...
On the 14-shape declared-exit table ... the r97 hook keeps t1/t4 declared (0) and keeps x1/x2 errored (70).
Counted quantity: declared-exit shapes the hook turns into 70 (x1/x2): before 2 false-declares under the r96 hook
(rc 1, wrong), after 0 (rc 70, correct)."

What the predicate actually checks (prereg lines 47-56, verified against
`census/round-97/c1-survivor-search.py` `main()` and `declared-shapes.py`):
- the `# crash-sentinel ... check=pass ...` line (7 CHECK modes with fixed want_rc/reason),
- `SEARCH-SUMMARY generated=10 ... errored=7 killed=2 survived=1`,
- `SHAPES-SUMMARY shapes=14 mismatched=0` where `mismatched` is computed by `declared-shapes.py` as plain-vs-hooked
  rc equality (declared) or hooked==70 (crash) over 14 FIXED files listed in `SHAPES`.

No step observes a RAISE/EH/RERAISE event, the latch state, or any self-assessment other than the final rc.

Alternative-rule experiment (cheap hooks NOT using `sys.monitoring`, run in scratch under
`/fast/scratch/hyaku/souji-r97/R97Critic/pattern/hook/sitecustomize.py`, final copy in seat dir as `sitecustomize.py`):
- Rule "stderr non-empty => crash": fails — all 14 shapes run plain with empty stderr and rc in {0,1,3}, so it
  predicts every shape declared; mismatched=6 (all six crash shapes). Receipt: own run table in transcript.
- Rule "plain rc==1 => crash, else declared": fails — v3/w1/w2/a3b are crash shapes with plain rc==3, same as
  declared shapes a1/a5/a12/v1 (rc==3); mismatched=4. Plain runs are externally indistinguishable:
  a1 vs v3 both exit 3 with empty stdout/stderr (verified); only the raise frame differs, which requires
  monitoring or source analysis. This part SUPPORTS the claim: no purely black-box rc/stdout/stderr rule separates
  the table.
- Source-text pattern hook (reads `sys.argv[0]` source at import, atexit-on-SystemExit pattern match for
  `finally:` / uncaught function-raise / module `except: raise`): after two iterations reached mismatched=4
  (caught shapes a4/t1/t4 contain the same indented `raise SystemExit` text as terminating ones; a12's
  module raise is also indented). Getting the last 4 right needs parse-level caught-vs-terminating analysis
  (AST or exception-event semantics), i.e. essentially the same information the latch uses. Honest result: I did
  NOT reach mismatched=0 with a grep-level pattern.
- Filename-table hook (basename-keyed canned rc): WOULD trivially print mismatched=0 on the 14 fixed files, and
  with the same 4 crash-channel hooks would print the check line (`souji_r97_check.py` basename is fixed in
  `c1-survivor-search.py` `main()`). I did not build/run this because it would only restate the known
  file list, but its possibility exposes the axis-fit point below.

Axis verdict for C1: the COUNTED quantity (x1/x2 at 70, t1/t4 at 0 over 14 L1-chosen files) measures rc-70-ness
on a fixed table. It does not measure "the lane's self-assessment vs observed state" in any runtime sense —
the search's verdict function `verdict()` (c1-survivor-search.py:302-314) is a pure function of harness rc/ROW
lines and was UNCHANGED from r95/r96; what changed is the hook's rc production. The prereg itself concedes at
limit (i) that the table is "a precondition, not a census of every exit shape a counter can have" and at limit
(v) that the ten-target summary "does not discriminate this claim". So the calibration label rests on narrative
(r96 declared x1/x2 at rc 1 = wrong) rather than a measured self-vs-observed agreement quantity that any
non-latch mechanism meeting the predicate would falsify. A basename-table hook meeting both predicate lines
would falsify the sentence "the r97 search replaces the immediate clear with a RERAISE-aware pending-clear
latch ... keeps x1/x2 errored" only as to MECHANISM ATTRIBUTION, not as to outcomes.

FALSIFIES-WORDING (C1, mechanism attribution): the predicate lines above are satisfiable in principle without
the latch (basename-table hook + crash-channel hooks); the counted quantity therefore does not prove the latch
ran. Reproducer class, not a full run: shape list fixed in `declared-shapes.py:13-28` (14 names), check filename
fixed in `c1-survivor-search.py` `main()` (`souji_r97_check.py`), verdict pure in rc/rows (`verdict()` :302-314).
My grep-level pattern attempts show small static patterns do NOT reach mismatched=0, so this is a
predicate-strength finding, not a demonstrated passing cheat. Severity: wording narrows to "rc outcomes on 14
files"; the latch's necessity is not measured. The prereg's own limits (i),(v) already concede most of this.

## 2. C2 — "operability": cheapest probe edit to 20/20 without pipe discipline

Cheat built in scratch (`/fast/scratch/hyaku/souji-r97/R97Critic/cheat/cheat-probe.py`, copy in seat dir):
a 3-line insertion into `census/round-97/c2-forgery-probe.py` `main()` — if `basename(fixture)` is not
`r93-k4-flagfail.py` / `r92-k4-flagfail.py`, raise `Fatal` (exit 2 + `C2-FORGERY-FATAL:` line) immediately,
with NO selector pipe wait, NO `--max-output` cap, NO timeout handling, NO grandchild reaping by the probe.
Diff:
```
199a200,202
>     import os as _os
>     if _os.path.basename(fixture) not in ("r93-k4-flagfail.py", "r92-k4-flagfail.py"):
>         raise Fatal("CHEAT basename: non-verdict fixture refused immediately (no pipe discipline)")
```

Run (receipts = seat dir `*.out` + transcript):
`census/round-97/c2-setup-arms.py --probe <cheat> --fixture-pass tests/fixtures/r93-k4-flagfail.py
--fixture-fail tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py
--before census/round-92/controls/c2-before-tool.py --work <empty scratch> --jobs 4`
Result: `ARM T1 exit=2 ... survivors=0`, `ARMS-SUMMARY arms=20 conform=20`, EXIT 0, wall 54.6 s
(faster than the ~5 min real run because S12/T1 never wait 120 s). Full 25-line ARM table in transcript.

Why it works — the counted quantity is gameable:
- Every non-P arm wants exit 2 + FATAL line; an immediate Fatal satisfies both without running the fixture at
  all. P1/P2/S1 legitimately need the real verdict path, which the cheat keeps for the two named basenames.
- S9/S10/S14 (mutated tool/before with the real fixture basenames) still go through the real paths and Fatal
  correctly; S7/S8/S12/T1/T4 use counter-written fixture basenames and are refused instantly.
- `survivors=0` on T1 is trivially achieved: the probe never spawns the pipe-holder fixture, so there is no
  grandchild to reap; and in the genuine design the reaping is done by the COUNTER
  (`c2-setup-arms.py` `one()`, argv-identity SIGKILL), not by the probe. The predicate therefore does not
  observe the probe's pipe discipline at all on T1.

FALSIFIES-WORDING (C2): the sentence "the r97 probe ... caps captured output (--max-output, 8 MiB default; a
fixture over the cap is a setup failure), and the r97 counter ... reaps the T1 grandchild by argv identity"
describes mechanisms the predicate never exercises for the claimed arm. The predicate
(`ARMS-SUMMARY arms=20 conform=20` + `survivors=0`) is met by a basename special-case with no cap, no selector
wait, and no reaping. Reproducer: `cheat-probe.py` + `arms` run above (seat dir `*.out`, `cheat-probe.py`).
The prefreeze note ("twenty-arm counter conform=20 with survivors=0") measured only this same printable
predicate, so it shares the blind spot. The after-receipt re-run on committed bytes does not close it either.
Implication for the counted quantity: "conforming arms of 20" and "survivors=0" as printed cannot distinguish
real operability (cap + timeout + reap) from immediate refusal of non-verdict inputs. A minimal tightening
would require observing the probe's actual cap/kill behavior (e.g. a fixture emitting >8 MiB that must exit 2
QUICKLY with its process group dead, plus a fixture run whose output is consumed to completion) — not present
in the frozen arms.

Note the near-miss that strengthes this: the furnished GD forgery ("claims setup refusal without reaping")
is refused ONLY because the counter itself kills and counts T1 processes (forgery runner special-cases GD
surv>0). The counter's identity reap is what scores survivors, so the probe's own T1 behavior is unobserved —
confirmed by my cheat passing without any reap logic.

## 3. Separability

- Files: `grep -l c2-` over `c1-survivor-search.py, declared-shapes.py, c1-targets.json` = none;
  `grep -l c1-` over `c2-forgery-probe.py, c2-setup-arms.py` = none. No imports, no shared helper files.
- C1 predicate invokes only c1 search + declared-shapes (+ shared counter/harness/population, all unchanged
  r93/r87 files). C2 predicate invokes only c2 probe + c2 arms (+ unchanged fixtures/tool/before).
- The two claims CAN each be verified with the other not landed: C1's search/shapes do not reference the c2
  probe or arms counter; C2's probe/arms do not reference the c1 search, hook, or shape table. The only shared
  surface is the work-dir convention and the harness clones (C1), which C2 does not use.
- Verdict: separable. Neither claim's predicate reads the other claim's instruments.

## 4. Universal words in prereg not enumerated by the counters

- Line 11: "never repaired silently (Amendment 59)" — process rule, not counted (intentionally out of scope).
- Line 63: "No work does not reach mismatched=0 with x1/x2 at 70 and t1/t4 at 0." — universal over "no work";
  enumerated only by the r95/r96 hooks on the 14 files (P2 receipts shapes-r95/shapes-r96.txt). Not enumerated:
  any other mechanism (e.g. a pattern/basename hook). Weaker than it reads. (See section 1.)
- Line 71: "a sentinel without the RERAISE latch do[es] not meet the predicate" — same scope limit: the FE
  forgery evidence covers only the 14-file table + 10-target summary, not "the predicate" as a general
  mechanism claim.
- Line 90: "the counter never reaps it (A4)" for the r96 counter — past-tense enumeration via r96 receipts,
  consistent with the filed r96 counter behavior; no counterexample in round evidence, but the universal is
  about the OLD instrument, vacuous for r97 correctness.
- Line 102: "S13 names an absent /tmp path it never creates" — enumerated by arm S13 (verified in r97 arms:
  conform=yes). No issue found.
- Line 105: "all unchanged" — hash-pinned in receipts (search arm headers print sha256 for probe/counter/
  fixtures/tool/before). Enumerated.
- Line 114: "No work does not reach survivors=0 with conform=20." — REFUTED in the narrow sense of section 2:
  my basename cheat reaches survivors=0 with conform=20. Exact sentence falsified; reproducer `cheat-probe.py`
  + arms run above. The intended reading ("no work OF THE CLAIMED KIND") is not stated in the sentence.
- Line 119: "the counter's identity check kills any arm whose T1 process is still alive" — code-read confirmed
  (c2-setup-arms.py `one()`: argv-identity SIGKILL + survivor count). Enumerated, but note this is the counter
  killing, not "any arm" erroring — GD is refused through the runner's GD special-case, not through conform.
- Line 120: "turning every failure into exit 2" — GA forgery evidence covers verdict-exit 2, not a probe that
  exits 2 for non-verdict fixtures (my cheat does exactly this and passes). The universal reads broader than
  the evidence.
- Line 123: "the counter never signals a pid it did not plant" — code-read: reap loop keys on argv==fixture
  path + before/after (pid,starttime,boot_id) identity set (`c2-setup-arms.py`). True as written on this
  host per stated limit (i) ("recycled argv token ... on this host"). Cross-host / pid-reuse beyond boot_id
  is explicitly out of the stated limit, so no falsification; flagging only that the universal is
  host-scoped while phrased absolutely.

## 5. Per-item verdicts

C1 (calibration): predicate met by the frozen instrument (P2 receipts shapes-r97.txt mismatched=0; I did not
re-run the 10-target search — ~20 s x clones, stated unchanged across r95-r97 in the prefreeze note and
limit (v)). FALSIFIES-WORDING as to mechanism attribution and axis fit: the counted quantity is rc-70-ness on
14 L1-chosen files; a basename-table hook would print the same SHAPES-SUMMARY without the latch (demonstrated
possible in principle; my non-latch grep-level pattern hooks did NOT reach mismatched=0 — transcript
mismatched 6/1/4 — so this is predicate-strength, not a passing non-latch run). No FALSIFIES-NUMBER: the
printed numbers (mismatched=0 after, 2 before; t1/t4 0, x1/x2 70) re-derive from the P2 receipts and my own
hooked runs of the frozen hook for all 14 shapes.

C2 (operability): predicate MET by a 3-line basename cheat without cap/timeout/reap (full arms run, EXIT 0,
conform=20, survivors=0). FALSIFIES-WORDING: line 114 "No work does not reach survivors=0 with conform=20"
is false as stated; reproducer `.ufo/waves/round-97/w1/R97Critic/cheat-probe.py` with the arms command in
section 2; outputs `P1.out..T4.out` in this seat dir (T1.out includes `--survivors 0 planted-killed 0--`).
Also FALSIFIES-WORDING as to what the counted quantity proves: conform/survivors do not observe pipe
discipline; the T1 reap is performed by the counter, and the probe never needs to spawn or kill the
pipe-holder fixture. No FALSIFIES-NUMBER for the genuine instrument's printed results (P2/L1 receipts carry
conform=20 survivors=0 for the real probe; my run reproduces the same printed predicate with the cheat).

## NO-FALSIFICATION summary

- C1 numbers: NO-FALSIFICATION — every printed rc/mismatched value re-derived for the frozen hook; the only
  C1 finding is the predicate-strength / mechanism-attribution wording point (section 1).
- C2 numbers for the genuine instrument: NO-FALSIFICATION — the real probe's printed conform=20/survivors=0
  is consistent with P2 receipts; the falsification is that the same lines are reachable without the claimed
  mechanism (section 2). The L1 should treat the C2 counted quantity as not measuring the claimed operability.
- Separability: verified clean (section 3). Universal-word audit: lines 63/114/120 are the exposed
  universals (section 4).

Scratch cleanup: `/fast/scratch/hyaku/souji-r97/R97Critic/` removed before yield. No tools installed.
No frozen files modified. No subagents dispatched (leaf member).
