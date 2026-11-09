# R97ReviewerShapes — Q172 declared-shape table conformance vs r97 staged wording

Seat: R97ReviewerShapes (reviewer, leaf, no subagents). Lane: souji-shokunin, lane master 053287d4eea5dc6c0e1aff9c2295cff0f0a2a3d9.
Scope: read-only against census/round-97, census/round-94..96, corpus/QUALITY.md, .ufo/waves/round-95/w1/R95Labrat/receipts/. Scratch under /fast/scratch/hyaku/souji-r97/R97ReviewerShapes/ (removed). No git/jj mutation, no tool install, no frozen file touched.

## Headline
- **FALSIFIES-WORDING** (2 sentences, plus one Q172 gap; details below). Numbers all reproduce. No FALSIFIES-NUMBER.

## 1. Control and table receipts (live re-runs, same command shape as the predicate)

| hook (search file) | command | result | EXIT | expected |
|---|---|---|---|---|
| r97 (census/round-97/c1-survivor-search.py) | declared-shapes.py --search ... --scripts census/round-97/shapes | `SHAPES-SUMMARY shapes=14 mismatched=0` | 0 | 0 |
| r96 (census/round-96/c1-survivor-search.py) | same | `SHAPES-SUMMARY shapes=14 mismatched=2` (x1, x2 hooked=1) | 1 | 2 |
| r95 (census/round-95/c1-survivor-search.py) | same | `SHAPES-SUMMARY shapes=14 mismatched=2` (t1, t4 hooked=70) | 1 | 2 |
| r94 (census/round-94/c1-survivor-search.py) | same | `SHAPES-SUMMARY shapes=14 mismatched=6` (v3,w1,w2,a3b,x1,x2 hooked=3/1; t1,t4 ok) | 1 | 6 |

The committed P2 receipts (census/round-97/controls/shapes-r9{5,6,7}.txt) match these lines exactly. Copies: receipts/r94-out.txt, r95-out.txt, r96-out.txt, r97-out.txt.

Per-shape r97 (all 14 ok): a1,a5,a5b,a4,a12,v1 declared rc3→3; v3,w1,w2,a3b crash 3→70; t1,t4 declared 0→0; x1,x2 crash 1→70.

## 2. Script census (SHAPES tuple in census/round-97/declared-shapes.py vs disk vs R95Labrat)
- SHAPES tuple: 14 names. Present under census/round-97/shapes/: **14/14**. Missing: none.
- Hashes (sha256) vs .ufo/waves/round-95/w1/R95Labrat/receipts/<name>: **12/12 identical** (a1, a5, a5b, a4, a12, v1, v3, w1, w2, a3b, t1, t4). Recomputed, full digests in receipts/ via the sha256 run in this seat's log.
- **x1-module-finally-term.py (sha256 417d0926…) and x2-module-reraise-term.py (sha256 a6b1abfc…) have no R95Labrat receipt** — they are the two new shapes of r97 (`receipts/x1-x2-sha.txt`).
- Disk holds 44 .py files; 30 are not in the table (helpers such as entry.py, runmain.py, sitecustomize.py, thrower.py, and a2/a3/a6-a11/a13/t2/t3/t5-t8/u1-u5/v2/w3/w4). Expected: the table names 14.

## 3. Per-limit verdicts (preregistration C1 STATED LIMITS (i)-(v))

(i) "Fourteen shapes ... a SystemExit caught at a non-module frame is a shape the table does not exercise (a4 is the counterpart)." — **FALSIFIED** as written. a4-caught-then-return.py raises SystemExit(9) inside `main()` and catches it inside `main()` (non-module frame), and is in the table (kind declared, plain 3 = hooked 3). The table DOES exercise it. See FALSIFIES-WORDING #2.
  - Same limit, second half: "A module-level finally whose exception is caught by the enclosing `except` (elig_fin_then_caught) keeps the mark ... it stays errored; that shape is recorded by the wave, not in the table." — The name appears only in the prereg; no fixture exists anywhere in census/, .ufo/waves/round-97/ or corpus/. I wrote it (receipts/elig-fin-then-caught.py): plain rc 0, r97 hook **rc 70** ("SystemExit first raised in helper() of the main script"). The prereg's "stays errored" is the measured behaviour; the prereg is consistent with the measurement. But see #1: the search docstring says otherwise.

(ii) Signal-safe write best-effort (E16/E18 full-pipe marker drop). — NOT TESTED by this seat; the table has no pipe-full arm and I did not construct one. No verdict.

(iii) EH/RERAISE interleaving "(EH, RERAISE, EH, RERAISE on a terminating finally; no RERAISE on a caught exit)" is not a documented guarantee. — **Consistent with measurement.** Module-level event trace (tool id 0, outside the hook's 3–5 range, module frames only):
  - x1-module-finally-term: RAISE EH RERAISE EH RERAISE
  - x2-module-reraise-term: RAISE EH RERAISE EH RERAISE
  - t1-catch-module-falloff: RAISE EH
  - t4-reraise-at-module: RAISE EH RAISE EH (the `raise saved` re-raise is a fresh RAISE inside a try, caught; no RERAISE)
  The limit names the interleaving honestly; it is one CPython 3.14.8 observation, which the limit already says.

(iv) Harness, population, counter unchanged; r93 routed items 1, 3-4 not addressed. — Out of this seat's table scope; not verified here (the limit disclaims it).

(v) Ten-target summary unchanged across r95/r96/r97 (errored=7 killed=2 survived=1); the claim's quantity is the shape table. — Verified against the committed receipt census/round-97/controls/c1-control-r95-rule.txt (`SEARCH-SUMMARY generated=10 ... errored=7 killed=2 survived=1`, EXIT 0). I did not rerun the ten-target search (out of this seat's scope); the limit's "does not discriminate" reading is consistent with that receipt.

## 4. Prereg claim-vs-table check (does any sentence claim a shape the table lacks?)
- "x1/x2 errored (70), t1/t4 declared (0)": **holds** (table, live).
- "six crash shapes (v3/w1/w2/a3b/x1/x2) at 70 by design": **holds** — and the reasons are the intended channels (stderr measured, receipts/reasons.txt): v3, w1, w2, a3b → "SystemExit first raised in main() of the main script"; x1, x2 → "SystemExit first raised in helper() of the main script". The table's `crash` rule itself only checks hooked==70, not the reason; the reason was measured separately here.
- "a SystemExit caught at a non-module frame": the table has it (a4). The limit wording that says it does not is wrong (see FALSIFIES #2).
- "os._exit(0) call": not in the table, not claimed by the prereg. Measured anyway: osexit0.py plain rc 0 → r97 hook **rc 70** ("SOUJI-R97-CRASH os._exit(0)"). Consistent with the search's `os._exit` channel.
- "twin tool-id collision": not in the table, not claimed. Measured via a fallback probe (below); see observation O1.
- argparse usage error: Q172 (corpus/QUALITY.md line 443) names "argparse's usage error" among the shapes the table must contain "at least". **None of the fourteen is an argparse usage error.** The sentinel's `argparse=2` check line is a separate check, not a table row. This is a Q172 criterion gap, not a sentence of the r97 prereg (the prereg does not claim argparse in the table). Recorded as a gap, not as a falsification of the prereg's sentence.

## 5. FALSIFIES-WORDING

**#1 — census/round-97/c1-survivor-search.py, docstring item 1 (lines 17–19):**
Sentence: "a SystemExit first raised in another module (argparse's usage error), at the top level itself, or one that is caught, is declared and keeps its status."
Reproducer: .ufo/waves/round-97/w1/R97ReviewerShapes/receipts/elig-fin-then-caught.py — a module-level `try: try: helper() finally: pass / except SystemExit: pass` with `helper()` raising SystemExit(1). Plain rc **0**; r97 hook rc **70** (`SOUJI-R97-CRASH SystemExit first raised in helper() of the main script`). A caught SystemExit is therefore NOT declared when a module-level finally sits between raise and catch.
Scope: the prereg (limit (i)) discloses this shape "stays errored", so the prereg is consistent; the instrument's own docstring sentence is falsified by it. Direct-catch without the finally is declared (elig-direct-caught-mod.py: plain 0, hooked 0 — receipts/). Recommended: narrowing amendment in plans/round-97.md (the docstring "one that is caught" → "one caught without a module-level finally between raise and catch"); the L1 decides.

**#2 — census/round-97/preregistration.txt, C1 STATED LIMITS (i), line 73–74:**
Sentence: "a SystemExit caught at a non-module frame is a shape the table does not exercise (a4 is the counterpart)."
Reproducer: census/round-97/shapes/a4-caught-then-return.py (raise SystemExit(9) and except inside `main()`). It IS in the table: `SHAPE a4-caught-then-return.py kind=declared plain=3 hooked=3 ok` (receipts/r97-out.txt). The sentence is false as written; the limit understates the table (the table covers it, a4 is not "the counterpart" of an uncovered shape). Direction: limit overstates what is missing, so it does not widen the claim; it is still a factually false sentence in a frozen file, so it is filed as FALSIFIES-WORDING under Amendment 59.

## 6. Observations (not falsifying any stated sentence)
- **O1 — no-free-tool-id fallback drops the SystemExit leg silently.** With sys.monitoring ids 0–5 all taken (fixture occupier loop, then the r97 HOOK), the hook prints `SOUJI-R97-SENTINEL no free sys.monitoring tool id` and keeps the excepthook/atexit/os._exit/thread channels. A3 holds: `os.get_blocking(2)` is True after the fallback. But a terminating foreign SystemExit (fb-foreign.py: raise SystemExit(1) in helper()) exits **rc 1** under the fallback (plain 1): the leg falls open, undetected by the table (the table's shapes run with a free id). The prereg does not claim the fallback covers the SystemExit leg, so it is not a falsification; it is a limit the prereg does not state. Reproducer: receipts/fb-foreign.py, receipts/fb-uncaught.py (uncaught RuntimeError → rc 70 under fallback, so the excepthook channel does survive). Suggest the L1 consider stating it.
- **O2 — tool-id-claim ordering:** the hook claims ids 3–5 with `range(3, 6)`; any harness counter using ids 3–5 is pre-empted. Not in the table; not claimed.
- **O3 — table's crash rule is `hooked == 70` only.** It does not bind the reason text (Q172 criterion requires an arm "asserts that guard's own reason text"). Reasons were measured separately (receipts/reasons.txt, all six correct) but the instrument itself does not check them. This is the Q172 "reason text" clause applied to the table, not to the sentinel's own CHECK.

## 7. Residual risk and verification gaps
- Not done: pipe-full marker (limit ii); harness/population/counter (limit iv); the ten-target search rerun (limit v, verified only against the committed receipt); the 20-arm C2 counter and forgery controls (other seats).
- The table contains 14 shapes chosen by the L1; no argparse usage error (Q172 gap, see §4).
- CPython 3.14.8 only; the EH/RERAISE interleaving (§3 iii) is measured on this host, not documented.

## Verdict
FALSIFIES-WORDING: (#1) census/round-97/c1-survivor-search.py docstring item 1 "or one that is caught, is declared" — falsified by elig-fin-then-caught (plain 0, hooked 70). (#2) census/round-97/preregistration.txt C1 limit (i) "a SystemExit caught at a non-module frame is a shape the table does not exercise" — falsified by a4 in the table.
FALSIFIES-NUMBER: none. Reproduced: r97 mismatched=0; r96 mismatched=2; r95 mismatched=2; r94 mismatched=6; census 14/14 present, 12/12 R95Labrat hashes identical, x1/x2 new.
