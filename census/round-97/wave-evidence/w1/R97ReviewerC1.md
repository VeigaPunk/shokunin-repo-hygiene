# R97ReviewerC1 — C1 correctness review (r97 crash sentinel / RERAISE-aware clear / signal-safe write / kill rule)

Seat: R97ReviewerC1. Lane souji-shokunin, cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Scope: `census/round-97/c1-survivor-search.py` (HOOK ll.106-237, CHECK ll.238-261, CHECKS l.262,
verdict ll.302-314, score ll.317-353, main/precondition ll.370-483),
`census/round-93/c1-false-row-harness.py` (counter invocation ll.458-558, every ROW branch),
prereg C1 (`census/round-97/preregistration.txt` ll.24-83). Frozen pins re-verified this run:
search `b8efc240…`, harness `1868a570…`, counter `fd0a8e24…`, targets `320ea2ec…` (all match prereg
INSTRUMENTS). Host Python 3.14.8. Receipts (text only, no clones):
`.ufo/waves/round-97/w1/R97ReviewerC1/receipts/` (scripts + frozen-hook copy).
Scratch `/fast/scratch/hyaku/souji-r97/R97ReviewerC1/` deleted before yield; no tool install (none needed).
Prior-round continuity: r96's R96ReviewerC1 found the same-object re-raise escape (their q1e) and called it
narrowing-grade FALSIFIES-WORDING; this seat re-tested that shape under the r97 latch (it still escapes — q1o
below) and found a second, novel r97-specific hole (q1q): a stale pending candidate clears a live terminating
mark belonging to a *different* exception object. q1q is a strict regression vs r96 (r96: 70, r97: 1).

## Q1 — top-level-handled clear (RERAISE-aware pending-clear latch)

**Verdict: correct on the filed 14-shape table (re-run: `SHAPES-SUMMARY shapes=14 mismatched=0`, EXIT 0,
per-shape ok lines observed) but the latch clears in two cases the wording says it must not: a terminating
explicit re-raise of a saved exception (q1o, hooked 1) and ANY terminating helper exit that follows an
earlier caught-at-module exit, via a stale pending candidate for a different object (q1q, hooked 1 — r97
regression).**

Mechanism recap (search ll.156-211): `_souji_raise` (RAISE, l.156) latches `foreign` at `<module>` for a
`SystemExit` first raised in a non-`<module>` frame of the main script. `_souji_handled` (EH, l.172) records
a pending candidate in `_SOUJI_ELIG[key]="pending"` (only if `latched` and frame is `<module>`) and sets
`_SOUJI_STATE["pending_key"]`. `_souji_reraise` (RERAISE, l.193) cancels a pending key to `"no"`.
`_souji_atexit` (l.204) flushes a still-pending key: pops `_SOUJI_SEEN[pending_key]`, and if its recorded
first-raise function equals the (current) `foreign`, clears `foreign` and exits declared; else crash 70.

Scratch results under the frozen HOOK (`receipts/q1*.py`; `plain` = no hook, `r97` = frozen HOOK):

| script | `plain` | `r97` | reading |
|---|---|---|---|
| q1a caught inside `main()`, returns 9 | 9 | 9 | non-module catch: never marked ✓ |
| q1b caught inside `main()`, pass | 9 | 9 | ^ ✓ |
| q1c caught at `<module>`, falloff | 0 | 0 | t1 shape ✓ |
| q1d module `finally`, terminating | 1 | 70 | EH,RERAISE pair cancels pending ✓ |
| q1e module `except: raise`, terminating | 1 | 70 | RERAISE cancels ✓ |
| q1f `sys.exit(helper())` (new int SystemExit) | 0 | 70 | first-raise-in-helper terminating ✓ (declared exit 0 → crash: by design, helper-raised) |
| q1g `finally` **inside `main()`, terminating** | 1 | 70 | finally in fn does not clear ✓ |
| q1h `except: raise` **inside `main()`, terminating** | 1 | 70 | ^ ✓ |
| q1i outer `try: try: helper() finally: pass except SystemExit: pass` (caught) | 0 | 70 | **fires on an exception that IS caught at `<module>` via the enclosing `except`** (prereg limit (i) acknowledges this shape: "keeps the mark… it stays errored") — disclosed limit, not new |
| q1j new `SystemExit(2)` raised in `main`'s except, terminating | 2 | 70 | fresh object, no EH cancellation ✓ |
| q1k caught in `main`, `return 7` then `sys.exit(7)` | 7 | 7 | int-exit declared ✓ |
| q1l `except SystemExit: raise SystemExit(2)` in main | 2 | 70 | new-object terminating ✓ |
| q1m EH at `<module>` then `except SystemExit: pass` + `finally: pass`, falloff | 0 | 0 | caught-at-module-but-finally outer ✓ |
| q1n `raise main()` at module, `main` re-raises fresh | 1 | 70 | ✓ |
| **q1o SAVE-THEN-BARE-RAISE, uncaught** (`try: helper() except SystemExit as e: saved=e` then `raise saved`) | 1 | **1** | **terminating explicit re-raise escapes** (see FALSIFIES-WORDING) |
| q1p first caught in `main`, then NEW `SystemExit(5)` in `main` terminating | 5 | 70 | second object terminates ✓ |
| **q1q CAUGHT-AT-MODULE then DIRECT `helper()` terminating** (two distinct objects) | 1 | **1** | **stale pending clears live mark** (see FALSIFIES-WORDING; r96 gives 70) |
| q1r caught in `main` then new terminating in `main` | 5 | 70 | ✓ |

Full 44-shape sweep (all filed `shapes/*.py`) also reproduced: t1/t4 0, x1/x2 70, v3/w1/w2/a3b 70,
a1/a4/a5/a5b/a12/v1 declared-unchanged; u2-shutdown-del-falloff 70 (unraisable), etc. No other surprises.

**FALSIFIES-WORDING (narrowing-grade, two reproducers).**

- **q1o** (`receipts/q1o.py`: plain 1, r97 hooked 1, want 70). The prereg describes the r96 bug as "clears a
  terminating exit that passes through … an explicit module-level re-raise" (prereg ll.29-31) and the instrument
  docstring (search ll.27-29) promises the latch clears "only when the same exception object never re-raised
  after its first module-level EH". A traceback-level trace (scratch dbg hook) shows `raise saved` outside
  the `except` block fires **RAISE but not RERAISE** on CPython 3.14.8: the latch never invalidates the
  pending candidate, and the atexit flush then clears the mark that the second RAISE re-lathed. A terminating
  helper-originated `SystemExit` is scored declared (hooked 1, no marker). q1o is the identical construction
  r96's reviewer filed as q1e; the r97 latch was the round's chance to close it and does not. (Control:
  with the second raise *inside* `try/except: pass` — the filed t4 shape — hooked 0 is correct because the
  exception is genuinely caught.)
- **q1q** (`receipts/q1q.py`: plain 1, r97 hooked 1 with no marker, want 70; **r96 hook gives 70**).
  `try: helper() except SystemExit: pass` (object 1, caught at `<module>`, pending) followed by a direct
  terminating `helper()` (object 2). The atexit flush (`_souji_atexit`, ll.204-211) pops object 1's pending
  record and clears the *current* `foreign` mark — which belongs to object 2 — whenever the recorded
  first-raise function name matches (`seen[2]==foreign`, both `"helper"`). No RERAISE event for either
  object is involved. The flush does not verify the pending object is the terminating object. This is the
  latch's central mechanism misfiring on its happiest path and is a r97 *regression*: the r96 hook scores
  this shape 70 (correct). The counted quantity (14-shape table) is unaffected because the table contains no
  two-object shape — stated limit (i) concedes the table "is not a census of every exit shape" — but the
  claim presents r97 as closing the A1 trade ("replaces the immediate clear with a RERAISE-aware pending-clear
  latch"), and the trade has in fact moved: {finally, reraise-in-except} fixed; {bare re-raise, stale pending
  after any prior module catch} newly broken or still broken. L1 to record as amendment; reproducers are
  `receipts/q1o.py` and `receipts/q1q.py`.

Also noted (not a falsification; unfolds prereg limit (i) further): q1i — an exception that passes through a
module-level `finally` and IS caught by the enclosing `except` at `<module>` stays 70 (the EH/RERAISE pairing
still cancels the pending candidate even though a later EH genuinely catches it). The prereg discloses this
exact shape ("keeps the mark by the same latch (it stays errored); that shape is recorded by the wave, not in
the table"), so no surprise; a future table should pin q1i (want 70), q1o (want 70), and q1q (want 70).

## Q2 — signal-safe write (deadlock / full-pipe)

**Verdict: as stated. No deadlock from a signal handler, no hang on a full undrained pipe on any crash
channel; the exit code is always 70 and the marker write is best-effort.**

- **Signal handler (E3c shape)**: `receipts/q2m.py` (handler raises `RuntimeError` while a writer thread is
  mid-`sys.stderr.write`) → hooked rc **70 in ~1 s**, no timeout, marker emitted. The `_souji_crash` raw
  `os.write` (HOOK ll.115-130) bypasses the `TextIOWrapper` lock as claimed. Plain rc 1.
- **Thread channel (E16 leg)**: `receipts/q2b_thread.py` (uncaught exception in a worker thread) → hooked rc
  **70**, marker `SOUJI-R97-CRASH thread RuntimeError`; no hang. r97 (A2) crashes before any traceback
  print, as stated.
- **Full undrained pipe (E16/E18)**: `receipts/q2c2.py` (terminating helper exit), `receipts/q2d_unraisable.py`
  (atexit crash), `receipts/q2e.py` (uncaught `RuntimeError`), `receipts/q2i.py` (atexit crash with a 20 000-char
  message), `receipts/q2j.py` (uncaught exception with a 20 000-char message) — each run with stderr = a
  pre-filled (64 KiB = pipe capacity) undrained pipe → all exit **rc 70 in ~0.02 s**, none hangs. Marker is
  dropped on the full pipe (best-effort), exactly stated limit (ii) (`rc=70, marker absent`). Control: a
  plain `sys.stderr.write` + `flush` on the same full pipe *does* hang (verified >3 s), so the harness is
  capable of detecting the hang and the hook genuinely avoids it.
- **One residual asymmetry, no measured harm**: `_souji_unraisable` (HOOK ll.139-144) still
  `print_exception()`s *before* `_souji_crash` (only the excepthook/thread channels were reordered by A2).
  Empirically the print stays in the `TextIOWrapper` buffer for every shape tried (up to 20 000 chars) and
  the process then `_exit(70)`s without flushing, so no hang and no observable difference. A pathological
  unraisable whose formatted traceback alone exceeds the buffer capacity *and* whose first flush blocks
  cannot be excluded, but no scratch reproducer produced a hang. Not a falsification.
- The crash path leaves fd 2 non-blocking (`os.set_blocking(2, False)`, l.121) — the process exits immediately
  via `_SOUJI_EXIT(70)`, so restoration is moot for the crasher; forked children inherit the flag (limit (ii),
  A4 whole-subtree scope, already carried). `sitecustomize`-scope (whole harness subtree) carries as stated.

## Q3 — non-crash mutants reaching `errored`

**Verdict: reachable by design on any declared 70, any signal kill, and any non-0/1 status; the stated rule
is exactly as implemented. No falsification.**

`verdict()` (search ll.302-314) probed directly (`receipts/verdict-probe` not saved; reproduced below in
this run):
- Counter legitimately exits **70 with all rows `match=yes`** → `errored` (`rc=70` row leg, l.308). The rule
  cannot distinguish "counter declared 70" from "sentinel forced 70" — any mutant whose counter exits 70 on
  any row is errored regardless of `match=`. Same for harness exit 70 with `match=yes`.
- Counter **killed by a signal** (git child or counter itself, harness prints `rc=-9`) → `errored` via the
  negative-rc leg (`rc < 0`, l.308); harness exit `<0` likewise. Exactly the filed signal leg.
- Exit 3 with `match=yes` → `errored` ("anything else is errored", l.314). Counter declared exits are
  constrained to 0 (survivor) or 1+`match=no` (killed). A counter exiting 2 (`match=error` setup rows) →
  `errored`.
- `rc=1` + `match=no` row *plus* an `rc=70` row → `errored` (70 leg dominates).
- The regex `r" rc=(-?\d+) match="` (l.307) requires ` rc=` immediately before the digits; a harness
  `detail={stderr[:200]!r}` (harness l.467 etc.) embedding the literal substring ` rc=70 match=` inside
  quoted stderr *would* false-trigger — but every such detail row already forces `errored` via other legs
  (rc≠1-with-match-no), so the spoof channel only matters when a genuine `match=no` row coexists.
  Foreign-captured stderr cannot reach harness stdout except through those quoted detail fields (harness
  pipes counter stdout/stderr; only `got`/marker/detail substrings leak), so no free ROW injection exists.
  Residual risk only; no counter in the population produces such stderr.

Harness `rc=70` sources (harness ll.458-558): **every** ROW branch prints `rc={p.returncode}` of the
counter subprocess (ll.472/513/534/558) or the fixed `rc=2 match=error` (ll.467/508/529/548). There is no
branch where the harness itself prints `rc=70`; a real `rc=70` can only arrive from the hooked counter's
exit status. The ten targets exercise no declared 70, so the predicate is unaffected.

## Q4 — CHECK reason assertion vs cross-wired legs m02/m03

**Verdict: as stated. Both r95 cross-wires are refused by the reason assertion while keeping rc 70.**

Replayed the search's CHECK loop (CHECK ll.238-261, CHECKS l.262, precondition ll.409-420) under one-edit
hook mutants (`receipts/mut/` not saved as files; hook source extracted per mutant in scratch):

- Frozen hook: `excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`, every
  `want_reason` substring present in stderr — `check=pass`. ✓
- **m02** (`threading.excepthook = _souji_excepthook`): thread child still rc 70, marker is
  `SOUJI-R97-CRASH uncaught TypeError` (excepthook wrapper's `getattr(t,"__name__","?")` over thread args)
  → missing `'SOUJI-R97-CRASH thread'` → `C1-SEARCH-FATAL`, exit 2. **REFUSED.** ✓
- **m03** (`os._exit = _souji_excepthook`): osexit child still rc 70, marker `uncaught TypeError` → missing
  `'SOUJI-R97-CRASH os._exit'` → `C1-SEARCH-FATAL` at osexit, exit 2. **REFUSED.** ✓
- Extra: `sys.unraisablehook = _souji_excepthook` → atexit child rc 1 (not 70) → refused by rc.
  `threading.excepthook = _souji_os_exit`-style rewires: rc/reason likewise fail closed.

The reason assertion is a per-mode substring test (l.418), so m02/m03 cannot pass by accident. Residual:
substring (not full-line) matching means a mutant emitting `SOUJI-R97-CRASH threadFake` would satisfy the
thread check — but every such mutant is a one-edit forgery of the frozen bytes, which is the
forgery-controls' remit (FA-FE, all refused per the filed P2 receipt), and it still exits 70. The prereg
sentence ("a cross-wired or missing reason fails closed with C1-SEARCH-FATAL") holds for the m02/m03 pair.

## Q5 — claim wording vs predicate coverage

Predicate = (a) full search run: check line `# crash-sentinel rc=70 check=pass …` + `SEARCH-SUMMARY
generated=10 … errored=7 killed=2 survived=1` + per-id `SEARCH` lines + exit 0; (b) declared-shapes:
`SHAPES-SUMMARY shapes=14 mismatched=0` + exit 0 (re-run this seat: verbatim, EXIT 0, x1/x2 at 70, t1/t4 at 0).

1. **Per-id verdicts** ("errored on h-sysexit, …; yes on …; no on …") — the `SEARCH-SUMMARY` line binds only
   the 7/2/1 counts; a verdict permutation preserving counts passes the summary (and the forgery runner's
   refusal test, which compares summary + shapes only) while violating the sentence. The sentence is enforced
   by the printed `SEARCH <id> … killed=<v>` lines (search l.455), which the prereg presents as predicate
   text ("per-id verdicts unchanged") but which no filed checker diffs. **Gap, not falsification** (true as
   filed; the counted quantity under-binds it). Carried from r96 Q5-1. The L1 after-receipt should diff the
   ten `SEARCH` lines against the r95 ten.
2. **`check=pass` line is fully bound**: rc tuple pinned verbatim (ll.410-421) and the per-channel reason
   assertion is inside the verdict — verified by Q4 mutants refusing with `C1-SEARCH-FATAL`, exit 2.
3. **"keeps t1/t4 declared and x1/x2 errored"** — the shape table binds exactly these (declared kind must
   equal plain; crash kind must be 70). q1o/q1q fall **outside** the table; see Q1 findings. The counted
   quantity is table-scoped, so the count itself is not falsified; the unqualified mechanism claim is.
4. **Do-nothing controls** (r95 hook `mismatched=2` t1/t4; r96 hook `mismatched=2` x1/x2) are consistent with
   the filed table and the knowledge audit; no discrepancy. (Note: the r95 hook on q1d/q1e gives 70,
   i.e. the do-nothing control *agrees* with r97 on x1/x2 — the prereg's discriminating power comes from the
   conjunction, correctly stated.)
5. Anything else the predicate does not check: search timing, harness clone size, full-population re-score —
   reported-not-claimed (limits (iv)), correctly stated.

## Residual risk and verification gaps

- q1o + q1q escapes (Q1). q1q is the sharp one: any counter that catches one `SystemExit` at `<module>` and
  later terminates helper-raised is scored declared. Real counters that catch-then-reraise a *saved*
  `SystemExit` object, or catch one exit then terminate on another, are rare; but a one-line counter edit
  produces either, and the ten targets + 14 shapes do not cover two-object shapes.
- q1i (module `finally` subsequently caught at `<module>`) stays 70 — disclosed in limit (i), noted here only
  to pin it as a future table row.
- `verdict()` detail-string spoof channel (` rc=70 match=` inside a quoted stderr detail): theoretical,
  unreproduced; residual only.
- t2-style shapes (catch inside `main`, never reaching `<module>`) are rc-correct but unexercised by the
  fourteen-shape table; a future table should add them plus q1i/q1o/q1q.
- Full ten-target search predicate **not** re-run by this seat (each run clones ~0.7 GB per mutant; the
  shape table + CHECK replays + verdict probes cover the mechanisms, and the full predicate is the L1's
  after-receipt run). Per-id `SEARCH` lines therefore not independently re-observed this seat — gap stated.
- E3c/E16/E18 reproduced at the hook level (mimicking the filed semantics with scratch scripts), not
  byte-identical to earlier reproducers; semantics match the filed outcomes.

## Verdict

`FALSIFIES-WORDING` (narrowing-grade, Q1 q1o + q1q) — the counted quantity (table `mismatched=0`, summary
`errored=7 killed=2 survived=1`, `check=pass`) is **re-derived and holds**, but the mechanism sentences
 ("a RERAISE of the same object cancels it; atexit flushes a still-pending candidate" / docstring ll.27-29
"the EH leg clears the mark only when the same exception object never re-raised") are falsified by q1q (stale
pending clears a live terminating mark of a different object; r96 gives 70, r97 gives 1) and by q1o
(bare re-raise of a saved object fires no RERAISE and escapes; plain 1, hooked 1). The r97 latch closes the
filed finally/re-raise-in-except trade and opens/moves the trade onto these two shapes; the claim as worded
("closes the trade") overstates. Q2/Q3/Q4 hold with reproducer receipts. Recommended L1 actions: amend with
q1o + q1q + q1i shapes in the table; require the after receipt to diff the ten `SEARCH` verdict lines, not
only `SEARCH-SUMMARY`; note r97's q1q regression vs r96 in the trade ledger. No frozen file modified (pins
re-verified); no git state touched; scratch removed.
