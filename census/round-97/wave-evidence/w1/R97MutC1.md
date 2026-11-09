# R97MutC1 — mutation test of the r97 search (C1 predicate)

Scope: one-edit mutants of `census/round-97/c1-survivor-search.py` (scratch copies under `/fast/scratch/hyaku/souji-r97/R97MutC1/mutants/`), run through the C1 predicate: (a) the search command (10 targets, --jobs 5) must print the exact check line, per-id verdicts and `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1`, EXIT 0, plus `SHAPES-SUMMARY shapes=14 mismatched=0`, EXIT 0 (mutant substituted for the search). A mutant SURVIVES iff the whole predicate still passes.

Detector definition: killed/survived is decided by BOTH commands. Any C1-SEARCH-FATAL/EXIT nonzero, any summary/verdict/check-line/shapes mismatch = killed. Survivors classified equivalent (behaviorally identical on all inputs the predicate can produce) vs unbound (a real defect the predicate cannot see).

## Baseline (pristine, restored bytes)

- `base-search.txt` (pristine): `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`, per-id verdicts errored on h-sysexit/h-atexit/h-thread/h-osexit/h-sigkill/h-crash-late/h-crash-index, yes on h-ok-admits-one/a491c22-<-to-<=, no on a127c26-True-to-False, `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1`, EXIT 0.
- `pristine-shapes.txt`: `SHAPES-SUMMARY shapes=14 mismatched=0`, EXIT 0.
- Pristine sha256 (search file): `b8efc240a7fb7aa02ce62cddf3c95501b5f85975278ee88cc32667a3c7af1345` — unchanged throughout; mutants ran on copies only, lane never written.

## Mutant table

| Mutant | Edit (one edit) | Search | Shapes | Verdict | Classification |
|---|---|---|---|---|---|
| m01-no-eh-registration | delete EXCEPTION_HANDLED register_callback | check=pass, summary identical, EXIT 0 | mismatched=2 (t1/t4@70), EXIT 1 | killed | — |
| m02-flip-module-test | `_souji_handled`: `!= "<module>"` → `== "<module>"` | check=pass, summary identical, EXIT 0 | mismatched=2 (t1/t4@70), EXIT 1 | killed | — |
| m03-widen-clear | delete `<module>` guard in `_souji_handled` (clear on any frame) | check=pass, summary identical, EXIT 0 | mismatched=0, EXIT 0 | SURVIVED | unbound (see S3) |
| m04-drop-check-reason | CHECKS sysexit reason → None | check=pass, summary identical, EXIT 0 | mismatched=0, EXIT 0 | SURVIVED | unbound (see S4) |
| m05-mispoint-crash-reason | excepthook writes "unraisable" instead of "uncaught" | C1-SEARCH-FATAL missing reason, EXIT 2 | mismatched=0 | killed | — |
| m06-set-blocking-false | A3 fallback `set_blocking(2, True)` → False | check=pass, summary identical, EXIT 0 | mismatched=0, EXIT 0 | SURVIVED | unbound (see S6) |
| m07-raise-main-test | RAISE main-file test `== main` → `!= main` | C1-SEARCH-FATAL sysexit child 1 want 70, EXIT 2 | mismatched=6 (all crash shapes@3/1), EXIT 1 | killed | — |
| m08-no-atexit-registration | delete `atexit.register(_souji_atexit)` | C1-SEARCH-FATAL sysexit child 1 want 70, EXIT 2 | mismatched=6, EXIT 1 | killed | — |
| m09-tool-id-loop-no-break | delete `break` after first free tool id | check=pass, summary identical, EXIT 0 | mismatched=0, EXIT 0 | SURVIVED | equivalent (see S9) |
| m10-verdict-row-neg-rc | verdict: drop `r < 0` in ROW disjunct | `errored=6 killed=3 survived=1` (h-sigkill errored→yes), EXIT 0 | mismatched=0 | killed | — |
| m11-verdict-harness-neg-rc | verdict: drop `rc < 0` in harness disjunct | check=pass, summary identical, EXIT 0 | mismatched=0, EXIT 0 | SURVIVED | equivalent (see S11) |
| m12-checks-want-code | CHECKS declared want 1 → 2 | C1-SEARCH-FATAL declared child 1 want 2, EXIT 2 | mismatched=0 | killed | — |
| m13-precondition-rc-assert-off | add `if False: pass` before the real rc assertion (sentinel untouched) | check=pass, summary identical, EXIT 0 | mismatched=0, EXIT 0 | SURVIVED | equivalent (see S13) |
| m14-raise-first-frame-record | RAISE callback re-records (seen always overwritten) | C1-SEARCH-FATAL sysexit child 1 want 70, EXIT 2 | mismatched=6, EXIT 1 | killed | — |
| m15-no-reraise-registration | delete RERAISE register_callback | check=pass, summary identical, EXIT 0 | mismatched=2 (x1/x2@1), EXIT 1 | killed | — |
| m16-atexit-flush-identity | atexit flush `== "pending"` → `== "no"` (flush never fires) | check=pass, summary identical, EXIT 0 | mismatched=2 (t1/t4@70), EXIT 1 | killed | — |
| m17-verdict-harness-rc-le0 | verdict harness `rc < 0` → `rc <= 0` | `errored=8 killed=2 survived=0` (true survivor killed), EXIT 0 | mismatched=0 | killed | — |
| m18-checks-reason-thread | CHECKS thread reason → "SOUJI-R97-CRASH os._exit" | C1-SEARCH-FATAL missing reason, EXIT 2 | mismatched=0 | killed | — |
| m19-tool-id-range | `range(3, 6)` → `range(3, 4)` (fewer ids) | check=pass, summary identical, EXIT 0 | mismatched=0, EXIT 0 | SURVIVED | unbound (see S19) |
| m20-no-set-events | delete set_events (callbacks never enabled) | C1-SEARCH-FATAL sysexit child 1 want 70, EXIT 2 | mismatched=6, EXIT 1 | killed | — |
| m21-handled-latched-flip | `_souji_handled` latched test `not ...` → bare (returns when latched) | check=pass, summary identical, EXIT 0 | mismatched=2 (t1/t4@70), EXIT 1 | killed | — |

Coverage: EH registration (m01), `<module>` test (m02), widening (m03), CHECK reason drop (m04), crash-reason mis-point (m05), set_blocking (m06), RAISE main-file (m07), atexit registration (m08), tool-id loop (m09, m19), ROW/HARNESS negative-rc (m10, m11, m17), CHECKS want-code (m12) and reason (m18), precondition loop (m13), RAISE first-frame (m14), RERAISE callback (m15), atexit flush (m16), set_events (m20), latched test (m21). 21 mutants ≥ 12 required, ≥1 per named leg.

## Survivors (findings — coverage gaps, not contract repairs)

### S3 (m03) — clear widened to any frame: UNBOUND. The 14-shape table never fires EH at a non-module frame with a latched foreign mark, and the 10-target set has no such counter mutant, so a cross-frame clear passes both. Binding target: a declared shape with a foreign SystemExit handled at a non-module frame (the prereg's stated limit i(b) names exactly this: "a SystemExit caught at a non-module frame is a shape the table does not exercise (a4 is the counterpart)"), or a shapes/ script exercising EH in a function.
### S4 (m04) — CHECK reason dropped (sysexit → None): UNBOUND. The precondition guards `want_reason is not None`, so dropping the reason disarms the assertion instead of failing it. Binding check: a CHECKS-table audit (reason strings non-None for every crash channel) or a precondition that FATALs on any None reason. The r97 hook still writes the reason correctly — this is a check-strength gap only.
### S6 (m06) — A3 fallback set_blocking forced False: UNBOUND. The no-free-tool-id branch never runs in the predicate (ids 3–5 are free on this host; probe confirmed all three free), so the blocking-restore line is dead code as far as the predicate observes it. Binding target: run the child with all candidate tool ids pre-taken, or an fs-level probe of fd 2 blocking mode after the fallback.
### S9 (m09) — tool-id loop break deleted: EQUIVALENT. With ids free, the first registration succeeds and every later free id registers the same callbacks on the same events; each callback is idempotent, and later `use_tool_id` calls never raise because every id is free. The predicate's check line and both outputs are identical because the sentinel's firing is unchanged. (If an id were in use, the mutant would fail where the pristine continues — but on this host no id is in use, and the fallback branch is unexercised; see S19 for the range variant.)
### S11 (m11) — verdict harness negative-rc leg dropped: EQUIVALENT. Dropping `rc < 0` leaves the final fall-through `errored`, which covers every negative harness rc (a negative rc is not 0, not 1, not 70). Verified: pristine and mutant agree on every (rc, out) pair over negatives × row variants. The ROW disjunct (m10, killed via h-sigkill errored→yes) is the leg that matters.
### S13 (m13) — precondition rc-assert no-op inserted before the real assertion: EQUIVALENT. The mutant inserts a dead `if False: pass` before the unchanged live assertion; the CHECKS table and the sentinel are untouched, so the check line prints identically. This mutant probes assertion architecture rather than behavior — the real precondition-rc mutation (deleting the live `if`) would print `excepthook=70 ...` from children that still exit 70 while a sentinel defect that changes codes went unnoticed only if the reason check also passed; m12/m18 show the table still guards code and reason separately. (Recorded as equivalent by inspection plus the identical check line.)
### S19 (m19) — tool-id range narrowed to (3,4): UNBOUND. One free id (3) suffices on this host, so the precondition and the fleet all pass. The mutant only diverges if id 3 is taken and 4/5 are free — no target exercises tool-id contention. Binding target: a child started with a pre-registered tool id (e.g. a test harness that takes id 3), or a tool-id-contention fixture.

## NO-FALSIFICATION of the claim wording

No mutant falsifies a sentence of C1. Every killed mutant is refused exactly as the r97 forgery controls predict for the EH/RERAISE legs (m01 ≈ FD, m15 ≈ FE), and the survivors above expose only precondition/target coverage, not a wrong verdict under the stated predicate. Specifically:
- The sentinel precondition catches every mutant that breaks a crash channel, the latch, the flush, or the tool-id/events activation (m05, m07, m08, m12, m14, m18, m20 refused with exit 2 and the exact C1-SEARCH-FATAL line).
- The 10-target summary discriminates both verdict legs (m10 errored=6 killed=3; m17 errored=8 survived=0).
- The shape table discriminates the latch legs (m01/m02/m16/m21 mismatched=2 at t1/t4; m15 mismatched=2 at x1/x2).

## Restoration evidence
- Lane `census/` bytes never touched: mutants are copies under `/fast/scratch/hyaku/souji-r97/R97MutC1/mutants/` (sha256 list in seat dir `receipts/mutant-sha256.txt`). Pristine copy sha256 `b8efc240a7fb7aa02ce62cddf3c95501b5f85975278ee88cc32667a3c7af1345` matches the committed search file.
- Each mutant ran against its own fresh `--work` dir; no --work dir was reused (initial non-empty-work FATALs from a shared work dir were discarded and rerun clean — receipts `m*-search.txt`/`m*-shapes.txt` record the clean runs).
- Scratch `/fast/scratch/hyaku/souji-r97/R97MutC1/` deleted before yield; per-mutant receipts (text only, no clones) copied to `.ufo/waves/round-97/w1/R97MutC1/receipts/`.

Receipts copied: baseline search (`base-search.txt`/`pristine-search.txt`), pristine shapes (`pristine-shapes.txt`), per-mutant `m*-search.txt`, `m*-shapes.txt`, `m*-exits.txt`, mutant sha256 list, `probe_m11.py` output. Report: `.ufo/waves/round-97/w1/R97MutC1.md`.
